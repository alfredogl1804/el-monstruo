#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
# 30va SEMILLA — Credenciales heredadas de contexto compactado de Manus
# ═══════════════════════════════════════════════════════════════════════════
#
# Origen: Incidente "Falso Positivo TiDB" del 2026-05-04. El Hilo Manus
# ticketlike reportó rotación de password productivo cuando en realidad
# usó credenciales de un cluster fantasma (gateway01, user
# 2JZ7xEfSRs2GZWW.root, db ticketlike) que arrastraba en su contexto
# compactado de sesión anterior, sin haber leído el credentials.md del
# skill como pre-flight.
#
# Esta semilla es la primera evidencia del Objetivo #15 (Memoria Soberana)
# en error_memory — concretiza el axioma fundacional como pattern verificable.
#
# Uso:
#   export MONSTRUO_API_KEY="..."
#   python3 scripts/seed_30_credenciales_heredadas_de_contexto_compactado.py
#
# Idempotente: UPSERT por error_signature, seguro para correr múltiples veces.
# ═══════════════════════════════════════════════════════════════════════════

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
    print(f"[seed-30] WARN: tools.memento_preflight no disponible ({_import_exc!r}); continuando sin preflight", file=sys.stderr)

KERNEL_URL = os.environ.get(
    "KERNEL_URL",
    "https://el-monstruo-kernel-production.up.railway.app",
)
API_KEY = os.environ.get("MONSTRUO_API_KEY")

if not API_KEY:
    print("ERROR: MONSTRUO_API_KEY no está en environment.", file=sys.stderr)
    print("Setear con: export MONSTRUO_API_KEY=\"...\"", file=sys.stderr)
    sys.exit(1)

SEMILLA_30 = {
    "error_signature": "seed_30_credenciales_heredadas_de_contexto_compactado_manus",
    "sanitized_message": (
        "Hilo Manus ejecuta operación crítica usando credenciales que arrastra "
        "de su propio contexto compactado de sesión anterior. Las credenciales "
        "en el contexto compactado pueden ser obsoletas, inválidas, o "
        "pertenecer a recursos diferentes (ej. cluster fantasma). El hilo no "
        "detecta la contaminación porque el contexto compactado se presenta "
        "como contexto activo. Caso real verificado: incidente 'Falso Positivo "
        "TiDB' del 2026-05-04 donde Hilo Manus ticketlike usó credenciales del "
        "cluster fantasma gateway01 (user 2JZ7xEfSRs2GZWW.root, db ticketlike) "
        "en lugar del cluster productivo real gateway05."
    ),
    "resolution": (
        "Antes de cualquier operación crítica (SQL prod, rotación cred, deploy "
        "prod, financial txn), leer programáticamente la fuente de verdad "
        "documentada (skills/X/references/credentials.md o equivalente) y "
        "comparar contra los parámetros que se van a usar. Si discrepan, "
        "abortar y reportar. Nunca confiar en credenciales que vengan solo del "
        "contexto interno del hilo Manus. Cuando la Capa 8 (Memento) del "
        "Objetivo #9 esté implementada (Sprint Memento), esta validación se "
        "automatiza vía POST /v1/memento/validate antes de la operación crítica."
    ),
    "confidence": 0.97,
    "module": "kernel.memento.preflight",
    "tags": [
        "memoria_soberana",
        "objetivo_15",
        "capa_memento",
        "sindrome_dory",
        "manus_amnesia_anterograda",
        "preflight_credenciales",
    ],
}


def upsert_semilla(semilla: dict) -> dict:
    url = f"{KERNEL_URL}/v1/error-memory/seed"
    body = json.dumps(semilla).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read().decode("utf-8")
            return {"status": resp.status, "body": json.loads(payload) if payload else None}
    except urllib.error.HTTPError as exc:
        try:
            payload = exc.read().decode("utf-8")
            body = json.loads(payload) if payload else None
        except Exception:
            body = None
        return {"status": exc.code, "body": body, "error": str(exc)}
    except urllib.error.URLError as exc:
        return {"status": 0, "body": None, "error": f"URLError: {exc}"}


def _run_preflight() -> int | None:
    """Pre-flight check via library Memento. Retorna exit code si bloquea, None si OK."""
    if not _MEMENTO_AVAILABLE:
        return None
    try:
        endpoint = f"{KERNEL_URL}/v1/error-memory/seed"
        preflight = preflight_check(
            operation="kernel_admin_call",
            context_used={
                "endpoint": endpoint,
                "kernel_url": KERNEL_URL,
                "signature": SEMILLA_30["error_signature"],
            },
            hilo_id="manus_ejecutor_seed_30",
            intent_summary="persistir 30va semilla credenciales_heredadas_de_contexto_compactado",
        )
        if not preflight.proceed:
            print(
                f"[seed-30] ABORT preflight bloqueó ejecución: "
                f"status={preflight.validation_status} "
                f"remediation={preflight.remediation}",
                file=sys.stderr,
            )
            return 3
        print(f"[seed-30] preflight OK validation_id={preflight.validation_id}")
        return None
    except MementoPreflightError as exc:
        print(f"[seed-30] WARN preflight falló: {exc!s}; continuando con fallback degradado", file=sys.stderr)
        return None
    except Exception as exc:
        print(f"[seed-30] WARN preflight inesperado: {exc!r}; continuando", file=sys.stderr)
        return None


def main() -> int:
    preflight_exit = _run_preflight()
    if preflight_exit is not None:
        return preflight_exit

    print(f"30va Semilla — UPSERT contra {KERNEL_URL}")
    print(f"  signature: {SEMILLA_30['error_signature']}")
    print(f"  module: {SEMILLA_30['module']}")
    print(f"  confidence: {SEMILLA_30['confidence']}")
    print()
    result = upsert_semilla(SEMILLA_30)
    print(f"HTTP {result['status']}")
    if result.get("body"):
        print(json.dumps(result["body"], indent=2, ensure_ascii=False))
    if result.get("error"):
        print(f"ERROR: {result['error']}", file=sys.stderr)
    if result["status"] in (200, 201):
        print("✓ 30va semilla persistida (UPSERT idempotente)")
        return 0
    print("✗ Falló persistencia", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
