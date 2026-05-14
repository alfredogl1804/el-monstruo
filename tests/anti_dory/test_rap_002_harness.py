"""
tests/anti_dory/test_rap_002_harness.py — RAP-002 harness (7 tests binarios).

Sprint MANUS-ANTI-DORY-002 v1 FASE B.7.
Doctrina §A.11: 7 tests duros (A-G) que validan el comportamiento del sistema
Anti-Dory SIN tocar Supabase real, SIN tocar Railway, SIN tocar Manus API.

Estrategia: MockRPCClient simula respuestas de RPCs canónicos. Cada test
inyecta un escenario y verifica el comportamiento esperado.

Casos (corresponden a §A.11 del SPEC):
- A. Happy path: snapshot fresh + confidence alta → ATTACHMENT_OK passed.
- B. Crash mid-session: no hay write_on_final → heartbeat snapshot existe
     → recovery_mode propone pregunta binaria.
- C. Concurrencia CAS: dos writers intentan accept simultáneo → 1 gana, 1 conflict.
- D. Stale snapshot: age > threshold → ATTACHMENT_OK passed=False, fallback_reason=stale.
- E. Sprint bloqueado: head apunta a sprint distinto del front_id → R7 violation.
- F. Branch mismatch: do_not_touch contiene path que agente quiere modificar.
     v1 solo verifica que do_not_touch sea expuesto correctamente.
- G. No-events: front_id sin runtime_events → recovery_mode declara HARD_FAILURE.

Ejecución: pytest tests/anti_dory/test_rap_002_harness.py -v
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import pytest

from kernel.anti_dory.context_broker import (
    AttachmentPack,
    CONFIDENCE_MIN_AUTO,
    ContextBroker,
    STALENESS_THRESHOLD_SECONDS,
    canonical_state_hash,
)
from kernel.anti_dory.guardian import (
    AttachmentVerdict,
    HaltAttachmentMismatch,
    verify_attachment_contract,
    verify_state_hash,
)
from kernel.anti_dory.recovery import RecoveryMode
from kernel.anti_dory.writers import (
    AgentExplicitWriter,
    HeartbeatWriter,
    WriteResult,
)


# =============================================================================
# Mock RPC client (NO toca Supabase real)
# =============================================================================

class MockRPCClient:
    """RPC client en memoria. Soporta los 5 RPCs canónicos.

    Estado interno simula tablas runtime_events, thread_snapshots,
    project_runtime_heads.
    """

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.snapshots: list[dict[str, Any]] = []
        self.heads: dict[tuple[str, str], dict[str, Any]] = {}
        # Stubs configurables por test
        self.stub_head: Optional[dict[str, Any]] = None
        self.stub_scan: Optional[dict[str, Any]] = None
        self.accept_should_fail: bool = False
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def call_rpc(self, name: str, params: dict[str, Any]) -> Any:
        self.calls.append((name, dict(params)))

        if name == "rpc_get_context_head":
            return [self.stub_head] if self.stub_head else []

        if name == "rpc_write_runtime_event":
            event_id = f"evt-{len(self.events) + 1:04d}"
            self.events.append({"id": event_id, **params})
            return event_id

        if name == "rpc_write_thread_snapshot":
            snap_id = f"snap-{len(self.snapshots) + 1:04d}"
            self.snapshots.append({"id": snap_id, **params})
            return snap_id

        if name == "rpc_accept_snapshot":
            if self.accept_should_fail:
                return [{"accepted": False, "new_lock_version": None,
                         "conflict_reason": "lock_version_mismatch"}]
            return [{"accepted": True, "new_lock_version": 1, "conflict_reason": None}]

        if name == "rpc_recovery_scan":
            return [self.stub_scan] if self.stub_scan else []

        raise ValueError(f"MockRPCClient: unsupported RPC {name}")


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def rpc() -> MockRPCClient:
    return MockRPCClient()


@pytest.fixture
def fresh_head_payload() -> dict[str, Any]:
    """Head representativo de un snapshot reciente, alta confianza."""
    payload = {
        "project_id": "el-monstruo",
        "front_id": "manus-anti-dory-002",
        "writer_mode": "explicit_final",
        "actor_type": "manus",
    }
    return {
        "snapshot_id": "snap-fresh-001",
        "sprint_id": "sprint-anti-dory-002-v1",
        "phase": "fase-b",
        "last_t1_decision": "T2-A GREEN + T1 autoriza FASE B",
        "next_expected_action": "continuar implementación writers",
        "do_not_touch": ["PR #118", "Mac local", "kernel/cowork_runtime/*"],
        "evidence_refs": [{"type": "pr", "number": 124, "state": "open"}],
        "confidence_score": 0.92,
        "state_hash": canonical_state_hash(payload),
        "writer_mode": "explicit_final",
        "snapshot_created_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
    }


# =============================================================================
# CASO A — Happy path
# =============================================================================

def test_caso_a_happy_path(rpc: MockRPCClient, fresh_head_payload: dict[str, Any]) -> None:
    """Snapshot fresh + confidence alta → ATTACHMENT_OK + Guardian passed."""
    rpc.stub_head = fresh_head_payload

    broker = ContextBroker(rpc_client=rpc, enabled=True)
    hydrated = broker.hydrate_prompt(
        project_id="el-monstruo",
        front_id="manus-anti-dory-002",
        user_prompt="continuá lo de ayer con El Monstruo; no te reexplico nada.",
    )

    assert hydrated.pack.attachment_ok is True
    assert hydrated.pack.snapshot_id == "snap-fresh-001"
    assert hydrated.pack.confidence_score == 0.92
    assert "ATTACHMENT_OK" in hydrated.hydrated_prompt
    assert "PR #118" in hydrated.hydrated_prompt

    verdict = verify_attachment_contract(hydrated.pack)
    assert verdict.passed is True, verdict.format_report()
    assert verdict.violations == []


# =============================================================================
# CASO B — Crash mid-session (no write_on_final)
# =============================================================================

def test_caso_b_crash_mid_session_heartbeat_recovers(rpc: MockRPCClient) -> None:
    """Sin head (write_on_final no ocurrió) pero heartbeat dejó pending snapshot.
    Recovery propone pregunta binaria."""
    rpc.stub_head = None
    rpc.stub_scan = {
        "event_count": 7,
        "last_event_id": "evt-0007",
        "last_event_type": "artifact_created",
        "last_actor_type": "manus",
        "last_pending_snapshot_id": "snap-pending-007",
        "last_sprint_id": "sprint-anti-dory-002-v1",
        "last_phase": "fase-b",
        "last_confidence": 0.66,
        "last_state_hash": "abc123",
        "last_age_seconds": 120,
    }

    recovery = RecoveryMode(rpc_client=rpc)
    proposal = recovery.attempt_recovery(
        project_id="el-monstruo",
        front_id="manus-anti-dory-002",
    )

    assert proposal.has_candidate is True
    assert proposal.binary_question is not None
    assert "snap-pen" in proposal.binary_question
    assert "Sí/No" in proposal.binary_question
    assert proposal.candidate_pack is not None
    assert proposal.candidate_pack.snapshot_id == "snap-pending-007"
    assert proposal.candidate_pack.confidence_score == 0.66


# =============================================================================
# CASO C — Concurrencia CAS
# =============================================================================

def test_caso_c_concurrency_cas_conflict(rpc: MockRPCClient) -> None:
    """Dos writers intentan accept_snapshot → uno gana, otro conflict."""
    rpc.accept_should_fail = True  # simula que ya hubo otro accept antes

    writer = AgentExplicitWriter(rpc_client=rpc, actor_type="manus")
    result = writer.write_on_final(
        parent_snapshot_id="snap-parent-001",
        project_id="el-monstruo",
        front_id="manus-anti-dory-002",
        exit_status="ok",
        summary="cierre normal",
        expected_lock_version=0,
    )

    # El snapshot se crea, el evento se registra, pero accept_snapshot devuelve conflict.
    assert result.snapshot_id is not None
    assert result.event_id is not None
    assert result.accepted is False
    assert result.error == "lock_version_mismatch"


# =============================================================================
# CASO D — Stale snapshot
# =============================================================================

def test_caso_d_stale_snapshot_blocks_attachment(rpc: MockRPCClient) -> None:
    """Snapshot age > threshold → attachment_ok=False, fallback_reason='stale'."""
    stale_ts = datetime.now(timezone.utc) - timedelta(seconds=STALENESS_THRESHOLD_SECONDS + 3600)
    rpc.stub_head = {
        "snapshot_id": "snap-old-001",
        "sprint_id": "sprint-old",
        "phase": "fase-a",
        "last_t1_decision": None,
        "next_expected_action": None,
        "do_not_touch": [],
        "evidence_refs": [],
        "confidence_score": 0.95,
        "state_hash": "xyz",
        "writer_mode": "explicit_final",
        "snapshot_created_at": stale_ts.isoformat(),
    }

    broker = ContextBroker(rpc_client=rpc, enabled=True)
    hydrated = broker.hydrate_prompt(
        project_id="el-monstruo",
        front_id="frente-stale",
        user_prompt="test",
    )

    assert hydrated.pack.attachment_ok is False
    assert hydrated.pack.fallback_reason == "stale"
    assert hydrated.hydrated_prompt == "test"  # prompt sin modificar

    verdict = verify_attachment_contract(hydrated.pack)
    assert verdict.passed is False
    assert any("R1:attachment_ok_false" in v for v in verdict.violations)
    assert any("R4:stale" in v for v in verdict.violations)
    assert verdict.suggest_recovery is True


# =============================================================================
# CASO E — Sprint bloqueado / writer_mode inválido
# =============================================================================

def test_caso_e_invalid_writer_mode_blocks(rpc: MockRPCClient) -> None:
    """Si head tiene writer_mode inválido → R7 violation."""
    rpc.stub_head = {
        "snapshot_id": "snap-bad-001",
        "sprint_id": "sprint-x",
        "phase": "fase-a",
        "last_t1_decision": None,
        "next_expected_action": None,
        "do_not_touch": [],
        "evidence_refs": [],
        "confidence_score": 0.95,
        "state_hash": "abc",
        "writer_mode": "MODO_INEXISTENTE",  # ← invalida R7
        "snapshot_created_at": datetime.now(timezone.utc).isoformat(),
    }

    broker = ContextBroker(rpc_client=rpc, enabled=True)
    hydrated = broker.hydrate_prompt(
        project_id="el-monstruo",
        front_id="frente-x",
        user_prompt="test",
    )

    # ContextBroker no rechaza writer_mode (lo hace Guardian).
    # Pero Guardian sí.
    verdict = verify_attachment_contract(hydrated.pack)
    assert verdict.passed is False
    assert any("R7:invalid_writer_mode" in v for v in verdict.violations)


# =============================================================================
# CASO F — do_not_touch expuesto correctamente
# =============================================================================

def test_caso_f_do_not_touch_expuesto_y_visible(rpc: MockRPCClient, fresh_head_payload: dict[str, Any]) -> None:
    """do_not_touch debe aparecer en el prompt hidratado para que el agente lo respete."""
    rpc.stub_head = fresh_head_payload

    broker = ContextBroker(rpc_client=rpc, enabled=True)
    hydrated = broker.hydrate_prompt(
        project_id="el-monstruo",
        front_id="manus-anti-dory-002",
        user_prompt="test",
    )

    assert "PR #118" in hydrated.hydrated_prompt
    assert "Mac local" in hydrated.hydrated_prompt
    assert "kernel/cowork_runtime/*" in hydrated.hydrated_prompt

    # Asegurar que se preserva en el pack como lista
    assert isinstance(hydrated.pack.do_not_touch, list)
    assert len(hydrated.pack.do_not_touch) == 3


# =============================================================================
# CASO G — No-events → HARD_FAILURE
# =============================================================================

def test_caso_g_no_events_hard_failure(rpc: MockRPCClient) -> None:
    """Front sin runtime_events → RecoveryMode declara HARD_FAILURE explícito."""
    rpc.stub_head = None
    rpc.stub_scan = None  # ni snapshots ni eventos

    recovery = RecoveryMode(rpc_client=rpc)
    proposal = recovery.attempt_recovery(
        project_id="el-monstruo",
        front_id="frente-virgen",
    )

    assert proposal.has_candidate is False
    assert proposal.binary_question is None
    assert proposal.candidate_pack is None
    assert proposal.hard_failure_reason is not None
    assert "no_events" in proposal.hard_failure_reason


# =============================================================================
# Extras de robustez
# =============================================================================

def test_feature_flag_off_devuelve_prompt_intacto(rpc: MockRPCClient, fresh_head_payload: dict[str, Any]) -> None:
    rpc.stub_head = fresh_head_payload
    broker = ContextBroker(rpc_client=rpc, enabled=False)
    hydrated = broker.hydrate_prompt(
        project_id="el-monstruo",
        front_id="manus-anti-dory-002",
        user_prompt="hola",
    )
    assert hydrated.hydrated_prompt == "hola"
    assert hydrated.pack.attachment_ok is False
    assert hydrated.pack.fallback_reason == "feature_flag_off"


def test_canonical_state_hash_is_deterministic() -> None:
    """state_hash debe ser estable bajo reordenamiento de keys."""
    a = canonical_state_hash({"b": 2, "a": 1})
    b = canonical_state_hash({"a": 1, "b": 2})
    assert a == b


def test_halt_exception_message_includes_violations() -> None:
    """HaltAttachmentMismatch debe exponer reason y violations."""
    exc = HaltAttachmentMismatch("test_reason", ["v1", "v2"])
    assert "test_reason" in str(exc)
    assert "v1" in str(exc) and "v2" in str(exc)
    assert exc.violations == ["v1", "v2"]


def test_writer_on_start_writes_event_and_snapshot(rpc: MockRPCClient) -> None:
    writer = AgentExplicitWriter(rpc_client=rpc, actor_type="manus")
    result = writer.write_on_start(
        project_id="el-monstruo",
        front_id="manus-anti-dory-002",
        sprint_id="sprint-anti-dory-002-v1",
        phase="fase-b",
        do_not_touch=["PR #118"],
        evidence_refs=[{"type": "pr", "number": 124}],
        confidence_score=0.90,
    )
    assert result.snapshot_id is not None
    assert result.event_id is not None
    assert len(rpc.snapshots) == 1
    assert len(rpc.events) == 1
    assert rpc.snapshots[0]["p_writer_mode"] == "explicit_start"


def test_heartbeat_writer_independent_of_agent(rpc: MockRPCClient) -> None:
    rpc.stub_scan = {
        "event_count": 3,
        "last_event_id": "evt-0003",
        "last_event_type": "artifact_created",
        "last_actor_type": "manus",
    }
    hb = HeartbeatWriter(rpc_client=rpc)
    result = hb.tick(project_id="el-monstruo", front_id="manus-anti-dory-002")
    assert result.snapshot_id is not None
    assert result.event_id is not None
    # Asegurar que el writer_mode es 'heartbeat'
    assert rpc.snapshots[0]["p_writer_mode"] == "heartbeat"
