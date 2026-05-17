# PACK 00 — BOOTSTRAP

> **Una página. Donde está el Monstruo en interfaces hoy, sin retórica.**

---

## El Monstruo en una frase

El Monstruo es **el sistema operativo personal soberano** de Alfredo González — no es un SaaS, no es un VC-funded startup, no es una herramienta freemium. Eventualmente versiones reducidas pueden ser otorgadas selectivamente. *(SRC-001 Cap 0)*

## La doctrina arquitectónica magna (corregida 2026-05-11)

> *"El Monstruo no es una app — es un kernel con múltiples cuerpos."* *(SRC-002 §0, SRC-001 Cap 1)*

Hay **un cerebro central** (LangGraph + 4 Catastros + 9+ Embriones + memoria SMP + ejecución consciente) y **N transports** que sirven el mismo propósito desde contextos distintos. Ningún transport es "la app del Monstruo" — todos son ciudadanos de primera clase del mismo kernel.

## Los dos paradigmas en conflicto (decisión T1 magna pendiente)

### Acto 1 — Diseño co-creado Alfredo ↔ Cowork (mayo 6)
- App excelente con paleta forja-graphite-acero
- 5 superficies Daily + 15 superficies Cockpit = **20 superficies fijas**
- Calidad Apple/Tesla por pixel
- *(SRC-001 Cap 2-3, SRC-021)*

### Acto 2 — Calm Tech / Hilo B paralelo (mayo 7-11)
- Equipo agéntico de 10+ roles ambient
- **Voz, notificación, conversación, automático** > UI visual
- Métrica de éxito: cuántas veces NO necesitás abrir nada
- Frase canónica magna §9.F: *"Si el usuario tiene que abrir dashboard para saber qué pasa, el Monstruo ya falló."* *(SRC-005)*
- Engranaje (⚙️ literal) + Reloj Suizo (8 piezas Patek) + Methodology-as-a-Service

### Conflicto sin firma
Acto 1 dice "20 superficies funcionales = éxito". Acto 2 dice "abrir el dashboard = falla". Ambos firmados (Acto 1 por Cowork T2, Acto 2 por Hilo B Manus + 4 sabios). Sin integración explícita, todo sprint UI nuevo arrastra deuda doctrinal.

## La realidad cruda del código (16-may)

| Dimensión | Estado |
|---|---|
| Brand DNA en mobile | **Cyan #00E5FF + púrpura #BB86FC** (viola canon forja-graphite-acero) |
| Modes Daily/Cockpit | NO existen (`lib/modes/daily/` ❌, `lib/modes/cockpit/` ❌) |
| 8 capabilities transversales | **0/8** implementadas |
| 5 superficies Daily | **0/5** existen |
| 15 superficies Cockpit | **0/15** existen (1 sola pantalla MOC vaga) |
| SMP (Sovereign Memory Protocol) | NO existe en código |
| Toggle Daily↔Cockpit | NO existe |
| Listening ambient | NO existe |
| Cronos | NO existe |
| Modo Confidente | NO existe |
| WhatsApp Gateway | NO existe |
| Apple Watch | NO existe |
| **Total Flutter** | **52 archivos .dart, prototipo Tier-Owner que Alfredo usa en su iPhone** |
| **Command Center web** | **7 superficies reales** (chat, finops, fleet, memory, runs, security, settings) en Next.js separado |
| **La Forja web** | Sprint v3.2 firmado, `apps/la-forja/` |
| **Bot Telegram** | Online en Railway |
| **A2UI** | Spec firmado + 51 tests en PR #92 NO mergeado, schema.py implementado en kernel |

## Las 5 decisiones T1 magna pendientes (heredadas del audit Cowork 11-may)

1. **Brand DNA en prototipo**: ¿refactor inmediato a forja o mantener cyan/púrpura como "Tier-Owner heritage"?
2. **Sprint Mobile 0 SMP timing**: ¿arranca YA en paralelo o se difiere?
3. **Hilo Mobile dedicado**: ¿se asigna un Manus exclusivo o rotamos?
4. **PR #92 A2UI merge**: ¿T8 smoke en iPhone esta semana o queda en hold?
5. **Sprint 90 NPM Stripe**: ¿hold indefinido?

## Tres hipótesis nacientes (NO canonizar sin firma T1)

1. **AI-First Living / Soberanía Contextual** — "todo mi actuar gira en torno a cómo le facilito a la IA las cosas para que la IA me ayude a facilitarme las mías" (Alfredo verbatim 2026-05-16). Articulado, NO firmado.
2. **Doctrina de la Interfaz Latente** — "la interfaz definitiva no tiene 20 superficies fijas. Tiene N superficies latentes que se invocan cuando el contexto lo demanda". Confirmado por Alfredo, NO commiteado.
3. **Servicio Silencioso bajo Co-Construcción Activa** — el usuario alimenta a la IA, la IA reciproca. NO es servicio pasivo. Articulado, NO firmado.

## El estado del Fabric

Esta es la **iteración 001 de INTERFACES-CONTEXT-FABRIC-001**. Manus es ejecutor forense. ChatGPT 5.5 Pro es arquitecto principal de interfaces. Cowork y Perplexity son auditores. Alfredo es T1 final solo para huecos irreducibles.

## Próximo paso

ChatGPT lee este pack, después `PACK_01_ACTO_1` y `PACK_02_ACTO_2`, después `PACK_10_REALIDAD_CODIGO_ACTUAL`, y produce su primera **decisión arquitectónica magna**: ¿Acto 1, Acto 2, o integración?
