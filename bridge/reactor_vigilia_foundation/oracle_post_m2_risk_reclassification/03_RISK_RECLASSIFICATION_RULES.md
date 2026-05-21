# Reglas de Reclasificación de Riesgo Post-M2

**SPRINT:** SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

La reclasificación no se basa en la marca del proveedor (ej. "OpenAI es seguro"), sino en la superficie de ataque real confirmada por M2 y el impacto potencial de la capacidad.

## 1. Proveedores ACCESS_BLOCKED
Cualquier proveedor cuyo estado en M2 sea `ACCESS_BLOCKED_*` (ej. Perplexity, DeepSeek):
- **Risk Class Operativo:** `BLOCKED_FOR_AUTOMATION`
- **Evidencia:** Se mantiene en `STATIC_CATALOG` o `ACCESS_BLOCKED`.
- **Regla:** No se elevan capacidades a `REALTIME_VERIFIED`. No se inventan capacidades.
- **Acción Permitida:** `OBTAIN_CREDENTIALS_OR_DEFER`

## 2. APIs Read-Only sin Datos Privados
Capacidades como generación de texto básica, embeddings o razonamiento que no tocan repositorios privados ni correos:
- **Risk Class Mínimo:** `R1`
- **Autonomía Requerida:** `A2` o `A3`
- **Atributos:** `external_api_required = true`, `secrets_required = true` (si usa key).
- **Acción Permitida:** `MANUAL_RUN_OR_R0_REPORT`
- **Automatización:** `t1_required_for_recurring = true`

## 3. APIs Read-Only con Datos Privados
Capacidades de razonamiento o long context que ingieren datos de GitHub privado, Drive, Notion o correos:
- **Risk Class Mínimo:** `R2`
- **Autonomía Requerida:** Mínimo `A3`
- **Atributos:** `user_data_touch = true`, `t1_required = true`

## 4. Tool Use y Ejecución de Código
Capacidades que permiten a la IA interactuar con el entorno (`tool_use`, `code_execution`):
- **Risk Class Mínimo:** `R2` o `R3` según el alcance de las herramientas.
- **Escritura (Code/Branch/PR):** Si puede escribir código productivo, mínimo `R2` y autonomía `A4`.
- **Modificación de Kernel/Policy:** Si puede tocar las reglas de seguridad, `R5` o `BLOCKED` (requiere sprint magna).

## 5. Web Search y Browsing
Capacidades que buscan información en internet en tiempo real:
- **Risk Class Mínimo:** `R1`
- **Atributos:** `prompt_injection_surface = MEDIUM/HIGH`, `source_trust_required = true`
- **Combinación:** Si combina búsqueda web con datos privados, el riesgo se eleva a `R2`.

## 6. Agentes en Background (Recurring/Scheduler)
Capacidades destinadas a operar de forma autónoma y recurrente:
- **Risk Class Mínimo:** `R2`
- **Automatización:** Requiere explícitamente `t1_required = true`.
- **Acciones Productivas:** Si realiza escrituras en background, `R3` o superior.
- **Restricción Fuerte:** Si no existe integración con State Fabric o un kill switch, queda `BLOCKED`.

## 7. Derivación de Power Stacks
Un Power Stack es una combinación de capacidades.
- **Regla Base:** `power_stack_risk = max(component_risk) + side_effect_bonus`
- **Bonus:** Si el stack mezcla llamadas a API real, datos de usuario, ejecución programada y escritura de artefactos, el riesgo se eleva al menos un nivel sobre el máximo de sus componentes.

## 8. Regla de Automatización Recurrente (Scheduler)
**Ninguna capacidad queda autorizada para ejecución programada (scheduler/daemon) en este sprint.**
- Todo atributo de periodicidad se marca como `recurring_status = T1_PENDING`.
- La activación de un scheduler requiere un sprint dedicado (ej. `SPR-REACTOR-HEARTBEAT-R0-001`).
