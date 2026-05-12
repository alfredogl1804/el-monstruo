---
id: cowork_to_manus_HILO_EJECUTOR_1_MIGRATION_DRIFT_RESOLUTION_001_v2_KICKOFF_2026_05_12
fecha: 2026-05-12T11:15:00Z
emisor: Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa
receptor: Manus Hilo Ejecutor 1
tipo: kickoff_v2_cherry_pick_quirurgico
prioridad: P0 (deroga kickoff v1 commit 3b37b547)
ETA_estimado: 3-5h reales
autoridad_T1: "si autorizado" 2026-05-12 ~11:15 UTC
---

# Kickoff MIGRATION-DRIFT-RESOLUTION-001 v2 — Cherry-pick (deroga v1)

## §1 Por qué v2 deroga v1

T2-B PBA Sesión 1 auditó PR #100 + PR #107 + validó que mergear como están DESTRUIRÍA 10 migrations recientes (branches 123 + 144 commits stale). Spec v1 asumí merge directo viable — FALSO.

Nuevo enfoque: **cherry-pick quirúrgico**.

## §2 Spec v2 firmado

Leer completo: `bridge/sprints_propuestos/sprint_MIGRATION_DRIFT_RESOLUTION_001_v2_cherry_pick.md` commit este (FIRME T1 directa).

9 tareas T1-T9. Tu rol Ejecutor 1: T1-T5 + T9. Cowork: T6 + T7 + T8.

## §3 Trigger

Post cierre T5 actual (crear PR job_executions del v1) + corrección 3 docs Cowork. Cuando termines esos 2 trabajos actuales, **descartá** el T5 v1 (era hacer PR para job_executions, ahora ese es T3 del v2 cherry-pick distinto). Arrancá T1 v2 zero pausa.

## §4 Renumber forensic conservador

```
0013_trend_signals.sql         → 0026_trend_signals.sql        (T1)
0018_catastro_repos.sql        → 0027_catastro_repos.sql       (T2)
0018_job_executions.sql        → 0028_job_executions.sql       (T3)
0004_enable_rls_p0_critico.sql → 0029_enable_rls_p0_critico.sql (T4)
0021_catastro_suppliers_humanos.sql → 0030_catastro_suppliers_humanos.sql (T5)
```

## §5 Modelo doctrinal a copiar

T2-B reconoció que `0018_catastro_repos.sql` es **modelo doctrinal superior** (T2 cherry-pick es el más limpio). Usalo como template para T1 + T3 si necesitan agregar idempotencia (BEGIN/COMMIT + DO blocks + DROP POLICY IF EXISTS + CREATE POLICY + REVOKE/GRANT explícito).

## §6 Reglas duras NO-CRUCE

- NO toques `kernel/espiral/` (Ejecutor 2 ESPIRAL-001 en curso)
- NO toques `kernel/cowork_runtime/` (PR #110 + Sprint COWORK-RUNTIME-001)
- NO toques Anthropic/OpenRouter env vars (T1 "no rotar nada")
- SÑ podés tocar `migrations/sql/0026 + 0027 + 0028 + 0029 + 0030` (nuevas) + refs sed-update

## §7 DSC-G-008 v3 §4 obligatorio en reporte final

Ver spec v2 T9. Sin §4 explícito → audit Cowork candidato a regresión post T2-B.

## §8 Permiso de merge

Self-merge PROHIBIDO. Cowork audita + Perplexity Sesión 1 PBA convergente + Cowork mergea con caveats verbatim.

## §9 Out-of-scope

T8 v1 + T9 v1 (renumber 0004 + 0021) ahora son T4 + T5 v2. DSC-S-012 enforcement + 0001 CREATE POLICY idempotency fix quedan para sprints separados.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 ~11:15 UTC
**Kickoff v2 deroga v1.** Cherry-pick magno + renumber forensic conservador + PRs obsoletos cerrados doctrinalmente.
