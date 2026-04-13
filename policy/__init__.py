"""
El Monstruo — Policy Module
Governance and compliance hooks for the sovereign AI system.
"""

from policy.matrix import (
    PolicyMatrixHook,
    PolicyMatrixPipeline,
    CostGuardHook,
    ContentFilterHook,
    classify_action,
    is_escalation_required,
    is_blocked,
    get_escalation_target,
    create_default_pipeline,
)

__all__ = [
    "PolicyMatrixHook",
    "PolicyMatrixPipeline",
    "CostGuardHook",
    "ContentFilterHook",
    "classify_action",
    "is_escalation_required",
    "is_blocked",
    "get_escalation_target",
    "create_default_pipeline",
]
