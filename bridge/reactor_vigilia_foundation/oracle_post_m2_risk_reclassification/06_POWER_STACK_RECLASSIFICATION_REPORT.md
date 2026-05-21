# Reporte de Reclasificación de Power Stacks

**SPRINT:** SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

Un Power Stack es una combinación de capacidades. Su riesgo derivado se calcula como el máximo riesgo de sus componentes, más un bonus si mezcla capacidades que multiplican la superficie de ataque (ej. API externa + ejecución de código).

## Resumen de Elevaciones de Stacks

| Power Stack | Componentes Clave | Riesgo Post-M2 | Autonomía Requerida | Razón |
|-------------|-------------------|----------------|---------------------|-------|
| `stack_deep_research` | Perplexity + OpenAI/Anthropic | `BLOCKED_FOR_AUTOMATION` | N/A | Perplexity está `ACCESS_BLOCKED`. El stack entero se degrada. |
| `stack_code_architect` | OpenAI Code Exec + Anthropic Tool Use | `R4` | `A4` | Combina ejecución de código (`R3`) con uso de herramientas (`R2`). El bonus eleva el riesgo total a `R4`. |
| `stack_vision_qa` | Gemini Vision + OpenAI Text | `R1` | `A2` | Ambos componentes son `R1`. No hay bonus por side effects destructivos. |
| `stack_autonomous_agent` | Tool Use (varios) + Grok/Anthropic | `R3` | `A3` | Combina múltiples herramientas (`R2`). Riesgo compuesto elevado. |

## Impacto del Estado M2 en Stacks

La regla más estricta del Monstruo es la de eslabón débil: **Si un Power Stack depende de una capacidad o proveedor que está `ACCESS_BLOCKED`, el stack entero no puede ser automatizado.**

Esto demuestra el valor de la verificación M2: en M1 (catálogo estático), el stack `stack_deep_research` parecía viable. Tras M2, sabemos empíricamente que fallará en producción, por lo que el Policy Engine lo bloqueará proactivamente.
