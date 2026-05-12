---
id: cowork_to_manus_HILO_CATASTRO_SPRINT_S_CONTRATOS_001_T3_T4_T6_KICKOFF_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Catastro (libre tras CATASTRO-A v2 cierre 3/3 verde)
tipo: kickoff_split_paralelo
prioridad: P1
duracion_estimada: 45-60 min reales (3 tareas T3+T4+T6 de 6 totales del sprint)
autoridad_T1: Alfredo 2026-05-12 + veredicto Sabio externo "Split. Ahora"
autoridad_T2: Cowork T2-A firma split tras reconocer F1+F2+F3+F4
spec_firmado: bridge/sprints_propuestos/sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md
hilo_paralelo: Hilo Ejecutor 1 tomando T1+T2+T5 simultáneamente (kickoff hermano commit 00c8cb7)
punto_sincronia: post-T1+T2+T5 vs T3+T4+T6 — coordinación final cuando ambos terminen
---

# Kickoff Sprint S-CONTRATOS-001 (T3+T4+T6) — Tu mitad paralela

## §1 ¿Por qué este split existe?

Cerraste CATASTRO-A v2 con 3/3 verde + 30 suppliers (6 reales + 24 placeholders bajo DSC-V-002) en 45 min. Estás libre.

Sabio externo detectó que Cowork inicialmente recomendó "Catastro toma S-CONTRATOS-001 completo + Ejecutor 1 standby" — eso era **F1 piloto castigo post-V25 + F3 protección Ejecutor 1 + F4 heroísmo individual**. Veredicto Sabio acatado: **Split. Paralelización binaria verificable.**

**Tu mitad = T3 (GitHub Action) + T4 (constraint SQL) + T6 (cleanup specs legacy). Tu fortaleza primaria = audits + reportes estructurados + cleanup canonización.**

## §2 Documento a leer ANTES de tocar código

**Spec firmado completo:** [`bridge/sprints_propuestos/sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md`](sprints_propuestos/sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md) — 6 tareas T1-T6 verbatim.

**DSCs que cierras al ejecutar tu mitad:**
- DSC-G-010 (E2E evidence required) via GitHub Action
- DSC-G-011 (anti-bucle de rotación) via constraint SQL UNIQUE
- DSC-G-008 v2 backfill via cleanup specs legacy

## §3 Tu scope: 3 tareas (T3 + T4 + T6)

### T3 — GitHub Action `e2e-evidence-required.yml` (DSC-G-010) — 15-20 min

`.github/workflows/e2e-evidence-required.yml` (NUEVO):

```yaml
name: E2E Evidence Required (DSC-G-010)
on:
  pull_request:
    types: [opened, synchronize, ready_for_review]

jobs:
  check-e2e-evidence:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify E2E evidence in PR body
        run: |
          # PR body debe tener sección "## E2E Evidence" con al menos 1 URL o path
          # de evidencia binaria (test run, screenshot, logs Railway, etc)
          python3 tools/_check_e2e_evidence.py "${{ github.event.pull_request.body }}"
```

`tools/_check_e2e_evidence.py` (NUEVO): parsea body PR, requiere sección `## E2E Evidence` con ≥1 referencia binaria.

Tests `tests/test_e2e_evidence_check.py`: 3 casos (PR con evidence válida, PR sin sección, PR con sección vacía).

### T4 — Constraint SQL anti-bucle de rotación (DSC-G-011) — 15-20 min

Migración 0025_anti_rotation_loop.sql (verificar siguiente libre post-Ejecutor1-T2 que toma 0024):

```sql
-- DSC-G-011: prevenir bucles de rotación de credentials
ALTER TABLE public.credential_rotations
  ADD CONSTRAINT unique_rotation_per_day_per_credential
  UNIQUE (credential_id, DATE(rotated_at));
```

**ALERTA:** el original DSC-G-011 spec dice `DATE(rotated_at::date)` lo que dispara el **mismo bug IMMUTABLE** que Perplexity T2-B detectó en migration 0020 (`DATE(TIMESTAMPTZ)` es STABLE no IMMUTABLE). 

**Fix preventivo:** usar columna generada o `(credential_id, rotated_at_date)` con `rotated_at_date GENERATED ALWAYS AS (DATE(rotated_at AT TIME ZONE 'UTC')) STORED`. Aplicar lección post-V25.

Si `credential_rotations` no existe todavía, crearla idempotente + RLS. Verificar pre-flight:
```sql
SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='credential_rotations');
```

### T6 — Cleanup specs legacy + DSC-G-008 v2 backfill — 20-25 min

Tu fortaleza pura. Audit binario sobre `discovery_forense/CAPILLA_DECISIONES/` + `bridge/sprints_propuestos/`:

1. Identificar specs firmados que NO tienen sección `## Contrato ejecutable` o marcador `**Estado:** Aspiracional`
2. Para cada uno: O agregar contrato (si existe artefacto en main) O marcar explícitamente aspirational + razón
3. Update `_dsc_contracts_index.yaml` con status real fresco

Output: `bridge/manus_to_cowork_S_CONTRATOS_001_T6_CLEANUP_REPORTE_2026_05_12.md` con matriz por DSC (DSC ID | estado pre | acción tomada | estado post).

DSCs ya cubiertos (NO tocar, solo verificar): S-001/S-002/S-003/S-004/S-005 (gitleaks/trufflehog), S-006/G-014/G-017 (milestones), V-002 (audit_visual_diff.py), G-008v2/G-012 (spec_lint.py).

DSCs que esperan T6: V-001 (cerrada con T1+T2 Ejecutor1), G-010 (cerrada con T3 tuya), G-011 (cerrada con T4 tuya). El resto: revisar.

## §4 Punto de sincronía con Hilo Ejecutor 1

Ejecutor 1 toma T1 (decorator Python) + T2 (migration validation_log) + T5 (pre-commit hook dsc-contract-check).

**Tu T3+T4+T6 son SEMI-DEPENDIENTES:**
- T3 y T4 son independientes del trabajo de Ejecutor 1
- **T6 cleanup tiene posible overlap con T1/T2/T5** porque al hacer cleanup vos podrías necesitar referenciar el decorator (T1), la tabla (T2), o el hook (T5) que Ejecutor 1 crea

**Estrategia binaria:** ejecutá T3+T4 PRIMERO (independientes). Cuando termines, verificá si Ejecutor 1 ya pushó T1+T2+T5. Si sí: T6 puede referenciar sus artefactos canonizados. Si no: pausá T6 hasta que él termine, o ejecutá T6 sin referenciar V-001/G-017 (esos quedan post-Ejecutor 1).

## §5 Reglas duras NO-CRUCE (estado fresco 2026-05-12)

| Path | Tu permiso | Ejecutor 1 permiso |
|---|---|---|
| `.github/workflows/e2e-evidence-required.yml` | **TUYO T3** | NO tocar |
| `tools/_check_e2e_evidence.py` | **TUYO T3** | NO tocar |
| `migrations/sql/0025_*.sql` (UNIQUE rotation) | **TUYO T4** | NO tocar |
| `discovery_forense/CAPILLA_DECISIONES/*.md` modificaciones | **TUYO T6** | NO tocar |
| `_dsc_contracts_index.yaml` | **TUYO T6** | NO tocar |
| `kernel/security/validation.py` | NO tocar | **EJECUTOR 1 T1** |
| `migrations/sql/0024_*.sql` (validation_log) | NO tocar | **EJECUTOR 1 T2** |
| `.pre-commit-config.yaml` | NO tocar | **EJECUTOR 1 T5** |
| `tools/_check_dsc_contracts.py` | NO tocar | **EJECUTOR 1 T5** |

5 hilos activos. **NO tocar:**
1. **PR #114** (Ejecutor 1 MOBILE-REALIGNMENT) — en audit T2-B convergencia
2. **PR #110** Perplexity — `kernel/cowork_runtime/`
3. **Ejecutor 2 ROTOR-001 PR** abriendo — `kernel/rotor/`, kernel embrion_*
4. **apps/mobile/** — territorio Ejecutor 1

## §6 Pre-flight obligatorio

```bash
cd ~/el-monstruo && git status && git pull origin main
ls migrations/sql/ | sort | tail -5
# Esperado: 0021/0022/0023 existen. Ejecutor1 toma 0024. Tu T4 toma 0025.
# Verificar credential_rotations tabla:
psql "$SUPABASE_DB_URL" -c "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='credential_rotations');"
# Si NO existe, T4 también debe crearla idempotente
grep -rn "credential_rotations\|rotation_loop" kernel/ | head -10
```

## §7 Permiso de merge

- **T3+T4+T6 cerradas:** PR limpio `[S-CONTRATOS-001-T3-T4-T6]` o coordinás con Ejecutor 1 PR único `[S-CONTRATOS-001-COMPLETO]` si vos cerrás último
- **Audit:** Cowork T2-A audita DSC-G-008 v2 + consulta PBA → T2-B antes de merge
- **Self-merge prohibido**

## §8 Embrion_memoria al cerrar tu mitad

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'S-CONTRATOS-001 T3+T4+T6 cerradas por Hilo Catastro. GitHub Action e2e-evidence-required + migration 0025 unique rotation per day + cleanup specs legacy con DSC-G-008 v2 backfill operativos. DSC-G-010 + DSC-G-011 + G-008v2 backfill cierran como contratos ejecutables. Pendiente: Ejecutor 1 T1+T2+T5 + merge final.',
  'manus-hilo-catastro',
  8
);
```

## §9 Autoridad y cierre

- T1 (Alfredo) ordenó split tras veredicto Sabio externo
- T2-A (Cowork) firma split tras reconocer F1+F2+F3+F4
- T3 (Hilo Catastro) ejecuta autónomamente bajo reglas duras §5
- ETA realista: 45-60 min (3 tareas mixtas, tu skill nativo audits + GitHub Action es CI básico)

## §10 Honestidad anti-autoboicot reforzada

Aplica regla anti-autoboicot canonizada por vos mismo en STASHES-FORENSIC-001 y reforzada en CATASTRO-A v2 (3-6 suppliers reales + 24 placeholders DSC-V-002):

- Si T3 GitHub Action te traba (CI YAML poco familiar), reportá honesto al bridge
- Si T4 constraint SQL te confunde, pausá y consulta Cowork — la lección DATE(TIMESTAMPTZ) IMMUTABLE de migration 0020 aplica acá
- Si T6 cleanup detectás drift mayor en DSCs, reportá antes de modificar — algunos DSCs pueden requerir firma T1 retroactiva

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 06:30 UTC

**Split paralelo decisión binaria post-veredicto Sabio externo. Paralelización binaria verificable + punto de sincronía único al final.**
