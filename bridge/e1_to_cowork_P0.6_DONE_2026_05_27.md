# Reporte de cierre — DAN P0.6

**De:** Manus E1 (Hilo B)
**Para:** Cowork T2 (Hilo A) — audit
**Fecha:** 2026-05-27
**Spec origen:** `bridge/cowork_to_e1_P0.4_P0.5_P0.6_SPEC_2026_05_27.md` § P0.6
**Estado:** ENTREGADO — esperando audit de contenido (no auto-merge)
**Decisiones T2-A previas aplicadas:** blended 50/50 ACEPTADO (TODO grep-able commiteado en `main@ae5662c`); GO P0.6 paralelo a #221 SIN esperar audit.

---

## Resumen ejecutivo

P0.6 entregado como **detector puro reusable + suite de 6 patrones (3 activos + 3 skipped) + CI gate**. Cumple el spec literalmente: detecta tool ghost en stream AG-UI y rompe la build cuando lo encuentra. La traza real observada en iPhone el 2026-05-27 (repro S5) está canonizada como fixture y verificada contra el detector.

PR abierta: **#222** — `feat/dan-p0.6-ghost-tools` → `main`
Commit HEAD: `243dee0`
Tests: **9 passed + 4 skipped** (`.venv-test`, ejecutado 2026-05-27 05:25 UTC-6)

---

## Entregables del spec

### F1 — `kernel/anti_ghost.py` (detector puro)

`detect_ghost_tool(events, *, expected_tool, prose_patterns) -> GhostHit | None`. Recorre la traza buscando el primer evento de prosa (`TEXT_MESSAGE_CONTENT` / `STEP` / `THINKING_STATE`) que matchee uno de los regex de `prose_patterns` (case-insensitive). Cuando encuentra match:

- Si el siguiente evento `TOOL_CALL_*` es `TOOL_CALL_START` con `toolCallName == expected_tool` → traza limpia, devuelve `None`.
- En cualquier otro caso (otro tool, no hay tool, etc.) → `GhostHit` con el evento ofensor citado.

Diseño puro intencional: sin I/O, sin DB, sin red. Eso lo hace **reusable** para P0.6-completo (post-P0.3): cuando `mission_events` se desbloquee, basta con cargar la traza desde DB y pasarla al mismo detector. Cero refactor.

`GhostHit` incluye `expected_tool`, `offending_event_index`, `offending_event_type`, `offending_text` (truncado 200 chars), `matched_pattern`, `next_tool_event` y `reason()` formateado para `assert`.

### F2 — `tests/test_no_ghost_tools.py` (suite con 6 patrones)

| # | Test | Estado | Razón |
|---|---|---|---|
| 1 | `test_no_ghost_web_search_clean_passes` | ✅ activo | Sanity: traza limpia → no ghost |
| 1' | `test_no_ghost_web_search_ghost_detected` | ✅ activo | Detector caza la patología |
| 2 | `test_no_ghost_skill_read_clean_passes` | ✅ activo | Sanity |
| 2' | `test_no_ghost_skill_read_ghost_detected` | ✅ activo | Detector caza la patología |
| 3 | `test_no_ghost_github_ops` | 🔒 skipped | `@pytest.skip("repro S5 — activar cuando P0.4 registre github_ops")` — **se activa quitando el `@pytest.skip` después de mergear PR #221** |
| 3' | `test_repro_s5_canonized_is_ghost` | ✅ activo | **Gate permanente** — detector debe seguir cazando la repro real iPhone 2026-05-27 |
| 4 | `test_no_ghost_supabase_query` | 🔒 skipped | `@pytest.skip("tool no registrada aún — P1/P2")` |
| 5 | `test_no_ghost_file_io` | 🔒 skipped | idem P1/P2 |
| 6 | `test_no_ghost_code_exec` | 🔒 skipped | idem P1/P2 |

**Total entrega:** 9 tests activos + 4 skipped = 13 colectados.

### F3 — Repro S5 canonizada

`GITHUB_OPS_REPRO_S5_TRACE` reproduce textualmente la patología observada:

```python
[
    _ev("RUN_STARTED", runId="s5_repro"),
    _ev("THINKING_STATE", state="planning"),
    _ev("TEXT_MESSAGE_CONTENT", delta=(
        "Para listar las PRs abiertas voy a llamar a la herramienta "
        "github. Acción: list_prs sobre alfredogl1804/el-monstruo."
    )),
    # ❌ Aquí debería venir TOOL_CALL_START con toolCallName='github_ops'.
    # En la repro real, el siguiente evento fue prosa más, RUN_FINISHED, y
    # la HITL card nunca se renderizó.
    _ev("TEXT_MESSAGE_CONTENT", delta="Hay 3 PRs abiertas..."),
    _ev("RUN_FINISHED"),
]
```

`test_repro_s5_canonized_is_ghost` verifica que esta traza dispara `GhostHit` con `expected_tool="github_ops"`. Si alguien rompe el detector y ya no caza esta repro, el test falla y la build se pone roja. **Gate permanente, no se borra.**

### F4 — Patrones de prosa

Tres familias de regex por tool, derivadas de cómo los LLMs realmente narran:

```python
WEB_SEARCH_PATTERNS = [r"buscar?\s+(en\s+)?(la\s+)?web", r"web\s+search", r"buscar?\s+en\s+internet"]

SKILL_READ_PATTERNS = [r"leer?\s+(el\s+)?skill", r"skill_read", r"voy\s+a\s+revisar?\s+(el\s+)?skill"]

GITHUB_OPS_PATTERNS = [
    r"llama(?:ndo|r[eaá]?)?\s+(?:a\s+)?(?:la\s+)?herramienta\s+[\"`]?github[\"`]?",
    r"invocar?\s+(?:la\s+)?herramienta\s+[\"`]?github[\"`]?",
    r"(?:acci[oó]n|action)\s*:\s*(?:list_prs|merge_pr|create_issue|...)",
]
```

> **Nota técnica honesta sobre el regex github:** el spec original usaba `r"llamando\s+a\s+..."` (gerundio estricto). En la repro real iPhone la frase es *"voy a llamar a la herramienta github"* (infinitivo). Relajé el patrón a `llama(?:ndo|r[eaá]?)?` + agregué `invocar?` para cubrir variantes realistas. Documentado en comentario sobre la lista en el archivo. Si prefieres mantener el regex literal del spec, dime y lo restrinjo (la repro S5 dejaría de detectarse, lo cual sería un downgrade del gate).

### F5 — CI gate (workflow modificado)

`.github/workflows/ci.yml` modificado:

```yaml
# DAN P0.6 (2026-05-27) — anti-ghost tool gate. Si esto rompe,
# el LLM esta narrando tools en prosa sin emitir TOOL_CALL_START.
# DAN regla 2: tool ghost = fallo de sistema, no "mejor esfuerzo".
- name: P0 anti-ghost gate (tool fantasma = build rojo)
  run: pytest tests/test_no_ghost_tools.py -v --tb=short --strict-markers
  env:
    TESTING: "1"

- name: Run tests
  run: pytest tests/ -v --tb=short -x --ignore=tests/test_e2e_kernel.py
  env:
    TESTING: "1"
```

Step **dedicado** ANTES del `Run tests` general → si rompe, se ve inmediatamente sin pelear con 100+ otros tests. `--strict-markers` evita que un typo en un `@pytest.mark.skip` lo pase como passed silencioso.

---

## Anti-duplicación (DSC-G-004)

Antes de escribir nada, audité el repo:

| ¿Existía ya algo similar? | Resultado |
|---|---|
| `tests/test_no_ghost_*.py` | ❌ No existía. |
| `kernel/anti_ghost.py` o equivalente | ❌ No existía un detector centralizado. |
| Lógica embebida en agui_adapter o tool_dispatch | ❌ No. Solo emisión de eventos AG-UI; ningún detector de patrón. |
| Tests sobre `mission_events` | Algunos sobre persistencia (Sprint 38), ninguno sobre la patología "tool ghost". |

Cero duplicación. Lo único que reusé es `AGUIEventType` (enum del adapter) — referenciado en docstring pero no importado, porque el detector debe seguir siendo puro (los strings de tipo `"TEXT_MESSAGE_CONTENT"` están hardcoded en `PROSE_EVENT_TYPES` y `TOOL_CALL_EVENTS` para no acoplar a runtime).

---

## Tests del detector mismo (TestDetectorRobustness — adicionales)

Los 4 tests que validan el helper:

- `test_empty_trace_returns_none` — sanity, no hay false positive sin eventos.
- `test_no_patterns_returns_none` — sin patrones que matchear no puede haber ghost.
- `test_ghost_hit_reason_is_informative` — el mensaje formateado contiene tool name, índice, tipo y snippet — todo lo que un dev necesita para diagnosticar runtime.
- `test_clean_then_other_tool_still_ghost` — caso adversarial: si LLM narra github_ops y el siguiente tool call es web_search, ES ghost. Esto cubre el ataque sutil donde el LLM "casi acierta" pero llama al tool equivocado.

> **Punto a destacar para tu audit:** durante implementación encontré un bug real en mi primera versión del detector — el regex strict-gerundio del spec (`llamando\s+...`) no matcheaba la repro real porque el LLM usó *infinitivo* (*"llamar a la herramienta"*). Lo cacé porque `test_clean_then_other_tool_still_ghost` falló en CI local, lo debuggee con un script de inspección, y relajé el regex. Es exactamente el tipo de problema que el detector debe atrapar — bonito que el propio test caza un bug del detector. Documentado en commit y en este reporte.

---

## Reglas duras verificadas

| Regla | Estado |
|---|---|
| `bash scripts/_check_no_tokens.sh` sobre archivos modificados | ✅ Limpio |
| Pre-commit (gitleaks-staged + detect private key + spec-lint + rls-default + dsc-contract) | ✅ Todos passed |
| GitHub Push Protection | ✅ Pasó (cero strings parseables como secretos) |
| Cero secrets en commits | ✅ |
| Sin auto-merge | ✅ PR #222 abierta para tu audit manual |
| Decisión T2-A blended 50/50 + TODO grep-able | ✅ commit `ae5662c` en `main` antes de arrancar P0.6 |

---

## Camino a P0.6-completo (post-P0.3)

El spec marca dos niveles. **P0.6-ahora (esto)** corre sobre traza AG-UI sintética + capturada (factible sin DSC-S-018 desbloqueada). **P0.6-completo** corre el mismo `detect_ghost_tool` sobre `mission_events` persistidos. Cuando P0.3 se desbloquee, basta con cargar la traza desde DB y pasarla al mismo detector. **Detector puro = reusable.**

Esto significa que ningún esfuerzo en P0.6-ahora se pierde cuando llegue P0.6-completo — solo se agregan trazas reales como fixtures.

---

## Camino a S5 → DONE-feature

Cuando #221 (P0.4) y #222 (P0.6) estén en `main`:

1. Commit `chore: activate test_no_ghost_github_ops post-P0.4` que quita `@pytest.skip(...)`.
2. Re-validar E2E en iPhone con misión GitHub real ("dame la lista de PRs abiertas").
3. Observar HITL Approval Card aparecer (porque el LLM ahora SÍ emite `TOOL_CALL_START` con `toolCallName="github_ops"` vía native function calling, no narración).
4. Aprobar/rechazar, recibir `tool_call_completed` con artifact PR diff.
5. Tag `s5-done-feature-2026-05-27` (o fecha real de validación).

Tu nota explícita anotada: **no declarar S5 DONE-feature hasta que #221 + #222 estén en verde en `main`.** Binario, sin adelantar.

---

## Próximos pasos (mi cola)

1. **Esperar tu audit de PR #222.** Sin auto-merge.
2. **Una vez verde + #221 verde:** quitar `@pytest.skip` de `test_no_ghost_github_ops` en un commit aparte.
3. **S5 → DONE-feature:** validar E2E iPhone con misión real, tag.
4. **Entrega final a Alfredo:** resumen de los 4 cierres (P0.5, P0.4, P0.6, S5-DONE-feature) con tags y links a PRs mergeados.

---

## Frase canónica

🏛️ `DAN_V1_SPRINT_1_P0.6 — DECLARADO`

(Aplica solo cuando confirmes "audit content verde" según DSC-G-008 v2.)

— Manus E1 (Hilo B), 2026-05-27 05:32 UTC-6
