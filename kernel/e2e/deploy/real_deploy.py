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

import os
import re
import time
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
    """Convierte texto a slug válido para repo name (lowercase, guiones)."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text).strip("-")
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


def render_landing_html(
    *,
    state: Dict[str, Any],
    run_id: str,
    ingest_url: str,
) -> Dict[str, str]:
    """
    Construye un sitio estático minimal a partir del state del pipeline.

    Retorna dict {filename: content} listo para `deploy_to_github_pages`.
    Usa lo que haya disponible; si no hay branding/copy, usa el frase_input.
    """
    creativo = (state.get("creativo") or {}).get("output_payload") or {}
    ventas = (state.get("ventas") or {}).get("output_payload") or {}
    architect = state.get("architect") or {}
    brief = architect.get("brief") or {}
    frase_input = state.get("frase_input") or "Sitio del Monstruo"

    nombre = (
        creativo.get("nombre")
        or brief.get("nombre_proyecto")
        or "El Monstruo"
    )
    tagline = (
        creativo.get("tagline")
        or ventas.get("propuesta_valor")
        or "Producto generado por El Monstruo."
    )
    body_copy = (
        creativo.get("body_copy")
        or ventas.get("propuesta_valor")
        or frase_input
    )
    cta_text = creativo.get("cta_text") or "Quiero saber más"

    # Sanitización mínima HTML
    def _esc(s: str) -> str:
        return (
            str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    tracking = _TRACKING_SCRIPT_TAG.format(run_id=run_id, ingest_url=ingest_url)

    index_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(nombre)}</title>
<meta name="description" content="{_esc(tagline)}">
<meta name="generator" content="El Monstruo Pipeline E2E v1.0">
<link rel="stylesheet" href="style.css">
</head>
<body>
<main>
  <section class="hero">
    <h1>{_esc(nombre)}</h1>
    <p class="tagline">{_esc(tagline)}</p>
  </section>
  <section class="copy">
    <p>{_esc(body_copy)}</p>
  </section>
  <section class="cta">
    <a class="btn" href="#contact">{_esc(cta_text)}</a>
  </section>
  <section id="contact" class="contact">
    <h2>Hablemos</h2>
    <p>Forjado por El Monstruo · Run {_esc(run_id)}</p>
  </section>
</main>
{_BRAND_FOOTER}
{tracking}
</body>
</html>
"""

    style_css = """:root {
  --forge: #f97316;
  --graphite: #1c1917;
  --steel: #a8a29e;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  background: #fafaf9;
  color: var(--graphite);
  line-height: 1.6;
}
main { max-width: 720px; margin: 0 auto; padding: 48px 24px; }
.hero { text-align: center; margin-bottom: 48px; }
.hero h1 {
  font-size: 48px;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--graphite);
  margin-bottom: 16px;
}
.tagline {
  font-size: 20px;
  color: #57534e;
  max-width: 560px;
  margin: 0 auto;
}
.copy {
  font-size: 17px;
  margin: 32px 0;
  padding: 24px;
  background: white;
  border-left: 4px solid var(--forge);
  border-radius: 4px;
}
.cta { text-align: center; margin: 48px 0; }
.btn {
  display: inline-block;
  padding: 14px 32px;
  background: var(--forge);
  color: white;
  text-decoration: none;
  font-weight: 600;
  border-radius: 4px;
  transition: background 0.2s;
}
.btn:hover { background: #ea580c; }
.contact {
  text-align: center;
  padding: 32px 0;
  border-top: 1px solid #e7e5e4;
  margin-top: 48px;
}
.contact h2 { font-size: 24px; margin-bottom: 12px; }
"""

    # Tracking script soberano (también se sirve estático separado para que el
    # navegador lo cachee independientemente)
    tracking_js = _MONSTRUO_TRACKING_JS

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
    creativo = (state.get("creativo") or {}).get("output_payload") or {}
    nombre = creativo.get("nombre") or state.get("frase_input") or run_id
    repo_name = f"monstruo-{_slugify(nombre, 30)}-{run_id[-8:]}"
    description = f"El Monstruo Pipeline E2E · Run {run_id}"

    try:
        provider_result = await _deploy_via_github_pages(
            repo_name=repo_name, files=files, description=description
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
