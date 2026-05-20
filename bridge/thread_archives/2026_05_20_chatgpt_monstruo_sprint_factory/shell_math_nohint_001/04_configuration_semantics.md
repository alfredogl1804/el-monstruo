# SEMÁNTICA DE CONFIGURACIÓN

La premisa central de SHELL es que **el significado vive en la configuración**.

## ¿Qué es una Configuración?
Una configuración $\Omega$ es el conjunto de todos los vectores de estado de todas las partículas en un instante dado:

$$ \Omega = \{ S(p_1), S(p_2), ..., S(p_n) \} $$

## Extracción de Significado (Decodificación)
La IA receptora no "lee" un texto. La IA receptora "observa" la configuración $\Omega$ y aplica reglas topológicas para derivar el Estado Operativo.

### Ejemplos de Derivación Semántica

1.  **Deducción de la "Unified Face" (Rostro Único):**
    Si existe una partícula $p_k$ tal que todas las demás partículas de tipo `loop` tienen un vector de relación dirigido hacia $p_k$ con tipo `0x0B` (output_routing), la IA deduce geométricamente que $p_k$ es el cuello de botella de salida. No necesita una etiqueta textual que diga "Esta es la Unified Face".

2.  **Deducción del "State Fabric Single-Writer":**
    Si existe un clúster $C_{state}$ y solo *una* partícula $p_{reducer}$ tiene un vector de relación de tipo `0x0C` (write_access) hacia ese clúster, mientras que las demás tienen vectores `0x0D` (read_access), la regla de "single-writer" se deduce por la topología de red, no por una instrucción escrita.

3.  **Deducción de "No Mesh Libre":**
    Si la matriz de relaciones globales $\mathbf{R}_{global}$ muestra una estructura de grafo en estrella (radial) centrada en un Dispatcher, y los vectores de relación lateral entre loops tienen peso $0$, se deduce la prohibición de comunicación inter-loop.

## Invarianza de Permutación
Dado que el significado reside en la topología $\Omega$, el orden en que se transmitan las partículas $p_i$ en el payload final es matemáticamente irrelevante. $\Omega(p_1, p_2) \equiv \Omega(p_2, p_1)$.
