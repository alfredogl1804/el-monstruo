"""kernel/motion/orchestrator.py

Motion Orchestrator — Sprint 63.3
Objetivo #2: Nivel Apple/Tesla

Orquesta animaciones a nivel de página para crear experiencias visuales
coherentes. Genera configuración de animaciones para cada componente
basándose en el perfil de movimiento del estilo visual del proyecto.

Soberanía:
    - Motion/Framer Motion: alternativa → CSS transitions + Intersection Observer
    - Configuración: JSON exportable → compatible con cualquier librería de animación
"""

import structlog
from typing import Optional
from kernel.motion.tokens import (
    INTERACTION_PRESETS,
    STYLE_MOTION_PROFILES,
    MOTION_TOKENS,
)
from kernel.utils.keyword_matcher import compile_keyword_pattern, match_any_keyword

logger = structlog.get_logger("motion.orchestrator")

# Sprint 84.7: Patterns precompilados (anti substring).
# treat_underscore_as_separator=True porque los nombres de componentes son
# snake_case ("hero_button", "product_card") y queremos que `button` matchee.
_BUTTON_LIKE_PATTERN = compile_keyword_pattern(
    ("button", "cta", "btn", "link"),
    treat_underscore_as_separator=True,
)
_CARD_LIKE_PATTERN = compile_keyword_pattern(
    ("card", "product", "item", "tile"),
    treat_underscore_as_separator=True,
)

# ── Errores con identidad ──────────────────────────────────────────────────────

ORCHESTRATOR_ESTILO_NO_ENCONTRADO = (
    "El estilo de movimiento especificado no existe en el catálogo. "
    "Se usará 'minimal' como fallback. Estilos disponibles: minimal, bold, elegant, playful."
)
ORCHESTRATOR_COMPONENTE_INVALIDO = (
    "El nombre de componente no puede estar vacío. "
    "Proporciona un identificador válido como 'hero', 'navbar', 'card_grid'."
)


class MotionOrchestrator:
    """Orquestador de animaciones para páginas completas.

    Genera configuración de animaciones coherente para todos los componentes
    de una página, respetando el perfil de movimiento del estilo visual.

    Args:
        style: Perfil de movimiento ("minimal", "bold", "elegant", "playful", etc.)

    Returns:
        Orquestador listo para generar configuraciones de animación

    Raises:
        ValueError: Si el estilo no existe (usa fallback "minimal")

    Soberanía:
        Motion library: alternativa → CSS transitions + Intersection Observer API
        Configuración: JSON puro → compatible con React, Vue, Svelte, vanilla JS
    """

    def __init__(self, style: str = "minimal"):
        if style not in STYLE_MOTION_PROFILES:
            logger.warning(
                "estilo_no_encontrado",
                style=style,
                hint=ORCHESTRATOR_ESTILO_NO_ENCONTRADO,
            )
            style = "minimal"
        self.style = style
        self.profile = STYLE_MOTION_PROFILES[style]
        logger.info("orchestrator_init", style=style, use_springs=self.profile["use_springs"])

    def get_page_animations(self, components: list) -> dict:
        """Generar configuración de animaciones para una página completa.

        Args:
            components: Lista de nombres de componentes en orden de aparición

        Returns:
            Dict con configuración de animación para cada componente

        Raises:
            ValueError: Si components está vacío

        Soberanía:
            Configuración: JSON puro exportable a cualquier framework
        """
        if not components:
            return {}

        animations = {}
        for i, component in enumerate(components):
            if not component:
                logger.warning("componente_invalido", hint=ORCHESTRATOR_COMPONENTE_INVALIDO)
                continue
            animations[component] = {
                "entrance": self._get_entrance(component, i),
                "interactions": self._get_interactions(component),
                "scroll": self._get_scroll_behavior(component, i),
                "exit": INTERACTION_PRESETS.get("fade_out", {}),
            }

        logger.info("page_animations_generated", components=len(animations), style=self.style)
        return animations

    def get_component_animation(self, component: str, index: int = 0) -> dict:
        """Obtener animación para un componente individual.

        Args:
            component: Nombre del componente
            index: Posición en la página (afecta delay de stagger)

        Returns:
            Dict con entrance, interactions y scroll behavior

        Soberanía:
            Sin librería: genera CSS equivalente via generate_motion_css()
        """
        return {
            "entrance": self._get_entrance(component, index),
            "interactions": self._get_interactions(component),
            "scroll": self._get_scroll_behavior(component, index),
        }

    def _get_entrance(self, component: str, index: int) -> dict:
        """Obtener animación de entrada para un componente."""
        entrance_preset = self.profile.get("entrance", "fade_in")
        base = dict(INTERACTION_PRESETS.get(entrance_preset, INTERACTION_PRESETS["fade_in"]))

        # Agregar delay de stagger basado en posición
        delay = index * self.profile.get("stagger_delay", 0.08)
        if "transition" in base and isinstance(base["transition"], dict):
            base["transition"] = dict(base["transition"])
            base["transition"]["delay"] = round(delay, 3)

        return base

    def _get_interactions(self, component: str) -> dict:
        """Obtener animaciones de interacción para un componente."""
        interactions = {}
        component_lower = component.lower()

        # Hover para todos los componentes
        hover_scale = self.profile.get("hover_scale", 1.02)
        if self.profile.get("use_springs"):
            interactions["hover"] = {
                "scale": hover_scale,
                "transition": {"type": "spring", "stiffness": 400, "damping": 30},
            }
        else:
            interactions["hover"] = {
                "scale": hover_scale,
                "transition": {"duration": 0.2},
            }

        # Tap para botones y CTAs
        # Sprint 84.7: word boundaries via _BUTTON_LIKE_PATTERN
        if match_any_keyword(component_lower, _BUTTON_LIKE_PATTERN):
            interactions["tap"] = dict(INTERACTION_PRESETS["button_tap"])

        # Lift para cards y productos
        # Sprint 84.7: word boundaries via _CARD_LIKE_PATTERN
        if match_any_keyword(component_lower, _CARD_LIKE_PATTERN):
            interactions["hover"] = dict(INTERACTION_PRESETS["card_hover"])

        return interactions

    def _get_scroll_behavior(self, component: str, index: int) -> dict:
        """Obtener animación activada por scroll."""
        # El primer componente (hero) no necesita scroll trigger
        if index == 0:
            return {}
        return dict(INTERACTION_PRESETS["scroll_reveal"])

    def generate_motion_css(self) -> str:
        """Generar CSS custom properties para los motion tokens.

        Returns:
            String CSS con variables y media query prefers-reduced-motion

        Soberanía:
            CSS puro — sin dependencia de JavaScript
        """
        return f"""
/* Motion Design System — El Monstruo Sprint 63.3 */
/* Estilo: {self.style} */
:root {{
  --motion-duration-instant: 100ms;
  --motion-duration-fast: 200ms;
  --motion-duration-normal: 300ms;
  --motion-duration-slow: 500ms;
  --motion-duration-deliberate: 800ms;
  --motion-duration-cinematic: 1200ms;
  --motion-easing-default: {self.profile['default_easing']};
  --motion-easing-enter: cubic-bezier(0, 0, 0.2, 1);
  --motion-easing-exit: cubic-bezier(0.4, 0, 1, 1);
  --motion-easing-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --motion-easing-spring: cubic-bezier(0.22, 1, 0.36, 1);
  --motion-hover-scale: {self.profile['hover_scale']};
}}

/* Accesibilidad: respetar preferencia de movimiento reducido */
@media (prefers-reduced-motion: reduce) {{
  :root {{
    --motion-duration-instant: 0ms;
    --motion-duration-fast: 0ms;
    --motion-duration-normal: 0ms;
    --motion-duration-slow: 0ms;
    --motion-duration-deliberate: 0ms;
    --motion-duration-cinematic: 0ms;
  }}
  *, *::before, *::after {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }}
}}
"""

    def generate_framer_config(self, components: list) -> dict:
        """Generar configuración completa para Framer Motion / Motion library.

        Args:
            components: Lista de componentes de la página

        Returns:
            Dict con configuración lista para usar en React con Motion

        Soberanía:
            Motion library: alternativa → CSS animations + Intersection Observer
        """
        page_animations = self.get_page_animations(components)
        return {
            "style": self.style,
            "profile": self.profile,
            "components": page_animations,
            "global_tokens": {
                name: token.to_dict()
                for name, token in MOTION_TOKENS.items()
            },
            "css_variables": self.generate_motion_css(),
        }

    def to_dict(self) -> dict:
        """Serializar estado para Command Center."""
        return {
            "module": "MotionOrchestrator",
            "sprint": "63.3",
            "objetivo": "#2 Nivel Apple/Tesla",
            "style": self.style,
            "tokens_available": len(MOTION_TOKENS),
            "presets_available": len(INTERACTION_PRESETS),
            "profiles_available": len(STYLE_MOTION_PROFILES),
            "use_springs": self.profile.get("use_springs", False),
            "reduced_motion_safe": self.profile.get("reduced_motion_safe", True),
        }


# ── Singleton ──────────────────────────────────────────────────────────────────

_motion_orchestrator: Optional[MotionOrchestrator] = None


def get_motion_orchestrator() -> Optional[MotionOrchestrator]:
    """Obtener instancia singleton del orquestador de movimiento."""
    return _motion_orchestrator


def init_motion_orchestrator(style: str = "minimal") -> MotionOrchestrator:
    """Inicializar el orquestador de movimiento.

    Args:
        style: Perfil de movimiento inicial

    Returns:
        MotionOrchestrator inicializado

    Soberanía:
        CSS puro disponible via generate_motion_css() sin Motion library
    """
    global _motion_orchestrator
    _motion_orchestrator = MotionOrchestrator(style=style)
    logger.info("motion_orchestrator_ready", style=style)
    return _motion_orchestrator
