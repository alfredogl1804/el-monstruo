"""kernel.escape.throttler — Throttler determinístico del Reloj Suizo.

Pieza Escape (doctrina §2.1 fila 2) — dosifica el consumo del embrion_budget
en pulsos discretos por consumer.

Spec firmado: bridge/sprints_propuestos/sprint_ESCAPE_001_throttler_deterministico.md
Defaults firmados: kernel/escape/config.py (T1 Alfredo 2026-05-12 ~07:55 UTC)

API canónica:

    from kernel.escape.throttler import Escapement
    escapement = Escapement("embrion_loop_latido")
    can_proceed, next_pulse_at = await escapement.can_pulse()
    if not can_proceed:
        await escapement.block_attempt()
        # sleep hasta next_pulse_at + retry
    await escapement.record_pulse()  # consume budget + persiste

DSC enforzados:
- DSC-MO-006 v1.1 (doctrina del silencio) — wiring via marcadores BEGIN/END
- DSC-MO-010 (Reloj Suizo §2.1 fila 2)
- DSC-G-008 v2 (anti-Goodhart) — blocked_count tracking obligatorio
- DSC-S-006 v1.1 (RLS) — persistencia vía service_role only
- DSC-S-016 (anti-fabricación) — único caller autorizado de budget.consume()
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from kernel.escape.config import (
    DEFAULT_ENERGY_CONSUMED_PER_PULSE,
    REGISTRY_CONSUMERS,
    get_pulse_interval_seconds,
    is_registered_consumer,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Resultado tipado de can_pulse / record_pulse
# ═══════════════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class PulseDecision:
    """Decisión binaria del Escapement.

    Si can_proceed=True, el caller puede ejecutar y debe llamar record_pulse() después.
    Si can_proceed=False, el caller debe esperar hasta next_pulse_at (o llamar block_attempt()).
    """
    can_proceed: bool
    next_pulse_at: Optional[datetime]
    last_pulse_at: Optional[datetime]
    consumer: str
    pulse_interval_seconds: int


@dataclass
class PulseRecord:
    """Pulso registrado tras record_pulse() exitoso."""
    consumer: str
    energy_consumed: Decimal
    pulse_interval_seconds: int
    recorded_at: datetime
    blocked_count_in_window: int = 0
    metadata: dict = field(default_factory=dict)
    persisted: bool = False
    persist_error: Optional[str] = None
    budget_consumed: bool = False


# ═══════════════════════════════════════════════════════════════════════════════
# Estado en memoria por consumer (per-proceso)
# ═══════════════════════════════════════════════════════════════════════════════
@dataclass
class _ConsumerState:
    """Estado en memoria del último pulso por consumer.

    Postgres `pulse_id` BIGSERIAL es la fuente de verdad cross-proceso.
    Este estado en memoria es para decisiones rápidas locales.
    """
    last_pulse_at: Optional[datetime] = None
    blocked_count_in_window: int = 0


_consumer_states: dict[str, _ConsumerState] = {}
_state_lock = asyncio.Lock()


# ═══════════════════════════════════════════════════════════════════════════════
# Escapement — clase principal
# ═══════════════════════════════════════════════════════════════════════════════
class Escapement:
    """Escapement determinístico por consumer.

    Cada instancia maneja UN consumer. Comparte estado en memoria con otras
    instancias del mismo consumer (via _consumer_states dict global).

    Para persistencia cross-proceso, la fuente de verdad es escape_pulse_log
    en Supabase (consultar via `_load_last_pulse_from_db()` opcional).

    Uso:
        escapement = Escapement("embrion_loop_latido")
        decision = await escapement.can_pulse()
        if decision.can_proceed:
            # ejecutar acción consumidora
            await escapement.record_pulse(energy_consumed=Decimal("1.0"))
        else:
            await escapement.block_attempt()
            # opcional: sleep((decision.next_pulse_at - now).total_seconds())
    """

    def __init__(
        self,
        consumer: str,
        pulse_interval_seconds: Optional[int] = None,
        *,
        budget_consumer=None,
    ):
        """Args:
            consumer: nombre canónico (validado vs REGISTRY_CONSUMERS, warning si desconocido).
            pulse_interval_seconds: override del default. Si None, usa get_pulse_interval_seconds(consumer).
            budget_consumer: callable async/sync que decrementa budget. Si None, lazy import
                de kernel.embrion_budget.consume cuando se necesite. Útil para inyectar mock en tests.
        """
        self.consumer = consumer
        if pulse_interval_seconds is None:
            self.pulse_interval_seconds = get_pulse_interval_seconds(consumer)
        else:
            self.pulse_interval_seconds = max(1, int(pulse_interval_seconds))

        self._budget_consumer = budget_consumer

        if not is_registered_consumer(consumer):
            logger.warning(
                "escape_consumer_not_registered",
                extra={
                    "consumer": consumer,
                    "registry": sorted(REGISTRY_CONSUMERS),
                    "fallback_interval_seconds": self.pulse_interval_seconds,
                },
            )

    # ───────────────────────────────────────────────────────────────────────────
    # can_pulse
    # ───────────────────────────────────────────────────────────────────────────
    async def can_pulse(self, *, now: Optional[datetime] = None) -> PulseDecision:
        """Decisión binaria: ¿puede ejecutar ahora?

        Args:
            now: timestamp override para tests (default: datetime.now(UTC)).

        Returns:
            PulseDecision con can_proceed, next_pulse_at, last_pulse_at.
        """
        current = now if now is not None else datetime.now(timezone.utc)

        async with _state_lock:
            state = _consumer_states.setdefault(self.consumer, _ConsumerState())
            last = state.last_pulse_at

        if last is None:
            # Primer pulso ever para este consumer en este proceso
            return PulseDecision(
                can_proceed=True,
                next_pulse_at=None,
                last_pulse_at=None,
                consumer=self.consumer,
                pulse_interval_seconds=self.pulse_interval_seconds,
            )

        next_pulse = last + timedelta(seconds=self.pulse_interval_seconds)
        if current >= next_pulse:
            return PulseDecision(
                can_proceed=True,
                next_pulse_at=None,
                last_pulse_at=last,
                consumer=self.consumer,
                pulse_interval_seconds=self.pulse_interval_seconds,
            )

        return PulseDecision(
            can_proceed=False,
            next_pulse_at=next_pulse,
            last_pulse_at=last,
            consumer=self.consumer,
            pulse_interval_seconds=self.pulse_interval_seconds,
        )

    # ───────────────────────────────────────────────────────────────────────────
    # record_pulse
    # ───────────────────────────────────────────────────────────────────────────
    async def record_pulse(
        self,
        energy_consumed: Decimal = DEFAULT_ENERGY_CONSUMED_PER_PULSE,
        *,
        metadata: Optional[dict] = None,
        now: Optional[datetime] = None,
    ) -> PulseRecord:
        """Registra pulso: actualiza estado en memoria + consume budget + persiste.

        Orden canónico:
        1. Actualiza last_pulse_at en memoria (best-effort)
        2. Consume budget vía embrion_budget.consume(amount) — único caller autorizado
        3. Persiste fila en escape_pulse_log (fail-soft: si DB no disponible, log warning)
        4. Resetea blocked_count_in_window a 0

        Args:
            energy_consumed: cantidad a consumir del budget (default 1.0).
            metadata: dict opcional persistido en metadata JSONB.
            now: timestamp override para tests.

        Returns:
            PulseRecord con detalles del pulso registrado.
        """
        current = now if now is not None else datetime.now(timezone.utc)
        meta = dict(metadata) if metadata else {}

        async with _state_lock:
            state = _consumer_states.setdefault(self.consumer, _ConsumerState())
            blocked_in_window = state.blocked_count_in_window
            state.last_pulse_at = current
            state.blocked_count_in_window = 0  # reset post-pulso

        # 2. Consume budget — único caller autorizado del Escape
        budget_ok = await self._invoke_budget_consume(energy_consumed)

        # 3. Persist a escape_pulse_log (fail-soft)
        persisted, persist_error = await self._persist_pulse(
            consumer=self.consumer,
            energy_consumed=energy_consumed,
            pulse_interval_seconds=self.pulse_interval_seconds,
            blocked_count=blocked_in_window,
            metadata=meta,
            now=current,
        )

        return PulseRecord(
            consumer=self.consumer,
            energy_consumed=energy_consumed,
            pulse_interval_seconds=self.pulse_interval_seconds,
            recorded_at=current,
            blocked_count_in_window=blocked_in_window,
            metadata=meta,
            persisted=persisted,
            persist_error=persist_error,
            budget_consumed=budget_ok,
        )

    # ───────────────────────────────────────────────────────────────────────────
    # block_attempt
    # ───────────────────────────────────────────────────────────────────────────
    async def block_attempt(self) -> int:
        """Registra que se intentó pulsar dentro del intervalo activo.

        Incrementa blocked_count_in_window. El contador se resetea al siguiente
        record_pulse exitoso, persistiéndose en esa fila de escape_pulse_log.

        DSC-G-008 v2 (anti-Goodhart) — visibility de presión sobre el throttler.

        Returns:
            int — blocked_count_in_window post-incremento.
        """
        async with _state_lock:
            state = _consumer_states.setdefault(self.consumer, _ConsumerState())
            state.blocked_count_in_window += 1
            count = state.blocked_count_in_window

        logger.info(
            "escape_block_attempt",
            extra={
                "consumer": self.consumer,
                "blocked_count_in_window": count,
                "pulse_interval_seconds": self.pulse_interval_seconds,
            },
        )
        return count

    # ───────────────────────────────────────────────────────────────────────────
    # Internals
    # ───────────────────────────────────────────────────────────────────────────
    async def _invoke_budget_consume(self, amount: Decimal) -> bool:
        """Invoca embrion_budget.consume(amount). Fail-soft.

        Si _budget_consumer fue inyectado (test), usa ese.
        Sino lazy import de kernel.embrion_budget.consume.
        Si la función no existe o falla, log warning y retorna False.
        """
        try:
            consumer = self._budget_consumer
            if consumer is None:
                # Lazy import — evita import cycle con embrion_budget
                from kernel import embrion_budget  # noqa: PLC0415

                consumer = getattr(embrion_budget, "consume", None)
                if consumer is None:
                    logger.warning(
                        "escape_budget_consume_missing",
                        extra={"consumer": self.consumer, "amount": str(amount)},
                    )
                    return False

            result = consumer(amount)
            if asyncio.iscoroutine(result):
                result = await result
            return bool(result)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "escape_budget_consume_error",
                extra={
                    "consumer": self.consumer,
                    "amount": str(amount),
                    "error": str(exc),
                },
            )
            return False

    async def _persist_pulse(
        self,
        *,
        consumer: str,
        energy_consumed: Decimal,
        pulse_interval_seconds: int,
        blocked_count: int,
        metadata: dict,
        now: datetime,
    ) -> tuple[bool, Optional[str]]:
        """Persiste fila en escape_pulse_log via _SupabaseRest del budget.

        Fail-soft: si DB no disponible o env vars missing, retorna (False, error).
        No bloquea el flujo del caller (el pulso ya pasó en memoria).
        """
        try:
            # Reuse del helper REST del budget (DRY)
            from kernel import embrion_budget  # noqa: PLC0415

            rest = getattr(embrion_budget, "_SupabaseRest", None)
            if rest is None:
                return (False, "supabase_rest_helper_missing")

            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            if not url or not key:
                return (False, "supabase_env_missing")

            client = rest(url, key)
            row = {
                "consumer": consumer,
                "energy_consumed": str(energy_consumed),
                "pulse_interval_seconds": int(pulse_interval_seconds),
                "blocked_count": int(blocked_count),
                "metadata": json.dumps(metadata) if metadata else "{}",
                "created_at": now.isoformat(),
            }
            await self._maybe_async(client.insert, "escape_pulse_log", [row])
            return (True, None)
        except Exception as exc:  # noqa: BLE001
            return (False, f"{type(exc).__name__}: {exc}")

    @staticmethod
    async def _maybe_async(fn, *args, **kwargs):
        """Llama fn; si retorna coroutine, await; si sync, retorna directo."""
        result = fn(*args, **kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers para tests / reset / introspection
# ═══════════════════════════════════════════════════════════════════════════════
async def reset_consumer_state(consumer: Optional[str] = None) -> None:
    """Resetea estado en memoria. Si consumer=None, resetea todos.

    Útil para tests que requieren estado limpio entre casos.
    """
    async with _state_lock:
        if consumer is None:
            _consumer_states.clear()
        else:
            _consumer_states.pop(consumer, None)


async def snapshot_state() -> dict:
    """Snapshot del estado en memoria (todos los consumers)."""
    async with _state_lock:
        return {
            c: {
                "last_pulse_at": s.last_pulse_at.isoformat() if s.last_pulse_at else None,
                "blocked_count_in_window": s.blocked_count_in_window,
            }
            for c, s in _consumer_states.items()
        }
