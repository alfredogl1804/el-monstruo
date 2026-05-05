#!/usr/bin/env python3
"""
Smoke productivo Sprint 86.8 - Confidentiality Tier filter en RecommendationEngine.

6 gates:
  G1: Imports correctos + constantes coherentes
  G2: Migration 027 SQL existe + check constraint con 4 tiers
  G3: Asignacion inicial conservadora SQL existe
  G4: Schema_generated.py incluye confidentiality_tier
  G5: Engine.recommend con tier filter funciona E2E (mock DB)
  G6: raise_on_no_eligible_tier semantica funciona

Exit 0 = todos los gates verdes.
Exit 1 = al menos un gate falla.

[Hilo Manus Catastro] · Sprint 86.8 Bloque 4 · 2026-05-05
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _gate(num: int, name: str, ok: bool, detail: str = "") -> bool:
    icon = "OK" if ok else "FAIL"
    print(f"  G{num} [{icon}] {name}{(' - ' + detail) if detail else ''}")
    return ok


def main() -> int:
    print("=" * 72)
    print("Smoke productivo Sprint 86.8 - Confidentiality Tier")
    print("=" * 72)
    t0 = time.time()
    gates_ok = []

    # ------------------------------------------------------------------------
    # G1: Imports + constantes
    # ------------------------------------------------------------------------
    try:
        from kernel.catastro.recommendation import (
            CONFIDENTIALITY_TIER_RANK,
            DEFAULT_MIN_TIER_REQUIRED,
            VALID_CONFIDENTIALITY_TIERS,
            CatastroChooseModelNoEligibleTier,
            CatastroRecommendInvalidArgs,
            ModeloRecomendado,
            RecommendationEngine,
        )
        coherent = (
            CONFIDENTIALITY_TIER_RANK["local_only"] == 0
            and CONFIDENTIALITY_TIER_RANK["cloud_only"] == 3
            and DEFAULT_MIN_TIER_REQUIRED == "cloud_only"
            and len(VALID_CONFIDENTIALITY_TIERS) == 4
        )
        gates_ok.append(_gate(
            1, "Imports + constantes coherentes",
            coherent, f"4 tiers, default={DEFAULT_MIN_TIER_REQUIRED}",
        ))
    except Exception as e:
        gates_ok.append(_gate(1, "Imports + constantes coherentes", False, str(e)))
        return 1

    # ------------------------------------------------------------------------
    # G2: Migration 027 SQL
    # ------------------------------------------------------------------------
    sql_path = REPO_ROOT / "scripts" / "027_sprint86_8_confidentiality_tier_schema.sql"
    if sql_path.exists():
        sql = sql_path.read_text()
        all_tiers_in_check = all(
            f"'{t}'" in sql
            for t in ["local_only", "tee_capable", "cloud_anonymized_ok", "cloud_only"]
        )
        idempotent = "ADD COLUMN IF NOT EXISTS confidentiality_tier" in sql
        gates_ok.append(_gate(
            2, "Migration 027 SQL coherente",
            all_tiers_in_check and idempotent,
            "4 tiers en CHECK, idempotente",
        ))
    else:
        gates_ok.append(_gate(2, "Migration 027 SQL existe", False, "archivo no encontrado"))

    # ------------------------------------------------------------------------
    # G3: Asignacion inicial conservadora
    # ------------------------------------------------------------------------
    assign_path = REPO_ROOT / "scripts" / "027_sprint86_8_assign_confidentiality_tiers.sql"
    gates_ok.append(_gate(
        3, "Asignacion inicial conservadora SQL existe",
        assign_path.exists(),
        f"size={assign_path.stat().st_size if assign_path.exists() else 0} bytes",
    ))

    # ------------------------------------------------------------------------
    # G4: schema_generated.py incluye confidentiality_tier
    # ------------------------------------------------------------------------
    schema_gen_path = REPO_ROOT / "kernel" / "catastro" / "schema_generated.py"
    schema_gen_text = schema_gen_path.read_text()
    has_field = (
        "confidentiality_tier" in schema_gen_text
        and "'confidentiality_tier'" in schema_gen_text
    )
    gates_ok.append(_gate(
        4, "schema_generated.py incluye confidentiality_tier",
        has_field, "regenerado tras migration 027",
    ))

    # ------------------------------------------------------------------------
    # G5: Engine.recommend con tier filter E2E (mock DB)
    # ------------------------------------------------------------------------
    class _ChainStub:
        def __init__(self, rows): self._rows = rows
        def select(self, *a, **kw): return self
        def eq(self, *a, **kw): return self
        def order(self, *a, **kw): return self
        def limit(self, *a, **kw): return self

        class _Result:
            def __init__(self, rows): self.data = rows

        def execute(self):
            return self._Result(self._rows)

    class _ClientStub:
        def __init__(self, rows): self._rows = rows
        def table(self, *a, **kw): return _ChainStub(self._rows)

    rows = [
        {
            "id": "llama-7b-local", "nombre": "Llama 7B local",
            "proveedor": "meta", "macroarea": "general",
            "dominio": "general", "estado": "production",
            "trono_global": 70.0, "trono_low": 65.0, "trono_high": 75.0,
            "rank_dominio": 3, "confidentiality_tier": "local_only",
        },
        {
            "id": "claude-tee", "nombre": "Claude TEE",
            "proveedor": "anthropic", "macroarea": "general",
            "dominio": "general", "estado": "production",
            "trono_global": 90.0, "trono_low": 85.0, "trono_high": 95.0,
            "rank_dominio": 1, "confidentiality_tier": "tee_capable",
        },
        {
            "id": "gpt-anon", "nombre": "GPT Anonymized",
            "proveedor": "openai", "macroarea": "general",
            "dominio": "general", "estado": "production",
            "trono_global": 85.0, "trono_low": 80.0, "trono_high": 90.0,
            "rank_dominio": 2, "confidentiality_tier": "cloud_anonymized_ok",
        },
        {
            "id": "hf-raw", "nombre": "HF raw",
            "proveedor": "huggingface", "macroarea": "general",
            "dominio": "general", "estado": "production",
            "trono_global": 80.0, "trono_low": 75.0, "trono_high": 85.0,
            "rank_dominio": 4, "confidentiality_tier": "cloud_only",
        },
    ]

    engine = RecommendationEngine(db_factory=lambda: _ClientStub(rows))

    # Test: cloud_anonymized_ok debe descartar hf-raw pero quedarse con los otros 3
    res_anon = engine.recommend(
        use_case="legal contract review",
        min_tier_required="cloud_anonymized_ok",
        top_n=10,
    )
    ids = {m.id for m in res_anon.modelos}
    expected = {"llama-7b-local", "claude-tee", "gpt-anon"}
    e2e_ok = (
        not res_anon.degraded
        and ids == expected
        and "hf-raw" not in ids
    )
    gates_ok.append(_gate(
        5, "Engine.recommend tier filter E2E",
        e2e_ok,
        f"min=cloud_anonymized_ok, ids={sorted(ids)}",
    ))

    # ------------------------------------------------------------------------
    # G6: raise_on_no_eligible_tier semantica
    # ------------------------------------------------------------------------
    only_cloud_engine = RecommendationEngine(
        db_factory=lambda: _ClientStub([rows[3]]),  # solo hf-raw
    )
    raised = False
    try:
        only_cloud_engine.recommend(
            use_case="legal", min_tier_required="local_only",
            raise_on_no_eligible_tier=True,
        )
    except CatastroChooseModelNoEligibleTier as e:
        raised = e.code == "catastro_choose_model_no_eligible_tier"
    gates_ok.append(_gate(
        6, "raise_on_no_eligible_tier funciona",
        raised, "Brand DNA: catastro_choose_model_no_eligible_tier",
    ))

    # ------------------------------------------------------------------------
    elapsed = time.time() - t0
    passed = sum(1 for g in gates_ok if g)
    total = len(gates_ok)
    print("=" * 72)
    print(f"Resultado: {passed}/{total} gates verdes  |  Tiempo: {elapsed:.2f}s")
    print("=" * 72)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
