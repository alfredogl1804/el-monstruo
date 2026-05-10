#!/usr/bin/env python3
"""
Auditoría RLS del schema public en Supabase.

Sprint S-002.6 — Tarea 6
Autor: Hilo B
Fecha: 2026-05-10

Ejecuta SQL contra Supabase Management API y valida:
1. Toda tabla (relkind='r') en public DEBE tener relrowsecurity=true.
2. Toda tabla con RLS DEBE tener al menos 1 policy.
3. Toda matview (relkind='m') en public DEBE tener REVOKE para PUBLIC/anon/authenticated.

Genera `rls_audit_report.md` con resumen.
Exit code:
    0 — todo verde
    1 — violación detectada (workflow falla y abre issue)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

API_BASE = "https://api.supabase.com/v1"
USER_AGENT = "monstruo-rls-audit/1.0"


def supabase_sql(token: str, project_ref: str, sql: str) -> list[dict]:
    """Ejecuta SQL via Supabase Management API."""
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
    # SUPABASE_PROJECT_REF no es secreto (es identificador público del proyecto Supabase).
    # El default permite ejecución local sin env var. DSC-S-004 no aplica porque no es credencial.
    project_ref = os.environ.get("SUPABASE_PROJECT_REF") or "xsumzuhwmivjgftsneov"

    if not token:
        print("ERROR: SUPABASE_ACCESS_TOKEN no configurado", file=sys.stderr)
        return 1

    violations: list[str] = []
    report_lines: list[str] = []

    # 1. Tablas sin RLS
    sql1 = """
        SELECT c.relname
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relkind = 'r'
          AND c.relrowsecurity = false
        ORDER BY c.relname;
    """
    no_rls = supabase_sql(token, project_ref, sql1)

    # 2. Tablas con RLS pero sin policies
    sql2 = """
        SELECT c.relname
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relkind = 'r'
          AND c.relrowsecurity = true
          AND (SELECT count(*) FROM pg_policies WHERE tablename = c.relname AND schemaname = 'public') = 0
        ORDER BY c.relname;
    """
    rls_no_policy = supabase_sql(token, project_ref, sql2)

    # 3. Matviews con grants públicos
    sql3 = """
        SELECT c.relname
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
    matviews_unsafe = supabase_sql(token, project_ref, sql3)

    # 4. Estadísticas globales
    sql4 = """
        SELECT
          (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname = 'public' AND c.relkind = 'r') AS total_tables,
          (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relrowsecurity = true) AS tables_rls,
          (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname = 'public' AND c.relkind = 'm') AS total_matviews;
    """
    stats = supabase_sql(token, project_ref, sql4)[0]

    # Construir reporte
    report_lines.append(f"# RLS Audit Report — schema public\n")
    report_lines.append(f"**Project**: `{project_ref}`")
    report_lines.append(f"**Total tablas**: {stats['total_tables']}")
    report_lines.append(f"**Tablas con RLS**: {stats['tables_rls']}")
    report_lines.append(f"**Total matviews**: {stats['total_matviews']}\n")

    if no_rls:
        violations.append(f"{len(no_rls)} tabla(s) sin RLS")
        report_lines.append("## Violación 1: tablas sin RLS\n")
        for r in no_rls:
            report_lines.append(f"- `{r['relname']}`")
        report_lines.append("")

    if rls_no_policy:
        violations.append(f"{len(rls_no_policy)} tabla(s) con RLS pero sin policy")
        report_lines.append("## Violación 2: RLS habilitado sin policies\n")
        for r in rls_no_policy:
            report_lines.append(f"- `{r['relname']}`")
        report_lines.append("")

    if matviews_unsafe:
        violations.append(f"{len(matviews_unsafe)} matview(s) con grants públicos")
        report_lines.append("## Violación 3: matviews con grants públicos\n")
        for r in matviews_unsafe:
            report_lines.append(f"- `{r['relname']}`")
        report_lines.append("")

    if not violations:
        report_lines.append("## ✅ Universo RLS al 100%\n")
        report_lines.append("No hay tablas sin RLS, ni RLS huérfano, ni matviews sin protección.")
    else:
        report_lines.append("## ❌ Violaciones detectadas\n")
        for v in violations:
            report_lines.append(f"- {v}")

    report = "\n".join(report_lines) + "\n"
    with open("rls_audit_report.md", "w") as f:
        f.write(report)

    print(report)

    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
