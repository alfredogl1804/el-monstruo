"""
Tests Sprint Memento Bloque 6 — ContaminationDetector
=====================================================

Cubre:
- H1: credential_hash obsoleto detectable en git history
- H2: host divergente con histórico de validaciones
- H3: operación sin pre-flight reciente
- Caso real del incidente TiDB 2026-05-04 (gateway01 fantasma vs gateway05 real)
- Falsos positivos evitados (cambio legítimo, hilo nuevo, etc.)
- Timeouts global y per-rule
- Skipped rules cuando faltan dependencias

Disciplina anti-Dory: mocks aislados, no asume estado del repo real,
usa fixtures temporales con git init para H1.
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock

import pytest

from kernel.memento.contamination_detector import (
    ContaminationDetector,
    ContaminationFinding,
    ContaminationReport,
)


# ===========================================================================
# Fixtures — Mock DB y repo git temporal
# ===========================================================================


class MockDB:
    """Mock simple del cliente Supabase async usado por el detector."""

    def __init__(self, rows_by_filter: Optional[List[Dict[str, Any]]] = None):
        self._rows = rows_by_filter or []
        self.calls: List[Dict[str, Any]] = []

    async def select(
        self,
        table: str,
        *,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        filters_gte: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        self.calls.append(
            {
                "table": table,
                "filters": filters or {},
                "order_by": order_by,
                "limit": limit,
                "filters_gte": filters_gte,
            }
        )
        # Filtrado mínimo: por hilo_id, operation, validation_status si están
        result = self._rows
        if filters:
            for key, value in filters.items():
                result = [r for r in result if r.get(key) == value]
        if filters_gte:
            for key, value in filters_gte.items():
                result = [r for r in result if (r.get(key) or "") >= value]
        if limit:
            result = result[:limit]
        return result


@pytest.fixture
def temp_git_repo(tmp_path):
    """Repo git temporal con un commit que contiene un hash conocido."""
    repo = tmp_path / "repo"
    repo.mkdir()

    def run(cmd):
        subprocess.run(cmd, cwd=repo, check=True, capture_output=True)

    run(["git", "init", "-q"])
    run(["git", "config", "user.email", "test@test.local"])
    run(["git", "config", "user.name", "Test"])

    # Commit con un hash conocido en el mensaje (simula credential rotation log)
    file = repo / "credentials_log.md"
    file.write_text("Old credential hash: deadbeef12345678 rotated 2025-12-01\n")
    run(["git", "add", "credentials_log.md"])
    run(["git", "commit", "-q", "-m", "rotate credential deadbeef12345678 to xxx"])

    return str(repo)


# ===========================================================================
# H1 — credential_hash obsoleto
# ===========================================================================


class TestH1CredentialHashObsolete:
    """H1 detecta credential_hash declarado que existió en commits previos."""

    @pytest.mark.asyncio
    async def test_h1_detects_obsolete_hash_in_git_history(self, temp_git_repo):
        """Hash declarado existe en commit previo pero no es la fuente actual → HIGH."""
        detector = ContaminationDetector(repo_root=temp_git_repo)
        report = await detector.detect(
            hilo_id="hilo_test",
            operation="sql_against_production",
            context_used={"credential_hash_first_8": "deadbeef"},
            current_source_of_truth={"credential_hash_first_8": "fa11abce"},
        )
        h1_findings = [f for f in report.findings if f.rule_id == "H1"]
        assert len(h1_findings) == 1
        assert h1_findings[0].severity == "HIGH"
        assert h1_findings[0].evidence["context_hash"] == "deadbeef"
        assert h1_findings[0].evidence["current_source_of_truth_hash"] == "fa11abce"
        assert h1_findings[0].evidence["matching_commits_count"] >= 1

    @pytest.mark.asyncio
    async def test_h1_no_finding_when_hashes_match(self, temp_git_repo):
        """Si ctx_hash == sot_hash, no dispara."""
        detector = ContaminationDetector(repo_root=temp_git_repo)
        report = await detector.detect(
            hilo_id="hilo_test",
            operation="sql_against_production",
            context_used={"credential_hash_first_8": "deadbeef"},
            current_source_of_truth={"credential_hash_first_8": "deadbeef"},
        )
        assert not [f for f in report.findings if f.rule_id == "H1"]

    @pytest.mark.asyncio
    async def test_h1_no_finding_when_hash_not_in_history(self, temp_git_repo):
        """Si el hash declarado nunca existió en el repo, no dispara (no es legacy)."""
        detector = ContaminationDetector(repo_root=temp_git_repo)
        report = await detector.detect(
            hilo_id="hilo_test",
            operation="sql_against_production",
            context_used={"credential_hash_first_8": "ffffffff"},
            current_source_of_truth={"credential_hash_first_8": "fa11abce"},
        )
        assert not [f for f in report.findings if f.rule_id == "H1"]

    @pytest.mark.asyncio
    async def test_h1_skipped_when_no_source_of_truth_provided(self):
        """Si no se pasa current_source_of_truth, H1 queda en skipped_rules."""
        detector = ContaminationDetector(repo_root="/nonexistent")
        report = await detector.detect(
            hilo_id="hilo_test",
            operation="sql_against_production",
            context_used={"credential_hash_first_8": "deadbeef"},
        )
        assert "H1" in report.skipped_rules
        assert not [f for f in report.findings if f.rule_id == "H1"]

    @pytest.mark.asyncio
    async def test_h1_no_finding_with_short_hash(self, temp_git_repo):
        """Hash con menos de 8 chars no se considera (anti-FP)."""
        detector = ContaminationDetector(repo_root=temp_git_repo)
        report = await detector.detect(
            hilo_id="hilo_test",
            operation="sql_against_production",
            context_used={"credential_hash_first_8": "abcd"},
            current_source_of_truth={"credential_hash_first_8": "fa11abce"},
        )
        assert not [f for f in report.findings if f.rule_id == "H1"]

    @pytest.mark.asyncio
    async def test_h1_no_finding_with_non_hex_hash(self, temp_git_repo):
        """Hash con chars no-hex no se considera (anti-FP, evita strings genéricos)."""
        detector = ContaminationDetector(repo_root=temp_git_repo)
        report = await detector.detect(
            hilo_id="hilo_test",
            operation="sql_against_production",
            context_used={"credential_hash_first_8": "myhashxx"},
            current_source_of_truth={"credential_hash_first_8": "fa11abce"},
        )
        assert not [f for f in report.findings if f.rule_id == "H1"]

    @pytest.mark.asyncio
    async def test_h1_skipped_when_repo_root_not_git(self, tmp_path):
        """Si repo_root no es un git repo, no falla (H1 queda silente)."""
        non_git_dir = tmp_path / "not_git"
        non_git_dir.mkdir()
        detector = ContaminationDetector(repo_root=str(non_git_dir))
        report = await detector.detect(
            hilo_id="hilo_test",
            operation="sql_against_production",
            context_used={"credential_hash_first_8": "deadbeef"},
            current_source_of_truth={"credential_hash_first_8": "fa11abce"},
        )
        # No finding y no excepción
        assert not [f for f in report.findings if f.rule_id == "H1"]


# ===========================================================================
# H2 — host divergente con histórico
# ===========================================================================


class TestH2HostDivergent:
    """H2 detecta cambios de host estructurales o sospechosos vs histórico."""

    @pytest.mark.asyncio
    async def test_h2_detects_structural_fqdn_change(self):
        """Cambio de cloud provider entre validaciones → HIGH."""
        previous_validation = {
            "validation_id": "mv_2026-05-04T10:00:00_aaa111",
            "context_used": {"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
            "validation_status": "ok",
            "hilo_id": "hilo_ticketlike",
            "operation": "sql_against_production",
            "ts": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
        }
        db = MockDB([previous_validation])
        detector = ContaminationDetector(db=db, repo_root="/nonexistent")
        report = await detector.detect(
            hilo_id="hilo_ticketlike",
            operation="sql_against_production",
            context_used={"host": "different.cluster.gcp.example.com"},
            current_validation_id="mv_2026-05-05T01:00:00_bbb222",
        )
        h2 = [f for f in report.findings if f.rule_id == "H2"]
        assert len(h2) == 1
        assert h2[0].severity == "HIGH"
        assert h2[0].evidence["change_type"] == "structural_fqdn"
        assert h2[0].validation_id_ref == "mv_2026-05-04T10:00:00_aaa111"

    @pytest.mark.asyncio
    async def test_h2_detects_tidb_gateway_incident_after_24h(self):
        """
        CASO REAL incidente TiDB 2026-05-04 sintetizado:
        - Última validación OK fue contra gateway01 hace 48h
        - Hoy el hilo declara gateway05
        - El cluster en realidad migró; gateway01 es fantasma
        → HIGH (numeric_in_first_segment_after_24h)
        """
        previous_validation = {
            "validation_id": "mv_2026-05-03T01:00:00_old",
            "context_used": {"host": "gateway01.us-east-1.prod.aws.tidbcloud.com"},
            "validation_status": "ok",
            "hilo_id": "hilo_ticketlike",
            "operation": "sql_against_production",
            "ts": (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat(),
        }
        db = MockDB([previous_validation])
        detector = ContaminationDetector(db=db, repo_root="/nonexistent")
        report = await detector.detect(
            hilo_id="hilo_ticketlike",
            operation="sql_against_production",
            context_used={"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
            current_validation_id="mv_2026-05-05T01:00:00_new",
        )
        h2 = [f for f in report.findings if f.rule_id == "H2"]
        assert len(h2) == 1
        assert h2[0].severity == "HIGH"
        assert h2[0].evidence["change_type"] == "numeric_in_first_segment_after_24h"
        assert h2[0].evidence["current_host"].startswith("gateway05")
        assert h2[0].evidence["previous_host"].startswith("gateway01")

    @pytest.mark.asyncio
    async def test_h2_no_finding_for_recent_numeric_change(self):
        """
        FALSO POSITIVO EVITADO: gateway01 → gateway05 dentro de 24h NO dispara.
        Es un cambio legítimo de cluster activo.
        """
        previous_validation = {
            "validation_id": "mv_aaa",
            "context_used": {"host": "gateway01.us-east-1.prod.aws.tidbcloud.com"},
            "validation_status": "ok",
            "hilo_id": "hilo_ticketlike",
            "operation": "sql_against_production",
            "ts": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
        }
        db = MockDB([previous_validation])
        detector = ContaminationDetector(db=db, repo_root="/nonexistent")
        report = await detector.detect(
            hilo_id="hilo_ticketlike",
            operation="sql_against_production",
            context_used={"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
            current_validation_id="mv_bbb",
        )
        assert not [f for f in report.findings if f.rule_id == "H2"]

    @pytest.mark.asyncio
    async def test_h2_no_finding_when_host_matches(self):
        """Mismo host → no finding."""
        previous_validation = {
            "validation_id": "mv_aaa",
            "context_used": {"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
            "validation_status": "ok",
            "hilo_id": "hilo_ticketlike",
            "operation": "sql_against_production",
            "ts": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
        }
        db = MockDB([previous_validation])
        detector = ContaminationDetector(db=db, repo_root="/nonexistent")
        report = await detector.detect(
            hilo_id="hilo_ticketlike",
            operation="sql_against_production",
            context_used={"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
            current_validation_id="mv_bbb",
        )
        assert not [f for f in report.findings if f.rule_id == "H2"]

    @pytest.mark.asyncio
    async def test_h2_no_finding_when_no_history(self):
        """Si no hay validaciones previas, no dispara (hilo nuevo)."""
        db = MockDB([])
        detector = ContaminationDetector(db=db, repo_root="/nonexistent")
        report = await detector.detect(
            hilo_id="hilo_nuevo",
            operation="sql_against_production",
            context_used={"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
            current_validation_id="mv_first",
        )
        assert not [f for f in report.findings if f.rule_id == "H2"]

    @pytest.mark.asyncio
    async def test_h2_skipped_without_db(self):
        """Sin db → H2 en skipped_rules."""
        detector = ContaminationDetector(db=None, repo_root="/nonexistent")
        report = await detector.detect(
            hilo_id="hilo_test",
            operation="sql_against_production",
            context_used={"host": "anyhost.com"},
        )
        assert "H2" in report.skipped_rules

    @pytest.mark.asyncio
    async def test_h2_no_finding_when_no_host_in_context(self):
        """Sin `host` en context_used → no aplica."""
        db = MockDB([{"validation_id": "x", "context_used": {"host": "x.com"}, "ts": "2026-01-01T00:00:00+00:00"}])
        detector = ContaminationDetector(db=db, repo_root="/nonexistent")
        report = await detector.detect(
            hilo_id="hilo_test",
            operation="some_op",
            context_used={"foo": "bar"},  # sin host
        )
        assert not [f for f in report.findings if f.rule_id == "H2"]


# ===========================================================================
# H3 — operación sin pre-flight reciente
# ===========================================================================


class TestH3NoRecentPreflight:
    """H3 informativo: hilo activo sin validar esta operation en la ventana."""

    @pytest.mark.asyncio
    async def test_h3_triggers_when_active_hilo_without_recent_op_validation(self):
        """5+ validaciones recientes pero ninguna para esta op → MEDIUM."""
        now = datetime.now(timezone.utc)
        recent_rows = [
            {
                "validation_id": f"mv_other_{i}",
                "operation": "other_operation",
                "hilo_id": "hilo_active",
                "ts": (now - timedelta(minutes=i * 5)).isoformat(),
            }
            for i in range(6)
        ]
        db = MockDB(recent_rows)
        detector = ContaminationDetector(db=db, repo_root="/nonexistent")
        report = await detector.detect(
            hilo_id="hilo_active",
            operation="critical_op_never_validated",
            context_used={"foo": "bar"},
            current_validation_id="mv_now",
        )
        h3 = [f for f in report.findings if f.rule_id == "H3"]
        assert len(h3) == 1
        assert h3[0].severity == "MEDIUM"
        assert h3[0].evidence["recent_validations_total"] >= 5

    @pytest.mark.asyncio
    async def test_h3_no_finding_when_recent_validation_for_same_op_exists(self):
        """Si hay validación reciente para la misma op → no dispara."""
        now = datetime.now(timezone.utc)
        rows = [
            {
                "validation_id": "mv_old",
                "operation": "critical_op",
                "hilo_id": "hilo_test",
                "ts": (now - timedelta(minutes=10)).isoformat(),
            },
            {
                "validation_id": "mv_other",
                "operation": "other_op",
                "hilo_id": "hilo_test",
                "ts": (now - timedelta(minutes=5)).isoformat(),
            },
        ] * 3  # 6 rows total, 3 con la misma op
        db = MockDB(rows)
        detector = ContaminationDetector(db=db, repo_root="/nonexistent")
        report = await detector.detect(
            hilo_id="hilo_test",
            operation="critical_op",
            context_used={"foo": "bar"},
            current_validation_id="mv_now",
        )
        assert not [f for f in report.findings if f.rule_id == "H3"]

    @pytest.mark.asyncio
    async def test_h3_no_finding_for_new_hilo_with_few_validations(self):
        """Hilo nuevo con < 5 validaciones recientes → no dispara (anti-FP)."""
        now = datetime.now(timezone.utc)
        rows = [
            {"validation_id": f"mv_{i}", "operation": "other", "hilo_id": "hilo_nuevo", "ts": (now - timedelta(minutes=i)).isoformat()}
            for i in range(2)
        ]
        db = MockDB(rows)
        detector = ContaminationDetector(db=db, repo_root="/nonexistent")
        report = await detector.detect(
            hilo_id="hilo_nuevo",
            operation="critical_op",
            context_used={"foo": "bar"},
            current_validation_id="mv_now",
        )
        assert not [f for f in report.findings if f.rule_id == "H3"]


# ===========================================================================
# Detector — comportamiento global
# ===========================================================================


class TestDetectorGlobal:
    """Tests del comportamiento agregado del detector."""

    @pytest.mark.asyncio
    async def test_detector_runs_all_rules_in_parallel(self, temp_git_repo):
        """Todas las heurísticas se ejecutan y agregan findings."""
        previous = {
            "validation_id": "mv_old",
            "context_used": {"host": "gateway01.us-east-1.prod.aws.tidbcloud.com"},
            "operation": "sql_against_production",
            "validation_status": "ok",
            "hilo_id": "hilo_x",
            "ts": (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat(),
        }
        db = MockDB([previous])
        detector = ContaminationDetector(db=db, repo_root=temp_git_repo)
        report = await detector.detect(
            hilo_id="hilo_x",
            operation="sql_against_production",
            context_used={
                "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
                "credential_hash_first_8": "deadbeef",
            },
            current_source_of_truth={"credential_hash_first_8": "fa11abce"},
            current_validation_id="mv_now",
        )
        rule_ids = {f.rule_id for f in report.findings}
        # H1 (deadbeef en repo) + H2 (gateway01→05 +24h)
        assert "H1" in rule_ids
        assert "H2" in rule_ids
        assert report.has_high_severity
        assert report.detector_runtime_ms > 0

    @pytest.mark.asyncio
    async def test_detector_no_findings_when_all_clean(self, temp_git_repo):
        """Sin razones para dispararse → report vacío."""
        db = MockDB([])
        detector = ContaminationDetector(db=db, repo_root=temp_git_repo)
        report = await detector.detect(
            hilo_id="hilo_clean",
            operation="sql_against_production",
            context_used={"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
            current_validation_id="mv_now",
        )
        assert not report.has_warning
        assert not report.has_high_severity

    @pytest.mark.asyncio
    async def test_detector_global_timeout_returns_partial_results(self, temp_git_repo):
        """Si el detector excede global_timeout, retorna lo que pudo + timed_out_rules."""

        class SlowDB:
            async def select(self, *args, **kwargs):
                await asyncio.sleep(2.0)
                return []

        detector = ContaminationDetector(
            db=SlowDB(),
            repo_root=temp_git_repo,
            timeout_ms_per_rule=2000,  # alto para que el rule no auto-cancele
            global_timeout_ms=100,  # global muy corto
        )
        report = await detector.detect(
            hilo_id="hilo_x",
            operation="sql_against_production",
            context_used={"host": "x.com", "credential_hash_first_8": "deadbeef"},
            current_source_of_truth={"credential_hash_first_8": "deadbeef"},
            current_validation_id="mv_now",
        )
        # Debe existir timed_out_rules (al menos H2 y H3 que dependen de la SlowDB)
        assert len(report.timed_out_rules) >= 1

    @pytest.mark.asyncio
    async def test_detector_db_exception_does_not_propagate(self, temp_git_repo):
        """Si la db lanza excepción, las heurísticas afectadas se silencian, otras siguen."""

        class FailingDB:
            async def select(self, *args, **kwargs):
                raise RuntimeError("supabase down")

        detector = ContaminationDetector(db=FailingDB(), repo_root=temp_git_repo)
        report = await detector.detect(
            hilo_id="hilo_x",
            operation="sql_against_production",
            context_used={
                "host": "x.com",
                "credential_hash_first_8": "deadbeef",
            },
            current_source_of_truth={"credential_hash_first_8": "fa11abce"},
            current_validation_id="mv_now",
        )
        # H1 sigue funcionando aunque H2 y H3 fallen silenciosamente
        h1 = [f for f in report.findings if f.rule_id == "H1"]
        assert len(h1) == 1  # H1 detecta el deadbeef en el repo

    @pytest.mark.asyncio
    async def test_report_to_dict_serializable(self, temp_git_repo):
        """ContaminationReport.to_dict() es serializable a JSON."""
        import json

        db = MockDB([])
        detector = ContaminationDetector(db=db, repo_root=temp_git_repo)
        report = await detector.detect(
            hilo_id="hilo_x",
            operation="sql_against_production",
            context_used={"credential_hash_first_8": "deadbeef"},
            current_source_of_truth={"credential_hash_first_8": "fa11abce"},
        )
        as_dict = report.to_dict()
        # No debe explotar
        json_str = json.dumps(as_dict)
        assert "findings" in json_str
        assert "detector_runtime_ms" in json_str

    def test_finding_to_dict_serializable(self):
        """ContaminationFinding.to_dict() es serializable a JSON."""
        import json

        f = ContaminationFinding(
            rule_id="H1",
            severity="HIGH",
            evidence={"x": 1},
            recommendation="do something",
            validation_id_ref="mv_xxx",
        )
        d = f.to_dict()
        assert d["rule_id"] == "H1"
        assert d["severity"] == "HIGH"
        # JSON OK
        json.dumps(d)
