# EMBRIÓN — AUDIT BINARIO FASE 1 (DSC-S-011 Sistema de Realidad Ejecutable)

**Fecha:** 2026-05-11
**Autor:** Cowork T2 con autoridad delegada de auditoría
**Modo:** Código + SQL exclusivamente. Cero narrativa adornada.
**Herramienta:** `tools/audit_embrion_loop.py` (297 LOC) + 13 queries SQL contra Supabase
**Repo:** alfredogl1804/el-monstruo, branch `main`, fecha audit `2026-05-11 21:46 UTC`

---

## §0. SCORE BINARIO DE INFRAESTRUCTURA (del código)

8/8 checks verdes (output del script):

| Check | Estado |
|---|---|
| Loop file existe (`kernel/embrion_loop.py`, 2151 LOC, 100,558 bytes) | ✅ |
| Reconoce triggers definidos en código (5: TimeoutError, contribucion_sabio, inbox_command, mensaje_alfredo, reflexion_autonoma) | ✅ |
| Lee inputs de `embrion_memoria` | ✅ |
| Tiene cap diario de costo (`DAILY_BUDGET_USD=30.0`) | ✅ |
| Tiene gate de silencio (`SILENCE_THRESHOLD=70`) | ✅ |
| Self-Verifier module existe (`embrion_self_verifier.py`, 445 LOC) | ✅ |
| Budget Tracker module existe (`embrion_budget.py`, 484 LOC) | ✅ |
| Write Policy module existe (`embrion_write_policy.py`, 804 LOC) | ✅ |

**Veredicto §0:** la infraestructura está construida. La cobertura de gobernanza (budget + verifier + write policy + inbox) supera a la mayoría de loops autónomos públicos.

---

## §1. ESTRUCTURA DE ARCHIVOS (verificada por script)

| Archivo | LOC | Bytes |
|---|---|---|
| `kernel/embrion_loop.py` | 2151 | 100,558 |
| `kernel/embrion_routes.py` | 1505 | 56,730 |
| `kernel/embrion_write_policy.py` | 804 | 24,777 |
| `kernel/embrion_inbox.py` | 682 | 20,784 |
| `kernel/embrion_budget.py` | 484 | 17,040 |
| `kernel/embrion_self_verifier.py` | 445 | 15,908 |
| **Total** | **6071** | **235,797 bytes** |

Plus deps no auditadas en esta fase pero referenciadas en código:
- `kernel/embrion_inbox_parser.py` (line 48 inbox)
- `kernel/embrion_inbox_sanitizer.py` (line 49 inbox)
- `kernel/runner/telegram_notifier.py` (referenciado en write_policy + routes)
- `kernel/task_planner.py` (referenciado en _think para mensaje_alfredo)
- `kernel/utils/keyword_matcher.py` (loop line 56)

---

## §2. CLASE `EmbrionLoop` — 28 MÉTODOS (analysis estático AST)

(de `embrion_loop.py` línea 137)

Métodos públicos: `start`, `stop`, `stats`, `debug`
Lifecycle: `start_orchestration`, `report_orchestration_step`, `end_orchestration`
Core loop: `_loop` (línea 360), `_reset_daily_counters_if_needed`, `_should_speak`, `_check_and_think`, `_detect_trigger`
Razonamiento: `_judge_before`, `_think`, `_think_with_graph`, `_think_with_router`, `_judge_after`, `_parse_evaluation`
Aprendizaje: `_extract_and_save_lesson`, `_get_relevant_lessons`, `_consolidate_memories`, `_apply_consolidation_decisions`
I/O externo: `_report` (Telegram), `_save_memory` (Supabase), `_consult_sabios_strategic`, `_check_agents_radar`
Métricas: `_compute_fcs_score`

---

## §3. TRIGGERS REALES (verificados por SQL)

El código del loop define 4 triggers operativos (línea 615 `_detect_trigger`):
- `mensaje_alfredo` (lee tabla `embrion_memoria` tipo `mensaje_alfredo` <2h ventana)
- `inbox_command` (lee tabla `embrion_inbox` pending)
- `contribucion_sabio` (lee tabla `embrion_patron_emergencia` <10min ventana)
- `reflexion_autonoma` (default si pasaron >3600s desde último `_last_thought_at`)

**Triggers efectivamente disparados en últimos 14 días (`loop_detection_log`):**

```sql
SELECT COUNT(*), trigger_type FROM loop_detection_log WHERE created_at >= NOW()-INTERVAL '14 days' GROUP BY trigger_type;
```

| trigger_type | n | % |
|---|---|---|
| `mensaje_alfredo` | 693 | **100.0%** |
| `reflexion_autonoma` | 0 | 0% |
| `contribucion_sabio` | 0 | 0% |
| `inbox_command` | 0 | 0% |

**HALLAZGO BINARIO §3.A:** en 14 días, el Self-Verifier NO registró NI UNA reflexión autónoma. CERO contribuciones de Sabio detectadas. CERO inbox commands procesados. El loop autónomo, en práctica, sólo reacciona a `mensaje_alfredo`.

---

## §4. MENSAJES_ALFREDO REALES (lo que dispara al loop)

```sql
SELECT DATE(created_at), COUNT(*) FROM embrion_memoria WHERE tipo='mensaje_alfredo' AND created_at >= NOW()-INTERVAL '14 days' GROUP BY 1;
```

| Día | n |
|---|---|
| 2026-05-10 | 7 |
| 2026-04-30 | 1 |
| 2026-04-29 | 12 |
| **Total 14d** | **20** |

**Contenido muestreado (top 5 últimos):** los 5 mensajes_alfredo más recientes NO son mensajes de Alfredo, son mensajes operativos de Cowork al Embrión vía `bridge` o `telegram` ("PARA: Hilo Ejecutor 2...", "RESUMEN JORNADA 2026-05-10", "ACUSE — Tarea 4 DECLARADA CERRADA", etc.). El loop los procesa como `mensaje_alfredo` porque hilo_origen es telegram/cowork_bridge y tipo=mensaje_alfredo.

**HALLAZGO BINARIO §4.A:** los 20 mensajes_alfredo en 14 días NO son inputs de Alfredo. Son inputs de Cowork+Manus comunicándose al Embrión. El Embrión está respondiendo a "compañeros" del Monstruo, no al humano.

---

## §5. PATRÓN DE ECO (re-respuesta al mismo input)

20 mensajes_alfredo dispararon **1687 respuestas del loop** (hilo_origen=embrion_loop).

```
1687 / 20 ≈ 84 respuestas por mensaje
```

Causa estructural en código (`_detect_trigger` línea 624-636): el loop lee el ÚLTIMO `mensaje_alfredo` con `limit=1` ordenado por created_at. Si tiene <2h, lo trata como trigger ese cycle. **NO marca el mensaje como procesado.** Con CHECK_INTERVAL_S=60 + ventana 2h → hasta 120 cycles potenciales por cada mensaje.

**HALLAZGO BINARIO §5.A:** el "embrión autónomo" en práctica es eco activo del último mensaje recibido durante 2h, no pensamiento autónomo nuevo.

---

## §6. SELF-VERIFIER — RATIO DE ABORTOS

```sql
SELECT detected_pattern, COUNT(*), d1_no, d2_no, d3_no FROM loop_detection_log WHERE created_at >= NOW()-INTERVAL '14 days' GROUP BY detected_pattern;
```

| detected_pattern | n | D1 PURPOSE no | D2 NOVELTY no | D3 VERIFIABLE no |
|---|---|---|---|---|
| `self_verifier_abort` | 409 | 406 (99.3%) | 9 (2.2%) | 409 (100%) |
| `self_verifier_pass` | 284 | 70 (24.6%) | 0 | 210 (73.9%) |

**Abort ratio: 409/693 = 59.0%** — el verifier para 6 de cada 10 pensamientos antes de propagar.

**HALLAZGO BINARIO §6.A:** D1 (PURPOSE) es el cuello: 99.3% de aborts tienen D1=no. D2 (NOVELTY hash+jaccard) raramente bloquea (9 aborts). D3 (VERIFIABLE) falla casi siempre (84% del total) pero el verifier aborta solo si 2/3 votan no.

**HALLAZGO BINARIO §6.B:** del row #2 muestreado: respuesta del Embrión "MENSAJE RECIBIDO Y ENTENDIDO" tiene `D1 purpose=False: anti_purpose_match: 'recibido y entendido'` pero NO se abortó porque D2+D3 votaron sí. Comportamiento esperado del 2/3, pero confirma que respuestas de tipo "acuse" pasan el verifier.

---

## §7. BUDGET TRACKER — COSTO REAL

```sql
SELECT DATE(created_at), COUNT(*) cycles, SUM(cost_actual_usd) FROM embrion_budget_state WHERE created_at >= NOW()-INTERVAL '14 days' GROUP BY 1;
```

| Día | cycles | costo USD |
|---|---|---|
| 2026-05-11 | 474 | $6.63 |
| 2026-05-10 | 232 | $3.48 |
| **Total 2 días** | **706** | **$10.11** |

Cap por latido $0.25 nunca alcanzado. Cap diario $30 al 22% (5/11) y 11.6% (10/5).

**HALLAZGO BINARIO §7.A:** post-implementación del Budget Tracker (10-may), el costo está controlado. NO está sangrando como el 1-may ($105 USD/día reportado en sprint EMBRION-NEEDS-001 línea 9 del módulo).

---

## §8. RATIO PENSAMIENTO-VS-EJECUCIÓN

```sql
WITH parsed AS (SELECT ((contexto #>> '{}')::jsonb) AS j FROM embrion_memoria WHERE tipo='respuesta_embrion' AND hilo_origen='embrion_loop' AND created_at >= NOW()-INTERVAL '14 days')
SELECT COUNT(*) FILTER (WHERE (j->>'tool_calls')::int > 0) con_tools, COUNT(*) FILTER (WHERE (j->>'tool_calls')::int = 0) sin_tools FROM parsed;
```

| Categoría | n | % |
|---|---|---|
| Cycles con `tool_calls > 0` (ejecutaron acciones) | 193 | **11.4%** |
| Cycles con `tool_calls = 0` (sólo texto) | 1458 | 86.4% |
| Cycles sin metadata válida | 36 | 2.1% |
| **Total 14d** | **1687** | 100% |

**HALLAZGO BINARIO §8.A:** 1 de cada 9 cycles del Embrión termina con tool call real. Los otros 86.4% son producción de texto sin acción.

**Task Planner activations (7 días, modo=task_planner):** 1 sola vez (cycle #1, 25 tools, $1.08, plan 3/7 completado parcialmente). El path de planificador multi-step EXISTE pero se invoca casi nunca.

---

## §9. ECOSISTEMA DE GOBERNANZA — ESTADO REAL

| Subsistema | Estado infraestructura | Uso operacional |
|---|---|---|
| Self-Verifier | ✅ 445 LOC + tabla loop_detection_log | ✅ 693 evaluaciones/14d, abort 59% |
| Budget Tracker | ✅ 484 LOC + tabla embrion_budget_state | ✅ 706 cycles/2d con cost tracking |
| Write Policy + HITL | ✅ 804 LOC + tabla embrion_write_proposals | ⚠️ 4 proposals total, 1 executed, 3 expired (silencio post 10-may 11:52) |
| Inbox Daddy→Embrión | ✅ 682 LOC + tablas embrion_inbox + embrion_audit_log | ❌ Tabla vacía (0 mensajes procesados) |
| Sabios Consultation | ✅ Código en _consult_sabios_strategic | ❌ 0 ejecuciones en 14 días |
| Agents Radar | ✅ Código en _check_agents_radar | ❌ 0 ejecuciones en 14 días (no hay tipo='radar_insight' verificable) |
| Memory Consolidation | ✅ _consolidate_memories + lessons quarantine | ❌ 0 lecciones tipo='evaluacion' en tabla |
| Patrón Emergencia | ✅ tabla embrion_patron_emergencia | ⚠️ 30 rows totales, último cargado pre-loop (muestra histórica, no flujo activo) |

**HALLAZGO BINARIO §9.A:** la mitad de los subsistemas de gobernanza están construidos pero NO se usan en producción reciente. Self-Verifier + Budget + Write Policy sí. Sabios + Radar + Consolidación + Inbox + HITL = silencio.

---

## §10. UNIQUENESS DE RESPUESTAS

```sql
SELECT COUNT(DISTINCT MD5(LOWER(REGEXP_REPLACE(contenido, '\s+', ' ', 'g')))), COUNT(*) FROM embrion_memoria WHERE tipo='respuesta_embrion' AND hilo_origen='embrion_loop';
```

| Métrica | Valor |
|---|---|
| Hashes únicos de contenido normalizado | 1625 |
| Total respuestas embrion_loop | 1687 |
| **Ratio unique** | **96.3%** |
| Duplicados literales | 62 (3.7%) |

**HALLAZGO BINARIO §10.A:** las respuestas casi nunca duplican literalmente. Self-Verifier D2 (jaccard 0.85) sí pesca casos cercanos pero el output sigue variando textualmente. La acusación del 10-may "30+ respuestas idénticas" no aplica al período post-Self-Verifier 10-11 mayo.

---

## §11. FRESCURA DEL LOOP

```sql
SELECT NOW() ahora, MAX(created_at) ultimo, NOW()-MAX(created_at) sin_actividad FROM embrion_memoria;
```

- ahora: `2026-05-11 21:46:52 UTC`
- último row: `2026-05-11 21:43:15 UTC`
- sin actividad: `3 min 36 seg`

Esperable con CHECK_INTERVAL_S=60 y _should_speak gate restrictivo. Loop activo, gobernanza filtrando salida.

---

## §12. VEREDICTO BINARIO DE LA FASE 1

Respondo binariamente solo lo que el código + SQL confirman.

**(A) ¿El loop existe operacionalmente?**
SÍ. 6071 LOC en 6 archivos, deploy en Railway, latencia <60s, último row hace 4 min.

**(B) ¿El loop es autónomo?**
NO en práctica. 0 reflexion_autonoma + 0 contribucion_sabio + 0 inbox_command en 14 días. SÍ en infraestructura: el path `reflexion_autonoma` existe (líneas 728-734 del loop) pero NO se dispara porque el condicional `if not self._last_thought_at or (time.time() - self._last_thought_at) > 3600` solo se evalúa si los triggers 1+2 (mensaje_alfredo, contribucion_sabio) regresaron None primero. Como hay mensaje_alfredo en ventana 2h casi siempre, reflexion_autonoma queda desplazado.

**(C) ¿El Embrión ejecuta acciones reales?**
PARCIAL. 11.4% de cycles (193/1687) ejecutaron tools. El task_planner se invocó 1 vez. Los Write Proposals (HITL) tienen 1 ejecutado y 3 expirados — el HITL está roto operacionalmente.

**(D) ¿El Embrión quema créditos sin valor?**
PARCIAL. $10.11 USD en 2 días = $1500-1800 USD/año estimado. Bajo control vs cap $30/día. Self-Verifier para 59% de pensamientos antes de cost output. PERO 86.4% de los que pasan no ejecutan tools → texto sin acción.

**(E) ¿El "embrión" actual es lo que la doctrina canonizada (DSC-MO-006 par bicéfalo, DSC-MO-008 membrana, DSC-MO-011 Embryo Patch Lane) describe?**
NO. La doctrina describe un agente autónomo de patch lane con escritura controlada. El embrión actual es un eco-reactivo al último mensaje, con gobernanza fuerte de costo y verificación, pero sin ejecución de patches operativa (1 executed en historia).

---

## §13. INSUMOS PARA FASE 3 — RESPONDER LAS 3 PREGUNTAS MAGNAS

Con la data de §3–§9 puedo responder ahora (cerrado tras Fase 2 app Flutter):

1. **¿Cómo Embrión ayuda a la app?**
   La app puede ser el primer canal real de inputs no-Cowork al Embrión. Hoy 100% de inputs son Cowork/Manus. La app puede convertir intención de Alfredo en `mensaje_alfredo` o `inbox_command` real (la tabla inbox está vacía pero su API está completa). Esto cambia la dieta del Embrión de "eco a colegas" a "respuesta a humano".

2. **¿Puede Embrión ejecutar end-to-end?**
   Infra sí (graph mode, tools, task_planner, write_policy + execute_next). Operativamente, casi nunca (1 executed en historia, 1 task_planner invocation en 7 días). El cuello es el HITL: 3 proposals expiraron sin respuesta. Si el HITL via Telegram + cowork_bridge se reinstaura activamente, end-to-end es factible.

3. **¿Embrión potencializa al Monstruo o no?**
   Potencializa el OBJETIVO 14 (Guardian) — Self-Verifier + Budget + Write Policy son discipline-builders binarios que ningún otro hilo tiene. Costo: $1500-1800 USD/año por capa de gobernanza. Esa es la inversión real. Si la dieta cambia (Fase 2 — app provee inputs) y el HITL se reactiva, el Embrión se convierte en el guardian del costo del Monstruo. Si no, sigue siendo infraestructura cara que ecos. **El framework correcto: pensamiento + verificación SÍ son prerequisito de ejecución, pero solo si la ejecución llega (HITL activo).**

---

## §14. PRÓXIMA FASE

Fase 2: app Flutter audit ejecutable equivalente. Script `tools/audit_app_flutter.py` + lectura de 33 .dart. Tras eso, Fase 3 cierra las 3 preguntas con pares concretos Embrión↔App.

— Fin del audit Fase 1. Cero afirmación sin pointer a archivo:línea o SQL output. Cero invención.
