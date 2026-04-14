"""
El Monstruo — LLM Client Soberano (Sprint 1)
==============================================
Cliente unificado multi-proveedor que habla directamente con cada API.
NO usa litellm. Usa SDKs nativos + httpx para OpenAI-compatible endpoints.

Proveedores soportados:
  - openai:     SDK nativo (openai==2.31.0)
  - anthropic:  SDK nativo (anthropic==0.94.0)
  - google:     SDK nativo (google-genai==1.72.0)
  - xai:        httpx → OpenAI-compatible (api.x.ai/v1)
  - openrouter: httpx → OpenAI-compatible (openrouter.ai/api/v1)
  - perplexity: httpx → OpenAI-compatible (api.perplexity.ai)

Principio: El Monstruo controla el routing. Los SDKs ejecutan.
Anti-autoboicot: Model IDs verificados 14 abril 2026.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx
import structlog

logger = structlog.get_logger("llm_client")


class LLMClient:
    """
    Cliente unificado que despacha llamadas al proveedor correcto
    basándose en el model_catalog.py.
    """

    def __init__(self) -> None:
        # Lazy-init SDKs — solo se crean cuando se necesitan
        self._openai_client: Any = None
        self._anthropic_client: Any = None
        self._google_client: Any = None
        self._httpx_clients: dict[str, httpx.AsyncClient] = {}

    # ── Lifecycle ──────────────────────────────────────────────────

    async def close(self) -> None:
        """Cerrar todos los clientes HTTP."""
        for client in self._httpx_clients.values():
            await client.aclose()
        self._httpx_clients.clear()
        # SDK clients don't need explicit close in async context

    # ── Public Interface ──────────────────────────────────────────

    async def chat(
        self,
        model_config: dict,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> tuple[str, dict[str, Any]]:
        """
        Enviar chat completion al proveedor correcto.
        
        Args:
            model_config: Entrada del MODELS dict en model_catalog.py
            messages: Lista de mensajes [{role, content}]
            temperature: Temperatura de sampling
            max_tokens: Máximo de tokens de respuesta
            
        Returns:
            (response_text, usage_dict)
        """
        provider = model_config["provider"]
        model_id = model_config["model_id"]
        api_key = os.environ.get(model_config["api_key_env"], "")

        if not api_key:
            raise ValueError(
                f"API key not found: {model_config['api_key_env']}. "
                f"Set it as an environment variable."
            )

        # Determinar max_tokens
        if max_tokens is None:
            if model_config.get("use_max_completion_tokens"):
                max_tokens = model_config.get("max_completion_tokens", 4000)
            else:
                max_tokens = model_config.get("max_tokens", 4096)

        logger.info(
            "llm_call_start",
            provider=provider,
            model_id=model_id,
            message_count=len(messages),
        )

        if provider == "openai":
            return await self._call_openai(model_id, api_key, messages, temperature, max_tokens, model_config)
        elif provider == "anthropic":
            return await self._call_anthropic(model_id, api_key, messages, temperature, max_tokens)
        elif provider == "google":
            return await self._call_google(model_id, api_key, messages, temperature, max_tokens)
        elif provider in ("xai", "openrouter", "perplexity"):
            base_url = model_config.get("base_url", "")
            return await self._call_openai_compatible(
                model_id, api_key, base_url, messages, temperature, max_tokens, provider
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    # ── OpenAI (SDK nativo) ───────────────────────────────────────

    async def _call_openai(
        self,
        model_id: str,
        api_key: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        model_config: dict,
    ) -> tuple[str, dict[str, Any]]:
        """Llamar a OpenAI via SDK nativo."""
        if self._openai_client is None:
            from openai import AsyncOpenAI
            self._openai_client = AsyncOpenAI(api_key=api_key)

        # GPT-5.4 usa max_completion_tokens en vez de max_tokens
        kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
        }
        if model_config.get("use_max_completion_tokens"):
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["max_tokens"] = max_tokens

        response = await self._openai_client.chat.completions.create(**kwargs)

        content = response.choices[0].message.content or ""
        usage = self._extract_usage(response.usage, model_id)

        logger.info("llm_call_ok", provider="openai", model=model_id, tokens=usage.get("total_tokens", 0))
        return content, usage

    # ── Anthropic (SDK nativo) ────────────────────────────────────

    async def _call_anthropic(
        self,
        model_id: str,
        api_key: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> tuple[str, dict[str, Any]]:
        """Llamar a Anthropic via SDK nativo."""
        if self._anthropic_client is None:
            from anthropic import AsyncAnthropic
            self._anthropic_client = AsyncAnthropic(api_key=api_key)

        # Anthropic separa system prompt de messages
        system_prompt = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                user_messages.append(msg)

        # Anthropic requiere al menos un mensaje de usuario
        if not user_messages:
            user_messages = [{"role": "user", "content": "Hola"}]

        kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": user_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await self._anthropic_client.messages.create(**kwargs)

        # Extraer texto de los content blocks
        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            "model_used": model_id,
        }

        logger.info("llm_call_ok", provider="anthropic", model=model_id, tokens=usage["total_tokens"])
        return content, usage

    # ── Google Gemini (SDK nativo google-genai) ───────────────────

    async def _call_google(
        self,
        model_id: str,
        api_key: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> tuple[str, dict[str, Any]]:
        """Llamar a Google Gemini via google-genai SDK."""
        if self._google_client is None:
            from google import genai
            self._google_client = genai.Client(api_key=api_key)

        # Convertir messages OpenAI-format a Gemini format
        system_instruction = ""
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
            elif msg["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})

        # Si no hay contenido, agregar un mensaje mínimo
        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Hola"}]}]

        # Configurar generación
        from google.genai import types
        gen_config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        if system_instruction:
            gen_config.system_instruction = system_instruction

        # google-genai v1.72+ usa generate_content async
        response = await self._google_client.aio.models.generate_content(
            model=model_id,
            contents=contents,
            config=gen_config,
        )

        content = response.text or ""

        # Extraer usage si está disponible
        usage_meta = getattr(response, "usage_metadata", None)
        usage = {
            "prompt_tokens": getattr(usage_meta, "prompt_token_count", 0) if usage_meta else 0,
            "completion_tokens": getattr(usage_meta, "candidates_token_count", 0) if usage_meta else 0,
            "total_tokens": getattr(usage_meta, "total_token_count", 0) if usage_meta else 0,
            "model_used": model_id,
        }

        logger.info("llm_call_ok", provider="google", model=model_id, tokens=usage["total_tokens"])
        return content, usage

    # ── OpenAI-Compatible (xAI, OpenRouter, Perplexity) ──────────

    async def _call_openai_compatible(
        self,
        model_id: str,
        api_key: str,
        base_url: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        provider: str,
    ) -> tuple[str, dict[str, Any]]:
        """Llamar a endpoints OpenAI-compatible via httpx."""
        # Perplexity usa base_url como endpoint directo, no /v1/chat/completions
        if provider == "perplexity":
            url = base_url  # Ya es https://api.perplexity.ai/chat/completions
        else:
            url = f"{base_url}/chat/completions"

        # Reusar o crear httpx client
        if provider not in self._httpx_clients:
            self._httpx_clients[provider] = httpx.AsyncClient(timeout=120.0)

        client = self._httpx_clients[provider]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # OpenRouter requiere headers adicionales
        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://elmonstruo.ai"
            headers["X-Title"] = "El Monstruo"

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        # Extraer respuesta (formato OpenAI estándar)
        choices = data.get("choices", [])
        if not choices:
            raise ValueError(f"No choices in {provider} response: {data}")

        content = choices[0].get("message", {}).get("content", "")

        # Extraer usage
        usage_data = data.get("usage", {})
        usage = {
            "prompt_tokens": usage_data.get("prompt_tokens", 0),
            "completion_tokens": usage_data.get("completion_tokens", 0),
            "total_tokens": usage_data.get("total_tokens", 0),
            "model_used": data.get("model", model_id),
        }

        logger.info("llm_call_ok", provider=provider, model=model_id, tokens=usage["total_tokens"])
        return content, usage

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _extract_usage(usage_obj: Any, model_id: str) -> dict[str, Any]:
        """Extraer usage de un objeto de respuesta OpenAI."""
        if usage_obj is None:
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "model_used": model_id}
        return {
            "prompt_tokens": getattr(usage_obj, "prompt_tokens", 0),
            "completion_tokens": getattr(usage_obj, "completion_tokens", 0),
            "total_tokens": getattr(usage_obj, "total_tokens", 0),
            "model_used": model_id,
        }
