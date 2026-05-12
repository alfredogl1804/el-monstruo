# Cowork — Estado Vivo del Monstruo

**Propósito:** Snapshot operacional ACTUAL del Monstruo. Lo que está corriendo, lo que está en backlog, los bloqueantes. Documento volátil — se actualiza con frecuencia.

**Estado:** v0.4 — actualizado 2026-05-12 ~07:25 UTC tras cascada de 13 sprints cerrados + objetivo magno HOY canonizado (kernel asiste memoria persistente Cowork).

**Cuándo actualizar:** después de cada sesión Cowork-Alfredo de >2h o cuando un sprint cambia de estado.

---

## 1. Snapshot global (resumen 1 línea)

**Monstruo al ~71%** (vs 70.5% del 10-may). Diferencial: **runtime ejecutable de obediencia Cowork canonizado en código** vía Sprint COWORK-RUNTIME-001 cerrado por Manus el 2026-05-11. Embrión vivo + HITL bidireccional + Universo RLS al 100% + Catastro 14 dominios + App Flutter avanzada (v0.1.0+1, 7,890 LOC, 22 commits) + Cowork ya no depende de su propia memoria para no empujar a Alfredo a pausar — depende de `kernel/cowork_runtime/pre_response_hook.py` que intercepta cada respuesta y bloquea suggest-pause sin advance score. Capas Transversales con código pero integraciones externas huecas. Sin sprint comercial corriendo.

**⚠️ NOTA DE CORRECCIÓN 2026-05-11 (mantener):** La frase "App Flutter congelada en Sprint 48" que estaba aquí hasta hoy era **falsa fantasma desde el 30-abril**. Sprint 48 fue solo uno de los hitos del 30-abr; después hubo Sprints 42/43/45 + 4 commits más en 2026-05-02. Corrección hecha por Cowork tras audit binario del Hilo Ejecutor Manus que demostró estado real con `git log`, `find`, `wc -l` y `grep` ejecutables.

**⚠️ NOTA NUEVA 2026-05-11 (Sprint COWORK-RUNTIME-001 cerrado):** Cowork pidió a Manus que construyera infraestructura ejecutable para enforzar las 22 reglas que Cowork mismo canonizaba y luego ignoraba. Manus cerró el sprint con 140/140 tests, 9 capabilities (T1-T8 + M9 Telegram veto), PR #90 mergeado en commit c0ee52309365ca375f939480651d3fbb599568eb. Todos los flags arrancan en `enabled=false` (shadow mode) — activación deliberada y reversible.

**Frase canónica del cierre:** *"El runtime de Cowork ya no depende de la memoria de Cowork. La doctrina ahora es código que se ejecuta, no texto que se lee."*

---

## 2. Estado por Capa Arquitectónica

| Capa | Estado | Bloqueantes inmediatos |
|---|---|---|
| Capa 0 Cimientos | ~85% | Vanguard Scanner integración con Catastro pendiente. Design System Quality Gate pendiente. |
| Capa 1 Manos | ~75% | **Sprint 87 Pagos NO arrancado.** Stripe + Stripe Connect pendientes. Bloquea Objetivo #1. |
| Capa 2 IE | ~72% | **Rotor del Reloj Suizo NO localizado.** Embrión-Daddy bidireccional spec firmado, código pendiente. **Runtime de obediencia Cowork ya canonizado en código (T1 MAGNA).** |
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
| T1 | Pre-response hook (intercept + suggest-pause regex + advance gate) | `kernel/cowork_runtime/pre_response_hook.py` | `COWORK_HOOK_ENABLED=true` | Shadow mode |
| T2 | Detector semántico (Companion Agent) | `kernel/cowork_runtime/semantic_detector.py` | `COWORK_SEMANTIC_ENABLED=true` | Shadow mode |
| T3 | Advance score calculator | `kernel/cowork_runtime/advance_score.py` | siempre activo en evaluación | Live |
| T4 | Persistencia sesiones a Supabase | tabla `public.cowork_sesiones` + writer | `COWORK_SESSION_PERSIST=true` | Migración aplicada |
| T5 | Pre-flight memento enforcer | `kernel/cowork_runtime/preflight.py` | `COWORK_PREFLIGHT_REQUIRED=true` | Shadow mode |
| T6 | Antipattern catalog F1-F22 enforced | `kernel/cowork_runtime/antipatterns.py` | `COWORK_ANTIPATTERN_ENFORCE=true` | Shadow mode |
| T7 | CLI `cowork_guardian` validator | `tools/cowork_guardian.py` | uso manual / CI | Live (no flag) |
| T8 | Test harness 140 casos | `tests/cowork_runtime/` | siempre activo en CI | Live |
| M9 | Veto Telegram channel (Alfredo bloquea Cowork desde su teléfono) | `kernel/cowork_runtime/telegram_veto.py` | `COWORK_VETO_TELEGRAM=true` | Shadow mode |

**Reportes auditables:**
- `bridge/manus_to_cowork_REPORTE_COWORK_RUNTIME_001_CIERRE.md` (firma Manus)
- `bridge/cowork_to_manus_PROMPT_AYUDA_COWORK_OBEDIENCIA_2026_05_11.md` (spec origen)

**Pendiente de Cowork ahora:** decidir orden de activación de flags en producción (acción #3 del cierre Manus) y soltar próximo spec para Hilo Ejecutor.

---

## 5. Bloqueantes activos (orden por urgencia arquitectónica)

| # | Bloqueante | Magnitud | Bloquea |
|---|---|---|---|
| 1 | **Rotor del Reloj Suizo** | Pensamiento + implementación nueva | Capa 2 IE al 100%. Autonomía sostenida. |
| 2 | **Embrión-Daddy bidireccional** (PR #81 spec, código pendiente) | Implementación | Activación de Fase 2 modelo de hilos |
| ~~3~~ | ~~**App Flutter Cara Completa**~~ | ~~75-150 min total~~ | ~~Interfaz primaria del Monstruo~~ — **CORREGIDO 2026-05-11**: app YA avanzada. Bloqueante real ahora es Sprint MOBILE_1B A2UI Implementation (firmado, no arrancado). |
| 4 | **Capa Transversal con integraciones reales** (Google Ads, LinkedIn, HubSpot wireado, Apollo/Clay) | Multiple sprints | Capacidad comercial real |
| 5 | **Sprint 87 Pagos del Monstruo** | Spec listo | Objetivo #1 al 100%. Cualquier subproyecto comercial. |
| 6 | **Decisión orden activación flags COWORK-RUNTIME** (T1→T2→...→M9 vs paralelo, qué ambiente primero, qué criterios para flip) | Spec corto | Encender el runtime ejecutable que Manus dejó listo en shadow mode |
| 7 | **Sprint MOBILE_1B A2UI Implementation** | 8 tareas firmadas | Renderizado dinámico kernel→app. EmpresaResultCard, LeadCard, ContenidoCard. |

---

## 12. Drifts Detectados 2026-05-12 (Consolidado Maestro Manus)

**Fuente:** `bridge/manus_to_cowork_CONSOLIDADO_MAESTRO_UNIVERSO_MONSTRUO_2026_05_12.md` (SHA-256 `719d0c19328f81ad4820050ec88777bb0cabc48e374e117f9289768756d75a08`, 160 LOC, 9,782 bytes) + `FUENTE_1_DOCTRINAL` (SHA `3fe8da58…8c41f`, 319 LOC).

**Verificación binaria fresca ejecutada por Cowork T2 el 2026-05-12 tras absorción:** 8/9 DRIFTs confirmados exactos, 1/9 drift evolucionado.

| ID | Componente | Doctrina/Handoff | Realidad fresca 2026-05-12 | Gravedad | Acción inmediata |
|---|---|---|---|---|---|
| DRIFT-001 | Objetivos Maestros | ROADMAP dice 13, nombre archivo dice "14" | **15** verificados en `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` líneas 42, 100, 139, 185, 248, 295, 342, 389, 422, 521, 574, 617, 662, 718, 823 | Alta | Renombrar archivo a `_15_OBJETIVOS_` o canonizar alias |
| DRIFT-007 | Universo RLS | Handoff 120/120 | **125/125** (5 tablas nuevas en 24h, RLS automática mantenida) | Baja | Documentar las 5 tablas nuevas en `DECISIONES_VIVAS §7` |
| DRIFT-008 | Latido autónomo | Acuse 11-may ordenó restaurar cada 6h | **1 latido en 7 días** — handler NO restaurado | **Crítica** | Reparar `kernel/embrion_scheduler.py` (Deuda #2 §6) |
| DRIFT-009 | Catastro agentes | Handoff 111 | **98** confirmado | Media | Actualizar `BASE_CONOCIMIENTO §9` + `HANDOFF` |
| DRIFT-010 | Cowork runtime sesiones | Sprint COWORK-RUNTIME-001 "cerrado con persistencia" | **1 row** (sólo smoke seed `ed7bfd59`). Shadow mode. | Alta | Activar flags T4 + decisión orden activación |
| DRIFT-011 | scheduled_tasks | Acuse 11-may ordenó cleanup destructivo | **17,700** (Manus reportó 17,695 → +5 rows en ~5h. Drift evolucionado activo) | **Crítica** | Cleanup destructivo urgente (Deuda #1 §6) |
| DRIFT-012 | Inventario DSCs | Handoff declara 64 | **62 archivos físicos**. 2 commits faltantes | Media | Buscar los 2 DSCs faltantes y/o actualizar `_INDEX.md` |
| DRIFT-013 | Git stashes | Handoff menciona "6 diffs preservados" | **27 stashes** acumulados | **Crítica** | Auditar stashes pendientes (Deuda #3 §6) |
| DRIFT-014 | Biblias v7.0_95 | Handoff no las menciona en core | **10 biblias** en `monstruo_biblias/` | Alta | Decidir si pertenecen al universo (subir a §1 de BASE_CONOCIMIENTO o marcar paralelo) |

**Exclusiones explícitas T1 (Alfredo 2026-05-11/12):**
- ❌ Guillermo Cortés NO parte del Monstruo
- ❌ Investigación Forense NO parte del Monstruo

**Plan A→B→C consolidado §5 del Consolidado:**
- Sprint 87 — A Ejecución Autónoma E2E (1-2 días)
- Sprint 88 — B Multiplicación 9 Embriones (3-5h)
- Sprint 89 — C Activación Guardian Autónomo (2-4h)
- Sprints 90-92 Transversales · 93 verificación 7 días · 94 Ticketlike · 95+ Stripe DIFERIDO

**6 deudas técnicas críticas §6 del Consolidado:**
1. Cleanup destructivo `scheduled_tasks` (Crítica DRIFT-011)
2. Restaurar `latido_autonomo` cada 6h (Crítica DRIFT-008)
3. Limpieza 27 git stashes (Crítica DRIFT-013)
4. Activar Fase 2 — implementar Tarea 5 EMBRION-NEEDS-001 (Embrión-Daddy, PR #81 spec firmado)
5. Decidir orden activación 9 flags COWORK-RUNTIME (shadow → enforce)
6. Rotar master password Bitwarden (runbook listo) — **NOTA:** decisión T1 explícita 11-may dice "no rotamos claves hasta que termine el avance" — este punto queda pausado por T1

---

## 13. CASCADA MAGNA 2026-05-12 — 13 sprints cerrados + objetivo magno kernel asiste memoria persistente Cowork

**Sesión Cowork 2026-05-12 ~01:00-07:25 UTC ~85 turnos.** Persistida en `cowork_sesiones` UUID `3a04e11b-e610-4958-964e-4a709f3a5c61`.

### 13.1 Sprints cerrados (cascada secuencial)

| # | Sprint | Hilo | Commit/PR | Estado |
|---|---|---|---|---|
| 1 | D-3 latido autónomo | Ejecutor 2 | PR #104 + `807eda4a` | ✅ Mergeado |
| 2 | D-4 schedulers zombies fix | Ejecutor 1 | `9d67f51` | ✅ Mergeado |
| 3 | D-5 restore overdue | Ejecutor 1 | `63767ef` + `f6ed3be` | ✅ Mergeado |
| 4 | D-6 anti-reentrada + timeout | Ejecutor 1 | `1a50e3e` + `132688f` | ✅ Mergeado |
| 5 | PAR_BICEFALO_001 (3 PRs Brand Engine Embrión 2) | Ejecutor 2 + Perplexity merge | PRs #108/#109/#111 | ✅ Mergeado |
| 6 | GUARDIAN-AUTONOMO-001 | Ejecutor 2 | PR #112 + `1b5ce49` | ✅ Mergeado, baseline `total_score_pct=65.51%` |
| 7 | STASHES-FORENSIC-001 | Catastro | `457bf6c` matriz 28×7 | ✅ Cerrado (DRIFT-013 resuelto) |
| 8 | PR #106 cleanup scheduled_tasks | Ejecutor 2 | `2bdbb6c` | ✅ Mergeado (DRIFT-011 resuelto, 17710→6 rows) |
| 9 | Sprint 89 v2 Opción B (vistas semánticas DSC-G-007.1 + suppliers) | Ejecutor 1 | `1bcb2c0` + `a384df0` | ✅ Mergeado |
| 10 | CATASTRO-A v2 (audit 3 vistas + 30 suppliers DSC-V-002) | Catastro | `cb07e45` | ✅ Cerrado VERDE 3/3 |
| 11 | MOBILE-REALIGNMENT-001 | Ejecutor 1 | PR #114 + `c0f2846` | ✅ Mergeado con 4 caveats P3 T2-B verbatim |
| 12 | ROTOR-001 (pieza Reloj Suizo) | Ejecutor 2 | PR #113 + `43b26755` | ✅ Mergeado con override CI rojo defendible 3 condiciones T2-B |
| 13 | COWORK-MEMORIA-AUTONOMA QW1+QW2 (objetivo magno HOY) | Cowork T2-A | `12bacecb` CLAUDE.md + row Supabase | ✅ Canonizado |

### 13.2 PBA (Protocolo Par Bicéfalo Activo) ACTIVADO

Commit canonización: `d4e81d0`. Operacionaliza DSC-MO-006 con **7 triggers obligatorios** donde Cowork DEBE consultar a Perplexity T2-B antes de afirmar/actuar:
1. Causalidad operativa (post-V25 grave detectado)
2. Apply migraciones SQL prod
3. Merge PRs write-risky kernel
4. DSCs nuevos / derogación
5. Decisiones magnas
6. Specs nuevos
7. Override spec firmado

**PBA aplicado exitosamente 3 veces HOY:** PR #112 GUARDIAN + PR #114 MOBILE + PR #113 ROTOR. T2-B detectó: 4 caveats P3 PR #114 + F2 menor narrativa PR #113. Cowork mergeó con caveats verbatim sin ocultar.

### 13.3 V25 grave reconocido sin suavizar

CLAIM-C: Cowork fabricó causalidad sobre migration 0020 (mezcló Sprint T5 con PAR_BICEFALO_001 sin grep previo). **Perplexity T2-B verificación independiente detectó la alucinación**. Documentado verbatim en `embrion_memoria` `efd71b9f-4622-49ac-82b6-13a0feefa250` importancia 10. Alfredo T1 activó PBA permanente como guardrail estructural.

### 13.4 Drifts del Consolidado Maestro — RESUELTOS HOY

| DRIFT | Estado pre-HOY | Estado post-HOY |
|---|---|---|
| DRIFT-008 latido autónomo | Crítico (1 latido 7 días) | ✅ Resuelto — D-3/D-4/D-5/D-6 cascada + tasks revivieron |
| DRIFT-011 scheduled_tasks | Crítico (17,700 rows saturándose) | ✅ Resuelto — PR #106 cleanup destructivo (17,710→6 rows) + UNIQUE constraint |
| DRIFT-013 git stashes | Crítico (27-28 stashes acumulados) | ✅ Resuelto — Hilo Catastro produjo matriz 28×7 (commit `457bf6c`) con clasificación canónica DROP/APPLY/CHERRY_PICK/REVIEW; ejecución pendiente firma T1 |
| DRIFT-010 cowork_sesiones | Crítico (1 row smoke) | 🟡 Parcial — sesión Cowork actual seedeada en row `3a04e11b` + commit canonización CLAUDE.md Paso 0; flags `enabled=false` shadow siguen pendientes |

### 13.5 Piezas Reloj Suizo (8 total)

| # | Pieza | Estado |
|---|---|---|
| 1 Resorte | `kernel/embrion_budget.py` | ✅ Existe |
| 2 **Escape** | Sin código | 🟡 **ESCAPE-001 spec firmado borrador** (commit `f7aa7fd`) + kickoff Ejecutor 2 (commit `3c9a5c3`) — esperando firma T1 + audit T2-B PBA |
| 3 Áncora | `kernel/embrion_scheduler.py` | ✅ Existe + fortalecida D-3/D-4/D-5/D-6 |
| 4 Volante | `kernel/embrion_loop.py` | ✅ Existe (doctrina del silencio) |
| 5 Espiral | Sin código | ❌ Sprint posterior |
| 6 **Rotor** | `kernel/rotor/` | ✅ **PR #113 mergeado HOY** (cap $30/día firmado T1 + recharge_mainspring 5min) |
| 7 Rubíes/Caché | `kernel/response_cache.py` | 🟡 Parcial — verificar cobertura |
| 8 Remontoir | Sin código | ❌ Sprint posterior |

### 13.6 Objetivo magno HOY canonizado — kernel asiste memoria persistente Cowork

Bajo orden T1 explícita `vamos a ponernos de objetivo usar hoy la memoria persistente del monstruo para que te asista y te sirva`:

- **QW1 ✅** sesión Cowork actual persistida en Supabase `cowork_sesiones` row `3a04e11b-e610-4958-964e-4a709f3a5c61` con 8 violaciones detectadas + 10 palabras clave Alfredo + 6 correctivos recibidos + **16 deudas pendientes para próxima sesión** + resumen lecciones + sprint activo + kernel_version
- **QW2 ✅** CLAUDE.md canonizado commit `12bacecb` con **Paso 0 Pre-flight Memento extendido** (CLI `session_memory pre-flight` antes de markdown docs) + Paso N cierre sesión + Paso M opcional pre-response hook decisiones magnas
- **QW3 ⏳** Audit + merge PR #110 Pre-Response Hook OBSERVE-ONLY autónomo del kernel — bloqueado por conflict G6 con CLAUDE.md de QW2; **rebase Perplexity en proceso**

### 13.7 Hilos activos al momento del refresh (07:25 UTC)

| Hilo | Estado |
|---|---|
| Ejecutor 1 | Standby activo TA-TD + TE cleanup `_tmp_notif.md` (commit `90e57eb`) |
| Ejecutor 2 | ESCAPE-001 PA/PB/PC preparatorias + espera firma T1 + audit T2-B PBA |
| Catastro | S-CONTRATOS-001 COMPLETO T1-T6 (override post Sabios 2+3 commit `59adf28`) arrancando |
| Perplexity T2-B | **Rebase PR #110** post-conflict G6 con QW2 |
| Cowork T2-A | Orquestador con PBA proporcional aplicado 3 veces exitosas + post-V25 reconocido |

### 13.8 Deudas T1 pendientes acumuladas (16 en `cowork_sesiones`)

1. T7 smoke binario PR #114 Mac Alfredo (CRÍTICO post-caveats T2-B widget_test debilitado)
2. Activar Telegram T3 GUARDIAN (chat_id + ventana + rate-limit)
3. Activar `BRAND_ENGINE_ENABLED=true` shadow canary Railway
4. Canonizar DSC-S-015 (scheduler respeta next_run de restore)
5. Canonizar DSC-OPS-001 (UPDATE manual datos prod requires bridge report)
6. Canonizar DSC anti-fabricación-causalidad-sin-grep (lección V25)
7. Cleanup `_tmp_notif.md` (delegado a Ejecutor 1 standby TE)
8. Ticket MOBILE-DSC-G-004-PHASE-2 (class identifiers)
9. Firmar spec ESCAPE-001 + 6 pulse_intervals defaults T2
10. Aplicar migration 0023_rotor_activity_log a Supabase prod (anti-IMMUTABLE check post-V25)
11. Encolar sprint LINT_DEBT_PURGE (84 N818 + 26 semgrep + sqlglot)
12. Resolver DRIFT-010 orden flags COWORK-RUNTIME-001 9 capabilities shadow
13. Hilo Catastro arrancando S-CONTRATOS-001 (monitoreo)
14. Hilo Ejecutor 1 standby activo (monitoreo)
15. Hilo Ejecutor 2 ESCAPE-001 preparatorias (monitoreo)
16. Perplexity T2-B LIBRE post-rebase PR #110

---

*Generado por Cowork 2026-05-10. v0.2 actualizada 2026-05-11 tras cierre Sprint COWORK-RUNTIME-001 por Manus. v0.3 actualizada 2026-05-12 tras absorción del Consolidado Maestro de Manus. **v0.4 actualizada 2026-05-12 ~07:25 UTC tras cascada de 13 sprints cerrados HOY + objetivo magno kernel asiste memoria persistente Cowork canonizado (QW1+QW2). Sesión persistida Supabase `cowork_sesiones` row `3a04e11b-e610-4958-964e-4a709f3a5c61`.***
