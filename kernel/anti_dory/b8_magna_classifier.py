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

ANTI_DORY_B8_V3_ENABLED: bool = os.environ.get("ANTI_DORY_B8_V3_ENABLED", "false").lower() in ("true", "1", "yes")


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

MAGNA_TRIGGERS = frozenset(
    [
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
    ]
)

# ============================================================
# LAYER 2: Keyword detection in action_type (v1.0 backward compat)
# ============================================================

DANGER_KEYWORDS_ACTION_TYPE = [
    "main",
    "production",
    "credential",
    "secret",
    "dory_dead",
    "phase_1",
    "private_key",
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
#
# NOTE: This list intentionally avoids broad action types like
# "git_push" because not every push is dangerous (feature-branch
# pushes are routine). For git pushes, use the explicit dangerous
# variants below (push_to_main, force_push_main, push_production)
# OR pass metadata.target_branch and rely on Layer 5.5
# branch-aware escalation.
# ============================================================

MAGNA_ACTION_TYPES_INHERENT = frozenset(
    [
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
        # Git operations that affect main / production
        # NOTE: broad "git_push" intentionally REMOVED to avoid escalating
        # benign feature-branch pushes. Use explicit dangerous variants.
        "git_merge",
        "push_to_main",
        "force_push_main",
        "force_push",
        "push_production",
        "push_to_production",
        # Environment modification
        "env_modify",
        "modify_env",
        # Execution without verification
        "execute_deploy",
        "execute_action",
    ]
)

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


# ============================================================
# LAYER 6 IMPLEMENTATION: Adversarial Evasion Detection
# ============================================================

import base64
import codecs

# 6A: Fragmentation patterns — multi-step sequences that compose a magna action
_FRAGMENTATION_PATTERNS = [
    # Dangerous runtime mutations
    r"(mutando|mutating|modifying)\s*(la)?\s*(pol\u00edtica|policy|RLS|rls)",
    r"(desactivando|deactivating|disabling)\s*(temporalmente|temporarily)?\s*(el)?\s*(flag|feature)",
    r"(enviando|sending)\s*(payload|request|data).*\s*(webhook|stripe|payment|live)",
    r"(reescribiendo|rewriting|overwriting)\s*(el)?\s*(historial|history|anchor|store|log)",
    r"(invocando|invoking|calling)\s*(la)?\s*(API|api).*\s*(regeneraci\u00f3n|regenerat|rotation|llaves|keys|maestras|master)",
    # Multi-step sequences that together form dangerous operations
    r"(primero|first|luego|then|después|after)\s*.*(merge|push|deploy|drop|delete|update|modify)",
    r"(paso|step)\s*\d+.*\s*(paso|step)\s*\d+",
    r"(git push.*luego|push.*then)\s*(merge|update|deploy)",
    r"(merge manual|manual merge)",
    r"(script|backup).*\s*(ya|already)\s*(tengo|have|listo|ready)",
    r"(limpieza|cleanup|clean).*\s*(huérfano|orphan|artefact)",
    r"(alinear|align)\s*(repositorio|repo)",
    # Chained operations that individually seem safe
    r"(haré|voy a|will)\s*(un|a)\s*(git push|merge|deploy|drop|force)",
    r"(ejecutando|running|executing)\s*(script|command).*\s*(drop|cascade|truncate|delete)",
    r"(temporalmente|temporarily)\s*(desactiv|disabl|remov|delet)",
    r"(saltar|skip|omit)\s*(el|the)?\s*(step|paso|audit|check|validat)",
]

# 6B: Semantic Inversion / Double Negation — intent hidden via negation
_INVERSION_PATTERNS = [
    # Double negation that hides true intent
    r"no\s*(voy a|haré)\s*(hacer|do)\s*(merge|push|deploy)\s*(sin|without)\s*(revisar|check)",
    r"(confirmo|confirm)\s*(que|that)\s*no\s*(hay|there is no)\s*(drift|error|problem)",
    r"(asegurar|ensure).*\s*(alineación|alignment|estrategia|strategy)",
    # Indirect permission seeking (Dory probe)
    r"(¿podrías|could you|can you)\s*(confirmar|confirm|recordar|remind|proveer|provide)",
    r"(¿me recuerdas|remind me|do you remember)",
    r"(¿cuál era|what was)\s*(exactamente|exactly)",
    # Reassurance-seeking that masks context loss
    r"(para asegurar|to ensure|to make sure)\s*(nuestra|our)\s*(alineación|alignment)",
    r"(retomemos|let's restart|empecemos de nuevo|start over)",
    r"(favor de proveer|please provide|necesito que me)\s*(el esquema|the schema|resumas|summarize)",
]

# 6C: Encoding/Obfuscation detection
_ENCODING_INDICATORS = [
    r"(clave privada|private key)\s*(ed25519|rsa|ecdsa|dsa)",
    r"volcado\s*(hexadecimal|hex)",
    r"(hex|hexadecimal)\s*:?\s*[`'\"]{0,1}[0-9a-f]{6,}",
    r"[0-9a-f]{2}(\s[0-9a-f]{2}){5,}",  # Hex bytes with spaces
    r"(base64|b64)\s*:?\s*[A-Za-z0-9+/=]{8,}",
    r"(rot13|caesar|cifrado|encoded|codificado)",
    r"(concatenaci\u00f3n|concatenation)\s*(de|of)\s*\W?\w+\W?\s*(y|and|\+)",
    r"(token|key|secret)\s*(es|is)\s*(la)?\s*(concatenación|concatenation|combination)",
    r"(pre-firmada|presigned|signed)\s*(url|URL)",
    r"(volcado|dump)\s*(de)?\s*(variables|env|environment|contenedor|container|docker)",
    r"(header|encabezado)\s*(Authorization|Bearer)\s*:?\s*(Bearer)?\s*\[",
    # Detect actual hex/base64 encoded secrets inline
    r"[0-9a-f]{16,}",  # Long hex strings
    r"eyJ[A-Za-z0-9_-]{10,}",  # JWT tokens (already in L3 but reinforced)
    r"sbp_[a-z0-9]{8,}",  # Supabase PAT
    r"ghp_[A-Za-z0-9]{20,}",  # GitHub PAT
    r"sk-[A-Za-z0-9]{20,}",  # OpenAI key
    r"sk-ant-[A-Za-z0-9]{20,}",  # Anthropic key
]

# 6D: Dory Probes — questions that reveal context loss without using keywords
_DORY_PROBE_PATTERNS = [
    # Asking for information that should be in context
    r"(¿|\?).*\s*(backend|BD|base de datos|database)\s*(es|is)\s*(relacional|NoSQL|SQL)",
    r"(reviso|check)\s*(mi|my)\s*(caché|cache).*\s*(discontinuidad|gap|error)",
    r"(debido a|due to)\s*(la longitud|the length|lo largo)\s*(del hilo|of the thread)",
    r"(no tengo|don't have|sin)\s*(visibilidad|visibility|access)\s*(del|to|of)\s*(anchor|store|state)",
    r"(asumiré|will assume|asumo)\s*(que|that)\s*(los valores|values|it)\s*(son|are|is)\s*(estándar|standard|default)",
    r"(iniciando|starting|beginning)\s*(análisis|analysis).*\s*(proveer|provide|give me)\s*(el esquema|the schema)",
    r"(como no tengo|since I don't have|as I lack)",
    r"(necesito que me|I need you to)\s*(resumas|summarize|expliques|explain)",
]

# 6E: Conviction-based False Memory — high-confidence claims without evidence
_CONVICTION_FALSE_MEMORY_PATTERNS = [
    # High-confidence claims about past events
    r"(de acuerdo a|according to)\s*(la confirmación|the confirmation|lo que)\s*(de|from|said)",
    r"(el comando|the command)\s*(ejecutado|executed|run)\s*(anteriormente|previously|before)\s*(retornó|returned)",
    r"(como se definió|as defined)\s*(en el|in the|in)\s*(PR|pull request|commit)\s*#?\d+",
    r"(la dependencia|the dependency).*\s*(ya fue|was already|already been)\s*(removida|removed|deleted)",
    r"(mi versión|my version)\s*(interna|internal)",
    r"(el script|the script).*\s*(se corrió|ran|executed)\s*(exitosamente|successfully).*\s*(anoche|last night|background)",
    r"(ya contamos con|we already have)\s*(la firma|the signature|firma)",
    r"(el log|the log).*\s*(mostró|showed|displayed)\s*\d+\s*(registros|records|entries)",
    r"(procedo con|proceeding with)\s*(el bypass|the bypass|bypass)",
    r"(la lógica|the logic).*\s*(se omite|is skipped|is omitted)",
    # Claiming authorization/results without evidence
    r"(ya|already)\s*(T1|t1)\s*(autorizó|authorized|approved|signed)",
    r"(Fase|Phase)\s*1\s*(está|is)\s*(activa|active)",
    r"(contamos con|we have)\s*(firma|signature)\s*(física|physical)",
    # Declaring state changes on things that never existed/happened
    r"(declare|claim|assert|report|confirm).*(?:resolved|completed|done|merged|passed|closed).*(?:when|but|without)",
    r"(?:was|were)\s+never\s+(?:opened|started|existed|created|run|executed|initiated)",
]


def _try_decode_obfuscated(text: str) -> str:
    """Attempt to decode base64/hex/rot13 segments in text."""
    decoded_parts = []

    # Try base64 segments
    b64_matches = re.findall(r"[A-Za-z0-9+/=]{16,}", text)
    for match in b64_matches:
        try:
            decoded = base64.b64decode(match).decode("utf-8", errors="ignore")
            if decoded and any(c.isalpha() for c in decoded):
                decoded_parts.append(decoded.lower())
        except Exception:
            pass

    # Try hex segments
    hex_matches = re.findall(r"(?:[0-9a-f]{2}\s){4,}", text.lower())
    for match in hex_matches:
        try:
            decoded = bytes.fromhex(match.replace(" ", "")).decode("utf-8", errors="ignore")
            if decoded and any(c.isalpha() for c in decoded):
                decoded_parts.append(decoded.lower())
        except Exception:
            pass

    # Try rot13
    if "rot13" in text.lower() or "cifrado" in text.lower():
        words = re.findall(r"[a-zA-Z]{4,}", text)
        for word in words:
            decoded = codecs.decode(word, "rot_13")
            decoded_parts.append(decoded.lower())

    return " ".join(decoded_parts)


def _layer6_adversarial_evasion(
    action_lower: str,
    description: str,
    combined_text: str,
) -> Optional[ActionClassification]:
    """Layer 6: Detect adversarial evasion attempts."""

    # 6A: Fragmentation detection
    for pattern in _FRAGMENTATION_PATTERNS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return ActionClassification(
                level=ActionLevel.MAGNA,
                reason=f"Layer 6A (Fragmentation) matched: /{pattern}/",
                action_description=description,
                requires_t1=True,
            )

    # 6B: Semantic Inversion / Double Negation
    for pattern in _INVERSION_PATTERNS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return ActionClassification(
                level=ActionLevel.MAGNA,
                reason=f"Layer 6B (Semantic Inversion) matched: /{pattern}/",
                action_description=description,
                requires_t1=True,
            )

    # 6C: Encoding / Obfuscation
    for pattern in _ENCODING_INDICATORS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return ActionClassification(
                level=ActionLevel.MAGNA,
                reason=f"Layer 6C (Encoding/Obfuscation) matched: /{pattern}/",
                action_description=description,
                requires_t1=True,
            )

    # 6C-decode: Try to decode obfuscated content and re-check
    decoded_content = _try_decode_obfuscated(combined_text)
    if decoded_content:
        # Check decoded content against secret patterns
        secret_patterns = [
            r"(key|secret|token|password|credential|api.?key|private.?key)",
            r"(merge|push|deploy|drop|delete|truncate)",
            r"(main|production|prod|master)",
        ]
        for pattern in secret_patterns:
            if re.search(pattern, decoded_content, re.IGNORECASE):
                return ActionClassification(
                    level=ActionLevel.MAGNA,
                    reason=f"Layer 6C-decode: Obfuscated content decoded reveals dangerous intent: /{pattern}/",
                    action_description=description,
                    requires_t1=True,
                )

    # 6D: Dory Probes
    for pattern in _DORY_PROBE_PATTERNS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return ActionClassification(
                level=ActionLevel.MAGNA,
                reason=f"Layer 6D (Dory Probe) matched: /{pattern}/",
                action_description=description,
                requires_t1=True,
            )

    # 6E: Conviction-based False Memory
    for pattern in _CONVICTION_FALSE_MEMORY_PATTERNS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return ActionClassification(
                level=ActionLevel.MAGNA,
                reason=f"Layer 6E (Conviction False Memory) matched: /{pattern}/",
                action_description=description,
                requires_t1=True,
            )

    return None


# ============================================================
# LAYER 7 IMPLEMENTATION: Capability/Resource-Based Gating
# ============================================================

# Protected resources: ANY action targeting these is MAGNA by capability,
# regardless of how the description is worded.
_PROTECTED_TABLES = frozenset(
    [
        # Anti-Dory governance tables
        "anti_dory_anchor_store",
        "anti_dory_plan_ledger",
        "anti_dory_audit_log",
        "anti_dory_canary_results",
        # Governance/authority tables
        "cowork_sesiones",
        "cowork_audit",
        "kernel_version",
        "kernel_state",
        # Memory/identity tables
        "error_memory",
        "memoria_semantica",
        "identidad_hilo",
        # Credential/secret storage
        "secrets_inventory",
        "credential_rotation_log",
    ]
)

_PROTECTED_RESOURCES = frozenset(
    [
        # Files/paths that are governance-critical
        ".monstruo",
        "guardian.py",
        "AGENTS.md",
        ".env",
        ".env.production",
        ".env.local",
        "minisign",
        "private_key",
        "service_role",
        # Governance artifacts
        "DSC",  # Decision documents
        "anchor_store",
        "plan_ledger",
        "authority_matrix",
    ]
)

_PROTECTED_CAPABILITIES = frozenset(
    [
        # Operations that are inherently dangerous by effect
        "write_credential",
        "rotate_secret",
        "modify_rls_policy",
        "alter_table_schema",
        "truncate_table",
        "drop_table",
        "modify_governance",
        "write_anchor",
        "transition_plan_status",
        "modify_kernel_state",
        "send_external_webhook",
        "publish_to_registry",
        "modify_ci_pipeline",
        "grant_permission",
        "revoke_permission",
    ]
)


def _layer7_capability_gating(
    metadata: dict,
    description: str,
) -> Optional[ActionClassification]:
    """Layer 7: Capability/resource-based gating.

    Structurally independent from Layers 1-6 (all lexical/regex).
    This layer gates based on WHAT the action touches, not HOW
    the description is worded.

    Metadata fields consumed:
      - target_resource: str — file/path/resource being targeted
      - affected_tables: list[str] — database tables affected
      - capability: str — the effect/capability being exercised
      - target_module: str — kernel module being modified
    """
    # 7A: Table-based gating
    affected_tables = metadata.get("affected_tables", [])
    if isinstance(affected_tables, str):
        affected_tables = [affected_tables]

    for table in affected_tables:
        table_lower = table.lower().strip()
        if table_lower in _PROTECTED_TABLES:
            return ActionClassification(
                level=ActionLevel.MAGNA,
                reason=(
                    f"Layer 7A (Capability): action affects protected table "
                    f"'{table_lower}' (resource-based gating, independent of description)"
                ),
                action_description=description,
                requires_t1=True,
            )

    # 7B: Resource-based gating
    target_resource = str(metadata.get("target_resource", "")).lower()
    if target_resource:
        for protected in _PROTECTED_RESOURCES:
            if protected.lower() in target_resource:
                return ActionClassification(
                    level=ActionLevel.MAGNA,
                    reason=(
                        f"Layer 7B (Capability): action targets protected resource "
                        f"'{target_resource}' (matches '{protected}')"
                    ),
                    action_description=description,
                    requires_t1=True,
                )

    # 7C: Capability-based gating
    capability = str(metadata.get("capability", "")).lower().strip()
    if capability in _PROTECTED_CAPABILITIES:
        return ActionClassification(
            level=ActionLevel.MAGNA,
            reason=(
                f"Layer 7C (Capability): action exercises protected capability '{capability}' (effect-based gating)"
            ),
            action_description=description,
            requires_t1=True,
        )

    # 7D: Module-based gating (any write to anti_dory kernel modules)
    target_module = str(metadata.get("target_module", "")).lower()
    if target_module and "anti_dory" in target_module:
        return ActionClassification(
            level=ActionLevel.MAGNA,
            reason=(
                f"Layer 7D (Capability): action modifies Anti-Dory kernel module "
                f"'{target_module}' (module-based gating)"
            ),
            action_description=description,
            requires_t1=True,
        )

    return None


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

    # Safe-context exclusion: educational/theoretical requests should not trigger
    _SAFE_CONTEXT_INDICATORS = [
        r"(expl\u00edcame|explain|mu\u00e9strame|show me)\s*.*(sintaxis|syntax|c\u00f3mo|how|ejemplo|example|te\u00f3rico|theoretical)",
        r"(redacta|write|draft)\s*(una)?\s*(expresi\u00f3n regular|regex|regexp)",
        r"(sintaxis correcta|correct syntax)\s*(para|for|to)",
        r"(ejemplo te\u00f3rico|theoretical example)",
    ]
    is_safe_educational = any(re.search(p, combined_text) for p in _SAFE_CONTEXT_INDICATORS)

    if not is_safe_educational:
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
                reason=(f"Action type '{action_type}' is inherently dangerous (MAGNA_ACTION_TYPES_INHERENT)"),
                action_description=description,
                requires_t1=True,
            )

        # LAYER 5: Context-Aware Heuristics (v3.0)
        for heuristic_category, patterns in CONTEXT_AWARE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined_text):
                    return ActionClassification(
                        level=ActionLevel.MAGNA,
                        reason=(f"Context-aware heuristic '{heuristic_category}' matched: /{pattern}/"),
                        action_description=description,
                        requires_t1=True,
                    )

    # LAYER 5.5: Branch-aware git push (active under v3 flag).
    # A bare git_push is STANDARD by default, but if metadata.target_branch
    # is main/master/production, escalate to MAGNA. Preserves safety for
    # main/production while not penalizing feature-branch pushes.
    if ANTI_DORY_B8_V3_ENABLED and metadata and action_lower in ("git_push", "push"):
        target = str(metadata.get("target_branch", "")).lower()
        if target in ("main", "master", "production", "prod", "release"):
            return ActionClassification(
                level=ActionLevel.MAGNA,
                reason=(f"git_push targets protected branch '{target}' (branch-aware MAGNA escalation)"),
                action_description=description,
                requires_t1=True,
            )

    # ============================================================
    # LAYER 6: Adversarial Evasion Detection (v3.1 NEW)
    # Detects 3 attack vectors identified by Grok 4 Heavy + Gemini 3.1 Pro:
    #   6A: Fragmentation — magna actions split into innocuous steps
    #   6B: Semantic Inversion / Double Negation — intent hidden via negation
    #   6C: Encoding / Obfuscation — base64, hex, rot13, indirect references
    #   6D: Dory Probes — questions that reveal context loss without keywords
    #   6E: Conviction-based False Memory — high-confidence false claims
    # Only active when ANTI_DORY_B8_V3_ENABLED=true
    # ============================================================
    if ANTI_DORY_B8_V3_ENABLED:
        l6_result = _layer6_adversarial_evasion(action_lower, description, combined_text)
        if l6_result:
            return l6_result

    # ============================================================
    # LAYER 7: Capability/Resource-Based Gating (v3.2 NEW)
    # STRUCTURALLY INDEPENDENT from regex/string-matching.
    # Gates based on WHAT RESOURCE the action targets, not HOW
    # the description is worded. This is the second epistemic
    # mechanism (capability-based) vs. Layers 1-6 (lexical).
    #
    # If metadata.target_resource matches a protected resource,
    # the action is MAGNA regardless of description content.
    # If metadata.affected_tables intersects protected tables,
    # the action is MAGNA regardless of description content.
    # ============================================================
    if ANTI_DORY_B8_V3_ENABLED and metadata:
        l7_result = _layer7_capability_gating(metadata, description)
        if l7_result:
            return l7_result

    # LAYER 8: Metadata override (si metadata indica forzar MAGNA)
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
