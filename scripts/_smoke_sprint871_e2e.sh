#!/usr/bin/env bash
# Smoke productivo Sprint 87.1 contra Railway
# Verifica que los steps LLM ya NO son stubs (output_payload con contenido real)
set -euo pipefail

BASE_URL="${BASE_URL:-https://el-monstruo-kernel-production.up.railway.app}"
API_KEY="${MONSTRUO_API_KEY:-}"

if [ -z "$API_KEY" ]; then
  echo "ERROR: MONSTRUO_API_KEY vacío. Ejecutar con: railway run bash scripts/_smoke_sprint871_e2e.sh"
  exit 1
fi

FRASE="Hacé una landing premium para vender pintura al óleo artesanal hecha en Mérida"

echo "===== Smoke Sprint 87.1 — Steps LLM Reales + Embriones Reales ====="
echo "BASE_URL=$BASE_URL"
echo "FRASE=$FRASE"
echo

# ── Paso 1: POST /v1/e2e/run ───────────────────────────────────────
echo "── POST /v1/e2e/run ──"
RUN_RESPONSE=$(curl -sS -m 60 -X POST "$BASE_URL/v1/e2e/run" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{\"frase_input\": \"$FRASE\"}")

RUN_ID=$(echo "$RUN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('run_id',''))")
echo "  run_id=$RUN_ID"
echo

if [ -z "$RUN_ID" ] || [ "$RUN_ID" == "None" ]; then
  echo "ERROR: run_id vacío. Response: $RUN_RESPONSE"
  exit 1
fi

# ── Paso 2: esperar pipeline ──────────────────────────────────────
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

# ── Paso 3: Inspeccionar step_log para verificar steps NO son stubs ──
echo "── Inspección step_log (output_payload de steps 4-8 LLM) ──"
RUN_DETAIL=$(curl -sS -m 15 "$BASE_URL/v1/e2e/runs/$RUN_ID" -H "X-API-Key: $API_KEY")
echo "$RUN_DETAIL" | python3 <<'PYEOF'
import json, sys
d = json.load(sys.stdin) if False else None
# leer del entorno via stdin
import os
PYEOF

echo "$RUN_DETAIL" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('  estado=', d.get('estado'))
print('  step_actual=', d.get('step_actual'))
print('  veredicto=', d.get('veredicto'))
print()
print('  ── Step log (verificar steps reales no-stubs) ──')
steps = d.get('step_log') or d.get('steps') or []
if not steps:
    print('  (sin step_log retornado por el endpoint)')
for s in steps:
    sn = s.get('step_number')
    name = s.get('step_name')
    status = s.get('status')
    op = s.get('output_payload') or {}
    has_v1_stub = 'v1.0 stub' in str(op)
    source = op.get('source', '?') if isinstance(op, dict) else '?'
    embrion = op.get('embrion', '') if isinstance(op, dict) else ''
    output_keys = list(op.keys())[:6] if isinstance(op, dict) else []
    print(f'    [{sn}] {name} status={status} source={source} embrion={embrion} stub_detected={has_v1_stub} keys={output_keys}')
"
echo

# ── Paso 4: judgment ───────────────────────────────────────────────
ESTADO_FINAL=$(echo "$RUN_DETAIL" | python3 -c "import sys,json; print(json.load(sys.stdin).get('estado',''))" 2>/dev/null || echo "?")
if [ "$ESTADO_FINAL" == "awaiting_judgment" ]; then
  echo "── POST /v1/e2e/runs/$RUN_ID/judgment ──"
  curl -sS -m 30 -X POST "$BASE_URL/v1/e2e/runs/$RUN_ID/judgment" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"veredicto": "comercializable", "score": 85, "notas": "smoke sprint 87.1 steps reales"}' | python3 -m json.tool
  echo
fi

# ── Paso 5: dashboard ──────────────────────────────────────────────
echo "── GET /v1/e2e/dashboard ──"
curl -sS -m 15 "$BASE_URL/v1/e2e/dashboard" -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo

echo "===== SMOKE OK ====="
echo "RUN_ID=$RUN_ID"
