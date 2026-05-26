"""
tools/check_cowork_no_speculative_claims.py — Sprint COWORK-AUTO-DISCIPLINE-REAL-001 T2

F21 pattern detector runtime para outputs de Cowork.

Enforza DSC-S-016 (anti-fabricación causalidad sin grep): si un output de Cowork
afirma un claim que matchea uno de los F21_PATTERNS canonizados (P1-P10) pero
NO existe en la `history` reciente un tool call requerido que justifique el claim,
el detector marca violation y el hook puede bloquear.

API principal:

    from tools.check_cowork_no_speculative_claims import check_speculative_claims

    history = [
        {"type": "tool_call", "name": "git diff --stat", "result": "..."},
        {"type": "user_message", "content": "..."},
    ]

    violations = check_speculative_claims(cowork_output, history)
    # violations: list[dict] vacía si pasa, sino con detalles por match

Cada violation tiene shape:

    {
        "pattern_id": "diff_stats",
        "match": "11 files changed, +1879/-0",
        "missing_tool_call": ["git diff", "gh pr view", ...],
        "severity": "P1",
        "match_start": 145,
        "match_end": 172,
    }

CLI:

    python -m tools.check_cowork_no_speculative_claims \\
        --output-file output.txt \\
        --history-file history.json

    Exit code 0 si passed, 1 si hay violations, 2 si error de uso.

Doctrina:
- DSC-S-016: validación binaria pre-aserción
- DSC-G-008 v3 §4: deducir consecuencias materiales (cada violation va a embrion_memoria)
- Patrón "habla con código, no con texto": este es el código que enforza F21 anti-doctrina
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Importación robusta del catálogo F21
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from kernel.cowork_runtime.f21_patterns import (  # noqa: E402
    F21_PATTERNS,
    F21_PATTERNS_VERSION,
    output_parece_audit,
)

# ============================================================================
# CORE DETECTOR
# ============================================================================


def _flatten_history_to_text(history: list[dict[str, Any]]) -> str:
    """
    Aplana history (lista de tool_calls + user_messages) en un solo string para
    búsqueda de tool call names. Cada entry contribuye su `name` (si tool_call)
    o su `content` (si user_message).

    Soporta múltiples shapes de history:
    - {"type": "tool_call", "name": "git diff", ...}
    - {"type": "tool_result", "tool": "git diff", "content": "..."}
    - {"role": "assistant", "tool_calls": [{"name": "git_diff", ...}]}
    - strings sueltos
    """
    parts: list[str] = []
    for entry in history:
        if isinstance(entry, str):
            parts.append(entry)
            continue
        if not isinstance(entry, dict):
            continue

        # Shape 1: explicit name/content
        if "name" in entry:
            parts.append(str(entry["name"]))
        if "tool" in entry:
            parts.append(str(entry["tool"]))
        if "content" in entry:
            parts.append(str(entry["content"]))
        if "command" in entry:
            parts.append(str(entry["command"]))
        if "result" in entry:
            parts.append(str(entry["result"]))

        # Shape 2: nested tool_calls (Anthropic/OpenAI style)
        tool_calls = entry.get("tool_calls") or []
        if isinstance(tool_calls, list):
            for tc in tool_calls:
                if isinstance(tc, dict):
                    if "name" in tc:
                        parts.append(str(tc["name"]))
                    if "function" in tc and isinstance(tc["function"], dict):
                        parts.append(str(tc["function"].get("name", "")))
                        parts.append(str(tc["function"].get("arguments", "")))

    return " | ".join(parts)


def _tool_call_present(required_tools: list[str], history_text: str) -> str | None:
    """
    Returns el primer tool name de `required_tools` que aparece en `history_text`,
    o None si ninguno aparece (= violation).

    Match es case-insensitive y permite parciales (ej. "git diff" matchea
    "git diff --stat", "execute_sql" matchea "execute_sql_query", etc.).
    """
    history_lower = history_text.lower()
    for tool in required_tools:
        tool_lower = tool.lower()
        # Normalizar caracteres especiales que romperían substring match
        # (ej. "ls migrations/sql" debe matchear "ls migrations/sql/")
        if tool_lower in history_lower:
            return tool
    return None


def check_speculative_claims(
    cowork_output: str,
    history: list[dict[str, Any]] | None = None,
    patterns: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Aplica los F21_PATTERNS al output candidato + valida tool calls en history.

    Args:
        cowork_output: el texto candidato que Cowork va a enviar a Alfredo.
        history: lista de entries del último K turns (tool calls + user msgs).
                 Si None, equivale a history vacía (todo match = violation).
        patterns: lista alternativa de patterns (default = F21_PATTERNS).

    Returns:
        list[dict] de violations. Vacía si no hay violaciones.
        Cada violation tiene: pattern_id, match, missing_tool_call, severity,
        match_start, match_end.
    """
    if history is None:
        history = []
    if patterns is None:
        patterns = F21_PATTERNS

    history_text = _flatten_history_to_text(history)
    is_audit = output_parece_audit(cowork_output)

    violations: list[dict[str, Any]] = []

    # Strip bloques de código y blockquotes para no falsos positivos
    # (los patterns canónicos viven en bloques de código de specs/docs).
    text_for_match = re.sub(r"```[\s\S]*?```", "", cowork_output)
    text_for_match = re.sub(r"^>.*$", "", text_for_match, flags=re.MULTILINE)

    # Crear un mapeo de posiciones del texto stripped al texto original para
    # devolver match_start/end relativos al original (best effort).
    for pattern in patterns:
        # Skip patterns que solo aplican en audits si el output no parece audit
        if pattern.get("only_in_audit_outputs") and not is_audit:
            continue

        regex = pattern["regex"]
        required_tools = pattern.get("requires_tool_call", [])

        for match in re.finditer(regex, text_for_match, flags=re.MULTILINE):
            matched_text = match.group(0)
            # ¿Hay tool call que justifique este claim?
            tool_found = _tool_call_present(required_tools, history_text)
            if tool_found is None:
                violations.append(
                    {
                        "pattern_id": pattern["id"],
                        "match": matched_text,
                        "missing_tool_call": required_tools,
                        "severity": pattern.get("severity", "P1"),
                        "description": pattern.get("description", ""),
                        "match_start": match.start(),
                        "match_end": match.end(),
                    }
                )

    return violations


def format_violations_human(violations: list[dict[str, Any]]) -> str:
    """Formatea violations para output human-readable (CLI + hook feedback)."""
    if not violations:
        return "[COWORK_F21_PASS] sin claims especulativos detectados"

    lines = [
        f"[COWORK_F21_BLOCK] {len(violations)} violation(s) detected",
        f"  F21_PATTERNS version: {F21_PATTERNS_VERSION}",
        "",
    ]
    for i, v in enumerate(violations, 1):
        lines.append(f"  [{i}] severity={v['severity']} pattern_id={v['pattern_id']}")
        lines.append(f"      match: {v['match']!r}")
        lines.append(f"      missing_tool_call: {v['missing_tool_call']}")
        lines.append(f"      description: {v['description'][:140]}")
        lines.append("")
    lines.append("Reescribi después de ejecutar el tool call requerido para validar el claim.")
    return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================


def _load_history(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        if not sys.stdin.isatty():
            try:
                raw = sys.stdin.read()
                if raw.strip():
                    return json.loads(raw)
            except json.JSONDecodeError:
                return []
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
        description="F21 pattern detector — bloquea claims especulativos sin tool call previo.",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output candidato de Cowork (string). Si no, se lee --output-file o stdin.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Archivo con output candidato.",
    )
    parser.add_argument(
        "--history-file",
        type=Path,
        help="Archivo JSON con history (list[dict]).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Salida en JSON (default: humano).",
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
        print("error: no hay output candidato (usa --output, --output-file o stdin)", file=sys.stderr)
        return 2

    history = _load_history(args.history_file)
    violations = check_speculative_claims(cowork_output, history=history)

    if args.json:
        result = {
            "passed": len(violations) == 0,
            "violations": violations,
            "patterns_version": F21_PATTERNS_VERSION,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_violations_human(violations))

    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
