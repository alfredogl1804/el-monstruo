# tests/test_check_index_drift.py
"""
Tests para tools/_check_index_drift.py (contrato ejecutable DSC-G-008 v4 §5).

Cubre:
* Happy path: zero drift detectado en un capilla sintético alineado.
* MISSING_FILESYSTEM: index declara código sin archivo en disco.
* MISSING_INDEX: archivo en disco sin entrada en index.
* Edge — tombstone: archivo con marker de relocate ignorado del check de deuda.
* Edge — _ARCHIVED/ subtree: archivos bajo _ARCHIVED/ excluidos del scan.
* Edge — entrada con `[brackets]` y `(paréntesis)` en el título: parser robusto.
* Edge — cross-reference a INCIDENTES/: tratada como redirección, no como entry.
* CLI smoke: exit code 0/1 y JSON estructurado correcto.
* Audit real del repo vigente: zero drift al cierre del spike.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "_check_index_drift.py"

# Importable interface via sys.path.
sys.path.insert(0, str(REPO_ROOT / "tools"))
import importlib.util

_spec = importlib.util.spec_from_file_location("_check_index_drift", SCRIPT)
assert _spec is not None and _spec.loader is not None
_module = importlib.util.module_from_spec(_spec)
sys.modules["_check_index_drift"] = _module  # required so @dataclass can resolve __module__
_spec.loader.exec_module(_module)

parse_index = _module.parse_index
scan_filesystem = _module.scan_filesystem
compute_drift = _module.compute_drift
main = _module.main


# -------------------- helpers --------------------


def _make_capilla(tmp_path: Path, *, declared: list[dict], on_disk: list[dict]) -> Path:
    """Crea un capilla sintético: _INDEX.md con declaraciones + archivos en disco.

    `declared` items: {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_foo.md", "title": "..."}.
    `on_disk` items: {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_foo.md", "tombstone": False}.
    """
    capilla = tmp_path / "CAPILLA_DECISIONES"
    capilla.mkdir(parents=True)

    # Filesystem entries
    for entry in on_disk:
        rel = capilla / entry["path"]
        rel.parent.mkdir(parents=True, exist_ok=True)
        body = "# Test DSC\n"
        if entry.get("tombstone"):
            body = "# Test DSC\n> **Nota de relocate (2026-05-07):** este archivo se llamaba antes ...\n"
        rel.write_text(body, encoding="utf-8")

    # Index file
    index = capilla / "_INDEX.md"
    lines = [
        "# Capilla de decisiones — test fixture\n",
        "\n",
        "## _GLOBAL\n",
        "\n",
        "| ID | Título | Tipo |\n",
        "|---|---|---|\n",
    ]
    for d in declared:
        title = d.get("title", "Título de prueba")
        lines.append(f"| `{d['code']}` | [{title}]({d['path']}) | politica |\n")
    index.write_text("".join(lines), encoding="utf-8")
    return capilla


# -------------------- unit tests --------------------


def test_happy_path_zero_drift(tmp_path: Path):
    """Index y filesystem alineados → zero drift, exit 0."""
    declared = [
        {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_alpha.md", "title": "Alpha"},
        {"code": "DSC-X-002", "path": "_GLOBAL/DSC-X-002_beta.md", "title": "Beta"},
    ]
    capilla = _make_capilla(tmp_path, declared=declared, on_disk=declared)

    idx = parse_index(capilla / "_INDEX.md")
    fs = scan_filesystem(capilla)
    report = compute_drift(idx, fs, capilla)

    assert report.has_drift is False
    assert len(report.missing_filesystem) == 0
    assert len(report.missing_index) == 0
    assert report.declared_codes == ["DSC-X-001", "DSC-X-002"]
    assert report.filesystem_codes == ["DSC-X-001", "DSC-X-002"]


def test_missing_filesystem_drift(tmp_path: Path):
    """Index declara código sin archivo → MISSING_FILESYSTEM."""
    declared = [
        {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_alpha.md", "title": "A"},
        {"code": "DSC-X-002", "path": "_GLOBAL/DSC-X-002_beta.md", "title": "B"},  # solo en index
    ]
    on_disk = [
        {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_alpha.md"},
    ]
    capilla = _make_capilla(tmp_path, declared=declared, on_disk=on_disk)

    idx = parse_index(capilla / "_INDEX.md")
    fs = scan_filesystem(capilla)
    report = compute_drift(idx, fs, capilla)

    assert report.has_drift is True
    assert len(report.missing_filesystem) == 1
    assert report.missing_filesystem[0]["code"] == "DSC-X-002"
    assert report.missing_filesystem[0]["declared_path"] == "_GLOBAL/DSC-X-002_beta.md"
    assert len(report.missing_index) == 0


def test_missing_index_drift(tmp_path: Path):
    """Archivo en disco sin entrada en index → MISSING_INDEX."""
    declared = [
        {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_alpha.md", "title": "A"},
    ]
    on_disk = [
        {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_alpha.md"},
        {"code": "DSC-X-009", "path": "_GLOBAL/DSC-X-009_huerfano.md"},  # huérfano
    ]
    capilla = _make_capilla(tmp_path, declared=declared, on_disk=on_disk)

    idx = parse_index(capilla / "_INDEX.md")
    fs = scan_filesystem(capilla)
    report = compute_drift(idx, fs, capilla)

    assert report.has_drift is True
    assert len(report.missing_index) == 1
    assert report.missing_index[0]["code"] == "DSC-X-009"
    assert report.missing_index[0]["filesystem_path"] == "_GLOBAL/DSC-X-009_huerfano.md"
    assert len(report.missing_filesystem) == 0


def test_tombstoned_file_not_flagged_as_missing_index(tmp_path: Path):
    """Archivo con tombstone NO se considera deuda inversa."""
    declared = [
        {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_alpha.md", "title": "A"},
    ]
    on_disk = [
        {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_alpha.md"},
        {"code": "DSC-X-099", "path": "_GLOBAL/DSC-X-099_legacy.md", "tombstone": True},
    ]
    capilla = _make_capilla(tmp_path, declared=declared, on_disk=on_disk)

    idx = parse_index(capilla / "_INDEX.md")
    fs = scan_filesystem(capilla)
    report = compute_drift(idx, fs, capilla)

    assert report.has_drift is False
    assert "_GLOBAL/DSC-X-099_legacy.md" in report.tombstoned_files
    assert all(item["code"] != "DSC-X-099" for item in report.missing_index)


def test_archived_subtree_excluded(tmp_path: Path):
    """Archivos bajo _ARCHIVED/ son ignorados por el scan."""
    declared = [
        {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_alpha.md", "title": "A"},
    ]
    capilla = _make_capilla(tmp_path, declared=declared, on_disk=declared)

    # Crea archivo bajo _ARCHIVED/ que NO debe aparecer en filesystem scan
    archived = capilla / "_ARCHIVED" / "DSC-X-500_obsoleto.md"
    archived.parent.mkdir(parents=True)
    archived.write_text("# obsolete\n", encoding="utf-8")

    fs = scan_filesystem(capilla)
    codes = {fe.code for fe in fs}
    assert "DSC-X-500" not in codes
    assert "DSC-X-001" in codes


def test_title_with_brackets_and_parens_parsed_correctly(tmp_path: Path):
    """Parser tolera `[brackets]` y `(parens)` dentro del título del DSC."""
    capilla = tmp_path / "CAPILLA_DECISIONES"
    (capilla / "_GLOBAL").mkdir(parents=True)
    (capilla / "_GLOBAL" / "DSC-S-003_scripts.md").write_text("# s3\n", encoding="utf-8")
    (capilla / "_GLOBAL" / "DSC-S-012_anti_deriva.md").write_text("# s12\n", encoding="utf-8")

    # Títulos que rompían el parser viejo: ()/[] no balanceados en el título.
    (capilla / "_INDEX.md").write_text(
        "## _GLOBAL\n\n"
        "| ID | Título | Tipo |\n"
        "|---|---|---|\n"
        "| `DSC-S-003` | [Scripts deben usar os.environ[VAR] (fail loud) — PROHIBIDO os.environ.get(VAR, default_secret).](_GLOBAL/DSC-S-003_scripts.md) | antipatron |\n"
        "| `DSC-S-012` | [Anti-deriva migraciones [DERIVA-RESUELTA] marca exigida](_GLOBAL/DSC-S-012_anti_deriva.md) | restriccion_dura |\n",
        encoding="utf-8",
    )

    idx = parse_index(capilla / "_INDEX.md")
    codes = {e.code for e in idx}
    assert codes == {"DSC-S-003", "DSC-S-012"}


def test_incidentes_path_treated_as_redirection_not_entry(tmp_path: Path):
    """Entradas que apuntan a INCIDENTES/ son redirecciones, no declaraciones."""
    capilla = tmp_path / "CAPILLA_DECISIONES"
    (capilla / "_GLOBAL").mkdir(parents=True)
    (capilla / "_GLOBAL" / "DSC-S-005_politica.md").write_text("# p\n", encoding="utf-8")
    (capilla / "_INDEX.md").write_text(
        "## _GLOBAL\n\n"
        "| ID | Título | Tipo |\n"
        "|---|---|---|\n"
        "| `DSC-S-005` | [Política canónica](_GLOBAL/DSC-S-005_politica.md) | politica |\n"
        "\n"
        "Note: snapshot forense relocated a [INCIDENTES](../INCIDENTES/snapshot.md) (no es entrada).\n",
        encoding="utf-8",
    )
    idx = parse_index(capilla / "_INDEX.md")
    # Solo debe contar la entrada canónica, no la referencia narrativa.
    assert [(e.code, e.declared_path) for e in idx] == [("DSC-S-005", "_GLOBAL/DSC-S-005_politica.md")]


def test_cli_exit_code_zero_when_no_drift(tmp_path: Path):
    """Exit 0 cuando no hay drift via CLI."""
    declared = [
        {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_alpha.md", "title": "A"},
    ]
    capilla = _make_capilla(tmp_path, declared=declared, on_disk=declared)

    out_json = tmp_path / "report.json"
    rc = main(
        [
            "--capilla",
            str(capilla),
            "--index",
            str(capilla / "_INDEX.md"),
            "--json",
            str(out_json),
            "--quiet",
        ]
    )
    assert rc == 0
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["summary"]["has_drift"] is False


def test_cli_exit_code_one_when_drift(tmp_path: Path):
    """Exit 1 cuando hay drift via CLI."""
    declared = [
        {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_alpha.md", "title": "A"},
    ]
    on_disk = [
        {"code": "DSC-X-001", "path": "_GLOBAL/DSC-X-001_alpha.md"},
        {"code": "DSC-X-009", "path": "_GLOBAL/DSC-X-009_huerfano.md"},
    ]
    capilla = _make_capilla(tmp_path, declared=declared, on_disk=on_disk)

    out_json = tmp_path / "report.json"
    rc = main(
        [
            "--capilla",
            str(capilla),
            "--index",
            str(capilla / "_INDEX.md"),
            "--json",
            str(out_json),
            "--quiet",
        ]
    )
    assert rc == 1
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["summary"]["has_drift"] is True
    assert payload["summary"]["missing_index_count"] == 1


def test_cli_exit_code_two_when_missing_index_file(tmp_path: Path):
    """Exit 2 cuando no se encuentra el index."""
    capilla = tmp_path / "CAPILLA_DECISIONES"
    capilla.mkdir()
    rc = main(
        [
            "--capilla",
            str(capilla),
            "--index",
            str(tmp_path / "_INDEX_does_not_exist.md"),
            "--quiet",
        ]
    )
    assert rc == 2


def test_real_repo_zero_drift_at_spike_close():
    """Sanity check: el repo vigente debe estar en zero drift al cierre del spike."""
    rc = main(["--quiet"])
    assert rc == 0, (
        "El repo tiene drift documental detectado. Ejecutar "
        "`python3 tools/_check_index_drift.py` para ver detalles y corregir."
    )


def test_script_runs_via_subprocess():
    """Smoke: el script es ejecutable como módulo CLI."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--quiet"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode in (0, 1), f"unexpected returncode {result.returncode}, stderr={result.stderr!r}"
