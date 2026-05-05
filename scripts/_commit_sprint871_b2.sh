#!/usr/bin/env bash
# Anti-Dory commit Sprint 87.1 Bloque 2 — Embrión Ventas real
set -euo pipefail
cd ~/el-monstruo

echo "=== STASH ==="
git stash push -u -m "sprint871_b2_pre_pull" || true

echo "=== PULL REBASE ==="
git pull --rebase origin main

echo "=== STASH POP ==="
git stash pop || echo "no stash entries"

echo "=== ADD ==="
git add kernel/embriones/ventas/ tests/test_sprint871_embrion_ventas.py scripts/_commit_sprint871_b2.sh

echo "=== STATUS ==="
git status --short

echo "=== COMMIT ==="
git commit -m "feat(sprint871-b2): Embrión Ventas real (LLM-as-parser + heurístico)

Cierra el resto de la deuda #2 del Sprint 87 NUEVO (embriones stubs).

Implementación:
- kernel/embriones/ventas/embrion_ventas.py (NUEVO, ~370 LOC)
  - EmbrionVentasReport Pydantic con extra='forbid'
  - PropuestaValor + PricingTentativo + CanalAdquisicion schemas
  - LLM-as-parser con client.beta.chat.completions.parse (semilla 39)
  - Fallback heurístico determinístico (ICP, pricing, canales)
  - Capa Memento: env var lookup en runtime
  - Brand DNA: EMBRION_VENTAS_LLM_INVALIDO

Tests: 9/9 PASS en 0.03s (3 casos sintéticos + schema validation + fallback)

Spec: bridge/sprint_87_1_preinvestigation/spec_embriones_reales_steps_llm_reales.md
Zona tocada: kernel/embriones/ventas/ (NUEVA)

Co-authored-by: Manus Memento <ejecutor@elmonstruo.local>"

echo "=== PUSH ==="
git push origin main

echo "=== LOG ==="
git log --oneline -3
