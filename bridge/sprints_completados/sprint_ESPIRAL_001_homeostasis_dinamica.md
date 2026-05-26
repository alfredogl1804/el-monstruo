<!-- lint_strict -->

# Sprint ESPIRAL-001 — Homeostasis Dinámica (pieza magna #5 Reloj Suizo)

**estado:** FIRME T2-A bajo autoridad T1 delegada ("si continua con tareas grandes" 2026-05-12 ~08:08 UTC)
**fecha_borrador:** 2026-05-12
**fecha_firma_T2-A:** 2026-05-12 ~08:10 UTC
**autor_borrador:** Cowork T2-A bajo autoridad T1 delegada — magna paralela cierre Reloj Suizo doctrinal
**pendiente_firma_T1:** Alfredo puede revocar o convergir en próximo turno
**Hilo principal candidato:** Manus Hilo Ejecutor 2 (continuidad Reloj Suizo post-ESCAPE-001)
**ETA recalibrado:** 80-110 min reales (similar ESCAPE-001 + ROTOR-001 velocity demostrada)
**Objetivo Maestro:** #11 (Autonomía progresiva) + #2 (Calidad Apple/Tesla — homeostasis = autoestabilización) + #4 (No equivocarse dos veces — feedback negativo corrige desviaciones automáticamente)
**Bloqueos pre-arranque:** ESCAPE-001 PR mergeado (ESPIRAL opera SOBRE el Escape leyendo blocked_count/pulse rate para calibrar dinámicamente)
**Resultado esperado:** pieza Espiral del Reloj Suizo implementada. **Cierra el feedback loop del sistema horológico**: Volante oscila → Escape libera pulsos → trabajo consume → ESPIRAL detecta deriva y devuelve al centro ajustando pulse_intervals dinámicamente. Sin Espiral, agente con Escape estático puede entrar en "sobreoscilación": picos consumo seguidos de subutilización.

---

## 0. Audit pre-sprint (DSC-G-008 v3 §1)

**Estado actual binario verificado por Cowork 2026-05-12 ~08:10 UTC:**

```bash
ls kernel/espiral kernel/homeostasis  → NO EXISTEN
grep -rln "hairspring\|homeostasis\|espiral" kernel/  → CERO HITS
```

**Las 8 piezas — estado post-ESCAPE-001:**

| # | Pieza | Estado |
|---|---|---|
| 1 Resorte | `kernel/embrion_budget.py` | ✅ existe |
| 2 Escape | `kernel/escape/` | 🟡 spec FIRME T1 commit ff8716f, Ejecutor 2 arrancará post-ROTOR merge |
| 3 Áncora | `kernel/embrion_scheduler.py` | ✅ existe |
| 4 Volante | `kernel/embrion_loop.py` | ✅ existe |
| 5 **Espiral** | NO existe | ❌ **este sprint** |
| 6 Rotor | `kernel/rotor/` | ⏳ PR #113 esperando merge T2-B |
| 7 Rubíes/Caché | `kernel/response_cache.py` | 🟡 parcial — sprint posterior expansión |
| 8 Remontoir | NO existe | ❌ siguiente sprint magno (spec sembrado paralelo a este) |

**ESPIRAL-001 es la pieza #3 magna doctrinal del Reloj Suizo**, post-ROTOR (entregada) + ESCAPE (firmada). Cierra el feedback loop estructural.

---

## 1. Procedencia doctrinal

`docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §2.1 verbatim:

> "**Espiral (Hairspring):** Fuerza de retroceso que devuelve el volante al centro → **Feedback Negativo (Homeostasis):** Regresa al agente a su estado base de bajo consumo tras una ráfaga de actividad."

En horología: el hairspring es lo que da PRECISIÓN al reloj. Sin él, el volante oscilaría irregularmente. La espiral espinosa (Breguet, Patek) es la innovación que dio precisión cronométrica a la alta horología.

Aplicado a IA agéntica: tras una ráfaga de actividad (ej. Escape libera 10 pulsos seguidos para responder query compleja), el agente queda en estado de "sobreoscilación" — consumió alta carga, budget bajó rápido, y el siguiente pulso del Escape se siente desfasado. ESPIRAL **detecta el desbalance y aplica feedback negativo** ajustando pulse_intervals temporalmente:

- Picos consumo (>2x baseline) → Espiral aumenta pulse_intervals temporalmente (consumo baja)
- Subutilización (<0.5x baseline) → Espiral disminuye pulse_intervals temporalmente (consumo sube)
- Estado base → Espiral relaja, deja Escape con intervals canonizados

Resultado: agente vuelve dinámicamente a estado base de bajo consumo después de ráfagas, sin requerir intervención humana. Es la pieza que da **CALIDAD APPLE/TESLA** (Obj #2): un Patek Philippe oscila igual al inicio y al final del día porque el hairspring corrige micro-derivas.

---

## 2. Tareas del Sprint (T1-T6)

### T1 — Migración SQL `embrion_homeostasis_log` (15-20 min)

**perfil_riesgo:** write-risky

`migrations/sql/00XX_embrion_homeostasis_log.sql` (siguiente número libre post-ESCAPE-001 T1 que toma probable 0026 — este toma probable 0027):

```sql
CREATE TABLE IF NOT EXISTS public.embrion_homeostasis_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    consumer TEXT NOT NULL,                          -- el consumer del Escape al que se aplicó homeostasis
    pulse_rate_observed NUMERIC(10, 4) NOT NULL,     -- pulses/min observado en ventana móvil
    pulse_rate_baseline NUMERIC(10, 4) NOT NULL,     -- baseline canónico del consumer
    deviation_ratio NUMERIC(10, 4) NOT NULL,         -- observed/baseline
    pulse_interval_adjusted_to INTEGER NOT NULL,     -- nuevo pulse_interval que aplicó Espiral
    pulse_interval_canonical INTEGER NOT NULL,       -- el canonical del consumer (al que retornará)
    adjustment_reason TEXT NOT NULL CHECK (adjustment_reason IN ('spike_dampening', 'undershoot_acceleration', 'return_to_canonical')),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_homeostasis_log_consumer_created
    ON public.embrion_homeostasis_log (consumer, created_at DESC);

ALTER TABLE public.embrion_homeostasis_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS homeostasis_log_service_role_only
    ON public.embrion_homeostasis_log FOR ALL TO service_role USING (true);
```

**⚠️ Lección post-V25:** NO usar `DATE(TIMESTAMPTZ)` en CREATE INDEX. Si requiere índice por día, usar columna generada STORED como `0025_credential_rotations`.

### T2 — Hairspring core `kernel/espiral/homeostasis.py` (25-35 min)

**perfil_riesgo:** write-risky (toca lógica de pulse calibration — corazón temporal)

Crear subpaquete `kernel/espiral/`:

```
kernel/espiral/
  __init__.py
  homeostasis.py        # clase Hairspring + sense_deviation() + apply_correction() + return_to_canonical()
  sensor.py             # observador pulse rate ventana móvil 5/15/30 min
  controller.py         # PID-like controller (proportional + integral + derivative) — opcional v1 solo P
```

API canónica:

```python
class Hairspring:
    def __init__(self, consumer: str, canonical_interval: int, sensitivity: float = 0.5):
        self.consumer = consumer
        self.canonical_interval = canonical_interval  # del Escape registry
        self.sensitivity = sensitivity  # 0.0 = inerte, 1.0 = correctivo agresivo

    async def sense_deviation(self, window_minutes: int = 15) -> dict:
        """Lee escape_pulse_log + calcula deviation_ratio.
           Retorna dict con pulse_rate_observed, baseline, deviation_ratio, recommendation."""

    async def apply_correction(self, sense_result: dict) -> int:
        """Si abs(deviation) > threshold, ajusta pulse_interval temporal del consumer.
           Registra en embrion_homeostasis_log. Retorna nuevo pulse_interval aplicado."""

    async def return_to_canonical(self) -> None:
        """Tras ventana de estabilidad confirmada (deviation < 10%), restaura pulse_interval canonical."""
```

**Lazos canonizados:**
- ventana_sensado: 15 min default (configurable env)
- threshold_correction: ±30% deviation
- threshold_return: ±10% deviation sostenida 5 min
- max_correction_factor: 2.0 (no aumentar interval más de 2x ni reducirlo a <0.5x del canonical)

**Criterios de cierre:** tests `tests/test_espiral_homeostasis.py` con ≥15 casos: deviation positiva (spike), deviation negativa (undershoot), retorno a baseline, max_correction cap, fail-soft sin DB, ventanas móviles. Reporte JSON.

### T3 — Wiring Espiral a Volante (`embrion_loop.py`) — 15-20 min

**perfil_riesgo:** write-risky (patrón ROTOR + ESCAPE replicado — marcadores explícitos)

```python
# ESPIRAL_BEGIN — Sprint ESPIRAL-001 2026-05-12
# Wiring del Hairspring al loop del Embrión. DSC-MO-006 v1.1 honrado: cero modificaciones fuera de marcadores.

from kernel.espiral.homeostasis import Hairspring
from kernel.escape.registry import get_canonical_interval

hairspring_latido = Hairspring("embrion_loop_latido", canonical_interval=get_canonical_interval("embrion_loop_latido"))

# Cada 5 minutos del Volante, ejecutar sense + correction:
if ciclo_actual % 5 == 0:  # cada 5 min asumiendo Volante 1/min
    sense = await hairspring_latido.sense_deviation(window_minutes=15)
    if abs(sense["deviation_ratio"] - 1.0) > 0.30:
        new_interval = await hairspring_latido.apply_correction(sense)
        # Espiral aplica al Escape registry temporal
    else:
        await hairspring_latido.return_to_canonical()

# ESPIRAL_END — Sprint ESPIRAL-001
```

**DSC-MO-006 v1.1 honrado:** cero modificaciones fuera de marcadores ESPIRAL_BEGIN/END.

### T4 — Integración Espiral ↔ Escape registry (15-20 min)

**perfil_riesgo:** write-risky (toca config de Escape)

Extender `kernel/escape/registry.py` con función `apply_temporal_override(consumer, new_interval, ttl_seconds)`:

```python
async def apply_temporal_override(consumer: str, new_interval: int, ttl_seconds: int) -> None:
    """Espiral aplica override temporal del pulse_interval canonical.
       Después de ttl_seconds, restaura canonical automáticamente."""
```

**Criterios de cierre:** tests integración 5 casos.

### T5 — Dashboard Espiral `kernel/dashboards/espiral_history.py` (15-20 min)

**perfil_riesgo:** write-safe

Patrón idéntico cost_history + rotor_history + escape_history. Visualiza:
- 24h/7d/30d: deviation_ratio por consumer
- Episodios de spike_dampening / undershoot_acceleration / return_to_canonical
- Gráfica de pulse_rate observed vs baseline

### T6 — Postmortem placeholder + DSC-MO-015 candidato (10 min)

DSC-MO-015 candidato: **Hairspring sensitivity calibration policy** (default 0.5 vs adaptive learning). Decisión post-7-días-prod.

---

## 3. Contratos ejecutables que adjunta

| DSC enforzado | Contrato producido | Archivo |
|---|---|---|
| DSC-MO-006 v1.1 (doctrina del silencio) | Marcadores ESPIRAL_BEGIN/END en embrion_loop.py | T3 |
| DSC-MO-010 (Reloj Suizo) | Pieza Espiral implementada según §2.1 | `kernel/espiral/` T2 |
| DSC-G-008 v3 (deducir consecuencias) | §4 deducción aplicada en este spec | §0 + §3 + §4 |
| DSC-S-006 v1.1 (RLS desde nacimiento) | embrion_homeostasis_log RLS service_role_only | T1 |
| DSC-S-012 (anti-deriva migraciones) | Migración en main pre-apply prod | T1 |
| DSC-MO-011 (Embryo Patch Lane) | Marcadores reversibles | T3 |

---

## 4. Criterios de cierre verde

- 6 tareas exit 0 + artifacts en `reports/` + tests verde
- 25+ tests passing sin DB ni red
- Tabla creada en prod post-merge
- Dashboard HTML generado contra prod
- Wiring marcado ESPIRAL_BEGIN/END
- Cowork audita DSC-G-008 v3 (con §4 explícito) + T2-B PBA convergente
- Frase canónica: `🌀 ESPIRAL-001 — DECLARADO (6/6 verde)`

---

## 5. Owner candidato y timing

**Owner técnico:** Manus Hilo Ejecutor 2 (continuidad Reloj Suizo post-ESCAPE-001)
**Owner arquitectónico:** Cowork T2-A (DSC-G-008 v3 §4 audit) + Perplexity T2-B (PBA trigger 3 verificación)
**Owner humano final:** Alfredo T1 (firma + decisión override CI)
**Timing:** post-ESCAPE-001 cerrado. Estimado 2026-05-13 si Ejecutor 2 cierra ESCAPE-001 hoy.

---

## 6. Trazabilidad

- Origen: `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §2.1 + §3 + §4
- Predecesores: ROTOR-001 (PR #113), ESCAPE-001 (spec firme commit ff8716f)
- Sucesor: REMONTOIR-001 (spec sembrado paralelo a este — pieza #8 cierra Reloj Suizo)
- Delta esperado Obj global: +2 pts (Obj #2 Calidad + Obj #11 Autonomía)

---

**Firma propuesta de cierre:** sólo válida si 6 tareas pasan + tests verde + wiring probado + audit Cowork DSC-G-008 v3 + T2-B PBA convergente. Sin las 4 condiciones, cierre queda en `🌀 ESPIRAL-001 — PIPELINE TÉCNICO DECLARADO`.

---

**Estado:** FIRME T2-A 2026-05-12 ~08:10 UTC. Pendiente firma T1 explícita en próximo turno (Alfredo puede revocar bajo autoridad T1 absoluta o convergir). Kickoff a Manus Ejecutor 2 PENDIENTE — espera cierre ESCAPE-001 + firma T1 ratificada.
