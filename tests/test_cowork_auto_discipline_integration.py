"""
tests/test_cowork_auto_discipline_integration.py — Sprint COWORK-AUTO-DISCIPLINE-REAL-001 T6

Tests integration end-to-end del enforcement runtime auto-discipline Cowork.

Cubre:
- F21 pattern detector P1-P10 (10 patterns canónicos)
- Verbatim citation enforcement (hex hashes, paths, schemas, timestamps)
- Hook integration: shadow vs enabled, history tracking, audit log row preparation
- F23-F27 antipatterns module accessible
- Re-export F1-F22 desde rule_reinjection (no broken)
- Graceful degradation cuando módulos nuevos faltan
- Backward compatibility: intercept() signature pre/post sprint unchanged

Run:
    pytest tests/test_cowork_auto_discipline_integration.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Asegurar import desde repo root
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from kernel.cowork_runtime.f21_patterns import (
    F21_PATTERNS,
    F21_PATTERNS_VERSION,
    all_pattern_ids,
    get_pattern_by_id,
    output_parece_audit,
)
from kernel.cowork_runtime.pre_response_hook import CoworkPreResponseHook
from tools._check_cowork_verbatim_citations import check_verbatim_citations
from tools.check_cowork_no_speculative_claims import check_speculative_claims

# ============================================================================
# F21_PATTERNS CATALOG
# ============================================================================


class TestF21PatternsCatalog:
    """Catálogo F21_PATTERNS canónico — 10 patterns P1-P10."""

    def test_catalog_has_10_patterns(self):
        assert len(F21_PATTERNS) == 10, f"Spec firmado §2.1 exige 10 patterns P1-P10. Found {len(F21_PATTERNS)}."

    def test_version_string(self):
        assert F21_PATTERNS_VERSION == "1.0.0"

    @pytest.mark.parametrize(
        "expected_id",
        [
            "diff_stats",
            "db_schema",
            "model_versions",
            "commit_hashes",
            "git_state",
            "pr_existence",
            "migration_filename",
            "branch_overlap",
            "test_count",
            "rls_policy",
        ],
    )
    def test_pattern_id_present(self, expected_id):
        assert expected_id in all_pattern_ids(), f"Pattern id {expected_id} ausente del catálogo canónico."

    def test_all_patterns_have_required_fields(self):
        required = {"id", "regex", "description", "requires_tool_call", "severity"}
        for p in F21_PATTERNS:
            missing = required - set(p.keys())
            assert not missing, f"Pattern {p.get('id')} missing fields: {missing}"

    def test_severity_values_valid(self):
        valid_severities = {"P0", "P1", "P2"}
        for p in F21_PATTERNS:
            assert p["severity"] in valid_severities, f"Pattern {p['id']} severity inválido: {p['severity']}"

    def test_get_pattern_by_id(self):
        assert get_pattern_by_id("diff_stats") is not None
        assert get_pattern_by_id("nonexistent") is None


# ============================================================================
# F21 PATTERN DETECTOR
# ============================================================================


class TestF21PatternDetector:
    """tools/check_cowork_no_speculative_claims.py — detector runtime."""

    def test_diff_stats_blocked_without_tool_call(self):
        output = "El PR tiene 11 files changed, +1879/-0 según diff binario."
        violations = check_speculative_claims(output, history=[])
        assert any(v["pattern_id"] == "diff_stats" for v in violations)

    def test_diff_stats_passes_with_git_diff_in_history(self):
        output = "El PR tiene 11 files changed, +1879/-0 según diff binario."
        history = [{"type": "tool_call", "name": "git diff --stat", "result": "..."}]
        violations = check_speculative_claims(output, history=history)
        assert not any(v["pattern_id"] == "diff_stats" for v in violations)

    def test_commit_hashes_blocked_without_git_log(self):
        output = "El commit abc1234def5678 mergea a main."
        violations = check_speculative_claims(output, history=[])
        assert any(v["pattern_id"] == "commit_hashes" for v in violations)

    def test_commit_hashes_passes_with_gh_pr_view(self):
        output = "El commit abc1234def5678 mergea a main."
        history = [{"name": "gh pr view 98", "result": "commit abc1234def5678"}]
        violations = check_speculative_claims(output, history=history)
        assert not any(v["pattern_id"] == "commit_hashes" for v in violations)

    def test_pr_existence_blocked_without_gh_pr_view(self):
        output = "PR #98 ya existe y está abierto en main."
        violations = check_speculative_claims(output, history=[])
        assert any(v["pattern_id"] == "pr_existence" for v in violations)

    def test_migration_filename_detected(self):
        output = "Modifica migrations/sql/0031_foo.sql al final."
        violations = check_speculative_claims(output, history=[])
        # El detector debe trigger porque no hubo ls migrations/sql
        # (puede que matchee migration_filename O file_path; verificamos al menos uno)
        pattern_ids = {v["pattern_id"] for v in violations}
        assert "migration_filename" in pattern_ids

    def test_test_count_blocked_without_pytest(self):
        output = "Verde 27/27 tests passed."
        violations = check_speculative_claims(output, history=[])
        assert any(v["pattern_id"] == "test_count" for v in violations)

    def test_test_count_passes_with_pytest_in_history(self):
        output = "Verde 27/27 tests passed."
        history = [{"name": "pytest tests/test_foo.py", "result": "27 passed"}]
        violations = check_speculative_claims(output, history=history)
        assert not any(v["pattern_id"] == "test_count" for v in violations)

    def test_rls_policy_only_in_audit_outputs(self):
        # Output que no parece audit → pattern rls_policy NO se aplica
        output_chat = "voy a habilitar RLS habilitada en la nueva tabla."
        violations = check_speculative_claims(output_chat, history=[])
        # No debe trigger porque output no parece audit
        assert not any(v["pattern_id"] == "rls_policy" for v in violations)

        # Output que parece audit (contains "verificación binaria")
        output_audit = "Verificación binaria: RLS habilitada en public.foo_table."
        violations_audit = check_speculative_claims(output_audit, history=[])
        assert any(v["pattern_id"] == "rls_policy" for v in violations_audit)

    def test_violations_have_complete_shape(self):
        output = "11 files changed, +1879/-0"
        violations = check_speculative_claims(output, history=[])
        assert violations
        v = violations[0]
        assert "pattern_id" in v
        assert "match" in v
        assert "missing_tool_call" in v
        assert "severity" in v
        assert "match_start" in v
        assert "match_end" in v


# ============================================================================
# VERBATIM CITATIONS
# ============================================================================


class TestVerbatimCitations:
    """tools/_check_cowork_verbatim_citations.py — citation enforcement."""

    def test_hex_hash_without_history_blocks(self):
        output = "El commit deadbeefcafe123 está mergeado."
        violations = check_verbatim_citations(output, history=[])
        assert any(v["type"] == "hex_hash" for v in violations)

    def test_hex_hash_with_verbatim_in_history_passes(self):
        output = "El commit deadbeefcafe123 está mergeado."
        history = [{"content": "commit deadbeefcafe123 by alfredogl"}]
        violations = check_verbatim_citations(output, history=history)
        assert not any(v["type"] == "hex_hash" for v in violations)

    def test_iso_timestamp_detected(self):
        output = "issuecomment-4432323670 posteado a las 2026-05-12T15:50:18Z."
        violations = check_verbatim_citations(output, history=[])
        types = {v["type"] for v in violations}
        assert "iso_timestamp" in types
        assert "issuecomment" in types

    def test_allowlist_main_branch_ignored(self):
        # "main" no se considera citation fabricable
        output = "branch main está actualizada."
        violations = check_verbatim_citations(output, history=[])
        assert not any(v["citation"] == "main" for v in violations)

    def test_file_path_with_extension_detected(self):
        output = "El archivo migrations/sql/9999_inexistente.sql no existe."
        violations = check_verbatim_citations(output, history=[])
        # Allowlist contiene "migrations/sql" así que se filtra
        # Verificamos al menos que no levante excepciones
        assert isinstance(violations, list)

    def test_dedupe_same_citation(self):
        output = "commit abc1234 vio commit abc1234 dos veces."
        violations = check_verbatim_citations(output, history=[])
        # Debe haber 1 sola violation pese a 2 menciones
        hex_violations = [v for v in violations if v["citation"] == "abc1234"]
        assert len(hex_violations) == 1


# ============================================================================
# HOOK INTEGRATION
# ============================================================================


class TestHookIntegration:
    """CoworkPreResponseHook con auto-discipline T4 integrado."""

    def test_hook_init_has_session_uuid(self):
        hook = CoworkPreResponseHook(enabled=False)
        assert hook.session_uuid
        assert hook.turn_index == 0
        assert hook.history == []
        assert hook.auto_discipline_shadow_count == 0

    def test_session_uuid_custom(self):
        custom_uuid = "11111111-2222-3333-4444-555555555555"
        hook = CoworkPreResponseHook(enabled=False, session_uuid=custom_uuid)
        assert hook.session_uuid == custom_uuid

    def test_intercept_increments_turn(self):
        hook = CoworkPreResponseHook(enabled=False)
        hook.intercept("output trivial sin claims", user_message="hola")
        assert hook.turn_index == 1
        hook.intercept("otro output", user_message="seguimos")
        assert hook.turn_index == 2

    def test_intercept_creates_invocation_record(self):
        hook = CoworkPreResponseHook(enabled=False)
        hook.intercept("trivial sin claims", user_message="ya")
        rec = hook.last_invocation_record
        assert rec is not None
        assert rec["session_uuid"] == hook.session_uuid
        assert rec["turn_index"] == 1
        assert rec["decision_magnitude"] in ("trivial", "medium", "magna")
        assert rec["output_passed"] is True
        assert rec["violations_detected"] == []

    def test_intercept_detects_violations_shadow_mode(self):
        hook = CoworkPreResponseHook(enabled=False)
        output = "PR #98 tiene 11 files changed, +1879/-0 y commit abc1234 mergea."
        ok, _ = hook.intercept(output, user_message="ya")
        # Shadow: pasa pero registra
        assert ok is True
        rec = hook.last_invocation_record
        assert rec is not None
        assert len(rec["violations_detected"]) > 0
        assert hook.auto_discipline_shadow_count == 1

    def test_register_tool_call_prevents_false_positive(self):
        hook = CoworkPreResponseHook(enabled=False)
        hook.register_tool_call(name="gh pr view 98", result="11 files +1879/-0")
        hook.register_tool_call(name="git log abc1234", result="commit abc1234")
        output = "PR #98 tiene 11 files changed, +1879/-0 según gh pr view."
        hook.intercept(output, user_message="ya")
        rec = hook.last_invocation_record
        # Con tool calls registrados, no debe haber F21 violations de diff_stats
        f21_ids = {v.get("pattern_id") for v in rec["violations_detected"] if v.get("detector") == "f21_patterns"}
        assert "diff_stats" not in f21_ids

    def test_history_capped_at_max(self):
        hook = CoworkPreResponseHook(enabled=False)
        hook.history_max = 3
        for i in range(10):
            hook.register_tool_call(name=f"tool_{i}", result=f"res_{i}")
        assert len(hook.history) == 3
        # Los últimos 3 son los que persisten
        assert hook.history[-1]["name"] == "tool_9"

    def test_session_health_exposes_auto_discipline(self):
        hook = CoworkPreResponseHook(enabled=False)
        h = hook.session_health()
        assert "session_uuid" in h
        assert "turn_index" in h
        assert "auto_discipline_enabled" in h
        assert "auto_discipline_shadow_count" in h
        assert "f21_patterns_version" in h
        assert "auto_discipline_available" in h
        assert h["auto_discipline_available"] is True

    def test_intercept_signature_backward_compat(self):
        """intercept(cowork_output, user_message='') sigue funcionando idéntico."""
        hook = CoworkPreResponseHook(enabled=False)
        result = hook.intercept("output simple")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)


# ============================================================================
# ANTIPATTERNS MODULE F23-F27
# ============================================================================


class TestAntipatternsModule:
    """kernel/cowork_runtime/antipatterns.py — F23-F27 + re-export F1-F22."""

    def test_module_imports(self):
        from kernel.cowork_runtime.antipatterns import (
            ALL_ANTIPATTERN_IDS,
            ANTIPATTERNS_VERSION,
            HISTORICAL_ANTIPATTERN_IDS,
            NEW_ANTIPATTERNS,
        )

        assert ANTIPATTERNS_VERSION == "1.0.0"
        assert len(NEW_ANTIPATTERNS) == 5
        assert len(HISTORICAL_ANTIPATTERN_IDS) == 22
        assert len(ALL_ANTIPATTERN_IDS) == 27

    @pytest.mark.parametrize("ap_id", ["F23", "F24", "F25", "F26", "F27"])
    def test_new_antipatterns_present(self, ap_id):
        from kernel.cowork_runtime.antipatterns import get_antipattern_by_id

        ap = get_antipattern_by_id(ap_id)
        assert ap is not None
        assert ap["id"] == ap_id
        assert "name" in ap
        assert "description" in ap
        assert "severity" in ap
        assert ap["severity"] in ("P0", "P1", "P2")

    def test_historical_f1_f22_referenced(self):
        from kernel.cowork_runtime.antipatterns import HISTORICAL_ANTIPATTERN_IDS

        for i in range(1, 23):
            assert f"F{i}" in HISTORICAL_ANTIPATTERN_IDS

    def test_get_canonical_hard_rules_returns_string(self):
        """Re-export F1-F22 desde rule_reinjection no debe romperse."""
        from kernel.cowork_runtime.antipatterns import get_canonical_hard_rules

        rules = get_canonical_hard_rules()
        assert isinstance(rules, str)
        # rules debe contener al menos algún F-pattern reference
        assert any(f"F{i}" in rules for i in range(1, 23))


# ============================================================================
# HEURISTICA AUDIT vs CHAT
# ============================================================================


class TestAuditHeuristic:
    """output_parece_audit — heurística para patterns only_in_audit_outputs."""

    def test_chat_output_no_audit(self):
        assert output_parece_audit("hola alfredo, mergeé el PR") is False

    def test_audit_keywords_trigger(self):
        assert output_parece_audit("Verificación binaria: PR mergeado OK") is True
        assert output_parece_audit("Audit completado, reportar a Cowork") is True
        assert output_parece_audit("post-merge smoke test verde") is True
