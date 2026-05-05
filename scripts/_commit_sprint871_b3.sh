#!/usr/bin/env bash
# Anti-Dory commit Sprint 87.1 Bloque 3 — Steps LLM reales
set -euo pipefail
cd ~/el-monstruo

echo "=== STASH ==="
git stash push -u -m "sprint871_b3_pre_pull" || true

echo "=== PULL REBASE ==="
git pull --rebase origin main

echo "=== STASH POP ==="
git stash pop || echo "no stash entries"

echo "=== ADD ==="
git add kernel/e2e/steps/ kernel/e2e/pipeline.py tests/test_sprint871_steps_llm_reales.py scripts/_commit_sprint871_b3.sh

echo "=== STATUS ==="
git status --short

echo "=== COMMIT ==="
git commit -m "feat(sprint871-b3): Steps LLM reales conectados al Catastro

Cierra deuda #1 del Sprint 87 NUEVO (5 steps LLM eran 'v1.0 stub structured').

Implementación:
- kernel/e2e/steps/llm_step.py (NUEVO, 380 LOC)
  - 7 schemas Pydantic con extra='forbid':
    Concept, ICP, Naming, Branding, Copy, Estrategia, Finanzas
  - run_llm_step: runner async con LLM-as-parser (semilla 39)
  - _call_openai_structured: client.beta.chat.completions.parse
  - _heuristic_fallback: contenido NO trivial determinístico (>50 palabras body_copy)

- kernel/e2e/pipeline.py: _step_llm_generic ahora invoca:
  - VENTAS  → EmbrionVentas real (cierra deuda #2)
  - TECNICO → EmbrionTecnico real (cierra deuda #2)
  - ESTRATEGIA → StepEstrategiaOutput vía LLM real
  - FINANZAS → StepFinanzasOutput vía LLM real
  - CREATIVO → StepBrandingOutput vía LLM real
  - El v1.0 'stub structured' DESAPARECE del pipeline.

Tests: 44/44 PASS en 85s
  - Sprint 87.1 B3 (steps LLM): 9/9
  - Sprint 87.1 B1 (Embrión Técnico): 9/9
  - Sprint 87.1 B2 (Embrión Ventas): 9/9
  - Sprint 87 E2E orchestrator: 17/17

Brand DNA: errores e2e_step_llm_*_failed
Capa Memento: env var OPENAI_API_KEY lookup en runtime
Pydantic: 7 schemas estrictos con extra='forbid' validados

Spec: bridge/sprint_87_1_preinvestigation/spec_embriones_reales_steps_llm_reales.md
Zona tocada: kernel/e2e/steps/ (NUEVA), kernel/e2e/pipeline.py
Zonas NO tocadas: kernel/catastro/, kernel/memento/, apps/mobile/

Co-authored-by: Manus Memento <ejecutor@elmonstruo.local>"

echo "=== PUSH ==="
git push origin main

echo "=== LOG ==="
git log --oneline -4
