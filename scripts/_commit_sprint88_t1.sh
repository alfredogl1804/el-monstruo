#!/usr/bin/env bash
# Anti-Dory commit Sprint 88 - Tarea 3.A.1 (middleware bypass /v1/traffic/ingest)
set -e
cd ~/el-monstruo
echo "=== git stash untracked + tracked ==="
git stash push -u -m "manus_b_sprint88_t1_pre_pull" || true
echo "=== pull rebase ==="
git pull --rebase origin main
echo "=== stash pop ==="
git stash pop || true
echo "=== add + commit ==="
git add kernel/auth.py tests/test_sprint88_auth_public_ingest.py scripts/_commit_sprint88_t1.sh
git commit -m "feat(sprint88-t3.a.1): bypass middleware para POST /v1/traffic/ingest

Sprint 88 Tarea 3.A.1 (cierre Cowork SESION_2026_05_06_CIERRE.md §3.A.1).

Problema:
APIKeyAuthMiddleware bloqueaba /v1/traffic/ingest con 401, lo que
impedia que el monstruo-tracking.js anonimo desde landings publicas
ingestara eventos. La infraestructura del traffic soberano (Sprint 87.2)
estaba completa pero inalcanzable desde el browser del visitante.

Solucion:
- Anadir frozenset PUBLIC_INGEST_PATHS = {/v1/traffic/ingest}
- Bypass exact-match SOLO para metodo POST (DELETE/GET/PUT siguen protegidos)
- GET /v1/traffic/summary/{run_id} sigue protegido (lectura privada)
- Subpaths como /v1/traffic/ingest/extra NO bypass

Disciplina:
- DSC-G-008 aplicado: tests codifican el contrato de bypass
- Brand DNA: log auth_public_ingest_bypass + e2e_traffic_ingest_public_path
- 9/9 tests verdes (incluido health no rompe + DELETE rechazado + subpath rechazado)

Nota DSC-G-008:
Spec original Sprint 88 (sprints_propuestos/sprint_88_cierre_v1_producto.md)
tenia drift por contaminacion de sub-agente Cowork (mencionaba v0.50.0,
Critic Score 78, /v1/ingest endpoint nuevo). Ejecuto las 4 tareas reales
del §3 del cierre Cowork (cowork_to_manus_SESION_2026_05_06_CIERRE.md).

Co-authored-by: Manus Memento <memento@elmonstruo.dev>"
echo "=== push ==="
git push origin main
echo "=== log ==="
git log --oneline -3
