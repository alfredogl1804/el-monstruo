# PACK 01 — ACTO 1: Interfaces co-creadas (Alfredo ↔ Cowork)

> **Estado:** CANON_VIGENTE (firmado por Cowork T2, no contradicho por T1)
> **Fecha doctrinal:** 2026-05-06 a 2026-05-11
> **Fuente magna:** SRC-001 (`docs/EL_MONSTRUO_APP_VISION_v1.md` v1.3, 1117 líneas) + SRC-002 (audit Cowork) + SRC-022 (DSC-MO-002)

---

## Síntesis del paradigma

El Monstruo es **un kernel con N cuerpos**. La app Flutter es UNO de los transports — no "la app del Monstruo". Cada transport renderiza A2UI generative UI según su capacidad. La excelencia visual es una de las 10 reglas inviolables: *"Si no es bonita no motiva"* (regla 2, SRC-001 Cap 0).

Brand DNA: **forja #F97316 + graphite #1C1917 + acero #A8A29E**, aplicado con minimalismo Apple/Tesla, no densidad Bloomberg. Cero badges, cero gamification, cero notificaciones falsas, cero engagement traps, cero streaks (regla 3 — silencio inteligente).

---

## Las 10 reglas inviolables (SRC-001 Cap 0, citadas verbatim)

| # | Nombre | Texto canónico |
|---|---|---|
| 1 | Menos es más | *"Cada feature, cada pantalla, cada palabra en la UI tiene que justificar su existencia."* |
| 2 | Si no es bonita no motiva | *"Brand DNA forja + graphite + acero aplicado con minimalismo, no con densidad Bloomberg."* |
| 3 | Silencio inteligente | *"Callado por defecto. Habla solo cuando le preguntan. Cero notificaciones falsas, cero gamification, cero engagement traps, cero streaks."* |
| 4 | Describir, no prescribir | *"Espejo, no entrenador. Anti-coaching invasivo."* |
| 5 | Verdad cruda | *"Modo detractor cuando hace falta — confrontar al usuario con verdades incómodas."* |
| 6 | Anti-influencia inadvertida | *"Articular lo que la persona ya tiene en la cabeza es válido; detonar arquitecturas elaboradas que la persona pueda adoptar pasivamente no lo es."* |
| 7 | Privacidad como física | *"La criptografía hace imposible. Pasamos de policy a physics."* |
| 8 | Cero fee | *"Pago pass-through transparente. Cero margen del Monstruo."* |
| 9 | Sin promoción | *"El Monstruo no se publicita. Se descubre."* |
| 10 | Validar contra 15 Objetivos | *"Cualquier feature... se chequea contra los 15 Objetivos. Si viola alguno, no entra."* |

---

## Las 5 superficies del Modo Daily (SRC-001 Cap 2)

| # | Superficie | Función | Estado código |
|---|---|---|---|
| D1 | **Home** | Voice-first input universal + cámara visual search + río de Cronos como franja navegable | ❌ no existe en `lib/modes/daily/home/` |
| D2 | **Threads** | Historial de conversaciones, una por línea con resumen 1-frase | ❌ no existe |
| D3 | **Pendientes** | Acciones HITL streaming — preview editable inline antes de confirmar | ❌ no existe |
| D4 | **Conexiones** | WhatsApp, Mail, Calendar, Maps, Photos, Files, Drive, Pay (toggle granular + audit) | ❌ no existe |
| D5 | **Perfil** | Identidad, privacidad, claves SMP, recovery Shamir, export/delete | ❌ no existe |

---

## Las 15 superficies del Modo Cockpit (SRC-001 Cap 3)

| # | Superficie | Función |
|---|---|---|
| C1 | **MOC Dashboard** | Operations command center con 15 Objetivos como panel |
| C2 | **Threads + Comando** | Hilos densos con metadata operacional |
| C3 | **Portfolio Empresas-Hijas** | 20 proyectos como tarjetas vivas (CIP primera) |
| C4 | **Catastro de los 4** | Modelos LLM + Agentes 2026 + Suppliers + Herramientas AI con Trono Score |
| C5 | **Embriones** | 9+ Embriones especializados con FCS, última invocación, decisiones |
| C6 | **Guardian** | 15 Objetivos como panel de instrumentos con scores rojo/amarillo/verde |
| C7 | **Memento** | error_memory + validaciones pre-flight + Síndrome Dory stats |
| C8 | **Replay (Timelapse)** | Selector E2E + timeline scrubable estilo Devin |
| C9 | **Computer Use / Sandbox** | Browser + terminal + filesystem en vivo del agente |
| C10 | **FinOps** | Tokens por hilo/empresa/sprint + costo por proveedor + ROI + forecast |
| C11 | **Pipeline E2E** | Sprint 87 NUEVO 12 pasos + extensiones CIP-complejidad |
| C12 | **Coding embedded** | IDE liviano para intervenir código sin salir |
| C13 | **Hilos Manus** | 3+ hilos activos con sprint actual + ETA + bridge accesible |
| C14 | **Bridge / Comunicación inter-hilos** | Reportes y audits navegables |
| C15 | **Settings + Admin** | Variables Railway, override defaults, gestión tier-access |

**Estado código:** **0/15 existen**. Solo hay 1 pantalla MOC vaga en el Flutter actual (SRC-002 §1).

---

## Las 8 capabilities transversales (SRC-001 Cap 4)

| Capability | Función | Estado |
|---|---|---|
| Visual Search | Cámara → identifica/precio/traduce | ❌ |
| Photo Intelligence | Búsqueda semántica fotos bajo SMP | ❌ |
| File Intelligence | Búsqueda semántica archivos bajo SMP | ❌ |
| App Intelligence | Inteligencia sobre apps usadas | ❌ |
| Vault Soberano | Passwords/keys bajo SMP | ❌ |
| Shopping Intelligence | Búsqueda + checkout HITL streaming | ❌ |
| Notes Intelligence | Apple Notes/Keep/Notion → tareas implícitas | ❌ |
| Health Intelligence | HealthKit/Health Connect bajo SMP | ❌ |

Plus 2 base transversales: **Listening Ambient** 24/7 con kill switch verbal "Monstruo apágate" + **Smart Rendering** que compone sobre los 4 Catastros.

---

## Toggle Daily ↔ Cockpit (SRC-001 Cap 1)

> *"3 dedos hold + Face ID. Opcionalmente segundo factor con device confiado agnóstico — Apple Watch, Wear OS, Garmin, o passphrase + biometría sola."*

Bundle único Flutter `com.elmonstruo.app`. Plataformas: iOS + macOS al inicio, iPadOS responsive, Android post-v1.0, Web no prioritaria.

---

## Estructura de carpetas canónica (SRC-001 Cap 1)

```
apps/mobile/
├── lib/
│   ├── main.dart                       # ÚNICO entry
│   ├── core/
│   │   ├── transport/kernel_websocket.dart
│   │   ├── a2ui/renderer.dart
│   │   ├── services/{kernel,catastro,embriones,memento,connections,voice,
│   │   │   visual_search,photo,file,app,vault,shopping,notes,health,
│   │   │   ambient_listening,smart_notebook,cronos,manifestation,replay}_service.dart
│   │   ├── theme/brand_dna.dart        # forja + graphite + acero
│   │   ├── widgets/{a2ui_components,memento_badge,error_toast}
│   │   ├── crypto/{smp,secure_enclave_bridge,on_device_transcription}
│   │   └── state/mode_provider.dart    # daily vs cockpit
│   ├── modes/
│   │   ├── daily/                      # 5 superficies
│   │   └── cockpit/                    # 12-15 superficies
│   └── routing/mode_router.dart
└── pubspec.yaml
```

Plus servicio paralelo:
```
apps/whatsapp_gateway/
├── kernel_bridge/
├── webhook_handler/
├── interactive_messages/
└── confidente_silent_link/
```

**Estado código actual** (SRC-019, 16-may): 52 archivos `.dart`, NO sigue esta estructura. Sprint MOBILE_REALIGNMENT_001 (SRC-006) firmado para pavimentar.

---

## El conflicto con Acto 2

Acto 1 dice: **"20 superficies funcionales = éxito"**.

Acto 2 dice: **"Si abrís dashboard, ya falló"** (SRC-005 frase canónica magna §9.F).

Sin integración explícita firmada por T1, todo sprint UI nuevo arrastra deuda doctrinal. Ver `PACK_02_ACTO_2_CALM_TECH.md`.
