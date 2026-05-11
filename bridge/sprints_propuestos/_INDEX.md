---
id: bridge_sprints_propuestos_INDEX
fecha: 2026-05-11
autor: Cowork T2 (Sprint NOMENCLATURA-001 bajo autorización T1 directa)
proposito: catálogo autoritativo de sprints en bridge/sprints_propuestos/ + estado real verificado binariamente
estado: vigente — supersede al README.md de 2026-05-06 como fuente autoritativa
version: 1.1 — 2026-05-11 (post firma T1 de Guardian + ROTOR-001 + DSC-S-012)
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
| [`sprint_GUARDIAN_AUTONOMO_001_activacion.md`](./sprint_GUARDIAN_AUTONOMO_001_activacion.md) | 🟡 **FIRMADO HOY (2026-05-11) — kickoff inmediato a Ejecutor 1** | Hilo Ejecutor 1 | Pendiente — Cowork prepara `bridge/cowork_to_manus_GUARDIAN_AUTONOMO_001_KICKOFF_2026_05_11.md` ahora mismo |

**Notas TRANSVERSAL-001:**
- 9 tareas T1-T9 con perfil_riesgo declarado
- ETA spec: 4-6h reales
- Δ Obj global esperado: +6-8 pts (audit CRUCE_DIMENSIONAL_5A §5 #3)
- T2/T4/T7 requieren coordinación humana con Alfredo (Stripe LIVE, Ads paused→active, SAT/CFDI real)

**Notas GUARDIAN-AUTONOMO-001:**
- 6 tareas T1-T6 con perfil_riesgo declarado
- ETA spec: 2-3 días reales
- Δ Obj global esperado: +3 pts (Obj #14 sube de 55% a 80%+)
- ROI máximo del backlog según audit `CRUCE_DIMENSIONAL_5A §5 #2` — libera a Cowork del rol de Guardian de facto
- T3 alerting Telegram requiere firma adicional de Alfredo para hora/canal antes del flip producción

---

## 3. Sprints PROPUESTOS — spec firmado, sin kickoff todavía

| # | Spec | Status | Hilo previsto | Bloqueantes |
|---|---|---|---|---|
| 1 | [`sprint_89_catastros_extension_suppliers_herramientas_ai.md`](./sprint_89_catastros_extension_suppliers_herramientas_ai.md) | Propuesto, no arrancado | Hilo Ejecutor backend | Ninguno (paralelizable con Catastro-A) |
| 2 | [`sprint_90_checkout_stripe_package.md`](./sprint_90_checkout_stripe_package.md) | Propuesto, no arrancado | Hilo Ejecutor backend o Manus WebDev | **Sprint 88 ya cerrado**; ver §3.1 abajo para aclaración vs TRANSVERSAL-001 |
| 3 | [`sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md`](./sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md) | Propuesto, no arrancado | Cowork + Manus | Ninguno — todos los inputs en main |
| 4 | [`sprint_ROTOR_001_reciclador_actividad.md`](./sprint_ROTOR_001_reciclador_actividad.md) | 🟢 **FIRMADO 2026-05-11** — esperando kickoff | Hilo Ejecutor (cualquiera libre tras GUARDIAN-AUTONOMO-001) | **Recomendación operativa T1+T2: GUARDIAN-AUTONOMO-001 primero**. Defaults energy_units firmados por Alfredo |
| 5 | [`sprint_catastro_A_investigacion_poblamiento.md`](./sprint_catastro_A_investigacion_poblamiento.md) | Propuesto, no arrancado | Hilo Catastro | Ninguno (paralelizable con Sprint 89) |
| 6 | [`sprint_catastro_B_design_tokens_oauth_skill_biblia_template.md`](./sprint_catastro_B_design_tokens_oauth_skill_biblia_template.md) | Propuesto, no arrancado | Hilo Catastro | Ninguno |
| 7 | [`sprint_mobile_1_esqueleto_flutter.md`](./sprint_mobile_1_esqueleto_flutter.md) | 🟡 **Parcial ~35%** | Hilo Mobile | Realignment necesario — REPORTE_BINARIO_APP_FLUTTER detecta divergencia arquitectónica (`services/` vs `mensajeros/` canónico, sin `modes/daily` ni `modes/cockpit`) |
| 8 | [`sprint_mobile_2_modo_daily_fase1_stubs.md`](./sprint_mobile_2_modo_daily_fase1_stubs.md) | 🟡 **Parcial ~20%** | Hilo Mobile | Mobile 1 Realignment primero |
| 9 | [`sprint_mobile_3_modo_cockpit_fase1.md`](./sprint_mobile_3_modo_cockpit_fase1.md) | 🟡 **Parcial ~50%** | Hilo Mobile | Mobile 1+2 |
| 10 | [`sprint_mobile_4_modo_cockpit_fase2.md`](./sprint_mobile_4_modo_cockpit_fase2.md) | 🔴 **~10%** | Hilo Mobile | Mobile 3 |
| 11 | [`sprint_mobile_5_modo_cockpit_fase3.md`](./sprint_mobile_5_modo_cockpit_fase3.md) | 🔴 **~10%** | Hilo Mobile | Mobile 4 |

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

Estos sprints aparecen referenciados en código (`NotImplementedError`, strings) o en docs (handoffs, audits) **pero NO tienen spec firmada en `bridge/sprints_propuestos/`**:

| Sprint citado | Referenciado en | Estado | Plan |
|---|---|---|---|
| **Sprint SOVEREIGN-INFRA** | `COWORK_BASE_CONOCIMIENTO §3` + audit 3A §4 | ❌ Fantasma | ⏸️ **Diferido** — no urgente para próximos 30 días. Capa 3 Soberanía (32.6% real) tiene otras prioridades primero (LLM v2 + Economía vía Pagos). |
| **Sprint 87 ORIGINAL Stripe** | audit 3A §2 H1 ("spec del 2026-05-04 dormido 6 días") | ❌ Fantasma o nunca commiteado a `bridge/` | ⏸️ **Diferido** — su scope queda cubierto por Sprint 90 (NPM) + TRANSVERSAL-001 T7 (kernel). Si Alfredo quiere revivirlo, requiere search en `git log --all` para localizar evidencia. |

**Sprints fantasma RESUELTOS hoy (2026-05-11) — antes eran 4, ahora son 2:**
- ✅ **Sprint GUARDIAN-AUTONOMO-001** — pasó a §2 (firmado y kickoff inmediato a Ejecutor 1).
- ✅ **Sprint ROTOR-001** — pasó a §3 (firmado, esperando kickoff post-Guardian).

**Patrón emergente residual:** los sprints fantasma se generan cuando código emite `NotImplementedError` con texto del sprint pero nadie redacta el spec firmable. **DSC-S-012 (firmado hoy)** canoniza la regla análoga aplicada a migraciones SQL; principio extensible a specs vía DSC futuro si emerge necesidad.

---

## 5. DSCs canonizados HOY (2026-05-11)

| DSC | Path | Estado | Status en `_dsc_contracts_index.yaml` | Notas |
|---|---|---|---|---|
| **DSC-S-012** | [`discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-012_anti_deriva_migraciones_supabase.md`](../../discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-012_anti_deriva_migraciones_supabase.md) | 🟢 firme (firmado por T1 2026-05-11) | `aspirational` con reason — contrato §1 pendiente | Total DSCs canonizados: 64 → **65**. Restricción dura anti-deriva DB↔repo. Deadline DSC-G-017 para implementación: 30 días = 2026-06-10. |

---

## 6. Archivos auxiliares en el directorio

| Archivo | Propósito |
|---|---|
| `README.md` (10,762 bytes, 2026-05-06) | Histórico narrativo del orden de ejecución original (Día 1 → Día 5 paralelo de 3 hilos). Sigue siendo lectura recomendada para contexto, pero NO autoritativo para "qué arrancar ahora". |
| `SPRINTS_PUSH_NOTE.md` (616 bytes, 2026-05-06) | DEPRECATED — marker temporal de confusión de push. Ya marcado como tal en su contenido. |
| `_INDEX.md` (este archivo) | **Autoritativo** sobre estado de cada sprint del directorio. |

---

## 7. Cambios derivados a hacer en próximas sesiones

### 7.1 Mover sprints mergeados fuera de "propuestos"

Sprints 88, S001, S002.6 ya están mergeados pero sus specs siguen en `sprints_propuestos/`. **Opción A** (limpia): mover a `bridge/sprints_propuestos/_completados/` con fecha de cierre. **Opción B** (mínima): este `_INDEX.md` ya los marca como completados, suficiente para evitar confusión. Recomendación T2: B por ahora, A en próximo housekeeping (~30 min Cowork puro).

### 7.2 Sprint Mobile Realignment

`REPORTE_BINARIO_APP_FLUTTER_2026_05_11.md` §VIII recomienda "Camino A — Realignment Incremental" antes de continuar Mobile 2-5. **Esto NO está en `sprints_propuestos/`.** Necesita redacción explícita como `sprint_mobile_REALIGNMENT_001.md` antes de continuar Mobile.

### 7.3 Sprint Inventory Bridge

`bridge/` completo tiene >100 archivos (handoffs, kickoffs, postmortems, reportes Manus). Vale un inventory similar a este `_INDEX.md` pero para `bridge/` raíz — diferenciando handoffs activos vs históricos.

### 7.4 Sprint Cowork-puro contrato ejecutable DSC-S-012

Recordatorio: hay deadline DSC-G-017 de **30 días desde firma (2026-06-10)** para implementar `tools/_check_migration_drift.py` + pre-commit hook + workflow CI. Sin esto, DSC-S-012 degrada a aspirational permanente. ETA: 2-3h Cowork puro.

---

## 8. Versión

- **v1.0** 2026-05-11 (Cowork T2, Sprint NOMENCLATURA-001). Inventario inicial con 4 sprints fantasma (Guardian + ROTOR + SOVEREIGN-INFRA + Sprint 87 original).
- **v1.1** 2026-05-11 (Cowork T2, post firma T1 SPECS-FIRMA-001 ampliado). GUARDIAN-AUTONOMO-001 y ROTOR-001 salen de §4 fantasma. DSC-S-012 canonizado como #65. §4 fantasma queda con 2 (SOVEREIGN-INFRA + Sprint 87 original).

---

*Generado por Cowork T2 como parte de Sprint NOMENCLATURA-001 (catálogo limpio de specs). v1.1 post firmas T1 del 2026-05-11. Sin pseudo-medición — cifras heredadas de audits codebase-validated del 2026-05-10/11. Cero claims sin evidencia binaria en filesystem o Supabase.*
