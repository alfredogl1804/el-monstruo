"""
kernel/marketplace/marketplace.py
Sprint 62.4 — Marketplace de Templates (Objetivo #12: Ecosistema)

Marketplace de templates de proyectos completos listos para desplegar.
Cada template es un proyecto completo con componentes, configuración y código.
Nivel de calidad: Producción-ready desde el primer despliegue.

Soberanía: Si Supabase no está disponible, usa catálogo local de templates.
Alternativa: JSON local con templates pre-definidos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import structlog

logger = structlog.get_logger("marketplace")


# --- Excepciones con identidad ---


class TemplateNoEncontrado(Exception):
    """Template no encontrado en el Marketplace."""

    def __init__(self, template_id: str):
        super().__init__(
            f"Template '{template_id}' no encontrado en el Marketplace. "
            f"Usa GET /api/marketplace/templates para ver los disponibles."
        )
        self.template_id = template_id


class TemplateIncompatible(Exception):
    """Template incompatible con la versión actual del Monstruo."""

    def __init__(self, template_id: str, version_requerida: str, version_actual: str):
        super().__init__(
            f"Template '{template_id}' requiere Monstruo v{version_requerida}, "
            f"pero la versión actual es v{version_actual}."
        )


# --- Dataclasses ---


@dataclass
class TemplateMetadata:
    """Metadatos de un template del Marketplace."""

    id: str
    name: str
    description: str
    category: str
    vertical: str
    author: str
    version: str
    monstruo_version_min: str
    price: float = 0.0
    downloads: int = 0
    rating: float = 0.0
    tags: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    preview_url: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "vertical": self.vertical,
            "author": self.author,
            "version": self.version,
            "price": self.price,
            "downloads": self.downloads,
            "rating": self.rating,
            "tags": self.tags,
            "components": self.components,
            "preview_url": self.preview_url,
        }


# --- Catálogo built-in de templates ---

BUILTIN_TEMPLATES: list[dict] = [
    {
        "id": "saas-starter",
        "name": "SaaS Starter",
        "description": "Template completo para SaaS B2B con auth, billing y dashboard",
        "category": "web-app",
        "vertical": "saas",
        "author": "El Monstruo",
        "version": "1.0.0",
        "monstruo_version_min": "1.0.0",
        "price": 0.0,
        "downloads": 0,
        "rating": 0.0,
        "tags": ["saas", "b2b", "dashboard", "stripe", "auth"],
        "components": ["navbar", "hero_centered", "feature_grid", "pricing_table", "footer"],
    },
    {
        "id": "ecommerce-fashion",
        "name": "Fashion Store",
        "description": "Tienda de moda con catálogo, carrito y checkout Stripe",
        "category": "ecommerce",
        "vertical": "fashion",
        "author": "El Monstruo",
        "version": "1.0.0",
        "monstruo_version_min": "1.0.0",
        "price": 0.0,
        "downloads": 0,
        "rating": 0.0,
        "tags": ["ecommerce", "fashion", "stripe", "inventory"],
        "components": ["navbar", "hero_split", "product_card", "cart_drawer", "checkout_form", "footer"],
    },
    {
        "id": "agency-portfolio",
        "name": "Agency Portfolio",
        "description": "Portfolio de agencia creativa con animaciones premium",
        "category": "portfolio",
        "vertical": "agency",
        "author": "El Monstruo",
        "version": "1.0.0",
        "monstruo_version_min": "1.0.0",
        "price": 0.0,
        "downloads": 0,
        "rating": 0.0,
        "tags": ["portfolio", "agency", "creative", "animations"],
        "components": ["navbar", "hero_video", "timeline", "stats_bar", "contact_form", "footer"],
    },
    {
        "id": "restaurant-menu",
        "name": "Restaurant & Menu",
        "description": "Sitio de restaurante con menú digital, reservas y pedidos online",
        "category": "local-business",
        "vertical": "food",
        "author": "El Monstruo",
        "version": "1.0.0",
        "monstruo_version_min": "1.0.0",
        "price": 0.0,
        "downloads": 0,
        "rating": 0.0,
        "tags": ["restaurant", "food", "menu", "reservations"],
        "components": ["navbar", "hero_parallax", "feature_grid", "testimonial", "contact_form", "footer"],
    },
    {
        "id": "fintech-dashboard",
        "name": "FinTech Dashboard",
        "description": "Dashboard financiero con gráficas, métricas y reportes",
        "category": "web-app",
        "vertical": "fintech",
        "author": "El Monstruo",
        "version": "1.0.0",
        "monstruo_version_min": "1.0.0",
        "price": 0.0,
        "downloads": 0,
        "rating": 0.0,
        "tags": ["fintech", "dashboard", "charts", "analytics"],
        "components": ["sidebar", "stats_bar", "feature_grid", "footer"],
    },
    {
        "id": "edtech-platform",
        "name": "EdTech Platform",
        "description": "Plataforma educativa con cursos, progreso y certificados",
        "category": "web-app",
        "vertical": "education",
        "author": "El Monstruo",
        "version": "1.0.0",
        "monstruo_version_min": "1.0.0",
        "price": 0.0,
        "downloads": 0,
        "rating": 0.0,
        "tags": ["edtech", "courses", "lms", "certificates"],
        "components": ["navbar", "hero_centered", "feature_grid", "pricing_table", "testimonial", "footer"],
    },
    {
        "id": "healthtech-clinic",
        "name": "HealthTech Clinic",
        "description": "Clínica digital con citas, telemedicina y expediente",
        "category": "web-app",
        "vertical": "health",
        "author": "El Monstruo",
        "version": "1.0.0",
        "monstruo_version_min": "1.0.0",
        "price": 0.0,
        "downloads": 0,
        "rating": 0.0,
        "tags": ["health", "clinic", "appointments", "telemedicine"],
        "components": ["navbar", "hero_split", "feature_grid", "stats_bar", "contact_form", "footer"],
    },
    {
        "id": "proptech-listings",
        "name": "PropTech Listings",
        "description": "Portal inmobiliario con búsqueda, filtros y tours virtuales",
        "category": "marketplace",
        "vertical": "real-estate",
        "author": "El Monstruo",
        "version": "1.0.0",
        "monstruo_version_min": "1.0.0",
        "price": 0.0,
        "downloads": 0,
        "rating": 0.0,
        "tags": ["proptech", "real-estate", "listings", "search"],
        "components": ["navbar", "hero_centered", "search_bar", "feature_grid", "footer"],
    },
    {
        "id": "legaltech-contracts",
        "name": "LegalTech Contracts",
        "description": "Plataforma de contratos digitales con firma electrónica",
        "category": "web-app",
        "vertical": "legal",
        "author": "El Monstruo",
        "version": "1.0.0",
        "monstruo_version_min": "1.0.0",
        "price": 0.0,
        "downloads": 0,
        "rating": 0.0,
        "tags": ["legaltech", "contracts", "esign", "compliance"],
        "components": ["navbar", "hero_split", "feature_grid", "pricing_table", "cta_section", "footer"],
    },
    {
        "id": "hrtech-talent",
        "name": "HRTech Talent Platform",
        "description": "Plataforma de talento con ATS, onboarding y performance",
        "category": "web-app",
        "vertical": "hr",
        "author": "El Monstruo",
        "version": "1.0.0",
        "monstruo_version_min": "1.0.0",
        "price": 0.0,
        "downloads": 0,
        "rating": 0.0,
        "tags": ["hrtech", "ats", "talent", "onboarding"],
        "components": ["navbar", "hero_centered", "feature_grid", "stats_bar", "cta_section", "footer"],
    },
]

MONSTRUO_VERSION = "1.0.0"


class Marketplace:
    """
    Marketplace de templates de proyectos completos.

    Permite descubrir, filtrar y desplegar templates de proyectos
    listos para producción en múltiples verticales.
    """

    def __init__(self, supabase=None):
        """
        Args:
            supabase: Cliente AsyncClient de Supabase (opcional).
        """
        self.supabase = supabase
        self._templates: dict[str, TemplateMetadata] = {}
        self._loaded = False

    async def load_catalog(self) -> int:
        """
        Carga el catálogo de templates (built-in + Supabase).

        Returns:
            Número total de templates cargados.
        """
        count = 0

        # Built-in
        for data in BUILTIN_TEMPLATES:
            template = TemplateMetadata(**data)
            self._templates[template.id] = template
            count += 1

        # Supabase (templates de la comunidad)
        if self.supabase:
            try:
                response = await self.supabase.table("marketplace_templates").select("*").execute()
                for row in response.data or []:
                    if row.get("id") not in self._templates:
                        template = TemplateMetadata(**row)
                        self._templates[template.id] = template
                        count += 1
            except Exception as e:
                logger.warning("marketplace_supabase_error", error=str(e))

        self._loaded = True
        logger.info("marketplace_cargado", total=count)
        return count

    def get_by_id(self, template_id: str) -> TemplateMetadata:
        """
        Obtiene un template por su ID.

        Args:
            template_id: ID del template.

        Returns:
            TemplateMetadata del template.

        Raises:
            TemplateNoEncontrado: Si el template no existe.
        """
        if template_id not in self._templates:
            raise TemplateNoEncontrado(template_id)
        return self._templates[template_id]

    def search(
        self, query: str = "", vertical: Optional[str] = None, category: Optional[str] = None, free_only: bool = False
    ) -> list[TemplateMetadata]:
        """
        Busca templates con filtros.

        Args:
            query: Texto a buscar en nombre, descripción y tags.
            vertical: Filtrar por vertical (saas, ecommerce, etc.).
            category: Filtrar por categoría (web-app, ecommerce, etc.).
            free_only: Solo mostrar templates gratuitos.

        Returns:
            Lista de TemplateMetadata que coinciden con los filtros.
        """
        results = list(self._templates.values())

        if query:
            query_lower = query.lower()
            results = [
                t
                for t in results
                if query_lower in t.name.lower()
                or query_lower in t.description.lower()
                or any(query_lower in tag for tag in t.tags)
            ]

        if vertical:
            results = [t for t in results if t.vertical == vertical]

        if category:
            results = [t for t in results if t.category == category]

        if free_only:
            results = [t for t in results if t.price == 0.0]

        return sorted(results, key=lambda t: t.downloads, reverse=True)

    def list_verticals(self) -> list[str]:
        """Lista todas las verticales disponibles."""
        return list({t.vertical for t in self._templates.values()})

    def list_categories(self) -> list[str]:
        """Lista todas las categorías disponibles."""
        return list({t.category for t in self._templates.values()})

    def to_dict(self) -> dict:
        """Serialización para el Command Center."""
        return {
            "total_templates": len(self._templates),
            "cargado": self._loaded,
            "verticals": self.list_verticals(),
            "categories": self.list_categories(),
            "templates_gratuitos": sum(1 for t in self._templates.values() if t.price == 0.0),
        }


# --- Singleton ---

_marketplace: Marketplace | None = None


def get_marketplace() -> Marketplace:
    """Retorna el singleton del Marketplace."""
    global _marketplace
    if _marketplace is None:
        _marketplace = Marketplace()
    return _marketplace


def init_marketplace(supabase=None) -> Marketplace:
    """Inicializa el singleton del Marketplace."""
    global _marketplace
    _marketplace = Marketplace(supabase=supabase)
    return _marketplace
