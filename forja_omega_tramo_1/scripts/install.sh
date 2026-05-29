#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# DTA Sync — Instalador one-liner
#
# Uso:
#   bash forja_omega_tramo_1/scripts/install.sh
#
# Qué hace:
#   1. Instala un git hook post-commit que dispara dta_sync.py
#   2. Registra un cron job cada 15 min como fallback (opcional)
#   3. Verifica que Python 3.9+ está disponible
#
# Autoría: Hilo B (Manus), Sprint DTA-AUTOMATIZACIONES, 2026-05-29.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK_PATH="$REPO_ROOT/.git/hooks/post-commit"
DTA_SCRIPT="$SCRIPT_DIR/dta_sync.py"

echo "═══ DTA Sync — Instalador ═══"
echo ""

# ── Verificar Python ──────────────────────────────────────────────────────────

PYTHON=""
for candidate in python3.11 python3.10 python3.9 python3; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ ERROR: Se requiere Python 3.9+. Instálalo primero."
    exit 1
fi
echo "✅ Python encontrado: $PYTHON ($($PYTHON --version))"

# ── Verificar que dta_sync.py existe ─────────────────────────────────────────

if [ ! -f "$DTA_SCRIPT" ]; then
    echo "❌ ERROR: No se encontró $DTA_SCRIPT"
    exit 1
fi
chmod +x "$DTA_SCRIPT"
echo "✅ Script DTA: $DTA_SCRIPT"

# ── Instalar git hook post-commit ─────────────────────────────────────────────

mkdir -p "$(dirname "$HOOK_PATH")"

# Si ya existe un post-commit, agregar al final (no sobreescribir)
if [ -f "$HOOK_PATH" ]; then
    if grep -q "dta_sync.py" "$HOOK_PATH"; then
        echo "✅ Git hook post-commit ya contiene dta_sync.py — sin cambios"
    else
        echo "" >> "$HOOK_PATH"
        echo "# ── DTA Sync (auto-instalado) ──" >> "$HOOK_PATH"
        echo "$PYTHON \"$DTA_SCRIPT\" 2>&1 | tee -a \"$REPO_ROOT/forja_omega_tramo_1/scripts/.dta_sync.log\" || true" >> "$HOOK_PATH"
        echo "✅ Git hook post-commit actualizado (append)"
    fi
else
    cat > "$HOOK_PATH" << EOF
#!/usr/bin/env bash
# Git post-commit hook — DTA Sync
# Auto-instalado por forja_omega_tramo_1/scripts/install.sh

# Solo ejecutar si hay cambios en forja_omega_tramo_1/bitacora.jsonl
if git diff-tree --no-commit-id --name-only -r HEAD | grep -q "forja_omega_tramo_1/bitacora.jsonl"; then
    $PYTHON "$DTA_SCRIPT" 2>&1 | tee -a "$REPO_ROOT/forja_omega_tramo_1/scripts/.dta_sync.log" || true
fi
EOF
    chmod +x "$HOOK_PATH"
    echo "✅ Git hook post-commit instalado"
fi

# ── Cron job (opcional) ───────────────────────────────────────────────────────

echo ""
read -p "¿Instalar cron job cada 15 min como fallback? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    CRON_CMD="*/15 * * * * cd \"$REPO_ROOT\" && $PYTHON \"$DTA_SCRIPT\" >> \"$SCRIPT_DIR/.dta_sync_cron.log\" 2>&1"
    
    # Verificar si ya existe
    if crontab -l 2>/dev/null | grep -q "dta_sync.py"; then
        echo "✅ Cron job ya existe — sin cambios"
    else
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        echo "✅ Cron job instalado (cada 15 min)"
    fi
else
    echo "⏭️  Cron job omitido"
fi

# ── Resumen ───────────────────────────────────────────────────────────────────

echo ""
echo "═══ Instalación completa ═══"
echo ""
echo "  Pipeline: $DTA_SCRIPT"
echo "  Hook:     $HOOK_PATH"
echo "  Log:      $SCRIPT_DIR/.dta_sync.log"
echo ""
echo "  Para ejecutar manualmente:"
echo "    cd $REPO_ROOT && $PYTHON $DTA_SCRIPT"
echo ""
echo "  Para dry-run:"
echo "    cd $REPO_ROOT && $PYTHON $DTA_SCRIPT --dry-run"
echo ""
echo "  Para forzar sync:"
echo "    cd $REPO_ROOT && $PYTHON $DTA_SCRIPT --force"
echo ""
echo "  Variable de entorno requerida para Guardian:"
echo "    export KERNEL_API_KEY=<tu-api-key>"
echo ""
