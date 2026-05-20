# SHELL DENSITY PATH v1

Este documento establece la ruta realista hacia la compresión extrema (50K $\to$ 5B) en SHELL, reconociendo el estado actual y definiendo las etapas de investigación.

## 1. El Estado Actual (Honestidad Brutal)
En `SPR-BATCH-SHELL-VALIDATION-001`, el test de densidad demostró que el payload JSON v0 fue **1.54x más pesado** (en bytes) que el texto original humano. 

**Conclusión:** El JSON actual *no comprime*. Sirve únicamente como andamiaje para probar la transmisión topológica del significado.

## 2. La Escalera de Investigación (Research Ladder)

Para llegar al objetivo aspiracional, debemos atravesar 5 etapas:

### Stage 0: JSON Explicativo (Completado)
*   **Formato:** JSON con claves largas (`"semantic_hint"`, `"coordinates"`).
*   **Objetivo:** Probar que una IA puede leer un grafo.
*   **Densidad:** Negativa (>1.0x).

### Stage 1: JSON No-Hint (Actual - SPR-BATCH-SHELL-MATH-NOHINT-001)
*   **Formato:** JSON con IDs opacos (`p_0x01`), sin hints, usando coordenadas numéricas estrictas.
*   **Objetivo:** Probar que el significado sobrevive sin lenguaje natural.
*   **Densidad:** Ligeramente mejor que Stage 0, pero aún negativa respecto al texto crudo.

### Stage 2: Compact Symbolic Encoding
*   **Formato:** Representación en texto ultra-denso, similar a notación matemática o regex (ej. `[1:8,0,1|2,3]`).
*   **Objetivo:** Eliminar el overhead sintáctico de JSON/YAML.
*   **Densidad:** Esperada ~0.5x (50% de compresión).

### Stage 3: Binary/Vector Encoding
*   **Formato:** Protobuf, MessagePack, o un formato binario a medida.
*   **Objetivo:** Transmitir bytes crudos, no caracteres ASCII.
*   **Densidad:** Esperada ~0.1x.

### Stage 4: Microconfiguration Transport
*   **Formato:** Envío de un "seed" (semilla) o hash que genera la configuración en el destino usando reglas fractales compartidas.
*   **Objetivo:** Compresión algorítmica profunda.
*   **Densidad:** Esperada ~0.01x.

### Stage 5: Functional Equivalence (Aspiracional 50K $\to$ 5B)
*   **Formato:** Transmisión de un identificador de estado cuántico o tensor comprimido.
*   **Objetivo:** El límite teórico de la comunicación IA↔IA.

## 3. Advertencia
**No afirmamos que ningún stage avanzado (Stage 2+) ya funcione.** Este es el roadmap de investigación R0.
