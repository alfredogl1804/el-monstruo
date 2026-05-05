"""
Sprint 87.2 Bloque 3 — Critic Visual real con Gemini Vision.

Diseño:
- Catastro elige modelo (StepName.CRITIC) — actual default `gemini-3-1-pro-preview`.
- Toma screenshot path + brief context, lo manda a Gemini Vision via google-genai.
- Output Pydantic estructurado: score 0-100 + sub-scores + razones.
- LLM-as-parser (semilla 39): response_schema con Pydantic.
- Threshold de comercializable: 80.

Capa Memento aplicada:
- Verifica que screenshot existe y < 5 MB antes de enviar a la API.
- Si Gemini key ausente, screenshot ausente, o llamada falla →
  fallback heurístico determinístico con score conservador 60 + razón explícita.
- NO bloquea el pipeline; siempre retorna un CriticVisualReport.

Brand DNA: critic_visual_evaluate_*_failed.

PUENTE hasta sovereign_browser (Capa 1 Manos magna post-v1.0).
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from pydantic import BaseModel, ConfigDict, Field

logger = structlog.get_logger("kernel.e2e.critic_visual.gemini_vision")

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB
DEFAULT_TIMEOUT_S = 45


# ── Errores con identidad ────────────────────────────────────────────────────


class GeminiVisionFailed(Exception):
    """Brand DNA: critic_visual_evaluate_*_failed."""

    code = "critic_visual_evaluate_failed"


class GeminiVisionMissingKey(GeminiVisionFailed):
    code = "critic_visual_evaluate_missing_key"


class GeminiVisionImageTooLarge(GeminiVisionFailed):
    code = "critic_visual_evaluate_image_too_large"


class GeminiVisionAPIFailed(GeminiVisionFailed):
    code = "critic_visual_evaluate_api_failed"


# ── Schemas Pydantic (LLM-as-parser) ─────────────────────────────────────────


class CriticVisualSubScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estetica: int = Field(..., ge=0, le=100, description="Calidad estética visual general")
    cta_claridad: int = Field(..., ge=0, le=100, description="Claridad del Call To Action")
    jerarquia_visual: int = Field(..., ge=0, le=100, description="Jerarquía visual / orden")
    profesionalismo: int = Field(..., ge=0, le=100, description="Percepción de profesionalismo")


class CriticVisualReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int = Field(..., ge=0, le=100, description="Score global 0-100")
    sub_scores: CriticVisualSubScores
    razones_aprobacion: List[str] = Field(default_factory=list)
    razones_mejora: List[str] = Field(default_factory=list)
    veredicto: str = Field(..., description="comercializable | rework | descartar")
    deploy_url: str
    modelo_consultado: str
    source: str = Field(..., description="gemini_vision | heuristic_fallback")
    fallback_reason: Optional[str] = None
    evaluated_at: str
    duration_ms: int


# ── Heuristic fallback determinístico ────────────────────────────────────────


def _heuristic_fallback(
    *, deploy_url: str, modelo: str, reason: str, started: float
) -> CriticVisualReport:
    """Score conservador 60 cuando Gemini Vision no se puede usar."""
    return CriticVisualReport(
        score=60,
        sub_scores=CriticVisualSubScores(
            estetica=60, cta_claridad=60, jerarquia_visual=60, profesionalismo=60
        ),
        razones_aprobacion=[
            "Pipeline completo sin errores. Estructura HTML válida según renderer Brand DNA.",
        ],
        razones_mejora=[
            "Critic Visual real no disponible: " + reason,
            "Score conservador 60 — recomendado human review.",
        ],
        veredicto="rework",
        deploy_url=deploy_url,
        modelo_consultado=modelo,
        source="heuristic_fallback",
        fallback_reason=reason,
        evaluated_at=datetime.now(timezone.utc).isoformat(),
        duration_ms=int((time.perf_counter() - started) * 1000),
    )


# ── Llamada Gemini Vision ────────────────────────────────────────────────────


_PROMPT_SYSTEM = """Eres un evaluador visual senior de landing pages. Tu trabajo es
evaluar la calidad visual y de conversión de una landing page deployada, dada una
captura de pantalla full-page.

Devuelves JSON estructurado con:
- score: int 0-100 (calidad global)
- sub_scores: estética, cta_claridad, jerarquia_visual, profesionalismo (cada uno 0-100)
- razones_aprobacion: lista de 1-4 razones específicas de por qué funciona visualmente
- razones_mejora: lista de 1-4 razones específicas de qué mejorar
- veredicto: "comercializable" si score>=80, "rework" si 50<=score<80, "descartar" si <50

Sé estricto pero justo. Una landing genérica sin identidad debe puntuar bajo.
Una landing con jerarquía clara, CTA visible y estética coherente debe puntuar alto."""


_PROMPT_USER_TEMPLATE = """Evalúa esta landing page deployada en {deploy_url}.

Contexto del brief original:
- Frase del usuario: {frase_input}
- Nombre del producto: {nombre}
- Propuesta de valor esperada: {propuesta_valor}

Devuelve el JSON estructurado según el schema."""


def _read_image_bytes(path: str) -> bytes:
    p = Path(path)
    if not p.exists():
        raise GeminiVisionFailed(
            f"critic_visual_evaluate_failed: screenshot no existe en {path}"
        )
    size = p.stat().st_size
    if size > MAX_IMAGE_BYTES:
        raise GeminiVisionImageTooLarge(
            f"critic_visual_evaluate_image_too_large: {size} bytes > {MAX_IMAGE_BYTES} cap"
        )
    return p.read_bytes()


async def _call_gemini_vision(
    *, image_bytes: bytes, deploy_url: str, brief_ctx: Dict[str, Any], model_id: str
) -> Dict[str, Any]:
    """Invoca Gemini Vision via google-genai. Retorna dict parseado del JSON."""
    api_key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    if not api_key:
        raise GeminiVisionMissingKey(
            "critic_visual_evaluate_missing_key: GEMINI_API_KEY ausente"
        )

    try:
        from google import genai
        from google.genai import types as genai_types
    except ImportError as e:
        raise GeminiVisionAPIFailed(
            f"critic_visual_evaluate_api_failed: google-genai no instalado — {e!s}"
        ) from e

    user_prompt = _PROMPT_USER_TEMPLATE.format(
        deploy_url=deploy_url,
        frase_input=brief_ctx.get("frase_input", "n/a"),
        nombre=brief_ctx.get("nombre", "n/a"),
        propuesta_valor=brief_ctx.get("propuesta_valor", "n/a"),
    )

    # Modelo Gemini real disponible: usa el más reciente que el SDK soporte.
    # El catastro elige el id; si trae preview que no existe, fallback al estable.
    candidate_models = [model_id, "gemini-2.5-pro", "gemini-2.0-flash-exp"]

    def _sync_call() -> Dict[str, Any]:
        client = genai.Client(api_key=api_key)
        last_err: Optional[Exception] = None
        for mid in candidate_models:
            try:
                # Sprint 87.2 hotfix B3: Pasamos la clase Pydantic directa.
                # google-genai 1.x convierte automáticamente al dialect OpenAPI 3.0
                # que Gemini espera (sin `additionalProperties` que rompe la API).
                response = client.models.generate_content(
                    model=mid,
                    contents=[
                        genai_types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                        _PROMPT_SYSTEM + "\n\n" + user_prompt,
                    ],
                    config=genai_types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=CriticVisualReport,
                    ),
                )
                text = response.text or "{}"
                parsed = json.loads(text)
                parsed["_model_used"] = mid
                return parsed
            except Exception as e:
                last_err = e
                continue
        raise GeminiVisionAPIFailed(
            f"critic_visual_evaluate_api_failed: todos los modelos fallaron — {last_err!s}"
        )

    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_sync_call), timeout=DEFAULT_TIMEOUT_S
        )
    except asyncio.TimeoutError as e:
        raise GeminiVisionAPIFailed(
            f"critic_visual_evaluate_api_failed: timeout {DEFAULT_TIMEOUT_S}s"
        ) from e


# ── API pública ──────────────────────────────────────────────────────────────


async def evaluate_landing(
    *,
    deploy_url: str,
    screenshot_path: Optional[str],
    brief_ctx: Dict[str, Any],
    modelo_elegido: str,
) -> CriticVisualReport:
    """
    Evalúa la landing visualmente.

    Estrategia:
    1. Si no hay screenshot → fallback heurístico inmediato.
    2. Si hay screenshot pero no GEMINI_API_KEY → fallback heurístico.
    3. Si Gemini Vision falla → fallback heurístico con razón.
    4. Si Gemini Vision OK → CriticVisualReport con score real.
    """
    started = time.perf_counter()

    if not screenshot_path:
        return _heuristic_fallback(
            deploy_url=deploy_url,
            modelo=modelo_elegido,
            reason="screenshot_no_disponible",
            started=started,
        )

    try:
        image_bytes = _read_image_bytes(screenshot_path)
    except GeminiVisionFailed as e:
        return _heuristic_fallback(
            deploy_url=deploy_url,
            modelo=modelo_elegido,
            reason=e.code,
            started=started,
        )

    try:
        parsed = await _call_gemini_vision(
            image_bytes=image_bytes,
            deploy_url=deploy_url,
            brief_ctx=brief_ctx,
            model_id=modelo_elegido,
        )
    except GeminiVisionFailed as e:
        logger.warning(
            "critic_visual_fallback",
            deploy_url=deploy_url,
            error=str(e),
            code=e.code,
        )
        return _heuristic_fallback(
            deploy_url=deploy_url,
            modelo=modelo_elegido,
            reason=e.code,
            started=started,
        )

    # Construir report a partir del JSON Gemini
    sub = parsed.get("sub_scores") or {}
    report = CriticVisualReport(
        score=int(parsed.get("score", 60)),
        sub_scores=CriticVisualSubScores(
            estetica=int(sub.get("estetica", 60)),
            cta_claridad=int(sub.get("cta_claridad", 60)),
            jerarquia_visual=int(sub.get("jerarquia_visual", 60)),
            profesionalismo=int(sub.get("profesionalismo", 60)),
        ),
        razones_aprobacion=list(parsed.get("razones_aprobacion") or []),
        razones_mejora=list(parsed.get("razones_mejora") or []),
        veredicto=str(parsed.get("veredicto") or "rework"),
        deploy_url=deploy_url,
        modelo_consultado=parsed.get("_model_used", modelo_elegido),
        source="gemini_vision",
        fallback_reason=None,
        evaluated_at=datetime.now(timezone.utc).isoformat(),
        duration_ms=int((time.perf_counter() - started) * 1000),
    )

    logger.info(
        "critic_visual_evaluated",
        deploy_url=deploy_url,
        score=report.score,
        modelo=report.modelo_consultado,
        duration_ms=report.duration_ms,
    )
    return report
