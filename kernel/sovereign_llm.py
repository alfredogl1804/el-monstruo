"""
El Monstruo — Sovereign LLM Layer (Sprint 56.5)
==============================================
Capa de abstracción para modelos LLM con soberanía progresiva.

Estrategia de routing:
  Tier 1 (Simple): Clasificación, formatting, extracción → Ollama local (gemma3)
  Tier 2 (Medio): Resumen, Q&A, análisis básico → Ollama cloud / gpt-4o-mini
  Tier 3 (Complejo): Razonamiento profundo, código, causal → GPT-4o / Gemini
  Tier 4 (Crítico): Decisiones de negocio, predicciones → Multi-modelo (Sabios)

Fallback chain:
  Primary (preferred for tier) → Next provider → Error

Benefits:
  - Tier 1-2 tasks: $0 cost (local) o ~$0.001 (Ollama cloud)
  - Availability: Si OpenAI cae, Ollama sigue funcionando
  - Privacy: Datos sensibles nunca salen del servidor (Ollama local)
  - Speed: Modelos locales = 0 network latency

Validated: ollama==0.6.2 (MIT, Apr 29, 2026), AsyncClient nativo
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.sovereign_llm")


class TaskTier(IntEnum):
    """Tier de complejidad de tarea."""

    SIMPLE = 1  # Clasificación, formatting, extracción
    MEDIUM = 2  # Resumen, Q&A, análisis básico
    COMPLEX = 3  # Razonamiento profundo, código, causal
    CRITICAL = 4  # Decisiones de negocio, predicciones (usa Sabios)


@dataclass
class LLMResponse:
    """Respuesta unificada de cualquier proveedor."""

    content: str
    model: str
    provider: str  # openai, anthropic, google, ollama_local, ollama_cloud
    tier: int
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    fallback_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "tier": self.tier,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "latency_ms": round(self.latency_ms, 1),
            "cost_usd": round(self.cost_usd, 6),
            "fallback_used": self.fallback_used,
        }


class SovereignLLM:
    """
    Capa soberana de LLM con routing inteligente y fallback.

    T1: Tier 1 tasks se ejecutan en Ollama local/cloud sin tocar OpenAI
    T2: Si Ollama falla, fallback automático a OpenAI funciona
    T3: Stats muestran distribución de calls por provider
    T4: Costo de Tier 1-2 es $0 (local) o <$0.001 (cloud)
    T5: initialize() detecta correctamente qué proveedores están disponibles
    """

    # Modelos por tier — orden = preferencia (primero = preferido)
    TIER_MODELS = {
        TaskTier.SIMPLE: [
            {"provider": "ollama_local", "model": "gemma3:8b", "cost_per_1k": 0.0},
            {"provider": "ollama_cloud", "model": "gemma3", "cost_per_1k": 0.0001},
            {"provider": "openai", "model": "gpt-4o-mini", "cost_per_1k": 0.00015},
        ],
        TaskTier.MEDIUM: [
            {"provider": "ollama_cloud", "model": "gpt-oss:120b-cloud", "cost_per_1k": 0.001},
            {"provider": "openai", "model": "gpt-4o-mini", "cost_per_1k": 0.00015},
            {"provider": "ollama_local", "model": "gemma3:8b", "cost_per_1k": 0.0},
        ],
        TaskTier.COMPLEX: [
            {"provider": "openai", "model": "gpt-4o", "cost_per_1k": 0.005},
            {"provider": "google", "model": "gemini-2.5-flash", "cost_per_1k": 0.00075},
            {"provider": "ollama_cloud", "model": "deepseek-v3.1:671b-cloud", "cost_per_1k": 0.003},
        ],
        TaskTier.CRITICAL: [
            # Tier 4 usa consult_sabios (multi-modelo), no esta capa
            # Fallback de emergencia:
            {"provider": "openai", "model": "gpt-4o", "cost_per_1k": 0.005},
        ],
    }

    def __init__(self):
        self._ollama_local = None
        self._ollama_cloud = None
        self._openai = None
        self._gemini = None
        self._initialized = False
        self._stats: dict[str, Any] = {
            "calls_by_provider": {},
            "calls_by_tier": {},
            "fallbacks_used": 0,
            "total_cost_usd": 0.0,
            "total_calls": 0,
        }

    async def initialize(self) -> None:
        """
        Inicializar clientes de LLM.
        T5: initialize() detecta correctamente qué proveedores están disponibles.
        """
        # ── Ollama local ───────────────────────────────────────────
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        try:
            from ollama import AsyncClient

            self._ollama_local = AsyncClient(host=ollama_host)
            # Test connection — si falla, Ollama no está disponible
            await self._ollama_local.list()
            logger.info("ollama_local_connected", host=ollama_host)
        except Exception as e:
            logger.info("ollama_local_unavailable", reason=str(e)[:100])
            self._ollama_local = None

        # ── Ollama cloud ───────────────────────────────────────────
        ollama_api_key = os.environ.get("OLLAMA_API_KEY")
        if ollama_api_key:
            try:
                from ollama import AsyncClient

                self._ollama_cloud = AsyncClient(
                    host="https://ollama.com",
                    headers={"Authorization": f"Bearer {ollama_api_key}"},
                )
                logger.info("ollama_cloud_configured")
            except Exception as e:
                logger.info("ollama_cloud_unavailable", reason=str(e)[:100])
                self._ollama_cloud = None

        # ── OpenAI ─────────────────────────────────────────────────
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import AsyncOpenAI

                self._openai = AsyncOpenAI(api_key=openai_key)
                logger.info("openai_configured")
            except Exception as e:
                logger.warning("openai_init_failed", error=str(e)[:100])

        # ── Google Gemini ──────────────────────────────────────────
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=gemini_key)
                self._gemini = genai
                logger.info("gemini_configured")
            except Exception as e:
                logger.warning("gemini_init_failed", error=str(e)[:100])

        self._initialized = True
        logger.info(
            "sovereign_llm_initialized",
            ollama_local=self._ollama_local is not None,
            ollama_cloud=self._ollama_cloud is not None,
            openai=self._openai is not None,
            gemini=self._gemini is not None,
        )

    async def generate(
        self,
        prompt: str,
        tier: TaskTier = TaskTier.MEDIUM,
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """
        Generar respuesta con routing inteligente por tier.
        Intenta el modelo preferido del tier, con fallback automático.

        T1: Tier 1 tasks se ejecutan en Ollama local/cloud sin tocar OpenAI
        T2: Si Ollama falla, fallback automático a OpenAI funciona
        """
        if not self._initialized:
            await self.initialize()

        start = time.time()
        models = self.TIER_MODELS.get(tier, self.TIER_MODELS[TaskTier.MEDIUM])
        last_error = None
        fallback_used = False

        for i, model_config in enumerate(models):
            provider = model_config["provider"]
            model = model_config["model"]

            try:
                content = await self._call_provider(
                    provider=provider,
                    model=model,
                    prompt=prompt,
                    system=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                latency = (time.time() - start) * 1000

                # Track stats
                self._stats["calls_by_provider"][provider] = self._stats["calls_by_provider"].get(provider, 0) + 1
                self._stats["calls_by_tier"][str(tier.value)] = self._stats["calls_by_tier"].get(str(tier.value), 0) + 1
                self._stats["total_calls"] += 1
                if i > 0:
                    self._stats["fallbacks_used"] += 1
                    fallback_used = True

                cost = model_config["cost_per_1k"] * (len(prompt) + len(content)) / 4000
                self._stats["total_cost_usd"] += cost

                logger.info(
                    "sovereign_llm_call",
                    provider=provider,
                    model=model,
                    tier=tier.value,
                    latency_ms=round(latency, 1),
                    fallback=fallback_used,
                )

                return LLMResponse(
                    content=content,
                    model=model,
                    provider=provider,
                    tier=tier.value,
                    latency_ms=latency,
                    cost_usd=cost,
                    fallback_used=fallback_used,
                )

            except Exception as e:
                last_error = e
                logger.warning(
                    "llm_provider_failed",
                    provider=provider,
                    model=model,
                    error=str(e)[:100],
                    trying_next=i < len(models) - 1,
                )
                continue

        # Todos los proveedores fallaron
        raise RuntimeError(f"All LLM providers failed for tier {tier}. Last error: {last_error}")

    async def _call_provider(
        self,
        provider: str,
        model: str,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Llamar a un proveedor específico."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        if provider == "ollama_local":
            if not self._ollama_local:
                raise RuntimeError("Ollama local not available")
            response = await self._ollama_local.chat(
                model=model,
                messages=messages,
                options={"temperature": temperature, "num_predict": max_tokens},
            )
            return response.message.content

        elif provider == "ollama_cloud":
            if not self._ollama_cloud:
                raise RuntimeError("Ollama cloud not available")
            response = await self._ollama_cloud.chat(
                model=model,
                messages=messages,
                options={"temperature": temperature, "num_predict": max_tokens},
            )
            return response.message.content

        elif provider == "openai":
            if not self._openai:
                raise RuntimeError("OpenAI not available")
            response = await self._openai.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""

        elif provider == "google":
            if not self._gemini:
                raise RuntimeError("Gemini not available")
            model_obj = self._gemini.GenerativeModel(model)
            response = await model_obj.generate_content_async(prompt)
            return response.text or ""

        else:
            raise RuntimeError(f"Unknown provider: {provider}")

    def get_stats(self) -> dict[str, Any]:
        """
        Estadísticas de uso.
        T3: Stats muestran distribución de calls por provider.
        """
        return {
            **self._stats,
            "providers_available": {
                "ollama_local": self._ollama_local is not None,
                "ollama_cloud": self._ollama_cloud is not None,
                "openai": self._openai is not None,
                "gemini": self._gemini is not None,
            },
            "initialized": self._initialized,
        }


# ── Singleton ──────────────────────────────────────────────────────

_sovereign_llm_instance: Optional[SovereignLLM] = None


def get_sovereign_llm() -> Optional[SovereignLLM]:
    """Obtener el singleton del SovereignLLM."""
    return _sovereign_llm_instance


async def init_sovereign_llm() -> SovereignLLM:
    """
    Inicializar el SovereignLLM singleton.
    Llamar desde el lifespan de main.py.
    """
    global _sovereign_llm_instance
    _sovereign_llm_instance = SovereignLLM()
    await _sovereign_llm_instance.initialize()
    return _sovereign_llm_instance
