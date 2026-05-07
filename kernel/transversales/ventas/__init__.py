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
        raise NotImplementedError(
            "VentasLayer.implement pendiente Sprint TRANSVERSAL-001. "
            "Requiere CRM (HubSpot) + billing (Stripe) integration. "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] integration_pattern_2026"
        )

    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        raise NotImplementedError(
            "VentasLayer.monitor pendiente Sprint TRANSVERSAL-001. "
            "Requiere event_store integration para CAC/LTV/conversion. "
            "Tag: [NEEDS_PERPLEXITY_VALIDATION] kpi_benchmark_2026"
        )


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
