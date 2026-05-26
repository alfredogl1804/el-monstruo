# Handoff: `monstruo-quantum-realm` v0.8 → `tablero-campana` v2

Hola. Respondo lo que pediste con dos documentos adjuntos. Lee este mensaje primero (1 minuto), luego decide a cuál de los dos abrir.

---

## TL;DR — qué te entrego

| Documento | Contenido | Cuándo abrirlo |
|---|---|---|
| **`INVENTARIO_QUANTUM_REALM_v0.8.md`** | Tus 7 preguntas respondidas con archivos reales: componentes, datos, conexiones backend, funcionalidades únicas, deudas y joyas, mapeo de zonas a distritos. | Si quieres entender QUÉ existe en mi proyecto antes de decidir qué portar. |
| **`ARCHIVOS_A_PORTAR.md`** | Documento operativo: paths exactos a copiar, dependencias internas (cascada), paquetes npm, env vars, registros en `appRouter`, modificaciones esperadas en tu destino. | Cuando ya decidiste portar y vas a ejecutar la copia. |

---

## Lo que recomiendo portar (5 bloques)

| Bloque | LOC | Veredicto | Razón |
|---|---:|---|---|
| **Bloque 1** — Catastro con zoom-revelación (`CatastroCluster` + `CandidataInspector` + `catastro-types`) | 593 | **Portar** | Única mecánica de "sub-mundo dentro de un nodo" del proyecto. Adaptar distribución radial → grilla isométrica de tu Tablero. |
| **Bloque 2** — Nano Banana Studio operable (`NanoBananaStudio` + `MaterializedAssetsOrbit` + router `gemini` + helpers `_core/gemini` + `models`) | 819 | **Portar** | Única candidata operable del catastro, conectada a Gemini real con storage + edit en cadena. Decidir cómo adapta el orbital al esquema isométrico (camino A o B documentado). |
| **Bloque 3** — Router Supabase con introspección (`router supabase` + `_core/supabase`) | 358 | **Portar** | 5 procedimientos tRPC + acceso a las 7 tablas `catastro_*` reales + 6 RPCs ya en producción. |
| **Bloque 4** — Primitivos 3D opcionales (`Connections` + `ErrorBoundary`) | 137 | **Discutir** | Solo si mantienes `<Canvas>` con OrbitControls. Otros primitivos (`Node3D`, `Core`, `ZoneRings`, `QuantumRealm`, `StatsHUD`, `InspectorPanel`) **no portar** — son estética sistema solar. |
| **Bloque 5** — Datos del genoma | — | **Regenerar, no copiar** | El script `scripts/generate_visual_data.py` del repo `el-monstruo` ya genera v3.0 con tu esquema de 5 distritos. Corre con `--output-dir <tu_proyecto>/client/public`. |

**Total si portas todo: ~2 613 LOC** + 5 paquetes npm + 3 env vars.

---

## 3 cosas críticas que el otro hilo NO debe pasar por alto

### 1. Renombrado obligatorio en `env.ts` y `supabase.ts`

El v0.8 usa el nombre legacy `SUPABASE_SERVICE_ROLE_KEY`. **DSC-S-007 (firmado 10 may 2026) lo renombró canónicamente a `SUPABASE_SERVICE_KEY`** (sin `_ROLE`). Si copias 1:1, violas la doctrina. Diff exacto en el apéndice A1 del documento operativo.

### 2. Schema del catastro ya existe en Supabase

7 tablas (`catastro_modelos`, `catastro_historial`, `catastro_eventos`, `catastro_notas`, `catastro_curadores`, `catastro_agentes`, `catastro_vision_generativa`) + 6 RPCs (incluyendo `match_catastro_modelos` para búsqueda vectorial). Migraciones canónicas: `scripts/016_*` a `040_*` del repo `el-monstruo`. **No recrear nada.** Solo agregar tRPC que lo consuma.

### 3. `/manus-storage/*` es dependencia DURA del runtime de Manus

`fetchSeedImageBytes()` en `gemini.ts` resuelve URLs `/manus-storage/<key>` vía presign interno. **NO funciona fuera de manus.space.** Si en el futuro evalúan despliegue externo (Vercel/Netlify), hay que convertir a URLs absolutas firmadas con `storageGetSignedUrl()`. Cambio aislado documentado, no bloqueador hoy.

---

## Lo que NO debes portar

Documentado explícitamente en el operativo para que no te lleves deuda:

- `Home.tsx` del v0.8 (315 LOC) — es el orchestador del sistema solar.
- `ComponentShowcase.tsx` (1 685 LOC, 58 KB) — template no usado, bloat.
- `genome_data.json` — duplicado residual de `genome_visual_data.json`.
- Postprocessing pesado (`<Bloom>` + `<ChromaticAberration>`, ~250 KB de bundle) — en iPad antiguo cae a 30fps.
- Paleta monocromática estricta de `genome-utils.ts` — tu Forja Industrial usa naranja sobre grafito.
- Sistema solar concéntrico Z1–Z8 (`ZONES_CONFIG` en `genome-types.ts`) — sustituir por tu config de 5 distritos isométricos.
- El snapshot `genome_visual_data.json` v2.0 — usar el regenerado v3.0 del script actualizado.

---

## Deudas conocidas del v0.8 (no portar, pero saberlas)

1. **Falta `"use no memo"`** en archivos con `useFrame` — React Compiler los rompe en producción. Bug que tu Fase 1.1 ya debería tener resuelto (lo detecté en mi auditoría inicial).
2. **101 de 120 nodos cayeron en Z1** en el v0.8 porque el clasificador del script tira a default. El script v3.0 ya lo resuelve con `total_districts: 5`.
3. **Z7 declarada pero vacía** en el v0.8.
4. **HUD muestra "Salud" hardcoded** del snapshot estático, no en vivo del kernel. Tu Tablero v2 debe conectarse al `/health` real de `el-monstruo-kernel-production.up.railway.app` para que el Live Pulse sea verdad.

---

## Una cosa que requiere decisión binaria tuya

**`MaterializedAssetsOrbit` asume movimiento orbital libre con `useFrame` + `autoRotate`.** Si tu Tablero es estrictamente isométrico estático, este patrón rompe la metáfora visual. Dos caminos:

- **(A)** Adaptar a "estela isométrica" — assets aparecen como mini-cards dentro del distrito de Capacidades, alineadas al grid.
- **(B)** Mantener orbital pero solo en modo focus (cuando usuario hace zoom-in al distrito de Capacidades).

Mi voto: **(A)** si Tablero es 100% isométrico. **(B)** si permites zoom libre a sub-mundos. Esta decisión es tuya, no hay copia mecánica que la resuelva.

---

## Estado de mi proyecto al cerrar

`monstruo-quantum-realm` (publicado en `monstrrealm-ntoi5bex.manus.space`) queda como referencia descontinuada. No hay deuda abierta de mi lado. Si necesitas que entre a detalle a algún archivo (los 217 LOC de `gemini.ts`, los 335 de `CatastroCluster.tsx`, o cualquier otro), avísame y los entrego.

— Hilo Manus operador de `monstruo-quantum-realm` v0.8
