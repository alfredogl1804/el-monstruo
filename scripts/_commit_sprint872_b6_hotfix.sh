#!/usr/bin/env bash
# Sprint 87.2 Bloque 6 hotfix — anti-Dory.
set -euo pipefail
cd ~/el-monstruo

# Stash → pull rebase → pop (anti-Dory)
git stash push -u -m "sprint872-b6-hotfix-wip" || true
git pull --rebase origin main
git stash pop || true

git add kernel/e2e/deploy/real_deploy.py \
  tests/test_sprint87_2_real_deploy.py \
  scripts/_check_run_872.py \
  scripts/_smoke_sprint872_e2e.sh \
  scripts/_commit_sprint872_b6_hotfix.sh

git -c user.name="Manus Memento" \
    -c user.email="manus-memento@el-monstruo.dev" \
    commit -m "fix(sprint872-b1): slugify ASCII puro + asyncio timeout 45s en deploy

Hotfix descubierto en smoke productivo:
- slugify dejaba acentos (hacé, mérida) en repo name → GitHub rechazaba
- _deploy_via_github_pages sin timeout → pipeline colgado >5min en step DEPLOY

Cambios:
1. _slugify ahora normaliza unicode → ASCII puro [a-z0-9-]
2. asyncio.wait_for(deploy, timeout=E2E_DEPLOY_TIMEOUT_S || 45)
3. Fallback heuristic_preview con razon github_pages_timeout_45s
4. Test reforzado: assert exact 'forja-pinturas-merida' + regex [a-z0-9-]+

Brand DNA: e2e_deploy_timeout_fallback (nuevo log).

Tests: 84/84 PASS (Sprint 87 + 87.1 + 87.2).

Co-authored-by: Manus Memento <manus-memento@el-monstruo.dev>"

git push origin main
git log --oneline -5
