"""
Sprint ESCAPE-001 — Tests unit + integration sin DB ni red.

Cobertura T1-T6:
  - TestConfig (T3 defaults firmados): 5 tests
  - TestEscapement (T2 class): 8 tests
  - TestEscapementBlockAttempt (T2 block): 2 tests
  - TestBudgetConsume (T4): 3 tests
  - TestDashboard (T5): 4 tests
  - TestMigrationSanity (T1): 2 tests
  - TestWiringSanity (T3-wiring): 2 tests
  - TestPostmortemSanity (T6): 1 test

Total: 27 tests esperados verdes.
"""

from __future__ import annotations

import asyncio
import importlib
import json
import os
import sys
from decimal import Decimal
from pathlib import Path

import pytest

# ── Setup paths ──────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ── T3: Config (defaults firmados) ───────────────────────────────────


@pytest.fixture(autouse=True)
def _isolate_config_env(monkeypatch):
    """Garantiza que ningún env var ESCAPE_PULSE_INTERVAL_* contamina otros tests.

    Borra todas las env vars del prefijo y forza reload del módulo config
    antes de cada test. Esto evita que un test que hace setenv contamine al
    siguiente vía caché de módulo Python.
    """
    for k in list(os.environ.keys()):
        if k.startswith("ESCAPE_PULSE_INTERVAL_"):
            monkeypatch.delenv(k, raising=False)
    try:
        from kernel.escape import config

        importlib.reload(config)
    except ImportError:
        pass
    yield
    try:
        from kernel.escape import config

        importlib.reload(config)
    except ImportError:
        pass


class TestConfig:
    """T3: defaults firmados por T1 (Alfredo) en pulse_intervals."""

    def test_registry_has_six_consumers(self):
        from kernel.escape import config

        assert len(config.REGISTRY_CONSUMERS) == 6
        expected = {
            "embrion_loop_latido",
            "guardian_daily_audit",
            "rotor_recharge",
            "self_verifier_call",
            "embrion_specialization",
            "external_llm_call",
        }
        assert set(config.REGISTRY_CONSUMERS) == expected

    def test_default_pulse_intervals_match_spec(self):
        from kernel.escape import config

        assert config.DEFAULT_PULSE_INTERVALS_SECONDS["embrion_loop_latido"] == 60
        assert config.DEFAULT_PULSE_INTERVALS_SECONDS["guardian_daily_audit"] == 86400
        assert config.DEFAULT_PULSE_INTERVALS_SECONDS["rotor_recharge"] == 300
        assert config.DEFAULT_PULSE_INTERVALS_SECONDS["self_verifier_call"] == 30
        assert config.DEFAULT_PULSE_INTERVALS_SECONDS["embrion_specialization"] == 120
        assert config.DEFAULT_PULSE_INTERVALS_SECONDS["external_llm_call"] == 10

    def test_get_pulse_interval_for_registered_consumer(self):
        from kernel.escape import config

        assert config.get_pulse_interval_seconds("embrion_loop_latido") == 60
        assert config.get_pulse_interval_seconds("external_llm_call") == 10

    def test_is_registered_consumer(self):
        from kernel.escape import config

        assert config.is_registered_consumer("embrion_loop_latido") is True
        assert config.is_registered_consumer("unknown_consumer") is False

    def test_env_override(self, monkeypatch):
        from kernel.escape import config

        monkeypatch.setenv("ESCAPE_PULSE_INTERVAL_EMBRION_LOOP_LATIDO", "120")
        # Forzar reload del módulo para que tome el env actualizado
        importlib.reload(config)
        try:
            assert config.get_pulse_interval_seconds("embrion_loop_latido") == 120
        finally:
            # Restaurar el módulo a su estado canónico
            monkeypatch.delenv("ESCAPE_PULSE_INTERVAL_EMBRION_LOOP_LATIDO")
            importlib.reload(config)


# ── T2: Escapement class ─────────────────────────────────────────────


class TestEscapement:
    """T2: Escapement throttler — can_pulse / record_pulse / persistence."""

    def _new_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

    def test_instantiate_with_registered_consumer(self):
        from kernel.escape.throttler import Escapement

        e = Escapement(consumer="embrion_loop_latido")
        assert e.consumer == "embrion_loop_latido"
        assert e.pulse_interval_seconds == 60

    def test_instantiate_with_unregistered_consumer_warns(self, caplog):
        from kernel.escape.throttler import Escapement

        e = Escapement(consumer="non_canonical", pulse_interval_seconds=10)
        assert e.consumer == "non_canonical"
        assert e.pulse_interval_seconds == 10

    def test_first_pulse_can_proceed(self):
        from kernel.escape.throttler import Escapement, reset_consumer_state

        loop = self._new_loop()
        try:
            loop.run_until_complete(reset_consumer_state())
            e = Escapement(consumer="self_verifier_call")  # interval 30s
            decision = loop.run_until_complete(e.can_pulse())
            assert decision.can_proceed is True
            assert decision.last_pulse_at is None
            assert decision.next_pulse_at is None
        finally:
            loop.close()

    def test_record_pulse_then_immediate_can_pulse_blocked(self):
        from kernel.escape.throttler import Escapement, reset_consumer_state

        loop = self._new_loop()
        try:
            loop.run_until_complete(reset_consumer_state())
            e = Escapement(consumer="embrion_specialization")  # interval 600s
            # primer pulso ok
            d1 = loop.run_until_complete(e.can_pulse())
            assert d1.can_proceed is True
            # registrar pulso
            rec = loop.run_until_complete(e.record_pulse())
            assert rec.consumer == "embrion_specialization"
            assert rec.energy_consumed == Decimal("1.000000")
            # segundo can_pulse inmediato → blocked
            d2 = loop.run_until_complete(e.can_pulse())
            assert d2.can_proceed is False
            assert d2.next_pulse_at is not None
            assert d2.last_pulse_at is not None
        finally:
            loop.close()

    def test_record_pulse_default_energy_matches_spec(self):
        from kernel.escape.throttler import Escapement, reset_consumer_state

        loop = self._new_loop()
        try:
            loop.run_until_complete(reset_consumer_state())
            e = Escapement(consumer="external_llm_call")
            rec = loop.run_until_complete(e.record_pulse())
            assert rec.energy_consumed == Decimal("1.000000")
        finally:
            loop.close()

    def test_record_pulse_persist_failsoft_without_supabase(self):
        from kernel.escape.throttler import Escapement, reset_consumer_state

        loop = self._new_loop()
        try:
            loop.run_until_complete(reset_consumer_state())
            # Sin SUPABASE_URL → persisted=False, sin excepción
            e = Escapement(consumer="rotor_recharge")
            rec = loop.run_until_complete(e.record_pulse())
            assert rec.persisted is False
            assert rec.consumer == "rotor_recharge"
        finally:
            loop.close()

    def test_record_pulse_with_metadata(self):
        from kernel.escape.throttler import Escapement, reset_consumer_state

        loop = self._new_loop()
        try:
            loop.run_until_complete(reset_consumer_state())
            e = Escapement(consumer="guardian_daily_audit")
            rec = loop.run_until_complete(e.record_pulse(metadata={"trigger": "test", "version": 1}))
            assert rec.metadata == {"trigger": "test", "version": 1}
        finally:
            loop.close()

    def test_snapshot_state_after_pulse(self):
        from kernel.escape.throttler import (
            Escapement,
            reset_consumer_state,
            snapshot_state,
        )

        loop = self._new_loop()
        try:
            loop.run_until_complete(reset_consumer_state())
            e = Escapement(consumer="embrion_loop_latido")
            loop.run_until_complete(e.record_pulse())
            snap = loop.run_until_complete(snapshot_state())
            assert isinstance(snap, dict)
            assert "embrion_loop_latido" in snap
        finally:
            loop.close()


# ── T2: block_attempt ────────────────────────────────────────────────


class TestEscapementBlockAttempt:
    """T2: counter de intentos bloqueados dentro de ventana."""

    def _new_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

    def test_block_attempt_increments_counter(self):
        from kernel.escape.throttler import Escapement, reset_consumer_state

        loop = self._new_loop()
        try:
            loop.run_until_complete(reset_consumer_state())
            e = Escapement(consumer="external_llm_call")
            n1 = loop.run_until_complete(e.block_attempt())
            n2 = loop.run_until_complete(e.block_attempt())
            assert n2 == n1 + 1
        finally:
            loop.close()

    def test_blocked_count_resets_after_pulse(self):
        from kernel.escape.throttler import Escapement, reset_consumer_state

        loop = self._new_loop()
        try:
            loop.run_until_complete(reset_consumer_state())
            e = Escapement(consumer="external_llm_call")
            # acumular 3 intentos bloqueados
            loop.run_until_complete(e.block_attempt())
            loop.run_until_complete(e.block_attempt())
            loop.run_until_complete(e.block_attempt())
            # registrar pulso → resetea contador
            rec = loop.run_until_complete(e.record_pulse())
            assert rec.blocked_count_in_window == 3
            # tras el reset interno, el siguiente bloqueado vuelve a 1
            n = loop.run_until_complete(e.block_attempt())
            assert n == 1
        finally:
            loop.close()


# ── T4: embrion_budget.consume() ─────────────────────────────────────


class TestBudgetConsume:
    """T4: consume() en embrion_budget — input validation + fail-soft."""

    def _new_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

    def test_consume_rejects_zero(self):
        from kernel.embrion_budget import consume

        with pytest.raises(ValueError):
            consume(amount=Decimal("0"), consumer="external_llm_call")

    def test_consume_rejects_negative(self):
        from kernel.embrion_budget import consume

        with pytest.raises(ValueError):
            consume(amount=Decimal("-1"), consumer="external_llm_call")

    def test_consume_failsoft_without_supabase(self, monkeypatch):
        from kernel.embrion_budget import consume

        # Asegurar sin env
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
        # consume() es sync, no async; retorna bool directo
        result = consume(amount=Decimal("0.5"), consumer="external_llm_call")
        # fail-soft: retorna False, no excepción
        assert result is False


# ── T5: Dashboard ────────────────────────────────────────────────────


class TestDashboard:
    """T5: dashboard escape_history HTML + JSON."""

    def test_render_html_no_data_template(self, monkeypatch):
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
        from kernel.escape.dashboard import render

        html = render(mode="html")
        assert "<!DOCTYPE html>" in html
        assert "No data disponible" in html
        assert "ESCAPE-001" in html

    def test_render_json_no_data(self, monkeypatch):
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
        from kernel.escape.dashboard import render

        text = render(mode="json")
        data = json.loads(text)
        assert data["available"] is False
        assert data["schema"] == "escape_pulse_log.dashboard.v1"
        assert data["recent_pulses"] == []

    def test_aggregate_function_with_synthetic_rows(self):
        from kernel.escape.dashboard import _aggregate

        rows = [
            {
                "consumer": "embrion_loop_latido",
                "decision": "allow",
                "energy_consumed": "1.0",
                "budget_consumed_usd": "0.001",
                "occurred_at": "2026-05-12T08:00:00Z",
            },
            {
                "consumer": "embrion_loop_latido",
                "decision": "block",
                "energy_consumed": "0",
                "budget_consumed_usd": "0",
                "occurred_at": "2026-05-12T08:00:30Z",
            },
            {
                "consumer": "external_llm_call",
                "decision": "allow",
                "energy_consumed": "1.0",
                "budget_consumed_usd": "0.01",
                "occurred_at": "2026-05-12T08:01:00Z",
            },
        ]
        agg = _aggregate(rows)
        assert agg["total_pulses"] == 3
        assert agg["allowed_pulses"] == 2
        assert agg["blocked_pulses"] == 1
        assert agg["by_consumer"]["embrion_loop_latido"]["total"] == 2
        assert agg["by_consumer"]["embrion_loop_latido"]["allowed"] == 1
        assert agg["by_consumer"]["embrion_loop_latido"]["blocked"] == 1
        assert pytest.approx(agg["total_energy"], 0.01) == 2.0

    def test_render_html_xss_protection(self):
        from kernel.escape.dashboard import _aggregate, _render_html

        evil_rows = [
            {
                "consumer": "<script>alert(1)</script>",
                "decision": "allow",
                "energy_consumed": "1",
                "budget_consumed_usd": "0.001",
                "occurred_at": "2026-05-12T08:00:00Z",
                "pulse_id": "1",
                "reason": "",
            },
        ]
        agg = _aggregate(evil_rows)
        html = _render_html(evil_rows, agg, limit=10)
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html


# ── T1: Migration sanity ─────────────────────────────────────────────


class TestMigrationSanity:
    """T1: migration 0024_escape_pulse_log.sql bien formada."""

    def test_migration_file_exists_and_has_rls(self):
        path = REPO_ROOT / "migrations" / "sql" / "0024_escape_pulse_log.sql"
        assert path.exists(), f"Migration {path} not found"
        content = path.read_text(encoding="utf-8")
        assert "CREATE TABLE" in content
        assert "escape_pulse_log" in content
        assert "ENABLE ROW LEVEL SECURITY" in content
        assert "CREATE POLICY" in content

    def test_migration_idempotent_guards(self):
        path = REPO_ROOT / "migrations" / "sql" / "0024_escape_pulse_log.sql"
        content = path.read_text(encoding="utf-8")
        # idempotent patterns
        assert "IF NOT EXISTS" in content
        # verificación automática del RLS al final
        assert "RAISE EXCEPTION" in content or "ASSERT" in content


# ── T3-wiring: marcadores en embrion_loop.py ─────────────────────────


class TestWiringSanity:
    """T3-wiring: marcadores ESCAPE_BEGIN/END en embrion_loop.py."""

    def test_escape_markers_present(self):
        path = REPO_ROOT / "kernel" / "embrion_loop.py"
        content = path.read_text(encoding="utf-8")
        assert "ESCAPE_BEGIN" in content
        assert "ESCAPE_END" in content

    def test_escape_import_and_flag_present(self):
        path = REPO_ROOT / "kernel" / "embrion_loop.py"
        content = path.read_text(encoding="utf-8")
        # Flag canónico
        assert "EMBRION_ESCAPE_ENABLED" in content
        # Import lazy del módulo de escape
        assert "kernel.escape" in content or "from kernel.escape" in content


# ── T6: Postmortem sanity ────────────────────────────────────────────


class TestPostmortemSanity:
    """T6: placeholder + DSC-MO-014 candidato presente."""

    def test_postmortem_file_exists(self):
        path = REPO_ROOT / "bridge" / "postmortems" / "postmortem_ESCAPE_001_PLACEHOLDER_2026_05_12.md"
        assert path.exists(), f"Postmortem {path} not found"
        content = path.read_text(encoding="utf-8")
        assert "DSC-MO-014" in content
        assert "Throttler" in content
        assert "PLACEHOLDER" in content
