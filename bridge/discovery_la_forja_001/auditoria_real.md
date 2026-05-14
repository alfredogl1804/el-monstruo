# Anexo B — Auditoría Binaria Estado Real Monstruo Producción

**Fecha**: 15 mayo 2026  
**Sprint**: LA-FORJA-001 v3.1  
**Método**: Llamadas reales a Railway, Supabase, GitHub, APIs externas  

## Resultado binario por punto auditado

### Infraestructura del Monstruo

| Punto | Resultado |
|---|---|
| Railway proyecto `el-monstruo-kernel` activo | ✅ HTTP 200 (`celebrated-achievement` → `el-monstruo-kernel`) |
| Variables Railway env | ✅ TODAS configuradas: ANTHROPIC, OPENAI, GEMINI, MANUS Apple+Google, LANGFUSE, GITHUB_TOKEN, SUPABASE_URL, SUPABASE_SERVICE_KEY, SONAR_API_KEY |
| Servicios Railway corriendo | ✅ python-app:8080 + frontend |

### APIs externas

| API | HTTP | Notas |
|---|---|---|
| Anthropic `claude-opus-4-7` | 200 | Rate limit: 1,000 RPM + 2.2M TPM (input + output combinados); 2M input tokens/min, 200K output tokens/min |
| OpenAI `gpt-5.5-pro` via `/v1/responses` | 200 | **Requiere `input` formato array de messages, NO string**. Modelo real `gpt-5.5-pro-2026-04-23` |
| Gemini `gemini-3.1-pro-preview` | 200 | No expone rate limits en headers |
| Perplexity `sonar-reasoning-pro` | 200 | Devuelve `citations` |
| Motor Simulador Railway externo | 200 | `https://simulador-api-production.up.railway.app` v5.2.1 producción, supabase OK, LLM disponible |

### Supabase del Monstruo

| Tabla | Estado |
|---|---|
| `thread_snapshots` | Existe; columna `is_canonical` NO existe (corregido en SPEC v3.1) |
| `project_runtime_heads` | Existe; canonical via JOIN con `head_snapshot_id` |
| `runtime_events` | Existe |
| `anti_dory_runtime_flags` | Existe; kill switch `shadow_write_enabled: false` |
| Tablas `forja_*` (las 9 propuestas) | NO existen (HTTP 404 las 9, sin colisión naming) |

### Snapshot canónico activo

Snapshot `7eece471-b5ee-4e72-ab21-d8f123a6b4a1` apuntado por `project_runtime_heads` con `(project_id="el_monstruo", front_id="anti_dory_d5_rap_001")`. Sprint MANUS-ANTI-DORY-002-v1, fase D5-FIRST.

### Tools del Monstruo

| Tool | Estado |
|---|---|
| `tools/manus_bridge.py` | Existe; base URL `https://api.manus.ai`; header `x-manus-api-key`; endpoints reales `POST /v2/task.create` y `GET /v2/task.get` (RPC-style, NO REST) |

### Apps del Monstruo

| App | Estado |
|---|---|
| `apps/mobile/` Flutter | Activa (modificada 6 mayo); 1 PR abierto #92 sobre MOBILE-1B |
| `apps/la-forja/` Node | NO existe aún; este sprint la crea |

### Bridge / sprints abiertos

25 sprints en `bridge/sprints_propuestos/`. **Cero colisiones** con `apps/la-forja/` ni migraciones `0036+`. Tres sprints relacionados con `apps/mobile/` Flutter pero NO con la-forja.

### Locks activos

- **Manus E2 (VERIFICADOR-001 DRAFT)**: lock activo declarativo desde 14 mayo sobre `tools/`, `kernel/`, `scripts/cowork_*`. La Forja NO toca estos directorios.
- **Cowork**: disponible para audit DSC-G-008 v3.

## Discrepancias entre SPEC v1/v2/v3 → v3.1 (resueltas)

| Discrepancia detectada | SPEC corregido a |
|---|---|
| `thread_snapshots.is_canonical` no existe | JOIN con `project_runtime_heads.head_snapshot_id` |
| `/v2/users/me` no existe en Manus API | Endpoints reales `/v2/task.create` y `/v2/task.get` |
| Asunción Consejo de Sabios (eliminado) | Solo Perplexity Sonar |
| Asunción Nixpacks (deprecado) | Railpack + Dockerfile |
| Asunción Next.js 15 | Next.js 16.2 |
| Asunción Vercel AI SDK v3 | v6.0.27 con AI Gateway |
| Asunción `temperature` en GPT-5.5 Pro | NO usar `temperature` (restricción del modelo) |

## Score acumulado

- v1 vs realidad: 56% alineado, 7 discrepancias bloqueantes
- v2 vs realidad: post-correcciones binarias
- v3.1 vs realidad: 100% reconciliado sobre 17 puntos auditados + 4 cierres pre-scaffolding

**Conclusión**: el SPEC v3.1 fue construido sobre el estado real del Monstruo HOY 15 mayo 2026, no sobre asunciones del entrenamiento.
