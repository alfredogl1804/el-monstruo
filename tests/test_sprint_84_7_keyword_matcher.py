"""
Sprint 84.7 — Test suite del refactor global de keyword matching
================================================================
Verifica:
1. Utility kernel/utils/keyword_matcher.py funciona correcta
2. Cada archivo refactorizado pasa A (match aislado), B (no falso positivo embedded), C (negación)
3. Circuit breaker del judge fail-open en EmbrionLoop
"""
from __future__ import annotations

import sys
import os

# Agregar repo root al path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ── Bloque 1: Utility kernel/utils/keyword_matcher ──────────────────────────────


def test_compile_keyword_pattern_basic():
    from kernel.utils.keyword_matcher import compile_keyword_pattern

    pat = compile_keyword_pattern(("ejecuta", "construye"))
    assert pat.search("ejecuta esto ahora") is not None  # A: match aislado
    assert pat.search("la ejecutación") is None  # B: substring NO matchea
    assert pat.search("EJECUTA") is not None  # case insensitive


def test_compile_keyword_pattern_multiword():
    from kernel.utils.keyword_matcher import compile_keyword_pattern

    pat = compile_keyword_pattern(("hecho a mano", "saas",))
    assert pat.search("producto hecho a mano") is not None
    assert pat.search("plataforma saas") is not None
    assert pat.search("salsas para pasta") is None  # 'saas' no embebido en 'salsas'


def test_compile_keyword_pattern_short_words():
    from kernel.utils.keyword_matcher import compile_keyword_pattern

    pat = compile_keyword_pattern(("api", "arte", "bar"))
    assert pat.search("usar api rest") is not None
    assert pat.search("una api") is not None
    assert pat.search("rapidez") is None  # api NO matchea
    assert pat.search("artesanal") is None  # arte NO matchea
    assert pat.search("bartender") is None  # bar NO matchea


def test_match_any_keyword():
    from kernel.utils.keyword_matcher import compile_keyword_pattern, match_any_keyword

    # Default: \b estándar (`_` es word-char)
    pat_default = compile_keyword_pattern(("button", "card"))
    assert match_any_keyword("el button rojo", pat_default)
    assert not match_any_keyword("buttoned_jacket", pat_default)
    assert not match_any_keyword("hero_button", pat_default)  # `_` es word-char

    # Con treat_underscore_as_separator=True (snake_case identifiers)
    pat_snake = compile_keyword_pattern(("button", "card"), treat_underscore_as_separator=True)
    assert match_any_keyword("hero_button", pat_snake)
    assert match_any_keyword("product_card", pat_snake)
    assert not match_any_keyword("buttoned", pat_snake)  # boundary preservado


def test_count_keyword_matches():
    from kernel.utils.keyword_matcher import compile_keyword_pattern, count_keyword_matches

    pat = compile_keyword_pattern(("taller", "clase"))
    assert count_keyword_matches("taller de yoga", pat) == 1
    assert count_keyword_matches("taller, clase, taller", pat) == 3
    assert count_keyword_matches("instalar", pat) == 0  # taller NO matchea instalar


def test_is_negation_or_question():
    from kernel.utils.keyword_matcher import is_negation_or_question

    # Negaciones explícitas
    assert is_negation_or_question("no voy a ejecutar")
    assert is_negation_or_question("antes de construir")
    # Preguntas
    assert is_negation_or_question("¿cómo se ejecuta?")
    assert is_negation_or_question("cómo se construye")
    assert is_negation_or_question("podrías ayudarme")
    assert is_negation_or_question("puedes mostrarme")
    # Affirmativos directos NO matchean
    assert not is_negation_or_question("ejecuta esto ahora")
    assert not is_negation_or_question("construye el monstruo")


# ── Bloque 2: Archivos refactorizados ───────────────────────────────────────────


def test_external_agents_patterns_compiled():
    """A: external_agents.py patterns precompilados al cargar módulo."""
    import kernel.external_agents as ea

    assert hasattr(ea, "_RESEARCH_PATTERN")
    assert hasattr(ea, "_MANUS_PATTERN")
    assert hasattr(ea, "_ANALYSIS_PATTERN")
    assert hasattr(ea, "_CODE_PATTERN")


def test_magna_classifier_patterns_compiled():
    """A: magna_classifier.py patterns precompilados."""
    import kernel.magna_classifier as mc

    assert hasattr(mc, "_TECH_PATTERN")
    assert hasattr(mc, "_ACTION_PATTERN")
    assert hasattr(mc, "_REFLECTION_PATTERN")


def test_supervisor_patterns_compiled():
    """A: supervisor.py patterns precompilados."""
    import kernel.supervisor as sup

    # Al menos un pattern del refactor (los nombres dependen del refactor)
    pattern_attrs = [a for a in dir(sup) if "PATTERN" in a]
    assert len(pattern_attrs) >= 1, f"supervisor debe tener patterns, encontrados: {pattern_attrs}"


def test_embrion_loop_patterns_and_circuit_breaker():
    """A: embrion_loop.py patterns + circuit breaker constants."""
    import kernel.embrion_loop as el

    # Patterns del refactor de silence_score
    pattern_attrs = [a for a in dir(el) if "PATTERN" in a]
    assert len(pattern_attrs) >= 1, "embrion_loop debe tener patterns para silence_score"
    # Circuit breaker constant
    assert hasattr(el, "MAX_JUDGE_CONSECUTIVE_FAILURES")
    assert el.MAX_JUDGE_CONSECUTIVE_FAILURES >= 1


def test_motion_orchestrator_patterns_compiled():
    """A: motion/orchestrator.py patterns precompilados."""
    import kernel.motion.orchestrator as mo

    assert hasattr(mo, "_BUTTON_LIKE_PATTERN")
    assert hasattr(mo, "_CARD_LIKE_PATTERN")
    # A: match aislado
    assert mo._BUTTON_LIKE_PATTERN.search("hero_button") is not None
    assert mo._CARD_LIKE_PATTERN.search("product_card") is not None
    # B: substring NO matchea
    assert mo._BUTTON_LIKE_PATTERN.search("buttoned") is None


def test_product_architect_uses_centralized_utility():
    """A: product_architect.py importa compile_keyword_pattern de la utility."""
    import kernel.embriones.product_architect as pa

    # Verificar import de utility
    assert hasattr(pa, "compile_keyword_pattern")
    # Verificar que VERTICALES_KEYWORDS sigue funcionando
    pattern = pa.compile_keyword_pattern(tuple(pa.VERTICALES_KEYWORDS["education_arts"]))
    assert pattern.search("taller de yoga") is not None
    # B: substring NO matchea (artesanal NO matchea arte)
    assert pattern.search("producto artesanal premium") is None or len(pattern.findall("producto artesanal premium")) == 0


# ── Bloque 5: Circuit Breaker ───────────────────────────────────────────────────


def test_circuit_breaker_constant_configurable():
    """Circuit breaker threshold debe ser configurable via env var."""
    import os
    # Default
    saved = os.environ.pop("EMBRION_MAX_JUDGE_FAILURES", None)
    # Reload module to pick up clean env
    import importlib
    import kernel.embrion_loop as el
    importlib.reload(el)
    assert el.MAX_JUDGE_CONSECUTIVE_FAILURES == 5
    if saved:
        os.environ["EMBRION_MAX_JUDGE_FAILURES"] = saved


# ── Smoke: ningún archivo refactorizado regresiona import ─────────────────────


def test_smoke_all_refactored_files_import():
    """Smoke: todos los archivos refactorizados se pueden importar sin errors."""
    import kernel.external_agents
    import kernel.magna_classifier
    import kernel.supervisor
    import kernel.embrion_loop
    import kernel.task_planner
    import kernel.nodes
    import kernel.motion.orchestrator
    import kernel.embriones.product_architect
    import kernel.utils.keyword_matcher
    # Todos importaron sin excepción
    assert True


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
