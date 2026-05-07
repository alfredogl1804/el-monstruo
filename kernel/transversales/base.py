# kernel/transversales/base.py
"""
Interfaz canonica para las Capas Transversales (Obj #9).

NO se puede declarar PRODUCTO COMERCIALIZABLE (DSC-G-014) sin que las 6 Capas
de negocio (Ventas, SEO, Publicidad, Tendencias, Operaciones, Finanzas)
implementen esta interfaz para TODOS los verticales que el Monstruo
comercializa.

Patron mirror de kernel.brand pero con dimension explicita de business-model
archetype (cada vertical pertenece a UN archetype: marketplace_services,
saas_b2b, ecommerce_artisanal, etc.) y hard constraints per-vertical
(constantes Python en `_canonical_constraints.py` derivadas de DSCs).

Origen: AGENTS.md Regla Dura #2, DSC-G-002.
"""
from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class VerticalId(str, enum.Enum):
    """
    Verticales canonicos del Monstruo. Identidades estables — los IDs no
    cambian aunque el nombre comercial evolucione.

    Trazabilidad por vertical:
      - cip                → DSC-CIP-001 a 006 (tokenizacion inmobiliaria)
      - liketickets        → DSC-LIKETICKETS-001, 003 + DSC-LT-002
      - kukulkan_365       → DSC-K365-001, 002
      - bioguard           → DSC-BG-001 + DSC-BG-PEND-001
      - top_control_pc     → DSC-TC-001, 002
      - mena_baduy         → DSC-MB-001 (OPSEC: NO comercial — ver
                             RestrictedVerticalError)
      - mundo_de_tata      → derivado del corpus, sin DSC dedicado
      - el_monstruo_app    → la propia app del Monstruo (auto-sales)
    """

    CIP = "cip"
    LIKETICKETS = "liketickets"
    KUKULKAN_365 = "kukulkan_365"
    BIOGUARD = "bioguard"
    TOP_CONTROL_PC = "top_control_pc"
    MENA_BADUY = "mena_baduy"
    MUNDO_DE_TATA = "mundo_de_tata"
    EL_MONSTRUO_APP = "el_monstruo_app"


class BusinessModelArchetype(str, enum.Enum):
    """Archetypes de modelo de negocio. Cada vertical pertenece a UN archetype."""

    SAAS_B2B = "saas_b2b"
    MARKETPLACE_SERVICES = "marketplace_services"
    ECOMMERCE_ARTISANAL = "ecommerce_artisanal"
    PROFESSIONAL_SERVICES = "professional_services"
    EDUCATION_ARTS = "education_arts"
    RESTAURANT = "restaurant"
    TOKENIZED_REAL_ESTATE = "tokenized_real_estate"
    TICKETING_LIMITED_INVENTORY = "ticketing_limited_inventory"
    REAL_ESTATE_DISTRICT = "real_estate_district"
    IOT_B2B_REGULATED = "iot_b2b_regulated"
    AI_AGENT_PLATFORM_CONSUMER = "ai_agent_platform_consumer"
    AGENT_PLATFORM_B2B = "agent_platform_b2b"


class GeoRegion(str, enum.Enum):
    MX_NACIONAL = "mx_nacional"
    MX_SURESTE = "mx_sureste"
    MX_MERIDA = "mx_merida"
    LATAM = "latam"
    GLOBAL = "global"


@dataclass
class TransversalContext:
    vertical: VerticalId
    archetype: BusinessModelArchetype
    geo_region: GeoRegion = GeoRegion.MX_NACIONAL
    current_metrics: dict[str, Any] = field(default_factory=dict)
    target_audience_override: str | None = None
    locale: str = "es-MX"
    brand_dna_snapshot: dict[str, Any] | None = None


@dataclass
class TransversalRecommendation:
    """
    Importante: el campo `value` puede contener data ESTRUCTURAL (pricing tiers,
    funnel stages, CTA conceptos) pero NO copy final. El copy final lo llena
    el brand-voice plugin contra los guidelines, o se revisa por humano.
    """

    layer_name: str
    rule_id: str
    severity: str  # "must" | "should" | "nice"
    value: dict[str, Any]
    rationale: str
    needs_validation_tags: list[str] = field(default_factory=list)
    source_dsc: list[str] = field(default_factory=list)


@dataclass
class TransversalRecommendations:
    layer_name: str
    vertical: VerticalId
    archetype: BusinessModelArchetype
    recommendations: list[TransversalRecommendation] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    aggregated_validation_tags: list[str] = field(default_factory=list)


class RestrictedVerticalError(Exception):
    """
    Vertical NO es comercial — no se puede generar output de ventas/SEO/etc.

    Casos canonicos:
      - VerticalId.MENA_BADUY (DSC-MB-001: OPSEC reforzado, operacion electoral
        real, NO admite output publico de ningun tipo).
    """


class TransversalLayer(ABC):
    """
    Cada una de las 6 Capas comerciales hereda de esta clase.

    Implementaciones DEBEN:
      1. Verificar `is_commercial(vertical)` antes de cualquier operacion;
         si False, levantar RestrictedVerticalError con razon.
      2. Importar constants de su `_canonical_constraints.py` y respetarlas
         como hard constraints.
      3. Etiquetar todo claim de estado-del-mundo (pricing benchmarks,
         competitor data, fechas, market size) con tag en
         `needs_validation_tags`. tools/check_perplexity_tags.py los detecta.
    """

    layer_name: str

    @abstractmethod
    def diagnose(self, ctx: TransversalContext) -> dict[str, Any]:
        ...

    @abstractmethod
    def recommend(self, ctx: TransversalContext) -> TransversalRecommendations:
        ...

    @abstractmethod
    def implement(
        self, recommendations: TransversalRecommendations
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def monitor(self, ctx: TransversalContext) -> dict[str, Any]:
        ...


def all_layers_implemented(layer_names: list[str]) -> bool:
    """
    Verificacion usada por kernel/milestones/gates.yaml gate
    `capas_transversales_operativas`. Retorna True si TODAS las capas
    listadas tienen implementacion (no NotImplementedError).

    Llamado por kernel.milestones.declare antes de declarar
    PRODUCTO_COMERCIALIZABLE (DSC-G-014).
    """
    import importlib
    for name in layer_names:
        try:
            mod = importlib.import_module(f"kernel.transversales.{name}")
        except ImportError:
            return False
        layer_cls_name = name.title() + "Layer"
        cls = getattr(mod, layer_cls_name, None)
        if cls is None:
            return False
        try:
            instance = cls()
        except TypeError:
            return False
        del instance
    return True
