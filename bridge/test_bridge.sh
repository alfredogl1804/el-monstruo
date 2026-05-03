#!/bin/bash
# Test: Manus → Claude Code bridge
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY ~/.zshrc | cut -d'"' -f2)
cd ~/el-monstruo

claude -p "Lee CLAUDE.md y responde en UNA linea que proyecto es" \
  --bare \
  --allowedTools "Read" \
  --output-format json \
  2>/dev/null > /tmp/bridge_result.json

python3 -c "
import json
with open('/tmp/bridge_result.json') as f:
    d = json.load(f)
print(d.get('result','ERROR'))
"
