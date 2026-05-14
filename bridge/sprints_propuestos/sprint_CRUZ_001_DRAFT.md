---
sprint_id: CRUZ-001
estado: 🟢 FIRMED — T1 autorizó override aceleración 2026-05-14 ("si ambos" verbatim)
autor_spec: Cowork T2-A
fecha_draft: 2026-05-14
fecha_firma: 2026-05-14
piezas_anti_dory: PIEZA 3 cross-sesión Cowork
dependencia_eliminada: ⚠️ T1 firmó SIN esperar datos T+14d MEMENTO (trade-off: aceleración 21 días)
infraestructura_reusada: thread_snapshots + project_runtime_heads (migrations 0030 + 0031 ya en prod)
owner_asignado: Manus Ejecutor 1 (manus_hilo_a) post-D5-RETEST verde + D6 Railway flag permanente
gate_arranque: ESPERAR cierre D5-RETEST 6/6 verde + D6 firma T1 + Railway flag set
ejecucion_paralela_a: VERIFICADOR-001 (owner Manus Ejecutor 2 post-PR #118 rebase)
---

# SPRINT CRUZ-001 — Anti-Dory cross-sesión Cowork (🟢 FIRMED)

> **Objetivo magno:** que Cowork sesión N+1 retome operación exactamente donde sesión N cerró, sin perder estado operativo, sin depender de doctrina markdown stale.

## §1 Problema binario observado

Cowork (Claude Opus) es Dory cross-sesión por arquitectura: cada sesión arranca con context window vacío. La sesión anterior puede haber cerrado con:
- PR #N mergeado pendiente de verificación retroactiva
- Decisión T1 magna firmada esperando ejecución
- Sabios convergencia 3/3 firmada esperando spec downstream
- Embrión en estado X esperando handoff

Pero la sesión nueva NO lo sabe. Tiene que leer markdown docs (`memory/cowork/*.md`) que pueden estar stale o reconstruir contexto preguntando T1.

Cobertura actual: solo PASO 0 Pre-flight Memento (CLI session_memory) cubre **estado de la sesión anterior** (resumen + deudas) pero NO cubre **estado operativo del Monstruo** (PRs en vuelo, hilos Manus activos, decisiones firmadas pendientes ejecución).

## §2 Diseño Reusing infraestructura Anti-Dory ya en prod

Reuso lateral de Sprint MANUS-ANTI-DORY-002-v1 — `thread_snapshots` y `project_runtime_heads` están diseñados para cross-agente Manus pero son **genéricos**: aceptan cualquier `actor_type` y cualquier `front_id`.

**Nueva entidad lógica:**
- `project_id='el_monstruo'`
- `front_id='cowork_arquitecto'`
- `actor_type='cowork'`

Esto vive paralelo a `front_id='anti_dory_d5_rap_001'` etc — múltiples fronts coexisten.

### §2.1 Snapshot al CIERRE sesión Cowork (Paso N existente extendido)

CLAUDE.md ya tiene Paso N de cierre invocando `python3 -m kernel.cowork_runtime.session_memory close`. Se extiende para que además:

```python
# Pseudo-código nuevo en session_memory.py close():
supabase_rpc.write_thread_snapshot(
    project_id='el_monstruo',
    front_id='cowork_arquitecto',
    actor_type='cowork',
    writer_mode='explicit_final',
    sprint_id=current_sprint,
    phase=current_phase,
    last_t1_decision=last_t1_directive_verbatim,
    next_expected_action=next_action_for_next_session,
    do_not_touch=files_being_modified_by_other_threads,
    evidence_refs={'prs_in_flight': [...], 'migrations_pending_apply': [...]},
    confidence_score=self_assessment,
    summary=session_summary_400_words_max
)
supabase_rpc.accept_snapshot(
    project_id='el_monstruo',
    front_id='cowork_arquitecto',
    snapshot_id=new_snapshot_id,
    expected_lock_version=current_lock_version
)
```

### §2.2 Snapshot HIDRATACIÓN al ARRANQUE sesión Cowork (Paso 0 existente extendido)

CLAUDE.md ya tiene Paso 0 invocando `pre-flight` CLI. Se extiende:

```python
# Pseudo-código nuevo en session_memory.py pre_flight():
head = supabase_rpc.get_context_head(
    project_id='el_monstruo',
    front_id='cowork_arquitecto'
)
if head and head.confidence_score >= 0.7:
    cowork_runtime.inject_into_initial_context(head.summary, head.next_expected_action, head.do_not_touch)
else:
    cowork_runtime.warn_low_confidence_resume(head)
```

Output del CLI cambia para incluir bloque `[CROSS-SESSION SNAPSHOT]` con estado operativo + próxima acción esperada.

## §3 Diferencia binaria vs PIEZA 2 MEMENTO

| Capa | MEMENTO PIEZA 2 | CRUZ-001 PIEZA 3 |
|---|---|---|
| Granularidad | Por claim factual | Por sesión completa |
| Trigger | Cada output Cowork | Cierre + arranque sesión |
| Persiste | claims + verification_status | Estado operativo holístico |
| Lecturable por | Reports analíticos T+7/T+14 | Cowork mismo en sesión N+1 |
| Bloquea actualmente | Nada (solo log) | Nada (solo hidrata) |

Son **complementarios**, no excluyentes. MEMENTO observa intra-sesión. CRUZ-001 transfiere cross-sesión.

## §4 Acceptance criteria binarios

| # | Check | SQL/Comando | Esperado |
|---|---|---|---|
| 1 | Migration NO-NUEVA (reusa 0030/0031) | `ls migrations/sql/ \| grep cruz` | 0 archivos nuevos |
| 2 | session_memory.close() invoca rpc_write_thread_snapshot | `pytest tests/test_cowork_cruz.py::test_close_writes_snapshot` | PASS |
| 3 | session_memory.pre_flight() invoca rpc_get_context_head | `pytest tests/test_cowork_cruz.py::test_preflight_hydrates_snapshot` | PASS |
| 4 | CLAUDE.md Paso 0 + Paso N extendidos | `grep -c "explicit_final\|cross_session_snapshot" CLAUDE.md` | ≥2 hits |
| 5 | Smoke test bash: 2 sesiones simuladas → 2da hidrata 1ra | `bash scripts/smoke_test_cruz_001.sh` | exit 0 |
| 6 | Cero modificación migrations existing | `git diff origin/main migrations/sql/` | 0 lines |
| 7 | Cero modificación kernel/anti_dory/ | `git diff origin/main kernel/anti_dory/` | 0 lines |
| 8 | Cero colisión con VERIFICADOR-001 (otro file) | `git diff origin/main kernel/cowork_runtime/pre_response_hook.py` | 0 lines (VERIFICADOR-001 toca ese file) |

## §5 Limitaciones declaradas obligatorias (DSC-G-008 v3 §4)

| Id | Limitación | Mitigación |
|---|---|---|
| L_C1 | Snapshot cierre depende de Cowork invocar close() — si crash, último snapshot stale | Heartbeat auto-snapshot cada 30min via cron |
| L_C2 | Multiple Cowork simultáneos (laptop + iPhone) podrían write_conflict | lock_version optimistic — second loser hace retry |
| L_C3 | Summary 400 words max puede perder detalle | evidence_refs jsonb compensa con punteros |
| L_C4 | Doctrina markdown legacy (memory/cowork/*.md) sigue siendo source secundaria — drift posible | Snapshot summary referencia docs vigentes con commit hash |
| L_C5 | Firma T1 acelerada sin datos T+14d MEMENTO — riesgo: si datos reales contradicen necesidad, gastamos esfuerzo | Mitigado por ejecución paralela CRUZ + VERIFICADOR (ambas piezas valen, no necesitamos priorizar) |

## §6 NO-CRUCE reglas duras

- ❌ NO modificar migrations 0029-0035 (Anti-Dory cross-agente ya en prod)
- ❌ NO modificar `kernel/anti_dory/` (PR #129 mergeado)
- ❌ NO modificar `kernel/cowork_runtime/claim_calibration.py` (MEMENTO PR #128 mergeado)
- ❌ NO modificar `kernel/cowork_runtime/pre_response_hook.py` (VERIFICADOR-001 lo toca — colisión inter-sprint)
- ✅ SÍ extender `kernel/cowork_runtime/session_memory.py` (módulo Cowork puro)
- ✅ SÍ editar `CLAUDE.md` Paso 0 + Paso N (regla dura ya canonizada — extensión doctrinal natural)

## §7 Owner + cadencia

**Owner asignado:** Manus Ejecutor 1 (manus_hilo_a).

**Gate de arranque:** Manus E1 toma este sprint ÚNICAMENTE post:
1. D5-RETEST 6/6 verde
2. D6 ANTI_DORY_ENABLED=true Railway flag permanente firmado T1

**Cadencia esperada:** 3-5 días implementación + 1-2 días Cowork audit + merge.

## §8 Override decisión binaria T+14d (justificación T1 acelerada)

Spec original §8 (DRAFT) condicionaba firma a datos MEMENTO T+14d para decidir entre CRUZ-001 vs VERIFICADOR-001 basado en tasa F21 dominante.

**Override T1 verbatim 2026-05-14:** *"si ambos"* → firmar AMBAS piezas HOY + ejecutar paralelo. Trade-off doctrinal:

- ❌ Pierdo precisión data-driven sobre cuál ataca el F21 dominante
- ✅ AMBAS piezas valen (cross-sesión Y intra-sesión son problemas reales documentados)
- ✅ Ejecución paralela con 2 Manus distintos = misma calendar time sin priorización
- ✅ Anti-Dory 4/4 completo en ~T+14 días vs T+35 días planificación normal (21 días menos)
- ✅ Cowork blindado cross-sesión + intra-sesión simultáneamente

Autoridad: T1 directa override regla evolucionada CLAUDE.md ("convergencia 3 Sabios Tier 1" excepcionable por instrucción T1 verbatim).

## §9 Ejecución paralela con VERIFICADOR-001 (CRÍTICO)

CRUZ-001 y VERIFICADOR-001 corren en paralelo con asignaciones disjuntas:

| Pieza | Owner | File modificado | Posible colisión |
|---|---|---|---|
| CRUZ-001 | Manus E1 (post-D5/D6) | `kernel/cowork_runtime/session_memory.py` | ❌ Cero |
| VERIFICADOR-001 | Manus E2 (post-PR #118) | `kernel/cowork_runtime/pre_response_hook.py` | ❌ Cero |

CLAUDE.md SÍ es modificado por ambos sprints (CRUZ extiende Paso 0 + Paso N, VERIFICADOR no toca CLAUDE.md). Cero colisión.

Audit + merge: Cowork T2-A en orden de llegada (PR primero mergeado primero auditado).

## §10 Trayectoria post-firma

1. **HOY:** spec firmada + pusheada
2. **HOY+1-2h:** D5-RETEST cerrado + D6 firmado + E1 libre
3. **HOY+1d:** PR #118 rebase mergeado + E2 libre
4. **HOY+1-6d:** E1 implementa CRUZ-001 (paralelo) + E2 implementa VERIFICADOR-001 (paralelo)
5. **HOY+7-9d:** Cowork audita ambos + mergea ambos
6. **HOY+10-14d:** Shadow validación cada uno
7. **HOY+14d:** **Anti-Dory completo 4/4 piezas activas**

---

**Status:** `🟢 FIRMED — gate: D5-RETEST + D6 verde`
**Cowork T2-A firma con autoridad delegada T1 "si ambos" verbatim 2026-05-14.**
