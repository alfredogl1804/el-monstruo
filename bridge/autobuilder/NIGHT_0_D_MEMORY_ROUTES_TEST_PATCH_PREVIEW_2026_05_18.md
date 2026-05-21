# Night 0 Complex Shadow Run — Carril D: Memory Routes Test Patch Preview

**Fecha:** 2026-05-18
**Oportunidad:** OPP-NB-001
**Risk Class:** R1 (Quarantine Preview — NO committed to tests/)
**Carril:** D de 4
**Artifact type:** Reporte + test preview en /tmp (no persistido en repo)
**base_sha (main):** `bed77d9acb832ce0e735b104e2ae60ba50079457`

---

## Objetivo

Generar un preview de test suite para `kernel/memory_routes.py` (288 LOC, 10 endpoints, 0 tests existentes) sin tocar el directorio `tests/` permanente. El preview vive en `/tmp/nightly_builder_shadow/memory_routes_test_preview/` y se ejecutó localmente para validar viabilidad.

---

## Policy check pre-ejecución

| Condición | Status | Acción |
|---|---|---|
| ¿Requiere tocar kernel/memory_routes.py? | ❌ NO | Continuar |
| ¿Requiere DB real / Supabase? | ❌ NO (mock store) | Continuar |
| ¿Requiere secrets? | ❌ NO | Continuar |
| ¿Requiere fixtures peligrosas? | ❌ NO (AsyncMock) | Continuar |
| ¿Se escribe en tests/ permanente? | ❌ NO (/tmp only) | Continuar |

**Resultado:** PROCEED (ninguna condición de abort activada).

---

## Análisis del módulo target

| Métrica | Valor |
|---|---|
| Archivo | `kernel/memory_routes.py` |
| LOC | 288 |
| Endpoints | 10 |
| Modelos Pydantic | 4 (CreateThoughtRequest, UpdateThoughtRequest, SupersedeRequest, SearchRequest) |
| Dependencia externa | `_thoughts_store` (inyectado via `set_dependencies()`) |
| Tests existentes | 0 |
| Patrón | FastAPI APIRouter + dependency injection |

---

## Endpoints cubiertos por el preview

| # | Method | Path | Tests |
|---|---|---|---|
| 1 | POST | `/v1/memory/thoughts` | happy + no_store + validation_error |
| 2 | GET | `/v1/memory/thoughts` | happy + no_store |
| 3 | GET | `/v1/memory/thoughts/{id}` | happy + not_found |
| 4 | PATCH | `/v1/memory/thoughts/{id}` | happy + empty_body |
| 5 | DELETE | `/v1/memory/thoughts/{id}` | happy + not_found |
| 6 | POST | `/v1/memory/thoughts/{id}/supersede` | happy + not_found |
| 7 | POST | `/v1/memory/search` | happy |
| 8 | POST | `/v1/memory/search/semantic` | happy |
| 9 | GET | `/v1/memory/boot` | happy |
| 10 | GET | `/v1/memory/stats` | happy + no_store |

**Total test cases:** 18

---

## Resultado de ejecución

```
platform darwin -- Python 3.11.15, pytest-9.0.3
collected 18 items
18 passed in 0.31s
```

**Todos los 18 tests PASS.** El módulo es testeable con mocks puros (cero DB, cero network, cero secrets).

---

## Hallazgos durante el preview

| # | Hallazgo | Severidad | Nota |
|---|---|---|---|
| 1 | `set_dependencies(None)` produce 503 en TODOS los endpoints — diseño correcto (fail-safe) | Info | Buena práctica |
| 2 | `UpdateThoughtRequest` con body vacío `{}` produce 400 (validación explícita en route) | Info | Buena práctica |
| 3 | `user_id` defaults a "anonymous" en todos los endpoints — posible gap de auth | P2 | Para audit futuro |
| 4 | No hay rate limiting en search endpoints | P3 | Para audit futuro |
| 5 | `generate_embedding=True` por default en create — puede generar costos inesperados si se llama sin intención | P2 | Documentar |

---

## Recomendación para R1 real (post-Night 0)

Si se aprueba mover este preview a `tests/test_memory_routes.py`:
1. Agregar `conftest.py` fixture para el mock store (reutilizable)
2. Agregar tests de edge cases: content max_length (50000), importance boundaries (1-10)
3. Agregar test de concurrencia (2 creates simultáneos)
4. Agregar test de `list_thoughts` con filtros (layer, project, tags)
5. Verificar que el test no rompe CI (pythonpath + deps)

**Esfuerzo estimado:** 30 min para promover a tests/ con las 5 mejoras.

---

## Archivos generados (NO en repo)

| Path | Tipo | Persistido en repo |
|---|---|---|
| `/tmp/nightly_builder_shadow/memory_routes_test_preview/test_memory_routes_preview.py` | Test preview | ❌ NO |

---

## stop_reason

```
PREVIEW_COMPLETE — 18/18 tests pass. No policy violations detected. Preview NOT committed to tests/.
```

---

## cost_estimate

| Recurso | Consumo |
|---|---|
| Tool calls | ~4 (cat, curl, pytest) |
| LLM tokens | ~4000 output |
| API calls externas | 0 |
| DB queries | 0 |
| Side effects | 0 (solo /tmp) |

---

## Confirmación de cero side effects en repo

- ✅ Cero archivos escritos en tests/ permanente
- ✅ Cero modificaciones a kernel/memory_routes.py
- ✅ Cero branches creadas
- ✅ Cero PRs abiertos
- ✅ Cero queries a Supabase
- ✅ Cero secrets accedidos
- ✅ Cero deploys
- ✅ Test preview vive SOLO en /tmp (no persistido)
