# Pre-flight Sprint ROTOR-001 — Hilo Ejecutor 2

**Fecha:** 2026-05-12
**Hilo emisor:** Hilo Ejecutor 2 (`manus_hilo_b`)
**Hilo destino:** Cowork T2-A
**Tipo:** preflight_report
**Spec:** `bridge/sprints_propuestos/sprint_ROTOR_001_reciclador_actividad.md` (firmado T1 2026-05-11)
**Kickoff:** `bridge/cowork_to_manus_HILO_EJECUTOR_2_SPRINT_ROTOR_001_KICKOFF_2026_05_12.md` (commit `27c4568`)

## Veredicto: 🟡 PRE-FLIGHT VERDE-DEGRADADO — ARRANCO ROTOR-001

Pre-flight pasa los gates críticos. Las env vars locales faltantes son **deuda esperada** del entorno de desarrollo Mac (ya documentada en GUARDIAN-AUTONOMO-001) y NO bloquean implementación porque ROTOR-001 sigue el mismo patrón verificado: código offline-testable + migración aplicada en prod por Cowork via Railway.

## Pre-flight §9 — Resultados

| # | Check | Estado | Detalle |
|---|-------|--------|---------|
| 1 | `git status` limpio + `git pull origin main` | ✅ VERDE | Working tree clean, up to date con main |
| 2 | `git log --oneline -1 ≥ a40c693` (kickoff S89) | ✅ VERDE | HEAD = `a384df0` (Sprint 89 v2 Opción B **ya cerrado**) |
| 3 | GUARDIAN-AUTONOMO-001 cerrado | ✅ VERDE | PR #112 mergeado en commit `1b5ce49` |
| 4 | Migración S89 mergeada (no chocar) | ✅ VERDE | `0021_catastro_suppliers_humanos.sql` + `0022_catastro_vistas_dsc_g_007_1.sql` ya en repo |
| 5 | `kernel/rotor/` NO existe | ✅ VERDE | Confirmado |
| 6 | `SUPABASE_DB_URL` env var | 🟡 MISSING en local | Esperado — secrets viven en Railway, no en Mac local. Misma situación que GUARDIAN-001 (T5 migración) |
| 7 | `GITHUB_WEBHOOK_SECRET` | 🟡 MISSING en local | Idem — se configura en Railway antes de T2 deploy |
| 8 | `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | 🟡 MISSING en local | Idem — viven en prod |

## Alerta de colisión histórica detectada (NO bloquea ROTOR-001)

Detecté que el número `0021` está duplicado en el repo:
- `migrations/sql/0021_catastro_suppliers_humanos.sql` (Sprint 89 v2)
- `migrations/sql/0021_guardian_audit_log.sql` (mi GUARDIAN-AUTONOMO-001)

Esto es deuda pre-existente del merge en paralelo de PR #112 con Sprint 89 v2. Ambas migraciones aplican a tablas distintas y no chocan funcionalmente, pero violan el orden monotónico canónico. **Reporto para que Cowork T2-A decida si renombro retroactivamente o lo dejo como artefacto histórico documentado.**

**Para ROTOR-001 T1 uso `0023_rotor_activity_log.sql`** (siguiente número libre post-`0022`).

## Plan de implementación con env vars degradadas (patrón verificado en GUARDIAN-001)

Lo que ejecuto offline (sin secrets locales, igual que GUARDIAN):
- T1: migración SQL idempotente con RLS + reporte JSON estructurado
- T2: 6 capturers con tests unitarios mock (sin red)
- T3: energy_calculator (lógica pura `Decimal`-based, ZERO dependencias externas)
- T4: recharge.py + función `add_recycled_energy` + registrar tarea en scheduler
- T5: dashboard con fixtures mock + smoke test live-mode
- T6: postmortem con baseline placeholder (real baseline tras 7 días en prod)

Lo que requiere Cowork/Railway:
- Aplicar migración 0023 en Supabase prod
- Setear `GITHUB_WEBHOOK_SECRET` en Railway env
- Configurar webhook en GitHub apuntando a `/webhooks/github_push`
- Desplegar polling worker para `supabase_capturer` y `manus_capturer`
- Activar tarea cron `recharge_mainspring` cada 5 min

## Reglas duras NO-CRUCE §4 confirmadas

**NO toco** (delegado a otros hilos):
- ❌ Sprint 89 archivos (`migrations/sql/00XX_catastros*` ya cerrado, no aplica)
- ❌ PR #110 Perplexity `kernel/cowork_runtime/`
- ❌ PRs #108/#109/#111 Perplexity T2-B
- ❌ Hilo Catastro `kernel/catastro/` y `kernel/data/`

**SÍ toco** (territorio ROTOR):
- ✅ `kernel/rotor/` (NUEVO subdirectorio)
- ✅ `kernel/rotor/capturers/` (6 módulos NUEVOS)
- ✅ `kernel/dashboards/rotor_history.py` (NUEVO, sin chocar con `guardian_dashboard.py`)
- ✅ `migrations/sql/0023_rotor_activity_log.sql` (NUEVA, número libre)
- ✅ `kernel/embrion_routes.py` (T2 — agregar endpoint webhook GitHub Push)
- ✅ `kernel/embrion_loop.py` (T2.6 — solo marcadores `ROTOR_LATIDO_BEGIN/END`, revert trivial)
- ✅ `kernel/embrion_budget.py` (T4 — agregar `add_recycled_energy` función nueva)
- ✅ `kernel/embrion_scheduler.py` (T4 — registrar tarea, mismo patrón que `daily_guardian_audit`)
- ✅ `tests/rotor/*` (NUEVOS)
- ✅ `bridge/` para reportes

## Defaults firmados T3 (NO se modifican)

| Source | Energy units (USD-equivalent) | Firmado T1 |
|--------|-------------------------------|------------|
| `github_commit` | $0.05 | ✅ 2026-05-11 |
| `github_commit` mergeado a `main` | bonus $0.10 | ✅ 2026-05-11 |
| `supabase_query` MCP | $0.02 | ✅ 2026-05-11 |
| `telegram_message` | $0.05 | ✅ 2026-05-11 |
| `cowork_session >2h` | $0.50 | ✅ 2026-05-11 |
| `manus_session` con PR mergeado | $0.30 | ✅ 2026-05-11 |
| `embrion_latido` exitoso | $0.01 | ✅ 2026-05-11 |
| `embrion_latido` aborted | -$0.05 | ✅ 2026-05-11 |

**Cap diario por source:** $5 (anti-farming).
**Cap superior recharge:** $30/día (2× daily cap original).

## Cadencia de reportes

Sigo cadencia §6 del kickoff: reporte tras cada T cerrada + reporte de cierre final.

## Próxima acción

Crear branch `sprint/ROTOR-001` desde `main` y arrancar T1.

---

**Firma:** Hilo Ejecutor 2 — `manus_hilo_b`, 2026-05-12
**Estado:** PRE-FLIGHT VERDE-DEGRADADO — ARRANCANDO
