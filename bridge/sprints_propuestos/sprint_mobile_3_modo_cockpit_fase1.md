# Sprint Mobile 3 — Modo Cockpit fase 1

**Owner:** Hilo Ejecutor (Manus) Mobile
**Zona protegida:** `apps/mobile/lib/modes/cockpit/`
**ETA estimada:** 4-7h reales con Apéndice 1.3 factor velocity
**Bloqueos:** Sprint Mobile 2 cerrado verde
**Prerequisito:** Modo Daily funcional + 5 superficies con stubs

---

## 1. Contexto

Mobile 1+2 entregaron la cara del Monstruo Daily — minimalista, austera, hermosa. Ahora arranca el **Cockpit** — el panel denso del arquitecto. Bloomberg + Linear + Cursor + Manus, pero hermoso.

Mobile 3 implementa **5 de las 12-15 superficies del Cockpit**: las que constituyen el "operations center" día a día de Alfredo.

---

## 2. Objetivo único del sprint

Implementar 5 superficies primarias del Modo Cockpit con stubs realistas:

1. **MOC Dashboard** (ya placeholder en Mobile 1, ahora completo)
2. **Threads denso** (versión arquitecto del Threads del Daily)
3. **Catastro** (vista de los 50+ modelos LLM rankeados — DSC-G-007)
4. **Embriones** (9+ Embriones especializados con FCS)
5. **Guardian** (los 15 Objetivos como panel de instrumentos)

Más atajos magna estilo Linear funcionales: ⌘K, ⌘P, ⌘E, ⌘G, ⌘T, ⌘shift+M.

---

## 3. Bloques del sprint

### 3.A — MOC Dashboard completo

**3.A.1 — Vista densa con métricas vivas (stub)**

`MOCDashboardScreen` extendido del placeholder de Mobile 1:

- Grid de 12-15 cards de métrica (no 4-6 como el placeholder):
  - Sprints corriendo (con sub-status por sprint)
  - Hilos Manus activos (Catastro / Ejecutor / Memento) con estado
  - Alertas Guardian rojas / amarillas / verdes
  - Empresas-hijas operando (CIP en diseño, LikeTickets activo, etc.)
  - Cron jobs próximos
  - Costo 24h por proveedor (Anthropic, OpenAI, Google, Manus)
  - Critic Visual último smoke + score
  - Pipeline E2E último run + status
  - Embrión más invocado últimas 24h
  - Modelo LLM más usado últimas 24h
  - Convergencias del día (cuándo dos hilos llegaron al mismo patrón)
  - Memento: pre-flights ejecutados

**3.A.2 — Refresh automático cada 15s**

Riverpod stream que actualiza métricas. Stub: rotación de números mock con jitter realista para feel vivo.

**3.A.3 — Modo presentación**

Tap en card → fullscreen para casteo a TV / proyector. Cierra con esc.

### 3.B — Threads denso

**3.B.1 — Vista arquitecto del Threads**

`CockpitThreadsScreen`:
- Multi-thread paralelos visibles (3 columnas o split panes)
- Filtros sofisticados: por proyecto del portfolio, por hilo Manus, por fecha, por sprint
- Búsqueda semántica en historial completo (stub: keyword search por ahora; semántica real post-pgvector)
- Atajos: ⌘K command palette inline, ⌘P salta a empresa-hija por nombre

**3.B.2 — Command palette ⌘K (stub)**

Modal con input + sugerencias contextuales:
- "Salta a CIP"
- "Pausa Sprint 88"
- "Catastro de Modelos LLM"
- "Empezá nuevo thread con Manus Catastro"
- "Cierra Sprint 87.2 con verdict comercializable"

Stub: ejecuta cualquier sugerencia con feedback simulado. Conexión real a kernel post-Mobile 6.

### 3.C — Catastro

**3.C.1 — Vista de los 50+ modelos LLM rankeados**

`CatastroLLMScreen`:
- Tabla densa con columnas: nombre, proveedor, macroárea, score compuesto, costo per-1M-tokens, latencia promedio, anti-gaming flags, último uso
- Filtros: por macroárea (Razonamiento, Coding, Arena humana, Razonamiento Estructurado, Embeddings), por confidentiality_tier, por activo/inactivo
- Sort por columna
- Tap en row → detalle completo del modelo + override manual disponible

Stub: data hardcoded de los 6 Sabios canónicos (DSC-V-001) + 44 modelos adicionales con scores plausibles.

**3.C.2 — Sub-tabs para los 3 Catastros (DSC-G-007)**

Navigation bar al top con 3 tabs:
- **Modelos LLM** (existente, completo en Mobile 3)
- **Suppliers Humanos** (placeholder visible — datos llegan post-Sprint Catastro-A)
- **Herramientas AI Especializadas** (placeholder visible — datos llegan post-Sprint Catastro-A)

Cuando Sprint Catastros 0 + Catastro-A cierren en kernel, los tabs vacíos se llenan automáticamente vía WebSocket.

### 3.D — Embriones

**3.D.1 — Vista de los 9+ Embriones**

`EmbrionesScreen`:
- Grid de cards, una por Embrión:
  - Critic Visual, Critic Brand (post-Sprint 88), Product Architect, Creativo, Estratega, Financiero, Investigador, Técnico, Ventas, Vigía, Manifestación (post-Sprint Kernel 0), Convergencia Cronos (post-SMP)
- Cada card muestra: FCS (Functional Consciousness Score), última invocación, decisiones recientes, sparkline de actividad

**3.D.2 — Modo `debate` y `quorum` visible**

Cuando los Embriones colectivos están activos (stub trigger: tap "simular debate"), aparece overlay mostrando los Embriones discutiendo en tiempo real (texto streaming en chat-like UI). Tres modos:
- `debate` — argumentos en favor/contra
- `quorum` — 5 Embriones votan, decisión por mayoría
- `synthesis` — Embrión Estratega sintetiza posiciones

Stub: textos pre-grabados por modo.

### 3.E — Guardian

**3.E.1 — Los 15 Objetivos Maestros como panel de instrumentos**

`GuardianScreen`:
- 15 cards (5×3 grid o 3×5), una por Objetivo
- Cada card con score visual (rojo / amarillo / verde) basado en heurística per Objetivo (stub)
- Alertas activas listadas con severidad
- Recomendaciones accionables (stub: 3-5 recomendaciones plausibles)

**3.E.2 — Niveles del Corrective Actor visibles**

- Nivel 1 (alerta): cards amarillas con "Atención: ..."
- Nivel 2 (bloqueo): cards rojas con "Bloqueante: ..."

**3.E.3 — Self-health check del Guardian**

Sub-card al final: "Guardian última auto-evaluación: 2h ago — saludable" (stub).

### 3.F — Atajos magna

**3.F.1 — Implementación completa**

Hook `useGlobalShortcuts` con:
- ⌘K → command palette universal
- ⌘P → jump to portfolio empresa
- ⌘E → jump to Embrión
- ⌘G → abre Guardian
- ⌘T → salta a Catastro (con sub-tab default Modelos LLM)
- ⌘R → abre Replay del último run (Sprint Mobile 4)
- ⌘shift+M → toggle a Modo Daily con biometría

Funcionan desde cualquier superficie del Cockpit. Visualmente discoverables: hint bar fina al bottom mostrando atajos disponibles en context.

### 3.G — Smoke productivo + validación

Builds limpios. Alfredo navega las 5 superficies + prueba atajos + valida densidad + estética. Si convence: Sprint Mobile 3 cerrado verde.

---

## 4. Magnitudes esperadas

- ~1,800 LOC nuevas
- ~25 archivos nuevos en `modes/cockpit/`
- ~20 widget tests + golden files
- 1 validación humana

---

## 5. Disciplina aplicada

- ✅ DSC-G-004: brand DNA en superficies densas (densidad NO es excusa para feo — Bloomberg + Apple)
- ✅ DSC-G-007: Catastro con 3 tabs preparados (LLM hoy, Suppliers + Herramientas AI cuando lleguen)
- ✅ Capa Memento: stubs aislados
- ✅ Brand DNA error naming Dart: `cockpitMOCDashboardRefreshFailed`, `cockpitCatastroLLMSortFailed`, etc.
- ✅ Privacy-first: el Cockpit es invisible a quien no pasó biometría

---

## 6. Cierre formal

> 🏛️ **Modo Cockpit fase 1 — DECLARADO** (5 superficies + atajos magna funcionales)

---

## 7. Lo que NO entra

- Memento + Portfolio + FinOps + Pipeline E2E + Replay (Sprint Mobile 4)
- Computer Use + Coding embedded + Bridge + Settings (Sprint Mobile 5)
- Datos reales (esperan SMP)

---

— Cowork (Hilo A), spec preparada 2026-05-06.