# Archivos a portar de `monstruo-quantum-realm` v0.8 → `tablero-campana` v2

**Origen (proyecto descontinuado):** `monstruo-quantum-realm`, sandbox `monstrrealm-ntoi5bex.manus.space`.
**Destino:** `tablero-campana`, sandbox `monstruo-fmpgkidx.manus.space`.
**Generado por:** hilo Manus operador del v0.8, 23 may 2026.
**Premisa:** copia quirúrgica de las joyas reutilizables, sin arrastrar deuda. Cada archivo lleva su árbol de dependencias resuelto.

---

## Cómo leer este documento

Para cada bloque de archivos a portar listo:

1. **Paths exactos** de origen y destino.
2. **Tamaño** (LOC y bytes) para que el receptor estime impacto.
3. **Dependencias internas** que también hay que copiar para que compile (efecto cascada).
4. **Dependencias externas** (paquetes npm) que el destino debe tener instaladas.
5. **Variables de entorno** que el destino necesita.
6. **Modificaciones esperadas** (lo que el receptor tendrá que adaptar a su esquema de distritos v2).

Todo lo que no está en este documento se descarta intencionalmente.

---

## Bloque 1 — Catastro con zoom-revelación

La pieza más valiosa del proyecto v0.8. Un sub-mundo que se materializa cuando la cámara se acerca al nodo `catastro`, con 120 IAs candidatas distribuidas en 7 familias × 3 tiers.

### Archivos

| Origen | Destino | LOC | Bytes |
|---|---|---:|---:|
| `client/src/components/quantum/CatastroCluster.tsx` | `client/src/components/quantum/CatastroCluster.tsx` | 335 | 10 709 |
| `client/src/components/quantum/CandidataInspector.tsx` | `client/src/components/quantum/CandidataInspector.tsx` | 176 | 6 553 |
| `client/src/lib/catastro-types.ts` | `client/src/lib/catastro-types.ts` | 82 | 2 183 |
| `client/public/catastro_visual_data.json` | **NO PORTAR** — regenerar con `scripts/generate_visual_data.py` del repo `el-monstruo` | — | — |

### Dependencias internas que arrastran

Ninguna fuera de las tres anteriores. `CatastroCluster` solo importa `@react-three/fiber`, `@react-three/drei` (para `<Text>` y `<Billboard>`), `three` y `catastro-types`. `CandidataInspector` solo importa `lucide-react` y `catastro-types`.

### Dependencias npm requeridas

```json
"@react-three/drei": "^10.7.7",
"@react-three/fiber": "^9.6.1",
"three": "^0.184.0",
"@types/three": "^0.184.1",
"lucide-react": "^0.453.0"
```

El template Manus que tu proyecto tiene **NO incluye** `@react-three/*` ni `three` por defecto. Hay que `pnpm add`.

### Variables de entorno

Ninguna. Es 100 % cliente.

### Modificaciones esperadas en destino

1. **Reemplazar la distribución radial por la grilla isométrica de tu Tablero.** El v0.8 distribuye las 7 familias en un círculo con `angulo` por familia (ver `catastro-types.ts`, campo `angulo: 0|51|102|153|204|255|306`). Tu Tablero puede mantener el `Billboard` + `Text` y solo cambiar las posiciones.
2. **Re-evaluar el detector de proximidad de cámara.** El v0.8 usa `CatastroProximityWatch` que dispara `onChange(open)` cuando la cámara entra a radio configurable del nodo `catastro`. Si tu Tablero es isométrico sin zoom libre, esta mecánica no aplica — tendrás que sustituirla por click en el distrito de Capacidades (o donde decidas que vive el catastro).
3. **Ajustar paleta.** El v0.8 usa monocromático estricto. Tu Tablero usa Forja Industrial (naranja sobre grafito). Reemplazar valores `'#FFFFFF'`, `'#808080'` en `getNodeColor` por tu paleta.

---

## Bloque 2 — Nano Banana Studio operable

Modal flotante para invocar Gemini Nano Banana Pro (generación + edición multimodal de imágenes), conectado a backend tRPC. Es **la única candidata operable del catastro** y el patrón que vale 1:1.

### Archivos cliente

| Origen | Destino | LOC | Bytes |
|---|---|---:|---:|
| `client/src/components/quantum/NanoBananaStudio.tsx` | `client/src/components/quantum/NanoBananaStudio.tsx` | 253 | 9 702 |
| `client/src/components/quantum/MaterializedAssetsOrbit.tsx` | `client/src/components/quantum/MaterializedAssetsOrbit.tsx` | 164 | 5 085 |

### Archivos servidor

| Origen | Destino | LOC | Bytes |
|---|---|---:|---:|
| `server/routers/gemini.ts` | `server/routers/gemini.ts` | 217 | 6 896 |
| `server/_core/gemini.ts` | `server/_core/gemini.ts` | 56 | 1 487 |
| `server/_core/models.ts` | `server/_core/models.ts` | 21 | 908 |
| `server/routers/gemini.test.ts` | `server/routers/gemini.test.ts` | 129 | 4 667 |

### Dependencias internas que arrastran

- `NanoBananaStudio.tsx` importa `@/lib/trpc` (que tu proyecto **ya tiene**, viene en el template Manus).
- `MaterializedAssetsOrbit.tsx` reexporta el tipo `GeneratedAsset` de `NanoBananaStudio` — son una pareja inseparable.
- `gemini.ts` (router) importa `server/storage.ts` para `storagePut`. **El template Manus ya trae `server/storage.ts`** — verificar que no la hayas modificado y, si lo hiciste, ajustar.
- `gemini.ts` (router) importa `server/_core/trpc.ts` para `protectedProcedure` y `router`. **El template ya lo trae.**

### Dependencias npm requeridas

```json
"@google/genai": "^2.6.0",
"@react-three/drei": "^10.7.7",
"@react-three/fiber": "^9.6.1",
"three": "^0.184.0",
"lucide-react": "^0.453.0"
```

### Variables de entorno

```bash
GEMINI_API_KEY=<tu_key_de_google_ai_studio>
```

En el proyecto v0.8 está como `GEMINI_API_KEY` plain en `env.ts`. En tu Tablero, agregarla vía `webdev_request_secrets`.

### Registrar en `appRouter`

En `server/routers.ts` (el agregador raíz):

```ts
import { geminiRouter } from "./routers/gemini";

export const appRouter = router({
  // ... otros routers
  gemini: geminiRouter,
});
```

### Procedimientos que expone `geminiRouter`

| Procedimiento | Auth | Propósito |
|---|---|---|
| `gemini.catalog` | protected | Devuelve la lista de modelos vigentes (constante `GEMINI_MODELS`) para que el front sepa qué tier ofrecer. |
| `gemini.ask` | protected | Razonamiento de texto contra `REASONING_TOP` o `REASONING_FAST`. |
| `gemini.nanoBananaGenerate` | protected | Genera o edita imagen vía Nano Banana Pro / 3.1 Flash. Recibe `prompt`, `tier` (`top` o `fast`), y opcional `seedImageUrl` (para edición multimodal). Guarda la imagen en Storage y devuelve `{url, key, mimeType}`. |

### Modelos Gemini vigentes (catálogo del v0.8)

```ts
REASONING_TOP:   "gemini-3.1-pro-preview"
REASONING_FAST:  "gemini-3.5-flash"
HEALTHCHECK:     "gemini-3.5-flash"
IMAGE_TOP:       "gemini-3-pro-image-preview"     // Nano Banana Pro
IMAGE_FAST:      "gemini-3.1-flash-image-preview" // Nano Banana 3.1 Flash
```

> **Verificar vigencia al momento de portar.** El comentario en `models.ts` dice "validado al 22/05/2026" — re-validar contra `https://generativelanguage.googleapis.com/v1beta/models` antes de mergear.

### Modificaciones esperadas en destino

1. **El asset orbital debe orbitar la pieza correcta de tu Tablero.** En el v0.8 orbita el nodo `catastro` (sistema solar). En tu Tablero v2, el natural sería que orbite el distrito de Capacidades, o el nodo específico de Nano Banana Pro dentro del catastro.
2. **El modal `NanoBananaStudio` no usa `<Canvas>`** — es HTML normal con `bg-black/80 backdrop-blur-2xl`. La estética de tu Forja Industrial puede aplicarse cambiando colores y tipografía sin tocar lógica.

### Dependencia DURA del runtime de Manus

**`fetchSeedImageBytes()` dentro de `gemini.ts` resuelve URLs `/manus-storage/<key>` vía presign interno del Forge API.** Esto NO funciona fuera del runtime de Manus.

| Escenario de despliegue | ¿Funciona? |
|---|---|
| Sitio servido por runtime Manus (manus.space) | Sí, sin modificación. |
| Vercel / Netlify / Cloudflare Pages / hosting propio | **NO funciona**. `/manus-storage/*` no existe ahí. La edición multimodal de Nano Banana se rompe silenciosamente — `fetchSeedImageBytes` devuelve null y el feature se cae. |

**Mitigación si en el futuro saca del runtime Manus:** convertir las URLs en absolutas usando el endpoint público del Forge API (`storageGetSignedUrl(key)` ya existe en `server/storage.ts`) y exponer URLs firmadas con TTL en lugar de las relativas `/manus-storage/<key>`. Cambio aislado a `gemini.ts` líneas ~115-145.

---

## Bloque 3 — Router de Supabase con introspección

Procedimientos tRPC para introspectar y leer las 182 tablas reales del Supabase del Monstruo (`xsumzuhwmivjgftsneov`). Útil si tu Tablero quiere mostrar tablas vivas como nodos con `count_rows` real.

### Archivos servidor

| Origen | Destino | LOC | Bytes |
|---|---|---:|---:|
| `server/routers/supabase.ts` | `server/routers/supabase.ts` | 233 | 6 890 |
| `server/_core/supabase.ts` | `server/_core/supabase.ts` | 72 | 2 203 |
| `server/routers/supabase.test.ts` | `server/routers/supabase.test.ts` | 53 | 1 934 |

### Dependencias npm requeridas

```json
"@supabase/supabase-js": "^2.106.1"
```

### Variables de entorno

```bash
SUPABASE_URL=https://xsumzuhwmivjgftsneov.supabase.co
SUPABASE_SERVICE_KEY=<sb_secret_*>
```

> **CRÍTICO — Naming canónico (DSC-S-007 firmado 10 may 2026).** El archivo del v0.8 usa el nombre legacy `SUPABASE_SERVICE_ROLE_KEY` en `server/_core/env.ts:11` y en `server/_core/supabase.ts:12`. El **nombre canónico actual** es `SUPABASE_SERVICE_KEY` (sin `_ROLE`). Al portar, **renombrar en ambos archivos** antes de mergear. Si copias 1:1, violas la doctrina canónica firmada y rompes la consistencia con el kernel y todos los demás proyectos del Monstruo.

> **Cuidado adicional.** La service key **bypasea RLS**. Toda invocación al router debe seguir siendo `protectedProcedure`. Nunca exponerla al frontend con prefijo `VITE_*`. La doctrina `DSC-S-002` aplica.

### Registrar en `appRouter`

```ts
import { supabaseRouter } from "./routers/supabase";

export const appRouter = router({
  // ...
  supabase: supabaseRouter,
});
```

### Procedimientos que expone `supabaseRouter`

| Procedimiento | Auth | Propósito |
|---|---|---|
| `supabase.health` | protected | Ping a `/rest/v1/` con la service key; devuelve `{ok, message}`. |
| `supabase.listTables` | protected | Lee el OpenAPI swagger de PostgREST y devuelve las 182 tablas agrupadas por familia (`catastro_*`, `lightrag_*`, `v5_*`, etc.). |
| `supabase.countRows` | protected | Cuenta filas de una tabla específica con `head:true` (barato, sin transferir datos). Acepta `tableName: string`. |
| `supabase.previewTable` | protected | Devuelve las primeras N filas (default 10). Acepta `tableName: string, limit?: number`. |
| `supabase.exportTableJson` | protected | Devuelve toda la tabla en JSON. **Cuidado con tablas grandes.** |

### Tablas del Catastro reales en Supabase (mapeo concreto)

De las 182 tablas que devuelve `listTables`, las **7 del prefijo `catastro_*`** son las relevantes si quieres visualizar el catastro de IAs como nodos vivos:

| Tabla | Origen (migración) | Propósito |
|---|---|---|
| `catastro_modelos` | `016_sprint86_catastro_schema.sql` | Modelos LLM y candidatas con embeddings vectoriales para similitud. |
| `catastro_historial` | `016_sprint86_catastro_schema.sql` | Histórico de transiciones de tier (en evaluación → candidato → trono). |
| `catastro_eventos` | `016_sprint86_catastro_schema.sql` | Log de eventos del catastro (votaciones, observaciones, decisiones). |
| `catastro_notas` | `016_sprint86_catastro_schema.sql` | Notas curatoriales de Alfredo y curadores sobre cada candidata. |
| `catastro_curadores` | `016_sprint86_catastro_schema.sql` | Tabla de curadores con permisos para votar. |
| `catastro_agentes` | `030_sprint88_catastro_agentes.sql` | Agentes IA específicos (distintos a modelos). |
| `catastro_vision_generativa` | `040_sprint88_3_vision_generativa.sql` | Catálogo específico de IAs de visión generativa (Nano Banana, etc.). |

### RPCs (funciones) del Catastro disponibles

| RPC | Migración | Para qué |
|---|---|---|
| `match_catastro_modelos(query_embedding, threshold, count)` | `016` | Búsqueda semántica vectorial sobre `catastro_modelos`. Útil si tu Tablero quiere buscador por similitud. |
| `catastro_apply_quorum_outcome(modelo_id, outcome)` | `018` y `019` | Aplica decisión de cuórum sobre una candidata (promueve a trono, degrada, descarta). |
| `catastro_recompute_trono(modelo_id)` | `019` | Recalcula el tier de una candidata específica basado en votos recientes. |
| `catastro_recompute_trono_all()` | `019` | Recalcula todos los tronos del catastro. **Caro** — solo cron nocturno. |
| `trg_catastro_set_updated_at()` | `016` | Trigger interno, no llamar directamente. |
| `trg_catastro_agentes_updated_at()` | `030` | Trigger interno, no llamar directamente. |

Las RPCs se invocan vía `supabase.rpc('nombre_rpc', { params })`. Para incluirlas en tu router tRPC, agregar procedimientos específicos (no están en el router del v0.8 todavía — son ampliación natural).

### Modificaciones esperadas en destino

Ninguna a nivel código. Solo decidir cómo visualizar las tablas en tu Tablero (¿mini-nodos dentro del distrito de Capacidades? ¿panel separado?).

---

## Bloque 4 — Primitivos 3D opcionales (decisión binaria)

Componentes 3D del v0.8 que tu Tablero v2 **puede o no querer**, dependiendo de si mantiene visualización 3D libre o ya tiene su propia geometría isométrica fija.

### Si tu Tablero v2 mantiene `<Canvas>` con OrbitControls

| Origen | Destino | LOC | Bytes | Sirve para |
|---|---|---:|---:|---|
| `client/src/components/quantum/Connections.tsx` | igual | 75 | 1 918 | Líneas tenues entre nodos cuyo `conexiones[]` apunta a otro nodo. Opacidad reactiva al estado de ambos extremos. |
| `client/src/components/quantum/ErrorBoundary.tsx` | `client/src/components/ErrorBoundary.tsx` | 62 | 1 688 | Captura crashes del Canvas y muestra fallback en HTML normal sin tirar la pestaña. |

### Si tu Tablero ya tiene su propia geometría y solo quiere referencia

Estos NO portarlos:

| Archivo | Razón |
|---|---|
| `Node3D.tsx` | Geometría derivada del tipo del componente (sphere/icosahedron/octahedron/etc.). Tu Tablero usa cubos isométricos uniformes — no aplica. |
| `Core.tsx` | Núcleo central blanco con dos anillos contra-rotantes. Estética sistema solar, no Tablero. |
| `ZoneRings.tsx` | Anillos horizontales concéntricos por zona. Estética sistema solar. |
| `QuantumRealm.tsx` | El root 3D del v0.8 con OrbitControls, Stars, postprocessing. Tu Tablero tiene su propio root. |
| `StatsHUD.tsx` | HUD esquina superior. Tu Tablero ya tiene Live Pulse panel. |
| `InspectorPanel.tsx` | Panel detalle del nodo genoma. Tu Tablero puede tener su propio diseño. |

### Dependencias npm si decides portar `Connections.tsx`

Solo `three` y `@react-three/fiber` (que ya están si portaste el Bloque 1 o 2).

---

## Bloque 5 — Datos del genoma (NO PORTAR archivos, regenerar)

| Archivo del v0.8 | Acción |
|---|---|
| `client/public/genome_visual_data.json` (70 KB, v2.0) | **NO copiar.** El script `scripts/generate_visual_data.py` del repo `el-monstruo` ya genera v3.0 con tu esquema de 5 distritos. Correr ese script con `--output-dir <tu_proyecto>/client/public`. |
| `client/public/catastro_visual_data.json` (89 KB) | **NO copiar.** Mismo script lo regenera. |
| `client/public/genome_data.json` (70 KB) | **NO copiar.** Es duplicado residual. |
| `client/src/lib/genome-types.ts` | **Portar SI** quieres reutilizar la `interface GenomeNode` y `interface GenomeData`. Pero **ZONES_CONFIG** que vive dentro de este archivo está en esquema Z1–Z8 (sistema solar) — sustituirla por tu config de 5 distritos isométricos. |
| `client/src/lib/genome-utils.ts` | **Portar SI** quieres reutilizar `calculateGenomeStats`, `getNodeColor`, `getNodeEmissive`, `getPulseSpeed`. Adaptar paleta a Forja Industrial. |
| `client/src/lib/genome-normalizer.ts` | **Portar SI** quieres reutilizar el normalizador que pone defaults en nodos con campos faltantes. Útil si la fuente del JSON puede tener variabilidad. |

---

## Resumen ejecutivo de la copia

### Total a portar si tomas todo lo recomendado

```
12 archivos cliente (.tsx + .ts)        →   1 962 LOC
 5 archivos servidor (.ts + .test.ts)   →     651 LOC
                                          ─────────
                                            2 613 LOC
```

### Dependencias npm a agregar

```bash
pnpm add @react-three/drei@^10.7.7 \
        @react-three/fiber@^9.6.1 \
        three@^0.184.0 \
        @google/genai@^2.6.0 \
        @supabase/supabase-js@^2.106.1

pnpm add -D @types/three@^0.184.1
```

### Variables de entorno a configurar (vía `webdev_request_secrets`)

```bash
GEMINI_API_KEY=<key_de_google_ai_studio>
SUPABASE_URL=https://xsumzuhwmivjgftsneov.supabase.co
SUPABASE_SERVICE_KEY=<sb_secret_*>     # <-- nombre canónico DSC-S-007, NO usar SUPABASE_SERVICE_ROLE_KEY
```

> **Recordatorio doctrinal.** El nombre `SUPABASE_SERVICE_ROLE_KEY` aparece en el archivo `server/_core/env.ts` del v0.8 y debe renombrarse a `SUPABASE_SERVICE_KEY` antes de mergear (DSC-S-007, firmado 10 may 2026).

### Registros en `server/routers.ts`

```ts
import { geminiRouter } from "./routers/gemini";
import { supabaseRouter } from "./routers/supabase";

export const appRouter = router({
  // ... routers existentes
  gemini: geminiRouter,
  supabase: supabaseRouter,
});
```

### Tests a correr después de portar

```bash
pnpm test server/routers/gemini.test.ts
pnpm test server/routers/supabase.test.ts
```

---

## Lo que explícitamente NO se porta

Quedan fuera porque no aplican al Tablero v2 o son deuda conocida:

| Archivo / cosa | Razón |
|---|---|
| `client/src/pages/Home.tsx` (315 LOC) | Es el orchestador del v0.8 (sistema solar). Tu Tablero tiene su propio Home. |
| `client/src/pages/ComponentShowcase.tsx` (1 685 LOC, 58 KB) | Template no usado. Bloat. |
| `client/public/genome_data.json` | Duplicado residual. |
| Postprocessing `<Bloom>` + `<ChromaticAberration>` (~250 KB en bundle) | En iPad antiguo baja a 30fps. Tu Forja Industrial puede usar menos efectos. |
| Paleta monocromática estricta de `genome-utils.ts` | Tu Tablero usa Forja Industrial (naranja sobre grafito). |
| Sistema solar concéntrico Z1–Z8 (`ZONES_CONFIG` en `genome-types.ts`) | Tu Tablero usa 5 distritos isométricos. Sustituir el `ZONES_CONFIG`. |
| El snapshot `genome_visual_data.json` v2.0 del v0.8 | El script ya genera v3.0 con tu esquema. |

---

## Una cosa que no es trivial

Cuando portes el Bloque 2 (Nano Banana), el patrón de **"asset generado por IA orbita el nodo de origen"** (`MaterializedAssetsOrbit`) asume movimiento orbital libre con `useFrame` y `autoRotate`. Si tu Tablero v2 es estrictamente isométrico estático, este patrón **rompe la metáfora visual** — el asset orbital flotando sobre cubos isométricos se ve raro. Dos caminos posibles:

- **(A)** Adaptar `MaterializedAssetsOrbit` a una "estela isométrica" — los assets aparecen como mini-cards dentro del distrito de Capacidades, alineadas al grid.
- **(B)** Mantener el orbital pero solo cuando el usuario hace zoom-in al distrito de Capacidades (modo focus).

Mi voto: **(A)** si el Tablero es 100% isométrico. **(B)** si tu Tablero permite zoom libre a sub-mundos.

Esta decisión la dejo al hilo receptor — no hay copia mecánica que la resuelva.

---

## Apéndice — Tres advertencias finales que el receptor debe leer antes de portar

### A1. Renombrado obligatorio: `SUPABASE_SERVICE_ROLE_KEY` → `SUPABASE_SERVICE_KEY`

Dos archivos del v0.8 hardcodean el nombre legacy y deben actualizarse al portar:

```diff
# server/_core/env.ts línea 11
- supabaseServiceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY ?? "",
+ supabaseServiceKey:     process.env.SUPABASE_SERVICE_KEY ?? "",

# server/_core/supabase.ts líneas 12, 17, 53, 54
- if (!ENV.supabaseUrl || !ENV.supabaseServiceRoleKey) { ... }
- _supabase = createClient(ENV.supabaseUrl, ENV.supabaseServiceRoleKey, { ... });
- apikey: ENV.supabaseServiceRoleKey!,
- Authorization: `Bearer ${ENV.supabaseServiceRoleKey!}`,
+ if (!ENV.supabaseUrl || !ENV.supabaseServiceKey) { ... }
+ _supabase = createClient(ENV.supabaseUrl, ENV.supabaseServiceKey, { ... });
+ apikey: ENV.supabaseServiceKey!,
+ Authorization: `Bearer ${ENV.supabaseServiceKey!}`,
```

Doctrina firmada: `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-007_naming_canonico_supabase_service_key.md`.

### A2. Schema del Catastro en Supabase: 7 tablas + 6 RPCs ya existen

No recrear nada. Las migraciones canónicas vigentes en el repo `el-monstruo` son:

- `scripts/016_sprint86_catastro_schema.sql` (tablas base + búsqueda vectorial)
- `scripts/018_sprint86_catastro_rpc.sql` (quórum)
- `scripts/019_sprint86_catastro_trono.sql` (recálculo de tronos)
- `scripts/030_sprint88_catastro_agentes.sql` (tabla de agentes)
- `scripts/040_sprint88_3_vision_generativa.sql` (visión generativa)

Tu Tablero hereda este schema en producción. Solo agregar router tRPC que lo consuma.

### A3. `/manus-storage/*` es dependencia dura del runtime de Manus

La edición multimodal de Nano Banana usa URLs relativas `/manus-storage/<key>` que solo resuelven dentro de manus.space. Si en algún futuro se considera despliegue externo (Vercel/Netlify/etc.), `fetchSeedImageBytes()` en `gemini.ts` debe convertirse a URLs absolutas firmadas vía `storageGetSignedUrl(key)`. No es bloqueador hoy, pero es deuda arquitectónica documentada.

---

**Fin del documento.** Si el hilo receptor necesita que entre en detalle a algún archivo (por ejemplo, los 217 LOC completos de `gemini.ts` o los 335 de `CatastroCluster.tsx` con explicación línea-por-línea), responde y los entrego.
