"""
tests/test_embrion_input_preverifier.py
=======================================

Tests para `kernel.embrion_self_verifier.evaluate_input_for_skip`.

Sprint EMBRION-VERIFIER-001 — Pre-Verifier de INPUT (anti eco/saludo).

Contexto del bug:
  2026-05-11: 307 ciclos `mensaje_alfredo` abortados por self-verifier post-LLM.
  El verifier funcionaba correctamente, pero pagábamos $0.014/ciclo antes de
  descubrir que era eco. Este pre-verifier ataja eco/saludos triviales SIN LLM.

Cobertura:
  - Saludos triviales (hola, ok, listo, claro, sí, no, ...)
  - Confirmaciones eco ("recibido y entendido", "estoy aquí escuchando")
  - Mensajes técnicos válidos (deben pasar)
  - Mensajes largos con saludo embebido (deben pasar — pueden traer payload)
  - Edge cases: vacío, whitespace, None
"""

from __future__ import annotations

import pytest

from kernel.embrion_self_verifier import evaluate_input_for_skip

# ── Casos que DEBEN saltarse (skip=True) ─────────────────────────────────────


@pytest.mark.parametrize(
    "msg",
    [
        "hola",
        "Hola",
        "HOLA",
        "hola!",
        "hola.",
        "hey",
        "Hey!",
        "buenas",
        "saludos",
        "hi",
        "Hello",
        "ok",
        "OK",
        "Okay",
        "vale",
        "listo",
        "claro",
        "sí",
        "si",
        "no",
        "no.",
        "ok!",
    ],
)
def test_trivial_greetings_skip(msg: str) -> None:
    """Saludos triviales cortos deben skip=True."""
    skip, reason = evaluate_input_for_skip(msg)
    assert skip is True, f"esperaba skip para {msg!r}, reason={reason}"
    assert "trivial_greeting" in reason


@pytest.mark.parametrize(
    "msg",
    [
        "recibido y entendido",
        "Recibido y entendido.",
        "RECIBIDO Y ENTENDIDO",
        "estoy aquí escuchando",
        "estoy aqui escuchando",
        "Estoy aqui escuchando!",
    ],
)
def test_anti_purpose_phrases_skip(msg: str) -> None:
    """Frases anti-purpose en mensajes cortos deben skip=True."""
    skip, reason = evaluate_input_for_skip(msg)
    assert skip is True, f"esperaba skip para {msg!r}, reason={reason}"
    assert "anti_purpose" in reason


@pytest.mark.parametrize("msg", ["", "   ", "\n\t  ", None])
def test_empty_inputs_skip(msg) -> None:
    """Mensajes vacíos o None deben skip=True con razón explícita."""
    skip, reason = evaluate_input_for_skip(msg)
    assert skip is True
    assert reason == "empty_input"


# ── Casos que NO deben saltarse (skip=False) ─────────────────────────────────


@pytest.mark.parametrize(
    "msg",
    [
        "Implementa el pre-verifier en embrion_loop.py",
        "Audita PR #92 línea por línea",
        "¿Por qué el embrión gasta $7 al día?",
        "Necesito que valides la doctrina del silencio",
        "Construir el monstruo soberano",
        "Investiga el bug de scheduled_tasks duplicado",
        "Diseña la doctrina anti-eco con el verifier",
        "Crea una migration 0019 para deduplicar tareas",
    ],
)
def test_meaningful_short_messages_proceed(msg: str) -> None:
    """Mensajes técnicos cortos con contenido real deben skip=False."""
    skip, reason = evaluate_input_for_skip(msg)
    assert skip is False, f"esperaba proceder para {msg!r}, reason={reason}"
    assert reason.startswith("proceed_normal_len=")


def test_long_message_with_greeting_proceeds() -> None:
    """Mensajes >=200 chars con saludo embebido NO deben skip (pueden traer payload)."""
    long_msg = (
        "hola, recibido y entendido. Te paso el contexto completo: "
        "necesito que audites el bug de scheduled_tasks porque tenemos "
        "16,943 filas duplicadas y eso multiplica el costo del kernel. "
        "Adjunto el resultado del SQL: SELECT name, COUNT(*) ..."
    )
    assert len(long_msg) >= 200
    skip, reason = evaluate_input_for_skip(long_msg)
    assert skip is False
    assert reason.startswith("proceed_normal_len=")


def test_short_message_anti_purpose_then_payload_proceeds() -> None:
    """Mensaje <200 chars que arranca con anti-purpose pero trae payload técnico:
    el comportamiento conservador actual es skip si contiene anti-purpose en
    mensaje corto. Aquí documentamos: usuarios deben evitar 'recibido y entendido'
    como apertura de mensajes operativos."""
    msg = "Recibido y entendido. Procede con el PR."
    skip, reason = evaluate_input_for_skip(msg)
    # Comportamiento esperado: skip=True porque length<200 y contiene anti-purpose.
    # Si esto se vuelve molesto en producción, se ajusta el threshold de length.
    assert skip is True
    assert "anti_purpose" in reason


# ── Edge cases técnicos ──────────────────────────────────────────────────────


def test_whitespace_only_skip() -> None:
    """Sólo whitespace cuenta como empty."""
    skip, reason = evaluate_input_for_skip("     \t\n   ")
    assert skip is True
    assert reason == "empty_input"


def test_greeting_with_trailing_punctuation_skip() -> None:
    """`hola!`, `ok.`, `claro??` deben skip."""
    for msg in ["hola!", "ok.", "claro??", "listo!!", "vale.."]:
        skip, reason = evaluate_input_for_skip(msg)
        assert skip is True, f"esperaba skip para {msg!r}, reason={reason}"


def test_greeting_with_too_much_extra_text_proceeds() -> None:
    """`hola, necesito ayuda con el kernel` NO matchea regex trivial estricto y
    no contiene anti-purpose phrase, así que debe pasar."""
    msg = "hola, necesito ayuda con el kernel del Monstruo y el scheduler"
    skip, reason = evaluate_input_for_skip(msg)
    assert skip is False
    assert reason.startswith("proceed_normal_len=")
