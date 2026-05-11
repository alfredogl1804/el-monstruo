---
id: REPORTE_BINARIO_APP_FLUTTER_2026_05_11
fecha: 2026-05-11
arquitecto: Cowork
naturaleza: reporte_operativo_no_audit
nivel_autoridad: 3 (datos derivados de verificación filesystem)
proposito: Mapear qué de Mobile 1-5 + APP_VISION v1.3 está implementado en código real
cruza_con:
  - APP_VISION v1.3 (1116 líneas)
  - sprint_mobile_1_esqueleto_flutter.md
  - sprint_mobile_2_modo_daily_fase1_stubs.md
  - sprint_mobile_3_modo_cockpit_fase1.md
  - sprint_mobile_4_modo_cockpit_fase2.md
  - sprint_mobile_5_modo_cockpit_fase3.md
---

# Reporte Binario — Estado de la App Flutter vs Canonización

## Hallazgo dura central

> **La app Flutter actual NO sigue la arquitectura canonizada de Mobile 1 + APP_VISION v1.3. Tiene 6,220 LOC funcional pero con paradigma equivocado: "chat con agente IA" en lugar de "kernel con multi-transport + A2UI generative UI + Daily/Cockpit + Cronos".**

NO es vacío. NO es perdido. Es **divergencia arquitectónica que requiere realignment**, no rewrite.

---

## I. Estructura canonizada (Mobile 1 spec) vs real

| Path canonizado | Estado real | Notas |
|---|---|---|
| `main.dart` | ✅ existe (48 LOC) | OK |
| `app.dart` | ✅ existe (22 LOC) | Bootstrap básico |
| `core/transport/kernel_websocket.dart` | ❌ NO | Existe `services/kernel_service.dart` con Dio+WS. Naming viola DSC-G-004 |
| `core/a2ui/renderer.dart` | ❌ NO | Existe `features/genui/genui_renderer.dart` con naming diferente |
| `core/mensajeros/` | ❌ NO | Existe `services/` — **DSC-G-004 VIOLACIÓN** explícita |
| `core/theme/brand_dna.dart` | ❌ NO | Existe `theme/monstruo_theme.dart` (237 LOC) — naming distinto |
| `core/widgets/a2ui_components/` | ❌ NO | Componentes inline en features |
| `core/crypto/` | ❌ NO | Falta capa SMP |
| `core/state/mode_provider.dart` | ❌ NO | **No existe toggle Daily/Cockpit** |
| `modes/daily/home_screen.dart` | ❌ NO | Existe `features/chat/chat_screen.dart` y `features/onboarding/` separados |
| `modes/cockpit/moc_dashboard_screen.dart` | ❌ NO | Existe `features/moc/moc_screen.dart` (646 LOC) pero NO dentro de `modes/cockpit/` |
| `routing/mode_router.dart` | ❌ NO | Existe `core/router.dart` (91 LOC) sin distinción Daily/Cockpit |

**Conclusión:** estructura física de carpetas NO sigue spec. Naming en varios casos viola DSC-G-004 ("NUNCA: service, handler, utils, helper, misc").

---

## II. Lo que SÍ existe en la app real (no canonizado en Mobile 1)

| Componente | LOC | Función observable |
|---|---|---|
| `features/chat/chat_screen.dart` | 206 | Chat principal con kernel |
| `features/chat/widgets/agent_selector.dart` | ? | **Selector de agentes externos** (Mobile 6 spec — voice + ambient + polish) |
| `features/chat/widgets/tool_activity_bar.dart` | ? | Tool activity en tiempo real |
| `features/embrion/embrion_screen.dart` | 545 | Pantalla del embrión — innovación no en Mobile 1 spec |
| `features/files/file_viewer.dart` | 458 | Visor de archivos |
| `features/files/files_screen.dart` | 58 | Lista de archivos |
| `features/finops/finops_screen.dart` | 304 | FinOps en Cockpit (cap 3 APP_VISION) |
| `features/genui/genui_renderer.dart` | 48 | **Generative UI renderer** — es el A2UI pero con naming diferente |
| `features/genui/genui_screen.dart` | 173 | Pantalla genui |
| `features/memory/memory_screen.dart` | 246 | Memoria del Monstruo |
| `features/moc/moc_screen.dart` | 646 | **MOC Dashboard del Cockpit** (Mobile 3 spec) — el más grande |
| `features/onboarding/onboarding_screen.dart` | 483 | Onboarding inicial |
| `features/sandbox/sandbox_screen.dart` | 377 | Computer Use sandbox |
| `features/settings/settings_screen.dart` | 268 | Settings |
| `services/kernel_service.dart` | 389 | Conexión Dio REST + WebSocket al Gateway |
| `services/agent_service.dart` | 145 | Servicio agentes externos |
| `services/voice_service.dart` | **34** | **STUB casi vacío** — falta voice continuo |
| `services/notification_service.dart` | 61 | Firebase Messaging |
| `services/thread_persistence.dart` | 104 | Hive persistence |
| `providers/chat_provider.dart` | 494 | Riverpod global state |
| `widgets/shell_scaffold.dart` | 362 | Shell scaffold con navigation |
| `widgets/foldable_layout.dart` | 38 | Soporte dual-screen |

**Total: 6,220 LOC** organizados en 31 archivos.

---

## III. Mapeo Mobile 1-6 specs → realidad

### Mobile 1 (Esqueleto) — Estado: ~35%

✅ App Flutter base macOS+iOS configurada (`pubspec.yaml` ^3.29.0)
✅ Riverpod + go_router + dio + web_socket_channel + firebase + hive
✅ Theme (pero no `brand_dna.dart` canonizado — está como `monstruo_theme.dart`)
✅ Kernel service con WebSocket
❌ Toggle Daily/Cockpit con 3 dedos + Face ID (NO existe)
❌ Estructura `modes/daily/` + `modes/cockpit/`
❌ `core/a2ui/renderer.dart` (existe equivalente con naming diferente)
❌ A2UI renderer pixel-a-pixel según spec
❌ MOC Dashboard dentro de `cockpit/` (está en features/moc)

### Mobile 2 (Daily fase 1 — 5 superficies) — Estado: ~20%

❌ Home superficie con input voice + cámara + Río Cronos (falta Río)
❌ Threads superficie como tab dedicado
❌ Pendientes superficie como tab dedicado
❌ Conexiones superficie como tab dedicado
❌ Perfil superficie como tab dedicado
❌ BottomNavigationBar 5 tabs
🟡 Algo de chat existe pero NO con paradigma Daily 5-superficies

### Mobile 3 (Cockpit fase 1) — Estado: ~50%

✅ MOC Dashboard implementado (646 LOC en `features/moc/`)
✅ Memory Screen
✅ Settings Screen
🟡 Embriones screen (innovación, no en spec original)
🟡 Sandbox screen (Computer Use)
🟡 FinOps screen (parte de Cap 3 APP_VISION)
❌ Threads + Comando con ⌘K command palette
❌ Portfolio Empresas-Hijas screen
❌ Catastro screen (Cockpit cap 3)
❌ Guardian screen
❌ Memento screen
❌ Replay (Timelapse) screen
❌ Pipeline E2E screen
❌ Coding embedded screen
❌ Hilos Manus screen
❌ Bridge screen

### Mobile 4-5 (Cockpit fase 2+3) — Estado: ~10%

La mayoría de las 12-15 superficies del Cockpit canónicas en cap 3 APP_VISION NO existen.

### Mobile 6 (voice + ambient + polish + i18n) — Estado: ~5%

✅ `agent_selector.dart` existe (componente de Mobile 6)
❌ `voice_service.dart` casi vacío (34 LOC stub)
❌ Listening ambient continuo (cap 4 APP_VISION) — totalmente ausente
❌ Apple Watch double-tap veto táctico
❌ Wake-phrase "Monstruo apágate"
❌ Voz brand distintiva con timbre canonizado
❌ i18n bridge entre kernel/i18n y app
❌ Push notifications wired

---

## IV. Las 8 Capabilities Transversales del Cap 4 APP_VISION — Estado

| Capability | Service esperado | Estado real |
|---|---|---|
| Visual Search | `visual_search_service.dart` | ❌ NO |
| Photo Intelligence | `photo_intelligence_service.dart` | ❌ NO |
| File Intelligence | `file_intelligence_service.dart` | 🟡 `features/files/` existe pero no semantic search |
| App Intelligence | `app_intelligence_service.dart` | ❌ NO |
| Vault Soberano | `vault_service.dart` | ❌ NO |
| Shopping Intelligence | `shopping_service.dart` | ❌ NO |
| Notes Intelligence | `notes_service.dart` | ❌ NO |
| Health Intelligence | `health_service.dart` | ❌ NO |
| Smart Rendering | `smart_rendering_service.dart` | ❌ NO |
| Listening ambient | `ambient_listening_service.dart` | ❌ NO |
| Smart Notebook (Cronos active) | `smart_notebook_service.dart` | ❌ NO |
| Cronos service | `cronos_service.dart` | ❌ NO |
| Manifestation service | `manifestation_service.dart` | ❌ NO |
| Replay service | `replay_service.dart` | ❌ NO |

**Total Capabilities Transversales implementadas: 0 de 14.** Conceptos canonizados en doctrina v1.3 pero código ausente.

---

## V. SMP (Capítulo 7 APP_VISION) — Estado

| Componente SMP | Estado |
|---|---|
| `core/crypto/smp.dart` | ❌ NO existe |
| `core/crypto/secure_enclave_bridge.dart` | ❌ NO existe |
| `core/crypto/on_device_transcription.dart` | ❌ NO existe |
| Confidentiality tier en Catastro | 🟡 Existe en backend, no propagado a Flutter |
| Shamir's Secret Sharing recovery | ❌ NO existe |

**SMP es Sprint Mobile 0 canonizado como prerequisito de v1.0 — NO implementado.**

---

## VI. Cronos (Capítulo 5 APP_VISION) — Estado

❌ Sin pantalla Cronos
❌ Sin río de Cronos
❌ Sin 4 modos de captura
❌ Sin 9 capas transversales personales
❌ Sin convergencias inter-capa
❌ Sin Modo Espejo / Testigo
❌ Sin Modo Cripta
❌ Sin Smart Notebook

**Cronos: 0% implementado. Es el corazón de la promesa "memoria verificable de tu vida".**

---

## VII. Veredicto operativo

**La app actual es:**
- ✅ Funcional como **prototipo de chat con kernel** (60-70% de eso)
- ❌ NO es la **app del Monstruo según APP_VISION v1.3** (~15-25% de la visión magna)

**Métrica realista:** la app está al **~20-25% de lo canonizado en APP_VISION v1.3**, NO al ~50-60% como sugerí en audits anteriores. Mi audit anterior subestimaba la doctrina canonizada e inflaba el sustrato.

**La doctrina dice que la app debe:**
- Tener 2 modos (Daily + Cockpit) con toggle gestual
- 5 superficies Daily + 12-15 superficies Cockpit
- A2UI generative UI invocado en tiempo real (sin pantallas pre-fabricadas)
- Cronos como capa central de memoria
- 14 capabilities transversales como servicios
- SMP como base criptográfica
- Voice as input dominante con ambient listening
- Modo Confidente sin nombre en UI

**Lo que existe es:**
- 1 modo (sin Cockpit-Daily explícito)
- ~10 pantallas estilo features tradicionales
- GenUI renderer existe pero sin paradigma A2UI completo
- Sin Cronos
- Sin capabilities transversales
- Sin SMP
- Voice service stub vacío
- Sin Modo Confidente

---

## VIII. 3 caminos posibles

### Camino A — Realignment Incremental (RECOMENDADO)

Mantener los 6,220 LOC. Agregar lo crítico que falta sin destruir lo que funciona. Sprint "Mobile Realignment 001":

1. Estructura `modes/daily/` + `modes/cockpit/` + toggle gestural
2. Renombrar `services/` → `mensajeros/` (DSC-G-004 enforcement)
3. Reorganizar `features/moc/` → `modes/cockpit/moc/`
4. Reorganizar `features/chat/` → `modes/daily/home/`
5. BottomNavigationBar Daily con 5 tabs (Home + Threads + Pendientes + Conexiones + Perfil)
6. Renombrar `genui/` → `core/a2ui/`
7. Agregar `core/theme/brand_dna.dart` (puede ser symlink/proxy de monstruo_theme.dart si la paleta ya es correcta)

**ETA estimada:** 1-2 sesiones Manus (Catastro). 200-400 LOC refactor + 600-800 LOC nuevas.

### Camino B — Verificar antes de mover

Antes del refactor estructural: verificar que la app **actualmente compila y funciona** en tu Mac. Si compila y conectás al kernel, mover archivos es menos riesgoso. Si NO compila, ese es el bloqueante real.

### Camino C — Aceptar divergencia, actualizar visión

Si el código actual representa una evolución consciente de la doctrina (no error), actualizar APP_VISION v1.4 para reflejar la realidad. Esto requeriría conversación contigo sobre por qué Manus desvió.

**Mi recomendación dura como T2:** **A + B en paralelo**. Vos verificás que compila en Mac (Camino B = T4 del sprint ARRANQUE-FLUTTER suspendido). Yo paralelamente preparo prompt para Hilo Catastro Manus que ejecute Camino A.

---

## IX. Próxima acción

Voy a producir en próximo turno (o este mismo si tengo turnos disponibles):

**Doc operativo:** `bridge/sprint_MOBILE_REALIGNMENT_001.md` con:
- Tareas concretas para Hilo Catastro Manus
- Order of operations (no romper lo que funciona)
- Tests de aceptación
- Coordinación con Sprint Mobile 6 (voice + ambient) que viene después

Después de eso queda canonizado el siguiente sprint operativo. Vos lanzás push a Manus Catastro y arranca.

**Lo que NO recomiendo hacer ahora:**
- ❌ Borrar la app actual y reempezar (perdés 6,220 LOC funcional)
- ❌ Construir SMP antes de verificar que la app compila
- ❌ Implementar 14 capabilities antes de tener Daily/Cockpit toggle
- ❌ Construir Cronos antes de tener las 5 superficies Daily

**Lo que SÍ recomiendo en orden:**
1. Tú: `cd apps/mobile && flutter analyze && flutter build macos --debug` (verificar compila)
2. Yo: producir spec Mobile Realignment 001
3. Manus Catastro: ejecutar Realignment (refactor estructural sin perder código)
4. Vos: smoke test app Realignment connecting to kernel
5. Después: Sprint Mobile 6 (voice + ambient) sobre arquitectura limpia
6. Después: SMP Sprint Mobile 0
7. Después: capabilities transversales progresivas
8. Después: Cronos completo

Eso es el orden honesto. ~8-12 semanas de trabajo total para "Cara Completa del Monstruo según APP_VISION v1.3".

---

*Reporte firmado por Cowork como Arquitecto T2. 2026-05-11. Bajo Pre-flight Memento ejecutado y modo "actuar sin preguntar" respetado por clasificación S7.*
