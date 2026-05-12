<!-- lint_strict -->

# Sprint ESCAPE-001 — Throttler Determinístico (pieza magna Reloj Suizo)

**estado:** FIRME T1 — firmado Alfredo 2026-05-12 ~07:55 UTC ("te firmo los 5 incluyendo el 5 de xcode") junto con 3 DSCs canonizados + Brand Engine canary + T7 smoke Mac PR #114
**fecha_borrador:** 2026-05-12
**fecha_firma_T1:** 2026-05-12 ~07:55 UTC
**autor_borrador:** Cowork T2-A bajo autoridad T1 delegada ("tu dime" + "tarea grande al hilo ejecutor 2 sobre el reloj suizo")
**Hilo principal:** Manus Hilo Ejecutor 2 (continuidad de dominio post-ROTOR-001)
**ETA recalibrado:** 90-120 min reales (similar a ROTOR-001 con velocity demostrada)
**Objetivo Maestro:** #11 (Autonomía progresiva) + #8 (Inteligencia Emergente Colectiva — el Escape evita loops infinitos sin Self-Verifier dependency) + #4 (No equivocarse dos veces)
**Bloqueos pre-arranque:** PR #113 ROTOR-001 esperando convergencia T2-B + merge — escape opera CON el Rotor en el ciclo
**Resultado esperado:** pieza Escape del Reloj Suizo implementada. **Cierra simetría doctrinal con Rotor.** Dosifica energía del Resorte (`embrion_budget`) liberando "pulsos de atención" a intervalos determinísticos. Previene loops infinitos y gasto explosivo de budget.

---

## 0. Procedencia

`docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §3 verbatim:

> "La razón por la que los agentes de IA mueren rápido es porque **no tienen Escape ni Rotor**. **Sin Escape:** Le das un objetivo complejo a un agente y gasta todo su presupuesto de tokens en 5 minutos en un loop infinito o en una búsqueda ineficiente. El Escape del Monstruo obliga al agente a pensar en 'pulsos' (ej. 1 acción por minuto), estirando la autonomía de minutos a días."

`docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §2.1 tabla canónica:

> "**Escape (Escapement):** Libera energía en pulsos discretos, impidiendo que el resorte se descargue de golpe → **Dosificador (Throttler Determinístico):** Impide que el agente gaste todo su presupuesto en una sola corrida. Libera 'pulsos de atención' a intervalos exactos."

`docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §4 ciclo de vida energía verbatim:

> "Oscilación: El Volante marca el tiempo. **El Áncora y el Escape liberan 1 unidad de energía por pulso.** Trabajo: Los engranajes usan esa unidad para procesar. Recarga: Tu actividad mueve el Rotor."

**Estado actual binario verificado por Cowork 2026-05-12 ~07:15 UTC:**

```
grep -rln "throttler\|escapement\|throttle_rate\|pulse_interval" kernel/  → CERO HITS
ls kernel/escape kernel/throttler  → NO EXISTEN
```

**Las 8 piezas verificadas binariamente:**

| # | Pieza | Estado |
|---|---|---|
| 1 Resorte | `kernel/embrion_budget.py` | ✅ existe |
| 2 **Escape** | NO existe | ❌ **este sprint** |
| 3 Áncora | `kernel/embrion_scheduler.py` | ✅ existe |
| 4 Volante | `kernel/embrion_loop.py` | ✅ existe |
| 5 Espiral | NO existe | ❌ sprint posterior |
| 6 Rotor | `kernel/rotor/` PR #113 | ⏳ entregado, esperando merge |
| 7 Rubíes/Caché | `kernel/response_cache.py` | 🟡 parcial — verificar cobertura |
| 8 Remontoir | NO existe | ❌ sprint posterior |

**ESCAPE-001 es el sprint magno faltante #2** de la doctrina Reloj Suizo (Rotor era #1, ya entregado). Sin Escape, ROTOR-001 queda asimétrico: recarga energía pero loops infinitos siguen posibles.

---

## 1. Concepto canónico — Escape en horología vs software agéntico

### Horología

El Escapement (en Patek Philippe, Audemars Piguet, etc.) es la pieza que **convierte la fuerza continua del Resorte en impulsos discretos**. Sin Escapement, el Resorte se descarga en segundos. Con Escapement, dosifica la entrega de energía a intervalos exactos (típicamente 8 tics por segundo en relojes mecánicos = 28,800 Hz).

### Aplicado a IA agéntica

El budget del Embrión (`embrion_budget.py`) tiene `daily_cap_remaining`. Sin Escape, una sola llamada LLM agresiva (ej: GPT-5.5 Pro con reasoning=high) puede consumir $0.50+ en 1 corrida. Loop infinito = budget agotado en minutos.

**Escape determinístico:** define un `pulse_interval` (default 60 segundos) durante el cual el Embrión SOLO puede ejecutar 1 acción consumidora de budget. Si se intenta una segunda acción dentro del intervalo, **se bloquea hasta el próximo pulso**.

Resultado: gasto del budget se distribuye en pulsos discretos predecibles. Loops infinitos imposibles. Autonomía perpetua viable.

### Diferencia con Rotor (que ya existe)

- **Rotor (existe):** RECARGA `daily_cap_remaining` con actividad externa (commits + queries + mensajes + cowork_session + manus_session + latido)
- **Escape (este sprint):** DOSIFICA el consumo del `daily_cap_remaining` en pulsos determinísticos

Son piezas **complementarias del ciclo**: Rotor llena el balde, Escape libera gotas constantes. **Cero overlap funcional.**

---

## 2. Tareas del Sprint (T1-T6)

### T1 — Migración SQL `escape_pulse_log` (15-20 min)

**perfil_riesgo:** write-risky

`migrations/sql/00XX_escape_pulse_log.sql` (siguiente número libre post-ROTOR-001 T1 que tomó 0023; este toma probablemente 0026 post-Catastro S-CONTRATOS-001 que toma 0024+0025):

```sql
CREATE TABLE IF NOT EXISTS public.escape_pulse_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    pulse_id BIGSERIAL NOT NULL,                          -- secuencia monotónica
    consumer TEXT NOT NULL,                                -- 'embrion_loop' | 'guardian_audit' | 'rotor_recharge' | 'self_verifier'
    energy_consumed NUMERIC(10, 6) NOT NULL DEFAULT 1.0,  -- unidades de energía consumidas
    pulse_interval_seconds INTEGER NOT NULL DEFAULT 60,   -- intervalo configurado para ese consumer
    blocked_count INTEGER DEFAULT 0,                       -- veces que el consumer fue bloqueado en este intervalo
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_escape_pulse_log_consumer_created
    ON public.escape_pulse_log (consumer, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_escape_pulse_log_pulse_id
    ON public.escape_pulse_log (pulse_id DESC);

ALTER TABLE public.escape_pulse_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS escape_pulse_log_service_role_only
    ON public.escape_pulse_log FOR ALL TO service_role USING (true);
```

**⚠️ Lección post-V25 / post-T4 Catastro S-CONTRATOS:** NO usar `DATE(TIMESTAMPTZ)` en CREATE INDEX. Si necesitás índice por día, usar columna generada STORED.

**Criterios de cierre:** migración idempotente aplicada en local + tests verifican RLS+índices. Reporte JSON en `reports/migration_escape_pulse_log.json`.

### T2 — Throttler determinístico `kernel/escape/throttler.py` (25-35 min)

**perfil_riesgo:** write-risky (toca lógica de budget — corazón económico)

Crear subpaquete `kernel/escape/` con:

```
kernel/escape/
  __init__.py
  throttler.py          # clase Escapement + función can_pulse() + record_pulse()
  config.py             # PULSE_INTERVALS por consumer (default 60s, configurable env)
  registry.py           # registro de consumers conocidos
```

API canónica:

```python
class Escapement:
    def __init__(self, consumer: str, pulse_interval_seconds: int = 60):
        self.consumer = consumer
        self.pulse_interval_seconds = pulse_interval_seconds

    async def can_pulse(self) -> tuple[bool, datetime | None]:
        """Retorna (True, None) si puede ejecutar, (False, next_pulse_at) si bloqueado."""

    async def record_pulse(self, energy_consumed: Decimal = Decimal("1.0")) -> dict:
        """Registra pulso en escape_pulse_log + decrementa budget via embrion_budget.consume(energy_consumed)."""

    async def block_attempt(self) -> None:
        """Registra blocked_count++ para el pulso actual del consumer."""
```

**6 consumers iniciales canonizados:**

| Consumer | pulse_interval default | Justificación |
|---|---|---|
| `embrion_loop_latido` | 60s | 1 ciclo del Volante por minuto |
| `guardian_daily_audit` | 86400s (1 día) | 1 audit por día |
| `rotor_recharge` | 300s (5min) | mismo intervalo que recharge_mainspring |
| `self_verifier_call` | 30s | Self-Verifier max 2/min |
| `embrion_specialization` | 120s | Especializaciones cada 2min |
| `external_llm_call` | 10s | Llamadas LLM agresivas |

**Pre-condiciones:** integración con `embrion_budget.consume(amount)` función existente. Si no existe esa función, crearla.

**Criterios de cierre:** tests `tests/test_escape_throttler.py` con ≥15 casos cubriendo: can_pulse en intervalo, can_pulse fuera intervalo, record_pulse decremento budget, block_attempt cuenta, cap superior, fail-soft sin DB, los 6 consumers default. Reporte `reports/escape_throttler_smoke.json`.

### T3 — Wiring del Escape al Volante (`embrion_loop.py`) — 15-20 min

**perfil_riesgo:** write-risky (toca doctrina del silencio — patrón ROTOR T2.6)

Como en ROTOR-001 T2.6, usar **marcadores explícitos para revert trivial**:

```python
# ESCAPE_BEGIN — Sprint ESCAPE-001 2026-05-12
# Wiring del Escape al loop del Embrión. Bajo DSC-MO-006 v1.1 (doctrina del silencio):
# 1 marcador BEGIN + 1 marcador END. Cero modificaciones fuera de estos marcadores.

from kernel.escape.throttler import Escapement
escapement_latido = Escapement("embrion_loop_latido", pulse_interval_seconds=60)

# En el punto de inicio de cada ciclo del loop:
can_proceed, next_pulse_at = await escapement_latido.can_pulse()
if not can_proceed:
    await escapement_latido.block_attempt()
    logger.info("escape_blocked", consumer="embrion_loop_latido", next_pulse_at=next_pulse_at)
    await asyncio.sleep((next_pulse_at - datetime.now(timezone.utc)).total_seconds())
    continue

# Ejecutar ciclo del loop normal
# ...

# Al final del ciclo:
await escapement_latido.record_pulse(energy_consumed=Decimal("1.0"))

# ESCAPE_END — Sprint ESCAPE-001
```

**DSC-MO-006 v1.1 honrado:** cero modificaciones fuera de marcadores BEGIN/END. Patrón idéntico a ROTOR-001 T2.6 + T5 Embrión-Daddy.

**Criterios de cierre:** test `tests/test_escape_loop_integration.py` con mock loop ejecutando 5 iteraciones, verificando 1 pulso por minuto exacto + blocked_count incrementa si se invoca dentro del intervalo.

### T4 — Integración con Resorte (`embrion_budget.py`) — 15-20 min

**perfil_riesgo:** write-risky (toca corazón económico)

Verificar/agregar función `embrion_budget.consume(amount: Decimal) -> bool`:

```python
async def consume(self, amount: Decimal) -> bool:
    """Consume <amount> del daily_cap_remaining. Retorna True si OK, False si insuficiente.

    Este método es invocado por Escapement.record_pulse() — el Escape es el ÚNICO
    autorizado a consumir budget en pulsos discretos. Llamadas directas a consume()
    desde otros módulos están prohibidas por doctrina (todos deben pasar por Escape).
    """
    if self.daily_cap_remaining < amount:
        logger.warning("escape_budget_insufficient", required=str(amount), available=str(self.daily_cap_remaining))
        return False

    self.daily_cap_remaining -= amount
    await self._persist_budget()
    return True
```

**Lección anti-fragmentación:** si `consume()` ya existe con firma distinta, NO duplicar. Refactorizar para que Escape sea el único caller en el caso de pulsos discretos.

**Criterios de cierre:** test `tests/test_escape_budget_integration.py` con 5 casos: consume exitoso, consume insuficiente, integración con Escapement, persistencia post-consume, fail-soft sin DB.

### T5 — Dashboard del Escape `kernel/dashboards/escape_history.py` (15-20 min)

**perfil_riesgo:** write-safe

Patrón idéntico a `cost_history.py` + `rotor_history.py` + `guardian_dashboard.py`:

- HTML estático con SVG inline
- 24h/7d/30d de pulsos por consumer
- Gráfica de "pulsos esperados vs ejecutados vs bloqueados"
- Tabla de blocked_count por consumer
- XSS protected (HTML escape)
- CLI: `python -m kernel.dashboards.escape_history --output bridge/escape_dashboard.html`

**Criterios de cierre:** ≥8 tests verde (snapshot, agregación temporal, XSS, idempotencia, CLI happy/error). Reporte `reports/escape_dashboard_smoke.json`.

### T6 — Postmortem placeholder + DSC-MO-014 candidato (10 min)

`bridge/postmortems/postmortem_ESCAPE_001_PLACEHOLDER_2026_05_12.md` — placeholder a llenar día 7 con datos reales prod.

**DSC-MO-014 CANDIDATO** propuesto (decisión 2026-06-19, mismo timing que DSC-MO-013 de ROTOR): **pulse_interval estático vs dinámico**.
- Estático: 60s default canonizado (este sprint)
- Dinámico: ajusta interval según carga del Resorte (mayor budget → intervals más cortos → pulsos más frecuentes; menor budget → intervals más largos → conservación)

Trade-off: estático es predecible + auditable; dinámico es eficiente pero menos predecible. Decisión post-7-días-prod.

---

## 3. Contratos ejecutables que adjunta

| DSC enforzado | Contrato producido | Archivo |
|---|---|---|
| DSC-MO-006 v1.1 (doctrina del silencio) | Marcadores ESCAPE_BEGIN/END en `embrion_loop.py` | `kernel/embrion_loop.py` T3 |
| DSC-MO-010 (Reloj Suizo) | Pieza Escape implementada según doctrina §2.1 | `kernel/escape/` T2 |
| DSC-G-008 v2 (anti-Goodhart) | Cap superior pulses/día por consumer + blocked_count tracking | `kernel/escape/throttler.py` T2 |
| DSC-S-006 v1.1 (RLS desde nacimiento) | `escape_pulse_log` tabla nace con RLS service_role_only | T1 migración |
| DSC-S-012 (anti-deriva migraciones) | Migración en main ANTES de apply prod | T1 |
| DSC-MO-011 (Embryo Patch Lane) | Marcadores reversibles + cero modificaciones embrion_loop fuera de BEGIN/END | T3 |

---

## 4. Criterios de cierre verde (Sprint completo)

- Las 6 tareas en exit 0 con artifacts en `reports/` y tests verde.
- 25+ tests passing sin DB ni red (target similar ROTOR 29/29 + GUARDIAN 17/17).
- `escape_pulse_log` tabla creada en prod post-merge.
- Dashboard HTML generado contra prod visible.
- Wiring `embrion_loop` con marcadores ESCAPE_BEGIN/END probado.
- Cowork audita DSC-G-008 v2 + Perplexity T2-B converge bajo PBA.
- Sprint cierra con frase canónica: `⚙️ ESCAPE-001 — DECLARADO (6/6 verde)`.

---

## 5. Owner

**Owner técnico principal:** Manus Hilo Ejecutor 2 (continuidad de dominio Reloj Suizo post-ROTOR-001)
**Owner arquitectónico:** Cowork T2-A (audit DSC-G-008 v2 pre-merge) + Perplexity T2-B (verificación independiente PBA trigger 3)
**Owner humano final:** Alfredo T1 (firma spec + decisión override CI si aplica post-audit)

---

## 6. Trazabilidad

- **Origen:** doctrina canónica `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §2.1 + §3 + §4
- **Sprint predecesor:** ROTOR-001 (PR #113 en queue merge T2-B). ESCAPE complementa funcionalmente al Rotor en el ciclo de energía
- **Sprints posteriores que destraba:**
  - ESPIRAL-001 (Hairspring/Homeostasis) — feedback negativo post-escape
  - REMONTOIR-001 (Constant Force) — estabilizador de calidad post-fallback
- **Delta esperado Obj global:** +2-3 pts (Obj #11 Autonomía + Obj #8 IE Colectiva)

---

## 7. Pre-flight check (Ejecutor 2 DEBE correr antes de arrancar)

```bash
cd ~/el-monstruo && git status && git pull origin main

# Verificar PR #113 ROTOR-001 cerrado/mergeado:
gh pr view 113 --json state,merged
# Esperado: state=MERGED

# Verificar siguiente migration libre:
ls migrations/sql/ | sort | tail -5
# Esperado: 0023 + 0024 + 0025 (Catastro S-CONTRATOS) existen. Tu T1 toma siguiente (probable 0026).

# Verificar embrion_budget tiene consume():
grep -n "def consume\|async def consume" kernel/embrion_budget.py
# Si NO existe, T4 también la crea.

# Verificar embrion_loop tiene marcadores compatibles:
grep -n "ROTOR_LATIDO_BEGIN\|ROTOR_LATIDO_END" kernel/embrion_loop.py
# Esperado: 2 marcadores ROTOR ya existen. Tu T3 agrega ESCAPE_BEGIN/END separados.

# Verificar response_cache (pieza 7 parcial):
wc -l kernel/response_cache.py
# Read-only — NO tocar en este sprint (es otra pieza Rubíes/Jewels)
```

Si pre-flight rojo, reportar al bridge.

---

## 8. Bloqueante humano declarado

**Decisión magna T1 sobre pulse_intervals defaults** (similar a ROTOR T3 energy_units que Alfredo firmó el 2026-05-11):

Los 6 consumers default propuestos en T2 (60s embrion_loop, 86400s guardian, 300s rotor, 30s self_verifier, 120s especializaciones, 10s external_llm) requieren **firma T1 explícita** antes de hardcodearlos como constantes. Alternativa: configurables via env vars con defaults documentados.

**Bloqueante NO bloquea cierre del sprint** — si Alfredo NO firma defaults, Ejecutor 2 implementa con env vars + valores que dejarán como `placeholder_pending_T1_signature` hasta firma.

---

**Firma propuesta de cierre:** sólo válida si las 6 tareas pasan + 25+ tests verde + wiring loop probado + Cowork audita DSC-G-008 v2 verde + T2-B converge. Sin las 4 condiciones, cierre queda en `⚙️ ESCAPE-001 — PIPELINE TÉCNICO DECLARADO` (DSC-G-014 distinción).

---

**estado:** FIRME T1 (Alfredo 2026-05-12 ~07:55 UTC). Audit T2-B PBA convergente. Kickoff a Manus Ejecutor 2 producido en `bridge/cowork_to_manus_HILO_EJECUTOR_2_SPRINT_ESCAPE_001_KICKOFF_2026_05_12.md`. Gate (a) firma T1 VERDE — Ejecutor 2 puede arrancar inmediatamente post-ROTOR-001 merge.
