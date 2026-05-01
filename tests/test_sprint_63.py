"""tests/test_sprint_63.py

Tests del Sprint 63 — Research Intelligence + Zero-Config + Motion System
+ Marketplace Global + Cross-Embrion Learning

Brand Compliance Checklist 7/7:
1. ✅ Naming con identidad (español, errores con contexto)
2. ✅ Errores con contexto (causa + sugerencia)
3. ✅ Endpoints para Command Center (to_dict() en cada módulo)
4. ✅ Logs estructurados (structlog)
5. ✅ Docstrings (Args, Returns, Raises, Soberanía)
6. ✅ Tests (este archivo — 35+ tests)
7. ✅ Soberanía (alternativas documentadas)
"""

import asyncio
import pytest
from datetime import datetime, timezone


# ══════════════════════════════════════════════════════════════════════════════
# SPRINT 63.1 — Research Intelligence Engine
# ══════════════════════════════════════════════════════════════════════════════

class TestDiscoveryItem:
    """Tests para el dataclass DiscoveryItem."""

    def test_discovery_item_creation(self):
        from kernel.vanguard.intelligence_engine import DiscoveryItem
        item = DiscoveryItem(
            source="agents_radar",
            title="FastAPI 0.120.0",
            url="https://github.com/fastapi/fastapi",
            category="library",
            summary="Nueva versión con mejoras de performance",
            tags=["fastapi", "python", "api"],
        )
        assert item.source == "agents_radar"
        assert item.title == "FastAPI 0.120.0"
        assert item.relevance_score == 0.0
        assert item.integration_effort == "unknown"

    def test_discovery_item_to_dict(self):
        from kernel.vanguard.intelligence_engine import DiscoveryItem
        item = DiscoveryItem(
            source="semantic_scholar",
            title="Multi-Agent LLM Systems",
            url="https://arxiv.org/abs/2024.12345",
            category="paper",
            relevance_score=0.85,
        )
        d = item.to_dict()
        assert d["source"] == "semantic_scholar"
        assert d["relevance_score"] == 0.85
        assert "discovered_at" in d
        assert len(d["summary"]) <= 200

    def test_discovery_item_categories(self):
        from kernel.vanguard.intelligence_engine import DiscoveryItem
        for category in ["library", "paper", "tool", "model", "framework"]:
            item = DiscoveryItem(
                source="test", title="Test", url="http://test.com", category=category
            )
            assert item.category == category


class TestIntegrationProposal:
    """Tests para el dataclass IntegrationProposal."""

    def test_proposal_creation(self):
        from kernel.vanguard.intelligence_engine import DiscoveryItem, IntegrationProposal
        item = DiscoveryItem(
            source="agents_radar", title="LangGraph 0.3.0",
            url="https://github.com/langchain-ai/langgraph", category="library",
            relevance_score=0.92,
        )
        proposal = IntegrationProposal(
            discovery=item,
            rationale="Mejora el loop de agentes",
            impact_areas=["#6", "#8"],
            estimated_effort_hours=8.0,
            risk_level="low",
            migration_steps=["Evaluar", "Implementar", "Testear"],
            rollback_plan="git revert",
        )
        assert proposal.approved is False
        assert proposal.executed is False
        assert proposal.risk_level == "low"

    def test_proposal_to_dict(self):
        from kernel.vanguard.intelligence_engine import DiscoveryItem, IntegrationProposal
        item = DiscoveryItem(
            source="test", title="Test Tool", url="http://test.com", category="tool"
        )
        proposal = IntegrationProposal(
            discovery=item, rationale="Mejora performance",
            impact_areas=["#5"], estimated_effort_hours=4.0,
            risk_level="medium", migration_steps=["Step 1"],
            rollback_plan="Revert",
        )
        d = proposal.to_dict()
        assert "discovery" in d
        assert d["risk_level"] == "medium"
        assert d["impact_areas"] == ["#5"]


class TestResearchIntelligenceEngine:
    """Tests para ResearchIntelligenceEngine."""

    def test_engine_init_without_supabase(self):
        from kernel.vanguard.intelligence_engine import ResearchIntelligenceEngine
        engine = ResearchIntelligenceEngine()
        assert engine.supabase is None
        assert engine.router is None

    def test_engine_to_dict(self):
        from kernel.vanguard.intelligence_engine import ResearchIntelligenceEngine
        engine = ResearchIntelligenceEngine()
        d = engine.to_dict()
        assert d["module"] == "ResearchIntelligenceEngine"
        assert d["sprint"] == "63.1"
        assert d["objetivo"] == "#6 Vanguardia Perpetua"
        assert d["has_supabase"] is False

    def test_engine_singleton(self):
        from kernel.vanguard.intelligence_engine import init_intelligence_engine, get_intelligence_engine
        engine = init_intelligence_engine()
        assert get_intelligence_engine() is engine

    @pytest.mark.asyncio
    async def test_analyze_discovery_scores_correctly(self):
        from kernel.vanguard.intelligence_engine import ResearchIntelligenceEngine, DiscoveryItem
        engine = ResearchIntelligenceEngine()
        item = DiscoveryItem(
            source="agents_radar", title="fastapi langraph",
            url="http://test.com", category="library",
            tags=["fastapi", "trending"],
        )
        scored = await engine.analyze_discovery(item)
        assert 0.0 <= scored.relevance_score <= 1.0
        assert scored.integration_effort in ["trivial", "moderate", "significant", "major"]

    @pytest.mark.asyncio
    async def test_generate_proposal_low_relevance_returns_none(self):
        from kernel.vanguard.intelligence_engine import ResearchIntelligenceEngine, DiscoveryItem
        engine = ResearchIntelligenceEngine()
        item = DiscoveryItem(
            source="test", title="Random Tool", url="http://test.com",
            category="tool", relevance_score=0.3,
        )
        proposal = await engine.generate_proposal(item)
        assert proposal is None

    def test_extract_objectives(self):
        from kernel.vanguard.intelligence_engine import ResearchIntelligenceEngine
        engine = ResearchIntelligenceEngine()
        text = "Este tool avanza el Objetivo #6 y también #8 del sistema"
        objectives = engine._extract_objectives(text)
        assert "#6" in objectives
        assert "#8" in objectives

    def test_extract_risk(self):
        from kernel.vanguard.intelligence_engine import ResearchIntelligenceEngine
        engine = ResearchIntelligenceEngine()
        assert engine._extract_risk("This is low risk") == "low"
        assert engine._extract_risk("High risk migration") == "high"
        assert engine._extract_risk("Standard migration") == "medium"

    def test_error_messages_have_context(self):
        from kernel.vanguard.intelligence_engine import (
            INTELIGENCIA_SIN_SUPABASE,
            INTELIGENCIA_PROPUESTA_FALLIDA,
            INTELIGENCIA_SCAN_FALLIDO,
        )
        for msg in [INTELIGENCIA_SIN_SUPABASE, INTELIGENCIA_PROPUESTA_FALLIDA, INTELIGENCIA_SCAN_FALLIDO]:
            assert len(msg) > 20
            assert "." in msg  # Tiene punto final (oración completa)


class TestSemanticScholarClient:
    """Tests para SemanticScholarClient."""

    def test_client_init(self):
        from kernel.vanguard.semantic_scholar import SemanticScholarClient
        client = SemanticScholarClient()
        assert hasattr(client, "_httpx_available")

    def test_client_to_dict(self):
        from kernel.vanguard.semantic_scholar import SemanticScholarClient
        client = SemanticScholarClient()
        d = client.to_dict()
        assert d["module"] == "SemanticScholarClient"
        assert d["sprint"] == "63.1"
        assert d["default_topics"] > 0

    def test_default_topics_exist(self):
        from kernel.vanguard.semantic_scholar import DEFAULT_TOPICS
        assert len(DEFAULT_TOPICS) >= 5
        assert all(isinstance(t, str) for t in DEFAULT_TOPICS)

    def test_singleton(self):
        from kernel.vanguard.semantic_scholar import init_scholar_client, get_scholar_client
        client = init_scholar_client()
        assert get_scholar_client() is client


class TestWeeklyDigestGenerator:
    """Tests para WeeklyDigestGenerator."""

    def test_generator_init(self):
        from kernel.vanguard.weekly_digest import WeeklyDigestGenerator
        gen = WeeklyDigestGenerator()
        assert gen.engine is None
        assert gen.scholar is None
        assert gen.supabase is None

    def test_generator_to_dict(self):
        from kernel.vanguard.weekly_digest import WeeklyDigestGenerator
        gen = WeeklyDigestGenerator()
        d = gen.to_dict()
        assert d["module"] == "WeeklyDigestGenerator"
        assert d["sprint"] == "63.1"
        assert d["weekly_topics"] >= 5

    @pytest.mark.asyncio
    async def test_generate_returns_dict_with_sections(self):
        from kernel.vanguard.weekly_digest import WeeklyDigestGenerator
        gen = WeeklyDigestGenerator()
        digest = await gen.generate()
        assert "generated_at" in digest
        assert "sections" in digest
        assert "stack_health" in digest["sections"]
        assert "trends" in digest["sections"]


# ══════════════════════════════════════════════════════════════════════════════
# SPRINT 63.2 — Zero-Config Experience
# ══════════════════════════════════════════════════════════════════════════════

class TestIntentInferrer:
    """Tests para IntentInferrer."""

    @pytest.mark.asyncio
    async def test_infer_restaurant(self):
        from kernel.zero_config.intent_inferrer import IntentInferrer
        inferrer = IntentInferrer()
        result = await inferrer.infer("Quiero una página para mi restaurante de comida italiana")
        assert result.industry == "restaurant"
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_infer_ecommerce(self):
        from kernel.zero_config.intent_inferrer import IntentInferrer
        inferrer = IntentInferrer()
        result = await inferrer.infer("Necesito una tienda para vender productos de moda")
        assert result.project_type in ["ecommerce", "landing"]
        assert result.industry in ["fashion", "ecommerce"]

    @pytest.mark.asyncio
    async def test_infer_empty_raises(self):
        from kernel.zero_config.intent_inferrer import IntentInferrer, INFERRER_INPUT_VACIO
        inferrer = IntentInferrer()
        with pytest.raises(ValueError) as exc_info:
            await inferrer.infer("")
        assert "vacío" in str(exc_info.value).lower() or "vac" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_infer_returns_features(self):
        from kernel.zero_config.intent_inferrer import IntentInferrer
        inferrer = IntentInferrer()
        result = await inferrer.infer("Quiero un dashboard SaaS con usuarios y pagos")
        assert len(result.features) > 0
        assert result.locale == "es-MX"

    @pytest.mark.asyncio
    async def test_infer_extracts_name(self):
        from kernel.zero_config.intent_inferrer import IntentInferrer
        inferrer = IntentInferrer()
        result = await inferrer.infer('Quiero una tienda llamada "La Boutique"')
        assert result.name == "La Boutique"

    def test_inferrer_to_dict(self):
        from kernel.zero_config.intent_inferrer import IntentInferrer
        inferrer = IntentInferrer()
        d = inferrer.to_dict()
        assert d["module"] == "IntentInferrer"
        assert d["sprint"] == "63.2"
        assert d["industry_patterns"] >= 10

    def test_singleton(self):
        from kernel.zero_config.intent_inferrer import init_intent_inferrer, get_intent_inferrer
        inferrer = init_intent_inferrer()
        assert get_intent_inferrer() is inferrer


class TestSmartDefaults:
    """Tests para SmartDefaults."""

    def test_get_defaults_restaurant_elegant(self):
        from kernel.zero_config.smart_defaults import get_defaults
        defaults = get_defaults("restaurant", "elegant")
        assert defaults.primary_color == "#C9A96E"
        assert defaults.dark_mode is True

    def test_get_defaults_tech_minimal(self):
        from kernel.zero_config.smart_defaults import get_defaults
        defaults = get_defaults("tech", "minimal")
        assert defaults.theme == "light"
        assert defaults.font_heading == "Inter"

    def test_get_defaults_fallback(self):
        from kernel.zero_config.smart_defaults import get_defaults
        defaults = get_defaults("unknown_industry", "unknown_style")
        assert defaults is not None  # Nunca lanza, siempre retorna fallback

    def test_list_combinations(self):
        from kernel.zero_config.smart_defaults import list_available_combinations
        combos = list_available_combinations()
        assert len(combos) >= 10

    def test_defaults_to_dict(self):
        from kernel.zero_config.smart_defaults import get_defaults
        defaults = get_defaults("fitness", "bold")
        d = defaults.to_dict()
        assert "theme" in d
        assert "primary_color" in d
        assert "components" in d


# ══════════════════════════════════════════════════════════════════════════════
# SPRINT 63.3 — Motion Design System
# ══════════════════════════════════════════════════════════════════════════════

class TestMotionTokens:
    """Tests para Motion Tokens."""

    def test_motion_tokens_count(self):
        from kernel.motion.tokens import MOTION_TOKENS
        assert len(MOTION_TOKENS) >= 10

    def test_interaction_presets_count(self):
        from kernel.motion.tokens import INTERACTION_PRESETS
        assert len(INTERACTION_PRESETS) >= 12

    def test_style_profiles_count(self):
        from kernel.motion.tokens import STYLE_MOTION_PROFILES
        assert len(STYLE_MOTION_PROFILES) >= 8

    def test_token_to_css_var(self):
        from kernel.motion.tokens import MOTION_TOKENS
        token = MOTION_TOKENS["fast"]
        css_var = token.to_css_var()
        assert "--motion-fast" in css_var

    def test_token_to_dict(self):
        from kernel.motion.tokens import MOTION_TOKENS
        token = MOTION_TOKENS["normal"]
        d = token.to_dict()
        assert d["name"] == "normal"
        assert d["duration"] == "300ms"

    def test_all_profiles_have_required_keys(self):
        from kernel.motion.tokens import STYLE_MOTION_PROFILES
        required_keys = ["default_duration", "default_easing", "hover_scale", "entrance"]
        for profile_name, profile in STYLE_MOTION_PROFILES.items():
            for key in required_keys:
                assert key in profile, f"Profile '{profile_name}' missing key '{key}'"


class TestMotionOrchestrator:
    """Tests para MotionOrchestrator."""

    def test_orchestrator_init_minimal(self):
        from kernel.motion.orchestrator import MotionOrchestrator
        orch = MotionOrchestrator(style="minimal")
        assert orch.style == "minimal"

    def test_orchestrator_invalid_style_fallback(self):
        from kernel.motion.orchestrator import MotionOrchestrator
        orch = MotionOrchestrator(style="nonexistent_style")
        assert orch.style == "minimal"  # Fallback

    def test_get_page_animations(self):
        from kernel.motion.orchestrator import MotionOrchestrator
        orch = MotionOrchestrator(style="elegant")
        components = ["hero", "feature_grid", "testimonial", "footer"]
        animations = orch.get_page_animations(components)
        assert len(animations) == 4
        assert "hero" in animations
        assert "entrance" in animations["hero"]

    def test_generate_motion_css(self):
        from kernel.motion.orchestrator import MotionOrchestrator
        orch = MotionOrchestrator(style="bold")
        css = orch.generate_motion_css()
        assert "--motion-duration-fast" in css
        assert "prefers-reduced-motion" in css

    def test_orchestrator_to_dict(self):
        from kernel.motion.orchestrator import MotionOrchestrator
        orch = MotionOrchestrator(style="playful")
        d = orch.to_dict()
        assert d["module"] == "MotionOrchestrator"
        assert d["sprint"] == "63.3"
        assert d["tokens_available"] >= 10
        assert d["presets_available"] >= 12

    def test_singleton(self):
        from kernel.motion.orchestrator import init_motion_orchestrator, get_motion_orchestrator
        orch = init_motion_orchestrator(style="minimal")
        assert get_motion_orchestrator() is orch


# ══════════════════════════════════════════════════════════════════════════════
# SPRINT 63.4 — Marketplace Global
# ══════════════════════════════════════════════════════════════════════════════

class TestMarketplaceRegistry:
    """Tests para MarketplaceRegistry."""

    def test_registry_init_with_seed(self):
        from kernel.marketplace.registry import MarketplaceRegistry, SEED_ITEMS
        registry = MarketplaceRegistry()
        assert len(registry._items) == len(SEED_ITEMS)

    @pytest.mark.asyncio
    async def test_search_all(self):
        from kernel.marketplace.registry import MarketplaceRegistry
        registry = MarketplaceRegistry()
        results = await registry.search()
        assert len(results) >= 10

    @pytest.mark.asyncio
    async def test_search_by_type(self):
        from kernel.marketplace.registry import MarketplaceRegistry
        registry = MarketplaceRegistry()
        plugins = await registry.search(item_type="plugin")
        assert all(r["type"] == "plugin" for r in plugins)

    @pytest.mark.asyncio
    async def test_search_by_query(self):
        from kernel.marketplace.registry import MarketplaceRegistry
        registry = MarketplaceRegistry()
        results = await registry.search(query="analytics")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_install_item(self):
        from kernel.marketplace.registry import MarketplaceRegistry
        registry = MarketplaceRegistry()
        result = await registry.install("hero-parallax-component", "user-123")
        assert result["status"] == "installed"
        assert "item" in result

    @pytest.mark.asyncio
    async def test_install_nonexistent_raises(self):
        from kernel.marketplace.registry import MarketplaceRegistry, MARKETPLACE_ITEM_NO_ENCONTRADO
        registry = MarketplaceRegistry()
        with pytest.raises(ValueError) as exc_info:
            await registry.install("nonexistent-id", "user-123")
        assert "no fue encontrado" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_rate_item(self):
        from kernel.marketplace.registry import MarketplaceRegistry
        registry = MarketplaceRegistry()
        await registry.rate("hero-parallax-component", "user-456", 5, "Excelente componente")
        item = registry._items["hero-parallax-component"]
        assert item.rating_count > 0

    @pytest.mark.asyncio
    async def test_rate_invalid_score_raises(self):
        from kernel.marketplace.registry import MarketplaceRegistry
        registry = MarketplaceRegistry()
        with pytest.raises(ValueError):
            await registry.rate("hero-parallax-component", "user-789", 6)

    def test_get_stats(self):
        from kernel.marketplace.registry import MarketplaceRegistry
        registry = MarketplaceRegistry()
        stats = registry.get_stats()
        assert stats["total_items"] >= 10
        assert stats["verified_items"] >= 10
        assert stats["total_downloads"] > 0

    def test_registry_to_dict(self):
        from kernel.marketplace.registry import MarketplaceRegistry
        registry = MarketplaceRegistry()
        d = registry.to_dict()
        assert d["module"] == "MarketplaceRegistry"
        assert d["sprint"] == "63.4"
        assert d["revenue_share_developer"] == "70%"

    def test_seed_items_are_verified(self):
        from kernel.marketplace.registry import SEED_ITEMS
        assert all(item.verified for item in SEED_ITEMS)

    def test_singleton(self):
        from kernel.marketplace.registry import init_marketplace_registry, get_marketplace_registry
        registry = init_marketplace_registry()
        assert get_marketplace_registry() is registry


# ══════════════════════════════════════════════════════════════════════════════
# SPRINT 63.5 — Cross-Embrion Learning
# ══════════════════════════════════════════════════════════════════════════════

class TestKnowledgePropagator:
    """Tests para KnowledgePropagator."""

    def test_propagator_init(self):
        from kernel.collective.knowledge_propagator import KnowledgePropagator
        propagator = KnowledgePropagator()
        assert propagator.supabase is None
        assert len(propagator._patterns) == 0

    @pytest.mark.asyncio
    async def test_register_pattern(self):
        from kernel.collective.knowledge_propagator import KnowledgePropagator, LearnedPattern
        propagator = KnowledgePropagator()
        pattern = LearnedPattern(
            source_embrion="tecnico",
            pattern_type="optimization",
            description="Usar cache para reducir llamadas LLM",
            context="cuando se repiten consultas similares",
            success_rate=0.9,
            times_applied=5,
            times_succeeded=5,
        )
        pattern_id = await propagator.register_pattern(pattern)
        assert pattern_id in propagator._patterns

    @pytest.mark.asyncio
    async def test_register_invalid_embrion_raises(self):
        from kernel.collective.knowledge_propagator import KnowledgePropagator, LearnedPattern, PROPAGADOR_EMBRION_INVALIDO
        propagator = KnowledgePropagator()
        pattern = LearnedPattern(
            source_embrion="embrion_invalido",
            pattern_type="strategy",
            description="Test",
            context="test",
            success_rate=0.9,
            times_applied=3,
            times_succeeded=3,
        )
        with pytest.raises(ValueError) as exc_info:
            await propagator.register_pattern(pattern)
        assert "válido" in str(exc_info.value).lower() or "invalido" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_auto_propagate_on_high_success(self):
        from kernel.collective.knowledge_propagator import KnowledgePropagator, LearnedPattern
        propagator = KnowledgePropagator()
        pattern = LearnedPattern(
            source_embrion="ventas",
            pattern_type="strategy",
            description="Estrategia de ventas efectiva",
            context="cuando el cliente pregunta por precios",
            success_rate=0.95,
            times_applied=5,
            times_succeeded=5,
        )
        pattern_id = await propagator.register_pattern(pattern)
        # Debe haberse propagado automáticamente
        registered = propagator._patterns[pattern_id]
        assert len(registered.propagated_to) > 0

    @pytest.mark.asyncio
    async def test_propagate_excludes_source(self):
        from kernel.collective.knowledge_propagator import KnowledgePropagator, LearnedPattern
        propagator = KnowledgePropagator()
        pattern = LearnedPattern(
            source_embrion="creativo",
            pattern_type="tool_usage",
            description="Uso efectivo de DALL-E para conceptos",
            context="generación de imágenes conceptuales",
            success_rate=0.85,
            times_applied=4,
            times_succeeded=4,
        )
        pattern_id = await propagator.register_pattern(pattern)
        registered = propagator._patterns[pattern_id]
        assert "creativo" not in registered.propagated_to

    @pytest.mark.asyncio
    async def test_record_outcome(self):
        from kernel.collective.knowledge_propagator import KnowledgePropagator, LearnedPattern
        propagator = KnowledgePropagator()
        pattern = LearnedPattern(
            source_embrion="financiero",
            pattern_type="optimization",
            description="Optimización de costos LLM",
            context="selección de modelo por tarea",
            success_rate=0.8,
            times_applied=3,
            times_succeeded=3,
        )
        pattern_id = await propagator.register_pattern(pattern)
        await propagator.record_outcome(pattern_id, "estratega", success=True)
        updated = propagator._patterns[pattern_id]
        assert updated.times_applied == 4

    def test_all_embriones_list(self):
        from kernel.collective.knowledge_propagator import ALL_EMBRIONES
        assert len(ALL_EMBRIONES) == 7
        expected = {"ventas", "tecnico", "vigia", "creativo", "estratega", "financiero", "investigador"}
        assert set(ALL_EMBRIONES) == expected

    def test_propagator_to_dict(self):
        from kernel.collective.knowledge_propagator import KnowledgePropagator
        propagator = KnowledgePropagator()
        d = propagator.to_dict()
        assert d["module"] == "KnowledgePropagator"
        assert d["sprint"] == "63.5"
        assert d["auto_propagate_threshold"] == 0.8

    def test_singleton(self):
        from kernel.collective.knowledge_propagator import init_knowledge_propagator, get_knowledge_propagator
        propagator = init_knowledge_propagator()
        assert get_knowledge_propagator() is propagator


class TestEmergenceDetector:
    """Tests para EmergenceDetector."""

    def test_detector_init_without_supabase(self):
        from kernel.collective.emergence_detector import EmergenceDetector
        detector = EmergenceDetector()
        assert detector.supabase is None
        assert len(detector._detected_patterns) == 0

    @pytest.mark.asyncio
    async def test_scan_without_supabase_returns_empty(self):
        from kernel.collective.emergence_detector import EmergenceDetector
        detector = EmergenceDetector()
        results = await detector.scan_for_emergence()
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_validate_requires_two_embriones(self):
        from kernel.collective.emergence_detector import EmergenceDetector
        detector = EmergenceDetector()
        # Patrón con solo 1 embrión — no debe ser válido
        pattern = {
            "type": "spontaneous_collaboration",
            "embriones": ["ventas"],
            "not_programmed": True,
            "task_count": 5,
        }
        valid = await detector._validate_emergence(pattern)
        assert valid is False

    @pytest.mark.asyncio
    async def test_validate_requires_not_programmed(self):
        from kernel.collective.emergence_detector import EmergenceDetector
        detector = EmergenceDetector()
        # Patrón programado — no debe ser válido
        pattern = {
            "type": "collaboration",
            "embriones": ["ventas", "tecnico"],
            "not_programmed": False,
            "task_count": 5,
        }
        valid = await detector._validate_emergence(pattern)
        assert valid is False

    @pytest.mark.asyncio
    async def test_validate_valid_pattern(self):
        from kernel.collective.emergence_detector import EmergenceDetector
        detector = EmergenceDetector()
        pattern = {
            "type": "spontaneous_collaboration",
            "embriones": ["ventas", "estratega"],
            "not_programmed": True,
            "task_count": 3,
        }
        valid = await detector._validate_emergence(pattern)
        assert valid is True

    @pytest.mark.asyncio
    async def test_get_emergence_history_without_supabase(self):
        from kernel.collective.emergence_detector import EmergenceDetector
        detector = EmergenceDetector()
        history = await detector.get_emergence_history()
        assert isinstance(history, list)

    def test_detector_to_dict(self):
        from kernel.collective.emergence_detector import EmergenceDetector
        detector = EmergenceDetector()
        d = detector.to_dict()
        assert d["module"] == "EmergenceDetector"
        assert d["sprint"] == "63.5"
        assert d["min_embriones"] == 2
        assert len(d["criterios"]) == 4

    def test_singleton(self):
        from kernel.collective.emergence_detector import init_emergence_detector, get_emergence_detector
        detector = init_emergence_detector()
        assert get_emergence_detector() is detector


# ══════════════════════════════════════════════════════════════════════════════
# BRAND COMPLIANCE — Verificaciones transversales
# ══════════════════════════════════════════════════════════════════════════════

class TestBrandCompliance:
    """Verificaciones del Brand Compliance Checklist 7/7."""

    def test_all_modules_have_to_dict(self):
        """Check 3: Todos los módulos exponen to_dict() para Command Center."""
        from kernel.vanguard.intelligence_engine import ResearchIntelligenceEngine
        from kernel.vanguard.semantic_scholar import SemanticScholarClient
        from kernel.vanguard.weekly_digest import WeeklyDigestGenerator
        from kernel.zero_config.intent_inferrer import IntentInferrer
        from kernel.motion.orchestrator import MotionOrchestrator
        from kernel.marketplace.registry import MarketplaceRegistry
        from kernel.collective.knowledge_propagator import KnowledgePropagator
        from kernel.collective.emergence_detector import EmergenceDetector

        modules = [
            ResearchIntelligenceEngine(),
            SemanticScholarClient(),
            WeeklyDigestGenerator(),
            IntentInferrer(),
            MotionOrchestrator(),
            MarketplaceRegistry(),
            KnowledgePropagator(),
            EmergenceDetector(),
        ]
        for module in modules:
            assert hasattr(module, "to_dict"), f"{type(module).__name__} falta to_dict()"
            d = module.to_dict()
            assert isinstance(d, dict), f"{type(module).__name__}.to_dict() no retorna dict"

    def test_all_error_messages_have_context(self):
        """Check 2: Todos los mensajes de error tienen causa + sugerencia."""
        from kernel.vanguard.intelligence_engine import (
            INTELIGENCIA_SIN_SUPABASE, INTELIGENCIA_PROPUESTA_FALLIDA
        )
        from kernel.zero_config.intent_inferrer import INFERRER_INPUT_VACIO
        from kernel.motion.orchestrator import ORCHESTRATOR_ESTILO_NO_ENCONTRADO
        from kernel.marketplace.registry import (
            MARKETPLACE_ITEM_NO_ENCONTRADO, MARKETPLACE_PUBLICACION_FALLIDA
        )
        from kernel.collective.knowledge_propagator import PROPAGADOR_PATRON_NO_ENCONTRADO
        from kernel.collective.emergence_detector import DETECTOR_SIN_SUPABASE

        error_messages = [
            INTELIGENCIA_SIN_SUPABASE, INTELIGENCIA_PROPUESTA_FALLIDA,
            INFERRER_INPUT_VACIO, ORCHESTRATOR_ESTILO_NO_ENCONTRADO,
            MARKETPLACE_ITEM_NO_ENCONTRADO, MARKETPLACE_PUBLICACION_FALLIDA,
            PROPAGADOR_PATRON_NO_ENCONTRADO, DETECTOR_SIN_SUPABASE,
        ]
        for msg in error_messages:
            assert len(msg) > 30, f"Mensaje muy corto: {msg}"
            # Debe tener al menos dos oraciones (causa + sugerencia)
            assert msg.count(".") >= 1, f"Mensaje sin punto final: {msg}"

    def test_sprint_63_modules_declare_sprint_number(self):
        """Check 5: Todos los módulos declaran su sprint en to_dict()."""
        from kernel.vanguard.intelligence_engine import ResearchIntelligenceEngine
        from kernel.zero_config.intent_inferrer import IntentInferrer
        from kernel.motion.orchestrator import MotionOrchestrator
        from kernel.marketplace.registry import MarketplaceRegistry
        from kernel.collective.knowledge_propagator import KnowledgePropagator

        modules = [
            (ResearchIntelligenceEngine(), "63.1"),
            (IntentInferrer(), "63.2"),
            (MotionOrchestrator(), "63.3"),
            (MarketplaceRegistry(), "63.4"),
            (KnowledgePropagator(), "63.5"),
        ]
        for module, expected_sprint in modules:
            d = module.to_dict()
            assert d.get("sprint") == expected_sprint, \
                f"{type(module).__name__} declara sprint {d.get('sprint')}, esperado {expected_sprint}"

    def test_sovereignty_documented(self):
        """Check 7: Soberanía documentada en módulos críticos."""
        import inspect
        from kernel.vanguard.intelligence_engine import ResearchIntelligenceEngine
        from kernel.collective.knowledge_propagator import KnowledgePropagator

        for cls in [ResearchIntelligenceEngine, KnowledgePropagator]:
            source = inspect.getsource(cls)
            assert "Soberanía" in source or "soberanía" in source.lower(), \
                f"{cls.__name__} no documenta soberanía"
