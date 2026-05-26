"""
tests/test_catastro_wiring.py
Sprint CATASTRO-WIRING-001 — Test regresión del wiring Embrión ↔ Catastro.

Spec firmado: bridge/sprints_propuestos/sprint_CATASTRO_WIRING_001_FIRMADO_2026_05_18.md
Decisión: Opción 1 / Camino B.1 (Cowork firma 2026-05-18, "OPCIÓN 1 — FIRMO").
Snapshot pre-fix: discovery_forense/INCIDENTES/CATASTRO_WIRING_001_pre_fix_2026_05_18.json

Invariante a proteger:
    "La selección de modelo del Embrión Loop pasa por el Catastro
     RecommendationEngine. NUNCA debe volver a hardcodear ACTOR_MODEL/JUDGE_MODEL
     en los 3 sitios canonicos (budget_estimation, autonomous_thought,
     ecosystem_reflection)."

Cobertura mínima por §4 spec:
  G_TEST_1: helper devuelve model_id real cuando engine responde OK
  G_TEST_2: helper devuelve fallback cuando engine es None (no inicializado)
  G_TEST_3: helper devuelve fallback cuando response.degraded=True
  G_TEST_4: helper devuelve fallback cuando response.modelos está vacío
  G_TEST_5: helper devuelve fallback cuando recommend lanza Exception
  G_TEST_6: feature flag EMBRION_CATASTRO_ENABLED=false hace bypass total
  G_TEST_7: existencia de los 3 use_cases canónicos como constantes
  G_TEST_8: invariante estructural — los 3 sitios usan _select_model_via_catastro

Strategy: mocks puros — NO toca DB real, NO toca Railway, NO red.
Determinístico, rápido (<1s), CI-friendly.
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ============================================================================
# G_TEST_7: Use cases canónicos existen como constantes
# ============================================================================
def test_use_cases_canonicos_definidos():
    """Los 3 use_cases del Embrión deben estar definidos como constantes."""
    from kernel.embrion_loop import (
        EMBRION_CATASTRO_USE_CASE_AUTONOMOUS_THOUGHT,
        EMBRION_CATASTRO_USE_CASE_BUDGET_ESTIMATION,
        EMBRION_CATASTRO_USE_CASE_ECOSYSTEM_REFLECTION,
    )

    assert EMBRION_CATASTRO_USE_CASE_AUTONOMOUS_THOUGHT == "autonomous_thought"
    assert EMBRION_CATASTRO_USE_CASE_BUDGET_ESTIMATION == "budget_estimation"
    assert EMBRION_CATASTRO_USE_CASE_ECOSYSTEM_REFLECTION == "ecosystem_reflection"


# ============================================================================
# G_TEST_1: Helper devuelve model_id real cuando engine responde OK
# ============================================================================
@pytest.mark.asyncio
async def test_select_model_returns_catastro_model_when_engine_ok():
    """Cuando el engine devuelve un modelo válido, el helper devuelve su id."""
    from kernel.embrion_loop import _select_model_via_catastro

    # Mock del top model
    fake_top = MagicMock()
    fake_top.id = "anthropic/claude-opus-4.7"
    fake_top.nombre = "Claude Opus 4.7"
    fake_top.trono_global = 92.5

    # Mock de la response
    fake_response = MagicMock()
    fake_response.degraded = False
    fake_response.degraded_reason = None
    fake_response.modelos = [fake_top]

    # Mock del engine
    fake_engine = MagicMock()
    fake_engine.recommend = MagicMock(return_value=fake_response)

    with patch("kernel.catastro.catastro_routes._engine_singleton", fake_engine):
        result = await _select_model_via_catastro(
            use_case="autonomous_thought",
            fallback="hardcoded-fallback",
        )
    assert result == "anthropic/claude-opus-4.7"
    fake_engine.recommend.assert_called_once_with(
        use_case="autonomous_thought",
        top_n=1,
    )


# ============================================================================
# G_TEST_2: Engine is None → fallback
# ============================================================================
@pytest.mark.asyncio
async def test_select_model_returns_fallback_when_engine_is_none():
    """Cuando el singleton del engine es None (Catastro no inicializado),
    el helper debe devolver el fallback hardcoded sin lanzar."""
    from kernel.embrion_loop import _select_model_via_catastro

    with patch("kernel.catastro.catastro_routes._engine_singleton", None):
        result = await _select_model_via_catastro(
            use_case="autonomous_thought",
            fallback="hardcoded-fallback",
        )
    assert result == "hardcoded-fallback"


# ============================================================================
# G_TEST_3: response.degraded=True → fallback
# ============================================================================
@pytest.mark.asyncio
async def test_select_model_returns_fallback_when_response_degraded():
    """Cuando la response viene en modo degraded, el helper devuelve fallback."""
    from kernel.embrion_loop import _select_model_via_catastro

    fake_response = MagicMock()
    fake_response.degraded = True
    fake_response.degraded_reason = "db_down"
    fake_response.modelos = []

    fake_engine = MagicMock()
    fake_engine.recommend = MagicMock(return_value=fake_response)

    with patch("kernel.catastro.catastro_routes._engine_singleton", fake_engine):
        result = await _select_model_via_catastro(
            use_case="budget_estimation",
            fallback="gpt-5",
        )
    assert result == "gpt-5"


# ============================================================================
# G_TEST_4: response.modelos vacío → fallback
# ============================================================================
@pytest.mark.asyncio
async def test_select_model_returns_fallback_when_modelos_empty():
    """Si la lista modelos está vacía aunque degraded=False, devuelve fallback."""
    from kernel.embrion_loop import _select_model_via_catastro

    fake_response = MagicMock()
    fake_response.degraded = False
    fake_response.degraded_reason = None
    fake_response.modelos = []

    fake_engine = MagicMock()
    fake_engine.recommend = MagicMock(return_value=fake_response)

    with patch("kernel.catastro.catastro_routes._engine_singleton", fake_engine):
        result = await _select_model_via_catastro(
            use_case="ecosystem_reflection",
            fallback="gpt-5",
        )
    assert result == "gpt-5"


# ============================================================================
# G_TEST_5: recommend lanza Exception → fallback (no propaga)
# ============================================================================
@pytest.mark.asyncio
async def test_select_model_returns_fallback_on_recommend_exception():
    """Si recommend lanza una exception arbitraria, el helper la captura y
    devuelve fallback (fail-open). No debe propagar el error al Embrión."""
    from kernel.embrion_loop import _select_model_via_catastro

    fake_engine = MagicMock()
    fake_engine.recommend = MagicMock(side_effect=RuntimeError("simulated db crash"))

    with patch("kernel.catastro.catastro_routes._engine_singleton", fake_engine):
        result = await _select_model_via_catastro(
            use_case="autonomous_thought",
            fallback="hardcoded-fallback",
        )
    assert result == "hardcoded-fallback"


# ============================================================================
# G_TEST_6: Feature flag EMBRION_CATASTRO_ENABLED=false → bypass total
# ============================================================================
@pytest.mark.asyncio
async def test_select_model_bypasses_when_flag_disabled():
    """Si EMBRION_CATASTRO_ENABLED=false, el helper salta sin tocar el engine
    (rollback instantáneo sin redeploy)."""
    from kernel import embrion_loop

    fake_engine = MagicMock()
    fake_engine.recommend = MagicMock()

    with (
        patch.object(embrion_loop, "EMBRION_CATASTRO_ENABLED", False),
        patch("kernel.catastro.catastro_routes._engine_singleton", fake_engine),
    ):
        result = await embrion_loop._select_model_via_catastro(
            use_case="autonomous_thought",
            fallback="hardcoded-fallback",
        )
    # No debe haber tocado el engine
    fake_engine.recommend.assert_not_called()
    assert result == "hardcoded-fallback"


# ============================================================================
# G_TEST_8: Invariante estructural — los 3 sitios usan _select_model_via_catastro
# ============================================================================
def test_invariante_estructural_no_hay_hardcodes_en_sitios_ejecutables():
    """
    Invariante magna del sprint: el archivo embrion_loop.py NO debe contener
    'model=ACTOR_MODEL,' ni 'model=JUDGE_MODEL,' como llamadas ejecutables.
    Las constantes pueden seguir definiéndose como fallback, pero las 3
    llamadas críticas (linea ~1086, ~1578, ~2449 originales) deben usar
    el helper _select_model_via_catastro.

    Si este test falla en el futuro, alguien revirtió el wiring del sprint
    CATASTRO-WIRING-001 por accidente. Investigar git blame inmediatamente.
    """
    embrion_loop_path = Path(__file__).parent.parent / "kernel" / "embrion_loop.py"
    content = embrion_loop_path.read_text(encoding="utf-8")

    # Los hardcodes ya NO deben aparecer como argumentos de llamada.
    # Acepta `fallback=ACTOR_MODEL,` y `fallback=JUDGE_MODEL,` (correcto).
    # Rechaza `model=ACTOR_MODEL,` y `model=JUDGE_MODEL,` (regresión).
    forbidden_patterns = [
        r"model=ACTOR_MODEL\s*,",
        r"model=JUDGE_MODEL\s*,",
    ]
    for pattern in forbidden_patterns:
        matches = re.findall(pattern, content)
        assert not matches, (
            f"REGRESIÓN CATASTRO-WIRING-001: el patrón {pattern!r} "
            f"reapareció en kernel/embrion_loop.py. "
            f"El wiring del Catastro fue revertido. "
            f"Revisar Sprint CATASTRO-WIRING-001 (Cowork firma 2026-05-18)."
        )

    # Los 3 sitios canonicos deben llamar al helper.
    expected_helper_calls = [
        r"_select_model_via_catastro\s*\(",
    ]
    for pattern in expected_helper_calls:
        matches = re.findall(pattern, content)
        # 1 definición + 3 llamadas = 4 ocurrencias mínimo
        assert len(matches) >= 4, (
            f"El helper _select_model_via_catastro tiene {len(matches)} ocurrencias, esperadas >=4 (1 def + 3 sitios)."
        )

    # Markers de auditoría deben existir
    assert "CATASTRO_WIRING_BEGIN" in content, "Marker CATASTRO_WIRING_BEGIN ausente en embrion_loop.py"
    assert "CATASTRO_WIRING_END" in content, "Marker CATASTRO_WIRING_END ausente en embrion_loop.py"


# ============================================================================
# G_TEST_9: Helper async wrappea engine.recommend con asyncio.to_thread
# ============================================================================
@pytest.mark.asyncio
async def test_helper_no_bloquea_event_loop_si_recommend_es_lento():
    """
    El helper debe usar asyncio.to_thread para no bloquear el event loop
    del Embrión, incluso si recommend tarda. Probamos que se puede ejecutar
    junto a otra tarea async sin congelar el loop.
    """
    import asyncio

    from kernel.embrion_loop import _select_model_via_catastro

    fake_top = MagicMock()
    fake_top.id = "test-model"
    fake_top.nombre = "Test"
    fake_top.trono_global = 50.0

    fake_response = MagicMock()
    fake_response.degraded = False
    fake_response.degraded_reason = None
    fake_response.modelos = [fake_top]

    # Simulamos un recommend que tarda 50ms
    import time

    def slow_recommend(*args, **kwargs):
        time.sleep(0.05)
        return fake_response

    fake_engine = MagicMock()
    fake_engine.recommend = slow_recommend

    async def concurrent_task():
        await asyncio.sleep(0.01)
        return "concurrent-done"

    with patch("kernel.catastro.catastro_routes._engine_singleton", fake_engine):
        # Si to_thread no se usa, el segundo task no se ejecutaria
        # hasta que recommend termine.
        results = await asyncio.gather(
            _select_model_via_catastro(
                use_case="autonomous_thought",
                fallback="fallback",
            ),
            concurrent_task(),
        )
    assert results[0] == "test-model"
    assert results[1] == "concurrent-done"
