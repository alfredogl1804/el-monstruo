"""Hard constraints per-vertical para Capa Tendencias (DSC-G-017)."""
from __future__ import annotations
from kernel.transversales.base import GeoRegion, VerticalId
from kernel.transversales.ventas._canonical_constraints import (
    NON_COMMERCIAL_VERTICALS, is_commercial, require_commercial,
)

SUPPORTED_DATA_SOURCES = {
    "blockchain_analytics", "real_estate_market_reports", "regulatory_feeds",
    "events_calendar", "sports_leagues_feeds", "social_trends",
    "tourism_data", "weather_feeds", "industry_reports_b2b", "tech_news",
    "github_trending", "ai_research_feeds", "ecommerce_trends",
    "enterprise_tech_news", "competitor_pricing_scrape", "search_trend_signals",
}

MONITORING_CADENCES = {"real_time", "hourly", "daily", "weekly", "monthly"}

TENDENCIAS_CANONICAL_PER_VERTICAL: dict[VerticalId, dict] = {
    VerticalId.CIP: {
        "data_sources": [
            "blockchain_analytics", "real_estate_market_reports",
            "regulatory_feeds", "competitor_pricing_scrape",
            "search_trend_signals",
        ],
        "monitoring_cadence": "daily",
        "monitoring_cadence_critical_signals": "real_time",
        "geo_focus": GeoRegion.MX_SURESTE.value,
        "signal_types_priorizados": [
            "tokenizacion_real_estate_competitor_launch",
            "regulatory_change_cnbv_sat_polygon",
            "market_yield_real_estate_yucatan",
            "diaspora_yucateca_remittance_volume",
        ],
        "source_dscs": ["DSC-CIP-004", "DSC-CIP-005", "DSC-CIP-006"],
    },
    VerticalId.LIKETICKETS: {
        "data_sources": [
            "events_calendar", "sports_leagues_feeds", "social_trends",
            "tourism_data", "weather_feeds",
        ],
        "monitoring_cadence": "real_time",
        "geo_focus": GeoRegion.MX_MERIDA.value,
        "signal_types_priorizados": [
            "evento_proximo_demand_signal",
            "ticket_secondary_market_pricing",
            "fan_sentiment_leones_yucatan",
            "evento_cancellation_or_reschedule",
        ],
        "source_dscs": ["DSC-LT-002"],
    },
    VerticalId.KUKULKAN_365: {
        "data_sources": [
            "tourism_data", "events_calendar", "weather_feeds",
            "social_trends",
        ],
        "monitoring_cadence": "daily",
        "geo_focus": GeoRegion.MX_MERIDA.value,
        "signal_types_priorizados": [
            "tourism_seasonality_yucatan",
            "evento_externo_competidor_distrito",
            "weather_extreme_heat_demand_climatizado",
            "merida_economic_indicator",
        ],
        "source_dscs": ["DSC-K365-001"],
    },
    VerticalId.BIOGUARD: {
        "data_sources": [
            "regulatory_feeds", "industry_reports_b2b", "ai_research_feeds",
        ],
        "monitoring_cadence": "weekly",
        "monitoring_cadence_critical_signals": "real_time",
        "geo_focus": GeoRegion.GLOBAL.value,
        "signal_types_priorizados": [
            "cofepris_regulatory_update",
            "competitor_iot_drug_detection_launch",
            "raman_spectroscopy_research_advance",
            "first_responder_b2b_pilot_opportunity",
        ],
        "source_dscs": ["DSC-BG-001", "DSC-BG-PEND-001"],
    },
    VerticalId.TOP_CONTROL_PC: {
        "data_sources": [
            "tech_news", "github_trending", "ai_research_feeds",
            "social_trends",
        ],
        "monitoring_cadence": "real_time",
        "geo_focus": GeoRegion.GLOBAL.value,
        "signal_types_priorizados": [
            "competitor_ai_agent_consumer_launch",
            "os_pc_capability_change",
            "model_capability_breakthrough_pc_control",
            "regulatory_ai_pc_consumer",
        ],
        "source_dscs": ["DSC-TC-001"],
    },
    VerticalId.MUNDO_DE_TATA: {
        "data_sources": [
            "ecommerce_trends", "social_trends", "competitor_pricing_scrape",
        ],
        "monitoring_cadence": "daily",
        "geo_focus": GeoRegion.MX_NACIONAL.value,
        "signal_types_priorizados": [
            "ecommerce_artisanal_trend",
            "competitor_sku_pricing",
            "social_artisanal_demand",
        ],
        "source_dscs": [],
    },
    VerticalId.EL_MONSTRUO_APP: {
        "data_sources": [
            "tech_news", "ai_research_feeds", "enterprise_tech_news",
            "github_trending",
        ],
        "monitoring_cadence": "daily",
        "geo_focus": GeoRegion.GLOBAL.value,
        "signal_types_priorizados": [
            "competitor_agent_platform_launch",
            "model_capability_breakthrough",
            "enterprise_ai_adoption_signal",
        ],
        "source_dscs": [],
    },
}

__all__ = [
    "TENDENCIAS_CANONICAL_PER_VERTICAL", "SUPPORTED_DATA_SOURCES",
    "MONITORING_CADENCES", "is_commercial", "require_commercial",
    "NON_COMMERCIAL_VERTICALS",
]
