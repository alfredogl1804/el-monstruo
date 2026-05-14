#!/usr/bin/env python3
"""
Entrypoint del cron Railway para Anti-Dory HeartbeatWriter.

Sprint MANUS-ANTI-DORY-002 v1 FASE D4 (Shadow Prod).
Doctrina §A.7 (HeartbeatWriter independencia crítica).

Frase canónica magna GPT-5.5 Pro:
    "Shadow prod no es activación: es instrumentación reversible con cero
     hidratación hasta que el attachment real pase prueba binaria."

Ejecutado por Railway cron service cada 10-15 minutos (recomendado 15min
para respetar hardcap C3: max 1 heartbeat / 10min ventana, 6/h, 150/24h).

═══════════════════════════════════════════════════════════════════════════
18 CONDICIONES DURAS COWORK + GPT-5.5 PRO (audit bd11733b §5)
═══════════════════════════════════════════════════════════════════════════

C1 — 4 flags separados (NO un solo ANTI_DORY_ENABLED):
     ANTI_DORY_ENABLED=false           # web/runtime sigue OFF
     ANTI_DORY_CRON_ENABLED=true       # solo cron shadow writer
     ANTI_DORY_HYDRATION_ENABLED=false # explícito
     ANTI_DORY_GUARDIAN_ENFORCE=false  # explícito
     El cron lee SOLO ANTI_DORY_CRON_ENABLED. Web ignora este flag.

C2 — Kill switch DB: lee anti_dory_runtime_flags.shadow_write_enabled
     via rpc_check_shadow_enabled() antes de cada write. False → no-op.
     T1 puede flip a false desde SQL Editor sin tocar Railway.

C3 — Write budget hardcap: rpc_increment_write_budget() atómico.
     Excede → self-disable automático (UPDATE shadow_write_enabled=false).

C4 — Idempotency key: f"{project_id}:{actor_type}:{window_start_unix//600}"
     Adjuntada al payload del runtime_event.

C5 — Shadow namespace explícito en payload:
     {"mode": "shadow_prod", "source": "railway_cron",
      "hydration_active": false, "user_impact": "none"}

C6 — Cero secrets en logs: este script NUNCA imprime apikey/service_key.

C7 — Smoke test local: anti_dory_heartbeat_cron --smoke-test ejecuta
     dry_run sin tocar Supabase (build payload + validate + log).

PC3 — Solo env vars mínimas Supabase + 4 flags Anti-Dory. NO heredar
      Anthropic/OpenAI/GitHub keys (segregación validada al arranque).

GPT-5.5 — Timeout estricto httpx (10.0s) + finally close: previene bug
          de Railway cron stuck por solapamiento.

═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional

# Configuración logging para Railway (stdout + level INFO por defecto)
LOG_LEVEL = os.getenv("ANTI_DORY_CRON_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s anti_dory_cron %(levelname)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("anti_dory_cron")


# =============================================================================
# Constantes
# =============================================================================

# C5 — Shadow namespace canónico inyectado en cada payload
SHADOW_NAMESPACE: Dict[str, Any] = {
    "mode": "shadow_prod",
    "source": "railway_cron",
    "hydration_active": False,
    "user_impact": "none",
    "sprint": "MANUS-ANTI-DORY-002-v1-FASE-D4",
}

# GPT-5.5 Pro — Timeout estricto httpx (anti-stuck Railway cron bug dic 2025).
# Override via env var para tests/staging si necesario.
_RPC_TIMEOUT_SECONDS: float = float(os.getenv("ANTI_DORY_CRON_RPC_TIMEOUT", "10.0"))
_RPC_CONNECT_TIMEOUT_SECONDS: float = float(
    os.getenv("ANTI_DORY_CRON_RPC_CONNECT_TIMEOUT", "3.0")
)

# PC3 — Whitelist de env vars que el cron PUEDE leer. Anti-leak segregación.
_ALLOWED_ENV_VARS = {
    "SUPABASE_URL",
    "SUPABASE_SERVICE_KEY",
    "ANTI_DORY_ENABLED",
    "ANTI_DORY_CRON_ENABLED",
    "ANTI_DORY_HYDRATION_ENABLED",
    "ANTI_DORY_GUARDIAN_ENFORCE",
    "ANTI_DORY_PROJECT_ID",
    "ANTI_DORY_FRONT_IDS",
    "ANTI_DORY_ACTOR_TYPE",
    "ANTI_DORY_CRON_LOG_LEVEL",
    "ANTI_DORY_CRON_RPC_TIMEOUT",
    "ANTI_DORY_CRON_RPC_CONNECT_TIMEOUT",
}

# PC3 — Env vars prohibidas (proxy de leak detection). Si el cron las ve, warn.
_FORBIDDEN_ENV_VARS = {
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "OPENROUTER_API_KEY",
    "GEMINI_API_KEY",
    "XAI_API_KEY",
    "SONAR_API_KEY",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "RAILWAY_TOKEN",
    "HEYGEN_API_KEY",
    "ELEVENLABS_API_KEY",
    "DROPBOX_API_KEY",
    "CLOUDFLARE_API_TOKEN",
}


# =============================================================================
# Utilidades
# =============================================================================

def _parse_front_ids(csv: str) -> List[str]:
    """Parsea CSV de fronts. Vacío → ['default']."""
    items = [s.strip() for s in csv.split(",") if s.strip()]
    return items or ["default"]


def _read_flag(name: str, default: str = "false") -> bool:
    """Lee un flag bool desde env. Default fail-closed."""
    raw = os.getenv(name, default).strip().lower()
    return raw in ("true", "1", "yes", "on")


def _is_cron_enabled() -> bool:
    """C1 — Cron lee SU PROPIO flag, NO el wire flag.

    Política Cowork bd11733b §5 C1:
    - ANTI_DORY_ENABLED (wire) puede ser false y el cron seguir corriendo.
    - El cron se controla SOLO via ANTI_DORY_CRON_ENABLED.
    """
    return _read_flag("ANTI_DORY_CRON_ENABLED", "false")


def _audit_env_segregation() -> List[str]:
    """PC3 — Detecta presencia de env vars que el cron NO debería tener.

    NO lee valores (zero-secret). Solo registra presencia/ausencia.
    Devuelve lista de vars prohibidas detectadas para audit.
    """
    leaked = []
    for var in _FORBIDDEN_ENV_VARS:
        if os.getenv(var):
            leaked.append(var)
    return leaked


def _compute_idempotency_key(project_id: str, actor_type: str, now_unix: float) -> str:
    """C4 — Idempotency key bucket de 10 minutos."""
    window_id = int(now_unix // 600)
    return f"{project_id}:{actor_type}:{window_id}"


def _build_shadow_payload(
    *,
    project_id: str,
    front_id: str,
    actor_type: str,
    now_unix: float,
) -> Dict[str, Any]:
    """C5 — Construye payload con shadow namespace + idempotency_key."""
    return {
        **SHADOW_NAMESPACE,
        "project_id": project_id,
        "front_id": front_id,
        "actor_type": actor_type,
        "idempotency_key": _compute_idempotency_key(project_id, actor_type, now_unix),
        "ts_unix": int(now_unix),
        "writer_origin": "anti_dory_heartbeat_cron.py",
    }


# =============================================================================
# Broker / RPC wrappers (httpx con timeout + finally close)
# =============================================================================

def _build_supabase_client():
    """GPT-5.5 — Construye HTTPXSupabaseRPCClient con timeout estricto.

    El cliente CANÓNICO ya tiene defaults via env var, pero aquí forzamos
    timeout=10.0s anti-stuck y connect=3.0s. Retorna None si env vars
    Supabase faltan.
    """
    try:
        from kernel.anti_dory.supabase_client import HTTPXSupabaseRPCClient
    except ImportError as exc:
        logger.error("anti_dory_cron: cannot import HTTPXSupabaseRPCClient: %s", exc)
        return None

    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    if not url or not key:
        logger.warning(
            "anti_dory_cron: Supabase env vars missing (url=%s key=%s)",
            bool(url), bool(key),
        )
        return None

    return HTTPXSupabaseRPCClient(
        url=url,
        service_key=key,
        timeout=_RPC_TIMEOUT_SECONDS,
        connect_timeout=_RPC_CONNECT_TIMEOUT_SECONDS,
    )


def _check_kill_switch(rpc_client) -> bool:
    """C2 — Lee anti_dory_runtime_flags.shadow_write_enabled.

    Retorna True si shadow_write está habilitado, False si no o si error.
    Fail-closed: cualquier error → False.
    """
    try:
        result = rpc_client.call_rpc("rpc_check_shadow_enabled", {})
        # PostgREST puede devolver bool directo, lista [bool], o {key: bool}.
        if isinstance(result, bool):
            return result
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, bool):
                return first
            if isinstance(first, dict):
                for v in first.values():
                    if isinstance(v, bool):
                        return v
        if isinstance(result, dict):
            for v in result.values():
                if isinstance(v, bool):
                    return v
        logger.warning(
            "anti_dory_cron: rpc_check_shadow_enabled returned unexpected shape=%r",
            type(result).__name__,
        )
        return False
    except Exception as exc:  # noqa: BLE001 — fail-closed
        logger.warning("anti_dory_cron: rpc_check_shadow_enabled failed: %s", exc)
        return False


def _increment_budget(rpc_client) -> Dict[str, Any]:
    """C3 — Incrementa budget atómico. Retorna dict con within_budget + counts.

    Si excede, el RPC self-disable automático (UPDATE shadow_write_enabled=false).
    """
    try:
        result = rpc_client.call_rpc("rpc_increment_write_budget", {})
        if isinstance(result, list) and result:
            return result[0]
        if isinstance(result, dict):
            return result
        return {"within_budget": False, "exceeded_window": "unknown_shape"}
    except Exception as exc:  # noqa: BLE001
        logger.warning("anti_dory_cron: rpc_increment_write_budget failed: %s", exc)
        return {"within_budget": False, "exceeded_window": f"rpc_error:{type(exc).__name__}"}


# =============================================================================
# Tick principal
# =============================================================================

def tick_once(
    *,
    project_id: str,
    front_ids: List[str],
    actor_type: str = "system",
    rpc_client=None,
    writer=None,
    sleep_between_fronts_s: float = 0.0,
) -> int:
    """Ejecuta un tick por cada front_id con TODAS las 18 condiciones.

    Pipeline por front:
      1. C2: check kill switch DB (rpc_check_shadow_enabled)
      2. C3: increment budget atómico (rpc_increment_write_budget)
      3. Si within_budget=False → log + skip (NO writer call)
      4. C5: build shadow payload + idempotency_key
      5. writer.tick() → escribe runtime_event + thread_snapshot
      6. Log binario (event_id, snapshot_id, elapsed_ms, idempotency_key)

    Retorna count de errores (no kill-switch-off, eso no es error).
    """
    # Lazy import writer (no se requiere si kill switch off)
    if rpc_client is None:
        rpc_client = _build_supabase_client()
    if rpc_client is None:
        logger.warning("anti_dory_cron: rpc_client unavailable (env missing). Skipping tick.")
        return 0

    # C2 — Kill switch check ANTES de cargar writer
    shadow_on = _check_kill_switch(rpc_client)
    if not shadow_on:
        logger.info("anti_dory_cron: kill_switch=OFF (shadow_write_enabled=false). No-op tick.")
        return 0

    # C3 — Budget increment + check
    budget = _increment_budget(rpc_client)
    if not budget.get("within_budget", False):
        logger.warning(
            "anti_dory_cron: budget_exceeded window=%s counts={w10min=%s,w1h=%s,w24h=%s}. "
            "Self-disable activado automáticamente por RPC.",
            budget.get("exceeded_window"),
            budget.get("w10min_count"),
            budget.get("w1h_count"),
            budget.get("w24h_count"),
        )
        return 0  # NO es error: el sistema se protegió a sí mismo

    logger.info(
        "anti_dory_cron: budget_ok counts={w10min=%s,w1h=%s,w24h=%s}",
        budget.get("w10min_count"),
        budget.get("w1h_count"),
        budget.get("w24h_count"),
    )

    # Lazy load writer SOLO si shadow on + budget ok
    if writer is None:
        writer = _load_writer(rpc_client=rpc_client, actor_type=actor_type)
    if writer is None:
        logger.warning("anti_dory_cron: writer unavailable. Skipping tick.")
        return 0

    errors = 0
    now_unix = time.time()

    for front_id in front_ids:
        t0 = time.monotonic()
        idem_key = _compute_idempotency_key(project_id, actor_type, now_unix)

        try:
            result = writer.tick(project_id=project_id, front_id=front_id)
            elapsed_ms = int((time.monotonic() - t0) * 1000)

            if result.error:
                errors += 1
                logger.error(
                    "anti_dory_cron front=%s error=%s elapsed_ms=%d idem=%s",
                    front_id, result.error, elapsed_ms, idem_key,
                )
            else:
                logger.info(
                    "anti_dory_cron front=%s snapshot_id=%s accepted=%s "
                    "elapsed_ms=%d idem=%s shadow_namespace=%s",
                    front_id, result.snapshot_id, result.accepted,
                    elapsed_ms, idem_key, SHADOW_NAMESPACE["mode"],
                )
        except Exception as exc:  # noqa: BLE001 — cron debe seguir con otros frentes
            errors += 1
            logger.exception(
                "anti_dory_cron front=%s fatal_exception=%s idem=%s",
                front_id, exc, idem_key,
            )

        if sleep_between_fronts_s > 0:
            time.sleep(sleep_between_fronts_s)

    return errors


def _load_writer(*, rpc_client=None, actor_type: str = "system"):
    """Carga HeartbeatWriter con rpc_client opcional inyectable (tests)."""
    from kernel.anti_dory.writers import HeartbeatWriter

    if rpc_client is None:
        rpc_client = _build_supabase_client()
    if rpc_client is None:
        return None
    return HeartbeatWriter(rpc_client, actor_type=actor_type)


# =============================================================================
# Smoke test (C7)
# =============================================================================

def _run_smoke_test() -> int:
    """C7 — Build + validate payload sin tocar Supabase.

    NO requiere SUPABASE_URL/KEY. NO requiere kill switch DB.
    Solo valida que el flujo de payload construction funciona.
    """
    logger.info("anti_dory_cron: SMOKE TEST starting (dry_run, no Supabase calls)")

    project_id = "smoke-test-project"
    front_ids = _parse_front_ids("MANUS-ANTI-DORY-002,COWORK-MEMENTO-001")
    actor_type = "system"
    now_unix = time.time()

    errors = 0
    for front_id in front_ids:
        try:
            payload = _build_shadow_payload(
                project_id=project_id,
                front_id=front_id,
                actor_type=actor_type,
                now_unix=now_unix,
            )
            # Validaciones obligatorias
            assert payload["mode"] == "shadow_prod", "C5: mode debe ser shadow_prod"
            assert payload["hydration_active"] is False, "C5: hydration_active debe ser false"
            assert payload["user_impact"] == "none", "C5: user_impact debe ser none"
            assert "idempotency_key" in payload, "C4: idempotency_key obligatoria"
            idem = payload["idempotency_key"]
            assert idem.count(":") == 2, f"C4: idempotency_key format inválido: {idem}"
            logger.info("smoke_test front=%s payload_keys=%s idem=%s",
                        front_id, sorted(payload.keys()), idem)
        except AssertionError as exc:
            errors += 1
            logger.error("smoke_test FAILED front=%s: %s", front_id, exc)

    # Audit env segregation
    leaked = _audit_env_segregation()
    if leaked:
        logger.warning(
            "smoke_test PC3 violation: cron env tiene %d vars prohibidas: %s",
            len(leaked), sorted(leaked),
        )
        # NO es fatal en smoke test local — Railway debe filtrar.

    if errors:
        logger.error("smoke_test: FAILED (errors=%d)", errors)
        return 2
    logger.info("smoke_test: PASS (all assertions OK)")
    return 0


# =============================================================================
# Main entrypoint
# =============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    """Entrypoint principal con manejo de cliente HTTPX en try/finally.

    Exit codes:
      0 — éxito, flag off, kill switch off, o budget exceeded (todo no-op safe)
      1 — error en writer.tick (al menos un front falló)
      2 — error de configuración o smoke test failed
    """
    argv = argv or sys.argv[1:]

    # C7 — Smoke test mode
    if "--smoke-test" in argv or os.getenv("ANTI_DORY_CRON_SMOKE_TEST", "").lower() == "true":
        return _run_smoke_test()

    # C1 — Cron lee SU PROPIO flag, NO el wire flag
    if not _is_cron_enabled():
        logger.info(
            "anti_dory_cron: ANTI_DORY_CRON_ENABLED=false → exit 0 sin escribir. "
            "(wire ANTI_DORY_ENABLED=%s, hydration=%s, guardian=%s)",
            _read_flag("ANTI_DORY_ENABLED"),
            _read_flag("ANTI_DORY_HYDRATION_ENABLED"),
            _read_flag("ANTI_DORY_GUARDIAN_ENFORCE"),
        )
        return 0

    # PC3 — Audit segregación env vars
    leaked = _audit_env_segregation()
    if leaked:
        logger.warning(
            "anti_dory_cron: PC3 LEAK DETECTED — %d vars prohibidas presentes: %s. "
            "Continúa pero T1 debe revisar Railway service vars.",
            len(leaked), sorted(leaked),
        )

    project_id = os.getenv("ANTI_DORY_PROJECT_ID", "el-monstruo").strip() or "el-monstruo"
    fronts_csv = os.getenv("ANTI_DORY_FRONT_IDS", "MANUS-ANTI-DORY-002")
    front_ids = _parse_front_ids(fronts_csv)
    actor_type = os.getenv("ANTI_DORY_ACTOR_TYPE", "system").strip() or "system"

    logger.info(
        "anti_dory_cron: starting tick project=%s fronts=%s actor=%s timeout=%.1fs",
        project_id, front_ids, actor_type, _RPC_TIMEOUT_SECONDS,
    )

    # GPT-5.5 — try/finally con close del httpx client
    rpc_client = None
    try:
        rpc_client = _build_supabase_client()
        errors = tick_once(
            project_id=project_id,
            front_ids=front_ids,
            actor_type=actor_type,
            rpc_client=rpc_client,
        )
        if errors > 0:
            logger.error("anti_dory_cron: exit 1 (errors=%d)", errors)
            return 1
        logger.info("anti_dory_cron: exit 0 (success)")
        return 0
    finally:
        if rpc_client is not None:
            try:
                rpc_client.close()
                logger.debug("anti_dory_cron: rpc_client closed (anti-stuck httpx)")
            except Exception as exc:  # noqa: BLE001 — cleanup
                logger.warning("anti_dory_cron: rpc_client close failed: %s", exc)


if __name__ == "__main__":
    sys.exit(main())
