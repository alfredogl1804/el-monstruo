"""
tests/test_cowork_rule_reinjection.py — Tests T2 (re-inyeccion periodica de reglas).

Sprint COWORK-RUNTIME-001 / T2 MAGNA P0.

DoD del prompt T2: 'Cada 5 turnos (o cuando contexto excede 50% capacidad),
inyectar bloque conciso al system prompt de Cowork: reglas duras top-5 mas
violadas, estado vivo del Monstruo, ultimo correctivo de Alfredo, pre-flight
check.'

Verifica integracion con guardian (T1 no se rompe), trigger por turnos,
trigger por contexto, trigger por correctivo pendiente, trigger por
pre-flight no ejecutado.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kernel.cowork_runtime.rule_reinjection import (
    DEFAULT_EVERY_N_TURNS,
    RuleReinjector,
)
from tools.cowork_guardian import AdvanceScore, GuardianVerdict


def _make_verdict(violations: list[str], demands: bool = True) -> GuardianVerdict:
    return GuardianVerdict(
        passed=False,
        violations=violations,
        advance_score=AdvanceScore(0, 1, 0.0),
        user_demands_advance=demands,
    )


# ============================================================================
# Trigger por cada N turnos
# ============================================================================


class TestTriggerPorTurnos:
    def test_no_reinyecta_antes_de_n_turnos(self):
        r = RuleReinjector(every_n_turns=5)
        for _ in range(4):
            r.tick(pre_flight_was_ejecutado_this_turn=True)
        assert r.should_reinject() is False

    def test_reinyecta_en_turno_n(self):
        r = RuleReinjector(every_n_turns=5)
        for _ in range(5):
            r.tick(pre_flight_was_ejecutado_this_turn=True)
        # Solo el primer tick puede setear pre_flight_ejecutado_turno_1
        assert r.state.pre_flight_ejecutado_turno_1 is True
        assert r.should_reinject() is True

    def test_mark_reinjected_resetea_contador(self):
        r = RuleReinjector(every_n_turns=3)
        for _ in range(3):
            r.tick(pre_flight_was_ejecutado_this_turn=True)
        assert r.should_reinject() is True
        r.build_reinjection_block()
        r.mark_reinjected()
        assert r.state.turnos_desde_ultima_reinyeccion == 0
        assert r.state.reinyecciones_total == 1

    def test_default_every_n_turns_es_5(self):
        assert DEFAULT_EVERY_N_TURNS == 5


# ============================================================================
# Trigger por contexto (>= threshold)
# ============================================================================


class TestTriggerPorContexto:
    def test_reinyecta_cuando_ctx_excede_threshold(self):
        r = RuleReinjector(every_n_turns=10, ctx_threshold=0.50)
        r.tick(pre_flight_was_ejecutado_this_turn=True)
        assert r.should_reinject(ctx_usage=0.45) is False
        assert r.should_reinject(ctx_usage=0.55) is True

    def test_threshold_exacto_dispara(self):
        r = RuleReinjector(every_n_turns=10, ctx_threshold=0.5)
        r.tick(pre_flight_was_ejecutado_this_turn=True)
        assert r.should_reinject(ctx_usage=0.50) is True


# ============================================================================
# Trigger por pre-flight NO ejecutado en turno 1
# ============================================================================


class TestTriggerPorPreFlight:
    def test_pre_flight_no_ejecutado_turno_1_reinyecta_en_turno_2(self):
        r = RuleReinjector(every_n_turns=10)
        r.tick(pre_flight_was_ejecutado_this_turn=False)  # turno 1 sin pre-flight
        r.tick(pre_flight_was_ejecutado_this_turn=False)  # turno 2
        assert r.should_reinject() is True
        block = r.build_reinjection_block()
        assert "Pre-flight Memento NO ejecutado" in block

    def test_pre_flight_ejecutado_turno_1_no_dispara(self):
        r = RuleReinjector(every_n_turns=10)
        r.tick(pre_flight_was_ejecutado_this_turn=True)
        r.tick()
        assert r.should_reinject() is False


# ============================================================================
# Trigger por correctivo de Alfredo pendiente
# ============================================================================


class TestTriggerPorCorrectivoAlfredo:
    def test_correctivo_pendiente_dispara_aunque_no_haya_pasado_n_turnos(self):
        r = RuleReinjector(every_n_turns=10)
        r.tick(
            correctivo_alfredo="Andate a obedecer YA",
            pre_flight_was_ejecutado_this_turn=True,
        )
        assert r.should_reinject() is True
        block = r.build_reinjection_block()
        assert "correctivo de Alfredo" in block
        assert "Andate a obedecer YA" in block


# ============================================================================
# Top-5 reglas: priorizar las matched por violaciones
# ============================================================================


class TestTopReglas:
    def test_top5_default_si_no_hay_violaciones(self):
        r = RuleReinjector()
        for _ in range(5):
            r.tick(pre_flight_was_ejecutado_this_turn=True)
        block = r.build_reinjection_block()
        # Debe contener al menos 3 codigos del fallback default
        assert "[F1]" in block
        assert "[F11]" in block
        assert "[PUSH-PAUSE]" in block

    def test_top5_priorizado_por_violaciones_acumuladas(self):
        r = RuleReinjector(every_n_turns=2)
        r.tick(
            verdict=_make_verdict(
                [
                    "MAGNA — Alfredo exige avance y Cowork sugiere parar: frase='andate a dormir', motivo=sugiere dormir",
                ]
            ),
            pre_flight_was_ejecutado_this_turn=True,
        )
        r.tick(
            verdict=_make_verdict(
                [
                    "PREMIUM — Output dominado por meta-trabajo (Cowork sobre Cowork) sin avance del Monstruo",
                ]
            )
        )
        block = r.build_reinjection_block()
        # PUSH-PAUSE y AVANCE-REAL deben aparecer
        assert "[PUSH-PAUSE]" in block
        assert "[AVANCE-REAL]" in block


# ============================================================================
# Estado vivo del Monstruo
# ============================================================================


class TestEstadoVivo:
    def test_block_incluye_estado_vivo_si_se_pasa(self):
        r = RuleReinjector()
        for _ in range(5):
            r.tick(pre_flight_was_ejecutado_this_turn=True)
        block = r.build_reinjection_block(
            estado_vivo={
                "kernel_version": "0.84.8-sprint-memento",
                "embrion_ultimo_latido_utc": "2026-05-11T05:30:00",
                "sprint_activo": "COWORK-RUNTIME-001",
                "commits_recientes": ["d67b1b6 spec(sprint)", "abc1234 feat(kernel)"],
            }
        )
        assert "0.84.8-sprint-memento" in block
        assert "COWORK-RUNTIME-001" in block
        assert "d67b1b6" in block

    def test_block_funciona_sin_estado_vivo(self):
        r = RuleReinjector()
        for _ in range(5):
            r.tick(pre_flight_was_ejecutado_this_turn=True)
        block = r.build_reinjection_block()
        assert block is not None
        assert "COWORK_REINJECT" in block


# ============================================================================
# Validaciones de constructor
# ============================================================================


class TestConstructor:
    def test_every_n_turns_invalido_lanza(self):
        with pytest.raises(ValueError):
            RuleReinjector(every_n_turns=0)

    def test_ctx_threshold_invalido_lanza(self):
        with pytest.raises(ValueError):
            RuleReinjector(ctx_threshold=0.0)
        with pytest.raises(ValueError):
            RuleReinjector(ctx_threshold=1.5)

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("COWORK_REINJECT_EVERY_N_TURNS", "3")
        monkeypatch.setenv("COWORK_REINJECT_CTX_THRESHOLD", "0.7")
        r = RuleReinjector()
        assert r.every_n_turns == 3
        assert r.ctx_threshold == 0.7


# ============================================================================
# Session health snapshot
# ============================================================================


class TestSessionHealth:
    def test_health_snapshot(self):
        r = RuleReinjector(every_n_turns=2)
        r.tick(
            verdict=_make_verdict(["MAGNA — test"]),
            pre_flight_was_ejecutado_this_turn=True,
        )
        r.tick()
        health = r.session_health()
        assert health["turnos_total"] == 2
        assert health["pre_flight_ejecutado_turno_1"] is True
        assert health["violaciones_acumuladas_count"] == 1
        assert health["every_n_turns"] == 2


# ============================================================================
# Integracion con T1 (no rompe el guardian)
# ============================================================================


class TestIntegracionConT1:
    def test_verdict_from_guardian_se_acumula_correctamente(self):
        from tools.cowork_guardian import validate_output

        r = RuleReinjector(every_n_turns=10)
        # Caso real: Cowork intenta enviar push-to-pause con Alfredo demanding
        verdict = validate_output(
            "Andate a dormir, mañana retomamos",
            "VAMOS A AVANZAR",
        )
        assert verdict.passed is False
        r.tick(verdict=verdict, pre_flight_was_ejecutado_this_turn=True)
        assert r.state.violaciones_acumuladas
        # No deberia disparar todavia (turno 1)
        assert r.should_reinject() is False or r.state.ultimo_correctivo_alfredo


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
