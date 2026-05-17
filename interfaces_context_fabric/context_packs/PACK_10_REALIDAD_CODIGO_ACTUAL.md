# PACK 10 — Realidad código vs doctrina (drift binario)

> **Estado:** evidencia E1 + E2 cruzadas
> **Fuentes:** SRC-002 audit Cowork (§1 + §3) + SRC-019 código mobile + SRC-015 a2ui schema + SRC-016 brand_dna + SRC-018 design-tokens + grep transversal SRC-032

---

## Tesis del pack

Hay **drift binario sustantivo** entre lo que la doctrina canonizada dice que debe existir y lo que el código realmente implementa. Este pack es la herramienta forense para que ChatGPT NO diseñe sobre supuestos — sino sobre hechos. Cada drift se documenta con evidencia path:line.

---

## Drift de identidad arquitectónica

La doctrina (SRC-001 Cap 1, SRC-002 §0) dice que el Monstruo es un **kernel con N transports**. El código actual implementa una **app Flutter con backend Railway**, sin abstracciones de "transport" en ninguna capa. El módulo `apps/whatsapp_gateway/` declarado en estructura canónica no existe. La carpeta `apps/mobile/lib/core/transport/` no existe — el equivalente vive como `services/kernel_service.dart` con WebSocket directo.

**Severidad:** magna. Implica que el primer refactor (MOBILE_REALIGNMENT_001) debe **introducir el concepto "transport"** explícitamente en el código antes de que cualquier otro transport (WhatsApp, Watch) pueda construirse coherentemente.

---

## Drift de Brand DNA

La doctrina canonizada (SRC-001 Cap 0 regla 2, SRC-016 `kernel/brand/brand_dna.py`, SRC-018 `packages/design-tokens/`, SRC-022 DSC-MO-002) declara la paleta:

> Forja **#F97316** + Graphite **#1C1917** + Acero **#A8A29E**

El código real del transport Flutter (`apps/mobile/lib/core/theme/brand_dna.dart` líneas 10-56, verificado en audit D2 2026-05-17):

```dart
// línea 10: static const Color primary = Color(0xFF00E5FF);
// línea 12: static const Color secondary = Color(0xFFBB86FC);
// línea 34: static const Color borderFocused = Color(0xFF00E5FF);
// línea 44: gradient colors: [Color(0xFF00E5FF), Color(0xFFBB86FC)]
// línea 50: gradient colors: [Color(0xFF00E5FF), Color(0xFF00B8D4)]
// línea 56: gradient colors: [Color(0x4000E5FF), Color(0x40BB86FC)]
```

**Severidad nominal agregada:** el archivo se llama literalmente `brand_dna.dart` pero contiene **el anti-brand-DNA**. Es el caso más explícito de drift entre nomenclatura canónica y contenido. Cualquier desarrollador o auditor que abra este archivo asumirá que es la fuente de verdad — y heredará el drift.

**Esta paleta es contradicción binaria a tres fuentes canónicas independientes**: APP_VISION, brand_dna.py kernel, y DSC-MO-002 firmado. La paleta cyan/púrpura es prototipo Tier-Owner heredado de la primera versión y NO debe entrar a producción.

**Mitigación parcial:** existe `packages/design-tokens/flutter/monstruo_tokens.dart` que es el mirror canónico forja-graphite-acero — listo para que el transport mobile lo consuma. **NO se consume hoy.** El refactor está en MOBILE_REALIGNMENT_001 firmado pero NO ejecutado.

---

## Drift de modos Daily/Cockpit

La doctrina (SRC-001 Cap 1) declara la estructura de carpetas canónica con `lib/modes/daily/` (5 superficies) + `lib/modes/cockpit/` (12-15 superficies). El código real:

| Path canónico | Existe |
|---|---|
| `lib/modes/daily/` | ❌ |
| `lib/modes/cockpit/` | ❌ |
| `lib/core/state/mode_provider.dart` | ❌ |
| `lib/routing/mode_router.dart` | ❌ |
| Toggle 3-dedos + Face ID | ❌ |

Lo que sí existe es un `MaterialApp.router` con `GoRouter`, `initialLocation: '/chat'`, ShellRoute con 4 tabs (Chat/Sandbox/Files/Settings) + 5 rutas separadas (Embrion/Memory/FinOps/GenUI/MOC). Total 9 superficies que NO se mapean limpiamente ni a las 5 Daily ni a las 15 Cockpit.

**Severidad:** alta. La app funciona en iPhone de Alfredo como prototipo, pero la estructura mental "5+15" no está reflejada en routing — significa que **cada nueva feature se enchufa al esquema viejo y arrastra deuda**.

---

## Drift de capabilities transversales

La doctrina (SRC-001 Cap 4) declara 8 capabilities + 2 base = 10 servicios en `lib/core/services/`. El código real:

| Capability canónica | Existe |
|---|---|
| visual_search_service.dart | ❌ |
| photo_intelligence_service.dart | ❌ |
| file_intelligence_service.dart | ❌ |
| app_intelligence_service.dart | ❌ |
| vault_service.dart | ❌ |
| shopping_service.dart | ❌ |
| notes_service.dart | ❌ |
| health_service.dart | ❌ |
| ambient_listening_service.dart | ❌ |
| smart_notebook_service.dart | ❌ |
| cronos_service.dart | ❌ |
| manifestation_service.dart | ❌ |
| replay_service.dart | ❌ |

**0 de 13 servicios canónicos existen en el código del transport Flutter.** Lo que sí existe es `services/kernel_service.dart` con WebSocket genérico que debería ser `core/transport/kernel_websocket.dart`.

---

## Drift de SMP

La doctrina (SRC-001 Cap 7) firma SMP como **cimiento NO acelerable, pre-requisito de Daily a producción**. El código real:

| Componente SMP | Existe |
|---|---|
| `lib/core/crypto/smp.dart` | ❌ |
| `lib/core/crypto/secure_enclave_bridge.dart` | ❌ |
| `lib/core/crypto/on_device_transcription.dart` | ❌ |
| Shamir Secret Sharing | ❌ |
| Confidential computing TEE | ❌ |
| Auditoría open source de la layer crítica | ❌ |

**0 de 6 componentes SMP existen al 17-may.** El Sprint MOBILE_0_SMP está propuesto pero NO firmado para arrancar — es una de las 5 decisiones T1 magna pendientes (timing).

---

## Drift de superficies del Cockpit en Command Center

El Command Center PWA (SRC-020) implementa 7 superficies reales (`chat`, `finops`, `fleet`, `memory`, `runs`, `security`, `settings`). La doctrina del Cockpit (SRC-001 Cap 3) lista 15. El gap detectado:

| Superficie Cockpit canónica | ¿Existe en Command Center? |
|---|---|
| MOC Dashboard | ⚠️ no claro |
| Threads + Comando | ✅ chat |
| Portfolio Empresas-Hijas | ❌ |
| Catastro de los 4 | ❌ |
| Embriones | ❌ |
| Guardian | ❌ |
| Memento | ✅ memory (parcial) |
| Replay (Timelapse) | ❌ |
| Computer Use / Sandbox | ❌ |
| FinOps | ✅ finops |
| Pipeline E2E | ⚠️ runs (parcial) |
| Coding embedded | ❌ |
| Hilos Manus | ❌ |
| Bridge | ❌ |
| Settings + Admin | ✅ settings |
| Security | ✅ security (NO en lista canónica) |
| Fleet | ✅ fleet (NO en lista canónica) |

**Drift bidireccional:** el Command Center implementa **2 superficies que NO están en la lista canónica del Cockpit (Security, Fleet)** y **omite 8 superficies canónicas**. Esto es deuda de coherencia entre transports.

---

## Drift de A2UI

La doctrina (SRC-014 spec firmado) define A2UI v1.0 con whitelist de 16 componentes base + 3 especializados. El código real (SRC-015 `kernel/a2ui/schema.py`) implementa exactamente esa whitelist con validación Pydantic. **Cero drift en la layer kernel.**

**Audit D2 2026-05-17 confirma:**
- `kernel/a2ui/` directorio existe
- `kernel/agui_adapter.py` existe (AG-UI adapter ChatGPT)
- `bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md` firmado
- `bridge/cowork_to_manus_RESULTADO_AUDIT_A2UI_2026_05_11.md` audit Cowork
- `bridge/sprint_MOBILE_1B_A2UI_IMPLEMENTATION_2026_05_11.md` sprint propuesto

PR #92 trae primitivos + renderer + 51 tests para que el transport Flutter consuma A2UI. **NO está mergeado.** La decisión T1 magna #4 del audit Cowork pregunta si T8 (smoke en iPhone físico) se hace esta semana o no.

**Estado neto:** A2UI canónicamente firmado y implementado en kernel; aún NO consumido por el transport Flutter porque PR #92 está bloqueado.

---

## Drift de transports adicionales

| Transport | APP_VISION priority | Estado código |
|---|---|---|
| WhatsApp Gateway | P0 | ❌ NO existe |
| Apple Watch | P1 | ❌ NO existe |
| Vision Pro | P3 | ❌ NO existe (esperado) |

**3 de 6 transports canónicos NO tienen código.** El más crítico es WhatsApp porque es **paralelo a Flutter en prioridad** y porque LATAM es 72% comercio conversacional.

---

## Lo que sí está bien implementado

Para no caer en pesimismo, el corpus tiene piezas sólidas que ChatGPT debe respetar:

**Backend kernel** — 8 capas transversales tienen al menos `diagnose+recommend`, con SEO completa hasta `monitor`, Resiliencia y Memento implementadas en su totalidad. SovereigntyEngine 533 LOC con activate_sovereign_mode (Ollama fallback) operativo.

**Brand DNA backend** — `kernel/brand/brand_dna.py` operativo con validators, anti-pattern detection, forbidden generic tokens. `packages/design-tokens/` mirror multi-lenguaje listo para consumo.

**A2UI kernel** — schema.py con whitelist + Pydantic + validación + fallback_to_markdown.

**Catastros** — `kernel/catastros/interfaces.py` con 3 interfaces (Lookup, Search, Orchestration), AI-First or human-first priority, NoSuitableResourceError, tests pasando.

**Bot Telegram** — online en Railway, Sprint 27 cerrado.

**Command Center PWA** — online con login wall, 7 superficies funcionales en Next.js.

---

## Recomendación operativa para ChatGPT

El siguiente diseño arquitectónico que ChatGPT produzca debe:

1. **Asumir que el transport Flutter actual es prototipo no-canon** — NO diseñar features que cementen el theme cyan/púrpura. Cualquier nueva pantalla debe consumir `packages/design-tokens/flutter/monstruo_tokens.dart`.
2. **Tratar las 5 superficies Daily como construcción de cero** post-Realignment — no como evolución de la app actual.
3. **Tratar las 15 superficies Cockpit como construcción nueva**, NO como traducción de las 9 superficies actuales.
4. **Aceptar que el Command Center PWA tiene drift propio** que debe reconciliarse separadamente.
5. **Reconocer que SMP es bloqueante de Daily** — no se pueden diseñar capabilities profundas sin que SMP esté firmado para arrancar.
