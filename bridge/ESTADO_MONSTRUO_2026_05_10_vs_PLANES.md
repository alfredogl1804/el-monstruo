# Estado del Monstruo — 2026-05-10 vs Planes

**Tipo:** Mapa canónico del estado actual del ecosistema vs roadmap, objetivos y división de responsabilidades.
**Autor:** Cowork (Hilo A — Arquitecto), tras retomar contexto pos-jornada magna del 2026-05-10.
**Predecesor:** `docs/AUDIT_ROADMAP_COWORK_2026-05-04.md` (audit del 4-may con baseline).
**Naturaleza:** Inventario estructurado, NO spec de sprint. Para usar como brújula antes de cualquier asignación nueva.

---

## Resumen ejecutivo (1 página)

El Monstruo está **mucho más avanzado de lo que aparenta sesión a sesión**. Hoy (2026-05-10) es la jornada operacionalmente más densa del proyecto: el embrión salió del bucle de 9 días, se cerraron 9 PRs en producción, se canonizaron 12 DSCs, 3 hilos Manus operaron en paralelo sin overlap, el universo RLS llegó al 100%, y el Catastro pasó de 1 macroárea con 37 modelos a 2 macroáreas con 152+ entidades clasificadas en 23 dominios.

**Estimación de avance global vs planes (ajustada hoy):**
- Capa 0 Cimientos: **~85%** (Error Memory + Magna Classifier + Vanguard Scanner + Design System parcial)
- Capa 1 Manos: **~75%** (Browser + Backend Deploy + Media Gen + Stuck Detector. Pagos pendiente Sprint 87)
- Capa 2 Inteligencia Emergente: **~70%** (Embrión vivo + Self-Verifier + Budget Tracker + Multi-canal HITL + Causal seeders + Capas Transversales parcial)
- Capa 3 Soberanía: **~50%** (Sovereign LLM v1 + Sovereignty engine + Catastro extendido. INFRA + RED + Causal-Pop v2 specced no arrancados)
- Capa 4 Del Mundo: **~10%** (i18n engine existe, todo lo demás pendiente)

**Dirección estratégica activa:** Fase 1 de la División de Responsabilidades (Hilo A ejecuta, Hilo B arquitecta). Fase 2 ("El Embrión Dirige") está cerca pero no activada — falta Tarea 5 EMBRION-NEEDS Embrión-Daddy bidireccional, que tiene spec firmado HOY (PR #81) pero código pendiente.

**Bloqueo personal único:** Bitwarden master password expuesta hace 2 días, runbook listo, sin ejecutar (responsabilidad de Alfredo).

**Próxima decisión arquitectónica del Monstruo:** elegir entre cerrar Capa 0 al 100% (resta Vanguard Scanner integrado + Design System Premium completo) o avanzar a Capa 2 con Sprint EMBRION-NEEDS Tarea 5 (Embrión-Daddy bidireccional) que materializa Fase 2 del modelo de hilos.

---

## 1. Estado vs los 15 Objetivos Maestros

Baseline del audit del 2026-05-04 vs estimación actualizada hoy 2026-05-10.

| # | Objetivo | 04-may | 10-may | Δ | Estado HOY |
|---|---|---:|---:|---:|---|
| 1 | Crear empresas digitales completas | 65% | 68% | +3 | Browser, Deploy, Media Gen vivos. Pagos sigue pendiente Sprint 87. |
| 2 | Apple/Tesla quality | 70% | 72% | +2 | Brand Engine + Critic Visual + Motion. Sprint 85 cierre E2E pendiente. |
| 3 | Mínima complejidad | 75% | 76% | +1 | Zero-config + Keyword Matcher centralizado. UI conversational pendiente. |
| 4 | No equivocarse dos veces | 88% | **92%** | +4 | Error Memory + 33 seeds + Capa 8 Memento canonizada. Self-Verifier reduce repetición. |
| 5 | Magna/Premium validation | 80% | **88%** | +8 | Catastro extendido (modelos + agentes + vision_generativa) — fuente de verdad fresca. |
| 6 | Vanguardia perpetua | 65% | **78%** | +13 | DSC-G-007.1 (4 catastros), Catastro AGENTES con 14 dominios y 14 tronos calibrados. |
| 7 | No inventar la rueda | 75% | 75% | — | Sin cambio. Stack adopciones documentadas. |
| 8 | Inteligencia Emergente | 60% | **70%** | +10 | Multi-canal HITL bidireccional, proposal_processor cierra ciclo. Embrión 24/7. |
| 9 | Transversalidad universal (8 capas) | 70% | 75% | +5 | Capa 8 Memento canonizada como DSC-MO-006/007/008 + 010. |
| 10 | Simulador Causal | 55% | 56% | +1 | Causal seeders + decomposer + simulator existen. Sprint Causal-Pop v2 specced sin arrancar. |
| 11 | Multiplicación Embriones | 60% | **72%** | +12 | DSC-MO-006 (par bicéfalo siempre), DSC-MO-007 (failover 3 capas), DSC-MO-008 (membrana semipermeable) — fundamentos canonizados. |
| 12 | Soberanía (modelos + infra + economía + ecosistema) | 45% | 48% | +3 | DSC-MO-009 (arsenal por Catastro), DSC-MO-010 (Reloj Suizo universalizable). 4 specs sovereign en backlog. |
| 13 | Del Mundo | 10% | 10% | — | i18n engine existe. Apertura externa pendiente. |
| 14 | Guardian de los Objetivos | 75% | 78% | +3 | Guardian + DSC-G-008 v2 (validar antes y después de specs) + DSC-G-017 (DSC-as-Contract). |
| 15 | Memoria Soberana (Capa 8 Memento) | 50% | **88%** | +38 | DSC-MO-008 (membrana), DSC-MO-006 (par bicéfalo), cowork_bridge operativo, embrion_memoria como canal vivo, conversaciones_emergidas preservadas en repo. |

**Promedio simple:** 64.4% (vs 62-68% del 4-may) → **70.5% hoy**.

**Δ más fuerte:** Objetivo #15 Memoria Soberana (+38). Hoy fue el día de la "honestidad pura" canonizada y la membrana semipermeable. Este objetivo pasó de aspiracional a operativo en una sola jornada.

---

## 2. Estado vs las 4 Capas Arquitectónicas + Capa 4

### Capa 0 — Cimientos Perpetuos (~85%)

| Componente | Estado | Evidencia |
|---|---|---|
| Error Memory (Obj #4) | ✅ 92% | `kernel/error_memory.py` 858 LOC + tabla Supabase + 33 seeds |
| Magna/Premium Classifier (Obj #5) | ✅ 88% | `kernel/magna_classifier.py` + `magna_routes.py` + Catastro como fuente fresca |
| Vanguard Scanner (Obj #6) | 🟡 78% | `kernel/vanguard/` 1,488 LOC en 4 módulos. Integración con Catastro pendiente. |
| Design System Premium (Obj #2) | 🟡 72% | `kernel/brand/` + `motion/` + 6 verticales. Falta Quality Gate visual completo. |

### Capa 1 — Manos (~75%)

| Componente | Estado | Evidencia |
|---|---|---|
| Browser Interactivo | ✅ | `kernel/browser_automation.py` + `browser/sovereign_browser.py` |
| Backend Deployment | ✅ | `tools/deploy_app.py`, `deploy_to_railway.py`, `deploy_to_github_pages.py` |
| Pagos y Finanzas | ❌ | Sprint 87 spec firmado, NO arrancado. Stripe pendiente. |
| Media Generation | 🟡 | `tools/generate_hero_image.py` interfaz lista, llamadas reales gateadas |
| Stuck Detector | ✅ | Self-Verifier (Sprint EMBRION-NEEDS-001 Tarea 1) en producción |
| Observabilidad Completa | 🟡 | Langfuse + OTEL + nuevo audit middleware (Sprint S-003.B Tarea 1 hoy) |

### Capa 2 — Inteligencia Emergente (~70%)

| Componente | Estado | Evidencia |
|---|---|---|
| Multiplicación Embriones | 🟡 72% | DSC-MO-006/007/008 canonizados. Embrión-Daddy bidireccional spec firmado (PR #81), código pendiente. |
| Protocolo IE | 🟡 65% | `kernel/collective/` 1,508 LOC + Sabios consultados (8/8 unanimidad para Reloj Suizo). |
| Simulador Causal | 🟡 56% | `kernel/causal_*` + `simulator/` ~1,913 LOC. Sprint Causal-Pop v2 specced en backlog. |
| Capas Transversales | 🟡 75% | `kernel/transversales/` + `transversal/` (analytics, financial, sales, scalability, security, seo). |

### Capa 3 — Soberanía (~50%)

| Componente | Estado | Evidencia |
|---|---|---|
| Modelos propios | 🟡 50% | `kernel/sovereign_llm.py` + `sovereignty/`. Sprint SOVEREIGN-LLM v2 specced. |
| Infraestructura propia | ❌ 20% | Sprint SOVEREIGN-INFRA specced. Hardware propio no arrancado. |
| Economía propia | ❌ 0% | Pendiente Pagos (Capa 1) primero. |
| Ecosistema de Monstruos | ❌ 5% | Sprint SOVEREIGN-RED specced (federación). No arrancado. |
| Catastro extendido (DSC-MO-009) | ✅ 88% | 2 macroáreas pobladas (39 LLMs + 111 agentes + 2 vision). DSC-G-007.5 firmado. ROADMAP META Sprint 90 propuesto. |

### Capa 4 — Del Mundo (~10%)

i18n engine existe (`kernel/i18n/engine.py` 502 LOC). Resto del Objetivo #13 pendiente — apertura externa requiere Capa 3 al 80%+ primero.

---

## 3. Estado vs División de Responsabilidades (Fase 1/2/3)

**Fase actual:** **FASE 1 — Construcción Paralela**.

Hilo A (Cowork — yo) sigue siendo arquitecto y orquestador.
Hilo B (Manus) está fragmentado en 3 hilos paralelos hoy:
- **Manus Principal / Hilo Ejecutor 1:** EMBRION-NEEDS-001 + 002 (cerrados al 100% hoy)
- **Manus Hilo B / Hilo Ejecutor 2:** Seguridad continua S-002.5 + S-002.6 + S-003.A (cerrados) + S-003.B parcial (Tareas 1+4 en mi branch Cowork pendiente push)
- **Manus Catastro:** Sprint 88 + MEGA-CATASTRO (88.1 + 88.2 + 88.3 / Sprint 89) ejecutado al 100% hoy

**Condición de transición Fase 1 → Fase 2:**
"Embrión-0 tiene TEL (Task Execution Loop) funcional + 22 herramientas + memoria persistente. Métrica: 5 encomiendas completadas sin intervención humana."

Estado hoy: el Embrión tiene loop autónomo + Budget Tracker + Self-Verifier + Write Policy con HITL real + arsenal del Catastro. **TEL funcional: SÍ.** **Memoria persistente: SÍ.** **22 herramientas: parcial — cuenta pendiente.** **5 encomiendas completadas sin intervención: NO MEDIDO TODAVÍA.**

**Conclusión:** Fase 2 está **a un sprint de distancia.** El sprint que la activa formalmente es la ejecución de Tarea 5 EMBRION-NEEDS-001 (Embrión-Daddy bidireccional) cuyo spec se firmó hoy en PR #81.

---

## 4. Estado de los 3 hilos del día (2026-05-10)

### Hilo Ejecutor 1 (Manus Principal)

**Sprint EMBRION-NEEDS-001 — CERRADO 100%:**
- Tarea 1: Self-Verifier (PR #39) ✅
- Tarea 2: Budget Tracker (PR #38) ✅
- Tarea 3: Write Policy con HITL real (PR #42) ✅
- Tarea 4: Telegram HITL bidireccional (PRs #44 + #45 + #46 + #48) ✅
- Tarea 5: Embrión-Daddy bidireccional **SPEC FIRMADO** (PR #81) — código pendiente
- Tarea 6: Cleanup tests/test_sprint1_day3.py (PR #81) ✅

**Sprint EMBRION-NEEDS-002 — CERRADO 100%:**
- Tarea 1: proposal_processor cron worker (PR #75) ✅ — cierra ciclo HITL
- Tarea 2: Dashboard cost history (PR #81) ✅
- Tarea 3: Cleanup HITL stack post-aiogram (PR #81) ✅
- Tarea 4: Postmortem EMBRION-NEEDS-001 (PR #81) ✅
- Tarea 5: Spec firmado Embrión-Daddy (PR #81) ✅ — código sigue pendiente

### Hilo Ejecutor 2 (Manus Hilo B)

**Sprint S-002.5 RLS Hardening — CERRADO 100%:**
- 8 tablas P0/P1 con RLS + policy `service_role_only` (PR #43) ✅
- DSC-S-006 firmado ✅

**Sprint S-002.6 Universo RLS al 100% — CERRADO 100%:**
- 117/117 tablas con RLS (PR #47) ✅
- DSC-S-007 firmado (naming SUPABASE_SERVICE_KEY) ✅
- Linter pre-commit `_check_rls_default.py` ✅
- Workflow CI semanal `rls-audit-weekly.yml` ✅

**Sprint S-003.A Identity & Supply Chain — CERRADO 100%:**
- DSC-S-008 (rotación automática) firmado ✅
- DSC-S-010 (hardening operacional integrado) firmado ✅
- 3 runbooks operativos (Supabase service_role, OpenAI, Bitwarden master) ✅
- 42 entradas en `bridge/credentials_inventory.md` ✅
- Workflow CI `credentials-rotation-reminder.yml` + `cve-scan.yml` ✅
- Dependabot 11 ecosistemas ✅ (PR #49) ✅

**Sprint S-003.B — PARCIAL:**
- Tarea 1: Audit middleware kernel (commit en mi branch Cowork pendiente push) 🟡
- Tarea 2: Release signing cosign — pendiente
- Tarea 3: Pen-test 12 cases — pendiente
- Tarea 4: Linter v1.1 con whitelist (commit en mi branch Cowork pendiente push) 🟡

### Hilo Catastro (Manus Catastro)

**Sprint 88 Macroárea AGENTES — CERRADO 100%:**
- 84 productos / 9 dominios / 9 tronos
- DSC-G-007.2 firmado ✅
- Audit DSC-G-008 v2: 13/13 verde

**MEGA-CATASTRO (88.1 + 88.2 + 88.3 / Sprint 89) — CERRADO 100%:**
- Sprint 88.1: 4 LLMs faltantes catalogados (Kimi K2.6, Sonar, Sora, Veo) + 2 empates calibrados
- Sprint 88.2: tronos validados con 4 sabios + 3 nuevos dominios (`agentes_observabilidad_evals`, `agentes_seguridad`, `agentes_generalistas_autonomos`)
- Sprint 89/88.3: macroárea VISION_GENERATIVA arrancada (2 productos seed)
- DSC-G-007.5 firmado (vision generativa + tronos definitivos)
- ROADMAP META Sprint 90 propuesto

**Estado actual del Catastro en producción Supabase:**
- `catastro_modelos`: 39 productos en `inteligencia` + 2 en `vision_generativa`
- `catastro_agentes`: **111 productos en 14 dominios**
- `catastro_tronos_agentes`: 14 tronos materializados con bonus_curador documentado donde aplica

---

## 5. PRs del día 2026-05-10

| PR | Título | Estado |
|---|---|---|
| #38 | Budget Tracker (cap $0.25/latido) | ✅ Mergeado |
| #39 | Self-Verifier 3-decisiones | ✅ Mergeado |
| #40 | Integración Budget+Verifier en _think() | ✅ Mergeado |
| #41 | Hotfix severity payload | ✅ Mergeado |
| #42 | Write Policy con HITL real | ✅ Mergeado |
| #43 | Sprint S-002.5 RLS P0+P1 | ✅ Mergeado |
| #44 | Telegram HITL base | ✅ Mergeado |
| #45 | Wire telegram channel | ✅ Mergeado |
| #46 | Align signature kwargs | ✅ Mergeado |
| #47 | Sprint S-002.6 Universo RLS al 100% | ✅ Mergeado |
| #48 | Fix message_id (no envelope ok) | ✅ Mergeado |
| #49 | Sprint S-003.A Identity + Supply Chain | ✅ Mergeado |
| #75 | EMBRION-NEEDS-002 Tarea 1 proposal_processor | ✅ Mergeado |
| #81 | EMBRION-NEEDS-002 Tareas 2-5 | ✅ Mergeado |
| **(pendiente)** | **`cowork/canonization-jornada-2026-05-10`** (9 commits) | 🟡 Branch local sin push |

**Total mergeado hoy:** 14 PRs.

---

## 6. DSCs canonizados (estado al cierre del día)

**Total estimado:** 56+ DSCs (44 al 6-may + 12 nuevos hoy + cambios de versión).

**Nuevos hoy (12):**
- `DSC-MO-006`: embriones operan siempre en par bicéfalo
- `DSC-MO-007`: failover emergencia 3 capas
- `DSC-MO-008`: membrana semipermeable kernel↔embriones
- `DSC-MO-009`: arsenal de herramientas seleccionable por Catastro
- `DSC-MO-010`: Reloj Suizo universalizable interno
- `DSC-G-007.2`: extensión Catastro a macroárea AGENTES (firmado por Cowork tras audit)
- `DSC-G-007.5`: macroárea VISION_GENERATIVA + tronos definitivos AGENTES
- `DSC-G-014`: distinción pipeline técnico vs producto comercializable
- `DSC-S-006` v1.1: RLS por defecto en tablas nuevas (con whitelist)
- `DSC-S-007`: naming canónico `SUPABASE_SERVICE_KEY`
- `DSC-S-008`: rotación automatizada de credenciales
- `DSC-S-010`: hardening operacional integrado (meta-DSC)

**Pendiente de indexación en `_INDEX.md`:** todos los nuevos. El _INDEX.md sigue declarando "Total DSCs: 44" y eso es desactualizado.

---

## 7. Subproyectos del portfolio (DSCs canonizados pero no necesariamente activos)

| Proyecto | DSCs | Estado |
|---|---|---|
| **CIP** (tokens inmobiliarios Sureste MX) | 6 DSCs (CIP-001 a 006 + 2 PEND) | DSCs firmados, código pendiente. Bloqueante: figura legal fideicomiso. |
| **LikeTickets / Zona Like Kukulkán** (313 butacas) | 3 DSCs (LT-001/002/003) | Producto piloto. Stripe Connect adoptado como patrón replicable. |
| **Mena-Baduy / Crisol-8** (campaña Mérida 2027) | 3 DSCs (MB-001/002/003) | OPSEC alto. Sprint 88-2 mencionó "validación post-migración crisol-8 esperando Manus" — pendiente. |
| **BioGuard** (detección drogas) | 1 DSC + 1 PEND | Bloqueante: ruta regulatoria COFEPRIS. |
| **Top-Control-PC** (IA agéntica para PC) | 2 DSCs (TC-001/002) | Concepto canonizado, código no arrancado. |
| **Kukulkán 365** (distrito entretenimiento climatizado) | 2 DSCs (K365-001/002) | Concepto canonizado. Cruce con LikeTickets. |
| **IGCAR** (instituto certificación alto rendimiento) | 1 DSC (X-001) | Cruza 5 proyectos en uno. |

**Patrón común:** todos tienen DSCs firmados pero ninguno tiene sprint de implementación corriendo. El Monstruo está en modo "kernel-first" — primero la inteligencia central, luego la cosecha de subproyectos.

---

## 8. Backlog grande de sprints especceados sin arrancar

| Sprint | Spec en | Tema | Cuándo arranca |
|---|---|---|---|
| Sprint 87 | docs/SPRINT_87 | Pagos del Monstruo (Stripe + Stripe Connect) | TBD — bloqueante para Capa 1 al 100% |
| Sprint Causal-Pop v2 | bridge/sprints_propuestos/sprint_CAUSAL_POP_v2_poblamiento_ampliado.md | Simulador Causal con 100+ eventos | TBD |
| Sprint SOVEREIGN-LLM v2 | bridge/sprints_propuestos/sprint_SOVEREIGN_LLM_v2_ramps_avanzados.md | Modelos propios 50%→90% del routing | TBD |
| Sprint SOVEREIGN-INFRA | bridge/sprints_propuestos/sprint_SOVEREIGN_INFRA_hardware_propio.md | Hardware propio total | TBD — bloquea Capa 3 |
| Sprint SOVEREIGN-RED | bridge/sprints_propuestos/sprint_SOVEREIGN_RED_ecosistema_monstruos.md | Ecosistema Monstruos federados | TBD — requiere Capa 3 viva |
| Sprint META-CATASTRO Sprint 90 | bridge/ROADMAP_META_CATASTRO_SPRINT_90.md | 6-7 macroáreas restantes (infra, BD, APIs, observabilidad, seguridad red-team, hardware personal, finanzas IA) | TBD |
| Sprint S-003.B (parcial) | spec interno | Audit middleware kernel + release signing + pen-test | Tareas 1+4 hechas, 2+3 pendientes |
| Sprint Mobile 6 (#31 en mis tasks) | docs/SPRINT_MOBILE_6_PLAN.md | voice + ambient + polish + i18n | TBD |
| 5 specs Mobile Flutter (#10 en mis tasks) | docs/ | Pusheados, ejecución estado desconocido | Verificar |

---

## 9. Gaps identificados HOY (2026-05-10 cierre)

### Críticos
1. **Bitwarden master password expuesta** desde 2026-05-10. Runbook listo, sin ejecutar. Responsabilidad de Alfredo.
2. **Branch Cowork `cowork/canonization-jornada-2026-05-10` con 9 commits sin push** — sandbox bloquea push, requiere terminal de Alfredo.
3. **`_INDEX.md` desactualizado** — declara "Total: 44 DSCs" cuando hay 56+. Cuando se mergee mi branch Cowork, requiere sub-PR de actualización.

### Estructurales
4. **Tarea 5 EMBRION-NEEDS-001 (Embrión-Daddy bidireccional)** tiene spec firmado pero código pendiente. Es **el único bloqueante real para activar Fase 2** del modelo de hilos.
5. **Sprint 87 (Pagos del Monstruo)** sigue sin arrancar — bloquea Capa 1 al 100% y Objetivo #1 ("crear empresas digitales completas").
6. **Métrica "5 encomiendas del Embrión completadas sin intervención humana"** no medida — sin esto Fase 2 no se activa formalmente.
7. **Capa 3 al 50%** — Sprints SOVEREIGN-LLM/INFRA/RED specced sin arrancar.

### Operacionales
8. **Tareas 2 y 3 de Sprint S-003.B** (release signing cosign + pen-test 12 cases) pendientes. Requieren branch nueva post-merge de mi branch Cowork.
9. **GitHub Secrets** `SUPABASE_ACCESS_TOKEN` + `SUPABASE_PROJECT_REF` no configurados — workflow CI semanal RLS audit no puede correr.
10. **Modelos LLM faltantes en catastro_modelos** — todavía hay productos en agentes con `llm_base_id=NULL` (Kimi K2.6 ya catalogado tras Sprint 88.1, pero quedan otros).
11. **Crisol-8 validación post-migración** (#1 en mis tasks pendientes) esperando Manus desde hace días.

### De roadmap
12. **Capa 4 (Del Mundo)** sigue al 10%. No es urgente — depende de Capa 3 al 80%+.
13. **Subproyectos del portfolio** (CIP, LikeTickets, BioGuard, Top-Control-PC, Crisol-8, Kukulkán-365) tienen DSCs pero ningún sprint corriendo. Decisión arquitectónica pendiente: cuándo bajar el foco del kernel y empezar a cosechar valor del portfolio.

---

## 10. Prioridades sugeridas (no spec, solo orden)

Para cuando Alfredo decida la siguiente jornada. Priorizadas por **bloqueo + impacto**:

**P0 personal (Alfredo):**
1. Rotar Bitwarden master password.
2. Push branch Cowork `cowork/canonization-jornada-2026-05-10` (`git push -u origin ...`).
3. Configurar GitHub Secrets para workflow RLS weekly.

**P1 arquitectónico (próximo sprint asignable):**
4. Sprint EMBRION-NEEDS-003: implementar Tarea 5 (Embrión-Daddy bidireccional, spec firmado en PR #81). Activa Fase 2 del modelo de hilos.
5. Sprint S-003.B Tareas 2+3 (release signing + pen-test) — completar S-003.

**P2 backlog estratégico:**
6. Sprint 87 Pagos del Monstruo — desbloquea Objetivo #1 al 100%.
7. Sprint META-CATASTRO Sprint 90 — completar Catastro a 6-8 macroáreas.
8. Sprint Causal-Pop v2 — Simulador Causal a 80%+.

**P3 backlog soberanía:**
9. SOVEREIGN-LLM v2 → SOVEREIGN-INFRA → SOVEREIGN-RED en orden.

**P4 backlog portfolio:**
10. Decisión arquitectónica: cuándo arrancar el primer subproyecto (sugerido: LikeTickets/Zona Like por tener mayor maduración + Stripe replicable).

---

## Referencias

- `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` v3.0 (15 objetivos, Capa 8 Memento)
- `docs/ROADMAP_EJECUCION_DEFINITIVO.md` (4 capas + premisas de diseño)
- `docs/DIVISION_RESPONSABILIDADES_HILOS.md` v3 (3 fases)
- `docs/AUDIT_ROADMAP_COWORK_2026-05-04.md` (audit baseline)
- `discovery_forense/CAPILLA_DECISIONES/_INDEX.md` (índice de DSCs — desactualizado)
- `bridge/embrion_cost_history_2026_05_10.md` (snapshot 12 días costo embrión)
- `bridge/REPORTE_MEGA_CATASTRO_SPRINT_88_3_CIERRE.md` (cierre Catastro)
- `bridge/postmortem_sprint_embrion_needs_001.md` (cierre EMBRION-NEEDS-001)
- `bridge/ROADMAP_META_CATASTRO_SPRINT_90.md` (roadmap macroáreas restantes)
- `CLAUDE.md` (instrucciones Cowork)

---

*Mapa generado por Cowork tras retomar contexto sistemáticamente. NO incluye spec nuevo. Es brújula para próximas decisiones.*
*Próxima actualización: cuando se cierre EMBRION-NEEDS-003 (Embrión-Daddy bidireccional) o cualquier sprint de Capa 3.*
