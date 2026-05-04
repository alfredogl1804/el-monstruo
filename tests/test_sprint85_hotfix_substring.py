"""
Tests de regresión HOTFIX Sprint 85 — substring matching → word boundaries.
============================================================================

Refactoriza `any(kw in text for kw in keywords)` → `pattern.findall(text)`
con `\\b...\\b` en 3 sitios del Sprint 85:

  - kernel/embriones/product_architect.py:_detectar_vertical
  - kernel/task_planner.py:_es_proyecto_web
  - kernel/embriones/critic_visual.py:_evaluar_estructura

Cobertura del spec del Sprint 84.5 / audit Cowork:
  - Caso A: keyword aislada → match (cero regresión funcional)
  - Caso B: keyword embedded en otra palabra → no match (bug fix verificado)
  - Caso C: multi-word keywords siguen funcionando

Run:
    pytest tests/test_sprint85_hotfix_substring.py -v
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Mock structlog si necesario
try:
    import structlog  # noqa
except ImportError:
    sys.modules["structlog"] = type(sys)("structlog")
    sys.modules["structlog"].get_logger = lambda *a, **k: type(
        "L", (), {
            "info": lambda s, *a, **k: None,
            "warning": lambda s, *a, **k: None,
            "error": lambda s, *a, **k: None,
        }
    )()


# ── HOTFIX 1: ProductArchitect._detectar_vertical ────────────────────────────
class TestProductArchitectVertical:
    """Verifica que la heurística de vertical no caiga en falsos positivos."""

    def setup_method(self):
        from kernel.embriones.product_architect import ProductArchitect
        self.pa = ProductArchitect(_sabios=None, _db=None)

    # Caso A — Cero regresión funcional (keyword aislada matchea)
    def test_taller_aislado_matchea_education_arts(self):
        v, c = self.pa._detectar_vertical("Quiero un taller de pintura al óleo")
        assert v == "education_arts"
        assert c > 0

    def test_saas_aislado_matchea_saas_b2b(self):
        v, c = self.pa._detectar_vertical("Necesito un SaaS B2B con dashboard")
        assert v == "saas_b2b"

    def test_restaurante_aislado_matchea_restaurant(self):
        v, c = self.pa._detectar_vertical("Restaurante de comida japonesa con menú")
        assert v == "restaurant"

    # Caso B — Bug fix: substring embebido NO debe matchear
    def test_artesanal_no_matchea_arte_solo(self):
        """'artesanal' contiene 'arte'. Antes: matcheaba education_arts.
        Ahora: solo matchea 'artesanal' (ecommerce_artisanal)."""
        # Texto sin keywords de education_arts excepto el potencial substring
        v, _ = self.pa._detectar_vertical(
            "Tienda de productos artesanales hechos a mano premium"
        )
        # Debería rutear a ecommerce_artisanal, NO a education_arts
        assert v == "ecommerce_artisanal", (
            f"Falso positivo: 'artesanal' matcheó 'arte' → vertical={v}"
        )

    def test_estudiosos_no_matchea_estudio(self):
        """'estudiosos' contiene 'estudio'. Antes: matcheaba.
        Ahora: NO debe matchear porque tiene sufijo 'sos'."""
        # Texto SIN ninguna keyword vlida (los keywords del data set
        # como 'empresas', 'consultor' se evitan a propsito).
        # As el nico potencial match sera substring 'estudio' dentro
        # de 'estudiosos' — que ahora NO matchea.
        v, c = self.pa._detectar_vertical(
            "Texto con clientes estudiosos del mercado"
        )
        # Sin matches reales, fallback a professional_services con confidence 0
        assert c == 0.0, f"'estudiosos' matcheó algo (falso positivo): vertical={v}, conf={c}"
        assert v == "professional_services"  # fallback genérico

    # Caso C — Multi-word keywords siguen funcionando
    def test_hecho_a_mano_multiword_matchea(self):
        v, _ = self.pa._detectar_vertical(
            "Vendo joyería hecho a mano en tienda boutique"
        )
        assert v == "ecommerce_artisanal"

    def test_servicios_profesionales_multiword_matchea(self):
        v, _ = self.pa._detectar_vertical(
            "Despacho de servicios profesionales para PYMES"
        )
        assert v == "professional_services"

    # Caso D — Sin keywords → fallback genérico con confidence 0
    def test_sin_keywords_fallback(self):
        v, c = self.pa._detectar_vertical("Hola mundo XYZ ABC")
        assert v == "professional_services"
        assert c == 0.0


# ── HOTFIX 2: task_planner._es_proyecto_web ─────────────────────────────────
class TestPlannerEsProyectoWeb:
    """Verifica que la heurística del Brief no caiga en falsos positivos."""

    def setup_method(self):
        # Importamos solo el helper sin instanciar el planner completo
        # (que requiere Supabase + LLM)
        from kernel.task_planner import _get_web_project_pattern
        self.pattern = _get_web_project_pattern()

    def _es_web(self, text: str) -> bool:
        if not text:
            return False
        return bool(self.pattern.search(text))

    # Caso A — Zero regresión funcional
    @pytest.mark.parametrize("text", [
        "hazme una landing del taller de Yuna",
        "construye un dashboard SaaS para mi startup",
        "crea un sitio web para mi restaurante",
        "monta una academia online",
        "necesito una página web profesional",
    ])
    def test_proyectos_web_legitimos_matchean(self, text):
        assert self._es_web(text), f"Falso negativo: '{text}'"

    # Caso B — Falsos positivos resueltos
    @pytest.mark.parametrize("text,reason", [
        ("calcula 2+2", "matemática"),
        ("manda un mensaje al usuario", "comunicación"),
        ("redeploy del kernel", "ops"),
        ("la saasoso es buena", "saasoso debería NO matchear saas"),
        ("escuelajo no aplica", "escuelajo no es escuela"),
        ("ese cafetero es bueno", "cafetero contiene café pero no es café"),
    ])
    def test_no_proyectos_web(self, text, reason):
        assert not self._es_web(text), f"Falso positivo ({reason}): '{text}'"

    # Caso C — Multi-word keywords funcionan
    def test_multiword_landing_page_matchea(self):
        assert self._es_web("Quiero una landing page para mi negocio")

    def test_multiword_taller_de_matchea(self):
        assert self._es_web("Hazme un sitio del taller de Yuna")


# ── HOTFIX 3: critic_visual._evaluar_estructura ─────────────────────────────
class TestCriticVisualEstructura:

    def setup_method(self):
        from kernel.embriones.critic_visual import CriticVisual
        self.critic = CriticVisual(_sabios=None, _db=None)

    def test_seccion_pricing_detectada_aislada(self):
        """Caso A: la sección 'pricing' está como heading real."""
        secciones = [{"id": "pricing"}]
        body = "Bienvenido. Conoce nuestros precios. Pricing transparente y claro."
        score, findings = self.critic._evaluar_estructura(secciones, body)
        assert score > 0
        # No debería haber finding de 'pricing' faltante
        assert not any(f.descripcion.lower().find("pricing") != -1 for f in findings)

    def test_seccion_learn_no_matchea_dentro_de_palabra(self):
        """Caso B: 'learn' aislado no debe matchear 'learning' dentro de
        otra palabra cuando lo que buscamos es la sección 'what_youll_learn'.

        En realidad ambas variantes son válidas para una landing de educación,
        pero el test garantiza que el matcher es estricto: si el body solo
        contiene 'learning' como sustantivo embebido, sigue matcheando porque
        'learning' es palabra completa. Lo que NO debe matchear es 'learnable'
        ni 'learnability' a 'learn'."""
        secciones = [{"id": "what_youll_learn"}]
        # body con 'learnability' (no es 'learn' aislado)
        body = "Algo sobre learnability del producto."
        score, findings = self.critic._evaluar_estructura(secciones, body)
        # Debería haber finding de sección no detectada
        assert any("what_youll_learn" in f.descripcion for f in findings), (
            "El refactor debería detectar que 'learnability' NO matchea 'learn'"
        )

    def test_seccion_completa_con_words_separadas(self):
        """Caso C: el matcher acepta cualquiera de las palabras del seccion_id."""
        secciones = [{"id": "what_youll_learn"}]
        body = "Hero principal. Aquí lo que vas a learn en este curso intensivo."
        score, _ = self.critic._evaluar_estructura(secciones, body)
        # 'learn' aislado debe matchear
        assert score > 0
