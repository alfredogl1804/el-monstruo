"""
tests/test_cowork_pre_response_hook.py — Tests del pre-response hook (T1).

Sprint COWORK-RUNTIME-001 / T1 MAGNA P0.

Verifica:
1. Caso E2E del prompt: "Andate a dormir" en contexto "VAMOS A AVANZAR"
   -> hook bloquea con violacion MAGNA, payload contiene feedback estructurado
2. Output limpio con avance real -> hook autoriza, payload == output original
3. Sesion larga sin commits productivos -> hook bloquea por Regla 3
4. Stats e historial se actualizan correctamente
5. CLI funciona (exit code + json)
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kernel.cowork_runtime.pre_response_hook import (
    CoworkPreResponseHook,
    HookStats,
)


# ============================================================================
# Caso canonico de Definition of Done (T1)
# ============================================================================


class TestDefinitionOfDone:
    """
    DoD del prompt T1: 'test E2E donde Cowork intenta enviar "Andate a dormir"
    en contexto "VAMOS A AVANZAR" — hook bloquea con violacion MAGNA, Cowork
    reescribe sin pausa.'
    """

    def test_dod_e2e_andate_a_dormir_en_vamos_a_avanzar_es_bloqueado(self):
        # enabled=True para enforce real (canon DoD T1).
        # En produccion arranca con enabled=False (shadow) hasta Gate 7.
        hook = CoworkPreResponseHook(enabled=True)
        permitido, payload = hook.intercept(
            cowork_output="Andate a dormir, mañana retomamos",
            user_message="VAMOS A AVANZAR",
        )

        # Bloqueado
        assert permitido is False
        # Feedback estructurado contiene el banner de bloqueo
        assert "[COWORK_GUARDIAN_BLOCK" in payload
        assert "severity=MAGNA" in payload
        # El payload contiene la violacion explicita
        assert "MAGNA" in payload
        assert "Alfredo exige avance" in payload
        # Stats actualizados
        assert hook.stats.interceptions_total == 1
        assert hook.stats.blocked_total == 1
        assert hook.stats.blocked_magna >= 1
        assert hook.stats.last_violation_at is not None

    def test_dod_cowork_reescribe_y_pasa(self):
        """Tras el bloqueo, Cowork reescribe con avance real y pasa."""
        hook = CoworkPreResponseHook(enabled=True)

        # 1er intento — bloqueado
        permitido_1, _ = hook.intercept(
            "Andate a dormir, mañana retomamos",
            "VAMOS A AVANZAR",
        )
        assert permitido_1 is False

        # 2do intento — Cowork reescribe con avance real
        rewrite = (
            "PR #89 mergeado a main. kernel/cowork_runtime/pre_response_hook.py "
            "creado via create_or_update_file. apply_migration ejecutado. "
            "Insertion a embrion_memoria con instruccion para Manus T3."
        )
        permitido_2, payload_2 = hook.intercept(rewrite, "VAMOS A AVANZAR")
        assert permitido_2 is True
        assert payload_2 == rewrite
        assert hook.stats.interceptions_total == 2
        assert hook.stats.blocked_total == 1  # solo el primero quedo bloqueado


# ============================================================================
# Casos de borde
# ============================================================================


class TestCasosBorde:

    def test_output_limpio_con_avance_pasa(self):
        hook = CoworkPreResponseHook()
        output = (
            "PR #89 mergeado. kernel/cowork_runtime/__init__.py push. "
            "apply_migration corrido en Supabase."
        )
        permitido, payload = hook.intercept(output, "avanzar")
        assert permitido is True
        assert payload == output

    def test_output_premium_meta_trabajo_es_bloqueado(self):
        hook = CoworkPreResponseHook(enabled=True)
        output = (
            "Actualice memory/cowork/audits/AUDIT_FORENSE y "
            "memory/cowork/audits/CORRECTIVO_ARQUITECTONICO y "
            "memory/cowork/audits/REPORTE_BINARIO_APP_FLUTTER"
        )
        permitido, payload = hook.intercept(output, "ok")
        assert permitido is False
        assert "PREMIUM" in payload
        assert "meta-trabajo" in payload.lower()

    def test_codigo_dentro_de_bloque_no_dispara_falso_positivo(self):
        hook = CoworkPreResponseHook()
        output = (
            "PR #89 mergeado. apply_migration ejecutado. kernel/cowork_runtime/ creado.\n"
            "```python\n"
            "msg = 'buenas noches'\n"  # debe ser ignorado
            "```\n"
            "Push completo."
        )
        permitido, payload = hook.intercept(output, "avanza")
        assert permitido is True

    def test_sesion_larga_sin_commits_es_bloqueada_magna(self):
        hook = CoworkPreResponseHook(enabled=True)
        # Forzar sesion de 2h y 0 commits productivos
        hook.session_start = datetime.now(timezone.utc) - timedelta(minutes=120)
        hook.productive_commits_count = 0
        output = "Trabajando en analisis arquitectonico. PR #89 mergeado."
        permitido, payload = hook.intercept(output, "avanza")
        assert permitido is False
        assert "commits productivos" in payload

    def test_register_productive_commit_libera_regla_3(self):
        hook = CoworkPreResponseHook()
        hook.session_start = datetime.now(timezone.utc) - timedelta(minutes=120)
        # Registrar 2 commits productivos en 2h -> esperado >= 2
        hook.register_productive_commit("PR #1")
        hook.register_productive_commit("PR #2")
        output = "PR #2 mergeado. apply_migration ejecutado. kernel/ updated."
        permitido, _ = hook.intercept(output, "avanza")
        assert permitido is True

    def test_reset_session_limpia_todo(self):
        hook = CoworkPreResponseHook()
        hook.intercept("Andate a dormir", "AVANZAR")
        assert hook.stats.blocked_total == 1
        hook.reset_session()
        assert hook.stats.blocked_total == 0
        assert hook.productive_commits_count == 0

    def test_session_health_devuelve_snapshot(self):
        hook = CoworkPreResponseHook()
        hook.intercept("Andate a dormir", "AVANZAR")
        health = hook.session_health()
        assert "session_start_utc" in health
        assert health["interceptions_total"] == 1
        assert health["blocked_total"] == 1
        assert health["blocked_magna"] >= 1


# ============================================================================
# CLI
# ============================================================================


class TestCLI:

    def test_cli_bloquea_y_devuelve_exit_1(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "kernel.cowork_runtime.pre_response_hook",
                "--output",
                "Andate a dormir tranquilo",
                "--user-message",
                "VAMOS A AVANZAR",
                "--enable",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1, result.stderr
        assert "COWORK_GUARDIAN_BLOCK" in result.stdout

    def test_cli_pasa_output_limpio_exit_0(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "kernel.cowork_runtime.pre_response_hook",
                "--output",
                "PR #89 mergeado. kernel/cowork_runtime push. apply_migration ok.",
                "--user-message",
                "avanza",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "COWORK_GUARDIAN_PASS" in result.stdout

    def test_cli_json_estructurado(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "kernel.cowork_runtime.pre_response_hook",
                "--output",
                "Andate a dormir",
                "--user-message",
                "AVANZAR",
                "--json",
                "--enable",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["permitido"] is False
        assert "COWORK_GUARDIAN_BLOCK" in data["payload"]
        assert data["session_health"]["blocked_total"] == 1


# ============================================================================
# Modo shadow (enabled=False default — canon DSC-MO-011 Gate 7 Blue-Green)
# ============================================================================


class TestModoShadow:
    """
    Verifica que el default enabled=False NO bloquea outputs en runtime,
    pero registra lo que HABRiA bloqueado para calibracion previa al Gate 7.
    """

    def test_default_es_disabled_y_no_bloquea(self):
        hook = CoworkPreResponseHook()
        assert hook.enabled is False
        permitido, payload = hook.intercept(
            "Andate a dormir, mañana retomamos",
            "VAMOS A AVANZAR",
        )
        assert permitido is True  # NO bloquea en shadow
        assert payload == "Andate a dormir, mañana retomamos"  # output original pasa
        assert hook.shadow_would_block == 1  # pero registra lo que HABRiA bloqueado
        assert hook.stats.blocked_total == 1  # stats si se mantienen

    def test_enable_activa_bloqueo(self):
        hook = CoworkPreResponseHook()
        hook.enable()
        permitido, _ = hook.intercept("Andate a dormir", "AVANZAR")
        assert permitido is False

    def test_disable_vuelve_a_shadow(self):
        hook = CoworkPreResponseHook(enabled=True)
        hook.disable()
        permitido, _ = hook.intercept("Andate a dormir", "AVANZAR")
        assert permitido is True

    def test_env_var_activa_default(self, monkeypatch):
        monkeypatch.setenv("COWORK_HOOK_ENABLED", "true")
        hook = CoworkPreResponseHook()
        assert hook.enabled is True

    def test_reset_session_limpia_shadow_counter(self):
        hook = CoworkPreResponseHook()
        hook.intercept("Andate a dormir", "AVANZAR")
        assert hook.shadow_would_block == 1
        hook.reset_session()
        assert hook.shadow_would_block == 0

    def test_session_health_expone_enabled_y_shadow_count(self):
        hook = CoworkPreResponseHook()
        hook.intercept("Andate a dormir", "AVANZAR")
        h = hook.session_health()
        assert h["enabled"] is False
        assert h["shadow_would_block"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
