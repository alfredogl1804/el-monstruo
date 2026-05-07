# kernel/transversales/ventas/_canonical_constraints.py
"""
Hard constraints per-vertical para la Capa Ventas (DSC-G-017 enforcement).

Cada constante aqui esta derivada de un DSC firme. Tests en
tests/test_transversales_ventas_constraints.py parsean los DSCs reales y
asertean que estos valores coinciden con el texto canonico. Si alguien
cambia el DSC sin actualizar el constant (o viceversa), el test falla.

Los YAMLs en archetypes/ son DEFAULTS por archetype; estos constants
los SOBREESCRIBEN per-vertical.

Origen: DSC-G-017 (DSC-as-Contract) — texto puede ser desobedecido,
codigo no.
"""
from __future__ import annotations

from kernel.transversales.base import (
    BusinessModelArchetype,
    GeoRegion,
    RestrictedVerticalError,
    VerticalId,
)


NON_COMMERCIAL_VERTICALS: dict[VerticalId, str] = {
    VerticalId.MENA_BADUY: (
        "DSC-MB-001: operacion electoral real Merida 2027. "
        "OPSEC reforzado mandatorio. Vertical NO admite output comercial."
    ),
}


def is_commercial(vertical: VerticalId) -> bool:
    return vertical not in NON_COMMERCIAL_VERTICALS


def require_commercial(vertical: VerticalId) -> None:
    if not is_commercial(vertical):
        reason = NON_COMMERCIAL_VERTICALS[vertical]
        raise RestrictedVerticalError(
            f"Vertical '{vertical.value}' NO es comercial. {reason}"
        )


VERTICAL_ARCHETYPE: dict[VerticalId, BusinessModelArchetype] = {
    VerticalId.CIP: BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
    VerticalId.LIKETICKETS: BusinessModelArchetype.TICKETING_LIMITED_INVENTORY,
    VerticalId.KUKULKAN_365: BusinessModelArchetype.REAL_ESTATE_DISTRICT,
    VerticalId.BIOGUARD: BusinessModelArchetype.IOT_B2B_REGULATED,
    VerticalId.TOP_CONTROL_PC: BusinessModelArchetype.AI_AGENT_PLATFORM_CONSUMER,
    VerticalId.MUNDO_DE_TATA: BusinessModelArchetype.ECOMMERCE_ARTISANAL,
    VerticalId.EL_MONSTRUO_APP: BusinessModelArchetype.AGENT_PLATFORM_B2B,
}


PRICING_CANONICAL_PER_VERTICAL: dict[VerticalId, dict] = {
    VerticalId.CIP: {
        "min_ticket_usd": 1.00,
        "max_ticket_usd": None,
        "pricing_basis": "investment_amount_per_token",
        "propiedad_nunca_se_enajena": True,
        "blockchain": "polygon",
        "token_standard": "ERC-3643",
        "geo_initial_markets": [
            GeoRegion.MX_SURESTE.value,
            "yucatan",
            "quintana_roo",
            "campeche",
        ],
        "geo_expansion_phase_2": [GeoRegion.MX_NACIONAL.value],
        "checkout_pattern": "stripe_session_webhook_canonical",
        "es_primer_producto_monstruo": True,
        "source_dscs": [
            "DSC-CIP-001",
            "DSC-CIP-002",
            "DSC-CIP-003",
            "DSC-CIP-004",
            "DSC-CIP-005",
            "DSC-CIP-006",
            "DSC-LIKETICKETS-003",
        ],
    },
    VerticalId.LIKETICKETS: {
        "min_ticket_usd": None,
        "max_ticket_usd": None,
        "pricing_basis": "per_seat_per_event",
        "inventario_piloto_butacas": 313,
        "eventos_piloto": 42,
        "zona_canonica": "zona_like_kukulkan",
        "stack_canonical": {
            "frontend": "vite_react_typescript_tailwind",
            "backend": "trpc_express",
            "db": "tidb_cloud_mysql_compatible",
            "payments": "stripe_test_mode_initial",
            "deploy": "railway_main_branch_auto",
        },
        "checkout_pattern": "stripe_session_webhook_canonical",
        "checkout_pattern_componentes": [
            "stripe_session_create",
            "webhook_checkout_session_completed",
            "confirmSeatsForOrder_db_write",
            "email_resend_confirmation",
            "conflict_handling_post_pay",
        ],
        "source_dscs": [
            "DSC-LIKETICKETS-001",
            "DSC-LIKETICKETS-003",
            "DSC-LT-002",
        ],
    },
    VerticalId.KUKULKAN_365: {
        "min_ticket_usd": None,
        "max_ticket_usd": None,
        "pricing_basis": "mixed_ticket_lease_concession",
        "ubicacion_geografica_unica": "merida",
        "operacion_anual_dias": 365,
        "piloto_comercial": "zona_like_via_liketickets",
        "checkout_pattern": "stripe_session_webhook_canonical",
        "source_dscs": ["DSC-K365-001", "DSC-K365-002"],
    },
    VerticalId.BIOGUARD: {
        "min_ticket_usd": None,
        "max_ticket_usd": None,
        "pricing_basis": "hardware_unit_plus_saas_subscription",
        "samples_supported": ["saliva", "hisopo_dermico", "sangre_capilar"],
        "diagnosis_type": "semicuantitativo",
        "regulatory_blocker": "cofepris_pending",
        "comercializacion_mx_permitida": False,
        "source_dscs": ["DSC-BG-001", "DSC-BG-PEND-001"],
    },
    VerticalId.TOP_CONTROL_PC: {
        "min_ticket_usd": None,
        "max_ticket_usd": None,
        "pricing_basis": "subscription_plus_usage",
        "modelo_operacion": "absorcion_soberana_pc_completo",
        "checkout_pattern": "stripe_session_webhook_canonical",
        "source_dscs": ["DSC-TC-001"],
    },
    VerticalId.MUNDO_DE_TATA: {
        "min_ticket_usd": None,
        "max_ticket_usd": None,
        "pricing_basis": "per_sku",
        "checkout_pattern": "stripe_session_webhook_canonical",
        "source_dscs": [],
    },
    VerticalId.EL_MONSTRUO_APP: {
        "min_ticket_usd": None,
        "max_ticket_usd": None,
        "pricing_basis": "subscription_per_seat_b2b",
        "source_dscs": [],
    },
}


__all__ = [
    "NON_COMMERCIAL_VERTICALS",
    "PRICING_CANONICAL_PER_VERTICAL",
    "VERTICAL_ARCHETYPE",
    "is_commercial",
    "require_commercial",
]
