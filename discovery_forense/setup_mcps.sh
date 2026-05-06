#!/bin/bash
# setup_mcps.sh — Instalador interactivo de MCP servers para Cowork (Claude Code)
# Generado por: Manus Catastro (Hilo B)
# Fecha: 2026-05-06
#
# Requisitos:
#   - Claude Code CLI instalado (`claude --version`)
#   - Credenciales en macOS Keychain (ver load_credentials.sh)
#   - Notion Internal Integration Token (generar en https://notion.so/profile/integrations)
#
# Este script NO toca claude_desktop_config.json directamente.
# Usa el CLI oficial `claude mcp add` para instalaciones seguras y reversibles.

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  Setup MCPs para Cowork — Discovery Forense Fase III"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Verificar Claude Code
if ! command -v claude &> /dev/null; then
    echo "[ERROR] Claude Code CLI no encontrado en PATH."
    echo "        Instala Claude Code primero: https://claude.com/code"
    exit 1
fi
echo "[OK] Claude Code CLI detectado: $(claude --version 2>&1 | head -1)"
echo ""

# Listar MCPs ya instalados
echo "── MCPs actualmente instalados ──"
claude mcp list 2>&1 || true
echo ""

# Cargar credenciales del Keychain
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [ -f "$SCRIPT_DIR/load_credentials.sh" ]; then
    source "$SCRIPT_DIR/load_credentials.sh"
    echo "[OK] Credenciales del Keychain cargadas"
else
    echo "[WARN] load_credentials.sh no encontrado. AWS y Dropbox quedarán sin instalar."
fi
echo ""

# ════════════════════════════════════════════════════════════════
# 1. NOTION (oficial — para Tarea 1: 69 biblias)
# ════════════════════════════════════════════════════════════════
echo "── 1/4: Notion MCP (oficial makenotion/notion-mcp-server) ──"
if [ -z "$NOTION_TOKEN" ]; then
    echo "[INPUT] Necesitas un Notion Internal Integration Token."
    echo "        Genéralo en: https://notion.so/profile/integrations → New integration"
    echo ""
    read -p "        Pega tu NOTION_TOKEN (o ENTER para skip): " NOTION_TOKEN_INPUT
    NOTION_TOKEN="$NOTION_TOKEN_INPUT"
fi

if [ -n "$NOTION_TOKEN" ]; then
    echo "[INSTALL] Notion MCP..."
    claude mcp add notion \
        --env NOTION_TOKEN="$NOTION_TOKEN" \
        -- npx -y @notionhq/notion-mcp-server || echo "[WARN] Falló — instala manualmente"
    echo "[OK] Notion MCP instalado"
else
    echo "[SKIP] Notion no instalado — sin token"
fi
echo ""

# ════════════════════════════════════════════════════════════════
# 2. SUPABASE (oficial — para Tarea 3: indexar dataset)
# ════════════════════════════════════════════════════════════════
echo "── 2/4: Supabase Connector (oficial Anthropic) ──"
echo "[INFO] Supabase es ahora un connector oficial de Claude."
echo "       Requiere OAuth interactivo en la UI:"
echo "       1. Abre Claude Code"
echo "       2. Settings → Connectors → busca 'Supabase'"
echo "       3. Click 'Connect' y autoriza en navegador"
echo "[ACTION REQUIRED] Hazlo manualmente — no se puede automatizar OAuth."
echo ""

# ════════════════════════════════════════════════════════════════
# 3. AWS S3 (third-party — opcional si Cowork quiere autonomía)
# ════════════════════════════════════════════════════════════════
echo "── 3/4: AWS S3 MCP (third-party samuraikun/aws-s3-mcp) ──"
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    read -p "        ¿Instalar AWS S3 MCP? [y/N]: " INSTALL_S3
    if [[ "$INSTALL_S3" =~ ^[Yy]$ ]]; then
        echo "[INSTALL] AWS S3 MCP..."
        claude mcp add aws-s3 \
            --env AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
            --env AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
            --env AWS_REGION="${AWS_DEFAULT_REGION:-us-east-1}" \
            -- npx -y @samuraikun/aws-s3-mcp || echo "[WARN] Falló — verifica el paquete npm"
        echo "[OK] AWS S3 MCP instalado"
    else
        echo "[SKIP] AWS S3 — Manus seguirá manejando S3"
    fi
else
    echo "[SKIP] Sin credenciales AWS — Manus maneja S3"
fi
echo ""

# ════════════════════════════════════════════════════════════════
# 4. DROPBOX DASH (oficial — opcional)
# ════════════════════════════════════════════════════════════════
echo "── 4/4: Dropbox Dash MCP (oficial dropbox/mcp-server-dash) ──"
echo "[INFO] Dropbox Dash MCP requiere OAuth interactivo:"
echo "       1. Settings → Connectors → Add custom connector"
echo "       2. Name: Dropbox Dash MCP"
echo "       3. URL: ver https://help.dropbox.com/integrations/set-up-MCP-server"
echo "       4. Autoriza con tu cuenta Dropbox"
echo "[ACTION REQUIRED] Hazlo manualmente si necesitas autonomía con Dropbox."
echo "[ALTERNATIVA] Mantener Manus para Dropbox (división híbrida)."
echo ""

# ════════════════════════════════════════════════════════════════
# RESUMEN
# ════════════════════════════════════════════════════════════════
echo "════════════════════════════════════════════════════════════════"
echo "  Setup completado. Verifica con: claude mcp list"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Próximos pasos:"
echo "  1. Reinicia Claude Code para cargar los MCPs nuevos"
echo "  2. Verifica con: claude mcp list"
echo "  3. Si instalaste Supabase y/o Dropbox, hazlo desde la UI (OAuth)"
echo "  4. Continúa con Fase III de Canonización"
echo ""
