"""
Multi-Namespace Catastro — Interfaces operativas para los 4 catastros canónicos.

Spec: bridge/sprints_propuestos/sprint_catastro_A_investigacion_poblamiento.md
DSC:  discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-G-007_aldea_4_catastros_self_reference_2026_05_06.md

Este módulo expone las 3 interfaces operativas del CATASTRO-A v2 sobre los
namespaces de Agentes 2026, Herramientas AI Verticales y Suppliers Humanos
Sureste MX. NO toca el catastro de Modelos LLM (kernel/catastro/) que es
operacional desde Sprint 89.

Diseño NO INVASIVO:
- Carga JSONs desde kernel/catastro/data/ (data-driven, sin code dependencies)
- Tres interfaces (find_best, peers_of, validate_against_spec) puramente funcionales
- Sin estado mutable, sin side effects
- Compatible con tests E2E offline (no requiere DB ni red)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"

NAMESPACES = ("agentes", "tools", "suppliers")


# -------------------------------------------------------------------
# Carga de datos
# -------------------------------------------------------------------


def _load_namespace(ns: str) -> dict[str, Any]:
    """Carga un namespace JSON desde data/. Fail-loud si no existe."""
    if ns not in NAMESPACES:
        raise ValueError(
            f"Namespace '{ns}' invalido. Validos: {NAMESPACES}"
        )
    path = DATA_DIR / f"catastro_{ns}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Catastro '{ns}' no encontrado en {path}. "
            "Poblar via spec sprint_catastro_A_investigacion_poblamiento.md"
        )
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_all() -> dict[str, dict[str, Any]]:
    """Carga los 3 catastros en un solo dict."""
    return {ns: _load_namespace(ns) for ns in NAMESPACES}


# -------------------------------------------------------------------
# Interface 1: find_best(query, namespace)
# -------------------------------------------------------------------


def find_best(
    query: str,
    namespace: str,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """
    Devuelve top_k entries del namespace que mejor matchean la query.

    Scoring simple por solapamiento de tokens (case-insensitive) entre
    la query y los campos textuales del entry. NO usa embeddings;
    es determinístico y suficiente para el corpus actual (<100 entries
    por namespace).

    Args:
        query: texto libre con keywords. Ej: "render arquitectonico"
        namespace: uno de "agentes" | "tools" | "suppliers"
        top_k: numero de matches a devolver (default 3)

    Returns:
        Lista de entries ordenados por score descendente.
    """
    data = _load_namespace(namespace)
    entries = data["entries"]

    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return []

    scored: list[tuple[float, dict[str, Any]]] = []
    for entry in entries:
        haystack = _flatten_text(entry).lower()
        haystack_tokens = set(_tokenize(haystack))
        score = len(query_tokens & haystack_tokens)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda t: t[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]


# -------------------------------------------------------------------
# Interface 2: peers_of(entry_id, namespace)
# -------------------------------------------------------------------


def peers_of(
    entry_id: str,
    namespace: str,
    same_category: bool = True,
) -> list[dict[str, Any]]:
    """
    Devuelve entries pares al entry_id dentro del namespace.

    Si same_category=True (default), filtra por la misma categoria
    del entry. Util para "espejo peer" — comparativa horizontal entre
    suppliers/tools/agentes equivalentes.

    Args:
        entry_id: id canonico del entry de referencia
        namespace: uno de "agentes" | "tools" | "suppliers"
        same_category: filtrar solo dentro de la misma categoria

    Returns:
        Lista de peers (excluyendo al entry mismo).
    """
    data = _load_namespace(namespace)
    entries = data["entries"]

    target = next((e for e in entries if e.get("id") == entry_id), None)
    if target is None:
        raise KeyError(
            f"entry_id '{entry_id}' no existe en namespace '{namespace}'"
        )

    if not same_category:
        return [e for e in entries if e.get("id") != entry_id]

    target_cat = target.get("categoria")
    return [
        e
        for e in entries
        if e.get("categoria") == target_cat and e.get("id") != entry_id
    ]


# -------------------------------------------------------------------
# Interface 3: validate_against_spec()
# -------------------------------------------------------------------


SPEC_REQUIREMENTS = {
    "agentes": {"min_entries": 21, "required_fields": ("id", "nombre", "categoria")},
    "tools": {"min_entries": 16, "required_fields": ("id", "nombre", "categoria")},
    "suppliers": {"min_entries": 30, "required_fields": ("id", "nombre_legal", "categoria")},
}


def validate_against_spec() -> dict[str, Any]:
    """
    Valida que los 3 catastros cumplan los requisitos minimos de la spec.

    Devuelve un dict con resultado per namespace y el flag global.
    Los requisitos vienen de:
        bridge/sprints_propuestos/sprint_catastro_A_investigacion_poblamiento.md

    Returns:
        {
          "ok": bool,
          "namespaces": {
             "agentes": {"ok": bool, "entries": int, "missing_fields": [...]},
             ...
          }
        }
    """
    result: dict[str, Any] = {"ok": True, "namespaces": {}}

    for ns, req in SPEC_REQUIREMENTS.items():
        ns_result: dict[str, Any] = {"ok": True}
        try:
            data = _load_namespace(ns)
        except (FileNotFoundError, ValueError) as exc:
            ns_result["ok"] = False
            ns_result["error"] = str(exc)
            result["ok"] = False
            result["namespaces"][ns] = ns_result
            continue

        entries = data.get("entries", [])
        ns_result["entries"] = len(entries)

        if len(entries) < req["min_entries"]:
            ns_result["ok"] = False
            ns_result["error"] = (
                f"min_entries={req['min_entries']} requerido, "
                f"actual={len(entries)}"
            )
            result["ok"] = False

        # Check required fields
        missing = []
        for entry in entries:
            for field in req["required_fields"]:
                if field not in entry or entry.get(field) is None:
                    missing.append({"id": entry.get("id", "?"), "field": field})
        if missing:
            ns_result["ok"] = False
            ns_result["missing_fields"] = missing[:10]  # cap a 10
            result["ok"] = False

        result["namespaces"][ns] = ns_result

    return result


# -------------------------------------------------------------------
# Helpers internos
# -------------------------------------------------------------------


def _tokenize(text: str) -> list[str]:
    """Tokenizer simple alphanumeric, case-insensitive."""
    return re.findall(r"[a-z0-9áéíóúñ]+", text.lower())


def _flatten_text(obj: Any) -> str:
    """Aplana recursivamente strings de un dict/list para indexar."""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return " ".join(_flatten_text(v) for v in obj.values() if v is not None)
    if isinstance(obj, list):
        return " ".join(_flatten_text(v) for v in obj if v is not None)
    return ""


# -------------------------------------------------------------------
# CLI rapido para smoke test manual
# -------------------------------------------------------------------


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso:")
        print("  python multi_namespace.py validate")
        print("  python multi_namespace.py find <namespace> <query>")
        print("  python multi_namespace.py peers <namespace> <entry_id>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "validate":
        result = validate_against_spec()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["ok"] else 1)

    elif cmd == "find":
        if len(sys.argv) < 4:
            print("Uso: find <namespace> <query>")
            sys.exit(1)
        results = find_best(sys.argv[3], sys.argv[2])
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif cmd == "peers":
        if len(sys.argv) < 4:
            print("Uso: peers <namespace> <entry_id>")
            sys.exit(1)
        results = peers_of(sys.argv[3], sys.argv[2])
        print(json.dumps(results, indent=2, ensure_ascii=False))

    else:
        print(f"Comando desconocido: {cmd}")
        sys.exit(1)
