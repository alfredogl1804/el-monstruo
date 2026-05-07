#!/usr/bin/env bash
# Scan rápido en repo el-monstruo (solo archivos trackeados via git ls-files)

cd ~/el-monstruo || exit 1

PATTERN_ANON="eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdW16dWh3bWl2amdmdHNuZW92Iiwicm9sZSI6ImFub24i"
PATTERN_SR="eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdW16dWh3bWl2amdmdHNuZW92Iiwicm9sZSI6InNlcnZp"

echo "=== Archivos trackeados ==="
TRACKED=$(git ls-files | wc -l | tr -d ' ')
echo "Total: $TRACKED"
echo ""

echo "=== ANON JWT del proyecto ==="
HITS_ANON=$(git ls-files | xargs grep -l "$PATTERN_ANON" 2>/dev/null)
if [ -z "$HITS_ANON" ]; then echo "(0 hits)"; else echo "$HITS_ANON"; fi
echo ""

echo "=== SERVICE_ROLE JWT del proyecto ==="
HITS_SR=$(git ls-files | xargs grep -l "$PATTERN_SR" 2>/dev/null)
if [ -z "$HITS_SR" ]; then echo "(0 hits)"; else echo "$HITS_SR"; fi
echo ""

echo "=== Cualquier JWT genérico que mencione el proyecto ==="
HITS_REF=$(git ls-files | xargs grep -l "xsumzuhwmivjgftsneov" 2>/dev/null)
if [ -z "$HITS_REF" ]; then echo "(0 hits)"; else echo "$HITS_REF"; fi
echo ""

echo "=== Archivos que importan @supabase/supabase-js o supabase_flutter ==="
HITS_IMP=$(git ls-files | xargs grep -l -E "@supabase/supabase-js|supabase_flutter|createClient.*supabase" 2>/dev/null)
if [ -z "$HITS_IMP" ]; then echo "(0 hits)"; else echo "$HITS_IMP"; fi
