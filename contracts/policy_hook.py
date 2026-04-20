"""
El Monstruo — Contrato Soberano #4: PolicyHook
================================================
Define el contrato para hooks de políticas y gobernanza.
Cada decisión del sistema pasa por PolicyHooks que pueden
aprobar, bloquear, modificar o escalar acciones.

Principio: El Monstruo tiene reglas propias. Ningún modelo
externo decide qué está permitido — las políticas sí.
"""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4


class PolicyVerdict(enum.Enum):
    """Resultado de la evaluación de una política."""

    ALLOW = "allow"  # Acción permitida, continuar
    BLOCK = "block"  # Acción bloqueada, no ejecutar
    MODIFY = "modify"  # Acción permitida con modificaciones
    ESCALATE = "escalate"  # Requiere aprobación humana
    LOG_ONLY = "log_only"  # Permitir pero registrar para auditoría


class PolicyPhase(enum.Enum):
    """Fase del ciclo de vida donde se evalúa la política."""

    PRE_ROUTE = "pre_route"  # Antes de decidir qué modelo usar
    POST_ROUTE = "post_route"  # Después de routing, antes de ejecución
    PRE_EXECUTE = "pre_execute"  # Antes de ejecutar con el modelo
    POST_EXECUTE = "post_execute"  # Después de ejecutar, antes de responder
    PRE_TOOL = "pre_tool"  # Antes de llamar una herramienta
    POST_TOOL = "post_tool"  # Después de llamar una herramienta
    PRE_RESPOND = "pre_respond"  # Antes de enviar respuesta al usuario
    ON_ERROR = "on_error"  # Cuando ocurre un error


@dataclass(frozen=True)
class PolicyContext:
    """Contexto completo para evaluar una política."""

    run_id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    channel: str = ""
    phase: PolicyPhase = PolicyPhase.PRE_EXECUTE
    intent: str = ""
    model: str = ""
    message: str = ""
    tool_name: Optional[str] = None
    tool_args: Optional[dict[str, Any]] = None
    response: Optional[str] = None
    cost_usd: float = 0.0
    tokens_used: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyDecision:
    """Resultado de evaluar una política."""

    decision_id: UUID = field(default_factory=uuid4)
    policy_name: str = ""
    verdict: PolicyVerdict = PolicyVerdict.ALLOW
    reason: str = ""
    modifications: Optional[dict[str, Any]] = None
    escalation_target: Optional[str] = None  # "telegram", "console"
    evaluated_at: datetime = field(default_factory=datetime.utcnow)


# ── Policy Hook Contract ────────────────────────────────────────────


class PolicyHook(ABC):
    """
    Contrato soberano para hooks de política.

    Cada PolicyHook evalúa una regla específica. Se pueden
    encadenar múltiples hooks en un pipeline de evaluación.

    Ejemplos de políticas:
        - CostGuard: bloquear si el costo acumulado > $X/día
        - ContentFilter: filtrar respuestas con contenido sensible
        - RateLimit: limitar requests por usuario/canal
        - ToolApproval: requerir aprobación para herramientas peligrosas
        - ModelRestriction: forzar modelo específico para ciertos usuarios
        - AuditLog: registrar todas las acciones sin bloquear
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre único de la política."""
        ...

    @property
    @abstractmethod
    def phase(self) -> PolicyPhase:
        """Fase donde se evalúa esta política."""
        ...

    @property
    def priority(self) -> int:
        """Prioridad de evaluación (menor = primero). Default: 100."""
        return 100

    @property
    def enabled(self) -> bool:
        """Si la política está activa. Default: True."""
        return True

    @abstractmethod
    async def evaluate(self, context: PolicyContext) -> PolicyDecision:
        """
        Evalúa la política dado el contexto.
        Retorna la decisión con veredicto y razón.
        """
        ...


# ── Policy Pipeline ─────────────────────────────────────────────────


class PolicyPipeline(ABC):
    """
    Pipeline que encadena múltiples PolicyHooks.
    Evalúa en orden de prioridad. Si alguno bloquea, se detiene.
    """

    @abstractmethod
    async def register(self, hook: PolicyHook) -> None:
        """Registra un hook en el pipeline."""
        ...

    @abstractmethod
    async def unregister(self, policy_name: str) -> bool:
        """Desregistra un hook por nombre."""
        ...

    @abstractmethod
    async def evaluate_all(
        self,
        context: PolicyContext,
    ) -> list[PolicyDecision]:
        """
        Evalúa todas las políticas activas para la fase dada.
        Retorna lista de decisiones. Si alguna es BLOCK, la acción
        no debe ejecutarse.
        """
        ...

    @abstractmethod
    async def get_active_policies(
        self,
        phase: Optional[PolicyPhase] = None,
    ) -> list[PolicyHook]:
        """Lista las políticas activas, opcionalmente filtradas por fase."""
        ...
