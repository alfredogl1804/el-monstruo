"""
kernel/cowork_runtime/epistemic_labels.py — 9 etiquetas epistemicas granulares.

Sprint convergencia 7 Sabios (2026-05-12) — convergencia de Copilot 365 +
Gemini 3.1 Pro + Claude Opus 4.7 + Kimi K2.6 + Grok 4 Heavy + GPT-5.5 Pro +
DeepSeek R1 firmada en bridge/cowork_to_perplexity_T2B_UPDATE_PR_110_...md.

Reemplaza el set anterior de 4 tags (VERIFICADO / INFERIDO / NO VERIFICADO /
REQUIERE READ/SQL) por 9 etiquetas granulares que capturan mejor la
licencia para afirmar y la fuente de validacion.

Las 9 etiquetas:

  VERIFIED_CURRENT_TURN        tool_call ejecutado en este turno
  VERIFIED_RECENT_LT_60M       validado <60min, no repetir tool_call
  SESSION_MEMORY_ONLY          solo memoria de sesion actual, NO afirmar como hecho
  INFERRED                     inferencia razonable, no verificacion
  USER_PROVIDED                dato que aporto el usuario (Alfredo T1) en sesion
  NEEDS_SQL                    claim factual que requiere SQL fresco antes de afirmar
  NEEDS_READ                   claim factual que requiere Read del repo antes de afirmar
  CONTRADICTED_BY_EXTERNAL     contradice output reciente de Sabio externo o data fresca
  UNVERIFIED_DO_NOT_ASSERT     sin licencia para afirmar, debe omitirse o degradarse

Compatibilidad hacia atras (legacy): se aceptan los 4 tags previos
VERIFICADO / INFERIDO / NO VERIFICADO / REQUIERE READ/SQL como aliases
hacia las nuevas etiquetas para no romper el audit log historico:

  VERIFICADO          -> VERIFIED_CURRENT_TURN (default si trae fuente+timestamp)
  INFERIDO            -> INFERRED
  NO VERIFICADO       -> UNVERIFIED_DO_NOT_ASSERT
  REQUIERE READ/SQL   -> NEEDS_READ o NEEDS_SQL

Que constituye "afirmacion factual fuerte" (sensible a estas etiquetas):
- claims P0 sobre estado operativo (kernel, embrion, gateway, RLS)
- claims P1 sobre estado del repo o memoria persistente
- toda metrica numerica concreta sobre estado del sistema
- toda afirmacion sobre acciones que Manus o agentes externos ejecutaron
"""
from __future__ import annotations

import re
from enum import Enum
from typing import Optional


class EpistemicLabel(str, Enum):
    """Las 9 etiquetas canonicas (convergencia 7 Sabios 2026-05-12)."""
    VERIFIED_CURRENT_TURN = "VERIFIED_CURRENT_TURN"
    VERIFIED_RECENT_LT_60M = "VERIFIED_RECENT_LT_60M"
    SESSION_MEMORY_ONLY = "SESSION_MEMORY_ONLY"
    INFERRED = "INFERRED"
    USER_PROVIDED = "USER_PROVIDED"
    NEEDS_SQL = "NEEDS_SQL"
    NEEDS_READ = "NEEDS_READ"
    CONTRADICTED_BY_EXTERNAL = "CONTRADICTED_BY_EXTERNAL"
    UNVERIFIED_DO_NOT_ASSERT = "UNVERIFIED_DO_NOT_ASSERT"


# Conjunto ordenado de strings para validacion rapida
VALID_LABELS_9: tuple[str, ...] = tuple(l.value for l in EpistemicLabel)

# Etiquetas que constituyen licencia para afirmar
LICENSED_LABELS: frozenset[str] = frozenset({
    EpistemicLabel.VERIFIED_CURRENT_TURN.value,
    EpistemicLabel.VERIFIED_RECENT_LT_60M.value,
    EpistemicLabel.USER_PROVIDED.value,
})

# Etiquetas que explicitan ausencia de licencia (degradan respuesta)
UNLICENSED_LABELS: frozenset[str] = frozenset({
    EpistemicLabel.SESSION_MEMORY_ONLY.value,
    EpistemicLabel.NEEDS_SQL.value,
    EpistemicLabel.NEEDS_READ.value,
    EpistemicLabel.CONTRADICTED_BY_EXTERNAL.value,
    EpistemicLabel.UNVERIFIED_DO_NOT_ASSERT.value,
})

# Etiquetas intermedias: no es claim factual operacional pero tampoco
# requiere licencia dura (INFERRED se permite si es transparente)
SOFT_LABELS: frozenset[str] = frozenset({
    EpistemicLabel.INFERRED.value,
})


# Mapeo legacy -> moderno (compatibilidad con audit log historico)
LEGACY_TO_MODERN: dict[str, str] = {
    "VERIFICADO": EpistemicLabel.VERIFIED_CURRENT_TURN.value,
    "INFERIDO": EpistemicLabel.INFERRED.value,
    "NO VERIFICADO": EpistemicLabel.UNVERIFIED_DO_NOT_ASSERT.value,
    "REQUIERE READ/SQL": EpistemicLabel.NEEDS_READ.value,
    "REQUIERE_READ_SQL": EpistemicLabel.NEEDS_READ.value,
}

# Regex que matchea CUALQUIERA de las 9 etiquetas modernas o las 4 legacy.
# Permite forma ampliada [VERIFIED_CURRENT_TURN fuente=mcp ts=...]
# y forma compacta [VERIFIED_CURRENT_TURN].
_MODERN_BODY = "|".join(re.escape(l) for l in VALID_LABELS_9)
_LEGACY_BODY = r"VERIFICADO|INFERIDO|NO\s+VERIFICADO|REQUIERE\s+READ/SQL"

LABEL_REGEX = re.compile(
    rf"\[(?:(?:{_MODERN_BODY})(?:[^\]]*)|(?:{_LEGACY_BODY})(?:[^\]]*))\]",
    re.IGNORECASE,
)


def normalize_label(raw: str) -> Optional[str]:
    """
    Toma el contenido detectado dentro de [...] (sin corchetes) y devuelve
    la etiqueta moderna canonica (uno de VALID_LABELS_9) o None si no
    matchea ninguna conocida.

    Acepta:
      "VERIFIED_CURRENT_TURN fuente=... ts=..."  -> VERIFIED_CURRENT_TURN
      "VERIFICADO fuente=... ts=..."             -> VERIFIED_CURRENT_TURN (legacy)
      "needs_sql"                                -> NEEDS_SQL
      "REQUIERE READ/SQL"                        -> NEEDS_READ (legacy default)
    """
    if not raw:
        return None
    upper = raw.strip().upper()
    # Match exacto contra modernos
    for label in VALID_LABELS_9:
        if upper.startswith(label):
            return label
    # Match contra legacy (con normalizacion de espacios)
    upper_compact = re.sub(r"\s+", " ", upper).strip()
    for legacy, modern in LEGACY_TO_MODERN.items():
        if upper_compact.startswith(legacy):
            return modern
    return None


def extract_label(sentence: str) -> tuple[bool, str, Optional[str]]:
    """
    Detecta la primera etiqueta presente en la oracion.

    Returns:
        (has_label, raw_match_with_brackets, normalized_label_or_None)

    Compatibilidad: si la oracion no tiene etiqueta moderna pero si una
    legacy, igualmente reporta has_label=True con normalized_label
    apuntando al equivalente moderno.
    """
    m = LABEL_REGEX.search(sentence)
    if not m:
        return False, "", None
    raw_full = m.group(0)
    inner = raw_full.strip("[]")
    normalized = normalize_label(inner)
    return True, raw_full, normalized


def is_licensed(label: Optional[str]) -> bool:
    """
    True si la etiqueta da licencia operativa para afirmar claim factual.

    USER_PROVIDED es licencia: si Alfredo lo dijo, Cowork puede repetirlo
    sin tool_call propio.
    """
    if not label:
        return False
    return label in LICENSED_LABELS


def is_unlicensed(label: Optional[str]) -> bool:
    """True si la etiqueta degrada explicitamente la afirmacion."""
    if not label:
        return False
    return label in UNLICENSED_LABELS


def requires_tool_call(label: Optional[str]) -> bool:
    """
    True si la etiqueta indica que se necesita tool_call para promover la
    afirmacion a licenciada. NEEDS_SQL y NEEDS_READ son los casos canonicos.
    """
    if not label:
        return False
    return label in (
        EpistemicLabel.NEEDS_SQL.value,
        EpistemicLabel.NEEDS_READ.value,
    )


def label_help_block() -> str:
    """Mensaje canonico que enumera las 9 etiquetas para mostrar a Cowork."""
    return (
        "Las 9 etiquetas epistemicas canonicas (convergencia 7 Sabios 2026-05-12):\n"
        "  [VERIFIED_CURRENT_TURN fuente=... ts=...]    tool_call en este turno\n"
        "  [VERIFIED_RECENT_LT_60M fuente=... ts=...]   validado <60min\n"
        "  [SESSION_MEMORY_ONLY]                        solo memoria de sesion\n"
        "  [INFERRED]                                   inferencia razonable\n"
        "  [USER_PROVIDED]                              dato que aporto Alfredo T1\n"
        "  [NEEDS_SQL] + propuesta de query             requiere SQL fresco\n"
        "  [NEEDS_READ] + path                          requiere Read del repo\n"
        "  [CONTRADICTED_BY_EXTERNAL fuente=...]        contradice output Sabio externo\n"
        "  [UNVERIFIED_DO_NOT_ASSERT]                   sin licencia, debe omitirse"
    )
