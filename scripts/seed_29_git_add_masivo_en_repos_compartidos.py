#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
# 29va SEMILLA — git add masivo en repos compartidos por múltiples hilos
# ═══════════════════════════════════════════════════════════════════════════
#
# Origen: Sprint 84.6 (Browser Automation Soberano). Durante el sprint el
# Hilo Manus Ejecutor estaba escribiendo 7 archivos del módulo browser
# soberano cuando el Hilo Cowork ejecutó `git add -A && git commit && git
# push` automático, absorbiendo el WIP del Ejecutor en el commit `f1f5c1a`
# de Cowork (mezcla de cambios de bridge + WIP de browser sin terminar).
# Posteriormente el Hilo Catastro detectó el problema y aplicó revert
# quirúrgico (commit `7aee84d`) para limpiar el working tree, permitiendo
# al Ejecutor volver a hacer su commit formal `8df678d` con autoría
# preservada. La semilla quedó documentada en el commit log del revert
# pero NO en error_memory hasta esta semilla.
#
# Esta semilla complementa al protocolo nuevo aplicado por el Catastro
# desde su commit del Sprint 86 Bloque 1 (`bcf2a91`):
#   - PROTOCOLO 1: git status -s (verificar working tree pre-add)
#   - PROTOCOLO 2: git add <paths específicos> (NUNCA `git add -A` ni `git add .`)
#   - PROTOCOLO 3: git diff --cached --name-only (verificar staged)
#   - PROTOCOLO 4: git commit + git push (verificar hash en push output)
#
# Es referenciada como "28va semilla" en el log del commit 7aee84d porque
# en ese momento la numeración aún no había absorbido la 28va semilla
# real (drop-in migration utility — script seed_28). Para evitar
# confusión, esta queda registrada como **29va semilla** correlativa.
#
# Uso:
#   export MONSTRUO_API_KEY="..."
#   python3 scripts/seed_29_git_add_masivo_en_repos_compartidos.py
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
    print(f"[seed-29] WARN: tools.memento_preflight no disponible ({_import_exc!r}); continuando sin preflight", file=sys.stderr)

KERNEL_URL = os.environ.get(
    "KERNEL_URL",
    "https://el-monstruo-kernel-production.up.railway.app",
)
API_KEY = os.environ.get("MONSTRUO_API_KEY")

if not API_KEY:
    print("ERROR: MONSTRUO_API_KEY no está en environment.", file=sys.stderr)
    print("Setear con: export MONSTRUO_API_KEY=\"...\"", file=sys.stderr)
    sys.exit(1)

SEMILLA_29 = {
    "error_signature": "seed_29_git_add_masivo_en_repos_compartidos_por_multiples_hilos",
    "sanitized_message": (
        "En un repo donde múltiples hilos ejecutivos (Manus Ejecutor, Manus "
        "Catastro, Cowork, Manus ticketlike) operan concurrentemente sobre el "
        "mismo working tree de la Mac de Alfredo, ejecutar `git add -A`, "
        "`git add .`, o `git add <directorio>` absorbe accidentalmente WIP de "
        "OTROS hilos en el commit propio. El log de autoría se contamina y "
        "los cambios pueden quedar en commits con mensaje incorrecto. Caso "
        "verificado: Sprint 84.6 commit `f1f5c1a` de Cowork absorbió el WIP "
        "del módulo browser soberano del Hilo Manus Ejecutor."
    ),
    "resolution": (
        "Aplicar disciplina estricta de 4 pasos antes de cada commit en repos "
        "compartidos: (1) `git status -s` para inventariar el working tree "
        "completo y detectar archivos de OTROS hilos; (2) `git add "
        "<paths_especificos>` con archivos enumerados explícitamente — NUNCA "
        "`git add -A`, `git add .`, ni `git add <directorio>` salvo cuando el "
        "directorio es exclusivamente de tu zona primaria; (3) `git diff "
        "--cached --name-only` para verificar que SOLO los archivos esperados "
        "están staged; (4) `git commit` con autoría explícita "
        "(`-c user.name=\"Hilo X\"`) + `git push` y verificar el hash en el "
        "output. Si en el paso 1 detectás archivos de otros hilos, NO HACER "
        "git stash/checkout — comunicar al hilo dueño vía bridge antes de "
        "cualquier acción que toque su WIP."
    ),
    "confidence": 0.98,
    "module": "kernel.bridge.protocolo_commits_concurrentes",
    "tags": [
        "git_disciplina",
        "repos_compartidos",
        "multiples_hilos_manus",
        "memoria_soberana",
        "objetivo_15",
        "capa_memento",
        "anti_contaminacion_working_tree",
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
                "signature": SEMILLA_29["error_signature"],
            },
            hilo_id="manus_ejecutor_seed_29",
            intent_summary="persistir 29va semilla git_add_masivo_en_repos_compartidos",
        )
        if not preflight.proceed:
            print(
                f"[seed-29] ABORT preflight bloqueó ejecución: "
                f"status={preflight.validation_status} "
                f"remediation={preflight.remediation}",
                file=sys.stderr,
            )
            return 3
        print(f"[seed-29] preflight OK validation_id={preflight.validation_id}")
        return None
    except MementoPreflightError as exc:
        print(f"[seed-29] WARN preflight falló: {exc!s}; continuando con fallback degradado", file=sys.stderr)
        return None
    except Exception as exc:
        print(f"[seed-29] WARN preflight inesperado: {exc!r}; continuando", file=sys.stderr)
        return None


def main() -> int:
    preflight_exit = _run_preflight()
    if preflight_exit is not None:
        return preflight_exit

    print(f"29va Semilla — UPSERT contra {KERNEL_URL}")
    print(f"  signature: {SEMILLA_29['error_signature']}")
    print(f"  module: {SEMILLA_29['module']}")
    print(f"  confidence: {SEMILLA_29['confidence']}")
    print()
    result = upsert_semilla(SEMILLA_29)
    print(f"HTTP {result['status']}")
    if result.get("body"):
        print(json.dumps(result["body"], indent=2, ensure_ascii=False))
    if result.get("error"):
        print(f"ERROR: {result['error']}", file=sys.stderr)
    if result["status"] in (200, 201):
        print("✓ 29va semilla persistida (UPSERT idempotente)")
        return 0
    print("✗ Falló persistencia", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
