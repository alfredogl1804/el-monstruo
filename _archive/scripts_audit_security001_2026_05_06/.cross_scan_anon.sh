#!/usr/bin/env bash
# Cross-scan ANON JWT del proyecto xsumzuhwmivjgftsneov en TODOS los repos del usuario
# Pattern: payload base64 prefix de un JWT con role:"anon" para ese ref específico

# Decoded payload: {"iss":"supabase","ref":"xsumzuhwmivjgftsneov","role":"anon"...
# Base64-encoded prefix: eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdW16dWh3bWl2amdmdHNuZW92Iiwicm9sZSI6ImFub24i

PATTERN_ANON="eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdW16dWh3bWl2amdmdHNuZW92Iiwicm9sZSI6ImFub24i"
PATTERN_SR="eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdW16dWh3bWl2amdmdHNuZW92Iiwicm9sZSI6InNlcnZp"
WORKDIR="/tmp/cross_scan_anon_2026_05_06"
mkdir -p "$WORKDIR"
cd "$WORKDIR" || exit 1

echo "=== CROSS-SCAN ANON JWT del proyecto xsumzuhwmivjgftsneov ==="
echo "Pattern ANON: ${PATTERN_ANON:0:30}..."
echo "Pattern SR:   ${PATTERN_SR:0:30}..."
echo ""

REPOS=$(gh repo list alfredogl1804 --limit 50 --json name --jq '.[].name')
TOTAL=$(echo "$REPOS" | wc -l | tr -d ' ')
echo "Total repos a escanear: $TOTAL"
echo ""

ANON_HITS=()
SR_HITS=()

for repo in $REPOS; do
  echo -n "[$repo] "
  TARGET="$WORKDIR/$repo"
  rm -rf "$TARGET" 2>/dev/null
  if gh repo clone "alfredogl1804/$repo" "$TARGET" -- --depth 1 --quiet 2>/dev/null; then
    HITS_ANON=$(grep -rl "$PATTERN_ANON" "$TARGET" 2>/dev/null | grep -v "/.git/" | grep -v "/node_modules/" | head -10)
    HITS_SR=$(grep -rl "$PATTERN_SR" "$TARGET" 2>/dev/null | grep -v "/.git/" | grep -v "/node_modules/" | head -10)

    if [ -n "$HITS_ANON" ] || [ -n "$HITS_SR" ]; then
      out_msg=""
      if [ -n "$HITS_ANON" ]; then
        echo -n "🟡 ANON "
        ANON_HITS+=("$repo")
        echo ""
        echo "    Files (ANON):"
        echo "$HITS_ANON" | sed "s|$TARGET/|    - |g"
      fi
      if [ -n "$HITS_SR" ]; then
        echo "    🔴 SERVICE_ROLE en mismo repo. Files:"
        SR_HITS+=("$repo")
        echo "$HITS_SR" | sed "s|$TARGET/|    - |g"
      fi
    else
      echo "clean"
    fi
    rm -rf "$TARGET"
  else
    echo "(clone failed)"
  fi
done

echo ""
echo "=== RESUMEN ==="
echo "Repos con ANON JWT: ${#ANON_HITS[@]}"
for r in "${ANON_HITS[@]}"; do echo "  - $r"; done
echo ""
echo "Repos con SERVICE_ROLE JWT: ${#SR_HITS[@]}"
for r in "${SR_HITS[@]}"; do echo "  - $r"; done
