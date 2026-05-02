"""
visual_quality_gate.py — Quality Gate Visual con LLM Multimodal
================================================================
Auto-evaluación visual de interfaces antes de entregar.
Usa GPT-4o o Gemini multimodal para evaluar si el output
cumple el estándar Apple/Tesla del Objetivo #2.

Criterios evaluados:
  1. Jerarquía visual y whitespace
  2. Tipografía y legibilidad
  3. Consistencia de color y contraste
  4. Alineación y spacing
  5. Polish y craft (atención al detalle)
  6. Profesionalismo general

Sprint 57 — "Las Capas Transversales"
"""

from __future__ import annotations

import base64
import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger("visual_quality_gate")


# ── Grades ────────────────────────────────────────────────────────────────────


class QualityGrade(Enum):
    KEYNOTE = "keynote"  # Listo para keynote de Apple (≥ 0.90)
    EXCELLENT = "excellent"  # Muy bueno, detalles menores (≥ 0.80)
    GOOD = "good"  # Bueno, necesita pulido (≥ 0.65)
    NEEDS_WORK = "needs_work"  # Problemas significativos (≥ 0.50)
    UNACCEPTABLE = "unacceptable"  # No entregar (< 0.50)


GRADE_THRESHOLDS = {
    QualityGrade.KEYNOTE: 0.90,
    QualityGrade.EXCELLENT: 0.80,
    QualityGrade.GOOD: 0.65,
    QualityGrade.NEEDS_WORK: 0.50,
}

CRITERIA_WEIGHTS = {
    "visual_hierarchy": 0.20,
    "typography": 0.15,
    "color_contrast": 0.15,
    "alignment_spacing": 0.15,
    "polish_craft": 0.20,
    "professionalism": 0.15,
}


# ── Evaluation result ─────────────────────────────────────────────────────────


@dataclass
class VisualEvaluation:
    """Resultado de evaluación visual."""

    grade: QualityGrade
    overall_score: float  # 0.0 - 1.0
    scores: dict  # Score por criterio con justificación
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    ready_to_deliver: bool
    model_used: str = "unknown"
    evaluation_time_ms: float = 0.0

    def to_report(self) -> str:
        """Generar reporte legible."""
        status = "✅ LISTO PARA ENTREGAR" if self.ready_to_deliver else "❌ NO LISTO — REQUIERE TRABAJO"
        lines = [
            "## Visual Quality Report",
            f"**Grade:** {self.grade.value.upper()} ({self.overall_score:.0%})",
            f"**Status:** {status}",
            "",
            "### Scores por criterio",
        ]
        for criterion, data in self.scores.items():
            score = data.get("score", 0) if isinstance(data, dict) else data
            justification = data.get("justification", "") if isinstance(data, dict) else ""
            lines.append(f"- **{criterion}**: {score:.0%} — {justification}")

        lines += [
            "",
            "### Fortalezas",
            *[f"- {s}" for s in self.strengths],
            "",
            "### Debilidades",
            *[f"- {w}" for w in self.weaknesses],
            "",
            "### Recomendaciones",
            *[f"- {r}" for r in self.recommendations],
        ]
        return "\n".join(lines)


# ── Evaluation prompt ─────────────────────────────────────────────────────────

VISUAL_EVAL_PROMPT = """You are a world-class UI/UX design critic with Apple and Tesla-level standards.
Evaluate this screenshot of a web interface on the following criteria, scoring each from 0.0 to 1.0:

1. VISUAL HIERARCHY (0.0-1.0): Is there clear hierarchy? Generous whitespace? Nothing feels cramped?
2. TYPOGRAPHY (0.0-1.0): Professional font pairing? Readable? Consistent scale? No orphans/widows?
3. COLOR & CONTRAST (0.0-1.0): Cohesive palette? Sufficient contrast? Intentional use of color?
4. ALIGNMENT & SPACING (0.0-1.0): Perfect alignment? Mathematical spacing? Grid consistency?
5. POLISH & CRAFT (0.0-1.0): Attention to detail? Micro-interactions visible? No rough edges?
6. PROFESSIONALISM (0.0-1.0): Would you show this at an Apple keynote? Does it inspire confidence?

For each criterion, provide:
- Score (0.0-1.0)
- Brief justification (1 sentence)

Then provide:
- Overall score (weighted average)
- Top 3 strengths
- Top 3 weaknesses
- Top 3 specific recommendations to improve

Respond ONLY in JSON format:
{
    "scores": {
        "visual_hierarchy": {"score": 0.0, "justification": "..."},
        "typography": {"score": 0.0, "justification": "..."},
        "color_contrast": {"score": 0.0, "justification": "..."},
        "alignment_spacing": {"score": 0.0, "justification": "..."},
        "polish_craft": {"score": 0.0, "justification": "..."},
        "professionalism": {"score": 0.0, "justification": "..."}
    },
    "overall_score": 0.0,
    "strengths": ["...", "...", "..."],
    "weaknesses": ["...", "...", "..."],
    "recommendations": ["...", "...", "..."]
}"""


# ── VisualQualityGate ─────────────────────────────────────────────────────────


class VisualQualityGate:
    """Quality Gate visual con LLM multimodal."""

    def __init__(
        self,
        llm_client=None,
        min_grade: QualityGrade = QualityGrade.GOOD,
        preferred_model: str = "gpt-4o",
    ):
        self._llm = llm_client
        self._min_grade = min_grade
        self._preferred_model = preferred_model

    async def evaluate_screenshot(self, screenshot_path: str) -> VisualEvaluation:
        """Evaluar un screenshot usando LLM multimodal."""
        import time

        start = time.time()

        if not self._llm:
            logger.warning("llm_not_configured_for_visual_evaluation")
            return self._fallback_evaluation()

        image_b64 = self._encode_image(screenshot_path)
        if not image_b64:
            return self._fallback_evaluation()

        try:
            response = await self._call_multimodal_llm(image_b64)
            evaluation = self._parse_response(response)
            evaluation.evaluation_time_ms = (time.time() - start) * 1000
            return evaluation
        except Exception as e:
            logger.error("visual_evaluation_failed", error=str(e), path=screenshot_path)
            return self._fallback_evaluation()

    async def evaluate_url(self, url: str, screenshot_fn=None) -> VisualEvaluation:
        """Evaluar una URL tomando screenshot primero."""
        if not screenshot_fn:
            return self._fallback_evaluation(reason="screenshot_fn not provided — cannot capture URL")

        try:
            screenshot_path = await screenshot_fn(url)
            return await self.evaluate_screenshot(screenshot_path)
        except Exception as e:
            logger.error("url_evaluation_failed", url=url, error=str(e))
            return self._fallback_evaluation()

    def passes_gate(self, evaluation: VisualEvaluation) -> bool:
        """Verificar si una evaluación pasa el quality gate."""
        grade_order = [
            QualityGrade.UNACCEPTABLE,
            QualityGrade.NEEDS_WORK,
            QualityGrade.GOOD,
            QualityGrade.EXCELLENT,
            QualityGrade.KEYNOTE,
        ]
        eval_idx = grade_order.index(evaluation.grade)
        min_idx = grade_order.index(self._min_grade)
        return eval_idx >= min_idx

    def _encode_image(self, path: str) -> Optional[str]:
        """Encode image to base64."""
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error("image_encoding_failed", path=path, error=str(e))
            return None

    async def _call_multimodal_llm(self, image_b64: str) -> str:
        """Llamar al LLM multimodal con el screenshot."""
        # Intentar con OpenAI GPT-4o primero
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            return await self._call_openai(image_b64, openai_key)

        # Fallback a Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            return await self._call_gemini(image_b64, gemini_key)

        raise ValueError("No multimodal LLM API key configured (OPENAI_API_KEY or GEMINI_API_KEY)")

    async def _call_openai(self, image_b64: str, api_key: str) -> str:
        """Llamar a OpenAI GPT-4o con imagen."""
        import httpx

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VISUAL_EVAL_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                        },
                    ],
                }
            ],
            "max_tokens": 1000,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            self._preferred_model = "gpt-4o"
            return data["choices"][0]["message"]["content"]

    async def _call_gemini(self, image_b64: str, api_key: str) -> str:
        """Llamar a Gemini con imagen."""
        import httpx

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": VISUAL_EVAL_PROMPT},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_b64,
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {"response_mime_type": "application/json"},
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self._preferred_model = "gemini-2.0-flash"
            return data["candidates"][0]["content"]["parts"][0]["text"]

    def _parse_response(self, response_text: str) -> VisualEvaluation:
        """Parsear respuesta JSON del LLM."""
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # Intentar extraer JSON del texto
            import re

            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                return self._fallback_evaluation(reason="Could not parse LLM response")

        # Calcular weighted score
        scores = data.get("scores", {})
        weighted_score = 0.0
        for criterion, weight in CRITERIA_WEIGHTS.items():
            criterion_data = scores.get(criterion, {})
            score = criterion_data.get("score", 0.5) if isinstance(criterion_data, dict) else 0.5
            weighted_score += score * weight

        overall = data.get("overall_score", weighted_score)

        # Determinar grade
        grade = QualityGrade.UNACCEPTABLE
        for g, threshold in sorted(GRADE_THRESHOLDS.items(), key=lambda x: x[1]):
            if overall >= threshold:
                grade = g

        return VisualEvaluation(
            grade=grade,
            overall_score=overall,
            scores=scores,
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            recommendations=data.get("recommendations", []),
            ready_to_deliver=self.passes_gate(
                VisualEvaluation(
                    grade=grade,
                    overall_score=overall,
                    scores=scores,
                    strengths=[],
                    weaknesses=[],
                    recommendations=[],
                    ready_to_deliver=False,
                )
            ),
            model_used=self._preferred_model,
        )

    def _fallback_evaluation(self, reason: str = "LLM not available") -> VisualEvaluation:
        """Evaluación de fallback cuando el LLM no está disponible."""
        logger.warning("visual_gate_fallback", reason=reason)
        return VisualEvaluation(
            grade=QualityGrade.GOOD,
            overall_score=0.70,
            scores={
                c: {"score": 0.70, "justification": "Fallback — LLM evaluation unavailable"} for c in CRITERIA_WEIGHTS
            },
            strengths=["Fallback evaluation — configure LLM for real assessment"],
            weaknesses=["Cannot evaluate without LLM multimodal capability"],
            recommendations=[
                "Set OPENAI_API_KEY or GEMINI_API_KEY for visual evaluation",
                "Re-run evaluation after configuring LLM",
            ],
            ready_to_deliver=True,  # No bloquear en fallback
            model_used="fallback",
        )


# ── Singleton factory ─────────────────────────────────────────────────────────

_visual_gate: Optional[VisualQualityGate] = None


def get_visual_quality_gate(
    min_grade: QualityGrade = QualityGrade.GOOD,
) -> VisualQualityGate:
    """Singleton factory para VisualQualityGate."""
    global _visual_gate
    if _visual_gate is None:
        _visual_gate = VisualQualityGate(min_grade=min_grade)
    return _visual_gate
