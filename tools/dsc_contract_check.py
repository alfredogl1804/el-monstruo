#!/usr/bin/env python3
# tools/dsc_contract_check.py
"""
Verificacion de contrato ejecutable adjunto en DSCs (DSC-G-017 enforcement).

Pre-commit hook que se dispara cuando un commit anade o modifica un archivo
en discovery_forense/CAPILLA_DECISIONES/. Verifica que el DSC declare al menos
un contrato ejecutable y que las rutas a codigo referenciadas existan.

Comportamiento:
    1. Consulta el index central _dsc_contracts_index.yaml PRIMERO.
       - Si DSC tiene entry status=enforced + paths que existen → exit 0
       - Si DSC tiene entry status=aspirational + reason → exit 0 con warning
    2. Fallback: parsing del .md (legacy):
       - DSC con seccion "## Contrato ejecutable" Y rutas que existen → exit 0
       - DSC con marcador `**Estado:** Aspiracional` → exit 0 con warning
       - Sin nada → exit 1

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
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore


# Path canonico al index central (DSC-G-017 enforcement sistemico).
DSC_CONTRACTS_INDEX_PATH = Path(
    "discovery_forense/CAPILLA_DECISIONES/_dsc_contracts_index.yaml"
)


CONTRACT_SECTION_PATTERNS = [
    r"^#{2,6}\s+contrato[s]?\s+ejecutable[s]?",
    r"^#{2,6}\s+contrato[s]?\s+adjunto[s]?",
    r"^#{2,6}\s+contrato[s]?\s+que\s+(?:adjunta|ana[dD]e)",
    r"^#{2,6}\s+dsc-as-contract",
]

ASPIRATIONAL_MARKERS = [
    r"^[\*\s]*estado[\s\*:`]+aspiracional[\s\*\.]*$",
    r"^\s*<!--\s*aspiracional\s*-->\s*$",
]

PATH_PATTERNS = [
    re.compile(
        r"`(\.?[\w/.\-]+\.(?:py|yml|yaml|sh|sql|toml|json|md|js|ts|tsx|go|rs))`"
    ),
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


def _load_index(repo_root: Path) -> dict[str, Any]:
    """Carga el index central. Vacio dict si no existe o yaml no instalado."""
    full = repo_root / DSC_CONTRACTS_INDEX_PATH
    if not full.exists() or yaml is None:
        return {}
    try:
        data = yaml.safe_load(full.read_text())
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    return data.get("dscs") or {}


def _index_key_for(path: Path, repo_root: Path) -> str | None:
    """Convierte path absoluto del DSC en key del index (relativo a CAPILLA)."""
    capilla = repo_root / "discovery_forense" / "CAPILLA_DECISIONES"
    try:
        rel = path.resolve().relative_to(capilla.resolve())
        return str(rel)
    except ValueError:
        return None


def check_dsc(path: Path, repo_root: Path) -> CheckResult:
    # 1. Consultar index central PRIMERO (DSC-G-017 sistemico).
    index = _load_index(repo_root)
    key = _index_key_for(path, repo_root)
    if key and key in index:
        entry = index[key]
        status = entry.get("status")
        if status == "enforced":
            contracts = entry.get("contracts") or []
            found = [c for c in contracts if (repo_root / c).exists()]
            missing = [c for c in contracts if not (repo_root / c).exists()]
            if found:
                return CheckResult(
                    file=str(path),
                    has_contract_section=True,
                    is_aspirational=False,
                    extracted_paths=contracts,
                    paths_found=found,
                    paths_missing=missing,
                    passed=True,
                    reason=(
                        f"OK via index. {len(found)}/{len(contracts)} contratos existen."
                        + (f" Faltan: {missing}" if missing else "")
                    ),
                )
            return CheckResult(
                file=str(path),
                has_contract_section=True,
                is_aspirational=False,
                extracted_paths=contracts,
                paths_found=[],
                paths_missing=missing,
                passed=False,
                reason=(
                    f"Index declara 'enforced' pero NINGUNA ruta existe: {missing}. "
                    f"Crear los archivos primero o cambiar status a 'aspirational'."
                ),
            )
        if status == "aspirational":
            return CheckResult(
                file=str(path),
                has_contract_section=False,
                is_aspirational=True,
                extracted_paths=[],
                paths_found=[],
                paths_missing=[],
                passed=True,
                reason=(
                    f"Aspirational via index. Razon: "
                    f"{entry.get('reason', 'sin razon documentada')[:200]}"
                ),
            )

    # 2. Fallback: parsing del .md (legacy path para DSCs no en index).
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
                "DSC sin entry en _dsc_contracts_index.yaml, sin seccion "
                "'## Contrato ejecutable' y sin marcador aspiracional. "
                "DSC-G-017 exige una de las tres."
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
            f"OK via .md parsing. {len(found)}/{len(extracted)} rutas existen."
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
            f"Anadir entry en _dsc_contracts_index.yaml o seccion "
            f"'## Contrato ejecutable' o marcador `**Estado:** Aspiracional`.",
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
