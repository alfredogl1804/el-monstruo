#!/usr/bin/env bash
# Smoke productivo /v1/catastro/* tras fix Sprint 86.4.5 Bloque 1
# Verifica que el bug `no_db_factory_configured` está cerrado.
set -e

URL="https://el-monstruo-kernel-production.up.railway.app"
KEY=$(railway variables --kv 2>/dev/null | grep '^MONSTRUO_API_KEY=' | cut -d'=' -f2-)

if [ -z "$KEY" ]; then
  echo "ERROR: MONSTRUO_API_KEY no encontrada en Railway"
  exit 1
fi

H_AUTH="X-API-Key: $KEY"
H_JSON="Content-Type: application/json"

echo "=== HEALTH ==="
curl -sS -m 15 "$URL/health" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"version={d.get('version')} uptime={d.get('uptime_seconds')}s healthy={d.get('healthy', d.get('status', 'n/a'))}\")"

echo ""
echo "=== /v1/catastro/status ==="
curl -sS -m 15 -H "$H_AUTH" "$URL/v1/catastro/status" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"trust_level={d.get('trust_level')} modelos={d.get('modelos_count')} dominios={d.get('dominios_count')} degraded={d.get('degraded')} reason={d.get('degraded_reason')}\")
"

echo ""
echo "=== /v1/catastro/recommend (top 5 general) ==="
curl -sS -m 15 -X POST -H "$H_AUTH" -H "$H_JSON" \
  -d '{"use_case":"general","top_n":5,"only_quorum":true}' \
  "$URL/v1/catastro/recommend" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"degraded={d.get('degraded')} reason={d.get('degraded_reason')} modelos_returned={len(d.get('modelos', []))}\")
for m in d.get('modelos', [])[:5]:
    print(f\"  · {m['id']:35s} prov={m['proveedor']:12s} trono={m['trono_global']:.1f} dom={m['dominio']}\")
"

echo ""
echo "=== /v1/catastro/recommend (filtro dominio=llm_frontier) ==="
curl -sS -m 15 -X POST -H "$H_AUTH" -H "$H_JSON" \
  -d '{"use_case":"frontier_chat","dominio":"llm_frontier","top_n":3}' \
  "$URL/v1/catastro/recommend" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"degraded={d.get('degraded')} modelos_returned={len(d.get('modelos', []))}\")
"

echo ""
echo "=== /v1/catastro/dominios ==="
curl -sS -m 15 -H "$H_AUTH" "$URL/v1/catastro/dominios" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"degraded={d.get('degraded')} total_dominios={d.get('total_dominios')}\")
for ma, doms in d.get('macroareas', {}).items():
    for dom in doms:
        print(f\"  · {ma:15s} / {dom['dominio']:20s} → {dom['modelos_count']} modelos\")
"

echo ""
echo "=== /v1/catastro/modelos/gemini-3-1-pro-preview ==="
curl -sS -m 15 -H "$H_AUTH" "$URL/v1/catastro/modelos/gemini-3-1-pro-preview" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"id={d.get('id')} nombre={d.get('nombre')} trono={d.get('trono_global')} estado={d.get('estado')}\")
"

echo ""
echo "=== EXIT VERDE ==="
