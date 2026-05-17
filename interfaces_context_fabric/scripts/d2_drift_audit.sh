#!/usr/bin/env bash
# d2_drift_audit.sh v2 — scopes restrictivos para evitar match-explosion
set -euo pipefail

ROOT="${1:-.}"
OUT="${2:-interfaces_context_fabric/reports/d2_drift_audit.md}"
mkdir -p "$(dirname "$OUT")"

{
  echo "# D2 Drift Audit — código vs doctrina"
  echo
  echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo

  echo "## 1. apps/mobile/lib/ (Flutter source code, NO build/cache)"
  echo
  if [ -d "$ROOT/apps/mobile/lib" ]; then
    echo "### Top-level files in lib/"
    ls "$ROOT/apps/mobile/lib/" 2>/dev/null
    echo
    echo "### Theme / colores hardcoded en lib/"
    grep -rn -E "F97316|1C1917|A8A29E|00E5FF|BB86FC" "$ROOT/apps/mobile/lib/" 2>/dev/null | head -30 || echo "(sin matches)"
  else
    echo "apps/mobile/lib/ NO EXISTE"
  fi
  echo

  echo "## 2. apps/la-forja/"
  echo
  if [ -d "$ROOT/apps/la-forja" ]; then
    ls "$ROOT/apps/la-forja/" 2>/dev/null
    echo
    echo "### subprojects con package.json"
    find "$ROOT/apps/la-forja" -maxdepth 3 -name "package.json" -not -path "*/node_modules/*" 2>/dev/null | head -10
  fi
  echo

  echo "## 3. bridge/ A2UI / AG-UI"
  echo
  ls "$ROOT/bridge/" 2>/dev/null | grep -iE "a2ui|ag.?ui|gateway" || echo "(no archivos a2ui en bridge/)"
  echo

  echo "## 4. kernel/ subdirs"
  echo
  if [ -d "$ROOT/kernel" ]; then
    ls "$ROOT/kernel/" 2>/dev/null
  fi
  echo

  echo "## 5. packages/"
  echo
  if [ -d "$ROOT/packages" ]; then
    ls "$ROOT/packages/" 2>/dev/null
  fi
  echo

  echo "## 6. Capabilities Cap 4 — hits en kernel/ y bridge/"
  echo
  for cap in visual_search photo_intelligence file_intelligence app_intelligence vault shopping ambient_listening smart_notebook cronos manifestation replay; do
    hits=$(grep -rln "$cap" "$ROOT/kernel" "$ROOT/bridge" 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
    echo "- $cap: $hits files"
  done
  echo

  echo "## 7. discovery_forense/PROJECT_MANIFESTS/"
  echo
  if [ -d "$ROOT/discovery_forense/PROJECT_MANIFESTS" ]; then
    ls "$ROOT/discovery_forense/PROJECT_MANIFESTS/" 2>/dev/null | head -30
  fi
} > "$OUT"

wc -l "$OUT"
