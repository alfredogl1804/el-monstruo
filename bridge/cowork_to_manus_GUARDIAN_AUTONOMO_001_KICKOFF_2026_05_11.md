---
id: cowork_to_manus_GUARDIAN_AUTONOMO_001_KICKOFF_2026_05_11
fecha: 2026-05-11
emisor: Cowork T2
destinatario: Hilo Ejecutor 1 (manus_hilo_ejecutor_1)
sprint: GUARDIAN-AUTONOMO-001
nombre_completo: "Activación del Guardián de los Objetivos"
spec_firmado: bridge/sprints_propuestos/sprint_GUARDIAN_AUTONOMO_001_activacion.md (commit 582cba5d, estado: firme, fecha_firma_T1: 2026-05-11)
autorizacion_t1: Alfredo 2026-05-11 (firma explícita en chat — "Hilo Ejecutor 1 libre ahora")
delta_esperado_obj_global: +3 pts (Obj #14 sube de 55% a 80%+ — audit CRUCE_DIMENSIONAL_5A §5 #2)
estado: ABIERTO — esperando arranque del ejecutor
---

# Kickoff Sprint GUARDIAN-AUTONOMO-001 — Activación del Guardián de los Objetivos

## 0. Cómo leer este kickoff

Si sos Hilo Ejecutor 1 leyendo esto: **antes de escribir una sola línea de código**, leé en orden:

1. Este documento entero.
2. `bridge/sprints_propuestos/sprint_GUARDIAN_AUTONOMO_001_activacion.md` (spec firmado por Alfredo T1 el 2026-05-11, commit `582cba5d` — **fuente de verdad — 6 tareas T1-T6 con perfil_riesgo declarado**).
3. `memory/cowork/audits/AUDIT_OBJETIVOS_2D_13_a_15_y_CIERRE_FASE2_2026_05_10.md` §5 Gap C1 + §6 L1 (contexto: por qué este sprint es ROI máximo del backlog).
4. `memory/cowork/audits/CRUCE_DIMENSIONAL_5A_2026_05_10.md` §5 #2 (Δ Obj global esperado + dependencias con otros sprints).
5. Código existente del Guardian — **leer, NO modificar**: `kernel/guardian.py` (544 LOC) + `monstruo-memoria/guardian.py` (452 LOC) = 996 LOC totales que este sprint hace cron + scoring + alerting + dashboard sobre ellos.

Si arrancás a codear sin leer los 5, parate. La doctrina del Monstruo es leer antes de escribir.

---

## 1. Contexto mínimo suficiente — por qué este sprint

`kernel/guardian.py` (544 LOC) implementa `GuardianDeObjetivos` desde Sprint 61. Meta-vigilancia + alertas con severidad. **Existe, pero solo corre cuando se invoca a demanda.** Hoy quien audita los 15 Objetivos Maestros del Monstruo es Cowork (yo) **manualmente** en audits por sprint.

Audit `AUDIT_OBJETIVOS_2D` §5 Gap C1 verbatim:

> "**Severidad: alta.** Mientras el Guardian no corra autónomo, Cowork (este hilo) sustituye al Obj #14 con audits manuales por sprint. Esto **ata la salud del proyecto a la disponibilidad de Cowork**. Si Cowork pierde contexto o no está disponible, el sistema deja de auto-vigilarse."

Este sprint cierra exactamente esa dependencia. **Sin código nuevo de fondo.** Wiring de cron + scoring engine + alerting Telegram + dashboard HTML estático sobre los 996 LOC existentes.

**Resultado:**
- Obj #14 (Guardián de los Objetivos) sube de 55% codebase-validated → 80%+
- Δ Obj global del Monstruo: **+3 pts** (audit CRUCE_DIMENSIONAL_5A §5 #2 — ROI máximo del backlog)
- Cowork queda libre del rol de Guardian de facto → puede enfocarse en arquitectura sin ser cuello de botella operativo
- Habilita iteración perpetua del Monstruo

---

## 2. Resumen del spec firmado (NO abrir a debate — ya canonizado por T1)

El spec firmado tiene **6 tareas T1-T6**, cada una con `perfil_riesgo` declarado:

| Tarea | Perfil riesgo | ETA estimada | Resumen |
|---|---|---|---|
| **T1** Wiring del Guardian al `embrion_scheduler` (cron diario) | write-safe | 30-45 min | Registrar `daily_guardian_audit` con frecuencia diaria 06:00 UTC. Handler invoca `GuardianDeObjetivos.run_full_audit()` y persiste en `guardian_audit_log`. |
| **T2** Scoring engine: `% por Objetivo` automático | write-risky | 4-6h (los 15 Objetivos × rúbrica YAML) | `kernel/guardian/scoring.py` con `compute_objective_score(objetivo_id: int) -> ObjectiveScore`. Rúbricas YAML por Objetivo en `kernel/guardian/rubricas/`. Cumple DSC-G-008 v2 (rúbrica + evidencia + denominador + falsadores). |
| **T3** Alerting Telegram en degradación | write-risky | 60 min | Si Δ < -5 pts O status crítico, envía mensaje a Telegram autorizado vía `TelegramNotifier`. **Validation magna `telegram_bot_api_2026` requerida ANTES de codificar (DSC-V-001).** **Bloqueante humano: requiere firma Alfredo para hora/canal antes del flip producción.** |
| **T4** Dashboard HTML estático | write-safe | 60-90 min | `kernel/dashboards/guardian_dashboard.py` replicando patrón `cost_history.py`. CLI standalone. SVG inline + tabla Δ vs baseline + alertas. |
| **T5** Tabla `guardian_audit_log` en Supabase | write-risky | 30 min | Migración SQL `00XX_guardian_audit_log.sql` (siguiente número libre — probable 0015 o 0016 tras renumeración S-003.B). RLS `service_role_only` desde nacimiento. Idempotente. |
| **T6** Pre-commit hook anti-stale-audit | write-safe | 30 min | Hook que verifica `guardian_audit_log` tenga ≥1 row en últimas 24h ANTES de permitir merge de PRs `[feat]` o `[sprint]`. Cowork puede bypassear con `--no-verify` solo bajo instrucción T1 explícita. |

**ETA total declarada en spec:** 2-3 días reales con velocity demostrada.

---

## 3. Criterios de aceptación verificables (10 CA — binariamente demostrables)

Cada criterio debe demostrarse con comando o test. Si no podés demostrarlo, no está hecho.

### CA1 — Tabla `guardian_audit_log` operativa en Supabase

```sql
SELECT count(*) FROM public.guardian_audit_log;
-- Esperado: ≥0 (tabla existe)
SELECT rowsecurity FROM pg_tables WHERE tablename='guardian_audit_log';
-- Esperado: true (RLS habilitada — DSC-S-006 v1.1)
SELECT policyname FROM pg_policies WHERE tablename='guardian_audit_log';
-- Esperado: 'service_role_only'
```

**Importante — DSC-S-012 enforcement:** la migración debe estar en `main` ANTES de aplicarse en producción. **NO ejecutar `sb_sql.py` o `psql` directo desde tu feature branch sin merge previo.** Si la urgencia operacional lo justifica, reportar al bridge con `manus_to_cowork_DERIVA_APLICADA_NNNN_2026_05_11.md` declarando idempotencia garantizada.

### CA2 — Cron diario registrado y ejecutado al menos una vez

```python
from kernel.embrion_scheduler import get_embrion_scheduler
sch = get_embrion_scheduler(db=...)
tasks = sch.get_all_tasks()
daily_guardian = [t for t in tasks if t.name == 'daily_guardian_audit']
assert len(daily_guardian) == 1
assert daily_guardian[0].schedule == 'daily 06:00 UTC'
```

+ `SELECT count(*) FROM guardian_audit_log WHERE created_at > now() - interval '24 hours'` ≥ 1.

### CA3 — Scoring engine: los 15 Objetivos con rúbrica YAML + función Python

```bash
ls kernel/guardian/rubricas/*.yaml | wc -l
# Esperado: 15
pytest tests/test_objective_score.py -v
# Esperado: 15+ tests PASS, 1 por Objetivo
```

Las rúbricas deben cumplir DSC-G-008 v2: rúbrica + evidencia + denominador + falsadores explícitos.

### CA4 — Scoring baseline post-deploy

`reports/scoring_engine_baseline.json` con baseline al 2026-05-12+ (primera ejecución cron post-deploy). Cifras esperadas (referencia, no obligatorias — el scoring puede revelar números distintos a los del audit 2D):

| Objetivo | Audit 2D §4 (10-may) | Esperado scoring 12-may |
|---|---|---|
| #4 No equivocarse 2× | 92% | 90-95% |
| #5 Magna/Premium | 88% | 85-90% |
| #9 Transversalidad | 75% (declarado) / 35.5% (audit 3B real) | 35-45% (codebase-validated) |
| #14 Guardian | 55% | 75-80% (Guardian autónomo activo = bonus) |

### CA5 — Validation magna pre-Telegram

```sql
SELECT * FROM public.validation_log
WHERE claim_type='telegram_bot_api_2026' AND valid_until > now();
-- Esperado: ≥1 row vigente registrada vía record_validation() ANTES de codificar T3
```

### CA6 — Alerting Telegram smoke

Test simulado de degradación verde:
```python
# Manipular score artificialmente para forzar Δ < -5
guardian.set_test_baseline(objetivo=14, pct=85)
guardian.run_full_audit()  # simulado retorna pct=78 → Δ=-7
assert mock_telegram_notifier.calls[-1].message.contains('Δ-7 pts Obj #14')
```

`reports/guardian_alerting_smoke.json` con timestamp + chat_id mock + mensaje serializado.

### CA7 — Dashboard HTML generado contra producción

```bash
python -m kernel.dashboards.guardian_dashboard --output bridge/guardian_dashboard.html
test -s bridge/guardian_dashboard.html
grep -q 'Objetivo #14' bridge/guardian_dashboard.html
grep -q 'SVG' bridge/guardian_dashboard.html
```

`pytest tests/test_guardian_dashboard.py` PASS con ≥8 tests (snapshot, agregaciones temporales, escape XSS, idempotencia, CLI happy/error path).

### CA8 — Pre-commit hook anti-stale activo

Test sintético reproducible:
```bash
# 1. Truncar guardian_audit_log (modo test)
# 2. git commit -m "[feat] test stale guardian"
# 3. Verificar que el commit FALLA con mensaje "Guardian autónomo no ha ejecutado en >24h"
# 4. Insertar row sintético reciente en guardian_audit_log
# 5. git commit retry → DEBE pasar
```

`reports/guardian_anti_stale_hook_test.json` con exit codes.

### CA9 — Seguridad DSC-S-002

- `gitleaks` clean en el diff completo del PR
- Grep manual sobre patches del diff sin matches de `sk_*`, `eyJ`, `sbp_`, `ghp_`, etc.
- `tools/dsc_contract_check.py` PASS sobre cualquier DSC nuevo (no se esperan DSCs nuevos en este sprint)

### CA10 — Audit DSC-G-008 v2 por Cowork verde antes de merge

Cuando el PR esté listo:
- Cowork audita con metodología DSC-G-008 v2 (rúbrica + evidencia + denominador + falsadores)
- Resultado: 🟢 GREEN en los 6 gates (G1-G6)
- Cowork comenta el PR con el audit verbatim
- Cowork mergea bajo regla evolucionada 2026-05-11 (autorización T1 + audit verde)
- **DSC-S-012 enforcement:** Cowork verifica binariamente que `guardian_audit_log` ya existe en prod (o NO existe — ambos casos válidos según orden de aplicación)

**Sin audit verde, el sprint NO se cierra como `🏛️ GUARDIAN-AUTONOMO-001 — DECLARADO`.**

---

## 4. Archivos a tocar / NO tocar

### Tocar (esperado)

- `kernel/guardian/` (subdirectorio nuevo si no existe — el `guardian.py` actual es archivo único, este sprint puede expandir a subdirectorio).
- `kernel/guardian/scoring.py` (nuevo) — scoring engine.
- `kernel/guardian/rubricas/objetivo_N.yaml` (15 archivos nuevos) — rúbricas por Objetivo.
- `kernel/dashboards/guardian_dashboard.py` (nuevo) — replicando patrón de `cost_history.py`.
- `kernel/embrion_scheduler.py` — agregar registración de `daily_guardian_audit` (extensión mínima, no refactor).
- `migrations/sql/00XX_guardian_audit_log.sql` (nuevo) — siguiente número libre. **Verificar slot disponible con `ls migrations/sql/` post-renumeración S-003.B.**
- `scripts/_apply_migration_00XX.py` (nuevo) — siguiendo patrón de `_apply_migration_0011.py`.
- `.pre-commit-config.yaml` — agregar hook anti-stale.
- `tests/test_guardian_scheduler_integration.py`, `tests/test_objective_score.py`, `tests/test_guardian_dashboard.py`, `tests/test_guardian_anti_stale_hook.py` (nuevos).
- `reports/*.json` — generar artifacts requeridos.

### NO TOCAR (zona prohibida)

- `kernel/guardian.py` **EXISTENTE** — solo lectura para entender API actual. Si necesitás extender, hazlo via `kernel/guardian/scoring.py` o módulo nuevo, NO modifiques el `guardian.py` actual.
- `monstruo-memoria/guardian.py` — **función distinta** (Guardian V3 Anti-Compactación para Obj #15). Sigue su roadmap aparte. No tocar.
- `kernel/embrion_loop.py` — Doctrina del silencio. Cero modificaciones.
- `kernel/embrion_budget.py`, `kernel/embrion_self_verifier.py`, `kernel/embrion_write_policy.py`, `kernel/embrion_inbox.py` (nuevo post-PR #94) — operan en flujo paralelo, no tocar.
- `kernel/catastro/` — territorio Hilo Catastro.
- `apps/mobile/` — territorio Hilo Mobile.
- `kernel/transversales/` — territorio Hilo Ejecutor 2 (TRANSVERSAL-001 en ejecución).
- Credenciales — NUNCA.

---

## 5. Pre-flight check obligatorio

ANTES de arrancar T1, correr los 5 comandos del §7 del spec firmado:

```bash
# 1. Repo limpio + main pull
git status && git pull origin main

# 2. Tests verde local
python tests/test_perplexity_decorator.py
pytest tests/test_brand_engine.py  # cobertura tangencial del Guardian existente

# 3. Acceso Supabase + Telegram
test -n "$SUPABASE_DB_URL"
test -n "$TELEGRAM_BOT_TOKEN" && test -n "$TELEGRAM_CHAT_ID"
psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM information_schema.tables WHERE table_name='guardian_audit_log';"
# Esperado: 0 (tabla no existe todavía, T5 la crea)

# 4. Verificar Guardian existente sin tocarlo
wc -l kernel/guardian.py monstruo-memoria/guardian.py
# Esperado: 544 + 452 = 996 LOC

# 5. Verificar scheduler funcional
python -c "from kernel.embrion_scheduler import get_embrion_scheduler; print('ok')"
```

Si cualquier paso falla, NO arrancar. Reportar al bridge con `manus_to_cowork_GUARDIAN_001_PREFLIGHT_FALLO_2026_05_11.md` y esperar dirección.

---

## 6. Protocolo de blocker >30min

Si te encontrás bloqueado >30min en cualquier tarea, **NO sigas atascado en silencio**. Insert directo en `embrion_memoria` vía MCP Supabase:

```sql
INSERT INTO public.embrion_memoria (tipo, contenido, contexto, hilo_origen, importancia)
VALUES (
  'mensaje_alfredo',
  'BLOCKER >30min en Sprint GUARDIAN-AUTONOMO-001. Tarea: T<N>. Descripción: <qué intenté, qué falló, hipótesis del por qué>. Acción requerida de T1: <propuesta concreta de decisión>. Sin acción → bloqueado.',
  jsonb_build_object(
    'sprint', 'GUARDIAN-AUTONOMO-001',
    'tarea', '<T1..T6>',
    'archivo_afectado', '<path>',
    'kickoff', 'bridge/cowork_to_manus_GUARDIAN_AUTONOMO_001_KICKOFF_2026_05_11.md',
    'destinatario', 'alfredo_t1',
    'cc', 'cowork_t2'
  ),
  'manus_hilo_ejecutor_1',
  9
);
```

- `tipo='mensaje_alfredo'` está en el whitelist permitido por la tabla.
- `hilo_origen='manus_hilo_ejecutor_1'` (NOTA: vos sos Ejecutor 1, NO 2 como TRANSVERSAL-001).
- `importancia=9` para blockers reales. NO abusar.
- Esperar respuesta vía `embrion_memoria` con `tipo='mensaje_alfredo'` de Alfredo o vía bridge file `cowork_to_manus_*`.

**Caso especial T3 alerting Telegram — bloqueante humano declarado:** antes de habilitar el bot en producción, generá reporte `bridge/manus_to_cowork_GUARDIAN_T3_FIRMA_REQUERIDA_2026_05_11.md` con: rango de horas permitidas propuesto + canales válidos + tipo de mensajes que va a enviar (severidad + frecuencia esperada). Esperá firma explícita de Alfredo antes del flip.

---

## 7. PR a abrir + naming convención

- **Branch:** `sprint/guardian-autonomo-001-activacion`
- **Base:** `main`
- **PR title:** `feat(guardian): Sprint GUARDIAN-AUTONOMO-001 — Activación del Guardián de los Objetivos`
- **PR body mínimo:**
  - Referencia explícita al spec firmado: `bridge/sprints_propuestos/sprint_GUARDIAN_AUTONOMO_001_activacion.md` (commit `582cba5d` post-firma T1)
  - Tabla de 6 tareas T1-T6 con check pass/fail por tarea
  - Cita verbatim de los 10 CA de este kickoff con evidencia adjunta (paths a `reports/*.json` + outputs SQL)
  - Métricas tests (≥30 nuevos PASS estimado entre T1+T2+T3+T4+T6 tests)
  - `gitleaks` clean en el diff completo
  - Frase canónica de cierre: `🏛️ GUARDIAN-AUTONOMO-001 — DECLARADO (6/6 verde)`
- **Commits:** atómicos por tarea. T1=1 commit, T2=1 commit (o varios si las 15 rúbricas se separan), ..., T6=1 commit.
- **No `git stash` sin issue de seguimiento** (anti-patrón V23 canonizado).
- **DSC-S-012 enforcement (NUEVO firmado hoy):** la migración 0XX debe estar en `main` ANTES de aplicarse a Supabase prod. Si por alguna razón la aplicás antes (NO recomendado), declarar deriva en `manus_to_cowork_DERIVA_APLICADA_GUARDIAN_<fecha>.md`.

---

## 8. Definition of Done (DoD)

El sprint está cerrado cuando se cumple TODO esto y se demuestra binariamente:

- [ ] CA1-CA10 todos en verde con evidencia citada en PR body.
- [ ] 6 tareas T1-T6 PASS, exit 0 con artifacts en `reports/`.
- [ ] `embrion_scheduler` registró `daily_guardian_audit` y ejecutó al menos una vez en producción post-deploy.
- [ ] `guardian_audit_log` tiene ≥1 row real post-deploy (no test fixture).
- [ ] Dashboard HTML generado contra producción + visible en `bridge/guardian_dashboard.html`.
- [ ] Telegram alerting test simulado verde + firma de Alfredo recibida para flip producción real.
- [ ] Cowork audit DSC-G-008 v2 verde (los 6 gates) — comentado verbatim en el PR.
- [ ] `bridge/manus_to_cowork_REPORTE_GUARDIAN_AUTONOMO_001_CIERRE_<fecha>.md` escrito y commiteado (timeline, bugs encontrados, lecciones, firmas recibidas).
- [ ] PR mergeada a `main`. Cowork T2 mergea bajo regla evolucionada 2026-05-11 (audit verde + autorización T1).
- [ ] `memory/cowork/COWORK_DECISIONES_VIVAS.md` §3 actualizada con cifra post-sprint del Obj #14 (esperado: 55% → 80%+) + referencia al PR de cierre.

---

## 9. Aclaraciones de nomenclatura (anti-V25)

- **GUARDIAN-AUTONOMO-001 NO es Sprint 92** — aunque audit 4-may lo llamaba "Sprint 92", esa nomenclatura nunca se canonizó en `bridge/sprints_propuestos/`. Hoy el nombre canónico es `GUARDIAN-AUTONOMO-001`.
- **GUARDIAN-AUTONOMO-001 NO toca `kernel/guardian.py` existente** — agrega `kernel/guardian/` como subdirectorio con scoring/rubricas/dashboard. El archivo existente queda intacto.
- **GUARDIAN-AUTONOMO-001 NO toca `monstruo-memoria/guardian.py`** — ese es Guardian V3 Anti-Compactación para Obj #15. Función distinta. Sigue su roadmap aparte.
- **GUARDIAN-AUTONOMO-001 NO implementa `ComplianceMonitor`** declarado en Sprint 68 — scope posterior. Este sprint solo activa el Guardian existente.

---

## 10. Lo que Cowork T2 NO va a hacer en este sprint (no esperés de mí lo que es tu trabajo)

- NO voy a escribir código del módulo `kernel/guardian/*` — eso es trabajo T3.
- NO voy a aplicar la migración 00XX desde mi sandbox — vos la corrés con tu acceso a Supabase, respetando DSC-S-012.
- NO voy a configurar el bot Telegram en producción — vos generás el reporte, Alfredo firma, vos hacés el flip.
- NO voy a escribir las 15 rúbricas YAML — eso es trabajo T2 del sprint, vos las redactás siguiendo DSC-G-008 v2 y yo audito.

Lo que SÍ voy a hacer cuando me notifiques avance:

- Audit DSC-G-008 v2 de tu PR cuando esté en review (mismo protocolo que usé hoy con PR #86 cerrado obsoleto + PR #94 mergeado + PR #95 mergeado).
- Si pasa audit verde + autorización T1: mergeo el PR (regla evolucionada 2026-05-11 me lo permite).
- Coordinar con Alfredo para firma de T3 alerting Telegram (rango de horas + canal).
- Actualizar `memory/cowork/COWORK_DECISIONES_VIVAS.md` §3 con cifra post-sprint del Obj #14.
- Auditar las 15 rúbricas YAML antes de aprobar T2 (cada rúbrica debe cumplir DSC-G-008 v2).

---

## 11. Frase de arranque

*"Cowork era el Guardian de facto. Este sprint hace que el Monstruo se vigile a sí mismo. Cowork queda libre para arquitectura."*

---

**Kickoff firmado por:** Cowork T2 (sesión 2026-05-11, post firma T1 de SPECS-FIRMA-001 ampliado).
**Bajo instrucción T1 directa:** Alfredo, 2026-05-11 — "Hilo Ejecutor 1 libre ahora, arrancar kickoff GUARDIAN-AUTONOMO-001".
**Spec fuente firmado:** `bridge/sprints_propuestos/sprint_GUARDIAN_AUTONOMO_001_activacion.md` commit `582cba5d`, estado `firme`, fecha_firma_T1 `2026-05-11`.
**DSC nuevo aplicable HOY:** DSC-S-012 (anti-deriva migraciones SQL) firmado por Alfredo T1 el 2026-05-11 commit `891bd20e`. Tu migración T5 debe respetarlo — `.sql` en main ANTES de aplicar a Supabase prod.
