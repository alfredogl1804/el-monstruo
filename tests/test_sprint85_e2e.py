"""
Test E2E Sprint 85 — Tests v2 sobre el pipeline completo
==========================================================
Ejecuta el pipeline real: objective -> Brief -> plan -> deploy -> Critic.

Estos tests requieren credenciales activas y se SKIPPEAN automáticamente
si no están presentes:
  - ANTHROPIC_API_KEY: para Brief generation y planning
  - SUPABASE_URL + SUPABASE_KEY: para persistir briefs y deployments
  - GH_TOKEN: para deploy a GitHub Pages (Bloque 4 ya lo provee)
  - BROWSERLESS_TOKEN o Sprint 84.6 cerrado: para Critic Visual

Run:
    pytest tests/test_sprint85_e2e.py -v -s

Skip si faltan credenciales:
    pytest tests/test_sprint85_e2e.py -v -m "not e2e"

Tests:
  Test 1 v2: Landing curso pintura óleo (Critic Score >= 80 esperado)
  Test 2 v2: Marketplace tutorías matemáticas (data integrity check)
  Test 3:    Auto-replicación con producto real (no placebo)

NOTA: estos tests son los que validan finalmente el cierre del Sprint 85.
Hasta que las credenciales estén verdes (Hilo Credenciales Ola 5+6),
los unit tests + smoke tests por bloque son la garantía estructural.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


# ── Markers + skip helpers ───────────────────────────────────────────────────
def _missing_creds() -> list[str]:
    missing = []
    if not os.environ.get("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")
    if not (os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY")):
        missing.append("SUPABASE_URL+SUPABASE_KEY")
    if not os.environ.get("GH_TOKEN"):
        missing.append("GH_TOKEN")
    return missing


def _missing_browser() -> bool:
    backend = os.environ.get("CRITIC_BROWSER_BACKEND", "soberano")
    if backend == "browserless":
        return not (os.environ.get("BROWSERLESS_URL") and os.environ.get("BROWSERLESS_TOKEN"))
    # soberano: requiere Sprint 84.6 cerrado
    try:
        from kernel.browser_automation import BrowserAutomation
        b = BrowserAutomation()
        # Si la implementación es solo stub, no podemos correr E2E
        return not hasattr(b, "_real_implementation")
    except Exception:
        return True


pytestmark = pytest.mark.e2e


@pytest.mark.skipif(
    _missing_creds() or _missing_browser(),
    reason=f"Credenciales faltantes: {_missing_creds()} o browser no listo",
)
class TestSprint85E2E:
    """Tests v2 que requieren pipeline real corriendo."""

    @pytest.mark.asyncio
    async def test_1_v2_landing_pintura_oleo(self):
        """Test 1 v2: Landing curso pintura óleo. Critic Score >= 80."""
        from kernel.embriones.product_architect import ProductArchitect
        from kernel.embriones.critic_visual import CriticVisual

        prompt = (
            "Crea una landing page para Yuna, instructora de pintura al óleo "
            "que ofrece un taller intensivo de 8 semanas. Público objetivo: "
            "adultos sin experiencia previa que quieren aprender técnica clásica. "
            "Precio: $4,500 MXN. Modalidad presencial en Mérida."
        )

        # 1. Brief
        pa = ProductArchitect(_sabios=None, _db=None)
        brief = await pa.producir_brief(prompt=prompt)
        assert brief.vertical == "education_arts", f"Vertical detectado: {brief.vertical}"
        assert brief.is_complete() or len(brief.data_missing) <= 2

        # 2-3. Plan + Deploy: el Hilo Catastro NO ejecuta el Executor real
        # en este test (requiere kernel completo corriendo). Marcamos como
        # responsabilidad del Hilo Ejecutor + Cowork al cerrar Sprint 85.
        pytest.skip(
            "Test 1 v2 deploy + Critic real: requiere kernel orquestado. "
            "Cowork ejecuta este test desde su entorno cuando Hilo Ejecutor "
            "valide el pipeline."
        )

    @pytest.mark.asyncio
    async def test_2_v2_marketplace_tutorias(self):
        """Test 2 v2: Marketplace tutorías matemáticas con data integrity."""
        from kernel.embriones.product_architect import ProductArchitect

        prompt = (
            "Construye un marketplace de tutorías de matemáticas para preparatoria. "
            "Debe mostrar al menos 3 tutores reales con foto, materias, precio por hora, "
            "rating y bio. Endpoints: /tutores, /tutores/{id}, /reservar, /reservas/{id}, /health."
        )
        pa = ProductArchitect(_sabios=None, _db=None)
        brief = await pa.producir_brief(prompt=prompt)
        assert brief.vertical == "marketplace_services"
        # Resto skip por mismo motivo que Test 1
        pytest.skip("Test 2 v2 deploy: ver nota en test_1_v2.")

    @pytest.mark.asyncio
    async def test_3_auto_replicacion_calculadora_imc(self):
        """Test 3: producto digital simple con contenido real (no placebo)."""
        pytest.skip("Test 3 deploy: ver nota en test_1_v2.")
