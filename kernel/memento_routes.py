"""
Memento Routes — Sprint Memento Bloque 3 (Capa Memoria Soberana v1.0)
=====================================================================

Router FastAPI que expone el endpoint POST /v1/memento/validate.

Diseño y decisiones (alineadas con spec_sprint_memento.md y green light Cowork):

1.  Auth idéntico al patrón existente (/v1/error-memory/seed, /v1/browser/*):
    header X-API-Key validado contra os.environ["MONSTRUO_API_KEY"] leído
    FRESH en cada request (no se cachea al boot — disciplina anti-Dory).
    El helper se exporta como `require_memento_admin_key` para reuso.

2.  El validador (MementoValidator) se instancia UNA vez al startup en el
    lifespan del kernel y se expone via `app.state.memento_validator`.
    El SourceCache vive en esa instancia, así los hits entre requests
    se aprovechan correctamente.

3.  Persistencia no-bloqueante: si Supabase falla al insertar, loggeamos
    `memento_persistence_failed` pero NO hacemos fail al cliente. La
    validación ya ocurrió y es lo importante; el log es secundario
    (Capa 7: Resiliencia Agéntica). La respuesta lleva el flag
    `persistence_failed=true` para que el llamador lo sepa.

4.  Logging estructurado con `structlog` (mismo patrón que el resto del
    kernel) en cada paso del pipeline.

5.  Rate limiting NO se implementa en v1.0 (lo dijo Cowork explícitamente).

6.  El endpoint es un APIRouter independiente, registrado en main.py via
    `app.include_router(memento_router, prefix="/v1/memento")`.

Refs:
    - bridge/sprint_memento_preinvestigation/spec_sprint_memento.md
    - kernel/memento/validator.py (lógica)
    - scripts/017_sprint_memento_schema.sql (tabla memento_validations)
"""
from __future__ import annotations

import asyncio
import html as _html
import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, HTTPException, Request, Response, status

from kernel.memento.contamination_detector import ContaminationDetector, ContaminationReport
from kernel.memento.models import (
    CriticalOperation,
    MementoValidationRequest,
    SourceOfTruth,
    ValidationResult,
)
from kernel.memento.validator import MementoValidator

logger = structlog.get_logger(__name__)

# Tabla en Supabase (espejo del bootstrap del Bloque 1, migration 017).
MEMENTO_VALIDATIONS_TABLE = "memento_validations"


# ===========================================================================
# Auth helper (reusable + testeable)
# ===========================================================================

def require_memento_admin_key(request: Request) -> None:
    """
    Valida el header X-API-Key contra MONSTRUO_API_KEY (lectura fresh).

    Raises:
        HTTPException(503): si MONSTRUO_API_KEY no está configurada en el env.
        HTTPException(401): si el header es válido pero la key no matchea
            (alineado con el patrón existente en error_memory_seed; aunque
            semánticamente sería 403, mantenemos consistencia con el resto
            del kernel).
        HTTPException(401): si falta el header.
    """
    admin_key = os.environ.get("MONSTRUO_API_KEY", "")
    if not admin_key:
        raise HTTPException(
            status_code=503,
            detail="memento_api_key_no_configurada",
        )
    provided = request.headers.get("X-API-Key", "") or request.headers.get(
        "Authorization", ""
    ).replace("Bearer ", "").strip()
    if not provided:
        raise HTTPException(
            status_code=401,
            detail="memento_api_key_missing",
        )
    if provided != admin_key:
        raise HTTPException(
            status_code=401,
            detail="memento_api_key_invalid",
        )


# ===========================================================================
# Persistencia (no-bloqueante)
# ===========================================================================

async def _persist_validation(
    *,
    db: Any,
    hilo_id: str,
    operation: str,
    context_used: Dict[str, Any],
    result: ValidationResult,
    intent_summary: Optional[str],
    contamination_report: Optional["ContaminationReport"] = None,
) -> bool:
    """
    Inserta la validación en `memento_validations`.

    Returns:
        True si la inserción fue exitosa, False si falló (no propaga excepción).
    """
    if db is None:
        logger.warning(
            "memento_persistence_skipped",
            reason="db_not_available",
            validation_id=result.validation_id,
        )
        return False

    try:
        row = {
            "validation_id": result.validation_id,
            "hilo_id": hilo_id,
            "operation": operation,
            "context_used": context_used,
            "intent_summary": intent_summary,
            "validation_status": result.validation_status.value,
            "discrepancy": result.discrepancy.model_dump(mode="json") if result.discrepancy else None,
            "proceed": result.proceed,
            "context_freshness_seconds": result.context_freshness_seconds,
            "remediation": result.remediation,
            "source_consulted": result.source_consulted,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        # Sprint Memento B6: contamination findings (shadow mode)
        if contamination_report is not None:
            row["contamination_warning"] = contamination_report.has_warning
            row["contamination_evidence"] = contamination_report.to_dict()
        await db.insert(MEMENTO_VALIDATIONS_TABLE, data=row)
        return True
    except Exception as exc:
        logger.warning(
            "memento_persistence_failed",
            error=str(exc),
            validation_id=result.validation_id,
            hilo_id=hilo_id,
            operation=operation,
        )
        return False


# ===========================================================================
# Router
# ===========================================================================

memento_router = APIRouter(tags=["memento"])


@memento_router.post(
    "/validate",
    summary="Validar contexto operativo contra fuentes de verdad",
    response_model=None,  # devolvemos un dict plano por compatibilidad con el spec
    status_code=status.HTTP_200_OK,
)
async def memento_validate(request: Request):
    """
    POST /v1/memento/validate

    Body (JSON):
        {
          "hilo_id": "hilo_manus_ticketlike",
          "operation": "sql_against_production",
          "context_used": {
            "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
            "user": "37Hy7adB53QmFW4.root",
            "credential_hash_first_8": "4N6caSwp"
          },
          "intent_summary": "Run E2E test post Stripe rotation"
        }

    Response (JSON, status 200):
        {
          "validation_id": "mv_2026-05-04T22:30:15_a1b2c3",
          "validation_status": "ok" | "discrepancy_detected" | "unknown_operation" | "source_unavailable",
          "proceed": true | false,
          "context_freshness_seconds": 12,
          "discrepancy": null | { ... },
          "remediation": null | "context_stale_or_contaminated: ...",
          "source_consulted": "ticketlike_credentials",
          "persistence_failed": false  // true si Supabase falló (no bloqueante)
        }

    Errors:
        - 401 unauthorized: API key missing or invalid
        - 422 validation error: malformed body (missing hilo_id, operation, context_used)
        - 503 service unavailable: MONSTRUO_API_KEY not configured OR validator not initialized
    """
    require_memento_admin_key(request)

    # Validator singleton (instanciado al startup del kernel)
    validator: Optional[MementoValidator] = getattr(
        request.app.state, "memento_validator", None
    )
    if validator is None:
        raise HTTPException(
            status_code=503,
            detail="memento_validator_not_initialized",
        )

    # Parse + valida body
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="memento_body_not_json",
        )

    try:
        req = MementoValidationRequest(**body)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"memento_body_invalid: {str(exc)[:300]}",
        )

    logger.info(
        "memento_validate_request",
        hilo_id=req.hilo_id,
        operation=req.operation,
        context_keys=list(req.context_used.keys()),
        intent_summary=req.intent_summary,
    )

    # Ejecutar validación
    try:
        result: ValidationResult = await validator.validate(
            operation=req.operation,
            context_used=req.context_used,
            hilo_id=req.hilo_id,
            intent_summary=req.intent_summary,
        )
    except Exception as exc:
        logger.error(
            "memento_validate_failed",
            error=str(exc),
            hilo_id=req.hilo_id,
            operation=req.operation,
        )
        raise HTTPException(
            status_code=500,
            detail=f"memento_validate_internal_error: {str(exc)[:300]}",
        )

    logger.info(
        "memento_validate_result",
        validation_id=result.validation_id,
        validation_status=result.validation_status.value,
        proceed=result.proceed,
        freshness=result.context_freshness_seconds,
        discrepancy_field=(result.discrepancy.field if result.discrepancy else None),
    )

    # ── Sprint Memento B6: detector de contexto contaminado (shadow mode) ──
    db = getattr(request.app.state, "db", None)
    detector: Optional[ContaminationDetector] = getattr(
        request.app.state, "memento_detector", None
    )
    contamination_report: Optional[ContaminationReport] = None
    if detector is not None:
        try:
            contamination_report = await detector.detect(
                hilo_id=req.hilo_id,
                operation=req.operation,
                context_used=req.context_used,
                current_validation_id=result.validation_id,
            )
            if contamination_report.has_warning:
                logger.warning(
                    "memento_contamination_detected",
                    validation_id=result.validation_id,
                    findings_count=len(contamination_report.findings),
                    has_high_severity=contamination_report.has_high_severity,
                    rule_ids=[f.rule_id for f in contamination_report.findings],
                    detector_runtime_ms=contamination_report.detector_runtime_ms,
                )
        except Exception as exc:  # pragma: no cover — defensive
            logger.warning(
                "memento_contamination_detector_error",
                error=str(exc),
                validation_id=result.validation_id,
            )
            contamination_report = None

    # Persistencia no-bloqueante
    persisted = await _persist_validation(
        db=db,
        hilo_id=req.hilo_id,
        operation=req.operation,
        context_used=req.context_used,
        result=result,
        intent_summary=req.intent_summary,
        contamination_report=contamination_report,
    )

    # Shape de respuesta — espejo del spec + B6 fields
    response: Dict[str, Any] = {
        "validation_id": result.validation_id,
        "validation_status": result.validation_status.value,
        "proceed": result.proceed,  # NO alterado por shadow mode
        "context_freshness_seconds": result.context_freshness_seconds,
        "discrepancy": result.discrepancy.model_dump(mode="json") if result.discrepancy else None,
        "remediation": result.remediation,
        "source_consulted": result.source_consulted,
        "persistence_failed": not persisted,
    }
    if contamination_report is not None:
        response["contamination_warning"] = contamination_report.has_warning
        response["contamination_findings"] = contamination_report.to_dict()["findings"]
    return response


# ===========================================================================
# Sprint Memento Bloque 7 — Admin endpoints (reload + dashboard)
# ===========================================================================
#
# Decisiones (alineadas con green light Cowork B7):
#
#   1. /admin/reload thread-safe via asyncio.Lock por app — un solo reload
#      simultáneo. Si otro request llega durante un reload activo: 409.
#   2. Hard timeout 5s. Si Supabase tarda más, abort + 504.
#   3. Recarga ATÓMICA: construye dicts nuevos, los swappea de una vez.
#      Nunca queda el validator con catálogo parcial.
#   4. Si Supabase falla pero hay YAML local → fallback (Capa 7) y returna
#      sources_loaded_from='yaml_fallback'.
#   5. /admin/dashboard reusa app.state.db, calcula métricas de los últimos
#      24h sobre memento_validations. JSON por default; HTML si Accept:text/html.
#
# Brand DNA: errores con identidad (memento_reload_*), naming /v1/memento/admin/*
# (Regla Dura #4), métricas pensadas para Command Center, no Grafana.

MEMENTO_RELOAD_TIMEOUT_SECONDS = 5
MEMENTO_DASHBOARD_LOOKBACK_HOURS = 24
MEMENTO_DASHBOARD_LOOKBACK_LIMIT = 1000  # cap defensivo de filas a procesar

# Lock por app (no global del módulo) — instancia perezosa en _get_reload_lock.
_RELOAD_LOCK_ATTR = "_memento_reload_lock"


def _get_reload_lock(request: Request) -> asyncio.Lock:
    """Crea (lazy) y devuelve el lock asyncio del app state. Un app = un lock."""
    lock: Optional[asyncio.Lock] = getattr(request.app.state, _RELOAD_LOCK_ATTR, None)
    if lock is None:
        lock = asyncio.Lock()
        setattr(request.app.state, _RELOAD_LOCK_ATTR, lock)
    return lock


async def _load_catalogs_from_supabase(
    db: Any,
) -> Dict[str, Any]:
    """
    Lee `memento_critical_operations` y `memento_sources_of_truth` desde
    Supabase y arma dicts {id: model}. Cualquier excepción se propaga al caller.
    """
    ops_rows = await db.select("memento_critical_operations", columns="*")
    src_rows = await db.select("memento_sources_of_truth", columns="*")

    critical_ops: Dict[str, CriticalOperation] = {}
    for r in ops_rows or []:
        if not r.get("activo", True):
            continue
        op = CriticalOperation(
            id=r["id"],
            nombre=r.get("nombre", r["id"]),
            descripcion=r.get("descripcion", ""),
            triggers=r.get("triggers") or [],
            requires_validation=bool(r.get("requires_validation", True)),
            requires_confirmation=r.get("requires_confirmation"),
            source_of_truth_ids=r.get("source_of_truth_ids") or [],
            activo=True,
        )
        critical_ops[op.id] = op

    sources: Dict[str, SourceOfTruth] = {}
    for r in src_rows or []:
        if not r.get("activo", True):
            continue
        s = SourceOfTruth(
            id=r["id"],
            nombre=r.get("nombre", r["id"]),
            descripcion=r.get("descripcion", ""),
            source_type=r["source_type"],
            location=r["location"],
            parser_id=r.get("parser_id"),
            cache_ttl_seconds=int(r.get("cache_ttl_seconds", 60)),
            activo=True,
        )
        sources[s.id] = s

    return {"critical_operations": critical_ops, "sources_of_truth": sources}


def _load_catalog_from_yaml() -> Dict[str, Any]:
    """
    Fallback YAML local para `memento_critical_operations`. Devuelve dict
    vacío para sources (el YAML actual sólo trae critical_operations).
    """
    import yaml as _yaml  # lazy

    yaml_path = Path(__file__).parent / "memento" / "critical_operations.yaml"
    if not yaml_path.exists():
        return {"critical_operations": {}, "sources_of_truth": {}}

    with open(yaml_path) as fh:
        cfg = _yaml.safe_load(fh) or {}

    critical_ops: Dict[str, CriticalOperation] = {}
    for r in cfg.get("critical_operations", []):
        op = CriticalOperation(
            id=r["id"],
            nombre=r.get("nombre", r["id"]),
            descripcion=r.get("descripcion", ""),
            triggers=r.get("triggers") or [],
            requires_validation=bool(r.get("requires_validation", True)),
            requires_confirmation=r.get("requires_confirmation"),
            source_of_truth_ids=r.get("source_of_truth_ids") or [],
            activo=bool(r.get("activo", True)),
        )
        if op.activo:
            critical_ops[op.id] = op

    return {"critical_operations": critical_ops, "sources_of_truth": {}}


@memento_router.post(
    "/admin/reload",
    summary="Recarga atómica del catálogo de operaciones críticas y fuentes de verdad",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def memento_admin_reload(request: Request):
    """
    POST /v1/memento/admin/reload

    Recarga el catálogo del MementoValidator desde Supabase con fallback a YAML.
    Atómico (swap completo) o falla. Thread-safe via asyncio.Lock.

    Auth: X-API-Key con MONSTRUO_API_KEY.

    Returns (200):
        {
          "status": "reloaded",
          "loaded_from": "supabase" | "yaml_fallback",
          "critical_operations_count": int,
          "sources_of_truth_count": int,
          "previous_critical_operations_count": int,
          "previous_sources_of_truth_count": int,
          "reload_runtime_ms": float,
          "cache_invalidated": true
        }

    Errors:
        - 401: API key missing/invalid
        - 409: reload already in progress (lock contention)
        - 503: validator not initialized OR no DB and no YAML available
        - 504: reload exceeded MEMENTO_RELOAD_TIMEOUT_SECONDS
    """
    require_memento_admin_key(request)

    validator: Optional[MementoValidator] = getattr(
        request.app.state, "memento_validator", None
    )
    if validator is None:
        raise HTTPException(
            status_code=503,
            detail="memento_validator_not_initialized",
        )

    lock = _get_reload_lock(request)
    if lock.locked():
        # Ya hay otro reload en curso. No bloqueamos al cliente — devolvemos 409.
        raise HTTPException(
            status_code=409,
            detail="memento_reload_already_in_progress",
        )

    db = getattr(request.app.state, "db", None)
    started = datetime.now(timezone.utc)
    previous_ops_count = len(validator.critical_operations)
    previous_sources_count = len(validator.sources_of_truth)

    async with lock:
        loaded_from: str
        try:
            if db is not None:
                try:
                    catalogs = await asyncio.wait_for(
                        _load_catalogs_from_supabase(db),
                        timeout=MEMENTO_RELOAD_TIMEOUT_SECONDS,
                    )
                    loaded_from = "supabase"
                except asyncio.TimeoutError:
                    logger.warning(
                        "memento_reload_supabase_timeout",
                        timeout_s=MEMENTO_RELOAD_TIMEOUT_SECONDS,
                    )
                    raise HTTPException(
                        status_code=504,
                        detail=f"memento_reload_supabase_timeout: > {MEMENTO_RELOAD_TIMEOUT_SECONDS}s",
                    )
                except HTTPException:
                    raise
                except Exception as exc:
                    # Supabase falló por otra razón → fallback YAML
                    logger.warning(
                        "memento_reload_supabase_failed_fallback_yaml",
                        error=str(exc),
                    )
                    catalogs = _load_catalog_from_yaml()
                    loaded_from = "yaml_fallback"
            else:
                catalogs = _load_catalog_from_yaml()
                loaded_from = "yaml_fallback"

            new_ops = catalogs["critical_operations"]
            new_sources = catalogs["sources_of_truth"]

            if not new_ops and not new_sources:
                raise HTTPException(
                    status_code=503,
                    detail="memento_reload_empty_catalog: ni Supabase ni YAML aportaron operaciones",
                )

            # SWAP ATÓMICO. Construimos un MementoValidator nuevo para que el
            # SourceCache se reinicialice (evita que un cambio de location de
            # una source quede tapado por el cache viejo).
            new_validator = MementoValidator(
                critical_operations=new_ops,
                sources_of_truth=new_sources,
            )
            request.app.state.memento_validator = new_validator

            runtime_ms = (datetime.now(timezone.utc) - started).total_seconds() * 1000.0

            logger.info(
                "memento_admin_reload_ok",
                loaded_from=loaded_from,
                ops=len(new_ops),
                sources=len(new_sources),
                runtime_ms=round(runtime_ms, 2),
            )

            return {
                "status": "reloaded",
                "loaded_from": loaded_from,
                "critical_operations_count": len(new_ops),
                "sources_of_truth_count": len(new_sources),
                "previous_critical_operations_count": previous_ops_count,
                "previous_sources_of_truth_count": previous_sources_count,
                "reload_runtime_ms": round(runtime_ms, 2),
                "cache_invalidated": True,  # nuevo SourceCache implícito
                "reloaded_at": started.isoformat(),
            }
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(
                "memento_admin_reload_failed",
                error=str(exc),
            )
            raise HTTPException(
                status_code=500,
                detail=f"memento_reload_internal_error: {str(exc)[:300]}",
            )


# ===========================================================================
# Dashboard
# ===========================================================================


def _safe_iso_to_dt(s: Any) -> Optional[datetime]:
    if not isinstance(s, str):
        return None
    try:
        # Soporta tanto "...Z" como "...+00:00"
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


async def _compute_dashboard_metrics(
    *,
    db: Any,
    validator: MementoValidator,
    detector: Optional[ContaminationDetector],
    lookback_hours: int = MEMENTO_DASHBOARD_LOOKBACK_HOURS,
) -> Dict[str, Any]:
    """Calcula las métricas del dashboard. Devuelve dict serializable."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    rows: List[Dict[str, Any]] = []

    if db is not None:
        try:
            raw = await db.select(
                MEMENTO_VALIDATIONS_TABLE,
                columns="validation_id,hilo_id,operation,validation_status,proceed,contamination_warning,contamination_evidence,ts",
                order_by="ts",
                order_desc=True,
                limit=MEMENTO_DASHBOARD_LOOKBACK_LIMIT,
            )
            rows = [r for r in (raw or []) if (_safe_iso_to_dt(r.get("ts")) or cutoff) >= cutoff]
        except TypeError:
            # MockDB de tests puede no aceptar order_by/limit
            try:
                raw = await db.select(MEMENTO_VALIDATIONS_TABLE, filters=None)
                rows = [r for r in (raw or []) if (_safe_iso_to_dt(r.get("ts")) or cutoff) >= cutoff]
            except Exception as exc:
                logger.warning("memento_dashboard_db_query_failed", error=str(exc))
                rows = []
        except Exception as exc:
            logger.warning("memento_dashboard_db_query_failed", error=str(exc))
            rows = []

    total = len(rows)
    ok_count = sum(1 for r in rows if r.get("validation_status") == "ok")
    discrepancy_count = sum(1 for r in rows if r.get("validation_status") == "discrepancy_detected")
    unknown_count = sum(1 for r in rows if r.get("validation_status") == "unknown_operation")
    source_unavailable_count = sum(1 for r in rows if r.get("validation_status") == "source_unavailable")
    contamination_count = sum(1 for r in rows if r.get("contamination_warning") is True)

    op_counter = Counter(r.get("operation") for r in rows if r.get("operation"))
    hilo_counter = Counter(r.get("hilo_id") for r in rows if r.get("hilo_id"))

    # Breakdown por rule_id (H1/H2/H3) y severity
    findings_breakdown: Dict[str, Counter] = {
        "by_rule_id": Counter(),
        "by_severity": Counter(),
    }
    for r in rows:
        evidence = r.get("contamination_evidence")
        if not isinstance(evidence, dict):
            continue
        for finding in evidence.get("findings", []) or []:
            rid = finding.get("rule_id")
            sev = finding.get("severity")
            if rid:
                findings_breakdown["by_rule_id"][rid] += 1
            if sev:
                findings_breakdown["by_severity"][sev] += 1

    def _rate(numerator: int) -> float:
        return round(numerator / total, 4) if total > 0 else 0.0

    # Salud del módulo
    health = {
        "validator_initialized": validator is not None,
        "detector_initialized": detector is not None,
        "db_available": db is not None,
        "critical_operations_loaded": len(validator.critical_operations) if validator else 0,
        "sources_of_truth_loaded": len(validator.sources_of_truth) if validator else 0,
    }

    return {
        "health": health,
        "window": {
            "lookback_hours": lookback_hours,
            "cutoff": cutoff.isoformat(),
            "sample_size": total,
            "sample_capped_at": MEMENTO_DASHBOARD_LOOKBACK_LIMIT,
        },
        "validations_last_24h": {
            "total": total,
            "ok": ok_count,
            "ok_rate": _rate(ok_count),
            "discrepancy_detected": discrepancy_count,
            "discrepancy_rate": _rate(discrepancy_count),
            "unknown_operation": unknown_count,
            "source_unavailable": source_unavailable_count,
        },
        "contamination_last_24h": {
            "warnings": contamination_count,
            "warning_rate": _rate(contamination_count),
            "breakdown": {
                "by_rule_id": dict(findings_breakdown["by_rule_id"]),
                "by_severity": dict(findings_breakdown["by_severity"]),
            },
        },
        "top_operations": [
            {"operation": op, "count": c} for op, c in op_counter.most_common(5)
        ],
        "top_hilos": [
            {"hilo_id": h, "count": c} for h, c in hilo_counter.most_common(5)
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _render_dashboard_html(metrics: Dict[str, Any]) -> str:
    """
    HTML mínimo para visualización humana. Brutalismo industrial: graphite + naranja forja.
    Sin JS, sin libs externas — sirve desde cualquier navegador / curl --header 'Accept: text/html'.
    """
    h = metrics["health"]
    w = metrics["window"]
    v = metrics["validations_last_24h"]
    c = metrics["contamination_last_24h"]
    top_ops = metrics["top_operations"]
    top_hilos = metrics["top_hilos"]

    def _row(k: str, val: Any) -> str:
        return f"<tr><td>{_html.escape(str(k))}</td><td>{_html.escape(str(val))}</td></tr>"

    ops_rows = "".join(
        f"<tr><td>{_html.escape(str(o['operation']))}</td><td>{o['count']}</td></tr>"
        for o in top_ops
    ) or "<tr><td colspan=2><em>sin datos en la ventana</em></td></tr>"
    hilos_rows = "".join(
        f"<tr><td>{_html.escape(str(o['hilo_id']))}</td><td>{o['count']}</td></tr>"
        for o in top_hilos
    ) or "<tr><td colspan=2><em>sin datos en la ventana</em></td></tr>"

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Memento — Dashboard de Vigilia</title>
<style>
  :root {{ --forja: #F97316; --graphite: #1C1917; --acero: #A8A29E; }}
  body {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background: var(--graphite); color: #E7E5E4; padding: 24px; }}
  h1, h2 {{ color: var(--forja); border-bottom: 2px solid var(--forja); padding-bottom: 6px; letter-spacing: 0.02em; }}
  h1 {{ font-size: 22px; }}
  h2 {{ font-size: 14px; margin-top: 28px; }}
  table {{ border-collapse: collapse; margin: 8px 0 16px; min-width: 380px; }}
  td {{ padding: 4px 12px; border-bottom: 1px solid #292524; font-size: 13px; }}
  td:first-child {{ color: var(--acero); }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 16px; }}
  .card {{ background: #0C0A09; border-left: 3px solid var(--forja); padding: 12px 16px; }}
  small {{ color: var(--acero); }}
</style>
</head>
<body>
<h1>Memento — Dashboard de Vigilia</h1>
<small>Capa Memoria Soberana · ventana últimas {w['lookback_hours']}h · generado {_html.escape(metrics['generated_at'])}</small>

<div class="grid">
  <div class="card">
    <h2>Salud del módulo</h2>
    <table>
      {_row('validator_initialized', h['validator_initialized'])}
      {_row('detector_initialized', h['detector_initialized'])}
      {_row('db_available', h['db_available'])}
      {_row('critical_operations_loaded', h['critical_operations_loaded'])}
      {_row('sources_of_truth_loaded', h['sources_of_truth_loaded'])}
    </table>
  </div>

  <div class="card">
    <h2>Validaciones (últimas {w['lookback_hours']}h)</h2>
    <table>
      {_row('total', v['total'])}
      {_row('ok', f"{v['ok']} ({v['ok_rate']*100:.1f}%)")}
      {_row('discrepancy_detected', f"{v['discrepancy_detected']} ({v['discrepancy_rate']*100:.1f}%)")}
      {_row('unknown_operation', v['unknown_operation'])}
      {_row('source_unavailable', v['source_unavailable'])}
    </table>
  </div>

  <div class="card">
    <h2>Contaminación detectada</h2>
    <table>
      {_row('warnings', f"{c['warnings']} ({c['warning_rate']*100:.1f}%)")}
    </table>
    <small>Por regla:</small>
    <table>
      {''.join(_row(k, v2) for k, v2 in (c['breakdown']['by_rule_id'] or {{'sin findings': 0}}).items())}
    </table>
    <small>Por severidad:</small>
    <table>
      {''.join(_row(k, v2) for k, v2 in (c['breakdown']['by_severity'] or {{'sin findings': 0}}).items())}
    </table>
  </div>

  <div class="card">
    <h2>Top operaciones</h2>
    <table>{ops_rows}</table>
  </div>

  <div class="card">
    <h2>Top hilos</h2>
    <table>{hilos_rows}</table>
  </div>
</div>

</body>
</html>"""


@memento_router.get(
    "/admin/dashboard",
    summary="Dashboard de salud y métricas del Memento (JSON o HTML)",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def memento_admin_dashboard(request: Request):
    """
    GET /v1/memento/admin/dashboard

    Devuelve métricas operativas de las últimas 24h.

    Auth: X-API-Key con MONSTRUO_API_KEY.

    Negociación de contenido:
        - Default → JSON
        - Header `Accept: text/html` → HTML brutalista (graphite + naranja forja)

    Errors:
        - 401: API key missing/invalid
        - 503: validator not initialized
    """
    require_memento_admin_key(request)

    validator: Optional[MementoValidator] = getattr(
        request.app.state, "memento_validator", None
    )
    if validator is None:
        raise HTTPException(
            status_code=503,
            detail="memento_validator_not_initialized",
        )

    db = getattr(request.app.state, "db", None)
    detector: Optional[ContaminationDetector] = getattr(
        request.app.state, "memento_detector", None
    )

    metrics = await _compute_dashboard_metrics(
        db=db,
        validator=validator,
        detector=detector,
    )

    accept = (request.headers.get("accept") or "").lower()
    if "text/html" in accept:
        body = _render_dashboard_html(metrics)
        return Response(content=body, media_type="text/html", status_code=200)
    return metrics


__all__ = [
    "memento_router",
    "require_memento_admin_key",
    "MEMENTO_VALIDATIONS_TABLE",
    "MEMENTO_RELOAD_TIMEOUT_SECONDS",
    "MEMENTO_DASHBOARD_LOOKBACK_HOURS",
]
