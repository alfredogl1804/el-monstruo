"""
tests/test_embrion_inbox_parser.py — Tests del parser determinista del inbox.

Sprint EMBRION-NEEDS-002 Tarea 5 (CA3).
Mínimo: ≥15 tests cubriendo /context, /override, /help, /status, /answer, /feedback,
comandos inválidos, payloads vacíos, edge cases.

CA3.2 cubierto: imports sólo del módulo bajo prueba — sin openai/anthropic/llm_*.
"""

from __future__ import annotations

import pytest

from kernel.embrion_inbox_parser import (
    COMMANDS_WITH_REQUIRED_PAYLOAD,
    COMMANDS_WITHOUT_PAYLOAD,
    KNOWN_COMMANDS,
    parse_command,
)


# ─── 1) /help — comando sin payload, válido ──────────────────────────────
def test_help_command_valid():
    pc = parse_command("/help")
    assert pc.valid is True
    assert pc.comando == "/help"
    assert pc.payload == {}
    assert pc.reason is None


# ─── 2) /status — comando sin payload, válido ────────────────────────────
def test_status_command_valid():
    pc = parse_command("/status")
    assert pc.valid is True
    assert pc.comando == "/status"
    assert pc.payload == {}


# ─── 3) /help con basura extra es tolerante (sin payload) ────────────────
def test_help_with_extra_text_still_valid():
    pc = parse_command("/help me please")
    # /help no requiere payload: texto extra se ignora explícitamente
    assert pc.valid is True
    assert pc.payload == {}


# ─── 4) /context con texto válido ────────────────────────────────────────
def test_context_with_text_valid():
    pc = parse_command("/context El sprint S-003 está bloqueado por RLS gap")
    assert pc.valid is True
    assert pc.comando == "/context"
    assert pc.payload == {"text": "El sprint S-003 está bloqueado por RLS gap"}


# ─── 5) /context sin texto → missing_payload ─────────────────────────────
def test_context_empty_payload_invalid():
    pc = parse_command("/context")
    assert pc.valid is False
    assert pc.reason == "missing_payload:/context"


# ─── 6) /override bien formado con un param ──────────────────────────────
def test_override_single_param_valid():
    pc = parse_command("/override abc12345 cap=0.5")
    assert pc.valid is True
    assert pc.comando == "/override"
    assert pc.payload["proposal_id"] == "abc12345"
    assert pc.payload["params"] == {"cap": "0.5"}


# ─── 7) /override con múltiples params ───────────────────────────────────
def test_override_multiple_params_valid():
    pc = parse_command("/override 550e8400-e29b-41d4-a716-446655440000 cap=0.5 timeout=30 risk=low")
    assert pc.valid is True
    assert pc.payload["params"] == {"cap": "0.5", "timeout": "30", "risk": "low"}


# ─── 8) /override sin proposal_id → malformed ────────────────────────────
def test_override_missing_proposal_id_invalid():
    pc = parse_command("/override")
    assert pc.valid is False
    assert pc.reason == "missing_payload:/override"


# ─── 9) /override con proposal_id muy corto → malformed ──────────────────
def test_override_short_proposal_id_invalid():
    pc = parse_command("/override abc cap=0.5")
    assert pc.valid is False
    assert pc.reason is not None
    assert pc.reason.startswith("override_malformed:invalid_proposal_id")


# ─── 10) /override sin params → malformed ────────────────────────────────
def test_override_no_params_invalid():
    pc = parse_command("/override abc12345")
    assert pc.valid is False
    assert pc.reason is not None
    assert "override_malformed" in pc.reason


# ─── 11) /override con par mal formado ───────────────────────────────────
def test_override_bad_param_invalid():
    pc = parse_command("/override abc12345 just_a_word")
    assert pc.valid is False
    assert pc.reason is not None
    assert "bad_param_pair" in pc.reason


# ─── 12) /answer con texto válido ────────────────────────────────────────
def test_answer_with_text_valid():
    pc = parse_command("/answer Usar la branch main directamente")
    assert pc.valid is True
    assert pc.comando == "/answer"
    assert pc.payload == {"text": "Usar la branch main directamente"}


# ─── 13) /feedback con texto válido ──────────────────────────────────────
def test_feedback_with_text_valid():
    pc = parse_command("/feedback Aprobado pero suba el cap a 1.0")
    assert pc.valid is True
    assert pc.comando == "/feedback"
    assert pc.payload == {"text": "Aprobado pero suba el cap a 1.0"}


# ─── 14) Comando desconocido → unknown_command ───────────────────────────
def test_unknown_command_invalid():
    pc = parse_command("/foo bar")
    assert pc.valid is False
    assert pc.comando == "/foo"
    assert pc.reason == "unknown_command:/foo"


# ─── 15) Texto libre sin slash → not_a_command ───────────────────────────
def test_plain_text_invalid():
    pc = parse_command("hola embrión qué tal")
    assert pc.valid is False
    assert pc.reason == "not_a_command"


# ─── 16) Texto vacío → empty_text ────────────────────────────────────────
def test_empty_text_invalid():
    pc = parse_command("")
    assert pc.valid is False
    assert pc.reason == "empty_text"


# ─── 17) Whitespace solamente → empty_text ───────────────────────────────
def test_whitespace_only_invalid():
    pc = parse_command("    \t  \n  ")
    assert pc.valid is False
    assert pc.reason == "empty_text"


# ─── 18) Comando case-insensitive (lowercased) ───────────────────────────
def test_command_case_insensitive():
    pc = parse_command("/HELP")
    assert pc.valid is True
    assert pc.comando == "/help"


# ─── 19) Comando con payload mantiene case del payload ───────────────────
def test_payload_case_preserved():
    pc = parse_command("/context El SPRINT S-003 Está en MAIN")
    assert pc.valid is True
    assert pc.payload["text"] == "El SPRINT S-003 Está en MAIN"


# ─── 20) Input no-string (None, int) → non_string_input ──────────────────
def test_non_string_input_invalid():
    pc = parse_command(None)  # type: ignore[arg-type]
    assert pc.valid is False
    assert pc.reason == "non_string_input"
    pc2 = parse_command(123)  # type: ignore[arg-type]
    assert pc2.valid is False


# ─── 21) Caracteres no-imprimibles → non_printable ───────────────────────
def test_non_printable_chars_invalid():
    # Caracteres de control típicos de prompt injection (NULL, ESC, etc.)
    pc = parse_command("/context hola\x00mundo")
    assert pc.valid is False
    assert pc.reason == "non_printable"


# ─── 22) ParsedCommand dataclass exporta raw_text ────────────────────────
def test_raw_text_preserved():
    raw = "/context El embrión escucha"
    pc = parse_command(raw)
    assert pc.raw_text == raw


# ─── 23) Whitelist canónica matchea constantes ───────────────────────────
def test_known_commands_complete():
    expected = {"/context", "/override", "/help", "/status", "/answer", "/feedback"}
    assert KNOWN_COMMANDS == expected
    assert COMMANDS_WITHOUT_PAYLOAD == {"/help", "/status"}
    assert COMMANDS_WITH_REQUIRED_PAYLOAD == {"/context", "/override", "/answer", "/feedback"}


# ─── 24) Override con UUID v4 estándar ───────────────────────────────────
def test_override_uuid_v4_valid():
    pc = parse_command("/override 550e8400-e29b-41d4-a716-446655440000 cap=0.5")
    assert pc.valid is True
    assert pc.payload["proposal_id"] == "550e8400-e29b-41d4-a716-446655440000"


# ─── 25) Determinismo: misma entrada → mismo output ──────────────────────
def test_determinism():
    raw = "/override abc12345 cap=0.5 timeout=30"
    pc1 = parse_command(raw)
    pc2 = parse_command(raw)
    assert pc1.comando == pc2.comando
    assert pc1.payload == pc2.payload
    assert pc1.valid == pc2.valid
    assert pc1.reason == pc2.reason


# ─── 26) Cero imports prohibidos en el módulo (anti-LLM) ─────────────────
def test_no_llm_imports_in_parser_module():
    """Inspección estática: el módulo NO debe importar openai/anthropic/llm_*."""
    import sys

    import kernel.embrion_inbox_parser as parser_mod

    mod = sys.modules[parser_mod.__name__]
    # Verifica que el módulo solo importó re, dataclasses, typing, future
    # Inspeccionar atributos del módulo que sean módulos importados
    for name in dir(mod):
        attr = getattr(mod, name)
        # Si es un módulo, debe pertenecer a allowed
        if hasattr(attr, "__name__") and hasattr(attr, "__file__"):
            mname = attr.__name__
            if mname.startswith(("openai", "anthropic", "kernel.llm_", "groq")):
                pytest.fail(f"Parser importa módulo prohibido: {mname}")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
