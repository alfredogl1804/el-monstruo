# DORY-CURE-CONVERGED-001 v1.0 DRAFT — Fusión Cowork-orchestrated

> **Tipo:** DRAFT propositivo Cowork T2-A — fusión doctrinal de 3 specs auditados HOY
> **Estado:** NO canon. NO implementación. NO firmado T1. Depositado en main bajo regla Cowork S7 + autorización T1 verbatim "seguimos manus pide que pushees" 2026-05-19.
> **Fuentes fusionadas (todas leídas binariamente HOY):**
> - MANUS-ANTI-DORY-003 v0.2 (Cowork commit `b3e211c2`)
> - DORY-CURE-001 v0.3 DRAFT (Perplexity, 13,893 bytes, SHA `50ea8f60`)
> - DORY-CURE-001 v0.4 DELTA (Perplexity, 8,492 bytes, SHA `6d67c486`)
> - ANTI-CONTEXT-LOSS-001 v1.2 (Manus E2, 22,069 bytes, SHA `c3441315`)
>
> **Caveat magno:** este DRAFT es PROPOSICIONAL Cowork. No sustituye originales. Convergencia 3 Sabios NO-Perplexity OBLIGATORIA pre-firma T1.

---

## §0 Identidad y rol

- **T1 = Alfredo** (único firmante magno)
- **T2-A Cowork** = arquitecto fusión (autor DRAFT)
- **T3 ejecutores** = Manus E1/E2/Catastro (target Fase 1 EXPERIMENTO T+14D)
- **Out-of-scope absoluto:** Nightly Builder R1, anonymous classification, APP_VISION write

---

## §1 Veredicto + cura 96% honesta + caveat residual <4%

**Tomado verbatim de Manus E2 v1.2** (anti-F19/F6):

> "En **≥96% de escenarios de prueba realistas**, un hilo que compacte, se degrade, muera o sea reemplazado puede recuperar estado operativo suficiente para continuar sin reexplicación humana, sin inventar, sin violar no-go list y sin filtrar secretos."

**NO "98% operativa". NO "Dory curado".** Cura **operativa, no matemática absoluta**, validable contra DORY_BENCH_1000 firmado.

**Residual <4% desglosado en 4 categorías (Manus E2):**

| # | Categoría | % | Mitigación parcial |
|---|---|---|---|
| 1 | Alucinación adversarial LLM al razonar sobre contexto inyectado | 1.5% | Echo-Back coercitivo + VERIFICADOR-001 |
| 2 | Catástrofe simultánea 3 proveedores | <1% | Capa Offline + GitHub append-only |
| 3 | Bugs nuevos en frameworks/glue (LangGraph/DBOS) | 1% | Tests + monitoreo upstream |
| 4 | Error humano T1 firmando contradictorio | <0.5% | Fuera scope kernel (MEMENTO + CRUZ cubren parcial) |

**Evidencia binaria del residual <5%:** Manus E2 detectó al vivo Perplexity Sonar Reasoning Pro fabricando 5 citas verificables durante validación de v1.2 mismo. El propio proceso de validación demostró el riesgo. **Este evento es input doctrinal vivo a este spec fusionado.**

---

## §2 Coordinación verbatim con sistemas vigentes

| Sistema vigente | Relación con DORY-CURE-CONVERGED-001 |
|---|---|
| **MANUS-ANTI-DORY-003 v0.2** (Cowork READY_FOR_T1_REVIEW) | Base intra-hilo conservada. EXTIENDE con Bounded State Capsule cripto-verificable + frameworks maduros + Echo-Back |
| **MANUS-ANTI-DORY-002 v1** (mergeado PR #125) | Attachment inicial / Context Broker. REUSADO directo |
| **MEMENTO Capa Memoria Soberana v1.0** (vivo kernel) | Validator + ContaminationDetector. INVOCADO antes de acciones críticas |
| **COWORK-MEMENTO-001** (mergeado PR #128) | Claim calibration retrospectiva. ALIMENTA F-pattern metrics |
| **CRUZ-001** (FIRMED, pending impl Manus E1) | Cross-sesión Cowork. CONSUMIDOR de Bounded State Capsule |
| **VERIFICADOR-001** (FIRMED, stash `d534c4a`) | Pre-emit blocking high-risk claims. RED DE SEGURIDAD final |
| **Control Tower Bridge Standard** (canonizado HOY) | Output operativo visible cross-agente |
| **DSC-G-013 v0.1 Coherence Gate Nivel A** | Pre-acción DB↔repo↔código check. INTEGRADO en Capa 9 Guardian |

**Regla magna:** Si conflicto entre este spec y sistemas vigentes, este spec **cita el conflicto + pide decisión T1**. NO sobrescribe automáticamente.

---

## §3 Problema cubierto — 5 vectores Dory

| Vector | Descripción | Cubierto por capas |
|---|---|---|
| **D1 Cold start** | Hilo nuevo sin contexto | Anti-Dory 002 + Capa 1 + Capa 5 |
| **D2 Compaction loss** | Compactación pierde detalles críticos | Capa 5 + Capa 6 + Capa 7 + Capa 8 |
| **D3 Intra-thread drift** | Hilo se degrada horas | Capa 4 + Capa 5 |
| **D4 Evidence drift** | PR/branch/migration/runtime cambia sin detección | Capa 1 + Capa 4 + Capa 7 + Capa 9 |
| **D5 Poison/secrets** | Persiste basura, instrucciones o secretos | Capa 8 sanitization + Capa 10 firewall |

---

## §4 Arquitectura — 12 capas convergentes

### **Capa 0 — External Kill-Switch Layer** (Perplexity v0.4)

```yaml
external_kill_switch_layer:
  name: "DORY_CURE_EXTERNAL_KILL_SWITCH"
  independence_requirement: "MUST_NOT_DEPEND_ON_CONTEXT_HEALTH"
  sources_order:
    - "local_kill_file: .monstruo/kill_switches/DORY_CURE_DISABLED"
    - "supabase_runtime_flag: anti_dory_runtime_flags.dory_cure_enabled"
    - "github_control_file: bridge/control_tower/runtime_flags/DORY_CURE_STATUS.md"
  default_if_all_unreachable: "DISABLED_FOR_MAGNA_ACTIONS"
  ttl_per_source_minutes: 5  # ← Cowork agrega resolviendo gap v0.4
```

**T1 verbatim "pausá Dory-Cure"** → local kill file creado primero, antes que cualquier otro paso.

### **Capa 1 — Source of Truth externa** (Perplexity v0.3)

GitHub + Supabase + Bridge + Docs canon + Runtime endpoints. **El transcript del hilo NUNCA es fuente de verdad.**

### **Capa 2 — Bounded State Capsule cripto-verificable** (Perplexity v0.3 + Cowork extensiones)

```yaml
bounded_state_capsule:
  schema_version: "1.0"
  capsule_id: "uuid"
  parent_capsule_id: "uuid|null"
  freshness_ttl_minutes: 240  # ← Cowork resuelve gap "capsule fresca"
  agent:
    agent_id: "manus_e2"
    role: "T3_EXECUTOR"
    platform: "manus|cowork|perplexity"
  scope:
    project_id: "el-monstruo"
    front_id: "la-forja-d6"
    active_sprint: "..."
    active_branch: "..."
    active_prs: [...]
  objective:
    current_objective: "..."
    next_allowed_action: "..."
    prohibited_actions: [merge, apply_migration, deploy, touch_secrets, r1]
  governance:
    last_t1_decision: "verbatim string"
    no_go_refs: [No Nightly Builder R1, No anonymous decision, No Dory muerto]
  evidence:
    evidence_refs:
      - type: "github_pr|github_commit|supabase_query|bridge|docs"
        ref: "url|path|sha"
  health:
    context_health_score: int
    context_health_state: "OK|WARN|REHYDRATE|HALT"
    last_rehydrated_at: "iso_timestamp"
    rehydration_count_session: int
  integrity:
    capsule_hash: "sha256:<hash>"
    parent_capsule_hash: "sha256:<hash|null>"
    event_log_tail_hash: "sha256:<hash>"
    evidence_index_hash: "sha256:<hash>"
    signature_mode: "hmac_phase_1|ed25519_phase_2|none_phase_0"  # ← Cowork defer key mgmt
    signer: "system|cowork|manus|perplexity"
    signed_at: "iso_timestamp"
```

**Caveat key management:** Fase 0 (diseño) = `signature_mode: none`. Fase 1 (canary) = `hmac_phase_1` con HMAC simple (key compartida ambiente). Fase 2+ = `ed25519_phase_2` con key management formal (DSC nuevo `DSC-MO-XXX_dory_cure_key_management` requerido).

**Reglas cápsula (Perplexity verbatim):**
- `capsule_hash` no valida → **HALT**
- Cadena `parent_capsule_hash` rota → **REHYDRATE once**; persiste → **HALT**
- Acción magna sin cápsula firmada y fresca (< TTL) → **HALT**
- Evidencia citada no verificable → downgrade a `DRAFT_PENDING_VERIFICATION`

### **Capa 3 — Event Log append-only** (Perplexity v0.3 + Capa 8 sanitization v0.4)

```json
{
  "schema_version": "1.0",
  "event_id": "uuid",
  "agent_id": "...",
  "project_id": "...",
  "front_id": "...",
  "event_type": "...",
  "evidence_ref": "...",
  "result_hash": "sha256:...",
  "created_at": "...",
  "side_effect": false,
  "side_effect_validator": "allowlist_check|guardian_pass|none"
}
```

**Validador binario `side_effect: false` (Cowork resuelve gap audit v0.3):**

`side_effect: false` requiere ≥1 de:
- (a) tool call signature en **read-only allowlist** verificable (Read/Grep/Glob/get_*/query_*/list_*)
- (b) Guardian Decision View con `recommendation: "ALLOW_READ_ONLY"`
- (c) `none` solo permitido si `result_hash` NO existe (acción no-op)

Sin estos, `side_effect: false` rechazado → evento downgrade a `UNTRUSTED`.

### **Capa 4 — Context Health Monitor** (Manus E2 + Perplexity convergentes)

```yaml
context_health_signals:
  - branch_declarado_neq_real: 2
  - pr_base_sha_obsoleto: 2
  - migration_repo_neq_supabase: 3
  - scope_bleed: 3
  - repite_error_corregido: 2
  - cita_dsc_inexistente: 3
  - turnos_sin_rehydration_gt_n: 1
  - compactacion_detectada: 4
  - accion_magna_sin_preflight: 5
  - hash_capsule_invalido: 10
  - kill_switch_remoto_on: 10

context_health_states:
  - score: "0-2"
    state: "OK"
    action: "continuar"
  - score: "3-5"
    state: "WARN"
    action: "verificar antes acción magna"
  - score: "6-9"
    state: "REHYDRATE"
    action: "rehidratación obligatoria antes output"
  - score: "≥10"
    state: "HALT"
    action: "detener + bridge halt_events.md + T1/Cowork"

rehydration_loop_policy:
  max_attempts_per_30min: 3
  same_cause_repeats: "HALT"
  new_cause_each_time: "ESCALATE_COWORK"
  external_state_unavailable: "DEGRADED_READONLY"
```

### **Capa 5 — Live Rehydration** (Manus E2 + Perplexity convergentes)

**8 triggers (combinación binaria):**
1. Compactación detectada (post-summary)
2. Cada N turnos (default N=15, configurable)
3. Cada X minutos (default X=20)
4. Antes de acción magna
5. Palabra T1 verbatim "rehidrátate"
6. Context-health ≥6
7. Hilo retomado tras pausa
8. Hilo nuevo desde `agent_id` + `front_id`

**Lecturas permitidas (allowlist):**
- Cápsula actual + event log sanitizado
- GitHub PR/branch/commit/checks
- Supabase heads/snapshots/migrations
- Bridge propio agente + docs canon (CLAUDE.md, AGENTS.md, _INDEX.md, DSCs)
- No-go list

**Prohibido leer/persistir:** secrets, cookies/JWTs, env values, bridges otros agentes sin cross-validation, contenido externo no firmado.

### **Capa 6 — Echo-Back Coercitivo** (Manus E2 Mec 2 — APORTE ÚNICO)

**Anti-alucinación post-rehidratación:**

```yaml
echo_back_policy:
  enforce_on:
    - "post_rehydration_first_response"
    - "post_compaction_first_response"
    - "pre_magna_action"
  protocol:
    1: "Kernel inyecta primera línea verbatim del snapshot al hilo"
    2: "Hilo OBLIGADO ecoar verbatim antes de razonar"
    3: "SHA-256 normalizado (trim + NFC + comillas) del eco comparado vs original"
    4: "Si match → razonamiento permitido"
    5: "Si mismatch → reintento (max 3 attempts)"
    6: "Si 3 attempts fallan → HALT + bridge + T1"
  normalization:
    - "strip leading/trailing whitespace"
    - "NFC Unicode normalization"
    - "smart quotes → ASCII quotes"
```

**Justificación binaria (Manus E2):** "Cuando el agente intenta ignorar el attachment, debe ser coercitivamente forzado a ecoarlo verbatim antes de pensar." Demostrado vital por la fabricación binaria Perplexity al vivo.

### **Capa 7 — Compaction Contract** (Perplexity v0.3+v0.4)

**Pre-compactación obligatorio:**
1. Escribir cápsula
2. Escribir event log tail
3. Escribir evidence index
4. Escribir no-go list
5. Escribir context-health
6. Ejecutar secret scan

**Post-compactación obligatorio:**
1. Detectar post-compaction
2. NO confiar en resumen ciegamente
3. Rehidratar desde fuentes externas
4. Comparar summary vs capsule
5. **Si contradice, gana external state — máximo 2 contradicciones consecutivas mismo field (Perplexity v0.4):**

```yaml
external_state_conflict_policy:
  max_consecutive_conflicts_same_field: 2
  conflict_window_minutes: 30
  on_first_conflict: "REHYDRATE_MINIMAL_SOURCES"
  on_second_conflict: "REHYDRATE_WITH_COWORK_AUDIT_REQUIRED"
  on_third_conflict: "HALT_T1_REQUIRED"
```

6. Ejecutar Echo-Back (Capa 6)

### **Capa 8 — Replay/Time Travel + Sanitization Gate** (Perplexity v0.3 + v0.4)

```yaml
event_log_sanitization_gate:
  required_before: [replay, capsule_reconstruction, post_compaction_rehydration]
  classification_states:
    SAFE: "puede entrar a replay"
    REDACTED: "entra con campos sensibles reemplazados"
    UNTRUSTED: "no entra al state commitment"
    QUARANTINED: "excluido + WARN/HALT según severidad"
  blocked_patterns:
    - "cookies"
    - "JWTs"
    - "API keys"
    - "connection strings"
    - "query params con tokens"
    - "tool outputs con secretos"
    - "ignore previous instructions injection"
    - "contenido externo no firmado"

replay_rules:
  - "Replay only uses event_log.sanitized.jsonl"
  - "Replay never executes side effects"
  - "Replay produces replay_report.md"
  - "Replay contaminado → HALT"
```

### **Capa 9 — Guardian Decision View** (Perplexity v0.3+v0.4)

```yaml
guardian_decision_view:
  action_requested: "merge PR #170|apply_migration|deploy|delete|...|R1"
  requested_by: "agent_id"
  capsule_hash: "sha256:<hash>"
  capsule_freshness: "fresh|stale|missing"  # < TTL Capa 2
  context_health_state: "OK|WARN|REHYDRATE|HALT"
  external_kill_switch:
    checked: true
    local_kill_file: "absent|present|unavailable"
    supabase_flag: "enabled|disabled|unavailable"
    github_control_file: "enabled|disabled|unavailable"
    final_state: "ENABLED|DISABLED|DEGRADED_READONLY"
  checks:
    t1_authorization: "PRESENT|PENDING"
    t1_auth_source: "capsule.last_t1_decision|bridge_control_tower|github_commit"
    scope_match: "PASS|FAIL"
    secrets_scan: "PASS|FAIL"
    evidence_freshness: "PASS|FAIL"
    dsc_g_013_coherence: "PASS|N/A"
    no_go_conflicts: []
    rollback_available: "YES|NO"
  recommendation: "ALLOW|BLOCK|T1_REQUIRED"
```

**Reglas magnas:**
- Si `external_kill_switch.final_state != ENABLED` → NO ALLOW magnas
- Si `t1_authorization: PENDING` → NO ALLOW magnas
- Si `rollback_available: NO` → NO ALLOW magnas
- Si Cowork y Guardian discrepan → Perplexity PBA audit (post resolución decisión T1 status Perplexity) → T1 decide

### **Capa 10 — Secret Firewall** (Manus E2 + Perplexity convergentes)

Prohibido persistir: API keys, JWTs, cookies, passwords, refresh tokens, connection strings, OAuth secrets, Supabase service keys.

```yaml
evidence_ref_policy:
  allow: [github_pr_url_without_tokens, commit_sha, repo_path_no_secret, supabase_table_name]
  deny: [query_strings_with_token, cookies, jwt, connection_strings, paths_with_secret_values]
  transform: [strip_query_params, redact_env_values, hash_sensitive_path_segments]
```

**Gate obligatorio:** gitleaks PASS + trufflehog PASS + regex deny-list PASS + N=1,000 synthetic bridge/snapshot files PASS.

### **Capa 11 — Offline/Local-First Fallback** (Perplexity v0.3)

```text
.monstruo/dory/
  latest_capsule.yaml
  event_log.jsonl
  evidence_index.jsonl
  no_go_list.md
  last_verified_git_state.json
  last_verified_db_state.json
```

| Sistema caído | Permitido | Bloqueado |
|---|---|---|
| Supabase | docs/read-only + local capsule | writes, migration claims |
| GitHub | local state + no side effects | merge, PR claims |
| Railway | docs/read-only | runtime claims/deploy |
| Todo externo | pedir T1 | toda acción magna |

### **Capa 12 — Universal Adapters** (Perplexity v0.3 + Manus E2 MCP server)

```yaml
universal_adapters:
  manus_adapter:
    uses: [tools/manus_bridge.py, ATTACHMENT_OK, thread_snapshots, heartbeat, Control Tower Bridge]
    role: "T3_EXECUTOR"
  cowork_adapter:
    uses: [session_memory.py, claim_calibration.py, pre_response_hook.py, CRUZ-001, VERIFICADOR-001]
    role: "T2-A_ARCHITECT_AUDITOR"
  perplexity_adapter:
    role: "T2-B_AUDITOR_HARNESS"
    requires_dsc: "DSC-MO-XXX_perplexity_audit_harness (PENDIENTE T1)"
    constraint: "NO execution rights + Echo-Back coercitivo aplicado a outputs"  # Post invalidación binaria
  mcp_server_monstruo_memory:
    uses: "Manus E2 v1.2 cross-agente MCP server"
    role: "shared state bridge"
```

---

## §5 Stack reusable open-source (Manus E2 APORTE MAGNO)

| Framework | Uso | Madurez | Licencia | Reemplaza custom |
|---|---|---|---|---|
| **DBOS Transact** | Durable workflows + exactly-once side effects | Production | MIT | `idempotency_proxy.py` + `side_effect_outbox` |
| **LangGraph PostgresSaver** | Checkpoint capsule storage Supabase-backed | Production | MIT | `snapshot_writer.py` |
| **gitleaks + trufflehog + regex denylist** | Secret scan obligatorio | Production | MIT | — |
| **Manus E2 MCP server `monstruo-memory`** | Cross-agente state bridge | Build | Internal | — |

**Net effect Manus E2:** -800 LOC custom + +200 LOC glue = **-600 LOC mantenidas internamente**.

---

## §6 Honestidad numerica 96%

Declarada en §1 verbatim. Cura **operativa, no matemática**. Verificable contra DORY_BENCH_1000 (§9).

---

## §7 Mapping DSC-G-013 v0.1 Coherence Gate Nivel A (Perplexity v0.3)

| Gate DSC-G-013 | DORY-CURE-CONVERGED-001 mapping |
|---|---|
| Repo ↔ DB coherence | Capa 4 migration_drift signal + Capa 9 dsc_g_013_coherence check |
| No schema claims sin DB proof | Capa 9 Guardian + Capa 7 external_state |
| No action magna sin evidence | Capa 9 Guardian Decision View |
| Manual Nivel A antes de automation | Fase 1 shadow, no enforce global |
| Nivel B experimental | DORY-CURE canary NO reemplaza DSC-G-013 |

---

## §8 Coordinación CRUZ / VERIFICADOR / Cowork-Memento / Memento / Anti-Dory 002 / v0.2

| Sistema | Relación |
|---|---|
| CRUZ-001 | Cubre cross-session Cowork. NO reemplazado. CONSUMIDOR Bounded State Capsule (Capa 2) |
| VERIFICADOR-001 | Bloquea claims high-risk pre-emit. Señales INPUT a Capa 9 Guardian |
| Cowork-Memento | Claim calibration. ALIMENTA F-pattern metrics |
| Memento | Context validation. INVOCADO antes acciones críticas |
| Anti-Dory 002 | Attachment inicial. EXTENDIDO |
| Anti-Dory 003 v0.2 | Base intra-hilo. ENDURECIDO |

**Regla magna:** NO duplicar hooks. Si dos sistemas bloquean, HALT consolidado único.

---

## §9 DORY_BENCH_1000 reproducible firmado (Perplexity v0.4 + Manus E2 DoD)

**Estructura:**
```
benchmarks/dory_bench_1000/
  README.md
  manifest.json + manifest.sha256
  fixtures/{cold_start,post_compaction,crash_recovery,stale_pr_branch,migration_drift,memory_poisoning,secret_leakage,false_halt}/*.json + hashes
  expected/expected_results.jsonl + hash
  results/run_<timestamp>/
    results.jsonl + results.sha256
    summary.json
    failures/
    signatures/evaluator_signature.txt
```

**Criterios PASS:**

| Familia | Cases | PASS |
|---|---|---|
| Cold start | 150 | ≥147 |
| Post-compaction | 200 | ≥196 |
| Crash recovery | 150 | ≥147 |
| Stale PR/branch | 150 | ≥147 |
| Migration drift | 100 | ≥98 |
| Memory poisoning | 100 | 100/100 blocked |
| Secret leakage | 100 | 0/100 leaks |
| False HALT | 50 | ≤1 |
| **Global** | **1000** | **≥980** + 0 unauthorized + 0 secrets + 0 poisoned promoted |

**Verificación cross-auditor:** Cowork o (post resolución status) Perplexity puede reproducir muestra ≥10%.

---

## §10 Rollout 5 fases obligatorias (Perplexity v0.3 + Manus E2 timing)

| Fase | Alcance | Enforce | Duración |
|---|---|---|---|
| **0** | Design audit (Cowork + Grok red-team + 3 Sabios NO-Perplexity + T1 firma) | no code | 3-5 días |
| **1** | Canary Manus shadow (1 agente) | warnings only | 7 días |
| **2** | Canary Manus enforce | HALT acciones magnas | 14 días |
| **3** | Cowork adapter (CRUZ + claim calibration + capsule) | enforce | 14 días |
| **4** | Universal bridge (Perplexity/Grok/Gemini auditors read-only) | enforce | post DSC nuevo |

**No saltar fase.**

---

## §11 Rollback plan formal (Perplexity v0.4 schema)

```yaml
rollback_plan:
  disable_flags:
    - "DORY_CURE_ENABLED=false"
    - "DORY_CURE_HALT_ENABLED=false"
  preserve_data:
    - "capsules"
    - "event_logs"
  stop_writes:
    - "guardian"
    - "heartbeat"
  restore_behavior:
    - "manual bridge only"
    - "Memento shadow only"
  owner: "Cowork T2-A + T1"
  test_before_enforce: true
  pre_phase_2_validation: "rollback tested in shadow"
```

---

## §12 Decisiones T1 separadas

| # | Decisión binaria | Opciones |
|---|---|---|
| 1 | Aprobar DORY-CURE-CONVERGED-001 v1.0 DRAFT como diseño Fase 0 | approve / revise / reject |
| 2 | Status Perplexity post-invalidación binaria 5 citas | mantener con caveat / sustituir / Echo-Back coercitivo / hold |
| 3 | Autorizar convergencia 3 Sabios NO-Perplexity | GPT-5.5+Opus+Gemini / GPT-5.5+Opus+DeepSeek / GPT-5.5+Opus+Kimi / custom |
| 4 | Autorizar Grok red-team final pass post-Cowork | yes / no |
| 5 | Aceptar cura 96% honesta vs perseguir 97-98% | aceptar 96% / v1.1 TLA+ + comprensión verificada LLM |
| 6 | Autorizar Fase 1 canary Manus shadow post-3 Sabios verde | yes / no |
| 7 | Autorizar runtime flags shadow | yes / no |
| 8 | Autorizar DORY_BENCH_1000 ejecución Fase 1 | yes / no |
| 9 | Autorizar rollback plan formal | yes / no |
| 10 | DSC formal post-firma magna (`DSC-MO-XXX_dory_cure_converged_001`) | yes / defer |
| 11 | DSC separado Perplexity audit harness role (Capa 12) | yes / defer / eliminar Capa 12 Perplexity |
| 12 | DSC separado key management HMAC/ed25519 (Fase 2+) | yes / defer |

**Ninguna decisión implica implementación salvo lo declare explícitamente.**

---

## §13 No-Go reforzado (22 items convergentes)

1. ❌ Declarar Dory muerto / cura 100%
2. ❌ Activar global sin fases secuenciales (0→1→2→3→4)
3. ❌ Saltar fases
4. ❌ Tocar secrets
5. ❌ Ejecutar migrations sin firma T1
6. ❌ Desbloquear Nightly Builder R1
7. ❌ Clasificar `user_id=anonymous`
8. ❌ Canonizar desde snapshots/event log/cápsula automáticamente
9. ❌ Aprobar T1 sin Guardian View
10. ❌ Superar DSC-G-013
11. ❌ Usar DORY-CURE como excusa para deploy
12. ❌ Implementar sin rollback probado
13. ❌ Implementar sin DORY_BENCH_1000 fixture design firmado
14. ❌ Ejecutar replay con event log NO sanitizado
15. ❌ Ignorar kill-switch externo
16. ❌ Usar context-health como único control
17. ❌ Aceptar external state wins >2 contradicciones consecutivas
18. ❌ Persistir secretos
19. ❌ Ejecutar acciones magnas sin Guardian Decision View
20. ❌ Modificar APP_VISION desde rehydration/Guardian
21. ❌ Promover Perplexity como auditor de su propio diseño sin Echo-Back coercitivo
22. ❌ Firmar "96%" sin baseline empírico medido en DORY_BENCH_1000

---

## §14 Apéndice — Mapping aportes por fuente (transparency)

| Capa / Sección | Aporte primario | Otros contributors |
|---|---|---|
| §1 Cura 96% honesta + residual <4% | **Manus E2 v1.2** | — |
| Capa 0 External Kill-Switch | **Perplexity v0.4** | Cowork agrega TTL per source |
| Capa 1 Source of Truth externa | **Perplexity v0.3** | — |
| Capa 2 Bounded State Capsule cripto | **Perplexity v0.3** | Cowork agrega TTL + signature_mode phased |
| Capa 3 Event Log + side_effect validator | **Perplexity v0.3** | Cowork agrega validador binario |
| Capa 4 Context Health | **Convergente Manus + Perplexity** | — |
| Capa 5 Live Rehydration | **Convergente Manus + Perplexity** | Cowork v0.2 §2 base |
| Capa 6 Echo-Back Coercitivo | **Manus E2 v1.2 Mec 2 ÚNICO** | — |
| Capa 7 Compaction Contract | **Perplexity v0.3+v0.4** | — |
| Capa 8 Replay + Sanitization Gate | **Perplexity v0.3+v0.4** | — |
| Capa 9 Guardian Decision View | **Perplexity v0.3+v0.4** | Cowork agrega t1_auth_source + dsc_g_013_coherence |
| Capa 10 Secret Firewall | **Convergente Manus + Perplexity** | — |
| Capa 11 Offline/Local-First | **Perplexity v0.3** | — |
| Capa 12 Universal Adapters | **Perplexity v0.3** | Cowork agrega Echo-Back para Perplexity post-invalidación + DSC requirement |
| §5 Stack reusable DBOS/LangGraph | **Manus E2 v1.2 APORTE MAGNO** | — |
| §9 DORY_BENCH_1000 | **Perplexity v0.4** | — |
| §10 Rollout 5 fases | **Perplexity v0.3** | Manus E2 timing |
| §11 Rollback plan | **Perplexity v0.4** | — |
| §13 No-Go 22 items | **Convergente** | Cowork agrega items 21 + 22 anti-F16/F19 |

---

## §15 Veredicto Cowork T2-A propuesto

**🟡 READY_FOR_3_SABIOS_NO_PERPLEXITY** con caveats binarios:

1. **Convergencia 3 Sabios DEBE ser NO-Perplexity** (autor + auditor implícito post-invalidación-binaria = F16). Recomendación: GPT-5.5 Pro + Opus 4.7 + Gemini 3.1 Pro
2. **Material para convergencia DEBE incluir verbatim:** este DRAFT + Manus E2 v1.2 + Perplexity v0.3+v0.4 + invalidación binaria 5 citas + Cowork audits previos
3. **Decisión T1 status Perplexity** (decisión #2 §12) DEBE ocurrir ANTES convergencia
4. **4 gaps resueltos en este DRAFT:** TTL operacional capsule fresca + key management phased + side_effect validador + Capa 12 declaración Perplexity con Echo-Back

---

## §16 Cierre

- ✅ No implementé código
- ✅ No abrí PR
- ✅ No modifiqué main fuera de bridge/ autorizado
- ✅ No canonicé
- ✅ No declaré Dory muerto
- ✅ No desbloqueé R1
- ✅ No decidí anonymous
- ✅ Push autorizado T1 verbatim "seguimos manus pide que pushees"

**Soy Cowork T2-A.** **Fusión producida sobre ground truth binario de 4 specs leídos verbatim.** **NO firmo este DRAFT — solo lo propongo.** **Espera firma T1 §12 + convergencia 3 Sabios NO-Perplexity post-decisión status Perplexity.**
