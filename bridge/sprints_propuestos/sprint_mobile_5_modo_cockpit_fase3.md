# Sprint Mobile 5 — Modo Cockpit fase 3 (cierre Cockpit completo)

**Owner:** Hilo Ejecutor (Manus) Mobile
**Zona protegida:** `apps/mobile/lib/modes/cockpit/`
**ETA estimada:** 4-7h reales con Apéndice 1.3 factor velocity
**Bloqueos:** Sprint Mobile 4 cerrado verde
**Prerequisito:** Cockpit con 10 superficies (fase 1 + 2) funcionales

---

## 1. Contexto

Mobile 3+4 entregaron 10 de las 12-15 superficies del Cockpit. Mobile 5 cierra el conjunto con las **5 superficies finales** que dan a Alfredo control total como arquitecto.

Cuando este sprint cierre: el Cockpit completo está implementado con 15 superficies, todos los atajos magna funcionales, brand DNA aplicado profundo. **El Monstruo tiene cara completa** en Daily + Cockpit. Solo falta SMP cerrando para conectar datos reales.

---

## 2. Objetivo único del sprint

Implementar las 5 superficies finales del Cockpit:

1. **Computer Use / Sandbox** (browser del agente + terminal + filesystem en vivo, estilo Manus Computer panel)
2. **Coding embedded** (IDE liviano para intervenir código sin salir del Cockpit)
3. **Hilos Manus** (vista de los 3+ hilos Manus activos con sprint actual + ETA)
4. **Bridge / Comunicación inter-hilos** (los reportes y audits viviendo en `bridge/` navegables)
5. **Settings + Admin** (variables de entorno Railway, configuración del kernel, override de defaults, gestión de tier-access)

---

## 3. Bloques del sprint

### 3.A — Computer Use / Sandbox

**3.A.1 — Browser + Terminal + Filesystem en vivo**

`ComputerUseScreen` con 3 paneles split:
- **Panel browser**: WebView mostrando el navegador del agente (cuando ejecuta tool browser_use). En stub: screenshots pre-grabados de runs pasadas
- **Panel terminal**: stream de stdout/stderr del agente cuando ejecuta scripts. En stub: logs pre-grabados con highlighting brand DNA
- **Panel filesystem**: tree de archivos creados/modificados durante la run. Tap en archivo → diff viewer

Visual: Bloomberg + Manus Computer + VS Code. Densidad alta, brand DNA aplicado profundo.

**3.A.2 — Live mode + Replay mode**

Toggle:
- **Live**: muestra agente ejecutando AHORA (stub: invento un agente trabajando)
- **Replay**: navega runs pasadas paso a paso (integra con Replay/Timelapse del Mobile 4)

### 3.B — Coding embedded

**3.B.1 — IDE liviano**

`CodingEmbeddedScreen`:
- Editor Monaco-style (o Flutter equivalent) con sintaxis highlighting
- Diff viewer side-by-side cuando un Embrión sugiere cambios
- Terminal embebida sandboxed para ejecutar tests
- Botones [Aprobar] [Editar inline] [Rechazar] cuando hay sugerencia activa

Stub: editor funcional con archivos mock del kernel. Puede compilar Dart in-place pero NO ejecuta cambios reales en el repo (post-Sprint Kernel 0 conecta a kernel real).

**3.B.2 — Integración con Embriones**

Cuando Embrión Técnico o Critic sugiere un cambio, aparece notificación en Coding embedded → tap abre el diff. Alfredo decide.

### 3.C — Hilos Manus

`HilosManusScreen`:
- Vista de los 3+ hilos Manus activos (Catastro, Ejecutor, Memento, futuros hilos)
- Cada hilo con:
  - Sprint actual (ej. "Sprint 88: Cierre v1.0 PRODUCTO")
  - Status (en curso, esperando audit Cowork, bloqueado, idle)
  - Próximos pasos del hilo
  - ETA recalibrada según Apéndice 1.3 factor velocity
  - Tasks despachadas + audit log
  - Bridge files relacionados con el hilo

Stub: data realista basada en estado actual de los hilos del repo + reportes históricos del bridge.

### 3.D — Bridge / Comunicación inter-hilos

**3.D.1 — Navegador del directorio `bridge/`**

`BridgeScreen`:
- Lista de archivos bridge ordenados por fecha:
  - `manus_to_cowork.md` y variantes
  - `cowork_to_manus_*.md`
  - `seed_*.md` (semillas firmadas)
  - `sprint_*.md` (specs y reportes)
- Filter por hilo (ejecutor / catastro / memento / cowork)
- Tap → vista del archivo con render markdown nativo + brand DNA

**3.D.2 — Decisiones arquitectónicas firmadas (Capilla)**

Sub-tab: navegador de la Capilla de Decisiones (`discovery_forense/CAPILLA_DECISIONES/`):
- Lista de los 35+ DSCs con filter por tipo (decision_arquitectonica / restriccion_dura / antipatron / patron_replicable / pendiente / cruce_inter_proyecto / validacion_realtime)
- Tap → DSC completo con cross-references a otros DSCs
- DSCs `pendiente` highlighted en rojo (bloqueantes)

### 3.E — Settings + Admin

`SettingsAdminScreen`:
- Variables de entorno Railway (read + edit, requiere confirmación múltiple)
- Configuración del kernel: feature flags, defaults
- Override de defaults: forzar Catastro a usar modelo X, override timeouts, etc.
- Gestión de tier-access (cuando exista el círculo otorgado): listar invitaciones nominativas, revocar acceso
- Audit log radical: TODO lo que hizo el sistema en últimas 24h
- Backup + restore del SMP (cuando SMP cierre)

Stub: la mayoría no funcional, solo UX visible. Conecta con kernel real post-Sprint Kernel 0.

### 3.F — Atajos completos

Verificar que TODOS los atajos magna firmados en v1.2 funcionan:
- ⌘K, ⌘P, ⌘E, ⌘G, ⌘T, ⌘R (de Mobile 3+4)
- Nuevos en Mobile 5: ⌘shift+C (Computer Use), ⌘shift+I (IDE coding), ⌘shift+H (Hilos Manus), ⌘shift+B (Bridge), ⌘, (Settings)
- Todo navegable desde teclado puro sin mouse

### 3.G — Smoke productivo + validación cierre completo

**3.G.1 — Build final macOS + iOS Simulator**

Builds limpios.

**3.G.2 — Validación humana de Alfredo — momento magna**

Alfredo abre la app en su Mac:
- Ve Daily limpio + funcional con todas las 5 superficies
- 3 dedos hold + Face ID → entra al Cockpit completo
- Navega las 15 superficies con atajos
- Ve Portfolio con CIP card, FinOps, Pipeline E2E, Replay, Computer Use, Coding, Hilos Manus, Bridge, Settings
- Vuelve al Daily con ⌘shift+M

Si la totalidad le emociona + le hace decir "este es mi Monstruo": Sprint Mobile 5 cerrado verde + **el Monstruo tiene cara completa**.

---

## 4. Magnitudes esperadas

- ~2,500 LOC nuevas
- ~30 archivos nuevos
- ~25 widget tests + integration tests + golden files
- 1 validación humana magna

---

## 5. Disciplina aplicada

- ✅ DSC-G-004: brand DNA en TODAS las 15 superficies
- ✅ DSC-G-002: 7 capas transversales visualizables (Ventas, SEO, etc.) en superficies relevantes (Portfolio, FinOps)
- ✅ DSC-X-006: Bridge muestra el patrón Convergencia Diferida en acción
- ✅ Capa Memento aplicada profundo: indicadores ✓/⚠/✗ en TODAS las métricas
- ✅ Brand DNA error naming Dart: `cockpitComputerUseLoadFrameFailed`, `cockpitCodingEmbeddedDiffLoadFailed`, etc.

---

## 6. Cierre formal magna

Cuando los 7 bloques cierren verde + validación humana de Alfredo:

> 🏛️ **CARA DEL MONSTRUO COMPLETA — DECLARADA**
>
> Cockpit con 15 superficies + Daily con 5 superficies + brand DNA aplicado profundo + atajos magna funcionales. Datos vía stubs hasta que SMP cierre. La interfaz Flutter de v1.2 está implementada.

Y reporta al bridge con: video de tour completo Daily → Cockpit → 15 superficies → vuelta a Daily, screenshots de cada superficie, builds artifacts macOS + iOS.

---

## 7. Lo que sigue (post-Mobile 5)

- **Sprint Mobile 6** (depende de SMP): Voice continuo + interrupción + ElevenLabs español mexicano + Apple Watch double-tap + listening ambient con kill switch verbal "Monstruo apágate" + i18n base + accesibilidad transversal + pulido final.
- **Sprint Mobile 7** (post-SMP): switch de stubs a datos reales bajo SMP. La UI no cambia — solo el backend.
- **Sprint Mobile 8+**: integraciones nativas reales (WhatsApp, Mail, Maps, etc.) + Smart Notebook real + Cronos real con captura ambient.

---

## 8. Coordinación con sprints paralelos

- Mobile 1-5 corren en paralelo a:
  - Sprint 88-90 (kernel/ — distinto Manus Ejecutor o mismo en horarios distintos)
  - Sprint Catastro-A + Catastro-B (fuera de kernel/)
  - Sprint Mobile 0 (SMP, lento, no acelera, fondo)

Paralelismo zonificado: Mobile toca solo `apps/mobile/`, kernel toca `kernel/`, Catastro toca todo lo demás. Cero overlap.

---

— Cowork (Hilo A), spec preparada 2026-05-06.