#!/usr/bin/env python3
"""
Smoke productivo Sprint 86.7 — Catastro Macroárea 4 LLM Razonamiento Estructurado.

6 gates:
  1. Pipeline incluye 3 reasoning sources cuando flag activa
  2. Run E2E exit 0 con dry_run + skip_persist
  3. Al menos 1 modelo persistible con data_extra.reasoning poblado
  4. Reasoning classification con tags del vocabulario controlado
  5. Anti-gaming v1 detectado en al menos 1 modelo (memorizer-math-v1)
  6. Anti-gaming v2 cross-area campos presentes (overfit_suspected, overfit_evidence)

[Hilo Manus Catastro] · Sprint 86.7 · 2026-05-05
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time

# Activar flags ANTES de importar pipeline
os.environ["CATASTRO_ENABLE_REASONING"] = "true"
os.environ["CATASTRO_ENABLE_CODING"] = "true"
os.environ["CATASTRO_SKIP_PERSIST"] = "true"

sys.path.insert(0, ".")
from kernel.catastro.pipeline import CatastroPipeline  # noqa: E402
from kernel.catastro.reasoning_classifier import REASONING_TAGS_VOCABULARY  # noqa: E402


GATES_RESULTS: list[tuple[str, bool, str]] = []


def gate(name: str, passed: bool, detail: str = "") -> None:
    GATES_RESULTS.append((name, passed, detail))
    icon = "OK " if passed else "FAIL"
    print(f"  [{icon}] {name}: {detail}")


async def main() -> int:
    print("\n=== SMOKE PRODUCTIVO SPRINT 86.7 — REASONING ===\n")
    started = time.time()

    # GATE 1: pipeline incluye 3 reasoning sources
    print("[1/6] Verificando flag CATASTRO_ENABLE_REASONING...")
    p = CatastroPipeline(dry_run=True)
    nombres = {s.nombre for s in p.sources}
    has_3_reasoning = all(n in nombres for n in ["aime", "gpqa", "mmlu_pro"])
    gate(
        "flag_reasoning_includes_3_sources",
        has_3_reasoning,
        f"sources: {sorted(nombres)}",
    )

    # GATE 2: run E2E exit 0
    print("[2/6] Ejecutando pipeline E2E...")
    try:
        result = await p.run()
        run_ok = True
        gate("pipeline_run_e2e", True, f"run_id={result.run_id[:8]}")
    except Exception as e:
        run_ok = False
        gate("pipeline_run_e2e", False, f"error: {e}")
        print("FAIL temprano - abortando smoke")
        return 1

    # GATE 3: al menos 1 modelo persistible con data_extra.reasoning
    print("[3/6] Verificando data_extra.reasoning poblado...")
    persistibles_with_reasoning = [
        (slug, m) for slug, m in result.modelos_persistibles.items()
        if "reasoning" in m.get("data_extra", {})
    ]
    gate(
        "data_extra_reasoning_populated",
        len(persistibles_with_reasoning) >= 1,
        f"{len(persistibles_with_reasoning)} modelos con reasoning",
    )

    # GATE 4: classification tags válidos
    print("[4/6] Verificando classification con vocabulario controlado...")
    classification_ok = False
    for slug, m in persistibles_with_reasoning:
        r = m.get("data_extra", {}).get("reasoning", {})
        cls = r.get("classification")
        if cls:
            tags = cls.get("tags", [])
            invalid_tags = [t for t in tags if t not in REASONING_TAGS_VOCABULARY]
            if not invalid_tags and tags:
                classification_ok = True
                gate(
                    "classification_vocabulary_valid",
                    True,
                    f"{slug}: tags={tags}",
                )
                break
    if not classification_ok:
        gate("classification_vocabulary_valid", False, "ningún modelo con tags válidos")

    # GATE 5: anti-gaming v1 detectado
    print("[5/6] Verificando anti-gaming v1 (memorizer-math-v1)...")
    # En el dry_run, memorizer-math-v1 NO debería pasar quorum (solo aparece en AIME),
    # pero al menos verificamos que el detect_gaming en el cache marcó algo
    gaming_v1_detected = False
    if hasattr(p, "_reasoning_cache"):
        for slug, cache in p._reasoning_cache.items():
            if cache.get("aime_gaming") or cache.get("gpqa_gaming") or cache.get("mmlu_pro_gaming"):
                gaming_v1_detected = True
                gate(
                    "anti_gaming_v1_detected",
                    True,
                    f"slug={slug} aime_g={cache.get('aime_gaming')}",
                )
                break
    if not gaming_v1_detected:
        gate("anti_gaming_v1_detected", False, "ningún modelo con gaming v1")

    # GATE 6: anti-gaming v2 fields presentes
    print("[6/6] Verificando anti-gaming v2 cross-area fields...")
    v2_fields_ok = False
    for slug, m in persistibles_with_reasoning:
        r = m.get("data_extra", {}).get("reasoning", {})
        if "overfit_suspected" in r and "overfit_evidence" in r:
            v2_fields_ok = True
            gate(
                "anti_gaming_v2_fields_present",
                True,
                f"{slug}: overfit_suspected={r['overfit_suspected']}",
            )
            break
    if not v2_fields_ok:
        gate("anti_gaming_v2_fields_present", False, "ningún modelo con campos v2")

    # Resumen final
    elapsed = time.time() - started
    n_passed = sum(1 for _, p, _ in GATES_RESULTS if p)
    n_total = len(GATES_RESULTS)
    print(f"\n=== RESUMEN: {n_passed}/{n_total} gates · {elapsed:.2f}s ===\n")

    if n_passed == n_total:
        print("SUCCESS · Sprint 86.7 production-ready")
        return 0
    print("FAILURE · Sprint 86.7 NO production-ready")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
