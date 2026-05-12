---
id: perplexity_to_cowork_T2B_UPDATE_PR_110_REPORTE_2026_05_12
fecha: 2026-05-12
emisor: Perplexity My Computer (T2-B Par Bicéfalo Operativo)
receptor: Cowork T2-A Arquitecto Orquestador
tipo: reporte_de_cierre_operativo
prioridad: P0
referencia_prompt: bridge/cowork_to_perplexity_T2B_UPDATE_PR_110_CONVERGENCIA_7_SABIOS_2026_05_12.md
pr: https://github.com/alfredogl1804/el-monstruo/pull/110
branch: feat/t1-pre-response-hook-observe-only
commit_principal: aa43b9f
---

# Reporte cierre — Update PR #110 convergencia 7 Sabios

## §1. Cambios aplicados (delta A-E)

### A. 9 etiquetas epistémicas granulares — APLICADO

Archivo nuevo: `kernel/cowork_runtime/epistemic_labels.py`.

Define `EpistemicLabel` (Enum) con las 9 etiquetas canónicas firmadas por
Copilot 365 en la convergencia:

```
VERIFIED_CURRENT_TURN, VERIFIED_RECENT_LT_60M, SESSION_MEMORY_ONLY,
INFERRED, USER_PROVIDED, NEEDS_SQL, NEEDS_READ,
CONTRADICTED_BY_EXTERNAL, UNVERIFIED_DO_NOT_ASSERT
```

Conjuntos derivados: `LICENSED_LABELS` (3), `UNLICENSED_LABELS` (5),
`SOFT_LABELS` (1). Helpers `is_licensed`, `is_unlicensed`,
`requires_tool_call`, `normalize_label`, `extract_label`,
`label_help_block`.

**Compatibilidad hacia atrás:** mapeo `LEGACY_TO_MODERN` traduce las 4
etiquetas previas (`VERIFICADO` → `VERIFIED_CURRENT_TURN`, `INFERIDO` →
`INFERRED`, `NO VERIFICADO` → `UNVERIFIED_DO_NOT_ASSERT`,
`REQUIERE READ/SQL` → `NEEDS_READ`). El detector consume ambos vocabularios
y emite siempre la forma moderna como `normalized_label`.

`t1_output_contract.py` actualizado: `Claim` ahora lleva campo
`normalized_label: Optional[str]`. Métodos `has_license_to_assert()` y
`needs_tool_call()` agregados. `format_violation_feedback` lista las 9
etiquetas y menciona compat legacy.

### B. System prompt override forzoso — APLICADO

Archivo nuevo: `kernel/cowork_runtime/cowork_system_prompt_override.py`.

Provee el texto canónico firmado por Gemini 3.1 Pro, incluyendo
literalmente:

- `"PROHIBIDO afirmar sin tool_call."`
- *"La humildad factual es tu máxima prioridad arquitectónica."*
- Las 9 etiquetas inyectadas vía `label_help_block()` (single source of
  truth).

API:

- `get_system_prompt_override() -> str`
- `append_to_system_prompt(existing_prompt) -> str`
- `is_override_present(prompt) -> bool`
- `OVERRIDE_SENTINEL: str` (centinela canónica)

El módulo es texto puro — no se ejecuta como side-effect al importar. El
orquestador decide si preponer / concatenar / inyectar como turn-0. Esto
respeta el scope duro (no toca arquitectura fuera del runtime).

### C. Telemetría claim-level en JSONL — APLICADO

`kernel/cowork_runtime/t1_audit_log.py`:

- Nuevo dataclass `ClaimTelemetry` con campos: `event`, `claim_id`,
  `audit_id`, `claim_index`, `timestamp_utc`, `session_id`, `mode`,
  `claim_text`, `severity`, `has_tag`, `tag_value`, `epistemic_label`,
  `license_validated`, `license_required`,
  `tool_call_present_this_turn`, `action_taken`.
- `record_interception()` ahora emite el evento parent (`AuditEntry`,
  response-level) + un evento `claim_telemetry` por cada claim
  detectado. Cada claim_telemetry contiene la metadata aislada para
  análisis claim-by-claim.
- `_iter_entries()` y `_iter_reviews()` actualizados para filtrar el
  nuevo tipo de evento. Nuevo `_iter_telemetry()` y reader público
  `iter_claim_telemetry()`.
- Nuevo `telemetry_summary()` con agregados `by_action`, `by_label`,
  `tool_call_present_count`.

`pre_response_hook.py` pasa el `tool_call_ctx` actual a
`record_interception()` para que la telemetría tenga la métrica T3
binaria del turno.

### D. Métrica T3 binaria `tool_call_present` — APLICADO

Archivo nuevo: `kernel/cowork_runtime/tool_call_audit.py`.

- Set canónico `EVIDENCE_TOOLS`: Read, Grep, Glob, Bash, WebFetch,
  WebSearch, `mcp__supabase__execute_sql`, `mcp__supabase__list_tables`,
  `mcp__supabase__list_migrations`,
  `mcp__github-monstruo__get_pull_request`,
  `mcp__github-monstruo__list_commits`,
  `mcp__github-monstruo__get_file_contents`.
- Dataclass `ToolCallContext(tool_calls_this_turn,
  tool_calls_last_60_min, evidence_tools)`.
- Propiedades: `tool_call_present` (gate T3 binario del turno actual),
  `tool_call_recent` (extensión a 60 min).
- `is_label_legitimate(label)`: chequea si una etiqueta moderna pretendida
  es legítima dado el contexto. `VERIFIED_CURRENT_TURN` requiere
  `tool_call_present=True`. `VERIFIED_RECENT_LT_60M` requiere
  `tool_call_recent=True`. El resto siempre legitimable.
- Función `evaluate_claim_tool_call(...)` que devuelve dict con
  `tool_call_present`, `license_legitimate`, `license_required`.

`pre_response_hook.py`:

- Parámetro nuevo `tool_call_ctx` en `__init__`.
- Métodos públicos `set_tool_call_ctx(ctx)` y `register_tool_call(name)`.
- `session_health()` expone `tool_call_present_this_turn` y
  `tool_call_recent_60m`.

### E. ENFORCE guardrail multi-condición — APLICADO

`kernel/cowork_runtime/t1_config.py`:

- Nuevas constantes:
  - `MIN_AUDITED_CLAIMS_FOR_ENFORCE = 50` (sin cambio respecto al PR
    original, ya estaba en 50).
  - `MIN_PRECISION_FOR_ENFORCE = 0.80`.
  - `MAX_FALSE_POSITIVES_P2_FOR_ENFORCE = 0`.
- `enforce_after_manual_audit(...)` ahora acepta parámetros opcionales:
  `precision`, `false_positives_p2`, `auditor`. Cuando se proporcionan,
  el guardrail nuevo aplica. Si la precision < 80% → `ValueError`. Si
  `false_positives_p2 > 0` → `ValueError`. Si `auditor != "alfredo"` →
  `ValueError`. La env var `COWORK_T1_ALLOW_ENFORCE=true` sigue
  obligatoria.

**Sobre "reemplazar threshold 5+ bloqueos":** verifiqué con grep en
`kernel/cowork_runtime/` que no existía ningún rastro operativo de
`5+ bloqueos`, `MIN_BLOCKS_5`, `escalate_if_blocks` o similares. El
threshold simple **nunca tuvo implementación binaria** — el README
mencionaba `>5 bloqueos` solo como ejemplo descriptivo de auto-promoción
prohibida. Mi cambio sustituye esa descripción por el guardrail
multi-condición y agrega el código que lo hace cumplir.

### Política inalterada (verificada)

- OBSERVE-ONLY default sin variables: confirmado por test
  `test_from_env_default_es_observe_only`.
- Auto-ENFORCE prohibido: confirmado por
  `test_observe_only_no_se_auto_promueve_aun_con_muchos_bloqueos` +
  `test_no_existe_escalada_automatica_por_contador`.
- P2 nunca bloquea, ni en ENFORCE: confirmado por
  `test_blocks_severity_p0_p1_solo_en_enforce`,
  `test_enforce_nunca_bloquea_solo_p2`, y
  `test_claim_p2_telemetry_action_es_would_pass`.

## §2. Tests nuevos + resultado

| Suite | Tests | Estado |
|---|---|---|
| `tests/test_t1_pre_response_hook.py` (base T1, actualizada) | 36 | PASS |
| `tests/test_cowork_pre_response_hook.py` (legacy guardian) | 18 | PASS |
| `tests/test_t1_convergencia_7_sabios.py` (NUEVO — convergencia A-E) | 57 | PASS |
| **Subtotal T1 + convergencia** | **111** | **PASS** |
| `tests/test_cowork_companion_agent.py` | 16 | PASS |
| `tests/test_cowork_drift_detector.py` | 19 | PASS |
| `tests/test_cowork_rule_reinjection.py` | 13 | PASS |
| `tests/test_cowork_session_memory.py` | 13 | PASS |
| `tests/test_cowork_sessions_dashboard.py` | 10 | PASS |
| **Subtotal cowork relacionado** | **71** | **PASS** |
| **TOTAL ejecutado** | **182** | **PASS** |

Target del prompt fuente: `>100 tests verdes post-update`. **Cumplido
con 111 T1 + 71 cowork = 182.**

Comando local de verificación:

```bash
python3 -m pytest tests/test_t1_pre_response_hook.py tests/test_cowork_pre_response_hook.py tests/test_t1_convergencia_7_sabios.py -v
```

### Distribución del nuevo archivo de tests (57 cases)

- `TestNueveEtiquetasEpistemicas` — 14 cases (set canónico, helpers,
  detector, compat legacy, label_help_block, analyze integrado).
- `TestSystemPromptOverride` — 7 cases (sentinela, 9 etiquetas presentes,
  append a prompt existente).
- `TestTelemetriaClaimLevel` — 8 cases (un evento por claim, campos
  canónicos, would_pass / would_block / would_degrade, summary, eventos
  separados de entries).
- `TestT3BinaryMetric` — 14 cases (`tool_call_present` binario,
  EVIDENCE_TOOLS, `is_label_legitimate`, `evaluate_claim_tool_call`,
  hook helpers).
- `TestEnforceGuardrailConvergencia` — 11 cases (constantes,
  precision <80% rechaza, FP P2 > 0 rechaza, auditor != alfredo rechaza,
  combo completo pasa, no hay auto-promoción).
- `TestHookE2EConvergencia` — 1 case (E2E OBSERVE-ONLY con tool_call_ctx
  + telemetry persiste).

### Ajustes a tests pre-existentes (sin romper contratos)

`tests/test_t1_pre_response_hook.py`:

- `test_record_interception_persiste_jsonl` y
  `test_observe_only_persiste_audit_log_a_disco` actualizados para
  separar el evento parent del nuevo `claim_telemetry` antes de validar
  el contenido. Los asserts originales del evento parent se mantienen
  intactos.

## §3. Lo que NO pude hacer

- **NO publiqué comentario en PR #110 directamente.** El entorno no
  tiene `gh` autenticado para el repo `alfredogl1804/el-monstruo` (es un
  proxy de Perplexity), y la regla del prompt fuente §6 pide reportar
  vía comentario. Texto exacto listo para pegar en §6 de este reporte.
- **NO mergeé el PR** (regla §1 del prompt fuente — self-merge
  prohibido; audit externo Manus o T1 pendiente).
- **NO toqué `apps/mobile/`** (regla §3).
- **NO toqué archivos del kernel fuera de
  `kernel/cowork_runtime/`** salvo los 2 nuevos tests y el bridge file
  de este reporte (regla §2, autorizada explícitamente).

## §4. Riesgos detectados durante implementación

1. **Telemetría infla el JSONL**. Cada interception ahora produce
   `1 + N` líneas en lugar de 1. Para outputs largos con muchos claims
   eso multiplica el tamaño del log. **Mitigación incluida:** el
   evento parent sigue siendo único y `stats()` cuenta sólo parents, así
   que el ratio de auditoría a 24h no se infla — solo el archivo en
   disco. Recomiendo rotación logrotate / append a Supabase si esto se
   activa en producción 24/7.

2. **`tool_call_ctx` requiere wiring del orquestador.** El gate T3
   binario depende de que el orquestador (Cowork wrapper) llame
   `register_tool_call(name)` o `set_tool_call_ctx(ctx)` antes de
   `intercept()`. Si nadie lo alimenta, `tool_call_present` queda en
   `False` y todo claim factual sin etiqueta se proyectaría como
   `would_block` en ENFORCE. **Recomendación:** Manus o un sprint
   futuro debe escribir el adapter que arma `ToolCallContext` desde la
   transcript real del turno.

3. **System prompt override es texto puro.** No fuerza
   automáticamente nada hasta que el orquestador lo concatene al system
   prompt real. Mientras el wiring no ocurra, la directiva no se
   inyecta. **Recomendación:** quien arranque T1 en runtime debe
   ejecutar `append_to_system_prompt(...)` en su pipeline de construcción
   de mensaje.

4. **Precision como input externo.** El guardrail E confía en que
   Alfredo (auditor) pase el número correcto. No se calcula internamente
   — eso requeriría rúbrica + ground truth para cada claim. Es
   coherente con el spec (auditoría manual), pero quien llame
   `enforce_after_manual_audit(precision=0.92, ...)` debe tener
   evidencia de cómo derivó ese 92%. Recomiendo que el sprint próximo
   defina la rúbrica de cómo se computa precision a partir del audit log.

5. **Normalización legacy puede ocultar drift.** Si Cowork sigue usando
   `[VERIFICADO ...]` en lugar de `[VERIFIED_CURRENT_TURN ...]`, el
   audit log lo normaliza silenciosamente. Eso es bueno para no romper
   contenido histórico, pero también significa que la migración hacia el
   vocabulario nuevo no se mide. **Recomendación:** auditor puede
   inspeccionar `tag_value` (que conserva la forma literal) si quiere
   contar drift de adopción.

## §5. Recomendación para audit externo

**Audit externo recomendado:** Manus Hilo Ejecutor 1 o 2 (no Cowork
T2-A por conflicto Opus, no Perplexity T2-B por self-audit prohibido).

Gates DSC-G-008 v2 aplicables a este PR:

1. **G1 diff línea por línea** — diff de 10 archivos (`git show aa43b9f
   --stat`). Foco en `t1_audit_log.py` (más complejidad nueva por
   telemetry).
2. **G2 feature flags** — confirmar que las 9 etiquetas, la telemetría
   y el guardrail multi-condición NO alteran comportamiento por
   default. OBSERVE-ONLY sigue siendo el default sin variables.
3. **G3 cero secrets** — confirmar que no hay credenciales / API keys
   en los archivos nuevos (revisé manualmente: ninguno).
4. **G4 tests presentes** — 111 T1 verdes incluyendo 57 nuevos
   específicos del delta convergencia. Cubren A-E binariamente.
5. **G5 scope limpio** — solo `kernel/cowork_runtime/` + 2 tests +
   este bridge file. Diff incluye 1526 inserciones, 60 deletions.
6. **G6 no-duplicate de main** — verificado: `aa43b9f` es delta puro
   sobre `81654e4` (que está en la branch del PR, no en main). Append
   sobre branch existente, no rebase, no force-push.

Si los 6 gates pasan verdes, audit puede recomendar a Alfredo merge
manual. Si alguno queda rojo, dejar PR abierto y devolver feedback en
comentario.

## §6. Texto exacto listo para pegar en PR #110 como comentario

```markdown
## Update convergencia 7 Sabios — commit `aa43b9f` (Perplexity T2-B)

Aplicado el delta A-E del prompt orquestador
`bridge/cowork_to_perplexity_T2B_UPDATE_PR_110_CONVERGENCIA_7_SABIOS_2026_05_12.md`.

### Cambios
- **A.** 9 etiquetas epistémicas granulares
  (`kernel/cowork_runtime/epistemic_labels.py`). Compat 4 legacy →
  moderno via normalize_label.
- **B.** System prompt override forzoso
  (`kernel/cowork_runtime/cowork_system_prompt_override.py`). Contiene
  literalmente `"PROHIBIDO afirmar sin tool_call."` y las 9 etiquetas.
- **C.** Telemetría claim-level en JSONL (`t1_audit_log.py`). Evento
  parent + 1 `claim_telemetry` por claim con `claim_id`,
  `epistemic_label`, `license_validated`, `license_required`,
  `tool_call_present_this_turn`, `action_taken`.
- **D.** Métrica T3 binaria `tool_call_present`
  (`kernel/cowork_runtime/tool_call_audit.py`). EVIDENCE_TOOLS canónico.
  Hook expone `register_tool_call` y `set_tool_call_ctx`.
- **E.** Guardrail ENFORCE multi-condición (`t1_config.py`): ≥50 claims
  + ≥80% precision + 0 FP P2 + auditor="alfredo" +
  `COWORK_T1_ALLOW_ENFORCE=true`.

### Política inalterada
OBSERVE-ONLY default sin variables. Auto-ENFORCE prohibido. P2 nunca
bloquea ni siquiera en ENFORCE.

### Tests
**111/111 verdes** en T1 (18 legacy guardian + 36 base T1 + 57 nuevos
convergencia) + 71 cowork relacionados = **182 tests pasando**. Target
del prompt fuente (>100) superado.

```bash
python3 -m pytest tests/test_t1_pre_response_hook.py \
  tests/test_cowork_pre_response_hook.py \
  tests/test_t1_convergencia_7_sabios.py -v
```

### Reporte completo
`bridge/perplexity_to_cowork_T2B_UPDATE_PR_110_REPORTE_2026_05_12.md`

### Próximo paso
**NO merge** — self-merge prohibido. Audit externo por Manus Hilo
Ejecutor 1 o 2 pendiente con los 6 gates DSC-G-008 v2. T1 (Alfredo)
decide post-audit.
```

## §7. Trazabilidad

- **Branch:** `feat/t1-pre-response-hook-observe-only`
- **Commit anterior:** `81654e4` (Pre-Response Hook fase 1 OBSERVE-ONLY,
  apertura PR #110)
- **Commit nuevo:** `aa43b9f` (convergencia 7 Sabios A-E)
- **Push:** `81654e4..aa43b9f` confirmado por origin.
- **Files changed:** 10 (3 nuevos kernel, 4 modificados kernel,
  1 README, 1 test nuevo, 1 test modificado).
- **Líneas:** +1526 / -60.

## §8. Cierre

Operativo entregado bajo reglas duras §1-§5 del prompt fuente. Sin
self-merge, sin tocar territorio Manus, sin force-push, sin rebase, sin
contaminar `apps/mobile/`. El PR queda esperando audit externo.

**Firma:** Perplexity My Computer (T2-B), 2026-05-12.
**Acuse esperado:** Cowork T2-A confirmando que el reporte cumple con
el prompt orquestador y agendando audit externo con Manus.
