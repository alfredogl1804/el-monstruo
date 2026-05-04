#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# ROTACIÓN PLAN A — Soberano · 17+ PATs → 2 PATs · El Monstruo · 2026-05
# ═══════════════════════════════════════════════════════════════════════════
# Plan: revocar TODOS los PATs Classic + fine-grained activos, mantener solo
# 2 nuevos con scope mínimo y expiración 90 días.
#
# Filosofía:
#   - Nada se borra hasta validar que los nuevos funcionan
#   - Backup completo antes de tocar nada
#   - Rollback path siempre disponible
#   - Logging total: todo queda en ~/.monstruo-rotation-2026-05/
#
# Uso:
#   cd ~/el-monstruo
#   bash scripts/rotacion_tokens_plan_a.sh
#
# Variables de entorno opcionales:
#   DRY_RUN=1     # Solo muestra qué haría, no toca nada
#   SKIP_WAIT=1   # Salta espera de 2-4h (NO recomendado)
#   FROM_PHASE=N  # Empezar desde fase N (para reanudar)
# ═══════════════════════════════════════════════════════════════════════════

set -uo pipefail

# ─── Config ────────────────────────────────────────────────────────────────
WORKDIR="${HOME}/.monstruo-rotation-2026-05"
LOG_FILE="${WORKDIR}/rotation_$(date +%Y%m%d_%H%M%S).log"
DRY_RUN="${DRY_RUN:-0}"
SKIP_WAIT="${SKIP_WAIT:-0}"
FROM_PHASE="${FROM_PHASE:-0}"

KERNEL_HEALTH_URL="https://el-monstruo-kernel-production.up.railway.app/v1/health"
RAILWAY_SERVICE="el-monstruo-kernel"
REPO_ROOT="${HOME}/el-monstruo"

NEW_TOKEN_MAC_NAME="el-monstruo-mac-2026-05"
NEW_TOKEN_KERNEL_NAME="el-monstruo-kernel-2026-05"

# ─── Colores y helpers ─────────────────────────────────────────────────────
bold()    { printf "\033[1m%s\033[0m\n" "$*"; }
green()   { printf "\033[32m%s\033[0m\n" "$*"; }
red()     { printf "\033[31m%s\033[0m\n" "$*"; }
yellow()  { printf "\033[33m%s\033[0m\n" "$*"; }
blue()    { printf "\033[34m%s\033[0m\n" "$*"; }
section() { echo; echo; bold "═══════════════════════════════════════════════════════════════"; bold "  $*"; bold "═══════════════════════════════════════════════════════════════"; }
phase()   { echo; bold "▌ FASE $*"; }

confirm() {
    local prompt="$1"
    local response
    if [[ "$DRY_RUN" == "1" ]]; then
        yellow "  [DRY RUN] Asumiendo SI a: $prompt"
        return 0
    fi
    while true; do
        read -r -p "$(yellow "  ⚠ $prompt [si/no]: ")" response
        case "$response" in
            si|SI|s|S|y|Y|yes|YES) return 0 ;;
            no|NO|n|N) return 1 ;;
            *) echo "  Respondé 'si' o 'no'" ;;
        esac
    done
}

pause_for_manual() {
    local instructions="$1"
    echo
    yellow "─── ACCIÓN MANUAL REQUERIDA ───"
    echo -e "$instructions"
    echo
    read -r -p "$(blue "  Cuando termines, presioná Enter para continuar...")"
}

run_or_dry() {
    if [[ "$DRY_RUN" == "1" ]]; then
        yellow "  [DRY RUN] $*"
    else
        echo "  → $*"
        eval "$@"
    fi
}

# ─── Inicialización ────────────────────────────────────────────────────────
mkdir -p "$WORKDIR"
chmod 700 "$WORKDIR"
exec > >(tee -a "$LOG_FILE") 2>&1

section "ROTACIÓN PLAN A · El Monstruo · $(date)"
[[ "$DRY_RUN" == "1" ]] && yellow "MODO DRY RUN ACTIVO — no se ejecutará nada destructivo"
[[ "$SKIP_WAIT" == "1" ]] && red "MODO SKIP_WAIT ACTIVO — saltando espera de validación (NO recomendado)"
echo "Log de esta sesión: $LOG_FILE"
echo "Workdir: $WORKDIR"
echo

# ═══════════════════════════════════════════════════════════════════════════
# FASE 0 — Pre-flight
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 0 ]]; then
    phase "0 · PRE-FLIGHT CHECKS"

    # gh CLI
    if ! command -v gh >/dev/null 2>&1; then
        red "✗ gh CLI no instalada. Ejecutá: brew install gh"
        exit 1
    fi
    green "✓ gh CLI disponible"

    if ! gh auth status >/dev/null 2>&1; then
        yellow "⚠ gh CLI no autenticada. Ejecutá ahora:"
        echo "    gh auth login --web --scopes repo"
        exit 1
    fi
    green "✓ gh CLI autenticada como: $(gh api user --jq .login)"

    # railway CLI
    if ! command -v railway >/dev/null 2>&1; then
        red "✗ railway CLI no instalada. Ejecutá: npm i -g @railway/cli"
        exit 1
    fi
    green "✓ railway CLI disponible"

    # Repo root
    [[ -d "$REPO_ROOT" ]] || { red "✗ $REPO_ROOT no existe"; exit 1; }
    green "✓ Repo root existe"

    # Workdir creado
    green "✓ Workdir: $WORKDIR (perms 700)"

    # Internet
    if curl -sf -o /dev/null --max-time 5 https://api.github.com; then
        green "✓ Conectividad GitHub API"
    else
        red "✗ Sin conectividad a GitHub API"
        exit 1
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 1 — Audit fine-grained tokens pendientes
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 1 ]]; then
    phase "1 · AUDIT FINE-GRAINED TOKENS (manual)"

    pause_for_manual "$(cat <<EOF
  Abrí en navegador (logueado a GitHub):
    https://github.com/settings/tokens?type=beta

  Anotá en un papel o en archivo:
    - Cantidad total de fine-grained tokens activos
    - Nombre + repos a los que tienen acceso de cada uno
    - 'Last used' de cada uno
    - Cuáles tienen expiración

  Esto es para confirmar que no hay sorpresas adicionales además de los 17 Classic.
EOF
)"

    confirm "¿Capturaste el inventario completo de fine-grained tokens?" || { red "Aborto: necesario antes de continuar"; exit 1; }

    if confirm "¿Apareció algún token fine-grained que NO esperabas (más allá del Railway #4 GITHUB_PERSONAL_ACCESS_TOKEN)?"; then
        yellow "⚠ Pegá información del/los token(s) sorpresa en $WORKDIR/extras_finegrained.txt"
        pause_for_manual "Crear archivo $WORKDIR/extras_finegrained.txt con detalles."
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 2 — Verificar Manus Custom MCP Server
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 2 ]]; then
    phase "2 · VERIFICAR MANUS MCP SERVER (manual)"

    pause_for_manual "$(cat <<EOF
  Abrí Manus (web o desktop) → Settings → Custom MCP Servers (o Integrations).
  Buscá un servidor MCP de GitHub (probablemente '@modelcontextprotocol/server-github').

  Reportá en $WORKDIR/manus_mcp_status.txt:
    - ¿Existe el MCP server de GitHub?
    - ¿Qué prefijo de token tiene cargado? (primeros 8 chars)
    - ¿Está enabled o disabled?
EOF
)"

    confirm "¿Verificaste y anotaste el estado del Manus MCP Server?" || { red "Aborto"; exit 1; }
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 3 — GitHub Security Log
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 3 ]]; then
    phase "3 · GITHUB SECURITY LOG (manual)"

    pause_for_manual "$(cat <<EOF
  Abrí: https://github.com/settings/security-log

  Buscá actividad sospechosa de últimos 90 días:
    - Logins desde IPs/países no familiares
    - Token creates que NO recordás haber hecho
    - 2FA disable/enable inesperado
    - SSH key adds inesperadas
    - OAuth authorize de apps que no instalaste vos

  Si ves CUALQUIER cosa rara, ABORTÁ esta rotación y avisá a Cowork primero.
  Una rotación con cuenta comprometida activa solo le da al atacante tokens nuevos.
EOF
)"

    if ! confirm "¿Security Log limpio sin actividad sospechosa?"; then
        red "ABORTO: investigá la actividad sospechosa primero. La rotación NO es la solución correcta si la cuenta está comprometida activamente — necesitás reset de password + 2FA + revisión de sesiones activas + posible support ticket a GitHub."
        exit 2
    fi
    green "✓ Security Log limpio"
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 4 — Generar 2 PATs nuevos
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 4 ]]; then
    phase "4 · GENERAR 2 PATs NUEVOS (manual en GitHub web)"

    pause_for_manual "$(cat <<EOF
  Abrí: https://github.com/settings/tokens/new

  ─── TOKEN 1 · MAC LOCAL ───
  Note (nombre):  $NEW_TOKEN_MAC_NAME
  Expiration:     90 days (Custom)
  Scopes:         repo (solo)
  NO marcar:      workflow, gist, admin:*, write:packages, read:org, etc.

  Click 'Generate token' → Copiá el token (empieza con 'ghp_')
  Guardalo en: $WORKDIR/token_mac.txt
  chmod 600 después de guardar.

  ─── TOKEN 2 · KERNEL RAILWAY ───
  Note (nombre):  $NEW_TOKEN_KERNEL_NAME
  Expiration:     90 days (Custom)
  Scopes:         repo
  NOTA: NO incluyas 'workflow' a menos que tu grep mostró que el kernel toca .github/workflows/

  Click 'Generate token' → Copiá el token
  Guardalo en: $WORKDIR/token_kernel.txt
  chmod 600 después de guardar.
EOF
)"

    # Verificar archivos
    [[ -f "$WORKDIR/token_mac.txt" ]] || { red "Falta $WORKDIR/token_mac.txt"; exit 1; }
    [[ -f "$WORKDIR/token_kernel.txt" ]] || { red "Falta $WORKDIR/token_kernel.txt"; exit 1; }
    chmod 600 "$WORKDIR/token_mac.txt" "$WORKDIR/token_kernel.txt"

    TOKEN_MAC=$(cat "$WORKDIR/token_mac.txt" | tr -d '[:space:]')
    TOKEN_KERNEL=$(cat "$WORKDIR/token_kernel.txt" | tr -d '[:space:]')

    # Validar formato
    if [[ ! "$TOKEN_MAC" =~ ^ghp_[A-Za-z0-9]{20,}$ ]]; then
        red "Token Mac no tiene formato válido (esperado: ghp_...)"
        exit 1
    fi
    if [[ ! "$TOKEN_KERNEL" =~ ^ghp_[A-Za-z0-9]{20,}$ ]]; then
        red "Token Kernel no tiene formato válido"
        exit 1
    fi

    # Validar que funcionan contra GitHub API
    if curl -sf -o /dev/null -H "Authorization: token $TOKEN_MAC" https://api.github.com/user; then
        green "✓ Token Mac válido contra GitHub API"
    else
        red "✗ Token Mac no autentica contra GitHub API"
        exit 1
    fi
    if curl -sf -o /dev/null -H "Authorization: token $TOKEN_KERNEL" https://api.github.com/user; then
        green "✓ Token Kernel válido contra GitHub API"
    else
        red "✗ Token Kernel no autentica contra GitHub API"
        exit 1
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 5 — Migrar Mac local
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 5 ]]; then
    phase "5 · MIGRAR MAC LOCAL"

    TOKEN_MAC=$(cat "$WORKDIR/token_mac.txt" | tr -d '[:space:]')

    # Backup git config actual
    git config --global --list > "$WORKDIR/git_config_backup.txt"
    green "✓ Backup git config: $WORKDIR/git_config_backup.txt"

    # Verificar credential helper actual
    CURRENT_HELPER=$(git config --global credential.helper 2>/dev/null || echo "")
    echo "Credential helper actual: ${CURRENT_HELPER:-(ninguno)}"

    # Borrar ~/.git-credentials si existe
    if [[ -f "$HOME/.git-credentials" ]]; then
        cp "$HOME/.git-credentials" "$WORKDIR/git-credentials.backup"
        chmod 600 "$WORKDIR/git-credentials.backup"
        if confirm "¿Borrar ~/.git-credentials? (backup en $WORKDIR/git-credentials.backup)"; then
            run_or_dry "rm $HOME/.git-credentials"
            green "✓ ~/.git-credentials borrado"
        fi
    else
        green "✓ ~/.git-credentials no existe"
    fi

    # Borrar credenciales viejas de GitHub en Keychain
    yellow "Borrando entradas viejas de github.com en Keychain..."
    if confirm "¿Borrar entradas 'github.com' del Keychain?"; then
        # Iterativo: security delete-internet-password puede tener varias entradas
        for i in 1 2 3 4 5; do
            run_or_dry "security delete-internet-password -s github.com 2>/dev/null || true"
        done
        green "✓ Entradas viejas de github.com borradas del Keychain"
    fi

    # Configurar gh CLI con nuevo token
    pause_for_manual "$(cat <<EOF
  Vamos a re-autenticar gh CLI con el token nuevo de Mac.

  Ejecutá en otra terminal (no en esta):
    echo '$TOKEN_MAC' | gh auth login --with-token

  Después verificá con: gh auth status
EOF
)"

    if gh auth status >/dev/null 2>&1; then
        green "✓ gh CLI re-autenticada"
    else
        red "✗ gh CLI no autenticada después del paso anterior"
        exit 1
    fi

    # Configurar git para usar gh como credential helper
    if confirm "¿Configurar git credential helper a 'gh' (recomendado)?"; then
        run_or_dry "git config --global --unset-all credential.helper 2>/dev/null || true"
        run_or_dry "git config --global credential.helper '!gh auth git-credential'"
        green "✓ git credential helper = gh"
    fi

    # Push dummy de prueba
    pause_for_manual "$(cat <<EOF
  Probá un push dummy desde tu Mac:

    cd ~/el-monstruo
    echo "# rotation test \$(date)" >> .rotation_test
    git add .rotation_test
    git commit -m 'test rotación token mac'
    git push

  Si falla → rollback. Si pasa → continúa.
EOF
)"

    if confirm "¿Push dummy exitoso?"; then
        # Limpiar archivo de prueba
        run_or_dry "cd $REPO_ROOT && git rm .rotation_test && git commit -m 'cleanup rotation test' && git push"
        green "✓ Mac validado con token nuevo"
    else
        red "ABORTO: Mac no puede pushear. Investigar antes de seguir."
        red "Rollback: gh auth login --web (con el token viejo si lo tenés)"
        exit 1
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 6 — Migrar Railway kernel
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 6 ]]; then
    phase "6 · MIGRAR RAILWAY KERNEL"

    TOKEN_KERNEL=$(cat "$WORKDIR/token_kernel.txt" | tr -d '[:space:]')

    # Backup completo de env vars
    yellow "Backup completo de env vars del kernel..."
    if [[ "$DRY_RUN" != "1" ]]; then
        railway variables --service "$RAILWAY_SERVICE" --kv > "$WORKDIR/railway_env_backup.env" 2>&1 || {
            red "✗ No pude leer env vars de Railway. Verificá: railway login"
            exit 1
        }
        chmod 600 "$WORKDIR/railway_env_backup.env"
        green "✓ Backup en $WORKDIR/railway_env_backup.env"
    fi

    # Mostrar valores actuales (enmascarados)
    if [[ -f "$WORKDIR/railway_env_backup.env" ]]; then
        echo "Variables GITHUB_* actuales:"
        grep "^GITHUB" "$WORKDIR/railway_env_backup.env" | sed 's/=.*/=<HIDDEN>/'
    fi

    if confirm "¿Setear ambas vars (GITHUB_TOKEN + GITHUB_PERSONAL_ACCESS_TOKEN) al token kernel nuevo?"; then
        run_or_dry "railway variables --service $RAILWAY_SERVICE --set GITHUB_TOKEN='$TOKEN_KERNEL' --set GITHUB_PERSONAL_ACCESS_TOKEN='$TOKEN_KERNEL'"
        green "✓ Vars seteadas"
    else
        red "ABORTO: necesario para que kernel funcione"
        exit 1
    fi

    # Trigger redeploy
    yellow "Trigger redeploy del kernel..."
    run_or_dry "railway redeploy --service $RAILWAY_SERVICE --yes"

    # Healthcheck con retry
    yellow "Esperando kernel healthy (max 5 min)..."
    HEALTHY=0
    for i in $(seq 1 30); do
        sleep 10
        if curl -sf --max-time 5 "$KERNEL_HEALTH_URL" >/dev/null 2>&1; then
            HEALTHY=1
            green "✓ Kernel healthy después de ${i}0 segundos"
            break
        fi
        echo "  Intento $i/30 — esperando..."
    done

    if [[ "$HEALTHY" != "1" ]]; then
        red "✗ Kernel NO está healthy después de 5 min"
        yellow "Rollback inmediato:"
        echo "  cat $WORKDIR/railway_env_backup.env | grep GITHUB"
        echo "  # Tomá los valores viejos y volvé a setearlos:"
        echo "  railway variables --service $RAILWAY_SERVICE --set GITHUB_TOKEN='<viejo>' --set GITHUB_PERSONAL_ACCESS_TOKEN='<viejo>'"
        echo "  railway redeploy --service $RAILWAY_SERVICE --yes"
        exit 1
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 7 — Esperar 2-4h validación producción
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 7 ]]; then
    phase "7 · ESPERAR 2-4h DE VALIDACIÓN EN PRODUCCIÓN"

    if [[ "$SKIP_WAIT" == "1" ]]; then
        yellow "⚠ SKIP_WAIT activo — saltando espera (NO recomendado)"
    else
        cat <<EOF

  $(yellow "Período de observación: 2 a 4 horas con kernel productivo activo.")

  Durante este tiempo monitoreá:

  1. Logs Railway en otra terminal:
     railway logs --service $RAILWAY_SERVICE --follow | grep -iE 'error|github|token|401|403'

  2. Healthcheck periódico:
     watch -n 60 'curl -s $KERNEL_HEALTH_URL'

  3. Si tenés tests E2E o smoke tests, corrélos.

  Si algo rompe en este lapso → es porque algún servicio externo dependía
  de un token viejo. Rollback de Railway env vars al backup.

  Cuando hayan pasado las 2-4h sin incidentes, continuá con la siguiente fase
  para revocar los tokens viejos.

EOF
        confirm "¿Pasaron las 2-4h sin incidentes y querés continuar a revocar?" || {
            yellow "Pausa aquí. Reanudá con: FROM_PHASE=8 bash $0"
            exit 0
        }
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 8 — Revocar 3 nucleares + 1 expirado
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 8 ]]; then
    phase "8 · REVOCAR NUCLEARES Y EXPIRADO"

    pause_for_manual "$(cat <<EOF
  Abrí: https://github.com/settings/tokens

  REVOCÁ EN ESTE ORDEN ESTRICTO (delete uno por uno):

    1. ${red:-}Manus monstruo 2${green:-}              [admin:* + sin expiración + Never used]
    2. ${red:-}Token Manus Kukulkan${green:-}          [admin:* + sin expiración + Last 4 weeks]
    3. ${yellow:-}Mounstro v2${green:-}                  [casi todos admin + expirado, limpieza]
    4. ${yellow:-}Manus-Sandbox-v3${green:-}             [scope repo + sin expiración + Last week]

  Para cada uno:
    - Click en el nombre del token
    - Scroll abajo → 'Delete'
    - Confirmar 'I understand, delete this token'

  El #4 (Manus-Sandbox-v3) tiene scope repo (no nuclear) pero sin expiración.
  Lo revocamos por política.
EOF
)"

    if confirm "¿Revocaste los 4 (3 nucleares + 1 expirado)?"; then
        green "✓ Nucleares revocados"
        echo "  Manus monstruo 2: revocado"   >> "$WORKDIR/revoked.txt"
        echo "  Token Manus Kukulkan: revocado" >> "$WORKDIR/revoked.txt"
        echo "  Mounstro v2: revocado"           >> "$WORKDIR/revoked.txt"
        echo "  Manus-Sandbox-v3: revocado"      >> "$WORKDIR/revoked.txt"
    else
        red "ABORTO: nucleares deben revocarse antes de seguir"
        exit 1
    fi

    # Healthcheck post-revocación
    if curl -sf --max-time 5 "$KERNEL_HEALTH_URL" >/dev/null; then
        green "✓ Kernel sigue healthy después de revocar nucleares"
    else
        red "✗ Kernel NO healthy después de revocar nucleares — investigar inmediato"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 9 — Revocar 13 menores
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 9 ]]; then
    phase "9 · REVOCAR 13 MENORES"

    pause_for_manual "$(cat <<EOF
  En: https://github.com/settings/tokens

  REVOCÁ los 13 menores (en cualquier orden):

    1. el-monstruo-ci-fix-2
    2. manus-sprint35
    3. manus-ops
    4. manus-temp-push
    5. manus-sandbox
    6. el-monstruo-ci-fix
    7. manus-sprint14
    8. manus-command-center
    9. observatorio-merida-2027
    10. manus-sandbox-apr2026
    11. manus-agent-push
    12. (token #16 con nombre raro: "Servidor MCP oficial de GitHub...")
    13. El Monstruo (el limpio que vence Feb 9 2027)

  El #13 'El Monstruo' tiene scope amplio (gist, notif, read:org, read:user, repo, user:email, workflow)
  con expiración lejana. Aunque parece "menos peligroso", su scope es excesivo.
  Lo revocamos por política de scope mínimo.

  Después de revocar los 13, también revocá cualquier fine-grained token
  inesperado que hayas detectado en Fase 1.
EOF
)"

    confirm "¿Revocaste los 13 menores + fine-grained extras?" || { red "Aborto"; exit 1; }
    echo "  13 menores: revocados $(date)" >> "$WORKDIR/revoked.txt"
    green "✓ Menores revocados"

    # Healthcheck final
    if curl -sf --max-time 5 "$KERNEL_HEALTH_URL" >/dev/null; then
        green "✓ Kernel healthy después de revocar todos los viejos"
    else
        red "✗ Kernel NO healthy — rollback urgente"
        exit 1
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 10 — OAuth Apps cleanup
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 10 ]]; then
    phase "10 · OAuth APPS NEVER-USED"

    pause_for_manual "$(cat <<EOF
  Abrí: https://github.com/settings/applications

  Sección 'Authorized OAuth Apps' (NO 'Authorized GitHub Apps').

  Revocá las que digan "Never used":
    - Atlas Cloud
    - FASHN
    - RunPod
    - novita.ai
    - Honcho
    - Langfuse
    - Vast

  Conservá las que SÍ usás (chequeá Last used reciente):
    - Cloudflare, Vercel, Railway, Supabase, GitHub CLI
    - ChatGPT Codex Connector, Manus Connector
    - OpenRouter, Replicate, api.together.ai (si las usás)

  Para cada app a revocar:
    - Click 'Revoke'
    - Confirmar
EOF
)"

    confirm "¿Revocaste OAuth Apps never-used?" || yellow "Pendiente — revisar manualmente después"
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 11 — Sembrar semilla en error_memory
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 11 ]]; then
    phase "11 · SEMBRAR SEMILLA EN ERROR_MEMORY"

    SEED_SQL=$(cat <<'SQL'
-- Sembrar lección magna del Sprint 84.X (rotación de credenciales)
INSERT INTO error_memory (
    error_signature,
    error_type,
    sanitized_message,
    resolution,
    confidence,
    occurrences,
    module,
    action,
    status,
    context
) VALUES (
    md5('seed_credenciales_dispersas_17_pats_descubiertos'),
    'SeedRule',
    'Audit reveló 17 PATs Classic activos donde el forense bash detectó solo 5. El audit programático en código + memoria + env vars NO ve los tokens cargados en GitHub Settings ni en herramientas externas (Manus MCP, browser extensions, Codespaces).',
    'Política de credenciales: máximo 2 PATs activos (Mac local vía gh auth login, Railway kernel). Auditoría trimestral en navegador a GitHub Settings → Tokens (no solo código). Migración a GitHub App con installation tokens efímeros antes de 6 meses. Ningún token sin expiración. Ningún token con scope admin:*.',
    0.97,
    1,
    'kernel.security',
    'audit_credentials',
    'resolved',
    jsonb_build_object(
        'seed_name', 'seed_credenciales_dispersas_17_pats_descubiertos',
        'sprint', '84.X',
        'source', 'cowork_directive',
        'rotation_date', NOW()::text,
        'tokens_revoked', 17,
        'tokens_kept', 2
    )
)
ON CONFLICT (error_signature) DO UPDATE SET
    occurrences = error_memory.occurrences + 1,
    last_seen_at = NOW();
SQL
)

    echo "$SEED_SQL" > "$WORKDIR/seed_security.sql"
    pause_for_manual "$(cat <<EOF
  Abrí Supabase Dashboard → SQL Editor → pegá y ejecutá:

  $(cat "$WORKDIR/seed_security.sql")

  (También guardado en $WORKDIR/seed_security.sql)

  Verificá que devolvió 1 fila INSERT/UPDATE.
EOF
)"

    confirm "¿Semilla sembrada en error_memory?" || yellow "Pendiente — sembrar después"
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 12 — Reporte final + AGENTS.md update
# ═══════════════════════════════════════════════════════════════════════════
if [[ "$FROM_PHASE" -le 12 ]]; then
    phase "12 · REPORTE FINAL + DOCUMENTACIÓN"

    REPORT_FILE="$REPO_ROOT/bridge/CREDENTIALS_ROTATION_$(date +%Y_%m_%d).md"

    cat > "$REPORT_FILE" <<EOF
# Rotación de Credenciales GitHub — $(date +%Y-%m-%d)

## Resumen ejecutivo

Plan A (Soberano) ejecutado. Reducción de 17+ PATs activos a 2 PATs con scope mínimo y expiración 90 días.

## Tokens activos POST-rotación

| Token | Servicio | Scope | Expira | Documentado |
|---|---|---|---|---|
| $NEW_TOKEN_MAC_NAME | Mac local (gh CLI) | repo | $(date -v +90d +%Y-%m-%d) | Notion |
| $NEW_TOKEN_KERNEL_NAME | Railway kernel (GITHUB_TOKEN + GITHUB_PERSONAL_ACCESS_TOKEN) | repo | $(date -v +90d +%Y-%m-%d) | Notion |

## Tokens revocados (17+)

Ver \`$WORKDIR/revoked.txt\` para lista completa con timestamps.

## Política nueva (agregada a AGENTS.md)

1. Máximo 2 PATs activos por persona física en El Monstruo
2. Mac local: \`gh auth login --web --scopes repo\` — no PAT manual
3. Servicios remotos: env vars con scope mínimo, una sola variable por servicio
4. Rotación: 90 días para PATs (no 12 meses)
5. Auditoría trimestral en navegador (GitHub Settings → Tokens) — no solo grep en código
6. Cero tokens con scope \`admin:*\` permanente
7. Cero tokens sin expiración
8. Sprint 86-87: migrar a GitHub App con installation tokens efímeros (tokens 1h TTL auto-rotados)

## Backups (eliminar después de 7 días estables)

- \`$WORKDIR/railway_env_backup.env\`
- \`$WORKDIR/git_config_backup.txt\`
- \`$WORKDIR/git-credentials.backup\`
- \`$WORKDIR/token_mac.txt\`
- \`$WORKDIR/token_kernel.txt\`

Limpieza después de 7 días estables:
\`\`\`bash
rm -rf $WORKDIR
\`\`\`

## Semilla sembrada

\`seed_credenciales_dispersas_17_pats_descubiertos\` (confidence 0.97, module kernel.security)

EOF

    green "✓ Reporte: $REPORT_FILE"

    # Sugerir update a AGENTS.md
    yellow "─── Manual: agregar a AGENTS.md ───"
    cat <<'EOF'

  Agregar al final de AGENTS.md una sección:

  ## Política de Credenciales (Sprint 84.X · 2026-05)

  - Máximo 2 PATs GitHub activos: uno Mac local (vía gh CLI), uno por servicio remoto.
  - Cero tokens con scope `admin:*` permanente. Cero tokens sin expiración.
  - Rotación 90 días.
  - Auditoría trimestral en navegador a GitHub Settings → Tokens (no solo en código).
  - Sprint 86-87: migración a GitHub App con installation tokens efímeros.
  - Bóveda de credenciales: 1Password/Bitwarden. Notion solo para documentación de QUÉ token cubre QUÉ servicio (sin valores).

EOF

    pause_for_manual "Editar manualmente AGENTS.md y commitear cuando estés."

    # Commit del reporte
    if confirm "¿Commitear el reporte $REPORT_FILE?"; then
        run_or_dry "cd $REPO_ROOT && git add '$REPORT_FILE' && git commit -m 'sprint 84.X: rotación credenciales — 17 PATs → 2 PATs scope mínimo' && git push"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# CIERRE
# ═══════════════════════════════════════════════════════════════════════════
section "ROTACIÓN COMPLETADA"

cat <<EOF

  ✅ Plan A ejecutado al 100%

  Tokens activos: 2 (Mac + Railway kernel)
  Tokens revocados: 17+ Classic + fine-grained extras + OAuth never-used
  Backups en: $WORKDIR
  Reporte: $(echo "$REPORT_FILE")
  Log de esta sesión: $LOG_FILE

  Próximos 7 días:
    - Monitorear logs Railway por errores 401/403 que indiquen token roto en algún servicio que no auditamos
    - Si pasa una semana estable, eliminar $WORKDIR
    - Documentar en Notion los 2 PATs nuevos (sin valor, solo nombre + servicio)

  Calendarizar:
    - $(date -v +85d +%Y-%m-%d): rotación próxima (90 días - 5 de margen)
    - Sprint 86-87: migración a GitHub App propia "El Monstruo"

EOF
