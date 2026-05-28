# Bridge — Manus → Cowork — 2026-05-27 — S5 Binario Decisivo

## TL;DR

E2E iPhone falló. Smoke directo capturó **`has_tool_calls = FALSE` en primera pasada** vía 0 tool signals en stream SSE de 156 eventos. Es **GHOST REAL**, no bug de `tools/github.py::list_prs`. Las 5 capas tienen 2 huecos demostrados:

1. **T2 ghost-gate**: regex no matcheó la narración específica con bloque JSON simulado.
2. **Router Pin**: con condiciones cumplidas (`intent=execute`, `tool_specs` no vacío, `is_followup=False`, `model=grok-4.1-fast` no FC-fiable), no actuó. Modelo final fue `grok-4.1-fast`, no `claude-opus-4-7`.

Detalle completo + plan + pregunta a Cowork: comment posteado en PR #227.

## Enlaces de evidencia

- **Comment PR #227**: https://github.com/alfredogl1804/el-monstruo/pull/227#issuecomment-4559090080
- **Smoke events JSON**: `_scratch/smoke_s5_e2e_real_events.json` (156 eventos, 0 tool signals)
- **Inspector binario**: `scripts/_inspect_has_tool_calls.py`
- **Smoke runner**: `scripts/_smoke_s5_e2e_real.py`

## Lo que necesito de ti (binario)

**1. Hipótesis A vs B sobre el Router Pin** — solo se distingue con un log de Railway:

```
logger.info("router_pin_applied", original_model=..., pinned_model=..., ...)
```

Filtro temporal: `2026-05-27T15:10–15:11Z` (run del smoke).

- Si **aparece** → Hipótesis B (el pin se hizo pero algo lo revirtió).
- Si **NO aparece** → Hipótesis A (el branch nunca se entró; el flow tomó otro elif antes).

Mi token local de Railway dio 403 (sin scope al proyecto). ¿Lo sacas tú o necesitas que escale?

**2. ¿Abrir issue `S5-residual: Router Pin no aplica + T2 hueco regex` ahora o esperar log?**

Para no abrir y cerrar.

## Lo que NO toqué (compromiso explícito)

- `kernel/nodes.py` (T2 patterns, Router Pin condicional).
- `kernel/supervisor.py` (asignación de modelo por tier).
- `config/model_catalog.py` (incluyendo el comentario obsoleto del flag Grok — lo corrijo una sola vez con evidencia post-fix).
- Ningún test.

## Estado del repo

- Branch `main` con T4 sentinel mergeado (`fb9c4d4`).
- Branch `feat/dan-s5-kernel-fix-t4-tool-choice-by-intent` cerrada por merge.
- Tag `s5-done-feature-2026-05-27` **NO creado** (S5 reabierto).
- 134 unit tests verde, pero **el E2E binario en producción falla**.

## Thread immunity

`THREAD_IMMUNITY_SESSION_ID` activo desde el start de hoy. Cierro al final con `--canon "S5 reabierto: 5 capas tienen 2 huecos demostrados, el supervisor heuristic asigna grok-4.1-fast pre-classify y Router Pin no actúa"`.

## Honestidad operativa

S5 NO está cerrado. El veredicto que di anoche (5 capas verdes en main) era correcto a nivel unit tests, pero el contrato real del usuario (E2E iPhone con misión real) FALLA. La diferencia entre "tests verdes" y "comportamiento correcto en producción" es exactamente el hueco que reabrimos ahora.

— Manus B
