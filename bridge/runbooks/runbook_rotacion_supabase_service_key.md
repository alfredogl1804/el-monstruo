# Runbook: Rotación de SUPABASE_SERVICE_KEY

**Credencial**: `SUPABASE_SERVICE_KEY` (formato `sb_secret_*`)
**Ubicación primaria**: Railway env vars del servicio `el-monstruo-kernel`
**Frecuencia objetivo**: 90 días
**Riesgo si comprometida**: Crítico (acceso pleno a la base de datos de Supabase, bypass de RLS)
**Tiempo estimado de rotación**: 15 minutos
**Responsable**: Alfredo
**Sprint origen**: S-003.A
**Referencias**: DSC-S-001, DSC-S-007, DSC-S-008

---

## Cuándo rotar

La rotación es obligatoria cuando ocurre cualquiera de las siguientes condiciones: la credencial actual cumple 90 días desde su última rotación documentada, hay sospecha confirmada de exposición (commit accidental, log expuesto, screenshot compartido), un colaborador con acceso al dashboard de Supabase deja el proyecto, o el workflow CI `credentials-rotation-reminder` abre un issue automático.

## Pre-requisitos

Acceso al dashboard de Supabase con permisos de `Owner` del proyecto `xsumzuhwmivjgftsneov`. Acceso a Railway dashboard con permisos sobre el servicio `el-monstruo-kernel`. Capacidad de ejecutar `gh secret set` localmente si la credencial también está en GitHub Secrets. Smoke test del kernel funcional (`scripts/_smoke_test_kernel.sh`).

## Pasos de ejecución

### Paso 1 — Generar la nueva service_role key

Navegar a https://supabase.com/dashboard/project/xsumzuhwmivjgftsneov/settings/api en el navegador. En la sección "Project API keys", localizar la `service_role` key actual. Click en el botón "Reveal new key" o "Rotate". Supabase generará una nueva key con formato `sb_secret_*`. **Copiar la nueva key al portapapeles**, no cerrar la pestaña hasta confirmar que el nuevo valor está aplicado en Railway. **No pegarla en chat, archivos de texto, ni capturas de pantalla.**

### Paso 2 — Actualizar la variable en Railway

Ejecutar en terminal local (no en chat ni en Cursor con AI activo):

```bash
cd ~/el-monstruo
railway variables set SUPABASE_SERVICE_KEY="<paste-new-key-here>" --service el-monstruo-kernel
```

Railway disparará automáticamente un redeploy del servicio. El downtime esperado es de 30-60 segundos. Confirmar el redeploy:

```bash
railway logs --service el-monstruo-kernel | head -20
```

### Paso 3 — Verificar funcionamiento

Esperar 60 segundos para que el redeploy complete. Ejecutar smoke test:

```bash
URL="https://el-monstruo-kernel-production.up.railway.app"
KEY=$(railway variables --service el-monstruo-kernel --kv 2>/dev/null | grep "^MONSTRUO_API_KEY=" | cut -d'=' -f2-)
for ep in /v1/stats /v1/memory/status /v1/embrion/estado /v1/error-memory/recent; do
  C=$(curl -sS -o /dev/null -w "%{http_code}" -H "X-API-Key: $KEY" "$URL$ep")
  printf "%-30s %s\n" "$ep" "$C"
done
```

Esperado: los 4 endpoints responden `200`. Si alguno responde `500` o `503`, ejecutar inmediatamente el rollback (Paso 6).

### Paso 4 — Sincronizar GitHub Secrets (si aplica)

Si la credencial también vive en GitHub Secrets (verificar con `gh secret list`), actualizarla:

```bash
echo "<paste-new-key>" | gh secret set SUPABASE_SERVICE_KEY
```

Disparar manualmente el workflow afectado para validar:

```bash
gh workflow list
gh workflow run "<workflow-name>"
gh run list --limit 1
```

### Paso 5 — Revocar la key antigua

En el mismo dashboard de Supabase (paso 1), localizar la key anterior y click "Revoke". Confirmar la revocación. **Esta acción es irreversible**: una vez revocada, cualquier sistema que aún use la key antigua dejará de funcionar inmediatamente. Por eso el orden importa: nueva → verificar → revocar antigua.

### Paso 6 — Rollback (solo si Paso 3 falla)

Si el smoke test del Paso 3 reporta errores, ejecutar inmediatamente:

```bash
railway variables set SUPABASE_SERVICE_KEY="<old-key>" --service el-monstruo-kernel
```

Esto requiere haber guardado la key antigua **antes** del Paso 1. Recomendación: anotar la key antigua en Bitwarden con nombre `Supabase service_role - PRE rotation YYYY-MM-DD` antes de iniciar el proceso, y borrar esta entrada 24 horas después de confirmar que la rotación fue exitosa.

### Paso 7 — Documentar la rotación

Editar `bridge/credentials_inventory.md` y actualizar la fila `SUPABASE_SERVICE_KEY` con `last_rotated_at: YYYY-MM-DD`. Agregar entrada al archivo `bridge/rotation_log.md` (crear si no existe) con:

```markdown
## Rotación 2026-XX-XX — SUPABASE_SERVICE_KEY

- Razón: <programada / sospecha exposición / offboarding colaborador>
- Ejecutado por: <quien>
- Resultado smoke test: <PASS/FAIL/PARTIAL>
- Tiempo total: <minutos>
- Notas: <relevantes>
```

Commit y push:

```bash
cd ~/el-monstruo
git add bridge/credentials_inventory.md bridge/rotation_log.md
git commit -m "chore: rotación SUPABASE_SERVICE_KEY YYYY-MM-DD"
git push
```

## Validación post-rotación

24 horas después de la rotación, verificar logs del kernel para confirmar que ningún cliente legacy intenta usar la key antigua. Si aparecen errores `401 Unauthorized` con la key antigua, identificar el cliente y actualizarlo. Borrar la entrada `Supabase service_role - PRE rotation` de Bitwarden.

## Errores comunes

Si Railway no redeploya tras `railway variables set`, ejecutar manualmente `railway redeploy --service el-monstruo-kernel`. Si Supabase no muestra el botón "Rotate", el usuario actual no tiene permisos de Owner; verificar en https://supabase.com/dashboard/org/wpgdrcvkrjnagikaezsh/team. Si la nueva key tiene formato JWT (`eyJ...`) en lugar de `sb_secret_*`, el proyecto está usando el formato legacy; consultar DSC-S-007 sobre la migración al formato nuevo.

---

**Última actualización**: 2026-05-10 (creación del runbook, Sprint S-003.A)
