#!/usr/bin/env bash
# Anti-Dory commit Sprint 87.1 Bloque 5 — Operational Guide + Bridge Report
set -euo pipefail
cd ~/el-monstruo

echo "=== STASH ==="
git stash push -u -m "sprint871_b5_pre_pull" || true

echo "=== PULL REBASE ==="
git pull --rebase origin main

echo "=== STASH POP ==="
git stash pop || echo "no stash entries"

echo "=== ADD ==="
git add bridge/SPRINT_87_1_OPERATIONAL_GUIDE.md \
        bridge/manus_to_cowork.md \
        scripts/_commit_sprint871_b5.sh \
        scripts/_smoke_sprint871_e2e.sh \
        tests/test_sprint871_steps_llm_reales.py 2>/dev/null || true

echo "=== STATUS ==="
git status --short

echo "=== COMMIT ==="
git commit -m "docs(sprint871-b5): operational guide + bridge report cierre

Sprint 87.1 cerrado VERDE PRODUCTIVO en ~4h reales.

Cierra 2 de las 5 deudas del Sprint 87 NUEVO:
- Steps LLM reales conectados al Catastro (deuda #1)
- Embriones Tecnico + Ventas reales (deuda #2)

Smoke productivo verificado en Railway production:
  run_id=e2e_1778002670_81cde7
  Steps 4-8 con source=llm_openai (no v1.0 stub)
  Step 7 embrion=embrion_ventas_real
  Step 8 embrion=embrion_tecnico_real

Tests: 44/44 PASS en 85s
Magnitudes: 2,332 LOC nuevas, 8 archivos nuevos, 27 tests nuevos

Co-authored-by: Manus Memento <ejecutor@elmonstruo.local>"

echo "=== PUSH ==="
git push origin main

echo "=== LOG ==="
git log --oneline -6
