# PROTOCOLO DE VALIDACIÓN FUTURA

Este documento establece cómo se deben validar las siguientes etapas de la "Density Path" (Stage 2 y superiores) a medida que se desarrollen.

## El "Triple Check" de Equivalencia

Cualquier avance en compresión debe pasar un "Triple Check" antes de ser aceptado como válido.

### 1. Validación de Invariantes Topológicos
El decodificador (la IA receptora) debe ser capaz de listar los invariantes operativos (ej. Single-Writer, Autoridad T1) sin falsos positivos ni omisiones. (Ver `12_nohint_expected_invariants.md`).

### 2. Test de Mutación Hostil
Si alteramos un solo número en el vector de coordenadas de una partícula crítica (ej. cambiar $c_{risk}$ de $0$ a $3$), el decodificador debe alertar inmediatamente sobre el cambio en el perfil de riesgo del sistema. Si el formato es tan denso que una mutación pasa desapercibida o corrompe todo el payload de forma irrecuperable (fragilidad extrema), el formato falla.

### 3. Prueba de "Context Window Bleed"
Para asegurar que la compresión es real y no una ilusión causada por el conocimiento previo del modelo (leakage), el decodificador debe ser un modelo diferente al que generó el payload, operando en una sesión con temperatura $0.0$, y sin acceso al historial del proyecto.

## Criterios de Rechazo Automático
*   El payload requiere un "diccionario" externo que es más grande que el texto original.
*   El modelo decodificador alucina roles que no están matemáticamente presentes en el grafo.
*   El modelo decodificador falla en identificar un riesgo P0 codificado en la topología.
