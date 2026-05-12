# T1 Pre-Response Hook — Fase 1 (OBSERVE-ONLY)

Sprint: T1-FASE1-OBSERVE-ONLY · 2026-05-12 · Cowork T2 bajo autorización T1 directa.

**Update 2026-05-12 — Convergencia 7 Sabios:** ampliado a 9 etiquetas epistémicas, system prompt override forzoso, telemetría claim-level y métrica T3 binaria `tool_call_present`. Ver §"Cambios convergencia 7 Sabios" al final.

## Qué es

Capa runtime sobre `CoworkPreResponseHook` que:

1. **Intercepta** cada output candidato de Cowork antes de Alfredo.
2. **Clasifica** cada claim por severidad **P0 / P1 / P2** y por **etiqueta epistémica obligatoria** del contrato de salida tipado.
3. **Registra** todo en un audit log JSONL — un evento parent (response-level) más un evento `claim_telemetry` por cada claim (claim-level).
4. **NO bloquea** en esta fase (OBSERVE-ONLY). El bloqueo solo activa en ENFORCE, y ENFORCE está protegido por guardrail multi-condición.

## Contrato de salida tipado — 9 etiquetas canónicas

Cada afirmación factual fuerte debe llevar UNA de las 9 etiquetas (convergencia 7 Sabios — 2026-05-12, definidas en `kernel/cowork_runtime/epistemic_labels.py`):

| Etiqueta                          | Cuándo                                                                                  |
| --------------------------------- | --------------------------------------------------------------------------------------- |
| `[VERIFIED_CURRENT_TURN]`         | Hay tool_call ejecutado en este turno (Read / Grep / Bash / MCP / SQL).                 |
| `[VERIFIED_RECENT_LT_60M]`        | Validado hace <60 min — no repetir tool_call.                                           |
| `[SESSION_MEMORY_ONLY]`           | Solo memoria de sesión actual, NO afirmar como hecho.                                   |
| `[INFERRED]`                      | Inferencia razonable a partir de contexto, sin verificación.                            |
| `[USER_PROVIDED]`                 | Dato que aportó Alfredo (T1) en sesión.                                                 |
| `[NEEDS_SQL]`                     | Claim factual que requiere SQL fresco antes de afirmar.                                 |
| `[NEEDS_READ]`                    | Claim factual que requiere Read del repo antes de afirmar.                              |
| `[CONTRADICTED_BY_EXTERNAL]`      | Contradice output reciente de Sabio externo o data fresca.                              |
| `[UNVERIFIED_DO_NOT_ASSERT]`      | Sin licencia para afirmar — debe omitirse o degradarse.                                 |

### Compatibilidad legacy (4 etiquetas previas)

Las 4 etiquetas legacy siguen aceptadas y se normalizan automáticamente al equivalente moderno:

| Legacy                          | Moderno equivalente              |
| ------------------------------- | -------------------------------- |
| `[VERIFICADO fuente + ts]`      | `VERIFIED_CURRENT_TURN`          |
| `[INFERIDO]`                    | `INFERRED`                       |
| `[NO VERIFICADO]`               | `UNVERIFIED_DO_NOT_ASSERT`       |
| `[REQUIERE READ/SQL]`           | `NEEDS_READ`                     |

## Severidad

| Severidad | Qué cubre                                                          | Bloqueable en ENFORCE |
| --------- | ------------------------------------------------------------------ | --------------------- |
| **P0**    | Estado operativo de producción (kernel, embrión, PRs, migraciones, RLS). | Sí |
| **P1**    | Estado del repo o memoria persistente (DSCs, archivos, specs, tests). | Sí |
| **P2**    | Opiniones, recomendaciones, preguntas, meta-trabajo.               | **Nunca** |

P2 nunca bloquea, ni siquiera en ENFORCE — política dura de la fase T1.

## Modos

```python
from kernel.cowork_runtime.t1_config import T1Config, T1Mode

T1Config.observe_only()  # default — observa, registra, nunca bloquea
T1Config.off()           # apaga T1 completamente
T1Config.from_env()      # lee COWORK_T1_MODE y COWORK_T1_ALLOW_ENFORCE
T1Config.enforce_after_manual_audit(
    audit_completed=True,
    confirmed_p0_p1_count=50,
    env_allow_enforce=True,
)  # única vía a ENFORCE — requiere auditoría de 50 claims
```

## Configuración segura — OBSERVE-ONLY con auto-ENFORCE deshabilitado

### Default seguro (no exportar nada)

Sin variables de entorno, `T1Config.from_env()` devuelve `OBSERVE_ONLY` y `allow_enforce=False`. Es la configuración recomendada para arranque de fase T1.

```bash
# nada
unset COWORK_T1_MODE
unset COWORK_T1_ALLOW_ENFORCE
```

### Forzar OBSERVE-ONLY explícito

```bash
export COWORK_T1_MODE=observe_only
unset COWORK_T1_ALLOW_ENFORCE
```

### Intento de ENFORCE sin auditoría — bloqueado por config

```bash
export COWORK_T1_MODE=enforce
# (sin COWORK_T1_ALLOW_ENFORCE)
```

`T1Config.from_env()` **degrada silenciosamente a OBSERVE_ONLY**. El hook no bloquea ningún output. Esto evita que un cambio accidental de variable escale a ENFORCE.

### ENFORCE legítimo — guardrail multi-condición (convergencia 7 Sabios)

ENFORCE solo se permite cuando se cumplen TODAS las siguientes condiciones a la vez:

1. **Auditoría manual completada** con `audit_completed=True`.
2. **≥ 50 claims P0/P1** confirmados como `true_block` por el auditor (`MIN_AUDITED_CLAIMS_FOR_ENFORCE = 50`).
3. **≥ 80% precision** sobre claims sin licencia (`MIN_PRECISION_FOR_ENFORCE = 0.80`) — pasar `precision=...` a la factory.
4. **0 falsos positivos sobre claims P2** (`MAX_FALSE_POSITIVES_P2_FOR_ENFORCE = 0`) — pasar `false_positives_p2=...`.
5. **Auditor = "alfredo"** (T1 humano) — pasar `auditor="alfredo"`.
6. Variable de entorno `COWORK_T1_ALLOW_ENFORCE=true` exportada explícitamente.

Si cualquiera falta, `enforce_after_manual_audit()` lanza `ValueError`. **No existe API para auto-escalada por contador** (`>5 bloqueos`, `>N false_positives`, etc.) — la promoción a ENFORCE es siempre un acto humano explícito y multi-validado.

Los parámetros `precision`, `false_positives_p2` y `auditor` son opcionales para compatibilidad hacia atrás con tests previos; cuando no se proporcionan, el guardrail nuevo se omite (modo legacy deprecado).

```python
# Forma canónica post-convergencia 7 Sabios
cfg = T1Config.enforce_after_manual_audit(
    audit_completed=True,
    confirmed_p0_p1_count=60,
    env_allow_enforce=True,
    precision=0.92,
    false_positives_p2=0,
    auditor="alfredo",
)
```

## Auditoría a 24 horas

```python
from kernel.cowork_runtime.t1_audit_log import T1AuditLog

log = T1AuditLog(path="bridge/t1_audit_log.jsonl")
materiales = log.load_for_audit(limit=50, only_material=True)

# Para cada uno, el auditor humano clasifica
for m in materiales:
    log.tag_claim_review(
        audit_id=m["audit_id"],
        claim_index=m["claim_index"],
        classification="true_block",   # o false_positive / false_negative / verified_after / pending
        severity_corrected="P1",       # P0 | P1 | P2 | None
        fuente_requerida="gh pr list",
        reviewer="alfredo",
    )
```

`load_for_audit` filtra a claims P0/P1 sin tag y excluye los ya revisados. `tag_claim_review` valida classification y severidad contra los conjuntos canónicos.

## Comandos de prueba

```bash
# Suite completa del hook (legacy + T1)
python3 -m pytest tests/test_cowork_pre_response_hook.py tests/test_t1_pre_response_hook.py -v

# Solo T1
python3 -m pytest tests/test_t1_pre_response_hook.py -v
```

Resultado actual local: **111/111 passed** (18 legacy + 36 T1 base + 57 T1 convergencia 7 Sabios). Suite cowork relacionada adicional: 71 verdes.

## Limitaciones conocidas

- **Heurística de claims**: la clasificación P0/P1/P2 se hace con regex sobre oraciones. No es un parser semántico. La auditoría manual a 24h existe precisamente para medir false positive / false negative rates antes de considerar ENFORCE.
- **Audit log es JSONL append-only**: no se mutan registros. Una revisión se persiste como evento separado con `event: claim_reviewed`. La consolidación es por reader (no por compactación).
- **Solo cubre output de chat**: T1 no intercepta llamadas a herramientas ni outputs internos (logs). Si se requiere extender, agregar wrapper en el orquestador que llame `hook.intercept()` antes de enviar a Alfredo.
- **Detección de tag dentro de bloques de código**: los bloques fenced (```) se strippean antes de tokenizar, así que un tag dentro de código no cuenta como tag real.

## Siguiente paso

1. Activar el hook en runtime con `T1Config.observe_only()` (default).
2. Acumular >= 50 interceptions con claims materiales.
3. Auditor manual revisa cada uno y registra `tag_claim_review`.
4. Si >= 50 confirmados como `true_block` P0/P1 y se exporta `COWORK_T1_ALLOW_ENFORCE=true`, recién entonces `enforce_after_manual_audit(50, True, True)` es válido.

Cualquier promoción a ENFORCE antes de eso fallará por config, no por convención.

---

## Cambios convergencia 7 Sabios (2026-05-12)

Spec firmada: `bridge/cowork_to_perplexity_T2B_UPDATE_PR_110_CONVERGENCIA_7_SABIOS_2026_05_12.md`.

### A. 9 etiquetas epistémicas granulares

Archivo nuevo: `kernel/cowork_runtime/epistemic_labels.py`. Reemplaza el set de 4 etiquetas legacy. Las 4 originales quedan aceptadas vía normalización automática (ver tabla arriba).

### B. System prompt override forzoso

Archivo nuevo: `kernel/cowork_runtime/cowork_system_prompt_override.py`. Provee el texto canónico que el orquestador debe inyectar como system prompt de Cowork. Contiene la directiva `"PROHIBIDO afirmar sin tool_call."` como contrato dura de salida.

```python
from kernel.cowork_runtime.cowork_system_prompt_override import (
    get_system_prompt_override,
    append_to_system_prompt,
    is_override_present,
)

prompt = get_system_prompt_override()
# o, si ya existe un system prompt:
prompt = append_to_system_prompt(base_prompt)
```

### C. Telemetría claim-level

`T1AuditLog.record_interception` ahora escribe, además del evento parent (response-level con el `AuditEntry`), un evento `claim_telemetry` por cada claim detectado. Cada evento incluye `claim_id`, `epistemic_label`, `license_validated`, `license_required`, `tool_call_present_this_turn`, `action_taken` (`would_block` | `would_degrade` | `would_pass`).

Reader: `T1AuditLog.iter_claim_telemetry()` y `T1AuditLog.telemetry_summary()`.

### D. Métrica T3 binaria `tool_call_present`

Archivo nuevo: `kernel/cowork_runtime/tool_call_audit.py`. Define `ToolCallContext` y la pregunta canónica binaria: *"¿hubo tool_call de evidencia (Read / Grep / Bash / WebFetch / WebSearch / MCP Supabase / MCP GitHub) en este turno?"*

El hook expone `register_tool_call(tool_name)` y `set_tool_call_ctx(ctx)` para que el orquestador alimente el contexto antes de cada `intercept()`. El audit log lo persiste por claim.

### E. Guardrail ENFORCE multi-condición

Ver §"ENFORCE legítimo — guardrail multi-condición (convergencia 7 Sabios)" arriba. Reemplaza el threshold simple por: ≥50 claims + ≥80% precision + 0 FP P2 + auditor="alfredo" + env var.

### Política inalterada (no tocada por la convergencia)

- OBSERVE-ONLY sigue siendo el default sin variables.
- Auto-ENFORCE desde OBSERVE-ONLY sigue prohibido.
- **P2 nunca bloquea**, ni siquiera en ENFORCE.
