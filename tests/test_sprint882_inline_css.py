"""
Sprint 88.2 — verificar que index.html lleva CSS inline (no <link> externo).

Bug raíz Sprint 88.1: Playwright en Railway capturaba screenshots de 21KB
(página vacía) mientras que el browser real veía la landing OK (236KB).
Causa probable: Chromium en Railway no descarga style.css externo a tiempo
(CSP / DNS / network race con GitHub Pages CDN).

Fix Sprint 88.2: incluir el CSS inline dentro del <head><style>...</style></head>
del index.html. Eso elimina la dependencia de fetch externo. style.css se sigue
generando como archivo separado por SEO/cache/inspección.
"""
from __future__ import annotations

import re

from kernel.e2e.deploy.real_deploy import render_landing_html


STATE_BASE = {
    "frase_input": "Test Sprint 88.2",
    "creativo": {"output_payload": {
        "colores_primarios": ["#7B5B3A", "#D9C8B2", "#F2E1D2"],
        "tono": "calido",
        "voice_attributes": ["premium"],
        "elevator_pitch": "test pitch",
    }},
    "ventas": {"output_payload": {
        "propuesta_valor": {
            "statement": "Statement test premium",
            "diferenciador": "Diferenciador test",
            "beneficios": ["B1", "B2"],
        },
        "icp_refinado": {"perfil": "test"},
        "pricing_tentativo": {"modelo": "test"},
        "canales_adquisicion": [{"nombre": "Instagram", "razon": "test"}],
        "primer_funnel": {},
        "metricas_clave": ["m1"],
    }},
    "architect": {"brief": {"nombre_proyecto": "TestProj"}},
}


def _render():
    return render_landing_html(
        state=STATE_BASE,
        run_id="test_882",
        ingest_url="https://example.com/ingest",
    )


def test_index_html_tiene_style_block_inline():
    files = _render()
    html = files["index.html"]
    # Debe haber un <style>...</style> en el <head>
    assert "<style>" in html, "index.html DEBE contener bloque <style> inline"
    assert "</style>" in html, "index.html DEBE cerrar el bloque <style>"


def test_index_html_no_contiene_link_stylesheet_local():
    files = _render()
    html = files["index.html"]
    # NO debe haber <link rel="stylesheet" href="style.css"> (CSS interno está inline)
    # Permitido: <link> a Google Fonts u otros CDN externos para fuentes web.
    assert 'href="style.css"' not in html and "href='style.css'" not in html, (
        "index.html NO debe linkear style.css local (debe estar inline en <style>)"
    )
    # Confirmar que SI hay un <style> inline (CSS interno)
    assert "<style>" in html


def test_style_block_contiene_paleta_real():
    files = _render()
    html = files["index.html"]
    # El bloque inline debe contener variables CSS de paleta dinámica
    style_match = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    assert style_match, "Bloque <style>...</style> no encontrado"
    style_content = style_match.group(1)
    assert "--primary:" in style_content, "Falta var --primary en style inline"
    assert "--bg:" in style_content, "Falta var --bg en style inline"
    assert "--text:" in style_content, "Falta var --text en style inline"
    # Y debe contener los colores reales (no placeholders)
    assert "#7B5B3A" in style_content, "Color primario debe estar materializado"


def test_style_css_archivo_sigue_generandose():
    """Por SEO/cache/inspección humana mantenemos style.css separado."""
    files = _render()
    assert "style.css" in files, "style.css debe seguir como archivo separado"
    assert len(files["style.css"]) > 100, "style.css debe tener contenido real"


def test_placeholder_no_quedo_en_html():
    """El placeholder __INLINE_STYLE_CSS__ debe haber sido reemplazado."""
    files = _render()
    html = files["index.html"]
    assert "__INLINE_STYLE_CSS__" not in html, (
        "Placeholder __INLINE_STYLE_CSS__ debe ser reemplazado por el CSS real"
    )
