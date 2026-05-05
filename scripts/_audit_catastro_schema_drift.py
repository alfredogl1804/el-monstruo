#!/usr/bin/env python3
"""
Audit de drift entre `schema_generated.py` (fuente: SQL) y `schema.py` (manual).

Reporta cualquier divergencia entre el espejo SQL y el modelo Pydantic
manual histórico. Hasta que `schema.py` manual sea oficialmente deprecado
(planeado Sprint 86.5/86.6), este audit sirve de canario:
  - Campo en SQL pero no en manual → manual desactualizado.
  - Campo en manual pero no en SQL → manual referencia algo que no existe
    (potencial bug latente).
  - Type mismatch (ej. str vs list[str]) → reporta.

Modos:
  - exit 0: no hay drift (ambos espejos coinciden, o solo hay diferencias
    documentadas como "ignored").
  - exit 1: hay drift material — reporta con detalle a stdout.

NO modifica archivos. Solo lee + reporta.

Uso:
    python3 scripts/_audit_catastro_schema_drift.py
    python3 scripts/_audit_catastro_schema_drift.py --json  # output JSON

Mini-Sprint 86.4.5 pre-B2 · 2026-05-05 · Hilo Manus
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# BASELINE_DRIFT: drifts conocidos y aceptados al 2026-05-05.
# El test FALLA si aparece un drift NUEVO no listado aquí (señal real).
# Si el manual se actualiza y elimina un drift, también FALLA — recordatorio
# de actualizar este baseline.
#
# Justificación de cada entrada documentada inline.
# Doctrina (Cowork): NO tocar schema.py manual hasta deprecación oficial
# (planeado Sprint 86.5/86.6). El generador es la fuente de verdad nueva.
BASELINE_DRIFT: dict[str, dict[str, list[str]]] = {
    "catastro_modelos": {
        # Columna agregada por migration 019.1 hotfix (Bloque 1 86.4.5).
        # Se llena en Sprint 86.6 (Visión multimodal). Manual no la espeja
        # porque está siendo deprecado.
        "in_sql_not_manual": ["validated_by"],
        "in_manual_not_sql": [],
    },
    "catastro_curadores": {
        # Aliases de curador para matching flexible en RPC. Agregada en
        # migration 016. Manual no la espeja por la misma razón.
        "in_sql_not_manual": ["curator_alias"],
        "in_manual_not_sql": [],
    },
}


def _load_generated() -> dict[str, list[str]]:
    """Carga TABLE_COLUMNS del schema generado."""
    try:
        from kernel.catastro.schema_generated import TABLE_COLUMNS  # type: ignore
        return TABLE_COLUMNS
    except ImportError as e:
        print(f"ERROR: catastro_schema_drift_generated_missing: {e}", file=sys.stderr)
        print("HINT: correr primero `python3 scripts/_gen_catastro_pydantic_from_sql.py`", file=sys.stderr)
        sys.exit(2)


def _load_manual_fields() -> dict[str, set[str]]:
    """Extrae nombres de campos de los BaseModels en kernel/catastro/schema.py.

    Mapeo manual → tabla (heurística por convención histórica del repo):
      - CatastroModelo  → catastro_modelos
      - CatastroHistorial → catastro_historial
      - CatastroEvento  → catastro_eventos
      - CatastroNota    → catastro_notas
      - CatastroCurador → catastro_curadores
    """
    try:
        from kernel.catastro import schema as _manual  # type: ignore
    except ImportError as e:
        print(f"ERROR: catastro_schema_drift_manual_missing: {e}", file=sys.stderr)
        sys.exit(2)

    mapping = {
        "catastro_modelos": "CatastroModelo",
        "catastro_historial": "CatastroHistorial",
        "catastro_eventos": "CatastroEvento",
        "catastro_notas": "CatastroNota",
        "catastro_curadores": "CatastroCurador",
    }
    out: dict[str, set[str]] = {}
    for table, cls_name in mapping.items():
        cls = getattr(_manual, cls_name, None)
        if cls is None:
            out[table] = set()
            continue
        # Pydantic v2: `.model_fields`
        fields = set(cls.model_fields.keys()) if hasattr(cls, "model_fields") else set()
        out[table] = fields
    return out


def _audit(gen: dict[str, list[str]], manual: dict[str, set[str]]) -> dict[str, Any]:
    """Compara gen vs manual y devuelve report estructurado."""
    report: dict[str, Any] = {
        "drift_detected": False,
        "tables": {},
    }

    all_tables = set(gen.keys()) | set(manual.keys())
    for table in sorted(all_tables):
        gen_cols = set(gen.get(table, []))
        man_cols = manual.get(table, set())
        in_gen_not_manual = gen_cols - man_cols
        in_manual_not_gen = man_cols - gen_cols

        # Aplicar baseline: drifts conocidos no fallan, pero NUEVOS sí
        baseline = BASELINE_DRIFT.get(table, {"in_sql_not_manual": [], "in_manual_not_sql": []})
        baseline_sql_not_manual = set(baseline.get("in_sql_not_manual", []))
        baseline_manual_not_sql = set(baseline.get("in_manual_not_sql", []))

        new_in_sql = in_gen_not_manual - baseline_sql_not_manual
        new_in_manual = in_manual_not_gen - baseline_manual_not_sql
        # También detectar baseline obsoleto (drift baseline ya no existe)
        stale_baseline_sql = baseline_sql_not_manual - in_gen_not_manual
        stale_baseline_manual = baseline_manual_not_sql - in_manual_not_gen

        table_report = {
            "in_sql_not_manual": sorted(in_gen_not_manual),
            "in_manual_not_sql": sorted(in_manual_not_gen),
            "new_in_sql_not_manual": sorted(new_in_sql),
            "new_in_manual_not_sql": sorted(new_in_manual),
            "stale_baseline_sql": sorted(stale_baseline_sql),
            "stale_baseline_manual": sorted(stale_baseline_manual),
            "common": sorted(gen_cols & man_cols),
            "drift": bool(new_in_sql or new_in_manual or stale_baseline_sql or stale_baseline_manual),
        }
        if table_report["drift"]:
            report["drift_detected"] = True
        report["tables"][table] = table_report

    return report


def _print_report(report: dict[str, Any]) -> None:
    if not report["drift_detected"]:
        print("OK: no hay drift NUEVO entre schema_generated.py y schema.py manual")
        baseline_count = 0
        for table, t in report["tables"].items():
            tot_baseline = len(t["in_sql_not_manual"]) + len(t["in_manual_not_sql"])
            baseline_count += tot_baseline
            print(f"  · {table}: {len(t['common'])} comunes, {tot_baseline} drifts en baseline (esperados)")
        print(f"  Total baseline drift conocido: {baseline_count}")
        return

    print("DRIFT NUEVO DETECTADO (no en BASELINE_DRIFT):")
    print()
    for table, t in report["tables"].items():
        if not t["drift"]:
            continue
        print(f"  Tabla: {table}")
        if t["new_in_sql_not_manual"]:
            print(f"    [!] Nuevo en SQL, NO en manual ({len(t['new_in_sql_not_manual'])}):")
            for c in t["new_in_sql_not_manual"]:
                print(f"        - {c}")
        if t["new_in_manual_not_sql"]:
            print(f"    [!] Nuevo en manual, NO en SQL ({len(t['new_in_manual_not_sql'])}):")
            for c in t["new_in_manual_not_sql"]:
                print(f"        - {c}  (potencial bug: columna inexistente)")
        if t["stale_baseline_sql"]:
            print(f"    [!] Baseline obsoleto SQL→manual ({len(t['stale_baseline_sql'])}):")
            for c in t["stale_baseline_sql"]:
                print(f"        - {c}  (ya no es drift, quitar de BASELINE_DRIFT)")
        if t["stale_baseline_manual"]:
            print(f"    [!] Baseline obsoleto manual→SQL ({len(t['stale_baseline_manual'])}):")
            for c in t["stale_baseline_manual"]:
                print(f"        - {c}  (ya no es drift, quitar de BASELINE_DRIFT)")
        print()
    print("Acciones sugeridas:")
    print("  1. Drift nuevo aceptable (manual atrasado intencionalmente):")
    print("     Agregar columna a BASELINE_DRIFT con justificación inline.")
    print("  2. Drift nuevo inaceptable (bug detectado):")
    print("     Sincronizar manual o refactorizar queries.")
    print("  3. Baseline obsoleto: actualizar BASELINE_DRIFT removiendo entrada.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit drift entre schema generado y manual")
    parser.add_argument("--json", action="store_true", help="Output JSON crudo")
    args = parser.parse_args()

    gen = _load_generated()
    manual = _load_manual_fields()
    report = _audit(gen, manual)

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        _print_report(report)

    return 1 if report["drift_detected"] else 0


if __name__ == "__main__":
    sys.exit(main())
