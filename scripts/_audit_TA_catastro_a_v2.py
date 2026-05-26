"""TA — Audit binario read-only de las 3 vistas DSC-G-007.1 + 1 tabla suppliers.

Sprint CATASTRO-A v2 (post-S89 v2 Opción B).
Ejecutar via: `railway run python3 scripts/_audit_TA_catastro_a_v2.py`
"""

from __future__ import annotations

import json
import os
import sys

import psycopg2

CATASTROS = [
    ("catastro_modelos_llm", "vista", 41, ["key", "name", "provider", "max_tokens", "cost_per_1k_input", "active"]),
    (
        "catastro_agentes_2026",
        "vista",
        98,
        ["key", "name", "version", "owner_org", "biblia_path", "capability_tags", "active"],
    ),
    ("catastro_herramientas_ai", "vista", 58, ["key", "name", "category", "auth_type", "cost_per_call", "active"]),
    ("catastro_suppliers_humanos", "tabla", 0, ["key", "name", "role", "skills", "contact", "active", "last_active"]),
]


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL / DATABASE_URL no presentes en env", file=sys.stderr)
        return 1

    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    cur = conn.cursor()

    results = {}
    fail = False

    for name, kind, expected_min, expected_cols in CATASTROS:
        item = {"kind": kind, "expected_min_rows": expected_min}

        try:
            cur.execute(f"SELECT count(*), MIN(name), MAX(name) FROM public.{name}")
            cnt, min_name, max_name = cur.fetchone()
            item["count"] = cnt
            item["min_name"] = min_name
            item["max_name"] = max_name
        except Exception as exc:
            item["count_error"] = str(exc)
            fail = True
            results[name] = item
            continue

        try:
            cur.execute(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema='public' AND table_name=%s
                ORDER BY ordinal_position
                """,
                (name,),
            )
            actual_cols = [r[0] for r in cur.fetchall()]
            item["actual_columns"] = actual_cols
            missing = [c for c in expected_cols if c not in actual_cols]
            item["missing_expected_cols"] = missing
            if missing:
                item["WARN"] = f"columns esperadas faltantes: {missing}"
        except Exception as exc:
            item["cols_error"] = str(exc)
            fail = True

        if name == "catastro_suppliers_humanos":
            try:
                cur.execute(
                    """
                    SELECT relrowsecurity, relforcerowsecurity
                    FROM pg_class WHERE relname=%s
                """,
                    (name,),
                )
                rls, force = cur.fetchone()
                item["rls_enabled"] = rls
                item["rls_forced"] = force
                cur.execute(
                    """
                    SELECT polname FROM pg_policy
                    JOIN pg_class ON pg_class.oid = pg_policy.polrelid
                    WHERE relname=%s
                """,
                    (name,),
                )
                item["policies"] = [r[0] for r in cur.fetchall()]
            except Exception as exc:
                item["rls_error"] = str(exc)
                fail = True
        else:
            try:
                cur.execute(
                    """
                    SELECT array_agg(DISTINCT a.privilege_type)
                    FROM information_schema.role_table_grants a
                    WHERE a.table_schema='public' AND a.table_name=%s
                """,
                    (name,),
                )
                grants = cur.fetchone()
                item["grants"] = grants[0] if grants else None
            except Exception as exc:
                item["grants_error"] = str(exc)

        if isinstance(item.get("count"), int) and expected_min > 0 and item["count"] < expected_min:
            item["FAIL"] = f"count={item['count']} < expected_min={expected_min}"
            fail = True

        results[name] = item

    print(json.dumps(results, indent=2, default=str, ensure_ascii=False))
    print()
    print("=" * 60)
    print("AUDIT", "VERDE" if not fail else "ROJO")
    print("=" * 60)

    cur.close()
    conn.close()
    return 0 if not fail else 2


if __name__ == "__main__":
    sys.exit(main())
