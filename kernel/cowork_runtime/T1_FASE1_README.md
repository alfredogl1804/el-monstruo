# T1 Pre-Response Hook — Fase 1 (OBSERVE-ONLY)

Sprint: T1-FASE1-OBSERVE-ONLY · 2026-05-12 · Cowork T2 bajo autorización T1 directa.

## Qué es

Capa runtime sobre `CoworkPreResponseHook` que:

1. **Intercepta** cada output candidato de Cowork antes de Alfredo.
2. **Clasifica** cada claim por severidad **P0 / P1 / P2** y por **tag obligatorio** del contrato de salida tipado.
3. **Registra** todo en un audit log JSONL para auditoría manual a 24h.
4. **NO bloquea** en esta fase (OBSERVE-ONLY). El bloqueo solo activa en ENFORCE, y ENFORCE está protegido por triple-guardrail.

## Contrato de salida tipado

Cada afirmación sustantiva debe llevar uno de cuatro tags:

| Tag                                 | Cuándo                                                                |
| ----------------------------------- | --------------------------------------------------------------------- |
| `[VERIFICADO fuente + timestamp]`   | Hay evidencia fresca de esta sesión (Read / Grep / Bash / MCP / SQL). |
| `[INFERIDO]`                        | Inferencia razonable a partir de contexto, sin fuente binaria.        |
| `[NO VERIFICADO]`                   | Dato que no se pudo comprobar en esta sesión.                         |
| `[REQUIERE READ/SQL]`               | Claim que necesita lectura fresca y aún no se hizo.                   |

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

### ENFORCE legítimo — requiere triple-guardrail

1. Auditoría manual completada con `audit_completed=True`.
2. Al menos **50 claims P0/P1** confirmados como `true_block` por el auditor.
3. Variable `COWORK_T1_ALLOW_ENFORCE=true` exportada explícitamente.

Si cualquiera de las tres falta, `enforce_after_manual_audit()` lanza `ValueError`. **No existe API para auto-escalada por contador** (`>5 bloqueos`, `>N false_positives`, etc.) — la promoción a ENFORCE es siempre un acto humano explícito.

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

Resultado actual local: **92/92 passed** (18 legacy + 36 T1 + 38 cowork relacionados).

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
