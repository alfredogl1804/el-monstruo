#!/usr/bin/env bash
# d0_legacy_audit_v3.sh — usa grep clásico, no rg (rg está respetando .gitignore extraño)
set -euo pipefail

ROOT="${1:-.}"
OUT="${2:-interfaces_context_fabric/reports/d0_legacy_audit_v3.md}"

mkdir -p "$(dirname "$OUT")"

# Scopes positivos
SCOPES=(
  "bridge"
  "memory"
  "discovery_forense"
  "kernel"
  "skills"
  "docs"
  "tools"
  "migrations"
  "interfaces_context_fabric"
  "monstruo-memoria"
  "scripts"
  "tests"
  "config"
  "agents"
  "packages/design-tokens"
  "apps/la-forja/web/src"
  "apps/la-forja/api/src"
  "apps/mobile/lib"
  "apps/web"
)

build_scope_args() {
  local args=""
  for s in "${SCOPES[@]}"; do
    if [[ -d "$ROOT/$s" ]]; then
      args="$args $ROOT/$s"
    fi
  done
  echo "$args"
}

SCOPE_ARGS=$(build_scope_args)

search_keyword() {
  local kw="$1"
  local title="$2"
  echo "### \`$kw\` ($title)"
  local results
  # shellcheck disable=SC2086
  results=$(grep -rln --binary-files=without-match -F "$kw" $SCOPE_ARGS 2>/dev/null || true)
  if [[ -z "$results" ]]; then
    echo "  (sin matches)"
  else
    local count
    count=$(echo "$results" | wc -l | tr -d ' ')
    echo "  **$count archivos**"
    echo '```'
    echo "$results" | head -30
    if [[ "$count" -gt 30 ]]; then
      echo "... ($count - 30 archivos más)"
    fi
    echo '```'
  fi
  echo ""
}

search_keyword_word() {
  local kw="$1"
  local title="$2"
  echo "### \`$kw\` (whole word, $title)"
  local results
  # shellcheck disable=SC2086
  results=$(grep -rln --binary-files=without-match -w "$kw" $SCOPE_ARGS 2>/dev/null || true)
  if [[ -z "$results" ]]; then
    echo "  (sin matches)"
  else
    local count
    count=$(echo "$results" | wc -l | tr -d ' ')
    echo "  **$count archivos**"
    echo '```'
    echo "$results" | head -30
    if [[ "$count" -gt 30 ]]; then
      echo "... ($count - 30 archivos más)"
    fi
    echo '```'
  fi
  echo ""
}

{
  echo "# D0 Legacy Audit v3 — usando grep clásico"
  echo
  echo "**Generated:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "**Scopes activos:**"
  for s in "${SCOPES[@]}"; do
    if [[ -d "$ROOT/$s" ]]; then
      echo "- \`$s\`"
    fi
  done
  echo ""
  echo "---"
  echo
  echo "## 1. FAMILIA / IDENTIDAD"
  echo
  search_keyword "el-mundo-de-tata" "subdomain del proyecto"
  search_keyword "mundo-de-tata" "alias"
  search_keyword_word "Tata" "nombre"
  search_keyword "Renata" "nombre"
  search_keyword_word "renata" "nombre minúscula"
  search_keyword_word "hija" "relación"
  search_keyword_word "hijos" "relación"
  search_keyword "familia" "concepto"
  search_keyword "Familia" "concepto"
  echo "## 2. LEGADO / NARRATIVA"
  echo
  search_keyword_word "legado" "concepto"
  search_keyword "herencia" "concepto"
  search_keyword "narrativa" "concepto"
  search_keyword "cronista" "rol"
  search_keyword "Cronista" "rol"
  search_keyword "Legacy" "concepto"
  search_keyword "legacy" "concepto"
  echo "## 3. TIEMPO / CRONOS / DIARIO"
  echo
  search_keyword_word "Cronos" "módulo"
  search_keyword "río de vida" "concepto"
  search_keyword "rio de vida" "alias"
  search_keyword "Memento" "módulo"
  search_keyword_word "memento" "minúscula"
  search_keyword "diario" "concepto"
  search_keyword "Diario" "concepto"
  search_keyword "Day One" "app"
  search_keyword "DayOne" "app"
  search_keyword_word "journal" "concepto"
  search_keyword_word "Journal" "concepto"
  search_keyword "timeline" "estructura"
  search_keyword "Timeline" "estructura"
  echo "## 4. MEMORIA / FOTOS / MOMENTOS"
  echo
  search_keyword "fototeca" "módulo"
  search_keyword "Fototeca" "módulo"
  search_keyword "álbum" "concepto"
  search_keyword "Album" "concepto"
  search_keyword "momentos" "concepto"
  search_keyword "Momentos" "concepto"
  search_keyword "recuerdos" "concepto"
  search_keyword "Recuerdos" "concepto"
  search_keyword "memories" "concepto"
  search_keyword "Memories" "concepto"
  echo ""
} > "$OUT"

echo "Done: $OUT ($(wc -l < "$OUT" | tr -d ' ') líneas)"
