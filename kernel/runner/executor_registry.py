"""Executor registry para el proposal_processor.

Mapea proposal_type → función ejecutora. Cada función recibe el row
completo de la proposal y retorna ExecutionResult.

Doctrina v1 (Sprint EMBRION-NEEDS-002):
  - Default: TODOS los executors son noop (success=True, result={"noop": True}).
  - Opt-in real: si proposal.payload_json.executor == 'real', se invoca el
    ejecutor real correspondiente. Esto permite smoke testing del worker en
    producción sin riesgo de side-effects accidentales.
  - code_commit: TODO Sprint futuro (clonar repo, commit, push). Por ahora noop.
  - db_write: ejecuta SQL parametrizado contra DB con service_role.
  - external_api_call: HTTP request según payload.method/url/body.
  - other: noop fijo.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, Optional

import httpx
import structlog

from kernel.embrion_write_policy import ExecutionResult

logger = structlog.get_logger("executor_registry")

ExecutorFn = Callable[[Dict[str, Any]], ExecutionResult]


def _is_real(proposal: Dict[str, Any]) -> bool:
    """True si la proposal explícitamente solicita ejecución real."""
    payload = proposal.get("payload_json") or {}
    if not isinstance(payload, dict):
        return False
    return payload.get("executor") == "real"


def _exec_noop(proposal: Dict[str, Any]) -> ExecutionResult:
    """Executor inocuo: marca success sin side-effects."""
    return ExecutionResult(
        proposal_id=str(proposal["id"]),
        success=True,
        result={
            "noop": True,
            "reason": "default noop executor (Sprint EMBRION-NEEDS-002 v1)",
            "proposal_type": proposal.get("proposal_type"),
        },
    )


def _exec_external_api_call(proposal: Dict[str, Any]) -> ExecutionResult:
    """Ejecuta HTTP request según payload.

    Espera en payload_json: {method, url, headers?, body?, timeout_sec?, executor='real'}
    """
    if not _is_real(proposal):
        return _exec_noop(proposal)

    payload = proposal["payload_json"]
    method = (payload.get("method") or "GET").upper()
    url = payload.get("url")
    if not url:
        return ExecutionResult(
            proposal_id=str(proposal["id"]),
            success=False,
            error="missing payload.url",
        )

    headers = payload.get("headers") or {}
    body = payload.get("body")
    timeout = float(payload.get("timeout_sec") or 10)

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.request(
                method,
                url,
                headers=headers,
                json=body if isinstance(body, (dict, list)) else None,
                content=body if isinstance(body, (str, bytes)) else None,
            )
        success = 200 <= resp.status_code < 300
        return ExecutionResult(
            proposal_id=str(proposal["id"]),
            success=success,
            result={
                "status_code": resp.status_code,
                "url": url,
                "method": method,
                "response_text_preview": resp.text[:500],
            },
            error=None if success else f"HTTP {resp.status_code}",
        )
    except Exception as exc:  # noqa: BLE001
        return ExecutionResult(
            proposal_id=str(proposal["id"]),
            success=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def _exec_db_write(proposal: Dict[str, Any]) -> ExecutionResult:
    """Ejecuta SQL parametrizado contra DB con service_role.

    Espera en payload_json: {sql, params?, executor='real'}.
    Opt-in obligatorio — sin executor='real' es noop.
    """
    if not _is_real(proposal):
        return _exec_noop(proposal)

    payload = proposal["payload_json"]
    sql = payload.get("sql")
    if not sql or not isinstance(sql, str):
        return ExecutionResult(
            proposal_id=str(proposal["id"]),
            success=False,
            error="missing or invalid payload.sql",
        )

    db_url = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        return ExecutionResult(
            proposal_id=str(proposal["id"]),
            success=False,
            error="SUPABASE_DB_URL / DATABASE_URL env var not configured",
        )

    params = payload.get("params") or []

    try:
        import psycopg

        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                affected = cur.rowcount
        return ExecutionResult(
            proposal_id=str(proposal["id"]),
            success=True,
            result={"rows_affected": affected, "sql_preview": sql[:200]},
        )
    except Exception as exc:  # noqa: BLE001
        return ExecutionResult(
            proposal_id=str(proposal["id"]),
            success=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def _exec_code_commit(proposal: Dict[str, Any]) -> ExecutionResult:
    """code_commit executor — diferido a Sprint futuro.

    Por ahora siempre noop. Cuando se implemente, requerirá: clonar repo target,
    aplicar diff de payload, hacer commit, push, abrir PR.
    """
    return ExecutionResult(
        proposal_id=str(proposal["id"]),
        success=True,
        result={
            "noop": True,
            "reason": "code_commit executor diferido a Sprint futuro",
            "deferred_to_sprint": "EMBRION-NEEDS-003+",
        },
    )


class ExecutorRegistry:
    """Registry que mapea proposal_type a su executor."""

    def __init__(self, overrides: Optional[Dict[str, ExecutorFn]] = None) -> None:
        self._executors: Dict[str, ExecutorFn] = {
            "code_commit": _exec_code_commit,
            "db_write": _exec_db_write,
            "external_api_call": _exec_external_api_call,
            "other": _exec_noop,
        }
        if overrides:
            self._executors.update(overrides)

    def dispatch(self, proposal: Dict[str, Any]) -> ExecutionResult:
        """Ejecuta la proposal según su proposal_type.

        Si el tipo no está registrado, retorna noop con success=True.
        """
        proposal_type = proposal.get("proposal_type") or "other"
        executor = self._executors.get(proposal_type, _exec_noop)
        try:
            return executor(proposal)
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "executor_registry.unhandled_exception",
                proposal_id=str(proposal.get("id")),
                proposal_type=proposal_type,
                error=str(exc),
            )
            return ExecutionResult(
                proposal_id=str(proposal.get("id", "unknown")),
                success=False,
                error=f"unhandled {type(exc).__name__}: {exc}",
            )

    def register(self, proposal_type: str, fn: ExecutorFn) -> None:
        """Registra/sobrescribe un executor para un tipo dado."""
        self._executors[proposal_type] = fn
