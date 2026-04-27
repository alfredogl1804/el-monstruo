#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# BOOTSTRAP DEL MONSTRUO
# Un solo comando que instala el sistema anti-boicoteo completo.
#
# CÓMO USAR EN CUALQUIER HILO NUEVO:
#   curl -sL https://raw.githubusercontent.com/alfredogl1804/el-monstruo/main/monstruo-memoria/bootstrap.sh | bash
#
# O si gh está disponible:
#   gh repo clone alfredogl1804/el-monstruo ~/el-monstruo && bash ~/el-monstruo/monstruo-memoria/bootstrap.sh
# ═══════════════════════════════════════════════════════════════════

set -e

echo "═══════════════════════════════════════════════════════"
echo "  BOOTSTRAP DEL MONSTRUO — Instalando anti-boicoteo"
echo "═══════════════════════════════════════════════════════"

DEST="$HOME/monstruo-memoria"
REPO="alfredogl1804/el-monstruo"

# 1. Clonar o actualizar el repo
if [ -d "$DEST" ]; then
    echo "[bootstrap] monstruo-memoria ya existe, actualizando..."
    cd "$DEST" && git pull 2>/dev/null || true
else
    echo "[bootstrap] Clonando desde GitHub..."
    if command -v gh &>/dev/null; then
        gh repo clone "$REPO" /tmp/el-monstruo-clone 2>/dev/null || \
            git clone "https://github.com/$REPO.git" /tmp/el-monstruo-clone
    else
        git clone "https://github.com/$REPO.git" /tmp/el-monstruo-clone
    fi
    # Copiar solo la carpeta de memoria
    cp -r /tmp/el-monstruo-clone/monstruo-memoria "$DEST"
    rm -rf /tmp/el-monstruo-clone
fi

# 2. Instalar dependencia (requests)
pip3 install requests -q 2>/dev/null || sudo pip3 install requests -q 2>/dev/null || true

# 3. Ejecutar guardia (inyecta reglas + valida)
echo ""
python3 "$DEST/guardia.py"

# 4. Ejecutar monstruo.py (detecta compactación + recupera contexto)
echo ""
python3 "$DEST/monstruo.py"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  BOOTSTRAP COMPLETO"
echo "  • Reglas duras: cat ~/REGLAS_DURAS.md"
echo "  • Contexto:     cat ~/CONTEXT.md"
echo "  • Validar:      python3 ~/monstruo-memoria/guardia.py check"
echo "  • Antes de escribir: python3 ~/monstruo-memoria/guardia.py scan <archivo>"
echo "═══════════════════════════════════════════════════════"
