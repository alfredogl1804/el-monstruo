# kernel/transversales/publicidad/_canonical_constraints.py
"""
Hard constraints per-vertical para la Capa Publicidad (DSC-G-017 enforcement).

Ad platforms permitidas, geo targeting, audience archetypes, regulatory
restrictions y disclaimers obligatorios derivados de DSCs firmes.

Origen: DSC-G-017. Texto puede ser desobedecido, codigo no.
"""
from __future__ import annotations

from kernel.transversales.base import GeoRegion, VerticalId
from kernel.transversales.ventas._canonical_constraints import (
    NON_COMMERCIAL_VERTICALS,
    is_commercial,
    require_commercial,
)


SUPPORTED_AD_PLATFORMS = {
    "meta_ads",
    "google_ads",
    "tiktok_ads",
    "linkedin_ads",
    "reddit_ads",
    "x_ads",
    "pinterest_ads",
    "youtube_ads",
}


PUBLICIDAD_CANONICAL_PER_VERTICAL: dict[VerticalId, dict] = {
    VerticalId.CIP: {
        "ad_platforms_allowed": [
            "meta_ads",
            "google_ads",
            "linkedin_ads",
        ],
        "ad_platforms_explicitly_blocked": ["tiktok_ads"],
        "ad_platforms_block_reason": (
            "Audiencia tokenizacion massmarket TikTok no se convierte "
            "a inversion real bienes raices. Re-evaluar en phase 2."
        ),
        "geo_target": GeoRegion.MX_SURESTE.value,
        "geo_target_states": ["yucatan", "quintana_roo", "campeche"],
        "audience_archetypes": [
            "professional_age_25_45_yucatan",
            "diaspora_yucateca_remittance_savers",
            "small_business_owner_excedente_capital",
            "early_adopter_tokenization_curious",
        ],
        "required_disclaimers": [
            "tokens_no_son_equity_inmueble",
            "rendimiento_no_garantizado_pasado_no_indica_futuro",
            "ticket_minimo_1_usd_acceso_democratico",
        ],
        "ad_priority_phase_1": True,
        "source_dscs": [
            "DSC-CIP-001", "DSC-CIP-002", "DSC-CIP-005", "DSC-CIP-006",
        ],
    },
    VerticalId.LIKETICKETS: {
        "ad_platforms_allowed": [
            "meta_ads",
            "google_ads",
            "tiktok_ads",
        ],
        "geo_target": GeoRegion.MX_MERIDA.value,
        "geo_target_states": ["yucatan"],
        "audience_archetypes": [
            "leones_yucatan_fan_recurrente",
            "familia_merida_entretenimiento_premium",
            "turismo_deportivo_sureste",
        ],
        "creative_angles_canonical": [
            "scarcity_zona_like_313_butacas",
            "experience_premium_vs_general",
            "evento_proximo_42_juegos_temporada",
        ],
        "ad_priority_phase_1": True,
        "source_dscs": ["DSC-LIKETICKETS-001", "DSC-LT-002"],
    },
    VerticalId.KUKULKAN_365: {
        "ad_platforms_allowed": [
            "meta_ads",
            "google_ads",
            "tiktok_ads",
        ],
        "geo_target": GeoRegion.MX_MERIDA.value,
        "geo_target_states": ["yucatan"],
        "audience_archetypes": [
            "familia_merida_entretenimiento",
            "turismo_yucatan_visitor",
            "joven_merida_entretenimiento_climatizado",
        ],
        "creative_angles_canonical": [
            "climatizado_vs_calor_extremo",
            "operacion_365_dias_siempre_abierto",
            "distrito_completo_vs_lugar_individual",
        ],
        "ad_priority_phase_1": True,
        "source_dscs": ["DSC-K365-001"],
    },
    VerticalId.BIOGUARD: {
        "ad_platforms_allowed": ["linkedin_ads"],
        "ad_platforms_explicitly_blocked": [
            "meta_ads", "tiktok_ads", "x_ads",
        ],
        "ad_platforms_block_reason": (
            "DSC-BG-PEND-001 COFEPRIS pendiente. Comercializacion MX "
            "BLOQUEADA. Solo B2B niche-targeted (LinkedIn) aceptable."
        ),
        "geo_target": GeoRegion.GLOBAL.value,
        "geo_blocked": [GeoRegion.MX_NACIONAL.value],
        "geo_blocked_reason": "DSC-BG-PEND-001 COFEPRIS pendiente",
        "audience_archetypes": [
            "hazmat_first_responder_lead",
            "forensics_lab_b2b",
            "regulatory_pilot_program_partner",
        ],
        "required_disclaimers": [
            "diagnostico_semicuantitativo_no_definitivo",
            "uso_profesional_b2b_only",
            "regulatory_status_pendiente_cofepris",
        ],
        "ad_priority_phase_1": False,
        "source_dscs": ["DSC-BG-001", "DSC-BG-PEND-001"],
    },
    VerticalId.TOP_CONTROL_PC: {
        "ad_platforms_allowed": [
            "meta_ads",
            "google_ads",
            "reddit_ads",
            "x_ads",
            "youtube_ads",
        ],
        "geo_target": GeoRegion.GLOBAL.value,
        "audience_archetypes": [
            "power_user_pc_productivity",
            "developer_automation_curious",
            "early_adopter_ai_agent",
        ],
        "creative_angles_canonical": [
            "absorcion_soberana_pc_completo",
            "delegacion_total_tareas_productividad",
            "demo_video_real_pc_control",
        ],
        "ad_priority_phase_1": False,
        "source_dscs": ["DSC-TC-001"],
    },
    VerticalId.MUNDO_DE_TATA: {
        "ad_platforms_allowed": [
            "meta_ads",
            "google_ads",
            "pinterest_ads",
        ],
        "geo_target": GeoRegion.MX_NACIONAL.value,
        "audience_archetypes": ["consumer_artisanal_premium"],
        "ad_priority_phase_1": False,
        "source_dscs": [],
    },
    VerticalId.EL_MONSTRUO_APP: {
        "ad_platforms_allowed": [
            "linkedin_ads",
            "x_ads",
            "google_ads",
            "reddit_ads",
        ],
        "geo_target": GeoRegion.GLOBAL.value,
        "audience_archetypes": [
            "founder_solo_no_dev",
            "smb_owner_quiere_negocio_digital",
            "enterprise_innovation_lab",
        ],
        "ad_priority_phase_1": False,
        "source_dscs": [],
    },
}


__all__ = [
    "PUBLICIDAD_CANONICAL_PER_VERTICAL",
    "SUPPORTED_AD_PLATFORMS",
    "is_commercial",
    "require_commercial",
    "NON_COMMERCIAL_VERTICALS",
]
