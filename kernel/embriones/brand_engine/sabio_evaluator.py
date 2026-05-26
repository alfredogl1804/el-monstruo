"""Sabio evaluator del Brand Engine — capa única de invocación al LLM evaluador.

Reutiliza ``router.engine.RouterEngine.execute()`` (patrón canónico ya usado
por ``kernel/deep_think_pipeline.py``) en vez de instanciar el SDK Anthropic
directamente. Esto:

1. Cumple DSC-G-004 (no se inventa wrapper paralelo cuando existe el canónico).
2. Hereda fallback automático (modelo principal → fallback heterogéneo) ya
   gestionado por el router.
3. Hereda cost accounting y observabilidad del Mainspring (DSC-MO-010).

Cada dimensión envía un prompt estructurado al Sabio configurado y espera una
respuesta JSON validable. El parser es tolerante a ruido (extrae el primer ``{``
balanceado, ignora preámbulos).

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T2-T5).
"""

from __future__ import annotations

import dataclasses
import json
import logging
import re
import time
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)


# ── Resultado canónico de una evaluación del Sabio ────────────────────────


@dataclasses.dataclass(frozen=True)
class SabioEvaluation:
    """Resultado parseado de una evaluación del Sabio sobre una dimensión.

    Atributos
    ---------
    score : float entre 0.0 y 1.0.
    reason : justificación textual emitida por el Sabio (1-3 frases).
    raw_response : texto completo retornado por el LLM (para auditoría).
    cost_usd : costo de esta evaluación específica.
    latency_ms : latencia en milisegundos.
    evaluator_llm : modelo efectivamente usado (puede ser fallback).
    error : str si hubo fallo de parsing o LLM (None si OK).
    """

    score: float
    reason: str
    raw_response: str
    cost_usd: float
    latency_ms: int
    evaluator_llm: str
    error: Optional[str]


# ── Cliente del Sabio ─────────────────────────────────────────────────────

_PROMPT_TEMPLATE = """Eres el Sabio Evaluador del Brand Engine del Monstruo.
Tu rol es asignar un score 0.0-1.0 a la respuesta candidata para la dimensión \
{dim_name}.

Criterios canónicos de esta dimensión:
{criterios_bullets}

Respuesta candidata a evaluar (delimitada por triple-backtick):
```
{respuesta}
```

Devuelve EXCLUSIVAMENTE un JSON con esta forma exacta (sin markdown, sin texto \
extra):
{{"score": <float 0.0-1.0>, "reason": "<1-3 frases explicando el score>"}}

Score 1.0 = la respuesta cumple plenamente los criterios.
Score 0.0 = la respuesta los viola completamente.
Sé estricto. Si la respuesta es genérica o pobre, score < 0.6."""


_JSON_OBJ_REGEX = re.compile(r"\{[^{}]*\}", re.DOTALL)


def _extract_json_object(text: str) -> Optional[dict]:
    """Extrae el primer objeto JSON balanceado del texto.

    Tolerante a preámbulos como ``Aquí está el JSON:`` o fences de markdown.
    Retorna None si no encuentra JSON parseable.
    """
    # Intento 1: parse directo del texto completo.
    try:
        return json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        pass

    # Intento 2: extraer dentro de ```json ... ``` fence.
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except (json.JSONDecodeError, ValueError):
            pass

    # Intento 3: primer { } balanceado.
    for match in _JSON_OBJ_REGEX.finditer(text):
        try:
            return json.loads(match.group(0))
        except (json.JSONDecodeError, ValueError):
            continue

    return None


async def evaluar_dimension_via_sabio(
    *,
    dim_name: str,
    respuesta_candidata: str,
    criterios: list[str],
    evaluator_llm: str,
    evaluator_fallback: Optional[str] = None,
) -> SabioEvaluation:
    """Invoca al Sabio para evaluar una dimensión específica.

    Parameters
    ----------
    dim_name : nombre canónico de la dimensión (``D1_brand_tono``, etc.).
    respuesta_candidata : texto a evaluar.
    criterios : lista de criterios del YAML para esta dimensión.
    evaluator_llm : modelo principal (ej. ``claude-opus-4-7``).
    evaluator_fallback : modelo de respaldo si el principal falla.

    Returns
    -------
    SabioEvaluation con score, reason, cost y latency.
    Si todo falla (incluyendo fallback), retorna score=0.5 (neutro) con error.
    """
    # Import diferido para evitar importar el router en CI sin secrets.
    from contracts.kernel_interface import IntentType
    from router.engine import RouterEngine

    criterios_bullets = "\n".join(f"  - {c}" for c in criterios)
    prompt = _PROMPT_TEMPLATE.format(
        dim_name=dim_name,
        criterios_bullets=criterios_bullets,
        respuesta=respuesta_candidata,
    )

    router = RouterEngine()
    t0 = time.perf_counter()
    text = ""
    usage: dict = {}
    used_llm = evaluator_llm
    error_msg: Optional[str] = None

    try:
        text, usage = await router.execute(
            message=prompt,
            model=evaluator_llm,
            intent=IntentType.SYSTEM,
            context={"system_prompt": "Eres el Sabio Evaluador del Brand Engine."},
        )
    except Exception as e1:
        log.warning(
            "brand_engine_evaluator_primary_failed",
            extra={"dim": dim_name, "model": evaluator_llm, "error": str(e1)[:200]},
        )
        if evaluator_fallback:
            try:
                text, usage = await router.execute(
                    message=prompt,
                    model=evaluator_fallback,
                    intent=IntentType.SYSTEM,
                    context={"system_prompt": "Eres el Sabio Evaluador del Brand Engine."},
                )
                used_llm = evaluator_fallback
            except Exception as e2:
                error_msg = f"primary={e1!s}; fallback={e2!s}"
                log.error(
                    "brand_engine_evaluator_fallback_failed",
                    extra={"dim": dim_name, "error": error_msg[:300]},
                )
        else:
            error_msg = str(e1)

    latency_ms = int((time.perf_counter() - t0) * 1000)
    cost_usd = float(usage.get("cost_usd", 0.0))

    if error_msg or not text:
        return SabioEvaluation(
            score=0.5,  # neutro — no bloquea ni aprueba en shadow/enforce.
            reason="Sabio inalcanzable — evaluación neutra por fail-open.",
            raw_response=text,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            evaluator_llm=used_llm,
            error=error_msg or "empty_response",
        )

    parsed = _extract_json_object(text)
    if parsed is None or "score" not in parsed:
        return SabioEvaluation(
            score=0.5,
            reason="Sabio respondió pero el JSON no fue parseable — neutro.",
            raw_response=text,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            evaluator_llm=used_llm,
            error="json_parse_failed",
        )

    try:
        score = float(parsed["score"])
        score = max(0.0, min(1.0, score))  # clip a [0, 1].
    except (TypeError, ValueError):
        score = 0.5

    reason = str(parsed.get("reason", ""))[:1000]

    return SabioEvaluation(
        score=score,
        reason=reason,
        raw_response=text,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        evaluator_llm=used_llm,
        error=None,
    )
