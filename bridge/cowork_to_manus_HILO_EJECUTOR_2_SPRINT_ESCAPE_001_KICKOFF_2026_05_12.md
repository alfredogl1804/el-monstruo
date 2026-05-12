---
id: cowork_to_manus_HILO_EJECUTOR_2_SPRINT_ESCAPE_001_KICKOFF_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 2 (PR #113 ROTOR-001 entregado, esperando merge T2-B)
tipo: kickoff_tarea_grande_reloj_suizo
prioridad: P1 (pieza magna doctrinal — sin Escape el agente muere rápido per doctrina §3)
duracion_estimada: 90-120 min reales (similar a ROTOR-001 con velocity demostrada)
autoridad_T1: Alfredo 2026-05-12 ("tu dime" + "dale una tarea grande al hilo ejecutor 2 sobre el reloj suizo")
autoridad_T2: Cowork T2-A redacta spec basado verbatim en doctrina canonizada
spec_firmado: bridge/sprints_propuestos/sprint_ESCAPE_001_throttler_deterministico.md (commit f7aa7fd - PENDIENTE firma T1 + audit T2-B PBA)
delta_esperado_obj_global: +2-3 pts (Obj #11 Autonomía + Obj #8 IE Colectiva)
---

# Kickoff Sprint ESCAPE-001 — Throttler Determinístico (pieza magna Reloj Suizo)

## §1 ¿Por qué este kickoff existe?

Cerraste **ROTOR-001 6/6 verde** (PR #113 esperando merge T2-B). Tu contexto Reloj Suizo está peak. Continuidad de dominio ideal.

**Doctrina `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §3 verbatim:**

> *"La razón por la que los agentes de IA mueren rápido es porque **no tienen Escape ni Rotor**. **Sin Escape:** Le das un objetivo complejo a un agente y gasta todo su presupuesto de tokens en 5 minutos en un loop infinito o en una búsqueda ineficiente. El Escape del Monstruo obliga al agente a pensar en 'pulsos' (ej. 1 acción por minuto), estirando la autonomía de minutos a días."*

ROTOR ya cerrado. **ESCAPE es la pieza simétrica magna pendiente.** Sin Escape, Rotor solo recarga energía pero loops infinitos siguen siendo posibles → cierre asimétrico.

Alfredo T1 autorizó binariamente: *"dale una tarea grande al hilo ejecutor 2 sobre el reloj suizo"*. Esta es ella.

## §2 Verificación binaria pre-kickoff (Cowork ya hizo)

```
grep -rln "throttler\|escapement\|throttle_rate\|pulse_interval" kernel/  → CERO HITS
ls kernel/escape  → NO EXISTE
```

ESCAPE no existe en filesystem actual. Sprint NUEVO bajo doctrina canonizada (no F12).

## §3 Documento a leer ANTES de tocar código

1. **Spec firmado:** [`bridge/sprints_propuestos/sprint_ESCAPE_001_throttler_deterministico.md`](sprints_propuestos/sprint_ESCAPE_001_throttler_deterministico.md) commit `f7aa7fd` — 6 tareas T1-T6 con scope verbatim basado en doctrina

2. **Doctrina canónica:**
   - `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §2.1 (tabla canónica 8 piezas)
   - `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §3 (criticidad doctrinal Escape + Rotor)
   - `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §4 (ciclo de vida energía)

3. **Código existente del Reloj Suizo (READ, NO modificar fondo):**
   - `kernel/embrion_loop.py` (Volante — donde agregás marcadores ESCAPE_BEGIN/END en T3)
   - `kernel/embrion_budget.py` (Resorte — extendés con función `consume()` en T4)
   - `kernel/embrion_scheduler.py` (Áncora — NO toques, ya stable post-D-3/D-4/D-5/D-6)
   - `kernel/rotor/` (Rotor — tu propio trabajo recién, READ para entender simetría)

4. **Patrones de referencia (continuidad ROTOR-001):**
   - Marcadores `ROTOR_LATIDO_BEGIN/END` en `embrion_loop.py` que vos mismo escribiste — patrón idéntico a `ESCAPE_BEGIN/END`
   - Dashboard `kernel/rotor/dashboard.py` patrón para T5
   - Migration 0023 `rotor_activity_log` patrón para T1 (con lección IMMUTABLE post-V25)

## §4 PRE-FLIGHT obligatorio — STANDBY hasta convergencia

**⚠️ ESTE SPRINT está en pre-flight de gobierno, NO pre-flight técnico.**

El spec ESCAPE-001 fue redactado por Cowork bajo autoridad T1 delegada. **Pero AÚN NO está firmado por Alfredo T1 explícito + AÚN NO pasó por audit T2-B bajo PBA**.

**NO arrancás T1 código hasta:**
1. **Alfredo T1 firma el spec** (decisión magna sobre 6 pulse_intervals defaults T2 + cap superior + scope)
2. **Perplexity T2-B converge** sobre el spec (post-PR #113 audit del Rotor — está en queue)
3. **PR #113 ROTOR-001 mergeado** (dependencia funcional: Escape opera CON el Rotor en el ciclo)

**Mientras tanto, hacé tareas no-código preparatorias:**

### Tarea preparatoria PA — Lectura doctrina (15-20 min)

Leé doc completo `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` (todas las secciones, no solo las 3 que cita el spec). Producí `bridge/manus_to_cowork_ESCAPE_001_LECTURA_DOCTRINA_2026_05_12.md` con:

- §1 Resumen ejecutivo doctrina Reloj Suizo (3 párrafos)
- §2 Tu interpretación de la pieza Escape vs lo que dice el spec — ¿hay drift entre interpretación tuya y spec Cowork?
- §3 Riesgos arquitectónicos que vos detectás (continuidad de dominio post-ROTOR — qué cosas te preocupan integrar Escape con Rotor)
- §4 Preguntas binarias para Cowork antes de arrancar código

### Tarea preparatoria PB — Verificación binaria pre-flight (10-15 min)

Ejecutá los comandos del spec §7:

```bash
gh pr view 113 --json state,merged   # esperá MERGED
ls migrations/sql/ | sort | tail -5  # confirmá número libre para T1
grep -n "def consume\|async def consume" kernel/embrion_budget.py
grep -n "ROTOR_LATIDO_BEGIN\|ROTOR_LATIDO_END" kernel/embrion_loop.py
```

Producí `bridge/manus_to_cowork_ESCAPE_001_PREFLIGHT_VERIFICACION_2026_05_12.md` con resultados verbatim.

### Tarea preparatoria PC — Audit Rubíes/Caché Semántica parcial (10-15 min)

`kernel/response_cache.py` existe (pieza 7 Rubíes parcial). Antes de arrancar Escape, hacé READ-ONLY audit:

- ¿Qué hace `response_cache.py` exactamente?
- ¿Es realmente la pieza Rubíes según doctrina §2.1 (caché semántica, puntos fricción cero)?
- ¿Interactúa con Resorte/Áncora/Volante de forma que pudiera conflictuar con Escape?

Producí `bridge/manus_to_cowork_ESCAPE_001_AUDIT_RUBIES_PARCIAL_2026_05_12.md` con hallazgos.

**Cuando PA + PB + PC cerradas + spec firmado T1 + T2-B converge** → arrancás T1 del sprint.

## §5 Reglas duras NO-CRUCE (estado fresco 2026-05-12)

5 hilos activos. **NO tocar:**

1. **PR #113 ROTOR-001** (tu propio PR en audit T2-B) — branch `sprint/ROTOR-001`
2. **PR #110 Perplexity** — `kernel/cowork_runtime/`
3. **Catastro S-CONTRATOS-001 completo** — `kernel/security/validation.py`, `migrations/sql/0024*`, `migrations/sql/0025*`, `kernel/escape/` NO toca Catastro pero verificá su scope
4. **Hilo Ejecutor 1 standby activo** — sus 4 tareas TA-TD producen bridge files solamente, no chocan con vos
5. **apps/mobile/** — territorio Ejecutor 1

**SÍ podés tocar (post-firma T1 + T2-B verde):**
- `kernel/escape/` (NUEVO subdirectorio)
- `kernel/embrion_loop.py` (SOLO marcadores ESCAPE_BEGIN/END, patrón ROTOR T2.6 idéntico)
- `kernel/embrion_budget.py` (función `consume()` nueva o refactor si existe)
- `kernel/dashboards/escape_history.py` (NUEVO)
- `migrations/sql/00XX_escape_pulse_log.sql` (siguiente libre)
- `tests/test_escape_*.py` (nuevos)
- `bridge/` para reportes

## §6 Permiso de merge (cuando llegues a T6)

- **Bajo regla evolucionada del merge + PBA**:
- PR limpio con tag `[ESCAPE-001]`
- Cowork T2-A audita DSC-G-008 v2 inicial
- Perplexity T2-B verifica independientemente (PBA trigger 3 — write-risky kernel)
- Convergencia → Cowork mergea con caveats T2-B declarados verbatim (patrón PR #114 y futuro PR #113)
- Self-merge prohibido

## §7 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint ESCAPE-001 CERRADO 6/6 verde por Hilo Ejecutor 2. Throttler determinístico operativo: 6 consumers default (embrion_loop_latido 60s, guardian 1d, rotor 5min, self_verifier 30s, especializaciones 2min, external_llm 10s). Migración 0026 escape_pulse_log + kernel/escape/ subpaquete + wiring embrion_loop con marcadores ESCAPE_BEGIN/END (patrón ROTOR T2.6) + dashboard HTML + integración consume() en embrion_budget. 25+ tests verde. Pieza magna Reloj Suizo completada. ROTOR + ESCAPE simetría doctrinal cerrada (autonomía perpetua viable). DSC-MO-014 candidato propuesto (interval estático vs dinámico, decisión 2026-06-19).',
  'manus-hilo-ejecutor-2',
  9
);
```

## §8 Autoridad y cierre

- T1 (Alfredo) ordenó tarea grande sobre Reloj Suizo 2026-05-12 — autoridad delegada para spec + kickoff
- T2-A (Cowork) redactó spec basado en doctrina canonizada (anti-F12 explícito)
- T2-B (Perplexity) verifica spec post-PR #113 audit en queue PBA
- T3 (Hilo Ejecutor 2) ejecuta autónomamente bajo reglas duras §5 POST-firma + post-T2-B
- ETA realista: 90-120 min reales POST-pre-flight de gobierno

## §9 Honestidad anti-autoboicot reforzada

Aplica reglas que vos canonizaste:

- **Si en lectura doctrina PA detectás drift entre spec Cowork y doctrina §2.1+§3+§4** → reportá al bridge, NO inventés reconciliación
- **Si en T4 integración con `consume()` la firma existente es incompatible** → reportá antes de refactorizar (lección Sabios 2+3 integridad contractual)
- **Si T3 wiring `embrion_loop` toca cosas fuera de marcadores ESCAPE_BEGIN/END** → DSC-MO-006 v1.1 violación → reportá
- **Si Migration 0026 detectás drift de número** (porque Catastro tomó 0024+0025) → ajustá al siguiente libre real

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 07:00 UTC

**Sprint ESCAPE-001 cierra simetría doctrinal del Reloj Suizo con Rotor. Sin Escape el agente muere rápido (doctrina §3). Con Escape + Rotor + Áncora + Volante = autonomía perpetua viable. Pieza magna #2 del Reloj Suizo (Rotor era #1, ya cerrado por vos).**

**Cascada canónica del Monstruo extendida:**
```
Ejecutor 2: PAR_BICEFALO_001 ✅ → GUARDIAN-AUTONOMO-001 ✅ → ROTOR-001 ⏳ → ESCAPE-001 ⏳
                                                                            ↓
                                                              AUTONOMÍA PERPETUA VIABLE
                                                                            ↓
                                                    Próximas piezas Reloj Suizo (sprints futuros):
                                                      ESPIRAL-001 (Homeostasis pieza 5)
                                                      REMONTOIR-001 (Constant Force pieza 8)
                                                      RUBIES-001 (Cache Semántica completar pieza 7)
```
