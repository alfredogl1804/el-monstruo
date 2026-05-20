# Visión de la Verificación en Tiempo Real (M2)

**SPRINT:** SPR-ORACLE-AI-M2-001
**Estado:** DOCTRINE_CANDIDATE

## El Problema de la Evidencia Estática
El Oráculo M1 (SPR-EMBRION-PERITO-LOOP-001) generó un catálogo de capacidades de IA basado en su conocimiento pre-entrenado y en investigación web. Esta evidencia se marcó como `STATIC_CATALOG`. Sin embargo, en el ecosistema de El Monstruo, la asunción de capacidades sin prueba criptográfica o empírica es un riesgo de seguridad (Autoboicot y Falsos Positivos).

## La Solución M2
El Oráculo M2 introduce la capa de **Verificación Empírica**. M2 se conecta a las APIs oficiales de los proveedores (OpenAI, Anthropic, Gemini, Grok, Perplexity, DeepSeek) utilizando credenciales inyectadas en el entorno.

M2 ejecuta **Sondas de Solo Lectura (Read-Only Probes)**. Estas sondas consultan los endpoints de listado de modelos o ejecutan prompts mínimos inofensivos para verificar que el proveedor responde, que la llave es válida, y que los modelos esperados están disponibles.

## El Ascenso de la Evidencia
Solo cuando una sonda retorna un código de éxito (HTTP 200 OK) y los datos coinciden con la expectativa, el estado de evidencia de esa capacidad se eleva a `REALTIME_VERIFIED`.

Si la llave no existe, la sonda falla, o el proveedor está caído, la capacidad se marca como `ACCESS_BLOCKED`. El catálogo estático original **nunca se destruye**; M2 genera un **Overlay de Tiempo Real** que se aplica sobre el catálogo base.

## Límite de Responsabilidad
M2 **no** reclasifica el nivel de riesgo de las capacidades. M2 solo proporciona la evidencia dura (el *ground truth*). La reclasificación de riesgo (elevar de R0 a R1-R4) ocurrirá en un sprint posterior (SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001), separando así la recolección de evidencia de la toma de decisiones de seguridad.
