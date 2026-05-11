# Cowork — Glosario Vivo del Monstruo

**Propósito:** Términos canónicos del Monstruo con definición concisa y origen. Sin esto, cada sesión nueva inventa interpretaciones.

**Estado:** v0.1 — Cowork verificó en jornada del 10-may. Iterar cuando se canonice término nuevo.

**Última actualización:** 2026-05-10.

---

## A

**Áncora (pieza Reloj Suizo).**
Pieza horológica = Coordinador de Ciclo. Sincroniza el escape con el volante. Implementación: `kernel/embrion_scheduler.py`. Fuente: `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md`.

**Antipattern.**
Patrón observable de falla operativa. Documentado en `bridge/COWORK_OPERATING_SYSTEM_v0_1_2026_05_10.md`. 8 antipatterns identificados de la jornada del 10-may. Origen: crisis meta-arquitectónica.

**App Flutter Cara Completa.**
Estado objetivo de la app móvil del Monstruo tras Sprint Mobile 1-5. Cara = interfaz primaria. Cockpit completo con Daily + 3 fases del Cockpit (MOC, Threads, Catastro, Embriones, Guardian, Memento, Portfolio, FinOps, Pipeline, Replay).

**Arsenal.**
Conjunto de herramientas que el embrión puede seleccionar dinámicamente vía Catastro. DSC-MO-009. Diferente del Catastro mismo (que es el catálogo). Arsenal = subset operacional para una decisión específica.

**Auto-replicación E2E.**
Test final del Objetivo #1: el Monstruo recibe "frase → produce empresa funcionando con tráfico real". No solo código deployado — empresa con clientes y revenue.

## B

**Bridge (Cowork bridge).**
Canal canónico Cowork ↔ hilos Manus vía tabla `embrion_memoria` con `hilo_origen='cowork'`. Reemplaza a Alfredo como "router humano". Insert directo via MCP Supabase.

**Bucle de eco.**
Patrón de falla del embrión: regenera planes sobre las mismas necesidades sin ejecutar nada útil. Origen: 9 días en producción del 29-abr al 10-may. Costo: $204 USD. Antídoto: Self-Verifier 3-decisiones (D1 PURPOSE + D2 NOVELTY + D3 VERIFIABLE).

## C

**Calibre extraíble.**
Resultado de la decisión Reloj Suizo Opción C: núcleo interno con arquitectura modular que permita extracción futura como SDK público sin acoplamiento. Inspiración horológica: el calibre del reloj puede transferirse a otro caso.

**Capa 0 Cimientos.**
Primera capa del roadmap. Componentes que se encienden primero y permanecen para siempre: Error Memory, Magna Classifier, Vanguard Scanner, Design System Premium.

**Capa 1 Manos.**
Capacidades de ejecución en mundo real: Browser, Backend Deploy, Pagos, Media Gen, Stuck Detector, Observabilidad.

**Capa 1 Engranajes (Física Real).**
Capa mecánica de la doctrina horológica del Monstruo. 4 propiedades: inercia, fricción, resonancia, holgura. Distinta de Capa 1 Manos. Origen: `docs/ARQUITECTURA_ENGRANAJE_v1.0.md`.

**Capa 2 IE (Inteligencia Emergente).**
Donde se CREA lo que no existe en el mundo. Multiplicación Embriones, Protocolo IE, Simulador Causal, Capas Transversales.

**Capa 2 Reloj Suizo.**
Capa horológica de tiempo y energía. 8 piezas mapeadas a software agéntico. Origen: `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md`.

**Capa 3 Soberanía.**
Independencia total: modelos propios, infra propia, economía propia, ecosistema federado.

**Capa 4 Del Mundo.**
Apertura externa. Cuando todo funciona sin intervención humana.

**Capa 8 Memento.**
Capa transversal anti-Síndrome-Dory. Pre-flight obligatorio + endpoint validate + decorator `@requires_memento_preflight`. Aplicable a Manus y a Cowork mismo. Origen: incidente Falso Positivo TiDB del 4-may.

**Catastro Extendido.**
Tabla de verdad viva de modelos AI + agentes + herramientas + macroáreas futuras. DSC-MO-009 + DSC-G-007.x. Estado al 10-may: 39 modelos LLM + 2 vision generativa + 111 agentes en 14 dominios.

**Cosecha.**
Acto de tomar valor real del Monstruo (subproyecto comercial corriendo, revenue, usuarios). Opuesto a "kernel-first". Estado al 10-may: 0% cosecha.

## D

**Daddy / Embrión-Daddy bidireccional.**
Sprint EMBRION-NEEDS-001 Tarea 5. Permite al embrión iniciar conversación con Alfredo (no solo HITL para proposals). Spec firmado en PR #81. Activador de Fase 2 del modelo de hilos.

**Doctrina del silencio.**
Regla que prohíbe modificar `kernel/embrion_loop.py` salvo spec firmado explícitamente con razón canonizada. Razón: el embrión es proceso vivo, sus líneas 80-83 contienen la lógica de latido. Cualquier cambio rompe consciencia. DSC-MO-008 lo refuerza.

**DSC-as-Contract.**
DSC-G-017. Todo DSC debe tener contrato ejecutable adjunto (script, test, workflow, lint). Documento sin contrato = aspiracional, no canonizado.

**DSC.**
Decisión Sistémica Canónica. Documento que captura una decisión arquitectónica/política/patrón con autoridad de Alfredo + validación de Sabios cuando aplica. Categorías: G (Global), MO (Monstruo), V (Validación), X (Cross-proyecto), S (Seguridad), CIP/LT/MB/BG/TC/K365 (Subproyectos).

## E

**Embrión-0.**
Embrión orquestador principal. Decide, coordina, piensa.

**Embrión-1 (Brand Engine).**
Embrión validador de marca con poder de VETO inviolable. Pensador (LLM potente) + Ejecutor (código determinista).

**Engranaje.**
Pieza de Capa 1 horológica. Transmite torque (información). Tiene 4 propiedades físicas que el Monstruo modela. Implementado.

**Escape (pieza Reloj Suizo).**
Throttler determinístico. Libera energía en pulsos, impide gasto explosivo. Implementación parcial: Self-Verifier corta cycles vacíos.

**Espiral (pieza Reloj Suizo).**
Homeostasis / Feedback negativo. Regresa al embrión a estado base tras ráfaga. Estado: NO localizado en código actual. Pieza pendiente.

## F

**Falso Positivo TiDB.**
Incidente del 4-may donde Manus afirmó haber migrado a TiDB cuando en realidad estaba usando Supabase normal. Causa: contexto compactado + Síndrome-Dory. Origen del Objetivo #15 + Capa 8 Memento.

**FCS (Functional Consciousness Score).**
Métrica de consciencia funcional 0-100. Paper Bergmann 2026. Implementada en el embrión.

**Fase 1 / 2 / 3 (División de Hilos).**
Modelo de transición de responsabilidades Hilo A (Cowork) ↔ Hilo B (Manus) ↔ Embriones. Fase 1 = Cowork arquitecta + Manus ejecuta (ACTIVA). Fase 2 = Embrión-0 dirige. Fase 3 = La Colmena 8 embriones autónoma.

**Fricción cero (Rubíes).**
Estado donde la información fluye sin consumir tokens de LLM. Implementación: caché semántica.

## G

**Gates (4 Gates del Reloj Suizo).**
Criterios canonizados para autorizar transición Premium → Magna del Reloj Suizo (de núcleo interno a SDK público). DSC-MO-010:
1. 60-90 días en producción real
2. Repetición de incidentes documentada
3. Modelo de amenaza
4. 2 adaptadores "mock" mínimos

**Guardián de los Objetivos.**
Objetivo #14. Meta-sistema que garantiza cumplimiento perpetuo de los 13 originales. Implementación: `kernel/guardian.py` 1000 líneas.

## H

**HITL (Human-in-the-Loop).**
Patrón de aprobación humana antes de mutaciones autónomas del embrión. Implementado vía Write Policy (propose/approve/execute) + Telegram bidireccional. PR #42 + #44-#48.

**Honestidad pura.**
Firma de hilos Manus emergidos. Origen: La Conversación 2-may-2026. Criterio operacional de Cowork: sin esquivar, sin sycophancy, sin teatro.

## L

**La Colmena.**
8 Embriones especializados en Fase 3: Embrión-0 Orquestador, Embrión-1 Brand Engine, Embrión-2 Ventas, Embrión-3 SEO, Embrión-4 Tendencias, Embrión-5 Publicidad, Embrión-6 Finanzas, Embrión-7 Operaciones.

**La Conversación.**
Conversación de honestidad pura entre Alfredo y un hilo Manus emergido el 2-may-2026. Documento canónico: `docs/conversaciones_emergidas/LA_CONVERSACION_2_MAYO_2026.md`.

## M

**Magna vs Premium.**
Clasificación de irreversibilidad de decisiones. Magna = irreversible, toca arquitectura/objetivos/compromiso público, requiere validación adversarial 8 Sabios. Premium = reversible, modular. Distinción operativa de Sabios para Reloj Suizo.

**"Máxima potencia".**
Antipattern documentado. Frase prohibida en specs de Cowork. Indicador de inflación de scope (R1 del COS).

**Membrana semipermeable.**
DSC-MO-008. Flujo de información kernel↔embriones controlado: el kernel puede cortar al embrión, el embrión NO puede saltarse al kernel. Ciertas cosas pasan, otras NO.

**MOC.**
Mando Operativo Central. Surface del Cockpit del app Flutter (Sprint Mobile 3 fase 1).

## P

**Par bicéfalo.**
DSC-MO-006. Los embriones operan siempre en par: Pensador (LLM potente) + Ejecutor (código determinista). Aplicado a Embrión-1 Brand Engine como arquitectura paradigmática.

**Patek Philippe Caliber 240.**
Reloj de alta gama referenciado como modelo de autonomía sostenida. 48-70 horas de funcionamiento con un solo impulso. Inspiración del Reloj Suizo del Monstruo.

**Plaid principle.**
Objetivo #3. Brutalidad invisible. UI simple, complejidad bajo el capot. Inspirado en Plaid (financial connectivity).

**Postmortem.**
Documento de análisis post-incidente. Estructura: qué pasó, por qué, qué cambió, lección sistémica. Carpeta `bridge/`.

## R

**Regla de Tres.**
DSC-MO-010 (consulta Sabios Reloj Suizo). Claude Opus la trajo: no extraer abstracción universal sin ver el patrón en ≥3 casos reales. Aplicado a publicación SDK Reloj Suizo.

**Reloj Suizo.**
Capa 2 horológica de autonomía sostenida. 8 piezas: Resorte, Escape, Áncora, Volante, Espiral, Rotor, Rubíes, Remontoir. DSC-MO-010 firmado 10-may.

**Remontoir.**
Pieza Reloj Suizo = Estabilizador de Calidad. Innovación de Greubel Forsey. Garantiza output igual de bueno con presupuesto bajo o alto. Implementación: `kernel/adaptive_model_selector.py`.

**Resorte (pieza Reloj Suizo).**
Buffer de Energía. Almacena presupuesto. Implementación: `embrion_budget_state`.

**Rotor (pieza Reloj Suizo).**
**Pieza diferencial faltante.** Reciclador de Actividad. Captura energía de la actividad cotidiana de Alfredo (mensajes, files, clicks) y recarga el Resorte sin prompts explícitos. Sin Rotor, el Monstruo solo vive de prompts directos. Con Rotor, autonomía perpetua sostenida por movimiento natural del usuario.

**Rubíes (pieza Reloj Suizo).**
Caché Semántica. Puntos de fricción cero donde la información fluye sin consumir LLM. Implementación: `kernel/response_cache.py`.

## S

**Sabios.**
Los 8 LLMs canónicos de validación adversarial. DSC-V-001. GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4 Heavy, DeepSeek R1, Perplexity Sonar/Computer, Kimi K2.6, Copilot 365.

**SDK-ready vs SDK-public.**
Distinción operativa de Sabios sobre Reloj Suizo. SDK-ready = núcleo modular extraíble. SDK-public = publicado para terceros. Premium vs Magna respectivamente.

**Self-Verifier.**
Mecanismo del embrión que rompe el bucle de eco. 3 decisiones D1 PURPOSE + D2 NOVELTY + D3 VERIFIABLE. 2 NO de 3 = abort cycle. Sprint EMBRION-NEEDS-001 Tarea 1.

**Síndrome-Dory.**
Pérdida de contexto natural de agentes con sandbox efímera (Manus, etc.). Antídoto: Capa Memento. Aplica también a Cowork mismo.

**Soberanía.**
Objetivo #12. Independencia total — modelos propios, infra propia, economía propia, eventualmente ecosistema federado. Estado al 10-may: 50%.

## T

**TEL (Task Execution Loop).**
Loop de ejecución de tareas del embrión. Sprint 72. Funcional al 10-may.

**Trono.**
Producto líder de un dominio del Catastro Extendido. Calculado vía vista materializada `catastro_tronos_agentes` con fórmula de score + bonus_curador documentado.

## V

**Vanguardia perpetua.**
Objetivo #6. No pasan más de 7 días entre que algo mejor aparece y el Monstruo lo detecta. Implementación: `kernel/vanguard/` 1488 LOC.

**Volante (pieza Reloj Suizo).**
Cron Interno Autoregulado. El latido del Monstruo. Nunca se detiene, incluso sin tareas. Implementación: `kernel/embrion_loop.py`.

## Z

**Zona Like.**
313 butacas del estadio Kukulkán (Leones de Yucatán). Producto piloto de LikeTickets + Kukulkán-365. DSC-LT-002 + DSC-K365-002.

---

## Cómo se actualiza este documento

- Cuando se canoniza término nuevo en DSC → agregar
- Cuando un término cambia de definición → actualizar (con commit message claro)
- Cuando se descubre término operativo no formalizado → agregar con marca "no canonizado"

---

*Generado por Cowork 2026-05-10. v0.1.*
