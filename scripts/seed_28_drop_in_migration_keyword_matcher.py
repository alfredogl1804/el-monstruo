#!/usr/bin/env python3
"""
El Monstruo — Sprint 85 cierre — Sembrar 28va semilla via endpoint admin
==========================================================================
Llama POST /v1/error-memory/seed del kernel productivo para persistir la
semilla 28 (drop-in migration de los 3 archivos del Sprint 85 a la utility
centralizada kernel/utils/keyword_matcher.py creada por Sprint 84.7).

Idempotente: si la semilla ya existe (mismo error_signature), hace UPSERT.

Uso:
    export MONSTRUO_API_KEY="..."
    python3 scripts/seed_28_drop_in_migration_keyword_matcher.py

Variables de entorno:
    KERNEL_URL          (default: https://el-monstruo-kernel-production.up.railway.app)
    MONSTRUO_API_KEY    (requerida — auth admin del endpoint)

Sprint 85 cierre + 84.7 migration — Hilo Manus Catastro — 2026-05-04.
Patrón seguido del Ejecutor: scripts/seed_sprint_84_5_via_endpoint.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error

# Sprint Memento Bloque 5 Fase 1 — pre-flight via library Memento
_MEMENTO_AVAILABLE = True
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.memento_preflight import (  # type: ignore
        preflight_check,
        MementoPreflightError,
    )
except Exception as _import_exc:
    _MEMENTO_AVAILABLE = False
    print(f"[seed-28] WARN: tools.memento_preflight no disponible ({_import_exc!r}); continuando sin preflight", file=sys.stderr)


KERNEL_URL = os.environ.get(
    "KERNEL_URL",
    "https://el-monstruo-kernel-production.up.railway.app",
).rstrip("/")
ADMIN_KEY = os.environ.get("MONSTRUO_API_KEY", "").strip()
ENDPOINT = f"{KERNEL_URL}/v1/error-memory/seed"
TIMEOUT_S = 20


SEED_28 = {
    "error_signature": "seed_drop_in_migration_keyword_matcher_sprint85_close",
    "sanitized_message": (
        "[Hilo Manus Catastro] Cierre Sprint 85: drop-in migration de los 3 "
        "archivos refactorizados en el HOTFIX (semilla 19) a la utility "
        "centralizada kernel/utils/keyword_matcher.py creada por el Hilo "
        "Ejecutor en Sprint 84.7 (commit 34b0c90). Archivos migrados: "
        "kernel/embriones/product_architect.py (migrado por Cowork en 84.7), "
        "kernel/task_planner.py (migrado por Cowork en 84.7), "
        "kernel/embriones/critic_visual.py (migrado por Catastro en cierre 85). "
        "Ahora los 3 usan compile_keyword_pattern() + count_keyword_matches() / "
        "match_any_keyword() del utility, eliminando regex inline duplicada. "
        "Beneficios: consistencia global del kernel, mantenimiento centralizado, "
        "soporte uniforme de multi-word keywords y treat_underscore_as_separator."
    ),
    "resolution": (
        "Patron consolidado: from kernel.utils.keyword_matcher import "
        "compile_keyword_pattern, count_keyword_matches, match_any_keyword. "
        "Cache de patterns a nivel modulo (lazy fill). 46/46 tests del Sprint "
        "85 PASS post-migration (test_sprint85_unit + test_sprint85_hotfix_"
        "substring). Cero regresion funcional. Code review rule: cualquier PR "
        "futura con 'kw in text' raw es BLOQUEANTE - usar la utility."
    ),
    "confidence": 0.95,
    "module": "kernel.embriones.product_architect+kernel.task_planner+kernel.embriones.critic_visual+kernel.utils.keyword_matcher",
    "action": "drop_in_migration_to_centralized_utility",
    "status": "resolved",
}


def _post_seed(seed: dict) -> tuple[int, dict | str]:
    """POST de un payload seed al endpoint admin."""
    payload = {
        "error_signature": seed["error_signature"],
        "sanitized_message": seed["sanitized_message"],
        "resolution": seed["resolution"],
        "confidence": float(seed["confidence"]),
        "module": seed.get("module", "manual.seed"),
        "action": seed.get("action", ""),
        "status": seed.get("status", "resolved"),
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": ADMIN_KEY,
            "User-Agent": "monstruo-seed-script/sprint85-close-28",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            return e.code, json.loads(err_body) if err_body else str(e)
        except Exception:
            return e.code, str(e)
    except urllib.error.URLError as e:
        return -1, f"URLError: {e.reason}"
    except Exception as e:
        return -1, f"Exception: {type(e).__name__}: {e}"


def _run_preflight() -> int | None:
    """Pre-flight check via library Memento. Retorna exit code si bloquea, None si OK."""
    if not _MEMENTO_AVAILABLE:
        return None
    try:
        preflight = preflight_check(
            operation="kernel_admin_call",
            context_used={
                "endpoint": ENDPOINT,
                "kernel_url": KERNEL_URL,
                "signature": SEED_28["error_signature"],
            },
            hilo_id="manus_ejecutor_seed_28",
            intent_summary="persistir semilla 28 drop-in migration keyword_matcher cierre Sprint 85",
        )
        if not preflight.proceed:
            print(
                f"[seed-28] ABORT preflight bloqueó ejecución: "
                f"status={preflight.validation_status} "
                f"remediation={preflight.remediation}",
                file=sys.stderr,
            )
            return 3
        print(f"[seed-28] preflight OK validation_id={preflight.validation_id}")
        return None
    except MementoPreflightError as exc:
        print(f"[seed-28] WARN preflight falló: {exc!s}; continuando con fallback degradado", file=sys.stderr)
        return None
    except Exception as exc:
        print(f"[seed-28] WARN preflight inesperado: {exc!r}; continuando", file=sys.stderr)
        return None


def main() -> int:
    if not ADMIN_KEY:
        print("ERROR: MONSTRUO_API_KEY no configurada (env var requerida)", file=sys.stderr)
        return 2

    preflight_exit = _run_preflight()
    if preflight_exit is not None:
        return preflight_exit

    print(f"[seed-28] POST {ENDPOINT}")
    print(f"[seed-28] signature={SEED_28['error_signature']}")
    print(f"[seed-28] confidence={SEED_28['confidence']}")
    print()

    status, body = _post_seed(SEED_28)
    print(f"HTTP {status}")
    if isinstance(body, dict):
        print(json.dumps(body, indent=2, ensure_ascii=False))
    else:
        print(body)

    if 200 <= status < 300:
        print("\n[OK] Semilla 28 persistida")
        return 0
    print(f"\n[FAIL] Status {status}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
