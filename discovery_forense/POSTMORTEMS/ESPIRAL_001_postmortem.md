# Postmortem ESPIRAL-001 — Hairspring (Pieza #5 Reloj Suizo)

**Estado:** placeholder firmado al cierre del sprint — actualizar tras 7d de operación en producción
**Sprint:** ESPIRAL-001 (Homeostasis Dinámica)
**Spec firmado T1:** commit `0de35e6`
**Gate VERDE Cowork:** commit `5325f17`
**Cierre Manus Hilo Ejecutor 2:** 2026-05-12

## §1 Qué se construyó

Pieza Espiral (Hairspring) del Reloj Suizo — la quinta de las 8 piezas magnas. Implementa feedback negativo dinámico que detecta deviation del pulse_rate observado vs baseline canónico del Escape (Pieza #2) en una ventana móvil de 15 minutos, y aplica overrides temporales del pulse_interval del consumer afectado:

- **spike_dampening:** observed > baseline + 30% → aumenta interval (hasta 2x el canonical)
- **undershoot_acceleration:** observed < baseline − 30% → reduce interval (hasta 0.5x el canonical)
- **return_to_canonical:** |deviation − 1| < 10% sostenida → restaura canonical

Override aplicado vía `kernel.escape.registry.apply_temporal_override()` con TTL default 30 min. Estado in-memory del registry; expiración automática sin acción humana. Auto-cleanup en `get_effective_pulse_interval()`.

## §2 Decisiones doctrinales (del DSC-G-008 v3 §4 dedución de consecuencias)

1. **Baseline NO se deriva del histórico (anti-Goodhart):** el baseline canónico se deriva siempre de `kernel.escape.config.get_pulse_interval_seconds(consumer)` firmado T1 ESCAPE-001, NO de medias móviles del propio sensor. Esto evita el bucle Goodhart donde el target se autoajusta al comportamiento observado.

2. **Fail-soft en TODA capa:** sensor (DB query), controller (decision), registry (override apply), logger (homeostasis_log persist). Si cualquier capa falla, la Espiral degrada a no-op silencioso. El latido del Volante NUNCA debe romper por culpa de la Espiral.

3. **TTL de override 30min default:** ventana razonable de estabilización. Si la deviation persiste, en el próximo ciclo (5 min) se renueva el override. Si la deviation cesa, en el próximo ciclo se aplica RETURN_TO_CANONICAL.

4. **Single Hairspring por consumer en v1:** el estado `_currently_overridden` vive en la instancia. Si en v2 se requieren múltiples Hairsprings por consumer, deberá agregarse `asyncio.Lock` por consumer-instance.

5. **`embrion_loop.py` wiring:** marcadores `ESPIRAL_BEGIN/END` insertados después de `ESCAPE_END` en el think loop. Cada N ciclos del Volante (default 5 = ~5 min con check_interval=60s), se ejecuta sense + correction. NO se modifica nada fuera de marcadores (DSC-MO-006 v1.1).

## §3 Riesgos vivos para vigilar (DSC-G-008 v3 §4 consecuencias materiales)

- **Oscillation entre overrides:** si la deviation oscila justo en el threshold (e.g., siempre 1.30±0.05), podría haber chatter. Mitigación: TTL de 30min absorbe oscillation rápida. Vigilar dashboard P95 deviation_ratio.
- **Override registry está in-memory:** si el proceso reinicia, los overrides activos se pierden y el consumer vuelve al canonical. Recuperación a los ~5 min del primer ciclo Espiral post-reinicio. Aceptable v1.
- **Sin RLS para vista materializada futura:** si en v2 se crean vistas analíticas sobre `embrion_homeostasis_log`, recordar el patrón `REVOKE ALL FROM PUBLIC, anon, authenticated; GRANT SELECT TO service_role`.
- **D7_DASHBOARD_XSS_AUDIT_001 cubierto:** el dashboard usa `html.escape()` en todo string user-controlled, validado por `TestDashboard.test_render_html_escapes_consumer_name`.

## §4 Métricas para 7d post-cierre

- `total_events` por día (esperado: <100/día en operación normal)
- Distribución `by_reason` (esperado: ~80% RETURN, ~10% SPIKE, ~10% UNDER en steady state; ratios fuera de eso → tuning de threshold)
- `deviation_avg / P95 / P99` (esperado: avg ≈ 1.0, P95 < 1.5, P99 < 2.0; valores mayores → ruido del sensor o problemas de calibración)

## §5 DSC candidato emergente

**DSC-MO-015 candidato (PID controller):** v1 implementa sólo P (proportional). Si en producción se observa overshoot/undershoot persistente, escalar a PID completo (Integral + Derivative) en v2. Decisión postpuesta hasta tener 30d de datos reales.

## §6 Cierre 8/8 simbólico Reloj Suizo

Tras ESPIRAL-001, restan en pipeline:

- **REMONTOIR-001** (Pieza #8 — Constant Force, fallback chain de los 8 Sabios + quality estimator + human-in-loop) — encolado post-merge
- **RUBIES-001** (Pieza #7 — Jewels, response_cache + budget tracker enriquecido) — pipeline post-REMONTOIR

## §7 Firma

**Hilo Ejecutor 2 (manus_hilo_b)**
2026-05-12
Sprint ESPIRAL-001 — DECLARADO 6/6 verde
