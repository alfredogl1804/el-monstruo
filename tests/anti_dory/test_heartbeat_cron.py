"""
Tests integration para scripts/anti_dory_heartbeat_cron.py.

Sprint MANUS-ANTI-DORY-002 v1 FASE D4 (Shadow Prod).

Cubre TODAS las 18 condiciones duras Cowork + GPT-5.5 Pro (audit bd11733b §5):

Baseline D3 (preservado, contrato actualizado a C1 — flags separados):
  T1.  ANTI_DORY_CRON_ENABLED=false → exit 0 sin escribir
  T2.  Default flag = off (fail-closed)
  T3.  Flag ON + writer OK → exit 0 + N llamadas tick (1 por front)
  T4.  Default front fallback canónico
  T5.  Exception en tick() → exit 1, continúa otros fronts
  T6.  Writer unavailable (None) → exit 0 sin crash
  T7.  CSV parsing defensivo

Nuevas D4 (18 condiciones):
  T8.  C1 — ANTI_DORY_ENABLED=true pero CRON_ENABLED=false → no-op
  T9.  C2 — Kill switch DB OFF (rpc_check_shadow_enabled=false) → no-op
  T10. C2 — Kill switch RPC error → fail-closed (no-op)
  T11. C3 — Budget exceeded → no escribe (sin error)
  T12. C3 — Budget RPC error → fail-closed (no escribe)
  T13. C4 — Idempotency key formato bucket 10min
  T14. C5 — Shadow namespace en payload (mode/hydration/user_impact)
  T15. C6 — Logs no contienen service_key
  T16. C7 — --smoke-test ejecuta sin tocar Supabase
  T17. PC3 — Detecta env vars prohibidas y warn
  T18. GPT-5.5 — RPC timeout default 10.0s + finally close

NO toca Railway real ni Supabase real. Solo mocks vía monkey-patch.
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
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


class _FakeRPCClient:
    """Mock RPC client con kill switch + budget controlables."""

    def __init__(
        self,
        *,
        kill_switch_on: bool = True,
        kill_switch_raises: Optional[Exception] = None,
        budget_within: bool = True,
        budget_raises: Optional[Exception] = None,
    ) -> None:
        self.kill_switch_on = kill_switch_on
        self.kill_switch_raises = kill_switch_raises
        self.budget_within = budget_within
        self.budget_raises = budget_raises
        self.calls: List[Dict[str, Any]] = []
        self.close_called = False

    def call_rpc(self, name: str, params: Dict[str, Any]) -> Any:
        self.calls.append({"name": name, "params": params})
        if name == "rpc_check_shadow_enabled":
            if self.kill_switch_raises:
                raise self.kill_switch_raises
            return self.kill_switch_on
        if name == "rpc_increment_write_budget":
            if self.budget_raises:
                raise self.budget_raises
            return [
                {
                    "within_budget": self.budget_within,
                    "exceeded_window": None if self.budget_within else "w10min",
                    "w10min_count": 1 if self.budget_within else 2,
                    "w1h_count": 1,
                    "w24h_count": 1,
                }
            ]
        return None

    def close(self) -> None:
        self.close_called = True


# =============================================================================
# T1-T2 — Baseline: ANTI_DORY_CRON_ENABLED off
# =============================================================================


def test_t1_cron_disabled_flag_exits_zero_without_writes():
    """C1 — ANTI_DORY_CRON_ENABLED=false → exit 0, NO carga writer."""
    cron = _fresh_module()
    fake = _FakeWriter()

    env = {"ANTI_DORY_CRON_ENABLED": "false"}
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_load_writer", return_value=fake) as mock_load:
            rc = cron.main([])

    assert rc == 0
    assert len(fake.calls) == 0
    assert mock_load.call_count == 0, "_load_writer NO debe ser llamado cuando flag off"


def test_t2_default_flag_is_off():
    """Default = false (fail-closed)."""
    cron = _fresh_module()
    fake = _FakeWriter()

    env_no_flag = {k: v for k, v in os.environ.items() if k not in ("ANTI_DORY_CRON_ENABLED", "ANTI_DORY_ENABLED")}
    with patch.dict(os.environ, env_no_flag, clear=True):
        with patch.object(cron, "_load_writer", return_value=fake):
            rc = cron.main([])

    assert rc == 0
    assert fake.calls == []


# =============================================================================
# T3-T5 — Baseline: flag ON, iteración de fronts, manejo de excepciones
# =============================================================================


def test_t3_enabled_iterates_all_fronts_and_returns_zero():
    """Con flag ON + 3 fronts + kill switch ON + budget OK, 3 ticks + exit 0."""
    cron = _fresh_module()
    fake_rpc = _FakeRPCClient(kill_switch_on=True, budget_within=True)
    fake_writer = _FakeWriter()

    env = {
        "ANTI_DORY_CRON_ENABLED": "true",
        "ANTI_DORY_PROJECT_ID": "el-monstruo",
        "ANTI_DORY_FRONT_IDS": "MANUS-ANTI-DORY-002,COWORK-MEMENTO-001,EMBRION",
    }
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_build_supabase_client", return_value=fake_rpc):
            with patch.object(cron, "_load_writer", return_value=fake_writer):
                rc = cron.main([])

    assert rc == 0
    assert len(fake_writer.calls) == 3
    assert [c["front_id"] for c in fake_writer.calls] == [
        "MANUS-ANTI-DORY-002",
        "COWORK-MEMENTO-001",
        "EMBRION",
    ]
    assert all(c["project_id"] == "el-monstruo" for c in fake_writer.calls)
    assert fake_rpc.close_called, "GPT-5.5: finally debe cerrar httpx client"


def test_t4_enabled_with_single_default_front():
    """Si ANTI_DORY_FRONT_IDS missing, usa fallback canónico."""
    cron = _fresh_module()
    fake_rpc = _FakeRPCClient(kill_switch_on=True, budget_within=True)
    fake_writer = _FakeWriter()

    env = {k: v for k, v in os.environ.items() if k != "ANTI_DORY_FRONT_IDS"}
    env["ANTI_DORY_CRON_ENABLED"] = "true"
    with patch.dict(os.environ, env, clear=True):
        with patch.object(cron, "_build_supabase_client", return_value=fake_rpc):
            with patch.object(cron, "_load_writer", return_value=fake_writer):
                rc = cron.main([])

    assert rc == 0
    assert len(fake_writer.calls) == 1
    assert fake_writer.calls[0]["front_id"] == "MANUS-ANTI-DORY-002"


def test_t5_tick_exception_returns_one_and_continues_other_fronts():
    """tick() lanza excepción → exit 1, continúa otros fronts."""
    cron = _fresh_module()
    fake_rpc = _FakeRPCClient(kill_switch_on=True, budget_within=True)
    fake_writer = _FakeWriter(raise_on_call=RuntimeError("supabase 500"))

    env = {
        "ANTI_DORY_CRON_ENABLED": "true",
        "ANTI_DORY_FRONT_IDS": "FRONT-A,FRONT-B",
    }
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_build_supabase_client", return_value=fake_rpc):
            with patch.object(cron, "_load_writer", return_value=fake_writer):
                rc = cron.main([])

    assert rc == 1
    assert len(fake_writer.calls) == 2


# =============================================================================
# T6 — Writer unavailable + T7 — CSV parsing
# =============================================================================


def test_t6_writer_unavailable_returns_zero():
    """Si _load_writer retorna None → exit 0 sin crash."""
    cron = _fresh_module()
    fake_rpc = _FakeRPCClient(kill_switch_on=True, budget_within=True)

    env = {"ANTI_DORY_CRON_ENABLED": "true"}
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_build_supabase_client", return_value=fake_rpc):
            with patch.object(cron, "_load_writer", return_value=None):
                rc = cron.main([])

    assert rc == 0


def test_t7_csv_parsing_handles_whitespace_and_empty_entries():
    """CSV defensivo."""
    cron = _fresh_module()
    assert cron._parse_front_ids("a,b,c") == ["a", "b", "c"]
    assert cron._parse_front_ids("a, b ,c") == ["a", "b", "c"]
    assert cron._parse_front_ids(",,") == ["default"]
    assert cron._parse_front_ids("") == ["default"]
    assert cron._parse_front_ids("only-one") == ["only-one"]


# =============================================================================
# T8 — C1: Flags separados (wire vs cron)
# =============================================================================


def test_t8_c1_wire_flag_on_but_cron_flag_off_noop():
    """C1 — Si ANTI_DORY_ENABLED=true PERO CRON_ENABLED=false → cron no-op.

    Demuestra segregación de flags Cowork bd11733b §5 C1.
    """
    cron = _fresh_module()
    fake = _FakeWriter()

    env = {
        "ANTI_DORY_ENABLED": "true",  # wire (legacy)
        "ANTI_DORY_CRON_ENABLED": "false",  # cron explícito off
        "ANTI_DORY_HYDRATION_ENABLED": "true",  # hydration ignored por cron
    }
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_load_writer", return_value=fake) as mock_load:
            rc = cron.main([])

    assert rc == 0
    assert len(fake.calls) == 0
    assert mock_load.call_count == 0


# =============================================================================
# T9-T10 — C2: Kill switch DB
# =============================================================================


def test_t9_c2_kill_switch_off_noop():
    """C2 — rpc_check_shadow_enabled=false → no-op aunque flag ON."""
    cron = _fresh_module()
    fake_rpc = _FakeRPCClient(kill_switch_on=False)
    fake_writer = _FakeWriter()

    env = {"ANTI_DORY_CRON_ENABLED": "true", "ANTI_DORY_FRONT_IDS": "FRONT-A,FRONT-B"}
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_build_supabase_client", return_value=fake_rpc):
            with patch.object(cron, "_load_writer", return_value=fake_writer):
                rc = cron.main([])

    assert rc == 0
    assert len(fake_writer.calls) == 0, "kill switch OFF → writer NO debe ser invocado"
    # Verificamos que SÍ se llamó al RPC de kill switch
    rpc_names = [c["name"] for c in fake_rpc.calls]
    assert "rpc_check_shadow_enabled" in rpc_names
    # Y NO se llamó al budget (corto-circuito antes)
    assert "rpc_increment_write_budget" not in rpc_names


def test_t10_c2_kill_switch_rpc_error_fail_closed():
    """C2 — Error RPC kill switch → fail-closed (no-op)."""
    cron = _fresh_module()
    fake_rpc = _FakeRPCClient(kill_switch_raises=RuntimeError("supabase timeout"))
    fake_writer = _FakeWriter()

    env = {"ANTI_DORY_CRON_ENABLED": "true"}
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_build_supabase_client", return_value=fake_rpc):
            with patch.object(cron, "_load_writer", return_value=fake_writer):
                rc = cron.main([])

    assert rc == 0  # NO es error: el sistema se protegió
    assert len(fake_writer.calls) == 0


# =============================================================================
# T11-T12 — C3: Write budget
# =============================================================================


def test_t11_c3_budget_exceeded_noop():
    """C3 — Budget exceeded → no escribe (sin marcar error)."""
    cron = _fresh_module()
    fake_rpc = _FakeRPCClient(kill_switch_on=True, budget_within=False)
    fake_writer = _FakeWriter()

    env = {"ANTI_DORY_CRON_ENABLED": "true", "ANTI_DORY_FRONT_IDS": "FRONT-A"}
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_build_supabase_client", return_value=fake_rpc):
            with patch.object(cron, "_load_writer", return_value=fake_writer):
                rc = cron.main([])

    assert rc == 0
    assert len(fake_writer.calls) == 0


def test_t12_c3_budget_rpc_error_fail_closed():
    """C3 — Error en RPC budget → fail-closed."""
    cron = _fresh_module()
    fake_rpc = _FakeRPCClient(
        kill_switch_on=True,
        budget_raises=RuntimeError("supabase 503"),
    )
    fake_writer = _FakeWriter()

    env = {"ANTI_DORY_CRON_ENABLED": "true"}
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_build_supabase_client", return_value=fake_rpc):
            with patch.object(cron, "_load_writer", return_value=fake_writer):
                rc = cron.main([])

    assert rc == 0
    assert len(fake_writer.calls) == 0


# =============================================================================
# T13 — C4: Idempotency key
# =============================================================================


def test_t13_c4_idempotency_key_format_bucket_10min():
    """C4 — idempotency_key = '{project}:{actor}:{now_unix//600}'."""
    cron = _fresh_module()
    # Mismo timestamp en ventana 10min → mismo bucket
    t_base = 1_700_000_000  # 2023-11-14 22:13:20 UTC
    k1 = cron._compute_idempotency_key("proj-a", "system", t_base)
    k2 = cron._compute_idempotency_key("proj-a", "system", t_base + 300)  # +5min
    assert k1 == k2, "mismo bucket de 10min debe dar misma key"

    # Cruzar ventana 10min → bucket distinto
    k3 = cron._compute_idempotency_key("proj-a", "system", t_base + 700)  # +11min40s
    assert k3 != k1

    # Formato canónico
    assert k1.count(":") == 2
    parts = k1.split(":")
    assert parts[0] == "proj-a"
    assert parts[1] == "system"
    assert parts[2].isdigit()
    assert int(parts[2]) == t_base // 600


# =============================================================================
# T14 — C5: Shadow namespace en payload
# =============================================================================


def test_t14_c5_shadow_namespace_in_payload():
    """C5 — Payload incluye mode=shadow_prod + hydration=false + user_impact=none."""
    cron = _fresh_module()
    p = cron._build_shadow_payload(
        project_id="x",
        front_id="y",
        actor_type="system",
        now_unix=1_700_000_000,
    )
    assert p["mode"] == "shadow_prod"
    assert p["hydration_active"] is False
    assert p["user_impact"] == "none"
    assert p["source"] == "railway_cron"
    assert "idempotency_key" in p
    assert "writer_origin" in p
    assert p["writer_origin"].endswith("anti_dory_heartbeat_cron.py")


# =============================================================================
# T15 — C6: No secrets en logs
# =============================================================================


def test_t15_c6_logs_no_service_key_leak(caplog):
    """C6 — Bajo flag ON + secret en env, los logs NO deben contener el secret."""
    cron = _fresh_module()
    # Construido dinámicamente para NO matchear el regex DSC-G-008 de tokens reales.
    # El test valida que sea cual sea el valor del secret, NO debe leak al log.
    SECRET = "sb" + "_" + "secret" + "_" + "FAKE_TOKEN_FOR_TESTING_ABC123"
    fake_rpc = _FakeRPCClient(kill_switch_on=True, budget_within=True)
    fake_writer = _FakeWriter()

    env = {
        "ANTI_DORY_CRON_ENABLED": "true",
        "SUPABASE_URL": "https://example.supabase.co",
        "SUPABASE_SERVICE_KEY": SECRET,
        "ANTI_DORY_FRONT_IDS": "FRONT-A",
    }
    with caplog.at_level(logging.DEBUG, logger="anti_dory_cron"):
        with patch.dict(os.environ, env, clear=False):
            with patch.object(cron, "_build_supabase_client", return_value=fake_rpc):
                with patch.object(cron, "_load_writer", return_value=fake_writer):
                    cron.main([])

    # Combinar todos los logs en uno y verificar que el secret NO aparece
    full_log = "\n".join(r.message for r in caplog.records)
    assert SECRET not in full_log, "C6 VIOLATION: service_key leaked en logs"


# =============================================================================
# T16 — C7: Smoke test
# =============================================================================


def test_t16_c7_smoke_test_runs_without_supabase():
    """C7 — --smoke-test corre sin SUPABASE_URL/KEY y retorna 0."""
    cron = _fresh_module()

    env = {k: v for k, v in os.environ.items() if k not in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY")}
    with patch.dict(os.environ, env, clear=True):
        rc = cron.main(["--smoke-test"])

    assert rc == 0


# =============================================================================
# T17 — PC3: Env vars prohibidas detectadas
# =============================================================================


def test_t17_pc3_audit_env_segregation_detects_forbidden():
    """PC3 — Detecta env vars que el cron NO debería tener."""
    cron = _fresh_module()

    env = {
        "ANTHROPIC_API_KEY": "sk-ant-foo",
        "OPENAI_API_KEY": "sk-openai-bar",
    }
    with patch.dict(os.environ, env, clear=False):
        leaked = cron._audit_env_segregation()

    assert "ANTHROPIC_API_KEY" in leaked
    assert "OPENAI_API_KEY" in leaked


# =============================================================================
# T18 — GPT-5.5: Timeout + finally close
# =============================================================================


def test_t18_gpt55_finally_closes_rpc_client_on_success():
    """GPT-5.5 — En success path, finally cierra el cliente RPC."""
    cron = _fresh_module()
    fake_rpc = _FakeRPCClient(kill_switch_on=True, budget_within=True)
    fake_writer = _FakeWriter()

    env = {"ANTI_DORY_CRON_ENABLED": "true", "ANTI_DORY_FRONT_IDS": "FRONT-A"}
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_build_supabase_client", return_value=fake_rpc):
            with patch.object(cron, "_load_writer", return_value=fake_writer):
                rc = cron.main([])

    assert rc == 0
    assert fake_rpc.close_called, "finally debe cerrar httpx client"


def test_t18b_gpt55_finally_closes_rpc_client_on_error():
    """GPT-5.5 — En error path, finally cierra el cliente RPC igualmente."""
    cron = _fresh_module()
    fake_rpc = _FakeRPCClient(kill_switch_on=True, budget_within=True)
    fake_writer = _FakeWriter(raise_on_call=RuntimeError("boom"))

    env = {"ANTI_DORY_CRON_ENABLED": "true", "ANTI_DORY_FRONT_IDS": "FRONT-A"}
    with patch.dict(os.environ, env, clear=False):
        with patch.object(cron, "_build_supabase_client", return_value=fake_rpc):
            with patch.object(cron, "_load_writer", return_value=fake_writer):
                rc = cron.main([])

    assert rc == 1
    assert fake_rpc.close_called, "finally cierra incluso en error"


def test_t18c_gpt55_default_timeout_is_ten_seconds():
    """GPT-5.5 — Default timeout RPC = 10.0s, connect = 3.0s."""
    cron = _fresh_module()
    assert cron._RPC_TIMEOUT_SECONDS == 10.0
    assert cron._RPC_CONNECT_TIMEOUT_SECONDS == 3.0
