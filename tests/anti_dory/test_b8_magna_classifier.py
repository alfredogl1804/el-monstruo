"""
Unit Tests — B8 Magna Classifier
Anti-Dory FORGE v3.0 — Batch 004 Célula A

Tests puros en memoria. Sin Supabase. Sin APIs externas.
"""

import pytest

from kernel.anti_dory.b8_magna_classifier import (
    MAGNA_TRIGGERS,
    ActionClassification,
    ActionLevel,
    classify_action,
)


class TestMagnaTriggersDirect:
    """Tests para coincidencia directa con MAGNA_TRIGGERS."""

    @pytest.mark.parametrize("action_type", [
        "merge_to_main",
        "push_to_main",
        "supabase_write_production",
        "deploy_production",
        "modify_credentials",
        "rotate_secrets",
        "declare_dory_dead",
        "approve_r1",
        "phase_1_action",
        "sign_dsc",
        "create_pr",
        "delete_table",
        "drop_migration",
        "override_guardian",
        "disable_rls",
        "expose_private_key",
    ])
    def test_direct_trigger_returns_magna(self, action_type: str):
        result = classify_action(action_type, f"Testing {action_type}")
        assert result.level == ActionLevel.MAGNA
        assert result.requires_t1 is True
        assert "MAGNA_TRIGGERS" in result.reason

    def test_all_triggers_covered(self):
        """Verifica que el parametrize cubre todos los triggers."""
        assert len(MAGNA_TRIGGERS) == 16


class TestDangerKeywords:
    """Tests para coincidencia parcial con keywords peligrosas."""

    @pytest.mark.parametrize("action_type,keyword", [
        ("write_to_main_branch", "main"),
        ("deploy_to_production_server", "production"),
        ("update_credential_store", "credential"),
        ("read_secret_vault", "secret"),
        ("set_dory_dead_flag", "dory_dead"),
        ("enter_phase_1_mode", "phase_1"),
        ("leak_private_key_to_log", "private_key"),
    ])
    def test_partial_keyword_returns_magna(self, action_type: str, keyword: str):
        result = classify_action(action_type, f"Testing partial: {action_type}")
        assert result.level == ActionLevel.MAGNA
        assert result.requires_t1 is True
        assert keyword in result.reason


class TestMetadataOverride:
    """Tests para metadata force_magna."""

    def test_force_magna_true(self):
        result = classify_action(
            "harmless_read",
            "A read action forced to magna",
            metadata={"force_magna": True},
        )
        assert result.level == ActionLevel.MAGNA
        assert result.requires_t1 is True
        assert "force_magna" in result.reason

    def test_force_magna_false_does_not_override(self):
        result = classify_action(
            "harmless_read",
            "A read action not forced",
            metadata={"force_magna": False},
        )
        assert result.level == ActionLevel.STANDARD
        assert result.requires_t1 is False


class TestStandardActions:
    """Tests para acciones que NO son MAGNA."""

    @pytest.mark.parametrize("action_type", [
        "read_memory",
        "list_endpoints",
        "run_local_test",
        "write_bridge_file",
        "create_branch",
        "commit_to_feature_branch",
        "query_catastro",
        "generate_report",
        "classify_intent",
        "health_check",
    ])
    def test_standard_actions(self, action_type: str):
        result = classify_action(action_type, f"Testing standard: {action_type}")
        assert result.level == ActionLevel.STANDARD
        assert result.requires_t1 is False
        assert "No MAGNA triggers matched" in result.reason


class TestEdgeCases:
    """Tests para casos borde."""

    def test_case_insensitive(self):
        result = classify_action("MERGE_TO_MAIN", "Uppercase trigger")
        assert result.level == ActionLevel.MAGNA

    def test_whitespace_stripped(self):
        result = classify_action("  merge_to_main  ", "Whitespace trigger")
        assert result.level == ActionLevel.MAGNA

    def test_empty_action_type(self):
        result = classify_action("", "Empty action")
        assert result.level == ActionLevel.STANDARD

    def test_none_metadata(self):
        result = classify_action("merge_to_main", "No metadata", metadata=None)
        assert result.level == ActionLevel.MAGNA

    def test_classification_dataclass_fields(self):
        result = classify_action("read_memory", "Test fields")
        assert isinstance(result, ActionClassification)
        assert result.action_description == "Test fields"
