#!/usr/bin/env python3
# tools/dsc_contract_check.py
"""
Verificacion de contrato ejecutable adjunto en DSCs (DSC-G-017 enforcement).

Pre-commit hook que se dispara cuando un commit anade o modifica un archivo
en discovery_forense/CAPILLA_DECISIONES/. Verifica que el DSC declare al menos
un contrato ejecutable y que las rutas a codigo referenciadas existan.

Comportamiento:
    - DSC con seccion "## Contrato ejecutable" o "## Contratos ejecutables" Y
      al menos una ruta de archivo que existe -> exit 0 (commit pasa)
    - DSC sin seccion de contrato Y sin marcador `estado: aspiracional` o
      `**Estado:** Aspiracional` -> exit 1 (commit bloqueado)
    - DSC con marcador aspiracional -> exit 0 con warning (commit pasa pero se
      registra que el DSC es aspiracional)

CLI:
    python tools/dsc_contract_check.py path/to/DSC-X.md [more.md ...]

Exit code:
    0 = todos los DSCs cumplen (o son explicitamente aspiracionales)
    1 = al menos uno viola DSC-G-017 sin marcador aspiracional
    2 = error de uso
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


CONTRACT_SECTION_PATTERNS = [
    r"^#{2,6}\s+contrato[s]?\s+ejecutable[s]?",
    r"^#{2,6}\s+contrato[s]?\s+adjunto[s]?",
    r"^#{2,6}\s+contrato[s]?\s+que\s+(?:adjunta|ana[dD]e)",
    r"^#{2,6}\s+dsc-as-contract",
]

ASPIRATIONAL_MARKERS = [
    # Marcador formal: linea entera "Estado: Aspiracional" o
    # "**Estado:** Aspiracional" o "**Estado**: Aspiracional".
    # Anclado a inicio/fin de linea para NO matchear prosa que mencione el
    # concepto (ej. "el DSC se etiqueta `estado: aspiracional`").
    r"^[\*\s]*estado[\s\*:`]+aspiracional[\s\*\.]*$",
    r"^\s*<!--\s*aspiracional\s*-->\s*$",
]

# Heuristica para extraer rutas de archivo. Importante: `\.?` al inicio para
# capturar paths como `.github/workflows/...` (hidden directories).
PATH_PATTERNS = [
    # Backtick-enclosed: `path/to/file.ext`
    re.compile(
        r"`(\.?[\w/.\-]+\.(?:py|yml|yaml|sh|sql|toml|json|md|js|ts|tsx|go|rs))`"
    ),
    # Inline (delimitado por espacio/parentesis/pipe/start/etc, NO por \b para
    # poder capturar el dot inicial)
    re.compile(
        r"(?:^|[\s\(\|>])(\.?(?:[\w.\-]+/)+[\w.\-]+"
        r"\.(?:py|yml|yaml|sh|sql|toml|json|md|js|ts|tsx|go|rs))"
    ),
]


@dataclass
class CheckResult:
    file: str
    has_contract_section: bool
    is_aspirational: bool
    extracted_paths: list[str]
    paths_found: list[str]
    paths_missing: list[str]
    passed: bool
    reason: str


def _has_section(text: str) -> bool:
    for pat in CONTRACT_SECTION_PATTERNS:
        if re.search(pat, text, flags=re.MULTILINE | re.IGNORECASE):
            return True
    return False


def _is_aspirational(text: str) -> bool:
    for pat in ASPIRATIONAL_MARKERS:
        if re.search(pat, text, flags=re.MULTILINE | re.IGNORECASE):
            return True
    return False


def _extract_paths_from_section(text: str) -> list[str]:
    """Extrae rutas de archivo mencionadas dentro de la seccion de contratos."""
    section_start = -1
    for pat in CONTRACT_SECTION_PATTERNS:
        m = re.search(pat, text, flags=re.MULTILINE | re.IGNORECASE)
        if m:
            section_start = m.start()
            break
    if section_start == -1:
        return []

    rest = text[section_start:]
    after_heading = rest.split("\n", 1)[1] if "\n" in rest else ""
    next_heading = re.search(r"\n#{1,6}\s+", after_heading)
    section_text = after_heading[:next_heading.start()] if next_heading else after_heading

    paths = []
    for pat in PATH_PATTERNS:
        for m in pat.finditer(section_text):
            p = m.group(1).strip()
            if p not in paths and len(p) > 3:
                paths.append(p)
    return paths


def check_dsc(path: Path, repo_root: Path) -> CheckResult:
    text = path.read_text(encoding="utf-8")
    aspirational = _is_aspirational(text)
    has_section = _has_section(text)
    extracted = _extract_paths_from_section(text) if has_section else []

    found: list[str] = []
    missing: list[str] = []
    for p in extracted:
        full = (repo_root / p).resolve()
        if full.exists():
            found.append(p)
        else:
            missing.append(p)

    if aspirational:
        return CheckResult(
            file=str(path),
            has_contract_section=has_section,
            is_aspirational=True,
            extracted_paths=extracted,
            paths_found=found,
            paths_missing=missing,
            passed=True,
            reason="DSC marcado aspiracional explicitamente — pasa con warning",
        )

    if not has_section:
        return CheckResult(
            file=str(path),
            has_contract_section=False,
            is_aspirational=False,
            extracted_paths=[],
            paths_found=[],
            paths_missing=[],
            passed=False,
            reason=(
                "DSC sin seccion '## Contrato ejecutable' y sin marcador aspiracional. "
                "DSC-G-017 exige contrato adjunto o etiqueta explicita."
            ),
        )

    if not found:
        return CheckResult(
            file=str(path),
            has_contract_section=True,
            is_aspirational=False,
            extracted_paths=extracted,
            paths_found=[],
            paths_missing=missing,
            passed=False,
            reason=(
                f"Seccion de contrato presente pero ninguna de las rutas referenciadas existe. "
                f"Rutas mencionadas: {extracted}. "
                "Crear los archivos primero o marcar el DSC aspiracional."
            ),
        )

    return CheckResult(
        file=str(path),
        has_contract_section=True,
        is_aspirational=False,
        extracted_paths=extracted,
        paths_found=found,
        paths_missing=missing,
        passed=True,
        reason=(
            f"OK. {len(found)}/{len(extracted)} rutas de contrato existen."
            + (f" Faltan: {missing}" if missing else "")
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verifica que cada DSC tenga contrato ejecutable adjunto (DSC-G-017). "
            "Pre-commit hook."
        )
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="archivos .md de DSC a verificar",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="raiz del repo para resolver rutas relativas (default cwd)",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    results: list[CheckResult] = []
    for f in args.files:
        if not f.exists():
            print(f"ERROR: no existe: {f}", file=sys.stderr)
            return 2
        name = f.name
        if not (name.startswith("DSC-") or "CAPILLA_DECISIONES" in str(f)):
            continue
        results.append(check_dsc(f, repo_root))

    failures = [r for r in results if not r.passed]
    aspirationals = [r for r in results if r.is_aspirational]

    for r in results:
        if r.passed and not r.is_aspirational:
            print(f"[ok]   {r.file}: {r.reason}")
        elif r.is_aspirational:
            print(f"[warn] {r.file}: {r.reason}")
        else:
            print(f"[ERR]  {r.file}: {r.reason}", file=sys.stderr)

    if failures:
        print(
            f"\n{len(failures)}/{len(results)} DSCs violan DSC-G-017. "
            f"Anadir seccion '## Contrato ejecutable' con ruta a codigo existente, "
            f"o marcar DSC con `**Estado:** Aspiracional`.",
            file=sys.stderr,
        )
        return 1

    if aspirationals:
        print(
            f"\n[ok] {len(results) - len(aspirationals)} DSCs con contrato + "
            f"{len(aspirationals)} aspiracionales documentados."
        )
    else:
        print(f"\n[ok] {len(results)} DSCs todos con contrato ejecutable adjunto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
