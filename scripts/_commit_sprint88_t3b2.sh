#!/usr/bin/env bash
# Sprint 88 Tarea 3.B.2 — commit anti-Dory para propagación de deploy_provider.
#
# Patrón:
#   1. stash WIP
#   2. pull --rebase origin main
#   3. stash pop
#   4. add archivos exactos
#   5. commit + push
set -euo pipefail

cd "$(dirname "$0")/.."

STASH_LABEL="manus_b_sprint88_t3b2_wip"

echo "==> 1) git stash WIP (label: ${STASH_LABEL})"
git stash push -u -m "${STASH_LABEL}" || true

echo "==> 2) git pull --rebase origin main"
git pull --rebase origin main

echo "==> 3) git stash pop (best-effort)"
git stash list | grep -q "${STASH_LABEL}" && git stash pop || echo "  no stash to pop"

echo "==> 4) git add (zona Sprint 88 T3.B.2)"
git add \
  kernel/e2e/schema.py \
  kernel/e2e/repository.py \
  kernel/e2e/pipeline.py \
  scripts/029_sprint88_e2e_runs_deploy_provider.sql \
  scripts/run_migration_029.py \
  scripts/_commit_sprint88_t3b2.sh \
  tests/test_sprint88_deploy_provider_propagation.py

echo "==> git status (staged)"
git status --short

echo "==> 5) git commit"
git commit -m "feat(sprint88-t3b2): propagar deploy_provider al rollup del run

- kernel/e2e/schema.py: add deploy_provider: Optional[str] a E2ERun
- kernel/e2e/repository.py: update_run() acepta deploy_provider
- kernel/e2e/pipeline.py: extrae deploy_provider del step 9 y lo persiste
- scripts/029_sprint88_e2e_runs_deploy_provider.sql: ADD COLUMN IF NOT EXISTS + backfill
- scripts/run_migration_029.py: runner idempotente (DATABASE_URL/SUPABASE_DB_URL)
- tests/test_sprint88_deploy_provider_propagation.py: 13 tests (schema + repo + contrato)

Brand DNA: errores e2e_deploy_provider_*_failed / e2e_migration_029_*_failed.
Migration 029 ya aplicada en Supabase production (9/15 runs backfilled).

Cierra Sprint 88 Tarea 3.B.2 (§3 cierre Cowork 2026-05-06)."

echo "==> 6) git push origin main"
git push origin main

echo "==> Done."
