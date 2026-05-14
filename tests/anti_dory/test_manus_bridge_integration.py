"""
tests/anti_dory/test_manus_bridge_integration.py
Sprint MANUS-ANTI-DORY-002 v1 FASE C T2.

Cubre el wire opt-in del ContextBroker en tools.manus_bridge.create_task.
Mockea httpx + broker; NO toca Supabase real, NO toca Manus API real.

Tests obligatorios del kickoff §2 T2:
  1. attach_context=False  → pass-through idéntico a pre-FASE-C
  2. attach_context=True + flag OFF → pass-through (no hidrata)
  3. attach_context=True + flag ON + broker mock → prompt hidratado
  4. broker.hydrate_prompt() lanza excepción → fail-open con prompt original

Constraints duros:
- No tocar httpx real (monkeypatch _request_with_retry).
- No tocar kernel.anti_dory.context_broker (usar broker mock vía factory).
- Reset rate limiter entre tests (mantiene aislamiento).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional
from unittest.mock import MagicMock

import pytest

from tools import manus_bridge as bridge_mod
from tools.manus_bridge import create_task, set_anti_dory_broker_factory


# =============================================================================
# Fixtures comunes
# =============================================================================

@pytest.fixture(autouse=True)
def _reset_state(monkeypatch):
    """Reset broker factory + rate limiter + mock httpx en cada test."""
    # 1. Reset broker factory
    set_anti_dory_broker_factory(None)
    yield
    set_anti_dory_broker_factory(None)
    # 2. Reset rate limiter (clear lista in-place)
    bridge_mod._call_timestamps.clear()


@pytest.fixture(autouse=True)
def _mock_manus_http(monkeypatch):
    """Sustituye _request_with_retry por un stub que captura el payload."""
    captured: dict[str, Any] = {}

    def fake_request(method, url, account, json_payload=None, timeout=30.0, retries=3):
        captured["method"] = method
        captured["url"] = url
        captured["account"] = account
        captured["json_payload"] = json_payload
        return {
            "ok": True,
            "data": {"task_id": "mock-task-id", "status": "queued"},
        }

    monkeypatch.setattr(bridge_mod, "_request_with_retry", fake_request)
    # Expose captured dict via module attribute for test introspection.
    bridge_mod._test_last_payload = captured  # type: ignore[attr-defined]
    yield captured
    if hasattr(bridge_mod, "_test_last_payload"):
        delattr(bridge_mod, "_test_last_payload")


# =============================================================================
# Helpers
# =============================================================================

@dataclass
class FakePack:
    attachment_ok: bool
    snapshot_id: Optional[str] = "snap-mock-001"
    confidence_score: float = 0.95
    fallback_reason: Optional[str] = None


@dataclass
class FakeHydratedPrompt:
    hydrated_prompt: str
    pack: FakePack


class FakeBrokerHydrates:
    """Mock broker que SIEMPRE hidrata con un prefijo conocido."""

    def hydrate_prompt(self, *, project_id, front_id, user_prompt):
        prefix = (
            f"=== ATTACHMENT_OK (mock) ===\n"
            f"project_id={project_id}\nfront_id={front_id}\n"
            f"=== END ATTACHMENT_OK ==="
        )
        return FakeHydratedPrompt(
            hydrated_prompt=f"{prefix}\n\n{user_prompt}",
            pack=FakePack(attachment_ok=True),
        )


class FakeBrokerRaises:
    """Mock broker que lanza excepción para verificar fail-open."""

    def hydrate_prompt(self, *, project_id, front_id, user_prompt):
        raise RuntimeError("simulated broker failure (RPC down)")


# =============================================================================
# Tests
# =============================================================================

def test_attach_context_false_passthrough(_mock_manus_http, monkeypatch):
    """Si attach_context=False, manus_bridge.create_task NO toca el prompt
    y no invoca al broker, idéntico a pre-FASE-C."""
    # Forzar ANTI_DORY_ENABLED=True para descartar que el flag sea quien protege.
    import kernel.anti_dory as anti_dory_pkg
    monkeypatch.setattr(anti_dory_pkg, "ANTI_DORY_ENABLED", True, raising=False)

    # Configurar broker que fallaría si se invocara: así verificamos que NO es invocado.
    set_anti_dory_broker_factory(lambda: FakeBrokerRaises())

    result = create_task("prompt-original-x", account="google", project_id="el-monstruo")

    # Verificación 1: payload enviado a Manus contiene el prompt ORIGINAL sin prefijo.
    assert _mock_manus_http["json_payload"]["message"]["content"] == "prompt-original-x"
    # Verificación 2: response del mock se respeta.
    assert result == {"task_id": "mock-task-id", "status": "queued"}


def test_attach_context_true_flag_off_passthrough(_mock_manus_http, monkeypatch):
    """Si attach_context=True pero ANTI_DORY_ENABLED=False (default actual),
    el wire respeta el flag global y NO hidrata. Broker no se invoca."""
    import kernel.anti_dory as anti_dory_pkg
    monkeypatch.setattr(anti_dory_pkg, "ANTI_DORY_ENABLED", False, raising=False)

    set_anti_dory_broker_factory(lambda: FakeBrokerRaises())

    result = create_task(
        "prompt-original-y",
        account="google",
        project_id="el-monstruo",
        attach_context=True,
    )

    # Payload contiene prompt original sin prefijo.
    assert _mock_manus_http["json_payload"]["message"]["content"] == "prompt-original-y"
    assert result["task_id"] == "mock-task-id"


def test_attach_context_true_flag_on_hydrates(_mock_manus_http, monkeypatch, caplog):
    """Si attach_context=True y ANTI_DORY_ENABLED=True y factory configurada,
    el prompt enviado a Manus está prefijado por el broker."""
    import kernel.anti_dory as anti_dory_pkg
    monkeypatch.setattr(anti_dory_pkg, "ANTI_DORY_ENABLED", True, raising=False)

    set_anti_dory_broker_factory(lambda: FakeBrokerHydrates())

    caplog.set_level(logging.INFO, logger="monstruo.manus_bridge")
    result = create_task(
        "continuá lo de ayer; no te reexplico nada.",
        account="google",
        project_id="el-monstruo",
        front_id="manus-anti-dory-002",
        attach_context=True,
    )

    sent_prompt = _mock_manus_http["json_payload"]["message"]["content"]
    assert "=== ATTACHMENT_OK (mock) ===" in sent_prompt
    assert "project_id=el-monstruo" in sent_prompt
    assert "front_id=manus-anti-dory-002" in sent_prompt
    # El user_prompt original sigue al final.
    assert sent_prompt.endswith("continuá lo de ayer; no te reexplico nada.")
    # Logging de attachment_ok.
    assert any(
        "anti_dory_attachment_ok" in record.message
        for record in caplog.records
    )
    assert result["status"] == "queued"


def test_broker_exception_fallback_to_original_prompt(_mock_manus_http, monkeypatch, caplog):
    """Si broker.hydrate_prompt() lanza excepción con flag ON, create_task
    cae en fail-open y manda el prompt original (NO interrumpe la tarea)."""
    import kernel.anti_dory as anti_dory_pkg
    monkeypatch.setattr(anti_dory_pkg, "ANTI_DORY_ENABLED", True, raising=False)

    set_anti_dory_broker_factory(lambda: FakeBrokerRaises())

    caplog.set_level(logging.WARNING, logger="monstruo.manus_bridge")
    result = create_task(
        "prompt-fail-open-z",
        account="google",
        project_id="el-monstruo",
        attach_context=True,
    )

    # Payload contiene prompt original (no hidratado).
    assert _mock_manus_http["json_payload"]["message"]["content"] == "prompt-fail-open-z"
    # Logging de fallback warning con la causa del fallo.
    assert any(
        "anti_dory_broker_fallback" in record.message
        and "simulated broker failure" in record.message
        for record in caplog.records
    )
    # Task se creó correctamente a pesar del fallo del broker.
    assert result["task_id"] == "mock-task-id"


# =============================================================================
# Tests extras de defensa (no requeridos pero recomendados)
# =============================================================================

def test_factory_none_with_flag_on_fails_open(_mock_manus_http, monkeypatch, caplog):
    """Si attach_context=True y flag ON pero factory NO configurada,
    create_task cae en fail-open (sin romper la tarea)."""
    import kernel.anti_dory as anti_dory_pkg
    monkeypatch.setattr(anti_dory_pkg, "ANTI_DORY_ENABLED", True, raising=False)

    # No setear factory; fuerza el path RuntimeError → fail-open.
    set_anti_dory_broker_factory(None)

    caplog.set_level(logging.WARNING, logger="monstruo.manus_bridge")
    result = create_task(
        "prompt-no-factory",
        account="google",
        project_id="el-monstruo",
        attach_context=True,
    )

    assert _mock_manus_http["json_payload"]["message"]["content"] == "prompt-no-factory"
    assert any(
        "anti_dory_broker_fallback" in record.message
        and "factory not configured" in record.message
        for record in caplog.records
    )
    assert result["task_id"] == "mock-task-id"


def test_default_front_id_helper():
    """_default_front_id devuelve project_id o 'unknown-project'."""
    assert bridge_mod._default_front_id("el-monstruo") == "el-monstruo"
    assert bridge_mod._default_front_id(None) == "unknown-project"
    assert bridge_mod._default_front_id("") == "unknown-project"



# =============================================================================
# F-pattern #11 mitigation tests (Sprint MANUS-ANTI-DORY-002 v1 FASE D5-FIX-PROJECT-ID)
# =============================================================================
# Verifica que tools.manus_bridge.create_task distingue correctamente entre:
# - Real Manus UUID (22-char alphanumeric) → forwarded to payload
# - Anti-Dory logical label (e.g. "el_monstruo") → broker-only, NOT in payload

def test_project_id_uuid_manus_passed_to_payload(_mock_manus_http):
    """UUID Manus real (22 chars alphanumeric) DEBE pasarse al payload."""
    result = create_task(
        "prompt-x",
        account="google",
        project_id="NXPZPniFoQMdfQ8SYEfhem",  # real Manus UUID format
    )
    assert _mock_manus_http["json_payload"]["project_id"] == "NXPZPniFoQMdfQ8SYEfhem"
    assert _mock_manus_http["json_payload"]["message"]["content"] == "prompt-x"
    assert result["task_id"] == "mock-task-id"


def test_project_id_logical_label_omitted_from_payload(_mock_manus_http):
    """Etiqueta lógica broker (no UUID) NO debe pasarse al payload Manus (F #11)."""
    result = create_task(
        "prompt-x",
        account="google",
        project_id="el_monstruo",  # Anti-Dory logical label
    )
    assert "project_id" not in _mock_manus_http["json_payload"]
    assert _mock_manus_http["json_payload"]["message"]["content"] == "prompt-x"
    assert result["task_id"] == "mock-task-id"
