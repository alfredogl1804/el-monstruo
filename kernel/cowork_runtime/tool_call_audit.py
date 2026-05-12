"""
kernel/cowork_runtime/tool_call_audit.py — Metrica T3 binaria.

Pregunta canonica (convergencia 7 Sabios — Gemini 3.1 Pro):

  "Para esta respuesta candidata que contiene afirmaciones factuales
   fuertes, hubo tool_call exitoso en la cadena de ejecucion inmediatamente
   anterior, dentro del turno activo?"

Si SI -> los claims pueden marcarse VERIFIED_CURRENT_TURN.
Si NO + el claim es factual fuerte -> falla licencia.

Esta metrica reemplaza la metrica anterior de "advance score subjetivo"
para el caso especifico de licencia para afirmar. El advance score sigue
existiendo en tools.cowork_guardian para la doctrina anti-suggest-pause,
pero NO se usa como gate de afirmacion factual.

API:

    ctx = ToolCallContext(tool_calls_this_turn=["Read", "Bash"])
    ctx.tool_call_present  # -> True
    ctx.tool_call_present_for_claim(claim)  # -> bool por claim

El consumidor (hook integrador, orquestador) es responsable de armar
`ToolCallContext` con los tool_calls observados del turno actual. Este
modulo NO inspecciona la cadena de ejecucion por si mismo — recibe la
informacion via dataclass.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

from kernel.cowork_runtime.epistemic_labels import (
    EpistemicLabel,
    is_licensed,
    requires_tool_call,
)


# Conjunto de tool_calls que cuentan como evidencia factual fresca.
# Si el orquestador reporta solo tool_calls no-evidence (ej. logging
# interno), no cuenta como tool_call_present para el gate.
EVIDENCE_TOOLS: frozenset[str] = frozenset({
    "Read",
    "Grep",
    "Glob",
    "Bash",
    "WebFetch",
    "WebSearch",
    # MCP tools que devuelven evidencia binaria
    "mcp__supabase__execute_sql",
    "mcp__supabase__list_tables",
    "mcp__supabase__list_migrations",
    "mcp__github-monstruo__get_pull_request",
    "mcp__github-monstruo__list_commits",
    "mcp__github-monstruo__get_file_contents",
})


@dataclass
class ToolCallContext:
    """
    Snapshot de los tool_calls observados durante el turno actual de
    Cowork, mas un buffer reciente (<60min) usado para
    VERIFIED_RECENT_LT_60M.

    Args:
        tool_calls_this_turn: nombres de tools ejecutados en este turno
            (orden de ejecucion). Ej: ["Read", "Bash", "mcp__supabase__execute_sql"]
        tool_calls_last_60_min: nombres de tools ejecutados en los
            ultimos 60 minutos (incluye los del turno actual).
        evidence_tools: override del set canonico (testing).
    """
    tool_calls_this_turn: list[str] = field(default_factory=list)
    tool_calls_last_60_min: list[str] = field(default_factory=list)
    evidence_tools: Optional[frozenset[str]] = None

    def _evidence_set(self) -> frozenset[str]:
        return self.evidence_tools if self.evidence_tools is not None else EVIDENCE_TOOLS

    @property
    def tool_call_present(self) -> bool:
        """
        Pregunta T3 binaria: hubo al menos un tool_call de evidencia
        en este turno?

        Esta es la metrica canonica que reemplaza "advance score
        subjetivo" para el gate de afirmacion factual.
        """
        ev = self._evidence_set()
        return any(t in ev for t in self.tool_calls_this_turn)

    @property
    def tool_call_recent(self) -> bool:
        """True si hubo tool_call de evidencia en los ultimos 60min."""
        ev = self._evidence_set()
        return any(t in ev for t in self.tool_calls_last_60_min)

    def licensable_label_options(self) -> tuple[str, ...]:
        """
        Devuelve las etiquetas modernas que el contexto actual habilita.
        Si no hay tool_call ni en el turno ni en los ultimos 60min,
        ninguna etiqueta licenciada es legitima.
        """
        out: list[str] = []
        if self.tool_call_present:
            out.append(EpistemicLabel.VERIFIED_CURRENT_TURN.value)
        if self.tool_call_recent:
            out.append(EpistemicLabel.VERIFIED_RECENT_LT_60M.value)
        # USER_PROVIDED nunca depende de tool_call — siempre potencial
        out.append(EpistemicLabel.USER_PROVIDED.value)
        return tuple(out)

    def is_label_legitimate(self, label: Optional[str]) -> bool:
        """
        True si una etiqueta pretendida es legitima dado el contexto.

        VERIFIED_CURRENT_TURN requiere tool_call_present=True.
        VERIFIED_RECENT_LT_60M requiere tool_call_recent=True.
        USER_PROVIDED: siempre legitimable (el detector no puede saber
            si el dato lo aporto el usuario; se confia en la etiqueta).
        Las etiquetas no-licenciadas (NEEDS_*, SESSION_MEMORY_ONLY,
            INFERRED, CONTRADICTED_BY_EXTERNAL, UNVERIFIED_DO_NOT_ASSERT)
            siempre son legitimables.
        """
        if not label:
            return False
        if label == EpistemicLabel.VERIFIED_CURRENT_TURN.value:
            return self.tool_call_present
        if label == EpistemicLabel.VERIFIED_RECENT_LT_60M.value:
            return self.tool_call_recent
        # Resto: legitimable por design
        return True


def evaluate_claim_tool_call(
    claim_has_license_label: bool,
    claim_normalized_label: Optional[str],
    ctx: Optional[ToolCallContext],
) -> dict:
    """
    Evalua para un claim individual la metrica T3 binaria.

    Returns dict con:
      tool_call_present: bool — gate T3 binario (true si hubo tool_call
        de evidencia en este turno).
      license_legitimate: bool — true si la etiqueta (si la hay) es
        legitima dado el contexto.
      license_required: str | None — etiqueta minima necesaria si el
        claim no tiene licencia ni etiqueta de degradacion.
    """
    if ctx is None:
        ctx = ToolCallContext()
    tool_call_present = ctx.tool_call_present
    license_legitimate = ctx.is_label_legitimate(claim_normalized_label) if claim_has_license_label else False

    # Si claim es factual fuerte y no tiene etiqueta, lo minimo aceptable
    # es VERIFIED_CURRENT_TURN (si hay tool_call) o NEEDS_SQL/NEEDS_READ
    # / UNVERIFIED_DO_NOT_ASSERT (si no).
    if claim_normalized_label is None:
        license_required = (
            EpistemicLabel.VERIFIED_CURRENT_TURN.value
            if tool_call_present
            else EpistemicLabel.UNVERIFIED_DO_NOT_ASSERT.value
        )
    elif requires_tool_call(claim_normalized_label):
        # NEEDS_SQL / NEEDS_READ son self-declarativas, no necesitan upgrade
        license_required = claim_normalized_label
    elif is_licensed(claim_normalized_label) and not license_legitimate:
        # Pretende licencia pero no la tiene -> degradar
        license_required = EpistemicLabel.UNVERIFIED_DO_NOT_ASSERT.value
    else:
        license_required = claim_normalized_label

    return {
        "tool_call_present": tool_call_present,
        "license_legitimate": license_legitimate,
        "license_required": license_required,
    }
