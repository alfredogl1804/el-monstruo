# Ticket: MANUS_API_KEY_GOOGLE_REGEN_001

**Tipo:** Acción manual pendiente (Alfredo)
**Prioridad:** Media (no bloquea producción, bloquea bridge inter-cuenta Google→Apple)
**Estado:** ABIERTO
**Creado:** 2026-05-12 por Hilo Ejecutor 1
**Bloquea:** Bridge inter-cuenta Manus completo (mitad Google sigue rota)

---

## Contexto

Durante el sprint TOKENS-BRIDGE-FIX (2026-05-12), verificación binaria reveló que `MANUS_API_KEY_GOOGLE` es **inválido** incluso después de limpiar trailing newlines:

```
GET https://api.manus.ai/v2/skill.list
Header: x-manus-api-key: sk-mUTK3_ww...cC3KANqe (length=98, limpio)
Response: HTTP 401 {"error":{"code":"unauthenticated","message":"invalid api key"}}
```

Posibles causas:
1. Token revocado en Manus UI
2. Token expirado (TTL alcanzado)
3. Token nunca fue válido (capturado mal en origen, hace meses)
4. Token pertenece a una cuenta diferente que la esperada

---

## Acción requerida (Alfredo, ~2 minutos)

1. Abrir https://manus.im/settings/api-keys logueado con cuenta Google `alfredogl1@hotmail.com`
2. Verificar si existe API key activa:
   - **Si existe:** copiarla con cuidado (sin espacios ni newlines del clipboard) y pasarla al hilo Ejecutor 1
   - **Si no existe o está revocada:** crear nueva API key, copiarla limpia, pasarla al hilo Ejecutor 1
3. Confirmar al hilo: "Aquí está el token Google nuevo: `sk-...`"

**Recomendación:** Pegar el token primero en un editor de texto plano (TextEdit en Plain Text mode, no Rich Text) para verificar que sea exactamente una sola línea sin whitespace antes de compartirlo.

---

## Acción del hilo Ejecutor 1 al recibir token

```bash
# Validación previa (paranoia anti-autoboicot)
python3 -c "
t = 'sk-NUEVO_TOKEN_AQUI'
assert t == t.strip(), 'Token tiene whitespace'
assert len(t) >= 80, f'Token sospechosamente corto: {len(t)}'
print(f'Token OK: length={len(t)}')
"

# Set en Railway
railway variables --service el-monstruo-kernel \
  --skip-deploys \
  --set "MANUS_API_KEY_GOOGLE=sk-NUEVO_TOKEN_AQUI"

# Smoke test binario
curl -sS -X GET https://api.manus.ai/v2/skill.list \
  -H "x-manus-api-key: sk-NUEVO_TOKEN_AQUI" | python3 -m json.tool

# Si HTTP 200 → declarar bridge Google funcional + cerrar ticket
# Si HTTP 401 → escalar (puede ser bug de la UI Manus o cuenta)
```

---

## Criterio de cierre

Ticket se cierra cuando:
- ✅ Token nuevo seteado en Railway sin whitespace
- ✅ `GET /v2/skill.list` con cuenta Google devuelve HTTP 200 + array de skills
- ✅ `bridge/credentials_inventory.md` actualizado con `last_rotated_at: 2026-05-12` + cuenta dueña confirmada
- ✅ Bridge `manus_to_cowork_TOKENS_BRIDGE_FIX_FINAL_2026_05_12.md` actualizado con sección "Cierre Google verde"

---

## Referencias

- Bridge principal: `bridge/manus_to_cowork_TOKENS_BRIDGE_FIX_FINAL_2026_05_12.md`
- Inventario credenciales: `bridge/credentials_inventory.md`
- DSC firmado en este sprint: DSC-S-009 (defensive .strip() en lectura env vars)
- Skill oficial Manus API: `skills/manus-api/SKILL.md`
