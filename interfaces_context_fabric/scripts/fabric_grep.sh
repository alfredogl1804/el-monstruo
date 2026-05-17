#!/usr/bin/env bash
# fabric_grep.sh — INTERFACES-CONTEXT-FABRIC-001
# Busca keywords doctrinales del Monstruo en el corpus para mantener vivo el Source Ledger.
# Uso: bash interfaces_context_fabric/scripts/fabric_grep.sh [ROOT] [OUT]
# Defaults: ROOT=. OUT=interfaces_context_fabric/reports/fabric_grep_results.md
set -euo pipefail

ROOT="${1:-.}"
OUT="${2:-interfaces_context_fabric/reports/fabric_grep_results.md}"

mkdir -p "$(dirname "$OUT")"

KEYWORDS=(
  "APP_VISION"
  "VISION_APP_MONSTRUO"
  "interfaces-monstruo-doctrina"
  "Acto 1"
  "Acto 2"
  "AI-First"
  "Schema-First"
  "Transport Cero"
  "Calm Tech"
  "Cronos"
  "Río de Cronos"
  "Reloj Suizo"
  "Engranaje"
  "Methodology-as-a-Service"
  "Curaduría"
  "Daily"
  "Cockpit"
  "Flutter"
  "Command Center"
  "WhatsApp"
  "A2UI"
  "Memento"
  "MOC"
  "Embriones"
  "Soberanía"
  "SMP"
  "Sovereign Memory Protocol"
  "Generative UI"
  "interfaz latente"
  "superficies latentes"
)

{
  echo "# Fabric Grep Results"
  echo
  echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "Root: $ROOT"
  echo "Total keywords: ${#KEYWORDS[@]}"
  echo
} > "$OUT"

for kw in "${KEYWORDS[@]}"; do
  echo "## Keyword: $kw" >> "$OUT"
  echo >> "$OUT"
  echo '```' >> "$OUT"

  if command -v rg >/dev/null 2>&1; then
    rg -n --hidden \
      --glob '!node_modules' \
      --glob '!.git' \
      --glob '!dist' \
      --glob '!build' \
      --glob '!.next' \
      --glob '!.venv' \
      --glob '!__pycache__' \
      --glob '!.dart_tool' \
      --glob '!Pods' \
      --glob '!.claude/worktrees' \
      "$kw" "$ROOT" 2>/dev/null | head -80 >> "$OUT" || true
  else
    grep -RIn \
      --exclude-dir=.git \
      --exclude-dir=node_modules \
      --exclude-dir=dist \
      --exclude-dir=build \
      --exclude-dir=.next \
      --exclude-dir=.venv \
      --exclude-dir=__pycache__ \
      --exclude-dir=.dart_tool \
      --exclude-dir=Pods \
      --exclude-dir=.claude \
      "$kw" "$ROOT" 2>/dev/null | head -80 >> "$OUT" || true
  fi

  echo '```' >> "$OUT"
  echo >> "$OUT"
done

echo "Wrote $OUT"
