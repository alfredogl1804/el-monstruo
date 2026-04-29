"""
El Monstruo — Sprint 1 Architecture Skeleton
=============================================
Esqueleto completo listo para copiar y adaptar.
Integra: LangGraph + LiteLLM + Mem0 + Langfuse + Supabase

Generado: 2026-04-09
Fuente: el-monstruo-toolkit skill

INSTRUCCIONES:
1. Copiar este archivo al proyecto
2. Instalar requirements.txt
3. Configurar env vars (ver env_template.yaml)
4. Adaptar los nodos a la lógica específica del Monstruo
"""

import os
import json
import operator
from typing import TypedDict, Annotated, Literal

# === LANGGRAPH ===
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver  # Dev: in-memory
# from langgraph.checkpoint.postgres import PostgresSaver  # Prod: Supabase

# === LITELLM ===
import litellm
litellm.set_verbose = False  # True para debug

# === MEM0 ===
from mem0 import Memory

# === LANGFUSE ===
from langfuse.callback import CallbackHandler as LangfuseHandler

# === UTILIDADES ===
import requests
from openai import OpenAI


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

# LiteLLM model aliases → providers reales
CEREBROS = {
    "estratega": {
        "model": "openai/gpt-5.4",
        "max_tokens": 4000,
        "fallbacks": ["anthropic/claude-opus-4-6", "xai/grok-4.20-0309-reasoning"]
    },
    "arquitecto": {
        "model": "anthropic/claude-opus-4-6",
        "max_tokens": 4096,
        "fallbacks": ["openai/gpt-5.4"]
    },
    "creativo": {
        "model": "gemini/gemini-3.1-pro-preview",
        "max_tokens": 4096,
        "fallbacks": ["openai/gpt-5.4"]
    },
    "codigo": {
        "model": "xai/grok-4.20-0309-reasoning",
        "max_tokens": 2000,
        "fallbacks": ["anthropic/claude-opus-4-6"]
    },
    "razonador": {
        "model": "openrouter/deepseek/deepseek-r1",
        "max_tokens": 2000,
        "fallbacks": ["openai/gpt-5.4"]
    },
    "investigador": {
        "model": "perplexity/sonar-reasoning-pro",
        "max_tokens": 4000,
        "fallbacks": ["xai/grok-4.20-0309-reasoning"]
    }
}

# Mem0 config con Supabase pgvector
MEM0_CONFIG = {
    "vector_store": {
        "provider": "supabase",
        "config": {
            "url": os.environ.get("SUPABASE_URL", ""),
            "key": os.environ.get("SUPABASE_SERVICE_KEY", ""),
            "table_name": "monstruo_memory",
            "embedding_dimension": 1536
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",
            "api_key": os.environ.get("OPENAI_API_KEY", "")
        }
    }
}

# Langfuse handler
langfuse_handler = LangfuseHandler(
    public_key=os.environ.get("LANGFUSE_PUBLIC_KEY", ""),
    secret_key=os.environ.get("LANGFUSE_SECRET_KEY", ""),
    host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
) if os.environ.get("LANGFUSE_PUBLIC_KEY") else None


# ============================================================
# 2. ESTADO DEL GRAFO
# ============================================================

class MonstruoState(TypedDict):
    """Estado tipado que fluye por todo el grafo."""
    messages: Annotated[list, operator.add]  # Historial de mensajes
    user_id: str                              # ID del usuario
    intent: str                               # Intent clasificado
    cerebro_activo: str                       # Qué cerebro está procesando
    memoria_contexto: list                    # Memorias relevantes recuperadas
    resultado: str                            # Respuesta final
    metadata: dict                            # Metadata adicional


# ============================================================
# 3. FUNCIONES AUXILIARES
# ============================================================

def llamar_cerebro(cerebro_id: str, messages: list, system: str = "") -> str:
    """Llama a un cerebro específico con fallback automático via LiteLLM."""
    config = CEREBROS[cerebro_id]
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)

    try:
        response = litellm.completion(
            model=config["model"],
            messages=msgs,
            max_tokens=config["max_tokens"],
            fallbacks=config.get("fallbacks", []),
            timeout=120
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR en {cerebro_id}]: {str(e)}"


def recuperar_memoria(query: str, user_id: str, limit: int = 5) -> list:
    """Recupera memorias relevantes de Supabase via Mem0."""
    try:
        memory = Memory.from_config(MEM0_CONFIG)
        results = memory.search(query, user_id=user_id, limit=limit)
        return [r["memory"] for r in results] if results else []
    except Exception:
        return []


def guardar_memoria(content: str, user_id: str, metadata: dict = None):
    """Guarda nueva memoria en Supabase via Mem0."""
    try:
        memory = Memory.from_config(MEM0_CONFIG)
        memory.add(content, user_id=user_id, metadata=metadata or {})
    except Exception:
        pass  # No fallar por memoria


# ============================================================
# 4. NODOS DEL GRAFO
# ============================================================

def nodo_clasificador(state: MonstruoState) -> dict:
    """Clasifica el intent del mensaje del usuario."""
    last_message = state["messages"][-1]["content"]
    memoria = recuperar_memoria(last_message, state["user_id"])

    system_prompt = f"""Eres el clasificador del Monstruo. Analiza el mensaje y responde SOLO con una palabra:
- investigacion: si necesita buscar información actual
- analisis: si necesita razonamiento profundo o matemáticas
- creativo: si necesita contenido creativo o multimodal
- codigo: si necesita escribir o revisar código
- estrategia: si necesita planificación o toma de decisiones
- directo: si es una pregunta simple que puedes responder directamente

Contexto de memoria del usuario: {json.dumps(memoria[:3], ensure_ascii=False)}"""

    intent = llamar_cerebro("estratega", state["messages"], system_prompt).strip().lower()

    # Validar intent
    valid_intents = ["investigacion", "analisis", "creativo", "codigo", "estrategia", "directo"]
    if intent not in valid_intents:
        intent = "directo"

    return {
        "intent": intent,
        "cerebro_activo": "clasificador",
        "memoria_contexto": memoria
    }


def nodo_investigar(state: MonstruoState) -> dict:
    """Sub-grafo de investigación: Perplexity + Grok."""
    resultado = llamar_cerebro(
        "investigador",
        state["messages"],
        "Investiga en profundidad. Cita fuentes. Sé exhaustivo pero conciso."
    )
    return {"resultado": resultado, "cerebro_activo": "investigador"}


def nodo_analizar(state: MonstruoState) -> dict:
    """Sub-grafo de análisis: DeepSeek R1."""
    resultado = llamar_cerebro(
        "razonador",
        state["messages"],
        "Analiza paso a paso. Muestra tu razonamiento. Sé preciso."
    )
    return {"resultado": resultado, "cerebro_activo": "razonador"}


def nodo_crear(state: MonstruoState) -> dict:
    """Sub-grafo creativo: Gemini 3.1 Pro."""
    resultado = llamar_cerebro(
        "creativo",
        state["messages"],
        "Genera contenido creativo y original. Sé innovador."
    )
    return {"resultado": resultado, "cerebro_activo": "creativo"}


def nodo_codigo(state: MonstruoState) -> dict:
    """Sub-grafo de código: Grok 4.20."""
    resultado = llamar_cerebro(
        "codigo",
        state["messages"],
        "Escribe código limpio, documentado y funcional. Incluye manejo de errores."
    )
    return {"resultado": resultado, "cerebro_activo": "codigo"}


def nodo_estrategia(state: MonstruoState) -> dict:
    """Sub-grafo de estrategia: GPT-5.4."""
    memoria_str = "\n".join(state.get("memoria_contexto", [])[:3])
    resultado = llamar_cerebro(
        "estratega",
        state["messages"],
        f"Eres el estratega del Monstruo. Contexto de memoria:\n{memoria_str}\n\nPlanifica y decide."
    )
    return {"resultado": resultado, "cerebro_activo": "estratega"}


def nodo_directo(state: MonstruoState) -> dict:
    """Respuesta directa para preguntas simples."""
    resultado = llamar_cerebro("estratega", state["messages"])
    return {"resultado": resultado, "cerebro_activo": "estratega"}


def nodo_sintetizar(state: MonstruoState) -> dict:
    """Sintetiza la respuesta final y guarda en memoria."""
    # Guardar interacción en memoria
    if state.get("resultado"):
        guardar_memoria(
            f"Q: {state['messages'][-1]['content']}\nA: {state['resultado'][:500]}",
            state["user_id"],
            {"intent": state.get("intent", "unknown")}
        )
    return state


# ============================================================
# 5. ROUTER
# ============================================================

def router_por_intent(state: MonstruoState) -> Literal[
    "investigar", "analizar", "crear", "codigo", "estrategia", "directo"
]:
    """Ruta condicional basada en el intent clasificado."""
    return state.get("intent", "directo")


# ============================================================
# 6. COMPILAR GRAFO
# ============================================================

def build_monstruo_graph():
    """Construye y compila el grafo del Monstruo."""
    graph = StateGraph(MonstruoState)

    # Agregar nodos
    graph.add_node("clasificador", nodo_clasificador)
    graph.add_node("investigar", nodo_investigar)
    graph.add_node("analizar", nodo_analizar)
    graph.add_node("crear", nodo_crear)
    graph.add_node("codigo", nodo_codigo)
    graph.add_node("estrategia", nodo_estrategia)
    graph.add_node("directo", nodo_directo)
    graph.add_node("sintetizar", nodo_sintetizar)

    # Entry point
    graph.set_entry_point("clasificador")

    # Routing condicional
    graph.add_conditional_edges(
        "clasificador",
        router_por_intent,
        {
            "investigacion": "investigar",
            "analisis": "analizar",
            "creativo": "crear",
            "codigo": "codigo",
            "estrategia": "estrategia",
            "directo": "directo"
        }
    )

    # Todos convergen en sintetizador
    for node in ["investigar", "analizar", "crear", "codigo", "estrategia", "directo"]:
        graph.add_edge(node, "sintetizar")

    graph.add_edge("sintetizar", END)

    # Compilar con checkpointer
    # Dev: MemorySaver (in-memory)
    # Prod: PostgresSaver (Supabase)
    checkpointer = MemorySaver()

    callbacks = [langfuse_handler] if langfuse_handler else []

    return graph.compile(checkpointer=checkpointer)


# ============================================================
# 7. USO
# ============================================================

if __name__ == "__main__":
    app = build_monstruo_graph()

    # Ejemplo de invocación
    result = app.invoke(
        {
            "messages": [{"role": "user", "content": "¿Cuáles son las tendencias de IA en 2026?"}],
            "user_id": "alfredo",
            "intent": "",
            "cerebro_activo": "",
            "memoria_contexto": [],
            "resultado": "",
            "metadata": {}
        },
        config={
            "configurable": {"thread_id": "test-1"},
            "callbacks": [langfuse_handler] if langfuse_handler else []
        }
    )

    print(f"Intent: {result['intent']}")
    print(f"Cerebro: {result['cerebro_activo']}")
    print(f"Resultado: {result['resultado'][:500]}")
