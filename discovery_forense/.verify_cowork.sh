#!/bin/bash
TOKEN=$(security find-generic-password -s "monstruo-notion" -w 2>/dev/null)
if [ -z "$TOKEN" ]; then
  echo "EMPTY TOKEN"
  exit 1
fi
echo "Token prefix: ${TOKEN:0:10}... length: ${#TOKEN}"
echo ""
echo "=== Test 1: /users/me ==="
curl -s -H "Authorization: Bearer $TOKEN" -H "Notion-Version: 2022-06-28" https://api.notion.com/v1/users/me
echo ""
echo ""
echo "=== Test 2: search 'Plan de Construccion' ==="
curl -s -H "Authorization: Bearer $TOKEN" -H "Notion-Version: 2022-06-28" -H "Content-Type: application/json" -X POST https://api.notion.com/v1/search -d '{"query":"Plan de Construccion","page_size":3}'
echo ""
echo ""
echo "=== Test 3: search Monstruo ==="
curl -s -H "Authorization: Bearer $TOKEN" -H "Notion-Version: 2022-06-28" -H "Content-Type: application/json" -X POST https://api.notion.com/v1/search -d '{"query":"Monstruo","page_size":5}'
