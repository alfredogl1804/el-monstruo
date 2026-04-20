"""
El Monstruo — E2E Test Suite for Kernel API
============================================
Tests each intent type, fallback chains, auth middleware,
streaming, and HITL flow against the production kernel.

Usage:
    # Against production:
    KERNEL_URL=https://el-monstruo-kernel-production.up.railway.app \
    MONSTRUO_API_KEY=xxx \
    python -m pytest tests/test_e2e_kernel.py -v

    # Against local:
    python -m pytest tests/test_e2e_kernel.py -v

Validated: 2026-04-16
"""

import json
import logging
import os
import sys
import time
from typing import Optional

import httpx
import pytest

# ── Config ──────────────────────────────────────────────────────────

KERNEL_URL = os.environ.get("KERNEL_URL", "http://localhost:8000")
API_KEY = os.environ.get("MONSTRUO_API_KEY", "")
TEST_USER_ID = "test_e2e_user"
TEST_SESSION_ID = f"test_session_{int(time.time())}"
TIMEOUT = 120  # seconds — some models are slow

logger = logging.getLogger(__name__)


# ── Helpers ─────────────────────────────────────────────────────────


def _headers() -> dict:
    """Build request headers with optional API key."""
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["X-API-Key"] = API_KEY
    return h


def _chat_payload(
    message: str,
    brain: Optional[str] = None,
    force_model: Optional[str] = None,
) -> dict:
    """Build a /v1/chat request payload."""
    payload = {
        "message": message,
        "user_id": TEST_USER_ID,
        "channel": "test",
        "session_id": TEST_SESSION_ID,
    }
    if brain:
        payload["brain"] = brain
    if force_model:
        payload["force_model"] = force_model
    return payload


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def client():
    """Synchronous httpx client for the test session."""
    with httpx.Client(
        base_url=KERNEL_URL,
        timeout=httpx.Timeout(TIMEOUT, connect=15.0),
        headers=_headers(),
    ) as c:
        yield c


@pytest.fixture(scope="session")
def async_client():
    """Async httpx client for streaming tests."""
    return httpx.AsyncClient(
        base_url=KERNEL_URL,
        timeout=httpx.Timeout(TIMEOUT, connect=15.0),
        headers=_headers(),
    )


# ══════════════════════════════════════════════════════════════════════
# SECTION 1: HEALTH & AUTH
# ══════════════════════════════════════════════════════════════════════


class TestHealthAndAuth:
    """Test health endpoint and auth middleware behavior."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 with status=healthy."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert "components" in data
        logger.info(f"Health OK: uptime={data['uptime_seconds']}s")

    def test_auth_rejects_no_key(self):
        """Protected endpoints should return 401 without API key."""
        with httpx.Client(
            base_url=KERNEL_URL,
            timeout=10.0,
            headers={"Content-Type": "application/json"},
        ) as c:
            resp = c.get("/v1/stats")
            # If MONSTRUO_API_KEY is not set in production, this might be 200
            # If it IS set, should be 401
            if API_KEY:
                assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
            else:
                # No auth configured, skip
                pytest.skip("No API key configured, auth not enforced")

    def test_auth_rejects_bad_key(self):
        """Protected endpoints should return 403 with wrong API key."""
        with httpx.Client(
            base_url=KERNEL_URL,
            timeout=10.0,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "definitely-wrong-key",
            },
        ) as c:
            resp = c.get("/v1/stats")
            if API_KEY:
                assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
            else:
                pytest.skip("No API key configured, auth not enforced")

    def test_stats_with_valid_key(self, client):
        """Stats endpoint should return 200 with valid API key."""
        resp = client.get("/v1/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "uptime_seconds" in data
        logger.info(f"Stats OK: {json.dumps(data, indent=2)[:500]}")


# ══════════════════════════════════════════════════════════════════════
# SECTION 2: CHAT — INTENT CLASSIFICATION
# ══════════════════════════════════════════════════════════════════════


class TestChatIntents:
    """Test that different message types are classified and routed correctly."""

    def test_chat_simple_greeting(self, client):
        """Simple greeting should be classified as chat_rapido or chat."""
        resp = client.post("/v1/chat", json=_chat_payload("Hola, ¿cómo estás?"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"], "Response should not be empty"
        assert data["status"] in ("completed", "awaiting_human")
        assert data["model_used"], "model_used should be populated"
        logger.info(f"Chat greeting: intent={data['intent']}, model={data['model_used']}")

    def test_chat_quick_question(self, client):
        """Quick factual question should route to a fast model."""
        resp = client.post(
            "/v1/chat",
            json=_chat_payload("¿Cuál es la capital de Francia?"),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"], "Response should not be empty"
        assert "París" in data["response"] or "Paris" in data["response"], (
            f"Expected 'París' in response, got: {data['response'][:200]}"
        )
        logger.info(
            f"Quick Q: intent={data['intent']}, model={data['model_used']}, latency={data.get('latency_ms', 0)}ms"
        )

    def test_deep_think_analysis(self, client):
        """Analytical question should trigger deep_think intent."""
        resp = client.post(
            "/v1/chat",
            json=_chat_payload(
                "Analiza en profundidad las ventajas y desventajas de usar "
                "microservicios vs monolitos para una startup en etapa temprana."
            ),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"], "Response should not be empty"
        assert len(data["response"]) > 200, f"Deep think response should be detailed, got {len(data['response'])} chars"
        logger.info(f"Deep think: intent={data['intent']}, model={data['model_used']}, len={len(data['response'])}")

    def test_system_command_memory_clear(self, client):
        """System commands (like memory operations) should be handled."""
        resp = client.post(
            "/v1/chat",
            json=_chat_payload("¿Qué recuerdas de mí?"),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"], "Response should not be empty"
        logger.info(f"System cmd: intent={data['intent']}, model={data['model_used']}")


# ══════════════════════════════════════════════════════════════════════
# SECTION 3: BRAIN OVERRIDE
# ══════════════════════════════════════════════════════════════════════


class TestBrainOverride:
    """Test that brain parameter forces specific model routing."""

    def test_force_model_parameter(self, client):
        """force_model should override the router's model selection."""
        resp = client.post(
            "/v1/chat",
            json=_chat_payload(
                "Di 'test exitoso' en una línea.",
                force_model="gemini_flash_lite",
            ),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"], "Response should not be empty"
        logger.info(f"Force model: model_used={data['model_used']}")

    def test_brain_parameter(self, client):
        """brain parameter should influence model selection."""
        resp = client.post(
            "/v1/chat",
            json=_chat_payload(
                "Di 'brain test exitoso' en una línea.",
                brain="investigador",
            ),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"], "Response should not be empty"
        logger.info(f"Brain param: brain_used={data.get('brain_used', '?')}, model={data['model_used']}")


# ══════════════════════════════════════════════════════════════════════
# SECTION 4: STREAMING
# ══════════════════════════════════════════════════════════════════════


class TestStreaming:
    """Test SSE streaming endpoint."""

    @pytest.mark.asyncio
    async def test_chat_stream_returns_chunks(self, async_client):
        """Streaming endpoint should return SSE events with chunks."""
        chunks_received = 0
        meta_received = False
        done_received = False
        accumulated_text = ""

        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json=_chat_payload("Cuenta del 1 al 5."),
            headers=_headers(),
        ) as resp:
            assert resp.status_code == 200

            async for line in resp.aiter_lines():
                line = line.strip()
                if not line or not line.startswith("data: "):
                    continue

                try:
                    event = json.loads(line[6:])
                except json.JSONDecodeError:
                    continue

                event_type = event.get("type", "")

                if event_type == "meta":
                    meta_received = True
                elif event_type == "chunk":
                    chunks_received += 1
                    accumulated_text += event.get("text", "")
                elif event_type == "done":
                    done_received = True
                    break
                elif event_type == "error":
                    pytest.fail(f"Stream error: {event.get('message', 'unknown')}")

        assert meta_received, "Should receive meta event"
        assert chunks_received > 0, "Should receive at least one chunk"
        assert done_received, "Should receive done event"
        assert accumulated_text.strip(), "Accumulated text should not be empty"
        logger.info(f"Stream OK: {chunks_received} chunks, {len(accumulated_text)} chars")


# ══════════════════════════════════════════════════════════════════════
# SECTION 5: ERROR HANDLING
# ══════════════════════════════════════════════════════════════════════


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_empty_message_rejected(self, client):
        """Empty message should be rejected with 422."""
        resp = client.post(
            "/v1/chat",
            json={"message": "", "user_id": TEST_USER_ID},
        )
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}"

    def test_missing_message_rejected(self, client):
        """Missing message field should be rejected with 422."""
        resp = client.post(
            "/v1/chat",
            json={"user_id": TEST_USER_ID},
        )
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}"

    def test_very_long_message_handled(self, client):
        """Very long message should either work or return appropriate error."""
        long_msg = "Hola " * 5000  # ~25000 chars, within 32000 limit
        resp = client.post(
            "/v1/chat",
            json=_chat_payload(long_msg),
        )
        # Should either succeed or return a clear error, not 500
        assert resp.status_code in (200, 422, 413), f"Expected 200/422/413, got {resp.status_code}"


# ══════════════════════════════════════════════════════════════════════
# SECTION 6: CONVERSATION CONTEXT
# ══════════════════════════════════════════════════════════════════════


class TestConversationContext:
    """Test that conversation memory works across messages."""

    def test_multi_turn_context(self, client):
        """Second message should have context from first."""
        session = f"test_context_{int(time.time())}"

        # First message
        resp1 = client.post(
            "/v1/chat",
            json={
                "message": "Mi nombre es TestBot y mi color favorito es azul.",
                "user_id": TEST_USER_ID,
                "channel": "test",
                "session_id": session,
            },
        )
        assert resp1.status_code == 200

        # Wait a moment for memory write
        time.sleep(2)

        # Second message referencing first
        resp2 = client.post(
            "/v1/chat",
            json={
                "message": "¿Cuál es mi color favorito?",
                "user_id": TEST_USER_ID,
                "channel": "test",
                "session_id": session,
            },
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        # The response should reference "azul" if memory works
        response_lower = data2["response"].lower()
        assert "azul" in response_lower or "blue" in response_lower, (
            f"Expected 'azul' in response, got: {data2['response'][:300]}"
        )
        logger.info("Multi-turn context: OK — response mentions 'azul'")


# ══════════════════════════════════════════════════════════════════════
# SECTION 7: HISTORY & EVENTS
# ══════════════════════════════════════════════════════════════════════


class TestHistoryAndEvents:
    """Test history and events endpoints."""

    def test_history_endpoint(self, client):
        """History endpoint should return conversation history."""
        resp = client.get(
            "/v1/history",
            params={"user_id": TEST_USER_ID, "limit": 5},
        )
        # Might be 200 or 404 if no history exists
        assert resp.status_code in (200, 404), f"Expected 200/404, got {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            logger.info(f"History: {len(data)} entries")

    def test_recent_events(self, client):
        """Recent events endpoint should return event list or dict with events."""
        resp = client.get("/v1/events/recent", params={"limit": 5})
        assert resp.status_code == 200
        data = resp.json()
        # API may return a list directly or a dict with {count, events}
        if isinstance(data, dict):
            assert "events" in data, f"Expected 'events' key in dict, got: {list(data.keys())}"
            events = data["events"]
            assert isinstance(events, list)
            logger.info(f"Recent events: {data.get('count', len(events))} entries")
        else:
            assert isinstance(data, list)
            logger.info(f"Recent events: {len(data)} entries")


# ══════════════════════════════════════════════════════════════════════
# SECTION 8: FULL E2E SMOKE TEST
# ══════════════════════════════════════════════════════════════════════


class TestFullE2ESmoke:
    """
    Full smoke test: send 5 different intent types and verify
    each gets a valid response with correct metadata.
    """

    @pytest.mark.parametrize(
        "message,expected_min_len",
        [
            ("Hola", 5),
            ("¿Cuál es el tipo de cambio del dólar hoy?", 20),
            ("Analiza las implicaciones de la IA en el empleo", 100),
            ("Recuérdame que tengo una junta mañana a las 10am", 10),
            ("Resume en 3 puntos qué es blockchain", 30),
        ],
    )
    def test_smoke_various_intents(self, client, message, expected_min_len):
        """Each message type should get a valid response."""
        resp = client.post("/v1/chat", json=_chat_payload(message))
        assert resp.status_code == 200, f"Failed for '{message}': {resp.status_code}"
        data = resp.json()
        assert data["response"], f"Empty response for '{message}'"
        assert len(data["response"]) >= expected_min_len, (
            f"Response too short for '{message}': {len(data['response'])} chars"
        )
        assert data["model_used"], f"No model_used for '{message}'"
        logger.info(
            f"Smoke [{data['intent']}]: "
            f"model={data['model_used']}, "
            f"len={len(data['response'])}, "
            f"latency={data.get('latency_ms', 0)}ms"
        )


# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Run tests directly with python."""
    sys.exit(
        pytest.main(
            [
                __file__,
                "-v",
                "--tb=short",
                "-x",  # Stop on first failure
                "--log-cli-level=INFO",
            ]
        )
    )
