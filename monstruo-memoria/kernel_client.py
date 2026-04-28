"""
kernel_client.py — Wrapper obligatorio para todas las llamadas al kernel del Monstruo.

REGLA: Ningún script llama al kernel directamente con requests.post.
Todo pasa por aquí. Los schemas están verificados con curl real contra
el kernel en producción (28-abr-2026).

Si el kernel cambia un endpoint, se cambia aquí y todos los scripts
se benefician sin tocar su código.

Schemas verificados:
  POST /v1/knowledge/ingest  → {content: str, source?: str, doc_type?: str}
  POST /v1/knowledge/query   → {query: str}
  POST /v1/chat              → {message: str, thread_id?: str}
  POST /v1/feedback          → {run_id: str, action: str}
  GET  /health               → sin auth
  GET  /health/auth          → con auth
  GET  /v1/memory/status     → con auth
  GET  /v1/stats             → con auth
"""

import os
import requests
from typing import Optional

KERNEL_URL = os.environ.get(
    "MONSTRUO_KERNEL_URL",
    "https://el-monstruo-kernel-production.up.railway.app"
)

# La key se busca en este orden:
# 1. Variable de entorno MONSTRUO_API_KEY
# 2. Archivo ~/CONTEXT.md (parseado)
# 3. Hardcoded como último recurso (la key actual)
def _get_key() -> str:
    key = os.environ.get("MONSTRUO_API_KEY", "")
    if key:
        return key
    # Fallback: leer de CONTEXT.md
    ctx = os.path.expanduser("~/CONTEXT.md")
    if os.path.exists(ctx):
        with open(ctx) as f:
            for line in f:
                if "Kernel API Key:" in line:
                    # Formato: '- **Kernel API Key:** c3f0cbaa-...'
                    val = line.split("Kernel API Key:", 1)[1].strip()
                    # Limpiar markdown residual (**, *, espacios)
                    val = val.replace("**", "").replace("*", "").strip()
                    if val:
                        return val
    # Último recurso
    return "c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259"


def _headers() -> dict:
    return {
        "X-API-Key": _get_key(),
        "Content-Type": "application/json",
    }


def _post(path: str, payload: dict, timeout: int = 60) -> dict:
    """POST genérico al kernel. Retorna el JSON de respuesta o lanza excepción."""
    resp = requests.post(
        f"{KERNEL_URL}{path}",
        headers=_headers(),
        json=payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def _get(path: str, timeout: int = 15) -> dict:
    """GET genérico al kernel."""
    resp = requests.get(
        f"{KERNEL_URL}{path}",
        headers=_headers(),
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


# ============================================================
# ENDPOINTS VERIFICADOS
# ============================================================

def knowledge_ingest(content: str, source: Optional[str] = None, doc_type: Optional[str] = None) -> dict:
    """
    Ingestar un documento en LightRAG.
    
    Args:
        content: El texto a ingestar (REQUERIDO)
        source: Identificador de origen (opcional)
        doc_type: Tipo de documento (opcional)
    
    Returns:
        {"status": "ok", "ingested": true, "content_length": N, "metadata": {...}}
    """
    payload = {"content": content}
    if source is not None:
        payload["source"] = source
    if doc_type is not None:
        payload["doc_type"] = doc_type
    return _post("/v1/knowledge/ingest", payload, timeout=60)


def knowledge_query(query: str) -> dict:
    """
    Consultar el knowledge graph de LightRAG.
    
    Args:
        query: La pregunta o búsqueda (REQUERIDO)
    
    Returns:
        Resultados del knowledge graph
    """
    return _post("/v1/knowledge/query", {"query": query}, timeout=30)


def chat(message: str, thread_id: Optional[str] = None) -> dict:
    """
    Enviar un mensaje al Monstruo vía el kernel.
    
    Args:
        message: El mensaje (REQUERIDO)
        thread_id: ID del hilo de conversación (opcional)
    
    Returns:
        Respuesta del Monstruo
    """
    payload = {"message": message}
    if thread_id is not None:
        payload["thread_id"] = thread_id
    return _post("/v1/chat", payload, timeout=120)


def feedback(run_id: str, action: str) -> dict:
    """
    Enviar feedback sobre una ejecución.
    
    Args:
        run_id: ID de la ejecución (REQUERIDO)
        action: Acción de feedback (REQUERIDO)
    
    Returns:
        Confirmación
    """
    return _post("/v1/feedback", {"run_id": run_id, "action": action}, timeout=15)


def health(auth: bool = False) -> dict:
    """
    Verificar salud del kernel.
    
    Args:
        auth: Si True, usa /health/auth (requiere API key)
    
    Returns:
        Estado del kernel con componentes
    """
    path = "/health/auth" if auth else "/health"
    return _get(path)


def memory_status() -> dict:
    """Estado de las capas de memoria."""
    return _get("/v1/memory/status")


def stats() -> dict:
    """Estadísticas del kernel."""
    return _get("/v1/stats")


# ============================================================
# VERIFICACIÓN RÁPIDA
# ============================================================

if __name__ == "__main__":
    import sys
    print("kernel_client.py — Verificación rápida")
    print(f"  URL: {KERNEL_URL}")
    print(f"  Key: {_get_key()[:10]}...")
    
    try:
        h = health()
        print(f"  Health: {h.get('status')} (v{h.get('version')})")
        print(f"  Componentes: {len(h.get('components', {}))}")
        print("  ✓ Kernel accesible")
    except Exception as e:
        print(f"  ✗ Kernel inaccesible: {e}")
        sys.exit(1)
    
    try:
        ha = health(auth=True)
        print(f"  Auth: {ha.get('status')} (mode={ha.get('mode')})")
        print("  ✓ Autenticación OK")
    except Exception as e:
        print(f"  ✗ Auth falló: {e}")
