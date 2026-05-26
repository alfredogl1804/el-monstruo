"""
Sprint ESPIRAL-001 — Tests unit + integration sin DB ni red.

Cobertura T1-T6:
  - TestController (T2 controller logic): 8 tests
  - TestSensor (T2 sensor): 4 tests
  - TestRegistry (T4 escape.registry): 6 tests
  - TestHairspring (T2 homeostasis class): 6 tests
  - TestDashboard (T5 espiral_history): 4 tests
  - TestMigrationSanity (T1): 2 tests
  - TestWiringSanity (T3 marcadores embrion_loop): 3 tests
  - TestDoctrineSanity (T6): 1 test

Total: 34 tests esperados verdes.

DSC enforzado en suite:
- DSC-G-008 v3 anti-Goodhart: tests verifican comportamiento correctivo SIN
  alterar baseline canonical (asegura que el feedback loop NO crea Goodhart).
- DSC-MO-006 v1.1: TestWiringSanity verifica marcadores ESPIRAL_BEGIN/END
  sin tocar cuerpo del embrion_loop.py.
- DSC-S-006 v1.1: TestMigrationSanity verifica RLS + policy en migration 0026.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

# ── Setup paths ──────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ─────────────────────────────────────────────────────────────────────
# T2: Controller — feedback negativo proportional
# ─────────────────────────────────────────────────────────────────────
class TestController:
    def test_decision_no_action_when_deviation_zero(self):
        from kernel.espiral.controller import CorrectionAction, ProportionalController

        c = ProportionalController(sensitivity=0.5)
        d = c.decide(deviation_ratio=0.0, canonical_interval_seconds=60, currently_overridden=False)
        assert d.action == CorrectionAction.NONE
        assert d.new_pulse_interval_seconds == 60

    def test_decision_no_action_when_deviation_within_threshold(self):
        from kernel.espiral.controller import CorrectionAction, ProportionalController

        c = ProportionalController(sensitivity=0.5)
        # deviation_ratio=1.10 → abs_deviation=0.10 < 0.30 (correction threshold)
        d = c.decide(deviation_ratio=1.10, canonical_interval_seconds=60, currently_overridden=False)
        assert d.action == CorrectionAction.NONE

    def test_decision_spike_dampening_increases_interval(self):
        from kernel.espiral.controller import CorrectionAction, ProportionalController

        c = ProportionalController(sensitivity=0.5)
        # deviation_ratio=2.0 → spike. factor = 1 + 0.5*1.0 = 1.5 → 60*1.5 = 90
        d = c.decide(deviation_ratio=2.0, canonical_interval_seconds=60, currently_overridden=False)
        assert d.action == CorrectionAction.SPIKE_DAMPENING
        assert d.new_pulse_interval_seconds == 90
        assert d.correction_factor == 1.5

    def test_decision_spike_dampening_capped_at_max(self):
        from kernel.espiral.controller import MAX_CORRECTION_FACTOR_UP, CorrectionAction, ProportionalController

        c = ProportionalController(sensitivity=1.0)
        # deviation_ratio=10 → factor raw = 1 + 1.0*9 = 10 → capped a 2.0 (MAX_CORRECTION_FACTOR_UP)
        d = c.decide(deviation_ratio=10.0, canonical_interval_seconds=60, currently_overridden=False)
        assert d.action == CorrectionAction.SPIKE_DAMPENING
        assert d.correction_factor == MAX_CORRECTION_FACTOR_UP
        assert d.new_pulse_interval_seconds == 120

    def test_decision_undershoot_acceleration_reduces_interval(self):
        from kernel.espiral.controller import CorrectionAction, ProportionalController

        c = ProportionalController(sensitivity=0.5)
        # deviation_ratio=0.5 → undershoot. abs_dev=0.5. factor = 1 - 0.5*0.5 = 0.75 → 60*0.75 = 45
        d = c.decide(deviation_ratio=0.5, canonical_interval_seconds=60, currently_overridden=False)
        assert d.action == CorrectionAction.UNDERSHOOT_ACCELERATION
        assert d.new_pulse_interval_seconds == 45

    def test_decision_undershoot_capped_at_min(self):
        from kernel.espiral.controller import MAX_CORRECTION_FACTOR_DOWN, CorrectionAction, ProportionalController

        c = ProportionalController(sensitivity=1.0)
        # deviation_ratio=0.01 → factor raw = 1 - 0.99 = 0.01 → capped a 0.5 (MAX_CORRECTION_FACTOR_DOWN)
        d = c.decide(deviation_ratio=0.01, canonical_interval_seconds=60, currently_overridden=False)
        assert d.action == CorrectionAction.UNDERSHOOT_ACCELERATION
        assert d.correction_factor == MAX_CORRECTION_FACTOR_DOWN
        assert d.new_pulse_interval_seconds == 30

    def test_decision_return_to_canonical_when_overridden_and_stable(self):
        from kernel.espiral.controller import CorrectionAction, ProportionalController

        c = ProportionalController(sensitivity=0.5)
        # deviation_ratio=1.05 → abs_dev=0.05 < 0.10 (return threshold) y overridden=True → RETURN
        d = c.decide(deviation_ratio=1.05, canonical_interval_seconds=60, currently_overridden=True)
        assert d.action == CorrectionAction.RETURN_TO_CANONICAL
        assert d.new_pulse_interval_seconds == 60

    def test_sensitivity_validation(self):
        from kernel.espiral.controller import ProportionalController

        with pytest.raises(ValueError):
            ProportionalController(sensitivity=-0.1)
        with pytest.raises(ValueError):
            ProportionalController(sensitivity=1.5)


# ─────────────────────────────────────────────────────────────────────
# T2: Sensor — observador pulse_rate ventana móvil
# ─────────────────────────────────────────────────────────────────────
class TestSensor:
    def test_baseline_rate_per_minute_from_canonical(self):
        from kernel.espiral.sensor import PulseRateSensor

        s = PulseRateSensor(consumer="embrion_loop_latido", window_minutes=15)
        # canonical típico embrion_loop_latido = 60s → baseline = 1.0 pulses/min
        assert s.baseline_rate_per_minute > 0

    @pytest.mark.asyncio
    async def test_sense_returns_zero_when_no_query_fn(self):
        from kernel.espiral.sensor import PulseRateSensor

        s = PulseRateSensor(consumer="embrion_loop_latido", window_minutes=15)
        r = await s.sense()
        assert r.pulses_observed == 0
        assert r.pulse_rate_observed == 0.0
        assert r.consumer == "embrion_loop_latido"

    @pytest.mark.asyncio
    async def test_sense_with_mock_query_calculates_rate(self):
        from kernel.espiral.sensor import PulseRateSensor

        # mock retorna 30 pulses en 15min = 2 pulses/min observed
        async def mock_query(consumer, window):
            return 30

        s = PulseRateSensor(consumer="embrion_loop_latido", window_minutes=15, db_query_fn=mock_query)
        r = await s.sense()
        assert r.pulses_observed == 30
        assert r.pulse_rate_observed == 2.0
        assert r.deviation_ratio > 0  # depende de baseline canonical

    @pytest.mark.asyncio
    async def test_sense_failsoft_on_query_exception(self):
        from kernel.espiral.sensor import PulseRateSensor

        async def failing_query(consumer, window):
            raise ConnectionError("DB down")

        s = PulseRateSensor(consumer="embrion_loop_latido", window_minutes=15, db_query_fn=failing_query)
        r = await s.sense()  # no debe romper
        assert r.pulses_observed == 0
        assert r.pulse_rate_observed == 0.0


# ─────────────────────────────────────────────────────────────────────
# T4: Escape registry — apply_temporal_override
# ─────────────────────────────────────────────────────────────────────
class TestRegistry:
    @pytest.fixture(autouse=True)
    def _reset(self):
        from kernel.escape.registry import _reset_state_for_tests

        _reset_state_for_tests()
        yield
        _reset_state_for_tests()

    @pytest.mark.asyncio
    async def test_apply_override_changes_effective_interval(self):
        from kernel.escape.config import get_pulse_interval_seconds
        from kernel.escape.registry import apply_temporal_override, get_effective_pulse_interval

        canonical = get_pulse_interval_seconds("embrion_loop_latido")
        await apply_temporal_override("embrion_loop_latido", canonical * 2, ttl_seconds=300)
        assert get_effective_pulse_interval("embrion_loop_latido") == canonical * 2

    @pytest.mark.asyncio
    async def test_restore_canonical_removes_override(self):
        from kernel.escape.config import get_pulse_interval_seconds
        from kernel.escape.registry import apply_temporal_override, get_effective_pulse_interval, restore_canonical

        canonical = get_pulse_interval_seconds("embrion_loop_latido")
        await apply_temporal_override("embrion_loop_latido", canonical * 2, ttl_seconds=300)
        assert get_effective_pulse_interval("embrion_loop_latido") == canonical * 2
        existed = await restore_canonical("embrion_loop_latido")
        assert existed is True
        assert get_effective_pulse_interval("embrion_loop_latido") == canonical

    @pytest.mark.asyncio
    async def test_override_expires_after_ttl(self):
        from kernel.escape.config import get_pulse_interval_seconds
        from kernel.escape.registry import apply_temporal_override, get_effective_pulse_interval

        canonical = get_pulse_interval_seconds("embrion_loop_latido")
        await apply_temporal_override("embrion_loop_latido", canonical * 2, ttl_seconds=1)
        assert get_effective_pulse_interval("embrion_loop_latido") == canonical * 2
        # forward time via now_epoch arg
        assert get_effective_pulse_interval("embrion_loop_latido", now_epoch=time.time() + 10) == canonical

    @pytest.mark.asyncio
    async def test_apply_override_validates_inputs(self):
        from kernel.escape.registry import apply_temporal_override

        with pytest.raises(ValueError):
            await apply_temporal_override("", 60, 300)
        with pytest.raises(ValueError):
            await apply_temporal_override("c", -1, 300)
        with pytest.raises(ValueError):
            await apply_temporal_override("c", 60, -1)

    @pytest.mark.asyncio
    async def test_restore_returns_false_when_no_override(self):
        from kernel.escape.registry import restore_canonical

        existed = await restore_canonical("embrion_loop_latido")
        assert existed is False

    @pytest.mark.asyncio
    async def test_list_active_overrides_filters_expired(self):
        from kernel.escape.registry import apply_temporal_override, list_active_overrides

        await apply_temporal_override("embrion_loop_latido", 120, ttl_seconds=300)
        await apply_temporal_override("guardian_audit", 600, ttl_seconds=1)
        actives = list_active_overrides()
        assert any(o.consumer == "embrion_loop_latido" for o in actives)
        # Después de un poco, el segundo debería expirar
        time.sleep(1.1)
        actives2 = list_active_overrides()
        consumers = {o.consumer for o in actives2}
        assert "embrion_loop_latido" in consumers
        assert "guardian_audit" not in consumers


# ─────────────────────────────────────────────────────────────────────
# T2: Hairspring class — integración E2E sin DB
# ─────────────────────────────────────────────────────────────────────
class TestHairspring:
    @pytest.fixture(autouse=True)
    def _reset(self):
        from kernel.escape.registry import _reset_state_for_tests

        _reset_state_for_tests()
        yield
        _reset_state_for_tests()

    def test_hairspring_validates_consumer(self):
        from kernel.espiral.homeostasis import Hairspring

        with pytest.raises(ValueError):
            Hairspring(consumer="")
        with pytest.raises(ValueError):
            Hairspring(consumer="x", window_minutes=0)
        with pytest.raises(ValueError):
            Hairspring(consumer="x", override_ttl_seconds=0)

    @pytest.mark.asyncio
    async def test_full_cycle_no_op_when_baseline_observed(self):
        from kernel.espiral.controller import CorrectionAction
        from kernel.espiral.homeostasis import Hairspring

        # Mock: pulses observed exactamente == baseline → deviation_ratio=1.0 → NONE
        async def mock_query(consumer, window):
            from kernel.escape.config import get_pulse_interval_seconds

            canonical_interval = get_pulse_interval_seconds(consumer)
            baseline_rate = 60.0 / canonical_interval if canonical_interval > 0 else 0
            return int(baseline_rate * window)  # exactamente baseline

        h = Hairspring(consumer="embrion_loop_latido", db_query_fn=mock_query)
        r = await h.sense_deviation()
        c = await h.apply_correction(r)
        assert c.action == CorrectionAction.NONE

    @pytest.mark.asyncio
    async def test_full_cycle_spike_dampening_invokes_override(self):
        from kernel.espiral.controller import CorrectionAction
        from kernel.espiral.homeostasis import Hairspring

        # Mock: pulses observed = baseline*3 → deviation_ratio=3.0 → SPIKE
        async def mock_query(consumer, window):
            from kernel.escape.config import get_pulse_interval_seconds

            ci = get_pulse_interval_seconds(consumer)
            base = 60.0 / ci if ci > 0 else 0
            return int(base * window * 3)

        override_calls = []

        async def mock_override(consumer, new_interval, ttl):
            override_calls.append((consumer, new_interval, ttl))

        h = Hairspring(
            consumer="embrion_loop_latido",
            db_query_fn=mock_query,
            registry_override_fn=mock_override,
        )
        r = await h.sense_deviation()
        c = await h.apply_correction(r)
        assert c.action == CorrectionAction.SPIKE_DAMPENING
        assert len(override_calls) == 1
        assert h.currently_overridden is True

    @pytest.mark.asyncio
    async def test_hairspring_logs_to_homeostasis_when_action(self):
        from kernel.espiral.homeostasis import Hairspring

        async def mock_query(consumer, window):
            from kernel.escape.config import get_pulse_interval_seconds

            ci = get_pulse_interval_seconds(consumer)
            base = 60.0 / ci if ci > 0 else 0
            return int(base * window * 3)

        log_calls = []

        async def mock_logger(consumer, reading, applied):
            log_calls.append((consumer, reading.deviation_ratio, applied.action.value))

        h = Hairspring(
            consumer="embrion_loop_latido",
            db_query_fn=mock_query,
            homeostasis_logger_fn=mock_logger,
        )
        r = await h.sense_deviation()
        c = await h.apply_correction(r)
        assert c.persisted is True
        assert len(log_calls) == 1
        assert log_calls[0][2] == "spike_dampening"

    @pytest.mark.asyncio
    async def test_hairspring_failsoft_when_logger_raises(self):
        from kernel.espiral.homeostasis import Hairspring

        async def mock_query(consumer, window):
            from kernel.escape.config import get_pulse_interval_seconds

            ci = get_pulse_interval_seconds(consumer)
            base = 60.0 / ci if ci > 0 else 0
            return int(base * window * 3)

        async def failing_logger(c, r, a):
            raise ConnectionError("DB down")

        h = Hairspring(
            consumer="embrion_loop_latido",
            db_query_fn=mock_query,
            homeostasis_logger_fn=failing_logger,
        )
        r = await h.sense_deviation()
        c = await h.apply_correction(r)
        # action sigue ocurriendo, sólo persisted=False
        assert c.persisted is False
        assert c.action.value == "spike_dampening"

    @pytest.mark.asyncio
    async def test_force_return_to_canonical_only_if_overridden(self):
        from kernel.espiral.homeostasis import Hairspring

        restore_calls = []

        async def mock_restore(consumer):
            restore_calls.append(consumer)

        h = Hairspring(
            consumer="embrion_loop_latido",
            registry_restore_fn=mock_restore,
        )
        # No overrideado → no llama restore
        await h.return_to_canonical()
        assert restore_calls == []
        # Forzar estado overrideado
        h._currently_overridden = True
        await h.return_to_canonical()
        assert restore_calls == ["embrion_loop_latido"]
        assert h.currently_overridden is False


# ─────────────────────────────────────────────────────────────────────
# T5: Dashboard espiral_history
# ─────────────────────────────────────────────────────────────────────
class TestDashboard:
    def test_aggregate_history_empty(self):
        from kernel.dashboards.espiral_history import aggregate_history

        s = aggregate_history([])
        assert s["total_events"] == 0
        assert s["by_reason"]["spike_dampening"] == 0

    def test_aggregate_history_counts_by_consumer_and_reason(self):
        from datetime import datetime, timezone

        from kernel.dashboards.espiral_history import HomeostasisRow, aggregate_history

        rows = [
            HomeostasisRow(
                id=str(i),
                created_at=datetime.now(timezone.utc),
                consumer="embrion_loop_latido",
                pulse_rate_observed=2.0,
                pulse_rate_baseline=1.0,
                deviation_ratio=2.0,
                pulse_interval_adjusted_to=120,
                pulse_interval_canonical=60,
                adjustment_reason=("spike_dampening" if i % 2 == 0 else "return_to_canonical"),
                window_minutes=15,
            )
            for i in range(10)
        ]
        s = aggregate_history(rows)
        assert s["total_events"] == 10
        assert s["by_reason"]["spike_dampening"] == 5
        assert s["by_reason"]["return_to_canonical"] == 5
        assert s["by_consumer"]["embrion_loop_latido"] == 10

    def test_render_html_escapes_consumer_name(self):
        from datetime import datetime, timezone

        from kernel.dashboards.espiral_history import HomeostasisRow, render_html

        evil = '<script>alert("xss")</script>'
        rows = [
            HomeostasisRow(
                id="1",
                created_at=datetime.now(timezone.utc),
                consumer=evil,
                pulse_rate_observed=1.0,
                pulse_rate_baseline=1.0,
                deviation_ratio=1.0,
                pulse_interval_adjusted_to=60,
                pulse_interval_canonical=60,
                adjustment_reason="spike_dampening",
                window_minutes=15,
            )
        ]
        out = render_html(rows, 24)
        assert evil not in out
        assert "&lt;script&gt;" in out

    def test_render_json_serializable(self):
        import json as _json
        from datetime import datetime, timezone

        from kernel.dashboards.espiral_history import HomeostasisRow, render_json

        rows = [
            HomeostasisRow(
                id="1",
                created_at=datetime.now(timezone.utc),
                consumer="c",
                pulse_rate_observed=1.0,
                pulse_rate_baseline=1.0,
                deviation_ratio=1.0,
                pulse_interval_adjusted_to=60,
                pulse_interval_canonical=60,
                adjustment_reason="return_to_canonical",
                window_minutes=15,
            )
        ]
        out = render_json(rows, 24)
        parsed = _json.loads(out)
        assert parsed["window_hours"] == 24
        assert parsed["summary"]["total_events"] == 1


# ─────────────────────────────────────────────────────────────────────
# T1: Migration sanity (no DB)
# ─────────────────────────────────────────────────────────────────────
class TestMigrationSanity:
    def test_migration_file_exists_and_canonical_naming(self):
        path = REPO_ROOT / "migrations" / "sql" / "0026_embrion_homeostasis_log.sql"
        assert path.exists()
        content = path.read_text()
        assert "CREATE TABLE IF NOT EXISTS public.embrion_homeostasis_log" in content
        assert "ALTER TABLE public.embrion_homeostasis_log ENABLE ROW LEVEL SECURITY" in content

    def test_migration_has_rls_policy_and_check_constraints(self):
        path = REPO_ROOT / "migrations" / "sql" / "0026_embrion_homeostasis_log.sql"
        content = path.read_text()
        assert "homeostasis_log_service_role_only" in content
        assert "homeostasis_log_adjustment_reason_valid" in content
        # Verifica los 3 valores canónicos del CHECK constraint
        assert "spike_dampening" in content
        assert "undershoot_acceleration" in content
        assert "return_to_canonical" in content
        # DSC-S-006 v1.1 verification block
        assert "DSC-S-006 v1.1 VIOLATION" in content


# ─────────────────────────────────────────────────────────────────────
# T3: Wiring sanity — marcadores ESPIRAL en embrion_loop.py
# ─────────────────────────────────────────────────────────────────────
class TestWiringSanity:
    def test_embrion_loop_has_espiral_markers(self):
        path = REPO_ROOT / "kernel" / "embrion_loop.py"
        content = path.read_text()
        assert content.count("ESPIRAL_BEGIN") >= 3, "Falta ESPIRAL_BEGIN (imports + flag + ejecutivo)"
        assert content.count("ESPIRAL_END") >= 3, "Falta ESPIRAL_END (imports + flag + ejecutivo)"

    def test_embrion_loop_espiral_uses_feature_flag(self):
        path = REPO_ROOT / "kernel" / "embrion_loop.py"
        content = path.read_text()
        assert "EMBRION_ESPIRAL_ENABLED" in content
        assert "EMBRION_ESPIRAL_CHECK_EVERY_N_CYCLES" in content
        assert "_ESPIRAL_AVAILABLE" in content

    def test_embrion_loop_espiral_after_escape_block(self):
        """ESPIRAL debe estar DESPUÉS de ESCAPE en el think loop (orden Reloj Suizo)."""
        path = REPO_ROOT / "kernel" / "embrion_loop.py"
        content = path.read_text()
        # En el bloque ejecutivo (no imports), el primer ESPIRAL_BEGIN ejecutivo
        # debe venir DESPUÉS del último ESCAPE_END
        # Buscar ocurrencias en cuerpo (no en comentarios de imports/flags)
        # Tomamos posición del ESCAPE_END ejecutivo y ESPIRAL_BEGIN ejecutivo
        # ESPIRAL_END (ejecutivo) > ESCAPE_END (ejecutivo)
        last_escape_end = content.rfind("ESCAPE_END")
        last_espiral_end = content.rfind("ESPIRAL_END")
        assert last_espiral_end > last_escape_end


# ─────────────────────────────────────────────────────────────────────
# T6: Doctrine sanity
# ─────────────────────────────────────────────────────────────────────
class TestDoctrineSanity:
    def test_postmortem_placeholder_exists(self):
        path = REPO_ROOT / "discovery_forense" / "POSTMORTEMS" / "ESPIRAL_001_postmortem.md"
        assert path.exists(), f"Missing postmortem placeholder at {path}"
        content = path.read_text()
        assert "ESPIRAL-001" in content
        assert "Hairspring" in content or "Espiral" in content
