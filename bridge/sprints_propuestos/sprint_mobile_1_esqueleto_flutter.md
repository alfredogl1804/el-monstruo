# Sprint Mobile 1 — Esqueleto Flutter unificado

## Audit Pre-Sprint

**Hallazgo crítico:** Codebase Flutter ya existe (~30 archivos, no from scratch). Violación Brand DNA detectada: paleta indigo/purple/mint usada en app existente en lugar de forja (#F97316) + graphite (#1C1917) + acero (#A8A29E).

**Velocity real:** 2-3x más rápido que estimación base. Manus cierra sprints en 15 min; velocidad demostrada: refactorings profundos + testing completo en ese marco.

**ETA recalibrada:** 15-30 min reales (no 3-5h). Tareas: (1) Brand DNA recovery + color refactor, (2) Design tokens integration, (3) Estructura base verification, (4) Tests + quality gates.

**Dependencias actualizadas:** Sprint Catastro-B produce `@monstruo/design-tokens` — consumible pero no bloqueante (colores puede ir inline si no está listo).

---

**Owner:** Hilo Ejecutor (Manus) — segundo Manus Ejecutor en paralelo al que está en `kernel/`, o el mismo en horario distinto
**Zona protegida:** `apps/mobile/` (nuevo) + `packages/design-tokens/` (de Sprint Catastro-B)
**ETA estimada:** 15-30 min reales con velocity demostrada (Manus cierra sprints en 15 min)
**Bloqueos:** Sprint Catastro-B debe haber entregado `@monstruo/design-tokens` (paralelizable, NO bloqueante absoluto — si no está se usa CSS vars inline temporales)
**Prerequisito:** v1.2 doc canónico (✅ commit `31166ab`)
**Dependencias:** ninguna externa que bloquee

---

## 1. Contexto

v1.2 firma la arquitectura Flutter del Monstruo: una sola app, dos modos (Daily + Cockpit) sobre el mismo cuerpo, multi-transport (Flutter como uno de N transports del kernel), generative UI vía A2UI v0.9, ejecución consciente como paradigma central.

Este sprint construye **el esqueleto** de la app Flutter — el chasis sin datos. Toggle entre modos, brand DNA aplicado, A2UI renderer streaming-first, conexión persistente WebSocket al kernel preparada (aunque sin handlers reales). Cuando este sprint cierra, Alfredo ve por primera vez la cara del Monstruo en pantalla — austera, hermosa, vacía pero visible.

**Crítico:** este sprint NO carga datos reales del usuario. SMP (Sprint Mobile 0) tarda 2-4 semanas reales en paralelo. Hasta que SMP cierre, la app vive con stubs en memoria. Esto es trade-off explícito firmado: ver el Monstruo en horas vs esperar semanas.

---

## 2. Objetivo único del sprint

Producir un esqueleto Flutter funcional, instalable en macOS + iOS, con:
- Bundle único `com.elmonstruo.app`
- Toggle gestural (3 dedos hold + Face ID) entre Modo Daily y Modo Cockpit
- Brand DNA forja (#F97316) + graphite (#1C1917) + acero (#A8A29E) aplicado a TODA superficie
- Conexión WebSocket persistente preparada (placeholder para kernel real, mock para sandbox)
- A2UI renderer básico que parsea esquemas declarativos JSON y renderiza tarjetas Flutter
- Modo Daily con superficie Home vacía + río de Cronos como franja horizontal con stub data
- Modo Cockpit con MOC Dashboard placeholder con stubs de métricas

Cuando este sprint cierra: Alfredo abre la app en su Mac, ve el Home minimalista con brand DNA aplicado, hace 3 dedos hold + Face ID, entra al Cockpit, ve la grilla densa, vuelve al Daily con ⌘shift+M. **Primera vista del Monstruo.**

---

## 3. Bloques del sprint

### 3.A — Bootstrap Flutter project

**3.A.1 — Crear proyecto Flutter en `apps/mobile/`**

```bash
cd apps
flutter create mobile --platforms=macos,ios --org=com.elmonstruo --project-name=elmonstruo
```

Configurar `pubspec.yaml`:
- Dart SDK >= 3.5.0 (validar versión vigente realtime per DSC-V-002)
- Dependencies: `flutter_riverpod`, `web_socket_channel`, `local_auth` (biometría), `shared_preferences`, `go_router`
- Dev: `flutter_lints`, `build_runner`

**3.A.2 — Estructura de carpetas según v1.2 Cap 1**

Replica EXACTA la estructura firmada en v1.2:

```
apps/mobile/lib/
├── main.dart                        # ÚNICO entry point
├── core/
│   ├── transport/
│   │   └── kernel_websocket.dart    # conexión persistente bidireccional (mock por ahora)
│   ├── a2ui/
│   │   └── renderer.dart            # renderer generative UI básico
│   ├── mensajeros/                  # placeholders con identidad (Brand DNA — DSC-G-004 prohíbe naming "services")
│   ├── theme/brand_dna.dart         # forja + graphite + acero aplicado
│   ├── widgets/
│   │   └── a2ui_components/         # componentes streaming-first
│   ├── crypto/                      # placeholder, sin SMP aún
│   └── state/
│       └── mode_provider.dart       # daily vs cockpit
├── modes/
│   ├── daily/
│   │   └── home_screen.dart         # superficie 1 con río Cronos stub
│   └── cockpit/
│       └── moc_dashboard_screen.dart # MOC con stubs
└── routing/
    └── mode_router.dart             # toggle Daily ↔ Cockpit
```

### 3.B — Brand DNA aplicado pixel a pixel

**3.B.1 — `core/theme/brand_dna.dart`**

Si `@monstruo/design-tokens` (Sprint Catastro-B) está listo: importar y consumir.
Si no: definir inline:

```dart
class BrandDNA {
  static const Color forja = Color(0xFFF97316);
  static const Color graphite = Color(0xFF1C1917);
  static const Color acero = Color(0xFFA8A29E);
  // + escalas 50-900 derivadas
  // + tipografía (familia + escala)
  // + spacing (escala 4px)
  // + shadows
  // + radius
  // + animations (curvas + duraciones canónicas)
}
```

**3.B.2 — `ThemeData` global con brand DNA**

Aplicar en `MaterialApp.theme` y `darkTheme` (dark mode nativo per v1.2 Cap 0 Regla 2):
- ColorScheme con seed `forja`
- Typography brutalista refinada
- AppBarTheme, ButtonTheme, etc. todos con identidad

NO usar `Colors.blue`, `Colors.grey` ni colores genéricos en NINGUNA pantalla.

### 3.C — Toggle Daily ↔ Cockpit

**3.C.1 — `mode_provider.dart`**

Riverpod `StateNotifier` con dos estados (`daily`, `cockpit`). Persistir preferencia en `shared_preferences` para que sobreviva restart.

Default: `daily` siempre que la app abre (Cockpit invisible para terceros que tomen el iPhone).

**3.C.2 — Gesto secreto + biometría**

Detector de 3 dedos hold de >1.5s sobre el logo del Monstruo en cualquier pantalla.
Al detectar: invocar `local_auth` para Face ID. Si éxito: switch a `cockpit`. Si falla: silencio total (no mostrar error — el Cockpit es invisible).

**3.C.3 — Atajo teclado ⌘shift+M en macOS**

`HardwareKeyboard` listener para volver de Cockpit a Daily con biometría rápida.

**3.C.4 — `mode_router.dart`**

`go_router` con dos sub-routers:
- `/daily/*` → DailyShell
- `/cockpit/*` → CockpitShell (guarded por estado `cockpit` activo)

Si alguien navega a `/cockpit/*` sin haber pasado el toggle, redirige silenciosamente a `/daily`.

### 3.D — Conexión persistente WebSocket (placeholder)

**3.D.1 — `core/transport/kernel_websocket.dart`**

Service que abre WebSocket al kernel del Monstruo en `wss://el-monstruo-kernel.railway.app/v1/agui/run` (o equivalente). Por ahora el WebSocket NO se conecta a kernel real — usa un mock que devuelve frames A2UI hardcodeados para demostrar el renderer.

Diseño: cuando el kernel real esté listo (post Sprint Kernel 0), solo cambia la URL — la app NO sabe la diferencia.

**3.D.2 — Reconexión automática + heartbeat**

Patrón estándar: ping cada 30s, reconnect con exponential backoff si pierde conexión. Estado expuesto vía Riverpod para que la UI muestre indicador sutil "conectado / reconectando" (un punto vivo / gris).

### 3.E — A2UI renderer básico

**3.E.1 — `core/a2ui/renderer.dart`**

Implementación mínima del estándar A2UI v0.9: parsea JSON declarativo y renderiza widgets Flutter. Soporta:

- `card` → `Card` widget con brand DNA
- `text` → `Text` con tipografía canónica
- `button` → `ElevatedButton` con estilo forja
- `image` → `Image.network` con placeholder graphite
- `column` / `row` → layouts básicos

NO soporta todavía: animaciones complejas, custom widgets, video, spatial. Esos vienen en sprints posteriores.

**3.E.2 — Test con esquemas mock**

Suite de tests con esquemas A2UI hardcodeados: el renderer produce widgets esperados.

### 3.F — Pantallas mínimas con stubs

**3.F.1 — Daily Home Screen**

Una superficie:
- Input central voice-first (placeholder, no funcional aún) + botón cámara
- Río de Cronos como franja horizontal abajo, scrollable, con 5-10 momentos stub (timestamps falsos pero formato correcto)
- AppBar minimalista con logo del Monstruo
- Cero badges, cero notificaciones, cero clutter

**3.F.2 — Cockpit MOC Dashboard Screen**

Superficie densa con stubs:
- Grid de 4-6 cards: "Sprints corriendo: 3 stub", "Hilos Manus activos: 2 stub", "Alertas Guardian: 0 stub", "Empresas-hijas: 7 stub", "Costo 24h: $X stub"
- Estilo Bloomberg + Linear + Cursor — denso pero hermoso, brand DNA aplicado profundo
- AppBar con atajos visibles ⌘K command palette (no funcional aún), ⌘P, ⌘shift+M

### 3.G — Smoke productivo

**3.G.1 — Build macOS + iOS Simulator**

```bash
cd apps/mobile
flutter build macos --release
flutter build ios --simulator
```

Ambos builds deben completar sin errores ni warnings críticos.

**3.G.2 — Validación humana de Alfredo**

Alfredo abre la app en su Mac:
- Ve Home limpio con brand DNA
- Hace 3 dedos hold sobre logo
- Pasa Face ID
- Entra al Cockpit, ve grid densa
- Cmd+shift+M vuelve a Daily

Si todo eso funciona y le emociona: Sprint Mobile 1 cerrado verde.
Si la estética no convence: hotfix con feedback específico antes de declarar cierre.

---

## 4. Magnitudes esperadas

- ~1,200 LOC nuevas (Flutter + Dart)
- ~25 archivos nuevos
- ~15 widget tests + 5 integration tests
- 2 builds productivos (macOS + iOS Simulator)
- 1 validación humana de Alfredo

---

## 5. Disciplina aplicada

- ✅ DSC-G-004: brand DNA aplicado pixel a pixel — cero colores genéricos
- ✅ DSC-V-002: validar versiones vigentes de Flutter SDK + Riverpod + paquetes Dart contra registries oficiales (Flutter has rapid releases)
- ✅ Brand DNA en error naming Dart: `kernelWebSocketConnectFailed`, `a2uiRendererParseFailed`, `modeToggleBiometricFailed`
- ✅ Capa Memento: si el WebSocket del kernel falla, la app sigue funcionando con stubs sin crash
- ✅ Privacy-first: NO recolectar telemetría hasta que SMP cierre
- ✅ Anti-Dory: stash → pull rebase → pop antes de cada commit

---

## 6. Cierre formal

Cuando los 7 bloques cierren verde + validación humana de Alfredo:

> 🏛️ **Esqueleto Flutter v0.1 — DECLARADO** (primera vista del Monstruo en pantalla)

Y reporta al bridge con: paths de archivos, screenshots de Daily Home + Cockpit MOC, video corto del toggle gestural, builds artifacts.

---

## 7. Lo que NO entra en este sprint

- Datos reales del usuario (esperan a SMP)
- Integraciones nativas con WhatsApp, Mail, Maps, Calendar (Sprint Mobile 2)
- Modo Confidente (Sprint Mobile 5+)
- Voz continua + Apple Watch double-tap (Sprint Mobile 6, depende de SMP)
- Captura ambient con kill switch verbal (Sprint Mobile 6, depende de SMP)
- Cronos real (stubs por ahora; real cuando SMP cierre)
- Smart Notebook (Sprint Mobile 4 con datos mock; real con SMP)
- Las 12-15 pantallas completas del Cockpit (Mobile 3 + 4 + 5 progresivos)

---

## 8. Coordinación con sprints paralelos

- **Sprint Mobile 1 (este)** corre en paralelo a Sprint 88-90 (kernel/) sin overlap
- **Sprint Catastro-B** entrega `@monstruo/design-tokens` que este sprint puede consumir si llega a tiempo
- **Sprint Mobile 0 (SMP)** corre en paralelo de fondo, no bloquea visualización del esqueleto

Punto de sincronización futuro: cuando SMP cierre, otro sprint (Mobile 7) cambia los stubs por datos reales bajo SMP.

---

— Cowork (Hilo A), spec preparada 2026-05-06.