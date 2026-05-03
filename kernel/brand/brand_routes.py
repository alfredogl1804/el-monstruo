"""
El Monstruo — Brand Engine Routes (Sprint 52)
===============================================
4 endpoints para el Brand Engine:
    GET  /v1/brand/dna          → Retorna el Brand DNA completo
    POST /v1/brand/validate     → Valida un nombre/endpoint/error contra el DNA
    GET  /v1/brand/violations   → Últimas violaciones de compliance
    POST /v1/brand/audit-tools  → Audita todas las ToolSpecs registradas

Consumidos por: Command Center, auditorías internas, bootstrap hook.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from kernel.brand.brand_dna import BRAND_DNA
from kernel.brand.validator import BrandValidator

logger = structlog.get_logger("brand.routes")

router = APIRouter(prefix="/v1/brand", tags=["brand"])

# ── Module-level validator (initialized at import, threshold from env) ──
_default_threshold = int(os.environ.get("BRAND_VALIDATOR_THRESHOLD", "60"))
brand_validator = BrandValidator(threshold=_default_threshold, mode="advisory")


# ── Request Models ───────────────────────────────────────────────────

class ValidateRequest(BaseModel):
    target: str = Field(..., min_length=1, max_length=500, description="Nombre, path o mensaje a validar")
    target_type: str = Field(
        ...,
        description="Tipo: output_name, endpoint, tool_spec, error_message",
    )
    spec: Optional[dict[str, Any]] = Field(
        default=None,
        description="ToolSpec completa (requerido si target_type=tool_spec)",
    )


class AuditToolsRequest(BaseModel):
    specs: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="Lista de ToolSpecs a auditar",
    )


# ── Routes ───────────────────────────────────────────────────────────

@router.get("/dna")
async def get_brand_dna():
    """
    Retorna el Brand DNA completo del Monstruo.

    Consumido por: Command Center (panel de identidad), Embriones (pre-output).
    """
    return {
        "brand_dna": BRAND_DNA,
        "validator": brand_validator.stats,
    }


@router.post("/validate")
async def validate_target(req: ValidateRequest):
    """
    Valida un nombre, endpoint o error message contra el Brand DNA.

    Retorna score 0-100, issues, suggestions, y si pasa el threshold.
    """
    if req.target_type == "output_name":
        result = brand_validator.validate_output_name(req.target)
    elif req.target_type == "endpoint":
        result = brand_validator.validate_endpoint_name(req.target)
    elif req.target_type == "error_message":
        result = brand_validator.validate_error_message(req.target)
    elif req.target_type == "tool_spec":
        if not req.spec:
            raise HTTPException(
                400,
                "brand_validate_missing_spec: target_type=tool_spec requiere campo 'spec'",
            )
        result = brand_validator.validate_tool_spec(req.spec)
    else:
        raise HTTPException(
            400,
            f"brand_validate_invalid_type: target_type '{req.target_type}' no reconocido. "
            "Usar: output_name, endpoint, tool_spec, error_message",
        )

    # Log to structured log (advisory mode)
    if not result.passes:
        logger.warning(
            "brand_validation_failed",
            target=result.target,
            target_type=result.target_type,
            score=result.score,
            issues=result.issues,
        )

    return {"result": result.to_dict()}


@router.get("/violations")
async def get_violations(
    limit: int = Query(default=50, ge=1, le=200),
    target_type: Optional[str] = Query(default=None),
):
    """
    Retorna las últimas violaciones de compliance de marca desde Supabase.

    Consumido por: Command Center (panel de compliance), auditorías.
    """
    try:
        from kernel.supabase_client import get_supabase_client

        supabase = get_supabase_client()
        query = (
            supabase.table("brand_compliance_log")
            .select("*")
            .eq("passes", False)
            .order("created_at", desc=True)
            .limit(limit)
        )

        if target_type:
            query = query.eq("target_type", target_type)

        response = query.execute()
        violations = response.data if response.data else []

        return {
            "violations": violations,
            "count": len(violations),
            "validator_stats": brand_validator.stats,
        }
    except Exception as e:
        logger.warning("brand_violations_query_failed", error=str(e))
        # Fallback: return in-memory stats only
        return {
            "violations": [],
            "count": 0,
            "validator_stats": brand_validator.stats,
            "note": "Supabase query failed — showing in-memory stats only",
        }


@router.post("/audit-tools")
async def audit_tools(req: AuditToolsRequest):
    """
    Audita una lista de ToolSpecs contra el Brand DNA.

    Retorna reporte completo: total, passed, failed, avg_score, detalle por tool.
    """
    report = brand_validator.audit_tool_specs(req.specs)

    # Log summary
    logger.info(
        "brand_audit_tools_executed",
        total=report.total,
        passed=report.passed,
        failed=report.failed,
        avg_score=report.avg_score,
    )

    return {"report": report.to_dict()}
