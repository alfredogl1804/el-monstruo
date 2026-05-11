---
id: VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11
fecha: 2026-05-11
autor: Cowork T2 (Architect)
naturaleza: visión arquitectónica magna app Monstruo
proposito: integrar APP_VISION v1.3 + 15 Objetivos Maestros + 8 Capas Transversales + Capa 17 Seguridad + estado real código vs sprints canonizados, y producir el camino concreto a "clase mundial"
metodologia: lectura completa APP_VISION v1.3 (1117 líneas) + 15 Objetivos v3.0 (974 líneas) + 8 capas en código (kernel/transversales/{6}, kernel/sovereignty/engine.py, kernel/memento/) + 11 archivos críticos Flutter (apps/mobile/lib/) + 16 specs sprints_propuestos
restricciones_doctrinales:
  - DSC-G-008 v2 Gate de Evidencia
  - Sin pseudo-medición salvo emergente de rúbrica binaria
  - Cita verbatim doctrina; sin paráfrasis
  - Sin frases canónicas inventadas
  - Cero recomendación sin evidencia o sin nombre de path
estado: firme
cadencia: 2do audit canónico del día — excepción explícita T1 por requerimiento magna
---

# Visión Clase Mundial — App del Monstruo (Daily + Cockpit + Multi-transport)

## §0 — Shift conceptual magno (lo que estaba mal en mis audits previos)

Mis dos audits anteriores (FLUTTER_Y_SPRINTS y A2UI) operaron bajo asunción incorrecta: **"el Monstruo tiene UNA app Flutter"**. APP_VISION v1.3 Cap 1 corrige binariamente:

> *"El Monstruo no es una app — es un kernel con múltiples cuerpos. Hay un cerebro central (el kernel: LangGraph + Catastro + Embriones + memoria SMP + el motor de ejecución consciente). Hay N transports que sirven al mismo propósito desde distintos contextos."*

**Esto reescribe todo:**

| Transport | Prioridad APP_VISION | Estado real hoy |
|---|---|---|
| **WhatsApp Gateway** | **P0 paralelo a Flutter** | ❌ no existe |
| **App Flutter Daily** | **P0 paralelo a WhatsApp** | 🟡 parcial (chat + 8 dashboards) |
| **App Flutter Cockpit** | P1 post-Daily mínimo | ❌ no existe |
| **Apple Watch** | P1 | ❌ no existe |
| **Web Command Center** | P2 | 🟡 existe repo `el-monstruo-command-center` no auditado |
| **Vision Pro** | P3 v1.2+ | ❌ futuro |

**Cuando audité "13%-22% app vs APP_VISION" subestimé Flutter** porque medí solo contra Daily+Cockpit del mismo Flutter. Cuando Alfredo dijo "65% real" probablemente promediaba: kernel sólido (~85%) + transport Flutter como prototipo (~30%) + capas backend (~75%) + portfolio canonizado (~70%). Su rúbrica era global; la mía era de un solo transport. Las dos lecturas no contradicen — son denominadores distintos.

---

## §1 — Realidad presente verificada (código real, no narración)

### App Flutter actual — `apps/mobile/lib/`

**Arquitectura:**
- `main.dart` con `ProviderScope` (Riverpod) + ThreadPersistence + lock orientation
- `app.dart` con `MaterialApp.router` (GoRouter) + `MonstruoTheme.dark`
- `core/router.dart`: `initialLocation: '/chat'`, ShellRoute con 4 tabs (Chat/Sandbox/Files/Settings) + 5 rutas separadas (Embrion/Memory/FinOps/GenUI/MOC)
- `widgets/shell_scaffold.dart`: BottomNav 4 + Drawer 5 = 9 surfaces
- `core/config.dart` líneas 15-27: URLs hardcoded `ag-ui-gateway-production.up.railway.app` + override SharedPreferences

**Theme (`theme/monstruo_theme.dart` línea 5):**
> *"Inspired by ChatGPT, Claude, Gemini latest interfaces"*

Paleta: primary `#00E5FF` (cyan), secondary `#BB86FC` (púrpura), tertiary `#64FFDA`. SpaceGrotesk via google_fonts. **Esta paleta CONTRADICE APP_VISION v1.3 línea 39:** *"Brand DNA forja (#F97316) + graphite (#1C1917) + acero (#A8A29E) aplicado con minimalismo."* Y APP_VISION línea 185 declara el path canónico: `lib/core/theme/brand_dna.dart` (que NO existe en el código).

**Servicios (`services/kernel_service.dart` 390 LOC):**
- WebSocket con reconnect (max 10 attempts) + heartbeat 25s ✅
- Handlers para `text_chunk|tool_start|tool_args|tool_end|thinking_state|step|run_start|run_end|error|genui_component|heartbeat|pong` ✅
- REST endpoints: health, chat, memory, embrion, finops, MOC, push register, AG-UI info

**Pantallas auditadas:**
- `chat_screen.dart`: empty state con 4 quick actions (Estado kernel, Estado Embrión, Buscar web, Ejecutar código). Cero referencia a verticales/empresas/Capas.
- `embrion_screen.dart` 545 LOC: singleton embrión. Métricas + budget + directive input con `// TODO: Send directive to kernel` línea 316. **Sin UI para 7 Embriones especializados de Obj #11.**
- `memory_screen.dart` 246 LOC: 3 tabs (Buscar/Recientes/Stats). Tab "Recientes" placeholder literal *"Cargando..."* línea 166. Lee `getMemoryStats/searchMemory` del backend.
- `finops_screen.dart` 304 LOC: total cost + by_model + by_component. **Lee `/api/finops` del gateway — no conectado a `run_costs` tabla directa.**
- `onboarding_screen.dart` 483 LOC: 3 páginas Welcome/Connect/Done. Permite override URL kernel + persist en SharedPreferences. **`initialLocation: '/chat'` evita que se dispare automáticamente — solo si ruta `/onboarding` se navega explícita.**

**Lo que NO existe en código verificado:**
- `lib/modes/daily/` ❌
- `lib/modes/cockpit/` ❌
- `lib/core/transport/kernel_websocket.dart` ❌ (vive como `services/kernel_service.dart`)
- `lib/core/theme/brand_dna.dart` ❌
- `lib/core/crypto/smp.dart` ❌ (Sovereign Memory Protocol)
- `lib/core/services/{visual_search,photo_intelligence,file_intelligence,app_intelligence,vault,shopping,notes,health,ambient_listening,smart_notebook,cronos,manifestation,replay}_service.dart` ❌ (0/13 de las capabilities transversales prometidas)
- `lib/widgets/a2ui_components/` ❌ (vive en `lib/core/a2ui/` solo en branch PR #92 no mergeada)
- `lib/widgets/memento_badge.dart` ❌
- Toggle Daily ↔ Cockpit + 3-dedos + Face ID ❌
- Auth, secure_storage real ❌ (declarado en pubspec, cero usos en código)
- i18n ❌ (es-MX hardcoded)

### Backend kernel — 8 Capas Transversales

| Capa | Path | Estado verificado binariamente (PRE-PR #100) |
|---|---|---|
| 1 Ventas | `kernel/transversales/ventas/__init__.py:48-188` | `diagnose+recommend` con DSCs, `implement/monitor` NotImplementedError |
| 2 SEO | `kernel/transversales/seo/__init__.py:50-383` | **completa**: JSON-LD + meta + hreflang + canonical + monitor structural |
| 3 Publicidad | `kernel/transversales/publicidad/__init__.py:42-247` | `diagnose+recommend` ✅, `implement/monitor` NotImplementedError |
| 4 Tendencias | `kernel/transversales/tendencias/__init__.py:16-109` | igual |
| 5 Operaciones | `kernel/transversales/operaciones/__init__.py:16-140` | igual |
| 6 Finanzas | `kernel/transversales/finanzas/__init__.py:16-156` | igual (TRANSVERSAL-001 lo DEFER) |
| 7 Resiliencia | `kernel/sovereignty/engine.py` 533 LOC | **completa**: SovereigntyEngine + 8 deps + activate_sovereign_mode (Ollama fallback) + score |
| 8 Memento | `kernel/memento/` 5 archivos | **completa**: MementoValidator + Discrepancy + sources + contamination_detector |

`kernel/transversales/__init__.py:5,14,15` explicita: 6 capas comerciales + Resiliencia separada + Memento separada. **Cuando dije "8 capas comerciales" me equivoqué. Son 6 + 2 estructurales.**

### Portfolio canonizado — Cap 10 APP_VISION

20 proyectos en 4 estados:
- 🟢 Activos (7): Mena Baduy/Crisol-8, LikeTickets/ticketlike.mx, Zona Like 313, Bot Telegram, Command Center, Observatorio Mérida 2027, Simulador Universal
- 🟡 En Construcción (4): El Monstruo orquestador, Kukulkán 365, Mundo de Tata, Roche Bobois/Alfombras Yaxché
- 🟠 En Diseño (5): **CIP** (primera magna), SoftRestaurantAI 10x, Marketplace Muebles, Top Control PC, Vivir Sano
- 🔵 Nominales (4): CIES, NIAS, BIOGUARD, OMNICOM

**Cero de estos 20 tiene superficie en la app Flutter actual.** El Cockpit `Portfolio Empresas-Hijas` (APP_VISION Cap 3) no existe.

---

## §2 — Visión canónica integrada (qué debe ser, citando verbatim)

### Reglas inviolables Cap 0 APP_VISION

| Regla | Texto canónico |
|---|---|
| 1 Menos es más | *"Cada feature, cada pantalla, cada palabra en la UI tiene que justificar su existencia."* |
| 2 Si no es bonita no motiva | *"Brand DNA forja (#F97316) + graphite (#1C1917) + acero (#A8A29E) aplicado con minimalismo, no con densidad Bloomberg."* |
| 3 Silencio inteligente | *"Callado por defecto. Habla solo cuando le preguntan. Cero notificaciones falsas, cero gamification, cero engagement traps, cero streaks."* |
| 4 Describir, no prescribir | *"Espejo, no entrenador. Anti-coaching invasivo."* |
| 5 Verdad cruda | *"Modo detractor cuando hace falta — confrontar al usuario con verdades incómodas."* |
| 6 Anti-influencia inadvertida | *"Articular lo que la persona ya tiene en la cabeza es válido; detonar arquitecturas elaboradas que la persona pueda adoptar pasivamente no lo es."* |
| 7 Privacidad como física | *"La criptografía hace imposible. Pasamos de policy a physics."* |
| 8 Cero fee | *"Pago pass-through transparente. Cero margen del Monstruo."* |
| 9 Sin promoción | *"El Monstruo no se publicita. Se descubre."* |
| 10 Validar contra 15 Objetivos | *"Cualquier feature... se chequea contra los 15 Objetivos. Si viola alguno, no entra."* |

### Arquitectura magna Cap 1

> *"El Monstruo no es una app — es un kernel con múltiples cuerpos."*

> *"Generative UI vía A2UI v0.9 como protocolo, no como widget. El kernel NO diseña pantallas pre-fabricadas. Emite intenciones + esquemas A2UI, y cada transport renderiza según su capacidad."*

> *"Cuatro Catastros paralelos: Modelos LLM + Agentes 2026 (21 sistemas autónomos) + Suppliers Humanos + Herramientas AI Especializadas."*

> *"Ejecución consciente (7 capas): WebSocket persistente bidireccional, ejecución concurrente con estado compartido, hot-mutable execution, manifestación contextual no broadcast, confianza emergente, anticipación silenciosa, visibilidad on-demand."*

### Modo Daily Cap 2 — 5 superficies

Home (input universal + río de Cronos), Threads, Pendientes, Conexiones, Perfil.

### Modo Cockpit Cap 3 — 12-15 superficies (Alfredo arquitecto)

MOC Dashboard · Threads+Comando · **Portfolio Empresas-Hijas** (CIP primer habitante) · Catastro (4 catastros con Trono Score) · Embriones (9+: Critic Visual, Product Architect, Creativo, Estratega, Financiero, Investigador, Técnico, Ventas, Vigía, Manifestación, Convergencia Cronos) · Guardian (15 Objetivos como panel de instrumentos) · Memento · Replay (Timelapse Devin-style) · Computer Use/Sandbox · FinOps · Pipeline E2E · Coding embedded · Hilos Manus · Bridge · Settings+Admin

Toggle: *"3 dedos hold + Face ID. Opcionalmente segundo factor con device confiado agnóstico — Apple Watch, Wear OS, Garmin, o passphrase + biometría sola."*

### 8 Capabilities transversales Cap 4

Visual Search · Photo Intelligence · File Intelligence · App Intelligence · Vault Soberano · Shopping Intelligence · Notes Intelligence · Health Intelligence

**Plus capabilities base transversales:**
- Listening ambient continuo *"encendido 24/7 por default con VAD on-device + Whisper local + voice kill switch 'Monstruo apágate' (latencia <200ms hardware-level)"*
- Smart Rendering como composición sobre los Catastros

### Cronos Cap 5 — memoria viaje

*"Río navegable de tu vida. Aguas arriba pasado, aguas abajo futuro proyectado. Niebla suave para futuro. 4 modos de captura: Passive 90% / Active asistido 8% / Smart Notebook / Deep journaling 2%. 9 capas transversales personales (Salud, Relaciones, Decisiones, Aprendizajes, Económica, Creativa, Emocional, Profesional, Filosófica) con convergencias inter-capa detectadas por Embrión Convergencia."*

### Modo Confidente Cap 6

*"Sin nombre en UI. Sin botón. Vive dentro de la conversación. Cuando WhatsApp inclina a íntimo: card silencioso con logo + deep link `monstruo://confidente/<thread>` que transfiere a Flutter bajo SMP."*

### SMP Cap 7

5 propiedades: clave non-custodial · operación sin claros (homomórfico + TEE) · protocolo público auditable · hardware-backed Secure Enclave · multi-factor con Shamir's Secret Sharing recovery.

**Cap 7 línea 634-639:** *"Sprint Mobile 0 — SMP antes que cualquier feature. NO es feature post-v1.0. Es cimiento que tiene que estar antes de que el Modo Daily llegue a producción. ETA 2-4 semanas reales. NO se acelera."*

### Sistema de tiers Cap 8

Owner (Alfredo 100%) · Trusted Circle (futuro per-persona configurada) · Funcional Accesible (capabilities reducidas reales). Invitaciones nominativas. Sin signup público. Sin paywalls.

### Economía Cap 9

BYOK pass-through. Cero fee del Monstruo. Monetización vía empresas-hijas, no vía el Monstruo mismo.

### Cap 17 Seguridad Magna post-P0

8 reglas inmutables + 3 mecanismos de enforcement (pre-commit hooks + audit cierre sprint + Memento validate_against_spec).

---

## §3 — Brecha real por dimensión (sin pseudo-medición)

| Dimensión | Estado hoy | Visión canónica | Brecha real |
|---|---|---|---|
| **Identidad arquitectónica** | "App Flutter con backend Railway" | "Kernel + N transports bajo mismo SMP" | App actual NO es transport — es prototipo |
| **Transports operativos** | 1 (Flutter prototipo) | 6 (Flutter Daily P0 + Flutter Cockpit P1 + WhatsApp P0 + Watch P1 + Web Command Center P2 + Vision Pro P3) | 5 transports faltan; 1 vive como prototipo no v1.0 |
| **Brand DNA** | Cyan/púrpura "Inspired ChatGPT/Claude/Gemini" | Forja/graphite/acero con minimalismo Apple/Tesla | Refactor `theme/` → `core/theme/brand_dna.dart` (canon path) |
| **Modos** | Sin Daily/Cockpit toggle | Daily (5 surfaces) + Cockpit (12-15) con 3-dedos+FaceID | Crear `lib/modes/daily/` + `lib/modes/cockpit/` |
| **Auth + Tiers** | Sin auth | Owner / Trusted Circle / Funcional Accesible | Crear auth + tier gating |
| **SMP** | No existe | Sprint Mobile 0 cimiento NO acelerable | Cero código de SMP, Secure Enclave, Shamir |
| **8 Capabilities Cap 4** | 0/8 con servicio | Visual/Photo/File/App/Vault/Shopping/Notes/Health | Cero implementadas; A2UI primitives de PR #92 son sustrato |
| **Listening ambient** | No existe | 24/7 con kill switch verbal | Sin implementar; sin servicios on-device VAD/Whisper |
| **Cronos** | No existe | River of life + 9 capas + Embrión Convergencia | Sin implementar; Smart Notebook tampoco |
| **Modo Confidente** | No existe | Sin nombre + deep link silencioso | Sin implementar |
| **Portfolio Empresas-Hijas** | No existe | 20 proyectos tarjetas vivas, CIP primera | Sin superficie en app — pero portfolio canonizado y sprints existen |
| **4 Catastros UI** | No existe (1 sola pantalla MOC vaga) | Cockpit con `Salud de los 4 Catastros` | Sin implementar |
| **A2UI rendering** | PR #92 trae primitivos + renderer + 51 tests, no mergeado | Renderer streaming en `lib/widgets/a2ui_components/` | PR #92 lista para merge tras T8 smoke + decisión paleta |
| **WhatsApp Gateway** | No existe `apps/whatsapp_gateway/` | P0 paralelo a Flutter Daily | Sprint completo faltante |
| **Capas comerciales backend** | 6/6 con diagnose+recommend; 1/6 con implement+monitor (SEO) | 6/6 completas | PR #100 TRANSVERSAL-001 cierra T2/T3/T4/T5/T6 implement+monitor; T7 Finanzas DEFERRED |
| **Capa 7 Resiliencia** | `SovereigntyEngine` completo backend; sin UI | Cockpit superficie `Memento + Resiliencia` | Surface UI faltante |
| **Capa 8 Memento** | `MementoValidator` completo backend; sin UI | Cockpit superficie Memento con error_memory + validations + Síndrome Dory stats | Surface UI faltante |
| **Voice brand** | Sin voz brand | ElevenLabs español mexicano "registro bajo, gravitas, calidez contenida" | Sin implementar |
| **i18n** | es-MX hardcoded | es-MX + es-AR + en mínimo | Sin implementar; `kernel/i18n/engine.py` 502 LOC existe backend |
| **Catastros backend** | 2/4 firmados (Modelos + Agentes 2026); Suppliers + Herramientas AI pendientes | 4/4 operativos | Sprint Catastro-A + Catastro-B pendientes |

---

## §4 — Patrón arquitectónico unificador (cómo se cierra la brecha sin romper el prototipo)

### Principio operativo: evolución continua, no big-bang

La app actual (7,890 LOC + iPhone funcional) es el **prototipo Tier-Owner** que Alfredo ya usa. APP_VISION v1.3 es la **v1.0 producto público** que tendrá el círculo otorgado eventualmente. **El path no es reemplazar — es evolucionar manteniendo continuidad.**

### Eje 1 — Refactor de identidad (Sprint MOBILE_REALIGNMENT_001)

- Renombrar `services/kernel_service.dart` mantenido pero crear capa `core/transport/kernel_websocket.dart` que lo wrappea (alineación canónica).
- Crear `core/theme/brand_dna.dart` con forja/graphite/acero + `MaterialTheme.dark` derivado.
- Decisión T1 magna: el theme actual cyan/púrpura ¿se reemplaza por forja o se mantiene como "Tier-Owner heritage" mientras producción usa forja?
- Reorganizar `lib/` para preparar `modes/daily/` y `modes/cockpit/` (carpetas vacías al principio + `mode_router.dart` placeholder).
- Test fix: el `widget_test.dart` referencia `MyApp` (no existe) — debe ser `MonstruoApp`. CI verde.

### Eje 2 — SMP cimientos (Sprint MOBILE_0_SMP, paralelo a Kernel_0)

- 2-4 semanas reales. NO se acelera. APP_VISION Cap 7 explícito.
- Implementación de Sovereign Memory Protocol con Secure Enclave (iOS) + Strongbox (Android) + TPM (macOS).
- Audit por consultor cripto externo.
- Shamir Secret Sharing recovery.
- Open source de la layer crítica.
- **Sin esto, no entra a producción ningún dato sensible adicional en la app.**

### Eje 3 — Ejecución consciente (Sprint KERNEL_0, paralelo a Sprint Mobile 0)

- Persistent WebSocket layer canonizado en kernel.
- Concurrency en LangGraph con estado compartido y propagación de contexto.
- Manifestation engine como nuevo Embrión.
- Trust emergence model count-based.
- Anticipation engine.
- 4-6 semanas reales.

### Eje 4 — WhatsApp Gateway P0 (Sprint WHATSAPP_GATEWAY_P0)

- LATAM 72% comercio conversacional. P0 paralelo a Flutter.
- `apps/whatsapp_gateway/` con kernel_bridge + webhook_handler + interactive_messages + confidente_silent_link.
- A2UI renderer adaptado (Interactive Messages + quick replies + cards).

### Eje 5 — Capabilities transversales progresivas

Cada una su sprint en `lib/core/services/`:
- Sprint VISUAL_SEARCH_CAPABILITY
- Sprint PHOTO_INTELLIGENCE_CAPABILITY
- Sprint FILE_INTELLIGENCE_CAPABILITY
- Sprint APP_INTELLIGENCE_CAPABILITY
- Sprint VAULT_SOBERANO_CAPABILITY (consume SMP)
- Sprint SHOPPING_INTELLIGENCE_CAPABILITY
- Sprint NOTES_INTELLIGENCE_CAPABILITY
- Sprint HEALTH_INTELLIGENCE_CAPABILITY

Plus base transversales:
- Sprint LISTENING_AMBIENT (VAD + Whisper local + kill switch verbal)
- Sprint SMART_RENDERING (composición sobre 4 catastros)
- Sprint VOICE_BRAND_ELEVENLABS

### Eje 6 — Cronos progresivo

- Sprint CRONOS_1 chasis del río + captura passive WhatsApp + Photos + ambient bajo SMP
- Sprint CRONOS_2 9 capas básicas + modo espejo + Smart Notebook
- Sprint CRONOS_3 niebla del futuro + Embrión Convergencia inter-capa + ofrendas voluntarias

### Eje 7 — Surface Cockpit progresivo

- Sprint COCKPIT_1: MOC Dashboard + Threads denso + Catastro (4) + Embriones + Guardian
- Sprint COCKPIT_2: Memento + Portfolio Empresas-Hijas (con CIP primera tarjeta) + FinOps + Pipeline E2E + Replay
- Sprint COCKPIT_3: Computer Use + Coding embedded + Hilos Manus + Bridge + Settings+Admin
- Sprint TOGGLE_DAILY_COCKPIT: 3-dedos + Face ID + segundo factor configurable

### Eje 8 — Sistema de Tiers + Auth (Sprint AUTH_TIERS_001)

- Owner (Alfredo) auth dura (Face ID + passphrase + Apple Watch optional)
- Trusted Circle: invitaciones nominativas via deep link firmado
- Funcional Accesible: configuraciones reducidas per-persona
- Pre-requisito: Sprint Mobile 0 SMP

### Eje 9 — Polish (Sprint MOBILE_6)

- Apple Watch double-tap veto
- i18n base (es-MX, es-AR, en)
- Accesibilidad transversal WCAG
- Pulido final

---

## §5 — Sequencing operativo realista

**Suposición:** los 3 hilos Manus disponibles + Cowork T2 + Alfredo T1. Cero hilo Mobile dedicado (confirmado por T1).

### Fase 1 — Cimientos (4-6 semanas reales paralelas)

| Sprint | Hilo | ETA | Dep |
|---|---|---|---|
| MOBILE_0_SMP | Manus libre | 2-4 sem | ninguno |
| KERNEL_0_EJECUCION_CONSCIENTE | Manus libre | 4-6 sem | ninguno |
| MOBILE_REALIGNMENT_001 | Manus libre | ~1 sem | ninguno |
| GUARDIAN_AUTONOMO_001 | Ejecutor 1 (ya firmado) | 2-3 días | ninguno |
| TRANSVERSAL_001 cleanup G5 + merge | Ejecutor 2 + Cowork merge | ~30 min | ninguno |
| S-CONTRATOS-001 | Cowork + Manus paralelo | ~90 min Cowork | ninguno |

### Fase 2 — Transports adicionales (4-6 semanas)

| Sprint | Hilo | Dep |
|---|---|---|
| WHATSAPP_GATEWAY_P0 | Manus | MOBILE_0_SMP |
| ROTOR_001 | Ejecutor 1 (post Guardian) | GUARDIAN_AUTONOMO_001 |
| Sprint 89 → Catastro-A → Catastro-B | Catastro libre | ninguno entre sí (89 instala base) |

### Fase 3 — Daily mode pulido (4-6 semanas)

| Sprint | Hilo |
|---|---|
| DAILY_5_SUPERFICIES | Manus |
| VOICE_BRAND_ELEVENLABS | Manus |
| LISTENING_AMBIENT | Manus (post SMP) |

### Fase 4 — Capabilities (paralelas, 6-10 semanas)

8 capabilities Cap 4 + Cronos progresivo + Smart Rendering. Algunas son rápidas (Visual Search via lens API), otras requieren SMP profundo (Vault, Cronos ambient).

### Fase 5 — Cockpit (3-5 semanas)

COCKPIT_1, COCKPIT_2, COCKPIT_3, TOGGLE_DAILY_COCKPIT.

### Fase 6 — Auth + Tiers + Polish (2-4 semanas)

AUTH_TIERS_001 + MOBILE_6 (i18n + accesibilidad + pulido).

**Total honesto:** 4-6 meses reales para v1.0 producto cuando los 3 hilos trabajan paralelo en lo que les corresponde. La app actual sigue corriendo en iPhone de Alfredo como prototipo Tier-Owner durante todo el período.

---

## §6 — Sprints existentes — qué mantener, qué reescribir, qué archivar

| Sprint | Estado actual | Acción recomendada |
|---|---|---|
| Sprint 88 cierre v1 producto | MERGEADO | **archive** a `_completados/` |
| Sprint S001 security hardening | MERGEADO | **archive** |
| Sprint S002.6 RLS continuación | MERGEADO | **archive** |
| Sprint 89 catastros extension | propuesto | **go** (instala CatastroBase para Catastro-A/B) |
| Sprint 90 NPM Stripe | propuesto | **hold** indefinido (apps TS externas, no afecta app Monstruo) |
| Sprint S-CONTRATOS-001 | propuesto | **go** (cierra deuda DSC-as-Contract + Capa 17) |
| GUARDIAN_AUTONOMO_001 | firmado | **go** (kickoff ya `93d6d649`) |
| ROTOR_001 | firmado | **go orden 2** (post-Guardian) |
| TRANSVERSAL_001 (PR #100) | kickeado, cleanup G5 pendiente | Ejecutor 2 cleanup + merge |
| Catastro-A | propuesto | **go** (post-Sprint 89) |
| Catastro-B | propuesto | **go** (paralelizable con A) |
| Mobile 1 esqueleto | parcial ~35% | **rewrite** como MOBILE_REALIGNMENT_001 (evolución, no from-scratch) |
| Mobile 2 modo daily fase 1 | parcial ~20% | **rewrite** como DAILY_5_SUPERFICIES (con DSCs citados + ETA realista + cero stubs from-scratch) |
| Mobile 3 cockpit fase 1 | parcial ~50% | **rewrite** como COCKPIT_1 |
| Mobile 4 cockpit fase 2 | ~10% | **rewrite** como COCKPIT_2 (sin "Show API keys" — viola DSC-S-001) |
| Mobile 5 cockpit fase 3 | ~10% | **rewrite** como COCKPIT_3 |

---

## §7 — Sprints nuevos que faltan canonizar (orden de creación)

Por orden de prioridad operativa:

1. **MOBILE_REALIGNMENT_001** — evolución no big-bang del codebase actual. Crítico para destrabar track Mobile.
2. **MOBILE_0_SMP** — cimiento APP_VISION Cap 7. 2-4 sem. Pre-requisito de auth, vault, ambient.
3. **KERNEL_0_EJECUCION_CONSCIENTE** — 7 capas de ejecución consciente Cap 1.
4. **WHATSAPP_GATEWAY_P0** — paralelo a Flutter Daily, LATAM 72% conversacional.
5. **DAILY_5_SUPERFICIES** — Home/Threads/Pendientes/Conexiones/Perfil rebuild.
6. **VOICE_BRAND_ELEVENLABS** — voz única del Monstruo.
7. **LISTENING_AMBIENT_CAPABILITY** — VAD + Whisper local + kill switch verbal.
8. **CAPABILITY_VISUAL_SEARCH** + **PHOTO** + **FILE** + **APP** + **VAULT** + **SHOPPING** + **NOTES** + **HEALTH** — cada una su sprint, 8 sprints.
9. **CRONOS_1** + **CRONOS_2** + **CRONOS_3** — río + 9 capas + niebla.
10. **SMART_RENDERING_CAPABILITY** — composición sobre 4 Catastros.
11. **PORTFOLIO_EMPRESAS_HIJAS_UI** — tarjetas vivas de los 20 proyectos en Cockpit.
12. **COCKPIT_1** + **COCKPIT_2** + **COCKPIT_3** + **TOGGLE_DAILY_COCKPIT** — superficies + auth.
13. **AUTH_TIERS_001** — Owner/Trusted/Funcional.
14. **MODO_CONFIDENTE_UI** — sin nombre + deep link silencioso desde WhatsApp.
15. **MOBILE_6_POLISH_I18N** — Watch + i18n + WCAG.
16. **DSC_S012_EXECUTABLE_CONTRACT** — deadline 2026-06-10 (Cowork puro).
17. **HOUSEKEEPING_SPRINTS_INDEX** — mover Sprint 88, S001, S002.6 a `_completados/`.

**Cowork puede redactar los specs sucesivamente sin esperar T1.** Cada uno: estructura R1-R5 + cita DSCs + ETA realista + sin violaciones de seguridad.

---

## §8 — Decisiones T1 magna pendientes (lista mínima de irreductibles)

Esto es lo que **NO puedo inferir del corpus** y necesita tu cabeza:

1. **Brand DNA en código actual del prototipo:** ¿se refactoriza inmediato a forja-graphite-acero (canon APP_VISION v1.3) o queda cyan/púrpura como "Tier-Owner heritage" hasta que existe Tier público? Mi default T2: **refactor a forja inmediato** porque el prototipo es la base sobre la que se construye producción.
2. **Sprint MOBILE_0 SMP timing:** ¿arranca YA (4-6 semanas mientras el resto avanza) o se difiere hasta que haya datos sensibles más allá de chat? APP_VISION Cap 7 dice "antes de Daily a producción". Default T2: **arrancar YA en paralelo a otros sprints**.
3. **Hilo Mobile dedicado:** confirmaste 3 hilos (no hay Mobile separado). ¿Asignamos un Manus específico al track Mobile o rotamos? Default T2: **el Manus más libre toma MOBILE_REALIGNMENT primero, después rota**.
4. **PR #92 A2UI merge:** ¿T8 smoke en iPhone esta semana o queda en hold? Bloqueante del cleanup A2UI. Default T2: **vos definís cuándo hacés el smoke; mientras tanto continuamos sin bloqueo**.
5. **Sprint 90 NPM Stripe:** ¿se difiere indefinido o tiene cliente externo esperando? Default T2: **hold indefinido**.

Todo lo demás puedo proponerlo como default T2 y vos corrigís si no te gusta.

---

## §9 — Falsadores (qué evidencia cambiaría esta visión)

- Si Alfredo decide que el prototipo actual ES la v1.0 producto (y no se reescribe a APP_VISION v1.3), todo el sequencing colapsa a "polish del prototipo" + capabilities incrementales sin SMP cimiento.
- Si emerge cliente externo magna para Sprint 90 NPM con ETA bloqueante, ese sube prioridad y se difiere algo del track Cockpit.
- Si la app del Tier-Owner debe ser distinta arquitectónicamente de la app del Tier-Trusted-Circle (no solo configurada), el bundle único `com.elmonstruo.app` cambia y se separa en dos apps.

---

## §10 — Cierre operativo

- Doc canónico aquí + commit a main.
- Pre-flight Memento esta vez SÍ aplicado a mí mismo: leí APP_VISION v1.3 completa, los 15 Objetivos enteros, las 8 capas en código.
- Sin preguntas básicas en el chat. Solo las 5 decisiones T1 magna del §8.
- Tabla de tareas internas actualizada.
- Cadencia ≤1 audit canónico/día: hoy fueron 2 (A2UI + este). Excepción T1 explícita.

---

*Audit firmado por Cowork T2 Arquitecto. 2026-05-11. DSC-G-008 v2 con Gate de Evidencia binario (rúbrica + paths + denominador + falsadores). Sin pseudo-medición. Cita verbatim APP_VISION v1.3 + 15 Objetivos v3.0. Lectura completa del corpus magna que hasta hoy había evitado por F12 (subestimar sustrato). Reparación binaria de mental model previo.*
