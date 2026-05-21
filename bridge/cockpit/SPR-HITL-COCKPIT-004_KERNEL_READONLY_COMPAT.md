# SPRINT 004 — Kernel Read-Only Compatibility

**Status:** READONLY_COMPAT_DOCUMENTED  
**Date:** 2026-05-18  
**Author:** Manus C (Cowork-Code)  
**Context:** Preparación para Cockpit UI (Productive Consolidation)  

## 1. Veredicto ejecutivo
El kernel es altamente compatible con una integración read-only para Cockpit. Existen 30+ endpoints GET estructurados que exponen el estado completo del sistema (finops, memory, agents, embrion, hitl, usage). 

La configuración CORS actual (`allow_origins=["*"]`) permite conexión local sin necesidad de allowlist. La autenticación está centralizada vía `X-API-Key` middleware, lo que requiere que Cockpit inyecte el header en sus peticiones.

No se detectaron riesgos críticos (P0) para la integración read-only, pero existen dependencias de inicialización (P2) donde los endpoints pueden devolver 503 si el subsistema subyacente (ej. ToolBroker, FinOps) no arrancó correctamente.

## 2. Endpoints GET auditados (Selección Core Cockpit)

| Endpoint | Existe | Read-only | Params | Response | Auth assumption | Riesgo |
|---|---|---|---|---|---|---|
| `/health` | Sí | Sí | Ninguno | `{"status", "version", ...}` | **Public** (bypasses auth) | LOW |
| `/health/auth` | Sí | Sí | Ninguno | `{"auth_configured", ...}` | **Public** (bypasses auth) | LOW |
| `/v1/stats` | Sí | Sí | Ninguno | Stats de memory, finops, db | `X-API-Key` middleware | LOW |
| `/v1/embrion/estado` | Sí | Sí | Ninguno | `{"latidos", "doctrinas", ...}` | `X-API-Key` middleware | LOW |
| `/v1/embrion/diagnostic` | Sí | Sí | Ninguno | `{"loop", "errors", ...}` | `X-API-Key` middleware | LOW |
| `/v1/hitl/pending` | Sí | Sí | Ninguno | `{"pending": [], "count": 0}` | `X-API-Key` middleware | LOW |
| `/v1/finops/summary` | Sí | Sí | Ninguno | Gastos, budget, top runs | `X-API-Key` middleware | LOW |
| `/v1/finops/history` | Sí | Sí | `limit` (Query) | `{"runs": [], "total": int}` | `X-API-Key` middleware | LOW |
| `/v1/memory/status` | Sí | Sí | Ninguno | `{"layers": {"mempalace", "mem0"}}` | `X-API-Key` middleware | LOW |
| `/v1/agents/status` | Sí | Sí | Ninguno | Registry status | `X-API-Key` middleware | LOW |
| `/v1/tools` | Sí | Sí | Ninguno | `{"tools": [], "total": int}` | `X-API-Key` middleware | LOW |
| `/v1/cowork/health` | Sí | Sí | Ninguno | `{"status", "endpoints"}` | `X-API-Key` middleware | LOW |
| `/v1/usage/today` | Sí | Sí | Ninguno | Usage metrics | `X-API-Key` middleware | LOW |

## 3. Contrato read-only

- **Cobertura:** El kernel expone telemetría detallada de casi todos sus subsistemas (Embrión, FinOps, Memoria, Agentes, Tools, HITL). La estructura de respuesta es consistentemente JSON.
- **Autenticación:** Cockpit DEBE enviar el header `X-API-Key: <MONSTRUO_API_KEY>` en todas las peticiones a `/v1/*`. Si no lo hace, recibirá un 503 Service Unavailable (fail-closed auth).
- **Gaps:** 
  - Algunos endpoints (ej. `/v1/tools`, `/v1/finops/status`) devuelven 503 o JSON de error si el subsistema no se inicializó correctamente en el arranque del kernel. Cockpit debe manejar respuestas gracefully.
  - La paginación es inconsistente (algunos usan `limit`/`offset`, otros devuelven todo).
  - `user_id` no se valida, por lo que Cockpit (si asume identidad) operará como el tenant global.

## 4. CORS local allowlist

- **Needed:** NO
- **Prepared:** NO
- **Productive config touched:** NO
- **Risk:** LOW. La configuración actual en `kernel/main.py` L1782-1787 es:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
  Esto permite que Cockpit ejecutándose en `http://localhost:3000` (o cualquier puerto) se conecte sin problemas de CORS. Las peticiones `OPTIONS` (preflight) están permitidas globalmente y hacen bypass del AuthMiddleware (verificado en `kernel/auth.py` L97).

## 5. Tests read-only

- **Applicable:** YES
- **Prepared:** NO (No se creó arnés nuevo, se documenta el plan).
- **Executado:** NO
- **Writes possible:** NO (si se usan mocks).
- **Risk:** LOW.
- **Test Plan:** Se pueden escribir tests unitarios para los endpoints GET utilizando `fastapi.testclient.TestClient`. Para evitar DB/Supabase, se deben inyectar mocks en `app.state` (ej. `app.state.db`, `app.state.finops`, `app.state.tool_registry`) antes de hacer las peticiones con el cliente de prueba.

## 6. No-action confirmations

| Restricción | Respetada | Evidencia |
|---|---|---|
| No POST | YES | Solo se analizaron `@app.get` y `@router.get`. |
| No DB writes | YES | Análisis estático únicamente. |
| No Supabase | YES | Análisis estático únicamente. |
| No auth/user_id/RLS | YES | No se modificó middleware ni policies. |
| No approve/reject real | YES | No se interactuó con `/v1/hitl/`. |
| No memory writes | YES | Análisis estático únicamente. |
| No secrets | YES | No se leyeron ni modificaron secrets. |

## 7. Riesgos y Gaps (P0/P1/P2)

- **P0:** Ninguno detectado para operaciones read-only.
- **P1:** Ninguno.
- **P2:** Fragilidad de inicialización. Varios endpoints devuelven 503 o errores genéricos si los subsistemas (`app.state.db`, `app.state.tool_registry`, `app.state.finops`) fallan al arrancar. Cockpit UI debe implementar robust error boundaries para no crashear si un widget recibe un 503.

## 8. Qué debe revisar Perplexity
- Auditar si la configuración CORS `allow_origins=["*"]` combinada con `allow_credentials=True` en FastAPI presenta vulnerabilidades explotables incluso con el `APIKeyAuthMiddleware` protegiendo los endpoints.

## 9. Qué debe integrar ChatGPT-2
- Al diseñar los widgets de Cockpit, asumir que la autenticación es obligatoria (`X-API-Key`) para `/v1/*`.
- Implementar manejo de errores para códigos 503 en widgets individuales (especialmente FinOps y Tools), ya que el kernel usa un patrón fail-closed si las dependencias no están listas.
