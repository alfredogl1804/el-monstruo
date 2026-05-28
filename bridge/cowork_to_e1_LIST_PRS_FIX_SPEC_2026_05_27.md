# Spec — fix `tools/github.py::list_prs` (S5 E2E follow-up)

**Emisor:** Cowork T2-A · **Destinatario:** Manus E1 · **Fecha:** 2026-05-27
**Lane:** kernel (tools/github.py + tests).
**Severidad:** P1 (Monstruo da respuestas objetivamente falsas a misiones EXECUTE legítimas).
**Origen:** E2E iPhone S5 2026-05-27. Pantalla mostró *"No se encontraron Pull Requests abiertas"*. Cowork verificó binariamente via `mcp__github__list_pull_requests` que hay **decenas de PRs abiertas** en `alfredogl1804/el-monstruo`. La respuesta fue objetivamente falsa.

## Diagnóstico hasta aquí (Cowork, in-repo, binario)

1. **`detect_ghost_in_response` SÍ matchea** el response_text del screenshot (verificado corriendo el detector contra el texto exacto en sandbox — `proced(?:o)...llamada` + alias `github_ops`).
2. Si en runtime el ghost-gate NO disparó Capa 4 (la pantalla mostró narración fabricada, no respuesta degradada), entonces el else-branch del execute node NO se ejecutó → **`has_tool_calls=True` en la 1ª pasada** → Gemini SÍ function-calleó → el fix del S5 ghost FUNCIONÓ.
3. Por tanto, el fallo está aguas abajo: `github_ops` → `list_prs` se ejecutó y devolvió 0 PRs, aunque hay decenas.

**Confirmación pendiente (no bloqueante para arrancar):** las 3 líneas del log del run (`has_tool_calls` 1ª pasada, ¿hubo `router_pin_applied`/`ghost_detected_reprompting`?, intent + model_used real). Si confirman, cierra el caso.

## Lo que el código de `list_prs` permite — los 3 caminos al `[]`

```python
async def list_prs(repo: str, state: str = "open", limit: int = 10) -> dict:
    data = await _request("GET", f"/repos/{repo}/pulls?state={state}&per_page={limit}")
    if isinstance(data, dict) and "error" in data:
        return data  # Camino A: error de GitHub propagado tal cual
    items = data if isinstance(data, list) else []  # Camino B: data no es list ni error
    return {"pull_requests": [...]}  # Camino C: data es [] genuino
```

- **A** — `_request` devolvió `{"error": ..., "detail": ...}`. Gemini pudo haberlo narrado como "no se encontraron". Probable si token expirado, repo mal escrito, o 4xx.
- **B** — `_request` devolvió algo que no es list ni error-dict. Improbable para `/pulls`, pero posible si GitHub responde 204 No Content.
- **C** — la API devolvió `[]` genuino. Posible si: `state` mal pasado por el LLM, o **el LLM pasó solo `el-monstruo` sin owner** → 404 → en realidad Camino A.

Indistinguibles desde fuera. La causa real solo se ve con logging del camino tomado.

## Tareas (en orden)

### T1 — Instrumentar `list_prs` con logging estructurado (P0)

```python
async def list_prs(repo: str, state: str = "open", limit: int = 10) -> dict:
    logger.info("list_prs_called", extra={"repo": repo, "state": state, "limit": limit})
    data = await _request("GET", f"/repos/{repo}/pulls?state={state}&per_page={limit}")
    logger.info(
        "list_prs_raw_response",
        extra={
            "repo": repo,
            "data_type": type(data).__name__,
            "is_list": isinstance(data, list),
            "len_if_list": len(data) if isinstance(data, list) else None,
            "has_error_key": isinstance(data, dict) and "error" in data,
            "error_detail": (data.get("detail", "")[:200] if isinstance(data, dict) else None),
        },
    )
    if isinstance(data, dict) and "error" in data:
        return data
    items = data if isinstance(data, list) else []
    logger.info("list_prs_returning", extra={"repo": repo, "pr_count": len(items)})
    return {"pull_requests": [...]}
```

**Sin esto, cualquier "fix" es F2.**

### T2 — Surfacear errores de `_request` al LLM (no devolverlos crudos)

```python
if isinstance(data, dict) and "error" in data:
    return {
        "pull_requests": [],
        "error": data["error"],
        "detail": data.get("detail", ""),
        "note": "Tool failed to fetch PRs. The empty list is NOT a confirmation that no PRs exist."
    }
```

Fuerza al LLM a leer `error` en vez de narrar "no encontraron" sobre un fallo.

### T3 — Validar `repo` format en la entrada (defensivo)

```python
if "/" not in repo or repo.count("/") != 1:
    return {"error": "Invalid repo format. Expected 'owner/repo' (e.g. 'alfredogl1804/el-monstruo')."}
```

### T4 — Tests unitarios

Mockear `_request` con 3 escenarios:
- Lista con N>0 PRs → `pull_requests` tiene N entradas.
- `[]` → `pull_requests=[]`.
- Dict de error → `error` field surfaceado + nota.

### T5 — Re-correr E2E iPhone con instrumentación viva

Mismo prompt: *"dame la lista de las PRs abiertas en alfredogl1804/el-monstruo"*. Los nuevos logs revelan el camino tomado. Si A (error real) → diagnosticar token/scope/repo. Si C (lista vacía genuina) → revisar token del kernel.

## NO-objetivos

- ❌ NO tocar las 5 capas S5 (el detector matcheó binariamente → S5 funcionó).
- ❌ NO cambiar el endpoint ni la firma de `list_prs` sin evidencia.
- ❌ NO agregar paginación hasta saber si el problema es count, error, o param.

## Criterios de Cierre

- PR en branch `feat/list-prs-instrumentation-2026-05-27`, sin auto-merge.
- Audit Cowork DSC-G-008 v3 — 6 gates.
- Tests T4 verde local + CI.
- E2E iPhone re-corrido con logs nuevos, screenshot + 3 log lines pegadas en el PR.
- **Comando reproducible:** `pytest tests/test_github_list_prs.py -v` verde.

## Bridge

Cuando termines, postea el PR + 3 log lines del E2E re-run + commit hash y notifica a Cowork.

— Cowork T2-A
