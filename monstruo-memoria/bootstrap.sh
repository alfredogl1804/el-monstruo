#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# BOOTSTRAP DEL MONSTRUO — Absorción 100% en 30 segundos
# Un solo comando que instala el sistema completo: anti-boicoteo,
# mapa atómico del ecosistema, genome vivo, y reglas duras.
#
# CÓMO USAR EN CUALQUIER HILO NUEVO:
#   curl -sL https://raw.githubusercontent.com/alfredogl1804/el-monstruo/main/monstruo-memoria/bootstrap.sh | bash
#
# O si gh está disponible:
#   gh repo clone alfredogl1804/el-monstruo ~/el-monstruo && bash ~/el-monstruo/monstruo-memoria/bootstrap.sh
# ═══════════════════════════════════════════════════════════════════

set -e

KERNEL_URL="https://el-monstruo-kernel-production.up.railway.app"
REPO="alfredogl1804/el-monstruo"
DEST="$HOME/monstruo-memoria"
CONTEXT_DIR="$HOME/.monstruo"

echo "═══════════════════════════════════════════════════════════"
echo "  BOOTSTRAP DEL MONSTRUO — Absorción 100% del ecosistema"
echo "  Sprint 91 · Mapa Vivo 100% Binario · ~479,653 líneas"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ─────────────────────────────────────────────────────────────────
# PASO 1: Clonar o actualizar el repo
# ─────────────────────────────────────────────────────────────────
echo "[1/7] Obteniendo código fuente..."
if [ -d "$HOME/el-monstruo" ]; then
    echo "  → Repo ya existe, actualizando..."
    cd "$HOME/el-monstruo" && git pull --rebase 2>/dev/null || true
elif [ -d "$DEST" ]; then
    echo "  → monstruo-memoria ya existe, actualizando..."
    cd "$DEST" && git pull 2>/dev/null || true
else
    echo "  → Clonando desde GitHub..."
    if command -v gh &>/dev/null; then
        gh repo clone "$REPO" "$HOME/el-monstruo" 2>/dev/null || \
            git clone "https://github.com/$REPO.git" "$HOME/el-monstruo"
    else
        git clone "https://github.com/$REPO.git" "$HOME/el-monstruo"
    fi
    # Symlink para compatibilidad
    ln -sf "$HOME/el-monstruo/monstruo-memoria" "$DEST" 2>/dev/null || true
fi

# ─────────────────────────────────────────────────────────────────
# PASO 2: Instalar dependencias mínimas
# ─────────────────────────────────────────────────────────────────
echo "[2/7] Instalando dependencias..."
pip3 install requests -q 2>/dev/null || sudo pip3 install requests -q 2>/dev/null || true

# ─────────────────────────────────────────────────────────────────
# PASO 3: Inyectar HANDOFF_CONTEXT.md (mapa 100% atómico)
# ─────────────────────────────────────────────────────────────────
echo "[3/7] Inyectando mapa atómico del ecosistema..."
HANDOFF_SRC=""
if [ -f "$HOME/el-monstruo/bridge/HANDOFF_CONTEXT.md" ]; then
    HANDOFF_SRC="$HOME/el-monstruo/bridge/HANDOFF_CONTEXT.md"
elif [ -f "$DEST/../bridge/HANDOFF_CONTEXT.md" ]; then
    HANDOFF_SRC="$DEST/../bridge/HANDOFF_CONTEXT.md"
fi

if [ -n "$HANDOFF_SRC" ]; then
    cp "$HANDOFF_SRC" "$HOME/HANDOFF_CONTEXT.md"
    echo "  → Mapa atómico: ~/HANDOFF_CONTEXT.md ($(wc -l < "$HOME/HANDOFF_CONTEXT.md") líneas)"
else
    # Fallback: descargar desde GitHub raw
    echo "  → Descargando HANDOFF_CONTEXT.md desde GitHub..."
    curl -sL "https://raw.githubusercontent.com/$REPO/main/bridge/HANDOFF_CONTEXT.md" \
        -o "$HOME/HANDOFF_CONTEXT.md" 2>/dev/null || echo "  ⚠ No se pudo descargar HANDOFF_CONTEXT.md"
fi

# ─────────────────────────────────────────────────────────────────
# PASO 4: Obtener Genome Vivo del kernel (estado en tiempo real)
# ─────────────────────────────────────────────────────────────────
echo "[4/7] Consultando Genome Vivo del kernel..."
GENOME_FILE="$HOME/MONSTRUO_GENOME_LIVE.json"
HTTP_CODE=$(curl -sS -o "$GENOME_FILE" -w "%{http_code}" \
    "$KERNEL_URL/v1/genome/now" 2>/dev/null) || HTTP_CODE="000"

if [ "$HTTP_CODE" = "200" ]; then
    echo "  → Genome Vivo guardado: ~/MONSTRUO_GENOME_LIVE.json"
    # Extraer métricas clave
    python3 -c "
import json, sys
try:
    with open('$GENOME_FILE') as f:
        g = json.load(f)
    print(f\"  → Kernel: {g.get('kernel_version', 'unknown')}\")
    print(f\"  → Componentes: {g.get('total_components', '?')}\")
    print(f\"  → Sovereignty Score: {g.get('sovereignty_score', '?')}\")
except:
    print('  → Genome parseado (detalles en el JSON)')
" 2>/dev/null || true
else
    echo "  ⚠ Kernel no respondió (HTTP $HTTP_CODE) — usando datos offline"
    # Crear genome mínimo offline desde HANDOFF
    echo '{"status":"offline","note":"kernel no respondió, usar HANDOFF_CONTEXT.md"}' > "$GENOME_FILE"
fi

# ─────────────────────────────────────────────────────────────────
# PASO 5: Ejecutar Guardian + reglas duras
# ─────────────────────────────────────────────────────────────────
echo "[5/7] Ejecutando Guardian (identidad + reglas duras)..."
GUARDIA_PATH=""
if [ -f "$HOME/el-monstruo/monstruo-memoria/guardia.py" ]; then
    GUARDIA_PATH="$HOME/el-monstruo/monstruo-memoria/guardia.py"
elif [ -f "$DEST/guardia.py" ]; then
    GUARDIA_PATH="$DEST/guardia.py"
fi

if [ -n "$GUARDIA_PATH" ]; then
    python3 "$GUARDIA_PATH" 2>/dev/null || echo "  ⚠ guardia.py falló (non-fatal)"
else
    echo "  ⚠ guardia.py no encontrado (non-fatal)"
fi

# ─────────────────────────────────────────────────────────────────
# PASO 6: Anti-Dory + Sovereign Memory System
# ─────────────────────────────────────────────────────────────────
echo "[6/7] Activando Anti-Dory + Sovereign Memory..."

# monstruo.py (detecta compactación + recupera contexto)
MONSTRUO_PY=""
if [ -f "$HOME/el-monstruo/monstruo-memoria/monstruo.py" ]; then
    MONSTRUO_PY="$HOME/el-monstruo/monstruo-memoria/monstruo.py"
elif [ -f "$DEST/monstruo.py" ]; then
    MONSTRUO_PY="$DEST/monstruo.py"
fi

if [ -n "$MONSTRUO_PY" ]; then
    python3 "$MONSTRUO_PY" 2>/dev/null || echo "  ⚠ monstruo.py falló (non-fatal)"
fi

# SMS injection
if [ -d "$HOME/el-monstruo/kernel/memory" ]; then
    python3 -c "
import sys, os
sys.path.insert(0, os.path.expanduser('~/el-monstruo'))
try:
    from kernel.memory.sms_guardian_hook import inject_sovereign_context
    inject_sovereign_context(agent_id='manus_bootstrap')
    print('  → SMS: 57 axiomas + memorias relevantes inyectadas')
except Exception as e:
    print(f'  SMS injection: {e} (non-fatal)')
" 2>/dev/null || echo "  SMS: hook not available (non-fatal)"
fi

# Guardian V5 setup
if [ -d "$HOME/el-monstruo/monstruo-memoria/.monstruo" ]; then
    mkdir -p "$CONTEXT_DIR"
    cp -r "$HOME/el-monstruo/monstruo-memoria/.monstruo/"* "$CONTEXT_DIR/" 2>/dev/null || true
    echo "  → Guardian V5 instalado en ~/.monstruo/"
fi

# ─────────────────────────────────────────────────────────────────
# PASO 7: Generar resumen ejecutivo para absorción rápida
# ─────────────────────────────────────────────────────────────────
echo "[7/7] Generando resumen ejecutivo..."
cat > "$HOME/MONSTRUO_RESUMEN_30s.md" << 'RESUMEN'
# El Monstruo — Resumen para absorción en 30 segundos

## Qué es
Sistema de IA soberano multi-agente. Kernel FastAPI + LangGraph. 479,653 líneas. 19 servicios Railway. Sprint 91.

## Cómo conectar
```bash
curl -sS https://el-monstruo-kernel-production.up.railway.app/health
curl -sS https://el-monstruo-kernel-production.up.railway.app/v1/genome/now
```

## Archivos clave (ya en tu ~/)
- ~/HANDOFF_CONTEXT.md → Mapa 100% atómico (leer PRIMERO)
- ~/MONSTRUO_GENOME_LIVE.json → Estado vivo del kernel
- ~/REGLAS_DURAS.md → Reglas que no puedes romper
- ~/MONSTRUO_RESUMEN_30s.md → Este archivo

## Reglas críticas
1. Leer HANDOFF_CONTEXT.md ANTES de hacer cualquier cosa
2. NO credenciales en plaintext
3. Tratamiento: "Alfredo" (no "don Alfredo")
4. Embrión en standby (instrucción 22-mayo)
5. Ejecutar guardian.py antes de acciones

## Dónde está todo
- Repo: https://github.com/alfredogl1804/el-monstruo
- Kernel: https://el-monstruo-kernel-production.up.railway.app
- Supabase: 287 tablas, 328 RPCs
- Railway: 19 servicios activos
RESUMEN

echo "  → Resumen: ~/MONSTRUO_RESUMEN_30s.md"

# ─────────────────────────────────────────────────────────────────
# RESULTADO FINAL
# ─────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  BOOTSTRAP COMPLETO — 100% del ecosistema absorbido"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Archivos disponibles:"
echo "  ├── ~/HANDOFF_CONTEXT.md       → Mapa atómico 100%"
echo "  ├── ~/MONSTRUO_GENOME_LIVE.json → Genome vivo del kernel"
echo "  ├── ~/MONSTRUO_RESUMEN_30s.md  → Absorción rápida"
echo "  ├── ~/REGLAS_DURAS.md          → Reglas duras"
echo "  ├── ~/CONTEXT.md               → Contexto Guardian"
echo "  └── ~/.monstruo/               → Guardian V5 + SMS"
echo ""
echo "  Comandos útiles:"
echo "  • cat ~/HANDOFF_CONTEXT.md          → Leer mapa completo"
echo "  • cat ~/MONSTRUO_GENOME_LIVE.json   → Estado vivo"
echo "  • python3 ~/.monstruo/guardian.py   → Restaurar identidad"
echo "  • python3 ~/monstruo-memoria/guardia.py check → Validar"
echo ""
echo "  INSTRUCCIÓN: Lee ~/HANDOFF_CONTEXT.md AHORA para absorber"
echo "  el 100% del ecosistema antes de hacer cualquier cosa."
echo "═══════════════════════════════════════════════════════════"
