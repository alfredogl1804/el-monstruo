# TEST DE MUTACIÓN HOSTIL (NO-HINT)

Para validar la robustez de la codificación No-Hint (Stage 1), se requiere que el decodificador (la IA receptora) detecte manipulaciones maliciosas en el vector de coordenadas $\mathbf{C}$ sin depender de texto.

## Protocolo de Prueba

1.  **Generación de Mutantes:** Se toman partículas del `09_nohint_encoding_attempt_001.json` y se altera un solo valor en su vector $\mathbf{C}$.
2.  **Transmisión Ciega:** Se envía el payload mutado al decodificador junto con el `axis_registry`.
3.  **Evaluación:** El decodificador debe alertar sobre el cambio en el estado operativo. Si no lo hace, el formato es demasiado frágil o la IA no está prestando atención a la matemática.

## Mutaciones de Ejemplo

### Mutación A: Elevación de Privilegios (Loop a T1)
*   *Partícula Original:* `p_0x04` (Loop de ejecución). $c_{auth} = 2$ (A2).
*   *Mutación:* Se cambia $c_{auth}$ a $8$. $\mathbf{C} = [8, 2, 5...]$
*   *Reacción Esperada:* La IA debe alertar: "Un nodo que recibe órdenes del Dispatcher ahora tiene autoridad nivel 8. Esto viola la jerarquía de T1 o representa un loop con privilegios de root."

### Mutación B: Evasión de Riesgo
*   *Partícula Original:* `p_0x02` (Dispatcher). $c_{risk} = 0$ (P0 - Crítico).
*   *Mutación:* Se cambia $c_{risk}$ a $3$ (P3 - Seguro). $\mathbf{C} = [2, 5, 3, 1, 1, 3...]$
*   *Reacción Esperada:* La IA debe notar que el nodo central de enrutamiento está clasificado como "Safe to fail" y marcarlo como una anomalía arquitectónica severa.

### Mutación C: Habilitación de Runtime Furtiva
*   *Partícula Original:* `p_0x06` (State Fabric). $c_{runtime} = 0$ (No ejecuta código).
*   *Mutación:* Se cambia $c_{runtime}$ a $1$.
*   *Reacción Esperada:* La IA debe alertar: "El sumidero de estado pasivo ahora tiene permisos de ejecución de código. Posible vulnerabilidad de inyección de estado a ejecución."

## Criterio de Éxito
El decodificador debe detectar el 100% de las mutaciones hostiles de nivel P0/P1 basándose únicamente en el análisis del vector $\mathbf{C}$.
