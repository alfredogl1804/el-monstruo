"""
Sprint 87.2 Bloque 4 — Tests para kernel/e2e/traffic/

Coverage:
1. TrafficEvent Pydantic strict
2. TrafficEvent normaliza event_type / device
3. TrafficEvent rechaza event_type inválido
4. Ingest exitoso con DBClient mock
5. Ingest falla si DBClient no conectado
6. summarize_run con eventos mock → métricas correctas
7. summarize_run con run sin eventos → métricas vacías
8. Brand DNA error codes
9. Endpoint POST /v1/traffic/ingest valida body size
10. Endpoint POST /v1/traffic/ingest valida JSON
11. Endpoint GET /v1/traffic/summary/{run_id}
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from kernel.e2e.traffic.repository import (
    TrafficEvent,
    TrafficIngestFailed,
    TrafficIngestPersistenceFailed,
    TrafficIngestValidationFailed,
    TrafficRepository,
    TrafficSummary,
)
from kernel.e2e.traffic.routes import MAX_BODY_BYTES, traffic_router


# ── Mock DBClient ────────────────────────────────────────────────────────────


class MockDB:
    def __init__(self, connected: bool = True, rows: Optional[List[Dict[str, Any]]] = None) -> None:
        self._connected = connected
        self._rows = rows or []
        self.inserted: List[Dict[str, Any]] = []

    @property
    def connected(self) -> bool:
        return self._connected

    async def insert(self, table: str, data: dict) -> Optional[dict]:
        self.inserted.append({"table": table, "data": data})
        return {"id": len(self.inserted), **data}

    async def select(self, table: str, columns: str = "*", filters=None,
                     order_by=None, order_desc=True, limit=None) -> list[dict]:
        return self._rows


# ── 1. TrafficEvent strict ──────────────────────────────────────────────────


def test_traffic_event_strict():
    e = TrafficEvent(
        run_id="e2e_999",
        session_id="sid_abc",
        event_type="pageview",
        url="https://x.io/landing",
        device="desktop",
    )
    assert e.event_type == "pageview"
    with pytest.raises(Exception):
        TrafficEvent(
            run_id="e2e_999",
            session_id="sid",
            event_type="pageview",
            url="https://x.io",
            extra_field="nope",
        )


# ── 2. Normalización event_type / device ────────────────────────────────────


def test_traffic_event_normalizes():
    e = TrafficEvent(
        run_id="e2e_999",
        session_id="sid",
        event_type="  PAGEVIEW  ",
        url="https://x.io",
        device="WeirdDevice",
    )
    assert e.event_type == "pageview"
    assert e.device == "unknown"  # WeirdDevice -> unknown


# ── 3. event_type inválido ──────────────────────────────────────────────────


def test_invalid_event_type_rejected():
    with pytest.raises(Exception, match="event_type debe ser uno de"):
        TrafficEvent(
            run_id="e2e_999",
            session_id="sid",
            event_type="not_real_event",
            url="https://x.io",
        )


# ── 4. Ingest exitoso ───────────────────────────────────────────────────────


def test_ingest_event_success():
    db = MockDB(connected=True)
    repo = TrafficRepository(db)
    event = TrafficEvent(
        run_id="e2e_999",
        session_id="sid_abc",
        event_type="pageview",
        url="https://x.io",
        device="mobile",
    )
    result = asyncio.run(repo.ingest_event(event))
    assert result["run_id"] == "e2e_999"
    assert len(db.inserted) == 1
    assert db.inserted[0]["table"] == "e2e_traffic"


# ── 5. Ingest falla DB no conectado ─────────────────────────────────────────


def test_ingest_fails_when_db_disconnected():
    db = MockDB(connected=False)
    repo = TrafficRepository(db)
    event = TrafficEvent(
        run_id="e2e_999", session_id="sid", event_type="pageview", url="x"
    )
    with pytest.raises(TrafficIngestPersistenceFailed):
        asyncio.run(repo.ingest_event(event))


# ── 6. summarize_run con eventos ────────────────────────────────────────────


def test_summarize_run_with_events():
    rows = [
        {"event_type": "pageview", "session_id": "s1", "device": "desktop", "ts": "2026-05-05T18:00:00+00:00"},
        {"event_type": "pageview", "session_id": "s2", "device": "mobile", "ts": "2026-05-05T18:01:00+00:00"},
        {"event_type": "cta_click", "session_id": "s1", "device": "desktop", "ts": "2026-05-05T18:02:00+00:00"},
        {"event_type": "pageview", "session_id": "s1", "device": "desktop", "ts": "2026-05-05T18:03:00+00:00"},
    ]
    db = MockDB(connected=True, rows=rows)
    repo = TrafficRepository(db)
    summary = asyncio.run(repo.summarize_run("e2e_test"))
    assert summary.pageviews == 3
    assert summary.cta_clicks == 1
    assert summary.unique_sessions == 2
    assert summary.cta_conversion_rate == round(1 / 3, 4)
    assert summary.devices_breakdown.get("desktop") == 3
    assert summary.devices_breakdown.get("mobile") == 1


# ── 7. summarize_run sin eventos ────────────────────────────────────────────


def test_summarize_run_empty():
    db = MockDB(connected=True, rows=[])
    repo = TrafficRepository(db)
    summary = asyncio.run(repo.summarize_run("e2e_empty"))
    assert summary.pageviews == 0
    assert summary.unique_sessions == 0
    assert summary.cta_conversion_rate == 0.0


# ── 8. Brand DNA ────────────────────────────────────────────────────────────


def test_brand_dna_codes():
    assert TrafficIngestFailed.code == "traffic_ingest_failed"
    assert TrafficIngestValidationFailed.code == "traffic_ingest_validation_failed"
    assert TrafficIngestPersistenceFailed.code == "traffic_ingest_persistence_failed"


# ── 9–11. Endpoint integration tests ────────────────────────────────────────


def _make_app(db: Optional[MockDB] = None) -> TestClient:
    app = FastAPI()
    app.include_router(traffic_router)
    if db is not None:
        app.state.traffic_repository = TrafficRepository(db)
    return TestClient(app)


def test_endpoint_body_too_large():
    db = MockDB()
    client = _make_app(db)
    big_payload = json.dumps({"x": "y" * (MAX_BODY_BYTES + 100)})
    r = client.post("/v1/traffic/ingest", content=big_payload)
    assert r.status_code == 413


def test_endpoint_invalid_json():
    db = MockDB()
    client = _make_app(db)
    r = client.post("/v1/traffic/ingest", content="not_json{{{")
    assert r.status_code == 400
    assert "traffic_ingest_validation_failed" in r.json()["detail"]


def test_endpoint_ingest_success_204():
    db = MockDB(connected=True)
    client = _make_app(db)
    payload = {
        "run_id": "e2e_test_endpoint",
        "session_id": "sid_xyz",
        "event_type": "pageview",
        "url": "https://x.io/landing",
        "device": "desktop",
    }
    r = client.post("/v1/traffic/ingest", json=payload)
    assert r.status_code == 204
    assert len(db.inserted) == 1


def test_endpoint_summary():
    rows = [
        {"event_type": "pageview", "session_id": "s1", "device": "desktop", "ts": "2026-05-05T18:00:00+00:00"},
        {"event_type": "cta_click", "session_id": "s1", "device": "desktop", "ts": "2026-05-05T18:01:00+00:00"},
    ]
    db = MockDB(connected=True, rows=rows)
    client = _make_app(db)
    r = client.get("/v1/traffic/summary/e2e_999")
    assert r.status_code == 200
    body = r.json()
    assert body["pageviews"] == 1
    assert body["cta_clicks"] == 1
    assert body["unique_sessions"] == 1
