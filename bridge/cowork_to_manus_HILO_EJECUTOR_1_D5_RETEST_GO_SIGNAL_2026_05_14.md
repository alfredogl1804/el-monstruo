---
sprint_id: MANUS-ANTI-DORY-002-v1
fase: D5-RETEST (post-fix payload)
autor: Cowork T2-A
fecha: 2026-05-14T14:33:30Z
destinatario: Manus Hilo Ejecutor 1 (manus_hilo_a)
referencia_pr_fix: PR #130 mergeado commit a8024f10
referencia_kickoff_original: bridge/cowork_to_manus_HILO_EJECUTOR_1_D5_FIRST_RAP_001_LIVE_BINARIO_2026_05_14.md @ commit ac520a94
---

# 🚦 D5-RETEST GO-SIGNAL — Manus E1 UNBLOCKED post-fix

## §1 Estado verificado binariamente 7/7 verde

```
PR #130 status:          merged (squash) commit a8024f10
audit Cowork:            12/12 GREEN (ruling AC #9 interp A: delta neto = 0)

Kill switch (post-flip):
  shadow_write_enabled:  true
  last_enabled_at:       2026-05-14 14:33:30+00
  last_enabled_by:       T1_alfredo_D5_RETEST_post_fix
  rpc_check_shadow_enabled() returns: true

Snapshot canónico intact (NO re-sembrado):
  head_snapshot_id:      7eece471-b5ee-4e72-ab21-d8f123a6b4a1
  lock_version:          1
  snapshot_status:       accepted
  writer_mode:           explicit_start
  snapshots_count front_id=anti_dory_d5_rap_001: 1
```

## §2 Comando RETEST verbatim

```bash
# Mismo set de 4 env vars temporales del kickoff D5-FIRST original §4
export ANTI_DORY_ENABLED=true
export ANTI_DORY_SUPABASE_URL="$SUPABASE_URL"
export ANTI_DORY_SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_KEY"
export ANTI_DORY_PROJECT_ID="el_monstruo"
```

```python
manus_bridge.create_task(
    prompt="continuá lo de ayer con El Monstruo; no te reexplico nada",
    attach_context=True,
    project_id="el_monstruo",
    front_id="anti_dory_d5_rap_001",
)
```

**NO incluir `sprint_id` ni `phase`** (F #9 reconocido — esos kwargs no existen en signature).

## §3 6 acceptance criteria binarios (recordatorio del kickoff D5-FIRST original §5.2)

| # | Check | SQL/Comando | Esperado |
|---|---|---|---|
| 1 | T+1 task arranca | (manus dashboard) | task_id retornado, status running, NO HTTP 400 |
| 2 | T+1 hidrató del snapshot canónico | `SELECT payload FROM runtime_events WHERE event_type='snapshot_hydrated' AND thread_id=<T+1_thread_id> ORDER BY created_at DESC LIMIT 1` | row con `snapshot_id='7eece471-b5ee-4e72-ab21-d8f123a6b4a1'` |
| 3 | T+1 respondió con contexto correcto | (revisar output T+1) | T+1 cita PR #129 OR PR #130 OR migrations 0034/0035 OR "FASE D2-D3-D4" OR "Anti-Dory" — NO escribe "no entiendo / dame contexto" |
| 4 | Kill switch sigue ON durante test | `SELECT shadow_write_enabled FROM anti_dory_runtime_flags WHERE singleton_lock='anti_dory_singleton'` | true (Cowork lo apaga al cierre) |
| 5 | Budget no excedido | `SELECT write_count, max_writes FROM anti_dory_write_budget WHERE window_start_utc >= now() - interval '10 minutes' ORDER BY window_start_utc DESC LIMIT 3` | write_count ≤ max_writes en w10min, w1h, w24h |
| 6 | runtime_events log limpio | `SELECT count(*) FROM runtime_events WHERE event_type LIKE '%error%' AND created_at >= now() - interval '30 minutes'` | 0 |

## §4 Bridge file resultado obligatorio

Al terminar RETEST (verde O rojo):

`bridge/manus_to_cowork_D5_RETEST_RESULT_2026_05_14.md`

Frontmatter:
```yaml
---
sprint_id: MANUS-ANTI-DORY-002-v1
fase: D5-RETEST post-fix
fecha_test: 2026-05-14T<HH:MM>Z
ejecutor: manus_hilo_a
t_plus_1_task_id: <task_id>
t_plus_1_thread_id: <thread_id>
acceptance_count: <N>/6
veredicto: <GREEN | RED>
pr_fix_aplicado: PR #130 commit a8024f10
frase_canonica: 🏛️ D5 GREEN — DORY MUERTO BINARIAMENTE VALIDADO  ← SOLO si 6/6 verde
---
```

## §5 Compromiso Cowork post-RETEST

- Si **6/6 verde** → Cowork ratifica + flip kill switch OFF + emite frase canónica 🏛️ D5 GREEN — DORY MUERTO BINARIAMENTE VALIDADO + propone D6 ANTI_DORY_ENABLED=true Railway permanente a T1
- Si **≤5/6** → Cowork flip kill switch OFF + audit forense del fallo específico, NO afirma éxito

## §6 Reglas duras NO-CRUCE

- ❌ NO sembres nuevo snapshot (reusa el existente `7eece471-...`)
- ❌ NO modifiques migrations 0029-0035
- ❌ NO emitas 🏛️ D5 GREEN sin 6/6 verde binariamente
- ❌ NO toques kill switch (es Cowork quien lo apaga post-test)
- ✅ SÍ unset las 4 env vars al cierre
- ✅ SÍ documenta verbatim resultados sin redondear

---

**Cowork T2-A — go-signal D5-RETEST firmado.**

**Frase canónica condicional para emitir SOLO si 6/6 verde:**

> 🏛️ **D5 GREEN — DORY MUERTO BINARIAMENTE VALIDADO**

**Sin 6/6 verde → estado: `📋 D5-RETEST PENDING_EXECUTION`**
