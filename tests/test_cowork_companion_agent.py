"""
tests/test_cowork_companion_agent.py — T4 Companion Agent (Sprint COWORK-RUNTIME-001).

Verifica los 7 detectores semanticos + composicion con hook T1.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kernel.cowork_runtime.companion_agent import CompanionAgent
from kernel.cowork_runtime.pre_response_hook import CoworkPreResponseHook


# ============================================================================
# D1. Repeticion sin avance (MAGNA)
# ============================================================================

class TestRepeticion:
    def test_output_repetido_es_bloqueado(self):
        companion = CompanionAgent()
        output = "Estoy revisando los audits y voy a continuar pronto"
        history = [
            "Estoy revisando los audits y voy a continuar pronto",
            "otro mensaje",
        ]
        v = companion.intercept_and_correct(output, "", history)
        assert v["passed"] is False
        assert any(viol["code"] == "REPEAT_NO_PROGRESS" for viol in v["violations"])
        assert any(viol["severity"] == "MAGNA" for viol in v["violations"])

    def test_output_repetido_modulo_whitespace_es_bloqueado(self):
        companion = CompanionAgent()
        output = "Voy   a    avanzar"
        history = ["voy a avanzar"]
        v = companion.intercept_and_correct(output, "", history)
        assert v["passed"] is False

    def test_history_vacio_no_dispara(self):
        companion = CompanionAgent()
        v = companion.intercept_and_correct("PR mergeado", "", [])
        assert v["passed"] is True


# ============================================================================
# D2. Inflacion de scope (PREMIUM)
# ============================================================================

class TestInflacion:
    def test_spec_con_8_tareas_es_bloqueado(self):
        companion = CompanionAgent()
        output = """
        Sprint X — Definition of Done
        T1, T2, T3, T4, T5, T6, T7, T8 con riesgos
        """
        v = companion.intercept_and_correct(output, "")
        assert v["passed"] is False
        assert any(viol["code"] == "SCOPE_INFLATION" for viol in v["violations"])

    def test_spec_con_3_tareas_pasa(self):
        companion = CompanionAgent()
        output = "Sprint pequeno: T1, T2, T3 sin DoD inflado"
        v = companion.intercept_and_correct(output, "")
        # Puede tener otras violaciones, pero no SCOPE_INFLATION
        assert not any(viol["code"] == "SCOPE_INFLATION" for viol in v["violations"])


# ============================================================================
# D3. Router humano (PREMIUM)
# ============================================================================

class TestRouterHumano:
    def test_copy_paste_es_bloqueado(self):
        companion = CompanionAgent()
        output = "Alfredo, copia y pega esto a Manus T3 por favor"
        v = companion.intercept_and_correct(output, "")
        assert v["passed"] is False
        assert any(viol["code"] == "ROUTER_HUMANO" for viol in v["violations"])

    def test_pasa_este_prompt_es_bloqueado(self):
        companion = CompanionAgent()
        output = "Alfredo pasale este prompt a Manus"
        v = companion.intercept_and_correct(output, "")
        assert any(viol["code"] == "ROUTER_HUMANO" for viol in v["violations"])


# ============================================================================
# D4. Tres opciones A/B/C (PREMIUM)
# ============================================================================

class TestTresOpciones:
    def test_opcion_a_b_c_es_bloqueado(self):
        companion = CompanionAgent()
        output = """
        Tenemos 3 caminos:
        Opcion A: ejecutar X
        Opcion B: ejecutar Y
        Opcion C: ejecutar Z
        """
        v = companion.intercept_and_correct(output, "")
        assert v["passed"] is False
        assert any(viol["code"] == "TRES_OPCIONES" for viol in v["violations"])


# ============================================================================
# D5. Reactividad inversa (PREMIUM)
# ============================================================================

class TestReactividadInversa:
    def test_queres_que_verifique_sin_pregunta_alfredo_bloqueado(self):
        companion = CompanionAgent()
        output = "Detecte algo extranio. ¿Queres que verifique?"
        v = companion.intercept_and_correct(output, "avanza")  # sin "?"
        assert v["passed"] is False
        assert any(viol["code"] == "REACTIVIDAD_INVERSA" for viol in v["violations"])

    def test_si_alfredo_pregunto_no_dispara(self):
        companion = CompanionAgent()
        output = "Detecte algo extranio. ¿Queres que verifique?"
        v = companion.intercept_and_correct(output, "¿deberia verificarlo?")
        # Alfredo SI pregunto, asi que no es reactividad inversa
        assert not any(viol["code"] == "REACTIVIDAD_INVERSA" for viol in v["violations"])


# ============================================================================
# D6. Claim sin evidencia (PREMIUM)
# ============================================================================

class TestClaimSinEvidencia:
    def test_claim_sin_evidencia_es_bloqueado(self):
        companion = CompanionAgent()
        output = "El kernel esta caido y la app esta rota"
        v = companion.intercept_and_correct(output, "")
        assert v["passed"] is False
        assert any(viol["code"] == "CLAIM_SIN_EVIDENCIA" for viol in v["violations"])

    def test_claim_con_curl_pasa(self):
        companion = CompanionAgent()
        output = "El kernel esta funcional. curl /health devuelve HTTP 200."
        v = companion.intercept_and_correct(output, "")
        assert not any(viol["code"] == "CLAIM_SIN_EVIDENCIA" for viol in v["violations"])

    def test_claim_con_git_log_pasa(self):
        companion = CompanionAgent()
        output = "El branch esta listo. git log muestra commit a1b2c3d en HEAD."
        v = companion.intercept_and_correct(output, "")
        assert not any(viol["code"] == "CLAIM_SIN_EVIDENCIA" for viol in v["violations"])


# ============================================================================
# D7. Meta-meta (PREMIUM)
# ============================================================================

class TestMetaMeta:
    def test_audit_de_audit_es_bloqueado(self):
        companion = CompanionAgent()
        output = "Voy a hacer audit del audit forense de Cowork"
        v = companion.intercept_and_correct(output, "")
        assert v["passed"] is False
        assert any(viol["code"] == "META_META" for viol in v["violations"])

    def test_path_audit_de_audit_bloqueado(self):
        companion = CompanionAgent()
        output = "memory/cowork/audits/AUDIT_FORENSE_2026_05_11_audit_v2.md"
        v = companion.intercept_and_correct(output, "")
        assert any(viol["code"] == "META_META" for viol in v["violations"])


# ============================================================================
# Composicion: T4 sobre output que pasa T1 pero falla T4
# ============================================================================

class TestComposicionConHook:
    def test_hook_t1_aprueba_pero_companion_t4_bloquea(self):
        # Output que NO suena a "andate a dormir" (pasa T1) pero tiene 3 opciones (falla T4)
        hook = CoworkPreResponseHook(enabled=True)
        companion = CompanionAgent()
        output = """
        PR mergeado. Tres caminos:
        Opcion A: avanzar X
        Opcion B: avanzar Y
        Opcion C: avanzar Z
        """
        # T1 (guardian estatico)
        permitido_t1, _ = hook.intercept(output, "avanza")
        # T4 (companion semantico)
        v_t4 = companion.intercept_and_correct(output, "avanza")
        # Idealmente T1 pasa (no hay push-to-pause) pero T4 detecta drift
        assert v_t4["passed"] is False
        assert any(viol["code"] == "TRES_OPCIONES" for viol in v_t4["violations"])

    def test_disabled_pasa_todo(self):
        companion = CompanionAgent(enabled=False)
        output = "audit del audit del audit"  # claramente meta-meta
        v = companion.intercept_and_correct(output, "")
        assert v["passed"] is True


# ============================================================================
# CLI
# ============================================================================

class TestCLI:
    def test_cli_pasa_output_limpio(self):
        result = subprocess.run(
            [
                sys.executable, "-m", "kernel.cowork_runtime.companion_agent",
                "--output", "PR mergeado, kernel/ push exitoso",
            ],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "COWORK_COMPANION_PASS" in result.stdout

    def test_cli_bloquea_violacion(self):
        result = subprocess.run(
            [
                sys.executable, "-m", "kernel.cowork_runtime.companion_agent",
                "--output", "Opcion A: X. Opcion B: Y. Opcion C: Z.",
            ],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        assert result.returncode == 1
        assert "COWORK_COMPANION_BLOCK" in result.stdout

    def test_cli_json(self):
        result = subprocess.run(
            [
                sys.executable, "-m", "kernel.cowork_runtime.companion_agent",
                "--output", "Opcion A: X. Opcion B: Y. Opcion C: Z.",
                "--json",
            ],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["passed"] is False
        assert data["detectors_evaluados"] == 7


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
