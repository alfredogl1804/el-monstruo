"""kernel/components — Component Library (Sprint 62.3)"""
from kernel.components.registry import (
    ComponentRegistry,
    ComponentDefinition,
    ComponentVariant,
    ComponenteNoEncontrado,
    ComponenteInvalido,
    get_component_registry,
    init_component_registry,
    BUILTIN_COMPONENTS,
    PROJECT_RECOMMENDATIONS,
)

__all__ = [
    "ComponentRegistry", "ComponentDefinition", "ComponentVariant",
    "ComponenteNoEncontrado", "ComponenteInvalido",
    "get_component_registry", "init_component_registry",
    "BUILTIN_COMPONENTS", "PROJECT_RECOMMENDATIONS",
]
