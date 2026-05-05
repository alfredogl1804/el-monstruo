# Memento — Guía Operativa (Capa Memoria Soberana v1.0)

> **Sprint Memento · Bloque 7 · 2026-05-04**
> **Audiencia:** operadores humanos del Monstruo (Alfredo, Hilo A, Hilo B) y cualquier hilo Manus que consuma `/v1/memento/*`.
> **Identidad:** este módulo es **El Guardián de la Memoria** — no un "validation service". Su trabajo es impedir que un hilo con contexto compactado destruya producción.

---

## 1. Para qué sirve Memento

El Síndrome Dory ya cobró tres víctimas reproducibles el 2026-05-04: el cluster fantasma `gateway01.us-east-1.prod.aws.tidbcloud.com`, el Radar legacy y la "migration pendiente". En los tres casos un hilo Manus operó con contexto heredado de una compactación previa **sin verificar contra evidencia forense**. Memento formaliza la verificación: ningún catálogo, ninguna heurística manual humana — código auditable que vive en el kernel.

| Capa Memento | Qué responde | Endpoint |
|---|---|---|
| **Validator** (B2) | "¿El contexto que declarás coincide con la fuente de verdad actual?" | `POST /v1/memento/validate` |
| **ContaminationDetector** (B6) | "¿Hay señales forenses de que tu contexto es heredado?" | `POST /v1/memento/validate` (adjunto) |
| **Catálogo en caliente** (B7) | "Cambiaron las operaciones críticas, recargá sin reiniciar." | `POST /v1/memento/admin/reload` |
| **Visibilidad humana** (B7) | "Mostrame qué pasó las últimas 24h." | `GET /v1/memento/admin/dashboard` |

Memento opera **en modo sombra (shadow mode v1.0)** para `contamination_warning`: detecta y persiste, **no bloquea `proceed`**. La discrepancia dura del Validator sí bloquea (`proceed=false`).

---

## 2. Endpoints — contrato resumido

Todos requieren `X-API-Key: $MONSTRUO_API_KEY`. Sin la cabecera o con valor inválido devuelven `401 memento_api_key_invalid`.

### `POST /v1/memento/validate`

Pre-flight obligatorio antes de cualquier operación marcada como `requires_validation=true` en el catálogo.

```bash
curl -sS -X POST "$KERNEL_URL/v1/memento/validate" \
  -H "X-API-Key: $MONSTRUO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "hilo_id": "hilo_manus_ticketlike",
    "operation": "sql_against_production",
    "context_used": {
      "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
      "user": "37Hy7adB53QmFW4.root",
      "credential_hash_first_8": "4N6caSwp"
    },
    "intent_summary": "Run migration 042 on prod"
  }'
```

Respuesta resumida:

| Campo | Significado operativo |
|---|---|
| `validation_status` | `ok` · `discrepancy_detected` · `unknown_operation` · `source_unavailable` |
| `proceed` | `true` solo si `validation_status == ok` |
| `discrepancy.field` | Campo concreto que no matchea (`host`, `user`, `credential_hash_first_8`) |
| `contamination_warning` | `true` si el detector encontró ≥1 finding (no bloquea) |
| `contamination_findings` | Lista de findings con `rule_id`, `severity`, `evidence`, `recommendation` |
| `persistence_failed` | `true` si Supabase rechazó el insert (la response sigue siendo válida) |

**Regla operativa para hilos:** si `proceed=false`, NO ejecutar la operación. Si `contamination_warning=true` y `severity=HIGH`, **detenerse y avisar al operador humano** aunque `proceed=true` (estamos en shadow mode pero la señal es real).

### `POST /v1/memento/admin/reload`

Recarga atómica del catálogo (`memento_critical_operations` + `memento_sources_of_truth`) desde Supabase, con fallback a `kernel/memento/critical_operations.yaml` si Supabase falla. Thread-safe vía `asyncio.Lock` por app.

```bash
curl -sS -X POST "$KERNEL_URL/v1/memento/admin/reload" \
  -H "X-API-Key: $MONSTRUO_API_KEY"
```

Códigos esperados: `200 reloaded` · `409 memento_reload_already_in_progress` · `503 memento_validator_not_initialized` o `memento_reload_empty_catalog` · `504 memento_reload_supabase_timeout` (>5s).

**Cuándo usar:** después de insertar/modificar filas en `memento_critical_operations` o `memento_sources_of_truth`, o cuando se actualiza el YAML local sin redeploy.

### `GET /v1/memento/admin/dashboard`

Métricas operativas de las últimas 24h. JSON por defecto; HTML brutalista (graphite + naranja forja) si `Accept: text/html`.

```bash
# JSON
curl -sS "$KERNEL_URL/v1/memento/admin/dashboard" -H "X-API-Key: $MONSTRUO_API_KEY"

# HTML (abrir en navegador local con un puerto temporal)
curl -sS "$KERNEL_URL/v1/memento/admin/dashboard" \
  -H "X-API-Key: $MONSTRUO_API_KEY" \
  -H "Accept: text/html" > /tmp/memento_dashboard.html && open /tmp/memento_dashboard.html
```

Bloques que entrega: `health`, `window`, `validations_last_24h` (con `ok_rate`, `discrepancy_rate`), `contamination_last_24h` (con breakdown por `rule_id` H1/H2/H3 y por `severity` HIGH/MEDIUM), `top_operations`, `top_hilos`.

---

## 3. Catálogo — cómo se carga y cómo se modifica

El catálogo vive primero en **Supabase** y, como red de seguridad, en `kernel/memento/critical_operations.yaml`.

| Tabla | Propósito | Campos críticos |
|---|---|---|
| `memento_critical_operations` | Qué operaciones requieren pre-flight | `id`, `triggers`, `requires_validation`, `requires_confirmation`, `source_of_truth_ids` |
| `memento_sources_of_truth` | Dónde está la verdad de cada operación | `id`, `source_type`, `location`, `parser_id`, `cache_ttl_seconds` |

**Flujo recomendado para agregar una nueva operación crítica:**

1. Insertar la fila en `memento_critical_operations` vía Supabase MCP (preferido) o SQL directo.
2. Si introduce una fuente nueva, insertar también en `memento_sources_of_truth`.
3. `POST /v1/memento/admin/reload` con `X-API-Key` válida.
4. Verificar el dashboard (`GET /admin/dashboard`): el contador `health.critical_operations_loaded` debe haber subido.
5. Disparar un `validate` real con la operación nueva y confirmar `validation_status=ok`.

**Si Supabase está caído:** el reload usa el YAML local y lo reporta en `loaded_from=yaml_fallback`. Esto es esperado y NO un error — la red de seguridad funcionó.

---

## 4. Heurísticas de contaminación (B6)

| Regla | Qué detecta | Severidad | Acción operativa |
|---|---|---|---|
| **H1** `credential_hash_obsolete` | El `credential_hash_first_8` del contexto NO coincide con la fuente actual, pero existió en commits previos. | HIGH | El hilo está usando credenciales viejas. Detener y re-leer credentials.md. |
| **H2** `host_divergent_with_history` | La última validación exitosa de este `hilo_id`+`operation` fue contra otro host estructuralmente distinto. | HIGH | Cluster fantasma probable. Verificar con `ticketlike_credentials` antes de reintentar. |
| **H3** `operation_without_recent_preflight` | El hilo tiene ≥5 validaciones recientes (60min) pero ninguna es de la operación actual. | MEDIUM | Hilo operando ciego. Informativo, no hostil. Puede continuar pero registrar el caso. |

Shadow mode v1.0 garantiza falsos positivos < 5% antes de activar bloqueo en HIGH (próximo sprint si las métricas lo respaldan).

---

## 5. Failure modes y respuestas operativas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `503 memento_validator_not_initialized` | El kernel arrancó sin catálogo (Supabase + YAML ambos vacíos). | Revisar logs `sprint_memento_b3_init_failed`. Insertar al menos una fila en YAML y reiniciar. |
| `504 memento_reload_supabase_timeout` | Supabase tardó >5s. | Reintentar; si persiste, revisar status de Supabase. El catálogo viejo sigue activo (no hubo swap). |
| `409 memento_reload_already_in_progress` | Otro reload corre simultáneo. | Esperar 1-2s y reintentar. El lock libera al terminar. |
| `200 persistence_failed=true` | Supabase no aceptó el insert de validación. | La validación es válida; el hilo puede proceder. Registrar incidente para el dashboard del próximo ciclo. |
| Dashboard muestra `db_available=false` | El kernel no tiene SupabaseClient. | Catastrófico para visibilidad. Revisar `memory.supabase_client` y env vars `SUPABASE_URL`/`SUPABASE_SERVICE_KEY`. |
| `unknown_operation` recurrente | Hilo invoca operaciones que no están en el catálogo. | Agregar al catálogo (paso 3 de §3) o corregir el `operation` en el cliente. |

---

## 6. Smoke tests y CI

| Comando | Qué cubre |
|---|---|
| `pytest tests/test_sprint_memento_b{2,3,4,5,6,7}* -q` | Suite Memento completa (139 tests, ~1.3s). |
| `python3 scripts/_smoke_credentials_md_b4.py` | Smoke local del parser de credentials.md. |
| `python3 scripts/_smoke_dashboard_memento_b7.py` | **Smoke productivo B7** contra Railway: 6 casos (auth, JSON, HTML, reload, validate post-reload). Requiere `MONSTRUO_API_KEY` en el ambiente. |
| `MEMENTO_INTEGRATION_TESTS=true pytest tests/test_sprint_memento_b7_e2e.py::test_integration_dashboard_against_railway` | Test opt-in equivalente, integrable a CI cuando el secret esté disponible. |

---

## 7. Línea de propiedad (zonas de modificación)

Después del Bloque 6, las siguientes zonas son **cerradas** salvo green light explícito de Cowork:

- `kernel/memento/validator.py`
- `kernel/memento/sources.py`
- `kernel/memento/models.py`
- `kernel/memento/contamination_detector.py`

El Bloque 7 cumplió esto: `kernel/memento_routes.py` (router) y archivos nuevos bajo `tests/` y `scripts/` y `docs/`. `kernel/main.py` no se tocó.

---

## 8. Roadmap inmediato (post-B7)

| Próximo paso | Pre-requisito |
|---|---|
| **Activar bloqueo en HIGH severity** (salir de shadow mode) | Falsos positivos < 5% durante 1-2 semanas, evidenciado por dashboard. |
| **Memento como pre-flight obligatorio en bot Telegram** | El Monstruo expone `/v1/memento/validate` y bot lo invoca antes de cada operación destructiva. |
| **H4: stale_validation_id** (detectar reuse de `validation_id` vencido) | Diseño + tests en B8 si se decide. |
| **Auto-rotación del catálogo cuando cambian credenciales** | Webhook desde rotación → POST /admin/reload. |

---

## 9. Contactos y documentación cruzada

| Doc | Referencia |
|---|---|
| Spec original del sprint | `bridge/sprint_memento_preinvestigation/spec_sprint_memento.md` |
| Schema SQL | `scripts/017_sprint_memento_schema.sql`, `scripts/020_memento_contamination_columns.sql` |
| Contrato Cowork ↔ Manus | `bridge/manus_to_cowork.md`, `bridge/cowork_to_manus.md` |
| Catálogo YAML local (fallback) | `kernel/memento/critical_operations.yaml` |
| Identidad y reglas duras | `AGENTS.md` (raíz del repo) |
