"""
kernel/response_cache.py — Sprint 39: Semantic Response Cache

Implementa cache de respuestas con TTL en memoria para reducir latencia
en preguntas repetidas o similares. Basado en las mejores prácticas de
Redis Blog "Streaming LLM Responses" (abril 2026):
  - Cache miss → stream + async store
  - Cache hit → devolver completo (15x más rápido)
  - Semantic matching via hash normalizado (sin dependencias externas)

No requiere Redis en esta versión — usa dict en memoria con TTL.
Para producción a escala se puede migrar a Redis LangCache.
"""

from __future__ import annotations

import hashlib
import re
import time
from typing import Optional

import structlog

logger = structlog.get_logger(__name__)

# ── Configuración ──────────────────────────────────────────────────────────────
_CACHE_TTL_SECONDS = 300  # 5 minutos
_CACHE_MAX_SIZE = 500  # máximo de entradas
_MIN_MESSAGE_LEN = 10  # no cachear mensajes muy cortos
_MAX_MESSAGE_LEN = 300  # no cachear mensajes muy largos (probablemente únicos)
_CACHEABLE_INTENTS = {"chat", "search", "summarize"}  # intents que se benefician del cache

# ── Almacenamiento interno ─────────────────────────────────────────────────────
# Estructura: { cache_key: {"response": str, "ts": float, "hits": int} }
_response_cache: dict[str, dict] = {}


def _normalize(message: str) -> str:
    """Normaliza el mensaje para aumentar hit rate en variaciones triviales."""
    # Lowercase, strip, colapsar espacios, quitar puntuación final
    text = message.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = text.rstrip("?.!,;")
    return text


def _make_key(message: str, intent: str) -> str:
    """Genera la cache key combinando mensaje normalizado + intent."""
    normalized = _normalize(message)
    raw = f"{intent}:{normalized}"
    return hashlib.md5(raw.encode()).hexdigest()


def _is_cacheable(message: str, intent: str) -> bool:
    """Determina si vale la pena cachear este mensaje."""
    if intent not in _CACHEABLE_INTENTS:
        return False
    msg_len = len(message.strip())
    if msg_len < _MIN_MESSAGE_LEN or msg_len > _MAX_MESSAGE_LEN:
        return False
    # No cachear mensajes con datos dinámicos obvios
    dynamic_patterns = [
        r"\d{4}-\d{2}-\d{2}",  # fechas
        r"\$\d+",  # precios
        r"ahora|ahorita|hoy|ayer|mañana",  # referencias temporales
    ]
    msg_lower = message.lower()
    for pattern in dynamic_patterns:
        if re.search(pattern, msg_lower):
            return False
    return True


def _evict_expired() -> None:
    """Elimina entradas expiradas del cache."""
    now = time.monotonic()
    expired = [k for k, v in _response_cache.items() if now - v["ts"] > _CACHE_TTL_SECONDS]
    for k in expired:
        del _response_cache[k]


def _evict_lru() -> None:
    """Elimina la entrada más antigua si el cache está lleno."""
    if len(_response_cache) >= _CACHE_MAX_SIZE:
        oldest = min(_response_cache, key=lambda k: _response_cache[k]["ts"])
        del _response_cache[oldest]
        logger.debug("response_cache_lru_evict", key=oldest)


def get(message: str, intent: str) -> Optional[str]:
    """
    Busca una respuesta cacheada para el mensaje dado.
    Retorna la respuesta si hay hit válido, None si miss o expirado.
    """
    if not _is_cacheable(message, intent):
        return None

    key = _make_key(message, intent)
    entry = _response_cache.get(key)
    if entry is None:
        return None

    # Verificar TTL
    if time.monotonic() - entry["ts"] > _CACHE_TTL_SECONDS:
        del _response_cache[key]
        return None

    # Hit válido
    entry["hits"] += 1
    logger.info(
        "response_cache_hit",
        intent=intent,
        hits=entry["hits"],
        age_s=round(time.monotonic() - entry["ts"], 1),
        preview=message[:50],
    )
    return entry["response"]


def store(message: str, intent: str, response: str) -> bool:
    """
    Almacena una respuesta en el cache.
    Retorna True si se almacenó, False si no era cacheable.
    """
    if not _is_cacheable(message, intent):
        return False
    if not response or len(response) < 3:
        return False

    _evict_expired()
    _evict_lru()

    key = _make_key(message, intent)
    _response_cache[key] = {
        "response": response,
        "ts": time.monotonic(),
        "hits": 0,
        "intent": intent,
        "preview": message[:60],
    }
    logger.info(
        "response_cache_store",
        intent=intent,
        response_len=len(response),
        cache_size=len(_response_cache),
        preview=message[:50],
    )
    return True


def stats() -> dict:
    """Retorna estadísticas del cache para observabilidad."""
    _evict_expired()
    total_hits = sum(v["hits"] for v in _response_cache.values())
    return {
        "size": len(_response_cache),
        "max_size": _CACHE_MAX_SIZE,
        "ttl_seconds": _CACHE_TTL_SECONDS,
        "total_hits": total_hits,
        "entries": [
            {
                "intent": v["intent"],
                "hits": v["hits"],
                "age_s": round(time.monotonic() - v["ts"], 1),
                "preview": v["preview"],
            }
            for v in sorted(_response_cache.values(), key=lambda x: -x["hits"])[:10]
        ],
    }


def invalidate(intent: Optional[str] = None) -> int:
    """Invalida entradas del cache. Si intent es None, limpia todo."""
    if intent is None:
        count = len(_response_cache)
        _response_cache.clear()
        logger.info("response_cache_cleared", count=count)
        return count
    keys = [k for k, v in _response_cache.items() if v["intent"] == intent]
    for k in keys:
        del _response_cache[k]
    logger.info("response_cache_invalidated", intent=intent, count=len(keys))
    return len(keys)
