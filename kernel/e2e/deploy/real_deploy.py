"""
Sprint 87.2 Bloque 1 — Deploy real al pipeline E2E.

Diseño:
- Default: GitHub Pages (sites estáticos, gratis, dominio .github.io).
- Fallback: Railway (sites con backend dinámico — futuro).
- Si tools de deploy fallan o GITHUB_TOKEN no está → preview URL determinística
  (`heuristic_preview`) para que el pipeline no bloquee.

Capa Memento aplicada: la operación de deploy es IRREVERSIBLE (publica contenido
del usuario al mundo). Validación previa de PII y placeholder se realiza antes
de invocar el tool real.

Brand DNA en errores: e2e_deploy_*_failed.

LLM-as-parser: NO aplica directamente acá; la generación de HTML/CSS viene de
los outputs de los steps CREATIVO + TECNICO + VENTAS del pipeline.
"""
from __future__ import annotations

import asyncio
import os
import re
import time
import unicodedata
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

import structlog
from pydantic import BaseModel, ConfigDict, Field

logger = structlog.get_logger("kernel.e2e.deploy.real_deploy")


# ── Errores con identidad ────────────────────────────────────────────────────


class E2EDeployError(Exception):
    """Base error class. Brand DNA: e2e_deploy_*_failed."""

    code = "e2e_deploy_failed"


class E2EDeployValidationFailed(E2EDeployError):
    code = "e2e_deploy_validation_failed"


class E2EDeployRenderFailed(E2EDeployError):
    code = "e2e_deploy_render_failed"


class E2EDeployProviderFailed(E2EDeployError):
    code = "e2e_deploy_provider_failed"


# ── Schema ───────────────────────────────────────────────────────────────────


class DeployTarget(str, Enum):
    GITHUB_PAGES = "github_pages"
    RAILWAY = "railway"
    HEURISTIC_PREVIEW = "heuristic_preview"


class RealDeployResult(BaseModel):
    """Resultado del deploy real para persistir en e2e_step_log."""

    model_config = ConfigDict(extra="forbid")

    deploy_url: str = Field(..., description="URL pública navegable")
    deploy_target: DeployTarget = Field(..., description="Provider usado")
    deploy_provider: str = Field(..., description="Identificador legible")
    deploy_at: str = Field(..., description="ISO timestamp UTC")
    repo: Optional[str] = Field(None, description="owner/repo si aplica")
    files_committed: int = Field(0, description="Cantidad de archivos publicados")
    build_confirmed: bool = Field(
        False, description="Si el provider confirmó que el build terminó"
    )
    real_deploy_pending: bool = Field(
        False, description="Si quedan pasos pendientes (sovereign domain, etc.)"
    )
    fallback_reason: Optional[str] = Field(
        None, description="Por qué se usó heuristic_preview, si aplica"
    )


# ── Validación pre-deploy (Capa Memento) ─────────────────────────────────────


_PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN simple
    re.compile(r"\b4\d{3}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b"),  # Visa-like
    re.compile(r"\b5[1-5]\d{2}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b"),  # MasterCard
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),  # API keys
]


def _validate_no_pii(html: str) -> None:
    """Capa Memento: rechaza HTML con PII obvio antes de deploy real."""
    for pat in _PII_PATTERNS:
        if pat.search(html):
            raise E2EDeployValidationFailed(
                f"e2e_deploy_validation_failed: PII pattern detectado "
                f"({pat.pattern[:40]}...) — deploy IRREVERSIBLE bloqueado."
            )


def _slugify(text: str, max_length: int = 40) -> str:
    """Convierte texto a slug ASCII válido para repo name de GitHub.

    GitHub repos requieren [a-zA-Z0-9._-]. Sprint 87.2: forzamos ASCII puro
    porque vimos en producción que acentos (hacé, mérida) bloquean la creación
    del repo y dejan el deploy colgado.
    """
    # 1) Normaliza unicode → ASCII (hacé → hace, mérida → merida)
    text = unicodedata.normalize("NFKD", text or "")
    text = text.encode("ascii", "ignore").decode("ascii")
    # 2) Solo [a-z0-9-]
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    # 3) Colapsa guiones múltiples
    text = re.sub(r"-+", "-", text)
    return text[:max_length] or "monstruo-site"


# ── Renderer mínimo (HTML soberano del Monstruo) ─────────────────────────────


_TRACKING_SCRIPT_TAG = """<script src="/monstruo-tracking.js" defer></script>
<script>
  window.__MONSTRUO_RUN_ID__ = "{run_id}";
  window.__MONSTRUO_INGEST_URL__ = "{ingest_url}";
</script>"""

_BRAND_FOOTER = """<footer style="margin-top:48px;padding:16px;text-align:center;
font-family:system-ui,-apple-system,sans-serif;font-size:12px;color:#a8a29e;
border-top:1px solid #e7e5e4">
  Site soberano del <strong style="color:#f97316">Monstruo</strong>
  · <a href="https://el-monstruo.dev/privacy" style="color:#a8a29e">tracking propio</a>
</footer>"""


def _is_valid_hex(color: str) -> bool:
    """Verifica si un color es HEX valido (#RGB o #RRGGBB)."""
    if not isinstance(color, str):
        return False
    return bool(re.match(r"^#[0-9A-Fa-f]{3}([0-9A-Fa-f]{3})?$", color.strip()))


def _extract_brand_palette(creativo: Dict[str, Any]) -> Dict[str, str]:
    """Extrae paleta del CREATIVO con fallback a Brand DNA del Monstruo (forge/graphite)."""
    raw = creativo.get("colores_primarios") or []
    valid_hex = [c.strip() for c in raw if _is_valid_hex(str(c))]
    primary = valid_hex[0] if valid_hex else "#f97316"
    secondary = valid_hex[1] if len(valid_hex) >= 2 else "#1c1917"
    accent = valid_hex[2] if len(valid_hex) >= 3 else "#a8a29e"
    return {"primary": primary, "secondary": secondary, "accent": accent}


def render_landing_html(
    *,
    state: Dict[str, Any],
    run_id: str,
    ingest_url: str,
) -> Dict[str, str]:
    """
    Construye una landing rica y comercializable a partir del state del pipeline.

    Sprint 88 Tarea 3.A.2: usa los outputs reales de los steps:
    - CREATIVO (StepBrandingOutput): tono, colores_primarios, voice_attributes, elevator_pitch
    - VENTAS (StepCopyOutput): hero_headline, hero_subheadline, body_copy, cta_primary, cta_secondary
    - ARCHITECT: brief.nombre_proyecto, brief.publico_objetivo, brief.problema, brief.solucion
    - INVESTIGAR: research insights

    Retorna dict {filename: content} listo para deploy_to_github_pages.
    """
    creativo = (state.get("creativo") or {}).get("output_payload") or {}
    ventas = (state.get("ventas") or {}).get("output_payload") or {}
    architect = state.get("architect") or {}
    brief = architect.get("brief") or {}
    estrategia = (state.get("estrategia") or {}).get("output_payload") or {}
    research = state.get("research") or {}
    tecnico = (state.get("tecnico") or {}).get("output_payload") or {}
    frase_input = state.get("frase_input") or "Sitio del Monstruo"

    # ---- Mapping CORRECTO de los outputs reales (Sprint 88 fix DSC-G-008) ----
    # CREATIVO outputea: tono, colores_primarios, voice_attributes, elevator_pitch
    # VENTAS outputea: hero_headline, hero_subheadline, body_copy, cta_primary, cta_secondary
    # Detecta nombre_proyecto inválido ("TBD", vacío, "El Monstruo" genérico)
    _raw_nombre = (
        brief.get("nombre_proyecto")
        or creativo.get("nombre")  # legacy field
        or ""
    ).strip()
    _NOMBRES_INVALIDOS = {"", "TBD", "tbd", "TODO", "PLACEHOLDER", "El Monstruo", "el monstruo"}
    if _raw_nombre in _NOMBRES_INVALIDOS:
        # Deriva nombre legible desde el primer sustantivo de la frase_input.
        # Heurística simple: toma 2-3 palabras significativas (no stopwords) de la frase.
        _stop = {"hace", "haz", "una", "un", "para", "de", "la", "el", "en", "con", "y", "o", "mi", "que", "al", "por", "del", "los", "las", "vender", "necesito", "quiero", "diseña", "landing", "premium", "online", "servicio"}
        _palabras = [w for w in (frase_input or "").split() if w.lower() not in _stop and len(w) > 2]
        if _palabras:
            nombre = " ".join(_palabras[:2]).strip(".,;:")[:40] or "Tu Negocio"
        else:
            nombre = "Tu Negocio"
    else:
        nombre = _raw_nombre
    elevator_pitch = creativo.get("elevator_pitch") or ""
    tono = creativo.get("tono") or "directo y confiable"
    voice_attrs = creativo.get("voice_attributes") or []

    # ---- Adapter Sprint 88.1: EmbrionVentas → campos del render ----
    # EmbrionVentasReport entrega: propuesta_valor.{statement,beneficios,diferenciador},
    # canales_adquisicion[], pricing_tentativo, icp_refinado.
    # StepCopyOutput (legacy LLM) entrega: hero_headline/cta_primary/cta_secondary.
    # Soportamos ambos shapes: si VENTAS trae los campos del render, los usamos;
    # si trae el shape de EmbrionVentas, los derivamos contextualmente.
    propuesta_valor = ventas.get("propuesta_valor") or {}
    pv_statement = (propuesta_valor.get("statement") or "").strip()
    pv_beneficios = propuesta_valor.get("beneficios") or []
    pv_diferenciador = (propuesta_valor.get("diferenciador") or "").strip()
    canales = ventas.get("canales_adquisicion") or []
    primer_canal = canales[0].get("canal") if canales and isinstance(canales[0], dict) else ""

    hero_headline = (
        ventas.get("hero_headline")
        or pv_statement
        or elevator_pitch
        or nombre
    )
    hero_subheadline = (
        ventas.get("hero_subheadline")
        or pv_diferenciador
        or elevator_pitch
        or frase_input
    )
    if ventas.get("body_copy"):
        body_copy = ventas["body_copy"]
    elif pv_beneficios:
        # Construye body_copy a partir de beneficios + diferenciador (>50 palabras objetivo)
        body_copy = (
            f"{pv_statement} " if pv_statement else ""
        ) + " ".join(str(b) for b in pv_beneficios[:4]) + (
            f" {pv_diferenciador}" if pv_diferenciador else ""
        )
    else:
        body_copy = elevator_pitch or frase_input

    # CTAs contextuales — derivados del proyecto, no genéricos.
    # Usa nombre del proyecto + canal preferido + diferenciador para personalizar.
    cta_primary = ventas.get("cta_primary")
    if not cta_primary:
        if nombre and len(nombre) <= 25 and nombre not in ("Tu Negocio",):
            cta_primary = f"Comprar {nombre}"
        else:
            cta_primary = "Comprar ahora"
    cta_secondary = ventas.get("cta_secondary")
    if not cta_secondary:
        if primer_canal:
            cta_secondary = f"Ver en {primer_canal}"[:60]
        elif pv_beneficios:
            cta_secondary = "Ver catálogo"
        else:
            cta_secondary = "Conocer más"

    publico = brief.get("publico_objetivo") or brief.get("publico") or ""
    problema = brief.get("problema") or ""
    solucion = brief.get("solucion") or ""

    # Fases de go-to-market y KPIs (de ESTRATEGIA) como prueba de plan
    fases = estrategia.get("fases") or []
    kpis = estrategia.get("kpis") or []

    # Tech stack (TECNICO) para credibilidad
    stack = tecnico.get("stack_propuesto") or tecnico.get("stack") or []

    # Investigación (3 hallazgos clave) para social proof
    insights = []
    research_summary = research.get("summary") or research.get("sintesis") or ""
    if isinstance(research.get("top_findings"), list):
        insights = research["top_findings"][:3]
    elif isinstance(research.get("findings"), list):
        insights = research["findings"][:3]

    # Paleta dinámica del CREATIVO (con fallback a Brand DNA)
    palette = _extract_brand_palette(creativo)

    # Sanitización mínima HTML
    def _esc(s: str) -> str:
        return (
            str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    # ---- Bloques opcionales ----
    # Beneficios derivados de voice_attributes + brief
    beneficios_raw = []
    if isinstance(brief.get("beneficios"), list):
        beneficios_raw = brief["beneficios"]
    elif solucion:
        # Derivar 3 beneficios desde solucion + voice_attrs
        beneficios_raw = [
            solucion[:120] if solucion else "Resultado garantizado",
            "Hecho con " + (voice_attrs[0] if voice_attrs else "calidad premium"),
            "Atención con tono " + tono,
        ]
    beneficios_html = ""
    if beneficios_raw:
        items = "".join(
            f'<li class="benefit"><span class="benefit-marker"></span><span>{_esc(b)}</span></li>'
            for b in beneficios_raw[:6]
            if isinstance(b, str) and b.strip()
        )
        if items:
            beneficios_html = f"""
  <section class="benefits" aria-labelledby="benefits-title">
    <h2 id="benefits-title">Por qué elegirnos</h2>
    <ul class="benefits-list">{items}</ul>
  </section>"""

    # Features grid (de fases + stack)
    features_html = ""
    feature_items = []
    for f in (fases or [])[:3]:
        if isinstance(f, str) and f.strip():
            feature_items.append(("Fase", f))
    for k in (kpis or [])[:2]:
        if isinstance(k, str) and k.strip():
            feature_items.append(("KPI", k))
    if feature_items:
        cards = "".join(
            f'<article class="feature-card"><div class="feature-tag">{_esc(label)}</div>'
            f'<p class="feature-text">{_esc(text)}</p></article>'
            for label, text in feature_items
        )
        features_html = f"""
  <section class="features" aria-labelledby="features-title">
    <h2 id="features-title">Nuestro plan</h2>
    <div class="features-grid">{cards}</div>
  </section>"""

    # Insights de investigación (social proof)
    insights_html = ""
    insight_items = [i for i in insights if isinstance(i, str) and i.strip()]
    if insight_items:
        items = "".join(
            f'<blockquote class="insight">{_esc(ins)}</blockquote>'
            for ins in insight_items[:3]
        )
        insights_html = f"""
  <section class="insights" aria-labelledby="insights-title">
    <h2 id="insights-title">Lo que descubrimos</h2>
    <div class="insights-list">{items}</div>
  </section>"""
    elif research_summary:
        insights_html = f"""
  <section class="insights" aria-labelledby="insights-title">
    <h2 id="insights-title">Contexto de mercado</h2>
    <p class="insights-summary">{_esc(str(research_summary)[:600])}</p>
  </section>"""

    # Público objetivo (cuando existe)
    publico_html = ""
    if publico:
        publico_html = (
            f'<p class="hero-eyebrow">Pensado para {_esc(publico)}</p>'
        )

    # Stack tecnológico (footer credencial)
    stack_str = ""
    if isinstance(stack, list) and stack:
        items = [s for s in stack if isinstance(s, str) and s.strip()]
        if items:
            stack_str = " · ".join(items[:5])

    tracking = _TRACKING_SCRIPT_TAG.format(run_id=run_id, ingest_url=ingest_url)

    # ---- HTML enriquecido (Sprint 88: target Critic Score >=80) ----
    index_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(nombre)} — {_esc(hero_headline[:60])}</title>
<meta name="description" content="{_esc(hero_subheadline[:160])}">
<meta name="generator" content="El Monstruo Pipeline E2E v1.0">
<meta property="og:title" content="{_esc(nombre)}">
<meta property="og:description" content="{_esc(hero_subheadline[:160])}">
<meta property="og:type" content="website">
<style>
/* Sprint 88.2: CSS inline para garantizar render en Playwright/Chromium
   sin dependencia de fetch de hoja externa (CDN/CSP/network races) */
__INLINE_STYLE_CSS__
</style>
</head>
<body>
<header class="site-header" role="banner">
  <div class="site-header-inner">
    <span class="brand-mark">{_esc(nombre)}</span>
    <nav aria-label="Principal">
      <a href="#beneficios">Beneficios</a>
      <a href="#plan">Plan</a>
      <a href="#contacto" class="nav-cta">{_esc(cta_secondary)}</a>
    </nav>
  </div>
</header>
<main>
  <section class="hero" aria-labelledby="hero-title">
    {publico_html}
    <h1 id="hero-title">{_esc(hero_headline)}</h1>
    <p class="hero-sub">{_esc(hero_subheadline)}</p>
    <div class="hero-ctas">
      <a class="btn btn-primary" href="#contacto">{_esc(cta_primary)}</a>
      <a class="btn btn-ghost" href="#beneficios">{_esc(cta_secondary)}</a>
    </div>
  </section>
  <section class="copy" aria-labelledby="copy-title">
    <h2 id="copy-title" class="section-title">Lo que ofrecemos</h2>
    <p class="body-copy">{_esc(body_copy)}</p>
  </section>
  <section id="beneficios" class="benefits-anchor" aria-hidden="true"></section>{beneficios_html}
  <section id="plan" class="plan-anchor" aria-hidden="true"></section>{features_html}{insights_html}
  <section id="contacto" class="contact" aria-labelledby="contact-title">
    <h2 id="contact-title">Hablemos</h2>
    <p class="contact-copy">{_esc(elevator_pitch or hero_subheadline)}</p>
    <a class="btn btn-primary btn-large" href="mailto:hola@el-monstruo.dev?subject={_esc(nombre)}">{_esc(cta_primary)}</a>
  </section>
</main>
<footer class="site-footer" role="contentinfo">
  <p>{_esc(nombre)} · Forjado por <a href="https://github.com/alfredogl1804/el-monstruo">El Monstruo</a></p>
  {f'<p class="footer-stack">{_esc(stack_str)}</p>' if stack_str else ''}
  <p class="run-id">Run {_esc(run_id)}</p>
</footer>
{_BRAND_FOOTER}
{tracking}
</body>
</html>
"""

    # ---- CSS enriquecido con paleta dinámica ----
    primary = palette["primary"]
    secondary = palette["secondary"]
    accent = palette["accent"]

    # Sprint 88.1 fix: --text DEBE ser graphite legible (#1C1917) del Brand DNA,
    # no `secondary` que puede ser un color claro de la paleta (beige/crema)
    # produciendo texto invisible sobre fondo blanco. La paleta de marca se
    # usa solo para acentos: primary (botones), secondary (badges), accent (links).
    style_css = f""":root {{
  --primary: {primary};
  --secondary: {secondary};
  --accent: {accent};
  --bg: #fafaf9;
  --bg-card: #ffffff;
  --text: #1C1917;
  --text-muted: #57534e;
  --border: #e7e5e4;
  --primary-hover: color-mix(in srgb, {primary} 88%, black);
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
  --radius: 8px;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}}
main {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

/* Header */
.site-header {{
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  padding: 16px 24px;
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(8px);
}}
.site-header-inner {{
  max-width: 1080px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}}
.brand-mark {{
  font-weight: 800;
  font-size: 18px;
  color: var(--text);
  letter-spacing: -0.01em;
}}
.site-header nav {{ display: flex; gap: 24px; align-items: center; }}
.site-header nav a {{
  color: var(--text-muted);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}}
.site-header nav a:hover {{ color: var(--primary); }}
.site-header nav a.nav-cta {{
  background: var(--primary);
  color: white;
  padding: 8px 16px;
  border-radius: var(--radius);
}}
.site-header nav a.nav-cta:hover {{ background: var(--primary-hover); color: white; }}

/* Hero */
.hero {{
  text-align: center;
  padding: 96px 24px 64px;
  max-width: 820px;
  margin: 0 auto;
}}
.hero-eyebrow {{
  display: inline-block;
  background: color-mix(in srgb, var(--primary) 12%, transparent);
  color: var(--primary);
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 24px;
}}
.hero h1 {{
  font-size: clamp(36px, 6vw, 64px);
  font-weight: 800;
  letter-spacing: -0.025em;
  color: var(--text);
  margin-bottom: 24px;
  line-height: 1.1;
}}
.hero-sub {{
  font-size: clamp(18px, 2.5vw, 22px);
  color: var(--text-muted);
  max-width: 640px;
  margin: 0 auto 40px;
  line-height: 1.5;
}}
.hero-ctas {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }}

/* Buttons */
.btn {{
  display: inline-block;
  padding: 14px 28px;
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
  border-radius: var(--radius);
  transition: all 0.2s ease;
  cursor: pointer;
  border: 2px solid transparent;
}}
.btn-primary {{ background: var(--primary); color: white; box-shadow: var(--shadow-sm); }}
.btn-primary:hover {{ background: var(--primary-hover); transform: translateY(-1px); box-shadow: var(--shadow-md); }}
.btn-ghost {{ background: transparent; color: var(--text); border-color: var(--border); }}
.btn-ghost:hover {{ border-color: var(--primary); color: var(--primary); }}
.btn-large {{ padding: 18px 36px; font-size: 17px; }}

/* Section title */
.section-title {{
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 24px;
  text-align: center;
}}

/* Copy */
.copy {{
  max-width: 720px;
  margin: 64px auto;
  padding: 32px;
  background: var(--bg-card);
  border-left: 4px solid var(--primary);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
}}
.body-copy {{ font-size: 18px; color: var(--text-muted); }}

/* Anchors */
.benefits-anchor, .plan-anchor {{ position: relative; top: -80px; visibility: hidden; }}

/* Benefits */
.benefits {{ padding: 64px 24px; max-width: 980px; margin: 0 auto; }}
.benefits h2 {{
  font-size: 32px;
  font-weight: 800;
  color: var(--text);
  text-align: center;
  margin-bottom: 40px;
  letter-spacing: -0.02em;
}}
.benefits-list {{ list-style: none; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
.benefit {{
  display: flex; align-items: flex-start; gap: 14px;
  padding: 24px;
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
}}
.benefit-marker {{
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--primary);
  flex-shrink: 0;
  margin-top: 8px;
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 20%, transparent);
}}
.benefit span:last-child {{ font-size: 16px; color: var(--text); line-height: 1.5; }}

/* Features */
.features {{ padding: 64px 24px; max-width: 1080px; margin: 0 auto; background: linear-gradient(180deg, transparent 0%, color-mix(in srgb, var(--primary) 4%, transparent) 100%); }}
.features h2 {{
  font-size: 32px;
  font-weight: 800;
  color: var(--text);
  text-align: center;
  margin-bottom: 40px;
  letter-spacing: -0.02em;
}}
.features-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }}
.feature-card {{
  background: var(--bg-card);
  padding: 28px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s, box-shadow 0.2s;
}}
.feature-card:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-md); }}
.feature-tag {{
  display: inline-block;
  background: var(--primary);
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 12px;
}}
.feature-text {{ font-size: 15px; color: var(--text); line-height: 1.55; }}

/* Insights */
.insights {{ padding: 64px 24px; max-width: 880px; margin: 0 auto; }}
.insights h2 {{
  font-size: 28px;
  font-weight: 800;
  color: var(--text);
  text-align: center;
  margin-bottom: 32px;
  letter-spacing: -0.02em;
}}
.insights-list {{ display: grid; gap: 16px; }}
.insight {{
  background: var(--bg-card);
  padding: 24px 28px;
  border-left: 3px solid var(--accent);
  border-radius: var(--radius);
  font-size: 16px;
  color: var(--text);
  font-style: italic;
  box-shadow: var(--shadow-sm);
}}
.insights-summary {{ font-size: 16px; color: var(--text-muted); text-align: center; }}

/* Contact */
.contact {{
  text-align: center;
  padding: 96px 24px 64px;
  max-width: 720px;
  margin: 0 auto;
  border-top: 1px solid var(--border);
  margin-top: 64px;
}}
.contact h2 {{
  font-size: 36px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}}
.contact-copy {{ font-size: 18px; color: var(--text-muted); margin-bottom: 32px; max-width: 560px; margin-left: auto; margin-right: auto; }}

/* Footer */
.site-footer {{
  text-align: center;
  padding: 32px 24px;
  border-top: 1px solid var(--border);
  font-size: 14px;
  color: var(--text-muted);
  background: var(--bg);
}}
.site-footer p {{ margin: 6px 0; }}
.site-footer a {{ color: var(--primary); text-decoration: none; }}
.site-footer a:hover {{ text-decoration: underline; }}
.footer-stack {{ font-size: 12px; opacity: 0.7; }}
.run-id {{ font-family: ui-monospace, SFMono-Regular, monospace; font-size: 11px; opacity: 0.5; }}

/* Responsive */
@media (max-width: 640px) {{
  .site-header nav {{ gap: 16px; }}
  .site-header nav a:not(.nav-cta) {{ display: none; }}
  .hero {{ padding: 64px 16px 48px; }}
  .copy {{ padding: 24px 20px; margin: 40px 16px; }}
}}
"""

    # Tracking script soberano (también se sirve estático separado para que el
    # navegador lo cachee independientemente)
    tracking_js = _MONSTRUO_TRACKING_JS

    # Sprint 88.2 fix: inline el CSS dentro del HTML para que Playwright/Chromium
    # renderice los estilos sin depender de fetch externo de style.css
    # (que falla en Railway por CSP/network race con GitHub Pages CDN).
    # Mantenemos style.css como archivo separado por SEO/cache/inspección.
    index_html = index_html.replace("__INLINE_STYLE_CSS__", style_css)

    return {
        "index.html": index_html,
        "style.css": style_css,
        "monstruo-tracking.js": tracking_js,
        ".nojekyll": "",  # Permite que GitHub Pages no intente Jekyll-procesar
    }


# Tracking script (~150 LOC) inline para que se sirva con cada deploy
_MONSTRUO_TRACKING_JS = """// monstruo-tracking.js — Sprint 87.2 Bloque 4
// Privacy-first: cero tracking cross-site, cookie soberana de primera parte.
(function () {
  "use strict";
  var RUN_ID = window.__MONSTRUO_RUN_ID__ || "unknown";
  var INGEST = window.__MONSTRUO_INGEST_URL__ || "/v1/traffic/ingest";
  var COOKIE_NAME = "monstruo_sid";
  var SESSION_TTL_MIN = 30;

  function _uuid() {
    if (window.crypto && window.crypto.randomUUID) {
      try { return window.crypto.randomUUID(); } catch (e) {}
    }
    return "sid_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 10);
  }

  function _getSid() {
    var match = document.cookie.match(/(?:^|;\\s*)monstruo_sid=([^;]+)/);
    if (match) return decodeURIComponent(match[1]);
    var sid = _uuid();
    var expires = new Date(Date.now() + SESSION_TTL_MIN * 60 * 1000).toUTCString();
    document.cookie = COOKIE_NAME + "=" + encodeURIComponent(sid) +
      "; path=/; expires=" + expires + "; SameSite=Lax";
    return sid;
  }

  function _device() {
    var ua = navigator.userAgent || "";
    if (/Mobi|Android|iPhone|iPad/i.test(ua)) return "mobile";
    return "desktop";
  }

  function _ping(eventType, extra) {
    var payload = {
      run_id: RUN_ID,
      session_id: _getSid(),
      event_type: eventType,
      url: window.location.href,
      referrer: document.referrer || "",
      device: _device(),
      ts: new Date().toISOString(),
      extra: extra || {}
    };
    try {
      if (navigator.sendBeacon) {
        var blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
        navigator.sendBeacon(INGEST, blob);
      } else {
        fetch(INGEST, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          keepalive: true
        }).catch(function () { /* swallow */ });
      }
    } catch (e) { /* privacy-first: nunca tirar errores al usuario */ }
  }

  // Pageview al cargar
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { _ping("pageview"); });
  } else {
    _ping("pageview");
  }

  // Tiempo en página al salir
  var loadedAt = Date.now();
  window.addEventListener("beforeunload", function () {
    _ping("unload", { time_on_page_ms: Date.now() - loadedAt });
  });

  // CTA clicks
  document.addEventListener("click", function (e) {
    var t = e.target;
    if (t && t.classList && t.classList.contains("btn")) {
      _ping("cta_click", { text: (t.textContent || "").trim().slice(0, 80) });
    }
  });
})();
"""


# ── Provider invocation ──────────────────────────────────────────────────────


async def _deploy_via_github_pages(
    *, repo_name: str, files: Dict[str, str], description: str
) -> Dict[str, Any]:
    """Invoca tools/deploy_to_github_pages reusando Capa 1 Manos."""
    from tools.deploy_to_github_pages import (
        deploy_to_github_pages,
        GitHubPagesDeployFalla,
        GitHubPagesBuildTimeout,
    )

    try:
        result = await deploy_to_github_pages(
            repo_name=repo_name,
            files=files,
            description=description,
            private=False,
            branch="main",
        )
        return result
    except (GitHubPagesDeployFalla, GitHubPagesBuildTimeout) as e:
        raise E2EDeployProviderFailed(
            f"e2e_deploy_provider_failed: GitHub Pages — {e!s}"
        ) from e


def _heuristic_preview_result(*, run_id: str, reason: str) -> RealDeployResult:
    """Fallback determinístico cuando no hay GITHUB_TOKEN o el provider falla.

    NO es un mock — es un preview URL con disclaimer explícito en el pipeline.
    """
    return RealDeployResult(
        deploy_url=f"https://preview.el-monstruo.dev/{run_id}",
        deploy_target=DeployTarget.HEURISTIC_PREVIEW,
        deploy_provider="heuristic_preview",
        deploy_at=datetime.now(timezone.utc).isoformat(),
        repo=None,
        files_committed=0,
        build_confirmed=False,
        real_deploy_pending=True,
        fallback_reason=reason,
    )


# ── API pública ──────────────────────────────────────────────────────────────


async def run_real_deploy(
    *,
    state: Dict[str, Any],
    run_id: str,
    ingest_url: Optional[str] = None,
    target: DeployTarget = DeployTarget.GITHUB_PAGES,
) -> RealDeployResult:
    """
    Ejecuta deploy real del state del pipeline.

    Si target=GITHUB_PAGES y GITHUB_TOKEN está disponible → publica.
    Si no, devuelve heuristic_preview con razón explícita.
    """
    started = time.perf_counter()

    # 1. Render HTML
    try:
        ingest = (
            ingest_url
            or os.environ.get("MONSTRUO_TRAFFIC_INGEST_URL")
            or "https://el-monstruo-kernel-production.up.railway.app/v1/traffic/ingest"
        )
        files = render_landing_html(state=state, run_id=run_id, ingest_url=ingest)
    except Exception as e:
        raise E2EDeployRenderFailed(
            f"e2e_deploy_render_failed: render_landing_html — {e!s}"
        ) from e

    # 2. Validación PII pre-deploy (Capa Memento)
    _validate_no_pii(files["index.html"])

    # 3. Si no hay GITHUB_TOKEN o target es preview → fallback determinístico
    has_gh_token = bool(os.environ.get("GITHUB_TOKEN", "").strip())
    if target == DeployTarget.HEURISTIC_PREVIEW or not has_gh_token:
        result = _heuristic_preview_result(
            run_id=run_id,
            reason="no_github_token" if not has_gh_token else "explicit_preview_target",
        )
        logger.info(
            "e2e_deploy_heuristic_preview",
            run_id=run_id,
            reason=result.fallback_reason,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
        return result

    # 4. Deploy real a GitHub Pages
    # Sprint 88: usar brief.nombre_proyecto (fuente real) en lugar de creativo.nombre (legacy)
    architect = state.get("architect") or {}
    brief = architect.get("brief") or {}
    creativo = (state.get("creativo") or {}).get("output_payload") or {}
    nombre = (
        brief.get("nombre_proyecto")
        or creativo.get("nombre")  # legacy fallback
        or state.get("frase_input")
        or run_id
    )
    repo_name = f"monstruo-{_slugify(nombre, 30)}-{run_id[-8:]}"
    description = f"El Monstruo Pipeline E2E · Run {run_id}"

    # Timeout total para no colgar el pipeline (build de Pages puede tomar 90s+)
    deploy_timeout_s = int(os.environ.get("E2E_DEPLOY_TIMEOUT_S", "45"))

    try:
        provider_result = await asyncio.wait_for(
            _deploy_via_github_pages(
                repo_name=repo_name, files=files, description=description
            ),
            timeout=deploy_timeout_s,
        )
        result = RealDeployResult(
            deploy_url=provider_result["url"],
            deploy_target=DeployTarget.GITHUB_PAGES,
            deploy_provider="github_pages",
            deploy_at=datetime.now(timezone.utc).isoformat(),
            repo=provider_result.get("repo"),
            files_committed=provider_result.get("files_committed", 0),
            build_confirmed=bool(provider_result.get("build_confirmed", False)),
            real_deploy_pending=not bool(provider_result.get("build_confirmed", False)),
            fallback_reason=None,
        )
        logger.info(
            "e2e_deploy_completed",
            run_id=run_id,
            deploy_url=result.deploy_url,
            target=result.deploy_target.value,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
        return result
    except asyncio.TimeoutError:
        # Build de Pages excedió budget — fallback determinístico, no bloquear
        logger.warning(
            "e2e_deploy_timeout_fallback",
            run_id=run_id,
            timeout_s=deploy_timeout_s,
            repo_name=repo_name,
        )
        return _heuristic_preview_result(
            run_id=run_id,
            reason=f"github_pages_timeout_{deploy_timeout_s}s",
        )
    except E2EDeployProviderFailed as e:
        # Fallback explícito — no romper el pipeline si GitHub falla
        logger.warning(
            "e2e_deploy_fallback_to_preview",
            run_id=run_id,
            error=str(e),
        )
        return _heuristic_preview_result(
            run_id=run_id,
            reason=f"provider_failed:{e.code}",
        )
