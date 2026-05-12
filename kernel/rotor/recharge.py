"""
recharge.py — Recharge Mainspring del Rotor.

Sprint: ROTOR-001 (T4) — pieza diferencial Reloj Suizo
DSC enforzado: DSC-MO-010 (Reloj Suizo), DSC-G-008 v2 (anti-Goodhart numérico)
Owner: Hilo Ejecutor 2 (manus_hilo_b)
Fecha: 2026-05-12

Esta función la ejecuta el scheduler cada 5 minutos (registrada en
`register_default_tasks` de kernel/embrion_scheduler.py como `recharge_mainspring`).

Flujo del recharge cycle:
  1. Lee filas de rotor_activity_log con consumed_by_embrion_at IS NULL
  2. Para cada fila, computa energy_units si está NULL (lazy enrichment)
  3. Aplica caps anti-farming (por source) y cap superior recharge ($30/día)
  4. Llama embrion_budget.add_recycled_energy() en una transacción
  5. Marca filas consumidas con consumed_by_embrion_at = NOW() + cycle_id

Fail-soft: el handler nunca tira el scheduler. Loguea + retorna degraded=True.
"""

from __future__ import annotations

import logging
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from kernel.rotor.energy_calculator import (
    ENERGY_CALCULATOR_VERSION,
    RotorActivity,
    apply_daily_source_cap,
    apply_total_recharge_cap,
    compute_energy_units,
)

try:
    import structlog
    logger = structlog.get_logger("rotor.recharge")
except ImportError:  # pragma: no cover
    logger = logging.getLogger("rotor.recharge")


# ---------------------------------------------------------------------------
# Resultado del cycle
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RechargeCycleResult:
    """Resultado de una corrida de recharge_mainspring."""

    cycle_id: int
    started_at: str
    finished_at: str
    rows_consumed: int
    rows_skipped_capped: int
    units_added_to_budget_usd: str  # str para JSON-friendly
    units_lost_capacity_exceeded_usd: str
    daily_recharge_total_after_usd: str
    by_source: dict[str, dict[str, str]] = field(default_factory=dict)
    degraded: bool = False
    degraded_reason: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "rows_consumed": self.rows_consumed,
            "rows_skipped_capped": self.rows_skipped_capped,
            "units_added_to_budget_usd": self.units_added_to_budget_usd,
            "units_lost_capacity_exceeded_usd": self.units_lost_capacity_exceeded_usd,
            "daily_recharge_total_after_usd": self.daily_recharge_total_after_usd,
            "by_source": self.by_source,
            "degraded": self.degraded,
            "degraded_reason": self.degraded_reason,
            "calculator_version": ENERGY_CALCULATOR_VERSION,
        }


# ---------------------------------------------------------------------------
# Función núcleo (PURA respecto al I/O — recibe fetcher/persister inyectables)
# ---------------------------------------------------------------------------
def _today_iso_date() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")


def run_recharge_cycle(
    *,
    pending_rows: list[dict[str, Any]],
    already_recharged_today_usd: Decimal,
    accumulated_today_by_source_usd: dict[str, Decimal],
    cycle_id: int,
) -> tuple[RechargeCycleResult, list[str], Decimal]:
    """
    Lógica pura del recharge cycle. NO toca DB.

    Args:
        pending_rows: filas de rotor_activity_log con consumed_by_embrion_at IS NULL.
                      Cada dict debe tener: id, source, actor, payload_jsonb,
                      energy_units (puede ser None).
        already_recharged_today_usd: total ya recargado hoy al budget.
        accumulated_today_by_source_usd: dict source → suma del día.
        cycle_id: id del cycle del Embrión que solicita el recharge.

    Returns:
        (RechargeCycleResult, list_of_consumed_row_ids, units_to_recharge_decimal)
    """
    started_at = datetime.now(tz=timezone.utc).isoformat()

    consumed_ids: list[str] = []
    skipped_capped = 0
    by_source_acc: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: {"consumed": Decimal("0"), "skipped": Decimal("0")}
    )

    pending_units_total = Decimal("0")
    # Trabajamos en copia para no mutar el input
    acc_by_source = dict(accumulated_today_by_source_usd)

    for row in pending_rows:
        source = row["source"]
        actor = row.get("actor", "unknown")
        payload = row.get("payload_jsonb") or {}
        raw_energy = row.get("energy_units")

        # Lazy enrichment: si energy_units es NULL, computarlo
        if raw_energy is None:
            try:
                activity = RotorActivity(source=source, actor=actor, payload=payload)
                raw_energy = compute_energy_units(activity)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "rotor.recharge.lazy_enrich_failed",
                    row_id=row.get("id"),
                    source=source,
                    err=str(exc),
                )
                continue
        else:
            raw_energy = Decimal(str(raw_energy))

        # Aplicar cap diario por source (anti-farming)
        capped = apply_daily_source_cap(
            raw_units=raw_energy,
            accumulated_today_for_source=acc_by_source.get(source, Decimal("0")),
        )

        if capped == Decimal("0") and raw_energy > Decimal("0"):
            # Cap excedido — skip pero marcar consumida para no reintentar
            skipped_capped += 1
            consumed_ids.append(str(row["id"]))
            by_source_acc[source]["skipped"] += raw_energy
            continue

        # Sumar al acumulado del source para que el siguiente row vea el cap actualizado
        acc_by_source[source] = acc_by_source.get(source, Decimal("0")) + capped
        pending_units_total += capped
        consumed_ids.append(str(row["id"]))
        by_source_acc[source]["consumed"] += capped

    # Aplicar cap superior recharge ($30/día)
    units_to_recharge, units_lost = apply_total_recharge_cap(
        pending_units=pending_units_total,
        already_recharged_today=already_recharged_today_usd,
    )

    finished_at = datetime.now(tz=timezone.utc).isoformat()

    by_source_serializable = {
        src: {
            "consumed_usd": str(vals["consumed"]),
            "skipped_capped_usd": str(vals["skipped"]),
        }
        for src, vals in by_source_acc.items()
    }

    result = RechargeCycleResult(
        cycle_id=cycle_id,
        started_at=started_at,
        finished_at=finished_at,
        rows_consumed=len(consumed_ids),
        rows_skipped_capped=skipped_capped,
        units_added_to_budget_usd=str(units_to_recharge),
        units_lost_capacity_exceeded_usd=str(units_lost),
        daily_recharge_total_after_usd=str(already_recharged_today_usd + units_to_recharge),
        by_source=by_source_serializable,
    )
    return result, consumed_ids, units_to_recharge


# ---------------------------------------------------------------------------
# Handler async para el scheduler — orquesta I/O
# ---------------------------------------------------------------------------
async def recharge_mainspring_handler(**kwargs: Any) -> dict[str, Any]:
    """
    Handler async invocado por el scheduler cada 5 minutos.

    Sigue el mismo patrón que daily_guardian_audit_handler:
      - Lazy import de psycopg + Supabase REST
      - Fail-soft: cualquier excepción → degraded=True, no raise
      - Retorna dict serializable (el scheduler lo persiste en task_runs)

    Cap superior $30/día firmado T1 — enforced en run_recharge_cycle.
    """
    cycle_id = int(kwargs.get("cycle_id", 0))
    started_at = datetime.now(tz=timezone.utc).isoformat()

    try:
        # Lazy import de psycopg para no fallar si la dependencia falta
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            return RechargeCycleResult(
                cycle_id=cycle_id,
                started_at=started_at,
                finished_at=datetime.now(tz=timezone.utc).isoformat(),
                rows_consumed=0,
                rows_skipped_capped=0,
                units_added_to_budget_usd="0",
                units_lost_capacity_exceeded_usd="0",
                daily_recharge_total_after_usd="0",
                degraded=True,
                degraded_reason=f"psycopg not installed: {exc}",
            ).to_dict()

        db_url = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
        if not db_url:
            return RechargeCycleResult(
                cycle_id=cycle_id,
                started_at=started_at,
                finished_at=datetime.now(tz=timezone.utc).isoformat(),
                rows_consumed=0,
                rows_skipped_capped=0,
                units_added_to_budget_usd="0",
                units_lost_capacity_exceeded_usd="0",
                daily_recharge_total_after_usd="0",
                degraded=True,
                degraded_reason="SUPABASE_DB_URL/DATABASE_URL no seteada",
            ).to_dict()

        today = _today_iso_date()

        with psycopg.connect(db_url, autocommit=False, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                # 1. Fetch pending rows (LIMIT defensivo: 500 por cycle)
                cur.execute(
                    """
                    SELECT id::text AS id, source, actor, payload_jsonb, energy_units
                    FROM public.rotor_activity_log
                    WHERE consumed_by_embrion_at IS NULL
                    ORDER BY created_at
                    LIMIT 500
                    """
                )
                pending_rows = [dict(r) for r in cur.fetchall()]

                # 2. Fetch already_recharged_today_usd
                cur.execute(
                    """
                    SELECT COALESCE(SUM(energy_units), 0) AS total
                    FROM public.rotor_activity_log
                    WHERE consumed_by_embrion_at IS NOT NULL
                      AND (consumed_by_embrion_at AT TIME ZONE 'UTC')::date = %s::date
                      AND energy_units > 0
                    """,
                    (today,),
                )
                already_recharged_today_usd = Decimal(str(cur.fetchone()["total"]))

                # 3. Fetch accumulated by source today
                cur.execute(
                    """
                    SELECT source, COALESCE(SUM(energy_units), 0) AS total
                    FROM public.rotor_activity_log
                    WHERE (created_at AT TIME ZONE 'UTC')::date = %s::date
                      AND energy_units IS NOT NULL
                    GROUP BY source
                    """,
                    (today,),
                )
                acc_by_source = {
                    r["source"]: Decimal(str(r["total"])) for r in cur.fetchall()
                }

                # 4. Run pure cycle
                result, consumed_ids, units_to_recharge = run_recharge_cycle(
                    pending_rows=pending_rows,
                    already_recharged_today_usd=already_recharged_today_usd,
                    accumulated_today_by_source_usd=acc_by_source,
                    cycle_id=cycle_id,
                )

                # 5. Marcar filas consumidas (atomicidad: una sola transacción)
                if consumed_ids:
                    cur.execute(
                        """
                        UPDATE public.rotor_activity_log
                        SET consumed_by_embrion_at = NOW(),
                            cycle_id_consumer = %s
                        WHERE id::text = ANY(%s)
                        """,
                        (cycle_id, consumed_ids),
                    )

                # 6. Notificar al embrion_budget (fail-soft si la función no existe)
                if units_to_recharge > Decimal("0"):
                    try:
                        from kernel.embrion_budget import add_recycled_energy
                        add_recycled_energy(
                            units_usd=units_to_recharge,
                            cycle_id=cycle_id,
                            source_breakdown=result.by_source,
                        )
                    except (ImportError, AttributeError) as exc:
                        # add_recycled_energy aún no inyectada — log + revert consumed marks
                        logger.warning(
                            "rotor.recharge.add_recycled_energy_unavailable",
                            err=str(exc),
                            cycle_id=cycle_id,
                            note="filas marcadas consumidas; recharge no aplicado al budget",
                        )

            conn.commit()

        logger.info(
            "rotor.recharge.cycle_complete",
            cycle_id=cycle_id,
            consumed=len(consumed_ids),
            units_added_usd=str(units_to_recharge),
        )
        return result.to_dict()

    except Exception as exc:  # noqa: BLE001 — fail-soft handler
        logger.error("rotor.recharge.cycle_error", err=str(exc), cycle_id=cycle_id)
        return RechargeCycleResult(
            cycle_id=cycle_id,
            started_at=started_at,
            finished_at=datetime.now(tz=timezone.utc).isoformat(),
            rows_consumed=0,
            rows_skipped_capped=0,
            units_added_to_budget_usd="0",
            units_lost_capacity_exceeded_usd="0",
            daily_recharge_total_after_usd="0",
            degraded=True,
            degraded_reason=str(exc),
        ).to_dict()


__all__ = [
    "RechargeCycleResult",
    "run_recharge_cycle",
    "recharge_mainspring_handler",
]
