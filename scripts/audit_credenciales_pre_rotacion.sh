#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# AUDIT DE CREDENCIALES PRE-ROTACIÓN GitHub — El Monstruo
# Sprint 84.X — Auditoría exhaustiva antes de matar tokens viejos
# ═══════════════════════════════════════════════════════════════════
# Uso:
#   cd ~/el-monstruo
#   bash scripts/audit_credenciales_pre_rotacion.sh 2>&1 | tee audit_$(date +%Y%m%d_%H%M).log
# ═══════════════════════════════════════════════════════════════════

set -uo pipefail

REPO_ROOT="${HOME}/el-monstruo"
RESULTS_OK=()
RESULTS_FOUND=()
RESULTS_ERROR=()

GITHUB_TOKEN_REGEX='ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|gho_[A-Za-z0-9]{20,}|ghs_[A-Za-z0-9]{20,}|ghu_[A-Za-z0-9]{20,}'

bold()   { printf "\033[1m%s\033[0m\n" "$*"; }
green()  { printf "\033[32m%s\033[0m\n" "$*"; }
red()    { printf "\033[31m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }
section() { echo; bold "═══ $* ═══"; }

# ─── Pre-flight ────────────────────────────────────────────────────
section "PRE-FLIGHT"
[[ -d "$REPO_ROOT" ]] && green "✓ Repo root existe: $REPO_ROOT" || { red "✗ NO EXISTE: $REPO_ROOT"; exit 1; }
command -v gh >/dev/null 2>&1 && green "✓ gh CLI disponible" || yellow "⚠ gh CLI NO instalada — instalá con: brew install gh"
command -v railway >/dev/null 2>&1 && green "✓ railway CLI disponible" || yellow "⚠ railway CLI NO instalada — instalá con: npm i -g @railway/cli"
command -v jq >/dev/null 2>&1 && green "✓ jq disponible" || yellow "⚠ jq NO instalado — instalá con: brew install jq"

# ─── Check 1: Tokens en código del repo ────────────────────────────
section "1. TOKENS HARD-CODED EN CÓDIGO DEL REPO"
cd "$REPO_ROOT"
matches=$(grep -rEn --include="*.py" --include="*.dart" --include="*.ts" --include="*.js" --include="*.tsx" --include="*.jsx" --include="*.sh" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.toml" --include="*.env*" "$GITHUB_TOKEN_REGEX" . 2>/dev/null | grep -v "node_modules\|\.git/\|build/\|dist/" || true)
if [[ -z "$matches" ]]; then
    green "✓ Cero tokens hard-coded en código fuente"
    RESULTS_OK+=("Código fuente limpio")
else
    red "✗ TOKENS ENCONTRADOS EN CÓDIGO:"
    echo "$matches"
    RESULTS_FOUND+=("Código fuente: $(echo "$matches" | wc -l) hits")
fi

# ─── Check 2: Tokens en bridge files ───────────────────────────────
section "2. TOKENS EN BRIDGE FILES"
bridge_matches=$(grep -rEn "$GITHUB_TOKEN_REGEX" bridge/ 2>/dev/null || true)
if [[ -z "$bridge_matches" ]]; then
    green "✓ Bridges limpios"
    RESULTS_OK+=("Bridge files limpios")
else
    red "✗ TOKENS ENCONTRADOS EN BRIDGES:"
    echo "$bridge_matches"
    RESULTS_FOUND+=("Bridges: leaked tokens")
fi

# ─── Check 3: Tokens en docs/ y AGENTS.md ──────────────────────────
section "3. TOKENS EN DOCUMENTACIÓN"
docs_matches=$(grep -rEn "$GITHUB_TOKEN_REGEX" docs/ AGENTS.md CLAUDE.md README.md 2>/dev/null || true)
if [[ -z "$docs_matches" ]]; then
    green "✓ Docs limpios"
    RESULTS_OK+=("Docs limpios")
else
    red "✗ TOKENS ENCONTRADOS EN DOCS:"
    echo "$docs_matches"
    RESULTS_FOUND+=("Docs: leaked tokens")
fi

# ─── Check 4: Tokens en git history (últimos 100 commits) ──────────
section "4. TOKENS EN GIT HISTORY (últimos 100 commits)"
git_matches=$(git log -p -100 2>/dev/null | grep -aEn "$GITHUB_TOKEN_REGEX" | head -20 || true)
if [[ -z "$git_matches" ]]; then
    green "✓ Git history (100 commits) limpio"
    RESULTS_OK+=("Git history reciente limpio")
else
    red "✗ TOKENS ENCONTRADOS EN GIT HISTORY:"
    echo "$git_matches"
    RESULTS_FOUND+=("Git history: leak permanente, requiere git filter-repo")
fi

# ─── Check 5: Uso de GITHUB_TOKEN vs GITHUB_PERSONAL_ACCESS_TOKEN ──
section "5. CONSUMO DE ENV VARS GITHUB EN CÓDIGO"
echo "Buscando referencias a GITHUB_TOKEN..."
gt_count=$(grep -rEn "GITHUB_TOKEN" --include="*.py" --include="*.dart" --include="*.ts" --include="*.js" . 2>/dev/null | grep -v "node_modules\|\.git/" | wc -l | xargs)
echo "  GITHUB_TOKEN: $gt_count referencias"
grep -rEn "GITHUB_TOKEN" --include="*.py" --include="*.dart" --include="*.ts" --include="*.js" . 2>/dev/null | grep -v "node_modules\|\.git/" | head -10

echo
echo "Buscando referencias a GITHUB_PERSONAL_ACCESS_TOKEN..."
pat_count=$(grep -rEn "GITHUB_PERSONAL_ACCESS_TOKEN" --include="*.py" --include="*.dart" --include="*.ts" --include="*.js" . 2>/dev/null | grep -v "node_modules\|\.git/" | wc -l | xargs)
echo "  GITHUB_PERSONAL_ACCESS_TOKEN: $pat_count referencias"
grep -rEn "GITHUB_PERSONAL_ACCESS_TOKEN" --include="*.py" --include="*.dart" --include="*.ts" --include="*.js" . 2>/dev/null | grep -v "node_modules\|\.git/" | head -10

if [[ "$pat_count" -eq 0 ]]; then
    green "✓ GITHUB_PERSONAL_ACCESS_TOKEN no se usa — eliminar de Railway sin efecto"
    RESULTS_OK+=("Solo GITHUB_TOKEN en uso, consolidación trivial")
elif [[ "$gt_count" -eq 0 ]]; then
    yellow "⚠ Solo se usa GITHUB_PERSONAL_ACCESS_TOKEN — consolidar a GITHUB_TOKEN requiere refactor"
    RESULTS_FOUND+=("Refactor: cambiar PAT por GITHUB_TOKEN en código")
else
    yellow "⚠ AMBAS env vars en uso — refactor para consolidar a una"
    RESULTS_FOUND+=("Refactor: $gt_count usos de GITHUB_TOKEN, $pat_count de GITHUB_PERSONAL_ACCESS_TOKEN")
fi

# ─── Check 6: Workflow scope necesario? ────────────────────────────
section "6. ¿KERNEL TOCA .github/workflows/*.yml?"
workflow_writes=$(grep -rEn "\.github/workflows" --include="*.py" tools/ kernel/ 2>/dev/null || true)
if [[ -z "$workflow_writes" ]]; then
    green "✓ Kernel no toca workflows — quitar 'workflow' scope del token kernel"
    RESULTS_OK+=("Token kernel solo necesita 'repo', no 'workflow'")
else
    yellow "⚠ Kernel referencia .github/workflows en:"
    echo "$workflow_writes"
    RESULTS_FOUND+=("Token kernel necesita scope 'workflow'")
fi

# ─── Check 7: Git credential helper actual ─────────────────────────
section "7. CONFIGURACIÓN GIT CREDENTIAL HELPER"
helper=$(git config --global credential.helper 2>/dev/null || echo "(no configurado)")
echo "Credential helper: $helper"
case "$helper" in
    *osxkeychain*) green "✓ Usa Keychain de macOS — recomendable" ;;
    *store*)       red "✗ Usa archivo plaintext ~/.git-credentials — INSEGURO" ;;
    "(no configurado)") yellow "⚠ Sin helper configurado — git va a pedir password cada vez" ;;
    *)             yellow "⚠ Helper personalizado: $helper — verificar manualmente" ;;
esac
echo
echo "Existencia de ~/.git-credentials:"
[[ -f "$HOME/.git-credentials" ]] && red "✗ ~/.git-credentials existe — contiene tokens en plaintext" || green "✓ ~/.git-credentials no existe"

# ─── Check 8: Repos forja-* en GitHub (si gh disponible) ───────────
section "8. REPOS FORJA-* CON SECRETS Y WORKFLOWS"
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    echo "Listando repos forja-* del usuario..."
    forja_repos=$(gh repo list --limit 100 --json name,visibility,pushedAt 2>/dev/null | jq -r '.[] | select(.name | startswith("forja-")) | .name' || true)
    if [[ -z "$forja_repos" ]]; then
        green "✓ No hay repos forja-* (o gh sin permisos)"
    else
        echo "Repos forja-* encontrados:"
        echo "$forja_repos"
        echo
        echo "Verificando secrets de cada uno..."
        while IFS= read -r repo; do
            [[ -z "$repo" ]] && continue
            secrets=$(gh secret list -R "alfredogl1804/$repo" 2>/dev/null || echo "")
            if [[ -n "$secrets" ]]; then
                yellow "  ⚠ $repo tiene secrets:"
                echo "$secrets" | sed 's/^/    /'
                RESULTS_FOUND+=("Repo $repo tiene secrets - revisar manualmente")
            fi
        done <<< "$forja_repos"
    fi
else
    yellow "⚠ gh CLI no auth o no instalada — saltado. Verificar manualmente en: https://github.com/alfredogl1804?tab=repositories"
fi

# ─── Check 9: Railway env vars del kernel ──────────────────────────
section "9. RAILWAY ENV VARS DEL KERNEL"
if command -v railway >/dev/null 2>&1; then
    echo "Variables de el-monstruo-kernel (sin valores, solo nombres):"
    railway variables --service el-monstruo-kernel 2>/dev/null | grep -E "^[A-Z_]+" | awk '{print $1}' | sort -u || yellow "⚠ Railway CLI no autenticado o servicio no encontrado"
    echo
    echo "Buscando GITHUB_* explícitamente..."
    railway variables --service el-monstruo-kernel --kv 2>/dev/null | grep "^GITHUB" | sed 's/=.*$/=<HIDDEN>/' || yellow "⚠ No pude leer kv"
else
    yellow "⚠ Railway CLI no instalada"
fi

# ─── Check 10: Tokens en logs Railway recientes ────────────────────
section "10. TOKENS EN LOGS RAILWAY (últimas 1000 líneas)"
if command -v railway >/dev/null 2>&1; then
    log_matches=$(railway logs --service el-monstruo-kernel 2>/dev/null | head -1000 | grep -aEo "$GITHUB_TOKEN_REGEX" | sort -u | head -10 || true)
    if [[ -z "$log_matches" ]]; then
        green "✓ Logs Railway recientes limpios"
        RESULTS_OK+=("Railway logs sin tokens leaked")
    else
        red "✗ TOKENS ENCONTRADOS EN LOGS RAILWAY:"
        echo "$log_matches"
        RESULTS_FOUND+=("Railway logs: tokens leaked en producción")
    fi
else
    yellow "⚠ Railway CLI no disponible — verificar manualmente en dashboard"
fi

# ─── Check 11: Dotfiles ────────────────────────────────────────────
section "11. DOTFILES Y CONFIG SHELL"
for f in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile" "$HOME/.zsh_history" "$HOME/.bash_history" "$HOME/.config/gh/hosts.yml" "$HOME/.netrc"; do
    [[ ! -f "$f" ]] && continue
    if grep -aE "$GITHUB_TOKEN_REGEX" "$f" >/dev/null 2>&1; then
        red "✗ Token encontrado en: $f"
        RESULTS_FOUND+=("Dotfile: $f")
    else
        green "✓ $f limpio"
    fi
done

# ─── Resumen final ─────────────────────────────────────────────────
section "RESUMEN FINAL"
echo
green "─── ✓ Verificaciones limpias (${#RESULTS_OK[@]}) ───"
for r in "${RESULTS_OK[@]}"; do echo "  • $r"; done
echo
if [[ ${#RESULTS_FOUND[@]} -gt 0 ]]; then
    red "─── ✗ Hallazgos que requieren acción (${#RESULTS_FOUND[@]}) ───"
    for r in "${RESULTS_FOUND[@]}"; do echo "  • $r"; done
else
    green "─── Sin hallazgos críticos ───"
fi
echo
yellow "─── ⚠ Verificaciones pendientes manuales ───"
echo "  • Manus app/web: Settings → Custom MCP Server → ¿qué token tiene cargado?"
echo "  • Supabase Dashboard SQL: query a 'thoughts' y 'episodic' (ver SQL aparte que Cowork te pasó)"
echo "  • Notion: revisar páginas de credenciales — confirmar tokens documentados vs vivos"
echo "  • Otros Railway projects: 'forja-marketplace-mate', 'forja-saludo-v2', 'truthful-freedom', 'simulador-universal'"
echo "  • Vercel/Netlify: GitHub Apps autorizadas en https://github.com/settings/applications"
echo

bold "Audit completado. Reportá los hallazgos en chat con Cowork antes de generar tokens nuevos."
