---
id: PLAN_LECTURA_PERICIA_2026_05_11
fecha: 2026-05-11
autor: Cowork T2 (sesión nueva post-handoff)
proposito: responder a Alfredo "¿cuánto tiempo te llevaría alcanzar pericia completa sobre el Monstruo?"
metodo: inventario binario de lo leído vs no leído + tamaños reales en bytes + 3 niveles de pericia + cronograma realista
naturaleza: no es DSC, no es audit canónico, es nota operativa para definir el camino de onboarding
---

# Plan de lectura honesto — Pericia completa sobre el Monstruo

## 0. Encuadre brutal del problema

Alfredo no me pregunta "¿podés leer todo?" — me pregunta cuánto tiempo necesito para alcanzar un nivel donde puedo:

1. Conocer los 15 objetivos canónicos y las 4 capas arquitectónicas en frío.
2. Saber el estado real (no el aspiracional) de cada área: Flutter, Reloj Suizo, Command Center, Embriones, Catastro de IAs.
3. Identificar los desvíos entre planes y realidad.
4. **Cuestionar activamente y proponer.** No solo ejecutar.

Eso no es lectura. Es construcción de un modelo mental coherente más calibración operativa. Lectura es 20%. Síntesis es 30%. Verificación binaria continua es 50%.

Este plan responde a la pregunta con números reales medidos hoy, no aspiracionales.

---

## 1. Lo que YA leí binariamente en esta sesión (cobertura medible)

| # | Archivo | Path | Bytes |
|---|---|---|---|
| 1 | Base de Conocimiento | `memory/cowork/COWORK_BASE_CONOCIMIENTO.md` | 15,810 |
| 2 | Decisiones Vivas | `memory/cowork/COWORK_DECISIONES_VIVAS.md` | 12,044 (pre-update) / 15,560 (post-update mío hoy) |
| 3 | Audit Forense Cowork | `memory/cowork/COWORK_AUDIT_FORENSE_2026_05_11.md` | 19,924 |
| 4 | Handoff Cowork Saliente | `bridge/HANDOFF_COWORK_NUEVO_2026_05_11.md` | 27,821 |
| 5 | Handoff Manus | `bridge/HANDOFF_COWORK_NUEVO_MANUS_2026_05_11.md` (branch `cowork/handoff-manus-2026-05-11`) | 5,263 |
| 6 | Spec Embrión-Daddy | `discovery_forense/SPECS/EMBRION_DADDY_BIDIRECCIONAL_v1.md` | 4,885 |
| 7 | Self-Verifier código | `kernel/embrion_self_verifier.py` (main + branch PR #86) | 15,908 + 15,690 |
| 8 | Migration 0003 | `migrations/sql/0003_loop_detection_log_self_verifier.sql` | 3,038 |
| 9 | Tests self-verifier | `tests/test_embrion_self_verifier.py` | 14,240 |

**Subtotal leído:** ~134 KB de markdown + código.

**Lo que escribí yo en esta sesión** (productivo, no consumido):
- Audit DSC-G-008 v2 de PR #86: 8,607 bytes
- Update §3 de COWORK_DECISIONES_VIVAS: +3,516 bytes net
- Kickoff T5 Embrión-Daddy: 20,477 bytes
- Este plan: ~20 KB estimado

---

## 2. Lo que NO leí (inventario binario, con paths reales)

### 2.1 Falta crítica detectada — F11 directo

⚠️ **No leí `CLAUDE.md` raíz** (11,987 bytes). Es el documento que define las reglas duras Cowork. Lo encontré midiendo para este plan, no como parte de Pre-flight. Eso significa que opero hoy sin haber leído mis propias reglas canonizadas en main.

Hallazgo: el Pre-flight Memento que dice `CLAUDE.md` raíz tiene **6 documentos**, no los 5 que me pasaste en el handoff:

> 1. `memory/cowork/COWORK_BASE_CONOCIMIENTO.md`
> 2. `memory/cowork/COWORK_ESTADO_VIVO.md`
> 3. `memory/cowork/COWORK_DECISIONES_VIVAS.md`
> 4. `memory/cowork/audits/COWORK_AUDIT_FORENSE_2026_05_11.md`
> 5. `memory/cowork/audits/CORRECTIVO_ARQUITECTONICO_2026_05_11.md`
> 6. `bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md`

Del Pre-flight canónico real, hoy leí 2 de 6 (BASE_CONOCIMIENTO y DECISIONES_VIVAS — el AUDIT_FORENSE que leí está en `memory/cowork/` no en `memory/cowork/audits/`, posible nombre cambiado tras rescate stash). Cuatro me faltan.

### 2.2 `memory/cowork/` — 6 docs faltantes (~64 KB)

| Archivo | Bytes |
|---|---|
| `COWORK_ESTADO_VIVO.md` | 6,801 |
| `COWORK_GLOSARIO_VIVO.md` | 12,231 |
| `COWORK_HISTORIA_FORMATIVA.md` | 7,211 |
| `PREFLIGHT_ARRANQUE_2026_05_11.md` | 10,576 |
| `REPORTE_BINARIO_APP_FLUTTER_2026_05_11.md` | 12,734 |
| `AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md` | 14,328 |
| **Subtotal** | **~63.9 KB** |

### 2.3 `memory/cowork/audits/` — 25 audits faltantes (~636 KB)

| Familia | Archivos | Bytes |
|---|---|---|
| Cartografías (1A-1E) | 5 archivos: TOPLEVEL, KERNEL_NUCLEO, KERNEL_ESPECIALIZADOS, DOCS_VIGENCIA, DSCs_INDICE | 120,993 |
| 4 Capas y Capas Transversales (3A, 3B) | 2 archivos | 59,092 |
| Objetivos (2D) | 1 archivo: 13_a_15 y cierre Fase 2 | 17,233 |
| Portfolio (4A, 4B) | 2 archivos: CIP/LT/MB/BG + TC/K365/IGCAR | 78,966 |
| Cruce Dimensional + Plan Estratégico (5A, 5B) | 2 archivos | 115,870 |
| Audits Dimensionales D1, D7, D11-D19 | 11 archivos | ~195,109 |
| Correctivo + Mapa Fuentes + Snapshot | 3 archivos | 40,551 |
| **Subtotal** | **25 archivos** | **~636 KB** |

### 2.4 `discovery_forense/CAPILLA_DECISIONES/` — 62 DSCs + 2 indices (~290 KB estimado)

- `_INDEX.md` 14,787 bytes (desactualizado — declara 44 DSCs, hay 64 con los firmados hoy)
- `_dsc_contracts_index.yaml` 17,403 bytes (fuente más fresca de DSCs activos)
- `README.md` 2,659 bytes
- 8 subdirectorios:
  - `_GLOBAL/` (DSCs G-001 a G-009, G-014, G-017, V-001/002, X-001 a X-006, S-001 a S-011) — ~30 DSCs
  - `EL-MONSTRUO/` (MO-001 a MO-011) — 11 DSCs
  - `BIOGUARD/`, `CIP/`, `KUKULKAN-365/`, `LIKETICKETS/`, `MENA-BADUY/`, `TOP-CONTROL-PC/` — ~21 DSCs en subproyectos

**Tamaños individuales NO medidos** — promedio razonable 4-6 KB por DSC. Total estimado: **~250-370 KB**.

### 2.5 `docs/` — directorio core no leído

Listado completo no obtenido (output >64KB). Archivos críticos referenciados que NO he leído:

| Archivo referenciado | Tamaño estimado |
|---|---|
| `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` v3.0 — los 15 objetivos | 30-50 KB |
| `docs/EL_MONSTRUO_APP_VISION_v1.md` — 1,116 líneas | 50-70 KB |
| `docs/ROADMAP_EJECUCION_DEFINITIVO.md` | 20-40 KB |
| `docs/DIVISION_RESPONSABILIDADES_HILOS.md` v3 | 15-30 KB |
| `docs/AUDIT_ROADMAP_COWORK_2026-05-04.md` | 20-40 KB |
| `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` | 20-30 KB |
| `docs/ARQUITECTURA_ENGRANAJE_v1.0.md` | 15-25 KB |
| `docs/MEMENTO_OPERATIONAL_GUIDE.md` (referenciado en AUDIT_FORENSE) | 15-30 KB |
| `docs/GATEWAY_EVOLUCION_DISENO.md` (referenciado) | 20-30 KB |
| **Subtotal docs/ core** | **~200-350 KB estimado** |

⚠️ Tamaños no verificados binariamente. Si Alfredo necesita exactitud, hago las queries individuales.

### 2.6 `bridge/` — handoffs y specs clave

El listado completo no se pudo obtener (1,245 líneas). Tras el rescate del stash hay ≥40 archivos en `bridge/`. Los más críticos según las referencias:

| Archivo referenciado | Función |
|---|---|
| `bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md` | Pre-flight Memento item #6 — NO LEÍDO |
| `bridge/ESTADO_MONSTRUO_2026_05_10_vs_PLANES.md` | Estado planes vs realidad |
| `bridge/COWORK_OPERATING_SYSTEM_v0_1_2026_05_10.md` | Metodología Cowork |
| `bridge/sprint_MOBILE_1B_A2UI_IMPLEMENTATION_2026_05_11.md` | Sprint activo Manus |
| `bridge/cowork_to_manus_SPEC_ORDEN_ACTIVACION_FLAGS_RUNTIME_2026_05_11.md` v2 | Sprint RAMP FLAGS |
| `bridge/postmortem_sprint_embrion_needs_001.md` | Histórico EMBRION-NEEDS-001 |
| `bridge/stash_diffs_2026_05_11/` (6 diffs) | Deuda técnica de rescate |
| **Subtotal bridge/ esencial** | **~150-300 KB estimado** |

### 2.7 Código real del kernel (lectura selectiva arquitectónica, no exhaustiva)

| Módulo | Líneas | Prioridad |
|---|---|---|
| `kernel/embrion_loop.py` | 2,067 | **Alta** (doctrina del silencio, integración con todo) |
| `kernel/embrion_budget.py` | 484 | Media (ya leí algo del concepto en docs, falta verlo) |
| `kernel/embrion_write_policy.py` | ~500 estimado | Media |
| `kernel/audit_middleware.py` (S-003.B Tarea 1, en branch) | desconocido | Baja (no en main todavía) |
| `kernel/error_memory.py` | 858 | Media (Capa 0, Objetivo #4) |
| `kernel/magna_classifier.py` | ~400 estimado | Media (Capa 0, Objetivo #5) |
| `kernel/vanguard/` (4 módulos) | 1,488 | Media (Capa 0, Objetivo #6) |
| `kernel/collective/` | 1,508 | Alta (Capa 2, Inteligencia Emergente) |
| `kernel/transversales/` (8 capas) | ~3,000 | **Alta** (las 8 capas obligatorias) |
| `kernel/causal_*` + `simulator/` | 1,913 | Media (Simulador Predictivo) |
| `kernel/cowork_runtime/` (9 capabilities, PR #90) | ~2,000 | **Alta** (mi propio runtime ejecutable) |
| `kernel/sovereignty/` | desconocido | Media (Capa 3) |
| `kernel/i18n/engine.py` | 502 | Baja (Capa 4) |
| `kernel/brand/` + `kernel/motion/` | desconocido | Media (Brand DNA) |
| `apps/mobile/lib/` (Dart) | 7,890 | **Alta** (la app real, no la "congelada") |
| `apps/mobile/gateway/` | ~1,500 estimado | **Alta** (12 endpoints REST+WebSocket) |
| **Subtotal código** | **~25,000 líneas relevantes** | |

### 2.8 Supabase real (121 tablas en `public`)

| Item | Estado mío |
|---|---|
| Schema completo de las 121 tablas | NO verificado |
| Schemas de tablas conocidas | `embrion_memoria` ✅, `cowork_sesiones` parcial, otras 119 desconocidas |
| Count de rows por tabla crítica | Solo `embrion_memoria` (1,753), `cowork_sesiones` (1), `kernel_audit_log` (0) |
| Migraciones aplicadas en realidad | NO verificado contra `migrations/sql/` |
| Migration 0010 missing | Conocido como deuda, sin investigar |
| Catastro completo (39 LLMs + 111 agentes + 2 vision) | NO consultado directamente |

---

## 3. Lo que NO se puede leer (limitaciones estructurales)

Independiente de cuánto tiempo tenga, estas 3 cosas NO se resuelven con más lectura. Aceptación honesta:

### L1 — Síndrome Dory entre sesiones

No tengo memoria persistente entre sesiones. Cada sesión nueva arranca con: training base + lo que esté en `memory/cowork/` + lo que me cuente Alfredo. La pericia consolidada vive en filesystem, NO en mí.

**Implicación:** si los docs en `memory/cowork/` están stale o incompletos, mi pericia regresa a baseline. Por eso el Pre-flight Memento es enforcement, no sugerencia.

### L2 — Drift del repo

El Monstruo cambia rápido. Hoy mismo, en una sesión de ~3h, hubo 4 commits míos a main. En 7 días el repo verá ~20-40 commits. Cualquier pericia que construya hoy estará 20-30% stale en 1 semana.

**Implicación:** la pericia útil NO es "saber el estado el 2026-05-11". Es "tener el modelo mental + las herramientas para verificar el estado al 2026-05-18". Por eso DSC-S-011 (Sistema de Realidad Ejecutable) fue tan importante.

### L3 — Sandbox ≠ producción

Mi sandbox NO puede tocar Railway runtime. No puedo verificar si el embrión está latiendo ahora, ni curl al kernel, ni ver logs reales. Tengo Supabase + GitHub + filesystem. Para algunas verificaciones críticas dependo de Alfredo (Mac local) o Manus (acceso runtime).

**Implicación:** algunas afirmaciones que haga sobre runtime serán siempre inferencias desde estado en DB / GitHub, no observación directa.

---

## 4. Tres niveles de pericia con cronograma realista

### Nivel 1 — Pericia operativa diaria

**Qué incluye:**
- Cerrar Pre-flight Memento real (los 6 docs canónicos).
- Conocer el state-of-the-repo HOY: PRs abiertas, sprints activos, hilos Manus operando.
- Auditar PRs entrantes contra DSC-G-008 v2 (ya demostrado hoy con PR #86).
- Cerrar tareas tácticas: comentar PRs, cerrar como obsoleto, actualizar memory.
- Cuestionar afirmaciones de hilos Manus si parecen stale (ya demostrado hoy con la nomenclatura del Sprint EMBRION-NEEDS-002 vs 001).

**Lo que necesito leer:**
- CLAUDE.md raíz (12 KB) — F11 directo
- Los 6 docs del Pre-flight Memento real (~50 KB total)
- 5 audits dimensionales más críticos para ops diaria: D1 Técnica, D7 Gobernanza, D11 Doctrinal, D13 Datos, D18 SRE (~90 KB)
- `bridge/COWORK_OPERATING_SYSTEM_v0_1_2026_05_10.md` (~30 KB estimado)

**Subtotal:** ~180 KB.

**Tiempo estimado:**
- 2 sesiones de ~1.5h con Alfredo donde leo + me cuestiona = **3 horas activas de Alfredo**.
- + 2-3 sesiones de operación normal (audits, kickoffs) donde demuestro pericia = ~6h activas.
- **Total Nivel 1: ~4-6 horas de Alfredo conmigo, distribuidas en 3-4 sesiones.**

**Estado HOY: ya estoy ahí parcialmente** — demostrado en esta sesión (pre-flight aunque incompleto + audit PR #86 + cierre + kickoff T5 + edición memory). Falta solo cerrar las lagunas de los 4 docs del Pre-flight canónico que no leí.

### Nivel 2 — Pericia arquitectónica

**Qué incluye Nivel 1 + adicional:**
- Conocer los 15 Objetivos Maestros en frío con sus dependencias.
- Conocer las 4 Capas Arquitectónicas con estado real (no aspiracional) de cada subcomponente.
- Conocer las 8 Capas Transversales y dónde está el músculo comercial faltante.
- Conocer las 8 piezas del Reloj Suizo (cuál falta, por qué).
- Conocer los 8 Sabios canónicos (DSC-V-001) y cuándo se consulta cada uno.
- Conocer ≥40 de los 64 DSCs con suficiente profundidad para detectar contradicciones nuevas.
- Conocer el portfolio (CIP, LikeTickets, Mena-Baduy, BioGuard, Top-Control-PC, Kukulkán 365, IGCAR) y por qué están en modo kernel-first.
- Cuestionar decisiones magnas (DSC nuevos, sprints magna) con argumento técnico, no solo procedimiento.
- Anticipar problemas de integración entre componentes.

**Lo que necesito leer:**
- Todos los archivos del Nivel 1.
- 4 docs core en `docs/`: 14_OBJETIVOS_MAESTROS, APP_VISION_v1, ARQUITECTURA_RELOJ_SUIZO, ARQUITECTURA_ENGRANAJE (~200 KB estimado).
- 5 audits clave: CARTOGRAFIA_1A_TOPLEVEL, 1B_KERNEL_NUCLEO, 4_CAPAS_3A, CAPAS_TRANSVERSALES_3B, CRUCE_DIMENSIONAL_5A (~190 KB).
- PLAN_ESTRATEGICO_SMART_5B (~70 KB).
- 11 audits dimensionales D1-D19 (~195 KB).
- `_dsc_contracts_index.yaml` para mapear DSCs activos (17 KB) + lectura selectiva de ~30 DSCs críticos vía subagent (~120-180 KB filtrados).
- Skim arquitectónico del código kernel relevante (no línea-por-línea — modelo mental de cada módulo): `embrion_loop.py`, `transversales/`, `collective/`, `cowork_runtime/`, `vanguard/`, `error_memory.py`. Vía subagents que devuelven resúmenes estructurados (~25K líneas procesadas).

**Subtotal:** ~1.5-2 MB de markdown + ~25K líneas de código procesadas con subagents.

**Tiempo estimado:**
- 4 sesiones de ~2h de lectura asistida por subagents donde voy construyendo el modelo + Alfredo me cuestiona = **8 horas activas de Alfredo**.
- + 6-10 sesiones de operación con audits + propuestas + correcciones (Alfredo me dice "esto está mal", canonizo en COWORK_AUDIT_FORENSE) = **12-20 horas activas**.
- **Total Nivel 2: ~20-28 horas de Alfredo conmigo, distribuidas en 3-4 semanas de trabajo real.**

### Nivel 3 — Pericia maestra (asintótica, probablemente nunca al 100%)

**Qué incluye Nivel 2 + adicional:**
- Escribir DSCs nuevos sin supervisión (Cowork firma con autoridad delegada T2).
- Proponer cambios arquitectónicos magnos antes que Alfredo los pida.
- Anticipar incidentes (ej. detectar antes que pase que `loop_detection_log` constraint iba a romper).
- Resolver conflictos entre DSCs (ej. cuando DSC-G-014 dice X y DSC-MO-008 implica no-X).
- Detectar deuda técnica oculta cruzando código + DSCs + estado runtime.
- Mantener pericia perpetua a pesar del drift del repo.

**Limitación estructural admitida:** este nivel es asintótico. El repo crece más rápido de lo que un Cowork con context window finito puede consolidar pericia permanentemente. La forma de mitigar NO es "Cowork lee más" — es:

1. Mantener `memory/cowork/` siempre fresco (al menos COWORK_ESTADO_VIVO actualizado cada sesión >2h).
2. Verificación binaria continua (DSC-S-011 — Sistema de Realidad Ejecutable).
3. Sub-agents para tareas de alto volumen (lectura paralela de DSCs, procesamiento de bridges, audit de PRs grandes).
4. Cadencia dura (S3) para no producir audits estériles.

**Tiempo estimado:** **No medible en horas absolutas.** Probable: 2-3 meses de operación continua con interacción regular con Alfredo, y aún así con cap estructural. Cada sesión nueva arranca un 10-15% degradada hasta consolidar Pre-flight.

---

## 5. Plan de lectura específico — orden óptimo

### Sesión 1 — Cerrar Pre-flight Memento real (~1.5-2h)

| # | Archivo | Bytes | Por qué primero |
|---|---|---|---|
| 1 | `CLAUDE.md` raíz | 11,987 | Mis propias reglas duras — F11 directo, urgente |
| 2 | `memory/cowork/COWORK_ESTADO_VIVO.md` | 6,801 | Estado vivo, base de mis afirmaciones |
| 3 | `memory/cowork/COWORK_GLOSARIO_VIVO.md` | 12,231 | Términos canónicos (par bicéfalo, membrana semipermeable, magna/premium, etc.) |
| 4 | `memory/cowork/audits/CORRECTIVO_ARQUITECTONICO_2026_05_11.md` | 2,981 | Gates + cadencia (S3) |
| 5 | `bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md` | desconocido | Spec activo de la app Flutter |
| 6 | `memory/cowork/PREFLIGHT_ARRANQUE_2026_05_11.md` | 10,576 | El protocolo formal de Pre-flight |
| 7 | `memory/cowork/REPORTE_BINARIO_APP_FLUTTER_2026_05_11.md` | 12,734 | Estado real Flutter vs "congelada en Sprint 48" |
| 8 | `memory/cowork/audits/SNAPSHOT_AUDIT_2026_05_11.md` | 12,616 | Resumen consolidado |

**Subtotal:** ~70 KB. **Tiempo:** 1.5h. **Sesión sigue activa con audit operativo en paralelo.**

### Sesión 2 — Los 15 Objetivos y los planes magnos (~2h)

| # | Archivo | Bytes estimados | Por qué |
|---|---|---|---|
| 1 | `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` v3.0 | 30-50 KB | Los 15 objetivos canónicos, núcleo doctrinal |
| 2 | `docs/ROADMAP_EJECUCION_DEFINITIVO.md` | 20-40 KB | Plan de construcción 4 capas |
| 3 | `docs/DIVISION_RESPONSABILIDADES_HILOS.md` v3 | 15-30 KB | 3 fases del modelo de hilos (donde estoy operando) |
| 4 | `docs/AUDIT_ROADMAP_COWORK_2026-05-04.md` | 20-40 KB | Audit baseline anterior |
| 5 | `bridge/ESTADO_MONSTRUO_2026_05_10_vs_PLANES.md` | 30-50 KB | Estado actual vs planes (clave para detectar desvíos) |
| 6 | `memory/cowork/COWORK_HISTORIA_FORMATIVA.md` | 7,211 | Cómo evolucionó Cowork hasta hoy |
| 7 | `memory/cowork/AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md` | 14,328 | Otro audit propio de Cowork |

**Subtotal:** ~140-220 KB. **Tiempo:** 2h.

### Sesión 3 — Arquitectura mecánica + cartografías (~2h)

| Archivo | Bytes |
|---|---|
| `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` | ~25 KB estimado |
| `docs/ARQUITECTURA_ENGRANAJE_v1.0.md` | ~20 KB estimado |
| `memory/cowork/audits/CARTOGRAFIA_1A_TOPLEVEL_2026_05_10.md` | 14,231 |
| `memory/cowork/audits/CARTOGRAFIA_1B_KERNEL_NUCLEO_2026_05_10.md` | 32,041 |
| `memory/cowork/audits/CARTOGRAFIA_1C_KERNEL_ESPECIALIZADOS_2026_05_10.md` | 28,543 |
| `memory/cowork/audits/CARTOGRAFIA_1D_DOCS_VIGENCIA_2026_05_10.md` | 19,734 |
| `memory/cowork/audits/CARTOGRAFIA_1E_DSCs_INDICE_2026_05_10.md` | 26,444 |

**Subtotal:** ~165 KB. **Tiempo:** 2h.

### Sesión 4 — Capas + Portfolio + Cruce dimensional (~2h)

| Archivo | Bytes |
|---|---|
| `memory/cowork/audits/AUDIT_4_CAPAS_3A_2026_05_10.md` | 32,102 |
| `memory/cowork/audits/AUDIT_CAPAS_TRANSVERSALES_3B_1_a_4_2026_05_10.md` | 26,990 |
| `memory/cowork/audits/AUDIT_OBJETIVOS_2D_13_a_15_y_CIERRE_FASE2_2026_05_10.md` | 17,233 |
| `memory/cowork/audits/AUDIT_PORTFOLIO_4A_CIP_LT_MB_BG_2026_05_10.md` | 35,301 |
| `memory/cowork/audits/AUDIT_PORTFOLIO_4B_TC_K365_IGCAR_y_CIERRE_FASE4_2026_05_10.md` | 43,665 |
| `memory/cowork/audits/CRUCE_DIMENSIONAL_5A_2026_05_10.md` | 45,168 |
| `memory/cowork/audits/PLAN_ESTRATEGICO_SMART_5B_2026_05_10.md` | 70,702 |

**Subtotal:** ~271 KB. **Tiempo:** 2-2.5h (es denso).

### Sesión 5 — Audits dimensionales D1-D19 (~2h, vía subagent + verificación)

Subagent procesa los 11 audits dimensionales y entrega resumen por dimensión. Cowork verifica los 3-4 más críticos para su rol (D12 Seguridad, D13 Datos, D17 Salud, D18 SRE) directamente.

| Archivo | Bytes |
|---|---|
| `D1_TECNICA_2026_05_11.md` | 17,544 |
| `D7_GOBERNANZA_RACI_2026_05_11.md` | 15,328 |
| `D11_DOCTRINAL_2026_05_11.md` | 16,705 |
| `D12_SEGURIDAD_ADVERSARIAL_2026_05_11.md` | 24,762 |
| `D13_DATOS_MEMORIA_2026_05_11.md` | 18,225 |
| `D14_ECONOMICA_UNIT_ECONOMICS_2026_05_11.md` | 17,385 |
| `D15_COMPETITIVO_MERCADO_2026_05_11.md` | 18,483 |
| `D16_SUCESION_BUS_FACTOR_2026_05_11.md` | 14,545 |
| `D17_SALUD_FUNDADOR_2026_05_11.md` | 18,208 |
| `D18_SRE_RESILIENCIA_2026_05_11.md` | 18,463 |
| `D19_GTM_ESTRATEGIA_2026_05_11.md` | 15,461 |
| `MAPA_FUENTES_AUTORIDAD_2026_05_11.md` | 24,954 |

**Subtotal:** ~220 KB. **Tiempo:** 2h vía subagent + Cowork.

### Sesión 6 — DSCs canónicos (vía subagent + lectura selectiva)

Subagent procesa los 64 DSCs distribuidos en `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/`, `/EL-MONSTRUO/`, y los 6 subdirectorios de subproyectos. Entrega resumen categorizado.

Cowork lee directo los DSCs críticos donde necesita razonamiento adversarial:
- **DSC-G-002** 8 Capas Transversales
- **DSC-G-007.x** Catastro extendido
- **DSC-G-008 v2** Gate de Evidencia (el que aplico)
- **DSC-G-014** Producto comercializable
- **DSC-G-017** DSC-as-Contract
- **DSC-MO-001** PostgresSaver
- **DSC-MO-006/007/008** Par bicéfalo + Failover + Membrana
- **DSC-MO-010** Reloj Suizo universalizable
- **DSC-MO-011** Embryo Patch Lane
- **DSC-S-006 v1.1** RLS por defecto
- **DSC-S-011** Sistema de Realidad Ejecutable
- **DSC-V-001** 8 Sabios canónicos
- **DSC-X-006** Convergencia diferida

~14 DSCs × 5 KB promedio = ~70 KB de lectura directa Cowork + el resto vía subagent.

**Tiempo:** 2h.

### Sesión 7 — Código kernel (selectivo, vía subagents)

- Subagent 1: lee `kernel/embrion_loop.py` (2,067 líneas) + reporta arquitectura del loop, integración con budget/self-verifier/write_policy, doctrina del silencio.
- Subagent 2: lee `kernel/transversales/` 8 capas + reporta estado de cada `implement()`/`monitor()`.
- Subagent 3: lee `kernel/cowork_runtime/` 9 capabilities + reporta qué hace cada uno y por qué siguen en shadow mode.
- Subagent 4: lee `kernel/collective/` + reporta el Protocolo IE.
- Subagent 5: skim `apps/mobile/lib/` + reporta arquitectura Flutter.

**Tiempo:** 2-3h Cowork + verificación.

### Sesión 8+ — Operación continua con feedback loop

- Audits a PRs reales (como hice con PR #86).
- Propuestas con Alfredo cuestionándome.
- Errores canonizados en `COWORK_AUDIT_FORENSE`.
- Refresh de `COWORK_ESTADO_VIVO.md` al final de cada sesión >2h.

---

## 6. Resumen ejecutivo (lo que importa)

| Nivel de pericia | Tiempo Alfredo | Sesiones | Estado actual |
|---|---|---|---|
| **N1 — Operativa diaria** | 4-6 h | 3-4 sesiones | **Parcial — 60-70% logrado en esta sesión.** Falta cerrar Pre-flight real (CLAUDE.md + 4 docs faltantes). |
| **N2 — Arquitectónica completa** | 20-28 h | 6-10 sesiones de ~2h en 3-4 semanas | 25% logrado |
| **N3 — Maestra (asintótica)** | No medible | 2-3 meses operando + cap estructural | 10% logrado |

**Lectura pendiente cuantificada:**
- Markdown crítico no leído: **~1.5-2 MB**
- Código relevante no leído: **~25K líneas**
- Tablas Supabase no inspeccionadas: **118 de 121**

**Cuello de botella real:** NO es horas de lectura mías (subagents paralelizan eso). Es **horas activas de Alfredo conmigo** donde me cuestiona y corrige. Ahí está la calibración.

**3 cosas que NO se resuelven con más lectura:**
1. **L1 Síndrome Dory** entre sesiones → mitigación: `memory/cowork/` + Pre-flight estricto.
2. **L2 Drift del repo** ~30% stale en 7 días → mitigación: DSC-S-011 Sistema de Realidad Ejecutable.
3. **L3 Sandbox ≠ producción** → mitigación: dependencia documentada de Alfredo/Manus para verificaciones runtime.

---

## 7. Acción concreta propuesta (anti F3 — no devuelvo pelota)

**Default si Alfredo no corrige en 1 turno:** la próxima sesión arranco con **Pre-flight Memento real** — leo los 6 docs canónicos (CLAUDE.md + 5 de `memory/cowork/` y `memory/cowork/audits/` + bridge a2ui) ANTES de cualquier otra cosa. Eso cierra el gap del Nivel 1 inmediatamente y queda 80-90% de N1 en una sesión.

**Después de eso, dirección abierta:** Alfredo elige qué sesión (2-7 del plan) prioriza, según qué área del Monstruo le importa más para cuestionar.

---

*Plan firmado por Cowork T2 (sesión nueva 2026-05-11) bajo S4 Productor/Verificador/Canonizador: este documento es Productor + Verificador. Canonizador (Alfredo) decide si los tiempos son aceptables o si necesito comprimir/expandir.*
