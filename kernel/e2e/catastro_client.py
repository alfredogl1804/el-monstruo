"""
Sprint 87 — Catastro Runtime Client.

Selecciona el modelo más apropiado para cada step LLM consultando el Catastro
vivo en runtime. NO hardcodea modelos. Es la diferencia v1 vs v2 del Sprint 87.

Patrón: para cada step → consulta /v1/catastro/recommend con un use_case →
elige el top-1 → loggea modelo_consultado en e2e_step_log.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx
import structlog

logger = structlog.get_logger("e2e_catastro_client")


# Mapeo step → use_case del Catastro.
# Si el Catastro no responde con ese use_case específico, fallback a top general.
STEP_USE_CASE_MAP: Dict[str, str] = {
    "INVESTIGAR": "research_grounded",
    "ARCHITECT": "product_architect",
    "ESTRATEGIA": "strategic_reasoning",
    "FINANZAS": "financial_analysis",
    "CREATIVO": "creative_writing",
    "VENTAS": "sales_copywriting",
    "TECNICO": "code_generation",
    "CRITIC": "vision_evaluation",
}


# Fallback hardcoded SOLO para casos catastro-down + step crítico.
# Documentado en spec como "deuda asumida en modo degraded".
STEP_FALLBACK_MODEL: Dict[str, str] = {
    "INVESTIGAR": "perplexity/sonar-pro",
    "ARCHITECT": "openai/gpt-5",
    "ESTRATEGIA": "anthropic/claude-opus-4-7",
    "FINANZAS": "anthropic/claude-opus-4-7",
    "CREATIVO": "openai/gpt-5",
    "VENTAS": "anthropic/claude-opus-4-7",
    "TECNICO": "openai/gpt-5",
    "CRITIC": "google/gemini-3-1-pro-preview",
}


class CatastroRuntimeClient:
    """Cliente HTTP que consulta el Catastro propio en runtime."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_seconds: float = 5.0,
    ) -> None:
        self._base_url = (
            base_url
            or os.environ.get("E2E_CATASTRO_BASE_URL")
            or os.environ.get("KERNEL_BASE_URL")
            or "http://localhost:8000"
        ).rstrip("/")
        self._api_key = api_key or os.environ.get("MONSTRUO_API_KEY", "")
        self._timeout = timeout_seconds

    async def select_model_for_step(
        self,
        step_name: str,
        *,
        top_n: int = 1,
        only_quorum: bool = True,
    ) -> Dict[str, Any]:
        """
        Devuelve {model_id, source, reasoning, degraded}.
        - source='catastro' si vino del recommend exitoso
        - source='fallback' si Catastro no respondió o no devolvió modelos
        """
        use_case = STEP_USE_CASE_MAP.get(step_name)
        if use_case is None:
            return self._fallback(step_name, reason="no_use_case_mapped")

        url = f"{self._base_url}/v1/catastro/recommend"
        body = {
            "use_case": use_case,
            "top_n": top_n,
            "only_quorum": only_quorum,
        }
        headers = {"X-API-Key": self._api_key} if self._api_key else {}

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=body, headers=headers)
            if response.status_code != 200:
                logger.warning(
                    "e2e_catastro_recommend_non_200",
                    step=step_name,
                    status=response.status_code,
                )
                return self._fallback(step_name, reason=f"http_{response.status_code}")

            data = response.json()
            if data.get("degraded"):
                return self._fallback(step_name, reason="catastro_degraded")

            modelos: List[Dict[str, Any]] = data.get("modelos", [])
            if not modelos:
                return self._fallback(step_name, reason="empty_modelos")

            top = modelos[0]
            return {
                "model_id": top.get("id") or top.get("nombre"),
                "model_label": top.get("nombre"),
                "model_provider": top.get("proveedor"),
                "trono_score": top.get("trono_global"),
                "source": "catastro",
                "use_case": use_case,
                "degraded": False,
            }
        except Exception as exc:  # pragma: no cover (network)
            logger.warning(
                "e2e_catastro_recommend_failed",
                step=step_name,
                error=str(exc),
            )
            return self._fallback(step_name, reason=f"exception_{type(exc).__name__}")

    def _fallback(self, step_name: str, *, reason: str) -> Dict[str, Any]:
        model = STEP_FALLBACK_MODEL.get(step_name, "openai/gpt-5")
        logger.info("e2e_catastro_fallback_used", step=step_name, model=model, reason=reason)
        return {
            "model_id": model,
            "model_label": model,
            "model_provider": model.split("/")[0] if "/" in model else None,
            "trono_score": None,
            "source": "fallback",
            "use_case": STEP_USE_CASE_MAP.get(step_name, "generic"),
            "degraded": True,
            "fallback_reason": reason,
        }
