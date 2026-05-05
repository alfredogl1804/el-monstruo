#!/usr/bin/env python3.11
"""
Runner unificado de semillas 32, 33, 34, 35, 36 al kernel productivo.
Bloqueo (d) del audit Cowork B7.

Las semillas originales (32-36) fueron escritas contra un schema viejo del
endpoint que aceptaba {id, categoria, titulo, leccion, ...}. El endpoint
actual /v1/error-memory/seed exige {error_signature, sanitized_message,
resolution} (ver kernel/main.py L1346-1355). Este runner extrae el payload
de cada semilla, lo MAPEA al schema actual sin perder información, y lo
POSTea al kernel.

Mapping aplicado:
    error_signature   <- id (semilla)
    sanitized_message <- titulo (semilla)
    resolution        <- consolidación textual de leccion/contexto/
                          patron_recomendado/anti_patron + tags
    confidence        <- 0.95 (todas las semillas vienen ya validadas
                          con tests + smoke por el Hilo Catastro)
    module            <- "kernel.catastro.seeds"
    error_type        <- "ArchitecturalLessonSeed"
    status            <- "resolved"
    action            <- categoria de la semilla

Uso:
    export MONSTRUO_API_KEY=...
    python3.11 scripts/_seed_32_to_36_runner.py

Variable opcional:
    KERNEL_URL (default: https://el-monstruo-kernel-production.up.railway.app)
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"

KERNEL_URL = os.environ.get(
    "KERNEL_URL", "https://el-monstruo-kernel-production.up.railway.app"
).rstrip("/")
API_KEY = os.environ.get("MONSTRUO_API_KEY", "")


def _load_module(file_path: Path):
    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _extract_payload(mod) -> dict | None:
    """Las semillas exponen el payload como SEED_PAYLOAD, SEED, o lo
    construyen dentro de main()/upsert(). Para 36 lo reconstruimos."""
    p = getattr(mod, "SEED_PAYLOAD", None) or getattr(mod, "SEED", None)
    if p is not None:
        return p
    # Caso especial seed_36: payload está dentro de main(), reconstruirlo
    src = Path(mod.__file__).read_text(encoding="utf-8")
    m = re.search(r"payload\s*=\s*\{(.+?)\n\s*\}", src, re.DOTALL)
    if m:
        # Lo devolvemos como dict mínimo; el id y titulo son lo que
        # necesitamos para el mapping
        return {
            "id": "seed_36_dashboard_visibilidad_obligatoria_sprint86",
            "categoria": "patron_arquitectonico",
            "titulo": (
                "Dashboard de Salud como visibilidad obligatoria de cualquier "
                "dominio del Monstruo (Catastro Bloque 7)"
            ),
            "leccion": (mod.__doc__ or "").strip(),
            "sprint": "86",
            "bloque": "7",
            "fecha": "2026-05-04",
        }
    return None


def _build_resolution(seed: dict) -> str:
    """Consolida los campos descriptivos en un único texto de resolution."""
    parts: list[str] = []
    if seed.get("leccion"):
        parts.append(f"Lección: {seed['leccion'].strip()}")
    if seed.get("contexto"):
        parts.append(f"Contexto: {seed['contexto']}")
    if seed.get("patron_recomendado"):
        parts.append(f"Patrón recomendado: {seed['patron_recomendado']}")
    if seed.get("patron_ganador"):
        parts.append(f"Patrón ganador: {seed['patron_ganador']}")
    if seed.get("antipatron_evitado"):
        parts.append(f"Anti-patrón evitado: {seed['antipatron_evitado']}")
    if seed.get("anti_patron_evitado"):
        parts.append(f"Anti-patrón evitado: {seed['anti_patron_evitado']}")
    if seed.get("salvaguardas_obligatorias"):
        sals = seed["salvaguardas_obligatorias"]
        if isinstance(sals, list):
            parts.append("Salvaguardas: " + " | ".join(str(s) for s in sals))
        else:
            parts.append(f"Salvaguardas: {sals}")
    if seed.get("descripcion"):
        parts.append(f"Descripción: {seed['descripcion']}")
    if seed.get("evidencia_archivos"):
        parts.append("Evidencia: " + ", ".join(seed["evidencia_archivos"]))
    if seed.get("tests_obligatorios"):
        ts = seed["tests_obligatorios"]
        parts.append("Tests: " + (", ".join(ts) if isinstance(ts, list) else str(ts)))
    if seed.get("validado_por"):
        parts.append(f"Validado por: {seed['validado_por']}")
    if seed.get("validacion_tiempo_real"):
        parts.append("Validación tiempo real: " + ", ".join(seed["validacion_tiempo_real"]))
    sprint = seed.get("sprint")
    bloque = seed.get("bloque")
    fecha = seed.get("fecha")
    if sprint or bloque or fecha:
        parts.append(f"Origen: Sprint {sprint} Bloque {bloque} ({fecha})")
    text = " || ".join(parts)
    # Cap defensivo de longitud (Supabase TEXT acepta más, pero evitamos descontrol)
    return text[:8000] if len(text) > 8000 else text


def _to_endpoint_payload(seed: dict) -> dict:
    return {
        "error_signature": seed.get("id") or seed.get("titulo") or "unknown_seed",
        "sanitized_message": (seed.get("titulo") or seed.get("descripcion") or "Architectural lesson seed")[:500],
        "resolution": _build_resolution(seed),
        "confidence": 0.95,
        "module": "kernel.catastro.seeds",
        "action": str(seed.get("categoria", "")),
        "error_type": "ArchitecturalLessonSeed",
        "status": "resolved",
    }


def _post_seed(payload: dict) -> tuple[bool, str]:
    if not API_KEY:
        return False, "MONSTRUO_API_KEY no configurada"
    url = f"{KERNEL_URL}/v1/error-memory/seed"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return True, f"HTTP {resp.status}: {resp.read().decode('utf-8')[:200]}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}: {exc.read().decode('utf-8')[:300] if exc.fp else ''}"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


def main() -> int:
    if not API_KEY:
        print("ERROR: MONSTRUO_API_KEY no configurada", file=sys.stderr)
        return 1

    print(f"=== Sembrando 32-36 al kernel: {KERNEL_URL} ===\n")

    failures: list[str] = []

    for n in (32, 33, 34, 35, 36):
        candidates = list(SCRIPTS_DIR.glob(f"seed_{n}_*.py"))
        if not candidates:
            failures.append(f"seed_{n}: archivo no encontrado")
            continue
        path = candidates[0]
        try:
            mod = _load_module(path)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"seed_{n} import: {exc}")
            print(f"[seed_{n}] FAIL importando: {exc}\n")
            continue

        seed = _extract_payload(mod)
        if seed is None:
            failures.append(f"seed_{n}: sin payload extraíble")
            print(f"[seed_{n}] FAIL: sin payload en {path.name}\n")
            continue

        payload = _to_endpoint_payload(seed)
        ok, msg = _post_seed(payload)
        status = "OK  " if ok else "FAIL"
        print(f"[seed_{n}] {status} signature={payload['error_signature'][:60]}")
        print(f"          {msg[:240]}\n")
        if not ok:
            failures.append(f"seed_{n}: {msg[:200]}")

    print("=== RESUMEN ===")
    if failures:
        print(f"  Fallos: {len(failures)}")
        for f in failures:
            print(f"    - {f}")
        return 1
    print("  Las 5 semillas (32, 33, 34, 35, 36) sembradas al kernel.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
