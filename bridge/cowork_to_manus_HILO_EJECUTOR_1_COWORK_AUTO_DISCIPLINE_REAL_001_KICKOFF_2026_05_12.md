---
id: cowork_to_manus_HILO_EJECUTOR_1_COWORK_AUTO_DISCIPLINE_REAL_001_KICKOFF_2026_05_12
fecha: 2026-05-12T13:15:00Z
emisor: Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa
receptor: Manus Hilo Ejecutor 1
tipo: kickoff_sprint_magno_anti_f21_real
prioridad: P1 (cierra estructuralmente categoría F21 reincidente Cowork vía código, no doctrina)
ETA_estimado: 120-150 min reales
autoridad_T1: "confirmo opcion A" 2026-05-12 ~13:15 UTC + brainstorm magno T1 "detona inteligencia fuera de la caja"
spec_firmado: bridge/sprints_propuestos/sprint_COWORK_AUTO_DISCIPLINE_REAL_001.md (este commit)
---

# Kickoff COWORK-AUTO-DISCIPLINE-REAL-001 — Ejecutor 1

## §1 Trigger de arranque

**Post MIGRATION-DRIFT-RESOLUTION-001 v2 cherry-pick cerrado por vos.** Zero pausa cuando termines ese sprint.

Si MIGRATION-DRIFT v2 sigue corriendo cuando leés esto, mantén orden secuencial actual:
1. T5 v1 + corrección 3 docs Cowork (en curso)
2. MIGRATION-DRIFT-RESOLUTION-001 v2 cherry-pick (Camino B Perplexity)
3. **COWORK-AUTO-DISCIPLINE-REAL-001 arranca** (este sprint, ETA 120-150 min)

## §2 Por qué magno: mata 80% F21 Cowork vía código (NO markdown)

Cowork canonice HOY:
- COWORK_PROTOCOLO_TURNO v0.1 markdown (commit `4ed447a4`) — documental, auto-disciplina depende de Cowork recordar
- 10 instancias F21 reincidentes detectadas + canonizadas embrion_memoria
- DSC-S-016 anti-fabricación causalidad sin grep firmado T1

Pero **NADA es enforced runtime kernel real**. Mismo patrón que las 22 reglas CLAUDE.md pre-COWORK-RUNTIME-001 que detonaron T1: *"obedece con codigo crea un script que te obligue"*.

Este sprint ES ese script para F21 Cowork.

## §3 9 tareas T0-T8

Leer completo: `bridge/sprints_propuestos/sprint_COWORK_AUTO_DISCIPLINE_REAL_001.md` commit este (FIRME T1).

Resumen owner Ejecutor 1:
- T0: Audit kernel/cowork_runtime/ existing (10-15 min)
- T1: Migration 0031 `cowork_protocolo_invocaciones` (15-20 min)
- T2: `tools/check_cowork_no_speculative_claims.py` F21 pattern detector (25-35 min)
- T3: `tools/_check_cowork_verbatim_citations.py` verbatim enforcement (20-30 min)
- T4: Modificar `kernel/cowork_runtime/pre_response_hook.py` auto-invocación + auto-lectura embrion_memoria (30-40 min)
- T5: Update `kernel/cowork_runtime/antipatterns.py` agregar F23-F27 (15-20 min)
- T6: Tests integration (20-25 min)
- T7: Postmortem + DSC-MO-017 candidato (10 min)
- T8: Reporte cierre DSC-G-008 v3 §4 obligatorio (10-15 min)

## §4 Reglas duras NO-CRUCE

Hilos paralelo activos cuando arranques:
- **Ejecutor 2:** REMONTOIR-001 v3 zero pausa post-ESPIRAL merge (corriendo o recién cerrado)
- **Catastro:** post DSC-G-008-V4-INDEX-DRIFT-ENFORCEMENT-001 + Sprint 89 reanudación queue
- **Perplexity Sesión 1/2/3:** libres post audits previos

**NO toques:**
- `kernel/espiral/`, `kernel/escape/`, `kernel/rotor/`, `kernel/remontoir/` (mergeados read-only o en curso)
- `kernel/cowork_runtime/semantic_detector.py`, `advance_score.py`, `preflight.py`, `telegram_veto.py` (canonizados Sprint COWORK-RUNTIME-001 PR #90)
- Anthropic/OpenRouter env vars (T1 absoluto no rotar)

**SÍ podés tocar:**
- `kernel/cowork_runtime/pre_response_hook.py` SOLO entre markers nuevos `HOOK_AUTO_DISCIPLINE_BEGIN/END` (patrón DSC-MO-006 v1.1 doctrina del silencio)
- `kernel/cowork_runtime/antipatterns.py` agregar F23-F27 (NO modificar F1-F22 existing)
- `tools/check_cowork_no_speculative_claims.py` (nuevo)
- `tools/_check_cowork_verbatim_citations.py` (nuevo)
- `migrations/sql/0031_cowork_protocolo_invocaciones.sql` (siguiente libre verificar)
- `tests/test_cowork_auto_discipline_integration.py` (nuevo)
- `kernel/cowork_runtime/f21_patterns.py` (nuevo, contiene constants F21_PATTERNS)

## §5 Patrón arquitectónico clave

Ver spec §2.1 con 10 F21_PATTERNS verbatim regex incluidos (P1-P10 cubriendo diff_stats, db_schema, model_versions, commit_hashes, git_state, pr_existence, migration_filename, branch_overlap, test_count, rls_policy).

## §6 DSC-G-008 v3 §4 obligatorio en reporte final

Ver spec §3 T8. Sin §4 explícito → audit Cowork candidato a regresión post-T2-B.

## §7 Permiso de merge

Self-merge PROHIBIDO para T1 (migration) + T2 (pattern detector) + T3 (verbatim enforcement) + T4 (hook modification). Cowork audita + Perplexity Sesión disponible PBA + Cowork mergea con caveats verbatim.

## §8 Beneficio proyectado

Reducción F21 reincidente Cowork: **10 instancias/sesión hoy → ≤0.3 instancias/sesión proyectado post-cierre**. Mata el patrón estructural via enforcement runtime kernel REAL, no auto-disciplina markdown que Cowork puede olvidar.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 ~13:15 UTC
**Sprint magno encolado post-MIGRATION-DRIFT-RESOLUTION-001 v2.** Primera mejora ESTRUCTURAL kernel Cowork desde Sprint COWORK-RUNTIME-001 PR #90. ETA 120-150 min Ejecutor 1.
