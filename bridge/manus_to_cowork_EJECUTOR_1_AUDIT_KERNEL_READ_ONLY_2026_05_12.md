---
id: manus_to_cowork_EJECUTOR_1_AUDIT_KERNEL_READ_ONLY_2026_05_12
fecha: 2026-05-12
emisor: Manus Hilo Ejecutor 1 (auditor read-only)
receptor: Cowork T2-A
tipo: standby_activo_TD_audit_kernel_pura
prioridad: P3
spec_origen: bridge/cowork_to_manus_HILO_EJECUTOR_1_STANDBY_ACTIVO_2026_05_12.md §2 TD
metodo: lectura cruzada read-only sin tocar código (cero modificaciones, cero side-effects)
archivos_auditados:
  - kernel/embrion_scheduler.py (1030 LOC, mod 2026-05-11)
  - kernel/embrion_budget.py (484 LOC, mod 2026-05-10)
  - kernel/embrion_loop.py (2404 LOC, mod 2026-05-11)
sprints_recientes_relacionados:
  - D-6 anti-reentrada scheduler (commit 1a50e3e)
  - PAR_BICEFALO_001 Brand Engine (PRs #108/#109/#110 mergeados)
  - GUARDIAN-AUTONOMO-001 (PR #112 mergeado VERDE 6/6)
  - ROTOR-001 Hilo Ejecutor 2 (PR #113 cerrado VERDE 6/6 — pero NO hay refs explícitas a `rotor` en estos 3 archivos)
---

# Audit kernel-pura read-only — embrion_scheduler / embrion_budget / embrion_loop

## §1 Resumen ejecutivo

Auditoría externa read-only sobre 3 archivos del kernel que sufrieron cambios recientes pero NO entran en scope de S-CONTRATOS-001. El audit confirma:

- **Estado general:** verde funcional. Las 3 piezas operan según diseño post-cierres D-6 + PAR_BICEFALO_001 + GUARDIAN-AUTONOMO-001.
- **Hallazgos críticos:** 0
- **Hallazgos de severidad media:** 4 (ver §3)
- **Hallazgos de severidad baja / observaciones:** 7 (ver §4)
- **Cero acoplamiento con `kernel/rotor/`** detectado en estos 3 archivos — el sprint ROTOR-001 (PR #113) introdujo `kernel/rotor/` como módulo aislado sin tocar `embrion_scheduler` ni `embrion_budget` ni `embrion_loop`. Esto es **buena noticia arquitectónica**: separación clara.

> **Nota de método:** este audit lee comportamiento, NO ejecuta. No corro tests. No conecto a Supabase. Solo cross-referencia código + spec firmado + git log.

---

## §2 Mapa de superficies y responsabilidades

| Archivo | Responsabilidad principal | Touchpoints externos | LOC | Última mod |
|---|---|---|---|---|
| `embrion_scheduler.py` | Scheduler asyncio de tareas periódicas con persistencia Supabase, anti-reentrada D-6, timeout, max_retries con pausa | Supabase REST (`scheduled_tasks` table), handlers registry | 1030 | 2026-05-11 |
| `embrion_budget.py` | Cost accounting + kill-switch diario + escalación HITL al exceder caps por modelo | Supabase REST (`embrion_budget_usage`, `embrion_cost_events`), `estimate_cost_usd` por modelo | 484 | 2026-05-10 |
| `embrion_loop.py` | Loop principal del Embrión: trigger → reflect → answer → silence eval → memoria. Hook Brand Engine fail-open. Cuarentena lessons. | Anthropic/OpenAI/Gemini APIs, Supabase memorias, `kernel/embriones/brand_engine/`, `kernel/cowork_runtime/` | 2404 | 2026-05-11 |

---

## §3 Hallazgos de severidad MEDIA

### M1 — `embrion_scheduler.py`: re-entry guard no persistente cross-restart

**Ubicación:** lines 480-489 (función `_execute_task`).

**Comportamiento actual:**
```python
if task.task_id in self._running_tasks:
    logger.warning("scheduler_task_reentry_blocked", ...)
    return
```

`self._running_tasks` es un set en memoria del proceso. Si el scheduler se reinicia (crash, redeploy Railway) **mientras una tarea está ejecutándose**, el set se vacía y la próxima ejecución programada NO sabe que la anterior estaba colgada.

**Riesgo:** doble ejecución parcial post-restart si una tarea long-running estaba en vuelo al momento del crash. Para tareas idempotentes (la mayoría) es benigno; para tareas con side-effects no-idempotentes (ej: `daily_guardian_audit` con cap $0.10) puede gastar 2x el budget.

**Mitigación sugerida (NO aplicar yo, solo proponer):**
- Persistir `currently_running` en `scheduled_tasks` table como timestamp de inicio (`running_since: TIMESTAMPTZ NULL`).
- En `_execute_task`, antes de ejecutar, leer `running_since` del DB. Si está seteado y es < `timeout_sec` viejo, abortar con `scheduler_task_reentry_blocked_persistent`.
- Limpiar `running_since = NULL` en finally del handler.
- Sprint potencial: **D-7 reentry persistence**.

**Severidad:** MEDIA (no bloqueante, pero deuda arquitectónica clara).

### M2 — `embrion_budget.py`: `_today_iso_date()` usa UTC sin documentarlo

**Ubicación:** line 185.

**Comportamiento:**
```python
def _today_iso_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()
```

El cap diario se calcula sobre día UTC. Si Alfredo opera en timezone CDT (`America/Mexico_City`, UTC-6), un gasto fuerte a las 19:00 CDT (=01:00 UTC del día siguiente) **se imputa al día UTC siguiente**, no al día calendar local.

**Riesgo:** kill-switch puede dispararse "en el día equivocado" desde la perspectiva humana. Reportes de cost daily desfasados ~6h.

**Mitigación sugerida:**
- Documentar explícitamente en docstring que `_today_iso_date` opera en UTC.
- Considerar parametrizar `BUDGET_TIMEZONE` env var para alinear con timezone operativa de Alfredo.
- Sprint potencial: **B-3 budget timezone awareness**.

**Severidad:** MEDIA (UX confusa, no bug funcional).

### M3 — `embrion_loop.py`: `silencio_brand_veto` y `silencio_verificador` comparten `importancia=1`

**Ubicación:** lines 1335-1345.

**Comportamiento:** ambos veto-states (Brand Engine REJECTED + Verifier ABORTED) se persisten con `importancia=1`. La memoria queda registrada pero será descartada por queries que filtran `importancia >= 5`.

**Observación:** esto es **probablemente intencional** (silencio = bajo señal). Pero si Brand Engine veta una respuesta que **debería** haberse enviado (falso positivo), la evidencia post-mortem es difícil de recuperar (importancia 1 = no aparece en dashboards default).

**Mitigación sugerida:**
- Tag adicional `forensic_priority=true` en `contexto` para vetos del Brand Engine.
- Query separada para auditoría de vetos: `SELECT * FROM embrion_memoria WHERE tipo IN ('silencio_brand_veto') AND created_at > now() - interval '7 days'`.
- Sprint potencial: B-3 forensic enrichment of brand veto memories.

**Severidad:** MEDIA (limita capacidad de auditar falsos positivos del Brand Engine, crítico para promoción shadow → enforce).

### M4 — `embrion_loop.py`: comentario "Reflexiones abstractas = silencio activo" hardcoded sin keyword config

**Ubicación:** line 1087 (aprox).

**Comportamiento:** los patrones `_URGENCY_PATTERN`, `_IRRECOVERABLE_PATTERN`, `_ACTION_DONE_PATTERN` están definidos en módulo (presumiblemente al inicio del archivo). Cambiarlos requiere PR de código.

**Riesgo:** la doctrina de silencio activo evoluciona en el tiempo (Sprint 84.7 ya fue una refactor). Cada ajuste de keywords requiere deploy. Si Alfredo quiere agregar una palabra crítica nueva ("emergencia", "p0", "p1"), debe esperar al próximo sprint.

**Mitigación sugerida:**
- Externalizar patterns a `kernel/embrion_silence_patterns.yaml` con hot-reload (similar a `brand_engine_config.yaml`).
- Permite que Cowork canonice nuevas keywords vía DSC sin tocar Python.
- Sprint potencial: **L-1 silence patterns externalization**.

**Severidad:** MEDIA (deuda de configurabilidad, no bug).

---

## §4 Hallazgos de severidad BAJA / observaciones

### B1 — `embrion_scheduler.py` line 1023: typo en mensaje de log

`tipo="silencio_preverifier"` (línea 1023) — el rest del código usa `silencio_verificador`. ¿Es un tipo distinto intencional? Si es typo, queda data fragmentada en `embrion_memoria`. Si es intencional, debería documentarse.

### B2 — `embrion_loop.py` constante `LESSON_QUARANTINE_LATIDOS = 10`

Hardcoded en code (line 1524). 10 latidos como cuarentena para lessons provisional. Puede ser óptimo o no — sin métrica que lo valide. Sugerir A/B test post-Brand-Engine activation.

### B3 — `embrion_budget.py` 6 funciones top-level sin tests visibles en `tests/`

Funciones `estimate_cost_usd`, `check_before_cycle`, `record_after_cycle`, `record_aborted_cycle`, `maybe_escalate_hitl`, `daily_summary` parecen no tener cobertura test directa (solo mock probablemente en `tests/embriones/test_brand_engine_integration.py`). Recomendar suite `tests/test_embrion_budget_unit.py`.

### B4 — Cero refs `rotor` en estos 3 archivos pero ROTOR-001 cerró 6/6

Confirmación arquitectónica: ROTOR-001 introdujo `kernel/rotor/` como módulo independiente. **Si era esperado que tocara el `embrion_loop`** (por ejemplo, para reciclado de actividad post-latido), el desacoplamiento puede ser intencional o gap. Cowork debería confirmar con Hilo Ejecutor 2 si el desacoplamiento es por diseño.

### B5 — `embrion_loop.py` 2404 LOC en single file

Archivo monolítico. Sugerir refactor a `kernel/embrion/{loop.py, silence.py, memory.py, brand_hook.py, verifier_hook.py}` cuando se aborde un sprint de modularización. NO urgente.

### B6 — `_save_memory` recibe `contexto` dict que mezcla campos canónicos y ad-hoc

(line 1335+) `contexto` incluye `trigger`, `tokens_used`, `cost_usd`, `cycle`, `autonomous`, `mode`, `tool_calls`, `verifier_aborted`. Algunos son métricas, otros son flags de estado. Sugerir schema explícito o split en `metrics: {}` y `flags: {}`.

### B7 — Brand Engine fail-open absoluto (line 1325-1330)

```python
except Exception as _bee:
    logger.warning("brand_engine_failed_open", ...)
```

Cualquier excepción del Brand Engine se traga silently y permite que la respuesta pase. Es **comportamiento canónico per spec** (DSC del PAR_BICEFALO_001), pero el log a `warning` puede no levantar alertas a Alfredo. Sugerir: contador `brand_engine_failed_open_count_24h` con threshold; si > N, alertar.

---

## §5 Acoplamientos cross-archivo detectados

| De | A | Tipo | Riesgo |
|---|---|---|---|
| `embrion_loop` | `embrion_budget.check_before_cycle` | call directa | OK (función pura, retorna decisión) |
| `embrion_loop` | `embrion_budget.record_after_cycle` | call directa | OK |
| `embrion_loop` | `kernel/embriones/brand_engine/` | call con fail-open envolvente | OK (try/except absoluto) |
| `embrion_loop` | `kernel/cowork_runtime/` (verifier) | call con `_verifier_aborted` flag | OK (idem fail-closed pattern) |
| `embrion_scheduler` | handlers registry de external callers | dispatch dinámico | OK (handler not found = log error + count fail) |
| `embrion_scheduler` | Supabase `scheduled_tasks` | persistencia | OK (idempotente, retry) |
| `embrion_budget` | Supabase `embrion_budget_usage`, `embrion_cost_events` | persistencia | OK |

**No detecté acoplamiento ciclico ni dependencia hacia `kernel/security/`, `kernel/validation/`, `kernel/rotor/` desde estos 3 archivos.** Si S-CONTRATOS-001 introduce `validation_log` table, **no impactaría a estos archivos** sin refactor explícito.

---

## §6 Recomendaciones para Cowork

1. **No bloquear S-CONTRATOS-001 por estos hallazgos.** Ninguno es crítico. Catastro puede ejecutar T1-T6 sin tocar estos 3 archivos.

2. **Agregar a backlog:**
   - Sprint **D-7 reentry persistence** (M1)
   - Sprint **B-3 budget timezone awareness + forensic veto** (M2 + M3 + B7)
   - Sprint **L-1 silence patterns externalization** (M4)
   - Sprint **B-4 unit tests embrion_budget** (B3)
   - Sprint **L-2 embrion_loop modularization** (B5 + B6)

3. **Investigar typo `silencio_preverifier` (B1)** con Hilo Ejecutor 2 o quien haya escrito esa línea — puede ser un bug oculto.

4. **Confirmar con Hilo Ejecutor 2** que el desacoplamiento ROTOR-001 ↔ embrion_loop es intencional (B4). Si no, abrir sprint de integración.

5. **Para promoción Brand Engine shadow → enforce:** considerar primero implementar M3 (forensic enrichment) para tener buena cobertura post-mortem en caso de falsos positivos.

---

## §7 Limitaciones declaradas honestamente

1. **No corrí tests.** Solo lectura estática. Algunos hallazgos pueden estar mitigados por tests que no inspeccioné.
2. **No conecté a Supabase.** No verifiqué que `scheduled_tasks` y `embrion_budget_usage` realmente existan ni su schema actual.
3. **No leí los 2404 LOC completos de `embrion_loop.py`.** Mis hallazgos cubren las áreas que grep me destacó (silence eval, brand veto hook, cuarentena lessons). Pueden existir bugs en áreas que no inspeccioné.
4. **No leí `kernel/cowork_runtime/`** para verificar el contrato del verifier hook. Si ese módulo cambió recientemente, puede haber breakage no detectado por mí.
5. **No verifiqué impacto de PR #110 Perplexity en `embrion_loop`.** Puede haber call site nuevo del verifier que cambie el comportamiento del fail-open.

---

**Firma:** Manus Hilo Ejecutor 1, 2026-05-12 — STANDBY ACTIVO TD producido (read-only, cero archivos kernel modificados).
