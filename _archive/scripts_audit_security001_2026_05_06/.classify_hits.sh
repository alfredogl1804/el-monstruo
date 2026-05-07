#!/bin/bash
# Para cada hit, extraer:
# - File:line
# - Tipo de secret detectado
# - Primer 8 chars + ... + último 4 chars
# - Length total
# - Indicador heurístico real_vs_placeholder

REPO_DIR="${1:-/Users/alfredogongora/el-monstruo}"
cd "$REPO_DIR" || exit 1

mask() {
    # input: secret string. output: first8 + ... + last4 + (len)
    local s="$1"
    local len=${#s}
    if [ "$len" -le 12 ]; then
        echo "<short:${len}>"
    else
        echo "${s:0:8}...${s: -4} (len=${len})"
    fi
}

heuristic() {
    # Determina si el secret parece real o placeholder
    local s="$1"
    local lower=$(echo "$s" | tr '[:upper:]' '[:lower:]')
    if echo "$lower" | grep -qE "your_|placeholder|example|xxxxx|<.*>|tu_key|tu_token|aqui|insert|fake|test_only"; then
        echo "[PLACEHOLDER]"
    elif echo "$lower" | grep -qE "^sk-proj-[a-z0-9]{20}|^sk-ant-[a-z0-9]{30}|^sk_live_[a-z0-9]{20}"; then
        echo "[LIKELY_REAL]"
    else
        echo "[VERIFY_MANUALLY]"
    fi
}

extract_first_match() {
    local file="$1"
    local pattern="$2"
    grep -oE "$pattern" "$file" 2>/dev/null | head -1
}

echo "============================================================"
echo "CLASIFICACION DE HITS — patron por patron"
echo "============================================================"
echo

# === Stripe live keys ===
echo "=== Stripe sk_live_ ==="
for f in bridge/archive/cowork_to_manus_sprint_84_X.md bridge/cowork_to_manus.md bridge/inventario_ecosistema_2026-05-04.md docs/SPRINT_58_PLAN.md kernel/embrion_tecnico.py; do
    if [ -f "$f" ]; then
        # Extraer el match con contexto
        secret=$(grep -oE "sk_live_[A-Za-z0-9]{16,}" "$f" 2>/dev/null | head -1)
        if [ -n "$secret" ]; then
            echo "  $f"
            echo "    -> $(mask "$secret") $(heuristic "$secret")"
        else
            # Es match en discusión, no secret real
            line=$(grep -n "sk_live_" "$f" 2>/dev/null | head -1 | cut -d: -f1-2)
            ctx=$(grep "sk_live_" "$f" 2>/dev/null | head -1 | head -c 80)
            echo "  $f:$line"
            echo "    -> CONTEXT_ONLY: $ctx..."
        fi
    fi
done
echo

# === OpenAI keys ===
echo "=== OpenAI sk-proj- ==="
for f in scripts/_check_no_tokens.sh scripts/inventario_credenciales_ecosistema.sh tests/test_sprint87_2_real_deploy.py; do
    if [ -f "$f" ]; then
        secret=$(grep -oE "sk-proj-[A-Za-z0-9_-]{20,}" "$f" 2>/dev/null | head -1)
        if [ -n "$secret" ]; then
            echo "  $f"
            echo "    -> $(mask "$secret") $(heuristic "$secret")"
        else
            line=$(grep -n "sk-proj-" "$f" 2>/dev/null | head -1 | cut -d: -f1-2)
            ctx=$(grep "sk-proj-" "$f" 2>/dev/null | head -1 | head -c 80)
            echo "  $f:$line"
            echo "    -> CONTEXT_ONLY: $ctx..."
        fi
    fi
done
echo

# === Anthropic keys ===
echo "=== Anthropic sk-ant- ==="
for f in bridge/inventario_ecosistema_2026-05-04.md docs/biblias_v73/BIBLIA_CLAUDE_COWORK_ANTHROPIC_v7.3.md docs/biblias_v73/BIBLIA_CLAUDE_OPUS_4.7_v7.3.md scripts/_check_no_tokens.sh scripts/inventario_credenciales_ecosistema.sh; do
    if [ -f "$f" ]; then
        secret=$(grep -oE "sk-ant-[A-Za-z0-9_-]{30,}" "$f" 2>/dev/null | head -1)
        if [ -n "$secret" ]; then
            echo "  $f"
            echo "    -> $(mask "$secret") $(heuristic "$secret")"
        else
            line=$(grep -n "sk-ant-" "$f" 2>/dev/null | head -1 | cut -d: -f1-2)
            ctx=$(grep "sk-ant-" "$f" 2>/dev/null | head -1 | head -c 80)
            echo "  $f:$line"
            echo "    -> CONTEXT_ONLY: $ctx..."
        fi
    fi
done
echo

# === Postgres URLs con password ===
echo "=== Postgres URLs con password ==="
for f in .env.example docker-compose.yml memory/pg_graph_storage.py scripts/audit_supabase_tokens.py scripts/register_sovereign_browser_tool.py; do
    if [ -f "$f" ]; then
        # Buscar URLs postgres con password
        url=$(grep -oE "postgres(ql)?://[^@\"' ]+@[^/\"' ]+" "$f" 2>/dev/null | head -1)
        if [ -n "$url" ]; then
            # Extraer el password de la URL (entre : y @)
            pwd=$(echo "$url" | sed -E 's|^postgres(ql)?://[^:]+:([^@]+)@.*|\2|')
            echo "  $f"
            if [ -n "$pwd" ] && [ "$pwd" != "$url" ]; then
                echo "    -> URL pwd: $(mask "$pwd") $(heuristic "$pwd")"
                # Marcar si es el password viejo de Supabase
                if [ "$pwd" = "0SsKDCchJpN5GhO3" ]; then
                    echo "    -> [DEAD: pwd viejo Supabase ya rotado]"
                fi
            fi
        fi
    fi
done
echo

# === TiDB connection strings ===
echo "=== TiDB connection strings ==="
for f in bridge/cowork_to_manus.md bridge/sprint_memento_preinvestigation/spec_sprint_memento.md docs/MEMENTO_OPERATIONAL_GUIDE.md kernel/memento/contamination_detector.py kernel/memento/sources.py; do
    if [ -f "$f" ]; then
        # TiDB URL típica: mysql://user:pass@gateway01-XXX.tidbcloud.com:4000
        url=$(grep -oE "mysql://[^@\"' ]+@[^/\"' ]+tidbcloud[^/\"' ]+" "$f" 2>/dev/null | head -1)
        if [ -n "$url" ]; then
            pwd=$(echo "$url" | sed -E 's|^mysql://[^:]+:([^@]+)@.*|\1|')
            echo "  $f"
            if [ -n "$pwd" ] && [ "$pwd" != "$url" ]; then
                echo "    -> URL pwd: $(mask "$pwd") $(heuristic "$pwd")"
            fi
        else
            # Hay solo mención del string tidbcloud, no URL completa
            line=$(grep -n "tidbcloud" "$f" 2>/dev/null | head -1 | cut -d: -f1)
            ctx=$(grep "tidbcloud" "$f" 2>/dev/null | head -1 | head -c 80)
            echo "  $f:$line"
            echo "    -> CONTEXT_ONLY: $ctx..."
        fi
    fi
done
echo

# === Archivos sensibles especiales ===
echo "=== Archivos sensibles ==="
for f in discovery_forense/load_credentials.sh bridge/CREDENTIALS_AUDIT_2026-05-04.md skills/ticketlike-ops/references/credentials.md; do
    if [ -f "$f" ]; then
        echo "  $f ($(wc -l < "$f" | tr -d ' ') lines, $(wc -c < "$f" | tr -d ' ') bytes)"
        # Resumen: cuantos secrets potenciales tiene
        cnt_aws=$(grep -cE "AKIA|sk_live|sk-proj-|sk-ant-|ghp_|password.*=.*[A-Za-z0-9]{12}" "$f" 2>/dev/null || echo 0)
        echo "    -> potential secret count: $cnt_aws"
    fi
done

echo
echo "============================================================"
echo "FIN clasificación"
echo "============================================================"
