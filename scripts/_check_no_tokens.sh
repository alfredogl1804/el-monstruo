#!/usr/bin/env bash
# Verifica que ningún archivo en scripts/ contiene tokens hardcoded
set -uo pipefail
cd "$(dirname "$0")"
PATTERN='ghp_[A-Za-z0-9]{36,}|sk-proj-[A-Za-z0-9_-]{30,}|sk-ant-api03-[A-Za-z0-9_-]{30,}|AIzaSy[A-Za-z0-9_-]{20,}|sk-or-v1-[a-f0-9]{30,}|xai-[A-Za-z0-9]{30,}|pplx-[A-Za-z0-9]{30,}'
FOUND=0
for f in install_mcp_github_monstruo.sh audit_credenciales_pre_rotacion.sh audit_railway_and_code.sh audit_supabase_tokens.py rotacion_tokens_plan_a.sh; do
  if [[ -f "$f" ]]; then
    if grep -EH "$PATTERN" "$f" > /dev/null 2>&1; then
      echo "$f: CONTIENE TOKEN"
      FOUND=1
    else
      echo "$f: limpio"
    fi
  else
    echo "$f: NO EXISTE"
  fi
done
exit $FOUND
