"""kernel.escape.registry — Override temporal del pulse_interval canonical.

Sprint ESPIRAL-001 T4 — extensión del Escape para permitir que la Espiral
(Pieza #5) aplique correcciones temporales al pulse_interval de un consumer
sin modificar el config canonical firmado T1.

Patrón:
    Hairspring detecta deviation → llama apply_temporal_override(consumer, new_interval, ttl)
    Escape registry guarda override in-memory con expiry timestamp
    get_effective_pulse_interval(consumer) retorna override si vigente, sino canonical
    Tras ttl_seconds, override expira automáticamente sin acción humana

Estado in-memory: por diseño v1 (single-process Embrión). En multi-proceso
futuro, esta info viviría en Redis o un slot de Supabase con TTL nativo.

Thread-safety: asyncio.Lock por consumer evita race conditions.

DSC-MO-006 v1.1 honrado: este módulo es nuevo, no modifica `config.py` firmado T1.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Optional

import structlog

from kernel.escape.config import (
    MAX_PULSE_INTERVAL_SECONDS,
    MIN_PULSE_INTERVAL_SECONDS,
    get_pulse_interval_seconds,
)

logger = structlog.get_logger("escape.registry")


@dataclass
class TemporalOverride:
    """Override temporal del pulse_interval para un consumer."""

    consumer: str
    pulse_interval_seconds: int
    canonical_interval_seconds: int
    applied_at_epoch: float
    ttl_seconds: int

    @property
    def expires_at_epoch(self) -> float:
        return self.applied_at_epoch + self.ttl_seconds

    def is_expired(self, now_epoch: Optional[float] = None) -> bool:
        if now_epoch is None:
            now_epoch = time.time()
        return now_epoch >= self.expires_at_epoch

    def remaining_ttl_seconds(self, now_epoch: Optional[float] = None) -> float:
        if now_epoch is None:
            now_epoch = time.time()
        remaining = self.expires_at_epoch - now_epoch
        return max(0.0, remaining)


# Estado in-memory: dict[consumer] -> TemporalOverride
_OVERRIDES: dict[str, TemporalOverride] = {}

# Lock por consumer (lazy-created en _get_lock)
_LOCKS: dict[str, asyncio.Lock] = {}


def _get_lock(consumer: str) -> asyncio.Lock:
    """Lazy-create asyncio.Lock por consumer (race-safe a primer touch)."""
    lock = _LOCKS.get(consumer)
    if lock is None:
        lock = asyncio.Lock()
        _LOCKS[consumer] = lock
    return lock


async def apply_temporal_override(
    consumer: str,
    new_interval_seconds: int,
    ttl_seconds: int,
) -> TemporalOverride:
    """La Espiral aplica override temporal del pulse_interval canonical.

    Args:
        consumer: nombre canónico del consumer del Escape.
        new_interval_seconds: el nuevo interval a usar (clamp [MIN, MAX]).
        ttl_seconds: cuánto tiempo dura el override antes de expirar.

    Returns:
        TemporalOverride aplicado.

    Raises:
        ValueError: si parámetros inválidos.
    """
    if not consumer or not isinstance(consumer, str):
        raise ValueError("consumer must be non-empty string")
    if new_interval_seconds <= 0:
        raise ValueError(f"new_interval_seconds must be positive, got {new_interval_seconds}")
    if ttl_seconds <= 0:
        raise ValueError(f"ttl_seconds must be positive, got {ttl_seconds}")

    # Clamping defensivo (mismo que config.get_pulse_interval_seconds)
    clamped_interval = max(
        MIN_PULSE_INTERVAL_SECONDS,
        min(MAX_PULSE_INTERVAL_SECONDS, new_interval_seconds),
    )

    canonical = get_pulse_interval_seconds(consumer)

    async with _get_lock(consumer):
        override = TemporalOverride(
            consumer=consumer,
            pulse_interval_seconds=clamped_interval,
            canonical_interval_seconds=canonical,
            applied_at_epoch=time.time(),
            ttl_seconds=ttl_seconds,
        )
        _OVERRIDES[consumer] = override

    logger.info(
        "escape_temporal_override_applied",
        consumer=consumer,
        new_interval=clamped_interval,
        canonical_interval=canonical,
        ttl_seconds=ttl_seconds,
    )
    return override


async def restore_canonical(consumer: str) -> bool:
    """Elimina el override de un consumer, restaurando canonical.

    Returns:
        True si había un override y se eliminó. False si no había nada.
    """
    if not consumer or not isinstance(consumer, str):
        raise ValueError("consumer must be non-empty string")

    async with _get_lock(consumer):
        existed = consumer in _OVERRIDES
        if existed:
            _OVERRIDES.pop(consumer, None)

    if existed:
        logger.info("escape_canonical_restored", consumer=consumer)
    return existed


def get_effective_pulse_interval(consumer: str, now_epoch: Optional[float] = None) -> int:
    """Retorna el pulse_interval efectivo del consumer.

    Si hay override vigente (no expirado) → retorna override.pulse_interval_seconds
    Si hay override expirado → lo elimina y retorna canonical (auto-cleanup).
    Si no hay override → retorna canonical desde config.

    Síncrona por simplicidad (lectura predominante; el lock sólo aplica a writes).
    """
    if not consumer or not isinstance(consumer, str):
        raise ValueError("consumer must be non-empty string")

    override = _OVERRIDES.get(consumer)
    if override is None:
        return get_pulse_interval_seconds(consumer)

    if override.is_expired(now_epoch=now_epoch):
        # Auto-cleanup: el override expiró, lo removemos y devolvemos canonical
        _OVERRIDES.pop(consumer, None)
        logger.info(
            "escape_temporal_override_expired",
            consumer=consumer,
            canonical_interval=override.canonical_interval_seconds,
            applied_at=override.applied_at_epoch,
            ttl_seconds=override.ttl_seconds,
        )
        return override.canonical_interval_seconds

    return override.pulse_interval_seconds


def get_active_override(consumer: str) -> Optional[TemporalOverride]:
    """Retorna el TemporalOverride activo (no expirado) o None."""
    override = _OVERRIDES.get(consumer)
    if override is None:
        return None
    if override.is_expired():
        _OVERRIDES.pop(consumer, None)
        return None
    return override


def list_active_overrides() -> tuple[TemporalOverride, ...]:
    """Lista snapshot de todos los overrides activos (expira ya cleaned)."""
    now = time.time()
    active = []
    expired = []
    for consumer, override in list(_OVERRIDES.items()):
        if override.is_expired(now_epoch=now):
            expired.append(consumer)
        else:
            active.append(override)
    for c in expired:
        _OVERRIDES.pop(c, None)
    return tuple(active)


def _reset_state_for_tests() -> None:
    """Helper interno SOLO para tests — limpia overrides y locks.

    NUNCA llamar en producción. Útil entre tests para aislar estado.
    """
    _OVERRIDES.clear()
    _LOCKS.clear()
