"""
Genome Now Routes — Sprint 91 F5 (Mapa Vivo 100% del Monstruo) + Sprint 91.7
============================================================================

Router FastAPI que expone el endpoint GET /v1/genome/now.

Este endpoint sirve el JSON canónico del estado vivo del Monstruo agregado
por scripts/genome_live/aggregator.py a partir de los outputs de F1-F4
(github.json, railway.json, supabase.json, live24h.json).

Estrategia de v1.0 (Sprint 91 base):
  - Sirve el JSON desde disco (`_genome_out/genome_now.json`).
  - Si el flag `?refresh=1` y el caller envía `X-API-Key`, vuelve a correr
    el aggregator antes de servir.
  - Por defecto devuelve resumen ejecutivo (`?full=0`); con `?full=1`
    devuelve el JSON completo (~360 KB).

Estrategia de v1.1 (Sprint 91.7 — background full refresh):
  - `?refresh=full` + header `X-API-Key`: dispara `run_all.py` en background
    thread (4 scanners + aggregator, ~8-12 min). Retorna inmediatamente con
    job metadata.
  - GET /v1/genome/now/job devuelve el estado del job activo (started_at,
    duration_sec, finished_at, status, last_error).
  - El estado se guarda en memoria (no persiste reinicios de Railway, pero
    cada reinicio de Railway implica re-deploy y los scanners se re-corren
    en el siguiente refresh). Un solo job activo por proceso (evita race
    conditions sobre _genome_out/*.json).

Auth: header X-API-Key validado contra os.environ['MONSTRUO_API_KEY']
para `?refresh=1` y `?refresh=full`. La lectura simple es pública.

Refs:
  - bridge/sprint_91_progress.md
  - scripts/genome_live/aggregator.py
  - scripts/genome_live/run_all.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query
from fastapi.responses import JSONResponse

genome_now_router = APIRouter(tags=["genome"])

ROOT = Path(__file__).resolve().parent.parent
GENOME_OUT = ROOT / "_genome_out" / "genome_now.json"
AGGREGATOR = ROOT / "scripts" / "genome_live" / "aggregator.py"
RUN_ALL = ROOT / "scripts" / "genome_live" / "run_all.py"

# In-memory job state (single active job per process).
# Sprint 91.7: background full refresh.
_JOB_LOCK = threading.Lock()
_JOB_STATE: dict[str, Any] = {
    "active": False,
    "started_at": None,
    "finished_at": None,
    "duration_sec": None,
    "status": "idle",  # idle | running | success | failed
    "last_error": None,
    "kind": None,  # "agg" | "full"
}


def _require_admin_key(api_key: str | None) -> None:
    expected = os.environ.get("MONSTRUO_API_KEY") or os.environ.get("MONSTRUO_WRITE_TOKEN")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="MONSTRUO_API_KEY no configurada en el server",
        )
    if not api_key or api_key.strip() != expected.strip():
        raise HTTPException(status_code=401, detail="X-API-Key inválida o ausente")


def _run_aggregator() -> None:
    """Ejecuta el aggregator localmente para regenerar genome_now.json."""
    if not AGGREGATOR.exists():
        raise HTTPException(
            status_code=500,
            detail=f"aggregator.py no encontrado en {AGGREGATOR}",
        )
    proc = subprocess.run(
        [sys.executable, str(AGGREGATOR)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"aggregator falló: {proc.stderr[-500:]}",
        )


def _run_full_pipeline_blocking() -> None:
    """
    Ejecuta scripts/genome_live/run_all.py en blocking mode (4 scanners +
    aggregator). Tarda 8-12 min. Solo debe llamarse desde un thread
    background — bloquearía el handler HTTP. Actualiza _JOB_STATE.
    """
    state = _JOB_STATE
    started = time.time()
    state["status"] = "running"
    state["last_error"] = None

    if not RUN_ALL.exists():
        state["status"] = "failed"
        state["last_error"] = f"run_all.py no encontrado en {RUN_ALL}"
        state["finished_at"] = datetime.now(timezone.utc).isoformat()
        state["duration_sec"] = round(time.time() - started, 1)
        state["active"] = False
        return

    try:
        proc = subprocess.run(
            [sys.executable, str(RUN_ALL)],
            capture_output=True,
            text=True,
            timeout=900,  # 15 min de hard limit
            cwd=str(ROOT),
        )
        if proc.returncode != 0:
            state["status"] = "failed"
            state["last_error"] = f"run_all.py exit={proc.returncode}: {proc.stderr[-500:]}"
        else:
            state["status"] = "success"
    except subprocess.TimeoutExpired:
        state["status"] = "failed"
        state["last_error"] = "run_all.py excedió timeout de 15 min"
    except Exception as e:
        state["status"] = "failed"
        state["last_error"] = f"excepción: {type(e).__name__}: {e}"

    state["finished_at"] = datetime.now(timezone.utc).isoformat()
    state["duration_sec"] = round(time.time() - started, 1)
    state["active"] = False


def _start_full_refresh_async() -> dict[str, Any]:
    """
    Dispara run_all.py en background thread. Retorna metadata del job.
    Si ya hay un job activo, retorna 409 (Conflict).
    """
    with _JOB_LOCK:
        if _JOB_STATE["active"]:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Ya hay un job de refresh corriendo",
                    "started_at": _JOB_STATE["started_at"],
                    "kind": _JOB_STATE["kind"],
                },
            )
        _JOB_STATE["active"] = True
        _JOB_STATE["kind"] = "full"
        _JOB_STATE["started_at"] = datetime.now(timezone.utc).isoformat()
        _JOB_STATE["finished_at"] = None
        _JOB_STATE["duration_sec"] = None
        _JOB_STATE["status"] = "running"
        _JOB_STATE["last_error"] = None

    thread = threading.Thread(target=_run_full_pipeline_blocking, daemon=True)
    thread.start()

    return {
        "accepted": True,
        "kind": "full",
        "started_at": _JOB_STATE["started_at"],
        "estimated_duration_sec": 600,
        "poll_url": "/v1/genome/now/job",
        "hint": "El job corre en background (~8-12 min). Pollea /v1/genome/now/job para ver status.",
    }


def _load_genome() -> dict[str, Any]:
    if not GENOME_OUT.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "genome_now.json no existe todavía. "
                "Corre los scanners F1-F4 y luego scripts/genome_live/aggregator.py "
                "(o llama a este endpoint con ?refresh=full y X-API-Key)."
            ),
        )
    try:
        return json.loads(GENOME_OUT.read_text())
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"genome_now.json corrupto: {e}")


@genome_now_router.get("/now", summary="Genome Vivo del Monstruo (estado binario)")
def get_genome_now(
    full: int = Query(0, description="1 = JSON completo, 0 = resumen ejecutivo"),
    refresh: str = Query("0", description="0/1/agg = aggregator (rápido); full = 4 scanners + aggregator (background, requiere X-API-Key)"),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> JSONResponse:
    """
    Devuelve el estado vivo del Monstruo en JSON.

    - `?full=0` (default): resumen ejecutivo + meta + cross_validation
    - `?full=1`: JSON completo (~360 KB) con todos los repos, servicios, tablas, etc.
    - `?refresh=1` + header `X-API-Key`: regenera el JSON re-corriendo
      SOLO el aggregator (~2 seg). Lee scanners ya cacheados en disco.
    - `?refresh=full` + header `X-API-Key` (Sprint 91.7): dispara run_all.py
      en background (4 scanners + aggregator, ~8-12 min). Retorna 202 con
      job metadata. Pollea GET /v1/genome/now/job para status.
    """
    refresh_normalized = (refresh or "0").strip().lower()

    if refresh_normalized == "full":
        _require_admin_key(x_api_key)
        job_meta = _start_full_refresh_async()
        # Incluir snapshot actual del genoma (puede estar viejo) para que el
        # caller tenga algo mientras espera.
        try:
            snapshot = _load_genome()
            current_meta = snapshot.get("meta", {})
        except HTTPException:
            current_meta = None
        return JSONResponse(
            status_code=202,
            content={
                "job": job_meta,
                "current_snapshot_meta": current_meta,
            },
        )

    if refresh_normalized in {"1", "agg", "aggregator"}:
        _require_admin_key(x_api_key)
        _run_aggregator()

    data = _load_genome()

    # Anotar si hay un job de refresh activo para que el caller sepa que el
    # snapshot puede estar siendo regenerado en background.
    job_state_view = {
        "active": _JOB_STATE["active"],
        "kind": _JOB_STATE["kind"],
        "started_at": _JOB_STATE["started_at"],
        "status": _JOB_STATE["status"],
    }

    if full == 0:
        return JSONResponse(
            content={
                "meta": data.get("meta", {}),
                "summaries": data.get("summaries", {}),
                "ecosystem_atomic_map": data.get("ecosystem_atomic_map", {}),
                "cross_validation": data.get("cross_validation", {}),
                "refresh_job": job_state_view,
                "_hint": "Llama con ?full=1 para JSON completo (~400 KB). Para datos frescos, usa ?refresh=full + X-API-Key.",
            }
        )

    # full=1: incluir job state pero no sobreescribir keys reales del JSON.
    response = dict(data)
    response.setdefault("refresh_job", job_state_view)
    return JSONResponse(content=response)


@genome_now_router.get("/now/health", summary="Health probe del endpoint Genome")
def genome_health() -> dict[str, Any]:
    """Health probe simple."""
    exists = GENOME_OUT.exists()
    if exists:
        try:
            data = json.loads(GENOME_OUT.read_text())
            return {
                "ok": True,
                "binario_100": data.get("meta", {}).get("binario_100", False),
                "generated_at": data.get("meta", {}).get("generated_at"),
                "size_bytes": GENOME_OUT.stat().st_size,
                "refresh_job": {
                    "active": _JOB_STATE["active"],
                    "status": _JOB_STATE["status"],
                    "kind": _JOB_STATE["kind"],
                },
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
    return {"ok": False, "error": "genome_now.json no existe"}


@genome_now_router.get("/now/job", summary="Estado del job de refresh full (Sprint 91.7)")
def genome_job_status() -> dict[str, Any]:
    """
    Retorna el estado del job de refresh full más reciente.
    - status: idle | running | success | failed
    - active: True mientras está corriendo
    - duration_sec: tiempo total cuando termina
    - last_error: detalle si status=failed
    """
    return dict(_JOB_STATE)
