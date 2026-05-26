#!/usr/bin/env python3
"""Genera reports/dsc_contract_check_hook_test.json como evidencia CA6 del Sprint TRANSVERSAL-001.

Ejecuta el test sintetico descrito en el kickoff:
    1. DSC sin entry en _dsc_contracts_index.yaml + sin contrato adjunto → debe FALLAR (exit 1)
    2. DSC con seccion '## Contrato ejecutable' + rutas existentes → debe PASAR (exit 0)
    3. DSC marcado aspiracional → debe PASAR con warn (exit 0)
    4. Archivo inexistente → debe ser error de uso (exit 2)

Output:
    reports/dsc_contract_check_hook_test.json — JSON con 4 cases + verdict global.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK_TOOL = REPO_ROOT / "tools" / "dsc_contract_check.py"
REPORT_PATH = REPO_ROOT / "reports" / "dsc_contract_check_hook_test.json"

DSC_INVALID = """\
# DSC-X-CA6-EVIDENCE-INVALID — Sin contrato

**Estado:** Firmado

## Decision

Texto sin contrato adjunto. Debe bloquear commit.
"""

DSC_VALID = """\
# DSC-X-CA6-EVIDENCE-VALID — Con contrato

**Estado:** Firmado

## Decision

Decision firmada.

## Contrato ejecutable

| Artefacto | Ruta | Enforza |
|---|---|---|
| Linter | `tools/spec_lint.py` | Lintea specs. |
| Tests | `tests/test_spec_lint.py` | Cubre el linter. |
"""

DSC_ASPIRATIONAL = """\
# DSC-X-CA6-EVIDENCE-ASPI — Aspiracional

**Estado:** Aspiracional

## Decision

Sin enforcement todavia.
"""


def run_hook(dsc_path: Path) -> dict:
    cmd = [
        sys.executable,
        str(HOOK_TOOL),
        "--repo-root",
        str(REPO_ROOT),
        str(dsc_path),
    ]
    t0 = time.time()
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )
    return {
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "duration_ms": round((time.time() - t0) * 1000, 1),
    }


def write_named(content: str, name: str) -> Path:
    p = Path(tempfile.gettempdir()) / name
    p.write_text(content, encoding="utf-8")
    return p


def main() -> int:
    cases = []

    # Case 1: DSC invalido → exit 1 (BLOCKED)
    p = write_named(DSC_INVALID, "DSC-X-CA6-EV-INVALID.md")
    try:
        result = run_hook(p)
        cases.append(
            {
                "case": "invalid_dsc_no_contract",
                "input": str(p.name),
                "expected_exit": 1,
                "expected_behavior": "BLOCKED (hook rechaza commit)",
                "actual": result,
                "verdict": "PASS" if result["exit_code"] == 1 else "FAIL",
            }
        )
    finally:
        p.unlink(missing_ok=True)

    # Case 2: DSC valido → exit 0 (PASSED)
    p = write_named(DSC_VALID, "DSC-X-CA6-EV-VALID.md")
    try:
        result = run_hook(p)
        cases.append(
            {
                "case": "valid_dsc_with_contract",
                "input": str(p.name),
                "expected_exit": 0,
                "expected_behavior": "PASSED (hook permite commit)",
                "actual": result,
                "verdict": "PASS" if result["exit_code"] == 0 else "FAIL",
            }
        )
    finally:
        p.unlink(missing_ok=True)

    # Case 3: DSC aspiracional → exit 0 (PASSED con warn)
    p = write_named(DSC_ASPIRATIONAL, "DSC-X-CA6-EV-ASPI.md")
    try:
        result = run_hook(p)
        cases.append(
            {
                "case": "aspirational_dsc",
                "input": str(p.name),
                "expected_exit": 0,
                "expected_behavior": "PASSED con [warn] (aspiracional explicito)",
                "actual": result,
                "verdict": "PASS" if result["exit_code"] == 0 else "FAIL",
            }
        )
    finally:
        p.unlink(missing_ok=True)

    # Case 4: archivo inexistente → exit 2 (error uso)
    fake = REPO_ROOT / "DSC-X-CA6-EV-NOEXIST.md"
    result = run_hook(fake)
    cases.append(
        {
            "case": "missing_file_usage_error",
            "input": str(fake.name),
            "expected_exit": 2,
            "expected_behavior": "ERROR DE USO (archivo no existe)",
            "actual": result,
            "verdict": "PASS" if result["exit_code"] == 2 else "FAIL",
        }
    )

    verdicts = [c["verdict"] for c in cases]
    global_verdict = "PASS" if all(v == "PASS" for v in verdicts) else "FAIL"

    report = {
        "sprint": "TRANSVERSAL-001",
        "task": "T8",
        "criterio_aceptacion": "CA6",
        "criterio_descripcion": "dsc_contract_check activo como hook bloqueante",
        "hook_id": "dsc-contract-check",
        "hook_entry": "python3 tools/dsc_contract_check.py",
        "hook_files_regex": "^discovery_forense/CAPILLA_DECISIONES/.*\\.md$",
        "tool_path": "tools/dsc_contract_check.py",
        "pre_commit_config": ".pre-commit-config.yaml",
        "cases": cases,
        "verdicts": {c["case"]: c["verdict"] for c in cases},
        "global_verdict": global_verdict,
        "generated_by": "scripts/_dsc_contract_check_hook_test.py",
        "generated_at_unix": time.time(),
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[ok] reporte escrito: {REPORT_PATH.relative_to(REPO_ROOT)}")
    print(f"[ok] global_verdict: {global_verdict}")
    return 0 if global_verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
