#!/usr/bin/env bash
#
# verify_embrion_post_fix.sh
#
# Verifica el estado real del embrion-loop usando el genome público
# /v1/genome/now?full=1 (no requiere API key).
#
# Distingue entre:
#   - SANO: running=true, cycle_count avanza, errors=[]
#   - STANDBY INTENCIONAL: running=true, last_trigger.type=mensaje_alfredo con STANDBY
#   - CAÍDO POR ERROR: running=true pero errors[] no vacío con kimi-k2-6 u otro
#   - APAGADO: running=false
#
# Uso:
#   bash scripts/verify_embrion_post_fix.sh

set -euo pipefail

KERNEL="${KERNEL:-https://el-monstruo-kernel-production.up.railway.app}"
SLEEP_SECS="${SLEEP_SECS:-30}"

echo "==> verify_embrion_post_fix.sh"
echo "    kernel: $KERNEL"
echo

# Helper Python para extraer fields del genome
extract() {
  local field="$1"
  python3 - <<PYEOF
import json, sys, urllib.request
try:
    with urllib.request.urlopen("$KERNEL/v1/genome/now?full=1", timeout=60) as r:
        data = json.load(r)
    embrion = data.get('summaries',{}).get('live24h',{}).get('kernel_health',{}).get('components',{}).get('embrion_loop',{})
    val = embrion
    for k in "$field".split('.'):
        if isinstance(val, dict):
            val = val.get(k, None)
        else:
            val = None
            break
    if val is None:
        print("NA")
    elif isinstance(val, (list, dict)):
        print(json.dumps(val))
    else:
        print(val)
except Exception as e:
    print(f"ERROR:{e}", file=sys.stderr)
    sys.exit(2)
PYEOF
}

echo "[1/3] Snapshot 1 del embrion..."
RUN1=$(extract "running")
CYCLE1=$(extract "cycle_count")
ERRORS1=$(extract "errors")
TRIGGER_TYPE1=$(extract "last_trigger.type")
LAST_RESULT1=$(extract "last_result")

echo "    running       : $RUN1"
echo "    cycle_count   : $CYCLE1"
echo "    errors[]      : $(echo "$ERRORS1" | head -c 100)"
echo "    last_trigger  : $TRIGGER_TYPE1"
echo

echo "[2/3] Esperando ${SLEEP_SECS}s para snapshot 2..."
sleep "$SLEEP_SECS"

CYCLE2=$(extract "cycle_count")
ERRORS2=$(extract "errors")

echo "    cycle_count   : $CYCLE2"
echo "    errors[]      : $(echo "$ERRORS2" | head -c 100)"
echo

echo "[3/3] Veredicto..."
echo "============================================================"

# Detectar STANDBY intencional
IS_STANDBY=false
if echo "$LAST_RESULT1" | grep -qi "STANDBY"; then
  IS_STANDBY=true
fi

# Detectar errores activos
HAS_ACTIVE_ERRORS=false
if [ "$ERRORS2" != "[]" ] && [ "$ERRORS2" != "NA" ] && [ -n "$ERRORS2" ]; then
  HAS_ACTIVE_ERRORS=true
fi

# Detectar kimi-k2-6 específicamente
HAS_KIMI_ERROR=false
if echo "$ERRORS2" | grep -qi "kimi-k2-6"; then
  HAS_KIMI_ERROR=true
fi

if [ "$RUN1" != "True" ] && [ "$RUN1" != "true" ]; then
  echo "❌ EMBRION APAGADO"
  echo "    running=$RUN1 — el servicio embrion_loop no está activo en kernel."
  exit 1
fi

if [ "$HAS_KIMI_ERROR" = "true" ]; then
  echo "❌ EMBRION CAÍDO con kimi-k2-6 ACTIVO"
  echo "    El fix nivel 1 no se aplicó o no fue efectivo."
  echo "    Ver: discovery_forense/INCIDENTES/EMBRION_DOWN_2026_05_26_kimi_k2_6_catalog_key_mismatch.md"
  exit 1
fi

if [ "$HAS_ACTIVE_ERRORS" = "true" ]; then
  echo "⚠️  EMBRION CON ERRORES (no kimi)"
  echo "    errors[]: $ERRORS2"
  echo "    Investigar logs Railway servicio embrion-loop."
  exit 1
fi

if [ "$IS_STANDBY" = "true" ]; then
  echo "✅ EMBRION EN STANDBY INTENCIONAL"
  echo "    running=true, errors=[], cycle_count=$CYCLE2"
  echo "    Última instrucción: STANDBY TOTAL (mensaje_alfredo)"
  echo "    Para reanudar: enviar mensaje al embrion con instrucción de reactivación."
  exit 0
fi

if [ "$CYCLE1" != "$CYCLE2" ]; then
  echo "✅ EMBRION SANO Y ACTIVO"
  echo "    cycle_count avanzó: $CYCLE1 → $CYCLE2"
  echo "    errors=[]"
  exit 0
else
  echo "⚠️  EMBRION RUNNING PERO CICLO NO AVANZA"
  echo "    cycle_count estancado en $CYCLE1 durante ${SLEEP_SECS}s"
  echo "    Posible causa: cooldown post-thought (think_cooldown_s=300)"
  echo "    Re-ejecutar con SLEEP_SECS=350 para confirmar."
  exit 0
fi
