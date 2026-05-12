# Postmortem ESCAPE-001 (PLACEHOLDER — D+7 / D+30)

> **Estado:** Placeholder. Reemplazar con datos reales del Throttler en producción.
> **Sprint:** ESCAPE-001 (Throttler Determinístico — magna #2 Reloj Suizo)
> **Fechas clave:**
> - 2026-05-12: Sprint cerrado, migración aplicada en prod, wiring activo
> - 2026-05-19 (D+7): Primera revisión con datos reales (ESTE postmortem)
> - 2026-06-11 (D+30): Decisión DSC-MO-014 (parámetros estáticos vs dinámicos)

---

## 1. Baseline esperado (post 7 días en producción)

| Métrica | Esperado D+7 | Real D+7 | Status |
|---|---|---|---|
| Pulsos emitidos `embrion_loop_latido` | ~10,080 (1/min × 7d) | `<rellenar>` | ⏳ |
| Pulsos bloqueados / pulsos solicitados | `<5%` | `<rellenar>` | ⏳ |
| Pulsos `guardian_daily_audit` | 7 (1/día) | `<rellenar>` | ⏳ |
| Pulsos `rotor_recharge` | ~2,016 (1/5min × 7d) | `<rellenar>` | ⏳ |
| Budget consumido por Escape | ~$1.00/día | `<rellenar>` | ⏳ |
| Bloqueos por `pulse_interval` | mayoría | `<rellenar>` | ⏳ |
| Bloqueos por `rate_limit` | <10% | `<rellenar>` | ⏳ |
| Bloqueos por `budget_cap` | 0 | `<rellenar>` | ⏳ |
| Bloqueos por `circuit_open` | 0 | `<rellenar>` | ⏳ |

## 2. Validación doctrinal (§4 Reloj Suizo, paso 5)

> *"Rotor capture suficiente energía para compensar el consumo del Escape"* — Doctrina Reloj Suizo §4.

| Componente | Energy capturada / consumida | Verificación |
|---|---|---|
| Rotor (energía captada) | `<rellenar de rotor_activity_log>` | ⏳ |
| Escape (energía consumida) | `<rellenar de escape_pulse_log>` | ⏳ |
| Balance neto | `Rotor - Escape >= 0` ? | ⏳ |

**Criterio de éxito:** autonomía perpetua viable si Rotor cubre Escape sin overspend del cap diario $30.

## 3. Hallazgos esperados

Lista de hipótesis a verificar con datos reales:

1. **Latido throttled correctamente:** el flag `EMBRION_ESCAPE_ENABLED=true` no degrada la responsividad ante mensajes de Alfredo (gate `_is_directive` no bloqueable).
2. **Cero starvation:** ningún consumer queda sin pulsos durante 24h.
3. **Cero memory leak:** `_Escapement` instances no acumulan estado entre cycles.
4. **Persistencia idempotente:** retries no duplican filas en `escape_pulse_log`.
5. **HITL no se dispara espurio:** budget tracker sigue gobernando el cap diario sin interferencia del Escape.

## 4. Riesgos detectados a D+7

> *Rellenar con incidentes reales si los hubo.*

- **Riesgo 1:** clock skew entre Railway y Supabase → `next_pulse_at` retrocede. Mitigación actual: `max(0, ...)` en `await asyncio.sleep`.
- **Riesgo 2:** rate spikes de `external_llm_call` agotan el cap diario. Mitigación actual: cap superior compartido $30/día.
- **Riesgo 3:** `embrion_specialization` no se invoca en ningún cycle → consumer huérfano. Acción: verificar invocation count en D+7.

## 5. Métricas Reloj Suizo (cierre simetría doctrinal)

Post ESCAPE-001 + ROTOR-001, las **2 piezas magnas** del Reloj Suizo están:

| Pieza | Estado | Sprint |
|---|---|---|
| ⚙️ Rotor (Reciclador) | ✅ Cerrado | ROTOR-001 |
| ⏱️ Escape (Throttler) | ✅ Cerrado | ESCAPE-001 |
| 🔋 Mainspring (Budget) | ✅ Existente | EMBRION-NEEDS-001 |
| 🛡️ Guardian (Auditor) | ✅ Existente | GUARDIAN-AUTONOMO-001 |
| 🔄 Anchor (Scheduler) | ✅ Existente | (pre-existente) |
| 💎 Rubíes (Caché Semántica) | ⏳ Parcial | RUBIES-001 propuesto |

**Autonomía perpetua viable a D+7:** SÍ/NO `<rellenar>`.

---

## 6. DSC-MO-014 candidato (decisión D+30)

### Título
DSC-MO-014: Parámetros del Throttler — estáticos vs dinámicos.

### Contexto
ESCAPE-001 implementa los `pulse_intervals` como **constantes firmadas por T1** (Alfredo) en `kernel/escape/config.py`:

```python
PULSE_INTERVALS_SECONDS = {
    "embrion_loop_latido": 60,
    "guardian_daily_audit": 86400,
    "rotor_recharge": 300,
    "self_verifier_call": 30,
    "embrion_specialization": 600,
    "external_llm_call": 5,
}
```

Estos valores son **estáticos por env override** pero no se ajustan dinámicamente al estado del budget ni al comportamiento del agente.

### Pregunta binaria

¿Después de 30 días en producción, los `pulse_intervals` deben permanecer **estáticos** o adoptar lógica **dinámica** (ej. acelerar throttling si daily_spent_usd > 80% del cap)?

### Opciones

#### Opción A: Estático (default, sin cambios)
- ✅ Predecible, auditable, simple
- ✅ Cero riesgo de oscilación o feedback loops
- ❌ No adapta a picos de uso ni a períodos de inactividad

#### Opción B: Dinámico-burst
- ✅ Permite ráfagas cuando hay budget disponible (intervals → 50% normal)
- ✅ Strangles cuando daily_spent > 80% (intervals → 200% normal)
- ❌ Riesgo de oscilación; más estado que mantener; harder to debug

#### Opción C: Híbrido (estático + override por consumer)
- ✅ Conservar default estático; permitir tagging por trigger con `override_interval` en metadata
- ✅ Útil para casos especiales (ej. directiva urgente de Alfredo bypass)
- ❌ Complejidad media; requiere governance de overrides

### Datos requeridos para decidir (D+30)

- Distribución real de inter-pulse times por consumer
- Cantidad de bloqueos por `budget_cap` (señal de necesidad de adaptación)
- Eventos donde Alfredo pidió respuesta rápida y Escape la frenó
- Tasa de cambio del baseline a lo largo de los 30 días

### Decisión esperada D+30

`<rellenar con análisis>`

### Firmante propuesto

Alfredo T1, basado en agregados de `escape_pulse_log` + dashboard al D+30.

---

## 7. Acciones operativas post-postmortem

- [ ] D+7: rellenar tabla §1 con SQL agregados
- [ ] D+7: ejecutar `python -m kernel.escape.dashboard --mode html --out reports/escape_d7.html`
- [ ] D+14: revisar si hay incidentes para mover a `bridge/incidents/`
- [ ] D+30: firmar DSC-MO-014 con decisión binaria

---

> Documento generado al cierre del Sprint ESCAPE-001 (2026-05-12).
> Permanece como placeholder hasta primera revisión D+7 (2026-05-19).
