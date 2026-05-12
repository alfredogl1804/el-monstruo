"""
Persistencia del Rotor — INSERT en rotor_activity_log.

Sprint: ROTOR-001 (T2 capa de persistencia compartida)
Owner: Hilo Ejecutor 2 (manus_hilo_b)

Lazy import de psycopg para no romper imports en entornos sin DB.
"""

from __future__ import annotations

import json
import logging
import os
from decimal import Decimal
from typing import Optional

from kernel.rotor.energy_calculator import (
    ENERGY_CALCULATOR_VERSION,
    RotorActivity,
    compute_energy_units,
)

logger = logging.getLogger(__name__)


def _get_db_url() -> str:
    """Fail-loud: requiere SUPABASE_DB_URL o DATABASE_URL."""
    url = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "rotor.persistence: SUPABASE_DB_URL o DATABASE_URL requerida"
        )
    return url


def persist_activity(activity: RotorActivity, *, compute_energy: bool = True) -> Optional[str]:
    """
    Persiste una RotorActivity en public.rotor_activity_log.

    Si compute_energy=True (default), pre-calcula energy_units localmente para
    evitar el polling lag entre captura y enriquecimiento.

    Returns:
        UUID de la fila creada (string) o None si falló.

    Raises:
        RuntimeError si no hay DB URL configurada (fail-loud).
        psycopg.Error si la inserción falla (caller decide fail-soft).
    """
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError(
            f"rotor.persistence: psycopg no instalado ({exc}). "
            "Run: pip install 'psycopg[binary]'"
        ) from exc

    db_url = _get_db_url()

    energy_units: Optional[Decimal] = None
    energy_calc_version: Optional[str] = None
    if compute_energy:
        try:
            energy_units = compute_energy_units(activity)
            energy_calc_version = ENERGY_CALCULATOR_VERSION
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "rotor.persist: compute_energy fallo (%s), persistiendo con NULL",
                exc,
            )

    sql = """
        INSERT INTO public.rotor_activity_log
            (source, actor, payload_jsonb, energy_units, energy_calculator_version)
        VALUES
            (%s, %s, %s::jsonb, %s, %s)
        RETURNING id::text
    """

    with psycopg.connect(db_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    activity.source,
                    activity.actor,
                    json.dumps(dict(activity.payload), default=str),
                    energy_units,
                    energy_calc_version,
                ),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return str(row[0])


__all__ = ["persist_activity"]
