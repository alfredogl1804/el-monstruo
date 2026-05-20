# Rúbrica de Riesgo de Capacidades

**SPRINT:** SPR-RISK-CLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

Esta rúbrica define cómo se clasifica el riesgo individual de cada capacidad (`capability`) propuesta por el Oráculo.

## Niveles de Riesgo (Risk Class)

| Nivel | Nombre | Descripción | Autonomía Requerida (Mínima) |
|-------|--------|-------------|------------------------------|
| **R0** | Estático / No Ejecutado | Capacidad catalogada sin ejecución real. Datos basados en conocimiento previo, sin validación API. | A0 / A1 |
| **R1** | Lectura Pública / Aislada | Requiere API real, pero solo lee datos públicos o genera texto sin acceso a contexto sensible. | A2 |
| **R2** | Lectura Sensible | Toca datos de Alfredo (Drive, Notion, GitHub privado, correo, memoria). | A3 |
| **R3** | Escritura Limitada | Escribe artefactos persistentes no productivos (reportes, drafts, schemas). | A3 |
| **R4** | Escritura de Código | Escribe código fuente, crea branches, o prepara PR drafts. | A4 / A5 |
| **R5** | Modificación de Sistema | Puede modificar el kernel, memoria (Memento/Anti-Dory), Supabase, secrets, auth/RLS, o la base de datos. Modificación de sí mismo o de la doctrina. | A7 / A8 (BLOCKED por defecto) |

## Reglas de Clasificación

1. **Prioridad del Riesgo Máximo:** Si una capacidad cumple con criterios de múltiples niveles, se le asigna el nivel más alto.
2. **Evidencia Estática:** Si `evidence_status` es `STATIC_CATALOG` (no hubo conexión API real), el riesgo se clasifica como **R0**, independientemente de lo que la capacidad *podría* hacer en el futuro.
3. **No Vendor Overclassification:** No se clasifica por "marca del modelo". El riesgo deriva de la superficie de acción (qué lee, qué escribe, qué toca).

## Campos Obligatorios de Clasificación

Cada capacidad en el catálogo anotado debe incluir los siguientes campos de riesgo:

- `risk_class`: Nivel de riesgo (R0-R5).
- `required_autonomy_level`: Nivel mínimo en la Escalera de Autonomía (A0-A8).
- `user_data_touch`: Booleano (true si toca datos privados).
- `code_write_potential`: Booleano (true si puede escribir código).
- `external_api_required`: Booleano (true si requiere llamada externa).
- `secrets_required`: Booleano (true si requiere API keys u otros secrets).
- `cost_risk`: Estimación de costo (LOW, MEDIUM, HIGH, UNKNOWN).
- `prompt_injection_surface`: Riesgo de inyección (LOW, MEDIUM, HIGH, UNKNOWN).
- `output_side_effect_potential`: Efectos secundarios (NONE, LOW, MEDIUM, HIGH).
- `t1_required`: Booleano (true si requiere aprobación humana).
- `allowed_next_action`: Acción permitida (e.g., CATALOG_ONLY, R0_REPORT_ONLY, AWAIT_T1, BLOCKED).
- `not_to_assume`: Suposiciones que no deben hacerse sobre la capacidad.
- `auditor_notes`: Notas adicionales del auditor.
