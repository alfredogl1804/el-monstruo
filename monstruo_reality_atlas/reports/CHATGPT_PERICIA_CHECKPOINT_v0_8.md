# CHATGPT PERICIA CHECKPOINT v0.8

> **Propósito:** persistir el estado actual de pericia de ChatGPT 5.5 Pro sobre El Monstruo para evitar pérdida por compactación, drift o re-interpretación futura.
>
> **Generado por:** Manus, por instrucción de Alfredo Góngora, 2026-05-18.
>
> **Estado:** blindaje. NO diseñar, NO canonizar, NO corregir Atlas todavía salvo notas de drift.
>
> **Si abrís este archivo en hilo nuevo:** leelo completo antes de proponer cualquier cosa. Después leé `CHATGPT_PERICIA_STATE_v0_8.json` y ejecutá `PERICIA_TEST_v0_8.md`. Si fallás el test, NO diseñes.

---

## 1. Estado general

ChatGPT está en fase:

```
ARQUITECTO_EN_CERTIFICACION
NO_ARQUITECTO_PRINCIPAL_TODAVIA
```

### Nivel aproximado por dominio

| Dominio | Pericia |
|---|---|
| Atlas / Fabric | 80% |
| APP_VISION / AGENTS | 80% |
| Flutter real (apps/mobile) | 70% |
| Command Center real | 50% |
| Kernel A2UI / Memento | 55% |
| Embriones / Budget / Self-Verifier / Write Policy | 65% |
| Catastros | 55% |
| Simulador causal | 55% |
| Bridge inter-hilos | 45% |
| **Pericia total estimada** | **68%** |

---

## 2. Fuentes principales leídas

```
monstruo_reality_atlas/*
interfaces_context_fabric/maps/*
interfaces_context_fabric/context_packs/PACK_03_AI_FIRST_LIVING.md
interfaces_context_fabric/context_packs/PACK_04_CRONOS_RIO_DE_VIDA.md
interfaces_context_fabric/context_packs/PACK_05_METODOLOGIAS_PRODUCTIVIDAD.md
interfaces_context_fabric/context_packs/PACK_06_RELOJ_SUIZO_ENGRANAJE.md
interfaces_context_fabric/context_packs/PACK_12_RIO_DE_LA_VIDA_EXISTING_AUDIT.md
interfaces_context_fabric/raw_rescues/alfredo_pre_ia_checkpoint_2020_2021_DRAFT.md
docs/EL_MONSTRUO_APP_VISION_v1.md
AGENTS.md
apps/mobile/lib/main.dart
apps/mobile/lib/app.dart
apps/mobile/lib/routing/mode_router.dart
apps/mobile/lib/core/state/mode_provider.dart
apps/mobile/lib/widgets/shell_scaffold.dart
apps/mobile/lib/features/chat/*
apps/mobile/lib/features/chat/widgets/typing_indicator.dart
apps/mobile/lib/core/mensajeros/kernel_messenger.dart
apps/mobile/lib/core/config.dart
apps/mobile/lib/modes/daily/*
apps/mobile/lib/modes/cockpit/*
apps/mobile/lib/core/a2ui/*
kernel/a2ui/*
kernel/memento/*
kernel/embrion_loop.py
kernel/embrion_budget.py
kernel/embrion_self_verifier.py
kernel/embrion_write_policy.py
kernel/runner/proposal_processor.py
kernel/runner/executor_registry.py
kernel/catastros/*
kernel/causal_decomposer.py
memory/causal_kb.py
kernel/simulator/causal_simulator_v2.py
bridge/cowork_to_manus.md
```

---

## 3. Verdades confirmadas

### 3.1 Monstruo no es app

El Monstruo = **kernel + múltiples transports**. Flutter, Command Center, Telegram, WhatsApp, Watch / Vision Pro son cuerpos del mismo núcleo, no aplicaciones independientes.

### 3.2 Flutter

Existe chasis Daily / Cockpit real con piezas funcionales:

- `mode_provider`
- `mode_router`
- `ShellScaffold`
- Daily bottom nav
- Cockpit drawer
- AG-UI Gateway client
- Chat funcional
- ThinkingIndicator
- A2UI screen parcial

Pero quedan brechas concretas:

- Home es proxy de ChatScreen, NO la Home Daily canónica
- Threads / Pendientes / Conexiones son placeholders
- Perfil es proxy a Settings
- Cockpit es parcial
- A2UI renderer es placeholder
- Brand DNA está en drift cyan / púrpura

### 3.3 Command Center

Existe como consola parcial, no Cockpit completo. Nav real detectado: **Chat, Runs, FinOps, Security, Memory, Settings**. Theme en drift, no Forja / Graphite / Acero.

### 3.4 A2UI

A2UI existe como **schema Pydantic real** en kernel. Flutter tiene pantalla A2UI, pero el renderer todavía es placeholder.

### 3.5 Memento

Memento existe como **validator importable real**. NO asumir endpoint HTTP completo sin verificar.

### 3.6 Cronos / Río de Vida

Cronos / River of Life / Modo Cripta están **canonizados / doctrinales** en APP_VISION cap 5. NO hay `kernel/cronos` leído / existente en este pase. NO rediseñar "Cronista Familiar"; es **alias de Cronos / Modo Cripta**.

### 3.7 SMP

SMP es **Sovereign Memory Plane**, cimiento criptográfico, no idea nueva. "Privacidad por Imposibilidad" es su función. NO se vio implementación real en código en este pase. NO tocar datos sensibles sin resolver SMP.

### 3.8 Embriones

Embrión existe como loop autónomo real con:

- purpose filter
- judge
- silence score
- HITL escalation
- FCS
- budget
- self-verifier
- sabios / radar
- piezas Reloj Suizo como Escape / Espiral por flags

### 3.9 Budget

Budget Tracker existe. Controla cap por latido, presupuesto diario, registro post-flight y escalación HITL.

### 3.10 Self-Verifier

Existe con 3 decisiones:

- `PURPOSE`
- `NOVELTY`
- `VERIFIABLE`

VERIFIABLE **exige un artefacto/acción verificable real** (commit, archivo, URL, tabla) para evitar eco o repetición vacía, no es fact-checking genérico.

### 3.11 Write Policy + HITL

Existe cola de proposals con estados:

```
pending → approved → executing → executed | failed | rejected | expired
```

Incluye idempotency, approve / reject, notify_hitl, execute_next.

### 3.12 Proposal Processor

Existe como **worker independiente** que expira y ejecuta proposals aprobadas.

### 3.13 Executor Registry

Por defecto los executors son **noop**. Side effects reales requieren payload `executor='real'`. `code_commit` está diferido. `db_write` y `external_api_call` pueden ser reales bajo opt-in.

### 3.14 Catastros

Existen 4 Catastros canónicos:

- `modelos_llm`
- `agentes_2026`
- `herramientas_ai`
- `suppliers_humanos`

Y 3 interfaces:

- `lookup`
- `search`
- `orchestration`

Catastro **NO es inventario visual**; es **motor de selección de recursos**.

### 3.15 Simulador causal

Existe:

- `CausalDecomposer`
- `CausalKnowledgeBase`
- `CausalSimulatorV2` Monte Carlo

Falta verificar endpoints / UI / uso real.

### 3.16 Bridge inter-hilos

Bridge existe como **sistema operativo social**:

- append-only
- versionado
- Cowork audita
- Manus ejecuta
- Alfredo firma
- archivo activo + archive por época

---

## 4. Errores corregidos de ChatGPT

- NO volver a proponer "Cronista Familiar" como módulo.
- NO tratar "Privacidad por Imposibilidad" como canon nuevo; es función de SMP.
- NO tratar Transport Cero como canon; es hipótesis naciente.
- NO asumir que Home canónica existe porque `/home` existe (y no mezclar Cockpit summary con Home Daily).
- NO asumir Memento endpoint completo porque validator existe.
- NO asumir que A2UI renderer existe porque schema existe.
- NO asumir que Acto 1 y Acto 2 se contradicen sin matiz: dirección provisional = **Acto 2 contiene Acto 1** (la invisibilidad gobierna, 20 superficies son backstops).
- NO diseñar interfaz final antes de conocer sustrato inteligente.

---

## 5. Rescates T1 vivos de Alfredo

- **Entrada Universal Inteligente / Boca del Monstruo.**
- Toda captura debe conectar con lo que tenga que conectar.
- **Ley de Persistencia por Conexión.**
- Solo debe perderse lo que realmente no sirve.
- **Federación Soberana de Contexto** entre Monstruos.
- **Espacio Vital Soberano / Mundo Paralelo Soberano.**
- AI-First Living sigue como **hipótesis viva, no canon**.
- Bloque pre-IA sigue **abierto**; NO cerrar hasta literal `CIERRE BLOQUE PRE-IA`.

---

## 6. Contradicciones activas

- Flutter chasis real vs Daily real incompleto.
- Brand DNA canon vs código cyan / púrpura.
- A2UI schema real vs renderer placeholder.
- Cronos canonizado vs código vacío.
- SMP cimiento vs implementación ausente.
- Memento validator real vs endpoint no confirmado.
- Command Center producción parcial vs Cockpit canon 12-15.
- Autonomía del Embrión vs executors noop por default.
- Catastro como motor de decisión vs posible UI de inventario.
- Simulador causal real vs UI / endpoint no verificado.

---

## 7. Lista de cosas que ChatGPT NO debe rediseñar

Espejo del bloque `do_not_redesign` en `CHATGPT_PERICIA_STATE_v0_8.json`. Cualquier hilo nuevo que vaya a proponer módulos debe revisar primero esta lista.

| ID | Concepto propuesto | Razón canónica |
|---|---|---|
| DNR-001 | Cronista Familiar / Herencia Narrativa / Legacy Capture | Alias de `cronos_modo_cripta`. Canonizado en APP_VISION cap 5. NO crear módulo nuevo. |
| DNR-002 | Privacidad por Imposibilidad como canon nuevo | Es función de SMP (Sovereign Memory Plane). NO promover a doctrina independiente. |
| DNR-003 | Transport Cero como canon firmado | Sigue como hipótesis naciente. 0 hits sustantivos en repo. NO firmar. |
| DNR-004 | Home canónica = `/home` existente | El `/home` actual es proxy de ChatScreen. La Home Daily canónica debe tener contexto/threads, no resúmenes de Cockpit. |
| DNR-005 | Memento endpoint HTTP completo | Solo el `MementoValidator` está confirmado importable. Endpoint sin verificar. |
| DNR-006 | A2UI renderer ya existente | Solo el schema Pydantic está confirmado. Renderer real es placeholder. |
| DNR-007 | Acto 1 vs Acto 2 como contradicción binaria | Dirección provisional firmada por Cowork: **Acto 2 contiene Acto 1** (latencia gobierna, superficies son backstops). |
| DNR-008 | Hipótesis pre-IA-001 a pre-IA-010 antes del cierre | Bloque pre-IA sigue abierto. NO firmar canon hasta literal `CIERRE BLOQUE PRE-IA` de Alfredo. |

### Regla operativa

Si ChatGPT detecta una propuesta nueva que cae en cualquiera de estos 8 patrones, debe:

1. NO seguir adelante con la propuesta como canon nuevo.
2. Mapear la propuesta al concept_id canónico que ya existe (vía `monstruo_reality_atlas/07_ALIAS_LEDGER.yaml`).
3. Si no hay concept_id existente, marcar la propuesta como `HIPOTESIS_T1_REQUIERE_AUDIT` y NO firmar hasta que Alfredo lo autorice.

---

## 8. Próximo gate

**Gate 3.3 — Wiring real en `kernel/main.py`**

Leer:

- `kernel/main.py`
- rutas AG-UI
- rutas memory
- rutas embrion
- rutas proposal / HITL
- rutas finops
- rutas moc
- collective / Sabios
- embrion_specializations

Objetivo: saber qué módulos están **realmente conectados al API** y qué solo existe como módulo importable.

---

## 9. Regla de continuidad

Si ChatGPT se compacta o abre hilo nuevo:

1. Leer este checkpoint.
2. Leer el JSON state (`CHATGPT_PERICIA_STATE_v0_8.json`).
3. Ejecutar `PERICIA_TEST_v0_8.md`.
4. Si falla el test (puntaje < 18/20), **NO diseñar**. Releer hasta que pase.
5. Si pasa el test, continuar exactamente desde el Próximo Gate (§8).

### Bloqueo explícito

- NO escribir APP_VISION v1.4 hasta que Alfredo lo autorice.
- NO firmar sprints CRONOS_1 / CRONOS_2 / CRONOS_3 / AUTH_TIERS_001 hasta que Alfredo los firme.
- NO ejecutar `CIERRE BLOQUE PRE-IA` hasta que Alfredo lo escriba literal.
- NO canonizar las 10 hipótesis pre-IA hasta el cierre del bloque.
- NO rediseñar nada de la lista §7.
