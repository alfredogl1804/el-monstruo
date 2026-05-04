"""
El Monstruo — Media Gen Wrapper (Sprint 85, Bloque 5)
========================================================
Generación de hero images vía Replicate Flux 1.1 Pro + fallback Recraft.

Interfaz declarada por el SPEC del Sprint 85 (Cowork):

    async def generate_hero_image(
        *, prompt: str, style: str, width: int = 1920, height: int = 1080
    ) -> dict:
        '''Returns: {"url": "https://...", "cost_usd": float, "duration_ms": int}'''

Provider primario: Replicate Flux 1.1 Pro (~$0.04/imagen)
Fallback: Recraft API (más caro pero más estable, opcional)

IMPORTANTE Sprint 85: la interfaz está LISTA pero las llamadas reales a
Replicate/Recraft están detrás del feature flag MEDIA_GEN_LIVE=true. Por
default, MEDIA_GEN_LIVE=false → devuelve un placeholder estructurado
(URL placeholder + cost_usd=0 + duration_ms simulado). Esto permite que
el resto del Sprint 85 funcione sin requerir que Hilo Credenciales termine
Ola 6 (REPLICATE_API_TOKEN).

Cuando Ola 6 cierre y se setee MEDIA_GEN_LIVE=true + REPLICATE_API_TOKEN,
el wrapper hace llamadas reales sin tocar el código del Executor ni del
Product Architect.

Errores con identidad:
- HERO_IMAGE_SIN_TOKEN: no hay REPLICATE_API_TOKEN
- HERO_IMAGE_GENERACION_FALLO: provider rechazó la generación
- HERO_IMAGE_PROMPT_VACIO: prompt vacío o muy corto

Sprint 85 — 2026-05-04
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import time
from dataclasses import dataclass
from typing import Any, Optional

import structlog

logger = structlog.get_logger("monstruo.tools.hero_image")


# ── Configuración via env (lectura en cada uso) ──────────────────────────────
def _media_gen_live() -> bool:
    return os.environ.get("MEDIA_GEN_LIVE", "false").lower() == "true"


def _provider_default() -> str:
    return os.environ.get("HERO_IMAGE_PROVIDER", "replicate").lower()


# Modelos válidos en mayo 2026 (verificar con anti-autoboicot antes de cada cambio)
REPLICATE_FLUX_MODEL = os.environ.get(
    "REPLICATE_FLUX_MODEL",
    "black-forest-labs/flux-1.1-pro",
)
REPLICATE_FLUX_COST_USD = 0.04  # $0.04/imagen 1024x1024 (mayo 2026)
RECRAFT_COST_USD = 0.08  # $0.08/imagen (más caro, fallback)

PLACEHOLDER_BASE_URL = (
    "https://placehold.co/{width}x{height}/F97316/1C1917"
    "?text=El+Monstruo+%7C+Hero+Pendiente"
)

# ── Estilos curados (alineados con verticals) ────────────────────────────────
ESTILOS_VALIDOS = {
    "warm_artisan",        # education_arts, ecommerce_artisanal
    "bold_corporate",      # saas_b2b
    "appetizing_natural",  # restaurant
    "trustworthy_clean",   # professional_services
    "energetic_youth",     # marketplace_services
    "minimal_premium",     # default genérico premium
}


# ── Errores con identidad de marca ───────────────────────────────────────────
class HeroImageError(Exception):
    """Error base de la generación de hero image."""


HERO_IMAGE_SIN_TOKEN = (
    "HERO_IMAGE_SIN_TOKEN: "
    "REPLICATE_API_TOKEN no está en environment. "
    "Sugerencia: setear MEDIA_GEN_LIVE=false (placeholder) o esperar Ola 6 del Hilo Credenciales."
)

HERO_IMAGE_PROMPT_VACIO = (
    "HERO_IMAGE_PROMPT_VACIO: "
    "El prompt está vacío o tiene menos de 10 caracteres. "
    "Sugerencia: el Product Architect debe generar prompts descriptivos basados en el Brief."
)


@dataclass
class HeroImageResult:
    """Resultado estructurado de generate_hero_image."""

    url: str
    cost_usd: float
    duration_ms: int
    provider: str
    model: Optional[str] = None
    is_placeholder: bool = False
    error: Optional[str] = None
    prompt_hash: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "cost_usd": self.cost_usd,
            "duration_ms": self.duration_ms,
            "provider": self.provider,
            "model": self.model,
            "is_placeholder": self.is_placeholder,
            "error": self.error,
            "prompt_hash": self.prompt_hash,
        }


# ── API pública ──────────────────────────────────────────────────────────────
async def generate_hero_image(
    *,
    prompt: str,
    style: str,
    width: int = 1920,
    height: int = 1080,
) -> dict[str, Any]:
    """
    Genera una hero image siguiendo el contrato del SPEC Sprint 85.

    Args:
        prompt: Descripción de la imagen (10+ chars). El Product Architect
                lo genera basado en el Brief del cliente.
        style: Uno de ESTILOS_VALIDOS. Si no es válido, cae a "minimal_premium".
        width: Ancho en px (default 1920).
        height: Alto en px (default 1080).

    Returns:
        dict con keys: url, cost_usd, duration_ms, provider, model, is_placeholder, error.

    Raises:
        HeroImageError si el prompt está vacío. NO lanza si el provider falla;
        en ese caso retorna un placeholder con error en el dict.
    """
    started = time.time()

    # Validación
    if not prompt or len(prompt.strip()) < 10:
        raise HeroImageError(HERO_IMAGE_PROMPT_VACIO)

    if style not in ESTILOS_VALIDOS:
        logger.warning(
            "hero_image_style_invalido_fallback",
            style_recibido=style,
            fallback="minimal_premium",
        )
        style = "minimal_premium"

    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
    enriched_prompt = _enriquecer_prompt(prompt, style)

    # Modo placeholder (default hasta Ola 6)
    if not _media_gen_live():
        logger.info(
            "hero_image_placeholder_mode",
            reason="MEDIA_GEN_LIVE=false",
            prompt_hash=prompt_hash,
        )
        result = HeroImageResult(
            url=PLACEHOLDER_BASE_URL.format(width=width, height=height),
            cost_usd=0.0,
            duration_ms=int((time.time() - started) * 1000),
            provider="placeholder",
            is_placeholder=True,
            prompt_hash=prompt_hash,
        )
        return result.to_dict()

    # Modo live: Replicate primario
    provider = _provider_default()
    if provider == "replicate":
        result = await _generar_via_replicate(
            prompt=enriched_prompt,
            width=width,
            height=height,
            prompt_hash=prompt_hash,
        )
        if result.url and not result.error:
            result.duration_ms = int((time.time() - started) * 1000)
            return result.to_dict()

        # Fallback a Recraft si Replicate falló
        logger.warning(
            "hero_image_replicate_failed_fallback_recraft",
            error=result.error,
        )

    result = await _generar_via_recraft(
        prompt=enriched_prompt,
        width=width,
        height=height,
        prompt_hash=prompt_hash,
    )
    result.duration_ms = int((time.time() - started) * 1000)

    # Si todo falló, devolver placeholder con error explícito
    if not result.url or result.error:
        return HeroImageResult(
            url=PLACEHOLDER_BASE_URL.format(width=width, height=height),
            cost_usd=0.0,
            duration_ms=int((time.time() - started) * 1000),
            provider="placeholder_after_failure",
            is_placeholder=True,
            error=result.error or "all_providers_failed",
            prompt_hash=prompt_hash,
        ).to_dict()

    return result.to_dict()


# ── Provider: Replicate Flux 1.1 Pro ─────────────────────────────────────────
async def _generar_via_replicate(
    *, prompt: str, width: int, height: int, prompt_hash: str
) -> HeroImageResult:
    token = os.environ.get("REPLICATE_API_TOKEN", "")
    if not token:
        return HeroImageResult(
            url="",
            cost_usd=0.0,
            duration_ms=0,
            provider="replicate",
            error=HERO_IMAGE_SIN_TOKEN,
            prompt_hash=prompt_hash,
        )

    try:
        import httpx
    except ImportError:
        return HeroImageResult(
            url="",
            cost_usd=0.0,
            duration_ms=0,
            provider="replicate",
            error="httpx no instalado",
            prompt_hash=prompt_hash,
        )

    # Replicate API: crear predicción + poll hasta succeeded
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": _aspect_ratio_string(width, height),
            "output_format": "webp",
            "output_quality": 90,
            "safety_tolerance": 2,
            "prompt_upsampling": True,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as cli:
            # Crear predicción
            create_resp = await cli.post(
                f"https://api.replicate.com/v1/models/{REPLICATE_FLUX_MODEL}/predictions",
                headers=headers,
                json=payload,
            )
            if create_resp.status_code not in (200, 201):
                return HeroImageResult(
                    url="",
                    cost_usd=0.0,
                    duration_ms=0,
                    provider="replicate",
                    model=REPLICATE_FLUX_MODEL,
                    error=f"replicate_create_failed: {create_resp.status_code} {create_resp.text[:200]}",
                    prompt_hash=prompt_hash,
                )

            prediction = create_resp.json()
            prediction_id = prediction.get("id")
            poll_url = prediction.get("urls", {}).get("get")

            # Poll hasta succeeded/failed (max 60s)
            for _ in range(30):
                await asyncio.sleep(2.0)
                poll_resp = await cli.get(poll_url, headers=headers)
                state = poll_resp.json()
                status = state.get("status")
                if status == "succeeded":
                    output = state.get("output")
                    img_url = output[0] if isinstance(output, list) else output
                    return HeroImageResult(
                        url=img_url,
                        cost_usd=REPLICATE_FLUX_COST_USD,
                        duration_ms=0,  # se llena fuera
                        provider="replicate",
                        model=REPLICATE_FLUX_MODEL,
                        prompt_hash=prompt_hash,
                    )
                if status in ("failed", "canceled"):
                    return HeroImageResult(
                        url="",
                        cost_usd=0.0,
                        duration_ms=0,
                        provider="replicate",
                        model=REPLICATE_FLUX_MODEL,
                        error=f"replicate_{status}: {state.get('error', 'unknown')}",
                        prompt_hash=prompt_hash,
                    )

            return HeroImageResult(
                url="",
                cost_usd=0.0,
                duration_ms=0,
                provider="replicate",
                model=REPLICATE_FLUX_MODEL,
                error="replicate_timeout_60s",
                prompt_hash=prompt_hash,
            )

    except Exception as exc:
        return HeroImageResult(
            url="",
            cost_usd=0.0,
            duration_ms=0,
            provider="replicate",
            model=REPLICATE_FLUX_MODEL,
            error=f"replicate_exception: {exc}",
            prompt_hash=prompt_hash,
        )


# ── Provider: Recraft (fallback) ─────────────────────────────────────────────
async def _generar_via_recraft(
    *, prompt: str, width: int, height: int, prompt_hash: str
) -> HeroImageResult:
    token = os.environ.get("RECRAFT_API_TOKEN", "")
    if not token:
        return HeroImageResult(
            url="",
            cost_usd=0.0,
            duration_ms=0,
            provider="recraft",
            error="RECRAFT_API_TOKEN no presente",
            prompt_hash=prompt_hash,
        )

    try:
        import httpx
    except ImportError:
        return HeroImageResult(
            url="",
            cost_usd=0.0,
            duration_ms=0,
            provider="recraft",
            error="httpx no instalado",
            prompt_hash=prompt_hash,
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "style": "realistic_image",
        "size": f"{width}x{height}",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as cli:
            resp = await cli.post(
                "https://external.api.recraft.ai/v1/images/generations",
                headers=headers,
                json=payload,
            )
            if resp.status_code != 200:
                return HeroImageResult(
                    url="",
                    cost_usd=0.0,
                    duration_ms=0,
                    provider="recraft",
                    error=f"recraft_failed: {resp.status_code} {resp.text[:200]}",
                    prompt_hash=prompt_hash,
                )
            data = resp.json()
            img_url = data.get("data", [{}])[0].get("url", "")
            if not img_url:
                return HeroImageResult(
                    url="",
                    cost_usd=0.0,
                    duration_ms=0,
                    provider="recraft",
                    error="recraft_empty_response",
                    prompt_hash=prompt_hash,
                )
            return HeroImageResult(
                url=img_url,
                cost_usd=RECRAFT_COST_USD,
                duration_ms=0,
                provider="recraft",
                model="recraft-v3",
                prompt_hash=prompt_hash,
            )

    except Exception as exc:
        return HeroImageResult(
            url="",
            cost_usd=0.0,
            duration_ms=0,
            provider="recraft",
            error=f"recraft_exception: {exc}",
            prompt_hash=prompt_hash,
        )


# ── Helpers ──────────────────────────────────────────────────────────────────
def _enriquecer_prompt(prompt: str, style: str) -> str:
    """Enriquece el prompt con descriptores de estilo curados por vertical."""
    style_descriptors = {
        "warm_artisan": (
            "warm tones, terracotta and ochre palette, soft natural light, "
            "artisanal feel, organic textures, hand-crafted aesthetic"
        ),
        "bold_corporate": (
            "clean professional composition, modern corporate aesthetic, "
            "vibrant gradients, geometric elements, high contrast"
        ),
        "appetizing_natural": (
            "appetizing food photography, natural daylight, vibrant fresh colors, "
            "shallow depth of field, mouth-watering, restaurant quality"
        ),
        "trustworthy_clean": (
            "calm professional setting, neutral palette, clean minimal composition, "
            "trustworthy atmosphere, soft lighting, premium feel"
        ),
        "energetic_youth": (
            "vibrant energetic colors, dynamic composition, modern young adults, "
            "diverse representation, optimistic mood, contemporary lifestyle"
        ),
        "minimal_premium": (
            "minimalist composition, premium aesthetic, refined details, "
            "sophisticated palette, high-end editorial quality"
        ),
    }
    descriptor = style_descriptors.get(style, style_descriptors["minimal_premium"])
    return f"{prompt}. Style: {descriptor}. High resolution, hero banner format."


def _aspect_ratio_string(width: int, height: int) -> str:
    """Calcula aspect ratio string compatible con Flux ('16:9', '4:3', etc.)."""
    ratio = width / height
    if abs(ratio - 16 / 9) < 0.05:
        return "16:9"
    if abs(ratio - 4 / 3) < 0.05:
        return "4:3"
    if abs(ratio - 1.0) < 0.05:
        return "1:1"
    if abs(ratio - 3 / 2) < 0.05:
        return "3:2"
    if abs(ratio - 21 / 9) < 0.05:
        return "21:9"
    return "16:9"  # default


# ── Estado para Command Center ──────────────────────────────────────────────
def estado() -> dict[str, Any]:
    """Estado del wrapper para introspección desde el Command Center."""
    return {
        "module": "tools.generate_hero_image",
        "live_mode": _media_gen_live(),
        "provider_default": _provider_default(),
        "replicate_token_present": bool(os.environ.get("REPLICATE_API_TOKEN")),
        "recraft_token_present": bool(os.environ.get("RECRAFT_API_TOKEN")),
        "replicate_model": REPLICATE_FLUX_MODEL,
        "estilos_validos": sorted(ESTILOS_VALIDOS),
        "costo_replicate_usd": REPLICATE_FLUX_COST_USD,
        "costo_recraft_usd": RECRAFT_COST_USD,
    }
