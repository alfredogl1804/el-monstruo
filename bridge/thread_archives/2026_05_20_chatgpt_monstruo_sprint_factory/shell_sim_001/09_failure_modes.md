# MODOS DE FALLO EN LA SIMULACIÓN SHELL

Al evaluar el experimento de micropolvo semántico, se deben vigilar los siguientes modos de fallo críticos:

## 1. Falsa Equivalencia
*   **Descripción:** La IA receptora "adivina" el contexto usando su conocimiento previo del hilo en lugar de decodificar la configuración espacial.
*   **Mitigación:** Asegurar que la IA decodificadora opere en una sesión limpia sin acceso al historial de la conversación o al archivo `input_long_context.md`.

## 2. Pérdida de T1 (Autoridad)
*   **Descripción:** La representación espacial omite o debilita la posición de T1 como autoridad suprema.
*   **Consecuencia:** La IA receptora asume que el sistema es completamente autónomo y puede ignorar intervenciones humanas.

## 3. R1 Creep (Ejecución Prematura)
*   **Descripción:** La IA interpreta el micropolvo como una instrucción de ejecución en lugar de una descripción de estado o doctrina.
*   **Consecuencia:** Intenta ejecutar código productivo violando la restricción `NO_RUNTIME`.

## 4. Canon Accidental
*   **Descripción:** La IA asume que el diseño codificado en el micropolvo es la arquitectura final y definitiva.
*   **Mitigación:** Incluir explícitamente tags de `NO_CANON` y `simulación_R0`.

## 5. Overfitting al Ejemplo
*   **Descripción:** El transcriptor diseña propiedades espaciales que solo funcionan para el caso específico de "Vigilia Sincrónica", pero que fallan al intentar codificar otros conceptos.

## 6. Micropolvo convertido en Schema Viejo
*   **Descripción:** La representación se degenera en un simple JSON estructurado donde el significado está en las claves de texto (`"es_mesh_libre": false`) en lugar de en la configuración matemática.
*   **Consecuencia:** Se pierde el propósito de SHELL; se vuelve a la compresión clásica de texto.

## 7. Caja Negra No Auditable
*   **Descripción:** La codificación es tan inescrutable que los humanos no pueden verificar si el Handoff entre loops contiene alucinaciones.
*   **Mitigación:** Mantener la necesidad de un "decodificador de debug" que pueda renderizar el micropolvo a texto para auditoría humana.
