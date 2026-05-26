"""kernel/components — Component Library (Sprint 62.3)"""

from kernel.components.registry import (
    BUILTIN_COMPONENTS,
    PROJECT_RECOMMENDATIONS,
    ComponentDefinition,
    ComponenteInvalido,
    ComponenteNoEncontrado,
    ComponentRegistry,
    ComponentVariant,
    get_component_registry,
    init_component_registry,
)

__all__ = [
    "ComponentRegistry",
    "ComponentDefinition",
    "ComponentVariant",
    "ComponenteNoEncontrado",
    "ComponenteInvalido",
    "get_component_registry",
    "init_component_registry",
    "BUILTIN_COMPONENTS",
    "PROJECT_RECOMMENDATIONS",
]
