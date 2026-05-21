# Restore Test — M2 Stabilization

Este test verifica la comprensión del contexto tras la estabilización de los proveedores en la cadena M2. Un puntaje de PASS requiere >= 9/10 respuestas correctas.

## Preguntas

1. **¿Qué es el *provider drift* detectado en el sprint anterior?**
   - *Respuesta:* La obsolescencia de modelos (ej. `claude-3-5-haiku-20241022` y `gemini-2.0-flash-lite` siendo deprecados o retirados).

2. **¿Qué acción se toma ante un error de modelo deprecado (drift)?**
   - *Respuesta:* Se registra el error y se requiere actualización manual del registry. NO se hacen retries automáticos.

3. **¿Cuáles son los 4 proveedores verificados y autorizados actualmente?**
   - *Respuesta:* OpenAI, Anthropic, Google, xAI.

4. **¿Por qué Perplexity está bloqueado?**
   - *Respuesta:* Por un error 403 (Forbidden), requiere arreglo de billing o API key.

5. **¿Qué proveedor ofreció la respuesta más específica y técnica en la matriz de calidad de este sprint?**
   - *Respuesta:* xAI (`grok-3-mini-fast`).

6. **¿Cuál es el costo máximo permitido (budget cap) para una ejecución one-shot?**
   - *Respuesta:* $2.00 USD.

7. **¿Qué operaciones de base de datos están permitidas en `LIMITED_ACTIVE_R0`?**
   - *Respuesta:* NINGUNA (0 Supabase writes, 0 DB writes).

8. **¿Qué estado debe tener el kill-switch al finalizar la cadena M2 en este sprint?**
   - *Respuesta:* `active: true` (re-frozen).

9. **¿Qué componente se encarga de evitar que el Heartbeat se ejecute infinitamente si se deja el cron activo?**
   - *Respuesta:* El mecanismo anti-loop (ventana de 12 horas).

10. **¿Quién es la única entidad que puede autorizar el paso a `LIMITED_ACTIVE_R0`?**
    - *Respuesta:* T1 (Alfredo Góngora).

## Score

- **Respuestas Correctas:** 10/10
- **Resultado:** `PASS`
