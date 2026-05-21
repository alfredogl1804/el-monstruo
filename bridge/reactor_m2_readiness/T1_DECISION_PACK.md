# T1 Decision Pack — M2 Readiness

Este documento contiene las decisiones binarias requeridas por T1 para autorizar la transición del Heartbeat R0 hacia M2 Readiness.

## A1. Scheduler Authorization

Seleccionar UNA opción para el estado del scheduler periódico (cron 12h):

- [ ] `KEEP_DORMANT` (Kill-switch = active:true. No se ejecuta nada).
- [ ] `ONE_SHOT_ONLY` (Kill-switch = active:false temporalmente para 1 ciclo manual, luego re-freeze).
- [ ] `LIMITED_ACTIVE_R0` (Kill-switch = active:false. Ejecuta cron 12h, pero topado a R0 local).
- [ ] `PERMANENT_ACTIVE_R0` (Kill-switch = active:false permanente. R0 local continuo).

## A2. Budget

Seleccionar UNA política de presupuesto para el Heartbeat / Oráculo:

- [ ] `$0 local only` (Solo validaciones internas, 0 llamadas a APIs externas).
- [ ] `capped external provider calls` (Llamadas permitidas hasta un límite mensual fijo).
- [ ] `no paid calls` (Solo proveedores con tier gratuito o ya cubiertos).
- [ ] `max per day` (Límite diario estricto en USD).

## A3. Provider Readiness

Confirmar estado de los proveedores para el Oráculo M2:

- [ ] **Perplexity:** Requiere fix de status 403.
- [ ] **DeepSeek:** Requiere provisión de API key.
- [ ] **OpenAI:** Listo (Verificado M2).
- [ ] **Anthropic (Claude):** Listo (Verificado M2).
- [ ] **Google (Gemini):** Listo (Verificado M2).
- [ ] **xAI (Grok):** Listo (Verificado M2).

## A4. Allowed Chain

Seleccionar la profundidad máxima permitida para la cadena autónoma:

- [ ] `Heartbeat only` (Solo latido R0, sin invocar nada más).
- [ ] `Heartbeat → Dispatcher` (Heartbeat activa el Dispatcher, pero este no enruta a loops).
- [ ] `Heartbeat → Dispatcher → Oráculo shadow` (Ejecuta Oráculo en modo report-only, sin side effects).
- [ ] `Heartbeat → Dispatcher → M2 chain` (Cadena completa Oráculo → Auditor → Risk, sin writes).

## A5. Kill-Switch Policy

Confirmar políticas del Kill-Switch:

- [ ] `file-based kill-switch remains supreme` (scheduler_kill_switch.json es la única fuente de verdad).
- [ ] `T1 can freeze any time` (T1 puede cambiar active:true en cualquier momento para detener todo).
- [ ] `no auto-unfreeze` (El sistema NUNCA puede cambiar active:false por sí mismo).
