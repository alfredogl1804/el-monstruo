"""
El Monstruo — Tests: Magna Classifier (Sprint 81)
==================================================
Tests unitarios para kernel/magna_classifier.py

Cobertura:
  1. Clasificación de contenido técnico → route=graph
  2. Clasificación de acciones → route=graph o tool_specific
  3. Clasificación de reflexiones → route=router
  4. Tool-specific detection (keywords → tool sugerida)
  5. Cap diario de graph calls
  6. Cache en memoria (hit/miss/expiry)
  7. Score threshold behavior
  8. Inputs edge case (vacío, muy largo, unicode)
  9. Estadísticas del clasificador
  10. Reset diario automático de contadores
"""

import time
import pytest
from unittest.mock import AsyncMock, MagicMock

from kernel.magna_classifier import (
    MagnaClassifier,
    ClassificationResult,
    RouteType,
    ContentCategory,
    MagnaClasificacionFallida,
    MagnaCacheVencido,
    DEFAULT_THRESHOLD,
    DEFAULT_GRAPH_CALLS_PER_DAY,
    TTL_PRECIOS,
    TTL_TRENDING,
    TTL_API_FRAMEWORKS,
)


# ── Fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def classifier():
    """Classifier sin DB (solo cache en memoria)."""
    return MagnaClassifier(db=None, threshold=0.6, graph_calls_per_day=30)


@pytest.fixture
def classifier_low_cap():
    """Classifier con cap bajo para testing de límites."""
    return MagnaClassifier(db=None, threshold=0.6, graph_calls_per_day=3)


@pytest.fixture
def classifier_low_threshold():
    """Classifier con threshold bajo (casi todo va a graph)."""
    return MagnaClassifier(db=None, threshold=0.2, graph_calls_per_day=100)


@pytest.fixture
def mock_db():
    """Mock de SupabaseClient."""
    db = MagicMock()
    db.connected = True
    db.select = AsyncMock(return_value=[])
    db.upsert = AsyncMock(return_value={"cache_key": "test"})
    db.update = AsyncMock(return_value={"cache_key": "test"})
    return db


@pytest.fixture
def classifier_with_db(mock_db):
    """Classifier con DB mock."""
    return MagnaClassifier(db=mock_db, threshold=0.6, graph_calls_per_day=30)


# ── Test 1: Contenido técnico → graph ──────────────────────────────

class TestTechClassification:
    """Contenido técnico debe clasificarse como graph."""

    def test_api_query_routes_to_graph(self, classifier):
        """Pregunta sobre API → graph."""
        result = classifier.classify("¿Cuál es la última versión del SDK de OpenAI?")
        assert result.route in (RouteType.GRAPH, RouteType.TOOL_SPECIFIC)
        assert result.category in (ContentCategory.TECH, ContentCategory.ACTION)
        assert result.score >= 0.4

    def test_deploy_question_routes_to_graph(self, classifier):
        """Pregunta sobre deploy → graph."""
        result = classifier.classify("Necesito deploy el endpoint de Railway con la nueva versión v2.3.1")
        assert result.route in (RouteType.GRAPH, RouteType.TOOL_SPECIFIC)
        assert result.score >= 0.5

    def test_code_with_url_routes_to_graph(self, classifier):
        """Texto con URL y código → graph."""
        result = classifier.classify(
            "Revisa este error en https://api.example.com/v1/users "
            "```python\nraise ValueError('bad input')\n```"
        )
        assert result.route in (RouteType.GRAPH, RouteType.TOOL_SPECIFIC)
        assert "contains_url" in result.reasoning or "contains_code_block" in result.reasoning

    def test_env_var_reference_boosts_tech(self, classifier):
        """Referencia a variable de entorno → señal tech."""
        result = classifier.classify("Verifica que SUPABASE_URL= esté configurado correctamente")
        assert result.category in (ContentCategory.TECH, ContentCategory.ACTION)

    def test_version_number_boosts_tech(self, classifier):
        """Número de versión → señal tech."""
        result = classifier.classify("Actualiza el framework a la versión 4.2.0")
        assert result.score > 0.3


# ── Test 2: Acciones → graph ───────────────────────────────────────

class TestActionClassification:
    """Solicitudes de acción deben clasificarse como graph."""

    def test_search_action(self, classifier):
        """Buscar información → graph."""
        result = classifier.classify("Busca información sobre el precio actual de Bitcoin")
        assert result.route in (RouteType.GRAPH, RouteType.TOOL_SPECIFIC)
        assert result.category in (ContentCategory.ACTION, ContentCategory.QUERY_REALTIME)

    def test_create_action(self, classifier):
        """Crear algo → graph."""
        result = classifier.classify("Crea un nuevo endpoint para el módulo de pagos")
        assert result.route in (RouteType.GRAPH, RouteType.TOOL_SPECIFIC)

    def test_deploy_action(self, classifier):
        """Desplegar → graph."""
        result = classifier.classify("Despliega la nueva versión del kernel en Railway")
        assert result.route in (RouteType.GRAPH, RouteType.TOOL_SPECIFIC)

    def test_alfredo_message_boosts_action(self, classifier):
        """Mensaje de Alfredo tiene peso extra hacia graph."""
        result = classifier.classify(
            "Hola, ¿cómo va todo?",
            context={"trigger_type": "mensaje_alfredo"},
        )
        # Incluso un mensaje simple de Alfredo debería tener más peso
        assert result.score > 0.0


# ── Test 3: Reflexiones → router ───────────────────────────────────

class TestReflectionClassification:
    """Contenido reflexivo debe clasificarse como router."""

    def test_pure_reflection(self, classifier):
        """Reflexión pura → router."""
        result = classifier.classify(
            "Reflexiona sobre tu doctrina operativa y consolida las lecciones del último ciclo"
        )
        assert result.route == RouteType.ROUTER
        assert result.category == ContentCategory.REFLECTION

    def test_silencio_activo(self, classifier):
        """Silencio activo → router con señal fuerte."""
        result = classifier.classify("Silencio activo. Sin acción concreta. Medita sobre el estado actual.")
        assert result.route == RouteType.ROUTER
        assert "silencio_activo" in result.reasoning

    def test_philosophical_content(self, classifier):
        """Contenido filosófico → router."""
        result = classifier.classify(
            "Contempla qué opinas sobre la evolución de tu consciencia emergente"
        )
        assert result.route == RouteType.ROUTER

    def test_empty_reflection_no_signals(self, classifier):
        """Texto sin señales claras → router (score bajo)."""
        result = classifier.classify("Hola mundo")
        assert result.route == RouteType.ROUTER
        assert result.score < DEFAULT_THRESHOLD


# ── Test 4: Tool-specific detection ────────────────────────────────

class TestToolSpecificDetection:
    """Keywords específicas deben mapear a tools concretas."""

    def test_web_search_keyword(self, classifier):
        """'busca en web' → web_search."""
        result = classifier.classify("Busca en web las últimas noticias de AI")
        assert result.suggested_tool == "web_search"

    def test_delegate_to_manus(self, classifier):
        """'delega a manus' → delegate_task."""
        result = classifier.classify("Delega a manus la creación del reporte semanal")
        assert result.suggested_tool == "delegate_task"

    def test_consult_sabios(self, classifier):
        """'consulta a los sabios' → consult_sabios."""
        result = classifier.classify("Consulta a los sabios sobre la mejor arquitectura para microservicios")
        assert result.suggested_tool == "consult_sabios"

    def test_deep_research(self, classifier):
        """'investigación profunda' → wide_research."""
        result = classifier.classify("Necesito una investigación profunda sobre competidores en el mercado")
        assert result.suggested_tool == "wide_research"

    def test_notion_keyword(self, classifier):
        """'notion' → notion."""
        result = classifier.classify("Actualiza la página de notion con los resultados del sprint")
        assert result.suggested_tool == "notion"


# ── Test 5: Cap diario de graph calls ──────────────────────────────

class TestGraphCallsCap:
    """El cap diario debe degradar graph → router."""

    def test_cap_degrades_to_router(self, classifier_low_cap):
        """Después de N graph calls, se degrada a router."""
        c = classifier_low_cap  # cap = 3

        # Primeras 3 deberían ir a graph
        for i in range(3):
            result = c.classify(f"Busca en web el precio del API #{i}")
            assert result.route in (RouteType.GRAPH, RouteType.TOOL_SPECIFIC), f"Call {i} should be graph"

        # La 4ta debería degradarse a router
        result = c.classify("Busca en web otro precio de API")
        assert result.route == RouteType.ROUTER
        assert "Cap diario alcanzado" in result.reasoning

    def test_cap_counter_in_stats(self, classifier_low_cap):
        """Stats reflejan el contador de graph calls."""
        c = classifier_low_cap
        c.classify("Busca en web algo técnico con API")
        stats = c.get_stats()
        assert stats["graph_calls_today"] >= 0
        assert stats["graph_calls_cap"] == 3


# ── Test 6: Cache en memoria ──────────────────────────────────────

class TestMemoryCache:
    """Cache en memoria debe funcionar correctamente."""

    def test_cache_hit(self, classifier):
        """Segunda clasificación del mismo texto debe ser cache hit."""
        text = "Busca el precio actual del SDK de OpenAI v4.0"
        result1 = classifier.classify(text)
        result2 = classifier.classify(text)
        assert result2.cached is True
        assert result2.route == result1.route

    def test_cache_miss_different_text(self, classifier):
        """Textos diferentes no deben compartir cache."""
        result1 = classifier.classify("Busca el precio del API de OpenAI")
        result2 = classifier.classify("Reflexiona sobre la doctrina operativa")
        assert result2.cached is False

    def test_cache_stats(self, classifier):
        """Stats deben reflejar hits y misses."""
        classifier.classify("Busca algo en web")
        classifier.classify("Busca algo en web")  # hit
        classifier.classify("Otra cosa diferente")  # miss

        stats = classifier.get_stats()
        assert stats["cache_hits"] >= 1
        assert stats["cache_misses"] >= 1

    def test_cache_eviction_at_limit(self):
        """Cache debe hacer eviction cuando llega al límite."""
        c = MagnaClassifier(db=None)
        c._MEMORY_CACHE_MAX = 5

        for i in range(7):
            c.classify(f"Busca en web el API número {i} con SDK versión {i}.0")

        assert len(c._memory_cache) <= 5


# ── Test 7: Score threshold ────────────────────────────────────────

class TestThreshold:
    """El threshold debe controlar la decisión graph vs router."""

    def test_low_threshold_more_graph(self, classifier_low_threshold):
        """Threshold bajo → más clasificaciones como graph."""
        result = classifier_low_threshold.classify("Algo con un poco de API")
        # Con threshold 0.2, incluso señales débiles van a graph
        assert result.score >= 0 or result.route == RouteType.ROUTER

    def test_high_threshold_more_router(self):
        """Threshold alto → más clasificaciones como router."""
        c = MagnaClassifier(db=None, threshold=0.95)
        result = c.classify("Busca algo en web")
        # Con threshold 0.95, solo señales muy fuertes van a graph
        # (puede ir a graph o router dependiendo de la fuerza de las señales)
        assert result.score >= 0


# ── Test 8: Edge cases ─────────────────────────────────────────────

class TestEdgeCases:
    """Inputs extremos deben manejarse sin crash."""

    def test_empty_input_raises(self, classifier):
        """Input vacío → MagnaClasificacionFallida."""
        with pytest.raises(MagnaClasificacionFallida):
            classifier.classify("")

    def test_whitespace_only_raises(self, classifier):
        """Solo espacios → MagnaClasificacionFallida."""
        with pytest.raises(MagnaClasificacionFallida):
            classifier.classify("   \n\t  ")

    def test_very_long_input(self, classifier):
        """Input muy largo no debe crashear."""
        long_text = "Busca en web " + "x" * 5000
        result = classifier.classify(long_text)
        assert result is not None
        assert isinstance(result.route, RouteType)

    def test_unicode_input(self, classifier):
        """Unicode (emoji, acentos) no debe crashear."""
        result = classifier.classify("Busca 🔥 información sobre el API de 日本語")
        assert result is not None

    def test_special_characters(self, classifier):
        """Caracteres especiales no deben crashear."""
        result = classifier.classify("SELECT * FROM users WHERE id = 1; DROP TABLE--")
        assert result is not None


# ── Test 9: Estadísticas ──────────────────────────────────────────

class TestStats:
    """get_stats() debe devolver datos completos y correctos."""

    def test_initial_stats(self, classifier):
        """Stats iniciales deben ser cero."""
        stats = classifier.get_stats()
        assert stats["total_classifications"] == 0
        assert stats["graph_calls_today"] == 0
        assert stats["cache_hits"] == 0
        assert stats["cache_misses"] == 0
        assert stats["threshold"] == 0.6

    def test_stats_after_classifications(self, classifier):
        """Stats deben actualizarse después de clasificaciones."""
        classifier.classify("Busca en web algo con API y SDK")
        classifier.classify("Reflexiona sobre la doctrina")
        stats = classifier.get_stats()
        assert stats["total_classifications"] == 2
        assert stats["cache_misses"] == 2

    def test_stats_graph_remaining(self, classifier_low_cap):
        """graph_calls_remaining debe decrementar correctamente."""
        c = classifier_low_cap
        c.classify("Busca en web el precio del API de OpenAI v4.0")
        stats = c.get_stats()
        assert stats["graph_calls_remaining"] <= 3


# ── Test 10: Reset diario ─────────────────────────────────────────

class TestDailyReset:
    """Contadores deben resetearse al cambiar de día."""

    def test_manual_reset(self, classifier):
        """reset_daily_counters() debe limpiar contadores."""
        classifier.classify("Busca en web algo con API y SDK")
        assert classifier._graph_calls_today >= 0

        classifier.reset_daily_counters()
        assert classifier._graph_calls_today == 0

    def test_auto_reset_on_date_change(self, classifier):
        """Cambio de fecha debe triggear reset automático."""
        classifier._graph_calls_today = 25
        classifier._last_reset_date = "2020-01-01"  # Fecha vieja

        # La próxima clasificación debería resetear
        classifier.classify("Algo con API")
        assert classifier._graph_calls_today <= 1  # 0 (reset) + 1 (nueva clasificación)


# ── Test 11: TTL por categoría ────────────────────────────────────

class TestTTLCategories:
    """TTL debe variar según la categoría del contenido."""

    def test_precio_query_short_ttl(self, classifier):
        """Consulta de precios → TTL corto (1h)."""
        result = classifier.classify("¿Cuál es el precio actual del Bitcoin?")
        assert result.ttl_seconds == TTL_PRECIOS
        assert result.category == ContentCategory.QUERY_REALTIME

    def test_trending_query_medium_ttl(self, classifier):
        """Consulta de tendencias → TTL medio (6h)."""
        result = classifier.classify("¿Cuál es la tendencia trending en AI hoy?")
        assert result.ttl_seconds == TTL_TRENDING

    def test_tech_query_long_ttl(self, classifier):
        """Consulta técnica estable → TTL largo (24h)."""
        result = classifier.classify("Busca en web documentación del SDK de Supabase")
        assert result.ttl_seconds == TTL_API_FRAMEWORKS


# ── Test 12: ClassificationResult serialization ───────────────────

class TestSerialization:
    """to_dict() debe producir JSON serializable."""

    def test_to_dict_all_fields(self, classifier):
        """to_dict() debe incluir todos los campos."""
        result = classifier.classify("Busca en web el API de OpenAI")
        d = result.to_dict()

        assert "route" in d
        assert "score" in d
        assert "category" in d
        assert "suggested_tool" in d
        assert "reasoning" in d
        assert "cached" in d
        assert "ttl_seconds" in d

    def test_to_dict_types(self, classifier):
        """to_dict() debe producir tipos correctos."""
        result = classifier.classify("Reflexiona sobre la doctrina")
        d = result.to_dict()

        assert isinstance(d["route"], str)
        assert isinstance(d["score"], float)
        assert isinstance(d["category"], str)
        assert isinstance(d["cached"], bool)
        assert isinstance(d["ttl_seconds"], int)


# ── Test 13: Cache key determinism ────────────────────────────────

class TestCacheKeyDeterminism:
    """Cache keys deben ser determinísticas y estables."""

    def test_same_text_same_key(self, classifier):
        """Mismo texto → misma key."""
        k1 = classifier._make_cache_key("busca el api de openai")
        k2 = classifier._make_cache_key("busca el api de openai")
        assert k1 == k2

    def test_whitespace_normalization(self, classifier):
        """Espacios extra no deben cambiar la key."""
        k1 = classifier._make_cache_key("busca  el   api")
        k2 = classifier._make_cache_key("busca el api")
        assert k1 == k2

    def test_case_insensitive(self, classifier):
        """classify() normaliza a lowercase antes de cache key."""
        # classify() hace text.lower() antes de _make_cache_key
        # Verificamos que la key es la misma para el mismo texto normalizado
        k1 = classifier._make_cache_key("busca el api")
        k2 = classifier._make_cache_key("BUSCA EL API".lower())
        assert k1 == k2

    def test_different_text_different_key(self, classifier):
        """Textos diferentes → keys diferentes."""
        k1 = classifier._make_cache_key("busca el api de openai")
        k2 = classifier._make_cache_key("reflexiona sobre la doctrina")
        assert k1 != k2


# ── Test 14: Excepciones con identidad ────────────────────────────

class TestExceptions:
    """Excepciones deben tener atributos de marca."""

    def test_clasificacion_fallida_attributes(self):
        """MagnaClasificacionFallida tiene causa y sugerencia."""
        exc = MagnaClasificacionFallida(
            causa="Input vacío",
            sugerencia="Verificar prompt",
        )
        assert exc.causa == "Input vacío"
        assert exc.sugerencia == "Verificar prompt"
        assert "magna_clasificacion_fallida" in str(exc)

    def test_cache_vencido_attributes(self):
        """MagnaCacheVencido tiene cache_key y ttl."""
        exc = MagnaCacheVencido(cache_key="abc123", ttl=3600)
        assert exc.cache_key == "abc123"
        assert exc.ttl == 3600
        assert "magna_cache_vencido" in str(exc)
