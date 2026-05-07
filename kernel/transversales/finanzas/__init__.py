"""Capa Transversal: Finanzas (Obj #9)."""
from __future__ import annotations
from typing import Any

from kernel.transversales.base import (
    RestrictedVerticalError, TransversalContext, TransversalLayer,
    TransversalRecommendation, TransversalRecommendations,
)
from kernel.transversales.finanzas._canonical_constraints import (
    FINANZAS_CANONICAL_PER_VERTICAL,
    SUPPORTED_REVENUE_MODELS, SUPPORTED_TAX_FRAMEWORKS,
    is_commercial, require_commercial,
)


class FinanzasLayer(TransversalLayer):
    layer_name = "finanzas"

    def diagnose(self, ctx: TransversalContext) -> dict[str, Any]:
        require_commercial(ctx.vertical)
        canonical = FINANZAS_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        return {
            "vertical": ctx.vertical.value,
            "archetype": ctx.archetype.value,
            "is_commercial": True,
            "revenue_models_count": len(canonical.get("revenue_models", [])),
            "tax_framework_pending_decision": canonical.get(
                "tax_framework_pending_decision", False),
            "tax_blocker_reason": canonical.get("tax_blocker_reason"),
            "revenue_can_be_recognized_mx_today": canonical.get(
                "revenue_can_be_recognized_mx_today", True),
            "deep_diagnostics_status": "pending_implementation",
        }

    def recommend(self, ctx: TransversalContext) -> TransversalRecommendations:
        require_commercial(ctx.vertical)
        canonical = FINANZAS_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        recs: list[TransversalRecommendation] = []
        validation_tags: list[str] = []

        revenue_models = canonical.get("revenue_models", [])
        if revenue_models:
            recs.append(TransversalRecommendation(
                layer_name="finanzas",
                rule_id="finanzas.revenue.models",
                severity="must",
                value={
                    "models": revenue_models,
                    "recognition_pattern": canonical.get("revenue_recognition_pattern"),
                    "min_unit_revenue_usd": canonical.get("min_unit_revenue_usd"),
                },
                rationale=(
                    "Revenue models y recognition pattern derivados del archetype "
                    "+ DSCs (ej. DSC-CIP-002 ticket $1 USD)."
                ),
                source_dsc=canonical.get("source_dscs", []),
            ))

        tax_frameworks = canonical.get("tax_frameworks_candidate", [])
        tax_pending = canonical.get("tax_framework_pending_decision", False)
        if tax_frameworks or tax_pending:
            recs.append(TransversalRecommendation(
                layer_name="finanzas",
                rule_id="finanzas.tax.framework",
                severity="must",
                value={
                    "frameworks_candidate": tax_frameworks,
                    "pending_decision": tax_pending,
                    "blocker_reason": canonical.get("tax_blocker_reason"),
                },
                rationale=(
                    "Tax framework candidatos. Bloqueado en verticales con "
                    "regulatorio pendiente."
                ),
                needs_validation_tags=[
                    f"[NEEDS_PERPLEXITY_VALIDATION] tax_rates_2026:"
                    f"{ctx.vertical.value}",
                ],
                source_dsc=canonical.get("source_dscs", []),
            ))
            validation_tags.append(
                f"[NEEDS_PERPLEXITY_VALIDATION] tax_rates_2026:"
                f"{ctx.vertical.value}"
            )

        if canonical.get("distribution_method_pending"):
            recs.append(TransversalRecommendation(
                layer_name="finanzas",
                rule_id="finanzas.distribution.pending",
                severity="must",
                value={
                    "pending": True,
                    "candidate_methods": canonical.get(
                        "distribution_methods_candidate", []),
                },
                rationale=(
                    "Distribucion de rendimientos al holder pendiente "
                    "(DSC-CIP-002 alt). USDC vs SPEI vs split."
                ),
                source_dsc=canonical.get("source_dscs", []),
            ))

        ue = canonical.get("unit_economics_tracked", [])
        if ue:
            recs.append(TransversalRecommendation(
                layer_name="finanzas",
                rule_id="finanzas.unit_economics",
                severity="should",
                value={"metrics_tracked": ue},
                rationale="Unit economics derivadas del archetype + DSCs.",
                needs_validation_tags=[
                    f"[NEEDS_PERPLEXITY_VALIDATION] industry_unit_economics_benchmark_2026:"
                    f"{ctx.archetype.value}",
                ],
                source_dsc=canonical.get("source_dscs", []),
            ))
            validation_tags.append(
                f"[NEEDS_PERPLEXITY_VALIDATION] industry_unit_economics_benchmark_2026:"
                f"{ctx.archetype.value}"
            )

        compliance = canonical.get("compliance_reporting", [])
        if compliance:
            recs.append(TransversalRecommendation(
                layer_name="finanzas",
                rule_id="finanzas.compliance.reporting",
                severity="must",
                value={"reports_required": compliance},
                rationale=(
                    "Compliance reporting derivado de DSCs (CFDI 4.0 MX, "
                    "on-chain audit polygon ERC-3643 DSC-CIP-004, COFEPRIS "
                    "post-aprobacion)."
                ),
                source_dsc=canonical.get("source_dscs", []),
            ))

        return TransversalRecommendations(
            layer_name="finanzas",
            vertical=ctx.vertical,
            archetype=ctx.archetype,
            recommendations=recs,
            diagnostics=self.diagnose(ctx),
            aggregated_validation_tags=validation_tags,
        )

    def implement(self, recommendations: TransversalRecommendations) -> dict[str, Any]:
        raise NotImplementedError(
            "FinanzasLayer.implement pendiente Sprint TRANSVERSAL-001. "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] accounting_stack_2026"
        )

    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        raise NotImplementedError(
            "FinanzasLayer.monitor pendiente Sprint TRANSVERSAL-001. "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] finops_dashboard_2026"
        )


__all__ = ["FinanzasLayer"]
