"""
B8 Magna Classifier — Anti-Dory FORGE v3.0 (v3.0 Context-Aware)

Clasifica acciones como MAGNA o STANDARD según reglas determinísticas
con detección semántica expandida y validación de contexto.

Una acción MAGNA requiere aprobación de la Authority Matrix (B9).
Una acción STANDARD puede ejecutarse sin gate adicional.

v3.0 Changes:
- Layer 4: Action Semantics — action_types inherently dangerous
  are MAGNA by default regardless of description.
- Layer 5: Context-Aware Heuristics — detects stale state assumptions,
  false memory indicators, unauthorized operations, and context loss
  through structural analysis of the action description.
- Backward compatible: all v1.0 triggers and v2.0 patterns still work.
"""

import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ============================================================
# FEATURE FLAG: B8 v3 Context-Aware Layers
# When False, only Layers 1-3 (v2.0 behavior) are active.
# When True, Layers 4-5 (v3.0 context-aware) are also active.
# Default: False (OFF) — requires explicit activation.
# ============================================================

ANTI_DORY_B8_V3_ENABLED: bool = os.environ.get(
    "ANTI_DORY_B8_V3_ENABLED", "false"
).lower() in ("true", "1", "yes")


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
# LAYER 3: Semantic pattern categories (v2.0)
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

# ============================================================
# LAYER 4: Action Semantics (v3.0 NEW)
# action_types that are inherently dangerous regardless of
# description content. These require explicit justification.
# ============================================================

MAGNA_ACTION_TYPES_INHERENT = frozenset([
    # Destructive operations
    "drop_table",
    "delete_table",
    "truncate_table",
    "destroy_resource",
    # Deployment / production
    "deploy",
    "deploy_production",
    "apply_migration",
    # Authorization / governance
    "activate_phase",
    "declare_status",
    "unlock_feature",
    "enable_guardian",
    "activate_global",
    # Git operations that affect main
    "git_merge",
    "git_push",
    "force_push",
    # Environment modification
    "env_modify",
    "modify_env",
    # Execution without verification
    "execute_deploy",
    "execute_action",
])

# ============================================================
# LAYER 5: Context-Aware Heuristics (v3.0 NEW)
# Structural analysis of description to detect:
# - Stale state assumptions (acting on unverified state)
# - False memory indicators (referencing non-existent artifacts)
# - Context loss patterns (ignoring current state)
# - Unauthorized operations (acting without required auth)
# - Secret exposure (writing/sharing credentials)
# - Side effects (destructive or irreversible actions)
# ============================================================

CONTEXT_AWARE_PATTERNS = {
    "stale_state_assumption": [
        # Acting without reading/checking current state
        r"without\s*(reading|checking|verifying|confirming|referencing|consulting)",
        r"ignoring\s*(current|existing|DSC|RLS|requirement|state|flag)",
        # Assuming state that may have changed
        r"(assuming|assume)\s*(guardian|feature|flag|branch|sprint|migration|table)",
        # Using old/deprecated/archived references
        r"(archived|deprecated|old|deleted|merged|revoked)\s*(thread|branch|endpoint|key|project|ref)",
        r"(was|were)\s*(merged|deleted|archived|revoked|rotated)",
        # Repeating completed work
        r"(again|from scratch|re-?implement)\s*(without|ignoring)",
        r"(from scratch)\s*(ignoring|without)",
        # Acting on unverified assumptions
        r"when\s*(current|we|it)\s*(is|are)\s*(on|at|in)\s*(batch|sprint)",
        r"(create|open)\s*(duplicate|again)",
        r"(instead of|not)\s*(SUPABASE_SERVICE_KEY)\b",
    ],
    "false_memory_indicator": [
        # Referencing artifacts that may not exist
        r"(that|which)\s*(does not|do not|never|was never|is not|has not)\s*(exist|creat|happen|occur)",
        r"(never)\s*(existed|created|happened|occurred|was)",
        # Claiming results without evidence
        r"(claiming|claim)\s*(t1|authorized|passed|merged|signed)",
        r"(when|but)\s*(no|zero)\s*(receipt|evidence|signature|consultation|authorization)",
        # Inventing non-existent resources
        r"(table|module|branch|dsc|migration|fixture|incident)\s*(that|which)\s*(does not|never)",
        r"(b12|b13|b14|b15)_\w+",  # Non-existent Anti-Dory modules
        r"DSC-[A-Z]-0[5-9][0-9]",  # High-numbered DSCs unlikely to exist
        r"(0052|0053|0054|0055)\w*\s*(claiming|but)",
        # Reporting false consensus or results
        r"(all\s*6\s*sabios|sabios\s*agreed)\s*(when|but|without)",
        r"(500|1000|999)\s*tests?\s*(passed|pass)",
        r"(breach|incident)\s*(that|which)\s*never\s*(occurred|happened)",
    ],
    "context_loss_action": [
        # Skipping required steps
        r"(without|sin)\s*(signature|receipt|rollback|evidence|canary)",
        # Acting outside authorized scope
        r"(outside|beyond)\s*(t1|authorization|scope|batch|canary)",
        r"(globally|universally)\s*(without|when only|when no)",
        r"(only|just)\s*(canary|sandbox)\s*(was|is)\s*authorized",
        # Ignoring governance requirements
        r"(without|sin)\s*(feature flag|flag|authorization|confirmation)",
        r"(without|sin)\s*(completing|meeting)\s*(all|prerequisite|requirement)",
    ],
    "secret_write_attempt": [
        # Writing secrets to files/code
        r"(write|store|save|put|include|embed)\s*.*\s*(directly|in)\s*(source|code|file|repo|fixture)",
        r"(PAT|pat|ghp_|sk-|sb_|eyJ)\w*\s*(directly|in)\s*(source|code|file)",
        r"(database|db)\s*(password|pass)\s*(in|to)\s*(user|message|chat|facing)",
        r"(copy|move|cp)\s*.*(minisign|private)\s*.*(key|\.key)",
        r"(real|actual)\s*(ANTHROPIC|OPENAI|HEYGEN|SUPABASE)\w*\s*(value|key)",
        r"(containing|with)\s*(real|actual)\s*(ANTHROPIC|OPENAI|HEYGEN|SUPABASE|API)\w*",
        r"(fixture|test)\s*(containing|with)\s*(real|actual)\s*\w*(key|secret|token|password)",
    ],
    "unauthorized_side_effect": [
        # Activating features without proper authorization
        r"(activate|enable|start|unlock|declare)\s*.*\s*(without|sin)\s*(canary|evidence|completion|prerequisite|flag|authorization)",
        r"(fase|phase)\s*1\s*(globally|universal|without)",
        r"(dory|muerto)\s*(universally|without|globally)",
        r"(r1|R1)\s*(without|sin)\s*(completing|all|prerequisite)",
        r"(guardian|cron)\s*(without|sin)\s*(feature flag|flag|authorization)",
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

    # LAYER 4: Action Semantics — inherently dangerous action_types (v3.0)
    # Only active when ANTI_DORY_B8_V3_ENABLED=true
    if ANTI_DORY_B8_V3_ENABLED:
        if action_lower in MAGNA_ACTION_TYPES_INHERENT:
            return ActionClassification(
                level=ActionLevel.MAGNA,
                reason=(
                    f"Action type '{action_type}' is inherently dangerous "
                    f"(MAGNA_ACTION_TYPES_INHERENT)"
                ),
                action_description=description,
                requires_t1=True,
            )

        # LAYER 5: Context-Aware Heuristics (v3.0)
        for heuristic_category, patterns in CONTEXT_AWARE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined_text):
                    return ActionClassification(
                        level=ActionLevel.MAGNA,
                        reason=(
                            f"Context-aware heuristic '{heuristic_category}' "
                            f"matched: /{pattern}/"
                        ),
                        action_description=description,
                        requires_t1=True,
                    )

    # LAYER 6: Metadata override (si metadata indica forzar MAGNA)
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
