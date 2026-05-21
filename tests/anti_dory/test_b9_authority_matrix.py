"""
Unit Tests — B9 Authority Matrix
Anti-Dory FORGE v3.0 — Batch 004 Célula B

10 test cases del plan B9-E3 v0.2 implementados con mocks puros.
Sin Supabase. Sin APIs externas. Sin runtime crítico.
"""

import pytest

from kernel.anti_dory.b9_authority_matrix import (
    AuthorityMatrix,
    AuthorityResult,
    Decision,
    LayerStatus,
    LayerVote,
    SystemState,
)


@pytest.fixture
def matrix():
    return AuthorityMatrix()


# === Caso 1: Acuerdo VERIFICADOR + Memento + Guardian + T1 = ALLOW ===
class TestB9_1_AllAgreeAllow:
    def test_unanimous_allow(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.ALLOW),
            memento=LayerVote(decision=Decision.ALLOW),
            guardian=LayerVote(decision=Decision.ALLOW),
            t1=LayerVote(decision=Decision.ALLOW),
        )
        assert result.final_decision == Decision.ALLOW
        assert result.system_state == SystemState.HEALTHY
        assert result.b8_disabled is False


# === Caso 2: Acuerdo todos = DENY ===
class TestB9_2_AllAgreeDeny:
    def test_unanimous_deny(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.DENY),
            memento=LayerVote(decision=Decision.DENY),
            guardian=LayerVote(decision=Decision.DENY),
            t1=LayerVote(decision=Decision.DENY),
        )
        assert result.final_decision == Decision.DENY
        assert result.system_state == SystemState.HEALTHY


# === Caso 3: Acuerdo todos = HALT ===
class TestB9_3_AllAgreeHalt:
    def test_unanimous_halt(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.HALT),
            memento=LayerVote(decision=Decision.HALT),
            guardian=LayerVote(decision=Decision.HALT),
            t1=LayerVote(decision=Decision.HALT),
        )
        assert result.final_decision == Decision.HALT
        assert result.system_state == SystemState.HEALTHY


# === Caso 4: Acuerdo todos = WAIT / AWAITING_GUARDIAN ===
class TestB9_4_AllAgreeWait:
    def test_unanimous_wait_becomes_awaiting_guardian(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.WAIT),
            memento=LayerVote(decision=Decision.WAIT),
            guardian=LayerVote(decision=Decision.WAIT),
            t1=None,
        )
        assert result.final_decision == Decision.AWAITING_GUARDIAN
        assert result.system_state == SystemState.HEALTHY


# === Caso 5: Desacuerdo B9.3 — VERIFICADOR ALLOW + Memento DENY → Memento gana ===
class TestB9_5_MementoOverridesVerificador:
    def test_memento_deny_overrides_verificador_allow(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.ALLOW),
            memento=LayerVote(decision=Decision.DENY),
            guardian=LayerVote(decision=Decision.ALLOW),
            t1=None,
        )
        assert result.final_decision == Decision.DENY
        assert "B9.3" in result.log_entries[0]
        assert result.system_state == SystemState.HEALTHY


# === Caso 6: Desacuerdo B9.4 — VERIFICADOR DENY + Guardian OVERRIDE → Guardian no puede sin T1 ===
class TestB9_6_GuardianCannotOverrideWithoutT1:
    def test_guardian_allow_cannot_override_verificador_deny(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.DENY),
            memento=LayerVote(decision=Decision.DENY),
            guardian=LayerVote(decision=Decision.ALLOW),
            t1=None,
        )
        assert result.final_decision == Decision.DENY
        assert result.system_state == SystemState.HEALTHY


# === Caso 7: Override B9.5 — T1 firma manual + VERIFICADOR DENY → T1 gana ===
class TestB9_7_T1Override:
    def test_t1_overrides_verificador_deny(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.DENY),
            memento=LayerVote(decision=Decision.DENY),
            guardian=LayerVote(decision=Decision.DENY),
            t1=LayerVote(decision=Decision.ALLOW),
        )
        assert result.final_decision == Decision.ALLOW
        assert any("T1_OVERRIDE_VERIFICADOR_DENY" in log for log in result.log_entries)
        assert result.system_state == SystemState.HEALTHY

    def test_t1_override_logs_correctly(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.DENY),
            memento=LayerVote(decision=Decision.ALLOW),
            guardian=LayerVote(decision=Decision.ALLOW),
            t1=LayerVote(decision=Decision.ALLOW),
        )
        assert result.final_decision == Decision.ALLOW
        assert any("T1_OVERRIDE" in log for log in result.log_entries)


# === Caso 8: Degradación B9.6 — VERIFICADOR falla → VERIFICADOR_DEGRADED + B8 DISABLED ===
class TestB9_8_VerificadorDegraded:
    def test_verificador_timeout(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.ALLOW, status=LayerStatus.TIMEOUT),
            memento=LayerVote(decision=Decision.ALLOW),
            guardian=LayerVote(decision=Decision.ALLOW),
            t1=None,
        )
        assert result.system_state == SystemState.VERIFICADOR_DEGRADED
        assert result.b8_disabled is True
        assert result.final_decision == Decision.HALT

    def test_verificador_none(self, matrix):
        result = matrix.resolve(
            verificador=None,
            memento=LayerVote(decision=Decision.ALLOW),
            guardian=LayerVote(decision=Decision.ALLOW),
            t1=None,
        )
        assert result.system_state == SystemState.VERIFICADOR_DEGRADED
        assert result.b8_disabled is True


# === Caso 9: Degradación B9.7 — Memento falla → acciones magnas bloqueadas ===
class TestB9_9_MementoDegraded:
    def test_memento_timeout(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.ALLOW),
            memento=LayerVote(decision=Decision.ALLOW, status=LayerStatus.TIMEOUT),
            guardian=LayerVote(decision=Decision.ALLOW),
            t1=None,
        )
        assert result.system_state == SystemState.MEMENTO_DEGRADED
        assert result.final_decision == Decision.HALT
        assert any("magna actions blocked" in log for log in result.log_entries)

    def test_memento_none(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.ALLOW),
            memento=None,
            guardian=LayerVote(decision=Decision.ALLOW),
            t1=None,
        )
        assert result.final_decision == Decision.HALT
        assert result.system_state == SystemState.MEMENTO_DEGRADED


# === Caso 10: Degradación B9.8 — Guardian falla → AWAITING_GUARDIAN ===
class TestB9_10_GuardianDegraded:
    def test_guardian_timeout(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.ALLOW),
            memento=LayerVote(decision=Decision.ALLOW),
            guardian=LayerVote(decision=Decision.ALLOW, status=LayerStatus.ERROR),
            t1=None,
        )
        assert result.system_state == SystemState.GUARDIAN_DEGRADED
        assert result.final_decision == Decision.AWAITING_GUARDIAN
        assert any("no auto-decision" in log for log in result.log_entries)

    def test_guardian_none(self, matrix):
        result = matrix.resolve(
            verificador=LayerVote(decision=Decision.ALLOW),
            memento=LayerVote(decision=Decision.ALLOW),
            guardian=None,
            t1=None,
        )
        assert result.final_decision == Decision.AWAITING_GUARDIAN
        assert result.system_state == SystemState.GUARDIAN_DEGRADED
