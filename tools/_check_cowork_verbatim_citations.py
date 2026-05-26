"""
tools/_check_cowork_verbatim_citations.py — Sprint COWORK-AUTO-DISCIPLINE-REAL-001 T3

Verbatim citation enforcement: si Cowork cita un substring ≥7 chars que parece
hash/path/schema/version/identificador, validar que ese exacto substring apareció
verbatim en algún tool result MCP/Bash en los last K=10 turns. Si no aparece →
violation P1 (fabrication).

El underscore prefix del filename (`_check_*`) indica que es un módulo interno
auxiliar, llamado solo por el hook + tests (no por humanos en CLI cotidiano).

Heurísticas para detectar "citation candidates" (substrings que parecen
identificadores fabricables):

1. Hex hashes (≥7 chars hex): commits, blob hashes
2. UUID-like (32 chars hex con dashes opcionales)
3. File paths con extensión: foo/bar.py, migrations/sql/0027_x.sql
4. Schema-like: table.column_name, snake_case_identifiers ≥10 chars
5. ISO timestamps: 2026-05-12T15:50:18Z
6. PR/Issue refs: PR #98, #114, issuecomment-NNNN
7. Version strings: v0.84.8, 1.2.3-sprint-memento

API principal:

    from tools._check_cowork_verbatim_citations import check_verbatim_citations

    history = [{"type": "tool_result", "content": "..."}]
    violations = check_verbatim_citations(cowork_output, history)

Each violation:

    {
        "citation": "676797d",
        "type": "hex_hash",
        "match_start": 145,
        "match_end": 152,
        "severity": "P1",
    }

CLI:

    python -m tools._check_cowork_verbatim_citations \\
        --output-file output.txt \\
        --history-file history.json

Exit 0 si pass, 1 si violations.

Doctrina:
- DSC-S-016: si Cowork cita hashes/paths/schemas que no aparecen en history,
  está fabricando. Patrón mata F21 reincidente F2/F21 sobre commits inventados.
- Anti-Goodhart: NO marcar comunes como "main"/"DSC-G-008"/"PR #N" si N existe
  en history como número (solo el formato verbatim cuenta).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# ============================================================================
# REGEXES — patterns que detectan citation candidates en outputs Cowork
# ============================================================================

# Cada citation pattern tiene id + regex + tipo semántico
CITATION_PATTERNS: list[dict[str, Any]] = [
    {
        "id": "hex_hash",
        "regex": r"\b[0-9a-f]{7,40}\b",
        "type": "hex_hash",
        "description": "Hex hash ≥7 chars (commits, blobs, etc.)",
    },
    {
        "id": "iso_timestamp",
        "regex": r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?\b",
        "type": "iso_timestamp",
        "description": "ISO 8601 timestamp con hora",
    },
    {
        "id": "issuecomment",
        "regex": r"\bissuecomment-\d{6,}\b",
        "type": "issuecomment",
        "description": "GitHub issuecomment-NNNNNNN reference",
    },
    {
        "id": "file_path",
        "regex": r"\b(?:[\w.-]+/){1,}[\w.-]+\.(py|sql|md|json|yaml|yml|toml|ts|tsx|js|jsx|sh|html|css)\b",
        "type": "file_path",
        "description": "Path relativo a archivo con extensión común",
    },
    {
        "id": "schema_dotted",
        "regex": r"\bpublic\.\w{4,}\b",
        "type": "schema_dotted",
        "description": "Schema.table dotted identifier (public.foo_bar)",
    },
    {
        "id": "version_string",
        "regex": r"\bv?\d+\.\d+\.\d+(-[\w.]+)?\b",
        "type": "version_string",
        "description": "Semver string (v0.84.8-sprint-memento, 1.2.3)",
    },
    {
        "id": "long_snake_case",
        "regex": r"\b[a-z]+(?:_[a-z0-9]+){2,}\b",
        "type": "long_snake_case",
        "description": "snake_case identifier con ≥3 segmentos (cowork_protocolo_invocaciones)",
    },
]


# Allowlist: substrings comunes que NO se consideran fabricables aunque matcheen
# (palabras de uso diario en specs/docs). Cualquier match con substring en esta
# lista se ignora.
COMMON_ALLOWLIST: tuple[str, ...] = (
    "main",
    "master",
    "develop",
    "true",
    "false",
    "null",
    "hotmail.com",
    "manus.ai",
    "manus.im",
    "github.com",
    "supabase",
    "railway.app",
    "el-monstruo",
    "kernel/cowork_runtime",  # se cita constantemente en specs cowork
    "tools/cowork_guardian",
    "migrations/sql",
    "bridge/cowork_to_manus",
    "bridge/manus_to_cowork",
    "discovery_forense",
    "f21_patterns.py",  # auto-referencia al módulo nuevo
    "antipatterns.py",
    "pre_response_hook.py",
    "rule_reinjection.py",
    "session_memory.py",
    "drift_detector.py",
    "companion_agent.py",
    "check_cowork_no_speculative_claims.py",
    "_check_cowork_verbatim_citations.py",
)


def _is_allowlisted(citation: str) -> bool:
    """True si la citation está en la allowlist (no se considera fabricable)."""
    citation_lower = citation.lower()
    for allow in COMMON_ALLOWLIST:
        if allow.lower() in citation_lower:
            return True
    return False


# ============================================================================
# HISTORY FLATTENING — extrae texto verbatim de tool results
# ============================================================================


def _flatten_history_verbatim(history: list[dict[str, Any]]) -> str:
    """
    Aplana history extrayendo TODO el texto verbatim de tool results + user msgs.
    A diferencia del detector F21 (que busca tool *names*), este busca substrings
    *content* exactos.
    """
    parts: list[str] = []
    for entry in history:
        if isinstance(entry, str):
            parts.append(entry)
            continue
        if not isinstance(entry, dict):
            continue

        for key in ("content", "result", "output", "stdout", "stderr", "text"):
            val = entry.get(key)
            if val is not None:
                parts.append(str(val))

        # Recursión a tool_calls anidados
        tool_calls = entry.get("tool_calls") or []
        if isinstance(tool_calls, list):
            for tc in tool_calls:
                if isinstance(tc, dict):
                    if "function" in tc and isinstance(tc["function"], dict):
                        parts.append(str(tc["function"].get("arguments", "")))
                    for key in ("content", "result", "output"):
                        if key in tc:
                            parts.append(str(tc[key]))
    return "\n".join(parts)


# ============================================================================
# CORE CHECKER
# ============================================================================


def check_verbatim_citations(
    cowork_output: str,
    history: list[dict[str, Any]] | None = None,
    min_citation_length: int = 7,
    severity: str = "P1",
) -> list[dict[str, Any]]:
    """
    Detecta citation candidates en `cowork_output` que NO aparecen verbatim en
    `history` (tool results last K=10 turns típicamente).

    Args:
        cowork_output: texto candidato.
        history: lista de entries con tool results.
        min_citation_length: longitud mínima de substring para considerar
                             "citation" (default 7 — corresponde a hex hash mínimo).
        severity: severidad de la violation (default P1).

    Returns:
        list[dict] de violations. Vacía si todas las citations son verificables.
    """
    if history is None:
        history = []

    history_text = _flatten_history_verbatim(history)

    # Strip bloques de código del output (specs/migrations contienen pseudocódigo
    # que NO es citation real).
    text_for_match = re.sub(r"```[\s\S]*?```", "", cowork_output)
    text_for_match = re.sub(r"^>.*$", "", text_for_match, flags=re.MULTILINE)

    violations: list[dict[str, Any]] = []
    seen_violations: set[tuple[str, str]] = set()  # dedupe por (citation, type)

    for pattern in CITATION_PATTERNS:
        for match in re.finditer(pattern["regex"], text_for_match, flags=re.IGNORECASE | re.MULTILINE):
            citation = match.group(0)
            if len(citation) < min_citation_length:
                continue
            if _is_allowlisted(citation):
                continue

            # ¿Aparece verbatim en history?
            if citation in history_text:
                continue
            # Case-insensitive fallback (algunos tool results vienen lowercased)
            if citation.lower() in history_text.lower():
                continue

            dedup_key = (citation, pattern["type"])
            if dedup_key in seen_violations:
                continue
            seen_violations.add(dedup_key)

            violations.append(
                {
                    "citation": citation,
                    "type": pattern["type"],
                    "pattern_id": pattern["id"],
                    "description": pattern["description"],
                    "severity": severity,
                    "match_start": match.start(),
                    "match_end": match.end(),
                }
            )

    return violations


def format_violations_human(violations: list[dict[str, Any]]) -> str:
    """Formatea violations human-readable (CLI + hook feedback)."""
    if not violations:
        return "[COWORK_VERBATIM_PASS] sin citations fabricadas detectadas"

    lines = [
        f"[COWORK_VERBATIM_BLOCK] {len(violations)} citation(s) sin respaldo verbatim en history",
        "",
    ]
    for i, v in enumerate(violations, 1):
        lines.append(f"  [{i}] severity={v['severity']} type={v['type']} citation={v['citation']!r}")
        lines.append(f"      {v['description']}")
        lines.append("")
    lines.append("Reescribi: o cita exactamente lo que aparece en un tool result, o ejecuta el tool call.")
    return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================


def _load_history(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    if not path.exists():
        print(f"warning: history file no existe: {path}", file=sys.stderr)
        return []
    with path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"error parsing history JSON: {e}", file=sys.stderr)
            return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verbatim citation enforcement — bloquea citas fabricadas sin respaldo en history.",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output candidato (string). Si no, --output-file o stdin.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Archivo con output candidato.",
    )
    parser.add_argument(
        "--history-file",
        type=Path,
        help="JSON con history (list[dict]).",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=7,
        help="Longitud mínima para considerar citation (default 7).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Salida JSON (default humano).",
    )
    args = parser.parse_args(argv)

    if args.output:
        cowork_output = args.output
    elif args.output_file:
        if not args.output_file.exists():
            print(f"error: output file no existe: {args.output_file}", file=sys.stderr)
            return 2
        cowork_output = args.output_file.read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        cowork_output = sys.stdin.read()
    else:
        print("error: pasa --output, --output-file o stdin", file=sys.stderr)
        return 2

    history = _load_history(args.history_file)
    violations = check_verbatim_citations(
        cowork_output,
        history=history,
        min_citation_length=args.min_length,
    )

    if args.json:
        print(json.dumps({"passed": len(violations) == 0, "violations": violations}, indent=2, ensure_ascii=False))
    else:
        print(format_violations_human(violations))

    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
