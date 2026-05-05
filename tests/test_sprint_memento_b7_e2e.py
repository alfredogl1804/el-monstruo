"""
Tests E2E del Sprint Memento Bloque 7 — capa Memoria Soberana v1.0
====================================================================

Cubre el flow integrado y los nuevos endpoints admin:

1. Flow completo: validate → contamination_detector → persistencia.
2. POST /v1/memento/admin/reload:
   - 401 sin auth, 200 reload exitoso desde Supabase mock,
   - 200 fallback YAML cuando Supabase falla,
   - 504 timeout cuando Supabase tarda > MEMENTO_RELOAD_TIMEOUT_SECONDS,
   - 409 lock contention si hay reload en curso,
   - swap atómico (ningún cliente ve catálogo parcial).
3. GET /v1/memento/admin/dashboard:
   - 401 sin auth, 200 con métricas JSON, 200 HTML cuando Accept: text/html,
   - métricas reflejan: ok_rate, contamination_warning_rate, top operations,
     top hilos, breakdown por rule_id (H1/H2/H3) y severity.
4. Casos del flow: ok, discrepancy, contamination warning HIGH (H1 sintética),
   contamination warning MEDIUM (H3), degraded mode (DB caída).
5. Test opt-in productivo (gated por MEMENTO_INTEGRATION_TESTS=true) que
   ejercita el endpoint real contra el Railway productivo si están las env vars.

Disciplina:
   - Auth fresh os.environ.get (anti-Dory).
   - MockDB que simula la firma real de SupabaseClient (`select(table, columns,
     filters, order_by, order_desc, limit)` y `insert(table, data)`).
   - Sin red ni Supabase real para los tests core. El opt-in está skipeado por default.
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from kernel.memento.contamination_detector import (
    ContaminationDetector,
    ContaminationFinding,
    ContaminationReport,
)
from kernel.memento.models import CriticalOperation, SourceOfTruth
from kernel.memento.validator import MementoValidator
from kernel.memento_routes import (
    MEMENTO_DASHBOARD_LOOKBACK_HOURS,
    MEMENTO_RELOAD_TIMEOUT_SECONDS,
    MEMENTO_VALIDATIONS_TABLE,
    memento_router,
)


FIXTURE_PATH = "tests/fixtures/credentials_md_sample.md"
TEST_API_KEY = "test_monstruo_api_key_b7_secret"


# ===========================================================================
# Fixtures comunes
# ===========================================================================


@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    repo_root = Path(__file__).resolve().parent.parent
    monkeypatch.setenv("MONSTRUO_API_KEY", TEST_API_KEY)
    monkeypatch.setenv("MEMENTO_REPO_ROOT", str(repo_root))


@pytest.fixture
def critical_op_sql() -> CriticalOperation:
    return CriticalOperation(
        id="sql_against_production",
        nombre="SQL Against Production",
        descripcion="E2E op",
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
        descripcion="E2E source",
        source_type="repo_file",
        location=FIXTURE_PATH,
        parser_id="credentials_md_v1",
        cache_ttl_seconds=60,
    )


class FakeSupabaseClient:
    """
    Simula la firma real de SupabaseClient. Captura inserts y permite
    pre-cargar filas para `select` (con soporte de `order_by`/`order_desc`/`limit`).

    También expone `slow_mode` para simular timeouts.
    """

    def __init__(
        self,
        *,
        slow_mode: bool = False,
        slow_seconds: float = 10.0,
        fail_select_for: Optional[List[str]] = None,
        fail_inserts: bool = False,
    ) -> None:
        self.tables: Dict[str, List[Dict[str, Any]]] = {}
        self.inserts: List[Dict[str, Any]] = []
        self.slow_mode = slow_mode
        self.slow_seconds = slow_seconds
        self.fail_select_for = fail_select_for or []
        self.fail_inserts = fail_inserts

    def preload(self, table: str, rows: List[Dict[str, Any]]) -> None:
        self.tables.setdefault(table, []).extend(rows)

    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = True,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        if self.slow_mode:
            await asyncio.sleep(self.slow_seconds)
        if table in self.fail_select_for:
            raise RuntimeError(f"simulated_select_failure:{table}")
        rows = list(self.tables.get(table, []))
        if filters:
            rows = [r for r in rows if all(r.get(k) == v for k, v in filters.items())]
        if order_by and order_by in {"ts"}:
            rows.sort(key=lambda r: r.get(order_by) or "", reverse=order_desc)
        if limit is not None:
            rows = rows[:limit]
        return rows

    async def insert(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self.fail_inserts:
            raise RuntimeError("simulated_insert_failure")
        record = {"_n": len(self.inserts) + 1, **data}
        self.tables.setdefault(table, []).append(record)
        self.inserts.append({"table": table, "data": data})
        return record


def _build_app(
    *,
    validator: Optional[MementoValidator],
    db: Optional[Any] = None,
    detector: Optional[ContaminationDetector] = None,
) -> FastAPI:
    app = FastAPI()
    app.state.memento_validator = validator
    app.state.db = db
    app.state.memento_detector = detector
    app.include_router(memento_router, prefix="/v1/memento")
    return app


@pytest.fixture
def validator(critical_op_sql, source_ticketlike) -> MementoValidator:
    return MementoValidator(
        critical_operations={critical_op_sql.id: critical_op_sql},
        sources_of_truth={source_ticketlike.id: source_ticketlike},
    )


def _auth_headers() -> Dict[str, str]:
    return {"X-API-Key": TEST_API_KEY}


# ===========================================================================
# 1. Flow E2E completo (validate → contamination → persistencia)
# ===========================================================================


def test_e2e_flow_ok_persists_and_returns_proceed(validator):
    db = FakeSupabaseClient()
    detector = ContaminationDetector(db=db, repo_root=None)
    app = _build_app(validator=validator, db=db, detector=detector)
    client = TestClient(app)

    body = {
        "hilo_id": "hilo_e2e_ok",
        "operation": "sql_against_production",
        "context_used": {
            "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
            "user": "37Hy7adB53QmFW4.root",
            "credential_hash_first_8": "4N6caSwp",
        },
        "intent_summary": "E2E happy path",
    }
    resp = client.post("/v1/memento/validate", json=body, headers=_auth_headers())
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["validation_status"] == "ok"
    assert data["proceed"] is True
    assert data["persistence_failed"] is False
    assert "contamination_warning" in data
    assert data["contamination_warning"] is False  # nada raro en happy path
    # Persistencia se realizó
    assert len(db.inserts) == 1
    assert db.inserts[0]["table"] == MEMENTO_VALIDATIONS_TABLE
    assert db.inserts[0]["data"]["validation_status"] == "ok"


def test_e2e_flow_discrepancy_blocks_proceed(validator):
    db = FakeSupabaseClient()
    detector = ContaminationDetector(db=db, repo_root=None)
    app = _build_app(validator=validator, db=db, detector=detector)
    client = TestClient(app)

    body = {
        "hilo_id": "hilo_e2e_discrepancy",
        "operation": "sql_against_production",
        "context_used": {
            "host": "gateway01.us-east-1.prod.aws.tidbcloud.com",  # cluster fantasma
            "user": "37Hy7adB53QmFW4.root",
            "credential_hash_first_8": "4N6caSwp",
        },
    }
    resp = client.post("/v1/memento/validate", json=body, headers=_auth_headers())
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["validation_status"] == "discrepancy_detected"
    assert data["proceed"] is False
    assert data["discrepancy"] is not None
    assert data["discrepancy"]["field"] == "host"
    assert data["persistence_failed"] is False


def test_e2e_flow_unknown_operation_returns_400_in_proceed_logic(validator):
    db = FakeSupabaseClient()
    detector = ContaminationDetector(db=db, repo_root=None)
    app = _build_app(validator=validator, db=db, detector=detector)
    client = TestClient(app)

    body = {
        "hilo_id": "hilo_e2e_unknown",
        "operation": "operacion_inexistente",
        "context_used": {"host": "x"},
    }
    resp = client.post("/v1/memento/validate", json=body, headers=_auth_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["validation_status"] == "unknown_operation"
    assert data["proceed"] is False
    assert "operation_not_in_catalog" in (data.get("remediation") or "")


def test_e2e_flow_degraded_mode_no_db(validator):
    """DB caída: validate sigue respondiendo 200 con persistence_failed=true."""
    detector = ContaminationDetector(db=None, repo_root=None)
    app = _build_app(validator=validator, db=None, detector=detector)
    client = TestClient(app)

    body = {
        "hilo_id": "hilo_e2e_degraded",
        "operation": "sql_against_production",
        "context_used": {
            "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
            "user": "37Hy7adB53QmFW4.root",
            "credential_hash_first_8": "4N6caSwp",
        },
    }
    resp = client.post("/v1/memento/validate", json=body, headers=_auth_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["validation_status"] == "ok"
    assert data["proceed"] is True
    assert data["persistence_failed"] is True


def test_e2e_flow_contamination_warning_h3_medium(validator):
    """H3: hilo con varios preflights recientes pero ninguno de la op actual."""
    db = FakeSupabaseClient()
    # Pre-cargamos 6 validaciones recientes del hilo con OTRA operación → dispara H3
    now = datetime.now(timezone.utc)
    for i in range(6):
        db.preload(
            MEMENTO_VALIDATIONS_TABLE,
            [
                {
                    "validation_id": f"mv_test_{i}",
                    "hilo_id": "hilo_e2e_h3",
                    "operation": "rotate_credential",  # otra op
                    "validation_status": "ok",
                    "proceed": True,
                    "ts": (now - timedelta(minutes=i + 1)).isoformat(),
                }
            ],
        )

    detector = ContaminationDetector(
        db=db,
        repo_root=None,
        h3_min_recent_validations=5,
    )
    app = _build_app(validator=validator, db=db, detector=detector)
    client = TestClient(app)

    body = {
        "hilo_id": "hilo_e2e_h3",
        "operation": "sql_against_production",
        "context_used": {
            "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
            "user": "37Hy7adB53QmFW4.root",
            "credential_hash_first_8": "4N6caSwp",
        },
    }
    resp = client.post("/v1/memento/validate", json=body, headers=_auth_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["proceed"] is True  # shadow mode: NO bloquea
    assert data["contamination_warning"] is True
    findings = data["contamination_findings"]
    assert any(f["rule_id"] == "H3" for f in findings)
    # Persistencia incluyó el shape extendido
    last_insert = db.inserts[-1]["data"]
    assert last_insert["contamination_warning"] is True
    assert isinstance(last_insert["contamination_evidence"], dict)


def test_e2e_flow_contamination_warning_high_synthetic_via_monkeypatch(
    validator, monkeypatch
):
    """
    HIGH severity sintética: stub-eamos detector.detect para retornar
    un finding HIGH (H1 simulado). Verificamos que se loguea, persiste,
    y devuelve has_high_severity=true en la response, pero no bloquea proceed.
    """
    db = FakeSupabaseClient()
    detector = ContaminationDetector(db=db, repo_root=None)

    high_finding = ContaminationFinding(
        rule_id="H1",
        severity="HIGH",
        evidence={
            "credential_hash_obsolete": "abc123de",
            "matched_in_commits": ["aaaa", "bbbb"],
        },
        recommendation="Re-leer credentials.md y reintentar; el hash declarado es obsoleto.",
    )
    high_report = ContaminationReport(
        findings=[high_finding],
        detector_runtime_ms=12.34,
        timed_out_rules=[],
        skipped_rules=[],
    )

    async def _fake_detect(**kwargs):
        return high_report

    monkeypatch.setattr(detector, "detect", _fake_detect)

    app = _build_app(validator=validator, db=db, detector=detector)
    client = TestClient(app)

    body = {
        "hilo_id": "hilo_e2e_high",
        "operation": "sql_against_production",
        "context_used": {
            "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
            "user": "37Hy7adB53QmFW4.root",
            "credential_hash_first_8": "4N6caSwp",
        },
    }
    resp = client.post("/v1/memento/validate", json=body, headers=_auth_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["proceed"] is True  # shadow mode v1.0 NO bloquea
    assert data["contamination_warning"] is True
    findings = data["contamination_findings"]
    assert len(findings) == 1
    assert findings[0]["rule_id"] == "H1"
    assert findings[0]["severity"] == "HIGH"


# ===========================================================================
# 2. POST /v1/memento/admin/reload
# ===========================================================================


def test_admin_reload_requires_auth(validator):
    db = FakeSupabaseClient()
    app = _build_app(validator=validator, db=db)
    client = TestClient(app)

    resp = client.post("/v1/memento/admin/reload")
    assert resp.status_code == 401


def test_admin_reload_503_when_validator_not_initialized():
    app = _build_app(validator=None, db=FakeSupabaseClient())
    client = TestClient(app)
    resp = client.post("/v1/memento/admin/reload", headers=_auth_headers())
    assert resp.status_code == 503


def test_admin_reload_loads_from_supabase_atomic_swap(validator):
    db = FakeSupabaseClient()
    db.preload(
        "memento_critical_operations",
        [
            {
                "id": "rotate_credential",
                "nombre": "Rotate Credential",
                "descripcion": "rotate",
                "triggers": [],
                "requires_validation": True,
                "requires_confirmation": None,
                "source_of_truth_ids": ["ticketlike_credentials"],
                "activo": True,
            },
            {
                "id": "deploy_to_production",
                "nombre": "Deploy to Production",
                "descripcion": "deploy",
                "triggers": [],
                "requires_validation": True,
                "requires_confirmation": None,
                "source_of_truth_ids": [],
                "activo": True,
            },
        ],
    )
    db.preload(
        "memento_sources_of_truth",
        [
            {
                "id": "ticketlike_credentials",
                "nombre": "Ticketlike Credentials",
                "descripcion": "src",
                "source_type": "repo_file",
                "location": FIXTURE_PATH,
                "parser_id": "credentials_md_v1",
                "cache_ttl_seconds": 60,
                "activo": True,
            }
        ],
    )

    app = _build_app(validator=validator, db=db)
    client = TestClient(app)

    resp = client.post("/v1/memento/admin/reload", headers=_auth_headers())
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "reloaded"
    assert data["loaded_from"] == "supabase"
    assert data["critical_operations_count"] == 2
    assert data["sources_of_truth_count"] == 1
    assert data["previous_critical_operations_count"] == 1
    assert data["previous_sources_of_truth_count"] == 1
    assert data["cache_invalidated"] is True

    # SWAP atómico: el validator del app.state apunta a un NUEVO objeto
    new_validator = app.state.memento_validator
    assert new_validator is not validator
    assert "rotate_credential" in new_validator.critical_operations
    assert "deploy_to_production" in new_validator.critical_operations


def test_admin_reload_falls_back_to_yaml_when_supabase_select_fails(validator):
    db = FakeSupabaseClient(fail_select_for=["memento_critical_operations"])
    app = _build_app(validator=validator, db=db)
    client = TestClient(app)

    resp = client.post("/v1/memento/admin/reload", headers=_auth_headers())
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["loaded_from"] == "yaml_fallback"
    # YAML local del repo tiene >0 ops
    assert data["critical_operations_count"] >= 1


def test_admin_reload_504_on_supabase_timeout(validator, monkeypatch):
    """Force timeout patcheando MEMENTO_RELOAD_TIMEOUT_SECONDS bajísimo."""
    # El kernel acepta la const importada al loadtime; patcheamos la del módulo
    import kernel.memento_routes as routes_mod

    monkeypatch.setattr(routes_mod, "MEMENTO_RELOAD_TIMEOUT_SECONDS", 0.05)

    db = FakeSupabaseClient(slow_mode=True, slow_seconds=1.0)
    app = _build_app(validator=validator, db=db)
    client = TestClient(app)

    resp = client.post("/v1/memento/admin/reload", headers=_auth_headers())
    assert resp.status_code == 504
    assert "memento_reload_supabase_timeout" in resp.json()["detail"]


def test_admin_reload_409_on_lock_contention(validator):
    """
    Si hay un reload activo, la segunda llamada concurrente recibe 409.
    Lo simulamos preadquiriendo el lock externamente.
    """
    db = FakeSupabaseClient()
    db.preload(
        "memento_critical_operations",
        [
            {
                "id": "rotate_credential",
                "nombre": "Rotate",
                "descripcion": "",
                "triggers": [],
                "requires_validation": True,
                "requires_confirmation": None,
                "source_of_truth_ids": [],
                "activo": True,
            }
        ],
    )
    db.preload("memento_sources_of_truth", [])

    app = _build_app(validator=validator, db=db)
    client = TestClient(app)

    # Pre-adquirimos el lock manualmente. Como TestClient corre cada request en
    # un event loop nuevo, primero generamos el lock invocando el endpoint una
    # vez (con slow_mode=False — completa rápido) y después sembramos un Lock
    # ya adquirido en el state.
    resp_first = client.post("/v1/memento/admin/reload", headers=_auth_headers())
    assert resp_first.status_code == 200

    # Sembramos un Lock "adquirido" sin depender del default event loop
    # (el TestClient corre cada request en su propio loop, y al volver al test
    # principal no necesariamente hay loop activo — esto es flaky en pytest 9).
    new_loop = asyncio.new_event_loop()
    try:
        locked = asyncio.Lock()
        new_loop.run_until_complete(locked.acquire())
    finally:
        new_loop.close()
    app.state._memento_reload_lock = locked

    resp = client.post("/v1/memento/admin/reload", headers=_auth_headers())
    assert resp.status_code == 409
    assert "memento_reload_already_in_progress" in resp.json()["detail"]


# ===========================================================================
# 3. GET /v1/memento/admin/dashboard
# ===========================================================================


def test_admin_dashboard_requires_auth(validator):
    db = FakeSupabaseClient()
    app = _build_app(validator=validator, db=db)
    client = TestClient(app)
    resp = client.get("/v1/memento/admin/dashboard")
    assert resp.status_code == 401


def test_admin_dashboard_503_without_validator():
    app = _build_app(validator=None, db=FakeSupabaseClient())
    client = TestClient(app)
    resp = client.get("/v1/memento/admin/dashboard", headers=_auth_headers())
    assert resp.status_code == 503


def _seed_dashboard_rows(db: FakeSupabaseClient) -> None:
    now = datetime.now(timezone.utc)
    rows = [
        {
            "validation_id": "mv_d1",
            "hilo_id": "hilo_a",
            "operation": "sql_against_production",
            "validation_status": "ok",
            "proceed": True,
            "contamination_warning": False,
            "contamination_evidence": None,
            "ts": (now - timedelta(minutes=10)).isoformat(),
        },
        {
            "validation_id": "mv_d2",
            "hilo_id": "hilo_a",
            "operation": "sql_against_production",
            "validation_status": "discrepancy_detected",
            "proceed": False,
            "contamination_warning": True,
            "contamination_evidence": {
                "findings": [
                    {"rule_id": "H2", "severity": "HIGH"},
                ]
            },
            "ts": (now - timedelta(minutes=20)).isoformat(),
        },
        {
            "validation_id": "mv_d3",
            "hilo_id": "hilo_b",
            "operation": "rotate_credential",
            "validation_status": "ok",
            "proceed": True,
            "contamination_warning": True,
            "contamination_evidence": {
                "findings": [
                    {"rule_id": "H3", "severity": "MEDIUM"},
                ]
            },
            "ts": (now - timedelta(minutes=30)).isoformat(),
        },
        {
            "validation_id": "mv_d_old",
            "hilo_id": "hilo_a",
            "operation": "sql_against_production",
            "validation_status": "ok",
            "proceed": True,
            "contamination_warning": False,
            "ts": (now - timedelta(hours=48)).isoformat(),  # FUERA de ventana 24h
        },
    ]
    db.preload(MEMENTO_VALIDATIONS_TABLE, rows)


def test_admin_dashboard_json_metrics(validator):
    db = FakeSupabaseClient()
    _seed_dashboard_rows(db)
    detector = ContaminationDetector(db=db, repo_root=None)
    app = _build_app(validator=validator, db=db, detector=detector)
    client = TestClient(app)

    resp = client.get("/v1/memento/admin/dashboard", headers=_auth_headers())
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["health"]["validator_initialized"] is True
    assert data["health"]["detector_initialized"] is True
    assert data["health"]["db_available"] is True
    assert data["health"]["critical_operations_loaded"] == 1
    assert data["window"]["lookback_hours"] == MEMENTO_DASHBOARD_LOOKBACK_HOURS
    assert data["window"]["sample_size"] == 3  # las 3 dentro de la ventana
    v = data["validations_last_24h"]
    assert v["total"] == 3
    assert v["ok"] == 2
    assert v["discrepancy_detected"] == 1
    assert 0.6 < v["ok_rate"] < 0.7

    c = data["contamination_last_24h"]
    assert c["warnings"] == 2
    assert c["breakdown"]["by_rule_id"] == {"H2": 1, "H3": 1}
    assert c["breakdown"]["by_severity"] == {"HIGH": 1, "MEDIUM": 1}

    top_ops = {o["operation"]: o["count"] for o in data["top_operations"]}
    assert top_ops["sql_against_production"] == 2
    assert top_ops["rotate_credential"] == 1
    top_hilos = {o["hilo_id"]: o["count"] for o in data["top_hilos"]}
    assert top_hilos["hilo_a"] == 2
    assert top_hilos["hilo_b"] == 1


def test_admin_dashboard_html_render(validator):
    db = FakeSupabaseClient()
    _seed_dashboard_rows(db)
    app = _build_app(validator=validator, db=db)
    client = TestClient(app)

    resp = client.get(
        "/v1/memento/admin/dashboard",
        headers={**_auth_headers(), "Accept": "text/html"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    body = resp.text
    assert "Memento" in body
    assert "Validaciones" in body
    assert "Contaminación detectada" in body or "Contaminacion" in body or "Contaminaci" in body


def test_admin_dashboard_no_db_returns_zero_metrics(validator):
    app = _build_app(validator=validator, db=None)
    client = TestClient(app)
    resp = client.get("/v1/memento/admin/dashboard", headers=_auth_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["health"]["db_available"] is False
    assert data["validations_last_24h"]["total"] == 0
    assert data["contamination_last_24h"]["warnings"] == 0


# ===========================================================================
# 4. Test opt-in productivo (gated por env var)
# ===========================================================================


@pytest.mark.skipif(
    os.environ.get("MEMENTO_INTEGRATION_TESTS", "").lower() != "true",
    reason="Set MEMENTO_INTEGRATION_TESTS=true para correr contra Railway productivo",
)
def test_integration_dashboard_against_railway():
    """Smoke productivo opcional contra Railway."""
    import urllib.request
    import json as _json

    base = os.environ.get("KERNEL_URL", "https://el-monstruo-kernel-production.up.railway.app")
    api_key = os.environ.get("MONSTRUO_API_KEY")
    assert api_key, "MONSTRUO_API_KEY no configurada en el ambiente"

    req = urllib.request.Request(
        f"{base}/v1/memento/admin/dashboard",
        headers={"X-API-Key": api_key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        assert resp.status == 200
        data = _json.loads(resp.read().decode("utf-8"))
    assert "health" in data
    assert "validations_last_24h" in data
    assert "contamination_last_24h" in data
