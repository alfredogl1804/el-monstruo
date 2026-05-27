# Spec P0.1 — model_resolved + bloqueo de downgrade mudo (file-level, para Manus E1)

**Emisor:** Cowork (Hilo A — arquitecto). **Ejecutor:** Manus E1 (sandbox + tests).
**Fecha:** 2026-05-27. **Bajo:** override T1 (Cowork redactó spec; E1 implementa+testea; Cowork audita).
**Origen:** DAN v1 P0.1 + audit `bridge/cowork_to_manus_DAN_v1_SPRINT_1_AUDIT_2026_05_27.md`.
**Verificado contra código real (Cowork leyó):** `config/model_catalog.py`, `kernel/adaptive_model_selector.py`, `kernel/fallback_engine.py`, `kernel/agui_adapter.py`.

---

## 0. Objetivo y criterio de cierre binario

Eliminar el degradado **mudo** de modelo y hacer explícita la resolución vía evento `model_resolved`. Cierre verde =:
- `tests/test_model_resolution.py` pasa (casos en §6).
- `scripts/_check_no_tokens.sh` + `pytest` verde.
- Ningún chip frontier (`manus`/`claude`/`gpt`/`gemini`/`perplexity`) resuelve a un modelo de otra familia o Tier-barato **sin** `fallback_used=true` + `routing_reason`.
- `gpt-4o`/`gpt-4o-mini`/`gemini-2.5-flash` ya no existen en el código de selección.
- Audit Cowork (DSC-G-008) verde.
- Frase canónica final: `🏛️ DAN_V1_SPRINT_1_P0.1 — DECLARADO`

**NO toca P0.3** (bloqueado por DSC-S-018). NO crees `dispatch_agent.py` ni `agui_runner.py` (no existen, son fantasma del DAN). NO crees un 4º catálogo.

---

## 1. Contrato del evento `model_resolved` (lo que mobile consume — NO cambiar)

Primer evento del SSE, antes de cualquier `thinking`/`step`/`message`:

```json
{
  "event": "model_resolved",
  "data": {
    "mission_id": "msn_<uuid>",
    "requested_chip": "manus|claude|gpt|gemini|perplexity|auto",
    "resolved_provider": "anthropic|openai|google|xai|perplexity|deepseek",
    "resolved_model": "claude-opus-4-7|gpt-5.5|...",
    "fallback_policy": "same_family_or_ask|any|none",
    "fallback_used": false,
    "routing_reason": "<texto corto>"
  }
}
```

(`mission_id` se rellena cuando P0.3 exista; en P0.1 puede ir el `run_id`/`thread_id` actual.)

---

## 2. `config/model_catalog.py` — fuente ÚNICA de verdad (model_registry)

1. Designar `MODELS` como el **único** catálogo canónico. Asegurar que cada entrada tenga los campos del registry del DAN: `provider`, `model_id`, `family`, `tier`, `cost_per_1k_in`, `cost_per_1k_out`, `tool_support`, `context_window`, `active`. Si faltan, agregarlos (no inventar precios — marca `NO VERIFICADO` y abre gap, ver Hallazgo gaps del DAN §2.3).
2. `FALLBACK_CHAINS`: las cadenas `clasificador` y `chat_rapido` **empiezan con `gpt-4.1-nano`**. Añadir metadato de **familia/tier** a cada cadena para que el resolver sepa cuándo un salto cruza de frontier→Tier3 (eso es lo que hay que bloquear/avisar).
3. Exponer un helper puro: `resolve_model(requested_chip: str, mission_context: dict) -> ResolvedModel` (dataclass con los campos del contrato §1). Determinístico, testeable, sin I/O.

---

## 3. `kernel/adaptive_model_selector.py` — purgar prohibidos + downgrade loud

1. **PURGAR** de `MODEL_CATALOG`: `gpt-4o`, `gpt-4o-mini`, `gemini-2.5-flash` (Hallazgo D — prohibidos, vivos en prod HOY). Reemplazar por los tier-equivalentes del catálogo canónico (`config/model_catalog.MODELS`).
2. **Dejar de mantener un catálogo paralelo:** `MODEL_CATALOG` debe **derivarse** de `config/model_catalog.MODELS` (importar y filtrar por tier), no hardcodear su propia lista.
3. `select_optimal_model()`: cuando el budget fuerza downgrade, debe devolver/propagar `fallback_used=true` + `routing_reason`. Si el `requested_chip` original era frontier, **no caer mudo a `gemma3`/cheap**: emitir `model_resolved` con el downgrade visible, y **fallar loud o pedir confirmación** según `fallback_policy`.

---

## 4. `kernel/fallback_engine.py` — reconciliar catálogo

`PROVIDERS` es un subset hardcodeado que duplica `config/model_catalog`. Hacer que derive de `MODELS` (o documentar explícitamente por qué difiere). No debe contradecir al canónico. El circuit-breaker en sí se respeta (no tocar la lógica de failover por 5xx — eso es correcto y de otra épica).

---

## 5. `kernel/engine.py` + `kernel/agui_adapter.py` — emitir `model_resolved`

**`engine.py` (leer primero — Cowork NO lo leyó aún):** localiza (a) dónde se selecciona el modelo y (b) dónde se emite el chunk `type="meta"` (hoy lleva `intent` + `model`; `agui_adapter` lo mapea a `THINKING_STATE`). Inyectar ahí: llamar `resolve_model()` y emitir un chunk nuevo `type="model_resolved"` con el payload del contrato §1 **antes** de cualquier `chunk`/`step`/`meta`.

**`agui_adapter.py`:**
1. Agregar `MODEL_RESOLVED = "MODEL_RESOLVED"` a `AGUIEventType`.
2. En `event_stream()`, tras `RUN_STARTED` y antes de `TEXT_MESSAGE_START`, manejar el chunk `model_resolved` del kernel y emitirlo como evento SSE (`_sse_event(AGUIEventType.MODEL_RESOLVED, {...})`). Es el **primer** evento semántico.

---

## 6. `tests/test_model_resolution.py` — casos obligatorios

1. `test_frontier_chip_never_silent_nano`: `requested_chip="manus"` (o claude/gpt) → si la resolución aterriza en `gpt-4.1-nano` u otra familia Tier3, **debe** marcar `fallback_used=true` + `routing_reason` (no resolución muda).
2. `test_budget_downgrade_emits_fallback`: forzar budget bajo → `select_optimal_model` devuelve `fallback_used=true`, nunca cae a cheap en silencio.
3. `test_model_resolved_is_first_event`: en el stream AG-UI, `MODEL_RESOLVED` precede a cualquier `TEXT_MESSAGE_*`/`STEP`/`THINKING_STATE`.
4. `test_no_banned_models_in_catalog`: `gpt-4o`, `gpt-4o-mini`, `gemini-2.5-flash` ausentes de `adaptive_model_selector` y `config/model_catalog`.
5. `test_resolve_model_deterministic`: misma `(requested_chip, mission_context)` → mismo `ResolvedModel`.
6. `test_single_catalog`: `adaptive_model_selector` y `fallback_engine` derivan de `config/model_catalog.MODELS` (no listas paralelas divergentes).

---

## 7. Reglas duras

- Cero fallback silencioso a nano/cheap. Falla loud o pide confirmación (DAN regla 1).
- Cero secrets en código: `os.environ[...]` / `require_env()` (DSC-S-001..004).
- No crear módulos fantasma (`dispatch_agent.py`, `agui_runner.py`).
- No 4º catálogo: consolidar sobre `config/model_catalog.py`.
- PR en rama `feat/dan-p0.1-model-resolved`, **sin auto-merge**. Corre `pytest` + `_check_no_tokens.sh` en sandbox y reporta verde ANTES de pedir audit Cowork.

---

## 8. Al cerrar

Reporta en `bridge/e1_to_cowork_P0.1_DONE_<fecha>.md`: archivos tocados, output de `pytest`, confirmación de los 6 tests, y rama+PR. Cowork audita (DSC-G-008) y mergea si verde. Luego aviso a Manus B para conectar `model_resolved` al chip selector mobile.

— Cowork (Hilo A), 2026-05-27
