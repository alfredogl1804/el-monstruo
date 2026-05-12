#!/usr/bin/env python
"""Cleanup destructivo de duplicados en public.scheduled_tasks.

Sprint D-2 (Hilo Ejecutor 2 = manus_hilo_b).
Autorizado por: DSC-S-013_scheduled_tasks_cleanup_destructivo_v1.

Lógica:
  Para cada (name, embrion_id), conservar la fila con MAX(last_run);
  si last_run IS NULL para todas las filas del grupo, conservar
  MAX(created_at). Borrar las demás.

Seguridad doble-llave:
  Default --dry-run=true. Para ejecutar el DELETE real se requiere:
    1) Pasar --apply en CLI
    2) Tener EMBRION_D2_CLEANUP_AUTHORIZED=true en env

Logging:
  Estructurado a discovery_forense/SNAPSHOTS/scheduled_tasks_cleanup_log_2026_05_11.txt

Idempotente:
  Si se ejecuta dos veces seguidas, la segunda no borra nada (no hay duplicados).

Usage:
  # Dry-run (default, seguro):
  python3 scripts/_cleanup_scheduled_tasks_duplicates.py
  python3 scripts/_cleanup_scheduled_tasks_duplicates.py --dry-run

  # Apply real (requiere doble llave):
  EMBRION_D2_CLEANUP_AUTHORIZED=true python3 scripts/_cleanup_scheduled_tasks_duplicates.py --apply
"""
import argparse
import datetime as dt
import os
import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("ERROR: psycopg2 no instalado. Instalar con: pip install psycopg2-binary")
    sys.exit(1)


# ── Configuración ────────────────────────────────────────────────────────────
DB_URL = os.environ.get("SUPABASE_DB_URL")
LOG_PATH = Path("discovery_forense/SNAPSHOTS/scheduled_tasks_cleanup_log_2026_05_11.txt")
TABLE = "scheduled_tasks"


def _connect():
    if not DB_URL:
        print("ERROR: SUPABASE_DB_URL no está en env")
        sys.exit(1)
    url = DB_URL
    if "?" in url:
        if "sslmode" not in url:
            url = url + "&sslmode=require"
    else:
        url = url + "?sslmode=require"
    conn = psycopg2.connect(url)
    conn.autocommit = False
    return conn


def _log(line: str, also_print: bool = True) -> None:
    """Append a una línea estructurada al log forense (y opcional a stdout)."""
    timestamp = dt.datetime.utcnow().isoformat() + "Z"
    out = f"[{timestamp}] {line}"
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(out + "\n")
    if also_print:
        print(out)


def _count_state(cur) -> dict:
    """Snapshot binario del estado actual de la tabla."""
    cur.execute(
        f"""
        SELECT
          COUNT(*) AS total_rows,
          COUNT(DISTINCT name) AS unique_names,
          COUNT(DISTINCT (name, embrion_id)) AS unique_pairs
        FROM {TABLE}
        """
    )
    row = cur.fetchone()
    return {
        "total_rows": row["total_rows"],
        "unique_names": row["unique_names"],
        "unique_pairs": row["unique_pairs"],
    }


def _select_winners(cur) -> list[dict]:
    """Para cada (name, embrion_id), elige la fila ganadora a conservar.

    Regla: MAX(last_run) primero; tie-break por MAX(created_at).
    """
    cur.execute(
        f"""
        WITH ranked AS (
          SELECT
            id, name, embrion_id, last_run, created_at,
            ROW_NUMBER() OVER (
              PARTITION BY name, embrion_id
              ORDER BY
                last_run DESC NULLS LAST,
                created_at DESC NULLS LAST
            ) AS rn
          FROM {TABLE}
        )
        SELECT id, name, embrion_id, last_run, created_at
        FROM ranked
        WHERE rn = 1
        ORDER BY name
        """
    )
    return cur.fetchall()


def _select_losers(cur) -> list[dict]:
    """Filas a borrar (todas las que NO ganan por grupo)."""
    cur.execute(
        f"""
        WITH ranked AS (
          SELECT
            id, name, embrion_id, last_run, created_at,
            ROW_NUMBER() OVER (
              PARTITION BY name, embrion_id
              ORDER BY
                last_run DESC NULLS LAST,
                created_at DESC NULLS LAST
            ) AS rn
          FROM {TABLE}
        )
        SELECT id, name, embrion_id
        FROM ranked
        WHERE rn > 1
        """
    )
    return cur.fetchall()


def main():
    parser = argparse.ArgumentParser(description="Cleanup duplicados scheduled_tasks (Sprint D-2)")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Ejecutar el DELETE real. Requiere también EMBRION_D2_CLEANUP_AUTHORIZED=true en env.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="(Default) No borra nada, solo reporta. Activar explícitamente o omitir --apply.",
    )
    args = parser.parse_args()

    # Doble llave para --apply
    apply_mode = args.apply and not args.dry_run
    authorized = os.environ.get("EMBRION_D2_CLEANUP_AUTHORIZED", "").lower() == "true"

    if apply_mode and not authorized:
        print("ERROR: --apply requiere también EMBRION_D2_CLEANUP_AUTHORIZED=true en env.")
        print("       Sin esa env var, este script ejecuta SOLO en modo dry-run.")
        sys.exit(2)

    mode_label = "APPLY (DELETE REAL)" if apply_mode else "DRY-RUN (no borra nada)"
    print()
    print(f"╔══ Cleanup scheduled_tasks — Modo: {mode_label} ══╗")
    print()
    _log(f"START mode={mode_label}")

    conn = _connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # 1) Snapshot pre
    pre = _count_state(cur)
    _log(f"PRE total_rows={pre['total_rows']} unique_names={pre['unique_names']} unique_pairs={pre['unique_pairs']}")

    if pre["total_rows"] == pre["unique_pairs"]:
        _log("OK: tabla ya sin duplicados. No hay nada que limpiar. Salgo sin error.")
        cur.close()
        conn.close()
        return 0

    # 2) Computar winners/losers
    winners = _select_winners(cur)
    losers = _select_losers(cur)
    _log(f"COMPUTED winners={len(winners)} losers={len(losers)}")

    # Reporte detallado de ganadores
    print()
    print(f"Filas a CONSERVAR ({len(winners)}):")
    for w in winners:
        print(
            f"  - name={w['name']:25s}  embrion_id={w['embrion_id'] or '<null>':20s}  "
            f"last_run={w['last_run']!s:<40s}  created_at={w['created_at']}"
        )
        _log(
            f"KEEP id={w['id']} name={w['name']} embrion_id={w['embrion_id']} "
            f"last_run={w['last_run']} created_at={w['created_at']}"
        )

    print()
    print(f"Filas a BORRAR ({len(losers)}):")
    by_name = {}
    for l in losers:
        by_name.setdefault(l["name"], 0)
        by_name[l["name"]] += 1
    for name, cnt in sorted(by_name.items(), key=lambda x: -x[1]):
        print(f"  - {name:30s}  {cnt:>6d} filas")
    _log(f"DELETE_BREAKDOWN { {k: int(v) for k, v in by_name.items()} }")

    if not apply_mode:
        print()
        print("MODO DRY-RUN — no se borrará nada.")
        print("Para ejecutar el DELETE real:")
        print("  EMBRION_D2_CLEANUP_AUTHORIZED=true \\")
        print("  python3 scripts/_cleanup_scheduled_tasks_duplicates.py --apply")
        _log("DRY_RUN_END — no se ejecutó DELETE")
        cur.close()
        conn.close()
        return 0

    # 3) Apply mode — DELETE real
    loser_ids = [l["id"] for l in losers]
    _log(f"APPLY about_to_delete={len(loser_ids)} ids")

    try:
        cur.execute(
            f"DELETE FROM {TABLE} WHERE id = ANY(%s::uuid[])",
            (loser_ids,),
        )
        deleted = cur.rowcount
        conn.commit()
        _log(f"DELETE_OK rows_deleted={deleted}")
    except Exception as e:
        conn.rollback()
        _log(f"DELETE_FAIL error={e!s}")
        cur.close()
        conn.close()
        sys.exit(3)

    # 4) Snapshot post
    post = _count_state(cur)
    _log(f"POST total_rows={post['total_rows']} unique_names={post['unique_names']} unique_pairs={post['unique_pairs']}")

    print()
    print(f"╔══ RESULTADO ══╗")
    print(f"  PRE  total_rows={pre['total_rows']}  unique_pairs={pre['unique_pairs']}")
    print(f"  POST total_rows={post['total_rows']}  unique_pairs={post['unique_pairs']}")
    print(f"  Filas borradas: {pre['total_rows'] - post['total_rows']}")

    # Verificación binaria del invariante
    if post["total_rows"] != post["unique_pairs"]:
        _log("WARN: post total_rows != unique_pairs (algo raro pasó)")
        cur.close()
        conn.close()
        sys.exit(4)

    _log("DONE_CLEAN")
    cur.close()
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
