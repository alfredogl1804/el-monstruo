#!/bin/bash
# Auditar los 7 proyectos Railway de Alfredo via CLI (railway status --json)
set -e

mkdir -p /tmp/railway_audit
cd /tmp/railway_audit

PROJECTS=(
  "forja-monstruo-direct-1777801048"
  "forja-monstruo-direct-1777801110"
  "forja-saludo-v2"
  "forja-marketplace-mate"
  "celebrated-achievement"
  "truthful-freedom"
  "simulador-universal"
)

for P in "${PROJECTS[@]}"; do
  echo "==> $P"
  WORK="/tmp/rwprobe_${P}"
  rm -rf "$WORK" && mkdir -p "$WORK" && cd "$WORK"
  railway link -p "$P" -e production > /dev/null 2>&1
  railway status --json > "/tmp/railway_audit/${P}.json" 2>/dev/null
  cd /tmp/railway_audit
done

echo ""
echo "=== Archivos generados ==="
ls -la /tmp/railway_audit/*.json | grep -v audit.log
