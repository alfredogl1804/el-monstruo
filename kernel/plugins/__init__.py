"""kernel/plugins — Plugin Architecture (Sprint 62.1)"""
from kernel.plugins.plugin_spec import MonstruoPluginSpec, hookspec, hookimpl, PLUGGY_DISPONIBLE
from kernel.plugins.plugin_manager import (
    PluginManager,
    PluginMetadata,
    PluginNoEncontrado,
    PluginSeguridad,
    PluginYaRegistrado,
    get_plugin_manager,
    init_plugin_manager,
)

__all__ = [
    "MonstruoPluginSpec", "hookspec", "hookimpl", "PLUGGY_DISPONIBLE",
    "PluginManager", "PluginMetadata",
    "PluginNoEncontrado", "PluginSeguridad", "PluginYaRegistrado",
    "get_plugin_manager", "init_plugin_manager",
]
