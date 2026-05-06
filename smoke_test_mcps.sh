#!/usr/bin/env bash
# Smoke test funcional read-only de los 4 MCPs instalados en Claude Code.
# Verifica que cada credencial efectivamente puede leer datos reales,
# no solo que el proceso de MCP arranque ("Connected").
set -u

PASS=0
FAIL=0
declare -a RESULTS=()

ok()  { echo "[OK]   $1"; PASS=$((PASS+1)); RESULTS+=("[OK]   $1"); }
err() { echo "[FAIL] $1"; FAIL=$((FAIL+1)); RESULTS+=("[FAIL] $1"); }

echo "========================================"
echo "  SMOKE TEST MCPs — $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo ""

# ===== 1. NOTION =====
echo "--- 1/4 NOTION ---"
NOTION_TOKEN=$(security find-generic-password -s "monstruo-notion" -a "token" -w 2>/dev/null)
if [ -z "$NOTION_TOKEN" ]; then
  err "Notion: no se pudo recuperar token de Keychain"
else
  RESP=$(curl -s -w "HTTP:%{http_code}" \
    -H "Authorization: Bearer $NOTION_TOKEN" \
    -H "Notion-Version: 2022-06-28" \
    -H "Content-Type: application/json" \
    -X POST "https://api.notion.com/v1/search" \
    -d '{"query":"MAOC","page_size":3}')
  HTTP=$(echo "$RESP" | grep -oE 'HTTP:[0-9]+' | cut -d: -f2)
  if [ "$HTTP" = "200" ]; then
    COUNT=$(echo "$RESP" | python3 -c "import sys,json; d=json.loads(sys.stdin.read().split('HTTP:')[0]); print(len(d.get('results',[])))" 2>/dev/null)
    if [ -z "$COUNT" ]; then COUNT="0"; fi
    if [ "$COUNT" = "0" ]; then
      ok "Notion API HTTP 200 — pero 0 resultados para 'MAOC' (necesitas conectar páginas a la integración 'Mounstruo Cowoork')"
    else
      ok "Notion API HTTP 200 — $COUNT resultados encontrados para 'MAOC'"
    fi
  else
    err "Notion API HTTP $HTTP"
  fi
fi
echo ""

# ===== 2. SUPABASE =====
echo "--- 2/4 SUPABASE ---"
SUPABASE_PAT=$(security find-generic-password -s "monstruo-supabase" -a "pat" -w 2>/dev/null)
PROJECT_REF=$(security find-generic-password -s "monstruo-supabase" -a "project_ref" -w 2>/dev/null)
if [ -z "$SUPABASE_PAT" ]; then
  err "Supabase: no se pudo recuperar PAT de Keychain"
else
  # Test 1: Management API — listar proyectos
  RESP=$(curl -s -w "HTTP:%{http_code}" \
    -H "Authorization: Bearer $SUPABASE_PAT" \
    "https://api.supabase.com/v1/projects")
  HTTP=$(echo "$RESP" | grep -oE 'HTTP:[0-9]+' | cut -d: -f2)
  if [ "$HTTP" = "200" ]; then
    PROJ=$(echo "$RESP" | python3 -c "import sys,json; d=json.loads(sys.stdin.read().split('HTTP:')[0]); print(d[0].get('name','?') if d else 'NONE')" 2>/dev/null)
    ok "Supabase Management API HTTP 200 — proyecto: $PROJ ($PROJECT_REF)"
  else
    err "Supabase Management API HTTP $HTTP"
  fi

  # Test 2: REST API del proyecto — listar tablas
  SERVICE_ROLE=$(security find-generic-password -s "monstruo-supabase" -a "service_role" -w 2>/dev/null)
  if [ -n "$SERVICE_ROLE" ] && [ -n "$PROJECT_REF" ]; then
    RESP=$(curl -s -w "HTTP:%{http_code}" \
      -H "apikey: $SERVICE_ROLE" \
      -H "Authorization: Bearer $SERVICE_ROLE" \
      "https://${PROJECT_REF}.supabase.co/rest/v1/")
    HTTP=$(echo "$RESP" | grep -oE 'HTTP:[0-9]+' | cut -d: -f2)
    if [ "$HTTP" = "200" ]; then
      ok "Supabase REST API HTTP 200 — endpoint del proyecto accesible"
    else
      err "Supabase REST API HTTP $HTTP"
    fi
  fi
fi
echo ""

# ===== 3. AWS S3 =====
echo "--- 3/4 AWS S3 ---"
AWS_KEY=$(security find-generic-password -s "monstruo-aws" -a "access" -w 2>/dev/null)
AWS_SECRET=$(security find-generic-password -s "monstruo-aws" -a "secret" -w 2>/dev/null)
if [ -z "$AWS_KEY" ]; then
  err "AWS S3: no se pudo recuperar Access Key de Keychain"
else
  export AWS_ACCESS_KEY_ID="$AWS_KEY"
  export AWS_SECRET_ACCESS_KEY="$AWS_SECRET"
  export AWS_REGION="us-east-1"
  BUCKETS=$(aws s3 ls 2>&1 | wc -l | tr -d ' ')
  if [ "$BUCKETS" -gt 0 ] 2>/dev/null; then
    ok "AWS S3 — $BUCKETS buckets visibles"
    # Test 2: leer 1 archivo del bucket operacion-doble-eje
    OBJS=$(aws s3 ls s3://operacion-doble-eje/ 2>&1 | wc -l | tr -d ' ')
    if [ "$OBJS" -gt 0 ] 2>/dev/null; then
      ok "AWS S3 — bucket operacion-doble-eje tiene $OBJS objetos accesibles"
    else
      err "AWS S3 — bucket operacion-doble-eje no accesible"
    fi
    unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
  else
    err "AWS S3 — falló al listar buckets"
  fi
fi
echo ""

# ===== 4. DROPBOX =====
echo "--- 4/4 DROPBOX ---"
DBX_KEY=$(security find-generic-password -s "monstruo-dropbox" -a "key" -w 2>/dev/null)
DBX_SECRET=$(security find-generic-password -s "monstruo-dropbox" -a "secret" -w 2>/dev/null)
DBX_REFRESH=$(security find-generic-password -s "monstruo-dropbox" -a "refresh" -w 2>/dev/null)
if [ -z "$DBX_REFRESH" ]; then
  err "Dropbox: no se pudo recuperar refresh token de Keychain"
else
  # Generar access token desde refresh token
  ACCESS=$(curl -s -X POST "https://api.dropboxapi.com/oauth2/token" \
    -u "${DBX_KEY}:${DBX_SECRET}" \
    -d "grant_type=refresh_token&refresh_token=${DBX_REFRESH}" \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
  if [ -z "$ACCESS" ]; then
    err "Dropbox: no se pudo generar access token"
  else
    # Test 1: get account info
    RESP=$(curl -s -w "HTTP:%{http_code}" -X POST \
      "https://api.dropboxapi.com/2/users/get_current_account" \
      -H "Authorization: Bearer $ACCESS")
    HTTP=$(echo "$RESP" | grep -oE 'HTTP:[0-9]+' | cut -d: -f2)
    if [ "$HTTP" = "200" ]; then
      NAME=$(echo "$RESP" | python3 -c "import sys,json; d=json.loads(sys.stdin.read().split('HTTP:')[0]); print(d.get('name',{}).get('display_name','?'))" 2>/dev/null)
      ok "Dropbox API HTTP 200 — cuenta: $NAME"
    else
      err "Dropbox API HTTP $HTTP"
    fi

    # Test 2: list root folder
    RESP=$(curl -s -w "HTTP:%{http_code}" -X POST \
      "https://api.dropboxapi.com/2/files/list_folder" \
      -H "Authorization: Bearer $ACCESS" \
      -H "Content-Type: application/json" \
      -d '{"path":"","limit":5}')
    HTTP=$(echo "$RESP" | grep -oE 'HTTP:[0-9]+' | cut -d: -f2)
    if [ "$HTTP" = "200" ]; then
      ENTRIES=$(echo "$RESP" | python3 -c "import sys,json; d=json.loads(sys.stdin.read().split('HTTP:')[0]); print(len(d.get('entries',[])))" 2>/dev/null)
      ok "Dropbox list root HTTP 200 — $ENTRIES entradas en raíz"
    else
      err "Dropbox list root HTTP $HTTP"
    fi
  fi
fi
echo ""

# ===== RESUMEN =====
echo "========================================"
echo "  RESUMEN"
echo "========================================"
for r in "${RESULTS[@]}"; do echo "$r"; done
echo "----------------------------------------"
echo "  TOTAL: $PASS passed, $FAIL failed"
echo "========================================"

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
