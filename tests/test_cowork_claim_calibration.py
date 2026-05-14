"""tests/test_cowork_claim_calibration.py — Sprint COWORK-MEMENTO-001 T5

Cubre las 16 pruebas binarias del spec §4 T5:

TestClaimExtractor:
  - test_extract_file_path
  - test_extract_table_name
  - test_extract_migration_number
  - test_extract_pr_number
  - test_extract_commit_hash
  - test_extract_branch_name
  - test_dedupe_same_claim
  - test_no_false_positive_on_prose

TestClaimLogger:
  - test_log_claim_inserts
  - test_log_batch_atomic
  - test_aggregate_daily_grouping
  - test_aggregate_filter_by_type

TestVerificationStatusInference:
  - test_verified_pre_explicit_register
  - test_verified_post_match_string_in_history
  - test_verified_post_mismatch_string_changed
  - test_unverified_no_tool_call

Adicionales (cobertura defensiva):
  - TestClaimRecord.test_to_db_row_shape
  - TestCLIReport.test_sandbox_fallback_empty
"""
from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from uuid import uuid4

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from kernel.cowork_runtime.claim_calibration import (  # noqa: E402
    ClaimCandidate,
    ClaimExtractor,
    ClaimLogger,
    ClaimRecord,
    ClaimType,
    VerificationStatus,
    infer_verification_status,
)


# ============================================================================
# Mocks
# ============================================================================

class _MockSupabaseClient:
    """Cliente Supabase mock para tests — captura inserts en lista interna."""

    def __init__(self) -> None:
        self.inserts: list[dict] = []
        self.batch_inserts: list[list[dict]] = []
        self.last_aggregate_query: dict | None = None
        self._aggregate_rows: list[dict] = []

    def set_aggregate_rows(self, rows: list[dict]) -> None:
        self._aggregate_rows = rows

    def insert(self, table: str, row: dict) -> None:
        self.inserts.append({"table": table, "row": row})

    def insert_batch(self, table: str, rows: list[dict]) -> None:
        self.batch_inserts.append({"table": table, "rows": rows})

    def aggregate_claims(self, days: int, claim_type: str | None = None):
        self.last_aggregate_query = {"days": days, "claim_type": claim_type}
        if claim_type:
            return [r for r in self._aggregate_rows if r.get("claim_type") == claim_type]
        return list(self._aggregate_rows)


# ============================================================================
# TestClaimExtractor
# ============================================================================

class TestClaimExtractor:
    def setup_method(self) -> None:
        self.extractor = ClaimExtractor()

    def test_extract_file_path(self) -> None:
        text = "Modificamos kernel/cowork_runtime/claim_calibration.py y tools/cowork_calibration_report.py"
        candidates = self.extractor.extract_claims(text)
        paths = [c.claim_value for c in candidates if c.claim_type == ClaimType.FILE_PATH]
        assert "kernel/cowork_runtime/claim_calibration.py" in paths
        assert "tools/cowork_calibration_report.py" in paths

    def test_extract_table_name(self) -> None:
        text = "SELECT * FROM cowork_claims_calibration WHERE id IS NOT NULL"
        candidates = self.extractor.extract_claims(text)
        tables = [c.claim_value for c in candidates if c.claim_type == ClaimType.TABLE_NAME]
        assert "cowork_claims_calibration" in tables

    def test_extract_migration_number(self) -> None:
        text = "Aplicamos migrations/sql/0033_cowork_claims_calibration.sql en prod"
        candidates = self.extractor.extract_claims(text)
        migs = [c.claim_value for c in candidates if c.claim_type == ClaimType.MIGRATION_NUMBER]
        assert "0033" in migs

    def test_extract_pr_number(self) -> None:
        text = "Cerré PR #117 y abrimos PR #126 también"
        candidates = self.extractor.extract_claims(text)
        prs = [c.claim_value for c in candidates if c.claim_type == ClaimType.PR_NUMBER]
        assert "117" in prs
        assert "126" in prs

    def test_extract_commit_hash(self) -> None:
        text = "Sobre commit d95a7253 después del merge"
        candidates = self.extractor.extract_claims(text)
        hashes = [c.claim_value for c in candidates if c.claim_type == ClaimType.COMMIT_HASH]
        assert any(h.startswith("d95a725") for h in hashes)

    def test_extract_branch_name(self) -> None:
        text = "Sobre feat/cowork-memento-001 + fix/anti-rotation-loop ya pusheada"
        candidates = self.extractor.extract_claims(text)
        branches = [c.claim_value for c in candidates if c.claim_type == ClaimType.BRANCH_NAME]
        assert "feat/cowork-memento-001" in branches
        assert "fix/anti-rotation-loop" in branches

    def test_dedupe_same_claim(self) -> None:
        text = "PR #117 mergeado. Tests sobre PR #117 verde. PR #117 sin conflicts."
        candidates = self.extractor.extract_claims(text)
        prs = [c.claim_value for c in candidates if c.claim_type == ClaimType.PR_NUMBER]
        # 3 menciones del mismo PR pero solo 1 entry
        assert prs.count("117") == 1

    def test_no_false_positive_on_prose(self) -> None:
        text = "Hoy es un buen día para escribir documentación clara y precisa."
        candidates = self.extractor.extract_claims(text)
        # Solo se permiten claims muy específicos en prosa — no debería capturar nada
        file_paths = [c for c in candidates if c.claim_type == ClaimType.FILE_PATH]
        tables = [c for c in candidates if c.claim_type == ClaimType.TABLE_NAME]
        prs = [c for c in candidates if c.claim_type == ClaimType.PR_NUMBER]
        assert file_paths == []
        assert tables == []
        assert prs == []


# ============================================================================
# TestClaimLogger
# ============================================================================

class TestClaimLogger:
    def setup_method(self) -> None:
        self.client = _MockSupabaseClient()
        self.session_id = uuid4()
        self.logger = ClaimLogger(self.client, session_id=self.session_id)

    def _make_record(self, claim_type: ClaimType, value: str) -> ClaimRecord:
        return ClaimRecord(
            claim_type=claim_type,
            claim_value=value,
            verification_status=VerificationStatus.UNVERIFIED,
            turn_index=1,
        )

    def test_log_claim_inserts(self) -> None:
        rec = self._make_record(ClaimType.PR_NUMBER, "117")
        ok = self.logger.log_claim(rec)
        assert ok is True
        assert self.logger.insert_count == 1
        assert len(self.client.inserts) == 1
        row = self.client.inserts[0]["row"]
        assert row["claim_type"] == "pr_number"
        assert row["claim_value"] == "117"
        assert row["session_uuid"] == str(self.session_id)

    def test_log_batch_atomic(self) -> None:
        records = [
            self._make_record(ClaimType.PR_NUMBER, "117"),
            self._make_record(ClaimType.MIGRATION_NUMBER, "0033"),
            self._make_record(ClaimType.FILE_PATH, "kernel/cowork_runtime/claim_calibration.py"),
        ]
        ok_count = self.logger.log_batch(records)
        assert ok_count == 3
        assert self.logger.insert_count == 3
        assert len(self.client.batch_inserts) == 1
        assert len(self.client.batch_inserts[0]["rows"]) == 3

    def test_aggregate_daily_grouping(self) -> None:
        self.client.set_aggregate_rows([
            {"claim_type": "file_path", "verification_status": "verified_post_match", "n": 5},
            {"claim_type": "file_path", "verification_status": "unverified", "n": 2},
            {"claim_type": "pr_number", "verification_status": "verified_post_match", "n": 3},
        ])
        result = self.logger.aggregate_daily(days=7)
        assert result["days"] == 7
        assert result["total_claims"] == 10
        assert result["by_type"]["file_path"]["verified_post_match"] == 5
        assert result["by_type"]["file_path"]["unverified"] == 2
        assert result["by_type"]["pr_number"]["verified_post_match"] == 3
        assert result["f21_rate"] == 0.2  # 2 unverified / 10 total

    def test_aggregate_filter_by_type(self) -> None:
        self.client.set_aggregate_rows([
            {"claim_type": "file_path", "verification_status": "unverified", "n": 4},
            {"claim_type": "pr_number", "verification_status": "verified_pre", "n": 6},
        ])
        result = self.logger.aggregate_daily(days=1, claim_type="file_path")
        assert "file_path" in result["by_type"]
        assert "pr_number" not in result["by_type"]
        assert result["total_claims"] == 4
        assert self.client.last_aggregate_query == {"days": 1, "claim_type": "file_path"}


# ============================================================================
# TestVerificationStatusInference
# ============================================================================

class TestVerificationStatusInference:
    def _cand(self, claim_type: ClaimType, value: str) -> ClaimCandidate:
        return ClaimCandidate(
            claim_type=claim_type,
            claim_value=value,
            detected_in_output="...snippet...",
            extraction_regex_id="test_regex",
        )

    def test_verified_pre_explicit_register(self) -> None:
        cand = self._cand(ClaimType.PR_NUMBER, "117")
        status, evidence = infer_verification_status(
            cand,
            tool_call_history=[],
            pre_registered_claims=["117", "118"],
        )
        assert status == VerificationStatus.VERIFIED_PRE
        assert evidence is not None
        assert "117" in evidence

    def test_verified_post_match_string_in_history(self) -> None:
        cand = self._cand(ClaimType.MIGRATION_NUMBER, "0033")
        status, evidence = infer_verification_status(
            cand,
            tool_call_history=[
                "ls migrations/sql/ output: 0030_thread_snapshots.sql 0031_project_runtime_heads.sql 0032_anti_dory_rpcs.sql"
                " 0033_cowork_claims_calibration.sql",
            ],
            pre_registered_claims=None,
        )
        assert status == VerificationStatus.VERIFIED_POST_MATCH
        assert evidence is not None

    def test_verified_post_mismatch_string_changed(self) -> None:
        cand = self._cand(ClaimType.MIGRATION_NUMBER, "0099")
        status, evidence = infer_verification_status(
            cand,
            tool_call_history=[
                "ls migrations/sql/ output: 0033_cowork_claims_calibration.sql"
            ],
            pre_registered_claims=None,
        )
        # claim_value="0099" no aparece en history, pero ".sql" sí → post_mismatch
        assert status == VerificationStatus.VERIFIED_POST_MISMATCH

    def test_unverified_no_tool_call(self) -> None:
        cand = self._cand(ClaimType.COMMIT_HASH, "deadbeef1234")
        status, evidence = infer_verification_status(
            cand,
            tool_call_history=[],
            pre_registered_claims=None,
        )
        assert status == VerificationStatus.UNVERIFIED
        assert evidence is None


# ============================================================================
# TestClaimRecord (cobertura defensiva)
# ============================================================================

class TestClaimRecord:
    def test_to_db_row_shape(self) -> None:
        session_id = uuid4()
        rec = ClaimRecord(
            claim_type=ClaimType.PR_NUMBER,
            claim_value="117",
            verification_status=VerificationStatus.VERIFIED_POST_MATCH,
            turn_index=42,
            detected_in_output="...PR #117 merged...",
            extraction_regex_id="regex_pr_number_v1",
            tool_call_evidence="gh pr view 117",
            session_uuid=session_id,
            metadata={"source": "test"},
        )
        row = rec.to_db_row()
        assert row["session_uuid"] == str(session_id)
        assert row["turn_index"] == 42
        assert row["claim_type"] == "pr_number"
        assert row["claim_value"] == "117"
        assert row["verification_status"] == "verified_post_match"
        assert row["tool_call_evidence"] == "gh pr view 117"
        assert row["extraction_regex_id"] == "regex_pr_number_v1"
        assert row["metadata"] == {"source": "test"}


# ============================================================================
# TestCLIReport (cobertura defensiva sobre tools/cowork_calibration_report.py)
# ============================================================================

class TestCLIReport:
    def test_sandbox_fallback_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """En sandbox sin Supabase env vars, el CLI debe retornar JSON con mode=sandbox."""
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

        from tools.cowork_calibration_report import build_report

        report = build_report(days=7, claim_type=None)
        assert report["mode"] == "sandbox"
        assert report["total_claims"] == 0
        assert report["days"] == 7
        assert report["by_type"] == {}
        assert report["f21_rate"] == 0.0
