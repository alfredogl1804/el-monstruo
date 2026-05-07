#!/usr/bin/env bash
# Scan AI-Pipeline (59 GB) limitado a archivos de código

PIPELINE_DIR="$HOME/AI-Pipeline"
PATTERN_REF="xsumzuhwmivjgftsneov"
PATTERN_JWT="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

cd "$PIPELINE_DIR" || { echo "ERROR: $PIPELINE_DIR no existe"; exit 1; }

echo "=== AI-Pipeline scan limitado a archivos código ==="
echo "Path: $PIPELINE_DIR"
echo ""
echo "=== Tamaño y conteo de archivos código ==="
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.dart" -o -name "*.env*" -o -name ".env*" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" -o -name "*.sh" \) -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/__pycache__/*" -not -path "*/dist/*" -not -path "*/build/*" -not -path "*/.next/*" 2>/dev/null | wc -l | xargs echo "Archivos código a escanear:"
echo ""

echo "=== Mención del project ref xsumzuhwmivjgftsneov ==="
HITS_REF=$(find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.dart" -o -name "*.env*" -o -name ".env*" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" -o -name "*.sh" \) -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/__pycache__/*" -not -path "*/dist/*" -not -path "*/build/*" -not -path "*/.next/*" 2>/dev/null | xargs grep -l "$PATTERN_REF" 2>/dev/null | head -30)
if [ -z "$HITS_REF" ]; then echo "(0 hits)"; else echo "$HITS_REF"; fi
echo ""

echo "=== JWT genérico (header pattern) en archivos con ref ==="
if [ -n "$HITS_REF" ]; then
  echo "$HITS_REF" | while read f; do
    if grep -q "$PATTERN_JWT" "$f" 2>/dev/null; then
      echo "  🚨 $f contiene JWT genérico"
    fi
  done
fi
