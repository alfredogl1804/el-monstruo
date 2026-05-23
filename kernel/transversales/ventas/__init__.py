# kernel/transversales/ventas/__init__.py
"""
Capa Transversal: Ventas (Obj #9).

Genera recomendaciones estructurales de pricing, funnel, conversion levers,
upsell/cross-sell y retention para CADA vertical que el Monstruo
comercializa. Mirror del patron kernel.brand pero para la dimension de
ventas.

IMPORTANTE — separacion estructura vs copy:
    Esta Capa devuelve DATA ESTRUCTURAL (numero de tiers, precios numericos,
    nombres conceptuales de stages del funnel, slots de mensaje). NO devuelve
    copy final en lenguaje natural. El copy final lo llena el plugin
    `brand-voice` o se revisa por humano. Esto evita que la Capa shipee texto
    que requiera juicio de tono — gap text-irreducible declarado en
    discusion 2026-05-07 con Alfredo.

IMPORTANTE — magna validation:
    Cualquier claim de estado-del-mundo (pricing benchmarks 2026, ARPU
    industria, conversion rate por canal, costo de adquisicion vigente)
    DEBE etiquetarse con tag string `[NEEDS_PERPLEXITY_VALIDATION]` en
    `needs_validation_tags`. tools/check_perplexity_tags.py lo enforza.

Origen: AGENTS.md Regla Dura #2 (Capa 1 de las 7 Transversales),
DSC-G-002, DSC-CIP-006 (CIP es el primer producto comercial completo —
prioridad de implementacion correcta).
"""
from __future__ import annotations

from typing import Any

from kernel.transversales.base import (
    BusinessModelArchetype,
    RestrictedVerticalError,
    TransversalContext,
    TransversalLayer,
    TransversalRecommendation,
    TransversalRecommendations,
    VerticalId,
)
from kernel.transversales.ventas._canonical_constraints import (
    PRICING_CANONICAL_PER_VERTICAL,
    is_commercial,
    require_commercial,
)


class VentasLayer(TransversalLayer):
    """
    Implementacion de la Capa Ventas.

    Estado:
        diagnose       — implementado parcialmente (lee constants)
        recommend      — implementado parcialmente (genera tiers + funnel
                         desde archetype + constants; copy slots vacios)
        implement      — NotImplementedError (requiere CRM/ops integrations)
        monitor        — NotImplementedError (requiere event_store + KPI calc)

    Roadmap:
        Sprint TRANSVERSAL-001 (proxima sesion):
          - implementar `implement` con HubSpot/CRM push de pricing tiers
          - implementar `monitor` con conversion KPIs leyendo event_store
          - validar pricing tiers contra benchmarks via DSC-V-001 decorator
    """

    layer_name = "ventas"

    def diagnose(self, ctx: TransversalContext) -> dict[str, Any]:
        require_commercial(ctx.vertical)
        canonical = PRICING_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        return {
            "vertical": ctx.vertical.value,
            "archetype": ctx.archetype.value,
            "is_commercial": True,
            "has_canonical_constraints": bool(canonical),
            "canonical_constraints_count": len(canonical),
            "current_metrics_provided": bool(ctx.current_metrics),
            "deep_diagnostics_status": "pending_implementation",
        }

    def recommend(self, ctx: TransversalContext) -> TransversalRecommendations:
        require_commercial(ctx.vertical)
        canonical = PRICING_CANONICAL_PER_VERTICAL.get(ctx.vertical, {})
        recs: list[TransversalRecommendation] = []
        validation_tags: list[str] = []

        min_ticket_usd = canonical.get("min_ticket_usd")
        max_ticket_usd = canonical.get("max_ticket_usd")
        recs.append(
            TransversalRecommendation(
                layer_name="ventas",
                rule_id="ventas.pricing.tiers.structural",
                severity="must",
                value={
                    "tier_count_recommended": _tier_count_for_archetype(
                        ctx.archetype
                    ),
                    "min_ticket_usd": min_ticket_usd,
                    "max_ticket_usd": max_ticket_usd,
                    "pricing_basis": canonical.get("pricing_basis"),
                    "tier_label_slots": [
                        "tier_entry_label",
                        "tier_mid_label",
                        "tier_top_label",
                    ][: _tier_count_for_archetype(ctx.archetype)],
                },
                rationale=(
                    f"Tiers para archetype {ctx.archetype.value}. "
                    f"Min ticket honrado per canonical_constraints."
                ),
                needs_validation_tags=[
                    f"[NEEDS_PERPLEXITY_VALIDATION] pricing_benchmark_2026:"
                    f"{ctx.archetype.value}",
                ],
                source_dsc=canonical.get("source_dscs", []),
            )
        )
        validation_tags.append(
            f"[NEEDS_PERPLEXITY_VALIDATION] pricing_benchmark_2026:"
            f"{ctx.archetype.value}"
        )

        funnel_stages = _funnel_stages_for_archetype(ctx.archetype)
        recs.append(
            TransversalRecommendation(
                layer_name="ventas",
                rule_id="ventas.funnel.stages",
                severity="must",
                value={
                    "stages": funnel_stages,
                    "checkout_pattern": canonical.get(
                        "checkout_pattern", "stripe_session_webhook_canonical"
                    ),
                },
                rationale=(
                    "Funnel stages estandar para archetype + checkout "
                    "pattern canonico (DSC-LIKETICKETS-003)."
                ),
                source_dsc=["DSC-LIKETICKETS-003"]
                + canonical.get("source_dscs", []),
            )
        )

        if "geo_initial_markets" in canonical:
            recs.append(
                TransversalRecommendation(
                    layer_name="ventas",
                    rule_id="ventas.geo.initial_markets",
                    severity="must",
                    value={
                        "initial_markets": canonical["geo_initial_markets"],
                        "expansion_phase_2_markets": canonical.get(
                            "geo_expansion_phase_2", []
                        ),
                    },
                    rationale=(
                        "Restriccion geografica canonica del vertical. "
                        "Comercializacion fuera de initial_markets requiere "
                        "decision explicita."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        return TransversalRecommendations(
            layer_name="ventas",
            vertical=ctx.vertical,
            archetype=ctx.archetype,
            recommendations=recs,
            diagnostics=self.diagnose(ctx),
            aggregated_validation_tags=validation_tags,
        )

    def implement(
        self, recommendations: TransversalRecommendations
    ) -> dict[str, Any]:
        """
        Genera payloads canonicos listos para inyectar en HubSpot CRM
        (Products + Pipeline + Deals) y Stripe (Products + Prices). NO ejecuta
        llamadas a red — produce payloads validables, dry-run por defecto.

        El push real a HubSpot/Stripe queda fuera de esta funcion: lo ejecuta
        un script de operaciones bajo HITL (DSC-G-002) cuando las credenciales
        esten configuradas y Alfredo firme la operacion.

        Patron canonico HubSpot (validado magna `hubspot_api_2026`,
        validation_log id=26 vigente hasta 2026-08-09):
          - Auth: Private App access token via header
            'Authorization: Bearer <HUBSPOT_ACCESS_TOKEN>'.
          - Endpoint Products: POST /crm/v3/objects/products
          - Endpoint Deals:    POST /crm/v3/objects/deals
          - Rate limits 2026: ~150 req/10s, ~250k req/day en Marketing Hub
            Enterprise (variar por tier; metadata.full_answer tiene detalle).

        Returns dict con keys:
            vertical: str
            crm_target: 'hubspot'
            billing_target: 'stripe'
            hubspot_products_payload: list[dict]
            stripe_products_payload: list[dict]
            funnel_pipeline_stages: list[str]
            checkout_pattern: str
            dry_run: bool (True hasta firma de Alfredo via DSC-G-002)
            pending_credentials: list[str] (vacio si ambas envs presentes)
            validation_log_anchor: dict (id+claim_type+ttl del row vigente)
            validation_tags_pending: list[str]
        """
        import os

        rules = {r.rule_id: r.value for r in recommendations.recommendations}

        # 1. Pricing tiers → HubSpot Products + Stripe Products/Prices.
        # Patron canonico: payload sale con SLOTS conceptuales
        # (TITLE_SLOT, PRICE_SLOT, DESCRIPTION_SLOT). Los slots se llenan por
        # brand-voice plugin o humano antes del push real. Mismo patron SEO
        # (TITLE_SLOT, DESCRIPTION_SLOT). Aisla estructura de copy/precios
        # finales — obj #9 (Capa Transversal sin texto-irreducible).
        pricing_rule = rules.get("ventas.pricing.tiers.structural", {})
        tier_count = pricing_rule.get("tier_count_recommended", 0)
        tier_label_slots = pricing_rule.get("tier_label_slots", [])
        min_ticket_usd = pricing_rule.get("min_ticket_usd")
        max_ticket_usd = pricing_rule.get("max_ticket_usd")
        pricing_basis = pricing_rule.get("pricing_basis")

        vertical_slug = recommendations.vertical.value
        hubspot_products_payload: list[dict[str, Any]] = []
        stripe_products_payload: list[dict[str, Any]] = []

        for idx, tier_label_slot in enumerate(tier_label_slots):
            # tier_label_slot es ej. 'tier_entry_label' — lo convertimos en
            # slot template upper para que el brand-voice plugin lo llene.
            slot_upper = tier_label_slot.upper()
            name_slot = f"{{{{{slot_upper}_NAME_SLOT}}}}"
            desc_slot = f"{{{{{slot_upper}_DESCRIPTION_SLOT}}}}"
            price_slot = f"{{{{{slot_upper}_PRICE_AMOUNT_SLOT}}}}"
            currency_slot = f"{{{{{slot_upper}_CURRENCY_SLOT}}}}"
            period_slot = f"{{{{{slot_upper}_BILLING_PERIOD_SLOT}}}}"

            hubspot_products_payload.append({
                "vertical": vertical_slug,
                "tier_idx": idx,
                "tier_label_slot": tier_label_slot,
                "endpoint": "POST /crm/v3/objects/products",
                "properties": {
                    "name": name_slot,
                    "price": price_slot,
                    "description": desc_slot,
                    "hs_recurring_billing_period": period_slot,
                    "hs_sku": f"{vertical_slug}-{tier_label_slot}",
                },
                "slots_required": [
                    name_slot, price_slot, desc_slot, period_slot,
                ],
            })

            stripe_products_payload.append({
                "vertical": vertical_slug,
                "tier_idx": idx,
                "tier_label_slot": tier_label_slot,
                "product": {
                    "name": name_slot,
                    "description": desc_slot,
                    "metadata": {
                        "vertical": vertical_slug,
                        "tier_label_slot": tier_label_slot,
                    },
                },
                "price": {
                    "unit_amount_slot": price_slot,
                    "currency_slot": currency_slot,
                    "recurring_interval_slot": period_slot,
                },
                "slots_required": [
                    name_slot, price_slot, currency_slot,
                    desc_slot, period_slot,
                ],
            })

        pricing_envelope = {
            "tier_count_recommended": tier_count,
            "min_ticket_usd": min_ticket_usd,
            "max_ticket_usd": max_ticket_usd,
            "pricing_basis": pricing_basis,
        }

        # 2. Funnel pipeline stages → HubSpot deal pipeline.
        funnel_rule = rules.get("ventas.funnel.stages", {})
        funnel_pipeline_stages = funnel_rule.get("stages", [])
        checkout_pattern = funnel_rule.get(
            "checkout_pattern", "stripe_session_webhook_canonical"
        )

        # 3. Credenciales pendientes (no las leemos como valores — solo presencia).
        pending_credentials: list[str] = []
        if not os.environ.get("HUBSPOT_ACCESS_TOKEN"):
            pending_credentials.append("HUBSPOT_ACCESS_TOKEN")
        if not os.environ.get("STRIPE_SECRET_KEY"):
            pending_credentials.append("STRIPE_SECRET_KEY")

        return {
            "vertical": recommendations.vertical.value,
            "crm_target": "hubspot",
            "billing_target": "stripe",
            "pricing_envelope": pricing_envelope,
            "hubspot_products_payload": hubspot_products_payload,
            "stripe_products_payload": stripe_products_payload,
            "funnel_pipeline_stages": funnel_pipeline_stages,
            "checkout_pattern": checkout_pattern,
            "dry_run": True,
            "dry_run_reason": (
                "Push real requiere firma de Alfredo via DSC-G-002 "
                "(HITL para operaciones write-risky)."
            ),
            "pending_credentials": pending_credentials,
            "validation_log_anchor": {
                "claim_type": "hubspot_api_2026",
                "row_id": 26,
                "validator": "perplexity",
                "ttl_seconds": 7776000,
                "valid_until_iso": "2026-08-09T16:14:05Z",
            },
            "validation_tags_pending": list(
                recommendations.aggregated_validation_tags
            ),
        }

    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        """
        Health-check estructural sin red. CAC/LTV/conversion reales requieren
        Amplitude/PostHog/HubSpot Analytics y quedan en status
        'pending_credentials' hasta que Alfredo firme el wiring.

        Verifica:
          - vertical comercial (RestrictedVerticalError si no)
          - payloads structuralmente validos (tier count > 0, funnel stages > 0)
          - credenciales presentes/ausentes
          - tags Perplexity pendientes
        """
        require_commercial(ctx.vertical)
        recommendations = self.recommend(ctx)
        impl_artifacts = self.implement(recommendations)

        warnings: list[str] = []
        blockers: list[str] = []

        if not impl_artifacts["hubspot_products_payload"]:
            blockers.append(
                "No hay pricing tiers en payload — imposible push a HubSpot."
            )
        if not impl_artifacts["funnel_pipeline_stages"]:
            warnings.append(
                "Funnel pipeline stages vacios — no se puede crear deal pipeline."
            )
        if impl_artifacts["pending_credentials"]:
            warnings.append(
                f"Credenciales pendientes: "
                f"{', '.join(impl_artifacts['pending_credentials'])}. "
                f"Push real bloqueado hasta wiring + firma Alfredo."
            )
        if impl_artifacts["validation_tags_pending"]:
            warnings.append(
                f"{len(impl_artifacts['validation_tags_pending'])} tags "
                f"Perplexity pendientes de resolver via DSC-V-001."
            )

        return {
            "vertical": ctx.vertical.value,
            "structural_health": {
                "hubspot_products_count": len(
                    impl_artifacts["hubspot_products_payload"]
                ),
                "stripe_products_count": len(
                    impl_artifacts["stripe_products_payload"]
                ),
                "funnel_stages_count": len(
                    impl_artifacts["funnel_pipeline_stages"]
                ),
                "checkout_pattern": impl_artifacts["checkout_pattern"],
                "dry_run": impl_artifacts["dry_run"],
            },
            "warnings": warnings,
            "blockers": blockers,
            "cac_ltv_health": {
                "status": "pending_credentials",
                "required_envs": [
                    "HUBSPOT_ACCESS_TOKEN", "STRIPE_SECRET_KEY",
                    "AMPLITUDE_API_KEY", "POSTHOG_API_KEY",
                ],
                "note": (
                    "CAC/LTV calculation requiere event source real (Amplitude o"
                    " PostHog) + billing source (Stripe API). Pendiente wiring"
                    " — stub estructural emitido para no bloquear pipeline."
                ),
            },
            "validation_log_anchor": impl_artifacts["validation_log_anchor"],
        }


_TIER_COUNT_BY_ARCHETYPE: dict[BusinessModelArchetype, int] = {
    BusinessModelArchetype.SAAS_B2B: 3,
    BusinessModelArchetype.MARKETPLACE_SERVICES: 1,
    BusinessModelArchetype.ECOMMERCE_ARTISANAL: 1,
    BusinessModelArchetype.PROFESSIONAL_SERVICES: 3,
    BusinessModelArchetype.EDUCATION_ARTS: 3,
    BusinessModelArchetype.RESTAURANT: 1,
    BusinessModelArchetype.TOKENIZED_REAL_ESTATE: 1,
    BusinessModelArchetype.TICKETING_LIMITED_INVENTORY: 1,
    BusinessModelArchetype.REAL_ESTATE_DISTRICT: 3,
    BusinessModelArchetype.IOT_B2B_REGULATED: 3,
    BusinessModelArchetype.AI_AGENT_PLATFORM_CONSUMER: 3,
    BusinessModelArchetype.AGENT_PLATFORM_B2B: 3,
}


def _tier_count_for_archetype(arch: BusinessModelArchetype) -> int:
    return _TIER_COUNT_BY_ARCHETYPE.get(arch, 3)


_FUNNEL_STAGES_BY_ARCHETYPE: dict[BusinessModelArchetype, list[str]] = {
    BusinessModelArchetype.SAAS_B2B: [
        "awareness", "consideration", "trial", "activation",
        "expansion", "retention",
    ],
    BusinessModelArchetype.MARKETPLACE_SERVICES: [
        "discovery_search", "match_request", "trust_check",
        "transaction", "review_loop",
    ],
    BusinessModelArchetype.ECOMMERCE_ARTISANAL: [
        "discovery", "product_view", "cart", "checkout",
        "post_purchase",
    ],
    BusinessModelArchetype.TOKENIZED_REAL_ESTATE: [
        "kyc_lite", "explorar_proyectos", "mini_inversion",
        "primera_distribucion", "reinversion_loop",
    ],
    BusinessModelArchetype.TICKETING_LIMITED_INVENTORY: [
        "scarcity_alert", "select_seat", "checkout_stripe_canonical",
        "delivery_email_qr", "post_event_loop",
    ],
    BusinessModelArchetype.IOT_B2B_REGULATED: [
        "lead_b2b", "qualification_regulatory", "demo_field",
        "pilot_program", "deployment", "expansion_seats",
    ],
}


def _funnel_stages_for_archetype(arch: BusinessModelArchetype) -> list[str]:
    return _FUNNEL_STAGES_BY_ARCHETYPE.get(
        arch,
        ["awareness", "consideration", "decision", "purchase", "retention"],
    )


__all__ = ["VentasLayer"]
