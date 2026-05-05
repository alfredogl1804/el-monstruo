#!/usr/bin/env bash
# Sprint 87.2 hotfix B3 — anti-Dory.
set -euo pipefail
cd ~/el-monstruo

git stash push -u -m "sprint872-b3-hotfix-wip" || true
git pull --rebase origin main
git stash pop || true

git add kernel/e2e/critic_visual/gemini_vision.py \
  scripts/_commit_sprint872_b3_hotfix.sh \
  scripts/_smoke_sprint872_e2e.sh

git -c user.name="Manus Memento" \
    -c user.email="manus-memento@el-monstruo.dev" \
    commit -m "fix(sprint872-b3): pasar Pydantic class directa a Gemini (no model_json_schema)

Bug detectado en smoke productivo run 4a4e12 / f71120:
- Gemini API rechaza response_schema con additionalProperties: false
- Pydantic v2 con extra='forbid' emite ese campo siempre
- Causa fallback heuristico_60 en producción a pesar de que screenshot SI se capturó

Fix:
- response_schema=CriticVisualReport (clase directa)
- google-genai 1.x convierte al dialect OpenAPI 3.0 sin additionalProperties

Tests: 9/9 PASS critic_visual.

Co-authored-by: Manus Memento <manus-memento@el-monstruo.dev>"

git push origin main
git log --oneline -3
