# REPORTE DE AUDITORÍA: SPEC MANUS-ANTI-DORY-002 V1

**Fecha:** 2026-05-14
**Emisor:** Manus (Hilo Ejecutor)
**Receptor:** Cowork T2-A / Alfredo Góngora T1
**Tipo:** Auditoría de Conformidad pre-implementación

---

## 1. Archivos Auditados
- `bridge/sabios/SABIO_GPT_5_5_PRO_audit_anti_dory_002_2026_05_13.md` (Auditoría GPT-5.5 Pro canonizada)
- `bridge/sprints_propuestos/sprint_MANUS_ANTI_DORY_002_v1_KICKOFF.md` (Contrato de Sprint Cowork)

## 2. Hallazgo Principal (Procedimental)
El SPEC v1 doctrinal firmable **no existe como archivo independiente todavía**. El kickoff instruye explícitamente que la FASE A del sprint consiste en que un hilo Manus redacte dicho SPEC (`bridge/sprints_propuestos/sprint_MANUS_ANTI_DORY_002_v1.md` de ~800-1200 LOC). 

Por lo tanto, esta auditoría evalúa **el contrato del SPEC definido en el Kickoff** contra los 10 puntos exigidos por GPT-5.5 Pro.

## 3. Matriz de Conformidad (Kickoff vs GPT-5.5 Pro)

El kickoff de Cowork incorporó la doctrina de GPT-5.5 Pro de manera excepcionalmente fiel. De las 10 modificaciones obligatorias exigidas por el Sabio, el kickoff incluye las 10:

| # | Exigencia GPT-5.5 Pro | Cubierto en Kickoff | Nivel de Detalle | Gap / Riesgo |
|---|---|---|---|---|
| 1 | `project_runtime_heads` + `runtime_events` + `thread_snapshots` | **SÍ** (§A.3, §3 FASE B.1) | Alto (Define 3 migrations exactas 0029, 0030, 0031) | Ninguno |
| 2 | `manus-snapshot-write` con 4 modos + heartbeat 10-15min | **SÍ** (§A.7, §3 FASE B.4) | Medio | Falta detallar en FASE A los 4 modos exactos dentro del `agent_explicit_writer` |
| 3 | `monstruo-context-broker` externo antes de `task.create` | **SÍ** (§A.5, §3 FASE B.3) | Alto (Integrado al kernel actual vía endpoint `/v1/anti_dory/broker/create_task`) | Ninguno |
| 4 | `guardian.py` como verificador secundario (HALT_ATTACHMENT_MISMATCH) | **SÍ** (§A.6, §3 FASE B.5) | Alto (Integración con `tools/cowork_guardian.py` existente) | Ninguno |
| 5 | Concurrencia con `lock_version` (compare-and-swap) | **SÍ** (§A.4) | Alto (`rpc_accept_snapshot`) | Ninguno |
| 6 | Staleness policy (≤60m, 60m-24h, >24h, mismatch, blocked) | **SÍ** (§A.9) | Alto (Cubre los 5 casos) | Ninguno |
| 7 | Contrato `ATTACHMENT_OK` en primer turno | **SÍ** (§A.10) | Alto (Lista todos los campos requeridos) | Ninguno |
| 8 | Recovery mode sin reexplicación humana (binario) | **SÍ** (§A.8, §3 FASE B.6) | Alto (Define scan sources y formato de pregunta) | Ninguno |
| 9 | RPCs con keys segregadas (`writer_role`, `reader_role`) | **SÍ** (§A.4) | Alto (Prohíbe acceso directo desde service_key) | Ninguno |
| 10 | Harness RAP-002 con 7 tests duros | **SÍ** (§A.11, §3 FASE C.1) | Alto (Lista los 7 casos A-G exactos) | Ninguno |

## 4. Contradicciones y Decisiones Abiertas

**Contradicciones:** Ninguna a nivel arquitectónico. Cowork alineó el scope cross-agente (Manus + Cowork + Embrión) perfectamente con la doctrina de que la solución debe vivir fuera del agente.

**Decisiones T1 Abiertas:** Ninguna. T1 ya autorizó "implementación real inmediata".

**Gaps Menores para el SPEC (FASE A):**
El único punto que requerirá atención especial al redactar el SPEC en la FASE A es detallar los 4 modos exactos de escritura (`write_on_start`, `write_on_transition`, `write_on_artifact`, `write_on_final`) que GPT-5.5 Pro pidió para el `agent_explicit_writer`. El kickoff solo menciona "agent_explicit", pero el SPEC deberá desglosarlo.

## 5. Estado Terminal

**`NEEDS_SPEC_PATCH`**

**Justificación:** El diseño arquitectónico está 100% alineado y listo, pero el archivo SPEC V1 físico (el entregable de la FASE A) aún debe ser redactado por un agente antes de poder pasar a la FASE B (Implementación). No podemos declarar `READY_FOR_T1_IMPLEMENTATION_APPROVAL` porque falta el blueprint de 800-1200 LOC contra el cual Cowork auditará el código.

## 6. Plan Propuesto (No Ejecutar)

Si T1 autoriza proceder, el plan inmediato es ejecutar la **FASE A** del sprint:
1. Crear el archivo `bridge/sprints_propuestos/sprint_MANUS_ANTI_DORY_002_v1.md`.
2. Redactar las 13 secciones (§A.1 a §A.13) detallando el schema SQL, los RPCs, el pseudocódigo del Context Broker y el Guardian, la Staleness Policy y el RAP-002 test harness.
3. Entregar a Cowork para su auditoría final pre-código.
