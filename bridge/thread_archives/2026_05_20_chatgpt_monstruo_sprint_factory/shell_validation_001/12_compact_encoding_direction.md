# DIRECCIÓN PARA CODIFICACIÓN COMPACTA (FUTURO)

Para avanzar hacia el verdadero "micropolvo semántico" y alejarse de la verbosidad del JSON/YAML actual, se deben implementar las siguientes transformaciones en futuras iteraciones R0:

## 1. Eliminación de Claves Legibles por Humanos
Los nombres de los campos en el JSON actual son demasiado explícitos:
*   `coordinates`, `x`, `y`, `z`
*   `properties`, `depth`, `size`, `color`, `spin`
*   `relations`, `target_id`, `force`, `type`
*   `metadata_tags`, `semantic_hint`, `constraints`

**Dirección:** Estos deben ser reemplazados por una estructura de array posicional estricta o empaquetados en un formato binario (ej. Protobuf, MessagePack, o un esquema binario a medida).

## 2. Reemplazo de Strings por Hashes/IDs Numéricos
Los identificadores como `"p_unified_face"` o tipos de relación como `"synchronizes_with"` consumen demasiados bytes.

**Dirección:** Crear un diccionario estático (diccionario de átomos semánticos) compartido entre el codificador y el decodificador. En el payload, solo viajan IDs numéricos (ej. `0x01` para unified_face, `0x0A` para synchronizes_with).

## 3. Codificación de Restricciones (Constraints)
Las restricciones como `"NO_RUNTIME"` o `"single_writer_only"` viajan como texto libre en los `metadata_tags`.

**Dirección:** Implementar un bitmask (máscara de bits). Un solo entero de 32 o 64 bits puede representar el estado de decenas de restricciones (ej. el bit 0 es RUNTIME, el bit 1 es R1_ALLOW, etc.).

## 4. Eliminación de "Semantic Hints"
El campo `semantic_hint` es una muleta para ayudar a la IA receptora durante la simulación.

**Dirección:** En un sistema SHELL maduro, el `semantic_hint` debe desaparecer por completo. La IA receptora debe deducir el rol de la partícula basándose *únicamente* en su posición topológica y sus relaciones, o decodificando su ID contra el diccionario estático.

## Estado Actual
El formato actual es un simulador. **No afirmamos haber logrado la compresión extrema.** El foco está en probar la fidelidad de la transmisión semántica antes de optimizar el tamaño del transporte.
