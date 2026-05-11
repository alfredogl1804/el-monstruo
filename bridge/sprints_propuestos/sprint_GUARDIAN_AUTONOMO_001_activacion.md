<!-- lint_strict -->

# Sprint GUARDIAN-AUTONOMO-001 — Activación del Guardián de los Objetivos

**estado:** DRAFT_PENDIENTE_FIRMA_T1
**autor_borrador:** Cowork T2 (Sprint SPECS-FIRMA-001 ampliado, 2026-05-11)
**autorización_T1:** pendiente Alfredo
**Hilo principal:** Manus Ejecutor (wiring) + Cowork (diseño + audit)
**ETA recalibrado:** 2-3 días reales según audit `AUDIT_OBJETIVOS_2D §6 L1` + `CRUCE_DIMENSIONAL_5A §5 #2`
**Objetivo Maestro:** #14 (Guardián de los Objetivos — actualmente al 55% codebase-validated) + #4 (No equivocarse dos veces) + #6 (Vanguardia perpetua) + #15 (Memoria Soberana)
**Bloqueos pre-arranque:** ninguno — todos los inputs en main (`kernel/guardian.py` 544 LOC + `monstruo-memoria/guardian.py` 452 LOC + DSC-G-008 v2 + DSC-G-017)
**Resultado esperado:** Guardian Autónomo corriendo cron diario + scoring por Objetivo + alerting Telegram + dashboard HTML estático. **Cierra la dependencia operativa de Cowork como Guardian de facto.**

---

## 0. Procedencia

`AUDIT_OBJETIVOS_2D_13_a_15_y_CIERRE_FASE2_2026_05_10.md` §5 Gap C1 verbatim:

> "**Severidad: alta.** Mientras el Guardian no corra autónomo, Cowork (este hilo) sustituye al Obj #14 con audits manuales por sprint. Esto **ata la salud del proyecto a la disponibilidad de Cowork**. Si Cowork pierde contexto o no está disponible, el sistema deja de auto-vigilarse. Este audit mismo es prueba — fue Cowork quien tuvo que producirlo, no el Guardian autónomo."

`CRUCE_DIMENSIONAL_5A_2026_05_10.md` §5 #2 verbatim:

> "**Δ Obj global:** +3 pts. **Cierra el Gap C1 magna del audit 2D §5** ('Cowork es Guardian de facto'). Habilita iteración del Monstruo sin Cowork constantemente en el loop. [...] `kernel/guardian.py` (544 LOC) + `monstruo-memoria/guardian.py` (452 LOC) ya existen (996 LOC totales). Falta wiring de cron + scoring engine + alerting + dashboard. **Sin código nuevo de fondo.**"

**ROI máximo declarado del backlog:** libera a Cowork del rol operativo, habilita iteración perpetua del Monstruo.

---

## 1. Audit pre-sprint — Estado actual

Lo que ya existe (verificable por Manus al arrancar):

- `kernel/guardian.py` 544 LOC — `GuardianDeObjetivos` clase Sprint 61. Meta-vigilancia + alertas con severidad. Init en `main.py:926-947`. Wiring básico OK.
- `monstruo-memoria/guardian.py` 452 LOC — Guardian V3 Anti-Compactación Tri-Anchor + OMEGA Memory. Diferente función (protección compactación) pero refuerza Obj #15.
- DSC-G-008 v2 + DSC-G-017 firmados — Gate de Evidencia para canonización + DSC-as-Contract enforzado.
- Los 64 DSCs canonizados en `discovery_forense/CAPILLA_DECISIONES/`.

Lo que falta (gaps verificados):

- Cron diario NO existe — el Guardian solo corre cuando se invoca a demanda.
- Scoring engine NO existe — `% por Objetivo` se calcula manualmente en audits Cowork (audit 2D §4 lo demuestra).
- ComplianceMonitor (declarado en Sprint 68, no implementado) — `grep -rln "ComplianceMonitor\|compliance_monitor" *.py` → 0 hits.
- Alerting Telegram NO existe — `TelegramNotifier` existe (`kernel/runner/telegram_notifier.py` 398 LOC) pero el Guardian no lo invoca.
- Dashboard NO existe — `kernel/dashboards/cost_history.py` (443 LOC) es el patrón existente, replicar.

---

## 2. Tareas del Sprint

### Tarea T1 — Wiring del Guardian al `embrion_scheduler` (cron diario)

**perfil_riesgo:** write-safe

**Descripción:** Registrar tarea `daily_guardian_audit` en `embrion_scheduler` con frecuencia diaria a las 06:00 UTC (alineado con `rls-audit-continuous` que ya corre a esa hora). El handler invoca `GuardianDeObjetivos.run_full_audit()` y persiste resultado en tabla nueva `guardian_audit_log`.

**Criterios de cierre:** `pytest tests/test_guardian_scheduler_integration.py` PASS (mínimo 3 tests: registro de tarea, ejecución del handler, persistencia del resultado). Reporte JSON en `reports/guardian_scheduler_smoke.json` con timestamp de la primera ejecución cron.

### Tarea T2 — Scoring engine: `% por Objetivo` automático

**perfil_riesgo:** write-risky

**Descripción:** Implementar `kernel/guardian/scoring.py` con función `compute_objective_score(objetivo_id: int) -> ObjectiveScore` que devuelve % codebase-validated por Objetivo (los 15 maestros). Cada Objetivo tiene una rúbrica explícita (DSC-G-008 v2 obliga rúbrica + evidencia + denominador + falsadores). Las rúbricas se canonizan en `kernel/guardian/rubricas/<objetivo_N>.yaml`.

**Pre-condiciones:** acceso a Supabase (para contar tablas, RLS, DSCs, etc.) + `git log` para contar PRs mergeados + filesystem para `wc -l` de módulos.

**Criterios de cierre:** los 15 Objetivos tienen rúbrica YAML firmada + función Python que la implementa + test `tests/test_objective_score.py` con caso por Objetivo. Reporte JSON en `reports/scoring_engine_baseline.json` con baseline al 2026-05-12 (= ejecución post-sprint).

### Tarea T3 — Alerting Telegram en degradación

**perfil_riesgo:** write-risky

**Descripción:** Configurar el Guardian para que después de cada ejecución cron, calcule Δ% por Objetivo vs ejecución anterior. Si Δ < -5 pts O status crítico (Capa con dependencia bloqueada nueva), envía mensaje a Telegram autorizado vía `TelegramNotifier` con resumen + link a dashboard.

**Validation magna requerida:** `record_validation("telegram_bot_api_2026", validator="perplexity", evidence_url=...)` ANTES de codificar la integración real (DSC-V-001 enforcement).

**Criterios de cierre:** test simulado de degradación: tomar baseline → manipular score artificialmente → verificar mensaje enviado a chat_id mock. Reporte JSON en `reports/guardian_alerting_smoke.json`.

### Tarea T4 — Dashboard HTML estático (`guardian_dashboard.html`)

**perfil_riesgo:** write-safe

**Descripción:** Replicar el patrón de `kernel/dashboards/cost_history.py` para Guardian: HTML estático con gráfica SVG inline (% por Objetivo histórico), tabla de Δ vs baseline, lista de alertas activas. CLI `python -m kernel.dashboards.guardian_dashboard --output bridge/guardian_dashboard.html`.

**Criterios de cierre:** `pytest tests/test_guardian_dashboard.py` PASS (mínimo 8 tests: snapshot, agregaciones temporales, escape XSS, idempotencia, CLI happy/error path). Reporte JSON en `reports/guardian_dashboard_smoke.json` + snapshot real generado contra producción.

### Tarea T5 — Tabla `guardian_audit_log` en Supabase

**perfil_riesgo:** write-risky

**Descripción:** Migración SQL nueva `migrations/sql/00XX_guardian_audit_log.sql` (siguiente número libre después de derivas DB↔repo resueltas — probablemente 0015 o 0016 si S-003.B renumera). Columnas mínimas: `id`, `created_at`, `objective_id`, `score_pct`, `delta_vs_previous`, `rubrica_version`, `evidence_jsonb`, `status` (CHECK in `'ok','warning','critical','emergency'`), `triggered_alert`. RLS `service_role_only` desde nacimiento (DSC-S-006 v1.1).

**Criterios de cierre:** migración idempotente (`CREATE TABLE IF NOT EXISTS` + `CREATE POLICY IF NOT EXISTS`), tabla con RLS verificada via SQL. Reporte JSON en `reports/migration_guardian_audit_log.json`.

### Tarea T6 — Pre-commit hook anti-stale-audit

**perfil_riesgo:** write-safe

**Descripción:** Hook nuevo que verifica que `guardian_audit_log` tenga al menos 1 row en últimas 24h ANTES de permitir merge de PRs con título `[feat]` o `[sprint]`. Si el Guardian no corrió ayer, el merge se bloquea con mensaje "Guardian autónomo no ha ejecutado en >24h, revisar `embrion_scheduler`". Cowork puede bypassear con `--no-verify` solo bajo instrucción T1 explícita.

**Criterios de cierre:** test sintético: commit `[feat]` con guardian_audit_log vacío → bloqueado. Después de insertar row sintético reciente → pasa. Reporte exit code en `reports/guardian_anti_stale_hook_test.json`.

---

## 3. Contratos ejecutables que adjunta

| DSC enforzado | Contrato producido | Archivo |
|---|---|---|
| DSC-G-008 v2 (Gate de Evidencia) | Rúbricas YAML firmadas por Objetivo | `kernel/guardian/rubricas/objetivo_N.yaml` (15 archivos) |
| DSC-G-017 (DSC-as-Contract) | Tabla `guardian_audit_log` + pre-commit hook anti-stale | migración SQL + `.pre-commit-config.yaml` |
| DSC-V-001 (validación magna) | `record_validation` antes de Telegram Bot API call | `kernel/guardian/scoring.py` |
| Obj #14 (Guardián de los Objetivos) | Cron + scoring + alerting + dashboard end-to-end | `kernel/guardian/*.py` wireado al scheduler |

---

## 4. Criterios de cierre verde (Sprint completo)

- Las 6 tareas en exit 0 con artifacts en `reports/`.
- `embrion_scheduler` registró `daily_guardian_audit` y ejecutó al menos una vez en producción.
- `guardian_audit_log` tiene ≥1 row real (no test fixture) post-deploy.
- Dashboard HTML generado contra producción visible en `bridge/guardian_dashboard.html`.
- Telegram alerting test simulado verde.
- Cowork audita DSC-G-008 v2 sobre el PR antes de mergear.
- Sprint cierra con frase canónica: `🏛️ GUARDIAN-AUTONOMO-001 — DECLARADO (6/6 verde)`.
- `memory/cowork/COWORK_DECISIONES_VIVAS.md` §3 actualizada con cifra post-sprint del Obj #14 (esperado: 55% → 80%+).

---

## 5. Owner

**Owner técnico principal:** Manus Ejecutor (T1-T6 implementación).
**Owner arquitectónico:** Cowork (rúbricas YAML + audit pre-cierre).
**Owner humano final:** Alfredo (firmar T3 antes de habilitar alerting Telegram con bot real).

---

## 6. Trazabilidad

- **Origen:** Audit `AUDIT_OBJETIVOS_2D §5 Gap C1` (severidad alta — Cowork es Guardian de facto) + audit `CRUCE_DIMENSIONAL_5A §5 #2` (ROI máximo del backlog).
- **Sprints anteriores que habilitan este:** Sprint 61 (Guardian inicial `kernel/guardian.py` 544 LOC), Sprint COWORK-RUNTIME-001 (PR #90 — patrón cron + persistencia + flags), Sprint TRANSVERSAL-001 T1 (validation_log table + Supabase wiring — si se ejecuta antes).
- **Sprint que destraba después:** ROTOR-001 (Guardian autónomo es prerrequisito para "autonomía sostenida" — la pieza Rotor del Reloj Suizo necesita un Guardian que valide el sistema mientras el Rotor recicla energía).
- **Delta esperado Obj global:** **+3 pts** (Obj #14 sube de 55% a 80%+ → impacto en agregado).

---

## 7. Pre-flight check (Manus DEBE correr antes de arrancar)

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

Si cualquier paso falla, NO arrancar. Reportar al bridge.

---

## 8. Bloqueante humano declarado

**T3 alerting Telegram requiere firma explícita de Alfredo antes de habilitar el bot en producción.** Razón: alerting puede generar mensajes de madrugada / fines de semana. Alfredo decide rangos de hora permitidos + canales válidos antes del flip.

---

## 9. Nota sobre coexistencia con dependencias

- `monstruo-memoria/guardian.py` (Guardian V3 Anti-Compactación) **NO se toca** en este sprint. Tiene función distinta (protección contra compactación de contexto, Obj #15). Sigue su roadmap aparte.
- El ComplianceMonitor declarado en Sprint 68 (audit 2D §2 lo marca como ausente) **NO se implementa en este sprint**. Es scope posterior — este sprint cubre la activación del Guardian existente, no agrega ComplianceMonitor nuevo.

---

**Firma propuesta de cierre:** sólo válida si las 6 tareas pasan + cron diario ejecutado al menos una vez en producción + dashboard generado contra prod + Cowork audita DSC-G-008 v2 verde. Sin las 4 condiciones, el cierre se queda en `🏛️ GUARDIAN-AUTONOMO-001 — PIPELINE TÉCNICO DECLARADO` (DSC-G-014 distinción canonizada) y el Guardian sigue siendo Cowork de facto hasta que la producción confirme el handoff.

---

**estado:** DRAFT_PENDIENTE_FIRMA_T1 — Alfredo firma cambio a `firme` antes del kickoff a Manus Ejecutor.
