"""
El Monstruo — Embrión Product Architect (Sprint 85)
=====================================================
Embrión nuevo que reemplaza el "shortcut creativo" del Executor.

Cuando el usuario pide "hazme una landing del taller de Yuna", este embrión
NO improvisa. Produce un Brief estructurado (contrato) que el Executor consume
para generar un sitio comercializable, no genérico.

Responsabilidades:
    1. Detectar el vertical del proyecto (1 de 6 verticales soportados).
    2. Producir un Brief JSON con: vertical, client_brand, product_meta,
       structure, data_known, data_missing.
    3. Identificar qué información falta (data_missing) en el prompt original.
    4. Si data_missing tiene keys críticas, emitir una user_question para
       que el planner se la haga al usuario antes de avanzar.
    5. Persistir el Brief en la tabla `briefs` (Supabase) para auditoría
       y reuso.

Dominio: Análisis del prompt, mapeo a vertical, contrato Brief.
Hereda: Patrón EmbrionCreativo (Sprint 59).
Hermanos: Critic Visual (Sprint 85, valida outputs del Executor).

Objetivo cubierto: #2 (Apple/Tesla — calidad sobre velocidad), #3 (Mínima
complejidad — el Executor recibe contrato claro), #4 (No equivocarse 2x —
el Brief evita ambigüedad).

Sprint 85 — 2026-05-04
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger("monstruo.embrion.product_architect")


# ── Errores con identidad ────────────────────────────────────────────────────
class EmbrionProductArchitectError(Exception):
    """Error base del Embrión Product Architect."""


PRODUCT_ARCHITECT_SIN_SABIOS = (
    "PRODUCT_ARCHITECT_SIN_SABIOS: "
    "ProductArchitect requiere un cliente _sabios para producir el Brief. "
    "Sugerencia: instanciar con ProductArchitect(_sabios=sabios_client)."
)

PRODUCT_ARCHITECT_VERTICAL_DESCONOCIDO = (
    "PRODUCT_ARCHITECT_VERTICAL_DESCONOCIDO: "
    "El vertical '{vertical}' no está en la library actual. "
    "Verticales válidos: {validos}. "
    "Sugerencia: usar 'professional_services' como fallback genérico."
)

PRODUCT_ARCHITECT_BRIEF_INVALIDO = (
    "PRODUCT_ARCHITECT_BRIEF_INVALIDO: "
    "El Brief generado no cumple el schema mínimo. "
    "Falta: {missing_keys}. "
    "Sugerencia: revisar prompt del LLM o reintentar."
)


# ── Verticales soportados (Bloque 6) ─────────────────────────────────────────
VERTICALES_VALIDOS = [
    "education_arts",          # Talleres, escuelas, academias creativas
    "saas_b2b",                # Software B2B, dashboards, herramientas pro
    "restaurant",              # Restaurantes, cafés, catering
    "professional_services",   # Consultoría, abogados, contadores, agencias
    "ecommerce_artisanal",     # E-commerce de productos artesanales/premium
    "marketplace_services",    # Marketplaces de servicios locales
]

# ── HOTFIX Sprint 85 (post-audit Sprint 84.5) ────────────────────────────────
# El patrón `kw in text_lower` causa falsos positivos en substring matching:
#   - "artesanal" matchea `arte` (vertical education_arts) en contexto ecommerce
#   - "no es delivery" matchea `delivery` pese a la negación
#   - keywords cortas (`api`, `arte`, `bar`) embebidas en otras palabras
# Solución: regex con word boundaries `\b...\b`, compilado una vez por vertical
# y cacheado a nivel módulo. Drop-in migrable a kernel/utils/keyword_matcher.py
# cuando el Hilo Ejecutor cierre Sprint 84.7.
#
# Patrón aprobado por spec del Sprint 84.5 (Cowork bridge 2026-05-04).
# Semilla 19 sembrada al cierre del HOTFIX.


def _compile_vertical_pattern(keywords: tuple[str, ...]) -> re.Pattern[str]:
    """Compila un pattern con word boundaries para una lista de keywords.

    Soporta multi-word keywords ("hecho a mano", "servicios profesionales")
    porque `\b` solo se ancla al inicio y final del grupo no-capturador.
    Las keywords se ordenan por longitud descendente para que multi-word
    matchee antes que sus subpartes (alternation greedy).
    """
    sorted_kws = sorted(keywords, key=len, reverse=True)
    return re.compile(
        r"\b(?:" + "|".join(re.escape(kw) for kw in sorted_kws) + r")\b",
        re.IGNORECASE,
    )


VERTICALES_KEYWORDS: dict[str, list[str]] = {
    "education_arts": [
        "taller", "clase", "curso", "academia", "escuela", "estudio", "ballet",
        "música", "música", "arte", "danza", "pintura", "yoga", "talleres",
        "aprender", "enseñar", "alumnos", "alumnas",
    ],
    "saas_b2b": [
        "saas", "software", "plataforma", "dashboard", "api", "herramienta",
        "automatización", "crm", "erp", "b2b", "empresas", "integración",
    ],
    "restaurant": [
        "restaurante", "café", "cafetería", "menú", "comida", "cocina",
        "chef", "delivery", "reservar", "platillos", "bebidas", "bar",
    ],
    "professional_services": [
        "consultoría", "abogado", "contador", "asesoría", "agencia", "estudio",
        "despacho", "consultor", "freelance", "servicios profesionales",
    ],
    "ecommerce_artisanal": [
        "tienda", "producto", "artesanal", "hecho a mano", "venta", "carrito",
        "comprar", "envío", "boutique", "marca", "premium", "limited edition",
    ],
    "marketplace_services": [
        "marketplace", "directorio", "buscar", "comparar", "reservar online",
        "marketplace local", "proveedores", "categorías", "filtros",
    ],
}

# Cache de patterns compilados (lazy fill en _detectar_vertical)
_PATTERN_CACHE: dict[str, re.Pattern[str]] = {}


# ── Schema del Brief ───────────────────────────────────────────────────────────────────────────
BRIEF_SCHEMA_KEYS = {
    "vertical",
    "client_brand",
    "product_meta",
    "structure",
    "data_known",
    "data_missing",
}

CRITICAL_DATA_KEYS = [
    "client_brand.name",
    "product_meta.value_proposition",
    "structure.primary_cta",
]


# ── Dataclass: Brief ─────────────────────────────────────────────────────────
@dataclass
class Brief:
    """
    Contrato estructurado producido por Product Architect.

    El Executor consume este Brief para construir un sitio sin improvisar.
    """

    prompt_original: str
    vertical: str
    client_brand: dict[str, Any] = field(default_factory=dict)
    product_meta: dict[str, Any] = field(default_factory=dict)
    structure: dict[str, Any] = field(default_factory=dict)
    data_known: dict[str, Any] = field(default_factory=dict)
    data_missing: list[str] = field(default_factory=list)
    user_question_emitted: Optional[str] = None
    architect_model: Optional[str] = None
    architect_cost_usd: float = 0.0
    architect_duration_ms: int = 0
    brief_id: Optional[str] = None  # Asignado al persistir en DB
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def is_complete(self) -> bool:
        """True si no hay data_missing crítica."""
        for crit_key in CRITICAL_DATA_KEYS:
            if crit_key in self.data_missing:
                return False
        return True

    def to_dict(self) -> dict[str, Any]:
        """Serializar para persistencia y respuesta API."""
        return {
            "prompt_original": self.prompt_original,
            "vertical": self.vertical,
            "client_brand": self.client_brand,
            "product_meta": self.product_meta,
            "structure": self.structure,
            "data_known": self.data_known,
            "data_missing": self.data_missing,
            "user_question_emitted": self.user_question_emitted,
            "architect_model": self.architect_model,
            "architect_cost_usd": self.architect_cost_usd,
            "architect_duration_ms": self.architect_duration_ms,
        }


# ── Embrión principal ────────────────────────────────────────────────────────
@dataclass
class ProductArchitect:
    """
    Embrión que produce el Brief estructurado a partir del prompt del usuario.

    Args:
        _sabios: Cliente de Sabios para generación del Brief via LLM.
        _db: Cliente Supabase para persistir Briefs (opcional).
        verticals_dir: Path a kernel/brand/verticals/ con los YAMLs.
        budget_daily_usd: Presupuesto diario máximo en USD para LLM calls.

    Soberanía:
        - Llama LLM principal (GPT-4o o Claude Sonnet via _sabios.ask).
        - Fallback heurístico: detecta vertical por keywords si LLM falla.
        - Persiste a Supabase si hay db; si no, solo retorna el Brief.
    """

    _sabios: Optional[object] = field(default=None, repr=False)
    _db: Optional[object] = field(default=None, repr=False)
    verticals_dir: Optional[str] = None
    budget_daily_usd: float = 1.0
    _spent_today: float = field(default=0.0, repr=False)

    EMBRION_ID: str = field(default="product-architect", init=False)
    SPECIALIZATION: str = field(
        default="Análisis de prompts, contrato Brief, vertical detection",
        init=False,
    )

    def __post_init__(self):
        """Resolver verticals_dir si no fue pasado."""
        if self.verticals_dir is None:
            # kernel/brand/verticals/ relativo al repo
            here = Path(__file__).resolve().parent.parent
            self.verticals_dir = str(here / "brand" / "verticals")

    # ── API pública ──────────────────────────────────────────────────────
    async def producir_brief(
        self,
        prompt: str,
        user_response: Optional[str] = None,
    ) -> Brief:
        """
        Produce un Brief estructurado a partir del prompt del usuario.

        Args:
            prompt: Prompt original del usuario (ej: "landing del taller de Yuna").
            user_response: Si Architect ya hizo una user_question previamente
                y el usuario respondió, este es ese texto adicional.

        Returns:
            Brief con vertical detectado y contrato listo para el Executor.

        Raises:
            PRODUCT_ARCHITECT_SIN_SABIOS si no hay cliente LLM y se requiere
            análisis profundo (vertical ambiguo).
        """
        started = datetime.now(timezone.utc)
        full_prompt = prompt
        if user_response:
            full_prompt = f"{prompt}\n\n--- Respuesta del usuario ---\n{user_response}"

        # Paso 1: Detección de vertical (heurística primero, LLM si ambigua)
        vertical, vertical_confidence = self._detectar_vertical(full_prompt)
        logger.info(
            "vertical_detected",
            vertical=vertical,
            confidence=vertical_confidence,
            method="heuristic" if vertical_confidence >= 0.6 else "llm_required",
        )

        # Si la heurística no da confianza alta y hay LLM, refinamos
        if vertical_confidence < 0.6 and self._sabios:
            vertical = await self._refinar_vertical_con_llm(full_prompt, vertical)

        if vertical not in VERTICALES_VALIDOS:
            raise EmbrionProductArchitectError(
                PRODUCT_ARCHITECT_VERTICAL_DESCONOCIDO.format(
                    vertical=vertical, validos=", ".join(VERTICALES_VALIDOS)
                )
            )

        # Paso 2: Cargar template del vertical
        template = self._cargar_vertical_template(vertical)

        # Paso 3: Generar Brief estructurado (LLM o heurístico)
        if self._sabios:
            brief = await self._generar_brief_con_llm(
                full_prompt, vertical, template
            )
        else:
            brief = self._generar_brief_heuristico(
                full_prompt, vertical, template
            )

        # Paso 4: Validar schema
        self._validar_brief(brief)

        # Paso 5: Identificar user_question si data_missing crítica
        if not brief.is_complete():
            brief.user_question_emitted = self._construir_user_question(brief)

        # Paso 6: Métricas
        elapsed_ms = int(
            (datetime.now(timezone.utc) - started).total_seconds() * 1000
        )
        brief.architect_duration_ms = elapsed_ms

        # Paso 7: Persistir si hay DB
        if self._db is not None and getattr(self._db, "_connected", False):
            try:
                row = brief.to_dict()
                inserted = await self._db.insert("briefs", row)
                if inserted:
                    brief.brief_id = str(inserted.get("id", ""))
                    logger.info(
                        "brief_persisted",
                        brief_id=brief.brief_id,
                        vertical=brief.vertical,
                        complete=brief.is_complete(),
                    )
            except Exception as exc:
                logger.warning("brief_persist_failed", error=str(exc))

        return brief

    # ── Detección de vertical ────────────────────────────────────────────
    def _detectar_vertical(self, text: str) -> tuple[str, float]:
        """
        Heurística rápida: cuenta keywords de cada vertical con word boundaries.

        HOTFIX Sprint 85 (post-audit 84.5): reemplazado substring matching
        por regex `\b...\b` para evitar falsos positivos como "artesanal"
        matcheando `arte` o "saasa" matcheando `saas`.

        Returns:
            (vertical, confidence) — confidence en [0.0, 1.0].
        """
        scores: dict[str, int] = {}
        for vertical, keywords in VERTICALES_KEYWORDS.items():
            pattern = _PATTERN_CACHE.get(vertical)
            if pattern is None:
                pattern = _compile_vertical_pattern(tuple(keywords))
                _PATTERN_CACHE[vertical] = pattern
            scores[vertical] = len(pattern.findall(text))

        if not scores or max(scores.values()) == 0:
            return ("professional_services", 0.0)  # Fallback genérico

        best = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = scores[best] / total if total > 0 else 0.0
        return (best, confidence)

    async def _refinar_vertical_con_llm(
        self, prompt: str, vertical_inicial: str
    ) -> str:
        """Pregunta al LLM cuál vertical es el correcto cuando hay ambigüedad."""
        verticales_str = "\n".join(f"- {v}" for v in VERTICALES_VALIDOS)
        llm_prompt = f"""Eres el Product Architect del Monstruo.

El usuario escribió este prompt:
"{prompt}"

La heurística sugiere el vertical: {vertical_inicial}, pero hay baja confianza.

Verticales válidos:
{verticales_str}

Responde ÚNICAMENTE con el nombre exacto de UN vertical de la lista. Sin explicación."""

        try:
            response = await self._sabios.ask(llm_prompt)
            response_clean = (response or "").strip().lower().split()[0] if response else ""
            if response_clean in VERTICALES_VALIDOS:
                return response_clean
        except Exception as exc:
            logger.warning("vertical_refine_llm_failed", error=str(exc))

        return vertical_inicial  # Fallback al de heurística

    # ── Template loader ─────────────────────────────────────────────────
    def _cargar_vertical_template(self, vertical: str) -> dict[str, Any]:
        """Carga el YAML del vertical desde kernel/brand/verticals/."""
        try:
            import yaml
        except ImportError:
            logger.warning("pyyaml_not_installed", hint="pip install pyyaml")
            return {}

        path = Path(self.verticals_dir) / f"{vertical}.yaml"
        if not path.exists():
            logger.warning("vertical_template_not_found", vertical=vertical, path=str(path))
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as exc:
            logger.warning("vertical_template_load_failed", vertical=vertical, error=str(exc))
            return {}

    # ── Generación del Brief ────────────────────────────────────────────
    async def _generar_brief_con_llm(
        self,
        prompt: str,
        vertical: str,
        template: dict[str, Any],
    ) -> Brief:
        """Pide al LLM que produzca el Brief en JSON estructurado."""
        template_str = json.dumps(template, ensure_ascii=False, indent=2)
        llm_prompt = f"""Eres el Product Architect del Monstruo. Tu trabajo es producir un Brief estructurado para que el Executor construya un sitio web comercializable, NO genérico.

Prompt del usuario:
"{prompt}"

Vertical detectado: {vertical}

Template del vertical (estructura esperada):
{template_str}

Produce un Brief en JSON con EXACTAMENTE estas keys:
- vertical: "{vertical}"
- client_brand: {{name, tagline, tone, color_palette, font_pair}}
- product_meta: {{value_proposition, target_audience, differentiator}}
- structure: {{sections, primary_cta, secondary_cta, hero_message}}
- data_known: {{... lo que el prompt SÍ dice}}
- data_missing: ["lista de keys críticas que el prompt NO dice"]

REGLAS:
1. Si el prompt no dice algo crítico (ej: nombre del cliente), pónlo en data_missing.
2. NO inventes datos. Si no sabes, dilo en data_missing.
3. Las keys de data_missing usan dot-notation: "client_brand.name", "product_meta.value_proposition".
4. Devuelve ÚNICAMENTE el JSON, sin explicación ni markdown.

JSON:"""

        try:
            response = await self._sabios.ask(llm_prompt)
            brief_json = self._extraer_json(response or "")
            return Brief(
                prompt_original=prompt,
                vertical=vertical,
                client_brand=brief_json.get("client_brand", {}),
                product_meta=brief_json.get("product_meta", {}),
                structure=brief_json.get("structure", {}),
                data_known=brief_json.get("data_known", {}),
                data_missing=brief_json.get("data_missing", []),
                architect_model=getattr(self._sabios, "model_name", None),
            )
        except Exception as exc:
            logger.warning(
                "brief_llm_generation_failed",
                error=str(exc),
                fallback="heuristic",
            )
            return self._generar_brief_heuristico(prompt, vertical, template)

    def _generar_brief_heuristico(
        self,
        prompt: str,
        vertical: str,
        template: dict[str, Any],
    ) -> Brief:
        """Genera un Brief mínimo sin LLM. Usado como fallback."""
        # data_known: lo único que sabemos es el prompt
        data_known = {"prompt_text": prompt, "vertical_inferred": vertical}

        # data_missing: todo lo crítico, porque sin LLM no podemos extraer
        data_missing = list(CRITICAL_DATA_KEYS)

        # Defaults del template (si lo cargamos)
        defaults = template.get("defaults", {})
        client_brand = defaults.get("client_brand", {})
        product_meta = defaults.get("product_meta", {})
        structure = defaults.get("structure", {
            "sections": ["hero", "about", "services", "contact"],
            "primary_cta": "Contactar",
            "hero_message": "Pendiente — completar con info del cliente",
        })

        return Brief(
            prompt_original=prompt,
            vertical=vertical,
            client_brand=client_brand,
            product_meta=product_meta,
            structure=structure,
            data_known=data_known,
            data_missing=data_missing,
            architect_model="heuristic",
        )

    # ── Validación ──────────────────────────────────────────────────────
    def _validar_brief(self, brief: Brief) -> None:
        """Verifica que el Brief tenga las keys mínimas."""
        d = brief.to_dict()
        missing = BRIEF_SCHEMA_KEYS - set(d.keys())
        if missing:
            raise EmbrionProductArchitectError(
                PRODUCT_ARCHITECT_BRIEF_INVALIDO.format(
                    missing_keys=", ".join(sorted(missing))
                )
            )

    # ── User question ──────────────────────────────────────────────────
    def _construir_user_question(self, brief: Brief) -> str:
        """Construye la pregunta al usuario cuando falta info crítica."""
        partes = []
        for key in brief.data_missing:
            if key not in CRITICAL_DATA_KEYS:
                continue
            if key == "client_brand.name":
                partes.append("¿Cuál es el nombre del proyecto/marca?")
            elif key == "product_meta.value_proposition":
                partes.append("¿Cuál es el valor diferenciador (qué hace único a este negocio)?")
            elif key == "structure.primary_cta":
                partes.append("¿Cuál es la acción principal que debe hacer el visitante (reservar, comprar, contactar)?")

        if not partes:
            return ""

        return (
            "Para construir un sitio comercializable necesito 3 datos:\n"
            + "\n".join(f"  • {p}" for p in partes)
        )

    # ── Helpers ─────────────────────────────────────────────────────────
    @staticmethod
    def _extraer_json(text: str) -> dict[str, Any]:
        """Extrae el primer bloque JSON válido de la respuesta del LLM."""
        text = text.strip()
        # Quitar markdown code fences si existen
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

        # Intentar parse directo
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Buscar el primer { ... } bloque
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError as exc:
                logger.warning("json_extract_failed", error=str(exc))

        return {}

    def estado(self) -> dict[str, Any]:
        """Estado del embrión para el Command Center."""
        return {
            "embrion_id": self.EMBRION_ID,
            "specialization": self.SPECIALIZATION,
            "estado": "activo" if self._sabios else "fallback_heuristico",
            "verticales_soportados": VERTICALES_VALIDOS,
            "verticals_dir": self.verticals_dir,
            "spent_today_usd": round(self._spent_today, 4),
            "budget_daily_usd": self.budget_daily_usd,
        }
