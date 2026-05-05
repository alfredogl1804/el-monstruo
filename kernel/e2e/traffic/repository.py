"""
Sprint 87.2 Bloque 4 — TrafficRepository: DAL para tabla e2e_traffic.

Privacy-first: cero servicios externos. Cookie soberana del Monstruo.
Persistencia en Supabase (mismo cliente que e2e_runs).

Brand DNA: traffic_ingest_*_failed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol

import structlog
from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = structlog.get_logger("kernel.e2e.traffic.repository")


# ── Errores con identidad ────────────────────────────────────────────────────


class TrafficIngestFailed(Exception):
    """Brand DNA: traffic_ingest_*_failed."""

    code = "traffic_ingest_failed"


class TrafficIngestValidationFailed(TrafficIngestFailed):
    code = "traffic_ingest_validation_failed"


class TrafficIngestPersistenceFailed(TrafficIngestFailed):
    code = "traffic_ingest_persistence_failed"


# ── Schema ───────────────────────────────────────────────────────────────────

VALID_EVENT_TYPES = {"pageview", "cta_click", "unload", "custom"}
VALID_DEVICES = {"desktop", "mobile", "tablet", "unknown"}


class TrafficEvent(BaseModel):
    """Un evento de tráfico capturado por monstruo-tracking.js."""

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(..., min_length=1, max_length=64)
    session_id: str = Field(..., min_length=1, max_length=128)
    event_type: str = Field(..., min_length=1, max_length=32)
    url: str = Field(..., min_length=1, max_length=2000)
    referrer: Optional[str] = Field(default="", max_length=2000)
    device: str = Field(default="unknown", min_length=1, max_length=16)
    extra: Dict[str, Any] = Field(default_factory=dict)
    ts: Optional[str] = None

    @field_validator("event_type")
    @classmethod
    def _v_event(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_EVENT_TYPES:
            raise ValueError(f"event_type debe ser uno de {VALID_EVENT_TYPES}")
        return v

    @field_validator("device")
    @classmethod
    def _v_device(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_DEVICES:
            return "unknown"
        return v


class TrafficSummary(BaseModel):
    """Snapshot de métricas para dashboard de un run."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    pageviews: int = 0
    unique_sessions: int = 0
    cta_clicks: int = 0
    cta_conversion_rate: float = 0.0  # cta_clicks / pageviews
    devices_breakdown: Dict[str, int] = Field(default_factory=dict)
    last_event_ts: Optional[str] = None


# ── DBClient Protocol ───────────────────────────────────────────────────────


class DBClient(Protocol):
    @property
    def connected(self) -> bool: ...

    async def insert(self, table: str, data: dict[str, Any]) -> Optional[dict]: ...

    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = True,
        limit: Optional[int] = None,
    ) -> list[dict]: ...


# ── Repository ──────────────────────────────────────────────────────────────


class TrafficRepository:
    """DAL para e2e_traffic. Acepta DBClient inyectable (mock-friendly)."""

    def __init__(self, db: DBClient) -> None:
        self.db = db

    async def ingest_event(self, event: TrafficEvent) -> Dict[str, Any]:
        """Persiste un evento. Capa Memento: validación Pydantic ya hecha."""
        if not self.db.connected:
            raise TrafficIngestPersistenceFailed(
                "traffic_ingest_persistence_failed: DB cliente no conectado"
            )

        row = {
            "run_id": event.run_id,
            "session_id": event.session_id,
            "event_type": event.event_type,
            "url": event.url,
            "referrer": event.referrer or "",
            "device": event.device,
            "extra": event.extra,
        }
        if event.ts:
            row["ts"] = event.ts

        try:
            result = await self.db.insert("e2e_traffic", row)
        except Exception as e:
            raise TrafficIngestPersistenceFailed(
                f"traffic_ingest_persistence_failed: {e!s}"
            ) from e

        logger.info(
            "traffic_event_ingested",
            run_id=event.run_id,
            event_type=event.event_type,
            session_id=event.session_id[:12] + "...",
        )
        return result or row

    async def summarize_run(self, run_id: str) -> TrafficSummary:
        """Calcula métricas agregadas para un run."""
        try:
            rows = await self.db.select(
                "e2e_traffic",
                columns="event_type,session_id,device,ts",
                filters={"run_id": run_id},
                order_by="ts",
                order_desc=True,
                limit=10000,
            )
        except Exception as e:
            logger.warning("traffic_summary_failed", run_id=run_id, error=str(e))
            return TrafficSummary(run_id=run_id)

        pageviews = 0
        cta_clicks = 0
        sessions: set[str] = set()
        devices: Dict[str, int] = {}
        last_ts: Optional[str] = None

        for r in rows or []:
            et = (r.get("event_type") or "").lower()
            if et == "pageview":
                pageviews += 1
            elif et == "cta_click":
                cta_clicks += 1
            sid = r.get("session_id")
            if sid:
                sessions.add(sid)
            dev = (r.get("device") or "unknown").lower()
            devices[dev] = devices.get(dev, 0) + 1
            if last_ts is None and r.get("ts"):
                last_ts = str(r["ts"])

        conversion = (cta_clicks / pageviews) if pageviews > 0 else 0.0

        return TrafficSummary(
            run_id=run_id,
            pageviews=pageviews,
            unique_sessions=len(sessions),
            cta_clicks=cta_clicks,
            cta_conversion_rate=round(conversion, 4),
            devices_breakdown=devices,
            last_event_ts=last_ts,
        )
