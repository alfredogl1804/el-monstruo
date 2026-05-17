# PACK 07 — Transports UI (los 6 cuerpos canonizados + Transport Cero)

> **Estado:** CANON_VIGENTE para los 6 transports. **Transport Cero** = HIPOTESIS_NACIENTE.
> **Fuente magna:** SRC-021 (skill `interfaces-monstruo-doctrina`) + SRC-002 (audit Cowork) + SRC-001 Cap 1

---

## Principio doctrinal

> *"El Monstruo NO es una app — es un kernel con múltiples cuerpos."* (SRC-002 §0, SRC-001 Cap 1)

Hay UN cerebro central + N transports. Cada transport renderiza A2UI generative UI según su capacidad. Ningún transport es "la app del Monstruo". Cada uno es ciudadano de primera clase.

---

## Inventario binario al 17-may-2026

### Transport 1 — Bot Telegram (preexistente)

- **Path:** `bot_v3.py` (path por reverificar — la skill detectó posible drift)
- **Bot:** `@MounstroOC_bot`
- **Plataforma:** Railway service `bot-telegram`
- **Estado:** 🟢 **ONLINE Sprint 27**
- **Prioridad APP_VISION:** preexistente (no recategorizado)
- **Capacidad UI:** texto + cards Telegram + quick replies + voice notes
- **A2UI compat:** parcial (componentes simples sí, complejos NO)
- **Skill canónico:** `el-monstruo-bot`

### Transport 2 — App Flutter

- **Path:** `apps/mobile/`
- **52 archivos `.dart`** al 16-may (vs 33 del audit Cowork 11-may → +19 en 5 días)
- **Plataforma:** iPhone físico de Alfredo, NO en App Store
- **Estado:** 🟡 **PROTOTIPO Tier-Owner**
- **Prioridad APP_VISION:** **P0 paralelo a WhatsApp**
- **Capacidad UI:** la más rica — A2UI generative completo, voz, cámara, gestos, biometría
- **Drift documentado:**
  - Theme actual cyan #00E5FF + púrpura #BB86FC ("Inspired ChatGPT/Claude/Gemini") → **VIOLA brand DNA forja+graphite+acero**
  - 0/13 capabilities transversales implementadas
  - 0/5 superficies Daily
  - 0/15 superficies Cockpit
  - SMP NO existe
  - Toggle Daily↔Cockpit NO existe
- **Sprint canónico bloqueante:** `MOBILE_REALIGNMENT_001` (SRC-006, firmado T1, NO ejecutado)

### Transport 3 — Command Center PWA

- **Repo:** `el-monstruo-command-center` (separado en GitHub, privado)
- **Stack:** Next.js + TypeScript + Tailwind + Drizzle
- **Plataforma:** Railway, login wall
- **Estado:** 🟢 **ONLINE**
- **Prioridad APP_VISION:** **P1** post-app
- **Superficies reales detectadas (`src/app/(protected)/`):**
  1. chat
  2. finops
  3. fleet
  4. memory
  5. runs
  6. security
  7. settings
- **Drift binario:** **7 superficies vs 15 del Cockpit canónico Acto 1**. Subset implementado, falta 8.

### Transport 4 — WhatsApp Gateway

- **Path:** `apps/whatsapp_gateway/` (estructura canónica de SRC-001 Cap 1)
- **Estado:** ❌ **NO existe código**
- **Prioridad APP_VISION:** **P0 paralelo a Flutter** (LATAM 72% comercio conversacional)
- **Sprint canónico:** WHATSAPP_GATEWAY_P0 (faltan canonizar specs)
- **Capacidad UI prevista:** Interactive Messages + quick replies + cards + deep link silencioso del logo (Modo Confidente, SRC-001 Cap 6)
- **A2UI subset adaptado** para los componentes que WhatsApp soporta

### Transport 5 — Apple Watch

- **Path:** N/A
- **Estado:** ❌ **NO existe código**
- **Prioridad APP_VISION:** **P1**
- **Capacidad UI prevista:**
  - Double-tap como **veto táctico** del agente (interrumpir sin sacar iPhone)
  - Indicación visual sutil de estado del Monstruo
  - Voz brand mínima
  - Notificaciones contextuales
- **Sprint:** sin canonizar

### Transport 6 — La Forja web

- **Path:** `apps/la-forja/` (85 archivos versionados según skill)
- **Estado:** 🟡 Sprint LA-FORJA-001 v3.2 firmado 15-may, ejecución parcial en branch `sprint/la-forja-001`
- **Prioridad APP_VISION:** **NO listado** (es proyecto-hijo "Cliente Cero")
- **Naturaleza:** vidriera pública del Monstruo, no transport del kernel pero **interfaz pública crítica**
- **DSC asociado:** DSC-LF-005 (SSE obligatorio endpoints LLM, SRC-023 — único hit "Schema-First" del corpus)

---

## Transport Cero (HIPOTESIS_NACIENTE — NO firmado)

### El concepto

> *"El transport ideal es el que no existe — la IA actúa sin que el usuario tenga que abrir nada."*

Mencionado verbalmente por Alfredo en chat con Manus, **NO commiteado al repo**. 0 hits en grep. Vive solo en hilos.

Implicación: si Acto 2 Calm Tech se canoniza, **Transport Cero es el transport por defecto**. Los 6 transports son backstops para cuando el ambient falla.

### Mecanismo

- Listening ambient continuo captura intención
- Embrión Diagnóstico decide si la intención requiere acción
- SI requiere → ejecuta automáticamente bajo Confianza Emergente (SRC-001 Cap 1, 7 capas ejecución consciente)
- Output: notificación silenciosa O voz mínima O acción visible solo si HITL exigido
- **Cero superficie abierta**

### Conflicto con Acto 1

- Acto 1 dice: "20 superficies excelentes son el éxito"
- Transport Cero dice: "ninguna superficie es el éxito"
- Sin firma T1, los sprints no saben a cuál servir.

---

## Tabla resumen

| # | Transport | APP_VISION priority | Estado | Drift |
|---|---|---|---|---|
| 0 | Transport Cero | NO firmado | HIPOTESIS_NACIENTE | sin spec |
| 1 | Bot Telegram | preexistente | 🟢 online | path `bot_v3.py` por verificar |
| 2 | App Flutter | P0 | 🟡 prototipo | brand DNA violado, 0/20 superficies |
| 3 | Command Center PWA | P1 | 🟢 online | 7/15 superficies Cockpit |
| 4 | WhatsApp Gateway | P0 | ❌ NO existe | sprint sin canonizar |
| 5 | Apple Watch | P1 | ❌ NO existe | sprint sin canonizar |
| 6 | La Forja web | proyecto-hijo | 🟡 firmado v3.2 | NO en main |

---

## Decisiones pendientes para ChatGPT

1. **¿Transport Cero se canoniza?** Si sí, requiere spec magna + impacto en sequencing de sprints.
2. **¿Apple Watch sube a P0?** Si Acto 2 Calm Tech gana, Watch es transport prioritario (notif silenciosa + double-tap veto).
3. **Web simple** (no Command Center, no La Forja) — ¿hay un 7º transport "Web Daily" para no-iPhone-users? APP_VISION no prioriza Web; ChatGPT debe firmar si esto cambia.
4. **Vision Pro** — APP_VISION lo lista P3 v1.2+. ¿Sigue siendo P3 o se difiere indefinidamente?
