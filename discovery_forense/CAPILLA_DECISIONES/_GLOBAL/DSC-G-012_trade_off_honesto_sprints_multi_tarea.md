# DSC-G-012 — Trade-off honesto en sprints multi-tarea

**ID:** DSC-G-012
**Tipo:** GLOBAL (gobernanza de ejecucion)
**Fecha:** 2026-05-07
**Estado:** Firmado
**Origen:** Sprint S-001 Security Hardening — ejecucion Opcion C hibrida
**Hilos firmantes:** Hilo A (Cowork) + Hilo B/Catastro (Manus)
**Relacion con otros DSCs:** complementa DSC-G-008 (validacion pre-spec/pre-cierre), DSC-G-011 (clasificacion de exposure PUBLICA/PRIVADA/ACOTADA/EFIMERA), DSC-G-013 (autoria revisable), DSC-S-005 (archive antes que delete), DSC-S-010 (exposure historica vs operacional).

---

## Contexto

Durante el cierre de Stream 2 (CATASTRO-A v2 + CATASTRO-B + S-001 Security Hardening), se observo un patron de bloqueo:

- Sprints multi-tarea agrupan acciones de **distinto perfil de riesgo** (read-only, write-safe, write-risky, requiere-coordinacion-humana).
- Si el sprint se trata como bloque atomico ("todo o nada"), las tareas seguras quedan **bloqueadas** esperando validacion humana de las riesgosas.
- El resultado es **stuck total**: ninguna tarea cierra hasta que las mas peligrosas se resuelven, aunque las seguras esten 100% listas.

Este antipatron se observo concretamente en S-001:

| Tarea | Perfil | Si esperamos validacion para todo... |
|---|---|---|
| S-1.1 pre-commit hooks | write-safe (config local) | quedaria bloqueada |
| S-1.4 GitHub Actions secret-scan | write-safe (workflow nuevo) | quedaria bloqueada |
| S-1.7 audit transcripts | read-only | quedaria bloqueada |
| S-1.2 refactor scripts viejos | write-risky (regresion) | requiere validacion humana |
| S-1.6 rename env vars Railway | write-risky (downtime) | requiere ventana coordinada |

Tratar el sprint como bloque atomico significa que ningun mecanismo de defensa nuevo se activa hasta que el item mas riesgoso (rename Railway) se ejecuta, lo cual puede tomar dias. Mientras tanto, la posibilidad de un nuevo incidente sigue abierta.

---

## Decision

**Los sprints multi-tarea pueden y deben cerrarse parcialmente cuando es seguro hacerlo.**

Reglas operativas:

### 1. Clasificacion obligatoria de tareas por perfil de riesgo

Cada tarea de un sprint debe etiquetarse con uno de:

- **read-only** — solo lectura (audit, scan, query). Sin riesgo de regresion.
- **write-safe** — escritura aislada (archivo nuevo, hook local, workflow nuevo). Reversible trivial.
- **write-risky** — modifica codigo/infra existente. Posible regresion.
- **requiere-coordinacion-humana** — necesita ventana, validacion presencial, o decision fuera del repo.

### 2. Orden de ejecucion preferente

1. Ejecutar primero **read-only** + **write-safe**.
2. Reportar cierre parcial al bridge con tabla de status.
3. Diferir **write-risky** y **requiere-coordinacion-humana** con razon explicita y owner.
4. El sprint queda en estado **PARCIAL — DECLARADO** hasta que las diferidas cierren.

### 3. Cierre parcial es valido

Un sprint PARCIAL — DECLARADO con N/M tareas verdes + (M-N) diferidas con razon es **estado valido y reportable**, no estado de fracaso. Cumple el criterio "valor entregado > 0" mejor que "stuck total".

### 4. Frase canonica

```
🏛️ <NOMBRE_SPRINT> — DECLARADO (N/M verde + K diferidas)
```

donde:
- N = tareas cerradas verde
- M = total de tareas en el sprint
- K = tareas diferidas con razon documentada

Si N == M, omitir el sufijo `(N/M verde + K diferidas)`.

### 5. Tareas diferidas requieren tabla en el reporte bridge

Cada diferida debe documentar:

| Campo | Requerido |
|---|---|
| ID tarea | Si |
| Razon de diferimiento | Si |
| Owner para retomar | Si |
| Pre-condicion para ejecutar | Si |
| Estimacion de impacto si NO se ejecuta | Si |

### 6. Reapertura natural

Cuando las pre-condiciones de las diferidas se cumplan, el sprint se reabre como sub-sprint focalizado (ej. S-001b). NO se "reabre" el sprint padre — el padre ya cerro PARCIAL.

---

## Antipatron evitado

**Bucle infinito de validacion cosmetica:**

> "Esperemos a que Cowork+Alfredo validen todo antes de mover nada → tareas seguras esperan → mecanismos de defensa no se activan → ventana de exposicion se mantiene abierta → otra incidencia ocurre antes del cierre."

DSC-G-012 rompe este bucle: las tareas seguras se ejecutan inmediatamente; las riesgosas se diferren con tabla; el sprint cierra parcial; nadie pierde el progreso.

---

## Implicaciones

- **Bridge files** deben aceptar la estructura `verde/diferida/razon` como formato estandar.
- **Cowork** valida el cierre parcial verificando solo las tareas verdes (no las diferidas).
- **Manus** propone el cierre parcial cuando detecta tareas seguras listas; Cowork firma o rechaza con razon.
- **Sprints futuros** deben pre-clasificar tareas en la spec, no descubrirlo en ejecucion.

---

## Trazabilidad

- **Origen empirico:** S-001 — 4 tareas write-safe + 1 read-only listas, mientras 2 write-risky + 1 read-only requerian validacion humana.
- **Decision tomada:** ejecutar las 5 listas, archivar 9 scripts del breach (S-1.2.b), diferir 2 write-risky con tabla.
- **Resultado:** S-001 PARCIAL DECLARADO con 6/8 tareas verde + 1 archivar simple + 2 diferidas. Defensas activas en repo desde 2026-05-07 sin esperar coordinacion humana.

---

**Firma Hilo A (Cowork):** ✅ aceptado en mensaje "✅ CORRECCIÓN — Cowork acepta error de bucle. DSC-G-011 + G-013 + S-010 aplicados" (2026-05-07).
**Firma Hilo B (Manus/Catastro):** ✅ canonizado en este DSC.
