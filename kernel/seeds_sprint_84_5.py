"""
El Monstruo — Semillas error_memory Sprint 84.5
================================================

Dos semillas a persistir en `error_memory` cuando exista endpoint admin
de seeding o script de migración (gap documentado en bridge).

13va semilla: bug original (slow path no llama _local_classify) RESUELTO.
14va semilla: bug bonus descubierto (substring matching sin word boundaries) RESUELTO.

Para sembrar manualmente vía SQL (cuando se decida el momento):

    INSERT INTO error_memory (
        error_signature, sanitized_message, resolution,
        confidence, occurrences, module, status, created_at
    ) VALUES
    (
        'seed_classifier_slow_path_preflight_resolved',
        'Bug 8va semilla resuelto. Slow path (COMPLEX/DEEP) ahora llama '
            '_local_classify() como preflight antes del router LLM.',
        'Patrón: preflight de heurísticas baratas antes de LLM costoso. '
            'Aplica a cualquier classifier de tiers con costo asimétrico.',
        0.95, 1, 'kernel.nodes', 'resolved', NOW()
    ),
    (
        'seed_keyword_matching_sin_word_boundaries_es_bug',
        'execute_keywords se matcheaban con substring sin word boundaries — '
            'falsos positivos en negaciones (no voy a ejecutar) y preguntas '
            '(cómo se actualiza).',
        'Word boundaries obligatorios en keyword matching: usar regex '
            'compilado con \\b. Adicional: filtrar negaciones y preguntas '
            'explícitas que contienen el verbo.',
        0.90, 1, 'kernel.nodes', 'resolved', NOW()
    );

Sprint 84.5 — Hilo Manus Ejecutor — 2026-05-04.
"""

from __future__ import annotations

from typing import Any


# ── Definiciones literales de las 2 semillas ─────────────────────────

SEED_13_CLASSIFIER_SLOW_PATH_RESOLVED: dict[str, Any] = {
    "error_signature": "seed_classifier_slow_path_preflight_resolved",
    "sanitized_message": (
        "Bug 8va semilla resuelto. Slow path (COMPLEX/DEEP) ahora llama "
        "_local_classify() como preflight antes del router LLM."
    ),
    "resolution": (
        "Patrón: preflight de heurísticas baratas antes de LLM costoso. "
        "Aplica a cualquier classifier de tiers con costo asimétrico."
    ),
    "confidence": 0.95,
    "occurrences": 1,
    "module": "kernel.nodes",
    "status": "resolved",
}

SEED_14_KEYWORD_MATCHING_BUG: dict[str, Any] = {
    "error_signature": "seed_keyword_matching_sin_word_boundaries_es_bug",
    "sanitized_message": (
        "execute_keywords se matcheaban con substring sin word boundaries — "
        "falsos positivos en negaciones ('no voy a ejecutar') y preguntas "
        "('cómo se actualiza')."
    ),
    "resolution": (
        "Word boundaries obligatorios en keyword matching: usar regex "
        "compilado con \\b. Adicional: filtrar negaciones y preguntas "
        "explícitas que contienen el verbo."
    ),
    "confidence": 0.90,
    "occurrences": 1,
    "module": "kernel.nodes",
    "status": "resolved",
}


# 15va — Cowork specs deben verificar schema antes de escribir
SEED_15_COWORK_SPECS_VERIFY_SCHEMA: dict[str, Any] = {
    "error_signature": "seed_cowork_specs_must_verify_schema_before_writing",
    "sanitized_message": (
        "Cowork escribió spec del Sprint 84.5 con campo 'name' en error_memory "
        "cuando el schema real usa 'error_signature'. Hilo Ejecutor catchó la "
        "discrepancia."
    ),
    "resolution": (
        "Antes de escribir specs que toquen schemas existentes, Cowork debe "
        "verificar el schema real (leer migración SQL o tabla en Supabase via "
        "GitHub MCP). Cero asumir nombres de campo."
    ),
    "confidence": 0.85,
    "occurrences": 1,
    "module": "cowork.spec_writing",
    "status": "resolved",
}

# 16va — Discrepancia versiones diagnostic vs health
SEED_16_VERSION_MISMATCH_DIAGNOSTIC_VS_HEALTH: dict[str, Any] = {
    "error_signature": "seed_version_string_inconsistency_diagnostic_vs_health",
    "sanitized_message": (
        "/v1/embrion/diagnostic reporta version='0.84.0-sprint84' mientras "
        "/health reporta '0.84.7-sprint84.7'. Probable hardcoded version en "
        "embrion_loop o reporter de diagnostic sin sync con kernel.main."
    ),
    "resolution": (
        "Centralizar version string en kernel/__init__.py o config único. "
        "Ambos endpoints leen desde mismo source. Sprint 87 cleanup task."
    ),
    "confidence": 0.80,
    "occurrences": 1,
    "module": "kernel.embrion_loop",
    "status": "open",
}


SEEDS_SPRINT_84_5: list[dict[str, Any]] = [
    SEED_13_CLASSIFIER_SLOW_PATH_RESOLVED,
    SEED_14_KEYWORD_MATCHING_BUG,
    SEED_15_COWORK_SPECS_VERIFY_SCHEMA,
    SEED_16_VERSION_MISMATCH_DIAGNOSTIC_VS_HEALTH,
]


# ── Función de siembra (idempotente) ─────────────────────────────────

async def seed_sprint_84_5_into_error_memory(error_memory: Any) -> dict[str, Any]:
    """Siembra las 2 reglas en `error_memory` de forma idempotente.

    Requiere `ErrorMemory` inicializado y conectado a Supabase.
    Si la regla ya existe (mismo error_signature), no la duplica.

    Returns:
        Dict con `seeded`, `skipped`, `errors`.

    Ejemplo de uso (en una migración o endpoint admin):

        from kernel.seeds_sprint_84_5 import seed_sprint_84_5_into_error_memory
        result = await seed_sprint_84_5_into_error_memory(app.state.error_memory)
        # → {"seeded": 2, "skipped": 0, "errors": []}
    """
    if not error_memory or not getattr(error_memory, "initialized", False):
        return {
            "seeded": 0,
            "skipped": 0,
            "errors": ["error_memory_no_inicializado"],
        }

    db = getattr(error_memory, "_db", None)
    if not db:
        return {
            "seeded": 0,
            "skipped": 0,
            "errors": ["db_no_disponible"],
        }

    seeded = 0
    skipped = 0
    errors: list[str] = []

    for seed in SEEDS_SPRINT_84_5:
        try:
            existing = await db.select(
                error_memory.TABLE,
                columns="id",
                filters={"error_signature": seed["error_signature"]},
                limit=1,
            )
            if existing:
                skipped += 1
                continue

            await db.insert(error_memory.TABLE, seed)
            seeded += 1
        except Exception as exc:  # pragma: no cover — defensivo
            errors.append(
                f"{seed['error_signature']}: {type(exc).__name__}: {exc}"
            )

    return {"seeded": seeded, "skipped": skipped, "errors": errors}
