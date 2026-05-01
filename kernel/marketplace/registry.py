"""kernel/marketplace/registry.py

Marketplace Global Registry — Sprint 63.4
Objetivo #13: Del Mundo

Transforma el marketplace local (Sprint 62) en un marketplace global
donde desarrolladores publican plugins, templates y componentes.
Revenue sharing 70/30 (developer/platform).

Soberanía:
    - Supabase: alternativa → SQLite local con tabla marketplace_items
    - Pagos: Stripe (futuro) → alternativa → PayPal / transferencia manual
"""

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = structlog.get_logger("marketplace.registry")

# ── Errores con identidad ──────────────────────────────────────────────────────

MARKETPLACE_ITEM_NO_ENCONTRADO = (
    "El ítem del marketplace no fue encontrado. "
    "Verifica el ID o busca en el catálogo con search()."
)
MARKETPLACE_PUBLICACION_FALLIDA = (
    "No se pudo publicar el ítem en el marketplace. "
    "Verifica que todos los campos requeridos estén completos."
)
MARKETPLACE_INSTALACION_FALLIDA = (
    "No se pudo instalar el ítem del marketplace. "
    "Verifica que el ítem esté verificado y disponible."
)
MARKETPLACE_CALIFICACION_INVALIDA = (
    "La calificación debe estar entre 1 y 5 estrellas. "
    "Proporciona un valor entero en ese rango."
)


# ── Modelo de datos ────────────────────────────────────────────────────────────

@dataclass
class MarketplaceItem:
    """Ítem del marketplace global (plugin, template o componente).

    Args:
        id: Identificador único
        name: Nombre del ítem
        type: Tipo ("plugin", "template", "component")
        author: Autor/desarrollador
        version: Versión semántica
        description: Descripción del ítem
        category: Categoría (ej: "ecommerce", "analytics", "ui")
        tags: Etiquetas para búsqueda
        downloads: Número de descargas
        rating: Calificación promedio 0-5
        rating_count: Número de calificaciones
        price_usd: Precio en USD (0 = gratis)
        revenue_share: Porcentaje para el desarrollador (0.70 = 70%)
        published_at: Fecha de publicación
        verified: Si fue verificado por el equipo
        source_url: URL del código fuente

    Returns:
        MarketplaceItem listo para publicar o instalar

    Soberanía:
        Pagos: Stripe → PayPal → transferencia manual
    """
    id: str
    name: str
    type: str
    author: str
    version: str
    description: str
    category: str
    tags: list = field(default_factory=list)
    downloads: int = 0
    rating: float = 0.0
    rating_count: int = 0
    price_usd: float = 0.0
    revenue_share: float = 0.70
    published_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified: bool = False
    source_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Serializar para Command Center."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "author": self.author,
            "version": self.version,
            "description": self.description[:200],
            "category": self.category,
            "tags": self.tags,
            "downloads": self.downloads,
            "rating": round(self.rating, 2),
            "rating_count": self.rating_count,
            "price_usd": self.price_usd,
            "revenue_share": self.revenue_share,
            "published_at": self.published_at.isoformat(),
            "verified": self.verified,
            "source_url": self.source_url,
        }


# ── Catálogo seed del marketplace ──────────────────────────────────────────────

SEED_ITEMS: list = [
    MarketplaceItem(
        id="monstruo-analytics-plugin",
        name="Analytics Dashboard Plugin",
        type="plugin",
        author="monstruo-team",
        version="1.0.0",
        description="Dashboard de analytics integrado con Langfuse y Supabase. Métricas en tiempo real.",
        category="analytics",
        tags=["analytics", "dashboard", "langfuse", "metrics"],
        downloads=42,
        rating=4.8,
        rating_count=12,
        price_usd=0.0,
        verified=True,
    ),
    MarketplaceItem(
        id="restaurant-landing-template",
        name="Restaurant Landing Template",
        type="template",
        author="monstruo-team",
        version="1.0.0",
        description="Template completo para restaurantes con menú, reservaciones y galería.",
        category="food",
        tags=["restaurant", "landing", "menu", "reservations"],
        downloads=156,
        rating=4.9,
        rating_count=28,
        price_usd=0.0,
        verified=True,
    ),
    MarketplaceItem(
        id="saas-dashboard-template",
        name="SaaS Dashboard Template",
        type="template",
        author="monstruo-team",
        version="1.0.0",
        description="Dashboard completo para SaaS con auth, billing, analytics y API.",
        category="saas",
        tags=["saas", "dashboard", "auth", "billing"],
        downloads=89,
        rating=4.7,
        rating_count=19,
        price_usd=0.0,
        verified=True,
    ),
    MarketplaceItem(
        id="hero-parallax-component",
        name="Hero Parallax Component",
        type="component",
        author="monstruo-team",
        version="1.0.0",
        description="Componente hero con efecto parallax y animaciones Motion.",
        category="ui",
        tags=["hero", "parallax", "animation", "motion"],
        downloads=234,
        rating=4.9,
        rating_count=45,
        price_usd=0.0,
        verified=True,
    ),
    MarketplaceItem(
        id="ecommerce-cart-plugin",
        name="E-commerce Cart Plugin",
        type="plugin",
        author="monstruo-team",
        version="1.0.0",
        description="Plugin de carrito de compras con integración Stripe y gestión de inventario.",
        category="ecommerce",
        tags=["ecommerce", "cart", "stripe", "payments"],
        downloads=67,
        rating=4.6,
        rating_count=15,
        price_usd=0.0,
        verified=True,
    ),
    MarketplaceItem(
        id="fitness-landing-template",
        name="Fitness Studio Template",
        type="template",
        author="monstruo-team",
        version="1.0.0",
        description="Template para gimnasios y estudios fitness con horarios, membresías y trainers.",
        category="fitness",
        tags=["fitness", "gym", "schedule", "membership"],
        downloads=78,
        rating=4.7,
        rating_count=22,
        price_usd=0.0,
        verified=True,
    ),
    MarketplaceItem(
        id="pricing-table-component",
        name="Pricing Table Component",
        type="component",
        author="monstruo-team",
        version="1.0.0",
        description="Tabla de precios con animaciones, toggle mensual/anual y CTA destacado.",
        category="ui",
        tags=["pricing", "table", "saas", "conversion"],
        downloads=312,
        rating=4.8,
        rating_count=67,
        price_usd=0.0,
        verified=True,
    ),
    MarketplaceItem(
        id="seo-optimizer-plugin",
        name="SEO Optimizer Plugin",
        type="plugin",
        author="monstruo-team",
        version="1.0.0",
        description="Plugin de SEO con meta tags automáticos, sitemap y structured data.",
        category="seo",
        tags=["seo", "meta", "sitemap", "structured-data"],
        downloads=145,
        rating=4.5,
        rating_count=31,
        price_usd=0.0,
        verified=True,
    ),
    MarketplaceItem(
        id="portfolio-creative-template",
        name="Creative Portfolio Template",
        type="template",
        author="monstruo-team",
        version="1.0.0",
        description="Portfolio creativo con galería, timeline y animaciones playful.",
        category="portfolio",
        tags=["portfolio", "creative", "gallery", "animation"],
        downloads=198,
        rating=4.9,
        rating_count=52,
        price_usd=0.0,
        verified=True,
    ),
    MarketplaceItem(
        id="testimonial-carousel-component",
        name="Testimonial Carousel Component",
        type="component",
        author="monstruo-team",
        version="1.0.0",
        description="Carrusel de testimonios con auto-play, indicadores y animaciones suaves.",
        category="ui",
        tags=["testimonial", "carousel", "social-proof", "animation"],
        downloads=267,
        rating=4.7,
        rating_count=58,
        price_usd=0.0,
        verified=True,
    ),
]


# ── Registry principal ─────────────────────────────────────────────────────────

class MarketplaceRegistry:
    """Registry global del marketplace de plugins, templates y componentes.

    Gestiona publicación, búsqueda, instalación y calificación de ítems.
    Revenue sharing 70/30 (developer/platform) para ítems de pago.

    Args:
        supabase: Cliente Supabase para persistencia

    Returns:
        Registry inicializado con catálogo seed

    Raises:
        RuntimeError: Si Supabase no está disponible (usa catálogo en memoria)

    Soberanía:
        Sin Supabase: catálogo en memoria con SEED_ITEMS
        Pagos: Stripe → PayPal → transferencia manual
    """

    def __init__(self, supabase=None):
        self.supabase = supabase
        self._items: dict = {item.id: item for item in SEED_ITEMS}
        logger.info("marketplace_registry_init", seed_items=len(SEED_ITEMS))

    async def search(
        self,
        query: str = "",
        item_type: str = None,
        category: str = None,
        sort: str = "relevance",
        free_only: bool = False,
    ) -> list:
        """Buscar ítems en el marketplace.

        Args:
            query: Texto de búsqueda
            item_type: Filtrar por tipo ("plugin", "template", "component")
            category: Filtrar por categoría
            sort: Ordenar por ("relevance", "downloads", "rating", "newest")
            free_only: Solo mostrar ítems gratuitos

        Returns:
            Lista de ítems que coinciden con los filtros

        Soberanía:
            Sin Supabase: búsqueda en catálogo en memoria
        """
        if self.supabase:
            try:
                return await self._search_supabase(query, item_type, category, sort, free_only)
            except Exception as exc:
                logger.warning("marketplace_supabase_fallback", error=str(exc))

        # Búsqueda en memoria
        results = list(self._items.values())

        if item_type:
            results = [i for i in results if i.type == item_type]
        if category:
            results = [i for i in results if i.category == category]
        if free_only:
            results = [i for i in results if i.price_usd == 0.0]
        if query:
            query_lower = query.lower()
            results = [
                i for i in results
                if query_lower in i.name.lower()
                or query_lower in i.description.lower()
                or any(query_lower in tag for tag in i.tags)
            ]

        # Ordenar
        if sort == "downloads":
            results.sort(key=lambda x: x.downloads, reverse=True)
        elif sort == "rating":
            results.sort(key=lambda x: x.rating, reverse=True)
        elif sort == "newest":
            results.sort(key=lambda x: x.published_at, reverse=True)
        else:  # relevance
            results.sort(key=lambda x: x.downloads * x.rating, reverse=True)

        return [i.to_dict() for i in results[:50]]

    async def _search_supabase(
        self, query: str, item_type: str, category: str, sort: str, free_only: bool
    ) -> list:
        """Búsqueda en Supabase."""
        q = self.supabase.table("marketplace_items").select("*")
        if item_type:
            q = q.eq("type", item_type)
        if category:
            q = q.eq("category", category)
        if free_only:
            q = q.eq("price_usd", 0)
        if query:
            q = q.or_(f"name.ilike.%{query}%,description.ilike.%{query}%")
        if sort == "downloads":
            q = q.order("downloads", desc=True)
        elif sort == "rating":
            q = q.order("rating", desc=True)
        elif sort == "newest":
            q = q.order("published_at", desc=True)
        else:
            q = q.order("downloads", desc=True)
        result = await q.limit(50).execute()
        return result.data or []

    async def publish(self, item: MarketplaceItem) -> str:
        """Publicar un ítem en el marketplace.

        Args:
            item: MarketplaceItem a publicar

        Returns:
            ID del ítem publicado

        Raises:
            ValueError: Si los campos requeridos están incompletos

        Soberanía:
            Sin Supabase: persiste en catálogo en memoria
        """
        if not item.name or not item.author:
            raise ValueError(MARKETPLACE_PUBLICACION_FALLIDA)

        # Agregar al catálogo en memoria
        self._items[item.id] = item

        if self.supabase:
            try:
                data = {
                    "name": item.name,
                    "type": item.type,
                    "author": item.author,
                    "version": item.version,
                    "description": item.description,
                    "category": item.category,
                    "tags": item.tags,
                    "price_usd": item.price_usd,
                    "revenue_share": item.revenue_share,
                    "verified": False,
                }
                result = await self.supabase.table("marketplace_items").insert(data).execute()
                item_id = result.data[0]["id"]
                logger.info("item_published_supabase", id=item_id, name=item.name)
                return item_id
            except Exception as exc:
                logger.error("publish_supabase_error", error=str(exc))

        logger.info("item_published_memory", id=item.id, name=item.name)
        return item.id

    async def install(self, item_id: str, user_id: str) -> dict:
        """Instalar un ítem del marketplace para un usuario.

        Args:
            item_id: ID del ítem a instalar
            user_id: ID del usuario que instala

        Returns:
            Dict con status e información del ítem instalado

        Raises:
            ValueError: Si el ítem no existe (MARKETPLACE_ITEM_NO_ENCONTRADO)

        Soberanía:
            Sin Supabase: registra instalación en memoria
        """
        # Buscar en memoria primero
        item = self._items.get(item_id)

        if not item and self.supabase:
            try:
                result = await self.supabase.table("marketplace_items")\
                    .select("*").eq("id", item_id).single().execute()
                if result.data:
                    item = result.data
            except Exception:
                pass

        if not item:
            raise ValueError(f"{MARKETPLACE_ITEM_NO_ENCONTRADO} ID: {item_id}")

        # Incrementar contador de descargas en memoria
        if item_id in self._items:
            self._items[item_id].downloads += 1

        if self.supabase:
            try:
                await self.supabase.table("marketplace_installations").insert({
                    "item_id": item_id,
                    "user_id": user_id,
                    "installed_at": datetime.now(timezone.utc).isoformat(),
                }).execute()
                await self.supabase.table("marketplace_items")\
                    .update({"downloads": (item.downloads if hasattr(item, "downloads") else 0) + 1})\
                    .eq("id", item_id).execute()
            except Exception as exc:
                logger.warning("install_supabase_error", error=str(exc))

        item_dict = item.to_dict() if hasattr(item, "to_dict") else item
        logger.info("item_installed", item_id=item_id, user_id=user_id)
        return {"status": "installed", "item": item_dict}

    async def rate(self, item_id: str, user_id: str, score: int, review: str = "") -> None:
        """Calificar un ítem del marketplace.

        Args:
            item_id: ID del ítem a calificar
            user_id: ID del usuario que califica
            score: Calificación 1-5 estrellas
            review: Reseña opcional

        Raises:
            ValueError: Si score no está entre 1 y 5

        Soberanía:
            Sin Supabase: actualiza rating en memoria
        """
        if not 1 <= score <= 5:
            raise ValueError(MARKETPLACE_CALIFICACION_INVALIDA)

        if self.supabase:
            try:
                await self.supabase.table("marketplace_reviews").insert({
                    "item_id": item_id,
                    "user_id": user_id,
                    "score": score,
                    "review": review,
                }).execute()
                # Recalcular rating promedio
                reviews = await self.supabase.table("marketplace_reviews")\
                    .select("score").eq("item_id", item_id).execute()
                scores = [r["score"] for r in (reviews.data or [])]
                avg = sum(scores) / len(scores) if scores else score
                await self.supabase.table("marketplace_items")\
                    .update({"rating": round(avg, 2), "rating_count": len(scores)})\
                    .eq("id", item_id).execute()
            except Exception as exc:
                logger.warning("rate_supabase_error", error=str(exc))

        # Actualizar en memoria
        if item_id in self._items:
            item = self._items[item_id]
            total = item.rating * item.rating_count + score
            item.rating_count += 1
            item.rating = round(total / item.rating_count, 2)

        logger.info("item_rated", item_id=item_id, score=score)

    def get_stats(self) -> dict:
        """Obtener estadísticas del marketplace."""
        items = list(self._items.values())
        return {
            "total_items": len(items),
            "plugins": sum(1 for i in items if i.type == "plugin"),
            "templates": sum(1 for i in items if i.type == "template"),
            "components": sum(1 for i in items if i.type == "component"),
            "free_items": sum(1 for i in items if i.price_usd == 0),
            "verified_items": sum(1 for i in items if i.verified),
            "total_downloads": sum(i.downloads for i in items),
            "avg_rating": round(
                sum(i.rating for i in items if i.rating_count > 0) /
                max(1, sum(1 for i in items if i.rating_count > 0)), 2
            ),
        }

    def to_dict(self) -> dict:
        """Serializar estado para Command Center."""
        stats = self.get_stats()
        return {
            "module": "MarketplaceRegistry",
            "sprint": "63.4",
            "objetivo": "#13 Del Mundo",
            "has_supabase": self.supabase is not None,
            "revenue_share_developer": "70%",
            "revenue_share_platform": "30%",
            **stats,
        }


# ── Singleton ──────────────────────────────────────────────────────────────────

_marketplace_registry: Optional[MarketplaceRegistry] = None


def get_marketplace_registry() -> Optional[MarketplaceRegistry]:
    """Obtener instancia singleton del marketplace registry."""
    return _marketplace_registry


def init_marketplace_registry(supabase=None) -> MarketplaceRegistry:
    """Inicializar el marketplace registry global.

    Args:
        supabase: Cliente Supabase (opcional)

    Returns:
        MarketplaceRegistry inicializado con catálogo seed

    Soberanía:
        Sin Supabase: catálogo en memoria con 10 ítems seed verificados
    """
    global _marketplace_registry
    _marketplace_registry = MarketplaceRegistry(supabase=supabase)
    logger.info("marketplace_registry_ready", seed_items=len(SEED_ITEMS))
    return _marketplace_registry
