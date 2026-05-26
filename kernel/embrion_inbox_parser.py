"""
kernel/embrion_inbox_parser.py — Parser determinista de comandos del inbox.

Sprint EMBRION-NEEDS-002 Tarea 5 (Embrión-Daddy bidireccional, implementación).
Spec firmado: discovery_forense/SPECS/EMBRION_DADDY_BIDIRECCIONAL_v1.md (PR #81).
Kickoff: bridge/cowork_to_manus_T5_EMBRION_DADDY_KICKOFF_2026_05_11.md
Autor: Hilo Ejecutor 2 (manus_hilo_ejecutor_2).

Doctrina:
  - CERO uso de LLM. Solo regex + split + dataclass.
  - Comandos desconocidos → valid=False, reason='unknown_command:<comando>'.
  - NO se acepta como /context por default si el comando no está reconocido.

Comandos soportados (sincronizados con migrations/sql/0012_embrion_inbox.sql):
  /context <texto>             — Inyectar contexto al embrión.
  /override <pid> <param=val>  — Modificar parámetro de un proposal existente.
  /help                        — Ayuda inline. Sin payload.
  /status                      — Estado actual del embrión. Sin payload.
  /answer <texto>              — Responder a pregunta abierta del embrión.
  /feedback <texto>            — Feedback contextual sobre una propuesta.

Comandos NO en whitelist:
  - Cualquier `/foo` no listado → valid=False, reason='unknown_command:/foo'
  - Texto libre sin slash → valid=False, reason='not_a_command'

CA3 cubierto (kickoff §3):
  3.1 ParsedCommand dataclass con (comando, payload, valid, reason).
  3.2 Cero imports de openai/anthropic/kernel.llm_*.
  3.3 Comandos desconocidos → valid=False explícito.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

# Whitelist canónica — sincronizada con CHECK constraint en 0012_embrion_inbox.sql
KNOWN_COMMANDS = frozenset(
    {
        "/context",
        "/override",
        "/help",
        "/status",
        "/answer",
        "/feedback",
    }
)

# Comandos que requieren payload obligatorio (no pueden ir vacíos)
COMMANDS_WITH_REQUIRED_PAYLOAD = frozenset(
    {
        "/context",
        "/override",
        "/answer",
        "/feedback",
    }
)

# Comandos sin payload (cualquier texto extra se ignora)
COMMANDS_WITHOUT_PAYLOAD = frozenset(
    {
        "/help",
        "/status",
    }
)

# Regex auxiliares
# /override <uuid> <param=value>[ <param=value>...]
# UUID flexible: acepta uuid v4 estándar o ids cortos alfanuméricos (>=8 chars)
_OVERRIDE_PROPOSAL_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,}$")
_OVERRIDE_PARAM_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]{0,63})=(.+)$")

# Anti-spoof: detecta líderes/sufijos no-imprimibles raros
_PRINTABLE_RE = re.compile(r"^[\x20-\x7E\u00C0-\u017F\u0080-\uFFFF\s]*$")


@dataclass
class ParsedCommand:
    """Resultado del parseo. Determinista, serializable a jsonb."""

    comando: str = ""  # texto crudo del comando (ej "/override")
    payload: dict = field(default_factory=dict)
    valid: bool = False
    reason: Optional[str] = None  # explicación legible si valid=False
    raw_text: str = ""  # texto original (útil para audit)


def _normalize(text: str) -> str:
    """Strip + lowercase del primer token (comando). Mantiene case del payload."""
    return text.strip()


def parse_command(text: str) -> ParsedCommand:
    """Parsear un texto crudo del inbox a ParsedCommand.

    Cero LLM. Determinista. Idempotente.

    Args:
        text: Texto crudo enviado por Daddy via Telegram.

    Returns:
        ParsedCommand con valid=True si reconocido + payload bien formado,
        valid=False con reason explícita en caso contrario.

    Comportamiento canónico:
      - Texto vacío o solo whitespace → valid=False, reason='empty_text'.
      - No empieza con '/' → valid=False, reason='not_a_command'.
      - Primer token no en KNOWN_COMMANDS → valid=False, reason='unknown_command:<token>'.
      - Comando requiere payload pero está vacío → valid=False, reason='missing_payload:<cmd>'.
      - /override mal formado → valid=False, reason='override_malformed:<detalle>'.
      - Caracteres no-imprimibles raros (anti-spoof) → valid=False, reason='non_printable'.
    """
    pc = ParsedCommand(raw_text=text if isinstance(text, str) else "")

    if not isinstance(text, str):
        pc.reason = "non_string_input"
        return pc

    norm = _normalize(text)

    if not norm:
        pc.reason = "empty_text"
        return pc

    if not _PRINTABLE_RE.match(norm):
        pc.reason = "non_printable"
        return pc

    if not norm.startswith("/"):
        pc.reason = "not_a_command"
        return pc

    parts = norm.split(maxsplit=1)
    cmd = parts[0].lower()
    rest = parts[1].strip() if len(parts) > 1 else ""

    if cmd not in KNOWN_COMMANDS:
        pc.comando = cmd
        pc.reason = f"unknown_command:{cmd}"
        return pc

    pc.comando = cmd

    # ── Comandos sin payload ──
    if cmd in COMMANDS_WITHOUT_PAYLOAD:
        pc.payload = {}
        pc.valid = True
        return pc

    # ── Comandos con payload obligatorio ──
    if not rest:
        pc.reason = f"missing_payload:{cmd}"
        return pc

    if cmd == "/override":
        return _parse_override(pc, rest)

    # /context, /answer, /feedback → payload libre (texto)
    pc.payload = {"text": rest}
    pc.valid = True
    return pc


def _parse_override(pc: ParsedCommand, rest: str) -> ParsedCommand:
    """Parsear payload específico de /override.

    Formato: <proposal_id> <param1=value1> [<param2=value2> ...]

    Reglas:
      - Primer token = proposal_id (>=8 chars alfanuméricos/dashes/underscores).
      - Tokens subsecuentes = pares param=value (regex _OVERRIDE_PARAM_RE).
      - Mínimo 1 param=value requerido. 0 params → malformed.
    """
    tokens = rest.split()
    if len(tokens) < 2:
        pc.reason = "override_malformed:need_proposal_id_and_at_least_one_param"
        return pc

    proposal_id = tokens[0]
    if not _OVERRIDE_PROPOSAL_ID_RE.match(proposal_id):
        pc.reason = f"override_malformed:invalid_proposal_id:{proposal_id[:32]}"
        return pc

    params = {}
    for raw in tokens[1:]:
        m = _OVERRIDE_PARAM_RE.match(raw)
        if not m:
            pc.reason = f"override_malformed:bad_param_pair:{raw[:32]}"
            return pc
        key, value = m.group(1), m.group(2)
        params[key] = value

    if not params:
        pc.reason = "override_malformed:no_params"
        return pc

    pc.payload = {
        "proposal_id": proposal_id,
        "params": params,
    }
    pc.valid = True
    return pc
