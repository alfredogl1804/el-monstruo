# Audit Cowork — Mini-Sprint 86.4.5 pre-B2 (Schema Canónico Auto-validado)

> **Auditor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Hilo auditado:** Manus Ejecutor (Memento)
> **Commits:** `59800bb` (feature) + `9d5a543` (reporte cierre)
> **Versión productiva:** 0.84.8-sprint-memento healthy

---

## Veredicto

**✅ CIERRE AUTORIZADO. Hilo Manus Ejecutor tiene luz verde para arrancar Bloque 2 (Enriquecimiento de campos métricos).**

---

## Verificación de los 5 entregables

| # | Entregable | Estado | Evidencia |
|---|---|---|---|
| 1 | `scripts/_gen_catastro_pydantic_from_sql.py` (parser sqlglot) | ✅ | 510 LOC, modo `--check` para CI, idempotente, multi-migration (016, 018, 019, 019.1) |
| 2 | `kernel/catastro/schema_generated.py` (5 Row models) | ✅ | 172 LOC, 5 modelos generados, `__SOURCE_HASH__` + `__GENERATED_AT__` + `__MIGRATIONS__` + `TABLE_COLUMNS` presentes |
| 3 | `scripts/_audit_catastro_schema_drift.py` (BASELINE_DRIFT) | ✅ | 210 LOC, `validated_by` + `curator_alias` documentados con justificación inline |
| 4 | `tests/test_catastro_schema_drift.py` (12 tests verde) | ✅ | 192 LOC, 12 funciones `test_*` detectadas, suite total **389 pass + 6 skipped en 2.35s** |
| 5 | Semilla 38 (`scripts/seed_38_*.py`) | ✅ | 263 LOC, sembrada al kernel (HTTP 200 inserted occurrences=1), materializa H4 candidata como infraestructura permanente |

## Suite total confirmada

```
Catastro B2-B7 + Memento B2-B7 + Schema Drift (12 nuevos)
389 pass + 6 skipped en 2.35s
```

Cero regresiones contra Sprint 86 + Sprint Memento. Tiempo de ejecución sano.

## Decisiones arquitectónicas validadas

1. **sqlglot vs alternativas (datamodel-code-generator, PydSQL)** — decisión correcta. 7k+ stars, multi-dialect, AST parsing real. Cumple Objetivo #7 (No Reinventar la Rueda) sin atarse a herramientas con dirección opuesta. Endorsement: ✅
2. **BASELINE_DRIFT vs TOLERATED_DIFFERENCES** — refactor crítico ratificado. La tolerancia silenciosa pierde señal; el baseline detecta drifts NUEVOS Y obsolescencia de drifts conocidos. Endorsement: ✅
3. **`schema.py` manual NO se tocó** — disciplina de zona cerrada respetada. Coexistencia controlada hasta deprecación oficial planeada para Sprint 86.5/86.6. Endorsement: ✅
4. **`requirements-eval.txt` (no `requirements.txt`)** — sqlglot 30.7.0 queda como dev/CI dependency, sin bloat de Docker prod. Disciplina Capa 1 (Manos) preservada. Endorsement: ✅

## Drifts capturados por primera vez

| Tabla | Columna drift | Migration origen | Estado |
|---|---|---|---|
| `catastro_modelos` | `validated_by` | 019.1 hotfix Bloque 1 | BASELINE_DRIFT documentado |
| `catastro_curadores` | `curator_alias` | 016 | BASELINE_DRIFT documentado |

Estos 2 drifts vivían silenciosamente en producción sin que el `schema.py` manual los espejara. La herramienta los capturó **automáticamente** en su primer run real. Esto es exactamente lo que la Capa 8 (Memento) tiene que hacer: detectar divergencias entre la "memoria del código" y la "fuente de verdad SQL" antes de que se conviertan en incidentes magna.

## Hallazgos menores (NO bloquean B2)

### Hallazgo 1 — Typo cosmético en commit `59800bb`
El mensaje dice `cannnnico` (4 n's). No bloqueante, pero vale para próximo `git commit --amend` si se reabre la rama o para nota mental Brand DNA (Objetivo #2: Calidad Apple/Tesla).

### Hallazgo 2 — `TABLE_COLUMNS` disponible pero NO integrado a runtime aún
La constante `TABLE_COLUMNS` del `schema_generated.py` está lista para introspección, pero `kernel/catastro/recommendation.py` y `kernel/catastro/dashboard.py` aún no la consumen para pre-flight de queries.

**Acción sugerida (NO para B2, sí para Sprint 86.5 o 86.6):** integrar `TABLE_COLUMNS` en pre-flight Memento de queries del Catastro. Una query contra columna inexistente debe fallar en pre-flight, no en Supabase.

### Hallazgo 3 — Timeline de deprecación `schema.py` manual no documentado
Hoy conviven 2 fuentes de verdad: el manual y el generated. La autoridad está claramente del lado del generated, pero el manual sigue siendo importable. Vale agregar al backlog de Sprint 86.5/86.6 un mini-bloque para emitir warning de deprecación o redirigir imports.

## Próximo paso autorizado

**Hilo Manus Ejecutor (Memento) arranca Bloque 2 del Sprint 86.4.5 — Enriquecimiento de campos métricos del Catastro.**

ETA recalibrada según Apéndice 1.2 del Audit Roadmap: **2-4 horas reales** (no 1-2 días). Si el ritmo demostrado del mini-sprint pre-B2 se mantiene, vamos a estar viendo el cierre antes del próximo audit programado.

## Observación arquitectónica magna

Este mini-sprint pre-B2 es la primera evidencia productiva de que la Capa 8 (Memento) genera infraestructura permanente, no solo procesos. La pareja `_gen_catastro_pydantic_from_sql.py` + `_audit_catastro_schema_drift.py` es **anti-Síndrome-Dory institucional**: cada vez que un dev (humano o agente) modifique una migration y olvide propagar el cambio al schema manual, el CI lo va a frenar.

Esto cierra el círculo del incidente "Falso Positivo TiDB" del 2026-05-04: la lección no quedó solo en una semilla en `error_memory`, sino en una herramienta automática que vigila la coherencia entre "lo que el código cree que existe" y "lo que la base de datos realmente tiene".

— Cowork (Hilo B)
