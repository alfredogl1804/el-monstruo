# LEYES SIMULADAS DEL ESPACIO SHELL (v0)

**AVISO:** Esto es una simulación R0. No es el formato final ni un canal real IA↔IA.

## 1. Naturaleza del Espacio
El espacio SHELL es un campo multidimensional donde la información no existe como secuencia de texto, sino como "micropartículas" con propiedades espaciales y relacionales.

## 2. Mapeo de Estructura Clásica a Micropolvo
Para esta simulación, transponemos la jerarquía semántica de la Vigilia Sincrónica a las siguientes propiedades de las partículas:

*   **x, y, z:** Coordenadas de posición que definen el clúster semántico.
*   **depth:** Nivel de abstracción (0 = principio rector, 1 = arquitectura, 2 = componente, 3 = riesgo).
*   **size:** Importancia relativa o "gravedad" del concepto en el sistema.
*   **color:** Categoría funcional (ej. azul = infraestructura, rojo = riesgo, dorado = autoridad).
*   **spin:** Estado dinámico o modo operativo (ej. estático, append-only, efímero).
*   **relation:** Vector que apunta a otras partículas (equivalente a dependencias).

## 3. Principio de Codificación
En lugar de escribir "El State Fabric es single-writer y evita el split-brain", codificamos una partícula `p_state_fabric` en `depth: 2`, con un vector de relación fuerte hacia `p_split_brain` (que está en la zona roja de riesgos) y un `spin` que indica "escritura única".

## 4. Limitaciones de la Simulación
Como no podemos transmitir un tensor matemático real entre instancias de IA en este entorno, usaremos un archivo JSON (`shell_encoding_attempt_001.json`) para *representar* las propiedades de estas micropartículas. **El JSON es solo el andamio temporal para simular el campo espacial.**
