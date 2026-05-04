"""
Sprint 84.7 — Semillas 19va a 26va para error_memory.

Origen: refactor global de keyword matching tras audit del Sprint 84.5.
Cowork detectó 17 instancias del antipatrón `any(kw in text for kw in keywords)`
en 10 archivos críticos del kernel. Este sprint resuelve 8 archivos (1
semilla por archivo refactorizado) + 1 magna estructural (la 19va).

Las semillas se persisten vía POST /v1/error-memory/seed (admin-only).
Ver scripts/seed_sprint_84_5_via_endpoint.py para el cliente.

Convención:
- error_signature: prefijo `seed_` + descripción concisa snake_case
- confidence: 0.95 para todas (alta certeza, validadas por tests A/B/C)
- triggers: lista vacía o keywords que dispararían el match (no usado
  por el motor actual de error_memory pero documenta intent)
- fix_steps: pasos exactos del refactor aplicado, en orden
- prevention: cómo evitar reintroducir el bug (code review checklist)
"""
from __future__ import annotations

from typing import Any

# ── Semilla 19va ─ MAGNA estructural ────────────────────────────────────────────
SEED_19_MAGNA_STRUCTURAL: dict[str, Any] = {
    "error_signature": "seed_substring_keyword_matching_es_anti_pattern_estructural",
    "category": "code_quality",
    "severity": "high",
    "confidence": 0.95,
    "description": (
        "El patrón `any(kw in text for kw in keywords)` es un anti-pattern "
        "estructural que causa falsos positivos sistemáticos en el kernel. "
        "Detectado en Sprint 84.5 (8va semilla, classifier slow-path), "
        "expandido a Sprint 84.7 tras audit que encontró 17 instancias "
        "en 10 archivos. NO es un bug aislado: es un patrón de pensamiento "
        "incorrecto que se propaga cada vez que un dev escribe lógica de "
        "intent classification basada en keywords."
    ),
    "fix_steps": [
        "1. Crear utility centralizada kernel/utils/keyword_matcher.py",
        "2. compile_keyword_pattern() con \\b word boundaries + flag opcional treat_underscore_as_separator",
        "3. match_any_keyword() / count_keyword_matches() reemplazan patrón viejo",
        "4. is_negation_or_question() filtra contextos invertidos",
        "5. Migrar TODAS las instancias en un sprint dedicado (Sprint 84.7)",
        "6. Code review checklist: cualquier `kw in text` raw es BLOQUEANTE",
    ],
    "prevention": (
        "PRE-COMMIT HOOK + code review check: rechazar PRs con `kw in text` "
        "raw a menos que sea búsqueda de query libre del usuario "
        "(ej. marketplace search)."
    ),
}

# ── Semilla 20va ─ external_agents.py refactor ──────────────────────────────────
SEED_20_EXTERNAL_AGENTS: dict[str, Any] = {
    "error_signature": "seed_external_agents_keyword_substring_refactored",
    "category": "code_quality",
    "severity": "medium",
    "confidence": 0.95,
    "description": (
        "kernel/external_agents.py tenía 4 instancias del antipatrón "
        "(líneas 173, 182, 191, 199) en _detect_research_intent, "
        "_detect_manus_intent, _detect_analysis_intent, _detect_code_intent. "
        "Causaba routing incorrecto a agentes externos."
    ),
    "fix_steps": [
        "Reemplazar 4 instancias con _RESEARCH_PATTERN, _MANUS_PATTERN, "
        "_ANALYSIS_PATTERN, _CODE_PATTERN precompilados a nivel módulo",
    ],
    "prevention": "Patterns siempre a nivel módulo, nunca recompilar en hot path.",
}

# ── Semilla 21va ─ magna_classifier.py refactor ────────────────────────────────
SEED_21_MAGNA_CLASSIFIER: dict[str, Any] = {
    "error_signature": "seed_magna_classifier_keyword_substring_refactored",
    "category": "code_quality",
    "severity": "high",
    "confidence": 0.95,
    "description": (
        "kernel/magna_classifier.py tenía 5 instancias del antipatrón "
        "(líneas 400, 436, 450, 492, 495). Magna decide entre graph/router/"
        "tool_specific — falsos positivos aquí desviaban TODO el flujo."
    ),
    "fix_steps": [
        "Reemplazar 5 instancias con _TECH_PATTERN, _ACTION_PATTERN, "
        "_REFLECTION_PATTERN, _PRECIO_PATTERN, _TRENDING_PATTERN "
        "precompilados a nivel módulo",
    ],
    "prevention": "Severidad alta: cualquier cambio en magna_classifier requiere tests A/B/C.",
}

# ── Semilla 22va ─ supervisor.py refactor ──────────────────────────────────────
SEED_22_SUPERVISOR: dict[str, Any] = {
    "error_signature": "seed_supervisor_keyword_substring_refactored",
    "category": "code_quality",
    "severity": "medium",
    "confidence": 0.95,
    "description": (
        "kernel/supervisor.py tenía 3 instancias del antipatrón "
        "(líneas 169, 184, 187) en lógica de skip_enrich. "
        "Esto degradaba calidad de respuestas con memoria."
    ),
    "fix_steps": ["Refactor con patterns precompilados de la utility centralizada"],
    "prevention": "Tests deben cubrir personal_markers + casos negativos.",
}

# ── Semilla 23va ─ embrion_loop.py refactor ────────────────────────────────────
SEED_23_EMBRION_LOOP: dict[str, Any] = {
    "error_signature": "seed_embrion_loop_silence_score_keyword_substring_refactored",
    "category": "code_quality",
    "severity": "medium",
    "confidence": 0.95,
    "description": (
        "kernel/embrion_loop.py tenía 3 instancias del antipatrón "
        "(líneas 405, 410, 418) en _calculate_silence_score(). "
        "Falsos positivos hacían que el Embrión hablara cuando no debía."
    ),
    "fix_steps": [
        "Refactor con _NOISE_PATTERN, _CASUAL_PATTERN, _META_PATTERN",
    ],
    "prevention": "silence_score afecta cuántos mensajes envía el Embrión a Alfredo. Tests A/B/C obligatorios.",
}

# ── Semilla 24va ─ task_planner.py + nodes.py refactor ─────────────────────────
SEED_24_TASK_PLANNER_NODES: dict[str, Any] = {
    "error_signature": "seed_task_planner_nodes_keyword_substring_refactored",
    "category": "code_quality",
    "severity": "medium",
    "confidence": 0.95,
    "description": (
        "task_planner.py (línea 1686) y nodes.py (línea 1639 personal_markers) "
        "tenían cada uno 1 instancia del antipatrón. nodes.py tenía caso "
        "delicado: markers con espacio trailing (\"mi \", \"tu \") que se "
        "stripearon porque \\b ya garantiza el boundary."
    ),
    "fix_steps": [
        "task_planner: pattern precompilado con utility",
        "nodes: stripear espacios de personal_markers + utility centralizada",
    ],
    "prevention": (
        "Documentar en código que markers con espacio trailing son anti-pattern: "
        "\\b ya garantiza el word boundary, agregar \" \" causa miss en \"mi.\" o \"mi,\""
    ),
}

# ── Semilla 25va ─ motion/orchestrator.py refactor ─────────────────────────────
SEED_25_MOTION_ORCHESTRATOR: dict[str, Any] = {
    "error_signature": "seed_motion_orchestrator_keyword_substring_refactored",
    "category": "code_quality",
    "severity": "low",
    "confidence": 0.95,
    "description": (
        "kernel/motion/orchestrator.py tenía 2 instancias del antipatrón "
        "(líneas 153, 157) para componente classification. Caso especial: "
        "snake_case identifiers (`hero_button`, `product_card`) requieren "
        "treat_underscore_as_separator=True porque \\b estándar trata `_` "
        "como word-char."
    ),
    "fix_steps": [
        "Refactor con _BUTTON_LIKE_PATTERN, _CARD_LIKE_PATTERN",
        "Activar treat_underscore_as_separator=True en compile_keyword_pattern",
    ],
    "prevention": "Cualquier matching contra snake_case identifiers requiere el flag.",
}

# ── Semilla 26va ─ product_architect.py drop-in migration ──────────────────────
SEED_26_PRODUCT_ARCHITECT_MIGRATION: dict[str, Any] = {
    "error_signature": "seed_product_architect_drop_in_to_centralized_utility",
    "category": "code_quality",
    "severity": "low",
    "confidence": 0.95,
    "description": (
        "kernel/embriones/product_architect.py ya había recibido HOTFIX en "
        "Sprint 85 (Hilo Catastro) con _compile_vertical_pattern() local. "
        "Sprint 84.7 cierra el ciclo migrando a la utility centralizada "
        "kernel/utils/keyword_matcher.py compile_keyword_pattern() — "
        "drop-in equivalente."
    ),
    "fix_steps": [
        "Importar compile_keyword_pattern de kernel.utils.keyword_matcher",
        "Reemplazar _compile_vertical_pattern(...) → compile_keyword_pattern(...)",
        "Mantener _PATTERN_CACHE local (cache por vertical)",
    ],
    "prevention": (
        "Cualquier HOTFIX que duplique lógica de utility centralizada debe "
        "marcarse como deuda técnica para sprint de cleanup."
    ),
}


SEEDS_SPRINT_84_7 = [
    SEED_19_MAGNA_STRUCTURAL,
    SEED_20_EXTERNAL_AGENTS,
    SEED_21_MAGNA_CLASSIFIER,
    SEED_22_SUPERVISOR,
    SEED_23_EMBRION_LOOP,
    SEED_24_TASK_PLANNER_NODES,
    SEED_25_MOTION_ORCHESTRATOR,
    SEED_26_PRODUCT_ARCHITECT_MIGRATION,
]


def seed_sprint_84_7_into_error_memory(error_memory) -> dict[str, Any]:
    """Persiste las 8 semillas vía ErrorMemory.upsert_rule().

    Args:
        error_memory: instancia de ErrorMemory (con DB connected)

    Returns:
        dict con counts de inserted/updated/failed
    """
    inserted, updated, failed = 0, 0, 0
    errors = []
    for seed in SEEDS_SPRINT_84_7:
        try:
            result = error_memory.upsert_rule(**seed)
            if result.get("status") == "inserted":
                inserted += 1
            elif result.get("status") == "updated":
                updated += 1
        except Exception as e:
            failed += 1
            errors.append({"signature": seed["error_signature"], "error": str(e)})
    return {
        "inserted": inserted,
        "updated": updated,
        "failed": failed,
        "total": len(SEEDS_SPRINT_84_7),
        "errors": errors,
    }
