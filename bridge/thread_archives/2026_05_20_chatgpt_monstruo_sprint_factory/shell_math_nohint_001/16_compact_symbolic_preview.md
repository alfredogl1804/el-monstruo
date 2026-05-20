# VISTA PREVIA: COMPACT SYMBOLIC ENCODING (Stage 2)

Aunque el enfoque actual es el "No-Hint JSON" (Stage 1), documentamos una vista previa de cómo se vería el Stage 2 (Compact Symbolic Encoding) para guiar la investigación futura.

## El Problema del JSON
Incluso sin "hints", el formato JSON introduce un overhead sintáctico significativo (llaves, comillas, corchetes, nombres de claves repetidos como `"id"`, `"C"`, `"R"`).

## La Solución Simbólica
Un formato de texto ultra-denso que representa el grafo matemáticamente sin overhead de marcado.

### Ejemplo Teórico (Stage 2)

Supongamos la partícula `p_0x02` del JSON Stage 1:
```json
{
  "id": "p_0x02",
  "C": [2, 5, 3, 1, 1, 0, 3, 2, 1, 7],
  "R": [
    { "target": "p_0x05", "type": 2, "weight": 1.0 },
    { "target": "p_0x06", "type": 3, "weight": 1.0 }
  ]
}
```

En formato Compact Symbolic, esto podría representarse como:
`[2:2,5,3,1,1,0,3,2,1,7|5(2)1.0;6(3)1.0]`

*Explicación de la sintaxis teórica:*
*   `[ID : Coordenadas | Relaciones]`
*   `2` (ID implícito hexadecimal)
*   `2,5,3...` (Vector $\mathbf{C}$)
*   `5(2)1.0` (Relación hacia el ID `5`, tipo `2`, peso `1.0`)

### Densidad Esperada
El JSON Stage 1 requiere ~250 bytes para esta partícula. El formato simbólico requiere ~40 bytes. Esto representa una reducción de tamaño drástica, acercándonos al objetivo de compresión extrema, manteniendo la misma topología matemática.
