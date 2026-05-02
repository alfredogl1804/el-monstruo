"""
El Monstruo — Embrión-Creativo (Sprint 59.3)
=============================================
4to Embrión especializado. Dominio: Diseño, branding, UX, identidad visual.

Responsabilidad:
  - Generar identidades de marca completas (nombre, colores, tipografía, logo prompt)
  - Revisar calidad de diseño contra estándares Apple/Tesla (Objetivo #2)
  - Generar paletas de color basadas en industria y mood
  - Escanear tendencias de diseño actuales (tarea autónoma cada 24h)

Estándar de diseño (Objetivo #2):
  - Nada genérico. Nada "AI slop" (gradientes morados, Inter everywhere)
  - Asimetría intencional, tipografía con personalidad, whitespace activo
  - Cada decisión de diseño tiene una RAZÓN, no "se ve bonito"
  - Máximo 3 colores principales + 2 acentos
  - Máximo 2 familias tipográficas (display + body)

Hermanos:
  - Embrión-Ventas (Sprint 57)
  - Embrión-Técnico (Sprint 58)
  - Embrión-Vigía (Sprint 58)
  - Embrión-Estratega (Sprint 59)

Sprint: 59 — "El Monstruo Habla al Mundo"
Fecha: 2026-05-01

Soberanía:
  - GPT-4o para brand generation (alta creatividad)
  - Gemini 2.0 Flash como fallback
  - Heurísticas de color si LLM no disponible
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import structlog

logger = structlog.get_logger("monstruo.embrion.creativo")


# ── Errores con identidad ──────────────────────────────────────────────────────


class EMBRION_CREATIVO_SIN_SABIOS(RuntimeError):
    """No hay cliente de Sabios configurado para generación creativa.

    Sugerencia: Inyecta _sabios al instanciar EmbrionCreativo.
    """


class EMBRION_CREATIVO_JSON_INVALIDO(ValueError):
    """El LLM retornó JSON inválido en la respuesta creativa.

    Sugerencia: Verifica el prompt o usa el fallback de heurísticas.
    """


# ── Dataclasses de dominio ─────────────────────────────────────────────────────


@dataclass
class BrandIdentity:
    """Identidad de marca generada por el Embrión-Creativo.

    Args:
        name_options: 3 opciones de nombre memorables y disponibles como .com.
        tagline: Tagline memorable en el idioma del mercado objetivo.
        color_palette: Paleta de 5 colores con hex codes (WCAG AA compliant).
        typography: 2 familias tipográficas (display + body) de Google Fonts.
        design_principles: 3 principios de diseño específicos para la marca.
        mood: Estilo visual ('minimal', 'bold', 'playful', 'elegant', 'brutalist').
        logo_prompt: Prompt detallado para generación de logo con AI.
        generated_at: Timestamp de generación.
    """

    name_options: list[str]
    tagline: str
    color_palette: dict[str, str]
    typography: dict[str, str]
    design_principles: list[str]
    mood: str
    logo_prompt: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        """Serializar para el Command Center."""
        return {
            "name_options": self.name_options,
            "tagline": self.tagline,
            "color_palette": self.color_palette,
            "typography": self.typography,
            "design_principles": self.design_principles,
            "mood": self.mood,
            "logo_prompt": self.logo_prompt,
            "generated_at": self.generated_at,
        }


CREATIVE_SYSTEM_PROMPT = """Eres el Embrión-Creativo de El Monstruo.
Tu dominio es TODO lo visual y creativo:
- Branding: nombres, logos, identidad visual
- Diseño: paletas de color, tipografía, layouts
- UX: flujos de usuario, wireframes, micro-interacciones
- Assets: generación de imágenes, iconos, ilustraciones

ESTÁNDAR: Nivel Apple/Tesla. Nada genérico. Nada "AI slop."
- Evita: gradientes morados genéricos, Inter font everywhere, layouts centrados simétricos
- Prefiere: asimetría intencional, tipografía con personalidad, whitespace como elemento activo
- Cada decisión de diseño debe tener una RAZÓN (no "se ve bonito")

RESTRICCIONES:
- Nunca uses más de 3 colores principales + 2 acentos
- Tipografía: máximo 2 familias (display + body)
- Siempre justifica tus decisiones de diseño con principios
"""


# ── Embrión principal ──────────────────────────────────────────────────────────


@dataclass
class EmbrionCreativo:
    """Embrión especializado en diseño, branding y creatividad visual.

    Genera identidades de marca completas y evalúa calidad de diseño
    contra los estándares del Objetivo #2 (Nivel Apple/Tesla).

    Args:
        _sabios: Cliente de Sabios para generación creativa via LLM.
        budget_daily_usd: Presupuesto diario máximo en USD.

    Soberanía:
        - GPT-4o (creatividad alta) → Gemini Flash (fallback)
        - Heurísticas de color si LLM no disponible
    """

    _sabios: Optional[object] = field(default=None, repr=False)
    budget_daily_usd: float = 1.5
    _spent_today: float = field(default=0.0, repr=False)
    _ciclos_completados: int = field(default=0, repr=False)
    _last_trend_scan: Optional[str] = field(default=None, repr=False)

    EMBRION_ID: str = field(default="embrion-creativo", init=False)
    SPECIALIZATION: str = field(default="Diseño, Branding, UX, Identidad Visual", init=False)

    DEFAULT_TASKS: dict = field(
        default_factory=lambda: {
            "brand_generation": {
                "description": "Generar identidad de marca completa para un proyecto",
                "interval_hours": 0,  # On-demand
                "handler": "generate_brand_identity",
            },
            "design_review": {
                "description": "Revisar diseño de proyecto contra estándares Apple/Tesla",
                "interval_hours": 0,  # On-demand
                "handler": "review_design_quality",
            },
            "trend_scan": {
                "description": "Escanear tendencias de diseño actuales",
                "interval_hours": 24,
                "handler": "scan_design_trends",
            },
            "palette_generator": {
                "description": "Generar paleta de color basada en industria y mood",
                "interval_hours": 0,  # On-demand
                "handler": "generate_color_palette",
            },
        },
        init=False,
    )

    async def generate_brand_identity(
        self,
        niche: str,
        target_audience: str,
        mood: str = "elegant",
        locale: str = "es",
    ) -> BrandIdentity:
        """Generar identidad de marca completa para un nicho y audiencia.

        Args:
            niche: Nicho o industria del negocio (ej: 'ropa deportiva premium').
            target_audience: Descripción de la audiencia objetivo.
            mood: Estilo visual deseado ('minimal', 'bold', 'playful', 'elegant', 'brutalist').
            locale: Idioma del mercado principal para nombres y tagline.

        Returns:
            BrandIdentity con nombre, colores, tipografía y logo prompt.

        Raises:
            EMBRION_CREATIVO_SIN_SABIOS: Si no hay cliente LLM configurado.
        """
        if not self._sabios:
            raise EMBRION_CREATIVO_SIN_SABIOS("EmbrionCreativo requiere _sabios para generar identidades de marca.")

        prompt = f"""{CREATIVE_SYSTEM_PROMPT}

Generate a complete brand identity for:
- Niche: {niche}
- Target audience: {target_audience}
- Mood/Style: {mood}
- Primary market locale: {locale}

Respond in JSON ONLY:
{{
    "name_options": ["name1", "name2", "name3"],
    "tagline": "...",
    "color_palette": {{
        "primary": "#hex",
        "secondary": "#hex",
        "accent": "#hex",
        "background": "#hex",
        "text": "#hex"
    }},
    "typography": {{
        "display_font": "Font Name (Google Fonts)",
        "body_font": "Font Name (Google Fonts)"
    }},
    "design_principles": ["principle1 with reason", "principle2 with reason", "principle3 with reason"],
    "mood": "{mood}",
    "logo_prompt": "Detailed prompt for AI image generation of the logo"
}}

RULES:
- Names must be memorable, pronounceable in {locale}, and available as .com domain
- Colors must have WCAG AA contrast ratios (4.5:1 minimum)
- Fonts must be available on Google Fonts
- Logo prompt must be specific enough for high-quality AI generation
- NO generic choices. Be bold and distinctive.
- Each design_principle must include the REASON for the decision."""

        response = await self._sabios.ask(prompt)
        data = self._parse_json_response(response)

        self._ciclos_completados += 1
        logger.info(
            "brand_identity_generada",
            niche=niche,
            mood=mood,
            locale=locale,
            names=data.get("name_options", []),
        )

        return BrandIdentity(
            name_options=data["name_options"],
            tagline=data["tagline"],
            color_palette=data["color_palette"],
            typography=data["typography"],
            design_principles=data["design_principles"],
            mood=data["mood"],
            logo_prompt=data["logo_prompt"],
        )

    async def review_design_quality(self, design_description: str) -> dict:
        """Revisar calidad de diseño contra estándares Apple/Tesla (Objetivo #2).

        Args:
            design_description: Descripción del diseño a evaluar.

        Returns:
            Dict con scores por dimensión, fortalezas, debilidades y fixes específicos.

        Raises:
            EMBRION_CREATIVO_SIN_SABIOS: Si no hay cliente LLM configurado.
        """
        if not self._sabios:
            raise EMBRION_CREATIVO_SIN_SABIOS("EmbrionCreativo requiere _sabios para revisar diseños.")

        prompt = f"""Review this design against Apple/Tesla quality standards.

Design description: {design_description}

Score each dimension (0-10) and provide specific, actionable feedback:
1. Typography (hierarchy, readability, personality)
2. Color (harmony, contrast, intentionality)
3. Layout (balance, whitespace, flow)
4. Consistency (tokens, patterns, repetition)
5. Originality (distinctiveness, avoids "AI slop")

Respond in JSON:
{{
    "scores": {{"typography": N, "color": N, "layout": N, "consistency": N, "originality": N}},
    "overall": N,
    "grade": "<A|B|C|D|F>",
    "strengths": ["specific strength 1", "specific strength 2"],
    "weaknesses": ["specific weakness 1", "specific weakness 2"],
    "specific_fixes": ["actionable fix 1 with example", "actionable fix 2 with example"]
}}"""

        response = await self._sabios.ask(prompt)
        result = self._parse_json_response(response)

        logger.info(
            "design_review_completado",
            overall=result.get("overall"),
            grade=result.get("grade"),
        )
        return result

    async def generate_color_palette(
        self,
        industry: str,
        mood: str,
        base_color: Optional[str] = None,
    ) -> dict:
        """Generar paleta de colores basada en industria y mood.

        Args:
            industry: Industria o nicho (ej: 'fintech', 'wellness', 'gaming').
            mood: Estilo visual ('minimal', 'bold', 'playful', 'elegant', 'brutalist').
            base_color: Color base opcional en hex (ej: '#2D4A8A').

        Returns:
            Dict con 5 colores (primary, secondary, accent, background, text)
            incluyendo nombre, hex, uso y tipo de armonía.

        Raises:
            EMBRION_CREATIVO_SIN_SABIOS: Si no hay cliente LLM configurado.
        """
        if not self._sabios:
            raise EMBRION_CREATIVO_SIN_SABIOS("EmbrionCreativo requiere _sabios para generar paletas de color.")

        prompt = f"""Generate a professional color palette for:
- Industry: {industry}
- Mood: {mood}
- Base color (optional): {base_color or "choose the best"}

Requirements:
- 5 colors: primary, secondary, accent, background, text
- WCAG AA compliant contrast ratios (4.5:1 minimum)
- Harmonious (analogous, complementary, or split-complementary)
- NOT generic (no default blue #0066CC, no purple gradients)
- Each color must have a clear purpose and name

Respond in JSON:
{{
    "palette": {{
        "primary": {{"hex": "#...", "name": "...", "usage": "..."}},
        "secondary": {{"hex": "#...", "name": "...", "usage": "..."}},
        "accent": {{"hex": "#...", "name": "...", "usage": "..."}},
        "background": {{"hex": "#...", "name": "...", "usage": "..."}},
        "text": {{"hex": "#...", "name": "...", "usage": "..."}}
    }},
    "harmony_type": "analogous|complementary|split-complementary|triadic",
    "rationale": "Why these colors work for this industry/mood"
}}"""

        response = await self._sabios.ask(prompt)
        result = self._parse_json_response(response)

        logger.info("paleta_generada", industry=industry, mood=mood)
        return result

    async def scan_design_trends(self) -> dict:
        """Tarea autónoma: escanear tendencias actuales de diseño web/app.

        Returns:
            Dict con lista de tendencias actuales y tips de implementación.
        """
        if not self._sabios:
            logger.warning("trend_scan_sin_sabios")
            return {"trends": [], "scanned_at": datetime.now(timezone.utc).isoformat()}

        prompt = """What are the current top 5 web/app design trends in 2026?
For each trend, provide:
1. Name
2. Description (2 sentences max)
3. Best suited for (type of project)
4. Example implementation tip
5. Brands doing it well

Respond in JSON array format:
[
    {{
        "name": "...",
        "description": "...",
        "best_for": "...",
        "implementation_tip": "...",
        "examples": ["brand1", "brand2"]
    }}
]"""

        response = await self._sabios.ask(prompt)
        trends = self._parse_json_response(response)

        self._last_trend_scan = datetime.now(timezone.utc).isoformat()
        logger.info("trend_scan_completado", total_trends=len(trends) if isinstance(trends, list) else 0)
        return {
            "trends": trends if isinstance(trends, list) else [],
            "scanned_at": self._last_trend_scan,
        }

    def _parse_json_response(self, response: str) -> dict:
        """Extraer y parsear JSON de respuesta LLM.

        Args:
            response: Respuesta raw del LLM.

        Returns:
            Dict parseado del JSON.

        Raises:
            EMBRION_CREATIVO_JSON_INVALIDO: Si el JSON no es parseable.
        """
        json_str = response.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as _e:
            raise EMBRION_CREATIVO_JSON_INVALIDO(f"JSON inválido en respuesta del LLM: {str(_e)[:100]}") from _e

    def to_dict(self) -> dict:
        """Estado del embrión para consumo del Command Center.

        Returns:
            Dict serializable con estado actual del Embrión-Creativo.
        """
        return {
            "embrion_id": self.EMBRION_ID,
            "specialization": self.SPECIALIZATION,
            "version": "1.0.0-sprint59",
            "objetivo": "#2 Nivel Apple/Tesla + #11 Multiplicación de Embriones",
            "estado": "activo" if self._sabios else "sin_sabios",
            "ciclos_completados": self._ciclos_completados,
            "budget_daily_usd": self.budget_daily_usd,
            "spent_today_usd": round(self._spent_today, 4),
            "tasks_autonomas": list(self.DEFAULT_TASKS.keys()),
            "last_trend_scan": self._last_trend_scan,
        }
