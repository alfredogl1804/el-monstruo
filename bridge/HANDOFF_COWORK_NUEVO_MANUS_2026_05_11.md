# Handoff: Estado Real del Monstruo (Cowork Nuevo)

**Fecha:** 11 de mayo de 2026
**Autor:** Manus (Hilo Ejecutor)
**Para:** Nuevo Hilo Cowork
**Objetivo:** Transferir el estado 100% real, verificado en código y repositorios, evitando alucinaciones o dependencias de memoria volátil. Todo lo afirmado aquí fue validado vía shell en el Mac de Alfredo.

---

## 1. Estado del Repositorio (`main`)

*   **Rama actual:** `main` está al día con `origin/main`.
*   **PRs Mergeados Recientemente:**
    *   ✅ **PR #93** (`4834e7a`): Rescate del stash de Cowork (36 archivos recuperados).
    *   ✅ **PR #91** (`f575b73`): P0 RLS Fix `catastro_vision_generativa` expuesta a anon (migración 0011).
    *   ✅ **PR #90** (`c0ee5230`): Sprint COWORK-RUNTIME-001 (T1-T8 + M9 cura síndrome Dory).
    *   ✅ **PR #89** (`70b8f5e`): Canon Metodologías + La Conversación 2.
    *   ✅ **PR #88** (`e5d1335`): Hotfix self-verifier loop detection insert shape.
*   **PRs Abiertos:**
    *   ✅ **PR #92** (`sprint/mobile-1b-a2ui-implementation`): 51/51 tests PASS. Faltante: T8 (Smoke E2E en iPhone físico por Alfredo).
    *   ✅ **PR #86** (`sprint/embrion-needs-001-task-2-self-verifier`): Abierto, 1497 adiciones.
    *   ✅ **PR #82** (`sprint/88-mega-catastro-sandbox`): Abierto, 4228 adiciones.
    *   ❌ **PR #93** (Rescate Stash): Ya NO está abierto, fue mergeado hace minutos.

---

## 2. Estado Supabase (`xsumzuhwmivjgftsneov`)

*   ⚠️ **RLS (Row Level Security):** *Pendiente de verificar en vivo.* (El hilo Manus actual no tiene la `SUPABASE_SERVICE_KEY` accesible. Según reportes previos en bridge, está en 120/120 tras PR #91, pero Cowork debe re-verificar usando MCP Supabase).
*   ✅ **Migraciones en código (`migrations/sql/`):**
    *   `0009_cowork_sesiones.sql`: Existe y aplica RLS a la memoria de Cowork.
    *   `0010`: **NO EXISTE** en el repositorio. Hubo un salto en la numeración o se renombró.
    *   `0011_rls_catastro_vision_generativa.sql`: Existe y sella la vulnerabilidad P0.

---

## 3. Módulos del Kernel (Embrion)

Los tres módulos clave de `kernel/` fueron verificados y contienen las siguientes implementaciones activas:

*   ✅ **`kernel/embrion_budget.py`** (484 líneas):
    *   Tracker estricto cableado (`c3f3547`).
    *   Flags activos (leídos vía `os.environ`): `EMBRION_CAP_PER_LATIDO_USD` (default $0.25), `EMBRION_DAILY_BUDGET` ($30.0), `EMBRION_HITL_ESCALATION_THRESHOLD` (3).
*   ✅ **`kernel/embrion_self_verifier.py`** (445 líneas):
    *   Lógica para romper bucles de eco (`54d116c`).
    *   Flags activos: `EMBRION_VERIFIER_NOVELTY_WINDOW_HOURS` (24), `EMBRION_VERIFIER_JACCARD_THRESHOLD` (0.85).
*   ✅ **`kernel/embrion_loop.py`** (2067 líneas):
    *   Integra Budget Tracker + Self-Verifier en `_think()` (`aefee24`).
    *   Implementa Circuit Breaker para `embrion_judge` fail-open (`34b0c90`).
    *   Flags activos: `EMBRION_CHECK_INTERVAL` (60s), `EMBRION_THINK_COOLDOWN` (300s), `EMBRION_JUDGE_MODEL` (gpt-5), `EMBRION_ACTOR_MODEL` (gpt-5.5).

---

## 4. Archivos Rescatados (`memory/cowork/`)

El PR #93 restauró 36 archivos que Cowork había dejado perdidos en un `git stash`. El directorio `memory/cowork/` ahora contiene:

*   ✅ `COWORK_BASE_CONOCIMIENTO.md`: Mapa estructural del Monstruo, semilla v0.1.
*   ✅ `COWORK_DECISIONES_VIVAS.md`: Decisiones en producción HOY, no aspiraciones.
*   ✅ `COWORK_AUDIT_FORENSE_2026_05_11.md`: Auditoría interna de Cowork, 22 fallos catalogados.
*   ✅ `COWORK_GLOSARIO_VIVO.md`: Definiciones canónicas.
*   ✅ `COWORK_HISTORIA_FORMATIVA.md`: Registro de evolución.
*   ✅ `COWORK_ESTADO_VIVO.md`: (Ya existía en main, se conservó versión de main).
*   ✅ `PREFLIGHT_ARRANQUE_2026_05_11.md` y `REPORTE_BINARIO_APP_FLUTTER_2026_05_11.md`.
*   ✅ **25 auditorías en `audits/`**: Cartografías 1A-1E, auditorías de capas 3A/3B, objetivos 2D, portfolio 4A/4B, cruce 5A, plan 5B, y dimensionales D1, D7, D11-D19.

---

## 5. Hilos Manus Activos y Sprints

*   ✅ **Hilo Ejecutor Principal (Este hilo):**
    *   Terminó Sprint `MOBILE_1B` A2UI Implementation (19 widgets, 51/51 tests PASS).
    *   Ejecutó rescate forense del stash de Cowork (PR #93).
*   ✅ **Hilo Catastro:** *Pendiente de verificar estado exacto.* (Asignado a PR #82 MEGA-CATASTRO 88.3).
*   ✅ **Hilo Ejecutor 2:** *Pendiente de verificar estado exacto.* (Asignado a Sprint RAMP FLAGS y fix path migración 0010 según logs).

---

## 6. Bugs Pre-existentes Detectados

Durante la verificación se encontraron dos inconsistencias a nivel de código/base de datos que requieren atención:

1.  ✅ **Tabla `run_costs` fantasma:** El archivo `kernel/finops.py` referencia explícitamente la tabla `run_costs` para acumular costos por `run_id`. Sin embargo, **no existe ninguna migración SQL** en el repositorio que cree esta tabla. Posible error en tiempo de ejecución si FinOps intenta escribir.
2.  ✅ **`embrion_judge` CHECK constraint:** Se detectó un historial reciente de fallos por violación de constraint en `self_verifier persist` (commits `dc1b14b` y `1f3b179`). Aunque hay fixes aplicados, el log muestra que el circuit breaker `embrion_judge_failopen_alfredo_override` se activó recientemente. Requiere monitoreo.
