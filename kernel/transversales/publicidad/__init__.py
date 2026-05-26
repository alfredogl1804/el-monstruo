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
                    "platforms_block_reason": canonical.get("ad_platforms_block_reason"),
                    "ad_priority_phase_1": canonical.get("ad_priority_phase_1", False),
                },
                rationale=(
                    "Ad platforms canonicas per vertical. Bloqueos derivados de DSCs (regulatorios o de audiencia)."
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
                        "geo_target_states": canonical.get("geo_target_states", []),
                        "geo_blocked": geo_blocked,
                        "geo_blocked_reason": canonical.get("geo_blocked_reason"),
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
                    rationale=("Audience archetypes derivados del modelo de negocio y DSCs canonicos del vertical."),
                    needs_validation_tags=[
                        f"[NEEDS_PERPLEXITY_VALIDATION] audience_size_2026:{ctx.vertical.value}",
                    ],
                    source_dsc=canonical.get("source_dscs", []),
                )
            )
            validation_tags.append(f"[NEEDS_PERPLEXITY_VALIDATION] audience_size_2026:{ctx.vertical.value}")

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
                        "Disclaimers regulatorios obligatorios en ads del vertical. Derivados de DSCs canonicos."
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
                    f"[NEEDS_PERPLEXITY_VALIDATION] cpc_benchmark_2026:{ctx.vertical.value}",
                    f"[NEEDS_PERPLEXITY_VALIDATION] ad_formats_2026:{ctx.archetype.value}",
                    "[NEEDS_PERPLEXITY_VALIDATION] platform_policy_2026",
                ],
                source_dsc=[],
            )
        )
        validation_tags.extend(
            [
                f"[NEEDS_PERPLEXITY_VALIDATION] cpc_benchmark_2026:{ctx.vertical.value}",
                f"[NEEDS_PERPLEXITY_VALIDATION] ad_formats_2026:{ctx.archetype.value}",
                "[NEEDS_PERPLEXITY_VALIDATION] platform_policy_2026",
            ]
        )

        return TransversalRecommendations(
            layer_name="publicidad",
            vertical=ctx.vertical,
            archetype=ctx.archetype,
            recommendations=recs,
            diagnostics=self.diagnose(ctx),
            aggregated_validation_tags=validation_tags,
        )

    def implement(self, recommendations: TransversalRecommendations) -> dict[str, Any]:
        """
        Genera plan canonico de campanas publicitarias en estado PAUSED.

        CRITICO: TODA campana se crea con status='paused' por defecto.
        Activacion requiere firma de Alfredo via DSC-G-002 (HITL bloqueante
        para spend real). Cero gasto sin firma.

        Produce:
        - campaigns_plan: 1 campaign por (platform, angle) con copy slots
        - ad_platform_endpoints: Meta/Google/TikTok endpoints REST oficiales
        - geo_targeting + audience_archetypes + disclaimers requeridos
        - hard_safeguards: campaign_status='paused', spend_cap_daily_usd=0
        - validation_log_anchors: rows 34 (cpc_benchmark), 35 (ad_formats),
          36 (platform_policy)
        """
        import os

        rules = {r.rule_id: r.value for r in recommendations.recommendations}
        platforms_rule = rules.get("publicidad.platforms.allowed_blocked", {})
        geo_rule = rules.get("publicidad.geo.targeting", {})
        audience_rule = rules.get("publicidad.audience.archetypes", {})
        creative_rule = rules.get("publicidad.creative.angles", {})
        disclaimers_rule = rules.get("publicidad.disclaimers.required", {})

        platforms_allowed = platforms_rule.get("platforms_allowed", [])
        platforms_blocked = platforms_rule.get("platforms_explicitly_blocked", [])

        # Endpoints REST canonicos per ad platform (validados magna
        # platform_policy_2026, validation_log id=36).
        ad_platform_endpoints = {
            "meta_ads": {
                "create_campaign": "POST https://graph.facebook.com/v20.0/act_{account_id}/campaigns",
                "insights": "GET https://graph.facebook.com/v20.0/act_{account_id}/insights",
                "env_required": ["META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID"],
                "campaign_default_status": "PAUSED",
            },
            "google_ads": {
                "create_campaign": "POST https://googleads.googleapis.com/v17/customers/{customer_id}/campaigns:mutate",
                "insights": "POST https://googleads.googleapis.com/v17/customers/{customer_id}/googleAds:searchStream",
                "env_required": [
                    "GOOGLE_ADS_DEVELOPER_TOKEN",
                    "GOOGLE_ADS_CUSTOMER_ID",
                    "GOOGLE_ADS_OAUTH_REFRESH_TOKEN",
                ],
                "campaign_default_status": "PAUSED",
            },
            "tiktok_ads": {
                "create_campaign": "POST https://business-api.tiktok.com/open_api/v1.3/campaign/create/",
                "insights": "GET https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
                "env_required": [
                    "TIKTOK_ACCESS_TOKEN",
                    "TIKTOK_ADVERTISER_ID",
                ],
                "campaign_default_status": "DISABLE",
            },
            "linkedin_ads": {
                "create_campaign": "POST https://api.linkedin.com/rest/adCampaigns",
                "insights": "GET https://api.linkedin.com/rest/adAnalytics",
                "env_required": [
                    "LINKEDIN_ACCESS_TOKEN",
                    "LINKEDIN_AD_ACCOUNT_ID",
                ],
                "campaign_default_status": "PAUSED",
            },
        }

        angles = creative_rule.get("angles", [])
        if not angles:
            angles = ["generic_awareness"]

        campaigns_plan: list[dict[str, Any]] = []
        all_pending_envs: set[str] = set()
        for platform in platforms_allowed:
            ep = ad_platform_endpoints.get(platform, {})
            req_envs = ep.get("env_required", [])
            pending = [e for e in req_envs if not os.environ.get(e)]
            all_pending_envs.update(pending)
            for angle in angles:
                campaigns_plan.append(
                    {
                        "platform": platform,
                        "angle": angle,
                        "campaign_name_slot": f"{{{{CAMPAIGN_NAME_{platform.upper()}_{angle.upper()}_SLOT}}}}",
                        "primary_text_slot": f"{{{{PRIMARY_TEXT_{angle.upper()}_SLOT}}}}",
                        "headline_slot": f"{{{{HEADLINE_{angle.upper()}_SLOT}}}}",
                        "cta_slot": "{{CTA_BUTTON_SLOT}}",
                        "image_url_slot": "{{IMAGE_URL_SLOT}}",
                        "status": "paused",  # HARD DEFAULT
                        "spend_cap_daily_usd": 0.0,  # HARD DEFAULT
                        "endpoints": ep,
                        "required_envs": req_envs,
                        "pending_envs": pending,
                        "ready_for_dryrun_payload": not pending,
                    }
                )

        return {
            "vertical": recommendations.vertical.value,
            "campaigns_plan": campaigns_plan,
            "platforms_allowed": platforms_allowed,
            "platforms_explicitly_blocked": platforms_blocked,
            "platforms_block_reason": platforms_rule.get("platforms_block_reason"),
            "geo_target": geo_rule.get("geo_target"),
            "geo_target_states": geo_rule.get("geo_target_states", []),
            "geo_blocked": geo_rule.get("geo_blocked", []),
            "geo_blocked_reason": geo_rule.get("geo_blocked_reason"),
            "audience_archetypes": audience_rule.get("audience_archetypes", []),
            "required_disclaimers": disclaimers_rule.get("disclaimers", []),
            "hard_safeguards": {
                "campaign_status_default": "paused",
                "spend_cap_daily_usd": 0.0,
                "activation_requires_firma_alfredo": True,
                "activation_dsc_gate": "DSC-G-002",
                "reason": (
                    "PublicidadLayer NUNCA activa campanas sin firma humana. "
                    "Push real con status=ACTIVE requiere DSC firmado por "
                    "Alfredo en el mismo PR, NUNCA por agente automatico."
                ),
            },
            "pending_envs": sorted(all_pending_envs),
            "dry_run": True,
            "dry_run_reason": (
                "DSC-G-002 HITL: cero spend publicitario sin firma humana. Payload generado para revision pre-firma."
            ),
            "validation_log_anchors": [
                {
                    "claim_type": f"cpc_benchmark_2026:{recommendations.vertical.value}",
                    "row_id_hint": 34,
                },
                {
                    "claim_type": f"ad_formats_2026:{recommendations.archetype.value}",
                    "row_id_hint": 35,
                },
                {"claim_type": "platform_policy_2026", "row_id": 36},
            ],
            "validation_tags_pending": list(recommendations.aggregated_validation_tags),
        }

    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        """
        Health-check estructural + spend_health canonico (cero gasto
        sin firma).

        Sin red. Spend observado requiere inyectar storage o ad platform
        API en futuro sprint.
        """
        require_commercial(ctx.vertical)
        recommendations = self.recommend(ctx)
        impl_artifacts = self.implement(recommendations)

        warnings: list[str] = []
        blockers: list[str] = []

        # BLOCKER duro: si geo_blocked tiene contenido sin razon documentada.
        if impl_artifacts["geo_blocked"] and not impl_artifacts["geo_blocked_reason"]:
            blockers.append("geo_blocked sin razon documentada — violacion DSC-G-008 v2.")

        not_ready = [c for c in impl_artifacts["campaigns_plan"] if not c["ready_for_dryrun_payload"]]
        if not_ready:
            warnings.append(
                f"{len(not_ready)} de {len(impl_artifacts['campaigns_plan'])} "
                f"campaigns no estan ready (faltan envs: "
                f"{', '.join(impl_artifacts['pending_envs'])})."
            )
        if impl_artifacts["validation_tags_pending"]:
            warnings.append(
                f"{len(impl_artifacts['validation_tags_pending'])} tags Perplexity pendientes via DSC-V-001."
            )

        # Verificacion HARD: TODAS las campanas DEBEN estar en paused.
        active_campaigns = [c for c in impl_artifacts["campaigns_plan"] if c["status"] != "paused"]
        if active_campaigns:
            blockers.append(
                f"VIOLACION DSC-G-002: {len(active_campaigns)} campanas "
                f"con status != 'paused' detectadas. Toda activacion "
                f"requiere firma Alfredo."
            )

        spend_health = {
            "spend_cap_daily_usd": 0.0,
            "spend_observed_24h_usd": 0.0,
            "active_campaigns_count": len(active_campaigns),
            "status": ("all_paused" if not active_campaigns else "VIOLATION_active_without_firma"),
            "note": (
                "Spend observado real requiere ad platform reporting APIs. "
                "Mientras Alfredo no firme activacion, spend permanece $0."
            ),
        }

        return {
            "vertical": ctx.vertical.value,
            "structural_health": {
                "campaigns_planned_count": len(impl_artifacts["campaigns_plan"]),
                "campaigns_ready_count": len(impl_artifacts["campaigns_plan"]) - len(not_ready),
                "platforms_allowed_count": len(impl_artifacts["platforms_allowed"]),
                "audience_archetypes_count": len(impl_artifacts["audience_archetypes"]),
                "all_paused": not active_campaigns,
                "dry_run": impl_artifacts["dry_run"],
            },
            "spend_health": spend_health,
            "hard_safeguards": impl_artifacts["hard_safeguards"],
            "warnings": warnings,
            "blockers": blockers,
            "validation_log_anchors": impl_artifacts["validation_log_anchors"],
        }


__all__ = ["PublicidadLayer"]
