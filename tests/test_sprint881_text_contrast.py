"""
Sprint 88.1 — fix CRÍTICO contraste --text invisible.

Bug raíz Critic Score 0-5: el CSS asignaba `--text: {secondary}` (color claro
de paleta de marca como #E3CDA6 beige), produciendo texto invisible sobre fondo
#fafaf9 blanco. Gemini Vision veía "página completamente vacía" porque el texto
literalmente NO se renderizaba con suficiente contraste.

Fix: --text fijo en #1C1917 (graphite Brand DNA) garantiza WCAG AA contrast.
La paleta dinámica del CREATIVO se usa solo para --primary/--secondary/--accent.
"""
from __future__ import annotations

import re
import pytest

from kernel.e2e.deploy.real_deploy import render_landing_html


def _state_with_light_palette() -> dict:
    """Caso problemático: paleta con colores claros (beige/crema)."""
    return {
        "frase_input": "Test contraste",
        "architect": {"brief": {"nombre_proyecto": "Test"}},
        "creativo": {
            "output_payload": {
                "tono": "elegante",
                "elevator_pitch": "Algo elegante",
                "voice_attributes": [],
                # Paleta clara peligrosa: beige sobre blanco = invisible
                "colores_primarios": ["#A05B2B", "#E3CDA6", "#7D4B29"],
            },
        },
        "ventas": {
            "output_payload": {
                "propuesta_valor": {
                    "statement": "Test contraste statement",
                    "beneficios": ["beneficio uno"],
                    "diferenciador": "diff",
                },
            },
        },
        "estrategia": {"output_payload": {}},
        "tecnico": {"output_payload": {}},
        "research": {},
    }


class TestTextContrastFix:
    """--text DEBE ser color oscuro fijo, no un color claro de paleta."""

    def test_text_color_es_graphite_no_secondary(self):
        files = render_landing_html(
            state=_state_with_light_palette(),
            run_id="test_881_contrast_a",
            ingest_url="https://example.com/ingest",
        )
        css = files["style.css"]
        # Buscar línea --text:
        match = re.search(r"--text:\s*([^;]+);", css)
        assert match, "CSS debe declarar --text"
        text_color = match.group(1).strip()
        # NO puede ser el secondary de la paleta (crema/beige)
        assert text_color != "#E3CDA6", "--text NO debe usar secondary de paleta"
        # SÍ debe ser graphite Brand DNA (oscuro, contraste alto vs #fafaf9)
        assert text_color.upper() == "#1C1917", f"--text debe ser graphite #1C1917, fue: {text_color}"

    def test_paleta_marca_se_mantiene_para_acentos(self):
        files = render_landing_html(
            state=_state_with_light_palette(),
            run_id="test_881_contrast_b",
            ingest_url="https://example.com/ingest",
        )
        css = files["style.css"]
        # Primary/secondary/accent siguen viniendo de la paleta del creativo
        assert "#A05B2B" in css, "primary debe estar presente"
        assert "#E3CDA6" in css, "secondary debe estar presente (para badges/headers)"
        assert "#7D4B29" in css, "accent debe estar presente"

    def test_bg_sigue_blanco_hueso(self):
        files = render_landing_html(
            state=_state_with_light_palette(),
            run_id="test_881_contrast_c",
            ingest_url="https://example.com/ingest",
        )
        css = files["style.css"]
        assert "--bg: #fafaf9" in css, "bg debe ser blanco hueso"
