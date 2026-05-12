---
id: cowork_validation_log_rows_29_30_31_canonizacion_doctrinal_2026_05_12
fecha: 2026-05-12T11:15:00Z
emisor: Cowork T2-A Arquitecto Orquestador post T2-B Sesión 1 verificación binaria
tipo: canonización_doctrinal_leave_as_is
prioridad: P3 informativo
---

# Canonización: validation_log rows 29/30/31 — LEAVE AS IS

## §1 Origen detección

Perplexity T2-B Sesión 1 forensic 2026-05-12 ~09:30 UTC detectó caveat sobre commit `de7375d`:

> Commit declaró "Universo RLS post-aplicacion: 124/124" pero referenciaba rows 29/30/31 validation_log que pueden ser fantasmas.

Cowork diseñó verificación binaria SQL en spec MIGRATION-DRIFT-RESOLUTION-001 v1 T6. **F21 reincidente Cowork:** mi query SQL fabricó columnas inexistentes (`decision`, `source`, `payload`, `timestamp`).

T2-B Sesión 1 corrigió query con esquema real + ejecutó.

## §2 Hallazgo binario verbatim T2-B

**Rows EXISTEN. NO son fantasmas. Son CANÓNICAS.**

Esquema real `validation_log`:
- `id`
- `claim_type`
- `claim_fingerprint`
- `claim_value`
- `validator`
- `evidence_url`
- `timestamp_unix`
- `ttl_seconds`
- `metadata`
- `created_at`

(NO existe columna `decision` ni `source` ni `payload` ni `timestamp` — esquema fabricado por Cowork era falso)

## §3 Contenido verbatim 3 rows

### Row 29

- `id`: 29
- `created_at`: 2026-05-11 16:25:56.948167+00
- `claim_type`: data_source_apis_vigentes_2026
- `validator`: perplexity
- `evidence_url`: https://coinstats.app/blog/best-crypto-api/
- `metadata.sprint`: TRANSVERSAL-001
- `metadata.purpose`: T5 Tendencias implement+monitor pre-requisite
- `inserted_by`: manus_hilo_ejecutor_2

### Row 30

- `id`: 30
- `created_at`: 2026-05-11 16:25:56.948167+00
- `claim_type`: alerting_stack_2026
- `validator`: perplexity
- `evidence_url`: https://clickhouse.com/resources/engineering/top-infrastructure-monitoring-tools-comparison
- `metadata.sprint`: TRANSVERSAL-001
- `metadata.purpose`: T5 Tendencias implement+monitor pre-requisite
- `inserted_by`: manus_hilo_ejecutor_2

### Row 31

- `id`: 31
- `created_at`: 2026-05-11 16:25:56.948167+00
- `claim_type`: trend_signals_active_2026:liketickets
- `validator`: perplexity
- `evidence_url`: https://erp.nema.gov.mn/today-chronicle/psei-mexican-baseball-league-and-espn-coverage-1764810566
- `metadata.sprint`: TRANSVERSAL-001
- `metadata.purpose`: T5 Tendencias implement+monitor pre-requisite
- `inserted_by`: manus_hilo_ejecutor_2

## §4 Decisión doctrinal

**LEAVE AS IS.** Cero cleanup destructivo. Cero reconstrucción.

Razones:
1. Rows existen + son legitimately pre-requisite Sprint TRANSVERSAL-001 T5
2. validator=perplexity + evidence_url poblados — trazabilidad doctrinal preservada
3. metadata.sprint + metadata.purpose explicitan origen
4. inserted_by = manus_hilo_ejecutor_2 (no Cowork) — audit trail intacto

## §5 F21 reincidente Cowork reconocido (DSC-S-016)

Mi query SQL spec v1 T6 fabricó columnas:
- `decision` → NO existe (esquema real: `claim_type`)
- `source` → NO existe (esquema real: `validator`)
- `payload` → NO existe (esquema real: `claim_value` + `metadata`)
- `timestamp` → NO existe (esquema real: `timestamp_unix` + `created_at`)

**Causa:** asumí schema sin verificar binariamente con `\d validation_log` o equivalente. F21 reincidente sin DSC-S-016 aplicado pre-afirmación.

**Mitigación estructural:** DSC-G-008 v3 §4 + T2-B PBA detectó + corrigió. Sistema funcionando.

## §6 Trazabilidad

- Origen: T2-B Sesión 1 audit 3 MIGRATION-DRIFT 2026-05-12 ~10:50 UTC
- Reporte verbatim: pegado Alfredo T1 chat session
- Spec v1 erroneo: `sprint_MIGRATION_DRIFT_RESOLUTION_001.md` commit `3b37b547` T6 SQL fabricado
- Spec v2 corregido: `sprint_MIGRATION_DRIFT_RESOLUTION_001_v2_cherry_pick.md` (este commit) T7 leave-as-is canonizado
- DSC enforced: DSC-S-016 (anti-fabricación causalidad sin grep) + DSC-G-008 v3 §4
