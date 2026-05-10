# Embrión — Write Policy con HITL real

> Sprint EMBRION-NEEDS-001, Tarea 3.
> PR: ver historial de `sprint/embrion-needs-001-task-3-write-policy`.
> Origen: `bridge/sprints_propuestos/sprint_EMBRION_NEEDS_001.md`.

## Qué es

Antes de Tarea 3, cualquier escritura del embrión (commit a repo, escritura a
una tabla productiva, llamada externa a una API que cuesta dinero) se ejecutaba
automáticamente al final del `_think()`. Esto cerraba el riesgo: una alucinación
del modelo podía mutar producción.

A partir de la Tarea 3, esas escrituras pasan por una **cola de proposals** que
requiere **aprobación humana** antes de ejecutarse.

```
embrion._think()
    └─ propose() ─────────► tabla embrion_write_proposals (status=pending)
                            │
                            └─ notify_hitl() ─► insert a embrion_memoria
                                                (importancia=10, Cowork lo lee)
                                                │
Alfredo aprueba ◄───────────────────────────────┘
    └─ POST /v1/embrion/approve/{id} ────► status=approved
                                           │
Worker (cron / loop) ──────────────────────┘
    └─ execute_next() ────► status=executing → executed | failed
```

## Estados de una proposal

| Estado      | Descripción                                                                  |
|-------------|------------------------------------------------------------------------------|
| `pending`   | Recién creada. Espera aprobación humana. Default TTL 24h.                    |
| `approved`  | Humano aprobó. El worker la tomará en el siguiente ciclo.                    |
| `rejected`  | Humano rechazó con razón. Inmutable.                                         |
| `expired`   | Pasó el TTL sin decisión. El expirator la marca con approved_by=`system_expirator`. |
| `executing` | Worker tomó el lock optimista y está corriendo el executor_fn.                |
| `executed`  | Ejecución exitosa. result_json contiene la salida.                           |
| `failed`    | Ejecución falló. result_json.error contiene el motivo.                       |

## Tipos de proposal

- `code_commit` — commit a un repo Git. Payload típico: `{repo, branch, files, message}`.
- `db_write` — INSERT/UPDATE/DELETE en una tabla productiva.
- `external_api_call` — llamada a una API externa (OpenAI, Telegram, etc).
- `other` — escape hatch para casos no previstos.

## Niveles de riesgo

`low`, `medium`, `high`, `critical`. El embrión los asigna heurísticamente; el
HITL puede usarlos para priorizar la cola visualmente. **No bloquean nada por sí
solos** (todo `pending` requiere aprobación humana).

## Endpoints HTTP

Todos bajo el prefix `/v1/embrion` del kernel.

### `POST /v1/embrion/propose`
Body:
```json
{
  "proposal_type": "db_write",
  "summary": "Insertar registro en pagos_clientes",
  "payload": {"table": "pagos_clientes", "row": {...}},
  "proposed_by": "embrion_loop",
  "cycle_id": 12345,
  "risk_level": "high",
  "expires_in_hours": 24
}
```
Respuesta (201 si nueva, 200 si idempotency hit):
```json
{
  "proposal_id": "uuid",
  "created": true,
  "status": "pending",
  "expires_at": "2026-05-11T03:00:00+00:00",
  "summary": "Insertar registro en pagos_clientes",
  "risk_level": "high"
}
```
**Idempotencia**: el `idempotency_key` se calcula como
`sha256(proposal_type + json.dumps(payload, sort_keys=True))`. Si dos llamadas
caen con el mismo key, la segunda devuelve la existente (`created: false`) sin
duplicar.

### `POST /v1/embrion/approve/{proposal_id}`
Body:
```json
{ "approved_by": "alfredo", "notes": "OK, payload validado" }
```
Respuesta:
```json
{ "proposal_id": "uuid", "status": "approved", "approved_by": "alfredo", "approved_at": "..." }
```
Errores:
- `404` si la proposal no existe.
- `409` si la proposal no está en `pending` (ya fue aprobada/rechazada/expirada).

### `POST /v1/embrion/reject/{proposal_id}`
Body:
```json
{ "approved_by": "alfredo", "reason": "Payload contiene un campo prohibido" }
```
Mismo manejo de errores que `approve`.

### `GET /v1/embrion/proposals?status=pending&limit=20`
Query params:
- `status`: `pending` (default), `approved`, `rejected`, `expired`, `executed`, `failed`, `all`
- `limit`: 1–200 (default 20)

`pending` ya filtra por `expires_at >= now` (no muestra expiradas todavía no marcadas).

## Cómo aprobar manualmente desde el shell

```bash
export RAILWAY_URL="https://el-monstruo-kernel-production.up.railway.app"

# Listar pendientes
curl -s "$RAILWAY_URL/v1/embrion/proposals?status=pending" | jq .

# Aprobar una (substituir UUID)
curl -s -X POST "$RAILWAY_URL/v1/embrion/approve/<UUID>" \
  -H "Content-Type: application/json" \
  -d '{"approved_by":"alfredo","notes":"validado manualmente"}' | jq .

# Rechazar una
curl -s -X POST "$RAILWAY_URL/v1/embrion/reject/<UUID>" \
  -H "Content-Type: application/json" \
  -d '{"approved_by":"alfredo","reason":"payload con campo prohibido"}' | jq .
```

## Notificación HITL — canales disponibles

| Canal             | Estado    | Descripción                                                                |
|-------------------|-----------|----------------------------------------------------------------------------|
| `cowork_bridge`   | **Activo** | Insert a `embrion_memoria` con `importancia=10`. Cowork lo lee del MCP de Supabase y lo presenta a Alfredo. |
| `telegram`        | Pendiente | Reservado para Tarea 4 (Bot Telegram reparado).                            |

Configuración: env var `EMBRION_HITL_CHANNEL` (default `cowork_bridge`).

## Expiración (TTL)

- Default 24 horas (env `EMBRION_PROPOSAL_TTL_HOURS`).
- El expirator (`expire_old`) corre como housekeeping (puede llamarse desde el
  loop principal o un cron separado). Marca como `expired` toda proposal pending
  cuyo `expires_at` < `now`.
- `expire_old(threshold_hours=N)` ignora `expires_at` y usa `created_at + N`
  como cutoff (útil para forzar limpieza por nueva política).

## Worker de ejecución

`embrion_write_policy.execute_next(client, executor, executor_fn=...)` toma la
siguiente proposal `approved` (FIFO por `approved_at`), aplica un **lock
optimista** (`UPDATE ... WHERE approval_status='approved'` → si no afecta filas,
otro worker la tomó primero), corre `executor_fn(proposal)` y persiste el
resultado.

`executor_fn` debe retornar un `ExecutionResult(proposal_id, success, result, error)`.
Si lanza una excepción, se captura y la proposal queda `failed` con
`result_json.error`.

Ejemplo de invocación desde un script o el embrion_loop:
```python
from kernel import embrion_write_policy as wp

def my_executor(proposal):
    payload = proposal["payload_json"]
    if proposal["proposal_type"] == "db_write":
        # ejecutar el write
        return wp.ExecutionResult(proposal_id=proposal["id"], success=True, result={"affected": 1})
    raise ValueError(f"tipo no soportado: {proposal['proposal_type']}")

client = wp._get_supabase_client()
result = wp.execute_next(client, executor="cron-worker", executor_fn=my_executor)
```

## Migración (DB)

Aplicada en producción: `migrations/sql/0004_embrion_write_proposals.sql`.

Tabla `embrion_write_proposals`:
- 22 columnas, 6 índices (PK + UNIQUE idempotency_key + 4 funcionales)
- 1 trigger `updated_at` automático
- CHECK constraints en `proposal_type`, `risk_level`, `approval_status`

## Variables de entorno

| Variable                      | Default            | Uso                                              |
|-------------------------------|--------------------|--------------------------------------------------|
| `EMBRION_PROPOSAL_TTL_HOURS`  | `24`               | TTL por defecto al crear una proposal sin TTL.   |
| `EMBRION_HITL_CHANNEL`        | `cowork_bridge`    | Canal de notificación al humano.                 |
| `SUPABASE_SERVICE_KEY`        | (Railway)          | Acceso a la DB.                                   |
| `SUPABASE_URL`                | xsumzuhwmivjgftsneov.supabase.co | Endpoint Supabase.                  |

## Operativa Cowork — ciclo de aprobación

Cuando aparezca una memoria con `metadata.kind = "hitl_proposal_pending"`:
1. Cowork lee el `proposal_id` y muestra el resumen + nivel de riesgo + payload.
2. Alfredo decide: aprobar, rechazar (con razón) o ignorar (expirará en 24h).
3. Cowork ejecuta el endpoint correspondiente vía MCP HTTP.
4. El worker de ejecución (cuando esté cableado en `embrion_loop` en una tarea
   futura, o como cron separado) tomará la `approved` y la procesará.

## Qué viene después

- **Tarea 4 — Bot Telegram reparado**: añade canal `telegram` a `notify_hitl`,
  para que Alfredo reciba la notificación en el celular sin abrir Cowork.
- **Cableado en `embrion_loop._think()`**: redirigir las escrituras directas
  actuales (si las hay) a `propose()`. Hoy, `propose()` está disponible pero
  no se invoca automáticamente — es un contrato listo para que el embrión lo
  use cuando se identifique una escritura sensible.
- **Worker como cron Railway**: agregar un job recurrente que corra
  `expire_old()` + `execute_next()` cada N segundos, independiente del loop
  principal (resiliencia: el worker ejecuta aunque el loop esté caído).

## Tests

`tests/test_embrion_write_policy.py` — 36 tests, todos verdes (0.06s):
- 5 validación de inputs
- 4 idempotency
- 7 approve/reject (incluye race conditions por status)
- 1 list_pending con filtro de expiración
- 4 expire_old (incluye timeout E2E con `expires_in_hours=0`)
- 7 execute_next (happy path, error path, lock perdido, FIFO)
- 4 notify_hitl (cowork_bridge, telegram pendiente, canal inválido)
- 3 E2E completos (approve, reject, timeout)
- 2 helpers (get_pending_count, get_proposal)

Estrategia: cliente in-memory `FakeClient` que reimplementa la firma
PostgREST mínima (eq, gte, lte, in, order, limit). Sin red, deterministas.
