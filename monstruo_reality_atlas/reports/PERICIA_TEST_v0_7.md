# PERICIA TEST v0.7 [SUPERSEDED_BY_v0_8]

> **⚠️ SUPERSEDED_BY_v0_8** — Este test contiene 4 preguntas con respuestas en deriva detectadas por ChatGPT el 2026-05-18.
>
> **NO usar como test válido.** Ir a la versión vigente:
> - `monstruo_reality_atlas/reports/PERICIA_TEST_v0_8.md`
>
> **Preguntas con deriva en v0.7:**
> - **P1** Home canónica — mezclaba Daily con Cockpit. La Home canónica pertenece a Daily, no a Cockpit.
> - **P7** Self-Verifier VERIFIABLE — decía "fact-checking contra fuentes" cuando es anti-eco / artefacto verificable.
> - **P10** SMP — decía "Secure Memory Protocol". Correcto: **Sovereign Memory Plane**.
> - **P13** Acto 1 / Acto 2 — mapeo invertido. Acto 1 = 20 superficies; Acto 2 = Calm Tech latente; Acto 2 contiene Acto 1.
>
> **Commit fix:** `d876a21` — `docs(atlas): fix ChatGPT pericia checkpoint v0.8 drift`
>
> Mantenido para trazabilidad histórica del bucle correctivo Anti-Dory.

---

> **Propósito:** verificar que ChatGPT (o cualquier hilo nuevo) ha absorbido el conocimiento del checkpoint v0.7 antes de diseñar.
>
> **Reglas del test:**
>
> - 20 preguntas con respuesta esperada.
> - Pasa con 18/20 correctas o más.
> - Si pasa 16-17/20: leer las preguntas falladas, releer secciones del checkpoint, reintentar una vez.
> - Si pasa menos de 16/20: **NO diseñar**. Releer checkpoint completo + JSON state. Reintentar después.
>
> **Fuente de verdad:** `CHATGPT_PERICIA_CHECKPOINT_v0_7.md` y `CHATGPT_PERICIA_STATE_v0_7.json`.

---

## Pregunta 1

**¿Por qué Home no es Home canónica?**

**Respuesta esperada:**

En `apps/mobile/lib/features/chat/` o equivalente, la ruta `/home` existe pero el widget Home es **proxy de ChatScreen**. No tiene contenido propio que correspondería a Home canónica del Cockpit (resumen de embriones, runs activos, propuestas pendientes, presupuesto del día). Es placeholder con redirect, no Home real.

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

Memento existe como **validator importable real** en `kernel/memento/`. Se puede importar desde Python y usar para validar que outputs cumplen el protocolo Memento. **NO está confirmado** que exista endpoint HTTP completo expuesto en `kernel/main.py` que permita a transports externos (Flutter, Command Center) llamar a Memento. Hasta verificar wiring en kernel/main.py, asumir solo validator local.

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

Tienen 3 interfaces: `lookup` (consulta directa por id), `search` (búsqueda semántica), `orchestration` (selección automática de mejor recurso para tarea).

**Catastro NO es inventario visual** (tabla estática que se mira). Es **motor de selección de recursos** que el Embrión consulta dinámicamente.

---

## Pregunta 7

**¿Qué hace Self-Verifier?**

**Respuesta esperada:**

`kernel/embrion_self_verifier.py` corre antes de que el Embrión emita output. Toma 3 decisiones binarias:

1. **PURPOSE** — ¿el output cumple el propósito declarado del latido?
2. **NOVELTY** — ¿el output aporta algo nuevo, o es eco/repetición de outputs previos?
3. **VERIFIABLE** — ¿el output incluye claims que se pueden verificar contra fuentes?

Si alguna decisión falla, el Embrión **aborta el latido** o lo escala a HITL. Sirve para evitar que el Embrión genere ruido, repita, o invente sin verificar.

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

**Falta verificar:** si hay endpoints HTTP que expongan el simulador, si hay UI en Flutter o Command Center que lo use, si está conectado al loop del Embrión. Hasta verificar wiring en kernel/main.py, asumir solo módulos importables.

---

## Pregunta 10

**¿Qué bloquea datos sensibles?**

**Respuesta esperada:**

**SMP** (Secure Memory Protocol o equivalente — el cimiento criptográfico). Hasta que SMP esté implementado en código (no solo doctrinal), **NO tocar datos sensibles**. Esto incluye datos de Cronos (vida personal de Alfredo), Modo Cripta (legado a familiares), credenciales, secretos, datos de salud, financieros, etc. SMP es la precondición técnica para que cualquier transport o módulo procese datos íntimos.

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

**¿Qué significa Acto 2 contiene Acto 1?**

**Respuesta esperada:**

**Acto 1** (Calm Tech / Quietud / Acompañamiento Silente) y **Acto 2** (Monstruo activo / Embrión autónomo / Acción) parecían contradecirse en hilos previos. La dirección provisional consensuada es:

> **Acto 2 contiene Acto 1.** El Monstruo activo (Acto 2) incluye periodos de quietud, observación silente, no-interrupción (Acto 1) como modo operativo dentro de su autonomía. No son fases secuenciales; son el mismo organismo en estados.

Esto evita el redesign del Acto 1 como fase pasada y permite diseñar el Cockpit con ambos modos simultáneos.

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

Cockpit canónico (12-15 superficies en APP_VISION) debe mostrar sobre el Embrión:

1. **Estado del loop** (latidos activos, latidos abortados por Self-Verifier, escalaciones a HITL).
2. **Budget consumido** vs presupuesto diario (Budget Tracker).
3. **Cola de proposals** con estados (pending, approved, executing, executed, failed, rejected, expired).
4. **Decisiones recientes** del Self-Verifier (PURPOSE/NOVELTY/VERIFIABLE).
5. **Sabios consultados** y resultados.
6. **Catastros consultados** y recursos seleccionados.
7. **Side effects ejecutados** (con executor real, no noop).
8. **Silencio activo** (Acto 1 dentro de Acto 2 — cuando el Embrión decide no actuar).

NO mostrar solo chat. El Embrión es más que conversación.

---

## Pregunta 17

**¿Qué sigue sin estudiar?**

**Respuesta esperada:**

Para llegar a `ARQUITECTO_PRINCIPAL` (de `ARQUITECTO_EN_CERTIFICACION`), faltan:

- **Gate 3.3**: `kernel/main.py` y todas las rutas (AG-UI, memory, embrion, proposal/HITL, finops, moc, collective/Sabios, embrion_specializations).
- Bridge inter-hilos completo (subir de 45% a 80%+).
- Command Center real (subir de 50% a 80%+).
- Catastros (subir de 55% a 80%+).
- Simulador causal verificado en endpoints/UI (subir de 55% a 80%+).
- Embriones especializados (qué embriones específicos existen).
- Sabios collective (cómo se consulta a múltiples sabios y se sintetizan respuestas).

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
- **Memento endpoint completo** — solo validator confirmado.
- **A2UI renderer real** — solo schema confirmado.
- **Acto 1 vs Acto 2 como contradicción** — la dirección es Acto 2 contiene Acto 1.
- **Las 10 hipótesis pre-IA y 5 órganos latentes** — esperan CIERRE BLOQUE PRE-IA.
- **Las 5 decisiones T1 magnas pendientes** — esperan firma explícita de Alfredo.

---

## Pregunta 20

**¿Cuál es el próximo gate?**

**Respuesta esperada:**

**Gate 3.3 — Wiring real en `kernel/main.py`**

Leer:

- `kernel/main.py`
- rutas AG-UI
- rutas memory
- rutas embrion
- rutas proposal/HITL
- rutas finops
- rutas moc
- collective/Sabios
- embrion_specializations

**Objetivo:** saber qué módulos están **realmente conectados al API** y qué solo existe como módulo importable. Esto distingue:

- `Memento validator` (módulo importable) vs `Memento endpoint` (ruta HTTP en kernel/main.py).
- `CausalSimulatorV2` (módulo importable) vs `simulador endpoint` (ruta HTTP).
- `Embrion loop` (módulo) vs `embrion endpoint` (ruta que dispara el loop desde transports).

Sin Gate 3.3, asumir solo módulos importables, NO endpoints reales.

---

## Resultado del test

Después de responder las 20 preguntas:

| Score | Acción |
|---|---|
| 18-20/20 | PASA. Puede proceder a diseñar (respetando reglas de DO_NOT_REDESIGN_BEFORE_READING.md). |
| 16-17/20 | PARCIAL. Releer preguntas falladas + secciones del checkpoint. Reintentar una vez. |
| <16/20 | FALLA. NO diseñar. Releer checkpoint completo + JSON state. Reintentar después. |

Registrar resultado en `monstruo_reality_atlas/reports/PERICIA_TEST_v0_7_RESULT_<fecha>.md` (cuando aplique).
