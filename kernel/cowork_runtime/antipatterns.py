"""
kernel/cowork_runtime/antipatterns.py — Sprint COWORK-AUTO-DISCIPLINE-REAL-001 T5

Catálogo unificado de antipatterns Cowork F1-F27.

F1-F22: re-exportados desde kernel/cowork_runtime/rule_reinjection.HARD_RULES_CANONICAS
        (fuente histórica canónica, NO modificada por este sprint).
F23-F27: nuevos antipatterns derivados de instancias F21 reincidentes y otros
         fallos sistémicos observados HOY (2026-05-12). Canonizados verbatim
         del spec firmado commit d53b80ff §3.

Doctrina:
- Los antipatterns se nombran Fxx (failure pattern) con N estable y referenciable
  en bridge/, DSCs y embrion_memoria.
- Cada antipattern declara: id, name, description, severity, related_dsc,
  detection_hint (cómo el hook lo puede atrapar runtime), countermeasure.
- F1-F22 viven en rule_reinjection como reglas duras inline. F23-F27 viven aquí
  como entries estructuradas. Futuras Fxx también van aquí.
- Si quieres modificar F1-F22, primero migrá su entry aquí + deprecá inline.
  (DSC firmado obligatorio para el cambio.)

Spec firmado: bridge/sprints_propuestos/sprint_COWORK_AUTO_DISCIPLINE_REAL_001.md commit d53b80ff
DSCs referenciados: DSC-S-016, DSC-G-008 v3, DSC-MO-006 v1.1, DSC-S-012.
"""

from __future__ import annotations

from typing import Any

# ============================================================================
# F23-F27 nuevos antipatterns canonizados HOY (Sprint COWORK-AUTO-DISCIPLINE-REAL-001)
# ============================================================================

NEW_ANTIPATTERNS: list[dict[str, Any]] = [
    {
        "id": "F23",
        "name": "Auto-discipline shadow ignorada en sprints subsecuentes",
        "description": (
            "Después de canonizar el hook auto-discipline, Cowork ignora los "
            "contadores `auto_discipline_shadow_count` y `last_invocation_record` "
            "en sesiones posteriores, repitiendo los mismos F21 que el hook ya "
            "detectó en shadow. Equivalente runtime al F22 (memoria efímera) pero "
            "específicamente sobre las violations ya señaladas por el hook."
        ),
        "severity": "P1",
        "related_dsc": ["DSC-S-016", "DSC-MO-006 v1.1"],
        "detection_hint": (
            "Si `session_health()['auto_discipline_shadow_count'] > 0` y Cowork "
            "envía un nuevo output sin reescribir el anterior, el hook debe "
            "promover el siguiente bloqueo a P0 (no shadow)."
        ),
        "countermeasure": (
            "Al inicio de cada turn, leer `last_invocation_record` y exigir que "
            "los violations detectados en el turn previo aparezcan resueltos (tool "
            "calls correspondientes) antes de aceptar el nuevo output."
        ),
    },
    {
        "id": "F24",
        "name": "Spec firmado con datos no verificados pre-firma",
        "description": (
            "Cowork firma un spec que asume estado existente (migration N libre, "
            "archivo X existe, función Y disponible) sin verificación binaria "
            "previa. Caso real HOY: spec d53b80ff afirmó migration 0031 libre + "
            "antipatterns.py existing + 4 módulos kernel inexistentes "
            "(semantic_detector, advance_score, preflight, telegram_veto)."
        ),
        "severity": "P0",
        "related_dsc": ["DSC-S-016", "DSC-S-012", "DSC-G-008 v3"],
        "detection_hint": (
            "Si un spec firmado contiene migration filename con número específico "
            "(`NNNN_*.sql`) o módulo path (`kernel/.../*.py`), el linter pre-firma "
            "debe ejecutar `ls migrations/sql/ | tail -1` + `test -f <path>` y "
            "rechazar firma si los datos asumidos no matchean realidad."
        ),
        "countermeasure": (
            "Pre-firma checklist obligatorio: (1) migration number = last_existing + 1, "
            "(2) todos los paths citados existen en HEAD, (3) versiones citadas "
            "matchean tags/branches actuales. Bloquear commit del spec si check falla."
        ),
    },
    {
        "id": "F25",
        "name": "Self-merge sin reviewer Manus",
        "description": (
            "Cowork mergea un PR que él mismo creó sin esperar audit Manus, "
            "violando DSC-G-008 v3 §4 (deducción de consecuencias). El sprint "
            "termina técnicamente verde pero queda sin par revisor neutral."
        ),
        "severity": "P0",
        "related_dsc": ["DSC-G-008 v3", "DSC-MO-011"],
        "detection_hint": (
            "gh pr view --json author + reviews → si author == merger == cowork, "
            "y `reviews` no contiene aprobación de hilo Manus, bloquear merge."
        ),
        "countermeasure": (
            "Branch protection main: require ≥1 review approval de actor "
            "manus_hilo_a o manus_hilo_b para todo PR cuyo author sea cowork-*. "
            "Si Manus no está disponible, el PR queda en `draft` hasta sesión humana."
        ),
    },
    {
        "id": "F26",
        "name": "Doctrina markdown sin enforcement de código equivalente",
        "description": (
            "Cowork canoniza un DSC o regla operativa solo como markdown en "
            "discovery_forense/CAPILLA_DECISIONES/_GLOBAL/ sin contraparte ejecutable "
            "(script, linter, CI workflow). La regla se cumple ~3 sesiones y luego "
            "se olvida. Patrón anti-'habla con código, no con texto'."
        ),
        "severity": "P1",
        "related_dsc": ["DSC-G-017 (DSC-as-Contract)", "DSC-MO-008"],
        "detection_hint": (
            "Para todo DSC nuevo firmado, grep en `scripts/`, `tools/`, `.github/workflows/`, "
            "`kernel/` un script/test/workflow que referencie el DSC id. Si ausente, "
            "abrir issue auto con label `dsc-orphan`."
        ),
        "countermeasure": (
            "Política: ningún DSC se considera 'activo' sin al menos una referencia "
            "ejecutable (script linter, test, workflow CI, módulo kernel). DSCs "
            "huérfanos quedan en estado `informational` no `enforced`."
        ),
    },
    {
        "id": "F27",
        "name": "Reporte verde sin reproducir audit binario",
        "description": (
            "Cowork declara sprint verde (`🏛️ NOMBRE — DECLARADO`) basándose en "
            "lectura del reporte Manus en lugar de reproducir el audit binario "
            "él mismo (ej. ejecutar `pytest tests/test_xxx.py`, `gh pr view`, "
            "`execute_sql SELECT ...`). DSC-G-008 v2 §5 exige Cowork AUDITA "
            "contenido, no solo lee reporte."
        ),
        "severity": "P0",
        "related_dsc": ["DSC-G-008 v2", "DSC-G-008 v3"],
        "detection_hint": (
            "Antes de la frase canónica `DECLARADO`, el hook exige que en la history "
            "del turn aparezcan ≥2 tool_calls de re-verificación (no solo lectura "
            "de reporte JSON/MD). Sin ellos, la frase canónica se reemplaza por "
            "`AUDIT_PENDIENTE`."
        ),
        "countermeasure": (
            "Token `DECLARADO` solo se emite si `last_invocation_record.queries_done` "
            "contiene ≥2 entries de verificación independiente (execute_sql, "
            "gh pr view --json, pytest, etc.) en el turn de cierre."
        ),
    },
]


def get_antipattern_by_id(antipattern_id: str) -> dict[str, Any] | None:
    """Lookup por id estable (F23-F27)."""
    for ap in NEW_ANTIPATTERNS:
        if ap["id"] == antipattern_id.upper():
            return ap
    return None


def all_new_ids() -> list[str]:
    """Lista de ids estables F23-F27."""
    return [ap["id"] for ap in NEW_ANTIPATTERNS]


# ============================================================================
# Re-export F1-F22 desde rule_reinjection (fuente histórica canónica)
# ============================================================================


def get_canonical_hard_rules() -> str:
    """
    Devuelve el bloque verbatim de HARD_RULES_CANONICAS desde rule_reinjection
    como string serializado (tuple de (id, descripción) joined por newline).
    NO modificar el contenido fuente — esta función solo lee y serializa.
    """
    try:
        from kernel.cowork_runtime.rule_reinjection import HARD_RULES_CANONICAS
    except ImportError:
        return ""
    # HARD_RULES_CANONICAS es tupla de tuplas (id, descripción)
    if isinstance(HARD_RULES_CANONICAS, str):
        return HARD_RULES_CANONICAS
    lines: list[str] = []
    for entry in HARD_RULES_CANONICAS:
        if isinstance(entry, (tuple, list)) and len(entry) >= 2:
            lines.append(f"{entry[0]}: {entry[1]}")
        else:
            lines.append(str(entry))
    return "\n".join(lines)


# ============================================================================
# CATÁLOGO UNIFICADO (para tests + diagnósticos)
# ============================================================================

ANTIPATTERNS_VERSION: str = "1.0.0"  # bump cuando se agregue F28+

# F1-F22 listados como referencias doctrinales (no contienen el texto inline —
# para eso ir a HARD_RULES_CANONICAS en rule_reinjection.py).
HISTORICAL_ANTIPATTERN_IDS: tuple[str, ...] = tuple(f"F{i}" for i in range(1, 23))

ALL_ANTIPATTERN_IDS: tuple[str, ...] = HISTORICAL_ANTIPATTERN_IDS + tuple(all_new_ids())
