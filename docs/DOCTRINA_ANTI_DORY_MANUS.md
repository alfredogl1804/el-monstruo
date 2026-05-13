# Doctrina Anti-Dory: Continuidad de Memoria para Hilos Efímeros (Manus)

> **Fecha:** 2026-05-13
> **Autor:** Manus (Hilo Principal)
> **Estado:** Fase 0 (Prerrequisitos Kernel) Completada. Fase 1 (Wiring Manus) Planificada.
> **Alineación:** Objetivo Maestro #15 (Capa Memento), L471-480 de `docs/EL_MONSTRUO_15_OBJETIVOS_MAESTROS.md`.

## 1. El Diagnóstico Honesto: Dos "Dorys" Distintos

Durante el sprint del 12-13 de mayo de 2026, se detectó una confusión de scope crítica. "Matar a Dory" (eliminar la amnesia del sistema) significa cosas distintas dependiendo de qué actor estemos mirando.

### A. Dory-Kernel (El Monstruo en Railway)
El kernel en producción sufría de amnesia porque su búsqueda semántica estaba *stubbed* (simulada) y su `SovereignCheckpointStore` no estaba instanciado.
**Estado:** Resuelto en **Fase 0** (PR #119). El kernel ya tiene infraestructura de memoria real.

### B. Dory-Manus (El Hilo Efímero Ejecutor)
Cada vez que Alfredo inicia una nueva sesión con Manus, el agente nace con la memoria en blanco. Manus no sabe qué hizo el hilo Manus de ayer, qué decisiones se tomaron, ni qué contexto operativo está vigente, a menos que se le inyecte manualmente.
**Estado:** Sigue sufriendo amnesia. La infraestructura construida en la Fase 0 no lo beneficia automáticamente porque no hay un cableado ("wiring") entre Manus y el Kernel.

Este documento establece el plan exacto para ejecutar la **Fase 1: Matar Dory-Manus**, utilizando al Kernel como Gatekeeper de Memoria [1] [2].

---

## 2. Fase 0: Lo que ya está construido (Prerrequisitos)

Para que Manus pueda heredar memoria, primero necesitábamos un lugar donde buscarla y guardarla. Esto se completó en el PR #119:

| Componente | Estado Actual (Prod) | Utilidad para Manus |
|---|---|---|
| **RPC `match_memory_events`** | ✅ Activo (Supabase) | Permite a Manus buscar contexto pasado por similitud semántica. |
| **`SovereignCheckpointStore`** | ✅ Activo (Railway) | Permite a Manus guardar su estado para que el siguiente hilo lo retome. |
| **Tabla `memory_events`** | ✅ Activa (4,829+ rows) | El repositorio histórico que Manus puede consultar. |

---

## 3. Fase 1: Plan de Ejecución "Anti-Dory Manus" (Wiring)

Para que el próximo hilo Manus nazca con contexto, debemos implementar el **Pacto de Memoria Persistente** descrito en la doctrina. Esto requiere construir el puente entre el script local (`guardian.py`) y el kernel en Railway.

Basado en los patrones de memoria de agentes state-of-the-art en 2026 (como Letta/MemGPT y Mem0) [3] [4], el enfoque correcto es "Event-sourced persistence" acoplado a un "Handoff Artifact" explícito [5] [6].

### Paso 1.1: Endpoint de Onboarding Semántico (Kernel)
El kernel debe exponer una ruta para inyectar contexto al nuevo hilo Manus basado en su objetivo.

**Acción:** Crear `POST /v1/memento/onboarding` en `kernel/api/routes.py`.
**Input:** `{"hilo_id": "manus_uuid", "objetivo_actual": "Construir modulo de pagos"}`
**Lógica:**
1. Usa la RPC `match_memory_events` para buscar las top 10 memorias relacionadas con el objetivo.
2. Busca el último checkpoint estructurado (Handoff Artifact) guardado por un hilo Manus anterior.
3. Devuelve un payload formateado en Markdown listo para inyección de contexto.

### Paso 1.2: Pre-flight Obligatorio (Manus Local)
Manus debe ser obligado a consumir ese endpoint antes de hacer cualquier otra cosa.

**Acción:** Modificar `monstruo-memoria/.monstruo/guardian.py` y `AGENTS.md`.
**Lógica:**
1. Al arrancar, `guardian.py` pide al usuario (o lee de env) el objetivo de la sesión.
2. Llama a `POST /v1/memento/onboarding`.
3. Imprime el contexto recuperado en la terminal con un header ineludible: `=== CONTEXTO HEREDADO (ANTI-DORY) ===`.

### Paso 1.3: Endpoint de Handoff / Checkpoint (Kernel)
Manus debe poder dejar un "Handoff Artifact" antes de morir o compactarse.

**Acción:** Crear `POST /v1/memento/checkpoint` en `kernel/api/routes.py`.
**Input:** `{"hilo_id": "manus_uuid", "resumen_ejecucion": "...", "next_steps": "...", "credenciales_usadas": [...]}`
**Lógica:** Guarda este artefacto en el `SovereignCheckpointStore` o en `memory_events` con un tag especial de `handoff`.

### Paso 1.4: Protocolo de Cierre (Manus Local)
Manus debe ser instruido para llamar al endpoint de Handoff antes de declarar una tarea terminada.

**Acción:** Actualizar la skill `protocolo-operativo-core` o `el-monstruo-core`.
**Lógica:** Añadir la regla dura: "Antes de entregar el resultado final al usuario, debes ejecutar un curl a `/v1/memento/checkpoint` resumiendo tu estado para el próximo hilo".

---

## 4. Costo y Criterios de Cierre

**Costo estimado:** 1 sesión de trabajo (4 a 6 horas). No requiere investigación nueva, solo wiring de APIs.

**Criterios de Cierre (Definition of Done):**
- [ ] Endpoint `/v1/memento/onboarding` desplegado y respondiendo con Markdown válido.
- [ ] `guardian.py` modificado para invocar onboarding.
- [ ] Endpoint `/v1/memento/checkpoint` desplegado y guardando en DB.
- [ ] Prueba E2E: Un hilo Manus ejecuta una tarea, hace checkpoint, y el SIGUIENTE hilo Manus arranca y recupera ese checkpoint automáticamente vía `guardian.py`.

## 5. Referencias

[1] Doctrina canónica de El Monstruo. `docs/EL_MONSTRUO_15_OBJETIVOS_MAESTROS.md`. Mayo 2026.
[2] Reporte F0 Runtime Reality Proof. `auditoria_dory/RUNTIME_REALITY_REPORT_2026_05_12.md`. Mayo 2026.
[3] Letta (formerly MemGPT). "Stateful AI Agents: A Deep Dive into Letta Memory Models". Febrero 2026.
[4] Fountain City Tech. "Agent Memory & Knowledge Systems Compared (2026 Guide)". Mayo 2026.
[5] Reddit r/AI_Agents. "How are you handling memory in long-running AI agents?". Mayo 2026.
[6] Andre Blair. "I Tried Building a Multi-Agent Assistant Stack (What Actually Worked)". Abril 2026.
