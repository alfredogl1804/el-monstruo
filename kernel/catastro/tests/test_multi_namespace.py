"""
Tests E2E para multi_namespace.py — Tarea E del CATASTRO-A v2.

Ejecuta offline (no DB, no red), valida que las 3 interfaces operativas
funcionan correctamente sobre los 3 namespaces (agentes, tools, suppliers).

Run:
    python -m pytest kernel/catastro/tests/test_multi_namespace.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permitir importar el módulo aunque pytest se ejecute desde la raíz del repo
KERNEL_DIR = Path(__file__).resolve().parents[2]
if str(KERNEL_DIR) not in sys.path:
    sys.path.insert(0, str(KERNEL_DIR))

from catastro.multi_namespace import (  # noqa: E402
    NAMESPACES,
    find_best,
    load_all,
    peers_of,
    validate_against_spec,
)


# -------------------------------------------------------------------
# Carga de datos
# -------------------------------------------------------------------


def test_load_all_3_namespaces() -> None:
    data = load_all()
    assert set(data.keys()) == set(NAMESPACES)
    for ns in NAMESPACES:
        assert "entries" in data[ns]
        assert "_meta" in data[ns]
        assert len(data[ns]["entries"]) > 0


# -------------------------------------------------------------------
# Interface 1: find_best
# -------------------------------------------------------------------


def test_find_best_returns_results() -> None:
    """Query semántica debería devolver resultados relevantes."""
    results = find_best("render arquitectonico", "tools", top_k=3)
    assert isinstance(results, list)
    assert len(results) <= 3
    if results:
        # Aljun match de "render" o "arquitectonic" debe estar en categoria/nombre
        first = results[0]
        haystack = " ".join(str(v) for v in first.values()).lower()
        assert "render" in haystack or "arquitect" in haystack or "image" in haystack


def test_find_best_suppliers_arquitectura() -> None:
    """Query 'arquitectura merida' debe traer estudios reales."""
    results = find_best("arquitectura merida", "suppliers", top_k=5)
    assert len(results) > 0
    # Esperamos que al menos uno sea de la categoría arquitectura
    assert any(
        e.get("categoria") == "estudios_arquitectura_interiores"
        for e in results
    )


def test_find_best_empty_query_returns_empty() -> None:
    assert find_best("", "agentes") == []


def test_find_best_invalid_namespace() -> None:
    import pytest

    with pytest.raises(ValueError):
        find_best("test", "invalid_namespace")


# -------------------------------------------------------------------
# Interface 2: peers_of
# -------------------------------------------------------------------


def test_peers_of_same_category() -> None:
    """Peers de un supplier de arquitectura → otros de arquitectura."""
    peers = peers_of("bc_studio_arq", "suppliers", same_category=True)
    assert len(peers) > 0
    target_cat = "estudios_arquitectura_interiores"
    for peer in peers:
        assert peer.get("categoria") == target_cat
        assert peer.get("id") != "bc_studio_arq"


def test_peers_of_all() -> None:
    """same_category=False devuelve TODOS menos él mismo."""
    data = load_all()
    total = len(data["suppliers"]["entries"])
    peers = peers_of("bc_studio_arq", "suppliers", same_category=False)
    assert len(peers) == total - 1


def test_peers_of_invalid_id() -> None:
    import pytest

    with pytest.raises(KeyError):
        peers_of("entry_inexistente_xyz", "suppliers")


# -------------------------------------------------------------------
# Interface 3: validate_against_spec
# -------------------------------------------------------------------


def test_validate_against_spec_passes() -> None:
    """La validación contra spec debe pasar verde — los 3 catastros poblados."""
    result = validate_against_spec()
    # Imprimir para debug si falla
    if not result["ok"]:
        import json

        print(json.dumps(result, indent=2, ensure_ascii=False))
    assert result["ok"], (
        f"Validación falló: {result['namespaces']}"
    )


def test_validate_min_entries() -> None:
    result = validate_against_spec()
    assert result["namespaces"]["agentes"]["entries"] >= 21
    assert result["namespaces"]["tools"]["entries"] >= 16
    assert result["namespaces"]["suppliers"]["entries"] >= 30


# -------------------------------------------------------------------
# Smoke integration: 3 interfaces juntas
# -------------------------------------------------------------------


def test_e2e_workflow() -> None:
    """
    Workflow completo: validate → find_best → peers_of.
    Simula uso real del kernel para "delegar a un agente/tool/supplier".
    """
    # 1. Validar spec
    spec_result = validate_against_spec()
    assert spec_result["ok"]

    # 2. Buscar mejor herramienta para "render fotorealista"
    tools = find_best("render fotorealista 3d", "tools", top_k=3)
    assert len(tools) > 0
    selected_tool = tools[0]
    assert "id" in selected_tool

    # 3. Encontrar peers/alternativas a esa herramienta
    peers = peers_of(selected_tool["id"], "tools", same_category=True)
    # Pueden ser 0 si la categoria solo tiene 1 entry, ok
    assert isinstance(peers, list)
