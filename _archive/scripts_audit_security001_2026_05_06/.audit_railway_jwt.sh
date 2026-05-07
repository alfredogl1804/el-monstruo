#!/usr/bin/env bash
# Audit Railway env vars buscando JWT viejo de service_role en cada service del proyecto celebrated-achievement

PATTERN="eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzdW16dWh3bWl2amdmdHNuZW92Iiwicm9sZSI6InNlcnZp"

for svc in el-monstruo-kernel ag-ui-gateway command-center el-monstruo worker open-webui Postgres Redis monstruo-bot; do
  echo "--- $svc ---"
  # Capturar todas las variables del service
  ALL_VARS=$(railway variables --service "$svc" 2>/dev/null)
  if [ -z "$ALL_VARS" ]; then
    echo "  (service does not exist or no access)"
    continue
  fi
  # Buscar variables con SUPABASE/SERVICE/JWT en el nombre
  HITS_NAME=$(echo "$ALL_VARS" | grep -iE "(SUPABASE_SERVICE|SUPA_KEY|SERVICE_ROLE|SUPABASE_KEY|JWT|ANON_KEY)" | grep -v "║" | head -10)
  # Buscar el JWT viejo específico por payload prefix
  HITS_JWT=$(echo "$ALL_VARS" | grep -F "$PATTERN" | head -5)

  if [ -n "$HITS_NAME" ]; then
    echo "  Variables candidatas (por nombre):"
    echo "$HITS_NAME" | head -10 | sed -E 's/(eyJ[A-Za-z0-9_-]{4})[A-Za-z0-9._-]+/\1***MASKED***/g'
  fi

  if [ -n "$HITS_JWT" ]; then
    echo "  ⚠️ JWT VIEJO ENCONTRADO en este service. Variables:"
    echo "$HITS_JWT" | sed -E 's/(eyJ[A-Za-z0-9_-]{4})[A-Za-z0-9._-]+/\1***MASKED***/g'
  fi

  if [ -z "$HITS_NAME" ] && [ -z "$HITS_JWT" ]; then
    echo "  clean"
  fi
done
echo "=== DONE ==="
