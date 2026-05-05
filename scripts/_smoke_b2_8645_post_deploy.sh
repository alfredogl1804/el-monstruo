#!/bin/bash
# Smoke productivo Sprint 86.4.5 Bloque 2 - re-run Catastro + verify enriquecimiento
set -e
cd /Users/alfredogongora/el-monstruo

echo "=== 1. Cargar variables Railway en bash ==="
eval "$(railway variables --kv 2>/dev/null | grep -E '^(SUPABASE_URL|SUPABASE_SERVICE_KEY|SUPABASE_DB_URL|ARTIFICIAL_ANALYSIS_API_KEY|OPENROUTER_API_KEY)=' | sed 's/^/export /')"
export SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_KEY"

echo "  SUPABASE_URL set: $(test -n "$SUPABASE_URL" && echo yes || echo NO)"
echo "  SUPABASE_SERVICE_ROLE_KEY set: $(test -n "$SUPABASE_SERVICE_ROLE_KEY" && echo yes || echo NO)"
echo "  ARTIFICIAL_ANALYSIS_API_KEY set: $(test -n "$ARTIFICIAL_ANALYSIS_API_KEY" && echo yes || echo NO)"

echo "=== 2. Re-run Catastro con field_mapping activo ==="
source .venv-test/bin/activate
PYTHONPATH=. python scripts/run_first_catastro_pipeline.py 2>&1 | tail -30

echo "=== 3. Query Supabase REST: cobertura de campos métricos ==="
python3 <<'PYEOF'
import os, json, urllib.request

url = os.environ["SUPABASE_URL"].rstrip("/")
key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}

# Leer todos los modelos con quorum
req = urllib.request.Request(
    f"{url}/rest/v1/catastro_modelos?quorum_alcanzado=eq.true&select=id,proveedor,quality_score,reliability_score,cost_efficiency,speed_score,precio_input_per_million,precio_output_per_million",
    headers=headers,
)
rows = json.loads(urllib.request.urlopen(req, timeout=30).read())
total = len(rows)
print(f"Total modelos con quorum: {total}")

if total == 0:
    print("Sin datos.")
    raise SystemExit(0)

def pct(field):
    n = sum(1 for r in rows if r.get(field) is not None)
    return n, round(100.0 * n / total, 1)

for f in ["quality_score","reliability_score","cost_efficiency","speed_score","precio_input_per_million","precio_output_per_million"]:
    n, p = pct(f)
    print(f"  {f:<32} {n:>3}/{total}  ({p:>5}%)")

# Top 5 por reliability
top5 = sorted(rows, key=lambda r: (r.get("reliability_score") or -1, r.get("quality_score") or -1), reverse=True)[:5]
print()
print("Top 5 por reliability_score:")
for r in top5:
    print(f"  - {r['id']:<40} prov={r['proveedor']:<12} qual={r.get('quality_score')} rel={r.get('reliability_score')} cost={r.get('cost_efficiency')} speed={r.get('speed_score')}")
PYEOF

echo "=== Done ==="
