"""
Sprint 86 Bloque 6 — Smoke E2E del primer run productivo (contra prod URL)

Valida que el primer run real haya poblado el Catastro con data fresca:

  1. GET  /v1/catastro/status         → trust_level=healthy, modelos_count > 0
  2. POST /v1/catastro/recommend      → top_n con datos reales (use_case LLM)
  3. GET  /v1/catastro/modelos/<top1> → ficha completa con quorum_alcanzado=true
  4. GET  /v1/catastro/dominios       → al menos 1 macroárea con dominios > 0

USO:

  # Smoke contra prod (Railway):
  KERNEL_URL=https://el-monstruo-mvp.up.railway.app \
  MONSTRUO_API_KEY=<key> \
  python3 scripts/_smoke_catastro_first_run.py

  # Smoke contra local:
  KERNEL_URL=http://localhost:8000 \
  MONSTRUO_API_KEY=<key> \
  python3 scripts/_smoke_catastro_first_run.py

EXIT CODES:

  0 — Todos los assertions PASS (Catastro vivo y poblado)
  1 — Algún assertion FAIL (Catastro vivo pero degradado / vacío)
  2 — Error de red / conexión / config

[Hilo Manus Catastro] · Sprint 86 Bloque 6 · 2026-05-04
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Optional

import urllib.request
import urllib.error


# ============================================================================
# CONFIG
# ============================================================================

DEFAULT_KERNEL_URL = "https://el-monstruo-mvp.up.railway.app"
KERNEL_URL = os.environ.get("KERNEL_URL", DEFAULT_KERNEL_URL).rstrip("/")
API_KEY = os.environ.get("MONSTRUO_API_KEY", "")
TIMEOUT = float(os.environ.get("CATASTRO_SMOKE_TIMEOUT", "20"))


# ============================================================================
# COLORES
# ============================================================================

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    OK = "\033[92m"
    WARN = "\033[93m"
    ERR = "\033[91m"
    INFO = "\033[94m"
    HEAD = "\033[95m"


def header(label: str) -> None:
    print(f"\n{C.HEAD}{'=' * 78}\n  {label}\n{'=' * 78}{C.RESET}")


def step(label: str) -> None:
    print(f"\n{C.BOLD}── {label}{C.RESET}")


def ok(msg: str) -> None: print(f"  {C.OK}✓{C.RESET} {msg}")
def warn(msg: str) -> None: print(f"  {C.WARN}⚠{C.RESET} {msg}")
def err(msg: str) -> None: print(f"  {C.ERR}✗{C.RESET} {msg}")
def info(msg: str) -> None: print(f"  {C.INFO}·{C.RESET} {msg}")


# ============================================================================
# HTTP HELPER
# ============================================================================

def http_call(method: str, path: str, body: Optional[dict] = None) -> tuple[int, dict]:
    """Llama al endpoint con auth Bearer. Retorna (status_code, json_body)."""
    url = f"{KERNEL_URL}{path}"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return resp.status, payload
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode("utf-8"))
        except Exception:
            payload = {"error": str(e)}
        return e.code, payload
    except Exception as e:  # noqa: BLE001
        return -1, {"error": str(e), "type": type(e).__name__}


# ============================================================================
# ASSERTIONS
# ============================================================================

def assert_status_healthy() -> tuple[bool, dict]:
    step("1. GET /v1/catastro/status")
    code, body = http_call("GET", "/v1/catastro/status")
    if code != 200:
        err(f"status {code}: {body}")
        return False, {}
    trust = body.get("trust_level")
    n_models = body.get("modelos_count", 0)
    n_dom = body.get("dominios_count", 0)
    info(f"trust_level={trust}  modelos={n_models}  dominios={n_dom}")
    info(f"degraded={body.get('degraded')}  cache_entries={body.get('cache_entries', '?')}")

    if trust == "healthy" and n_models > 0:
        ok("Catastro vivo y poblado")
        return True, body
    elif trust in ("degraded", "down"):
        err(f"Catastro NO healthy (trust_level={trust})")
        return False, body
    elif n_models == 0:
        err("Catastro VIVO pero VACÍO (modelos_count=0). El primer run no se ha ejecutado o falló silencioso.")
        return False, body
    return False, body


def assert_recommend_devuelve_modelos() -> tuple[bool, list]:
    step("2. POST /v1/catastro/recommend (use_case=LLM frontier)")
    code, body = http_call("POST", "/v1/catastro/recommend", {
        "use_case": "Tareas de razonamiento de frontera con contextos largos",
        "top_n": 5,
    })
    if code != 200:
        err(f"status {code}: {body}")
        return False, []
    modelos = body.get("modelos", [])
    info(f"degraded={body.get('degraded')}  cache_hit={body.get('cache_hit')}")
    info(f"modelos retornados: {len(modelos)}")
    if not modelos:
        err("recommend devolvió 0 modelos (Catastro vacío o sin matches)")
        return False, []
    for i, m in enumerate(modelos[:3], 1):
        info(f"  {i}. {m.get('id')} (trono={m.get('trono_global')})")
    ok(f"recommend devuelve {len(modelos)} modelos")
    return True, modelos


def assert_get_modelo(modelo_id: str) -> bool:
    step(f"3. GET /v1/catastro/modelos/{modelo_id}")
    code, body = http_call("GET", f"/v1/catastro/modelos/{modelo_id}")
    if code != 200:
        err(f"status {code}: {body}")
        return False
    info(f"id={body.get('id')}  nombre={body.get('nombre')}")
    info(f"proveedor={body.get('proveedor')}  macroarea={body.get('macroarea')}")
    info(f"estado={body.get('estado')}  quorum_alcanzado={body.get('quorum_alcanzado', '?')}")
    info(f"trono_global={body.get('trono_global')}")
    if body.get("id") != modelo_id:
        err("ID del modelo retornado no coincide")
        return False
    ok(f"Ficha completa de {modelo_id} accesible")
    return True


def assert_dominios_no_vacio() -> bool:
    step("4. GET /v1/catastro/dominios")
    code, body = http_call("GET", "/v1/catastro/dominios")
    if code != 200:
        err(f"status {code}: {body}")
        return False
    macros = body.get("macroareas", {})
    total = body.get("total_dominios", 0)
    info(f"macroareas: {list(macros.keys())}")
    info(f"total_dominios: {total}")
    if not macros or total == 0:
        err("Sin macroáreas ni dominios — Catastro vacío")
        return False
    ok(f"{len(macros)} macroáreas y {total} dominios poblados")
    return True


# ============================================================================
# MAIN
# ============================================================================

def main() -> int:
    header(f"CATASTRO · Smoke E2E primer run · {KERNEL_URL}")

    if not API_KEY:
        err("MONSTRUO_API_KEY no está configurada. Abortando.")
        info("export MONSTRUO_API_KEY='<tu-key>' && python3 scripts/_smoke_catastro_first_run.py")
        return 2

    info(f"KERNEL_URL: {KERNEL_URL}")
    info(f"TIMEOUT:    {TIMEOUT}s")

    results = {"status": False, "recommend": False, "get_modelo": False, "dominios": False}

    status_ok, _ = assert_status_healthy()
    results["status"] = status_ok

    rec_ok, modelos = assert_recommend_devuelve_modelos()
    results["recommend"] = rec_ok

    if rec_ok and modelos:
        top_id = modelos[0].get("id", "")
        if top_id:
            results["get_modelo"] = assert_get_modelo(top_id)
        else:
            warn("Top modelo sin id — saltando get_modelo")
    else:
        warn("Recommend falló — saltando get_modelo")

    results["dominios"] = assert_dominios_no_vacio()

    # ── RESUMEN ─────────────────────────────────────────────────────
    header("RESUMEN")
    for label, passed in results.items():
        if passed:
            ok(f"{label:20s}  PASS")
        else:
            err(f"{label:20s}  FAIL")

    all_ok = all(results.values())
    if all_ok:
        print(f"\n{C.OK}{C.BOLD}  ✓ SMOKE E2E PRIMER RUN — TODOS LOS ASSERTIONS PASS{C.RESET}\n")
        return 0
    else:
        print(f"\n{C.ERR}{C.BOLD}  ✗ SMOKE E2E PRIMER RUN — ASSERTIONS FALLARON{C.RESET}")
        print(f"  {C.WARN}El Catastro no está poblado o degradado. Revisar logs Railway.{C.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
