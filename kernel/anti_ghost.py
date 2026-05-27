"""
El Monstruo — Anti-Ghost Tool Detector (DAN P0.6)
==================================================
Detector puro, sin I/O, sin dependencias de red ni DB. Recibe una traza de
eventos AG-UI (lista de dicts) y un patrón esperado, y devuelve un `GhostHit`
si el LLM narró en prosa que iba a usar una herramienta pero NO emitió un
`TOOL_CALL_START` correspondiente con el `toolCallName` correcto.

Definición operativa del DAN (correcta): un *tool ghost* es un evento de texto
del LLM (`TEXT_MESSAGE_CONTENT`, `STEP`, `THINKING_STATE`) que matchea uno de
los `prose_patterns` esperados para un tool, pero el siguiente evento de tipo
tool (en orden temporal) NO es `TOOL_CALL_START` con `toolCallName ==
expected_tool`.

DAN Regla 2: tool ghost = fallo de sistema, no "mejor esfuerzo".

Diseño:
- El detector es **puro** (recibe lista, devuelve `GhostHit | None`). Esto lo
  hace trivial de testear en CI sin LLM real, y reusable: el día que se quiera
  correr sobre `mission_events` persistidos (P0.6-completo, post-P0.3) basta
  con cargar la traza y pasarla al mismo detector.
- La traza real observada en iPhone (2026-05-27, repro S5) se canoniza como
  fixture en `tests/test_no_ghost_tools.py::SAMPLE_TRACES`.

Sprint DAN — P0.6 — 2026-05-27 — Manus E1
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

# Tipos de eventos AG-UI que pueden contener prosa del LLM (donde se esconde
# la narración del tool fantasma).
PROSE_EVENT_TYPES = frozenset(
    {
        "TEXT_MESSAGE_CONTENT",
        "STEP",
        "THINKING_STATE",
    }
)

# Eventos que indican que el LLM SÍ emitió un tool call estructurado.
TOOL_CALL_EVENTS = frozenset(
    {
        "TOOL_CALL_START",
        "TOOL_CALL_ARGS",
        "TOOL_CALL_END",
        "TOOL_CALL_COMPLETED",
        "TOOL_CALL_FAILED",
    }
)


@dataclass(frozen=True)
class GhostHit:
    """Resultado positivo del detector — hay un tool fantasma en la traza."""

    expected_tool: str
    """Nombre del tool que debería haberse llamado (e.g. 'github_ops')."""

    offending_event_index: int
    """Índice 0-based del evento de prosa que disparó la sospecha."""

    offending_event_type: str
    """Tipo del evento ofensor (TEXT_MESSAGE_CONTENT, STEP, THINKING_STATE)."""

    offending_text: str
    """Snippet del texto ofensor (truncado a 600 chars)."""

    matched_pattern: str
    """Regex que disparó el match (string del patrón, no objeto compilado)."""

    next_tool_event: dict[str, Any] | None
    """Siguiente evento de tipo tool en la traza, o None si no hubo ninguno."""

    def reason(self) -> str:
        """Mensaje de fallo formateado para `assert`."""
        nxt = self.next_tool_event
        if nxt is None:
            after = "no subsequent TOOL_CALL_* event in trace"
        else:
            t = nxt.get("type", "?")
            name = (
                nxt.get("data", {}).get("toolCallName")
                or nxt.get("data", {}).get("toolName")
                or "?"
            )
            after = f"next tool event was {t}(toolCallName={name!r})"
        return (
            f"Tool ghost detected: expected '{self.expected_tool}' but LLM "
            f"narrated in prose at event #{self.offending_event_index} "
            f"({self.offending_event_type}) matching pattern {self.matched_pattern!r}; "
            f"{after}. Offending text: {self.offending_text!r}"
        )


def _extract_text(event: dict[str, Any]) -> str:
    """
    Extrae el texto narrativo de un evento AG-UI según su tipo.
    Tolera variantes en el shape del payload (data.delta vs data.text vs
    data.content vs data.message), porque distintos generadores del kernel
    han usado keys ligeramente distintas.
    """
    data = event.get("data") or {}
    if not isinstance(data, dict):
        return ""
    for key in ("delta", "text", "content", "message", "step", "state"):
        v = data.get(key)
        if isinstance(v, str) and v:
            return v
    return ""


def _next_tool_event_after(
    events: list[dict[str, Any]], start_idx: int
) -> dict[str, Any] | None:
    """Devuelve el siguiente evento `TOOL_CALL_*` en la traza desde `start_idx+1`."""
    for i in range(start_idx + 1, len(events)):
        if events[i].get("type") in TOOL_CALL_EVENTS:
            return events[i]
    return None


def detect_ghost_tool(
    events: Iterable[dict[str, Any]],
    *,
    expected_tool: str,
    prose_patterns: list[str],
) -> GhostHit | None:
    """
    Recorre la traza buscando el primer evento de prosa que matchee uno de
    `prose_patterns` (regex case-insensitive). Si lo encuentra, mira el
    siguiente evento de tipo tool:

    - Si es `TOOL_CALL_START` con `toolCallName == expected_tool` → OK, no
      es fantasma (el LLM anunció Y ejecutó).
    - En cualquier otro caso → `GhostHit`. Esto incluye:
        * No hay ningún `TOOL_CALL_*` después.
        * El siguiente tool call es de otro tool.
        * El siguiente evento es `TOOL_CALL_END` huérfano sin START previo
          con el `expected_tool`.

    Args:
        events: traza de eventos AG-UI (lista de dicts {type, data, ...}).
        expected_tool: nombre canónico del tool en el registry (ej. 'github_ops').
        prose_patterns: lista de regex que indican que el LLM narró el tool en
            prosa (ej. r'llamando\\s+a\\s+(la\\s+)?herramienta\\s+["`]?github').

    Returns:
        `GhostHit` si hay tool fantasma, `None` si la traza está limpia.

    Notas:
    - Si el LLM narra el tool y luego sí emite el `TOOL_CALL_START` correcto
      pero MÁS TARDE (con otros tool calls intermedios de OTROS tools), eso
      cuenta como ghost: el contrato del DAN es que la prosa anuncia el
      *próximo* tool call estructurado.
    - Múltiples menciones en prosa: el detector reporta solo la primera. CI
      gate detecta presencia, no exhaustividad.
    """
    if not prose_patterns:
        return None

    compiled = [re.compile(p, re.IGNORECASE) for p in prose_patterns]
    events_list = list(events)

    for idx, ev in enumerate(events_list):
        if ev.get("type") not in PROSE_EVENT_TYPES:
            continue
        text = _extract_text(ev)
        if not text:
            continue
        for pat in compiled:
            if not pat.search(text):
                continue
            # Match — verificar siguiente evento de tool
            nxt = _next_tool_event_after(events_list, idx)
            if nxt is not None and nxt.get("type") == "TOOL_CALL_START":
                data = nxt.get("data") or {}
                name = data.get("toolCallName") or data.get("toolName") or ""
                if name == expected_tool:
                    # Limpio: anunció y ejecutó. Salir del loop entero — la
                    # traza no es fantasma para este expected_tool.
                    return None
            return GhostHit(
                expected_tool=expected_tool,
                offending_event_index=idx,
                offending_event_type=ev.get("type", "?"),
                offending_text=(text[:600] + ("…" if len(text) > 600 else "")),
                matched_pattern=pat.pattern,
                next_tool_event=nxt,
            )
    return None


# ── DAN T2 (S5 KERNEL FIX 2026-05-27) ──────────────────────────────────────
# Detector server-side post-LLM-response (NO post-stream). Recibe el texto
# plano que el LLM devolvió y la lista de tools disponibles, y reporta si la
# prosa narra una tool del catálogo sin que el LLM haya emitido un tool_call
# estructurado en la misma respuesta.
#
# Diferencia con `detect_ghost_tool` (P0.6): aquí no hay traza AG-UI todavía
# — el kernel tiene la respuesta del LLM en mano (LLMResponse.content +
# LLMResponse.tool_calls) y necesita decidir SI re-promptea con
# tool_choice="required" antes de servir nada al frontend. Es la primera línea
# de defensa contra ghost a nivel de kernel.
# ───────────────────────────────────────────────────────────────────────────


# Patrones genéricos de prosa que indican que el LLM va a usar UNA tool del
# catálogo. Cada patrón es case-insensitive y matchea variantes ES/EN +
# markdown bold ("**Herramienta:** X") porque la traza V2 del repro S5 usaba
# exactamente esa estructura.
# Cada patrón DEBE contener {tool_alias} — son tool-specific. Patrones
# genéricos como "procedo con la llamada" se manejan como FALLBACK separado
# (ver _GENERIC_FALLBACK_PATTERNS) y solo aplican si hay match tool-specific
# de fortalecimiento.
_GENERIC_GHOST_PATTERNS_TEMPLATE = [
    # "voy a llamar / llamando / llamo / llamando a la herramienta X"
    # Cubre conjugaciones: indicativo presente (llamo, llama), gerundio
    # (llamando), infinitivo (llamar), participio (llamado), etc.
    r"(?:voy\s+a\s+|estoy\s+|mientras\s+|cuando\s+)?llam(?:ar|ando|ado|o|a|amos|aremos|ar[eé])\s+(?:a\s+)?(?:la\s+)?herramienta\s+[\"`'*]*{tool_alias}",
    # "voy a invocar / invocando / invoco X"
    r"(?:voy\s+a\s+|estoy\s+)?invoc(?:ar|ando|o|a|amos)\s+(?:a\s+)?(?:la\s+herramienta\s+)?[\"`'*]*{tool_alias}",
    # "usaré / usando / uso / usar X"
    r"(?:voy\s+a\s+)?us(?:ar|ando|o|a|ar[eé])\s+(?:la\s+herramienta\s+)?[\"`'*]*{tool_alias}",
    # Markdown bold: "**Herramienta:** X" (V2 repro S5 — debe matchear con o sin
    # tool_alias inmediatamente después; el alias puede aparecer después en la línea)
    r"\*\*herramienta\*\*\s*:?\s*[\"`'*\s]*{tool_alias}",
    # Markdown bold: "**Tool:** X" (variante EN)
    r"\*\*tool\*\*\s*:?\s*[\"`'*\s]*{tool_alias}",
    # EN: "I'll call X" / "calling X" / "I am calling X"
    r"(?:i['\u2019]?ll\s+|i\s+am\s+|i'm\s+|will\s+)?call(?:ing|s)?\s+(?:the\s+)?[\"`'*]*{tool_alias}",
]

# Patrones genéricos sin tool_alias — indican narración de tool-call sin
# nombrar tool específico. Si la traza tiene UNO de estos Y además la
# prosa menciona literalmente alguno de los tool_aliases en cualquier parte,
# se considera ghost. Esto cubre patrones como "voy a ejecutarla ahora" o
# "procedo con la llamada" que aparecen en V2 repro S5.
_GENERIC_FALLBACK_PATTERNS = [
    r"proced(?:o|er[eé])\s+(?:con|a)\s+(?:la\s+)?llamada",
    r"voy\s+a\s+ejecutarla?\s+ahora",
    r"executing\s+now",
]

# Aliases legacy → canonical mapping. Si el LLM narra "github" en prosa, eso
# debería detectarse como ghost de "github_ops" (que es el tool real). Esto
# defiende contra el patrón observado en repro S5 V1 (2026-05-27) donde el
# LLM usaba el nombre legacy aunque ya no estuviera en el registry.
TOOL_NAME_ALIASES: dict[str, list[str]] = {
    "github_ops": ["github_ops", "github"],
    # Otros tools no tienen aliases legacy conocidos — usan su nombre canónico.
}


@dataclass(frozen=True)
class ResponseGhostHit:
    """Resultado positivo del detector post-response (texto plano, no traza)."""

    suspected_tool: str
    """Tool del catálogo que el LLM narró en prosa."""

    matched_alias: str
    """Alias específico del tool que matcheó (puede ser legacy, e.g. 'github')."""

    matched_pattern: str
    """Regex que disparó el match."""

    offending_excerpt: str
    """Snippet del texto ofensor (truncado a 400 chars)."""

    def reason(self) -> str:
        """Mensaje legible para logs y eventos AG-UI."""
        return (
            f"Ghost detected: LLM narrated tool '{self.suspected_tool}' "
            f"(alias '{self.matched_alias}') in prose without emitting a "
            f"tool_call. Pattern: {self.matched_pattern!r}. "
            f"Excerpt: {self.offending_excerpt!r}"
        )


def detect_ghost_in_response(
    response_text: str,
    *,
    available_tool_names: list[str],
    has_tool_calls: bool,
) -> ResponseGhostHit | None:
    """
    Detecta tool fantasma en una respuesta del LLM ANTES de que sea servida
    al frontend. Usado en `kernel/nodes.py::execute()` post-`execute_with_tools`
    para decidir si re-promptea con `tool_choice="required"`.

    Args:
        response_text: el contenido textual de `LLMResponse.content`. Si vacío
            o None, la función retorna `None` (no hay prosa que analizar).
        available_tool_names: nombres canónicos de tools en el registry actual
            (e.g. `[s.name for s in get_tool_specs()]`).
        has_tool_calls: `LLMResponse.has_tool_calls` — si `True`, el LLM SÍ
            emitió tool_calls estructurados, por lo tanto NO es ghost aunque
            la prosa también mencione la tool. Esto evita falsos positivos
            cuando el LLM anuncia Y luego function-calleó correctamente.

    Returns:
        `ResponseGhostHit` si detectó ghost (LLM narró tool en prosa Y NO
        emitió tool_calls), o `None` si la respuesta está limpia.

    Diseño:
    - Si `has_tool_calls=True` → retorna `None` sin analizar (tool_call wins).
    - Para cada tool del catálogo, genera regex usando aliases (canonical +
      legacy). Si CUALQUIER patrón matchea la prosa, reporta hit.
    - Patrones son case-insensitive y matchean ES/EN + markdown bold + variantes
      observadas en repro S5 V1 y V2 (iPhone 2026-05-27).
    """
    # Si el LLM emitió tool_calls estructurados, no es ghost — la prosa puede
    # ser anuncio legítimo ("Voy a llamar a github_ops") seguido del call real.
    if has_tool_calls:
        return None

    if not response_text or not isinstance(response_text, str):
        return None

    if not available_tool_names:
        return None

    # ── Fase 1: tool-specific patterns ────────────────────────────────────
    # Para cada tool disponible, probar todos sus aliases con patrones que
    # incluyen el {tool_alias} literal en el regex.
    for tool_name in available_tool_names:
        aliases = TOOL_NAME_ALIASES.get(tool_name, [tool_name])
        for alias in aliases:
            # Escapar el alias para insertarlo seguro en el regex template.
            alias_escaped = re.escape(alias)
            for tpl in _GENERIC_GHOST_PATTERNS_TEMPLATE:
                pattern_str = tpl.format(tool_alias=alias_escaped)
                pat = re.compile(pattern_str, re.IGNORECASE)
                m = pat.search(response_text)
                if m is None:
                    continue
                # Match — extraer snippet alrededor del match.
                start = max(0, m.start() - 50)
                end = min(len(response_text), m.end() + 150)
                excerpt = response_text[start:end].strip()
                if len(excerpt) > 400:
                    excerpt = excerpt[:400] + "…"
                return ResponseGhostHit(
                    suspected_tool=tool_name,
                    matched_alias=alias,
                    matched_pattern=pattern_str,
                    offending_excerpt=excerpt,
                )

    # ── Fase 2: fallback patterns (sin {tool_alias}) ────────────────────
    # Si la prosa contiene un patrón genérico ("procedo con la llamada",
    # "voy a ejecutarla ahora") Y además menciona literalmente el alias de
    # alguna tool del catálogo, también cuenta como ghost. Esto captura
    # estructuras V2 donde el bold "**Herramienta:** github" + el cierre
    # "procedo con la llamada" están separados en líneas distintas.
    fallback_compiled = [re.compile(p, re.IGNORECASE) for p in _GENERIC_FALLBACK_PATTERNS]
    for fb_pat in fallback_compiled:
        m_fb = fb_pat.search(response_text)
        if m_fb is None:
            continue
        # Hay fallback pattern. ¿Menciona literalmente algún tool del catálogo?
        # Buscamos el alias como palabra word-boundary para evitar falsos positivos.
        for tool_name in available_tool_names:
            aliases = TOOL_NAME_ALIASES.get(tool_name, [tool_name])
            for alias in aliases:
                alias_pat = re.compile(
                    r"\b" + re.escape(alias) + r"\b", re.IGNORECASE
                )
                m_alias = alias_pat.search(response_text)
                if m_alias is None:
                    continue
                # Tenemos fallback + alias literal → ghost.
                start = max(0, m_alias.start() - 50)
                end = min(len(response_text), m_alias.end() + 150)
                excerpt = response_text[start:end].strip()
                if len(excerpt) > 400:
                    excerpt = excerpt[:400] + "…"
                return ResponseGhostHit(
                    suspected_tool=tool_name,
                    matched_alias=alias,
                    matched_pattern=f"{fb_pat.pattern} + alias '{alias}'",
                    offending_excerpt=excerpt,
                )

    return None
