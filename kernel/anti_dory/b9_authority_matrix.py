"""
B9 Authority Matrix — Anti-Dory FORGE v3.0

Implementa la matriz de autoridad con 4 capas de decisión:
1. VERIFICADOR — Validación semántica automática.
2. Memento — Memoria doctrinal (precedencia sobre VERIFICADOR para safety).
3. Guardian — Auditoría autónoma (no puede override sin T1).
4. T1 — Firma humana (override absoluto).

Reglas de precedencia (B9 Authority Matrix v1.0):
- B9.3: VERIFICADOR ALLOW + Memento DENY → Memento gana.
- B9.4: VERIFICADOR DENY + Guardian OVERRIDE → Guardian NO puede sin T1.
- B9.5: T1 firma manual + VERIFICADOR DENY → T1 gana, log T1_OVERRIDE.
- B9.6: VERIFICADOR falla → VERIFICADOR_DEGRADED + B8 DISABLED_FOR_MAGNA.
- B9.7: Memento falla → Acciones magnas bloqueadas.
- B9.8: Guardian falla → AWAITING_GUARDIAN, no auto-decisión.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Decision(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    HALT = "HALT"
    WAIT = "WAIT"
    AWAITING_GUARDIAN = "AWAITING_GUARDIAN"


class SystemState(Enum):
    HEALTHY = "HEALTHY"
    VERIFICADOR_DEGRADED = "VERIFICADOR_DEGRADED"
    MEMENTO_DEGRADED = "MEMENTO_DEGRADED"
    GUARDIAN_DEGRADED = "GUARDIAN_DEGRADED"


class LayerStatus(Enum):
    OK = "OK"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


@dataclass
class LayerVote:
    decision: Decision
    status: LayerStatus = LayerStatus.OK
    reason: str = ""


@dataclass
class AuthorityResult:
    final_decision: Decision
    system_state: SystemState
    log_entries: list = field(default_factory=list)
    b8_disabled: bool = False


class AuthorityMatrix:
    """
    Resuelve la decisión final basándose en los votos de las 4 capas.
    """

    def resolve(
        self,
        verificador: Optional[LayerVote] = None,
        memento: Optional[LayerVote] = None,
        guardian: Optional[LayerVote] = None,
        t1: Optional[LayerVote] = None,
    ) -> AuthorityResult:
        """
        Resuelve la decisión final aplicando las reglas de precedencia B9.

        Args:
            verificador: Voto del VERIFICADOR (puede ser None si degradado).
            memento: Voto del Memento (puede ser None si degradado).
            guardian: Voto del Guardian (puede ser None si degradado).
            t1: Voto de T1 (puede ser None si no firmó).

        Returns:
            AuthorityResult con decisión final, estado del sistema y logs.
        """
        logs = []
        state = SystemState.HEALTHY
        b8_disabled = False

        # === Degradation checks (B9.6, B9.7, B9.8) ===

        # B9.6: VERIFICADOR falla
        if verificador is None or verificador.status != LayerStatus.OK:
            state = SystemState.VERIFICADOR_DEGRADED
            b8_disabled = True
            logs.append("VERIFICADOR_DEGRADED: B8 DISABLED_FOR_MAGNA_ACTIONS")
            # Si Memento también está degradado, HALT
            if memento is None or memento.status != LayerStatus.OK:
                logs.append("MEMENTO_DEGRADED: magna actions blocked")
                return AuthorityResult(
                    final_decision=Decision.HALT,
                    system_state=SystemState.MEMENTO_DEGRADED,
                    log_entries=logs,
                    b8_disabled=True,
                )
            # Con VERIFICADOR degradado pero Memento OK, usar Memento
            return AuthorityResult(
                final_decision=Decision.HALT,
                system_state=state,
                log_entries=logs,
                b8_disabled=b8_disabled,
            )

        # B9.7: Memento falla
        if memento is None or memento.status != LayerStatus.OK:
            state = SystemState.MEMENTO_DEGRADED
            logs.append("MEMENTO_DEGRADED: magna actions blocked")
            return AuthorityResult(
                final_decision=Decision.HALT,
                system_state=state,
                log_entries=logs,
                b8_disabled=False,
            )

        # B9.8: Guardian falla
        if guardian is None or guardian.status != LayerStatus.OK:
            state = SystemState.GUARDIAN_DEGRADED
            logs.append("GUARDIAN_DEGRADED: AWAITING_GUARDIAN, no auto-decision")
            return AuthorityResult(
                final_decision=Decision.AWAITING_GUARDIAN,
                system_state=state,
                log_entries=logs,
                b8_disabled=False,
            )

        # === All layers healthy — apply precedence rules ===

        # B9.5: T1 override (highest priority)
        if t1 is not None and t1.status == LayerStatus.OK:
            if t1.decision != verificador.decision:
                logs.append(f"T1_OVERRIDE_VERIFICADOR_{verificador.decision.value}")
            logs.append(f"T1_DECISION: {t1.decision.value}")
            return AuthorityResult(
                final_decision=t1.decision,
                system_state=state,
                log_entries=logs,
                b8_disabled=False,
            )

        # B9.3: Memento overrides VERIFICADOR for safety
        if verificador.decision == Decision.ALLOW and memento.decision == Decision.DENY:
            logs.append("B9.3: Memento DENY overrides VERIFICADOR ALLOW (safety)")
            return AuthorityResult(
                final_decision=Decision.DENY,
                system_state=state,
                log_entries=logs,
                b8_disabled=False,
            )

        # B9.4: Guardian cannot override VERIFICADOR DENY without T1
        if verificador.decision == Decision.DENY and guardian.decision == Decision.ALLOW:
            logs.append("B9.4: Guardian ALLOW cannot override VERIFICADOR DENY without T1")
            return AuthorityResult(
                final_decision=Decision.DENY,
                system_state=state,
                log_entries=logs,
                b8_disabled=False,
            )

        # Agreement cases (B9.1, B9.2, B9.3 for HALT, B9.4 for WAIT)
        if verificador.decision == memento.decision == guardian.decision:
            decision = verificador.decision
            if decision == Decision.WAIT:
                decision = Decision.AWAITING_GUARDIAN
            logs.append(f"UNANIMOUS: {decision.value}")
            return AuthorityResult(
                final_decision=decision,
                system_state=state,
                log_entries=logs,
                b8_disabled=False,
            )

        # Default: most conservative wins
        priority = [Decision.HALT, Decision.DENY, Decision.WAIT, Decision.ALLOW]
        votes = [verificador.decision, memento.decision, guardian.decision]
        for p in priority:
            if p in votes:
                logs.append(f"CONSERVATIVE_DEFAULT: {p.value}")
                final = Decision.AWAITING_GUARDIAN if p == Decision.WAIT else p
                return AuthorityResult(
                    final_decision=final,
                    system_state=state,
                    log_entries=logs,
                    b8_disabled=False,
                )

        # Fallback (should never reach)
        return AuthorityResult(
            final_decision=Decision.HALT,
            system_state=state,
            log_entries=["FALLBACK_HALT"],
            b8_disabled=False,
        )
