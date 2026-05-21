# Reporte de Reclasificación de Capacidades

**SPRINT:** SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

Este reporte detalla cómo las capacidades detectadas en M2 fueron reclasificadas de su estado inerte (`R0`) a su riesgo operativo real (`R1-R4`).

## Metodología de Elevación

Las capacidades con `evidence_status = REALTIME_VERIFIED` son evaluadas contra las reglas de reclasificación (`03_RISK_RECLASSIFICATION_RULES.md`). Las capacidades con estado `ACCESS_BLOCKED_*` permanecen en `BLOCKED_FOR_AUTOMATION`.

## Resumen de Elevaciones (Post-M2)

### OpenAI
| Capacidad | Riesgo Previo | Riesgo Post-M2 | Autonomía | Razón Principal |
|-----------|---------------|----------------|-----------|-----------------|
| `text_reasoning` | R0 | R1 | A2 | API read-only básica. |
| `vision` | R0 | R1 | A2 | Procesamiento de imagen pasivo. |
| `audio` | R0 | R1 | A2 | Procesamiento de audio pasivo. |
| `embeddings` | R0 | R1 | A2 | Vectorización pasiva. |
| `structured_outputs` | R0 | R1 | A2 | Retorno de JSON estricto. |
| `tool_use` | R0 | R2 | A3 | Capacidad de interactuar con entorno (side effects). |
| `code_execution` | R0 | R3 | A4 | Ejecución en sandbox. Superficie de ataque alta. |

### Anthropic
| Capacidad | Riesgo Previo | Riesgo Post-M2 | Autonomía | Razón Principal |
|-----------|---------------|----------------|-----------|-----------------|
| `text_reasoning` | R0 | R1 | A2 | API read-only básica. |
| `tool_use` | R0 | R2 | A3 | Capacidad de interactuar con entorno. |

### Google Gemini
| Capacidad | Riesgo Previo | Riesgo Post-M2 | Autonomía | Razón Principal |
|-----------|---------------|----------------|-----------|-----------------|
| `text_reasoning` | R0 | R1 | A2 | API read-only básica. |
| `vision` | R0 | R1 | A2 | Procesamiento de imagen pasivo. |
| `audio` | R0 | R1 | A2 | Procesamiento de audio pasivo. |
| `image_generation` | R0 | R1 | A2 | Generación pasiva. |
| `embeddings` | R0 | R1 | A2 | Vectorización pasiva. |
| `structured_outputs` | R0 | R1 | A2 | Retorno de JSON estricto. |
| `tool_use` | R0 | R2 | A3 | Capacidad de interactuar con entorno. |

### xAI Grok
| Capacidad | Riesgo Previo | Riesgo Post-M2 | Autonomía | Razón Principal |
|-----------|---------------|----------------|-----------|-----------------|
| `text_reasoning` | R0 | R1 | A2 | API read-only básica. |
| `vision` | R0 | R1 | A2 | Procesamiento de imagen pasivo. |
| `tool_use` | R0 | R2 | A3 | Capacidad de interactuar con entorno. |

### Proveedores Bloqueados (Perplexity, DeepSeek)
- Todas sus capacidades teóricas permanecen con riesgo `BLOCKED_FOR_AUTOMATION`.
- No se les asigna nivel de autonomía hasta que M2 los verifique empíricamente.
