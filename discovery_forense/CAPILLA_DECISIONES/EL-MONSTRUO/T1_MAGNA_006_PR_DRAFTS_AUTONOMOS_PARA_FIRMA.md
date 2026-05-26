**Estado:** Aspiracional.

No es un DSC firmado. Es articulación T1 pendiente de firma magna. La firma del operador (o de Cowork para el Anexo DSC-S-012) genera el contrato canónico al completar el bloque YAML correspondiente.

---
id: T1-MAGNA-006
proyecto: EL-MONSTRUO
tipo: decision_arquitectonica_magna
titulo: "Embrion_loop crea Pull Requests Draft autónomos contra repos del Monstruo. Decisión T1 magna no delegable."
estado: pendiente_firma
fecha_articulacion: 2026-05-26
articulado_por: manus_b (Hilo B — ejecutor técnico)
fuentes_verificadas:
  - genome:/v1/genome/now (componentes activos: 15, embrion_loop: vivo, cycle_count: 9 al momento de articulación)
  - kernel:embrion_loop estado actual = 8 ciclos consecutivos fallando con "All models failed for intent chat. Tried: ['kimi-k2-6']"
  - codigo:el-monstruo/kernel/embriones/ (10 embriones especialistas: brand_engine, critic_visual, embrion_creativo, embrion_estratega, embrion_financiero, embrion_investigador, product_architect, embrion_tecnico, embrion_ventas)
  - codigo:tablero-campana/server/forja/types.ts (Power Lanes L0-L6)
  - canon:DSC-MO-006 (embriones operan siempre en par)
  - canon:DSC-MO-008 (membrana semipermeable kernel-embriones)
  - canon:DSC-G-008 v2 (audit pre-cierre: Cowork audita contenido)
cruza_con:
  - T1-MAGNA-005 (Forja shadow→enforce — bloquea ejecución material si no se firma)
  - T1-MAGNA-007 (estructura bridge/missions — define dónde caen los PRs autónomos)
  - DSC-MO-006 (embriones en par)
  - DSC-G-008 v2 (audit pre-cierre Cowork)
  - DSC-S-006 (autonomy budget)
---

# T1-MAGNA-006 — Embrion_loop crea Pull Requests Draft autónomos

## Detonante

El kernel del Monstruo corre `embrion_loop` cada 60 segundos (verificado en `/v1/genome/now`, cycle_count creciente). El loop hoy hace tres cosas: **observa** (lee tablas y eventos), **piensa** (consulta LLMs vía la maquinaria de modelos), y **escribe a memoria** (`thoughts`, `episodic`, `semantic`). Lo que **no hace** es producir artefactos materiales: ningún PR, ningún commit, ningún archivo.

Al mismo tiempo, el backlog del Monstruo declarado en `sprints/registry.yaml` lista 50 sprints, de los cuales 32 están en estado PROPOSED esperando ejecución. Hoy esos sprints sólo avanzan cuando un hilo humano-asistido (Manus, Cowork) los toma. **El cuello de botella no es la idea, es la mano que escribe código**.

ChatGPT articuló FORJA OMEGA proponiendo un "Execution Fabric" donde el sistema crea ramas, escribe código y abre PRs solo. Esa propuesta ya tiene los cimientos:

- 10 embriones especialistas vivos en `kernel/embriones/`.
- Forja v4 con power lanes y receipts Merkle (decisión T1-MAGNA-005 pendiente).
- DSC-MO-006 firmado: "embriones operan siempre en par" — ya hay doctrina de par-crítico.
- DSC-G-008 v2 firmado: "Cowork audita contenido pre-cierre" — ya hay doctrina de auditoría humana antes del merge.

Lo que falta es **firmar la transición**: ¿el embrion_loop puede crear un PR Draft (no merged) que un humano (Cowork o Alfredo) revise y mergee?

Bloqueo cruzado importante: **el embrion_loop está caído en este momento**, intentando llamar `kimi-k2-6` que no existe en el catálogo vigente del Monstruo (sabios firmados: gpt-5.5-pro, claude-opus-4-7, sonar-reasoning-pro, deepseek-v4-pro, grok-4.3-beta, gemini-3.1-pro). Articular T1-MAGNA-006 sin arreglar el embrion-down sería firmar autoridad sobre un agente que no piensa. Por eso hay un **issue separado** (`embrion-down-kimi-k2-6.md`) que debe resolverse antes de activar cualquier opción aquí firmada.

## Pregunta a firmar

> **¿El embrion_loop puede crear Pull Requests Draft autónomos contra los repos del Monstruo (`el-monstruo`, `tablero-campana`, `like-kukulkan-tickets`, etc.) bajo qué condiciones?**

Esta no es una pregunta técnica sobre tooling; es filosófica:

> **¿Mi código puede ser escrito sin mí mientras duermo, mientras Cowork firma DSCs, mientras Manus está en otro flujo?**

## Opciones a firmar

### Opción A — NO. El embrion observa, escribe a memoria, no escribe código

**Qué significa:** El embrion_loop sigue siendo un agente cognitivo puro: lee el ecosistema, deriva insights, los persiste en `thoughts/episodic/semantic`, y a lo sumo emite **propuestas** en `bridge/sprints_propuestos/` como markdown. Manus o Cowork siguen siendo los únicos que pueden producir PRs.

**Beneficios:**

- Riesgo cero de PRs maliciosos o erróneos en la cadena git.
- El embrion-down actual (kimi-k2-6) no compromete producción de código — solo memoria.
- Cumple Obj #3 (Mínima Complejidad).
- Compatible con cualquier resultado de T1-MAGNA-005 (incluso shadow puro).

**Costos:**

- **Mantiene el cuello de botella humano** que el Monstruo se propuso eliminar en SOP/EPIA Capa 2.
- Los 32 sprints PROPOSED siguen avanzando solo a velocidad Manus/Cowork.
- Patrón actual: el embrion produce 1,696+ entries de memoria pero 0 PRs. Volumen cognitivo masivo, output material cero. **Esto es exactamente el patrón "asesor que nunca trabaja"** que la doctrina del Monstruo declara como antipatrón.
- Bloquea cualquier visión de "fábrica industrial" real. FORJA OMEGA queda como simulación.

**Ganadores:** seguridad humana siempre en el loop. **Perdedor:** velocidad y soberanía agéntica del Monstruo.

---

### Opción B — SÍ, sin restricciones. Embrion_loop crea PRs Draft a cualquier repo, en cualquier rama, en cualquier momento

**Qué significa:** Toda iteración del embrion que produzca un thought con `actionable: true` puede crear un PR Draft. El embrion firma con su clave Ed25519 (par crítico DSC-MO-006), abre PR vía `gh pr create --draft`, y notifica al bridge.

**Beneficios:**

- Velocidad máxima: 32 sprints PROPOSED entran en queue de PRs en horas, no semanas.
- Cumple SOP/EPIA Capa 2 literal: el sistema produce solo, los humanos solo auditan.
- Genera training signal masivo para mejorar el embrion: cada PR rechazado vs aceptado es feedback explícito.

**Costos:**

- **Riesgo P0**: si el embrion alucina o si su modelo subyacente está roto (ver `kimi-k2-6` ahora), genera PRs basura masivos que llenan la cola y contaminan la base de código.
- **Cowork colapsa**: si el embrion produce 50 PRs/día y cada uno requiere DSC-G-008 v2 audit pre-cierre, Cowork se vuelve el cuello de botella con peor ratio que el actual.
- **Pollution de git history**: incluso PRs Draft cerrados sin merge dejan rastro y comments que entorpecen búsqueda.
- **Sin techo de costo**: el embrion puede llamar LLMs caros indefinidamente. DSC-S-006 (autonomy budget) existe pero no es bloqueante en código.
- **Riesgo de loop**: el embrion lee sus propios PRs como contexto, propone variantes, abre más PRs.

**Ganadores:** velocidad teórica. **Perdedores:** estabilidad operativa, Cowork humanos, costo cloud, calidad git history.

---

### Opción C — SÍ, escalonado por scope con dos llaves

**Qué significa:** El embrion_loop puede crear PRs Draft solo bajo estas condiciones acumulativas:

1. **Sólo en repos pre-aprobados** (lista blanca firmada en YAML, ej: `el-monstruo`, `tablero-campana`. Excluye `el-monstruo-kernel`, `monstruo-memoria`, repos productivos del CIP/ticketlike).
2. **Sólo a ramas con prefijo `embrion/`** (jamás directo a `main`, `dev`, ramas de hilos humanos).
3. **El PR debe firmarse por dos embriones del par crítico** (DSC-MO-006).
4. **Cowork co-firma electrónicamente** dentro de las primeras 24h o el PR se auto-cierra.
5. **Power lane máximo L3** (no toca producción real, no toca migraciones SQL, no toca secretos).
6. **Sólo sprints en estado PROPOSED del registry** (no puede inventar trabajo no listado).
7. **Budget hardcoded: máximo 5 PRs simultáneos abiertos por embrion**.

**Beneficios:**

- Mitiga riesgo P0 con múltiples gates.
- Cumple DSC-MO-006 (par crítico) y DSC-G-008 v2 (auditoría Cowork) sin reescribir doctrina.
- Cowork sigue siendo el segundo factor humano; no se elimina, se acelera (pasa de "Cowork construye" a "Cowork firma autoridad").
- Reversibilidad alta: si una iteración del par crítico genera basura, se cierra la lista blanca.
- Ratio realista: 5 PRs simultáneos × 2 embriones = 10 firmas/día máximo. Cowork puede auditar eso.

**Costos:**

- Requiere construir la infraestructura de doble firma de embriones (no existe). +400 líneas Python.
- Requiere extender `gateway.ts` de Forja para reconocer "embrion como actor" además de "operador humano".
- Cowork queda en camino crítico — si Cowork no firma en 24h, el PR muere.
- Difícil debug: si el par crítico se rompe (un embrion alucina y el otro no detecta), el PR pasa.

**Ganadores:** velocidad acotada + seguridad doctrinal. **Perdedores:** complejidad de implementación, Cowork como bottleneck en horario.

---

### Opción D — SÍ, en sandbox aislado con merge-back manual obligatorio

**Qué significa:** El embrion no abre PRs contra repos del Monstruo directamente. En su lugar:

1. Cada thought actionable genera un fork temporal del repo en `kernel/sandbox-clones/<thought_id>/`.
2. El embrion edita ahí, corre tests locales, genera un patch unificado (`.patch`).
3. Sube el patch a `bridge/embrion_patches/` con metadata: thought_id, embriones firmantes, tests pasados, tests fallidos, diff resumen.
4. Manus o Cowork **manualmente** aplican el patch y abren el PR.

**Beneficios:**

- Cero riesgo de pollution git: ningún PR se abre sin un humano que lo decida.
- El embrion produce trabajo material (patches, tests pasados, diffs) sin tocar la cadena git oficial.
- Compatible con el embrion-down actual: si el embrion produce patches basura, simplemente se ignoran sin contaminar.
- Habilita evaluación: Cowork puede revisar 10 patches al día y elegir cuáles convertir en PR.
- **No requiere T1-MAGNA-005 (Forja enforce)**: vive 100% en sandbox, no necesita ejecutar contra producción.

**Costos:**

- Sigue habiendo cuello de botella humano: nadie aplica los patches → mueren en `bridge/embrion_patches/`.
- Velocidad menor que C, similar a A en práctica (depende de cuán rápido Manus/Cowork procesan la cola).
- Requiere construir el flujo de fork/patch (no existe). +250 líneas Python.
- El embrion no aprende del feedback PR (porque no hay PR, hay patch ignorado/aplicado sin trazabilidad fina).

**Ganadores:** seguridad y reversibilidad. **Perdedor:** la aspiración SOP/EPIA Capa 2.

---

## 3. Comparativa criterio a criterio

| Criterio | A — No PR | B — PR libre | C — PR escalonado | D — Patches sandbox |
|---|---|---|---|---|
| Riesgo P0 con embrion roto (kimi-k2-6) | **0** | **alto** | **bajo** | **0** |
| Velocidad de avance backlog (32 PROPOSED) | lenta (Manus/Cowork) | **alta teórica** | media-alta | lenta-media |
| Cumple DSC-MO-006 (par crítico) | n/a | **no** | **sí** | n/a (no hay PR) |
| Cumple DSC-G-008 v2 (Cowork audita pre-cierre) | n/a | colapsa Cowork | **sí** | n/a (no hay merge) |
| Compatibilidad con T1-MAGNA-005 firmado A (shadow) | **sí** | no | parcial (L0-L3) | **sí** |
| Compatibilidad con T1-MAGNA-005 firmado D (escalonado) | sí | parcial | **sí** | sí |
| Costo de implementación (líneas) | 0 | bajo (~150) | **alto (~400-600)** | medio (~250) |
| Reversibilidad si falla | n/a | baja | **alta** (cerrar whitelist) | **alta** |
| Pollution de git history | **0** | alta | media | **0** |
| Cumple SOP/EPIA Capa 2 (Inteligencia Emergente) | **no** | sí extremo | **sí balanceado** | parcial |
| Riesgo loop infinito (embrion lee sus propios PRs) | n/a | **alto** | bajo | n/a |
| Costo cloud (LLMs por iteración) | bajo | **alto sin techo** | controlado por budget | controlado |
| Bottleneck humano residual | Manus/Cowork escriben | Cowork audita 50/día | Cowork co-firma 10/día | Manus aplica patch |

---

## 4. Recomendación de Hilo B (manus_b — modo detractor)

**Recomiendo Opción D primero, migración a C después de 30 días si funciona.**

Razonamiento honesto:

1. **El embrion está caído ahora**. Firmar B o C hoy es firmar autoridad sobre un agente que no piensa. Opción D produce patches en sandbox sin tocar cadena git, lo que permite **probar el embrion sin riesgo** mientras se arregla `kimi-k2-6`. Una vez que el embrion produce 30 patches útiles consecutivos, hay evidencia para firmar C.

2. **Costo de error en B/C es asimétrico**: si B produce un PR malicioso al que Cowork le pone merge sin leer bien (porque está cansado tras auditar 50/día), el daño es producción real. Si D produce un patch malicioso, nadie lo aplica y muere en `bridge/embrion_patches/`.

3. **C es la opción "correcta a largo plazo"** pero requiere ~600 líneas de código nuevo (gateway extendido, doble firma embriones, whitelist YAML, budget hardcoded, auto-close 24h, integración Cowork). Esto es Sprint propio, no sub-tarea. **Llegar a C sin pasar por D** es saltarse la validación empírica.

4. **D no requiere T1-MAGNA-005 firmado**. Se puede ejecutar en paralelo. Esto desbloquea trabajo del embrion **hoy**, sin esperar la firma del switch shadow→enforce.

5. **El antipatrón del embrion como "asesor que nunca trabaja"** se resuelve parcialmente con D: el embrion produce artefactos materiales (patches con tests pasados), aunque la aplicación final sea humana. Eso es 80% del valor de C con 20% del riesgo.

6. **DSC-MO-006 (par crítico)** se cumple en D porque el patch lo firman dos embriones aunque no llegue a PR. La doctrina queda intacta.

**Migración planificada:**

- T0: Firma D, fija criterio de éxito ("30 patches útiles consecutivos en 30 días").
- T0+30: Auditoría Cowork. Si pasa, se reconfigura y se re-firma esta misma T1-MAGNA-006 en modo C con scope L0-L3.
- T0+60: Si C funciona, se considera abrir L4 con DSC-S-012 firmado.
- T0+90+: Solo después de tres meses de C estable se evalúa cualquier ampliación.

Opción A es path de menor resistencia pero contradice SOP/EPIA. Opción B es technical debt sin techo. Opción C es destino, no punto de partida.

---

## 5. Lo que se espera de Cowork (canonizador)

Si Alfredo firma Opción D:

1. **Definir el formato canónico** del archivo de patch en `bridge/embrion_patches/<thought_id>.json` (campos obligatorios, hash de firma, lista de tests pasados/fallidos, diff resumen ≤ 80 líneas).
2. **Especificar el criterio de "patch útil"** (no es subjetivo: ¿pasó tests CI sintéticos? ¿el diff afecta archivos en whitelist? ¿la firma del par crítico verifica?).
3. **Auditar mensual** la calidad de los patches: ratio aplicados/ignorados, tipos de errores recurrentes.
4. **Decidir migración a C** después de 30 días con datos.

Si Alfredo firma Opción C de inmediato:

1. **Redactar y firmar DSC-MO-EMBRION-PR-AUTONOMY** con la lista blanca de repos, prefijo de ramas, política de auto-close 24h, budget máximo.
2. **Definir matriz de power lanes para embrion** (qué tipo de cambio cae en L0, L1, L2, L3).
3. **Construir el procedimiento de revocación** si una iteración del embrion produce PRs masivos basura.
4. **Establecer el SLA Cowork** para co-firma (¿8h hábiles? ¿24h totales?).

---

## 6. Lo que se espera de ChatGPT (estratega — iteración 002)

**No le pidas decidir entre A/B/C/D.** Pídele:

1. **Comparativa con sistemas equivalentes**: ¿cómo manejan Devin, Cognition AI, OpenHands, Aider, Cursor Composer, Claude Code el problema de "agente abre PRs"? Tabla con: control humano, granularidad de aprobación, nivel de autonomía, modelo de billing.
2. **Stress test de Opción C**: ¿qué patrón de ataque hace que el par crítico colapse simultáneamente? ¿privilege escalation cuando un embrion vota por sí mismo? ¿race condition con commits paralelos?
3. **Diseñar el formato del patch JSON** de Opción D con esquema OpenAPI, validación, ejemplos.
4. **Articular cómo el embrion aprende del feedback**: si Cowork rechaza un patch, ¿el embrion incorpora esa señal? ¿cómo? ¿con qué granularidad?
5. **Estimar el costo cloud realista** de cada opción en términos de llamadas LLM/día con un embrion sano (no kimi-k2-6 down).

---

## 7. Decisión a firmar

```yaml
decision_t1_magna_006:
  modo_pr_autonomo_ganador: ___  # A | B | C | D
  fecha_firma: ___
  firmante: Alfredo Góngora
  justificacion_corta: ___

  # Solo si firma C:
  whitelist_repos: ___  # ej: [el-monstruo, tablero-campana]
  prefijo_ramas: "embrion/"
  power_lane_maximo: ___  # ej: L3
  sla_cowork_co_firma_horas: ___  # ej: 24
  budget_prs_simultaneos_por_embrion: ___  # ej: 5

  # Solo si firma D:
  formato_patch: "bridge/embrion_patches/<thought_id>.json"
  criterio_patch_util: ___  # ej: tests pasados Y diff <80 líneas Y firma par crítico válida
  fecha_revision_30_dias: ___  # auto: fecha_firma + 30d
  criterio_migracion_a_c: "30 patches útiles consecutivos sin patches dañinos"

  # Aplica a todas:
  precondicion_embrion_sano: "issue embrion-down-kimi-k2-6 cerrado y verificado"
  rollback_si_falla: ___
```

Al firmar:

1. Se commitea como `T1_MAGNA_006_PR_DRAFTS_AUTONOMOS_FIRMADA.md`.
2. Manus B implementa la opción ganadora en el sprint EMBRION_AUTONOMY_v1 (nuevo, agregar al registry).
3. Cowork firma DSCs derivados según opción.
4. Se actualiza `MONSTRUO_GENOME.yaml` con `embrion_pr_mode: D | C`.
5. Si firma D, no se requiere T1-MAGNA-005 firmado para arrancar.
6. Si firma C, se requiere T1-MAGNA-005 firmado en opción D mínimo (escalonado).

---

## 8. Bloqueos cruzados resueltos por esta firma

- **Sprint EMBRION_AUTONOMY_v1** (nuevo): se desbloquea para diseño con cualquier firma B/C/D.
- **FORJA-OMEGA-VISUAL Bloque B componente `EmbryoWorkerCard`**: necesita saber qué render mostrar (PR count vs patch count) — se aclara con esta firma.
- **DSC-S-006 (autonomy budget)**: se vuelve crítico activarlo si firma B/C.
- **Sprint MOBILE_0_SMP**: indirectamente: si los PRs autónomos funcionan, los sprints mobile podrían avanzar sin esperar Manus humano.
- **Patrón "asesor que no trabaja"**: se cierra con D mínimo.

---

## 9. Notas finales

Este documento NO firma por ti. Solo te entrega las cuatro opciones con criterios verificables y la recomendación de Hilo B con justificación.

La firma es tuya, T1 magna, no delegable a Manus, ni a Cowork, ni a ChatGPT.

**Recordatorio crítico**: el embrion_loop está caído ahora mismo (`kimi-k2-6`). Cualquier opción B/C/D que firmes hoy queda **suspendida hasta que el issue `embrion-down-kimi-k2-6.md` se cierre**. Si firmas A, no hay precondición. Si firmas D, puedes empezar el día que el embrion piense de nuevo. Si firmas C, requiere además el sprint de implementación del gateway extendido (~2 semanas con Manus + Cowork).

La opción D es la única que **no requiere infraestructura nueva crítica**: el embrion ya escribe a `bridge/`, sólo se le agrega un nuevo subdirectorio `embrion_patches/` con esquema canónico. La inversión es ~250 líneas Python.

Cuando firmes, responde en este hilo o agrega el bloque YAML al final del documento. Manus B aplica el cambio al kernel en menos de 1 día si la opción es D, en 2 semanas si es C. Cowork puede auditar en su próximo ciclo.

---

**Documento generado por:** Manus B (cuenta `manus_b` — Hilo B ejecutor técnico)
**Fecha de generación:** 2026-05-26
**Bloquea:** velocidad de avance del backlog, autonomía agéntica del Monstruo, FORJA-OMEGA-VISUAL Bloque B componente EmbryoWorkerCard
**Tiempo estimado de lectura:** 7 minutos
**Thread Immunity Session:** 8af84475-598b-4d14-aa79-7d5e0c0c589c
**Precondición operativa:** issue `embrion-down-kimi-k2-6.md` cerrado antes de activar B/C/D
