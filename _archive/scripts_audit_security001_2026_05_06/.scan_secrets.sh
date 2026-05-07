#!/bin/bash
# ACCION 3: Escaneo profundo del historial git del repo el-monstruo
# Busca el password viejo + otros patrones de secret comunes
# Output: stdout (no escribe archivos sensibles)

REPO_DIR="${1:-/Users/alfredogongora/el-monstruo}"
cd "$REPO_DIR" || { echo "FAIL: no se pudo cd a $REPO_DIR"; exit 1; }

echo "============================================================"
echo "Escaneo profundo de secrets — repo: $REPO_DIR"
echo "============================================================"
echo

# Patrón 1: password viejo Supabase exacto (16 chars)
PWD_OLD="0SsKDCchJpN5GhO3"
echo "=== PATRON 1: password viejo Supabase ($PWD_OLD) ==="
echo "--- En HEAD (working tree) ---"
git grep -l "$PWD_OLD" 2>/dev/null | head -20
echo "--- En historial completo (todas las ramas) ---"
git log --all --pretty=format:'%H %ad %s' --date=short -S "$PWD_OLD" 2>/dev/null | head -20
echo "--- Total commits que tocaron este string ---"
git log --all --pretty=oneline -S "$PWD_OLD" 2>/dev/null | wc -l
echo

# Patrón 2: variantes URL-encoded del mismo password
echo "=== PATRON 2: variantes posibles ==="
for variant in "0SsKDCchJpN5GhO3" "0SsKDCchJpN5GhO3i" "WLfuaWPFgWmOr5c4"; do
    cnt=$(git log --all --pretty=oneline -S "$variant" 2>/dev/null | wc -l | tr -d ' ')
    echo "  variant '${variant:0:6}...' (${#variant} chars): $cnt commits"
done
echo

# Patrón 3: otros secrets típicos
echo "=== PATRON 3: otros secrets comunes en HEAD ==="
echo "--- Stripe live keys (sk_live_) ---"
git grep -l "sk_live_" 2>/dev/null | head -5
echo "--- AWS access key (AKIA...) ---"
git grep -l "AKIA[0-9A-Z]\{16\}" 2>/dev/null | head -5
echo "--- OpenAI keys (sk-proj-...) ---"
git grep -l "sk-proj-" 2>/dev/null | head -5
echo "--- Anthropic keys (sk-ant-) ---"
git grep -l "sk-ant-" 2>/dev/null | head -5
echo "--- HeyGen API keys ---"
git grep -l "HEYGEN_API_KEY.*=.*[A-Za-z0-9]\{20\}" 2>/dev/null | head -5
echo "--- ElevenLabs API keys ---"
git grep -l "ELEVENLABS_API_KEY.*=.*[A-Za-z0-9]\{20\}" 2>/dev/null | head -5
echo "--- GitHub PAT (ghp_) ---"
git grep -l "ghp_[A-Za-z0-9]\{30,\}" 2>/dev/null | head -5
echo "--- Telegram bot tokens ---"
git grep -lE "[0-9]{8,12}:[A-Za-z0-9_-]{30,}" 2>/dev/null | head -5
echo "--- Postgres URLs con password ---"
git grep -lE "postgres(ql)?://[^:]+:[^@]{8,}@" 2>/dev/null | head -10
echo "--- TiDB connection strings ---"
git grep -l "tidbcloud" 2>/dev/null | head -5
echo "--- Railway tokens ---"
git grep -lE "RAILWAY_TOKEN.*=.*[A-Za-z0-9]{20,}" 2>/dev/null | head -5
echo "--- JWT tokens (eyJ...) ---"
git grep -lE "eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+" 2>/dev/null | head -5
echo

# Patrón 4: archivos que típicamente contienen secrets
echo "=== PATRON 4: archivos sensibles trackeados ==="
echo "--- .env trackeados (debería ser CERO) ---"
git ls-files | grep -E "^\.env$|/\.env$|^\.env\.|\.env\.local$" 2>/dev/null | head -10
echo "--- credentials.* / secrets.* ---"
git ls-files | grep -iE "credentials|secrets\." 2>/dev/null | head -10
echo "--- private keys (.pem .key) ---"
git ls-files | grep -E "\.pem$|\.key$|id_rsa|id_ed25519" 2>/dev/null | head -10
echo

# Patrón 5: stashes
echo "=== PATRON 5: stashes ==="
git stash list 2>/dev/null | head -10
echo "--- Stashes que contienen pwd viejo ---"
for s in $(git stash list --pretty=format:%gd 2>/dev/null); do
    if git stash show -p "$s" 2>/dev/null | grep -q "$PWD_OLD"; then
        echo "  $s contiene pwd viejo"
    fi
done

echo
echo "============================================================"
echo "Escaneo completo."
echo "============================================================"
