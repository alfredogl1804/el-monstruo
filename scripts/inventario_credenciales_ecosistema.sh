#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# INVENTARIO DE CREDENCIALES DEL ECOSISTEMA · El Monstruo · 2026-05
# ═══════════════════════════════════════════════════════════════════════════
# Discovery (NO rotación) de todas las credenciales del ecosistema fuera de
# GitHub (que ya rotamos en Plan A).
#
# Cubre: filesystem Mac, Bitwarden vault, Railway envs, Mac Keychain, código
# del repo. Para cada provider lista qué se encontró + URL de su dashboard
# para verificación manual.
#
# Uso:
#   cd ~/el-monstruo
#   bash scripts/inventario_credenciales_ecosistema.sh 2>&1 | tee inventario_$(date +%Y%m%d_%H%M).log
#
# Variables opcionales:
#   SKIP_BW=1           # Saltar Bitwarden (si no está bw CLI)
#   SKIP_RAILWAY=1      # Saltar Railway
#   SKIP_KEYCHAIN=1     # Saltar Keychain (algunos sistemas piden password)
#   VERBOSE=1           # Mostrar valores parciales (primeros 8 chars de cada key)
#
# Output: archivo Markdown estructurado en
#   ~/.monstruo-inventory-2026-05/inventario_$(date +%Y%m%d_%H%M).md
# ═══════════════════════════════════════════════════════════════════════════

set -uo pipefail

# ─── Config ────────────────────────────────────────────────────────────────
WORKDIR="${HOME}/.monstruo-inventory-2026-05"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT="${WORKDIR}/inventario_${TIMESTAMP}.md"
LOG_FILE="${WORKDIR}/inventario_${TIMESTAMP}.log"
REPO_ROOT="${HOME}/el-monstruo"

SKIP_BW="${SKIP_BW:-0}"
SKIP_RAILWAY="${SKIP_RAILWAY:-0}"
SKIP_KEYCHAIN="${SKIP_KEYCHAIN:-0}"
VERBOSE="${VERBOSE:-0}"

mkdir -p "$WORKDIR"
chmod 700 "$WORKDIR"
exec > >(tee -a "$LOG_FILE") 2>&1

# ─── Helpers ───────────────────────────────────────────────────────────────
bold()    { printf "\033[1m%s\033[0m\n" "$*"; }
green()   { printf "\033[32m%s\033[0m\n" "$*"; }
red()     { printf "\033[31m%s\033[0m\n" "$*"; }
yellow()  { printf "\033[33m%s\033[0m\n" "$*"; }
blue()    { printf "\033[34m%s\033[0m\n" "$*"; }
section() { echo; bold "═══════════════════════════════════════════════════════════════"; bold "  $*"; bold "═══════════════════════════════════════════════════════════════"; }

# Acumuladores para reporte
declare -a FINDINGS
add_finding() {
    local provider="$1"
    local source="$2"
    local detail="$3"
    local risk="$4"
    FINDINGS+=("$provider|$source|$detail|$risk")
}

# Pattern matching por provider (extensible)
declare -A PATTERNS=(
    ["openai"]='sk-[A-Za-z0-9_-]{20,}|sk-proj-[A-Za-z0-9_-]{40,}'
    ["anthropic"]='sk-ant-[A-Za-z0-9_-]{40,}|sk-ant-api[0-9]{2}-[A-Za-z0-9_-]{40,}'
    ["google"]='AIza[A-Za-z0-9_-]{35}'
    ["xai"]='xai-[A-Za-z0-9]{40,}'
    ["perplexity"]='pplx-[A-Za-z0-9]{40,}'
    ["replicate"]='r8_[A-Za-z0-9]{37}'
    ["elevenlabs"]='sk_[a-f0-9]{32,}|xi-api-[A-Za-z0-9]{32,}'
    ["stripe_live"]='sk_live_[A-Za-z0-9]{20,}|rk_live_[A-Za-z0-9]{20,}|pk_live_[A-Za-z0-9]{20,}'
    ["stripe_test"]='sk_test_[A-Za-z0-9]{20,}|pk_test_[A-Za-z0-9]{20,}'
    ["sendgrid"]='SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}'
    ["twilio_account"]='AC[a-f0-9]{32}'
    ["twilio_api"]='SK[a-f0-9]{32}'
    ["resend"]='re_[A-Za-z0-9]{40,}'
    ["cloudflare"]='[A-Za-z0-9_-]{40}'  # genérico, validar manualmente
    ["supabase_anon"]='eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
    ["railway"]='[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'  # UUID format
    ["mistral"]='[A-Za-z0-9]{32}'  # genérico
    ["deepseek"]='sk-[a-f0-9]{32,}'
    ["moonshot"]='sk-[A-Za-z0-9]{40,}'
)

# ═══════════════════════════════════════════════════════════════════════════
section "INVENTARIO DE CREDENCIALES · El Monstruo · $(date)"
echo "Workdir: $WORKDIR"
echo "Reporte final: $REPORT"
echo

# ─── Inicio del reporte Markdown ───────────────────────────────────────────
cat > "$REPORT" <<EOF
# Inventario de Credenciales del Ecosistema — $(date +%Y-%m-%d)

> **Generado por:** \`scripts/inventario_credenciales_ecosistema.sh\`
> **Timestamp:** $(date)
> **Host:** $(hostname)

EOF

# ═══════════════════════════════════════════════════════════════════════════
section "1. PRE-FLIGHT CHECKS"
echo "## 1. Pre-flight checks" >> "$REPORT"
echo >> "$REPORT"

CHECKS_OK=()
CHECKS_MISSING=()

if command -v bw >/dev/null 2>&1; then
    green "✓ Bitwarden CLI disponible"
    CHECKS_OK+=("bw")
else
    yellow "⚠ Bitwarden CLI no instalada — saltar inventario Bitwarden"
    CHECKS_MISSING+=("bw")
    SKIP_BW=1
fi

if command -v railway >/dev/null 2>&1; then
    green "✓ Railway CLI disponible"
    CHECKS_OK+=("railway")
else
    yellow "⚠ Railway CLI no instalada — saltar inventario Railway"
    CHECKS_MISSING+=("railway")
    SKIP_RAILWAY=1
fi

if command -v jq >/dev/null 2>&1; then
    green "✓ jq disponible"
    CHECKS_OK+=("jq")
else
    yellow "⚠ jq no instalado — algunas funciones limitadas"
    CHECKS_MISSING+=("jq")
fi

if [[ -d "$REPO_ROOT" ]]; then
    green "✓ Repo: $REPO_ROOT"
    CHECKS_OK+=("repo")
else
    red "✗ Repo no existe en $REPO_ROOT"
fi

echo "- Disponibles: ${CHECKS_OK[*]}" >> "$REPORT"
[[ ${#CHECKS_MISSING[@]} -gt 0 ]] && echo "- Faltantes: ${CHECKS_MISSING[*]}" >> "$REPORT"
echo >> "$REPORT"

# ═══════════════════════════════════════════════════════════════════════════
section "2. INVENTARIO BITWARDEN VAULT"
echo "## 2. Bitwarden vault" >> "$REPORT"
echo >> "$REPORT"

if [[ "$SKIP_BW" == "1" ]]; then
    yellow "⚠ Saltado (SKIP_BW=1 o bw no instalada)"
    echo "**Saltado.** Para inventariar Bitwarden:" >> "$REPORT"
    echo "1. Instalar: \`brew install bitwarden-cli\` o \`npm install -g @bitwarden/cli\`" >> "$REPORT"
    echo "2. Login: \`bw login alfredogl1.gongora@gmail.com\`" >> "$REPORT"
    echo "3. Re-correr este script" >> "$REPORT"
    echo >> "$REPORT"
else
    # Verificar status de bw
    BW_STATUS=$(bw status 2>/dev/null | jq -r '.status' 2>/dev/null || echo "unknown")
    echo "Estado bw: $BW_STATUS"

    if [[ "$BW_STATUS" == "unauthenticated" ]]; then
        yellow "⚠ bw no autenticado. Ejecutá: bw login"
        echo "**bw no autenticado.** Login con: \`bw login alfredogl1.gongora@gmail.com\`" >> "$REPORT"
    elif [[ "$BW_STATUS" == "locked" ]]; then
        yellow "⚠ Vault locked. Ejecutá: export BW_SESSION=\$(bw unlock --raw)"
        echo "**Vault locked.** Unlock con: \`export BW_SESSION=\$(bw unlock --raw)\`" >> "$REPORT"
    elif [[ "$BW_STATUS" == "unlocked" ]]; then
        green "✓ bw vault unlocked"
        echo "**Items en vault:**" >> "$REPORT"
        echo >> "$REPORT"
        echo "| Nombre | Username | Notas (preview) |" >> "$REPORT"
        echo "|---|---|---|" >> "$REPORT"

        bw list items 2>/dev/null | jq -r '.[] | [.name, (.login.username // "-"), ((.notes // "")[0:80] | gsub("\n";" "))] | @tsv' 2>/dev/null | while IFS=$'\t' read -r name user notes; do
            echo "| $name | $user | $notes |" >> "$REPORT"
        done

        TOTAL=$(bw list items 2>/dev/null | jq '. | length' 2>/dev/null || echo "?")
        green "✓ $TOTAL items en Bitwarden vault"
        echo >> "$REPORT"
        echo "**Total: $TOTAL items.**" >> "$REPORT"
    else
        red "✗ Estado bw desconocido: $BW_STATUS"
    fi
fi
echo >> "$REPORT"

# ═══════════════════════════════════════════════════════════════════════════
section "3. INVENTARIO RAILWAY (todos los projects, todos los services)"
echo "## 3. Railway env vars (nombres, sin valores)" >> "$REPORT"
echo >> "$REPORT"

if [[ "$SKIP_RAILWAY" == "1" ]]; then
    yellow "⚠ Saltado"
    echo "**Saltado** (railway CLI no instalada o SKIP_RAILWAY=1)." >> "$REPORT"
else
    if ! railway whoami >/dev/null 2>&1; then
        yellow "⚠ railway no autenticado. Ejecutá: railway login"
        echo "**railway no autenticado.** Login con \`railway login\`." >> "$REPORT"
    else
        green "✓ railway autenticado como: $(railway whoami 2>/dev/null)"
        echo "Listando projects..."

        # Algunas versiones de railway requieren cwd con un proyecto vinculado.
        # Mejor: usar railway list o iterar manualmente.
        # Como hack: si no puede listar, pedir manual.

        railway list 2>/dev/null > "$WORKDIR/railway_projects.txt" || echo "" > "$WORKDIR/railway_projects.txt"

        if [[ -s "$WORKDIR/railway_projects.txt" ]]; then
            echo "**Projects detectados:**" >> "$REPORT"
            echo '```' >> "$REPORT"
            cat "$WORKDIR/railway_projects.txt" >> "$REPORT"
            echo '```' >> "$REPORT"
        fi

        echo >> "$REPORT"
        echo "**Env vars del kernel (\`el-monstruo-kernel\`):**" >> "$REPORT"
        echo >> "$REPORT"
        echo '```' >> "$REPORT"
        railway variables --service el-monstruo-kernel 2>/dev/null | grep -E "^[A-Z_]+" | awk '{print $1}' | sort -u >> "$REPORT" || echo "(no pude leer)" >> "$REPORT"
        echo '```' >> "$REPORT"
        echo >> "$REPORT"

        # Detectar patrones de credenciales por nombre de var
        CRED_VARS=$(railway variables --service el-monstruo-kernel 2>/dev/null | grep -iE "_KEY=|_TOKEN=|_SECRET=|_PASSWORD=|API_=" | awk -F'=' '{print $1}' | sort -u)
        if [[ -n "$CRED_VARS" ]]; then
            echo "**Variables con apariencia de credencial:**" >> "$REPORT"
            echo >> "$REPORT"
            echo "$CRED_VARS" | while read -r var; do
                add_finding "Railway" "kernel env var" "$var" "C"
                echo "- $var" >> "$REPORT"
            done
            echo >> "$REPORT"
        fi

        yellow "MANUAL: revisá también services del project que NO sean el kernel:"
        echo "**MANUAL:** Otros services del project \`celebrated-achievement\` o de otros projects (ticketlike, etc.):" >> "$REPORT"
        echo "Ejecutá: \`railway projects\` y por cada project: \`railway service list\`" >> "$REPORT"
    fi
fi
echo >> "$REPORT"

# ═══════════════════════════════════════════════════════════════════════════
section "4. DOTFILES Y CONFIG SHELL"
echo "## 4. Dotfiles del Mac" >> "$REPORT"
echo >> "$REPORT"

DOTFILES=(
    "$HOME/.netrc"
    "$HOME/.npmrc"
    "$HOME/.docker/config.json"
    "$HOME/.aws/credentials"
    "$HOME/.aws/config"
    "$HOME/.gcloud/credentials"
    "$HOME/.config/gcloud/credentials.db"
    "$HOME/.config/gh/hosts.yml"
    "$HOME/.config/openai/auth.json"
    "$HOME/.cursor/auth"
    "$HOME/.zshenv"
    "$HOME/.zprofile"
    "$HOME/.bash_profile"
)

echo "| Archivo | Existe | Tiene credenciales? |" >> "$REPORT"
echo "|---|---|---|" >> "$REPORT"

for f in "${DOTFILES[@]}"; do
    if [[ -f "$f" ]]; then
        # Buscar patterns de credenciales
        FOUND_CREDS=""
        for provider in "${!PATTERNS[@]}"; do
            if grep -aE "${PATTERNS[$provider]}" "$f" >/dev/null 2>&1; then
                FOUND_CREDS="$FOUND_CREDS $provider"
            fi
        done

        if [[ -n "$FOUND_CREDS" ]]; then
            red "✗ $f tiene credenciales:$FOUND_CREDS"
            echo "| \`$(basename "$f")\` | ✓ | $FOUND_CREDS |" >> "$REPORT"
            for prov in $FOUND_CREDS; do
                add_finding "$prov" "dotfile" "$f" "varies"
            done
        else
            green "✓ $f limpio"
            echo "| \`$(basename "$f")\` | ✓ | - |" >> "$REPORT"
        fi
    else
        echo "| \`$(basename "$f")\` | - | n/a |" >> "$REPORT"
    fi
done
echo >> "$REPORT"

# ─── Buscar archivos .env* en home ─────────────────────────────────────────
echo "**Archivos .env* en \$HOME (no en el repo):**" >> "$REPORT"
ENV_FILES=$(find "$HOME" -maxdepth 3 -name ".env*" -type f 2>/dev/null | grep -v node_modules | grep -v "\.git/" | head -20)
if [[ -n "$ENV_FILES" ]]; then
    echo '```' >> "$REPORT"
    echo "$ENV_FILES" >> "$REPORT"
    echo '```' >> "$REPORT"
    yellow "⚠ Archivos .env* en home:"
    echo "$ENV_FILES"
    while IFS= read -r f; do
        for provider in "${!PATTERNS[@]}"; do
            if grep -aE "${PATTERNS[$provider]}" "$f" >/dev/null 2>&1; then
                add_finding "$provider" ".env file" "$f" "varies"
            fi
        done
    done <<< "$ENV_FILES"
else
    green "✓ No hay .env* en home"
    echo "(Sin archivos)" >> "$REPORT"
fi
echo >> "$REPORT"

# ═══════════════════════════════════════════════════════════════════════════
section "5. KEYCHAIN MAC (entradas relevantes)"
echo "## 5. Mac Keychain" >> "$REPORT"
echo >> "$REPORT"

if [[ "$SKIP_KEYCHAIN" == "1" ]]; then
    yellow "⚠ Saltado (SKIP_KEYCHAIN=1)"
    echo "**Saltado** por SKIP_KEYCHAIN=1." >> "$REPORT"
else
    echo "Buscando entradas con nombres de providers comunes (puede pedir password)..."
    PROVIDERS_KC=("openai" "anthropic" "google" "perplexity" "xai" "stripe" "twilio" "elevenlabs" "replicate" "supabase" "cloudflare" "vercel" "notion" "slack" "linear")

    echo "| Provider | Entradas en Keychain |" >> "$REPORT"
    echo "|---|---|" >> "$REPORT"

    for prov in "${PROVIDERS_KC[@]}"; do
        # Búsqueda por server name (internet password) y por service (generic password)
        FOUND_INET=$(security find-internet-password -s "$prov" 2>/dev/null | head -1 || echo "")
        FOUND_GEN=$(security find-generic-password -s "$prov" 2>/dev/null | head -1 || echo "")

        if [[ -n "$FOUND_INET" || -n "$FOUND_GEN" ]]; then
            yellow "⚠ Keychain tiene entradas de $prov"
            echo "| $prov | sí (internet o generic) |" >> "$REPORT"
            add_finding "$prov" "Keychain Mac" "internet/generic password" "varies"
        else
            echo "| $prov | - |" >> "$REPORT"
        fi
    done
fi
echo >> "$REPORT"

# ═══════════════════════════════════════════════════════════════════════════
section "6. CÓDIGO DEL REPO (grep por patterns)"
echo "## 6. Repo el-monstruo (grep por patterns)" >> "$REPORT"
echo >> "$REPORT"

cd "$REPO_ROOT"
echo "| Provider | Hits en código | Files |" >> "$REPORT"
echo "|---|---|---|" >> "$REPORT"

# Excluir directorios voluminosos y bridge (donde sabemos hay leaks históricos discutidos)
EXCLUDES="--exclude-dir=node_modules --exclude-dir=.git --exclude-dir=build --exclude-dir=dist --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=venv"

for provider in "${!PATTERNS[@]}"; do
    HITS=$(grep -rEn $EXCLUDES "${PATTERNS[$provider]}" . 2>/dev/null | wc -l | xargs)
    if [[ "$HITS" -gt 0 ]]; then
        FILES_LIST=$(grep -rlE $EXCLUDES "${PATTERNS[$provider]}" . 2>/dev/null | head -5 | tr '\n' ',' | sed 's/,$//')
        red "✗ $provider: $HITS hits"
        echo "| $provider | $HITS | $FILES_LIST |" >> "$REPORT"
        add_finding "$provider" "código repo" "$HITS hits en $FILES_LIST" "high"
    else
        green "✓ $provider: 0"
        echo "| $provider | 0 | - |" >> "$REPORT"
    fi
done
echo >> "$REPORT"

# ═══════════════════════════════════════════════════════════════════════════
section "7. PROVIDERS CONOCIDOS — VERIFICACIÓN MANUAL"
cat >> "$REPORT" <<'EOF'
## 7. Providers conocidos — verificación manual en dashboards

Para cada provider abrí el dashboard, listá keys activas, anotá:
- Cantidad total
- "Last used" de cada una
- Scopes/permissions
- Cuáles seguís usando vs cuáles son legacy

### Categoría A — Catastrófica (rotar HOY si hay sospecha)

| Provider | Dashboard | Tipo de riesgo |
|---|---|---|
| Stripe LIVE | https://dashboard.stripe.com/apikeys | Robo de dinero real, refunds fraudulentos |
| AWS root | https://console.aws.amazon.com/iam/home#/security_credentials | Cuenta entera, billing nuclear |
| Banking APIs (Belvo, Plaid) | provider | Datos financieros del cliente |

### Categoría B — Costo $$$$ (rotar esta semana)

| Provider | Dashboard | Tipo de riesgo |
|---|---|---|
| OpenAI | https://platform.openai.com/api-keys | Billing $$$$ rápido |
| Anthropic | https://console.anthropic.com/settings/keys | Billing $$$$ rápido |
| Google AI / Gemini | https://aistudio.google.com/app/apikey | Billing |
| Perplexity | https://www.perplexity.ai/settings/api | Billing |
| Replicate | https://replicate.com/account/api-tokens | GPU billing |
| ElevenLabs | https://elevenlabs.io/app/settings/api-keys | Voice generation $$ |
| Twilio | https://console.twilio.com/ | SMS spam masivo |
| SendGrid | https://app.sendgrid.com/settings/api_keys | Email spam masivo |
| Resend | https://resend.com/api-keys | Email spam masivo |

### Categoría C — Infra crítica (rotar coordinada con redeploy)

| Provider | Dashboard | Notas |
|---|---|---|
| Railway API tokens | https://railway.com/account/tokens | Si filtran, atacante deploya o destroza |
| Supabase service_role | https://supabase.com/dashboard/project/_/settings/api | Acceso DB sin RLS |
| Cloudflare API | https://dash.cloudflare.com/profile/api-tokens | DNS, Workers, R2 |
| Vercel | https://vercel.com/account/tokens | Si tenés despliegues ahí |

### Categoría D — Datos privados (rotar este mes)

| Provider | Dashboard |
|---|---|
| Notion API | https://www.notion.so/profile/integrations |
| Slack Apps | https://api.slack.com/apps |
| Linear API | https://linear.app/settings/api |
| Asana | https://app.asana.com/0/my-apps |
| Gmail OAuth | https://myaccount.google.com/permissions |

### Categoría E — Operacionales menores

| Provider | Dashboard |
|---|---|
| xAI / Grok | https://console.x.ai/ |
| Kimi (Moonshot) | https://platform.moonshot.cn/console/api-keys |
| DeepSeek | https://platform.deepseek.com/api_keys |
| Mistral AI | https://console.mistral.ai/api-keys |
| Together AI | https://api.together.ai/settings/api-keys |
| Honcho | provider dashboard |
| Langfuse | https://cloud.langfuse.com/project/_/settings |
| Apify | https://console.apify.com/account/integrations |
| E2B | https://e2b.dev/dashboard |

### Otros que pueden tener tokens

- RunPod: https://www.runpod.io/console/user/settings
- vast.ai: https://cloud.vast.ai/account/
- HuggingFace: https://huggingface.co/settings/tokens
- ngrok: https://dashboard.ngrok.com/get-started/your-authtoken
- Tailscale: https://login.tailscale.com/admin/settings/keys
- 1Password / Bitwarden / Doppler / Infisical (si bóveda secundaria)

EOF

# ═══════════════════════════════════════════════════════════════════════════
section "8. RESUMEN DE FINDINGS"
echo "## 8. Resumen de findings (automatizado)" >> "$REPORT"
echo >> "$REPORT"

if [[ ${#FINDINGS[@]} -eq 0 ]]; then
    green "✓ Cero credenciales detectadas en filesystem/Railway/repo (audit automático)"
    echo "**Cero credenciales detectadas en lugares automatizados.**" >> "$REPORT"
    echo >> "$REPORT"
    echo "Esto NO significa que no haya credenciales en el ecosistema — significa que" >> "$REPORT"
    echo "no están en lugares que el audit programático pueda ver. Las credenciales" >> "$REPORT"
    echo "viven principalmente en dashboards web de cada provider. Procedé con la" >> "$REPORT"
    echo "verificación manual de la sección 7." >> "$REPORT"
else
    echo "Total findings: ${#FINDINGS[@]}"
    echo "**Total findings: ${#FINDINGS[@]}**" >> "$REPORT"
    echo >> "$REPORT"
    echo "| Provider | Source | Detail | Risk |" >> "$REPORT"
    echo "|---|---|---|---|" >> "$REPORT"
    for f in "${FINDINGS[@]}"; do
        IFS='|' read -r prov src det rsk <<< "$f"
        echo "| $prov | $src | $det | $rsk |" >> "$REPORT"
    done
fi
echo >> "$REPORT"

# ═══════════════════════════════════════════════════════════════════════════
section "9. PRÓXIMOS PASOS"
cat >> "$REPORT" <<EOF
## 9. Próximos pasos sugeridos

### Inmediato (hoy o mañana)

1. **Verificación manual de Categoría A** (Stripe live si lo usás, AWS, banking) — 10 min
2. **Inventario manual de Categoría B** (LLM providers + Twilio + SendGrid + ElevenLabs + Replicate) — 30 min
   - Por cada uno: cuántas keys activas, last used, cuáles deprecar
3. **Capturar inventario en archivo** \`bridge/CREDENTIALS_ECOSYSTEM_INVENTORY_$(date +%Y_%m_%d).md\`

### Esta semana

4. **Rotación coordinada de Categoría B**: una key activa por servicio, en Bitwarden
5. **Setear quotas + alertas de gasto** en cada provider que lo permita (OpenAI, Anthropic, etc.)
6. **Activar IP allowlist** donde se pueda (OpenAI permite, Anthropic permite, Cloudflare permite)

### Próxima semana

7. **Rotación Categoría C** (Railway API token + Supabase service_role) — coordinada con redeploy del kernel
8. **Migración de credenciales sueltas a Bitwarden** — fuente única de verdad

### Sprint 87+

9. **Doppler o Infisical** para inyección automática de secrets a Railway sin que estén hardcoded en env vars
10. **GitHub App propia** para reemplazar los 2 PATs activos (deuda existente)

---

> **Reporte generado:** $(date)
> **Para correr de nuevo:** \`bash scripts/inventario_credenciales_ecosistema.sh\`
EOF

# ═══════════════════════════════════════════════════════════════════════════
section "INVENTARIO COMPLETADO"
echo
green "✅ Reporte generado en:"
echo "   $REPORT"
echo
green "✅ Log de la sesión:"
echo "   $LOG_FILE"
echo
yellow "Próximo paso:"
echo "   1. Abrí el reporte: open '$REPORT'"
echo "   2. Reportá a Cowork lo más relevante de la sección 'Findings' y de la sección 7 (manual)"
echo "   3. Cowork te diseña el plan de rotación por categoría"
echo
