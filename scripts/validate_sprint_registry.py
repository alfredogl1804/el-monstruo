#!/usr/bin/env python3
"""
validate_sprint_registry.py — CI guard del Sprint Registry.

Sprint 91.16. Garantiza que `sprints/registry.yaml` se mantenga consistente:

1. El YAML parsea y tiene estructura `{version, sprints: [...]}`.
2. Cada sprint tiene los campos requeridos (id, status, paradigm).
3. `id` único en todo el archivo.
4. `status` ∈ {PROPOSED, SIGNED, IN_PROGRESS, COMPLETED, CANCELLED, BLOCKED}.
5. `paradigm` ∈ {acto_1_pantallas, acto_2_calm_tech, transversal,
   obsoleto_pendiente_decision, capa_transversal_comercial, vanguardia_perpetua}.
6. Cada `path` referenciado debe existir físicamente en el repo.
7. Cada archivo en `bridge/sprints_propuestos/sprint_*.md` debería estar
   referenciado en el registry (warning si no, no error).

Falla con exit code 1 si encuentra errores, exit 0 si todo OK.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "sprints" / "registry.yaml"
PROPUESTOS_DIR = ROOT / "bridge" / "sprints_propuestos"
COMPLETADOS_DIR = ROOT / "bridge" / "sprints_completados"

VALID_STATUSES = {
    "PROPOSED",
    "SIGNED",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELLED",
    "BLOCKED",
}

VALID_PARADIGMS = {
    "acto_1_pantallas",
    "acto_2_calm_tech",
    "transversal",
    "obsoleto_pendiente_decision",
    "capa_transversal_comercial",
    "vanguardia_perpetua",
}

REQUIRED_FIELDS = {"id", "status"}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not REGISTRY_PATH.exists():
        print(f"FAIL: {REGISTRY_PATH} no existe", file=sys.stderr)
        return 1

    try:
        data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: registry.yaml no parsea: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict) or not isinstance(data.get("sprints"), list):
        print("FAIL: estructura del registry inválida", file=sys.stderr)
        return 1

    seen_ids: dict[str, int] = {}
    referenced_paths: set[str] = set()

    for i, sprint in enumerate(data["sprints"]):
        if not isinstance(sprint, dict):
            errors.append(f"#{i}: entrada no es dict")
            continue

        sid = sprint.get("id")
        if not sid:
            errors.append(f"#{i}: id faltante")
            continue

        # Campos requeridos
        for field in REQUIRED_FIELDS:
            if field not in sprint:
                errors.append(f"{sid}: campo requerido '{field}' faltante")

        # Unicidad de id
        if sid in seen_ids:
            errors.append(f"{sid}: id duplicado (también en posición #{seen_ids[sid]})")
        else:
            seen_ids[sid] = i

        # Status válido
        status = sprint.get("status")
        if status and status not in VALID_STATUSES:
            errors.append(f"{sid}: status inválido '{status}' (válidos: {sorted(VALID_STATUSES)})")

        # Paradigm válido (opcional pero si existe debe ser válido)
        paradigm = sprint.get("paradigm")
        if paradigm and paradigm not in VALID_PARADIGMS:
            errors.append(f"{sid}: paradigm inválido '{paradigm}' (válidos: {sorted(VALID_PARADIGMS)})")

        # Path referenciado debe existir
        path_str = sprint.get("path")
        if path_str:
            referenced_paths.add(path_str)
            full = ROOT / path_str
            if not full.exists():
                errors.append(f"{sid}: path '{path_str}' no existe en el repo")

    # Warning: archivos en sprints_propuestos sin referencia en registry
    if PROPUESTOS_DIR.exists():
        for md in sorted(PROPUESTOS_DIR.glob("sprint_*.md")):
            rel = md.relative_to(ROOT).as_posix()
            if rel not in referenced_paths:
                warnings.append(f"propuesto sin referencia en registry: {rel}")

    # Resultado
    if warnings:
        print("⚠️  Warnings:")
        for w in warnings:
            print(f"   - {w}")
        print()

    if errors:
        print("❌ Errores:")
        for e in errors:
            print(f"   - {e}", file=sys.stderr)
        print(f"\nTotal: {len(errors)} errores, {len(warnings)} warnings", file=sys.stderr)
        return 1

    print(f"✅ registry.yaml OK ({len(data['sprints'])} sprints, {len(warnings)} warnings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
