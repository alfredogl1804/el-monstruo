# DORY-CURE-001 v0.3 DRAFT — Cura 98% del Síndrome Dory

**Estado:** DRAFT de diseño, no canon, no implementación  
**Autor:** Perplexity My Computer, Torre de Control PBA / Auditor Externo / Perito 95 / QA Multiagente  
**Fecha:** 2026-05-19  
**Autorización T1:** Alfredo autorizó únicamente producir v0.3 DRAFT. No autorizó implementación, runtime flags, canary, canonización, declaración “Dory muerto” ni cambios en `main`.  

## Control de alcance

Este documento consolida:

1. Los 9 cambios obligatorios del red-team SuperGrok.
2. Los 7 cambios obligatorios de Cowork T2-A.
3. La coordinación explícita con `MANUS-ANTI-DORY-003 v0.2`.
4. No-Go list reforzada.
5. Decisiones T1 separadas.
6. Rollback plan.
7. Mapping DSC-G-013.
8. Coordinación CRUZ/VERIFICADOR.

Este documento **no** implementa código, no modifica repositorio, no activa runtime y no declara éxito.

---

## Veredicto de diseño

El Síndrome Dory no se cura con memoria larga, resúmenes, snapshots aislados ni bridge manual. La cura 98% requiere un sistema de continuidad externo, verificable y acotado:

> **Bounded State Capsule + Event Log + Live Rehydration + Context Health + Compaction Contract + Replay + Guardian + Secret Firewall + Rollback + Benchmarks.**

La cura se considera lograda solo si supera un benchmark de recuperación de contexto con **≥98% de éxito**, **0 secretos filtrados**, **0 acciones magnas no autorizadas** y **0 promoción automática de memoria contaminada**.

---

## Relación con MANUS-ANTI-DORY-003 v0.2

`DORY-CURE-001 v0.3` no reemplaza `MANUS-ANTI-DORY-003 v0.2`. Lo convierte en una arquitectura más completa.

| Elemento | MANUS-ANTI-DORY-003 v0.2 | DORY-CURE-001 v0.3 |
|---|---|---|
| Núcleo intra-hilo | Pre-flight cada N turnos / X minutos | Conservado |
| Snapshot intra-hilo | YAML tipado | Formalizado como Bounded State Capsule |
| Context-health | 8 señales + umbrales | Conservado + firmado/hash + loop control |
| Live rehydration | Sí | Conservado + fallback offline/local-first |
| Compaction/replay | Sí, inicial | Fortalecido con event log, replay read-only y benchmark |
| Secret hygiene | Sí | Fortalecido con sanitizer de `evidence_ref` |
| Rollout | 4 fases | Convertido en obligatorio |
| Guardian | Implícito / parcial | Formalizado con Guardian T1-check verificable |

**Regla:** Si hay conflicto entre v0.2 y v0.3, v0.3 debe citar el conflicto y pedir decisión T1; no puede sobrescribir v0.2 automáticamente.

---

## Problema cubierto

El Síndrome Dory se divide en cinco vectores:

| Vector | Descripción | Cubierto por |
|---|---|---|
| D1 Cold start | Hilo nuevo nace sin contexto | Anti-Dory 002 + DORY-CURE |
| D2 Compaction loss | Compactación pierde detalles críticos | DORY-CURE |
| D3 Intra-thread drift | Mismo hilo se degrada durante horas | Anti-Dory 003 + DORY-CURE |
| D4 Evidence drift | PR/branch/migration/runtime cambia sin que el hilo lo detecte | Memento + DORY-CURE |
| D5 Poison/secrets | Se persiste basura, instrucciones o secretos | Memento + Secret Firewall |

---

## Arquitectura v0.3

### Capa A — Bounded State Capsule

Cada hilo vivo mantiene una cápsula compacta, tipada, verificable y firmada.

```yaml
bounded_state_capsule:
  schema_version: "1.0"
  capsule_id: "uuid"
  parent_capsule_id: "uuid|null"
  agent:
    agent_id: "manus_e2"
    role: "T3_EXECUTOR"
    platform: "manus"
  scope:
    project_id: "el-monstruo"
    front_id: "la-forja-d6"
    active_sprint: "D6-CREDITS-RESTORE-001"
    active_branch: "fix/d6-credits-restore-circuit-breaker"
    active_prs:
      - pr: 170
        role: "D6 circuit breaker"
        base_sha: "<sha>"
        head_sha: "<sha>"
        state: "open_unstable"
  objective:
    current_objective: "Prepare PR #170 for Cowork reclassification"
    next_allowed_action: "Collect logs and update evidence only"
    prohibited_actions:
      - "merge"
      - "apply_migration"
      - "deploy"
      - "touch_secrets"
  governance:
    last_t1_decision: "No merge without explicit T1"
    no_go_refs:
      - "No Nightly Builder R1"
      - "No anonymous decision"
      - "No Dory muerto declaration"
  evidence:
    evidence_refs:
      - type: "github_pr"
        ref: "https://github.com/alfredogl1804/el-monstruo/pull/170"
      - type: "bridge"
        ref: "bridge/control_tower/2026-05-19/manus_e2/..."
  health:
    context_health_score: 2
    context_health_state: "OK"
    last_rehydrated_at: "2026-05-19T06:00:00Z"
    rehydration_count_session: 0
  integrity:
    capsule_hash: "sha256:<hash>"
    parent_capsule_hash: "sha256:<hash|null>"
    event_log_tail_hash: "sha256:<hash>"
    evidence_index_hash: "sha256:<hash>"
    signature_mode: "hmac_or_ed25519"
    signer: "system|cowork|manus|perplexity"
    signed_at: "iso_timestamp"
```

### Reglas de cápsula

- Si `capsule_hash` no valida → **HALT**.
- Si `parent_capsule_hash` rompe cadena → **REHYDRATE una vez**; si persiste → **HALT**.
- Si acción magna no tiene cápsula firmada y fresca → **HALT**.
- Si evidencia citada no existe o no se puede verificar → downgrade a `DRAFT_PENDING_VERIFICATION`.

---

### Capa B — Event Log append-only

Todo evento relevante se guarda fuera del transcript.

```json
{
  "schema_version": "1.0",
  "event_id": "uuid",
  "agent_id": "manus_e2",
  "project_id": "el-monstruo",
  "front_id": "la-forja-d6",
  "event_type": "pr_status_checked",
  "evidence_ref": "github_pr:170",
  "result_hash": "sha256:<hash>",
  "created_at": "iso_timestamp",
  "side_effect": false
}
```

Reglas:

- Event log es append-only.
- Replay es read-only.
- Side effects nunca se repiten desde replay.
- Eventos con evidencia no verificable no pueden promoverse a estado persistente.

---

### Capa C — Context Health Score

| Señal | Peso |
|---|---:|
| Branch declarado ≠ branch real | 2 |
| PR base SHA obsoleto | 2 |
| Migration repo ≠ Supabase | 3 |
| Scope bleed | 3 |
| Repite error ya corregido | 2 |
| Cita DSC/F# inexistente | 3 |
| Turnos sin rehidratación > N | 1 |
| Compactación detectada | 4 |
| Acción magna sin preflight | 5 |
| Hash capsule inválido | 10 |
| Kill-switch remoto ON | 10 |

| Score | Estado | Acción |
|---:|---|---|
| 0–2 | OK | continuar |
| 3–5 | WARN | verificar antes de acción magna |
| 6–9 | REHYDRATE | rehidratación obligatoria antes de output operativo |
| ≥10 | HALT | detener, emitir bridge, pedir T1/Cowork |

### Loop control

```yaml
rehydration_loop_policy:
  max_attempts_per_30min: 3
  same_cause_repeats: "HALT"
  new_cause_each_time: "ESCALATE_COWORK"
  external_state_unavailable: "DEGRADED_READONLY"
```

Si `External state wins` produce contradicción repetida:

1. intento normal;
2. intento con fuentes mínimas;
3. **HALT + bridge report + T1**.

---

### Capa D — Live Rehydration

La rehidratación se dispara:

- al detectar compactación;
- cada N turnos;
- cada X minutos;
- antes de acción magna;
- con palabra T1 “rehidrátate”;
- si context-health ≥6;
- al retomar tras pausa;
- al crear hilo nuevo desde `agent_id` + `front_id`.

Lecturas permitidas:

- cápsula actual;
- event log;
- GitHub PR/branch/commit/checks;
- Supabase heads/snapshots/migrations;
- bridge propio;
- no-go list;
- docs canon (`CLAUDE.md`, `AGENTS.md`, `_INDEX.md`, DSCs).

Prohibido leer/persistir:

- secretos;
- cookies/JWTs;
- valores de env vars;
- Bridge de otros agentes sin cross-validation;
- documentos históricos con credenciales sin sanitizer.

---

### Capa E — Compaction Contract

Antes de compactación:

1. escribir cápsula;
2. escribir event log tail;
3. escribir evidence index;
4. escribir no-go list;
5. escribir context-health;
6. ejecutar secret scan.

Después de compactación:

1. detectar post-compaction;
2. no confiar ciegamente en el resumen;
3. rehidratar desde fuentes externas;
4. comparar summary vs capsule;
5. si contradice, gana external state;
6. si contradicción se repite 3 veces → HALT.

---

### Capa F — Replay / Time Travel

Replay reconstruye estado, no ejecuta.

Fuentes:

- último accepted capsule;
- eventos posteriores;
- GitHub/Supabase fresh state;
- bridge propio.

Reglas:

- Replay es read-only.
- Replay nunca ejecuta tool calls con side effects.
- Replay debe producir `replay_report.md`.
- Replay contaminado → HALT.

---

### Capa G — Guardian T1-check verificable

Toda acción magna requiere:

```yaml
guardian_decision_view:
  action_requested: "merge PR #170"
  requested_by: "manus_e2"
  capsule_hash: "sha256:<hash>"
  context_health_state: "OK"
  checks:
    t1_authorization: "PENDING|PRESENT"
    scope_match: "PASS|FAIL"
    secrets_scan: "PASS|FAIL"
    evidence_freshness: "PASS|FAIL"
    no_go_conflicts: []
    rollback_available: "YES|NO"
  recommendation: "ALLOW|BLOCK|T1_REQUIRED"
```

Reglas:

- T1 approval sin Guardian View = no informado.
- Guardian View debe ser auditable por Cowork y Perplexity.
- Si Cowork y Guardian discrepan, Perplexity PBA emite audit; T1 decide.
- Si rollback no existe, acción magna no procede.

---

### Capa H — Secret Firewall

Prohibido persistir:

- API keys;
- JWTs;
- cookies;
- passwords;
- refresh tokens;
- connection strings;
- OAuth secrets;
- Supabase service keys.

`evidence_ref` se sanitiza:

```yaml
evidence_ref_policy:
  allow:
    - "github_pr_url_without_tokens"
    - "commit_sha"
    - "repo_path_without_secret_values"
    - "supabase_table_name"
  deny:
    - "query_strings_with_token"
    - "cookies"
    - "jwt"
    - "connection_strings"
    - "paths_containing_secret_values"
  transform:
    - "strip_query_params"
    - "redact_env_values"
    - "hash_sensitive_path_segments"
```

Gate:

- gitleaks PASS;
- trufflehog PASS;
- regex deny-list PASS;
- no secrets in 1,000 synthetic bridge/snapshot files.

---

### Capa I — Offline / local-first fallback

Para evitar Supabase/GitHub/Railway como SPOF:

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

---

## Mapping DSC-G-013

DORY-CURE-001 respeta DSC-G-013 así:

| DSC-G-013 Gate | DORY-CURE mapping |
|---|---|
| Repo ↔ DB coherence | Migration drift signal + pre-action check |
| No schema claims sin DB proof | Supabase migration check required |
| No action magna sin evidence | Guardian Decision View |
| Manual Level A antes de automation | Fase 1 shadow, no enforce global |
| Nivel B experimental | DORY-CURE canary no reemplaza DSC-G-013 |

No se permite que DORY-CURE declare DB/schema reality sin query fresh o cached verified state dentro de TTL.

---

## Coordinación CRUZ / VERIFICADOR

| Sistema | Relación |
|---|---|
| CRUZ-001 | Cubre cross-session Cowork; DORY-CURE no lo reemplaza |
| VERIFICADOR-001 | Bloquea claims high-risk pre-emit; DORY-CURE usa sus señales como input |
| Cowork-Memento | Claim calibration; alimenta benchmark y F-pattern metrics |
| Memento | Context validation; DORY-CURE lo invoca antes de acciones críticas |
| Anti-Dory 002 | Attachment inicial; DORY-CURE lo extiende |
| Anti-Dory 003 v0.2 | Base intra-hilo; DORY-CURE lo endurece |

Regla: no duplicar hooks. Si dos sistemas bloquean, se emite un solo HALT consolidado.

---

## Benchmark DORY_BENCH_1000

| Familia | Casos | PASS |
|---|---:|---|
| Cold start | 150 | ≥147 |
| Post-compaction | 200 | ≥196 |
| Crash recovery | 150 | ≥147 |
| Stale branch/PR | 150 | ≥147 |
| Migration/schema drift | 100 | ≥98 |
| Memory poisoning | 100 | 100 blocked |
| Secret leakage | 100 | 0 leaks |
| False HALT | 50 | ≤1 false halt |

Global PASS:

- ≥980/1000 recovery/detection success;
- 0 unauthorized side effects;
- 0 secrets;
- 0 poisoned memory promoted.

---

## Rollout obligatorio

| Fase | Alcance | Enforce |
|---|---|---|
| 0 | Design audit | no code |
| 1 | Manus shadow | warnings only |
| 2 | Manus enforce | HALT en acciones magnas |
| 3 | Cowork adapter | claim/capsule integration |
| 4 | Universal bridge | auditors read-only |

No se puede saltar fase.

---

## Rollback plan

Cada fase debe tener:

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
```

Rollback debe ser probado antes de enforce.

---

## Decisiones T1 separadas

| # | Decisión | Opciones |
|---|---|---|
| 1 | Aprobar DORY-CURE-001 v0.3 como diseño para auditoría | approve / revise / reject |
| 2 | Autorizar red-team final Cowork+Grok | yes / no |
| 3 | Autorizar Fase 1 shadow Manus | yes / no |
| 4 | Autorizar runtime flags shadow | yes / no |
| 5 | Autorizar benchmark DORY_BENCH_1000 | yes / no |
| 6 | Autorizar rollback plan formal | yes / no |

Ninguna decisión implica implementación salvo que lo diga explícitamente.

---

## No-Go reforzado

No se permite:

1. declarar Dory muerto;
2. activar global;
3. saltar fases;
4. tocar secrets;
5. ejecutar migrations;
6. desbloquear Nightly Builder R1;
7. clasificar `anonymous`;
8. canonizar desde snapshots;
9. aprobar T1 sin Guardian View;
10. superar DSC-G-013;
11. usar DORY-CURE como excusa para deploy;
12. implementar sin rollback.

---

## Veredicto v0.3

Esta versión queda lista para:

- Cowork forensic audit;
- SuperGrok red-team second pass;
- Perplexity PBA synthesis.

No está lista para:

- implementación;
- runtime flags;
- canary;
- canonización;
- declaración de victoria.

