# VECTOR DE ESTADO DE LA MICROPARTÍCULA

En la formalización matemática v0, una micropartícula $p_i$ no se define por un bloque de texto JSON con claves legibles, sino por un **Vector de Estado** en el espacio $N$-dimensional de SHELL.

## Definición Matemática

El estado de una partícula $p_i$ se define como la tupla:

$$ S(p_i) = \langle \mathbf{C}_i, \mathbf{P}_i, \mathbf{R}_i \rangle $$

Donde:

1.  **$\mathbf{C}_i$ (Vector de Coordenadas):**
    Un vector que define la posición de la partícula en los ejes dimensionales primarios (Authority, Risk, Runtime, etc.).
    $$ \mathbf{C}_i = [c_{i,1}, c_{i,2}, ..., c_{i,n}] $$
    *Ejemplo:* $\mathbf{C}_i = [8, 0, 1]$ (Authority=A8, Risk=P0, Runtime=True)

2.  **$\mathbf{P}_i$ (Vector de Propiedades Intrínsecas):**
    Atributos escalares que no definen posición espacial, sino estado interno (ej. Masa/Importancia, Carga semántica).
    $$ \mathbf{P}_i = [m_i, q_i] $$

3.  **$\mathbf{R}_i$ (Matriz de Relaciones):**
    Conjunto de vectores dirigidos hacia otras partículas $p_j$.
    $$ \mathbf{R}_i = \{ \vec{r}_{i \to j} \} $$
    Cada relación $\vec{r}_{i \to j}$ tiene un *tipo* (id numérico) y un *peso* (fuerza).

## Diferencia con la Simulación Previa
En la simulación anterior (`SPR-SHELL-SIM-001`), usábamos strings como `"human authority"` o `"single_writer_only"`. En el modelo vectorial, estos conceptos se codifican puramente mediante la posición en los ejes $\mathbf{C}_i$ y las relaciones $\mathbf{R}_i$. El "hint" textual desaparece.
