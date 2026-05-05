#!/usr/bin/env bash
# load_credentials.sh
# Carga credenciales de AWS y Dropbox desde macOS Keychain a variables de entorno.
# Uso: source discovery_forense/load_credentials.sh
#
# Pre-requisitos: las credenciales deben estar guardadas previamente con:
#   security add-generic-password -U -s "monstruo-aws" -a "access" -w "AKIA..."
#   security add-generic-password -U -s "monstruo-aws" -a "secret" -w "..."
#   security add-generic-password -U -s "monstruo-dropbox" -a "refresh" -w "..."
#   security add-generic-password -U -s "monstruo-dropbox" -a "key" -w "..."
#   security add-generic-password -U -s "monstruo-dropbox" -a "secret" -w "..."
#
# Solo funciona en macOS. En Linux/sandbox las credenciales deben venir en .env separado.

set -e

if [[ "$OSTYPE" != "darwin"* ]]; then
  echo "ERROR: load_credentials.sh solo funciona en macOS (Keychain)." >&2
  echo "       Si estás en sandbox/Linux, pídele a Alfredo el .env temporal." >&2
  return 1 2>/dev/null || exit 1
fi

# AWS S3
export AWS_ACCESS_KEY_ID=$(security find-generic-password -s "monstruo-aws" -a "access" -w 2>/dev/null)
export AWS_SECRET_ACCESS_KEY=$(security find-generic-password -s "monstruo-aws" -a "secret" -w 2>/dev/null)
export AWS_DEFAULT_REGION="us-east-1"

# Dropbox (refresh token + app credentials)
export DROPBOX_REFRESH_TOKEN=$(security find-generic-password -s "monstruo-dropbox" -a "refresh" -w 2>/dev/null)
export DROPBOX_APP_KEY=$(security find-generic-password -s "monstruo-dropbox" -a "key" -w 2>/dev/null)
export DROPBOX_APP_SECRET=$(security find-generic-password -s "monstruo-dropbox" -a "secret" -w 2>/dev/null)

# Verificación
missing=()
[[ -z "$AWS_ACCESS_KEY_ID" ]] && missing+=("AWS_ACCESS_KEY_ID")
[[ -z "$AWS_SECRET_ACCESS_KEY" ]] && missing+=("AWS_SECRET_ACCESS_KEY")
[[ -z "$DROPBOX_REFRESH_TOKEN" ]] && missing+=("DROPBOX_REFRESH_TOKEN")
[[ -z "$DROPBOX_APP_KEY" ]] && missing+=("DROPBOX_APP_KEY")
[[ -z "$DROPBOX_APP_SECRET" ]] && missing+=("DROPBOX_APP_SECRET")

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "WARN: faltan credenciales en Keychain: ${missing[*]}" >&2
  echo "      Pídele a Alfredo que ejecute los comandos add-generic-password de nuevo." >&2
else
  echo "[OK] Credenciales cargadas: AWS (access+secret), Dropbox (refresh+key+secret)"
  echo "[OK] AWS_ACCESS_KEY_ID = ${AWS_ACCESS_KEY_ID:0:8}..."
  echo "[OK] DROPBOX_APP_KEY    = ${DROPBOX_APP_KEY}"
fi

# Helper para refrescar el access token de Dropbox cuando lo necesites
dropbox_get_access_token() {
  curl -s -X POST "https://api.dropboxapi.com/oauth2/token" \
    -u "${DROPBOX_APP_KEY}:${DROPBOX_APP_SECRET}" \
    -d "grant_type=refresh_token&refresh_token=${DROPBOX_REFRESH_TOKEN}" \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])"
}

export -f dropbox_get_access_token 2>/dev/null || true
