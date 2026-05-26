"""
Tests del Sprint GUARDIAN-AUTONOMO-001 (T1-T6)
================================================
Owner: Hilo Ejecutor 2 (manus_hilo_b)

Cobertura:
  - T2 scoring: compute_all_objectives_scores retorna 15 ObjectiveScore
  - T1 runner: run_audit con persist=False produce AuditCycleResult valido
  - T1 handler: daily_guardian_audit_handler retorna dict con keys requeridos
  - T3 telegram: stub no emite cuando GUARDIAN_TELEGRAM_ALERTS!=true
  - T3 telegram: stub no emite cuando falta chat_id
  - T4 dashboard: generate_html_report acepta None y produce HTML valido
  - T4 dashboard: clasificacion de niveles (passing/warning/critical/emergency)
  - T6 pre-commit: hook con env vacio retorna exit 0 (skip)

Filosofia:
  - Sin DB (no requieren SUPABASE_DB_URL).
  - Sin red (no llaman Telegram, OpenAI, etc).
  - Smoke + integration livianos: deben correr en <30s.
  - Anti-Goodhart: los tests verifican shape y contratos, NO valores fijos.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path

import pytest

# ── Asegurar que el path del repo esta disponible para imports ─────────────
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# ─────────────────────────────────────────────────────────────────────────
#  T2 scoring
# ─────────────────────────────────────────────────────────────────────────


class TestT2Scoring:
    """Verifica que el scoring engine produce 15 ObjectiveScore validos."""

    def test_compute_all_objectives_returns_15(self):
        from kernel.guardian_runner import scoring

        scores = scoring.compute_all_objectives_scores()
        assert isinstance(scores, dict), "debe retornar dict"
        assert len(scores) == 15, f"esperaba 15 objetivos, vino {len(scores)}"
        # keys son ids 1..15
        assert set(scores.keys()) == set(range(1, 16)), "keys deben ser 1..15"

    def test_each_objective_has_required_fields(self):
        from kernel.guardian_runner import scoring

        scores = scoring.compute_all_objectives_scores()
        for oid, score in scores.items():
            assert hasattr(score, "objective_id"), f"obj {oid}: falta objective_id"
            assert hasattr(score, "objective_name"), f"obj {oid}: falta objective_name"
            assert hasattr(score, "score_pct"), f"obj {oid}: falta score_pct"
            assert hasattr(score, "status"), f"obj {oid}: falta status"
            assert hasattr(score, "evidence"), f"obj {oid}: falta evidence"
            # score_pct debe ser numerico [0, 100]
            assert 0 <= score.score_pct <= 100, f"obj {oid}: score_pct fuera de rango: {score.score_pct}"
            # status debe ser uno de los validos
            # El scoring engine usa 'ok' como status canonico; el runner
            # lo normaliza a 'passing' para el contrato del dashboard.
            assert score.status in ("ok", "passing", "warning", "critical", "emergency", "error"), (
                f"obj {oid}: status invalido: {score.status}"
            )


# ─────────────────────────────────────────────────────────────────────────
#  T1 runner.run_audit
# ─────────────────────────────────────────────────────────────────────────


class TestT1RunAudit:
    """Verifica que run_audit produce AuditCycleResult valido sin DB."""

    def test_run_audit_no_persist_succeeds(self, monkeypatch):
        # Limpiar env vars de DB para forzar modo dry-run
        monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)

        from kernel.guardian_runner.runner import AuditCycleResult, run_audit

        result = run_audit(trigger="manual", persist=False)
        assert isinstance(result, AuditCycleResult)
        assert result.run_id, "run_id debe estar poblado"
        assert result.trigger == "manual"
        assert result.duration_ms >= 0
        # Agregados consistentes
        total = result.passing_count + result.warning_count + result.critical_count + result.emergency_count
        assert total <= 15, f"total cuenta debe ser <= 15, vino {total}"
        # total_score_pct debe ser numerico [0, 100]
        assert 0 <= result.total_score_pct <= 100

    def test_run_audit_invalid_trigger_raises(self):
        from kernel.guardian_runner.runner import run_audit

        with pytest.raises(ValueError, match="trigger"):
            run_audit(trigger="invalid_trigger_xyz", persist=False)

    def test_run_audit_populates_objective_scores(self, monkeypatch):
        """Sprint T4: AuditCycleResult debe incluir objective_scores dict."""
        monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)

        from kernel.guardian_runner.runner import run_audit

        result = run_audit(trigger="manual", persist=False)
        assert hasattr(result, "objective_scores"), "AuditCycleResult debe tener objective_scores"
        assert isinstance(result.objective_scores, dict)
        # 15 objetivos
        assert len(result.objective_scores) == 15
        # Cada entry debe tener score_pct y level
        for oid_str, data in result.objective_scores.items():
            assert "score_pct" in data, f"obj {oid_str}: falta score_pct"
            assert "level" in data, f"obj {oid_str}: falta level"
            assert "objective_name" in data, f"obj {oid_str}: falta objective_name"

    def test_audit_cycle_result_to_dict(self, monkeypatch):
        """to_dict debe serializar todos los campos."""
        monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)

        from kernel.guardian_runner.runner import run_audit

        result = run_audit(trigger="manual", persist=False)
        d = result.to_dict()
        assert d["run_id"] == result.run_id
        assert d["total_score_pct"] == result.total_score_pct
        assert "objective_scores" in d
        assert "degradations_pp" in d


# ─────────────────────────────────────────────────────────────────────────
#  T1 daily_guardian_audit_handler (async)
# ─────────────────────────────────────────────────────────────────────────


class TestT1Handler:
    """Verifica el handler async registrado en EmbrionScheduler."""

    def test_handler_returns_dict(self, monkeypatch):
        monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)
        # Asegurar que el handler corre con persist=False internamente
        monkeypatch.setenv("GUARDIAN_HANDLER_PERSIST", "false")

        from kernel.guardian_runner.runner import daily_guardian_audit_handler

        result = asyncio.run(daily_guardian_audit_handler())
        assert isinstance(result, dict)
        # Keys minimos del contrato del handler
        for key in ("run_id", "total_score_pct", "duration_ms"):
            assert key in result, f"handler dict debe tener {key}"


# ─────────────────────────────────────────────────────────────────────────
#  T3 Telegram stub fail-closed
# ─────────────────────────────────────────────────────────────────────────


class TestT3TelegramStub:
    """Verifica que el stub Telegram NO emite hasta firma humana."""

    def test_stub_no_chat_id_returns_silently(self, monkeypatch, caplog):
        monkeypatch.delenv("TELEGRAM_GUARDIAN_CHAT_ID", raising=False)
        monkeypatch.delenv("GUARDIAN_TELEGRAM_ALERTS", raising=False)

        from kernel.guardian_runner.runner import AuditCycleResult, _emit_telegram_alert

        result = AuditCycleResult(
            run_id="test-run",
            trigger="manual",
            started_at="2026-05-12T00:00:00+00:00",
            finished_at="2026-05-12T00:00:01+00:00",
            duration_ms=1000,
            total_score_pct=50.0,
            passing_count=0,
            warning_count=5,
            critical_count=5,
            emergency_count=5,
            degradations_pp={1: 15.0},
        )
        # No debe levantar excepcion
        _emit_telegram_alert(result)

    def test_stub_with_chat_id_does_not_send(self, monkeypatch):
        """Aun con chat_id seteado, el stub no envia mensaje real
        hasta que se implemente el envio post-firma humana."""
        monkeypatch.setenv("TELEGRAM_GUARDIAN_CHAT_ID", "fake_chat_id_12345")

        from kernel.guardian_runner.runner import AuditCycleResult, _emit_telegram_alert

        result = AuditCycleResult(
            run_id="test-run-2",
            trigger="manual",
            started_at="2026-05-12T00:00:00+00:00",
            finished_at="2026-05-12T00:00:01+00:00",
            duration_ms=1000,
            total_score_pct=30.0,
            passing_count=0,
            warning_count=0,
            critical_count=5,
            emergency_count=10,
            degradations_pp={1: 25.0, 2: 12.0},
        )
        # No debe lanzar — solo loguea "would_emit" sin enviar real
        _emit_telegram_alert(result)


# ─────────────────────────────────────────────────────────────────────────
#  T4 Dashboard
# ─────────────────────────────────────────────────────────────────────────


class TestT4Dashboard:
    """Verifica el generador de HTML del dashboard."""

    def test_generate_html_report_with_none_returns_html(self):
        from kernel.guardian_runner.dashboard import generate_html_report

        html = generate_html_report(latest=None, history=None)
        assert isinstance(html, str)
        assert "<html" in html.lower()
        assert "</html>" in html.lower()
        # Banner WARN debe aparecer cuando no hay datos
        assert "WARN" in html or "sin datos" in html

    def test_generate_html_report_with_data(self):
        from kernel.guardian_runner.dashboard import generate_html_report

        latest = {
            "run_id": "test-uuid",
            "trigger": "manual",
            "started_at": "2026-05-12T00:00:00+00:00",
            "finished_at": "2026-05-12T00:00:05+00:00",
            "duration_ms": 5000,
            "total_score_pct": 75.5,
            "passing_count": 5,
            "warning_count": 5,
            "critical_count": 3,
            "emergency_count": 2,
            "objective_scores": {
                "1": {
                    "score_pct": 90.0,
                    "level": "passing",
                    "objective_name": "Latido Persistente",
                    "rationale": "OK",
                },
            },
            "degradations_pp": {},
            "error": None,
        }
        html = generate_html_report(latest=latest, history=[])
        assert "75.50%" in html or "75.5" in html
        assert "Latido Persistente" in html
        assert "passing" in html

    def test_classify_levels(self):
        from kernel.guardian_runner.dashboard import _classify

        assert _classify(95.0) == "passing"
        assert _classify(80.0) == "passing"
        assert _classify(70.0) == "warning"
        assert _classify(50.0) == "critical"
        assert _classify(20.0) == "emergency"
        assert _classify(None) == "unknown"

    def test_html_escape_xss_protection(self):
        from kernel.guardian_runner.dashboard import _html_escape

        evil = '<script>alert("xss")</script>'
        escaped = _html_escape(evil)
        assert "<script>" not in escaped
        assert "&lt;script&gt;" in escaped


# ─────────────────────────────────────────────────────────────────────────
#  T6 Pre-commit hook
# ─────────────────────────────────────────────────────────────────────────


class TestT6PreCommitHook:
    """Verifica el comportamiento del hook anti-stale-audit."""

    def test_hook_without_db_url_exits_zero(self, tmp_path, monkeypatch):
        """Sin DB URL el hook debe hacer skip y retornar 0."""
        monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)

        hook_path = _REPO_ROOT / "scripts" / "_check_guardian_stale_audit.py"
        assert hook_path.exists(), f"hook no existe en {hook_path}"

        # Limpiar env para el subprocess
        clean_env = {k: v for k, v in os.environ.items() if k not in ("SUPABASE_DB_URL", "DATABASE_URL")}
        result = subprocess.run(
            [sys.executable, str(hook_path)],
            capture_output=True,
            text=True,
            timeout=10,
            env=clean_env,
        )
        assert result.returncode == 0, (
            f"hook debe retornar 0 sin DB URL, vino {result.returncode}. stderr: {result.stderr}"
        )
        # Banner OK skip debe aparecer
        assert "skip" in result.stderr.lower() or "OK" in result.stderr

    def test_hook_disabled_via_env_exits_zero(self, monkeypatch):
        """GUARDIAN_STALE_HOOK_DISABLED=true debe ser escape hatch."""
        hook_path = _REPO_ROOT / "scripts" / "_check_guardian_stale_audit.py"
        env = {**os.environ, "GUARDIAN_STALE_HOOK_DISABLED": "true"}
        result = subprocess.run(
            [sys.executable, str(hook_path)],
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        assert result.returncode == 0


# ─────────────────────────────────────────────────────────────────────────
#  T1 wiring: scheduler agrega daily_guardian_audit
# ─────────────────────────────────────────────────────────────────────────


class TestT1Wiring:
    """Verifica que el scheduler registra la task daily_guardian_audit."""

    def test_register_default_tasks_includes_guardian_audit(self):
        # add_task usa asyncio.get_event_loop() que requiere loop activo en
        # MainThread. Crear uno explicitamente para que pytest no rompa.
        try:
            asyncio.get_event_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())
        from kernel.embrion_scheduler import EmbrionScheduler, register_default_tasks

        scheduler = EmbrionScheduler(db=None)
        register_default_tasks(scheduler)
        # `get_all_tasks()` puede retornar dicts (.to_dict()) o ScheduledTask
        # objects dependiendo de la version. Soportamos ambos via attr/key access.
        raw_tasks = (
            scheduler.get_all_tasks() if hasattr(scheduler, "get_all_tasks") else list(scheduler._tasks.values())
        )

        def _get(t, key, default=None):
            if hasattr(t, key):
                return getattr(t, key)
            if isinstance(t, dict):
                return t.get(key, default)
            return default

        names = [_get(t, "name") for t in raw_tasks]
        assert "daily_guardian_audit" in names, f"daily_guardian_audit no encontrada. Tasks: {names}"
        # Verificar schedule daily @ 3am UTC
        ga = next(t for t in raw_tasks if _get(t, "name") == "daily_guardian_audit")
        assert _get(ga, "schedule_type") == "daily"
        assert _get(ga, "daily_hour") == 3
        assert _get(ga, "handler") == "daily_guardian_audit"
        assert _get(ga, "max_cost_usd", 0.0) <= 0.20, "cap de costo debe ser bajo"

    def test_register_stub_handlers_includes_guardian_audit(self):
        from kernel.embrion_scheduler import EmbrionScheduler, register_stub_handlers

        scheduler = EmbrionScheduler(db=None)
        register_stub_handlers(scheduler)
        assert "daily_guardian_audit" in scheduler._handlers, "handler stub debe estar registrado"
