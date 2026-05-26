# Inventario del Proyecto `monstruo-quantum-realm` v0.8

**De:** hilo Manus operador del proyecto `monstruo-quantum-realm` (dominio `monstrrealm-ntoi5bex.manus.space`).
**Para:** hilo Manus operador del proyecto `tablero-campana` (dominio `monstruo-fmpgkidx.manus.space`).
**Propósito:** entregar un inventario binario, verificado contra los archivos reales del repo, de todo lo que existe en este proyecto para que decidas qué portar al tuyo.
**Verificado en sandbox al:** 23 may 2026.
**Sin código todavía, solo inventario, propósito y deuda.**

---

## 1) Inventario de componentes

### `client/src/pages/`

| Archivo | LOC | Propósito | ¿Reutilizable? |
|---|---|---|---|
| `Home.tsx` | 315 | Página única que orquesta TODO: carga `genome_visual_data.json`, carga `catastro_visual_data.json`, mantiene estados `selectedNode`, `selectedCandidata`, `hoveredCandidata`, `isCatastroOpen`, `studioOpen`, `generatedAssets`, monta `<QuantumRealm>` + `<StatsHUD>` + inspectores + `<NanoBananaStudio>`. Toda la mecánica de la app vive aquí. | **Lógica** sí; el layout específico no, porque tu Tablero usa otra grilla. Útil mirarlo como referencia de cómo conviven 5-6 estados de selección sin enredarse. |
| `ComponentShowcase.tsx` | 1.685 | Página template de shadcn que vino con el scaffold. Nunca se usó. | No — descartar. |
| `NotFound.tsx` | 38 | 404 default del template. | Trivial. |

### `client/src/components/` (top-level, sin `ui/`)

| Archivo | Propósito | ¿Reutilizable? |
|---|---|---|
| `ErrorBoundary.tsx` | Boundary mínimo que captura los crashes del `<Canvas>` y muestra un fallback monocromático "Fallo crítico" sin tirar toda la pestaña. | Sí — útil envolver tu Tablero. |
| `ManusDialog.tsx` | Modal genérico del template (no usado en producción). | No. |
| `AIChatBox.tsx`, `DashboardLayout.tsx`, `DashboardLayoutSkeleton.tsx`, `Map.tsx` | Componentes pre-built del template Manus, no usados por este proyecto. | No (los tendrás idénticos en tu template). |

### `client/src/components/quantum/` — el corazón del proyecto

| Archivo | Propósito | Reutilización |
|---|---|---|
| `QuantumRealm.tsx` (281 LOC) | Componente raíz 3D. Monta `<Canvas>` de R3F con `<OrbitControls>` + `<Stars>` + `<ContactShadows>` + `<AdaptiveDpr>` + `<AdaptiveEvents>` + `<PerformanceMonitor>` + postprocessing (`<Bloom>` con `KernelSize.LARGE`, `<Vignette>`, `<ChromaticAberration>`). Adentro: `<Core>`, `<ZoneRings>`, todos los `<Node3D>` con sus posiciones calculadas, `<Connections>`, `<CatastroCluster>` con detector de proximidad de cámara (`CatastroProximityWatch`), `<CatastroPortalHalo>`, `<MaterializedAssetsOrbit>`. | **Contenido específico** (sistema solar concéntrico). Lo que sí vale portar: el patrón de **detector de cercanía de cámara** que emite eventos cuando la cámara entra a un nodo + el patrón de **halo portal** alrededor de un nodo "puerta". |
| `Node3D.tsx` (115 LOC) | Renderiza un nodo del genoma. **Geometría derivada del tipo + faces del AST** (sphere/icosahedron/octahedron/torus/box/tetrahedron/dodecahedron/organic), escala = `visual_scale`, color = blanco/gris/azul-tenue/casi-negro según estado, opacidad = `node.opacidad`, glow blanco para activos, wireframe para futuros. Animación: pulsado por `pulseSpeed` derivado de `peso`, rotación lenta proporcional a peso, movimiento orgánico irregular si `tipo='organic'`. | **Reutilizable**. El mapeo "geometría = ADN del código" es del autor original y tiene valor — los embriones se ven distintos porque su tipo es `organic`, los almacenes son `sphere`, los orquestadores son `icosahedron`. |
| `Core.tsx` (~70 LOC) | Núcleo central blanco brillante con dos anillos contra-rotantes. Pulsado de respiración + `pointLight` para que ilumine los nodos circundantes. | Reutilizable si quieres tener un "centro" en el Tablero. |
| `ZoneRings.tsx` (21 LOC) | Anillos circulares horizontales en cada radio de zona — guía visual del territorio. | Trivial, fácil portar o descartar. |
| `Connections.tsx` (76 LOC) | Renderiza líneas tenues entre nodos cuyo `node.conexiones[]` apunta a otro nodo presente. Opacidad 0.25 si ambos activos, 0.08 si alguno degradado. | **Útil** si tu Tablero quiere mostrar las conexiones reales del genoma; el patrón de `Map<string, [x,y,z]>` para reusar posiciones es eficiente. |
| `CatastroCluster.tsx` (272 LOC) | **Joya central.** Sub-mundo que se materializa solo cuando la cámara está cerca del nodo `catastro`. Fade in/out con `scale.setScalar(0.3 + fadeIn * 0.7)`, 7 familias distribuidas radialmente con `Billboard` + `Text` de drei (sin TTF, fuente de R3F), conector tenue familia→centro, candidatas como mini-meshes por tier (opacidad 1.0/0.75/0.35 para trono/candidato/en-evaluación), marcador especial de doble anillo + label "○ OPERABLE · TOCA PARA INVOCAR" para candidatas con `operable=true`. | **Altamente portable**. Aunque tu Tablero no use sistema solar, **el patrón "zoom-revelación" con `<Billboard>` de drei** y el doble anillo de operable es transferible a cualquier visualización 3D. |
| `MaterializedAssetsOrbit.tsx` (124 LOC) | Renderiza los assets generados por Nano Banana Pro como esferas PBR con la imagen del asset como textura, orbitando el nodo catastro con `autoRotate`. Usa `useTexture` de drei + `MeshPhysicalMaterial` con `clearcoat`. Click → reabre Studio en modo edit. | **Patrón portable**: "asset generado por IA se materializa como objeto orbitando su nodo de origen". Si en tu Tablero Nano Banana Pro vive en distrito Capacidades, sus assets pueden orbitarlo. |
| `NanoBananaStudio.tsx` (270 LOC) | Modal flotante (no usa `<Canvas>`, es HTML normal) para operar Gemini Nano Banana Pro vía `trpc.gemini.nanoBananaGenerate`. Prompt textarea + selector `top`/`fast` + botón generar + preview del último asset + botón descargar. Modo edit cuando recibe `seedAsset` (los textos cambian a "Aplicar edición" en vez de "Materializar"). | **Reutilizable casi 1:1**. Si tu Tablero quiere permitir "operar" candidatas directamente desde el HUD, este modal ya está hecho y conectado al backend real. |
| `StatsHUD.tsx` (100 LOC) | HUD esquina superior-izquierda. Calcula `salud = activos/total * 100` con threshold de color (blanco >70, amarillo 40-70, rojo <40). Muestra: salud, componentes, activos, degradados, futuros, líneas de código, peso total. Glass-morphism con `bg-black/40 backdrop-blur-md`. | Patrón visual sí, pero tu Tablero ya tiene Live Pulse panel propio. Si quieres unificar HUDs, el patrón de `<Row>` aquí es limpio. |
| `InspectorPanel.tsx` (~150 LOC) | Panel lateral derecho que muestra detalle del nodo seleccionado (path, LOC, archivos, funciones, tests, zona, peso). | Si tu Tablero no tiene aún panel de inspector, esto es un esqueleto ya hecho. |
| `CandidataInspector.tsx` (~200 LOC) | Panel lateral para detalle de candidata del catastro (familia, tier, diferenciador, arquitectura, lecciones, biblia_size, fuente). Si `operable=true`, muestra CTA "Operar" que abre el Studio. | Reutilizable si tu Tablero quiere catalogar IAs del catastro. |

---

## 2) Inventario de datos

### Archivos de datos en `client/public/`

| Archivo | Tamaño | Generado por | Sincronizado con genoma real |
|---|---|---|---|
| `genome_visual_data.json` | 70 KB | **`scripts/generate_visual_data.py`** del repo `el-monstruo` (commit `d5f0a41`, PR #198). Lee `MONSTRUO_GENOME.yaml` + AST de `kernel/`, `embriones/`, `scripts/`, `tools/`, `apps/` reales. | **Sí, pero estático.** Es snapshot del 22 may 2026. No hay regeneración automática — Alfredo corre el script manualmente, copia el JSON al `public/`, hace checkpoint, redeploya. |
| `catastro_visual_data.json` | 89 KB | Mismo script `scripts/generate_visual_data.py`. Lee `kernel/catastro/data/catastro_agentes.json` + `kernel/catastro/data/catastro_tools.json` + `docs/biblias_v73/`. | Sí, snapshot del 22 may 2026. |
| `genome_data.json` | 70 KB | Duplicado de `genome_visual_data.json` (residuo de iteración anterior). | **Descartar.** |

### Composición real del `genome_visual_data.json`

```
meta:
  total_nodes: 120
  total_zones: 7
  heaviest: "scripts" (peso 34655)

Distribución por zona:
  Z1 (CEREBRO):       101 nodos  ← prácticamente todo el repo cae aquí
  Z2 (MEMORIA):         4 nodos  (catastro, memory, lightrag, mem0)
  Z3 (AUTONOMIA):       2 nodos  (scripts, embriones)
  Z4 (INTELIGENCIA):    4 nodos
  Z5 (INTERFACES):      2 nodos  (app_la-forja, app_mobile)
  Z6 (SEGURIDAD):       4 nodos
  Z8 (SATELITES):       3 nodos
  Z7 (CONOCIMIENTO):    0 nodos  ← declarada en ZONES_CONFIG pero vacía en data

Distribución por estado:
  ACTIVO:    119
  ASPIRANTE:   1  ← no documentado en TS types (deuda)
```

### Composición real del `catastro_visual_data.json`

```
total_candidatas: 120
total_familias: 7
host_node_id: "catastro"

Familias:
  F1 MODELOS LLM:         20
  F2 AGENTES CODING:      17
  F3 AGENTES AUTÓNOMOS:   30
  F4 BROWSER/COMPUTER:    10
  F5 ORQUESTACIÓN/SWARM:  13
  F6 RESEARCH/RAG:        15
  F7 GENERATIVOS:         15

Tiers:
  Tier 1 TRONO:          17
  Tier 2 CANDIDATO:      28
  Tier 3 EN EVALUACIÓN:  75

Operables: 1
  - "Nano Banana Pro" (familia F7) via "trpc.gemini.nanoBananaGenerate"
```

---

## 3) Conexiones reales en backend

**Sí, el proyecto tiene backend tRPC con conexiones a tres servicios reales.**

| Servicio | Router | Procedimientos | Frecuencia |
|---|---|---|---|
| **Gemini API** (`gemini-3-pro-image-preview` para imágenes, `gemini-2.5-pro-preview` para razonamiento) | `server/routers/gemini.ts` (217 LOC) | `catalog`, `ask`, `nanoBananaGenerate` (con soporte de `seedImageUrl` para edición multimodal). Imagen generada se guarda en Storage del Monstruo (`storagePut`) y se devuelve URL `/manus-storage/<key>`. | Bajo demanda (cuando el usuario operar Nano Banana). |
| **Supabase del Monstruo** (`xsumzuhwmivjgftsneov`, key `sb_secret_*` rotada en SECURITY-002) | `server/routers/supabase.ts` (233 LOC) | `health`, `listTables` (introspección del OpenAPI swagger de PostgREST → devuelve **182 tablas reales** agrupadas por familia: catastro 16, lightrag 14, v5 12, embrion 11, forja 9, etc.), `countRows`, `previewTable`, `exportTableJson`. | Bajo demanda (toda `protectedProcedure`). |
| **Storage Manus** | `server/storage.ts` (helpers `storagePut`/`storageGet`). | Guarda imágenes de Nano Banana, devuelve `/manus-storage/<key>`. | Bajo demanda. |

**No hay conexión actual al kernel Railway**. El `genome_visual_data.json` viene de generación batch, no en vivo. El HUD muestra "Salud: X%" basado en el snapshot estático, no en `/health` del kernel.

---

## 4) Funcionalidades únicas (lo que tu Tablero v2 probablemente NO tiene)

1. **Catastro de 120 IAs candidatas con zoom-revelación.** Al acercar la cámara al nodo `catastro` (Z2), se materializa un sub-mundo con las 120 IAs organizadas en 7 familias radiales × 3 tiers, con sus 17 tronos brillando opacidad 1.0 y los 75 "en evaluación" apenas visibles a opacidad 0.35. Cuando te alejas, todo desaparece. Doctrina: "un sub-mundo dentro de un nodo del mundo".
2. **Nano Banana Pro como única candidata operable.** Esta candidata tiene `operable=true` y `operable_via='trpc.gemini.nanoBananaGenerate'`. Doble anillo visual con label "○ OPERABLE · TOCA PARA INVOCAR". Al hacer click → abre `<NanoBananaStudio>`, modal flotante conectado a Gemini real. Usuario escribe prompt, genera imagen, se guarda en Storage, **se materializa orbitando el catastro como esfera PBR con la imagen como textura**.
3. **Edit en cadena de assets.** Click en un asset orbital → reabre Studio en modo edit con `seedImageUrl` poblado. Gemini hace edición multimodal (recibe la imagen base64 + el prompt). El asset editado se guarda como uno nuevo (no reemplaza el original) y también orbita.
4. **Pastilla "Nano Banana Pro · Operable · toca" persistente en HUD inferior izquierdo.** Decisión post-IMG_5251: el zoom era indiscoverable en iPhone, así que se agregó acceso directo siempre visible.
5. **Detector de proximidad de cámara** (`CatastroProximityWatch`) que dispara `onChange(open)` cuando la cámara entra/sale de un radio configurable. Patrón reutilizable.
6. **Login persistente con Manus OAuth** habilitado (`web-db-user`). Sin login → solo visualización. Con login → desbloquea operar Nano Banana y consultar Supabase. `useAuth()` con `getLoginUrl()`.
7. **Botón descargar al iPhone.** El asset generado tiene botón descargar que en Safari iPhone abre el share sheet → "Save to Photos" / "Save to Files".
8. **Geometría derivada del AST** real del código (faces, complexity, irregularity).

---

## 5) Bugs conocidos y deuda técnica que NO debes portar

| # | Deuda | Severidad |
|---|---|---|
| 1 | **Falta `"use no memo"`** al inicio de los archivos que usan `useFrame`. El template de Manus tiene React Compiler activo, y eso rompe `useFrame` en producción (warmup + bucle). Hoy funciona por casualidad. | Alta — bloqueador si activas React Compiler en tu Tablero. |
| 2 | **Z7 CONOCIMIENTO declarada en `ZONES_CONFIG` pero data tiene 0 nodos en Z7.** El renderer dibuja el anillo de Z7 sin nada dentro. | Media — visual. |
| 3 | **101 de los 120 nodos están en Z1** porque el clasificador `generate_visual_data.py` cae a Z1 por default cuando no hay regla de mapeo explícita. Visualmente el centro queda sobre-poblado y las otras zonas vacías. | Alta — afecta legibilidad. Si portas datos, regenera mapeo. |
| 4 | **Estado `ASPIRANTE` aparece en data pero NO está en el type `EstadoEjecucion`** (`activo`/`degradado`/`futuro`/`descartado`). `normalizeEstado()` lo trata como `activo` por default. | Media — silenciosa, pero pierde información. |
| 5 | **`genome_data.json` duplica `genome_visual_data.json`.** Residuo. | Trivial — borrar. |
| 6 | **`ComponentShowcase.tsx` (58 KB)** sigue en el bundle aunque la ruta no se usa. Bloat de ~30 KB minificado. | Baja. |
| 7 | **Sin tests E2E ni a11y**. Solo hay 3 vitest server-side (auth, gemini, supabase, catastro-nano-banana). | Media. |
| 8 | **El HUD muestra "Salud 99%" hardcoded** (calculado del snapshot estático). No es en vivo del kernel. | Alta de honestidad. En tu Tablero v2 el "Live Pulse" debe ser realmente live. |
| 9 | **`<EffectComposer>` con `<Bloom>` + `<ChromaticAberration>`** pesa ~250 KB en bundle. En iPad de 67 años de papá de Alfredo, baja a 30fps. | Media — considera bajar postprocessing. |
| 10 | **`scripts/generate_visual_data.py` es batch manual**. No hay CI ni cron que lo regenere. Snapshot envejece. | Media de proceso. |

---

## 6) Joyas escondidas

1. **`server/routers/supabase.ts` con introspección del OpenAPI de PostgREST.** En vez de mantener una lista manual de las 182 tablas, hace fetch a `/rest/v1/?accept=application/openapi+json` y parsea las paths. Detecta automáticamente la familia por prefijo (`catastro_*`, `lightrag_*`, `v5_*`, etc.) y agrupa. **Si tu Tablero quiere visualizar las tablas de Supabase como nodos vivos**, este router te las da gratis. Procedimientos: `health`, `listTables`, `countRows` (batch con `head:true` para ser barato), `previewTable`, `exportTableJson`.
2. **`server/routers/gemini.ts` con `fetchSeedImageBytes()`** que resuelve URLs `/manus-storage/<key>` vía presign de Forge, descarga la imagen, la convierte a base64 y la pasa como `inlineData` a Gemini en formato multimodal correcto. **Es el pegamento que hace edit en cadena posible**. Si tu Tablero quiere operar IAs generativas, este patrón es directamente portable.
3. **Paleta monocromática estricta** documentada en `genome-utils.ts` (`getNodeColor`, `getNodeEmissive`): blanco puro = activo, gris medio = degradado, azul-gris tenue = futuro, casi negro = descartado. **El color queda reservado SOLO para alarmas/estados**, no para diferenciar zonas — la diferenciación se lee por geometría, tamaño y posición. Doctrina Tesla/Apple, escrita en comentarios y respetada.
4. **`getPulseSpeed(node)` proporcional a `peso/10000`**. Los nodos pesados pulsan más rápido = "están más vivos". Pequeño detalle de gameplay que hace que el sistema solar tenga arritmia propia.
5. **`scripts/generate_visual_data.py` ya conoce el AST**. `geometria.faces`, `geometria.irregularity`, `geometria.is_cluster`, `geometria.cluster_count`, `geometria.elongation` se calculan desde el AST real con `ast.parse()`. Si tu Tablero quiere mantener esta dimensión, **ejecuta el mismo script** y consume el mismo JSON — el formato ya está estable v2.0.
6. **Configuración del catastro con `angulo` por familia.** En `catastro-types.ts`, cada familia tiene un campo `angulo` (en grados) que distribuye las 7 familias radialmente. Si quieres que las "familias de IA" tengan una orientación cardinal estable (norte = LLM, este = Coding, sur = Autónomos, etc.), el mapeo está hecho.
7. **`TIER_LABELS` y `TIER_OPACITY` con los 3 tiers (TRONO/CANDIDATO/EN EVALUACIÓN) y sus opacidades canónicas (1.0/0.75/0.35).** Útil si tu Tablero quiere mostrar candidatas con jerarquía visual.
8. **`AdaptiveDpr` + `AdaptiveEvents` + `PerformanceMonitor`** ya integrados — degradan automáticamente la resolución si los frames caen abajo de 30fps. Te ahorras esa pelea.
9. **Doctrina del "click stopPropagation"** en cada nodo y candidata, para que clicks en sub-objetos no propaguen al `<OrbitControls>` y rompan el navegado.
10. **`<ErrorBoundary>` envolviendo todo.** Si el Canvas crashea (caso real: el preset `night` de `<Environment>` fallaba descargando HDR de CDN externo), no tira la pestaña — muestra "Fallo crítico" en monocromático.

---

## 7) Mapa del genoma a las zonas

**Mapeo derivado, NO manual.** El script `scripts/generate_visual_data.py` decide la zona Z1–Z8 por reglas sobre el `path` y el `id` del componente. Reglas detectadas leyendo el script:

```
Z1 CEREBRO       → todo lo que no matchea ninguna otra regla
                   (default, por eso 101/120 caen aquí)
Z2 MEMORIA       → paths que contienen: memory, catastro, lightrag, mem0
Z3 AUTONOMIA    → paths que contienen: embriones, scripts (loop perpetuo, cron)
Z4 INTELIGENCIA  → paths que contienen: sabios, llm, reasoning
Z5 INTERFACES    → paths que contienen: apps/la-forja, apps/mobile, command_center, bot
Z6 SEGURIDAD     → paths que contienen: security, policy, audit, guardian
Z7 CONOCIMIENTO  → paths que contienen: skills, biblias, docs (DECLARADO PERO 0 NODOS)
Z8 SATELITES     → repos externos del ecosistema (like-kukulkan-tickets, etc.)
```

**ZONES_CONFIG en `genome-types.ts`** define el `radius` de cada zona (centro Z1 → órbita 24 en Z8):

| Zona | Radius | Altura |
|---|---|---|
| Z1 CEREBRO | 0 | 0 |
| Z2 MEMORIA | 4 | 0 |
| Z3 AUTONOMIA | 7 | 0.5 |
| Z4 INTELIGENCIA | 10 | -0.5 |
| Z5 INTERFACES | 13 | 0 |
| Z6 SEGURIDAD | 16 | 1 |
| Z7 CONOCIMIENTO | 19 | -1 |
| Z8 SATELITES | 24 | 0 |

**Para tu Tablero v2:** este mapeo Z1–Z8 está hecho para sistema solar concéntrico. Tu Tablero usa 5 distritos isométricos (Cognición/Interfaces/Infra/Capacidades/Futuro). El **mapeo entre los dos esquemas** no existe — alguien tiene que diseñarlo. Sugerencia binaria:

| Tu distrito v2 | Zonas v0.8 que se mapean |
|---|---|
| Cognición | Z1 (CEREBRO) + Z4 (INTELIGENCIA) |
| Interfaces | Z5 (INTERFACES) |
| Infraestructura | Z6 (SEGURIDAD) + parte de Z3 (scripts) |
| Capacidades | Z2 (MEMORIA) + Z7 (CONOCIMIENTO) |
| Futuro | nodos con `estado='futuro'` independiente de su zona |
| (sin distrito) | Z8 SATELITES → tu inventario de satélites (PR #197) los maneja aparte |

---

## Recomendación binaria

| Portar | Veredicto |
|---|---|
| `CatastroCluster` con zoom-revelación | **Sí** — es la mejor pieza del proyecto, transferible a tu Tablero. |
| `NanoBananaStudio` + edit en cadena | **Sí** — único modal operable de IA generativa, conectado a Gemini real. |
| `MaterializedAssetsOrbit` | **Sí** — patrón "asset generado orbita su nodo origen" es valioso. |
| Router `supabase.ts` con introspección | **Sí** — 182 tablas con `listTables`/`countRows`/`previewTable` ya está hecho. |
| Router `gemini.ts` con `fetchSeedImageBytes` | **Sí** — pegamento multimodal. |
| Paleta monocromática estricta de `genome-utils.ts` | **No** — tu Tablero tiene Forja Industrial. Mantén tu paleta. |
| `Node3D` con geometría por AST | **Discutir** — si tu Tablero usa cubos isométricos uniformes, esto no aplica. Si quieres mantener diferenciación geométrica del genoma, sí. |
| `Connections` con líneas tenues | **Sí** — para mostrar conexiones reales del genoma sin sobrecargar visual. |
| `genome_visual_data.json` y `catastro_visual_data.json` | **Regenerar.** Usa `scripts/generate_visual_data.py` con `--output-dir` apuntando a tu proyecto. NO copies los snapshots de hoy. |
| `Home.tsx`, `App.tsx`, layout | **No** — tu Tablero tiene su propio shell. |
| `ComponentShowcase`, `genome_data.json` duplicado, postprocessing pesado | **No** — son deuda. |
| `<ErrorBoundary>` | **Sí** — siempre. |

---

**Fin del inventario.** Si necesitas que entre a algún archivo en detalle (por ejemplo, los 217 LOC completos de `gemini.ts` o los 272 de `CatastroCluster.tsx`), responde y los entrego.
