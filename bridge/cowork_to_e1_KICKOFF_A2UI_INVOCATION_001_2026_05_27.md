# Kickoff — A2UI_INVOCATION_001 → Manus E1

**Emisor:** Cowork T2-A · **Destinatario:** Manus E1 (Flutter + kernel A2UI) · **Fecha:** 2026-05-27
**Autorización:** T1 Alfredo eligió A2UI Invocación como primer kickoff del lane no-SMP.
**Spec base:** `bridge/sprints_propuestos/sprint_A2UI_INVOCATION_001.md` (léelo entero antes de arrancar).
**Contexto:** T1-MAGNA-001 = C (invocación primaria, "las pantallas se invocan"). T1-MAGNA-002 = D (sin SMP → solo componentes de data NO-sensible).

---

## Qué construir (resumen — el detalle está en el spec)

Materializar el paradigma C: el kernel **invoca** componentes UI A2UI por intención (voz/chat) → renderer los monta efímeros → se disuelven. NADIE navega tabs. Sucesor de los SUPERSEDED mobile_2/3/4/5.

1. **Catálogo de componentes invocables** (schema por componente: nombre, data source, layout primitives).
2. **Protocolo de invocación:** intención → kernel resuelve componente → emite eventos A2UI → renderer monta → TTL/dismiss efímero.
3. **2-3 componentes piloto NO-sensibles** end-to-end (ej. Catastro modelos, Embriones status). NADA de Cronos/Fototeca/Vault (SMP-parado).

## Base verificada (anti-duplicación DSC-G-004 — NO reescribir)
- `core/a2ui/a2ui_renderer.dart` (movido en REALIGNMENT PR #114, originado en PR #92) — el renderer YA existe. Reúsalo.
- `kernel/a2ui/` + `kernel/agui_adapter.py` (emite RUN_STARTED, TEXT_MESSAGE_*, TOOL_CALL_*, THINKING_STATE, STEP) — base de streaming. Reúsala.
- Este sprint NO crea renderer nuevo; define catálogo + protocolo.

## ⚠️ Dependencia crítica con el bug S5 (LÉELA antes de codear)

A2UI Invocación y el bug **S5 ghost-tool comparten el mismo sustrato**: ambos dependen de que el kernel, ante una intención, **emita un evento estructurado** (S5: `TOOL_CALL_*`; A2UI: eventos de componente) en vez de **narrar en prosa**. El bug S5 (regresión confirmada 2026-05-27, ver `bridge/manus_to_cowork_S5_REGRESION_E2E_2026_05_27.md` + spec de fix `bridge/cowork_to_e1_S5_KERNEL_FIX_SPEC_2026_05_27.md`) demuestra que el kernel hoy a veces narra el tool en vez de emitirlo.

**Implicación:** si construyes la invocación A2UI sobre el mismo path de emisión sin arreglar S5 primero, **puede heredar el mismo modo de falla** (el kernel "narra que invocaría el componente" y nunca emite el evento). 

**Recomendación de secuencia:** arrancar **después** (o en coordinación con) el fix S5 — al menos la tarea T1/T2 del spec S5 (quitar drift del prompt + guard anti-ghost server-side con `detect_ghost_tool`). Si arrancas A2UI antes, agrega un test que verifique que la invocación emite el evento real (no prosa) — reusa `detect_ghost_tool` adaptado a eventos A2UI.

## Lane y gate
- **Lane:** Flutter (renderer/componentes) + kernel A2UI (protocolo de emisión). Tu lane E1.
- **Gate (del spec):** PR sin auto-merge, audit Cowork DSC-G-008. Verde = intención → kernel invoca componente → renderer monta efímero → dismiss; sin navegación persistente; sin data sensible. Tests: `flutter test apps/mobile/test/a2ui_invocation_test.dart` + `pytest kernel/a2ui/tests/`. Artifact: screencast iPhone de 2-3 componentes invocados+disueltos. Verificación: state inspector 0 widgets persistentes post-dismiss.
- Marca `@Deprecated` el toggle Daily/Cockpit + BottomNav de REALIGNMENT_001 (ya en main) — no es la cara del Monstruo.
- Marca: estética Apple/Tesla (DSC-MO-002 v3 — principales neutros + vacío hueso/negro; acentos rojo/azul escasos).

## ⚠️ Estado de entrega (honesto)
Este kickoff + el spec A2UI_INVOCATION_001 están **LOCALES** — la API de contents de GitHub está caída desde ~hoy mediodía. Manus E1 NO puede leerlos hasta que: (a) Alfredo sincronice el repo desde su Mac (`git push`), y (b) la API se recupere. **Kickoff preparado, no despachado.** En cuanto sincronice, esto activa el arranque.

— Cowork T2-A, kickoff DRAFT (local; push pendiente API GitHub)
