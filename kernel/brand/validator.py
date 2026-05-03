"""
El Monstruo — Brand Validator (Sprint 82)
==========================================
Evalúa outputs, endpoints, tool specs y error messages contra el Brand DNA.
Score 0-100 por validación. Threshold configurable (default 60, objetivo 75).

Modo ADVISORY: loguea violaciones sin bloquear. Promoción a bloqueante
cuando 100% de tools pasen threshold 75.

Referencia: docs/BRAND_ENGINE_ESTRATEGIA.md
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

from kernel.brand.brand_dna import (
    BRAND_DNA,
    get_forbidden_matches,
    is_generic_error,
    validate_output_name as _dna_validate_output_name,
)

logger = structlog.get_logger("brand.validator")


# ── Result Types ─────────────────────────────────────────────────────

@dataclass
class BrandValidationResult:
    """Resultado de una validación de compliance de marca."""

    target: str
    target_type: str  # "output_name", "endpoint", "tool_spec", "error_message"
    score: int
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    passes: bool = True
    validated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "target_type": self.target_type,
            "score": self.score,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "passes": self.passes,
            "validated_at": self.validated_at,
        }


@dataclass
class BrandAuditReport:
    """Reporte de auditoría de múltiples validaciones."""

    total: int = 0
    passed: int = 0
    failed: int = 0
    avg_score: float = 0.0
    results: list[dict[str, Any]] = field(default_factory=list)
    threshold: int = 60
    audited_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "avg_score": round(self.avg_score, 1),
            "results": self.results,
            "threshold": self.threshold,
            "audited_at": self.audited_at,
        }


# ── Brand Validator ──────────────────────────────────────────────────

class BrandValidator:
    """
    Valida outputs del Monstruo contra el Brand DNA.

    Score 0-100 por validación. Threshold configurable.
    Modo ADVISORY por default (loguea, no bloquea).

    Args:
        threshold: Score mínimo para pasar (default 60, objetivo 75).
        mode: "advisory" (solo loguea) o "enforcing" (bloquea).
    """

    def __init__(
        self,
        threshold: int = 60,
        mode: str = "advisory",
    ):
        self.threshold = max(0, min(100, threshold))
        self.mode = mode
        self._dna = BRAND_DNA
        self._validations_total = 0
        self._violations_total = 0

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "threshold": self.threshold,
            "mode": self.mode,
            "validations_total": self._validations_total,
            "violations_total": self._violations_total,
        }

    # ── Output Name Validation ───────────────────────────────────────

    def validate_output_name(self, name: str) -> BrandValidationResult:
        """
        Valida que un nombre de módulo/variable/clase siga las convenciones.

        Penalizaciones:
            -25 por cada término prohibido (service, handler, utils, etc.)
            -10 si el nombre es todo minúsculas sin separador (poco legible)
        """
        self._validations_total += 1
        score = 100
        issues: list[str] = []
        suggestions: list[str] = []

        if not name or not isinstance(name, str):
            return BrandValidationResult(
                target=str(name),
                target_type="output_name",
                score=0,
                issues=["Nombre vacío o inválido"],
                passes=False,
            )

        # Check forbidden terms
        forbidden = get_forbidden_matches(name)
        for f in forbidden:
            score -= 25
            issues.append(f"Término prohibido detectado: '{f}'")
            suggestions.append(
                f"Reemplazar '{f}' con un nombre con identidad "
                f"(ej: forja, guardian, colmena, magna, vigía)"
            )

        # Check readability
        if name == name.lower() and "_" not in name and len(name) > 12:
            score -= 10
            issues.append("Nombre largo sin separadores — difícil de leer")
            suggestions.append("Usar snake_case o PascalCase para legibilidad")

        score = max(0, score)
        passes = score >= self.threshold

        if not passes:
            self._violations_total += 1

        return BrandValidationResult(
            target=name,
            target_type="output_name",
            score=score,
            issues=issues,
            suggestions=suggestions,
            passes=passes,
        )

    # ── Endpoint Name Validation ─────────────────────────────────────

    def validate_endpoint_name(self, path: str) -> BrandValidationResult:
        """
        Valida que un endpoint siga las convenciones de naming.

        Penalizaciones:
            -25 por término prohibido en el path
            -15 si no tiene versionado (/api/v1/... o /v1/...)
            -10 si usa plural genérico sin identidad (/api/items)
        """
        self._validations_total += 1
        score = 100
        issues: list[str] = []
        suggestions: list[str] = []

        if not path or not isinstance(path, str):
            return BrandValidationResult(
                target=str(path),
                target_type="endpoint",
                score=0,
                issues=["Path vacío o inválido"],
                passes=False,
            )

        # Check forbidden terms in path segments
        segments = path.lower().split("/")
        for segment in segments:
            forbidden = get_forbidden_matches(segment)
            for f in forbidden:
                score -= 25
                issues.append(f"Término prohibido en endpoint: '{f}'")
                suggestions.append(
                    f"Renombrar segmento '{segment}' con identidad de marca"
                )

        # Check versioning
        has_version = bool(re.search(r"/v\d+/", path))
        if not has_version and not path.startswith("/health"):
            score -= 15
            issues.append("Endpoint sin versionado (/v1/, /v2/)")
            suggestions.append("Agregar prefijo de versión: /v1/...")

        score = max(0, score)
        passes = score >= self.threshold

        if not passes:
            self._violations_total += 1

        return BrandValidationResult(
            target=path,
            target_type="endpoint",
            score=score,
            issues=issues,
            suggestions=suggestions,
            passes=passes,
        )

    # ── Tool Spec Validation ─────────────────────────────────────────

    def validate_tool_spec(self, spec: dict[str, Any]) -> BrandValidationResult:
        """
        Valida que una ToolSpec cumpla con las convenciones de marca.

        Evalúa:
            - Nombre de la tool (sin términos prohibidos)
            - Descripción (no vacía, no genérica)
            - Categoría (presente)
            - Error handling (formato on-brand)

        Args:
            spec: Dict con al menos "name" y "description".
        """
        self._validations_total += 1
        score = 100
        issues: list[str] = []
        suggestions: list[str] = []

        tool_name = spec.get("name", "")
        description = spec.get("description", "")
        category = spec.get("category", "")

        # Validate name
        if not tool_name:
            score -= 30
            issues.append("Tool sin nombre")
        else:
            forbidden = get_forbidden_matches(tool_name)
            for f in forbidden:
                score -= 20
                issues.append(f"Nombre de tool contiene término prohibido: '{f}'")
                suggestions.append(
                    f"Renombrar '{tool_name}' — evitar '{f}'"
                )

        # Validate description
        if not description:
            score -= 20
            issues.append("Tool sin descripción")
            suggestions.append("Agregar descripción clara y específica")
        elif len(description) < 10:
            score -= 10
            issues.append("Descripción demasiado corta")
            suggestions.append("Expandir descripción con propósito y contexto")

        # Validate category
        if not category:
            score -= 10
            issues.append("Tool sin categoría")
            suggestions.append("Asignar categoría (ej: orquestación, investigación, ejecución)")

        score = max(0, score)
        passes = score >= self.threshold

        if not passes:
            self._violations_total += 1

        return BrandValidationResult(
            target=tool_name or "(sin nombre)",
            target_type="tool_spec",
            score=score,
            issues=issues,
            suggestions=suggestions,
            passes=passes,
        )

    # ── Error Message Validation ─────────────────────────────────────

    def validate_error_message(self, message: str) -> BrandValidationResult:
        """
        Valida que un error message siga el formato de marca.

        El Monstruo nunca dice "something went wrong". Cada error tiene
        identidad: módulo, acción, tipo de falla.

        Penalizaciones:
            -30 si es un error genérico
            -15 si no sigue el formato {module}_{action}_{failure_type}
        """
        self._validations_total += 1
        score = 100
        issues: list[str] = []
        suggestions: list[str] = []

        if not message or not isinstance(message, str):
            return BrandValidationResult(
                target=str(message),
                target_type="error_message",
                score=0,
                issues=["Mensaje de error vacío"],
                passes=False,
            )

        # Check for generic errors
        if is_generic_error(message):
            score -= 30
            issues.append(f"Error genérico detectado: '{message}'")
            suggestions.append(
                "Usar formato: {module}_{action}_{failure_type} "
                "(ej: embrion_classify_timeout)"
            )

        # Check format compliance (module_action_failure)
        has_brand_format = bool(re.match(r"^[a-z]+_[a-z]+_[a-z_]+$", message.strip()))
        if not has_brand_format and not is_generic_error(message):
            # Only penalize if it's not already caught as generic
            if "_" not in message:
                score -= 15
                issues.append("Error message sin formato de marca")
                suggestions.append(
                    "Formato esperado: {module}_{action}_{failure_type}"
                )

        score = max(0, score)
        passes = score >= self.threshold

        if not passes:
            self._violations_total += 1

        return BrandValidationResult(
            target=message[:100],
            target_type="error_message",
            score=score,
            issues=issues,
            suggestions=suggestions,
            passes=passes,
        )

    # ── Batch Audit ──────────────────────────────────────────────────

    def audit_tool_specs(
        self, specs: list[dict[str, Any]]
    ) -> BrandAuditReport:
        """
        Audita una lista completa de ToolSpecs contra el Brand DNA.

        Returns:
            BrandAuditReport con total, passed, failed, avg_score y detalle.
        """
        report = BrandAuditReport(threshold=self.threshold)
        scores: list[int] = []

        for spec in specs:
            result = self.validate_tool_spec(spec)
            report.results.append(result.to_dict())
            scores.append(result.score)

            if result.passes:
                report.passed += 1
            else:
                report.failed += 1

        report.total = len(specs)
        report.avg_score = sum(scores) / len(scores) if scores else 0.0

        logger.info(
            "brand_audit_completed",
            total=report.total,
            passed=report.passed,
            failed=report.failed,
            avg_score=report.avg_score,
            threshold=self.threshold,
        )

        return report

    def audit_endpoints(self, paths: list[str]) -> BrandAuditReport:
        """
        Audita una lista de endpoints contra las convenciones de naming.
        """
        report = BrandAuditReport(threshold=self.threshold)
        scores: list[int] = []

        for path in paths:
            result = self.validate_endpoint_name(path)
            report.results.append(result.to_dict())
            scores.append(result.score)

            if result.passes:
                report.passed += 1
            else:
                report.failed += 1

        report.total = len(paths)
        report.avg_score = sum(scores) / len(scores) if scores else 0.0

        return report
