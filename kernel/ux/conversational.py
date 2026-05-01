"""
El Monstruo — Conversational UX Layer (Sprint 59.2)
=====================================================
Capa de abstracción que traduce lenguaje natural del usuario
en intents ejecutables por el sistema.

Principio: "Máximo Poder, Mínima Complejidad" (Objetivo #3)
El usuario dice QUÉ quiere. El Monstruo decide CÓMO hacerlo.

Flujo:
  Usuario: "Quiero una tienda de ropa para Japón"
      ↓
  ConversationalUX.parse_intent()
      ↓
  Intent: CREATE_BUSINESS {type: ecommerce, niche: clothing, market: ja}
      ↓
  Orchestrator dispatches to EmbrionVentas + EmbrionCreativo + EmbrionEstratega

Objetivo: #3 — Máximo Poder, Mínima Complejidad
Sprint: 59 — "El Monstruo Habla al Mundo"
Fecha: 2026-05-01

Soberanía:
  - GPT-4o-mini (primario, intent parsing)
  - Gemini Flash (fallback, si OpenAI falla)
  - Heurísticas de quick commands (sin LLM, cero costo)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any

import structlog

logger = structlog.get_logger("monstruo.ux.conversational")


# ── Errores con identidad ──────────────────────────────────────────────────────

class CONVERSATIONAL_UX_SIN_SABIOS(RuntimeError):
    """No hay cliente de Sabios configurado para parsear intents.
    
    Sugerencia: Inyecta _sabios al instanciar ConversationalUX o usa quick commands.
    """


class CONVERSATIONAL_UX_INTENT_INVALIDO(ValueError):
    """El intent recibido no es un IntentType válido.
    
    Sugerencia: Verifica que el LLM retornó un JSON con el campo 'intent' correcto.
    """


# ── Enums ──────────────────────────────────────────────────────────────────────

class IntentType(str, Enum):
    """Intents reconocidos por el sistema."""
    CREATE_BUSINESS = "create_business"
    MODIFY_BUSINESS = "modify_business"
    ANALYZE_MARKET = "analyze_market"
    PREDICT_OUTCOME = "predict_outcome"
    GENERATE_CONTENT = "generate_content"
    MANAGE_FINANCES = "manage_finances"
    RESEARCH_TOPIC = "research_topic"
    SCHEDULE_TASK = "schedule_task"
    CHECK_STATUS = "check_status"
    HELP = "help"
    UNKNOWN = "unknown"


# ── Dataclasses ────────────────────────────────────────────────────────────────

@dataclass
class ParsedIntent:
    """Intent parseado del input del usuario.
    
    Args:
        type: Tipo de intent detectado.
        confidence: Confianza del parser (0.0 - 1.0).
        parameters: Parámetros extraídos del texto.
        original_text: Texto original del usuario.
        locale: Idioma detectado del input.
        clarification_needed: Pregunta de aclaración si confidence < threshold.
    """
    type: IntentType
    confidence: float
    parameters: dict[str, Any] = field(default_factory=dict)
    original_text: str = ""
    locale: str = "es"
    clarification_needed: Optional[str] = None

    def to_dict(self) -> dict:
        """Serializar para el Command Center."""
        return {
            "type": self.type.value,
            "confidence": self.confidence,
            "parameters": self.parameters,
            "original_text": self.original_text[:200],
            "locale": self.locale,
            "clarification_needed": self.clarification_needed,
        }


# ── Quick Commands (shortcuts sin LLM) ────────────────────────────────────────

QUICK_COMMANDS: dict[str, IntentType] = {
    "/nuevo": IntentType.CREATE_BUSINESS,
    "/new": IntentType.CREATE_BUSINESS,
    "/analizar": IntentType.ANALYZE_MARKET,
    "/analyze": IntentType.ANALYZE_MARKET,
    "/predecir": IntentType.PREDICT_OUTCOME,
    "/predict": IntentType.PREDICT_OUTCOME,
    "/estado": IntentType.CHECK_STATUS,
    "/status": IntentType.CHECK_STATUS,
    "/ayuda": IntentType.HELP,
    "/help": IntentType.HELP,
    "/contenido": IntentType.GENERATE_CONTENT,
    "/content": IntentType.GENERATE_CONTENT,
    "/finanzas": IntentType.MANAGE_FINANCES,
    "/finance": IntentType.MANAGE_FINANCES,
}

# Sugerencias de próximas acciones por intent
NEXT_ACTIONS_BY_INTENT: dict[IntentType, list[str]] = {
    IntentType.CREATE_BUSINESS: [
        "¿Quieres que analice la competencia en ese mercado?",
        "¿Necesitas que genere el branding (logo, colores, nombre)?",
        "¿Quieres una predicción de viabilidad antes de empezar?",
    ],
    IntentType.ANALYZE_MARKET: [
        "¿Quieres que simule escenarios de entrada al mercado?",
        "¿Necesitas un plan financiero basado en este análisis?",
        "¿Quieres que identifique oportunidades no explotadas?",
    ],
    IntentType.PREDICT_OUTCOME: [
        "¿Quieres que ejecute más simulaciones con parámetros diferentes?",
        "¿Necesitas un plan de mitigación para los riesgos identificados?",
    ],
    IntentType.GENERATE_CONTENT: [
        "¿Quieres que adapte el contenido para otros idiomas?",
        "¿Necesitas variantes A/B del mismo contenido?",
    ],
    IntentType.CHECK_STATUS: [
        "¿Quieres un reporte detallado de algún componente específico?",
    ],
}

INTENT_PARSE_PROMPT = """Analyze this user request and extract the intent.

User said: "{user_input}"

Respond in JSON format ONLY:
{{
    "intent": "<one of: create_business, modify_business, analyze_market, predict_outcome, generate_content, manage_finances, research_topic, schedule_task, check_status, help, unknown>",
    "confidence": <0.0 to 1.0>,
    "parameters": {{
        "business_type": "<if applicable: ecommerce, saas, content, service, marketplace>",
        "niche": "<specific niche or industry>",
        "target_market": "<country/region code>",
        "budget": "<if mentioned>",
        "timeline": "<if mentioned>",
        "specific_request": "<any specific detail>"
    }},
    "clarification": "<null or question to ask user if confidence < 0.7>"
}}

Rules:
- Be precise. If confidence < 0.7, ask for clarification.
- Remove null/empty parameters from the response.
- The clarification question must be in the same language as the user input."""


# ── Capa principal ─────────────────────────────────────────────────────────────

@dataclass
class ConversationalUX:
    """Capa de UX conversacional de El Monstruo.
    
    Traduce lenguaje natural en intents ejecutables.
    Soporta quick commands sin LLM para máxima velocidad.
    
    Args:
        _sabios: Cliente de Sabios para intent parsing (soberanía: quick commands sin LLM).
        _i18n: Motor i18n para detección de idioma (opcional).
        confidence_threshold: Umbral mínimo de confianza para ejecutar sin aclaración.
    
    Soberanía:
        - LLM intent parsing → heurísticas keyword si Sabios no disponible
        - DeepL detection → charset heuristics si i18n no disponible
    """
    _sabios: Optional[object] = field(default=None, repr=False)
    _i18n: Optional[object] = field(default=None, repr=False)
    confidence_threshold: float = 0.7
    _total_parses: int = field(default=0, repr=False)
    _clarifications_requested: int = field(default=0, repr=False)

    async def parse_intent(self, user_input: str) -> ParsedIntent:
        """Parsear intent del usuario usando LLM con fallback a heurísticas.
        
        Args:
            user_input: Texto del usuario a analizar.
        
        Returns:
            ParsedIntent con type, confidence, parameters y locale detectado.
        
        Soberanía:
            1. Quick command detection (sin LLM, cero costo)
            2. LLM parsing via Sabios
            3. Heurística keyword (si Sabios no disponible)
        """
        if not user_input or not user_input.strip():
            return ParsedIntent(
                type=IntentType.UNKNOWN,
                confidence=0.0,
                original_text=user_input,
                clarification_needed="¿En qué puedo ayudarte?",
            )

        # Estrategia 1: Quick commands (sin LLM, cero costo)
        quick_intent = check_quick_command(user_input)
        if quick_intent:
            logger.info("quick_command_detectado", intent=quick_intent.value)
            return ParsedIntent(
                type=quick_intent,
                confidence=1.0,
                original_text=user_input,
                locale="es",
            )

        # Detectar idioma
        locale = "es"
        if self._i18n:
            locale = await self._i18n.detect_language(user_input)

        # Estrategia 2: LLM parsing
        if self._sabios:
            try:
                prompt = INTENT_PARSE_PROMPT.format(user_input=user_input[:500])
                response = await self._sabios.ask(prompt)

                json_str = response.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0]
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0]

                parsed = json.loads(json_str)
                intent_type = IntentType(parsed.get("intent", "unknown"))
                confidence = float(parsed.get("confidence", 0.5))
                parameters = {
                    k: v for k, v in parsed.get("parameters", {}).items()
                    if v and v != "null"
                }
                clarification = (
                    parsed.get("clarification")
                    if confidence < self.confidence_threshold else None
                )

                self._total_parses += 1
                if clarification:
                    self._clarifications_requested += 1

                logger.info(
                    "intent_parseado",
                    intent=intent_type.value,
                    confidence=confidence,
                    locale=locale,
                )
                return ParsedIntent(
                    type=intent_type,
                    confidence=confidence,
                    parameters=parameters,
                    original_text=user_input,
                    locale=locale,
                    clarification_needed=clarification,
                )

            except (json.JSONDecodeError, ValueError) as _e:
                logger.warning("intent_parse_fallo", error=str(_e), input=user_input[:100])

        # Estrategia 3: Heurística keyword (sin LLM)
        return self._heuristic_parse(user_input, locale)

    def _heuristic_parse(self, text: str, locale: str) -> ParsedIntent:
        """Fallback heurístico para cuando Sabios no está disponible.
        
        Args:
            text: Texto del usuario.
            locale: Idioma detectado.
        
        Returns:
            ParsedIntent con confidence baja pero funcional.
        """
        text_lower = text.lower()
        keywords = {
            IntentType.CREATE_BUSINESS: ["crear", "nuevo", "emprender", "start", "create", "build", "lanzar"],
            IntentType.ANALYZE_MARKET: ["analizar", "mercado", "analyze", "market", "competencia"],
            IntentType.PREDICT_OUTCOME: ["predecir", "predict", "simular", "simulate", "forecast"],
            IntentType.CHECK_STATUS: ["estado", "status", "cómo va", "how is", "reporte"],
            IntentType.GENERATE_CONTENT: ["generar", "escribir", "generate", "write", "contenido"],
            IntentType.MANAGE_FINANCES: ["finanzas", "dinero", "finance", "money", "presupuesto"],
        }
        for intent_type, words in keywords.items():
            if any(w in text_lower for w in words):
                return ParsedIntent(
                    type=intent_type,
                    confidence=0.4,
                    original_text=text,
                    locale=locale,
                    clarification_needed="¿Podrías darme más detalles sobre lo que necesitas?",
                )

        return ParsedIntent(
            type=IntentType.UNKNOWN,
            confidence=0.0,
            original_text=text,
            locale=locale,
            clarification_needed="No entendí tu solicitud. ¿Podrías reformularla?",
        )

    async def generate_response(self, intent: ParsedIntent, result: dict) -> str:
        """Generar respuesta conversacional basada en el resultado de la acción.
        
        Args:
            intent: Intent original del usuario.
            result: Resultado de la acción ejecutada.
        
        Returns:
            Respuesta en lenguaje natural en el idioma del usuario.
        """
        if intent.clarification_needed:
            return intent.clarification_needed

        if not self._sabios:
            return json.dumps(result, indent=2, default=str)

        locale_instruction = (
            f"Respond in {intent.locale}." if intent.locale != "es" else ""
        )
        prompt = (
            f"Generate a friendly, concise response for the user.\n"
            f"{locale_instruction}\n\n"
            f"Their request was: \"{intent.original_text}\"\n"
            f"The system processed it as: {intent.type.value}\n"
            f"The result was: {json.dumps(result, default=str)[:2000]}\n\n"
            f"Write a natural, helpful response that:\n"
            f"1. Confirms what was done\n"
            f"2. Highlights key outcomes\n"
            f"3. Suggests next steps if applicable\n"
            f"Keep it under 200 words."
        )
        return await self._sabios.ask(prompt)

    async def suggest_next_actions(self, intent: ParsedIntent) -> list[str]:
        """Sugerir próximas acciones basadas en el intent actual.
        
        Args:
            intent: Intent parseado del usuario.
        
        Returns:
            Lista de sugerencias de próximas acciones.
        """
        return NEXT_ACTIONS_BY_INTENT.get(
            intent.type, ["¿En qué más puedo ayudarte?"]
        )

    def to_dict(self) -> dict:
        """Estado de la capa para consumo del Command Center.
        
        Returns:
            Dict serializable con métricas y estado actual.
        """
        return {
            "componente": "conversational_ux",
            "version": "1.0.0-sprint59",
            "objetivo": "#3 Máximo Poder, Mínima Complejidad",
            "backends_activos": {
                "sabios": self._sabios is not None,
                "i18n": self._i18n is not None,
            },
            "confidence_threshold": self.confidence_threshold,
            "quick_commands_disponibles": list(QUICK_COMMANDS.keys()),
            "intents_soportados": [e.value for e in IntentType],
            "metricas": {
                "total_parses": self._total_parses,
                "clarifications_requested": self._clarifications_requested,
            },
        }


# ── Helpers de módulo ──────────────────────────────────────────────────────────

def check_quick_command(text: str) -> Optional[IntentType]:
    """Verificar si el texto es un quick command (sin LLM, cero costo).
    
    Args:
        text: Texto del usuario.
    
    Returns:
        IntentType si es un quick command, None si no lo es.
    """
    first_word = text.strip().split()[0].lower() if text.strip() else ""
    return QUICK_COMMANDS.get(first_word)
