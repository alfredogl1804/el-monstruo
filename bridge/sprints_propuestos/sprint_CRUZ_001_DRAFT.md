---
sprint_id: CRUZ-001
estado: DRAFT — NO FIRMADO (espera decisión binaria T+14d post-datos MEMENTO)
autor: Cowork T2-A
fecha_draft: 2026-05-14
piezas_anti_dory: PIEZA 3 cross-sesión Cowork
dependencia: MEMENTO T+14d report (decide entre CRUZ-001 vs VERIFICADOR-001)
infraestructura_reusada: thread_snapshots + project_runtime_heads (migrations 0030 + 0031 ya en prod)
---

# SPRINT CRUZ-001 — Anti-Dory cross-sesión Cowork (DRAFT)

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

## §5 Limitaciones declaradas obligatorias (DSC-G-008 v3 §4)

| Id | Limitación | Mitigación |
|---|---|---|
| L_C1 | Snapshot cierre depende de Cowork invocar close() — si crash, último snapshot stale | Heartbeat auto-snapshot cada 30min via cron |
| L_C2 | Multiple Cowork simultáneos (laptop + iPhone) podrían write_conflict | lock_version optimistic — second loser hace retry |
| L_C3 | Summary 400 words max puede perder detalle | evidence_refs jsonb compensa con punteros |
| L_C4 | Doctrina markdown legacy (memory/cowork/*.md) sigue siendo source secundaria — drift posible | Snapshot summary referencia docs vigentes con commit hash |

## §6 NO-CRUCE reglas duras

- ❌ NO modificar migrations 0029-0035 (Anti-Dory cross-agente ya en prod)
- ❌ NO modificar `kernel/anti_dory/` (PR #129 mergeado)
- ❌ NO modificar `cowork_runtime/claim_calibration.py` (MEMENTO PR #128 mergeado)
- ✅ SÍ extender `kernel/cowork_runtime/session_memory.py` (módulo Cowork puro)
- ✅ SÍ editar `CLAUDE.md` Paso 0 + Paso N (regla dura ya canonizada — extensión doctrinal natural)

## §7 Owner + cadencia

**Owner:** Manus Ejecutor 1 o 2 (cualquier hilo libre). Cowork NO escribe código kernel (regla inviolable CLAUDE.md).

**Cadencia esperada:** 3-5 días desde firma T1 + datos T+14d MEMENTO → spec firmado → implementación → audit + merge.

## §8 Decisión binaria T+14d Sabios

Esta spec se firma SOLO si datos MEMENTO T+14d muestran:
- Tasa F21 cross-sesión (Cowork olvida estado entre sesiones) > tasa F21 intra-sesión (Cowork afirma sin verificar)
- Si lo contrario → priorizar VERIFICADOR-001 (PIEZA 4) que ataca intra-sesión

Mientras tanto, esta spec queda DRAFT. **NO firmar hasta convergencia 3 Sabios Tier 1 DSC-V-001 sobre los datos T+14.**

---

**Status:** `📋 DRAFT PENDING_DATA_DRIVEN_SIGNATURE`
