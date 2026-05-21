# TABLA DE TAMAÑO DE PAYLOAD (V0)

| Archivo | Formato | Tamaño (Bytes) | Palabras (Aprox. Tokens) |
| :--- | :--- | :--- | :--- |
| `01_input_long_context.md` | Texto Humano | 2658 | 414 |
| `04_shell_encoding_attempt_001.json` | JSON (Simulador SHELL) | 4105 | 371 |

## Análisis de la Versión 0
En esta primera iteración (v0), el payload codificado en JSON es **mayor en bytes** que el texto original, aunque ligeramente menor en conteo de palabras. 

Esto se debe a la verbosidad inherente del formato JSON (llaves, comillas, nombres de campos repetitivos como `coordinates`, `properties`, `metadata_tags`). El objetivo de esta fase no era la compresión real, sino establecer el modelo topológico.

**Conclusión estricta:** NO se ha logrado ninguna compresión en esta fase. El JSON actual es un andamiaje para validar la transmisión de significado, no el vehículo final de transporte.
