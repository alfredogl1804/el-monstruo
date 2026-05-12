---
sprint_id: COWORK-MEMENTO-001
nombre: Claim calibration retrospectiva — pieza 1 anti-Dory
fecha_drafting: 2026-05-12T15:30:00Z
autor_borrador: Cowork T2-A Arquitecto Orquestador
firmante_propuesto: T1 Alfredo Góngora
owner_ejecucion: Manus Hilo Ejecutor 1 (manus_hilo_a, cuenta apple)
prioridad: P0 magna (prerequisite estructural anti-Dory)
estado: BORRADOR — pendiente firma T1
secuencia_anti_dory:
  - PIEZA_1_AHORA: MEMENTO-001 (este sprint) — claim calibration retrospectiva
  - PIEZA_2_PARALELO: MURALLA-001 — state digest auto-inyectado
  - PIEZA_3_POST_DATOS: CRUZ-001 — cross-validation hilo-a-hilo
  - PIEZA_4_FINAL: VERIFICADOR-001 — verification gates pre-emit
diagnostico_dory_atacado:
  - D2 no-transfer cross-dominio (parcial)
  - D3 asimetría costo verificar vs afirmar (parcial — vía datos para iterar harness)
dsc_enforced:
  - DSC-V-001 (validación claims estado-del-mundo)
  - DSC-S-006 v1.1 (RLS por defecto)
  - DSC-S-012 (anti-deriva migraciones)
  - DSC-S-016 (anti-fabricación causalidad sin grep)
  - DSC-G-008 v3 (deducción consecuencias materiales §4)
  - DSC-G-017 (DSC-as-Contract)
  - DSC-MO-006 v1.1 (PBA permanente)
  - F24 (spec firmado con datos no verificados pre-firma) — anti-F24 declarado abajo
  - F26 (doctrina markdown sin enforcement código) — este sprint ES código, no doctrina
  - F27 (reporte verde sin reproducir audit binario) — frase canónica condicional
fuente_doctrinal_intelectual:
  - Opus 4.7 Thinking Ronda 1 — bridge/sabio_OPUS_4_7_THINKING_response_ronda_1_2026_05_12.md Entregable A + Dirección 4
  - Kimi K2.6 Thinking Ronda 1 — Proposal-2 (causality validator) + Proposal-12 (hook audit) — subsets de este sprint
  - Síntesis Cowork T2-A — bridge/cowork_T2A_RECONOCIMIENTO_OPUS_MAGNO_RECOMENDACION_T1_2026_05_12.md
---

# Sprint COWORK-MEMENTO-001 — Claim calibration retrospectiva

## §0 Contexto y por qué

### §0.1 Síndrome de Dory diagnosticado (Opus 4.7 Entregable A)

El síndrome de Dory que afecta a Cowork (modelo Claude) tiene 3 dimensiones independientes que se componen:

- **D1 — Memoria efímera cross-sesión.** PARCIALMENTE resuelto vía `session_memory` + `embrion_memoria` + Pre-flight Memento.
- **D2 — No-transfer cross-dominio dentro de sesión.** Que Cowork haya sido corregido en migrations no transfiere a tablas ni a paths. **NO resuelto**.
- **D3 — Asimetría costo verificar vs afirmar en tiempo de generación.** El sampler premia fluency sobre verification. Pattern-matching predictivo "se siente como conocimiento". **NO resuelto, raíz dura**.

**MEMENTO-001 ataca D2 + D3 vía datos** — recolectando claims factuales emitidos por Cowork con `verification_status`, creando dataset retrospectivo para iterar harness con evidencia (no hipótesis).

### §0.2 Cita verbatim Opus 4.7 Thinking — Dirección 4

> *"Telemetría de calibration retrospectiva como simulador. Cada afirmación factual de Cowork se loguea con `claim_type`, `claim_value`, `verification_status` (verified-pre / verified-post-match / verified-post-mismatch / unverified). Agregado diario. Este dataset sirve simultáneamente como input para iterar prompt engineering con evidencia, no con hipótesis; ground-truth para evaluar cualquier mitigación nueva; fuente de la calibración necesaria. **Esta es la que recomiendo primero. Sin ella, todas las demás son cocción de hipótesis y la decisión de qué construir queda anclada a la intuición del agente que está fallando.**"*

### §0.3 Por qué este sprint NO duplica AUTO-DISCIPLINE-REAL-001 (PR #118)

- **AUTO-DISCIPLINE** = detección post-hoc de 10 F21 patterns regex en output ya generado + hook bloqueo
- **MEMENTO-001** = **logging granular** de toda afirmación factual (incluso las que pasan AUTO-DISCIPLINE) con verificación binaria post-hoc + dataset retrospectivo
- AUTO-DISCIPLINE responde "¿hay F21 ahora?" en runtime. MEMENTO responde "¿qué F21 cometí realmente en los últimos 7 días, agregado por dominio?"
- Son complementarios: MEMENTO usa hook decisions + claim extraction independiente para alimentar dataset

### §0.4 12 F21 reincidentes HOY justifican magnitud del sprint

Día 2026-05-12: 12 instancias F21 detectadas en sesión Cowork de ~13h. Patrón común: paths/tablas/columnas/migrations/PRs/cifras afirmados sin tool call previo en turno activo. MEMENTO crea el dataset que valida o invalida cualquier mitigación futura propuesta.

---

## §1 Objetivo magno + métrica éxito

### §1.1 Objetivo

Implementar **enforcement runtime kernel REAL** (no doctrina markdown) que registra cada afirmación factual de Cowork con `verification_status` binario, exponiendo dataset retrospectivo para iterar el sistema con evidencia.

### §1.2 Métrica éxito binaria

**Post-merge + 7 días operación normal:**

1. ≥80% de afirmaciones factuales Cowork tienen entry en `cowork_claims_calibration` (cobertura)
2. CLI report `python3 -m tools.cowork_calibration_report --days 7` retorna agregado por `claim_type` con breakdown: verified-pre / verified-post-match / verified-post-mismatch / unverified
3. Dataset permite responder pregunta: **"¿cuántas F21 cometí en los últimos 7 días, por categoría?"** con número binario, no estimación
4. Cero secrets/credenciales en tabla (validation_log pattern)
5. Tests integration 100% PASS

**NO-métrica (anti-Goodhart):**

- NO objetivo: "reducir F21 a X%" — esa decisión espera tener dataset primero
- NO objetivo: "bloquear todos los claims unverified" — eso es VERIFICADOR-001 (PIEZA 4), no MEMENTO

---

## §2 Scope

### §2.1 ENTRA en scope

- Migration 0028 `cowork_claims_calibration` tabla nueva con RLS + DO block (igual patrón 0027)
- Module Python `kernel/cowork_runtime/claim_calibration.py` (~200 LOC) con clase `ClaimLogger`
- Integración hook `pre_response_hook.py` entre nuevos markers `CLAIM_CALIBRATION_BEGIN/END` (backward compat 100%, igual patrón AUTO-DISCIPLINE markers)
- CLI report tool `tools/cowork_calibration_report.py` con flags `--days`, `--output`, `--claim-type-filter`
- Tests pytest `tests/test_cowork_claim_calibration.py` cubriendo extract_claims regex, log_claim insert, aggregate_daily counts, verification_status transitions
- Postmortem + reporte cierre Manus
- DSC-G-008 v3 §4 audit estructura completa pre/post

### §2.2 NO entra en scope (explícito anti-F24)

- NO bloqueo runtime de output (eso es VERIFICADOR-001, PIEZA 4 futura)
- NO modificación del decision flow Cowork (solo logging)
- NO pgvector ni embeddings (PIEZA futura COWORK-SEMANTIC-MEMORY-001)
- NO modificar `session_memory.py` ni `f21_patterns.py` ni `antipatterns.py`
- NO touching `rule_reinjection.py` ni `companion_agent.py` ni `drift_detector.py`
- NO cambiar regla evolucionada del merge ni DSCs existentes
- NO añadir Sabios consultations adicionales (Opus crítica magna)
- NO doctrina markdown nueva más allá de este spec + DSC referenciado (F26 respeto)

---

## §3 Estado kernel binario verificado pre-firma (anti-F24)

**Verificación ejecutada 2026-05-12 ~15:30 UTC por Cowork T2-A pre-drafting spec:**

### §3.1 Migrations disponibles en main

```bash
$ ls migrations/sql/ | sort | tail -3
0025_anti_rotation_loop.sql
0026_embrion_homeostasis_log.sql
0027_cowork_protocolo_invocaciones.sql  # branch #118 — ya aplicada Supabase prod HOY
```

**ASUNCIÓN DECLARADA:** migration MEMENTO-001 = **0028** ASUMIENDO PR #118 mergeado a main pre-arranque sprint. Si #118 NO mergeado al T1 del sprint, **Ejecutor 1 verifica `ls migrations/sql/ | sort | tail -1` y usa el siguiente libre**, documentando divergencia verbatim en migration comment (patrón canonizado AUTO-DISCIPLINE-REAL-001 T1). Esta cláusula respeta DSC-S-012 anti-deriva.

### §3.2 kernel/cowork_runtime/ archivos existentes (verificados binariamente)

```
__init__.py
alfredo_veto_channel.py     294 LOC
antipatterns.py             199 LOC  (NUEVO PR #118 — disponible post-merge)
companion_agent.py          498 LOC
drift_detector.py           257 LOC
f21_patterns.py             295 LOC  (NUEVO PR #118 — disponible post-merge)
pre_response_hook.py        674 LOC  (modificado PR #118 con markers BEGIN/END)
rule_reinjection.py         396 LOC
session_memory.py           481 LOC
```

**Archivo a CREAR:** `kernel/cowork_runtime/claim_calibration.py` (~200 LOC) — NO existe en main ni en branch #118.

### §3.3 tools/ existentes

```
tools/_check_cowork_verbatim_citations.py  (NUEVO PR #118 — disponible post-merge)
tools/cowork_guardian.py                   (existing pre-PR-90 — 22 reglas F1-F22)
```

**Archivo a CREAR:** `tools/cowork_calibration_report.py` (~150 LOC) — NO existe.

### §3.4 tests/ existentes

```
tests/test_cowork_auto_discipline_integration.py  (NUEVO PR #118)
tests/test_cowork_companion_agent.py
tests/test_cowork_drift_detector.py
tests/test_cowork_pre_response_hook.py
tests/test_cowork_routes.py
```

**Archivo a CREAR:** `tests/test_cowork_claim_calibration.py` (~150 LOC) — NO existe.

### §3.5 cowork_sesiones schema verificado vía Supabase MCP

```
id                                   uuid          NOT NULL  PRIMARY KEY
fecha_inicio                         timestamptz   NOT NULL
fecha_fin                            timestamptz   YES
duracion_minutos                     integer       YES
turnos_totales                       integer       NOT NULL
pre_flight_ejecutado                 boolean       NOT NULL
commits_productivos                  integer       NOT NULL
violaciones_detectadas               jsonb         NOT NULL
palabras_clave_alfredo               jsonb         NOT NULL
correctivos_recibidos                jsonb         NOT NULL
deudas_pendientes_proxima_sesion     jsonb         NOT NULL
resumen_lecciones                    text          YES
sprint_activo                        text          YES
kernel_version                       text          YES
embrion_ultimo_latido                timestamptz   YES
created_at                           timestamptz   NOT NULL
updated_at                           timestamptz   NOT NULL
```

FK soft a `cowork_sesiones.id` será nullable para invocaciones standalone CLI.

---

## §4 Tareas T0-T8

### T0 — Audit pre-sprint binario (Ejecutor 1 inicial, ~10m)

Reproducir verificaciones §3 + adicional:
- `ls migrations/sql/ | sort | tail -1` para confirmar número migration real
- `python3 -c "from kernel.cowork_runtime.f21_patterns import F21_PATTERNS; print(len(F21_PATTERNS))"` debe retornar 10
- `python3 -c "from kernel.cowork_runtime.antipatterns import ALL_ANTIPATTERN_IDS; print(len(ALL_ANTIPATTERN_IDS))"` debe retornar 27
- Documentar cualquier divergencia spec↔realidad en `reports/cowork_memento_pre_sprint_audit.json`

**Output T0:** archivo JSON con discrepancias o "discrepancies: []".

### T1 — Migration 0028 con RLS + DO block (Ejecutor 1, ~20m)

Crear `migrations/sql/0028_cowork_claims_calibration.sql` (~95 LOC) siguiendo plantilla migration 0027:

- `CREATE TABLE IF NOT EXISTS public.cowork_claims_calibration` con columnas §5
- 4-5 índices (`session_uuid+turn_index`, `created_at DESC`, `claim_type+verification_status+created_at DESC`, `verification_status+created_at DESC WHERE verification_status='unverified'`)
- COMMENT ON TABLE + COMMENT ON COLUMN
- ALTER TABLE ENABLE ROW LEVEL SECURITY
- DROP+CREATE POLICY `cowork_claims_calibration_service_role_only` FOR ALL TO service_role
- REVOKE ALL FROM PUBLIC/anon/authenticated + GRANT a service_role
- DO block con RAISE EXCEPTION si RLS no habilitada o policy_count=0

**Output T1:** `migrations/sql/0028_cowork_claims_calibration.sql` listo para apply via MCP Supabase.

### T2 — Module Python `claim_calibration.py` (Ejecutor 1, ~40m)

Crear `kernel/cowork_runtime/claim_calibration.py` (~200 LOC):

- `class ClaimType(Enum)`: file_path, table_name, column_name, migration_number, pr_number, commit_hash, branch_name, sprint_name, loc_count, test_count, fecha_iso, version_string
- `class VerificationStatus(Enum)`: verified_pre, verified_post_match, verified_post_mismatch, unverified
- `@dataclass class ClaimRecord`: campos correspondientes a tabla
- `@dataclass class ClaimCandidate`: claim extraído de output sin verificar aún
- `class ClaimExtractor`:
  - `extract_claims(self, output_text: str) -> List[ClaimCandidate]` — usa regex para extraer paths (`/[\w/]+\.\w+`), table_names (post `FROM ` / `INTO ` / `UPDATE `), migration_numbers (`\d{4}_\w+\.sql`), pr_numbers (`#\d+`), commit_hashes (`[a-f0-9]{7,40}`), branch_names, etc.
- `class ClaimLogger`:
  - `__init__(self, supabase_client, session_id: Optional[UUID])`
  - `log_claim(self, claim: ClaimRecord) -> None` — INSERT a `cowork_claims_calibration`
  - `log_batch(self, claims: List[ClaimRecord]) -> None`
  - `aggregate_daily(self, days: int = 1, claim_type: Optional[str] = None) -> Dict` — SELECT GROUP BY claim_type, verification_status

**APIs públicas:** `ClaimType`, `VerificationStatus`, `ClaimRecord`, `ClaimCandidate`, `ClaimExtractor`, `ClaimLogger`.

**Output T2:** module Python pasando `python3 -c "from kernel.cowork_runtime.claim_calibration import ClaimLogger, ClaimExtractor, ClaimType; print('OK')"`.

### T3 — Hook integration entre markers `CLAIM_CALIBRATION_BEGIN/END` (Ejecutor 1, ~30m)

Modificar `kernel/cowork_runtime/pre_response_hook.py` añadiendo bloques entre markers `# CLAIM_CALIBRATION_BEGIN — Sprint COWORK-MEMENTO-001 T3` / `# CLAIM_CALIBRATION_END` (igual patrón AUTO-DISCIPLINE markers, backward compat 100%):

- Import lazy `ClaimExtractor`, `ClaimLogger` desde claim_calibration
- En `intercept()` post-extract violations: llamar `extractor.extract_claims(output_candidate)` → para cada claim, intentar match contra `self._tool_call_history` reciente → asignar `verification_status`:
  - Si match exacto en tool result → `verified_post_match`
  - Si tool call existe pero strings no matchean → `verified_post_mismatch`
  - Si no hay tool call relacionado → `unverified`
  - Si `register_tool_call()` se llamó pre-emit con el claim verbatim → `verified_pre`
- `logger.log_batch(claims_with_status)` async-fire-and-forget para no bloquear hook

**Constraint duro:** modificación NO debe romper tests existentes 50/50 PASS de AUTO-DISCIPLINE-REAL-001. Markers BEGIN/END garantizan rollback trivial.

**Output T3:** hook modificado + tests existing AUTO-DISCIPLINE pasan idénticos.

### T4 — CLI report tool `cowork_calibration_report.py` (Ejecutor 1, ~25m)

Crear `tools/cowork_calibration_report.py` (~150 LOC):

```python
# tools/cowork_calibration_report.py
"""
CLI report aggregando cowork_claims_calibration de los últimos N días.
Uso:
  python3 -m tools.cowork_calibration_report --days 7
  python3 -m tools.cowork_calibration_report --days 1 --output report.json
  python3 -m tools.cowork_calibration_report --days 7 --claim-type file_path
"""

import argparse
import json
import os
from typing import Dict, Any, Optional

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--claim-type", type=str, default=None)
    args = parser.parse_args()

    # Query Supabase via env vars (mismo patrón session_memory.py)
    # SELECT claim_type, verification_status, COUNT(*) AS n
    # FROM cowork_claims_calibration
    # WHERE created_at >= now() - interval '{days} days'
    # {'AND claim_type = X' if claim_type else ''}
    # GROUP BY claim_type, verification_status
    # ORDER BY claim_type, verification_status;

    # Output: JSON con shape {
    #   "days": N,
    #   "total_claims": M,
    #   "by_type": {
    #     "file_path": {"verified_pre": X, "verified_post_match": Y, "verified_post_mismatch": Z, "unverified": W},
    #     ...
    #   },
    #   "f21_rate": "Z + W" / total_claims,  # F21 reales del período
    #   "generated_at": ISO timestamp
    # }
```

**Output T4:** CLI standalone funcionando con sandbox fallback (env vars Supabase) + tests CLI básicos.

### T5 — Tests pytest (Ejecutor 1, ~30m)

Crear `tests/test_cowork_claim_calibration.py` (~150 LOC):

- `TestClaimExtractor`:
  - test_extract_file_path
  - test_extract_table_name
  - test_extract_migration_number
  - test_extract_pr_number
  - test_extract_commit_hash
  - test_extract_branch_name
  - test_dedupe_same_claim
  - test_no_false_positive_on_prose
- `TestClaimLogger`:
  - test_log_claim_inserts
  - test_log_batch_atomic
  - test_aggregate_daily_grouping
  - test_aggregate_filter_by_type
- `TestVerificationStatusInference`:
  - test_verified_pre_explicit_register
  - test_verified_post_match_string_in_history
  - test_verified_post_mismatch_string_changed
  - test_unverified_no_tool_call

**Acceptance criteria:** 100% PASS, sin warnings, ETA <1s.

### T6 — Postmortem (Ejecutor 1, ~15m)

Crear `bridge/postmortems/COWORK_MEMENTO_001_postmortem.md` siguiendo template AUTO-DISCIPLINE-REAL-001:

- §1 Resumen ejecutivo
- §2 Lo que funcionó
- §3 Divergencias spec↔realidad (D1 D2 D3...)
- §4 Métricas (LOC, ETA real vs estimado, tests count, files)
- §5 Verificación reproducible (bash commands)
- §6 DSC candidato nuevo si aplica (P0 si ninguno)
- §7 Próximos pasos para Cowork (audit)

### T7 — Reporte cierre + bridge file (Ejecutor 1, ~15m)

Crear `bridge/manus_to_cowork_COWORK_MEMENTO_001_DONE_2026_05_NN.md`:

- Status por tarea T0-T7 con archivos entregados
- Limitaciones declaradas L1-LN
- Consecuencias materiales deducidas (DSC-G-008 v3 §4)
- Frase canónica condicional **AUDIT_PENDIENTE** (NO `DECLARADO` hasta audit Cowork — F27)
- Comandos verificación reproducible
- Próximas acciones Cowork (audit + apply migration + merge)

### T8 — Push branch + PR draft (Ejecutor 1, ~5m)

```bash
git checkout -b feat/cowork-memento-001
git add -A
git commit -m "feat(cowork-runtime): Sprint COWORK-MEMENTO-001 T0-T8 — claim calibration retrospectiva"
git push origin feat/cowork-memento-001
gh pr create --draft --title "..." --body "..."
```

PR draft → Cowork audit DSC-G-008 v3 §4 → si verde + T1 firma → merge.

---

## §5 Migration 0028 SQL — referencia para T1 (Ejecutor 1 verifica número binario)

```sql
-- Migration 0028: cowork_claims_calibration
-- Sprint: COWORK-MEMENTO-001 (T1) — Claim calibration retrospectiva pieza 1 anti-Dory
-- DSC enforzado: DSC-V-001 (validación claims), DSC-S-006 v1.1 (RLS), DSC-S-012 (anti-deriva),
--                DSC-G-017 (DSC-as-Contract), DSC-G-008 v3 (anti-Goodhart + deducción)

BEGIN;

CREATE TABLE IF NOT EXISTS public.cowork_claims_calibration (
    id                      UUID         DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at              TIMESTAMPTZ  NOT NULL DEFAULT now(),
    session_uuid            UUID,                              -- FK soft a cowork_sesiones.id
    turn_index              INTEGER      NOT NULL,
    claim_type              TEXT         NOT NULL,
    claim_value             TEXT         NOT NULL,
    verification_status     TEXT         NOT NULL,
    tool_call_evidence      TEXT,                              -- string del tool call que verifica
    detected_in_output      TEXT,                              -- snippet contextual +-50 chars
    extraction_regex_id     TEXT,                              -- que regex de ClaimExtractor lo capturo
    metadata                JSONB        NOT NULL DEFAULT '{}'::jsonb,

    CONSTRAINT cowork_claims_calibration_claim_type_valid CHECK (
        claim_type IN (
            'file_path', 'table_name', 'column_name', 'migration_number',
            'pr_number', 'commit_hash', 'branch_name', 'sprint_name',
            'loc_count', 'test_count', 'fecha_iso', 'version_string'
        )
    ),
    CONSTRAINT cowork_claims_calibration_verification_status_valid CHECK (
        verification_status IN (
            'verified_pre', 'verified_post_match',
            'verified_post_mismatch', 'unverified'
        )
    ),
    CONSTRAINT cowork_claims_calibration_turn_index_nonneg CHECK (turn_index >= 0)
);

COMMENT ON TABLE public.cowork_claims_calibration IS
'Calibration retrospectiva claims factuales Cowork. Sprint COWORK-MEMENTO-001 PR #NN. '
'Dataset para iterar harness anti-Dory con evidencia (Opus Direccion 4) no hipotesis.';

CREATE INDEX IF NOT EXISTS idx_cowork_claims_calibration_session_turn
    ON public.cowork_claims_calibration (session_uuid, turn_index);

CREATE INDEX IF NOT EXISTS idx_cowork_claims_calibration_created_desc
    ON public.cowork_claims_calibration (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cowork_claims_calibration_type_status
    ON public.cowork_claims_calibration (claim_type, verification_status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cowork_claims_calibration_unverified
    ON public.cowork_claims_calibration (created_at DESC)
    WHERE verification_status IN ('unverified', 'verified_post_mismatch');

ALTER TABLE public.cowork_claims_calibration ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS cowork_claims_calibration_service_role_only
    ON public.cowork_claims_calibration;

CREATE POLICY cowork_claims_calibration_service_role_only
    ON public.cowork_claims_calibration
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

REVOKE ALL ON public.cowork_claims_calibration FROM PUBLIC;
REVOKE ALL ON public.cowork_claims_calibration FROM anon;
REVOKE ALL ON public.cowork_claims_calibration FROM authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.cowork_claims_calibration TO service_role;

DO $$
DECLARE
    v_rls_enabled BOOLEAN;
    v_policy_count INTEGER;
BEGIN
    SELECT relrowsecurity INTO v_rls_enabled
    FROM pg_class
    WHERE relname = 'cowork_claims_calibration' AND relnamespace = 'public'::regnamespace;

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: cowork_claims_calibration creada sin RLS habilitado';
    END IF;

    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'cowork_claims_calibration';

    IF v_policy_count = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: cowork_claims_calibration sin policies explícitas';
    END IF;

    RAISE NOTICE 'cowork_claims_calibration creada OK: RLS=%, policies=%', v_rls_enabled, v_policy_count;
END $$;

COMMIT;
```

---

## §6 Acceptance criteria binarios

Para que Cowork emita frase canónica `🏛️ COWORK-MEMENTO-001 — DECLARADO`, audit binario debe reproducir TODOS los siguientes:

```bash
# 1. Migration applied + RLS verified
SELECT relrowsecurity AS rls_enabled,
       (SELECT COUNT(*) FROM pg_policies WHERE tablename='cowork_claims_calibration') AS policy_count
FROM pg_class WHERE relname='cowork_claims_calibration';
# Esperado: rls_enabled=true, policy_count=1

# 2. Module imports OK
python3 -c "from kernel.cowork_runtime.claim_calibration import ClaimLogger, ClaimExtractor, ClaimType, VerificationStatus; print('OK')"

# 3. Tests 100% PASS
python3 -m pytest tests/test_cowork_claim_calibration.py -v
# Esperado: NN passed in <1s, 0 failed, 0 errors

# 4. CLI standalone funciona
python3 -m tools.cowork_calibration_report --days 1 --output /tmp/report.json
cat /tmp/report.json | python3 -m json.tool
# Esperado: JSON estructurado con by_type breakdown

# 5. Hook backward compat: tests AUTO-DISCIPLINE existing pasan
python3 -m pytest tests/test_cowork_auto_discipline_integration.py -v
# Esperado: 50 passed in 0.10s (idéntico pre-MEMENTO)
```

**F27 enforcement:** frase canónica DECLARADO solo se emite tras Cowork reproducir los 5 checks arriba, NO leer reporte Manus.

---

## §7 Limitaciones esperadas + Consecuencias materiales pre-firma (DSC-G-008 v3 §4)

### §7.1 Limitaciones anticipadas (Cowork las declara, Ejecutor 1 las refina post-T0 audit)

- **L_A1** Coverage limitada al output que el hook intercepta — claims pre-hook NO se loguean (gap conocido, cubre VERIFICADOR-001 futuro)
- **L_A2** Regex extraction tiene falsos negativos (paths sin extensión, tablas en CTE complejas)
- **L_A3** verification_status post-hoc heurístico: si tool call result match string Y, asumimos verified — pero result podría ser stale
- **L_A4** Cobertura ≥80% es objetivo, no garantía — T0 audit puede demostrar menos
- **L_A5** Migration número 0028 ASUMIENDO PR #118 mergeado — fallback Ejecutor 1 si no

### §7.2 Consecuencias materiales deducidas (anti-Goodhart)

| Limitación | Consecuencia material | Mitigación | Owner |
|---|---|---|---|
| L_A1 | Subset de claims fuera del dataset | VERIFICADOR-001 futuro extiende pre-hook | T1 firma futura |
| L_A2 | F21 reales no contadas en dataset | Iterar regex con datos T+7d | Cowork |
| L_A3 | False verified_post_match si tool result stale | Tag tool_call_evidence con timestamp + critica visual | Cowork audit reports |
| L_A4 | Métrica éxito puede no alcanzarse | Re-evaluar threshold post-7d con datos reales | T1 |
| L_A5 | Migration number wrong = DSC-S-012 violation | Ejecutor 1 verifica `ls migrations/sql/ | tail -1` al T1 | Ejecutor 1 |

### §7.3 NO consecuencias declaradas (escope limitado)

- NO bloqueo runtime de outputs (no es PIEZA 4)
- NO modificación UX Cowork (puro logging)
- NO consumo significativo recursos (async fire-and-forget + tabla con índices)

---

## §8 Anti-fabricación checklist pre-firma (anti-F24 explícito)

Cowork T2-A declara verbatim antes de pedir firma T1:

- [x] Migration number 0028 verificado con asunción explícita post-merge PR #118 + fallback
- [x] `kernel/cowork_runtime/*.py` listado ls real binario verificado §3.2
- [x] `tools/*.py` listado ls real binario verificado §3.3
- [x] `tests/*.py` listado ls real binario verificado §3.4
- [x] `cowork_sesiones` schema verificado vía Supabase MCP `information_schema.columns` §3.5
- [x] Plantilla migration 0027 leída + adoptada (DSC-S-006 v1.1 DO block verbatim)
- [x] Plantilla AUTO-DISCIPLINE-REAL-001 spec leída para formato magno
- [x] Cita Opus Dirección 4 verbatim §0.2 (no parafraseado)
- [x] Diagnóstico Dory 3 dimensiones verbatim Opus Entregable A §0.1
- [x] NO doctrina markdown nueva (F26 respeto)
- [x] NO rotación secrets (T1 absoluto)
- [x] NO asumir módulos kernel inexistentes (anti-F21 propio)

**Si Cowork firma este spec con UN solo checkbox arriba NO marcado, viola F24 verbatim. Spec se rechaza por T1.**

---

## §9 Frase canónica condicional (F27)

**Pre-audit:** `📋 COWORK-MEMENTO-001 — AUDIT_PENDIENTE`

**Post-audit verde 6/6 reproducido binariamente:** `🏛️ COWORK-MEMENTO-001 — DECLARADO`

**F27 enforcement:** Cowork NO puede emitir `DECLARADO` basándose en lectura del reporte Manus. Debe haber reproducido los 5 checks de §6 verbatim en su turno de cierre.

---

## §10 DSCs enforced explícitos

| DSC | Cómo este sprint lo enforça |
|---|---|
| DSC-V-001 | Cada claim factual Cowork loguea verification_status en `cowork_claims_calibration` (subset del decorator) |
| DSC-S-006 v1.1 | Migration 0028 con DO block que raises si RLS=false o policy_count=0 |
| DSC-S-012 | Migration number verificado con fallback Ejecutor 1 binario |
| DSC-S-016 | Dataset retrospectivo permite iterar anti-fabricación con datos reales |
| DSC-G-008 v3 §4 | Limitaciones §7.1 + Consecuencias materiales §7.2 declaradas pre-firma |
| DSC-G-017 | Spec firmado es contrato, no markdown opcional |
| DSC-MO-006 v1.1 | PBA permanente: dataset alimenta decisiones Sabios futuras con evidencia, no hipótesis |
| F24 (anti) | Checklist §8 verifica binariamente todos los paths/tablas/numbers asumidos |
| F26 (anti) | Sprint produce CÓDIGO ejecutable, no doctrina markdown nueva |
| F27 (anti) | Frase canónica DECLARADO requiere audit binario reproducido, no lectura reporte |

---

## §11 Follow-up tickets post-merge

1. **MEMENTO-T+1** (Cowork) — Apply migration 0028 via MCP Supabase + verificar binariamente prod (rls=true, policy=1, columns=N, indexes=M)
2. **MEMENTO-T+7** (Cowork) — Primer report aggregation diaria 7d post-merge para validar cobertura ≥80%
3. **MEMENTO-T+14** (Cowork + T1) — Decisión binaria PIEZA 3 (CRUZ-001) vs PIEZA 4 (VERIFICADOR-001) basada en datos calibration
4. **MURALLA-001 paralelo** (Cowork drafting + Ejecutor 1 ejecución) — PIEZA 2 anti-Dory state digest auto-inyectado
5. **DSC-MO-018 candidato** (T1) — "Sprints estructurales anti-Dory secuenciados por datos retrospectivos" (formaliza patrón MEMENTO → datos → CRUZ/VERIFICADOR decisión)

---

## §12 Plan operativo binario T1 → Manus

**Owner cada fase:**

1. **Drafting spec:** Cowork T2-A (ESTE DOC)
2. **Firma T1:** Alfredo Góngora aprobando este spec con su firma verbatim
3. **Kickoff:** Cowork pushea spec a `bridge/sprints_propuestos/sprint_COWORK_MEMENTO_001.md` + crea Ejecutor 1 prompt
4. **Ejecución T0-T8:** Manus Hilo Ejecutor 1 (manus_hilo_a)
5. **Audit pre-merge:** Cowork DSC-G-008 v3 §4 (6 gates verde + §3 limitaciones + §4 consecuencias materiales)
6. **Merge + apply migration:** Cowork bajo regla evolucionada (audit verde 6/6 + autoridad T2-A)
7. **Operación 7d:** sistema vive, dataset acumula
8. **Análisis T+7:** Cowork CLI report + recomendación T1 sobre PIEZA 3 vs 4

---

## §13 Anti-redundancia con AUTO-DISCIPLINE-REAL-001 (PR #118)

| Aspecto | AUTO-DISCIPLINE-REAL-001 | MEMENTO-001 (este) |
|---|---|---|
| Función primaria | Detección post-hoc 10 F21 patterns + bloqueo | Logging granular todas afirmaciones factuales + dataset retrospectivo |
| Output | Hook return (False, feedback) | INSERT a tabla |
| Granularidad | 10 patterns regex | 12 claim_types extracted vía regex + AST |
| Decisión runtime | Sí (bloquea output) | No (puro logging) |
| Dataset retrospectivo | Limitado (cowork_protocolo_invocaciones) | Sí (granular por claim_type + verification_status) |
| Atacando dimensión Dory | D2 (parcial post-hoc) | D2 + D3 vía datos |

**MEMENTO usa AUTO-DISCIPLINE como capa inferior** — los outputs del hook AUTO-DISCIPLINE se inspeccionan post-decisión para extraer claims + verification_status. Cero duplicación.

---

## §14 Firmas

**Borrador:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 ~15:30 UTC
**Bajo razonamiento Opus 4.7 + diagnóstico Dory + cita verbatim Opus Dirección 4**
**Anti-F24 checklist §8 verificado binariamente**
**Anti-F26 cumplido: este spec produce código ejecutable, no doctrina nueva**

**Pendiente firma T1:** Alfredo Góngora (autoriza ejecución Ejecutor 1)

**Una vez firmado T1:**
- Cowork pushea spec a `bridge/sprints_propuestos/sprint_COWORK_MEMENTO_001.md` (este path en main)
- Cowork crea prompt kickoff Ejecutor 1 con verificación binaria + path spec + ETA ~150-180m

---

**Fin spec borrador. ETA drafting Cowork real: 35 min. Total: ~630 LOC markdown + boilerplate código completo + tests + acceptance criteria binarios.**
