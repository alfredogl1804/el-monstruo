#!/bin/bash
set -e
cd /Users/alfredogongora/el-monstruo

echo "=== Stash + pull rebase + pop ==="
git stash --include-untracked || true
git pull --rebase origin main
git stash pop || true
git status --short

echo "=== Add all changes ==="
git add kernel/catastro/sources/artificial_analysis.py \
        scripts/_smoke_b2_8645_post_deploy.sh \
        scripts/_commit_b2_8645.sh \
        scripts/_commit_b2_followup.sh \
        bridge/manus_to_cowork.md

echo "=== Commit ==="
git commit -m "fix(catastro/aa): dual-read intelligence_index + bridge B2 cierre

Sprint 86.4.5 B2 followup — bug residual descubierto en smoke productivo:
La API de Artificial Analysis renombro evaluations.intelligence_index a
evaluations.artificial_analysis_intelligence_index. El primer smoke post-
deploy mostraba quality_score 0/37 a pesar de field_mapping correcto.

Fix con dual-read defensivo en extract_quality_score (mismo patron
que SUPABASE_SERVICE_KEY/_ROLE_KEY en B1).

Resultado smoke productivo final:
  - quality_score:        37/37 (100%)
  - reliability_score:    37/37 (100%)
  - cost_efficiency:      37/37 (100%)
  - speed_score:          37/37 (100%)
  - precio_input/output:  37/37 (100%)

Top 5 cualitativamente coherente (gpt-5-5, claude-opus-4-7,
gemini-3-1-pro-preview, gpt-5-4).

Suite total: 443 PASS + 6 skipped (cero regresiones).

Reporte cierre B2 al bridge: Sprint 86.4.5 Bloque 2 VERDE TOTAL.
Patron capitalizable: dual-read en extract_* de fuentes externas
candidato a heuristica Memento v1.1.

Hilo Manus Memento - 2026-05-05"

echo "=== Push ==="
git push origin main

git log --oneline -3
