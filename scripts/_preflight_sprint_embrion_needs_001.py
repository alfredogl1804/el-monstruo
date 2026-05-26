#!/usr/bin/env python3
"""
Pre-flight Sprint EMBRION-NEEDS-001
Ejecuta los 5 pasos del handoff cowork_to_manus_SPRINT_EMBRION_NEEDS_001_2026_05_10.md

Pasos:
  1. Validar 2 mensaje_alfredo via cowork_bridge del 10 mayo
  2. Validar respuesta del embrion (cycle 76, "Recibido" + "0.25")
  3. Snapshot de estado actual (count por tipo + costo histórico 14d)
  4. Validar acceso a GitHub (gh auth status)
  5. Confirmar canal HITL (Cowork bridge mientras Tarea 4 no exista)

Salidas:
  - bridge/snapshot_pre_sprint_embrion_needs_001_2026_05_10.md (paso 3)
  - reports/_preflight_sprint_embrion_needs_001.json (telemetría completa)
  - stdout: VEREDICTO GO/NO-GO
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUPA_URL = "https://xsumzuhwmivjgftsneov.supabase.co"
PROJECT_REF = "xsumzuhwmivjgftsneov"

SUPA_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
if not SUPA_KEY:
    print("FATAL: env var SUPABASE_SERVICE_KEY no esta seteada.")
    print("       Exportala antes de correr este script.")
    sys.exit(99)

HEADERS = {
    "apikey": SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
    "Content-Type": "application/json",
    "Prefer": "count=exact",
}

# -------- helpers --------------------------------------------------------------


def supa_rest(path, params=None, prefer=None):
    """GET a la REST API de Supabase. Devuelve (status, body_json)."""
    url = f"{SUPA_URL}/rest/v1/{path}"
    h = dict(HEADERS)
    if prefer:
        h["Prefer"] = prefer
    r = requests.get(url, headers=h, params=params or {}, timeout=20)
    try:
        body = r.json()
    except Exception:
        body = r.text
    return r.status_code, body, r.headers


def supa_rpc_sql(sql_text):
    """
    Supabase no expone /rest/v1/rpc/_sql arbitrario sin función previa.
    Usamos el endpoint POST /rest/v1/rpc/<fn> SI existe; si no, devolvemos error
    pidiendo el MCP. Esto es para queries agregadas que no se pueden expresar
    como filtro PostgREST simple.

    Returns (ok: bool, result, info)
    """
    return False, None, "rpc_sql_no_disponible_usar_mcp_o_filtro_postgrest"


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# -------- paso 1: validar 2 mensaje_alfredo via cowork_bridge -----------------


def paso_1():
    section("PASO 1 — Validar 2 mensaje_alfredo via cowork_bridge del 10 mayo")
    params = {
        "select": "id,created_at,hilo_origen,importancia",
        "tipo": "eq.mensaje_alfredo",
        "hilo_origen": "eq.cowork_bridge",
        "created_at": "gt.2026-05-10T00:00:00+00:00",
        "order": "created_at.asc",
    }
    code, body, _ = supa_rest("embrion_memoria", params=params)
    rows = body if isinstance(body, list) else []

    print(f"  HTTP={code}")
    print(f"  Filas encontradas: {len(rows)}")
    for r in rows:
        print(f"    - id={r.get('id')[:8]}... created={r.get('created_at')} importancia={r.get('importancia')}")

    expected_ids = {
        "a02242b0-6d67-4c68-a189-c6ffcc696fb1",
        "7d620b24-d198-4749-a97c-1833f6747666",
    }
    found_ids = {r.get("id") for r in rows}
    matched = expected_ids.intersection(found_ids)

    ok = code == 200 and len(rows) >= 2 and len(matched) == 2
    print(f"  IDs esperados encontrados: {len(matched)}/2")
    print(f"  >>> RESULTADO: {'PASS' if ok else 'FAIL'}")
    return {
        "paso": 1,
        "titulo": "Validar 2 mensaje_alfredo via cowork_bridge",
        "ok": ok,
        "rows_found": len(rows),
        "expected_ids_matched": len(matched),
        "rows": rows,
    }


# -------- paso 2: validar respuesta del embrion --------------------------------


def paso_2():
    section("PASO 2 — Validar respuesta del embrion (Recibido + 0.25)")
    params = {
        "select": "id,created_at,contenido,contexto",
        "tipo": "eq.respuesta_embrion",
        "created_at": "gt.2026-05-10T02:03:43+00:00",
        "contenido": "ilike.*Recibido*",
        "order": "created_at.asc",
        "limit": "5",
    }
    code, body, _ = supa_rest("embrion_memoria", params=params)
    rows = body if isinstance(body, list) else []

    # filtrar tambien que contenga "0.25"
    matching = [r for r in rows if "0.25" in (r.get("contenido") or "")]

    print(f"  HTTP={code}")
    print(f"  Filas con 'Recibido': {len(rows)}")
    print(f"  Filas con 'Recibido' + '0.25': {len(matching)}")
    for r in matching[:3]:
        cont = (r.get("contenido") or "")[:120].replace("\n", " ")
        print(f"    - id={r.get('id')[:8]}... created={r.get('created_at')}")
        print(f"      contenido='{cont}...'")

    ok = code == 200 and len(matching) >= 1
    print(f"  >>> RESULTADO: {'PASS' if ok else 'FAIL'}")
    return {
        "paso": 2,
        "titulo": "Respuesta del embrion (cycle 76, Recibido + 0.25)",
        "ok": ok,
        "rows_recibido": len(rows),
        "rows_recibido_y_025": len(matching),
        "first_match": matching[0] if matching else None,
    }


# -------- paso 3: snapshot del estado -----------------------------------------


def paso_3():
    section("PASO 3 — Snapshot estado actual (count por tipo + costo 14d)")
    # 3a) count por tipo: pedimos all rows con select=tipo y agregamos en Python
    #     (más caro pero sin RPC)
    params = {"select": "tipo"}
    code, body, hdrs = supa_rest("embrion_memoria", params=params, prefer="count=exact")
    total = int(hdrs.get("Content-Range", "0/0").split("/")[-1] or 0)
    rows = body if isinstance(body, list) else []

    counts = {}
    for r in rows:
        t = r.get("tipo") or "<null>"
        counts[t] = counts.get(t, 0) + 1
    counts_sorted = sorted(counts.items(), key=lambda x: -x[1])

    print(f"  Total filas embrion_memoria: {total} (count={len(rows)})")
    print("  Distribución por tipo:")
    for t, c in counts_sorted:
        print(f"    {t:30s} {c:6d}")

    # 3b) Para el costo histórico, intentamos vía MCP/filtro: pedimos las
    #     ultimas 14 dias de respuesta_embrion con contexto.
    params2 = {
        "select": "created_at,contexto",
        "tipo": "eq.respuesta_embrion",
        "created_at": "gt.2026-04-26T00:00:00+00:00",
        "order": "created_at.asc",
    }
    code2, body2, _ = supa_rest("embrion_memoria", params=params2)
    resps = body2 if isinstance(body2, list) else []

    # Agrupar por dia y sumar cost_usd
    from collections import defaultdict

    cost_by_day = defaultdict(lambda: {"respuestas": 0, "costo_usd": 0.0})
    for r in resps:
        created = r.get("created_at", "")[:10]
        ctx = r.get("contexto") or {}
        if isinstance(ctx, str):
            try:
                ctx = json.loads(ctx)
            except Exception:
                ctx = {}
        cost_by_day[created]["respuestas"] += 1
        try:
            cost_by_day[created]["costo_usd"] += float(ctx.get("cost_usd") or 0)
        except Exception:
            pass

    print()
    print("  Respuestas embrion últimos 14 días:")
    print(f"    {'fecha':12s} {'resps':>8s} {'costo_usd':>12s}")
    for day in sorted(cost_by_day.keys(), reverse=True):
        d = cost_by_day[day]
        print(f"    {day:12s} {d['respuestas']:>8d} {d['costo_usd']:>12.4f}")

    # Escribir el snapshot a bridge/
    snapshot_path = os.path.join(REPO_ROOT, "bridge", "snapshot_pre_sprint_embrion_needs_001_2026_05_10.md")
    lines = [
        "# Snapshot pre-Sprint EMBRION-NEEDS-001",
        "",
        f"**Generado:** {datetime.now(timezone.utc).isoformat()}",
        "**Por:** Manus pre-flight script",
        "**Sprint:** EMBRION-NEEDS-001",
        "",
        "## Distribución por tipo en `embrion_memoria`",
        "",
        f"Total filas: **{total}**",
        "",
        "| Tipo | Cantidad |",
        "|---|---:|",
    ]
    for t, c in counts_sorted:
        lines.append(f"| `{t}` | {c} |")
    lines.append("")
    lines.append("## Respuestas del embrión por día (últimos 14 días)")
    lines.append("")
    lines.append("| Fecha | Respuestas | Costo USD |")
    lines.append("|---|---:|---:|")
    total_resp = 0
    total_cost = 0.0
    for day in sorted(cost_by_day.keys(), reverse=True):
        d = cost_by_day[day]
        total_resp += d["respuestas"]
        total_cost += d["costo_usd"]
        lines.append(f"| {day} | {d['respuestas']} | {d['costo_usd']:.4f} |")
    lines.append(f"| **TOTAL** | **{total_resp}** | **{total_cost:.4f}** |")
    lines.append("")
    lines.append("## Notas")
    lines.append("")
    lines.append("- Este snapshot es la baseline para validar Tarea 1 (Budget Tracker).")
    lines.append("- Costo USD calculado sumando `contexto.cost_usd` de respuestas tipo `respuesta_embrion`.")
    lines.append("- Si una respuesta no tiene `cost_usd` en su contexto, suma 0.")
    lines.append("")

    os.makedirs(os.path.dirname(snapshot_path), exist_ok=True)
    with open(snapshot_path, "w") as f:
        f.write("\n".join(lines))

    print()
    print(f"  Snapshot escrito en: {snapshot_path}")
    print("  >>> RESULTADO: PASS")

    return {
        "paso": 3,
        "titulo": "Snapshot estado actual",
        "ok": True,
        "total_rows": total,
        "counts_by_tipo": dict(counts_sorted),
        "cost_by_day": {k: dict(v) for k, v in cost_by_day.items()},
        "snapshot_path": snapshot_path,
    }


# -------- paso 4: validar acceso GitHub ---------------------------------------


def paso_4():
    section("PASO 4 — Validar acceso GitHub")
    try:
        out = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        print(out.stdout or "")
        print(out.stderr or "")
        ok_auth = out.returncode == 0
    except Exception as e:
        print(f"  ERROR: {e}")
        ok_auth = False

    # Verificar si tengo permisos sobre el repo del sprint
    # Nota: gh repo view --json devuelve JSON puro a stdout. Usamos
    # subprocess.check_output para forzar separacion correcta.
    data = {}
    ok_repo = False
    try:
        env = dict(os.environ)
        env["NO_COLOR"] = "1"
        env["CLICOLOR"] = "0"
        out2 = subprocess.run(
            ["gh", "repo", "view", "alfredogl1804/el-monstruo", "--json", "name,viewerPermission,defaultBranchRef"],
            capture_output=True,
            text=True,
            timeout=15,
            env=env,
        )
        raw = (out2.stdout or "").strip()
        # Strip ANSI escape codes (gh los emite incluso con NO_COLOR en Macs)
        raw = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", raw)
        print("  raw stdout (clean):", raw[:200])
        if out2.returncode == 0 and raw:
            try:
                data = json.loads(raw)
                perm = data.get("viewerPermission")
                ok_repo = perm in ("ADMIN", "MAINTAIN", "WRITE")
            except json.JSONDecodeError as je:
                print(f"  WARN: JSON parse failed: {je}. raw[:80]={raw[:80]!r}")
        else:
            print("  stderr:", out2.stderr[:300] if out2.stderr else "")
    except Exception as e:
        print(f"  ERROR: {e}")

    ok = ok_auth and ok_repo
    print(
        f"  Auth OK: {ok_auth} | Permisos repo: {data.get('viewerPermission', '?')} | Branch protegido: {data.get('defaultBranchRef', {}).get('branchProtectionRule') is not None}"
    )
    print(f"  >>> RESULTADO: {'PASS' if ok else 'FAIL'}")
    return {
        "paso": 4,
        "titulo": "Acceso GitHub a alfredogl1804/el-monstruo",
        "ok": ok,
        "auth_ok": ok_auth,
        "repo_data": data,
    }


# -------- paso 5: confirmar canal HITL ----------------------------------------


def paso_5():
    section("PASO 5 — Confirmar canal HITL (Cowork bridge temporal)")
    print("  Tarea 4 (bot Telegram) NO esta completa todavia.")
    print("  Por lo tanto, mientras dure el sprint, el canal HITL es:")
    print("    1. INSERT en embrion_memoria con tipo='pensamiento',")
    print("       hilo_origen='manus_executor', importancia=10,")
    print("       contexto.requires_alfredo_approval=true")
    print("    2. Avisar a Alfredo por chat directo de Manus")
    print()
    print("  Esto es protocolo declarado en el handoff (lineas 98-104).")
    print("  No requiere validacion runtime — es un protocolo de comunicacion.")
    print("  >>> RESULTADO: PASS (acordado)")
    return {
        "paso": 5,
        "titulo": "Canal HITL confirmado: Cowork bridge + chat Manus",
        "ok": True,
        "policy": "embrion_memoria insert + chat directo Manus mientras Tarea 4 pendiente",
    }


# -------- main ----------------------------------------------------------------


def main():
    started = datetime.now(timezone.utc).isoformat()
    print("Pre-flight Sprint EMBRION-NEEDS-001")
    print(f"Inicio: {started}")
    print(f"Project ref: {PROJECT_REF}")

    results = []
    for fn in (paso_1, paso_2, paso_3, paso_4, paso_5):
        try:
            results.append(fn())
        except Exception as e:
            results.append(
                {
                    "paso": "?",
                    "ok": False,
                    "error": f"{type(e).__name__}: {e}",
                }
            )

    # Veredicto final
    section("VEREDICTO FINAL")
    fails = [r for r in results if not r.get("ok")]
    print(f"  Pasos PASS: {len(results) - len(fails)}/{len(results)}")
    if fails:
        print(f"  Pasos FAIL: {len(fails)}")
        for r in fails:
            print(f"    - paso {r.get('paso')}: {r.get('titulo', '?')}")
        print()
        print("  >>> NO-GO. Escalá a Alfredo antes de arrancar Tarea 1.")
        verdict = "NO-GO"
    else:
        print()
        print("  >>> GO. Listo para arrancar Tarea 1 (Budget Tracker).")
        verdict = "GO"

    # Persistir telemetría
    out_dir = os.path.join(REPO_ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "_preflight_sprint_embrion_needs_001.json")
    with open(out_path, "w") as f:
        json.dump(
            {
                "started_at": started,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "verdict": verdict,
                "results": results,
            },
            f,
            indent=2,
            default=str,
        )
    print(f"  Telemetría completa: {out_path}")

    sys.exit(0 if verdict == "GO" else 2)


if __name__ == "__main__":
    main()
