# DSC-M-001: Sovereign Memory System es el Sistema Canónico de Memoria

**Fecha:** 2026-05-21
**Autor:** Manus C (Hilo Ejecutor)
**Aprobado por:** Alfredo Góngora (humano)
**Severidad:** Arquitectónica
**Estado:** VIGENTE

---

## Contexto

El Monstruo acumuló 3 sistemas de memoria independientes durante su evolución:

1. **`monstruo_memory`** (tabla legacy, Sprint 5) — usada solo por `guardian.py` para inyectar contexto al inicio de sesión.
2. **`/v1/memory/thoughts`** (Sprint 12) — sistema de "pensamientos" con auth por `MONSTRUO_API_KEY`. Nunca fue adoptado por hilos externos.
3. **`sovereign_memories` + `sovereign_axioms`** (Sprint 27, SMS v3.1) — sistema completo con embeddings, AUDN Loop, temporal invalidation, REM Cycle, y API REST.

Esta coexistencia genera confusión, duplicación, y ningún hilo sabe cuál usar.

---

## Decisión

> **El Sovereign Memory System (tablas `sovereign_*`, API `/sms/sms/*`) es el sistema CANÓNICO y ÚNICO de memoria del Monstruo a partir de esta fecha.**

### Implicaciones:

1. **`monstruo_memory`** — DEPRECATED. Guardian V5 ya usa el hook SMS. La tabla legacy se mantiene read-only por 30 días y luego se archiva.
2. **`/v1/memory/thoughts`** — DEPRECATED. Los endpoints se mantienen por retrocompatibilidad pero no reciben nuevas escrituras. Migrar datos existentes al SMS en Sprint 28.
3. **`/sms/sms/*`** — CANÓNICO. Todo hilo que necesite memoria DEBE usar estos endpoints.
4. **Regla Dura #12** (AGENTS.md) — ya instruye escritura orgánica al SMS.

### Componentes del sistema canónico:

| Componente | Archivo | Función |
|-----------|---------|---------|
| Storage Layer | `sms_supabase_adapter.py` | CRUD + embeddings + AUDN |
| HTTP API | `sms_universal_api.py` | Endpoints REST con auth |
| Guardian Hook | `sms_guardian_hook.py` | Inyección al inicio de sesión |
| Consolidation | `sms_rem_cycle.py` | Ciclo nocturno 3 AM CST |
| Schema | `migrations/sql/0052_*.sql` + `0053_*.sql` | Tablas + RPCs |

### Auth:
- `SMS_API_KEY` requerida para todos los endpoints
- Configurada en Railway (kernel + rem-cycle)

---

## Razón

Un sistema de memoria dividido en 3 es peor que no tener memoria. La soberanía requiere una fuente única de verdad. El SMS tiene las capacidades más avanzadas (AUDN, temporal, consolidation) y es el único con API pública documentada.

---

## Firmado

```
DSC-M-001 | 2026-05-21 | sovereign_memory_canonical | VIGENTE
Firmado: Manus C + Alfredo Góngora
```
