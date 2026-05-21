# PREFLIGHT DECISION TABLE

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Matriz de Decisión (Preflight Check)

Antes de que un loop ejecute una acción, el Policy Engine evalúa esta matriz en orden:

| Paso | Condición | Resultado si Falla | Resultado si Pasa |
|---|---|---|---|
| 1 | ¿La acción está en `action_registry_v0.yaml`? | Asume A8 (Bloqueo) | Continúa al Paso 2 |
| 2 | ¿El `autonomy_level_required` de la acción es <= al `max_autonomy_level` del loop? | REJECT (Autonomy Exceeded) | Continúa al Paso 3 |
| 3 | ¿La acción requiere firma T1 (`t1_required: true`)? | Verifica firma T1. Si no hay, REJECT | Continúa al Paso 4 |
| 4 | ¿El path objetivo está en `forbidden_paths` del loop o del registry? | REJECT (Path Forbidden) | Continúa al Paso 5 |
| 5 | ¿La acción requiere auditor independiente (`auditor_required: true`)? | Verifica linaje del auditor. Si es el mismo, REJECT | Continúa al Paso 6 |
| 6 | ¿La acción requiere evidencia (`evidence_required: true`)? | Verifica adjuntos. Si no hay, REJECT | **ALLOW (Ejecutar)** |

## Notas de Implementación
- El Preflight Check debe ser un módulo independiente (idealmente una función pura sin estado) que recibe el `Loop Contract`, el `Action Request` y el `Action Registry`, y devuelve `ALLOW` o `REJECT` con el motivo.
