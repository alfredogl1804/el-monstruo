"""
El Monstruo — Policy Matrix (Convergencia Sprint 1)
=====================================================
Implementa el contrato soberano PolicyHook usando la Policy Matrix
de 5 clases y 12 acciones del Hilo Bot.

Origen: exports/policy_matrix.py del Hilo Bot (@MounstroBot)
Integración: Implementa contracts/policy_hook.py (PolicyHook ABC)
"""

from __future__ import annotations

import re
from typing import Any, Optional

import structlog

from contracts.policy_hook import (
    PolicyContext,
    PolicyDecision,
    PolicyHook,
    PolicyPhase,
    PolicyPipeline,
    PolicyVerdict,
)

logger = structlog.get_logger("policy.matrix")


# ===================== POLICY MATRIX — 5 CLASES, 12 ACCIONES =====================

# Clase 1: Financiera (dinero real)
FINANCIAL_ACTIONS = {
    "pagar", "transferir", "comprar", "invertir", "reembolsar",
    "pay", "transfer", "buy", "invest", "refund",
    "cobrar", "facturar", "cotizar",
}

# Clase 2: Comunicación externa (reputación)
COMMS_ACTIONS = {
    "publicar", "enviar", "responder", "postear", "tuitear",
    "publish", "send", "reply", "post", "tweet",
    "email", "whatsapp", "telegram",
}

# Clase 3: Datos sensibles (privacidad)
DATA_ACTIONS = {
    "borrar", "eliminar", "modificar", "exportar", "compartir",
    "delete", "remove", "modify", "export", "share",
    "migrar", "resetear",
}

# Clase 4: Infraestructura (estabilidad)
INFRA_ACTIONS = {
    "desplegar", "deploy", "rollback", "escalar", "reiniciar",
    "scale", "restart", "shutdown", "update", "upgrade",
    "configurar", "instalar",
}

# Clase 5: Información (bajo riesgo)
INFO_ACTIONS = {
    "buscar", "analizar", "resumir", "investigar", "comparar",
    "search", "analyze", "summarize", "research", "compare",
    "listar", "consultar", "explicar",
}


# ── Risk levels per class ──────────────────────────────────────────

CLASS_RISK: dict[str, dict[str, Any]] = {
    "financial": {
        "keywords": FINANCIAL_ACTIONS,
        "risk": "critical",
        "default_verdict": PolicyVerdict.ESCALATE,
        "reason": "Acción financiera requiere aprobación humana",
        "escalation_target": "telegram",
    },
    "communications": {
        "keywords": COMMS_ACTIONS,
        "risk": "high",
        "default_verdict": PolicyVerdict.ESCALATE,
        "reason": "Comunicación externa requiere revisión",
        "escalation_target": "telegram",
    },
    "data": {
        "keywords": DATA_ACTIONS,
        "risk": "high",
        "default_verdict": PolicyVerdict.ESCALATE,
        "reason": "Operación sobre datos sensibles requiere aprobación",
        "escalation_target": "telegram",
    },
    "infrastructure": {
        "keywords": INFRA_ACTIONS,
        "risk": "medium",
        "default_verdict": PolicyVerdict.LOG_ONLY,
        "reason": "Operación de infraestructura registrada para auditoría",
        "escalation_target": None,
    },
    "information": {
        "keywords": INFO_ACTIONS,
        "risk": "low",
        "default_verdict": PolicyVerdict.ALLOW,
        "reason": "Operación informativa — permitida sin restricción",
        "escalation_target": None,
    },
}


# ===================== POLICY HOOKS (implementing PolicyHook ABC) =====================

class PolicyMatrixHook(PolicyHook):
    """
    Main policy hook that classifies actions into 5 risk classes
    and applies the corresponding verdict.
    """

    @property
    def name(self) -> str:
        return "policy_matrix"

    @property
    def phase(self) -> PolicyPhase:
        return PolicyPhase.PRE_EXECUTE

    @property
    def priority(self) -> int:
        return 10  # High priority — runs first

    async def evaluate(self, context: PolicyContext) -> PolicyDecision:
        """Classify the action and return the appropriate verdict."""
        action_class = classify_action(context.message)
        class_config = CLASS_RISK.get(action_class, CLASS_RISK["information"])

        verdict = class_config["default_verdict"]
        reason = class_config["reason"]

        logger.info(
            "policy_matrix_evaluated",
            action_class=action_class,
            risk=class_config["risk"],
            verdict=verdict.value,
            message_preview=context.message[:80],
        )

        return PolicyDecision(
            policy_name=self.name,
            verdict=verdict,
            reason=reason,
            escalation_target=class_config.get("escalation_target"),
            modifications={"action_class": action_class, "risk": class_config["risk"]},
        )


class CostGuardHook(PolicyHook):
    """
    Blocks requests if daily cost exceeds the configured limit.
    """

    def __init__(self, daily_limit_usd: float = 50.0) -> None:
        self._daily_limit = daily_limit_usd
        self._daily_cost: float = 0.0

    @property
    def name(self) -> str:
        return "cost_guard"

    @property
    def phase(self) -> PolicyPhase:
        return PolicyPhase.PRE_EXECUTE

    @property
    def priority(self) -> int:
        return 5  # Runs before policy_matrix

    async def evaluate(self, context: PolicyContext) -> PolicyDecision:
        """Check if daily cost limit has been exceeded."""
        if self._daily_cost >= self._daily_limit:
            logger.warning(
                "cost_guard_blocked",
                daily_cost=self._daily_cost,
                limit=self._daily_limit,
            )
            return PolicyDecision(
                policy_name=self.name,
                verdict=PolicyVerdict.BLOCK,
                reason=f"Límite diario de ${self._daily_limit} USD alcanzado. "
                       f"Costo acumulado: ${self._daily_cost:.2f}",
            )

        return PolicyDecision(
            policy_name=self.name,
            verdict=PolicyVerdict.ALLOW,
            reason=f"Costo diario OK: ${self._daily_cost:.2f} / ${self._daily_limit}",
        )

    def add_cost(self, cost_usd: float) -> None:
        """Track cost after execution."""
        self._daily_cost += cost_usd

    def reset_daily(self) -> None:
        """Reset daily counter (call at midnight)."""
        self._daily_cost = 0.0


class ContentFilterHook(PolicyHook):
    """
    Filters responses that contain sensitive content patterns.
    """

    SENSITIVE_PATTERNS = [
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card numbers
        r"\b[A-Z]{4}\d{6}[A-Z0-9]{8}\b",                  # CURP (Mexico)
        r"\b\d{3}-?\d{2}-?\d{4}\b",                        # SSN
        r"(?i)contraseña|password|secret|api.?key",         # Credentials
    ]

    @property
    def name(self) -> str:
        return "content_filter"

    @property
    def phase(self) -> PolicyPhase:
        return PolicyPhase.POST_EXECUTE

    @property
    def priority(self) -> int:
        return 20

    async def evaluate(self, context: PolicyContext) -> PolicyDecision:
        """Check response for sensitive content."""
        text = context.response or ""

        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, text):
                logger.warning(
                    "content_filter_triggered",
                    pattern=pattern,
                    message_preview=text[:80],
                )
                return PolicyDecision(
                    policy_name=self.name,
                    verdict=PolicyVerdict.MODIFY,
                    reason=f"Contenido sensible detectado (patrón: {pattern})",
                    modifications={"redact_pattern": pattern},
                )

        return PolicyDecision(
            policy_name=self.name,
            verdict=PolicyVerdict.ALLOW,
            reason="Sin contenido sensible detectado",
        )


# ===================== POLICY PIPELINE IMPLEMENTATION =====================

class PolicyMatrixPipeline(PolicyPipeline):
    """
    Concrete implementation of PolicyPipeline using the 5-class matrix.
    Evaluates hooks in priority order. Stops on first BLOCK.
    """

    def __init__(self) -> None:
        self._hooks: list[PolicyHook] = []

    async def register(self, hook: PolicyHook) -> None:
        """Register a hook in the pipeline."""
        self._hooks.append(hook)
        self._hooks.sort(key=lambda h: h.priority)
        logger.info("policy_registered", name=hook.name, priority=hook.priority)

    async def unregister(self, policy_name: str) -> bool:
        """Unregister a hook by name."""
        before = len(self._hooks)
        self._hooks = [h for h in self._hooks if h.name != policy_name]
        removed = len(self._hooks) < before
        if removed:
            logger.info("policy_unregistered", name=policy_name)
        return removed

    async def evaluate_all(
        self,
        context: PolicyContext,
    ) -> list[PolicyDecision]:
        """
        Evaluate all active policies for the given phase.
        Returns list of decisions. If any is BLOCK, action should not execute.
        """
        decisions: list[PolicyDecision] = []

        active = [h for h in self._hooks if h.enabled and h.phase == context.phase]

        for hook in active:
            try:
                decision = await hook.evaluate(context)
                decisions.append(decision)

                if decision.verdict == PolicyVerdict.BLOCK:
                    logger.warning(
                        "policy_blocked",
                        policy=hook.name,
                        reason=decision.reason,
                    )
                    break  # Stop on first BLOCK

            except Exception as e:
                logger.error(
                    "policy_evaluation_error",
                    policy=hook.name,
                    error=str(e),
                )
                # On error, allow but log
                decisions.append(PolicyDecision(
                    policy_name=hook.name,
                    verdict=PolicyVerdict.LOG_ONLY,
                    reason=f"Error evaluando política: {e}",
                ))

        return decisions

    async def get_active_policies(
        self,
        phase: Optional[PolicyPhase] = None,
    ) -> list[PolicyHook]:
        """List active policies, optionally filtered by phase."""
        hooks = [h for h in self._hooks if h.enabled]
        if phase:
            hooks = [h for h in hooks if h.phase == phase]
        return hooks


# ===================== HELPER FUNCTIONS =====================

def classify_action(message: str) -> str:
    """
    Classify a message into one of the 5 action classes.
    Returns the class name: financial, communications, data, infrastructure, information.
    """
    msg_lower = message.lower()
    words = set(msg_lower.split())

    # Check each class in risk order (highest first)
    for class_name in ["financial", "communications", "data", "infrastructure", "information"]:
        keywords = CLASS_RISK[class_name]["keywords"]
        if words & keywords:
            return class_name

    return "information"  # Default: lowest risk


def is_escalation_required(decisions: list[PolicyDecision]) -> bool:
    """Check if any decision requires escalation."""
    return any(d.verdict == PolicyVerdict.ESCALATE for d in decisions)


def is_blocked(decisions: list[PolicyDecision]) -> bool:
    """Check if any decision blocks the action."""
    return any(d.verdict == PolicyVerdict.BLOCK for d in decisions)


def get_escalation_target(decisions: list[PolicyDecision]) -> Optional[str]:
    """Get the escalation target from the first ESCALATE decision."""
    for d in decisions:
        if d.verdict == PolicyVerdict.ESCALATE and d.escalation_target:
            return d.escalation_target
    return None


async def create_default_pipeline() -> PolicyMatrixPipeline:
    """
    Create a pipeline with the default set of policy hooks.
    Call this during app startup.
    """
    pipeline = PolicyMatrixPipeline()
    await pipeline.register(CostGuardHook(daily_limit_usd=50.0))
    await pipeline.register(PolicyMatrixHook())
    await pipeline.register(ContentFilterHook())
    return pipeline
