---
id: bridge_sprints_propuestos_INDEX
fecha: 2026-05-11
autor: Cowork T2 (Sprint NOMENCLATURA-001 bajo autorización T1 directa)
proposito: catálogo autoritativo de sprints en bridge/sprints_propuestos/ + estado real verificado binariamente
estado: vigente — supersede al README.md de 2026-05-06 como fuente autoritativa
---

# Catálogo de Sprints — Inventario autoritativo 2026-05-11

## 0. Nota magna sobre nomenclatura

Este `_INDEX.md` resuelve el patrón antipatrón sistémico detectado en audit `CARTOGRAFIA_3A` §2 H1 (dos Sprints 87 distintos sin renombrar) y replicado en otros casos. **A partir de hoy, este archivo es la fuente autoritativa** de qué sprints existen, en qué estado, y dónde vive su spec.

El `README.md` previo (2026-05-06, autor "Cowork Hilo A") queda como histórico narrativo del orden de ejecución original. Sigue siendo válido como contexto histórico, pero NO debe usarse para decidir qué sprint arrancar — para eso, usar este `_INDEX.md`.

---

## 1. Sprints YA MERGEADOS en `main` (no son "propuestos" — están cerrados)

Estos specs **deben moverse fuera de `bridge/sprints_propuestos/` o archivarse** en próximo sprint de housekeeping. Mientras tanto, este índice los marca como histórico.

| Spec | Estado real | Merge commit | Notas |
|---|---|---|---|
| `sprint_88_cierre_v1_producto.md` | ✅ **MERGEADO** (Sprint 88.1+88.2+88.3) | commits `2e0b2a5` + `005ddf7` + posteriores | Cerrado como `🏛️ v1.0 PIPELINE TÉCNICO FUNCIONAL` (DSC-G-014 distinción canonizada; NO se declaró PRODUCTO COMERCIALIZABLE) |
| `sprint_S001_security_hardening.md` | ✅ **MERGEADO** | DSCs S-001 a S-010 firmados | Gitleaks + trufflehog + rotación + RLS implementados |
| `sprint_S002_6_rls_continuacion.md` | ✅ **MERGEADO** (S-002.5 + S-002.6) | commits previos al P0 RLS fix | Universo RLS 117/117 (después 120/120 post PR #91, hoy 123 con 122 RLS post PR #94) |
| — | ✅ **MERGEADO** Sprint COWORK-RUNTIME-001 | PR #90 commit `c0ee5230` | 9 capabilities en shadow mode esperando ramp. NO tiene spec en `sprints_propuestos/` — spec original vive en `bridge/cowork_to_manus_PROMPT_AYUDA_COWORK_OBEDIENCIA_2026_05_11.md` |
| — | ✅ **MERGEADO** Sprint EMBRION-NEEDS-002 T5 Embrión-Daddy bidireccional | PR #94 commit `aaf4b298` (HOY 2026-05-11) | Spec firmado vive en `discovery_forense/SPECS/EMBRION_DADDY_BIDIRECCIONAL_v1.md`. Caveat 🟡 MFA stub: corregir wording postmortem + Tarea 5b antes de uso real de `/override` |
| — | ✅ **MERGEADO** PR #95 Migration 0010 (resolución gap + 3 derivas DB↔repo) | commit `a0f4b1cb` (HOY 2026-05-11) | Aplicar migración a producción post-merge: `python3 scripts/_apply_migration_0010.py` |

---

## 2. Sprints EN EJECUCIÓN (kickoff enviado, código pendiente)

| Spec | Estado | Hilo | Kickoff |
|---|---|---|---|
| [`sprint_TRANSVERSAL_001_capas_implement_monitor.md`](./sprint_TRANSVERSAL_001_capas_implement_monitor.md) | 🟡 **KICKEADO HOY** — esperando código | Hilo Ejecutor 2 (libre desde 2026-05-11 ~15:00 UTC) | [`bridge/cowork_to_manus_TRANSVERSAL_001_KICKOFF_2026_05_11.md`](../cowork_to_manus_TRANSVERSAL_001_KICKOFF_2026_05_11.md) (commit `836222e`) |

**Notas TRANSVERSAL-001:**
- 9 tareas T1-T9 con perfil_riesgo declarado
- ETA spec: 4-6h reales
- Δ Obj global esperado: +6-8 pts (audit CRUCE_DIMENSIONAL_5A §5 #3)
- T2/T4/T7 requieren coordinación humana con Alfredo (Stripe LIVE, Ads paused→active, SAT/CFDI real)

---

## 3. Sprints PROPUESTOS — spec firmado, sin kickoff todavía

| # | Spec | Status | Hilo previsto | Bloqueantes |
|---|---|---|---|---|
| 1 | [`sprint_89_catastros_extension_suppliers_herramientas_ai.md`](./sprint_89_catastros_extension_suppliers_herramientas_ai.md) | Propuesto, no arrancado | Hilo Ejecutor backend | Ninguno (paralelizable con Catastro-A) |
| 2 | [`sprint_90_checkout_stripe_package.md`](./sprint_90_checkout_stripe_package.md) | Propuesto, no arrancado | Hilo Ejecutor backend o Manus WebDev | **Sprint 88 ya cerrado**; ver §3.1 abajo para aclaración vs TRANSVERSAL-001 |
| 3 | [`sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md`](./sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md) | Propuesto, no arrancado | Cowork + Manus | Ninguno — todos los inputs en main |
| 4 | [`sprint_catastro_A_investigacion_poblamiento.md`](./sprint_catastro_A_investigacion_poblamiento.md) | Propuesto, no arrancado | Hilo Catastro | Ninguno (paralelizable con Sprint 89) |
| 5 | [`sprint_catastro_B_design_tokens_oauth_skill_biblia_template.md`](./sprint_catastro_B_design_tokens_oauth_skill_biblia_template.md) | Propuesto, no arrancado | Hilo Catastro | Ninguno |
| 6 | [`sprint_mobile_1_esqueleto_flutter.md`](./sprint_mobile_1_esqueleto_flutter.md) | 🟡 **Parcial ~35%** | Hilo Mobile | Realignment necesario — REPORTE_BINARIO_APP_FLUTTER detecta divergencia arquitectónica (`services/` vs `mensajeros/` canónico, sin `modes/daily` ni `modes/cockpit`) |
| 7 | [`sprint_mobile_2_modo_daily_fase1_stubs.md`](./sprint_mobile_2_modo_daily_fase1_stubs.md) | 🟡 **Parcial ~20%** | Hilo Mobile | Mobile 1 Realignment primero |
| 8 | [`sprint_mobile_3_modo_cockpit_fase1.md`](./sprint_mobile_3_modo_cockpit_fase1.md) | 🟡 **Parcial ~50%** | Hilo Mobile | Mobile 1+2 |
| 9 | [`sprint_mobile_4_modo_cockpit_fase2.md`](./sprint_mobile_4_modo_cockpit_fase2.md) | 🔴 **~10%** | Hilo Mobile | Mobile 3 |
| 10 | [`sprint_mobile_5_modo_cockpit_fase3.md`](./sprint_mobile_5_modo_cockpit_fase3.md) | 🔴 **~10%** | Hilo Mobile | Mobile 4 |

### 3.1 Aclaración magna — Sprint 90 NPM vs Sprint TRANSVERSAL-001 T7 (kernel)

**No compiten. Son complementarios.**

| Aspecto | Sprint 90 (`sprint_90_checkout_stripe_package.md`) | Sprint TRANSVERSAL-001 T7 |
|---|---|---|
| **Lenguaje/Stack** | TypeScript/React (npm package) | Python (kernel) |
| **Output** | Paquete `@monstruo/checkout-stripe` publicado a npm | `kernel/transversales/finanzas/__init__.py` con `FinanzasLayer.implement()` real |
| **Consumer** | Apps TS (LikeTickets actual, futuro Marketplace TS) | Kernel del Monstruo (`embrion_loop`, pipeline E2E) |
| **Cierra** | Reutilización del patrón Stripe entre proyectos TS | `FinanzasLayer.implement()` que hoy levanta `NotImplementedError` |
| **Bloqueante de** | Marketplace, CIP, Mundo Tata (apps TS futuras) | DSC-G-014 PRODUCTO COMERCIALIZABLE + Obj #9 Transversalidad |

Si se ejecutan ambos, **TRANSVERSAL-001 T7 va primero** porque cierra deuda arquitectónica del kernel. Sprint 90 NPM puede ser después como capa cliente para apps TS.

---

## 4. Sprints FANTASMA — citados sin spec firmada

Estos sprints aparecen referenciados en código (`NotImplementedError`, strings) o en docs (handoffs, audits) **pero NO tienen spec firmada en `bridge/sprints_propuestos/`**. Son deuda nominal que el Sprint SPECS-FIRMA-001 (próximo) cerrará para 3 de los 4:

| Sprint citado | Referenciado en | Estado | Plan |
|---|---|---|---|
| **Sprint 92 Guardián Autónomo** | `memory/cowork/audits/AUDIT_OBJETIVOS_2D §6 L1` + `CRUCE_DIMENSIONAL_5A §5 #2` | ❌ Fantasma | 🟡 **Cowork redactará spec en SPECS-FIRMA-001 (próximo)** — 996 LOC de Guardian existen, falta wiring cron + scoring + dashboard. ROI máximo del backlog. |
| **Sprint ROTOR-001** | `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md §3` ("agentes mueren rápido sin Escape ni Rotor") + audit 3A §3 + handoff Cowork bloqueante #1 | ❌ Fantasma | 🟡 **Cowork redactará spec en SPECS-FIRMA-001 (próximo)** — pieza diferencial del Reloj Suizo declarada faltante. |
| **Sprint SOVEREIGN-INFRA** | `COWORK_BASE_CONOCIMIENTO §3` + audit 3A §4 | ❌ Fantasma | ⏸️ **Diferido** — no urgente para próximos 30 días. Capa 3 Soberanía (32.6% real) tiene otras prioridades primero (LLM v2 + Economía vía Pagos). |
| **Sprint 87 ORIGINAL Stripe** | audit 3A §2 H1 ("spec del 2026-05-04 dormido 6 días") | ❌ Fantasma o nunca commiteado a `bridge/` | ⏸️ **Diferido** — su scope queda cubierto por Sprint 90 (NPM) + TRANSVERSAL-001 T7 (kernel). Si Alfredo quiere revivirlo, requiere search en `git log --all` para localizar evidencia. |

**Patrón emergente:** los sprints fantasma se generan cuando código emite `NotImplementedError` con texto del sprint pero nadie redacta el spec firmable. **DSC-S-012 propuesto** (anti-deriva migraciones) tiene un análogo aplicable a specs: "prohibido referenciar Sprint X en código sin spec firmada en `bridge/sprints_propuestos/`". Pendiente discutir si canonizar esa regla en SPECS-FIRMA-001 ampliado.

---

## 5. Archivos auxiliares en el directorio

| Archivo | Propósito |
|---|---|
| `README.md` (10,762 bytes, 2026-05-06) | Histórico narrativo del orden de ejecución original (Día 1 → Día 5 paralelo de 3 hilos). Sigue siendo lectura recomendada para contexto, pero NO autoritativo para "qué arrancar ahora". |
| `SPRINTS_PUSH_NOTE.md` (616 bytes, 2026-05-06) | DEPRECATED — marker temporal de confusión de push. Ya marcado como tal en su contenido. |
| `_INDEX.md` (este archivo) | **Autoritativo** sobre estado de cada sprint del directorio. |

---

## 6. Cambios derivados a hacer en próximas sesiones

### 6.1 Mover sprints mergeados fuera de "propuestos"

Sprints 88, S001, S002.6 ya están mergeados pero sus specs siguen en `sprints_propuestos/`. **Opción A** (limpia): mover a `bridge/sprints_propuestos/_completados/` con fecha de cierre. **Opción B** (mínima): este `_INDEX.md` ya los marca como completados, suficiente para evitar confusión. Recomendación T2: B por ahora, A en próximo housekeeping (~30 min Cowork puro).

### 6.2 Sprint Mobile Realignment

`REPORTE_BINARIO_APP_FLUTTER_2026_05_11.md` §VIII recomienda "Camino A — Realignment Incremental" antes de continuar Mobile 2-5. **Esto NO está en `sprints_propuestos/`.** Necesita redacción explícita como `sprint_mobile_REALIGNMENT_001.md` antes de continuar Mobile.

### 6.3 Sprint Inventory Bridge

`bridge/` completo tiene >100 archivos (handoffs, kickoffs, postmortems, reportes Manus). Vale un inventory similar a este `_INDEX.md` pero para `bridge/` raíz — diferenciando handoffs activos vs históricos.

---

## 7. Versión

- **v1.0** 2026-05-11 (Cowork T2, Sprint NOMENCLATURA-001 bajo autorización T1 directa de Alfredo). Basado en lectura binaria de los 16 archivos del directorio + audits CARTOGRAFIA 1A/1B/1C/3A/3B + CRUCE_DIMENSIONAL_5A + REPORTE_BINARIO_APP_FLUTTER.

---

*Generado por Cowork T2 como parte de Sprint NOMENCLATURA-001 (catálogo limpio de specs). Sin pseudo-medición — cifras heredadas de audits codebase-validated del 2026-05-10/11. Cero claims sin evidencia binaria en filesystem o Supabase.*
