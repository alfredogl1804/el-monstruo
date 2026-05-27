# Cruce: Sprints Flutter/App-Vision × 15 Objetivos Maestros — Vigencia bajo "No Hay Interfaz"

**Autor:** Cowork (Arquitecto T2-A)
**Fecha:** 2026-05-27
**Autorización:** T1 Alfredo — "puedes cruzarlos con los 15 objetivos para ver cuáles están vigentes, la visión es que la interfaz del Monstruo es que no hay interfaz y las pantallas se invocan no se muestran"
**Método:** verificación directa de docs reales (anti-F2). Archivos leídos: `docs/EL_MONSTRUO_15_OBJETIVOS_MAESTROS.md`, `bridge/sprints_propuestos/sprint_mobile_2_modo_daily_fase1_stubs.md`, `sprint_mobile_3_modo_cockpit_fase1.md`, `sprint_mobile_REALIGNMENT_001.md`.

---

## 0. El ancla doctrinal (no es opinión Cowork — es objetivo canonizado)

`docs/EL_MONSTRUO_15_OBJETIVOS_MAESTROS.md` **línea 149**, Objetivo #3 (Principio Plaid):

> "Una sola interfaz — Un chat. Un input. Sin menús infinitos, sin configuración visible."

La visión T1 "no hay interfaz, las pantallas se invocan no se muestran" **no es nueva** — es la lectura literal del Objetivo #3 + Objetivo #2 (Apple/Tesla = interfaz invisible). Esto convierte el cruce en binario: todo sprint que construya **chrome de navegación persistente** (tabs, sidebar, dashboard multi-superficie) **contradice un objetivo canonizado**.

---

## 1. Veredicto por sprint

| Sprint | Qué construye | Paradigma | Veredicto |
|---|---|---|---|
| **mobile_1 esqueleto** (ejecutado) | Chat con kernel | Un input | ✅ **VIGENTE** |
| **A2UI / GenUI renderer** `core/a2ui/` (MOBILE_1B PR #92 + REALIGNMENT T1/T2) | Render generativo de componentes UI invocados por el agente | **Pantallas se invocan** | ✅ **VIGENTE — es EL mecanismo de la visión** |
| **mobile_REALIGNMENT_001** (ejecutado PR #114) | Renames DSC-G-004 + `core/a2ui/` + `mode_provider` toggle Daily/Cockpit + `mode_router` + BottomNav | Mixto | ⚠️ **PARCIAL** — plumbing A2UI vigente; el toggle Daily/Cockpit + BottomNav nacen obsoletos |
| **mobile_2 Daily Fase 1** (NO ejecutado) | BottomNavigationBar 5 tabs: Home, Threads, Pendientes, Conexiones, Perfil (líneas 21, 253-257) | Chrome persistente | ❌ **OBSOLETO** vs Obj #3 |
| **mobile_3 Cockpit Fase 1** (NO ejecutado) | Sidebar + MOC Dashboard + Catastro 3-tab + Embriones + Guardian (líneas 276-316) | Dashboard navegable | ❌ **OBSOLETO** vs Obj #3 |
| **mobile_4 Cockpit Fase 2** (NO ejecutado) | 5 superficies: Memento, Portfolio, FinOps, Pipeline, Replay (mobile_3 §351) | Dashboard navegable | ❌ **OBSOLETO** vs Obj #3 |
| **mobile_5 Cockpit Fase 3** (NO ejecutado) | 5 superficies: Computer Use, Coding, Hilos Manus, Bridge, Settings → "15-surface Cockpit = CARA DEL MONSTRUO COMPLETA" (mobile_3 §352-353) | Dashboard navegable | ❌ **OBSOLETO** — es el opuesto literal de "no hay interfaz" |

**Conteo real de sprints Flutter canonizados-no-ejecutados = 4** (mobile_2 + mobile_3 + mobile_4 + mobile_5), todos OBSOLETOS bajo la visión. El "~50/35/17" que Alfredo recordaba **no son archivos de sprint** — es el scope del roadmap `APP_VISION v1.3` (~75-80% sin ejecutar per CLAUDE.md). Esos ~50 ítems son **capabilities**, no pantallas; se re-enmarcan, no se descartan.

---

## 2. Cruce contra los 15 Objetivos (los que mueven la aguja)

| Objetivo | Relación con mobile_2-5 | Efecto |
|---|---|---|
| **#3 Mínima complejidad** (L149 "un chat, sin menús, sin config visible") | **Contradicción frontal.** 15 superficies + BottomNav + Sidebar = "menús infinitos" prohibidos | **Falsador principal** |
| **#2 Apple/Tesla** | Calidad Apple = interfaz que desaparece, no 15 tabs | Refuerza no-interfaz |
| **#1 Valor real medible** | El VALOR está en los datos (Catastro, Embriones, Guardian, FinOps), no en el chrome que los enmarca | Re-enmarcar |
| **#9 Transversalidad (8 capas)** | Las superficies Cockpit ya SON capas transversales — deben **invocarse**, no tabularse | Re-enmarcar |
| **#10 Psicohistoria / #11 Embriones / #14 Guardian / #15 Memoria** | Son las **fuentes de datos** que el A2UI invoca on-demand (voz/chat → kernel streamea la superficie) | Fuente de invocación |

Ningún objetivo exige una pantalla persistente. Cada "superficie" Cockpit es **dato invocable**, no destino navegable.

---

## 3. Recomendación arquitectónica (Cowork T2-A)

1. **VIGENTE y a profundizar:** A2UI / GenUI renderer (`core/a2ui/`). Es el órgano que materializa "las pantallas se invocan". Prioridad de inversión.
2. **DEPRECAR como paradigma primario:** el toggle Daily/Cockpit + BottomNavigationBar + Sidebar de REALIGNMENT_001. Ya está en main (PR #114) → no se borra, se marca `@Deprecated` y deja de ser la cara del Monstruo.
3. **CONGELAR mobile_2/3/4/5** en `sprints_propuestos/` con tag `[OBSOLETO-NO-INTERFAZ-2026-05-27]`. No ejecutar como están escritos.
4. **RE-ENMARCAR el contenido valioso:** cada superficie (Catastro, Embriones, Guardian, FinOps, Pipeline, Río Cronos, Threads) se convierte en un **A2UI component invocable** — el kernel decide cuándo streamearla en respuesta a intención del usuario (voz/chat), no el usuario navegando tabs.
5. **Nuevo sprint sucesor propuesto:** `sprint_mobile_A2UI_INVOCATION_001` — catálogo de componentes invocables + protocolo de invocación (intención → kernel → A2UI stream → render efímero). Sustituye Mobile 2-5.

---

## 4. Pendiente de decisión T1

- ¿Autorizas marcar mobile_2/3/4/5 como `[OBSOLETO-NO-INTERFAZ]` y redactar `sprint_mobile_A2UI_INVOCATION_001` como sucesor?
- ¿Canonizamos esto como DSC nuevo (ej. `DSC-MO-012 — Paradigma de Invocación, No de Navegación`) para que ningún hilo futuro reconstruya el Cockpit de 15 tabs?

**Firma:** Cowork T2-A — veredicto reversible, T1 puede revocar. Cero ejecución de código en este cruce; solo arquitectura.
