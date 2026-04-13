"""
Tests for the /v1/feedback endpoint and HITL event categories.
Sprint 1 — Convergence Phase.
"""

import pytest
from uuid import uuid4

from contracts.event_envelope import EventCategory, EventBuilder


# ── EventCategory HITL Tests ──────────────────────────────────────

class TestHITLEventCategories:
    """Test that HITL event categories exist and have correct values."""

    def test_human_feedback_exists(self):
        assert EventCategory.HUMAN_FEEDBACK.value == "hitl.feedback"

    def test_human_approved_exists(self):
        assert EventCategory.HUMAN_APPROVED.value == "hitl.approved"

    def test_human_rejected_exists(self):
        assert EventCategory.HUMAN_REJECTED.value == "hitl.rejected"

    def test_hitl_categories_are_distinct(self):
        hitl_values = {
            EventCategory.HUMAN_FEEDBACK.value,
            EventCategory.HUMAN_APPROVED.value,
            EventCategory.HUMAN_REJECTED.value,
        }
        assert len(hitl_values) == 3

    def test_build_feedback_event(self):
        run_id = uuid4()
        event = (
            EventBuilder()
            .category(EventCategory.HUMAN_FEEDBACK)
            .actor("alfredo_telegram")
            .action("feedback:approve")
            .for_run(run_id)
            .with_payload({
                "action": "approve",
                "comment": "Looks good",
                "edited_response": None,
            })
            .build()
        )
        assert event.category == EventCategory.HUMAN_FEEDBACK
        assert event.actor == "alfredo_telegram"
        assert event.action == "feedback:approve"
        assert event.run_id == run_id
        assert event.payload["action"] == "approve"

    def test_build_rejection_event(self):
        run_id = uuid4()
        event = (
            EventBuilder()
            .category(EventCategory.HUMAN_REJECTED)
            .actor("alfredo_telegram")
            .action("feedback:reject")
            .for_run(run_id)
            .with_payload({
                "action": "reject",
                "comment": "Not what I asked for",
            })
            .build()
        )
        assert event.category == EventCategory.HUMAN_REJECTED
        assert event.payload["comment"] == "Not what I asked for"


# ── FeedbackRequest Model Tests ───────────────────────────────────

class TestFeedbackRequestModel:
    """Test the FeedbackRequest Pydantic model from main.py."""

    def test_import_feedback_request(self):
        from kernel.main import FeedbackRequest
        req = FeedbackRequest(
            run_id=str(uuid4()),
            action="approve",
            user_id="alfredo",
            comment="LGTM",
        )
        assert req.action == "approve"
        assert req.user_id == "alfredo"
        assert req.comment == "LGTM"
        assert req.edited_response is None

    def test_feedback_request_with_edit(self):
        from kernel.main import FeedbackRequest
        req = FeedbackRequest(
            run_id=str(uuid4()),
            action="edit",
            user_id="alfredo",
            edited_response="This is the corrected response.",
        )
        assert req.action == "edit"
        assert req.edited_response == "This is the corrected response."

    def test_feedback_request_minimal(self):
        from kernel.main import FeedbackRequest
        req = FeedbackRequest(
            run_id=str(uuid4()),
            action="reject",
        )
        assert req.action == "reject"
        assert req.user_id == "alfredo"  # default
        assert req.comment is None

    def test_feedback_actions(self):
        """Verify all 4 expected actions can be created."""
        from kernel.main import FeedbackRequest
        for action in ["approve", "reject", "edit", "escalate"]:
            req = FeedbackRequest(run_id=str(uuid4()), action=action)
            assert req.action == action


# ── FastAPI Endpoint Tests ────────────────────────────────────────

class TestFeedbackEndpoint:
    """Test the /v1/feedback endpoint via TestClient."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from kernel.main import app
        return TestClient(app)

    def test_feedback_returns_503_when_kernel_not_initialized(self, client):
        """Without lifespan, kernel is None → 503."""
        response = client.post("/v1/feedback", json={
            "run_id": str(uuid4()),
            "action": "approve",
        })
        assert response.status_code == 503

    def test_feedback_invalid_run_id(self, client):
        """Invalid UUID format → 400 (if kernel were initialized)."""
        # Without kernel, we get 503 first
        response = client.post("/v1/feedback", json={
            "run_id": "not-a-uuid",
            "action": "approve",
        })
        # 503 because kernel is not initialized in test mode
        assert response.status_code == 503

    def test_feedback_endpoint_exists(self, client):
        """Verify the endpoint exists and accepts POST."""
        response = client.post("/v1/feedback", json={
            "run_id": str(uuid4()),
            "action": "approve",
        })
        # Should be 503 (kernel not init), NOT 404 (route not found)
        assert response.status_code != 404


# ── Dockerfile Existence Tests ────────────────────────────────────

class TestDeploymentFiles:
    """Verify deployment files exist and have correct structure."""

    def test_dockerfile_exists(self):
        import os
        assert os.path.exists("/home/ubuntu/el-monstruo/Dockerfile")

    def test_railway_toml_exists(self):
        import os
        assert os.path.exists("/home/ubuntu/el-monstruo/railway.toml")

    def test_env_example_exists(self):
        import os
        assert os.path.exists("/home/ubuntu/el-monstruo/.env.example")

    def test_dockerfile_uses_python312(self):
        with open("/home/ubuntu/el-monstruo/Dockerfile") as f:
            content = f.read()
        assert "python:3.12" in content

    def test_dockerfile_exposes_port(self):
        with open("/home/ubuntu/el-monstruo/Dockerfile") as f:
            content = f.read()
        assert "EXPOSE" in content

    def test_env_example_has_kernel_api_url(self):
        with open("/home/ubuntu/el-monstruo/.env.example") as f:
            content = f.read()
        assert "KERNEL_API_URL" in content
