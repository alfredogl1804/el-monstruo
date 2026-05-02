"""
sales_engine.py — Motor de Ventas Transversal
==============================================
Capa Transversal #1 del Objetivo #9.
Se inyecta automáticamente en todo proyecto que El Monstruo cree.

Responsabilidades:
  1. Definir estrategia de pricing óptima
  2. Generar funnels de conversión
  3. Configurar tracking de métricas
  4. Proponer A/B tests
  5. Monitorear y optimizar conversión

Sprint 57 — "Las Capas Transversales"
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger("sales_engine")


# ── PostHog integration (graceful degradation) ───────────────────────────────

try:
    from posthog import Posthog  # type: ignore

    POSTHOG_AVAILABLE = True
except ImportError:
    POSTHOG_AVAILABLE = False
    logger.warning("PostHog SDK not installed. Run: pip install posthog==7.13.2")


# ── Stripe integration (graceful degradation) ────────────────────────────────

try:
    import stripe  # type: ignore

    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logger.warning("Stripe SDK not installed. Run: pip install stripe==15.1.0")


# ── Data models ───────────────────────────────────────────────────────────────


class PricingModel(Enum):
    FREEMIUM = "freemium"
    TIERED = "tiered"
    USAGE_BASED = "usage_based"
    FLAT_RATE = "flat_rate"
    COMMISSION = "commission"
    HYBRID = "hybrid"


@dataclass
class PricingTier:
    name: str
    price_usd: float | str  # "custom" for enterprise
    features: list[str]
    limits: dict = field(default_factory=dict)
    is_popular: bool = False


@dataclass
class ConversionGoal:
    name: str
    event_name: str
    target_rate: float  # 0.0 to 1.0
    current_rate: float = 0.0
    posthog_filter: dict = field(default_factory=dict)


@dataclass
class SalesEngineConfig:
    """Configuración del motor de ventas para un proyecto."""

    project_id: str
    vertical: str
    pricing_model: PricingModel
    tiers: list[PricingTier]
    conversion_goals: list[ConversionGoal]
    funnel_stages: list[str] = field(
        default_factory=lambda: ["awareness", "interest", "consideration", "intent", "purchase", "retention"]
    )
    ab_tests_enabled: bool = True
    posthog_project_id: Optional[str] = None
    stripe_account_id: Optional[str] = None


# ── Vertical → Pricing Model mapping ─────────────────────────────────────────

VERTICAL_PRICING: dict[str, PricingModel] = {
    "saas": PricingModel.FREEMIUM,
    "marketplace": PricingModel.COMMISSION,
    "ecommerce": PricingModel.TIERED,
    "content": PricingModel.TIERED,
    "api": PricingModel.USAGE_BASED,
    "consulting": PricingModel.FLAT_RATE,
    "fintech": PricingModel.HYBRID,
    "edtech": PricingModel.TIERED,
    "healthtech": PricingModel.TIERED,
}


# ── SalesEngine ───────────────────────────────────────────────────────────────


class SalesEngine:
    """Motor de ventas transversal — se inyecta en cada proyecto."""

    def __init__(
        self,
        config: SalesEngineConfig,
        posthog_client=None,
        stripe_client=None,
    ):
        self._config = config
        self._posthog = posthog_client
        self._stripe = stripe_client
        logger.info("sales_engine_initialized", project=config.project_id, vertical=config.vertical)

    async def setup_for_project(self, project_id: str, vertical: str) -> dict:
        """Configurar motor de ventas para un nuevo proyecto."""
        # 1. Determinar pricing model óptimo
        pricing = await self._determine_pricing(vertical)

        # 2. Generar funnel template
        funnel = self._generate_funnel_template(vertical)

        # 3. Definir conversion goals
        goals = self._define_conversion_goals(vertical)

        # 4. Setup tracking events
        tracking = await self._setup_tracking(project_id, goals)

        return {
            "project_id": project_id,
            "vertical": vertical,
            "pricing": pricing,
            "funnel": funnel,
            "goals": goals,
            "tracking": tracking,
            "status": "configured",
        }

    async def _determine_pricing(self, vertical: str) -> dict:
        """Determinar modelo de pricing óptimo para un vertical."""
        model = VERTICAL_PRICING.get(vertical.lower(), PricingModel.TIERED)
        return {
            "model": model.value,
            "rationale": f"Based on {vertical} vertical best practices",
            "confidence": 0.85,
        }

    def _generate_funnel_template(self, vertical: str) -> dict:
        """Generar template de funnel para un vertical."""
        return {
            "stages": self._config.funnel_stages,
            "touchpoints": {
                "awareness": ["SEO content", "Social media", "PR", "Paid ads"],
                "interest": ["Landing page", "Lead magnet", "Email capture", "Demo video"],
                "consideration": ["Case studies", "Comparison pages", "Free trial", "Webinar"],
                "intent": ["Pricing page", "Demo request", "Consultation", "ROI calculator"],
                "purchase": ["Checkout", "Payment", "Onboarding", "Welcome email"],
                "retention": ["Email nurture", "Feature updates", "Loyalty program", "NPS survey"],
            },
        }

    def _define_conversion_goals(self, vertical: str) -> list[dict]:
        """Definir goals de conversión para tracking."""
        base_goals = [
            {"name": "signup", "event": "user_signed_up", "target": 0.05},
            {"name": "activation", "event": "user_activated", "target": 0.40},
            {"name": "purchase", "event": "purchase_completed", "target": 0.03},
            {"name": "retention_7d", "event": "user_returned_7d", "target": 0.30},
            {"name": "referral", "event": "user_referred", "target": 0.10},
        ]

        # Agregar goals específicos por vertical
        if vertical == "marketplace":
            base_goals.append({"name": "first_listing", "event": "listing_created", "target": 0.60})
        elif vertical == "ecommerce":
            base_goals.append({"name": "cart_add", "event": "product_added_to_cart", "target": 0.10})

        return base_goals

    async def _setup_tracking(self, project_id: str, goals: list) -> dict:
        """Configurar tracking de eventos en PostHog."""
        if not self._posthog:
            return {
                "status": "posthog_not_configured",
                "events_to_track": goals,
                "action_required": "Set POSTHOG_API_KEY environment variable",
            }

        # En producción: crear PostHog actions/insights via API
        return {
            "status": "configured",
            "project_id": project_id,
            "events_registered": len(goals),
        }

    async def get_conversion_report(self, project_id: str, period_days: int = 30) -> dict:
        """Generar reporte de conversión para un proyecto."""
        return {
            "project_id": project_id,
            "period_days": period_days,
            "funnel_metrics": {
                "visitors": 0,
                "signups": 0,
                "activated": 0,
                "purchased": 0,
                "retained": 0,
            },
            "recommendations": [
                "Configure PostHog events for real-time tracking",
                "Set up A/B test for pricing page",
                "Create email nurture sequence for trial users",
            ],
        }

    async def create_stripe_product(self, name: str, price_usd: float, interval: str = "month") -> dict:
        """Crear producto y precio en Stripe."""
        if not STRIPE_AVAILABLE:
            return {"error": "Stripe SDK not installed"}

        stripe_key = os.getenv("STRIPE_SECRET_KEY")
        if not stripe_key:
            return {"error": "STRIPE_SECRET_KEY not configured"}

        try:
            stripe.api_key = stripe_key
            product = stripe.Product.create(name=name)
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(price_usd * 100),  # Stripe usa centavos
                currency="usd",
                recurring={"interval": interval},
            )
            return {
                "product_id": product.id,
                "price_id": price.id,
                "name": name,
                "price_usd": price_usd,
                "interval": interval,
            }
        except Exception as e:
            logger.error("stripe_product_creation_failed", error=str(e))
            return {"error": str(e)}


# ── ConversionTracker ─────────────────────────────────────────────────────────


class ConversionTracker:
    """Tracker de conversión basado en PostHog 7.13.2."""

    def __init__(self, api_key: Optional[str] = None, host: Optional[str] = None):
        self._api_key = api_key or os.getenv("POSTHOG_API_KEY")
        self._host = host or os.getenv("POSTHOG_HOST", "https://app.posthog.com")
        self._client = None

        if POSTHOG_AVAILABLE and self._api_key:
            self._client = Posthog(
                project_api_key=self._api_key,
                host=self._host,
            )
            logger.info("posthog_client_initialized", host=self._host)

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def track_event(self, distinct_id: str, event: str, properties: dict = None) -> bool:
        """Track a conversion event."""
        if not self._client:
            logger.debug("posthog_not_configured", event=event)
            return False

        self._client.capture(
            distinct_id=distinct_id,
            event=event,
            properties=properties or {},
        )
        return True

    def track_signup(self, user_id: str, source: str = "organic", plan: str = "free") -> bool:
        return self.track_event(user_id, "user_signed_up", {"source": source, "plan": plan})

    def track_purchase(self, user_id: str, amount_usd: float, product: str) -> bool:
        return self.track_event(
            user_id,
            "purchase_completed",
            {
                "amount_usd": amount_usd,
                "product": product,
            },
        )

    def track_activation(self, user_id: str, action: str) -> bool:
        return self.track_event(user_id, "user_activated", {"activation_action": action})

    def identify_user(self, user_id: str, properties: dict) -> bool:
        if not self._client:
            return False
        self._client.identify(distinct_id=user_id, properties=properties)
        return True

    def flush(self) -> None:
        if self._client:
            self._client.flush()

    def shutdown(self) -> None:
        if self._client:
            self._client.shutdown()


# ── Factory ───────────────────────────────────────────────────────────────────


def create_sales_engine(project_id: str, vertical: str) -> SalesEngine:
    """Factory para crear un SalesEngine configurado para un proyecto."""
    model = VERTICAL_PRICING.get(vertical.lower(), PricingModel.TIERED)
    config = SalesEngineConfig(
        project_id=project_id,
        vertical=vertical,
        pricing_model=model,
        tiers=[],
        conversion_goals=[],
    )
    tracker = ConversionTracker()
    return SalesEngine(
        config=config,
        posthog_client=tracker._client,
    )
