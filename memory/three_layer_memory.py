"""
Memoria de 3 Capas (Three-Layer Memory)
=======================================
Implementación basada en la arquitectura de Claude Code (Anthropic).
Resuelve el problema de degradación de contexto en tareas largas.

Capas:
1. Working Memory (Contexto Activo): Lo que el LLM ve en el prompt actual.
2. Project Memory (memory.md): Archivo markdown en la raíz del proyecto que el agente lee/escribe.
3. Archive Memory (Grep/Search): Búsqueda semántica o por regex en el historial completo.
"""

from __future__ import annotations

from pathlib import Path

import structlog

logger = structlog.get_logger()


class ThreeLayerMemory:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.memory_file = self.project_root / "memory.md"
        self.working_memory: list[dict] = []

    def init_project_memory(self) -> None:
        """Inicializa el archivo memory.md si no existe."""
        if not self.memory_file.exists():
            content = (
                "# Project Memory\n\n## Contexto General\n\n## Decisiones Arquitectónicas\n\n## Tareas Pendientes\n"
            )
            self.memory_file.write_text(content, encoding="utf-8")
            logger.info("project_memory_initialized", path=str(self.memory_file))

    def read_project_memory(self) -> str:
        """Lee el contenido actual de memory.md."""
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding="utf-8")
        return ""

    def update_project_memory(self, new_content: str) -> None:
        """Sobrescribe el archivo memory.md con nuevo contenido."""
        self.memory_file.write_text(new_content, encoding="utf-8")
        logger.info("project_memory_updated", path=str(self.memory_file))

    def add_to_working_memory(self, role: str, content: str) -> None:
        """Añade un mensaje al contexto activo."""
        self.working_memory.append({"role": role, "content": content})

    def get_working_memory(self, max_tokens: int = 8000) -> list[dict]:
        """Retorna el contexto activo, truncando si es necesario."""
        # Implementación simplificada: retorna los últimos N mensajes
        return self.working_memory[-20:]

    def archive_search(self, query: str) -> list[str]:
        """Busca en el historial completo (simulado con grep en el proyecto)."""
        import subprocess

        try:
            result = subprocess.run(
                ["grep", "-rn", query, str(self.project_root)], capture_output=True, text=True, timeout=5
            )
            return result.stdout.splitlines()[:10]  # Top 10 resultados
        except Exception as e:
            logger.error("archive_search_failed", error=str(e))
            return []
