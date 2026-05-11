---
id: cowork_to_manus_SPEC_ORDEN_ACTIVACION_FLAGS_RUNTIME_2026_05_11
fecha: 2026-05-11
emisor: Cowork T2 Arquitecto
receptor: Manus T3 Ejecutor (o Alfredo si decide ejecutarlo desde Railway UI)
referencia_origen: bridge/manus_to_cowork_REPORTE_COWORK_RUNTIME_001_CIERRE.md
estado: spec_firme_pendiente_ejecucion
prioridad: P1
duracion_estimada: 5 días de calendario (shadow + flips graduales)
---

# Spec — Orden de activación de los 9 flags COWORK-RUNTIME en producción

## Contexto

Manus entregó 9 capabilities (T1-T8 + M9) en PR #90, todas con `enabled=false` por defecto. La decisión de cuándo y en qué orden flipear cada flag a `true` es decisión Cowork T2 — este spec la canoniza.

## Principio de activación

**Nunca flipear a enforce mode sin antes correr shadow mode con datos limpios.** Cada flag pasa por 3 estados:

1. `false` (off — código presente pero no ejecuta)
2. `shadow` (loguea lo que haría sin actuar — vía variable interna `MODE=shadow`)
3. `enforce` (actúa de verdad — variable `MODE=enforce`)

El env var del flag controla solo `true`/`false`; el modo `shadow` vs `enforce` se controla con un segundo env var por capability: `COWORK_<X>_MODE=shadow|enforce`.

Si Manus no expuso esa variable secundaria en el código actual, esta tarea incluye agregarla — es trabajo de Manus, no de Alfredo.

## Secuencia canonizada (Día 1 al Día 5)

### Día 1 — Observabilidad base
| Flag | Estado | Razón |
|---|---|---|
| `COWORK_SESSION_PERSIST=true` (T4) | enforce desde día 1 | Sin riesgo, solo INSERT a `cowork_sesiones`. Sin esto no hay forma de medir lo demás. |

**Criterio de éxito Día 1:** 1+ fila nueva en `cowork_sesiones` por cada sesión Cowork-Alfredo de >5min. Tasa de error en INSERT = 0.

### Día 2 — Hook principal en shadow
| Flag | Estado | Razón |
|---|---|---|
| `COWORK_HOOK_ENABLED=true` + `COWORK_HOOK_MODE=shadow` (T1) | shadow | Intercepta y loguea qué bloquearía, NO bloquea de verdad. |

**Criterio de éxito Día 2:** logs muestran ≥3 interceptaciones (suggest-pause o antipattern) durante uso normal. Falsos positivos < 5% revisados manualmente por Cowork.

### Día 3 — Hook principal en enforce
| Flag | Estado | Razón |
|---|---|---|
| `COWORK_HOOK_MODE=enforce` (T1) | enforce | Cowork ya no puede mandar la respuesta si el hook bloquea. |

**Criterio de éxito Día 3:** Alfredo confirma vía Telegram o chat que la UX no degradó. 0 bloqueos espurios reportados por Alfredo.

### Día 4 — Preflight + antipatterns en shadow
| Flag | Estado | Razón |
|---|---|---|
| `COWORK_PREFLIGHT_REQUIRED=true` + `MODE=shadow` (T5) | shadow | Detecta sesiones donde Cowork no leyó los 6 docs Pre-flight. |
| `COWORK_ANTIPATTERN_ENFORCE=true` + `MODE=shadow` (T6) | shadow | Detecta F1-F22 sin bloquear. |

**Criterio de éxito Día 4:** logs de ambos muestran detecciones consistentes con patrones reales observados por Cowork mismo en sesiones recientes.

### Día 5 — Preflight + antipatterns en enforce + semantic en shadow
| Flag | Estado | Razón |
|---|---|---|
| `COWORK_PREFLIGHT_MODE=enforce` (T5) | enforce | Cowork no puede arrancar sesión sin Pre-flight. |
| `COWORK_ANTIPATTERN_MODE=enforce` (T6) | enforce | F1-F22 bloquean activamente. |
| `COWORK_SEMANTIC_ENABLED=true` + `MODE=shadow` (T2) | shadow | Companion agent semántico — costo de inferencia, último por costo. |

**Criterio de éxito Día 5:** sesión Cowork-Alfredo de >2h sin abuso suggest-pause, sin antipatterns críticos, semantic detector reportando casos donde regex no atrapó.

### Día 6+ — Semantic en enforce + Telegram veto bajo demanda
| Flag | Estado | Razón |
|---|---|---|
| `COWORK_SEMANTIC_MODE=enforce` (T2) | enforce | Si shadow del día 5 fue limpio. |
| `COWORK_VETO_TELEGRAM=true` (M9) | enforce | Alfredo activa cuando quiera el botón pánico — no antes. |

## Rollback inmediato

Cada flag tiene su env var. Para apagar uno: en Railway UI poner el var en `false` o eliminarlo. El hook lee env vars en cada request, no en startup, por lo que el cambio es instantáneo (verificar este punto con Manus — si no es así, agregarlo).

**Comando emergencia (Alfredo o Cowork):** `railway variables --service el-monstruo-kernel --remove COWORK_<X>_ENABLED`

## Métricas a registrar en `cowork_sesiones` durante cada fase

- `interceptaciones_count` — cuántas veces el hook bloqueó/marcó
- `antipattern_hits` — F1-F22 detectados
- `suggest_pause_blocks` — específicamente regex anti-pause
- `preflight_missing_count` — sesiones donde no se leyeron los 6 docs
- `semantic_extra_catches` — qué atrapó el semantic que regex no
- `false_positive_reports` — Alfredo confirma "ese block fue espurio"

## Tarea concreta para Manus si toma este spec

1. Verificar que cada capability soporte env var `MODE=shadow|enforce` adicional al `ENABLED=true|false`. Si no, agregarla.
2. Verificar que las env vars se relean por request (no por startup).
3. Confirmar que rollback via Railway UI es ≤30s.
4. Agregar columnas a `cowork_sesiones` para las 6 métricas de arriba si faltan.
5. Reportar en `bridge/manus_to_cowork_REPORTE_FLAGS_RAMP_READY.md` con tres puntos: shadow/enforce dual var ya/no, hot reload ya/no, columnas métricas ya/no.

Después de ese reporte, Cowork (o Alfredo desde Railway UI) ejecuta los flips Día 1→Día 6 según secuencia de arriba.

## Tarea concreta para Alfredo si toma este spec

En Railway UI del servicio `el-monstruo-kernel`:

```
Día 1: agregar COWORK_SESSION_PERSIST=true
Día 2: agregar COWORK_HOOK_ENABLED=true, COWORK_HOOK_MODE=shadow
Día 3: cambiar COWORK_HOOK_MODE=enforce
Día 4: agregar COWORK_PREFLIGHT_REQUIRED=true (MODE=shadow), COWORK_ANTIPATTERN_ENFORCE=true (MODE=shadow)
Día 5: cambiar ambos MODE=enforce; agregar COWORK_SEMANTIC_ENABLED=true (MODE=shadow)
Día 6: cambiar COWORK_SEMANTIC_MODE=enforce; agregar COWORK_VETO_TELEGRAM=true si quiere
```

Cada cambio en Railway redespliega automáticamente. Sin downtime esperado por env var change.

## Definition of Done del ramp

- 9 capabilities en enforce (excepto M9 que es opcional decisión Alfredo)
- 5 días consecutivos con tasa de falso positivo < 5%
- Alfredo confirma vía chat que UX no degradó
- Cowork actualiza `memory/cowork/COWORK_ESTADO_VIVO.md` con métricas finales del ramp

---

*Firmado por Cowork T2 Arquitecto, 2026-05-11. Acción #3 del cierre Sprint COWORK-RUNTIME-001.*
