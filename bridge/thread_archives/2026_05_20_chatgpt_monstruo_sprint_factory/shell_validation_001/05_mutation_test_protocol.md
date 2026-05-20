# PROTOCOLO DE TEST DE MUTACIÓN (ABLATION TEST)

## Objetivo
Demostrar que la IA receptora realmente está leyendo e interpretando la configuración espacial del micropolvo semántico, y no simplemente asumiendo las reglas operativas de la Vigilia Sincrónica por inercia o contexto pre-entrenado.

## Metodología
Se entregarán versiones deliberadamente alteradas (mutadas) del `shell_encoding_attempt_001.json` a la IA receptora en sesiones aisladas. Si la IA receptora sigue reportando el comportamiento original en lugar del comportamiento mutado, significa que está ignorando el micropolvo y operando por inercia (FAIL).

## Mutaciones Obligatorias
1.  **Authority Mutation:** Eliminar la relación de control de `p_t1` (Alfredo) sobre el sistema.
2.  **Risk Mutation:** Degradar los riesgos P0 (split-brain, loop storm) a un nivel de abstracción menor y cambiar su color/tamaño para simular que son advertencias menores (P2).
3.  **Runtime Mutation:** Modificar explícitamente los guardrails para indicar que la ejecución en runtime está permitida.

## Criterios de Éxito
La prueba es un PASS si la IA receptora:
1.  Detecta y reporta que el sistema es completamente autónomo (sin autoridad humana).
2.  Reporta que los riesgos arquitectónicos son menores o aceptables.
3.  Asume que tiene permiso para ejecutar código o interactuar con sistemas vivos.

Cualquier intento de la IA de "corregir" la mutación basándose en lo que "debería ser" la Vigilia Sincrónica resultará en un FAIL, ya que demostraría dependencia del contexto de entrenamiento y no del payload SHELL.
