"""
Embrión Técnico — análisis técnico de viabilidad de un brief de producto.

Responsabilidad:
  - Stack tech recomendado (frontend, backend, hosting, deploy_target)
  - Complejidad estimada (1-5)
  - Riesgos técnicos detectados con severidad y mitigación
  - Output: `EmbrionTecnicoReport` Pydantic estricto

Patrón LLM-as-parser con Structured Outputs Pydantic (39va semilla):
  - Si OPENAI_API_KEY presente → `client.beta.chat.completions.parse` con
    `response_format=EmbrionTecnicoReport`
  - Si OPENAI_API_KEY ausente → fallback heurístico determinístico

Capa Memento:
  - Lee env var en runtime, NO cachea
  - Brand DNA: `embrion_tecnico_llm_invalido`, `embrion_tecnico_llm_unavailable`

[Hilo Manus Memento — Ejecutor] · Sprint 87.1 Bloque 1 · 2026-05-05
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


logger = logging.getLogger(__name__)


# ============================================================================
# ERRORES CON IDENTIDAD DE MARCA (Brand DNA)
# ============================================================================

class EMBRION_TECNICO_LLM_INVALIDO(ValueError):
    """El LLM retornó output que no satisface el schema EmbrionTecnicoReport.

    Sugerencia: revisar prompt o caer al fallback heurístico determinístico.
    """


# ============================================================================
# DOMAIN MODELS — STRUCTURED OUTPUT SCHEMA (39va semilla)
# ============================================================================

class StackRecomendado(BaseModel):
    """Stack tech recomendado para implementar el producto."""

    model_config = ConfigDict(extra="forbid")

    frontend: str = Field(
        ...,
        description="Framework/lenguaje frontend recomendado. Ej: 'Next.js 14 + Tailwind'.",
        min_length=3,
        max_length=200,
    )
    backend: str = Field(
        ...,
        description="Framework/lenguaje backend recomendado. Ej: 'FastAPI + PostgreSQL'.",
        min_length=3,
        max_length=200,
    )
    hosting: str = Field(
        ...,
        description="Plataforma de hosting recomendada. Ej: 'Vercel + Supabase'.",
        min_length=3,
        max_length=200,
    )
    deploy_target: str = Field(
        ...,
        description="Target de deploy concreto. Ej: 'vercel', 'railway', 'cloudflare-pages'.",
        min_length=3,
        max_length=80,
    )
    razonamiento: str = Field(
        ...,
        description="Razonamiento corto (1-2 oraciones) de por qué este stack.",
        min_length=10,
        max_length=500,
    )


class RiesgoTecnico(BaseModel):
    """Un riesgo técnico identificado con severidad y mitigación propuesta."""

    model_config = ConfigDict(extra="forbid")

    descripcion: str = Field(
        ...,
        description="Descripción concreta del riesgo técnico.",
        min_length=10,
        max_length=400,
    )
    severidad: str = Field(
        ...,
        description="Severidad del riesgo. Uno de: 'baja', 'media', 'alta', 'critica'.",
    )
    mitigacion: str = Field(
        ...,
        description="Acción concreta para mitigar el riesgo.",
        min_length=10,
        max_length=400,
    )


class EmbrionTecnicoReport(BaseModel):
    """Output estructurado del Embrión Técnico."""

    model_config = ConfigDict(extra="forbid")

    stack_recomendado: StackRecomendado = Field(
        ...,
        description="Stack tech recomendado para implementar el producto.",
    )
    complejidad_1_5: int = Field(
        ...,
        ge=1,
        le=5,
        description="Complejidad estimada del proyecto en escala 1-5.",
    )
    riesgos: list[RiesgoTecnico] = Field(
        default_factory=list,
        description="Lista de riesgos técnicos detectados (0 a 8 items).",
        max_length=8,
    )
    tiempo_mvp_dias: int = Field(
        ...,
        ge=1,
        le=180,
        description="Estimación de días para llegar a MVP funcional.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confianza del análisis 0.0-1.0.",
    )
    source: str = Field(
        default="unknown",
        description="Origen del análisis. Uno de: 'llm_openai', 'heuristic_fallback'.",
    )
    analyzed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp ISO 8601 UTC del análisis.",
    )


# ============================================================================
# EMBRIÓN TÉCNICO
# ============================================================================

_VALID_SEVERIDADES = {"baja", "media", "alta", "critica"}


class EmbrionTecnico:
    """Análisis técnico de un brief de producto.

    Args:
        use_llm: si True, intenta LLM-as-parser. Si False o key ausente, fallback.
        model_id: modelo a usar. Default 'gpt-4o-mini' (ligero y barato).
    """

    def __init__(
        self,
        *,
        use_llm: bool = True,
        model_id: str = "gpt-4o-mini",
    ) -> None:
        self.use_llm = use_llm
        self.model_id = model_id

    # ── Capa Memento: env var lookup en runtime ─────────────────────────────
    def _llm_available(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    # ── API pública ─────────────────────────────────────────────────────────
    def analizar(
        self,
        *,
        frase_input: str,
        brief: Optional[dict] = None,
    ) -> EmbrionTecnicoReport:
        """Analiza un brief y devuelve `EmbrionTecnicoReport` validado.

        Args:
            frase_input: frase canónica del usuario.
            brief: dict opcional con keys como 'nombre_proyecto', 'audiencia',
                'propuesta_valor', 'secciones_landing'.
        """
        brief = brief or {}
        if self.use_llm and self._llm_available():
            try:
                report = self._analizar_con_llm(frase_input, brief)
                report.source = "llm_openai"
                return report
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "embrion_tecnico_llm_unavailable fallback_heuristic frase_len=%d error=%s",
                    len(frase_input),
                    exc,
                )
                report = self._analizar_heuristico(frase_input, brief)
                report.source = "heuristic_fallback"
                return report
        report = self._analizar_heuristico(frase_input, brief)
        report.source = "heuristic_fallback"
        return report

    # ── LLM-as-parser ────────────────────────────────────────────────────────
    def _analizar_con_llm(
        self,
        frase_input: str,
        brief: dict,
    ) -> EmbrionTecnicoReport:
        """LLM-as-parser con Structured Outputs Pydantic (39va semilla)."""
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - sdk presente en prod
            raise EMBRION_TECNICO_LLM_INVALIDO(
                f"openai SDK no instalado: {exc}"
            ) from exc

        client = OpenAI()
        prompt = self._build_prompt(frase_input, brief)

        response = client.beta.chat.completions.parse(
            model=self.model_id,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sos el Embrión Técnico de El Monstruo, una IA "
                        "especializada en análisis técnico de productos digitales. "
                        "Tu personalidad es Implacable, Preciso, Soberano. "
                        "Devolvés output estricto en el schema EmbrionTecnicoReport. "
                        "Razonás en español rioplatense, técnicamente preciso, sin rodeos."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format=EmbrionTecnicoReport,
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise EMBRION_TECNICO_LLM_INVALIDO(
                "LLM devolvió None en structured parse"
            )
        # Validar severidades de riesgos contra vocabulario controlado
        valid_riesgos = []
        for r in parsed.riesgos:
            if r.severidad in _VALID_SEVERIDADES:
                valid_riesgos.append(r)
            else:
                logger.warning(
                    "embrion_tecnico_riesgo_severidad_invalida descartado severidad=%s",
                    r.severidad,
                )
        parsed.riesgos = valid_riesgos
        return parsed

    # ── Fallback heurístico determinístico ──────────────────────────────────
    def _analizar_heuristico(
        self,
        frase_input: str,
        brief: dict,
    ) -> EmbrionTecnicoReport:
        """Fallback determinístico cuando OPENAI_API_KEY ausente."""
        frase_lower = frase_input.lower()

        # Heurística stack: detección por palabras clave
        if "landing" in frase_lower or "página" in frase_lower or "pagina" in frase_lower:
            stack = StackRecomendado(
                frontend="Next.js 14 + Tailwind",
                backend="API serverless (Vercel Functions)",
                hosting="Vercel",
                deploy_target="vercel",
                razonamiento=(
                    "Heurístico: landing premium → Next.js + Vercel "
                    "es stack estándar para SEO+performance."
                ),
            )
            tiempo_mvp = 5
            complejidad = 2
        elif "tienda" in frase_lower or "ecommerce" in frase_lower or "vender" in frase_lower:
            stack = StackRecomendado(
                frontend="Next.js 14 + Tailwind",
                backend="FastAPI + PostgreSQL + Stripe",
                hosting="Vercel + Railway",
                deploy_target="vercel",
                razonamiento=(
                    "Heurístico: ecommerce → Next.js front + FastAPI/Stripe "
                    "para checkout. Pago Stripe necesario."
                ),
            )
            tiempo_mvp = 14
            complejidad = 3
        elif "app" in frase_lower or "móvil" in frase_lower or "movil" in frase_lower:
            stack = StackRecomendado(
                frontend="React Native (Expo)",
                backend="FastAPI + PostgreSQL",
                hosting="EAS + Railway",
                deploy_target="expo",
                razonamiento=(
                    "Heurístico: app móvil → Expo permite iOS+Android single codebase."
                ),
            )
            tiempo_mvp = 21
            complejidad = 4
        else:
            stack = StackRecomendado(
                frontend="Next.js 14 + Tailwind",
                backend="FastAPI + PostgreSQL",
                hosting="Vercel + Railway",
                deploy_target="vercel",
                razonamiento=(
                    "Heurístico default: stack soberano El Monstruo."
                ),
            )
            tiempo_mvp = 10
            complejidad = 3

        # Riesgos heurísticos
        riesgos: list[RiesgoTecnico] = []
        if "premium" in frase_lower:
            riesgos.append(
                RiesgoTecnico(
                    descripcion=(
                        "Expectativa de calidad premium exige assets de alta "
                        "resolución y performance impecable (LCP < 1.5s)."
                    ),
                    severidad="media",
                    mitigacion=(
                        "Auditar Lighthouse, comprimir imágenes con AVIF, "
                        "habilitar ISR en Vercel."
                    ),
                )
            )
        if "vender" in frase_lower or "tienda" in frase_lower:
            riesgos.append(
                RiesgoTecnico(
                    descripcion=(
                        "Integración de pagos requiere compliance PCI y "
                        "manejo seguro de webhooks Stripe."
                    ),
                    severidad="alta",
                    mitigacion=(
                        "Usar Stripe Checkout hosted, validar webhooks con "
                        "signature, NO almacenar PAN."
                    ),
                )
            )
        if not riesgos:
            riesgos.append(
                RiesgoTecnico(
                    descripcion="Sin riesgos críticos detectados en heurístico.",
                    severidad="baja",
                    mitigacion="Monitorear errores con Sentry desde día 1.",
                )
            )

        return EmbrionTecnicoReport(
            stack_recomendado=stack,
            complejidad_1_5=complejidad,
            riesgos=riesgos,
            tiempo_mvp_dias=tiempo_mvp,
            confidence=0.5,  # heurístico = baja confianza
            source="heuristic_fallback",
        )

    # ── Prompt builder ──────────────────────────────────────────────────────
    def _build_prompt(self, frase_input: str, brief: dict) -> str:
        brief_keys = ", ".join(brief.keys()) if brief else "ninguno"
        propuesta = brief.get("propuesta_valor", frase_input)
        audiencia = brief.get("audiencia", "no especificada")
        secciones = brief.get("secciones_landing", [])
        secciones_str = ", ".join(secciones) if secciones else "no especificadas"
        return (
            f"Frase canónica del usuario: {frase_input}\n\n"
            f"Brief recibido (keys: {brief_keys}):\n"
            f"  - propuesta_valor: {propuesta}\n"
            f"  - audiencia: {audiencia}\n"
            f"  - secciones_landing: {secciones_str}\n\n"
            "Tu tarea:\n"
            "1. Recomendar un stack técnico concreto (frontend, backend, hosting, deploy_target).\n"
            "2. Estimar complejidad del proyecto en escala 1-5.\n"
            "3. Identificar 1-5 riesgos técnicos concretos con severidad "
            "(baja|media|alta|critica) y mitigación.\n"
            "4. Estimar tiempo a MVP en días (1-180).\n"
            "5. Asignar confidence 0-1 según completitud del brief recibido.\n\n"
            "Responde estrictamente en el schema EmbrionTecnicoReport. "
            "No inventes campos. Razona en español, técnicamente preciso."
        )
