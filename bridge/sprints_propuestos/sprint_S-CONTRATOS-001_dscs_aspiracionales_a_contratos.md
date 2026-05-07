<!-- lint_strict -->

# Sprint S-CONTRATOS-001 — Traducción de DSCs aspiracionales a contratos ejecutables

**Estado:** Propuesto
**Hilo:** Cowork (diseño + implementación) + Manus Ejecutor (validación local + push CI)
**ETA recalibrado:** 90-120 min reales con velocity demostrada
**Objetivo Maestro:** #4 (No equivocarse dos veces) + #11 (Seguridad adversarial) + #14 (Guardian de los Objetivos) + #9 (Capa 8 Memento)
**Bloqueos:** ninguno — todos los inputs (DSC-G-017 + spec_lint.py + audit_visual_diff.py + milestones/declare.py) ya están en main.
**Resultado esperado:** los 5 DSCs aspiracionales restantes (V-001, G-010, G-011, plus G-008 v2 y G-012 que este sprint cierra al integrarse al pre-commit) tienen contrato ejecutable adjunto y auto-validado.

---

## 0. Procedencia

DSC-G-017 (DSC-as-Contract, firmado 2026-05-07) re-clasifica retroactivamente como `aspiracional` cualquier DSC firmado en texto sin contrato ejecutable adjunto. La jornada 2026-05-06/07 firmó 17 DSCs; sólo 6 tienen contrato adjunto al cierre del 2026-05-07 (S-001 a S-005 cubiertos por gitleaks/trufflehog, S-006 + G-014 + G-017 cubiertos por `kernel/milestones/`, V-002 cubierto por `scripts/audit_visual_diff.py`, G-008 v2 + G-012 cubiertos por `tools/spec_lint.py`).

Los 5 DSCs aspiracionales restantes (V-001, G-010, G-011 — más eventualmente cualquier futuro DSC sin contrato) son la deuda objetivo de este sprint.

---

## 1. Audit pre-sprint — Estado actual

Lo que ya existe:

- `kernel/milestones/declare.py` + `gates.yaml` — DSC-G-014 + G-017 enforzado (commit `1787cb7`).
- `.github/workflows/milestone-declaration-guard.yml` — pendiente de push manual por Alfredo (limitación de permisos del GitHub App). Una vez pusheado, cierra el ciclo CI.
- `scripts/audit_visual_diff.py` + `tests/test_audit_visual_diff.py` — DSC-V-002 enforzado (commit `1e64605`).
- `tools/spec_lint.py` + `tests/test_spec_lint.py` — DSC-G-008 v2 + G-012 enforzado.

Lo que falta (gaps):

- Decorator `@requires_perplexity_validation` para DSC-V-001.
- Tabla `validation_log` en Supabase para registrar validaciones magna.
- GitHub Action `e2e-evidence-required.yml` para DSC-G-010.
- Migración SQL con constraint `UNIQUE(credential_id, rotated_at::date)` para DSC-G-011.

---

## 2. Tareas del Sprint

### Tarea T1 — Decorator `@requires_perplexity_validation` (DSC-V-001)

**perfil_riesgo:** write-safe

**Descripción:** Crear `kernel/validation/perplexity_decorator.py` con un decorator que envuelve cualquier función que devuelva un "hecho de mundo" (precio, modelo LLM disponible, API endpoint vigente, fecha de algo). Antes de retornar, verifica que exista un log reciente (<24h) en la tabla `validation_log` de Supabase con un timestamp coincidente con la consulta vía Perplexity. Si no, levanta `StaleClaimError`.

**Solución:**
```python
@requires_perplexity_validation(claim_type="model_availability", ttl_hours=24)
def get_current_top_llm() -> str:
    return "claude-opus-4-7"
```

**Criterios de cierre:** test `tests/test_perplexity_decorator.py` con casos (válido, expirado, ausente) en exit 0.

### Tarea T2 — Migración SQL `validation_log` (DSC-V-001 storage)

**perfil_riesgo:** write-risky

**Descripción:** Migración Supabase que crea la tabla `validation_log` con columnas (id, claim_type, claim_value_hash, perplexity_query_id, timestamp, ttl_seconds, validator).

**Criterios de cierre:** comando `supabase db diff` produce migración sin conflicto, aplicada en staging, reproducible artifact en `reports/migration_validation_log.json`.

### Tarea T3 — GitHub Action `e2e-evidence-required.yml` (DSC-G-010)

**perfil_riesgo:** write-safe

**Descripción:** Workflow que dispara en PRs cuyo título matchea `🏛️ * — DECLARADO` y verifica que el PR adjunte vía artifact upload los logs E2E con timestamps coincidentes con el push. No artifact = bloqueo de merge.

**Criterios de cierre:** PR de prueba sin artifact es bloqueado; PR con artifact pasa. Reporte JSON en `reports/e2e_evidence_check.json` por cada run.

### Tarea T4 — Constraint SQL anti-bucle de rotación (DSC-G-011)

**perfil_riesgo:** write-risky

**Descripción:** Migración Supabase que añade tabla `rotation_log(credential_id, rotated_at, by, reason)` con constraint `UNIQUE(credential_id, rotated_at::date)`. Más rate limiter que rechaza nueva rotación de la misma credencial si <72h desde la anterior, salvo override explícito firmado por Alfredo.

**Criterios de cierre:** test SQL ejecuta dos rotaciones del mismo credencial en mismo día, la segunda falla con error de constraint. Reporte en `reports/rotation_constraint_test.json`.

### Tarea T5 — Pre-commit hook `dsc-contract-check` (DSC-G-017 enforcement de futuro)

**perfil_riesgo:** write-safe

**Descripción:** Hook nuevo que detecta cuando un commit añade un archivo en `discovery_forense/CAPILLA_DECISIONES/` y verifica que el DSC tenga sección obligatoria `## Contrato ejecutable` con ruta a archivo de código existente. Si la sección está ausente, el commit se aborta o el DSC se etiqueta `aspiracional` automáticamente.

**Criterios de cierre:** test sintético: commit que añade DSC sin contrato es bloqueado; commit que añade DSC con contrato pasa. Reporte exit code en `reports/dsc_contract_check_test.json`.

### Tarea T6 — Cleanup de specs legacy y refactor a strict (DSC-G-008 v2 backfill)

**perfil_riesgo:** read-only

**Descripción:** Audit con `tools/spec_lint.py` sobre `bridge/sprints_propuestos/`, generar tabla de issues por spec, abrir 1 issue por spec con los errores estructurales y warnings de perfil_riesgo. NO modificar specs en este sprint — sólo documentar la deuda.

**Criterios de cierre:** archivo `bridge/audit_specs_legacy_2026_05_07.md` con tabla de los 15 specs y sus violaciones. Output JSON reproducible vía `python tools/spec_lint.py --json bridge/sprints_propuestos/`.

---

## 3. Contratos ejecutables que adjunta

Este sprint produce los siguientes contratos ejecutables, cumpliendo DSC-G-017 desde el origen:

| DSC | Contrato producido | Archivo |
|---|---|---|
| DSC-V-001 | decorator + tabla `validation_log` | `kernel/validation/perplexity_decorator.py` + migración SQL |
| DSC-G-010 | GitHub Action `e2e-evidence-required.yml` | `.github/workflows/e2e-evidence-required.yml` |
| DSC-G-011 | constraint SQL + rate limiter | migración SQL `rotation_log` |
| DSC-G-017 | pre-commit hook `dsc-contract-check` | `tools/dsc_contract_check.py` + `.pre-commit-config.yaml` |

---

## 4. Criterios de cierre verde (Sprint completo)

- Las 6 tareas en exit 0 con artifacts en `reports/`.
- `python tools/spec_lint.py --strict bridge/sprints_propuestos/sprint_S-CONTRATOS-001_*.md` retorna exit 0 (este spec pasa modo estricto).
- `python -m kernel.milestones.declare pipeline_tecnico_funcional` permanece en estado consistente (no se daña pipeline existente).
- Cowork audita contenido de archivos nuevos antes de declarar verde (DSC-G-008 v2).
- Sprint cierra con frase canónica: `🏛️ S-CONTRATOS-001 — DECLARADO (6/6 verde)`.

---

## 5. Owner

**Owner técnico:** Manus Ejecutor (implementación de tareas T1-T5).
**Owner arquitectónico:** Cowork (diseño + audit pre-cierre).
**Owner humano final:** Alfredo (validación de los contratos ejecutándose en su Mac antes de declarar).

---

## 6. Trazabilidad

- **Origen:** DSC-G-017 firmado 2026-05-07.
- **Sprint anterior (S-001 Security Hardening):** instaló los DSCs S-001 a S-005 con sus contratos (gitleaks + trufflehog).
- **Sprint paralelo (88.1 + 88.2 RETRY):** produjo PIPELINE TÉCNICO FUNCIONAL pero no PRODUCTO COMERCIALIZABLE — DSC-G-014 firmado bloquea declaración prematura, este sprint completa el aparato de enforcement.

---

**Firma propuesta de cierre:** sólo válida si `python -m kernel.milestones.declare` y `python tools/spec_lint.py --strict` ambos retornan exit 0 para los archivos producidos. Sin verificación reproducible local + CI, el cierre se queda en AMARILLO PARCIAL DECLARADO (DSC-G-012).
