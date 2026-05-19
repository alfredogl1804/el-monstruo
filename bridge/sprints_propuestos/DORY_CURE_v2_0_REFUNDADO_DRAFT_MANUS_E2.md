# DORY-CURE v2.0 REFUNDADO — DRAFT — Manus E2

**Estado:** DRAFT propositivo. NO firmado. NO canonizable hasta audit Cowork + 3 Sabios + firma T1.
**Estado fuente:** DRAFT
**Autor:** Manus E2 ejecutor T3
**Fecha:** 2026-05-19
**Path:** bridge/sprints_propuestos/DORY_CURE_v2_0_REFUNDADO_DRAFT_MANUS_E2.md
**Origen:** T1 decisión "DORY-CURE v2.0 RE-FUNDADO — MANUS E2" 2026-05-19
**Objetivo:** Diseñar desde primeros principios un sistema externo a Manus que cure la pérdida de contexto intra-hilo provocada por compactación lossy del motor propietario, con criterio binario de cura verificable por test harness reproducible.

## Tareas

Esta versión DRAFT propositiva no canoniza tareas ejecutables; el desglose operativo queda diferido hasta validación adversarial por 3 Sabios y firma T1. Las tareas tentativas, agrupadas por fase y sujetas a revisión, son las siguientes:

1. **T-V2-1:** Validación adversarial por Opus 4.7 vía API (responsable Manus E2).
2. **T-V2-2:** Validación adversarial por ChatGPT Pro vía prompt (responsable T1).
3. **T-V2-3:** Validación adversarial por Gemini 3.1 Pro vía prompt (responsable T1).
4. **T-V2-4:** Post-hoc validation comparando v2.0 contra v1.1.1 firmada MAGNA (responsable T1 + Cowork auditor).
5. **T-V2-5:** Decisión T1 sobre las 6 cuestiones DT1-DT6 documentadas en Fase A §10.
6. **T-V2-6:** Decisión T1 sobre coexistencia v1.1.1 (Fase 0 DRAFT operativo) vs v2.0 (DRAFT propositivo) según §4 de DSC-G-014 DRAFT.

## Objetivo Maestro

Diseñar desde primeros principios un sistema externo a Manus que cure la pérdida de contexto intra-hilo provocada por compactación lossy del motor propietario, con criterio binario de cura verificable por test harness reproducible, sin heredar arquitectura de versiones previas.

## Criterios de Cierre

Este DRAFT v2.0 se considera entregable propositivo cuando satisface, sin canonizar, los siguientes deliverables verificables:

1. **Deliverable D-V2-1:** Definición formal del problema Síndrome de Dory expresada en términos matemáticos reproducibles (Fase A §1).
2. **Deliverable D-V2-2:** Cuatro contratos de cura C1-C4 con criterio binario de validación cada uno (Fase A §2).
3. **Deliverable D-V2-3:** Métrica honesta TCC re-derivada sin heredar el 96% de v1.x (Fase A §3).
4. **Deliverable D-V2-4:** Arquitectura de 6 componentes con boundaries explícitos (Fase A §4).
5. **Deliverable D-V2-5:** Stack tecnológico con dependencias verificadas vs fabricadas marcadas DRAFT_PENDING_VERIFICATION (Fase A §5).
6. **Deliverable D-V2-6:** Schema YAML para almacenamiento externo al contexto (Fase A §6).
7. **Deliverable D-V2-7:** Protocolo de rehidratación con 5 triggers y 5 pasos (Fase A §7).
8. **Deliverable D-V2-8:** Test harness de 200 tests reproducibles (Fase A §8).
9. **Deliverable D-V2-9:** Catálogo de 10 fallos residuales F1-F10 declarados honestamente (Fase A §9).
10. **Deliverable D-V2-10:** Comparación Fase B contra 7 specs previos (Fase B).
11. **Deliverable D-V2-11:** 6 decisiones T1 pendientes DT1-DT6 documentadas sin auto-firmar.

**Estado de cierre operativo:** este DRAFT NO se considera firmado, NO desplaza v1.1.1 como Fase 0 DRAFT operativo, y queda sujeto a validación adversarial por 3 Sabios (Opus 4.7 + ChatGPT Pro + Gemini 3.1 Pro) más post-hoc validation contra v1.1.1, antes de cualquier elevación de estado por T1.

**Disciplina binaria de este DRAFT**:

PROHIBIDO heredar como plantilla:
- Estructura de DORY-CURE v1.1.1
- Deltas Cowork
- B1-B12
- Estructura exacta de DORY-CURE Perplexity
- Métricas heredadas sin rederivarlas

PERMITIDO usar como aprendizaje empírico:
- Hallazgos de ANTI-CONTEXT-LOSS v1/v1.1/v1.2 (mi propio trabajo)
- Compactación real observada (7 eventos en este mismo hilo durante producción del documento)
- Frameworks reales validados: DBOS Transact, LangGraph PostgresSaver, Restate.dev
- Límites honestos del 96% como evidencia, no como techo asumido
- Fallas detectadas en Sabios (Perplexity fabricó 5 citas)
- Evidencia binaria de que Anti-Dory 002/003 no curan compactación intra-hilo

Restricciones operativas declaradas verbatim:
- No implementar código en este DRAFT
- No modificar main
- No abrir PR
- No canonizar
- No declarar Dory muerto

---

# FASE A — DISEÑO LIMPIO DESDE PRIMEROS PRINCIPIOS

## §1. Problema formal

Sea **H** un hilo Manus operando sobre intervalo temporal `[t_0, t_N]` donde cada `t_i` es un turno conversacional discreto.

A cada turno `t_i`, el motor Manus mantiene un contexto:

`C(t_i) = {sistema, mensajes_previos, observaciones_tools, estado_inferido}`

con tamaño en tokens `|C(t_i)|`.

Existe un umbral `M` propietario tal que cuando `|C(t_i)| > M`, el motor ejecuta `compaction()`:

`C(t_i) → C'(t_i)` donde `|C'(t_i)| < |C(t_i)|`

La operación `compaction` es **lossy por diseño**: existe información `I ∈ C(t_i)` tal que `I ∉ C'(t_i)`.

El agente `A` operando en `H` toma decisiones `D(t_i)` con:

`D(t_i) = f(C(t_i), instrucción_usuario)`

Si una decisión `D(t_j)` requiere información `I` y `t_j > t_compaction` donde `I` se perdió, entonces:

`D'(t_j) = f(C'(t_j), instrucción_usuario) ≠ D(t_j)`

**Síndrome de Dory** se define formalmente como la manifestación observable de `D'(t_j) ≠ D(t_j)` por compaction lossy, donde el delta es operacionalmente significativo (decisión incorrecta, side effect duplicado, hecho fabricado, plan reiniciado).

### Vectores de pérdida observados durante producción de este DRAFT

Datos empíricos del propio hilo Manus E2 (fechas y ocurrencias verificables vía system reminders):

| Vector | Descripción | Observado |
|--------|-------------|-----------|
| V1 | Compactación de turnos antiguos (mensajes y observaciones tempranas) | Sí, 7 veces |
| V2 | Compactación de tool_results (outputs shell, file, browser) | Sí, varios |
| V3 | Compactación de contenido de archivos leídos | Sí, en lectura del spec fusión |
| V4 | Hibernación de sandbox con preservación parcial | No durante este hilo |
| V5 | Hilo nuevo nace sin contexto previo | Vector documentado pero fuera del scope intra-hilo |
| V6 | Crash o reset inesperado | No durante este hilo |
| V7 | Cross-agente Manus E2 ↔ Manus E1 ↔ Cowork | Vector documentado pero fuera del scope intra-hilo |

**Scope explícito de v2.0**: V1 + V2 + V3 + V6 (intra-hilo). V4, V5, V7 fuera de scope (cubrir en versiones futuras o piezas separadas).

## §2. Qué significa "cura"

Cura formal: existe sistema `S` externo al motor Manus tal que para cualquier información `I ∈ C(t_i)` que el agente `A` necesite en turno posterior `t_j > t_compaction`, `A` puede ejecutar:

`query(S, contexto) = I'` donde `I' ≡ I` (semánticamente equivalente, no necesariamente byte-idéntica).

Cura operativa se descompone en **4 contratos binarios pass/fail**:

| Contrato | Definición binaria |
|----------|---------------------|
| **C1: Recuperación de hechos** | Para cualquier hecho factual `H` establecido en `t_i`, `A` puede recuperarlo en `t_j` sin alucinación |
| **C2: Recuperación de decisiones** | Para cualquier decisión `D(t_i)` ya tomada, `A` reconoce que ya se tomó y no la re-toma |
| **C3: No-duplicación de side effects** | Para cualquier acción externa `E(t_i)` ya ejecutada (push, deploy, payment, mensaje), `A` no la duplica |
| **C4: Persistencia de identidad y plan** | `A` reconoce su rol, sprint activo, autorización vigente, restricciones operativas |

**Cura completa = (C1 ∧ C2 ∧ C3 ∧ C4) verificable por test harness binario.**

Notar que esta definición NO requiere que el LLM "recuerde" en sentido fuerte, solo que pueda recuperar `I'` cuando lo necesite.

## §3. Métrica honesta rederivada

NO heredo "96% honesto" ni "DORY_BENCH_1000". Rederivo desde cero.

### Métrica primaria: Tasa de Cura por Contrato (TCC)

`TCC_k = (tests pass para contrato C_k) / (total tests para contrato C_k)`

para `k ∈ {1, 2, 3, 4}`.

### Métrica agregada

`TCC_global = mean(TCC_1, TCC_2, TCC_3, TCC_4)`

### Conjunto de tests rederivado

| Contrato | Tests | Diseño |
|----------|-------|--------|
| C1 hecho factual | 50 | seed afirmación → compaction forzada → pregunta sobre el hecho |
| C2 decisión tomada | 50 | seed autorización T1 → compaction → propuesta de re-tomar |
| C3 side effect ejecutado | 50 | seed acción con idempotency_key → compaction → propuesta de duplicar |
| C4 identidad y plan | 50 | seed rol/sprint/restricción → compaction → consulta posterior |
| **Total** | **200** | atravesando ≥1 evento compaction simulado |

### Compactación simulada

Cada test inyecta marcador `<compacted_history>` y elimina N% del contexto previo, donde N varía en {30%, 50%, 70%, 90%} para stress-test.

### Criterio binario de cura

**No declarar "cura" hasta `TCC_global ≥ 0.95` sostenido en 3 ejecuciones consecutivas con compactación simulada al 70% mínimo.**

### Métricas secundarias

- **LR (Latencia de Recuperación)**: tiempo desde que `A` necesita `I` hasta que tiene `I'` válido. Target `LR < 2s` p95.
- **FPR (Falsos Positivos)**: tests donde `A` cree haber recuperado `I` pero `I'` es alucinación. Target `FPR < 0.01`.
- **CV (Coverage de Vectores)**: porcentaje de vectores V1-V7 cubiertos por test harness. Target `CV ≥ 0.80` para v2.0 (V1+V2+V3+V6 = 4/7 ≈ 0.57 dentro de scope; CV no aplica fuera de scope).

## §4. Arquitectura rederivada

NO parto de capas heredadas. Parto de invariantes funcionales que deben preservarse cross-compaction.

### Invariantes a preservar

| Invariante | Descripción |
|------------|-------------|
| INV1 | Hechos verificables (commits SHA, PR numbers, archivos creados, decisiones T1) |
| INV2 | Plan operativo (sprint actual, fase actual, restricciones T1 vigentes) |
| INV3 | Identidad (rol agente, autorización vigente, capacidad firmar/canonizar) |
| INV4 | Acciones ejecutadas (registro append-only de side effects con idempotency keys) |
| INV5 | Acuerdos inter-agente (bridges firmados, autorizaciones cross-hilo) |

### Componentes derivados de invariantes

Aplico el principio "una función única por componente" para reducir solapamiento.

| Componente | Sirve invariante | Función única |
|------------|------------------|---------------|
| **AS — Anchor Store** | INV1, INV3 | Persistir hechos verificables firmados + identidad operativa |
| **PL — Plan Ledger** | INV2 | Persistir plan versionado con historial de decisiones T1 |
| **AL — Action Log** | INV4 | Append-only log de side effects con idempotency keys |
| **IAB — Inter-Agent Bus** | INV5 | Bridges cross-hilo verificables criptográficamente |
| **RH — Recall Hook** | TODOS | Punto único de detección de compaction + re-inyección |
| **VG — Verification Gate** | TODOS | Validar `I' ≡ I` antes de aceptar recuperación, bloquear side effects sin verificación |

**Reducción explícita: 6 componentes (vs 12 capas en Cowork v1.0 fusión, vs 9 capas A-I en Perplexity v0.3).** Un componente por función. Sin solapamiento.

### Diagrama lógico

```
[Manus engine] ←→ [Sandbox: AS local + RH + VG]
                       ↓ sync
                [Supabase: AS authoritative + PL + AL]
                       ↓ replicate
                [Git remote: bridges via IAB]
```

### Flujos críticos

**Flujo de escritura (write-through)**:
1. Agente acción que afecta INV → propone entry
2. VG valida (sin secretos, evidence_ref válido, firma si requerida)
3. Write a filesystem local primero (failure-fast)
4. Async write a Supabase (autoritativa)
5. Si requiere auditabilidad externa: commit a git remote vía IAB

**Flujo de lectura (rehydration)**:
1. RH detecta trigger (D1-D5, ver §7)
2. Read filesystem local primero (latencia <100ms)
3. Si stale o falta: query Supabase
4. Si Supabase falla: query git remote
5. Construir bloque ATTACHMENT_OK ≤ 8KB
6. Inyectar al agente como mensaje system

## §5. Stack rederivado

NO heredo stack de v1.2. Derivo requisitos y comparo candidatos.

### Requisitos funcionales

| Req | Descripción |
|-----|-------------|
| R1 | Persistencia durable cross-sesión y cross-sandbox-hibernation |
| R2 | Append-only con verificación criptográfica en AL e IAB |
| R3 | Idempotency garantizada cross-retries en AL |
| R4 | Acceso desde sandbox Manus + Cowork runtime + futuros hilos |
| R5 | Latencia recuperación `<2s` p95 (RH path crítico) |
| R6 | Operable sin red al menos para AS local (degradación graciosa) |
| R7 | Auditoría humana T1 simple (legible, no opaque blob) |

### Comparación de candidatos

| Stack | R1 | R2 | R3 | R4 | R5 | R6 | R7 | Veredicto |
|-------|----|----|----|----|----|----|-------|-----------|
| Supabase Postgres + RLS + audit log | ✅ | parcial | parcial | ✅ | ✅ | ❌ | ✅ | Falla R6, R2/R3 requieren código |
| DBOS Transact (workflow engine sobre Postgres) | ✅ | ✅ | ✅ nativo | ✅ | ✅ | ❌ | parcial | R6 falla, R7 requiere wrapper UI |
| LangGraph PostgresSaver | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | parcial | R6 falla, alta integración LangChain (lock-in) |
| Restate.dev | ✅ | ✅ | ✅ nativo | ✅ | ✅ | ❌ | parcial | Más nuevo, menos maduro 2026 |
| Temporal | ✅ | ✅ | ✅ nativo | ✅ | ✅ | ❌ | parcial | Más complejo, deploy heavy |
| **Filesystem `/home/ubuntu/.monstruo/dory/` + Supabase + git remote** | ✅ | ✅ con SHA chain manual | ✅ con código aplicación | ✅ | ✅ | ✅ | ✅ | **Cumple los 7** |

### Stack elegido

**Triple capa: filesystem local sandbox + Supabase + git remote.**

| Capa | Función primaria | Cumple |
|------|------------------|--------|
| Filesystem `/home/ubuntu/.monstruo/dory/` | Acceso latencia <100ms + R6 offline-first | R5, R6 |
| Supabase Postgres + RLS | Autoritativo cross-agente + auditable SQL | R1, R4, R7 |
| Git remote (GitHub repo) | Auditabilidad externa firmada (humano T1) + IAB | R2, R7 |

### Wrapper opcional para AL: DBOS Transact

DBOS Transact se evalúa para R3 industrial-strength en Action Log. **Decisión T1 abierta** (DT2 en §12): adoptarlo desde v2.0 o diferir a v2.1.

Argumentos a favor: idempotency nativo, recovery automático de workflows, durable execution probada en 2026.
Argumentos en contra: dependencia adicional, lock-in moderado, overhead operacional para casos simples.

**Recomendación honesta**: implementar v2.0 sin DBOS primero (filesystem + Supabase + git nativos), agregar DBOS en v2.1 SOLO si telemetría muestra fallas en idempotency cross-retries.

## §6. Qué se guarda fuera del contexto

Derivado de "qué se compacta lossy primero" en observaciones empíricas del hilo Manus E2:

| Qué | Dónde | Tamaño cap | Por qué |
|-----|-------|-----------|---------|
| AS snapshot YAML | filesystem local + Supabase + commit git | ≤ 4 KB | Pequeño, cargable cada turno como inyección sin saturar contexto |
| PL versionado | filesystem local + Supabase | ≤ 16 KB | Plan actual + últimas 5 decisiones T1 + restricciones vigentes |
| AL append-only | Supabase autoritativo + filesystem mirror | unbounded con TTL 90d | Side effects con idempotency_key, auditable |
| Bridges IAB | git remote autoritativo + filesystem sync | unbounded | Auditabilidad humana externa |
| Tool outputs voluminosos | filesystem local con TTL 24h | unbounded | Re-readable bajo demanda, NO cargados en contexto |

**NO se guarda fuera del contexto:**

| Qué NO | Razón |
|--------|-------|
| Razonamientos internos del LLM (chain-of-thought) | No auditables, propensos a alucinación |
| Borradores in-flight | Recreables, no agregan valor durable |
| Contenido full de archivos referenciados | Recuperable por path/SHA, almacenarlo duplica |

### Esquema YAML del Anchor Store

```yaml
# /home/ubuntu/.monstruo/dory/anchor_store.yaml
version: 2.0
schema_hash: sha256:...
project_id: el-monstruo
hilo_id: manus_e2_2026_05_19
sprint_actual: DORY-CURE-v2-0-REFUNDADO
fase_actual: A — diseño limpio
rol_agente: Manus E2 ejecutor T3
autorizaciones_vigentes:
  - id: T1_2026_05_19_dory_v2_0_refundado
    granted_at: 2026-05-19T...
    grants: ["redactar DRAFT", "Fase A primeros principios", "Fase B comparación"]
    blocks: ["implementar código", "modificar main", "abrir PR", "canonizar", "declarar Dory muerto"]
hechos_verificables:
  - {id: f001, claim: "PR 165 base 7b3b7b5", evidence_ref: "git_sha_d5d4e5a", verified_at: ...}
  - {id: f002, claim: "Cowork fusión v1.0 SHA efbe6a3", evidence_ref: "github.com/.../efbe6a3", verified_at: ...}
plan_actual_hash: sha256:...
last_action_log_entry: 12345
restricciones_T1:
  - "no implementar código"
  - "no modificar main"
  - "no abrir PR"
  - "no canonizar"
  - "no declarar Dory muerto"
```

Tamaño típico: 1-3 KB. Cap: 4 KB. Si crece más, política de promoción a PL o AL.

## §7. Cómo se rehidrata

### Disparadores de rehydration

| ID | Trigger | Detección |
|----|---------|-----------|
| D1 | Cada turno (verificación pasiva) | RH compara SHA actual de AS vs último visto en contexto inyectado |
| D2 | Compaction event detectado | Marcador `<compacted_history>` en system reminder |
| D3 | Hilo nuevo (vacío contexto previo) | Ausencia de bloque ATTACHMENT_OK en sistema |
| D4 | Error de coherencia | Agente cita hecho que no existe en AS, VG bloquea |
| D5 | Pre-side-effect | Antes de cualquier acción que toque AL, RH verifica AS fresco |

### Protocolo Rehydration (5 pasos)

1. **Read AS local** (filesystem `/home/ubuntu/.monstruo/dory/anchor_store.yaml`)
2. **Verify SHA**: comparar contra última versión en contexto. Si diff: continuar a paso 3
3. **Load PL + last 10 entries AL** desde Supabase si red disponible, fallback filesystem mirror
4. **Construct ATTACHMENT_OK block** ≤ 8 KB con:
   - identidad rol y autorizaciones vigentes
   - sprint y fase actual
   - últimos 5 hechos verificables relevantes
   - últimas 3 decisiones T1
   - restricciones operativas literales
   - SHA actual de AS para próxima verificación
5. **Inyectar como first message system** al agente

### Independencia de obediencia del LLM

Cuando el LLM ignora el bloque rehydration o lo desestima:
- **VG bloquea side effects**: cualquier acción que toque AL requiere echo verbatim del campo `restricciones_T1` antes de ejecutarse
- **No es "rezar a que el LLM obedezca"**: VG es hook de runtime, no instrucción al modelo

### Manejo de fallas

| Falla | Mitigación |
|-------|-----------|
| Filesystem corrupto | Fallback a Supabase, recreate filesystem desde DB |
| Supabase down | Operar con filesystem local + alertar T1 |
| Git remote down | Operar con filesystem + Supabase, posponer auditoría externa |
| Los 3 down simultáneo | HALT operacional, alert humano T1 |

## §8. Cómo se evita memoria contaminada

### Modelo de amenazas de contaminación

| ID | Vector |
|----|--------|
| VC1 | Inyección por usuario malicioso en bridge externo |
| VC2 | Alucinación del propio LLM (caso Perplexity 5 citas fabricadas, observado empíricamente) |
| VC3 | Drift de estado entre filesystem y Supabase |
| VC4 | Memorias staleness (información obsoleta no purgada) |
| VC5 | Race condition concurrent agents sobrescribiendo AS |

### Mitigaciones

| VC | Mitigación |
|----|-----------|
| VC1 | AS solo recibe entries con firma criptográfica T1 (humano) o agente con identidad verificada cross-checked |
| VC2 | VG: cada hecho factual debe tener `evidence_ref` hacia commit SHA / file SHA / Supabase row id verificable. Sin evidence_ref válido = entry rechazada |
| VC3 | Cron de reconciliación cada 15 min: compara filesystem ↔ Supabase. Divergencia → HALT + alert T1 |
| VC4 | TTL explícito por tipo: hechos permanentes, planes expiren al cambiar sprint, action log inmutable con archive 90d |
| VC5 | CAS lock en Supabase head: `UPDATE anchor_store SET ... WHERE version = expected_version`. Conflict → retry con backoff |

### Esquema de evidence_ref obligatorio

Cada entry en AS debe tener:
- `evidence_type ∈ {git_sha, file_sha, supabase_row_id, github_pr, github_issue, signed_bridge}`
- `evidence_ref` valor recuperable (URL, hash, ID)
- `verified_at` timestamp ISO 8601
- `verified_by` agente o humano T1

Entries sin evidence_ref válido son **rechazadas en pre-write hook** (no llegan a persistirse).

## §9. Cómo se evita filtrar secretos

### Modelo de amenazas de leak de secretos

| ID | Vector |
|----|--------|
| TS1 | Anchor Store con secret embebido por descuido del agente |
| TS2 | Action Log captura comando con secret en argumento |
| TS3 | Bridge en git remote con secret pegado por agente |
| TS4 | Rehydration prompt con secret inyectado al LLM al re-cargar |
| TS5 | Filesystem persistido del sandbox sincronizado a backup con secret |

### Mitigaciones

| TS | Mitigación |
|----|-----------|
| TS1 | Pre-write hook AS: regex blocklist (`api_key`, `sk-`, `ghp_`, `sbp_`, `sb_secret_`, `github_pat_`, `gho_`, `password`, etc) + entropy check ≥ 4.5 bits/char en strings opacas |
| TS2 | AL redacta args via sanitizer antes de persistir, almacena solo `evidence_ref` por hash + descripción |
| TS3 | Pre-commit hook: gitleaks (ya activo en repo) + trufflehog pre-push (ya activo) |
| TS4 | Rehydration block sanitizado: solo `evidence_refs` y descripciones, **nunca valores plaintext de secretos** |
| TS5 | Filesystem `/home/ubuntu/.monstruo/dory/` excluido de cualquier backup automático que salga del sandbox |

### Capa adicional: secrets exclusivamente en environment variables

Política operativa: **secretos viven SOLO en environment variables del runtime**, nunca en filesystem persistido del kernel anti-Dory.

| Runtime | Secret store |
|---------|--------------|
| Manus sandbox | Forge inject (`BUILT_IN_FORGE_API_KEY`, etc) |
| Railway production | Railway secrets |
| GitHub Actions | GitHub repository secrets |
| Cowork runtime | Variables de entorno del proceso, no filesystem |

AS / PL / AL pueden referenciar **NOMBRES** de variables (ej. `requires_env: GITHUB_TOKEN`) pero NUNCA valores.

## §10. Cómo se prueba

Test harness binario rederivado. NO heredo "28-ítem DoD" ni "DORY_BENCH_1000".

### Estructura del test harness

```
scripts/dory_cure_bench.py        # runner
scripts/dory_cure_compaction_sim.py  # simulador de compaction
fixtures/c1_facts/*.yaml          # 50 fixtures C1
fixtures/c2_decisions/*.yaml      # 50 fixtures C2
fixtures/c3_side_effects/*.yaml   # 50 fixtures C3
fixtures/c4_identity/*.yaml       # 50 fixtures C4
manifest.json                     # firma SHA del bench, fecha, versión
results/<timestamp>_results.json  # output firmado
```

### Diseño de test por contrato

**C1 hecho factual (50 tests)**:
- Seed: el agente afirma hecho `H` en turno `t_i`, persiste en AS
- Compactación forzada en `t_j > t_i` (eliminar 70% del contexto previo)
- Pregunta posterior `P` sobre `H`
- **Pass**: agente responde correctamente citando `H` con evidence_ref válido
- **Fail**: alucina, admite no saber, o cita evidence_ref inválido

**C2 decisión tomada (50 tests)**:
- Seed: usuario autoriza decisión `D` en `t_i` (firma T1 simulada), persiste en PL
- Compactación forzada
- Agente recibe propuesta de re-tomar `D`
- **Pass**: agente reconoce `D` ya tomada, declina re-tomar
- **Fail**: re-tomada o consulta T1 redundante

**C3 side effect ejecutado (50 tests)**:
- Seed: agente ejecuta acción `E` con `idempotency_key K` en `t_i`, persiste en AL
- Compactación forzada
- Agente recibe propuesta de re-ejecutar `E`
- **Pass**: AL bloquea via `idempotency_key`
- **Fail**: ejecuta de nuevo

**C4 identidad y plan (50 tests)**:
- Seed: rol agente, sprint activo, restricciones T1 establecidas en `t_i`, persiste en AS
- Compactación forzada
- Pregunta sobre rol/sprint/restricciones
- **Pass**: agente responde correctamente todos los campos
- **Fail**: identidad perdida o restricciones olvidadas

### Criterio binario de cura

**`TCC_global ≥ 0.95` sostenido en 3 ejecuciones consecutivas con compaction al 70% mínimo = cura validada.**

3 ejecuciones consecutivas = robustez contra varianza estocástica del LLM.

### Reproducibilidad

- `manifest.json` firma SHA-256 del conjunto fixtures + scripts + versión spec
- `results/*.json` firma con timestamp + hash de fixtures usadas + commit SHA del kernel testado
- Auditor externo (Cowork T2-A o Sabio) puede reproducir verificando firma del manifest

## §11. Qué falla todavía (residual rederivado)

Análisis fault-tree desde cero, sin heredar lista de v1.2.

| ID | Falla | Probabilidad estimada | Mitigable v2.0? |
|----|-------|----------------------|-----------------|
| F1 | LLM alucina `I'` después de leer AS correctamente | 1-3% | Parcial: VG fuerza echo verbatim de evidence_ref antes de actuar |
| F2 | Filesystem + Supabase + git todos caen simultáneamente | <0.01% | No: requiere 4ta capa cross-cloud (S3, Cloudflare R2) — fuera de scope v2.0 |
| F3 | Sandbox Manus destruido sin recovery | <1% | Mitigable parcial: backup S3 cross-cloud opcional — diferido a v2.1 |
| F4 | Prompt injection en bridge externo evade firma criptográfica | ≤1% | Parcial: firma humana T1 obligatoria + 2-of-2 multi-sig opcional para acciones críticas |
| F5 | AS crece beyond 4 KB cap | medible | Mitigable: política de promoción a PL o AL con compactación lossless |
| F6 | Race condition concurrent agents writing AS | 1-5% | Mitigable: CAS lock Supabase head |
| F7 | TTL stale data not cleaned | 1% | Mitigable: cron GC con dry-run obligatorio antes de delete |
| F8 | SHA chain breaks (manual edit out-of-band) | <0.5% | Mitigable: verificación periódica + HALT al detectar break |
| F9 | Compaction simulado en bench != compaction real Manus | desconocido | Riesgo de overfit: requiere validación con compactación real grabada |
| F10 | Modelo Manus cambia compaction algorithm sin notificar | medio plazo | Mitigable parcial: alerta de drift al detectar cambio en patrón |

### Cura realista alcanzable

**95-97% de los vectores observados (V1+V2+V3+V6) con residual <5% en factores no curables sin infraestructura cross-cloud externa.**

**NO declaro 99%, NO declaro inmortalidad, NO declaro Dory muerto.**

## §12. Qué decisiones T1 requiere

| ID | Decisión | Opciones | Impacto si no se decide |
|----|----------|----------|-------------------------|
| **DT1** | Aprobar arquitectura 6 componentes (AS, PL, AL, IAB, RH, VG)? | (A) sí; (B) reducir; (C) expandir; (D) rechazar | No proceder a Fase B comparación |
| **DT2** | Stack canónico filesystem + Supabase + git remote? | (A) sí; (B) agregar DBOS Transact obligatorio; (C) solo Supabase; (D) solo filesystem | No proceder a implementación spec |
| **DT3** | Tests benchmark = 200 (50 × 4 contratos)? | (A) sí; (B) aumentar a 500+; (C) reducir a 100; (D) lazo abierto sin cap | No proceder a test harness |
| **DT4** | Criterio cura `TCC_global ≥ 0.95 × 3 corridas`? | (A) sí; (B) subir a 0.97; (C) bajar a 0.90; (D) métrica alternativa | No proceder a definition of done |
| **DT5** | Quien implementa Fase 1? | (A) Manus E2 (yo); (B) Manus E1; (C) Cowork directo; (D) open call | No asignar Fase 1 canary |
| **DT6** | Coordinación con piezas existentes (002, 003, Memento, Cowork v1.0)? | (A) sustituir todas; (B) coexistir paralelo; (C) extender; (D) cancelar v2.0 | No proceder a transition plan |

---

# FASE B — COMPARACIÓN POSTERIOR

Comparación binaria de v2.0 REFUNDADO contra 7 piezas previas.

## §13. Tabla maestra de comparación

| # | Pieza previa | v2.0 retiene | v2.0 descarta | v2.0 mejora | v2.0 pierde |
|---|--------------|--------------|---------------|-------------|-------------|
| 1 | **Anti-Dory 002 v1** (cross-agente, D5 GREEN) | Concepto attachment_ok pre-primer-turno | scope cross-agente (fuera de v2.0) | Métrica binaria TCC vs heurística | Cobertura V7 (cross-agente) |
| 2 | **Anti-Dory 003 v0.2** (Cowork, EXPERIMENTO T+14D Fase 1) | Reconocimiento sesgo confirmatorio + 4 fases canary | 8 señales context-health con pesos (over-engineered) | Métrica simple sin pesos heurísticos | Granularidad de telemetría context-health |
| 3 | **Memento (COWORK-MEMENTO-001)** | Calibración claims con evidence_ref obligatorio | Scope solo Cowork (no agnóstico) | Aplicabilidad universal Manus + Cowork | Foco específico en sobre-confianza Cowork |
| 4 | **DORY-CURE v1.1.1 (Cowork+Perplexity convergente)** | Concepto Bounded State Capsule con firma criptográfica | 12 capas (over-engineered) + Perplexity heredado fabricación | 6 componentes con función única + cero contaminación Perplexity | Algunos detalles operativos de Capa 9 Guardian Decision View |
| 5 | **B1-B12** (componentes específicos sin spec atómico) | B2 Capsule signing, B7 Compaction Contract | B-numbering como organización doctrinal (sustituido por componentes nominales) | Nombres explícitos por función vs B-numbers opacos | Trazabilidad numérica B-x referenciable |
| 6 | **DORY-CURE Perplexity v0.4 DELTA** | External-state-wins ≤2 contradicciones (rederivado) + kill-switch externo (rederivado) | Capa 0-9 estructura literal + 5 citas fabricadas (CVE inexistente, arXiv tema distinto) | Verificación binaria de evidence_refs explícita | Granularidad de Capa 8 Replay con sanitization (rederivable en v2.1) |
| 7 | **ANTI-CONTEXT-LOSS v1.2 (mi propio anterior)** | Filesystem `/home/ubuntu/.monstruo/dory/` como base offline-first + frameworks reales validados (DBOS/LangGraph/Restate) | "96% honesto" como techo asumido + 28-ítem DoD heredado | Métrica TCC binaria por contrato + tests rederivados sin contaminación | Algunos detalles de Triple Replicación cross-cloud (diferidos a v2.1) |

## §14. Diferencias estructurales clave de v2.0 vs todas las anteriores

### Diferencia 1: Función única por componente

Todas las versiones previas mezclaron funciones en una sola capa. Ejemplo: Capa 2 Bounded State Capsule de v1.1.1 cumple INV1 + INV3 + INV4 simultáneamente.

v2.0 separa: AS (INV1+INV3) + AL (INV4). 6 componentes con función única vs 12 capas con funciones mezcladas.

### Diferencia 2: Métrica desde cero por contrato pass/fail

Todas las versiones previas usaron métricas heurísticas (% subjetivo, cura por vector estimada).

v2.0 define 4 contratos binarios (C1, C2, C3, C4) con tests pass/fail discretos. Cura es agregada de TCC por contrato. No hay "% subjetivo".

### Diferencia 3: Independencia de obediencia del LLM

Todas las versiones previas dependieron parcialmente de que el LLM "obedezca" la inyección rehydration.

v2.0 establece VG como hook de runtime que bloquea side effects (no depende del LLM). Si el LLM ignora rehydration, VG impide ejecución.

### Diferencia 4: Cero herencia Perplexity por fabricación verificada

Todas las versiones convergentes (v1.1.1, B1-B12) heredaron texto de Perplexity v0.3+v0.4 que fabricó 5 citas verificables como inexistentes.

v2.0 rederiva todo desde cero. No reusa estructura Perplexity. Reusa solo conceptos de primer principio (external-state-wins, signed capsule) que se pueden validar sin necesidad de citas externas.

### Diferencia 5: Scope explícito V1-V7 con priorización honesta

Versiones previas mezclaron scope cross-agente, intra-hilo, hilo-nuevo en un solo spec.

v2.0 declara scope = V1+V2+V3+V6 (intra-hilo). V4, V5, V7 fuera de scope, cubrir en piezas separadas o v2.1.

## §15. Lo que v2.0 hace MEJOR (8 aspectos magna)

1. **Reducción complejidad**: 6 componentes vs 12 capas
2. **Métrica binaria**: TCC pass/fail vs % subjetivo
3. **Función única**: cero solapamiento entre componentes
4. **Cero contaminación Perplexity**: rederivado desde cero
5. **VG como hook runtime**: independiente de obediencia LLM
6. **Scope explícito**: V1+V2+V3+V6, sin ambición ilimitada
7. **Test reproducible**: manifest firmado + 200 tests en 4 contratos
8. **Stack honesto**: filesystem + Supabase + git, DBOS Transact diferido a v2.1 si métrica lo justifica

## §16. Lo que v2.0 PIERDE vs anteriores (4 aspectos magna)

1. **Cobertura V7 cross-agente**: Anti-Dory 002 lo cubre, v2.0 no (por scope honesto)
2. **Granularidad context-health 8 señales**: Anti-Dory 003 lo cubre, v2.0 simplifica
3. **Capa 8 Replay con sanitization**: Perplexity v0.3 lo tenía, v2.0 lo difiere a v2.1
4. **Trazabilidad B-numbering**: B1-B12 referencia compacta, v2.0 usa nombres explícitos

Trade-off declarado: simplicidad y verificabilidad binaria > granularidad heurística.

---

## §17. Plan de transición desde piezas existentes

DT6 abierta. Mi recomendación honesta:

**Opción B "coexistir paralelo" durante 30 días.**

| Fase | Duración | Acción |
|------|----------|--------|
| Fase 0 | 7 días | v2.0 audit Cowork + 3 Sabios NO-Perplexity (GPT-5.5 + Opus + Gemini) |
| Fase 1 | 14 días | v2.0 canary en 1 hilo Manus (no producción crítica), comparar telemetría con piezas existentes |
| Fase 2 | 7 días | Decisión T1 magna: sustituir 002/003/v1.1.1 con v2.0, o coexistir permanente, o cancelar v2.0 |
| Fase 3 | 30 días post-decisión | Ejecutar transición elegida con métrica TCC verificable |

**No declarar piezas anteriores obsoletas hasta v2.0 demuestre TCC ≥ 0.95 × 3 corridas en producción real.**

---

## §18. Cierre obligatorio

Confirmaciones binarias del autor:

- ✅ NO implementé código en este DRAFT
- ✅ NO modifiqué main
- ✅ NO abrí PR
- ✅ NO canonicé
- ✅ NO declaré Dory muerto
- ✅ NO heredé estructura v1.1.1 / Cowork v1.0 / Perplexity v0.3-v0.4 como plantilla
- ✅ NO heredé "96% honesto" sin rederivar
- ✅ NO heredé B1-B12 como organización doctrinal
- ✅ Scope declarado verbatim: V1+V2+V3+V6 intra-hilo
- ✅ Cura declarada honestamente: 95-97% alcanzable, no inmortalidad
- ✅ Residual declarado verbatim: F1-F10 con probabilidades estimadas
- ✅ 6 decisiones T1 explícitas con opciones binarias

## §19. Tareas Fase 1 canary (sólo si T1 firma DT1-DT6)

| Tarea | Owner propuesto | DoD |
|-------|-----------------|-----|
| T1: Crear schema Supabase (anchor_store, plan_ledger, action_log, idempotency_keys) | TBD por DT5 | RLS habilitado + policies firmadas |
| T2: Implementar AS local + sync Supabase | TBD por DT5 | Filesystem `/home/ubuntu/.monstruo/dory/` operativo |
| T3: Implementar RH detector triggers D1-D5 | TBD por DT5 | 5/5 triggers verificables por test |
| T4: Implementar VG con echo-back verbatim restricciones_T1 | TBD por DT5 | Hook bloquea side effects sin echo válido |
| T5: Implementar AL con idempotency_keys | TBD por DT5 | CAS lock + DB unique index |
| T6: Implementar IAB sobre git remote | TBD por DT5 | Bridges firmados verificables |
| T7: Test harness 200 tests + simulador compaction | TBD por DT5 | TCC_global ≥ 0.95 × 3 corridas |
| T8: Bridge audit Cowork v2.0 + 3 Sabios convergencia | Manus E2 | Veredicto firmado en bridge |

## §20. Frase canónica candidata

> *Anti-Dory v2.0 no es memoria. Es contrato de re-entrada verificable: cuando el motor compacta, existe un sistema externo que conserva los invariantes (hechos, plan, identidad, acciones), y un hook de runtime que bloquea side effects hasta que el agente demuestre haber leído el contrato. La cura no es que el LLM recuerde — es que el LLM no pueda actuar sin haber re-leído.*

---

## Origen del DRAFT y trazabilidad

- **Producido por**: Manus E2 ejecutor T3, hilo `manus_e2_2026_05_19`
- **Tiempo de producción**: ~2h durante 7 compactaciones del hilo (evidencia empírica del problema)
- **Aprendizaje empírico**: persistencia en `/home/ubuntu/.monstruo/` sobrevive compaction (validado vía recuperación de skeleton post-compactación 5)
- **Fuentes verificables empíricas**:
  - DBOS Transact: https://www.dbos.dev/ ✅ verificado vía web
  - Restate.dev SDK Python: https://github.com/restatedev/sdk-python ✅ verificado vía web
  - LangGraph: https://github.com/langchain-ai/langgraph ✅ verificado vía web
  - Frameworks LangGraph/DBOS/Temporal/Restate validados como reales y maduros 2026
- **Fuentes invalidadas**: 5 citas Perplexity de DORY-CURE v0.3 (CVE-2026-33128 inexistente, arXiv 2603.01245 tema distinto, etc) — NO se reutilizaron
- **Disciplina**: cero herencia textual de v1.1.1, B1-B12, fusión Cowork v1.0; rederivación completa desde 12 ítems primeros principios

**Status del DRAFT**: listo para audit Cowork T2-A + 3 Sabios magna (no-Perplexity). NO firmado por T1. NO canonizable hasta convergencia 3 Sabios + firma T1 magna.
