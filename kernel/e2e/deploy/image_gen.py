"""
Sprint 88.3 Fix 4/4 — Hero image generation per vertical.

Para v1.0 PRODUCTO COMERCIALIZABLE: usamos imagenes curadas de Unsplash
seleccionadas por vertical detectado. Esto garantiza que cada landing
tenga una imagen profesional sin depender de una API externa que pueda
fallar y bloquear el deploy.

Roadmap futuro: integrar Imagen 4 Fast (gemini-2.5-flash-image) cuando
GEMINI_API_KEY tenga permisos de generacion de imagenes y se valide
el round-trip (S3 upload).
"""
from __future__ import annotations

from typing import Optional


_HERO_IMAGES = {
    "ecommerce": "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=1200&q=80&auto=format&fit=crop",
    "saas": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80&auto=format&fit=crop",
    "servicios": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1200&q=80&auto=format&fit=crop",
    "local": "https://images.unsplash.com/photo-1556740749-887f6717d7e4?w=1200&q=80&auto=format&fit=crop",
    "generico": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=80&auto=format&fit=crop",
}


def generate_hero_image(
    vertical: str, frase_input: str, run_id: str
) -> Optional[str]:
    """
    Devuelve una URL de hero image apropiada al vertical.

    Args:
        vertical: 'ecommerce' | 'saas' | 'servicios' | 'local' | 'generico'
        frase_input: brief original del usuario (no usado en version curada)
        run_id: identificador del run (para tracking, no usado aun)

    Returns:
        URL HTTPS de una imagen de Unsplash; fallback a 'generico' si vertical desconocido.
    """
    return _HERO_IMAGES.get(vertical, _HERO_IMAGES["generico"])
