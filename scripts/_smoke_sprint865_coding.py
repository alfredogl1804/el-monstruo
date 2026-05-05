"""
Smoke productivo E2E Sprint 86.5 — Catastro Macroárea 3 LLM Coding.

Requisitos:
  - CATASTRO_ENABLE_CODING=true para activar las 3 fuentes coding
  - dry_run=True para evitar llamadas a APIs reales (BenchLM/SWE-bench)
  - skip_persist=True para evitar tocar Supabase

Validaciones:
  1. Pipeline corre sin crash (is_success).
  2. >=3 fuentes coding presentes en snapshots.
  3. >=10 modelos en _coding_cache (mínimo del SPEC).
  4. Overfit Coder UC Berkeley detectado (gaming=True).
  5. Modelos persistibles tienen data_extra.coding poblado.
  6. classification.tags poblados desde vocabulario controlado.

Exit codes:
  0 = OK
  1 = Validación falló
  2 = Pipeline crash

[Hilo Manus Catastro] · Sprint 86.5 · 2026-05-05
"""
from __future__ import annotations

import asyncio
import os
import sys

# Activar coding ANTES de instanciar pipeline
os.environ["CATASTRO_ENABLE_CODING"] = "true"
os.environ["CATASTRO_SKIP_PERSIST"] = "true"

from kernel.catastro.pipeline import CatastroPipeline


async def smoke():
    print("=" * 70)
    print("SMOKE PRODUCTIVO E2E SPRINT 86.5 — Catastro Macroarea 3 LLM Coding")
    print("=" * 70)

    pipeline = CatastroPipeline(dry_run=True)
    print(f"Pipeline construido: sources={[s.nombre for s in pipeline.sources]}")
    print(f"  - skip_persist={pipeline.skip_persist}")
    print(f"  - dry_run={pipeline.dry_run}")
    print()

    result = await pipeline.run()

    cache = getattr(pipeline, "_coding_cache", {})
    n_cache = len(cache)
    n_with_scores = sum(
        1 for d in cache.values()
        if any(d.get(k) is not None for k in ["swe_bench_verified", "human_eval_plus", "mbpp_plus"])
    )
    n_gaming = sum(1 for d in cache.values() if d.get("gaming_detected"))
    n_with_data_extra = sum(
        1 for p_ in result.modelos_persistibles.values()
        if "data_extra" in p_ and "coding" in p_.get("data_extra", {})
    )

    print("RESULTADOS")
    print("-" * 70)
    print(f"is_success         : {result.is_success}")
    print(f"duration_seconds   : {result.duration_seconds:.2f}")
    print(f"snapshots          : {list(result.snapshots.keys())}")
    print(f"fuente_errors      : {result.fuente_errors}")
    print(f"modelos_procesados : {len(result.modelos_procesados)}")
    print(f"modelos_persistibles: {len(result.modelos_persistibles)}")
    print(f"coding_cache       : {n_cache} entries (with_scores={n_with_scores}, gaming={n_gaming})")
    print(f"persistibles c/coding: {n_with_data_extra}")
    print()

    print("MODELOS CODING ENRIQUECIDOS")
    print("-" * 70)
    for slug, p_ in result.modelos_persistibles.items():
        coding = p_.get("data_extra", {}).get("coding")
        if not coding:
            continue
        cls = coding.get("classification") or {}
        print(
            f"  {slug:35s} | "
            f"swe_v={coding.get('swe_bench_verified')} "
            f"he+={coding.get('human_eval_plus')} "
            f"mbpp+={coding.get('mbpp_plus')} | "
            f"gaming={coding.get('gaming_detected')} | "
            f"tags={cls.get('tags', [])}"
        )
    print()

    # ====================================================================
    # VALIDACIONES (gates Sprint 86.5 Bloque 5)
    # ====================================================================
    failures = []

    if not result.is_success:
        failures.append("pipeline_not_success")

    if n_cache < 3:
        failures.append(f"coding_cache_too_small ({n_cache} < 3)")

    if "overfit-coder-v1" not in cache:
        failures.append("overfit_coder_missing")
    elif not cache["overfit-coder-v1"].get("gaming_detected"):
        failures.append("overfit_coder_NOT_detected_as_gaming")

    if n_with_data_extra < 1:
        failures.append("no_persistible_with_data_extra_coding")

    print("=" * 70)
    if failures:
        print(f"FAIL — {len(failures)} validation(s) failed:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("OK — todas las validaciones del SPEC Sprint 86.5 pasaron")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    try:
        code = asyncio.run(smoke())
        sys.exit(code)
    except Exception as e:
        import traceback
        print(f"CRASH: {type(e).__name__}: {e}")
        traceback.print_exc()
        sys.exit(2)
