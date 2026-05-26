# tests/test_dsc_contract_check.py
"""
Tests del verificador de contrato ejecutable (DSC-G-017).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.dsc_contract_check as dcc  # noqa: E402

DSC_VALID_WITH_EXISTING_PATH = """\
# DSC-X-001 — Mi DSC con contrato real

**Estado:** Firmado

## Decision

Algo importante.

## Contrato ejecutable

| Artefacto | Ruta | Enforza |
|---|---|---|
| Linter | `tools/spec_lint.py` | Lintea specs de sprint. |
| Tests | `tests/test_spec_lint.py` | Cubre el linter. |
"""

DSC_VALID_ASPIRATIONAL = """\
# DSC-X-002 — Mi DSC aspiracional

**Estado:** Aspiracional

## Decision

Algo todavia sin enforzamiento.
"""

DSC_INVALID_NO_SECTION = """\
# DSC-X-003 — Mi DSC roto

**Estado:** Firmado

## Decision

Texto sin contrato adjunto. Esto deberia bloquear el commit.
"""

DSC_INVALID_PATHS_DONT_EXIST = """\
# DSC-X-004 — Contrato fantasma

**Estado:** Firmado

## Contrato ejecutable

- Linter: `tools/no_existe_este_archivo.py`
- Tests: `tests/test_tampoco_existe.py`
"""


def _write_tmp(content: str, prefix: str = "DSC-TEST") -> Path:
    f = tempfile.NamedTemporaryFile(
        "w",
        prefix=prefix + "-",
        suffix=".md",
        delete=False,
        encoding="utf-8",
    )
    f.write(content)
    f.close()
    return Path(f.name)


def test_valid_dsc_with_existing_path():
    p = _write_tmp(DSC_VALID_WITH_EXISTING_PATH, prefix="DSC-X-001")
    res = dcc.check_dsc(p, ROOT)
    print(f"[valid] passed={res.passed} found={res.paths_found} missing={res.paths_missing}")
    assert res.passed, f"DSC con contrato y rutas existentes debe pasar. reason={res.reason}"
    assert "tools/spec_lint.py" in res.paths_found
    assert "tests/test_spec_lint.py" in res.paths_found


def test_valid_aspirational():
    p = _write_tmp(DSC_VALID_ASPIRATIONAL, prefix="DSC-X-002")
    res = dcc.check_dsc(p, ROOT)
    print(f"[aspiracional] passed={res.passed} is_aspirational={res.is_aspirational}")
    assert res.passed
    assert res.is_aspirational


def test_invalid_no_section():
    p = _write_tmp(DSC_INVALID_NO_SECTION, prefix="DSC-X-003")
    res = dcc.check_dsc(p, ROOT)
    print(f"[no_section] passed={res.passed} reason={res.reason}")
    assert not res.passed
    assert not res.has_contract_section


def test_invalid_paths_dont_exist():
    p = _write_tmp(DSC_INVALID_PATHS_DONT_EXIST, prefix="DSC-X-004")
    res = dcc.check_dsc(p, ROOT)
    print(f"[ghost_paths] passed={res.passed} missing={res.paths_missing}")
    assert not res.passed
    assert res.has_contract_section
    assert len(res.paths_missing) >= 1
    assert len(res.paths_found) == 0


# ───────────────────────────────────────────────────────────────────────
# Sprint TRANSVERSAL-001 T8 (CA6): tests del comportamiento BLOQUEANTE del
# hook dsc-contract-check via CLI (main()). Los 4 tests previos cubren la
# funcion check_dsc() pura; estos cubren el contrato pre-commit real.
# ───────────────────────────────────────────────────────────────────────
import os
import subprocess


def _run_cli(*paths: Path) -> tuple[int, str, str]:
    """Invoca tools/dsc_contract_check.py como subprocess (igual que pre-commit)."""
    cmd = [
        sys.executable,
        str(ROOT / "tools" / "dsc_contract_check.py"),
        "--repo-root",
        str(ROOT),
        *[str(p) for p in paths],
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    return proc.returncode, proc.stdout, proc.stderr


def _write_named(content: str, name: str) -> Path:
    """Escribe contenido con nombre DSC-* explicito para que pase el filtro de main()."""
    p = Path(tempfile.gettempdir()) / name
    p.write_text(content, encoding="utf-8")
    return p


def test_cli_blocks_invalid_dsc_exit_1():
    """CA6: DSC sin contrato + sin marcador aspiracional → exit 1 (bloquea commit)."""
    p = _write_named(DSC_INVALID_NO_SECTION, "DSC-X-CA6-1.md")
    try:
        code, out, err = _run_cli(p)
        print(f"[cli_blocks_invalid] code={code} stderr={err[:200]}")
        assert code == 1, f"DSC invalido debe exit 1 (got {code}). stderr={err}"
        assert "DSC-G-017" in err or "violan" in err
    finally:
        p.unlink(missing_ok=True)


def test_cli_passes_valid_dsc_exit_0():
    """CA6: DSC con contrato ejecutable + rutas existentes → exit 0 (permite commit)."""
    p = _write_named(DSC_VALID_WITH_EXISTING_PATH, "DSC-X-CA6-2.md")
    try:
        code, out, err = _run_cli(p)
        print(f"[cli_passes_valid] code={code} stdout={out[:200]}")
        assert code == 0, f"DSC valido debe exit 0 (got {code}). stderr={err}"
        assert "[ok]" in out
    finally:
        p.unlink(missing_ok=True)


def test_cli_passes_aspirational_exit_0_with_warn():
    """CA6: DSC marcado aspiracional → exit 0 con [warn] (permite commit pero advierte)."""
    p = _write_named(DSC_VALID_ASPIRATIONAL, "DSC-X-CA6-3.md")
    try:
        code, out, err = _run_cli(p)
        print(f"[cli_aspiracional] code={code} stdout={out[:200]}")
        assert code == 0, f"DSC aspiracional debe exit 0 (got {code}). stderr={err}"
        assert "[warn]" in out or "aspiracional" in out.lower()
    finally:
        p.unlink(missing_ok=True)


def test_cli_missing_file_exit_2():
    """CA6: archivo inexistente → exit 2 (error de uso)."""
    fake_path = ROOT / "DSC-X-CA6-4-no-existe.md"
    assert not fake_path.exists()
    code, out, err = _run_cli(fake_path)
    print(f"[cli_missing_file] code={code} stderr={err[:200]}")
    assert code == 2, f"Archivo inexistente debe exit 2 (got {code}). stderr={err}"
    assert "no existe" in err.lower()


if __name__ == "__main__":
    test_valid_dsc_with_existing_path()
    test_valid_aspirational()
    test_invalid_no_section()
    test_invalid_paths_dont_exist()
    test_cli_blocks_invalid_dsc_exit_1()
    test_cli_passes_valid_dsc_exit_0()
    test_cli_passes_aspirational_exit_0_with_warn()
    test_cli_missing_file_exit_2()
    print("\n[ok] Los 8 tests pasaron (4 unit + 4 CLI bloqueante T8/CA6).")
