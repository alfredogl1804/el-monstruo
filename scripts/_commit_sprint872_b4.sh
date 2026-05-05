#!/usr/bin/env bash
set -euo pipefail
cd ~/el-monstruo
git stash push -u -m "sprint872_b4_pre" || true
git pull --rebase origin main
git stash pop || echo "no stash"
git add kernel/e2e/traffic/ scripts/028_sprint87_2_e2e_traffic_schema.sql scripts/run_migration_028.py tests/test_sprint87_2_traffic.py scripts/_commit_sprint872_b4.sh
git status --short
git commit -m "feat(sprint872-b4): Traffic soberano - migration 028 + repo + endpoints

Cierra deuda #5 del Sprint 87 NUEVO: stub vigia -> instrumentacion propia.
Privacy-first: cero GA, cero Plausible, cookie de primera parte.

Componentes:
- scripts/028_sprint87_2_e2e_traffic_schema.sql: tabla e2e_traffic +3 indices.
- scripts/run_migration_028.py: runner idempotente patron 027.
- kernel/e2e/traffic/repository.py (~190 LOC): TrafficEvent + TrafficRepository
  + TrafficSummary con metricas agregadas (pageviews, sessions, conversion).
- kernel/e2e/traffic/routes.py (~95 LOC):
  POST /v1/traffic/ingest (sin auth, body cap 4 KB, 204 No Content).
  GET  /v1/traffic/summary/{run_id}.

Capa Memento: validacion Pydantic estricta del payload + body size cap +
event_type / device whitelist.

Brand DNA: traffic_ingest_validation_failed, traffic_ingest_persistence_failed.

Tests: 12/12 PASS

Co-authored-by: Manus Memento <ejecutor@elmonstruo.local>"
git push origin main
git log --oneline -4
