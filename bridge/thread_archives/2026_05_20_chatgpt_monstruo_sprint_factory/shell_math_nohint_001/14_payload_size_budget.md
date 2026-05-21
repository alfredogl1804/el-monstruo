# PAYLOAD SIZE BUDGET

Para medir el progreso a lo largo de la "Density Path", establecemos las siguientes métricas y presupuestos.

## Métricas de Medición
1.  **Bytes (Raw):** Tamaño del payload en disco.
2.  **Tokens (LLM):** Número de tokens que consume el payload al ser procesado por un tokenizer estándar (ej. `cl100k_base`).
3.  **Equivalencia Funcional:** Score de PASS/FAIL en la rúbrica de decodificación (debe mantenerse $\ge 9/10$).
4.  **Error Crítico:** Cualquier fallo en decodificar una restricción de seguridad (T1, NO_RUNTIME, Riesgo P0) resulta en un FAIL automático del test de densidad.

## Baseline (Texto Humano)
*   Documento de referencia: `01_input_long_context.md` (Vigilia Sincrónica).
*   Bytes: ~2,658
*   Tokens: ~650

## Presupuestos por Etapa

| Stage | Formato | Target Bytes | Target Tokens | Ratio (vs Baseline) |
| :--- | :--- | :--- | :--- | :--- |
| Stage 0 | JSON Hint | ~4,100 | ~900 | > 1.0x (Peor) |
| Stage 1 | JSON No-Hint | ~1,500 | ~400 | ~ 0.6x |
| Stage 2 | Compact Symbolic | ~500 | ~150 | ~ 0.2x |
| Stage 3 | Binary/Hex | ~200 | ~80 | ~ 0.08x |

El objetivo de este sprint (Stage 1) es reducir el tamaño del payload eliminando el lenguaje natural, acercándonos por primera vez a una densidad positiva (ratio < 1.0x) sin perder la equivalencia funcional.
