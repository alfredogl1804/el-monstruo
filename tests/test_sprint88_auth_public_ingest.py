"""Tests Sprint 88 — Tarea 3.A.1: middleware bypass para /v1/traffic/ingest.

Verifica que:
- POST /v1/traffic/ingest pasa sin API key (bypass).
- GET /v1/traffic/summary/{id} sigue requiriendo API key.
- POST /v1/e2e/run sigue requiriendo API key.
- DELETE /v1/traffic/ingest NO bypassea (solo POST).
- Path no exacto bajo /v1/traffic/* (ej /v1/traffic/ingest/extra) NO bypassea.

DSC-G-008: estas pruebas codifican el contrato del bypass para evitar regresión
silenciosa por drift futuro.
"""
from __future__ import annotations

import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from kernel.auth import APIKeyAuthMiddleware, PUBLIC_INGEST_PATHS


@pytest.fixture
def app_with_auth(monkeypatch):
    monkeypatch.setenv("MONSTRUO_API_KEY", "test-key-sprint88")
    app = FastAPI()
    app.add_middleware(APIKeyAuthMiddleware)

    @app.post("/v1/traffic/ingest")
    async def traffic_ingest():
        return {"ok": True, "endpoint": "ingest"}

    @app.get("/v1/traffic/summary/{run_id}")
    async def traffic_summary(run_id: str):
        return {"ok": True, "run_id": run_id}

    @app.post("/v1/e2e/run")
    async def e2e_run():
        return {"ok": True, "endpoint": "run"}

    @app.delete("/v1/traffic/ingest")
    async def traffic_ingest_delete():
        return {"ok": True}

    @app.post("/v1/traffic/ingest/extra")
    async def traffic_ingest_extra():
        return {"ok": True}

    return TestClient(app)


def test_public_ingest_paths_set_includes_traffic_ingest():
    """El whitelist debe contener exactamente /v1/traffic/ingest."""
    assert "/v1/traffic/ingest" in PUBLIC_INGEST_PATHS


def test_post_traffic_ingest_bypasses_auth(app_with_auth):
    """POST /v1/traffic/ingest sin X-API-Key debe pasar (bypass)."""
    response = app_with_auth.post("/v1/traffic/ingest", json={"event": "page_view"})
    assert response.status_code == 200
    assert response.json() == {"ok": True, "endpoint": "ingest"}


def test_post_traffic_ingest_with_invalid_key_still_passes(app_with_auth):
    """POST /v1/traffic/ingest con key invalida tambien pasa (bypass total)."""
    response = app_with_auth.post(
        "/v1/traffic/ingest",
        json={"event": "page_view"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 200


def test_get_traffic_summary_requires_auth(app_with_auth):
    """GET /v1/traffic/summary/{run_id} sin key debe rechazarse (lectura privada)."""
    response = app_with_auth.get("/v1/traffic/summary/abc-123")
    assert response.status_code == 401
    body = response.json()
    assert "Missing API key" in body.get("detail", "")


def test_get_traffic_summary_with_valid_key_works(app_with_auth):
    """GET /v1/traffic/summary/{run_id} con key valida funciona."""
    response = app_with_auth.get(
        "/v1/traffic/summary/abc-123",
        headers={"X-API-Key": "test-key-sprint88"},
    )
    assert response.status_code == 200


def test_post_e2e_run_requires_auth(app_with_auth):
    """POST /v1/e2e/run sin key debe rechazarse (no esta en whitelist)."""
    response = app_with_auth.post("/v1/e2e/run", json={"frase_input": "test"})
    assert response.status_code == 401


def test_delete_traffic_ingest_not_bypassed(app_with_auth):
    """DELETE /v1/traffic/ingest NO debe bypass (solo POST)."""
    response = app_with_auth.delete("/v1/traffic/ingest")
    assert response.status_code == 401


def test_traffic_ingest_subpath_not_bypassed(app_with_auth):
    """POST /v1/traffic/ingest/extra NO debe bypass (exact-match only)."""
    response = app_with_auth.post("/v1/traffic/ingest/extra", json={})
    assert response.status_code == 401


def test_health_still_public(app_with_auth):
    """/health debe seguir siendo publico (no requiere bypass nuevo)."""
    # Endpoint /health no fue declarado en este app, pero el middleware igual deberia
    # responder 404 (no 401). Si responde 401, hay regresion.
    response = app_with_auth.get("/health")
    assert response.status_code in (200, 404)
    # Importante: NO debe ser 401/403/503.
    assert response.status_code not in (401, 403, 503)
