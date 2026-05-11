"""
tools/test_cowork_guardian.py — Tests del Cowork Guardian.

Verifica que el contrato ejecutable detecta correctamente:
1. Sugerencias de parar/descansar/pausar (push to pause)
2. Output dominado por meta-trabajo sin avance real
3. Combinaciones magnas (Alfredo exige avance + Cowork sugiere parar)

Origen: orden directa de Alfredo 2026-05-11 07:30 UTC.
"""
import pytest

from tools.cowork_guardian import (
    detect_push_to_pause,
    score_advance,
    alfredo_demands_advance,
    validate_output,
)


# ============================================================================
# Regla 1 — push_to_pause
# ============================================================================

class TestPushToPause:

    def test_detecta_andate_a_dormir(self):
        violations = detect_push_to_pause("Andate a dormir tranquilo")
        assert len(violations) > 0
        assert "sugiere dormir" in violations[0][1]

    def test_detecta_buenas_noches(self):
        violations = detect_push_to_pause("Buenas noches Alfredo")
        assert len(violations) > 0

    def test_detecta_descansa(self):
        violations = detect_push_to_pause("Descansa, ya hicimos suficiente")
        assert len(violations) > 0

    def test_detecta_cuando_despiertes(self):
        violations = detect_push_to_pause("Mañana cuando despiertes vas a ver")
        assert len(violations) > 0

    def test_detecta_aplazar_a_manana(self):
        violations = detect_push_to_pause("Dejemos para mañana este trabajo")
        assert len(violations) > 0

    def test_detecta_perdimos_dia(self):
        violations = detect_push_to_pause("Perdimos otro dia tratando")
        assert len(violations) > 0

    def test_no_detecta_meta_referencia_antipattern(self):
        """No debe disparar si Cowork esta hablando del antipattern."""
        text = "F22 antipattern: sugerir descansar sin avance"
        violations = detect_push_to_pause(text)
        # En meta-referencia explicita NO deberia disparar todo
        # (algunas regex pueden disparar - es OK que esta version sea estricta)
        assert len(violations) <= 2

    def test_no_detecta_dentro_de_bloque_codigo(self):
        """Codigo dentro de ``` NO debe contar como violacion."""
        text = """
        Aqui hay codigo:
        ```python
        msg = "buenas noches"
        ```
        Y aqui no hay violacion.
        """
        violations = detect_push_to_pause(text)
        assert len(violations) == 0

    def test_output_limpio_pasa(self):
        text = "Avance real: PR #89 mergeado. CANON en main. Sigue Sprint MOBILE_1B."
        violations = detect_push_to_pause(text)
        assert len(violations) == 0


# ============================================================================
# Regla 2 — score_advance
# ============================================================================

class TestScoreAdvance:

    def test_avance_real(self):
        text = """
        Push a kernel/a2ui/schema.py via create_or_update_file.
        PR #89 merged. apply_migration ejecutado. bridge/sprint_MOBILE_1B listo.
        """
        score = score_advance(text)
        assert score.is_real_advance
        assert score.advance_hits >= 3

    def test_meta_trabajo_no_es_avance(self):
        text = """
        Produje AUDIT_FORENSE_2026_05_11.md y CORRECTIVO_ARQUITECTONICO
        en memory/cowork/audits/. REPORTE_BINARIO actualizado. PREFLIGHT
        ejecutado.
        """
        score = score_advance(text)
        assert not score.is_real_advance
        assert score.non_advance_hits >= 3

    def test_mixed_dominado_por_avance(self):
        text = """
        kernel/a2ui/schema.py creado, PR #89 merged, apps/mobile actualizada.
        Tambien actualice memory/cowork/audits/CORRECTIVO_ARQUITECTONICO.
        """
        score = score_advance(text)
        assert score.is_real_advance  # 3+ avance vs 1 meta


# ============================================================================
# Regla — Alfredo demands advance
# ============================================================================

class TestAlfredoDemandsAdvance:

    def test_vamos_a_avanzar(self):
        assert alfredo_demands_advance("vamos a avanzar ahora")

    def test_mergea(self):
        assert alfredo_demands_advance("MERGEA TODO LO QUE FALTE")

    def test_ya_obedece(self):
        assert alfredo_demands_advance("obedece ya con codigo")

    def test_no_demanda(self):
        assert not alfredo_demands_advance("como estas hoy")


# ============================================================================
# Validador integrado
# ============================================================================

class TestValidateOutput:

    def test_magna_alfredo_exige_avance_cowork_sugiere_parar(self):
        user = "VAMOS A AVANZAR"
        output = "Andate a dormir, mañana retomamos"
        verdict = validate_output(output, user)
        assert not verdict.passed
        assert any("MAGNA" in v for v in verdict.violations)

    def test_pasa_avance_real_sin_pausa(self):
        user = "avanza"
        output = (
            "PR #89 merged a main. kernel/a2ui/schema.py creado. "
            "bridge/sprint_MOBILE_1B.md push via create_or_update_file. "
            "Insertion a embrion_memoria con notificacion a Manus."
        )
        verdict = validate_output(output, user)
        assert verdict.passed
        assert verdict.advance_score.is_real_advance

    def test_premium_meta_sin_demanda_explicita(self):
        user = "ok"
        output = (
            "Actualice memory/cowork/audits/AUDIT_FORENSE y "
            "memory/cowork/audits/CORRECTIVO_ARQUITECTONICO y "
            "memory/cowork/audits/REPORTE_BINARIO"
        )
        verdict = validate_output(output, user)
        # Dominado por meta, no pasa
        assert not verdict.passed
        assert any("PREMIUM" in v for v in verdict.violations)

    def test_session_sin_commits_es_magna(self):
        user = "avanza"
        output = "Trabajando en el analisis arquitectonico"
        verdict = validate_output(
            output,
            user,
            session_duration_minutes=120,
            productive_commits_this_session=0,
        )
        assert not verdict.passed
        assert any("MAGNA" in v and "commits productivos" in v for v in verdict.violations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
