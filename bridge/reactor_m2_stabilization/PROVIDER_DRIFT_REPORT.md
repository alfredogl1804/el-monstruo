# Provider Drift Report

**Fecha de Detección:** 2026-05-21
**Sprint:** SPR-REACTOR-M2-ONESHOT-001

## Resumen del Incidente
Durante la primera ejecución one-shot de la cadena M2, se detectó un *provider drift* (obsolescencia de modelos) en dos de los cuatro proveedores autorizados. El código original apuntaba a modelos que los proveedores ya han marcado como deprecados o han retirado del acceso para nuevos usuarios.

## Detalles del Drift

### 1. Anthropic
- **Modelo Solicitado:** `claude-3-5-haiku-20241022`
- **Error/Warning:** `DeprecationWarning: The model 'claude-3-5-haiku-20241022' is deprecated and will reach end-of-life...`
- **Acción Tomada:** Actualizado en el registro a `claude-sonnet-4-20250514`.

### 2. Google (Gemini)
- **Modelo Solicitado:** `gemini-2.0-flash-lite`
- **Error/Warning:** `404 This model models/gemini-2.0-flash-lite is no longer available to new users.`
- **Acción Tomada:** Actualizado en el registro a `gemini-2.0-flash`.

*(Nota adicional: La librería `google.generativeai` arrojó un `FutureWarning` indicando que el soporte ha terminado y se debe migrar a `google.genai`. Esta migración técnica se programará para un sprint futuro; por ahora, el cambio de nombre de modelo resolvió el error 404).*

## Políticas de Mitigación
1. **No Retries en Drift:** Si un modelo falla por error 404 de obsolescencia o advertencia de deprecación, el Oráculo shadow **NO** debe hacer un retry automático. Debe fallar, registrar el drift y requerir actualización manual del registro.
2. **Registry como Fuente de Verdad:** El código ejecutor de la cadena M2 debe leer los modelos a utilizar directamente de `PROVIDER_REGISTRY_M2.json` para asegurar consistencia.
