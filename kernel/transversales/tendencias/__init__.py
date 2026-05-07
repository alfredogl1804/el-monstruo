"""Capa Transversal: Tendencias y Adaptacion (Obj #9)."""
from __future__ import annotations
from typing import Any

from kernel.transversales.base import (
    RestrictedVerticalError, TransversalContext, TransversalLayer,
    TransversalRecommendation, TransversalRecommendations,
)
from kernel.transversales.tendencias._canonical_constraints import (
    MONITORING_CADENCES, SUPPORTED_DATA_SOURCES,
    TENDENCIAS_CANONICAL_PER_VERTICAL,
    is_commercial, require_commercial,
)


class TendenciasLayer(TransversalLayer):
    layer_name = "tendencias"

    def diagnose(self, ctx: TransversalContext) -> dict[str, Any]:
        require_commercial(ctx.vertical)
        canonical = TENDENCIAS_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        return {
            "vertical": ctx.vertical.value,
            "archetype": ctx.archetype.value,
            "is_commercial": True,
            "data_sources_count": len(canonical.get("data_sources", [])),
            "monitoring_cadence": canonical.get("monitoring_cadence"),
            "signal_types_count": len(canonical.get("signal_types_priorizados", [])),
            "deep_diagnostics_status": "pending_implementation",
        }

    def recommend(self, ctx: TransversalContext) -> TransversalRecommendations:
        require_commercial(ctx.vertical)
        canonical = TENDENCIAS_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        recs: list[TransversalRecommendation] = []
        validation_tags: list[str] = []

        data_sources = canonical.get("data_sources", [])
        if data_sources:
            recs.append(TransversalRecommendation(
                layer_name="tendencias", rule_id="tendencias.data_sources",
                severity="must",
                value={
                    "data_sources": data_sources,
                    "geo_focus": canonical.get("geo_focus"),
                },
                rationale=(
                    "Data sources canonicas per archetype + vertical. "
                    "Adicion fuera de SUPPORTED_DATA_SOURCES requiere DSC."
                ),
                source_dsc=canonical.get("source_dscs", []),
            ))

        cadence = canonical.get("monitoring_cadence")
        critical_cadence = canonical.get("monitoring_cadence_critical_signals")
        if cadence:
            recs.append(TransversalRecommendation(
                layer_name="tendencias",
                rule_id="tendencias.monitoring_cadence",
                severity="must",
                value={"cadence": cadence,
                       "cadence_critical_signals": critical_cadence},
                rationale="Cadence derivada del archetype.",
                source_dsc=canonical.get("source_dscs", []),
            ))

        signals = canonical.get("signal_types_priorizados", [])
        if signals:
            recs.append(TransversalRecommendation(
                layer_name="tendencias",
                rule_id="tendencias.signal_types",
                severity="should",
                value={"signal_types_priorizados": signals},
                rationale="Signal types derivados de DSCs canonicos.",
                needs_validation_tags=[
                    f"[NEEDS_PERPLEXITY_VALIDATION] trend_signals_active_2026:"
                    f"{ctx.vertical.value}",
                ],
                source_dsc=canonical.get("source_dscs", []),
            ))
            validation_tags.append(
                f"[NEEDS_PERPLEXITY_VALIDATION] trend_signals_active_2026:"
                f"{ctx.vertical.value}"
            )

        validation_tags.append(
            "[NEEDS_PERPLEXITY_VALIDATION] data_source_apis_vigentes_2026"
        )

        return TransversalRecommendations(
            layer_name="tendencias",
            vertical=ctx.vertical,
            archetype=ctx.archetype,
            recommendations=recs,
            diagnostics=self.diagnose(ctx),
            aggregated_validation_tags=validation_tags,
        )

    def implement(self, recommendations: TransversalRecommendations) -> dict[str, Any]:
        raise NotImplementedError(
            "TendenciasLayer.implement pendiente Sprint TRANSVERSAL-001. "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] data_source_apis_vigentes_2026"
        )

    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        raise NotImplementedError(
            "TendenciasLayer.monitor pendiente Sprint TRANSVERSAL-001. "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] alerting_stack_2026"
        )


__all__ = ["TendenciasLayer"]
