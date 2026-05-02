"""
El Monstruo — Fallback Engine (Sprint 29 — Épica 5)
=====================================================
Automatic failover to Groq/Together when primary providers fail.

Implements:
  1. Circuit breaker pattern per provider
  2. Exponential backoff with jitter
  3. Provider health tracking
  4. Automatic fallback chain execution

Gate Épica 5: When primary provider returns 5xx or timeout,
             system automatically falls back to Groq/Together
             within 2 seconds.

Provider Priority:
  OpenAI → Anthropic → Google → xAI → OpenRouter → Groq → Together

Sprint 29 | 0.22.0-sprint29 | 25 abril 2026
"""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import httpx
import structlog

logger = structlog.get_logger("kernel.fallback_engine")


# ── Circuit Breaker States ────────────────────────────────────────────


class CircuitState(str, Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Provider failing, skip it
    HALF_OPEN = "half_open"  # Testing if provider recovered


@dataclass
class ProviderCircuit:
    """Circuit breaker state for a single provider."""

    provider: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure: float = 0.0
    last_success: float = 0.0
    open_until: float = 0.0
    total_calls: int = 0
    total_failures: int = 0

    # Config
    failure_threshold: int = 3  # Failures before opening circuit
    recovery_timeout: float = 60.0  # Seconds before trying half-open
    half_open_max: int = 1  # Max concurrent half-open attempts


@dataclass
class FallbackResult:
    """Result from a fallback chain execution."""

    provider: str
    model: str
    response: Any
    latency_ms: float
    fallback_depth: int  # 0 = primary, 1+ = fallback
    circuit_states: dict[str, str]


# ── Provider Configurations ───────────────────────────────────────────

PROVIDERS: dict[str, dict[str, Any]] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "models": ["gpt-5.5", "gpt-4.1-mini"],
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "api_key_env": "ANTHROPIC_API_KEY",
        "models": ["claude-opus-4-7", "claude-sonnet-4-6"],
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "api_key_env": "GEMINI_API_KEY",
        "models": ["gemini-3.1-pro", "gemini-3.1-flash-lite"],
    },
    "xai": {
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "XAI_API_KEY",
        "models": ["grok-4.20"],
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "models": ["deepseek-r1-0528", "kimi-k2.5"],
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "models": ["groq-llama-scout"],
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "api_key_env": "TOGETHER_API_KEY",
        "models": ["together-llama-scout"],
    },
}


class FallbackEngine:
    """
    Manages provider failover with circuit breakers.
    Automatically routes to backup providers when primaries fail.
    """

    def __init__(self) -> None:
        self._circuits: dict[str, ProviderCircuit] = {}
        for provider in PROVIDERS:
            self._circuits[provider] = ProviderCircuit(provider=provider)

    def _get_circuit(self, provider: str) -> ProviderCircuit:
        """Get or create circuit for a provider."""
        if provider not in self._circuits:
            self._circuits[provider] = ProviderCircuit(provider=provider)
        return self._circuits[provider]

    def _check_circuit(self, provider: str) -> bool:
        """Check if a provider is available (circuit not open)."""
        circuit = self._get_circuit(provider)
        now = time.monotonic()

        if circuit.state == CircuitState.CLOSED:
            return True

        if circuit.state == CircuitState.OPEN:
            if now >= circuit.open_until:
                circuit.state = CircuitState.HALF_OPEN
                logger.info("circuit_half_open", provider=provider)
                return True
            return False

        if circuit.state == CircuitState.HALF_OPEN:
            return True

        return False

    def _record_success(self, provider: str) -> None:
        """Record a successful call to a provider."""
        circuit = self._get_circuit(provider)
        circuit.total_calls += 1
        circuit.last_success = time.monotonic()
        circuit.failure_count = 0

        if circuit.state == CircuitState.HALF_OPEN:
            circuit.state = CircuitState.CLOSED
            logger.info("circuit_closed", provider=provider, reason="recovery_success")

    def _record_failure(self, provider: str) -> None:
        """Record a failed call to a provider."""
        circuit = self._get_circuit(provider)
        circuit.total_calls += 1
        circuit.total_failures += 1
        circuit.failure_count += 1
        circuit.last_failure = time.monotonic()

        if circuit.failure_count >= circuit.failure_threshold:
            circuit.state = CircuitState.OPEN
            # Exponential backoff with jitter
            backoff = circuit.recovery_timeout * (2 ** min(circuit.total_failures - circuit.failure_threshold, 4))
            jitter = random.uniform(0, backoff * 0.1)
            circuit.open_until = time.monotonic() + backoff + jitter
            logger.warning(
                "circuit_opened",
                provider=provider,
                failures=circuit.failure_count,
                backoff_s=f"{backoff + jitter:.1f}",
            )

    def get_provider_for_model(self, model_name: str) -> Optional[str]:
        """Find which provider serves a given model."""
        for provider, config in PROVIDERS.items():
            if model_name in config["models"]:
                return provider
        return None

    async def call_with_fallback(
        self,
        primary_model: str,
        fallback_models: list[str],
        messages: list[dict[str, str]],
        max_tokens: int = 1000,
        temperature: Optional[float] = None,
    ) -> FallbackResult:
        """
        Call primary model, falling back through the chain on failure.

        Returns FallbackResult with the first successful response.
        Raises RuntimeError if all models in the chain fail.
        """
        chain = [primary_model] + fallback_models
        last_error = None

        for depth, model in enumerate(chain):
            provider = self.get_provider_for_model(model)
            if not provider:
                logger.warning("model_provider_unknown", model=model)
                continue

            if not self._check_circuit(provider):
                logger.info("circuit_skip", provider=provider, model=model, state="open")
                continue

            api_key = os.environ.get(PROVIDERS[provider]["api_key_env"], "")
            if not api_key:
                logger.info("provider_no_key", provider=provider)
                continue

            start = time.monotonic()
            try:
                response = await self._call_provider(
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                latency_ms = (time.monotonic() - start) * 1000
                self._record_success(provider)

                logger.info(
                    "fallback_success",
                    model=model,
                    provider=provider,
                    depth=depth,
                    latency_ms=f"{latency_ms:.0f}",
                )

                return FallbackResult(
                    provider=provider,
                    model=model,
                    response=response,
                    latency_ms=latency_ms,
                    fallback_depth=depth,
                    circuit_states=self.get_circuit_states(),
                )

            except Exception as e:
                self._record_failure(provider)
                last_error = e
                logger.warning(
                    "fallback_attempt_failed",
                    model=model,
                    provider=provider,
                    depth=depth,
                    error=str(e)[:200],
                )

        raise RuntimeError(f"All models in fallback chain failed. Chain: {chain}. Last error: {last_error}")

    async def _call_provider(
        self,
        provider: str,
        model: str,
        api_key: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: Optional[float],
    ) -> dict[str, Any]:
        """Make an actual API call to a provider."""
        from config.model_catalog import MODELS, supports_temperature

        catalog_entry = MODELS.get(model, {})
        model_id = catalog_entry.get("model_id", model)

        # Build request based on provider
        if provider == "anthropic":
            return await self._call_anthropic(api_key, model_id, messages, max_tokens, temperature)
        elif provider == "google":
            return await self._call_google(api_key, model_id, messages, max_tokens)
        else:
            # OpenAI-compatible (OpenAI, xAI, OpenRouter, Groq, Together)
            base_url = PROVIDERS[provider]["base_url"]
            return await self._call_openai_compat(
                api_key,
                base_url,
                model_id,
                messages,
                max_tokens,
                temperature if supports_temperature(model) else None,
            )

    async def _call_openai_compat(
        self,
        api_key: str,
        base_url: str,
        model_id: str,
        messages: list,
        max_tokens: int,
        temperature: Optional[float],
    ) -> dict:
        """Call OpenAI-compatible API (OpenAI, xAI, OpenRouter, Groq, Together)."""
        body: dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if temperature is not None:
            body["temperature"] = temperature

        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            r.raise_for_status()
            return r.json()

    async def _call_anthropic(
        self,
        api_key: str,
        model_id: str,
        messages: list,
        max_tokens: int,
        temperature: Optional[float],
    ) -> dict:
        """Call Anthropic API."""
        body: dict[str, Any] = {
            "model": model_id,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if temperature is not None:
            body["temperature"] = temperature

        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            r.raise_for_status()
            data = r.json()
            # Normalize to OpenAI format
            return {
                "choices": [
                    {
                        "message": {
                            "content": data["content"][0]["text"],
                            "role": "assistant",
                        }
                    }
                ],
                "usage": data.get("usage", {}),
                "model": model_id,
            }

    async def _call_google(
        self,
        api_key: str,
        model_id: str,
        messages: list,
        max_tokens: int,
    ) -> dict:
        """Call Google Gemini API."""
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": contents,
                    "generationConfig": {"maxOutputTokens": max_tokens},
                },
            )
            r.raise_for_status()
            data = r.json()
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return {
                "choices": [{"message": {"content": text, "role": "assistant"}}],
                "model": model_id,
            }

    def get_circuit_states(self) -> dict[str, str]:
        """Get current circuit breaker states for all providers."""
        return {provider: circuit.state.value for provider, circuit in self._circuits.items()}

    def get_status(self) -> dict[str, Any]:
        """Return fallback engine status for /health endpoint."""
        circuits = {}
        for provider, circuit in self._circuits.items():
            has_key = bool(os.environ.get(PROVIDERS[provider]["api_key_env"], ""))
            circuits[provider] = {
                "state": circuit.state.value,
                "available": has_key,
                "failures": circuit.total_failures,
                "calls": circuit.total_calls,
            }

        return {
            "active": True,
            "version": "1.0.0-sprint29",
            "providers": len(circuits),
            "circuits": circuits,
        }


# ── Singleton ─────────────────────────────────────────────────────────

_engine: Optional[FallbackEngine] = None


def get_fallback_engine() -> FallbackEngine:
    """Get the singleton FallbackEngine instance."""
    global _engine
    if _engine is None:
        _engine = FallbackEngine()
    return _engine
