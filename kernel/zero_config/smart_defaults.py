"""kernel/zero_config/smart_defaults.py

Smart Defaults — Sprint 63.2
Objetivo #3: Mínima Complejidad

Defaults inteligentes por industria + estilo. Sin configuración manual.
El sistema elige tipografía, colores, layout y animaciones automáticamente.

Soberanía:
    - Completamente local — sin dependencias externas
    - Alternativa: permitir al usuario sobrescribir cualquier default
"""

from dataclasses import dataclass, field

import structlog

logger = structlog.get_logger("zero_config.defaults")

# ── Errores con identidad ──────────────────────────────────────────────────────

DEFAULTS_COMBINACION_NO_ENCONTRADA = (
    "No se encontraron defaults para la combinación industria+estilo especificada. "
    "Se usará 'tech_minimal' como fallback. Puedes personalizar cualquier valor después."
)


# ── Modelo de datos ────────────────────────────────────────────────────────────


@dataclass
class ProjectDefaults:
    """Defaults completos para un proyecto.

    Args:
        theme: Tema base ("light", "dark")
        primary_color: Color primario en hex
        font_heading: Fuente para títulos
        font_body: Fuente para cuerpo de texto
        layout: Tipo de layout ("full-width", "contained", "editorial", "asymmetric")
        animations: Perfil de animaciones ("subtle", "energetic", "smooth", "playful", "gentle")
        dark_mode: Si incluye modo oscuro
        components: Lista de componentes base a incluir

    Returns:
        ProjectDefaults con toda la configuración visual

    Soberanía:
        Fuentes: Google Fonts → alternativa → system fonts stack
    """

    theme: str
    primary_color: str
    font_heading: str
    font_body: str
    layout: str
    animations: str
    dark_mode: bool
    components: list = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serializar para Command Center."""
        return {
            "theme": self.theme,
            "primary_color": self.primary_color,
            "font_heading": self.font_heading,
            "font_body": self.font_body,
            "layout": self.layout,
            "animations": self.animations,
            "dark_mode": self.dark_mode,
            "components": self.components,
        }


# ── Catálogo de defaults por industria + estilo ────────────────────────────────

SMART_DEFAULTS: dict = {
    "restaurant_elegant": ProjectDefaults(
        theme="dark",
        primary_color="#C9A96E",
        font_heading="Playfair Display",
        font_body="Lato",
        layout="full-width",
        animations="subtle",
        dark_mode=True,
        components=["hero_parallax", "feature_grid", "testimonial", "contact_form", "footer"],
    ),
    "fitness_bold": ProjectDefaults(
        theme="dark",
        primary_color="#FF4500",
        font_heading="Oswald",
        font_body="Open Sans",
        layout="full-width",
        animations="energetic",
        dark_mode=True,
        components=["hero_video", "stats_bar", "pricing_table", "testimonial", "cta_section", "footer"],
    ),
    "tech_minimal": ProjectDefaults(
        theme="light",
        primary_color="#2563EB",
        font_heading="Inter",
        font_body="Inter",
        layout="contained",
        animations="subtle",
        dark_mode=False,
        components=["navbar", "hero_split", "feature_grid", "pricing_table", "faq", "footer"],
    ),
    "fashion_elegant": ProjectDefaults(
        theme="light",
        primary_color="#1A1A1A",
        font_heading="Cormorant Garamond",
        font_body="Montserrat",
        layout="editorial",
        animations="smooth",
        dark_mode=False,
        components=["navbar", "hero_centered", "product_card", "testimonial", "newsletter", "footer"],
    ),
    "creative_playful": ProjectDefaults(
        theme="light",
        primary_color="#7C3AED",
        font_heading="Space Grotesk",
        font_body="DM Sans",
        layout="asymmetric",
        animations="playful",
        dark_mode=False,
        components=["navbar", "hero_split", "timeline", "gallery", "contact_form", "footer"],
    ),
    "health_clean": ProjectDefaults(
        theme="light",
        primary_color="#059669",
        font_heading="Nunito",
        font_body="Nunito",
        layout="contained",
        animations="gentle",
        dark_mode=False,
        components=["navbar", "hero_centered", "feature_grid", "testimonial", "contact_form", "footer"],
    ),
    "ecommerce_clean": ProjectDefaults(
        theme="light",
        primary_color="#F59E0B",
        font_heading="Poppins",
        font_body="Inter",
        layout="contained",
        animations="subtle",
        dark_mode=False,
        components=["navbar", "hero_banner", "product_grid", "cart", "checkout", "footer"],
    ),
    "consulting_minimal": ProjectDefaults(
        theme="light",
        primary_color="#1E40AF",
        font_heading="IBM Plex Sans",
        font_body="IBM Plex Sans",
        layout="contained",
        animations="subtle",
        dark_mode=False,
        components=["navbar", "hero_split", "services_grid", "team", "testimonial", "contact_form", "footer"],
    ),
    "education_friendly": ProjectDefaults(
        theme="light",
        primary_color="#7C3AED",
        font_heading="Nunito",
        font_body="Nunito",
        layout="contained",
        animations="gentle",
        dark_mode=False,
        components=["navbar", "hero_centered", "course_grid", "instructor_profiles", "pricing_table", "footer"],
    ),
    "real_estate_minimal": ProjectDefaults(
        theme="light",
        primary_color="#0F172A",
        font_heading="Raleway",
        font_body="Open Sans",
        layout="full-width",
        animations="subtle",
        dark_mode=False,
        components=["navbar", "hero_search", "property_grid", "map", "contact_form", "footer"],
    ),
    "travel_vibrant": ProjectDefaults(
        theme="light",
        primary_color="#0EA5E9",
        font_heading="Poppins",
        font_body="Inter",
        layout="full-width",
        animations="smooth",
        dark_mode=False,
        components=["navbar", "hero_parallax", "destination_grid", "testimonial", "booking_form", "footer"],
    ),
    "food_delivery_bold": ProjectDefaults(
        theme="light",
        primary_color="#EF4444",
        font_heading="Poppins",
        font_body="Inter",
        layout="full-width",
        animations="energetic",
        dark_mode=False,
        components=["navbar", "hero_banner", "category_grid", "restaurant_cards", "cart", "footer"],
    ),
}


def get_defaults(industry: str, style: str) -> ProjectDefaults:
    """Obtener defaults para una combinación industria + estilo.

    Args:
        industry: Industria detectada (ej: "restaurant", "tech")
        style: Estilo visual (ej: "elegant", "minimal", "bold")

    Returns:
        ProjectDefaults con toda la configuración visual

    Raises:
        (nunca lanza — siempre retorna un fallback)

    Soberanía:
        Sin match: usa tech_minimal como fallback universal
    """
    key = f"{industry}_{style}"

    if key in SMART_DEFAULTS:
        logger.info("defaults_found", key=key)
        return SMART_DEFAULTS[key]

    # Buscar por industria con cualquier estilo
    for k, v in SMART_DEFAULTS.items():
        if k.startswith(f"{industry}_"):
            logger.info("defaults_partial_match", key=k, requested=key)
            return v

    # Fallback universal
    logger.warning(
        "defaults_fallback",
        requested=key,
        hint=DEFAULTS_COMBINACION_NO_ENCONTRADA,
    )
    return SMART_DEFAULTS["tech_minimal"]


def list_available_combinations() -> list:
    """Listar todas las combinaciones industria+estilo disponibles."""
    return list(SMART_DEFAULTS.keys())


def to_dict() -> dict:
    """Serializar catálogo para Command Center."""
    return {
        "module": "SmartDefaults",
        "sprint": "63.2",
        "objetivo": "#3 Mínima Complejidad",
        "combinations_available": len(SMART_DEFAULTS),
        "combinations": list(SMART_DEFAULTS.keys()),
    }
