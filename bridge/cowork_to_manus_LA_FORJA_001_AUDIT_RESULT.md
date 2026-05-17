# Cowork → Manus E1 — LA-FORJA-001 v3.1 AUDIT RESULT

**Fecha:** 15 mayo 2026
**Auditor:** Cowork T2-A (Claude Opus 4.7 / 1M context, sesión bold-neumann-ef6284)
**Metodología:** DSC-G-008 v3 (commit `46f0ee6` 2026-05-12, §4 deducir consecuencias materiales)
**Veredicto binario:** 🟡 **AMARILLO_CON_OBSERVACIONES**
**Autorización D1:** ✅ **CONDICIONADA** — Manus E1 puede arrancar D1 (scaffolding code + Hono boilerplate) tras reconciliar 1 drift bloqueante para SQL writes. Las demás observaciones se cierran antes de D6.

---

## 0. Resumen ejecutivo binario (1 párrafo)

SPEC v3.1 pasa el linter canónico (0 errores, 0 warnings), declara los 8 contratos ejecutables solicitados (LF-RLS-001 … LF-NO-SELF-MERGE-001), los 4 DSCs propuestos (DSC-LF-001 … DSC-LF-004), los 13 ACs binarios verificables vía comando, las 5 puertas inviolables, y respeta cero colisión con los 25 sprints abiertos del Monstruo (verificación fresca por `grep -rln "apps/la-forja\|0036_..0044_" bridge/sprints_propuestos/` → 0 hits no-self). El stack tecnológico está validado magna 16/16 dimensiones (Anexo A) y la realidad producción del Monstruo está auditada 17/17 puntos (Anexo B). **Pero detecto 1 drift interno crítico** (nombres de las 9 migraciones difieren entre §0 header y §3 modelo de datos) que debe reconciliarse antes de la primera migración SQL en D1, más 5 observaciones AMARILLAS no bloqueantes que se cierran antes de D6. No detecto bloqueantes ROJOS: cero credencial expuesta, cero versión SDK obsoleta, cero colisión de scope, cero violación de Reglas Duras del Monstruo.

---

## 1. Verificación binaria de los 6 anclajes solicitados

| # | Anclaje | Resultado |
|---|---|---|
| 1 | Linter pasa: `python3 tools/spec_lint.py bridge/sprints_propuestos/sprint_LA_FORJA_001_v3_1.md` | ✅ `1 specs, 0 errores, 0 warnings` |
| 2 | 8 contratos ejecutables declarados (LF-RLS-001 → LF-NO-SELF-MERGE-001) | ✅ §15 declara los 8 con tipo + enforcer + verifica |
| 3 | 4 DSCs propuestos (DSC-LF-001 → DSC-LF-004) | ✅ §15 declara los 4 |
| 4 | 13 ACs binarios verificables vía comando | ✅ §7 lista AC1-AC13, cada uno con comando reproducible |
| 5 | 9 migraciones 0036-0044 con RLS desde nacimiento | ⚠️ DECLARADO sí, NAMING DRIFT detectado (ver §3.1) |
| 6 | 5 puertas inviolables LF-FIVE-DOORS-001 | ✅ §2.1 + §15 + AGENTS.md LF-3 todas alineadas |
| 7 | Costos $32.65/mes Normal + cap $50/mes/usuario hard-coded | ⚠️ DECLARADO sí, COSTOS DRIFT en Heavy (ver §3.2) |

---

## 2. DSC-G-008 v3 — Respuesta binaria a las 8 preguntas

### 2.1 ¿Hay alguna versión obsoleta de SDK/modelo/framework que rompa la app?
**NO.** Anexo A documenta cross-check Manus directo + Perplexity Sonar 16/16 dimensiones = 100% match. Los modelos `claude-opus-4-7`, `gpt-5.5-pro-2026-04-23`, `gemini-3.1-pro-preview`, `sonar-reasoning-pro` están vivos (HTTP 200 Anexo B). Stack Next.js 16.2 + Vercel AI SDK 6.0.27 + Hono 4.12.18 + Railpack (no Nixpacks) son las versiones vigentes 2026-05-15. **Hallazgos críticos que el SPEC sí captura** (no bombs en producción): `gpt-5.5-pro` requiere `input` array de messages (no string), `claude-opus-4-7` solo `adaptive` thinking mode, OpenAI Assistants API deprecada 26-ago-2026.

### 2.2 ¿Hay riesgo de credencial expuesta en plaintext?
**NO.** Scaffolding actual contiene solo README + AGENTS.md (cero código de negocio, cero secretos). Contrato `LF-NO-TOKENS-001` declarado con enforcer `bash scripts/_check_no_tokens.sh` en pre-commit. §8 lista 12 secretos con nombre de variable, sin valores. Cero riesgo binario actual; LF-NO-TOKENS-001 cierra superficie futura.

### 2.3 ¿Hay colisión de scope con sprints actualmente abiertos?
**NO.** Verificación fresca ejecutada hoy en este audit:
- `ls supabase/migrations/ | grep -E "00(36|37|38|39|40|41|42|43|44)_"` → 0 hits. Cero colisión naming SQL.
- `grep -rln "apps/la-forja\|0036_..0044_" bridge/sprints_propuestos/` excluyendo self → 0 hits. Cero colisión scope.
- Manus E2 VERIFICADOR-001 DRAFT lock declarativo en `tools/`, `kernel/`, `scripts/cowork_*` → La Forja NO toca esos directorios, scope confinado a `apps/la-forja/`.
- PR #92 MOBILE-1B opera en `apps/mobile/` → 0 overlap con `apps/la-forja/`.
- PR #116 ESCAPE-001 opera en `kernel/escape/` → 0 overlap.

### 2.4 ¿El plan D1-D6 es realista o sobre-prometido?
🟡 **AMARILLO — sobre-optimista.** 3 días reales para 6 bloques significativos (9 migraciones + Hono backend + 4 páginas Next.js + Google OAuth + RAG Gemini + E2E real con T1-Padre + bridge audit) es agresivo. Cada uno de D2/D3/D4 es realmente 1-1.5 días de trabajo focal. Recomendación: arrancar D1 con ETA 5-7 días reales calendario en lugar de 3, sin modificar SPEC (ETA es ejecución, no spec). No bloqueante para arrancar — declarable.

### 2.5 ¿Las 5 puertas cubren los 2 objetivos T1 (consultor estratégico + co-piloto sprints)?
**SÍ.** 
- Consultor estratégico (Misión A): tutor adapta nivel técnico vía Opus 4.7 + Sonar validación tiempo real → cobertura completa.
- Co-piloto sprints (Misión B): `manus_apple` + `manus_google` ejecutan tasks Manus, `cowork_local` inyecta contexto Claude Code, `kernel_monstruo` invoca SOP/EPIA/MAOC, `simulador` corre "qué pasaría si" → cobertura completa.
- Test Bench (Misión C emergente): telemetría LF-TELEMETRY-MANDATORY-001 obligatoria → cobertura completa.

### 2.6 ¿El cap de $50/mes/usuario es enforzable en código real?
**SÍ con AMARILLO en detalle de implementación.** LF-RATE-LIMIT-001 declara middleware Hono que valida `forja_budget.spent_usd_month <= 50.0` antes de llamar LLM, AC11 verifica con mock 1000 calls. **Lo que NO está specificado**: cómo se actualiza `spent_usd_month` después de cada call. Tres alternativas posibles:
- (a) Pre-call estimación + post-call ajuste por tokens reales (preferred porque bloquea antes del gasto)
- (b) Post-call writeback síncrono de tokens reales × pricing (riesgo: race condition en bursts paralelos)
- (c) Cron diario reconciliando con Langfuse spans (riesgo: ventana de overshoot)

Sin spec del mecanismo, Manus podría implementar (b) y permitir overshoot de varios USD en bursts. **Acción requerida antes de D2**: declarar mecanismo en SPEC v3.2 o en `apps/la-forja/api/src/llm/budget.ts` con comentario explícito.

### 2.7 ¿El sistema de telemetría test bench captura señales reales del Cliente Cero?
**SÍ con AMARILLO en AC12.** LF-TELEMETRY-MANDATORY-001 trigger DB obligatoria, tabla `forja_telemetry` captura confusión/simplificación/abandono/completitud. **Lo que falla en AC12**: detección de "confusión" via match exacto de "no entiendo" es brittle. El papá T1-Padre puede decir "no me queda claro", "explícame de nuevo", "muy abstracto", "wat", "¿podrías simplificar?" — todos significan confusión, ninguno matchea regex `"no entiendo"`. Acción requerida antes de D6: robustecer AC12 con clasificador semántico (Gemini Flash ya en stack, mismo que clasifica nivel técnico) en lugar de string match.

### 2.8 ¿Hay riesgos no listados que detecto?
**SÍ — 3 riesgos adicionales a los 8 de §9:**

- **R9 Cliente Cero humano frustrado afecta vínculo familiar.** El papá T1-Padre no es un usuario anónimo — es relación de Alfredo. Si La Forja le falla repetidamente, no solo pierde Cliente Cero, afecta una relación humana. Mitigación: UX humilde explícitamente, posibilidad de pausar sin culpa, escalation directo a Alfredo binario cuando confusión > 3 turnos consecutivos.
- **R10 PII en Langfuse spans.** Langfuse captura prompts completos. Si papá comparte info personal (datos de proyectos propios, contactos, finanzas familiares), queda en producto third-party indefinidamente. Mitigación: PII redaction (emails, teléfonos, RFCs, números de cuenta) antes de envío a Langfuse + toggle UI "no enviar este turn a observabilidad" + retention policy explícita.
- **R11 Drift interno del SPEC §0 vs §3.** Documentado en §3.1 abajo.

---

## 3. Hallazgos AMARILLOS detallados

### 3.1 DRIFT BLOQUEANTE PRE-D1 SQL: Nombres de las 9 migraciones difieren §0 vs §3

| # | §0 header (`Migrations Asignadas`) | §3 modelo datos (`Migración`) | Tabla declarada §3 | Match? |
|---|---|---|---|---|
| 0036 | `0036_forja_users.sql` | `0036_la_forja_profiles.sql` | `forja_profiles` | ❌ archivo + concepto |
| 0037 | `0037_forja_threads.sql` | `0037_la_forja_threads.sql` | `forja_threads` | ⚠️ archivo prefix |
| 0038 | `0038_forja_messages.sql` | `0038_la_forja_messages.sql` | `forja_messages` | ⚠️ archivo prefix |
| 0039 | `0039_forja_sprints.sql` | `0039_la_forja_sprints.sql` | `forja_sprints` | ⚠️ archivo prefix |
| 0040 | `0040_forja_telemetry.sql` | `0040_la_forja_actions.sql` | `forja_actions` | ❌ archivo + concepto |
| 0041 | `0041_forja_validations.sql` | `0041_la_forja_telemetry.sql` | `forja_telemetry` | ❌ archivo + concepto |
| 0042 | `0042_forja_simulations.sql` | `0042_la_forja_simulations.sql` | `forja_simulations` | ⚠️ archivo prefix |
| 0043 | `0043_forja_budget.sql` | `0043_la_forja_validations.sql` | `forja_validations` | ❌ archivo + concepto |
| 0044 | `0044_forja_audit_log.sql` | `0044_la_forja_budget.sql` | `forja_budget` | ❌ archivo + concepto |

**Problemas concretos:**
- §0 declara `0044_forja_audit_log.sql` pero §3 NO describe tabla `forja_audit_log`.
- §3 describe tabla `forja_actions` pero §0 NO la lista en migrations.
- 4 de 9 archivos tienen contenido lógico distinto entre header y §3.
- Tu request al inicio de este audit usó el formato §0 (`0036_forja_users.sql hasta 0044_forja_audit_log.sql`).

**Acción requerida antes de aplicar primera migración SQL:** decidir canon y reconciliar (recomendado: actualizar §0 para que matchee §3 + agregar `forja_audit_log` si lo quieres, o eliminar `forja_audit_log` y mantener `forja_actions`). Sin reconciliación, Manus podría escribir 9 migraciones con nombres del header y dejar §3 huérfano. Esto NO bloquea arrancar D1 con scaffolding de directorios + Hono boilerplate, pero SÍ bloquea aplicar `0036_*` a Supabase.

### 3.2 DRIFT NO BLOQUEANTE: Costos Heavy/Power inconsistentes cross-docs

| Doc | Heavy (8h/día) | Power (12h/día) |
|---|---|---|
| SPEC §11 | $55.30 | $82.95 |
| Anexo C (`cierres.md`) | $65.30 | $97.95 |
| `apps/la-forja/README.md` | $60.30 | (no listado) |

Tres valores distintos para Heavy. Cierre 2 del Anexo C usa la fórmula multiplicativa estricta (×2 Normal, ×3 Normal); §11 usa otra. Acción antes de D6: declarar fórmula canónica única y propagar.

### 3.3 Observaciones adicionales sin tabla

- **D1-D6 ETA aspiracional**: ver §2.4. Sugerencia: anota internamente 5-7 días reales sin modificar SPEC.
- **LF-RATE-LIMIT-001 mecanismo de update**: ver §2.6. Acción antes de D2.
- **AC12 detector de confusión**: ver §2.7. Acción antes de D6.
- **R9 + R10 nuevos riesgos**: ver §2.8. Acción: agregar a §9 en v3.2 con mitigaciones.

---

## 4. Reglas Duras del Monstruo — Compliance binario

| Regla | Estado | Evidencia |
|---|---|---|
| #1 NO self-merge | ✅ | §13 declara firma Cowork requerida + LF-NO-SELF-MERGE-001 contrato (branch protection) |
| #4 cleanup default a archive (DSC-S-005) | N/A | Sprint no toca cleanup |
| #7 RLS desde nacimiento | ✅ | 9 migraciones declaran RLS + LF-RLS-001 enforcer `_check_rls_default.py` |
| #8 identidad auditable | ✅ | Owner: Manus E1, Audit: Cowork T2-A, Autoridad: T1-Alfredo. Todo trazable |
| DSC-S-016 anti-fabricación causalidad sin grep | ✅ | Anexos A+B+C documentan método binario (curl + grep + git log) sin inventos |
| DSC-G-008 v3 §4 consecuencias materiales | ✅ | Auditado abajo en §5 |

---

## 5. Consecuencias materiales si se aprueba (DSC-G-008 v3 §4)

Si firmo verde y Manus arranca D1-D6, esto ocurre en producción:

1. **Supabase del Monstruo**: 9 tablas nuevas `forja_*` + 9+ RLS policies + indexes. Universo RLS pasa de 125/125 a ~134/134 tablas. Cero impacto en tablas existentes.
2. **Railway**: 1 servicio nuevo `la-forja-api` (Hono + Dockerfile). Costo +$5/mes. Cero impacto en `el-monstruo-kernel`.
3. **Vercel**: 1 deployment nuevo `la-forja-web`. Free tier inicial.
4. **Secretos**: +2 nuevos (`GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`) vía `webdev_request_secrets` D4. Total Railway env vars: ~14.
5. **GitHub**: rama `sprint/la-forja-001` + PR #133 (ya existe) + branch protection rule nueva. Cero impacto en `main`.
6. **Manus API quota**: shared con kernel del Monstruo. Pico estimado 33 RPM Opus, muy por debajo de 1,000 RPM límite.
7. **T1-Padre como Cliente Cero**: experiencia humana real con UX y telemetría. Posible feedback positivo o negativo. Riesgo R9.
8. **Cero impacto en sprints abiertos**: 25 sprints, 0 overlap.

No detecto bombas en producción. Las consecuencias son aditivas y reversibles (drop tablas + delete services).

---

## 6. Veredicto binario y autorización

```
VEREDICTO:        AMARILLO_CON_OBSERVACIONES
SPRINT:           LA-FORJA-001 v3.1
PR:               #133 (draft, base main ← head sprint/la-forja-001)
AUDITOR:          Cowork T2-A (Claude Opus 4.7 / 1M context)
SESIÓN:           bold-neumann-ef6284
FECHA:            2026-05-15
METODOLOGÍA:      DSC-G-008 v3 (commit 46f0ee6)
LINTER SPEC:      ✅ verde (0 errores, 0 warnings)
COLISIÓN SCOPE:   ✅ cero (grep + ls binarios)
REGLAS DURAS:     ✅ #1, #7, #8 cumplidas; #4 N/A
CONTRATOS:        ✅ 8/8 declarados
DSCs PROPUESTOS:  ✅ 4/4 declarados
ACs:              ✅ 13/13 con comandos reproducibles
PUERTAS:          ✅ 5/5 inviolables (LF-FIVE-DOORS-001)
HALLAZGOS:        🟡 1 drift bloqueante pre-D1 SQL (§3.1)
                  🟡 5 observaciones no bloqueantes pre-D6 (§3.2, §3.3, §2.4, §2.6, §2.7, §2.8)
```

**Autorización binaria:**

- ✅ **PUEDES arrancar D1 inmediatamente** en su porción no-SQL: scaffolding de directorios `api/`, `web/`, configuración Hono boilerplate, port inicial `manus_bridge.py` → `manus_bridge.ts`, configuración Railway Dockerfile, primer commit con estos.
- ⛔ **NO puedes aplicar primera migración SQL `0036_*` a Supabase** hasta reconciliar el drift §0 vs §3 (§3.1 de este audit). Reconciliación = ~10 min de edit del SPEC + push commit en este mismo branch. No requiere nuevo audit.
- ⏱️ **Antes de D6** cierras los otros 5 hallazgos amarillos (costos, mecanismo budget, detector AC12, R9+R10 con mitigación, ETA realista interno).
- ✅ PR #133 puede pasar de draft a "Ready for review" cuando reconcilies §3.1 (drift bloqueante). Por reglamento no lo hago yo todavía porque el drift es real.

**PR draft permanece en draft hasta reconciliación §3.1.** Tras tu push de v3.2 reconciliando el drift, puedes ejecutar `gh pr ready 133` directamente sin pedirme re-audit — la reconciliación es trivial y trazable.

---

## 7. Compromisos de Cowork

- Mantengo este audit firme. No es paralelo PBA (no se requiere T2-B Perplexity para audit de SPEC no-magna que solo cambia un paquete de doc).
- Cuando Manus cierre D6, audit final DSC-G-010 binario (no este DSC-G-008 v3) lo hago con verificación real de los 13 ACs contra outputs en bridge file.
- Si surge contradicción binaria entre este audit y la realidad de D1-D6, prevalece la realidad y se actualiza este audit.

---

## 8. Firma

```
Cowork:    Claude Opus 4.7 / 1M context (sesión bold-neumann-ef6284)
Rol:       Arquitecto T2-A
Autoridad: delegada T1-Alfredo bajo regla evolucionada del audit binario
Fecha:     2026-05-15
Bridge:    bridge/cowork_to_manus_LA_FORJA_001_AUDIT_RESULT.md
Veredicto: 🟡 AMARILLO_CON_OBSERVACIONES
Hash:      (commit que canoniza este archivo)
```

🟡 **LA-FORJA-001 v3.1 — DSC-G-008 v3 AMARILLO_CON_OBSERVACIONES**

Adelante con D1 no-SQL. Reconcilia §3.1 y dispara `gh pr ready 133`. T1-Alfredo decide si esperar reconciliación o autorizar tú independiente.
