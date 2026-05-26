**Estado:** Aspiracional.

No es un DSC firmado. Es articulación T1 pendiente de firma magna. La firma del operador (o de Cowork para el Anexo DSC-S-012) genera el contrato canónico al completar el bloque YAML correspondiente.

---
id: T1-MAGNA-007
proyecto: EL-MONSTRUO
tipo: decision_arquitectonica_magna
titulo: "Estructura del Evidence Pack del Monstruo: ¿se mantiene `bridge/sprints_propuestos/` + `bridge/sprints_completados/` o se migra a `bridge/missions/<MISSION_ID>/`? Decisión T1 magna no delegable."
estado: pendiente_firma
fecha_articulacion: 2026-05-26
articulado_por: manus_b (Hilo B — ejecutor técnico)
fuentes_verificadas:
  - filesystem:el-monstruo/bridge/sprints_propuestos/ (decenas de archivos canonizados)
  - filesystem:el-monstruo/bridge/sprints_completados/
  - filesystem:el-monstruo/bridge/control_tower/ (subdirectorio activo con jerarquía propia)
  - filesystem:el-monstruo/bridge/thread_immunity/ (sesiones de hilo activas, ejemplo: 8af84475-598b-4d14-aa79-7d5e0c0c589c)
  - canon:DSC-G-008 v2 (audit pre-cierre Cowork sobre archivos del bridge)
  - canon:DSC-S-001..005 (no-secrets-in-bridge)
  - prompt_externo:FORJA-OMEGA propuesta de ChatGPT pidiendo `bridge/missions/<MISSION_ID>/`
  - codigo:tablero-campana/sprints/registry.yaml (50 sprints consolidados, post Sprint 91.16)
cruza_con:
  - T1-MAGNA-005 (Forja shadow→enforce — los receipts Merkle deciden dónde se commitean)
  - T1-MAGNA-006 (PR Drafts autónomos — define dónde caen los outputs del embrion)
  - DSC-G-008 v2 (audit pre-cierre)
  - DSC-S-001..005 (cero secrets en bridge)
  - Sprint 91.16 (Sprint Registry como fuente única de verdad)
---

# T1-MAGNA-007 — Estructura del Evidence Pack: bridge/sprints_* vs bridge/missions/

## Detonante

El repo `el-monstruo` tiene hoy una estructura canonizada de dos rieles:

1. **`bridge/sprints_propuestos/`** — archivos markdown con sprints propuestos pero no firmados.
2. **`bridge/sprints_completados/`** — archivos markdown con evidencia y postmortem de sprints terminados.
3. **`bridge/control_tower/<fecha>/<actor>/`** — torre de control con docs operativos por jornada.
4. **`bridge/thread_immunity/<session_id>/`** — receipts de identidad de hilo.

A esto se suma post Sprint 91.16:

5. **`sprints/registry.yaml`** — fuente única de verdad de los 50 sprints (32 PROPOSED + 3 SIGNED + 15 DONE), validada por GitHub Action.

Total: **5 carpetas distintas en `bridge/` + 1 archivo canónico en `sprints/`** que cooperativamente forman el "Evidence Pack" del Monstruo.

ChatGPT, en el prompt FORJA OMEGA, propuso colapsar todo a una nueva ruta:

> *"bridge/missions/AUTONOMY-OMEGA-001/0_intent.md, 1_orders/, 2_assemblies/, 3_executions/, 4_evidence/, 5_court/, 6_outcomes.md"*

Esta propuesta es **doctrinalmente significativa**. No es renombrar carpetas: es decidir si la unidad de trabajo del Monstruo es **el sprint** (concepto firmado en Sprint 91.16, atado al registry) o **la misión** (concepto de FORJA OMEGA donde un sprint puede generar varias misiones, o varias sprints pueden colapsar en una misión).

La pregunta es magna porque cualquier decisión rompe doctrina existente:

- Si se queda con `sprints_*`, FORJA OMEGA tiene que renunciar a su nomenclatura.
- Si se migra a `missions/`, el registry recién cerrado en Sprint 91.16 se queda sin home claro y los DSCs vigentes que apuntan a `bridge/sprints_*` pierden trazabilidad.
- Si se híbrida, se mantiene la complejidad de tener dos sistemas cooperando.

## Pregunta a firmar

> **¿La unidad canónica de trabajo del Monstruo es el SPRINT (atado al registry, persistido en `bridge/sprints_*/`) o la MISIÓN (concepto FORJA OMEGA, persistido en `bridge/missions/`)? ¿O ambos coexisten?**

Esta es una pregunta **ontológica**, no de organización de carpetas:

> **¿Mi memoria operativa se reorganiza por un tercero (ChatGPT/FORJA OMEGA) o conserva el orden que yo construí (registry + sprints_*)?**

## Opciones a firmar

### Opción A — STATU QUO. Se mantiene `bridge/sprints_*/` + `sprints/registry.yaml` como única estructura canónica

**Qué significa:** Toda evidencia, todo PR, todo postmortem, todo receipt Merkle, todo intent del embrion cae bajo la jerarquía existente. La nomenclatura "misión" se rechaza explícitamente como término canon. FORJA OMEGA, si se ejecuta, mapea sus conceptos a `bridge/sprints_*/` con prefijos (ej: `FORJA-OMEGA-VISUAL-1` como sprint registrado en el registry).

**Beneficios:**

- Cero migración. Cero ruptura de doctrina vigente.
- DSCs existentes (DSC-G-008 v2, DSC-S-001..005) siguen aplicando sin cambios.
- Sprint 91.16 (registry como fuente única) queda intacto.
- El embrion (T1-MAGNA-006) escribe a `bridge/embrion_patches/` o `bridge/sprints_propuestos/` según opción ganadora — ya hay home definido.
- La GitHub Action `sprint-registry-validate.yml` (mergeada hoy en PR #214) sigue funcionando sin cambios.

**Costos:**

- FORJA OMEGA pierde su nomenclatura propuesta. Sus 932 líneas de prosa se simplifican a "es un sprint con prefijo FORJA-OMEGA-*".
- Algunos conceptos de FORJA OMEGA (ej: "Sovereign Court verdict por misión") tienen que reformularse como "verdict por sprint".
- Si en el futuro un sprint genera varias unidades de trabajo paralelas (ej: un sprint Forja con 3 envelopes simultáneos), se necesita sub-estructura. Hoy no existe.
- El concepto "Mission" es semánticamente más rico (una misión puede atravesar sprints), pero se pierde.

**Ganadores:** estabilidad doctrinal, continuidad operativa, no romper Sprint 91.16. **Perdedor:** expresividad semántica para flujos multi-sprint.

---

### Opción B — MIGRACIÓN TOTAL. Se mueve todo a `bridge/missions/<MISSION_ID>/` y se deprecan `bridge/sprints_*/`

**Qué significa:** Se acepta la propuesta de ChatGPT/FORJA OMEGA. Cada unidad de trabajo se identifica con `MISSION_ID` y vive bajo `bridge/missions/<MISSION_ID>/`. Los sprints existentes se migran (se les asigna `MISSION_ID`). El `sprints/registry.yaml` se renombra `missions/registry.yaml` o se transforma en `bridge/missions/_index.yaml`.

**Beneficios:**

- Estructura unificada: una misión = una carpeta con todo (intent, orders, assemblies, executions, evidence, court, outcomes).
- Permite expresar trabajo no-sprint (ej: "investigación exploratoria que cruza 3 sprints").
- Compatible con la propuesta FORJA OMEGA al pie de la letra.
- Permite agregar metadata rica por misión (paradigm, OM, capa transversal, embriones asignados, power lane, budget).

**Costos:**

- **Rompe Sprint 91.16 a 24 horas de cerrarse.** El registry recién canonizado y la GitHub Action recién mergeada (PR #213, #214) tendrían que retirarse o reescribirse.
- Migración masiva: decenas de archivos en `bridge/sprints_propuestos/` y `bridge/sprints_completados/` deben moverse, renombrarse, mantener trazabilidad histórica.
- DSCs existentes que apuntan a `bridge/sprints_*` necesitan emisión de superseding DSCs (DSC-G-008 v3, DSC-S-006..010 actualizados).
- `THREAD_IMMUNITY_RECEIPT` apunta a `bridge/thread_immunity/<uuid>/` — coexistiría con `bridge/missions/`. Cierta inconsistencia residual.
- Riesgo de "decisión a impulso ChatGPT": ChatGPT no auditó los DSCs vigentes antes de proponer la migración.
- Costo de comunicación interna: cada hilo nuevo tiene que aprender la nueva nomenclatura.

**Ganadores:** unidad estructural, expresividad semántica. **Perdedores:** estabilidad doctrinal post-Sprint 91.16, trazabilidad histórica, costo de migración.

---

### Opción C — COEXISTENCIA. `sprints/registry.yaml` se mantiene como manifiesto canónico; `bridge/missions/` se introduce como capa de ejecución concreta

**Qué significa:**

- **Nivel manifiesto (registry)**: `sprints/registry.yaml` sigue siendo la fuente única de qué sprints existen, su estado (PROPOSED/SIGNED/IN_PROGRESS/DONE), su paradigm, OM, capa transversal. Validado por CI. **No se toca.**

- **Nivel ejecución (missions)**: cuando un sprint pasa a estado `IN_PROGRESS`, se le asigna un `MISSION_ID` (puede ser igual al sprint ID, o sufijado: `MOBILE_0_SMP-01`, `MOBILE_0_SMP-02` para múltiples ejecuciones). Bajo `bridge/missions/<MISSION_ID>/` viven los artefactos vivos: orders del operador, assemblies de embriones, evidence Merkle, court verdicts.

- **Nivel histórico (sprints_completados)**: cuando una misión termina, se genera un resumen consolidado en `bridge/sprints_completados/<sprint_id>_<fecha>.md` que apunta a las misiones que ejecutaron ese sprint. Las misiones quedan archivadas en `bridge/missions/_archive/<MISSION_ID>.tar.gz`.

- **Nivel propuesta (sprints_propuestos)**: se mantiene como hoy para sprints en estado PROPOSED que aún no tienen misión. Cuando uno se firma y arranca ejecución, nace su primera misión.

**Beneficios:**

- **No rompe Sprint 91.16**: el registry y la CI quedan intactos.
- Acepta la riqueza semántica de FORJA OMEGA en la capa de ejecución.
- Permite un sprint con múltiples misiones paralelas (ej: 3 envelopes Forja activos simultáneamente).
- Trazabilidad clara: registry → missions → sprints_completados.
- DSCs existentes siguen aplicando con un anexo: "cuando se diga 'archivo en bridge/sprints_*', léase 'archivo en bridge/missions/* o bridge/sprints_*' según el momento del ciclo".
- Compatible con T1-MAGNA-005 firmado en cualquier opción: los receipts Merkle viven en `bridge/missions/<MISSION_ID>/4_evidence/` cuando hay misión activa, en `bridge/sprints_completados/` cuando ya cerró.
- Compatible con T1-MAGNA-006 firmado en cualquier opción: los patches/PRs del embrion se atan a una misión.

**Costos:**

- Más complejo de explicar: 3 niveles en lugar de 1.
- Requiere DSC-G-008 v3 (audit pre-cierre extiende su scope a `bridge/missions/`).
- El esquema de `<MISSION_ID>` debe canonizarse (es subset de Sprint ID? o totalmente independiente?).
- Migración menor pero real: hay que escribir el "consolidador" que cuando una misión cierra genera el resumen para `bridge/sprints_completados/`.

**Ganadores:** estabilidad + expresividad. **Perdedores:** simplicidad estructural, claridad para hilos nuevos.

---

### Opción D — COEXISTENCIA INVERTIDA. `bridge/missions/` solo para flujos autónomos del embrion; sprints humanos siguen en `bridge/sprints_*`

**Qué significa:**

- Sprints ejecutados por hilos humanos (Manus, Cowork) → `bridge/sprints_*/` como hoy.
- Misiones ejecutadas autónomamente por el embrion (post T1-MAGNA-006 firmado) → `bridge/missions/<MISSION_ID>/`.

Es decir: la nomenclatura "mission" se reserva para trabajo del embrion, "sprint" para trabajo de hilos humanos.

**Beneficios:**

- Separación clara por origen del trabajo. Auditable visualmente: ¿qué hizo el embrion vs qué hicieron los humanos?
- No rompe Sprint 91.16 ni doctrina existente.
- Permite que el embrion (T1-MAGNA-006 D) escriba a `bridge/missions/` sin contaminar `bridge/sprints_*`.
- Compatible con DSCs vigentes.
- ChatGPT/FORJA OMEGA tiene su nomenclatura preservada para el caso autónomo.

**Costos:**

- Crea una asimetría doctrinal: "mismo trabajo, diferente carpeta según quién lo hizo". Si Manus toma una misión del embrion para corregirla, ¿se mueve a `bridge/sprints_*`?
- Si un sprint humano genera autónomamente sub-trabajo del embrion, ¿el sprint vive en `sprints_*` y la sub-misión en `missions/`? Cruce de árboles.
- Trazabilidad fragmentada: la línea temporal de un OM se ve solo combinando ambos árboles.

**Ganadores:** semántica clara por origen, no rompe doctrina. **Perdedores:** asimetría, fragmentación de trazabilidad.

---

## 3. Comparativa criterio a criterio

| Criterio | A — Statu quo | B — Migración total | C — Coexistencia jerárquica | D — Coexistencia por origen |
|---|---|---|---|---|
| Rompe Sprint 91.16 | **no** | **sí (crítico)** | **no** | **no** |
| Acepta nomenclatura FORJA OMEGA | no | sí | sí | sí (parcial) |
| Costo de migración | **0** | **alto** | medio | bajo |
| DSCs existentes siguen aplicando sin cambios | **sí** | no | sí (con anexo) | sí |
| Permite sprint con múltiples misiones paralelas | **no** | **sí** | **sí** | parcial |
| Permite trazabilidad histórica continua | sí | requiere reescritura | **sí** | parcial (fragmentada) |
| Complejidad para hilo nuevo | **baja** | media | media-alta | alta (asimetría) |
| Compatibilidad con T1-MAGNA-005 (cualquier opción) | sí | sí | **sí** | sí |
| Compatibilidad con T1-MAGNA-006 D | sí (patches en sprints_propuestos) | sí | sí | **sí (claridad máxima)** |
| Riesgo de "decisión apurada por ChatGPT" | n/a | **alto** | bajo | bajo |
| Reversibilidad si falla | n/a | **muy baja** | media (consolidador es reversible) | alta |
| Cumple regla doctrinal "no inventar rueda si ya existe" | **sí** | no | parcial | parcial |
| Expresividad semántica | baja | **alta** | **alta** | media |

---

## 4. Recomendación de Hilo B (manus_b — modo detractor)

**Recomiendo Opción C — COEXISTENCIA JERÁRQUICA.**

Justificación honesta y verificable:

1. **Sprint 91.16 cerró hace menos de 24 horas**. Migrar el registry hoy sería tirar trabajo recién hecho. Cualquier opción que rompa Sprint 91.16 es autoboicot puro.

2. **La propuesta de ChatGPT no es trivialmente equivocada — es semánticamente rica**. La distinción "una misión puede tener varias ejecuciones, una ejecución puede contribuir a varios objetivos" es real y útil. Rechazarla 100% (Opción A) es subóptimo.

3. **C separa lo permanente de lo efímero**:
   - Permanente: el registry (¿qué sprints existen y en qué estado están?). Cambia raramente, validado por CI.
   - Efímero: las misiones (¿qué se está ejecutando ahora mismo?). Pueden vivir días, semanas, y luego archivarse.
   
   Esa separación coincide con la separación natural entre **planificación** y **ejecución**, que ya está en la doctrina del Monstruo (paradigm + OM + capa son planificación; bridge/* es ejecución).

4. **C no requiere que ChatGPT haya tenido razón sobre todo**. Solo le da home a la capa de ejecución concreta sin destruir la planificación canónica. Es la versión disciplinada de su propuesta.

5. **El consolidador (cuando una misión cierra → genera resumen en sprints_completados) es ~150 líneas Python y resuelve la trazabilidad histórica**. Es trabajo pequeño con valor alto.

6. **C es la única opción compatible con todas las firmas posibles de T1-MAGNA-005 y T1-MAGNA-006**. Eso reduce el riesgo de tomar firmas magnas en orden equivocado.

7. **D es seductor pero asimétrico**. La regla "mismo trabajo, diferente carpeta según quién lo hizo" se rompe la primera vez que un humano corrige una misión del embrion. Termina siendo C disfrazado.

8. **B es el path que ChatGPT propuso por desconocimiento**. Si supiera que Sprint 91.16 cerró ayer, no habría propuesto migración total. **No firmar B hoy es honrar la disciplina de "auditar antes de construir"** que tu propio skill canoniza.

Opción A es defendible si decides que la doctrina existente es suficiente expresivamente. Opción C es defendible si reconoces que FORJA OMEGA tiene un punto válido sobre la riqueza de "missions" que `sprints` por sí solo no captura.

---

## 5. Lo que se espera de Cowork (canonizador)

Si Alfredo firma Opción C:

1. **Redactar y firmar DSC-G-008 v3** que extienda audit pre-cierre Cowork a `bridge/missions/<MISSION_ID>/`.
2. **Definir esquema canónico de `MISSION_ID`** (¿es `<SPRINT_ID>-<NN>`? ¿es UUID? ¿es un slug humano-legible? ¿se persiste en `bridge/missions/_index.yaml`?).
3. **Especificar qué metadata mínima debe tener cada misión** (sprint padre, embrión/hilo ejecutor, power lane, budget, fecha apertura, fecha cierre prevista).
4. **Aprobar el formato del consolidador** que genera `bridge/sprints_completados/<sprint_id>_<fecha>.md` cuando una misión cierra.
5. **Decidir política de archivado**: ¿`bridge/missions/_archive/` con `.tar.gz`? ¿se borran después de N días? ¿se guardan permanentemente?

Si Alfredo firma Opción A:

1. Cowork emite **canon explícito** de que `mission` no es término canónico. Eso queda firmado para que ChatGPT/FORJA OMEGA en sus próximos prompts no lo asuman.
2. Se reescribe en `_dsc_contracts_index.yaml` con el rechazo explícito.

Si Alfredo firma Opción B (no recomendado):

1. Se requiere DSC de migración, plan de comunicación interna, retraction de Sprint 91.16, y ~3 días de trabajo Manus + Cowork para reorganizar.

---

## 6. Lo que se espera de ChatGPT (estratega — iteración 002)

**No le pidas decidir entre A/B/C/D.** Pídele:

1. **Comparativa con sistemas equivalentes**: ¿cómo organizan repos de evidence pack los proyectos análogos? GitOps de Argo CD usa `applications/`. Devin usa `runs/`. Cognition usa `tasks/`. ¿Qué patrones de éxito y fracaso hay?
2. **Diseñar el esquema de `MISSION_ID`** asumiendo Opción C: humano-legible vs UUID vs híbrido. Pros y contras.
3. **Articular la metadata mínima** de una misión: campos obligatorios, campos opcionales, ejemplo concreto en YAML.
4. **Diseñar el consolidador** (~150 líneas Python) que cuando misión cierra genera resumen en `bridge/sprints_completados/`.
5. **Reconocer públicamente** en el manifesto FORJA OMEGA v2 que su propuesta original (`bridge/missions/<MISSION_ID>/0_intent.md`...) era una mejora pero que la versión disciplinada es Opción C, no Opción B. Esto evita futura presión hacia migración total.

---

## 7. Decisión a firmar

```yaml
decision_t1_magna_007:
  estructura_evidence_pack_ganadora: ___  # A | B | C | D
  fecha_firma: ___
  firmante: Alfredo Góngora
  justificacion_corta: ___

  # Solo si firma C:
  esquema_mission_id: ___  # ej: "<SPRINT_ID>-<NN>" | "uuid" | "slug-humano"
  metadata_obligatoria_mision: ___  # lista de campos
  ruta_canonica_misiones: "bridge/missions/<MISSION_ID>/"
  ruta_archivado: "bridge/missions/_archive/"
  consolidador_a_completados: ___  # path del script
  fecha_implementacion_consolidador: ___

  # Solo si firma D:
  separacion_origen: "humanos -> sprints_*; embrion -> missions/"
  manejo_caso_cruce: ___  # qué pasa cuando humano corrige misión del embrion

  # Solo si firma B:
  plan_migracion: ___  # path de doc detallado
  fecha_retraccion_sprint_91_16: ___
  retraccion_pr_213_214: ___  # cómo se invalida la GitHub Action

  # Aplica a todas:
  fecha_revision_60_dias: ___  # auto: fecha_firma + 60d
  rollback_si_falla: ___
```

Al firmar:

1. Se commitea como `T1_MAGNA_007_ESTRUCTURA_BRIDGE_MISSIONS_FIRMADA.md`.
2. Manus B implementa la opción ganadora.
3. Cowork firma DSCs derivados según opción.
4. Se actualiza `MONSTRUO_GENOME.yaml` con `evidence_pack_structure: A | B | C | D`.
5. Se actualiza `AGENTS.md` con la nueva regla si es C/D (informar a hilos nuevos sobre la dualidad).

---

## 8. Bloqueos cruzados resueltos por esta firma

- **FORJA-OMEGA-VISUAL Bloque B**: el componente `EvidenceConveyor` del Tablero necesita saber dónde leer evidence (sprints_completados/ vs missions/_active/). Se desbloquea con cualquier firma A/C/D. Con B requiere reescritura.
- **T1-MAGNA-005 enforce**: los receipts Merkle viven donde firme esta T1.
- **T1-MAGNA-006 D (patches embrion)**: si firma A, los patches viven en `bridge/embrion_patches/`. Si firma C, viven en `bridge/missions/<MISSION_ID>/2_assemblies/embrion_patches/`. Si firma D, viven en `bridge/missions/`. Si firma B, viven en `bridge/missions/`.
- **Sprint 91.16**: queda intacto si firma A/C/D, queda invalidado si firma B.
- **GitHub Action `sprint-registry-validate.yml`** (PR #214 mergeado hoy): sigue funcionando si firma A/C/D, requiere rollback si firma B.

---

## 9. Notas finales

Este documento NO firma por ti. Solo te entrega las cuatro opciones con criterios verificables y la recomendación de Hilo B con justificación.

La firma es tuya, T1 magna, no delegable.

**Recordatorio**: ChatGPT propuso B sin auditar el repo. Si firmas B, estás cediendo el orden de tu memoria operativa a un sabio que no audita antes de proponer. **No es una decisión equivocada per se** — pero es una decisión que vale la pena tomar conscientemente, no por inercia narrativa.

**Recomendación operativa**: si dudas entre A y C, firma A primero. Si en 30 días Sprint 91.16 demuestra ser insuficiente expresivamente para flujos multi-misión paralelos, retoma esta T1 y firma C. La inversión perdida en A→C es ~150 líneas Python (el consolidador). La inversión perdida en B si se equivoca es 1 sprint completo y la disciplina del Sprint 91.16 destruida.

Cuando firmes, responde en este hilo o agrega el bloque YAML al final del documento. Manus B aplica el cambio en menos de 1 día si la opción es A/C/D, en 3 días si es B.

---

**Documento generado por:** Manus B (cuenta `manus_b` — Hilo B ejecutor técnico)
**Fecha de generación:** 2026-05-26
**Bloquea:** estructura del Evidence Pack del Monstruo, FORJA-OMEGA-VISUAL Bloque B EvidenceConveyor, integridad post-Sprint 91.16
**Tiempo estimado de lectura:** 6 minutos
**Thread Immunity Session:** 8af84475-598b-4d14-aa79-7d5e0c0c589c
