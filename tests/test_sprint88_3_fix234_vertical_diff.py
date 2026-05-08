"""
Tests Sprint 88.3 — Fix 2/4 + 3/4 + 4/4: diferenciación per vertical.

Contrato (DSC-G-014):
- Fix 2/4: Sección "plan" tiene title adaptado al vertical
  (Cómo comprar / Cómo funciona / Nuestro proceso / Nuestro plan).
- Fix 3/4: Layout reorganiza orden de secciones según vertical
  (ecommerce: plan → beneficios; otros: beneficios → plan).
- Fix 4/4: Hero image curada per vertical (URL de Unsplash).
"""
from __future__ import annotations

from kernel.e2e.deploy.real_deploy import render_landing_html
from kernel.e2e.deploy.image_gen import generate_hero_image


def _make_state(frase: str, nombre: str = "TestCo") -> dict:
    return {
        "frase_input": frase,
        "architect": {"brief": {"nombre_proyecto": nombre}},
        "creativo": {
            "output_payload": {
                "elevator_pitch": "Pitch genérico",
                "voice_attributes": ["confiable"],
            }
        },
        "ventas": {"output_payload": {}},
        "estrategia": {"output_payload": {"fases": ["Etapa A", "Etapa B"]}},
        "tecnico": {"output_payload": {}},
        "research": {},
    }


# ──────────────────────────────────────────────────────────────────────────
# Fix 2/4: section title vertical-aware
# ──────────────────────────────────────────────────────────────────────────


def test_ecommerce_section_title_es_como_comprar():
    state = _make_state("Vender ropa premium online")
    files = render_landing_html(
        state=state, run_id="test_fix234_a", ingest_url="https://x.test/i"
    )
    html = files["index.html"]
    assert "Cómo comprar" in html


def test_saas_section_title_es_como_funciona():
    state = _make_state("Software SaaS de gestión de inventario")
    files = render_landing_html(
        state=state, run_id="test_fix234_b", ingest_url="https://x.test/i"
    )
    html = files["index.html"]
    assert "Cómo funciona" in html


def test_servicios_section_title_es_nuestro_proceso():
    state = _make_state("Consultoría de marketing digital")
    files = render_landing_html(
        state=state, run_id="test_fix234_c", ingest_url="https://x.test/i"
    )
    html = files["index.html"]
    assert "Nuestro proceso" in html


# ──────────────────────────────────────────────────────────────────────────
# Fix 3/4: orden de secciones per vertical
# ──────────────────────────────────────────────────────────────────────────


def test_ecommerce_layout_plan_antes_de_beneficios():
    """En e-commerce el flujo de compra (plan) debe ir antes que los beneficios."""
    state = _make_state("Vender pintura al óleo artesanal")
    state["architect"]["brief"]["beneficios"] = ["Calidad premium", "Envío rápido"]
    files = render_landing_html(
        state=state, run_id="test_fix234_d", ingest_url="https://x.test/i"
    )
    html = files["index.html"]
    pos_plan = html.find('id="plan"')
    pos_beneficios = html.find('id="beneficios"')
    assert pos_plan != -1 and pos_beneficios != -1
    assert pos_plan < pos_beneficios, "En ecommerce, 'plan' debe aparecer antes de 'beneficios'"


def test_saas_layout_beneficios_antes_de_plan():
    """En SaaS, los beneficios (valor) deben ir antes que el plan (cómo funciona)."""
    state = _make_state("Software de gestión de tareas")
    state["architect"]["brief"]["beneficios"] = ["Ahorra tiempo", "Más productividad"]
    files = render_landing_html(
        state=state, run_id="test_fix234_e", ingest_url="https://x.test/i"
    )
    html = files["index.html"]
    pos_plan = html.find('id="plan"')
    pos_beneficios = html.find('id="beneficios"')
    assert pos_plan != -1 and pos_beneficios != -1
    assert pos_beneficios < pos_plan, "En SaaS, 'beneficios' debe aparecer antes de 'plan'"


# ──────────────────────────────────────────────────────────────────────────
# Fix 4/4: hero image per vertical
# ──────────────────────────────────────────────────────────────────────────


def test_hero_image_se_inyecta_en_html():
    state = _make_state("Tienda online de zapatos")
    files = render_landing_html(
        state=state, run_id="test_fix234_f", ingest_url="https://x.test/i"
    )
    html = files["index.html"]
    assert 'class="hero-image"' in html
    assert 'images.unsplash.com' in html


def test_generate_hero_image_returns_url_per_vertical():
    """Función debe retornar URL diferente per vertical."""
    url_ec = generate_hero_image("ecommerce", "test", "r1")
    url_saas = generate_hero_image("saas", "test", "r2")
    url_serv = generate_hero_image("servicios", "test", "r3")
    assert url_ec != url_saas
    assert url_saas != url_serv
    assert all(u and u.startswith("https://") for u in [url_ec, url_saas, url_serv])


def test_generate_hero_image_fallback_para_vertical_desconocido():
    url = generate_hero_image("vertical_inventado", "test", "r")
    # Debe caer al fallback "generico"
    assert url == generate_hero_image("generico", "test", "r")
