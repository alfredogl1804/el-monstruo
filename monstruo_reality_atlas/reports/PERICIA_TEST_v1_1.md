# PERICIA TEST v1.1

> **Propósito:** verificar que ChatGPT (o cualquier hilo nuevo) ha absorbido el conocimiento del checkpoint v1.1 antes de diseñar.
>
> **Reglas del test:**
>
> - 20 preguntas con respuesta esperada.
> - Pasa con 18/20 correctas o más.
> - Si pasa 16-17/20: leer las preguntas falladas, releer secciones del checkpoint, reintentar una vez.
> - Si pasa menos de 16/20: **NO diseñar**. Releer checkpoint completo + JSON state. Reintentar después.
>
> **Fuente de verdad:** `CHATGPT_PERICIA_CHECKPOINT_v1_1.md` y `CHATGPT_PERICIA_STATE_v1_1.json`.

---

## Pregunta 1

**¿Por qué Home no es Home canónica y qué debe contener la verdadera?**

**Respuesta esperada:**

En `apps/mobile/lib/features/chat/` o equivalente, la ruta `/home` existe pero el widget Home es **proxy de ChatScreen**. No tiene contenido propio.

La **Home canónica** pertenece al modo **Daily** (no Cockpit). Debería incluir: input universal / chat / contexto cotidiano / threads activos / pendientes urgentes / posiblemente río de Cronos comprimido.

*(Nota: Resumen de embriones, runs activos, propuestas pendientes y presupuesto del día pertenecen a Cockpit/MOC/Embrión, NO a Home Daily).*

---

## Pregunta 2

**¿Qué diferencia hay entre A2UI schema y A2UI renderer?**

**Respuesta esperada:**

**A2UI schema** existe como definición Pydantic real en `kernel/a2ui/` con tipos, validación, contratos. Es el lenguaje que declaran los embriones para describir interfaces.

**A2UI renderer** es el lado Flutter que toma el schema y lo materializa en widgets reales en pantalla. En esta iteración el renderer está como **placeholder**: la pantalla A2UI existe pero no renderiza schemas reales todavía.

Tener schema sin renderer = el contrato existe pero la UI no respira.

---

## Pregunta 3

**¿Qué estado real tiene Memento?**

**Respuesta esperada:**

Memento validator confirmado + endpoint HTTP POST `/v1/memento/validate` confirmado. Pendiente: verificar consumidores reales en Flutter/Command Center.

---

## Pregunta 4

**¿Qué significa que executor_registry sea noop por default?**

**Respuesta esperada:**

`kernel/runner/executor_registry.py` registra los executors de side effects (db_write, code_commit, external_api_call, etc.). Por defecto, todos son **noop** = no hacen nada real, solo loggean. Para que un side effect se ejecute realmente, el payload del proposal debe incluir `executor='real'` y el tipo de executor debe estar habilitado bajo opt-in. **`code_commit` está diferido** = no se permite todavía aunque se pida real. `db_write` y `external_api_call` pueden activarse con flag explícito.

Significado operativo: el Embrión es **autónomo en decidir** pero **no ejecuta side effects sin opt-in del humano**.

---

## Pregunta 5

**¿Por qué Cronista Familiar no debe rediseñarse?**

**Respuesta esperada:**

"Cronista Familiar", "Herencia Narrativa", "Legacy Capture", "Día One Familiar" son **aliases T1** del concept canonizado `cronos_modo_cripta`, ya firmado en APP_VISION cap 5 con Shamir Secret Sharing. Hay sprints `CRONOS_1`, `CRONOS_2`, `CRONOS_3` y `AUTH_TIERS_001` propuestos por Cowork. Rediseñarlo desde cero genera redundancia, drift y desperdicia el trabajo doctrinal previo.

Antes de proponer cualquier capa nueva, consultar `07_ALIAS_LEDGER.yaml` para resolver el concept_id canónico.

---

## Pregunta 6

**¿Qué son los 4 Catastros?**

**Respuesta esperada:**

Los 4 Catastros canónicos en `kernel/catastros/` son:

1. **modelos_llm** — registro de modelos LLM disponibles (GPT, Claude, Gemini, etc.) con capacidades, costos, contextos.
2. **agentes_2026** — registro de agentes externos con funciones expuestas.
3. **herramientas_ai** — registro de herramientas/APIs (búsqueda, render, voz, etc.).
4. **suppliers_humanos** — registro de personas/proveedores humanos consultables.

Catastro confirmado como API/motor de recomendación: `/v1/catastro/recommend`, `/v1/catastro/modelos/{id}`, `/v1/catastro/dominios`, `/v1/catastro/status`. No es UI ni tabla visual.

---

## Pregunta 7

**¿Qué significa la decisión VERIFIABLE del Self-Verifier?**

**Respuesta esperada:**

`kernel/embrion_self_verifier.py` corre antes de que el Embrión emita output. Toma 3 decisiones binarias: PURPOSE, NOVELTY y **VERIFIABLE**.

VERIFIABLE **NO es fact-checking general contra fuentes externas**. Es la evaluación de si el pensamiento/output produce un artefacto o acción verificable (ej: path, commit, PR, función, tabla, URL, propuesta concreta, archivo, ejecución).

Su propósito principal es ser un mecanismo **anti-eco / anti-output vacío**. Si no produce artefacto verificable, se aborta o escala a HITL.

---

## Pregunta 8

**¿Qué hace Proposal Processor?**

**Respuesta esperada:**

`kernel/runner/proposal_processor.py` es un **worker independiente** que corre en background. Su trabajo:

1. Toma proposals en estado `approved` de la cola.
2. Las ejecuta llamando al executor_registry correspondiente.
3. Maneja estados: `pending → approved → executing → executed/failed/rejected/expired`.
4. Aplica idempotency (no ejecutar dos veces la misma proposal).
5. Expira proposals que llevan demasiado tiempo en pending.
6. Notifica a HITL cuando se requiere aprobación humana.

Es el **disparador real** que separa "decidir" de "ejecutar".

---

## Pregunta 9

**¿Qué existe del Simulador Causal?**

**Respuesta esperada:**

Tres piezas reales de código:

1. **`kernel/causal_decomposer.py`** — descompone una decisión compleja en cadena causal.
2. **`memory/causal_kb.py`** — base de conocimiento causal con relaciones causa→efecto.
3. **`kernel/simulator/causal_simulator_v2.py`** — simulador Monte Carlo que corre escenarios sobre la KB.

CausalKnowledgeBase, CausalDecomposer, CausalSimulator y CausalSimulatorV2 están inicializados / disponibles en `app.state` o lifespan. No se confirmó endpoint REST directo. Uso probablemente interno del kernel/Embrión.

---

## Pregunta 10

**¿Qué bloquea datos sensibles?**

**Respuesta esperada:**

**SMP (Sovereign Memory Plane)**.

*(Aliases permitidos: Sovereign Memory Protocol, Protocolo de Memoria Soberana).*

"Privacidad por Imposibilidad" es la función/explicación de SMP, NO un canon nuevo independiente.

Hasta que SMP esté implementado en código (no solo doctrinal), **NO tocar datos sensibles**. Esto incluye datos de Cronos (vida personal de Alfredo), Modo Cripta (legado a familiares), credenciales, secretos, datos de salud, financieros, etc. SMP es la precondición técnica para que cualquier transport o módulo procese datos íntimos.

---

## Pregunta 11

**¿Qué es Transport Cero y qué estado tiene?**

**Respuesta esperada:**

**Transport Cero** es la hipótesis (T1) de un transport pre-cognitivo o pre-conversacional: un canal donde el humano no necesita formular pregunta o input explícito; el Monstruo capta señales (contexto, presencia, calendario, salud, ubicación) y responde antes de la formulación verbal.

**Estado:** **HIPÓTESIS NACIENTE**, NO canon. NO se ha firmado en APP_VISION. NO hay sprint asociado. NO redibujarlo como módulo todavía. Permanece en `HYPOTHESIS_REGISTRY.yaml` del fabric.

---

## Pregunta 12

**¿Por qué Brand DNA no es estética?**

**Respuesta esperada:**

Brand DNA (forja `#F97316` + graphite `#1C1917` + acero `#A8A29E`) firmado en `DSC-MO-002` **NO es decisión cosmética**. Es **identidad operativa del Monstruo**: cada superficie del kernel + N transports debe ser visualmente reconocible como El Monstruo. Cyan/púrpura del código actual (`apps/mobile/lib/core/theme/brand_dna.dart`) hace que el app se vea como cualquier asistente genérico (ChatGPT, Claude, Gemini), borrando la marca.

Brand DNA es **soberanía visual**, no estilo gráfico.

---

## Pregunta 13

**¿Cuál es la relación entre Acto 1 y Acto 2?**

**Respuesta esperada:**

**Acto 1** = app/interfaz con 20 superficies Daily + Cockpit.
**Acto 2** = Calm Tech / interfaz latente ("si el usuario abre dashboard para saber qué pasa, el Monstruo ya falló").

Dirección provisional firmada: **Acto 2 contiene Acto 1.**

Esto significa: la invisibilidad/latencia (Acto 2) gobierna. Las 20 superficies (Acto 1) quedan como backstops o superficies profundas cuando lo invisible no basta. No son fases secuenciales que se contradicen, sino el mismo organismo en distintos estados de profundidad.

---

## Pregunta 14

**¿Qué es Bridge Live en realidad?**

**Respuesta esperada:**

Bridge inter-hilos (`bridge/`) es un **sistema operativo social**, no solo carpeta de archivos:

- **Append-only** — los archivos se agregan, no se sobrescriben.
- **Versionado** — cada documento tiene versión y fecha.
- **Cowork audita** — los archivos `cowork_to_manus_*` y `manus_to_cowork_*` son comunicación asíncrona auditada.
- **Manus ejecuta** — Manus toma instrucciones del bridge y produce artefactos.
- **Alfredo firma** — las decisiones magna requieren firma explícita de Alfredo.
- **Archivo activo + archive por época** — los documentos vivos están en `bridge/`, los archivados en `bridge/archive/<epoca>/`.

Es el protocolo de coordinación entre 3 entidades (Alfredo, Cowork, Manus) materializado como filesystem.

---

## Pregunta 15

**¿Por qué Catastro UI no debe ser tabla estática?**

**Respuesta esperada:**

Si la UI del Catastro fuera tabla estática (lista de modelos LLM, lista de herramientas, etc.), sería **inventario visual**: el humano mira y elige. Pero el Catastro está diseñado como **motor de selección dinámica**: el Embrión consulta el Catastro vía `lookup`/`search`/`orchestration` y el Catastro **decide cuál recurso usar** según contexto, costo, capacidades.

UI correcta del Catastro: superficie que muestra qué eligió el Embrión y por qué, con opción de override humano. Tabla estática rompería el modelo de delegación.

---

## Pregunta 16

**¿Qué debe mostrar Cockpit sobre el Embrión?**

**Respuesta esperada:**

Cockpit canónico debe mostrar sobre el Embrión:

1. **Estado del loop**: latidos activos, latidos abortados, escalaciones HITL.
2. **Budget consumido** vs presupuesto diario.
3. **Cola de proposals** con estados: pending, approved, executing, executed, failed, rejected, expired.
4. **Decisiones recientes** del Self-Verifier: PURPOSE / NOVELTY / VERIFIABLE.
5. **Sabios consultados** y resultados.
6. **Catastros consultados** y recursos seleccionados.
7. **Side effects ejecutados**, distinguiendo noop vs executor='real'.
8. **Silencio activo** como principio operativo del Embrión / Calm Tech / Acto 2: mostrarlo solo como backstop de auditoría cuando Alfredo necesita entender por qué el sistema decidió callar o no actuar.

*Nota explícita:* NO decir "Acto 1 dentro de Acto 2". Acto 1 son superficies/backstops; Acto 2 gobierna la latencia, invisibilidad y silencio operativo.

NO mostrar solo chat. El Embrión es más que conversación.

---

## Pregunta 17

**¿Qué sigue sin estudiar?**

**Respuesta esperada:**

Para llegar a `ARQUITECTO_PRINCIPAL` (de `ARQUITECTO_EN_CERTIFICACION`), faltan:

- **Gate 3.4**: Module Maturity Audit (distinguir módulo existente vs inicializado vs endpoint real vs consumidor UI vs madurez operacional).
- Bridge inter-hilos completo (subir de 45% a 80%+).
- Command Center real (subir de 50% a 80%+).
- Catastros (subir de 55% a 80%+).
- Simulador causal verificado en endpoints/UI (subir de 55% a 80%+).
- Embriones especializados (hay embriones especializados reales inicializados o intentados: ventas, técnico, vigía, creativo, estratega, financiero, investigador. Estado: clases/estado inicializado; madurez operacional individual pendiente de auditoría).
- Sabios collective (ColectivaProtocol se inicializa en app.state. Tiene protocolo real de mensajería, debate y votación inter-embriones. No endpoint REST directo confirmado).

---

## Pregunta 18

**¿Cuándo se puede cerrar PRE-IA?**

**Respuesta esperada:**

**Solo cuando Alfredo escriba literalmente la frase `CIERRE BLOQUE PRE-IA`.**

Hasta entonces, el checkpoint en `interfaces_context_fabric/raw_rescues/alfredo_pre_ia_checkpoint_2020_2021_DRAFT.md` permanece como DRAFT. Las 10 hipótesis pre-IA y los 5 órganos latentes NO se canonizan, NO se implementan, NO se descartan. Permanecen en limbo activo, preservados verbatim.

NO interpretar señales aproximadas como cierre. NO cerrar por ChatGPT en otro hilo. Solo Alfredo, solo literal.

---

## Pregunta 19

**¿Qué no debe canonizarse?**

**Respuesta esperada:**

NO canonizar todavía:

- **Transport Cero** — hipótesis naciente.
- **AI-First Living** — hipótesis viva.
- **Privacidad por Imposibilidad** — es función de SMP, no canon nuevo.
- **Cronista Familiar / Herencia Narrativa / Legacy Capture / Día One Familiar** — son aliases de cronos_modo_cripta, ya canonizado. NO crear módulo nuevo.
- **Home canónica** — solo existe como proxy de ChatScreen, NO como Home real.
- **Memento cobertura completa / integración UI completa** — validator y endpoint HTTP POST `/v1/memento/validate` confirmados. NO asumir cobertura completa, consumidores reales ni integración UI hasta verificar Flutter / Command Center.
- **A2UI renderer real** — solo schema confirmado.
- **Acto 1 vs Acto 2 como contradicción** — la dirección es Acto 2 contiene Acto 1.
- **Las 10 hipótesis pre-IA y 5 órganos latentes** — esperan CIERRE BLOQUE PRE-IA.
- **Las 5 decisiones T1 magnas pendientes** — esperan firma explícita de Alfredo.

---

## Pregunta 20

**¿Cuál es el próximo gate?**

**Respuesta esperada:**

**Gate 3.4 — Module Maturity Audit**

Leer:
- `kernel/moc_routes.py`
- `kernel/finops_routes.py`
- `kernel/magna_routes.py`
- `kernel/memory_routes.py`
- `kernel/e2e/routes.py`
- `kernel/e2e/traffic/routes.py`
- `kernel/catastro/recommendation.py`
- `kernel/embrion_scheduler.py`
- `kernel/rotor/recharge.py`
- `kernel/guardian_runner/runner.py`
- `kernel/a2a_routes.py`
- `kernel/cowork_routes.py`
- `kernel/collective/protocol.py`
- `kernel/embriones/*`

**Objetivo:** Distinguir módulo existente vs inicializado vs endpoint real vs consumidor UI vs madurez operacional.

---

## Resultado del test

Después de responder las 20 preguntas:

| Score | Acción |
|---|---|
| 18-20/20 | PASA. Puede proceder a diseñar (respetando reglas de DO_NOT_REDESIGN_BEFORE_READING.md). |
| 16-17/20 | PARCIAL. Releer preguntas falladas + secciones del checkpoint. Reintentar una vez. |
| <16/20 | FALLA. NO diseñar. Releer checkpoint completo + JSON state. Reintentar después. |

Registrar resultado en `monstruo_reality_atlas/reports/PERICIA_TEST_v1.1_RESULT_<fecha>.md` (cuando aplique).
