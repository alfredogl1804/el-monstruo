"""
Genome Now Routes — Sprint 91 F5 (Mapa Vivo 100% del Monstruo)
==============================================================

Router FastAPI que expone el endpoint GET /v1/genome/now.

Este endpoint sirve el JSON canónico del estado vivo del Monstruo agregado
por scripts/genome_live/aggregator.py a partir de los outputs de F1-F4
(github.json, railway.json, supabase.json, live24h.json).

Estrategia de v1.0 (esta entrega):
  - Sirve el JSON desde disco (`_genome_out/genome_now.json`).
  - Si el flag `?refresh=1` y el caller envía `X-API-Key`, vuelve a correr
    el aggregator antes de servir.
  - Por defecto devuelve resumen ejecutivo (`?full=0`); con `?full=1`
    devuelve el JSON completo (~360 KB).

v1.1 (futuro, Sprint 92): el endpoint disparará los scanners on-demand
con caching (TTL configurable), no leerá el JSON de disco.

Auth: header X-API-Key validado contra os.environ['MONSTRUO_API_KEY']
para `?refresh=1`. La lectura simple es pública para que cualquier hilo
pueda consumirlo sin credenciales.

Refs:
  - bridge/sprint_91_progress.md
  - scripts/genome_live/aggregator.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query
from fastapi.responses import JSONResponse

genome_now_router = APIRouter(tags=["genome"])

ROOT = Path(__file__).resolve().parent.parent
GENOME_OUT = ROOT / "_genome_out" / "genome_now.json"
AGGREGATOR = ROOT / "scripts" / "genome_live" / "aggregator.py"


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


def _load_genome() -> dict[str, Any]:
    if not GENOME_OUT.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "genome_now.json no existe todavía. "
                "Corre los scanners F1-F4 y luego scripts/genome_live/aggregator.py "
                "(o llama a este endpoint con ?refresh=1 y X-API-Key)."
            ),
        )
    try:
        return json.loads(GENOME_OUT.read_text())
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"genome_now.json corrupto: {e}")


@genome_now_router.get("/now", summary="Genome Vivo del Monstruo (estado binario)")
def get_genome_now(
    full: int = Query(0, description="1 = JSON completo, 0 = resumen ejecutivo"),
    refresh: int = Query(0, description="1 = vuelve a correr el aggregator (requiere X-API-Key)"),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> JSONResponse:
    """
    Devuelve el estado vivo del Monstruo en JSON.

    - `?full=0` (default): resumen ejecutivo + meta + cross_validation
    - `?full=1`: JSON completo (~360 KB) con todos los repos, servicios, tablas, etc.
    - `?refresh=1` + header `X-API-Key`: regenera el JSON antes de servir
    """
    if refresh == 1:
        _require_admin_key(x_api_key)
        _run_aggregator()

    data = _load_genome()

    if full == 0:
        # Resumen ejecutivo: meta + summaries + cross_validation, sin los blobs grandes
        return JSONResponse(
            content={
                "meta": data.get("meta", {}),
                "summaries": data.get("summaries", {}),
                "cross_validation": data.get("cross_validation", {}),
                "_hint": "Llama con ?full=1 para JSON completo (~360 KB)",
            }
        )

    return JSONResponse(content=data)


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
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
    return {"ok": False, "error": "genome_now.json no existe"}
