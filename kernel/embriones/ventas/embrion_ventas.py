"""
Embrión Ventas — análisis comercial de viabilidad de un brief de producto.

Responsabilidad:
  - ICP refinado (Ideal Customer Profile)
  - Propuesta de valor sintetizada (3 beneficios + diferenciador)
  - Pricing tentativo (modelo + rango)
  - Canales de adquisición sugeridos (top 3 con CAC estimado)
  - Output: `EmbrionVentasReport` Pydantic estricto

Patrón LLM-as-parser con Structured Outputs Pydantic (39va semilla):
  - Si OPENAI_API_KEY presente → `client.beta.chat.completions.parse`
  - Si OPENAI_API_KEY ausente → fallback heurístico determinístico

Capa Memento:
  - Lee env var en runtime, NO cachea
  - Brand DNA: `embrion_ventas_*_failed`

[Hilo Manus Memento — Ejecutor] · Sprint 87.1 Bloque 2 · 2026-05-05
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

class EMBRION_VENTAS_LLM_INVALIDO(ValueError):
    """El LLM retornó output que no satisface el schema EmbrionVentasReport.

    Sugerencia: revisar prompt o caer al fallback heurístico determinístico.
    """


# ============================================================================
# DOMAIN MODELS — STRUCTURED OUTPUT SCHEMA (39va semilla)
# ============================================================================

class PropuestaValor(BaseModel):
    """Propuesta de valor sintetizada del producto."""

    model_config = ConfigDict(extra="forbid")

    statement: str = Field(
        ...,
        description="Statement de propuesta de valor en una oración.",
        min_length=15,
        max_length=300,
    )
    beneficios: list[str] = Field(
        ...,
        description="Top 3 beneficios concretos para el cliente.",
        min_length=1,
        max_length=5,
    )
    diferenciador: str = Field(
        ...,
        description="Qué te hace único frente a competencia.",
        min_length=10,
        max_length=300,
    )


class PricingTentativo(BaseModel):
    """Modelo de pricing tentativo."""

    model_config = ConfigDict(extra="forbid")

    modelo: str = Field(
        ...,
        description="Modelo de pricing. Uno de: 'one-time', 'subscription', 'freemium', 'usage-based', 'enterprise'.",
    )
    rango_min: float = Field(
        ...,
        ge=0.0,
        description="Rango mínimo en USD.",
    )
    rango_max: float = Field(
        ...,
        ge=0.0,
        description="Rango máximo en USD.",
    )
    razonamiento: str = Field(
        ...,
        description="Razonamiento corto (1-2 oraciones).",
        min_length=10,
        max_length=400,
    )


class CanalAdquisicion(BaseModel):
    """Canal de adquisición sugerido con CAC estimado."""

    model_config = ConfigDict(extra="forbid")

    canal: str = Field(
        ...,
        description="Nombre del canal. Ej: 'Google Ads', 'Instagram orgánico', 'SEO content', 'Outbound LinkedIn'.",
        min_length=3,
        max_length=120,
    )
    cac_usd_estimado: float = Field(
        ...,
        ge=0.0,
        description="CAC (Customer Acquisition Cost) estimado en USD.",
    )
    razonamiento: str = Field(
        ...,
        description="Por qué este canal es adecuado para el ICP.",
        min_length=10,
        max_length=400,
    )


class EmbrionVentasReport(BaseModel):
    """Output estructurado del Embrión Ventas."""

    model_config = ConfigDict(extra="forbid")

    icp_refinado: str = Field(
        ...,
        description="ICP (Ideal Customer Profile) refinado en 1-2 oraciones.",
        min_length=20,
        max_length=600,
    )
    propuesta_valor: PropuestaValor = Field(
        ...,
        description="Propuesta de valor sintetizada.",
    )
    pricing_tentativo: PricingTentativo = Field(
        ...,
        description="Pricing tentativo.",
    )
    canales_adquisicion: list[CanalAdquisicion] = Field(
        ...,
        description="Top 3 canales de adquisición sugeridos.",
        min_length=1,
        max_length=5,
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
# EMBRIÓN VENTAS
# ============================================================================

_VALID_PRICING_MODELOS = {
    "one-time", "subscription", "freemium", "usage-based", "enterprise"
}


class EmbrionVentas:
    """Análisis comercial de un brief de producto.

    Args:
        use_llm: si True, intenta LLM-as-parser. Si False o key ausente, fallback.
        model_id: modelo a usar. Default 'gpt-4o-mini'.
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
    ) -> EmbrionVentasReport:
        """Analiza un brief y devuelve `EmbrionVentasReport` validado."""
        brief = brief or {}
        if self.use_llm and self._llm_available():
            try:
                report = self._analizar_con_llm(frase_input, brief)
                report.source = "llm_openai"
                return report
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "embrion_ventas_llm_unavailable fallback_heuristic frase_len=%d error=%s",
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
    ) -> EmbrionVentasReport:
        """LLM-as-parser con Structured Outputs Pydantic."""
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise EMBRION_VENTAS_LLM_INVALIDO(
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
                        "Sos el Embrión Ventas de El Monstruo, una IA "
                        "especializada en estrategia comercial. "
                        "Personalidad: Implacable, Preciso, Soberano. "
                        "Devolvés output estricto en el schema EmbrionVentasReport. "
                        "Razonás en español rioplatense, directo, sin rodeos."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format=EmbrionVentasReport,
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise EMBRION_VENTAS_LLM_INVALIDO(
                "LLM devolvió None en structured parse"
            )
        # Validar pricing modelo contra vocabulario controlado
        if parsed.pricing_tentativo.modelo not in _VALID_PRICING_MODELOS:
            logger.warning(
                "embrion_ventas_pricing_modelo_invalido recibido=%s, default=one-time",
                parsed.pricing_tentativo.modelo,
            )
            parsed.pricing_tentativo.modelo = "one-time"
        # Validar rango_max >= rango_min
        if parsed.pricing_tentativo.rango_max < parsed.pricing_tentativo.rango_min:
            parsed.pricing_tentativo.rango_max = parsed.pricing_tentativo.rango_min
        return parsed

    # ── Fallback heurístico determinístico ──────────────────────────────────
    def _analizar_heuristico(
        self,
        frase_input: str,
        brief: dict,
    ) -> EmbrionVentasReport:
        """Fallback determinístico cuando OPENAI_API_KEY ausente."""
        frase_lower = frase_input.lower()
        propuesta_valor_brief = brief.get("propuesta_valor", frase_input)
        audiencia_brief = brief.get("audiencia", "")

        # ── ICP heurístico ─────────────────────────────────────────────────
        if "premium" in frase_lower or "artesanal" in frase_lower:
            icp = (
                f"Compradores con poder adquisitivo medio-alto interesados en "
                f"productos artesanales o premium. {audiencia_brief}"
            ).strip()
        elif "tienda" in frase_lower or "ecommerce" in frase_lower or "vender" in frase_lower:
            icp = (
                f"Consumidores online que buscan {propuesta_valor_brief}. "
                f"{audiencia_brief}"
            ).strip()
        elif "app" in frase_lower or "móvil" in frase_lower or "movil" in frase_lower:
            icp = (
                f"Usuarios móviles que buscan {propuesta_valor_brief}. "
                f"{audiencia_brief}"
            ).strip()
        else:
            icp = (
                f"Audiencia objetivo derivada de la frase: {propuesta_valor_brief}. "
                f"{audiencia_brief}"
            ).strip()

        # ── Propuesta de valor heurística ──────────────────────────────────
        beneficios = [
            "Calidad verificable y trazable",
            "Atención al cliente de respuesta rápida",
            "Experiencia de compra premium end-to-end",
        ]
        if "artesanal" in frase_lower:
            beneficios[0] = "Producto artesanal único hecho a mano"
        if "mérida" in frase_lower or "merida" in frase_lower or "yucatán" in frase_lower:
            beneficios[2] = "Origen yucateco autentico con denominación de identidad"

        propuesta = PropuestaValor(
            statement=(
                f"Solución diseñada para {icp.split('.')[0]}, "
                f"diferenciada por calidad y experiencia premium."
            )[:300],
            beneficios=beneficios,
            diferenciador=(
                "Calidad artesanal verificable + branding premium + storytelling auténtico."
                if "premium" in frase_lower or "artesanal" in frase_lower
                else "Velocidad de ejecución + experiencia premium + soporte humano."
            ),
        )

        # ── Pricing heurístico ─────────────────────────────────────────────
        if "premium" in frase_lower and "artesanal" in frase_lower:
            pricing = PricingTentativo(
                modelo="one-time",
                rango_min=80.0,
                rango_max=500.0,
                razonamiento=(
                    "Heurístico: producto artesanal premium → pricing one-time "
                    "con rango amplio según tamaño/complejidad de la pieza."
                ),
            )
        elif "saas" in frase_lower or "subscription" in frase_lower or "suscripción" in frase_lower:
            pricing = PricingTentativo(
                modelo="subscription",
                rango_min=29.0,
                rango_max=199.0,
                razonamiento=(
                    "Heurístico: producto SaaS → modelo de suscripción mensual estándar."
                ),
            )
        elif "freemium" in frase_lower or "gratis" in frase_lower:
            pricing = PricingTentativo(
                modelo="freemium",
                rango_min=0.0,
                rango_max=49.0,
                razonamiento=(
                    "Heurístico: producto con tier gratuito → freemium con upsell."
                ),
            )
        else:
            pricing = PricingTentativo(
                modelo="one-time",
                rango_min=49.0,
                rango_max=199.0,
                razonamiento=(
                    "Heurístico default: pricing one-time mid-market."
                ),
            )

        # ── Canales heurísticos ────────────────────────────────────────────
        canales: list[CanalAdquisicion] = []
        if "premium" in frase_lower or "artesanal" in frase_lower:
            canales.append(
                CanalAdquisicion(
                    canal="Instagram orgánico + UGC",
                    cac_usd_estimado=8.0,
                    razonamiento=(
                        "Producto visual artesanal → Instagram con storytelling "
                        "y user-generated content tiene CAC bajo."
                    ),
                )
            )
            canales.append(
                CanalAdquisicion(
                    canal="Pinterest Ads",
                    cac_usd_estimado=12.0,
                    razonamiento="Audiencia compradora premium con alta intención visual."
                )
            )
            canales.append(
                CanalAdquisicion(
                    canal="Galerías/showrooms locales (B2B)",
                    cac_usd_estimado=25.0,
                    razonamiento=(
                        "Distribución física en galerías permite acceso a coleccionistas."
                    ),
                )
            )
        elif "tienda" in frase_lower or "ecommerce" in frase_lower:
            canales = [
                CanalAdquisicion(
                    canal="Google Ads (Shopping)",
                    cac_usd_estimado=18.0,
                    razonamiento="Estándar para ecommerce con intención de compra alta.",
                ),
                CanalAdquisicion(
                    canal="Meta Ads (FB+IG)",
                    cac_usd_estimado=22.0,
                    razonamiento="Lookalike audiences con catálogo de productos.",
                ),
                CanalAdquisicion(
                    canal="Email marketing post-compra",
                    cac_usd_estimado=3.0,
                    razonamiento="Retención y up-sell con CAC marginal.",
                ),
            ]
        elif "app" in frase_lower or "móvil" in frase_lower or "movil" in frase_lower:
            canales = [
                CanalAdquisicion(
                    canal="App Store Optimization (ASO)",
                    cac_usd_estimado=4.0,
                    razonamiento="Discovery orgánico vía keywords del store.",
                ),
                CanalAdquisicion(
                    canal="TikTok Ads",
                    cac_usd_estimado=15.0,
                    razonamiento="Demographic match para usuarios móviles jóvenes.",
                ),
                CanalAdquisicion(
                    canal="Influencer marketing micro",
                    cac_usd_estimado=20.0,
                    razonamiento="Trust signal y demo orgánico del producto.",
                ),
            ]
        else:
            canales = [
                CanalAdquisicion(
                    canal="SEO content marketing",
                    cac_usd_estimado=10.0,
                    razonamiento="Long-tail orgánico con CAC decreciente en el tiempo.",
                ),
                CanalAdquisicion(
                    canal="Google Ads",
                    cac_usd_estimado=20.0,
                    razonamiento="Captura intención de búsqueda directa.",
                ),
                CanalAdquisicion(
                    canal="LinkedIn outbound",
                    cac_usd_estimado=35.0,
                    razonamiento="B2B targeting preciso para early adopters.",
                ),
            ]

        return EmbrionVentasReport(
            icp_refinado=icp[:600],
            propuesta_valor=propuesta,
            pricing_tentativo=pricing,
            canales_adquisicion=canales,
            confidence=0.5,
            source="heuristic_fallback",
        )

    # ── Prompt builder ──────────────────────────────────────────────────────
    def _build_prompt(self, frase_input: str, brief: dict) -> str:
        brief_keys = ", ".join(brief.keys()) if brief else "ninguno"
        propuesta = brief.get("propuesta_valor", frase_input)
        audiencia = brief.get("audiencia", "no especificada")
        return (
            f"Frase canónica del usuario: {frase_input}\n\n"
            f"Brief recibido (keys: {brief_keys}):\n"
            f"  - propuesta_valor: {propuesta}\n"
            f"  - audiencia: {audiencia}\n\n"
            "Tu tarea:\n"
            "1. Refinar el ICP (Ideal Customer Profile) en 1-2 oraciones concretas.\n"
            "2. Sintetizar propuesta de valor (statement + 3 beneficios + diferenciador).\n"
            "3. Proponer pricing tentativo (modelo de "
            "[one-time|subscription|freemium|usage-based|enterprise], rango USD min-max, razonamiento).\n"
            "4. Recomendar top 3 canales de adquisición con CAC USD estimado y razonamiento.\n"
            "5. Asignar confidence 0-1 según completitud del brief.\n\n"
            "Responde estrictamente en el schema EmbrionVentasReport. "
            "No inventes campos. Usa rangos USD realistas para el mercado LATAM."
        )
