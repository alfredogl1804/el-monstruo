"""
Tests del Sprint Memento Bloque 3 — endpoint POST /v1/memento/validate.

Cubre:
    - 401 sin API key / con key inválida
    - 503 si MONSTRUO_API_KEY no configurada
    - 503 si validator no inicializado
    - 200 con request válido + ok
    - 200 con discrepancy detectada (incidente "Falso Positivo TiDB")
    - 200 con unknown_operation (fallo blando, no excepción)
    - 422 con body malformado / faltando campos requeridos
    - persistencia: insert se llamó con shape correcto
    - persistencia falla → endpoint sigue respondiendo con persistence_failed=true
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from kernel.memento.models import CriticalOperation, SourceOfTruth
from kernel.memento.validator import MementoValidator
from kernel.memento_routes import memento_router

FIXTURE_PATH = "tests/fixtures/credentials_md_sample.md"
TEST_API_KEY = "test_monstruo_api_key_b3_secret"


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    """API key + repo root para todos los tests."""
    repo_root = Path(__file__).resolve().parent.parent
    monkeypatch.setenv("MONSTRUO_API_KEY", TEST_API_KEY)
    monkeypatch.setenv("MEMENTO_REPO_ROOT", str(repo_root))


@pytest.fixture
def critical_op_sql() -> CriticalOperation:
    return CriticalOperation(
        id="sql_against_production",
        nombre="SQL Against Production",
        descripcion="Test op",
        triggers=["host_matches_production_pattern"],
        requires_validation=True,
        requires_confirmation="pre_flight_credentials_md",
        source_of_truth_ids=["ticketlike_credentials"],
        activo=True,
    )


@pytest.fixture
def source_ticketlike() -> SourceOfTruth:
    return SourceOfTruth(
        id="ticketlike_credentials",
        nombre="Ticketlike Credentials",
        descripcion="Test source",
        source_type="repo_file",
        location=FIXTURE_PATH,
        parser_id="credentials_md_v1",
        cache_ttl_seconds=60,
    )


class MockDb:
    """
    Mock thread-safe del SupabaseClient.
    Captura cada insert para inspección.
    """
    def __init__(self, fail_inserts: bool = False) -> None:
        self.inserts: List[Dict[str, Any]] = []
        self.fail_inserts = fail_inserts
        self.connected = True

    async def insert(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self.fail_inserts:
            raise RuntimeError("supabase_insert_simulated_failure")
        self.inserts.append({"table": table, "data": data})
        return {"id": len(self.inserts), **data}


def _build_app(
    *,
    validator: Optional[MementoValidator],
    db: Optional[MockDb] = None,
) -> FastAPI:
    """Construye una app FastAPI mínima con el router montado."""
    app = FastAPI()
    app.state.memento_validator = validator
    app.state.db = db
    app.include_router(memento_router, prefix="/v1/memento")
    return app


@pytest.fixture
def validator(critical_op_sql, source_ticketlike) -> MementoValidator:
    return MementoValidator(
        critical_operations={critical_op_sql.id: critical_op_sql},
        sources_of_truth={source_ticketlike.id: source_ticketlike},
    )


@pytest.fixture
def app_with_db(validator) -> tuple[FastAPI, MockDb]:
    db = MockDb()
    return _build_app(validator=validator, db=db), db


@pytest.fixture
def client(app_with_db) -> TestClient:
    app, _ = app_with_db
    return TestClient(app)


# ===========================================================================
# Tests de auth
# ===========================================================================

class TestAuth:
    def test_missing_api_key_returns_401(self, client):
        r = client.post("/v1/memento/validate", json={
            "hilo_id": "hilo_test",
            "operation": "sql_against_production",
            "context_used": {"host": "x"},
        })
        assert r.status_code == 401
        assert "memento_api_key_missing" in r.text

    def test_invalid_api_key_returns_401(self, client):
        r = client.post(
            "/v1/memento/validate",
            json={"hilo_id": "h", "operation": "sql_against_production", "context_used": {}},
            headers={"X-API-Key": "wrong-key"},
        )
        assert r.status_code == 401
        assert "memento_api_key_invalid" in r.text

    def test_api_key_via_authorization_bearer(self, client):
        r = client.post(
            "/v1/memento/validate",
            json={
                "hilo_id": "h",
                "operation": "sql_against_production",
                "context_used": {"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
            },
            headers={"Authorization": f"Bearer {TEST_API_KEY}"},
        )
        assert r.status_code == 200

    def test_unconfigured_api_key_returns_503(self, validator, monkeypatch):
        monkeypatch.delenv("MONSTRUO_API_KEY", raising=False)
        app = _build_app(validator=validator, db=MockDb())
        c = TestClient(app)
        r = c.post(
            "/v1/memento/validate",
            json={"hilo_id": "h", "operation": "sql_against_production", "context_used": {}},
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert r.status_code == 503
        assert "memento_api_key_no_configurada" in r.text


# ===========================================================================
# Tests del endpoint
# ===========================================================================

class TestEndpoint:
    def test_returns_503_if_validator_not_initialized(self, monkeypatch):
        # Nota: el helper require_memento_admin_key valida ANTES que el validator,
        # así que igual mandamos la API key correcta.
        app = _build_app(validator=None, db=MockDb())
        c = TestClient(app)
        r = c.post(
            "/v1/memento/validate",
            json={"hilo_id": "h", "operation": "x", "context_used": {}},
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert r.status_code == 503
        assert "memento_validator_not_initialized" in r.text

    def test_invalid_json_body_returns_422(self, client):
        r = client.post(
            "/v1/memento/validate",
            content=b"not json",
            headers={"X-API-Key": TEST_API_KEY, "Content-Type": "application/json"},
        )
        assert r.status_code == 422
        assert "memento_body_not_json" in r.text

    def test_missing_required_fields_returns_422(self, client):
        r = client.post(
            "/v1/memento/validate",
            json={"hilo_id": "h"},  # falta operation y context_used
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert r.status_code == 422
        assert "memento_body_invalid" in r.text

    def test_empty_hilo_id_returns_422(self, client):
        r = client.post(
            "/v1/memento/validate",
            json={"hilo_id": "", "operation": "sql_against_production", "context_used": {}},
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert r.status_code == 422
        assert "memento_body_invalid" in r.text

    def test_valid_request_ok(self, client):
        r = client.post(
            "/v1/memento/validate",
            json={
                "hilo_id": "hilo_test",
                "operation": "sql_against_production",
                "context_used": {
                    "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
                    "user": "37Hy7adB53QmFW4.root",
                },
                "intent_summary": "Run smoke test",
            },
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["proceed"] is True
        assert body["validation_status"] == "ok"
        assert body["discrepancy"] is None
        assert body["validation_id"].startswith("mv_")
        assert body["persistence_failed"] is False

    def test_discrepancy_detected_returns_200_with_proceed_false(self, client):
        # Reproduce el incidente "Falso Positivo TiDB" del 2026-05-04
        r = client.post(
            "/v1/memento/validate",
            json={
                "hilo_id": "hilo_manus_ticketlike",
                "operation": "sql_against_production",
                "context_used": {
                    "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",  # FANTASMA
                },
                "intent_summary": "Run E2E test post Stripe rotation",
            },
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["proceed"] is False
        assert body["validation_status"] == "discrepancy_detected"
        assert body["discrepancy"] is not None
        assert body["discrepancy"]["field"] == "host"
        assert "gateway01" in str(body["discrepancy"]["context_used"])
        assert "gateway05" in str(body["discrepancy"]["source_of_truth"])
        assert "context_stale_or_contaminated" in (body["remediation"] or "")

    def test_unknown_operation_returns_200_with_proceed_false(self, client):
        r = client.post(
            "/v1/memento/validate",
            json={
                "hilo_id": "h",
                "operation": "this_operation_does_not_exist",
                "context_used": {},
            },
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["proceed"] is False
        assert body["validation_status"] == "unknown_operation"
        assert "operation_not_in_catalog" in (body["remediation"] or "")


# ===========================================================================
# Tests de persistencia
# ===========================================================================

class TestPersistence:
    def test_insert_called_with_correct_shape(self, app_with_db):
        app, db = app_with_db
        c = TestClient(app)
        r = c.post(
            "/v1/memento/validate",
            json={
                "hilo_id": "hilo_test",
                "operation": "sql_against_production",
                "context_used": {"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
                "intent_summary": "smoke",
            },
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert r.status_code == 200
        assert len(db.inserts) == 1
        ins = db.inserts[0]
        assert ins["table"] == "memento_validations"
        data = ins["data"]
        # Campos del schema 017
        assert data["validation_id"].startswith("mv_")
        assert data["hilo_id"] == "hilo_test"
        assert data["operation"] == "sql_against_production"
        assert data["intent_summary"] == "smoke"
        assert data["validation_status"] == "ok"
        assert data["proceed"] is True
        assert data["discrepancy"] is None
        assert data["context_used"]["host"] == "gateway05.us-east-1.prod.aws.tidbcloud.com"
        assert "ts" in data
        assert "context_freshness_seconds" in data
        assert "remediation" in data
        assert "source_consulted" in data

    def test_discrepancy_persisted_with_full_detail(self, app_with_db):
        app, db = app_with_db
        c = TestClient(app)
        c.post(
            "/v1/memento/validate",
            json={
                "hilo_id": "hilo_manus_ticketlike",
                "operation": "sql_against_production",
                "context_used": {"host": "gateway01.us-east-1.prod.aws.tidbcloud.com"},
            },
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert len(db.inserts) == 1
        data = db.inserts[0]["data"]
        assert data["validation_status"] == "discrepancy_detected"
        assert data["proceed"] is False
        assert data["discrepancy"]["field"] == "host"
        assert "gateway01" in str(data["discrepancy"]["context_used"])

    def test_persistence_failure_does_not_block_response(self, validator):
        # DB que falla en TODOS los inserts
        broken_db = MockDb(fail_inserts=True)
        app = _build_app(validator=validator, db=broken_db)
        c = TestClient(app)
        r = c.post(
            "/v1/memento/validate",
            json={
                "hilo_id": "h",
                "operation": "sql_against_production",
                "context_used": {"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
            },
            headers={"X-API-Key": TEST_API_KEY},
        )
        # Endpoint sigue respondiendo 200 (Capa 7 Resiliencia)
        assert r.status_code == 200
        body = r.json()
        assert body["proceed"] is True
        assert body["persistence_failed"] is True
        # El insert intentó ocurrir pero no se capturó (failed)
        assert len(broken_db.inserts) == 0

    def test_no_db_does_not_block_response(self, validator):
        app = _build_app(validator=validator, db=None)
        c = TestClient(app)
        r = c.post(
            "/v1/memento/validate",
            json={
                "hilo_id": "h",
                "operation": "sql_against_production",
                "context_used": {"host": "gateway05.us-east-1.prod.aws.tidbcloud.com"},
            },
            headers={"X-API-Key": TEST_API_KEY},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["proceed"] is True
        assert body["persistence_failed"] is True


# ===========================================================================
# Test integración opt-in (real Supabase) — solo si MEMENTO_INTEGRATION_TESTS=true
# ===========================================================================

@pytest.mark.skipif(
    os.environ.get("MEMENTO_INTEGRATION_TESTS", "").lower() != "true",
    reason="Requiere MEMENTO_INTEGRATION_TESTS=true + SUPABASE_DB_URL configurado",
)
class TestIntegrationReal:
    def test_real_insert_then_select(self, app_with_db):
        # Este test SOLO corre si el env flag está activo.
        # Reemplazaría el MockDb por SupabaseClient real.
        # En CI normal NO se ejecuta.
        pass
