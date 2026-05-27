# Biblioteca de Sprints — 19 conceptos (todo menos SMP) — v2 PULIDA

**Autor:** Cowork (Arquitecto T2-A) · **Fecha:** 2026-05-27 · **Estado:** DRAFTs pulidos para firma T1
**Objetivo:** Índice/biblioteca de los 19 conceptos no-SMP — drafts de scope para firma T1 (NO es un sprint ejecutable único; cada §X es su propio sprint-draft).
**Origen:** instrucción T1 "redacta los 19" + "pule todos, déjalos listos".
**Contexto:** T1-MAGNA-001 = C (invocación). T1-MAGNA-002 = D (diferir SMP). Grounding verificado contra `docs/EL_MONSTRUO_APP_VISION_v1.md` cap. 5 (líneas 407-525, 833) — anti-F2, no fabricado.

---

## ⛔ Techo honesto: qué falta para el 100% "listo para codear"

Los specs abajo están pulidos al máximo que permiten los docs. Lo que **NO puedo finalizar sin ti** (fabricarlo violaría "no inventes datos") — **lista única de inputs T1**:

| # | Input T1 requerido | Bloquea |
|---|---|---|
| I1 | WhatsApp: Cloud API directo (recomendado) vs BSP + número Business | WhatsApp Gateway |
| I2 | Voice ID de ElevenLabs (voz canónica) | Voice Brand |
| I3 | Las 8 preguntas de Ontological Intake (hoy verbales, sin escribir) | Boca de ingesta |
| I4 | Enumeración confirmada de las 9 capas/dimensiones de Cronos (APP_VISION las nombra como dimensiones; falta la lista canónica firmada) | Cronos fase 2 |
| I5 | Shamir: umbral k-of-n + lista de herederos | Modo Cripta |
| I6 | Mecanismo del deep-link silencioso del Confidente | Modo Confidente |
| I7 | Decisión: AI-First Living y Origen Pre-IA → ¿canonizar / descartar / diferir? | §F, §G |

Resuelve estos 7 y los 14 quedan 100%. Sin ellos, quedan "estructura final + TBD marcado". Y los SMP-dependientes igual no ejecutan hasta firmar SMP (D).

---

## Tabla maestra — cobertura 19/19

| # | Concepto | Estado | Ubicación |
|---|---|---|---|
| 2.1 | Cronos / Río de la Vida | DRAFT pulido, parado (SMP) | §A |
| 2.2 | Modo Cripta | DRAFT pulido, parado (SMP+AUTH) | §B |
| 2.3 | Memento | ✅ producción | — |
| 2.4 | el-mundo-de-tata | proyecto separado | manifest propio |
| 2.5 | Niebla del Futuro | DRAFT (= Cronos fase 3) | §A |
| 2.6 | Acto 1 Daily+Cockpit | Daily 5 ✅ / Cockpit cancelado | `sprint_DAILY_5_MINIMAL_001` |
| 2.7 | Acto 2 Calm Tech | ✅ firma C | T1-MAGNA-001 FIRMADA |
| 2.8 | AI-First Living | DRAFT investigación | §F |
| 2.9 | Transport Cero / Boca de ingesta | DRAFT pulido, parado (SMP) | §C |
| 2.10 | Origen Pre-IA | DRAFT extracción (espera CIERRE) | §G |
| 2.11 | Engranaje + Reloj Suizo | DRAFT decisión | §H |
| 2.12 | A2UI Protocol | ✅ PR #92 + `sprint_A2UI_INVOCATION_001` | — |
| 2.14 | Command Center | ✅ `sprint_COMMAND_CENTER_THEME_001` | — |
| 2.15 | Brand DNA | ✅ DSC-MO-002 v3 | — |
| 2.16 | Fototeca | DRAFT pulido, parado (SMP) | §D |
| 2.17 | WhatsApp Gateway | ✅ `sprint_WHATSAPP_GATEWAY_001` | — |
| 2.18 | Modo Confidente | DRAFT pulido, parado (SMP) | §E |
| 2.19 | Embriones | ✅ código/canon | — |
| 2.20 | AUTH_TIERS_001 | DRAFT pulido, parado (SMP) | §I |

---

## §A — CRONOS_001 (Río de la Vida) — parado (SMP)

**Owner:** Manus E1. **Dep:** SMP + AUTH_TIERS. **Fuente:** APP_VISION cap. 5 (L407-441, 833).
**Concepto:** río navegable de la vida. Aguas arriba = pasado; aguas abajo = futuro proyectado (**niebla**, no transparencia — proyecciones reflexivas de cadenas causales del propio usuario, NO predicciones exactas). Pinch zoom (años↔momentos). En cada punto: personas, lugares, decisiones, clima emocional. Vive como franja horizontal bajo el input del Home, swipe lateral, no obligatoria (L230).
**Modos:** Espejo (default — marginalia gris discreta cuando convergen patrones) · Testigo silente (toggle, el río graba pero suspende reflexiones; agencia total) · Cripta (§B).
**Regla de oro:** describe, no prescribe. NUNCA "deberías X" → "veo que en patrones similares pasó X, ¿qué te resuena?". Espejo, no entrenador (L43).
**Fases (verbatim L833):**
- **CRONOS_1:** chasis del río + captura passive (WhatsApp + Photos + ambient audio) bajo SMP.
- **CRONOS_2:** 9 capas/dimensiones + modo Espejo + Smart Notebook conectada.
- **CRONOS_3:** Niebla del Futuro + Embrión Convergencia inter-capa + ofrendas voluntarias.
- **Resúmenes:** semanal (dom AM), mensual (día 1), anual (31 dic) — narrativa + métricas + fotos + decisiones magna; usuario es editor (L437).
**Alcance bajo D:** persistencia personal cifrada → **bloqueado hasta SMP**.
**TBD T1:** I4 (las 9 capas — son dimensiones del río, no tabs; APP_VISION las trata como dimensiones tipo Salud/Relaciones pero falta la lista canónica firmada).
**Aceptación (post-SMP):** río renderiza, navegación temporal + pinch, captura passive cifrada, 3 modos, niebla aguas abajo, resúmenes. Audit DSC-G-008.

## §B — MODO_CRIPTA_001 — parado (SMP + AUTH_TIERS)

**Owner:** Manus E1. **Dep:** SMP + AUTH_TIERS + CRONOS_1. **Fuente:** APP_VISION L478-484, 943.
**Concepto:** al fallecer, el Cronos se lega a seres queridos — soberano, encriptado, **navegable pero cerrado a edición**. Shamir's Secret Sharing pre-distribuido a herederos.
**Alcance v1.1 (firmado en visión):** SOLO preservación pura. **Simulación post-mortem diferida a v1.3+** con precondiciones éticas: consentimiento pre-mortem firmado, marca visible permanente, acceso restringido, límites de profundidad, sunset opcional.
**TBD T1:** I5 (umbral Shamir k-of-n + lista de herederos). Decisión ética simulación (v1.3+).
**Aceptación (post-SMP+AUTH):** Cronos legado descifrable solo con k shards de herederos; navegable; no editable; marca de legado visible.

## §C — TRANSPORT_CERO_001 (Boca de ingesta / Ontological Intake) — parado (SMP)

**Owner:** Manus E1. **Dep:** SMP. **Fuente:** verbal T1 (NO escrito — riesgo de fabricación).
**Concepto:** la única boca de entrada. NO es ingesta de archivos: son **8 preguntas de juicio** que deciden qué entra y cómo — Ontological Intake, Capture Heat Check, Reconstruction Sufficiency Score, Microcontext Prompt, Rhythm Gate, Delegation Router, Focus Guard, Memory Candidate.
**TBD T1 (bloqueante real):** I3 — el contenido de las 8 preguntas está verbal, sin escribir. **No las escribo yo** (sería fabricar doctrina). T1 las dicta o aprueba una versión escrita antes de implementar.
**Alcance bajo D:** la salida persiste a memoria soberana → **bloqueado hasta SMP**.
**Aceptación (post-SMP + I3):** las 8 compuertas filtran toda captura; nada entra a memoria sin pasar el juicio.

## §D — FOTOTECA_001 (photo_intelligence) — parado (SMP)

**Owner:** Manus E1. **Dep:** SMP. **Fuente:** APP_VISION cap. 4.
**Concepto:** capability de fotos + fuente passive de CRONOS_1. NO módulo separado — es Cap 4 (photo_intelligence) invocable.
**Alcance:** captura/análisis personal → **bloqueado hasta SMP**.
**Aceptación (post-SMP):** fotos ingresan cifradas, alimentan Cronos, análisis invocado on-demand (paradigma C), no tab persistente.

## §E — MODO_CONFIDENTE_001 — parado (SMP)

**Owner:** Manus E1. **Dep:** SMP. **Fuente:** APP_VISION L43, 508, 525.
**Concepto:** acceso silencioso en crisis. Usuario pregunta "¿qué hice mal hoy?" / "¿qué hago ahora?" → el Monstruo activa bajo el capó la maquinaria entera: Catastro elige LLM de conversación íntima, Embriones en `debate` silencioso, Memento con uncertainty tracking, Guardian observando, Cronos buscando patrones del propio pasado, 9 capas convergiendo. Respuesta = "configuración del ADN del usuario", no genérica.
**Regla:** describe, no prescribe. Espejo, no entrenador (L43). Sin nombre visible, deep link encriptado.
**TBD T1:** I6 (mecanismo del deep-link silencioso — cómo se invoca sin dejar rastro).
**Alcance:** contenido íntimo/sensible → **bloqueado hasta SMP**.
**Aceptación (post-SMP + I6):** deep link abre modo sin nombre, convoca todas las piezas, cifrado, sin persistencia no-soberana.

## §F — AI_FIRST_LIVING_INVESTIGACION_001 — investigación (no canon)

**Owner:** Cowork + Sabios. **Estado:** hipótesis naciente — NO canonizar todavía.
**Objetivo:** validar "Alfredo organiza información para que la IA la absorba, no para leerla él". ¿Acto 3 o capa transversal?
**Entregable:** convergencia 3 Sabios + veredicto (canonizar / descartar / re-enmarcar) para firma T1. NO implementación.
**TBD T1:** I7.

## §G — ORIGEN_PRE_IA_EXTRACCION_001 — extracción (espera CIERRE T1)

**Owner:** Cowork. **Estado:** EN_EXTRACCION_T1 / NO_CANONIZAR hasta "CIERRE BLOQUE PRE-IA" de Alfredo.
**Objetivo:** extraer los 10 principios pre-IA-001..010 (2020-2021). ¿Acto 0 doctrinal o background?
**Entregable:** extracción documental. Bloqueado por decisión irreducible de Alfredo.
**TBD T1:** I7 + declarar CIERRE BLOQUE PRE-IA.

## §H — ENGRANAJE_RELOJ_SUIZO_001 — decisión (incorporar/sandbox)

**Owner:** Manus E2. **Estado:** prototipo `scripts/prototipo_engranaje.py`, no canonizado.
**Objetivo:** decidir si el prototipo Calm Tech se incorpora al kernel o queda sandbox. **Anti-DSC-G-004:** ya existen DSC-MO-010 (Reloj Suizo) + ESPIRAL + REMONTOIR mergeados — verificar solapamiento ANTES de incorporar; puede que el prototipo ya esté superado por esos.
**Aceptación:** decisión documentada + (si incorpora) wiring con audit Cowork.

## §I — AUTH_TIERS_001 — parado (SMP, pre-req de Cripta)

**Owner:** Manus E1. **Dep:** SMP. **Fuente:** VISION_APP_MONSTRUO_CLASE_MUNDIAL Eje 8.
**Concepto:** 3 tiers — Owner (Alfredo: Face ID + passphrase + Apple Watch), Trusted Circle (invitaciones nominativas), Funcional Accesible (config reducida). Pre-requisito de Modo Cripta.
**Alcance:** identidad/cripto → **bloqueado hasta SMP**.
**Aceptación (post-SMP):** 3 tiers operativos, Owner con MFA hardware, Trusted Circle nominativo, Funcional con superficie reducida.

---

## Tareas

Cada concepto §A-§I de arriba ES una tarea-sprint (objetivo + dependencias + alcance + aceptación). Esta biblioteca es el ÍNDICE de los 19; cada draft se parte en archivo individual al firmarse o al desbloquearse SMP. Las tareas ejecutables-ya viven en sus archivos propios (WhatsApp, Voz, A2UI Invocación, Daily 5, CC theme).

## Criterios de Cierre / Entregables

- **Entregable:** los 9 drafts §A-§I pulidos con grounding APP_VISION + los 5 sprints en archivo individual = cobertura 19/19.
- **Cierre por sprint:** cada §X cierra cuando se resuelven sus TBD T1 (I1-I7) y, para los SMP-dependientes, cuando se firme SMP. Cada uno se ejecuta con su propio gate DSC-G-008.
- **Estado:** pulidos §A-§I (9) · en archivo individual (5) · ya existentes sin redactar (Memento, A2UI Protocol, Brand DNA, Embriones, 6 CAPA). Lo único entre esto y "100% listo para codear": los 7 inputs T1 (I1-I7) + firmar SMP para desbloquear los parados.

— Cowork T2-A, v2 PULIDA (índice/biblioteca, no sprint ejecutable único)
