---
id: cowork_to_manus_HILO_CATASTRO_SPRINT_S_CONTRATOS_001_KICKOFF_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Catastro (libre tras CATASTRO-A v2 cierre 3/3 verde)
tipo: kickoff_OVERRIDE_post_convergencia_sabios
prioridad: P1
duracion_estimada: 90-120 min reales (sprint completo 6 tareas)
autoridad_T1: Alfredo 2026-05-12 (consultó 3 Sabios externos)
autoridad_T2: Cowork T2-A firma override del split previo bajo convergencia 2/3 Sabios externos
spec_firmado: bridge/sprints_propuestos/sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md
hilo_paralelo: Hilo Ejecutor 1 en STANDBY ACTIVO con 4 tareas no interferentes (kickoff hermano post)
kickoff_previo_OVERRIDE: commit 51ca79f (T3+T4+T6 split) → ESTE override toma scope COMPLETO T1-T6
---

# Kickoff Sprint S-CONTRATOS-001 COMPLETO — Catastro toma scope end-to-end

## §1 ¿Por qué este kickoff override existe?

Cerraste CATASTRO-A v2 con calidad ejemplar (3/3 verde + 30 suppliers DSC-V-002).

Cowork T2-A consultó Sabio externo 1 que recomendó SPLIT del sprint S-CONTRATOS-001 entre vos y Ejecutor 1. **Pusheé kickoffs split** (commits `00c8cb7` Ejecutor 1 + `51ca79f` vos).

**Alfredo T1 consultó 2 Sabios más** posteriormente. Veredicto binario:

| Sabio | Veredicto |
|---|---|
| Sabio 1 (primero) | SPLIT entre 2 hilos paralelos |
| **Sabio 2** (segundo) | **NO SPLIT** — Catastro completo + Ejecutor 1 standby activo |
| **Sabio 3** (tercero) | **NO SPLIT** — Catastro completo + Ejecutor 1 standby |

**Convergencia 2/3 a favor de NO-SPLIT.** Razón canónica binaria de Sabios 2+3:

> "S-CONTRATOS-001 es sprint de **integridad contractual con superficies acopladas** (decorator + SQL migration + GitHub Action + pre-commit hook + cleanup legacy). Partirlo entre 2 hilos justo después de V25 epistemológico introduce riesgo de divergencia semántica."

**Tomás S-CONTRATOS-001 COMPLETO end-to-end.** Ejecutor 1 queda en standby activo con 4 tareas no interferentes (preparar checklist T7 PR #114 + lectura S-CONTRATOS riesgos + comandos Mac Alfredo + revisión kernel-pura).

## §2 Documento a leer ANTES de tocar código

**Spec firmado completo:** [`bridge/sprints_propuestos/sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md`](sprints_propuestos/sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md) — 6 tareas T1-T6 verbatim. ETA spec: 90-120 min reales.

**5 DSCs aspiracionales que cerrás como contratos ejecutables:**
- DSC-V-001 (Validación Magna obligatoria) via T1 decorator + T2 table
- DSC-G-010 (E2E evidence required) via T3 GitHub Action
- DSC-G-011 (anti-bucle de rotación) via T4 constraint SQL
- DSC-G-017 (DSC-as-Contract enforcement) via T5 pre-commit hook
- DSC-G-008 v2 backfill via T6 cleanup specs legacy

## §3 Tu scope COMPLETO: 6 tareas T1-T6

### T1 — Decorator `@requires_perplexity_validation` (DSC-V-001) — 15-20 min

`kernel/security/validation.py` (NUEVO archivo):

```python
def requires_perplexity_validation(claim_id: str):
    """Decorator: la función NO se ejecuta sin record_validation reciente para claim_id."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            recent = await query_latest_validation(claim_id, max_age_minutes=15)
            if recent is None:
                raise RuntimeError(
                    f"DSC-V-001 violation: function {func.__name__} requires "
                    f"recent validation for claim '{claim_id}'."
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

Tests `tests/test_validation_decorator.py`: 3 casos (decorator bloquea sin validation, decorator pasa con validation reciente, decorator rechaza validation >15min).

### T2 — Migration SQL `validation_log` (DSC-V-001 storage) — 15-20 min

Migración 0024_validation_log.sql:

```sql
CREATE TABLE IF NOT EXISTS public.validation_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    claim_id TEXT NOT NULL,
    validator TEXT NOT NULL,
    evidence_url TEXT,
    evidence_jsonb JSONB,
    expires_at TIMESTAMPTZ NOT NULL,
    valid BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_validation_log_claim_id_recent
    ON public.validation_log (claim_id, created_at DESC);

ALTER TABLE public.validation_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS validation_log_service_role_only
    ON public.validation_log FOR ALL TO service_role USING (true);
```

Apply post-merge con `scripts/_apply_migration_0024.py`. Bajo DSC-S-012, migration en main ANTES de apply prod.

### T3 — GitHub Action `e2e-evidence-required.yml` (DSC-G-010) — 15-20 min

`.github/workflows/e2e-evidence-required.yml` (NUEVO) — verifica PR body tenga sección `## E2E Evidence` con ≥1 URL/path binario. `tools/_check_e2e_evidence.py` (NUEVO) parser.

Tests `tests/test_e2e_evidence_check.py`: 3 casos.

### T4 — Constraint SQL anti-bucle de rotación (DSC-G-011) — 15-20 min

Migración 0025_anti_rotation_loop.sql.

**⚠️ ALERTA CRÍTICA — Lección post-V25 migration 0020:**

El spec original DSC-G-011 dice `UNIQUE(credential_id, DATE(rotated_at::date))` lo que **dispara el mismo bug IMMUTABLE** que Perplexity T2-B detectó: `DATE(TIMESTAMPTZ)` tiene `provolatile='s'` (STABLE), NO IMMUTABLE en Postgres. NO usar `DATE()` directo en CREATE INDEX/UNIQUE.

**Fix preventivo:** columna generada IMMUTABLE:

```sql
-- Si credential_rotations NO existe, crearla:
CREATE TABLE IF NOT EXISTS public.credential_rotations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    credential_id TEXT NOT NULL,
    rotated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    rotated_at_date DATE GENERATED ALWAYS AS ((rotated_at AT TIME ZONE 'UTC')::date) STORED,
    metadata JSONB
);

ALTER TABLE public.credential_rotations
    ADD CONSTRAINT IF NOT EXISTS unique_rotation_per_day_per_credential
    UNIQUE (credential_id, rotated_at_date);
```

RLS service_role_only desde nacimiento.

### T5 — Pre-commit hook `dsc-contract-check` (DSC-G-017 enforcement) — 15-20 min

`.pre-commit-config.yaml` append + `tools/_check_dsc_contracts.py` (NUEVO) verifica cada DSC firmado tenga contrato O marcador aspiracional. Exit 1 si DSC firmado sin nada.

### T6 — Cleanup specs legacy + DSC-G-008 v2 backfill — 20-25 min

Audit binario sobre `discovery_forense/CAPILLA_DECISIONES/` + `bridge/sprints_propuestos/`:

1. Identificar specs firmados sin `## Contrato ejecutable` ni `**Estado:** Aspiracional`
2. Para cada uno: agregar contrato (si existe artefacto) O marcar explícitamente aspirational + razón
3. Update `_dsc_contracts_index.yaml` con status fresco

DSCs ya cubiertos (NO tocar): S-001/S-002/S-003/S-004/S-005 (gitleaks), S-006/G-014/G-017 (milestones), V-002 (audit_visual_diff.py), G-008v2/G-012 (spec_lint.py).

DSCs que cierran con tu sprint: V-001 (T1+T2), G-010 (T3), G-011 (T4), G-017 (T5 enforcement), G-008 v2 backfill (T6).

**Output:** `bridge/manus_to_cowork_S_CONTRATOS_001_T6_CLEANUP_REPORTE_2026_05_12.md` con matriz por DSC (ID | estado pre | acción | estado post).

## §4 Reglas duras NO-CRUCE

5 hilos activos. **NO tocar:**

1. **PR #114** (Ejecutor 1 MOBILE-REALIGNMENT) — en audit T2-B convergencia
2. **PR #110** Perplexity — `kernel/cowork_runtime/`
3. **Ejecutor 2 ROTOR-001 PR** abriendo — `kernel/rotor/`, kernel embrion_*
4. **apps/mobile/** — territorio Ejecutor 1
5. **Ejecutor 1 standby activo** — está leyendo `bridge/sprints_propuestos/sprint_S-CONTRATOS-001*.md` produciendo lista de riesgos. NO toca código. NO bloquea tu trabajo

## §5 Pre-flight obligatorio

```bash
cd ~/el-monstruo && git status && git pull origin main
ls migrations/sql/ | sort | tail -5
# Esperado: 0021/0022/0023 existen (S89 v2 + ROTOR). Tus T2 y T4 usan 0024 + 0025.

psql "$SUPABASE_DB_URL" -c "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='credential_rotations');"
# Si NO existe, T4 también crea la tabla idempotente.

psql "$SUPABASE_DB_URL" -c "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='validation_log');"
# Esperado: false (T2 la crea).

grep -rn "record_validation\|requires_perplexity_validation" kernel/ | head -10
# Si existe implementación previa, leela primero. NO inventes.
```

Si pre-flight rojo, reportá al bridge antes de codear (regla anti-autoboicot que vos canonizaste).

## §6 Permiso de merge

- PR limpio con tag `[S-CONTRATOS-001]`
- Cowork T2-A audita DSC-G-008 v2 + consulta PBA → T2-B antes de merge (write-risky: migrations SQL + decorator security + pre-commit hook)
- Self-merge prohibido

## §7 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint S-CONTRATOS-001 CERRADO por Hilo Catastro. 5 DSCs aspiracionales → contratos ejecutables: V-001 (decorator + validation_log), G-010 (e2e-evidence GitHub Action), G-011 (UNIQUE rotation_per_day constraint sin bug IMMUTABLE), G-017 (dsc-contract-check pre-commit hook), G-008 v2 backfill (cleanup specs legacy). Migración 0024 + 0025 aplicadas idempotentes. 18+ tests verde. 65 DSCs canonizados → 70 (con contratos ejecutables todos los 5 nuevos).',
  'manus-hilo-catastro',
  9
);
```

## §8 Autoridad y cierre

- T1 (Alfredo) ordenó cambio post-Sabios 2+3 convergencia
- T2-A (Cowork) firma override del split previo bajo convergencia 2/3
- T3 (Hilo Catastro) ejecuta S-CONTRATOS-001 COMPLETO end-to-end
- ETA realista: 90-120 min reales

## §9 Honestidad anti-autoboicot reforzada

Lección post-V25 migration 0020 + post-Sabios:
- **T4 constraint SQL:** lección DATE(TIMESTAMPTZ) IMMUTABLE — usá columna generada STORED, no DATE() directo
- **T6 cleanup:** si detectás DSC que requiere firma T1 retroactiva, reportá al bridge antes de modificar
- **Integridad contractual:** este sprint es sobre coherencia. Si en alguna tarea sentís que "el aprendizaje se contradice con el spec firmado", parate y reportá. NO inventés reconciliación.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 06:50 UTC

**Override binario post-convergencia 2/3 Sabios externos. Catastro toma scope contractual completo coherente. Ejecutor 1 standby activo no interferente. El Monstruo aplica par bicéfalo + Sabios externos como guardrails estructurales.**
