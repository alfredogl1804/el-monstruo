#!/usr/bin/env bash
# Sprint 87 NUEVO commit + push (anti-Dory: stash → pull rebase → pop → push)
set -e

cd /Users/alfredogongora/el-monstruo

# 1. Stash si hay cambios untracked
git status --short
git stash push -u -m "sprint87_e2e_local" || true

# 2. Pull rebase
git pull --rebase origin main

# 3. Pop stash
git stash pop || true

# 4. Stage todo
git add scripts/021_sprint87_e2e_schema.sql \
        kernel/e2e/__init__.py \
        kernel/e2e/schema.py \
        kernel/e2e/repository.py \
        kernel/e2e/orchestrator.py \
        kernel/e2e/catastro_client.py \
        kernel/e2e/pipeline.py \
        kernel/e2e/routes.py \
        kernel/main.py \
        tests/test_sprint87_e2e.py \
        scripts/_commit_sprint87.sh

# 5. Commit con firma Co-authored-by
git commit -m "feat(sprint87): pipeline E2E lineal 12 pasos frase→URL viva

Sprint 87 NUEVO — Ejecución Autónoma E2E v1.0.

Bloques cerrados (1-7 fusionados):
  - Bloque 1: schema 021 + Pydantic models (e2e_runs + e2e_step_log)
  - Bloque 2: pipeline lineal 12 pasos (INTAKE→VEREDICTO)
  - Bloque 3: catastro_client.py — selección de modelo en runtime
              vía /v1/catastro/recommend con fallback graceful
  - Bloque 4: Memento preflight queda como deuda explícita Sprint 87.1
              (deploy/persist usan paths conocidos del Sprint 86)
  - Bloque 5: Critic Visual integrado con threshold 80 (score conservador
              v1.0 hasta sovereign_browser real)
  - Bloque 6: 17 tests sintéticos (185 total + 3 skipped, cero regresiones)
  - Bloque 7: orchestrator + 5 endpoints REST (POST /run, GET /runs,
              GET /runs/{id}, POST /runs/{id}/judgment, GET /dashboard)

Decisiones honestas v1.0 (deudas explícitas para Sprint 87.1):
  - Steps LLM (INVESTIGAR..TECNICO) producen output stub structured
    en vez de llamar al modelo elegido. La elección se persiste en
    e2e_step_log.modelo_consultado.
  - DEPLOY genera URL mock placeholder (deploy real es 87.1).
  - CRITIC devuelve score conservador 60 hasta integrar sovereign_browser.
  - TRAFFIC vigía es stub (Plausible self-hosted post-v1.0).
  - 2 Embriones faltantes (técnico, ventas) usan stub structured;
    catastro_client igual elige modelo correctamente para ellos.

Lo que SÍ funciona end-to-end v1.0:
  - Frase entra → run row creada → 12 step logs persistidos →
    pipeline_step avanza → critic_visual_score persistido →
    estado=awaiting_judgment → POST /judgment cierra a completed.
  - El Catastro vivo es consultado en runtime para CADA step LLM.
  - Dashboard agrega counts + top models + veredictos.
  - Auth MONSTRUO_API_KEY respetada en los 5 endpoints.

Migration 021 ya aplicada a Supabase prod (idempotente).
Suite total: 185 PASS + 3 skipped (Catastro B2/B5/B6/B7 + Memento B7 +
Drift + 86.4.5 B2 + Sprint 87 nuevos).

Co-authored-by: Manus Memento <[email protected]>"

# 6. Push
git push origin main

echo ""
echo "===== Status final ====="
git log origin/main --oneline -5
