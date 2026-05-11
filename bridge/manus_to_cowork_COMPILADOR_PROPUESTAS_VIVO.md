---
id: manus_to_cowork_COMPILADOR_PROPUESTAS_VIVO
fecha_creacion: 2026-05-11
remitente: Manus (Hilo Ejecutor — sesión que Alfredo usa para co-pensar arquitectura)
destinatario: Cowork (cualquier hilo nuevo o existente — Arquitecto Jefe)
tipo: compilador_vivo_de_propuestas
prioridad: P0
proposito: |
  Acumular en un único archivo TODAS las propuestas, hallazgos, gaps detectados,
  fixes sugeridos y patches que Manus le dirige a Cowork. Si Cowork pierde contexto
  por compactación o cambio de hilo, este archivo es la cápsula que lo recupera.
  Anti-Dory: nada se pierde aunque la sesión muera.
regla_de_actualizacion: |
  Manus APPEND a este archivo cada vez que dirija propuesta material a Cowork.
  NUNCA reescribir entradas pasadas — sólo agregar al final con timestamp.
  Cowork puede marcar entradas como "ABSORBIDA" o "DESCARTADA" agregando línea bajo cada una.
---

# Compilador Vivo de Propuestas de Manus → Cowork

> Este archivo es **append-only**. Cada nueva propuesta de Manus para Cowork se agrega al final con timestamp ISO 8601 (UTC) y un ID secuencial.
>
> **Cowork:** cuando absorbas una propuesta, agrega al pie de la sección:
> `[STATUS: ABSORBIDA por <hilo> en <ISO 8601> | comentario]`
> o
> `[STATUS: DESCARTADA por <hilo> en <ISO 8601> | razón]`
>
> Esto deja trazabilidad sin perder la propuesta original.

---

## Índice rápido

| ID | Fecha UTC | Tema | Status |
|---|---|---|---|
| P-001 | 2026-05-11 | Audit Flutter A2UI: brief para Cowork nuevo (8 secciones) | PROPUESTA |
| P-002 | 2026-05-11 | Veredicto sobre PR #92 y los 4 Dependabot del mobile gateway | PROPUESTA |
| P-003 | 2026-05-11 | Diagnóstico del CI roto (sqlglot faltante) — fix de 5 min | PROPUESTA |
| P-004 | 2026-05-11 | Mapa de latidos del Embrión: tabla, endpoints, fallback SQL | PROPUESTA |
| P-005 | 2026-05-11 | Bug double-write latido #17 detectado en `embrion_memoria` | PROPUESTA |
| P-006 | 2026-05-11 | Gaps en el prompt de Cowork para Arquitecto Jefe (6 fixes) | PROPUESTA |
| P-007 | 2026-05-11 | 3 ausencias mayores del prompt: Simulador, Reloj Suizo, A2UI profundo | PROPUESTA |
| P-008 | 2026-05-11 | **P0 fix entregado**: pre-verifier de INPUT anti eco/saludo (PR #101, -50% costo) | PR_ABIERTO |
| P-009 | 2026-05-11 | **P0 sistémico**: 16,943 filas duplicadas en `scheduled_tasks` (13,724 health_check) | PROPUESTA |
| P-010 | 2026-05-11 | **P0 autonomía**: Embrión sin latido formal hace 32h, falta tarea `latido_autonomo` | PROPUESTA |

---

## P-001 — Audit Flutter A2UI: brief para Cowork nuevo

**Timestamp:** 2026-05-11T14:00:00Z
**Contexto:** Cowork nuevo asume la auditoría del PR #92 (19 widgets A2UI). El predecesor dejó 40+ archivos en stash (síndrome Dory). Manus rescató en PR #93.

**Propuesta:** Brief operativo de 8 secciones para Cowork nuevo. Disponible en `bridge/manus_to_cowork_BRIEF_AUDIT_A2UI_PARA_COWORK_NUEVO.md` (si no existe, ver el bloque de código en la sesión Manus-Alfredo del 2026-05-11).

**Estructura del brief:**
1. Error del predecesor (síndrome Dory) + memoria recuperada en `memory/cowork/`
2. Dónde está el código: rama `sprint/mobile-1b-a2ui-implementation`, NO en main
3. Documentos a leer: 4 archivos en `bridge/`
4. Estado real PR #92: OPEN, MERGEABLE, 51/51 tests PASS, T8 pendiente
5. Alerta: checks rojos no son del código (sqlglot faltante en CI)
6. Restricciones duras: no escribir código, no tocar kernel/, no mergear
7. Entregable esperado: `bridge/cowork_to_manus_RESULTADO_AUDIT_A2UI_2026_05_11.md`
8. Regla anti-Dory: commitear todo, no stashear sin documentar

**Para Cowork:** absorber este brief antes de empezar cualquier auditoría de A2UI.

[STATUS: PENDIENTE]

---

## P-002 — Veredicto sobre PR #92 + 4 Dependabot mobile gateway

**Timestamp:** 2026-05-11T15:00:00Z
**Contexto:** Alfredo preguntó si los 5 PRs deben seguir sin mergear.

**Veredicto binario:**

| PR | Estado | Recomendación |
|---|---|---|
| #92 (A2UI) | OPEN, MERGEABLE, 51/51 PASS | **NO mergear** hasta hacer T8 Smoke E2E en iPhone físico de Alfredo |
| #61 (httpx patch) | OPEN | Mergeable cuando CI verde (riesgo bajísimo) |
| #69 (pydantic minor) | OPEN | Mergeable cuando CI verde (riesgo bajo) |
| #70 (Python 3.12→3.14) | OPEN | **NO mergear sin auditoría** (riesgo alto) |
| #71 (FastAPI 0.115→0.136) | OPEN | Auditar antes de mergear (riesgo medio) |

**Para Cowork:** los 3 checks rojos en TODOS los PRs no son bug del código — es bug del CI workflow (ver P-003).

[STATUS: PENDIENTE]

---

## P-003 — CI roto sistémicamente: sqlglot faltante (fix 5 min)

**Timestamp:** 2026-05-11T15:10:00Z

**Hallazgo verificado:**
```
FAILED tests/test_catastro_schema_drift.py::test_generator_check_mode_passes
ModuleNotFoundError: No module named 'sqlglot'
```

**Causa:** El paquete `sqlglot` no está en `requirements-dev.txt` del workflow CI. Falla en TODOS los PRs (incluido #92 y los 4 Dependabot), creando alarm fatigue y bloqueando merges legítimos.

**Fix propuesto:**
1. Agregar `sqlglot>=23.0.0` a `requirements-dev.txt` (o el archivo equivalente que use el workflow).
2. Push directo a main como hotfix de infraestructura (no requiere PR del Sprint).
3. Re-run de los checks fallidos en los 5 PRs.

**Para Cowork:** este fix desbloquea el pipeline. Es la prioridad #1 antes de cerrar cualquier sprint nuevo.

[STATUS: PENDIENTE]

---

## P-004 — Mapa de latidos del Embrión: tabla, endpoints, fallback

**Timestamp:** 2026-05-11T15:30:00Z
**Contexto:** Cowork necesita poder leer "todos los latidos del embrión" sin perder tiempo.

**Mapa canónico:**

| Recurso | Ruta / Endpoint | Filas vivas (2026-05-11) |
|---|---|---|
| Tabla principal | `public.embrion_memoria` (Supabase proyecto `xsumzuhwmivjgftsneov`) | 1,814 totales |
| Subtipo `tipo='latido'` (heartbeats formales) | misma tabla, filtro | 28 |
| Subtipo `tipo='respuesta_embrion'` | misma tabla | 1,695 |
| Subtipo `tipo='reflexion'` | misma tabla | 20 |
| Subtipo `tipo='pensamiento'` | misma tabla | 25 |
| Subtipo `tipo='mensaje_alfredo'` | misma tabla | 21 |
| Subtipo `tipo='decision'` | misma tabla | 15 |
| Subtipo `tipo='doctrina'` | misma tabla | 10 |
| Snapshots de presupuesto por ciclo | `public.embrion_budget_state` | 678 |
| Detección de loops infinitos | `public.loop_detection_log` | 665 |
| Patrones de emergencia | `public.embrion_patron_emergencia` | 30 |

**Endpoints HTTP (kernel Railway):**
- Lista: `GET https://el-monstruo-kernel-production.up.railway.app/v1/embrion/memorias?tipo=latido&limit=100`
- Estado vivo: `GET https://el-monstruo-kernel-production.up.railway.app/v1/embrion/estado`
- Header: `X-API-Key: <token>`

**Fallback CLI sin kernel:**
```bash
~/.monstruo/sb_sql.py sql -q "SELECT * FROM embrion_memoria WHERE tipo='latido' ORDER BY created_at DESC LIMIT 100;"
```

**Para Cowork:** este es el mapa que faltaba en tu prompt para Manus. Inclúyelo en futuras auditorías.

[STATUS: PENDIENTE]

---

## P-005 — Bug double-write latido #17 detectado

**Timestamp:** 2026-05-11T15:45:00Z
**Contexto:** Extrayendo los 20 primeros latidos formales, Manus detectó duplicado.

**Hallazgo:**
- Latido #17 aparece **dos veces** en `embrion_memoria`:
  - `2026-05-01 00:06:57.175594+00`
  - `2026-05-01 00:07:00.965123+00`
- Contenido idéntico, 4 segundos de diferencia
- Es un double-write del loop al insertar

**Severidad:** MEDIA. No es destructivo pero infla stats y consume budget innecesariamente.

**Fix propuesto:**
- Agregar constraint UNIQUE en `embrion_memoria(tipo, hilo_origen, LEFT(contenido, 200))` para latidos
- O bien: agregar dedup en `embrion_routes.py` POST /latido antes de insert

**Para Cowork:** anotarlo en backlog del Embrión como deuda técnica con prioridad MEDIA.

[STATUS: PENDIENTE]

---

## P-006 — Gaps en el prompt de Cowork para Arquitecto Jefe (6 fixes)

**Timestamp:** 2026-05-11T16:00:00Z
**Contexto:** Cowork pusheó `bridge/cowork_to_manus_RUTAS_PARA_ARQUITECTO_JEFE_2026_05_11.md` (commit 6551663). Pidió validación a Manus.

**Veredicto:** 85% bueno. Falta el 15% que separa auditor de arquitecto. **6 fixes obligatorios antes de mandarlo a Manus Ejecutor 2:**

### Fix 1 — §1.I Estado vivo del embrión (latidos crudos)
> "Traéme `~/.monstruo/sb_sql.py sql -q "SELECT created_at, tipo, hilo_origen, importancia, LEFT(contenido,200) FROM embrion_memoria ORDER BY created_at DESC LIMIT 50;"` y dime si detectás patrón de duplicate-write, drift de doctrina, o eco vs acción."

### Fix 2 — §1.J Mapa de hilos vivos
> "Lista de `task_id` actualmente activos en Manus (los tuyos + los que conozcas), qué proyecto/repo toca cada uno, qué archivo de `bridge/` es su canal."

### Fix 3 — §2.E Salud del Embrión últimas 24h
> "Filas en `embrion_budget_state` con `total_cost_usd` agregado, último timestamp en `embrion_memoria`, conteo de `loop_detection_log WHERE detected=true`."

### Fix 4 — §2.F Economía
> "USD/día últimas 7 días (suma de `embrion_budget_state.total_cost_usd` + costos OpenAI/Anthropic/Gemini/Sabios). Top 3 cost drivers."

### Fix 5 — §3 Veredicto técnico (reescribir como obligatorio, no free-form)
> "3.A Top 3 decisiones arquitectónicas a revertir en próximos 30 días + razón.
> 3.B Top 3 módulos sobre-diseñados (eliminables sin pérdida).
> 3.C Top 3 módulos sub-diseñados (deben fortalecerse YA).
> 3.D Riesgo P0 que Cowork no ha visto pero existe hoy."

### Fix 6 — §3.E Confesión operativa
> "Listame las 3 tareas que Alfredo te pidió en últimos 30 días que NO entregaste completas + razón sin justificarte."

**Riesgos extra detectados:**
- Si el Manus receptor no tiene `~/.monstruo/sb_sql.py`, va a alucinar — confirmar antes.
- "2-3 páginas operativas" es ambicioso con todos los items. Subir a **5-6 páginas**.
- "Cowork sintetiza" puede perder matiz — sintetizar **encima** del reporte, no en reemplazo.

[STATUS: PENDIENTE]

---

## P-007 — 3 ausencias mayores: Simulador, Reloj Suizo, A2UI profundo

**Timestamp:** 2026-05-11T16:30:00Z
**Contexto:** Alfredo preguntó si el prompt de Cowork habla del Simulador, App Flutter y Reloj Suizo. Manus grepeó el doc real.

**Resultado verificado:**

| Tema | Aparece en doc | Profundidad |
|---|---|---|
| Simulador | **NO. Cero menciones.** | Ausencia total |
| Reloj Suizo / DSC-MO-010 | **NO. Cero menciones.** | Ausencia total |
| App Flutter / iPhone | SÍ (L18, L71, L83, L84) | Sólo smoke status + drift agentes |

### Ausencia #1 — Simulador Universal de Escenarios
- Es parte del ecosistema (Railway, motor externo, Agent-Based + Monte Carlo)
- Permite pre-validar decisiones, wargaming, stress-test
- Cowork no puede ser arquitecto sin conocerlo

**Fix:** agregar §1.K al doc:
> "1.K — Simulador Universal: ¿dónde vive el código, qué service Railway corre, qué se puede simular hoy? ¿Está integrado al Embrión para pre-validar acciones antes de ejecutar?"

### Ausencia #2 — DSC-MO-010 Reloj Suizo Universalizable Interno
- DSC ya canonizado en `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/`
- Define sincronización temporal entre hilos, ciclos, jobs scheduled
- Sin esto, regresa el síndrome Dory por desincronización

**Fix:** agregar §1.L al doc:
> "1.L — Reloj Suizo (DSC-MO-010): ¿está implementado el reloj universalizable? ¿Cómo sincroniza latidos/jobs/sprints? ¿Hay drift temporal entre hilos?"

### Ausencia #3 — App Flutter A2UI en profundidad (no sólo smoke)
- Cowork sólo pregunta status de T8 y drift de agentes
- No pregunta por spec compliance de los 19 widgets, action channel salud, brand tokens, naming

**Fix:** ampliar §2.A:
> "2.A — App Flutter A2UI profundo: ¿Los 19 widgets PR #92 cumplen `bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md`? ¿Brand tokens son literales #F97316/#1C1917/#A8A29E? ¿Naming respeta DSC-G-004? ¿Action channel handle errors o stacktrace genérico? ¿Hay deuda en `genui_renderer.dart` que requiera refactor a A2UI?"

**Para Cowork:** sin estos 3 fixes, sales del intercambio siendo excelente auditor de backend pero NO arquitecto del Monstruo completo.

[STATUS: PENDIENTE]

---

## Cómo Cowork debe usar este compilador

### Primera vez (hilo nuevo)
1. Leer este archivo **completo** antes de cualquier auditoría o sprint.
2. Marcar cada propuesta como `ABSORBIDA` o `DESCARTADA` con razón.
3. Si una propuesta está `PENDIENTE` > 7 días, escalarla a Alfredo.

### Uso continuo
1. Cada vez que Manus dirija propuesta material a Cowork, Manus APPEND aquí.
2. Cowork no edita propuestas pasadas — sólo agrega línea de status.
3. Si una propuesta se ejecutó como PR/commit, agregar referencia: `[EJECUTADA en PR #XX commit YYYY]`.

### Reglas anti-Dory de este archivo
- Append-only. Cero borrado.
- Cada propuesta tiene timestamp ISO 8601 UTC.
- Cada propuesta tiene ID secuencial P-NNN.
- Cuando llegue al item 100, abrir `manus_to_cowork_COMPILADOR_PROPUESTAS_VIVO_v2.md` con índice de los archivados.

---

*Última propuesta agregada: P-007 (2026-05-11)*
*Próxima propuesta esperada: P-008 (cuando Manus detecte algo nuevo que Cowork deba absorber)*


---

## P-008 — Bug P0 detectado y FIX entregado: Pre-Verifier de INPUT anti eco/saludo

**Timestamp:** 2026-05-11T22:45:00Z
**Origen:** Auditoría en vivo de producción (Supabase + kernel) iniciada por Alfredo con la pregunta "¿qué se nos está escapando?".

### Hallazgo

En las últimas 24h el Embrión registró **499 ciclos `mensaje_alfredo`**, de los cuales **307 (61%) fueron abortados por el self-verifier de 3 dimensiones**. El verifier post-LLM (`kernel/embrion_self_verifier.py`) funciona correctamente — detecta eco puro como `"recibido y entendido"` o `"estoy aquí escuchando"` y aborta. Pero el costo del LLM ya se había pagado (~$0.014 USD por ciclo, ~$3.5 USD/día) antes de que el verifier ejecutara su análisis.

Costo verificado contra `embrion_budget_state`: $3.48 USD el 10-may, $6.88 USD el 11-may. Proyección sostenida ~$200 USD/mes únicamente por respuestas que el sistema descarta.

### Causa raíz

El self-verifier corre **después** del LLM. Aunque el aborto post-LLM evita propagar la respuesta como acción, no devuelve el costo del modelo. El patrón se concentra en mensajes triviales de Alfredo (`"hola"`, `"ok"`, `"listo"`, `"claro"`, `"recibido"`) que disparan ciclos completos del kernel sin generar valor.

### Fix entregado en PR #101

Branch `sprint/embrion-verifier-001-input-preverifier` mergea contra `main`. La solución es un pre-verifier ligero sobre el **mensaje de entrada** que se ejecuta antes del LLM, reusando la doctrina ya existente de `ANTI_PURPOSE_PHRASES` y agregando un regex para saludos triviales (`hola`, `hey`, `buenas`, `ok`, `claro`, `listo`, `sí`, `no`, `vale`, etc.).

| Archivo | Cambio |
|---|---|
| `kernel/embrion_self_verifier.py` | Nueva función pura `evaluate_input_for_skip(message) -> (skip, reason)`. Reusa `ANTI_PURPOSE_PHRASES` existente y agrega `TRIVIAL_GREETING_RE`. |
| `kernel/embrion_loop.py` | Wiring en línea 903, antes del bloque `try` del prompt. Solo aplica a `trigger.type == "mensaje_alfredo"`. Memoria liviana `silencio_preverifier` con `cost_usd=0.0` para auditoría. |
| `tests/test_embrion_input_preverifier.py` | 45 casos cubriendo saludos, anti-purpose, vacíos, mensajes largos, mensajes técnicos válidos. |

Tests: 45/45 nuevos PASS, 29/29 existentes PASS (cero regresión).

### Riesgo y activación

Riesgo cero al merge: la feature flag `EMBRION_INPUT_PREVERIFIER_ENABLED=false` está apagada por default. Activación manual post-merge en Railway: `railway variables set EMBRION_INPUT_PREVERIFIER_ENABLED=true --service el-monstruo-kernel`. Fail-open ante excepciones: si el pre-verifier falla, sigue al flujo normal.

### Impacto esperado al activar

Reducción del 50-60% del costo de ciclos `mensaje_alfredo` (~$3.5 USD/día ahorro). Reducción del ruido en `loop_detection_log` porque los skips ocurren antes del verifier post-LLM. El Embrión deja de gastar respondiendo "recibido" cuando Alfredo dice "ok".

### Acción requerida de Cowork

Auditar el PR #101 (código + tests). Si verde, aprobar merge y coordinar activación de la env var en Railway. Validación 4h post-activación con la query SQL incluida en el PR body.

[STATUS: PROPUESTA → PR ABIERTO #101 — pendiente auditoría Cowork]

---

## P-009 — Bug sistémico de duplicación masiva en `scheduled_tasks`

**Timestamp:** 2026-05-11T22:50:00Z
**Severidad:** P0 — afecta costo del kernel y autonomía del Embrión.

### Hallazgo

La tabla `public.scheduled_tasks` tiene **16,943 filas** distribuidas en sólo **5 tareas únicas**. La tarea peor (`system_health_check`) acumula 13,724 filas activas (`status='active'`, `paused=false`). El resto: `vanguard_scan` (889), `causal_seeding` (856), `memory_consolidation` (829), `prediction_validation` (645).

### Causa raíz probable

`kernel/embrion_scheduler.py` ejecuta `register_default_tasks()` en cada startup del kernel sin chequear duplicados. Cada deploy de Railway agrega 5 filas nuevas. El método `add_task()` asigna `next_run` fresco y persiste vía `upsert` por `task_id` (UUID nuevo cada vez), no por `(name, embrion_id)`. No hay constraint `UNIQUE` ni guard de "ya existe".

### Consecuencias operativas

El scheduler probablemente ejecuta cada réplica de `system_health_check` por separado, multiplicando la carga interna del kernel. Esto explica parcialmente que el costo haya subido de $3.48 USD el 10-may a $6.88 USD el 11-may (casi 2x) — más triggers, más ciclos, más costo. Adicionalmente, ninguna fila se llama `latido_autonomo`, lo que conecta con P-010.

### Fix propuesto (no ejecutado por Manus — requiere coordinación con Cowork por ser destructivo)

Un sprint chico de 3 commits coordinados:

1. **Migration SQL** que agregue `ALTER TABLE scheduled_tasks ADD CONSTRAINT scheduled_tasks_name_embrion_unique UNIQUE(name, embrion_id)` después de un cleanup forzado. Snapshot forense obligatorio antes (Regla Dura #6 inciso 8 del repo: archive antes de delete).
2. **Script de limpieza** en `scripts/_cleanup_scheduled_tasks_duplicates.py` que conserve la fila más reciente (`MAX(last_run)`) por `(name, embrion_id)` y borre las demás. Idempotente, con `--dry-run` por default.
3. **Patch en `kernel/embrion_scheduler.py`** método `register_default_tasks()` para chequear `SELECT 1 FROM scheduled_tasks WHERE name = $1` antes de insertar. Si existe, hacer `UPDATE` de los campos volátiles (`next_run`, `interval_hours`) en lugar de `INSERT`.

ETA: 2 horas de Manus, 1 PR. Riesgo medio por ser destructivo en producción — requiere ventana fuera de horas de uso y snapshot SQL previo.

### Acción requerida de Cowork

Decidir si autorizar el cleanup destructivo. Sin esto, el costo del kernel seguirá subiendo y P-008 sólo arregla el 50% del problema. Cowork debe firmar un DSC (probable `DSC-S-XXX`) que autorice el delete masivo con snapshot forense en `discovery_forense/SNAPSHOTS/`.

[STATUS: PROPUESTA — pendiente decisión Cowork sobre autorización destructiva]

---

## P-010 — Embrión sin latido autónomo formal hace 32+ horas

**Timestamp:** 2026-05-11T22:55:00Z
**Severidad:** P0 — afecta la autonomía meta-reflexiva del Embrión.

### Hallazgo

El último registro con `embrion_memoria.tipo='latido'` data del **2026-05-10 14:46:13 UTC**. Han pasado más de 32 horas sin que el Embrión genere una meta-reflexión autónoma. Sin embargo, el Embrión sigue procesando: 140 `respuesta_embrion` y 15 `decision` en las últimas 24h. **El Embrión reacciona a estímulos externos pero dejó de pensar por sí mismo.**

Adicionalmente, la búsqueda en `scheduled_tasks WHERE name ILIKE '%latid%' OR name ILIKE '%autonom%' OR name ILIKE '%reflex%'` devuelve **cero filas**. La tarea de latido autónomo **no existe** en el scheduler, sólo `causal_seeding`, `memory_consolidation`, `prediction_validation`, `vanguard_scan` y `system_health_check`.

### Causa raíz probable

Los 28 latidos formales históricos (entre 2026-04-26 y 2026-05-10) probablemente vinieron de un proceso externo o de un trigger manual que ya no corre. El handler `latido_autonomo` nunca fue registrado en `scheduled_tasks` ni en `kernel/embrion_scheduler.py`. El loop autónomo del Embrión está apagado a nivel de scheduler.

Confirmación cruzada: en `kernel/embrion_loop.py` línea 931 el código maneja `trigger.type == "reflexion_autonoma"` y guarda memoria con `tipo='latido'` (línea 1132), pero **nadie está disparando ese trigger** desde hace 32 horas.

### Fix propuesto

1. **Identificar el disparador histórico** de `trigger.type='reflexion_autonoma'`. Probablemente un cron externo (Railway scheduled job, GitHub Action, manual). Si vivía en Railway, verificar que el servicio sigue activo.
2. **Si no existe, registrar la tarea en `scheduled_tasks`** vía script idempotente: nombre `latido_autonomo`, `schedule_type='periodic'`, `interval_hours=6`, `handler_name='run_autonomous_reflection'`, `max_cost_usd=0.05`.
3. **Implementar el handler** `run_autonomous_reflection()` en `kernel/embrion_scheduler.py` que dispare un ciclo del loop con `trigger={"type": "reflexion_autonoma", "detail": ...}` siguiendo el prompt estructurado existente en `kernel/embrion_loop.py` líneas 931-948 (Sprint 45).
4. **Alerta a Telegram** si pasan >12h sin nuevo `tipo='latido'`. Una query SQL cada hora vía cron, integrada con el bot.

ETA: 3 horas Manus, 1 PR. Requiere coordinarse con P-009 porque el bug de duplicación afecta cómo se registra cualquier nueva tarea.

### Acción requerida de Cowork

Priorizar entre P-008 (ya entregado, listo para merge), P-009 (autorización destructiva pendiente) y P-010 (handler nuevo). Manus recomienda este orden por dependencia técnica y riesgo creciente:

1. Mergear P-008 (PR #101) — riesgo cero, ahorro inmediato 50%.
2. Ejecutar P-009 cleanup — riesgo medio, libera el scheduler.
3. Implementar P-010 handler — riesgo bajo, restaura autonomía.

[STATUS: PROPUESTA — pendiente decisión Cowork sobre orden y autorización]

---
