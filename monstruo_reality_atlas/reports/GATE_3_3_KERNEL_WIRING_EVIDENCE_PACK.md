# GATE 3.3 KERNEL WIRING EVIDENCE PACK

> **Propósito:** Preparar evidencia real de código para que ChatGPT estudie Gate 3.3 (Wiring del Kernel) sin perder tiempo ni inventar.
>
> **⚠️ REGLAS DURAS PARA CHATGPT:**
> 1. Esto NO autoriza diseño.
> 2. Esto NO te convierte en Arquitecto Principal.
> 3. NO tocar APP_VISION.
> 4. NO cerrar PRE-IA.
> 5. NO crear sprint nuevo.
> 6. NO inventar endpoints.
>
> **Fuente de verdad:** Auditoría real del repositorio `el-monstruo` ejecutada el 2026-05-18.

---

## 1. Resumen Ejecutivo

El kernel (`kernel/main.py` con 3342 líneas) expone 21 routers y docenas de endpoints directos. La auditoría revela que:

- **A2UI** existe como schema estricto (`kernel/a2ui/schema.py`), pero el renderer en Flutter (`apps/mobile/lib/core/a2ui/a2ui_renderer.dart`) es un **placeholder**.
- **Memento** está completamente wired con endpoint `/v1/memento/validate` y validator instanciado en el lifespan del kernel.
- **Embrión** tiene su loop asíncrono (`EmbrionLoop`) arrancando en el lifespan de `main.py`. Expone endpoints de proposal, approve, reject y webhook de Telegram.
- **Write Policy / HITL** es real. Las proposals entran por `/v1/embrion/propose`, se aprueban por `/v1/embrion/approve/{id}` (o vía botones inline de Telegram) y un worker independiente (`kernel/runner/proposal_processor.py`) las ejecuta.
- **Catastros** NO son tablas visuales. Son un motor de recomendación expuesto en `/v1/catastro/recommend` y cargado en el lifespan del kernel.
- **Simulador Causal** y **Collective** existen como código (módulos importables) pero carecen de endpoints HTTP explícitos en `main.py`.

---

## 2. Evidencia de Endpoints Clave

| Módulo | Endpoint | Status | Consumidor Probable | Evidencia (Archivo:Línea) |
|---|---|---|---|---|
| **AG-UI** | `POST /v1/agui/run` | WIRED_HTTP | Flutter (`kernel_messenger.dart`) | `kernel/agui_adapter.py:114` |
| **Memento** | `POST /v1/memento/validate` | WIRED_HTTP | Command Center, Flutter | `kernel/memento_routes.py:170` |
| **Embrión (Propose)** | `POST /v1/embrion/propose` | WIRED_HTTP | Embrión, Flutter | `kernel/embrion_routes.py:852` |
| **Embrión (Approve)** | `POST /v1/embrion/approve/{id}` | WIRED_HTTP | Telegram, Command Center | `kernel/embrion_routes.py:1061` |
| **Embrión (Webhook)** | `POST /v1/embrion/telegram/webhook` | WIRED_HTTP | Telegram API | `kernel/embrion_routes.py:1240` |
| **Catastro (Recommend)** | `POST /v1/catastro/recommend` | WIRED_HTTP | Embrión, Command Center | `kernel/catastro/catastro_routes.py:165` |
| **Sabios** | `POST /v1/tools/consult_sabios` | WIRED_HTTP | Embrión, Command Center | `kernel/main.py:2689` |

---

## 3. Estado de Módulos (Wiring Real)

### A2UI
- **Schema:** `kernel/a2ui/schema.py` (Pydantic models estrictos).
- **Endpoint:** No hay endpoint exclusivo; viaja como payload `genui_component` en el SSE de `/v1/agui/run`.
- **Flutter:** `apps/mobile/lib/core/a2ui/a2ui_renderer.dart` existe pero es un placeholder visual (`"Generative UI Component"`).

### Write Policy y Side Effects
- **Proposal Processor:** Worker independiente (`kernel/runner/proposal_processor.py`) que procesa propuestas en estado `approved`.
- **Executor Registry:** `kernel/runner/executor_registry.py`. Por defecto, TODOS los side effects son **noop** (no hacen nada, solo loggean) a menos que se especifique `executor='real'`. `code_commit` está diferido.
- **Telegram Notifier:** `kernel/runner/telegram_notifier.py` envía teclados inline (`approve:abc-123`, `reject:abc-123`) para HITL.

### Catastros
- **Ubicación:** `kernel/catastro/catastro_routes.py` (incluido en `main.py` línea 1368).
- **Funcionamiento:** Se carga un `RecommendationEngine` en el `app.state` durante el startup. Expone endpoints para recomendar recursos. No es una tabla estática.

### Simulador Causal y Collective
- **Simulador:** `kernel/simulator/causal_simulator_v2.py` existe como módulo importable (Monte Carlo). NO se encontró endpoint HTTP directo.
- **Collective:** `kernel/collective/protocol.py` existe (pub/sub, debate, votación). NO se encontró endpoint HTTP directo.

### Embriones Especializados
- **Contradicción:** El directorio `kernel/embrion_specializations/` está vacío (solo `__init__.py`). Los embriones reales (estratega, financiero, investigador, etc.) viven en `kernel/embriones/`.

---

## 4. Contradicciones y Advertencias para ChatGPT

1. **A2UI es estricto en Python pero ciego en Flutter:** No asumas que el usuario ya puede interactuar con widgets generativos complejos. Flutter solo muestra un placeholder gris.
2. **Catastro es un API, no una UI:** No diseñes pantallas de "Lista de Catastros" para que el usuario elija. El Embrión elige vía API (`/v1/catastro/recommend`). La UI solo audita esa elección.
3. **Simulador y Collective están "desconectados" del exterior:** Tienen código profundo pero no exponen endpoints REST. Solo pueden ser usados internamente por el kernel o el Embrión.
4. **`embrion_specializations/` vs `embriones/`:** Si necesitas referenciar embriones específicos, usa `kernel/embriones/`, no `embrion_specializations/`.

---

## 5. Orden de Lectura Recomendado

Cuando Alfredo te pida estudiar Gate 3.3, enfócate en este orden:

1. `kernel/main.py` (lifespan y wiring de routers).
2. `kernel/embrion_routes.py` (flujo propose -> approve -> execute).
3. `kernel/runner/executor_registry.py` (noop vs real).
4. `kernel/catastro/catastro_routes.py` (Catastro como API).

---

## 6. Preguntas Irreducibles para Alfredo

*(Solo si realmente no se pueden resolver en el repo)*

1. ¿El Simulador Causal y Collective (Sabios) deben exponerse vía endpoints REST en `main.py` para Command Center, o son exclusivamente de uso interno del Embrión?
2. Dado que el renderer A2UI en Flutter es un placeholder, ¿debemos priorizar el wiring del renderer real en Flutter antes de que el Embrión empiece a emitir schemas complejos?
