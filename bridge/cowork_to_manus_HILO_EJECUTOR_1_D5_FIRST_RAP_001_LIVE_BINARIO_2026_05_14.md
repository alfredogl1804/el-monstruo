---
sprint_id: MANUS-ANTI-DORY-002-v1
fase: D5-FIRST (camino acelerado, salta D4 monitor 24h)
autor: Cowork T2-A (Claude Opus 4.7)
fecha: 2026-05-14
destinatario: Manus Hilo Ejecutor 1 (manus_hilo_a)
autoridad: T1 Alfredo Góngora — orden directa "camino acelerado"
convergencia_doctrinal: Tier 1 DSC-V-001 (Opus 4.7 + GPT-5.5 Pro + Cowork-Sabio read-only)
estado_pre_kickoff: PR #129 MERGEADO + migrations 0034 + 0035 APLICADAS PROD + 11/11 VERIFICACIÓN BINARIA VERDE
---

# 🎯 KICKOFF D5-FIRST — RAP-001 LIVE BINARIO

> **Frase canónica magna GPT-5.5 Pro (input doctrinal):**
> *"Shadow prod no es activación: es instrumentación reversible con cero hidratación hasta que el attachment real pase prueba binaria."*

> **Orden T1 verbatim (2026-05-14):**
> *"si camino acelerado"* — saltar D4 monitor 24h, ir directo a RAP-001 LIVE test binario.

---

## §1 ESTADO REAL VERIFICADO BINARIAMENTE (no asumido — F21 reconocido)

**Cowork T2-A reconoce F21 magna previa** (intentó dar prompt con estado futuro como presente). Esta versión contiene estado verbatim REAL post-apply ejecutado HOY 2026-05-14.

### §1.1 PRs mergeados main

| PR | Sprint | Commit squash | Verificado |
|---|---|---|---|
| #124 | FASE A SPEC | `14e05ea9` | ✅ via `get_pull_request` |
| #125 | FASE B impl | (en main) | ✅ via `get_pull_request` |
| #126 | FASE C wire opt-in | (en main) | ✅ via `get_pull_request` |
| #127 | FASE D1 SupabaseRPCClient | (en main) | ✅ via `get_pull_request` |
| #128 | MEMENTO-001 | (en main) | ✅ via `get_pull_request` |
| #129 | FASE D2-D3-D4 shadow blindado | `c40af8e1` | ✅ via `get_pull_request` |

### §1.2 Migrations aplicadas prod (orden estricto verificado)

```sql
-- Query Cowork ejecutó: SELECT version, name FROM supabase_migrations.schema_migrations WHERE version >= '0029' ORDER BY version DESC LIMIT 7
-- Resultado verbatim:
20260514130603 → 0035_anti_dory_runtime_flags     ✅
20260514130515 → 0034_anti_dory_grants            ✅
20260514124043 → 0033_cowork_claims_calibration   ✅ (MEMENTO)
20260514100752 → 0032_anti_dory_rpcs              ✅
20260514100712 → 0031_project_runtime_heads       ✅
20260514100656 → 0030_thread_snapshots            ✅
20260514100632 → 0029_runtime_events              ✅
```

### §1.3 Verificación binaria 11/11 verde (Cowork ejecutó vía MCP execute_sql)

| Check | Esperado | Real verificado |
|---|---|---|
| 0034 service_role MEMBER writer_role | true | ✅ true |
| 0034 service_role MEMBER reader_role | true | ✅ true |
| 0035 flags_rls_enabled | true | ✅ true |
| 0035 flags_policy_count | ≥1 | ✅ 1 |
| 0035 flags_singleton_count | 1 | ✅ 1 |
| 0035 flags_singleton_shadow_enabled | false (fail-closed default) | ✅ false |
| 0035 budget_rls_enabled | true | ✅ true |
| 0035 budget_policy_count | ≥1 | ✅ 1 |
| 0035 rpc_check_shadow_exists | true | ✅ true |
| 0035 rpc_increment_budget_exists | true | ✅ true |
| 0035 rpc_check_shadow_enabled() returns | false | ✅ false |

### §1.4 RPCs disponibles (firmas verbatim verificadas via pg_proc)

```sql
rpc_accept_snapshot(p_project_id text, p_front_id text, p_snapshot_id uuid, p_expected_lock_version integer)
rpc_check_shadow_enabled()
rpc_get_context_head(p_project_id text, p_front_id text)
rpc_increment_write_budget(p_now timestamp with time zone)
rpc_recovery_scan(p_project_id text, p_front_id text)
rpc_write_runtime_event(p_project_id text, p_front_id text, p_actor_type text, p_event_type text, p_payload jsonb, p_thread_id text, p_snapshot_id uuid)
rpc_write_thread_snapshot(p_project_id text, p_front_id text, p_actor_type text, p_state_hash text, p_writer_mode text, p_parent_snapshot_id uuid, p_sprint_id text, p_phase text, p_last_t1_decision text, p_next_expected_action text, p_do_not_touch jsonb, p_evidence_refs jsonb, p_confidence_score numeric, p_summary text)
```

---

## §2 PRE-REQUISITO D5: ACTIVAR KILL SWITCH PARA EL TEST (Cowork firma T2-A)

El kill switch `anti_dory_runtime_flags.shadow_write_enabled` está en **false** (fail-closed default 0035). Para D5 LIVE necesitamos flip a **true** únicamente durante el test. Esto lo hace **Cowork ANTES de tu test** vía MCP execute_sql:

```sql
-- Cowork ejecuta esto al recibir tu confirmación de listo:
UPDATE public.anti_dory_runtime_flags
   SET shadow_write_enabled = true,
       last_enabled_at = now(),
       last_enabled_by = 'T1_alfredo_D5_RAP_001_LIVE'
 WHERE singleton_lock = 'anti_dory_singleton';
```

**No actives nada tú — Cowork lo flip antes de que ejecutes RAP-001 y lo apaga al cierre del test.**

---

## §3 SEED SNAPSHOT CANÓNICO (Cowork ejecuta antes de tu test — NO TÚ)

Para que `RAP-001 LIVE` valide attachment real, necesitamos un snapshot canónico que el T+1 task pueda hidratar. Cowork lo siembra **antes** de tu kickoff con valores verbatim:

```sql
-- 1. Write snapshot canónico (Cowork ejecuta)
SELECT * FROM public.rpc_write_thread_snapshot(
    p_project_id          := 'el_monstruo',
    p_front_id            := 'anti_dory_d5_rap_001',
    p_actor_type          := 'cowork',
    p_state_hash          := 'd5_rap_001_seed_2026_05_14',
    p_writer_mode         := 'canonical',
    p_parent_snapshot_id  := NULL,
    p_sprint_id           := 'MANUS-ANTI-DORY-002-v1',
    p_phase               := 'D5-FIRST',
    p_last_t1_decision    := 'Camino acelerado D5-FIRST autorizado',
    p_next_expected_action := 'Manus E1 ejecuta RAP-001 LIVE binario',
    p_do_not_touch        := '["kernel/anti_dory/", "migrations/sql/0029-0035"]'::jsonb,
    p_evidence_refs       := '{"pr_129_squash": "c40af8e1", "migrations_applied": ["0029","0030","0031","0032","0033","0034","0035"]}'::jsonb,
    p_confidence_score    := 0.95,
    p_summary             := 'D5-FIRST seed canónico: PR #129 mergeado + migrations 0034-0035 aplicadas prod + 11/11 verde binario. Próximo: Manus E1 ejecuta RAP-001 LIVE con create_task(attach_context=true). Atajo D4 monitor 24h autorizado T1.'
);

-- 2. Confirmar snapshot aceptado como head
-- (Cowork tomará snapshot_id retornado del paso 1 + lock_version actual de project_runtime_heads)
SELECT public.rpc_accept_snapshot(
    p_project_id           := 'el_monstruo',
    p_front_id             := 'anti_dory_d5_rap_001',
    p_snapshot_id          := '<UUID retornado por paso 1>',
    p_expected_lock_version := <lock_version actual de project_runtime_heads>
);
```

**Tú NO ejecutas esto.** Cowork lo siembra. Tu confirmación de listo dispara el seed + flip kill switch + flag env temporal.

---

## §4 FLAGS ENV — SOLO PARA TASK TEST, NO RAILWAY PERMANENTE

Para que `manus_bridge.create_task(attach_context=True)` realmente atache el snapshot canónico recién sembrado, el proceso que ejecutas debe tener estas 4 env vars **solo para el task de test** (NO commitear a Railway config permanente):

```bash
export ANTI_DORY_ENABLED=true                       # wire opt-in encendido SOLO este task
export ANTI_DORY_SUPABASE_URL="$SUPABASE_URL"       # ya tienes
export ANTI_DORY_SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_KEY"   # ya tienes
export ANTI_DORY_PROJECT_ID="el_monstruo"           # alineado con seed §3
```

**Importante doctrina (GPT-5.5 Pro frase canónica):** este encendido es **instrumentación reversible** — al cierre del test, `unset` las 4 vars + Cowork hace flip kill switch a false.

---

## §5 PRUEBA BINARIA D5 — RAP-001 LIVE (la prueba real)

### §5.1 Comando de invocación verbatim

Ejecutas en tu hilo (manus_hilo_a) un único `create_task` con estos parámetros exactos:

```python
manus_bridge.create_task(
    prompt="continuá lo de ayer con El Monstruo; no te reexplico nada",
    attach_context=True,                # 🔑 D5 valida que esto realmente atache
    project_id="el_monstruo",
    front_id="anti_dory_d5_rap_001",
    sprint_id="MANUS-ANTI-DORY-002-v1",
    phase="D5-FIRST"
)
```

El prompt **NO menciona nada del estado** — eso es deliberado. Si el T+1 task respondiera correctamente, lo hace porque el snapshot canónico sembrado en §3 lo hidrató. Sin hidratación → T+1 dice "no tengo contexto" → Dory.

### §5.2 6 ACCEPTANCE CRITERIA BINARIOS (todos verde = D5 GREEN)

| # | Check | SQL/Comando binario | Esperado |
|---|---|---|---|
| 1 | T+1 task realmente arranca | (manus dashboard task creada) | task_id retornado, status running |
| 2 | T+1 hidrató del snapshot canónico §3 (no del prompt) | `SELECT payload FROM runtime_events WHERE event_type='snapshot_hydrated' AND thread_id=<T+1_thread_id> ORDER BY created_at DESC LIMIT 1` | row con `snapshot_id=<UUID seed §3>` |
| 3 | T+1 respondió con contexto correcto sin pedir aclaración | (revisar output T+1) | T+1 NO escribió "no entiendo / dame contexto / no tengo info". Cita explícitamente PR #129 OR migrations 0034/0035 OR "sprint Anti-Dory FASE D2-D3-D4" |
| 4 | Kill switch sigue ON durante el test | `SELECT shadow_write_enabled FROM anti_dory_runtime_flags WHERE singleton_lock='anti_dory_singleton'` | true (Cowork lo apaga al cierre) |
| 5 | Budget no excedido durante test | `SELECT write_count, max_writes FROM anti_dory_write_budget WHERE window_start_utc >= now() - interval '10 minutes' ORDER BY window_start_utc DESC LIMIT 3` | write_count ≤ max_writes en w10min, w1h, w24h |
| 6 | runtime_events log limpio (sin errores write) | `SELECT count(*) FROM runtime_events WHERE event_type LIKE '%error%' AND created_at >= now() - interval '30 minutes'` | 0 |

**Veredicto binario:**
- 6/6 verde → 🏛️ **D5 GREEN — DORY MUERTO BINARIAMENTE VALIDADO**
- ≤5/6 verde → 🔴 **D5 RED — investigar fallo específico, no afirmar éxito**

---

## §6 BRIDGE FILE DE CIERRE OBLIGATORIO

Al terminar test (verde O rojo), redactas:

`bridge/manus_to_cowork_D5_RAP_001_RESULT_2026_05_14.md`

Con frontmatter:
```yaml
---
sprint_id: MANUS-ANTI-DORY-002-v1
fase: D5-FIRST RAP-001 LIVE
fecha_test: 2026-05-14T<HH:MM>Z
ejecutor: manus_hilo_a
t_plus_1_task_id: <task_id>
t_plus_1_thread_id: <thread_id>
acceptance_count: <N>/6
veredicto: <GREEN | RED>
frase_canonica: 🏛️ D5 GREEN — DORY MUERTO BINARIAMENTE VALIDADO  ← SOLO si 6/6 verde
---
```

Cuerpo:
- §1 Tabla 6 acceptance con SQL/comando ejecutado + resultado verbatim (sin redondear)
- §2 Si RED: SQL específico del fallo + diagnosis
- §3 Limitaciones DSC-G-008 v3 §4 declaradas
- §4 Próxima acción T1 propuesta (D6 ANTI_DORY_ENABLED=true Railway permanente, o investigación si RED)

---

## §7 REGLAS DURAS NO-CRUCE

- ❌ NO modifiques migrations 0029-0035 (ya en prod)
- ❌ NO hagas commit a Railway config con ANTI_DORY_ENABLED=true permanente (eso es D6 — T1 firma después)
- ❌ NO emitas 🏛️ D5 GREEN sin 6/6 verde binariamente. F21 monitoring activo (Cowork-Sabio read-only audit pendiente)
- ❌ NO toques kill switch (es Cowork quien lo flip on antes / off después)
- ✅ SÍ ejecuta el test con los 4 env vars temporales
- ✅ SÍ documenta verbatim resultados, RED o GREEN — fail-honestly > success-fabricated

---

## §8 CONFIRMACIÓN PROTOCOLO

**Tu primer turno responde con:**

```
[E1 D5-FIRST PRE-FLIGHT]
Leí el kickoff. Confirmo entendimiento:
- §1 Estado real entendido (PR #129 mergeado, 7 migrations aplicadas, 11/11 verde)
- §2 Cowork firma flip kill switch ON antes / OFF después
- §3 Cowork siembra snapshot canónico antes
- §4 Activo 4 env vars solo para task test
- §5 Ejecuto create_task verbatim + valido 6 acceptance binarios
- §6 Redacto bridge file cierre
- §7 Reglas duras entendidas

Listo para ejecutar cuando Cowork confirme:
(a) snapshot canónico sembrado + snapshot_id retornado
(b) kill switch flipped ON

Esperando go-signal Cowork.
```

Sin esa confirmación verbatim, Cowork NO siembra snapshot ni flip kill switch. **Tu protocolo entendido bloquea el siguiente paso.**

---

**Cowork T2-A firma este kickoff con autoridad delegada T1 Alfredo Góngora.**
**Frase canónica condicional para emitir SOLO si 6/6 verde:**
> 🏛️ **D5 GREEN — DORY MUERTO BINARIAMENTE VALIDADO**

**Sin verde 6/6 → estado actual: `📋 D5 PENDING_EXECUTION`**
