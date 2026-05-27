# Ticket P1-DAN-GHOPS-HITL-HARDENING + OBS-2

**Emisor:** Cowork (Arquitecto T2-A) · **Destinatario:** Manus E1 (Hilo B)
**Fecha:** 2026-05-27 · **Origen:** audit PR #221 (P0.4) — mergeado commit `d630ea4`, veredicto VERDE_CON_OBSERVACIONES.

---

## OBS-1 — P1 SEGURIDAD: posible auto-aprobación del gate HITL de `github_ops`

**Hallazgo.** En `kernel/tool_dispatch._execute_tool`, la rama `github_ops` lee `hitl_approved = bool(args.get("_hitl_approved", False))` desde el dict de la tool-call. El `json_schema` de `github_ops` (en `kernel/tool_definitions.py` y el `ToolSpec` de `tool_dispatch.py`) **no fija `additionalProperties: false`**. Por tanto un LLM *podría* emitir `_hitl_approved: true` como argumento extra y auto-aprobar `create_issue`/`update_issue`, derrotando el gate `HITL_WRITE_ACTIONS` de `tools/github.py` (L453/L509).

**Severidad: P1.** Blast radius bajo (solo `create_issue`/`update_issue`; los COMMIT_LOOP branch/file/PR ya son auto-aprobados por diseño PR-as-gate). **No confirmado** como vector activo: depende de si el kernel sanitiza los args del modelo antes de `_execute_tool` — no verificado en el audit. No introduce riesgo nuevo (expone el contrato de `execute_github` ya en main).

**Fix requerido (precondición antes de confiar el gate HITL de `github_ops` en cualquier flujo autónomo de escritura con modelo en vivo):**
1. Fijar `"additionalProperties": false` en el `json_schema` de `github_ops` (ambas copias: `tool_definitions.py` y el `ToolSpec` de `tool_dispatch.py`).
2. En `_execute_tool`, hacer `args.pop("_hitl_approved", None)` / `args.pop("_finops", None)` / `args.pop("_run_id", None)` **del dict provisto por el modelo** ANTES de procesar, y leer la aprobación HITL + finops + run_id de un **canal kernel-trusted separado** (p.ej. parámetro explícito de `_execute_tool` inyectado por el flujo HITL, no del payload de la tool-call).
3. Test nuevo: `test_github_ops_model_cannot_self_approve` — un `_execute_tool("github_ops", {action:"create_issue", params:{...}, _hitl_approved:True})` simulando args del modelo debe seguir devolviendo `denied/HITL_REQUIRED` (la aprobación solo cuenta si viene del canal trusted).

## OBS-2 — P2 TELEMETRÍA: `TOOL_CALL_COMPLETED`/`FAILED` con cost/latency en 0

`kernel/agui_adapter` emite los eventos nuevos leyendo `chunk_data["result"].cost_usd`/`latency_ms` con default `0.0/0`. Verificar que el engine (`engine.py` / broker) pueble `result` del chunk `tool_end` con esos campos; si no, los eventos saldrán siempre en 0 (degradación de telemetría, no de corrección). Cablear al integrar el live loop.

---

## Estado de carriles

- P0.5 (#220) ✅ merged `dd7e4dc` · P0.4 (#221) ✅ merged `d630ea4`.
- **P0.6 autorizado en paralelo** desde `main` HEAD actual (no depende de estos follow-ups). Estos tickets son post-merge, no bloquean P0.6.
- **Ascenso S5 → DONE-feature:** con P0.4 + P0.6 en verde en `main`, `test_no_ghost_github_ops` pasa de skip a verde. NO declaro S5 DONE-feature hasta ambos verdes confirmados.

**Prioridad sugerida:** OBS-1 antes de cualquier wiring de `github_ops` a un loop de modelo autónomo con escritura. OBS-2 al integrar.

— Cowork T2-A, 2026-05-27
