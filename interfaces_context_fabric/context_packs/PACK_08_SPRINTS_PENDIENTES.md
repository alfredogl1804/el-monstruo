# PACK 08 — Sprints UI pendientes (mapa operativo)

> **Estado:** mapa vivo, requiere refresh con cada commit a `bridge/sprints_propuestos/`
> **Fuente:** `bridge/sprints_propuestos/` + audit Cowork SRC-002 §6-§7

---

## Lectura del estado del backlog UI

El audit Cowork del 11-may produjo un veredicto magna sobre el backlog de sprints UI: la mayoría de sprints "Mobile 2/3/4/5" están **parcialmente implementados** (entre 10% y 50%) y arrastran asunciones del paradigma "una app única" que el shift conceptual ha invalidado. La acción correcta NO es continuarlos — es **reescribirlos** bajo el principio kernel+N transports y bajo el sequencing de Realignment 001 → SMP → Daily 5 → Cockpit 1/2/3.

A esto se suma una **deuda magna de canonización**: los transports prioritarios P0 (WhatsApp Gateway) y los componentes magna del Reloj Suizo (Rotor, Espiral) tienen sprints firmados pero NO ejecutados. La cadena de bloqueo es pesada.

---

## Tabla canónica del estado al 17-may-2026

| Sprint | Categoría | Estado | Acción recomendada Cowork |
|---|---|---|---|
| Sprint 88 cierre v1 producto | core | MERGEADO | archive a `_completados/` |
| Sprint S001 security hardening | core | MERGEADO | archive |
| Sprint S002.6 RLS continuación | core | MERGEADO | archive |
| Sprint 89 catastros extension | core | propuesto | go (instala CatastroBase para A/B) |
| Sprint 90 NPM Stripe | core | propuesto | hold indefinido (T1 magna pendiente) |
| Sprint S-CONTRATOS-001 | doctrina | propuesto | go (cierra deuda DSC-as-Contract + Cap 17) |
| GUARDIAN_AUTONOMO_001 | core | firmado | go — kickoff `93d6d649` |
| ROTOR_001 | UI Reloj Suizo | firmado, NO ejecutado | go orden 2 (post-Guardian) |
| ESPIRAL_001 | UI Reloj Suizo | firmado, NO ejecutado | después de ROTOR_001 |
| TRANSVERSAL_001 (PR #100) | core | kickeado, cleanup G5 pendiente | Ejecutor 2 cleanup + merge |
| Catastro-A | catastros | propuesto | go (post-Sprint 89) |
| Catastro-B | catastros | propuesto | go (paralelizable con A) |
| Mobile 1 esqueleto | UI mobile | parcial ~35% | rewrite como **MOBILE_REALIGNMENT_001** (firmado T1, NO ejecutado) |
| Mobile 2 modo daily fase 1 | UI mobile | parcial ~20% | rewrite como **DAILY_5_SUPERFICIES** |
| Mobile 3 cockpit fase 1 | UI mobile | parcial ~50% | rewrite como **COCKPIT_1** |
| Mobile 4 cockpit fase 2 | UI mobile | ~10% | rewrite como **COCKPIT_2** (sin "Show API keys" — viola DSC-S-001) |
| Mobile 5 cockpit fase 3 | UI mobile | ~10% | rewrite como **COCKPIT_3** |
| MOBILE_1B_A2UI_IMPLEMENTATION | UI mobile | PR #92 con 51 tests, NO mergeado | T8 iPhone smoke pendiente (decisión T1 magna) |
| LA_FORJA_001 v3.2 | web hijo | firmado 15-may | ejecución parcial branch `sprint/la-forja-001` |
| COWORK_MEMENTO_001 | core | mergeado | archive |

---

## Sprints nuevos faltantes por canonizar (orden Cowork §7)

El audit Cowork cerró la lista priorizada de 17 sprints nuevos que hay que canonizar para que el track UI avance bajo doctrina correcta. Vienen en este orden operativo:

1. **MOBILE_REALIGNMENT_001** — evolución no big-bang del codebase actual. Firmado T1 12-may, NO ejecutado. Crítico para destrabar todo lo demás.
2. **MOBILE_0_SMP** — cimiento APP_VISION Cap 7. 2-4 semanas. Pre-requisito de auth, vault, ambient. **Decisión T1 magna pendiente** sobre timing.
3. **KERNEL_0_EJECUCION_CONSCIENTE** — 7 capas de ejecución consciente Cap 1. 4-6 semanas paralelo a Mobile 0.
4. **WHATSAPP_GATEWAY_P0** — paralelo a Flutter Daily, LATAM 72% conversacional.
5. **DAILY_5_SUPERFICIES** — Home / Threads / Pendientes / Conexiones / Perfil rebuild bajo Realignment.
6. **VOICE_BRAND_ELEVENLABS** — voz única del Monstruo (registro bajo, gravitas, calidez contenida).
7. **LISTENING_AMBIENT_CAPABILITY** — VAD + Whisper local + kill switch verbal "Monstruo apágate".
8. Las **8 capabilities transversales**: VISUAL_SEARCH, PHOTO_INTELLIGENCE, FILE_INTELLIGENCE, APP_INTELLIGENCE, VAULT_SOBERANO, SHOPPING_INTELLIGENCE, NOTES_INTELLIGENCE, HEALTH_INTELLIGENCE.
9. **CRONOS_1** + **CRONOS_2** + **CRONOS_3** — río + 9 capas + niebla del futuro.
10. **SMART_RENDERING_CAPABILITY** — composición sobre 4 Catastros.
11. **PORTFOLIO_EMPRESAS_HIJAS_UI** — 20 proyectos como tarjetas vivas (CIP primera) en Cockpit.
12. **COCKPIT_1/2/3** + **TOGGLE_DAILY_COCKPIT**.
13. **AUTH_TIERS_001** — Owner / Trusted / Funcional Accesible.
14. **MODO_CONFIDENTE_UI** — sin nombre + deep link silencioso desde WhatsApp.
15. **MOBILE_6_POLISH_I18N** — Watch + i18n + WCAG.
16. **DSC_S012_EXECUTABLE_CONTRACT** — deadline 2026-06-10.
17. **HOUSEKEEPING_SPRINTS_INDEX** — mover Sprint 88, S001, S002.6 a `_completados/`.

Cowork firmó que **puede redactar las specs sucesivamente sin esperar T1**, siempre que cada una respete estructura R1-R5, cite DSCs, declare ETA realista, y sin violaciones de seguridad. Ese mandato sigue vigente.

---

## Lo que ChatGPT debe decidir en iteración 002

La pregunta arquitectónica clave es **cuál de los 17 sprints sale primero del backlog y entra al pipeline de ejecución**. La respuesta NO es trivial — depende de qué paradigma gana (Acto 1 vs Acto 2) y de qué decisiones T1 magna se firman.

Si gana Acto 1, el orden natural es Realignment → Mobile 0 SMP → Daily 5 superficies → Cockpit 1/2/3, secuencial sobre el codebase Flutter actual evolucionado.

Si gana Acto 2 Calm Tech, el orden cambia drásticamente: WhatsApp Gateway P0 + Listening Ambient + Voice Brand suben, Cockpit baja, y las 20 superficies se diluyen a "backstops cuando el ambient falla". Los sprints de Cockpit pueden quedarse en estado de espec sin construirse hasta que haya volumen real de usuarios.

Si gana una integración consciente (que es probablemente lo que va a salir), ChatGPT tiene que producir un **sequencing nuevo** que conjuga ambos paradigmas y que reescribe la prioridad de los 17 sprints.
