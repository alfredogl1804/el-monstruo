#!/bin/bash
# Anti-Dory Sprint 88 Tarea 3.B.1 — Cleanup repos GitHub Pages (archive DSC-S-005)
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Anti-Dory: stash → pull rebase → pop ==="
git stash push -u -m "manus_b_pre_t3b1_$(date +%s)" 2>&1 | tail -3 || true
git pull --rebase origin main 2>&1 | tail -5
git stash pop 2>&1 | tail -3 || true

echo "=== Add files Tarea 3.B.1 ==="
git add scripts/cleanup_github_pages_repos.py \
        scripts/_audit_secrets_before_cleanup.py \
        bridge/manus_to_cowork_CLEANUP_REPOS_S87_2_2026_05_06.md \
        scripts/_commit_sprint88_t3b1.sh

git status -s

echo "=== Commit ==="
git commit -m "feat(sprint88-t3b1): cleanup repos GitHub Pages con archive (DSC-S-005)

Tarea 3.B.1 cerrada — 7 repos monstruo-*-{run_id} archivados (de 12 acumulados
del Sprint 87.2). Quedan 5 activos (los más recientes, incluyendo run d260cc del
smoke productivo final). Política TTL canonizada.

Decisión Magna DSC-S-005 (Cowork firmado 2026-05-06):
Default a archive antes que delete (reversible > irreversible).
- archive solo requiere scope repo (ya disponible)
- delete requiere scope delete_repo (no disponible, evita browser flow)
- Reversible: si en 30 días confirmamos que ninguno hace falta, delete bulk

Archivos:
- scripts/cleanup_github_pages_repos.py: script con --archive (default) y --delete
- scripts/_audit_secrets_before_cleanup.py: Guardrail 2 (verificó 0 archivos
  sospechosos en los 7 repos antes de archive)
- bridge/manus_to_cowork_CLEANUP_REPOS_S87_2_2026_05_06.md: snapshot forense
  completo con los 3 guardrails magna documentados

Verificación post-archive:
- Total monstruo-*: 12
- Activos (no archivados): 5 ✅ (los más recientes)
- Archivados: 7 ✅ (coincide con plan)
- Fallos: 0

Co-authored-by: Manus Memento <manus-memento@el-monstruo.local>"

echo "=== Push ==="
git push origin main 2>&1 | tail -8

echo "=== Log último ==="
git log --oneline -3
