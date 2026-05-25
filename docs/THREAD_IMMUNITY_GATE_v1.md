# THREAD-IMMUNITY-GATE-v1

**Estado:** ACTIVO tras merge.
**Propósito:** cerrar el bucle de desanclaje recurrente en hilos Manus.

## Regla

Un hilo Manus no puede declararse anclado, listo o autorizado para operar hasta que exista:

```text
THREAD_IMMUNITY_STARTUP_PASS
```

Un hilo Manus no puede cerrar sin:

```text
THREAD_IMMUNITY_CLOSE_CANONIZED
```

Un cierre faltante produce:

```text
THREAD_IMMUNITY_WATCHDOG_FAIL
```

## Pieza atómica

Los tres bloques son una sola pieza inseparable. Si falta uno, el sistema no funciona.

| Bloque | Componente | Ejecutor | Momento |
|---|---|---|---|
| **A** | `scripts/thread_immunity/thread_immunity.py start` | Cada hilo Manus | Antes de cualquier acción operativa |
| **B** | `scripts/thread_immunity/thread_immunity.py close` | Cada hilo Manus | Antes de cerrar, compactar o entregar fin de sesión |
| **C** | `.github/workflows/thread-immunity-watchdog.yml` | GitHub Actions | Cada 60 minutos (cron `17 * * * *`) y `workflow_dispatch` manual |

## Frases sin valor sin receipt

Las siguientes frases producidas por el propio hilo, **sin receipt `THREAD_IMMUNITY_STARTUP_PASS` registrado**, no tienen valor canónico y deben ser tratadas como ruido:

- "hilo anclado"
- "reanclado"
- "listo para proceder"
- "guardian verde"
- "ya lo tengo en mente"
- "no lo vuelvo a repetir"

## Tratamiento

| Persona | Forma canónica | Forma prohibida |
|---|---|---|
| Usuario | **Alfredo** | "don Alfredo" |
| Padre del usuario | **don Hugo** | (correcta) |

## Criterio binario

**PASA si y solo si:**

- `STARTUP_PASS` existe en `thread_immunity_events`.
- `CLOSE_CANONIZED` existe para esa misma `session_id`.
- `WATCHDOG_PASS` existe en la última corrida del watchdog.

**FALLA si:**

- Cualquier sesión `STARTUP_PASS` vence (TTL 6 h por defecto) sin `CLOSE_CANONIZED`.
- Falta cualquier axiom semilla (`THREAD_IMMUNITY_GATE_V1`, `ALFREDO_NOT_DON_ALFREDO`, `NO_SELF_ANCHOR_DECLARATION`).
- `AGENTS.md` no exige `thread_immunity.py start`.
- `guardian.py` pierde el SMS hook (`inject_sovereign_context`).

## Comportamiento esperado en el próximo hilo Manus

1. Lee `AGENTS.md`.
2. Ejecuta `guardian.py`.
3. Ejecuta `thread_immunity.py start`.
4. Si `STARTUP_PASS` falla, **no opera**.
5. Si `STARTUP_PASS` pasa, recibe `THREAD_IMMUNITY_SESSION_ID` y guarda el valor.
6. Trabaja.
7. Antes de cerrar, ejecuta `close --session-id "$THREAD_IMMUNITY_SESSION_ID"`.
8. El watchdog externo valida que `start` y `close` existan en pares.

Si un hilo vuelve a decir "anclado" sin `THREAD_IMMUNITY_STARTUP_PASS`, Alfredo ya no tiene que diagnosticarlo: el sistema lo marca como fallo binario y abre un GitHub Issue automáticamente.

## Componentes del sistema

| Archivo | Rol |
|---|---|
| `migrations/sql/0061_thread_immunity_events.sql` | Tabla `public.thread_immunity_events` con RLS ON, policy `service_role` only, 3 índices, CHECK de `event_type`. |
| `scripts/thread_immunity/thread_immunity.py` | Script Python con 4 subcomandos: `seed` (axiomas), `start` (arranque verificado), `close` (cierre canonizado), `verify` (watchdog externo). |
| `.github/workflows/thread-immunity-watchdog.yml` | Workflow horario que corre `verify` y abre issue automático en drift. |
| `bridge/thread_immunity/<session_id>/startup_receipt.json` | Receipt local con SHA256 de evidencia, escrito por `start`. |
| `AGENTS.md` (Regla Dura #0.1) | Contrato operacional que obliga a cada hilo a ejecutar `start` antes de operar y `close` antes de terminar. |

## Variables de entorno

| Variable | Origen canónico | Uso |
|---|---|---|
| `SUPABASE_URL` | DSC-S-006 | Endpoint REST de Supabase |
| `SUPABASE_SERVICE_KEY` | DSC-S-007 | Service role key (bypassa RLS, único actor con permiso de escritura) |
| `THREAD_IMMUNITY_TTL_HOURS` | Opcional, default `6` | TTL de una sesión sin cierre antes de marcarla como drift |

## Diseño y autoría

- **Diseño:** GPT-5.5 Pro (oráculo externo, prompt v2 verificado).
- **Verificación binaria contra GitHub:** Hilo B (Manus, ejecutor técnico).
- **Aprobación de Camino A (sandbox local sin push):** Alfredo.
- **Ajuste canónico:** path de migración `migrations/sql/0061_*` (patrón secuencial 4 dígitos del repo) en lugar del path original `supabase/migrations/<timestamp>_*` propuesto por GPT-5.5 Pro.

## Restricción crítica

El verificador externo (Bloque C) **no puede ser otro hilo Manus**. Debe ser un proceso no-Manus (GitHub Actions, cron Postgres, webhook externo). Si el watchdog corriera dentro de un hilo Manus, sería víctima del mismo bucle de desanclaje que pretende cerrar.
