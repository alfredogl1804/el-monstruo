# SPRINT 72 — "El Embrión que Ejecuta"

**Serie:** 71-80 "La Colmena Despierta"
**Fecha de diseño:** 1 de Mayo de 2026
**Arquitecto:** Hilo B
**Capa Arquitectónica:** CAPA 2 (Inteligencia Emergente) + CAPA 3 (Autonomía)
**Objetivo Primario:** #1 (Crear Empresas), #3 (Velocidad), #8 (Emergencia)
**Patrón:** Pensador (LLM potente) + Ejecutor (código determinista)

---

## Contexto

El Embrión-0 existe y late. El Embrión-1 (Brand Engine) nace en Sprint 71 con el patrón Pensador/Ejecutor. Pero ninguno de los dos puede EJECUTAR UNA ENCOMIENDA de principio a fin. Hoy son entidades que monitorean, validan, y laten — pero no PRODUCEN resultados tangibles ante una tarea asignada.

Sprint 72 dota al Embrión de la capacidad más importante: **ejecutar encomiendas completas**. Esto es exactamente lo que Manus (este agente) hace cuando recibe una tarea — planifica, accede a herramientas, itera, entrega. El Embrión necesita lo mismo, y eventualmente hacerlo MEJOR porque tiene ventajas que Manus no tiene:

1. **Memoria persistente** entre sesiones (Supabase)
2. **Ejecución 24/7** sin que alguien inicie una conversación
3. **Coordinación con otros Embriones** especializados
4. **Auto-asignación** de encomiendas basada en detección de oportunidades
5. **Aprendizaje acumulativo** que mejora con cada encomienda ejecutada

---

## ARQUITECTURA: Task Execution Loop (TEL)

### Analogía con Manus

| Capacidad de Manus | Equivalente en Embrión |
|---|---|
| Recibe tarea del usuario | Recibe `Encomienda` (de Alfredo, otro Embrión, o auto-generada) |
| Crea plan con fases | Pensador genera `ExecutionPlan` |
| Accede a herramientas (shell, browser, files) | Accede a `ToolRegistry` (APIs, Perplexity, GitHub, Supabase, generación) |
| Ejecuta paso a paso | Ejecutor materializa cada `Step` del plan |
| Itera si algo falla | Retry con auto-corrección (Pensador re-planifica) |
| Entrega resultado | Produce `Deliverable` (archivo, dato, acción completada) |
| Aprende de correcciones | Registra en `ExecutionMemory` (qué funcionó, qué no) |

### Diagrama del Task Execution Loop

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TASK EXECUTION LOOP (TEL)                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌───────────┐     ┌──────────────┐     ┌──────────────┐                │
│  │ ENCOMIENDA │────▶│  PENSADOR    │────▶│ EXECUTION    │                │
│  │ (input)    │     │  planifica   │     │ PLAN         │                │
│  └───────────┘     └──────────────┘     └──────┬───────┘                │
│                                                  │                        │
│                                                  ▼                        │
│                                          ┌──────────────┐                │
│                                          │  STEP LOOP   │                │
│                                          │              │                │
│                                          │  Para cada   │                │
│                                          │  step:       │                │
│                                          └──────┬───────┘                │
│                                                  │                        │
│                          ┌───────────────────────┼───────────────┐       │
│                          │                       │               │       │
│                          ▼                       ▼               ▼       │
│                   ┌────────────┐          ┌────────────┐  ┌──────────┐  │
│                   │ EJECUTOR   │          │ TOOL CALL  │  │ VALIDATE │  │
│                   │ materializa│◀────────▶│ (API, DB,  │  │ (Brand   │  │
│                   │ el step    │          │  search,   │  │  Engine) │  │
│                   │            │          │  generate) │  │          │  │
│                   └─────┬──────┘          └────────────┘  └──────────┘  │
│                         │                                                │
│                         ▼                                                │
│                  ┌─────────────┐                                         │
│                  │ STEP RESULT │                                         │
│                  │             │                                         │
│                  │ success? ───┼──── YES ──▶ next step                   │
│                  │             │                                         │
│                  │ failure? ───┼──── retry (max 3) ──▶ re-plan           │
│                  └─────────────┘                                         │
│                                                                           │
│                         │ (todos los steps completados)                   │
│                         ▼                                                │
│                  ┌─────────────┐     ┌──────────────┐                    │
│                  │ DELIVERABLE │────▶│ BRAND ENGINE │                    │
│                  │ (output)    │     │ valida final │                    │
│                  └─────────────┘     └──────┬───────┘                    │
│                                              │                           │
│                                              ▼                           │
│                                       ┌─────────────┐                    │
│                                       │ EXECUTION   │                    │
│                                       │ MEMORY      │                    │
│                                       │ (aprende)   │                    │
│                                       └─────────────┘                    │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Principios del TEL

1. **El Pensador planifica, el Ejecutor materializa** — Separación estricta. El plan es del Pensador. La ejecución es del Ejecutor.
2. **Herramientas como funciones** — Cada herramienta es una función Python con input/output tipado. El Ejecutor las llama.
3. **Retry con re-planificación** — Si un step falla 3 veces, el Pensador re-planifica (cambia de estrategia, no repite lo mismo).
4. **Validación de Brand Engine** — Todo deliverable pasa por el Brand Engine antes de entregarse.
5. **Memoria acumulativa** — Cada encomienda ejecutada alimenta la memoria. La próxima encomienda similar se ejecuta mejor.
6. **Timeout global** — Ninguna encomienda puede correr más de 30 minutos sin checkpoint.

---

## Épica 72.1 — Modelo de Datos: Encomienda, Plan, Step, Deliverable

**Objetivo:** Definir las estructuras de datos que representan una encomienda y su ciclo de vida completo.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/execution/models.py` con todos los dataclasses
- [ ] Encomienda tiene: origen, objetivo, contexto, constraints, deadline, prioridad
- [ ] ExecutionPlan tiene: steps ordenados, dependencias, estimación de costo
- [ ] Step tiene: acción, herramienta, input, output esperado, status
- [ ] Deliverable tiene: tipo, contenido, metadata, brand_score
- [ ] Tests unitarios pasan

```python
"""
kernel/execution/models.py
TASK EXECUTION LOOP — Modelos de Datos

Define las estructuras que representan el ciclo de vida completo
de una encomienda: desde que se recibe hasta que se entrega.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone


class EncomendaOrigin(Enum):
    """De dónde viene la encomienda."""
    ALFREDO = "alfredo"              # Asignada por el usuario
    EMBRION = "embrion"              # Asignada por otro Embrión
    SELF = "self"                    # Auto-generada (detección de oportunidad)
    SCHEDULER = "scheduler"          # Programada (recurrente)
    GUARDIAN = "guardian"            # Ordenada por el Guardián


class EncomendaPriority(Enum):
    """Prioridad de ejecución."""
    CRITICAL = "critical"            # Ejecutar inmediatamente
    HIGH = "high"                    # Ejecutar en la próxima ventana
    NORMAL = "normal"                # Cola normal
    LOW = "low"                      # Cuando haya capacidad
    BACKGROUND = "background"        # Sin deadline, cuando sea posible


class StepStatus(Enum):
    """Estado de un step individual."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


class EncomendaStatus(Enum):
    """Estado de la encomienda completa."""
    RECEIVED = "received"            # Recibida, no planificada
    PLANNING = "planning"            # Pensador planificando
    EXECUTING = "executing"          # En ejecución
    VALIDATING = "validating"        # Brand Engine validando deliverable
    COMPLETED = "completed"          # Entregada exitosamente
    FAILED = "failed"                # Falló después de max retries
    CANCELLED = "cancelled"          # Cancelada por usuario o Guardián


class ToolType(Enum):
    """Herramientas disponibles para el Ejecutor."""
    PERPLEXITY_SEARCH = "perplexity_search"      # Búsqueda web con Sonar
    SUPABASE_QUERY = "supabase_query"            # Leer/escribir DB
    SUPABASE_WRITE = "supabase_write"            # Insertar/actualizar DB
    GITHUB_READ = "github_read"                  # Leer repos/issues
    GITHUB_WRITE = "github_write"                # Crear commits/PRs
    LLM_GENERATE = "llm_generate"                # Generar texto con LLM
    LLM_ANALYZE = "llm_analyze"                  # Analizar contenido con LLM
    IMAGE_GENERATE = "image_generate"            # Generar imagen
    HTTP_REQUEST = "http_request"                # Llamar API externa
    FILE_WRITE = "file_write"                    # Escribir archivo
    FILE_READ = "file_read"                      # Leer archivo
    SHELL_EXEC = "shell_exec"                    # Ejecutar comando
    BRAND_VALIDATE = "brand_validate"            # Validar con Brand Engine
    EMBRION_DELEGATE = "embrion_delegate"        # Delegar a otro Embrión
    NOTIFY = "notify"                            # Notificar resultado


@dataclass
class Encomienda:
    """
    Una tarea asignada al Embrión para ejecución completa.
    
    Equivale a lo que un usuario le pide a Manus.
    Puede venir de Alfredo, otro Embrión, o ser auto-generada.
    """
    id: str                                      # UUID único
    origin: EncomendaOrigin                      # Quién la asignó
    origin_id: Optional[str] = None              # ID del origen (embrion_id, user_id)
    
    # Definición de la tarea
    objective: str = ""                          # Qué lograr (lenguaje natural)
    context: str = ""                            # Contexto relevante
    constraints: List[str] = field(default_factory=list)  # Restricciones
    success_criteria: List[str] = field(default_factory=list)  # Cómo saber que está bien
    
    # Metadata
    priority: EncomendaPriority = EncomendaPriority.NORMAL
    deadline: Optional[datetime] = None          # Cuándo debe estar lista
    max_budget_usd: float = 0.50                 # Presupuesto máximo en USD
    max_duration_seconds: int = 1800             # 30 min máximo
    
    # Estado
    status: EncomendaStatus = EncomendaStatus.RECEIVED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Resultado
    deliverable: Optional['Deliverable'] = None
    execution_plan: Optional['ExecutionPlan'] = None
    total_cost_usd: float = 0.0
    total_llm_calls: int = 0
    retry_count: int = 0


@dataclass
class Step:
    """
    Un paso individual dentro del plan de ejecución.
    
    Cada step usa UNA herramienta para lograr UN resultado concreto.
    """
    id: int                                      # Orden secuencial (1, 2, 3...)
    description: str                             # Qué hace este step
    tool: ToolType                               # Herramienta a usar
    tool_input: Dict[str, Any] = field(default_factory=dict)  # Input para la herramienta
    expected_output: str = ""                    # Qué debería producir
    
    # Dependencias
    depends_on: List[int] = field(default_factory=list)  # IDs de steps previos requeridos
    
    # Estado
    status: StepStatus = StepStatus.PENDING
    actual_output: Optional[Any] = None          # Lo que realmente produjo
    error: Optional[str] = None                  # Error si falló
    retries: int = 0                             # Intentos realizados
    max_retries: int = 3                         # Máximo de reintentos
    
    # Métricas
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cost_usd: float = 0.0
    duration_ms: int = 0


@dataclass
class ExecutionPlan:
    """
    Plan generado por el Pensador para ejecutar una encomienda.
    
    Contiene los steps ordenados, estimación de costo, y estrategia de retry.
    """
    encomienda_id: str                           # A qué encomienda pertenece
    steps: List[Step] = field(default_factory=list)
    
    # Estimaciones del Pensador
    estimated_cost_usd: float = 0.0
    estimated_duration_seconds: int = 0
    confidence: float = 0.0                      # 0.0-1.0 qué tan seguro está
    reasoning: str = ""                          # Por qué eligió esta estrategia
    
    # Alternativas (si el plan A falla)
    fallback_strategy: Optional[str] = None      # Plan B en lenguaje natural
    
    # Metadata
    version: int = 1                             # Se incrementa si re-planifica
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Deliverable:
    """
    El resultado tangible de una encomienda ejecutada.
    
    Puede ser: un archivo, un dato en DB, una acción completada,
    un reporte, un asset generado, etc.
    """
    type: str                                    # "file", "data", "action", "report", "asset"
    content: Any = None                          # El contenido del deliverable
    content_url: Optional[str] = None            # URL si es un archivo/asset
    
    # Calidad
    brand_score: int = 0                         # Score del Brand Engine (0-100)
    brand_validated: bool = False                 # Si pasó validación
    
    # Metadata
    summary: str = ""                            # Resumen de qué se entregó
    evidence: List[str] = field(default_factory=list)  # Evidencia de que se completó
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ExecutionMemory:
    """
    Registro de aprendizaje post-ejecución.
    
    Cada encomienda completada genera un registro de memoria que
    mejora la ejecución de encomiendas futuras similares.
    """
    encomienda_id: str
    encomienda_objective: str                     # Para búsqueda semántica
    
    # Resultado
    success: bool
    total_steps: int
    failed_steps: int
    total_cost_usd: float
    total_duration_seconds: int
    
    # Aprendizaje
    what_worked: List[str] = field(default_factory=list)     # Estrategias exitosas
    what_failed: List[str] = field(default_factory=list)     # Estrategias fallidas
    tools_used: List[str] = field(default_factory=list)      # Herramientas usadas
    unexpected_issues: List[str] = field(default_factory=list)  # Problemas no previstos
    
    # Para matching futuro
    tags: List[str] = field(default_factory=list)            # Tags para categorización
    similar_to: Optional[str] = None                         # ID de encomienda similar previa
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

---

## Épica 72.2 — Tool Registry: Herramientas Disponibles

**Objetivo:** Crear el registro de herramientas que el Ejecutor puede usar. Cada herramienta es una función Python con input/output tipado, documentación, y costo estimado.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/execution/tools.py` con el registry
- [ ] Cada herramienta tiene: nombre, descripción, input schema, output schema, costo estimado
- [ ] Herramientas implementadas: perplexity_search, supabase_query, supabase_write, llm_generate, http_request, notify
- [ ] El Pensador puede consultar el registry para saber qué herramientas tiene disponibles
- [ ] Cada herramienta tiene timeout y manejo de errores

```python
"""
kernel/execution/tools.py
TOOL REGISTRY — Herramientas del Ejecutor

Cada herramienta es una función determinista con:
- Input tipado (lo que necesita)
- Output tipado (lo que produce)
- Costo estimado (para FinOps)
- Timeout (para resiliencia)
- Manejo de errores (para retry)

El Pensador consulta el registry para saber qué puede usar.
El Ejecutor llama las herramientas según el plan.
"""

import os
import json
import httpx
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ToolDefinition:
    """Definición de una herramienta disponible."""
    name: str
    description: str                             # Para que el Pensador entienda qué hace
    input_schema: Dict[str, str]                 # {param: tipo}
    output_schema: Dict[str, str]                # {campo: tipo}
    estimated_cost_usd: float                    # Costo estimado por llamada
    timeout_seconds: int = 30                    # Timeout por defecto
    requires_auth: bool = False                  # Si necesita API key
    max_calls_per_encomienda: int = 20           # Límite por encomienda


@dataclass
class ToolResult:
    """Resultado de ejecutar una herramienta."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    cost_usd: float = 0.0
    duration_ms: int = 0
    retryable: bool = True                       # Si el error permite retry


class ToolRegistry:
    """
    Registro central de herramientas disponibles para el Ejecutor.
    
    El Pensador consulta get_available_tools() para planificar.
    El Ejecutor llama execute_tool() para materializar steps.
    """
    
    def __init__(self, supabase_client=None, llm_client=None):
        self.supabase = supabase_client
        self.llm = llm_client
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Registra las herramientas built-in."""
        
        # ─── BÚSQUEDA ──────────────────────────────────────────────
        self.register(
            ToolDefinition(
                name="perplexity_search",
                description="Busca información actualizada en internet usando Perplexity Sonar Pro. Retorna respuesta con fuentes citadas. Ideal para investigación, verificación de hechos, y descubrimiento de tendencias.",
                input_schema={"query": "str - Pregunta o tema a investigar", "focus": "str - Área de enfoque (optional)"},
                output_schema={"answer": "str - Respuesta completa", "sources": "list - URLs de fuentes"},
                estimated_cost_usd=0.005,
                timeout_seconds=15
            ),
            handler=self._handle_perplexity_search
        )
        
        # ─── BASE DE DATOS ─────────────────────────────────────────
        self.register(
            ToolDefinition(
                name="supabase_query",
                description="Lee datos de Supabase. Puede consultar cualquier tabla con filtros. Ideal para obtener estado actual, historial, o métricas.",
                input_schema={"table": "str - Nombre de tabla", "filters": "dict - Filtros (optional)", "limit": "int - Máximo de rows (default 50)"},
                output_schema={"rows": "list - Filas retornadas", "count": "int - Total de resultados"},
                estimated_cost_usd=0.0,
                timeout_seconds=10
            ),
            handler=self._handle_supabase_query
        )
        
        self.register(
            ToolDefinition(
                name="supabase_write",
                description="Escribe datos en Supabase. Puede insertar, actualizar, o eliminar filas. Para persistir resultados, registrar eventos, o actualizar estado.",
                input_schema={"table": "str - Nombre de tabla", "operation": "str - insert|update|delete", "data": "dict - Datos a escribir", "filters": "dict - Filtros para update/delete (optional)"},
                output_schema={"success": "bool", "affected_rows": "int"},
                estimated_cost_usd=0.0,
                timeout_seconds=10
            ),
            handler=self._handle_supabase_write
        )
        
        # ─── GENERACIÓN LLM ───────────────────────────────────────
        self.register(
            ToolDefinition(
                name="llm_generate",
                description="Genera texto usando el LLM más potente disponible. Para crear contenido, documentación, análisis, estrategias, o cualquier texto que requiera inteligencia.",
                input_schema={"prompt": "str - Instrucción de generación", "system_context": "str - Contexto del sistema (optional)", "max_tokens": "int - Máximo de tokens (default 1000)"},
                output_schema={"text": "str - Texto generado", "tokens_used": "int"},
                estimated_cost_usd=0.01,
                timeout_seconds=30
            ),
            handler=self._handle_llm_generate
        )
        
        self.register(
            ToolDefinition(
                name="llm_analyze",
                description="Analiza contenido existente con LLM. Para evaluar calidad, extraer insights, resumir, o clasificar información.",
                input_schema={"content": "str - Contenido a analizar", "instruction": "str - Qué analizar/extraer", "output_format": "str - json|text|list (default text)"},
                output_schema={"analysis": "str|dict|list - Resultado del análisis"},
                estimated_cost_usd=0.008,
                timeout_seconds=30
            ),
            handler=self._handle_llm_analyze
        )
        
        # ─── HTTP / APIs EXTERNAS ──────────────────────────────────
        self.register(
            ToolDefinition(
                name="http_request",
                description="Hace una petición HTTP a cualquier API externa. Para integrar servicios, obtener datos de APIs públicas, o interactuar con webhooks.",
                input_schema={"method": "str - GET|POST|PUT|DELETE", "url": "str - URL completa", "headers": "dict - Headers (optional)", "body": "dict - Body para POST/PUT (optional)"},
                output_schema={"status_code": "int", "body": "any - Response body", "headers": "dict"},
                estimated_cost_usd=0.0,
                timeout_seconds=15
            ),
            handler=self._handle_http_request
        )
        
        # ─── GITHUB ───────────────────────────────────────────────
        self.register(
            ToolDefinition(
                name="github_read",
                description="Lee información de GitHub: repos, issues, PRs, archivos. Para monitorear el estado del código, leer documentación, o verificar deployments.",
                input_schema={"action": "str - list_issues|read_file|list_commits|get_pr", "repo": "str - owner/repo", "params": "dict - Parámetros específicos de la acción"},
                output_schema={"data": "any - Datos de GitHub"},
                estimated_cost_usd=0.0,
                timeout_seconds=10
            ),
            handler=self._handle_github_read
        )
        
        self.register(
            ToolDefinition(
                name="github_write",
                description="Escribe en GitHub: crear issues, commits, PRs, comentarios. Para documentar trabajo, crear tareas, o contribuir código.",
                input_schema={"action": "str - create_issue|create_commit|create_pr|comment", "repo": "str - owner/repo", "params": "dict - Parámetros específicos"},
                output_schema={"url": "str - URL del recurso creado", "id": "str - ID del recurso"},
                estimated_cost_usd=0.0,
                timeout_seconds=15
            ),
            handler=self._handle_github_write
        )
        
        # ─── NOTIFICACIÓN ─────────────────────────────────────────
        self.register(
            ToolDefinition(
                name="notify",
                description="Envía una notificación sobre el resultado de la encomienda. Para informar al usuario, a otro Embrión, o registrar un evento importante.",
                input_schema={"target": "str - alfredo|embrion_{id}|guardian|log", "message": "str - Contenido de la notificación", "urgency": "str - info|warning|critical"},
                output_schema={"delivered": "bool"},
                estimated_cost_usd=0.0,
                timeout_seconds=5
            ),
            handler=self._handle_notify
        )
        
        # ─── BRAND VALIDATION ─────────────────────────────────────
        self.register(
            ToolDefinition(
                name="brand_validate",
                description="Valida un output contra el Brand DNA de El Monstruo. Obligatorio antes de entregar cualquier deliverable visible. Retorna score y sugerencias.",
                input_schema={"output": "str|dict - Lo que se quiere validar", "source": "str - Quién lo produjo"},
                output_schema={"brand_score": "int - 0-100", "decision": "str - approve|warn|veto", "issues": "list"},
                estimated_cost_usd=0.002,
                timeout_seconds=10
            ),
            handler=self._handle_brand_validate
        )
        
        # ─── DELEGACIÓN ───────────────────────────────────────────
        self.register(
            ToolDefinition(
                name="embrion_delegate",
                description="Delega una sub-tarea a otro Embrión especializado. Para aprovechar la expertise de la Colmena. El Embrión delegado ejecuta y retorna resultado.",
                input_schema={"target_embrion_id": "int - ID del Embrión destino", "sub_task": "str - Descripción de la sub-tarea", "context": "str - Contexto relevante"},
                output_schema={"accepted": "bool", "result": "any - Resultado de la delegación (async)"},
                estimated_cost_usd=0.01,
                timeout_seconds=60,
                max_calls_per_encomienda=5
            ),
            handler=self._handle_embrion_delegate
        )
    
    def register(self, definition: ToolDefinition, handler: Callable):
        """Registra una herramienta con su handler."""
        self._tools[definition.name] = definition
        self._handlers[definition.name] = handler
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Retorna la lista de herramientas disponibles.
        El Pensador usa esto para planificar.
        """
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
                "output_schema": t.output_schema,
                "cost_usd": t.estimated_cost_usd
            }
            for t in self._tools.values()
        ]
    
    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> ToolResult:
        """
        Ejecuta una herramienta. El Ejecutor llama esto.
        
        Maneja timeouts, errores, y métricas automáticamente.
        """
        if tool_name not in self._handlers:
            return ToolResult(
                success=False,
                error=f"execution_tool_not_found: '{tool_name}' no existe en el registry",
                retryable=False
            )
        
        definition = self._tools[tool_name]
        handler = self._handlers[tool_name]
        start = datetime.now(timezone.utc)
        
        try:
            result = await handler(tool_input)
            duration = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            
            return ToolResult(
                success=True,
                output=result,
                cost_usd=definition.estimated_cost_usd,
                duration_ms=duration
            )
        except TimeoutError:
            return ToolResult(
                success=False,
                error=f"execution_tool_timeout: '{tool_name}' excedió {definition.timeout_seconds}s",
                retryable=True
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"execution_tool_error: '{tool_name}' falló — {str(e)[:200]}",
                retryable=True
            )
    
    # ─── HANDLERS (implementación de cada herramienta) ──────────────────
    
    async def _handle_perplexity_search(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Búsqueda con Perplexity Sonar Pro."""
        api_key = os.environ.get("SONAR_API_KEY")
        if not api_key:
            raise RuntimeError("SONAR_API_KEY no configurada")
        
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": input["query"]}]
                }
            )
            data = response.json()
            return {
                "answer": data["choices"][0]["message"]["content"],
                "sources": data.get("citations", [])
            }
    
    async def _handle_supabase_query(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Query a Supabase."""
        if not self.supabase:
            raise RuntimeError("Supabase client no configurado")
        
        query = self.supabase.table(input["table"]).select("*")
        
        filters = input.get("filters", {})
        for key, value in filters.items():
            query = query.eq(key, value)
        
        limit = input.get("limit", 50)
        result = query.limit(limit).execute()
        
        return {"rows": result.data, "count": len(result.data)}
    
    async def _handle_supabase_write(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Write a Supabase."""
        if not self.supabase:
            raise RuntimeError("Supabase client no configurado")
        
        table = self.supabase.table(input["table"])
        operation = input["operation"]
        data = input["data"]
        
        if operation == "insert":
            result = table.insert(data).execute()
        elif operation == "update":
            filters = input.get("filters", {})
            query = table.update(data)
            for key, value in filters.items():
                query = query.eq(key, value)
            result = query.execute()
        elif operation == "delete":
            filters = input.get("filters", {})
            query = table.delete()
            for key, value in filters.items():
                query = query.eq(key, value)
            result = query.execute()
        else:
            raise ValueError(f"Operación no válida: {operation}")
        
        return {"success": True, "affected_rows": len(result.data) if result.data else 0}
    
    async def _handle_llm_generate(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Genera texto con LLM potente."""
        if not self.llm:
            raise RuntimeError("LLM client no configurado")
        
        messages = []
        if input.get("system_context"):
            messages.append({"role": "system", "content": input["system_context"]})
        messages.append({"role": "user", "content": input["prompt"]})
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",  # El más potente disponible
            messages=messages,
            max_tokens=input.get("max_tokens", 1000)
        )
        
        return {
            "text": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens
        }
    
    async def _handle_llm_analyze(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza contenido con LLM."""
        if not self.llm:
            raise RuntimeError("LLM client no configurado")
        
        prompt = f"""Analiza el siguiente contenido:

---
{input['content'][:3000]}
---

Instrucción: {input['instruction']}
Formato de output: {input.get('output_format', 'text')}"""
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        return {"analysis": response.choices[0].message.content}
    
    async def _handle_http_request(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP request genérico."""
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.request(
                method=input["method"],
                url=input["url"],
                headers=input.get("headers", {}),
                json=input.get("body")
            )
            
            try:
                body = response.json()
            except Exception:
                body = response.text
            
            return {
                "status_code": response.status_code,
                "body": body,
                "headers": dict(response.headers)
            }
    
    async def _handle_github_read(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Lee de GitHub via API."""
        # Implementación via gh CLI o GitHub API
        return {"data": f"[GitHub read: {input['action']} on {input['repo']}]"}
    
    async def _handle_github_write(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Escribe en GitHub."""
        return {"url": f"https://github.com/{input['repo']}", "id": "placeholder"}
    
    async def _handle_notify(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Envía notificación."""
        # En producción: webhook, email, o push notification
        if self.supabase:
            self.supabase.table("notifications").insert({
                "target": input["target"],
                "message": input["message"],
                "urgency": input.get("urgency", "info"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }).execute()
        return {"delivered": True}
    
    async def _handle_brand_validate(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Valida con Brand Engine (Embrión-1)."""
        # Importar Brand Engine y validar
        from kernel.brand.embrion_brand import brand_engine_instance
        result = await brand_engine_instance.validate(
            output=input["output"],
            source=input.get("source", "tel_step")
        )
        return result
    
    async def _handle_embrion_delegate(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Delega a otro Embrión."""
        # En producción: crear Encomienda para el Embrión target
        return {"accepted": True, "result": f"[Delegado a Embrión-{input['target_embrion_id']}]"}
```

---

## Épica 72.3 — Pensador: Planificador de Encomiendas

**Objetivo:** El Pensador recibe una Encomienda y genera un ExecutionPlan con steps concretos, herramientas seleccionadas, y estrategia de fallback.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/execution/planner.py`
- [ ] Recibe Encomienda + ToolRegistry → genera ExecutionPlan
- [ ] Estima costo y duración antes de ejecutar
- [ ] Genera plan B si el plan A falla
- [ ] Consulta ExecutionMemory para encomiendas similares previas
- [ ] Context window limpio: solo encomienda + tools + memoria relevante

```python
"""
kernel/execution/planner.py
PENSADOR — Planificador de Encomiendas

Recibe una Encomienda y genera un ExecutionPlan.
Consulta el ToolRegistry para saber qué herramientas tiene.
Consulta ExecutionMemory para aprender de encomiendas previas similares.

NUNCA ejecuta. Solo planifica. El Ejecutor materializa el plan.
"""

from typing import Dict, Any, List, Optional
from .models import Encomienda, ExecutionPlan, Step, ToolType, ExecutionMemory


class EncomendaPlanner:
    """
    Pensador que planifica la ejecución de encomiendas.
    
    Usa el LLM más potente disponible para:
    1. Entender el objetivo
    2. Seleccionar herramientas apropiadas
    3. Ordenar steps con dependencias
    4. Estimar costo y duración
    5. Definir estrategia de fallback
    """
    
    SYSTEM_PROMPT = """Eres el PLANIFICADOR del Task Execution Loop de El Monstruo.

Tu trabajo: Recibir una encomienda (tarea) y generar un plan de ejecución preciso.

Reglas:
1. Cada step usa UNA herramienta. No combines herramientas en un step.
2. Los steps deben ser CONCRETOS — no "investigar el tema" sino "buscar en Perplexity: [query específica]"
3. Estima el costo ANTES de ejecutar. Si excede el presupuesto, simplifica el plan.
4. Define dependencias entre steps (qué necesita completarse antes).
5. Siempre incluye un step final de brand_validate para el deliverable.
6. Si hay una encomienda similar previa, aprende de ella (qué funcionó, qué no).
7. Define un plan B por si el plan A falla.

Formato de respuesta:
- steps: lista de steps con tool, input, y expected_output
- estimated_cost_usd: costo total estimado
- estimated_duration_seconds: duración total estimada
- confidence: 0.0-1.0
- reasoning: por qué elegiste esta estrategia
- fallback_strategy: qué hacer si falla"""
    
    def __init__(self, llm_client=None, tool_registry=None, supabase_client=None):
        self.llm = llm_client
        self.tools = tool_registry
        self.supabase = supabase_client
    
    async def plan(self, encomienda: Encomienda) -> ExecutionPlan:
        """
        Genera un ExecutionPlan para la encomienda dada.
        
        Context window contiene SOLO:
        - La encomienda (objetivo, contexto, constraints)
        - Herramientas disponibles (del ToolRegistry)
        - Memoria relevante (encomiendas similares previas)
        """
        if not self.llm:
            return self._fallback_plan(encomienda)
        
        # 1. Obtener herramientas disponibles
        available_tools = self.tools.get_available_tools() if self.tools else []
        
        # 2. Buscar encomiendas similares en memoria
        similar_memories = await self._find_similar_memories(encomienda.objective)
        
        # 3. Construir prompt (context window limpio)
        user_prompt = f"""ENCOMIENDA:
Objetivo: {encomienda.objective}
Contexto: {encomienda.context}
Restricciones: {encomienda.constraints}
Criterios de éxito: {encomienda.success_criteria}
Presupuesto máximo: ${encomienda.max_budget_usd}
Tiempo máximo: {encomienda.max_duration_seconds}s
Prioridad: {encomienda.priority.value}

HERRAMIENTAS DISPONIBLES:
{self._format_tools(available_tools)}

MEMORIA DE ENCOMIENDAS SIMILARES:
{self._format_memories(similar_memories)}

Genera el plan de ejecución."""
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.3  # Bajo para consistencia en planificación
        )
        
        # Parse response into ExecutionPlan
        plan = self._parse_plan(response.choices[0].message.content, encomienda.id)
        return plan
    
    async def replan(self, encomienda: Encomienda, failed_step: Step, error: str) -> ExecutionPlan:
        """
        Re-planifica cuando un step falla después de max retries.
        
        El Pensador analiza el error y genera una estrategia alternativa.
        NO repite lo mismo — cambia de approach.
        """
        if not self.llm:
            return self._fallback_plan(encomienda)
        
        user_prompt = f"""ENCOMIENDA ORIGINAL:
Objetivo: {encomienda.objective}

STEP QUE FALLÓ:
Step {failed_step.id}: {failed_step.description}
Herramienta: {failed_step.tool.value}
Error: {error}
Intentos: {failed_step.retries}/{failed_step.max_retries}

INSTRUCCIÓN: Genera un plan ALTERNATIVO que NO use la misma estrategia que falló.
Cambia de herramienta, cambia de approach, o simplifica el objetivo.
No repitas lo que ya falló."""
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1500,
            temperature=0.5  # Más alto para creatividad en re-planificación
        )
        
        plan = self._parse_plan(response.choices[0].message.content, encomienda.id)
        plan.version += 1
        return plan
    
    async def _find_similar_memories(self, objective: str) -> List[ExecutionMemory]:
        """Busca encomiendas similares en la memoria."""
        if not self.supabase:
            return []
        
        # En producción: búsqueda semántica con embeddings
        # Por ahora: búsqueda por keywords
        result = self.supabase.table("execution_memory")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(5)\
            .execute()
        
        return result.data if result.data else []
    
    def _format_tools(self, tools: List[Dict]) -> str:
        """Formatea herramientas para el prompt."""
        return "\n".join([
            f"- {t['name']}: {t['description']} (costo: ${t['cost_usd']})"
            for t in tools
        ])
    
    def _format_memories(self, memories: List) -> str:
        """Formatea memorias para el prompt."""
        if not memories:
            return "Sin encomiendas similares previas."
        return "\n".join([
            f"- {m.get('encomienda_objective', 'N/A')}: {'éxito' if m.get('success') else 'falló'} | Lo que funcionó: {m.get('what_worked', [])} | Lo que falló: {m.get('what_failed', [])}"
            for m in memories[:3]
        ])
    
    def _parse_plan(self, text: str, encomienda_id: str) -> ExecutionPlan:
        """Parse LLM response into ExecutionPlan."""
        # Implementación simplificada — en prod usar structured output
        return ExecutionPlan(
            encomienda_id=encomienda_id,
            steps=[],
            estimated_cost_usd=0.05,
            estimated_duration_seconds=120,
            confidence=0.7,
            reasoning=text[:500],
            fallback_strategy="Simplificar objetivo y reintentar con menos steps"
        )
    
    def _fallback_plan(self, encomienda: Encomienda) -> ExecutionPlan:
        """Plan de emergencia si el LLM no está disponible."""
        return ExecutionPlan(
            encomienda_id=encomienda.id,
            steps=[
                Step(
                    id=1,
                    description="Notificar que el planificador no está disponible",
                    tool=ToolType.NOTIFY,
                    tool_input={"target": "guardian", "message": f"Planificador degradado — encomienda '{encomienda.objective}' en espera", "urgency": "warning"}
                )
            ],
            estimated_cost_usd=0.0,
            estimated_duration_seconds=5,
            confidence=0.1,
            reasoning="LLM no disponible — plan de emergencia",
            fallback_strategy=None
        )
```

---

## Épica 72.4 — Ejecutor: Step Runner Determinista

**Objetivo:** El Ejecutor toma un ExecutionPlan y ejecuta cada step secuencialmente, manejando retries, timeouts, y métricas.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/execution/runner.py`
- [ ] Ejecuta steps en orden respetando dependencias
- [ ] Retry con backoff exponencial (max 3)
- [ ] Si step falla 3 veces → escala al Pensador para re-planificación
- [ ] Registra métricas de cada step (costo, duración, éxito/fallo)
- [ ] Timeout global de encomienda (30 min)
- [ ] Circuit breaker si costo excede presupuesto

```python
"""
kernel/execution/runner.py
EJECUTOR — Step Runner Determinista

Toma un ExecutionPlan y ejecuta cada step secuencialmente.
NO toma decisiones. Solo ejecuta lo que el Pensador planificó.

Maneja:
- Retry con backoff exponencial
- Timeout por step y global
- Circuit breaker por costo
- Métricas automáticas
- Escalación al Pensador si falla
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

from .models import (
    Encomienda, ExecutionPlan, Step, StepStatus, 
    EncomendaStatus, Deliverable, ExecutionMemory, ToolType
)
from .tools import ToolRegistry, ToolResult
from .planner import EncomendaPlanner


class StepRunner:
    """
    Ejecutor del Task Execution Loop.
    
    Código determinista. Sin LLM. Ejecuta steps según el plan.
    Si algo falla, escala al Pensador (Planner) para re-planificación.
    """
    
    MAX_REPLAN_ATTEMPTS = 2              # Máximo de re-planificaciones
    BACKOFF_BASE_SECONDS = 2             # Base para backoff exponencial
    
    def __init__(
        self, 
        tool_registry: ToolRegistry, 
        planner: EncomendaPlanner,
        supabase_client=None
    ):
        self.tools = tool_registry
        self.planner = planner
        self.supabase = supabase_client
        self._replan_count = 0
    
    async def execute_encomienda(self, encomienda: Encomienda) -> Encomienda:
        """
        Ejecuta una encomienda completa de principio a fin.
        
        Flujo:
        1. Pensador planifica
        2. Ejecutor ejecuta steps
        3. Si falla → Pensador re-planifica
        4. Brand Engine valida deliverable
        5. Registra en memoria
        """
        encomienda.status = EncomendaStatus.PLANNING
        encomienda.started_at = datetime.now(timezone.utc)
        self._replan_count = 0
        
        # PASO 1: Pensador planifica
        plan = await self.planner.plan(encomienda)
        encomienda.execution_plan = plan
        
        # Verificar presupuesto antes de ejecutar
        if plan.estimated_cost_usd > encomienda.max_budget_usd:
            encomienda.status = EncomendaStatus.FAILED
            encomienda.deliverable = Deliverable(
                type="error",
                summary=f"execution_budget_exceeded: Plan estima ${plan.estimated_cost_usd:.3f} > presupuesto ${encomienda.max_budget_usd:.2f}",
            )
            return encomienda
        
        # PASO 2: Ejecutar steps
        encomienda.status = EncomendaStatus.EXECUTING
        success = await self._execute_plan(encomienda, plan)
        
        if not success:
            encomienda.status = EncomendaStatus.FAILED
            await self._record_memory(encomienda, success=False)
            return encomienda
        
        # PASO 3: Construir deliverable
        deliverable = self._build_deliverable(plan)
        
        # PASO 4: Brand Engine valida
        encomienda.status = EncomendaStatus.VALIDATING
        brand_result = await self.tools.execute_tool(
            "brand_validate",
            {"output": deliverable.summary, "source": f"encomienda_{encomienda.id}"}
        )
        
        if brand_result.success:
            deliverable.brand_score = brand_result.output.get("brand_score", 0)
            deliverable.brand_validated = True
        
        encomienda.deliverable = deliverable
        encomienda.status = EncomendaStatus.COMPLETED
        encomienda.completed_at = datetime.now(timezone.utc)
        
        # PASO 5: Registrar en memoria
        await self._record_memory(encomienda, success=True)
        
        # Persistir resultado
        await self._persist_encomienda(encomienda)
        
        return encomienda
    
    async def _execute_plan(self, encomienda: Encomienda, plan: ExecutionPlan) -> bool:
        """Ejecuta todos los steps de un plan."""
        
        for step in plan.steps:
            # Check timeout global
            elapsed = (datetime.now(timezone.utc) - encomienda.started_at).total_seconds()
            if elapsed > encomienda.max_duration_seconds:
                step.status = StepStatus.FAILED
                step.error = "execution_global_timeout: Encomienda excedió tiempo máximo"
                return False
            
            # Check presupuesto
            if encomienda.total_cost_usd > encomienda.max_budget_usd:
                step.status = StepStatus.FAILED
                step.error = f"execution_budget_exceeded: ${encomienda.total_cost_usd:.3f} > ${encomienda.max_budget_usd:.2f}"
                return False
            
            # Check dependencias
            if not self._dependencies_met(step, plan.steps):
                step.status = StepStatus.SKIPPED
                continue
            
            # Ejecutar step con retry
            success = await self._execute_step_with_retry(step, encomienda)
            
            if not success:
                # Intentar re-planificación
                if self._replan_count < self.MAX_REPLAN_ATTEMPTS:
                    self._replan_count += 1
                    new_plan = await self.planner.replan(encomienda, step, step.error or "Unknown")
                    encomienda.execution_plan = new_plan
                    return await self._execute_plan(encomienda, new_plan)
                else:
                    return False
        
        return True
    
    async def _execute_step_with_retry(self, step: Step, encomienda: Encomienda) -> bool:
        """Ejecuta un step individual con retry y backoff."""
        
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now(timezone.utc)
        
        while step.retries <= step.max_retries:
            result = await self.tools.execute_tool(step.tool.value, step.tool_input)
            
            if result.success:
                step.status = StepStatus.SUCCESS
                step.actual_output = result.output
                step.cost_usd = result.cost_usd
                step.duration_ms = result.duration_ms
                step.completed_at = datetime.now(timezone.utc)
                
                # Acumular métricas en encomienda
                encomienda.total_cost_usd += result.cost_usd
                if step.tool in (ToolType.LLM_GENERATE, ToolType.LLM_ANALYZE):
                    encomienda.total_llm_calls += 1
                
                return True
            
            # Fallo — retry con backoff
            step.retries += 1
            step.error = result.error
            
            if not result.retryable:
                break
            
            if step.retries <= step.max_retries:
                step.status = StepStatus.RETRYING
                backoff = self.BACKOFF_BASE_SECONDS ** step.retries
                await asyncio.sleep(backoff)
        
        step.status = StepStatus.FAILED
        step.completed_at = datetime.now(timezone.utc)
        encomienda.retry_count += step.retries
        return False
    
    def _dependencies_met(self, step: Step, all_steps: list) -> bool:
        """Verifica que las dependencias de un step están completadas."""
        for dep_id in step.depends_on:
            dep_step = next((s for s in all_steps if s.id == dep_id), None)
            if dep_step and dep_step.status != StepStatus.SUCCESS:
                return False
        return True
    
    def _build_deliverable(self, plan: ExecutionPlan) -> Deliverable:
        """Construye el deliverable a partir de los outputs de los steps."""
        successful_steps = [s for s in plan.steps if s.status == StepStatus.SUCCESS]
        
        # El último step exitoso generalmente tiene el output final
        final_output = successful_steps[-1].actual_output if successful_steps else None
        
        return Deliverable(
            type="composite",
            content=final_output,
            summary=f"Encomienda completada: {len(successful_steps)}/{len(plan.steps)} steps exitosos",
            evidence=[
                f"Step {s.id}: {s.description} → OK ({s.duration_ms}ms, ${s.cost_usd:.4f})"
                for s in successful_steps
            ]
        )
    
    async def _record_memory(self, encomienda: Encomienda, success: bool):
        """Registra el aprendizaje de esta encomienda."""
        plan = encomienda.execution_plan
        if not plan:
            return
        
        memory = ExecutionMemory(
            encomienda_id=encomienda.id,
            encomienda_objective=encomienda.objective,
            success=success,
            total_steps=len(plan.steps),
            failed_steps=sum(1 for s in plan.steps if s.status == StepStatus.FAILED),
            total_cost_usd=encomienda.total_cost_usd,
            total_duration_seconds=int(
                (encomienda.completed_at - encomienda.started_at).total_seconds()
            ) if encomienda.completed_at and encomienda.started_at else 0,
            what_worked=[
                f"{s.tool.value}: {s.description}"
                for s in plan.steps if s.status == StepStatus.SUCCESS
            ],
            what_failed=[
                f"{s.tool.value}: {s.error}"
                for s in plan.steps if s.status == StepStatus.FAILED
            ],
            tools_used=list(set(s.tool.value for s in plan.steps)),
            unexpected_issues=[
                s.error for s in plan.steps 
                if s.status == StepStatus.FAILED and s.error
            ]
        )
        
        if self.supabase:
            self.supabase.table("execution_memory").insert({
                "encomienda_id": memory.encomienda_id,
                "encomienda_objective": memory.encomienda_objective,
                "success": memory.success,
                "total_steps": memory.total_steps,
                "failed_steps": memory.failed_steps,
                "total_cost_usd": memory.total_cost_usd,
                "total_duration_seconds": memory.total_duration_seconds,
                "what_worked": memory.what_worked,
                "what_failed": memory.what_failed,
                "tools_used": memory.tools_used,
                "unexpected_issues": memory.unexpected_issues,
                "tags": memory.tags,
                "created_at": memory.created_at.isoformat()
            }).execute()
    
    async def _persist_encomienda(self, encomienda: Encomienda):
        """Persiste el estado final de la encomienda."""
        if self.supabase:
            self.supabase.table("encomiendas").upsert({
                "id": encomienda.id,
                "origin": encomienda.origin.value,
                "objective": encomienda.objective,
                "status": encomienda.status.value,
                "priority": encomienda.priority.value,
                "total_cost_usd": encomienda.total_cost_usd,
                "total_llm_calls": encomienda.total_llm_calls,
                "retry_count": encomienda.retry_count,
                "created_at": encomienda.created_at.isoformat(),
                "started_at": encomienda.started_at.isoformat() if encomienda.started_at else None,
                "completed_at": encomienda.completed_at.isoformat() if encomienda.completed_at else None,
                "deliverable_summary": encomienda.deliverable.summary if encomienda.deliverable else None,
                "brand_score": encomienda.deliverable.brand_score if encomienda.deliverable else None
            }).execute()
```

---

## Épica 72.5 — Orquestador: EmbrionExecutor

**Objetivo:** Unir Planner + Runner + ToolRegistry en una interfaz coherente que cualquier Embrión puede usar para ejecutar encomiendas.

**Criterios de Aceptación:**
- [ ] Archivo `kernel/execution/embrion_executor.py`
- [ ] Interfaz simple: `executor.execute(encomienda)` → Deliverable
- [ ] Integrado con EmbrionScheduler (puede recibir encomiendas programadas)
- [ ] Endpoints API para asignar encomiendas externamente
- [ ] Métricas expuestas para el Command Center

```python
"""
kernel/execution/embrion_executor.py
EMBRIÓN EXECUTOR — Orquestador del Task Execution Loop

Interfaz unificada que cualquier Embrión puede usar para ejecutar encomiendas.
Une: Planner (Pensador) + Runner (Ejecutor) + ToolRegistry (Herramientas)

Uso:
    executor = EmbrionExecutor(supabase, llm)
    result = await executor.execute(encomienda)
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from .models import Encomienda, EncomendaOrigin, EncomendaPriority, EncomendaStatus
from .tools import ToolRegistry
from .planner import EncomendaPlanner
from .runner import StepRunner


class EmbrionExecutor:
    """
    Orquestador del Task Execution Loop.
    
    Provee una interfaz simple para que cualquier Embrión ejecute encomiendas.
    Maneja la cola de encomiendas, priorización, y métricas globales.
    """
    
    def __init__(self, supabase_client=None, llm_client=None):
        self.supabase = supabase_client
        self.llm = llm_client
        
        # Componentes del TEL
        self.tool_registry = ToolRegistry(supabase_client=supabase_client, llm_client=llm_client)
        self.planner = EncomendaPlanner(llm_client=llm_client, tool_registry=self.tool_registry, supabase_client=supabase_client)
        self.runner = StepRunner(tool_registry=self.tool_registry, planner=self.planner, supabase_client=supabase_client)
        
        # Cola de encomiendas
        self._queue: List[Encomienda] = []
        self._active: Optional[Encomienda] = None
        
        # Métricas
        self._total_executed = 0
        self._total_succeeded = 0
        self._total_failed = 0
        self._total_cost_usd = 0.0
    
    async def execute(self, encomienda: Encomienda) -> Encomienda:
        """
        Ejecuta una encomienda de principio a fin.
        
        Interfaz principal — simple y directa.
        """
        self._active = encomienda
        
        try:
            result = await self.runner.execute_encomienda(encomienda)
            
            # Actualizar métricas
            self._total_executed += 1
            self._total_cost_usd += result.total_cost_usd
            
            if result.status == EncomendaStatus.COMPLETED:
                self._total_succeeded += 1
            else:
                self._total_failed += 1
            
            return result
        
        finally:
            self._active = None
    
    def create_encomienda(
        self,
        objective: str,
        origin: EncomendaOrigin = EncomendaOrigin.ALFREDO,
        context: str = "",
        constraints: List[str] = None,
        success_criteria: List[str] = None,
        priority: EncomendaPriority = EncomendaPriority.NORMAL,
        max_budget_usd: float = 0.50,
        max_duration_seconds: int = 1800
    ) -> Encomienda:
        """
        Factory method para crear encomiendas con defaults sensatos.
        """
        return Encomienda(
            id=str(uuid.uuid4()),
            origin=origin,
            objective=objective,
            context=context,
            constraints=constraints or [],
            success_criteria=success_criteria or [],
            priority=priority,
            max_budget_usd=max_budget_usd,
            max_duration_seconds=max_duration_seconds
        )
    
    async def execute_from_text(self, text: str, origin: EncomendaOrigin = EncomendaOrigin.ALFREDO) -> Encomienda:
        """
        Shortcut: crea y ejecuta una encomienda desde texto plano.
        
        Equivalente a lo que Manus hace cuando recibe un mensaje del usuario.
        """
        encomienda = self.create_encomienda(
            objective=text,
            origin=origin
        )
        return await self.execute(encomienda)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Métricas para el Command Center."""
        return {
            "module": "execution_engine",
            "total_executed": self._total_executed,
            "total_succeeded": self._total_succeeded,
            "total_failed": self._total_failed,
            "success_rate": (self._total_succeeded / self._total_executed * 100) if self._total_executed > 0 else 0,
            "total_cost_usd": round(self._total_cost_usd, 4),
            "avg_cost_per_encomienda": round(self._total_cost_usd / self._total_executed, 4) if self._total_executed > 0 else 0,
            "active_encomienda": self._active.objective if self._active else None,
            "queue_size": len(self._queue)
        }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Lista de herramientas disponibles (para UI/API)."""
        return self.tool_registry.get_available_tools()


# ─── API ROUTES ─────────────────────────────────────────────────────────

"""
kernel/execution/api_routes.py
Endpoints del Task Execution Loop
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/v1/execution", tags=["execution_engine"])


class CreateEncomendaRequest(BaseModel):
    objective: str
    context: Optional[str] = ""
    constraints: Optional[List[str]] = []
    success_criteria: Optional[List[str]] = []
    priority: Optional[str] = "normal"
    max_budget_usd: Optional[float] = 0.50


@router.post("/encomienda")
async def create_and_execute_encomienda(request: CreateEncomendaRequest):
    """Crea y ejecuta una encomienda."""
    encomienda = executor_instance.create_encomienda(
        objective=request.objective,
        context=request.context,
        constraints=request.constraints,
        success_criteria=request.success_criteria,
        priority=EncomendaPriority(request.priority),
        max_budget_usd=request.max_budget_usd
    )
    
    result = await executor_instance.execute(encomienda)
    
    return {
        "module": "execution_engine",
        "encomienda_id": result.id,
        "status": result.status.value,
        "deliverable": {
            "summary": result.deliverable.summary if result.deliverable else None,
            "brand_score": result.deliverable.brand_score if result.deliverable else None
        },
        "metrics": {
            "cost_usd": result.total_cost_usd,
            "llm_calls": result.total_llm_calls,
            "retries": result.retry_count
        }
    }


@router.get("/metrics")
async def get_execution_metrics():
    """Métricas del Execution Engine para el Command Center."""
    return executor_instance.get_metrics()


@router.get("/tools")
async def list_available_tools():
    """Lista herramientas disponibles."""
    return {
        "module": "execution_engine",
        "tools": executor_instance.get_available_tools()
    }


@router.get("/history")
async def get_execution_history(limit: int = 20):
    """Historial de encomiendas ejecutadas."""
    # Query Supabase
    return {"module": "execution_engine", "history": []}
```

---

## Épica 72.6 — Tablas Supabase

**Objetivo:** Crear las tablas necesarias para persistir encomiendas, planes, y memoria.

```sql
-- Tabla: encomiendas
CREATE TABLE IF NOT EXISTS encomiendas (
    id TEXT PRIMARY KEY,
    origin TEXT NOT NULL CHECK (origin IN ('alfredo', 'embrion', 'self', 'scheduler', 'guardian')),
    origin_id TEXT,
    objective TEXT NOT NULL,
    context TEXT DEFAULT '',
    constraints JSONB DEFAULT '[]',
    success_criteria JSONB DEFAULT '[]',
    priority TEXT NOT NULL DEFAULT 'normal',
    deadline TIMESTAMPTZ,
    max_budget_usd NUMERIC(10,4) DEFAULT 0.50,
    max_duration_seconds INTEGER DEFAULT 1800,
    status TEXT NOT NULL DEFAULT 'received',
    total_cost_usd NUMERIC(10,4) DEFAULT 0,
    total_llm_calls INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    deliverable_summary TEXT,
    brand_score INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Tabla: execution_plans
CREATE TABLE IF NOT EXISTS execution_plans (
    id BIGSERIAL PRIMARY KEY,
    encomienda_id TEXT REFERENCES encomiendas(id),
    version INTEGER NOT NULL DEFAULT 1,
    steps JSONB NOT NULL DEFAULT '[]',
    estimated_cost_usd NUMERIC(10,4) DEFAULT 0,
    estimated_duration_seconds INTEGER DEFAULT 0,
    confidence NUMERIC(3,2) DEFAULT 0,
    reasoning TEXT,
    fallback_strategy TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla: execution_steps
CREATE TABLE IF NOT EXISTS execution_steps (
    id BIGSERIAL PRIMARY KEY,
    encomienda_id TEXT REFERENCES encomiendas(id),
    step_order INTEGER NOT NULL,
    description TEXT NOT NULL,
    tool TEXT NOT NULL,
    tool_input JSONB DEFAULT '{}',
    expected_output TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    actual_output JSONB,
    error TEXT,
    retries INTEGER DEFAULT 0,
    cost_usd NUMERIC(10,4) DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Tabla: execution_memory (aprendizaje acumulativo)
CREATE TABLE IF NOT EXISTS execution_memory (
    id BIGSERIAL PRIMARY KEY,
    encomienda_id TEXT REFERENCES encomiendas(id),
    encomienda_objective TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    total_steps INTEGER DEFAULT 0,
    failed_steps INTEGER DEFAULT 0,
    total_cost_usd NUMERIC(10,4) DEFAULT 0,
    total_duration_seconds INTEGER DEFAULT 0,
    what_worked JSONB DEFAULT '[]',
    what_failed JSONB DEFAULT '[]',
    tools_used JSONB DEFAULT '[]',
    unexpected_issues JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    similar_to TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_encomiendas_status ON encomiendas(status);
CREATE INDEX idx_encomiendas_origin ON encomiendas(origin);
CREATE INDEX idx_encomiendas_created ON encomiendas(created_at DESC);
CREATE INDEX idx_execution_memory_objective ON execution_memory USING gin(to_tsvector('spanish', encomienda_objective));
CREATE INDEX idx_execution_memory_success ON execution_memory(success);
CREATE INDEX idx_execution_steps_encomienda ON execution_steps(encomienda_id);
```

---

## Métricas de Éxito

| Métrica | Target | Cómo se mide |
|---|---|---|
| Encomienda Success Rate | ≥ 70% (MVP) | Completadas / Total |
| Avg Cost per Encomienda | < $0.10 | Costo total / encomiendas |
| Avg Duration | < 5 min | Tiempo promedio de ejecución |
| Replan Rate | < 30% | Veces que necesitó re-planificar |
| Brand Score promedio | ≥ 75 | Score del Brand Engine en deliverables |
| Memory Utilization | > 0 | Veces que consultó memoria para planificar |
| Tool Diversity | ≥ 3 tools/encomienda | Herramientas distintas usadas por encomienda |

---

## Dependencias

| Dependencia | Estado | Sprint |
|---|---|---|
| EmbrionScheduler | Activo | Sprint 53 |
| Supabase | Activo | Sprint 51 |
| FastAPI (kernel) | Activo | Sprint 51 |
| OpenAI client | Activo | Sprint 52 |
| Perplexity (Sonar Pro) | Activo | Sprint 52 |
| Brand Engine (Embrión-1) | Sprint 71 | Pendiente |

---

## Orden de Implementación

1. **72.1** Modelos de datos (sin dependencias) — 30 min
2. **72.6** Tablas Supabase (sin dependencias) — 15 min
3. **72.2** Tool Registry (depende de 72.1) — 1h
4. **72.3** Planner/Pensador (depende de 72.1 + 72.2) — 1h
5. **72.4** Runner/Ejecutor (depende de 72.2 + 72.3) — 1h
6. **72.5** Orquestador + API (depende de todo) — 45 min

**MVP mínimo:** 72.1 + 72.2 + 72.4 (sin Planner LLM). El Runner puede ejecutar steps hardcodeados sin planificación LLM. El Planner se agrega después.

---

## Nota para el Hilo A (Ejecutor)

> **TASK EXECUTION LOOP — El corazón de la autonomía.**
>
> Este sprint le da al Embrión la capacidad de HACER cosas, no solo monitorear.
> Es el equivalente a lo que Manus hace cuando recibe una tarea.
>
> Patrón obligatorio:
> - Pensador (Planner) planifica con LLM potente
> - Ejecutor (Runner) materializa con código determinista
> - Herramientas (ToolRegistry) son funciones Python con input/output tipado
> - Memoria (ExecutionMemory) acumula aprendizaje
>
> El TEL es GENÉRICO — cualquier Embrión puede usarlo.
> El Embrión-1 (Brand Engine) lo usa para ejecutar validaciones complejas.
> El Embrión-2 (Motor de Ventas) lo usará para ejecutar campañas.
> El Embrión-3 (SEO) lo usará para ejecutar auditorías.
>
> Si implementas esto bien, TODOS los Embriones futuros heredan la capacidad de ejecutar.
>
> **DIRECTIVA DE MARCA:** Los error messages del TEL deben seguir el formato
> `execution_{module}_{failure_type}: {descripción con contexto}`.
> No usar "Error", "Failed", o mensajes genéricos.
