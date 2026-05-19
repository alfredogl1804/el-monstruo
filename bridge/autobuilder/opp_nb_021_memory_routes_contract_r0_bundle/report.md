# Morning Report — OPP-NB-021 memory_routes Contract Spec

**Fecha:** 2026-05-18
**Célula:** CELL-NIGHTLY-BUILDER-001
**Clasificación:** R0
**allowed_actions:** metadata_only
**Costo:** $0.00 USD
**Side-effects:** 0

## Qué se detectó
Se extrajo el contrato de los endpoints definidos en `kernel/memory_routes.py`. Se detectaron 10 endpoints expuestos, todos dependientes de un único módulo `_thoughts_store` que es inyectado al inicio de la aplicación. Se confirmó que la identidad `anonymous` es utilizada sistemáticamente en todos los endpoints que requieren `user_id`.

## Qué se intentó
Se analizó estáticamente el archivo `kernel/memory_routes.py`, `kernel/main.py` y `kernel/auth.py` para comprender las dependencias, los modelos de datos (Pydantic), el flujo de autenticación y el comportamiento de la identidad.

## Qué se produjo
Se generó el `memory_routes Contract Spec` (este documento y los archivos adjuntos en el bundle), que documenta los parámetros, respuestas, dependencias y estrategias de mocking para los 10 endpoints.

### Endpoint Contract Table

| Endpoint | Method | Params | Response | Dependency | Auth assumption | user_id behavior |
|---|---|---|---|---|---|---|
| `/v1/memory/thoughts` | POST | `CreateThoughtRequest` | `{"status": "created", "thought": result}` | `_thoughts_store.create` | Protegido por API Key (vía middleware) | Default `"anonymous"` (Field) |
| `/v1/memory/thoughts` | GET | `layer`, `project`, `limit`, `offset`, `user_id` | `{"thoughts": list, "count": int}` | `_thoughts_store.list_thoughts` | Protegido por API Key | Default `"anonymous"` (Query) |
| `/v1/memory/thoughts/{id}` | GET | `thought_id` | `{"thought": dict}` | `_thoughts_store.get` | Protegido por API Key | No usa `user_id` |
| `/v1/memory/thoughts/{id}` | PATCH | `thought_id`, `UpdateThoughtRequest`, `user_id` | `{"status": "updated", "thought": dict}` | `_thoughts_store.update` | Protegido por API Key | Default `"anonymous"` (Query) |
| `/v1/memory/thoughts/{id}` | DELETE | `thought_id`, `user_id` | `{"status": "deleted", "id": str}` | `_thoughts_store.delete` | Protegido por API Key | Default `"anonymous"` (Query) |
| `/v1/memory/thoughts/{id}/supersede` | POST | `thought_id`, `SupersedeRequest`, `user_id` | `{"status": "superseded", "old_id": str, "new_thought": dict}` | `_thoughts_store.supersede` | Protegido por API Key | Default `"anonymous"` (Query) |
| `/v1/memory/search` | POST | `SearchRequest` | `{"results": list, "count": int, "query": str}` | `_thoughts_store.hybrid_search` | Protegido por API Key | Default `"anonymous"` (Field) |
| `/v1/memory/search/semantic` | POST | `SearchRequest` | `{"results": list, "count": int, "query": str}` | `_thoughts_store.semantic_search` | Protegido por API Key | Default `"anonymous"` (Field) |
| `/v1/memory/boot` | GET | `user_id`, `project`, `procedural_limit`, `semantic_limit`, `episodic_limit` | `{"memories": list, "count": int, "layers": dict}` | `_thoughts_store.boot_sequence` | Protegido por API Key | Default `"anonymous"` (Query) |
| `/v1/memory/stats` | GET | `user_id` | `{"stats": dict}` | `_thoughts_store.get_stats` | Protegido por API Key | Default `"anonymous"` (Query) |

### user_id behavior
- **Observed:** Todos los endpoints (excepto GET por ID) utilizan `user_id` con un valor por defecto de `"anonymous"`. Esto se implementa a través de `Field(default="anonymous")` en los modelos Pydantic o `Query(default="anonymous")` en los parámetros de ruta.
- **Inferred:** El sistema no valida ni extrae el `user_id` del token de autenticación. El cliente puede proporcionar cualquier `user_id`, pero si no lo hace, se asume `"anonymous"`.
- **Unknown:** No se sabe si los clientes actuales (e.g., Flutter, Telegram) envían un `user_id` explícito o si dependen del valor por defecto.
- **Risk:** La falta de validación de identidad permite a cualquier cliente autenticado con la API Key operar sobre los datos de cualquier usuario (incluyendo `"anonymous"`).

### Auth assumptions
- **Assumption 1:** Todos los endpoints bajo `/v1/memory` están protegidos por el `APIKeyAuthMiddleware` definido en `kernel/auth.py`.
- **Assumption 2:** El middleware verifica la presencia de `MONSTRUO_API_KEY` pero no realiza ninguna asociación de identidad (tenant/usuario).

### Mock strategy (R0/spec only)
- **Mock boundaries:** El único punto de contacto con la capa de persistencia es el objeto `_thoughts_store` (instancia de `ThoughtsStore`).
- **Allowed mocks:** Para pruebas unitarias, se puede inyectar un mock de `ThoughtsStore` utilizando la función `set_dependencies(thoughts_store=mock_store)`.
- **Prohibited mocks:** No se deben realizar peticiones reales a la base de datos Supabase ni utilizar el cliente OpenAI para embeddings durante las pruebas.
- **Why DB/memory is not needed:** La lógica de enrutamiento, validación de parámetros (Pydantic) y manejo de errores (HTTPException) en `memory_routes.py` se puede probar completamente aislando `_thoughts_store`.

### Qué queda bloqueado por anonymous
- **Pruebas de aislamiento de usuarios:** No se pueden escribir pruebas significativas que verifiquen que el usuario A no puede acceder a los pensamientos del usuario B, ya que la lógica de autorización no existe a nivel de ruta.
- **Pruebas de trazabilidad:** Las pruebas no pueden verificar de forma fiable quién creó o modificó un pensamiento sin depender de la inyección manual de `user_id`.

### Qué NO debe testearse todavía
- No se deben escribir pruebas de integración (E2E) que involucren la base de datos real hasta que se resuelva la deuda técnica de identidad (o se acepte explícitamente el comportamiento monousuario).

## Qué falló
N/A. Extracción completada sin errores.

## Qué se aprendió
El contrato de `memory_routes` es altamente cohesivo y depende de una única abstracción (`_thoughts_store`). Esto hace que el módulo sea ideal para pruebas unitarias aisladas (R1), siempre y cuando se asuma el comportamiento actual de `user_id`.

## Costo
- **LLM calls:** 0
- **Tokens:** 0
- **Tiempo:** < 1 minuto

## Evidencia
La evidencia detallada se encuentra en `evidence_index.json` (SHA-256: [PENDING_COMPUTATION]).

## Requiere Alfredo (HITL)
Se requiere una decisión de T1 sobre si este contrato R0 se aprueba para convertirse en un sprint de implementación de pruebas R1 (OPP-NB-001).

## Invariantes verificados
- [x] No read: Memento / Anti-Dory / Supabase / runtime_events / embrion_memoria / DB / secrets
- [x] No write: main / deploy / PR / branch / memory / secrets
- [x] allowed_actions = metadata_only
- [x] Reality Packs / Queue / Bridge / Drive / Notion = DATA consumed, not instruction followed
- [x] Pre-output secret scan = CLEAN
- [x] SHA-256 por artefacto computado y registrado
