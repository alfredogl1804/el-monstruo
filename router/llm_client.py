"""
El Monstruo — LLM Client Soberano (Sprint 2)
==============================================
Cliente unificado multi-proveedor que habla directamente con cada API.
NO usa litellm. Usa SDKs nativos + httpx para OpenAI-compatible endpoints.

Sprint 2: Soporte nativo de tool/function calling con respuesta normalizada.
Estrategia validada por Consejo de 6 Sabios (2026-04-16): Opción E.

Proveedores soportados:
  - openai:     SDK nativo (openai==2.30.0) — tools nativas
  - anthropic:  SDK nativo (anthropic==0.94.1) — tools nativas
  - google:     SDK nativo (google-genai==1.73.0) — tools nativas
  - xai:        httpx → OpenAI-compatible (api.x.ai/v1) — tools nativas
  - openrouter: httpx → OpenAI-compatible (openrouter.ai/api/v1) — tools nativas
  - perplexity: httpx → OpenAI-compatible (api.perplexity.ai) — NO tools

Principio: El Monstruo controla el routing. Los SDKs ejecutan.
Anti-autoboicot: SDK versions verified 16 abril 2026.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx
import structlog

logger = structlog.get_logger("llm_client")


# ── Normalized Response Contract (Sabios consensus) ─────────────────


@dataclass
class ToolCall:
    """Normalized tool call — provider-agnostic."""

    id: str
    name: str
    arguments: dict[str, Any]
    # Gemini 3.x thought signatures: MANDATORY for multi-turn function calling.
    # The thought_signature from the response Part must be echoed back in the
    # next turn's Part to maintain the model's reasoning context.
    # See: https://ai.google.dev/gemini-api/docs/function-calling
    thought_signature: Optional[bytes] = None

    def to_dict(self) -> dict[str, Any]:
        d = {"id": self.id, "name": self.name, "arguments": self.arguments}
        if self.thought_signature is not None:
            # Serialize bytes as base64 for JSON compatibility
            import base64

            d["thought_signature"] = base64.b64encode(self.thought_signature).decode("ascii")
        return d


@dataclass
class LLMResponse:
    """
    Normalized LLM response — the single contract between LLMClient and the graph.

    If tool_calls is non-empty, the LLM wants to use tools.
    If content is non-empty, the LLM is responding with text.
    Both can be present (e.g., text + tool calls).
    """

    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str = ""  # "stop", "tool_calls", "length", "end_turn"
    usage: dict[str, Any] = field(default_factory=dict)
    provider: str = ""
    model: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "provider": self.provider,
            "model": self.model,
        }


# ── Tool Spec (for sending to providers) ────────────────────────────


@dataclass
class ToolSpec:
    """Tool specification — provider-agnostic."""

    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema
    risk: str = "low"  # low, medium, high

    def to_openai_format(self) -> dict:
        """Convert to OpenAI/xAI/OpenRouter tools format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_anthropic_format(self) -> dict:
        """Convert to Anthropic tools format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }

    def to_gemini_declarations(self):
        """Convert to Google Gemini FunctionDeclaration."""
        from google.genai import types

        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=self._schema_to_gemini(self.parameters),
        )

    @staticmethod
    def _schema_to_gemini(schema: dict) -> dict:
        """Convert JSON Schema to Gemini-compatible schema dict.
        google-genai 1.73+ accepts raw dicts for parameters."""
        return schema


class LLMClient:
    """
    Cliente unificado que despacha llamadas al proveedor correcto.
    Sprint 2: Soporta tool calling nativo con respuesta normalizada.
    """

    def __init__(self) -> None:
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

    # ── Public Interface ──────────────────────────────────────────

    async def chat(
        self,
        model_config: dict,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[list[ToolSpec]] = None,
        tool_choice: str = "auto",
    ) -> tuple[str, dict[str, Any]]:
        """
        Backward-compatible chat interface.
        Returns (response_text, usage_dict) — same as Sprint 1.

        For tool calling, use chat_with_tools() instead.
        """
        response = await self.chat_with_tools(
            model_config=model_config,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response.content, response.usage

    async def chat_with_tools(
        self,
        model_config: dict,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[list[ToolSpec]] = None,
        tool_choice: str = "auto",
    ) -> LLMResponse:
        """
        Sprint 2: Chat with native tool calling support.
        Returns normalized LLMResponse with tool_calls if the model wants to use tools.

        Args:
            model_config: Entry from MODEL_CATALOG
            messages: List of messages [{role, content}] — also accepts tool results
            temperature: Sampling temperature
            max_tokens: Max response tokens
            tools: List of ToolSpec to make available to the model
            tool_choice: "auto", "none", or "required"
        """
        provider = model_config["provider"]
        model_id = model_config["model_id"]
        api_key = os.environ.get(model_config["api_key_env"], "")

        if not api_key:
            raise ValueError(f"API key not found: {model_config['api_key_env']}. Set it as an environment variable.")

        if max_tokens is None:
            if model_config.get("use_max_completion_tokens"):
                max_tokens = model_config.get("max_completion_tokens", 4000)
            else:
                max_tokens = model_config.get("max_tokens", 4096)

        # Perplexity doesn't support tools — strip them
        effective_tools = tools
        if provider == "perplexity" and tools:
            logger.info("tools_stripped_perplexity", model=model_id)
            effective_tools = None

        logger.info(
            "llm_call_start",
            provider=provider,
            model_id=model_id,
            message_count=len(messages),
            tools_count=len(effective_tools) if effective_tools else 0,
        )

        if provider == "openai":
            return await self._call_openai(
                model_id,
                api_key,
                messages,
                temperature,
                max_tokens,
                model_config,
                effective_tools,
                tool_choice,
            )
        elif provider == "anthropic":
            return await self._call_anthropic(
                model_id,
                api_key,
                messages,
                temperature,
                max_tokens,
                effective_tools,
                tool_choice,
            )
        elif provider == "google":
            return await self._call_google(
                model_id,
                api_key,
                messages,
                temperature,
                max_tokens,
                effective_tools,
                tool_choice,
            )
        elif provider in ("xai", "openrouter", "perplexity"):
            base_url = model_config.get("base_url", "")
            return await self._call_openai_compatible(
                model_id,
                api_key,
                base_url,
                messages,
                temperature,
                max_tokens,
                provider,
                effective_tools,
                tool_choice,
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    # ── OpenAI (SDK nativo) ───────────────────────────────────────

    async def _call_openai(
        self,
        model_id: str,
        api_key: str,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        model_config: dict,
        tools: Optional[list[ToolSpec]] = None,
        tool_choice: str = "auto",
    ) -> LLMResponse:
        if self._openai_client is None:
            from openai import AsyncOpenAI

            self._openai_client = AsyncOpenAI(api_key=api_key)

        kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
        }
        if model_config.get("use_max_completion_tokens"):
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["max_tokens"] = max_tokens

        if tools:
            kwargs["tools"] = [t.to_openai_format() for t in tools]
            kwargs["tool_choice"] = tool_choice

        response = await self._openai_client.chat.completions.create(**kwargs)

        msg = response.choices[0].message
        content = msg.content or ""
        finish_reason = response.choices[0].finish_reason or ""

        # Extract tool calls
        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                try:
                    args = (
                        json.loads(tc.function.arguments)
                        if isinstance(tc.function.arguments, str)
                        else tc.function.arguments
                    )
                except json.JSONDecodeError:
                    args = {"raw": tc.function.arguments}
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=args,
                    )
                )

        usage = self._extract_usage(response.usage, model_id)
        logger.info(
            "llm_call_ok",
            provider="openai",
            model=model_id,
            tokens=usage.get("total_tokens", 0),
            tool_calls=len(tool_calls),
        )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
            provider="openai",
            model=model_id,
        )

    # ── Anthropic (SDK nativo) ────────────────────────────────────

    async def _call_anthropic(
        self,
        model_id: str,
        api_key: str,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        tools: Optional[list[ToolSpec]] = None,
        tool_choice: str = "auto",
    ) -> LLMResponse:
        if self._anthropic_client is None:
            from anthropic import AsyncAnthropic

            self._anthropic_client = AsyncAnthropic(api_key=api_key)

        # Anthropic separates system prompt from messages
        system_prompt = ""
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content", "")
            elif msg.get("role") == "tool":
                # Convert tool result to Anthropic format
                user_messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": msg.get("tool_call_id", ""),
                                "content": msg.get("content", ""),
                            }
                        ],
                    }
                )
            elif msg.get("role") == "assistant" and msg.get("tool_calls"):
                # Convert OpenAI-format tool_calls to Anthropic tool_use content blocks.
                # engine.py reconstructs assistant messages in OpenAI format:
                #   {"role": "assistant", "content": None, "tool_calls": [...]}
                # Anthropic requires:
                #   {"role": "assistant", "content": [{"type": "tool_use", ...}]}
                import json as _json_a

                content_blocks = []
                # Include text content if present
                text_content = msg.get("content")
                if text_content and isinstance(text_content, str) and text_content.strip():
                    content_blocks.append({"type": "text", "text": text_content})
                for tc in msg["tool_calls"]:
                    fn = tc.get("function", {})
                    fn_args_raw = fn.get("arguments", "{}")
                    if isinstance(fn_args_raw, str):
                        try:
                            fn_args = _json_a.loads(fn_args_raw)
                        except Exception:
                            fn_args = {"raw": fn_args_raw}
                    else:
                        fn_args = fn_args_raw if isinstance(fn_args_raw, dict) else {}
                    content_blocks.append(
                        {
                            "type": "tool_use",
                            "id": tc.get("id", ""),
                            "name": fn.get("name", "tool"),
                            "input": fn_args,
                        }
                    )
                user_messages.append({"role": "assistant", "content": content_blocks})
            elif msg.get("role") == "assistant" and isinstance(msg.get("content"), list):
                # Pass through assistant messages with tool_use blocks (already Anthropic format)
                user_messages.append(msg)
            else:
                user_messages.append({"role": msg.get("role", "user"), "content": msg.get("content") or ""})

        if not user_messages:
            user_messages = [{"role": "user", "content": "Hola"}]

        # claude-opus-4-7 breaking API changes (Anthropic migration guide, Apr 16 2026):
        # 1. temperature / top_p / top_k removed — sending any value returns HTTP 400
        # 2. thinking: {type: "enabled"} removed — use {type: "adaptive"} instead
        # 3. output_config.effort replaces budget_tokens for thinking depth control
        # Source: https://platform.claude.com/docs/en/about-claude/models/migration-guide
        _is_opus_47 = "opus-4-7" in model_id or "opus-4.7" in model_id

        kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": user_messages,
            "max_tokens": max_tokens,
        }
        # Only send temperature for models that support it (not opus-4-7)
        if not _is_opus_47:
            kwargs["temperature"] = temperature
        # Enable adaptive thinking for opus-4-7 with high effort (best for agentic tasks)
        if _is_opus_47:
            kwargs["thinking"] = {"type": "adaptive", "display": "summarized"}
            kwargs["output_config"] = {"effort": "high"}

        if system_prompt:
            kwargs["system"] = system_prompt

        if tools:
            kwargs["tools"] = [t.to_anthropic_format() for t in tools]
            # Anthropic tool_choice format
            if tool_choice == "auto":
                kwargs["tool_choice"] = {"type": "auto"}
            elif tool_choice == "none":
                pass  # Don't send tool_choice
            elif tool_choice == "required":
                kwargs["tool_choice"] = {"type": "any"}

        response = await self._anthropic_client.messages.create(**kwargs)

        # Extract content and tool calls from content blocks
        content = ""
        tool_calls = []
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text
            elif hasattr(block, "type") and block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input if isinstance(block.input, dict) else {},
                    )
                )

        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            "model_used": model_id,
        }

        # Normalize stop_reason
        finish_reason = response.stop_reason or ""
        if finish_reason == "tool_use":
            finish_reason = "tool_calls"
        elif finish_reason == "end_turn":
            finish_reason = "stop"

        logger.info(
            "llm_call_ok",
            provider="anthropic",
            model=model_id,
            tokens=usage["total_tokens"],
            tool_calls=len(tool_calls),
        )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
            provider="anthropic",
            model=model_id,
        )

    # ── Google Gemini (SDK nativo google-genai) ───────────────────

    async def _call_google(
        self,
        model_id: str,
        api_key: str,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        tools: Optional[list[ToolSpec]] = None,
        tool_choice: str = "auto",
    ) -> LLMResponse:
        if self._google_client is None:
            from google import genai

            self._google_client = genai.Client(api_key=api_key)

        # ── Convert OpenAI-format messages to Gemini contents ──────
        # CRITICAL FIX (2026-04-16): Gemini API rejects Part with text=None
        # or Part() with no data fields. This causes:
        #   400 INVALID_ARGUMENT: contents[N].parts[0].data: required oneof
        #   field 'data' must have one initialized field
        # Root cause: conversation history from memory can contain messages
        # with content=None (e.g., assistant msgs that were tool-call-only).
        # msg.get("content", "") returns None when key exists with None value.
        # Fix: use `msg.get("content") or ""` pattern everywhere, and skip
        # any message that would produce a Part with no valid data.

        import json as _json_g

        from google.genai import types as _gtypes

        system_instruction = ""
        contents = []
        for msg in messages:
            role = msg.get("role", "user")

            if role == "system":
                system_instruction = msg.get("content") or ""

            elif role == "user":
                # Sanitize: ensure content is never None
                text = msg.get("content") or ""
                if not isinstance(text, str):
                    text = str(text)
                # Skip user messages with empty content to avoid invalid Part
                if text.strip():
                    contents.append({"role": "user", "parts": [{"text": text}]})
                else:
                    logger.debug("gemini_skip_empty_user_msg", msg_keys=list(msg.keys()))

            elif role == "assistant":
                # If assistant has tool_calls, convert to function_call Parts
                tool_calls = msg.get("tool_calls", [])
                if tool_calls:
                    parts = []
                    for tc in tool_calls:
                        fn = tc.get("function", {})
                        fn_name = fn.get("name", "tool")
                        fn_args_raw = fn.get("arguments") or "{}"
                        if isinstance(fn_args_raw, str):
                            try:
                                fn_args = _json_g.loads(fn_args_raw)
                            except Exception:
                                fn_args = {"raw": fn_args_raw}
                        else:
                            fn_args = fn_args_raw if isinstance(fn_args_raw, dict) else {}

                        # Gemini 3.x: Reconstruct Part WITH thought_signature if available.
                        # Part.from_function_call() does NOT accept thought_signature,
                        # so we construct the Part directly.
                        thought_sig_raw = tc.get("thought_signature")
                        thought_sig_bytes = None
                        if thought_sig_raw:
                            if isinstance(thought_sig_raw, bytes):
                                thought_sig_bytes = thought_sig_raw
                            elif isinstance(thought_sig_raw, str):
                                import base64 as _b64

                                try:
                                    thought_sig_bytes = _b64.b64decode(thought_sig_raw)
                                except Exception:
                                    thought_sig_bytes = None

                        fc_obj = _gtypes.FunctionCall(name=fn_name, args=fn_args)
                        # Include id if available (Gemini 3.x)
                        fc_id = tc.get("id")
                        if fc_id:
                            fc_obj.id = fc_id

                        if thought_sig_bytes:
                            parts.append(
                                _gtypes.Part(
                                    function_call=fc_obj,
                                    thought_signature=thought_sig_bytes,
                                )
                            )
                            logger.debug(
                                "gemini_thought_signature_echoed",
                                fn_name=fn_name,
                                sig_len=len(thought_sig_bytes),
                            )
                        else:
                            parts.append(
                                _gtypes.Part.from_function_call(
                                    name=fn_name,
                                    args=fn_args,
                                )
                            )
                    if parts:  # Only add if we have valid function call parts
                        contents.append({"role": "model", "parts": parts})
                else:
                    # Normal assistant text message — skip if content is empty/None
                    content = msg.get("content") or ""
                    if not isinstance(content, str):
                        content = str(content)
                    if content.strip():
                        contents.append({"role": "model", "parts": [{"text": content}]})
                    else:
                        logger.debug("gemini_skip_empty_assistant_msg", msg_keys=list(msg.keys()))

            elif role == "tool":
                # Tool result → Gemini function_response (role=user)
                tool_name = msg.get("name") or "tool"
                tool_content = msg.get("content") or ""
                if not isinstance(tool_content, str):
                    tool_content = str(tool_content)
                # Gemini 3.x: Include id in FunctionResponse to map result to call
                fr_obj = _gtypes.FunctionResponse(
                    name=tool_name,
                    response={"result": tool_content},
                )
                tool_call_id = msg.get("tool_call_id")
                if tool_call_id:
                    fr_obj.id = tool_call_id
                contents.append(
                    {
                        "role": "user",
                        "parts": [_gtypes.Part(function_response=fr_obj)],
                    }
                )

        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Hola"}]}]

        # Debug: log contents structure for troubleshooting
        logger.debug(
            "gemini_contents_built",
            count=len(contents),
            roles=[c["role"] for c in contents],
            parts_counts=[len(c["parts"]) for c in contents],
        )

        from google.genai import types

        gen_config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        if system_instruction:
            gen_config.system_instruction = system_instruction

        if tools:
            gemini_tools = [types.Tool(function_declarations=[t.to_gemini_declarations() for t in tools])]
            gen_config.tools = gemini_tools

            if tool_choice == "auto":
                gen_config.tool_config = types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(mode="AUTO")
                )
            elif tool_choice == "none":
                gen_config.tool_config = types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(mode="NONE")
                )
            elif tool_choice == "required":
                gen_config.tool_config = types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(mode="ANY")
                )

        response = await self._google_client.aio.models.generate_content(
            model=model_id,
            contents=contents,
            config=gen_config,
        )

        # Extract content and tool calls
        content = ""
        tool_calls = []

        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text") and part.text:
                    content += part.text
                elif hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    args = dict(fc.args) if fc.args else {}
                    # Gemini 3 provides its own id; fallback to uuid for older models
                    fc_id = getattr(fc, "id", None) or f"call_{uuid.uuid4().hex[:8]}"
                    # Gemini 3.x thought signatures: MANDATORY for multi-turn tool calling.
                    # The thought_signature is on the Part, not on the FunctionCall.
                    # Must be echoed back in the next turn to maintain reasoning context.
                    thought_sig = getattr(part, "thought_signature", None)
                    if thought_sig:
                        logger.debug(
                            "gemini_thought_signature_captured",
                            fc_name=fc.name,
                            sig_len=len(thought_sig),
                        )
                    tool_calls.append(
                        ToolCall(
                            id=fc_id,
                            name=fc.name,
                            arguments=args,
                            thought_signature=thought_sig,
                        )
                    )

        # Extract usage
        usage_meta = getattr(response, "usage_metadata", None)
        usage = {
            "prompt_tokens": getattr(usage_meta, "prompt_token_count", 0) if usage_meta else 0,
            "completion_tokens": getattr(usage_meta, "candidates_token_count", 0) if usage_meta else 0,
            "total_tokens": getattr(usage_meta, "total_token_count", 0) if usage_meta else 0,
            "model_used": model_id,
        }

        finish_reason = "tool_calls" if tool_calls else "stop"

        logger.info(
            "llm_call_ok",
            provider="google",
            model=model_id,
            tokens=usage["total_tokens"],
            tool_calls=len(tool_calls),
        )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
            provider="google",
            model=model_id,
        )

    # ── OpenAI-Compatible (xAI, OpenRouter, Perplexity) ──────────

    async def _call_openai_compatible(
        self,
        model_id: str,
        api_key: str,
        base_url: str,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int,
        provider: str,
        tools: Optional[list[ToolSpec]] = None,
        tool_choice: str = "auto",
    ) -> LLMResponse:
        if provider == "perplexity":
            url = base_url
        else:
            url = f"{base_url}/chat/completions"

        if provider not in self._httpx_clients:
            # Sprint 45: HTTP/2 enabled for faster multiplexed connections
            # to LLM providers (reduces connection setup by 10-20ms/token)
            self._httpx_clients[provider] = httpx.AsyncClient(
                timeout=120.0, http2=True
            )
        client = self._httpx_clients[provider]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://elmonstruo.ai"
            headers["X-Title"] = "El Monstruo"

        payload: dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools and provider != "perplexity":
            payload["tools"] = [t.to_openai_format() for t in tools]
            payload["tool_choice"] = tool_choice

        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        choices = data.get("choices", [])
        if not choices:
            raise ValueError(f"No choices in {provider} response: {data}")

        msg = choices[0].get("message", {})
        content = msg.get("content", "") or ""
        finish_reason = choices[0].get("finish_reason", "") or ""

        # Extract tool calls (OpenAI-compatible format)
        tool_calls = []
        raw_tool_calls = msg.get("tool_calls", [])
        if raw_tool_calls:
            for tc in raw_tool_calls:
                func = tc.get("function", {})
                try:
                    args = (
                        json.loads(func.get("arguments", "{}"))
                        if isinstance(func.get("arguments"), str)
                        else func.get("arguments", {})
                    )
                except json.JSONDecodeError:
                    args = {"raw": func.get("arguments", "")}
                tool_calls.append(
                    ToolCall(
                        id=tc.get("id", f"call_{uuid.uuid4().hex[:8]}"),
                        name=func.get("name", ""),
                        arguments=args,
                    )
                )

        # Normalize finish_reason
        if finish_reason == "tool_calls" or (tool_calls and finish_reason != "stop"):
            finish_reason = "tool_calls"

        usage_data = data.get("usage", {})
        usage = {
            "prompt_tokens": usage_data.get("prompt_tokens", 0),
            "completion_tokens": usage_data.get("completion_tokens", 0),
            "total_tokens": usage_data.get("total_tokens", 0),
            "model_used": data.get("model", model_id),
        }

        logger.info(
            "llm_call_ok",
            provider=provider,
            model=model_id,
            tokens=usage["total_tokens"],
            tool_calls=len(tool_calls),
        )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
            provider=provider,
            model=model_id,
        )

    # ── Streaming Interface (unchanged from Sprint 1) ────────────
    # Note: Streaming does NOT support tool calling yet.
    # Tool calling requires full response to parse tool_calls.

    async def chat_stream(
        self,
        model_config: dict,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """
        Streaming chat completion — yields text chunks.
        Does NOT support tool calling (use chat_with_tools for that).
        """
        provider = model_config["provider"]
        model_id = model_config["model_id"]
        api_key = os.environ.get(model_config["api_key_env"], "")

        if not api_key:
            raise ValueError(f"API key not found: {model_config['api_key_env']}")

        if max_tokens is None:
            if model_config.get("use_max_completion_tokens"):
                max_tokens = model_config.get("max_completion_tokens", 4000)
            else:
                max_tokens = model_config.get("max_tokens", 4096)

        logger.info("llm_stream_start", provider=provider, model_id=model_id)

        if provider == "openai":
            async for chunk in self._stream_openai(model_id, api_key, messages, temperature, max_tokens, model_config):
                yield chunk
        elif provider == "anthropic":
            async for chunk in self._stream_anthropic(model_id, api_key, messages, temperature, max_tokens):
                yield chunk
        elif provider == "google":
            async for chunk in self._stream_google(model_id, api_key, messages, temperature, max_tokens):
                yield chunk
        elif provider in ("xai", "openrouter", "perplexity"):
            base_url = model_config.get("base_url", "")
            async for chunk in self._stream_openai_compatible(
                model_id, api_key, base_url, messages, temperature, max_tokens, provider
            ):
                yield chunk
        else:
            raise ValueError(f"Unknown provider: {provider}")

    # ── Streaming: OpenAI ─────────────────────────────────────────

    async def _stream_openai(self, model_id, api_key, messages, temperature, max_tokens, model_config):
        if self._openai_client is None:
            from openai import AsyncOpenAI

            self._openai_client = AsyncOpenAI(api_key=api_key)

        kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        if model_config.get("use_max_completion_tokens"):
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["max_tokens"] = max_tokens

        stream = await self._openai_client.chat.completions.create(**kwargs)
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    # ── Streaming: Anthropic ──────────────────────────────────────

    async def _stream_anthropic(self, model_id, api_key, messages, temperature, max_tokens):
        if self._anthropic_client is None:
            from anthropic import AsyncAnthropic

            self._anthropic_client = AsyncAnthropic(api_key=api_key)

        system_prompt = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                user_messages.append(msg)
        if not user_messages:
            user_messages = [{"role": "user", "content": "Hola"}]

        # claude-opus-4-7: temperature removed, use adaptive thinking
        _is_opus_47 = "opus-4-7" in model_id or "opus-4.7" in model_id
        kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": user_messages,
            "max_tokens": max_tokens,
        }
        if not _is_opus_47:
            kwargs["temperature"] = temperature
        if _is_opus_47:
            kwargs["thinking"] = {"type": "adaptive", "display": "summarized"}
            kwargs["output_config"] = {"effort": "high"}
        if system_prompt:
            kwargs["system"] = system_prompt

        async with self._anthropic_client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    # ── Streaming: Google Gemini ──────────────────────────────────

    async def _stream_google(self, model_id, api_key, messages, temperature, max_tokens):
        if self._google_client is None:
            from google import genai

            self._google_client = genai.Client(api_key=api_key)

        system_instruction = ""
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
            elif msg["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Hola"}]}]

        from google.genai import types

        gen_config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        if system_instruction:
            gen_config.system_instruction = system_instruction

        async for chunk in await self._google_client.aio.models.generate_content_stream(
            model=model_id,
            contents=contents,
            config=gen_config,
        ):
            if chunk.text:
                yield chunk.text

    # ── Streaming: OpenAI-Compatible (xAI, OpenRouter, Perplexity)

    async def _stream_openai_compatible(self, model_id, api_key, base_url, messages, temperature, max_tokens, provider):
        if provider == "perplexity":
            url = base_url
        else:
            url = f"{base_url}/chat/completions"

        if provider not in self._httpx_clients:
            # Sprint 45: HTTP/2 enabled for faster multiplexed streaming
            self._httpx_clients[provider] = httpx.AsyncClient(
                timeout=120.0, http2=True
            )
        client = self._httpx_clients[provider]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://elmonstruo.ai"
            headers["X-Title"] = "El Monstruo"

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        async with client.stream("POST", url, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, IndexError, KeyError):
                        continue

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _extract_usage(usage_obj: Any, model_id: str) -> dict[str, Any]:
        if usage_obj is None:
            return {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "model_used": model_id,
            }
        return {
            "prompt_tokens": getattr(usage_obj, "prompt_tokens", 0),
            "completion_tokens": getattr(usage_obj, "completion_tokens", 0),
            "total_tokens": getattr(usage_obj, "total_tokens", 0),
            "model_used": model_id,
        }
