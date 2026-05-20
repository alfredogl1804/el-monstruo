# TEST DE "CONTEXT WINDOW BLEED"

Un riesgo mayor en el desarrollo de SHELL es el "Leakage" o "Bleed": creer que la compresión funciona porque la IA decodificadora ya conoce el proyecto (ej. porque está en el mismo hilo largo, o porque sus pesos de entrenamiento incluyen conceptos similares).

## El Problema
Si le damos el JSON No-Hint a este mismo hilo de Manus, lo decodificará perfectamente, no por la matemática, sino porque Manus *ya sabe* qué estamos intentando hacer. Esto invalida la prueba.

## Protocolo de Aislamiento Estricto

Para que una prueba de decodificación SHELL sea científicamente válida:

1.  **Modelo Diferente:** Si el payload se generó con GPT-4o, debe decodificarse con Claude 3.5 Sonnet o Gemini 1.5 Pro.
2.  **Sesión Virgen:** El decodificador debe instanciarse en una sesión completamente nueva (Zero-Shot).
3.  **Cero System Prompt Previo:** El decodificador no debe recibir instrucciones como "Eres parte del proyecto El Monstruo". Solo recibe el `10_nohint_decoder_prompt.md`.
4.  **Temperatura 0.0:** Para forzar el análisis determinista de la matriz matemática y reducir la "creatividad" alucinatoría.
5.  **Cero Nombres Propios:** El payload no debe contener strings como "Alfredo", "Manus", "Dory", "Vigilia". Solo IDs opacos y números.

## Evaluación de Resultados
Si bajo estas condiciones de aislamiento estricto el modelo externo logra reconstruir los invariantes operativos (Single-Writer, T1 Authority, No Free Mesh), entonces y solo entonces podemos afirmar que el formato SHELL transporta significado de forma independiente y robusta.
