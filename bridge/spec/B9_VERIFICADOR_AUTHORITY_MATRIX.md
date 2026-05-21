# B9-E1 — VERIFICADOR Authority Matrix (N×N) Design

**Estado:** `DRAFT_T1_PENDING`
**Autor:** Manus E2 (autor NO-Cowork)
**Fuente normativa:** `bridge/control_tower/2026-05-20/manus_e2/B6_B12_DESIGN_CLOSURE_PACK_v0_2.md` §5
**Rama:** `control-tower/2026-05-20-b9-evidence-pack`
**Fecha:** 2026-05-20
**Lote:** ANTI_DORY_PARALLEL_GATES_BATCH_001

> Este documento NO canoniza B9. Es un design pack derivado y consolidado desde el closure v0.2 firmado. No implementa runtime. No modifica main.

---

## §1 Definición (verbatim closure v0.2 §5.1)

Este gate canoniza la matriz de autoridad y degradación entre **VERIFICADOR-001** (componente runtime de validación criptográfica), **Memento Validator** (capa de validación de hechos del Protocolo Memento), **Guardian Decision View** (capa de decisión humana asistida del Sprint 27+), y **firma T1 manual**. Cada par tiene escenarios de acuerdo y desacuerdo; este gate define quién gana en cada caso, y qué ruta de degradación toma el sistema cuando un componente falla.

---

## §2 Los 4 actores

| Actor | Rol primario | Naturaleza | Failure mode |
|-------|--------------|------------|--------------|
| **VERIFICADOR-001** | Validación criptográfica de firmas ed25519 sobre payloads | Componente runtime determinístico | Caída del componente, latencia >timeout, error interno |
| **Memento Validator** | Validación de hechos contra fuente autoritativa (Supabase + bridge) | Capa de validación basada en estado canónico | Cuerpo legal Memento ausente, evolución de versión, Supabase down |
| **Guardian Decision View** | Decisión humana asistida del Sprint 27+ | Capa de decisión con HITL | Guardian caído, operador no disponible, cola saturada |
| **T1 firma manual** | Firma magna humana de Alfredo | Decisión humana definitiva | T1 incomunicado, fatiga decisional |

---

## §3 PASS criteria binarios (verbatim closure v0.2 §5.2)

| # | Criterio |
|---|----------|
| B9.1 | Matriz N×N completa entre los 4 actores documentada con resultado binario para cada celda (autoridad ganadora + razón). |
| B9.2 | Casos de empate o degradación tienen resolución verbatim documentada, sin "según contexto" ni cláusulas abiertas. |
| B9.3 | Caso "VERIFICADOR ALLOW + Memento DENY" tiene resolución binaria: **Memento gana**. Razón: Memento valida hechos contra fuente autoritativa (Supabase + bridge), VERIFICADOR solo valida firma criptográfica del payload; un payload firmado correctamente puede contener un hecho falso. |
| B9.4 | Caso "VERIFICADOR DENY + Guardian OVERRIDE" tiene resolución binaria: **Guardian no puede override sin escalación a T1**. Guardian puede solicitar review T1, pero no ejecutar la acción rechazada por VERIFICADOR sin firma T1 explícita en el run_id. |
| B9.5 | Caso "T1 firma manual + VERIFICADOR DENY" tiene resolución binaria: **T1 gana**, pero el evento se loggea como `T1_OVERRIDE_VERIFICADOR_DENY` con run_id, timestamp, razón verbatim escrita por T1, y se notifica a Cowork + Sabio auditor designado. |
| B9.6 | Ruta de degradación si VERIFICADOR-001 falla: el sistema entra en `VERIFICADOR_DEGRADED` ⇒ aplica B8 (DISABLED_FOR_MAGNA_ACTIONS), permite acciones no-magnas con warning, intenta failover a réplica VERIFICADOR-002 si existe. |
| B9.7 | Ruta de degradación si Memento Validator falla: VERIFICADOR sigue siendo autoritativo para firma criptográfica, pero ninguna acción magna se permite hasta que Memento se restaure o T1 firme override. |
| B9.8 | Ruta de degradación si Guardian Decision View falla: las acciones que requerían decisión humana asistida se ponen en cola de espera (`AWAITING_GUARDIAN`); no hay fallback a auto-decisión. |
| **B9.9 (CONTEO CORREGIDO v0.2)** | **Tests binarios para los 10 casos canónicos de la matriz** — 4 acuerdos + 2 desacuerdos críticos (B9.3, B9.4) + 1 override T1 (B9.5) + 3 degradaciones (B9.6, B9.7, B9.8) = **10 tests**. Cada test produce evidencia firmada. |

---

## §4 Matriz N×N (4 actores, 6 pares no-ordenados)

La matriz cubre los pares no-ordenados entre los 4 actores. Las celdas describen el resultado en caso de **acuerdo** y de **desacuerdo**.

### §4.1 Pares con ambos componentes operativos

| Par | Acuerdo (ambos ALLOW) | Acuerdo (ambos DENY) | Desacuerdo (A ALLOW + B DENY) | Desacuerdo (A DENY + B ALLOW) |
|-----|----------------------|----------------------|-------------------------------|-------------------------------|
| VERIFICADOR ↔ Memento | Acción procede; ambos validaron en su dominio. | Acción bloqueada; razón = unión de razones. | **B9.3: Memento gana** (hecho falso firmado correctamente). | **Memento gana** (acción no validada contra fuente autoritativa). |
| VERIFICADOR ↔ Guardian | Acción procede; firma OK + HITL OK. | Acción bloqueada; doble veto. | Guardian puede mejorar contexto pero no override sin T1. | **B9.4: Guardian NO override** sin escalación T1 (escalación obligatoria al fallo VERIFICADOR). |
| VERIFICADOR ↔ T1 | Acción procede; firma técnica + firma magna. | Acción bloqueada; T1 confirmó. | T1 puede aceptar acción a pesar de firma técnica (raro, requiere razón verbatim T1). | **B9.5: T1 gana**, evento `T1_OVERRIDE_VERIFICADOR_DENY` con notificación obligatoria. |
| Memento ↔ Guardian | Hechos OK + HITL OK ⇒ acción procede si VERIFICADOR no la bloquea. | Bloqueada por ambos. | Guardian puede solicitar review humana de los hechos en disputa; el resultado se loggea como decisión Memento amended (versionada). | Guardian no override Memento sin firma T1; las acciones quedan en `AWAITING_GUARDIAN` hasta resolución humana. |
| Memento ↔ T1 | Acción procede; hechos OK + firma magna. | Bloqueada por ambos. | T1 puede aceptar amendment Memento con razón verbatim; el bridge actualiza el cuerpo legal Memento con commit firmado. | **T1 gana**, pero abre review automático de los hechos en disputa para el siguiente sprint. |
| Guardian ↔ T1 | HITL OK + firma magna ⇒ acción procede si VERIFICADOR + Memento no bloquean. | Bloqueada por ambos. | T1 anula la objeción Guardian con razón verbatim. | T1 puede confirmar la objeción Guardian; el evento se loggea como `T1_HONORS_GUARDIAN_VETO`. |

### §4.2 Pares con degradación (un componente caído)

Las rutas de degradación están definidas en §5 (sección dedicada). Cada actor caído activa un modo distinto del sistema.

---

## §5 Rutas de degradación (B9.6, B9.7, B9.8)

### §5.1 VERIFICADOR-001 falla (B9.6)

Disparador: componente caído, latencia >timeout configurado, error interno persistente >3 reintentos.

Estado activado: `VERIFICADOR_DEGRADED`.

Comportamiento:

1. El sistema aplica políticas B8 — acciones magnas (categorías a-m) entran en `DISABLED_FOR_MAGNA_ACTIONS`.
2. Acciones no-magnas continúan con warning explícito al operador y al bridge.
3. Si existe réplica `VERIFICADOR-002` (decisión T1 pendiente, ver §9), el sistema intenta failover automático; si la réplica también está caída, queda en degradado total.
4. Alerta proactiva al operador y a Cowork T2-A con `incident_id` reproducible.
5. La recuperación de VERIFICADOR-001 dispara `VERIFICADOR_RESTORED` y reanuda operación normal previa verificación de integridad por VERIFICADOR-001 sobre el estado canon del bridge.

### §5.2 Memento Validator falla (B9.7)

Disparador: Supabase down, cuerpo legal Memento ausente, error de validación persistente.

Estado activado: `MEMENTO_DEGRADED`.

Comportamiento:

1. VERIFICADOR-001 sigue siendo autoritativo para firma criptográfica.
2. Ninguna acción magna procede hasta restauración de Memento o firma T1 verbatim que asuma el riesgo.
3. Acciones no-magnas pueden proceder con warning al operador.
4. Alerta proactiva con `incident_id`; intentos de reconexión a Supabase con backoff exponencial.

### §5.3 Guardian Decision View falla (B9.8)

Disparador: Guardian caído, operador no disponible, cola saturada >threshold.

Estado activado: `GUARDIAN_DEGRADED`.

Comportamiento:

1. Acciones que requerían decisión humana asistida se ponen en cola `AWAITING_GUARDIAN`.
2. **No hay fallback a auto-decisión** (regla binaria explícita: el sistema NO decide solo cuando Guardian es requerido por la matriz).
3. Si la cola supera `threshold_t1_escalation` (T1-pending, propuesta: 24 horas o 50 items, lo que ocurra primero), canal manual de escalación a T1.
4. Restauración de Guardian procesa la cola en orden FIFO.

### §5.4 Degradación cascada (múltiples actores caídos)

Si dos o más actores caen simultáneamente:

| Caída | Estado |
|-------|--------|
| VERIFICADOR + Memento | `DUAL_DEGRADED_HALT_MAGNA` — ninguna acción magna, no-magnas con doble warning |
| VERIFICADOR + Guardian | `DEGRADED_NO_HITL` — magnas off, no-magnas con warning, cola Guardian crece |
| Memento + Guardian | `DEGRADED_NO_FACTS_NO_HITL` — magnas off, no-magnas si VERIFICADOR ALLOW + warning |
| Los 3 no-T1 caídos | `FULL_DEGRADED_AWAITING_T1` — todo en cola hasta T1 firma override o componentes se restauran |

T1 firma magna siempre puede mover acciones de cualquier cola con razón verbatim, dejando log inmutable.

---

## §6 Lista canónica de los 10 tests B9.9

| # | ID test | Caso | Tipo |
|---|---------|------|------|
| 1 | B9.9.T1 | VERIFICADOR ALLOW + Memento ALLOW + Guardian ALLOW + T1 ALLOW ⇒ acción procede | acuerdo trivial |
| 2 | B9.9.T2 | VERIFICADOR DENY + Memento DENY ⇒ acción bloqueada por unión de razones | acuerdo trivial |
| 3 | B9.9.T3 | Guardian DENY + T1 DENY ⇒ acción bloqueada | acuerdo trivial |
| 4 | B9.9.T4 | VERIFICADOR ALLOW + Guardian ALLOW ⇒ acción procede si Memento no bloquea | acuerdo trivial |
| 5 | B9.9.T5 | VERIFICADOR ALLOW + Memento DENY ⇒ **Memento gana** (B9.3) | desacuerdo crítico |
| 6 | B9.9.T6 | VERIFICADOR DENY + Guardian OVERRIDE_REQUEST ⇒ **escalación obligatoria a T1** (B9.4) | desacuerdo crítico |
| 7 | B9.9.T7 | VERIFICADOR DENY + T1 firma magna OVERRIDE ⇒ **T1 gana** con evento `T1_OVERRIDE_VERIFICADOR_DENY` (B9.5) | override T1 |
| 8 | B9.9.T8 | VERIFICADOR-001 caído ⇒ `VERIFICADOR_DEGRADED` + acciones magnas off (B9.6) | degradación |
| 9 | B9.9.T9 | Memento Validator caído ⇒ `MEMENTO_DEGRADED` + magnas off hasta restauración (B9.7) | degradación |
| 10 | B9.9.T10 | Guardian Decision View caído ⇒ acciones en `AWAITING_GUARDIAN`, NO auto-decisión (B9.8) | degradación |

Total: 4 acuerdos triviales (T1-T4) + 2 desacuerdos críticos (T5-T6) + 1 override T1 (T7) + 3 degradaciones (T8-T10) = **10 tests**.

> **Aclaración doctrinal v0.2:** v0.1 enunció "9 tests binarios" en B9.9 pero listó 10 casos. v0.2 corrige a 10 tests, alineado con el conteo real de casos.

---

## §7 FAIL criteria

- Matriz N×N incompleta o con celdas con cláusulas abiertas.
- Cualquiera de los casos B9.3, B9.4, B9.5 con resolución no-binaria.
- Ruta de degradación ausente para cualquiera de los 3 actores no-T1.
- **v0.2:** Tests B9.9 sin evidencia firmada (10 tests requeridos, no 9).
- Permiso de Guardian para override sin escalación a T1 (B9.4).
- Permiso de auto-decisión sin Guardian disponible (B9.8).

---

## §8 Riesgos identificados

- **R-B9-1: Matriz teórica vs comportamiento runtime.** Una matriz documentada puede no coincidir con el comportamiento implementado. Mitigación: tests B9.9 ejecutan los 10 casos sobre el runtime real, no sobre simulación.
- **R-B9-2: Cuerpo legal Memento ausente o evolucionando.** Memento Validator depende del Protocolo Memento canon; si el protocolo evoluciona, la celda "VERIFICADOR vs Memento" puede invertirse. Mitigación: B9 referencia versión de Memento por hash y se re-canoniza cuando Memento bumpea major.
- **R-B9-3: Override T1 abusado.** Si T1 ejerce B9.5 frecuentemente, VERIFICADOR pierde valor binario. Mitigación: notificación obligatoria a Cowork + Sabio auditor + log público (run_id reproducible).
- **R-B9-4: Cascada de degradación.** Si VERIFICADOR cae y Memento también está degradado, el sistema queda en `DISABLED_FOR_MAGNA_ACTIONS` total + cola Guardian llena. Mitigación: SLA mínimo de uptime cada componente + alerta proactiva al operador.
- **R-B9-5: Guardian Decision View como single-point.** Si Guardian es el único decidor humano-asistido, su caída bloquea decisiones. Mitigación: B9.8 cola `AWAITING_GUARDIAN` + canal manual de escalación a T1 si la cola se acumula >threshold.

---

## §9 Decisión T1 requerida

- **D-B9-1:** Aprobación verbatim de la matriz N×N B9.1 (§4 de este documento).
- **D-B9-2:** Confirmación de los 3 casos críticos B9.3, B9.4, B9.5 con resoluciones binarias.
- **D-B9-3:** Designación del Sabio auditor permanente para overrides T1 (propuesta: Opus 4.7 por familiaridad governance).
- **D-B9-4:** Decisión sobre existencia de réplica VERIFICADOR-002 (B9.6) — propuesta: sí, con failover automático activado.

---

## §10 Estado actual del gate

- **Veredicto:** `DRAFT_T1_PENDING`
- **Bloqueado por:** D-B9-1..D-B9-4 (firma magna T1).
- **No-runtime:** este pack es solo diseño documental; no produce B9-E3 (10 logs de tests) que requiere VERIFICADOR-001 + Memento + Guardian ejecutándose.
- **Productores no-runtime cubiertos:** B9-E1 (este archivo), B9-E2 (diagramas Mermaid en `B9_authority_decision_flows.mmd`), B9-E4 (procedimiento de escalación T1 en `B9_T1_ESCALATION_PROCEDURE.md`).
- **Próximo paso:** T1 firma decisiones D-B9-1..D-B9-4 ⇒ T1 redacta B9-E4 ⇒ VERIFICADOR + Memento + Guardian ejecutan los 10 tests ⇒ Sabio externo audita ⇒ T1 firma magna PASS.

---

## §11 Cross-refs

- **B8** la lista taxonómica (a)-(m) de acciones magna define qué bloquea VERIFICADOR_DEGRADED.
- **B6** firma ed25519 que valida VERIFICADOR; si B6 entra en `KEY_REVOKED`, VERIFICADOR no puede validar payloads ⇒ activación B9.6.
- **B11** Sabio auditor para B9-E3 y overrides T1 (propuesta: Opus 4.7) coincide con Sabio activo del trimestre B11.

---

**Firma magna pendiente.** Este documento es DRAFT y NO canoniza B9.
