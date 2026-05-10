#!/usr/bin/env bash
# DSC-S-002 — Verificación rápida de secrets en archivos del PR Tarea 3.
# Uso: bash scripts/_dsc_s002_check_task3.sh
set -e
cd "$(dirname "$0")/.."

FILES=(
  "kernel/embrion_write_policy.py"
  "kernel/embrion_routes.py"
  "tests/test_embrion_write_policy.py"
  "bridge/EMBRION_WRITE_POLICY_GUIDE.md"
  "migrations/sql/0004_embrion_write_proposals.sql"
  "scripts/_apply_migration_0004.py"
)

PATTERN='sk-[A-Za-z0-9]{20}|eyJ[A-Za-z0-9_-]{30}|service_role|sbp_[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{20}|xoxb-[A-Za-z0-9]+|postgres://.*:.*@'

ERRORS=0
for f in "${FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "MISSING $f"
    ERRORS=$((ERRORS+1))
    continue
  fi
  hits=$(grep -nEi "$PATTERN" "$f" || true)
  if [ -n "$hits" ]; then
    echo "WARN $f:"
    echo "$hits"
    ERRORS=$((ERRORS+1))
  else
    echo "ok $f"
  fi
done

if [ "$ERRORS" -eq 0 ]; then
  echo
  echo "DSC-S-002 PASS — sin secrets detectados."
  exit 0
else
  echo
  echo "DSC-S-002 FAIL — revisar matches arriba."
  exit 1
fi
