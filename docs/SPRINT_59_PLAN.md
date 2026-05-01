# Sprint 59 — "El Monstruo Habla al Mundo"

**Fecha:** 1 mayo 2026
**Autor:** Manus AI
**Tema:** Internacionalización, UX Conversacional, y Embriones Creativos
**Dependencias:** Sprints 51-58 (especialmente 54: EmbrionLoop, 57: Embrión-Ventas, 58: Embrión-Técnico/Vigía)

---

## Resumen Ejecutivo

Sprint 59 aborda los tres gaps más vergonzosos del proyecto después de 8 sprints: el Objetivo #13 (Del Mundo) que lleva 0% de cobertura, el Objetivo #3 (Mínima Complejidad) cuya UX para el usuario final nunca fue abordada, y el Objetivo #8 (Inteligencia Emergente) que carece de evidencia demostrable. Además, avanza el Objetivo #11 creando 2 embriones especializados adicionales (5/7 total).

El nombre "El Monstruo Habla al Mundo" refleja la transformación: de un sistema técnico interno a un producto accesible para cualquier persona en cualquier idioma.

---

## Stack Validado en Tiempo Real

| Herramienta | Versión | Fecha Release | Uso en Sprint 59 |
|---|---|---|---|
| DeepL Python SDK | 1.30.0 | Apr 9, 2026 | Motor de traducción profesional |
| react-i18next | ~15.x | 2026 | Template i18n para proyectos React |
| Babel (Python) | ~2.16.x | 2026 | Locale data y formatting |
| LLM Translation (Sabios) | — | — | Fallback soberano sin dependencia externa |

---

## Épica 59.1 — i18n Engine (Objetivo #13)

### Contexto

El Monstruo dice crear "empresas digitales" pero solo funciona en español. No hay una sola línea de código de internacionalización en todo el codebase (confirmado con grep exhaustivo). Esto es inaceptable para un sistema que aspira a ser "Del Mundo."

### Arquitectura de Dos Niveles

**Nivel 1 — i18n Interno (El Monstruo mismo):**
- System prompts multilingües para los Sabios
- Logs y alerts en el idioma del usuario
- Detección automática de idioma del input

**Nivel 2 — i18n de Proyectos Generados:**
- Templates de i18n inyectables en proyectos React/Next.js
- Traducción automática de contenido generado
- Locale-aware formatting (fechas, monedas, números)

### Implementación

**Archivo:** `kernel/i18n/engine.py`

```python
"""
El Monstruo — i18n Engine (Sprint 59)
======================================
Motor de internacionalización de dos niveles:
1. Interno: El Monstruo opera en el idioma del usuario
2. Proyectos: Los proyectos generados nacen multilingües

Supported locales (initial): es, en, pt, fr, de, it, ja, zh, ko, ar
Sprint 59 — 2026-05-01
"""
from __future__ import annotations
import os
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import structlog

logger = structlog.get_logger("monstruo.i18n")


class SupportedLocale(str, Enum):
    ES = "es"  # Español (default)
    EN = "en"  # English
    PT = "pt"  # Português
    FR = "fr"  # Français
    DE = "de"  # Deutsch
    IT = "it"  # Italiano
    JA = "ja"  # 日本語
    ZH = "zh"  # 中文
    KO = "ko"  # 한국어
    AR = "ar"  # العربية


@dataclass
class LocaleConfig:
    """Configuration for a specific locale."""
    code: str
    name: str
    direction: str = "ltr"  # "ltr" or "rtl"
    date_format: str = "YYYY-MM-DD"
    currency: str = "USD"
    number_separator: str = ","
    decimal_separator: str = "."


LOCALE_CONFIGS: dict[str, LocaleConfig] = {
    "es": LocaleConfig("es", "Español", currency="MXN", number_separator=",", decimal_separator="."),
    "en": LocaleConfig("en", "English", currency="USD"),
    "pt": LocaleConfig("pt", "Português", currency="BRL", number_separator=".", decimal_separator=","),
    "fr": LocaleConfig("fr", "Français", currency="EUR", number_separator=" ", decimal_separator=","),
    "de": LocaleConfig("de", "Deutsch", currency="EUR", number_separator=".", decimal_separator=","),
    "it": LocaleConfig("it", "Italiano", currency="EUR", number_separator=".", decimal_separator=","),
    "ja": LocaleConfig("ja", "日本語", currency="JPY", number_separator=","),
    "zh": LocaleConfig("zh", "中文", currency="CNY", number_separator=","),
    "ko": LocaleConfig("ko", "한국어", currency="KRW", number_separator=","),
    "ar": LocaleConfig("ar", "العربية", direction="rtl", currency="SAR"),
}


@dataclass
class I18nEngine:
    """Motor de internacionalización de El Monstruo."""
    
    default_locale: str = "es"
    _translator: Optional[object] = field(default=None, repr=False)
    _sabios: Optional[object] = field(default=None, repr=False)
    
    async def detect_language(self, text: str) -> str:
        """Detectar idioma del texto usando heurísticas + LLM fallback."""
        # Fast heuristic: character set detection
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            return "zh"
        if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text):
            return "ja"
        if any('\uac00' <= c <= '\ud7af' for c in text):
            return "ko"
        if any('\u0600' <= c <= '\u06ff' for c in text):
            return "ar"
        
        # LLM-based detection for Latin scripts
        if self._sabios:
            prompt = f"Detect the language of this text. Reply with ONLY the ISO 639-1 code (es, en, pt, fr, de, it): '{text[:200]}'"
            response = await self._sabios.ask_fastest(prompt)
            code = response.strip().lower()[:2]
            if code in [e.value for e in SupportedLocale]:
                return code
        
        return self.default_locale
    
    async def translate(self, text: str, target_locale: str, 
                        source_locale: Optional[str] = None) -> str:
        """Traducir texto al locale objetivo."""
        if source_locale == target_locale:
            return text
        
        # Strategy 1: DeepL (highest quality for EU languages)
        if self._translator and target_locale in ("en", "es", "pt", "fr", "de", "it"):
            try:
                import deepl
                result = self._translator.translate_text(
                    text, 
                    target_lang=target_locale.upper(),
                    source_lang=source_locale.upper() if source_locale else None,
                )
                logger.info("translated_deepl", target=target_locale, chars=len(text))
                return result.text
            except Exception as e:
                logger.warning("deepl_fallback", error=str(e))
        
        # Strategy 2: LLM Translation (sovereign fallback)
        if self._sabios:
            locale_name = LOCALE_CONFIGS.get(target_locale, LocaleConfig(target_locale, target_locale)).name
            prompt = (
                f"Translate the following text to {locale_name}. "
                f"Maintain the tone, formatting, and technical terms. "
                f"Reply with ONLY the translation:\n\n{text}"
            )
            return await self._sabios.ask(prompt)
        
        logger.error("no_translation_backend")
        return text  # Return original if no backend available
    
    async def translate_batch(self, texts: list[str], target_locale: str) -> list[str]:
        """Traducir múltiples textos en batch (optimizado para DeepL)."""
        if self._translator and target_locale in ("en", "es", "pt", "fr", "de", "it"):
            try:
                import deepl
                results = self._translator.translate_text(
                    texts,
                    target_lang=target_locale.upper(),
                )
                return [r.text for r in results]
            except Exception:
                pass
        
        # Fallback: translate one by one
        return [await self.translate(t, target_locale) for t in texts]
    
    def get_locale_config(self, locale: str) -> LocaleConfig:
        """Obtener configuración de locale."""
        return LOCALE_CONFIGS.get(locale, LOCALE_CONFIGS["en"])
    
    def format_currency(self, amount: float, locale: str) -> str:
        """Formatear moneda según locale."""
        config = self.get_locale_config(locale)
        if config.currency in ("JPY", "KRW"):
            return f"{config.currency} {int(amount):,}".replace(",", config.number_separator)
        formatted = f"{amount:,.2f}".replace(",", "TEMP").replace(".", config.decimal_separator).replace("TEMP", config.number_separator)
        return f"{config.currency} {formatted}"
    
    def generate_i18n_template(self, framework: str = "react") -> dict[str, str]:
        """Generar template de i18n para proyectos."""
        if framework == "react":
            return self._react_i18n_template()
        elif framework == "nextjs":
            return self._nextjs_i18n_template()
        return {}
    
    def _react_i18n_template(self) -> dict[str, str]:
        """Template react-i18next para proyectos generados."""
        return {
            "src/i18n/index.ts": '''import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en.json';
import es from './locales/es.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: { en: { translation: en }, es: { translation: es } },
    fallbackLng: 'es',
    interpolation: { escapeValue: false },
  });

export default i18n;
''',
            "src/i18n/locales/es.json": json.dumps({
                "common": {
                    "welcome": "Bienvenido",
                    "loading": "Cargando...",
                    "error": "Ha ocurrido un error",
                    "save": "Guardar",
                    "cancel": "Cancelar",
                    "delete": "Eliminar",
                    "search": "Buscar",
                },
                "nav": {
                    "home": "Inicio",
                    "about": "Acerca de",
                    "contact": "Contacto",
                },
            }, indent=2, ensure_ascii=False),
            "src/i18n/locales/en.json": json.dumps({
                "common": {
                    "welcome": "Welcome",
                    "loading": "Loading...",
                    "error": "An error occurred",
                    "save": "Save",
                    "cancel": "Cancel",
                    "delete": "Delete",
                    "search": "Search",
                },
                "nav": {
                    "home": "Home",
                    "about": "About",
                    "contact": "Contact",
                },
            }, indent=2, ensure_ascii=False),
            "package_deps": '{"i18next": "^24.0.0", "react-i18next": "^15.0.0", "i18next-browser-languagedetector": "^8.0.0"}',
        }
    
    def _nextjs_i18n_template(self) -> dict[str, str]:
        """Template next-intl para proyectos Next.js."""
        return {
            "src/i18n/request.ts": '''import { getRequestConfig } from 'next-intl/server';

export default getRequestConfig(async ({ locale }) => ({
  messages: (await import(`./messages/${locale}.json`)).default,
}));
''',
            "package_deps": '{"next-intl": "^4.0.0"}',
        }


# ── System Prompt Localization ─────────────────────────────────────

SYSTEM_PROMPT_TEMPLATES = {
    "es": "Eres un asistente experto de El Monstruo. Responde siempre en español.",
    "en": "You are an expert assistant of El Monstruo. Always respond in English.",
    "pt": "Você é um assistente especialista de El Monstruo. Sempre responda em português.",
    "fr": "Vous êtes un assistant expert d'El Monstruo. Répondez toujours en français.",
    "de": "Du bist ein Experten-Assistent von El Monstruo. Antworte immer auf Deutsch.",
    "it": "Sei un assistente esperto di El Monstruo. Rispondi sempre in italiano.",
    "ja": "あなたはEl Monstruoの専門アシスタントです。常に日本語で回答してください。",
    "zh": "你是El Monstruo的专家助手。请始终用中文回答。",
    "ko": "당신은 El Monstruo의 전문 어시스턴트입니다. 항상 한국어로 응답하세요.",
    "ar": "أنت مساعد خبير في El Monstruo. أجب دائمًا باللغة العربية.",
}


def get_localized_system_prompt(locale: str, base_prompt: str = "") -> str:
    """Obtener system prompt localizado."""
    locale_instruction = SYSTEM_PROMPT_TEMPLATES.get(locale, SYSTEM_PROMPT_TEMPLATES["es"])
    return f"{base_prompt}\n\n{locale_instruction}" if base_prompt else locale_instruction
```

### Tabla Supabase

```sql
-- Sprint 59: Supported locales and user preferences
CREATE TABLE IF NOT EXISTS supported_locales (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    direction TEXT DEFAULT 'ltr',
    is_active BOOLEAN DEFAULT true,
    translation_quality FLOAT DEFAULT 0.0,  -- 0-1, measured by back-translation BLEU
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User locale preferences
ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS 
    preferred_locale TEXT DEFAULT 'es' REFERENCES supported_locales(code);
```

### Dependencias

```
# requirements.txt additions
deepl>=1.30.0
babel>=2.16.0
```

---

## Épica 59.2 — Conversational UX Layer (Objetivo #3)

### Contexto

El Monstruo tiene un poder enorme pero la interfaz para el usuario es técnica y compleja. No hay una forma simple de "pedir" un negocio. El Objetivo #3 dice "Máximo Poder, Mínima Complejidad" — Sprint 59 crea la capa que traduce lenguaje natural en acciones del sistema.

### Arquitectura

```
Usuario: "Quiero una tienda de ropa online para el mercado japonés"
    ↓
ConversationalUX.parse_intent()
    ↓
Intent: CREATE_BUSINESS
Params: {type: "ecommerce", niche: "clothing", market: "ja", locale: "ja"}
    ↓
Orchestrator dispatches to relevant Embriones
```

### Implementación

**Archivo:** `kernel/ux/conversational.py`

```python
"""
El Monstruo — Conversational UX Layer (Sprint 59)
===================================================
Capa de abstracción que traduce lenguaje natural del usuario
en intents ejecutables por el sistema.

Principio: "Máximo Poder, Mínima Complejidad"
El usuario dice QUÉ quiere. El Monstruo decide CÓMO hacerlo.

Sprint 59 — 2026-05-01
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
import structlog

logger = structlog.get_logger("monstruo.ux.conversational")


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


@dataclass
class ParsedIntent:
    """Intent parseado del input del usuario."""
    type: IntentType
    confidence: float  # 0.0 - 1.0
    parameters: dict[str, Any] = field(default_factory=dict)
    original_text: str = ""
    locale: str = "es"
    clarification_needed: Optional[str] = None  # If confidence < threshold


@dataclass
class ConversationalUX:
    """Capa de UX conversacional de El Monstruo."""
    
    _sabios: Optional[object] = field(default=None, repr=False)
    _i18n: Optional[object] = field(default=None, repr=False)
    confidence_threshold: float = 0.7
    
    async def parse_intent(self, user_input: str) -> ParsedIntent:
        """Parsear intent del usuario usando LLM."""
        if not self._sabios:
            return ParsedIntent(type=IntentType.UNKNOWN, confidence=0.0, original_text=user_input)
        
        # Detect language first
        locale = "es"
        if self._i18n:
            locale = await self._i18n.detect_language(user_input)
        
        prompt = f"""Analyze this user request and extract the intent.

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
    "clarification": "<null or question to ask if confidence < 0.7>"
}}"""
        
        response = await self._sabios.ask(prompt)
        
        try:
            # Parse JSON from LLM response
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            parsed = json.loads(json_str)
            
            intent_type = IntentType(parsed.get("intent", "unknown"))
            confidence = float(parsed.get("confidence", 0.5))
            parameters = parsed.get("parameters", {})
            # Remove null/empty params
            parameters = {k: v for k, v in parameters.items() if v and v != "null"}
            
            clarification = parsed.get("clarification") if confidence < self.confidence_threshold else None
            
            return ParsedIntent(
                type=intent_type,
                confidence=confidence,
                parameters=parameters,
                original_text=user_input,
                locale=locale,
                clarification_needed=clarification,
            )
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("intent_parse_failed", error=str(e), input=user_input[:100])
            return ParsedIntent(
                type=IntentType.UNKNOWN,
                confidence=0.0,
                original_text=user_input,
                locale=locale,
                clarification_needed="No entendí tu solicitud. ¿Podrías reformularla?",
            )
    
    async def generate_response(self, intent: ParsedIntent, result: dict) -> str:
        """Generar respuesta conversacional basada en el resultado."""
        if intent.clarification_needed:
            return intent.clarification_needed
        
        if not self._sabios:
            return json.dumps(result, indent=2)
        
        locale_instruction = f"Respond in {intent.locale}." if intent.locale != "es" else ""
        
        prompt = f"""Generate a friendly, concise response for the user.
{locale_instruction}

Their request was: "{intent.original_text}"
The system processed it as: {intent.type.value}
The result was: {json.dumps(result, default=str)[:2000]}

Write a natural, helpful response that:
1. Confirms what was done
2. Highlights key outcomes
3. Suggests next steps if applicable
Keep it under 200 words."""
        
        return await self._sabios.ask(prompt)
    
    async def suggest_next_actions(self, intent: ParsedIntent) -> list[str]:
        """Sugerir próximas acciones basadas en el intent actual."""
        suggestions = {
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
        }
        return suggestions.get(intent.type, ["¿En qué más puedo ayudarte?"])


# ── Quick Commands (shortcuts) ─────────────────────────────────────

QUICK_COMMANDS = {
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
}


def check_quick_command(text: str) -> Optional[IntentType]:
    """Verificar si el texto es un quick command."""
    first_word = text.strip().split()[0].lower() if text.strip() else ""
    return QUICK_COMMANDS.get(first_word)
```

### Integración con FastAPI

```python
# En kernel/main.py — nuevo endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Endpoint conversacional simplificado."""
    ux = ConversationalUX(_sabios=sabios, _i18n=i18n_engine)
    
    # Check quick commands first
    quick = check_quick_command(request.message)
    if quick:
        intent = ParsedIntent(type=quick, confidence=1.0, original_text=request.message)
    else:
        intent = await ux.parse_intent(request.message)
    
    # If clarification needed, return question
    if intent.clarification_needed:
        return ChatResponse(
            message=intent.clarification_needed,
            intent=intent.type.value,
            confidence=intent.confidence,
            needs_clarification=True,
        )
    
    # Dispatch to appropriate handler
    result = await dispatch_intent(intent)
    
    # Generate conversational response
    response_text = await ux.generate_response(intent, result)
    suggestions = await ux.suggest_next_actions(intent)
    
    return ChatResponse(
        message=response_text,
        intent=intent.type.value,
        confidence=intent.confidence,
        suggestions=suggestions,
        data=result,
    )
```

---

## Épica 59.3 — Embrión-Creativo (Objetivo #11)

### Contexto

4to embrión especializado. Se encarga de todo lo visual y creativo: branding, diseño, UX, color palettes, tipografía, y assets visuales. Hereda de `EmbrionLoop` (Sprint 54).

### Implementación

**Archivo:** `kernel/embriones/embrion_creativo.py`

```python
"""
El Monstruo — Embrión-Creativo (Sprint 59)
============================================
4to Embrión especializado.
Dominio: Diseño, branding, UX, identidad visual.

Hereda: EmbrionLoop (Sprint 54)
Hermanos: Embrión-Ventas (57), Embrión-Técnico (58), Embrión-Vigía (58)

Sprint 59 — 2026-05-01
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional
import structlog

logger = structlog.get_logger("monstruo.embrion.creativo")


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


@dataclass
class BrandIdentity:
    """Identidad de marca generada."""
    name_options: list[str]
    tagline: str
    color_palette: dict[str, str]  # {primary, secondary, accent, bg, text}
    typography: dict[str, str]  # {display_font, body_font}
    design_principles: list[str]
    mood: str  # "minimal", "bold", "playful", "elegant", "brutalist"
    logo_prompt: str  # Prompt para generar logo con AI


@dataclass
class EmbrionCreativo:
    """Embrión especializado en diseño y creatividad."""
    
    _sabios: Optional[object] = field(default=None, repr=False)
    budget_daily_usd: float = 1.5
    _spent_today: float = 0.0
    
    # ── Tareas Autónomas ───────────────────────────────────────────
    
    DEFAULT_TASKS = {
        "brand_generation": {
            "description": "Generar identidad de marca completa para un proyecto",
            "interval_hours": 0,  # On-demand only
            "handler": "generate_brand_identity",
        },
        "design_review": {
            "description": "Revisar diseño de proyecto contra estándares Apple/Tesla",
            "interval_hours": 0,  # On-demand only
            "handler": "review_design_quality",
        },
        "trend_scan": {
            "description": "Escanear tendencias de diseño actuales",
            "interval_hours": 24,
            "handler": "scan_design_trends",
        },
        "palette_generator": {
            "description": "Generar paletas de color basadas en industria/mood",
            "interval_hours": 0,  # On-demand only
            "handler": "generate_color_palette",
        },
    }
    
    async def generate_brand_identity(self, niche: str, target_audience: str,
                                       mood: str = "elegant", locale: str = "es") -> BrandIdentity:
        """Generar identidad de marca completa."""
        if not self._sabios:
            raise RuntimeError("Sabios not configured")
        
        prompt = f"""Generate a complete brand identity for:
- Niche: {niche}
- Target audience: {target_audience}
- Mood/Style: {mood}
- Primary market locale: {locale}

Respond in JSON:
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
    "design_principles": ["principle1", "principle2", "principle3"],
    "mood": "{mood}",
    "logo_prompt": "Detailed prompt for AI image generation of the logo"
}}

RULES:
- Names must be memorable, pronounceable in {locale}, and available as .com domain
- Colors must have WCAG AA contrast ratios
- Fonts must be available on Google Fonts
- Logo prompt must be specific enough for high-quality AI generation
- NO generic choices. Be bold and distinctive."""
        
        response = await self._sabios.ask(prompt)
        data = json.loads(self._extract_json(response))
        
        return BrandIdentity(
            name_options=data["name_options"],
            tagline=data["tagline"],
            color_palette=data["color_palette"],
            typography=data["typography"],
            design_principles=data["design_principles"],
            mood=data["mood"],
            logo_prompt=data["logo_prompt"],
        )
    
    async def review_design_quality(self, design_description: str,
                                     screenshots: list[str] = None) -> dict:
        """Revisar calidad de diseño contra estándares Apple/Tesla."""
        prompt = f"""Review this design against Apple/Tesla quality standards.

Design description: {design_description}

Score each dimension (0-10) and provide specific feedback:
1. Typography (hierarchy, readability, personality)
2. Color (harmony, contrast, intentionality)
3. Layout (balance, whitespace, flow)
4. Consistency (tokens, patterns, repetition)
5. Originality (distinctiveness, avoids "AI slop")

Respond in JSON:
{{
    "scores": {{"typography": N, "color": N, "layout": N, "consistency": N, "originality": N}},
    "overall": N,
    "strengths": ["..."],
    "weaknesses": ["..."],
    "specific_fixes": ["actionable fix 1", "actionable fix 2", "..."]
}}"""
        
        response = await self._sabios.ask(prompt)
        return json.loads(self._extract_json(response))
    
    async def generate_color_palette(self, industry: str, mood: str,
                                      base_color: Optional[str] = None) -> dict:
        """Generar paleta de colores basada en industria y mood."""
        prompt = f"""Generate a professional color palette for:
- Industry: {industry}
- Mood: {mood}
- Base color (optional): {base_color or 'choose the best'}

Requirements:
- 5 colors: primary, secondary, accent, background, text
- WCAG AA compliant contrast ratios
- Harmonious (analogous, complementary, or split-complementary)
- NOT generic (no default blue, no purple gradients)

Respond in JSON:
{{
    "palette": {{
        "primary": {{"hex": "#...", "name": "...", "usage": "..."}},
        "secondary": {{"hex": "#...", "name": "...", "usage": "..."}},
        "accent": {{"hex": "#...", "name": "...", "usage": "..."}},
        "background": {{"hex": "#...", "name": "...", "usage": "..."}},
        "text": {{"hex": "#...", "name": "...", "usage": "..."}}
    }},
    "harmony_type": "...",
    "rationale": "..."
}}"""
        
        response = await self._sabios.ask(prompt)
        return json.loads(self._extract_json(response))
    
    async def scan_design_trends(self) -> dict:
        """Escanear tendencias actuales de diseño."""
        prompt = """What are the current top 5 web/app design trends in 2026?
For each trend, provide:
1. Name
2. Description (2 sentences)
3. Best suited for (type of project)
4. Example implementation tip

Respond in JSON array format."""
        
        response = await self._sabios.ask(prompt)
        return json.loads(self._extract_json(response))
    
    @staticmethod
    def _extract_json(text: str) -> str:
        """Extraer JSON de respuesta LLM."""
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        if "```" in text:
            return text.split("```")[1].split("```")[0]
        return text.strip()
```

---

## Épica 59.4 — Embrión-Estratega (Objetivo #11)

### Contexto

5to embrión especializado. Se encarga de planning estratégico, roadmaps, análisis de mercado, priorización, y decisiones de alto nivel. Reutiliza `InvestigadorRealidad` (ya existente en skills/) como herramienta de research.

### Implementación

**Archivo:** `kernel/embriones/embrion_estratega.py`

```python
"""
El Monstruo — Embrión-Estratega (Sprint 59)
=============================================
5to Embrión especializado.
Dominio: Estrategia, planning, market analysis, priorización.

Hereda: EmbrionLoop (Sprint 54)
Hermanos: Ventas (57), Técnico (58), Vigía (58), Creativo (59)
Herramienta: InvestigadorRealidad (skills/)

Sprint 59 — 2026-05-01
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional
import structlog

logger = structlog.get_logger("monstruo.embrion.estratega")


STRATEGIST_SYSTEM_PROMPT = """Eres el Embrión-Estratega de El Monstruo.
Tu dominio es la ESTRATEGIA y el PENSAMIENTO de alto nivel:
- Market Analysis: tamaño de mercado, competencia, oportunidades
- Business Planning: modelos de negocio, unit economics, go-to-market
- Prioritization: qué hacer primero, qué ignorar, qué delegar
- Risk Assessment: identificar riesgos y planes de mitigación
- Roadmapping: secuenciar acciones para máximo impacto

PRINCIPIOS:
- Datos sobre opiniones. Siempre busca evidencia.
- First principles thinking. Descompón problemas complejos.
- Contrarian thinking. Cuestiona assumptions populares.
- Speed of execution > perfection of plan.

RESTRICCIONES:
- Nunca recomiendes sin justificación cuantitativa
- Siempre incluye al menos un escenario pesimista
- Identifica los 3 riesgos principales de cada recomendación
"""


@dataclass
class MarketAnalysis:
    """Análisis de mercado estructurado."""
    market_size_usd: str  # TAM
    growth_rate: str
    key_players: list[dict]  # [{name, market_share, strength, weakness}]
    opportunities: list[str]
    threats: list[str]
    entry_barriers: list[str]
    recommended_positioning: str


@dataclass
class StrategicPlan:
    """Plan estratégico con fases."""
    vision: str
    phases: list[dict]  # [{name, duration, objectives, kpis, budget}]
    risks: list[dict]  # [{risk, probability, impact, mitigation}]
    success_metrics: list[str]
    kill_criteria: list[str]  # When to abandon


@dataclass
class EmbrionEstratega:
    """Embrión especializado en estrategia y planning."""
    
    _sabios: Optional[object] = field(default=None, repr=False)
    budget_daily_usd: float = 2.0
    _spent_today: float = 0.0
    
    DEFAULT_TASKS = {
        "market_scan": {
            "description": "Escanear oportunidades de mercado para proyectos activos",
            "interval_hours": 12,
            "handler": "scan_market_opportunities",
        },
        "priority_review": {
            "description": "Revisar y re-priorizar tareas pendientes",
            "interval_hours": 6,
            "handler": "review_priorities",
        },
        "risk_assessment": {
            "description": "Evaluar riesgos de proyectos activos",
            "interval_hours": 24,
            "handler": "assess_project_risks",
        },
        "competitive_intel": {
            "description": "Monitorear competencia de proyectos activos",
            "interval_hours": 48,
            "handler": "monitor_competition",
        },
    }
    
    async def analyze_market(self, niche: str, geography: str = "global") -> MarketAnalysis:
        """Analizar mercado para un nicho específico."""
        if not self._sabios:
            raise RuntimeError("Sabios not configured")
        
        prompt = f"""Perform a comprehensive market analysis for:
- Niche: {niche}
- Geography: {geography}

Provide data-driven analysis. Use real numbers where possible.
If exact data unavailable, provide reasonable estimates with confidence levels.

Respond in JSON:
{{
    "market_size_usd": "TAM estimate with source",
    "growth_rate": "CAGR % with timeframe",
    "key_players": [
        {{"name": "...", "market_share": "X%", "strength": "...", "weakness": "..."}}
    ],
    "opportunities": ["opportunity1", "opportunity2", "..."],
    "threats": ["threat1", "threat2", "..."],
    "entry_barriers": ["barrier1", "barrier2", "..."],
    "recommended_positioning": "Specific positioning strategy"
}}"""
        
        response = await self._sabios.ask(prompt)
        data = json.loads(self._extract_json(response))
        
        return MarketAnalysis(**data)
    
    async def create_strategic_plan(self, business_type: str, niche: str,
                                     budget: str = "bootstrap",
                                     timeline: str = "6 months") -> StrategicPlan:
        """Crear plan estratégico completo."""
        prompt = f"""Create a strategic plan for:
- Business type: {business_type}
- Niche: {niche}
- Budget: {budget}
- Timeline: {timeline}

Requirements:
- Phase-based approach (3-5 phases)
- Each phase has clear KPIs and budget
- Include kill criteria (when to pivot/abandon)
- Pessimistic scenario included

Respond in JSON:
{{
    "vision": "One-sentence vision",
    "phases": [
        {{
            "name": "Phase name",
            "duration": "X weeks/months",
            "objectives": ["obj1", "obj2"],
            "kpis": ["kpi1 (target: X)", "kpi2 (target: Y)"],
            "budget": "$X"
        }}
    ],
    "risks": [
        {{
            "risk": "Description",
            "probability": "high/medium/low",
            "impact": "high/medium/low",
            "mitigation": "Strategy"
        }}
    ],
    "success_metrics": ["metric1", "metric2"],
    "kill_criteria": ["If X happens, pivot", "If Y by month Z, abandon"]
}}"""
        
        response = await self._sabios.ask(prompt)
        data = json.loads(self._extract_json(response))
        
        return StrategicPlan(**data)
    
    async def prioritize_tasks(self, tasks: list[dict]) -> list[dict]:
        """Priorizar tareas usando framework ICE (Impact, Confidence, Ease)."""
        prompt = f"""Prioritize these tasks using the ICE framework:
(Impact × Confidence × Ease, each scored 1-10)

Tasks: {json.dumps(tasks, default=str)}

For each task, score and rank. Respond in JSON:
[
    {{
        "task": "...",
        "impact": N,
        "confidence": N,
        "ease": N,
        "ice_score": N,
        "rationale": "Why this priority"
    }}
]

Sort by ICE score descending."""
        
        response = await self._sabios.ask(prompt)
        return json.loads(self._extract_json(response))
    
    async def scan_market_opportunities(self) -> dict:
        """Tarea autónoma: escanear oportunidades."""
        prompt = """Identify 3 emerging market opportunities in digital businesses that are:
1. Underserved (few competitors)
2. Growing (>20% CAGR)
3. Accessible (can be started with <$5000)

For each, provide: niche, market size, why now, entry strategy.
Respond in JSON array."""
        
        response = await self._sabios.ask(prompt)
        return {"opportunities": json.loads(self._extract_json(response))}
    
    async def assess_project_risks(self, project_context: dict = None) -> dict:
        """Tarea autónoma: evaluar riesgos."""
        context = json.dumps(project_context or {"status": "no active projects"})
        prompt = f"""Assess risks for current projects:
Context: {context}

Identify top 5 risks with probability, impact, and mitigation.
Respond in JSON array."""
        
        response = await self._sabios.ask(prompt)
        return {"risks": json.loads(self._extract_json(response))}
    
    @staticmethod
    def _extract_json(text: str) -> str:
        """Extraer JSON de respuesta LLM."""
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        if "```" in text:
            return text.split("```")[1].split("```")[0]
        return text.strip()
```

---

## Épica 59.5 — Emergent Behavior Tracker (Objetivo #8)

### Contexto

El Objetivo #8 dice "Inteligencia Emergente" — que el sistema exhiba comportamientos no programados explícitamente. Los sprints anteriores crearon mecanismos (Causal KB, Monte Carlo, Embriones autónomos) pero nunca se ha medido si realmente hay emergencia. Sprint 59 crea el tracker que detecta y documenta comportamiento emergente real.

### Definición de Emergencia

Un comportamiento es **emergente** si cumple TODAS estas condiciones:
1. **No fue programado explícitamente** — no hay un handler directo para esa acción
2. **Surge de la interacción** entre componentes (no de un componente solo)
3. **Es útil** — produce un resultado positivo no esperado
4. **Es reproducible** — puede ocurrir de nuevo bajo condiciones similares

### Implementación

**Archivo:** `kernel/emergence/tracker.py`

```python
"""
El Monstruo — Emergent Behavior Tracker (Sprint 59)
=====================================================
Sistema que detecta, documenta, y cataloga comportamientos
emergentes del sistema multi-agente.

Definición de emergencia:
1. No programado explícitamente
2. Surge de interacción entre componentes
3. Produce resultado útil
4. Reproducible

Sprint 59 — 2026-05-01
"""
from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
import structlog

logger = structlog.get_logger("monstruo.emergence")


class EmergenceType(str, Enum):
    """Tipos de comportamiento emergente."""
    NOVEL_SOLUTION = "novel_solution"  # Solución no prevista a un problema
    CROSS_DOMAIN = "cross_domain"  # Conexión entre dominios no relacionados
    SELF_OPTIMIZATION = "self_optimization"  # Auto-mejora no programada
    COLLABORATIVE = "collaborative"  # Cooperación emergente entre embriones
    CREATIVE = "creative"  # Output creativo no template-based
    PREDICTIVE = "predictive"  # Predicción acertada sin datos directos


class EmergenceLevel(str, Enum):
    """Nivel de emergencia (qué tan sorprendente es)."""
    LOW = "low"  # Ligeramente inesperado
    MEDIUM = "medium"  # Claramente no programado
    HIGH = "high"  # Genuinamente sorprendente
    BREAKTHROUGH = "breakthrough"  # Cambio de paradigma


@dataclass
class EmergentEvent:
    """Un evento de comportamiento emergente detectado."""
    id: str
    timestamp: str
    type: EmergenceType
    level: EmergenceLevel
    description: str
    components_involved: list[str]  # Qué componentes participaron
    trigger: str  # Qué lo desencadenó
    outcome: str  # Qué resultado produjo
    novelty_score: float  # 0-1, qué tan nuevo es vs. comportamientos previos
    usefulness_score: float  # 0-1, qué tan útil fue
    reproducibility: str  # Condiciones para reproducir
    evidence: dict  # Logs, traces, outputs que lo demuestran


@dataclass
class EmergenceTracker:
    """Tracker de comportamientos emergentes."""
    
    _sabios: Optional[object] = field(default=None, repr=False)
    _supabase: Optional[object] = field(default=None, repr=False)
    _known_behaviors: set = field(default_factory=set)  # Hash of known behaviors
    
    async def evaluate_for_emergence(self, action_log: dict) -> Optional[EmergentEvent]:
        """Evaluar si una acción del sistema exhibe comportamiento emergente."""
        
        # Quick filter: single-component actions are rarely emergent
        components = action_log.get("components_involved", [])
        if len(components) < 2:
            return None
        
        # Check if this behavior pattern is already known
        behavior_hash = self._hash_behavior(action_log)
        if behavior_hash in self._known_behaviors:
            return None
        
        # LLM evaluation for emergence
        if not self._sabios:
            return None
        
        prompt = f"""Evaluate if this system action exhibits emergent behavior.

Action log:
{json.dumps(action_log, default=str, indent=2)[:3000]}

Emergent behavior criteria:
1. NOT explicitly programmed (no direct handler for this exact action)
2. Arises from INTERACTION between multiple components
3. Produces a USEFUL result
4. Is REPRODUCIBLE

Respond in JSON:
{{
    "is_emergent": true/false,
    "confidence": 0.0-1.0,
    "type": "<novel_solution|cross_domain|self_optimization|collaborative|creative|predictive>",
    "level": "<low|medium|high|breakthrough>",
    "description": "What happened and why it's emergent",
    "novelty_score": 0.0-1.0,
    "usefulness_score": 0.0-1.0,
    "reproducibility": "Conditions to reproduce",
    "reasoning": "Why this qualifies (or doesn't) as emergent"
}}

Be STRICT. Most actions are NOT emergent. Only flag genuinely surprising behaviors."""
        
        response = await self._sabios.ask(prompt)
        
        try:
            data = json.loads(self._extract_json(response))
            
            if not data.get("is_emergent") or data.get("confidence", 0) < 0.7:
                return None
            
            event = EmergentEvent(
                id=f"emg_{behavior_hash[:12]}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                type=EmergenceType(data["type"]),
                level=EmergenceLevel(data["level"]),
                description=data["description"],
                components_involved=components,
                trigger=action_log.get("trigger", "unknown"),
                outcome=action_log.get("outcome", "unknown"),
                novelty_score=data["novelty_score"],
                usefulness_score=data["usefulness_score"],
                reproducibility=data["reproducibility"],
                evidence={"action_log": action_log, "reasoning": data["reasoning"]},
            )
            
            # Register as known behavior
            self._known_behaviors.add(behavior_hash)
            
            # Persist to database
            await self._persist_event(event)
            
            logger.info(
                "emergence_detected",
                type=event.type.value,
                level=event.level.value,
                description=event.description[:100],
            )
            
            return event
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning("emergence_eval_failed", error=str(e))
            return None
    
    async def get_emergence_report(self, days: int = 30) -> dict:
        """Generar reporte de comportamientos emergentes."""
        if not self._supabase:
            return {"events": [], "summary": "No database configured"}
        
        # Query recent events
        response = self._supabase.table("emergent_events").select("*").gte(
            "timestamp", 
            (datetime.now(timezone.utc).replace(day=1)).isoformat()
        ).execute()
        
        events = response.data if response.data else []
        
        return {
            "total_events": len(events),
            "by_type": self._count_by_field(events, "type"),
            "by_level": self._count_by_field(events, "level"),
            "avg_novelty": sum(e.get("novelty_score", 0) for e in events) / max(len(events), 1),
            "avg_usefulness": sum(e.get("usefulness_score", 0) for e in events) / max(len(events), 1),
            "top_events": sorted(events, key=lambda e: e.get("novelty_score", 0), reverse=True)[:5],
            "components_most_involved": self._most_common_components(events),
        }
    
    async def _persist_event(self, event: EmergentEvent) -> None:
        """Persistir evento en Supabase."""
        if not self._supabase:
            return
        
        self._supabase.table("emergent_events").insert({
            "id": event.id,
            "timestamp": event.timestamp,
            "type": event.type.value,
            "level": event.level.value,
            "description": event.description,
            "components_involved": event.components_involved,
            "trigger": event.trigger,
            "outcome": event.outcome,
            "novelty_score": event.novelty_score,
            "usefulness_score": event.usefulness_score,
            "reproducibility": event.reproducibility,
            "evidence": event.evidence,
        }).execute()
    
    @staticmethod
    def _hash_behavior(action_log: dict) -> str:
        """Hash a behavior pattern for deduplication."""
        key_parts = [
            str(sorted(action_log.get("components_involved", []))),
            action_log.get("action_type", ""),
            action_log.get("trigger", ""),
        ]
        return hashlib.sha256("|".join(key_parts).encode()).hexdigest()
    
    @staticmethod
    def _count_by_field(events: list, field: str) -> dict:
        counts = {}
        for e in events:
            val = e.get(field, "unknown")
            counts[val] = counts.get(val, 0) + 1
        return counts
    
    @staticmethod
    def _most_common_components(events: list) -> list:
        counts = {}
        for e in events:
            for comp in e.get("components_involved", []):
                counts[comp] = counts.get(comp, 0) + 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    @staticmethod
    def _extract_json(text: str) -> str:
        if "```json" in text:
            return text.split("```json")[1].split("```")[0]
        if "```" in text:
            return text.split("```")[1].split("```")[0]
        return text.strip()
```

### Tabla Supabase

```sql
-- Sprint 59: Emergent behavior tracking
CREATE TABLE IF NOT EXISTS emergent_events (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    type TEXT NOT NULL,  -- novel_solution, cross_domain, etc.
    level TEXT NOT NULL,  -- low, medium, high, breakthrough
    description TEXT NOT NULL,
    components_involved TEXT[] NOT NULL,
    trigger TEXT,
    outcome TEXT,
    novelty_score FLOAT NOT NULL DEFAULT 0.0,
    usefulness_score FLOAT NOT NULL DEFAULT 0.0,
    reproducibility TEXT,
    evidence JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_emergent_events_type ON emergent_events(type);
CREATE INDEX idx_emergent_events_level ON emergent_events(level);
CREATE INDEX idx_emergent_events_timestamp ON emergent_events(timestamp DESC);
```

---

## Integración entre Épicas

Las 5 épicas se conectan así:

```
Usuario (cualquier idioma)
    ↓
[59.1] i18n Engine detecta idioma
    ↓
[59.2] Conversational UX parsea intent
    ↓
Orchestrator decide qué Embriones invocar
    ↓
[59.3] Embrión-Creativo (si necesita diseño)
[59.4] Embrión-Estratega (si necesita planning)
    ↓
[59.5] Emergence Tracker evalúa si hubo comportamiento emergente
    ↓
Respuesta al usuario (en su idioma)
```

---

## Archivos a Crear/Modificar

| Archivo | Acción | Épica |
|---|---|---|
| `kernel/i18n/__init__.py` | Crear | 59.1 |
| `kernel/i18n/engine.py` | Crear | 59.1 |
| `kernel/ux/__init__.py` | Crear | 59.2 |
| `kernel/ux/conversational.py` | Crear | 59.2 |
| `kernel/embriones/embrion_creativo.py` | Crear | 59.3 |
| `kernel/embriones/embrion_estratega.py` | Crear | 59.4 |
| `kernel/emergence/__init__.py` | Crear | 59.5 |
| `kernel/emergence/tracker.py` | Crear | 59.5 |
| `kernel/main.py` | Modificar (agregar /chat endpoint) | 59.2 |
| `requirements.txt` | Agregar deepl, babel | 59.1 |
| `supabase/migrations/` | Crear tablas | 59.1, 59.5 |

---

## Criterios de Aceptación

| Épica | Criterio | Verificación |
|---|---|---|
| 59.1 | Detectar idioma de input con >90% accuracy | Test con 50 frases en 10 idiomas |
| 59.1 | Traducir contenido ES↔EN con calidad profesional | BLEU score >0.7 en back-translation |
| 59.2 | Parsear intent con >80% accuracy | Test con 30 requests naturales |
| 59.2 | Responder en <3s para intents simples | Benchmark de latencia |
| 59.3 | Generar brand identity coherente | Review manual de 5 identidades |
| 59.3 | Design review score correlaciona con calidad real | Calibración contra 10 diseños conocidos |
| 59.4 | Market analysis produce datos verificables | Cross-check con 3 fuentes |
| 59.4 | Strategic plan tiene kill criteria realistas | Review por Sabios |
| 59.5 | Tracker NO flag comportamientos normales como emergentes | <5% false positive rate |
| 59.5 | Tracker SÍ detecta emergencia simulada | Test con escenarios artificiales |

---

## Estimación de Costos

| Componente | Costo Mensual |
|---|---|
| DeepL API Free | $0 (500K chars/mes) |
| DeepL API Pro (overflow) | $0-6/mes |
| LLM calls adicionales (Embriones) | ~$3-8/mes |
| Emergence evaluation calls | ~$1-3/mes |
| **Total Sprint 59** | **$4-17/mes adicionales** |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| DeepL free tier insuficiente | Media | Bajo | LLM fallback soberano |
| Intent parsing inaccurate | Media | Alto | Confidence threshold + clarification |
| Emergence tracker demasiado permisivo | Alta | Medio | Threshold estricto (0.7) + human review |
| Embriones gastan demasiado budget | Baja | Medio | Daily caps ya implementados |
| i18n RTL (Arabic) rompe layouts | Media | Bajo | CSS `dir="rtl"` en templates |

---

## Referencias

[1]: https://pypi.org/project/deepl/ "DeepL Python SDK 1.30.0"
[2]: https://dev.to/erayg/best-i18n-libraries-for-nextjs-react-react-native-in-2026-honest-comparison-3m8f "Best i18n Libraries for React 2026"
[3]: https://www.reddit.com/r/reactjs/comments/1s01nfj/ "React i18n modern approach (2026)"
[4]: https://better-i18n.com/en/blog/python-i18n-guide/ "Python i18n: From gettext to Modern Workflows"
[5]: https://www.langchain.com/ "LangChain Agent Framework"
