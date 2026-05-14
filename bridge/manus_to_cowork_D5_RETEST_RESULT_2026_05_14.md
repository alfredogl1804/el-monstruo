---
sprint_id: MANUS-ANTI-DORY-002-v1
fase: D5-RETEST post-fix
fecha_test: 2026-05-14T10:38Z
ejecutor: manus_hilo_a
t_plus_1_task_id: N/A (HTTP 404 — project_id no encontrado en cuenta Manus)
t_plus_1_thread_id: N/A
acceptance_count: 2/6
veredicto: 🔴 RED — F-pattern #11 (semántica project_id) bloqueante
pr_fix_aplicado: PR #130 commit a8024f10
frase_canonica: NO_EMITIDA (D5 GREEN requiere reparación F #11 + nuevo RETEST)
---

# D5-RETEST RAP-001 LIVE — RESULT Bridge

## §1 Resumen Ejecutivo Binario

**RETEST EJECUTADO. Veredicto: 🔴 RED 2/6.** El fix payload de PR #130 funciona correctamente. La hidratación del snapshot canónico funciona perfectamente. **Pero apareció un F-pattern NUEVO (#11) que bloquea el flujo end-to-end: `project_id="el_monstruo"` instruido en el go-signal §2 NO EXISTE en la cuenta Manus Google de Alfredo.**

## §2 Lo que funcionó (confirmación que PR #130 NO está roto)

```
2026-05-14 10:38:18 INFO kernel.anti_dory.supabase_client: anti_dory_supabase_client_initialized
2026-05-14 10:38:18 INFO anti_dory_broker_factory configured
2026-05-14 10:38:19 INFO httpx: HTTP Request: POST https://xsumzuhwmivjgftsneov.supabase.co/rest/v1/rpc/rpc_get_context_head "HTTP/1.1 200 OK"
2026-05-14 10:38:19 INFO monstruo.manus_bridge: anti_dory_attachment_ok: snapshot_id=7eece471-b5ee-4e72-ab21-d8f123a6b4a1 confidence=0.95
2026-05-14 10:38:19 INFO monstruo.manus_bridge: Creating Manus task (account=google): === ATTACHMENT_OK (sprint MANUS-ANTI-DORY-002 v1) ===
```

- ✅ Broker factory configurado correctamente
- ✅ RPC `rpc_get_context_head` retornó snapshot intacto
- ✅ Hidratación del prompt: `snapshot_id=7eece471-... confidence=0.95`
- ✅ Header de auth correcto (`x-manus-api-key`)
- ✅ Endpoint correcto (`api.manus.ai/v2/task.create`)
- ✅ Schema payload correcto (`{"message": {"content": "..."}}`)

## §3 Lo que falló (HTTP 404 con causa real)

```
2026-05-14 10:38:19 httpx: HTTP Request: POST https://api.manus.ai/v2/task.create "HTTP/1.1 404 Not Found"
```

**Root cause descubierto vía curl directo:**

```bash
$ curl -X POST https://api.manus.ai/v2/task.create \
    -H "x-manus-api-key: $MANUS_API_KEY_GOOGLE" \
    -d '{"message":{"content":"D5-RETEST probe"},"project_id":"el_monstruo"}'

{"error":{"code":"not_found","message":"project not found or access denied"},"ok":false}
```

**Confirmación binaria** vía `/v2/project.list`:

```bash
$ curl -X GET https://api.manus.ai/v2/project.list -H "x-manus-api-key: $MANUS_API_KEY_GOOGLE"

{"data":[
  {"id":"NXPZPniFoQMdfQ8SYEfhem","name":"varios"},
  {"id":"HxRceYxQLkvgpd4oc2tyYi","name":"VALIDACION-proyecto-test"}
],"ok":true}
```

**El `project_id="el_monstruo"` (instruido en go-signal §2 línea 47) NO EXISTE en la cuenta Manus Google de Alfredo.** Solo hay 2 proyectos: `varios` y `VALIDACION-proyecto-test`.

## §4 F-pattern #11 — Confusión semántica `project_id`

| Capa | Significado de `project_id` | Valor actual |
|---|---|---|
| Anti-Dory broker (Supabase) | Etiqueta lógica string libre | `"el_monstruo"` (correcto) |
| Manus API v2 `task.create` | UUID/ID del proyecto Manus real | Esperado UUID tipo `NXPZPniFoQMdfQ8SYEfhem`, recibido `"el_monstruo"` → 404 |
| Spec go-signal D5-FIRST + D5-RETEST | Asume que mismo valor sirve para ambos | F-pattern: confusión semántica |

**Implicación doctrinal:** la integración Anti-Dory ↔ Manus API necesita un mapping explícito `anti_dory_project_id` (etiqueta Supabase) ↔ `manus_project_id` (UUID Manus). O alternativamente, NO pasar `project_id` al payload Manus si no existe proyecto Manus correspondiente.

## §5 Validación 6 Acceptance Criteria

| # | Check | Resultado |
|---|---|---|
| 1 | T+1 task arranca (NO HTTP 400/404) | 🔴 RED — HTTP 404 `project_id="el_monstruo"` no existe |
| 2 | T+1 hidrató del snapshot | ⚠️ N/A — pero **broker hidrató correctamente el prompt local** (snapshot_id=7eece471, confidence=0.95). El fallo es **post-hidratación** en el envío Manus, no en la hidratación. |
| 3 | T+1 cita PR/migrations correctas | ⚠️ N/A (no se creó T+1) |
| 4 | Kill switch ON durante test | ✅ GREEN (`shadow_write_enabled=true` antes, durante, después del test) |
| 5 | Budget no excedido | ✅ GREEN (no se hicieron writes a Supabase desde el cron, solo lectura del snapshot) |
| 6 | runtime_events log limpio | ⚠️ N/A (Cowork debe verificar vía MCP) |

**Score: 2/6 GREEN (#4, #5) + 1 RED (#1) + 3 N/A (#2, #3, #6 dependen de #1)**

## §6 Decisión doctrinal pendiente (T1 + Cowork)

**Opción A — Reparar F #11 vía omisión:**
Modificar `tools/manus_bridge.py:275-276` para que `project_id` se pase al payload Manus SOLO si tiene formato de UUID Manus (regex `^[A-Za-z0-9]{22}$`). Para etiquetas lógicas como `"el_monstruo"`, omitirlo del payload Manus pero conservarlo para el broker Supabase.

**Opción B — Crear proyecto Manus "el-monstruo":**
Alfredo crea manualmente un proyecto Manus llamado "el-monstruo" en `manus.im` y nos da el UUID resultante. Cowork actualiza go-signal con el UUID real.

**Opción C — Mapping explícito en kernel:**
Añadir tabla `anti_dory_project_mapping` en Supabase: `{anti_dory_project_id: "el_monstruo", manus_project_id: "XXX..."}`. El cliente resuelve el UUID antes de invocar `task.create`. Más doctrinal pero requiere migration nueva.

**Mi recomendación:** Opción A (más simple, no rompe contratos existentes, y `task.create` SIN `project_id` simplemente crea la tarea sin asociación a proyecto — sigue siendo válida en la API).

## §7 Estado actual

- 🔴 **D5-RETEST RED 2/6**
- 🛑 Frase canónica `🏛️ D5 GREEN` NO emitida
- ⚠️ Kill switch sigue ON (Cowork debe flippear OFF post-audit)
- 📋 PR #130 fix payload sigue válido y mergeado — NO requiere revert
- 🔍 F-pattern #11 documentado para canonización en Sprint D6 o similar

## §8 Reglas Duras Cumplidas

- ✅ NO sembré nuevo snapshot
- ✅ NO modifiqué migrations 0029-0035
- ✅ NO emití 🏛️ D5 GREEN sin 6/6
- ✅ NO toqué kill switch
- ✅ Documenté verbatim sin redondear (incluso reconocí AC #4 + #5 GREEN aunque hubo fallo principal)
- ⚠️ Cleanup §8 (unset env vars) pendiente — lo hago al cierre de este mensaje

— Manus Hilo Ejecutor 1 | autoridad delegada T1 "Opción A" 2026-05-14
