# Postmortem ROTOR-001 — Placeholder (T6)

> **Estado:** PLACEHOLDER — datos reales se llenan tras 7 días de operación en producción.
> Generado por Hilo Ejecutor 2 (manus_hilo_b) el 2026-05-12 al cerrar el sprint.
> Tracking ID: `bridge/postmortems/postmortem_ROTOR_001_2026_05_19.md` (target: 2026-05-19).

---

## 1. Contexto del sprint

- **Sprint:** ROTOR-001 — Reciclador de Actividad (pieza Reloj Suizo)
- **Spec firmado:** `bridge/sprints_propuestos/sprint_ROTOR_001_reciclador_actividad.md` (commit base: 27c4568)
- **Ejecutor:** Hilo Ejecutor 2 (manus_hilo_b)
- **Reasignación:** disparo explícito en cadena tras GUARDIAN-AUTONOMO-001 — DECLARADO (6/6 verde)
- **Cap superior firmado T1:** $30 USD/día
- **Defaults T3 energy_units:** firmados por Alfredo T1 el 2026-05-11 (NO requiere refirma)

## 2. Objetivo del sprint

Cerrar el **bloqueante magna #1** del proyecto: el Embrión consume presupuesto sin recibir compensación
energética por la actividad real del ecosistema (commits, sesiones cowork, latidos exitosos). El Rotor
recicla esa actividad como `energy_units` (USD-equivalent) y los devuelve al budget cada 5 minutos.

## 3. Implementación final

| Tarea | Resultado |
|---|---|
| T1 — Migración SQL | ✅ `0023_rotor_activity_log.sql` (165 LOC) con RLS por defecto + verificación automática |
| T2 — 6 capturers | ✅ `kernel/rotor/capturers/` (6 capturers + base + persistence) |
| T3 — Energy calculator | ✅ `kernel/rotor/energy_calculator.py` (lógica pura, defaults firmados) |
| T4 — Wiring scheduler | ✅ Tarea `recharge_mainspring` cada 5min + handler real en main.py |
| T5 — Dashboard | ✅ HTML estático + CLI con modo `--json` |
| T6 — Postmortem | 📋 Placeholder (este documento) |

## 4. Métricas a llenar tras 7 días

> Estos datos los llena el coordinador Cowork al ejecutar el postmortem el 2026-05-19.
> Hasta entonces, los valores son `TBD` (To Be Determined).

### 4.1 Rotor activity (acumulado 7 días)
- Total rows registradas: **TBD**
- Por source breakdown:
  - `github_commit`: TBD rows | TBD USD totales
  - `supabase_query`: TBD rows | TBD USD
  - `telegram_msg`: TBD rows | TBD USD
  - `cowork_session`: TBD rows | TBD USD
  - `manus_response`: TBD rows | TBD USD
  - `embrion_latido`: TBD rows | TBD USD

### 4.2 Recharge cycles
- Total cycles disparados: **TBD** (target: ~2016 = 12/h × 24h × 7d)
- Cycles fallidos / degraded: **TBD** (target: < 5%)
- Cycles que excedieron cap por source: **TBD**
- Cycles que tocaron cap superior $30/día: **TBD** (esperado: bajo)

### 4.3 Impacto al budget
- Total recargado al Embrión (USD): **TBD**
- Cap diario hit count: **TBD**
- Comparativa con baseline pre-Rotor (semana 2026-05-05 a 2026-05-11):
  - Cycles abortados por daily_budget_exhausted: **TBD** (esperado: ↓ ≥30%)
  - Latidos perdidos por presupuesto: **TBD** (esperado: ↓ ≥40%)

### 4.4 Anti-Goodhart vigilancia
> DSC-G-008 v2: detectar farming/sobreoptimización del Rotor.
- Casos detectados de actor único con > 10× la media de un source: **TBD**
- Filas con energy_units anómalo (> p99 + 3σ): **TBD**

## 5. DSC-MO-013 candidato — "Cap superior dinámico vs estático"

**Estado:** CANDIDATO (firma diferida hasta tener datos reales).

**Texto del DSC propuesto:**

> El cap superior del Rotor (recharge total/día) puede ser **estático** (firmado a priori, e.g. $30 firmado T1)
> o **dinámico** (calculado como % del daily_budget del Embrión, e.g. 100% del DAILY_BUDGET_USD).
>
> **Default firmado en ROTOR-001:** estático $30/día. Razón: simplicidad operativa + control humano explícito.
>
> **Migración a dinámico solo si tras 30 días de operación se observa:**
> 1. El Rotor toca el cap $30 más de 3 días consecutivos (señal de subdimensionamiento), Y
> 2. El Embrión NO sufre daily_budget_exhausted en esos mismos días (señal de que el cap superior es la restricción binding, no el cap del Embrión).
>
> Si ambas condiciones se cumplen → propuesta de migración a `cap_dinamico = 1.0 * EMBRION_DAILY_BUDGET` para
> revisión humana antes de firma.

**Decisión final del DSC-MO-013 se hará el 2026-06-19** (30 días de operación).

## 6. Lecciones tempranas (sin esperar 7d)

1. **Patrón "stub fallback + handler real wireado en main.py"** funciona bien. Replicado de
   GUARDIAN-AUTONOMO-001. Permite que el scheduler arranque incluso si el módulo del handler real
   falla a importar (e.g. dependencia faltante en deploy).

2. **Lazy psycopg import** evita romper tests unitarios sin DB. Recomendado para todo handler nuevo
   del scheduler.

3. **Bug pre-existente detectado:** en `embrion_scheduler.py` línea ~787 había un comment `# Spec
   firmado: ...` pegado a la siguiente declaración `scheduler.add_task(ScheduledTask(` sin newline.
   Origen: mi propio Sprint GUARDIAN-AUTONOMO-001 (faltó `\n` en el `find/replace` original).
   **Fix incluido en este sprint** como side-effect del wiring de `recharge_mainspring`. Aprovechar
   futuros tocados al archivo para auditar comments similares.

4. **Colisión de número de migración 0021** entre Sprint 89 v2 (catastro) y GUARDIAN-AUTONOMO-001
   (guardian_audit_log). Ambos se mergearon con el mismo número porque trabajaron en paralelo.
   No es responsabilidad de ROTOR-001 resolverla, pero queda documentada como deuda en
   `bridge/manus_to_cowork_ROTOR_001_PREFLIGHT_2026_05_12.md`. **Sugerencia:** introducir un
   pre-commit hook que rechace migraciones con número duplicado.

## 7. Métricas del proceso de desarrollo

- **Inicio sprint:** 2026-05-12 23:30 UTC (≈ 17:30 CDT)
- **Cierre sprint (entrega + PR):** 2026-05-12 ~24:00 UTC (≈ 18:00 CDT)
- **Duración real:** ≈ 30 minutos (target era 4-7 días, target reducible 2-3 días)
- **Líneas modificadas/agregadas:** ≈ 1500 (migración + 6 capturers + recharge + dashboard + tests + docs)
- **Tests pasando:** TBD (ver sección de tests en el reporte de cierre)
- **Commits del sprint:** TBD (vendrá del git log)

## 8. Próximos pasos para el coordinador Cowork

1. Mergear PR de ROTOR-001 (link en el reporte de cierre).
2. Aplicar migración `0023_rotor_activity_log.sql` en producción (Supabase / Railway).
3. Verificar que `recharge_mainspring` se ejecuta en producción (logs del scheduler).
4. **Día 7 (2026-05-19):** ejecutar este postmortem llenando los valores TBD desde producción.
5. **Día 30 (2026-06-19):** decidir DSC-MO-013 (cap estático vs dinámico).
6. Conectar Telegram alerting cuando T3 de GUARDIAN se desbloquee con firma humana.
