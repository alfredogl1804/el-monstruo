# Runbook: Rotación de OPENAI_API_KEY

**Credencial**: `OPENAI_API_KEY` (formato `sk-proj-*` o `sk-*`)
**Ubicación primaria**: Railway env vars del servicio `el-monstruo-kernel`
**Frecuencia objetivo**: 30 días (alta frecuencia debido a riesgo de costo por abuso)
**Riesgo si comprometida**: Alto (gasto incontrolado en tokens GPT, exposición de fine-tunes propietarios, acceso a Assistants API con state)
**Tiempo estimado de rotación**: 10 minutos
**Responsable**: Alfredo
**Sprint origen**: S-003.A
**Referencias**: DSC-S-001, DSC-S-008

---

## Cuándo rotar

La rotación es obligatoria cuando ocurre cualquiera de las siguientes condiciones: la credencial cumple 30 días desde su última rotación, OpenAI dashboard muestra usage anómalo (spike de tokens, requests desde IPs desconocidas), facturación mensual supera el budget objetivo en >20% sin causa identificable, hay sospecha de exposición, o el workflow CI `credentials-rotation-reminder` abre un issue.

## Pre-requisitos

Acceso a la consola de OpenAI (https://platform.openai.com) con la cuenta organizacional del proyecto. Permisos de admin en la organización para crear y revocar API keys. Acceso a Railway dashboard. Smoke test del kernel y test mínimo de embedding/chat completions (`scripts/_smoke_test_openai.py` si existe, o `curl -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models`).

## Pasos de ejecución

### Paso 1 — Generar la nueva API key

Navegar a https://platform.openai.com/api-keys. Click "Create new secret key". Configurar:

- **Name**: `el-monstruo-kernel-2026-XX-XX` (incluir fecha para trazabilidad)
- **Project**: seleccionar el project asociado a El Monstruo
- **Permissions**: Restricted, con sólo los scopes necesarios (`/v1/chat/completions`, `/v1/embeddings`, `/v1/responses`, etc.). Evitar All permissions.

Click "Create secret key". OpenAI mostrará la key una sola vez con formato `sk-proj-*`. **Copiar al portapapeles**, no cerrar la pestaña hasta confirmar Paso 3.

### Paso 2 — Actualizar la variable en Railway

```bash
cd ~/el-monstruo
railway variables set OPENAI_API_KEY="<paste-new-key-here>" --service el-monstruo-kernel
```

Confirmar el redeploy automático:

```bash
railway logs --service el-monstruo-kernel 2>&1 | head -20
```

### Paso 3 — Verificar funcionamiento

Esperar 60 segundos. Probar un endpoint del kernel que use OpenAI:

```bash
URL="https://el-monstruo-kernel-production.up.railway.app"
KEY=$(railway variables --service el-monstruo-kernel --kv 2>/dev/null | grep "^MONSTRUO_API_KEY=" | cut -d'=' -f2-)
curl -sS -X POST -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"prompt": "ping", "max_tokens": 5}' \
  "$URL/v1/llm/test" | head -5
```

(Si no existe `/v1/llm/test`, usar cualquier endpoint que invoque OpenAI internamente y verificar logs.)

Esperado: respuesta válida sin error 401. Si falla, ejecutar Paso 6 (rollback).

### Paso 4 — Sincronizar otros storages (si aplica)

Si la key también vive en GitHub Secrets, Vercel env vars, o el `.env` local del Mac, actualizar todos los storages:

```bash
# GitHub Secrets
echo "<paste-new-key>" | gh secret set OPENAI_API_KEY

# Vercel (si aplica)
vercel env rm OPENAI_API_KEY production
vercel env add OPENAI_API_KEY production

# .env local
sed -i.bak "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=<paste>|" ~/.env
```

### Paso 5 — Revocar la key antigua

Volver a https://platform.openai.com/api-keys. Localizar la key antigua. Click el icono de menú → "Revoke key". Confirmar. Esperar 5 minutos antes de cerrar la sesión para asegurar que la revocación se propaga.

### Paso 6 — Rollback (solo si Paso 3 falla)

```bash
railway variables set OPENAI_API_KEY="<old-key>" --service el-monstruo-kernel
```

Esto requiere haber anotado la key antigua en Bitwarden antes del Paso 1.

### Paso 7 — Documentar la rotación

Actualizar `bridge/credentials_inventory.md` línea de `OPENAI_API_KEY` con `last_rotated_at: YYYY-MM-DD`. Agregar entrada a `bridge/rotation_log.md`. Commit y push.

## Monitoreo post-rotación

Durante las 48 horas siguientes, revisar el dashboard de OpenAI (https://platform.openai.com/usage) para confirmar que el patrón de consumo se mantiene normal. Si aparece consumo desde la key antigua, identificar el cliente legacy y actualizarlo, o documentar el residual como aceptable hasta su decommission.

## Errores comunes

Si OpenAI rechaza la nueva key con `401 Invalid API key`, esperar 30-60 segundos: la propagación interna no es instantánea. Si el kernel devuelve `429 Rate limit exceeded` post-rotación, verificar que el rate limit del project no haya sido reducido. Si Railway no redeploya, ejecutar `railway redeploy --service el-monstruo-kernel` manualmente.

## Consideraciones de costo

OpenAI no cobra por crear/revocar keys, pero un periodo de doble facturación (key vieja + key nueva) puede ocurrir si ambas están activas simultáneamente y reciben requests. Mantener el solapamiento <5 minutos minimiza este riesgo.

---

**Última actualización**: 2026-05-10 (creación del runbook, Sprint S-003.A)
