"""
Sprint 84.5 — Tests A-F del classifier slow-path fix.

Verifica:
- Bug 8va semilla: prompts largos con execute keywords ahora ruteado a EXECUTE
  (a través de _local_classify, que es el preflight del slow-path).
- Bug 14va semilla: word boundaries + filtro de negaciones/preguntas elimina
  falsos positivos de substring matching.

Ejecutar:
    cd ~/el-monstruo && python -m pytest tests/test_sprint_84_5_classifier.py -v
"""

from __future__ import annotations

import pytest

from contracts.kernel_interface import IntentType
from kernel.nodes import _local_classify, _is_negation_or_question


# ── Test A: Prompt corto execute (fast-path actual ya funciona) ──
def test_a_prompt_corto_execute() -> None:
    """Caso A: 'crea landing pintura' → EXECUTE (fast-path)."""
    result = _local_classify("crea landing pintura")
    assert result == IntentType.EXECUTE, (
        f"Test A FAIL: esperado EXECUTE, got {result.value}"
    )


# ── Test B: Prompt LARGO execute (BUG #1 — 8va semilla) ──
def test_b_prompt_largo_execute_bug_8va() -> None:
    """Caso B: prompt largo con 'crea' al inicio → EXECUTE (antes del fix iba a background)."""
    prompt = (
        "Crea una landing detallada para curso de pintura al óleo "
        "con secciones de instructor, programa, precio, FAQ, testimonios, "
        "hero con imagen, CTA prominente, mobile responsive, integración "
        "con calendario, sistema de pagos Stripe y email marketing."
    )
    result = _local_classify(prompt)
    assert result == IntentType.EXECUTE, (
        f"Test B FAIL (bug 8va): esperado EXECUTE, got {result.value}. "
        "Slow-path debe atrapar 'crea' aunque el prompt sea COMPLEX/DEEP."
    )


# ── Test C: Prompt largo background legítimo (no debe regresionar) ──
def test_c_prompt_largo_background_legitimo() -> None:
    """Caso C: 'investiga las mejores prácticas...' → DEEP_THINK (no EXECUTE)."""
    prompt = (
        "Investiga las mejores prácticas de marketing digital para empresas "
        "SaaS B2B en 2026, con foco en automatización, growth loops y "
        "atribución multi-touch."
    )
    result = _local_classify(prompt)
    # 'investiga' es think keyword → DEEP_THINK (clasificación local;
    # el LLM router en slow-path lo refinaría a BACKGROUND si aplica).
    assert result == IntentType.DEEP_THINK, (
        f"Test C FAIL: esperado DEEP_THINK, got {result.value}. "
        "'investiga' es think keyword, no execute."
    )


# ── Test D: Prompt vacío (no crash) ──
def test_d_prompt_vacio_no_crash() -> None:
    """Caso D: '' → CHAT (sin crash, error controlado)."""
    result = _local_classify("")
    assert result == IntentType.CHAT, (
        f"Test D FAIL: esperado CHAT (no crash), got {result.value}"
    )

    # También probar solo whitespace
    result_ws = _local_classify("   \n\t  ")
    assert result_ws == IntentType.CHAT, (
        f"Test D FAIL (whitespace): esperado CHAT, got {result_ws.value}"
    )


# ── Test E: Negación con execute keyword (BUG #2 — 14va semilla) ──
def test_e_negacion_con_execute_keyword_bug_14va() -> None:
    """Caso E: 'No voy a ejecutar esto todavía' → CHAT (antes era EXECUTE)."""
    result = _local_classify("No voy a ejecutar esto todavía")
    assert result == IntentType.CHAT, (
        f"Test E FAIL (bug 14va): esperado CHAT, got {result.value}. "
        "Negación 'no voy a' debe invalidar match de execute keyword."
    )

    # Variantes adicionales
    variantes = [
        "no quiero crear el sitio aún",
        "no debería borrar este archivo",
        "no voy a actualizar nada todavía",
    ]
    for v in variantes:
        r = _local_classify(v)
        assert r == IntentType.CHAT, (
            f"Test E FAIL en variante '{v}': esperado CHAT, got {r.value}"
        )


# ── Test F: Pregunta con execute keyword (BUG #2 — 14va semilla) ──
def test_f_pregunta_con_execute_keyword_bug_14va() -> None:
    """Caso F: '¿Cómo se actualiza el sistema?' → CHAT (antes era EXECUTE)."""
    result = _local_classify("¿Cómo se actualiza el sistema?")
    # Es pregunta (¿?) y tiene "cómo se" → no es orden ejecutable.
    assert result in (IntentType.CHAT, IntentType.DEEP_THINK), (
        f"Test F FAIL (bug 14va): esperado CHAT o DEEP_THINK, got {result.value}. "
        "Pregunta no debe disparar EXECUTE."
    )
    # El filtro debe haberse activado.
    assert _is_negation_or_question("¿cómo se actualiza el sistema?"), (
        "Test F FAIL: filtro de pregunta no detectó '¿cómo se ... ?'"
    )

    # Variantes
    preguntas = [
        "¿podrías crear un dashboard?",  # pregunta educada
        "¿cómo se ejecuta este script?",
        "antes de borrar, ¿qué pasa con los datos?",
    ]
    for q in preguntas:
        r = _local_classify(q)
        assert r != IntentType.EXECUTE, (
            f"Test F FAIL en pregunta '{q}': no debe ser EXECUTE, got {r.value}"
        )


# ── Smoke tests adicionales: no regresión del fast-path ──
def test_smoke_no_regression_fast_path_execute() -> None:
    """Casos cortos que ya funcionaban deben seguir funcionando."""
    casos_execute = [
        "ejecuta el script",
        "haz un deploy",
        "deploy a producción",
        "instala las dependencias",
        "borra el archivo temp",
        "elimina la cuenta",
        "publica el post",
        "create a new branch",
        "delete this file",
        "send the email",
    ]
    for caso in casos_execute:
        r = _local_classify(caso)
        assert r == IntentType.EXECUTE, (
            f"Regresión fast-path: '{caso}' debe ser EXECUTE, got {r.value}"
        )


def test_smoke_no_regression_think() -> None:
    """Think keywords siguen funcionando."""
    casos_think = [
        "analiza este código",
        "compara estas dos opciones",
        "explica cómo funciona LangGraph",
        "evaluate this approach",
    ]
    for caso in casos_think:
        r = _local_classify(caso)
        assert r == IntentType.DEEP_THINK, (
            f"Regresión think: '{caso}' debe ser DEEP_THINK, got {r.value}"
        )


def test_smoke_system_commands() -> None:
    """Comandos / y ! siguen mapeando a SYSTEM."""
    assert _local_classify("/help") == IntentType.SYSTEM
    assert _local_classify("!status") == IntentType.SYSTEM


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
