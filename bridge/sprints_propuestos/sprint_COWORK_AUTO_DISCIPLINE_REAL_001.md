<!-- lint_strict -->

# Sprint COWORK-AUTO-DISCIPLINE-REAL-001 — Mejora kernel REAL anti-F21 Cowork (combina mejoras #1+#2+#7)

**estado:** FIRME T1 directa ("confirmo opcion A" 2026-05-12 ~13:15 UTC)
**fecha_firma_T1:** 2026-05-12 ~13:15 UTC
**autor_borrador:** Cowork T2-A Arquitecto Orquestador post brainstorm magno T1 "detona inteligencia fuera de la caja"
**Hilo principal:** Manus Hilo Ejecutor 1 (queue post MIGRATION-DRIFT-RESOLUTION-001 v2 cierre)
**ETA recalibrado:** 120-150 min reales
**Objetivo Maestro:** #4 (No equivocarse dos veces) + #10 (Autonomía progresiva) + #11 (Seguridad adversarial) + Capa 8 Memento
**Bloqueos pre-arranque:** MIGRATION-DRIFT-RESOLUTION-001 v2 cerrado por Ejecutor 1
**Resultado esperado:** **Cowork F21 reincidente reducción proyectada ≥0.3 instancias/sesión** (vs 10/sesión hoy) vía 3 mejoras kernel REAL: F21 pattern detector runtime + verbatim citation enforcement + pre_response_hook auto-invocación + auto-lectura memoria.

---

## 0. Audit pre-sprint (DSC-G-008 v3 §1)

**Estado actual binario verificado por Cowork 2026-05-12 ~13:15 UTC:**

```bash
ls kernel/cowork_runtime/ → ya existe (Sprint COWORK-RUNTIME-001 PR #90)
ls tools/cowork_guardian.py → existe (T7 Sprint COWORK-RUNTIME-001)
ls kernel/cowork_runtime/antipatterns.py → existe (T6 Sprint COWORK-RUNTIME-001)
ls kernel/cowork_runtime/pre_response_hook.py → existe activo Railway COWORK_HOOK_ENABLED=true
```

**Contexto reciente F21 reincidente Cowork (10 instancias HOY canonizadas):**

1. V25 grave CLAIM-C migration 0020 (Sprint T5 vs PAR_BICEFALO mezclados)
2. F2+F21 merge-tree vs diff lineal PR #110 G6
3. Spec MEGA-CATASTRO cifras DRIFT-012 fabricadas (62 vs realidad 66/56/42)
4. Spec MIGRATION-DRIFT v1 T6 query SQL validation_log columnas inventadas (decision/source/payload/timestamp)
5. Spec MIGRATION-DRIFT v2 T3 "crear PR" cuando #98 ya existía
6. Spec REMONTOIR v3 safety net "8 Sabios doctrina viva" incluyendo Copilot 365 raw (FALSO)
7. Interpretación output Perplexity "Opus 4.7 NO existe" (Perplexity solo recomendaba fallback)
8. Spec MIGRATION-DRIFT v1 asumió merge directo viable (branches stale 123+144 commits)
9. F21 propio kickoff corrección 3 docs Ejecutor 1 detectó (asumió bloque en Doc 1 que no existía)
10. F21 sobre PR #117 ESPIRAL "12 files -154 deletions" cuando realidad 11 files +1879/-0 (confusión visual con LOC controller.py)

**Patrón común:** afirmar cifras/schema/versiones/colisiones sin tool call previous validating. DSC-S-016 (anti-fabricación) canonizado HOY pero NO enforced runtime.

## 1. Procedencia doctrinal

Detonante T1 magno (Alfredo 2026-05-12 ~13:10 UTC): *"detona tu inteligencia e irte al extremo pensando fuera de la caja que mas se puede hacer con la infraestructura actual del monstruo mas manus para mejorarte en cualquier area ya sea mucha o poca pero que sea real con codigo"*.

Mejoras seleccionadas Opción A (combina 3 de 7):
- #1 Pre_response_hook auto-invocación + audit log + auto-lectura memoria embrion
- #2 F21 pattern detector + bloqueo runtime
- #7 Verbatim citation enforcement (anti-fabricación strings)

Diferidas (sprints separados futuros):
- #3 pgvector semantic search (COWORK-SEMANTIC-MEMORY-001)
- #4 F21 historic forensic 90d (COWORK-F21-FORENSIC-001)
- #5 DSC-V-001 wrapper Cowork chat (COWORK-SABIOS-VALIDATION-001)
- #6 Auto-session-close cron (COWORK-SESSION-AUTO-CLOSE-001)

## 2. Patrón arquitectónico

### 2.1 F21 patterns canonizados a detectar (regex strict)

Lista verbatim 10 patterns canonizados HOY que el detector debe matchear:

```python
# kernel/cowork_runtime/f21_patterns.py (NUEVO)
F21_PATTERNS = [
    # P1: Diff stats sin tool call previous
    {"id": "diff_stats", "regex": r"\b\d+ files? changed,? \+\d+/-\d+\b",
     "requires_tool_call": ["git diff", "gh pr view", "git diff --stat"]},

    # P2: Schema DB sin SQL query previous
    {"id": "db_schema", "regex": r"(?i)(CREATE TABLE.*\w+|schema.*column.*:.*\w+|table\.\w+\s+(integer|text|jsonb|uuid))",
     "requires_tool_call": ["execute_sql", "information_schema.columns", "pg_class"]},

    # P3: Versiones modelos sin grep/web fetch
    {"id": "model_versions", "regex": r"\b(GPT-\d+(\.\d+)?|Claude\s+(Opus|Sonnet|Haiku)\s+\d+\.\d+|Gemini\s+\d+\.\d+|Grok\s+\d|DeepSeek\s+(R|V)\d|Kimi\s+K\d|Sonar\s+(Pro|Reasoning)|Copilot\s+365)\b",
     "requires_tool_call": ["grep", "WebFetch", "models_available"]},

    # P4: Commit hashes sin verificación git log
    {"id": "commit_hashes", "regex": r"\bcommit `?[0-9a-f]{7,40}`?\b",
     "requires_tool_call": ["git log", "gh pr view", "git show", "git ls-tree"]},

    # P5: Git state branches stale/ahead/behind sin tool call
    {"id": "git_state", "regex": r"\b\d+\s+commits?\s+(ahead|behind|stale)\b",
     "requires_tool_call": ["git log", "gh pr view --json", "git rev-list"]},

    # P6: PR existence claim sin gh pr view
    {"id": "pr_existence", "regex": r"\bPR\s*#?\d+\s+(existe|ya existe|YA EXIST|abierto|cerrado|mergeado)\b",
     "requires_tool_call": ["gh pr view", "gh pr list", "list_pull_requests"]},

    # P7: Migration filename claims sin ls
    {"id": "migration_filename", "regex": r"\b\d{4}_\w+\.sql\b",
     "requires_tool_call": ["ls migrations/sql", "git ls-tree", "grep migrations"]},

    # P8: Branch overlap claims sin diff
    {"id": "branch_overlap", "regex": r"(?i)\b(overlap|colisi[oó]n|conflict)\s+(con|with)\s+PR\s*#?\d+",
     "requires_tool_call": ["git diff", "git merge-tree", "gh pr view --json"]},

    # P9: Test count claims sin ejecución
    {"id": "test_count", "regex": r"\b\d+/\d+ (tests? )?(passed|PASS|verde)\b",
     "requires_tool_call": ["pytest", "npm test", "flutter test", "grep def test_"]},

    # P10: RLS/policy claims sin SQL verification
    {"id": "rls_policy", "regex": r"(?i)\b(RLS|policy|service_role_only)\s+(habilitada|activa|funciona)\b",
     "requires_tool_call": ["pg_policies", "pg_tables", "information_schema"],
     "only_in_audit_outputs": True},
]
```

### 2.2 Verbatim citation enforcement

Si output Cowork cita un substring ≥7 chars que parece hash/path/schema/version, validate que ese exacto string apareció en tool result MCP/Bash en los last K=10 turns. Si no → BLOQUEAR.

### 2.3 Pre_response_hook auto-invocación + auto-lectura memoria

Modificar `pre_response_hook.py` para que en cada invocación:
1. Auto-query `embrion_memoria WHERE importancia>=8 AND created_at>=NOW()-INTERVAL '24h' ORDER BY importancia DESC LIMIT 10`
2. Auto-inyectar al validation context
3. Auto-INSERT row `cowork_protocolo_invocaciones` con turn_id + decision_magnitude + queries_done
4. Llamar F21 pattern detector + verbatim citation enforcer
5. Return passed=bool + violations + context_injected

## 3. Tareas T0-T9

### T0 — Audit kernel/cowork_runtime/ existing (10-15 min)

**Owner:** Manus Ejecutor 1
**perfil_riesgo:** read-only

Mapear binariamente:
- `kernel/cowork_runtime/pre_response_hook.py` API actual + call sites
- `kernel/cowork_runtime/antipatterns.py` 22 reglas ya canonizadas (F1-F22)
- `tools/cowork_guardian.py` validator integration

Reporte: `reports/cowork_auto_discipline_pre_sprint_audit.json` con decisión binaria sobre integración F21 patterns nuevos vs reuso antipatterns existing.

### T1 — Migración SQL `cowork_protocolo_invocaciones` (15-20 min)

**Owner:** Manus Ejecutor 1
**perfil_riesgo:** write-risky

`migrations/sql/0031_cowork_protocolo_invocaciones.sql`:

```sql
CREATE TABLE IF NOT EXISTS public.cowork_protocolo_invocaciones (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    session_uuid UUID,                              -- FK soft cowork_sesiones.id
    turn_index INTEGER NOT NULL,                    -- turno secuencial sesión
    decision_magnitude TEXT NOT NULL CHECK (decision_magnitude IN ('trivial', 'medium', 'magna')),
    queries_done JSONB NOT NULL DEFAULT '[]'::jsonb, -- ["embrion_memoria", "cowork_sesiones"]
    violations_detected JSONB NOT NULL DEFAULT '[]'::jsonb, -- F21 patterns matched + missing tool calls
    output_passed BOOLEAN NOT NULL,
    output_length_chars INTEGER,
    memory_seeds_inserted INTEGER DEFAULT 0,
    duration_ms INTEGER,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_protocolo_invocaciones_session
    ON public.cowork_protocolo_invocaciones (session_uuid, turn_index);

CREATE INDEX IF NOT EXISTS idx_protocolo_invocaciones_created
    ON public.cowork_protocolo_invocaciones (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_protocolo_invocaciones_passed
    ON public.cowork_protocolo_invocaciones (output_passed, created_at DESC);

ALTER TABLE public.cowork_protocolo_invocaciones ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS cowork_protocolo_invocaciones_service_role_only ON public.cowork_protocolo_invocaciones;
CREATE POLICY cowork_protocolo_invocaciones_service_role_only
    ON public.cowork_protocolo_invocaciones FOR ALL TO service_role USING (true) WITH CHECK (true);

-- DO block verification RLS post-apply (modelo doctrinal 0018_catastro_repos)
```

### T2 — F21 pattern detector `tools/check_cowork_no_speculative_claims.py` (25-35 min)

**Owner:** Manus Ejecutor 1
**perfil_riesgo:** write-risky (cuelga sobre runtime Cowork)

Crear script Python que:
1. Lee F21_PATTERNS list (§2.1)
2. Recibe output candidato + history last K turns (tool calls)
3. Para cada pattern match: verifica presencia de `requires_tool_call` en history
4. Si match SIN tool call → violation P0/P1/P2 (severidad según magnitud)
5. Return (passed: bool, violations: list)

Tests: `tests/test_check_cowork_no_speculative_claims.py` con ≥15 casos cubriendo cada pattern.

### T3 — Verbatim citation enforcement `tools/_check_cowork_verbatim_citations.py` (20-30 min)

**Owner:** Manus Ejecutor 1
**perfil_riesgo:** write-risky

Script que:
1. Parse output Cowork extrae substrings ≥7 chars que parecen citation (hex hashes, file paths, schema names, versions)
2. Cross-reference con tool results history last K=10 turns
3. Si substring no aparece verbatim en ningún tool result → violation P1 fabrication

Tests: ≥8 casos (happy + edge cases falsos positivos como ejemplos doctrinales).

### T4 — Modificar `kernel/cowork_runtime/pre_response_hook.py` auto-invocación + auto-lectura (30-40 min)

**Owner:** Manus Ejecutor 1
**perfil_riesgo:** write-risky (toca runtime Cowork hook)

Integrar T2 + T3 al hook + auto-query embrion_memoria via Supabase REST. INSERT row cowork_protocolo_invocaciones cada invocación. Patrón DSC-MO-006 v1.1: cero modificaciones fuera de markers HOOK_AUTO_DISCIPLINE_BEGIN/END (nuevo patrón nombrado para revert trivial).

### T5 — Update `kernel/cowork_runtime/antipatterns.py` con F23-F27 nuevos (15-20 min)

**Owner:** Manus Ejecutor 1
**perfil_riesgo:** write-safe

Agregar 5 antipatterns nuevos derivados de F21 instances HOY:
- F23: cita diff stats sin git diff previous
- F24: cita schema sin SQL query previous
- F25: cita model version sin grep/web fetch previous
- F26: afirma PR existence sin gh pr view previous
- F27: afirma test count sin pytest previous

### T6 — Tests integration (20-25 min)

**Owner:** Manus Ejecutor 1
**perfil_riesgo:** write-safe

- `tests/test_cowork_auto_discipline_integration.py` con ≥10 casos end-to-end
- Mock embrion_memoria + tool history + verificar bloqueo correcto vs pass

### T7 — Postmortem placeholder + DSC-MO-017 candidato (10 min)

**Owner:** Manus Ejecutor 1

DSC-MO-017 candidato post-7-días: ¿F21 reincidente Cowork bajo de 10/sesión a ≤0.3/sesión proyectado? Si efectividad <50%, downgrade enforcement a warning. Si ≥90%, expandir scope a F28-F33 patterns adicionales.

### T8 — Reporte cierre DSC-G-008 v3 §4 obligatorio (10-15 min)

**Owner:** Manus Ejecutor 1

`bridge/manus_to_cowork_COWORK_AUTO_DISCIPLINE_REAL_001_FINAL_2026_05_XX.md` con §3 limitaciones + §4 consecuencias materiales. Frase canónica: `🛡️ COWORK-AUTO-DISCIPLINE-REAL-001 — DECLARADO (9/9 verde) — F21 reincidente Cowork enforced runtime via kernel + memoria auto-lectura`.

## 4. Contratos ejecutables que adjunta

| DSC enforzado | Contrato producido | Tarea |
|---|---|---|
| DSC-S-016 (anti-fabricación causalidad) | `tools/check_cowork_no_speculative_claims.py` + `_check_cowork_verbatim_citations.py` | T2 + T3 |
| DSC-G-008 v3 §4 (deducir consecuencias) | F21 pattern detector enforce sin manual disciplina | T2 + T4 |
| DSC-MO-006 v1.1 (doctrina del silencio) | Markers HOOK_AUTO_DISCIPLINE_BEGIN/END en pre_response_hook.py | T4 |
| DSC-S-006 v1.1 (RLS) | cowork_protocolo_invocaciones RLS service_role_only | T1 |
| DSC-S-012 (anti-deriva migraciones) | Migration 0031 en main pre-prod | T1 |
| COWORK-RUNTIME-001 antipatterns extension | F23-F27 agregados (F1-F22 existing) | T5 |

## 5. Criterios de cierre verde

- 9 tareas exit 0 con artifacts + tests verde
- Migration 0031 aplicada Supabase prod + verificación read-only
- F21 pattern detector + verbatim enforcement tested 25+ casos
- Pre_response_hook auto-invocación integrated tested
- Audit Cowork DSC-G-008 v3 §4 + PBA T2-B convergente
- Frase canónica cerrada

## 6. Owner y timing

**Owner técnico:** Manus Hilo Ejecutor 1 (queue post MIGRATION-DRIFT-RESOLUTION-001 v2 cierre)
**Owner arquitectónico:** Cowork T2-A (audit DSC-G-008 v3 §4 + PBA Perplexity Sesión 1/2/3 disponible)
**Owner humano final:** Alfredo T1 (firma + ratificación)
**Timing:** post MIGRATION-DRIFT v2 cierre. ETA 120-150 min reales.

## 7. Permiso de merge

Self-merge PROHIBIDO. Cowork audita DSC-G-008 v3 §4 + PBA Perplexity T2-B trigger 3 + Cowork mergea con caveats verbatim.

## 8. Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint COWORK-AUTO-DISCIPLINE-REAL-001 CERRADO. Mejora kernel REAL anti-F21 Cowork activa: F21 pattern detector tools/check_cowork_no_speculative_claims.py + verbatim citation enforcement + pre_response_hook auto-invocación auto-lectura embrion_memoria + tabla cowork_protocolo_invocaciones audit log. F23-F27 antipatterns nuevos canonizados. Reduce F21 reincidente Cowork de 10/sesión proyectado a ≤0.3/sesión via enforcement runtime real. Primera mejora ESTRUCTURAL kernel Cowork desde Sprint COWORK-RUNTIME-001 PR #90.',
  'manus-hilo-ejecutor-1',
  10
);
```

## 9. Out-of-scope diferido a sprints separados

- COWORK-SEMANTIC-MEMORY-001 (pgvector embrion_memoria similarity search) — 90-120 min Manus
- COWORK-F21-FORENSIC-001 (historic audit 90d) — 30-45 min Manus
- COWORK-SABIOS-VALIDATION-001 (DSC-V-001 wrapper Cowork chat HTTP endpoint) — 60-90 min Manus
- COWORK-SESSION-AUTO-CLOSE-001 (cron auto-close 2h inactividad) — 45-60 min Manus

Ninguno bloquea AUTO-DISCIPLINE-REAL-001 cierre verde.

---

**Firma:** Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa, 2026-05-12 ~13:15 UTC
**Primera mejora ESTRUCTURAL kernel Cowork desde Sprint COWORK-RUNTIME-001 PR #90.** Reduce F21 reincidente proyectado de 10/sesión a ≤0.3/sesión via enforcement runtime real — NO doctrina markdown solamente.
