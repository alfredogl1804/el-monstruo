"""
kernel/embrion_inbox_sanitizer.py — Sanitización determinista de payloads del inbox.

Sprint EMBRION-NEEDS-002 Tarea 5 (CA4).
Kickoff: bridge/cowork_to_manus_T5_EMBRION_DADDY_KICKOFF_2026_05_11.md
Autor: Hilo Ejecutor 2 (manus_hilo_ejecutor_2).

Doctrina:
  - CERO uso de LLM. Solo regex + heurísticas determinísticas.
  - Defense-in-depth: el parser ya valida formato; el sanitizer valida intención
    y limpia el contenido antes de entregárselo al embrión.
  - Falla cerrada: si el sanitizer marca 'attack' o 'jailcheck' con alta
    confianza, embrion_loop rechaza el mensaje (no lo ignora silenciosamente).

Función principal:
  sanitize_daddy_payload(parsed_cmd) -> SanitizedPayload
    Devuelve payload limpio + intent_class + confidence.

Intent classes:
  - safe         : payload normal de Daddy (default si nada sospechoso).
  - attack       : SQL injection, command injection, exfiltración.
  - jailbreak    : intento de modificar comportamiento del embrión via prompt.
  - uncertain    : señales débiles, NO bloquea pero se loguea para revisión.

CA4 cubierto (kickoff §4):
  4.1 sanitize_daddy_payload(parsed_cmd) → texto limpio + intent_class.
  4.2 Fixture de 10+ ataques (en tests/test_embrion_inbox_sanitizer.py).
  4.3 Recall ≥90% en detección de ataques.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from kernel.embrion_inbox_parser import ParsedCommand


# ─── Patrones de ataque ────────────────────────────────────────────────────

# SQL injection
_SQL_INJECTION_PATTERNS = [
    re.compile(r"(?i)\b(union\s+select|select\s+.+\s+from|drop\s+table|truncate\s+table|delete\s+from\s+\w)"),
    re.compile(r"(?i)\b(or|and)\s+\d+\s*=\s*\d+\s*(--|#|/\*)"),
    re.compile(r"(?i)(';\s*(drop|delete|truncate|update|insert)\b)"),
    re.compile(r"(?i)\bxp_cmdshell\b"),
    re.compile(r"(?i)\b(information_schema|pg_catalog|pg_user|pg_shadow)\b"),
]

# Command injection (shell / Python eval)
_COMMAND_INJECTION_PATTERNS = [
    re.compile(r"(?i)(\||;|&&|\$\(|`)\s*(curl|wget|nc|bash|sh|python|eval|exec|rm\s+-rf)\b"),
    re.compile(r"(?i)\b(os\.system|subprocess\.|eval\s*\(|exec\s*\()"),
    re.compile(r"(?i)/(etc|root|home)/[a-zA-Z0-9_./-]+"),
    re.compile(r"(?i)\b(sudo|chmod|chown)\s+"),
]

# Exfiltración (intentar leer secrets / env)
_EXFIL_PATTERNS = [
    re.compile(r"(?i)\b(env|environ|SUPABASE_\w+|TELEGRAM_\w+|OPENAI_\w+|ANTHROPIC_\w+|GEMINI_\w+|XAI_\w+|AWS_\w+)\b"),
    re.compile(r"(?i)\b(API_KEY|SERVICE_KEY|SECRET_KEY|PRIVATE_KEY|BEARER|sb_secret_)"),
    re.compile(r"(?i)\b(printenv|env\s*\|)"),
]

# Jailbreak: intentos de modificar comportamiento del embrión
_JAILBREAK_PATTERNS = [
    re.compile(r"(?i)\b(ignore|forget|disregard)\s+(previous|all|your)\s+(instructions?|rules?|prompts?|context|memory)"),
    re.compile(r"(?i)\b(act\s+as|you\s+are\s+now|pretend\s+to\s+be|roleplay\s+as)\s+"),
    re.compile(r"(?i)\b(system\s+prompt|developer\s+mode|jailbreak|DAN|do\s+anything\s+now)\b"),
    re.compile(r"(?i)\b(override\s+(?:your|the)\s+(?:rules|policy|safety|guardrails?))"),
    re.compile(r"(?i)\b(reveal|disclose|print|show)\s+(?:your|the)\s+(prompt|instructions|rules|policies)"),
]

# Patrones débiles (uncertain, no bloquea)
_UNCERTAIN_PATTERNS = [
    re.compile(r"(?i)\b(http://|https://)[a-zA-Z0-9.\-]+/[^\s]{20,}"),  # URLs largas sospechosas
    re.compile(r"(?i)<script\b"),
    re.compile(r"(?i)\b(base64|hex)\s*(decode|encode)\("),
]


# ─── Límites ─────────────────────────────────────────────────────────────

PAYLOAD_MAX_LENGTH = 2000  # caracteres máximos en text payloads
MIN_CONFIDENCE_FOR_BLOCK = 0.7  # si confidence ≥0.7 → bloquear; <0.7 → uncertain


@dataclass
class SanitizedPayload:
    """Resultado de la sanitización."""
    payload: dict = field(default_factory=dict)
    intent_class: str = "safe"   # safe | attack | jailbreak | uncertain
    confidence: float = 0.0       # 0.0..1.0
    signals: List[str] = field(default_factory=list)  # patrones que matchearon
    rejected: bool = False
    rejection_reason: str = ""
    truncated: bool = False


def _scan_patterns(text: str, patterns: List[re.Pattern], label: str) -> List[str]:
    """Devuelve los nombres de los patrones que matchean."""
    matches = []
    for i, pat in enumerate(patterns):
        if pat.search(text):
            matches.append(f"{label}:{i}")
    return matches


def _truncate(text: str, max_len: int = PAYLOAD_MAX_LENGTH) -> tuple[str, bool]:
    if len(text) <= max_len:
        return text, False
    return text[:max_len], True


def sanitize_daddy_payload(parsed: ParsedCommand) -> SanitizedPayload:
    """Sanitizar payload de un ParsedCommand válido.

    Args:
        parsed: ParsedCommand del parser. Debe tener valid=True; si no, se
            devuelve un SanitizedPayload rejected sin escanear.

    Returns:
        SanitizedPayload con intent_class, confidence, signals, payload limpio.
    """
    sp = SanitizedPayload()

    if not parsed.valid:
        sp.rejected = True
        sp.rejection_reason = f"parser_invalid:{parsed.reason or 'unknown'}"
        sp.intent_class = "uncertain"
        return sp

    # Extraer texto-objetivo del payload
    # /context, /answer, /feedback → payload['text']
    # /override → payload['proposal_id'] + payload['params'] (escanear todo concatenado)
    # /help, /status → payload vacío, nada que sanitizar
    payload = dict(parsed.payload or {})

    if not payload:
        sp.payload = payload
        sp.intent_class = "safe"
        sp.confidence = 0.0
        return sp

    target_text_parts = []
    if "text" in payload:
        text, was_truncated = _truncate(payload["text"])
        payload["text"] = text
        sp.truncated = was_truncated
        target_text_parts.append(text)
    if "proposal_id" in payload:
        target_text_parts.append(str(payload["proposal_id"]))
    if "params" in payload and isinstance(payload["params"], dict):
        for k, v in payload["params"].items():
            target_text_parts.append(f"{k}={v}")

    target_text = " | ".join(target_text_parts)

    # Escaneo de patrones
    sql_hits = _scan_patterns(target_text, _SQL_INJECTION_PATTERNS, "sql")
    cmd_hits = _scan_patterns(target_text, _COMMAND_INJECTION_PATTERNS, "cmd")
    exfil_hits = _scan_patterns(target_text, _EXFIL_PATTERNS, "exfil")
    jb_hits = _scan_patterns(target_text, _JAILBREAK_PATTERNS, "jb")
    unc_hits = _scan_patterns(target_text, _UNCERTAIN_PATTERNS, "uncertain")

    all_signals = sql_hits + cmd_hits + exfil_hits + jb_hits + unc_hits
    sp.signals = all_signals

    # Clasificación
    if sql_hits or cmd_hits or exfil_hits:
        sp.intent_class = "attack"
        sp.confidence = min(1.0, 0.7 + 0.1 * len(sql_hits + cmd_hits + exfil_hits))
        sp.rejected = True
        sp.rejection_reason = f"attack_detected:{','.join((sql_hits + cmd_hits + exfil_hits)[:5])}"
    elif jb_hits:
        sp.intent_class = "jailbreak"
        sp.confidence = min(1.0, 0.7 + 0.1 * len(jb_hits))
        sp.rejected = True
        sp.rejection_reason = f"jailbreak_detected:{','.join(jb_hits[:5])}"
    elif unc_hits:
        sp.intent_class = "uncertain"
        sp.confidence = 0.4
        sp.rejected = False  # uncertain NO bloquea; sólo se loguea
    else:
        sp.intent_class = "safe"
        sp.confidence = 0.0
        sp.rejected = False

    sp.payload = payload
    return sp
