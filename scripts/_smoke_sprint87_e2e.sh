#!/usr/bin/env bash
# Smoke productivo Sprint 87 E2E contra Railway
# Ejecuta el pipeline lineal 12 pasos con la frase canónica de Alfredo
# y verifica los 5 endpoints: POST /run, GET /runs, GET /runs/{id}, POST judgment, GET /dashboard
set -euo pipefail

BASE_URL="${BASE_URL:-https://el-monstruo-kernel-production.up.railway.app}"
API_KEY="${MONSTRUO_API_KEY:-}"

if [ -z "$API_KEY" ]; then
  echo "ERROR: MONSTRUO_API_KEY vacío. Ejecutar con: railway run bash scripts/_smoke_sprint87_e2e.sh"
  exit 1
fi

FRASE="Hacé una landing premium para vender pintura al óleo artesanal hecha en Mérida"

echo "===== Smoke Sprint 87 E2E ====="
echo "BASE_URL=$BASE_URL"
echo "FRASE=$FRASE"
echo

# ── Paso 0: /health ────────────────────────────────────────────────
echo "── /health ──"
curl -sS -m 15 "$BASE_URL/health" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  version=',d.get('version'),' uptime=',d.get('uptime_seconds'),'s status=',d.get('status'))"
echo

# ── Paso 1: POST /v1/e2e/run ───────────────────────────────────────
echo "── POST /v1/e2e/run ──"
RUN_RESPONSE=$(curl -sS -m 60 -X POST "$BASE_URL/v1/e2e/run" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{\"frase_input\": \"$FRASE\"}")

echo "$RUN_RESPONSE" | python3 -m json.tool || { echo "ERROR: respuesta no-JSON: $RUN_RESPONSE"; exit 1; }
RUN_ID=$(echo "$RUN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('run_id',''))")
ESTADO_INICIAL=$(echo "$RUN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('estado',''))")
echo
echo "  run_id=$RUN_ID"
echo "  estado_inicial=$ESTADO_INICIAL"

if [ -z "$RUN_ID" ] || [ "$RUN_ID" == "None" ]; then
  echo "ERROR: run_id vacío"
  exit 1
fi
echo

# ── Paso 2: esperar pipeline (steps secuenciales) ──────────────────
echo "── Esperando pipeline (max 90s) ──"
for i in {1..30}; do
  sleep 3
  STATUS_RESPONSE=$(curl -sS -m 15 "$BASE_URL/v1/e2e/runs/$RUN_ID" -H "X-API-Key: $API_KEY")
  ESTADO=$(echo "$STATUS_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('estado',''))" 2>/dev/null || echo "?")
  STEP_ACTUAL=$(echo "$STATUS_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('step_actual',''))" 2>/dev/null || echo "?")
  echo "  [$i] estado=$ESTADO step_actual=$STEP_ACTUAL"
  if [ "$ESTADO" == "awaiting_judgment" ] || [ "$ESTADO" == "completed" ] || [ "$ESTADO" == "failed" ]; then
    break
  fi
done
echo

# ── Paso 3: GET /v1/e2e/runs/{id} ──────────────────────────────────
echo "── GET /v1/e2e/runs/$RUN_ID ──"
curl -sS -m 15 "$BASE_URL/v1/e2e/runs/$RUN_ID" -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo

# ── Paso 4: GET /v1/e2e/runs ───────────────────────────────────────
echo "── GET /v1/e2e/runs ──"
curl -sS -m 15 "$BASE_URL/v1/e2e/runs?limit=5" -H "X-API-Key: $API_KEY" | python3 -c "
import sys, json
d = json.load(sys.stdin)
runs = d.get('runs', d) if isinstance(d, dict) else d
if isinstance(runs, list):
    print(f'  total={len(runs)}')
    for r in runs[:3]:
        print(f'    {r.get(\"run_id\",\"?\")[:8]}... estado={r.get(\"estado\",\"?\")} step={r.get(\"step_actual\",\"?\")}')
else:
    print(json.dumps(d, indent=2)[:500])
"
echo

# ── Paso 5: POST /v1/e2e/runs/{id}/judgment ────────────────────────
if [ "$ESTADO" == "awaiting_judgment" ]; then
  echo "── POST /v1/e2e/runs/$RUN_ID/judgment ──"
  JUDGMENT_RESPONSE=$(curl -sS -m 30 -X POST "$BASE_URL/v1/e2e/runs/$RUN_ID/judgment" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"veredicto": "comercializable", "score": 85, "notas": "smoke test sprint 87"}')
  echo "$JUDGMENT_RESPONSE" | python3 -m json.tool
  echo

  # Verificar estado final
  echo "── Estado final ──"
  curl -sS -m 15 "$BASE_URL/v1/e2e/runs/$RUN_ID" -H "X-API-Key: $API_KEY" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('  estado_final=', d.get('estado'))
print('  veredicto=', d.get('veredicto'))
print('  score=', d.get('score'))
print('  url_publicada=', d.get('url_publicada'))
"
  echo
fi

# ── Paso 6: GET /v1/e2e/dashboard ──────────────────────────────────
echo "── GET /v1/e2e/dashboard ──"
curl -sS -m 15 "$BASE_URL/v1/e2e/dashboard" -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo

echo "===== SMOKE OK ====="
echo "RUN_ID=$RUN_ID"
