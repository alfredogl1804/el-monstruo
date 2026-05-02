"""
Tests del Sprint 59 — El Monstruo Habla al Mundo
=================================================
Brand Compliance Checklist Check #6: Tests obligatorios.

Cubre:
  - 59.1: I18nEngine
  - 59.2: ConversationalUX
  - 59.3: EmbrionCreativo
  - 59.4: EmbrionEstratega
  - 59.5: EmergentBehaviorTracker
"""

import asyncio
import json

import pytest

# ── 59.1: I18nEngine ──────────────────────────────────────────────────────────


def test_i18n_engine_importable():
    """I18nEngine debe ser importable sin errores."""
    from kernel.i18n.engine import I18nEngine, SupportedLocale

    assert I18nEngine is not None
    assert SupportedLocale is not None


def test_i18n_supported_locales():
    """SupportedLocale debe incluir los idiomas principales."""
    from kernel.i18n.engine import SupportedLocale

    locales = [e.value for e in SupportedLocale]
    assert "es" in locales
    assert "en" in locales
    assert "pt" in locales


def test_i18n_engine_to_dict():
    """I18nEngine.to_dict() debe retornar dict serializable para Command Center."""
    from kernel.i18n.engine import I18nEngine

    engine = I18nEngine()
    result = engine.to_dict()
    assert isinstance(result, dict)
    assert "componente" in result
    assert "locales_soportados" in result
    assert result["componente"] == "i18n_engine"


def test_i18n_translate_sync():
    """I18nEngine debe traducir texto básico de forma síncrona."""
    from kernel.i18n.engine import I18nEngine

    engine = I18nEngine()
    result = asyncio.new_event_loop().run_until_complete(engine.translate("Hello", target_locale="es"))
    # Sin Sabios, debe retornar el texto original con nota de fallback
    assert isinstance(result, str)
    assert len(result) > 0


def test_i18n_detect_language_heuristic():
    """I18nEngine debe detectar idioma por heurísticas sin LLM."""
    from kernel.i18n.engine import I18nEngine

    engine = I18nEngine()
    locale = asyncio.new_event_loop().run_until_complete(engine.detect_language("Hello world, this is English text"))
    assert isinstance(locale, str)
    assert len(locale) == 2  # código ISO 639-1


# ── 59.2: ConversationalUX ────────────────────────────────────────────────────


def test_conversational_ux_importable():
    """ConversationalUX debe ser importable sin errores."""
    from kernel.ux.conversational import ConversationalUX, IntentType

    assert ConversationalUX is not None
    assert IntentType is not None


def test_conversational_ux_quick_commands():
    """Quick commands deben ser detectados sin LLM."""
    from kernel.ux.conversational import IntentType, check_quick_command

    assert check_quick_command("/nuevo") == IntentType.CREATE_BUSINESS
    assert check_quick_command("/status") == IntentType.CHECK_STATUS
    assert check_quick_command("/help") == IntentType.HELP
    assert check_quick_command("texto normal") is None


def test_conversational_ux_parse_quick_command():
    """parse_intent debe detectar quick commands con confidence 1.0."""
    from kernel.ux.conversational import ConversationalUX, IntentType

    ux = ConversationalUX()
    result = asyncio.new_event_loop().run_until_complete(ux.parse_intent("/nuevo"))
    assert result.type == IntentType.CREATE_BUSINESS
    assert result.confidence == 1.0


def test_conversational_ux_heuristic_fallback():
    """Sin Sabios, debe usar heurísticas con confidence baja."""
    from kernel.ux.conversational import ConversationalUX, IntentType

    ux = ConversationalUX()
    result = asyncio.new_event_loop().run_until_complete(ux.parse_intent("quiero crear una tienda online"))
    assert result.type == IntentType.CREATE_BUSINESS
    assert result.confidence < 0.7  # heurística, no LLM


def test_conversational_ux_empty_input():
    """Input vacío debe retornar UNKNOWN con clarification."""
    from kernel.ux.conversational import ConversationalUX, IntentType

    ux = ConversationalUX()
    result = asyncio.new_event_loop().run_until_complete(ux.parse_intent(""))
    assert result.type == IntentType.UNKNOWN
    assert result.clarification_needed is not None


def test_conversational_ux_to_dict():
    """to_dict() debe retornar estado serializable para Command Center."""
    from kernel.ux.conversational import ConversationalUX

    ux = ConversationalUX()
    result = ux.to_dict()
    assert isinstance(result, dict)
    assert "componente" in result
    assert "quick_commands_disponibles" in result
    assert result["componente"] == "conversational_ux"


def test_conversational_ux_suggest_next_actions():
    """suggest_next_actions debe retornar lista no vacía."""
    from kernel.ux.conversational import ConversationalUX, IntentType, ParsedIntent

    ux = ConversationalUX()
    intent = ParsedIntent(
        type=IntentType.CREATE_BUSINESS,
        confidence=0.9,
        original_text="/nuevo",
    )
    result = asyncio.new_event_loop().run_until_complete(ux.suggest_next_actions(intent))
    assert isinstance(result, list)
    assert len(result) > 0


# ── 59.3: EmbrionCreativo ─────────────────────────────────────────────────────


def test_embrion_creativo_importable():
    """EmbrionCreativo debe ser importable sin errores."""
    from kernel.embriones.embrion_creativo import BrandIdentity, EmbrionCreativo

    assert EmbrionCreativo is not None
    assert BrandIdentity is not None


def test_embrion_creativo_sin_sabios_raises():
    """generate_brand_identity sin Sabios debe lanzar error con identidad."""
    from kernel.embriones.embrion_creativo import EMBRION_CREATIVO_SIN_SABIOS, EmbrionCreativo

    creativo = EmbrionCreativo()
    with pytest.raises(EMBRION_CREATIVO_SIN_SABIOS):
        asyncio.new_event_loop().run_until_complete(creativo.generate_brand_identity("ropa", "jóvenes"))


def test_embrion_creativo_to_dict():
    """to_dict() debe retornar estado serializable para Command Center."""
    from kernel.embriones.embrion_creativo import EmbrionCreativo

    creativo = EmbrionCreativo()
    result = creativo.to_dict()
    assert isinstance(result, dict)
    assert result["embrion_id"] == "embrion-creativo"
    assert "tasks_autonomas" in result
    assert "trend_scan" in result["tasks_autonomas"]


def test_embrion_creativo_default_tasks():
    """EmbrionCreativo debe tener exactamente 4 tareas autónomas."""
    from kernel.embriones.embrion_creativo import EmbrionCreativo

    creativo = EmbrionCreativo()
    assert len(creativo.DEFAULT_TASKS) == 4
    assert "brand_generation" in creativo.DEFAULT_TASKS
    assert "design_review" in creativo.DEFAULT_TASKS
    assert "trend_scan" in creativo.DEFAULT_TASKS
    assert "palette_generator" in creativo.DEFAULT_TASKS


def test_embrion_creativo_json_invalido_raises():
    """_parse_json_response con JSON inválido debe lanzar error con identidad."""
    from kernel.embriones.embrion_creativo import EMBRION_CREATIVO_JSON_INVALIDO, EmbrionCreativo

    creativo = EmbrionCreativo()
    with pytest.raises(EMBRION_CREATIVO_JSON_INVALIDO):
        creativo._parse_json_response("esto no es json {{{")


# ── 59.4: EmbrionEstratega ────────────────────────────────────────────────────


def test_embrion_estratega_importable():
    """EmbrionEstratega debe ser importable sin errores."""
    from kernel.embriones.embrion_estratega import EmbrionEstratega, MarketAnalysis, StrategicPlan

    assert EmbrionEstratega is not None
    assert MarketAnalysis is not None
    assert StrategicPlan is not None


def test_embrion_estratega_sin_sabios_raises():
    """analyze_market sin Sabios debe lanzar error con identidad."""
    from kernel.embriones.embrion_estratega import EMBRION_ESTRATEGA_SIN_SABIOS, EmbrionEstratega

    estratega = EmbrionEstratega()
    with pytest.raises(EMBRION_ESTRATEGA_SIN_SABIOS):
        asyncio.new_event_loop().run_until_complete(estratega.analyze_market("SaaS para restaurantes"))


def test_embrion_estratega_to_dict():
    """to_dict() debe retornar estado serializable para Command Center."""
    from kernel.embriones.embrion_estratega import EmbrionEstratega

    estratega = EmbrionEstratega()
    result = estratega.to_dict()
    assert isinstance(result, dict)
    assert result["embrion_id"] == "embrion-estratega"
    assert "tasks_autonomas" in result
    assert "market_scan" in result["tasks_autonomas"]


def test_embrion_estratega_default_tasks():
    """EmbrionEstratega debe tener exactamente 4 tareas autónomas."""
    from kernel.embriones.embrion_estratega import EmbrionEstratega

    estratega = EmbrionEstratega()
    assert len(estratega.DEFAULT_TASKS) == 4
    assert "market_scan" in estratega.DEFAULT_TASKS
    assert "priority_review" in estratega.DEFAULT_TASKS
    assert "risk_assessment" in estratega.DEFAULT_TASKS
    assert "competitive_intel" in estratega.DEFAULT_TASKS


def test_embrion_estratega_json_invalido_raises():
    """_parse_json_response con JSON inválido debe lanzar error con identidad."""
    from kernel.embriones.embrion_estratega import EMBRION_ESTRATEGA_JSON_INVALIDO, EmbrionEstratega

    estratega = EmbrionEstratega()
    with pytest.raises(EMBRION_ESTRATEGA_JSON_INVALIDO):
        estratega._parse_json_response("no es json")


# ── 59.5: EmergentBehaviorTracker ─────────────────────────────────────────────


def test_emergent_tracker_importable():
    """EmergentBehaviorTracker debe ser importable sin errores."""
    from kernel.emergent_tracker import BehaviorSignificance, BehaviorType, EmergentBehaviorTracker

    assert EmergentBehaviorTracker is not None
    assert BehaviorType is not None
    assert BehaviorSignificance is not None


def test_emergent_tracker_register_in_memory():
    """register() debe funcionar en modo in-memory sin Supabase."""
    from kernel.emergent_tracker import BehaviorSignificance, BehaviorType, EmergentBehaviorTracker

    tracker = EmergentBehaviorTracker()
    behavior = asyncio.new_event_loop().run_until_complete(
        tracker.register(
            embrion_id="embrion-creativo",
            behavior_type=BehaviorType.SOLUCION_CREATIVA,
            description="Generó una paleta de colores no programada explícitamente",
            significance=BehaviorSignificance.MEDIA,
        )
    )
    assert behavior.id is not None
    assert behavior.embrion_id == "embrion-creativo"
    assert tracker._total_registered == 1


def test_emergent_tracker_campos_requeridos():
    """register() sin campos requeridos debe lanzar error con identidad."""
    from kernel.emergent_tracker import (
        EMERGENT_TRACKER_COMPORTAMIENTO_INVALIDO,
        BehaviorType,
        EmergentBehaviorTracker,
    )

    tracker = EmergentBehaviorTracker()
    with pytest.raises(EMERGENT_TRACKER_COMPORTAMIENTO_INVALIDO):
        asyncio.new_event_loop().run_until_complete(
            tracker.register(
                embrion_id="",  # vacío — debe fallar
                behavior_type=BehaviorType.SOLUCION_CREATIVA,
                description="",  # vacío — debe fallar
            )
        )


def test_emergent_tracker_get_recent_in_memory():
    """get_recent_behaviors() debe retornar comportamientos in-memory."""
    from kernel.emergent_tracker import BehaviorSignificance, BehaviorType, EmergentBehaviorTracker

    tracker = EmergentBehaviorTracker()
    asyncio.new_event_loop().run_until_complete(
        tracker.register(
            embrion_id="embrion-tecnico",
            behavior_type=BehaviorType.OPTIMIZACION_AUTONOMA,
            description="Optimizó el pipeline de forma autónoma",
            significance=BehaviorSignificance.ALTA,
        )
    )
    recent = asyncio.new_event_loop().run_until_complete(tracker.get_recent_behaviors(limit=10))
    assert isinstance(recent, list)
    assert len(recent) >= 1


def test_emergent_tracker_analyze_patterns_empty():
    """analyze_patterns() con 0 comportamientos debe retornar recomendación."""
    from kernel.emergent_tracker import EmergentBehaviorTracker

    tracker = EmergentBehaviorTracker()
    result = asyncio.new_event_loop().run_until_complete(tracker.analyze_patterns())
    assert result["total_analyzed"] == 0
    assert len(result["recommendations"]) > 0


def test_emergent_tracker_to_dict():
    """to_dict() debe retornar estado serializable para Command Center."""
    from kernel.emergent_tracker import EmergentBehaviorTracker

    tracker = EmergentBehaviorTracker()
    result = tracker.to_dict()
    assert isinstance(result, dict)
    assert result["componente"] == "emergent_behavior_tracker"
    assert "behavior_types" in result
    assert "metricas" in result


def test_emergent_tracker_behavior_to_dict():
    """EmergentBehavior.to_dict() debe ser JSON serializable."""
    from kernel.emergent_tracker import BehaviorSignificance, BehaviorType, EmergentBehaviorTracker

    tracker = EmergentBehaviorTracker()
    behavior = asyncio.new_event_loop().run_until_complete(
        tracker.register(
            embrion_id="embrion-vigia",
            behavior_type=BehaviorType.COLABORACION_ESPONTANEA,
            description="Colaboró con EmbrionCreativo sin instrucción explícita",
            significance=BehaviorSignificance.ALTA,
            reproducible=True,
            metadata={"collaborator": "embrion-creativo"},
        )
    )
    data = behavior.to_dict()
    # Debe ser JSON serializable
    json_str = json.dumps(data)
    assert len(json_str) > 0
    assert data["reproducible"] is True
    assert data["metadata"]["collaborator"] == "embrion-creativo"


def test_emergent_tracker_singleton_not_initialized():
    """get_emergent_tracker() sin inicializar debe lanzar RuntimeError."""
    import kernel.emergent_tracker as et_module

    # Reset singleton para test
    original = et_module._emergent_tracker
    et_module._emergent_tracker = None
    with pytest.raises(RuntimeError):
        et_module.get_emergent_tracker()
    # Restaurar
    et_module._emergent_tracker = original
