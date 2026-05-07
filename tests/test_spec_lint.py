# tests/test_spec_lint.py
"""
Tests del linter de specs (DSC-G-008 v2 + DSC-G-012 + DSC-G-017).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.spec_lint as sl  # noqa: E402


SPEC_VALID_LEGACY = """\
# Sprint S-XX — Mi sprint legacy

**Estado:** Propuesto
**Objetivo:** demostrar que un spec viejo sin perfil_riesgo aun pasa lenient

## Tareas

### Tarea S-XX.1 — Hacer cosa A

Detalle de la cosa A.

## Criterios de cierre verde

- pytest tests/test_cosa_a.py pasa
- exit code 0
"""

SPEC_VALID_STRICT = """\
---
lint_strict: true
---

# Sprint S-CONTRATOS-001 — Traduccion de DSCs aspiracionales

**Estado:** Propuesto
**Objetivo:** producir contratos ejecutables para DSCs aspiracionales pendientes

## Tareas

### Tarea T1 — Decorator de validacion

**perfil_riesgo:** write-safe

Detalle.

### Tarea T2 — Migracion SQL

**perfil_riesgo:** write-risky

Detalle.

## Contratos ejecutables que adjunta

- DSC-V-001 -> kernel/validation/perplexity_decorator.py
- DSC-G-011 -> migrations/0001_rotation_log_constraint.sql

## Criterios de cierre verde

- python -m kernel.validation.test_decorator pasa con exit 0
- migracion SQL aplicada en staging y reproducible artifact en reports/
"""

SPEC_INVALID_NO_TITLE = """\
**Estado:** Propuesto
**Objetivo:** roto, no tiene H1

## Tareas

### Tarea X
"""

SPEC_INVALID_MISSING_SECTIONS = """\
# Sprint X
**Estado:** Propuesto
"""

SPEC_STRICT_MISSING_PERFIL = """\
<!-- lint_strict -->

# Sprint S-Z

**Estado:** Propuesto
**Objetivo:** estricto pero sin perfil

## Tareas

### Tarea Z.1 — Algo

(falta perfil_riesgo)

## Criterios de cierre verde

- pytest pasa
"""


def _write_tmp(content: str) -> Path:
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


def test_legacy_spec_passes_lenient():
    p = _write_tmp(SPEC_VALID_LEGACY)
    res = sl.lint_file(p, force_strict=False)
    print(f"[legacy] errors={len(res.errors)} warnings={len(res.warnings)} strict={res.strict_mode}")
    for f in res.findings:
        print(f"   {f}")
    assert res.passed(), f"Legacy spec deberia pasar lenient. errors={res.errors}"


def test_strict_spec_passes_strict():
    p = _write_tmp(SPEC_VALID_STRICT)
    res = sl.lint_file(p, force_strict=False)
    print(f"[strict_ok] errors={len(res.errors)} warnings={len(res.warnings)} strict={res.strict_mode}")
    for f in res.findings:
        print(f"   {f}")
    assert res.strict_mode, "Auto-strict deberia activarse por frontmatter lint_strict: true"
    assert res.passed(), f"Spec estricto valido deberia pasar. errors={res.errors}"


def test_no_title_fails():
    p = _write_tmp(SPEC_INVALID_NO_TITLE)
    res = sl.lint_file(p)
    print(f"[no_title] errors={len(res.errors)}")
    rules = {f.rule for f in res.errors}
    assert "structure.title" in rules, f"Debe fallar structure.title. got: {rules}"


def test_missing_sections_fails():
    p = _write_tmp(SPEC_INVALID_MISSING_SECTIONS)
    res = sl.lint_file(p)
    print(f"[missing_sections] errors={len(res.errors)}")
    rules = {f.rule for f in res.errors}
    assert "structure.objetivo" in rules
    assert "structure.tareas_section" in rules
    assert "structure.criterios_cierre" in rules


def test_strict_missing_perfil_riesgo_fails():
    p = _write_tmp(SPEC_STRICT_MISSING_PERFIL)
    res = sl.lint_file(p)
    print(f"[strict_no_perfil] strict={res.strict_mode} errors={len(res.errors)}")
    for f in res.findings:
        print(f"   {f}")
    assert res.strict_mode, "Auto-strict via comentario HTML deberia activarse"
    rules = {f.rule for f in res.errors}
    assert "dsc-g-012.perfil_riesgo_missing" in rules, (
        f"En strict, perfil_riesgo missing debe ser ERROR. got: {rules}"
    )


def test_lenient_missing_perfil_is_warning():
    """Mismo spec pero sin marcador strict — perfil_riesgo missing es WARNING."""
    text = SPEC_STRICT_MISSING_PERFIL.replace("<!-- lint_strict -->", "")
    p = _write_tmp(text)
    res = sl.lint_file(p)
    print(f"[lenient_no_perfil] strict={res.strict_mode} errors={len(res.errors)} warnings={len(res.warnings)}")
    assert not res.strict_mode
    warning_rules = {f.rule for f in res.warnings}
    error_rules = {f.rule for f in res.errors}
    assert "dsc-g-012.perfil_riesgo_missing" in warning_rules
    assert "dsc-g-012.perfil_riesgo_missing" not in error_rules


if __name__ == "__main__":
    test_legacy_spec_passes_lenient()
    test_strict_spec_passes_strict()
    test_no_title_fails()
    test_missing_sections_fails()
    test_strict_missing_perfil_riesgo_fails()
    test_lenient_missing_perfil_is_warning()
    print("\n[ok] Los 6 tests pasaron.")
