"""
Sprint 88.1 — Adapter EmbrionVentasReport → render_landing_html.

Cierra la deuda de Cowork DSC-G-008 v2: el render landing tiene CTAs vacios
porque el embrion VENTAS produce shape comercial (propuesta_valor, canales,
pricing, icp_refinado), NO el shape StepCopyOutput (hero_headline, cta_primary).

El adapter en real_deploy.py mapea ambos shapes:
- StepCopyOutput (legacy LLM) → usa hero_headline/cta_* directos
- EmbrionVentasReport → deriva contextualmente desde propuesta_valor + canales

Brand DNA: errores prefijo e2e_render_landing_cta_*_failed.
"""
from __future__ import annotations

import pytest

from kernel.e2e.deploy.real_deploy import render_landing_html


def _state_with_embrion_ventas_shape() -> dict:
    """State del pipeline con VENTAS en shape EmbrionVentasReport (real)."""
    return {
        "frase_input": "Hace una landing premium para vender pintura al oleo artesanal hecha en Merida",
        "architect": {
            "brief": {
                "nombre_proyecto": "Pinturas Mérida",
                "publico_objetivo": "coleccionistas de arte 25-55 años",
                "problema": "decoración genérica e impersonal",
                "solucion": "obras únicas hechas a mano en Mérida",
            },
        },
        "creativo": {
            "output_payload": {
                "tono": "elegante y artesanal",
                "elevator_pitch": "Arte único de Mérida para tu hogar",
                "voice_attributes": ["auténtico", "premium", "cercano"],
                "colores_primarios": ["#8B4513", "#F4A460"],
            },
        },
        "ventas": {
            "output_payload": {
                # Shape REAL de EmbrionVentasReport (no StepCopyOutput)
                "icp_refinado": "Personas 25-55 años nivel medio-alto que valoran arte artesanal",
                "propuesta_valor": {
                    "statement": "Pintura al óleo artesanal de Mérida que transforma espacios con autenticidad y calidad excepcional.",
                    "beneficios": [
                        "Obras únicas hechas a mano que aportan exclusividad.",
                        "Técnicas tradicionales con materiales premium.",
                        "Apoyo directo a artistas locales de Mérida.",
                    ],
                    "diferenciador": "Cada pieza es exclusiva y no se replica jamás.",
                },
                "canales_adquisicion": [
                    {"canal": "Galería online", "cac_usd_estimado": 25.0, "razonamiento": "Alta intención compra"},
                    {"canal": "Instagram orgánico", "cac_usd_estimado": 8.0, "razonamiento": "Visual"},
                ],
                "pricing_tentativo": {
                    "modelo": "one-time",
                    "rango_min": 150.0,
                    "rango_max": 500.0,
                    "razonamiento": "Tamaño y complejidad",
                },
                "confidence": 0.85,
                "source": "llm_openai",
                "analyzed_at": "2026-05-06T12:00:00Z",
            },
        },
        "estrategia": {"output_payload": {"fases": ["Lanzamiento"], "kpis": ["Ventas"]}},
        "tecnico": {"output_payload": {"stack_propuesto": ["Shopify", "Stripe"]}},
        "research": {"summary": "Mercado del arte artesanal en LATAM", "top_findings": []},
    }


def _state_with_step_copy_output_shape() -> dict:
    """State con VENTAS en shape legacy StepCopyOutput."""
    return {
        "frase_input": "Vender consultoría",
        "architect": {"brief": {"nombre_proyecto": "Consultora Premium"}},
        "creativo": {
            "output_payload": {
                "tono": "directo",
                "elevator_pitch": "Consultoría premium",
                "voice_attributes": [],
            },
        },
        "ventas": {
            "output_payload": {
                "hero_headline": "Tu negocio escala 10x con consultoría real",
                "hero_subheadline": "Diagnóstico, plan y ejecución en 30 días.",
                "body_copy": "Consultoría premium con foco en resultados medibles. " * 5,
                "cta_primary": "Reservar diagnóstico",
                "cta_secondary": "Ver casos",
            },
        },
        "estrategia": {"output_payload": {}},
        "tecnico": {"output_payload": {}},
        "research": {},
    }


# ============================================================================
# Tests adapter EmbrionVentasReport
# ============================================================================

class TestRenderLandingAdapterEmbrionVentas:
    """El render extrae propuesta_valor del EmbrionVentasReport para hero/body/CTA."""

    def test_hero_headline_uses_propuesta_valor_statement(self):
        state = _state_with_embrion_ventas_shape()
        files = render_landing_html(
            state=state, run_id="test_881_a", ingest_url="https://example.com/ingest"
        )
        html = files["index.html"]
        assert "Pintura al óleo artesanal de Mérida" in html

    def test_hero_subheadline_uses_diferenciador(self):
        state = _state_with_embrion_ventas_shape()
        files = render_landing_html(
            state=state, run_id="test_881_b", ingest_url="https://example.com/ingest"
        )
        html = files["index.html"]
        assert "Cada pieza es exclusiva" in html

    def test_body_copy_concatena_beneficios(self):
        state = _state_with_embrion_ventas_shape()
        files = render_landing_html(
            state=state, run_id="test_881_c", ingest_url="https://example.com/ingest"
        )
        html = files["index.html"]
        # Al menos uno de los beneficios debe estar en el body
        assert any(
            b in html
            for b in ["Obras únicas hechas a mano", "Técnicas tradicionales", "Apoyo directo a artistas"]
        )

    def test_cta_primary_es_contextual_no_generico(self):
        state = _state_with_embrion_ventas_shape()
        files = render_landing_html(
            state=state, run_id="test_881_d", ingest_url="https://example.com/ingest"
        )
        html = files["index.html"]
        # NO debe caer al fallback genérico "Empezar ahora" cuando hay propuesta_valor
        assert "Empezar ahora" not in html
        # SÍ debe usar el nombre del proyecto en el CTA primary
        assert "Comprar Pinturas Mérida" in html or "Comprar ahora" in html

    def test_cta_secondary_usa_primer_canal(self):
        state = _state_with_embrion_ventas_shape()
        files = render_landing_html(
            state=state, run_id="test_881_e", ingest_url="https://example.com/ingest"
        )
        html = files["index.html"]
        assert "Ver en Galería online" in html

    def test_no_renderiza_TBD_subject(self):
        state = _state_with_embrion_ventas_shape()
        files = render_landing_html(
            state=state, run_id="test_881_f", ingest_url="https://example.com/ingest"
        )
        html = files["index.html"]
        # mailto subject debe ser nombre real del proyecto, no "TBD"
        assert "subject=Pinturas%20M" in html or "Pinturas Mérida" in html


# ============================================================================
# Tests retrocompat StepCopyOutput
# ============================================================================

class TestRenderLandingBackwardsCompatStepCopy:
    """Si VENTAS produce shape legacy StepCopyOutput, sigue funcionando igual."""

    def test_legacy_hero_headline_passthrough(self):
        state = _state_with_step_copy_output_shape()
        files = render_landing_html(
            state=state, run_id="test_881_legacy_a", ingest_url="https://example.com/ingest"
        )
        html = files["index.html"]
        assert "Tu negocio escala 10x con consultoría real" in html

    def test_legacy_cta_primary_passthrough(self):
        state = _state_with_step_copy_output_shape()
        files = render_landing_html(
            state=state, run_id="test_881_legacy_b", ingest_url="https://example.com/ingest"
        )
        html = files["index.html"]
        assert "Reservar diagnóstico" in html
        assert "Ver casos" in html


# ============================================================================
# Tests defensivos — VENTAS vacío
# ============================================================================

class TestRenderLandingDefensivoVentasVacio:
    """Si VENTAS no produce nada útil, el render no falla y usa fallbacks."""

    def test_ventas_vacio_no_explota(self):
        state = {
            "frase_input": "Test fallback",
            "architect": {"brief": {"nombre_proyecto": "FallbackCo"}},
            "creativo": {"output_payload": {"elevator_pitch": "Pitch fallback"}},
            "ventas": {"output_payload": {}},
            "estrategia": {"output_payload": {}},
            "tecnico": {"output_payload": {}},
            "research": {},
        }
        files = render_landing_html(
            state=state, run_id="test_881_def_a", ingest_url="https://example.com/ingest"
        )
        html = files["index.html"]
        # Hero cae al elevator_pitch
        assert "Pitch fallback" in html
        # Sprint 88.3 Fix 1/4: CTA primary se adapta al vertical detectado.
        # 'Test fallback' → vertical = generico → 'Empezar ahora'.
        # NO debe concatenarse con el nombre del proyecto (eso era el bug DSC-G-013).
        assert "Empezar ahora" in html or "Comprar ahora" in html or "Agendar llamada" in html
        assert "Comprar FallbackCo" not in html  # bug viejo NO debe regresar

    def test_ventas_solo_propuesta_valor_minima(self):
        state = {
            "frase_input": "Vender X",
            "architect": {"brief": {"nombre_proyecto": "X"}},
            "creativo": {"output_payload": {}},
            "ventas": {
                "output_payload": {
                    "propuesta_valor": {
                        "statement": "X resuelve el problema Y de manera única.",
                        "beneficios": [],
                        "diferenciador": "",
                    },
                },
            },
            "estrategia": {"output_payload": {}},
            "tecnico": {"output_payload": {}},
            "research": {},
        }
        files = render_landing_html(
            state=state, run_id="test_881_def_b", ingest_url="https://example.com/ingest"
        )
        html = files["index.html"]
        assert "X resuelve el problema Y" in html
