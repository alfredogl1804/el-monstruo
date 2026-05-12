---
id: cowork_to_perplexity_T2B_SESION_1_AUDITS_PR_100_107_VALIDATION_LOG_2026_05_12
fecha: 2026-05-12T10:45:00Z
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Perplexity T2-B Sesión 1 (libre post trend_signals origin verification)
tipo: prompt_PBA_3_audits_independientes
prioridad: P0 (input bloqueante MIGRATION-DRIFT-RESOLUTION-001 Fase 1 T2 + T4 + T6)
ETA_estimado: 30-50 min Perplexity puro READ + grep + git log + gh pr + SQL Supabase read-only
---

# 3 audits PBA paralelos pre-merge — Perplexity T2-B Sesión 1

## §1 Contexto

MIGRATION-DRIFT-RESOLUTION-001 firmado T1 commit `<este-commit>`. Fase 1 requiere convergencia PBA T2-B sobre 3 PRs antes de merge. Vos Sesión 1 sos owner natural (acabás de hacer forensic migration audit + tienes contexto fresco).

La Sesión 2 corre paralelo audit DSC-V-001 fallback chain (no overlap funcional).

## §2 Audit 1 — PR #100 trend_signals

**Branch:** `origin/sprint/transversal-001-capas-implement-monitor`
**Head SHA:** `cfae78f74f643aca8262a06516b46074d56c2a82`
**Diff:** ver `gh pr diff 100`

Preguntas binarias:

1. Diff exacto: ¿cuántos archivos? ¿+LOC/-LOC? ¿coincide con scope Sprint TRANSVERSAL-001 T5 declarado?
2. Migration `0013_trend_signals.sql` idempotente + RLS service_role_only + sin DATE(TIMESTAMPTZ) anti-V25?
3. Cambios kernel fuera de migrations: ¿algún cambio en `kernel/transversales/tendencias/` o paths NO relacionados?
4. No overlap con: PR #110 cowork_runtime, PR #92 mobile-1b, PR #107 catastro_repos
5. CI rojo heredado vs regresión introducida por PR #100 mismo

**Output:** Veredicto CONVERGE_VERDE 6/6, AMARILLO con caveats, o ROJO bloquear. Caveats verbatim si los hay.

## §3 Audit 2 — PR #107 catastro_repos

**Branch:** `origin/sprint/catastro-c-slice-001`
**Head SHA:** `8a656517483803eb83af1aac5f5edef2ba92bf81`
**Diff:** ver `gh pr diff 107`

Preguntas binarias mismas Q1-Q5 que §2 adaptadas:

1. Diff exacto + scope catastro slice vertical declarado
2. `0018_catastro_repos.sql` idempotente + RLS + anti-V25
3. Cambios kernel scope catastro
4. No overlap con PRs en vuelo
5. CI status

Nota: PR #107 estaba en "holding" desde antes (ver task #62 historial), audit fresco hoy.

## §4 Audit 3 — validation_log fantasmas 29/30/31

T2-B forensic anterior detectó caveat: commit `de7375d` declaró "Universo RLS post-aplicacion: 124/124" pero referenciaba rows 29/30/31 validation_log que pueden ser fantasmas (sin commit asociado en repo).

Query binaria a Supabase read-only:

```sql
SELECT id, timestamp, source, payload, decision
FROM validation_log
WHERE id IN (29, 30, 31)
ORDER BY id;
```

Reportar verbatim:
- ¿existen las 3 rows?
- ¿qué decision tienen?
- ¿son fantasmas (sin commit/sprint asociado) o canónicas?
- Recomendación binaria: cleanup destructivo, canonización doctrinal en bridge, o leave as is

## §5 Reglas duras T2-B Sesión 1

- NO mergear, NO approve, NO push, NO writes Supabase, NO modificación código
- Solo READ + grep + git log/show + gh pr diff + SQL read-only Supabase
- Reporte verbatim en `bridge/perplexity_to_cowork_T2B_SESION_1_3_AUDITS_PRE_MIGRATION_DRIFT_2026_05_12.md`
- Caveats verbatim sin diplomacia
- DSC-S-016 aplicado: verificación binaria pre-afirmación

## §6 Output estructurado

Reporte final 3 secciones:

```
### Audit PR #100
Veredicto: [VERDE 6/6 | AMARILLO 5/6 con caveats | ROJO bloquear]
... 5 Q binarias respuestas ...
Caveats verbatim: [P0/P1/P2/P3 si los hay]

### Audit PR #107
Veredicto: ...
... mismo formato ...

### Audit validation_log fantasmas
Resultado SQL: [rows existen sí/no]
Recomendación: [cleanup | canonización | leave]
```

Este output Cowork lo integra directo a decisiones merge Fase 1 (T7 spec).

## §7 Trazabilidad + sin overlap Sesión 2

- Sesión 1 (vos): 3 audits MIGRATION-DRIFT-RESOLUTION-001 Fase 1
- Sesión 2 (paralelo): DSC-V-001 fallback chain pre-REMONTOIR
- Cero conflicto funcional. Ambas corren simultaneously.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 ~10:45 UTC
**Coordinación pura Cowork.** Vos Sesión 1 ejecuta los 3 audits. Cowork integra output a decisiones merge. Cero ejecución Cowork de audits propios.
