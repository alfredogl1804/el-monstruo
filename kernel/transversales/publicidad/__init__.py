# kernel/transversales/publicidad/__init__.py
"""
Capa Transversal: Publicidad y Campañas (Obj #9).

Genera recomendaciones estructurales de ad platforms permitidas, geo
targeting, audience archetypes, creative angles, y required disclaimers
regulatorios per vertical.

IMPORTANTE — separacion estructura vs copy:
    Esta Capa devuelve DATA ESTRUCTURAL (platforms, audiences, creative
    angles conceptuales). NO devuelve ad copy final ni creative final.

IMPORTANTE — magna validation:
    Costos CPM/CPC benchmark 2026, audiencias vigentes, ad formats nuevos
    post-mayo-2025 estan fuera del cutoff de Cowork. Tags
    `[NEEDS_PERPLEXITY_VALIDATION]` aplicados.

Origen: AGENTS.md Regla Dura #2 (Capa 3 de las 7), DSC-G-002.
"""
from __future__ import annotations

from typing import Any

from kernel.transversales.base import (
    BusinessModelArchetype,
    GeoRegion,
    RestrictedVerticalError,
    TransversalContext,
    TransversalLayer,
    TransversalRecommendation,
    TransversalRecommendations,
    VerticalId,
)
from kernel.transversales.publicidad._canonical_constraints import (
    PUBLICIDAD_CANONICAL_PER_VERTICAL,
    SUPPORTED_AD_PLATFORMS,
    is_commercial,
    require_commercial,
)


class PublicidadLayer(TransversalLayer):
    """Implementacion de la Capa Publicidad."""

    layer_name = "publicidad"

    def diagnose(self, ctx: TransversalContext) -> dict[str, Any]:
        require_commercial(ctx.vertical)
        canonical = PUBLICIDAD_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        platforms_allowed = canonical.get("ad_platforms_allowed", [])
        platforms_blocked = canonical.get("ad_platforms_explicitly_blocked", [])
        return {
            "vertical": ctx.vertical.value,
            "archetype": ctx.archetype.value,
            "is_commercial": True,
            "platforms_allowed_count": len(platforms_allowed),
            "platforms_blocked_count": len(platforms_blocked),
            "platforms_allowed": platforms_allowed,
            "ad_priority_phase_1": canonical.get("ad_priority_phase_1", False),
            "geo_blocked": canonical.get("geo_blocked"),
            "geo_blocked_reason": canonical.get("geo_blocked_reason"),
            "deep_diagnostics_status": "pending_implementation",
        }

    def recommend(self, ctx: TransversalContext) -> TransversalRecommendations:
        require_commercial(ctx.vertical)
        canonical = PUBLICIDAD_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        recs: list[TransversalRecommendation] = []
        validation_tags: list[str] = []

        platforms_allowed = canonical.get("ad_platforms_allowed", [])
        platforms_blocked = canonical.get("ad_platforms_explicitly_blocked", [])
        recs.append(
            TransversalRecommendation(
                layer_name="publicidad",
                rule_id="publicidad.platforms.allowed_blocked",
                severity="must",
                value={
                    "platforms_allowed": platforms_allowed,
                    "platforms_explicitly_blocked": platforms_blocked,
                    "platforms_block_reason": canonical.get(
                        "ad_platforms_block_reason"
                    ),
                    "ad_priority_phase_1": canonical.get(
                        "ad_priority_phase_1", False
                    ),
                },
                rationale=(
                    "Ad platforms canonicas per vertical. Bloqueos derivados "
                    "de DSCs (regulatorios o de audiencia)."
                ),
                source_dsc=canonical.get("source_dscs", []),
            )
        )

        geo_target = canonical.get("geo_target")
        geo_blocked = canonical.get("geo_blocked", [])
        if geo_target or geo_blocked:
            recs.append(
                TransversalRecommendation(
                    layer_name="publicidad",
                    rule_id="publicidad.geo.targeting",
                    severity="must",
                    value={
                        "geo_target": geo_target,
                        "geo_target_states": canonical.get(
                            "geo_target_states", []
                        ),
                        "geo_blocked": geo_blocked,
                        "geo_blocked_reason": canonical.get(
                            "geo_blocked_reason"
                        ),
                    },
                    rationale=(
                        "Geo targeting derivado de DSCs. Bloqueos regulatorios "
                        "(ej. COFEPRIS) impiden geo-targeting hasta resolver."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        audiences = canonical.get("audience_archetypes", [])
        if audiences:
            recs.append(
                TransversalRecommendation(
                    layer_name="publicidad",
                    rule_id="publicidad.audience.archetypes",
                    severity="should",
                    value={
                        "audience_archetypes": audiences,
                        "audience_count": len(audiences),
                    },
                    rationale=(
                        "Audience archetypes derivados del modelo de negocio "
                        "y DSCs canonicos del vertical."
                    ),
                    needs_validation_tags=[
                        f"[NEEDS_PERPLEXITY_VALIDATION] audience_size_2026:"
                        f"{ctx.vertical.value}",
                    ],
                    source_dsc=canonical.get("source_dscs", []),
                )
            )
            validation_tags.append(
                f"[NEEDS_PERPLEXITY_VALIDATION] audience_size_2026:"
                f"{ctx.vertical.value}"
            )

        angles = canonical.get("creative_angles_canonical", [])
        if angles:
            recs.append(
                TransversalRecommendation(
                    layer_name="publicidad",
                    rule_id="publicidad.creative.angles",
                    severity="should",
                    value={
                        "angles": angles,
                        "copy_slot_per_angle": [f"{a}_copy_slot" for a in angles],
                    },
                    rationale=(
                        "Creative angles derivados de DSCs (ej. scarcity 313 "
                        "butacas, climatizado vs calor extremo). Slots de copy "
                        "vacios — los llena brand-voice."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        disclaimers = canonical.get("required_disclaimers", [])
        if disclaimers:
            recs.append(
                TransversalRecommendation(
                    layer_name="publicidad",
                    rule_id="publicidad.disclaimers.required",
                    severity="must",
                    value={
                        "disclaimers": disclaimers,
                        "placement": "ad_creative_or_landing_post_click",
                    },
                    rationale=(
                        "Disclaimers regulatorios obligatorios en ads del "
                        "vertical. Derivados de DSCs canonicos."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        recs.append(
            TransversalRecommendation(
                layer_name="publicidad",
                rule_id="publicidad.benchmarks.research_pending",
                severity="should",
                value={
                    "cost_benchmarks_pending": True,
                    "audience_validation_pending": True,
                },
                rationale=(
                    "Costos CPM/CPC benchmark 2026, audiencias activas, ad "
                    "formats post-mayo-2025 estan fuera del cutoff de Cowork. "
                    "Validacion via Perplexity requerida antes de campaign live."
                ),
                needs_validation_tags=[
                    f"[NEEDS_PERPLEXITY_VALIDATION] cpc_benchmark_2026:"
                    f"{ctx.vertical.value}",
                    f"[NEEDS_PERPLEXITY_VALIDATION] ad_formats_2026:"
                    f"{ctx.archetype.value}",
                    "[NEEDS_PERPLEXITY_VALIDATION] platform_policy_2026",
                ],
                source_dsc=[],
            )
        )
        validation_tags.extend([
            f"[NEEDS_PERPLEXITY_VALIDATION] cpc_benchmark_2026:"
            f"{ctx.vertical.value}",
            f"[NEEDS_PERPLEXITY_VALIDATION] ad_formats_2026:"
            f"{ctx.archetype.value}",
            "[NEEDS_PERPLEXITY_VALIDATION] platform_policy_2026",
        ])

        return TransversalRecommendations(
            layer_name="publicidad",
            vertical=ctx.vertical,
            archetype=ctx.archetype,
            recommendations=recs,
            diagnostics=self.diagnose(ctx),
            aggregated_validation_tags=validation_tags,
        )

    def implement(
        self, recommendations: TransversalRecommendations
    ) -> dict[str, Any]:
        raise NotImplementedError(
            "PublicidadLayer.implement pendiente Sprint TRANSVERSAL-001. "
            "Requiere ad platform APIs (Meta Marketing API, Google Ads API, "
            "TikTok Ads API, LinkedIn Ads API). "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] ad_platform_api_2026"
        )

    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        raise NotImplementedError(
            "PublicidadLayer.monitor pendiente Sprint TRANSVERSAL-001. "
            "Requiere ad platform reporting APIs + spend tracking. "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] ad_reporting_api_2026"
        )


__all__ = ["PublicidadLayer"]
