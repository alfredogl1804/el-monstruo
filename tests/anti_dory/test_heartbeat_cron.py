"""
Tests integration para scripts/anti_dory_heartbeat_cron.py.

Sprint MANUS-ANTI-DORY-002 v1 FASE D3.

Cubre los 3 contratos críticos del cron entrypoint:

1. ANTI_DORY_ENABLED=false → exit 0 sin escribir (fail-closed clean).
2. ANTI_DORY_ENABLED=true + writer OK → exit 0 + N llamadas tick (1 por front).
3. ANTI_DORY_ENABLED=true + writer.tick excepciona → exit 1 (logged, no crash).

NO toca Railway real ni Supabase real. Solo mocks vía monkey-patch.
"""
from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional
from unittest.mock import patch


# Add scripts/ to path for import
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


def _fresh_module():
    """Recarga el módulo cron entre tests para resetear caches de env."""
    if "anti_dory_heartbeat_cron" in sys.modules:
        del sys.modules["anti_dory_heartbeat_cron"]
    return importlib.import_module("anti_dory_heartbeat_cron")


@dataclass
class _FakeWriteResult:
    snapshot_id: Optional[str] = "snap-fake-1"
    accepted: bool = True
    error: Optional[str] = None


@dataclass
class _FakeWriter:
    """Captura todas las llamadas a tick() para asserts."""
    calls: List[dict] = field(default_factory=list)
    raise_on_call: Optional[Exception] = None
    next_result: _FakeWriteResult = field(default_factory=_FakeWriteResult)

    def tick(self, *, project_id: str, front_id: str):
        self.calls.append({"project_id": project_id, "front_id": front_id})
        if self.raise_on_call is not None:
            raise self.raise_on_call
        return self.next_result


# =============================================================================
# Test 1 — ANTI_DORY_ENABLED=false → exit 0 sin escribir
# =============================================================================

def test_disabled_flag_exits_zero_without_writes():
    """Cuando ANTI_DORY_ENABLED=false el cron retorna 0 y NO carga writer."""
    cron = _fresh_module()
    fake = _FakeWriter()

    with patch.dict(os.environ, {"ANTI_DORY_ENABLED": "false"}, clear=False):
        with patch.object(cron, "_load_writer", return_value=fake) as mock_load:
            rc = cron.main([])

    assert rc == 0, "exit code debe ser 0 cuando flag off"
    assert len(fake.calls) == 0, "writer NO debe ser invocado cuando flag off"
    assert mock_load.call_count == 0, "_load_writer NO debe ser llamado cuando flag off"


def test_default_flag_is_off():
    """Si no hay ANTI_DORY_ENABLED en env, default = false (fail-closed)."""
    cron = _fresh_module()
    fake = _FakeWriter()

    env_no_flag = {k: v for k, v in os.environ.items() if k != "ANTI_DORY_ENABLED"}
    with patch.dict(os.environ, env_no_flag, clear=True):
        with patch.object(cron, "_load_writer", return_value=fake):
            rc = cron.main([])

    assert rc == 0
    assert fake.calls == []


# =============================================================================
# Test 2 — Flag ON + writer OK → exit 0 + 1 llamada por front
# =============================================================================

def test_enabled_iterates_all_fronts_and_returns_zero():
    """Con flag ON y 3 fronts, el cron llama tick() 3 veces y retorna 0."""
    cron = _fresh_module()
    fake = _FakeWriter()

    env = {
        "ANTI_DORY_ENABLED": "true",
        "ANTI_DORY_PROJECT_ID": "el-monstruo",
        "ANTI_DORY_FRONT_IDS": "MANUS-ANTI-DORY-002,COWORK-MEMENTO-001,EMBRION",
    }
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_load_writer", return_value=fake):
            rc = cron.main([])

    assert rc == 0, "exit 0 cuando todos los ticks succeed"
    assert len(fake.calls) == 3, f"esperaban 3 ticks, hubo {len(fake.calls)}"
    fronts_called = [c["front_id"] for c in fake.calls]
    assert fronts_called == ["MANUS-ANTI-DORY-002", "COWORK-MEMENTO-001", "EMBRION"]
    assert all(c["project_id"] == "el-monstruo" for c in fake.calls)


def test_enabled_with_single_default_front():
    """Si ANTI_DORY_FRONT_IDS no está, usa fallback canónico 'MANUS-ANTI-DORY-002'."""
    cron = _fresh_module()
    fake = _FakeWriter()

    env_no_fronts = {k: v for k, v in os.environ.items() if k != "ANTI_DORY_FRONT_IDS"}
    env_no_fronts["ANTI_DORY_ENABLED"] = "true"
    with patch.dict(os.environ, env_no_fronts, clear=True):
        with patch.object(cron, "_load_writer", return_value=fake):
            rc = cron.main([])

    assert rc == 0
    assert len(fake.calls) == 1
    assert fake.calls[0]["front_id"] == "MANUS-ANTI-DORY-002"


# =============================================================================
# Test 3 — writer.tick excepciona → exit 1, log claro, no crash
# =============================================================================

def test_tick_exception_returns_one_and_continues_other_fronts():
    """Si tick() levanta excepción en un front, el cron loggea y sigue con otros."""
    cron = _fresh_module()
    fake = _FakeWriter(raise_on_call=RuntimeError("supabase 500"))

    env = {
        "ANTI_DORY_ENABLED": "true",
        "ANTI_DORY_FRONT_IDS": "FRONT-A,FRONT-B",
    }
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_load_writer", return_value=fake):
            rc = cron.main([])

    assert rc == 1, "exit code 1 cuando todos los ticks fallan"
    assert len(fake.calls) == 2, "cron debe intentar todos los fronts aunque uno falle"


def test_writer_unavailable_returns_zero():
    """Si _load_writer retorna None (env vars Supabase missing), exit 0 sin crash."""
    cron = _fresh_module()

    with patch.dict(os.environ, {"ANTI_DORY_ENABLED": "true"}, clear=False):
        with patch.object(cron, "_load_writer", return_value=None):
            rc = cron.main([])

    assert rc == 0, "broker unavailable NO debe matar al servicio cron"


# =============================================================================
# Test extra — Parsing CSV defensivo
# =============================================================================

def test_csv_parsing_handles_whitespace_and_empty_entries():
    """CSV con espacios y entries vacíos se parsea correctamente."""
    cron = _fresh_module()

    assert cron._parse_front_ids("a,b,c") == ["a", "b", "c"]
    assert cron._parse_front_ids("a, b ,c") == ["a", "b", "c"]
    assert cron._parse_front_ids(",,") == ["default"]
    assert cron._parse_front_ids("") == ["default"]
    assert cron._parse_front_ids("only-one") == ["only-one"]
