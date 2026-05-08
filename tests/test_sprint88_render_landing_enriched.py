"""Tests Sprint 88 — Tarea 3.A.2: render_landing_html enriquecido.

Verifica que el render:
1. Usa los outputs REALES de los steps (no campos legacy inventados).
2. Genera HTML con secciones múltiples (hero, copy, benefits, features, insights, contact).
3. Aplica paleta dinámica del CREATIVO (colores_primarios).
4. Incluye meta tags SEO (description, og:title, og:description).
5. Tiene navegación funcional (header con anchor links).
6. Maneja state mínimo con fallbacks Brand DNA del Monstruo.
7. Es responsivo (media queries en CSS).
8. NO tiene placeholder genéricos del template viejo.

DSC-G-008: tests codifican el contrato del HTML enriquecido para que el Critic Score
real (Gemini Vision) pueda subir a >=80 con outputs LLM ricos.
"""
from __future__ import annotations

import re

from kernel.e2e.deploy.real_deploy import (
    _extract_brand_palette,
    _is_valid_hex,
    render_landing_html,
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _full_state_pintura():
    """State realista del pipeline para frase_input pintura al óleo."""
    return {
        "frase_input": "Hacé una landing premium para vender pintura al óleo artesanal hecha en Mérida",
        "architect": {
            "brief": {
                "nombre_proyecto": "Forja Pinturas",
                "publico_objetivo": "coleccionistas, galerías y entusiastas del arte",
                "problema": "escasez de óleo artesanal premium en el sureste mexicano",
                "solucion": "pigmentos puros molidos a mano, lote limitado, certificación de origen",
                "beneficios": [
                    "Calidad museo: pigmentos minerales puros sin solventes industriales",
                    "Edición limitada firmada por el artesano",
                    "Envío express en Mérida, paquete con certificado de origen",
                ],
            }
        },
        "creativo": {
            "output_payload": {
                "tono": "artesanal, premium, mediterráneo cálido",
                "colores_primarios": ["#8B4513", "#F5DEB3", "#1c1917"],
                "voice_attributes": ["confiable", "premium", "auténtico"],
                "elevator_pitch": "Óleo hecho a mano en Mérida con pigmentos puros para artistas y coleccionistas exigentes.",
            }
        },
        "ventas": {
            "output_payload": {
                "hero_headline": "Óleo artesanal de Mérida, listo para tu próxima obra maestra",
                "hero_subheadline": "Pigmentos puros, lote pequeño, hecho a mano. Para artistas que no aceptan compromisos.",
                "body_copy": "Cada tubo nace de horas de paciencia: minerales molidos, aceite virgen, mezclas únicas. No es producto industrial; es herramienta de oficio.",
                "cta_primary": "Pedí tu kit inicial",
                "cta_secondary": "Ver paleta completa",
            }
        },
        "estrategia": {
            "output_payload": {
                "fases": [
                    "Fase 1: lanzamiento con 50 artistas locales seleccionados",
                    "Fase 2: distribución en 3 galerías de la Ciudad de México",
                    "Fase 3: exportación a coleccionistas internacionales",
                ],
                "kpis": [
                    "30 kits vendidos en mes 1",
                    "85% recompra a 90 días",
                ],
            }
        },
        "research": {
            "summary": "El mercado de óleo artesanal en LATAM crece 18% YoY",
            "top_findings": [
                "El 72% de los pintores profesionales prefieren pigmentos sin solventes",
                "Mérida concentra 12 escuelas de arte con 800+ estudiantes activos",
                "Galerías locales reportan demanda creciente de materiales de origen",
            ],
        },
        "tecnico": {
            "output_payload": {
                "stack_propuesto": ["Stripe Checkout", "Shopify", "Mailchimp"],
            }
        },
    }


# ── 1. Mapping correcto de outputs reales ────────────────────────────────


def test_render_uses_brief_nombre_proyecto():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    assert "Forja Pinturas" in files["index.html"]


def test_render_uses_ventas_hero_headline():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    assert "Óleo artesanal de Mérida" in files["index.html"]


def test_render_uses_ventas_cta_primary_y_secondary():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    html = files["index.html"]
    assert "Pedí tu kit inicial" in html  # cta_primary
    assert "Ver paleta completa" in html  # cta_secondary


def test_render_uses_creativo_elevator_pitch():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    assert "pigmentos puros" in files["index.html"]


# ── 2. Secciones enriquecidas presentes ──────────────────────────────────


def test_render_includes_header_with_navigation():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    html = files["index.html"]
    assert "<header" in html
    assert "site-header" in html
    assert 'href="#beneficios"' in html or 'href="#contacto"' in html


def test_render_includes_benefits_section():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    html = files["index.html"]
    assert 'class="benefits"' in html or 'id="beneficios"' in html
    assert "Por qué elegirnos" in html
    assert "Calidad museo" in html  # del primer beneficio


def test_render_includes_features_section_from_estrategia():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    html = files["index.html"]
    # Sprint 88.3 Fix 2/4: title se adapta al vertical detectado.
    # 'pintura al óleo artesanal' → vertical = ecommerce → 'Cómo comprar'.
    assert any(
        title in html
        for title in ["Nuestro plan", "Cómo comprar", "Cómo funciona", "Nuestro proceso"]
    )
    assert "Fase 1" in html  # primera fase de estrategia


def test_render_includes_insights_from_research():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    html = files["index.html"]
    assert "Lo que descubrimos" in html or "Contexto de mercado" in html
    assert "72%" in html or "Mérida concentra" in html  # un finding real


def test_render_includes_footer_with_stack():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    html = files["index.html"]
    assert "<footer" in html
    assert "site-footer" in html
    assert "Stripe Checkout" in html  # del stack técnico


# ── 3. SEO y meta tags ────────────────────────────────────────────────────


def test_render_includes_seo_meta_tags():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    html = files["index.html"]
    assert 'name="description"' in html
    assert 'property="og:title"' in html
    assert 'property="og:description"' in html
    assert 'property="og:type"' in html


def test_render_includes_lang_es():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    assert '<html lang="es">' in files["index.html"]


# ── 4. Paleta dinámica del CREATIVO ──────────────────────────────────────


def test_palette_uses_creativo_colors():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    css = files["style.css"]
    assert "#8B4513" in css  # primer color del CREATIVO
    assert "#F5DEB3" in css  # segundo
    assert "#1c1917" in css  # tercero


def test_palette_falls_back_to_brand_dna_when_creativo_empty():
    state = {
        "frase_input": "test",
        "creativo": {"output_payload": {}},  # sin colores_primarios
    }
    files = render_landing_html(
        state=state, run_id="e2e_88_002", ingest_url="https://api.test/ingest"
    )
    css = files["style.css"]
    # Brand DNA del Monstruo: forge orange + graphite + steel
    assert "#f97316" in css
    assert "#1c1917" in css


def test_palette_rejects_invalid_hex():
    creativo = {
        "colores_primarios": [
            "not-hex",
            "rgb(100,100,100)",
            "#ZZZZZZ",
            "#abc",
            "#aabbcc",
        ]
    }
    palette = _extract_brand_palette(creativo)
    # Solo #abc y #aabbcc son válidos
    assert palette["primary"] == "#abc"
    assert palette["secondary"] == "#aabbcc"
    # Tercero cae a fallback Brand DNA
    assert palette["accent"] == "#a8a29e"


def test_is_valid_hex_function():
    assert _is_valid_hex("#abc") is True
    assert _is_valid_hex("#aabbcc") is True
    assert _is_valid_hex("#AABBCC") is True
    assert _is_valid_hex("not-hex") is False
    assert _is_valid_hex("#ZZZZZZ") is False
    assert _is_valid_hex("rgb(0,0,0)") is False
    assert _is_valid_hex("") is False
    assert _is_valid_hex(None) is False


# ── 5. Responsive design ──────────────────────────────────────────────────


def test_css_includes_media_query():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    css = files["style.css"]
    assert "@media" in css
    assert "max-width" in css


def test_css_uses_clamp_for_fluid_typography():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    assert "clamp(" in files["style.css"]


# ── 6. Fallbacks con state mínimo ────────────────────────────────────────


def test_render_handles_empty_state():
    """Con state casi vacío, debe producir HTML válido sin crashear."""
    state = {"frase_input": "test mínimo"}
    files = render_landing_html(
        state=state, run_id="e2e_88_min", ingest_url="https://api.test/ingest"
    )
    assert "<!DOCTYPE html>" in files["index.html"]
    assert "El Monstruo" in files["index.html"]  # nombre fallback
    assert "test mínimo" in files["index.html"]  # frase_input como body


def test_render_no_legacy_template_strings():
    """Verifica que no quedaron strings del template viejo."""
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    html = files["index.html"]
    # Estos strings eran del template minimal viejo
    assert "Quiero saber más" not in html  # cta_text legacy fallback
    # El nuevo "Hablemos" sí puede aparecer pero ahora con sub-copy real
    if "Hablemos" in html:
        # Si el título sigue siendo "Hablemos", el body debe ser elevator_pitch real, no placeholder
        assert "Forjado por El Monstruo" not in html.split("Hablemos")[1].split("</section>")[0]


# ── 7. Tracking script preservado ────────────────────────────────────────


def test_tracking_script_still_present():
    """Sprint 87.2 traffic soberano debe seguir funcionando."""
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    assert 'src="/monstruo-tracking.js"' in files["index.html"]
    assert 'window.__MONSTRUO_RUN_ID__ = "e2e_88_001"' in files["index.html"]
    assert len(files["monstruo-tracking.js"]) > 1000


# ── 8. HTML válido (smoke check estructural) ─────────────────────────────


def test_html_is_well_formed():
    state = _full_state_pintura()
    files = render_landing_html(
        state=state, run_id="e2e_88_001", ingest_url="https://api.test/ingest"
    )
    html = files["index.html"]
    # Tags esenciales presentes
    assert html.count("<html") == 1
    assert html.count("</html>") == 1
    assert html.count("<body") >= 1
    assert html.count("</body>") >= 1
    assert html.count("<main") >= 1
    assert html.count("</main>") >= 1
    # No quedaron variables sin sustituir
    assert "{nombre}" not in html
    assert "{run_id}" not in html
    assert "${" not in html
