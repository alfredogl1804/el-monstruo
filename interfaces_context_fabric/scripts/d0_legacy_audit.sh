#!/usr/bin/env bash
# d0_legacy_audit.sh
# Búsqueda exhaustiva de cobertura existente para señales T1 sobre legado/familia.
# Versión 2: scopes positivos (whitelist), no exclusiones (blacklist).
# Esto evita match-explosion en node_modules anidados.
#
# Uso: bash interfaces_context_fabric/scripts/d0_legacy_audit.sh
# Output: interfaces_context_fabric/reports/d0_legacy_audit_results.md

set -euo pipefail

ROOT="${1:-.}"
OUT="${2:-interfaces_context_fabric/reports/d0_legacy_audit_results.md}"

mkdir -p "$(dirname "$OUT")"

# Keywords organizados por familia semántica
KW_LEGACY=(
  "legado"
  "herencia"
  "narrativa"
  "Legacy"
  "legacy"
  "Heritage"
  "heritage"
  "cronista"
  "Cronista"
  "cuando yo no esté"
)

KW_FAMILY=(
  "Renata"
  "renata"
  "Tata"
  "tata"
  "el-mundo-de-tata"
  "mundo-de-tata"
  "hija"
  "hijos"
  "familia"
  "Familia"
  "family"
  "Family"
  "historia familiar"
  "memoria familiar"
)

KW_TIME=(
  "Cronos"
  "cronos"
  "río de vida"
  "rio de vida"
  "Memento"
  "memento"
  "timeline"
  "Timeline"
  "diario"
  "Diario"
  "Day One"
  "DayOne"
  "journal"
  "Journal"
)

KW_MEMORY=(
  "álbum"
  "Album"
  "album"
  "Álbum"
  "fototeca"
  "Fototeca"
  "momentos"
  "Momentos"
  "recuerdos"
  "Recuerdos"
  "memories"
  "Memories"
  "carta"
  "futuro"
)

# Scopes positivos: solo escanear estos subdirectorios
# (excluye node_modules, .git, .claude, build, dist, _tmp_*, .venv, etc.)
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
  "apps/mobile/test"
  "apps/web"
)

run_grep() {
  local kw="$1"
  if command -v rg >/dev/null 2>&1; then
    for scope in "${SCOPES[@]}"; do
      if [[ -d "$ROOT/$scope" ]]; then
        rg -n --no-heading -F "$kw" "$ROOT/$scope" 2>/dev/null || true
      fi
    done
  else
    for scope in "${SCOPES[@]}"; do
      if [[ -d "$ROOT/$scope" ]]; then
        grep -RIn "$kw" "$ROOT/$scope" 2>/dev/null || true
      fi
    done
  fi
}

run_section() {
  local section_name="$1"
  shift
  local kws=("$@")

  echo "## Sección: $section_name" >> "$OUT"
  echo >> "$OUT"

  for kw in "${kws[@]}"; do
    echo "### Keyword: \`$kw\`" >> "$OUT"
    local results
    results=$(run_grep "$kw")
    if [[ -z "$results" ]]; then
      echo "  (sin matches)" >> "$OUT"
    else
      echo '```' >> "$OUT"
      echo "$results" | head -100 >> "$OUT"
      local total
      total=$(echo "$results" | wc -l | tr -d ' ')
      if [[ "$total" -gt 100 ]]; then
        echo "" >> "$OUT"
        echo "... (truncated: $total matches total, mostrando primeros 100)" >> "$OUT"
      fi
      echo '```' >> "$OUT"
    fi
    echo >> "$OUT"
  done

  echo >> "$OUT"
}

{
  echo "# D0 — Legacy Coverage Audit Results (v2)"
  echo
  echo "**Generated:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "**Root:** $ROOT"
  echo "**Propósito:** detectar cobertura existente de legado/familia/Cronos/memoria antes de aceptar nuevas capas T1."
  echo "**Scopes whitelist:** ${SCOPES[*]}"
  echo
  echo "---"
  echo
} > "$OUT"

run_section "LEGADO / NARRATIVA" "${KW_LEGACY[@]}"
run_section "FAMILIA / HIJOS" "${KW_FAMILY[@]}"
run_section "TIEMPO / CRONOS / DIARIO" "${KW_TIME[@]}"
run_section "MEMORIA / ÁLBUM / MOMENTOS" "${KW_MEMORY[@]}"

{
  echo "---"
  echo
  echo "## Inventario de scopes escaneados"
  echo
  for scope in "${SCOPES[@]}"; do
    if [[ -d "$ROOT/$scope" ]]; then
      count=$(find "$ROOT/$scope" -type f 2>/dev/null | wc -l | tr -d ' ')
      echo "- \`$scope/\`: $count archivos"
    else
      echo "- \`$scope/\`: NO EXISTE"
    fi
  done
} >> "$OUT"

echo "Wrote $OUT ($(wc -l < "$OUT" | tr -d ' ') líneas)"
