#!/bin/bash
# Eval canónico Sprint 88.1+88.2: 5 frases canónicas, target Critic Score >=80 en 4/5
set -u
if [ -z "${MONSTRUO_API_KEY:-}" ]; then
    echo "ERROR: MONSTRUO_API_KEY no definida (usar railway run para inyectar env)"
    exit 1
fi
KERNEL="https://el-monstruo-kernel-production.up.railway.app"
declare -a FRASES=(
    "Hace una landing premium para vender pintura al oleo artesanal hecha en Merida"
    "Necesito una landing para vender cursos online de programacion en Python para principiantes en LATAM"
    "Quiero promocionar mi cafeteria de especialidad en Polanco con servicio de delivery"
    "Vendemos joyeria artesanal de plata mexicana hecha en Oaxaca, hazme una landing"
    "Lanzamos un servicio de coaching ejecutivo para CTOs de startups, necesito landing"
)
declare -a TAGS=(pintura_oleo_merida cursos_python_latam cafe_polanco joyeria_oaxaca coaching_ctos)
declare -a RUN_IDS=()
echo "=== EVAL SPRINT 88.1+88.2 — 5 FRASES CANONICAS ==="
echo "Kernel: $KERNEL"
echo
for i in "${!FRASES[@]}"; do
    FRASE="${FRASES[$i]}"
    TAG="${TAGS[$i]}"
    PAYLOAD=$(printf '{"frase_input":"%s","metadata":{"smoke":"sprint881_eval","tag":"%s"}}' "$FRASE" "$TAG")
    RESP=$(curl -sS -m 30 -H "X-API-Key: $MONSTRUO_API_KEY" -H "Content-Type: application/json" -d "$PAYLOAD" "$KERNEL/v1/e2e/run" 2>&1 | tail -1)
    RID=$(echo "$RESP" | grep -oE '"run_id":"[^"]+"' | sed 's/.*"run_id":"//;s/"//')
    if [ -z "$RID" ]; then
        echo "[$TAG] FAIL launch: $RESP"
        RUN_IDS+=("FAIL_LAUNCH")
    else
        echo "[$TAG] launched: $RID"
        RUN_IDS+=("$RID")
    fi
done
echo
echo "=== Esperando hasta 600s para completion ==="
sleep 240
for poll in 0 60 120 180 240 300; do
    PENDING=0
    for RID in "${RUN_IDS[@]}"; do
        if [ "$RID" = "FAIL_LAUNCH" ]; then continue; fi
        ROLLUP=$(curl -sS -m 12 -H "X-API-Key: $MONSTRUO_API_KEY" "$KERNEL/v1/e2e/runs/$RID" 2>&1)
        ESTADO=$(echo "$ROLLUP" | grep -oE '"estado":"[^"]+"' | head -1 | sed 's/.*"estado":"//;s/"//')
        if [ "$ESTADO" = "in_progress" ] || [ -z "$ESTADO" ]; then
            PENDING=$((PENDING+1))
        fi
    done
    if [ $PENDING -eq 0 ]; then echo "Todos completaron tras +${poll}s"; break; fi
    echo "Pendientes: $PENDING/${#RUN_IDS[@]} (poll +${poll}s)"
    sleep 60
done
echo
echo "=== RESULTADOS ==="
PASS_COUNT=0
for i in "${!RUN_IDS[@]}"; do
    TAG="${TAGS[$i]}"
    RID="${RUN_IDS[$i]}"
    if [ "$RID" = "FAIL_LAUNCH" ]; then
        echo "[$TAG] FAIL_LAUNCH"
        continue
    fi
    ROLLUP=$(curl -sS -m 12 -H "X-API-Key: $MONSTRUO_API_KEY" "$KERNEL/v1/e2e/runs/$RID" 2>&1)
    SCORE=$(echo "$ROLLUP" | grep -oE '"critic_visual_score":[0-9.]+' | head -1 | sed 's/.*://')
    URL=$(echo "$ROLLUP" | grep -oE '"deploy_url":"[^"]+"' | head -1 | sed 's/.*"deploy_url":"//;s/"//')
    ESTADO=$(echo "$ROLLUP" | grep -oE '"estado":"[^"]+"' | head -1 | sed 's/.*"estado":"//;s/"//')
    SCORE=${SCORE:-null}
    URL=${URL:-null}
    PASS="NO"
    if [ "$SCORE" != "null" ] && [ -n "$SCORE" ]; then
        IS_PASS=$(awk -v s="$SCORE" 'BEGIN { print (s+0 >= 80) ? 1 : 0 }')
        if [ "$IS_PASS" = "1" ]; then
            PASS="YES"
            PASS_COUNT=$((PASS_COUNT+1))
        fi
    fi
    printf "%-22s | RID=%-30s | estado=%-12s | score=%-6s | pass=%-3s | url=%s\n" "$TAG" "$RID" "$ESTADO" "$SCORE" "$PASS" "$URL"
done
echo
echo "=== VEREDICTO: $PASS_COUNT / 5 PASS (target: >=4) ==="
if [ $PASS_COUNT -ge 4 ]; then
    echo "VERDE TECNICO"
    exit 0
else
    echo "AMARILLO/ROJO"
    exit 1
fi
