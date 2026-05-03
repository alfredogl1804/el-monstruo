#!/bin/bash
# ============================================================
# EL MONSTRUO — Puente Inter-Hilos: Manus → Claude Code
# ============================================================
# Uso: bash bridge/manus_bridge.sh "tu prompt aquí"
# Uso con archivo: bash bridge/manus_bridge.sh --file bridge/encomienda.md
# ============================================================

set -euo pipefail

BRIDGE_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$BRIDGE_DIR")"
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/.zshrc | cut -d'"' -f2)

# Parse arguments
if [ "${1:-}" = "--file" ]; then
    PROMPT=$(cat "$REPO_DIR/${2}")
else
    PROMPT="${1:-Responde PUENTE_ACTIVO para confirmar conexión}"
fi

# Execute Claude Code headless
cd "$REPO_DIR"
RESULT=$(claude -p "$PROMPT" \
    --bare \
    --allowedTools "Read,Edit,Bash" \
    --output-format json \
    2>/dev/null)

# Extract result and session_id
RESPONSE=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result','ERROR'))")
SESSION_ID=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id','unknown'))")

# Save response
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "---" >> "$BRIDGE_DIR/cowork_to_manus.md"
echo "## Respuesta Claude Code — $TIMESTAMP" >> "$BRIDGE_DIR/cowork_to_manus.md"
echo "Session: $SESSION_ID" >> "$BRIDGE_DIR/cowork_to_manus.md"
echo "" >> "$BRIDGE_DIR/cowork_to_manus.md"
echo "$RESPONSE" >> "$BRIDGE_DIR/cowork_to_manus.md"
echo "" >> "$BRIDGE_DIR/cowork_to_manus.md"

# Output
echo "$RESPONSE"
