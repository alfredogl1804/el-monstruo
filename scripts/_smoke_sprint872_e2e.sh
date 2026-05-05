#!/usr/bin/env bash
# Sprint 87.2 — Smoke productivo end-to-end con frase canonica de Alfredo.
# Verifica: deploy_url real (GitHub Pages o preview), screenshot, critic visual,
# tracking endpoints expuestos, veredicto auto-promocion si score>=80.
set -uo pipefail

API="${1:-https://el-monstruo-production.up.railway.app}"
KEY="${MONSTRUO_API_KEY:-${E2E_API_KEY:-}}"

if [[ -z "$KEY" ]]; then
  echo "ERROR: define MONSTRUO_API_KEY o E2E_API_KEY"
  exit 2
fi

FRASE="Hacé una landing premium para vender pintura al óleo artesanal hecha en Mérida"

echo "=== Sprint 87.2 Smoke productivo ==="
echo "API: $API"
echo "Frase: $FRASE"
echo

echo "[1] POST /v1/e2e/run"
RUN_JSON=$(curl -sS -m 30 -X POST "$API/v1/e2e/run" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"frase_input\": $(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$FRASE"), \"metadata\": {\"smoke\": \"sprint872\"}}")
echo "$RUN_JSON" | python3 -m json.tool 2>/dev/null || echo "$RUN_JSON"

RUN_ID=$(echo "$RUN_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['run_id'])")
echo
echo "RUN_ID=$RUN_ID"
echo

echo "[2] esperando 120s para que pipeline termine 12 steps reales (incluye 45s timeout deploy)..."
sleep 120

echo "[3] GET /v1/e2e/runs/$RUN_ID"
DETAIL=$(curl -sS -m 30 "$API/v1/e2e/runs/$RUN_ID" -H "X-API-Key: $KEY")
echo "$DETAIL" | python3 -m json.tool > /tmp/sprint872_run_detail.json
echo "  guardado en /tmp/sprint872_run_detail.json"

echo
echo "[4] Verificacion deuda #3 DEPLOY REAL:"
python3 - "$DETAIL" <<'PY'
import sys, json
d = json.loads(sys.argv[1])
steps = d.get("steps", [])
deploy = next((s for s in steps if s["step_name"] == "DEPLOY"), None)
if not deploy:
    print("  FAIL: step DEPLOY no presente"); sys.exit(1)
op = deploy.get("output_payload") or {}
url = op.get("deploy_url", "")
provider = op.get("provider", "")
real = op.get("real_deploy", False)
print(f"  deploy_url    = {url}")
print(f"  provider      = {provider}")
print(f"  real_deploy   = {real}")
print(f"  status        = {deploy.get('status')}")
PY

echo
echo "[5] Verificacion deuda #4 CRITIC VISUAL REAL:"
python3 - "$DETAIL" <<'PY'
import sys, json
d = json.loads(sys.argv[1])
steps = d.get("steps", [])
critic = next((s for s in steps if s["step_name"] == "CRITIC"), None)
if not critic:
    print("  FAIL: step CRITIC no presente"); sys.exit(1)
op = critic.get("output_payload") or {}
print(f"  source        = {op.get('source')}")
print(f"  score         = {op.get('score')} (umbral comercializable=80)")
print(f"  veredicto     = {op.get('veredicto')}")
print(f"  modelo_consultado = {op.get('modelo_consultado')}")
sub = op.get("sub_scores") or {}
if sub:
    print(f"  sub_scores    = {sub}")
shot = op.get("screenshot") or {}
if shot:
    print(f"  screenshot    = {shot.get('source')} | path={shot.get('screenshot_path')}")
PY

echo
echo "[6] Verificacion deuda #5 TRAFFIC SOBERANO:"
python3 - "$DETAIL" <<'PY'
import sys, json
d = json.loads(sys.argv[1])
steps = d.get("steps", [])
traffic = next((s for s in steps if s["step_name"] == "TRAFFIC"), None)
if not traffic:
    print("  FAIL: step TRAFFIC no presente"); sys.exit(1)
op = traffic.get("output_payload") or {}
print(f"  vigia_status  = {op.get('vigia_status')}")
print(f"  tracking_endpoint = {op.get('tracking_endpoint')}")
print(f"  observability = {op.get('observability')}")
PY

echo
echo "[7] Estado run + veredicto:"
python3 - "$DETAIL" <<'PY'
import sys, json
d = json.loads(sys.argv[1])
run = d.get("run", {})
print(f"  estado            = {run.get('estado')}")
print(f"  pipeline_step     = {run.get('pipeline_step')}")
print(f"  veredicto_alfredo = {run.get('veredicto_alfredo')}")
print(f"  critic_visual_score = {run.get('critic_visual_score')}")
print(f"  deploy_url        = {run.get('deploy_url')}")
PY

echo
echo "[8] Smoke ingest endpoint /v1/traffic/ingest:"
INGEST_PAYLOAD=$(python3 -c "import json; print(json.dumps({'run_id': '$RUN_ID', 'session_id': 'smoke_test_session', 'event_type': 'pageview', 'url': 'https://example.com/landing', 'device': 'desktop'}))")
INGEST_CODE=$(curl -sS -m 10 -o /dev/null -w "%{http_code}" -X POST "$API/v1/traffic/ingest" \
  -H "Content-Type: application/json" \
  -d "$INGEST_PAYLOAD")
echo "  POST /v1/traffic/ingest -> HTTP $INGEST_CODE"

echo
echo "[9] GET /v1/traffic/summary/$RUN_ID:"
curl -sS -m 10 "$API/v1/traffic/summary/$RUN_ID" | python3 -m json.tool

echo
echo "=== Smoke completado ==="
echo "RUN_ID=$RUN_ID"
