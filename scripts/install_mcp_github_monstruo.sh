#!/usr/bin/env bash
# install_mcp_github_monstruo.sh
# Inyecta el server MCP "github-monstruo" en claude_desktop_config.json
# Reusa el PAT activo de gh auth (el-monstruo-mac-2026-05) — un solo PAT, un solo punto de rotación
set -euo pipefail

CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
BACKUP="${CONFIG}.backup-2026-05-04"

if [[ ! -f "$CONFIG" ]]; then
  echo "ERROR: no existe $CONFIG" >&2
  exit 1
fi

TOKEN="$(gh auth token 2>/dev/null || true)"
if [[ -z "$TOKEN" ]]; then
  echo "ERROR: gh auth token vacío. Ejecuta: gh auth status" >&2
  exit 1
fi

# 1. Backup (si no existe)
if [[ ! -f "$BACKUP" ]]; then
  cp "$CONFIG" "$BACKUP"
  echo "Backup creado → $BACKUP"
else
  echo "Backup ya existe → $BACKUP (no se sobrescribe)"
fi

# 2. Inyectar mcpServers.github-monstruo preservando preferences
TMP="$(mktemp)"
jq --arg token "$TOKEN" '
  . + {
    mcpServers: ((.mcpServers // {}) + {
      "github-monstruo": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": $token }
      }
    })
  }
' "$CONFIG" > "$TMP"

# Validar JSON resultante
jq . "$TMP" > /dev/null

mv "$TMP" "$CONFIG"

# 3. chmod 600
chmod 600 "$CONFIG"

# 4. Mostrar resultado redactado
echo "---NUEVO CONFIG (token redactado)---"
jq . "$CONFIG" | sed 's/ghp_[A-Za-z0-9]*/ghp_***REDACTED***/g'

echo "---PERMISOS---"
ls -la "$CONFIG"
