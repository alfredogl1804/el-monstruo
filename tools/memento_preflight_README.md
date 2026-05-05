# Memento Preflight Library — Guía operativa

> **Capa Memoria Soberana v1.0 — Sprint Memento Bloque 4**
> Library standalone que cualquier hilo Manus puede importar para validar
> contexto contra fuentes de verdad **antes** de ejecutar operaciones críticas.

---

## ¿Qué problema resuelve?

El incidente del **2026-05-04 ("Falso Positivo TiDB")** demostró que un hilo
puede operar con contexto stale (host fantasma `gateway01` cuando la realidad
era `gateway05`) y reportar éxitos que no existen. Sin pre-flight, los errores
se descubren minutos u horas después.

La library **fuerza** la consulta al endpoint `POST /v1/memento/validate` antes
de cada operación crítica. Si el contexto declarado no coincide con la fuente
de verdad, el hilo se bloquea (modo default) y recibe un payload con la
discrepancia exacta + remediación sugerida.

---

## Instalación

La library es **standalone**: solo depende de `httpx` (≥0.24) y stdlib.

```bash
pip install httpx>=0.24
```

Luego copiá `tools/memento_preflight.py` al sandbox del hilo (o agregá al
PYTHONPATH).

---

## Configuración (variables de entorno)

| Variable | Default | Propósito |
|---|---|---|
| `MEMENTO_VALIDATOR_URL` | `https://el-monstruo-kernel-production.up.railway.app/v1/memento/validate` | Endpoint del kernel. Para tests locales: `http://localhost:8080/v1/memento/validate`. |
| `MEMENTO_API_KEY` o `MONSTRUO_API_KEY` | _(obligatorio)_ | API key. `MEMENTO_API_KEY` tiene prioridad sobre `MONSTRUO_API_KEY`. |
| `MEMENTO_AUTH_FORMAT` | `x-api-key` | `x-api-key` o `bearer`. |
| `MEMENTO_HILO_ID` | `hilo_unknown` | Identificador del hilo (queda en `memento_validations.hilo_id`). |
| `MEMENTO_TIMEOUT_SECONDS` | `5.0` | Timeout HTTP por request. |
| `MEMENTO_RETRY_ATTEMPTS` | `3` | Reintentos en caso de timeout/network/5xx. |
| `MEMENTO_RETRY_BACKOFF_BASE` | `1.0` | Base del backoff exponencial (1s, 2s, 4s). |
| `MEMENTO_FALLBACK_POLICY` | `block` | `block` (default — bloquea si endpoint no responde) o `warn` (loguea + permite). |

> **Anti-Dory:** todas las variables se leen **fresh en cada request**. Si
> rotás credenciales o cambiás `MEMENTO_VALIDATOR_URL` en runtime, no es
> necesario reiniciar el proceso.

---

## Uso 1 — Decorator (recomendado)

```python
from tools.memento_preflight import requires_memento_preflight

@requires_memento_preflight(
    operation="sql_against_production",
    context_from_kwargs=["host", "user"],  # solo estos van al validador
)
async def query_tidb(host: str, user: str, query: str):
    # Si pre-flight bloquea, este cuerpo NO se ejecuta
    # (raise MementoPreflightDiscrepancyError)
    ...
```

### Comportamiento

- Antes del cuerpo, el decorator construye `context_used = {"host": ..., "user": ...}`
  con los valores reales pasados como kwargs.
- Llama a `POST /v1/memento/validate` con `operation` + `context_used` + `hilo_id`.
- Si `proceed=True`: ejecuta el cuerpo normalmente.
- Si `proceed=False`: `raise MementoPreflightDiscrepancyError` con el detalle
  de la discrepancia accesible vía `exc.result.discrepancy`.
- Si endpoint unavailable + `MEMENTO_FALLBACK_POLICY=block`: `raise MementoPreflightUnavailableError`.
- Si endpoint unavailable + `MEMENTO_FALLBACK_POLICY=warn`: loguea y ejecuta
  el cuerpo (útil para hilos no críticos).

### Sin `context_from_kwargs`

Si NO especificás `context_from_kwargs`, el decorator infiere TODO el bound
de la función como `context_used` (excluyendo `self`/`cls` y valores
no-JSON-serializables). Útil para operaciones donde TODOS los kwargs son
relevantes:

```python
@requires_memento_preflight(operation="deploy_to_railway")
async def deploy(env_name: str, branch: str, sha: str):
    # context_used = {"env_name": ..., "branch": ..., "sha": ...}
    ...
```

### Funciones síncronas

El decorator detecta `async def` vs `def` automáticamente. Para sync corre el
cliente HTTP en un loop nuevo via `asyncio.run`. **Limitación**: no usar el
decorator sync dentro de un loop ya corriendo (FastAPI handlers, por ejemplo) —
en ese caso usar `await preflight_check_async(...)` directamente.

---

## Uso 2 — Llamada directa

```python
from tools.memento_preflight import preflight_check_async

result = await preflight_check_async(
    operation="sql_against_production",
    context_used={"host": "gateway05.us-west-2.prod.aws.tidbcloud.com", "user": "alfredo"},
    hilo_id="hilo_ejecutor",
    intent_summary="migración 018 — añadir columna activo a tabla X",
)

if not result.proceed:
    print(f"Bloqueado: {result.discrepancy}")
    print(f"Remediación: {result.remediation}")
    raise SystemExit(1)

# Proceder con la operación
```

### Sync wrapper

```python
from tools.memento_preflight import preflight_check

result = preflight_check(
    operation="sql_against_production",
    context_used={"host": "gateway05"},
    hilo_id="hilo_a",
)
```

---

## Cache local

La library mantiene un cache in-memory thread-safe con TTL (60s default).

```python
from tools.memento_preflight import get_cache

# Cache hit/miss automáticos
result = await preflight_check_async(operation="op_x", context_used={"a": 1})

# Invalidar manualmente (ej. después de rotar credenciales)
get_cache().invalidate("op_x", {"a": 1})

# Limpiar todo
get_cache().clear()
```

### Cuándo deshabilitar el cache

```python
result = await preflight_check_async(
    operation="op_x",
    context_used={"a": 1},
    use_cache=False,  # siempre llama al endpoint
)
```

Útil para:
- Operaciones idempotentes que requieren re-validación cada vez.
- Tests E2E donde querés observar cada request individualmente.

---

## Manejo de errores

| Excepción | Causa | Cómo manejar |
|---|---|---|
| `MementoPreflightConfigError` | `MONSTRUO_API_KEY`/`MEMENTO_API_KEY` no seteada o 401/403 del endpoint | Verificar env vars; arreglar y reintentar manualmente |
| `MementoPreflightDiscrepancyError` | `proceed=False` (discrepancy/unknown_operation) | Inspeccionar `exc.result.discrepancy` y `exc.result.remediation` |
| `MementoPreflightUnavailableError` | Endpoint no respondió tras todos los retries (`fallback=block`) | Verificar Railway; o usar `MEMENTO_FALLBACK_POLICY=warn` para operaciones no críticas |
| `MementoPreflightError` | 422 (request inválido) u otro error genérico | Revisar payload (especialmente `operation` y `context_used`) |

### Ejemplo

```python
from tools.memento_preflight import (
    requires_memento_preflight,
    MementoPreflightDiscrepancyError,
    MementoPreflightUnavailableError,
)

@requires_memento_preflight(operation="sql_against_production", context_from_kwargs=["host"])
async def write_to_db(host: str, payload: dict):
    ...

try:
    await write_to_db(host="gateway05", payload={"x": 1})
except MementoPreflightDiscrepancyError as e:
    logger.error("blocked", discrepancy=e.result.discrepancy, remediation=e.result.remediation)
    # Decisión: abortar el sprint, pedir al humano, o reconsultar fuente y reintentar
except MementoPreflightUnavailableError as e:
    logger.warning("preflight_endpoint_down", error=str(e))
    # Decisión: bloquear y pedir al humano, o usar fallback="warn" si la operación es de bajo riesgo
```

---

## Patrones de uso por hilo

### Hilo Ejecutor (Manus)

Operaciones críticas típicas:
- `sql_against_production` (TiDB / Supabase)
- `deploy_to_railway`
- `commit_to_main` (cuando ya esté en el catálogo)
- `enable_feature_flag_in_prod`

```python
@requires_memento_preflight(operation="deploy_to_railway")
async def deploy(env_name: str, branch: str, sha: str):
    ...
```

### Hilo Catastro

Operaciones críticas típicas:
- `migrate_supabase_schema` (cuando ya esté en el catálogo del Sprint 86 B5+)
- `bulk_upsert_catastro`

### Hilo ticketlike

Operaciones críticas típicas:
- `sql_against_production` (TiDB Cloud)
- `stripe_charge_real`

---

## Testing local sin endpoint real

Los tests del proyecto usan `http_client_factory` para inyectar un mock de
`httpx.AsyncClient`. Ejemplo mínimo:

```python
import httpx
import pytest
from tools.memento_preflight import preflight_check_async, PreflightResult

class _MockResp:
    def __init__(self, status, data): self.status_code = status; self._data = data; self.text = ""
    def json(self): return self._data

class _MockClient:
    def __init__(self, response): self._r = response; self.calls = []
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False
    async def post(self, url, json, headers, **kw):
        self.calls.append({"url": url, "json": json})
        return self._r

@pytest.mark.asyncio
async def test_my_operation(monkeypatch):
    monkeypatch.setenv("MONSTRUO_API_KEY", "test_key")
    mock = _MockClient(_MockResp(200, {"validation_id": "mv_x", "validation_status": "ok", "proceed": True}))
    result = await preflight_check_async(
        operation="my_op",
        context_used={"a": 1},
        hilo_id="test",
        http_client_factory=lambda: mock,
        use_cache=False,
    )
    assert result.proceed
```

Ver `tests/test_sprint_memento_b4.py` para 41 ejemplos cubriendo todos los casos.

---

## Bloque siguiente (B5)

El Bloque 5 del Sprint Memento migra los hilos existentes (Ejecutor, Catastro,
ticketlike) para que sus operaciones críticas usen este decorator. Ese trabajo
se hace en cada repo / sandbox, no en `el-monstruo`.

---

## Referencias

- **Spec del sprint:** `bridge/sprint_memento_preinvestigation/spec_sprint_memento.md`
- **Endpoint:** `kernel/memento_routes.py`
- **Models:** `kernel/memento/models.py`
- **Catálogo de operaciones críticas:** `kernel/memento/critical_operations.yaml` + tabla `memento_critical_operations` en Supabase
- **Tests:** `tests/test_sprint_memento_b4.py` (41 tests, 100% PASS)
- **Incidente que motivó el sprint:** "Falso Positivo TiDB" del 2026-05-04 (semilla 30 en `error_memory`)

---

**Autoría:** Hilo Manus Ejecutor · 2026-05-04 · Sprint Memento Bloque 4
