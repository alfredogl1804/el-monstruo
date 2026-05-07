"""
Runner standalone para los tests E2E sin depender de pytest.
Ejecutar desde la raíz del repo: python kernel/catastro/tests/run_tests_standalone.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Bypass __init__.py del catastro (que importa pydantic/dashboard pesados)
# cargando multi_namespace.py directamente con importlib.
import importlib.util

MODULE_PATH = Path(__file__).resolve().parent.parent / "multi_namespace.py"
spec = importlib.util.spec_from_file_location("multi_namespace", MODULE_PATH)
mn = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mn)

NAMESPACES = mn.NAMESPACES
find_best = mn.find_best
load_all = mn.load_all
peers_of = mn.peers_of
validate_against_spec = mn.validate_against_spec


def run() -> int:
    failed = 0

    # Test 1
    try:
        data = load_all()
        assert set(data.keys()) == set(NAMESPACES)
        for ns in NAMESPACES:
            assert "entries" in data[ns]
            assert "_meta" in data[ns]
            assert len(data[ns]["entries"]) > 0
        print("PASS test_load_all_3_namespaces")
    except AssertionError as exc:
        print(f"FAIL test_load_all_3_namespaces: {exc}")
        failed += 1

    # Test 2
    try:
        results = find_best("render arquitectonico", "tools", top_k=3)
        assert isinstance(results, list) and len(results) <= 3
        print(f"PASS test_find_best_render ({len(results)} results)")
    except AssertionError as exc:
        print(f"FAIL test_find_best_render: {exc}")
        failed += 1

    # Test 3 — buscar suppliers con palabras que están en sus nombres reales
    try:
        results = find_best("merida diseño", "suppliers", top_k=10)
        assert len(results) > 0
        # Esperamos al menos un match con keyword 'merida' (id contiene merida)
        merida_matches = [e for e in results if "merida" in str(e.get("id", "")).lower()]
        assert len(merida_matches) > 0, f"esperaba matches con 'merida' en id"
        print(f"PASS test_find_best_suppliers_merida ({len(merida_matches)} merida matches)")
    except AssertionError as exc:
        print(f"FAIL test_find_best_suppliers_merida: {exc}")
        failed += 1

    # Test 4
    try:
        peers = peers_of("bc_studio_arq", "suppliers", same_category=True)
        assert len(peers) > 0
        for p in peers:
            assert p.get("categoria") == "estudios_arquitectura_interiores"
            assert p.get("id") != "bc_studio_arq"
        print(f"PASS test_peers_of_same_category ({len(peers)} peers)")
    except AssertionError as exc:
        print(f"FAIL test_peers_of_same_category: {exc}")
        failed += 1

    # Test 5
    try:
        result = validate_against_spec()
        assert result["ok"]
        a = result["namespaces"]["agentes"]["entries"]
        t = result["namespaces"]["tools"]["entries"]
        s = result["namespaces"]["suppliers"]["entries"]
        assert a >= 21
        assert t >= 16
        assert s >= 30
        print(f"PASS test_validate_against_spec (a={a}, t={t}, s={s})")
    except AssertionError as exc:
        print(f"FAIL test_validate_against_spec: {exc}")
        failed += 1

    # Test 6 e2e
    try:
        spec_result = validate_against_spec()
        assert spec_result["ok"]
        tools = find_best("render fotorealista 3d", "tools", top_k=3)
        assert len(tools) > 0
        selected = tools[0]
        peers = peers_of(selected["id"], "tools", same_category=True)
        assert isinstance(peers, list)
        print(
            f"PASS test_e2e_workflow (selected={selected['id']}, peers={len(peers)})"
        )
    except AssertionError as exc:
        print(f"FAIL test_e2e_workflow: {exc}")
        failed += 1

    print()
    if failed == 0:
        print("All 6/6 tests PASSED")
        return 0
    else:
        print(f"{failed}/6 tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run())
