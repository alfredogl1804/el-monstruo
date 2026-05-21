"""
tests/test_memory_routes.py
OPP-NB-001 — Tests R1 para memory_routes.py
============================================
Autorización: T1 firma explícita 2026-05-18 "Apruebo R1 OPP-NB-001"
Contrato base: bridge/autobuilder/opp_nb_021_memory_routes_contract_r0_bundle/

Strategy: mocks puros via set_dependencies(thoughts_store=mock).
- NO toca DB real.
- NO toca Supabase.
- NO toca secrets.
- NO requiere Railway.
- NO requiere red.
- Determinístico, rápido (<1s), CI-friendly.

Cobertura:
  MR_TEST_01: POST /thoughts — create success
  MR_TEST_02: POST /thoughts — 503 when store not initialized
  MR_TEST_03: POST /thoughts — 500 when store.create returns None
  MR_TEST_04: GET /thoughts — list success with filters
  MR_TEST_05: GET /thoughts — 503 when store not initialized
  MR_TEST_06: GET /thoughts/{id} — success
  MR_TEST_07: GET /thoughts/{id} — 404 not found
  MR_TEST_08: GET /thoughts/{id} — 503 when store not initialized
  MR_TEST_09: PATCH /thoughts/{id} — update success
  MR_TEST_10: PATCH /thoughts/{id} — 400 no fields
  MR_TEST_11: PATCH /thoughts/{id} — 404 not found
  MR_TEST_12: DELETE /thoughts/{id} — success
  MR_TEST_13: DELETE /thoughts/{id} — 404 not found
  MR_TEST_14: POST /thoughts/{id}/supersede — success
  MR_TEST_15: POST /thoughts/{id}/supersede — 404 not found
  MR_TEST_16: POST /search — hybrid search success
  MR_TEST_17: POST /search/semantic — semantic search success
  MR_TEST_18: GET /boot — boot sequence success
  MR_TEST_19: GET /stats — stats success
  MR_TEST_20: GET /boot — 503 when store not initialized
  MR_TEST_21: user_id defaults to "anonymous" (deuda documentada TTL 90d)
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Add kernel to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kernel.memory_routes import router, set_dependencies


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_thoughts_store():
    """Create a fully mocked thoughts store with all required methods."""
    store = AsyncMock()
    store.create = AsyncMock(return_value={
        "id": "thought-001",
        "user_id": "anonymous",
        "layer": "episodic",
        "content": "Test thought content",
        "summary": "Test summary",
        "tags": ["test"],
        "importance": 5,
        "project": None,
    })
    store.list_thoughts = AsyncMock(return_value=[
        {"id": "thought-001", "layer": "episodic", "content": "First"},
        {"id": "thought-002", "layer": "semantic", "content": "Second"},
    ])
    store.get = AsyncMock(return_value={
        "id": "thought-001",
        "user_id": "anonymous",
        "layer": "episodic",
        "content": "Test thought content",
    })
    store.update = AsyncMock(return_value={
        "id": "thought-001",
        "content": "Updated content",
    })
    store.delete = AsyncMock(return_value=True)
    store.supersede = AsyncMock(return_value={
        "id": "thought-002",
        "content": "New superseding content",
    })
    store.hybrid_search = AsyncMock(return_value=[
        {"id": "thought-001", "score": 0.95, "content": "Matched"},
    ])
    store.semantic_search = AsyncMock(return_value=[
        {"id": "thought-001", "score": 0.92, "content": "Semantic match"},
    ])
    store.boot_sequence = AsyncMock(return_value=[
        {"id": "thought-001", "layer": "procedural", "content": "Boot memory 1"},
        {"id": "thought-002", "layer": "semantic", "content": "Boot memory 2"},
        {"id": "thought-003", "layer": "episodic", "content": "Boot memory 3"},
    ])
    store.get_stats = AsyncMock(return_value={
        "total": 42,
        "by_layer": {"episodic": 20, "semantic": 15, "procedural": 7},
    })
    return store


@pytest.fixture
def client(mock_thoughts_store):
    """Create a test client with mocked dependencies."""
    app = FastAPI()
    app.include_router(router)
    set_dependencies(thoughts_store=mock_thoughts_store)
    yield TestClient(app)
    # Cleanup: reset to None to avoid leaking between tests
    set_dependencies(thoughts_store=None)


@pytest.fixture
def client_no_store():
    """Create a test client WITHOUT thoughts_store (simulates uninitialized)."""
    app = FastAPI()
    app.include_router(router)
    set_dependencies(thoughts_store=None)
    return TestClient(app)


# ── MR_TEST_01: POST /thoughts — create success ──────────────────────────────

def test_create_thought_success(client, mock_thoughts_store):
    """MR_TEST_01: Creating a thought returns 200 with thought data."""
    response = client.post("/v1/memory/thoughts", json={
        "layer": "episodic",
        "content": "This is a test thought",
        "importance": 7,
        "tags": ["test", "r1"],
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert data["thought"]["id"] == "thought-001"
    mock_thoughts_store.create.assert_called_once()


# ── MR_TEST_02: POST /thoughts — 503 when store not initialized ──────────────

def test_create_thought_503_no_store(client_no_store):
    """MR_TEST_02: 503 when thoughts store is not initialized."""
    response = client_no_store.post("/v1/memory/thoughts", json={
        "layer": "episodic",
        "content": "This should fail",
    })
    assert response.status_code == 503


# ── MR_TEST_03: POST /thoughts — 500 when store.create returns None ──────────

def test_create_thought_500_on_failure(client, mock_thoughts_store):
    """MR_TEST_03: 500 when store.create returns None."""
    mock_thoughts_store.create = AsyncMock(return_value=None)
    response = client.post("/v1/memory/thoughts", json={
        "layer": "semantic",
        "content": "This will fail internally",
    })
    assert response.status_code == 500


# ── MR_TEST_04: GET /thoughts — list success with filters ────────────────────

def test_list_thoughts_success(client, mock_thoughts_store):
    """MR_TEST_04: List thoughts returns filtered results."""
    response = client.get("/v1/memory/thoughts", params={
        "layer": "episodic",
        "limit": 10,
    })
    assert response.status_code == 200
    data = response.json()
    assert "thoughts" in data
    assert data["count"] == 2
    mock_thoughts_store.list_thoughts.assert_called_once()


# ── MR_TEST_05: GET /thoughts — 503 when store not initialized ───────────────

def test_list_thoughts_503_no_store(client_no_store):
    """MR_TEST_05: 503 when thoughts store is not initialized."""
    response = client_no_store.get("/v1/memory/thoughts")
    assert response.status_code == 503


# ── MR_TEST_06: GET /thoughts/{id} — success ────────────────────────────────

def test_get_thought_success(client, mock_thoughts_store):
    """MR_TEST_06: Get single thought by ID returns 200."""
    response = client.get("/v1/memory/thoughts/thought-001")
    assert response.status_code == 200
    data = response.json()
    assert data["thought"]["id"] == "thought-001"
    mock_thoughts_store.get.assert_called_once_with("thought-001")


# ── MR_TEST_07: GET /thoughts/{id} — 404 not found ──────────────────────────

def test_get_thought_404(client, mock_thoughts_store):
    """MR_TEST_07: 404 when thought not found."""
    mock_thoughts_store.get = AsyncMock(return_value=None)
    response = client.get("/v1/memory/thoughts/nonexistent")
    assert response.status_code == 404


# ── MR_TEST_08: GET /thoughts/{id} — 503 when store not initialized ──────────

def test_get_thought_503_no_store(client_no_store):
    """MR_TEST_08: 503 when thoughts store is not initialized."""
    response = client_no_store.get("/v1/memory/thoughts/thought-001")
    assert response.status_code == 503


# ── MR_TEST_09: PATCH /thoughts/{id} — update success ───────────────────────

def test_update_thought_success(client, mock_thoughts_store):
    """MR_TEST_09: Update thought returns 200 with updated data."""
    response = client.patch("/v1/memory/thoughts/thought-001", json={
        "content": "Updated content",
        "importance": 8,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "updated"
    mock_thoughts_store.update.assert_called_once()


# ── MR_TEST_10: PATCH /thoughts/{id} — 400 no fields ────────────────────────

def test_update_thought_400_no_fields(client):
    """MR_TEST_10: 400 when no fields provided for update."""
    response = client.patch("/v1/memory/thoughts/thought-001", json={})
    assert response.status_code == 400


# ── MR_TEST_11: PATCH /thoughts/{id} — 404 not found ────────────────────────

def test_update_thought_404(client, mock_thoughts_store):
    """MR_TEST_11: 404 when thought not found for update."""
    mock_thoughts_store.update = AsyncMock(return_value=None)
    response = client.patch("/v1/memory/thoughts/thought-001", json={
        "content": "Will not update",
    })
    assert response.status_code == 404


# ── MR_TEST_12: DELETE /thoughts/{id} — success ─────────────────────────────

def test_delete_thought_success(client, mock_thoughts_store):
    """MR_TEST_12: Delete thought returns 200."""
    response = client.delete("/v1/memory/thoughts/thought-001")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"
    assert data["id"] == "thought-001"


# ── MR_TEST_13: DELETE /thoughts/{id} — 404 not found ────────────────────────

def test_delete_thought_404(client, mock_thoughts_store):
    """MR_TEST_13: 404 when thought not found for delete."""
    mock_thoughts_store.delete = AsyncMock(return_value=False)
    response = client.delete("/v1/memory/thoughts/thought-001")
    assert response.status_code == 404


# ── MR_TEST_14: POST /thoughts/{id}/supersede — success ─────────────────────

def test_supersede_thought_success(client, mock_thoughts_store):
    """MR_TEST_14: Supersede thought returns 200 with new thought."""
    response = client.post("/v1/memory/thoughts/thought-001/supersede", json={
        "new_content": "This supersedes the old thought",
        "new_summary": "Superseded",
        "new_tags": ["v2"],
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "superseded"
    assert data["old_id"] == "thought-001"
    assert data["new_thought"]["id"] == "thought-002"


# ── MR_TEST_15: POST /thoughts/{id}/supersede — 404 not found ───────────────

def test_supersede_thought_404(client, mock_thoughts_store):
    """MR_TEST_15: 404 when original thought not found for supersede."""
    mock_thoughts_store.supersede = AsyncMock(return_value=None)
    response = client.post("/v1/memory/thoughts/thought-001/supersede", json={
        "new_content": "Will not supersede",
    })
    assert response.status_code == 404


# ── MR_TEST_16: POST /search — hybrid search success ────────────────────────

def test_hybrid_search_success(client, mock_thoughts_store):
    """MR_TEST_16: Hybrid search returns results."""
    response = client.post("/v1/memory/search", json={
        "query": "test query",
        "limit": 5,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["query"] == "test query"
    assert len(data["results"]) == 1


# ── MR_TEST_17: POST /search/semantic — semantic search success ──────────────

def test_semantic_search_success(client, mock_thoughts_store):
    """MR_TEST_17: Semantic search returns results."""
    response = client.post("/v1/memory/search/semantic", json={
        "query": "semantic test",
        "layer": "episodic",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["query"] == "semantic test"


# ── MR_TEST_18: GET /boot — boot sequence success ───────────────────────────

def test_boot_sequence_success(client, mock_thoughts_store):
    """MR_TEST_18: Boot sequence returns layered memories."""
    response = client.get("/v1/memory/boot", params={
        "procedural_limit": 3,
        "semantic_limit": 3,
        "episodic_limit": 5,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    assert "layers" in data
    assert data["layers"]["procedural"] == 1
    assert data["layers"]["semantic"] == 1
    assert data["layers"]["episodic"] == 1


# ── MR_TEST_19: GET /stats — stats success ──────────────────────────────────

def test_memory_stats_success(client, mock_thoughts_store):
    """MR_TEST_19: Stats returns aggregated data."""
    response = client.get("/v1/memory/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["stats"]["total"] == 42
    assert "by_layer" in data["stats"]


# ── MR_TEST_20: GET /boot — 503 when store not initialized ──────────────────

def test_boot_503_no_store(client_no_store):
    """MR_TEST_20: 503 when thoughts store is not initialized."""
    response = client_no_store.get("/v1/memory/boot")
    assert response.status_code == 503


# ── MR_TEST_21: user_id defaults to "anonymous" ─────────────────────────────

def test_user_id_defaults_anonymous(client, mock_thoughts_store):
    """MR_TEST_21: Validates that user_id defaults to 'anonymous'.
    
    NOTE: This is documented deuda técnica with TTL 90 days (decision T1 2026-05-18).
    The system is monousuario. When multi-user is implemented, these assertions
    should be updated to reflect the new auth behavior.
    """
    # GET /thoughts without user_id param
    response = client.get("/v1/memory/thoughts")
    assert response.status_code == 200
    call_args = mock_thoughts_store.list_thoughts.call_args
    assert call_args.kwargs.get("user_id") == "anonymous"
    
    # GET /stats without user_id param  
    response = client.get("/v1/memory/stats")
    assert response.status_code == 200
    mock_thoughts_store.get_stats.assert_called_with("anonymous")
    
    # GET /boot without user_id param
    mock_thoughts_store.get_stats.reset_mock()
    response = client.get("/v1/memory/boot")
    assert response.status_code == 200
    boot_call = mock_thoughts_store.boot_sequence.call_args
    assert boot_call.kwargs.get("user_id") == "anonymous"
