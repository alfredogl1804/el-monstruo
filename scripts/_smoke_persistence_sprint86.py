#!/usr/bin/env python3
"""
Smoke test del Sprint 86 Bloque 3 — Persistencia atómica.

Ejecuta:
  - Construcción de CatastroPersistence en modo dry_run
  - persist() de un modelo de ejemplo con evento + deltas
  - Verifica que rpc_params_preview tiene la forma correcta
  - persist_many con 3 modelos
  - Pipeline completo en dry_run con persistence inyectada

Uso:
  python3 scripts/_smoke_persistence_sprint86.py

[Hilo Manus Catastro] · Sprint 86 Bloque 3 · 2026-05-04
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Ensure repo root is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kernel.catastro import (  # noqa: E402
    CatastroEvento,
    CatastroModelo,
    CatastroPersistence,
    CatastroPipeline,
    PrioridadEvento,
    TipoEvento,
    __version__,
)


def header(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def smoke_dry_run_basic() -> None:
    header("1. Persist single (dry_run)")
    p = CatastroPersistence(dry_run=True)
    modelo = CatastroModelo(
        id="gpt-5-5-mini",
        nombre="GPT-5.5 Mini",
        proveedor="openai",
        dominios=["llm_frontier"],
        quality_score=87.4,
        precio_input_per_million=0.35,
        precio_output_per_million=1.10,
    )
    evento = CatastroEvento(
        tipo=TipoEvento.NEW_MODEL,
        prioridad=PrioridadEvento.IMPORTANTE,
        modelo_id=modelo.id,
        descripcion="Smoke test del Bloque 3",
    )
    deltas = {
        "artificial_analysis": 0.0,
        "openrouter": 0.0,
        "lmarena": -0.05,
    }
    result = p.persist(modelo=modelo, evento=evento, trust_deltas=deltas)
    print(f"  success={result.success} dry_run={result.dry_run} modelo_id={result.modelo_id}")
    assert result.success and result.dry_run
    print("  RPC params preview keys:", sorted(result.rpc_params_preview.keys()))
    assert set(result.rpc_params_preview.keys()) == {"p_modelo", "p_evento", "p_trust_deltas"}
    print("  OK")


def smoke_persist_many() -> None:
    header("2. persist_many (dry_run, 3 modelos)")
    p = CatastroPersistence(dry_run=True)
    items = [
        {
            "modelo": CatastroModelo(
                id=f"smoke-model-{i}",
                nombre=f"Smoke {i}",
                proveedor="smoke",
                dominios=["llm_frontier"],
            )
        }
        for i in range(3)
    ]
    results = p.persist_many(items)
    for r in results:
        print(f"  - {r.modelo_id}: success={r.success} dry={r.dry_run}")
    assert len(results) == 3 and all(r.success for r in results)
    print("  OK")


def smoke_pipeline_with_persistence() -> None:
    header("3. Pipeline end-to-end (dry_run)")
    pipeline = CatastroPipeline(dry_run=True)
    result = asyncio.run(pipeline.run())
    summary = result.summary()
    print(json.dumps(summary, indent=2, default=str))
    assert isinstance(result.persist_results, list)
    print(f"  persistibles={len(result.modelos_persistibles)} persist_results={len(result.persist_results)}")
    print("  OK")


def main() -> int:
    print(f"\n[Catastro v{__version__}] Smoke test Sprint 86 Bloque 3\n")
    try:
        smoke_dry_run_basic()
        smoke_persist_many()
        smoke_pipeline_with_persistence()
    except AssertionError as e:
        print(f"\n[FAIL] AssertionError: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"\n[FAIL] {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    print("\n[OK] Smoke test del Bloque 3 PASS\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
