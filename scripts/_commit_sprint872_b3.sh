#!/usr/bin/env bash
set -euo pipefail
cd ~/el-monstruo
git stash push -u -m "sprint872_b3_pre" || true
git pull --rebase origin main
git stash pop || echo "no stash"
git add kernel/e2e/critic_visual/ tests/test_sprint87_2_critic_visual.py scripts/_commit_sprint872_b3.sh
git status --short
git commit -m "feat(sprint872-b3): Critic Visual real con Gemini Vision (puente)

Cierra deuda #4 del Sprint 87 NUEVO: stub conservador 60 -> score real 0-100
con Gemini Vision evaluando el screenshot full-page.

Componentes:
- kernel/e2e/critic_visual/gemini_vision.py (~280 LOC):
  * Lee screenshot, valida tamano (cap 5 MB).
  * Catastro elige modelo CRITIC; SDK google-genai con response_schema Pydantic.
  * Multi-model fallback: si modelo elegido no existe, prueba gemini-2.5-pro,
    luego gemini-2.0-flash-exp.
  * Pydantic structured output: score + sub_scores (estetica, cta_claridad,
    jerarquia_visual, profesionalismo) + razones + veredicto.
  * Threshold comercializable=80, rework=50, descartar<50.

Capa Memento aplicada:
- Validacion previa de existencia + tamano del screenshot.
- Si GEMINI_API_KEY ausente / screenshot ausente / API falla -> fallback
  heuristico con score conservador 60 + razon explicita en fallback_reason.
- NUNCA bloquea el pipeline.

Brand DNA: critic_visual_evaluate_*_failed (missing_key, image_too_large,
api_failed).

PUENTE hasta sovereign_browser (Capa 1 Manos magna post-v1.0).

Tests: 9/9 PASS

Co-authored-by: Manus Memento <ejecutor@elmonstruo.local>"
git push origin main
git log --oneline -4
