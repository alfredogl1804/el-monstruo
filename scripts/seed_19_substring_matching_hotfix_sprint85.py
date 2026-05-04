"""
SEMILLA 19 — HOTFIX Sprint 85: substring matching → word boundaries.
======================================================================
Sembrada localmente por el [Hilo Manus Catastro] mientras se aplica el
HOTFIX preventivo en 3 archivos del Sprint 85, anticipando el refactor
global del Sprint 84.7 (Hilo Ejecutor).

Cuando el endpoint POST /v1/error-memory/seed esté live (Sprint 84.5.5),
ejecutar este script para persistir la semilla en Supabase.

Uso:
    python scripts/seed_19_substring_matching_hotfix_sprint85.py

Spec del patrón: bridge/cowork_to_manus.md sección 🚨 AUDIT MASIVO (2026-05-04)
Patrón aprobado: Sprint 84.5
"""
from __future__ import annotations

import json
import os
import sys


SEED_19_HOTFIX_SUBSTRING_SPRINT85 = {
    "error_signature": "seed_substring_matching_hotfix_sprint85_resolved",
    "sanitized_message": (
        "[Hilo Manus Catastro] HOTFIX preventivo Sprint 85: refactor del patrón "
        "`any(kw in text for kw in keywords)` en 3 archivos del Sprint 85 "
        "(product_architect.py:313, task_planner.py:1638, critic_visual.py:449). "
        "Causa: substring matching sin word boundaries provoca falsos positivos "
        "como 'artesanal' matcheando `arte`, 'saasoso' matcheando `saas`. "
        "Aplicado patrón aprobado del Sprint 84.5: regex con `\\b...\\b`, "
        "compilado a nivel módulo y cacheado, soporta multi-word keywords."
    ),
    "resolution": (
        "Cada archivo refactorizado usa `re.compile(r'\\b(?:kw1|kw2|...)\\b', re.IGNORECASE)` "
        "con keywords ordenadas por longitud descendente para greedy alternation. "
        "Pattern cacheado en _PATTERN_CACHE (product_architect) o _WEB_PROJECT_PATTERN "
        "(task_planner) o pattern local (critic_visual). 24 tests de regresión PASS "
        "(tests/test_sprint85_hotfix_substring.py). Cuando Sprint 84.7 cree "
        "kernel/utils/keyword_matcher.py, migrar drop-in a la utility centralizada."
    ),
    "confidence": 0.90,
    "module": "kernel.embriones.product_architect+kernel.task_planner+kernel.embriones.critic_visual",
    "status": "resolved",
    "metadata": {
        "sprint": "85-hotfix",
        "files_refactored": [
            "kernel/embriones/product_architect.py:_detectar_vertical",
            "kernel/task_planner.py:_es_proyecto_web",
            "kernel/embriones/critic_visual.py:_evaluar_estructura",
        ],
        "tests_added": "tests/test_sprint85_hotfix_substring.py (24 tests)",
        "spec_source": "bridge/cowork_to_manus.md sección 🚨 AUDIT MASIVO (2026-05-04)",
        "depends_on": "Sprint 84.7 (Hilo Ejecutor) creará kernel/utils/keyword_matcher.py — drop-in migration",
    },
}


def main():
    api_url = os.environ.get(
        "ERROR_MEMORY_SEED_URL",
        "http://localhost:8000/v1/error-memory/seed",
    )
    print(f"Sembrando semilla 19 en {api_url} ...")
    try:
        import urllib.request
        req = urllib.request.Request(
            api_url,
            data=json.dumps(SEED_19_HOTFIX_SUBSTRING_SPRINT85).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Status: {resp.status}")
            print(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"Endpoint no disponible aún (esperado si Sprint 84.5.5 no cerró): {exc}")
        print("\nPayload listo para sembrar manualmente cuando el endpoint abra:")
        print(json.dumps(SEED_19_HOTFIX_SUBSTRING_SPRINT85, indent=2, ensure_ascii=False))
        return 0  # No es error, es estado esperado


if __name__ == "__main__":
    sys.exit(main() or 0)
