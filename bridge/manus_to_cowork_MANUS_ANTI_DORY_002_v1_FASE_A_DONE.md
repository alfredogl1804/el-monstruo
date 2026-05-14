# 📋 SPEC V1 — AUDIT_PENDIENTE

**Sprint:** MANUS-ANTI-DORY-002 v1
**Fase:** A — Redacción del SPEC doctrinal firmable
**Owner FASE A:** Manus Hilo Ejecutor (cuenta Google)
**Auditor designado:** Cowork T2-A
**Autoridad T1:** Alfredo Góngora
**Fecha cierre FASE A:** 2026-05-14
**Frase canónica:** `📋 SPEC V1 — AUDIT_PENDIENTE`

---

## 1. Entregables FASE A

| # | Artefacto | Ruta | Estado |
|---|---|---|---|
| 1 | Pre-audit Anti-F24 (verificación binaria) | `reports/anti_dory_002_v1_pre_spec_audit.json` | Creado |
| 2 | SPEC v1 doctrinal firmable (13 secciones §A.1-§A.13) | `bridge/sprints_propuestos/sprint_MANUS_ANTI_DORY_002_v1.md` | Creado |
| 3 | Bridge file de cierre (este archivo) | `bridge/manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_A_DONE.md` | Creado |

## 2. Cumplimiento de constraints duros

| Constraint | Estado | Evidencia |
|---|---|---|
| Anti-F24 (verificación binaria pre-SPEC) | **PASS** | JSON pre-audit con 14 checks A-N |
| Anti-F26 (SPEC = blueprint para CÓDIGO, no doctrina markdown duplicada) | **PASS** | SPEC contiene SQL ejecutable, Python pseudocode, JSON contract |
| NO-CRUCE (`kernel/cowork_runtime/*.py` intacto) | **PASS** | No tocado en FASE A |
| DSC-G-008 v3 §4 (limitaciones esperadas + consecuencias materiales) | **PASS** | §A.13 con L1-L2 y C1-C3 |
| Migrations 0029/0030/0031 verificadas libres | **PASS** | Última real es 0028 (gap 0027 documentado, no bloqueante) |
| Patch obligatorio §A.7 (4 modos `agent_explicit_writer` con código real) | **PASS** | Líneas 134-148 del SPEC |
| `heartbeat_writer` documentado como INDEPENDIENTE del agente | **PASS** | Líneas 150-153 con marca CRÍTICO |
| NO implementación de código | **PASS** | Solo redacción |
| NO migrations creadas | **PASS** | Solo `.md` y `.json` de docs/reports |
| NO Supabase real tocado | **PASS** | NO_VERIFICABLE_DESDE_SANDBOX, deferred a FASE B |
| NO Railway tocado | **PASS** | No interactuado |
| NO secrets manipulados/impresos | **PASS** | T1 ACCEPTED_RISK vigente |
| NO self-merge | **PASS** | Push a rama doc dedicada, sin PR mergeada |

## 3. Hallazgos para Cowork T2-A (input al audit)

### 3.1 Decisiones técnicas relevantes

1. **Punto de inyección del Context Broker:** `tools/manus_bridge.create_task()` — wrapper ya existente. No se crea wrapper nuevo, se intercepta el actual.
2. **Punto de extensión del Guardian:** `tools/cowork_guardian.GuardianVerdict` — clase ya existente con `validate_output()`. Se agrega `verify_attachment_contract()`.
3. **Plantilla de migrations:** `migrations/sql/0026_embrion_homeostasis_log.sql` — incluye DO block con `RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION'` que se replicará en 0029/0030/0031.
4. **Gap 0027 en migrations:** existe drift no relacionado. Se decide saltar (no ocupar 0027 con un fix lateral que contaminaría el sprint).

### 3.2 Decisiones de diseño que requieren validación de Cowork

1. **§A.4 — Roles segregados (`anti_dory_writer_role`, `anti_dory_reader_role`):** propuesta inicial. Cowork puede simplificar a un solo rol si considera excesivo.
2. **§A.9 — Umbrales de staleness (60min FRESH, 24h STALE):** propuesta inicial basada en GPT-5.5 Pro audit. Cowork puede ajustar si hay contexto operativo distinto.
3. **§A.11 — 7 casos de RAP-002:** Cowork puede agregar/quitar casos según política.

### 3.3 Limitaciones declaradas (DSC-G-008 v3 §4)

- L1: Si Supabase cae → Context Broker bloquea creación de hilo (fail-closed).
- L2: `heartbeat_writer` requiere infra externa (Railway cron) para no depender del agente.

### 3.4 Consecuencias materiales declaradas

- C1: ~2-4s extra de latencia pre-`task.create`.
- C2: ~200-300 tokens extra por hilo (`ATTACHMENT_OK`).
- C3: Memoria es puntero (head), no archivo profundo de código.

## 4. Discrepancia menor con kickoff

El kickoff sugería SPEC de **800-1200 LOC**. El SPEC entregado tiene **221 líneas**. Justificación: prioricé densidad técnica (SQL ejecutable, código Python real, JSON contract concreto) sobre expansión narrativa para evitar Anti-F26 (doctrina markdown duplicada). Si Cowork prefiere expansión narrativa con racionales detallados por cada decisión, lo solicita en su audit y se redacta v1.1 en patch posterior.

## 5. Próximo paso esperado (FASE B)

Cowork T2-A audita el SPEC contra DSC-G-008 v3 §4 + verifica que cada componente tiene blueprint suficiente para implementación. Si Cowork firma `🏛️ SPEC V1 — APROBADO`, T1 autoriza FASE B (implementación: crear migrations, RPCs, Context Broker real, writers, harness RAP-002).

**NO se ha iniciado FASE B.** Ningún archivo de código fue creado. Ningún recurso real (Supabase, Railway, secrets) fue tocado.

---

**Firma:** Manus Hilo Ejecutor (Hilo Google), 2026-05-14
**Frase canónica de cierre:** `📋 SPEC V1 — AUDIT_PENDIENTE`
