#!/bin/bash
# Audit Railway logs + grep codigo kernel por uso de tokens GitHub
# Sprint 85 pre-rotacion

cd ~/el-monstruo || exit 1

echo "=== RAILWAY LOGS kernel: buscar tokens leakeados ==="
railway logs --service el-monstruo-kernel 2>/dev/null | grep -E "ghp_[A-Za-z0-9_]{10,}|github_pat_[A-Za-z0-9_]{10,}" | head -10
echo "(fin scan logs)"
echo ""

echo "=== GREP CODIGO: uso de GITHUB_TOKEN vs GITHUB_PERSONAL_ACCESS_TOKEN ==="
grep -rn "GITHUB_TOKEN\|GITHUB_PERSONAL_ACCESS_TOKEN" \
  --include="*.py" --include="*.ts" --include="*.js" . 2>/dev/null \
  | grep -v "/\.git/" \
  | grep -v "/node_modules/" \
  | grep -v "/\.venv/" \
  | head -50
echo ""

echo "=== ARCHIVOS QUE IMPORTAN GitHub libs ==="
grep -rn "from github\|import github\|@octokit\|github3" \
  --include="*.py" --include="*.ts" --include="*.js" . 2>/dev/null \
  | grep -v "/\.git/" \
  | grep -v "/node_modules/" \
  | grep -v "/\.venv/" \
  | head -20
echo ""

echo "=== USO de tools/code_exec.py si existe (trampa #2 del Sabio) ==="
if [ -f kernel/tools/code_exec.py ]; then
  grep -n "GITHUB" kernel/tools/code_exec.py
elif [ -f tools/code_exec.py ]; then
  grep -n "GITHUB" tools/code_exec.py
fi
echo ""

echo "=== USO de sovereignty/engine.py si existe (trampa #3 del Sabio) ==="
if [ -f kernel/sovereignty/engine.py ]; then
  grep -n "GITHUB" kernel/sovereignty/engine.py
elif [ -f sovereignty/engine.py ]; then
  grep -n "GITHUB" sovereignty/engine.py
fi
echo ""

echo "=== FIN AUDIT ==="
