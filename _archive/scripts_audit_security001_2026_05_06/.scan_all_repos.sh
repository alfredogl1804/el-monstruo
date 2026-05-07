#!/bin/bash
# ACCION 4 SECURITY-001: escanear todos los repos del ecosistema
# Output: /tmp/scan_results.txt

OUTPUT=/tmp/scan_results.txt
echo "============================================================" > $OUTPUT
echo "ACCION 4 SECURITY-001: scan all repos at $(date)" >> $OUTPUT
echo "============================================================" >> $OUTPUT
echo >> $OUTPUT

REPOS=(
    biblia-github-motor crisol-8 el-monstruo-bot el-monstruo-command-center
    el-mundo-de-tata forja-api-hello forja-landing-pintura-oleo forja-landing-pintura-oleo-v2
    forja-magna-test-wrapper forja-magna-test-wrapper-v2 forja-marketplace-mate-1777801830
    forja-saludo-monstruo-1777800772 forja-saludo-monstruo-v2-1777801675
    honcho-railway k365-knowledge-repo like-kukulkan-tickets
    manus-memory-merida2027 monstruo-hac--una-landing-premium-para--0_9e2e6c
    monstruo-hac--una-landing-premium-para--3_888e5d monstruo-hac--una-landing-premium-para--4_401772
    monstruo-hace-una-landing-premium-para--1_2c15ec monstruo-hace-una-landing-premium-para--2_bcafee
    monstruo-hace-una-landing-premium-para--2_df60e8 monstruo-hace-una-landing-premium-para--3_e85981
    monstruo-hace-una-landing-premium-para--4_d260cc monstruo-hace-una-landing-premium-para--7_c4ec87
    monstruo-hace-una-landing-premium-para--7_f71120 monstruo-hace-una-landing-premium-para--9_4a4e12
    monstruo-hace-una-landing-premium-para--9_a95211 observatorio-merida-2027 rug-carousel
    simulador-universal test-manus-github-cli
)

WORK=/tmp/repo_scan_work
mkdir -p $WORK

cd $WORK
total=${#REPOS[@]}
i=0
for repo in "${REPOS[@]}"; do
    i=$((i+1))
    echo "[$i/$total] Scanning $repo..."
    SCAN_DIR="$WORK/$repo"
    if [ ! -d "$SCAN_DIR" ]; then
        gh repo clone alfredogl1804/$repo $SCAN_DIR -- --depth 1 --quiet 2>/dev/null
    fi
    if [ ! -d "$SCAN_DIR" ]; then
        echo "  $repo: CLONE_FAIL" >> $OUTPUT
        continue
    fi
    # Run gitleaks on HEAD only
    cd $SCAN_DIR
    leaks=$(gitleaks detect --source . --no-git --report-format json --report-path /tmp/leak_$repo.json --redact 2>&1 | grep -E "leaks found|no leaks found" | head -1)
    n_leaks=$(jq 'length' /tmp/leak_$repo.json 2>/dev/null || echo "0")
    if [ "$n_leaks" -gt 0 ] 2>/dev/null; then
        echo "  $repo: 🚨 $n_leaks LEAKS" >> $OUTPUT
        # Listar tipos de leak
        jq -r '.[] | "    - \(.RuleID) en \(.File):\(.StartLine)"' /tmp/leak_$repo.json 2>/dev/null | head -15 >> $OUTPUT
    else
        # Verificar que el escaneo fue exitoso (no error)
        if echo "$leaks" | grep -q "no leaks found"; then
            echo "  $repo: ✅ clean" >> $OUTPUT
        else
            echo "  $repo: ⚠️ scan_inconclusive ($leaks)" >> $OUTPUT
        fi
    fi
    cd $WORK
    rm -rf $SCAN_DIR
    rm -f /tmp/leak_$repo.json
done

echo >> $OUTPUT
echo "============================================================" >> $OUTPUT
echo "Scan completo. Total repos: $total" >> $OUTPUT
echo "============================================================" >> $OUTPUT

cat $OUTPUT | head -100
