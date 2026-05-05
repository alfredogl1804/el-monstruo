#!/usr/bin/env python3
"""
El Monstruo — Sprint 85 HOTFIX — Sembrar 19va semilla via endpoint admin
==========================================================================
Llama POST /v1/error-memory/seed del kernel productivo para persistir la
semilla 19 (HOTFIX substring matching del Sprint 85 — Hilo Catastro).

Idempotente: si la semilla ya existe (mismo error_signature), hace UPSERT.

Uso:
    export MONSTRUO_API_KEY="..."
    python3 scripts/seed_19_substring_matching_hotfix_sprint85.py

Variables de entorno:
    KERNEL_URL          (default: https://el-monstruo-kernel-production.up.railway.app)
    MONSTRUO_API_KEY    (requerida — auth admin del endpoint)

Sprint 85 HOTFIX — Hilo Manus Catastro — 2026-05-04.
Patrón seguido del Ejecutor: scripts/seed_sprint_84_5_via_endpoint.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error

# Sprint Memento Bloque 5 Fase 1 — pre-flight via library Memento
# Eat your own dogfood: este script ahora se valida a sí mismo antes de
# llamar al endpoint admin del kernel. Si la library no está disponible,
# fallback degradado: continúa pero loggea el incidente.
_MEMENTO_AVAILABLE = True
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.memento_preflight import (  # type: ignore
        preflight_check,
        MementoPreflightError,
    )
except Exception as _import_exc:
    _MEMENTO_AVAILABLE = False
    print(f"[seed-19] WARN: tools.memento_preflight no disponible ({_import_exc!r}); continuando sin preflight", file=sys.stderr)


KERNEL_URL = os.environ.get(
    "KERNEL_URL",
    "https://el-monstruo-kernel-production.up.railway.app",
).rstrip("/")
ADMIN_KEY = os.environ.get("MONSTRUO_API_KEY", "").strip()
ENDPOINT = f"{KERNEL_URL}/v1/error-memory/seed"
TIMEOUT_S = 20


SEED_19 = {
    "error_signature": "seed_substring_matching_hotfix_sprint85_resolved",
    "sanitized_message": (
        "[Hilo Manus Catastro] HOTFIX preventivo Sprint 85: refactor del patron "
        "'any(kw in text for kw in keywords)' en 3 archivos del Sprint 85 "
        "(product_architect.py:_detectar_vertical, task_planner.py:_es_proyecto_web, "
        "critic_visual.py:_evaluar_estructura). Causa: substring matching sin word "
        "boundaries provoca falsos positivos como 'artesanal' matcheando 'arte', "
        "'saasoso' matcheando 'saas', 'learnability' matcheando 'learn'. Aplicado "
        "patron aprobado del Sprint 84.5: regex con \\b...\\b, compilado a nivel "
        "modulo y cacheado, soporta multi-word keywords. Cuando Sprint 84.7 cierre "
        "kernel/utils/keyword_matcher.py, migrar drop-in a la utility centralizada."
    ),
    "resolution": (
        "Cada archivo refactorizado usa re.compile(r'\\b(?:kw1|kw2|...)\\b', "
        "re.IGNORECASE) con keywords ordenadas por longitud descendente para greedy "
        "alternation. Pattern cacheado en _PATTERN_CACHE (product_architect) o "
        "_WEB_PROJECT_PATTERN (task_planner) o pattern local (critic_visual). 24 "
        "tests de regresion PASS (tests/test_sprint85_hotfix_substring.py). "
        "Migration drop-in al utility centralizado pendiente despues del cierre "
        "del Sprint 84.7."
    ),
    "confidence": 0.90,
    "module": "kernel.embriones.product_architect+kernel.task_planner+kernel.embriones.critic_visual",
    "action": "hotfix_word_boundaries",
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
            "User-Agent": "monstruo-seed-script/sprint85-hotfix",
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


def main() -> int:
    if not ADMIN_KEY:
        print("ERROR: MONSTRUO_API_KEY no configurada (env var requerida)", file=sys.stderr)
        return 2

    # Sprint Memento B5 F1 — pre-flight check via library Memento
    if _MEMENTO_AVAILABLE:
        try:
            preflight = preflight_check(
                operation="kernel_admin_call",
                context_used={
                    "endpoint": ENDPOINT,
                    "kernel_url": KERNEL_URL,
                    "signature": SEED_19["error_signature"],
                },
                hilo_id="manus_ejecutor_seed_19",
                intent_summary="persistir semilla 19 substring matching hotfix Sprint 85",
            )
            if not preflight.proceed:
                print(
                    f"[seed-19] ABORT preflight bloqueó ejecución: "
                    f"status={preflight.validation_status} "
                    f"remediation={preflight.remediation}",
                    file=sys.stderr,
                )
                return 3
            print(f"[seed-19] preflight OK validation_id={preflight.validation_id}")
        except MementoPreflightError as exc:
            print(f"[seed-19] WARN preflight falló: {exc!s}; continuando con fallback degradado", file=sys.stderr)
        except Exception as exc:
            print(f"[seed-19] WARN preflight inesperado: {exc!r}; continuando", file=sys.stderr)

    print(f"[seed-19] POST {ENDPOINT}")
    print(f"[seed-19] signature={SEED_19['error_signature']}")
    print(f"[seed-19] confidence={SEED_19['confidence']}")
    print()

    status, body = _post_seed(SEED_19)
    print(f"HTTP {status}")
    if isinstance(body, dict):
        print(json.dumps(body, indent=2, ensure_ascii=False))
    else:
        print(body)

    if 200 <= status < 300:
        print("\n[OK] Semilla 19 persistida")
        return 0
    print(f"\n[FAIL] Status {status}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
