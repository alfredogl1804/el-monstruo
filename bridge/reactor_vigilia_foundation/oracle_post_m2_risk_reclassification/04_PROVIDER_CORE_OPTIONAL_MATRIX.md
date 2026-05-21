# Matriz: Proveedores Core vs. Opcionales

**SPRINT:** SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

Este documento define la metodología para proponer a T1 qué proveedores deben ser considerados fundamentales (Core) para la operación del Monstruo y cuáles son auxiliares (Opcionales). **Este sprint solo propone; T1 decide.**

## Categorías de la Matriz

| Categoría | Descripción |
|-----------|-------------|
| `CORE_CANDIDATE` | Proveedor crítico. Si falla, operaciones clave del Monstruo se detienen. |
| `OPTIONAL_CANDIDATE` | Proveedor útil pero no bloqueante. Su caída degrada capacidades secundarias. |
| `BLOCKED_PENDING_CREDENTIALS` | Proveedor con potencial pero actualmente inaccesible por falta de credenciales. |
| `DEFER` | Decisión pospuesta por falta de evidencia o utilidad clara. |
| `RETIRE_CANDIDATE` | Proveedor obsoleto o redundante que debería ser eliminado del catálogo. |

## Criterios para proponer `CORE_CANDIDATE`

Para que un proveedor sea propuesto como Core, debe cumplir con la mayoría de estos criterios:

1. **Evidencia Empírica:** Su estado en M2 debe ser `REALTIME_VERIFIED`.
2. **Alto Valor Estratégico:** Provee capacidades avanzadas (ej. razonamiento complejo, tool use confiable, visión de alta fidelidad) esenciales para el Oráculo.
3. **Estabilidad:** Historial de alta disponibilidad y baja tasa de errores (inferido o conocido).
4. **Costo Controlable:** Modelos con precios predecibles y razonables para operaciones recurrentes.
5. **Riesgo Manejable:** Superficie de ataque comprendida y mitigable mediante la Escalera de Autonomía.
6. **Independencia de Datos Privados (Inicial):** Puede aportar valor operando solo con contexto inyectado, sin requerir acceso irrestricto a repositorios privados desde el día 1.

## Aplicación a los Resultados M2

Basado en los resultados de `SPR-ORACLE-AI-M2-001`:

- **OpenAI, Anthropic, Google Gemini:** Fuertes candidatos a `CORE_CANDIDATE` debido a su verificación en tiempo real, amplio soporte de tool use y razonamiento avanzado.
- **xAI Grok:** Candidato a `OPTIONAL_CANDIDATE` o `CORE_CANDIDATE` dependiendo de la estrategia de redundancia de T1.
- **Perplexity, DeepSeek:** Clasificados como `BLOCKED_PENDING_CREDENTIALS`. No pueden ser Core hasta que M2 los verifique exitosamente.
