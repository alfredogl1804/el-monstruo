"""
El Monstruo — Kernel Entry Point
==================================
FastAPI application that exposes the Kernel API.
Sprint 1, Día 0: Stub with health check.
"""

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="El Monstruo",
    description="Sistema de Inteligencia Artificial Soberana",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOOT_TIME = datetime.now(timezone.utc)


@app.get("/health")
async def health():
    """Health check endpoint."""
    now = datetime.now(timezone.utc)
    return {
        "status": "ok",
        "service": "el-monstruo",
        "version": "0.1.0",
        "sprint": 1,
        "day": 0,
        "uptime_seconds": (now - BOOT_TIME).total_seconds(),
        "timestamp": now.isoformat(),
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "El Monstruo",
        "description": "Sistema de Inteligencia Artificial Soberana",
        "status": "Sprint 1 — Día 0 — Contracts & Infrastructure",
        "contracts": [
            "KernelInterface",
            "MemoryInterface",
            "EventEnvelope",
            "PolicyHook",
            "CheckpointStore",
        ],
    }
