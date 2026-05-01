"""
kernel/plugins/plugin_manager.py
Sprint 62.1 — Plugin Architecture (Objetivo #12: Ecosistema/Soberanía)

Registry central y lifecycle manager para plugins de El Monstruo.
Patrón Microkernel — el core no sabe nada de los plugins, solo de los hooks.

Soberanía: Si pluggy no está disponible, opera en modo stub sin plugins externos.
Alternativa: Sistema de hooks manual con dict[str, list[Callable]].
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any

import structlog

from kernel.plugins.plugin_spec import MonstruoPluginSpec, PLUGGY_DISPONIBLE

logger = structlog.get_logger("plugins.manager")


# --- Excepciones con identidad ---

class PluginNoEncontrado(Exception):
    """Plugin no registrado en el PluginManager."""
    def __init__(self, nombre: str):
        super().__init__(
            f"Plugin '{nombre}' no encontrado. "
            f"Verifica que esté instalado con POST /api/plugins."
        )
        self.nombre = nombre


class PluginSeguridad(Exception):
    """Plugin rechazado por el security check."""
    def __init__(self, nombre: str, razon: str):
        super().__init__(
            f"Plugin '{nombre}' rechazado por seguridad: {razon}. "
            f"Los plugins no pueden usar os.system, subprocess, eval o exec."
        )
        self.nombre = nombre
        self.razon = razon


class PluginYaRegistrado(Exception):
    """Plugin con ese nombre ya existe en el registry."""
    def __init__(self, nombre: str):
        super().__init__(
            f"Plugin '{nombre}' ya está registrado. "
            f"Usa PATCH /api/plugins/{nombre} para actualizarlo."
        )
        self.nombre = nombre


# --- Dataclasses ---

@dataclass
class PluginMetadata:
    """Metadatos de un plugin registrado."""
    name: str
    version: str
    author: str
    description: str
    hooks: list[str]
    enabled: bool = True
    config: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "hooks": self.hooks,
            "enabled": self.enabled,
        }


# --- Plugin Manager ---

class PluginManager:
    """
    Registry central y lifecycle manager para plugins de El Monstruo.

    Gestiona registro, validación de seguridad, habilitación/deshabilitación
    y dispatch de hooks a todos los plugins registrados.
    """

    def __init__(self):
        self._registry: dict[str, PluginMetadata] = {}
        self._plugins: dict[str, Any] = {}
        self._load_order: list[str] = []

        if PLUGGY_DISPONIBLE:
            import pluggy
            self._pm = pluggy.PluginManager("monstruo")
            self._pm.add_hookspecs(MonstruoPluginSpec)
        else:
            self._pm = None

        logger.info("plugin_manager_iniciado", pluggy=PLUGGY_DISPONIBLE)

    async def register(self, plugin: Any, metadata: PluginMetadata) -> bool:
        """
        Registra y valida un plugin.

        Args:
            plugin: Instancia del plugin a registrar.
            metadata: Metadatos del plugin.

        Returns:
            True si el registro fue exitoso, False si falló.

        Raises:
            PluginYaRegistrado: Si ya existe un plugin con ese nombre.
            PluginSeguridad: Si el plugin no pasa el security check.
        """
        if metadata.name in self._registry:
            raise PluginYaRegistrado(metadata.name)

        seguro, razon = await self._security_check(plugin)
        if not seguro:
            raise PluginSeguridad(metadata.name, razon)

        if self._pm is not None:
            self._pm.register(plugin, name=metadata.name)

        self._registry[metadata.name] = metadata
        self._plugins[metadata.name] = plugin
        self._load_order.append(metadata.name)

        logger.info(
            "plugin_registrado",
            name=metadata.name,
            version=metadata.version,
            hooks=metadata.hooks,
        )
        return True

    async def unregister(self, nombre: str) -> bool:
        """
        Desregistra un plugin por nombre.

        Args:
            nombre: Nombre del plugin a desregistrar.

        Returns:
            True si fue desregistrado, False si no existía.
        """
        if nombre not in self._registry:
            return False

        if self._pm is not None:
            self._pm.unregister(name=nombre)

        del self._registry[nombre]
        del self._plugins[nombre]
        self._load_order.remove(nombre)

        logger.info("plugin_desregistrado", name=nombre)
        return True

    def call_hook(self, hook_name: str, **kwargs) -> list[Any]:
        """
        Llama un hook y recolecta resultados de todos los plugins.

        Args:
            hook_name: Nombre del hook a llamar.
            **kwargs: Argumentos del hook.

        Returns:
            Lista de resultados de todos los plugins que implementan el hook.
        """
        if self._pm is None:
            return []

        hook = getattr(self._pm.hook, hook_name, None)
        if hook is None:
            logger.warning("hook_no_encontrado", hook=hook_name)
            return []

        try:
            return hook(**kwargs)
        except Exception as e:
            logger.error("hook_error", hook=hook_name, error=str(e))
            return []

    def enable(self, nombre: str) -> bool:
        """Habilita un plugin deshabilitado."""
        if nombre not in self._registry:
            raise PluginNoEncontrado(nombre)
        self._registry[nombre].enabled = True
        logger.info("plugin_habilitado", name=nombre)
        return True

    def disable(self, nombre: str) -> bool:
        """Deshabilita un plugin sin desregistrarlo."""
        if nombre not in self._registry:
            raise PluginNoEncontrado(nombre)
        self._registry[nombre].enabled = False
        logger.info("plugin_deshabilitado", name=nombre)
        return True

    def list_plugins(self) -> list[PluginMetadata]:
        """Lista todos los plugins registrados."""
        return list(self._registry.values())

    def get_plugin(self, nombre: str) -> PluginMetadata:
        """Obtiene metadatos de un plugin específico."""
        if nombre not in self._registry:
            raise PluginNoEncontrado(nombre)
        return self._registry[nombre]

    def to_dict(self) -> dict:
        """Serialización para el Command Center."""
        return {
            "total_plugins": len(self._registry),
            "habilitados": sum(1 for p in self._registry.values() if p.enabled),
            "deshabilitados": sum(1 for p in self._registry.values() if not p.enabled),
            "plugins": [p.to_dict() for p in self._registry.values()],
            "pluggy_disponible": PLUGGY_DISPONIBLE,
        }

    async def _security_check(self, plugin: Any) -> tuple[bool, str]:
        """
        Valida que el plugin no use módulos peligrosos.

        Args:
            plugin: Instancia del plugin a validar.

        Returns:
            Tupla (es_seguro, razon).
        """
        try:
            source = inspect.getsource(type(plugin))
            forbidden = ["os.system", "subprocess", "eval(", "exec(", "__import__"]
            for f in forbidden:
                if f in source:
                    return False, f"Contiene '{f}'"
            return True, "OK"
        except Exception:
            # Si no podemos inspeccionar el código, lo aceptamos con advertencia
            logger.warning("plugin_security_check_skip", plugin=type(plugin).__name__)
            return True, "skip"


# --- Singleton ---

_plugin_manager: PluginManager | None = None


def get_plugin_manager() -> PluginManager:
    """Retorna el singleton del PluginManager."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def init_plugin_manager() -> PluginManager:
    """Inicializa el singleton del PluginManager."""
    global _plugin_manager
    _plugin_manager = PluginManager()
    return _plugin_manager
