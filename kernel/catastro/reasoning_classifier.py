"""
El Catastro · Reasoning Classifier (Sprint 86.7).

LLM-as-classifier que asigna subcapacidades de razonamiento estructurado
a un modelo basándose en sus scores en AIME, GPQA Diamond y MMLU-Pro.

Vocabulario controlado de 13 tags (Sprint 86.7 — firma Cowork):
  - 12 tags ortogonales al vocabulario coding (sin solapamiento)
  - +1 tag 'reasoning-overfit-suspected' del anti-gaming v2 cross-area

Patrón: simétrico al coding_classifier — LLM-as-parser con Structured
Outputs Pydantic (39va semilla). Capa Memento: si OPENAI_API_KEY no está
disponible, degrada a heuristic mode determinístico.

[Hilo Manus Catastro] · Sprint 86.7 · 2026-05-05
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


# ============================================================================
# VOCABULARIO CONTROLADO 13 TAGS DE RAZONAMIENTO ESTRUCTURADO
# ============================================================================
# 12 base + 1 anti-gaming v2 cross-area. Ortogonal al vocabulario coding.
REASONING_TAGS_VOCABULARY = (
    # Áreas (6)
    "math-strong",
    "physics-strong",
    "chemistry-strong",
    "biology-strong",
    "logic-formal-strong",
    "multidominio-strong",
    # Estilos (6)
    "step-by-step-reasoning",
    "chain-of-thought-strong",
    "abstract-reasoning",
    "quantitative-strong",
    "structured-output-strong",
    "anti-gaming-reasoning-verified",
    # Anti-gaming v2 cross-area (1)
    "reasoning-overfit-suspected",
)


# ============================================================================
# STRUCTURED OUTPUT SCHEMA (39va semilla - LLM-as-parser Pydantic)
# ============================================================================

class ReasoningClassification(BaseModel):
    """Output estructurado del reasoning classifier."""

    tags: list[str] = Field(
        ...,
        description="Subcapacidades de razonamiento del vocabulario de 13."
    )
    primary_strength: str = Field(
        ...,
        description="Fortaleza principal del modelo en razonamiento estructurado."
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confianza del classifier en 0-1."
    )
    reasoning: str = Field(
        ...,
        description="Razonamiento corto del classifier (1-2 oraciones)."
    )


# ============================================================================
# REASONING CLASSIFIER
# ============================================================================

class ReasoningClassifier:
    """
    Clasificador de subcapacidades de razonamiento estructurado.

    Input: scores normalizados {aime, gpqa, mmlu_pro}
    Output: ReasoningClassification con tags del vocabulario controlado.
    """

    def __init__(self, *, use_llm: bool = True) -> None:
        """
        Args:
            use_llm: Si True, intenta usar LLM-as-classifier (Pydantic structured).
                     Si False o LLM no disponible, usa heuristic mode.
        """
        self.use_llm = use_llm

    def classify(
        self,
        modelo_id: str,
        scores: dict[str, Optional[float]],
        gaming_detected: bool = False,
    ) -> ReasoningClassification:
        """
        Asigna subcapacidades de razonamiento a un modelo.

        Args:
            modelo_id: slug del modelo.
            scores: dict con keys 'aime', 'gpqa', 'mmlu_pro' (opcional cada una).
            gaming_detected: si True, NO agrega 'anti-gaming-reasoning-verified'.

        Returns:
            ReasoningClassification con tags, fortaleza principal, confianza, razonamiento.
        """
        if self.use_llm and self._llm_available():
            try:
                return self._classify_with_llm(modelo_id, scores, gaming_detected)
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    f"[reasoning_classifier] LLM falló para {modelo_id}, "
                    f"fallback heuristic: {e}"
                )
                return self._classify_heuristic(modelo_id, scores, gaming_detected)
        else:
            return self._classify_heuristic(modelo_id, scores, gaming_detected)

    def _llm_available(self) -> bool:
        """Capa Memento: lee env var en runtime, nunca cachea."""
        return bool(os.environ.get("OPENAI_API_KEY"))

    def _classify_with_llm(
        self,
        modelo_id: str,
        scores: dict[str, Optional[float]],
        gaming_detected: bool,
    ) -> ReasoningClassification:
        """LLM-as-parser con Structured Outputs Pydantic (39va semilla)."""
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError("catastro_reasoning_classify_openai_sdk_missing") from e

        client = OpenAI()
        prompt = self._build_prompt(modelo_id, scores, gaming_detected)

        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",  # ligero y barato para classifier
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sos un experto en clasificación de modelos LLM por capacidades de "
                        "razonamiento estructurado (matemática AIME, ciencias GPQA Diamond, "
                        "conocimiento estructurado MMLU-Pro). Devolvés output estricto en el schema."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format=ReasoningClassification,
        )

        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise RuntimeError("catastro_reasoning_classify_llm_returned_none")

        # Validar tags contra vocabulario controlado (whitelist)
        valid_tags = [t for t in parsed.tags if t in REASONING_TAGS_VOCABULARY]
        if len(valid_tags) != len(parsed.tags):
            invalid = set(parsed.tags) - set(REASONING_TAGS_VOCABULARY)
            logger.warning(
                f"[reasoning_classifier] Tags inválidos descartados para "
                f"{modelo_id}: {invalid}"
            )
            parsed.tags = valid_tags

        return parsed

    def _classify_heuristic(
        self,
        modelo_id: str,
        scores: dict[str, Optional[float]],
        gaming_detected: bool,
    ) -> ReasoningClassification:
        """Fallback heuristic determinístico si LLM no disponible."""
        tags: list[str] = []
        primary = "general-reasoning"

        aime = scores.get("aime") or 0.0
        gpqa = scores.get("gpqa") or 0.0
        mmlu_pro = scores.get("mmlu_pro") or 0.0

        # Heuristics por área
        if aime >= 70.0:
            tags.append("math-strong")
            tags.append("quantitative-strong")
            primary = "math-strong"
        if gpqa >= 70.0:
            # GPQA cubre física, química y biología — usamos multidominio cuando alto
            tags.append("multidominio-strong")
            if not primary or primary == "general-reasoning":
                primary = "multidominio-strong"
        if mmlu_pro >= 70.0:
            tags.append("structured-output-strong")
            tags.append("multidominio-strong")

        # Estilo: razonamiento estructurado fuerte si todos altos
        if aime >= 60.0 and gpqa >= 60.0:
            tags.append("step-by-step-reasoning")
            tags.append("chain-of-thought-strong")

        if mmlu_pro >= 60.0 and aime >= 50.0:
            tags.append("abstract-reasoning")

        # Anti-gaming verified
        if not gaming_detected and (aime >= 50.0 or gpqa >= 50.0 or mmlu_pro >= 50.0):
            tags.append("anti-gaming-reasoning-verified")

        # Deduplicar preservando orden
        seen: set[str] = set()
        deduped = []
        for t in tags:
            if t not in seen:
                seen.add(t)
                deduped.append(t)
        tags = deduped

        # Default si nada matcheó
        if not tags:
            tags = ["multidominio-strong"]

        confidence = 0.5  # heuristic = confianza baja
        reasoning_text = (
            f"Heuristic: AIME={aime:.1f}, GPQA={gpqa:.1f}, MMLU-Pro={mmlu_pro:.1f}. "
            f"Gaming={gaming_detected}."
        )

        return ReasoningClassification(
            tags=tags,
            primary_strength=primary,
            confidence=confidence,
            reasoning=reasoning_text,
        )

    @staticmethod
    def detect_overfit_reasoning_cross_area(
        aime_score: Optional[float],
        gpqa_score: Optional[float],
        mmlu_pro_score: Optional[float],
        coding_score: Optional[float],
        razonamiento_general: Optional[float],
        arena_rank: Optional[int],
    ) -> tuple[bool, dict[str, Any]]:
        """
        Regla anti-gaming v2 cross-area Reasoning (Sprint 86.7).

        Detecta overfit INTER-macroárea: modelo "memorizador de benchmarks de
        razonamiento" pero que no aplica el razonamiento a coding ni rinde en
        Arena humana.

        Criterio firme:
        - Reasoning-strong: max(aime, gpqa, mmlu_pro) >= 70.0 (al menos 1 de los 3)
        - Y al menos UNA condición de overfit:
            (a) coding_score < 30.0 (razonamiento sin transferencia a código)
            (b) arena_rank > 50 (razonamiento sin valor humano percibido)
            (c) razonamiento_general < 40.0 (incoherencia interna macroárea 1 vs 4)

        Returns:
            (is_overfit, evidence_dict)
        """
        evidence: dict[str, Any] = {
            "aime": aime_score,
            "gpqa": gpqa_score,
            "mmlu_pro": mmlu_pro_score,
            "coding": coding_score,
            "razonamiento_general": razonamiento_general,
            "arena_rank": arena_rank,
        }

        # Calcular reasoning-strong (al menos 1 de 3 >= 70)
        reasoning_max = max(
            (s for s in [aime_score, gpqa_score, mmlu_pro_score] if s is not None),
            default=None,
        )
        if reasoning_max is None or reasoning_max < 70.0:
            return False, evidence

        # Verificar condiciones de overfit cross-area
        reasons: list[str] = []
        if coding_score is not None and coding_score < 30.0:
            reasons.append("reasoning_high_but_coding_low")
        if arena_rank is not None and arena_rank > 50:
            reasons.append("reasoning_high_but_arena_rank_low")
        if razonamiento_general is not None and razonamiento_general < 40.0:
            reasons.append("reasoning_high_but_general_reasoning_low")

        if reasons:
            evidence["reason"] = reasons[0]  # primary reason
            evidence["all_reasons"] = reasons
            return True, evidence

        return False, evidence

    def _build_prompt(
        self,
        modelo_id: str,
        scores: dict[str, Optional[float]],
        gaming_detected: bool,
    ) -> str:
        vocab_str = ", ".join(REASONING_TAGS_VOCABULARY)
        return (
            f"Modelo: {modelo_id}\n"
            f"Scores Macroárea 4 (Razonamiento Estructurado):\n"
            f"  - AIME (matemática competitiva): {scores.get('aime')}\n"
            f"  - GPQA Diamond (física/química/biología PhD-level): {scores.get('gpqa')}\n"
            f"  - MMLU-Pro (conocimiento estructurado multidominio): {scores.get('mmlu_pro')}\n"
            f"Gaming detectado (intra-fuente v1): {gaming_detected}\n\n"
            f"Vocabulario controlado de tags (USAR SOLO ESTOS): {vocab_str}\n\n"
            f"Asigná 2-5 tags relevantes basados en los scores. "
            f"Si gaming_detected=True, NO uses 'anti-gaming-reasoning-verified'. "
            f"Si reasoning_max >= 70 y los otros indicadores son bajos, podés "
            f"considerar 'reasoning-overfit-suspected' (el caller también puede "
            f"agregarlo automáticamente vía detect_overfit_reasoning_cross_area). "
            f"Identificá la fortaleza principal entre las 6 áreas."
        )
