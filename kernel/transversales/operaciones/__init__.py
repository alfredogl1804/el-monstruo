"""Capa Transversal: Administracion y Operaciones (Obj #9)."""

from __future__ import annotations

from typing import Any

from kernel.transversales.base import (
    RestrictedVerticalError,
    TransversalContext,
    TransversalLayer,
    TransversalRecommendation,
    TransversalRecommendations,
)
from kernel.transversales.operaciones._canonical_constraints import (
    OPERACIONES_CANONICAL_PER_VERTICAL,
    SUPPORTED_FULFILLMENT_PATTERNS,
    SUPPORTED_SUPPORT_CHANNELS,
    is_commercial,
    require_commercial,
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
            "operations_can_launch_mx_today": canonical.get("operations_can_launch_mx_today", True),
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
            recs.append(
                TransversalRecommendation(
                    layer_name="operaciones",
                    rule_id="operaciones.support.channels",
                    severity="must",
                    value={
                        "channels": channels,
                        "sla_first_response_hours": canonical.get("support_sla_first_response_hours"),
                        "support_24_7_required": canonical.get("support_24_7_required", False),
                        "timezone": canonical.get("support_business_hours_timezone", "UTC"),
                    },
                    rationale=(
                        "Support channels y SLA derivados del archetype y constraints "
                        "del vertical (DSC-K365-001 365 dias)."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        fulfillment = canonical.get("fulfillment_patterns", [])
        if fulfillment:
            recs.append(
                TransversalRecommendation(
                    layer_name="operaciones",
                    rule_id="operaciones.fulfillment.patterns",
                    severity="must",
                    value={
                        "patterns": fulfillment,
                        "components_required": canonical.get("fulfillment_components_required", []),
                    },
                    rationale=(
                        "Fulfillment patterns canonicos. DSC-LIKETICKETS-003 declara "
                        "stripe_session_webhook_canonical replicable."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        inventory_strategy = canonical.get("inventory_strategy")
        if inventory_strategy:
            recs.append(
                TransversalRecommendation(
                    layer_name="operaciones",
                    rule_id="operaciones.inventory.strategy",
                    severity="must",
                    value={
                        "strategy": inventory_strategy,
                        "canonical_count": canonical.get("inventory_canonical_count"),
                    },
                    rationale="Inventory strategy derivada de DSC del vertical.",
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        blockers = canonical.get("regulatory_blockers", [])
        prohibited = canonical.get("prohibited_operations", [])
        if blockers or prohibited:
            recs.append(
                TransversalRecommendation(
                    layer_name="operaciones",
                    rule_id="operaciones.regulatory.gates",
                    severity="must",
                    value={
                        "regulatory_blockers": blockers,
                        "prohibited_operations": prohibited,
                        "operations_can_launch_mx_today": canonical.get("operations_can_launch_mx_today", True),
                        "blocker_reason": canonical.get("operations_blocker_reason"),
                        "regulatory_ops_post_approval": canonical.get("regulatory_ops_post_approval", []),
                    },
                    rationale=(
                        "Regulatory gates duros derivados de DSCs (CIP fideicomiso, BG COFEPRIS, etc). Bloqueantes."
                    ),
                    source_dsc=canonical.get("source_dscs", []),
                )
            )

        validation_tags.append(f"[NEEDS_PERPLEXITY_VALIDATION] regulatory_landscape_2026:{ctx.vertical.value}")

        return TransversalRecommendations(
            layer_name="operaciones",
            vertical=ctx.vertical,
            archetype=ctx.archetype,
            recommendations=recs,
            diagnostics=self.diagnose(ctx),
            aggregated_validation_tags=validation_tags,
        )

    def implement(self, recommendations: TransversalRecommendations) -> dict[str, Any]:
        """
        Genera plan canonico de operaciones:
        - helpdesk_payload por canal (Intercom / Front / Zendesk stubs con
          OAuth scope + endpoints REST oficiales).
        - fulfillment_pipeline canonico.
        - regulatory_gates duros (operations_can_launch_mx_today flag).
        - sla_thresholds_seconds derivado de support_sla_first_response_hours.

        Sin red. Push real (creacion de tickets, registro SLA) requiere HITL.
        """
        import os

        rules = {r.rule_id: r.value for r in recommendations.recommendations}
        support_rule = rules.get("operaciones.support.channels", {})
        fulfillment_rule = rules.get("operaciones.fulfillment.patterns", {})
        regulatory_rule = rules.get("operaciones.regulatory.gates", {})
        inventory_rule = rules.get("operaciones.inventory.strategy", {})

        channels = support_rule.get("channels", [])
        sla_hours = support_rule.get("sla_first_response_hours")
        sla_seconds = (sla_hours or 0) * 3600 if sla_hours else None

        # Mapeo canonico support_channel -> helpdesk_target.
        helpdesk_target_map = {
            "chat_web": "intercom",
            "chat_widget": "intercom",
            "email": "front",
            "whatsapp": "intercom",
            "phone": "front",
            "sms": "twilio",
            "discord": "discord_bot",
            "telegram": "telegram_bot",
            "web_form": "front",
            "in_app": "intercom",
        }

        # Endpoints REST canonicos per helpdesk (validados magna
        # helpdesk_api_2026, validation_log id=32).
        helpdesk_endpoints = {
            "intercom": {
                "create_conversation": "POST https://api.intercom.io/conversations",
                "get_conversation_metrics": "GET https://api.intercom.io/conversations/{id}",
                "oauth_scope": "read_conversations,write_conversations",
                "env_required": ["INTERCOM_ACCESS_TOKEN"],
            },
            "front": {
                "create_conversation": "POST https://api2.frontapp.com/inboxes/{inbox_id}/imports",
                "get_conversation_metrics": "GET https://api2.frontapp.com/conversations/{id}",
                "oauth_scope": "shared:*",
                "env_required": ["FRONT_API_TOKEN", "FRONT_INBOX_ID"],
            },
            "twilio": {
                "create_conversation": "POST https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                "oauth_scope": "basic_auth",
                "env_required": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"],
            },
            "discord_bot": {
                "create_conversation": "POST https://discord.com/api/v10/channels/{id}/messages",
                "env_required": ["DISCORD_BOT_TOKEN"],
            },
            "telegram_bot": {
                "create_conversation": "POST https://api.telegram.org/bot{token}/sendMessage",
                "env_required": ["TELEGRAM_BOT_TOKEN"],
            },
        }

        helpdesk_plan: list[dict[str, Any]] = []
        all_pending_envs: set[str] = set()
        for ch in channels:
            target = helpdesk_target_map.get(ch, "intercom")
            ep = helpdesk_endpoints.get(target, {})
            req_envs = ep.get("env_required", [])
            pending = [e for e in req_envs if not os.environ.get(e)]
            all_pending_envs.update(pending)
            helpdesk_plan.append(
                {
                    "channel": ch,
                    "helpdesk_target": target,
                    "endpoints": ep,
                    "required_envs": req_envs,
                    "pending_envs": pending,
                    "ready": not pending,
                }
            )

        can_launch = regulatory_rule.get("operations_can_launch_mx_today", True)
        regulatory_blockers = regulatory_rule.get("regulatory_blockers", [])
        prohibited = regulatory_rule.get("prohibited_operations", [])

        return {
            "vertical": recommendations.vertical.value,
            "helpdesk_plan": helpdesk_plan,
            "sla_first_response_hours": sla_hours,
            "sla_first_response_seconds": sla_seconds,
            "support_24_7_required": support_rule.get("support_24_7_required", False),
            "timezone": support_rule.get("timezone", "UTC"),
            "fulfillment_patterns": fulfillment_rule.get("patterns", []),
            "fulfillment_components_required": fulfillment_rule.get("components_required", []),
            "inventory_strategy": inventory_rule.get("strategy"),
            "regulatory_gates": {
                "operations_can_launch_mx_today": can_launch,
                "regulatory_blockers": regulatory_blockers,
                "prohibited_operations": prohibited,
                "blocker_reason": regulatory_rule.get("blocker_reason"),
                "post_approval_ops": regulatory_rule.get("regulatory_ops_post_approval", []),
            },
            "pending_envs": sorted(all_pending_envs),
            "dry_run": True,
            "dry_run_reason": (
                "Push real (crear tickets, registrar SLA) requiere firma de "
                "Alfredo via DSC-G-002 (HITL para operaciones write-risky)."
            ),
            "validation_log_anchors": [
                {"claim_type": "helpdesk_api_2026", "row_id": 32},
                {
                    "claim_type": f"regulatory_landscape_2026:{recommendations.vertical.value}",
                    "row_id_hint": 33,
                },
            ],
            "validation_tags_pending": list(recommendations.aggregated_validation_tags),
        }

    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        """
        Health-check estructural + sla_health canonico.

        Sin red. Stub de first_response_p50/p95 desde event_store si esta
        inyectado; sino, status='pending_storage_injection'.
        """
        require_commercial(ctx.vertical)
        recommendations = self.recommend(ctx)
        impl_artifacts = self.implement(recommendations)

        warnings: list[str] = []
        blockers: list[str] = []

        # Regulatory gates: si no puede launch, es BLOCKER duro.
        gates = impl_artifacts["regulatory_gates"]
        if not gates["operations_can_launch_mx_today"]:
            blockers.append(
                f"Operations NO pueden launch MX hoy: {gates.get('blocker_reason') or '<sin razon documentada>'}."
            )

        not_ready = [c for c in impl_artifacts["helpdesk_plan"] if not c["ready"]]
        if not_ready:
            warnings.append(
                f"{len(not_ready)} de {len(impl_artifacts['helpdesk_plan'])} "
                f"canales no estan ready (faltan envs: "
                f"{', '.join(impl_artifacts['pending_envs'])})."
            )
        if impl_artifacts["validation_tags_pending"]:
            warnings.append(
                f"{len(impl_artifacts['validation_tags_pending'])} tags Perplexity pendientes via DSC-V-001."
            )

        sla_health = {
            "sla_first_response_seconds": impl_artifacts["sla_first_response_seconds"],
            "first_response_p50_observed": None,
            "first_response_p95_observed": None,
            "status": "pending_storage_injection",
            "note": (
                "first_response observado requiere inyectar storage Supabase "
                "y tabla support_tickets futura (no parte de TRANSVERSAL-001)."
            ),
        }

        return {
            "vertical": ctx.vertical.value,
            "structural_health": {
                "helpdesk_channels_count": len(impl_artifacts["helpdesk_plan"]),
                "helpdesk_channels_ready_count": (len(impl_artifacts["helpdesk_plan"]) - len(not_ready)),
                "fulfillment_patterns_count": len(impl_artifacts["fulfillment_patterns"]),
                "can_launch_mx_today": gates["operations_can_launch_mx_today"],
                "dry_run": impl_artifacts["dry_run"],
            },
            "sla_health": sla_health,
            "regulatory_gates": gates,
            "warnings": warnings,
            "blockers": blockers,
            "validation_log_anchors": impl_artifacts["validation_log_anchors"],
        }


__all__ = ["OperacionesLayer"]
