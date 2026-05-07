#!/usr/bin/env python3
"""
Audit Supabase memory tables del kernel por leakage de tokens GitHub.
Sprint 85 — Pre-rotación de tokens. Ejecutar UNA vez.
"""
import psycopg2
import re
import sys

DSN = "postgresql://postgres.xsumzuhwmivjgftsneov:0SsKDCchJpN5GhO3@aws-1-us-east-2.pooler.supabase.com:5432/postgres?sslmode=require"

# Patrones de tokens GitHub
TOKEN_PATTERN = r"(ghp_|github_pat_|gho_|ghs_|ghu_)[A-Za-z0-9_]{20,}"

# Tablas y columnas a auditar
SCAN_TARGETS = [
    ("thoughts", "content"),
    ("episodic", "content"),
    ("task_plans", "prompt"),
    ("task_plans", "result::text"),
    ("verification_results", "verdict::text"),
    ("tool_registry", "metadata::text"),
    ("error_memory", "sanitized_message"),
    ("error_memory", "resolution"),
    ("active_orchestration", "context::text"),
    ("active_orchestration", "result::text"),
]

print("=" * 70)
print("AUDIT SUPABASE — leakage de tokens GitHub (Sprint 85 pre-rotación)")
print("=" * 70)

try:
    conn = psycopg2.connect(DSN)
    conn.autocommit = True
    cur = conn.cursor()

    # Listar tablas reales en public
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
    tables = [r[0] for r in cur.fetchall()]
    print(f"\nTablas en schema public: {len(tables)}")
    for t in tables:
        print(f"  - {t}")

    print("\n" + "=" * 70)
    print("ESCANEANDO LEAKAGE...")
    print("=" * 70)

    total_leaks = 0
    for table, column in SCAN_TARGETS:
        if table not in tables:
            print(f"  [SKIP] {table}.{column} — tabla no existe")
            continue
        try:
            # Limpiar nombre de columna para query
            col_clean = column.split("::")[0]
            query = f"""
                SELECT count(*) FROM {table}
                WHERE {column} ~* %s
            """
            cur.execute(query, (TOKEN_PATTERN,))
            count = cur.fetchone()[0]
            status = "OK" if count == 0 else "LEAK"
            print(f"  [{status}] {table}.{column}: {count} rows")
            total_leaks += count
            if count > 0:
                # Mostrar las 3 primeras filas
                detail_query = f"""
                    SELECT id, created_at, LEFT({column}, 200) AS preview
                    FROM {table}
                    WHERE {column} ~* %s
                    ORDER BY created_at DESC
                    LIMIT 3
                """
                cur.execute(detail_query, (TOKEN_PATTERN,))
                for row in cur.fetchall():
                    print(f"    → id={row[0]} created={row[1]}")
                    print(f"      preview: {row[2][:150]}...")
        except Exception as e:
            print(f"  [ERR] {table}.{column}: {e}")

    print("\n" + "=" * 70)
    print(f"TOTAL LEAKS ENCONTRADOS: {total_leaks}")
    print("=" * 70)

    if total_leaks == 0:
        print("\n✓ SAFE — Ninguna fila contiene tokens GitHub.")
        print("  Procede con rotación.")
    else:
        print(f"\n⚠ DEUDA — {total_leaks} filas contienen tokens.")
        print("  ANTES de rotar: redactar/borrar las filas con UPDATE/DELETE.")
        print("  Tras rotar: los tokens viejos quedan inertes pero recordar limpiar.")

    cur.close()
    conn.close()
except Exception as e:
    print(f"\nERROR FATAL: {e}")
    sys.exit(1)
