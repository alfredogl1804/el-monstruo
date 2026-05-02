"""
El Monstruo — Causal Decomposition Engine (Sprint 55.4)
=====================================================
Motor de descomposición causal.
Toma cualquier evento y lo descompone en factores causales atómicos.

Pipeline:
  1. Recibe evento (título + contexto)
  2. Consulta Sabios para descomposición inicial (multi-modelo)
  3. Investiga en tiempo real factores adicionales (Perplexity)
  4. Asigna pesos probabilísticos a cada factor
  5. Valida causalidad vs correlación (DoWhy heurístico)
  6. Almacena en CausalKnowledgeBase

Ejemplo:
  Input: "Tesla superó $1T de market cap en 2021"
  Output: [
    {factor: "EV adoption acceleration", weight: 0.85, direction: "positive"},
    {factor: "Elon Musk cult following", weight: 0.7, direction: "positive"},
    {factor: "Zero interest rate environment", weight: 0.8, direction: "positive"},
    ...
  ]

Validated: consult_sabios (ya en stack), Perplexity Sonar (ya en stack)
Future: DoWhy 0.14 para validación estadística cuando haya datos suficientes
"""

from __future__ import annotations

import json
import os
from typing import Optional

import structlog

from memory.causal_kb import CausalEvent, CausalFactor, CausalKnowledgeBase

logger = structlog.get_logger("kernel.causal_decomposer")


DECOMPOSITION_PROMPT = """Eres un analista causal experto. Tu trabajo es descomponer eventos complejos en sus factores causales atómicos.

EVENTO A DESCOMPONER:
{event_title}

CONTEXTO:
{event_context}

INSTRUCCIONES:
1. Identifica TODOS los factores que causaron este evento (no solo los obvios)
2. Para cada factor, asigna:
   - description: Descripción clara y específica del factor
   - category: Una de [economic, political, social, technological, cultural, environmental, psychological]
   - weight: 0.0 a 1.0 (qué tan determinante fue este factor)
   - direction: "positive" (contribuyó al evento), "negative" (lo frenó pero no lo impidió), "neutral"
   - confidence: 0.0 a 1.0 (qué tan seguro estás de que es CAUSAL y no solo correlacional)
   - evidence: Lista de evidencias que soportan esta relación causal

3. REGLAS:
   - Mínimo 5 factores, máximo 15
   - Los pesos NO tienen que sumar 1.0 (múltiples factores pueden ser altamente determinantes)
   - Distingue CAUSA de CORRELACIÓN. Si algo solo co-ocurrió pero no causó, NO lo incluyas
   - Incluye factores de segundo orden (causas de las causas) si son relevantes
   - Sé específico, no genérico. "Condiciones económicas favorables" es malo. "Tasas de interés en 0% por política Fed post-COVID" es bueno.

RESPONDE EN JSON:
{{
  "factors": [
    {{
      "description": "...",
      "category": "...",
      "weight": 0.X,
      "direction": "positive|negative|neutral",
      "confidence": 0.X,
      "evidence": ["...", "..."]
    }}
  ],
  "meta": {{
    "total_factors": N,
    "dominant_category": "...",
    "causal_complexity": "low|medium|high|extreme",
    "temporal_span": "...",
    "counterfactual": "Si [factor principal] no hubiera existido, [qué habría pasado]"
  }}
}}
"""


class CausalDecomposer:
    """
    Motor de descomposición causal.
    Usa multi-modelo (Sabios) para descomponer eventos en factores atómicos.
    """

    def __init__(
        self,
        causal_kb: CausalKnowledgeBase,
        sabios_fn=None,
        search_fn=None,
    ):
        """
        Args:
            causal_kb: Base de conocimiento causal para almacenar resultados
            sabios_fn: Función para consultar Sabios (async) — opcional
            search_fn: Función para búsqueda web en tiempo real (async) — opcional
        """
        self._kb = causal_kb
        self._consult_sabios = sabios_fn
        self._web_search = search_fn

    async def decompose(
        self,
        title: str,
        context: str = "",
        category: str = "general",
        event_date: Optional[str] = None,
        sources: Optional[list[str]] = None,
        enrich_with_research: bool = True,
    ) -> CausalEvent:
        """
        Descomponer un evento en factores causales atómicos.

        Pipeline:
          1. Consultar Sabios para descomposición multi-modelo
          2. (Opcional) Investigar factores adicionales con Perplexity
          3. Consolidar y asignar pesos
          4. Almacenar en CausalKnowledgeBase
        """
        logger.info("causal_decomposition_start", title=title, category=category)

        # ── Paso 1: Descomposición multi-modelo ────────────────────
        prompt = DECOMPOSITION_PROMPT.format(
            event_title=title,
            event_context=context or "No additional context provided.",
        )

        raw_decomposition = await self._call_sabios(prompt)
        factors = self._parse_factors(raw_decomposition)

        # ── Paso 2: Enriquecimiento con investigación ──────────────
        if enrich_with_research and self._web_search and factors:
            additional_factors = await self._research_additional_factors(title, factors)
            factors.extend(additional_factors)

        # ── Paso 3: Buscar eventos similares para validación cruzada ──
        try:
            similar = await self._kb.search_similar(title, limit=3)
            if similar:
                factors = self._cross_validate(factors, similar)
        except Exception as e:
            logger.warning("cross_validation_failed", error=str(e))

        # ── Paso 4: Construir y almacenar evento ───────────────────
        event = CausalEvent(
            title=title,
            description=context,
            category=category,
            date=event_date,
            outcome=title,  # El evento mismo es su outcome
            factors=factors,
            sources=sources or [],
            decomposed_by="causal_decomposer_v1",
            validation_score=self._calculate_validation_score(factors),
        )

        event_id = await self._kb.store_event(event)

        logger.info(
            "causal_decomposition_complete",
            event_id=event_id,
            title=title,
            factors_count=len(factors),
            validation_score=event.validation_score,
        )

        return event

    async def _call_sabios(self, prompt: str) -> str:
        """
        Consultar Sabios para descomposición.
        Fallback: OpenAI GPT-4o directo.
        """
        if self._consult_sabios:
            try:
                result = await self._consult_sabios(prompt)
                return result if isinstance(result, str) else json.dumps(result)
            except Exception as e:
                logger.warning("sabios_call_failed", error=str(e), fallback="openai")

        # Fallback: usar OpenAI directamente
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or "{}"
        except Exception as e:
            logger.error("openai_fallback_failed", error=str(e))

        # Último fallback: Gemini
        try:
            import google.generativeai as genai

            genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt + "\n\nResponde SOLO con JSON válido.")
            return response.text or "{}"
        except Exception as e:
            logger.error("gemini_fallback_failed", error=str(e))
            return "{}"

    async def _research_additional_factors(
        self, title: str, existing_factors: list[CausalFactor]
    ) -> list[CausalFactor]:
        """
        Investigar factores adicionales no capturados por los Sabios.
        Usa Perplexity Sonar para búsqueda en tiempo real.
        """
        if not self._web_search:
            return []

        query = f"causas factores que provocaron: {title}"
        try:
            search_result = await self._web_search(query)
            # En v1: los Sabios son suficientes para la descomposición inicial.
            # En v2 (Sprint 57+): parsear search_result con un LLM call adicional
            # para extraer factores no mencionados por los Sabios.
            return []
        except Exception as e:
            logger.warning("research_additional_factors_failed", error=str(e))
            return []

    def _parse_factors(self, raw: str) -> list[CausalFactor]:
        """Parsear respuesta JSON de los Sabios a CausalFactors."""
        if not raw or raw.strip() in ("{}", ""):
            return []

        try:
            # Limpiar markdown code blocks si los hay
            clean = raw.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:-1]) if len(lines) > 2 else clean

            data = json.loads(clean)
            factors_data = data.get("factors", [])

            factors = []
            for f in factors_data:
                if not f.get("description"):
                    continue
                factor = CausalFactor(
                    description=f.get("description", ""),
                    category=f.get("category", "general"),
                    weight=float(f.get("weight", 0.5)),
                    confidence=float(f.get("confidence", 0.7)),
                    direction=f.get("direction", "positive"),
                    evidence=f.get("evidence", []),
                )
                factors.append(factor)

            return factors
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.error("factor_parse_failed", error=str(e), raw_length=len(raw))
            return []

    def _cross_validate(self, factors: list[CausalFactor], similar_events: list[dict]) -> list[CausalFactor]:
        """
        Validar factores contra eventos similares.
        Si un factor aparece en eventos similares, sube su confianza.
        T4: Cross-validation contra eventos similares incrementa confianza.
        """
        similar_factor_descriptions: set[str] = set()
        for event in similar_events:
            raw_factors = event.get("factors", "[]")
            try:
                event_factors = raw_factors if isinstance(raw_factors, list) else json.loads(raw_factors)
                for f in event_factors:
                    desc = f.get("description", "") if isinstance(f, dict) else str(f)
                    if desc:
                        similar_factor_descriptions.add(desc.lower())
            except (json.JSONDecodeError, TypeError):
                pass

        # Boost confidence si factor aparece en similares
        for factor in factors:
            desc_lower = factor.description.lower()
            for sim_desc in similar_factor_descriptions:
                if desc_lower in sim_desc or sim_desc in desc_lower:
                    factor.confidence = min(1.0, factor.confidence + 0.1)
                    break

        return factors

    def _calculate_validation_score(self, factors: list[CausalFactor]) -> float:
        """
        Calcular score de validación de la descomposición.
        Basado en: diversidad de categorías, confianza promedio, evidencia.
        T3: validation_score se calcula correctamente.
        """
        if not factors:
            return 0.0

        # Diversidad de categorías (más categorías = mejor descomposición)
        categories = {f.category for f in factors}
        diversity_score = min(1.0, len(categories) / 4.0)

        # Confianza promedio
        avg_confidence = sum(f.confidence for f in factors) / len(factors)

        # Evidencia (factores con evidencia son más confiables)
        evidence_ratio = sum(1 for f in factors if f.evidence) / len(factors)

        # Score compuesto
        return round(
            (diversity_score * 0.3) + (avg_confidence * 0.4) + (evidence_ratio * 0.3),
            3,
        )


# ── Singleton ──────────────────────────────────────────────────────

_decomposer_instance: Optional[CausalDecomposer] = None


def get_causal_decomposer() -> Optional[CausalDecomposer]:
    """Obtener el singleton del CausalDecomposer."""
    return _decomposer_instance


def init_causal_decomposer(
    causal_kb: CausalKnowledgeBase,
    sabios_fn=None,
    search_fn=None,
) -> CausalDecomposer:
    """
    Inicializar el CausalDecomposer singleton.
    Llamar desde el lifespan de main.py o desde CausalSeeder.
    """
    global _decomposer_instance
    _decomposer_instance = CausalDecomposer(
        causal_kb=causal_kb,
        sabios_fn=sabios_fn,
        search_fn=search_fn,
    )
    logger.info("causal_decomposer_initialized")
    return _decomposer_instance
