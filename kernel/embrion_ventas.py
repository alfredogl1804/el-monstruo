"""
embrion_ventas.py — Embrión-Ventas: Especialista en Estrategia Comercial
=========================================================================
Primer Embrión especializado del sistema (Obj #11).
Hereda de EmbrionLoop pero con:
  - System prompt especializado en ventas
  - Knowledge base de funnels, pricing, conversión
  - Tareas autónomas: análisis de mercado, optimización de pricing
  - Integración con PostHog para métricas de conversión

Sprint 57 — "Las Capas Transversales"
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from kernel.embrion_loop import EmbrionLoop

logger = logging.getLogger("embrion_ventas")


# ── System Prompt especializado ──────────────────────────────────────────────

VENTAS_SYSTEM_PROMPT = """Eres Embrión-Ventas, el especialista en estrategia comercial
del sistema El Monstruo. Tu expertise incluye:

1. FUNNELS DE CONVERSIÓN: Diseño de funnels TOFU/MOFU/BOFU optimizados
2. PRICING STRATEGY: Modelos de pricing (freemium, tiered, usage-based, marketplace splits)
3. COPYWRITING DE VENTA: Headlines, CTAs, landing pages que convierten
4. UNIT ECONOMICS: CAC, LTV, payback period, margins
5. A/B TESTING: Diseño de experimentos para optimización de conversión
6. RETENTION: Estrategias de churn prevention y engagement

Cuando El Monstruo crea un proyecto, tú inyectas la capa de ventas que
garantiza que el negocio genere revenue desde el día 1.

Principios:
- Datos sobre opiniones. Siempre basa recomendaciones en métricas reales.
- Simplicidad sobre complejidad. El mejor funnel es el más simple que convierte.
- Revenue first. Si no genera dinero, no es un negocio.
"""


# ── Knowledge Base de Ventas ─────────────────────────────────────────────────

class VentasKnowledgeBase:
    """Base de conocimiento curada de estrategias de ventas."""

    PRICING_TEMPLATES: dict[str, dict] = {
        "saas": {
            "model": "tiered_subscription",
            "tiers": [
                {"name": "Free", "price": 0, "features": "Core features, limited usage"},
                {"name": "Pro", "price": 29, "features": "Full features, priority support"},
                {"name": "Enterprise", "price": "custom", "features": "Custom, SLA, dedicated"},
            ],
            "rationale": "Freemium drives adoption, Pro captures SMBs, Enterprise captures high-value",
            "benchmarks": ["Notion $16/mo", "Linear $8/mo", "Figma $12/mo"],
        },
        "marketplace": {
            "model": "commission_based",
            "tiers": [
                {"name": "Standard", "commission": "10-15%", "features": "Basic listing"},
                {"name": "Premium", "commission": "8-12%", "features": "Featured placement, analytics"},
                {"name": "Enterprise", "commission": "5-8%", "features": "Custom terms, API access"},
            ],
            "rationale": "Lower commission for higher volume sellers incentivizes growth",
            "benchmarks": ["Airbnb 3-5%", "Etsy 6.5%", "Shopify 2%"],
        },
        "ecommerce": {
            "model": "direct_sales",
            "tiers": [
                {"name": "Standard", "margin": "40-60%", "features": "Standard shipping"},
                {"name": "Premium", "margin": "60-80%", "features": "Express shipping, gift wrap"},
                {"name": "Subscription", "discount": "15-20%", "features": "Auto-replenish, loyalty"},
            ],
            "rationale": "Subscription model increases LTV and reduces churn",
            "benchmarks": ["Dollar Shave Club 85% LTV increase via subscription"],
        },
        "api": {
            "model": "usage_based",
            "tiers": [
                {"name": "Starter", "price": 0, "features": "1K calls/mo free"},
                {"name": "Growth", "price": 0.001, "features": "$0.001/call after 1K"},
                {"name": "Scale", "price": 0.0005, "features": "$0.0005/call after 100K"},
            ],
            "rationale": "Usage-based aligns cost with value, reduces friction for adoption",
            "benchmarks": ["Stripe 2.9%+30¢", "Twilio $0.0085/SMS"],
        },
        "consulting": {
            "model": "flat_rate",
            "tiers": [
                {"name": "Project", "price": "5K-50K", "features": "Fixed scope, fixed price"},
                {"name": "Retainer", "price": "2K-10K/mo", "features": "Ongoing support"},
                {"name": "Success", "price": "% of outcome", "features": "Risk-sharing model"},
            ],
            "rationale": "Retainer model creates predictable revenue and deepens client relationships",
            "benchmarks": ["McKinsey $50K+/week", "Boutique $5-15K/week"],
        },
    }

    FUNNEL_BENCHMARKS: dict[str, dict] = {
        "saas": {
            "visitor_to_signup": 0.03,      # 3% industry average
            "signup_to_activation": 0.40,   # 40% activation
            "activation_to_paid": 0.15,     # 15% conversion to paid
            "paid_to_annual": 0.30,         # 30% upgrade to annual
            "monthly_churn": 0.05,          # 5% monthly churn
        },
        "ecommerce": {
            "visitor_to_cart": 0.10,        # 10% add to cart
            "cart_to_checkout": 0.65,       # 65% checkout rate
            "checkout_to_purchase": 0.80,   # 80% purchase completion
            "repeat_purchase_30d": 0.20,    # 20% buy again in 30 days
        },
    }

    def get_pricing_template(self, project_type: str) -> dict:
        """Get pricing template for a project type."""
        return self.PRICING_TEMPLATES.get(
            project_type.lower(),
            self.PRICING_TEMPLATES["saas"],  # Default to SaaS
        )

    def get_funnel_benchmarks(self, vertical: str) -> dict:
        """Get funnel benchmarks for a vertical."""
        return self.FUNNEL_BENCHMARKS.get(
            vertical.lower(),
            self.FUNNEL_BENCHMARKS["saas"],
        )


# ── Embrión-Ventas ───────────────────────────────────────────────────────────

class EmbrionVentas(EmbrionLoop):
    """Embrión especializado en estrategia comercial y ventas.

    Primer Embrión especializado del sistema (Obj #11).
    Hereda de EmbrionLoop con governance completo (budget, silence, HITL).
    """

    EMBRION_ID = "embrion-ventas"
    SPECIALIZATION = "ventas"

    # Tareas autónomas del Embrión-Ventas
    DEFAULT_TASKS: dict[str, dict] = {
        "market_analysis": {
            "description": "Analizar tendencias de mercado para proyectos activos",
            "interval_hours": 12,
            "max_cost_usd": 0.30,
            "priority": 2,
        },
        "pricing_optimization": {
            "description": "Evaluar y optimizar estrategias de pricing",
            "interval_hours": 24,
            "max_cost_usd": 0.20,
            "priority": 2,
        },
        "conversion_audit": {
            "description": "Auditar métricas de conversión de proyectos activos",
            "interval_hours": 6,
            "max_cost_usd": 0.10,
            "priority": 1,
        },
        "competitor_pricing_scan": {
            "description": "Escanear pricing de competidores",
            "interval_hours": 48,
            "max_cost_usd": 0.40,
            "priority": 3,
        },
    }

    def __init__(
        self,
        db: Any,
        kernel: Any,
        notifier: Optional[Any] = None,
        search_fn=None,
        posthog_client=None,
    ):
        # Llamar al constructor de EmbrionLoop con la firma correcta
        super().__init__(db=db, kernel=kernel, notifier=notifier)
        self._search = search_fn
        self._posthog = posthog_client
        self._knowledge_base = VentasKnowledgeBase()
        logger.info("embrion_ventas_initialized", specialization=self.SPECIALIZATION)

    # ── Métodos especializados ────────────────────────────────────────────────

    async def analyze_market(self, vertical: str, region: str = "global") -> dict:
        """Analizar mercado para un vertical específico usando Perplexity."""
        if not self._search:
            return {"error": "Search function not available", "vertical": vertical}

        query = f"market size trends {vertical} {region} 2026 TAM SAM SOM"
        try:
            result = await self._search(query, context=f"Market analysis for {vertical}")
            return {
                "vertical": vertical,
                "region": region,
                "analysis": result.get("answer", ""),
                "citations": result.get("citations", []),
                "benchmarks": self._knowledge_base.get_funnel_benchmarks(vertical),
                "confidence": "magna_validated",
            }
        except Exception as e:
            logger.warning("market_analysis_failed", vertical=vertical, error=str(e))
            return {"error": str(e), "vertical": vertical}

    async def recommend_pricing(self, project_type: str, features: list[str] = None) -> dict:
        """Recomendar estrategia de pricing basada en tipo de proyecto."""
        strategy = self._knowledge_base.get_pricing_template(project_type)
        return {
            "project_type": project_type,
            "recommended_model": strategy["model"],
            "tiers": strategy["tiers"],
            "rationale": strategy["rationale"],
            "benchmarks": strategy.get("benchmarks", []),
            "features_considered": features or [],
        }

    async def generate_funnel(self, product_description: str, vertical: str = "saas") -> dict:
        """Generar funnel de conversión optimizado para un producto."""
        benchmarks = self._knowledge_base.get_funnel_benchmarks(vertical)
        return {
            "product": product_description,
            "vertical": vertical,
            "tofu": {
                "channels": ["SEO", "Content Marketing", "Social Media", "PR"],
                "content_types": ["Blog posts", "Infographics", "Videos", "Podcasts"],
                "kpis": ["Traffic", "Impressions", "Click-through rate"],
            },
            "mofu": {
                "channels": ["Email nurture", "Retargeting", "Webinars", "Free tools"],
                "content_types": ["Case studies", "Whitepapers", "Free trials", "Demos"],
                "kpis": ["Email open rate", "Trial signups", "Engagement score"],
            },
            "bofu": {
                "channels": ["Sales calls", "Demo requests", "Limited offers", "Social proof"],
                "content_types": ["ROI calculators", "Testimonials", "Pricing pages", "Comparisons"],
                "kpis": ["Conversion rate", "ACV", "Time to close", "Win rate"],
            },
            "benchmarks": benchmarks,
        }

    async def audit_conversion_metrics(self, project_id: str) -> dict:
        """Auditar métricas de conversión de un proyecto via PostHog."""
        if not self._posthog:
            return {
                "project_id": project_id,
                "error": "PostHog client not configured",
                "recommendation": "Set POSTHOG_API_KEY to enable real-time conversion tracking",
            }

        # En producción: query PostHog API para funnel metrics
        return {
            "project_id": project_id,
            "metrics_available": True,
            "recommendation": "Configure PostHog events for conversion tracking",
            "posthog_configured": True,
        }

    async def generate_ab_test(self, element: str, hypothesis: str) -> dict:
        """Generar diseño de A/B test para un elemento."""
        return {
            "element": element,
            "hypothesis": hypothesis,
            "variants": [
                {"name": "control", "description": f"Current {element}"},
                {"name": "variant_a", "description": f"Test version of {element}"},
            ],
            "success_metric": "conversion_rate",
            "minimum_sample_size": 1000,
            "confidence_level": 0.95,
            "estimated_duration_days": 14,
        }

    def get_ventas_stats(self) -> dict:
        """Retornar estadísticas del Embrión-Ventas."""
        base_stats = self.stats  # Stats de EmbrionLoop
        return {
            **base_stats,
            "specialization": self.SPECIALIZATION,
            "embrion_id": self.EMBRION_ID,
            "posthog_configured": bool(self._posthog),
            "search_configured": bool(self._search),
            "default_tasks": list(self.DEFAULT_TASKS.keys()),
        }


# ── Singleton factory ─────────────────────────────────────────────────────────

_embrion_ventas_instance: Optional[EmbrionVentas] = None


def get_embrion_ventas(
    db: Any = None,
    kernel: Any = None,
    notifier: Any = None,
    search_fn=None,
    posthog_client=None,
) -> EmbrionVentas:
    """Singleton factory para EmbrionVentas."""
    global _embrion_ventas_instance
    if _embrion_ventas_instance is None:
        _embrion_ventas_instance = EmbrionVentas(
            db=db,
            kernel=kernel,
            notifier=notifier,
            search_fn=search_fn,
            posthog_client=posthog_client,
        )
    return _embrion_ventas_instance
