#!/usr/bin/env bash
set -euo pipefail
cd ~/el-monstruo

git stash push -u -m "sprint872-b7-wip" || true
git pull --rebase origin main
git stash pop || true

git add bridge/SPRINT_87_2_OPERATIONAL_GUIDE.md \
  bridge/manus_to_cowork.md \
  scripts/_commit_sprint872_b7.sh

git -c user.name="Manus Memento" \
    -c user.email="manus-memento@el-monstruo.dev" \
    commit -m "docs(sprint872-b7): operational guide + bridge report v1.0 funcional declarado

Cierre formal Sprint 87.2:
- bridge/SPRINT_87_2_OPERATIONAL_GUIDE.md: arquitectura 4 módulos, hotfixes, smoke productivo
- bridge/manus_to_cowork.md: append cierre + declaracion v1.0 backend funcional

Smoke productivo verde: run e2e_1778014574_d260cc
- Deploy real GitHub Pages URL viva
- Critic Visual gemini_vision (no fallback) score 1/100 (juicio honesto sobre placeholder)
- Traffic soberano vigia_status=sovereign_tracking_active

Las 5 deudas del Sprint 87 NUEVO: TODAS CERRADAS.
v1.0 backend funcional - DECLARADO.

Co-authored-by: Manus Memento <manus-memento@el-monstruo.dev>"

git push origin main
git log --oneline -5
