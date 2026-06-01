"""
Rotor Wiring — módulo central de inyección fail-soft para los 6 capturers.
Sprint: ROTOR-001 (T2 — wiring final)
Owner: Manus Auditor 2026-06-01

Diseño:
  - Cada función es fire-and-forget, fail-soft (nunca rompe el caller).
  - Lazy imports para no romper si psycopg o dependencias no están.
  - Logging estructurado para observabilidad.
  - Thread-safe: cada llamada crea su propio capturer (stateless).

Uso desde puntos de inyección:
    from kernel.rotor.rotor_wiring import rotor_capture_latido
    rotor_capture_latido(cycle_id=123, status="success", duration_ms=850)
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _persist_fn_lazy():
    """Lazy import de persist_activity para evitar circular imports."""
    from kernel.rotor.persistence import persist_activity
    return persist_activity


# ─────────────────────────────────────────────────────────────────────
# 1. LATIDO CAPTURER — embrion_loop.py
# ─────────────────────────────────────────────────────────────────────
def rotor_capture_latido(
    *,
    cycle_id: int,
    status: str = "success",
    duration_ms: int = 0,
    aborted_reason: Optional[str] = None,
) -> None:
    """Fire-and-forget: captura un latido del Embrión."""
    try:
        from kernel.rotor.capturers.latido_capturer import LatidoCapturer
        capturer = LatidoCapturer(persist_fn=_persist_fn_lazy())
        capturer.capture_and_persist({
            "cycle_id": cycle_id,
            "status": status,
            "duration_ms": duration_ms,
            "aborted_reason": aborted_reason,
        })
    except Exception as exc:
        logger.warning("rotor_wiring_latido_fail", error=str(exc), cycle_id=cycle_id)


# ─────────────────────────────────────────────────────────────────────
# 2. TELEGRAM CAPTURER — embrion_routes.py telegram_webhook
# ─────────────────────────────────────────────────────────────────────
def rotor_capture_telegram(
    *,
    chat_id: str,
    message_id: int = 0,
    text: str = "",
    from_username: str = "",
) -> None:
    """Fire-and-forget: captura un mensaje de Telegram."""
    try:
        from kernel.rotor.capturers.telegram_capturer import TelegramCapturer
        capturer = TelegramCapturer(persist_fn=_persist_fn_lazy())
        capturer.capture_and_persist({
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "from_username": from_username,
        })
    except Exception as exc:
        logger.warning("rotor_wiring_telegram_fail", error=str(exc), chat_id=chat_id)


# ─────────────────────────────────────────────────────────────────────
# 3. MANUS CAPTURER — nodes.py respond() o polling embrion_memoria
# ─────────────────────────────────────────────────────────────────────
def rotor_capture_manus(
    *,
    memoria_id: str = "",
    tipo: str = "",
    contenido: str = "",
    hilo_origen: str = "",
    importancia: int = 0,
    created_at: str = "",
) -> None:
    """Fire-and-forget: captura actividad de un hilo Manus."""
    try:
        from kernel.rotor.capturers.manus_capturer import ManusCapturer
        capturer = ManusCapturer(persist_fn=_persist_fn_lazy())
        capturer.capture_and_persist({
            "id": memoria_id,
            "tipo": tipo,
            "contenido": contenido,
            "hilo_origen": hilo_origen,
            "importancia": importancia,
            "created_at": created_at,
        })
    except Exception as exc:
        logger.warning("rotor_wiring_manus_fail", error=str(exc), hilo_origen=hilo_origen)


# ─────────────────────────────────────────────────────────────────────
# 4. COWORK CAPTURER — nodes.py o cowork_sesiones trigger
# ─────────────────────────────────────────────────────────────────────
def rotor_capture_cowork(
    *,
    session_id: str = "",
    started_at: str = "",
    ended_at: str = "",
    duration_seconds: int = 0,
    actor: str = "cowork",
    decisiones_count: int = 0,
) -> None:
    """Fire-and-forget: captura una sesión cerrada de Cowork."""
    try:
        from kernel.rotor.capturers.cowork_capturer import CoworkCapturer
        capturer = CoworkCapturer(persist_fn=_persist_fn_lazy())
        capturer.capture_and_persist({
            "session_id": session_id,
            "started_at": started_at,
            "ended_at": ended_at,
            "duration_seconds": duration_seconds,
            "actor": actor,
            "decisiones_count": decisiones_count,
        })
    except Exception as exc:
        logger.warning("rotor_wiring_cowork_fail", error=str(exc), session_id=session_id)


# ─────────────────────────────────────────────────────────────────────
# 5. GITHUB CAPTURER — webhook POST /webhooks/github_push
# ─────────────────────────────────────────────────────────────────────
def rotor_capture_github(
    *,
    repo: str = "",
    ref: str = "",
    sha: str = "",
    actor: str = "",
    merged_to_main: bool = False,
    files_changed: int = 0,
) -> None:
    """Fire-and-forget: captura un push/commit de GitHub."""
    try:
        from kernel.rotor.capturers.github_capturer import GitHubCapturer
        capturer = GitHubCapturer(persist_fn=_persist_fn_lazy())
        capturer.capture_and_persist({
            "repo": repo,
            "ref": ref,
            "sha": sha,
            "actor": actor,
            "merged_to_main": merged_to_main,
            "files_changed": files_changed,
        })
    except Exception as exc:
        logger.warning("rotor_wiring_github_fail", error=str(exc), sha=sha[:8])


# ─────────────────────────────────────────────────────────────────────
# 6. SUPABASE CAPTURER — polling de kernel_audit_log
# ─────────────────────────────────────────────────────────────────────
def rotor_capture_supabase(
    *,
    actor: str = "cowork_mcp",
    table_name: str = "",
    query_type: str = "UNKNOWN",
    query_text: str = "",
    rows_affected: int = 0,
    duration_ms: int = 0,
) -> None:
    """Fire-and-forget: captura una query de kernel_audit_log."""
    try:
        from kernel.rotor.capturers.supabase_capturer import SupabaseCapturer
        capturer = SupabaseCapturer(persist_fn=_persist_fn_lazy())
        capturer.capture_and_persist({
            "actor": actor,
            "table_name": table_name,
            "query_type": query_type,
            "query_text": query_text,
            "rows_affected": rows_affected,
            "duration_ms": duration_ms,
        })
    except Exception as exc:
        logger.warning("rotor_wiring_supabase_fail", error=str(exc), table=table_name)


__all__ = [
    "rotor_capture_latido",
    "rotor_capture_telegram",
    "rotor_capture_manus",
    "rotor_capture_cowork",
    "rotor_capture_github",
    "rotor_capture_supabase",
]
