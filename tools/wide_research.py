"""
WideResearchTool — Sprint 51
==============================
Implementación basada en la arquitectura de Kimi K2.6 (Moonshot AI).
Resuelve la brecha crítica #2 del Backlog Técnico: el Monstruo no tiene
sub-agentes paralelos autónomos para investigación profunda.

Arquitectura (Kimi K2.6 Swarm):
- Un agente Orquestador descompone la tarea en N sub-tareas independientes
- N sub-agentes Investigadores ejecutan en paralelo (hasta 10 simultáneos)
- El Orquestador agrega y sintetiza los resultados
- Cada sub-agente tiene su propio contexto y herramientas

Diferencia con el multi_agent.py existente:
- multi_agent.py: despacha tareas a agentes especializados (1 a la vez)
- WideResearchTool: lanza N investigaciones paralelas sobre el MISMO tema
"""
from __future__ import annotations
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Optional
import structlog

logger = structlog.get_logger()


@dataclass
class ResearchSubTask:
    """Una sub-tarea de investigación individual."""
    task_id: str
    query: str
    focus: str  # Aspecto específico a investigar
    result: Optional[str] = None
    error: Optional[str] = None
    completed: bool = False


@dataclass
class WideResearchResult:
    """Resultado agregado de una investigación amplia."""
    main_query: str
    sub_tasks: list[ResearchSubTask] = field(default_factory=list)
    synthesis: str = ""
    sources_count: int = 0
    success_rate: float = 0.0


class WideResearchTool:
    """
    Herramienta de investigación amplia con sub-agentes paralelos.
    
    Basada en la arquitectura de Kimi K2.6 que lanza hasta 300 sub-agentes
    en swarm para investigación profunda. Esta implementación usa hasta 10
    sub-agentes paralelos con asyncio.
    """
    
    MAX_PARALLEL_AGENTS = 10
    
    def __init__(self, web_search_fn=None, llm_fn=None):
        """
        Args:
            web_search_fn: Función de búsqueda web (ej. tools.web_search.search)
            llm_fn: Función del LLM para síntesis (ej. kernel.engine.generate)
        """
        self.web_search_fn = web_search_fn
        self.llm_fn = llm_fn
    
    def decompose_query(self, main_query: str, num_agents: int = 5) -> list[ResearchSubTask]:
        """
        Descompone una query principal en N sub-tareas independientes.
        
        Estrategia de descomposición (basada en Kimi K2.6):
        1. Aspecto técnico / arquitectura
        2. Benchmarks y métricas de rendimiento
        3. Casos de uso y ejemplos reales
        4. Comparación con competidores
        5. Tendencias y roadmap futuro
        """
        focuses = [
            f"arquitectura técnica e implementación interna de: {main_query}",
            f"benchmarks, métricas de rendimiento y evaluaciones de: {main_query}",
            f"casos de uso reales, ejemplos y testimonios de: {main_query}",
            f"comparación con alternativas y competidores de: {main_query}",
            f"tendencias recientes, actualizaciones y roadmap de: {main_query}",
            f"limitaciones, problemas conocidos y críticas de: {main_query}",
            f"integraciones, APIs y ecosistema de: {main_query}",
            f"pricing, modelo de negocio y accesibilidad de: {main_query}",
            f"comunidad, documentación y soporte de: {main_query}",
            f"seguridad, privacidad y compliance de: {main_query}",
        ]
        
        sub_tasks = []
        for i, focus in enumerate(focuses[:num_agents]):
            sub_tasks.append(ResearchSubTask(
                task_id=f"subtask_{i+1}",
                query=main_query,
                focus=focus,
            ))
        
        return sub_tasks
    
    async def _execute_sub_task(self, sub_task: ResearchSubTask) -> ResearchSubTask:
        """Ejecuta una sub-tarea de investigación individual."""
        try:
            if self.web_search_fn:
                result = await asyncio.to_thread(
                    self.web_search_fn, 
                    sub_task.focus
                )
                sub_task.result = str(result)
            else:
                # Modo simulado para testing
                sub_task.result = f"[Resultado simulado para: {sub_task.focus}]"
            
            sub_task.completed = True
            logger.info("sub_task_completed", task_id=sub_task.task_id)
            
        except Exception as e:
            sub_task.error = str(e)
            sub_task.completed = False
            logger.error("sub_task_failed", task_id=sub_task.task_id, error=str(e))
        
        return sub_task
    
    async def research_async(
        self, 
        main_query: str, 
        num_agents: int = 5,
        synthesize: bool = True
    ) -> WideResearchResult:
        """
        Ejecuta investigación amplia con N sub-agentes en paralelo.
        
        Args:
            main_query: La pregunta principal a investigar
            num_agents: Número de sub-agentes paralelos (máx 10)
            synthesize: Si True, sintetiza los resultados al final
        """
        num_agents = min(num_agents, self.MAX_PARALLEL_AGENTS)
        
        logger.info("wide_research_started", query=main_query, agents=num_agents)
        
        # Descomponer la query en sub-tareas
        sub_tasks = self.decompose_query(main_query, num_agents)
        
        # Ejecutar todas las sub-tareas en paralelo
        completed_tasks = await asyncio.gather(
            *[self._execute_sub_task(task) for task in sub_tasks],
            return_exceptions=False
        )
        
        # Calcular métricas
        successful = [t for t in completed_tasks if t.completed]
        success_rate = len(successful) / len(completed_tasks) if completed_tasks else 0
        
        result = WideResearchResult(
            main_query=main_query,
            sub_tasks=list(completed_tasks),
            sources_count=len(successful),
            success_rate=success_rate,
        )
        
        # Síntesis con LLM si está disponible
        if synthesize and self.llm_fn and successful:
            context = "\n\n".join([
                f"### {t.focus}\n{t.result}" 
                for t in successful
            ])
            synthesis_prompt = (
                f"Sintetiza los siguientes hallazgos de investigación sobre '{main_query}' "
                f"en un análisis coherente y estructurado:\n\n{context}"
            )
            try:
                result.synthesis = await asyncio.to_thread(self.llm_fn, synthesis_prompt)
            except Exception as e:
                logger.error("synthesis_failed", error=str(e))
                result.synthesis = context  # Fallback: concatenar sin síntesis
        
        logger.info(
            "wide_research_completed",
            query=main_query,
            agents=num_agents,
            success_rate=success_rate,
        )
        
        return result
    
    def research(self, main_query: str, num_agents: int = 5) -> WideResearchResult:
        """Versión síncrona de research_async para compatibilidad."""
        return asyncio.run(self.research_async(main_query, num_agents))


# Instancia global para uso desde el task_planner
_wide_research_tool: Optional[WideResearchTool] = None


def get_wide_research_tool(web_search_fn=None, llm_fn=None) -> WideResearchTool:
    """Retorna la instancia global del WideResearchTool."""
    global _wide_research_tool
    if _wide_research_tool is None:
        _wide_research_tool = WideResearchTool(
            web_search_fn=web_search_fn,
            llm_fn=llm_fn,
        )
    return _wide_research_tool
