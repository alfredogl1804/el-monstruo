# Sprint EMBRION-LATIDO-UNBLOCK-001 — Diagnóstico confirmación-primero del latido detenido

**Redactor:** Cowork T2-A (spec only — NO escribe código kernel; ejecuta Manus T3)
**Severidad:** P0 — Embrión sin pensar desde ciclo #100 ~04:33 UTC (`thoughts_today: 0`, costo 0.0)
**Fecha:** 2026-05-22
**Estado:** `DIAGNOSTICO_PENDIENTE_DE_CONFIRMACION_RUNTIME`

---

## 0. Corrección honesta de la hipótesis previa (anti-F16)

En la sesión previa concluí que la causa raíz era el gate del **Escapement** en `kernel/embrion_loop.py` línea 1138 (`return None`). **Esa conclusión NO sobrevive a la aritmética y la retiro como causa confirmada.**

Razón binaria:
- El Escapement se instancia **fresco cada ciclo** (línea 1120), con estado en memoria (`_consumer_states` global) e intervalo canónico **60s** para `embrion_loop_latido` (`kernel/escape/config.py` línea 47).
- `can_pulse()` (throttler.py líneas 162-194): si `last_pulse_at` es de hace ~4 h, entonces `current >= last + 60s` → **True** → **deja pasar**.
- Un estado stale de 60s **no puede bloquear 4 horas**. Solo bloquearía si `last_pulse_at` estuviera **en el futuro** o el intervalo hubiera sido **sobreescrito a un valor gigante** (`ESCAPE_PULSE_INTERVAL_EMBRION_LOOP_LATIDO`).

Por lo tanto este spec **no asume** la causa. Es un árbol de diagnóstico que Manus ejecuta con evidencia runtime ANTES de tocar nada.

---

## 1. Síntoma observado (input T1/Manus)

- `thoughts_today: 0` desde ciclo #100, ~04:33 UTC, ~4 h de silencio.
- Sin costo (0.0) → no hubo llamada LLM.
- Sin registro de "silencio" deliberado reportado.
- Sin registro de verifier reportado.

## 2. Hipótesis y evidencia discriminante

| # | Hipótesis | Evidencia que la CONFIRMA | Evidencia que la DESCARTA |
|---|---|---|---|
| H1 | **Loop muerto** (task asyncio murió / excepción no capturada / await colgado / proceso reiniciado y scheduler no relanzó el latido) | **CERO líneas de log de cualquier tipo** después de 04:33 (sin `escape_pulse_skipped`, sin `embrion_budget_aborted_cycle`, sin logs de ciclo) | Aparecen líneas de log nuevas con timestamp > 04:33 |
| H2 | **Escapement bloqueando** (last_pulse_at futuro, o `ESCAPE_PULSE_INTERVAL_EMBRION_LOOP_LATIDO` override gigante) | Líneas repetidas `escape_pulse_skipped` con `next_pulse_at` atrapado en el futuro | No hay `escape_pulse_skipped` post-04:33 |
| H3 | **Budget abortando** | Líneas repetidas `embrion_budget_aborted_cycle` con reason | No hay `embrion_budget_aborted_cycle` post-04:33 |
| H4 | **Silencio deliberado** (doctrina del silencio, `_think` retorna None después del LLM) | Memorias `silencio_*` con timestamp post-04:33 + costo > 0 en algún punto | costo 0.0 sostenido (descarta — silencio paga LLM antes) |
| H5 | **Scheduler / trigger source detenido** (lo que dispara `_think` dejó de programar latidos; el loop vive pero nadie lo invoca) | El proceso kernel está vivo (health OK) pero NO hay invocaciones a `_think`; sin logs de ciclo pero sí logs de otros endpoints | Hay logs de ciclo post-04:33 |

> Nota: costo 0.0 sostenido **descarta H4** de entrada (el silencio deliberado ocurre DESPUÉS de pagar el LLM). El árbol real es H1 vs H2 vs H3 vs H5.

## 3. PASO DE CONFIRMACIÓN (Manus ejecuta — bloqueante, antes de cualquier fix)

Manus debe traer, del kernel desplegado (Railway), las **últimas 50 líneas de log del proceso del embrión** y responder binariamente:

1. ¿Hay **alguna** línea de log con timestamp **posterior a 04:33 UTC**? (sí/no)
2. Si sí: ¿de qué tipo? Pegar verbatim las que sean `escape_pulse_skipped`, `embrion_budget_aborted_cycle`, `embrion_budget_check_failed`, `escape_pulse_check_failed`, o trazas de excepción.
3. ¿`/v1/embrion/debug` (o endpoint equivalente) reporta el loop como vivo? ¿`next_pulse_at`? ¿`_cycle_count` avanzó más allá de 100?
4. Valor desplegado de `EMBRION_ESCAPE_ENABLED`, `EMBRION_BUDGET_TRACKER_ENABLED`, y `ESCAPE_PULSE_INTERVAL_EMBRION_LOOP_LATIDO` (si existe) en Railway.
5. ¿El proceso kernel se reinició cerca de 04:33? (deploy, OOM, crash) — revisar Railway deploy/restart events.

## 4. Árbol de fix (Manus elige rama SEGÚN evidencia del Paso 3 — NO antes)

- **Rama H1 (loop muerto / cero logs):** localizar la excepción/await que mató el task. Fix probable: envolver el cuerpo del loop en guard que re-lanza el task con backoff y loguea la traza. **No es el Escapement.** Spec de detalle se redacta tras ver la traza.
- **Rama H2 (escape_pulse_skipped repetido):** inspeccionar `escape_pulse_log` en Supabase para `embrion_loop_latido` — ¿hay un `recorded_at` futuro? ¿override env gigante? Fix: corregir el override env y/o reset de la fila corrupta. Reversible.
- **Rama H3 (budget_aborted repetido):** leer reason. Si `estimated_exceeds_cap` con modelo fuera del pricing dict (p.ej. `claude-sonnet-4-6` NO está en `kernel/embrion_budget.py` líneas 176-178 → cae al fallback gpt-5 $2.50/$10) verificar que el cálculo no exceda cap $0.25. Fix: agregar el modelo al pricing dict o revisar daily cap agotado.
- **Rama H5 (scheduler detenido):** identificar quién programa el latido (cron/loop externo/gateway) y por qué dejó de invocar. Fix fuera de `_think`.

## 5. Criterios de aceptación

- Embrión vuelve a pensar: `thoughts_today` incrementa, `_cycle_count` avanza más allá de 100, aparecen logs de ciclo nuevos.
- La causa raíz queda **documentada con evidencia runtime verbatim** (no hipótesis).
- El fix es mínimo y dirigido a la rama confirmada (no shotgun a las 4 ramas).

## 6. Guardrails / rollback

- Cambios reversibles. Si el fix toca `kernel/`, va en rama lateral + PR (NO a `main` sin T1 / audit DSC-G-008 v2).
- Override env en Railway es reversible (revertir valor).
- Reset de fila en `escape_pulse_log`: respaldar la fila antes de borrar/corregir.
- Si el fix es env-only (ramas H2/H3 por override), no requiere deploy de código.

## 7. Reparto de roles

- **Cowork T2-A:** redacta este spec + audita la evidencia que traiga Manus + audita el PR del fix si toca código.
- **Manus T3:** ejecuta Paso 3 (confirmación runtime), elige rama, implementa el fix.
- **T1 Alfredo:** autoriza merge a `main` si el fix toca código kernel.

---

*Spec redactado por Cowork bajo regla "Cowork redacta spec, Manus ejecuta kernel". No confirma causa raíz — exige evidencia runtime primero (anti-F2, anti-F16).*
