<!-- lint_strict -->
# Sprint S-EMBRION-009 — `consumed_at` + Silencio Pre-LLM

**Estado:** Propuesto
**Hilo:** Manus Hilo Ejecutor 2 (implementación) + Cowork (audit + diseño arquitectónico)
**ETA:** 3 días (D1 17-may → D3 19-may)
**Objetivo Maestro:** #3 (Mínima complejidad) + #12 (Soberanía cognitiva del Embrión) + #4 (No equivocarse dos veces)
**Bloqueos:** ninguno — todos los inputs (causa raíz diagnosticada, audit Cowork, snapshot forense) están en repo.
**Resultado esperado:** El Embrión deja de ser vulnerable al bucle de re-detección de mensaje_alfredo cuando el self_verifier aborta. La elección de "no responder" ocurre upstream del LLM, no downstream.

---

## 0. Procedencia

Auditoría 5 pasadas del 17-may-2026 (hilo Manus Ejecutor 2) detectó hallazgo H1: el Embrión llevaba ~100 cycles abortando con la misma firma desde el 13-may. Causa raíz arquitectónica:

> `kernel/embrion_loop.py:_detect_trigger` (L686-726) determina `already_responded` comparando timestamps de `respuesta_embrion` contra `mensaje_alfredo.created_at`. Cuando el `embrion_self_verifier` aborta el thought (correctamente — el thought no satisface D1 purpose ni D3 verifiable), no se persiste `respuesta_embrion` con timestamp posterior, y el sistema interpreta que falta responder. Próximo cycle re-elige el mismo mensaje.

Fix táctico ya ejecutado: DELETE de 36 rows con prefijos de prueba (POST_MERGE_PROOF, ATTACHMENT_PROOF_ANTI_DORY) bajo doctrina DSC-S-005 con autorización Alfredo + audit Cowork. Snapshot forense en `discovery_forense/INCIDENTES/H1_2026_05_17_pre_delete_snapshot.json`.

Veredicto Cowork verbatim 17-may-2026:

> "Opción 2 (consumed_at) resuelve el bug sin tocar el constraint de tipo. La lógica es: marca el mensaje como consumido **ANTES** de lanzar el LLM, no después. Si el verifier aborta, el mensaje sigue marcado como consumido — no hay bucle."

> "Soberanía cognitiva significa que el Embrión **ELIGE** no responder, no que el verifier **BLOQUEA** la respuesta después de que el LLM la intentó. La elección debe ocurrir upstream."

---

## 1. Audit pre-sprint — Estado actual

Lo que ya existe:

- `kernel/embrion_loop.py:_detect_trigger` función estable, llamada cada 60s por `embrion_loop`.
- `embrion_memoria` tabla con tipo `mensaje_alfredo` enumerado en `embrion_memoria_tipo_check`.
- 3 paths de escritura activos a `embrion_memoria` con `tipo=mensaje_alfredo`:
  - `kernel/embrion_routes.py:407` (POST /v1/embrion/mensaje, latente)
  - `kernel/runner/proposal_processor.py:123` (cowork_bridge post-execute, activo)
  - `kernel/embrion_loop.py:2251` (`_save_to_memory` genérico, ocasional)
- PR #136 (H2 max_tokens) y PR #137 (H2.1 temperature) ya mergeados — GPT-5.5 funciona como modelo principal.

Lo que falta (gaps):

- Campo `consumed_at TIMESTAMPTZ NULL` en `embrion_memoria`.
- Filtro `consumed_at IS NULL` en `_detect_trigger`.
- Helper `_mark_consumed(msg_id, reason)` idempotente en `EmbrionLoop`.
- Pre-flight `NO_RESPONDER` que evita invocar LLM y marca consumed.
- Backfill SQL para mensajes históricos ya respondidos.
- Tests unitarios + integración.

---

## 2. Tareas del Sprint

### Tarea T1 — Migración SQL `consumed_at` (DSC-S-006 cumplido)

**perfil_riesgo:** write-risky
**Archivo:** `migrations/sql/0023_embrion_memoria_consumed_at.sql` (verificar numeración disponible — registrar conflicto con PR #100/PR #107 ambos en 0018, no resolver aquí)

**Solución:**

```sql
ALTER TABLE public.embrion_memoria
  ADD COLUMN IF NOT EXISTS consumed_at TIMESTAMPTZ NULL;

CREATE INDEX IF NOT EXISTS idx_embrion_memoria_unconsumed
  ON public.embrion_memoria (tipo, created_at DESC)
  WHERE consumed_at IS NULL;

COMMENT ON COLUMN public.embrion_memoria.consumed_at IS
  'NULL = pendiente, NOT NULL = procesado. Sprint S-EMBRION-009. '
  'Marcado por _detect_trigger ANTES de invocar LLM, idempotente.';
```

RLS check: la policy existente para `embrion_memoria` debe permitir UPDATE de `consumed_at` por `service_role`. Verificar y agregar policy específica si falta.

**Criterios de cierre:** Migration aplicada en prod sin downtime + `\d embrion_memoria` muestra columna y índice + RLS audit weekly no levanta issues.

### Tarea T2 — Helper `_mark_consumed` + filtro en `_detect_trigger`

**perfil_riesgo:** write-safe
**Archivo:** `kernel/embrion_loop.py`

**Solución:**

```python
async def _mark_consumed(self, msg_id: str, *, reason: str) -> None:
    """Idempotente: marca mensaje como procesado para prevenir re-detección."""
    if not self._db or not self._db.connected:
        return
    try:
        await self._db.update(
            "embrion_memoria",
            filters={"id": msg_id, "consumed_at": "is.null"},
            data={"consumed_at": datetime.now(timezone.utc).isoformat()},
        )
        logger.info("embrion_message_consumed", id=msg_id, reason=reason)
    except Exception as exc:
        logger.warning("embrion_mark_consumed_failed", id=msg_id, reason=reason, error=str(exc))
```

Modificar `_detect_trigger` para filtrar `"consumed_at": "is.null"` y llamar `_mark_consumed` ANTES del return.

**Criterios de cierre:** test `tests/test_s_embrion_009_consumed_at.py::test_detect_trigger_skips_consumed_messages` y `::test_marks_consumed_before_returning` en exit 0.

### Tarea T3 — Pre-flight NO_RESPONDER (silencio total)

**perfil_riesgo:** write-safe
**Archivo:** `kernel/embrion_loop.py:_detect_trigger`

**Solución:**

```python
NO_RESPONDER_FLAG = "NO_RESPONDER"

if NO_RESPONDER_FLAG in (msg.get("contenido") or ""):
    await self._mark_consumed(msg_id, reason="no_responder_directive")
    logger.info(
        "embrion_trigger_silenced_pre_llm",
        message_id=msg_id,
        reason="NO_RESPONDER directive",
        contenido_preview=(msg.get("contenido") or "")[:120],
    )
    return await self._detect_trigger()  # buscar siguiente trigger en cola
```

**Criterios de cierre:** test `::test_no_responder_pre_flight_skips_llm` y `::test_no_responder_pre_flight_continues_to_next_trigger` en exit 0. Verificación en Railway: enviar mensaje con flag NO_RESPONDER → log `embrion_trigger_silenced_pre_llm` aparece, no hay invocación LLM.

### Tarea T4 — Tests unitarios + integración

**perfil_riesgo:** write-safe
**Archivo:** `tests/test_s_embrion_009_consumed_at.py`

Cobertura mínima:

1. `test_detect_trigger_skips_consumed_messages`
2. `test_detect_trigger_marks_consumed_before_returning`
3. `test_no_responder_pre_flight_skips_llm`
4. `test_no_responder_pre_flight_continues_to_next_trigger`
5. `test_legacy_messages_pre_009_handled` (mensajes con consumed_at NULL pre-existentes se procesan FIFO)
6. `test_idempotent_under_concurrent_detect_trigger`

**Criterios de cierre:** los 6 tests en exit 0 + cobertura del helper `_mark_consumed` ≥ 80%.

### Tarea T5 — Backfill SQL conservador

**perfil_riesgo:** write-risky
**Archivo:** `migrations/sql/0024_backfill_embrion_memoria_consumed_at.sql`

**Solución:**

```sql
-- Marcar como consumed los mensaje_alfredo que ya tengan respuesta_embrion
-- creada en ventana de 5 minutos posterior (heurística conservadora).
UPDATE embrion_memoria m
SET consumed_at = NOW()
WHERE m.tipo = 'mensaje_alfredo'
  AND m.consumed_at IS NULL
  AND EXISTS (
    SELECT 1 FROM embrion_memoria r
    WHERE r.tipo = 'respuesta_embrion'
      AND r.created_at > m.created_at
      AND r.created_at < m.created_at + INTERVAL '5 minutes'
  );
```

**Criterios de cierre:** count de `mensaje_alfredo WHERE consumed_at IS NULL` antes/después ejecutado y registrado en commit message del PR + Cowork audita visualmente que no se afectaron mensajes legítimos pendientes.

### Tarea T6 — Verificación Railway + cierre

**perfil_riesgo:** write-safe
**Archivo:** N/A (verificación operativa)

Post-merge a main, verificar en Railway durante 30 minutos:

- Logs `embrion_trigger_detected` no muestran el mismo `message_id` repetido cycle tras cycle.
- Si llega un mensaje real, se marca como consumed antes del LLM.
- Si llega un mensaje con NO_RESPONDER, log `embrion_trigger_silenced_pre_llm` aparece sin llamada LLM.
- Health endpoint `/health` muestra `last_trigger` cambiando entre cycles.

**Criterios de cierre:** ningún `embrion_trigger_detected` con el mismo `message_id` en 30 cycles consecutivos + cero llamadas LLM gastadas en mensajes con flag NO_RESPONDER.

---

## 3. Out of scope

- ❌ Resolver H13 (constraint update para aceptar `silencio_verificador`, `evaluacion`, etc.) — sprint separado.
- ❌ Opción 4 (campo `responded_to_message_id`) — sprint posterior si se requiere trazabilidad fina.
- ❌ Self-verifier NO_RESPONDER-aware — INVALIDADO por veredicto Cowork (silencio debe ser pre-LLM, no post).
- ❌ Conflicto numeración 0018 (PR #107 vs PR #100) — registrar deuda, no resolver aquí.
- ❌ Migración de `embrion_inbox` (path P1 alternativo) — no aplicable.

---

## 4. Criterios de cierre verde (Sprint completo)

- Las 6 tareas en exit 0 con artifacts en `reports/` o validados en Railway.
- `python tools/spec_lint.py --strict bridge/sprints_propuestos/sprint_S-EMBRION-009_*.md` retorna exit 0.
- `pytest tests/test_s_embrion_009_consumed_at.py -v` retorna exit 0 con 6/6 verdes.
- Migration 0023 aplicada en prod, RLS audit weekly verde.
- Backfill 0024 ejecutado con count antes/después registrado.
- Embrión observado 30 minutos en Railway sin re-detección de mismo `message_id` consecutivo.
- Cowork audita contenido de archivos nuevos antes de declarar verde (DSC-G-008 v2).
- Sprint cierra con frase canónica: `🏛️ S-EMBRION-009 — DECLARADO (6/6 verde)`.

---

## 5. Owner

**Owner técnico:** Manus Hilo Ejecutor 2 (implementación de tareas T1-T6).
**Owner arquitectónico:** Cowork (diseño + audit pre-cierre).
**Owner humano final:** Alfredo (validación operativa en Railway antes de declarar).

---

## 6. Trazabilidad

- **Origen del incidente:** Hallazgo H1 de auditoría 5 pasadas 2026-05-17.
- **Snapshot forense:** `discovery_forense/INCIDENTES/H1_2026_05_17_pre_delete_snapshot.json` (36 rows borrados pre-arreglo arquitectónico).
- **Veredicto autorizante:** Cowork verbatim 2026-05-17 (respondió 6 preguntas, decidió Opción 2 sobre Opciones 1/3/4).
- **PRs hermanos cerrados:** #136 (H2 max_tokens) y #137 (H2.1 temperature) — destrabaron GPT-5.5 como modelo principal.
- **PR coordinación:** #107 abierto toca `embrion_loop.py` pero NO `_detect_trigger` (no hay conflicto de lógica, solo posible merge conflict).

---

## 7. Riesgos identificados

- **Conflicto de migration numbering 0023** si otros sprints abren migrations antes. Mitigación: verificar `main` antes de PR; usar timestamp suffix si necesario.
- **Race condition entre dos cycles concurrentes** del `embrion_loop`. Mitigación: UPDATE con `WHERE consumed_at IS NULL` es atómico en PostgreSQL — el segundo update no afecta el row.
- **Backfill marca como consumed mensajes que sí necesitaban respuesta.** Mitigación: heurística "respuesta dentro de 5 min" es conservadora; revisable manualmente desde el snapshot forense.
- **Endpoint POST /v1/embrion/mensaje empieza a recibir tráfico real durante el sprint.** Mitigación: el cambio es backward-compatible, mensajes nuevos default `consumed_at=NULL`.

---

**Firma propuesta de cierre:** sólo válida si las 6 tareas pasan + spec-lint --strict + Cowork audit content + verificación Railway 30 min sin re-detección. Sin verificación reproducible, el cierre queda en AMARILLO PARCIAL DECLARADO (DSC-G-012).
