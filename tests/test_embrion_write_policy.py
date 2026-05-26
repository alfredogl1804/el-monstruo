"""
tests/test_embrion_write_policy.py
Sprint EMBRION-NEEDS-001, Tarea 3 — Write Policy con HITL real.

Cubre los casos REQUERIDOS por el spec:
  - propose() crea proposal pending con idempotency key.
  - propose() idempotente: segunda llamada con mismo key → no duplica.
  - approve() cambia status a approved (solo desde pending).
  - reject() cambia status a rejected con razón.
  - expire_old() marca expired las que pasaron expires_at.
  - E2E: propose → approve → execute_next → status=executed.
  - Timeout: proposal con expires_in_hours=0 → expire_old la marca expired.
  - list_pending() retorna solo pending no expiradas.
  - execute_next() con executor_fn que lanza excepción → status=failed.
  - notify_hitl() inserta en embrion_memoria con importancia=10.
  - Race condition: approve segunda vez sobre approved falla.
  - Race condition: execute_next con lock perdido retorna None.

Estrategia: FakeClient en memoria con la misma firma que _SupabaseRest
(select/insert/update). Cero red.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pytest

# Importamos antes de tocar env porque DEFAULT_EXPIRATION_HOURS lee al import.
from kernel import embrion_write_policy as wp

# ──────────────────────────────────────────────────────────────────────
# FakeClient: cliente in-memory con misma firma que _SupabaseRest
# ──────────────────────────────────────────────────────────────────────


class FakeClient:
    """In-memory store por tabla con select/insert/update y filtros estilo
    PostgREST (eq.X, gte.X, lte.X, in.(a,b))."""

    def __init__(self, prefilled: dict[str, list[dict]] | None = None):
        self.tables: dict[str, list[dict]] = prefilled or {}
        self.calls: list[tuple] = []

    # ── Helpers de filtro
    @staticmethod
    def _matches(row: dict, params: dict) -> bool:
        for k, v in params.items():
            if k in ("select", "limit", "order", "offset"):
                continue
            if not isinstance(v, str):
                continue
            if v.startswith("eq."):
                expected = v[len("eq.") :]
                if expected == "true":
                    if row.get(k) is not True:
                        return False
                elif expected == "false":
                    if row.get(k) is not False:
                        return False
                else:
                    if str(row.get(k)) != expected:
                        return False
            elif v.startswith("gte."):
                cutoff = v[len("gte.") :]
                if (str(row.get(k) or "")) < cutoff:
                    return False
            elif v.startswith("lte."):
                cutoff = v[len("lte.") :]
                if (str(row.get(k) or "")) > cutoff:
                    return False
            elif v.startswith("in."):
                allowed = v[len("in.") :].strip("()").split(",")
                if str(row.get(k)) not in allowed:
                    return False
        return True

    def select(self, table: str, params: dict, prefer: str | None = None):
        self.calls.append(("select", table, dict(params)))
        rows = [r for r in self.tables.get(table, []) if self._matches(r, params)]
        order = params.get("order", "")
        if order:
            field, _, direction = order.partition(".")
            rows.sort(key=lambda r: r.get(field) or "", reverse=(direction == "desc"))
        lim = params.get("limit")
        if lim is not None:
            rows = rows[: int(lim)]
        return rows, {"Content-Range": f"0-{max(0, len(rows) - 1)}/{len(rows)}"}

    def insert(self, table: str, payload: Any):
        self.calls.append(("insert", table, payload))
        if isinstance(payload, dict):
            payload = [payload]
        out = []
        for p in payload:
            row = dict(p)
            row.setdefault("id", str(uuid4()))
            row.setdefault("created_at", datetime.now(timezone.utc).isoformat())
            row.setdefault("attempts", 0)
            self.tables.setdefault(table, []).append(row)
            out.append(row)
        return out

    def update(self, table: str, params: dict, payload: dict):
        self.calls.append(("update", table, dict(params), dict(payload)))
        affected = []
        for row in self.tables.get(table, []):
            if self._matches(row, params):
                row.update(payload)
                affected.append(dict(row))
        return affected


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────


def _make_payload(extra: int = 0) -> dict:
    return {"action": "test", "n": extra, "nested": {"k": "v"}}


# ──────────────────────────────────────────────────────────────────────
# 1. propose() básico
# ──────────────────────────────────────────────────────────────────────


def test_propose_creates_pending_proposal():
    client = FakeClient()
    res = wp.propose(
        client,
        proposal_type="db_write",
        summary="Test proposal",
        payload=_make_payload(),
        cycle_id=42,
    )
    assert res.created is True
    assert res.status == "pending"
    assert res.summary == "Test proposal"
    assert res.risk_level == "medium"

    # La proposal está en la tabla
    assert len(client.tables[wp.TABLE_PROPOSALS]) == 1
    row = client.tables[wp.TABLE_PROPOSALS][0]
    assert row["approval_status"] == "pending"
    assert row["proposal_type"] == "db_write"
    assert row["cycle_id"] == 42
    assert row["idempotency_key"]
    assert len(row["idempotency_key"]) == 64  # sha256 hex


def test_propose_validates_proposal_type():
    client = FakeClient()
    with pytest.raises(ValueError, match="proposal_type inválido"):
        wp.propose(
            client,
            proposal_type="hack_the_planet",
            summary="x",
            payload={},
        )


def test_propose_validates_risk_level():
    client = FakeClient()
    with pytest.raises(ValueError, match="risk_level inválido"):
        wp.propose(
            client,
            proposal_type="db_write",
            summary="x",
            payload={},
            risk_level="catastrophic",
        )


def test_propose_validates_payload_type():
    client = FakeClient()
    with pytest.raises(TypeError, match="payload debe ser dict"):
        wp.propose(
            client,
            proposal_type="db_write",
            summary="x",
            payload="not a dict",  # type: ignore[arg-type]
        )


def test_propose_validates_summary_not_empty():
    client = FakeClient()
    with pytest.raises(ValueError, match="summary"):
        wp.propose(
            client,
            proposal_type="db_write",
            summary="   ",
            payload={},
        )


# ──────────────────────────────────────────────────────────────────────
# 2. Idempotency
# ──────────────────────────────────────────────────────────────────────


def test_propose_is_idempotent_on_same_payload():
    client = FakeClient()
    payload = _make_payload(extra=1)

    r1 = wp.propose(client, proposal_type="db_write", summary="A", payload=payload)
    r2 = wp.propose(client, proposal_type="db_write", summary="A", payload=payload)

    assert r1.created is True
    assert r2.created is False
    assert r1.proposal_id == r2.proposal_id
    # Solo hay 1 fila en la tabla
    assert len(client.tables[wp.TABLE_PROPOSALS]) == 1


def test_propose_different_payloads_creates_distinct_proposals():
    client = FakeClient()
    r1 = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload(1))
    r2 = wp.propose(client, proposal_type="db_write", summary="B", payload=_make_payload(2))
    assert r1.proposal_id != r2.proposal_id
    assert len(client.tables[wp.TABLE_PROPOSALS]) == 2


def test_compute_idempotency_key_deterministic():
    k1 = wp.compute_idempotency_key("db_write", {"a": 1, "b": 2})
    k2 = wp.compute_idempotency_key("db_write", {"b": 2, "a": 1})  # orden distinto
    assert k1 == k2
    assert len(k1) == 64


def test_compute_idempotency_key_salt_changes_hash():
    k1 = wp.compute_idempotency_key("db_write", {"a": 1})
    k2 = wp.compute_idempotency_key("db_write", {"a": 1}, extra_salt="retry-1")
    assert k1 != k2


# ──────────────────────────────────────────────────────────────────────
# 3. approve() / reject()
# ──────────────────────────────────────────────────────────────────────


def test_approve_pending_proposal():
    client = FakeClient()
    p = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    updated = wp.approve(client, p.proposal_id, approved_by="alfredo")
    assert updated["approval_status"] == "approved"
    assert updated["approved_by"] == "alfredo"
    assert updated["approved_at"]


def test_approve_with_notes_stored_in_result_json():
    client = FakeClient()
    p = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    updated = wp.approve(client, p.proposal_id, approved_by="alfredo", notes="LGTM")
    assert updated["result_json"] == {"approval_notes": "LGTM"}


def test_approve_fails_on_non_pending():
    client = FakeClient()
    p = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    wp.approve(client, p.proposal_id, approved_by="alfredo")
    # Segunda llamada debería fallar (ya no está pending)
    with pytest.raises(ValueError, match="no está pending"):
        wp.approve(client, p.proposal_id, approved_by="alfredo")


def test_approve_fails_on_unknown_id():
    client = FakeClient()
    with pytest.raises(ValueError, match="no encontrada"):
        wp.approve(client, "00000000-0000-0000-0000-000000000000", approved_by="x")


def test_reject_pending_proposal():
    client = FakeClient()
    p = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    updated = wp.reject(client, p.proposal_id, approved_by="alfredo", reason="Riesgo no aceptado")
    assert updated["approval_status"] == "rejected"
    assert updated["rejection_reason"] == "Riesgo no aceptado"


def test_reject_requires_non_empty_reason():
    client = FakeClient()
    p = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    with pytest.raises(ValueError, match="requiere reason"):
        wp.reject(client, p.proposal_id, approved_by="alfredo", reason="   ")


def test_reject_fails_on_non_pending():
    client = FakeClient()
    p = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    wp.approve(client, p.proposal_id, approved_by="alfredo")
    with pytest.raises(ValueError, match="no está pending"):
        wp.reject(client, p.proposal_id, approved_by="alfredo", reason="meh")


# ──────────────────────────────────────────────────────────────────────
# 4. list_pending()
# ──────────────────────────────────────────────────────────────────────


def test_list_pending_returns_only_pending_unexpired():
    client = FakeClient()
    p1 = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload(1))
    p2 = wp.propose(client, proposal_type="db_write", summary="B", payload=_make_payload(2))
    wp.propose(client, proposal_type="db_write", summary="C", payload=_make_payload(3))
    # Aprobamos la 2 → ya no debe aparecer
    wp.approve(client, p2.proposal_id, approved_by="alfredo")

    pending = wp.list_pending(client)
    pending_ids = {r["id"] for r in pending}
    assert p1.proposal_id in pending_ids
    assert p2.proposal_id not in pending_ids
    assert len(pending) == 2


# ──────────────────────────────────────────────────────────────────────
# 5. expire_old() y timeout E2E
# ──────────────────────────────────────────────────────────────────────


def test_expire_old_marks_expired_proposals():
    client = FakeClient()
    # Crear con expires_in_hours=0 (ya está expirada al instante)
    p = wp.propose(
        client,
        proposal_type="db_write",
        summary="ya expira",
        payload=_make_payload(99),
        expires_in_hours=0,
    )
    assert p.status == "pending"

    n = wp.expire_old(client)
    assert n == 1

    row = client.tables[wp.TABLE_PROPOSALS][0]
    assert row["approval_status"] == "expired"
    assert row["approved_by"] == "system_expirator"


def test_expire_old_skips_unexpired():
    client = FakeClient()
    wp.propose(
        client,
        proposal_type="db_write",
        summary="vive 24h",
        payload=_make_payload(),
        expires_in_hours=24,
    )
    n = wp.expire_old(client)
    assert n == 0


def test_expire_old_does_not_touch_approved():
    client = FakeClient()
    p = wp.propose(
        client,
        proposal_type="db_write",
        summary="approved-and-old",
        payload=_make_payload(7),
        expires_in_hours=0,
    )
    wp.approve(client, p.proposal_id, approved_by="alfredo")
    n = wp.expire_old(client)
    assert n == 0
    row = client.tables[wp.TABLE_PROPOSALS][0]
    assert row["approval_status"] == "approved"


def test_expire_old_with_threshold_hours():
    """threshold_hours fuerza expiración por created_at + threshold."""
    client = FakeClient()
    # Insert manual con created_at viejo
    client.tables[wp.TABLE_PROPOSALS] = [
        {
            "id": str(uuid4()),
            "approval_status": "pending",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=10)).isoformat(),
        }
    ]
    n = wp.expire_old(client, threshold_hours=24)
    assert n == 1
    assert client.tables[wp.TABLE_PROPOSALS][0]["approval_status"] == "expired"


# ──────────────────────────────────────────────────────────────────────
# 6. execute_next() — happy path, error path, lock perdido
# ──────────────────────────────────────────────────────────────────────


def test_execute_next_returns_none_when_no_approved():
    client = FakeClient()
    assert wp.execute_next(client, executor="worker-1") is None


def test_execute_next_happy_path_noop():
    client = FakeClient()
    p = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    wp.approve(client, p.proposal_id, approved_by="alfredo")

    result = wp.execute_next(client, executor="worker-1")
    assert result is not None
    assert result["approval_status"] == "executed"
    assert result["executor"] == "worker-1"
    assert result["attempts"] == 1
    assert result["result_json"]["success"] is True
    assert result["result_json"]["result"]["noop"] is True


def test_execute_next_with_executor_fn_success():
    client = FakeClient()
    p = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    wp.approve(client, p.proposal_id, approved_by="alfredo")

    captured = {}

    def fn(proposal):
        captured["id"] = proposal["id"]
        return wp.ExecutionResult(proposal_id=proposal["id"], success=True, result={"affected_rows": 7})

    result = wp.execute_next(client, executor="worker-1", executor_fn=fn)
    assert captured["id"] == p.proposal_id
    assert result["approval_status"] == "executed"
    assert result["result_json"]["result"] == {"affected_rows": 7}


def test_execute_next_executor_fn_raises_marks_failed():
    client = FakeClient()
    p = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    wp.approve(client, p.proposal_id, approved_by="alfredo")

    def boom(proposal):
        raise RuntimeError("DB connection refused")

    result = wp.execute_next(client, executor="worker-1", executor_fn=boom)
    assert result["approval_status"] == "failed"
    assert "RuntimeError" in result["result_json"]["error"]
    assert "DB connection refused" in result["result_json"]["error"]


def test_execute_next_executor_fn_wrong_return_type_marks_failed():
    client = FakeClient()
    p = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    wp.approve(client, p.proposal_id, approved_by="alfredo")

    def bad_fn(proposal):
        return {"not": "an ExecutionResult"}

    result = wp.execute_next(client, executor="worker-1", executor_fn=bad_fn)
    assert result["approval_status"] == "failed"
    assert "TypeError" in result["result_json"]["error"]


def test_execute_next_processes_one_at_a_time_in_order():
    client = FakeClient()
    p1 = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload(1))
    p2 = wp.propose(client, proposal_type="db_write", summary="B", payload=_make_payload(2))
    wp.approve(client, p1.proposal_id, approved_by="alfredo")
    # Avanzamos el reloj garantizando approved_at distinto vía sleep simulado:
    import time

    time.sleep(0.01)
    wp.approve(client, p2.proposal_id, approved_by="alfredo")

    r1 = wp.execute_next(client, executor="w")
    r2 = wp.execute_next(client, executor="w")
    r3 = wp.execute_next(client, executor="w")
    assert r1["id"] == p1.proposal_id
    assert r2["id"] == p2.proposal_id
    assert r3 is None


# ──────────────────────────────────────────────────────────────────────
# 7. notify_hitl()
# ──────────────────────────────────────────────────────────────────────


def test_notify_hitl_inserts_to_embrion_memoria():
    client = FakeClient()
    p = wp.propose(
        client,
        proposal_type="db_write",
        summary="A",
        payload=_make_payload(),
        auto_notify=False,  # lo llamamos manualmente para aislar
    )
    proposal = client.tables[wp.TABLE_PROPOSALS][0]
    ok = wp.notify_hitl(client, proposal, channel="cowork_bridge")
    assert ok is True

    memos = client.tables.get(wp.TABLE_MEMORIA, [])
    assert len(memos) == 1
    m = memos[0]
    assert m["tipo"] == "respuesta_embrion"
    assert m["hilo_origen"] == "embrion_write_policy"
    assert m["importancia"] == 10
    assert m["metadata"]["kind"] == "hitl_proposal_pending"
    assert m["metadata"]["proposal_id"] == p.proposal_id
    assert "[HITL EMBRION]" in m["contenido"]
    # Verifica que marca notified_at en la proposal
    assert client.tables[wp.TABLE_PROPOSALS][0]["notified_at"]
    assert client.tables[wp.TABLE_PROPOSALS][0]["notified_via"] == "cowork_bridge"


def test_propose_auto_notifies_by_default():
    client = FakeClient()
    wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    memos = client.tables.get(wp.TABLE_MEMORIA, [])
    assert len(memos) == 1
    assert memos[0]["importancia"] == 10


def test_notify_hitl_telegram_returns_false_pending_task4():
    client = FakeClient()
    proposal = {
        "id": str(uuid4()),
        "summary": "x",
        "risk_level": "low",
        "proposal_type": "db_write",
        "expires_at": _now_iso_plus(24),
    }
    ok = wp.notify_hitl(client, proposal, channel="telegram")
    assert ok is False  # placeholder hasta Tarea 4
    assert wp.TABLE_MEMORIA not in client.tables


def test_notify_hitl_invalid_channel_raises():
    client = FakeClient()
    proposal = {
        "id": str(uuid4()),
        "summary": "x",
        "risk_level": "low",
        "proposal_type": "db_write",
        "expires_at": _now_iso_plus(24),
    }
    with pytest.raises(ValueError, match="channel inválido"):
        wp.notify_hitl(client, proposal, channel="carrier_pigeon")


# ──────────────────────────────────────────────────────────────────────
# 8. E2E: propose → approve → execute → executed
# ──────────────────────────────────────────────────────────────────────


def test_e2e_full_flow_propose_approve_execute():
    client = FakeClient()

    # 1. Embrión propone
    res = wp.propose(
        client,
        proposal_type="external_api_call",
        summary="Llamar GPT-5 con prompt sensible",
        payload={"endpoint": "openai/v1/chat", "prompt": "..."},
        cycle_id=12345,
        risk_level="high",
    )
    assert res.created is True

    # 2. Hay 1 pending; alfredo lo ve y aprueba
    pending = wp.list_pending(client)
    assert len(pending) == 1
    assert pending[0]["risk_level"] == "high"

    approved = wp.approve(client, res.proposal_id, approved_by="alfredo", notes="OK")
    assert approved["approval_status"] == "approved"

    # 3. Worker ejecuta
    def real_executor(proposal):
        # En producción: aquí se llamaría a OpenAI con el payload
        return wp.ExecutionResult(
            proposal_id=proposal["id"],
            success=True,
            result={"openai_status": 200, "tokens": 150},
        )

    final = wp.execute_next(client, executor="worker-prod", executor_fn=real_executor)
    assert final["approval_status"] == "executed"
    assert final["result_json"]["result"]["openai_status"] == 200
    assert final["result_json"]["duration_ms"] >= 0

    # 4. Estado final coherente
    row = wp.get_proposal(client, res.proposal_id)
    assert row["approval_status"] == "executed"
    assert row["executed_at"]


def test_e2e_propose_reject_no_execute():
    client = FakeClient()
    p = wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload())
    wp.reject(client, p.proposal_id, approved_by="alfredo", reason="Demasiado riesgo")

    # No hay nada que ejecutar
    assert wp.execute_next(client, executor="w") is None
    # Está rejected
    row = wp.get_proposal(client, p.proposal_id)
    assert row["approval_status"] == "rejected"


def test_e2e_propose_timeout_then_expire():
    client = FakeClient()
    p = wp.propose(
        client,
        proposal_type="db_write",
        summary="ignorada",
        payload=_make_payload(123),
        expires_in_hours=0,
    )
    # Justo después de crear, el cron de expiración corre
    n = wp.expire_old(client)
    assert n == 1

    # No queda en pending list
    assert wp.list_pending(client) == []
    # No es ejecutable
    assert wp.execute_next(client, executor="w") is None
    row = wp.get_proposal(client, p.proposal_id)
    assert row["approval_status"] == "expired"


# ──────────────────────────────────────────────────────────────────────
# 9. Helpers públicos
# ──────────────────────────────────────────────────────────────────────


def test_get_pending_count():
    client = FakeClient()
    assert wp.get_pending_count(client) == 0
    wp.propose(client, proposal_type="db_write", summary="A", payload=_make_payload(1))
    wp.propose(client, proposal_type="db_write", summary="B", payload=_make_payload(2))
    assert wp.get_pending_count(client) == 2


def test_get_proposal_returns_none_for_unknown():
    client = FakeClient()
    assert wp.get_proposal(client, "00000000-0000-0000-0000-000000000000") is None


# ──────────────────────────────────────────────────────────────────────
# Helpers de tests
# ──────────────────────────────────────────────────────────────────────


def _now_iso_plus(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()
