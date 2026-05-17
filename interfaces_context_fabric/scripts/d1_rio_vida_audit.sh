#!/usr/bin/env bash
# d1_rio_vida_audit.sh — audit exhaustivo de Río de la Vida + Cronos + Niebla del Futuro
set -uo pipefail

ROOT="${1:-/Users/alfredogongora/el-monstruo}"
OUT="${2:-/Users/alfredogongora/el-monstruo/interfaces_context_fabric/reports/d1_rio_vida_audit.md}"

mkdir -p "$(dirname "$OUT")"
{
  echo "# D1 — Audit Río de la Vida / Cronos / Niebla del Futuro"
  echo
  echo "**Generado:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "**Root:** $ROOT"
  echo
} > "$OUT"

# Scopes positivos para no explotar en node_modules
SCOPES=(
  "bridge"
  "memory"
  "discovery_forense"
  "kernel"
  "skills"
  "docs"
  "tools"
  "interfaces_context_fabric"
  "monstruo-memoria"
  "scripts"
  "tests"
  "config"
  "packages/design-tokens"
  "apps/mobile/lib"
)

scope_args=()
for s in "${SCOPES[@]}"; do
  if [ -d "$ROOT/$s" ]; then
    scope_args+=("$ROOT/$s")
  fi
done

KEYWORDS=(
  "Río de la Vida"
  "Rio de la Vida"
  "RIO DE LA VIDA"
  "RÍO DE LA VIDA"
  "rio_de_la_vida"
  "rio-de-la-vida"
  "River of Life"
  "river_of_life"
  "CRONOS_1"
  "CRONOS_2"
  "CRONOS_3"
  "cronos_1"
  "cronos_2"
  "cronos_3"
  "Niebla del Futuro"
  "niebla_del_futuro"
  "niebla del futuro"
  "Cronos"
  "CRONOS"
  "cronos"
  "Memento"
  "MEMENTO"
  "memento"
  "Fototeca"
  "fototeca"
  "Day One"
  "DayOne"
  "day_one"
  "diario"
  "Diario"
  "Renata"
  "Tata"
  "legado"
  "Legado"
  "LEGADO"
  "linea narrativa"
  "narrativa de vida"
  "cuando no esté"
  "para mi hija"
  "fotos familia"
  "videos familia"
  "timelapse"
  "timeline"
  "memoria familiar"
)

for kw in "${KEYWORDS[@]}"; do
  echo "## Keyword: \`$kw\`" >> "$OUT"
  echo >> "$OUT"
  hits=$(grep -rln -F "$kw" "${scope_args[@]}" 2>/dev/null | grep -v "node_modules" | grep -v "/.git/" | sort -u || true)
  if [ -z "$hits" ]; then
    echo "_0 hits_" >> "$OUT"
  else
    n=$(echo "$hits" | wc -l | tr -d ' ')
    echo "**$n archivos:**" >> "$OUT"
    echo '```' >> "$OUT"
    echo "$hits" | head -40 >> "$OUT"
    echo '```' >> "$OUT"
  fi
  echo >> "$OUT"
done

echo "Audit completed. Wrote $OUT"
