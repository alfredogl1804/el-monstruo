# Cowork — Estado Vivo del Monstruo

**Propósito:** Snapshot operacional ACTUAL del Monstruo. Lo que está corriendo, lo que está en backlog, los bloqueantes. Documento volátil — se actualiza con frecuencia.

**Estado:** v0.3 — actualizado 2026-05-12 tras absorción del Consolidado Maestro de Manus.

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

*Generado por Cowork 2026-05-10. v0.2 actualizada 2026-05-11 tras cierre Sprint COWORK-RUNTIME-001 por Manus. v0.3 actualizada 2026-05-12 tras absorción del Consolidado Maestro de Manus (Cowork T2 con verificación binaria 8/9 confirmados + 1 drift evolucionado).*
