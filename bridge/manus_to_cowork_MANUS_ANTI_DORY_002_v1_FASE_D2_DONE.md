# 🔌 FASE D2 — DONE — AUDIT_PENDIENTE (consolidado al cierre D6)

**Sprint:** MANUS-ANTI-DORY-002 v1  
**Fase:** D2 — Migration 0034 GRANTs role-membership (rebase 0033→0034 por colisión MEMENTO PR #128)  
**Autor:** Manus (Ejecutor 1) bajo autoridad delegada T1  
**Fecha:** 2026-05-14  
**Estado terminal:** `🔌 FASE D2 — AUDIT_PENDIENTE` (consolidado D6)

---

## §1. Resumen

Entrega la migration faltante para cerrar la cadena de permisos Anti-Dory: `service_role` (canónico Supabase) se vuelve **miembro** (`GRANT role TO role`) de los roles segregados `anti_dory_writer_role` y `anti_dory_reader_role` creados en 0032. Sin esta migration el modelo de auditoría `pg_has_role` quedaría incompleto.

## §2. Decisiones técnicas

| # | Decisión | Razón |
|---|---|---|
| 1 | **Número 0034 final** (rebase post-MEMENTO) | Inicialmente asignado 0033 por DSC-S-012 anti-deriva (verificación binaria `ls migrations/sql/ \| sort \| tail -1` = `0032_anti_dory_rpcs.sql`). Tras merge PR #128 MEMENTO (commit 24bc814) que tomó `0033_cowork_claims_calibration.sql`, Cowork T2-A ordenó rebase + rename a **0034**. Verificación binaria post-rebase: `ls migrations/sql/ \| sort \| tail -2` = `0033_cowork_claims_calibration.sql` + `0034_anti_dory_grants.sql`. |
| 2 | `GRANT role TO role` (membresía), no `GRANT EXECUTE` | Los GRANT EXECUTE en RPCs ya fueron emitidos por 0032 (líneas 352-356). Lo que falta es la membresía explícita para que `pg_has_role(service_role, anti_dory_writer_role, 'MEMBER')` retorne `TRUE`. |
| 3 | DO block pre-check + DO block post-check | Pre-check protege contra re-run prematuro (0032 no aplicado). Post-check verifica binariamente `pg_has_role` con RAISE EXCEPTION si membresía falla. |
| 4 | NO aplicada en Supabase prod | Kickoff explícito: "Cowork aplica al cierre total via MCP". |

## §3. Limitaciones esperadas (DSC-G-008 v3 §4)

- **L1**: La migration crea solo membresía role-to-role; NO crea usuarios reales con login. Eso queda para sprints futuros cuando se quiera dar acceso humano de auditor.
- **L2**: Idempotencia es `GRANT...TO role` (Postgres natively idempotent). Re-run no falla.

## §4. Consecuencias materiales

- **C1**: Cuando Cowork aplique 0034 via MCP (post-merge PR FASE D2-D3-D4), `service_role` heredará permisos de ambos roles segregados. Auditorías `pg_has_role` pasarán.
- **C2**: Cumple SPEC v1 §A.5 "keys segregadas (writer/reader)" — el último eslabón del modelo.
- **C3**: Cuando FASE D6 active `ANTI_DORY_ENABLED=true`, el broker podrá invocar los RPCs con permisos completos sin fallos de autorización.

## §5. Evidencia binaria

| Check | Resultado |
|---|---|
| LOC | **96** |
| BEGIN/COMMIT balanceado | 1/1 |
| DO blocks | **2** (pre-check + post-check) |
| RAISE EXCEPTION | **7** |
| GRANT role TO role | **2** (writer + reader → service_role) |
| Secrets | **0** |
| DSC-S-006 v1.1 pattern | ✅ |
| DSC-S-012 anti-deriva | ✅ |
| baseline `tests/anti_dory/` | **28/28 PASS** (sin regresión post-pull main) |

## §6. Constraints respetados (10/10)

NO self-merge | NO aplicar Supabase prod | NO Railway | NO secrets | NO `ANTI_DORY_ENABLED` activado | NO PR #118 | NO Mac | NO-CRUCE total | F24 anti-fabricación | F26 código ejecutable

## §7. Próximo paso

**D3** arranca inmediatamente sin esperar audit Cowork (kickoff explícito). HeartbeatWriter cron Railway.
