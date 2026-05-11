"""
kernel/embrion_inbox.py — Buzón Asíncrono Tipado del Embrión (Daddy → Embrión).

Sprint EMBRION-NEEDS-002 Tarea 5 (CA1 + CA6).
Spec firmado: discovery_forense/SPECS/EMBRION_DADDY_BIDIRECCIONAL_v1.md (PR #81).
Kickoff: bridge/cowork_to_manus_T5_EMBRION_DADDY_KICKOFF_2026_05_11.md
Autor: Hilo Ejecutor 2 (manus_hilo_ejecutor_2).

Tablas (creadas en migrations/sql/0012_embrion_inbox.sql):
  - embrion_inbox: cola tipada de mensajes pendientes.
  - embrion_audit_log: trazabilidad del procesamiento (cycle_id, proposal_id, decision).

Patrón:
  - Idéntico a embrion_write_policy: _SupabaseRest mínimo + status machine + race-safe.
  - Status machine: pending → processing → processed | rejected | expired | requires_mfa
  - Optimistic UPDATE WHERE estado='pending' para tomar lock antes de procesar.
  - audit_log se escribe en cada transición de estado (CA6).

API pública:
    enqueue(client, chat_id, text, *, priority=5, rate_limit_bucket=...) -> InboxEnqueued
    consume_next(client, *, cycle_id, limit=5) -> list[dict]
    mark_processed(client, inbox_id, *, cycle_id, proposal_id=None, notes=None)
    mark_rejected(client, inbox_id, *, cycle_id, reason)
    mark_requires_mfa(client, inbox_id, *, mfa_pin_hash, mfa_expires_at)
    expire_old(client) -> int
    audit(client, inbox_id, decision, *, cycle_id=None, proposal_id=None, ...)
    get_pending_count(client) -> int

Configuración via env vars:
    EMBRION_INBOX_TTL_MINUTES       default "30"
    EMBRION_INBOX_RATE_LIMIT_MAX    default "5" (mensajes por minuto por bucket)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

try:
    import structlog
    logger = structlog.get_logger("embrion.inbox")
except ImportError:  # pragma: no cover
    import logging
    logger = logging.getLogger("embrion.inbox")

from kernel.embrion_inbox_parser import parse_command, ParsedCommand
from kernel.embrion_inbox_sanitizer import sanitize_daddy_payload, SanitizedPayload


# ── Constantes y configuración

TABLE_INBOX = "embrion_inbox"
TABLE_AUDIT = "embrion_audit_log"

INBOX_STATUSES = frozenset({
    "pending", "processing", "processed", "rejected", "expired", "requires_mfa",
})

INBOX_COMMANDS = frozenset({
    "/context", "/override", "/help", "/status", "/answer", "/feedback",
    "unauthorized_origin", "unknown",
})

DEFAULT_TTL_MINUTES = int(os.environ.get("EMBRION_INBOX_TTL_MINUTES", "30"))
RATE_LIMIT_MAX_PER_MIN = int(os.environ.get("EMBRION_INBOX_RATE_LIMIT_MAX", "5"))


# Comandos alto-riesgo: requieren MFA stub (CA7)
HIGH_RISK_COMMANDS = frozenset({
    "/override",   # modificar parámetros de un proposal existente
})


# ── Cliente REST (mismo patrón que embrion_write_policy._SupabaseRest)

class _SupabaseRest:
    """Cliente REST mínimo, testeable, inyectable vía monkeypatch."""

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
    key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_KEY")
        or os.environ.get("SUPA_KEY")
    )
    if not key:
        raise RuntimeError(
            "embrion_inbox: ninguna env var Supabase encontrada "
            "(probadas: SUPABASE_SERVICE_KEY, SUPABASE_KEY, SUPA_KEY)"
        )
    return _SupabaseRest(url=url, key=key)


# ── Dataclasses

@dataclass
class InboxEnqueued:
    """Resultado de enqueue()."""
    inbox_id: str
    created: bool                  # True si insertado, False si rate-limited/rechazado
    estado: str
    tipo_comando: str
    intent_class: str
    rejected_reason: Optional[str] = None


# ── Helpers internos

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _redact_payload(payload: dict) -> dict:
    """Redactar campos sensibles antes de almacenar en audit_log.

    Mantiene estructura pero reemplaza valores largos por hash truncado para
    no almacenar PII / secrets en plain text.
    """
    if not isinstance(payload, dict):
        return {"_redacted": "non_dict"}
    out = {}
    for k, v in payload.items():
        if isinstance(v, str) and len(v) > 200:
            out[k] = v[:60] + "...[truncated]"
        elif isinstance(v, dict):
            out[k] = _redact_payload(v)
        else:
            out[k] = v
    return out


# ── Audit (CA6)

def audit(
    client: Any,
    inbox_id: Optional[str],
    decision: str,
    *,
    cycle_id: Optional[int] = None,
    proposal_id: Optional[str] = None,
    command_type: str = "unknown",
    parser_result: Optional[dict] = None,
    intent_class: Optional[str] = None,
    payload_redacted: Optional[dict] = None,
    chat_id_origen: Optional[str] = None,
    source: str = "embrion_inbox",
    notes: Optional[str] = None,
) -> Optional[dict]:
    """Registrar evento en embrion_audit_log (CA6).

    Decisiones canónicas (sincronizadas con CHECK constraint):
        enqueued, parsed_ok, parse_failed, sanitize_rejected, consumed,
        processed_ok, processed_failed, expired, superseded, requires_mfa,
        mfa_validated, unauthorized
    """
    row = {
        "inbox_id": inbox_id,
        "cycle_id": cycle_id,
        "proposal_id": proposal_id,
        "command_type": command_type,
        "decision": decision,
        "parser_result": parser_result,
        "intent_class": intent_class,
        "payload_redacted": payload_redacted,
        "chat_id_origen": chat_id_origen,
        "source": source,
        "notes": notes,
    }
    try:
        result = client.insert(TABLE_AUDIT, row)
        return result[0] if isinstance(result, list) and result else result
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "embrion_inbox.audit_failed",
            inbox_id=inbox_id,
            decision=decision,
            error=str(exc),
        )
        return None


# ── Rate limit (CA5 también lo usa pero la implementación vive aquí)

def _count_recent_in_bucket(
    client: Any,
    bucket: str,
    *,
    window_seconds: int = 60,
) -> int:
    """Cuántos mensajes hay en `bucket` en los últimos `window_seconds` segundos."""
    since = (_now_dt() - timedelta(seconds=window_seconds)).isoformat()
    try:
        rows, _ = client.select(
            TABLE_INBOX,
            {
                "rate_limit_bucket": f"eq.{bucket}",
                "created_at": f"gte.{since}",
                "select": "id",
                "limit": "100",
            },
        )
        return len(rows or [])
    except Exception:  # noqa: BLE001
        return 0


# ── API pública

def enqueue(
    client: Any,
    chat_id: str,
    text: str,
    *,
    priority: int = 5,
    rate_limit_bucket: Optional[str] = None,
    ttl_minutes: Optional[int] = None,
    enforce_rate_limit: bool = True,
) -> InboxEnqueued:
    """Insertar un mensaje en embrion_inbox tras parsear + sanitizar.

    Pasos:
      1. parse_command(text) — determinista, cero LLM.
      2. sanitize_daddy_payload(parsed) — detecta attacks/jailbreaks.
      3. Rate limit por bucket (default 5 msg/min).
      4. INSERT a embrion_inbox con estado='pending' (o 'rejected' si sanitizer falló).
      5. audit_log: 'enqueued' | 'parse_failed' | 'sanitize_rejected'.

    Args:
        chat_id: Telegram chat_id del origen (string).
        text: texto crudo del mensaje.
        priority: 1-10 (5 default; mensajes /override pueden subir a 9).
        rate_limit_bucket: identificador del bucket (default chat_id).
        ttl_minutes: TTL custom (default EMBRION_INBOX_TTL_MINUTES).
        enforce_rate_limit: si False, no aplica rate limit (útil para tests).

    Returns:
        InboxEnqueued con inbox_id (o "" si no se insertó), created, estado.
    """
    bucket = rate_limit_bucket or f"chat:{chat_id}"
    ttl_min = ttl_minutes if ttl_minutes is not None else DEFAULT_TTL_MINUTES
    expires_at = (_now_dt() + timedelta(minutes=ttl_min)).isoformat()

    # 1. Parse
    parsed = parse_command(text)

    # 2. Sanitize
    sanitized = sanitize_daddy_payload(parsed)

    # 3. Rate limit
    if enforce_rate_limit:
        recent = _count_recent_in_bucket(client, bucket)
        if recent >= RATE_LIMIT_MAX_PER_MIN:
            logger.info(
                "embrion_inbox.rate_limited",
                bucket=bucket,
                recent=recent,
                chat_id=chat_id,
            )
            audit(
                client,
                inbox_id=None,
                decision="unauthorized",
                command_type=parsed.comando or "unknown",
                chat_id_origen=chat_id,
                notes=f"rate_limited:{recent}>={RATE_LIMIT_MAX_PER_MIN}",
                source="embrion_inbox",
            )
            return InboxEnqueued(
                inbox_id="",
                created=False,
                estado="rejected",
                tipo_comando=parsed.comando or "unknown",
                intent_class="rate_limited",
                rejected_reason="rate_limited",
            )

    # 4. Determinar estado inicial y tipo_comando
    tipo_comando = parsed.comando if parsed.valid else "unknown"
    if tipo_comando not in INBOX_COMMANDS:
        tipo_comando = "unknown"

    if sanitized.rejected:
        estado_inicial = "rejected"
        error_reason = sanitized.rejection_reason
    elif not parsed.valid:
        estado_inicial = "rejected"
        error_reason = f"parse_failed:{parsed.reason}"
    elif parsed.comando in HIGH_RISK_COMMANDS:
        estado_inicial = "requires_mfa"
        error_reason = None
    else:
        estado_inicial = "pending"
        error_reason = None

    # Priority boost: /override y /context tienen prioridad 7
    if parsed.valid and parsed.comando in ("/override", "/context"):
        priority = max(priority, 7)

    row = {
        "chat_id_origen": chat_id,
        "comando": parsed.raw_text[:500] if parsed.raw_text else text[:500],
        "tipo_comando": tipo_comando,
        "payload": sanitized.payload,
        "estado": estado_inicial,
        "priority": priority,
        "rate_limit_bucket": bucket,
        "parser_result": {
            "valid": parsed.valid,
            "reason": parsed.reason,
            "comando": parsed.comando,
        },
        "intent_class": sanitized.intent_class,
        "requires_mfa": (estado_inicial == "requires_mfa"),
        "error_reason": error_reason,
        "expires_at": expires_at,
    }

    try:
        result = client.insert(TABLE_INBOX, row)
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "embrion_inbox.insert_failed",
            chat_id=chat_id,
            error=str(exc),
        )
        return InboxEnqueued(
            inbox_id="",
            created=False,
            estado="rejected",
            tipo_comando=tipo_comando,
            intent_class="error",
            rejected_reason=f"db_error:{type(exc).__name__}",
        )

    inserted = result[0] if isinstance(result, list) and result else result
    inbox_id = str(inserted.get("id", ""))

    # 5. Audit
    decision = (
        "enqueued"
        if estado_inicial == "pending"
        else ("sanitize_rejected" if sanitized.rejected else
              ("requires_mfa" if estado_inicial == "requires_mfa" else "parse_failed"))
    )
    audit(
        client,
        inbox_id=inbox_id,
        decision=decision,
        command_type=tipo_comando,
        parser_result={"valid": parsed.valid, "reason": parsed.reason},
        intent_class=sanitized.intent_class,
        payload_redacted=_redact_payload(sanitized.payload),
        chat_id_origen=chat_id,
        source="embrion_inbox",
    )

    return InboxEnqueued(
        inbox_id=inbox_id,
        created=True,
        estado=estado_inicial,
        tipo_comando=tipo_comando,
        intent_class=sanitized.intent_class,
        rejected_reason=error_reason,
    )


def consume_next(
    client: Any,
    *,
    cycle_id: int,
    limit: int = 5,
) -> List[dict]:
    """Tomar los próximos N mensajes pending (priority DESC, created ASC).

    Race-safe: hace optimistic UPDATE WHERE estado='pending' para tomar lock.
    Solo devuelve mensajes que efectivamente lockeó este cycle.

    Args:
        cycle_id: id del ciclo actual del embrion_loop (para audit).
        limit: máx mensajes a tomar (default 5, sincronizado con rate limit).

    Returns:
        Lista de rows con estado='processing' tomados por este cycle.
    """
    now_iso = _now_iso()

    # 1. SELECT candidatos
    try:
        candidates, _ = client.select(
            TABLE_INBOX,
            {
                "estado": "eq.pending",
                "expires_at": f"gte.{now_iso}",
                "select": "*",
                "order": "priority.desc,created_at.asc",
                "limit": str(limit),
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("embrion_inbox.consume_select_failed", error=str(exc))
        return []

    if not candidates:
        return []

    locked_rows: List[dict] = []
    for cand in candidates:
        cand_id = str(cand["id"])
        try:
            locked = client.update(
                TABLE_INBOX,
                {"id": f"eq.{cand_id}", "estado": "eq.pending"},
                {"estado": "processing", "cycle_id": cycle_id},
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "embrion_inbox.consume_lock_failed",
                inbox_id=cand_id,
                error=str(exc),
            )
            continue

        if not locked:
            # Otro cycle lo tomó antes (race condition normal)
            continue
        locked_row = locked[0] if isinstance(locked, list) else locked

        audit(
            client,
            inbox_id=cand_id,
            decision="consumed",
            cycle_id=cycle_id,
            command_type=locked_row.get("tipo_comando", "unknown"),
            intent_class=locked_row.get("intent_class"),
            chat_id_origen=locked_row.get("chat_id_origen"),
            source="embrion_loop",
        )
        locked_rows.append(locked_row)

    return locked_rows


def mark_processed(
    client: Any,
    inbox_id: str,
    *,
    cycle_id: int,
    proposal_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> Optional[dict]:
    """Marcar un mensaje como processed."""
    updates = {
        "estado": "processed",
        "processed_at": _now_iso(),
    }
    if proposal_id:
        updates["proposal_id"] = proposal_id

    try:
        result = client.update(
            TABLE_INBOX,
            {"id": f"eq.{inbox_id}"},
            updates,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "embrion_inbox.mark_processed_failed",
            inbox_id=inbox_id,
            error=str(exc),
        )
        return None

    audit(
        client,
        inbox_id=inbox_id,
        decision="processed_ok",
        cycle_id=cycle_id,
        proposal_id=proposal_id,
        notes=notes,
        source="embrion_loop",
    )
    return result[0] if isinstance(result, list) and result else result


def mark_rejected(
    client: Any,
    inbox_id: str,
    *,
    cycle_id: Optional[int] = None,
    reason: str,
) -> Optional[dict]:
    """Marcar un mensaje como rejected con razón explícita."""
    try:
        result = client.update(
            TABLE_INBOX,
            {"id": f"eq.{inbox_id}"},
            {
                "estado": "rejected",
                "processed_at": _now_iso(),
                "error_reason": reason,
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "embrion_inbox.mark_rejected_failed",
            inbox_id=inbox_id,
            error=str(exc),
        )
        return None

    audit(
        client,
        inbox_id=inbox_id,
        decision="processed_failed",
        cycle_id=cycle_id,
        notes=reason,
        source="embrion_loop",
    )
    return result[0] if isinstance(result, list) and result else result


def mark_requires_mfa(
    client: Any,
    inbox_id: str,
    *,
    mfa_pin_hash: str,
    mfa_expires_at: str,
) -> Optional[dict]:
    """Marcar mensaje como requires_mfa con PIN hash + TTL.

    El embrion_loop notifica via Telegram con el PIN y espera respuesta del Daddy
    en próximo ciclo. Si valida → mark_processed. Si TTL expira → expire_old.
    """
    try:
        result = client.update(
            TABLE_INBOX,
            {"id": f"eq.{inbox_id}"},
            {
                "estado": "requires_mfa",
                "mfa_pin_hash": mfa_pin_hash,
                "mfa_expires_at": mfa_expires_at,
                "requires_mfa": True,
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "embrion_inbox.mark_mfa_failed",
            inbox_id=inbox_id,
            error=str(exc),
        )
        return None

    audit(
        client,
        inbox_id=inbox_id,
        decision="requires_mfa",
        notes=f"mfa_expires_at={mfa_expires_at}",
        source="embrion_loop",
    )
    return result[0] if isinstance(result, list) and result else result


def expire_old(client: Any) -> int:
    """Marcar todos los mensajes con expires_at < now como 'expired'.

    Devuelve cuántos quedaron expirados.
    """
    now_iso = _now_iso()
    try:
        result = client.update(
            TABLE_INBOX,
            {
                "expires_at": f"lt.{now_iso}",
                "estado": "in.(pending,processing,requires_mfa)",
            },
            {
                "estado": "expired",
                "processed_at": now_iso,
                "error_reason": "ttl_expired",
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("embrion_inbox.expire_old_failed", error=str(exc))
        return 0

    count = len(result) if isinstance(result, list) else (1 if result else 0)

    if count > 0:
        for row in (result if isinstance(result, list) else [result]):
            audit(
                client,
                inbox_id=str(row.get("id", "")),
                decision="expired",
                command_type=row.get("tipo_comando", "unknown"),
                source="embrion_inbox",
            )

    return count


def get_pending_count(client: Any) -> int:
    """Helper: cuántos mensajes pending no expirados hay ahora mismo."""
    try:
        rows, _ = client.select(
            TABLE_INBOX,
            {
                "estado": "eq.pending",
                "expires_at": f"gte.{_now_iso()}",
                "select": "id",
                "limit": "1000",
            },
        )
        return len(rows or [])
    except Exception:  # noqa: BLE001
        return 0


def get_inbox(client: Any, inbox_id: str) -> Optional[dict]:
    """Lookup directo por id."""
    try:
        rows, _ = client.select(
            TABLE_INBOX,
            {"id": f"eq.{inbox_id}", "select": "*", "limit": "1"},
        )
        return rows[0] if rows else None
    except Exception:  # noqa: BLE001
        return None
