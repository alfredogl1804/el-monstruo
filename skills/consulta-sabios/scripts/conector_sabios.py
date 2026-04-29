#!/usr/bin/env python3.11
"""
conector_sabios.py — Módulo Central de Conexión a los 6 Sabios
=========================================================================
Cada conector verificado en tiempo real contra APIs reales (24 abril 2026).
NO improvisar código de conexión. Cada modelo y endpoint fue validado con
código ejecutado contra las APIs de producción.

Uso:
    from conector_sabios import consultar_sabio, consultar_todos, ping_todos

Sabios (verificado 24 abril 2026 via validate_sabios_realtime.py):
    1. GPT-5.5 Pro       → OpenAI Responses API (/v1/responses)
    2. Claude Opus 4.7   → Anthropic SDK directo (NO OpenRouter)
    3. Gemini 3.1 Pro    → Google GenAI SDK
    4. Grok 4            → xAI API (compatible OpenAI chat/completions)
    5. DeepSeek R1       → OpenRouter (compatible OpenAI chat/completions)
    6. Perplexity Sonar  → Perplexity API (compatible OpenAI chat/completions)

NOTAS CRÍTICAS (descubiertas por validación en tiempo real):
    - GPT-5.x-pro modelos NO funcionan con /v1/chat/completions (404).
      REQUIEREN /v1/responses con output_text.
    - GPT-5.x (sin -pro) SÍ funcionan con chat/completions pero requieren
      max_completion_tokens (NO max_tokens).
    - Claude via Anthropic SDK directo es más confiable que via OpenRouter.
    - sonar-reasoning está DEPRECATED (400). Usar sonar-reasoning-pro.
    - Claude 3.x modelos ya NO existen (404). Solo Claude 4.x+.
"""

import os
import json
import time
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Optional


def _json_serialize(payload: dict) -> bytes:
    """Serializa payload a JSON bytes con soporte Unicode completo.
    aiohttp por defecto usa ensure_ascii=True, lo cual corrompe
    caracteres como Ú, á, ñ. Esta función lo resuelve."""
    return json.dumps(payload, ensure_ascii=False).encode('utf-8')

# ═══════════════════════════════════════════════════════════════════
# CONFIGURACIÓN — Verificada contra APIs reales 24 abril 2026
# ═══════════════════════════════════════════════════════════════════

SABIOS = {
    "gpt55": {
        "nombre": "GPT-5.5 Pro",
        "modelo": "gpt-5.5-pro",
        "modelo_resuelto": "gpt-5.5-pro-2026-04-23",  # Verificado via API
        "proveedor": "openai_responses",  # REQUIERE Responses API, NO chat/completions
        "contexto_max": 1_050_000,
        "grupo": "completo",  # Recibe documentos completos
        "timeout": 300,
        "notas": "Flagship OpenAI. Usa /v1/responses, NO /v1/chat/completions.",
    },
    "claude": {
        "nombre": "Claude Opus 4.7",
        "modelo": "claude-opus-4-7",
        "proveedor": "anthropic_directo",  # SDK directo, más confiable que OpenRouter
        "contexto_max": 1_000_000,
        "grupo": "completo",
        "timeout": 300,
        "notas": "Flagship Anthropic. Usar SDK directo con ANTHROPIC_API_KEY.",
    },
    "gemini": {
        "nombre": "Gemini 3.1 Pro Preview",
        "modelo": "gemini-3.1-pro-preview",
        "proveedor": "google_genai",
        "contexto_max": 1_000_000,
        "grupo": "completo",
        "timeout": 300,
        "notas": "Flagship Google. Usar google-genai SDK.",
    },
    "grok": {
        "nombre": "Grok 4",
        "modelo": "grok-4-0709",
        "proveedor": "xai",
        "contexto_max": 2_000_000,
        "grupo": "completo",
        "timeout": 300,
        "notas": "Flagship xAI. API compatible OpenAI en api.x.ai.",
    },
    "deepseek": {
        "nombre": "DeepSeek R1",
        "modelo": "deepseek/deepseek-r1",
        "proveedor": "openrouter",
        "contexto_max": 128_000,
        "grupo": "condensado",  # Necesita resumen ejecutivo
        "timeout": 300,
        "notas": "Reasoning model. Via OpenRouter.",
    },
    "perplexity": {
        "nombre": "Perplexity Sonar Reasoning Pro",
        "modelo": "sonar-reasoning-pro",
        "proveedor": "perplexity",
        "contexto_max": 128_000,
        "grupo": "condensado",
        "timeout": 120,
        "notas": "Grounded search. sonar-reasoning DEPRECATED, usar sonar-reasoning-pro.",
    },
}

# Alias de compatibilidad: "gpt54" → "gpt55" (el sabio OpenAI se actualizó)
SABIOS["gpt54"] = SABIOS["gpt55"]

# ═══════════════════════════════════════════════════════════════════
# CREDENCIALES — Mapeadas directamente a variables de entorno
# ═══════════════════════════════════════════════════════════════════

_CREDS_CACHE = {}

_CREDS_MAP = {
    "openai_responses": "OPENAI_API_KEY",
    "anthropic_directo": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "google_genai": "GEMINI_API_KEY",
    "xai": "XAI_API_KEY",
    "perplexity": "SONAR_API_KEY",
}


def _get_cred(proveedor: str) -> str:
    """Obtiene la credencial de UN proveedor específico. Cacheada tras primer acceso."""
    if proveedor in _CREDS_CACHE:
        return _CREDS_CACHE[proveedor]
    env_var = _CREDS_MAP.get(proveedor)
    if not env_var:
        raise ValueError(f"Proveedor desconocido: {proveedor}")
    val = os.environ.get(env_var, "")
    if not val:
        raise EnvironmentError(f"Variable de entorno faltante: {env_var} (proveedor: {proveedor})")
    _CREDS_CACHE[proveedor] = val
    return val


def _get_creds():
    """Obtiene TODAS las credenciales. Usado por ping y pre-vuelo."""
    creds = {}
    faltantes = []
    for prov, env_var in _CREDS_MAP.items():
        val = os.environ.get(env_var, "")
        if val:
            creds[env_var] = val
            _CREDS_CACHE[prov] = val
        else:
            faltantes.append(env_var)
    if faltantes:
        raise EnvironmentError(f"Variables de entorno faltantes: {', '.join(faltantes)}")
    return creds


def _classify_error(error: Exception) -> dict:
    """Clasifica un error en campos normalizados para telemetría."""
    err_str = str(error)
    err_lower = err_str.lower()
    result = {
        "error_msg": err_str[:300],
        "error_type": "unknown",
        "http_status": None,
        "is_timeout": False,
        "is_rate_limit": False,
        "is_auth": False,
        "is_context_overflow": False,
        "retryable": True,
    }
    import re as _re
    status_match = _re.search(r'HTTP (\d{3})', err_str)
    if status_match:
        result["http_status"] = int(status_match.group(1))

    if "timeout" in err_lower or "timed out" in err_lower:
        result["error_type"] = "timeout"
        result["is_timeout"] = True
    elif "429" in err_str or "rate limit" in err_lower:
        result["error_type"] = "rate_limit"
        result["is_rate_limit"] = True
    elif "401" in err_str or "unauthorized" in err_lower:
        result["error_type"] = "auth_error"
        result["is_auth"] = True
        result["retryable"] = False
    elif "403" in err_str or "forbidden" in err_lower:
        result["error_type"] = "forbidden"
        result["retryable"] = False
    elif "context" in err_lower or ("token" in err_lower and "length" in err_lower):
        result["error_type"] = "context_overflow"
        result["is_context_overflow"] = True
        result["retryable"] = False
    elif "500" in err_str or "502" in err_str or "503" in err_str:
        result["error_type"] = "server_error"
    return result


# ═══════════════════════════════════════════════════════════════════
# CONECTORES INDIVIDUALES — Verificados contra APIs reales
# ═══════════════════════════════════════════════════════════════════

async def _llamar_openai_responses(prompt: str, system: str, modelo: str, timeout: int) -> str:
    """
    Conector para GPT-5.5 Pro vía OpenAI Responses API (/v1/responses).

    CRÍTICO: Los modelos gpt-5.x-pro NO funcionan con /v1/chat/completions.
    Requieren /v1/responses. Verificado 24 abril 2026.

    La respuesta viene en resp.output_text (no en choices[0].message.content).
    """
    api_key = _get_cred("openai_responses")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # CRÍTICO: gpt-5.5-pro NO soporta temperature (verificado 24 abril 2026)
    payload = {
        "model": modelo,
        "input": f"{system}\n\n---\n\n{prompt}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/responses",
            headers=headers,
            data=_json_serialize(payload),
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"OpenAI Responses HTTP {resp.status}: {body[:500]}")
            data = await resp.json()
            # Responses API: output_text contiene la respuesta directa
            output_text = data.get("output_text", "")
            if output_text:
                return output_text
            # Fallback: buscar en output array
            for item in data.get("output", []):
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            return content.get("text", "")
            raise RuntimeError(f"OpenAI Responses: no output_text found in response")


async def _llamar_anthropic_directo(prompt: str, system: str, modelo: str, timeout: int) -> str:
    """
    Conector para Claude Opus 4.7 vía Anthropic SDK directo.

    CRÍTICO: Usar API directa de Anthropic, NO OpenRouter, para máxima
    confiabilidad. Verificado 24 abril 2026.

    Usa /v1/messages con max_tokens (Anthropic sí usa max_tokens, no max_completion_tokens).
    """
    api_key = _get_cred("anthropic_directo")
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    # CRÍTICO: claude-opus-4-7 NO soporta temperature (deprecated, verificado 24 abril 2026)
    payload = {
        "model": modelo,
        "max_tokens": 4096,
        "system": system,
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            data=_json_serialize(payload),
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"Anthropic HTTP {resp.status}: {body[:500]}")
            data = await resp.json()
            # Anthropic Messages API: content[0].text
            content = data.get("content", [])
            if content and content[0].get("type") == "text":
                return content[0]["text"]
            raise RuntimeError(f"Anthropic: unexpected response format: {json.dumps(data)[:300]}")


async def _llamar_openrouter(prompt: str, system: str, modelo: str, timeout: int) -> str:
    """Conector para DeepSeek R1 vía OpenRouter (compatible OpenAI chat/completions)."""
    api_key = _get_cred("openrouter")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://manus.im",
        "X-Title": "Consulta Sabios - El Monstruo",
    }
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=_json_serialize(payload),
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"OpenRouter HTTP {resp.status}: {body[:500]}")
            data = await resp.json()
            return data["choices"][0]["message"]["content"]


async def _llamar_google_genai(prompt: str, system: str, modelo: str, timeout: int) -> str:
    """Conector para Gemini 3.1 Pro vía Google GenAI SDK con timeout explícito."""
    api_key = _get_cred("google_genai")
    from google import genai
    client = genai.Client(api_key=api_key)

    loop = asyncio.get_event_loop()
    def _call():
        response = client.models.generate_content(
            model=modelo,
            contents=f"{system}\n\n---\n\n{prompt}",
            config=genai.types.GenerateContentConfig(
                temperature=0.7,
            ),
        )
        return response.text

    return await asyncio.wait_for(
        loop.run_in_executor(None, _call),
        timeout=timeout
    )


async def _llamar_xai(prompt: str, system: str, modelo: str, timeout: int) -> str:
    """Conector para Grok 4 vía API de xAI (compatible OpenAI chat/completions)."""
    api_key = _get_cred("xai")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            data=_json_serialize(payload),
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"xAI HTTP {resp.status}: {body[:500]}")
            data = await resp.json()
            return data["choices"][0]["message"]["content"]


async def _llamar_perplexity(prompt: str, system: str, modelo: str, timeout: int) -> str:
    """Conector para Perplexity Sonar Reasoning Pro vía REST directo."""
    api_key = _get_cred("perplexity")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            data=_json_serialize(payload),
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"Perplexity HTTP {resp.status}: {body[:500]}")
            data = await resp.json()
            return data["choices"][0]["message"]["content"]


# ═══════════════════════════════════════════════════════════════════
# DISPATCHER — Mapea proveedor a conector
# ═══════════════════════════════════════════════════════════════════

_DISPATCH = {
    "openai_responses": _llamar_openai_responses,
    "anthropic_directo": _llamar_anthropic_directo,
    "openrouter": _llamar_openrouter,
    "google_genai": _llamar_google_genai,
    "xai": _llamar_xai,
    "perplexity": _llamar_perplexity,
}


# ═══════════════════════════════════════════════════════════════════
# FUNCIONES PÚBLICAS — Lo único que el agente debe usar
# ═══════════════════════════════════════════════════════════════════

async def consultar_sabio(
    sabio_id: str,
    prompt: str,
    system: str = "Eres un experto analista y estratega de primer nivel mundial.",
    reintentos: int = 3,
    guardar_en: Optional[str] = None,
) -> dict:
    """
    Consulta a UN sabio específico con retry y exponential backoff.

    Args:
        sabio_id: Clave del sabio ('gpt55', 'gpt54', 'claude', 'gemini', 'grok', 'deepseek', 'perplexity')
        prompt: El prompt completo a enviar
        system: El system prompt (opcional)
        reintentos: Número máximo de reintentos (default: 3)
        guardar_en: Ruta de directorio donde guardar la respuesta (opcional)

    Returns:
        dict con: sabio, modelo, respuesta, tiempo_seg, exito, error
    """
    if sabio_id not in SABIOS:
        return {
            "sabio": sabio_id,
            "modelo": "desconocido",
            "respuesta": "",
            "tiempo_seg": 0,
            "exito": False,
            "error": f"Sabio '{sabio_id}' no existe. Válidos: {list(set(SABIOS.keys()) - {'gpt54'})}",
        }

    config = SABIOS[sabio_id]
    fn = _DISPATCH[config["proveedor"]]
    inicio = time.time()

    for intento in range(1, reintentos + 1):
        try:
            respuesta = await fn(
                prompt=prompt,
                system=system,
                modelo=config["modelo"],
                timeout=config["timeout"],
            )
            elapsed = round(time.time() - inicio, 1)

            resultado = {
                "sabio": config["nombre"],
                "sabio_id": sabio_id,
                "modelo": config["modelo"],
                "respuesta": respuesta,
                "tiempo_seg": elapsed,
                "exito": True,
                "error": None,
                "intento": intento,
                "timestamp": datetime.now().isoformat(),
            }

            if guardar_en:
                _guardar_respuesta(guardar_en, sabio_id, resultado)

            return resultado

        except Exception as e:
            err_info = _classify_error(e)
            if intento < reintentos and err_info["retryable"]:
                wait = 2 ** intento
                await asyncio.sleep(wait)
            elif intento < reintentos and not err_info["retryable"]:
                elapsed = round(time.time() - inicio, 1)
                return {
                    "sabio": config["nombre"],
                    "sabio_id": sabio_id,
                    "modelo": config["modelo"],
                    "respuesta": "",
                    "tiempo_seg": elapsed,
                    "exito": False,
                    "error": f"Error no reintentable: {err_info['error_msg']}",
                    "error_info": err_info,
                    "intento": intento,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                elapsed = round(time.time() - inicio, 1)
                return {
                    "sabio": config["nombre"],
                    "sabio_id": sabio_id,
                    "modelo": config["modelo"],
                    "respuesta": "",
                    "tiempo_seg": elapsed,
                    "exito": False,
                    "error": f"Falló tras {reintentos} intentos: {err_info['error_msg']}",
                    "error_info": err_info,
                    "intento": intento,
                    "timestamp": datetime.now().isoformat(),
                }


async def consultar_todos(
    prompt_completo: str,
    prompt_condensado: Optional[str] = None,
    system: str = "Eres un experto analista y estratega de primer nivel mundial.",
    sabios: Optional[list] = None,
    guardar_en: Optional[str] = None,
) -> list:
    """
    Consulta a TODOS los sabios en paralelo.

    Args:
        prompt_completo: Prompt con contexto completo (para sabios de 1M+)
        prompt_condensado: Prompt con resumen ejecutivo (para DeepSeek/Perplexity).
                          Si no se provee, se usa prompt_completo para todos.
        system: System prompt
        sabios: Lista de sabio_ids a consultar (default: los 6 únicos, sin alias)
        guardar_en: Directorio donde guardar respuestas individuales

    Returns:
        Lista de dicts con resultados de cada sabio
    """
    if sabios is None:
        # Los 6 sabios únicos (excluir alias gpt54)
        sabios = ["gpt55", "claude", "gemini", "grok", "deepseek", "perplexity"]

    tareas = []
    for sid in sabios:
        if sid not in SABIOS:
            continue
        config = SABIOS[sid]
        if config["grupo"] == "condensado" and prompt_condensado:
            prompt = prompt_condensado
        else:
            prompt = prompt_completo
        tareas.append(consultar_sabio(sid, prompt, system, guardar_en=guardar_en))

    resultados = await asyncio.gather(*tareas, return_exceptions=True)

    finales = []
    for i, r in enumerate(resultados):
        if isinstance(r, Exception):
            finales.append({
                "sabio": sabios[i],
                "modelo": "error",
                "respuesta": "",
                "tiempo_seg": 0,
                "exito": False,
                "error": str(r),
            })
        else:
            finales.append(r)

    return finales


async def ping_todos() -> list:
    """
    Ping rápido a los 6 sabios con un prompt mínimo.
    Valida que las credenciales y APIs estén vivas.
    Retorna lista de resultados con exito=True/False.
    """
    ping_prompt = "Responde ÚNICAMENTE con la palabra 'OK'. Nada más."
    ping_system = "Responde con una sola palabra."

    # Los 6 sabios únicos (sin alias)
    sabios_unicos = ["gpt55", "claude", "gemini", "grok", "deepseek", "perplexity"]
    tareas = []
    for sid in sabios_unicos:
        tareas.append(consultar_sabio(sid, ping_prompt, ping_system, reintentos=1))

    return await asyncio.gather(*tareas)


# ═══════════════════════════════════════════════════════════════════
# UTILIDADES INTERNAS
# ═══════════════════════════════════════════════════════════════════

def _guardar_respuesta(directorio: str, sabio_id: str, resultado: dict):
    """Guarda la respuesta de un sabio inmediatamente al disco."""
    path = Path(directorio)
    path.mkdir(parents=True, exist_ok=True)

    archivo_txt = path / f"resp_{sabio_id}.md"
    with open(archivo_txt, "w", encoding="utf-8") as f:
        f.write(f"# Respuesta de {resultado['sabio']}\n")
        f.write(f"**Modelo:** {resultado['modelo']}\n")
        f.write(f"**Tiempo:** {resultado['tiempo_seg']}s\n")
        f.write(f"**Timestamp:** {resultado['timestamp']}\n")
        f.write(f"**Éxito:** {resultado['exito']}\n\n")
        f.write("---\n\n")
        f.write(resultado["respuesta"])

    archivo_json = path / f"resp_{sabio_id}.json"
    meta = {k: v for k, v in resultado.items() if k != "respuesta"}
    meta["archivo_respuesta"] = str(archivo_txt)
    with open(archivo_json, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def resumen_resultados(resultados: list) -> str:
    """Genera un resumen legible de los resultados de una consulta."""
    lines = ["# Resumen de Consulta a los Sabios", ""]
    exitosos = sum(1 for r in resultados if r.get("exito"))
    total = len(resultados)
    lines.append(f"**Resultado:** {exitosos}/{total} sabios respondieron exitosamente")

    if exitosos < 3:
        lines.append("ALTO: Menos de 3 sabios respondieron. Protocolo semilla v7.3 requiere mínimo 3.")

    lines.append("")
    lines.append("| Sabio | Modelo | Tiempo | Estado |")
    lines.append("|-------|--------|--------|--------|")
    for r in resultados:
        estado = "OK" if r.get("exito") else f"FAIL: {r.get('error', 'Error desconocido')[:50]}"
        lines.append(f"| {r.get('sabio', '?')} | {r.get('modelo', '?')} | {r.get('tiempo_seg', 0)}s | {estado} |")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# EJECUCIÓN DIRECTA — Para pruebas rápidas
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    async def main():
        if len(sys.argv) > 1 and sys.argv[1] == "ping":
            print("Ejecutando ping a los 6 sabios...\n")
            resultados = await ping_todos()
            print(resumen_resultados(resultados))
        else:
            print("Uso: python3.11 conector_sabios.py ping")
            print("  ping  — Verifica conexión con los 6 sabios")

    asyncio.run(main())
