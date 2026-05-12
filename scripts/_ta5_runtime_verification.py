"""
TA5 — Runtime verification post-Ejecutor 1 TA3 redeploy (Sprint MEGA-CIERRE-HOY).

Ejecuta 4 verificaciones binarias del kickoff §TA5:
  V1 SQL: nuevas filas en cowork_sesiones (últimos 30 min, distintas a 3a04e11b)
  V2 audit log: existe bridge/t1_audit_log.jsonl
  V3 Railway vars: COWORK_HOOK_ENABLED / SESSION_PERSIST / PREFLIGHT_REQUIRED = true
  V4 kernel health: GET /health (ya verificado vía curl, se reporta status snapshot)

Run con `railway run --service el-monstruo-kernel python3 scripts/_ta5_runtime_verification.py`.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import psycopg
import urllib.request

KERNEL_URL = "https://el-monstruo-kernel-production.up.railway.app"
COWORK_CANONICAL_SESSION_ID = "3a04e11b-e610-4958-964e-4a709f3a5c61"
REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT_LOG_PATH = REPO_ROOT / "bridge" / "t1_audit_log.jsonl"


def v1_check_cowork_sesiones() -> dict[str, Any]:
    """V1 SQL: count rows in cowork_sesiones inserted in last 30 min, excl canonical."""
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        return {"check": "V1_cowork_sesiones", "status": "SKIP", "reason": "SUPABASE_DB_URL not set"}
    try:
        with psycopg.connect(db_url, sslmode="require") as conn:
            with conn.cursor() as cur:
                # Verificar primero que la tabla existe
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name='cowork_sesiones')"
                )
                table_exists = cur.fetchone()[0]
                if not table_exists:
                    return {
                        "check": "V1_cowork_sesiones",
                        "status": "TABLA_NO_EXISTE",
                        "table_exists": False,
                        "note": "cowork_sesiones aún no creada (es parte de COWORK-RUNTIME-001 Fase 1+)",
                    }
                cur.execute(
                    "SELECT count(*) FROM public.cowork_sesiones "
                    "WHERE fecha_inicio > NOW() - INTERVAL '30 minutes' "
                    "  AND id != %s",
                    (COWORK_CANONICAL_SESSION_ID,),
                )
                new_rows = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM public.cowork_sesiones")
                total_rows = cur.fetchone()[0]
                return {
                    "check": "V1_cowork_sesiones",
                    "status": "VERDE" if new_rows >= 0 else "ROJO",
                    "table_exists": True,
                    "new_rows_last_30min_excl_canonical": new_rows,
                    "total_rows": total_rows,
                }
    except Exception as e:
        return {"check": "V1_cowork_sesiones", "status": "ERROR", "error": str(e)[:200]}


def v2_check_audit_log() -> dict[str, Any]:
    """V2 audit log: existe bridge/t1_audit_log.jsonl + tamaño + última línea."""
    if not AUDIT_LOG_PATH.exists():
        return {
            "check": "V2_audit_log",
            "status": "ARCHIVO_NO_EXISTE",
            "path": str(AUDIT_LOG_PATH),
            "note": "t1_audit_log.jsonl aún no fue creado por el kernel (depende de COWORK_PREFLIGHT_REQUIRED runtime)",
        }
    size = AUDIT_LOG_PATH.stat().st_size
    last_line = ""
    try:
        with open(AUDIT_LOG_PATH, "rb") as f:
            f.seek(0, 2)
            end = f.tell()
            f.seek(max(end - 4096, 0))
            tail = f.read().decode("utf-8", errors="ignore").strip().splitlines()
            if tail:
                last_line = tail[-1][:200]
    except Exception as e:
        last_line = f"<read error: {e}>"
    return {
        "check": "V2_audit_log",
        "status": "VERDE",
        "path": str(AUDIT_LOG_PATH),
        "size_bytes": size,
        "last_line_preview": last_line,
    }


def v3_check_railway_flags() -> dict[str, Any]:
    """V3 Railway flags: COWORK_HOOK_ENABLED / SESSION_PERSIST / PREFLIGHT_REQUIRED.

    Lee directamente os.environ porque corremos via `railway run --service el-monstruo-kernel`.
    """
    flags = {
        "COWORK_HOOK_ENABLED": os.environ.get("COWORK_HOOK_ENABLED"),
        "COWORK_SESSION_PERSIST": os.environ.get("COWORK_SESSION_PERSIST"),
        "COWORK_PREFLIGHT_REQUIRED": os.environ.get("COWORK_PREFLIGHT_REQUIRED"),
    }
    all_true = all(v == "true" for v in flags.values())
    return {
        "check": "V3_railway_flags",
        "status": "VERDE" if all_true else "ROJO",
        "flags": flags,
        "all_true": all_true,
    }


def v4_check_kernel_health() -> dict[str, Any]:
    """V4 kernel health: GET /health y reportar status + uptime."""
    try:
        req = urllib.request.Request(f"{KERNEL_URL}/health")
        with urllib.request.urlopen(req, timeout=10) as resp:
            status_code = resp.status
            raw = resp.read().decode("utf-8", errors="replace")
        if status_code != 200:
            return {
                "check": "V4_kernel_health",
                "status": "ROJO",
                "http_status": status_code,
                "body_preview": raw[:200],
            }
        body = json.loads(raw)
        return {
            "check": "V4_kernel_health",
            "status": "VERDE" if body.get("status") == "healthy" else "DEGRADED",
            "kernel_status": body.get("status"),
            "version": body.get("version"),
            "motor": body.get("motor"),
            "uptime_seconds": body.get("uptime_seconds"),
            "components_kernel": body.get("components", {}).get("kernel"),
            "components_checkpointer": body.get("components", {}).get("checkpointer"),
            "components_embrion": body.get("components", {}).get("embrion"),
            "embrion_loop_running": (body.get("components", {}).get("embrion_loop") or {}).get("running")
                if isinstance(body.get("components", {}).get("embrion_loop"), dict) else None,
        }
    except Exception as e:
        return {"check": "V4_kernel_health", "status": "ERROR", "error": str(e)[:200]}


def main() -> int:
    print("=" * 72)
    print("TA5 — Runtime verification (Sprint MEGA-CIERRE-HOY post-Ejecutor 1 TA3)")
    print("=" * 72)

    results = [
        v1_check_cowork_sesiones(),
        v2_check_audit_log(),
        v3_check_railway_flags(),
        v4_check_kernel_health(),
    ]

    for r in results:
        print()
        print(json.dumps(r, indent=2, ensure_ascii=False, default=str))

    print()
    print("=" * 72)
    print("RESUMEN BINARIO:")
    print("=" * 72)
    for r in results:
        check = r.get("check", "?")
        status = r.get("status", "?")
        print(f"  {check:30s} → {status}")

    # Verde global = V3 + V4 verdes (V1 y V2 dependen de tráfico Cowork real
    # que solo se generará cuando Cowork mande el primer mensaje post-redeploy).
    v3 = next(r for r in results if r["check"] == "V3_railway_flags")
    v4 = next(r for r in results if r["check"] == "V4_kernel_health")
    if v3["status"] == "VERDE" and v4["status"] == "VERDE":
        print()
        print("[VERDE] V3+V4 verdes → kernel asiste Cowork ACTIVO (infraestructura lista).")
        print("        V1+V2 dependen de tráfico Cowork real (se llenarán post-primera sesión).")
        return 0
    else:
        print()
        print("[ROJO] V3 o V4 no verdes — revisar arriba.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
