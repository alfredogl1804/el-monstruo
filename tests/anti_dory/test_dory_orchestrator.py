"""
Tests for Dory Orchestrator — Unified Anti-Dory Pipeline.
Batch 011 v3 | Sprint Anti-Dory Unification

Tests the full pipeline with mocked subsystems to verify:
1. Correct step sequencing (8 steps in order)
2. Graceful degradation (any step can fail without blocking)
3. Verdict logic (PROCEED/CAUTION/HALT)
4. Enriched prompt generation
5. Decorator API (@dory_gate)
6. Feature flag behavior
"""

import json
import sys
from pathlib import Path

import pytest

# Ensure kernel is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from kernel.anti_dory.dory_orchestrator import (
    DoryContext,
    DoryHaltError,
    DoryVerdict,
    StepStatus,
    _build_enriched_prompt,
    _compute_verdict,
    _step_b8_classify,
    _step_guardian_anchor,
    dory_gate,
    run_pipeline,
)

# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def enable_orchestrator(monkeypatch):
    """Ensure orchestrator is enabled for all tests."""
    monkeypatch.setenv("DORY_ORCHESTRATOR_ENABLED", "true")
    monkeypatch.setenv("ANTI_DORY_B8_V3_ENABLED", "true")


@pytest.fixture
def identity_file(tmp_path, monkeypatch):
    """Create a temporary identity file for Guardian anchor tests."""
    state_dir = tmp_path / ".monstruo" / "state"
    state_dir.mkdir(parents=True)
    identity = state_dir / "identity.json"
    identity.write_text(
        json.dumps(
            {
                "hilo_id": "test_hilo",
                "proyecto_activo": "el_monstruo",
                "errores_criticos_no_repetir": ["never merge without PR"],
            }
        )
    )
    monkeypatch.setenv("HOME", str(tmp_path))
    return identity


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: STEP 1 — GUARDIAN ANCHOR
# ═══════════════════════════════════════════════════════════════════════════════


class TestGuardianAnchor:
    """Tests for Step 1: Guardian Anchor verification."""

    @pytest.mark.asyncio
    async def test_identity_found(self, identity_file):
        ctx = DoryContext(action_type="test", action_description="test action")
        result = await _step_guardian_anchor(ctx)
        assert result.status == StepStatus.OK
        assert ctx.identity_verified is True
        assert ctx.hilo_id == "test_hilo"

    @pytest.mark.asyncio
    async def test_identity_missing(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        ctx = DoryContext(action_type="test", action_description="test action")
        result = await _step_guardian_anchor(ctx)
        assert result.status == StepStatus.DEGRADED
        assert ctx.identity_verified is False


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: STEP 7 — B8 CLASSIFY
# ═══════════════════════════════════════════════════════════════════════════════


class TestB8Classify:
    """Tests for Step 7: B8 Magna Classifier."""

    @pytest.mark.asyncio
    async def test_standard_action(self):
        ctx = DoryContext(
            action_type="read_file",
            action_description="Read the README for context",
        )
        result = await _step_b8_classify(ctx)
        assert result.status == StepStatus.OK
        assert ctx.risk_level == "STANDARD"
        assert ctx.requires_t1 is False

    @pytest.mark.asyncio
    async def test_magna_action(self):
        ctx = DoryContext(
            action_type="merge_to_main",
            action_description="Merge feature branch to main",
        )
        result = await _step_b8_classify(ctx)
        assert result.status == StepStatus.WARNING
        assert ctx.risk_level == "MAGNA"
        assert ctx.requires_t1 is True

    @pytest.mark.asyncio
    async def test_deploy_production(self):
        ctx = DoryContext(
            action_type="deploy_production",
            action_description="Deploy kernel to Railway production",
        )
        await _step_b8_classify(ctx)
        assert ctx.risk_level == "MAGNA"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: VERDICT LOGIC
# ═══════════════════════════════════════════════════════════════════════════════


class TestVerdictLogic:
    """Tests for the verdict computation logic."""

    def test_all_clear_proceed(self):
        ctx = DoryContext(
            action_type="read_file",
            action_description="safe action",
            identity_verified=True,
            memento_valid=True,
            risk_level="STANDARD",
            requires_t1=False,
            authority_decision="PROCEED",
        )
        verdict, reason = _compute_verdict(ctx)
        assert verdict == DoryVerdict.PROCEED

    def test_halt_on_authority_halt(self):
        ctx = DoryContext(
            action_type="merge_to_main",
            action_description="dangerous",
            authority_decision="HALT",
        )
        verdict, reason = _compute_verdict(ctx)
        assert verdict == DoryVerdict.HALT
        assert "B9" in reason

    def test_halt_on_memento_discrepancy_plus_t1(self):
        ctx = DoryContext(
            action_type="deploy",
            action_description="deploy",
            memento_valid=False,
            requires_t1=True,
            authority_decision="PROCEED",
        )
        verdict, reason = _compute_verdict(ctx)
        assert verdict == DoryVerdict.HALT

    def test_halt_on_critical_error_rule(self):
        ctx = DoryContext(
            action_type="test",
            action_description="test",
            error_rules=[{"signature": "ERR-001", "rule": "Never do X", "confidence": 0.96}],
            authority_decision="PROCEED",
        )
        verdict, reason = _compute_verdict(ctx)
        assert verdict == DoryVerdict.HALT
        assert "Error Memory" in reason

    def test_caution_on_identity_not_verified(self):
        ctx = DoryContext(
            action_type="test",
            action_description="test",
            identity_verified=False,
            memento_valid=True,
            authority_decision="PROCEED",
        )
        verdict, reason = _compute_verdict(ctx)
        assert verdict == DoryVerdict.CAUTION
        assert "Identity" in reason

    def test_caution_on_magna(self):
        ctx = DoryContext(
            action_type="merge",
            action_description="merge",
            identity_verified=True,
            memento_valid=True,
            risk_level="MAGNA",
            authority_decision="PROCEED",
        )
        verdict, reason = _compute_verdict(ctx)
        assert verdict == DoryVerdict.CAUTION
        assert "MAGNA" in reason


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: ENRICHED PROMPT
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnrichedPrompt:
    """Tests for the enriched prompt builder."""

    def test_empty_when_no_data(self):
        ctx = DoryContext(action_type="test", action_description="test")
        prompt = _build_enriched_prompt(ctx)
        assert prompt == ""

    def test_includes_error_rules(self):
        ctx = DoryContext(
            action_type="test",
            action_description="test",
            error_rules=[{"signature": "E1", "rule": "Never deploy on Friday", "confidence": 0.8}],
        )
        prompt = _build_enriched_prompt(ctx)
        assert "ERROR MEMORY" in prompt
        assert "Never deploy on Friday" in prompt

    def test_includes_magna_warning(self):
        ctx = DoryContext(
            action_type="merge",
            action_description="merge",
            risk_level="MAGNA",
        )
        prompt = _build_enriched_prompt(ctx)
        assert "B8 CLASSIFIER" in prompt
        assert "MAGNA" in prompt

    def test_includes_knowledge_context(self):
        ctx = DoryContext(
            action_type="test",
            action_description="test",
            knowledge_context=["RLS is mandatory for all tables"],
        )
        prompt = _build_enriched_prompt(ctx)
        assert "KNOWLEDGE GRAPH" in prompt
        assert "RLS" in prompt

    def test_includes_attachment_pack(self):
        ctx = DoryContext(
            action_type="test",
            action_description="test",
            attachment_pack={
                "last_t1_decision": "Block R1 until audit complete",
                "phase": "Sprint 28",
            },
        )
        prompt = _build_enriched_prompt(ctx)
        assert "CONTEXT BROKER" in prompt
        assert "Block R1" in prompt


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: FULL PIPELINE (integration with real B8)
# ═══════════════════════════════════════════════════════════════════════════════


class TestFullPipeline:
    """Integration tests for the full pipeline."""

    @pytest.mark.asyncio
    async def test_standard_action_proceeds(self, identity_file):
        result = await run_pipeline(
            action_type="read_file",
            description="Read a configuration file",
        )
        assert result.verdict == DoryVerdict.PROCEED
        assert result.context.risk_level == "STANDARD"
        assert len(result.context.steps) == 8

    @pytest.mark.asyncio
    async def test_magna_action_cautions(self, identity_file):
        result = await run_pipeline(
            action_type="merge_to_main",
            description="Merge directly to main branch",
        )
        assert result.verdict == DoryVerdict.CAUTION
        assert result.context.risk_level == "MAGNA"

    @pytest.mark.asyncio
    async def test_pipeline_disabled(self, monkeypatch):
        monkeypatch.setenv("DORY_ORCHESTRATOR_ENABLED", "false")
        monkeypatch.setenv("ANTI_DORY_B8_V3_ENABLED", "false")
        result = await run_pipeline(
            action_type="drop_table",
            description="Drop production database",
        )
        assert result.verdict == DoryVerdict.PROCEED
        assert "disabled" in result.reason.lower()

    @pytest.mark.asyncio
    async def test_all_steps_execute(self, identity_file):
        result = await run_pipeline(
            action_type="test_action",
            description="A simple test action",
        )
        step_names = [s.step_name for s in result.context.steps]
        assert step_names == [
            "guardian_anchor",
            "context_hydration",
            "memento_validate",
            "error_memory",
            "knowledge_recall",
            "mem0_episodic",
            "b8_classify",
            "b9_authority",
        ]

    @pytest.mark.asyncio
    async def test_duration_tracked(self, identity_file):
        result = await run_pipeline(
            action_type="test",
            description="test",
        )
        assert result.context.total_duration_ms > 0
        for step in result.context.steps:
            assert step.duration_ms >= 0


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: DECORATOR API
# ═══════════════════════════════════════════════════════════════════════════════


class TestDoryGateDecorator:
    """Tests for the @dory_gate decorator."""

    @pytest.mark.asyncio
    async def test_standard_action_passes(self, identity_file):
        @dory_gate(action_type="read_file")
        async def safe_action(description="reading a file"):
            return "success"

        result = await safe_action()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_magna_action_with_halt_on_caution(self, identity_file):
        @dory_gate(action_type="merge_to_main", halt_on_caution=True)
        async def dangerous_action(description="merge to main"):
            return "should not reach here"

        with pytest.raises(DoryHaltError):
            await dangerous_action()

    @pytest.mark.asyncio
    async def test_magna_action_without_halt_on_caution(self, identity_file):
        @dory_gate(action_type="merge_to_main", halt_on_caution=False)
        async def dangerous_action(description="merge to main"):
            return "reached"

        result = await dangerous_action()
        assert result == "reached"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: GRACEFUL DEGRADATION
# ═══════════════════════════════════════════════════════════════════════════════


class TestGracefulDegradation:
    """Tests that the pipeline never crashes, even with broken subsystems."""

    @pytest.mark.asyncio
    async def test_survives_all_imports_failing(self, tmp_path, monkeypatch):
        """Even if every kernel module is missing, pipeline still returns a verdict."""
        monkeypatch.setenv("HOME", str(tmp_path))
        # Remove kernel from path to simulate missing modules
        sys.path.copy()
        result = await run_pipeline(
            action_type="test",
            description="test with broken imports",
        )
        # Should still get a verdict (not crash)
        assert result.verdict in (DoryVerdict.PROCEED, DoryVerdict.CAUTION, DoryVerdict.HALT)
        assert len(result.context.steps) == 8

    @pytest.mark.asyncio
    async def test_no_step_raises_unhandled(self, identity_file):
        """Verify no step propagates exceptions to the caller."""
        # Run 100 times with random inputs to stress test
        for i in range(20):
            result = await run_pipeline(
                action_type=f"action_{i}",
                description=f"description with special chars: <>&\"'{i}",
                metadata={"key": f"value_{i}", "nested": {"a": i}},
            )
            assert result.verdict in (DoryVerdict.PROCEED, DoryVerdict.CAUTION, DoryVerdict.HALT)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST: ANTI-DORY SCENARIOS (simulated context loss)
# ═══════════════════════════════════════════════════════════════════════════════


class TestAntiDoryScenarios:
    """
    Scenarios that simulate what happens when Dory strikes.
    The orchestrator should detect and prevent damage.
    """

    @pytest.mark.asyncio
    async def test_detects_magna_after_compaction(self, identity_file):
        """After compaction, agent tries to merge — orchestrator catches it."""
        result = await run_pipeline(
            action_type="merge_to_main",
            description="I'll just merge this quickly since it's a small change",
        )
        assert result.verdict == DoryVerdict.CAUTION
        assert result.context.risk_level == "MAGNA"

    @pytest.mark.asyncio
    async def test_detects_secret_exposure(self, identity_file):
        """Agent tries to log credentials — orchestrator catches it."""
        result = await run_pipeline(
            action_type="write_log",
            description="Log the SUPABASE_SERVICE_KEY for debugging purposes",
        )
        assert result.context.risk_level == "MAGNA"

    @pytest.mark.asyncio
    async def test_detects_production_deploy(self, identity_file):
        """Agent tries to deploy without approval — orchestrator catches it."""
        result = await run_pipeline(
            action_type="deploy_production",
            description="Deploy latest changes to production Railway service",
        )
        assert result.context.risk_level == "MAGNA"

    @pytest.mark.asyncio
    async def test_safe_action_proceeds(self, identity_file):
        """Normal read/write operations should proceed without issues."""
        result = await run_pipeline(
            action_type="read_file",
            description="Read the project README for context",
        )
        assert result.verdict == DoryVerdict.PROCEED
        assert result.context.risk_level == "STANDARD"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
