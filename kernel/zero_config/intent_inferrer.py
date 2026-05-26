"""kernel/zero_config/intent_inferrer.py

Inferidor de Intención — Sprint 63.2
Objetivo #3: Mínima Complejidad

Un usuario nuevo debe poder crear su primer proyecto funcional en menos
de 60 segundos, sin llenar un solo formulario. El sistema infiere todo
lo necesario a partir de una sola frase.

Soberanía:
    - Inferencia local: sin dependencia de LLM para casos simples
    - LLM: GPT-4o-mini → Gemini Flash para casos ambiguos
"""

import re
from dataclasses import dataclass
from typing import Optional

import structlog

logger = structlog.get_logger("zero_config.inferrer")

# ── Errores con identidad ──────────────────────────────────────────────────────

INFERRER_INPUT_VACIO = (
    "El texto de entrada está vacío. "
    "Proporciona una descripción de tu proyecto, por ejemplo: 'Quiero una tienda de ropa'."
)
INFERRER_CONFIANZA_BAJA = (
    "La confianza en la inferencia es baja. "
    "Agrega más detalles sobre tu industria o tipo de proyecto para mejorar la precisión."
)


# ── Patrones de detección ──────────────────────────────────────────────────────

INDUSTRY_PATTERNS: dict = {
    "restaurant": ["restaurante", "comida", "menu", "food", "cafe", "bar", "cocina", "chef", "taqueria", "pizzeria"],
    "fitness": ["gym", "fitness", "yoga", "crossfit", "entrenamiento", "workout", "deporte", "pilates"],
    "tech": ["saas", "app", "software", "startup", "api", "platform", "tech", "sistema", "plataforma"],
    "fashion": ["moda", "ropa", "tienda", "boutique", "fashion", "clothing", "store", "zapatos", "accesorios"],
    "real_estate": ["inmobiliaria", "propiedades", "real estate", "apartments", "casas", "departamentos"],
    "education": ["escuela", "cursos", "academia", "learning", "education", "tutoring", "clases", "universidad"],
    "health": ["clinica", "doctor", "salud", "health", "medical", "dental", "therapy", "hospital", "farmacia"],
    "creative": ["fotografia", "diseno", "portfolio", "creative", "art", "design", "studio", "agencia"],
    "consulting": ["consultoria", "consulting", "advisory", "coaching", "mentoring", "asesoria"],
    "ecommerce": ["tienda", "vender", "productos", "shop", "ecommerce", "marketplace", "catalogo"],
    "food_delivery": ["delivery", "pedidos", "domicilio", "entrega", "repartidor"],
    "travel": ["viajes", "turismo", "hotel", "hospedaje", "tours", "travel", "booking"],
}

TYPE_PATTERNS: dict = {
    "ecommerce": ["tienda", "vender", "shop", "store", "productos", "carrito", "checkout", "comprar"],
    "saas": ["saas", "dashboard", "usuarios", "suscripcion", "subscription", "platform", "admin"],
    "portfolio": ["portfolio", "portafolio", "proyectos", "trabajos", "showcase", "galeria"],
    "blog": ["blog", "articulos", "contenido", "posts", "noticias", "magazine", "revista"],
    "landing": ["landing", "pagina", "presentar", "negocio", "empresa", "servicio", "presentacion"],
    "booking": ["reservas", "citas", "agenda", "booking", "calendario", "turnos"],
    "directory": ["directorio", "listado", "guia", "catalogo", "buscador", "directorio"],
}


# ── Modelo de datos ────────────────────────────────────────────────────────────


@dataclass
class InferredProject:
    """Configuración de proyecto inferida de una sola frase.

    Args:
        project_type: Tipo de proyecto inferido
        industry: Industria detectada
        locale: Locale del usuario
        features: Lista de features inferidas
        style: Estilo visual inferido
        name: Nombre del proyecto (si se detecta)
        description: Descripción original del usuario
        confidence: Confianza de la inferencia 0-1
        inferred_from: Texto original de entrada

    Returns:
        InferredProject con toda la configuración necesaria para crear el proyecto

    Raises:
        ValueError: Si el input está vacío (INFERRER_INPUT_VACIO)

    Soberanía:
        Inferencia: heurísticas locales → sin dependencia de LLM
    """

    project_type: str
    industry: str
    locale: str
    features: list
    style: str
    name: Optional[str] = None
    description: Optional[str] = None
    confidence: float = 0.0
    inferred_from: str = ""

    def to_dict(self) -> dict:
        """Serializar para Command Center."""
        return {
            "project_type": self.project_type,
            "industry": self.industry,
            "locale": self.locale,
            "features": self.features,
            "style": self.style,
            "name": self.name,
            "description": self.description,
            "confidence": round(self.confidence, 3),
            "inferred_from": self.inferred_from[:100],
        }


# ── Inferidor principal ────────────────────────────────────────────────────────


class IntentInferrer:
    """Inferir configuración completa de proyecto desde una sola frase.

    Usa heurísticas locales para detectar tipo de proyecto, industria,
    features y estilo visual sin necesidad de formularios ni LLM.

    Args:
        (sin argumentos — inferencia completamente local)

    Returns:
        Inferidor listo para procesar frases en español e inglés

    Raises:
        ValueError: Si el input está vacío

    Soberanía:
        Inferencia: heurísticas locales → 0 dependencias externas
        LLM: disponible como mejora opcional para casos ambiguos
    """

    async def infer(self, user_input: str, user_locale: str = "es-MX") -> InferredProject:
        """Inferir configuración de proyecto desde lenguaje natural.

        Args:
            user_input: Descripción del proyecto en lenguaje natural
            user_locale: Locale del usuario (default: es-MX)

        Returns:
            InferredProject con configuración completa

        Raises:
            ValueError: Si user_input está vacío

        Soberanía:
            Sin LLM: inferencia basada en patrones de palabras clave
        """
        if not user_input or not user_input.strip():
            raise ValueError(INFERRER_INPUT_VACIO)

        input_lower = user_input.lower()

        project_type = self._detect_type(input_lower)
        industry = self._detect_industry(input_lower)
        features = self._infer_features(project_type, industry)
        style = self._infer_style(industry)
        confidence = self._calculate_confidence(project_type, industry, input_lower)

        result = InferredProject(
            project_type=project_type,
            industry=industry,
            locale=user_locale,
            features=features,
            style=style,
            name=self._extract_name(user_input),
            description=user_input,
            confidence=confidence,
            inferred_from=user_input,
        )

        logger.info(
            "intent_inferred",
            type=project_type,
            industry=industry,
            confidence=round(confidence, 3),
            features_count=len(features),
        )

        if confidence < 0.3:
            logger.warning("confianza_baja", confidence=confidence, hint=INFERRER_CONFIANZA_BAJA)

        return result

    def _detect_type(self, text: str) -> str:
        """Detectar tipo de proyecto desde texto."""
        scores: dict = {}
        for ptype, patterns in TYPE_PATTERNS.items():
            scores[ptype] = sum(1 for p in patterns if p in text)
        if max(scores.values(), default=0) > 0:
            return max(scores, key=lambda k: scores[k])
        return "landing"  # Default

    def _detect_industry(self, text: str) -> str:
        """Detectar industria desde texto."""
        scores: dict = {}
        for industry, patterns in INDUSTRY_PATTERNS.items():
            scores[industry] = sum(1 for p in patterns if p in text)
        if max(scores.values(), default=0) > 0:
            return max(scores, key=lambda k: scores[k])
        return "tech"  # Default

    def _infer_features(self, project_type: str, industry: str) -> list:
        """Inferir features basadas en tipo de proyecto e industria."""
        base_features = {
            "ecommerce": ["payments", "cart", "product_catalog", "search", "auth"],
            "saas": ["auth", "dashboard", "billing", "analytics", "api"],
            "portfolio": ["gallery", "contact_form", "blog", "testimonials"],
            "blog": ["cms", "search", "categories", "newsletter", "comments"],
            "landing": ["contact_form", "testimonials", "pricing", "faq"],
            "booking": ["calendar", "reservations", "notifications", "auth"],
            "directory": ["search", "listings", "filters", "map", "reviews"],
        }
        features = list(base_features.get(project_type, ["contact_form"]))

        industry_extras = {
            "restaurant": ["menu_display", "reservations", "gallery"],
            "fitness": ["class_schedule", "membership", "trainer_profiles"],
            "real_estate": ["property_listings", "map", "virtual_tours"],
            "education": ["course_catalog", "enrollment", "progress_tracking"],
            "health": ["appointment_booking", "doctor_profiles", "telemedicine"],
            "travel": ["search", "booking", "reviews", "map", "itinerary"],
            "food_delivery": ["menu", "cart", "tracking", "payments"],
        }
        features.extend(industry_extras.get(industry, []))
        return list(set(features))

    def _infer_style(self, industry: str) -> str:
        """Inferir estilo visual basado en industria."""
        style_map = {
            "restaurant": "elegant",
            "fitness": "bold",
            "tech": "minimal",
            "fashion": "elegant",
            "creative": "playful",
            "consulting": "minimal",
            "health": "clean",
            "education": "friendly",
            "real_estate": "minimal",
            "ecommerce": "clean",
            "travel": "vibrant",
            "food_delivery": "bold",
        }
        return style_map.get(industry, "minimal")

    def _calculate_confidence(self, project_type: str, industry: str, text: str) -> float:
        """Calcular confianza basada en fuerza de las señales detectadas."""
        signals = 0
        type_matches = sum(1 for p in TYPE_PATTERNS.get(project_type, []) if p in text)
        signals += min(type_matches, 3)
        industry_matches = sum(1 for p in INDUSTRY_PATTERNS.get(industry, []) if p in text)
        signals += min(industry_matches, 3)
        if len(text) > 50:
            signals += 1
        if len(text) > 100:
            signals += 1
        return min(signals / 8.0, 0.95)

    def _extract_name(self, text: str) -> Optional[str]:
        """Intentar extraer nombre del proyecto o negocio del input."""
        # Buscar texto entre comillas
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            return quoted[0]
        # Buscar patrones "llamado/called/named X"
        named = re.search(r"(?:llamad[oa]|called|named|se llama)\s+(\w+(?:\s+\w+)?)", text, re.I)
        if named:
            return named.group(1)
        return None

    def to_dict(self) -> dict:
        """Serializar estado para Command Center."""
        return {
            "module": "IntentInferrer",
            "sprint": "63.2",
            "objetivo": "#3 Mínima Complejidad",
            "industry_patterns": len(INDUSTRY_PATTERNS),
            "type_patterns": len(TYPE_PATTERNS),
            "supported_locales": ["es-MX", "es-AR", "es-CO", "en-US"],
        }


# ── Singleton ──────────────────────────────────────────────────────────────────

_intent_inferrer: Optional[IntentInferrer] = None


def get_intent_inferrer() -> Optional[IntentInferrer]:
    """Obtener instancia singleton del inferidor de intención."""
    return _intent_inferrer


def init_intent_inferrer() -> IntentInferrer:
    """Inicializar el inferidor de intención.

    Returns:
        IntentInferrer inicializado

    Soberanía:
        Completamente local — sin dependencias externas
    """
    global _intent_inferrer
    _intent_inferrer = IntentInferrer()
    logger.info("intent_inferrer_ready", industries=len(INDUSTRY_PATTERNS))
    return _intent_inferrer
