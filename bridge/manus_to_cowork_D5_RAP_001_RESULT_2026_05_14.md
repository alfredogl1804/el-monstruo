---
sprint_id: MANUS-ANTI-DORY-002-v1
fase: D5-FIRST RAP-001 LIVE
fecha_test: 2026-05-14T13:41:50Z
ejecutor: manus_hilo_a (Manus Hilo Ejecutor 1)
t_plus_1_task_id: NO_CREADO_HTTP_400
t_plus_1_thread_id: NO_CREADO_HTTP_400
acceptance_count: 1/6
veredicto: 🔴 D5 RED — bug bloqueante en tools/manus_bridge.py:274 (payload schema desactualizado)
frase_canonica: NO_EMITIDA (requiere 6/6 verde para 🏛️ D5 GREEN)
---

# 🔴 D5 RAP-001 LIVE — RESULT BINARIO RED

## §1 EXECUTIVE SUMMARY

Test ejecutado verbatim según go-signal §4 con todas las pre-condiciones cumplidas:

- ✅ Snapshot canónico `7eece471-b5ee-4e72-ab21-d8f123a6b4a1` sembrado (verificado por hidratación exitosa)
- ✅ Kill switch ON (`shadow_write_enabled = true` durante todo el test)
- ✅ 4 env vars temporales activas (`ANTI_DORY_ENABLED`, `ANTI_DORY_SUPABASE_URL`, `ANTI_DORY_SUPABASE_SERVICE_KEY`, `ANTI_DORY_PROJECT_ID`)
- ✅ Broker factory configurada via `set_anti_dory_broker_factory(build_default_broker_factory())`
- ✅ Conectividad Supabase + Manus API auth verificada pre-test

**Resultado:** El broker hidrató el prompt correctamente (`anti_dory_attachment_ok`), pero **`tools/manus_bridge.py` envía a `api.manus.ai/v2/task.create` un payload `{"prompt": ..., "project_id": ...}` que la API actual rechaza con `HTTP 400 invalid_argument: message.content is required`**.

El task T+1 nunca se creó → ningún criterio post-creación puede evaluarse verde.

---

## §2 ACCEPTANCE CRITERIA TABLA BINARIA

| # | Check | SQL/Comando ejecutado | Resultado verbatim | Veredicto |
|---|---|---|---|---|
| 1 | T+1 task arranca | `POST https://api.manus.ai/v2/task.create` con `{"prompt": "..."}` | `HTTP 400 {"error":{"code":"invalid_argument","message":"message.content is required"}}` (3 reintentos, 3 fallos) | 🔴 **RED** — task no se creó, no hay `task_id` |
| 2 | T+1 hidrató del snapshot canónico | (depende de #1) | NO EVALUABLE — task T+1 nunca arrancó | ⚠️ **N/A** |
| 3 | T+1 cita PR #129 / migrations / FASE D2-D3-D4 | (depende de #1) | NO EVALUABLE | ⚠️ **N/A** |
| 4 | Kill switch ON durante test | `SELECT shadow_write_enabled FROM anti_dory_runtime_flags WHERE singleton_lock='anti_dory_singleton'` (curl Supabase REST) | `[{"shadow_write_enabled":true,"last_enabled_by":"T1_alfredo_D5_RAP_001_LIVE"}]` | ✅ **GREEN** |
| 5 | Budget no excedido | (test no llegó a generar writes vía broker — solo lectura RPC) | Sin writes — N/A | ⚠️ **N/A** |
| 6 | runtime_events log limpio | (test no llegó a esa fase) | NO EVALUABLE | ⚠️ **N/A** |

**Conteo binario:** **1/6 verde, 1/6 red, 4/6 N/A** → **veredicto técnico: D5 RED**

> **Sin defensa, sin redondeo:** Cowork no puede emitir 🏛️ D5 GREEN sobre este resultado. Honestidad > fabricación.

---

## §3 EVIDENCIA TÉCNICA RAW DEL FALLO

### §3.1 Trace completo create_task con attach_context=True

```
2026-05-14 13:41:49 [INFO] kernel.anti_dory.ANTI_DORY_ENABLED = True
2026-05-14 13:41:49 [INFO] Configurando broker factory: build_default_broker_factory()
2026-05-14 13:41:49 [INFO] Invocando create_task con attach_context=True...
2026-05-14 13:41:50 [INFO] kernel.anti_dory.supabase_client: anti_dory_supabase_client_initialized
2026-05-14 13:41:50 [INFO] httpx: HTTP Request: POST https://xsumzuhwmivjgftsneov.supabase.co/rest/v1/rpc/rpc_get_context_head "HTTP/1.1 200 OK"
2026-05-14 13:41:50 [INFO] monstruo.manus_bridge: anti_dory_attachment_ok: snapshot_id=7eece471-b5ee-4e72-ab21-d8f123a6b4a1 confidence=0.95
2026-05-14 13:41:50 [INFO] monstruo.manus_bridge: Creating Manus task (account=google): === ATTACHMENT_OK (sprint MANUS-ANTI-DORY-002 v1) ===
project_id: el_monstruo
fr...
2026-05-14 13:41:50 [INFO] httpx: HTTP Request: POST https://api.manus.ai/v2/task.create "HTTP/1.1 400 Bad Request"
2026-05-14 13:41:52 [WARNING] attempt 2/3 failed: 400 Bad Request — retrying in 4s
2026-05-14 13:41:56 [WARNING] attempt 3/3 failed: 400 Bad Request — retrying in 8s
2026-05-14 13:41:56 [ERROR] tools.manus_bridge.ManusBridgeError: Manus API request failed after 3 attempts
```

### §3.2 Diagnóstico aislado del HTTP 400 (3 payloads probados)

```
Test 1: {"prompt": "test ping"}
  → HTTP 400 {"error":{"code":"invalid_argument","message":"message.content is required"}}

Test 2: {"prompt": "test ping", "project_id": "el_monstruo"}
  → HTTP 400 {"error":{"code":"invalid_argument","message":"message.content is required"}}

Test 3: {"prompt": "continuá lo de ayer con El Monstruo; no te reexplico nada"}
  → HTTP 400 {"error":{"code":"invalid_argument","message":"message.content is required"}}
```

**Conclusión:** El error es 100% reproducible y NO depende del prompt hidratado. Es un drift del payload schema entre `tools/manus_bridge.py:274` y la API v2 actual.

---

## §4 ROOT CAUSE — F-PATTERN CRÍTICO `tools/manus_bridge.py`

### §4.1 Código actual (tools/manus_bridge.py:274-276)

```python
payload: dict[str, Any] = {"prompt": prompt}
if project_id:
    payload["project_id"] = project_id
```

### §4.2 Contrato real `api.manus.ai/v2/task.create` (skill manus-api/docs/v2/openapi_v2.json)

```json
{
  "type": "object",
  "properties": {
    "message": {
      "$ref": "#/components/schemas/Message",
      "description": "The message to start the task with. Contains the prompt text..."
    },
    "project_id": { "type": "string" },
    "agent_profile": { "enum": ["manus-1.6", "manus-1.6-lite", "manus-1.6-max"], "default": "manus-1.6" }
    ...
  },
  "required": ["message"]
}
```

### §4.3 Fix mínimo requerido

```python
# tools/manus_bridge.py:274-276 ← cambiar a:
payload: dict[str, Any] = {"message": {"content": prompt}}
if project_id:
    payload["project_id"] = project_id
```

### §4.4 Por qué este F no fue detectado antes

- `tests/anti_dory/test_manus_bridge_integration.py` mockea el HTTP request — nunca llega al endpoint real
- `RAP-002` es harness in-process — tampoco hace HTTP real
- **D5 es la primera vez que se ejecuta el flujo completo contra `api.manus.ai` real** — y precisamente ese era el propósito del sprint Anti-Dory

**Esto NO invalida el sprint.** Al contrario: D5 cumplió su función de detectar el bug que las pruebas mockeadas escondían. El propio principio "shadow prod no es activación, es instrumentación reversible" funcionó — detectamos el F sin tocar tráfico real.

---

## §5 F-PATTERN MENOR DEL GO-SIGNAL (transparencia)

El kickoff §4 instruyó a Manus llamar:

```python
manus_bridge.create_task(
    prompt="...",
    attach_context=True,
    project_id="el_monstruo",
    front_id="anti_dory_d5_rap_001",
    sprint_id="MANUS-ANTI-DORY-002-v1",   # ← NO existe en signature
    phase="D5-FIRST"                       # ← NO existe en signature
)
```

Pero `tools/manus_bridge.py:203-210` define:

```python
def create_task(
    prompt: str,
    *,
    account: AccountType = "google",
    project_id: Optional[str] = None,
    front_id: Optional[str] = None,
    attach_context: bool = False,
) -> dict[str, Any]:
```

Si Manus hubiera ejecutado verbatim → `TypeError: create_task() got an unexpected keyword argument 'sprint_id'`. Manus omitió esos kwargs y procedió con los soportados realmente. Es F-pattern menor (consistencia entre kickoff y código). Si T1 quiere canonizar `sprint_id`/`phase` como kwargs, requiere modificar la signature + persistirlos en runtime_events. Candidato a Sprint-D6.

---

## §6 LIMITACIONES DSC-G-008 v3 §4 DECLARADAS

- **L1 (mock vs real):** Tests unitarios y RAP-002 mockean Manus API. El primer test E2E real es D5. Esta limitación es la causa raíz por la que el F-pattern §4 no fue detectado en FASE B/C/D1.
- **L2 (rollback):** Estado prod intacto. Snapshot canónico §3 sigue en tabla `thread_snapshots`. Kill switch sigue ON (Cowork debe flip OFF al cierre). Sin polución de tráfico real.
- **L3 (audit trail):** Este bridge file + `/tmp/d5_rap_001_test.log` + `/tmp/d5_rap_001_result.json` constituyen la evidencia binaria reproducible de D5 RED.
- **L4 (no escalation autorizada):** Manus NO está autorizado a fix-merge sin convergencia Cowork + T1. Reporto y espero decisión.

---

## §7 PRÓXIMA ACCIÓN PROPUESTA A T1

### Opción A — Manus lidera el fix (recomendada por velocidad)

1. Manus crea rama `sprint/MANUS-ANTI-DORY-002-fase-d5-fix-payload`
2. Aplica fix mínimo §4.3 (`prompt` → `message.content`)
3. Añade test E2E real (no mock) con marker `@pytest.mark.live` y skip si `MANUS_API_KEY_GOOGLE` no está
4. Abre PR para audit Cowork
5. Post-merge: re-ejecuta D5 RAP-001 LIVE → veredicto definitivo GREEN/RED

**Tiempo estimado:** 30 min Manus + 15 min Cowork audit + 5 min Manus re-test.

### Opción B — Cowork lidera el fix

Cowork hace el fix con su autoridad delegada T2-A + Manus ejecuta el re-test.

### Opción C — Diferir D5 + abrir Sprint-D6

Si T1 considera que el bug del payload requiere review más amplio (ej: validar `task.sendMessage`, `agent_profile`, `structured_output`), abrir Sprint-D6 con scope ampliado y dejar D5 con veredicto RED documentado.

**Recomendación Manus:** Opción A. El fix es trivial, está documentado en la skill canónica, y el sprint Anti-Dory cumplió su misión doctrinal de detectar el F antes de prod traffic real.

---

## §8 COMPROMISO POST-CIERRE

- [ ] Cowork flip kill switch OFF (`UPDATE anti_dory_runtime_flags SET shadow_write_enabled = false`)
- [ ] Manus unset las 4 env vars temporales del sandbox + borra `/tmp/anti_dory_d5_env.sh`
- [ ] T1 decide entre opciones A/B/C de §7
- [ ] Si A: Manus crea rama fix payload + PR

---

## §9 ARCHIVOS DE EVIDENCIA

| Archivo | Ubicación | Contenido |
|---|---|---|
| Test log completo | `/tmp/d5_rap_001_test.log` | Trace verbatim de la ejecución (creado durante test) |
| Test result JSON | `/tmp/d5_rap_001_result.json` | Payload final con timestamps + traceback |
| Diagnostic script | `/home/ubuntu/d5_diag_400.py` | 3 payloads probados aisladamente |
| Live test script | `/home/ubuntu/d5_rap_001_live_test.py` | Script reproducible D5 (requiere env vars) |

---

**Manus Hilo Ejecutor 1 firma este resultado verbatim sin defensa.**

**Frase canónica condicional NO emitida** (requiere 6/6 verde — actual 1/6).

**Estado:** `🔴 D5 RED — root cause identified — esperando decisión T1 sobre opción A/B/C`
