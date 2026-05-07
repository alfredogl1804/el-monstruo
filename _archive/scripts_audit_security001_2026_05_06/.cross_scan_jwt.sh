#!/usr/bin/env bash
# Cross-scan estricto del JWT viejo de service_role en TODOS los repos del usuario alfredogl1804

PATTERN="eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdW16dWh3bWl2amdmdHNuZW92Iiwicm9sZSI6InNlcnZp"
WORKDIR="/tmp/cross_scan_jwt_2026_05_06"
mkdir -p "$WORKDIR"
cd "$WORKDIR" || exit 1

echo "=== CROSS-SCAN JWT service_role del proyecto xsumzuhwmivjgftsneov ==="
echo "Pattern: ${PATTERN:0:30}..."
echo ""

# Listar repos del usuario
REPOS=$(gh repo list alfredogl1804 --limit 50 --json name --jq '.[].name')
TOTAL=$(echo "$REPOS" | wc -l | tr -d ' ')
echo "Total repos a escanear: $TOTAL"
echo ""

HITS_FOUND=()

for repo in $REPOS; do
  echo -n "[$repo] "
  TARGET="$WORKDIR/$repo"
  if [ -d "$TARGET" ]; then
    rm -rf "$TARGET"
  fi
  # Clonar shallow para acelerar
  if gh repo clone "alfredogl1804/$repo" "$TARGET" -- --depth 1 --quiet 2>/dev/null; then
    HITS=$(grep -rl "$PATTERN" "$TARGET" 2>/dev/null | grep -v "/.git/" | grep -v "/node_modules/" | head -10)
    if [ -n "$HITS" ]; then
      echo "🚨 HIT"
      HITS_FOUND+=("$repo")
      echo "    Files:"
      echo "$HITS" | sed "s|$TARGET/|    - |g"
    else
      echo "clean"
    fi
    # Limpiar después del scan para no acumular disco
    rm -rf "$TARGET"
  else
    echo "(clone failed)"
  fi
done

echo ""
echo "=== RESUMEN ==="
if [ ${#HITS_FOUND[@]} -eq 0 ]; then
  echo "✅ Todos los repos limpios (excepto los ya conocidos)"
else
  echo "🚨 Repos con JWT viejo:"
  for r in "${HITS_FOUND[@]}"; do
    echo "  - $r"
  done
fi
