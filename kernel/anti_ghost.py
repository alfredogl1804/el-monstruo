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
