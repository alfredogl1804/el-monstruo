# Sprint 51 — "Los Cimientos Perpetuos"

**Fecha:** 1 mayo 2026
**Duración estimada:** 5-7 días
**Presupuesto infra:** ~$0/mes adicional (usa Supabase + Perplexity ya pagados)
**Modelo de planificación:** claude-opus-4-7 (ya activo en task_planner.py)

---

## Contexto

El Monstruo tiene 20 tools en `tools/`, un kernel funcional con Task Planner (ReAct loop, stuck detection, budget control), 4 capas de memoria (Mem0, MemPalace, LightRAG, embrion_memoria), y un Embrión autónomo corriendo 24/7. Los Sprints 43-50 cerraron los gaps de File Ops, Web Dev, Stuck Detector, y E2E tests.

Lo que NO tiene: los cimientos perpetuos que hacen que todo lo que se construya encima sea robusto. Este sprint los enciende.

---

## Épica 51.1 — Error Memory (Objetivo #4)

> "No se equivoca en lo mismo dos veces. Nunca."

### 51.1.1 — Qué se adopta (Objetivo #7: no inventar la rueda)

**Mem0 v2.0.0** — ya instalado (`mem0ai==2.0.0` en requirements.txt), ya integrado (`memory/mem0_bridge.py`), ya conectado a pgvector en Supabase. Mem0 soporta metadata filtering, user-scoped memories, y búsqueda semántica por embeddings. No necesitamos otra librería — extendemos lo que ya existe.

### 51.1.2 — Schema de Error Memory

Mem0 almacena memorias como texto + metadata + embedding. No creamos tabla nueva — usamos Mem0 con metadata estructurada para errores.

**Formato de cada error memory:**

```python
# Texto que Mem0 almacena (se convierte en embedding para búsqueda semántica)
memory_text = f"""
ERROR en tool '{tool_name}': {error_message}
CONTEXTO: {step_description}
ROOT CAUSE: {root_cause_analysis}
FIX APLICADO: {fix_description}
REGLA: {prevention_rule}
"""

# Metadata para filtrado exacto
metadata = {
    "type": "error_memory",          # Filtro principal
    "tool_name": "web_dev",          # Qué tool falló
    "error_category": "timeout",     # Categoría: timeout, auth, schema, api_change, etc.
    "severity": "high",              # high, medium, low
    "confidence": 0.9,               # 0.0-1.0, sube con cada validación
    "sprint": 51,                    # Cuándo se registró
    "times_prevented": 0,            # Cuántas veces esta regla evitó un error
    "last_triggered": "2026-05-01",  # Última vez que se consultó
}
```

### 51.1.3 — Archivo a crear: `memory/error_memory.py`

```python
"""
memory/error_memory.py — Error Memory System (Sprint 51, Objetivo #4)
=====================================================================
Extiende Mem0 para registrar, buscar, y aprender de errores.
Nunca se equivoca en lo mismo dos veces.

Hooks:
    - post_error(tool, error, context) → analiza, extrae root cause, guarda
    - pre_action(tool, args) → busca errores similares, retorna warnings
    - update_confidence(memory_id, prevented=True) → sube/baja confianza
"""
from __future__ import annotations
import json
import asyncio
from datetime import datetime, timezone
from typing import Optional
import structlog

logger = structlog.get_logger("memory.error_memory")

# Usa el bridge existente de Mem0
from memory.mem0_bridge import _get_mem0

# User ID fijo para error memories (separado de user memories)
ERROR_MEMORY_USER = "error_memory_system"


async def post_error(
    tool_name: str,
    error_message: str,
    step_description: str,
    root_cause: str,
    fix_applied: str,
    prevention_rule: str,
    severity: str = "medium",
    error_category: str = "unknown",
) -> dict:
    """
    Registra un error en Error Memory después de que ocurre y se resuelve.
    Llamado por el Task Planner después de un retry exitoso o un step failure.
    """
    memory_text = (
        f"ERROR en tool '{tool_name}': {error_message}\n"
        f"CONTEXTO: {step_description}\n"
        f"ROOT CAUSE: {root_cause}\n"
        f"FIX APLICADO: {fix_applied}\n"
        f"REGLA: {prevention_rule}"
    )
    metadata = {
        "type": "error_memory",
        "tool_name": tool_name,
        "error_category": error_category,
        "severity": severity,
        "confidence": 0.8,  # Empieza en 0.8, sube con validaciones
        "sprint": 51,
        "times_prevented": 0,
        "last_triggered": datetime.now(timezone.utc).isoformat(),
    }
    try:
        m = _get_mem0()
        messages = [{"role": "assistant", "content": memory_text}]
        result = await asyncio.to_thread(
            m.add, messages, user_id=ERROR_MEMORY_USER, metadata=metadata
        )
        logger.info(
            "error_memory_saved",
            tool=tool_name,
            category=error_category,
            severity=severity,
        )
        return {"saved": True, "result": result}
    except Exception as e:
        logger.error("error_memory_save_failed", error=str(e))
        return {"saved": False, "error": str(e)}


async def pre_action_check(
    tool_name: str,
    step_description: str,
    limit: int = 3,
) -> list[dict]:
    """
    Pre-flight check: busca errores similares ANTES de ejecutar una acción.
    Llamado por el Task Planner antes de cada tool call en el ReAct loop.
    
    Returns:
        Lista de warnings con errores pasados relevantes y sus reglas de prevención.
        Lista vacía = no hay errores conocidos para esta acción.
    """
    query = f"error en {tool_name}: {step_description}"
    try:
        m = _get_mem0()
        result = await asyncio.to_thread(
            m.search,
            query,
            user_id=ERROR_MEMORY_USER,
            limit=limit,
        )
        warnings = []
        raw = result.get("results", []) if isinstance(result, dict) else result
        for r in raw:
            score = r.get("score", 0.0)
            if score > 0.7:  # Solo warnings con alta relevancia
                warnings.append({
                    "id": r.get("id", ""),
                    "memory": r.get("memory", ""),
                    "score": score,
                    "metadata": r.get("metadata", {}),
                })
        if warnings:
            logger.info(
                "error_memory_preflight_hit",
                tool=tool_name,
                warnings=len(warnings),
            )
        return warnings
    except Exception as e:
        logger.warning("error_memory_preflight_failed", error=str(e))
        return []  # Fail open — no bloquear ejecución si Error Memory falla


async def update_confidence(memory_id: str, prevented: bool = True) -> None:
    """
    Actualiza la confianza de una regla de error.
    prevented=True → la regla evitó un error → sube confianza
    prevented=False → la regla no aplicaba (falso positivo) → baja confianza
    """
    # Mem0 v2 no soporta update de metadata directamente.
    # Workaround: log para análisis posterior. En Sprint 52+ se implementa
    # un pattern aggregator que lee estos logs y recalcula confianza.
    logger.info(
        "error_memory_confidence_update",
        memory_id=memory_id,
        prevented=prevented,
    )
```

### 51.1.4 — Hook en `kernel/task_planner.py`

**Archivo a modificar:** `kernel/task_planner.py`
**Método:** `_execute_step_with_react` (línea 845)
**Cambios:**

**A. Pre-flight check (ANTES del ReAct loop, después de construir el context):**

Insertar después de la línea que construye `user_message` (aprox. línea 890), antes del `for attempt in range(...)`:

```python
# ── Sprint 51: Error Memory Pre-flight ──────────────────
from memory.error_memory import pre_action_check
error_warnings = await pre_action_check(
    tool_name=step.tool_hint or "unknown",
    step_description=step.description,
)
if error_warnings:
    warning_text = "\n".join(
        f"⚠️ ERROR PREVIO: {w['memory'][:200]}"
        for w in error_warnings
    )
    user_message += f"\n\nADVERTENCIAS DE ERRORES PREVIOS (EVITAR):\n{warning_text}"
    logger.info("task_planner_preflight_warnings", step=step.index, warnings=len(error_warnings))
```

**B. Post-error hook (DESPUÉS de un step failure, en el bloque except):**

En el bloque donde `step.error` se asigna (aprox. línea 1060), agregar:

```python
# ── Sprint 51: Error Memory Post-error ──────────────────
try:
    from memory.error_memory import post_error
    # Pedir a Claude que analice el root cause
    root_cause_resp = await asyncio.wait_for(
        client.messages.create(
            model="claude-opus-4-7",
            max_tokens=500,
            system="Analiza este error y responde SOLO con JSON: {\"root_cause\": \"...\", \"prevention_rule\": \"...\", \"category\": \"timeout|auth|schema|api_change|dependency|logic|unknown\"}",
            messages=[{"role": "user", "content": f"Tool: {tool_name}\nError: {str(e)[:500]}\nContexto: {step.description}"}],
        ),
        timeout=15,
    )
    import json as _json
    analysis = _json.loads(root_cause_resp.content[0].text)
    await post_error(
        tool_name=tool_name or step.tool_hint or "unknown",
        error_message=str(e)[:300],
        step_description=step.description,
        root_cause=analysis.get("root_cause", "unknown"),
        fix_applied="pending",  # Se actualiza si el retry tiene éxito
        prevention_rule=analysis.get("prevention_rule", ""),
        severity="high" if attempt >= MAX_RETRIES_PER_STEP else "medium",
        error_category=analysis.get("category", "unknown"),
    )
except Exception as em_err:
    logger.warning("error_memory_post_error_failed", error=str(em_err))
```

### 51.1.5 — Criterio de éxito

| Test | Descripción | Pasa/Falla |
|------|-------------|------------|
| T1 | `post_error()` guarda en Mem0 con metadata type=error_memory | Verificar con `mem0.search("error", user_id="error_memory_system")` retorna resultado |
| T2 | `pre_action_check("web_dev", "deploy a Vercel")` retorna el error guardado en T1 | Score > 0.7 |
| T3 | El Task Planner inyecta warnings en el prompt cuando hay errores previos | Log `task_planner_preflight_warnings` aparece |
| T4 | Después de un step failure, se registra automáticamente en Error Memory | Log `error_memory_saved` aparece |
| T5 | E2E: Provocar un error conocido → verificar que en la siguiente ejecución el warning aparece | El segundo intento no repite el error |

### 51.1.6 — Costo estimado

- Root cause analysis por error: ~$0.02 (500 tokens Claude)
- Pre-flight search: ~$0.001 (Mem0 pgvector local, sin API call)
- Total por plan con 1 error: ~$0.02 adicional
- Total mensual estimado (50 errores/día): ~$30/mes

---

## Épica 51.2 — Clasificador Magna/Premium (Objetivo #5)

> "Si un dato puede haber cambiado desde que el modelo fue entrenado, NO es un hecho — es una hipótesis que requiere verificación."

### 51.2.1 — Qué se adopta (Objetivo #7)

**Perplexity Sonar API** — ya integrado como Sabio (`tools/consult_sabios.py`), ya tiene `SONAR_API_KEY` en Railway. Perplexity retorna respuestas con citations en tiempo real. No necesitamos otra API — extendemos el uso del Sabio que ya existe.

### 51.2.2 — Arquitectura del Clasificador

El clasificador NO es un modelo ML. Es un sistema de reglas + heurísticas que clasifica claims en dos categorías:

```
PREMIUM (no validar):
  - Matemáticas, lógica, álgebra
  - Historia (eventos pasados con fecha)
  - Geografía física
  - Leyes de la física/química/biología
  - Gramática, lingüística
  - Filosofía clásica, literatura publicada

MAGNA (siempre validar):
  - TODO lo tecnológico (frameworks, APIs, versiones, herramientas, IA)
  - Precios, costos, planes de servicio
  - Empresas (estado actual, empleados, productos)
  - Noticias, eventos recientes
  - Best practices (cambian con el tiempo)
  - Documentación técnica (puede estar desactualizada)
  - Estadísticas, métricas de mercado
  - Regulaciones, leyes vigentes
  - Personas vivas (cargos, roles, estado)
```

### 51.2.3 — Archivo a crear: `kernel/magna_classifier.py`

```python
"""
kernel/magna_classifier.py — Clasificador Magna/Premium (Sprint 51, Objetivo #5)
=================================================================================
Clasifica datos/claims como PREMIUM (inmutables) o MAGNA (requieren validación
en tiempo real). Todo lo tecnológico es MAGNA. Siempre.

Integración:
    - Task Planner lo usa antes de ejecutar steps que dependen de datos externos
    - El Embrión lo usa en sus ciclos de pensamiento
    - Los Sabios pasan por el filtro antes de que sus respuestas se usen
"""
from __future__ import annotations
import re
from enum import Enum
from typing import Optional
import structlog

logger = structlog.get_logger("kernel.magna_classifier")


class DataFreshness(str, Enum):
    PREMIUM = "premium"  # Inmutable, no requiere validación
    MAGNA = "magna"      # Caduca, requiere validación en tiempo real


# ── Patrones de detección ────────────────────────────────────────────

# Keywords que indican datos MAGNA (tecnología, actualidad, mercado)
MAGNA_KEYWORDS = [
    # Tecnología
    r"\b(api|sdk|framework|library|librería|package|paquete|version|versión)\b",
    r"\b(python|javascript|typescript|react|vue|angular|next\.?js|node\.?js)\b",
    r"\b(docker|kubernetes|aws|gcp|azure|vercel|railway|supabase|firebase)\b",
    r"\b(openai|anthropic|google|meta|mistral|llama|gpt|claude|gemini)\b",
    r"\b(github|npm|pypi|pip|pnpm|yarn)\b",
    r"\b(browser.use|stagehand|playwright|selenium|puppeteer)\b",
    r"\b(langchain|langgraph|crewai|autogen|mem0|lightrag)\b",
    r"\b(stripe|paypal|twilio|sendgrid|cloudflare)\b",
    # Mercado y negocios
    r"\b(precio|price|pricing|costo|cost|plan|tier|suscripción|subscription)\b",
    r"\b(trending|tendencia|market share|cuota de mercado)\b",
    r"\b(startup|empresa|company|CEO|CTO|fundador|founder)\b",
    r"\b(revenue|ingresos|valuation|valoración|funding|ronda)\b",
    # Actualidad
    r"\b(hoy|today|actualmente|currently|ahora|now|reciente|recent)\b",
    r"\b(2025|2026|2027|último|latest|nuevo|new|actualizado|updated)\b",
    r"\b(ley|law|regulación|regulation|normativa|compliance|gdpr)\b",
    # IA y modelos
    r"\b(modelo|model|benchmark|score|accuracy|parámetros|parameters)\b",
    r"\b(fine.?tune|training|entrenamiento|dataset|token)\b",
    r"\b(best practice|mejor práctica|recomendación|recommendation)\b",
]

# Keywords que indican datos PREMIUM (inmutables)
PREMIUM_KEYWORDS = [
    r"\b(teorema|theorem|axioma|axiom|ley de newton|ley de ohm)\b",
    r"\b(pi|euler|fibonacci|pitágoras|pythagoras)\b",
    r"\b(segunda guerra|world war|revolución francesa|french revolution)\b",
    r"\b(continente|continent|océano|ocean|río|river|montaña|mountain)\b",
    r"\b(tabla periódica|periodic table|elemento químico|chemical element)\b",
    r"\b(gramática|grammar|sintaxis|syntax|etimología|etymology)\b",
    r"\b(platón|aristóteles|sócrates|kant|nietzsche|descartes)\b",
]

# Compilar una vez
_MAGNA_PATTERNS = [re.compile(p, re.IGNORECASE) for p in MAGNA_KEYWORDS]
_PREMIUM_PATTERNS = [re.compile(p, re.IGNORECASE) for p in PREMIUM_KEYWORDS]


def classify(text: str) -> DataFreshness:
    """
    Clasifica un texto/claim como PREMIUM o MAGNA.
    
    Regla: si hay CUALQUIER indicador MAGNA, es MAGNA.
    Solo es PREMIUM si NO hay indicadores MAGNA y SÍ hay indicadores PREMIUM.
    Default: MAGNA (fail-safe — en caso de duda, validar).
    """
    magna_score = sum(1 for p in _MAGNA_PATTERNS if p.search(text))
    premium_score = sum(1 for p in _PREMIUM_PATTERNS if p.search(text))
    
    if magna_score > 0:
        return DataFreshness.MAGNA
    if premium_score > 0:
        return DataFreshness.PREMIUM
    
    # Default: MAGNA (fail-safe)
    return DataFreshness.MAGNA


async def validate_if_magna(
    claim: str,
    context: str = "",
) -> dict:
    """
    Si el claim es MAGNA, lo valida contra Perplexity Sonar en tiempo real.
    Si es PREMIUM, lo retorna sin validar.
    
    Returns:
        {
            "classification": "magna" | "premium",
            "validated": True | False,
            "original_claim": "...",
            "validation_result": "..." | None,
            "citations": [...] | None,
            "confidence": 0.0-1.0,
        }
    """
    freshness = classify(claim)
    
    if freshness == DataFreshness.PREMIUM:
        return {
            "classification": "premium",
            "validated": False,  # No necesita validación
            "original_claim": claim,
            "validation_result": None,
            "citations": None,
            "confidence": 0.95,
        }
    
    # Es MAGNA — validar con Perplexity Sonar
    try:
        import os
        import httpx
        
        sonar_key = os.environ.get("SONAR_API_KEY", "")
        if not sonar_key:
            logger.warning("magna_validation_no_key")
            return {
                "classification": "magna",
                "validated": False,
                "original_claim": claim,
                "validation_result": None,
                "citations": None,
                "confidence": 0.3,  # Baja confianza sin validación
            }
        
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {sonar_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar-pro",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Verifica si la siguiente afirmación es correcta HOY. Responde con JSON: {\"is_correct\": true/false, \"current_info\": \"...\", \"confidence\": 0.0-1.0}",
                        },
                        {
                            "role": "user",
                            "content": f"Afirmación a verificar: {claim}\nContexto: {context}",
                        },
                    ],
                },
            )
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = data.get("citations", [])
            
            import json
            try:
                validation = json.loads(content)
            except json.JSONDecodeError:
                validation = {"is_correct": None, "current_info": content, "confidence": 0.5}
            
            logger.info(
                "magna_validated",
                claim=claim[:100],
                is_correct=validation.get("is_correct"),
                confidence=validation.get("confidence", 0.5),
            )
            
            return {
                "classification": "magna",
                "validated": True,
                "original_claim": claim,
                "validation_result": validation.get("current_info", ""),
                "is_correct": validation.get("is_correct"),
                "citations": citations,
                "confidence": validation.get("confidence", 0.5),
            }
    except Exception as e:
        logger.error("magna_validation_failed", error=str(e), claim=claim[:100])
        return {
            "classification": "magna",
            "validated": False,
            "original_claim": claim,
            "validation_result": None,
            "citations": None,
            "confidence": 0.3,
        }
```

### 51.2.4 — Hook en `kernel/task_planner.py`

**Integración en el planning prompt** (línea 240 aprox.):

Agregar al `planning_prompt` después de las instrucciones existentes:

```python
# ── Sprint 51: Magna/Premium awareness ──────────────────
planning_prompt += """

REGLA CRÍTICA — GASOLINA MAGNA vs PREMIUM:
- Todo dato tecnológico (APIs, frameworks, versiones, herramientas, precios, best practices) es MAGNA — puede estar obsoleto.
- Cuando un paso depende de datos tecnológicos, SIEMPRE incluye un sub-paso de validación en tiempo real ANTES de usarlo.
- Usa web_search o browse_web para validar datos MAGNA antes de tomar decisiones basadas en ellos.
- Solo los datos matemáticos, históricos, geográficos y de ciencias naturales son PREMIUM (no requieren validación).
"""
```

**Integración en el executor** (método `_execute_tool`, cuando se usa `web_dev` o `code_exec`):

```python
# ── Sprint 51: Magna validation para tools que dependen de datos tech ──
if tool_name in ("web_dev", "code_exec", "github") and step.description:
    from kernel.magna_classifier import classify, DataFreshness
    if classify(step.description) == DataFreshness.MAGNA:
        logger.info("magna_step_detected", tool=tool_name, step=step.index)
        # El warning ya está en el prompt via planning_prompt
        # Aquí solo logueamos para observabilidad
```

### 51.2.5 — Criterio de éxito

| Test | Descripción | Pasa/Falla |
|------|-------------|------------|
| T1 | `classify("browser-use version 0.12.6")` retorna MAGNA | |
| T2 | `classify("el teorema de Pitágoras dice que a²+b²=c²")` retorna PREMIUM | |
| T3 | `classify("Stripe Connect API pricing")` retorna MAGNA | |
| T4 | `classify("la Segunda Guerra Mundial terminó en 1945")` retorna PREMIUM | |
| T5 | `classify("React 19 es la última versión")` retorna MAGNA | |
| T6 | `classify("algo ambiguo sin keywords claros")` retorna MAGNA (fail-safe) | |
| T7 | `validate_if_magna("browser-use tiene 78K stars en GitHub")` retorna validación de Perplexity con citations | |
| T8 | El planning prompt incluye la regla MAGNA/PREMIUM | Verificar en logs |

### 51.2.6 — Costo estimado

- Clasificación: $0 (regex local, sin API call)
- Validación Perplexity (solo cuando se necesita): ~$0.005 por query
- Total por plan con 3 validaciones: ~$0.015
- Total mensual estimado (100 validaciones/día): ~$15/mes

---

## Épica 51.3 — Browser Interactivo (Gap #1 pendiente del Sprint 47)

> "Sin browser real, El Monstruo es ciego ante el 90% de internet interactivo."

### 51.3.1 — Qué se adopta (Objetivo #7)

**browser-use v0.12.6** [1] — 78K+ stars en GitHub, Python nativo (`pip install browser-use`), built on Playwright, model-agnostic, 89.1% success rate en WebVoyager benchmark [2]. Es la herramienta best-in-class para browser automation en Python a fecha 1 mayo 2026.

**Por qué browser-use y no las alternativas:**

| Herramienta | Lenguaje | Self-hosted | Python nativo | Stars | Veredicto |
|---|---|---|---|---|---|
| browser-use | Python | Sí | Sí | 78K+ | **ADOPTAR** |
| Stagehand | TypeScript | Sí | No | 14K+ | Descartado — no Python |
| Firecrawl | API | No (SaaS) | SDK sí | 113K | Descartado — dependencia externa |
| Agent Browser | Rust/Node | Sí | No | 2K | Descartado — sin reasoning layer |

### 51.3.2 — Archivo a crear: `tools/interactive_browser.py`

```python
"""
tools/interactive_browser.py — Browser Interactivo (Sprint 51, Objetivo #7)
============================================================================
Reemplaza tools/browser.py (Cloudflare read-only) con browser-use (Playwright).
El Monstruo puede ahora: navegar, hacer click, llenar forms, hacer login,
tomar screenshots, extraer datos — todo lo que un humano puede hacer en un browser.

Dependencias:
    pip install browser-use playwright
    playwright install chromium

Integración:
    - Registrado en task_planner.py como tool "interactive_browser"
    - Usa Claude claude-opus-4-7 como LLM (ya configurado)
    - Self-hosted en Railway (Playwright headless)

Nota: tools/browser.py (Cloudflare) se mantiene como fallback read-only.
"""
from __future__ import annotations
import asyncio
import json
import os
from typing import Any, Optional
import structlog

logger = structlog.get_logger("tools.interactive_browser")


async def execute(action: str, params: dict) -> dict:
    """
    Ejecuta una acción de browser interactivo.
    
    Actions:
        - agent_task: Ejecutar una tarea completa en lenguaje natural
          params: {"task": "...", "url": "...", "max_steps": 10}
        - navigate: Navegar a una URL y extraer contenido
          params: {"url": "..."}
        - screenshot: Tomar screenshot de la página actual
          params: {"url": "..."}
    """
    try:
        if action == "agent_task":
            return await _agent_task(
                task=params.get("task", ""),
                url=params.get("url"),
                max_steps=params.get("max_steps", 10),
            )
        elif action == "navigate":
            return await _navigate(url=params["url"])
        elif action == "screenshot":
            return await _screenshot(url=params.get("url", ""))
        else:
            return {"error": f"Unknown action: {action}"}
    except ImportError:
        return {
            "error": "browser-use not installed. Run: pip install browser-use playwright && playwright install chromium",
            "fallback": "Use tools/browser.py (Cloudflare read-only) instead",
        }
    except Exception as e:
        logger.error("interactive_browser_error", action=action, error=str(e))
        return {"error": str(e)}


async def _agent_task(task: str, url: Optional[str] = None, max_steps: int = 10) -> dict:
    """Ejecuta una tarea completa usando browser-use agent."""
    from browser_use import Agent
    from langchain_anthropic import ChatAnthropic
    
    llm = ChatAnthropic(
        model_name="claude-opus-4-7",
        api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        timeout=60,
        max_tokens=4000,
    )
    
    full_task = task
    if url:
        full_task = f"Navega a {url} y luego: {task}"
    
    agent = Agent(
        task=full_task,
        llm=llm,
        max_actions_per_step=3,
    )
    
    result = await agent.run(max_steps=max_steps)
    
    return {
        "success": True,
        "result": str(result),
        "task": task,
        "steps_used": min(max_steps, 10),
    }


async def _navigate(url: str) -> dict:
    """Navegación simple — extraer contenido de una URL."""
    from browser_use import Agent
    from langchain_anthropic import ChatAnthropic
    
    llm = ChatAnthropic(
        model_name="claude-opus-4-7",
        api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        timeout=30,
        max_tokens=2000,
    )
    
    agent = Agent(
        task=f"Navigate to {url} and extract the main content of the page as structured text.",
        llm=llm,
        max_actions_per_step=2,
    )
    
    result = await agent.run(max_steps=3)
    return {"success": True, "content": str(result), "url": url}


async def _screenshot(url: str) -> dict:
    """Tomar screenshot de una URL."""
    from browser_use import Agent
    from langchain_anthropic import ChatAnthropic
    
    llm = ChatAnthropic(
        model_name="claude-opus-4-7",
        api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        timeout=30,
        max_tokens=1000,
    )
    
    agent = Agent(
        task=f"Navigate to {url} and take a screenshot.",
        llm=llm,
        max_actions_per_step=2,
    )
    
    result = await agent.run(max_steps=2)
    return {"success": True, "result": str(result), "url": url}
```

### 51.3.3 — Cambios en `requirements.txt`

Agregar:

```
# ── Browser Interactivo (Sprint 51) ────────────────────────────────────
# browser-use: AI browser agent built on Playwright
# MIT license — validated 2026-05-01 via PyPI (latest=0.12.6)
# 78K+ GitHub stars, 89.1% WebVoyager benchmark
# Requires: playwright install chromium (in Dockerfile/Railway)
browser-use==0.12.6
```

### 51.3.4 — Registro en `kernel/task_planner.py`

Agregar a `available_tools` (línea 224):

```python
"interactive_browser — navegar web interactivamente: click, llenar forms, login, extraer datos, screenshots (Playwright + browser-use)",
```

Agregar a `_EXECUTOR_TOOLS` (línea 472):

```python
{
    "name": "interactive_browser",
    "description": "Navegar web interactivamente con Playwright. Puede hacer click, llenar formularios, hacer login, extraer datos, tomar screenshots. Usar para cualquier interacción web que requiera más que leer una página.",
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Acción: agent_task (tarea completa en lenguaje natural), navigate (ir a URL), screenshot",
                "enum": ["agent_task", "navigate", "screenshot"],
            },
            "params": {
                "type": "object",
                "description": "Parámetros: {task, url, max_steps} para agent_task; {url} para navigate/screenshot",
            },
        },
        "required": ["action", "params"],
    },
},
```

Agregar al dispatch en `_execute_tool` (después del bloque de `browse_web`):

```python
elif tool_name == "interactive_browser":
    from tools.interactive_browser import execute as browser_execute
    result = await browser_execute(
        action=tool_input.get("action", "navigate"),
        params=tool_input.get("params", {}),
    )
    return json.dumps(result, ensure_ascii=False)
```

### 51.3.5 — Deploy en Railway

**Dockerfile cambio:**

```dockerfile
# Agregar después de pip install
RUN playwright install chromium --with-deps
```

**Railway env vars (ya existentes, no se necesitan nuevas):**
- `ANTHROPIC_API_KEY` — ya configurada

### 51.3.6 — Criterio de éxito

| Test | Descripción | Pasa/Falla |
|------|-------------|------------|
| T1 | `interactive_browser.execute("navigate", {"url": "https://example.com"})` retorna contenido | |
| T2 | `interactive_browser.execute("agent_task", {"task": "busca 'El Monstruo' en Google", "url": "https://google.com"})` completa la búsqueda | |
| T3 | `interactive_browser.execute("agent_task", {"task": "llena el form de contacto con datos de prueba", "url": "https://httpbin.org/forms/post"})` llena y envía el form | |
| T4 | Task Planner puede usar `interactive_browser` en un plan | Plan generado con tool_hint="interactive_browser" |
| T5 | E2E: "Navega a GitHub, busca browser-use, y dime cuántas stars tiene" | Retorna número correcto |

### 51.3.7 — Costo estimado

- browser-use usa Claude por debajo: ~$0.10-0.30 por tarea (depende de complejidad)
- Playwright en Railway: ~$0/mes adicional (ya está en el plan actual)
- Total mensual estimado (20 tareas browser/día): ~$60-180/mes

---

## Épica 51.4 — Vanguard Scanner (Objetivo #6, primera versión)

> "Si existe algo mejor en el mundo y El Monstruo no lo tiene, es un bug."

### 51.4.1 — Tabla `component_map` en Supabase

```sql
CREATE TABLE IF NOT EXISTS component_map (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    component_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,  -- 'memory', 'browser', 'llm', 'deploy', 'observability', etc.
    current_tool TEXT NOT NULL,
    current_version TEXT,
    best_known_tool TEXT,
    best_known_version TEXT,
    best_known_stars INTEGER DEFAULT 0,
    best_known_source TEXT,  -- URL de GitHub/PyPI/docs
    is_up_to_date BOOLEAN DEFAULT TRUE,
    last_checked TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed inicial con el stack actual
INSERT INTO component_map (component_name, category, current_tool, current_version, best_known_tool, best_known_version) VALUES
('browser_automation', 'browser', 'cloudflare_browser_run', 'GA_2026', 'browser-use', '0.12.6'),
('episodic_memory', 'memory', 'mem0', '2.0.0', 'mem0', '2.0.0'),
('deep_memory', 'memory', 'mempalace_pgvector', 'custom', 'mempalace_pgvector', 'custom'),
('knowledge_graph', 'memory', 'lightrag', '1.4.15', 'lightrag', '1.4.15'),
('llm_router', 'llm', 'custom_router', 'sprint27', 'custom_router', 'sprint27'),
('code_sandbox', 'execution', 'e2b', '2.6.1', 'e2b', '2.6.1'),
('web_deploy', 'deploy', 'vercel_cli', 'latest', 'vercel_cli', 'latest'),
('observability', 'observability', 'langfuse', '4.5.1', 'langfuse', '4.5.1'),
('task_orchestration', 'orchestration', 'langgraph', '0.4.x', 'langgraph', '0.4.x'),
('search', 'search', 'perplexity_sonar', 'sonar-pro', 'perplexity_sonar', 'sonar-pro'),
('mcp_server', 'protocol', 'fastmcp', '3.2.4', 'fastmcp', '3.2.4'),
('agent_protocol', 'protocol', 'copilotkit_agui', '0.1.87', 'copilotkit_agui', '0.1.87')
ON CONFLICT (component_name) DO NOTHING;
```

### 51.4.2 — Archivo a crear: `kernel/vanguard_scanner.py`

```python
"""
kernel/vanguard_scanner.py — Vanguard Scanner v1 (Sprint 51, Objetivo #6)
==========================================================================
Escanea el mundo cada 6 horas para detectar si existe algo mejor que lo que
El Monstruo tiene. Primera versión: consulta Perplexity Sonar para cada
componente del component_map.

Integración:
    - Llamado por el Embrión en su ciclo autónomo (cada 6h)
    - Escribe alertas en Supabase y notifica a Alfredo si hay upgrades
"""
from __future__ import annotations
import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Optional
import httpx
import structlog

logger = structlog.get_logger("kernel.vanguard_scanner")


async def scan_component(
    component_name: str,
    category: str,
    current_tool: str,
    current_version: str,
) -> dict:
    """
    Consulta Perplexity Sonar para verificar si existe algo mejor
    que current_tool para la categoría dada.
    """
    sonar_key = os.environ.get("SONAR_API_KEY", "")
    if not sonar_key:
        return {"error": "SONAR_API_KEY not set"}
    
    query = (
        f"What is the best {category} tool/library for AI agents as of today May 2026? "
        f"I currently use {current_tool} v{current_version}. "
        f"Is there something better? Compare stars, benchmarks, and production readiness. "
        f"Respond with JSON: {{\"best_tool\": \"...\", \"best_version\": \"...\", "
        f"\"stars\": N, \"is_better\": true/false, \"reason\": \"...\"}}"
    )
    
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {sonar_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar-pro",
                    "messages": [
                        {"role": "system", "content": "You are a technology analyst. Respond ONLY with valid JSON."},
                        {"role": "user", "content": query},
                    ],
                },
            )
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = data.get("citations", [])
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = {"best_tool": current_tool, "is_better": False, "reason": content}
            
            result["citations"] = citations
            result["component"] = component_name
            result["scanned_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(
                "vanguard_scan_result",
                component=component_name,
                current=current_tool,
                best=result.get("best_tool"),
                is_better=result.get("is_better"),
            )
            return result
    except Exception as e:
        logger.error("vanguard_scan_failed", component=component_name, error=str(e))
        return {"error": str(e), "component": component_name}


async def full_scan(db) -> list[dict]:
    """
    Escanea TODOS los componentes del component_map.
    Retorna lista de resultados con alertas para componentes desactualizados.
    """
    try:
        result = db._client.table("component_map").select("*").execute()
        components = result.data or []
    except Exception as e:
        logger.error("vanguard_full_scan_db_error", error=str(e))
        return [{"error": str(e)}]
    
    results = []
    for comp in components:
        scan = await scan_component(
            component_name=comp["component_name"],
            category=comp["category"],
            current_tool=comp["current_tool"],
            current_version=comp.get("current_version", "unknown"),
        )
        results.append(scan)
        
        # Actualizar component_map si encontró algo mejor
        if scan.get("is_better"):
            try:
                db._client.table("component_map").update({
                    "best_known_tool": scan.get("best_tool", ""),
                    "best_known_version": scan.get("best_version", ""),
                    "best_known_stars": scan.get("stars", 0),
                    "best_known_source": (scan.get("citations", [None]) or [None])[0],
                    "is_up_to_date": False,
                    "last_checked": datetime.now(timezone.utc).isoformat(),
                    "notes": scan.get("reason", ""),
                }).eq("component_name", comp["component_name"]).execute()
            except Exception as e:
                logger.warning("vanguard_update_failed", component=comp["component_name"], error=str(e))
        else:
            try:
                db._client.table("component_map").update({
                    "is_up_to_date": True,
                    "last_checked": datetime.now(timezone.utc).isoformat(),
                }).eq("component_name", comp["component_name"]).execute()
            except Exception as e:
                pass
        
        # Rate limit: no bombardear Perplexity
        await asyncio.sleep(2)
    
    # Generar alerta si hay componentes desactualizados
    outdated = [r for r in results if r.get("is_better")]
    if outdated:
        logger.warning(
            "vanguard_outdated_components",
            count=len(outdated),
            components=[r["component"] for r in outdated],
        )
    
    return results
```

### 51.4.3 — Criterio de éxito

| Test | Descripción | Pasa/Falla |
|------|-------------|------------|
| T1 | Tabla `component_map` creada en Supabase con 12 componentes | |
| T2 | `scan_component("browser_automation", "browser", "cloudflare_browser_run", "GA_2026")` retorna resultado de Perplexity | |
| T3 | `full_scan(db)` escanea los 12 componentes y actualiza la tabla | |
| T4 | Componentes desactualizados tienen `is_up_to_date=False` | |

### 51.4.4 — Costo estimado

- 12 componentes × $0.005/query × 4 scans/día = ~$0.24/día = ~$7.20/mes

---

## Resumen de Archivos

### Archivos a CREAR:

| Archivo | Épica | Descripción |
|---|---|---|
| `memory/error_memory.py` | 51.1 | Error Memory — post_error, pre_action_check, update_confidence |
| `kernel/magna_classifier.py` | 51.2 | Clasificador Magna/Premium — classify, validate_if_magna |
| `tools/interactive_browser.py` | 51.3 | Browser interactivo — browser-use wrapper |
| `kernel/vanguard_scanner.py` | 51.4 | Vanguard Scanner v1 — scan_component, full_scan |

### Archivos a MODIFICAR:

| Archivo | Cambio | Épica |
|---|---|---|
| `kernel/task_planner.py` | Pre-flight hook (Error Memory), Post-error hook, Magna awareness en prompt, Registro de interactive_browser | 51.1, 51.2, 51.3 |
| `requirements.txt` | Agregar `browser-use==0.12.6` | 51.3 |
| Dockerfile (Railway) | Agregar `playwright install chromium --with-deps` | 51.3 |

### SQL a ejecutar en Supabase:

| Script | Épica | Descripción |
|---|---|---|
| `CREATE TABLE component_map ...` | 51.4 | Tabla de componentes + seed de 12 componentes |

---

## Orden de Ejecución

```
Día 1-2: Épica 51.1 (Error Memory)
  → Crear memory/error_memory.py
  → Modificar kernel/task_planner.py (hooks)
  → Tests T1-T5

Día 2-3: Épica 51.2 (Magna/Premium)
  → Crear kernel/magna_classifier.py
  → Modificar kernel/task_planner.py (prompt + awareness)
  → Tests T1-T8

Día 3-5: Épica 51.3 (Browser Interactivo)
  → pip install browser-use playwright
  → Crear tools/interactive_browser.py
  → Modificar kernel/task_planner.py (registro)
  → Modificar requirements.txt + Dockerfile
  → Tests T1-T5

Día 5-6: Épica 51.4 (Vanguard Scanner v1)
  → SQL en Supabase (component_map)
  → Crear kernel/vanguard_scanner.py
  → Tests T1-T4

Día 6-7: E2E Integration Test
  → Plan completo que usa Error Memory + Magna validation + Browser
  → Verificar que los 4 cimientos funcionan juntos
```

---

## Presupuesto Total Sprint 51

| Concepto | Costo mensual estimado |
|---|---|
| Error Memory (root cause analysis) | ~$30/mes |
| Magna Validation (Perplexity) | ~$15/mes |
| Browser Interactivo (Claude calls) | ~$60-180/mes |
| Vanguard Scanner (Perplexity) | ~$7.20/mes |
| **TOTAL** | **~$112-232/mes** |

Nota: El costo de browser interactivo es el más variable. Se puede reducir usando un modelo más barato (gpt-5-mini) para tareas de navegación simples.

---

## Referencias

[1] browser-use GitHub: https://github.com/browser-use/browser-use — 78K+ stars, v0.12.6 (Apr 2, 2026)
[2] Firecrawl "11 Best AI Browser Agents in 2026": https://www.firecrawl.dev/blog/best-browser-agents — WebVoyager benchmark 89.1%
[3] Mem0 v2.0.0: https://pypi.org/project/mem0ai/ — ya instalado en requirements.txt
[4] Perplexity Sonar API: https://docs.perplexity.ai — ya integrado como Sabio
[5] Stagehand vs Browser Use (Apr 2026): https://scrapfly.io/blog/posts/stagehand-vs-browser-use — comparación detallada
