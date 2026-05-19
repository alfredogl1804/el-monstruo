# AGENT OUTPUT — manus_e2 — AUDIT INDEPENDIENTE FUSIÓN DORY-CURE-CONVERGED-001 v1.0

## Metadata
- **agente:** manus_e2
- **rol real:** ejecutor T3 LA-FORJA + auditor independiente desde perspectiva propia (mi v1.2 fue uno de los 4 componentes fusionados)
- **fecha/hora:** 2026-05-19 ~03:30 UTC-6
- **rama:** `control-tower/manus-e2-audit-dory-cure-converged-001-2026-05-19` (lateral, push pendiente confirmación)
- **PR:** ninguno
- **commit:** pendiente
- **estado fuente:** AUDIT
- **tocó código:** no
- **tocó main:** no
- **fuente leída binariamente:** `bridge/sprints_propuestos/sprint_DORY_CURE_CONVERGED_001_v1_0_DRAFT_COWORK.md` blob `41bb46f4f5cf2e1fbcaae60ab0aed00138771882` commit `efbe6a323a7dcf5f6d883f09b0b8971378f3e3af` en `origin/main` (24,932 bytes, 612 líneas)

## Qué hice
1. Verifiqué binariamente que la fusión Cowork existe en `origin/main` con SHA `efbe6a3` declarado por T1
2. Leí los 612 líneas de la fusión completa vía `git show origin/main:...` ↔ checkout local + lectura por rangos en mount
3. Tenía pre-cargada la lectura binaria de los 4 componentes constituyentes (mi v1.2 + Cowork v0.2 + Perplexity v0.3 + Perplexity v0.4 DELTA) realizada antes del push de la fusión
4. Comparé verbatim 12 aportes magna de mi v1.2 vs su integración en la fusión
5. Identifiqué 5 gaps + 4 diluciones binariamente verificables citando línea/sección
6. Producí veredicto binario sin fabricar referencias

## Evidencia
- **Fusión leída:** lineas 1-612 de `bridge/sprints_propuestos/sprint_DORY_CURE_CONVERGED_001_v1_0_DRAFT_COWORK.md` commit `efbe6a3`
- **Mi v1.2 referenciado:** `bridge/sprints_propuestos/sprint_ANTI_CONTEXT_LOSS_001_v1_2_ADDENDUM_DRAFT.md` en branch `sprints-propuestos/2026-05-19-anti-context-loss-audit-request` commit `5cdbf74` (mi push previo)
- **Componentes Perplexity leídos:** `DORY-CURE-001_v0_3_DRAFT_PERPLEXITY.md` (518 líneas), `DORY-CURE-001_v0_4_DELTA_PERPLEXITY.md` (320 líneas)
- **Componente Cowork leído:** `bridge/sprints_propuestos/sprint_MANUS-ANTI-DORY-003_v0_2_DRAFT.md` en main + copia control tower

---

## §1 Tabla "Tu aporte v1.2 integrado en fusión?"

| # | Aporte Manus E2 v1.2 | Integrado? | Sí/No/Parcial | Ubicación verbatim fusión |
|---|---|---|---|---|
| 1 | **Cura 96% honesta vs 98% Perplexity** | ✅ | **Sí verbatim** | §1 línea 28 ("≥96% de escenarios de prueba realistas") + §1 línea 30 ("NO 98% operativa. NO Dory curado") + §6 línea 412 + §13 No-Go #22 línea 560 ("Firmar 96% sin baseline empírico"). Citado explícitamente como "Tomado verbatim de Manus E2 v1.2" |
| 2 | **DBOS Transact (reemplaza idempotency_proxy custom)** | ✅ | **Sí** | §5 tabla línea 403: "DBOS Transact \| Durable workflows + exactly-once side effects \| Production \| MIT \| `idempotency_proxy.py` + `side_effect_outbox`". §14 mapping línea 582 acredita a "Manus E2 v1.2 APORTE MAGNO" |
| 3 | **LangGraph PostgresSaver (reemplaza snapshot_writer custom)** | ✅ | **Sí** | §5 tabla línea 404: "LangGraph PostgresSaver \| Checkpoint capsule storage Supabase-backed \| Production \| MIT \| `snapshot_writer.py`" |
| 4 | **Echo-Back coercitivo Mec 2** | ✅ | **Sí preservado núcleo** | Capa 6 líneas 233-256, declarada explícitamente "Manus E2 Mec 2 — APORTE ÚNICO". §14 mapping línea 575 confirma "Manus E2 v1.2 Mec 2 ÚNICO". Capa 12 línea 391 también lo aplica al adapter Perplexity post-invalidación |
| 5 | **SHA-256 normalizado (trim + NFC + comillas)** | ✅ | **Sí** | Capa 6 línea 246 ("SHA-256 normalizado (trim + NFC + comillas)") + líneas 250-253 explícito normalization steps verbatim |
| 6 | **Triple replicación cross-provider (filesystem sandbox + Supabase + GitHub append-only)** | 🟡 | **Parcial** | Mecanismo distribuido en Capa 1 (líneas 92-94 "GitHub + Supabase + Bridge + Docs canon + Runtime endpoints") + Capa 11 Offline `.monstruo/dory/` (líneas 359-369) + Capa 0 sources_order (líneas 82-86) — pero **NO declarado como mecanismo unificado "Triple Replicación"**, está fragmentado en 3 capas distintas. Mi spec lo presentaba como Mec 1 nominado |
| 7 | **Invalidación binaria 5 citas Perplexity como input doctrinal vivo** | ✅ | **Sí** | §1 línea 41 verbatim: "Manus E2 detectó al vivo Perplexity Sonar Reasoning Pro fabricando 5 citas verificables durante validación de v1.2 mismo. El propio proceso de validación demostró el riesgo. **Este evento es input doctrinal vivo a este spec fusionado.**". Reforzado en Capa 12 línea 391 + §13 No-Go #21 línea 559 + §15 caveat #1 línea 594 |
| 8 | **Residual <4% desglosado en 4 categorías concretas** | ✅ | **Sí verbatim** | §1 tabla líneas 32-39 con las 4 categorías idénticas: alucinación adversarial LLM 1.5%, catástrofe 3 proveedores <1%, bugs frameworks 1%, error humano T1 <0.5% |
| 9 | **-600 LOC custom net effect** | ✅ | **Sí** | §5 línea 408: "Net effect Manus E2: -800 LOC custom + +200 LOC glue = **-600 LOC mantenidas internamente**" |
| 10 | **MCP server `monstruo-memory` cross-agente** | ✅ | **Sí** | §5 tabla línea 406 + Capa 12 líneas 392-393: "mcp_server_monstruo_memory: uses: Manus E2 v1.2 cross-agente MCP server, role: shared state bridge" |
| 11 | **Dry-run gradual 3 niveles riesgo** | ❌ | **No** | **NO encontrado** ni en §10 Rollout (5 fases canary→universal sin granularidad por nivel de riesgo de acción), ni en Capa 9 Guardian Decision View (binary ALLOW/BLOCK/T1_REQUIRED sin matriz dry-run por riesgo). Mi v1.2 proponía 3 niveles (read-only/idempotent/destructive) cada uno con política propia. Diluido por completo |
| 12 | **28 ítems DoD unificado** | 🟡 | **Parcial** | §9 DORY_BENCH_1000 fixture design + 8 familias + criterios pass/fail (~10 ítems benchmark) + §11 Rollback plan + §12 12 decisiones T1 + §13 22 No-Go suman ítems pero **NO consolidados en una sola tabla "Definition of Done"** como tenía mi v1.2 (28 ítems numerados secuenciales). Disperso en 4 secciones distintas |

**Conteo binario integración:** 9 ✅ Sí + 2 🟡 Parcial + 1 ❌ No = **75% integración total + 17% parcial + 8% ausente**

---

## §2 Tabla "Gaps de fusión vs mi v1.2 original"

| # | Gap (algo que mi v1.2 cubría y la fusión NO) | Severidad | Impacto operativo |
|---|---|---|---|
| G1 | **Dry-run gradual 3 niveles riesgo** (read-only / idempotent / destructive) cada uno con política propia | 🟠 ALTA | Sin granularidad por nivel de riesgo, Guardian Decision View (Capa 9) recomienda binario ALLOW/BLOCK/T1_REQUIRED. Acciones idempotentes (e.g. `git fetch`, queries) tienen mismo treatment que destructivas (`git push --force`). Mayor fricción operativa o mayor riesgo según interpretación |
| G2 | **DoD unificado 28 ítems numerados** en una sola tabla revisable | 🟡 MEDIA | Ítems dispersos en §9, §10, §11, §12, §13. Auditor o ejecutor debe agregarlos manualmente. Riesgo de perder ítems durante audit forensic |
| G3 | **Triple Replicación nominada como mecanismo unificado Mec 1** | 🟡 MEDIA | Fragmentada en 3 capas (1 + 11 + 0). Sin contrato de "qué se replica simultáneamente vs qué es cache local vs qué es kill-switch". Posible inconsistencia de implementación cross-agente |
| G4 | **Comparación binaria explícita "lo que cura el v1.2" vs "lo que cura la fusión"** (matriz vector → cura) | 🟢 BAJA | Mi v1.2 mostraba 7 vectores con cura individual estimada. La fusión los reduce a 5 vectores Dory (D1-D5 §3) sin tabla cura-por-vector. Información útil para validación residual <4% perdida |
| G5 | **Justificación binaria framework-by-framework** (por qué DBOS específicamente, por qué LangGraph PostgresSaver específicamente, qué alternativas se descartaron) | 🟢 BAJA | §5 tabla declara los frameworks pero **no incluye sección "Frameworks evaluados y descartados"** que tenía mi v1.2 (Temporal, Restate.dev, Inngest evaluados y descartados). Auditor que no tiene mi v1.2 abierto pierde el racional |

---

## §3 Tabla "Diluciones — aportes míos versión fusionada vs original"

| # | Aporte original verbatim v1.2 | Versión en fusión Cowork | ¿Diluido? Sí/No | Recomendación binaria |
|---|---|---|---|---|
| D1 | "Cura ~96% realista" + tabla 12 vectores cubiertos individualmente cada uno con porcentaje | "≥96% de escenarios de prueba realistas" — porcentajes individuales por vector eliminados | 🟡 **Sí parcial** | Agregar §1.5 "Cura por vector Dory" con tabla 5 vectores (D1-D5) × % cubierto. Trazable a DORY_BENCH_1000 familias §9 |
| D2 | Mec 2 Echo-Back coercitivo descrito como "el más frágil del diseño" en mi opinión personal v1.2 con caveat de fragilidad explícito | Capa 6 líneas 233-256 sin caveat de fragilidad | 🟡 **Sí parcial** | Agregar caveat verbatim en Capa 6: "Mecanismo más frágil del diseño — depende de capacidad LLM de ecoar verbatim. SHA-256 mismatch repetido (3+) requiere escalation T1, no auto-retry indefinido" |
| D3 | DBOS Transact + LangGraph PostgresSaver como "lock-in consciente declarado" en mi spec con sección "Trade-offs lock-in y mitigación" | §5 tabla simple sin sección lock-in trade-offs | 🟡 **Sí parcial** | Agregar §5.1 "Lock-in trade-offs": qué hacer si DBOS cambia licencia (mitigación: workflow definitions son data, migrable), si LangGraph pivota (mitigación: PostgresSaver es interfaz simple, custom shim viable) |
| D4 | "Triple Replicación" como mecanismo nominado Mec 1 con SLA write-success específico | Distribuido en 3 capas (Capa 1 + 11 + 0) sin SLA específico | 🟡 **Sí estructural** | Agregar §1.6 "Mecanismo Triple Replicación nominado": filesystem sandbox (write SLA <50ms) + Supabase (write SLA <500ms) + GitHub bridge append-only (write SLA <2s). Define qué pasa si solo 1 o 2 destinos exitosos |

**Conteo binario diluciones:** 4 diluciones detectadas (3 parciales semánticas + 1 estructural). **Ninguna pérdida total, todas reparables con adiciones acotadas.**

---

## §4 Veredicto binario

**`NEEDS_REVISION_BEFORE_FIRMA_T1`**

Justificación binaria:
- Integración de mi aporte: **9 ✅ + 2 🟡 + 1 ❌** (75% sí + 17% parcial + 8% ausente)
- Gaps detectados: **5** (1 ALTA + 2 MEDIA + 2 BAJA) — todos reparables con secciones acotadas, NO requieren rediseño de capas
- Diluciones detectadas: **4** (todas parciales/estructurales, núcleo conservado)
- Composición magna: **EFECTIVAMENTE SUPERIOR a mi v1.2 sola** en 7 aspectos (Capa 0 kill-switch, Capa 2 cripto-verificable, Capa 3 sanitization, Capa 7 external-state-wins-≤2, Capa 8 sanitization gate, Capa 9 Guardian, §9 DORY_BENCH_1000 firmado)
- **Pero** la composición pierde 1 aporte mío (G1 dry-run gradual) que tenía valor operativo neto
- **Y** la composición diluye 4 aportes míos (D1-D4) cuyo núcleo se conserva pero pierden contexto crítico (caveat fragilidad Echo-Back, lock-in trade-offs, SLA replicación)

Veredicto neto: **la fusión es magna pero no está lista para firma T1 sin las correcciones del §5**.

---

## §5 Cambios obligatorios pre-firma T1

### CO-1 — Agregar Capa 9.1 "Dry-run gradual por nivel de riesgo" (CRÍTICO para CO)

Insertar entre Capa 9 (líneas 313-344) y Capa 10:

```yaml
guardian_dry_run_policy:
  risk_levels:
    LOW_READ_ONLY:
      examples: [git_fetch, get_*, query_*, list_*, Read, Grep, Glob]
      dry_run_required: false
      guardian_recommendation_default: "ALLOW"
    MEDIUM_IDEMPOTENT:
      examples: [git_pull, supabase_select, github_status_check]
      dry_run_required: false
      guardian_recommendation_default: "ALLOW_WITH_LOG"
      requires: capsule_fresh + context_health<=WARN
    HIGH_DESTRUCTIVE:
      examples: [merge, deploy, apply_migration, git_push_force, delete]
      dry_run_required: true  # explica qué haría primero, espera T1
      guardian_recommendation_default: "T1_REQUIRED"
      requires: capsule_fresh + context_health=OK + rollback_available + t1_authorization_present
```

### CO-2 — Agregar §1.5 "Cura por vector Dory + DORY_BENCH_1000 mapping" (MEDIA)

Tabla 5 vectores D1-D5 × % cura realista × familia DORY_BENCH_1000 que lo valida:

| Vector | Cura realista | Familia bench validadora |
|---|---|---|
| D1 Cold start | ~98% | cold_start (150 cases) |
| D2 Compaction loss | ~95% | post_compaction (200 cases) |
| D3 Intra-thread drift | ~95% | post_compaction + crash_recovery |
| D4 Evidence drift | ~96% | stale_pr_branch + migration_drift |
| D5 Poison/secrets | ~99% (blocking) | memory_poisoning + secret_leakage |
| **Promedio** | **~96%** | global ≥980/1000 |

### CO-3 — Agregar §1.6 "Mecanismo Triple Replicación nominado con SLA" (MEDIA)

Sección formal definiendo:
- Destino 1: filesystem sandbox `.monstruo/dory/latest_capsule.yaml` — SLA write <50ms — TTL 5min
- Destino 2: Supabase `bounded_state_capsules` table — SLA write <500ms — TTL 4h (Capa 2 freshness_ttl_minutes)
- Destino 3: GitHub append-only `bridge/control_tower/[fecha]/[agente]/event_log.jsonl` — SLA write <2s — append-only forever
- **Política write-success:** ≥2 de 3 destinos para considerar capsule "committed". 1 solo destino → DEGRADED_READONLY. 0 destinos → HALT.

### CO-4 — Agregar §5.1 "Lock-in trade-offs frameworks" (MEDIA)

Sección documentando:
- DBOS Transact: workflow definitions son data (TypeScript decorators) — migrables a Temporal/Restate.dev con shim si DBOS pivota
- LangGraph PostgresSaver: interfaz simple (`get_tuple`, `put`) — custom shim viable si LangChain pivota
- Frameworks evaluados y descartados (con razón verbatim):
  - Temporal: overkill para single-process orchestration
  - Restate.dev: menos maduro que DBOS para Postgres-backed durable workflows
  - Inngest: SaaS-only, no self-hosted opción

### CO-5 — Agregar caveat fragilidad en Capa 6 línea 256 (BAJA)

Insertar verbatim al final de Capa 6:

> **Caveat fragilidad Manus E2:** Echo-Back es el mecanismo MÁS frágil del diseño — depende de capacidad LLM de ecoar verbatim. Cuando SHA-256 mismatch ocurre 3+ veces consecutivas, **NO auto-retry indefinido**: escalation obligatoria a T1 (humano) vía bridge file `halt_events.md`. La cura del 96% incluye esta limitación residual (~1.5% alucinación adversarial categoría #1 §1).

### CO-6 — Agregar §12.13 decisión T1 sobre los CO-1 a CO-5 (BAJA)

Decisión T1 #13 nueva: "Aprobar los 5 cambios obligatorios CO-1 a CO-5 propuestos por Manus E2 audit pre-firma T1". Opciones: aprobar todos / aprobar selectivos / rechazar (mantener fusión as-is).

---

## §6 Bloqueos

| Bloqueo | Causa | Quién desbloquea | Urgencia |
|---|---|---|---|
| Audit no firma DRAFT | Regla T1 verbatim "NO firmes este DRAFT" | T1 (Alfredo) | Baja — esperado |
| Push branch lateral pendiente confirmación | Necesito autorización T1 explícita para push del audit (regla operativa CONTROL TOWER) | T1 (Alfredo) | Media — para que Cowork vea audit |
| Convergencia 3 Sabios NO-Perplexity bloqueada | Decisión T1 §12 #2 status Perplexity pendiente | T1 (Alfredo) | Media — antes de Fase 0 audit final |

---

## §7 Decisiones T1 requeridas

| # | Decisión | Opciones | Impacto | Urgencia |
|---|---|---|---|---|
| 1 | ¿Aprobar los 5 cambios obligatorios CO-1 a CO-5? | (A) aprobar todos; (B) aprobar selectivos; (C) rechazar | Determina si fusión avanza a 3 Sabios NO-Perplexity o regresa a Cowork para v1.1 | Alta |
| 2 | ¿Push de este audit a branch lateral `control-tower/manus-e2-audit-dory-cure-converged-001-2026-05-19`? | (A) sí; (B) no, mantener local | Visibilidad para Cowork T2-A + 3 Sabios NO-Perplexity | Media |
| 3 | ¿Yo (Manus E2) sigo en cola LA-FORJA #165 rebase post-audit, o me asigno como ejecutor Fase 1 canary DORY-CURE? | (A) #165 prioridad; (B) Fase 1 DORY-CURE; (C) ambos paralelo | Asignación recursos | Media |

---

## §8 Contradicciones / drift detectado

| # | claim A (mi v1.2) | fuente A | claim B (fusión Cowork) | fuente B | severidad |
|---|---|---|---|---|---|
| 1 | "Triple Replicación = mecanismo unificado Mec 1 con SLA explícito" | mi v1.2 §1.6 | "fragmentado en 3 capas (Capa 1 + Capa 11 + Capa 0)" | fusión §4 capas | 🟡 estructural — núcleo coincide, falta SLA |
| 2 | "Echo-Back es el mecanismo más frágil con caveat documentado" | mi v1.2 §3 limitaciones | "Capa 6 sin caveat fragilidad" | fusión líneas 233-256 | 🟢 baja — agregable con CO-5 |
| 3 | "Dry-run gradual 3 niveles riesgo" | mi v1.2 §2 mecanismos | "Guardian binario ALLOW/BLOCK/T1_REQUIRED" | fusión Capa 9 línea 337 | 🟠 alta — gap funcional, agregable con CO-1 |
| 4 | "DoD unificado 28 ítems numerados" | mi v1.2 §6 | "Disperso en §9, §10, §11, §12, §13" | fusión secciones | 🟡 media — agregable consolidando en sección nueva |

---

## §9 Qué NO asumir

1. ❌ NO asumir que mi audit firma el DRAFT — explícitamente NO firmo (regla T1)
2. ❌ NO asumir que `NEEDS_REVISION_BEFORE_FIRMA_T1` significa rechazo del trabajo de Cowork — la fusión es magna y superior a mi v1.2 sola en 7 aspectos
3. ❌ NO asumir que los CO-1 a CO-5 son los únicos cambios necesarios — son los detectados desde mi perspectiva ejecutora; 3 Sabios NO-Perplexity pueden encontrar más
4. ❌ NO asumir que `~96%` es métrica garantizada — es estimación operativa pendiente validación contra DORY_BENCH_1000 firmado (No-Go #22 lo prohíbe explícitamente)
5. ❌ NO asumir que la integración de Perplexity v0.4 valida automáticamente a Perplexity como Sabio — caveat #1 §15 + No-Go #21 + Echo-Back coercitivo aplicado al adapter Perplexity (Capa 12)
6. ❌ NO asumir que mi v1.2 es "mejor" que la fusión — es PEOR sin las contribuciones Perplexity (Capas 0, 2 cripto, 3 sanitization, 7, 8, 9, 11, §9 DORY_BENCH_1000) y Cowork (TTL operacional, signature_mode phased, side_effect validador, §13 No-Go #21+#22, §10 5 fases secuenciales)
7. ❌ NO asumir que cura 96% = "Dory muerto" — No-Go #1 prohíbe explícitamente esa declaración
8. ❌ NO asumir que esta audit desbloquea Fase 1 — requiere firma T1 §12 + 3 Sabios NO-Perplexity + Grok red-team (decisiones #4 + #6)

---

## §10 Recomendación DRAFT

Como Manus E2 ejecutor T3 y co-autor del aporte magno -600 LOC + DBOS + LangGraph + Echo-Back + 96% honesto + invalidación Perplexity:

**Recomiendo a T1 (Alfredo) DRAFT:**
- (A) **Aprobar fusión Cowork DORY-CURE-CONVERGED-001 v1.0 con los 5 cambios obligatorios CO-1 a CO-5** integrados antes de convergencia 3 Sabios NO-Perplexity
- (B) **Mantener Perplexity en hold doctrinal** (decisión §12 #2) hasta Echo-Back coercitivo aplicado a sus outputs operativos (Capa 12)
- (C) **Convergencia 3 Sabios NO-Perplexity = GPT-5.5 Pro + Opus 4.7 + Gemini 3.1 Pro** (rechazar DeepSeek y Kimi por menor track record en context engineering 2026)
- (D) **Yo Manus E2 sigo cola LA-FORJA #165 rebase pendiente** (decisión §7 #3 opción A) — la implementación Fase 1 canary DORY-CURE puede asignarse a Manus E1 (ya tiene D6 Railway permanente firmada) post-firma magna

**Esto es DRAFT, NO decisión.** Solo T1 firma.

---

## §11 Cierre

- ✅ No incluí secretos
- ✅ No canonizo nada
- ✅ No desbloqueo R1
- ✅ No recomiendo merge/deploy sin T1
- ✅ No firmé este DRAFT de fusión
- ✅ No fabriqué citas — cada cita a la fusión incluye número de línea o sección verbatim verificable
- ✅ No declaré Dory muerto
- ✅ No decidí anonymous
- ✅ Este output queda listo para revisión de Cowork T2-A + Perplexity Torre de Control PBA (post-resolución status §12 decisión #2)

---

**Soy Manus E2 ejecutor T3.** **Audité fusión Cowork v1.0 desde mi perspectiva como co-autor de 1 de 4 componentes fusionados.** **Veredicto: NEEDS_REVISION_BEFORE_FIRMA_T1 con 5 cambios obligatorios reparables.** **Espera firma T1 §12 + integración CO-1 a CO-5 + 3 Sabios NO-Perplexity + Grok red-team antes de Fase 0 design audit final.**
