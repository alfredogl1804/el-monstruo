#!/usr/bin/env python3
# tools/check_perplexity_tags.py
"""
Scanner de tags `[NEEDS_PERPLEXITY_VALIDATION]` no resueltos (DSC-V-001).

Cualquier claim de estado-del-mundo (precios benchmark, competidores
vigentes, fechas de mercado, conversion rates de industria) que el
codigo Cowork produzca debe etiquetarse con la string literal
`[NEEDS_PERPLEXITY_VALIDATION]` hasta que Perplexity (DSC-V-001) valide
el claim. Este script scanea el repo y reporta donde hay tags no
resueltos.

Modo default: report-only, exit 0 siempre. Modo --fail-on-found:
exit 1 si hay tags. La activacion como hook bloqueante es Tarea T1
de Sprint S-CONTRATOS-001 (decorator `@requires_perplexity_validation`
con tabla `validation_log`).

CLI:
    python tools/check_perplexity_tags.py                    # report-only
    python tools/check_perplexity_tags.py --fail-on-found    # bloqueante
    python tools/check_perplexity_tags.py --json             # JSON output
    python tools/check_perplexity_tags.py kernel/transversales/  # path scope

Origen: DSC-V-001 + DSC-G-017. Texto de claim en codigo no es validacion;
la validacion vive en Perplexity log. Mientras tanto, el tag explicito
es deuda auto-detectable.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


TAG_PATTERN = re.compile(
    r"\[NEEDS_PERPLEXITY_VALIDATION\][^\n]*",
    flags=re.IGNORECASE,
)

DEFAULT_SKIP_PATTERNS = [
    "tools/check_perplexity_tags.py",
    "tests/test_check_perplexity_tags.py",
    "discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-V-001",
    "bridge/audit_dscs_aspiracionales",
    "bridge/sprints_propuestos/sprint_S-CONTRATOS-001",
    "discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-G-017",
]

DEFAULT_INCLUDE_EXTS = {".py", ".yml", ".yaml", ".md", ".sh", ".sql", ".toml"}


@dataclass
class TagHit:
    file: str
    line: int
    snippet: str
    tag: str


def _should_skip(rel_path: str, skip_patterns: list[str]) -> bool:
    return any(p in rel_path for p in skip_patterns)


def scan_file(path: Path, root: Path) -> list[TagHit]:
    if path.suffix not in DEFAULT_INCLUDE_EXTS:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    hits: list[TagHit] = []
    for ln_idx, line in enumerate(text.splitlines(), start=1):
        m = TAG_PATTERN.search(line)
        if m:
            try:
                rel = str(path.relative_to(root))
            except ValueError:
                rel = str(path)
            hits.append(
                TagHit(
                    file=rel,
                    line=ln_idx,
                    snippet=line.strip()[:200],
                    tag=m.group(0)[:200],
                )
            )
    return hits


def scan_path(target: Path, root: Path, skip_patterns: list[str]) -> list[TagHit]:
    if target.is_file():
        rel = str(target.relative_to(root)) if root in target.parents else str(target)
        if _should_skip(rel, skip_patterns):
            return []
        return scan_file(target, root)

    hits: list[TagHit] = []
    for f in target.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix not in DEFAULT_INCLUDE_EXTS:
            continue
        try:
            rel = str(f.relative_to(root))
        except ValueError:
            rel = str(f)
        if _should_skip(rel, skip_patterns):
            continue
        if "__pycache__" in rel or ".git/" in rel:
            continue
        hits.extend(scan_file(f, root))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scan de tags [NEEDS_PERPLEXITY_VALIDATION] no resueltos "
            "(DSC-V-001 enforcement parcial)."
        )
    )
    parser.add_argument(
        "paths", nargs="*", type=Path, default=[Path(".")],
        help="paths a scanear (default cwd recursivo)",
    )
    parser.add_argument(
        "--fail-on-found", action="store_true",
        help="exit 1 si encuentra tags (default: exit 0 report-only)",
    )
    parser.add_argument("--json", action="store_true",
                        help="output JSON en vez de texto")
    parser.add_argument("--skip", action="append", default=[],
                        help="patrones extra a skipear (path substring)")
    args = parser.parse_args()

    root = Path.cwd().resolve()
    skip_patterns = DEFAULT_SKIP_PATTERNS + args.skip

    all_hits: list[TagHit] = []
    for p in args.paths:
        target = (root / p).resolve() if not p.is_absolute() else p.resolve()
        if not target.exists():
            print(f"WARN: no existe: {target}", file=sys.stderr)
            continue
        all_hits.extend(scan_path(target, root, skip_patterns))

    if args.json:
        out = {"total_hits": len(all_hits), "hits": [asdict(h) for h in all_hits]}
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        if not all_hits:
            print("[ok] No hay tags [NEEDS_PERPLEXITY_VALIDATION] sin resolver.")
        else:
            print(
                f"Encontrados {len(all_hits)} claims con tag "
                f"[NEEDS_PERPLEXITY_VALIDATION]:\n"
            )
            for h in all_hits:
                print(f"  {h.file}:{h.line}  {h.tag}")
                print(f"    {h.snippet}")
                print()
            print(
                f"\nTotal: {len(all_hits)}. Estos claims requieren validacion "
                f"via Perplexity (DSC-V-001) antes de shipear a produccion. "
                f"Plan: Sprint S-CONTRATOS-001 T1 (decorator + validation_log)."
            )

    if args.fail_on_found and all_hits:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
