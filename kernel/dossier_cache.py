"""
kernel/dossier_cache.py — Sprint 39: Dossier Cache con TTL

El dossier de usuario se cargaba desde Supabase en CADA request de enrich,
añadiendo 50-150ms de latencia de red por request.

Este módulo implementa un cache en memoria con TTL de 5 minutos por user_id.
El dossier cambia raramente (datos del usuario, proyectos, contexto personal),
por lo que 5 minutos de cache es seguro y reduce drásticamente la latencia.

Basado en el patrón de "lazy loading con TTL" recomendado por Redis Blog (abril 2026).
"""

from __future__ import annotations

import time
from typing import Optional

import structlog

logger = structlog.get_logger(__name__)

# ── Configuración ──────────────────────────────────────────────────────────────
_DOSSIER_TTL_SECONDS = 300  # 5 minutos
_DOSSIER_MAX_USERS = 50  # máximo de usuarios en cache simultáneo

# ── Almacenamiento interno ─────────────────────────────────────────────────────
# Estructura: { user_id: {"dossier": str, "ts": float} }
_dossier_cache: dict[str, dict] = {}


def get(user_id: str) -> Optional[str]:
    """
    Retorna el dossier cacheado para el user_id dado.
    Retorna None si no está en cache o expiró.
    """
    entry = _dossier_cache.get(user_id)
    if entry is None:
        return None

    if time.monotonic() - entry["ts"] > _DOSSIER_TTL_SECONDS:
        del _dossier_cache[user_id]
        logger.debug("dossier_cache_expired", user_id=user_id)
        return None

    logger.debug(
        "dossier_cache_hit",
        user_id=user_id,
        age_s=round(time.monotonic() - entry["ts"], 1),
        chars=len(entry["dossier"]),
    )
    return entry["dossier"]


def store(user_id: str, dossier: str) -> None:
    """Almacena el dossier en cache para el user_id dado."""
    if not dossier:
        return

    # Evict si está lleno (LRU simple)
    if len(_dossier_cache) >= _DOSSIER_MAX_USERS:
        oldest = min(_dossier_cache, key=lambda k: _dossier_cache[k]["ts"])
        del _dossier_cache[oldest]
        logger.debug("dossier_cache_lru_evict", evicted_user=oldest)

    _dossier_cache[user_id] = {
        "dossier": dossier,
        "ts": time.monotonic(),
    }
    logger.debug(
        "dossier_cache_store",
        user_id=user_id,
        chars=len(dossier),
        cache_size=len(_dossier_cache),
    )


def invalidate(user_id: Optional[str] = None) -> int:
    """Invalida el cache de un usuario específico o de todos."""
    if user_id is None:
        count = len(_dossier_cache)
        _dossier_cache.clear()
        logger.info("dossier_cache_cleared", count=count)
        return count
    if user_id in _dossier_cache:
        del _dossier_cache[user_id]
        logger.info("dossier_cache_invalidated", user_id=user_id)
        return 1
    return 0


def stats() -> dict:
    """Retorna estadísticas del cache para observabilidad."""
    now = time.monotonic()
    active = {k: v for k, v in _dossier_cache.items() if now - v["ts"] <= _DOSSIER_TTL_SECONDS}
    return {
        "size": len(active),
        "max_users": _DOSSIER_MAX_USERS,
        "ttl_seconds": _DOSSIER_TTL_SECONDS,
        "users": [
            {
                "user_id": k,
                "age_s": round(now - v["ts"], 1),
                "chars": len(v["dossier"]),
            }
            for k, v in active.items()
        ],
    }
