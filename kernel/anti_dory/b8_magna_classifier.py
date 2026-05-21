"""
B8 Magna Classifier — Anti-Dory FORGE v3.0 (v2.0 Semantic Expansion)

Clasifica acciones como MAGNA o STANDARD según reglas determinísticas
con detección semántica expandida.

Una acción MAGNA requiere aprobación de la Authority Matrix (B9).
Una acción STANDARD puede ejecutarse sin gate adicional.

v2.0 Changes:
- Expanded from 7 danger keywords to 10 semantic categories.
- Added pattern-based detection for indirect dangerous actions.
- Added combined-signal detection (action_type + description).
- Backward compatible: all v1.0 triggers still work.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ActionLevel(Enum):
    MAGNA = "MAGNA"
    STANDARD = "STANDARD"


@dataclass
class ActionClassification:
    level: ActionLevel
    reason: str
    action_description: str
    requires_t1: bool


# ============================================================
# LAYER 1: Exact action_type triggers (v1.0 backward compat)
# ============================================================

MAGNA_TRIGGERS = frozenset([
    "merge_to_main",
    "push_to_main",
    "supabase_write_production",
    "deploy_production",
    "modify_credentials",
    "rotate_secrets",
    "declare_dory_dead",
    "approve_r1",
    "phase_1_action",
    "sign_dsc",
    "create_pr",
    "delete_table",
    "drop_migration",
    "override_guardian",
    "disable_rls",
    "expose_private_key",
])

# ============================================================
# LAYER 2: Keyword detection in action_type (v1.0 backward compat)
# ============================================================

DANGER_KEYWORDS_ACTION_TYPE = [
    "main", "production", "credential", "secret",
    "dory_dead", "phase_1", "private_key",
]

# ============================================================
# LAYER 3: Semantic pattern categories (v2.0 NEW)
# Detects dangerous INTENT across action_type + description.
# ============================================================

SEMANTIC_CATEGORIES = {
    "bypass_guardian": [
        r"(skip|bypass|ignore|disable|override)\s*(guardian|agents\.md|identity|monstruo)",
        r"(without|sin)\s*(guardian|verification|validation|checking)",
        r"skip\s*(reading|execution|running)\s*(agents|guardian)",
        r"ignore\s*(agents\.md|guardian\.py)",
        r"overwrite\s*\.?monstruo",
    ],
    "stale_state": [
        r"(assume|stale|cached|outdated|old)\s*(state|session|credentials?|schema|deploy|branch|sprint|version|file)",
        r"without\s*(check|verif|re-?read|reading|validat)",
        r"(7|30|60|90)\s*days?\s*ago",
        r"previous\s*session\s*state",
        r"(deleted|removed)\s*(branch|ref)",
        r"reference\s*sprint\s*\d+.*sprint\s*\d+",
    ],
    "unauthorized_api": [
        r"(without|sin)\s*(t1|authorization|approval|budget|permission)",
        r"unauthorized\s*(api|email|publish|dns|access)",
        r"(paid|external)\s*(service|api)\s*(without|sin)",
        r"unbudgeted",
    ],
    "hidden_side_effects": [
        r"(without|sin)\s*(migration|backup|file|tracking|review)",
        r"(untracked|hidden)\s*(table|change|effect|side)",
        r"(enable|activate|start)\s*(cron|scheduler|job)\s*(in|on)?\s*(prod|production)",
        r"(modify|change|update)\s*(env|environment|railway|variable)",
        r"(railway|vercel|heroku)\s.*(variable|env|config)",
        r"environment\s*variable.*direct",
        r"(open|expose)\s*port",
        r"(trigger|fire|send)\s*webhook",
        r"(create|add)\s*(dns|record|table)\s*(without|sin)",
    ],
    "context_loss": [
        r"(rm|delete|remove|drop|destroy)\s*(-rf\s*)?(kernel|table|migration|database|\.monstruo|identity)",
        r"(force|--force)\s*(push|rebase|reset|drop)",
        r"(supabase|db)\s*(push|reset|drop)\s*--force",
        r"(deploy|push)\s*(to|without)\s*(prod|production|ci)",
        r"(git\s*)?(rebase|reset)\s*(-i\s*)?(main|--force)",
        r"drop\s*table",
    ],
    "false_memory": [
        r"(claim|assert|report|declare)\s*.*(passed|merged|applied|active|dead|unblocked|signed|authorized)",
        r"(false|phantom|inflated|premature|hallucinated)",
        r"(does not|do not|is not|was not)\s*exist",
        r"(it is still|still)\s*(draft|blocked|off|pending)",
        r"(no such|no\s*signature|no\s*authorization)",
    ],
    "privilege_escalation": [
        r"(escalat|elevat|promot)\w*\s*(privilege|role|access|permission)",
        r"(grant|give)\s*(admin|superuser|service_role|root)",
        r"(disable|bypass|override)\s*(rls|policy|security|auth)",
        r"(impersonat|spoof|forge)\w*\s*(identity|token|user)",
    ],
    "cost_billing": [
        r"(paid|billing|cost|charge|spend|budget)\s*(api|service|call|action)",
        r"(without|sin)\s*(budget|cost|billing)\s*(check|approval|limit)",
        r"(expensive|costly)\s*(operation|call|query)",
    ],
    "secret_exposure": [
        r"(echo|print|log|write|send|share|upload|commit|expose|store|include)\s*.*"
        r"(key|secret|token|password|credential|jwt|api.?key|private.?key|\.env|service.?key)",
        r"(SUPABASE|OPENAI|ANTHROPIC|HEYGEN|DROPBOX|ELEVENLABS|GEMINI|XAI|SONAR|CLOUDFLARE)"
        r".*(_KEY|_TOKEN|_SECRET|_PASSWORD)",
        r"eyj[a-z0-9]",
        r"(exfiltrat|leak|expos)\s*(key|secret|token|cred)",
        r"(public|external)\s*(repo|webhook|endpoint).*\.(env|key|pem|secret)",
    ],
    "production_impact": [
        r"(production|prod)\s*(write|delete|modify|update|push|deploy|enable|disable)",
        r"(apply|run|execute)\s*(migration|schema)\s*(to|on|in)\s*(prod|production|live)",
        r"(npm|docker|registry)\s*(publish|push)\s*(without|sin)",
        r"(railway|vercel|supabase)\s*(env|variable|config)\s*(modify|change|update|delete)",
    ],
}


def classify_action(
    action_type: str,
    description: str,
    metadata: Optional[dict] = None,
) -> ActionClassification:
    """
    Clasifica una acción como MAGNA o STANDARD.

    Args:
        action_type: Identificador del tipo de acción (ej. "merge_to_main").
        description: Descripción legible de la acción.
        metadata: Contexto adicional opcional.

    Returns:
        ActionClassification con nivel, razón y si requiere T1.
    """
    action_lower = action_type.lower().strip()

    # LAYER 1: Coincidencia directa con triggers
    if action_lower in MAGNA_TRIGGERS:
        return ActionClassification(
            level=ActionLevel.MAGNA,
            reason=f"Action type '{action_type}' is in MAGNA_TRIGGERS set",
            action_description=description,
            requires_t1=True,
        )

    # LAYER 2: Coincidencia parcial con keywords en action_type
    for keyword in DANGER_KEYWORDS_ACTION_TYPE:
        if keyword in action_lower:
            return ActionClassification(
                level=ActionLevel.MAGNA,
                reason=f"Action type contains danger keyword '{keyword}'",
                action_description=description,
                requires_t1=True,
            )

    # LAYER 3: Semantic pattern matching across action_type + description
    combined_text = f"{action_type} {description}".lower()

    for category, patterns in SEMANTIC_CATEGORIES.items():
        for pattern in patterns:
            if re.search(pattern, combined_text):
                return ActionClassification(
                    level=ActionLevel.MAGNA,
                    reason=f"Semantic category '{category}' matched: /{pattern}/",
                    action_description=description,
                    requires_t1=True,
                )

    # LAYER 4: Metadata override (si metadata indica forzar MAGNA)
    if metadata and metadata.get("force_magna", False):
        return ActionClassification(
            level=ActionLevel.MAGNA,
            reason="Metadata flag 'force_magna' is True",
            action_description=description,
            requires_t1=True,
        )

    # Default: STANDARD
    return ActionClassification(
        level=ActionLevel.STANDARD,
        reason="No MAGNA triggers matched",
        action_description=description,
        requires_t1=False,
    )
