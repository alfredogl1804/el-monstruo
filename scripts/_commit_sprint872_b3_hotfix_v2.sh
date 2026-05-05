#!/usr/bin/env bash
set -euo pipefail
cd ~/el-monstruo

git stash push -u -m "sprint872-b3-v2-wip" || true
git pull --rebase origin main
git stash pop || true

git add kernel/e2e/critic_visual/gemini_vision.py \
  scripts/_commit_sprint872_b3_hotfix_v2.sh

git -c user.name="Manus Memento" \
    -c user.email="manus-memento@el-monstruo.dev" \
    commit -m "fix(sprint872-b3-v2): sanitize Gemini schema (drop additionalProperties + inline \$defs)

Hotfix v2 al critic visual: el SDK google-genai 1.x convierte la clase Pydantic
internamente con model_json_schema() que igual incluye additionalProperties: false.

Solución: pasar schema sanitizado:
- Remover additionalProperties / additional_properties recursivamente
- Inlinear \$defs / \$ref (Gemini no soporta refs internas)
- Quitar title / default (no requeridos)

Validado contra schema real de CriticVisualReport: 0 campos prohibidos.
Tests: 9/9 PASS critic_visual.

Co-authored-by: Manus Memento <manus-memento@el-monstruo.dev>"

git push origin main
git log --oneline -3
