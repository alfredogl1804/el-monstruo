# El Monstruo — App Móvil

App móvil nativa para El Monstruo, el agente IA soberano de Alfredo Góngora.

## Stack

- **Flutter 3.41+** (Dart 3.7+) — Un codebase, 3 dispositivos
- **AG-UI Protocol** — Streaming en tiempo real desde el kernel
- **A2UI / GenUI SDK** — Generative UI (interfaces dinámicas generadas por el agente)
- **Riverpod** — State management reactivo
- **Go Router** — Navegación declarativa

## Dispositivos Target

| Dispositivo | Pantalla | Rol |
|---|---|---|
| Samsung S26 Ultra | 6.9" | Comando principal |
| OPPO Find N5 | 8.12" (desplegado) | Estación de trabajo |
| iPhone 17 Pro | 6.3" | Canal de voz (Siri + MCP futuro) |

## Estructura

```
lib/
  main.dart              → Entry point
  app.dart               → MaterialApp + Router
  core/
    config.dart           → Kernel URLs, timeouts, feature flags
    router.dart           → GoRouter configuration
  features/
    chat/                 → Chat principal con streaming
    sandbox/              → Terminal + Browser viewer
    files/                → Archivos generados
    settings/             → Config + Kernel status
    genui/                → A2UI Generative UI renderer
  models/                 → Data models (ChatMessage, ToolEvent, etc.)
  providers/              → Riverpod state management
  services/               → KernelService (REST + WebSocket)
  widgets/                → Shared widgets
  theme/                  → MonstruoTheme design system
```

## Setup

```bash
# Instalar dependencias
flutter pub get

# Correr en desarrollo
flutter run

# Build Android APK
flutter build apk --release

# Build iOS
flutter build ios --release
```

## Arquitectura

```
[Flutter App] ←── AG-UI/WebSocket ──→ [AG-UI Gateway] ──→ [Kernel Railway]
                                                                  │
                                                          [LangGraph + Tools]
                                                          [E2B Sandbox]
                                                          [Memory + Knowledge]
```

## Conexión al Kernel

La app se conecta al kernel de El Monstruo en Railway via:
1. **REST API** — Para comandos y queries (health, memory, tools)
2. **WebSocket** — Para streaming de mensajes y tool events en tiempo real
3. **AG-UI Protocol** — Para Generative UI components

El gateway traduce entre AG-UI events y la API del kernel.
