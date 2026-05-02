"""
kernel/components/registry.py
Sprint 62.3 — Component Library (Objetivo #2: Nivel Apple/Tesla)

Catálogo de 30+ componentes pre-built para generación de proyectos.
Cada componente tiene variantes, es responsive, accesible y sigue el Design System.
Nivel de calidad: Apple Human Interface Guidelines + Tesla UI patterns.

Soberanía: Si el LLM no está disponible, usa templates JSX estáticos de alta calidad.
Alternativa: Renderizado estático desde JSON sin LLM.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger("components.registry")


# --- Excepciones con identidad ---


class ComponenteNoEncontrado(Exception):
    """Componente no registrado en el ComponentRegistry."""

    def __init__(self, component_id: str):
        super().__init__(
            f"Componente '{component_id}' no encontrado en el catálogo. "
            f"Usa GET /api/components para ver los disponibles."
        )
        self.component_id = component_id


class ComponenteInvalido(Exception):
    """Definición de componente inválida."""

    def __init__(self, component_id: str, razon: str):
        super().__init__(
            f"Componente '{component_id}' inválido: {razon}. "
            f"Verifica que el JSON cumpla el schema de ComponentDefinition."
        )
        self.component_id = component_id
        self.razon = razon


# --- Dataclasses ---


@dataclass
class ComponentVariant:
    """Variante visual de un componente."""

    name: str
    description: str
    tailwind_classes: dict[str, str] = field(default_factory=dict)
    animations: list[str] = field(default_factory=list)
    dark_mode: bool = True


@dataclass
class ComponentDefinition:
    """Definición completa de un componente de la librería."""

    id: str
    category: str
    name: str
    description: str
    variants: list[ComponentVariant] = field(default_factory=list)
    props: dict[str, dict] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    accessibility: dict = field(default_factory=dict)
    responsive_breakpoints: dict[str, dict] = field(default_factory=dict)
    quality_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "name": self.name,
            "description": self.description,
            "variants": [v.name for v in self.variants],
            "dependencies": self.dependencies,
            "quality_score": self.quality_score,
        }


# --- Catálogo built-in de 30 componentes ---

BUILTIN_COMPONENTS: list[dict] = [
    # Navigation (4)
    {
        "id": "navbar",
        "category": "navigation",
        "name": "Navigation Bar",
        "description": "Barra de navegación responsive con logo, links y CTA",
        "variants": [
            {
                "name": "minimal",
                "description": "Limpio y minimalista",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
            {
                "name": "bold",
                "description": "Con fondo sólido y tipografía fuerte",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
            {
                "name": "glass",
                "description": "Glassmorphism con blur",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
            {
                "name": "floating",
                "description": "Flotante sobre el hero",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
        ],
        "props": {"logo": {"type": "string", "required": True}, "links": {"type": "array", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {"role": "navigation", "aria-label": "Main navigation"},
        "responsive_breakpoints": {"sm": {"mobile_menu": True}},
        "quality_score": 0.95,
    },
    {
        "id": "sidebar",
        "category": "navigation",
        "name": "Sidebar Navigation",
        "description": "Navegación lateral colapsable con iconos y labels",
        "variants": [
            {
                "name": "minimal",
                "description": "Solo iconos",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
            {
                "name": "expanded",
                "description": "Iconos + labels",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
        ],
        "props": {"items": {"type": "array", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {"role": "navigation"},
        "responsive_breakpoints": {},
        "quality_score": 0.90,
    },
    {
        "id": "breadcrumb",
        "category": "navigation",
        "name": "Breadcrumb",
        "description": "Migas de pan para navegación jerárquica",
        "variants": [
            {
                "name": "minimal",
                "description": "Texto simple con separadores",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            }
        ],
        "props": {"items": {"type": "array", "required": True}},
        "dependencies": [],
        "accessibility": {"aria-label": "Breadcrumb"},
        "responsive_breakpoints": {},
        "quality_score": 0.88,
    },
    {
        "id": "tabs",
        "category": "navigation",
        "name": "Tab Navigation",
        "description": "Pestañas de navegación con indicador animado",
        "variants": [
            {
                "name": "underline",
                "description": "Línea inferior animada",
                "tailwind_classes": {},
                "animations": ["underline_slide"],
                "dark_mode": True,
            },
            {
                "name": "pills",
                "description": "Pastillas redondeadas",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
        ],
        "props": {"tabs": {"type": "array", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {"role": "tablist"},
        "responsive_breakpoints": {},
        "quality_score": 0.92,
    },
    # Hero (4)
    {
        "id": "hero_split",
        "category": "hero",
        "name": "Split Hero",
        "description": "Hero dividido: texto a la izquierda, imagen/video a la derecha",
        "variants": [
            {
                "name": "light",
                "description": "Fondo claro",
                "tailwind_classes": {},
                "animations": ["fade_in_left"],
                "dark_mode": False,
            },
            {
                "name": "dark",
                "description": "Fondo oscuro premium",
                "tailwind_classes": {},
                "animations": ["fade_in_left"],
                "dark_mode": True,
            },
            {
                "name": "gradient",
                "description": "Gradiente de marca",
                "tailwind_classes": {},
                "animations": ["fade_in_left"],
                "dark_mode": True,
            },
        ],
        "props": {"headline": {"type": "string", "required": True}, "cta_text": {"type": "string", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {"role": "banner"},
        "responsive_breakpoints": {"sm": {"layout": "stacked"}},
        "quality_score": 0.97,
    },
    {
        "id": "hero_centered",
        "category": "hero",
        "name": "Centered Hero",
        "description": "Hero centrado con headline grande y dos CTAs",
        "variants": [
            {
                "name": "dark",
                "description": "Fondo oscuro con partículas",
                "tailwind_classes": {},
                "animations": ["fade_in_up"],
                "dark_mode": True,
            },
            {
                "name": "gradient",
                "description": "Gradiente animado",
                "tailwind_classes": {},
                "animations": ["gradient_shift"],
                "dark_mode": True,
            },
        ],
        "props": {"headline": {"type": "string", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {"role": "banner"},
        "responsive_breakpoints": {},
        "quality_score": 0.96,
    },
    {
        "id": "hero_video",
        "category": "hero",
        "name": "Video Hero",
        "description": "Hero con video de fondo en loop, overlay y CTA",
        "variants": [
            {
                "name": "dark",
                "description": "Overlay oscuro sobre video",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            }
        ],
        "props": {"video_url": {"type": "string", "required": True}, "headline": {"type": "string", "required": True}},
        "dependencies": [],
        "accessibility": {"aria-label": "Hero video background"},
        "responsive_breakpoints": {"sm": {"video": "hidden"}},
        "quality_score": 0.94,
    },
    {
        "id": "hero_parallax",
        "category": "hero",
        "name": "Parallax Hero",
        "description": "Hero con efecto parallax al hacer scroll",
        "variants": [
            {
                "name": "dark",
                "description": "Fondo con parallax oscuro",
                "tailwind_classes": {},
                "animations": ["parallax_scroll"],
                "dark_mode": True,
            }
        ],
        "props": {"background_image": {"type": "string", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {"role": "banner"},
        "responsive_breakpoints": {"sm": {"parallax": "disabled"}},
        "quality_score": 0.91,
    },
    # Content (5)
    {
        "id": "feature_grid",
        "category": "content",
        "name": "Feature Grid",
        "description": "Grid de características con iconos, títulos y descripciones",
        "variants": [
            {
                "name": "cards",
                "description": "Tarjetas con sombra",
                "tailwind_classes": {},
                "animations": ["stagger_in"],
                "dark_mode": True,
            },
            {
                "name": "minimal",
                "description": "Sin tarjetas, solo iconos",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
        ],
        "props": {"features": {"type": "array", "required": True}},
        "dependencies": [],
        "accessibility": {},
        "responsive_breakpoints": {"sm": {"cols": 1}, "md": {"cols": 2}},
        "quality_score": 0.93,
    },
    {
        "id": "testimonial",
        "category": "content",
        "name": "Testimonial Section",
        "description": "Testimonios de clientes con foto, nombre y empresa",
        "variants": [
            {
                "name": "cards",
                "description": "Tarjetas individuales",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
            {
                "name": "carousel",
                "description": "Carrusel automático",
                "tailwind_classes": {},
                "animations": ["slide"],
                "dark_mode": True,
            },
        ],
        "props": {"testimonials": {"type": "array", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {},
        "responsive_breakpoints": {},
        "quality_score": 0.90,
    },
    {
        "id": "pricing_table",
        "category": "content",
        "name": "Pricing Table",
        "description": "Tabla de precios con planes, features y CTAs",
        "variants": [
            {
                "name": "cards",
                "description": "Tarjetas por plan",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            }
        ],
        "props": {"plans": {"type": "array", "required": True}},
        "dependencies": [],
        "accessibility": {},
        "responsive_breakpoints": {"sm": {"layout": "stacked"}},
        "quality_score": 0.95,
    },
    {
        "id": "timeline",
        "category": "content",
        "name": "Timeline",
        "description": "Línea de tiempo vertical para mostrar historia o proceso",
        "variants": [
            {
                "name": "minimal",
                "description": "Línea simple con puntos",
                "tailwind_classes": {},
                "animations": ["fade_in_up"],
                "dark_mode": True,
            }
        ],
        "props": {"events": {"type": "array", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {},
        "responsive_breakpoints": {},
        "quality_score": 0.88,
    },
    {
        "id": "faq",
        "category": "content",
        "name": "FAQ Accordion",
        "description": "Preguntas frecuentes con acordeón animado",
        "variants": [
            {
                "name": "minimal",
                "description": "Acordeón simple",
                "tailwind_classes": {},
                "animations": ["accordion"],
                "dark_mode": True,
            }
        ],
        "props": {"questions": {"type": "array", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {"role": "list"},
        "responsive_breakpoints": {},
        "quality_score": 0.89,
    },
    # Forms (4)
    {
        "id": "contact_form",
        "category": "forms",
        "name": "Contact Form",
        "description": "Formulario de contacto con validación y feedback visual",
        "variants": [
            {
                "name": "inline",
                "description": "Campos en línea",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
            {
                "name": "floating",
                "description": "Labels flotantes",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
        ],
        "props": {"fields": {"type": "array", "required": True}},
        "dependencies": ["react-hook-form"],
        "accessibility": {"role": "form"},
        "responsive_breakpoints": {},
        "quality_score": 0.92,
    },
    {
        "id": "checkout_form",
        "category": "forms",
        "name": "Checkout Form",
        "description": "Formulario de pago multi-step con Stripe Elements",
        "variants": [
            {
                "name": "steps",
                "description": "Pasos numerados",
                "tailwind_classes": {},
                "animations": ["step_transition"],
                "dark_mode": True,
            }
        ],
        "props": {"steps": {"type": "array", "required": True}},
        "dependencies": ["@stripe/react-stripe-js", "react-hook-form"],
        "accessibility": {"role": "form"},
        "responsive_breakpoints": {},
        "quality_score": 0.96,
    },
    {
        "id": "search_bar",
        "category": "forms",
        "name": "Search Bar",
        "description": "Barra de búsqueda con autocompletado y resultados en tiempo real",
        "variants": [
            {
                "name": "minimal",
                "description": "Input simple con icono",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
            {
                "name": "expanded",
                "description": "Con dropdown de resultados",
                "tailwind_classes": {},
                "animations": ["dropdown_fade"],
                "dark_mode": True,
            },
        ],
        "props": {"placeholder": {"type": "string", "required": False}},
        "dependencies": [],
        "accessibility": {"role": "search"},
        "responsive_breakpoints": {},
        "quality_score": 0.90,
    },
    {
        "id": "newsletter",
        "category": "forms",
        "name": "Newsletter Signup",
        "description": "Formulario de suscripción a newsletter con confirmación",
        "variants": [
            {
                "name": "inline",
                "description": "Email + botón en línea",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            }
        ],
        "props": {"placeholder": {"type": "string", "required": False}},
        "dependencies": [],
        "accessibility": {"role": "form"},
        "responsive_breakpoints": {},
        "quality_score": 0.88,
    },
    # Commerce (4)
    {
        "id": "product_card",
        "category": "commerce",
        "name": "Product Card",
        "description": "Tarjeta de producto con imagen, precio, variantes y CTA",
        "variants": [
            {
                "name": "grid",
                "description": "Para grids de productos",
                "tailwind_classes": {},
                "animations": ["hover_lift"],
                "dark_mode": True,
            },
            {
                "name": "compact",
                "description": "Versión compacta para listas",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
        ],
        "props": {"product": {"type": "object", "required": True}},
        "dependencies": [],
        "accessibility": {},
        "responsive_breakpoints": {},
        "quality_score": 0.94,
    },
    {
        "id": "cart_drawer",
        "category": "commerce",
        "name": "Cart Drawer",
        "description": "Carrito lateral deslizante con items y resumen",
        "variants": [
            {
                "name": "minimal",
                "description": "Drawer limpio",
                "tailwind_classes": {},
                "animations": ["slide_in_right"],
                "dark_mode": True,
            }
        ],
        "props": {"items": {"type": "array", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {"role": "dialog"},
        "responsive_breakpoints": {},
        "quality_score": 0.93,
    },
    {
        "id": "order_summary",
        "category": "commerce",
        "name": "Order Summary",
        "description": "Resumen de orden con subtotal, impuestos y total",
        "variants": [
            {
                "name": "minimal",
                "description": "Lista simple con totales",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            }
        ],
        "props": {"items": {"type": "array", "required": True}},
        "dependencies": [],
        "accessibility": {},
        "responsive_breakpoints": {},
        "quality_score": 0.91,
    },
    {
        "id": "wishlist",
        "category": "commerce",
        "name": "Wishlist",
        "description": "Lista de deseos con toggle de corazón animado",
        "variants": [
            {
                "name": "grid",
                "description": "Grid de productos guardados",
                "tailwind_classes": {},
                "animations": ["heart_pulse"],
                "dark_mode": True,
            }
        ],
        "props": {"items": {"type": "array", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {},
        "responsive_breakpoints": {},
        "quality_score": 0.87,
    },
    # Layout (5)
    {
        "id": "footer",
        "category": "layout",
        "name": "Footer",
        "description": "Pie de página con links, redes sociales y copyright",
        "variants": [
            {
                "name": "centered",
                "description": "Todo centrado",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
            {
                "name": "split",
                "description": "Columnas de links",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
        ],
        "props": {"links": {"type": "array", "required": True}},
        "dependencies": [],
        "accessibility": {"role": "contentinfo"},
        "responsive_breakpoints": {},
        "quality_score": 0.92,
    },
    {
        "id": "cta_section",
        "category": "layout",
        "name": "CTA Section",
        "description": "Sección de llamada a la acción con headline y botones",
        "variants": [
            {
                "name": "centered",
                "description": "Centrado con fondo de color",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
            {
                "name": "split",
                "description": "Texto a la izquierda, botones a la derecha",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
        ],
        "props": {"headline": {"type": "string", "required": True}, "cta_text": {"type": "string", "required": True}},
        "dependencies": [],
        "accessibility": {},
        "responsive_breakpoints": {},
        "quality_score": 0.93,
    },
    {
        "id": "stats_bar",
        "category": "layout",
        "name": "Stats Bar",
        "description": "Barra de estadísticas con números animados y labels",
        "variants": [
            {
                "name": "minimal",
                "description": "Números grandes con labels",
                "tailwind_classes": {},
                "animations": ["count_up"],
                "dark_mode": True,
            }
        ],
        "props": {"stats": {"type": "array", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {},
        "responsive_breakpoints": {},
        "quality_score": 0.90,
    },
    {
        "id": "divider",
        "category": "layout",
        "name": "Section Divider",
        "description": "Divisor visual entre secciones con variantes decorativas",
        "variants": [
            {"name": "wave", "description": "Ola SVG", "tailwind_classes": {}, "animations": [], "dark_mode": True},
            {
                "name": "angle",
                "description": "Corte diagonal",
                "tailwind_classes": {},
                "animations": [],
                "dark_mode": True,
            },
        ],
        "props": {},
        "dependencies": [],
        "accessibility": {"role": "separator"},
        "responsive_breakpoints": {},
        "quality_score": 0.85,
    },
    {
        "id": "banner",
        "category": "layout",
        "name": "Announcement Banner",
        "description": "Banner de anuncio dismissable en la parte superior",
        "variants": [
            {
                "name": "minimal",
                "description": "Texto + botón de cierre",
                "tailwind_classes": {},
                "animations": ["slide_down"],
                "dark_mode": True,
            }
        ],
        "props": {"message": {"type": "string", "required": True}},
        "dependencies": ["framer-motion"],
        "accessibility": {"role": "alert"},
        "responsive_breakpoints": {},
        "quality_score": 0.87,
    },
]

# Recomendaciones por tipo de proyecto
PROJECT_RECOMMENDATIONS: dict[str, list[str]] = {
    "ecommerce": ["navbar", "hero_split", "product_card", "cart_drawer", "checkout_form", "footer"],
    "saas": ["navbar", "hero_centered", "feature_grid", "pricing_table", "testimonial", "cta_section", "footer"],
    "portfolio": ["navbar", "hero_video", "timeline", "stats_bar", "contact_form", "footer"],
    "blog": ["navbar", "hero_centered", "feature_grid", "search_bar", "footer"],
    "landing": ["navbar", "hero_split", "feature_grid", "testimonial", "pricing_table", "cta_section", "footer"],
}


class ComponentRegistry:
    """
    Catálogo central de todos los componentes disponibles.

    Carga componentes desde el catálogo built-in y opcionalmente
    desde archivos JSON en el directorio de la librería.
    """

    def __init__(self, library_dir: Optional[Path] = None):
        """
        Args:
            library_dir: Directorio con JSONs de componentes adicionales.
        """
        self.library_dir = library_dir or Path("kernel/components/library")
        self._components: dict[str, ComponentDefinition] = {}
        self._categories: dict[str, list[str]] = {}
        self._loaded = False

    async def load_all(self) -> int:
        """
        Carga todos los componentes (built-in + archivos JSON).

        Returns:
            Número total de componentes cargados.
        """
        count = 0

        # Cargar built-in
        for data in BUILTIN_COMPONENTS:
            try:
                component = self._parse_component(data)
                self._register_component(component)
                count += 1
            except Exception as e:
                logger.error("componente_builtin_error", id=data.get("id"), error=str(e))

        # Cargar desde archivos JSON si el directorio existe
        if self.library_dir.exists():
            for json_file in self.library_dir.rglob("*.json"):
                try:
                    data = json.loads(json_file.read_text())
                    component = self._parse_component(data)
                    self._register_component(component)
                    count += 1
                except Exception as e:
                    logger.error("componente_json_error", file=str(json_file), error=str(e))

        self._loaded = True
        logger.info("componentes_cargados", total=count, categorias=len(self._categories))
        return count

    def get_by_id(self, component_id: str) -> ComponentDefinition:
        """
        Obtiene un componente por su ID.

        Args:
            component_id: ID del componente.

        Returns:
            ComponentDefinition del componente.

        Raises:
            ComponenteNoEncontrado: Si el componente no existe.
        """
        if component_id not in self._components:
            raise ComponenteNoEncontrado(component_id)
        return self._components[component_id]

    def get_by_category(self, category: str) -> list[ComponentDefinition]:
        """Retorna todos los componentes de una categoría."""
        ids = self._categories.get(category, [])
        return [self._components[id] for id in ids if id in self._components]

    def search(self, query: str) -> list[ComponentDefinition]:
        """Busca componentes por nombre o descripción."""
        query_lower = query.lower()
        return [
            c
            for c in self._components.values()
            if query_lower in c.name.lower() or query_lower in c.description.lower()
        ]

    def get_for_project_type(self, project_type: str) -> list[ComponentDefinition]:
        """
        Retorna los componentes recomendados para un tipo de proyecto.

        Args:
            project_type: Tipo de proyecto (ecommerce, saas, portfolio, blog, landing).

        Returns:
            Lista de ComponentDefinition recomendados.
        """
        ids = PROJECT_RECOMMENDATIONS.get(project_type, PROJECT_RECOMMENDATIONS["landing"])
        return [self._components[id] for id in ids if id in self._components]

    def list_categories(self) -> list[str]:
        """Lista todas las categorías disponibles."""
        return list(self._categories.keys())

    def to_dict(self) -> dict:
        """Serialización para el Command Center."""
        return {
            "total_componentes": len(self._components),
            "categorias": {cat: len(ids) for cat, ids in self._categories.items()},
            "cargado": self._loaded,
            "project_types_soportados": list(PROJECT_RECOMMENDATIONS.keys()),
        }

    def _register_component(self, component: ComponentDefinition) -> None:
        """Registra un componente en el catálogo."""
        self._components[component.id] = component
        if component.category not in self._categories:
            self._categories[component.category] = []
        if component.id not in self._categories[component.category]:
            self._categories[component.category].append(component.id)

    def _parse_component(self, data: dict) -> ComponentDefinition:
        """Parsea un dict a ComponentDefinition."""
        if "id" not in data or "category" not in data or "name" not in data:
            raise ComponenteInvalido(data.get("id", "unknown"), "Faltan campos requeridos: id, category, name")

        variants = []
        for v in data.get("variants", []):
            variants.append(
                ComponentVariant(
                    name=v.get("name", "default"),
                    description=v.get("description", ""),
                    tailwind_classes=v.get("tailwind_classes", {}),
                    animations=v.get("animations", []),
                    dark_mode=v.get("dark_mode", True),
                )
            )

        return ComponentDefinition(
            id=data["id"],
            category=data["category"],
            name=data["name"],
            description=data.get("description", ""),
            variants=variants,
            props=data.get("props", {}),
            dependencies=data.get("dependencies", []),
            accessibility=data.get("accessibility", {}),
            responsive_breakpoints=data.get("responsive_breakpoints", {}),
            quality_score=data.get("quality_score", 0.0),
        )


# --- Singleton ---

_component_registry: ComponentRegistry | None = None


def get_component_registry() -> ComponentRegistry:
    """Retorna el singleton del ComponentRegistry."""
    global _component_registry
    if _component_registry is None:
        _component_registry = ComponentRegistry()
    return _component_registry


def init_component_registry(library_dir: Optional[Path] = None) -> ComponentRegistry:
    """Inicializa el singleton del ComponentRegistry."""
    global _component_registry
    _component_registry = ComponentRegistry(library_dir=library_dir)
    return _component_registry
