#!/bin/bash
# Smoke check no destructivo para ticketlike.mx
# Uso: bash prod_smoke_check.sh

echo "=========================================="
echo "SMOKE CHECK — ticketlike.mx"
echo "=========================================="

# 1. Homepage
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 https://ticketlike.mx/)
if [ "$STATUS" = "200" ]; then
    echo "✅ Homepage: HTTP $STATUS"
else
    echo "❌ Homepage: HTTP $STATUS"
fi

# 2. Admin panel
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 https://ticketlike.mx/admin)
if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ]; then
    echo "✅ Admin panel: HTTP $STATUS"
else
    echo "❌ Admin panel: HTTP $STATUS"
fi

# 3. API events
EVENTS=$(curl -s --max-time 10 "https://ticketlike.mx/api/trpc/events.listWithInventory" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('result',{}).get('data',{}).get('json',[])))" 2>/dev/null)
if [ -n "$EVENTS" ] && [ "$EVENTS" -gt 0 ]; then
    echo "✅ API events: $EVENTS eventos activos"
else
    echo "❌ API events: no responde o 0 eventos"
fi

# 4. DB connection
python3 "$(dirname "$0")/db_connect.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ DB connection: OK"
else
    echo "❌ DB connection: FALLO"
fi

echo "=========================================="
echo "Smoke check completado."
