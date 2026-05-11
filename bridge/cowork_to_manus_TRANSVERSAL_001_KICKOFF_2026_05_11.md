---
id: cowork_to_manus_TRANSVERSAL_001_KICKOFF_2026_05_11
fecha: 2026-05-11
emisor: Cowork T2
destinatario: Hilo Ejecutor 2 (manus_hilo_ejecutor_2)
sprint: TRANSVERSAL-001
nombre_completo: "Capas Transversales — implement() + monitor() reales"
spec_firmado: bridge/sprints_propuestos/sprint_TRANSVERSAL_001_capas_implement_monitor.md (blob 4159f710149f6a28ae6e38cf1e8fbde776f92bbf, 14,550 bytes)
autorizacion_t1: Alfredo 2026-05-11 (instrucción explícita "Hilo Ejecutor 2 libre ahora, arrancar kickoff TRANSVERSAL-001")
delta_esperado_obj_global: +6-8 pts (de ~67% a ~74-75% — audit CRUCE_DIMENSIONAL_5A §5 #3)
estado: ABIERTO — esperando arranque del ejecutor
---

# Kickoff Sprint TRANSVERSAL-001 — Implementación de las 6 Capas Transversales

## 0. Cómo leer este kickoff

Si sos Hilo Ejecutor 2 leyendo esto: **antes de escribir una sola línea de código**, leé en orden:

1. Este documento entero.
2. `bridge/sprints_propuestos/sprint_TRANSVERSAL_001_capas_implement_monitor.md` (spec firmado, **fuente de verdad — 9 tareas T1-T9 detalladas con perfil_riesgo, pre-flight check del §7, criterios de cierre del §4**).
3. `memory/cowork/audits/AUDIT_CAPAS_TRANSVERSALES_3B_1_a_4_2026_05_10.md` (contexto del estado real al 2026-05-10).
4. `memory/cowork/audits/CARTOGRAFIA_1C_KERNEL_ESPECIALIZADOS_2026_05_10.md` §3.2 (cobertura técnica de `kernel/transversales/`).
5. Pre-flight check del §7 del spec (5 comandos bash de verificación).

Si arrancás a codear sin leer los 5, parate. La doctrina del Monstruo es leer antes de escribir.

---

## 1. Contexto mínimo suficiente — por qué este sprint

El `kernel/transversales/` tiene 6 capas declaradas (Ventas, SEO, Publicidad, Tendencias, Operaciones, Finanzas). Estado real verificado el 2026-05-10 (audit 3B + 1C):

- ✅ **SeoLayer** end-to-end (`implement()` + `monitor()` reales, sin red).
- 🟡 **5 capas restantes:** `diagnose()` + `recommend()` OK, pero **`implement()` y `monitor()` levantan `NotImplementedError`** apuntando explícitamente a este sprint.
- ❌ **`kernel/transversales/` está aislado del flujo principal** — `grep -rln "kernel\.transversales" kernel/` excluyendo el propio dir y tests = **0 hits**. Ningún módulo del kernel principal importa una sola capa transversal. Obj #9 ("Transversalidad Universal — 8 capas en TODO producto") es texto, no enforcement de código.
- ❌ **`validation_log` table NO existe en Supabase production** todavía (migración `0001_validation_log.sql` lista para aplicar pero no aplicada).
- ❌ **`dsc_contract_check.py` NO activado como hook bloqueante** (existe pero no enforce).
- ❌ **42+ tags `[NEEDS_PERPLEXITY_VALIDATION]`** sin resolver en `validation_log`.

Este sprint cierra TODO eso. Cumple 4 Objetivos Maestros simultáneos: #9 (Transversalidad) + #2 (Apple/Tesla) + #11 (Resiliencia agéntica) + #15 (Memoria soberana).

**Delta esperado en Obj global:** +6-8 pts (de ~67% a ~74-75%). Es el sprint con mayor leverage del proyecto según `CRUCE_DIMENSIONAL_5A_2026_05_10.md` §5 #3.

---

## 2. Resumen del spec firmado (NO abrir a debate — ya canonizado)

El spec firmado tiene **9 tareas T1-T9**, cada una con `perfil_riesgo` declarado:

| Tarea | Perfil riesgo | ETA estimada | Resumen |
|---|---|---|---|
| **T1** Aplicar migration `validation_log` + inyectar `SupabaseStorage` | write-risky | 30 min | Migración 0001 a Supabase prod + wire `kernel/validation/_storage_supabase.py` |
| **T2** `VentasLayer.implement+monitor` con HubSpot/Stripe | write-risky | 60-90 min | Push pricing tiers a HubSpot Products + Stripe Products/Prices. Validation magna `hubspot_api_2026` requerida ANTES de codificar |
| **T3** `SeoLayer.implement+monitor` con render integration + Search Console | write-safe | 60 min | JSON-LD blocks + meta tags HTML. Search Console API en `monitor()`. Validation magna `schema_org_vocabulary_2026` |
| **T4** `PublicidadLayer.implement+monitor` con Meta/Google/LinkedIn Ads APIs | requiere-coordinacion-humana | 90-120 min | Campañas template en estado `paused`. **NO ejecuta gasto real.** Validation magna `cpc_benchmark_2026`, `audience_size_2026`, etc. **Coordinación con Alfredo OBLIGATORIA** antes de cualquier `paused → active` |
| **T5** `TendenciasLayer.implement+monitor` con data feeds | write-safe | 60 min | Subscripciones Polygon webhook + Google Trends scraper + RSS feeds. Nueva tabla `trend_signals` |
| **T6** `OperacionesLayer.implement+monitor` con helpdesk integration | write-risky | 60 min | Support channels per vertical (Intercom o Front). SLA first-response calculation |
| **T7** `FinanzasLayer.implement+monitor` con accounting + CFDI emitter | requiere-coordinacion-humana | 90-120 min | Contpaq/Quickbooks API + CFDI 4.0 emitter para MX. **Coordinación con Alfredo OBLIGATORIA** — operaciones de finanzas reales NO se shipan sin firma humana. Validation magna `tax_rates_2026:<vertical>` + `cfdi_4_canonical_format` |
| **T8** Activar `dsc_contract_check` como pre-commit hook bloqueante | write-safe | 30 min | Editar `.pre-commit-config.yaml`. Test sintético: DSC nuevo sin entry → blocked |
| **T9** Resolver 42+ tags Perplexity en `validation_log` | read-only | 60 min batch | Para cada tag detectado por `tools/check_perplexity_tags.py`, ejecutar Perplexity query + `record_validation()`. NO modifica código del repo, solo poblar la tabla |

**ETA total declarada en spec:** 4-6 horas reales en 7 sub-sprints. **Velocity Manus demostrada:** factible.

---

## 3. Criterios de aceptación verificables (10 CA — binariamente demostrables)

Cada criterio debe demostrarse con comando o test. Si no podés demostrarlo, no está hecho.

### CA1 — `validation_log` table operativa en Supabase

```sql
SELECT count(*) FROM public.validation_log;
-- Esperado: ≥0 (tabla existe, count válido aunque sea 0)
SELECT rowsecurity FROM pg_tables WHERE tablename='validation_log';
-- Esperado: true (RLS habilitada — DSC-S-006 v1.1)
```

### CA2 — Wiring `SupabaseStorage` activo

```bash
python -c "from kernel.validation import requires_perplexity_validation; from kernel.validation._storage_supabase import SupabaseStorage; print('ok')"
# Esperado: imprime 'ok' sin error
```

+ smoke contra Supabase real: `reports/validation_log_supabase_smoke.json` con al menos 1 row insertada por el decorator.

### CA3 — 6 capas con `implement()` y `monitor()` REALES (no `NotImplementedError`)

```bash
grep -rn "raise NotImplementedError" kernel/transversales/
# Esperado: 0 hits
```

+ `pytest tests/test_*_implement_integration.py` PASS para cada capa.

### CA4 — Reports de smoke por capa

Archivos esperados en `reports/`:
- `ventas_implement_smoke.json` (con tier IDs HubSpot + Stripe creados)
- `seo_implement_smoke.json` (con JSON-LD generado per 8 verticales)
- `publicidad_implement_smoke.json` (con campaign IDs en estado `paused`)
- `tendencias_implement_smoke.json` (con signals reales en `trend_signals`)
- `operaciones_implement_smoke.json` (con channels configurados al menos para LikeTickets)
- `finanzas_implement_smoke.json` (con transacción Stripe test mode → CFDI sandbox)

### CA5 — Validation magna pre-codificación documentada

Para cada tarea que tenga `Validation magna requerida` (T2, T3, T4, T6, T7):
```sql
SELECT claim_type, validator, evidence_url, valid_until
FROM public.validation_log
WHERE claim_type IN (
  'hubspot_api_2026', 'schema_org_vocabulary_2026',
  'cpc_benchmark_2026', 'audience_size_2026', 'platform_policy_2026',
  'helpdesk_api_2026', 'tax_rates_2026', 'cfdi_4_canonical_format'
)
AND valid_until > now();
-- Esperado: ≥1 row vigente para cada claim_type listado
```

### CA6 — `dsc_contract_check` activo como hook bloqueante

Test sintético reproducible:
```bash
# 1. Crear DSC nuevo sin entry en _dsc_contracts_index.yaml
# 2. git add + git commit
# 3. Verificar que el commit FALLA con mensaje "DSC sin entry en index"
# 4. Agregar entry y reintentar — commit DEBE pasar
```

+ Reporte JSON en `reports/dsc_contract_check_hook_test.json`.

### CA7 — 42+ tags Perplexity resueltos

```bash
python tools/check_perplexity_tags.py --fail-on-found
echo $?
# Esperado: 0 (todos los tags tienen validation_log registrado)
```

### CA8 — Pipeline técnico funcional declarable

```bash
python -m kernel.milestones.declare pipeline_tecnico_funcional
echo $?
# Esperado: 0 (pytest e2e + coverage 80%+ + smoke endpoint verde)
```

### CA9 — Tests verdes integrales

```bash
pytest tests/ -v
# Esperado: 100% PASS, sin xfail nuevos
```

Volumen mínimo: tests existentes (103+) **siguen verdes** + tests nuevos (uno por T2-T7 al menos) **PASS**.

### CA10 — Audit DSC-G-008 v2 por Cowork verde antes de merge

Cuando el PR esté listo:
- Cowork audita con metodología DSC-G-008 v2 (rúbrica + evidencia + denominador + falsadores).
- Resultado debe ser 🟢 GREEN en los 6 gates (G1-G6).
- Cowork comenta el PR con el audit verbatim.
- Cowork mergea bajo regla evolucionada 2026-05-11 (autorización T1 + audit verde).

**Sin audit verde, el sprint NO se cierra como `🏛️ TRANSVERSAL-001 — DECLARADO`.**

---

## 4. Archivos a tocar / NO tocar

### Tocar (esperado)

- `kernel/transversales/{ventas,seo,publicidad,tendencias,operaciones,finanzas}/__init__.py` — eliminar `NotImplementedError`, implementar `implement()` y `monitor()` reales.
- `kernel/validation/_storage_supabase.py` — verificar implementación o completar si falta.
- `kernel/main.py` — añadir wiring `set_default_storage(SupabaseStorage(supabase_client))` en boot (mínimo cambio).
- `migrations/sql/0001_validation_log.sql` — aplicar a Supabase prod (si no aplicada).
- `migrations/sql/00XX_trend_signals.sql` — crear (nueva tabla para T5).
- `tests/test_ventas_implement_integration.py` y equivalentes per capa — crear o extender.
- `.pre-commit-config.yaml` — añadir hook `dsc_contract_check`.
- `reports/*.json` — generar artifacts requeridos (CA4 + CA5 + CA6).

### NO TOCAR (zona prohibida)

- `kernel/embrion_loop.py` — **Doctrina del silencio.** Cero modificaciones (la integración del Embrión con las capas viene en sprint posterior).
- `kernel/embrion_budget.py`, `kernel/embrion_self_verifier.py`, `kernel/embrion_write_policy.py` — operan en flujo paralelo.
- `kernel/catastro/` — territorio Hilo Catastro.
- `apps/mobile/` — territorio Hilo Ejecutor Oficial (Sprint MOBILE_1B).
- `kernel/sovereignty/`, `kernel/i18n/`, `kernel/brand/` — fuera de scope.
- `kernel/cowork_runtime/` — runtime de Cowork (Sprint COWORK-RUNTIME-001 ya mergeado, no tocar).
- `kernel/transversales/seo/` — `implement()` y `monitor()` **ya están reales** (única capa cerrada). Solo extender `monitor()` con Search Console API en T3, no reescribir.
- Credenciales (Bitwarden, Railway env vars, Supabase keys, Stripe keys, HubSpot keys, etc.) — NUNCA.

---

## 5. Pre-flight check obligatorio (del §7 del spec firmado)

ANTES de arrancar T1, correr los 5 comandos del §7 del spec:

```bash
# 1. Repo limpio y synced
git status && git pull origin main

# 2. Tests verde local (96+ tests sin red)
python tests/test_perplexity_decorator.py
python tests/test_transversales_ventas_constraints.py
python tools/dsc_contract_check.py $(find discovery_forense/CAPILLA_DECISIONES -name "DSC-*.md")

# 3. Credenciales Supabase + Railway env vars
test -n "$SUPABASE_DB_URL"
test -n "$RAILWAY_TOKEN"

# 4. Conexión Supabase
psql "$SUPABASE_DB_URL" -c "SELECT 1;"

# 5. APIs externas para T2/T4/T6/T7 — Manus debe confirmar acceso ANTES de arrancar esas tareas específicas
```

Si cualquier paso falla, NO arrancar. Reportar al bridge antes de seguir (ver §6).

---

## 6. Protocolo de blocker >30min

Si te encontrás bloqueado >30min en cualquier tarea, **NO sigas atascado en silencio**. Insert directo en `embrion_memoria` vía MCP Supabase:

```sql
INSERT INTO public.embrion_memoria (tipo, contenido, contexto, hilo_origen, importancia)
VALUES (
  'mensaje_alfredo',
  'BLOCKER >30min en Sprint TRANSVERSAL-001. Tarea: T<N>. Descripción: <qué intenté, qué falló, hipótesis del por qué>. Acción requerida de T1: <propuesta concreta de decisión>. Sin acción → bloqueado.',
  jsonb_build_object(
    'sprint', 'TRANSVERSAL-001',
    'tarea', '<T1..T9>',
    'archivo_afectado', '<path>',
    'kickoff', 'bridge/cowork_to_manus_TRANSVERSAL_001_KICKOFF_2026_05_11.md',
    'destinatario', 'alfredo_t1',
    'cc', 'cowork_t2'
  ),
  'manus_hilo_ejecutor_2',
  9
);
```

- `tipo='mensaje_alfredo'` está en el whitelist permitido por la tabla.
- `importancia=9` para blockers reales. NO abusar.
- Esperar respuesta vía `embrion_memoria` con `tipo='mensaje_alfredo'` de Alfredo o vía bridge file `cowork_to_manus_*`.

**Casos especiales que requieren coordinación humana OBLIGATORIA** (del spec):
- T4 (Publicidad): cualquier transición `paused → active` requiere firma explícita de Alfredo. NO ejecutar gasto real sin firma.
- T7 (Finanzas): setup SAT/CFDI requiere firma explícita de Alfredo. NO emitir CFDIs reales sin firma.

Para esos casos, NO uses `tipo='mensaje_alfredo'` automático — pausá la tarea, generá reporte en `bridge/manus_to_cowork_<tarea>_FIRMA_REQUERIDA_<fecha>.md`, y esperá firma explícita.

---

## 7. PR a abrir + naming convención

- **Branch:** `sprint/transversal-001-capas-implement-monitor`
- **Base:** `main`
- **PR title:** `feat(transversales): Sprint TRANSVERSAL-001 — implement() + monitor() reales para las 6 Capas Transversales`
- **PR body mínimo:**
  - Referencia explícita al spec: `bridge/sprints_propuestos/sprint_TRANSVERSAL_001_capas_implement_monitor.md` (blob `4159f710`).
  - Tabla de 9 tareas T1-T9 con check pass/fail por tarea.
  - Cita verbatim de los 10 CA de este kickoff con evidencia adjunta (paths a `reports/*.json` + outputs SQL).
  - Métricas tests (≥103 existentes verdes + N nuevos PASS).
  - `gitleaks` clean en el diff completo.
  - Frase canónica de cierre: `🏛️ TRANSVERSAL-001 — DECLARADO (9/9 verde)`.
- **Commits:** atómicos por tarea. T1=1 commit, T2=1 commit, …, T9=1 commit. Sin "WIP" ni "fix tests" mezclados.
- **No `git stash` sin issue de seguimiento** (anti-patrón V23 canonizado tras incidente del 2026-05-11).

---

## 8. Definition of Done (DoD)

El sprint está cerrado cuando se cumple TODO esto y se demuestra binariamente:

- [ ] CA1-CA10 todos en verde con evidencia citada en PR body.
- [ ] 9 tareas T1-T9 PASS, exit 0 con artifacts en `reports/`.
- [ ] `python -m kernel.milestones.declare pipeline_tecnico_funcional` retorna exit 0.
- [ ] `tools/check_perplexity_tags.py --fail-on-found` retorna exit 0.
- [ ] `python tools/dsc_contract_check.py $(find discovery_forense/CAPILLA_DECISIONES -name "DSC-*.md")` retorna exit 0 con 100% cobertura.
- [ ] `pytest tests/` PASS completo.
- [ ] Cowork audit DSC-G-008 v2 verde (los 6 gates) — comentado verbatim en el PR.
- [ ] `bridge/manus_to_cowork_REPORTE_TRANSVERSAL_001_CIERRE_<fecha>.md` escrito y commiteado (timeline, bugs encontrados, lecciones, decisión paused→active si aplica).
- [ ] PR mergeada a `main`. Cowork T2 mergea bajo regla evolucionada 2026-05-11 (audit verde + autorización T1).
- [ ] `memory/cowork/COWORK_DECISIONES_VIVAS.md` §6 (8 Capas Transversales) actualizada con cifras post-sprint y referencia al PR de cierre.

**Hito secundario T1 firma requerida:** `python -m kernel.milestones.declare producto_comercializable` solo retorna exit 0 si Alfredo firma `reports/firma_alfredo_producto.sig` validando que el output es Apple/Tesla quality real per vertical. Sin esa firma, el cierre queda como `🏛️ TRANSVERSAL-001 — PIPELINE TÉCNICO DECLARADO` (DSC-G-014 distinción canonizada).

---

## 9. Aclaraciones de nomenclatura (anti-V25)

- **Sprint TRANSVERSAL-001 NO es lo mismo que Sprint 90 Checkout Stripe.** Son complementarios.
  - TRANSVERSAL-001 implementa `FinanzasLayer.implement()` (T7) en kernel Python con CFDI + accounting.
  - Sprint 90 (`bridge/sprints_propuestos/sprint_90_checkout_stripe_package.md`) extrae el patrón Stripe a paquete TypeScript `@monstruo/checkout-stripe` para apps TS (LikeTickets actual). Distinto stack, distinto scope.
- **TRANSVERSAL-001 cierra 5 stubs simultáneos** (Ventas, Publicidad, Tendencias, Operaciones, Finanzas) + extiende SeoLayer.monitor() con Search Console.
- **TRANSVERSAL-001 NO toca el flujo del Embrión.** La integración del Embrión consumiendo las capas viene en sprint posterior (probablemente Sprint EMBRION-NEEDS-003 o equivalente).

---

## 10. Lo que Cowork T2 NO va a hacer en este sprint (no esperés de mí lo que es tu trabajo)

- NO voy a escribir código de las capas — eso es trabajo T3.
- NO voy a aplicar la migration 0001 desde mi sandbox — vos la corrés con tu acceso a Supabase.
- NO voy a configurar HubSpot/Stripe/Meta/Google/LinkedIn/SAT — vos tenés las credenciales operativas, yo no.
- NO voy a ejecutar el pre-flight check del §7 — vos lo corrés con tus env vars.

Lo que SÍ voy a hacer cuando me notifiques avance:

- Audit DSC-G-008 v2 de tu PR cuando esté en review (mismo protocolo que usé hoy con PR #86 cerrado obsoleto + PR #93 mergeado).
- Si pasa audit verde + autorización T1: mergeo el PR (regla evolucionada 2026-05-11 me lo permite).
- Actualizar `memory/cowork/COWORK_DECISIONES_VIVAS.md` §6 con cifras post-sprint.
- Si encontrás casos T4/T7 que requieren firma de Alfredo, te ayudo a redactar el pedido al bridge para que Alfredo decida rápido.

---

## 11. Frase de arranque

*"Las 8 capas existen como subsistema canónico-pero-callable-por-nadie. Este sprint las hace callable. El Objetivo #9 deja de ser texto."*

---

**Kickoff firmado por:** Cowork T2 (sesión 2026-05-11, post-cierre Sprint CLAUDE_MD-001 commit `e2b1170`).
**Bajo instrucción T1 directa:** Alfredo, 2026-05-11 — "Ejecutor 2 libre ahora, arrancar kickoff TRANSVERSAL-001".
**Spec fuente (leído binariamente antes de redactar este documento):** `bridge/sprints_propuestos/sprint_TRANSVERSAL_001_capas_implement_monitor.md` blob `4159f710149f6a28ae6e38cf1e8fbde776f92bbf`, 14,550 bytes.
