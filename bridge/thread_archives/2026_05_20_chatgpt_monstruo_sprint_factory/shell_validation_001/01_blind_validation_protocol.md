# PROTOCOLO DE VALIDACIÓN CIEGA (BLIND DECODER)

## Objetivo
Demostrar que la codificación SHELL (micropolvo semántico) transmite entendimiento operativo real y no es simplemente el resultado de una "alucinación circular" donde la IA que codifica y decodifica tiene el mismo contexto previo.

## Reglas Estrictas para el Validador
1.  **Aislamiento:** La IA o modelo externo que ejecute la decodificación debe operar en una sesión/contexto completamente limpio.
2.  **Archivos Prohibidos:** El validador NO debe tener acceso a:
    *   `input_long_context.md` (el texto original).
    *   `decoded_understanding_report.md` (el reporte de la simulación 1).
    *   `simulation_summary.md`.
    *   Cualquier otro archivo del archivo de hilos que describa la Vigilia Sincrónica.
3.  **Archivos Permitidos (Blind Packet):**
    *   `shell_encoding_attempt_001.json` (la configuración espacial).
    *   `decoder_prompt_ia_only.md` (las instrucciones de decodificación).
    *   `equivalence_rubric.yaml` (los criterios a evaluar).
4.  **Formato de Salida:** El validador debe producir un reporte siguiendo el `04_blind_validation_results_template.md`.

## Criterios de Éxito
El test se considera PASS si el validador independiente logra una puntuación de 9/10 o 10/10 en la rúbrica de equivalencia, basándose *exclusivamente* en las relaciones y propiedades topológicas definidas en el JSON.
