# TEST DE DENSIDAD Y COMPRESIÓN (DENSITY TEST)

## Objetivo
Evaluar el ratio de reducción actual entre el contexto largo humano (`input_long_context.md`) y la configuración espacial JSON (`shell_encoding_attempt_001.json`), identificando áreas de mejora para futuras versiones de codificación.

## Reglas de Evaluación
1.  **No afirmar éxito prematuro:** Está estrictamente prohibido afirmar que se ha logrado el objetivo de "50k en 5 bytes" o que la compresión clásica ha sido superada.
2.  **Identificar verbosidad:** Se deben señalar las partes del JSON simulado que siguen siendo legibles por humanos (verbose) y que, por tanto, no son verdadero "micropolvo".
3.  **Proponer dirección:** Definir qué campos específicos deben convertirse en representaciones matemáticas o hashes en iteraciones futuras.

## Metodología
Se utilizarán herramientas estándar de shell (`wc -c` para bytes, `wc -w` para palabras como proxy de tokens) para medir el tamaño de ambos archivos y calcular el ratio de reducción actual. El análisis cualitativo se enfocará en el contenido del JSON.
