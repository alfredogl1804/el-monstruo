<!-- lint_strict -->

# Sprint ROTOR-001 — Reciclador de Actividad (pieza diferencial Reloj Suizo)

**estado:** DRAFT_PENDIENTE_FIRMA_T1
**autor_borrador:** Cowork T2 (Sprint SPECS-FIRMA-001 ampliado, 2026-05-11)
**autorización_T1:** pendiente Alfredo
**Hilo principal:** Manus Ejecutor (implementación) + Cowork (diseño doctrinal + audit)
**ETA recalibrado:** 4-7 días reales — más complejo que Guardian porque agrega código de fondo nuevo + integraciones
**Objetivo Maestro:** #11 (Multiplicación de Embriones + Reloj Suizo) + #15 (Memoria Soberana — captura actividad como memoria persistente) + #8 (Inteligencia Emergente Colectiva — la actividad alimenta emergencia)
**Bloqueos pre-arranque:** ninguno — pero **Sprint GUARDIAN-AUTONOMO-001 recomendado primero** porque el Rotor sin Guardian que valide el sistema mientras recicla energía es un loop sin observador
**Resultado esperado:** Pieza Rotor del Reloj Suizo implementada — captura actividad real de Alfredo + hilos Manus → la convierte en energía (budget, contexto, prioridad) → recarga el Resorte (`embrion_budget`) del Embrión. **Autonomía sostenida desbloqueada.**

---

## 0. Procedencia

`docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §3 verbatim:

> "La razón por la que los agentes de IA mueren rápido es porque **no tienen Escape ni Rotor**"

`AUDIT_4_CAPAS_3A_2026_05_10.md` §3 tabla Reloj Suizo verbatim:

> "**Rotor (Reciclador)** | Captura energía actividad usuario para recargar Resorte | ❌ **AUSENTE — declarado**"

`AUDIT_4_CAPAS_3A_2026_05_10.md` §7 H3 verbatim:

> "**Severidad: media-alta para autonomía sostenida.** [...] **Acción:** crear `sprint_ROTOR_001_reciclador_actividad.md` — captura de actividad del Command Center / Mac → recarga del Resorte (`embrion_budget`)."

`CRUCE_DIMENSIONAL_5A_2026_05_10.md` §5 #5 verbatim:

> "**Diferencial principal:** ROTOR-001 es **pieza diferencial de autonomía sostenida** según `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §3. Sin Rotor, el Monstruo nunca alcanza autonomía perpetua y depende de prompts explícitos. **Es el primer paso real hacia Embrión-Dirige (Fase 2 del modelo de hilos).**"

Handoff Cowork saliente 2026-05-11 §9 bloqueantes activos verbatim:

> "**Rotor del Reloj Suizo** | Pensamiento + implementación nueva | Capa 2 IE al 100%. Autonomía sostenida."

**Bloqueante magna #1 del proyecto.** Sin spec no se puede arrancar; este borrador es el primer paso.

---

## 1. Concepto canónico

### El Rotor en horología

En relojes mecánicos automáticos (Audemars Piguet, Patek Philippe), el **rotor** es un disco semicircular que gira con el movimiento de la muñeca del usuario. Cada giro transmite energía mecánica al **resorte (mainspring)**, recargándolo sin intervención manual. Sin rotor, el reloj se detiene en ~40h. Con rotor, dura indefinidamente mientras el usuario lo use.

### Aplicado a IA agéntica (DSC-MO-010)

El Embrión del Monstruo es el reloj. El budget económico ($0.25/cycle), el contexto del LLM y la prioridad de las tareas son su "resorte" (Mainspring = `embrion_budget`). Sin reciclaje, el resorte se agota en horas → el Embrión muere por presupuesto exhausto o pérdida de contexto.

El **Rotor del Monstruo** es el componente que captura la actividad real del operador humano (Alfredo) y los hilos Manus, y la convierte en señales que recargan el resorte:

- **Commits de GitHub** → contexto + dirección estratégica
- **Queries en Supabase via MCP** → señales de qué tablas/datos son relevantes
- **Mensajes en Telegram al bot** → directivas explícitas
- **Sesiones Cowork** → arquitectura + canonización
- **Activity del Manus** → ejecución + entrega
- **Latidos del Embrión mismo** → auto-recarga parcial

El Rotor agrega estas fuentes en una **señal de energía** que el Resorte consume.

### Diferencia con el Volante existente

- **Volante (Balance Wheel)** ya existe (`kernel/embrion_loop.py`): es el latido constante del Embrión, ~390 latidos/24h. **Es el que SE GASTA.**
- **Rotor** NO existe: es el que **RECARGA** el resorte basado en actividad externa. Sin Rotor, cada latido drena el budget; con Rotor, el budget se renueva cuando el usuario actúa.

---

## 2. Audit pre-sprint — Estado actual

Lo que existe:
- `kernel/embrion_loop.py` (2,067 LOC) — Volante. Doctrina del silencio. Sigue intacto.
- `kernel/embrion_budget.py` (484 LOC) — Resorte. Cap $0.25/cycle pre-flight.
- `kernel/finops.py` (252 LOC) — FinOps Soberano. Telemetría de gasto.
- `kernel/embrion_scheduler.py` (706 LOC) — Áncora (funcional pero no nominal).
- `mcp__github-monstruo__*` + `mcp__supabase-monstruo__*` — fuentes de actividad ya conectadas a Cowork.
- Telegram bot operativo con `TelegramNotifier`.

Lo que NO existe:
- `kernel/rotor/` (subdirectorio nuevo, propuesto en este sprint).
- Tabla `rotor_activity_log` en Supabase.
- Algoritmo de "actividad → energía" canonizado.
- Dashboard del Rotor.

---

## 3. Tareas del Sprint

### Tarea T1 — Tabla `rotor_activity_log` en Supabase

**perfil_riesgo:** write-risky

**Descripción:** Migración SQL `migrations/sql/00XX_rotor_activity_log.sql` (siguiente número libre post-derivas resueltas). Columnas mínimas: `id`, `created_at`, `source` (CHECK in `'github_commit'|'supabase_query'|'telegram_message'|'cowork_session'|'manus_session'|'embrion_latido'`), `actor` (text), `payload_jsonb`, `energy_units` (numeric — convertido por algoritmo T3), `consumed_by_embrion_at` (timestamp nullable), `cycle_id_consumer` (bigint nullable). RLS `service_role_only`.

**Criterios de cierre:** migración idempotente aplicada, tabla con RLS verificada, índices en `(source, created_at DESC)` y `(consumed_by_embrion_at NULLS LAST)`. Reporte JSON en `reports/migration_rotor_activity_log.json`.

### Tarea T2 — Capturadores de actividad (6 sources)

**perfil_riesgo:** write-risky

**Descripción:** Implementar `kernel/rotor/capturers/` con un módulo por source:

| Source | Módulo | Trigger |
|---|---|---|
| `github_commit` | `github_capturer.py` | Webhook GitHub Push (nuevo endpoint en `kernel/embrion_routes.py`) |
| `supabase_query` | `supabase_capturer.py` | Polling de `kernel_audit_log` cada 60s (cuando esté en main post-S-003.B) |
| `telegram_message` | `telegram_capturer.py` | Extender el existente `telegram_webhook` para INSERT en `rotor_activity_log` además del inbox |
| `cowork_session` | `cowork_capturer.py` | INSERT en `cowork_sesiones` ya existente (Sprint COWORK-RUNTIME-001) → trigger nuevo que copia row a `rotor_activity_log` |
| `manus_session` | `manus_capturer.py` | Polling de `embrion_memoria` filtrando `hilo_origen LIKE 'manus_%'` |
| `embrion_latido` | `latido_capturer.py` | Hook directo en `embrion_loop.py` — usar marcadores `ROTOR_BEGIN/END` para revert trivial (patrón del Sprint T5 Embrión-Daddy) |

**Cada capturer** persiste row en `rotor_activity_log` con `energy_units=NULL` (calculado por T3).

**Pre-condiciones:** Webhooks GitHub configurados (nuevo endpoint), polling workers desplegados como servicio Railway separado (igual que `proposal_processor`).

**Criterios de cierre:** los 6 capturers tienen test 1:1 con fixture. `pytest tests/rotor/test_capturers_*.py` PASS. Reporte JSON en `reports/rotor_capturers_smoke.json` con 1 row generado por cada source contra Supabase real.

### Tarea T3 — Algoritmo "actividad → energía"

**perfil_riesgo:** write-safe (es lógica pura)

**Descripción:** Implementar `kernel/rotor/energy_calculator.py` con función `compute_energy_units(activity: RotorActivity) -> Decimal`. Reglas iniciales (canonizables como DSC-MO-013 si Alfredo firma):

| Source | Energy units (USD-equivalent) |
|---|---|
| `github_commit` (Cowork, Manus, Alfredo) | $0.05 por commit (vale 1/5 de un cycle del Embrión) |
| `github_commit` mergeado a `main` | bonus $0.10 (recompensa cierre) |
| `supabase_query` MCP de Cowork | $0.02 por query no-trivial |
| `telegram_message` de chat autorizado | $0.05 por mensaje (atención humana es magna) |
| `cowork_session` >2h | $0.50 por sesión cerrada (sesión productiva real) |
| `manus_session` con PR mergeado | $0.30 por PR cerrado |
| `embrion_latido` exitoso (no abort por Self-Verifier) | $0.01 (recarga lenta auto-sostenida) |
| `embrion_latido` aborted | $-0.05 (penalización por gasto sin output) |

**Cap diario por source:** evitar farming. Cada source tiene techo de $5/día.

**Validation magna requerida:** `record_validation("rotor_energy_calibration_2026", ...)` antes de calibrar valores reales. La tabla arriba son **defaults canónicos**, no validados contra producción todavía.

**Criterios de cierre:** función pura testeable, `pytest tests/rotor/test_energy_calculator.py` con ≥20 casos (un test por source × 3 escenarios cada uno). Reporte JSON en `reports/rotor_energy_calculator_calibration.json` con baseline contra 24h de actividad real post-deploy.

### Tarea T4 — Wiring del Rotor al Resorte (`embrion_budget`)

**perfil_riesgo:** write-risky (toca el budget — el corazón económico del Embrión)

**Descripción:** Implementar `kernel/rotor/recharge.py` con función `recharge_mainspring()` que corre cada 5 minutos via `embrion_scheduler`. Lee `rotor_activity_log WHERE consumed_by_embrion_at IS NULL`, agrega `SUM(energy_units)`, llama a una función NUEVA `embrion_budget.add_recycled_energy(units: Decimal)` que sube el `daily_cap_remaining` del día actual.

**Doctrina del silencio sobre `embrion_loop.py`:** este sprint NO toca `embrion_loop.py` excepto el capturer T2.6 (latido_capturer) que va en marcadores `ROTOR_LATIDO_BEGIN/END`. Todo lo demás va a `kernel/rotor/`.

**Cap superior:** el recharge NO puede exceder 2× el daily cap original ($30/día). Si Rotor genera $80 de energía un día, $30 entran al budget, $50 quedan registrados como "energía perdida — capacidad excedida" para análisis post-hoc.

**Criterios de cierre:** test `pytest tests/rotor/test_recharge.py` con simulación de día completo (24h de actividades mock → recharge → budget actualizado). Cap superior verificado. Reporte JSON en `reports/rotor_recharge_smoke.json` post-deploy.

### Tarea T5 — Dashboard del Rotor

**perfil_riesgo:** write-safe

**Descripción:** `kernel/dashboards/rotor_history.py` siguiendo patrón de `cost_history.py`. Visualiza: 24h/7d/30d de actividad por source + energía total generada vs consumida + cap excedido + correlación con productividad real (commits mergeados). CLI `python -m kernel.dashboards.rotor_history --output bridge/rotor_dashboard.html`.

**Criterios de cierre:** `pytest tests/test_rotor_dashboard.py` PASS (mínimo 10 tests). Reporte JSON en `reports/rotor_dashboard_smoke.json`.

### Tarea T6 — Postmortem + canonización doctrinal

**perfil_riesgo:** read-only

**Descripción:** `bridge/postmortem_sprint_ROTOR_001.md` documentando timeline, decisiones técnicas (especialmente la tabla de energy_units), bugs encontrados, lecciones, métricas baseline de los primeros 7 días post-deploy.

**Si Alfredo lo aprueba, crear DSC-MO-013 — "Rotor: reciclador de actividad humano → energía Embrión"** con contrato ejecutable adjunto (la tabla T3 + algoritmo).

**Criterios de cierre:** postmortem firmado. DSC-MO-013 candidato preparado para firma T1 separada (NO se firma en este sprint — solo redacción).

---

## 4. Contratos ejecutables que adjunta

| DSC enforzado | Contrato producido | Archivo |
|---|---|---|
| DSC-MO-010 (Reloj Suizo) | Pieza Rotor implementada end-to-end | `kernel/rotor/` (módulo nuevo, ~1,500 LOC estimado) |
| Obj #11 (Multiplicación + Reloj Suizo) | Recharge del Resorte basado en actividad externa | `kernel/rotor/recharge.py` + extensión `embrion_budget.add_recycled_energy()` |
| DSC-G-014 (PIPELINE vs PRODUCTO) | Validación humana magna requerida pre-canonización DSC-MO-013 | `bridge/postmortem_sprint_ROTOR_001.md` |
| Obj #15 (Memoria Soberana) | Tabla `rotor_activity_log` como capa de memoria de actividad humana | migración SQL |

---

## 5. Criterios de cierre verde (Sprint completo)

- Las 6 tareas en exit 0 con artifacts en `reports/`.
- 6 capturers operativos: cada source genera al menos 1 row real en `rotor_activity_log` post-deploy.
- Recharge ejecutado cada 5 min en producción durante 24h consecutivas sin errores.
- Dashboard generado contra producción + visible en `bridge/rotor_dashboard.html`.
- Métricas baseline post-deploy: ≥$1 USD de energía reciclada/día durante primeros 3 días (correlación esperada con actividad real de Alfredo + hilos Manus).
- Cowork audita DSC-G-008 v2 sobre el PR antes de mergear.
- Sprint cierra con frase canónica: `🏛️ ROTOR-001 — DECLARADO (6/6 verde + Reloj Suizo de 45% nominal a 60%+)`.
- `memory/cowork/COWORK_DECISIONES_VIVAS.md` §4 (Reloj Suizo 8 piezas) actualizada — Rotor pasa de "❌ AUSENTE" a "✅ Implementado nominalmente".

---

## 6. Owner

**Owner técnico principal:** Manus Ejecutor (T1-T5 implementación).
**Owner arquitectónico:** Cowork (diseño doctrinal + tabla de energy_units T3 + audit pre-cierre).
**Owner humano final:** Alfredo (firmar tabla T3 antes de calibrar valores reales — decisión económica magna; firmar DSC-MO-013 post-postmortem si la implementación funciona).

---

## 7. Trazabilidad

- **Origen:** bloqueante magna #1 del handoff Cowork saliente 2026-05-11 + audits 3A §7 H3 + 5A §5 #5 + doc canónico `ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §3.
- **Sprints anteriores que habilitan este:**
  - Sprint EMBRION-NEEDS-001 Tarea 1 (`embrion_budget` 484 LOC — el Resorte que el Rotor recarga).
  - Sprint COWORK-RUNTIME-001 (`cowork_sesiones` table + Sprint NOMENCLATURA-001 + Migration 0010 KPIs — fuente para `cowork_capturer`).
  - Sprint EMBRION-NEEDS-002 T5 (`embrion_inbox` + Telegram capturado — fuente para `telegram_capturer`).
  - Sprint S-003.B post-merge con renumeración (`kernel_audit_log` — fuente para `supabase_capturer`).
- **Sprint que destraba después:** Embrión-Dirige (Fase 2 del modelo de hilos). Sin Rotor, el Embrión no puede dirigirse autónomamente — siempre depende de prompts externos para reponer su budget.
- **Δ esperado Obj global:** **+3 pts** directo (Obj #11 al 72% sube a 80%+, Reloj Suizo a 60%+) + leverage indirecto magna (autonomía sostenida desbloquea iteración perpetua).

---

## 8. Pre-flight check (Manus DEBE correr antes de arrancar)

```bash
# 1. Repo limpio + main pull
git status && git pull origin main

# 2. Tests verde local
pytest tests/test_embrion_budget.py  # cobertura del Resorte

# 3. Acceso Supabase + GitHub webhook capability
test -n "$SUPABASE_DB_URL"
test -n "$GITHUB_WEBHOOK_SECRET"  # nuevo env var requerido
test -n "$TELEGRAM_BOT_TOKEN"

# 4. Verificar Resorte funcional pre-Rotor
python -c "from kernel.embrion_budget import get_budget_state; print(get_budget_state())"
# Esperado: dict con daily_cap_remaining + monthly_cap_remaining

# 5. Verificar scheduler existente
python -c "from kernel.embrion_scheduler import get_embrion_scheduler; print('ok')"

# 6. Verificar que el directorio kernel/rotor/ NO existe todavía
test ! -d kernel/rotor/
```

Si cualquier paso falla, NO arrancar. Reportar al bridge.

---

## 9. Bloqueante humano declarado

**T3 tabla de energy_units requiere firma explícita de Alfredo antes de calibrar valores reales.** Razón: es decisión económica magna — define cuánto vale cada acción humana en términos de budget para el Embrión. Calibración mal hecha puede crear loops perversos (ej. farming de commits triviales para inflar budget). Alfredo decide las cifras finales antes del flip a producción.

**T6 DSC-MO-013 canonización requiere firma separada post-postmortem.** Si los primeros 7 días post-deploy muestran que el Rotor funciona como diseñado, Alfredo firma el DSC. Si no, queda como sprint exitoso pero sin canonización doctrinal.

---

## 10. Nota sobre dependencias con Guardian

**Recomendación operativa T2:** ejecutar Sprint GUARDIAN-AUTONOMO-001 ANTES de ROTOR-001. Razón:
- Guardian Autónomo establece el observador que mide `% por Objetivo` continuamente.
- Sin Guardian, el ROTOR pasa de "ausente" a "implementado" pero **nadie mide si funciona** — Cowork tendría que auditar manualmente cada semana.
- Con Guardian, el delta del Obj #11 (Multiplicación + Reloj Suizo) se reporta automáticamente.

Si se prioriza ROTOR-001 antes que GUARDIAN, agregar Tarea T0 al sprint: "Verificación manual diaria por Cowork de baseline post-deploy durante 7 días". Esto agrega ~30 min/día de Cowork × 7 días = 3.5h de Cowork. Comparado con Sprint GUARDIAN-AUTONOMO-001 (2-3 días Manus), GUARDIAN primero es más eficiente.

---

**Firma propuesta de cierre:** sólo válida si las 6 tareas pasan + 6 capturers generan rows reales + recharge ejecuta 24h sin errores + Cowork audita DSC-G-008 v2 verde + métricas baseline de ≥$1/día USD reciclada. Sin las 5 condiciones, el cierre se queda en `🏛️ ROTOR-001 — PIPELINE TÉCNICO DECLARADO` (DSC-G-014 distinción) y el Reloj Suizo sigue al 45% nominal hasta que la producción confirme reciclaje real.

---

**estado:** DRAFT_PENDIENTE_FIRMA_T1 — Alfredo firma cambio a `firme` antes del kickoff a Manus Ejecutor. Calibración T3 + canonización T6 son sub-decisiones T1 separadas que pueden venir post-firma del sprint mismo.
