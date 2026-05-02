"""
kernel/plugins/plugin_spec.py
Sprint 62.1 — Plugin Architecture (Objetivo #12: Ecosistema/Soberanía)

Especificación de todos los hooks disponibles para plugins de terceros.
Patrón Microkernel con hooks estilo Pluggy.

Soberanía: Si pluggy no está disponible, el sistema opera sin plugins externos.
Alternativa: Implementar un sistema de hooks manual con dict[str, list[Callable]].
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger("plugins.spec")

# --- Importación con soberanía ---
try:
    import pluggy

    hookspec = pluggy.HookspecMarker("monstruo")
    hookimpl = pluggy.HookimplMarker("monstruo")
    PLUGGY_DISPONIBLE = True
except ImportError:
    logger.warning("pluggy_no_disponible", alternativa="hooks_manual")
    PLUGGY_DISPONIBLE = False

    def hookspec(func=None, **kwargs):  # type: ignore[misc]
        """Stub cuando pluggy no está disponible."""
        if func is not None:
            return func

        def decorator(f):
            return f

        return decorator

    def hookimpl(func=None, **kwargs):  # type: ignore[misc]
        """Stub cuando pluggy no está disponible."""
        if func is not None:
            return func

        def decorator(f):
            return f

        return decorator


class MonstruoPluginSpec:
    """
    Especificación de todos los hooks disponibles para plugins de El Monstruo.

    Cada método define un punto de extensión donde los plugins pueden
    inyectar comportamiento personalizado sin modificar el core.
    """

    @hookspec
    def on_project_created(self, project_id: str, config: dict) -> None:
        """
        Llamado cuando se crea un nuevo proyecto.

        Args:
            project_id: UUID del proyecto recién creado.
            config: Configuración inicial del proyecto.
        """

    @hookspec
    def on_task_completed(self, task_id: str, result: dict) -> dict:
        """
        Llamado cuando un Embrión completa una tarea. Puede modificar el resultado.

        Args:
            task_id: UUID de la tarea completada.
            result: Resultado original de la tarea.

        Returns:
            Resultado modificado o el original sin cambios.
        """

    @hookspec
    def on_model_selected(self, intent: str, model_name: str) -> str | None:
        """
        Llamado antes del routing de modelos. Permite redirigir a un modelo alternativo.

        Args:
            intent: Intención de la tarea (execute, research, creative, etc.).
            model_name: Modelo seleccionado por el router nativo.

        Returns:
            Nombre del modelo alternativo, o None para aceptar el seleccionado.
        """

    @hookspec
    def on_content_generated(self, content: str, content_type: str) -> str:
        """
        Llamado después de generar contenido. Puede transformar el contenido.

        Args:
            content: Contenido generado.
            content_type: Tipo de contenido (code, copy, design, etc.).

        Returns:
            Contenido transformado o el original.
        """

    @hookspec
    def on_error(self, error: Exception, context: dict) -> dict | None:
        """
        Llamado cuando ocurre un error. Puede proveer una acción de recuperación.

        Args:
            error: La excepción capturada.
            context: Contexto del error (módulo, operación, etc.).

        Returns:
            Acción de recuperación como dict, o None para propagar el error.
        """

    @hookspec
    def on_deploy(self, project_id: str, artifacts: dict) -> dict:
        """
        Llamado antes del deployment. Puede agregar o modificar artefactos.

        Args:
            project_id: UUID del proyecto a deployar.
            artifacts: Artefactos de deployment (archivos, configs, etc.).

        Returns:
            Artefactos modificados.
        """

    @hookspec
    def get_tools(self) -> list[dict]:
        """
        Retorna herramientas adicionales que este plugin provee.

        Returns:
            Lista de definiciones de herramientas en formato ToolSpec.
        """

    @hookspec
    def get_templates(self) -> list[dict]:
        """
        Retorna templates de proyectos que este plugin provee.

        Returns:
            Lista de templates de proyectos.
        """
