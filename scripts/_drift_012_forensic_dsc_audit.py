"""
DRIFT-012 forensic audit: identificar DSCs missing en _INDEX.md vs físicos en disco.

Tipo A — DSCs declarados en _INDEX.md pero sin archivo físico:
    DSC-LT-001, DSC-LT-003, DSC-MO-001, DSC-MO-003, DSC-MO-004, DSC-X-003

Tipo B — DSCs físicos sin entrada en _INDEX.md (deuda inversa):
    DSC-G-009/012/014/017, DSC-MO-006..011, DSC-OPS-001, DSC-S-006..016

Para Tipo A: buscar en git log si alguna vez existieron en un commit pasado
y fueron eliminados/movidos.

Para Tipo B: identificar qué archivos físicos faltan en _INDEX.md para que
una próxima migración lo actualice.

Output: reporte JSON estructurado.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CAPILLA_DIR = REPO_ROOT / "discovery_forense" / "CAPILLA_DECISIONES"

TIPO_A_MISSING = [
    "DSC-LT-001",
    "DSC-LT-003",
    "DSC-MO-001",
    "DSC-MO-003",
    "DSC-MO-004",
    "DSC-X-003",
]

TIPO_B_NO_INDEX = [
    "DSC-G-009",
    "DSC-G-012",
    "DSC-G-014",
    "DSC-G-017",
    "DSC-MO-006",
    "DSC-MO-007",
    "DSC-MO-008",
    "DSC-MO-009",
    "DSC-MO-010",
    "DSC-MO-011",
    "DSC-OPS-001",
    "DSC-S-006",
    "DSC-S-007",
    "DSC-S-008",
    "DSC-S-010",
    "DSC-S-011",
    "DSC-S-012",
    "DSC-S-013",
    "DSC-S-015",
    "DSC-S-016",
]


def git_log_for_dsc(dsc_code: str) -> dict:
    """Busca en git log si el DSC alguna vez existió como archivo, fue movido o eliminado."""
    # Buscar archivos que contengan el código en su nombre, con --diff-filter=A,D,R
    try:
        # 1. ¿Algún commit creó un archivo con ese nombre?
        result = subprocess.run(
            [
                "git",
                "log",
                "--all",
                "--diff-filter=AD",
                "--name-status",
                "--",
                f"discovery_forense/CAPILLA_DECISIONES/**/{dsc_code}_*.md",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
        log_output = result.stdout.strip()
        # 2. Buscar referencias al código con --all
        ref_search = subprocess.run(
            [
                "git",
                "log",
                "--all",
                "--source",
                "-S",
                f"{dsc_code}_",
                "--oneline",
                "--",
                "discovery_forense/CAPILLA_DECISIONES/",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
        # 3. Buscar archivos eliminados que matchean
        deleted = subprocess.run(
            ["git", "log", "--all", "--diff-filter=D", "--summary"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
        )
        deleted_lines = [ln for ln in deleted.stdout.splitlines() if dsc_code in ln and "delete mode" in ln]

        return {
            "dsc": dsc_code,
            "found_in_history": bool(log_output) or bool(deleted_lines),
            "git_log_AD": log_output[:1000],
            "ref_search_oneline": ref_search.stdout[:500],
            "deleted_files": deleted_lines[:5],
        }
    except subprocess.TimeoutExpired:
        return {"dsc": dsc_code, "error": "timeout"}
    except Exception as e:
        return {"dsc": dsc_code, "error": str(e)[:200]}


def map_tipo_b_files() -> dict:
    """Para Tipo B, ubicar el archivo físico de cada código."""
    mapping = {}
    for code in TIPO_B_NO_INDEX:
        files = list(CAPILLA_DIR.rglob(f"{code}_*.md"))
        mapping[code] = [str(f.relative_to(REPO_ROOT)) for f in files]
    return mapping


def main() -> int:
    print("=" * 72)
    print("DRIFT-012 — Forensic audit DSCs missing")
    print("=" * 72)

    # Tipo A: forensic git log
    print("\n## TIPO A — Declarados en _INDEX.md pero SIN archivo físico\n")
    tipo_a_results = []
    for dsc in TIPO_A_MISSING:
        r = git_log_for_dsc(dsc)
        tipo_a_results.append(r)
        print(f"\n{dsc}:")
        print(f"  found_in_history={r.get('found_in_history')}")
        if r.get("deleted_files"):
            for ln in r["deleted_files"]:
                print(f"    deleted: {ln.strip()}")
        if r.get("git_log_AD"):
            for ln in r["git_log_AD"].splitlines()[:3]:
                print(f"    log: {ln}")

    # Tipo B: file mapping
    print("\n" + "=" * 72)
    print("## TIPO B — Físicos sin entrada en _INDEX.md (deuda inversa)\n")
    tipo_b = map_tipo_b_files()
    for code, files in tipo_b.items():
        print(f"  {code:15s} → {files[0] if files else '(NO ENCONTRADO)'}")

    # Output JSON
    out_path = REPO_ROOT / "bridge" / "DRIFT_012_FORENSIC_DSC_AUDIT_2026_05_12.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "tipo_a_index_sin_fisico": tipo_a_results,
                "tipo_b_fisico_sin_index": tipo_b,
                "summary": {
                    "tipo_a_count": len(TIPO_A_MISSING),
                    "tipo_b_count": len(TIPO_B_NO_INDEX),
                    "fisicos_total": len(list(CAPILLA_DIR.rglob("DSC-*.md"))),
                    "fisicos_codigos_unicos": 56,
                    "index_codigos_unicos": 42,
                },
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"\n[VERDE] reporte JSON: {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
