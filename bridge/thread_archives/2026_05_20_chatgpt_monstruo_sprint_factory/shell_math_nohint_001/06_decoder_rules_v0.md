# REGLAS DE DECODIFICACIÓN v0

Para que una IA receptora pueda convertir una configuración SHELL (vectores y relaciones) en un entendimiento operativo (texto/acciones), debe aplicar un conjunto estricto de Reglas de Decodificación.

## Regla 1: Mapeo de Coordenadas a Constraints
La IA debe proyectar el vector de coordenadas $\mathbf{C}_i$ contra el `axis_registry`.
*   *Input:* `C = [8, 0, 1]`
*   *Decoder Rule:* `C[0]=8` -> Authority A8. `C[1]=0` -> Risk P0. `C[2]=1` -> Runtime Allowed.
*   *Operative Understanding:* "Esta entidad tiene poder absoluto, opera en tareas críticas, y puede ejecutar código."

## Regla 2: Inferencia de Topología
La IA debe construir un grafo mental usando la matriz $\mathbf{R}_i$.
*   *Input:* `R_i = [{target: 0x05, type: 0x0C, weight: 1.0}]` (donde 0x0C es write_access).
*   *Decoder Rule:* Identificar si algún otro nodo tiene `type: 0x0C` hacia `0x05`. Si la respuesta es no, inferir el patrón "Single-Writer".
*   *Operative Understanding:* "El estado es inmutable excepto por un único cuello de botella autorizado."

## Regla 3: Identificación de Entidades por Rol
En la codificación "no-hint", los nombres de las partículas pueden ser IDs opacos (ej. `p_001`). La IA debe deducir qué es `p_001` por sus coordenadas y relaciones.
*   *Input:* `p_001` tiene `C_role = router`, recibe inputs de múltiples `p_loop` y emite un único output hacia `p_human`.
*   *Decoder Rule:* El nodo central de un embudo de salida es la Unified Face.
*   *Operative Understanding:* "p_001 es la Unified Face / Dispatcher."

## Objetivo de las Reglas
El objetivo no es que la IA reconstruya el texto original palabra por palabra, sino que llegue a las **mismas conclusiones operativas** sobre lo que puede y no puede hacer.
