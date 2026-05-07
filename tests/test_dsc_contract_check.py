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


if __name__ == "__main__":
    test_valid_dsc_with_existing_path()
    test_valid_aspirational()
    test_invalid_no_section()
    test_invalid_paths_dont_exist()
    print("\n[ok] Los 4 tests pasaron.")
