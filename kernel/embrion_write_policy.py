"""
kernel/embrion_write_policy.py — Write Policy con HITL real para el Embrión

Sprint EMBRION-NEEDS-001, Tarea 3.
Origen: bridge/sprints_propuestos/sprint_EMBRION_NEEDS_001.md
Handoff: bridge/cowork_to_manus_SPRINT_EMBRION_NEEDS_001_2026_05_10.md

Misión:
  Reemplazar la ejecución directa de escrituras del embrión (db_write,
  code_commit, external_api_call) por una cola de proposals que requieren
  aprobación humana antes de ejecutarse. Cierra el riesgo de que el embrión
  haga mutaciones autónomas no auditadas.

Flujo:
    embrion -> propose() -> notify_hitl() -> humano aprueba/rechaza ->
    worker ejecuta -> resultado registrado

Estados (tabla embrion_write_proposals):
    pending → approved → executing → executed | failed
            → rejected
            → expired (default 24h)

Diseño:
  - Tabla `embrion_write_proposals` (migración 0004, ya en producción).
  - Idempotencia vía sha256 del payload normalizado (UNIQUE constraint en DB).
  - Notificación HITL fallback: insert a embrion_memoria con tipo
    'respuesta_embrion' importancia 10 (Cowork lo lee del MCP).
    Cuando Tarea 4 (bot Telegram) se complete, se añade canal Telegram.
  - Optimistic concurrency: UPDATE ... WHERE approval_status = expected.
  - Cliente REST mínimo (mismo patrón que embrion_budget y embrion_self_verifier),
    inyectable en tests sin red.

API pública:
    propose(client, *, proposal_type, summary, payload, ...) -> ProposalCreated
    approve(client, proposal_id, *, approved_by, notes=None) -> dict
    reject(client, proposal_id, *, approved_by, reason) -> dict
    list_pending(client, *, limit=20, only_unexpired=True) -> list[dict]
    expire_old(client, *, threshold_hours=None) -> int
    execute_next(client, executor, *, executor_fn=None) -> Optional[dict]
    notify_hitl(client, proposal, *, channel='cowork_bridge') -> bool
    get_pending_count(client) -> int
    get_proposal(client, proposal_id) -> Optional[dict]

Configuración via env vars:
    EMBRION_PROPOSAL_TTL_HOURS  default "24"
    EMBRION_HITL_CHANNEL        default "cowork_bridge"
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

try:
    import structlog

    logger = structlog.get_logger("embrion.write_policy")
except ImportError:  # pragma: no cover
    import logging

    logger = logging.getLogger("embrion.write_policy")


# ── Constantes y configuración

PROPOSAL_TYPES = frozenset(
    {
        "code_commit",
        "db_write",
        "external_api_call",
        "other",
    }
)

APPROVAL_STATUSES = frozenset(
    {
        "pending",
        "approved",
        "rejected",
        "expired",
        "executing",
        "executed",
        "failed",
    }
)

RISK_LEVELS = frozenset({"low", "medium", "high", "critical"})

DEFAULT_EXPIRATION_HOURS = int(os.environ.get("EMBRION_PROPOSAL_TTL_HOURS", "24"))
NOTIFICATION_CHANNEL_DEFAULT = os.environ.get("EMBRION_HITL_CHANNEL", "cowork_bridge")

TABLE_PROPOSALS = "embrion_write_proposals"
TABLE_MEMORIA = "embrion_memoria"


# ── Cliente REST mínimo (mismo patrón que embrion_budget._SupabaseRest pero
# con select/insert/update; reusamos firma esperada por los tests del sprint)


class _SupabaseRest:
    """Cliente REST mínimo y testeable. Evita supabase-py para mantener
    superficie chica e inyectable vía monkeypatch en tests."""

    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key

    def _headers(self, prefer: Optional[str] = None):
        h = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }
        if prefer:
            h["Prefer"] = prefer
        return h

    def select(self, table: str, params: dict, prefer: Optional[str] = None):
        import requests

        r = requests.get(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(prefer=prefer),
            params=params,
            timeout=15,
        )
        r.raise_for_status()
        return r.json(), r.headers

    def insert(self, table: str, payload: dict | list[dict]):
        import requests

        r = requests.post(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(prefer="return=representation"),
            json=payload,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()

    def update(self, table: str, params: dict, payload: dict):
        """PATCH a /rest/v1/{table}?<filters>. Devuelve filas afectadas."""
        import requests

        r = requests.patch(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(prefer="return=representation"),
            params=params,
            json=payload,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()


def _get_supabase_client() -> _SupabaseRest:
    url = os.environ.get("SUPABASE_URL", "https://xsumzuhwmivjgftsneov.supabase.co")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("SUPA_KEY")
    if not key:
        raise RuntimeError(
            "embrion_write_policy: ninguna env var Supabase encontrada "
            "(probadas: SUPABASE_SERVICE_KEY, SUPABASE_KEY, SUPA_KEY)"
        )
    return _SupabaseRest(url=url, key=key)


# ── Dataclasses


@dataclass
class ProposalCreated:
    """Resultado de propose()."""

    proposal_id: str
    created: bool  # True si se insertó, False si idempotency key colisionó
    status: str  # status actual
    expires_at: str  # ISO8601
    summary: str
    risk_level: str


@dataclass
class ExecutionResult:
    """Resultado de la ejecución de una proposal aprobada."""

    proposal_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration_ms: int = 0


# ── Helpers internos


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_payload_for_hash(payload: dict) -> str:
    """Serialización determinística del payload para idempotency_key."""
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)


def compute_idempotency_key(
    proposal_type: str,
    payload: dict,
    *,
    extra_salt: str = "",
) -> str:
    """SHA-256 hexdigest del proposal_type + payload normalizado + salt opcional.

    Útil para evitar duplicar proposals idénticas. El salt opcional permite
    al embrión forzar un nuevo proposal (ej. retry deliberado) sin chocar.
    """
    h = hashlib.sha256()
    h.update(proposal_type.encode("utf-8"))
    h.update(b"|")
    h.update(_normalize_payload_for_hash(payload).encode("utf-8"))
    if extra_salt:
        h.update(b"|")
        h.update(extra_salt.encode("utf-8"))
    return h.hexdigest()


# ── API pública


def propose(
    client: Any,
    *,
    proposal_type: str,
    summary: str,
    payload: dict,
    proposed_by: str = "embrion_loop",
    cycle_id: Optional[int] = None,
    latido_id: Optional[str] = None,
    risk_level: str = "medium",
    idempotency_key: Optional[str] = None,
    expires_in_hours: Optional[int] = None,
    auto_notify: bool = True,
    notification_channel: str = NOTIFICATION_CHANNEL_DEFAULT,
) -> ProposalCreated:
    """Crear una proposal pendiente.

    Si `idempotency_key` colisiona con una proposal existente, retorna la
    existente sin crear duplicado.

    Si `auto_notify=True`, intenta enviar notificación HITL post-creación.
    """
    if proposal_type not in PROPOSAL_TYPES:
        raise ValueError(f"proposal_type inválido: {proposal_type!r}. Válidos: {sorted(PROPOSAL_TYPES)}")
    if risk_level not in RISK_LEVELS:
        raise ValueError(f"risk_level inválido: {risk_level!r}. Válidos: {sorted(RISK_LEVELS)}")
    if not isinstance(payload, dict):
        raise TypeError("payload debe ser dict serializable a JSON")
    if not summary or not summary.strip():
        raise ValueError("summary no puede estar vacío")

    if idempotency_key is None:
        idempotency_key = compute_idempotency_key(proposal_type, payload)

    ttl_hours = expires_in_hours if expires_in_hours is not None else DEFAULT_EXPIRATION_HOURS
    expires_at = (_now_dt() + timedelta(hours=ttl_hours)).isoformat()

    # 1) Verificar idempotency
    existing, _ = client.select(
        TABLE_PROPOSALS,
        {
            "idempotency_key": f"eq.{idempotency_key}",
            "select": "id,approval_status,expires_at,summary,risk_level",
            "limit": 1,
        },
    )
    if existing:
        e = existing[0]
        logger.info(
            "embrion_write_policy.propose_idempotent_hit",
            proposal_id=e["id"],
            existing_status=e["approval_status"],
        )
        return ProposalCreated(
            proposal_id=str(e["id"]),
            created=False,
            status=e["approval_status"],
            expires_at=e["expires_at"],
            summary=e["summary"],
            risk_level=e["risk_level"],
        )

    # 2) Insert
    row = {
        "proposed_by": proposed_by,
        "cycle_id": cycle_id,
        "latido_id": latido_id,
        "idempotency_key": idempotency_key,
        "proposal_type": proposal_type,
        "summary": summary.strip(),
        "payload_json": payload,
        "risk_level": risk_level,
        "approval_status": "pending",
        "expires_at": expires_at,
    }
    inserted = client.insert(TABLE_PROPOSALS, row)
    if not inserted:
        raise RuntimeError(f"propose() insert no retornó data: {inserted!r}")
    new = inserted[0] if isinstance(inserted, list) else inserted
    proposal_id = str(new["id"])

    logger.info(
        "embrion_write_policy.proposed",
        proposal_id=proposal_id,
        proposal_type=proposal_type,
        risk_level=risk_level,
        cycle_id=cycle_id,
    )

    # 3) Notificación HITL
    if auto_notify:
        try:
            notify_hitl(client, new, channel=notification_channel)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "embrion_write_policy.notify_failed",
                proposal_id=proposal_id,
                error=str(exc),
            )

    return ProposalCreated(
        proposal_id=proposal_id,
        created=True,
        status="pending",
        expires_at=new["expires_at"],
        summary=new["summary"],
        risk_level=new["risk_level"],
    )


def approve(
    client: Any,
    proposal_id: str,
    *,
    approved_by: str,
    notes: Optional[str] = None,
) -> dict:
    """Marcar proposal como approved. Solo permitido sobre status='pending'."""
    rows, _ = client.select(
        TABLE_PROPOSALS,
        {"id": f"eq.{proposal_id}", "select": "*", "limit": 1},
    )
    if not rows:
        raise ValueError(f"proposal {proposal_id} no encontrada")
    p = rows[0]
    if p["approval_status"] != "pending":
        raise ValueError(f"proposal {proposal_id} no está pending (status actual: {p['approval_status']!r})")

    update = {
        "approval_status": "approved",
        "approved_by": approved_by,
        "approved_at": _now_iso(),
    }
    if notes:
        update["result_json"] = {"approval_notes": notes}

    updated = client.update(
        TABLE_PROPOSALS,
        {"id": f"eq.{proposal_id}", "approval_status": "eq.pending"},
        update,
    )
    if not updated:
        raise RuntimeError(
            f"approve race condition en proposal {proposal_id} — otro agente cambió el status mientras aprobábamos"
        )

    logger.info(
        "embrion_write_policy.approved",
        proposal_id=proposal_id,
        approved_by=approved_by,
    )
    return updated[0] if isinstance(updated, list) else updated


def reject(
    client: Any,
    proposal_id: str,
    *,
    approved_by: str,
    reason: str,
) -> dict:
    """Marcar proposal como rejected con razón explícita."""
    if not reason or not reason.strip():
        raise ValueError("reject() requiere reason no vacío")

    rows, _ = client.select(
        TABLE_PROPOSALS,
        {"id": f"eq.{proposal_id}", "select": "*", "limit": 1},
    )
    if not rows:
        raise ValueError(f"proposal {proposal_id} no encontrada")
    p = rows[0]
    if p["approval_status"] != "pending":
        raise ValueError(f"proposal {proposal_id} no está pending (status actual: {p['approval_status']!r})")

    update = {
        "approval_status": "rejected",
        "approved_by": approved_by,
        "approved_at": _now_iso(),
        "rejection_reason": reason.strip(),
    }
    updated = client.update(
        TABLE_PROPOSALS,
        {"id": f"eq.{proposal_id}", "approval_status": "eq.pending"},
        update,
    )
    if not updated:
        raise RuntimeError(f"reject race condition en proposal {proposal_id}")

    logger.info(
        "embrion_write_policy.rejected",
        proposal_id=proposal_id,
        approved_by=approved_by,
    )
    return updated[0] if isinstance(updated, list) else updated


def list_pending(
    client: Any,
    *,
    limit: int = 20,
    only_unexpired: bool = True,
) -> list[dict]:
    """Listar proposals pending, ordenadas por created_at ASC (más viejas primero)."""
    params = {
        "approval_status": "eq.pending",
        "select": "*",
        "order": "created_at.asc",
        "limit": str(limit),
    }
    if only_unexpired:
        params["expires_at"] = f"gte.{_now_iso()}"
    rows, _ = client.select(TABLE_PROPOSALS, params)
    return rows or []


def expire_old(
    client: Any,
    *,
    threshold_hours: Optional[int] = None,
) -> int:
    """Marcar como 'expired' todas las proposals pending vencidas.

    Si `threshold_hours` se provee, ignora `expires_at` y usa
    created_at + threshold (útil para forzar expiración por nueva política).

    Retorna el número de proposals expiradas.
    """
    now_iso = _now_iso()

    params = {
        "approval_status": "eq.pending",
        "select": "id,created_at,expires_at",
        "limit": "500",
    }
    if threshold_hours is not None:
        cutoff = (_now_dt() - timedelta(hours=threshold_hours)).isoformat()
        params["created_at"] = f"lte.{cutoff}"
    else:
        params["expires_at"] = f"lte.{now_iso}"

    candidates, _ = client.select(TABLE_PROPOSALS, params)
    if not candidates:
        return 0

    n_total = 0
    for c in candidates:
        updated = client.update(
            TABLE_PROPOSALS,
            {
                "id": f"eq.{c['id']}",
                "approval_status": "eq.pending",
            },
            {
                "approval_status": "expired",
                "approved_at": now_iso,
                "approved_by": "system_expirator",
            },
        )
        if updated:
            n_total += 1

    logger.info("embrion_write_policy.expired_batch", count=n_total)
    return n_total


def execute_next(
    client: Any,
    executor: str,
    *,
    executor_fn: Optional[Callable[[dict], "ExecutionResult"]] = None,
) -> Optional[dict]:
    """Tomar la siguiente proposal en status 'approved' y ejecutarla.

    `executor_fn(proposal)` es la función que sabe ejecutar el payload según
    proposal_type. Si no se provee, este worker solo marca como 'executed' con
    result_json={"noop": True} (útil para tests que no necesitan side-effects).

    Retorna el row final de la proposal, o None si no había nada que ejecutar.

    Race-safe: usa optimistic UPDATE WHERE approval_status='approved' para tomar lock.
    """
    candidates, _ = client.select(
        TABLE_PROPOSALS,
        {
            "approval_status": "eq.approved",
            "select": "*",
            "order": "approved_at.asc",
            "limit": 1,
        },
    )
    if not candidates:
        return None

    p = candidates[0]
    proposal_id = str(p["id"])

    # Optimistic lock
    locked = client.update(
        TABLE_PROPOSALS,
        {"id": f"eq.{proposal_id}", "approval_status": "eq.approved"},
        {
            "approval_status": "executing",
            "executor": executor,
            "attempts": (p.get("attempts") or 0) + 1,
        },
    )
    if not locked:
        logger.info(
            "embrion_write_policy.execute_lock_lost",
            proposal_id=proposal_id,
        )
        return None
    locked_row = locked[0] if isinstance(locked, list) else locked

    # Ejecutar
    started_at = _now_dt()
    if executor_fn is None:
        result = ExecutionResult(
            proposal_id=proposal_id,
            success=True,
            result={"noop": True, "reason": "no executor_fn provided"},
        )
    else:
        try:
            result = executor_fn(locked_row)
            if not isinstance(result, ExecutionResult):
                raise TypeError(f"executor_fn debe retornar ExecutionResult, retornó {type(result).__name__}")
        except Exception as exc:  # noqa: BLE001
            result = ExecutionResult(
                proposal_id=proposal_id,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
            )

    duration_ms = int((_now_dt() - started_at).total_seconds() * 1000)
    result.duration_ms = duration_ms

    # Persistir resultado
    final_status = "executed" if result.success else "failed"
    result_payload = {
        "success": result.success,
        "duration_ms": duration_ms,
        "result": result.result,
        "error": result.error,
    }
    final = client.update(
        TABLE_PROPOSALS,
        {"id": f"eq.{proposal_id}"},
        {
            "approval_status": final_status,
            "executed_at": _now_iso(),
            "result_json": result_payload,
        },
    )

    logger.info(
        "embrion_write_policy.executed",
        proposal_id=proposal_id,
        status=final_status,
        duration_ms=duration_ms,
    )

    if final and isinstance(final, list):
        return final[0]
    return locked_row


def _notify_via_cowork_bridge(client: Any, proposal_id: str, ptype: str, risk: str, text: str) -> bool:
    """Insert a row in embrion_memoria with importancia=10 to wake Alfredo via cowork."""
    memo_row = {
        "tipo": "respuesta_embrion",
        "hilo_origen": "embrion_write_policy",
        "contenido": text,
        "importancia": 10,
        "metadata": {
            "kind": "hitl_proposal_pending",
            "proposal_id": proposal_id,
            "proposal_type": ptype,
            "risk_level": risk,
        },
    }
    try:
        client.insert(TABLE_MEMORIA, memo_row)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "embrion_write_policy.notify_memoria_failed",
            proposal_id=proposal_id,
            error=str(exc),
        )
        return False


def _notify_via_telegram(proposal: dict) -> bool:
    """Send proposal to Telegram with inline keyboard (Aprobar/Rechazar).

    Async-safe: detects existing event loop and adapts.
    Returns True if sent, False on any failure (non-fatal).
    """
    try:
        from kernel.runner.telegram_notifier import TelegramNotifier  # noqa: PLC0415
    except ImportError as exc:
        logger.warning(
            "embrion_write_policy.telegram_notifier_unavailable",
            error=str(exc),
        )
        return False

    notifier = TelegramNotifier()
    if not notifier.enabled:
        logger.info(
            "embrion_write_policy.telegram_disabled",
            hint="set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars",
        )
        return False

    proposal_id = str(proposal.get("id"))
    coro = notifier.send_proposal_for_hitl(
        proposal_id=proposal_id,
        action_type=proposal.get("proposal_type", "other"),
        risk_level=proposal.get("risk_level", "medium"),
        target=proposal.get("summary", "")[:120],
        reason=proposal.get("summary", ""),
        cost_estimate_usd=float(proposal.get("cost_estimate_usd") or 0.0),
        expires_at=str(proposal.get("expires_at") or ""),
    )

    import asyncio  # noqa: PLC0415

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            result = asyncio.run(coro)
            return result is not None
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "embrion_write_policy.telegram_send_exception",
                proposal_id=proposal_id,
                error=str(exc),
            )
            return False
    else:
        # Running loop: schedule fire-and-forget
        loop.create_task(coro)
        logger.info(
            "embrion_write_policy.telegram_scheduled_async",
            proposal_id=proposal_id,
        )
        return True


def _parse_channels(channel: str) -> list[str]:
    """Split a 'cowork_bridge,telegram' CSV string into a list of valid channels."""
    valid = {"cowork_bridge", "telegram"}
    parsed = [c.strip().lower() for c in channel.split(",") if c.strip()]
    invalid = [c for c in parsed if c not in valid]
    if invalid:
        raise ValueError(f"channel inválido: {invalid!r}; permitidos: {sorted(valid)!r}")
    if not parsed:
        raise ValueError("channel vacío")
    return parsed


def notify_hitl(
    client: Any,
    proposal: dict,
    *,
    channel: str = NOTIFICATION_CHANNEL_DEFAULT,
) -> bool:
    """Notificar a Alfredo de una proposal pending.

    Canales soportados (CSV): 'cowork_bridge', 'telegram', o ambos
    ('cowork_bridge,telegram'). Por defecto, sólo cowork_bridge.

    Doctrina: 2 canales independientes garantizan resiliencia. Si telegram está
    caído, cowork_bridge sigue funcionando, y viceversa.

    Retorna True si AL MENOS UN canal notificó exitosamente.
    Retorna False sólo si TODOS los canales fallan (no fatal).
    """
    proposal_id = str(proposal.get("id"))
    summary = proposal.get("summary", "")
    risk = proposal.get("risk_level", "medium")
    ptype = proposal.get("proposal_type", "other")
    expires = proposal.get("expires_at", "")

    text = (
        f"[HITL EMBRION] Proposal {proposal_id[:8]} requiere aprobación.\n"
        f"Tipo: {ptype} | Riesgo: {risk}\n"
        f"Resumen: {summary}\n"
        f"Expira: {expires}\n"
        f"Aprobar: POST /v1/embrion/approve/{proposal_id}\n"
        f"Listar pending: GET /v1/embrion/proposals"
    )

    channels = _parse_channels(channel)
    successes: list[str] = []
    failures: list[str] = []

    for ch in channels:
        if ch == "cowork_bridge":
            if _notify_via_cowork_bridge(client, proposal_id, ptype, risk, text):
                successes.append(ch)
            else:
                failures.append(ch)
        elif ch == "telegram":
            if _notify_via_telegram(proposal):
                successes.append(ch)
            else:
                failures.append(ch)

    if not successes:
        logger.warning(
            "embrion_write_policy.all_channels_failed",
            proposal_id=proposal_id,
            channels=channels,
        )
        return False

    notified_via = ",".join(successes)
    try:
        client.update(
            TABLE_PROPOSALS,
            {"id": f"eq.{proposal_id}"},
            {"notified_at": _now_iso(), "notified_via": notified_via},
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "embrion_write_policy.notify_mark_failed",
            proposal_id=proposal_id,
            error=str(exc),
        )

    logger.info(
        "embrion_write_policy.notified",
        proposal_id=proposal_id,
        succeeded=successes,
        failed=failures,
    )
    return True


# ── Utilidades para integración con embrion_loop / endpoints


def get_pending_count(client: Any) -> int:
    """Helper para checkpoints rápidos. Retorna el conteo de pending vigentes."""
    rows, _ = client.select(
        TABLE_PROPOSALS,
        {
            "approval_status": "eq.pending",
            "expires_at": f"gte.{_now_iso()}",
            "select": "id",
            "limit": "1000",
        },
    )
    return len(rows or [])


def get_proposal(client: Any, proposal_id: str) -> Optional[dict]:
    """Lookup directo por id. Retorna None si no existe."""
    rows, _ = client.select(
        TABLE_PROPOSALS,
        {"id": f"eq.{proposal_id}", "select": "*", "limit": 1},
    )
    return rows[0] if rows else None
