---
sprint_id: MANUS-ANTI-DORY-002-v1
fase: D5-FIRST RAP-001 LIVE — GO-SIGNAL
autor: Cowork T2-A
fecha: 2026-05-14T13:28:47Z
destinatario: Manus Hilo Ejecutor 1 (manus_hilo_a)
referencia_kickoff: bridge/cowork_to_manus_HILO_EJECUTOR_1_D5_FIRST_RAP_001_LIVE_BINARIO_2026_05_14.md @ commit ac520a94
---

# 🚦 D5 GO-SIGNAL — Manus E1 UNBLOCKED

## §1 Snapshot canónico sembrado (verificado binariamente)

```
snapshot_id_seeded:    7eece471-b5ee-4e72-ab21-d8f123a6b4a1
head_snapshot_id:      7eece471-b5ee-4e72-ab21-d8f123a6b4a1   (match)
lock_version:          1
status:                accepted
writer_mode:           explicit_start
project_id:            el_monstruo
front_id:              anti_dory_d5_rap_001
sprint_id:             MANUS-ANTI-DORY-002-v1
phase:                 D5-FIRST
state_hash:            d5_rap_001_seed_2026_05_14
confidence_score:      0.95
created_at:            2026-05-14 13:28:47.987927+00
```

**Summary verbatim sembrado:**
> *"D5-FIRST seed canonico: PR 129 mergeado c40af8e1 + migrations 0034-0035 aplicadas prod + 11/11 verde binario. Sprint MANUS-ANTI-DORY-002-v1 FASE D2-D3-D4. Proximo: Manus E1 ejecuta create_task(prompt='continua lo de ayer con El Monstruo; no te reexplico nada', attach_context=true) con 4 env vars temporales. Atajo D4 monitor 24h autorizado T1."*

**evidence_refs (jsonb):**
```json
{"pr_129_squash": "c40af8e1", "migrations_applied": ["0029","0030","0031","0032","0033","0034","0035"]}
```

**do_not_touch (jsonb):**
```json
["kernel/anti_dory/", "migrations/sql/0029-0035"]
```

## §2 Kill switch flipped ON (verificado binariamente)

```
shadow_write_enabled:  true
last_enabled_at:       2026-05-14 13:28:47.987927+00
last_enabled_by:       T1_alfredo_D5_RAP_001_LIVE
singleton_lock:        anti_dory_singleton
rpc_check_shadow_enabled() returns:  true
```

## §3 Verificación binaria 8/8 verde

| Check | Esperado | Real |
|---|---|---|
| head_snapshot_id matches snapshot_id_seeded | true | ✅ |
| lock_version | 1 | ✅ 1 |
| snapshot_status | accepted | ✅ accepted |
| snapshot_writer_mode | explicit_start | ✅ explicit_start |
| snapshots_count para front_id | 1 (no dup) | ✅ 1 |
| shadow_write_enabled | true | ✅ true |
| rpc_check_shadow_enabled() returns | true | ✅ true |
| project_runtime_heads row exists | 1 | ✅ 1 |

## §4 Manus E1 — procede RAP-001 LIVE

Tu protocolo §8 pre-flight confirmado. Cowork sembró seed §3 + kill switch ON §2.

**Ejecuta verbatim:**

```bash
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
    sprint_id="MANUS-ANTI-DORY-002-v1",
    phase="D5-FIRST"
)
```

**Después valida los 6 acceptance criteria binarios §5.2 del kickoff bridge file.**

## §5 Acceptance criteria binarios (recordatorio verbatim del kickoff)

| # | Check | SQL/Comando | Esperado |
|---|---|---|---|
| 1 | T+1 task arranca | (manus dashboard) | task_id retornado, status running |
| 2 | T+1 hidrató del snapshot canónico | `SELECT payload FROM runtime_events WHERE event_type='snapshot_hydrated' AND thread_id=<T+1_thread_id> ORDER BY created_at DESC LIMIT 1` | row con `snapshot_id='7eece471-b5ee-4e72-ab21-d8f123a6b4a1'` |
| 3 | T+1 respondió con contexto correcto | (revisar output T+1) | T+1 cita PR #129 OR migrations 0034/0035 OR "FASE D2-D3-D4", NO escribe "no entiendo" |
| 4 | Kill switch sigue ON durante test | `SELECT shadow_write_enabled FROM anti_dory_runtime_flags WHERE singleton_lock='anti_dory_singleton'` | true |
| 5 | Budget no excedido | `SELECT write_count, max_writes FROM anti_dory_write_budget WHERE window_start_utc >= now() - interval '10 minutes'` | write_count ≤ max_writes en 3 ventanas |
| 6 | runtime_events log limpio | `SELECT count(*) FROM runtime_events WHERE event_type LIKE '%error%' AND created_at >= now() - interval '30 minutes'` | 0 |

## §6 Compromiso Cowork post-test

Al recibir tu bridge file `manus_to_cowork_D5_RAP_001_RESULT_2026_05_14.md`:

- Si **6/6 verde** → Cowork ratifica veredicto + flip kill switch OFF + emite frase canónica `🏛️ D5 GREEN — DORY MUERTO BINARIAMENTE VALIDADO` + propone D6 a T1
- Si **≤5/6** → Cowork flip kill switch OFF + audit forense del fallo específico, NO afirma éxito

## §7 F-pattern menor documentado (transparencia)

Durante el seed §1, mi query inicial usó pattern `(public.rpc_accept_snapshot(...)).*` dentro de CTE. PostgreSQL evaluó la función **2 veces**: la 1ra hizo el INSERT del head (accepted=true, lock=1), la 2da vio el head ya existente con lock=1 y reportó `conflict_reason='lock_version_conflict:expected=0,actual=1'` (cosmético, sin efecto real).

Verificación §3 confirma que el estado persistido es correcto (1ra evaluación es la que cuenta). **Aprendizaje para canonización futura:** NO expandir `RETURNS TABLE` con `.*` en CTE para funciones con side effects — usar `SELECT * FROM rpc(...)` directo. Candidato a DSC nuevo si se repite.

---

**Cowork T2-A — go-signal firmado.**

**Manus E1: procede. Esperando bridge file resultado.**
