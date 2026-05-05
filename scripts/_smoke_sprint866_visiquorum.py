#!/usr/bin/env python3
"""
Smoke productivo Sprint 86.6 — Visión Quorum 2-de-3 anti-gaming v2 cross-area.

Ejecuta el pipeline E2E con CATASTRO_ENABLE_CODING=true y valida 5 gates:
  G1: Pipeline corre en dry_run con exit 0
  G2: >=1 modelo persistible con data_extra.coding poblado (regresión 86.5)
  G3: Todos los modelos con coding tienen overfit_suspected (bool)
  G4: Todos los modelos con coding tienen overfit_evidence (dict con 3 keys)
  G5: La función detect_overfit_cross_area está integrada al classifier

Uso:
  PYTHONPATH=. python3 scripts/_smoke_sprint866_visiquorum.py

[Hilo Manus Catastro] · Sprint 86.6 · 2026-05-05
"""
from __future__ import annotations

import asyncio
import os
import sys


async def main() -> int:
    os.environ["CATASTRO_ENABLE_CODING"] = "true"
    os.environ["CATASTRO_SKIP_PERSIST"] = "true"

    print("=" * 72)
    print("SMOKE PRODUCTIVO SPRINT 86.6 — Visión Quorum 2-de-3 anti-gaming v2")
    print("=" * 72)

    # G5 (early): verificar contrato
    from kernel.catastro.coding_classifier import (
        CodingClassifier,
        CODING_TAGS_VOCABULARY,
    )

    assert hasattr(CodingClassifier, "detect_overfit_cross_area"), (
        "[FAIL G5] CodingClassifier.detect_overfit_cross_area no existe"
    )
    assert "coding-overfit-suspected" in CODING_TAGS_VOCABULARY, (
        "[FAIL G5] Tag 'coding-overfit-suspected' no está en vocabulario"
    )
    print(f"[OK  G5] Vocabulario: {len(CODING_TAGS_VOCABULARY)} tags · detect_overfit_cross_area presente")

    # G1: pipeline run
    from kernel.catastro.pipeline import CatastroPipeline

    pipeline = CatastroPipeline(dry_run=True)
    result = await pipeline.run()

    if not result.is_success:
        print(f"[FAIL G1] Pipeline degradado: solo {len(result.snapshots)} fuentes")
        return 1
    print(f"[OK  G1] Pipeline run_id={result.run_id} success · {len(result.snapshots)} fuentes")

    # G2: persistibles con coding poblado
    persistibles_con_coding = {
        slug: p for slug, p in result.modelos_persistibles.items()
        if "data_extra" in p and "coding" in p["data_extra"]
    }
    if not persistibles_con_coding:
        print("[FAIL G2] Ningún persistible tiene data_extra.coding poblado")
        return 2
    print(f"[OK  G2] {len(persistibles_con_coding)} persistibles con coding: {list(persistibles_con_coding.keys())}")

    # G3 + G4: overfit_suspected + overfit_evidence
    g3_failures = []
    g4_failures = []
    overfit_detected: list[str] = []

    for slug, p in persistibles_con_coding.items():
        coding = p["data_extra"]["coding"]

        if "overfit_suspected" not in coding or not isinstance(coding["overfit_suspected"], bool):
            g3_failures.append(slug)
        elif coding["overfit_suspected"]:
            overfit_detected.append(slug)

        evidence = coding.get("overfit_evidence")
        if not isinstance(evidence, dict):
            g4_failures.append(slug)
        else:
            required_keys = {"swe_bench", "razonamiento", "arena_rank"}
            if not required_keys.issubset(set(evidence.keys())):
                g4_failures.append(f"{slug} (missing keys: {required_keys - set(evidence.keys())})")

    if g3_failures:
        print(f"[FAIL G3] Persistibles sin overfit_suspected válido: {g3_failures}")
        return 3
    print(f"[OK  G3] Todos los persistibles con coding tienen overfit_suspected (bool)")

    if g4_failures:
        print(f"[FAIL G4] Persistibles sin overfit_evidence válido: {g4_failures}")
        return 4
    print(f"[OK  G4] Todos los persistibles con coding tienen overfit_evidence (dict 3-keys)")

    print("=" * 72)
    print(f"OVERFIT DETECTADOS EN DRY-RUN: {overfit_detected if overfit_detected else 'ninguno (esperado: dry-run sano)'}")
    print(f"5/5 GATES PASSED · Sprint 86.6 production-ready")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
