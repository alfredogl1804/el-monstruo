#!/usr/bin/env python3
"""
Smoke test del Sprint 86 Bloque 4 — Trono Score Calculator.

Valida sin tocar Supabase:
  - Construcción de TronoCalculator con pesos default y custom.
  - compute_for_domain con 3+ modelos (modo z_score).
  - compute_for_domain con 1 modelo (modo neutral).
  - compute_all sobre múltiples dominios.
  - Bandas de confianza correctas (trono_low <= trono_new <= trono_high).
  - apply_results_to_models actualiza in-place.
  - Manejo de pesos inválidos (catastro_trono_invalid_weights).

Uso:
  python3 scripts/_smoke_trono_sprint86.py

[Hilo Manus Catastro] · Sprint 86 Bloque 4 · 2026-05-04
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import asyncio  # noqa: E402
import os  # noqa: E402

from kernel.catastro.schema import CatastroModelo  # noqa: E402
from kernel.catastro.pipeline import CatastroPipeline  # noqa: E402
from kernel.catastro.trono import (  # noqa: E402
    DEFAULT_WEIGHTS,
    METRIC_FIELDS,
    CatastroTronoInvalidWeights,
    TronoCalculator,
    apply_results_to_models,
)


def header(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def smoke_z_score_mode() -> None:
    header("1. compute_for_domain — modo z_score (3 modelos)")
    calc = TronoCalculator()
    modelos = [
        CatastroModelo(
            id="model-alpha", nombre="Alpha", proveedor="anthropic",
            dominios=["llm_frontier"],
            quality_score=90.0, cost_efficiency=80.0, speed_score=70.0,
            reliability_score=95.0, brand_fit=0.9, confidence=0.85,
        ),
        CatastroModelo(
            id="model-beta", nombre="Beta", proveedor="openai",
            dominios=["llm_frontier"],
            quality_score=70.0, cost_efficiency=90.0, speed_score=85.0,
            reliability_score=80.0, brand_fit=0.5, confidence=0.70,
        ),
        CatastroModelo(
            id="model-gamma", nombre="Gamma", proveedor="google",
            dominios=["llm_frontier"],
            quality_score=80.0, cost_efficiency=60.0, speed_score=75.0,
            reliability_score=88.0, brand_fit=0.7, confidence=0.60,
        ),
    ]
    results = calc.compute_for_domain(modelos, "llm_frontier")
    for r in results:
        print(f"  {r.modelo_id}: trono={r.trono_new} delta={r.trono_delta} "
              f"band=[{r.trono_low},{r.trono_high}] mode={r.mode}")
        # Sanity: low <= new <= high
        assert r.trono_low <= r.trono_new <= r.trono_high, "banda invertida"
        assert r.mode == "z_score"
    # Promedio cercano a 50 (base) para n=3
    avg = sum(r.trono_new for r in results) / len(results)
    print(f"  promedio: {avg:.2f} (esperado ≈ 50)")
    assert 40.0 <= avg <= 60.0, f"promedio {avg} fuera de banda esperada"
    print("  OK")


def smoke_neutral_mode() -> None:
    header("2. compute_for_domain — modo neutral (1 modelo)")
    calc = TronoCalculator()
    modelos = [
        CatastroModelo(
            id="lonely-model", nombre="Solo", proveedor="x",
            dominios=["coding_llms"],
            quality_score=75.0, cost_efficiency=70.0, speed_score=80.0,
            reliability_score=90.0, brand_fit=0.8, confidence=0.50,
        ),
    ]
    results = calc.compute_for_domain(modelos, "coding_llms")
    assert len(results) == 1
    r = results[0]
    print(f"  {r.modelo_id}: trono={r.trono_new} mode={r.mode} warnings={r.warnings}")
    assert r.trono_new == 50.0
    assert r.mode == "neutral"
    assert "menos_de_2_modelos" in r.warnings
    print("  OK")


def smoke_compute_all() -> None:
    header("3. compute_all — múltiples dominios")
    calc = TronoCalculator()
    modelos = [
        CatastroModelo(id=f"model-front-{i}", nombre=f"F{i}", proveedor="x",
                       dominios=["llm_frontier"],
                       quality_score=70 + i * 5, cost_efficiency=80,
                       speed_score=75, reliability_score=90, brand_fit=0.7)
        for i in range(3)
    ] + [
        CatastroModelo(id=f"model-code-{i}", nombre=f"C{i}", proveedor="y",
                       dominios=["coding_llms"],
                       quality_score=60 + i * 10, cost_efficiency=70,
                       speed_score=80, reliability_score=85, brand_fit=0.6)
        for i in range(2)
    ]
    by_dominio = calc.compute_all(modelos)
    for dom, results in by_dominio.items():
        print(f"  {dom}: {len(results)} modelos, "
              f"trono_avg={sum(r.trono_new for r in results)/len(results):.2f}")
    assert "llm_frontier" in by_dominio
    assert "coding_llms" in by_dominio
    assert len(by_dominio["llm_frontier"]) == 3
    assert len(by_dominio["coding_llms"]) == 2
    print("  OK")


def smoke_apply_results() -> None:
    header("4. apply_results_to_models — actualización in-place")
    calc = TronoCalculator()
    modelos = [
        CatastroModelo(id=f"apply-{i}", nombre=f"M{i}", proveedor="x",
                       dominios=["llm_frontier"],
                       quality_score=70 + i * 10, cost_efficiency=80,
                       speed_score=75, reliability_score=90, brand_fit=0.7)
        for i in range(3)
    ]
    # Inicialmente trono_global = None
    assert all(m.trono_global is None for m in modelos)
    results = calc.compute_for_domain(modelos, "llm_frontier")
    n = apply_results_to_models(modelos, results)
    print(f"  modelos actualizados: {n}")
    for m in modelos:
        print(f"  {m.id}: trono_global={m.trono_global} delta={m.trono_delta}")
        assert m.trono_global is not None
    assert n == 3
    print("  OK")


def smoke_invalid_weights() -> None:
    header("5. Validación de pesos inválidos")
    # Pesos que NO suman 1.0
    try:
        TronoCalculator(weights={
            "quality_score": 0.5, "cost_efficiency": 0.3,
            "speed_score": 0.1, "reliability_score": 0.05, "brand_fit": 0.0,
        })
        raise AssertionError("Debió haber lanzado CatastroTronoInvalidWeights")
    except CatastroTronoInvalidWeights as e:
        print(f"  OK: {e.code} = {e}")

    # Pesos faltantes
    try:
        TronoCalculator(weights={"quality_score": 1.0})
        raise AssertionError("Debió haber lanzado CatastroTronoInvalidWeights")
    except CatastroTronoInvalidWeights as e:
        print(f"  OK: {e.code} = {e}")
    print("  OK")


def smoke_pipeline_integration() -> None:
    header("6. Pipeline integration — trono + persist + skip_persist")
    # Limpiar env vars que podrían interferir
    for k in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY",
              "CATASTRO_SKIP_PERSIST"):
        os.environ.pop(k, None)

    # 6a. Pipeline en dry_run sin skip_persist → trono se calcula y persist es dry
    pipe = CatastroPipeline(dry_run=True, skip_persist=False)
    result = asyncio.run(pipe.run())
    summary = result.summary()
    print(f"  6a (no skip): persistibles={summary['modelos_persistibles']} "
          f"trono_dominios={summary['trono_summary']['dominios']} "
          f"persist_skipped={summary['persist_summary']['skipped']}")
    assert summary["persist_summary"]["skipped"] is False
    assert "failure_rate_observed" in summary["persist_summary"]
    assert "error_categories" in summary["persist_summary"]
    if summary["modelos_persistibles"] > 0:
        assert summary["trono_summary"]["dominios"] >= 1
        assert summary["trono_summary"]["modelos_calculados"] >= 1

    # 6b. Pipeline en dry_run CON skip_persist → ni siquiera dry-run de persist
    pipe2 = CatastroPipeline(dry_run=True, skip_persist=True)
    result2 = asyncio.run(pipe2.run())
    summary2 = result2.summary()
    print(f"  6b (skip):    persistibles={summary2['modelos_persistibles']} "
          f"trono_dominios={summary2['trono_summary']['dominios']} "
          f"persist_skipped={summary2['persist_summary']['skipped']}")
    assert summary2["persist_summary"]["skipped"] is True
    assert result2.persist_results == []
    # Trono SI debe haberse calculado aunque persist se omita
    if summary2["modelos_persistibles"] > 0:
        assert summary2["trono_summary"]["dominios"] >= 1

    # 6c. Pipeline lee CATASTRO_SKIP_PERSIST=true del env
    os.environ["CATASTRO_SKIP_PERSIST"] = "true"
    pipe3 = CatastroPipeline(dry_run=True)  # sin pasar skip_persist
    assert pipe3.skip_persist is True, "env CATASTRO_SKIP_PERSIST no respetado"
    os.environ.pop("CATASTRO_SKIP_PERSIST")
    print(f"  6c (env):     skip_persist leído correctamente desde env var")
    print("  OK")


def main() -> int:
    print(f"\n[Catastro] Smoke test Sprint 86 Bloque 4 — TronoCalculator\n")
    print(f"  pesos default: {DEFAULT_WEIGHTS}")
    print(f"  Σ pesos: {sum(DEFAULT_WEIGHTS.values())}")
    print(f"  métricas: {METRIC_FIELDS}")
    try:
        smoke_z_score_mode()
        smoke_neutral_mode()
        smoke_compute_all()
        smoke_apply_results()
        smoke_invalid_weights()
        smoke_pipeline_integration()
    except AssertionError as e:
        print(f"\n[FAIL] AssertionError: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"\n[FAIL] {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    print("\n[OK] Smoke test del Bloque 4 PASS\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
