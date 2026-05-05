#!/usr/bin/env bash
set -euo pipefail
cd ~/el-monstruo

echo "=== STASH ==="
git stash push -u -m "sprint872_b1_pre" || true
echo "=== PULL REBASE ==="
git pull --rebase origin main
echo "=== STASH POP ==="
git stash pop || echo "no stash"
echo "=== ADD ==="
git add kernel/e2e/deploy/ tests/test_sprint87_2_real_deploy.py scripts/_commit_sprint872_b1.sh
git status --short
echo "=== COMMIT ==="
git commit -m "feat(sprint872-b1): Deploy real con GitHub Pages + tracking script soberano

Cierra deuda #3 del Sprint 87 NUEVO: DEPLOY mock -> GitHub Pages real.

Componentes:
- kernel/e2e/deploy/real_deploy.py (510 LOC): orquesta render + validacion PII +
  deploy a GitHub Pages via tools/deploy_to_github_pages (Capa 1 Manos reusada).
- Renderer minimal con HTML + CSS Brand DNA + injection de monstruo-tracking.js.
- Capa Memento: validacion pre-deploy bloquea PII obvio (SSN, credit cards,
  API keys) antes de la operacion IRREVERSIBLE.
- Fallback heuristic_preview si GITHUB_TOKEN ausente o provider falla
  (no rompe el pipeline; razon explicita en fallback_reason).
- Tracking script soberano (~150 LOC) inyectado en cada landing.

Tests: 13/13 PASS

Co-authored-by: Manus Memento <ejecutor@elmonstruo.local>"
echo "=== PUSH ==="
git push origin main
git log --oneline -4
