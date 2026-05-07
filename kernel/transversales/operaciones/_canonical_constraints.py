"""Hard constraints per-vertical para Capa Operaciones (DSC-G-017)."""
from __future__ import annotations
from kernel.transversales.base import GeoRegion, VerticalId
from kernel.transversales.ventas._canonical_constraints import (
    NON_COMMERCIAL_VERTICALS, is_commercial, require_commercial,
)

SUPPORTED_SUPPORT_CHANNELS = {
    "email_async", "chat_live_business_hours", "chat_live_24x7",
    "phone_business_hours", "phone_24x7", "in_app_messaging",
    "whatsapp_business", "knowledge_base_self_serve", "community_forum",
}

SUPPORTED_FULFILLMENT_PATTERNS = {
    "digital_delivery_instant", "stripe_session_webhook_canonical",
    "escrow_pre_release", "physical_shipping_courier", "pickup_in_person",
    "saas_subscription_provisioning", "blockchain_token_mint_polygon",
    "hardware_dispatch_b2b",
}

OPERACIONES_CANONICAL_PER_VERTICAL: dict[VerticalId, dict] = {
    VerticalId.CIP: {
        "support_channels": [
            "in_app_messaging", "email_async", "whatsapp_business",
            "knowledge_base_self_serve",
        ],
        "support_sla_first_response_hours": 4,
        "support_business_hours_timezone": "America/Merida",
        "fulfillment_patterns": [
            "stripe_session_webhook_canonical",
            "blockchain_token_mint_polygon",
        ],
        "regulatory_blockers": ["figura_legal_fideicomiso_sapi_sofom_pendiente"],
        "operations_can_launch_mx_today": False,
        "operations_blocker_reason": "DSC-CIP-PEND-001 figura legal pendiente",
        "prohibited_operations": [
            "venta_directa_inmueble_subyacente",
            "transferencia_propiedad_a_token_holder",
        ],
        "source_dscs": [
            "DSC-CIP-001", "DSC-CIP-002", "DSC-CIP-006", "DSC-CIP-PEND-001",
        ],
    },
    VerticalId.LIKETICKETS: {
        "support_channels": [
            "in_app_messaging", "email_async", "chat_live_business_hours",
            "whatsapp_business",
        ],
        "support_sla_first_response_hours": 1,
        "support_business_hours_timezone": "America/Merida",
        "fulfillment_patterns": ["stripe_session_webhook_canonical"],
        "fulfillment_components_required": [
            "stripe_session_create",
            "webhook_checkout_session_completed",
            "confirmSeatsForOrder_db_write",
            "email_resend_confirmation_qr_ticket",
            "conflict_handling_post_pay_operacional",
        ],
        "inventory_strategy": "limited_inventory_with_holds_pre_pay",
        "inventory_canonical_count": 313,
        "operations_can_launch_mx_today": True,
        "source_dscs": [
            "DSC-LIKETICKETS-001", "DSC-LIKETICKETS-003", "DSC-LT-002",
        ],
    },
    VerticalId.KUKULKAN_365: {
        "support_channels": [
            "phone_24x7", "chat_live_24x7", "in_app_messaging",
            "knowledge_base_self_serve",
        ],
        "support_sla_first_response_hours": 0.5,
        "support_24_7_required": True,
        "support_business_hours_timezone": "America/Merida",
        "fulfillment_patterns": [
            "pickup_in_person", "stripe_session_webhook_canonical",
        ],
        "operations_can_launch_mx_today": True,
        "source_dscs": ["DSC-K365-001"],
    },
    VerticalId.BIOGUARD: {
        "support_channels": [
            "phone_business_hours", "email_async", "knowledge_base_self_serve",
        ],
        "support_sla_first_response_hours": 24,
        "support_business_hours_timezone": "America/Mexico_City",
        "fulfillment_patterns": [
            "hardware_dispatch_b2b", "saas_subscription_provisioning",
        ],
        "regulatory_blockers": ["cofepris_pendiente"],
        "operations_can_launch_mx_today": False,
        "operations_blocker_reason": "DSC-BG-PEND-001 COFEPRIS pendiente",
        "regulatory_ops_post_approval": [
            "cofepris_quarterly_reporting",
            "adverse_event_reporting_24h",
            "device_serial_traceability",
        ],
        "source_dscs": ["DSC-BG-001", "DSC-BG-PEND-001"],
    },
    VerticalId.TOP_CONTROL_PC: {
        "support_channels": [
            "in_app_messaging", "email_async", "community_forum",
            "knowledge_base_self_serve",
        ],
        "support_sla_first_response_hours": 12,
        "support_business_hours_timezone": "UTC",
        "fulfillment_patterns": [
            "saas_subscription_provisioning", "digital_delivery_instant",
        ],
        "operations_can_launch_mx_today": True,
        "source_dscs": ["DSC-TC-001"],
    },
    VerticalId.MUNDO_DE_TATA: {
        "support_channels": [
            "whatsapp_business", "email_async", "in_app_messaging",
        ],
        "support_sla_first_response_hours": 24,
        "support_business_hours_timezone": "America/Mexico_City",
        "fulfillment_patterns": [
            "stripe_session_webhook_canonical", "physical_shipping_courier",
        ],
        "operations_can_launch_mx_today": True,
        "source_dscs": [],
    },
    VerticalId.EL_MONSTRUO_APP: {
        "support_channels": [
            "in_app_messaging", "email_async", "knowledge_base_self_serve",
            "community_forum",
        ],
        "support_sla_first_response_hours": 8,
        "support_business_hours_timezone": "UTC",
        "fulfillment_patterns": [
            "saas_subscription_provisioning", "digital_delivery_instant",
        ],
        "operations_can_launch_mx_today": True,
        "source_dscs": [],
    },
}

__all__ = [
    "OPERACIONES_CANONICAL_PER_VERTICAL", "SUPPORTED_SUPPORT_CHANNELS",
    "SUPPORTED_FULFILLMENT_PATTERNS", "is_commercial", "require_commercial",
    "NON_COMMERCIAL_VERTICALS",
]
