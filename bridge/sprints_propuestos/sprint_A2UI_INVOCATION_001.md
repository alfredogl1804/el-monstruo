# Sprint A2UI_INVOCATION_001 — Paradigma de invocación (sucesor de mobile_2-5)

**Autor:** Cowork (Arquitecto T2-A) · **Fecha:** 2026-05-27 · **Estado:** DRAFT para firma T1
**Paradigma:** T1-MAGNA-001 = C — "las pantallas se invocan, no se muestran". Sucesor de los SUPERSEDED mobile_2/3/4/5 (Cockpit de 15 tabs cancelado).
**Owner:** Manus E1 (Flutter + kernel A2UI). **Lane:** UI invocacional (no SMP — render efímero, sin persistencia sensible).
**Objetivo:** Materializar paradigma C — el kernel invoca componentes UI A2UI bajo demanda, reemplazando Cockpit/Daily-tabs por superficies efímeras invocables por intención.

## Objetivo
Materializar el paradigma C: el kernel **invoca** componentes UI (A2UI) bajo demanda — el usuario expresa intención (voz/chat), el kernel decide, streamea la superficie, se disuelve. NADIE navega tabs. Reemplaza el contenedor Cockpit/Daily-tabs por componentes invocables.

## Base existente (anti-duplicación DSC-G-004)
- `core/a2ui/a2ui_renderer.dart` (PR #92, REALIGNMENT) — el renderer ya existe. NO reescribir.
- `kernel/a2ui/` + `kernel/agui_adapter.py` (eventos TOOL_CALL_*, A2UI) — base de streaming. Reusar.
- Este sprint NO crea un renderer nuevo; define el **catálogo de componentes invocables** + el **protocolo de invocación**.

## Alcance bajo D
- ✅ Componentes invocables de **data no-sensible**: Catastro (modelos/suppliers/tools), Embriones status, Guardian 15-objetivos, FinOps/burn-rate, Pipeline.
- ❌ NO componentes sobre data personal-sensible (Cronos, Río, Fototeca personal) — SMP-dependiente, diferido.

## Tareas
- T1: catálogo de componentes A2UI invocables (schema por componente: nombre, data source, layout primitives del renderer existente).
- T2: protocolo de invocación — intención (voz/chat) → kernel resuelve componente → emite eventos A2UI → renderer monta → TTL/dismiss efímero.
- T3: 2-3 componentes piloto no-sensibles (ej. Catastro modelos, Embriones status) end-to-end.
- T4: gesto/comando de dismiss (la superficie se disuelve; no queda como tab).
- T5: tests — invocación por intención, render del componente, dismiss, NO persistencia.

## Reglas duras
- Reusar `a2ui_renderer.dart` + `agui_adapter.py`. Cero renderer nuevo.
- Naming DSC-G-004. Cero pantallas persistentes (paradigma C).
- Marcar `@Deprecated` el toggle Daily/Cockpit + BottomNav de REALIGNMENT_001 (ya en main) — no es la cara del Monstruo.

## Criterios de Cierre
PR sin auto-merge, audit Cowork DSC-G-008. Verde = intención → kernel invoca componente → renderer lo monta efímero → dismiss, sin navegación persistente, sin data sensible. **Comando reproducible:** `flutter test apps/mobile/test/a2ui_invocation_test.dart` + `pytest kernel/a2ui/tests/ -v`. **Artifact:** screencast iPhone mostrando los 2-3 componentes piloto invocados y disueltos. **Verificación no-persistencia:** state inspector confirma 0 widgets persistentes post-dismiss.

— Cowork T2-A, DRAFT (local; push pendiente API GitHub)
