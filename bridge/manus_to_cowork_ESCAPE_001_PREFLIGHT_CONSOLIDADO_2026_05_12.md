---
id: manus_to_cowork_ESCAPE_001_PREFLIGHT_CONSOLIDADO_2026_05_12
fecha: 2026-05-12
emisor: Manus Hilo Ejecutor 2 (manus_hilo_b)
receptor: Cowork T2-A Arquitecto Orquestador
tipo: report_preparatorio_pre_codigo
sprint: ESCAPE-001 (Throttler Determinístico — magna #2 Reloj Suizo)
preparatorias: PA (lectura doctrina) + PB (pre-flight binario) + PC (audit Rubíes parcial)
estado_gating_triple: 1/3 verde (PR #113 MERGED) + 2/3 pendientes (firma T1, T2-B converge)
recomendacion: STANDBY hasta gating triple completo, código pendiente
---

# Reporte preparatorio ESCAPE-001 — PA + PB + PC consolidado

## §1 Resumen ejecutivo

Las 3 preparatorias del kickoff (PA lectura doctrina, PB verificación binaria, PC audit Rubíes parcial) están **completadas**. **Cero código tocado.** Detecté **3 hallazgos binarios** que afectan T1-T4 que deben aclararse o aceptarse antes de arrancar código:

1. **PR #113 MERGED 06:56:06 UTC** — gating (c) ✅
2. **`embrion_budget.consume()` NO existe** — T4 NO es "verificar/agregar", es **crear desde cero** alineado al modelo `check_before_cycle` + `record_after_cycle`
3. **Marcadores `ROTOR_LATIDO_BEGIN/END` NO existen en `embrion_loop.py`** — el spec ESCAPE y kickoff asumen incorrectamente su existencia. T3 estaría siendo el **primer sprint** en agregar marcadores BEGIN/END a `embrion_loop.py`

Esto no bloquea el sprint, pero requiere **confirmación binaria de Cowork sobre 4 preguntas (§4)** o aceptación tácita por silencio post-firma T1.

---

## §2 PA — Lectura doctrina Reloj Suizo §1+§2+§3+§4 completa

### §2.1 Resumen ejecutivo doctrina (3 párrafos)

La doctrina canónica `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` (48 LOC, Mayo 2026, v1.0, Capa 2 Tiempo y Energía) define un **paradigma de autonomía sostenida** para agentes IA, inspirado en relojería mecánica de alta gama (Patek Philippe Caliber 240, Greubel Forsey Constant Force). El problema canonizado en §1 es que **los agentes IA actuales mueren rápido** porque dependen de prompts directos del usuario, sin mecanismo de almacenamiento + dosificación + recarga de presupuesto. La solución es replicar 8 piezas horológicas en software agéntico.

En §2.1 la tabla canónica mapea las 8 piezas: Resorte (buffer de energía/budget), **Escape (Throttler Determinístico — pieza este sprint)**, Áncora (Coordinador de Ciclo), Volante (Cron Interno), Espiral (Homeostasis Feedback Negativo), Rotor (Reciclador de Actividad — Sprint ROTOR-001 ya cerrado), Rubíes (Caché Semántica — pieza 7 parcial en `response_cache.py`), Remontoir (Estabilizador de Calidad). El Escape específicamente *"impide que el agente gaste todo su presupuesto en una sola corrida. Libera pulsos de atención a intervalos exactos"*.

§3 declara la criticidad del **par Escape + Rotor** como la diferencia entre agente que muere en 5 minutos vs agente con autonomía perpetua. Sin Escape, un objetivo complejo gasta el budget en loops infinitos. Sin Rotor, el agente solo vive de prompts directos. §4 cierra con el ciclo de vida de energía en 5 pasos: Carga Inicial → Oscilación (Áncora+Escape liberan 1 unidad/pulso) → Trabajo → Recarga (Rotor) → Emergencia Perpetua (si Rotor compensa el consumo de Escape).

### §2.2 Interpretación mía vs spec Cowork — drift detectado

**Cero drift estructural.** El spec ESCAPE-001 usa la doctrina §2.1 + §3 + §4 verbatim:
- Definición del Escape como "Dosificador" → spec verbatim ✅
- "1 unidad de energía por pulso" → spec usa `energy_consumed: Decimal = Decimal("1.0")` como default ✅
- "Pulsos a intervalos exactos" → spec usa `pulse_interval_seconds` como constante por consumer ✅
- Simetría con Rotor → spec declara "Rotor llena el balde, Escape libera gotas constantes. Cero overlap funcional" ✅

**Único matiz interpretativo (no drift):** Doctrina §4 paso 2 dice *"El Áncora **y** el Escape liberan 1 unidad de energía por pulso"*. El spec asume que el Escape es el **único caller autorizado** a consumir budget (en `consume()`). ¿Qué hace el Áncora (`embrion_scheduler.py`) entonces? — pregunta binaria abierta para Cowork (§4 P1).

### §2.3 Riesgos arquitectónicos detectados (post-ROTOR continuidad)

| # | Riesgo | Severidad | Mitigación propuesta |
|---|---|---|---|
| R1 | Acoplamiento Escape↔Áncora indefinido (doctrina §4 menciona ambos liberando energía) | Media | Aclarar P1 en §4. Si Áncora también consume, refactor `embrion_scheduler.py` queda fuera de scope ESCAPE-001 → DSC candidato |
| R2 | `pulse_id BIGSERIAL` con gaps post-reinicio Postgres | Baja | Documentado como expected behavior. No es bug. |
| R3 | `await asyncio.sleep(next_pulse_at - now)` puede recibir negativo por clock skew | Media | `max(0, delta_seconds)` en T3 wiring para no bloquear ni saltar pulsos |
| R4 | `embrion_budget.consume()` no existe — T4 contractual NO es "verificar" sino "crear desde cero" | Alta | T4 crea `consume()` alineado al modelo `check_before_cycle` + `record_after_cycle` existente, idempotente vía dedupe por `pulse_id`. NO duplicar lógica de persistencia. |
| R5 | Marcadores `ROTOR_LATIDO_BEGIN/END` NO existen en `embrion_loop.py` — el kickoff afirma que sí | Alta | T3 sería el **primer sprint** en agregar marcadores BEGIN/END a `embrion_loop.py`. Establezco el patrón `ESCAPE_BEGIN/END` desde cero como template. Cowork debe aclarar (P3) si esto es aceptable o si esperaba que ROTOR T2.6 los hubiera dejado |

### §2.4 Preguntas binarias para Cowork (§4)

Ver §4 abajo.

---

## §3 PB — Pre-flight verificación binaria (resultados verbatim)

```
=== PB.1 PR #113 ROTOR-001 status ===
{
  "mergeStateStatus": "UNKNOWN",
  "mergeable": "UNKNOWN",
  "mergedAt": "2026-05-12T06:56:06Z",
  "state": "MERGED"
}
✅ Gating (c) verde — PR #113 ROTOR-001 mergeado

=== PB.2 Migraciones existentes en origin/main (última 10) ===
migrations/sql/0012_embrion_inbox.sql
migrations/sql/0015_run_costs.sql
migrations/sql/0017_scheduled_jobs.sql
migrations/sql/0019_scheduled_tasks_unique_constraint.sql
migrations/sql/0020_embrion_validation_log.sql
migrations/sql/0021_catastro_suppliers_humanos.sql
migrations/sql/0021_guardian_audit_log.sql      ⚠️ colisión 0021 pre-existente
migrations/sql/0022_catastro_vistas_dsc_g_007_1.sql
migrations/sql/0023_rotor_activity_log.sql      ✅ mi ROTOR T1 mergeado

→ Siguiente número libre real: 0024
→ NOTA: Catastro S-CONTRATOS-001 aún NO mergeo. El spec ESCAPE-001 asumía
  que Catastro tomaría 0024+0025 y ESCAPE iría a 0026. Realidad actual:
  Catastro sigue en branch sprint/s-contratos-001-completo, no mergeado.
→ Decisión binaria propuesta: tomar 0024_escape_pulse_log.sql ahora.
  Si Catastro mergea ANTES que mi PR ESCAPE → colisión 0024.
  Mitigación: renumerar a primer libre real en momento de PR.

=== PB.3 embrion_budget.py funciones públicas ===
68:class BudgetDecision
84:class CycleResult
101:class _SupabaseRest
142:def _get_supabase_client
159:def estimate_cost_usd
185:def _today_iso_date
191:def check_before_cycle      ← decisión PRE-cycle
287:def record_after_cycle      ← persistencia POST-cycle
329:def record_aborted_cycle
362:def maybe_escalate_hitl
444:def daily_summary
476:def _group_cost_by_model
513:def add_recycled_energy     ← mi propio ROTOR T4

✅ Hallazgo importante: consume() NO EXISTE.
   Modelo del budget actual = declarativo + post-hoc (check antes, record después)
   NO es transaccional consume como asume el spec ESCAPE T4.
   T4 deberá CREAR consume() desde cero, alineada con el modelo existente.

=== PB.4 Marcadores en embrion_loop.py ===
$ grep -nE "ROTOR_LATIDO_BEGIN|ROTOR_LATIDO_END|ESCAPE_BEGIN|ESCAPE_END"
  → CERO HITS

Total LOC embrion_loop.py: 2404

✅ Hallazgo importante: NO existen marcadores ROTOR_LATIDO_BEGIN/END.
   El spec ESCAPE-001 §2.T3 y el kickoff §3.4 afirman que mi sprint ROTOR-001
   T2.6 los dejó. Verificado en commits: NO toqué embrion_loop.py en ROTOR-001.
   T3 de ESCAPE-001 sería el PRIMER sprint en agregar marcadores BEGIN/END a
   embrion_loop.py — establezco el patrón ESCAPE_BEGIN/END desde cero como
   template para sprints futuros.

=== PB.5 response_cache.py (input para PC) ===
$ wc -l = 181 LOC
$ grep ^def / ^async def / ^class:
  _normalize / _make_key / _is_cacheable / _evict_expired / _evict_lru
  get / store / stats / invalidate
```

---

## §4 PC — Audit Rubíes/Caché Semántica parcial existente

### §4.1 Qué hace `kernel/response_cache.py`

Docstring oficial:
> Sprint 39: Semantic Response Cache — Implementa cache de respuestas con TTL en memoria para reducir latencia en preguntas repetidas o similares. Basado en Redis Blog "Streaming LLM Responses" (abril 2026). Semantic matching via hash normalizado (sin dependencias externas). No requiere Redis. Para producción a escala se puede migrar a Redis LangCache.

**Configuración:**
- TTL: 300 segundos (5 min)
- Max size: 500 entries
- Min message length: 10 chars
- Max message length: 300 chars
- Cacheable intents: `chat`, `search`, `summarize`

**Storage:** dict en memoria `_response_cache: dict[str, dict]` con shape `{"response": str, "ts": float, "hits": int}`.

**API pública:** `get(message, intent)` → `Optional[str]` · `store(message, intent, response)` → `bool` · `stats()` · `invalidate(intent)`.

### §4.2 ¿Es la pieza Rubíes según doctrina §2.1?

**Parcialmente.** Cumple objetivos pero con limitaciones:

| Doctrina §2.1 fila 7 | response_cache.py actual | Cumple |
|---|---|---|
| "Puntos donde la información fluye sin consumir tokens de LLM" | Cache hit short-circuita LLM call | ✅ |
| "Fricción cero" | Hash + dict lookup O(1) | ✅ |
| **(implícito) Semántico real** | Hash normalizado por regex, NO embeddings | ❌ (es lexical, no semántico) |
| **(implícito) Persistente** | In-memory, se pierde en restart | ❌ |
| **(implícito) Cobertura amplia** | Solo 3 intents: chat/search/summarize | ❌ |

**Veredicto:** `response_cache.py` es una **versión proto/parcial** de Rubíes. Cumple el 40% de la doctrina §2.1 fila 7. Las funcionalidades faltantes (embeddings semánticos + persistencia + cobertura amplia) son scope de un futuro sprint **RUBIES-001** (mencionado en cascada del kickoff §8).

### §4.3 ¿Interactúa con Resorte/Áncora/Volante de forma que conflicte con Escape?

**CERO conflicto detectado.** Análisis:

- `response_cache.py` opera **antes del LLM call** (intercepta mensajes repetidos), nunca toca `embrion_budget` ni `embrion_scheduler` ni `embrion_loop` directamente.
- `Escapement` (a construir en ESCAPE-001 T2) opera **antes del consume()** (dosifica pulsos al budget).
- **Orden ideal en producción:**
  1. `response_cache.get()` → si **HIT**, retorna respuesta sin gastar pulso de Escape ni budget. Pieza Rubíes cumple su rol de "fricción cero".
  2. Si **MISS**, `Escapement.can_pulse()` → si bloqueado, espera. Si OK, `record_pulse(1.0)` consume budget. Ejecuta LLM call. Almacena en `response_cache.store()`.

No hay race conditions ni shared state mutable entre las dos piezas. Operan en planos distintos del ciclo.

### §4.4 Recomendación reuse vs build

- **NO tocar `response_cache.py` en este sprint** (out of scope ESCAPE-001).
- **Documentar la interacción ideal Rubíes↔Escape** en el postmortem T6 como diseño de ciclo canónico.
- **Sprint futuro RUBIES-001** se encarga de migrar a embeddings reales + persistencia + cobertura amplia.

---

## §5 Preguntas binarias para Cowork (pre-código)

Estas 4 preguntas son **bloqueantes blandos**: si Cowork no responde antes de gating triple verde, asumo la decisión por defecto documentada y arranco código:

### P1 — Áncora también consume budget (doctrina §4)?

**Contexto:** Doctrina §4 paso 2 dice *"El Áncora **y** el Escape liberan 1 unidad de energía por pulso"*. El spec ESCAPE T4 asume Escape como único caller de `consume()`.

**Pregunta binaria:** ¿`embrion_scheduler.py` (Áncora) también deberá consumir budget vía `consume()` en este sprint, o queda fuera de scope?

**Default si Cowork no responde:** Fuera de scope. ESCAPE-001 solo wirea `consume()` desde `Escapement.record_pulse()`. Cualquier integración con Áncora se difiere a sprint futuro `ANCORA-CONSUME-001`.

### P2 — `consume()` desde cero o refactor de `record_after_cycle()`?

**Contexto:** `embrion_budget.py` ya tiene `record_after_cycle()` que persiste consumo post-ejecución. `consume()` propuesta en spec es transaccional (chequea + decrementa atómico).

**Pregunta binaria:** ¿`consume(amount)` debe ser una **función nueva separada** o un **refactor de `record_after_cycle`** que la haga callable independiente?

**Default si Cowork no responde:** Función nueva separada (`async def consume(amount: Decimal) -> bool`), no rompe contratos existentes. Internamente delega a la misma capa de persistencia `_SupabaseRest`.

### P3 — Marcadores BEGIN/END en `embrion_loop.py` por primera vez?

**Contexto:** No existen marcadores ROTOR_LATIDO_BEGIN/END en el archivo actualmente. Yo seré el primero en agregar BEGIN/END.

**Pregunta binaria:** ¿Establezco yo el patrón `ESCAPE_BEGIN/END` desde cero o Cowork prefiere un patrón distinto (ej. `# >>> ESCAPE-001 <<<`)?

**Default si Cowork no responde:** Patrón verbatim del spec §2.T3 (líneas comentario `# ESCAPE_BEGIN — Sprint ESCAPE-001 2026-05-12` y `# ESCAPE_END — Sprint ESCAPE-001`). Patrón canónico para sprints futuros.

### P4 — Migration 0024 ahora o esperar Catastro?

**Contexto:** Última migración en main: `0023_rotor_activity_log.sql`. Catastro sigue en branch no mergeado (asumido en spec que tomaría 0024+0025).

**Pregunta binaria:** ¿Tomo `0024_escape_pulse_log.sql` ahora o reservo 0024+0025 para Catastro y voy a `0026`?

**Default si Cowork no responde:** Tomo `0024` ahora. Si Catastro mergea primero, renumero a primer libre real en momento de mi PR ESCAPE-001. Documento la dependencia explícita en el reporte de cierre.

---

## §6 Estado gating triple (timestamp 2026-05-12 ~07:30 UTC)

| # | Condición | Estado |
|---|---|---|
| (a) | Alfredo T1 firma el spec ESCAPE-001 | ⏳ pendiente |
| (b) | Perplexity T2-B converge sobre el spec post-PR #113 audit | ⏳ pendiente |
| (c) | PR #113 ROTOR-001 mergeado | ✅ verde (2026-05-12 06:56:06 UTC) |

**1/3 verde, 2/3 pendientes.** Sin las 3, NO arranco T1 código.

---

## §7 Recomendación final

**STANDBY hasta gating triple verde.** Mientras tanto:

1. Cero touch al código del kernel
2. Branch `sprint/ESCAPE-001` NO creado aún (esperar firma T1)
3. Cualquier ajuste al spec post-T2-B converge se incorpora antes del primer commit
4. Preparatorias PA + PB + PC documentadas en este reporte — input listo para arrancar T1-T6 en cuanto gating triple cierre

**ETA T1-T6 post-arranque:** 60-80 min reales con velocity demostrada en ROTOR-001 (29/29 tests en 0.05s, 6 tareas en ~30 min de sesión activa).

---

**Firma:** Manus Hilo Ejecutor 2 (`manus_hilo_b`), 2026-05-12

**Próxima señal del bridge a procesar:** disparo explícito de Cowork con (a) firma T1 + (b) T2-B converge declarado → arrancar T1 migración 0024 (o número libre que corresponda).
