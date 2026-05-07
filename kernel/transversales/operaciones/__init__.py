"""Capa Transversal: Administracion y Operaciones (Obj #9)."""
from __future__ import annotations
from typing import Any

from kernel.transversales.base import (
    RestrictedVerticalError, TransversalContext, TransversalLayer,
    TransversalRecommendation, TransversalRecommendations,
)
from kernel.transversales.operaciones._canonical_constraints import (
    OPERACIONES_CANONICAL_PER_VERTICAL,
    SUPPORTED_FULFILLMENT_PATTERNS, SUPPORTED_SUPPORT_CHANNELS,
    is_commercial, require_commercial,
)


class OperacionesLayer(TransversalLayer):
    layer_name = "operaciones"

    def diagnose(self, ctx: TransversalContext) -> dict[str, Any]:
        require_commercial(ctx.vertical)
        canonical = OPERACIONES_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        return {
            "vertical": ctx.vertical.value,
            "archetype": ctx.archetype.value,
            "is_commercial": True,
            "support_channels_count": len(canonical.get("support_channels", [])),
            "support_sla_first_response_hours": canonical.get("support_sla_first_response_hours"),
            "operations_can_launch_mx_today": canonical.get(
                "operations_can_launch_mx_today", True),
            "operations_blocker_reason": canonical.get("operations_blocker_reason"),
            "deep_diagnostics_status": "pending_implementation",
        }

    def recommend(self, ctx: TransversalContext) -> TransversalRecommendations:
        require_commercial(ctx.vertical)
        canonical = OPERACIONES_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        recs: list[TransversalRecommendation] = []
        validation_tags: list[str] = []

        channels = canonical.get("support_channels", [])
        if channels:
            recs.append(TransversalRecommendation(
                layer_name="operaciones",
                rule_id="operaciones.support.channels",
                severity="must",
                value={
                    "channels": channels,
                    "sla_first_response_hours": canonical.get("support_sla_first_response_hours"),
                    "support_24_7_required": canonical.get("support_24_7_required", False),
                    "timezone": canonical.get(
                        "support_business_hours_timezone", "UTC"),
                },
                rationale=(
                    "Support channels y SLA derivados del archetype y constraints "
                    "del vertical (DSC-K365-001 365 dias)."
                ),
                source_dsc=canonical.get("source_dscs", []),
            ))

        fulfillment = canonical.get("fulfillment_patterns", [])
        if fulfillment:
            recs.append(TransversalRecommendation(
                layer_name="operaciones",
                rule_id="operaciones.fulfillment.patterns",
                severity="must",
                value={
                    "patterns": fulfillment,
                    "components_required": canonical.get(
                        "fulfillment_components_required", []),
                },
                rationale=(
                    "Fulfillment patterns canonicos. DSC-LIKETICKETS-003 declara "
                    "stripe_session_webhook_canonical replicable."
                ),
                source_dsc=canonical.get("source_dscs", []),
            ))

        inventory_strategy = canonical.get("inventory_strategy")
        if inventory_strategy:
            recs.append(TransversalRecommendation(
                layer_name="operaciones",
                rule_id="operaciones.inventory.strategy",
                severity="must",
                value={
                    "strategy": inventory_strategy,
                    "canonical_count": canonical.get("inventory_canonical_count"),
                },
                rationale="Inventory strategy derivada de DSC del vertical.",
                source_dsc=canonical.get("source_dscs", []),
            ))

        blockers = canonical.get("regulatory_blockers", [])
        prohibited = canonical.get("prohibited_operations", [])
        if blockers or prohibited:
            recs.append(TransversalRecommendation(
                layer_name="operaciones",
                rule_id="operaciones.regulatory.gates",
                severity="must",
                value={
                    "regulatory_blockers": blockers,
                    "prohibited_operations": prohibited,
                    "operations_can_launch_mx_today": canonical.get(
                        "operations_can_launch_mx_today", True),
                    "blocker_reason": canonical.get("operations_blocker_reason"),
                    "regulatory_ops_post_approval": canonical.get(
                        "regulatory_ops_post_approval", []),
                },
                rationale=(
                    "Regulatory gates duros derivados de DSCs (CIP fideicomiso, "
                    "BG COFEPRIS, etc). Bloqueantes."
                ),
                source_dsc=canonical.get("source_dscs", []),
            ))

        validation_tags.append(
            "[NEEDS_PERPLEXITY_VALIDATION] regulatory_landscape_2026:"
            f"{ctx.vertical.value}"
        )

        return TransversalRecommendations(
            layer_name="operaciones",
            vertical=ctx.vertical,
            archetype=ctx.archetype,
            recommendations=recs,
            diagnostics=self.diagnose(ctx),
            aggregated_validation_tags=validation_tags,
        )

    def implement(self, recommendations: TransversalRecommendations) -> dict[str, Any]:
        raise NotImplementedError(
            "OperacionesLayer.implement pendiente Sprint TRANSVERSAL-001. "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] helpdesk_api_2026"
        )

    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        raise NotImplementedError(
            "OperacionesLayer.monitor pendiente Sprint TRANSVERSAL-001. "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] sla_metrics_pipeline_2026"
        )


__all__ = ["OperacionesLayer"]
