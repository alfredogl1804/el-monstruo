"""kernel/motion/tokens.py

Motion Design Tokens — Sprint 63.3
Objetivo #2: Nivel Apple/Tesla

El vocabulario de movimiento de El Monstruo. Tokens de duración, easing
y distancia que definen cómo se mueven los elementos en la interfaz.
No animaciones aleatorias — un sistema coherente con propósito.

Soberanía:
    - Motion tokens: CSS custom properties → sin dependencia de librería JS
    - Framer Motion / Motion: alternativa → CSS transitions nativas
"""

from dataclasses import dataclass

import structlog

logger = structlog.get_logger("motion.tokens")


# ── Modelo de datos ────────────────────────────────────────────────────────────


@dataclass
class MotionToken:
    """Token de movimiento del sistema de diseño.

    Args:
        name: Nombre del token
        duration: Duración CSS ("200ms", "0.3s") o "spring"
        easing: Función de easing CSS o config de spring
        distance: Distancia de movimiento ("4px", "16px", "auto")
        description: Descripción del uso del token

    Returns:
        MotionToken listo para generar CSS custom properties

    Soberanía:
        CSS: compatible con cualquier framework frontend
    """

    name: str
    duration: str
    easing: str
    distance: str
    description: str

    def to_css_var(self) -> str:
        """Generar CSS custom property."""
        return f"--motion-{self.name}: {self.duration};"

    def to_dict(self) -> dict:
        """Serializar para Command Center."""
        return {
            "name": self.name,
            "duration": self.duration,
            "easing": self.easing,
            "distance": self.distance,
            "description": self.description,
        }


# ── Tokens de movimiento ───────────────────────────────────────────────────────

MOTION_TOKENS: dict = {
    # Duraciones
    "instant": MotionToken("instant", "100ms", "ease-out", "0", "Micro-feedback, toggles"),
    "fast": MotionToken("fast", "200ms", "ease-out", "4px", "Button states, tooltips"),
    "normal": MotionToken("normal", "300ms", "cubic-bezier(0.4, 0, 0.2, 1)", "8px", "Transiciones estándar"),
    "slow": MotionToken("slow", "500ms", "cubic-bezier(0.4, 0, 0.2, 1)", "16px", "Elementos entrando"),
    "deliberate": MotionToken("deliberate", "800ms", "cubic-bezier(0.22, 1, 0.36, 1)", "32px", "Hero animations"),
    "cinematic": MotionToken("cinematic", "1200ms", "cubic-bezier(0.22, 1, 0.36, 1)", "64px", "Transiciones de página"),
    # Springs (para Motion/Framer Motion)
    "spring_snappy": MotionToken(
        "spring_snappy", "spring", "stiffness:400,damping:30", "auto", "Interacciones rápidas"
    ),
    "spring_gentle": MotionToken("spring_gentle", "spring", "stiffness:120,damping:14", "auto", "Movimientos suaves"),
    "spring_bouncy": MotionToken("spring_bouncy", "spring", "stiffness:300,damping:10", "auto", "Rebotes lúdicos"),
    "spring_stiff": MotionToken("spring_stiff", "spring", "stiffness:500,damping:40", "auto", "Respuesta inmediata"),
    "spring_wobbly": MotionToken(
        "spring_wobbly", "spring", "stiffness:180,damping:8", "auto", "Animaciones expresivas"
    ),
}


# ── Presets de animación ───────────────────────────────────────────────────────

INTERACTION_PRESETS: dict = {
    "button_hover": {
        "scale": 1.02,
        "transition": {"type": "spring", "stiffness": 400, "damping": 30},
    },
    "button_tap": {
        "scale": 0.98,
        "transition": {"type": "spring", "stiffness": 400, "damping": 30},
    },
    "card_hover": {
        "y": -4,
        "shadow": "0 20px 40px rgba(0,0,0,0.1)",
        "transition": {"duration": 0.3, "ease": [0.4, 0, 0.2, 1]},
    },
    "fade_in": {
        "initial": {"opacity": 0, "y": 20},
        "animate": {"opacity": 1, "y": 0},
        "transition": {"duration": 0.5, "ease": [0.4, 0, 0.2, 1]},
    },
    "fade_out": {
        "animate": {"opacity": 0, "y": -10},
        "transition": {"duration": 0.3, "ease": [0.4, 0, 1, 1]},
    },
    "slide_in_left": {
        "initial": {"opacity": 0, "x": -40},
        "animate": {"opacity": 1, "x": 0},
        "transition": {"duration": 0.6, "ease": [0.22, 1, 0.36, 1]},
    },
    "slide_in_right": {
        "initial": {"opacity": 0, "x": 40},
        "animate": {"opacity": 1, "x": 0},
        "transition": {"duration": 0.6, "ease": [0.22, 1, 0.36, 1]},
    },
    "slide_in_up": {
        "initial": {"opacity": 0, "y": 40},
        "animate": {"opacity": 1, "y": 0},
        "transition": {"duration": 0.6, "ease": [0.22, 1, 0.36, 1]},
    },
    "scale_in": {
        "initial": {"opacity": 0, "scale": 0.9},
        "animate": {"opacity": 1, "scale": 1},
        "transition": {"type": "spring", "stiffness": 200, "damping": 20},
    },
    "scale_out": {
        "animate": {"opacity": 0, "scale": 0.95},
        "transition": {"duration": 0.2},
    },
    "stagger_children": {
        "animate": {"transition": {"staggerChildren": 0.1, "delayChildren": 0.2}},
    },
    "scroll_reveal": {
        "initial": {"opacity": 0, "y": 60},
        "whileInView": {"opacity": 1, "y": 0},
        "viewport": {"once": True, "margin": "-100px"},
        "transition": {"duration": 0.7, "ease": [0.22, 1, 0.36, 1]},
    },
    "page_enter": {
        "initial": {"opacity": 0},
        "animate": {"opacity": 1},
        "exit": {"opacity": 0},
        "transition": {"duration": 0.3},
    },
    "parallax_slow": {
        "style": {"y": "calc(var(--scroll-y) * -0.3)"},
    },
    "parallax_fast": {
        "style": {"y": "calc(var(--scroll-y) * -0.6)"},
    },
}


# ── Perfiles de movimiento por estilo ─────────────────────────────────────────

STYLE_MOTION_PROFILES: dict = {
    "minimal": {
        "default_duration": "300ms",
        "default_easing": "cubic-bezier(0.4, 0, 0.2, 1)",
        "hover_scale": 1.01,
        "entrance": "fade_in",
        "stagger_delay": 0.08,
        "use_springs": False,
        "reduced_motion_safe": True,
    },
    "bold": {
        "default_duration": "400ms",
        "default_easing": "cubic-bezier(0.22, 1, 0.36, 1)",
        "hover_scale": 1.05,
        "entrance": "scale_in",
        "stagger_delay": 0.12,
        "use_springs": True,
        "reduced_motion_safe": False,
    },
    "elegant": {
        "default_duration": "600ms",
        "default_easing": "cubic-bezier(0.4, 0, 0.2, 1)",
        "hover_scale": 1.02,
        "entrance": "slide_in_left",
        "stagger_delay": 0.15,
        "use_springs": False,
        "reduced_motion_safe": True,
    },
    "playful": {
        "default_duration": "500ms",
        "default_easing": "spring",
        "hover_scale": 1.05,
        "entrance": "scale_in",
        "stagger_delay": 0.1,
        "use_springs": True,
        "reduced_motion_safe": False,
    },
    "smooth": {
        "default_duration": "500ms",
        "default_easing": "cubic-bezier(0.22, 1, 0.36, 1)",
        "hover_scale": 1.02,
        "entrance": "fade_in",
        "stagger_delay": 0.1,
        "use_springs": False,
        "reduced_motion_safe": True,
    },
    "energetic": {
        "default_duration": "350ms",
        "default_easing": "cubic-bezier(0.22, 1, 0.36, 1)",
        "hover_scale": 1.04,
        "entrance": "slide_in_up",
        "stagger_delay": 0.07,
        "use_springs": True,
        "reduced_motion_safe": False,
    },
    "gentle": {
        "default_duration": "600ms",
        "default_easing": "cubic-bezier(0.4, 0, 0.2, 1)",
        "hover_scale": 1.01,
        "entrance": "fade_in",
        "stagger_delay": 0.12,
        "use_springs": False,
        "reduced_motion_safe": True,
    },
    "clean": {
        "default_duration": "300ms",
        "default_easing": "ease-in-out",
        "hover_scale": 1.01,
        "entrance": "fade_in",
        "stagger_delay": 0.08,
        "use_springs": False,
        "reduced_motion_safe": True,
    },
    "vibrant": {
        "default_duration": "400ms",
        "default_easing": "cubic-bezier(0.22, 1, 0.36, 1)",
        "hover_scale": 1.03,
        "entrance": "scale_in",
        "stagger_delay": 0.09,
        "use_springs": True,
        "reduced_motion_safe": False,
    },
    "friendly": {
        "default_duration": "400ms",
        "default_easing": "cubic-bezier(0.34, 1.56, 0.64, 1)",
        "hover_scale": 1.03,
        "entrance": "scale_in",
        "stagger_delay": 0.1,
        "use_springs": True,
        "reduced_motion_safe": False,
    },
}
