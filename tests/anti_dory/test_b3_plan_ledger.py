"""
Unit Tests — B3 Plan Ledger Adapter
Anti-Dory FORGE v3.0 — Batch 005 Célula B

Tests with mocked Supabase client. No real DB writes.
"""

from unittest.mock import MagicMock

import pytest

from kernel.anti_dory.b3_plan_ledger import (
    VALID_TRANSITIONS,
    InvalidTransitionError,
    PlanCreateRequest,
    PlanDuplicateError,
    PlanEntry,
    PlanLedgerAdapter,
    PlanLedgerError,
    PlanNotFoundError,
    PlanStatus,
    compute_plan_hash,
)


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def adapter(mock_client):
    return PlanLedgerAdapter(client=mock_client)


@pytest.fixture
def sample_row():
    return {
        "id": "plan-001",
        "plan_hash": "abc123def456",
        "plan_summary": "Deploy Anti-Dory B1",
        "status": "CREATED",
        "delegated_to": None,
        "delegated_at": None,
        "parent_plan_id": None,
        "metadata": {"batch": "005"},
        "created_at": "2026-05-20T12:00:00+00:00",
        "completed_at": None,
    }


class TestComputePlanHash:
    def test_deterministic(self):
        h1 = compute_plan_hash("test", {"key": "value"})
        h2 = compute_plan_hash("test", {"key": "value"})
        assert h1 == h2

    def test_different_inputs_different_hash(self):
        h1 = compute_plan_hash("plan A", {})
        h2 = compute_plan_hash("plan B", {})
        assert h1 != h2

    def test_hash_length(self):
        h = compute_plan_hash("test", {})
        assert len(h) == 16


class TestCreatePlan:
    def test_create_without_delegation(self, adapter, mock_client, sample_row):
        mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[sample_row])
        request = PlanCreateRequest(plan_summary="Deploy Anti-Dory B1", metadata={"batch": "005"})
        result = adapter.create_plan(request)
        assert isinstance(result, PlanEntry)
        assert result.plan_summary == "Deploy Anti-Dory B1"

    def test_create_with_delegation(self, adapter, mock_client, sample_row):
        sample_row["status"] = "DELEGATED"
        sample_row["delegated_to"] = "manus_c"
        sample_row["delegated_at"] = "2026-05-20T12:00:00+00:00"
        mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[sample_row])
        request = PlanCreateRequest(plan_summary="Deploy", delegated_to="manus_c")
        result = adapter.create_plan(request)
        assert result.status == PlanStatus.DELEGATED
        assert result.delegated_to == "manus_c"

    def test_create_duplicate_raises(self, adapter, mock_client):
        mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("duplicate key")
        request = PlanCreateRequest(plan_summary="Dup")
        with pytest.raises(PlanDuplicateError):
            adapter.create_plan(request)


class TestGetPlan:
    def test_get_existing(self, adapter, mock_client, sample_row):
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[sample_row])
        )
        result = adapter.get_plan("plan-001")
        assert result.id == "plan-001"

    def test_get_not_found(self, adapter, mock_client):
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[])
        )
        with pytest.raises(PlanNotFoundError):
            adapter.get_plan("nonexistent")


class TestTransitionStatus:
    def test_valid_transition_created_to_in_progress(self, adapter, mock_client, sample_row):
        # get_plan mock
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[sample_row])
        )
        # update mock
        updated_row = {**sample_row, "status": "IN_PROGRESS"}
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[updated_row]
        )
        result = adapter.transition_status("plan-001", PlanStatus.IN_PROGRESS)
        assert result.status == PlanStatus.IN_PROGRESS

    def test_invalid_transition_completed_to_created(self, adapter, mock_client, sample_row):
        sample_row["status"] = "COMPLETED"
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[sample_row])
        )
        with pytest.raises(InvalidTransitionError):
            adapter.transition_status("plan-001", PlanStatus.CREATED)

    def test_invalid_transition_failed_to_in_progress(self, adapter, mock_client, sample_row):
        sample_row["status"] = "FAILED"
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            MagicMock(data=[sample_row])
        )
        with pytest.raises(InvalidTransitionError):
            adapter.transition_status("plan-001", PlanStatus.IN_PROGRESS)


class TestListPlans:
    def test_list_all(self, adapter, mock_client, sample_row):
        mock_chain = mock_client.table.return_value.select.return_value
        mock_chain.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[sample_row]
        )
        result = adapter.list_plans()
        assert len(result) == 1

    def test_list_with_status_filter(self, adapter, mock_client, sample_row):
        mock_chain = mock_client.table.return_value.select.return_value
        mock_chain.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[sample_row]
        )
        result = adapter.list_plans(status_filter=PlanStatus.CREATED)
        assert len(result) == 1


class TestValidTransitions:
    def test_terminal_states_have_no_transitions(self):
        assert VALID_TRANSITIONS[PlanStatus.COMPLETED] == set()
        assert VALID_TRANSITIONS[PlanStatus.FAILED] == set()
        assert VALID_TRANSITIONS[PlanStatus.CANCELLED] == set()

    def test_created_can_delegate(self):
        assert PlanStatus.DELEGATED in VALID_TRANSITIONS[PlanStatus.CREATED]

    def test_all_states_covered(self):
        for status in PlanStatus:
            assert status in VALID_TRANSITIONS


class TestNoClient:
    def test_raises_without_client(self):
        adapter = PlanLedgerAdapter(client=None)
        with pytest.raises(PlanLedgerError, match="not initialized"):
            adapter.get_plan("test")
