# kernel/transversales/seo/_canonical_constraints.py
"""
Hard constraints per-vertical para la Capa SEO (DSC-G-017 enforcement).

Schema.org types, hreflang, geo targeting, regulatory disclosure flags y
restricciones de robots/indexing derivadas de DSCs firmes per vertical.

Tests en tests/test_transversales_seo_constraints.py parsean DSCs reales y
asertean que estos valores coinciden con texto canonico.

Origen: DSC-G-017 (DSC-as-Contract). Texto puede ser desobedecido, codigo no.
"""
from __future__ import annotations

from kernel.transversales.base import GeoRegion, VerticalId
from kernel.transversales.ventas._canonical_constraints import (
    NON_COMMERCIAL_VERTICALS,
    is_commercial,
    require_commercial,
)


SEO_CANONICAL_PER_VERTICAL: dict[VerticalId, dict] = {
    VerticalId.CIP: {
        "schema_org_types": [
            "InvestmentOrInvestmentScheme",
            "RealEstateListing",
        ],
        "geo_target": GeoRegion.MX_SURESTE.value,
        "geo_target_states": ["yucatan", "quintana_roo", "campeche"],
        "hreflang": ["es-MX"],
        "hreflang_expansion_phase_2": ["es-MX", "es-419"],
        "robots_indexable": True,
        "required_disclosures": [
            "tokens_no_son_equity_inmueble",
            "rendimiento_no_garantizado",
            "blockchain_polygon_erc3643",
        ],
        "url_pattern_template": "/proyectos/{slug-proyecto}/",
        "canonical_url_strategy": "self_canonical_per_project",
        "source_dscs": [
            "DSC-CIP-001",
            "DSC-CIP-005",
            "DSC-CIP-006",
        ],
    },
    VerticalId.LIKETICKETS: {
        "schema_org_types": ["Event", "Product"],
        "geo_target": GeoRegion.MX_MERIDA.value,
        "geo_target_states": ["yucatan"],
        "hreflang": ["es-MX"],
        "robots_indexable": True,
        "required_schema_fields_event": [
            "name",
            "startDate",
            "location.address",
            "offers.price",
            "offers.availability",
            "offers.url",
        ],
        "ssr_required_for_event_pages": True,
        "url_pattern_template": "/eventos/{slug-equipo}/{fecha}/{slug-evento}/",
        "canonical_url_strategy": "self_canonical_per_event",
        "source_dscs": [
            "DSC-LIKETICKETS-001",
            "DSC-LT-002",
        ],
    },
    VerticalId.KUKULKAN_365: {
        "schema_org_types": [
            "EntertainmentBusiness",
            "Place",
            "LocalBusiness",
        ],
        "geo_target": GeoRegion.MX_MERIDA.value,
        "geo_target_states": ["yucatan"],
        "hreflang": ["es-MX"],
        "robots_indexable": True,
        "differentiator_keywords": [
            "365_dias",
            "climatizado",
            "merida_yucatan",
            "distrito_entretenimiento",
        ],
        "url_pattern_template": "/{slug-zona}/",
        "canonical_url_strategy": "self_canonical",
        "source_dscs": ["DSC-K365-001", "DSC-K365-002"],
    },
    VerticalId.BIOGUARD: {
        "schema_org_types": ["MedicalDevice", "Product"],
        "geo_target": GeoRegion.MX_NACIONAL.value,
        "hreflang": ["es-MX", "en-US"],
        "robots_indexable": False,
        "robots_indexable_blocker_reason": "DSC-BG-PEND-001 COFEPRIS pendiente",
        "required_disclosures": [
            "diagnostico_semicuantitativo_no_definitivo",
            "uso_profesional_b2b_only",
            "regulatory_status_pendiente_cofepris",
        ],
        "url_pattern_template": "/productos/{slug-product}/",
        "canonical_url_strategy": "self_canonical",
        "source_dscs": ["DSC-BG-001", "DSC-BG-PEND-001"],
    },
    VerticalId.TOP_CONTROL_PC: {
        "schema_org_types": ["SoftwareApplication"],
        "geo_target": GeoRegion.GLOBAL.value,
        "hreflang": ["es-MX", "en-US", "en-GB"],
        "robots_indexable": True,
        "required_schema_fields_application": [
            "name",
            "applicationCategory",
            "operatingSystem",
            "offers.price",
        ],
        "url_pattern_template": "/{slug-product}/",
        "canonical_url_strategy": "self_canonical",
        "source_dscs": ["DSC-TC-001"],
    },
    VerticalId.MUNDO_DE_TATA: {
        "schema_org_types": ["Product", "Store"],
        "geo_target": GeoRegion.MX_NACIONAL.value,
        "hreflang": ["es-MX"],
        "robots_indexable": True,
        "url_pattern_template": "/tienda/{slug-categoria}/{slug-producto}/",
        "canonical_url_strategy": "self_canonical_per_sku",
        "source_dscs": [],
    },
    VerticalId.EL_MONSTRUO_APP: {
        "schema_org_types": ["SoftwareApplication"],
        "geo_target": GeoRegion.GLOBAL.value,
        "hreflang": ["es-MX", "en-US"],
        "robots_indexable": True,
        "url_pattern_template": "/{section}/",
        "canonical_url_strategy": "self_canonical",
        "source_dscs": [],
    },
}


__all__ = [
    "SEO_CANONICAL_PER_VERTICAL",
    "is_commercial",
    "require_commercial",
    "NON_COMMERCIAL_VERTICALS",
]
