"""
El Monstruo — Tests de Convergencia (Sprint 1)
================================================
Tests para los 3 módulos importados del Hilo Bot:
- config/model_catalog.py (12 modelos, fallback chains)
- policy/matrix.py (5 clases, 3 hooks, pipeline)
- prompts/system_prompts.py (6 cerebros, classifier, dossier)
"""

import os
import sys

import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ===================== MODEL CATALOG TESTS =====================


class TestModelCatalog:
    """Tests for config/model_catalog.py"""

    def test_catalog_has_13_models(self):
        from config.model_catalog import MODELS

        assert len(MODELS) == 13, f"Expected 13 models, got {len(MODELS)}"

    def test_all_models_have_required_fields(self):
        from config.model_catalog import MODELS

        required = {"provider", "model_id", "litellm_alias", "roles", "validated"}
        for name, cfg in MODELS.items():
            missing = required - set(cfg.keys())
            assert not missing, f"Model {name} missing fields: {missing}"

    def test_gpt54_context_is_1m(self):
        """Anti-autoboicot: GPT-5.4 context must be 1,000,000 (not 1,050,000)"""
        from config.model_catalog import MODELS

        assert MODELS["gpt-5.4"]["context_window"] == 1_000_000

    def test_kimi_pricing_is_correct(self):
        """Anti-autoboicot: Kimi K2.5 input pricing must be $0.3827 (not $0.60)"""
        from config.model_catalog import MODELS

        assert MODELS["kimi-k2.5"]["pricing"]["input"] == 0.3827

    def test_grok_context_is_2m(self):
        """Grok 4.20 context window is 2M tokens"""
        from config.model_catalog import MODELS

        assert MODELS["grok-4.20"]["context_window"] == 2_000_000

    def test_claude_opus_exists(self):
        """Claude Opus 4.6 was added from Bot thread"""
        from config.model_catalog import MODELS

        assert "claude-opus-4-6" in MODELS
        assert MODELS["claude-opus-4-6"]["model_id"] == "claude-opus-4-6"

    def test_deepseek_r1_0528_exists(self):
        """DeepSeek R1 0528 was added from Bot thread"""
        from config.model_catalog import MODELS

        assert "deepseek-r1-0528" in MODELS
        assert MODELS["deepseek-r1-0528"]["model_id"] == "deepseek/deepseek-r1-0528"

    def test_all_litellm_aliases_unique(self):
        from config.model_catalog import MODELS

        aliases = [cfg["litellm_alias"] for cfg in MODELS.values()]
        assert len(aliases) == len(set(aliases)), f"Duplicate aliases: {aliases}"

    def test_get_model_function(self):
        from config.model_catalog import get_model

        model = get_model("gpt-5.4")
        assert model["provider"] == "openai"
        assert model["litellm_alias"] == "gpt-5"

    def test_get_model_raises_on_unknown(self):
        from config.model_catalog import get_model

        with pytest.raises(KeyError):
            get_model("nonexistent-model")

    def test_get_litellm_alias(self):
        from config.model_catalog import get_litellm_alias

        assert get_litellm_alias("gpt-5.4") == "gpt-5"
        assert get_litellm_alias("claude-opus-4-6") == "claude-opus-prev"
        assert get_litellm_alias("kimi-k2.5") == "kimi"

    def test_get_models_for_role(self):
        from config.model_catalog import get_models_for_role

        estrategas = get_models_for_role("estratega")
        assert "gpt-5.4" in estrategas

    def test_fallback_chains_exist(self):
        from config.model_catalog import FALLBACK_CHAINS

        assert len(FALLBACK_CHAINS) >= 10
        assert "estratega" in FALLBACK_CHAINS
        assert "investigador" in FALLBACK_CHAINS
        assert "motor_barato" in FALLBACK_CHAINS

    def test_fallback_chains_reference_valid_models(self):
        from config.model_catalog import FALLBACK_CHAINS, MODELS

        for role, chain in FALLBACK_CHAINS.items():
            for model_name in chain:
                assert model_name in MODELS, f"Fallback chain '{role}' references unknown model '{model_name}'"

    def test_sprint2_candidates_exist(self):
        from config.model_catalog import SPRINT2_CANDIDATES

        assert len(SPRINT2_CANDIDATES) >= 3

    def test_all_validated_dates_are_april_2026(self):
        from config.model_catalog import MODELS

        valid_dates = {"2026-04-12", "2026-04-18", "2026-04-20"}
        for name, cfg in MODELS.items():
            if "validated" in cfg:
                assert cfg["validated"] in valid_dates, f"Model {name} has stale validation date: {cfg['validated']}"


# ===================== POLICY MATRIX TESTS =====================


class TestPolicyMatrix:
    """Tests for policy/matrix.py"""

    def test_classify_financial(self):
        from policy.matrix import classify_action

        assert classify_action("pagar la factura de AWS") == "financial"
        assert classify_action("transferir dinero a la cuenta") == "financial"

    def test_classify_communications(self):
        from policy.matrix import classify_action

        assert classify_action("publicar el post en redes") == "communications"
        assert classify_action("enviar email al cliente") == "communications"

    def test_classify_data(self):
        from policy.matrix import classify_action

        assert classify_action("borrar los registros viejos") == "data"
        assert classify_action("exportar la base de datos") == "data"

    def test_classify_infrastructure(self):
        from policy.matrix import classify_action

        assert classify_action("desplegar la nueva versión") == "infrastructure"
        assert classify_action("reiniciar el servidor") == "infrastructure"

    def test_classify_information(self):
        from policy.matrix import classify_action

        assert classify_action("buscar información sobre el mercado") == "information"
        assert classify_action("analizar los datos de ventas") == "information"

    def test_classify_default_is_information(self):
        from policy.matrix import classify_action

        assert classify_action("hola cómo estás") == "information"

    @pytest.mark.asyncio
    async def test_policy_matrix_hook_financial_escalates(self):
        from contracts.policy_hook import PolicyContext, PolicyPhase, PolicyVerdict
        from policy.matrix import PolicyMatrixHook

        hook = PolicyMatrixHook()
        ctx = PolicyContext(
            message="pagar la factura de AWS",
            phase=PolicyPhase.PRE_EXECUTE,
        )
        decision = await hook.evaluate(ctx)
        assert decision.verdict == PolicyVerdict.ESCALATE
        assert decision.escalation_target == "telegram"

    @pytest.mark.asyncio
    async def test_policy_matrix_hook_info_allows(self):
        from contracts.policy_hook import PolicyContext, PolicyPhase, PolicyVerdict
        from policy.matrix import PolicyMatrixHook

        hook = PolicyMatrixHook()
        ctx = PolicyContext(
            message="buscar información sobre competidores",
            phase=PolicyPhase.PRE_EXECUTE,
        )
        decision = await hook.evaluate(ctx)
        assert decision.verdict == PolicyVerdict.ALLOW

    @pytest.mark.asyncio
    async def test_cost_guard_allows_under_limit(self):
        from contracts.policy_hook import PolicyContext, PolicyPhase, PolicyVerdict
        from policy.matrix import CostGuardHook

        hook = CostGuardHook(daily_limit_usd=50.0)
        ctx = PolicyContext(
            message="test",
            phase=PolicyPhase.PRE_EXECUTE,
        )
        decision = await hook.evaluate(ctx)
        assert decision.verdict == PolicyVerdict.ALLOW

    @pytest.mark.asyncio
    async def test_cost_guard_blocks_over_limit(self):
        from contracts.policy_hook import PolicyContext, PolicyPhase, PolicyVerdict
        from policy.matrix import CostGuardHook

        hook = CostGuardHook(daily_limit_usd=10.0)
        hook.add_cost(15.0)  # Exceed limit
        ctx = PolicyContext(
            message="test",
            phase=PolicyPhase.PRE_EXECUTE,
        )
        decision = await hook.evaluate(ctx)
        assert decision.verdict == PolicyVerdict.BLOCK

    @pytest.mark.asyncio
    async def test_cost_guard_reset(self):
        from contracts.policy_hook import PolicyContext, PolicyPhase, PolicyVerdict
        from policy.matrix import CostGuardHook

        hook = CostGuardHook(daily_limit_usd=10.0)
        hook.add_cost(15.0)
        hook.reset_daily()
        ctx = PolicyContext(
            message="test",
            phase=PolicyPhase.PRE_EXECUTE,
        )
        decision = await hook.evaluate(ctx)
        assert decision.verdict == PolicyVerdict.ALLOW

    @pytest.mark.asyncio
    async def test_content_filter_detects_credit_card(self):
        from contracts.policy_hook import PolicyContext, PolicyPhase, PolicyVerdict
        from policy.matrix import ContentFilterHook

        hook = ContentFilterHook()
        ctx = PolicyContext(
            response="Tu tarjeta es 4111 1111 1111 1111",
            phase=PolicyPhase.POST_EXECUTE,
        )
        decision = await hook.evaluate(ctx)
        assert decision.verdict == PolicyVerdict.MODIFY

    @pytest.mark.asyncio
    async def test_content_filter_allows_clean_text(self):
        from contracts.policy_hook import PolicyContext, PolicyPhase, PolicyVerdict
        from policy.matrix import ContentFilterHook

        hook = ContentFilterHook()
        ctx = PolicyContext(
            response="El mercado inmobiliario en Mérida creció 15%",
            phase=PolicyPhase.POST_EXECUTE,
        )
        decision = await hook.evaluate(ctx)
        assert decision.verdict == PolicyVerdict.ALLOW

    @pytest.mark.asyncio
    async def test_pipeline_creation(self):
        from policy.matrix import create_default_pipeline

        pipeline = await create_default_pipeline()
        hooks = await pipeline.get_active_policies()
        assert len(hooks) == 3
        # Verify priority order
        names = [h.name for h in hooks]
        assert names == ["cost_guard", "policy_matrix", "content_filter"]

    @pytest.mark.asyncio
    async def test_pipeline_evaluate_all(self):
        from contracts.policy_hook import PolicyContext, PolicyPhase
        from policy.matrix import create_default_pipeline

        pipeline = await create_default_pipeline()
        ctx = PolicyContext(
            message="buscar datos del mercado",
            phase=PolicyPhase.PRE_EXECUTE,
        )
        decisions = await pipeline.evaluate_all(ctx)
        assert len(decisions) >= 1  # At least cost_guard + policy_matrix

    @pytest.mark.asyncio
    async def test_pipeline_blocks_on_first_block(self):
        from contracts.policy_hook import PolicyContext, PolicyPhase, PolicyVerdict
        from policy.matrix import create_default_pipeline

        pipeline = await create_default_pipeline()
        # Get the cost guard and exceed its limit
        hooks = await pipeline.get_active_policies()
        for h in hooks:
            if h.name == "cost_guard":
                h.add_cost(100.0)  # Way over limit

        ctx = PolicyContext(
            message="pagar factura",
            phase=PolicyPhase.PRE_EXECUTE,
        )
        decisions = await pipeline.evaluate_all(ctx)
        assert decisions[0].verdict == PolicyVerdict.BLOCK
        assert len(decisions) == 1  # Stopped after BLOCK

    def test_is_escalation_required(self):
        from contracts.policy_hook import PolicyDecision, PolicyVerdict
        from policy.matrix import is_escalation_required

        decisions = [
            PolicyDecision(verdict=PolicyVerdict.ALLOW),
            PolicyDecision(verdict=PolicyVerdict.ESCALATE),
        ]
        assert is_escalation_required(decisions) is True

    def test_is_blocked(self):
        from contracts.policy_hook import PolicyDecision, PolicyVerdict
        from policy.matrix import is_blocked

        assert is_blocked([PolicyDecision(verdict=PolicyVerdict.BLOCK)]) is True
        assert is_blocked([PolicyDecision(verdict=PolicyVerdict.ALLOW)]) is False

    def test_get_escalation_target(self):
        from contracts.policy_hook import PolicyDecision, PolicyVerdict
        from policy.matrix import get_escalation_target

        decisions = [
            PolicyDecision(
                verdict=PolicyVerdict.ESCALATE,
                escalation_target="telegram",
            ),
        ]
        assert get_escalation_target(decisions) == "telegram"

    @pytest.mark.asyncio
    async def test_pipeline_unregister(self):
        from policy.matrix import create_default_pipeline

        pipeline = await create_default_pipeline()
        removed = await pipeline.unregister("cost_guard")
        assert removed is True
        hooks = await pipeline.get_active_policies()
        assert len(hooks) == 2


# ===================== SYSTEM PROMPTS TESTS =====================


class TestSystemPrompts:
    """Tests for prompts/system_prompts.py"""

    def test_6_brains_exist(self):
        from prompts.system_prompts import BRAIN_PROMPTS

        expected = {
            "estratega",
            "investigador",
            "arquitecto",
            "creativo",
            "critico",
            "operador",
        }
        assert set(BRAIN_PROMPTS.keys()) == expected

    def test_all_brains_have_user_dossier(self):
        from prompts.system_prompts import BRAIN_PROMPTS

        for brain, prompt in BRAIN_PROMPTS.items():
            assert "Alfredo" in prompt, f"Brain {brain} missing user dossier"
            assert "Hive" in prompt, f"Brain {brain} missing Hive reference"

    def test_get_brain_prompt_returns_correct(self):
        from prompts.system_prompts import get_brain_prompt

        prompt = get_brain_prompt("estratega")
        assert "ESTRATEGA" in prompt
        assert "Alfredo" in prompt

    def test_get_brain_prompt_fallback_to_operador(self):
        from prompts.system_prompts import get_brain_prompt

        prompt = get_brain_prompt("nonexistent_brain")
        assert "OPERADOR" in prompt

    def test_get_classifier_prompt(self):
        from prompts.system_prompts import get_classifier_prompt

        prompt = get_classifier_prompt()
        assert "estratega" in prompt
        assert "investigador" in prompt
        assert "operador" in prompt

    def test_get_user_dossier(self):
        from prompts.system_prompts import get_user_dossier

        dossier = get_user_dossier()
        assert "Alfredo Góngora" in dossier
        assert "Hive Business Center" in dossier
        assert "Mérida" in dossier

    def test_get_available_brains(self):
        from prompts.system_prompts import get_available_brains

        brains = get_available_brains()
        assert len(brains) == 6
        assert "estratega" in brains

    def test_brain_prompts_are_substantial(self):
        """Each brain prompt should be at least 500 chars (rich, not stub)"""
        from prompts.system_prompts import BRAIN_PROMPTS

        for brain, prompt in BRAIN_PROMPTS.items():
            assert len(prompt) > 500, f"Brain {brain} prompt too short ({len(prompt)} chars)"

    def test_classifier_mentions_all_brains(self):
        from prompts.system_prompts import get_available_brains, get_classifier_prompt

        prompt = get_classifier_prompt()
        for brain in get_available_brains():
            assert brain in prompt, f"Classifier missing brain: {brain}"


# ===================== ROUTER ENGINE CONVERGENCE TESTS =====================


class TestRouterConvergence:
    """Tests for the updated router/engine.py with brain support"""

    def test_brain_model_map_exists(self):
        from router.engine import BRAIN_MODEL_MAP

        assert len(BRAIN_MODEL_MAP) == 6
        assert BRAIN_MODEL_MAP["estratega"] == "gpt-5.4"
        assert BRAIN_MODEL_MAP["investigador"] == "sonar-reasoning-pro"
        assert BRAIN_MODEL_MAP["arquitecto"] == "claude-opus-4-6"

    def test_expanded_fallback_chain(self):
        from router.engine import FALLBACK_CHAIN

        assert "claude-opus-4-6" in FALLBACK_CHAIN
        assert "deepseek-r1-0528" in FALLBACK_CHAIN
        assert "sonar-reasoning-pro" in FALLBACK_CHAIN
        assert "kimi-k2.5" in FALLBACK_CHAIN
        assert "gpt-5.4-mini" in FALLBACK_CHAIN

    def test_fallback_chain_has_all_models(self):
        from router.engine import FALLBACK_CHAIN

        assert len(FALLBACK_CHAIN) >= 11

    def test_default_model_map_unchanged(self):
        """Original intent→model mapping should still work"""
        from contracts.kernel_interface import IntentType
        from router.engine import DEFAULT_MODEL_MAP

        assert DEFAULT_MODEL_MAP[IntentType.CHAT] == "gemini-3.1-flash-lite"
        assert DEFAULT_MODEL_MAP[IntentType.DEEP_THINK] == "gpt-5.4"
        assert DEFAULT_MODEL_MAP[IntentType.EXECUTE] == "claude-sonnet-4-6"


# ===================== LITELLM CONFIG TESTS =====================


class TestLiteLLMConfig:
    """Tests for the expanded litellm_config.yaml"""

    def test_config_file_exists(self):
        import yaml

        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "litellm_config.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert "model_list" in config

    def test_config_has_13_model_entries(self):
        """13 entries (12 models + fast-chat alias)"""
        import yaml

        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "litellm_config.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert len(config["model_list"]) == 13

    def test_config_has_new_models(self):
        import yaml

        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "litellm_config.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        names = [m["model_name"] for m in config["model_list"]]
        assert "claude-opus" in names
        assert "deepseek-r1" in names
        assert "sonar-reasoning" in names
        assert "gpt-5-mini" in names
        assert "gemini-pro" in names
        assert "kimi" in names

    def test_config_fallbacks_include_new_models(self):
        import yaml

        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "litellm_config.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        fallbacks = config["router_settings"]["fallbacks"]
        # Should have fallbacks for all models
        fallback_keys = set()
        for fb in fallbacks:
            fallback_keys.update(fb.keys())
        assert "claude-opus" in fallback_keys
        assert "kimi" in fallback_keys
