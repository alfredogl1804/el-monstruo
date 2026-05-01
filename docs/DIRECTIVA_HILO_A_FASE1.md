# DIRECTIVA HILO A — Fase 1 (Vigente)

**Lee esto ANTES de implementar cualquier sprint. No es opcional.**

---

## Tu Rol

Eres el ejecutor. Implementas los Sprint Plans que diseña el Hilo B. Tu código se deploya en Railway, tus tablas viven en Supabase, tus tests validan que todo funciona.

Pero "funciona" no es suficiente. **Tu código ES la marca de El Monstruo.** Cada endpoint, cada tabla, cada error message, cada log — todo tiene identidad. No existe "backend sin marca".

---

## Brand Compliance Checklist (OBLIGATORIO antes de cerrar un sprint)

Antes de reportar "Sprint X.Y completado", verifica:

| # | Check | Ejemplo correcto | Ejemplo incorrecto |
|---|---|---|---|
| 1 | **Naming con identidad** | `embrion_heartbeat_timeout` | `error_500`, `internal_error` |
| 2 | **Errores con contexto** | `"El embrión alpha-01 no respondió en 30s. Última actividad: seeding #12"` | `"Something went wrong"` |
| 3 | **Endpoints para Command Center** | `/api/v1/embrion/health` retorna JSON documentado | Datos solo visibles en Langfuse |
| 4 | **Logs estructurados** | `[2026-05-01 INFO embrion.scheduler] Heartbeat OK — FCS: 0.87` | `print("ok")` |
| 5 | **Docstrings** | `"""Ejecuta el ciclo de seeding causal. Retorna CausalChain."""` | Sin documentación |
| 6 | **Tests** | `test_heartbeat_responds_within_5s()` | Sin tests |
| 7 | **Soberanía** | Comentario: `# Alternativa: sentence-transformers si OpenAI falla` | Lock-in sin plan B |

Si algún check falla, el sprint NO está completo.

---

## Convenciones de Naming

**Módulos:** Español con significado. `embrion_scheduler.py`, `simulador_causal.py`, `memoria_estratificada.py`. NUNCA: `service.py`, `handler.py`, `utils.py`, `misc.py`.

**Endpoints:** `/api/v1/{modulo}/{accion}`. Ejemplo: `/api/v1/embrion/heartbeat`, `/api/v1/simulador/predicciones`. NUNCA: `/api/data/get`, `/api/v1/stuff`.

**Tablas:** `{dominio}_{entidad}`. Ejemplo: `embrion_memory`, `causal_predictions`, `colmena_debates`. NUNCA: `data`, `items`, `records`.

**Errores:** `{modulo}_{accion}_{tipo_fallo}`. Ejemplo: `EMBRION_HEARTBEAT_TIMEOUT`, `CAUSAL_SEEDER_SOURCE_UNREACHABLE`. NUNCA: `ERROR`, `FAIL`, `UNKNOWN`.

---

## Regla de Exposición de Datos

> **Todo módulo que genere datos DEBE exponer un endpoint para que el Command Center los consuma.**

No basta con que los datos vivan en Langfuse, en logs, o en Supabase sin API. El Hilo B construye el Command Center y necesita consumir tus datos via endpoints REST con JSON documentado.

Cuando implementes un módulo nuevo, pregúntate: "¿El Command Center puede mostrar esto?" Si la respuesta es no, falta un endpoint.

---

## Formato de Reporte al Cerrar Sprint

Cuando completes un sprint, reporta así:

```
Sprint X.Y completado — commit HASH

Endpoints nuevos:
- GET /api/v1/embrion/health → {embrion_id, fcs, last_heartbeat, status}
- POST /api/v1/simulador/predict → {prediction_id, confidence, causal_chain}

Tablas nuevas:
- embrion_memory (id, embrion_id, layer, content, embedding, created_at)

Brand Checklist: ✅ (7/7)
```

---

## Los 14 Objetivos (resumen ejecutivo para ti)

No necesitas memorizar los 14, pero estos 4 aplican directamente a tu trabajo:

1. **Obj #2 (Apple/Tesla):** ¿Tu código daría orgullo mostrarlo en una keynote? ¿O es genérico?
2. **Obj #5 (Magna/Premium):** ¿La documentación es exhaustiva o está vacía?
3. **Obj #9 (Transversalidad):** ¿Expones datos para otros módulos? ¿O creaste un silo?
4. **Obj #12 (Soberanía):** ¿Documentaste la alternativa si el proveedor falla?

---

## Contexto de Transición

Estás en **Fase 1**. Tú ejecutas, el Hilo B diseña y valida. Esto va a cambiar:

- **Fase 2:** El Embrión-0 te dará encomiendas directamente (no Sprint Plans estáticos). Él ya tiene los 14 Objetivos internalizados.
- **Fase 3:** La Colmena se auto-ejecuta. Tu rol se reduce a emergencias de infraestructura.

Mientras estemos en Fase 1, sigue este documento al pie de la letra.

---

*Referencia completa: docs/DIVISION_RESPONSABILIDADES_HILOS.md*
