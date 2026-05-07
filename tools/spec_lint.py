#!/usr/bin/env python3
# tools/spec_lint.py
"""
Linter de specs de sprint (DSC-G-008 v2 + DSC-G-012 + DSC-G-017).

Contrato ejecutable que enforza estructura minima en specs de sprint y, en modo
estricto, exige perfil_riesgo per tarea (DSC-G-012) y declaracion de contratos
ejecutables si el sprint produce DSCs (DSC-G-017).

Modos:
    default  — errores de estructura, warnings de DSC-G-012/017 (legacy-friendly)
    --strict — todos los warnings se convierten en errores
    auto-strict — si el spec contiene `lint_strict: true` en frontmatter o linea
                  `<!-- lint_strict -->`, modo estricto se activa automaticamente

CLI:
    python tools/spec_lint.py bridge/sprints_propuestos/sprint_xyz.md
    python tools/spec_lint.py --strict path/to/spec.md
    python tools/spec_lint.py bridge/sprints_propuestos/  # recursive

Exit code:
    0  = sin errores (warnings ok)
    1  = al menos un error
    2  = error de uso o archivo no existe
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


# Perfiles de riesgo canonicos (DSC-G-012)
PERFILES_VALIDOS = {
    "read-only",
    "write-safe",
    "write-risky",
    "requiere-coordinacion-humana",
}


@dataclass
class Finding:
    severity: str  # "error" | "warning"
    rule: str
    line: int  # 0-indexed; 0 si no aplica
    message: str

    def __str__(self) -> str:
        return f"  [{self.severity:7}] line {self.line:>4}  {self.rule}: {self.message}"


@dataclass
class LintResult:
    file: str
    strict_mode: bool
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warning"]

    def passed(self) -> bool:
        return not self.errors


# ---- Reglas individuales -----------------------------------------------------


def _check_title(lines: list[str]) -> list[Finding]:
    if not lines:
        return [Finding("error", "structure.title", 0, "spec vacio")]

    # Skip YAML frontmatter si arranca con ---
    idx = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                idx = i + 1
                break
        else:
            return [Finding("error", "structure.frontmatter",
                            1, "frontmatter YAML abierto sin cierre '---'")]

    # Skip HTML comments (<!-- ... -->) que pueden contener marcadores como
    # <!-- lint_strict --> antes del titulo.
    while idx < len(lines):
        ln = lines[idx].strip()
        if not ln:
            idx += 1
            continue
        if ln.startswith("<!--"):
            if "-->" in ln:
                idx += 1
                continue
            idx += 1
            while idx < len(lines) and "-->" not in lines[idx]:
                idx += 1
            idx += 1
            continue
        break

    first = lines[idx] if idx < len(lines) else ""
    if not first.lstrip().startswith("# "):
        return [Finding(
            "error",
            "structure.title",
            idx + 1,
            f"primera linea no-vacia post-frontmatter/comments debe ser titulo H1 ('# ...'). got: {first[:80]!r}",
        )]
    return []


def _check_field(text: str, label: str, rule: str) -> list[Finding]:
    """Busca **Label:** algo o Label: algo en cualquier linea."""
    pattern = r"\*?\*?" + re.escape(label) + r"\s*:\*?\*?\s*\S"
    if re.search(pattern, text, flags=re.IGNORECASE):
        return []
    return [Finding(
        "error",
        rule,
        0,
        f"falta campo obligatorio '{label}:' (formato '**{label}:** valor' o 'Label: valor')",
    )]


def _check_field_any(text: str, labels: list[str], rule: str) -> list[Finding]:
    """Pasa si CUALQUIER label existe."""
    for lab in labels:
        if not _check_field(text, lab, rule):
            return []
    return [Finding(
        "error",
        rule,
        0,
        f"falta campo obligatorio. Aceptados: {labels}",
    )]


def _check_section(lines: list[str], section_pattern: str, rule: str,
                   severity: str = "error") -> list[Finding]:
    """Verifica que exista al menos un heading que matchea section_pattern."""
    # Nota: NO usar f-string aqui — `{1,6}` se interpolaria como tupla en f-string raw.
    pat = re.compile(r"^#{1,6}\s+.*" + section_pattern, flags=re.IGNORECASE)
    for ln in lines:
        if pat.match(ln):
            return []
    return [Finding(
        severity,
        rule,
        0,
        f"falta seccion que matchea /{section_pattern}/",
    )]


def _check_section_any(lines: list[str], section_patterns: list[str],
                        rule: str) -> list[Finding]:
    """Pasa si CUALQUIER seccion matchea."""
    for pat in section_patterns:
        if not _check_section(lines, pat, rule):
            return []
    return [Finding(
        "error",
        rule,
        0,
        f"falta seccion. Patterns aceptados: {section_patterns}",
    )]


def _detect_strict_mode(text: str) -> bool:
    """Activacion automatica de modo estricto si el spec lo declara."""
    if re.search(r"^\s*lint_strict\s*:\s*true", text, flags=re.MULTILINE | re.IGNORECASE):
        return True
    if re.search(r"<!--\s*lint_strict\s*-->", text, flags=re.IGNORECASE):
        return True
    return False


def _find_task_headings(lines: list[str]) -> list[tuple[int, str]]:
    """Devuelve lista de (line_idx_1based, heading_text) para cada heading de tarea."""
    pat = re.compile(r"^#{2,6}\s+Tarea\s+", flags=re.IGNORECASE)
    return [(i + 1, ln.strip()) for i, ln in enumerate(lines) if pat.match(ln)]


def _check_perfil_riesgo_per_task(lines: list[str], strict: bool) -> list[Finding]:
    """DSC-G-012: cada tarea debe tener perfil_riesgo en uno de los valores canonicos."""
    severity = "error" if strict else "warning"
    findings: list[Finding] = []
    headings = _find_task_headings(lines)
    if not headings:
        return findings

    n = len(lines)
    # Acepta cualquier combinacion de **, :, espacios, ` entre label y valor.
    perfil_pat = re.compile(
        r"(?:perfil[_\s-]?riesgo|risk[_\s-]?profile|perfil)"
        r"[\*\s:`]+"
        r"(read-only|write-safe|write-risky|requiere-coordinacion-humana)",
        flags=re.IGNORECASE,
    )
    for idx, (start_line, heading) in enumerate(headings):
        end_line = headings[idx + 1][0] - 1 if idx + 1 < len(headings) else n
        block = "\n".join(lines[start_line - 1:end_line])
        match = perfil_pat.search(block)
        if not match:
            findings.append(Finding(
                severity,
                "dsc-g-012.perfil_riesgo_missing",
                start_line,
                f"tarea {heading[:60]!r} no declara perfil_riesgo "
                f"(valores: {sorted(PERFILES_VALIDOS)})",
            ))
        else:
            value = match.group(1).lower()
            if value not in PERFILES_VALIDOS:
                findings.append(Finding(
                    "error",
                    "dsc-g-012.perfil_riesgo_invalid",
                    start_line + block[:match.start()].count("\n"),
                    f"perfil_riesgo invalido: {value!r}. valores validos: {sorted(PERFILES_VALIDOS)}",
                ))
    return findings


def _check_dsc_contracts_section(text: str, strict: bool) -> list[Finding]:
    """DSC-G-017: si el spec menciona producir DSCs, debe tener seccion de contratos."""
    severity = "error" if strict else "warning"
    findings: list[Finding] = []
    produces_dscs = bool(re.search(
        r"\b(produce|produc[ie]r|firma|firmar|canoniz[ae]r?|nuevo[s]? DSC)s?\b.{0,80}DSC-",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    ))
    has_contract_section = bool(re.search(
        r"^#{2,6}\s+.*(?:contrato[s]?\s+ejecutable[s]?|dsc-as-contract|"
        r"contratos\s+adjuntos|contratos\s+que\s+(?:ana[dD]e|adjunta))",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    ))
    if produces_dscs and not has_contract_section:
        findings.append(Finding(
            severity,
            "dsc-g-017.contracts_section_missing",
            0,
            "spec menciona producir DSCs pero no tiene seccion '## Contratos ejecutables' "
            "(DSC-G-017 exige enforzamiento adjunto)",
        ))
    return findings


def _check_criterios_cierre_specifics(lines: list[str], strict: bool) -> list[Finding]:
    """DSC-G-010: criterios de cierre verde deben ser reproducibles/verificables."""
    severity = "warning"
    findings: list[Finding] = []
    pat = re.compile(r"^#{2,6}\s+.*criterios?\s+(?:de\s+)?cierre", flags=re.IGNORECASE)
    in_section = False
    section_start = 0
    section_lines: list[str] = []
    for i, ln in enumerate(lines, start=1):
        if pat.match(ln):
            in_section = True
            section_start = i
            section_lines = []
            continue
        if in_section:
            if re.match(r"^#{1,6}\s+", ln) and not pat.match(ln):
                break
            section_lines.append(ln)
    if in_section and section_lines:
        joined = "\n".join(section_lines).lower()
        has_reproducible = bool(re.search(
            r"(comando|command|exit\s+code|test|pytest|curl|http|"
            r"smoke|reporte|artifact|json|coverage)",
            joined,
        ))
        if not has_reproducible:
            findings.append(Finding(
                severity,
                "dsc-g-010.cierre_no_reproducible",
                section_start,
                "criterios de cierre no mencionan comando/test/artifact reproducible "
                "(DSC-G-010: cierre verde requiere verificacion E2E)",
            ))
    return findings


# ---- Driver ------------------------------------------------------------------


def lint_file(path: Path, force_strict: bool = False) -> LintResult:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    auto_strict = _detect_strict_mode(text)
    strict = force_strict or auto_strict

    result = LintResult(file=str(path), strict_mode=strict)

    # Reglas de estructura (siempre errores)
    result.findings.extend(_check_title(lines))
    result.findings.extend(_check_field(text, "Estado", "structure.estado"))
    result.findings.extend(_check_field_any(
        text,
        ["Objetivo Maestro", "Objetivo", "Goal", "Meta"],
        "structure.objetivo",
    ))
    result.findings.extend(_check_section(
        lines, r"tareas?\b", "structure.tareas_section",
    ))
    result.findings.extend(_check_section_any(
        lines,
        [
            r"criterios?\s+(?:de\s+)?cierre",
            r"definition\s+of\s+done",
            r"deliverable[s]?\b",
            r"entreg(?:able|a)[s]?\b",
            r"resultado[s]?\s+esperado[s]?",
        ],
        "structure.criterios_cierre",
    ))

    # Reglas DSC (warning por default, error si strict)
    result.findings.extend(_check_perfil_riesgo_per_task(lines, strict))
    result.findings.extend(_check_dsc_contracts_section(text, strict))
    result.findings.extend(_check_criterios_cierre_specifics(lines, strict))

    return result


def lint_path(path: Path, force_strict: bool) -> list[LintResult]:
    if path.is_file() and path.suffix == ".md":
        return [lint_file(path, force_strict)]
    if path.is_dir():
        results: list[LintResult] = []
        for f in sorted(path.rglob("sprint_*.md")):
            results.append(lint_file(f, force_strict))
        return results
    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Linter de specs de sprint (DSC-G-008 v2 + DSC-G-012 + DSC-G-017). "
            "Contrato ejecutable. Pre-commit hook adjunto."
        )
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="archivos .md o directorios con sprint_*.md",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="forzar modo estricto: warnings -> errores",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="output JSON en vez de texto",
    )
    args = parser.parse_args()

    all_results: list[LintResult] = []
    for p in args.paths:
        if not p.exists():
            print(f"ERROR: no existe: {p}", file=sys.stderr)
            return 2
        all_results.extend(lint_path(p, args.strict))

    total_errors = sum(len(r.errors) for r in all_results)
    total_warnings = sum(len(r.warnings) for r in all_results)

    if args.json:
        out = {
            "files_linted": len(all_results),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "results": [
                {
                    "file": r.file,
                    "strict_mode": r.strict_mode,
                    "errors": [asdict(f) for f in r.errors],
                    "warnings": [asdict(f) for f in r.warnings],
                }
                for r in all_results
            ],
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        for r in all_results:
            mode = "strict" if r.strict_mode else "lenient"
            if not r.findings:
                print(f"[ok]   {r.file} ({mode})")
                continue
            print(f"[{'ERR' if r.errors else 'warn'}] {r.file} ({mode})")
            for f in r.findings:
                print(f)
        print(
            f"\nResumen: {len(all_results)} specs, "
            f"{total_errors} errores, {total_warnings} warnings."
        )

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
