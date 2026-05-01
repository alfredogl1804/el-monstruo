"""
El Monstruo — i18n Engine (Sprint 59.1)
========================================
Motor de internacionalización de dos niveles:

Nivel 1 — Interno: El Monstruo opera en el idioma del usuario.
  - Detección automática de idioma del input
  - System prompts multilingües para los Sabios
  - Logs y alerts en el idioma del usuario

Nivel 2 — Proyectos: Los proyectos generados nacen multilingües.
  - Templates de i18n inyectables en proyectos React/Next.js
  - Traducción automática de contenido generado
  - Locale-aware formatting (fechas, monedas, números)

Objetivo: #13 — Del Mundo (primer módulo que lo implementa)
Sprint: 59 — "El Monstruo Habla al Mundo"
Fecha: 2026-05-01

Soberanía:
  - DeepL (primario, alta calidad para idiomas europeos)
  - LLM Translation via Sabios (fallback soberano, cero dependencia externa)
  - Heurísticas de charset (detección sin LLM para CJK/árabe)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import structlog

logger = structlog.get_logger("monstruo.i18n.engine")


# ── Errores con identidad ──────────────────────────────────────────────────────

class I18N_ENGINE_SIN_BACKEND(RuntimeError):
    """No hay backend de traducción disponible (DeepL ni Sabios configurados).
    
    Sugerencia: Configura DEEPL_API_KEY o inyecta _sabios al inicializar I18nEngine.
    """


class I18N_ENGINE_LOCALE_NO_SOPORTADO(ValueError):
    """El locale solicitado no está en la lista de locales soportados.
    
    Sugerencia: Usa uno de los valores de SupportedLocale (es, en, pt, fr, de, it, ja, zh, ko, ar).
    """


# ── Enums y configuración ──────────────────────────────────────────────────────

class SupportedLocale(str, Enum):
    """Locales soportados por El Monstruo."""
    ES = "es"   # Español (default)
    EN = "en"   # English
    PT = "pt"   # Português
    FR = "fr"   # Français
    DE = "de"   # Deutsch
    IT = "it"   # Italiano
    JA = "ja"   # 日本語
    ZH = "zh"   # 中文
    KO = "ko"   # 한국어
    AR = "ar"   # العربية


@dataclass
class LocaleConfig:
    """Configuración de formato para un locale específico.
    
    Args:
        code: Código ISO 639-1 del locale.
        name: Nombre legible del idioma.
        direction: Dirección del texto ('ltr' o 'rtl').
        date_format: Formato de fecha preferido.
        currency: Código ISO 4217 de la moneda principal.
        number_separator: Separador de miles.
        decimal_separator: Separador decimal.
    """
    code: str
    name: str
    direction: str = "ltr"
    date_format: str = "YYYY-MM-DD"
    currency: str = "USD"
    number_separator: str = ","
    decimal_separator: str = "."


LOCALE_CONFIGS: dict[str, LocaleConfig] = {
    "es": LocaleConfig("es", "Español", currency="MXN"),
    "en": LocaleConfig("en", "English", currency="USD"),
    "pt": LocaleConfig("pt", "Português", currency="BRL", number_separator=".", decimal_separator=","),
    "fr": LocaleConfig("fr", "Français", currency="EUR", number_separator=" ", decimal_separator=","),
    "de": LocaleConfig("de", "Deutsch", currency="EUR", number_separator=".", decimal_separator=","),
    "it": LocaleConfig("it", "Italiano", currency="EUR", number_separator=".", decimal_separator=","),
    "ja": LocaleConfig("ja", "日本語", currency="JPY"),
    "zh": LocaleConfig("zh", "中文", currency="CNY"),
    "ko": LocaleConfig("ko", "한국어", currency="KRW"),
    "ar": LocaleConfig("ar", "العربية", direction="rtl", currency="SAR"),
}

# System prompts localizados para los Sabios
SYSTEM_PROMPT_TEMPLATES: dict[str, str] = {
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


# ── Motor principal ────────────────────────────────────────────────────────────

@dataclass
class I18nEngine:
    """Motor de internacionalización de El Monstruo.
    
    Detecta idioma, traduce texto y genera templates i18n para proyectos.
    Soporta 10 locales con fallback soberano via LLM.
    
    Args:
        default_locale: Locale por defecto cuando no se puede detectar (default: 'es').
        _translator: Cliente DeepL opcional (soberanía: LLM fallback).
        _sabios: Cliente de Sabios para traducción LLM y detección de idioma.
    
    Soberanía:
        - DeepL → LLM Translation (si DeepL no está disponible)
        - LLM Detection → heurísticas charset (si Sabios no está disponible)
    """
    default_locale: str = "es"
    _translator: Optional[object] = field(default=None, repr=False)
    _sabios: Optional[object] = field(default=None, repr=False)

    async def detect_language(self, text: str) -> str:
        """Detectar idioma del texto usando heurísticas de charset + LLM fallback.
        
        Args:
            text: Texto a analizar.
        
        Returns:
            Código ISO 639-1 del idioma detectado (ej: 'es', 'en', 'ja').
        """
        if not text or not text.strip():
            return self.default_locale

        # Heurística rápida: detección por charset (sin LLM, sin costo)
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            return "zh"
        if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text):
            return "ja"
        if any('\uac00' <= c <= '\ud7af' for c in text):
            return "ko"
        if any('\u0600' <= c <= '\u06ff' for c in text):
            return "ar"

        # LLM para scripts latinos (requiere Sabios)
        if self._sabios:
            try:
                prompt = (
                    f"Detect the language of this text. "
                    f"Reply with ONLY the ISO 639-1 code (es, en, pt, fr, de, it): "
                    f"'{text[:200]}'"
                )
                response = await self._sabios.ask_fastest(prompt)
                code = response.strip().lower()[:2]
                if code in [e.value for e in SupportedLocale]:
                    logger.info("idioma_detectado_llm", locale=code, chars=len(text))
                    return code
            except Exception as _e:
                logger.warning("deteccion_idioma_llm_fallo", error=str(_e))

        return self.default_locale

    async def translate(
        self,
        text: str,
        target_locale: str,
        source_locale: Optional[str] = None,
    ) -> str:
        """Traducir texto al locale objetivo.
        
        Args:
            text: Texto a traducir.
            target_locale: Locale destino (ej: 'en', 'ja').
            source_locale: Locale origen opcional (mejora calidad en DeepL).
        
        Returns:
            Texto traducido. Si no hay backend disponible, retorna el original.
        
        Raises:
            I18N_ENGINE_LOCALE_NO_SOPORTADO: Si target_locale no está en SupportedLocale.
        
        Soberanía:
            1. DeepL (alta calidad, idiomas europeos)
            2. LLM via Sabios (fallback soberano, todos los idiomas)
            3. Texto original (si ningún backend disponible, no crashea)
        """
        supported = [e.value for e in SupportedLocale]
        if target_locale not in supported:
            raise I18N_ENGINE_LOCALE_NO_SOPORTADO(
                f"Locale '{target_locale}' no soportado. "
                f"Usa uno de: {supported}"
            )

        if source_locale == target_locale:
            return text

        # Estrategia 1: DeepL (idiomas europeos, alta calidad)
        deepl_locales = ("en", "es", "pt", "fr", "de", "it")
        if self._translator and target_locale in deepl_locales:
            try:
                import deepl  # soberanía: si falla, cae al LLM
                result = self._translator.translate_text(
                    text,
                    target_lang=target_locale.upper(),
                    source_lang=source_locale.upper() if source_locale else None,
                )
                logger.info("traduccion_deepl", target=target_locale, chars=len(text))
                return result.text
            except Exception as _e:
                logger.warning("deepl_fallo_usando_llm", error=str(_e))

        # Estrategia 2: LLM Translation (fallback soberano)
        if self._sabios:
            try:
                locale_name = LOCALE_CONFIGS.get(
                    target_locale, LocaleConfig(target_locale, target_locale)
                ).name
                prompt = (
                    f"Translate the following text to {locale_name}. "
                    f"Maintain the tone, formatting, and technical terms. "
                    f"Reply with ONLY the translation:\n\n{text}"
                )
                translated = await self._sabios.ask(prompt)
                logger.info("traduccion_llm", target=target_locale, chars=len(text))
                return translated
            except Exception as _e:
                logger.warning("traduccion_llm_fallo", error=str(_e))

        # Estrategia 3: Retornar original (no crashea el sistema)
        logger.error(
            "sin_backend_traduccion",
            target=target_locale,
            sugerencia="Configura DEEPL_API_KEY o inyecta _sabios",
        )
        return text

    async def translate_batch(self, texts: list[str], target_locale: str) -> list[str]:
        """Traducir múltiples textos en batch (optimizado para DeepL).
        
        Args:
            texts: Lista de textos a traducir.
            target_locale: Locale destino.
        
        Returns:
            Lista de textos traducidos en el mismo orden.
        """
        deepl_locales = ("en", "es", "pt", "fr", "de", "it")
        if self._translator and target_locale in deepl_locales:
            try:
                import deepl
                results = self._translator.translate_text(
                    texts,
                    target_lang=target_locale.upper(),
                )
                return [r.text for r in results]
            except Exception as _e:
                logger.warning("batch_deepl_fallo", error=str(_e))

        # Fallback: traducir uno por uno
        return [await self.translate(t, target_locale) for t in texts]

    def get_locale_config(self, locale: str) -> LocaleConfig:
        """Obtener configuración de formato para un locale.
        
        Args:
            locale: Código ISO 639-1 del locale.
        
        Returns:
            LocaleConfig con formatos de fecha, moneda y números.
        """
        return LOCALE_CONFIGS.get(locale, LOCALE_CONFIGS["en"])

    def format_currency(self, amount: float, locale: str) -> str:
        """Formatear moneda según las convenciones del locale.
        
        Args:
            amount: Cantidad numérica a formatear.
            locale: Locale para determinar símbolo y separadores.
        
        Returns:
            String formateado (ej: 'MXN 1,234.56', 'EUR 1.234,56').
        """
        config = self.get_locale_config(locale)
        if config.currency in ("JPY", "KRW"):
            # Sin decimales para monedas sin centavos
            return f"{config.currency} {int(amount):,}".replace(",", config.number_separator)
        formatted = (
            f"{amount:,.2f}"
            .replace(",", "TEMP")
            .replace(".", config.decimal_separator)
            .replace("TEMP", config.number_separator)
        )
        return f"{config.currency} {formatted}"

    def generate_i18n_template(self, framework: str = "react") -> dict[str, str]:
        """Generar template de i18n inyectable en proyectos generados.
        
        Args:
            framework: Framework objetivo ('react' o 'nextjs').
        
        Returns:
            Dict con rutas de archivo como keys y contenido como values.
            Listo para escribir directamente en el filesystem del proyecto.
        """
        if framework == "react":
            return self._react_i18n_template()
        elif framework == "nextjs":
            return self._nextjs_i18n_template()
        logger.warning("framework_i18n_no_soportado", framework=framework)
        return {}

    def _react_i18n_template(self) -> dict[str, str]:
        """Template react-i18next para proyectos React.
        
        Soberanía: react-i18next → i18next-vanilla si React no está disponible.
        """
        return {
            "src/i18n/index.ts": (
                "import i18n from 'i18next';\n"
                "import { initReactI18next } from 'react-i18next';\n"
                "import LanguageDetector from 'i18next-browser-languagedetector';\n\n"
                "import en from './locales/en.json';\n"
                "import es from './locales/es.json';\n\n"
                "i18n\n"
                "  .use(LanguageDetector)\n"
                "  .use(initReactI18next)\n"
                "  .init({\n"
                "    resources: { en: { translation: en }, es: { translation: es } },\n"
                "    fallbackLng: 'es',\n"
                "    interpolation: { escapeValue: false },\n"
                "  });\n\n"
                "export default i18n;\n"
            ),
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
                "nav": {"home": "Inicio", "about": "Acerca de", "contact": "Contacto"},
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
                "nav": {"home": "Home", "about": "About", "contact": "Contact"},
            }, indent=2, ensure_ascii=False),
            "package_deps": json.dumps({
                "i18next": "^24.0.0",
                "react-i18next": "^15.0.0",
                "i18next-browser-languagedetector": "^8.0.0",
            }),
        }

    def _nextjs_i18n_template(self) -> dict[str, str]:
        """Template next-intl para proyectos Next.js.
        
        Soberanía: next-intl → react-i18next si Next.js no está disponible.
        """
        return {
            "src/i18n/request.ts": (
                "import { getRequestConfig } from 'next-intl/server';\n\n"
                "export default getRequestConfig(async ({ locale }) => ({\n"
                "  messages: (await import(`./messages/${locale}.json`)).default,\n"
                "}));\n"
            ),
            "package_deps": json.dumps({"next-intl": "^4.0.0"}),
        }

    def to_dict(self) -> dict:
        """Estado del motor para consumo del Command Center.
        
        Returns:
            Dict serializable con estado actual del motor i18n.
        """
        return {
            "componente": "i18n_engine",
            "version": "1.0.0-sprint59",
            "objetivo": "#13 Del Mundo",
            "default_locale": self.default_locale,
            "locales_soportados": [e.value for e in SupportedLocale],
            "total_locales": len(SupportedLocale),
            "backends_activos": {
                "deepl": self._translator is not None,
                "llm_sabios": self._sabios is not None,
                "heuristicas_charset": True,  # siempre activo
            },
            "frameworks_soportados": ["react", "nextjs"],
        }


# ── Helpers de módulo ──────────────────────────────────────────────────────────

def get_localized_system_prompt(locale: str, base_prompt: str = "") -> str:
    """Obtener system prompt localizado para los Sabios.
    
    Args:
        locale: Código ISO 639-1 del idioma objetivo.
        base_prompt: Prompt base al que se agrega la instrucción de idioma.
    
    Returns:
        System prompt con instrucción de idioma al final.
    """
    locale_instruction = SYSTEM_PROMPT_TEMPLATES.get(
        locale, SYSTEM_PROMPT_TEMPLATES["es"]
    )
    return f"{base_prompt}\n\n{locale_instruction}" if base_prompt else locale_instruction


_i18n_engine_singleton: Optional[I18nEngine] = None


def get_i18n_engine() -> I18nEngine:
    """Obtener singleton del I18nEngine.
    
    Returns:
        Instancia global del motor i18n.
    """
    global _i18n_engine_singleton
    if _i18n_engine_singleton is None:
        _i18n_engine_singleton = I18nEngine()
        logger.info("i18n_engine_inicializado", default_locale="es")
    return _i18n_engine_singleton


def init_i18n_engine(
    default_locale: str = "es",
    deepl_api_key: Optional[str] = None,
    sabios: Optional[object] = None,
) -> I18nEngine:
    """Inicializar I18nEngine con backends opcionales.
    
    Args:
        default_locale: Locale por defecto.
        deepl_api_key: API key de DeepL (soberanía: opcional).
        sabios: Cliente de Sabios para LLM translation.
    
    Returns:
        Instancia configurada del motor i18n.
    
    Soberanía:
        deepl → LLM Sabios → heurísticas charset
    """
    global _i18n_engine_singleton

    translator = None
    if deepl_api_key or os.environ.get("DEEPL_API_KEY"):
        try:
            import deepl  # soberanía: opcional, LLM fallback disponible
            translator = deepl.Translator(deepl_api_key or os.environ["DEEPL_API_KEY"])
            logger.info("deepl_configurado")
        except ImportError:
            logger.warning(
                "deepl_no_instalado",
                sugerencia="pip install deepl>=1.30.0 o usa LLM translation",
            )

    _i18n_engine_singleton = I18nEngine(
        default_locale=default_locale,
        _translator=translator,
        _sabios=sabios,
    )
    logger.info(
        "i18n_engine_listo",
        default_locale=default_locale,
        deepl=translator is not None,
        sabios=sabios is not None,
    )
    return _i18n_engine_singleton
