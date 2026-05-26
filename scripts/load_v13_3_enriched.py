#!/usr/bin/env python3
"""
Cargar el snapshot v13.3_enriched a Supabase del Monstruo.

Usa dollar-quoted strings de Postgres ($mq$...$mq$) para evitar escape issues.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SNAPSHOT_VERSION = "v13.3_enriched"
SNAPSHOT_DATE = "2026-05-16"
TAG = "mq"  # dollar-quote tag

# Tags alternos por si el contenido contiene "$mq$" literal (improbable)
TAGS_FALLBACK = ["mq", "mq2", "mq3", "monstruo"]


def safe_dollar_quote(s):
    """Devuelve un dollar-quoted literal seguro escogiendo un tag que no aparezca en s."""
    if s is None or s == "":
        return "NULL"
    s = str(s)
    for tag in TAGS_FALLBACK:
        delim = f"${tag}$"
        if delim not in s:
            return f"{delim}{s}{delim}"
    # Último recurso: escape clásico
    return "E'" + s.replace("\\", "\\\\").replace("'", "''") + "'"


def sql_array(items):
    """ARRAY[$mq$...$mq$, ...]::text[]."""
    if not items:
        return "NULL"
    cleaned = [str(x) for x in items if x is not None]
    if not cleaned:
        return "NULL"
    parts = [safe_dollar_quote(x) for x in cleaned]
    return "ARRAY[" + ",".join(parts) + "]::text[]"


def sql_str(s):
    return safe_dollar_quote(s)


def sql_bool(b):
    if b is None:
        return "NULL"
    return "TRUE" if b else "FALSE"


def sql_num(n):
    if n is None:
        return "NULL"
    try:
        return str(float(n))
    except (TypeError, ValueError):
        return "NULL"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--batch", type=int, default=50)
    args = ap.parse_args()

    src = Path(args.file).expanduser()
    if not src.exists():
        print(f"ERROR: {src} no existe", file=sys.stderr)
        sys.exit(1)

    services = json.load(open(src))
    print(f"Cargando {len(services)} servicios como snapshot {SNAPSHOT_VERSION} ({SNAPSHOT_DATE})")

    cols = [
        "snapshot_version",
        "snapshot_date",
        "nombre",
        "nombre_canonico",
        "categoria",
        "que_es",
        "para_que_sirve",
        "capacidades",
        "tiene_api",
        "api_auth_method",
        "api_docs_url",
        "tiene_ia",
        "tipo_ia",
        "monstruo_fit",
        "padre",
        "gratuito",
        "alternativas",
        "url_oficial",
        "confidence",
        "razonamiento",
        "costo_mxn",
        "estado",
        "notas",
        "fuentes",
    ]

    batches = []
    for i in range(0, len(services), args.batch):
        batch = services[i : i + args.batch]
        values = []
        for s in batch:
            row = (
                f"({sql_str(SNAPSHOT_VERSION)},"
                f"{sql_str(SNAPSHOT_DATE)},"
                f"{sql_str(s.get('nombre_input', ''))},"
                f"{sql_str(s.get('nombre_canonico'))},"
                f"{sql_str(s.get('categoria'))},"
                f"{sql_str(s.get('que_es'))},"
                f"{sql_str(s.get('para_que_sirve'))},"
                f"{sql_array(s.get('capacidades') or [])},"
                f"{sql_bool(s.get('tiene_api'))},"
                f"{sql_str(s.get('api_auth_method'))},"
                f"{sql_str(s.get('api_docs_url'))},"
                f"{sql_bool(s.get('tiene_ia'))},"
                f"{sql_array(s.get('tipo_ia') or [])},"
                f"{sql_str(s.get('monstruo_fit'))},"
                f"{sql_str(s.get('padre'))},"
                f"{sql_bool(s.get('gratuito'))},"
                f"{sql_array(s.get('alternativas') or [])},"
                f"{sql_str(s.get('url_oficial'))},"
                f"{sql_num(s.get('confidence'))},"
                f"{sql_str(s.get('razonamiento'))},"
                f"0,"
                f"{sql_str('activo')},"
                f"{sql_str(s.get('contexto_v11_v13', ''))},"
                f"{sql_str('enriquecido_gemini_2.5_pro_grounding_2026-05-16')})"
            )
            values.append(row)

        sql = (
            f"INSERT INTO public.monstruo_inventario_suscripciones "
            f"({','.join(cols)}) VALUES "
            + ",\n".join(values)
            + "\nON CONFLICT (snapshot_version, nombre) DO UPDATE SET "
            "nombre_canonico=EXCLUDED.nombre_canonico,"
            "categoria=EXCLUDED.categoria,"
            "que_es=EXCLUDED.que_es,"
            "para_que_sirve=EXCLUDED.para_que_sirve,"
            "capacidades=EXCLUDED.capacidades,"
            "tiene_api=EXCLUDED.tiene_api,"
            "api_auth_method=EXCLUDED.api_auth_method,"
            "api_docs_url=EXCLUDED.api_docs_url,"
            "tiene_ia=EXCLUDED.tiene_ia,"
            "tipo_ia=EXCLUDED.tipo_ia,"
            "monstruo_fit=EXCLUDED.monstruo_fit,"
            "padre=EXCLUDED.padre,"
            "gratuito=EXCLUDED.gratuito,"
            "alternativas=EXCLUDED.alternativas,"
            "url_oficial=EXCLUDED.url_oficial,"
            "confidence=EXCLUDED.confidence,"
            "razonamiento=EXCLUDED.razonamiento,"
            "updated_at=NOW();"
        )
        batches.append(sql)

    print(f"Generados {len(batches)} batches de hasta {args.batch} servicios cada uno")

    if args.dry_run:
        print("\n=== DRY RUN ===")
        # Buscar el batch que tenía Apify (batch 3) para validar
        for i, sql in enumerate(batches, 1):
            if "Apify" in sql:
                print(f"Batch {i} (con Apify) primeros 600 chars:")
                idx = sql.find("Apify")
                print(sql[max(0, idx - 100) : idx + 500])
                break
        return

    total_ok = 0
    for i, sql in enumerate(batches, 1):
        tmpfile = Path(f"/tmp/load_v13_3_batch_{i}.sql")
        tmpfile.write_text(sql)

        result = subprocess.run(
            ["python3", str(Path.home() / ".monstruo" / "sb_sql.py"), "sql", "-f", str(tmpfile)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and "[HTTP 2" in result.stdout:
            total_ok += min(args.batch, len(services) - (i - 1) * args.batch)
            print(f"  Batch {i}/{len(batches)} OK ({total_ok}/{len(services)})")
        else:
            print(f"  Batch {i}/{len(batches)} ERROR")
            print(f"    stdout (last 400): {result.stdout[-400:]}")
            print(f"    SQL guardado en {tmpfile} para inspección")
            sys.exit(2)

        tmpfile.unlink()

    print(f"\n✅ Cargados {total_ok}/{len(services)} servicios como {SNAPSHOT_VERSION}")


if __name__ == "__main__":
    main()
