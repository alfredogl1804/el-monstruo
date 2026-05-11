"""tests/test_cowork_routes.py — T8 endpoint /v1/cowork/memento/validate."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from kernel.cowork_routes import cowork_router


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("MONSTRUO_API_KEY", "test-key-123")
    app = FastAPI()
    app.include_router(cowork_router, prefix="/v1/cowork")
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


# ---- Health (sin auth) ----

def test_health_sin_auth(client):
    r = client.get("/v1/cowork/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "memento/validate" in body["endpoints"][0]


# ---- Auth ----

def test_validate_sin_api_key_401(client):
    r = client.post("/v1/cowork/memento/validate", json={"hilo_solicitante": "test"})
    assert r.status_code == 401


def test_validate_api_key_invalida_401(client):
    r = client.post(
        "/v1/cowork/memento/validate",
        json={"hilo_solicitante": "test"},
        headers={"X-API-Key": "wrong"},
    )
    assert r.status_code == 401


def test_validate_sin_monstruo_api_key_503(monkeypatch):
    monkeypatch.delenv("MONSTRUO_API_KEY", raising=False)
    app = FastAPI()
    app.include_router(cowork_router, prefix="/v1/cowork")
    client = TestClient(app)
    r = client.post(
        "/v1/cowork/memento/validate",
        json={"hilo_solicitante": "test"},
        headers={"X-API-Key": "anything"},
    )
    assert r.status_code == 503


# ---- Logica binaria fresco / no-fresco ----

def test_validate_sin_sesiones_no_fresco(client):
    with patch("kernel.cowork_routes.SessionMemoryStore") as MockStore:
        MockStore.return_value.read_recent.return_value = []
        r = client.post(
            "/v1/cowork/memento/validate",
            json={"hilo_solicitante": "hilo_test"},
            headers={"X-API-Key": "test-key-123"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["cowork_fresco"] is False
    assert "No hay sesiones" in body["razon"]
    assert body["drift_action"] == "force_preflight"


def test_validate_pre_flight_ok_fresco(client):
    sesion_fresca = {
        "id": "abc",
        "fecha_inicio": datetime.now(timezone.utc).isoformat(),
        "sprint_activo": "TEST-001",
        "pre_flight_ejecutado": True,
        "commits_productivos": 3,
        "turnos_totales": 2,
        "violaciones_detectadas": [],
        "kernel_version": "0.84.8",
        "embrion_ultimo_latido": "2026-05-11T08:00:00Z",
    }
    with patch("kernel.cowork_routes.SessionMemoryStore") as MockStore:
        MockStore.return_value.read_recent.return_value = [sesion_fresca]
        r = client.post(
            "/v1/cowork/memento/validate",
            json={"hilo_solicitante": "hilo_test"},
            headers={"X-API-Key": "test-key-123"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["cowork_fresco"] is True
    assert body["drift_action"] == "no_op"
    assert body["metricas"]["pre_flight_ejecutado"] is True
    assert body["ultima_sesion"]["sprint_activo"] == "TEST-001"


def test_validate_sin_pre_flight_no_fresco(client):
    sesion_sin_pf = {
        "id": "xyz",
        "fecha_inicio": datetime.now(timezone.utc).isoformat(),
        "pre_flight_ejecutado": False,
        "commits_productivos": 0,
        "turnos_totales": 1,
        "violaciones_detectadas": [],
    }
    with patch("kernel.cowork_routes.SessionMemoryStore") as MockStore:
        MockStore.return_value.read_recent.return_value = [sesion_sin_pf]
        r = client.post(
            "/v1/cowork/memento/validate",
            json={"hilo_solicitante": "hilo_test"},
            headers={"X-API-Key": "test-key-123"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["cowork_fresco"] is False
    assert "NO ejecutado" in body["razon"]


def test_validate_demasiadas_violaciones_no_fresco(client):
    sesion_violatoria = {
        "id": "v1",
        "fecha_inicio": datetime.now(timezone.utc).isoformat(),
        "pre_flight_ejecutado": True,
        "commits_productivos": 1,
        "turnos_totales": 5,
        "violaciones_detectadas": ["v1", "v2", "v3", "v4"],
    }
    with patch("kernel.cowork_routes.SessionMemoryStore") as MockStore:
        MockStore.return_value.read_recent.return_value = [sesion_violatoria]
        r = client.post(
            "/v1/cowork/memento/validate",
            json={"hilo_solicitante": "hilo_test"},
            headers={"X-API-Key": "test-key-123"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["cowork_fresco"] is False
    assert body["drift_action"] in ("reinject_rules", "hard_halt")


def test_validate_request_sin_hilo_solicitante_422(client):
    r = client.post(
        "/v1/cowork/memento/validate",
        json={},
        headers={"X-API-Key": "test-key-123"},
    )
    assert r.status_code == 422  # validation error pydantic


def test_validate_acepta_razon_opcional(client):
    sesion_fresca = {
        "id": "abc",
        "fecha_inicio": datetime.now(timezone.utc).isoformat(),
        "pre_flight_ejecutado": True,
        "commits_productivos": 1,
        "turnos_totales": 1,
        "violaciones_detectadas": [],
    }
    with patch("kernel.cowork_routes.SessionMemoryStore") as MockStore:
        MockStore.return_value.read_recent.return_value = [sesion_fresca]
        r = client.post(
            "/v1/cowork/memento/validate",
            json={"hilo_solicitante": "hilo_test", "razon": "Antes de aceptar spec X"},
            headers={"X-API-Key": "test-key-123"},
        )
    assert r.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
