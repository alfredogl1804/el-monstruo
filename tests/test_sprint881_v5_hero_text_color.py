"""
Sprint 88.1 v5 — fix CRITICO: hero h1 estaba en var(--secondary) pálido.

Bug raíz QUINTA iteración (post fixes v3 contraste body, v4 wait_until=load):
- v3 cambió `--text` (body) a graphite #1C1917 — OK pero solo aplica a `body`.
- v4 fix Playwright capturando antes de CSS aplicar — OK.
- PERO: el `.hero h1` (el TEXTO MÁS PROMINENTE de la landing) tenía
  `color: var(--secondary)` que el creativo asigna a colores PÁLIDOS DE MARCA
  (ej #D9C8B2 beige claro, #C8B8A0 crema, #E8DAC4 nude). Sobre fondo
  `--bg: #fafaf9` (off-white) el contraste WCAG es ~1.5:1 — FALLA AA.

Resultado en producción: Gemini Vision veía el hero "casi invisible" y reportaba
"página vacía, wireframe sin texto". Verificado visualmente con browser:
heading enorme apenas legible en beige sobre crema.

Mismo bug en .section-title, .benefits h2, .features h2, .insights h2,
.contact h2, .brand-mark, .btn-ghost — todos textos prominentes en color
de marca pálido.

Fix v5: 8 cambios `color: var(--secondary)` → `color: var(--text)` en TEXTOS.
`--secondary` queda solo para backgrounds/accents/eyebrow (donde se usa con
opacity o como marca decorativa).

Tests verifican que el CSS template no use --secondary para texto prominente.
"""
from __future__ import annotations

from kernel.e2e.deploy.real_deploy import render_landing_html


class TestHeroTextColor:
    """Verifica que h1/h2 prominentes usen --text (graphite), no --secondary (pálido)."""

    STATE_BASE = {
        "frase_input": "Test landing premium",
        "creativo": {"output_payload": {
            "colores_primarios": ["#7B5B3A", "#D9C8B2", "#F2E1D2"],
            "tono": "calido",
            "voice_attributes": ["premium", "artesanal"],
            "elevator_pitch": "test pitch",
        }},
        "ventas": {"output_payload": {
            "propuesta_valor": {
                "statement": "Statement test premium",
                "diferenciador": "Diferenciador test",
                "beneficios": ["B1", "B2", "B3"],
            },
            "icp_refinado": {"perfil": "test"},
            "pricing_tentativo": {"modelo": "test"},
            "canales_adquisicion": [{"nombre": "Instagram", "razon": "test"}],
            "primer_funnel": {},
            "metricas_clave": ["m1"],
        }},
        "architect": {"brief": {"nombre_proyecto": "TestProj"}},
    }

    def _render(self):
        out = render_landing_html(
            state=self.STATE_BASE,
            run_id="test_v5",
            ingest_url="https://example.com/ingest",
        )
        css = out.get("style.css", "")
        html = out.get("index.html", "")
        return html, css

    def test_hero_h1_usa_text_no_secondary(self):
        _, css = self._render()
        # Busca .hero h1 { ... color: var(--text); ... }
        import re
        m = re.search(r"\.hero h1\s*\{[^}]*\}", css)
        assert m, "No se encontró bloque .hero h1"
        block = m.group(0)
        assert "color: var(--text)" in block, (
            f".hero h1 DEBE usar color: var(--text). Encontrado: {block}"
        )
        assert "color: var(--secondary)" not in block, (
            f".hero h1 NO debe usar var(--secondary) (pálido). Encontrado: {block}"
        )

    def test_section_titles_no_usan_secondary(self):
        _, css = self._render()
        # h1/h2/section-title prominentes NO deben tener var(--secondary)
        import re
        for selector in [
            r"\.section-title",
            r"\.benefits h2",
            r"\.features h2",
            r"\.insights h2",
            r"\.contact h2",
            r"\.brand-mark",
        ]:
            m = re.search(selector + r"\s*\{[^}]*\}", css)
            assert m, f"No se encontró bloque {selector}"
            block = m.group(0)
            assert "color: var(--secondary)" not in block, (
                f"{selector} NO debe usar var(--secondary). Encontrado: {block}"
            )

    def test_btn_ghost_usa_text(self):
        _, css = self._render()
        # btn-ghost debe usar --text para legibilidad
        assert ".btn-ghost { background: transparent; color: var(--text);" in css, (
            "btn-ghost debe usar var(--text), no var(--secondary)"
        )

    def test_secondary_aun_usado_para_background_accents(self):
        _, css = self._render()
        # --secondary aún debe declararse como custom prop (paleta del creativo)
        assert "--secondary:" in css, "--secondary debe seguir declarándose"
