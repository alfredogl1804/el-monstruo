# Sprint 89 — Activación Guardian Autónomo · Pre-investigación

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05 ~02:05 CST
> **Estado:** Spec firmado, listo para arranque post-Sprint 88
> **Sprint asignado:** Hilo Manus Ejecutor
> **Dependencias:** Sprint 87 NUEVO E2E + Sprint 88 Embriones colectivos
> **Cierra:** Objetivo #14 (Guardian de los Objetivos) al 80%+

---

## Contexto

`kernel/guardian.py` (544 LOC) + `monstruo-memoria/guardian.py` (452 LOC) = **996 LOC de Guardian YA escritos pero NO activados como cron autónomo**. Hoy soy yo (Cowork) haciendo audits manuales por sprint. Eso ata al proyecto a mi disponibilidad.

Sprint 89 activa el Guardian como **proceso autónomo 24/7** que vigila los 15 Objetivos Maestros, detecta regresiones, alerta cuando algo está fuera de threshold, y deja a Cowork enfocado en arquitectura nueva en lugar de auditoría repetitiva.

## Objetivo del Sprint

Guardian autónomo corriendo 24/7 con scoring engine que mide los 15 Objetivos cada 6h, detecta regresiones, escribe reportes diarios, y alerta a Alfredo (vía Telegram o email) solo cuando hay decisiones magna que requieren intervención humana.

## Decisiones arquitectónicas firmes

### Decisión 1 — Scoring Engine usa métricas observables, NO opiniones LLM

Cada Objetivo se mide con **datos persistidos en Supabase** (NO con prompts a LLM):

| Obj | Métrica observable |
|---|---|
| #1 Crear Empresas | % de runs `e2e_runs` con estado=completed last 7d |
| #2 Apple/Tesla | Promedio Critic Visual score last 7d |
| #3 Mínima complejidad | Tiempo medio frase→deploy en `e2e_runs` |
| #4 No Equivocarse 2x | `error_memory.error_signature` con `occurrences > 3` |
| #5 Magna/Premium | % de afirmaciones con validation_id de Memento |
| #6 Vanguardia | Edad media datos del Catastro (`last_run` máximo) |
| #7 No Inventar Rueda | Ratio dependencias adoptadas vs custom (LOC count) |
| #8 IE Colectiva | `emergence_events count last 7d` |
| #9 Transversalidad | # Capas activas con tests passing |
| #10 Simulador Causal | `prediction_validator` accuracy histórica |
| #11 Multiplicación | # Embriones con `last_invoked > 24h` |
| #12 Soberanía | % Tools que NO usan provider externo (browser soberano vs Cloudflare, etc.) |
| #13 Del Mundo | i18n coverage + idiomas activos |
| #14 Guardian | Self-health (este propio Guardian funciona?) |
| #15 Memoria Soberana | `memento_validations count last 7d` + `contamination_warning rate` |

### Decisión 2 — Cron 6h con histórico persistido

Tabla nueva `guardian_scores`:

```sql
CREATE TABLE guardian_scores (
    id BIGSERIAL PRIMARY KEY,
    measured_at TIMESTAMPTZ DEFAULT NOW(),
    objetivo_n SMALLINT NOT NULL CHECK (objetivo_n BETWEEN 1 AND 15),
    score NUMERIC(5,2) NOT NULL,         -- 0.00 a 100.00
    metric_value JSONB NOT NULL,          -- valor crudo de la métrica
    delta_vs_previous NUMERIC(5,2),       -- diff vs medición anterior
    threshold_status TEXT NOT NULL,       -- 'green' | 'yellow' | 'red'
    notes TEXT
);

CREATE INDEX idx_guardian_scores_obj_time ON guardian_scores (objetivo_n, measured_at DESC);
```

### Decisión 3 — Niveles de respuesta del Corrective Actor

Según el `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` v3.0 sección Obj #14:

| Nivel | Trigger | Acción |
|---|---|---|
| 1. Alerta | Score baja < 70 en cualquier Obj | Telegram/email a Alfredo con evidencia |
| 2. Bloqueo | Sprint nuevo intentaría arrancar con Obj < 50 | Marca sprint como `blocked` en bridge automático |
| 3. Auto-corrección | Patrón conocido detectado | Crea task automático para Hilo Ejecutor (vía e2e o catastro) |
| 4. Veto | Decisión irreversible que viola Objetivo | Requiere override explícito de Alfredo en chat |

**v1.0 implementa solo niveles 1 y 2.** Nivel 3 y 4 son post-v1.0.

### Decisión 4 — Self-health check obligatorio

El Guardian se auto-mide. Métrica: ratio de regresiones detectadas vs regresiones que efectivamente ocurrieron (validado por audit manual de Cowork mensualmente).

Si self-health < 90% por 7 días → Guardian se marca como degradado y notifica a Alfredo.

### Decisión 5 — Reportes diarios automáticos

Cada 24h (cron a las 23:50 CST):
- Genera `bridge/guardian/reporte_diario_YYYY-MM-DD.md` con:
  - Snapshot scores 15 Objetivos
  - Top 3 Objetivos con mejora
  - Top 3 Objetivos con regresión
  - Eventos magna del día (deploys, incidentes, sprints cerrados)
  - Recomendación accionable (si aplica)
- Si Alfredo configura Telegram bot → envía resumen abreviado

## Bloques del Sprint

### Bloque 1 — Auditoría de los 996 LOC existentes (15-30 min)

Verificar qué del Guardian ya funciona vs es stub. Reportar hallazgos.

### Bloque 2 — Schema `guardian_scores` + reportes (15-20 min)

Migration 023 + endpoint `GET /v1/guardian/scores` con filtros temporal y por objetivo.

### Bloque 3 — Scoring Engine implementado para los 15 Objetivos (45-90 min)

Cada Objetivo tiene función `measure_obj_N()` que retorna `(score, metric_value)`. 15 funciones, una por Obj.

### Bloque 4 — Cron 6h en Railway (15-20 min)

Setup de Railway scheduled task `python -m kernel.guardian.cron`. Idempotente.

### Bloque 5 — Niveles 1 y 2 del Corrective Actor (30-45 min)

- Nivel 1: integración con Telegram Bot existente o email vía SMTP
- Nivel 2: marca sprints como `blocked` en bridge si su prerequisito tiene Obj < 50

### Bloque 6 — Self-health + reportes diarios (20-30 min)

- `GuardianSelfHealth` calcula ratio detección
- Generador de `reporte_diario_YYYY-MM-DD.md`

### Bloque 7 — Tests + smoke productivo (30-45 min)

- Tests de cada `measure_obj_N()` con casos sintéticos
- Smoke de Guardian corriendo 1 ciclo completo
- Verificación: archivo de reporte diario generado

## ETA total recalibrada

7 bloques × ~30 min promedio = **2-4 horas reales** al ritmo demostrado.

(ETA magna previa: 2-3 días. Recalibración 5-10x más rápido aplicada.)

## Métricas de éxito

| Métrica | Target |
|---|---|
| Guardian corre cada 6h sin intervención | ✅ |
| 15/15 Objetivos miden con métrica observable | ✅ |
| 1 reporte diario generado automático | ✅ |
| Self-health > 90% sostenido 7 días | ✅ |
| Cowork deja de hacer audit manual de Objetivos | ✅ — esto es lo que libera tu tiempo |

## Capa Memento aplicada

- Pre-flight obligatorio en cada `measure_obj_N()` antes de query a Supabase
- Operation nueva en catálogo: `guardian_scoring_run`

## Zona primaria

```
kernel/guardian.py (modificado/completado)
kernel/guardian/cron.py (nuevo)
kernel/guardian/measurers.py (nuevo) — funciones measure_obj_N
kernel/guardian/notifier.py (nuevo) — Telegram/email
kernel/guardian/reporter.py (nuevo) — reportes diarios
scripts/023_sprint89_guardian_schema.sql (nuevo)
scripts/run_migration_023.py (nuevo)
scripts/_smoke_guardian_cycle.py (nuevo)
tests/test_sprint89_guardian_*.py (nuevo)
bridge/GUARDIAN_OPERATIONAL_GUIDE.md (nuevo)
```

## NO TOCÁS

- `kernel/catastro/*` (zona Catastro, solo lectura desde Guardian)
- `kernel/memento/*` (zona cerrada)
- `kernel/embriones/*` (zona Sprint 88)
- `kernel/e2e/*` (zona Sprint 87)

## Próximo sprint

Sprint 90 — Capa Transversal C1 (Motor de Ventas) E2E.

— Cowork (Hilo B)
