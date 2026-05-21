# AGENT OUTPUT — Manus C — B1-B5/B10 Tickets + Implementation Map

## Metadata
- agente: manus_c
- rol real: planificador de tickets
- fecha/hora: 2026-05-20T23:35 CST
- rama: control-tower/2026-05-20-batch-004-gap-tickets
- PR: N/A
- commit: pending
- estado fuente: SAFE_RUNTIME (Tickets only)
- tocó código: no
- tocó main: no

## Implementation Map (Anti-Dory FORGE v3.0)

Este documento detalla los tickets necesarios para implementar los componentes faltantes de la arquitectura Anti-Dory (B1-B5, B10). **Ninguno de estos tickets debe ejecutarse sin autorización magna explícita para Supabase/Runtime.**

### Ticket 1: B1 Anchor Store (Supabase Migration)
**Estado:** `NEEDS_RUNTIME`
**Dependencias:** Ninguna.
**Descripción:** Crear la tabla `anti_dory_anchor_store` en Supabase para almacenar la doctrina inmutable.
**Tareas:**
1. Crear migración SQL `0009_anti_dory_anchor_store.sql`.
2. Schema: `id` (UUID), `concept` (TEXT), `definition` (TEXT), `canon_date` (TIMESTAMPTZ), `t1_signature` (TEXT).
3. Habilitar RLS (`ENABLE ROW LEVEL SECURITY`).
4. Crear policy de solo lectura para `service_role`. (Escritura solo vía T1 signature).

### Ticket 2: B3 Plan Ledger (Supabase Migration)
**Estado:** `NEEDS_RUNTIME`
**Dependencias:** Ticket 1 (B1).
**Descripción:** Crear la tabla `anti_dory_plan_ledger` en Supabase (append-only) para registro inmutable de planes y delegaciones.
**Tareas:**
1. Crear migración SQL `0010_anti_dory_plan_ledger.sql`.
2. Schema: `id` (UUID), `plan_hash` (TEXT), `status` (TEXT), `delegated_to` (TEXT), `created_at` (TIMESTAMPTZ).
3. Habilitar RLS.
4. Crear policy append-only para `service_role`.

### Ticket 3: B2 Claim Verification Gate (Kernel Module)
**Estado:** `NEEDS_DESIGN`
**Dependencias:** Ticket 1 (B1).
**Descripción:** Implementar el motor de validación semántica en Python.
**Tareas:**
1. Crear `kernel/anti_dory/b2_claim_vg.py`.
2. Implementar extracción de claims del input.
3. Implementar búsqueda semántica contra el Anchor Store (B1).
4. Definir algoritmo de similitud (ej. embeddings) y umbrales de rechazo.
5. Integrar fallback a B5 (Enjambre de Sabios) en caso de baja confianza.

### Ticket 4: B4 State Memento (Kernel Module)
**Estado:** `NEEDS_DESIGN`
**Dependencias:** Ticket 2 (B3).
**Descripción:** Implementar la lógica de snapshots periódicos del estado global.
**Tareas:**
1. Crear `kernel/anti_dory/b4_memento.py`.
2. Definir payload del snapshot (estado actual, último plan activo, contexto crítico).
3. Implementar serialización a JSON/Markdown.
4. Definir política de retención (TTL).

### Ticket 5: B10 Guardian Autónomo (Nightly Builder Cron)
**Estado:** `NEEDS_DESIGN`
**Dependencias:** Tickets 1-4, B11 (KL Divergence).
**Descripción:** Proceso background que audita la salud del sistema y detecta derivas.
**Tareas:**
1. Crear `scripts/nightly_builder/guardian_cron.py`.
2. Implementar heurísticas de alerta (ej. si KL Divergence < 0.15).
3. Integrar lectura del Plan Ledger (B3) para detectar planes atascados.
4. Configurar ejecución periódica (cron/Railway schedule).

## Archivos tocados
| archivo | acción | branch | commit | nota |
|---|---|---|---|---|
| bridge/control_tower/2026-05-20/manus_c/B1_B5_B10_TICKETS.md | CREATED | control-tower/2026-05-20-batch-004-gap-tickets | pending | Solo tickets documentales |

## Confirmaciones
- No escribí en Supabase.
- No ejecuté código crítico.
- No modifiqué el kernel real.
- No canonizo nada.
- No desbloqueo R1.
- No recomiendo merge/deploy sin T1.
