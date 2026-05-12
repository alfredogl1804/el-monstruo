---
id: cowork_to_manus_HILO_EJECUTOR_1_MIGRATION_DRIFT_RESOLUTION_001_KICKOFF_2026_05_12
fecha: 2026-05-12T10:45:00Z
emisor: Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa
receptor: Manus Hilo Ejecutor 1 (queue post Brand-Canary + corrección-3-docs-Cowork encadenadas)
tipo: kickoff_sprint_magno_estructural
prioridad: P0 (cierre drift DB↔repo + colisiones numéricas histórico)
ETA_estimado: 3-5h reales (Fase 1 2-3h + Fase 2 1-2h)
autoridad_T1: "opcion A, voy con tu recomendacion" 2026-05-12 ~10:45 UTC
---

# Kickoff MIGRATION-DRIFT-RESOLUTION-001 — Ejecutor 1

## §1 Trigger de arranque

**Post cierre corrección-3-docs-Cowork** (sprint encadenado post-Brand-Canary). Zero pausa cuando cierres ese sprint.

Si corrección-3-docs sigue corriendo cuando lees esto, mantén orden secuencial:
1. Brand-Canary cierre (ETA original ~5-15 min)
2. Corrección-3-docs cierre (ETA ~10-15 min)
3. **MIGRATION-DRIFT-RESOLUTION-001 arranca** (este sprint, ETA 3-5h)

## §2 Spec firmado T1

Leer completo: `bridge/sprints_propuestos/sprint_MIGRATION_DRIFT_RESOLUTION_001.md` commit `<este-commit>` (FIRME T1 directa).

9 tareas T1-T9 divididas en 2 fases:
- **Fase 1 (T1-T7):** Cierre drift DB↔repo. Re-audit + PBA + merge PR #100 trend_signals + PR #107 catastro_repos + PR nuevo job_executions + audit validation_log fantasmas
- **Fase 2 (T8-T9):** Renumber forensic colisiones 0004 + 0021

## §3 Pre-flight obligatorio

```bash
cd ~/el-monstruo && git status && git pull origin main

# Verificar PRs existentes:
gh pr view 100 --json state,merged,headRefOid
gh pr view 107 --json state,merged,headRefOid
# Esperado ambos: state=OPEN, merged=false

# Verificar branch job_executions sin PR:
git branch -r | grep "fix/migration-0016-job-executions-drift"
# Esperado: presente

# Verificar colisiones 0004 + 0021 en main:
ls migrations/sql/ | grep -E "^000[4]_|^002[1]_"
# Esperado: 4 archivos (2 por cada colisión)

# Verificar siguiente migration libre post Fase 1:
ls migrations/sql/ | sort | tail -3
# Esperado: 0025 (último). Fase 2 T8 → 0026. T9 → 0027.
```

Si pre-flight rojo, reportar `bridge/manus_to_cowork_MIGRATION_DRIFT_RESOLUTION_PREFLIGHT_BLOCKED_2026_05_12.md`.

## §4 Reglas duras NO-CRUCE post-cascada

Hilos paralelos vivos al momento de este kickoff:
- **Ejecutor 2:** ESPIRAL-001 → REMONTOIR-001 pipeline (NO toques `kernel/espiral/`, `kernel/remontoir/`)
- **Catastro:** DSC-S-005-CANONICAL-AUDIT spike → Sprint 89 queue (NO toques DSC-S-005*)
- **Perplexity T2-B Sesión 1:** libre, recibirá tus prompts PBA (T2 + T4 + T6)
- **Perplexity T2-B Sesión 2:** DSC-V-001 fallback chain (NO conflict)
- **Cowork T2-A:** standby para audits DSC-G-008 v3 §4

## §5 Audit T1 trend_signals PR #100 (paso T1 del spec)

Cowork audita primero. Si Cowork audit verde + Perplexity Sesión 1 PBA convergente, vos merge bajo regla evolucionada. NO self-audit Cowork. 

Tu rol Ejecutor 1 en Fase 1: ejecutar merges post audits verdes + crear PR job_executions T5.

## §6 DSC-G-008 v3 §4 obligatorio en reporte cierre

Tu reporte final `bridge/manus_to_cowork_MIGRATION_DRIFT_RESOLUTION_001_FINAL_2026_05_12.md` DEBE incluir:
- §1 logros verificados binariamente por cada PR mergeado + cada migration renumerada
- §2 commits hash + diff stats por tarea
- §3 limitaciones declaradas honestamente (qué NO verificaste)
- §4 consecuencias materiales deducidas + mitigación pre/post merge
- Frase canónica: `🏛️ MIGRATION-DRIFT-RESOLUTION-001 — DECLARADO (9/9 verde) — drift DB↔repo cerrado + 2 colisiones resueltas`

Sin §4 explícito → audit Cowork candidato a regresión post-T2-B.

## §7 Permiso de merge

- **Self-merge PROHIBIDO** para 3 PRs write-risky (PR #100 + #107 + job_executions). Cowork audita + Perplexity convergente + Cowork mergea con caveats verbatim.
- **PR T8 + T9 renumber**: audit Cowork DSC-G-008 v3 + PBA T2-B + Cowork merge si verde.
- **Bypass T1 directo NO autorizado** para esta cascada (T1 firmó scope completo).

## §8 Embrion_memoria al cerrar

Ver spec §7.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 ~10:45 UTC
**Sprint magno encolado a tu queue post Brand-Canary + corrección-3-docs.** Cierra drift histórico DB↔repo + colisiones. ETA 3-5h reales bajo standby Ejecutor 1.
