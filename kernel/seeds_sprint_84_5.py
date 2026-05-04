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


SEEDS_SPRINT_84_5: list[dict[str, Any]] = [
    SEED_13_CLASSIFIER_SLOW_PATH_RESOLVED,
    SEED_14_KEYWORD_MATCHING_BUG,
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
