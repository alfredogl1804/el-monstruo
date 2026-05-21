# M2 Chain Gates

Las "Gates" (puertas de validación) son puntos de control críticos dentro de la cadena M2 que deben superarse exitosamente para que la ejecución continúe.

## Gate 1: Heartbeat Wake
- **Condición:** `kill-switch` == `false`.
- **Fallo:** Aborto inmediato.

## Gate 2: Anti-Loop
- **Condición:** No se ha ejecutado un ciclo exitoso en las últimas 12 horas.
- **Fallo:** Aborto inmediato (prevención de loops infinitos).

## Gate 3: Identity Guard
- **Condición:** `user_id` != `anonymous` (o validación explícita de contexto de sistema).
- **Fallo:** Bloqueo de la operación.

## Gate 4: Preflight Check
- **Condición:** Todos los constraints (0 Supabase, 0 secrets, etc.) se mantienen.
- **Fallo:** La cadena se detiene antes de invocar al Oráculo.

## Gate 5: Budget Authorization
- **Condición:** La ejecución solicitada está dentro del budget autorizado por T1.
- **Fallo:** Fallback a ejecución R0 local o aborto.

## Gate 6: Provider Readiness
- **Condición:** Los proveedores requeridos por el Oráculo están verificados y tienen keys válidas.
- **Fallo:** El Oráculo omite al proveedor fallido o aborta si no se alcanza el quórum mínimo.

## Gate 7: Auditor Compliance
- **Condición:** El output del Oráculo pasa la revisión del Auditor contra los 15 Objetivos Maestros.
- **Fallo:** El output es descartado o marcado para revisión manual.
