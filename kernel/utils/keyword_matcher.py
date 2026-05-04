"""
El Monstruo — Keyword matching con word boundaries.

Utility centralizada para reemplazar el patrón anti-pattern
`any(kw in text for kw in keywords)` que causaba falsos positivos
en múltiples archivos del kernel.

Sprint 84.7 — Refactor global tras audit que detectó 17 instancias
en 10 archivos críticos.

CONTRATO:
    1. Word boundary `\b` evita matches dentro de palabras compuestas
       ("ejecuta" no matchea "subejecutar", "actualizar" no matchea "actuar")
    2. case_insensitive por default
    3. compile_keyword_pattern() debe llamarse a nivel módulo (cache),
       no por cada llamada (regex compilation es caro)
    4. is_negation_or_question() es filtro defensivo para casos donde el
       contexto invierte el significado del keyword

USO:
    from kernel.utils.keyword_matcher import (
        compile_keyword_pattern, match_any_keyword,
        count_keyword_matches, is_negation_or_question,
    )

    _MY_KEYWORDS = ("ejecuta", "construye", "implementa")
    _MY_PATTERN = compile_keyword_pattern(_MY_KEYWORDS)

    def is_action_request(text: str) -> bool:
        if is_negation_or_question(text):
            return False
        return match_any_keyword(text, _MY_PATTERN)

CODE REVIEW: cualquier PR con `kw in text` raw es BLOQUEANTE.
"""
from __future__ import annotations

import re
from typing import Iterable


def compile_keyword_pattern(
    keywords: Iterable[str],
    case_insensitive: bool = True,
    treat_underscore_as_separator: bool = False,
) -> re.Pattern[str]:
    """
    Compila pattern con word boundaries. Reusable a nivel módulo.

    Args:
        keywords: lista/tupla de keywords a matchear (escapadas automáticamente)
        case_insensitive: True por default (la mayoría de los casos)
        treat_underscore_as_separator: si True, considera `_` como separador
            (útil para identificadores snake_case como `hero_button`).
            Default False = comportamiento `\b` estándar (donde `_` es word-char).

    Returns:
        Pattern compilado listo para usar con match_any_keyword()
        o count_keyword_matches()

    Raises:
        ValueError: si keywords es vacío
    """
    kws = [kw for kw in keywords if kw]
    if not kws:
        raise ValueError("keywords no puede estar vacío")
    flags = re.IGNORECASE if case_insensitive else 0
    # Sort keywords by length DESC so multi-word keywords match before sub-parts
    kws_sorted = sorted(kws, key=len, reverse=True)
    alternatives = "|".join(re.escape(kw) for kw in kws_sorted)

    if treat_underscore_as_separator:
        # Custom boundaries: NO alfanumérico ni undersocore antes/después.
        # Lookbehind/lookahead negativos contra [a-zA-Z0-9] (sin _).
        boundary_open = r"(?<![a-zA-Z0-9])"
        boundary_close = r"(?![a-zA-Z0-9])"
    else:
        boundary_open = r"\b"
        boundary_close = r"\b"

    return re.compile(
        boundary_open + r"(?:" + alternatives + r")" + boundary_close,
        flags,
    )


def match_any_keyword(text: str, pattern: re.Pattern[str]) -> bool:
    """
    Reemplaza el anti-pattern `any(kw in text for kw in keywords)`.

    Args:
        text: texto a buscar
        pattern: pattern compilado con compile_keyword_pattern()

    Returns:
        True si al menos una keyword está presente como palabra completa
    """
    if not text:
        return False
    return bool(pattern.search(text))


def count_keyword_matches(text: str, pattern: re.Pattern[str]) -> int:
    """
    Reemplaza el anti-pattern `sum(1 for kw in keywords if kw in text)`.

    Args:
        text: texto a buscar
        pattern: pattern compilado con compile_keyword_pattern()

    Returns:
        Número de matches (cuenta cada ocurrencia, no solo keywords únicos)
    """
    if not text:
        return 0
    return len(pattern.findall(text))


# Filtros opcionales reutilizables
NEGATION_OR_QUESTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bno\s+(?:quiero|voy\s+a|debería|necesito|puedo|deseo)\b", re.IGNORECASE),
    re.compile(r"\bantes\s+de\b", re.IGNORECASE),
    re.compile(r"\bcómo\s+se\b", re.IGNORECASE),
    re.compile(r"\b(?:podrías|puedes|podes|podrias)\b", re.IGNORECASE),
    re.compile(r"^\s*[¿?]"),
    re.compile(r"[¿?]\s*$"),
)


def is_negation_or_question(text: str) -> bool:
    """
    Detecta si el texto es una negación o pregunta donde un keyword
    de "execute" no debería disparar acción real.

    Casos cubiertos:
        - "no voy a ejecutar eso"      → True
        - "antes de ejecutar, ¿qué?"   → True
        - "cómo se ejecuta el script?" → True
        - "¿podrías ejecutar X?"       → True
        - "¿esto ejecuta algo?"        → True
        - "ejecuta mi prompt"          → False

    Args:
        text: texto a analizar

    Returns:
        True si el texto es claramente negación/pregunta
    """
    if not text:
        return False
    return any(pat.search(text) for pat in NEGATION_OR_QUESTION_PATTERNS)


__all__ = [
    "compile_keyword_pattern",
    "match_any_keyword",
    "count_keyword_matches",
    "is_negation_or_question",
    "NEGATION_OR_QUESTION_PATTERNS",
]
