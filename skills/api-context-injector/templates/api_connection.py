#!/usr/bin/env python3.11
"""
api_connection.py — Plantilla estándar para conectar con cualquier API del ecosistema.

Uso:
    from templates.api_connection import get_llm_client, call_llm, get_media_client

Ejemplo:
    client = get_llm_client("openai")
    response = call_llm("openai", "Hola, ¿cómo estás?")
"""

import json
import os
from typing import Optional

import requests

# ============================================================
# LLM Clients
# ============================================================


def get_llm_client(provider: str):
    """
    Retorna un cliente configurado para el proveedor LLM.

    Proveedores soportados:
        openai, anthropic, google, xai, deepseek, perplexity
    """
    if provider == "openai":
        from openai import OpenAI

        return OpenAI()  # Usa OPENAI_API_KEY automáticamente

    elif provider == "anthropic":
        from anthropic import Anthropic

        return Anthropic()  # Usa ANTHROPIC_API_KEY automáticamente

    elif provider == "google":
        from google import genai

        return genai.Client()  # Usa GEMINI_API_KEY automáticamente

    elif provider == "xai":
        from openai import OpenAI

        return OpenAI(api_key=os.environ["XAI_API_KEY"], base_url="https://api.x.ai/v1")

    elif provider == "deepseek":
        from openai import OpenAI

        return OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")

    elif provider == "perplexity":
        # Perplexity NO usa SDK — retorna None, usar call_llm directamente
        return None

    else:
        raise ValueError(f"Proveedor desconocido: {provider}")


def call_llm(provider: str, prompt: str, system: str = "", max_tokens: int = 4096) -> str:
    """
    Llama a un LLM y retorna la respuesta como texto.

    Args:
        provider: openai, anthropic, google, xai, deepseek, perplexity
        prompt: El mensaje del usuario
        system: Mensaje de sistema (opcional)
        max_tokens: Máximo de tokens de respuesta

    Returns:
        Texto de la respuesta
    """
    MODEL_IDS = {
        "openai": "gpt-5.4",
        "anthropic": "anthropic/claude-sonnet-4-6",  # Vía OpenRouter (Opus tiene timeouts)
        "google": "gemini-3.1-pro-preview",
        "xai": "grok-4.20-0309-reasoning",
        "deepseek": "deepseek/deepseek-r1",
        "perplexity": "sonar-reasoning-pro",
    }

    model = MODEL_IDS.get(provider)
    if not model:
        raise ValueError(f"Proveedor desconocido: {provider}")

    # --- Perplexity (SOLO requests) ---
    if provider == "perplexity":
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['SONAR_API_KEY']}"},
            json={"model": model, "messages": messages, "max_tokens": max_tokens},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    # --- Google Gemini ---
    if provider == "google":
        client = get_llm_client("google")
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = client.models.generate_content(model=model, contents=full_prompt)
        return response.text

    # --- Anthropic ---
    if provider == "anthropic":
        client = get_llm_client("anthropic")
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        return response.content[0].text

    # --- OpenAI-compatible (openai, xai, deepseek) ---
    client = get_llm_client(provider)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    kwargs = {"model": model, "messages": messages}
    if provider == "openai":
        kwargs["max_completion_tokens"] = max_tokens  # NUNCA max_tokens para GPT-5.4
    else:
        kwargs["max_tokens"] = max_tokens

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


# ============================================================
# Media Clients
# ============================================================


def call_heygen(payload: dict) -> dict:
    """Genera un video con HeyGen."""
    response = requests.post(
        "https://api.heygen.com/v2/video/generate",
        headers={"X-Api-Key": os.environ["HEYGEN_API_KEY"], "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def get_heygen_status(video_id: str) -> dict:
    """Obtiene el estado de un video de HeyGen."""
    response = requests.get(
        f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
        headers={"X-Api-Key": os.environ["HEYGEN_API_KEY"]},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def call_elevenlabs_tts(
    text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM", model_id: str = "eleven_multilingual_v2"
) -> bytes:
    """Genera audio con ElevenLabs."""
    from elevenlabs import ElevenLabs

    client = ElevenLabs()
    audio = client.text_to_speech.convert(text=text, voice_id=voice_id, model_id=model_id)
    return audio


# ============================================================
# MCP Helpers
# ============================================================


def call_mcp(server: str, tool: str, input_json: dict) -> str:
    """Ejecuta un comando MCP y retorna el resultado."""
    import subprocess

    cmd = ["manus-mcp-cli", "tool", "call", tool, "--server", server, "--input", json.dumps(input_json)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result.stdout


# ============================================================
# Credential Lookup
# ============================================================


def get_notion_credential(service_name: str) -> Optional[str]:
    """
    Busca una credencial en la DB de Notion.
    ADVERTENCIA: Solo usar cuando sea absolutamente necesario.
    Preferir env vars del sandbox.
    """
    result = call_mcp(
        "notion",
        "notion-search",
        {
            "query": service_name,
            "data_source_url": "collection://d94369d5-5dc3-437e-b483-fa86a5e98b74",
            "page_size": 1,
            "filters": {},
        },
    )

    try:
        data = json.loads(result)
        if data.get("results"):
            page_id = data["results"][0]["id"]
            page_result = call_mcp("notion", "notion-fetch", {"id": page_id})
            page_data = json.loads(page_result)
            # Extraer API Key del texto
            import re

            text = page_data.get("text", "")
            match = re.search(r'"API Key":"([^"]+)"', text)
            if match:
                return match.group(1)
    except Exception:
        pass

    return None
