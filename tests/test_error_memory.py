"""
Tests para kernel/error_memory.py — Sprint 51.

Cubre:
- Sanitización determinística (mismo error → mismo signature)
- Cómputo de signature
- ErrorRule.to_prompt_hint()
- Modo degradado (sin DB, sin embeddings)
- Truncación de context

Tests de integración con Supabase real están fuera de este archivo
(requieren conexión y van en tests/integration/).
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from kernel.error_memory import (
    ErrorMemory,
    ErrorRule,
    ErrorPattern,
    build_embedding_client,
    DEFAULT_EMBEDDING_DIMS,
)


# ── Sanitización ──────────────────────────────────────────────────────

def test_sanitize_strips_uuid():
    em = ErrorMemory()
    msg = "Error in run a1b2c3d4-e5f6-7890-abcd-ef0123456789 at execute"
    sanitized = em._sanitize_message(msg)
    assert "<UUID>" in sanitized
    assert "a1b2c3d4" not in sanitized


def test_sanitize_strips_timestamp():
    em = ErrorMemory()
    msg = "Failed at 2026-05-03T12:34:56Z connection refused"
    sanitized = em._sanitize_message(msg)
    assert "<TS>" in sanitized
    assert "2026-05-03" not in sanitized


def test_sanitize_strips_hex_hash():
    em = ErrorMemory()
    msg = "Commit 7f3a8b2c1d9e4f50a6b7c8d9e0f1a2b3c4d5e6f7 missing"
    sanitized = em._sanitize_message(msg)
    assert "<HASH>" in sanitized


def test_sanitize_strips_path_line():
    em = ErrorMemory()
    msg = "AssertionError in /app/kernel/nodes.py:1247"
    sanitized = em._sanitize_message(msg)
    assert "<LINE>" in sanitized
    assert "1247" not in sanitized


def test_sanitize_idempotent_collapses_whitespace():
    em = ErrorMemory()
    msg = "Error    with     extra      spaces"
    sanitized = em._sanitize_message(msg)
    assert "  " not in sanitized


def test_signature_stable_for_equivalent_messages():
    """Dos errores con mismo tipo + módulo + mensaje sanitizado → mismo signature."""
    em = ErrorMemory()
    sig1 = em._compute_signature(
        "TimeoutError",
        "kernel.task_planner",
        em._sanitize_message("Step timeout exceeded 60s on run abc-123"),
    )
    sig2 = em._compute_signature(
        "TimeoutError",
        "kernel.task_planner",
        em._sanitize_message("Step timeout exceeded 60s on run xyz-789"),
    )
    assert sig1 == sig2


def test_signature_changes_with_module():
    em = ErrorMemory()
    sig1 = em._compute_signature("KeyError", "kernel.tool_dispatch", "missing tool")
    sig2 = em._compute_signature("KeyError", "kernel.task_planner", "missing tool")
    assert sig1 != sig2


# ── ErrorRule ─────────────────────────────────────────────────────────

def test_rule_to_prompt_hint_includes_confidence():
    rule = ErrorRule(
        error_signature="abc123",
        sanitized_message="Tool not found",
        resolution="Verify tool_dispatch.get_tool_specs()",
        confidence=0.85,
        occurrences=4,
        module="kernel.tool_dispatch",
    )
    hint = rule.to_prompt_hint()
    assert "85%" in hint
    assert "4x" in hint
    assert "kernel.tool_dispatch" in hint
    assert "Tool not found" in hint
    assert "Verify tool_dispatch" in hint


def test_rule_without_resolution_omits_resolution_line():
    rule = ErrorRule(
        error_signature="abc",
        sanitized_message="some error",
        resolution=None,
        confidence=0.7,
    )
    hint = rule.to_prompt_hint()
    assert "Resolución conocida" not in hint


# ── Modo degradado ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_initialize_returns_false_without_db():
    em = ErrorMemory(db=None)
    assert await em.initialize() is False
    assert em.initialized is False


@pytest.mark.asyncio
async def test_record_returns_none_when_not_initialized():
    em = ErrorMemory()
    sig = await em.record(ValueError("test"), {"module": "test"})
    assert sig is None


@pytest.mark.asyncio
async def test_consult_returns_empty_when_not_initialized():
    em = ErrorMemory()
    rules = await em.consult("test", {"module": "test"})
    assert rules == []


# ── Truncación ────────────────────────────────────────────────────────

def test_truncate_context_drops_module_and_action():
    em = ErrorMemory()
    out = em._truncate_context({
        "module": "kernel.x",
        "action": "do_something",
        "run_id": "abc",
    })
    assert "module" not in out
    assert "action" not in out
    assert out["run_id"] == "abc"


def test_truncate_context_truncates_long_strings():
    em = ErrorMemory()
    long_text = "x" * 1000
    out = em._truncate_context({"data": long_text})
    assert len(out["data"]) < 600
    assert "[truncado]" in out["data"]


# ── Bootstrap helper ──────────────────────────────────────────────────

def test_build_embedding_client_returns_none_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = build_embedding_client()
    assert client is None


# ── Mock de DB para flujo end-to-end ──────────────────────────────────

@pytest.mark.asyncio
async def test_record_dedupes_existing_signature():
    """Si el signature ya existe, debe incrementar occurrences sin insertar."""
    db = MagicMock()
    db.connected = True
    db.select = AsyncMock(side_effect=[
        [],  # initialize probe
        [{"id": "uuid-1", "occurrences": 3}],  # record probe
    ])
    db.update = AsyncMock(return_value={})
    db.insert = AsyncMock()
    db.rpc = AsyncMock(side_effect=Exception("pgvector no disponible"))

    em = ErrorMemory(db=db)
    await em.initialize()
    assert em.initialized is True

    sig = await em.record(
        ValueError("test error"),
        {"module": "kernel.test", "action": "test_action"},
    )
    assert sig is not None
    assert len(sig) == 32
    db.update.assert_called_once()
    db.insert.assert_not_called()
    update_args = db.update.call_args
    assert update_args.kwargs["data"]["occurrences"] == 4


@pytest.mark.asyncio
async def test_record_inserts_new_signature():
    """Si el signature no existe, debe insertar fila nueva."""
    db = MagicMock()
    db.connected = True
    db.select = AsyncMock(side_effect=[
        [],  # initialize probe
        [],  # record probe — no existing
    ])
    db.update = AsyncMock()
    db.insert = AsyncMock(return_value={"id": "new-uuid"})
    db.rpc = AsyncMock(side_effect=Exception("pgvector no disponible"))

    em = ErrorMemory(db=db)
    await em.initialize()

    sig = await em.record(
        TimeoutError("step timeout"),
        {"module": "kernel.task_planner", "action": "execute_step"},
    )
    assert sig is not None
    db.insert.assert_called_once()
    insert_args = db.insert.call_args
    data = insert_args.kwargs["data"]
    assert data["error_type"] == "TimeoutError"
    assert data["module"] == "kernel.task_planner"
    assert data["action"] == "execute_step"
    assert data["occurrences"] == 1
    assert data["status"] == "open"


@pytest.mark.asyncio
async def test_consult_degraded_filters_by_module():
    """Sin pgvector, consult filtra por module exacto."""
    db = MagicMock()
    db.connected = True
    db.select = AsyncMock(side_effect=[
        [],  # initialize probe
        [  # consult exact
            {
                "error_signature": "sig1",
                "sanitized_message": "Tool not found: github",
                "resolution": "Check tool_specs",
                "confidence": 0.8,
                "occurrences": 2,
                "module": "kernel.tool_dispatch",
                "action": "_execute_tool",
            },
            {
                "error_signature": "sig2",
                "sanitized_message": "low confidence error",
                "resolution": None,
                "confidence": 0.4,  # below threshold
                "occurrences": 1,
                "module": "kernel.tool_dispatch",
                "action": "other",
            },
        ],
    ])
    db.rpc = AsyncMock(side_effect=Exception("no pgvector"))

    em = ErrorMemory(db=db)
    await em.initialize()
    rules = await em.consult(
        "ejecutar github",
        {"module": "kernel.tool_dispatch", "action": "_execute_tool"},
    )
    # Solo la regla con confidence >= 0.7 debe aparecer
    assert len(rules) == 1
    assert rules[0].error_signature == "sig1"
    assert rules[0].confidence == 0.8


@pytest.mark.asyncio
async def test_aggregate_patterns_promotes_clusters_with_min_size():
    db = MagicMock()
    db.connected = True
    rows = [
        {"error_signature": f"s{i}", "error_type": "TimeoutError",
         "module": "kernel.task_planner", "occurrences": 2}
        for i in range(4)
    ] + [
        {"error_signature": "lonely", "error_type": "RareError",
         "module": "kernel.weird", "occurrences": 1}
    ]
    db.select = AsyncMock(side_effect=[[], rows])
    db.rpc = AsyncMock(side_effect=Exception("no pgvector"))
    db.upsert = AsyncMock()

    em = ErrorMemory(db=db)
    await em.initialize()
    patterns = await em.aggregate_patterns()

    # Solo el cluster de 4 promueve (min_cluster_size=3); el solitario no
    assert len(patterns) == 1
    assert patterns[0].pattern_name.startswith("TimeoutError_kernel_task_planner")
    assert len(patterns[0].signature_cluster) == 4
