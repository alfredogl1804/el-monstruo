#!/usr/bin/env python
"""Genera snapshot forense de public.scheduled_tasks vía Supabase Management API.

Sprint D-2 cleanup destructivo scheduled_tasks (Hilo Ejecutor 2 = manus_hilo_b).
Autorizado por: DSC-S-013_scheduled_tasks_cleanup_destructivo_v1.

Reemplaza `pg_dump --table=public.scheduled_tasks --data-only --column-inserts`
que requeriría credenciales DB directas (SUPABASE_DB_URL). Aquí usamos el
script de query genérico ~/.monstruo/sb_sql.py que ya está autenticado vía
Supabase Management API + service_role JWT.

Salida:
  discovery_forense/SNAPSHOTS/2026_05_11_pre_cleanup_scheduled_tasks.sql.gz

Formato:
  INSERT statements estilo pg_dump --column-inserts. Restaurable con:
    gunzip -c <snapshot>.sql.gz | psql $SUPABASE_DB_URL

Usage:
  python3 scripts/_snapshot_scheduled_tasks.py
"""
import datetime as dt
import gzip
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path


SNAPSHOT_PATH = Path("discovery_forense/SNAPSHOTS/2026_05_11_pre_cleanup_scheduled_tasks.sql.gz")
SB_SQL = os.path.expanduser("~/.monstruo/sb_sql.py")
TABLE = "public.scheduled_tasks"


def _sb_sql(query: str):
    """Ejecuta query via sb_sql.py y retorna lista de dicts.

    El output de sb_sql empieza con un header `[HTTP 201]\n` seguido
    de un JSON array/object. Detectamos el primer caracter `[` o `{`
    que esté al inicio de línea y parseamos desde ahí.
    """
    if not Path(SB_SQL).exists():
        print(f"ERROR: {SB_SQL} no existe (esperado en ~/.monstruo/sb_sql.py)")
        sys.exit(1)
    result = subprocess.run(
        ["python3", SB_SQL, "sql", "-q", query],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        print(f"sb_sql error rc={result.returncode}: stderr={result.stderr}")
        sys.exit(2)
    stdout = result.stdout
    # Buscar inicio del JSON: primer `\n[` o `\n{` después del header.
    idx_bracket = stdout.find("\n[")
    idx_brace = stdout.find("\n{")
    candidates = [i for i in (idx_bracket, idx_brace) if i != -1]
    if not candidates:
        # Quizá el output empieza directo con `[` o `{` sin header
        s = stdout.strip()
        if s.startswith("[") or s.startswith("{"):
            try:
                return json.loads(s)
            except json.JSONDecodeError as e:
                print(f"JSON parse fail (sin header): {e}")
                print(f"Stdout primeras 500 chars: {stdout[:500]}")
                sys.exit(4)
        print(f"sb_sql no devolvió JSON parseable. stdout primeras 500 chars:\n{stdout[:500]}")
        sys.exit(3)
    start = min(candidates) + 1  # +1 para skipear el \n
    json_blob = stdout[start:].strip()
    try:
        return json.loads(json_blob)
    except json.JSONDecodeError as e:
        print(f"JSON parse fail: {e}")
        print(f"Blob primeras 500 chars: {json_blob[:500]}")
        sys.exit(4)


def _format_value(v):
    """Formatea un valor Python como literal SQL Postgres."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, (dict, list)):
        # JSON literal escapado
        j = json.dumps(v, ensure_ascii=False)
        return "'" + j.replace("'", "''") + "'::jsonb"
    # str u otros
    s = str(v)
    return "'" + s.replace("'", "''") + "'"


def main() -> int:
    print(f"[1] Snapshot forense de {TABLE}")
    print(f"    Output: {SNAPSHOT_PATH}")

    # 1) Schema columns en orden
    columns_rows = _sb_sql(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema='public' AND table_name='scheduled_tasks' "
        "ORDER BY ordinal_position"
    )
    columns = [r["column_name"] for r in columns_rows]
    print(f"    Columns: {len(columns)}")

    # 2) Count
    cnt_rows = _sb_sql("SELECT COUNT(*) AS cnt FROM scheduled_tasks")
    total = cnt_rows[0]["cnt"]
    print(f"    Rows a snapshotear: {total}")

    # 3) Paginación SELECT — sb_sql trae todo de una; si supera 50k cambiar a paginated
    # Pedimos todas las columnas explícitamente
    col_list = ", ".join(columns)
    rows = _sb_sql(f"SELECT {col_list} FROM scheduled_tasks ORDER BY created_at NULLS LAST")
    print(f"    Filas recibidas: {len(rows)}")

    if len(rows) != total:
        print(f"    WARN: count mismatch (total={total}, received={len(rows)})")

    # 4) Generar SQL en formato column-inserts
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "--",
        "-- Snapshot forense de public.scheduled_tasks",
        f"-- Generado: {dt.datetime.utcnow().isoformat()}Z",
        f"-- Total rows: {total}",
        "-- Autor: Hilo Ejecutor 2 (manus_hilo_b)",
        "-- Sprint: D-2 cleanup destructivo scheduled_tasks",
        "-- DSC: DSC-S-013_scheduled_tasks_cleanup_destructivo_v1",
        "--",
        "-- Restauración:",
        "--   gunzip -c 2026_05_11_pre_cleanup_scheduled_tasks.sql.gz | psql $SUPABASE_DB_URL",
        "--",
        "SET statement_timeout = 0;",
        "SET client_encoding = 'UTF8';",
        "SET standard_conforming_strings = on;",
        "",
    ]
    sql_lines = list(header)

    insert_prefix = f"INSERT INTO public.scheduled_tasks ({col_list}) VALUES"
    for r in rows:
        vals = ", ".join(_format_value(r[c]) for c in columns)
        sql_lines.append(f"{insert_prefix} ({vals});")

    sql_lines.append("")
    sql_lines.append("-- EOF snapshot")
    sql_content = "\n".join(sql_lines)

    # 5) gzip y escribir
    with gzip.open(SNAPSHOT_PATH, "wt", encoding="utf-8", compresslevel=9) as f:
        f.write(sql_content)

    size_kb = SNAPSHOT_PATH.stat().st_size / 1024.0
    print(f"    OK — snapshot escrito ({size_kb:.1f} KB gzipped, {len(rows)} INSERT statements)")

    # 6) Sidecar metadata para auditoría
    # Path.with_suffix solo cambia la última extensión, generamos el nombre manualmente.
    meta_path = SNAPSHOT_PATH.parent / (SNAPSHOT_PATH.name + ".meta.json")
    meta = {
        "generated_at_utc": dt.datetime.utcnow().isoformat() + "Z",
        "table": TABLE,
        "total_rows": total,
        "rows_in_snapshot": len(rows),
        "columns": columns,
        "compression": "gzip",
        "format": "column_inserts",
        "size_bytes": SNAPSHOT_PATH.stat().st_size,
        "purpose": "pre-cleanup forensic backup for D-2 destructive cleanup",
        "dsc": "DSC-S-013_scheduled_tasks_cleanup_destructivo_v1",
        "sprint": "D-2",
        "autor": "manus_hilo_ejecutor_2",
        "restore_command": "gunzip -c <file>.sql.gz | psql $SUPABASE_DB_URL",
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"    Sidecar metadata: {meta_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
