#!/usr/bin/env bash
# =============================================================================
# Sprint 86 Bloque 6 — Setup Railway scheduled task para Catastro cron diario
# =============================================================================
#
# IMPORTANTE: Este script NO EJECUTA nada. Solo imprime las instrucciones para
# que el Hilo Ejecutor configure manualmente el cron en Railway dashboard o vía
# Railway CLI. No ejecutar automáticamente porque:
#
#   1. Requiere Railway CLI autenticado con credenciales del Hilo Ejecutor.
#   2. Crea recursos (servicio cron) que tienen costo.
#   3. Necesita confirmación humana antes del primer run productivo.
#
# Uso:
#   bash scripts/setup_railway_cron_catastro.sh
#
# [Hilo Manus Catastro] · Sprint 86 Bloque 6 · 2026-05-04
# =============================================================================

set -euo pipefail

cat <<'EOF'
================================================================================
  CATASTRO · Configuración del Railway scheduled task (cron diario)
================================================================================

Este es un MANUAL de operación. El script NO toca Railway. Las instrucciones
asumen que ya existe el proyecto el-monstruo en Railway.

────────────────────────────────────────────────────────────────────────────────
  PRE-REQUISITOS (verificar ANTES de configurar el cron)
────────────────────────────────────────────────────────────────────────────────

  [ ] Migrations 016, 018, 019 ejecutadas en Supabase production.
      Verificar con:

        SELECT tablename FROM pg_tables
        WHERE schemaname='public' AND tablename LIKE 'catastro%';

      Esperado: 5 tablas (catastro_modelos, catastro_eventos,
      catastro_curadores, catastro_quorum_log, catastro_run_metrics)
      + 1 vista (catastro_trono_view) + 2 funciones RPC
      (catastro_apply_quorum_outcome, catastro_recompute_trono,
      catastro_recompute_trono_all).

  [ ] fastmcp 3.x instalado en Railway (pip install fastmcp==3.2.4).
      Verificar con: railway run python -c "import fastmcp; print(fastmcp.__version__)"

  [ ] ARTIFICIAL_ANALYSIS_API_KEY configurada en Railway.
      Verificar con: railway variables --service el-monstruo-mvp

  [ ] Primer run manual ejecutado y validado VERDE:
      railway run python3 scripts/run_first_catastro_pipeline.py

  [ ] Smoke E2E contra producción ejecutado y PASS:
      python3 scripts/_smoke_catastro_first_run.py

────────────────────────────────────────────────────────────────────────────────
  OPCIÓN A: Configuración vía Railway Dashboard (RECOMENDADO)
────────────────────────────────────────────────────────────────────────────────

  1. Acceder a https://railway.app/project/<proyecto-el-monstruo>
  2. New Service → Empty Service
  3. Nombre del servicio: catastro-cron
  4. Settings → Cron Schedule:
       Schedule:        0 13 * * *
       Description:     Diariamente 13:00 UTC (07:00 CST México)
  5. Settings → Build Command:
       pip install -r requirements.txt
       (o el comando de build de tu proyecto principal)
  6. Settings → Start Command:
       python -m kernel.catastro.cron
  7. Settings → Variables (heredar del servicio principal o setear explícitas):
       SUPABASE_URL                    = <ya configurada>
       SUPABASE_SERVICE_ROLE_KEY       = <ya configurada>
       ARTIFICIAL_ANALYSIS_API_KEY     = <agregar si falta>
       OPENROUTER_API_KEY              = <opcional>
       HF_TOKEN                        = <opcional>
       CATASTRO_FAILURE_RATE_THRESHOLD = 0.10
       CATASTRO_LOG_LEVEL              = INFO
       MONSTRUO_API_KEY                = <ya configurada>
  8. Deploy y verificar logs del primer run programado (espera hasta las 13:00 UTC).

────────────────────────────────────────────────────────────────────────────────
  OPCIÓN B: Configuración vía Railway CLI
────────────────────────────────────────────────────────────────────────────────

  Asume railway CLI autenticado y proyecto linkeado:

    # 1. Linkear (una vez)
    railway link

    # 2. Crear servicio cron
    railway service create catastro-cron

    # 3. Setear variables (heredar las globales + las específicas)
    railway variables set CATASTRO_FAILURE_RATE_THRESHOLD=0.10 \
                          CATASTRO_LOG_LEVEL=INFO \
                          --service catastro-cron

    # 4. Setear cron schedule (Railway no soporta cron nativo via CLI todavía;
    #    usar Dashboard para esto. Esta opción CLI configura un servicio que
    #    requiere trigger manual o Dashboard cron schedule).

    # 5. Configurar start command
    railway service update --service catastro-cron \
                           --start-command "python -m kernel.catastro.cron"

    # 6. Deploy
    railway up --service catastro-cron

────────────────────────────────────────────────────────────────────────────────
  OPCIÓN C: Cron externo (GitHub Actions, cron-job.org) si Railway cron caro
────────────────────────────────────────────────────────────────────────────────

  Si Railway cron añade costo no deseado, alternativa: usar GitHub Actions
  schedule para llamar al endpoint del cron via HTTP. Ver docs de:
  https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule

  En este caso, exponer un endpoint admin /v1/catastro/cron/trigger en
  kernel/catastro/catastro_routes.py protegido con MONSTRUO_API_KEY que
  internamente llame a kernel.catastro.cron.main().

  No implementado en Bloque 6 — agendado para Bloque 7+ si Railway cron
  resulta inviable.

────────────────────────────────────────────────────────────────────────────────
  POST-CONFIGURACIÓN: Validación
────────────────────────────────────────────────────────────────────────────────

  Después del primer run programado, validar:

    1. Logs de Railway:
       - Buscar "catastro_pipeline_summary" (JSON estructurado)
       - Verificar is_success=true
       - Verificar persist_summary.failure_rate_observed <= 0.10

    2. Smoke E2E manual:
       python3 scripts/_smoke_catastro_first_run.py

    3. Dashboard Catastro (si existe Command Center):
       https://el-monstruo-mvp.up.railway.app/v1/catastro/status
       Esperado: trust_level=healthy, modelos_count > 0

    4. Logs de Supabase:
       SELECT count(*), max(created_at) FROM catastro_eventos
       WHERE evento_tipo IN ('new_model', 'metrica_actualizada');

────────────────────────────────────────────────────────────────────────────────
  ALERTAS
────────────────────────────────────────────────────────────────────────────────

  El cron loggea ERROR (visible en Railway alerting) si:

    - failure_rate_observed > CATASTRO_FAILURE_RATE_THRESHOLD (default 0.10)
      → mensaje: "[catastro_persist_degradation] failure_rate=X% supera ..."

    - hay >0 errores de tipo db_down en error_categories
      → mensaje: "[catastro_persist_db_down] N fallos de tipo db_down ..."

  Configurar Railway alerting para enviar notificación a Discord/Slack ante
  cualquier mensaje con prefijo [catastro_persist_*].

================================================================================

EOF

# Salida con código 0 (instrucciones impresas correctamente)
exit 0
