"""Hard constraints per-vertical para Capa Finanzas (DSC-G-017)."""
from __future__ import annotations
from kernel.transversales.base import GeoRegion, VerticalId
from kernel.transversales.ventas._canonical_constraints import (
    NON_COMMERCIAL_VERTICALS, is_commercial, require_commercial,
)

SUPPORTED_REVENUE_MODELS = {
    "subscription_recurring", "transactional_per_event",
    "transactional_per_token", "commission_marketplace",
    "hardware_sale_one_time", "hardware_plus_saas_combo",
    "lease_recurring", "concession_revenue_share", "freemium_to_paid",
}

SUPPORTED_TAX_FRAMEWORKS = {
    "mx_pyme_general", "mx_isr_personas_fisicas", "mx_iva_16",
    "mx_securities_cnbv", "mx_medical_devices_cofepris",
    "us_state_local", "global_revenue_recognition_ifrs",
    "global_us_gaap_asc606",
}

FINANZAS_CANONICAL_PER_VERTICAL: dict[VerticalId, dict] = {
    VerticalId.CIP: {
        "revenue_models": ["transactional_per_token", "commission_marketplace"],
        "revenue_recognition_pattern": "deferred_until_distribution_event",
        "min_unit_revenue_usd": 0.01,
        "tax_frameworks_candidate": ["mx_securities_cnbv", "mx_iva_16"],
        "tax_framework_pending_decision": True,
        "tax_blocker_reason": "DSC-CIP-PEND-001 figura legal SAPI/SOFOM/Fideicomiso pendiente",
        "distribution_method_pending": True,
        "distribution_methods_candidate": [
            "usdc_stablecoin_on_chain_polygon",
            "fiat_mxn_spei_off_chain",
            "split_per_holder_preference",
        ],
        "compliance_reporting": [
            "on_chain_token_flow_polygon_erc3643_audit",
            "kyc_aml_per_holder",
            "cnbv_reporting_post_resolucion_figura_legal",
        ],
        "source_dscs": [
            "DSC-CIP-001", "DSC-CIP-002", "DSC-CIP-004", "DSC-CIP-PEND-001",
        ],
    },
    VerticalId.LIKETICKETS: {
        "revenue_models": ["transactional_per_event", "commission_marketplace"],
        "revenue_recognition_pattern": "recognized_at_event_attendance",
        "min_unit_revenue_usd": None,
        "tax_frameworks_candidate": ["mx_pyme_general", "mx_iva_16"],
        "tax_framework_pending_decision": False,
        "unit_economics_tracked": [
            "revenue_per_seat_per_event",
            "average_ticket_price_zona_like",
            "fill_rate_42_games_temporada",
            "cac_per_seat_sold",
        ],
        "compliance_reporting": ["cfdi_4_per_transaction"],
        "source_dscs": ["DSC-LIKETICKETS-001", "DSC-LT-002"],
    },
    VerticalId.KUKULKAN_365: {
        "revenue_models": [
            "lease_recurring", "concession_revenue_share",
            "transactional_per_event",
        ],
        "revenue_recognition_pattern": "lease_straight_line_plus_event_at_attendance",
        "min_unit_revenue_usd": None,
        "tax_frameworks_candidate": ["mx_pyme_general", "mx_iva_16"],
        "tax_framework_pending_decision": False,
        "unit_economics_tracked": [
            "lease_revenue_per_local_per_month",
            "concession_revenue_per_brand",
            "occupancy_rate_distrito_365_dias",
            "cost_climatizacion_per_dia",
        ],
        "source_dscs": ["DSC-K365-001"],
    },
    VerticalId.BIOGUARD: {
        "revenue_models": ["hardware_plus_saas_combo", "subscription_recurring"],
        "revenue_recognition_pattern": "hardware_at_delivery_plus_saas_recurring",
        "min_unit_revenue_usd": None,
        "tax_frameworks_candidate": [
            "mx_medical_devices_cofepris", "mx_iva_16",
        ],
        "tax_framework_pending_decision": True,
        "tax_blocker_reason": "DSC-BG-PEND-001 COFEPRIS pendiente",
        "revenue_can_be_recognized_mx_today": False,
        "compliance_reporting": [
            "cofepris_quarterly_post_aprobacion",
            "device_serial_traceability_per_unit",
        ],
        "source_dscs": ["DSC-BG-001", "DSC-BG-PEND-001"],
    },
    VerticalId.TOP_CONTROL_PC: {
        "revenue_models": ["subscription_recurring", "freemium_to_paid"],
        "revenue_recognition_pattern": "subscription_pro_rata_per_period",
        "min_unit_revenue_usd": 0,
        "tax_frameworks_candidate": [
            "global_us_gaap_asc606", "global_revenue_recognition_ifrs",
        ],
        "tax_framework_pending_decision": False,
        "unit_economics_tracked": [
            "mrr_per_paying_user",
            "free_to_paid_conversion_rate",
            "churn_per_cohort",
            "cac_per_paying_user",
        ],
        "source_dscs": ["DSC-TC-001"],
    },
    VerticalId.MUNDO_DE_TATA: {
        "revenue_models": ["transactional_per_event"],
        "revenue_recognition_pattern": "recognized_at_shipment",
        "min_unit_revenue_usd": None,
        "tax_frameworks_candidate": ["mx_pyme_general", "mx_iva_16"],
        "tax_framework_pending_decision": False,
        "compliance_reporting": ["cfdi_4_per_transaction"],
        "source_dscs": [],
    },
    VerticalId.EL_MONSTRUO_APP: {
        "revenue_models": ["subscription_recurring"],
        "revenue_recognition_pattern": "subscription_pro_rata_per_period",
        "min_unit_revenue_usd": None,
        "tax_frameworks_candidate": ["global_us_gaap_asc606"],
        "tax_framework_pending_decision": False,
        "unit_economics_tracked": [
            "arr_per_seat", "expansion_revenue_per_account", "logo_churn",
        ],
        "source_dscs": [],
    },
}

__all__ = [
    "FINANZAS_CANONICAL_PER_VERTICAL", "SUPPORTED_REVENUE_MODELS",
    "SUPPORTED_TAX_FRAMEWORKS", "is_commercial", "require_commercial",
    "NON_COMMERCIAL_VERTICALS",
]
