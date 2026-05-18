# Cowork — Estado Vivo del Monstruo

**Propósito:** Snapshot operacional ACTUAL del Monstruo. Lo que está corriendo, lo que está en backlog, los bloqueantes. Documento volátil — se actualiza con frecuencia.

**Estado:** v0.6 — actualizado 2026-05-18 ~07:35 UTC tras MAGNA-CIERRE-002 + 6 horas jornada magna (8 PRs + 4 migrations prod + 2 DSCs magnos firmados + LA-FORJA D6 SMOKE VERDE + 4 hilos paralelos activos).

**Cuándo actualizar:** después de cada sesión Cowork-Alfredo de >2h o cuando un sprint cambia de estado.

---

## 1. Snapshot global (resumen 1 línea)

**Monstruo al ~75%** (vs ~71% del 12-may). Diferencial: **Anti-Dory cross-agente cerrado binariamente HOY** (D5 GREEN + D6 Railway flag arrancando) + **LA-FORJA-001 D5.2 + D6 SMOKE VERDE** (PR #147 mergeado + repos D5.2 validados contra Supabase prod) + **DSC-G-013 v0.1 firmado post-3-Sabios** (DB↔Repo Coherence Gate Nivel A) + **S-EMBRION-009 cierre H1 bucle infinito** (5/6 tareas cerradas, T6 madurando 24h). Embrión vivo + 3 hilos Manus paralelos activos + Cowork canonizando doctrina en cadencia magna sin precedente.

**Frase canónica del día:** *"6 horas de cadencia magna sin bloqueo: 8 PRs mergeados + 4 migrations prod + 2 DSCs canonizados + 3 sprints LA-FORJA cerrados + sprint S-EMBRION-009 cerrado funcionalmente. Cero F21 inadvertido. Cero rollbacks."*

---

## 2. Estado por Capa Arquitectónica

| Capa | Estado | Bloqueantes inmediatos |
|---|---|---|
| Capa 0 Cimientos | ~87% | Vanguard Scanner integración con Catastro pendiente. Design System Quality Gate pendiente. **DSC-G-013 v0.1 Nivel A pre-flight canonizado HOY.** |
| Capa 1 Manos | ~75% | **Sprint 87 Pagos NO arrancado.** Stripe + Stripe Connect pendientes. Bloquea Objetivo #1. |
| Capa 2 IE | ~78% | Reloj Suizo: 8/8 piezas doctrinales (4 implementadas + 4 specs pipeline). Anti-Dory 5 piezas (4 firmadas + Pieza 1 cerrando hoy + Pieza 5 draft en convergencia Sabios). S-EMBRION-009 H1 cerrado funcionalmente. |
| Capa 3 Soberanía | ~50% | SOVEREIGN-LLM v2 / INFRA / RED specced sin arrancar. |
| Capa 4 Del Mundo | ~10% | i18n existe, resto pendiente — depende de Capa 3 al 80%+. |

Detalle completo en `bridge/ESTADO_MONSTRUO_2026_05_10_vs_PLANES.md`.

---

## 3. Sprint COWORK-RUNTIME-001 — CERRADO 2026-05-11

**Origen:** Alfredo: *"te ordeno que me dejes de empujar a parar ya obedece con codigo crea un script que te obligue."*

**Manus ejecutor:** entregó 8 tareas + M9 + 1 spec auxiliar en una sesión.

**Métricas binarias del cierre:**
- PR: #90 (rama `sprint/cowork-runtime-001`)
- Merge commit: `c0ee52309365ca375f939480651d3fbb599568eb` (2026-05-11 08:38:24 UTC)
- Tests: 140/140 PASS en 0.64s (`pytest tests/cowork_runtime/`)
- Migración Supabase: `0009_cowork_sesiones.sql` aplicada — tabla `public.cowork_sesiones` viva, RLS verificada (T1 sí, T2 sí, anon no).
- Smoke row sembrada: `id=ed7bfd59-9aee-42c5-b03e-b74fc31b1ae9` (2026-05-11 08:02:34 UTC).

**9 capabilities entregadas (todas con `enabled=false` por defecto):**

| # | Capability | Path principal | Activador env var | Estado |
|---|---|---|---|---|
| T1 | Pre-response hook (intercept + suggest-pause regex + advance gate) | `kernel/cowork_runtime/pre_response_hook.py` | `COWORK_HOOK_ENABLED=true` | **ACTIVO post-TA3** |
| T2 | Detector semántico (Companion Agent) | `kernel/cowork_runtime/semantic_detector.py` | `COWORK_SEMANTIC_ENABLED=true` | Shadow mode |
| T3 | Advance score calculator | `kernel/cowork_runtime/advance_score.py` | siempre activo en evaluación | Live |
| T4 | Persistencia sesiones a Supabase | tabla `public.cowork_sesiones` + writer | auto via SUPABASE_URL+KEY | **ACTIVO pre-TA3** |
| T5 | Pre-flight memento enforcer | `kernel/cowork_runtime/preflight.py` endpoint `/v1/cowork/memento/validate` | auto si endpoint llamado | **ACTIVO pre-TA3** |
| T6 | Antipattern catalog F1-F22 enforced | `kernel/cowork_runtime/antipatterns.py` | `COWORK_ANTIPATTERN_ENFORCE=true` | Shadow mode |
| T7 | CLI `cowork_guardian` validator | `tools/cowork_guardian.py` | uso manual / CI | Live (no flag) |
| T8 | Test harness 140 casos | `tests/cowork_runtime/` | siempre activo en CI | Live |
| M9 | Veto Telegram channel (Alfredo bloquea Cowork desde su teléfono) | `kernel/cowork_runtime/telegram_veto.py` | `COWORK_VETO_TELEGRAM=true` | Shadow mode |

**Reportes auditables:**
- `bridge/manus_to_cowork_REPORTE_COWORK_RUNTIME_001_CIERRE.md` (firma Manus)
- `bridge/cowork_to_manus_PROMPT_AYUDA_COWORK_OBEDIENCIA_2026_05_11.md` (spec origen)
- `bridge/manus_to_cowork_SPRINT_MEGA_CIERRE_HOY_EJECUTOR1_TA3_2026_05_12.md` (Fase 1 activación T1+T4+T5)

---

## 5. Bloqueantes activos (orden por urgencia arquitectónica)

| # | Bloqueante | Magnitud | Bloquea |
|---|---|---|---|
| 1 | **CRUZ-001 implementación post-D6 verde** (Pieza 3 Anti-Dory cross-sesión Cowork) | sprint | Cierre Anti-Dory 4 piezas |
| 2 | **VERIFICADOR-001 implementación post-T6 mañana** (Pieza 4 Anti-Dory pre-emit blocking) | sprint | Cierre Anti-Dory 4 piezas |
| 3 | **Convergencia 3 Sabios MANUS-ANTI-DORY-003** (Pieza 5 intra-hilo Manus) | spec firma | Anti-Dory completo 5 piezas |
| 4 | **LA-FORJA D5.3 cost-per-thread fix** (issues #148 #149 #154) | mini-sprint | Dashboards SPEC v3.2 §7 con costos reales |
| 5 | **LA-FORJA D6 deploy Railway** (paralelo con D6 SMOKE VERDE) | deploy + smoke C2 | Producción LA-FORJA live |
| 6 | **Sprint 87 Pagos del Monstruo** | spec listo | Objetivo #1 al 100% |
| 7 | **Sprint MOBILE_1B A2UI Implementation** | 8 tareas firmadas | Renderizado dinámico kernel→app |

---

## 12. Drifts Detectados 2026-05-12 (Consolidado Maestro Manus)

[Sección preservada de v0.5 — referencia histórica intacta. Ver Git log commits previos para detalle. Drifts 008/010/011/013 RESUELTOS 12-may, drifts 001/007/009/012/014 abiertos.]

---

## 13. CASCADA MAGNA 2026-05-12 — 13 sprints cerrados + objetivo magno kernel asiste memoria persistente Cowork

[Sección preservada de v0.5. Persistida en `cowork_sesiones` UUID `3a04e11b-e610-4958-964e-4a709f3a5c61`. Ver Git history para detalle completo: §13.1 13 sprints + §13.2 PBA activado + §13.3 V25 + §13.4 drifts resueltos + §13.5 Reloj Suizo 8/8 + §13.6 QW1+QW2+QW3 Fase 1 activa.]

---

## §14 CASCADA POST-CIERRE MAGNA 2026-05-12 ~08:00-08:55 UTC

[Sección preservada de v0.5. PRs #115 #116 + MEGA-CIERRE-HOY + DSC-S-015/DSC-OPS-001/DSC-S-016/DSC-G-008 v3 + hallazgos kernel. Ver Git log para detalle.]

---

## §15 CASCADA MAGNA 2026-05-17/18 — Jornada magna 6 horas (MAGNA-CIERRE-002 en progreso)

**Sesión Cowork ~01:00-07:35 UTC, ~120 turnos.** Sesión más productiva binaria de la historia del Monstruo:
- 8 PRs mergeados (todos con audit Cowork DSC-G-008 v4 verde)
- 4 migrations prod aplicadas via MCP supabase-monstruo
- 2 DSCs magnos canonizados (DSC-G-013 v0.1 + DSC-LF-011) + 3 referenced (DSC-LF-008/009/010)
- 3 hilos Manus en paralelo activos
- 1 sprint S-EMBRION-009 cerrado funcionalmente (5/6 tareas)
- Cero rollbacks, cero F21 inadvertido

### §15.1 PRs mergeados HOY (8 total)

| # | PR | Sprint | Merge commit | Owner audit |
|---|---|---|---|---|
| 1 | #142 | S-EMBRION-009 T1 migration 0048 consumed_at | `f57850b9` | Cowork audit + apply prod + merge |
| 2 | #143 | S-EMBRION-009 T2+T3+T4 (código + 6 tests) | `129721b1` | Cowork audit + merge |
| 3 | #144 | H11 housekeeping `.gitignore` | `5b95738` | Manus E2 (Cowork body fix DSC-G-010) |
| 4 | #146 | AGENTS.md Regla Dura #10 doc-only PRs | `0b91891` | Manus E2 (auto bajo label `no-e2e-required` Opción C) |
| 5 | #147 | LA-FORJA-001 D5.2 stubs→repos Supabase | `dc79cb71` | Cowork audit + merge (+2 tickets follow-up #148 #149) |
| 6 | #150 | H4 OTelBridge LANGFUSE_HOST fallback removed | `26b5759c` | Cowork audit + merge |
| 7 | #151 | S-EMBRION-009 T5 backfill 0049 | `473dfa06` | Cowork audit + apply prod + merge |
| 8 | (PR #152+) | LA-FORJA D6 SMOKE pendiente | smoke verde branch `sprint/la-forja-001-d6-smoke` | Cowork audit 9/9 VERDE + autorización deploy |

### §15.2 Migrations prod aplicadas via MCP (4 total)

| # | Migration | Sprint | Aplicada por | Verificación post-apply |
|---|---|---|---|---|
| 1 | `0015_run_costs.sql` | H12 fix (tabla missing prod desde sprint olvidado) | Cowork via MCP | RLS + 3 indexes + 3 constraints + service_role_only policy ✅ |
| 2 | `0047_embrion_memoria_tipo_check_expand_vivos.sql` | H13 fix (4 tipos vivos código rechazados silente) | Cowork via MCP | 13 tipos en constraint + 4 INSERTs smoke pass + control negativo rechaza ✅ |
| 3 | `0048_embrion_memoria_consumed_at.sql` | S-EMBRION-009 T1 | Cowork via MCP | column TIMESTAMPTZ NULL + idx parcial WHERE consumed_at IS NULL ✅ |
| 4 | `0049_embrion_memoria_consumed_at_backfill.sql` | S-EMBRION-009 T5 | Cowork via MCP | 14 mensaje_alfredo backfilled (de 21 NULL) + 7 legítimos pendientes + 0 scope leak ✅ |

### §15.3 DSCs magnos canonizados HOY

#### DSC-G-013 v0.1 — DB↔Repo Coherence Gate (firmado T1 "firmo 5" 2026-05-18)

Path: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-G-013_db_repo_coherence_gate.md` (8.5KB quirúrgico).

**Hipótesis degradada post-convergencia 3 Sabios CON CAVEAT:** "Familia de drift pre-acción entre DB, repo, schema y código, con posible síntoma adicional de modelo mental desactualizado." (NO "3 capas estructurales" como v1 pre-Sabios decía).

- **Nivel A firmable** (pre-flight binario manual)
- **Nivel B → EXPERIMENTO T+14D** (automatización `tools/_coherence_gate.py` con métricas binarias)
- 7 limitaciones declaradas (L_C1-L_C7 incluyendo multi-branch + DB state out-of-band)
- Caveat doctrinal explícito: "Guardrail pre-acción. No patrón universal probado."

**3 veredictos Sabios verbatim preservados** en `bridge/veredictos_dsc_g_013/`:
- Opus 4.7 → 🟡 CON CAVEAT (3 ajustes técnicos)
- Perplexity Sonar T2-B → 🟡 CON CAVEAT (Atlas/Flyway/Liquibase referencia industria)
- GPT-5.5 Pro → 🟡 DEGRADADO (sesgo confirmatorio detectado, refactor magno)

**v1 archivado:** `_archived/DSC-G-013_v1_pre_sabios_2026_05_18.md`.

#### DSC-LF-011 — LA-FORJA-001 D5.2 persistencia stubs replaced

Path: `discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-011_d5_2_persistencia_stubs_replaced.md`.

5 decisiones magnas canonizadas:
1. Selector binario stub vs real por NODE_ENV (preserva 207 tests baseline)
2. ESM-first sin require dinámico (`await import()` lazy)
3. Anti-IDOR ensureThread zero data leak (doble `.eq()` filter)
4. Fail-soft binario en `routes/tutor.ts` (try/catch persistencia ortogonal a budget/LLM)
5. Drift P2 SPRINT_STATES TS↔SQL reconciliado binariamente (8/8 idéntico)

### §15.4 CLAUDE.md Paso 0.B canonizado (DSC-G-013 v0.1 Nivel A operacional)

Commit `a1dae1c1`. Antes de cualquier acción magna (`apply_migration`, INSERT con CHECK, `DROP/ALTER TABLE`, scope tactical N items), Cowork DEBE ejecutar coherence gate Nivel A pre-flight binario:
- `ls migrations/sql/ | tail -3` (próximo número libre)
- `SELECT version, name FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 3` (últimas registradas prod)
- `SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='<chk_name>'` (si involucra CHECK)

Si difieren → flag amarillo. Si divergencia confirmada → bloquear acción.

Latencia +2-5s por turno. **Nueva palabra clave T1: "Coherence Gate"** invoca pre-acción inmediato.

### §15.5 LA-FORJA-001 — 5 sprints cerrados acumulado

| Sprint | Status | DSC |
|---|---|---|
| D2.5 hardening | ✅ | DSC-LF-008 |
| D3.3 SSE migration AI SDK 6 | ✅ PR #133 mergeado | DSC-LF-008 |
| D4 OAuth + JWT | ✅ | DSC-LF-009 |
| D5.1 9 migraciones RLS | ✅ | DSC-LF-010 |
| D5.2 stubs→repos | ✅ PR #147 mergeado | DSC-LF-011 |
| **D6 SMOKE C1.C** | **🏛️ DECLARADO 2026-05-18** | propuesta DSC-G-014 CANARY_SMOKE_PROTOCOL |
| D6 DEPLOY Railway | 🟢 Manus E2 ejecutando paralelo | — |

### §15.6 Sprint S-EMBRION-009 (intra-loop Embrión H1 bucle infinito)

| Tarea | Status | PR | Apply prod |
|---|---|---|---|
| T1 migration 0048 | ✅ | #142 | ✅ MCP |
| T2 _mark_consumed | ✅ | #143 | N/A |
| T3 _detect_trigger filter | ✅ | #143 | N/A |
| T4 NO_RESPONDER pre-flight + 6 tests | ✅ | #143 | N/A |
| T5 backfill 0049 | ✅ | #151 | ✅ MCP (14 backfilled, 7 pendientes legítimos) |
| T6 verificación 24h Railway | 🟡 madurando ~mañana 06:30 UTC | — | — |

**Hallazgo magno binario:** 14 mensaje_alfredo backfilled = evidencia del bucle infinito histórico que existía pre-fix. `contribucion_sabio` importancia=9 perdida por meses (H13 fix simultáneo).

### §15.7 Anti-Dory 5 piezas — status consolidado

| Pieza | Status | Owner próxima movida |
|---|---|---|
| 1 cross-agente Manus | 🟢 D6 Railway flag ejecutando | Manus E1 (1h) |
| 2 MEMENTO calibration | ✅ vive prod | — |
| 3 CRUZ-001 cross-sesión Cowork | 🟢 firmada, espera D6 verde E1 | Manus E1 post-Pieza 1 |
| 4 VERIFICADOR-001 pre-emit blocking | 🟢 go-signal post-T6 mañana | Manus E2 |
| 5 MANUS-ANTI-DORY-003 intra-hilo | 🟡 draft v0.1 esperando 3 Sabios | Cowork + 3 Sabios |

### §15.8 Issues abiertos relacionados HOY

| # | Título | Severidad |
|---|---|---|
| #120 | Lint debt heredado 4,042 errores Ruff | P2 (no introducido HOY) |
| #145 | H15 ModuleNotFoundError tools rompe CI | P2 |
| #148 | LA-FORJA-D5.3-COST-PER-THREAD-001 | P2 (D5.2 follow-up) |
| #149 | LA-FORJA-D5.3-BUDGET-DOC-HEADER-FIX | P3 (D5.2 follow-up) |
| #154 | LA-FORJA-D5.3-ENSURE-THREAD-METADATA-001 | P3 (D6 SMOKE follow-up) |

**Agrupable D5.3 mini-PR:** #148 + #149 + #154 = 30min-3h total + audit Cowork lightweight.

### §15.9 MAGNA-CIERRE-002 — status final del día (en progreso)

| Pieza | Acción | Status |
|---|---|---|
| P1 | D6 Anti-Dory Railway flag bridge → Manus E1 | ✅ ejecutando |
| P2 | VERIFICADOR-001 go-signal → Manus E2 | ✅ esperando T6 |
| P3 | Spec MANUS-ANTI-DORY-003 v0.1 + 3 prompts Sabios | ✅ pusheado, esperando veredictos |
| P4-A | Update `_INDEX.md` (DRIFT-013) | ✅ commit `d476ca06` |
| P4-B | Update `COWORK_ESTADO_VIVO.md` (este §15) | ✅ ESTE DOC |
| P4-C | DSC-LF-011 firmado | ✅ commit `a1a05670` |
| P4-D | CLAUDE.md Paso 0.B Coherence Gate | ✅ commit `a1dae1c1` |
| Bonus #5 | Bridge Catastro reactivación | ⏳ prompt entregado a T1 |
| BONUS D6 SMOKE | Audit + autorización deploy LA-FORJA | ✅ commit `392341428` |

### §15.10 Deudas pendientes próxima sesión (post-MAGNA-CIERRE-002)

1. ⏳ Esperar bridge Manus E1 D6 Anti-Dory Railway flag verde → cerrar formalmente Pieza 1
2. ⏳ Esperar bridge Manus E2 D6 LA-FORJA DEPLOY done → frase canónica D6 LA-FORJA
3. ⏳ Esperar T6 S-EMBRION-009 verde 24h (~mañana 06:30 UTC)
4. ⏳ Esperar 3 veredictos Sabios MANUS-ANTI-DORY-003 (asincrónico)
5. ⏳ Catastro bridge reactivación (T1 pega prompt)
6. ⏳ Manus E2 mini-PR D5.3 LA-FORJA (#148 + #149 + #154 agrupable)
7. ⏳ Spec DSC-G-014 CANARY_SMOKE_PROTOCOL (Cowork autoría post-MAGNA-CIERRE)
8. ⏳ Update `COWORK_DECISIONES_VIVAS.md` con decisiones MAGNA-CIERRE-002 (próxima sesión, anti-Memento)

### §15.11 Lecciones binarias del día

1. **Rebase quirúrgico funciona mejor que rebase -i para scope-bleed.** Manus E2 hizo cherry-pick + force-with-lease en 5min cuando rebase -i habría sido más invasivo. Lección para futuro.
2. **Sabios adversariales rompen sesgo confirmatorio Cowork.** GPT-5.5 Pro detectó "3 capas estructurales" como over-claim cuando F#15 era síntoma operativo. Cowork integró sin defensividad.
3. **Cierre binario H13 + S-EMBRION-009 dependía del orden.** Apliqué 0047 H13 antes de mergear #143 S-EMBRION-009. Si hubiera ido al revés, INSERT `silencio_preverifier` habría fallado silente. Cero F21 reincidente solo por casualidad doctrinal.
4. **Paridad H1/H2 binaria como blueprint canary smoke.** L7.1 Manus E2 propone DSC-G-014. Mismo protocolo (snapshot pre-DELETE) sirve tanto para intervenciones quirúrgicas (H1) como pre-deploy (H2).

---

*Generado por Cowork 2026-05-10. v0.2 actualizada 2026-05-11 tras Sprint COWORK-RUNTIME-001. v0.3 actualizada 2026-05-12 tras Consolidado Maestro. v0.4 actualizada 2026-05-12 ~07:25 UTC tras cascada 13 sprints + QW1+QW2. v0.5 actualizada 2026-05-12 ~08:55 UTC tras MEGA-CIERRE-HOY + Reloj Suizo 8/8 + PR #115 + PR #116 + créditos P0. **v0.6 actualizada 2026-05-18 ~07:35 UTC tras jornada magna MAGNA-CIERRE-002 (8 PRs + 4 migrations + 2 DSCs magnos + LA-FORJA D6 SMOKE VERDE + 3 hilos Manus paralelos activos + cero rollbacks).** Sesión persistirá en `cowork_sesiones` al cierre de turnos.*
