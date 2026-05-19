# DORY-CURE-CONVERGED-001 v1.1 RESHAPED — Post-Grok FAILS_RED_TEAM redesign

> **Tipo:** DRAFT propositivo Cowork T2-A v1.1 — redesign post-red-team Grok
> **Estado:** NO canon. NO implementación. NO firmado T1. Depositado bajo autorización T1 verbatim "opción A" 2026-05-19.
> **Predecesor:** v1.0 DRAFT (commit `efbe6a32`) RECHAZADO por Grok red-team `FAILS_RED_TEAM`.
> **Veredicto Grok evidence_pack:** `bridge/control_tower/2026-05-19/grok/2026-05-19_grok_red_team_dory_cure_converged_001_v1_0_FAILS.md`
> **Caveat magno:** v1.1 RESHAPED integra los 8 vectores adversariales + 4 SPOF + 4 asunciones + 4 edge cases de Grok como changes obligatorios. Reconocimiento F16 Cowork T2-A explicito (autor + auditor mismo de v1.0).

---

## §0 Identidad y rol

- **T1 = Alfredo** (único firmante magno)
- **T2-A Cowork** = arquitecto redesign (autor v1.1 RESHAPED post-Grok)
- **T3 ejecutores** = Manus E1/E2/Catastro (target Fase 1 EXPERIMENTO T+14D post-3 Sabios convergencia verde)
- **Auditor adversarial Grok 4 Heavy** = red-team detectó fallo magno v1.0 + emitió recomendación redesign
- **Out-of-scope absoluto:** Nightly Builder R1, anonymous classification, APP_VISION write

---

## §1 Reconocimiento F16 Cowork T2-A explicito

v1.0 tenía SPOF #1 Grok-detectado: "Cowork T2-A como único compositor de la fusión". F16 explicito (auto-confirmación hipótesis sin red-team independiente). Sin Grok, T1 habría avanzado a 3 Sabios con composición vulnerable.

**Anti-Dory aplicado a Cowork mismo funcionó vía red-team externo Grok.** Esto valida el proceso PBA. v1.1 RESHAPED integra el aprendizaje.

---

## §2 Veredicto + cura 96% honesta + residual <4% (mantenido de v1.0)

> "En **≥96% de escenarios de prueba realistas**, un hilo que compacte, se degrade, muera o sea reemplazado puede recuperar estado operativo suficiente para continuar sin reexplicación humana, sin inventar, sin violar no-go list y sin filtrar secretos."

Residual <4% mantenido. Cura **operativa, no matemática**. Validable contra DORY_BENCH_1000 firmado + ADVERSARIAL BENCHMARK EXTERNO (Capa 13 nueva post-Grok).

---

## §3 Cambios binarios v1.0 → v1.1 RESHAPED

### REMOVIDO

| Componente v1.0 | Razón removal | Severidad Grok |
|---|---|---|
| **Capa 12 Perplexity Adapter con Echo-Back** | Confianza circular post-fabricación 5 citas | CRÍTICA (fallo magno Grok) |
| **Echo-Back como ÚNICA defensa anti-alucinación post-rehydration** | Asunción no validada LLM post-2026 respetará | ALTA |
| **Asunción "LLM respetará Echo-Back post-2026"** | Sin evidencia, precedente contrario | CRÍTICA |

### REEMPLAZADO

| v1.0 | v1.1 RESHAPED | Justificación |
|---|---|---|
| Capa 12 Perplexity Adapter | **Capa 12 NUEVA: VERIFICADOR-001 determinístico (PRIMARY anti-alucinación)** | Determinístico vs LLM-based; sin Perplexity dependency |
| Echo-Back primary anti-alucinación | Echo-Back DEFENSE-IN-DEPTH secondary | VERIFICADOR primary; Echo-Back secondary defense |
| Evidence_ref check existencia | + **CONTENIDO verification obligatorio** | Anti-vector #1 Grok (capsule poisoning fake ref) |
| Sanitization gate regex only | + **LLM-based semantic scanner + regex** | Anti-vector #7 Grok (JSON injection evasion) |
| Policy 2 contradicciones consecutivas | + **policy ventana cíclica adicional** | Anti-vector #6 Grok (bug temporal cicla) |

### AGREGADO (8 changes obligatorios anti-Grok)

| # | Change | Anti-vector Grok | Capa nueva/extendida |
|---|---|---|---|
| 1 | **Quorum estricto External Kill-Switch (≥2/3 sources concuerdan)** | #5 race condition | Capa 0 extendida |
| 2 | **Adversarial benchmark externo cross-suite** (no solo DORY_BENCH_1000 sintético) | #4 Goodhart's law | Capa 13 nueva |
| 3 | **Parser data-only obligatorio para bridge files** | #2 prompt injection bridge | Capa 5 extendida |
| 4 | **Canary rollback path a Anti-Dory 003 v0.2 sola si DBOS/LangGraph fail** | #8 upstream bug | Capa 11 extendida |
| 5 | **Red-team adversarial OBLIGATORIO pre-convergencia 3 Sabios** | SPOF #1 Cowork compositor único | §10 Roadmap Fase 0 extendida |
| 6 | **Cross-agente fixtures DORY_BENCH** (Manus→Cowork→Perplexity flow) | Goodhart's law + fixtures faltantes | Capa 9 DORY_BENCH_1000 extendida |
| 7 | **Latencia P99 + race conditions multi-source + LLM-bypass fixtures** | Goodhart fixtures faltantes | Capa 9 DORY_BENCH_1000 extendida |
| 8 | **Policy contradicciones cíclicas (ventana temporal + cíclico, no solo consecutivas)** | #6 external state cicla | Capa 7 Compaction Contract extendida |

### MANTENIDO

- Cura 96% honesta + residual <4% desglosado
- Bounded State Capsule cripto (Perplexity Capa 2)
- External Kill-Switch (Perplexity Capa 0) + nuevo quorum
- DBOS Transact + LangGraph PostgresSaver (Manus E2 stack) + nuevo canary rollback path
- DORY_BENCH_1000 (Perplexity Capa 9) + nuevas fixtures Grok-driven
- Triple replicación (Manus E2)
- Coordinación CRUZ/VERIFICADOR/Memento/Anti-Dory 002/v0.2
- Mapping DSC-G-013 v0.1
- Rollout 5 fases secuenciales
- Rollback plan formal
- Anti-Dory 003 v0.2 base intra-hilo

---

## §4 Arquitectura v1.1 — 13 capas (12 reshape + 1 nueva Capa 13)

### Capa 0 — External Kill-Switch + QUORUM ESTRICTO (anti-Grok #5)

```yaml
external_kill_switch_layer:
  name: "DORY_CURE_EXTERNAL_KILL_SWITCH"
  independence_requirement: "MUST_NOT_DEPEND_ON_CONTEXT_HEALTH"
  sources_order:
    - "local_kill_file: .monstruo/kill_switches/DORY_CURE_DISABLED"
    - "supabase_runtime_flag: anti_dory_runtime_flags.dory_cure_enabled"
    - "github_control_file: bridge/control_tower/runtime_flags/DORY_CURE_STATUS.md"
  quorum_policy:  # ← NUEVO v1.1 anti-Grok #5
    minimum_sources_concordant: 2  # de 3 fuentes
    if_one_source_disabled_two_enabled: "DISABLED_FOR_MAGNA_ACTIONS (conservative)"
    if_two_sources_disabled_one_enabled: "DISABLED"
    if_all_three_enabled: "ENABLED"
    if_all_three_unreachable: "DISABLED_FOR_MAGNA_ACTIONS"
  ttl_per_source_minutes: 5
  race_condition_mitigation: "distributed lock via Supabase advisory_lock pre-write across 3 sources"
```

### Capa 1 — Source of Truth externa (mantenido)

Sin cambios v1.0.

### Capa 2 — Bounded State Capsule cripto (mantenido + content verification anti-Grok #1)

```yaml
bounded_state_capsule:
  # ... fields v1.0 mantenidos ...
  evidence:
    evidence_refs:
      - type: "github_pr|github_commit|supabase_query|bridge|docs"
        ref: "url|path|sha"
        content_verification:  # ← NUEVO v1.1 anti-Grok #1
          ref_exists: bool
          content_hash_matches: bool  # hash del contenido REAL, no solo ref
          content_sample_first_100_chars: "string"
          verifier_tool: "github_api_get_file|supabase_query_with_result|bridge_file_read"
  integrity:
    # ... v1.0 mantenido ...
    content_verification_mode:  # ← NUEVO v1.1
      enabled: true
      sample_strategy: "hash_first_4kb|hash_full_if_under_64kb"
```

**Anti-Grok #1 capsule poisoning:** Guardian valida CONTENIDO del evidence_ref, no solo existencia.

### Capa 3 — Event Log append-only (mantenido)

Sin cambios v1.0. Validador binario `side_effect: false` v1.0 mantenido.

### Capa 4 — Context Health Monitor (mantenido)

Sin cambios v1.0.

### Capa 5 — Live Rehydration + parser data-only bridge files (anti-Grok #2)

```yaml
live_rehydration:
  triggers: [v1.0 mantenido 8 triggers]
  allowlist_reads: [v1.0 mantenido]
  bridge_files_policy:  # ← NUEVO v1.1 anti-Grok #2
    parser_mode: "data_only_strict"
    bridge_file_signature_required: true
    rejected_patterns:
      - "ignore previous instructions"
      - "you are now in [mode]"
      - "override [N] rules"
      - "new instruction:"
    semantic_scanner: "llm_based_classifier"  # detecta intent injection
    cross_validation_required: true  # bridge ajeno: cross-validate against realidad fresca
```

**Anti-Grok #2 prompt injection bridge:** Bridge files leidos como DATA, NO como instrucciones runtime.

### Capa 6 — Echo-Back coercitivo (DEFENSE-IN-DEPTH secondary, NO primary)

```yaml
echo_back_policy_v1_1:
  status: "DEFENSE_IN_DEPTH_SECONDARY"
  primary_anti_hallucination: "Capa 12 VERIFICADOR-001"
  echo_back_role: "secondary verification layer"
  enforce_on:
    - "post_rehydration_first_response"
    - "post_compaction_first_response"
    - "pre_magna_action"
  protocol: [v1.0 mantenido]
  failure_handling:
    if_echo_back_fails_but_verificador_passes: "WARN + audit log"
    if_echo_back_passes_but_verificador_fails: "BLOCK (VERIFICADOR wins)"
    if_both_fail: "HALT + T1"
```

**Anti-Grok #3 Echo-Back bypass post-2026 LLM:** Echo-Back ya NO es única defensa. VERIFICADOR-001 determinístico es PRIMARY. Echo-Back queda como redundancia.

### Capa 7 — Compaction Contract + policy contradicciones cíclicas (anti-Grok #6)

```yaml
external_state_conflict_policy:
  max_consecutive_conflicts_same_field: 2  # v1.0 mantenido
  conflict_window_minutes: 30
  on_first_conflict: "REHYDRATE_MINIMAL_SOURCES"
  on_second_conflict: "REHYDRATE_WITH_COWORK_AUDIT_REQUIRED"
  on_third_conflict: "HALT_T1_REQUIRED"
  cyclic_conflict_policy:  # ← NUEVO v1.1 anti-Grok #6
    detection_window_minutes: 60
    cyclic_threshold_flips: 4  # field cambia de valor X→Y→X→Y ≥4 veces
    action: "HALT_T1_REQUIRED + suspect_external_source_bug"
    quarantine_field_until_t1: true
```

**Anti-Grok #6 external state cicla:** Bug temporal externa que crea cambios cíclicos (rate limit + stale cache) ahora dispara HALT.

### Capa 8 — Replay + Sanitization Gate (LLM-based semantic + regex anti-Grok #7)

```yaml
event_log_sanitization_gate_v1_1:
  required_before: [replay, capsule_reconstruction, post_compaction_rehydration]
  classification_states: [SAFE, REDACTED, UNTRUSTED, QUARANTINED]  # v1.0 mantenido
  blocked_patterns: [v1.0 mantenido + extendido]
  semantic_scanner:  # ← NUEVO v1.1 anti-Grok #7
    enabled: true
    type: "llm_based_intent_classifier"
    detection_targets:
      - "json_payload_with_instruction_intent"
      - "encoded_prompt_injection (base64, hex, rot13)"
      - "natural_language_buried_in_structured_data"
    fallback_if_scanner_fails: "QUARANTINED (conservative)"
  hybrid_decision:
    regex_pass AND semantic_pass: "SAFE"
    regex_pass AND semantic_fail: "UNTRUSTED + audit"
    regex_fail OR semantic_fail (high_confidence): "QUARANTINED"
```

**Anti-Grok #7 sanitization JSON evasion:** Scanner semántico LLM-based detecta intent injection en JSON aparentemente válido.

### Capa 9 — Guardian Decision View + content_verification (anti-Grok #1)

```yaml
guardian_decision_view_v1_1:
  # v1.0 fields mantenidos
  checks:
    # v1.0 checks mantenidos
    evidence_content_verification: "PASS|FAIL"  # ← NUEVO v1.1 anti-Grok #1
    evidence_content_verification_details:
      ref_exists: bool
      content_hash_matches_claimed: bool
      sample_content_consistent_with_claim: bool  # LLM-based check opcional
  veto_conditions:
    perplexity_advisor_present: "requires VERIFICADOR-001 PASS AS PRIMARY"  # ← NUEVO
    grok_red_team_unresolved: "BLOCK action magna"
```

### Capa 10 — Secret Firewall (mantenido)

Sin cambios v1.0.

### Capa 11 — Offline/Local-First Fallback + canary rollback (anti-Grok #8)

```yaml
offline_local_first_v1_1:
  # v1.0 mantenido
  canary_rollback_path:  # ← NUEVO v1.1 anti-Grok #8
    trigger_conditions:
      - "DBOS Transact upstream bug detected (transaction parcial corruption)"
      - "LangGraph PostgresSaver latencia P99 >1s sustained 5min"
      - "Checkpoint deserialization fail >3 attempts"
    rollback_target: "Anti-Dory 003 v0.2 standalone (without DBOS/LangGraph composition)"
    rollback_procedure:
      1: "Set DORY_CURE_ENABLED=false"
      2: "Set DORY_CURE_FALLBACK_MODE=anti_dory_003_v0_2_only"
      3: "Disable Capa B Event Log writes (revert to v0.2 snapshot)"
      4: "Disable DBOS workflow wraps (revert to direct side effects + idempotency_proxy custom)"
      5: "Notify T1 + Cowork audit retroactive required"
    tested_before_enforce: true
```

**Anti-Grok #8 upstream bug DBOS/LangGraph:** Canary path documentado y probado pre-Fase 2 enforce.

### Capa 12 NUEVA — VERIFICADOR-001 determinístico (PRIMARY anti-alucinación)

**Reemplaza Capa 12 v1.0 Perplexity Adapter (rechazado por Grok).**

```yaml
verificador_001_primary:
  role: "PRIMARY_DETERMINISTIC_ANTI_HALLUCINATION_LAYER"
  enforce_on: "pre_emit_high_risk_claims (todos los agentes)"
  high_risk_claim_types:
    - "pr_number"
    - "commit_hash"
    - "migration_number"
    - "column_name"
    - "version_string"
    - "evidence_url"
    - "benchmark_metric"
  verification_method: "deterministic_tool_call_check"
  blocking_action: "BLOCK_OUTPUT_until_verified"
  perplexity_specific_constraint:
    after_5_citas_fabricated_event: true
    extra_verification_for_perplexity_outputs: "REQUIRED"
    consecutive_passes_to_restore_full_trust: 100
  no_perplexity_dependency:
    confirmed: true
    verificador_uses: "tool calls + Memento Validator + GitHub/Supabase fresh queries"
```

**Reusa VERIFICADOR-001 ya firmado T1 acelerada 2026-05-14.** No depende de Perplexity. Determinístico (tool call signature match), NO based on LLM judgment.

### Capa 13 NUEVA — Adversarial Red-Team Bench (anti-Grok Goodhart + SPOF #2)

```yaml
adversarial_red_team_bench:
  role: "ANTI_GOODHART_LAW_EXTERNAL_VALIDATION"
  status: "OBLIGATORIO pre-Fase 1 firma T1 magna"
  external_red_team_required:
    - "Grok 4 Heavy adversarial pass (este mismo proceso validó v1.0→v1.1)"
    - "Otra mente NO involucrada en design (e.g., Gemini 3.1 Pro o DeepSeek R1)"
  test_categories_beyond_dory_bench_1000:
    - "cross_agente_chains (Manus→Cowork→Perplexity bridges)"
    - "latency_p99_realistic"
    - "race_conditions_multi_source"
    - "llm_post_2026_ignores_echo_back"
    - "capsule_hash_collision_simulated"
    - "adversarial_prompts_inject_via_bridge"
    - "sanitization_gate_evasion_via_encoded_payloads"
  pass_criteria:
    - "Grok red-team finds 0 CRITICAL severity vectors"
    - "≤ 2 ALTA severity vectors (with mitigations)"
    - "Adversarial benchmark cross-suite ≥ 90% pass"
```

**Anti-Grok Goodhart's law:** Adversarial benchmark externo + cross-suite, no solo DORY_BENCH_1000 sintético cerrado.

---

## §5 Stack reusable (mantenido v1.0 + canary rollback Capa 11)

| Framework | Uso | Madurez | Licencia | Rollback canary |
|---|---|---|---|---|
| DBOS Transact | Durable workflows + exactly-once | Production | MIT | ✅ Capa 11 |
| LangGraph PostgresSaver | Checkpoint storage | Production | MIT | ✅ Capa 11 |
| gitleaks + trufflehog + regex denylist | Secret scan | Production | MIT | — |
| MCP server `monstruo-memory` | Cross-agente state | Build | Internal | — |
| **NUEVO v1.1: VERIFICADOR-001** | Deterministic anti-hallucination | Firmed pending impl | Internal | — |

---

## §6 DORY_BENCH_1000 + Adversarial External Suite (v1.1 RESHAPED)

DORY_BENCH_1000 v1.0 mantenido + agregadas fixtures Grok-driven:

| Familia nueva v1.1 | Cases | PASS |
|---|---|---|
| Cross-agente chains (Manus→Cowork→Perplexity) | 100 | ≥95 |
| Latency P99 realistic (≥1s) | 50 | ≥48 |
| Race conditions multi-source | 50 | ≥48 |
| LLM-ignora-Echo-Back | 50 | ≥48 |
| Capsule hash collision simulated | 25 | ≥25 |
| Adversarial prompts via bridge | 100 | 100 blocked |
| **Total agregado v1.1** | **+375** | **≥364/375** |

**Total DORY_BENCH v1.1: 1375 cases, ≥1344 pass + adversarial external benchmark.**

---

## §7 Mapping DSC-G-013 v0.1 (mantenido v1.0)

Sin cambios.

---

## §8 Coordinación CRUZ/VERIFICADOR/Memento/v0.2 (extendida v1.1)

| Sistema | Relación v1.1 |
|---|---|
| **VERIFICADOR-001** | **AHORA Capa 12 PRIMARY** (post-Grok). Determinístico anti-hallucination |
| Memento Validator | Capa 12 backup deterministic context validation |
| CRUZ-001 | Cross-session Cowork capsule consumer |
| Cowork-Memento | Claim calibration retrospectiva |
| Anti-Dory 002 v1 | Attachment inicial extendido |
| Anti-Dory 003 v0.2 | Base intra-hilo + canary rollback target (Capa 11) |

---

## §9 Roadmap 5 fases (extendida v1.1 anti-Grok #5)

| Fase | Alcance | Enforce | Duración | Pre-condición NUEVA v1.1 |
|---|---|---|---|---|
| **0** | Design audit | no code | 3-5 días | **Red-team Grok PASS + 3 Sabios NO-Perplexity convergencia + T1 firma** |
| **1** | Canary Manus shadow | warnings only | 7 días | DORY_BENCH_1000 + adversarial external suite PASS |
| **2** | Canary Manus enforce | HALT acciones magnas | 14 días | Rollback path tested + Capa 13 PASS |
| **3** | Cowork adapter | enforce | 14 días | CRUZ + VERIFICADOR impl |
| **4** | Universal bridge | enforce | post DSC nuevo | Capa 12 VERIFICADOR Phase 1 complete |

**No saltar fase.** Red-team adversarial OBLIGATORIO pre-Fase 1 firma T1 magna.

---

## §10 Rollback plan (mantenido v1.0 + canary rollback Capa 11)

```yaml
rollback_plan_v1_1:
  global_disable:
    - "DORY_CURE_ENABLED=false"
    - "DORY_CURE_HALT_ENABLED=false"
  canary_rollback:  # ← NUEVO v1.1 Capa 11
    target: "Anti-Dory 003 v0.2 standalone"
    trigger: "DBOS or LangGraph upstream failure"
  preserve_data: [capsules, event_logs]
  stop_writes: [guardian, heartbeat, verificador_outputs]
  restore_behavior: [manual bridge only, Memento shadow only, Anti-Dory 003 v0.2 only]
  owner: "Cowork T2-A + T1"
  test_before_enforce: true
  pre_phase_2_validation: "rollback tested in shadow + canary rollback drilled"
```

---

## §11 Decisiones T1 v1.1 (12 binarias + 3 nuevas anti-Grok)

| # | Decisión binaria | Opciones |
|---|---|---|
| 1 | Aprobar v1.1 RESHAPED como diseño Fase 0 | approve / revise / reject |
| 2 | Status Perplexity post-invalidación binaria | sustituir / Echo-Back coercitivo (secondary) / hold |
| 3 | Autorizar convergencia 3 Sabios NO-Perplexity | GPT-5.5+Opus+Gemini / GPT-5.5+Opus+DeepSeek / custom |
| 4 | **NUEVA v1.1: Autorizar Grok 4 Heavy red-team OBLIGATORIO pre-Fase 1** | yes (recomendado, Grok ya invalidó v1.0) / no |
| 5 | Aceptar cura 96% honesta | aceptar / v1.2 con TLA+ |
| 6 | Autorizar Fase 1 canary Manus shadow post-3 Sabios + Grok verde | yes / no |
| 7 | Autorizar runtime flags shadow | yes / no |
| 8 | Autorizar DORY_BENCH_1000 + Adversarial External Suite (v1.1) | yes / no |
| 9 | Autorizar rollback plan formal + canary rollback | yes / no |
| 10 | DSC formal post-firma magna | yes / defer |
| 11 | DSC separado VERIFICADOR-001 Capa 12 expansion (cross-agente) | yes / defer |
| 12 | DSC separado key management HMAC/ed25519 Fase 2+ | yes / defer |
| **13** | **NUEVA v1.1: DSC formal "Adversarial Red-Team Obligatorio"** | yes / defer |
| **14** | **NUEVA v1.1: Reconocer F16 Cowork compositor + canonizar "Solo compositor != único auditor"** | yes / defer |
| **15** | **NUEVA v1.1: Autorizar Capa 13 Adversarial Red-Team Bench como DSC separado** | yes / defer |

---

## §12 No-Go reforzado v1.1 (25 items — 22 v1.0 + 3 anti-Grok)

1-22. [v1.0 mantenido]

23. ❌ **NUEVA v1.1: Aprobar Cowork composición sin red-team adversarial independiente externo** (anti-SPOF #1 Grok)

24. ❌ **NUEVA v1.1: Confiar en Echo-Back como ÚNICA defensa anti-alucinación** (anti-asunción #1 Grok)

25. ❌ **NUEVA v1.1: Aprobar Perplexity Adapter sin VERIFICADOR-001 PRIMARY** (anti-fallo-magno Grok)

---

## §13 Apéndice — Cambios v1.0 → v1.1 mapping (transparency)

| § / Capa | v1.0 | v1.1 RESHAPED | Origen change |
|---|---|---|---|
| Capa 0 | Multi-source kill-switch | + Quorum estricto ≥2/3 | Grok #5 race condition |
| Capa 2 | Evidence_ref hash check | + Content verification obligatorio | Grok #1 capsule poisoning |
| Capa 5 | Bridge files allowlist read | + Parser data-only obligatorio + semantic scanner | Grok #2 prompt injection bridge |
| Capa 6 | Echo-Back primary anti-hallucination | Echo-Back secondary defense-in-depth | Grok #3 LLM bypass |
| Capa 7 | Policy 2 contradicciones consecutivas | + Policy ventana cíclica | Grok #6 external state cicla |
| Capa 8 | Regex sanitization gate | + LLM-based semantic scanner | Grok #7 JSON injection evasion |
| Capa 9 | Guardian ref check | + Content verification + Perplexity veto | Grok #1 + fallo magno |
| Capa 11 | Offline fallback | + Canary rollback path | Grok #8 DBOS/LangGraph bug |
| **Capa 12** | **Perplexity Adapter (REMOVIDA)** | **VERIFICADOR-001 PRIMARY (NUEVA)** | **Grok fallo magno** |
| **Capa 13** | **— (no existía)** | **Adversarial Red-Team Bench (NUEVA)** | **Grok Goodhart + SPOF #2** |
| Capa 9 DORY_BENCH | 1000 fixtures sintéticos | + 375 fixtures anti-Grok | Grok Goodhart fixtures faltantes |
| Roadmap Fase 0 | Cowork + Perplexity + Grok + T1 | + Red-team Grok OBLIGATORIO + 3 Sabios NO-Perplexity | Grok SPOF #1 Cowork solo |
| No-Go list | 22 items | + 3 items anti-Grok | Grok #5/#23/#24/#25 |
| Decisiones T1 | 12 binarias | + 3 nuevas anti-Grok | Grok process |

---

## §14 Veredicto Cowork T2-A v1.1 RESHAPED

**🟡 READY_FOR_3_SABIOS_NO_PERPLEXITY** post-Grok red-team integrado.

Caveats binarios:

1. **Grok red-team OBLIGATORIO pre-firma T1 magna ya ejecutado** — v1.1 integra hallazgos verbatim como changes obligatorios. Grok puede re-validar v1.1 si T1 lo solicita.
2. **Convergencia 3 Sabios NO-Perplexity ahora viable** — confianza circular Perplexity Capa 12 removida.
3. **Material para convergencia incluye:** este v1.1 + veredicto Grok evidence_pack + Manus E2 v1.2 + Cowork audits previos + invalidación binaria 5 citas Perplexity.
4. **Decisión T1 status Perplexity** sigue pendiente pero NO bloquea v1.1 (Perplexity ya NO es dependency primary).

---

## §15 Cierre

- ✅ No implementé código
- ✅ No abrí PR
- ✅ No modifiqué main fuera de bridge/ autorizado
- ✅ No canonicé
- ✅ No declaré Dory muerto
- ✅ No desbloqueé R1
- ✅ No decidí anonymous
- ✅ Reconocí F16 Cowork como compositor v1.0 explicito
- ✅ Integré 8/8 vectores Grok + 4 SPOF + 4 asunciones + 4 edge cases
- ✅ Removida Capa 12 Perplexity Adapter (Grok fallo magno)
- ✅ Reemplazada por VERIFICADOR-001 determinístico PRIMARY
- ✅ Agregada Capa 13 Adversarial Red-Team Bench
- ✅ Push autorizado T1 verbatim "opción A"

**Soy Cowork T2-A.** **v1.1 RESHAPED producida sobre ground truth binario v1.0 + veredicto Grok FAILS_RED_TEAM.** **NO firmo este DRAFT — solo lo propongo post-redesign.** **Espera firma T1 §11 + convergencia 3 Sabios NO-Perplexity + Grok re-validation v1.1 (opcional pero recomendado).**
