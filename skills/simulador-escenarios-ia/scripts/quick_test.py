#!/usr/bin/env python3
"""
Test rápido del Simulador Universal.
Verifica conectividad con el motor y ejecuta una simulación mínima.
"""
import json
import sys
import time

import requests

API_BASE = "https://simulador-api-production.up.railway.app"


def test_health():
    """Verificar que el motor está vivo."""
    print("1. Testing /health...")
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=15)
        data = resp.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Version: {data.get('version')}")
        print(f"   Supabase: {data.get('supabase_connected')}")
        print(f"   LLM: {data.get('llm_available')}")
        return data.get("status") == "ok"
    except Exception as e:
        print(f"   ERROR: {e}")
        return False


def test_profiles():
    """Listar perfiles disponibles."""
    print("\n2. Testing /profiles...")
    try:
        resp = requests.get(f"{API_BASE}/profiles", timeout=10)
        data = resp.json()
        profiles = data.get("profiles", [])
        print(f"   Perfiles encontrados: {len(profiles)}")
        for p in profiles:
            print(f"   - {p.get('name', '?')}: {p.get('display_name', '?')}")
        return len(profiles) > 0
    except Exception as e:
        print(f"   ERROR: {e}")
        return False


def test_monte_carlo_only():
    """Ejecutar simulación Monte Carlo mínima."""
    print("\n3. Testing Monte Carlo simulation...")
    payload = {
        "name": "Test MC",
        "profile": "custom",
        "user_prompt": "Test de conectividad",
        "monte_carlo": {
            "iterations": 100,
            "variables": [
                {
                    "name": "test_var",
                    "distribution": "normal",
                    "params": {"mean": 50, "std": 10},
                }
            ],
        },
    }
    try:
        resp = requests.post(f"{API_BASE}/simulations", json=payload, timeout=30)
        data = resp.json()
        sim_id = data.get("simulation_id")
        print(f"   Simulation ID: {sim_id}")
        print(f"   Status: {data.get('status')}")

        # Esperar resultado
        for _ in range(12):
            time.sleep(5)
            status = requests.get(f"{API_BASE}/simulations/{sim_id}/status", timeout=10).json()
            print(f"   Polling... status={status.get('status')}")
            if status.get("status") != "running":
                break

        results = requests.get(f"{API_BASE}/simulations/{sim_id}/results", timeout=10).json()
        print(f"   Final status: {results.get('status')}")
        if results.get("monte_carlo_results"):
            mc = results["monte_carlo_results"]
            print(f"   MC Results: {json.dumps(mc, indent=2)[:500]}")
        return results.get("status") == "completed"
    except Exception as e:
        print(f"   ERROR: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("SIMULADOR UNIVERSAL — Quick Test")
    print("=" * 60)

    results = {
        "health": test_health(),
        "profiles": test_profiles(),
        "monte_carlo": test_monte_carlo_only(),
    }

    print("\n" + "=" * 60)
    print("RESULTADOS:")
    for test, passed in results.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {test}")

    all_passed = all(results.values())
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    sys.exit(0 if all_passed else 1)
