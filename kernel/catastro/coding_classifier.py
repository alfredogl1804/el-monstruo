"""
El Catastro · Coding Classifier.

LLM-as-classifier que asigna subcapacidades de coding a un modelo
basándose en sus scores en SWE-bench, HumanEval+ y MBPP.

Vocabulario controlado de 15 tags (Sprint 86.5 — firma Cowork).
Patrón: LLM-as-parser con Structured Outputs Pydantic — esquiva regex
(35va semilla + 39va semilla del trío).

Capa Memento:
- Si el modelo OPENAI_API_KEY no está disponible, el classifier degrada
  a heuristic mode (basado en scores numéricos).
- LLM-as-classifier es preferido pero opcional para evitar bloqueos.

[Hilo Manus Catastro] · Sprint 86.5 · 2026-05-05
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


# ============================================================================
# VOCABULARIO CONTROLADO 15 TAGS DE CODING
# ============================================================================
# Firma Cowork audit del trío A+B+C — anti-saturación + cobertura amplia
CODING_TAGS_VOCABULARY = (
    # Lenguajes
    "python-strong",
    "javascript-strong",
    "typescript-strong",
    "rust-capable",
    "go-capable",
    # Tareas
    "bug-fix",
    "feature-implementation",
    "refactor",
    "code-review",
    "documentation",
    # Estilos
    "agentic-coding",
    "long-context-coding",
    "test-generation",
    "anti-gaming-verified",
    "competitive-programming",
)


# ============================================================================
# STRUCTURED OUTPUT SCHEMA (39va semilla)
# ============================================================================

class CodingClassification(BaseModel):
    """Output estructurado del classifier."""
    
    tags: list[str] = Field(
        ...,
        description="Subcapacidades de coding asignadas, del vocabulario de 15."
    )
    primary_strength: str = Field(
        ...,
        description="Fortaleza principal del modelo en coding."
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confianza del classifier en 0-1."
    )
    reasoning: str = Field(
        ...,
        description="Razonamiento corto (1-2 oraciones)."
    )


# ============================================================================
# CODING CLASSIFIER
# ============================================================================

class CodingClassifier:
    """
    Clasificador de subcapacidades coding.
    
    Input: scores normalizados {swe_bench: float, human_eval: float, mbpp: float}
    Output: CodingClassification con tags del vocabulario controlado.
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
    ) -> CodingClassification:
        """
        Asigna subcapacidades coding a un modelo basándose en sus scores.
        
        Args:
            modelo_id: slug del modelo.
            scores: dict con keys 'swe_bench', 'human_eval', 'mbpp' (opcional cada una).
            gaming_detected: si True, agrega tag 'anti-gaming-verified' si NO hay gaming.
        
        Returns:
            CodingClassification con tags, fortaleza principal, confianza, razonamiento.
        """
        if self.use_llm and self._llm_available():
            try:
                return self._classify_with_llm(modelo_id, scores, gaming_detected)
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    f"[coding_classifier] LLM falló para {modelo_id}, fallback heuristic: {e}"
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
    ) -> CodingClassification:
        """LLM-as-parser con Structured Outputs Pydantic (39va semilla)."""
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError("openai SDK no instalado") from e

        client = OpenAI()
        prompt = self._build_prompt(modelo_id, scores, gaming_detected)

        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",  # ligero y barato para classifier
            messages=[
                {"role": "system", "content": "Sos un experto en clasificación de modelos LLM por capacidades de coding. Devolvés output estricto en el schema."},
                {"role": "user", "content": prompt},
            ],
            response_format=CodingClassification,
        )

        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise RuntimeError("LLM devolvió None en structured parse")
        
        # Validar tags contra vocabulario controlado
        valid_tags = [t for t in parsed.tags if t in CODING_TAGS_VOCABULARY]
        if len(valid_tags) != len(parsed.tags):
            invalid = set(parsed.tags) - set(CODING_TAGS_VOCABULARY)
            logger.warning(
                f"[coding_classifier] Tags inválidos descartados para {modelo_id}: {invalid}"
            )
            parsed.tags = valid_tags

        return parsed

    def _classify_heuristic(
        self,
        modelo_id: str,
        scores: dict[str, Optional[float]],
        gaming_detected: bool,
    ) -> CodingClassification:
        """Fallback heuristic si LLM no disponible."""
        tags: list[str] = []
        primary = "general-coding"
        
        swe = scores.get("swe_bench") or 0.0
        he = scores.get("human_eval") or 0.0
        mbpp = scores.get("mbpp") or 0.0
        
        # Heuristics simples basadas en scores
        if swe >= 40.0:
            tags.append("agentic-coding")
            tags.append("bug-fix")
            primary = "agentic-coding"
        if he >= 80.0:
            tags.append("python-strong")
        if mbpp >= 80.0:
            tags.append("feature-implementation")
        if swe >= 50.0 and not gaming_detected:
            tags.append("anti-gaming-verified")
        if he >= 90.0 and mbpp >= 90.0:
            tags.append("competitive-programming")
        
        # Default si nada matcheó
        if not tags:
            tags = ["python-strong"]
        
        confidence = 0.5  # heuristic = baja confianza
        reasoning = (
            f"Heuristic mode: SWE={swe:.1f}, HE={he:.1f}, MBPP={mbpp:.1f}. "
            f"Gaming={gaming_detected}."
        )
        
        return CodingClassification(
            tags=tags,
            primary_strength=primary,
            confidence=confidence,
            reasoning=reasoning,
        )

    def _build_prompt(
        self,
        modelo_id: str,
        scores: dict[str, Optional[float]],
        gaming_detected: bool,
    ) -> str:
        vocab_str = ", ".join(CODING_TAGS_VOCABULARY)
        return (
            f"Modelo: {modelo_id}\n"
            f"Scores:\n"
            f"  - SWE-bench Verified: {scores.get('swe_bench')}\n"
            f"  - HumanEval+: {scores.get('human_eval')}\n"
            f"  - MBPP+: {scores.get('mbpp')}\n"
            f"Gaming detectado: {gaming_detected}\n\n"
            f"Vocabulario controlado de tags (USAR SOLO ESTOS): {vocab_str}\n\n"
            f"Asigná 2-5 tags relevantes basados en los scores. "
            f"Si gaming_detected=True, NO uses 'anti-gaming-verified'. "
            f"Identificá la fortaleza principal."
        )
