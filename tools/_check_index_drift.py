#!/usr/bin/env python3
# tools/_check_index_drift.py
"""
Audit binario del drift entre `discovery_forense/CAPILLA_DECISIONES/_INDEX.md`
(declaracion doctrinal) y los archivos `DSC-*.md` reales en filesystem
(realidad material).

Contrato ejecutable de DSC-G-008 v4 §5 — "drifts documentales sobreviven a su
resolucion material" (insight Manus Hilo Catastro en spike
DSC-S-005-CANONICAL-AUDIT-001, 2026-05-12, canonizado por Cowork T2-A).

Reporta dos clases de drift:

* `MISSING_FILESYSTEM`: codigo DSC declarado en `_INDEX.md` cuya entrada apunta
  a un path que no existe en disco. Drift "el index promete lo que no entrega".
* `MISSING_INDEX`: archivo `DSC-*.md` presente en disco que no aparece como
  entrada en `_INDEX.md`. Drift "deuda inversa de indexacion".

Exit codes:
    0 = zero drift detectado
    1 = drift detectado (cualquiera de las dos clases)
    2 = error de uso o parsing

Output:
    - stdout: resumen humano legible
    - --json PATH: reporte estructurado para auditoria (`reports/index_drift_audit.json`)

CLI:
    python3 tools/_check_index_drift.py
    python3 tools/_check_index_drift.py --json reports/index_drift_audit.json
    python3 tools/_check_index_drift.py --capilla custom/CAPILLA --index custom/_INDEX.md

Edge cases honrados:

* `discovery_forense/INCIDENTES/`: archivos forenses no son DSCs aunque su
  nombre antiguo haya tenido prefijo DSC-S-005-*. Excluidos por path raiz.
* `discovery_forense/CAPILLA_DECISIONES/_ARCHIVED/`: si existe, excluido del
  scan de filesystem (se considera explicitamente fuera del corpus vigente).
* Archivos con tombstone (linea 2 que contiene `relocate` o `RELOCATED`) en el
  subtree de CAPILLA_DECISIONES se marcan como `tombstoned` y NO requieren
  entrada en index si su contenido lo declara explicitamente.
* `_INDEX.md` puede contener referencias historicas (tablas de "RESUELTO" o
  "Conflicto pasado") que no son entradas vigentes. El parser solo considera
  entradas en formato cell estandar dentro de tablas markdown que apunten a un
  `.md` real bajo `_GLOBAL/`, `EL-MONSTRUO/`, etc.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[1]
CAPILLA_DEFAULT = "discovery_forense/CAPILLA_DECISIONES"
INDEX_DEFAULT = "discovery_forense/CAPILLA_DECISIONES/_INDEX.md"

# Patron de codigo DSC canonico: DSC-<PREFIX>-<NUM>
# Acepta letras/digitos en el segmento medio para sopportar DSC-MO-001,
# DSC-CIP-002, DSC-CIP-PEND-002, DSC-S-006, etc.
DSC_CODE_RE = re.compile(r"DSC-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d+", re.ASCII)

# Patron robusto para entrada de tabla en _INDEX.md.
# Formato canonico:
#   | `DSC-S-001` | [titulo opcional con [brackets] y (parens)](_GLOBAL/DSC-S-001_xxx.md) | tipo |
#
# Estrategia en dos pasos para tolerar [], () y caracteres especiales en el
# titulo del DSC sin abortar el match: (1) detectar codigo en celda de tabla,
# (2) buscar el path `(.../DSC-XXX.md)` mas cercano hacia adelante en la misma
# linea. Esto evita regex anidados fragiles.
INDEX_CODE_CELL_RE = re.compile(r"\|\s*`(?P<code>DSC-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)`\s*\|")
INDEX_PATH_RE = re.compile(r"\((?P<path>(?:[A-Za-z0-9_/\.-]+/)?DSC-[A-Za-z0-9_\.-]+\.md)\)")

# Tombstone marker en linea 2 de un archivo forense relocado.
TOMBSTONE_HINTS = ("relocate", "RELOCATED", "tombstone", "Nota de relocate")


@dataclass
class IndexEntry:
    code: str
    declared_path: str  # relativo a CAPILLA_DECISIONES (ej `_GLOBAL/DSC-S-001_xxx.md`)
    line: int


@dataclass
class FilesystemEntry:
    code: str
    abs_path: Path
    relative_to_capilla: str
    tombstoned: bool = False


@dataclass
class DriftReport:
    capilla_root: str
    index_path: str
    declared_codes: list[str] = field(default_factory=list)
    filesystem_codes: list[str] = field(default_factory=list)
    missing_filesystem: list[dict] = field(default_factory=list)
    missing_index: list[dict] = field(default_factory=list)
    tombstoned_files: list[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.missing_filesystem) or bool(self.missing_index)

    def to_json(self) -> dict:
        return {
            "capilla_root": self.capilla_root,
            "index_path": self.index_path,
            "summary": {
                "declared_in_index": len(self.declared_codes),
                "files_in_filesystem": len(self.filesystem_codes),
                "missing_filesystem_count": len(self.missing_filesystem),
                "missing_index_count": len(self.missing_index),
                "tombstoned_files_count": len(self.tombstoned_files),
                "has_drift": self.has_drift,
            },
            "missing_filesystem": self.missing_filesystem,
            "missing_index": self.missing_index,
            "tombstoned_files": sorted(self.tombstoned_files),
        }


def _is_tombstoned(path: Path) -> bool:
    """Return True if file is forensic tombstone (relocate marker in first 3 lines)."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            head = [next(fh, "") for _ in range(3)]
    except (OSError, StopIteration):
        return False
    joined = "\n".join(head)
    return any(hint in joined for hint in TOMBSTONE_HINTS)


def parse_index(index_path: Path) -> list[IndexEntry]:
    """Parse _INDEX.md and return all (code, declared_path) entries.

    Only considers table rows that reference a markdown file under
    CAPILLA_DECISIONES (relative path). Skips entries pointing to files
    outside the capilla (e.g., INCIDENTES/), which are documented redirections.
    """
    entries: list[IndexEntry] = []
    if not index_path.is_file():
        raise FileNotFoundError(f"Index not found: {index_path}")
    with index_path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            # Step 1: detect every DSC code present as a leading cell.
            for code_m in INDEX_CODE_CELL_RE.finditer(line):
                code = code_m.group("code")
                # Step 2: search the nearest .md path to the right of this cell.
                tail = line[code_m.end() :]
                path_m = INDEX_PATH_RE.search(tail)
                if not path_m:
                    # Code listed without an inline path link (e.g. plain narrative
                    # row). Skip — not a canonical declaration.
                    continue
                path = path_m.group("path")
                # Skip cross-references to INCIDENTES/ or _ARCHIVED/ — those are
                # explicit redirections, not declarations of canonical DSCs.
                if "INCIDENTES/" in path or "_ARCHIVED/" in path:
                    continue
                # Only accept paths whose basename starts with the same code.
                # This prevents accidentally matching a cross-reference link to
                # another DSC within the same row.
                basename = path.rsplit("/", 1)[-1]
                if not basename.startswith(code + "_") and basename != f"{code}.md":
                    continue
                entries.append(IndexEntry(code=code, declared_path=path, line=lineno))
    return entries


def scan_filesystem(capilla_root: Path) -> list[FilesystemEntry]:
    """Walk CAPILLA_DECISIONES and return one entry per DSC-*.md file.

    Excludes `_ARCHIVED/` subtree if present. Marks tombstoned files.
    """
    if not capilla_root.is_dir():
        raise FileNotFoundError(f"Capilla root not found: {capilla_root}")
    entries: list[FilesystemEntry] = []
    for dirpath, dirnames, filenames in os.walk(capilla_root):
        # Prune _ARCHIVED/ defensively
        dirnames[:] = [d for d in dirnames if d != "_ARCHIVED"]
        for filename in filenames:
            if not filename.startswith("DSC-") or not filename.endswith(".md"):
                continue
            code_match = DSC_CODE_RE.match(filename)
            if not code_match:
                continue
            code = code_match.group(0)
            abs_path = Path(dirpath) / filename
            relative = abs_path.relative_to(capilla_root).as_posix()
            entries.append(
                FilesystemEntry(
                    code=code,
                    abs_path=abs_path,
                    relative_to_capilla=relative,
                    tombstoned=_is_tombstoned(abs_path),
                )
            )
    return entries


def compute_drift(
    index_entries: list[IndexEntry],
    fs_entries: list[FilesystemEntry],
    capilla_root: Path,
) -> DriftReport:
    """Cross declarations vs filesystem and produce a DriftReport."""
    # MISSING_FILESYSTEM: index declared_path no existe en disco.
    missing_filesystem: list[dict] = []
    for ie in index_entries:
        declared_abs = capilla_root / ie.declared_path
        if not declared_abs.is_file():
            missing_filesystem.append(
                {
                    "code": ie.code,
                    "declared_path": ie.declared_path,
                    "index_line": ie.line,
                    "reason": "declared_in_index_but_not_in_filesystem",
                }
            )

    # MISSING_INDEX: file en disco que no aparece como entry en index.
    # Si el archivo es tombstoned, no se considera deuda — el tombstone declara
    # explicitamente que el archivo es residual.
    declared_codes = {ie.code for ie in index_entries}
    missing_index: list[dict] = []
    tombstoned_files: list[str] = []
    for fe in fs_entries:
        if fe.tombstoned:
            tombstoned_files.append(fe.relative_to_capilla)
            continue
        if fe.code not in declared_codes:
            missing_index.append(
                {
                    "code": fe.code,
                    "filesystem_path": fe.relative_to_capilla,
                    "reason": "in_filesystem_but_not_indexed",
                }
            )

    return DriftReport(
        capilla_root=str(capilla_root),
        index_path=str(capilla_root / "_INDEX.md"),
        declared_codes=sorted(declared_codes),
        filesystem_codes=sorted({fe.code for fe in fs_entries}),
        missing_filesystem=missing_filesystem,
        missing_index=missing_index,
        tombstoned_files=tombstoned_files,
    )


def render_human(report: DriftReport) -> str:
    """Render a human-readable summary."""
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("INDEX DRIFT AUDIT (DSC-G-008 v4 §5 contract enforcement)")
    lines.append("=" * 72)
    lines.append(f"Capilla root  : {report.capilla_root}")
    lines.append(f"Index path    : {report.index_path}")
    lines.append(f"Declared codes: {len(report.declared_codes)}")
    lines.append(f"Filesystem    : {len(report.filesystem_codes)}")
    lines.append(f"Tombstoned    : {len(report.tombstoned_files)}")
    lines.append("")

    if not report.has_drift:
        lines.append("✅ ZERO DRIFT — index and filesystem are aligned.")
        return "\n".join(lines)

    lines.append("❌ DRIFT DETECTED")
    if report.missing_filesystem:
        lines.append("")
        lines.append(f"-- MISSING_FILESYSTEM ({len(report.missing_filesystem)}) --")
        for item in report.missing_filesystem:
            lines.append(
                f"  · {item['code']:<24} declared at _INDEX.md:L{item['index_line']}"
                f" → path `{item['declared_path']}` NOT FOUND"
            )
    if report.missing_index:
        lines.append("")
        lines.append(f"-- MISSING_INDEX ({len(report.missing_index)}) --")
        for item in report.missing_index:
            lines.append(f"  · {item['code']:<24} present at `{item['filesystem_path']}` but no entry in _INDEX.md")
    lines.append("")
    lines.append("Acción: actualizar _INDEX.md y/o filesystem para cerrar el drift.")
    lines.append("Doctrina: DSC-G-008 v4 §5 — drifts documentales sobreviven a su")
    lines.append("resolución material si no hay enforcement automatizado.")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit drift between _INDEX.md declarations and DSC-*.md filesystem reality. "
            "Contrato ejecutable de DSC-G-008 v4 §5."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT_DEFAULT),
        help="Repository root (default: derived from script location).",
    )
    parser.add_argument(
        "--capilla",
        default=None,
        help=f"Capilla decisiones root (default: <repo-root>/{CAPILLA_DEFAULT}).",
    )
    parser.add_argument(
        "--index",
        default=None,
        help=f"Path to _INDEX.md (default: <repo-root>/{INDEX_DEFAULT}).",
    )
    parser.add_argument(
        "--json",
        dest="json_out",
        default=None,
        help="Write structured report to this JSON path (e.g. reports/index_drift_audit.json).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress human stdout (still writes JSON if --json given).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    repo_root = Path(args.repo_root).resolve()
    capilla = Path(args.capilla).resolve() if args.capilla else (repo_root / CAPILLA_DEFAULT)
    index_path = Path(args.index).resolve() if args.index else (repo_root / INDEX_DEFAULT)

    try:
        index_entries = parse_index(index_path)
        fs_entries = scan_filesystem(capilla)
    except FileNotFoundError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    report = compute_drift(index_entries, fs_entries, capilla)

    if not args.quiet:
        print(render_human(report))

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(report.to_json(), fh, indent=2, ensure_ascii=False, sort_keys=True)
            fh.write("\n")

    return 1 if report.has_drift else 0


if __name__ == "__main__":
    sys.exit(main())
