#!/usr/bin/env bash
# Anti-Dory commit Sprint 87.1 Bloque 1 — Embrión Técnico real
set -euo pipefail
cd ~/el-monstruo

echo "=== STASH ==="
git stash push -u -m "sprint871_b1_pre_pull" || true

echo "=== PULL REBASE ==="
git pull --rebase origin main

echo "=== STASH POP ==="
git stash pop || echo "no stash entries"

echo "=== ADD ==="
git add kernel/embriones/tecnico/ tests/test_sprint871_embrion_tecnico.py scripts/_commit_sprint871_b1.sh

echo "=== STATUS ==="
git status --short

echo "=== COMMIT ==="
git commit -m "feat(sprint871-b1): Embrión Técnico real (LLM-as-parser + heurístico)

Cierra parte de la deuda #2 del Sprint 87 NUEVO (embriones stubs).

Implementación:
- kernel/embriones/tecnico/embrion_tecnico.py (NUEVO, 311 LOC)
  - EmbrionTecnicoReport Pydantic con extra='forbid'
  - StackRecomendado + RiesgoTecnico schemas
  - LLM-as-parser con client.beta.chat.completions.parse (semilla 39)
  - Fallback heurístico determinístico (sin OPENAI_API_KEY)
  - Capa Memento: env var lookup en runtime
  - Brand DNA: EMBRION_TECNICO_LLM_INVALIDO

Tests: 9/9 PASS en 0.04s (3 casos sintéticos + schema validation + fallback)
Suite focalizada: 157 passed, 2 skipped en 86s (Sprint 87.1 + 87 E2E + Memento)

Spec: bridge/sprint_87_1_preinvestigation/spec_embriones_reales_steps_llm_reales.md
Zona tocada: kernel/embriones/tecnico/ (NUEVA)
Zonas NO tocadas: kernel/catastro/, kernel/memento/, apps/mobile/

Co-authored-by: Manus Memento <ejecutor@elmonstruo.local>"

echo "=== PUSH ==="
git push origin main

echo "=== LOG ==="
git log --oneline -3
