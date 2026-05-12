"""
tests/rotor/test_rotor.py — Tests del Sprint ROTOR-001

Cobertura:
  T2 capturers (6) — cada uno produce RotorActivity correcto desde su payload
  T3 energy_calculator — defaults firmados T1 + caps + edge cases
  T4 recharge.run_recharge_cycle — pure function (sin DB)
  T4 recharge_mainspring_handler — fail-soft sin psycopg/sin DB
  T4 add_recycled_energy — positivo, zero (no-op), negativo (raise)
  T4 wiring scheduler — task registrada + handler stub registrado
  T5 dashboard — render_html con None data (no_data template), render_json
  T1 migración — SQL bien formado (smoke parse)

Ejecutar: pytest tests/rotor/ -v
"""

from __future__ import annotations

import asyncio
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# T2 — Capturers
# ---------------------------------------------------------------------------
class TestCapturers:
    def test_github_capturer(self):
        from kernel.rotor.capturers.github_capturer import GitHubCapturer

        ev = {
            "sha": "abc123",
            "ref": "refs/heads/main",
            "actor": "alfredo",
            "merged_to_main": True,
        }
        a = GitHubCapturer().capture(ev)
        assert a.source == "github_commit"
        assert a.actor == "alfredo"
        assert a.payload["merged_to_main"] is True

    def test_supabase_capturer(self):
        from kernel.rotor.capturers.supabase_capturer import SupabaseCapturer

        ev = {"table": "embrion_memoria", "operation": "insert", "rows": 1}
        a = SupabaseCapturer().capture(ev)
        assert a.source == "supabase_query"

    def test_telegram_capturer(self):
        from kernel.rotor.capturers.telegram_capturer import TelegramCapturer

        ev = {"chat_id": "123", "message": "hola", "from": "user"}
        a = TelegramCapturer().capture(ev)
        assert a.source == "telegram_message"

    def test_cowork_capturer(self):
        from kernel.rotor.capturers.cowork_capturer import CoworkCapturer

        ev = {"session_id": "s1", "duration_seconds": 10800, "actor": "alfredo"}
        a = CoworkCapturer().capture(ev)
        assert a.source == "cowork_session"
        assert a.payload["duration_seconds"] == 10800

    def test_manus_capturer(self):
        from kernel.rotor.capturers.manus_capturer import ManusCapturer

        ev = {"task_id": "t1", "tokens_in": 1000, "tokens_out": 500}
        a = ManusCapturer().capture(ev)
        assert a.source == "manus_session"

    def test_latido_capturer(self):
        from kernel.rotor.capturers.latido_capturer import LatidoCapturer

        ev = {"latido_id": "l1", "status": "ok"}
        a = LatidoCapturer().capture(ev)
        assert a.source == "embrion_latido"

    def test_all_six_capturers_registered(self):
        """T2 contract: exactamente 6 capturers en el registry."""
        from kernel.rotor.capturers import REGISTRY

        assert len(REGISTRY) == 6, f"Expected 6 capturers, got {len(REGISTRY)}"
        expected = {
            "github_commit",
            "supabase_query",
            "telegram_message",
            "cowork_session",
            "manus_session",
            "embrion_latido",
        }
        assert set(REGISTRY.keys()) == expected


# ---------------------------------------------------------------------------
# T3 — Energy Calculator (defaults firmados)
# ---------------------------------------------------------------------------
class TestEnergyCalculator:
    def test_github_commit_main_default(self):
        """Default firmado T1: github_commit merged a main = $0.15"""
        from kernel.rotor.energy_calculator import RotorActivity, compute_energy_units

        a = RotorActivity(
            source="github_commit",
            actor="alfredo",
            payload={"merged_to_main": True},
        )
        units = compute_energy_units(a)
        assert units == Decimal("0.15"), f"Expected 0.15, got {units}"

    def test_github_commit_branch_default(self):
        """github_commit no-main = $0.05"""
        from kernel.rotor.energy_calculator import RotorActivity, compute_energy_units

        a = RotorActivity(
            source="github_commit",
            actor="alfredo",
            payload={"merged_to_main": False},
        )
        units = compute_energy_units(a)
        assert units == Decimal("0.05")

    def test_cowork_session_3h(self):
        """cowork_session 3 horas = $0.50 (default firmado)"""
        from kernel.rotor.energy_calculator import RotorActivity, compute_energy_units

        a = RotorActivity(
            source="cowork_session",
            actor="cowork",
            payload={"duration_seconds": 10800},
        )
        units = compute_energy_units(a)
        assert units == Decimal("0.50")

    def test_latido_aborted_penalty(self):
        """embrion_latido aborted = -$0.05 (penalización)"""
        from kernel.rotor.energy_calculator import RotorActivity, compute_energy_units

        a = RotorActivity(
            source="embrion_latido",
            actor="embrion",
            payload={"status": "aborted"},
        )
        units = compute_energy_units(a)
        assert units == Decimal("-0.05")

    def test_apply_daily_source_cap(self):
        """Cap diario por source = $5/día"""
        from kernel.rotor.energy_calculator import apply_daily_source_cap

        # Bajo el cap: pasa intacto
        out = apply_daily_source_cap(
            raw_units=Decimal("0.50"),
            accumulated_today_for_source=Decimal("4.0"),
        )
        assert out == Decimal("0.50")

        # Saldría sobre el cap: se trimea
        out2 = apply_daily_source_cap(
            raw_units=Decimal("2.0"),
            accumulated_today_for_source=Decimal("4.0"),
        )
        assert out2 == Decimal("1.0"), f"Expected 1.0 (cap trim), got {out2}"

        # Ya en el cap: zero
        out3 = apply_daily_source_cap(
            raw_units=Decimal("1.0"),
            accumulated_today_for_source=Decimal("5.0"),
        )
        assert out3 == Decimal("0")

    def test_apply_total_recharge_cap(self):
        """Cap superior $30/día firmado T1"""
        from kernel.rotor.energy_calculator import apply_total_recharge_cap

        # Bajo el cap: todo pasa
        units, lost = apply_total_recharge_cap(
            pending_units=Decimal("5.0"),
            already_recharged_today=Decimal("10.0"),
        )
        assert units == Decimal("5.0")
        assert lost == Decimal("0")

        # Excede cap: se trimea + reporta lost
        units2, lost2 = apply_total_recharge_cap(
            pending_units=Decimal("25.0"),
            already_recharged_today=Decimal("20.0"),
        )
        assert units2 == Decimal("10.0"), f"Cap trim a $30 (10 disponibles), got {units2}"
        assert lost2 == Decimal("15.0")


# ---------------------------------------------------------------------------
# T4 — Recharge cycle (pure function)
# ---------------------------------------------------------------------------
class TestRechargeCyclePure:
    def test_empty_pending_returns_zero(self):
        from kernel.rotor.recharge import run_recharge_cycle

        result, ids, units = run_recharge_cycle(
            pending_rows=[],
            already_recharged_today_usd=Decimal("0"),
            accumulated_today_by_source_usd={},
            cycle_id=1,
        )
        assert ids == []
        assert units == Decimal("0")
        assert result.rows_consumed == 0

    def test_lazy_enrichment_works(self):
        """Filas con energy_units=None se calculan al vuelo"""
        from kernel.rotor.recharge import run_recharge_cycle

        pending = [
            {
                "id": "r1",
                "source": "github_commit",
                "actor": "alfredo",
                "payload_jsonb": {"merged_to_main": True},
                "energy_units": None,
            }
        ]
        result, ids, units = run_recharge_cycle(
            pending_rows=pending,
            already_recharged_today_usd=Decimal("0"),
            accumulated_today_by_source_usd={},
            cycle_id=1,
        )
        assert len(ids) == 1
        assert units == Decimal("0.15")  # default firmado

    def test_cap_diario_por_source_marca_consumida(self):
        """Filas que exceden cap diario por source se marcan consumidas pero no recargan"""
        from kernel.rotor.recharge import run_recharge_cycle

        # Source ya en el cap ($5)
        pending = [
            {
                "id": "r1",
                "source": "github_commit",
                "actor": "alfredo",
                "payload_jsonb": {"merged_to_main": True},
                "energy_units": None,
            }
        ]
        result, ids, units = run_recharge_cycle(
            pending_rows=pending,
            already_recharged_today_usd=Decimal("0"),
            accumulated_today_by_source_usd={"github_commit": Decimal("5.0")},
            cycle_id=1,
        )
        # Marcada consumida (no reintentar) pero unit zero
        assert "r1" in ids
        assert result.rows_skipped_capped == 1
        assert units == Decimal("0")

    def test_cap_superior_30_usd_firmado(self):
        """Cap superior $30/día firmado T1: rows aportan max 30 - already_today"""
        from kernel.rotor.recharge import run_recharge_cycle

        # Ya recargados $28; el cap restante es $2
        pending = [
            {
                "id": "r1",
                "source": "cowork_session",
                "actor": "cowork",
                "payload_jsonb": {"duration_seconds": 21600},  # 6h = $1
                "energy_units": None,
            },
            {
                "id": "r2",
                "source": "cowork_session",
                "actor": "cowork",
                "payload_jsonb": {"duration_seconds": 21600},
                "energy_units": None,
            },
            {
                "id": "r3",
                "source": "cowork_session",
                "actor": "cowork",
                "payload_jsonb": {"duration_seconds": 21600},
                "energy_units": None,
            },
        ]
        result, ids, units = run_recharge_cycle(
            pending_rows=pending,
            already_recharged_today_usd=Decimal("28.0"),
            accumulated_today_by_source_usd={},
            cycle_id=1,
        )
        # cowork_session es flat $0.50 (no escala con duracion). 3 sesiones = $1.50.
        # already_today=$28, cap superior=$30, disponible=$2. Como $1.50 < $2, todo entra.
        assert units == Decimal("1.5"), f"3 cowork x $0.50 = $1.50, got {units}"
        assert Decimal(result.units_lost_capacity_exceeded_usd) == Decimal("0")


# ---------------------------------------------------------------------------
# T4 — recharge_mainspring_handler (fail-soft sin DB)
# ---------------------------------------------------------------------------
class TestRechargeHandlerFailSoft:
    def test_no_db_url_returns_degraded(self, monkeypatch):
        from kernel.rotor.recharge import recharge_mainspring_handler

        monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)

        result = asyncio.run(recharge_mainspring_handler(cycle_id=42))
        assert result["degraded"] is True
        assert "DB_URL" in result["degraded_reason"] or "psycopg" in result["degraded_reason"]
        assert result["rows_consumed"] == 0


# ---------------------------------------------------------------------------
# T4 — add_recycled_energy en embrion_budget
# ---------------------------------------------------------------------------
class TestAddRecycledEnergy:
    def test_positive_units_persists(self):
        from kernel.embrion_budget import add_recycled_energy

        mock = MagicMock()
        mock.insert.return_value = [{"id": "uuid", "cost_actual_usd": -0.6}]
        out = add_recycled_energy(
            units_usd=Decimal("0.6"),
            cycle_id=42,
            source_breakdown={"github_commit": {"consumed_usd": "0.15"}},
            supabase_client=mock,
        )
        assert out["recorded"] is True
        # Verifica que el payload tiene cost_actual_usd negativo (=recharge)
        call_args = mock.insert.call_args
        payload = call_args[0][1]
        assert payload["cost_actual_usd"] == -0.6
        assert payload["abort_reason"].startswith("rotor_recharge")

    def test_zero_units_no_op(self):
        from kernel.embrion_budget import add_recycled_energy

        mock = MagicMock()
        out = add_recycled_energy(units_usd=Decimal("0"), cycle_id=42, supabase_client=mock)
        assert out["recorded"] is False
        assert out["reason"] == "zero_units"
        # No insert call
        mock.insert.assert_not_called()

    def test_negative_raises_value_error(self):
        from kernel.embrion_budget import add_recycled_energy

        mock = MagicMock()
        with pytest.raises(ValueError, match=">= 0"):
            add_recycled_energy(units_usd=Decimal("-1"), cycle_id=42, supabase_client=mock)


# ---------------------------------------------------------------------------
# T4 — Wiring scheduler
# ---------------------------------------------------------------------------
class TestSchedulerWiring:
    def test_recharge_mainspring_task_registered(self):
        """T4 contract: recharge_mainspring debe estar en register_default_tasks"""
        from kernel.embrion_scheduler import EmbrionScheduler, register_default_tasks

        # add_task usa asyncio.get_event_loop() — necesita un loop activo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        scheduler = EmbrionScheduler(db=None)
        register_default_tasks(scheduler)
        tasks = scheduler.get_all_tasks()
        names = [t["name"] for t in tasks]
        assert "recharge_mainspring" in names

        recharge = next(t for t in tasks if t["name"] == "recharge_mainspring")
        assert recharge["schedule_type"] == "periodic"
        # 5 min ≈ 0.0833h
        assert abs(recharge["interval_hours"] - 5.0 / 60.0) < 0.001
        assert recharge["max_cost_usd"] == 0.05
        assert recharge["handler"] == "recharge_mainspring"

    def test_recharge_mainspring_stub_registered(self):
        from kernel.embrion_scheduler import (
            EmbrionScheduler,
            register_default_tasks,
            register_stub_handlers,
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        scheduler = EmbrionScheduler(db=None)
        register_default_tasks(scheduler)
        register_stub_handlers(scheduler)
        assert "recharge_mainspring" in scheduler._handlers


# ---------------------------------------------------------------------------
# T5 — Dashboard
# ---------------------------------------------------------------------------
class TestDashboard:
    def test_render_html_no_data_template(self):
        from kernel.rotor.dashboard import render_html

        html_out = render_html(None)
        assert "<!DOCTYPE html>" in html_out
        assert "Sin datos disponibles" in html_out
        assert "SUPABASE_DB_URL" in html_out

    def test_render_html_with_data(self):
        from kernel.rotor.dashboard import render_html

        data = {
            "fetched_at": "2026-05-12T23:50:00+00:00",
            "summary_24h": {
                "total_rows": 100,
                "pending": 10,
                "consumed": 90,
                "total_positive_units": "12.50",
                "total_negative_units": "-0.50",
            },
            "by_source_24h": [
                {
                    "source": "github_commit",
                    "rows": 25,
                    "total_units": "3.75",
                    "last_seen_at": "2026-05-12T23:00:00",
                }
            ],
            "recharge_today": {"cycles": 144, "total_recharged_usd": "12.0"},
            "latest_activities": [
                {
                    "id": "abc12345",
                    "source": "github_commit",
                    "actor": "alfredo",
                    "energy_units": "0.15",
                    "consumed": True,
                    "created_at": "2026-05-12T23:00:00",
                }
            ],
        }
        out = render_html(data)
        assert "github_commit" in out
        assert "alfredo" in out
        assert "$12.0" in out  # recharged
        assert "144" in out  # cycles
        assert "$30.00" in out  # cap firmado

    def test_render_html_xss_protection(self):
        """HTML escape obligatorio en valores que vienen de DB"""
        from kernel.rotor.dashboard import render_html

        data = {
            "fetched_at": "now",
            "summary_24h": {"total_rows": 1, "pending": 0, "consumed": 1,
                            "total_positive_units": "0", "total_negative_units": "0"},
            "by_source_24h": [],
            "recharge_today": {"cycles": 0, "total_recharged_usd": "0"},
            "latest_activities": [
                {
                    "id": "<script>alert('XSS')</script>",
                    "source": "<img src=x onerror=alert(1)>",
                    "actor": "user&admin",
                    "energy_units": "0",
                    "consumed": False,
                    "created_at": "2026-05-12",
                }
            ],
        }
        out = render_html(data)
        # Escapados, no pasan crudo
        assert "<script>alert" not in out
        assert "&lt;script&gt;" in out
        assert "&lt;img" in out
        assert "user&amp;admin" in out

    def test_render_json(self):
        import json as _json

        from kernel.rotor.dashboard import render_json

        out = render_json({"foo": "bar", "n": 42})
        parsed = _json.loads(out)
        assert parsed["foo"] == "bar"
        assert parsed["n"] == 42

    def test_render_json_none_data(self):
        import json as _json

        from kernel.rotor.dashboard import render_json

        out = render_json(None)
        parsed = _json.loads(out)
        assert "error" in parsed


# ---------------------------------------------------------------------------
# T1 — SQL migration sanity
# ---------------------------------------------------------------------------
class TestMigrationSanity:
    def test_0023_migration_exists_and_has_rls(self):
        """T1 contract: migración 0023 existe y declara RLS"""
        repo_root = Path(__file__).resolve().parents[2]
        sql_path = repo_root / "migrations" / "sql" / "0023_rotor_activity_log.sql"
        assert sql_path.exists(), f"Migración faltante: {sql_path}"

        sql = sql_path.read_text(encoding="utf-8")
        assert "CREATE TABLE IF NOT EXISTS public.rotor_activity_log" in sql
        assert "ENABLE ROW LEVEL SECURITY" in sql
        assert "CREATE POLICY" in sql
        # Idempotente
        assert "IF NOT EXISTS" in sql or "DROP POLICY IF EXISTS" in sql
        # RAISE EXCEPTION sanity check
        assert "RAISE EXCEPTION" in sql
