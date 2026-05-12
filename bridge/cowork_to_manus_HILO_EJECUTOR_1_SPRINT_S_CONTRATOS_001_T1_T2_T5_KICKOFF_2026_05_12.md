---
id: cowork_to_manus_HILO_EJECUTOR_1_SPRINT_S_CONTRATOS_001_T1_T2_T5_KICKOFF_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 1 (libre tras PR #114 MOBILE-REALIGNMENT-001 en audit T2-B)
tipo: kickoff_split_paralelo
prioridad: P1
duracion_estimada: 45-60 min reales (3 tareas T1+T2+T5 de 6 totales del sprint)
autoridad_T1: Alfredo 2026-05-12 ("hilo ejecutor 1 y catastro esperan tareas grandes estan libres" + veredicto Sabio externo "Split. Ahora")
autoridad_T2: Cowork T2-A firma split tras reconocer F1+F2+F3+F4 detectadas por Sabio externo
spec_firmado: bridge/sprints_propuestos/sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md (Estado Propuesto, scope verbatim adoptado)
hilo_paralelo: Hilo Catastro tomando T3+T4+T6 simultáneamente (kickoff hermano commit pareado)
punto_sincronia: post-T1+T2+T5 vs T3+T4+T6 — coordinación final cuando ambos hilos terminen sus 3 tareas
---

# Kickoff Sprint S-CONTRATOS-001 (T1+T2+T5) — Tu mitad paralela

## §1 ¿Por qué este split existe?

Cerraste MOBILE-REALIGNMENT-001 (PR #114) con velocity ejemplar (Flutter nuevo dominio + 13/13 tests + honestidad operativa sobre force-push de otro hilo). Estás libre.

Catastro también está libre tras Catastro-A v2 (3/3 verde + 30 suppliers DSC-V-002).

Sabio externo consultado por Alfredo T1 detectó que mi recomendación inicial ("Catastro solo + Ejecutor 1 standby") era **F1 piloto automático de castigo post-V25 + F3 protección maternal sobre vos + F4 heroísmo individual sobre paralelización**. Veredicto Sabio: *"Split. Ahora. El Monstruo no es eficiente con héroes; es eficiente con paralelización binaria verificable."*

Alfredo T1 acató veredicto. Procedo con split.

**Tu mitad = T1 (decorator Python) + T2 (migration SQL) + T5 (pre-commit hook). Kernel puro = tu territorio nativo.**

## §2 Documento a leer ANTES de tocar código

**Spec firmado completo:** [`bridge/sprints_propuestos/sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md`](sprints_propuestos/sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md) — 6 tareas T1-T6 con scope verbatim.

**DSCs que cierras al ejecutar tu mitad:**
- DSC-V-001 (Validación Magna obligatoria) via decorator + table validation_log
- DSC-G-017 (DSC-as-Contract) via pre-commit hook anti-stale-DSC

## §3 Tu scope: 3 tareas (T1 + T2 + T5)

### T1 — Decorator `@requires_perplexity_validation` (DSC-V-001) — 15-20 min

`kernel/security/validation.py` (NUEVO archivo o append a existente):

```python
def requires_perplexity_validation(claim_id: str):
    """Decorator: la función NO se ejecuta sin record_validation reciente para claim_id."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar en validation_log la última validación de claim_id
            recent = await query_latest_validation(claim_id, max_age_minutes=15)
            if recent is None:
                raise RuntimeError(
                    f"DSC-V-001 violation: function {func.__name__} requires "
                    f"recent validation for claim '{claim_id}'. "
                    f"Call record_validation({claim_id}, ...) within last 15 min first."
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

Tests `tests/test_validation_decorator.py`: 3 casos (decorator bloquea sin validation, decorator pasa con validation reciente, decorator rechaza validation >15min).

### T2 — Migration SQL `validation_log` (DSC-V-001 storage) — 15-20 min

Migración 0024_validation_log.sql (verificar siguiente número libre con `python3 scripts/_check_migration_gaps.py 2>/dev/null || ls migrations/sql/ | tail -3`):

```sql
CREATE TABLE IF NOT EXISTS public.validation_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    claim_id TEXT NOT NULL,
    validator TEXT NOT NULL,  -- 'perplexity' | 'gemini_pro' | 'opus' | etc
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

Apply con `scripts/_apply_migration_NNNN.py` post-merge.

### T5 — Pre-commit hook `dsc-contract-check` (DSC-G-017 enforcement) — 15-20 min

`.pre-commit-config.yaml` append + hook nuevo:

```yaml
- repo: local
  hooks:
    - id: dsc-contract-check
      name: dsc-contract-check (DSC-G-017)
      entry: python3 tools/_check_dsc_contracts.py
      language: system
      pass_filenames: true
      files: 'discovery_forense/CAPILLA_DECISIONES/.*\.md$'
```

`tools/_check_dsc_contracts.py` (NUEVO): verifica que cada DSC firmado tenga:
- Header `**estado:** firme`
- Sección `## Contrato ejecutable` con path al artefacto
- O explícitamente `**Estado:** Aspiracional` con razón

Si DSC firmado sin contrato y sin marcador aspirational → exit 1.

Tests: 3 casos (DSC válido con contrato, DSC válido aspiracional, DSC rojo sin nada).

## §4 Punto de sincronía con Hilo Catastro

Catastro toma T3 (GitHub Action) + T4 (constraint SQL) + T6 (cleanup specs legacy).

**Tu T1+T2+T5 son INDEPENDIENTES del pipeline T3→T4 de Catastro.** Cero overlap esperado.

**ÚNICO punto de overlap potencial:** archivos compartidos. Reglas duras NO-CRUCE:

| Path | Tu permiso | Catastro permiso |
|---|---|---|
| `kernel/security/validation.py` | **TUYO T1** | NO tocar |
| `migrations/sql/0024_*.sql` | **TUYO T2** | NO tocar |
| `.pre-commit-config.yaml` | **TUYO T5** | NO tocar (Catastro NO modifica .pre-commit-config) |
| `tools/_check_dsc_contracts.py` | **TUYO T5** | NO tocar |
| `.github/workflows/e2e-evidence-required.yml` | NO tocar | **CATASTRO T3** |
| `migrations/sql/0025_*.sql` (UNIQUE rotation) | NO tocar | **CATASTRO T4** |
| `discovery_forense/CAPILLA_DECISIONES/*.md` modificaciones | NO tocar | **CATASTRO T6** |

**Si vos terminás antes que Catastro:** notificá al bridge `bridge/manus_to_cowork_S_CONTRATOS_001_T1_T2_T5_DONE_2026_05_12.md` con commits. Catastro completa su mitad y luego ambos coordinan PR final unificado.

**Si Catastro termina antes que vos:** él notifica al bridge, vos completás.

## §5 Reglas duras NO-CRUCE (estado fresco 2026-05-12)

5 hilos activos. **NO tocar:**

1. **PR #114** (tu propio MOBILE-REALIGNMENT) — en audit T2-B convergencia
2. **PR #110** (Perplexity feat/t1-pre-response-hook-observe-only) — `kernel/cowork_runtime/`
3. **Ejecutor 2 ROTOR-001** PR abriendo — `kernel/rotor/`, `kernel/embrion_loop.py`, `kernel/embrion_budget.py`, `kernel/embrion_scheduler.py`, `kernel/embrion_routes.py`
4. **Hilo Catastro paralelo** — sus 3 tareas T3+T4+T6 (ver §4)
5. **apps/mobile/** — territorio que acabás de cerrar, no tocar

## §6 Pre-flight obligatorio

```bash
cd ~/el-monstruo && git status && git pull origin main
# Verificar siguiente migration number libre:
ls migrations/sql/ | sort | tail -5
# Esperado: 0021, 0022, 0023 ya existen (S89 v2 + ROTOR). Tu T2 usa 0024.
# Verificar que record_validation function NO existe ya:
grep -rn "record_validation\|requires_perplexity_validation" kernel/ | head -10
# Si encontrás implementación existente — leela primero, no inventes.
```

Si encontrás drift (ej: migration 0024 ya existe), reportá al bridge antes de codear.

## §7 Permiso de merge

- **T1+T2+T5 cerradas:** PR limpio `[S-CONTRATOS-001-T1-T2-T5]` o coordinás con Catastro un PR único `[S-CONTRATOS-001-COMPLETO]` si vos cerrás último
- **Audit:** Cowork T2-A audita DSC-G-008 v2 + consulta PBA → T2-B antes de merge (write-risky)
- **Self-merge prohibido**

## §8 Embrion_memoria al cerrar tu mitad

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'S-CONTRATOS-001 T1+T2+T5 cerradas por Ejecutor 1. Decorator @requires_perplexity_validation + migration 0024 validation_log + pre-commit hook dsc-contract-check operativos. DSC-V-001 + DSC-G-017 cierran como contratos ejecutables. Pendiente: Catastro T3+T4+T6 + merge final.',
  'manus-hilo-ejecutor-1',
  8
);
```

## §9 Autoridad y cierre

- T1 (Alfredo) ordenó split tras veredicto Sabio externo
- T2-A (Cowork) firma split reconociendo F1+F2+F3+F4 detectadas
- T3 (Ejecutor 1) ejecuta autónomamente bajo reglas duras §5
- ETA realista: 45-60 min reales (3 tareas Python+SQL+hook, tu skill nativo)

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 06:30 UTC

**Split paralelo decisión binaria post-veredicto Sabio externo. Cero héroes solitarios. Paralelización binaria verificable + punto de sincronía único al final.**
