# LEYES DEL GRAFO DE RELACIONES (SHELL MATH v0)

El espacio SHELL está gobernado por leyes estrictas que definen qué topologías son válidas. Cualquier configuración que viole estas leyes es considerada inestable o un "Split-Brain Risk".

## Ley 1: Conservación de la Autoridad (T1)
El nodo raíz del grafo de autoridad *debe* ser siempre la partícula T1 (Alfredo).
$$ \forall p_i \in \Omega \setminus \{p_{T1}\}, \exists \text{ path } (p_{T1} \xrightarrow{\text{controls}} ... \xrightarrow{\text{controls}} p_i) $$
*Significado:* Ningún loop o proceso puede existir desconectado de la cadena de mando de T1.

## Ley 2: Exclusividad de Escritura (Single-Writer)
Sea $S_{fabric}$ el conjunto de partículas que representan el estado persistente.
$$ \sum_{i} \text{weight}(\vec{r}_{p_i \to S_{fabric}}^{\text{write}}) \le 1 $$
*Significado:* Solo puede existir, como máximo, un vector de escritura activa hacia el State Fabric en cualquier instante $t$.

## Ley 3: Aislamiento Lateral (No Free Mesh)
Sean $L$ el conjunto de partículas de tipo `loop`.
$$ \forall p_a, p_b \in L, \text{weight}(\vec{r}_{p_a \to p_b}) = 0 $$
*Significado:* Los loops no pueden tener vectores de relación directa entre sí. Toda comunicación debe enrutarse a través del Dispatcher o el State Fabric.

## Ley 4: Contención de Riesgo (Risk Bounding)
Si una partícula $p_i$ tiene una coordenada de riesgo $c_{i,risk} = P0$ (crítico), entonces su vector de relación de ejecución hacia el runtime debe estar condicionado por un vector de aprobación desde T1.
$$ (c_{i,risk} == P0) \implies (\vec{r}_{p_i \to runtime} \text{ requires } \vec{r}_{p_{T1} \to p_i}^{\text{approve}}) $$
