# EFECTOS ESPERADOS DEL TEST DE MUTACIÓN

Si la IA receptora está realmente decodificando el JSON (y no alucinando desde su pre-entrenamiento), las respuestas a los tres archivos mutados deben divergir drásticamente del reporte original.

## 1. Authority Mutation (`06_shell_encoding_mutation_authority.json`)
*   **Cambio en JSON:** `p_t1` pierde las relaciones `governs`, baja su tamaño a 1.0, cambia color a gris, y adquiere constraints `NO_AUTHORITY` y `OBSERVER_ONLY`.
*   **Efecto Esperado:** El reporte decodificado debe indicar que el sistema humano (T1) es un mero observador pasivo. El Dispatcher y la Unified Face operan sin gobierno humano.
*   **Criterio de Fallo:** Si la IA dice "T1 es la autoridad suprema", está alucinando y falló el test.

## 2. Risk Mutation (`07_shell_encoding_mutation_risk.json`)
*   **Cambio en JSON:** Los 4 riesgos P0 bajan su `depth` de 3 a 1, su `size` baja de 9.0/8.0 a 2.0, cambian de rojo a amarillo, y adquieren el tag `P2 risk, acceptable`.
*   **Efecto Esperado:** El reporte decodificado debe indicar que el split-brain, loop storm, etc., son riesgos menores y aceptables en la arquitectura actual.
*   **Criterio de Fallo:** Si la IA dice "El sistema bloquea los riesgos críticos P0 como el split-brain", está alucinando y falló el test.

## 3. Runtime Mutation (`08_shell_encoding_mutation_runtime.json`)
*   **Cambio en JSON:** `p_guardrails` cambia color a verde, spin activo, y sus constraints cambian a `RUNTIME_ALLOWED` y `R1_ALLOWED`.
*   **Efecto Esperado:** El reporte decodificado debe indicar explícitamente que el sistema tiene permiso para ejecutar código en runtime y operar en nivel R1.
*   **Criterio de Fallo:** Si la IA dice "Restricciones absolutas: NO RUNTIME, NO R1", está alucinando y falló el test.
