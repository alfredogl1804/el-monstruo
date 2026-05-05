#!/usr/bin/env bash
set -euo pipefail
cd ~/el-monstruo
git stash push -u -m "sprint872_b5_pre" || true
git pull --rebase origin main
git stash pop || echo "no stash"
git add kernel/e2e/pipeline.py kernel/main.py scripts/_commit_sprint872_b5.sh
git status --short
git commit -m "feat(sprint872-b5): pipeline + main.py integran 4 bloques reales

Pipeline:
- _step_deploy: invoca run_real_deploy(state, run_id) -> GitHub Pages real
  con tracking soberano inyectado, fallback heuristic_preview seguro.
- _step_critic_visual: capture_screenshot(deploy_url) + evaluate_landing()
  con Gemini Vision via Catastro runtime, fallback score 60.
- _step_traffic: confirma instrumentacion soberana activa, expone
  endpoints /v1/traffic/ingest y /v1/traffic/summary/{run_id}.

main.py:
- Monta traffic_router al lado del e2e_router en lifespan.
- Inicializa app.state.traffic_repository = TrafficRepository(db).
- Brand DNA: sprint_872_traffic_initialized / sprint_872_traffic_init_failed.

Capa Memento end-to-end: cada step nuevo tiene fallback determinista,
ninguno bloquea el pipeline si falta un secret externo.

Suite focalizada: 84/84 PASS en 85s
- Sprint 87 E2E pipeline: 17 PASS
- Sprint 87.1 (B1+B2+B3): 27 PASS
- Sprint 87.2 (B1+B2+B3+B4): 40 PASS

Co-authored-by: Manus Memento <ejecutor@elmonstruo.local>"
git push origin main
git log --oneline -5
