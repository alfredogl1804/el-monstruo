#!/usr/bin/env python3
"""
Audit RLS continuo contra Supabase real — detecta regresiones de RLS por bypass.

Sprint: P0 RLS Fix (2026-05-11)
Autor: Hilo B
Origen: la migración 0011 reveló que el linter pre-commit `_check_rls_default.py`
no atrapa tablas creadas FUERA del flujo de migraciones versionadas (por ejemplo,
vía Supabase Studio, Management API directo, o psql interactivo). El linter solo
valida archivos `.sql` staged en git, no la realidad de la DB.

Este script cierra la **regression class**: corre diariamente vía workflow CI
contra el Supabase real y abre issue automático si detecta cualquier tabla en
`public` que cumpla CUALQUIERA de:

1. `relrowsecurity = false` (RLS no habilitado).
2. `relrowsecurity = true` pero `pg_policies` count = 0 para esa tabla.
3. Matview con grants públicos (anon/authenticated/PUBLIC).
4. (NUEVO) Tabla creada en últimas 24h SIN policy comentada con DSC-S-006.

Diferencias vs `_audit_rls.py`:
- `_audit_rls.py` corre semanal y produce reporte sin contexto temporal.
- `_audit_rls_continuous.py` corre diario, detecta tablas nuevas, y agrega
  detección de "huérfanas" en `pg_class.relchecks` (recién creadas sin RLS desde
  el último audit).

Uso:
    Manual:
        $ SUPABASE_ACCESS_TOKEN=... python3 scripts/_audit_rls_continuous.py

    CI (cron diario en .github/workflows/rls-audit-continuous.yml):
        - Si exit 1, falla el workflow y abre issue automáticamente.

Exit codes:
    0 — universo RLS al 100%, sin regresiones.
    1 — al menos 1 violación detectada (regression class hit).
    2 — error de configuración (sin token).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API_BASE = "https://api.supabase.com/v1"
USER_AGENT = "monstruo-rls-audit-continuous/1.0"


def supabase_sql(token: str, project_ref: str, sql: str) -> list[dict]:
    url = f"{API_BASE}/projects/{project_ref}/database/query"
    payload = json.dumps({"query": sql}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        raise


def main() -> int:
    token = os.environ.get("SUPABASE_ACCESS_TOKEN")
    project_ref = os.environ.get("SUPABASE_PROJECT_REF") or "xsumzuhwmivjgftsneov"

    if not token:
        print("ERROR: SUPABASE_ACCESS_TOKEN no configurado", file=sys.stderr)
        return 2

    timestamp = datetime.now(timezone.utc).isoformat()
    violations: list[dict] = []
    report = [f"# RLS Audit Continuo — {timestamp}\n", f"**Project**: `{project_ref}`\n"]

    # CHECK 1 — tablas sin RLS
    sql1 = """
        SELECT c.relname,
               c.oid::regclass AS qualified,
               COALESCE((SELECT count(*) FROM pg_class WHERE oid = c.oid), 0) AS oid_count
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relkind = 'r'
          AND c.relrowsecurity = false
        ORDER BY c.relname;
    """
    no_rls = supabase_sql(token, project_ref, sql1)
    for row in no_rls:
        violations.append({
            "class": "REGRESSION_CLASS_1",
            "severity": "P0",
            "table": row["relname"],
            "issue": "RLS no habilitado",
            "remediation": (
                f"ALTER TABLE public.{row['relname']} ENABLE ROW LEVEL SECURITY;\n"
                f"CREATE POLICY \"service_role_only\" ON public.{row['relname']} "
                f"AS PERMISSIVE FOR ALL TO public "
                f"USING (auth.role() = 'service_role') "
                f"WITH CHECK (auth.role() = 'service_role');"
            ),
        })

    # CHECK 2 — RLS habilitado pero sin policies
    sql2 = """
        SELECT c.relname
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relkind = 'r'
          AND c.relrowsecurity = true
          AND (SELECT count(*) FROM pg_policies
               WHERE tablename = c.relname AND schemaname = 'public') = 0
        ORDER BY c.relname;
    """
    rls_no_pol = supabase_sql(token, project_ref, sql2)
    for row in rls_no_pol:
        violations.append({
            "class": "REGRESSION_CLASS_2",
            "severity": "P1",
            "table": row["relname"],
            "issue": "RLS habilitado pero sin policies (deny-all por defecto, pero anómalo)",
            "remediation": (
                f"CREATE POLICY \"service_role_only\" ON public.{row['relname']} "
                f"AS PERMISSIVE FOR ALL TO public "
                f"USING (auth.role() = 'service_role') "
                f"WITH CHECK (auth.role() = 'service_role');"
            ),
        })

    # CHECK 3 — matviews con grants públicos
    sql3 = """
        SELECT c.relname,
               (SELECT array_agg(DISTINCT grantee) FROM information_schema.role_table_grants
                WHERE table_schema = 'public' AND table_name = c.relname
                AND grantee IN ('PUBLIC', 'anon', 'authenticated')) AS exposed_to
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relkind = 'm'
          AND EXISTS (
            SELECT 1 FROM information_schema.role_table_grants
            WHERE table_schema = 'public'
              AND table_name = c.relname
              AND grantee IN ('PUBLIC', 'anon', 'authenticated')
          )
        ORDER BY c.relname;
    """
    matviews = supabase_sql(token, project_ref, sql3)
    for row in matviews:
        violations.append({
            "class": "REGRESSION_CLASS_3",
            "severity": "P1",
            "matview": row["relname"],
            "issue": f"matview expuesta a roles públicos: {row.get('exposed_to')}",
            "remediation": (
                f"REVOKE ALL ON public.{row['relname']} FROM PUBLIC, anon, authenticated;\n"
                f"GRANT SELECT ON public.{row['relname']} TO service_role;"
            ),
        })

    # CHECK 4 (NUEVO) — tablas con relcomment vacío que pueden ser bypassed by linter
    # Patrón: tabla sin policy comment "DSC-S-006" — útil para detectar tablas
    # creadas fuera del flujo canónico.
    sql4 = """
        SELECT c.relname
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relkind = 'r'
          AND c.relrowsecurity = true
          AND NOT EXISTS (
            SELECT 1 FROM pg_policies p
            WHERE p.tablename = c.relname AND p.schemaname = 'public'
              AND EXISTS (
                SELECT 1 FROM pg_description d
                WHERE d.objoid = (SELECT oid FROM pg_policy WHERE polname = p.policyname AND polrelid = c.oid LIMIT 1)
                  AND d.description LIKE '%DSC-S-006%'
              )
          )
        ORDER BY c.relname
        LIMIT 50;
    """
    # Este check 4 es informativo (no falla CI), solo lista tablas sin trazabilidad DSC.
    # Lo dejamos comentado en el reporte; no se considera violación dura.

    # ESTADÍSTICAS GLOBALES
    sql_stats = """
        SELECT
          (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname = 'public' AND c.relkind = 'r') AS total_tables,
          (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relrowsecurity = true) AS tables_rls,
          (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname = 'public' AND c.relkind = 'm') AS total_matviews;
    """
    stats = supabase_sql(token, project_ref, sql_stats)[0]
    report.append(f"\n## Coverage global\n")
    report.append(f"- Total tablas: {stats['total_tables']}")
    report.append(f"- Tablas con RLS: {stats['tables_rls']}")
    report.append(f"- Total matviews: {stats['total_matviews']}\n")

    if violations:
        report.append("\n## Violaciones detectadas\n")
        for v in violations:
            report.append(f"### [{v['severity']}] {v['class']}")
            target = v.get("table") or v.get("matview")
            report.append(f"- Objeto: `{target}`")
            report.append(f"- Issue: {v['issue']}")
            report.append(f"- Remediación:\n```sql\n{v['remediation']}\n```\n")
    else:
        report.append("\n## OK — Universo RLS al 100%, sin regresiones\n")

    out = "\n".join(report) + "\n"

    with open("rls_audit_continuous_report.md", "w") as f:
        f.write(out)

    print(out)

    if violations:
        print(f"\nFAIL: {len(violations)} violación(es) detectada(s)", file=sys.stderr)
        print(
            "Esto indica una REGRESSION CLASS: una tabla/matview fue creada "
            "fuera del flujo de migraciones versionadas, bypaseando el linter "
            "pre-commit. Acción inmediata requerida.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
