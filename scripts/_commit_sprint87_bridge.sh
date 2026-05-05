#!/usr/bin/env bash
# Commit anti-Dory: stash → pull rebase → pop → add → commit → push
# Reporte de cierre Sprint 87 al bridge + smoke script
set -euo pipefail

cd /Users/alfredogongora/el-monstruo

echo "===== git status pre ====="
git status --short

echo "===== stash + pull rebase + pop ====="
STASH_NEEDED=0
if ! git diff --quiet || ! git diff --cached --quiet || git status --porcelain | grep -q '^??'; then
  git stash push -u -m "sprint87_bridge_wip" && STASH_NEEDED=1 || true
fi

git pull --rebase origin main

if [ "$STASH_NEEDED" == "1" ]; then
  git stash pop || true
fi

echo "===== add + commit ====="
git add bridge/manus_to_cowork.md scripts/_smoke_sprint87_e2e.sh scripts/_commit_sprint87_bridge.sh

git commit -m "docs(sprint87): reporte cierre + smoke productivo verde

- Append a bridge/manus_to_cowork.md: reporte de cierre Sprint 87 NUEVO
  con resultados de smoke productivo contra Railway prod.
- run_id e2e_1777956256_cc1a6f: pipeline 12 pasos en ~3s, judgment
  comercializable score=85, estado=completed.
- 5 endpoints verificados (POST /run, GET /runs, GET /runs/{id},
  POST judgment, GET /dashboard).
- Catastro vivo en runtime: gemini-3-1-flash-lite-preview elegido
  para 5 steps LLM, source=catastro, degraded=false.
- 5 deudas explícitas para Sprint 87.1 documentadas (LLM stubs,
  embriones técnico/ventas, deploy mock, critic 60, traffic stub).
- 4 preguntas abiertas para Cowork sobre priorización 87.1.
- scripts/_smoke_sprint87_e2e.sh: anti-TTY-mutilation, reusable
  para runs futuros.

Co-authored-by: Manus Memento <[email protected]>"

echo "===== push ====="
git push origin main

echo "===== log final ====="
git log --oneline -5
