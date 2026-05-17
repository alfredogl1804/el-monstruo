# DRIFT_FORENSIC_MAP — Drift de código vs doctrina con evidencia

> **Iteración 001 — INTERFACES-CONTEXT-FABRIC-001**
> **Generado:** 2026-05-17
> **Fuentes:** PACK_10_REALIDAD_CODIGO_ACTUAL.md + grep transversal `reports/fabric_grep_results.md` + audit Cowork SRC-002

---

## Sentido del mapa

Este mapa NO es opinión — es **evidencia path-line cruzada** entre lo que el corpus doctrinal afirma como canon y lo que el código realmente implementa. Cada drift se documenta con cuatro elementos: la pieza canónica que afirma cómo debería ser, la pieza de código que evidencia el estado real, la severidad binaria, y la implicación operativa para el siguiente sprint.

ChatGPT 5.5 Pro debe usar este mapa como **filtro de realidad** antes de proponer cualquier diseño nuevo. Si el diseño asume que existe algo que el mapa muestra como NO existente, el diseño está mal calibrado.

---

## DRIFT-UI-001 — Identidad arquitectónica "kernel + N transports"

**Canon (afirma):** SRC-001 Cap 1 declara "el Monstruo NO es una app — es un kernel con múltiples cuerpos. Hay N transports."

**Código (evidencia):** No existe la abstracción `transport` en ninguna capa de `apps/mobile/lib/`. La carpeta `apps/whatsapp_gateway/` declarada en SRC-001 Cap 1 NO existe en el repo. Los servicios viven como `services/kernel_service.dart` con WebSocket directo, sin abstracción de transport entre kernel y UI.

**Severidad:** MAGNA. Implica que MOBILE_REALIGNMENT_001 debe **introducir el concepto "transport" explícitamente** en código antes de que cualquier otro transport (WhatsApp, Watch) pueda construirse coherentemente.

**Implicación operativa:** ChatGPT diseñando arquitectura debe declarar `lib/core/transport/` como módulo nuevo y especificar cómo el transport Flutter consume el kernel a través de él, NO directamente.

---

## DRIFT-UI-002 — Brand DNA del transport Flutter

**Canon (afirma):** SRC-001 Cap 0 regla 2 + SRC-016 `kernel/brand/brand_dna.py` + SRC-018 `packages/design-tokens/` + SRC-022 DSC-MO-002 firmado declaran paleta canónica forja #F97316 + graphite #1C1917 + acero #A8A29E.

**Código (evidencia):** `apps/mobile/lib/theme/monstruo_theme.dart` línea 5 contiene comentario *"Inspired by ChatGPT, Claude, Gemini latest interfaces"* y declara primary `#00E5FF` (cyan), secondary `#BB86FC` (púrpura), tertiary `#64FFDA`.

**Severidad:** ALTA — viola tres fuentes canónicas independientes pero el código está en prototipo Tier-Owner, no en App Store.

**Mitigación parcial:** existe `packages/design-tokens/flutter/monstruo_tokens.dart` listo para consumo, NO se consume hoy.

**Implicación operativa:** todo sprint UI nuevo debe consumir el archivo de tokens canónico y NO el theme cyan/púrpura. Decisión T1-MAGNA-009 pendiente sobre cuándo se migra el theme completo.

---

## DRIFT-UI-003 — Estructura de carpetas modes/

**Canon (afirma):** SRC-001 Cap 1 declara estructura `lib/modes/daily/` (5 superficies) + `lib/modes/cockpit/` (12-15 superficies) + `lib/core/state/mode_provider.dart` + `lib/routing/mode_router.dart`.

**Código (evidencia):** Ninguna de esas rutas existe. Lo que sí existe es `MaterialApp.router` con `GoRouter`, `initialLocation: '/chat'`, ShellRoute con 4 tabs (Chat/Sandbox/Files/Settings) + 5 rutas separadas (Embrion/Memory/FinOps/GenUI/MOC). Total 9 superficies que NO se mapean ni a Daily ni a Cockpit canónicos.

**Severidad:** ALTA. La app funciona como prototipo, pero la estructura mental "5+15" no está reflejada — cada feature nueva se enchufa al esquema viejo.

**Implicación operativa:** MOBILE_REALIGNMENT_001 debe crear la estructura `modes/` y migrar las 9 superficies actuales a 5+15 canónicas, decidiendo qué se mantiene, qué se renombra, qué se difiere. Esta migración no es trivial.

---

## DRIFT-UI-004 — Capabilities transversales

**Canon (afirma):** SRC-001 Cap 4 declara 8 capabilities + 2 base = 10 servicios en `lib/core/services/` (visual_search, photo_intelligence, file_intelligence, app_intelligence, vault, shopping, notes, health, ambient_listening, smart_notebook, cronos, manifestation, replay).

**Código (evidencia):** **0 de 13 servicios canónicos existen.** Lo que sí existe es `services/kernel_service.dart` con WebSocket genérico.

**Severidad:** MAGNA. Las capabilities son el cuerpo funcional del Monstruo — sin ellas, las superficies son vacías.

**Implicación operativa:** cada capability requiere su propio sprint canonizado (sprints 8-15 del orden Cowork §7). Sin SMP arrancado (T1-MAGNA-002), las capabilities sensibles (Vault, Photos, Health) están bloqueadas.

---

## DRIFT-UI-005 — SMP cripto

**Canon (afirma):** SRC-001 Cap 7 firma SMP como cimiento NO acelerable. 5 propiedades canónicas (E2EE, zero-knowledge backend, local-first compute, Shamir, auditable open source). Sub-archivos canónicos: `lib/core/crypto/smp.dart`, `secure_enclave_bridge.dart`, `on_device_transcription.dart`.

**Código (evidencia):** **0 de 6 componentes SMP existen al 17-may.** El sprint MOBILE_0_SMP está propuesto pero NO firmado para arrancar (decisión T1-MAGNA-002).

**Severidad:** MAGNA. Bloquea capabilities sensibles + modo confidente + Vault Soberano + producción del Modo Daily.

---

## DRIFT-UI-006 — Cockpit en Command Center PWA

**Canon (afirma):** SRC-001 Cap 3 declara 15 superficies del Cockpit con nombres canónicos.

**Código (evidencia, github://alfredogl1804/el-monstruo-command-center):** 7 superficies reales en `src/app/(protected)/`: `chat`, `finops`, `fleet`, `memory`, `runs`, `security`, `settings`.

**Drift bidireccional:**

| Lado | Cuántas | Cuáles |
|---|---|---|
| Implementadas y canónicas | 5 | chat → C2 (parcial), finops → C10, memory → C7 (parcial), runs → C11 (parcial), settings → C15 |
| Implementadas pero fuera de canon | 2 | security, fleet |
| Canónicas pero NO implementadas | 10 | MOC, Portfolio, Catastro, Embriones, Guardian, Replay, Computer Use, Coding, Hilos Manus, Bridge |

**Severidad:** ALTA — drift bidireccional implica decisión de canonización (CONTRA-009).

---

## DRIFT-UI-007 — A2UI consumo

**Canon (afirma):** SRC-014 spec firmado declara A2UI v1.0 con whitelist de 16 componentes base + 3 especializados.

**Código (evidencia):** Layer kernel (`kernel/a2ui/schema.py`, SRC-015) implementa exactamente esa whitelist con validación Pydantic — **cero drift**. PR #92 trae primitivos + renderer + 51 tests para que el transport Flutter consuma A2UI — **NO está mergeado**, bloqueado por T8 smoke iPhone (T1-MAGNA-004).

**Severidad:** MEDIA — el canon está bien implementado en kernel, falta solo el merge para que el transport consuma.

---

## DRIFT-UI-008 — Transports faltantes

**Canon (afirma):** SRC-001 Cap 1 lista 6 transports canónicos.

**Código (evidencia):**

| Transport | Estado |
|---|---|
| Bot Telegram | ONLINE, OK |
| App Flutter | PROTOTIPO con drift de tema y estructura |
| Command Center PWA | ONLINE con drift de superficies |
| WhatsApp Gateway | NO existe (P0 según canon) |
| Apple Watch | NO existe (P1 según canon) |
| La Forja web | Branch sprint, NO en main |
| Vision Pro | NO existe (P3 según canon, esperado) |

**Severidad:** ALTA — 3 de 6 transports canónicos sin código. El más crítico es WhatsApp (P0).

---

## DRIFT-UI-009 — Cronos como módulo

**Canon (afirma):** SRC-001 Cap 5 firma Cronos como río de vida con 4 modos de captura, 9 capas transversales, niebla del futuro.

**Código (evidencia):** `kernel/cronos/` NO existe. `apps/mobile/lib/core/services/cronos_service.dart` NO existe. Sub-río 9 capas NO existe. Embrión Convergencia NO existe como módulo dedicado. Niebla del futuro NO existe.

**Severidad:** MAGNA — Cronos es una de las piezas magna del valor del Monstruo (apuesta civilizacional 30 años) y NO está implementado en ningún lugar al 17-may.

---

## DRIFT-DOCTRINAL-001 — Cronos homonimia

**Canon (afirma):** Cronos = río de vida (SRC-001 Cap 5).

**Otros usos (evidencia):** Skill `automation-and-scheduling` usa "Cronos" para cron scheduler. Algunos audits Cowork usan "Cronos" para "memoria temporal" sin la metáfora del río.

**Severidad:** ALTA — homonimia genera ambigüedad en cualquier feature que mencione "Cronos".

**Implicación operativa:** ChatGPT debe firmar canonización A1 = Cronos (río) y renombrar A2 a "Scheduler" o "Cron Engine".

---

## DRIFT-DOCTRINAL-002 — Schema-First doctrinal

**Canon (afirma):** la skill `interfaces-monstruo-doctrina` lista Schema-First como doctrina embrionaria.

**Evidencia:** **1 hit en grep transversal** — `discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-005_sse_obligatorio_endpoints_llm.md`. Es la única canonización formal del concepto.

**Severidad:** MEDIA — la doctrina existe en germinal en un solo DSC. Cualquier referencia a "Schema-First" en sprints futuros debe citar DSC-LF-005 o canonizar más doctrina.

---

## DRIFT-DOCTRINAL-003 — Calm Tech una sola fuente

**Canon (afirma):** Calm Tech es Acto 2.

**Evidencia:** **1 hit en grep transversal** — `CANON_METODOLOGIAS_PRODUCTIVIDAD_2026.md` (SRC-005). El Acto 2 entero vive en UN documento.

**Severidad:** ALTA — fragilidad doctrinal. Si SRC-005 se modifica o pierde, el Acto 2 desaparece. Necesita ser citado y referenciado en más documentos para tener resiliencia.

**Implicación operativa:** ChatGPT en iter 002 debe escribir audit que cite §9.F en al menos 3 documentos canónicos adicionales (audit Cowork, sprint nuevo, DSC magno) para distribuir el peso doctrinal.

---

## DRIFT-DOCTRINAL-004 — AI-First Living no commiteado

**Canon (afirma):** Skill `interfaces-monstruo-doctrina` lo lista como hipótesis naciente.

**Evidencia:** **1 hit relevante en código** (`kernel/catastros/interfaces.py` — solo como flag de prioridad). 0 hits "Soberanía Contextual". 0 docs canónicos en `docs/`.

**Severidad:** MEDIA — la cita-detonante de Alfredo (2026-05-16) merece commit canónico al repo. Sin él, vive solo en hilos y se pierde con compactación.

**Implicación operativa:** decisión T1-MAGNA-007 pendiente — ChatGPT debe articular consecuencias.

---

## DRIFT-DOCTRINAL-005 — Transport Cero verbal

**Canon (afirma):** Skill `interfaces-monstruo-doctrina` lo lista como hipótesis naciente.

**Evidencia:** **0 hits en grep**. Vive solo verbalmente en hilos.

**Severidad:** MAGNA si se canoniza — invierte prioridad de los 6 transports.

---

## Síntesis para ChatGPT

El drift más severo es **MAGNA en 3 frentes simultáneos**: identidad arquitectónica kernel+N transports (DRIFT-UI-001), capabilities transversales 0/13 (DRIFT-UI-004), Cronos sin implementar (DRIFT-UI-009). Estos 3 drifts juntos significan que el cuerpo funcional del Monstruo NO existe en código — solo en doctrina.

El drift más urgente operativamente es **MOBILE_REALIGNMENT_001 firmado pero NO ejecutado** (DRIFT-UI-002 y DRIFT-UI-003 dependen de él). Cada día que pasa sin ejecutar Realignment, los nuevos commits al transport Flutter agregan deuda al theme cyan/púrpura y al routing viejo.

El drift más sutil es **doctrinal-003 (Calm Tech una sola fuente)**: si SRC-005 desaparece, el Acto 2 entero se evapora. Esto es fragilidad de canon, no de código, pero es igualmente urgente.
