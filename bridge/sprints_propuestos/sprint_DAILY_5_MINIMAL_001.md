# Sprint DAILY_5_MINIMAL_001 — Backstop mínimo bajo paradigma C

**Autor:** Cowork (Arquitecto T2-A) · **Fecha:** 2026-05-27 · **Estado:** DRAFT para firma T1
**Paradigma:** T1-MAGNA-001 = C — Daily 5 es la ÚNICA pantalla del Acto 1 que sobrevive, como **backstop minimalista**, no como la cara del Monstruo. D (sin SMP).
**Owner:** Manus E1 (Flutter). **Lane:** UI backstop no-SMP.
**Objetivo:** Pantalla Daily mínima como red de seguridad bajo paradigma C, sin Cockpit ni tabs, lanzadora hacia invocación.

## Objetivo
Pantalla Daily mínima como red de seguridad cuando la invocación (voz/WhatsApp/A2UI) no basta o falla — NO como destino de navegación primario. Bajo C, la invocación es el modo principal; Daily 5 existe para "¿qué tengo hoy?" y como fallback si el ambient falla (la red que el Acto 2 puro NO tiene).

## Diferencia con el SUPERSEDED mobile_2
mobile_2 proponía 5 tabs (Home/Threads/Pendientes/Conexiones/Perfil) con BottomNav como paradigma central. Aquí Daily 5 es **mínima y secundaria**: una vista de estado del día, invocable, no el centro de gravedad. Sin Cockpit, sin toggle.

## Alcance bajo D
- ✅ Estado del día con data no-sensible: pendientes, hilos recientes (resumen no-sensible), accesos.
- ❌ NO Río Cronos, NO captura personal, NO Vault (SMP-dependiente, diferido).

## Tareas
- T1: shell Daily mínima (1 superficie de estado, no 5 tabs navegables) reusando `core/a2ui/` donde aplique.
- T2: data no-sensible (pendientes, threads resumidos) vía kernel; sin persistencia personal.
- T3: entrada a invocación (voz/chat) desde Daily — Daily NO atrapa al usuario; lo lanza a invocar.
- T4: tests — render, data no-sensible, ruta a invocación.

## Reglas duras
- NO reconstruir el Cockpit de 15 tabs (T1-MAGNA-001 lo canceló).
- Naming DSC-G-004. Estética Apple/Tesla (DSC-MO-002 v3 — PRINCIPALES: neutros sólidos + vacío hueso/negro absoluto; ACENTOS escasos: escala rojo Tesla #E82127 + escala azul Apple #0071E3, nunca como fondo).
- Cero data sensible bajo D.

## Criterios de Cierre
PR sin auto-merge, audit Cowork DSC-G-008. Verde = Daily mínima renderiza estado no-sensible + lanza a invocación, sin tabs Cockpit, paleta Apple/Tesla. **Comando reproducible:** `flutter test apps/mobile/test/daily_minimal_test.dart`. **Artifact:** screenshot Daily renderizada en iPhone + grep "BottomNav" devuelve 0 ocurrencias. **Verificación no-sensibilidad:** code review confirma 0 imports de Cronos/Fototeca/Vault.

— Cowork T2-A, DRAFT (local; push pendiente API GitHub)
