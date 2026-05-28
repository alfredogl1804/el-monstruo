# FORJA OMEGA — Prompt Visual v2 (Factory Mode UI en `tablero-campana`)

**Versión:** v2 — calibrado contra Genome vivo `binario_100=true` (2026-05-28T02:21:38Z, size 394 542 B)
**Autor:** Manus B (Hilo B, cuenta `manus_b`)
**Fecha de emisión:** 2026-05-28
**Habilitado por:** PR #231 (firmas T1-006 D + T1-007 C, SHA `736b47e`), PR #233 (cierre sprint, SHA `a3fb5ef`), PR #234 (bridge S5 evidencia, SHA `ffb605e`)
**Destino:** sprint nuevo `SPR-FACTORY-UI-001` a registrarse en `sprints/registry.yaml` con paradigm `frontend` y capa `C1 + C2`

---

## 1. Por qué este prompt es v2 y no v1

ChatGPT entregó un manifiesto FORJA OMEGA de 932 líneas que describía **12 motores cognitivo-ejecutivos** que ya existen o están en construcción avanzada en el Monstruo. Si ejecutáramos ese prompt al pie de la letra construiríamos por segunda o tercera vez código que ya está vivo.

Esta v2 se calibra contra el **Genoma vivo** y restringe el alcance a una sola cosa: **la UI de Factory Mode en `tablero-campana`** — el delta real entre lo que se ve hoy en el tablero (5 lentes vivas, panel Forja shadow, omnibox, brújula, sprints panel, timeline slider) y lo que la Cognitive Republic exige mostrar.

**Cero código de backend en este sprint.** Los 4 endpoints aggregator ya existen (`/v1/factory/{constellation,economy,timeline,diff}`, 938 LOC en `kernel/factory_routes.py`, auth gate 401 confirmado). Cero código de envelope-mesh: `server/forja/` ya tiene 2 549 LOC TS en la rama `design/forja-os-sovereign-agentic-fabric`. Cero nuevas tablas: las nueve `forja_*` ya viven en Supabase.

---

## 2. Auditoría binaria pre-prompt — qué ya existe

La columna **Evidencia** apunta a archivo, commit o endpoint verificable hoy.

| Componente | Estado | Evidencia |
|---|---|---|
| 4 endpoints `/v1/factory/*` | **LIVE con auth gate** | `kernel/factory_routes.py` 938 LOC; HTTP 401 + payload JSON `{"detail":"Missing API key..."}` |
| 9 tablas `forja_*` Supabase | LIVE | Genome `summaries.supabase.tables[157..165]`: `forja_actions, _budget, _messages, _profiles, _simulations, _sprints, _telemetry, _threads, _validations` |
| `server/forja/` envelope mesh | LIVE (rama design) | 2 549 LOC TS en `design/forja-os-sovereign-agentic-fabric`; tag `forja-v4-envelope-001`; archivos: `gateway.ts` 442, `router.ts` 644, `attenuation-verifier.ts`, `canonical.ts`, `ed25519.ts`, `types.ts`, 4 archivos de tests |
| `ForjaShadowPanel.tsx` cliente | LIVE | `client/src/components/hud/ForjaShadowPanel.tsx` 186 LOC, ya wireado en `Home.tsx:48,260-273` con queries tRPC `forjaShadow.{allowlist,stats,list}` |
| 5 lentes vivas en `LayerSwitcher` | LIVE | Distrito · Salud · Antigüedad · Tamaño · Cambio (`client/src/components/hud/LayerSwitcher.tsx`) |
| Brand DNA Forja | CANONIZADO | `AGENTS.md` Regla Dura #4: naranja `#F97316` + graphite `#1C1917` + acero `#A8A29E`, brutalismo industrial refinado |
| Sprint 91 Genome Vivo | LIVE | `binario_100=true`, 103 repos / 19 servicios / 287 tablas / 328 RPCs |
| Embrion-loop | ACTIVE | 209 ciclos, sano post-fix kimi-k2-6, costo `≈USD 1.45/día` |
| Sprint `SPR-FACTORY-AGGREGATORS-000` | COMPLETED | PR #216 mergeado; schemas JSON canonizados de los 4 endpoints |
| T1-006 Opción D | FIRMADA | PR #231 SHA `736b47e` |
| T1-007 Opción C | FIRMADA | PR #231 SHA `736b47e`; `bridge/missions/README.md` canonizado |
| `bridge/missions/` capa viva | CANONIZADO | Coexistencia jerárquica `registry.yaml + bridge/missions/ + sprints_completados/` |

> **Regla operativa:** si el prompt v2 propone reconstruir cualquier ítem listado arriba, **el sprint debe rechazarse** y reescribirse el prompt. Todo lo anterior se usa, se conecta o se reusa — nunca se duplica.

---

## 3. Delta real — qué falta para Factory Mode UI

Lo que **no existe hoy** y este prompt manda construir:

1. **Una 6ª lente en `LayerSwitcher`** llamada **"Fábrica"** que cambia el modo de render del `IsometricBoard` de "ecosistema declarativo" (vista actual) a "vista federada de fábricas" alimentada por `/v1/factory/constellation`.
2. **Cuatro paneles HUD nuevos** (uno por endpoint), todos sidebar-derecha con la misma estética del `ForjaShadowPanel` existente:
   - `ConstellationPanel.tsx` — Forge nodes + envelope mesh edges en grid jerárquico (tiers `core | inner | mid | outer`).
   - `EconomyPanel.tsx` — Cognitive P&L: 15 KPIs en cards + 5 fórmulas canonizadas + disclaimer honesto sobre métricas con `null`.
   - `TimelinePanel.tsx` — Sovereign Time Axis: feed cronológico de eventos civilizacionales con filtros por `types`, badges por severidad, deltas (`sovereignty | productivity | risk | cost`).
   - `RealityDiffPanel.tsx` — Reality Diff: 4 dominios (`github, railway, supabase, live24h`) lado a lado, drift count, alertas.
3. **Un proxy server-side en `server/routers/factory.ts`** (tRPC) que llama los 4 endpoints aggregator con la `KERNEL_API_KEY` que vive en variables de entorno del backend `tablero-campana`. **El cliente NUNCA lleva la key** — todo va por el server-side BFF.
4. **Un dock unificado "Factory Mode"** en `Home.tsx` con un botón Forja extendido que abre un `Drawer` apilado de los 4 paneles (similar al `ForjaShadowPanel` actual pero con tabs).
5. **Hidratación reactiva** con `refetchInterval` calibrado por panel: constellation 30 s, economy 60 s, timeline 15 s, diff 120 s. Cada panel muestra `last_updated_at` derivado de `generated_at` del payload.
6. **Tests Vitest** para cada panel: shape match, manejo de `null` (data_quality.coverage = "partial"), filtros de query params (`tier`, `kind`, `window`, `types`, `limit`).

> Estimación de scope: **~1 200 LOC TSX** distribuidas en 6 archivos nuevos + 2 modificaciones (`LayerSwitcher.tsx`, `Home.tsx`) + 1 archivo de proxy tRPC. Aproximadamente 1 sprint de 1–2 días de Manus A.

---

## 4. Bandera de marca — el filtro estético

Cada componente nuevo **debe pasar la checklist Brand Compliance** del `AGENTS.md` Regla Dura #4 antes de declararse verde:

1. Forja `#F97316` para emisiones, acento de hover, badges activos.
2. Graphite `#1C1917` como fondo dominante, NO `bg-slate-*` genérico.
3. Acero `#A8A29E` para texto secundario y bordes; NO `text-gray-500`.
4. Sin gradientes morados, sin centrados generic, sin Inter (la fuente del tablero ya está canonizada como serif con anclas industriales).
5. Naming de funciones y endpoints con identidad: `useForjaConstellation`, `useCognitiveEconomy`, `useSovereignTimeline`, `useRealityDiff`. **No** `useFactoryData`, `useFactoryStuff`, `useMisc`.
6. Mensajes de error con formato `{module}_{action}_{failure}` — por ejemplo `constellation_fetch_auth_denied`, `economy_window_invalid`. **No** `"something went wrong"`.
7. El test final: ¿esto daría orgullo mostrarlo en una keynote de Apple sobre soberanía cognitiva? Si la respuesta es no, no está terminado.

---

## 5. Prompt operativo — copia y pega en sesión nueva

```text
ROL: Manus A (ejecutor técnico frontend).
PROYECTO: tablero-campana (rama base design/forja-os-sovereign-agentic-fabric).
SPRINT: SPR-FACTORY-UI-001 (a registrar en sprints/registry.yaml).
TOLERANCIA: lectura del kernel + UI nueva. Cero migrations. Cero secrets nuevos en client.
POWER LANE: L3 (Draft Execution) + L4 (local tests/build/check).

CONTEXTO BINARIO VERIFICADO (no negociable):
- Genome vivo: binario_100=true (2026-05-28T02:21:38Z).
- Endpoints /v1/factory/{constellation,economy,timeline,diff} ya viven en kernel
  el-monstruo (kernel/factory_routes.py, 938 LOC, auth gate 401).
- server/forja/ tiene 2549 LOC TS en design/forja-os-sovereign-agentic-fabric.
- ForjaShadowPanel.tsx (186 LOC) ya existe en client/src/components/hud/.
- T1-006 D + T1-007 C firmadas en PR #231 (SHA 736b47e).
- bridge/missions/ canonizada como capa viva por T1-007 C.

OBJETIVO ÚNICO:
Construir la 6ª lente "Fábrica" + 4 paneles HUD + proxy tRPC server-side que
consumen los 4 endpoints aggregator del kernel y los renderizan en la estética
Forja del tablero (naranja F97316 + graphite 1C1917 + acero A8A29E, brutalismo
industrial refinado).

ENTREGABLES:
1. server/routers/factory.ts (tRPC proxy, lee KERNEL_API_KEY del backend env).
2. client/src/components/hud/ConstellationPanel.tsx.
3. client/src/components/hud/EconomyPanel.tsx.
4. client/src/components/hud/TimelinePanel.tsx.
5. client/src/components/hud/RealityDiffPanel.tsx.
6. client/src/components/hud/FactoryModeDock.tsx (drawer con tabs hospedando los 4 paneles).
7. Modificación de client/src/components/hud/LayerSwitcher.tsx para agregar la 6ª lente "Fábrica".
8. Modificación de client/src/pages/Home.tsx para wirear FactoryModeDock al botón Forja existente.
9. Tests Vitest server/factory.proxy.test.ts (shape + manejo de 401) y server/factory.ui.test.ts (smoke render de los 4 paneles con fixtures).

REGLAS DURAS NO NEGOCIABLES:
- NO escribir KERNEL_API_KEY en código del cliente. Solo en el server BFF.
- NO inventar KPIs ni eventos: si el endpoint devuelve null o vacío, el panel muestra
  el disclaimer honesto del payload con copy de marca.
- NO usar bg-slate-*, bg-gray-*, text-gray-*, ni colores genéricos. SOLO los tres
  tokens Forja del Brand DNA.
- NO usar la palabra "Factory Mode" en UI visible al usuario. La lente se llama
  "Fábrica" en español, los paneles "Constelación", "Economía cognitiva",
  "Línea soberana del tiempo", "Diferencial de realidad".
- NO crear nuevas migraciones, NO modificar drizzle.config.ts.
- NO modificar archivos en server/forja/ ni en server/_core/. Esos son inmutables
  en este sprint.
- Cumplir checklist de marca de AGENTS.md Regla Dura #4 antes de cualquier checkpoint.

VALIDACIÓN PRE-MERGE:
1. pnpm typecheck pasa sin errores.
2. pnpm vitest run pasa con los nuevos tests.
3. pnpm build genera bundle sin warnings nuevos.
4. Screenshot de los 4 paneles en iPhone real (Safari) anexado al PR.
5. Audit Cowork sobre BRAND COMPLIANCE (no solo lectura del PR — verificación
   visual del bundle desplegado en Manus space).
6. PR body incluye sección "## E2E Evidence" con URLs de screenshots o label
   no-e2e-required si Cowork lo justifica.

PLAZO OBJETIVO: 1-2 días tras kickoff.

CIERRE: crear bridge/missions/SPR-FACTORY-UI-001/ con la estructura canonizada por
T1-007 C (0_intent.md, 1_orders/, 2_assemblies/, 3_executions/, 4_evidence/,
5_court/, 6_outcomes.md) y archivar al cerrar el sprint.
```

---

## 6. Diferencias con el manifiesto FORJA OMEGA original de ChatGPT

| Tema | ChatGPT v1 (932 líneas) | Manus B v2 (este prompt) |
|---|---|---|
| Alcance | 12 motores cognitivo-ejecutivos nuevos | Sola UI cliente sobre motores ya vivos |
| LOC estimado | varios miles | ~1 200 TSX |
| Backend nuevo | sí (Intent Reactor, Production Order Engine, etc.) | cero — los 4 endpoints ya existen |
| Tablas nuevas | sí | cero |
| Tiempo estimado | semanas | 1-2 días |
| Riesgo de duplicación | alto (T1-006/007 no estaban firmadas) | bajo (T1 firmadas, delta auditado contra Genome) |
| Brand compliance | no explícita | regla dura embebida |
| Validación de evidencia | no exigida | E2E iPhone real obligatorio |

---

## 7. Sub-sprints derivados que NO se ejecutan aquí

Quedan registrados como dependencias futuras, **fuera del alcance** de `SPR-FACTORY-UI-001`:

1. `sprint_T1_006_EMBRION_SANDBOX_PATCHES.md` — construir `tools/embrion_patch_writer.py` + schema JSON canónico de patches.
2. `sprint_T1_007_CONSOLIDADOR_MISSIONS.md` — `tools/missions_consolidator.py` + hook git pre-merge.
3. `DSC-G-008 v3 anexo` — Cowork extiende scope de audit a `bridge/missions/` y `bridge/embrion_patches/`.
4. `REPUBLIC-CONSTELLATION-001` piloto — el sprint que consume estos paneles con datos reales una vez Manus A los entregue.

---

## 8. Cierre y firma

Este prompt v2 sustituye al manifiesto FORJA OMEGA v1 de ChatGPT como **fuente única operativa para construir la Factory Mode UI**. Cualquier disonancia entre ambos se resuelve a favor de v2, porque v2 está calibrado contra el Genoma vivo con `binario_100=true` y respeta las firmas T1-006 / T1-007 ya merged.

**Estado:** propuesto. Para activarlo:

1. Alfredo da OK al prompt (puede tachar, sumar, restar).
2. Manus B abre el sprint `SPR-FACTORY-UI-001` en `sprints/registry.yaml` con estado `PROPOSED` y referencia este archivo.
3. Cowork audita el sprint pre-arranque (DSC-G-008 v2).
4. Manus A ejecuta el prompt como agente frontend en una sesión limpia.

**Emitido por:** Manus B (cuenta `manus_b`, Hilo B ejecutor técnico)
**Sesión origen:** Cabina post-rebase #227 + firmas T1 binarias + smoke E2E S5
**Validación en tiempo real:** completada (Genome `/v1/genome/now/health` 2026-05-28T02:21:38Z, 401 confirmado en 4 endpoints `/v1/factory/*`)
**Cruza con:** T1-MAGNA-005 (D), T1-MAGNA-006 (D), T1-MAGNA-007 (C), DSC-G-008 v2, DSC-G-017, DSC-G-019, AGENTS.md Reglas Duras #1–#6, Sprint 91.16
