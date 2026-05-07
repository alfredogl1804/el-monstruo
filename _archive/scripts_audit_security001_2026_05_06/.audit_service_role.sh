#!/usr/bin/env bash
# Audit COMPLETO del JWT service_role viejo de Supabase project xsumzuhwmivjgftsneov
# Estrategia: usar el prefijo único del JWT decoded (eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdW16dWh3bWl2amdmdHNuZW92Iiwicm9sZSI6InNlcnZp...)
# para hacer grep amplio sin imprimir el JWT completo.

set +e

# Pattern: el inicio del payload base64-encoded del JWT real (decoded: {"iss":"supabase","ref":"xsumzuhwmivjgftsneov","role":"service")
# Esto es 100% único de este proyecto Supabase y NO matchea otros JWTs.
JWT_PREFIX_PAYLOAD="eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdW16dWh3bWl2amdmdHNuZW92Iiwicm9sZSI6InNlcnZp"

# Pattern más laxo (cualquier JWT con header HS256)
JWT_HEADER="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

REPORT=/tmp/audit_service_role_report.md
echo "# AUDIT JWT service_role — $(date -u +%Y-%m-%dT%H:%M:%SZ)" > $REPORT
echo "" >> $REPORT
echo "Pattern usado: \`${JWT_PREFIX_PAYLOAD:0:20}...\` (payload prefix decoded del JWT real)" >> $REPORT
echo "" >> $REPORT

# === 1. Mac filesystem grep ===
echo "## 1. Mac filesystem (Users/alfredogongora) — excluyendo node_modules, .git, vendor" >> $REPORT
echo "" >> $REPORT
echo "### Hits con payload-prefix exacto del proyecto:" >> $REPORT
echo "" >> $REPORT

cd /Users/alfredogongora 2>/dev/null
grep -rln "$JWT_PREFIX_PAYLOAD" \
  --include="*.py" --include="*.js" --include="*.ts" --include="*.tsx" --include="*.jsx" \
  --include="*.env" --include="*.env.*" --include=".env" --include=".env.*" \
  --include="*.json" --include="*.yaml" --include="*.yml" --include="*.md" \
  --include="*.toml" --include="*.sh" --include="*.txt" --include="*.cfg" --include="*.ini" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor \
  --exclude-dir=.next --exclude-dir=dist --exclude-dir=build \
  --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=venv \
  . 2>/dev/null | head -200 >> $REPORT

echo "" >> $REPORT
echo "Total hits con prefix exacto: $(grep -rl "$JWT_PREFIX_PAYLOAD" --include="*.py" --include="*.js" --include="*.ts" --include="*.env*" --include=".env*" --include="*.json" --include="*.yaml" --include="*.yml" --include="*.md" --include="*.toml" --include="*.sh" --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor . 2>/dev/null | wc -l)" >> $REPORT
echo "" >> $REPORT

cat $REPORT
