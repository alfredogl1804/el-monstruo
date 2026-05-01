# Biblia de Implementación: Agent-S v0.3.2 Simular AI architecture technical details GUI agent

**Fecha de Lanzamiento:** Mayo 01, 2026
**Versión:** v0.3.2
**Arquitectura Principal:** Framework Modular, Planificación Jerárquica Proactiva, Grounding Visual, Interfaz Agente-Computadora (ACI) con Módulos Expertos, Mecanismo de Memoria Agéntica.

## 1. Visión General y Diferenciador Único

**Agent S** es un framework de código abierto diseñado para permitir la interacción autónoma con computadoras a través de interfaces gráficas de usuario (GUI). Su misión es construir agentes GUI inteligentes capaces de aprender de experiencias pasadas y realizar tareas complejas de forma autónoma en un entorno informático. El framework ha demostrado la capacidad de superar el rendimiento humano en benchmarks como OSWorld con su versión S3, alcanzando un 72.60% de precisión [1].

El diferenciador único de Agent S radica en su **arquitectura modular** que orquesta diversos modelos (fundacionales y especializados) en lugar de depender de un sistema monolítico. Esta modularidad, combinada con una **planificación jerárquica proactiva**, un **grounding visual** avanzado y un **mecanismo de memoria agéntica**, le permite interactuar con las computadoras de una manera similar a la humana, adaptándose y mejorando continuamente [2].

## 2. Arquitectura Técnica

La arquitectura de Agent S2 (la segunda generación del framework) se basa en cuatro principios de diseño clave que le otorgan modularidad, escalabilidad y un rendimiento superior [2]:

*   **Planificación Jerárquica Proactiva:** Agent S2 combina modelos especializados para la ejecución de bajo nivel (ej. selección de elementos de UI) con modelos generalizados para la planificación de alto nivel. A diferencia de la planificación reactiva, Agent S2 actualiza dinámicamente sus planes después de cada subtarea, mejorando la adaptabilidad, la continuidad y la optimización de los pasos futuros [2].

*   **Grounding Visual para Interacción Precisa:** Agent S2 opera exclusivamente con **capturas de pantalla en bruto** como entrada, eliminando la necesidad de árboles de accesibilidad. Delega la comprensión visual a modelos de grounding especializados (como UI-TARS), lo que le permite localizar y manipular con precisión elementos de la UI como botones, texto e imágenes [2].

*   **Interfaz Agente-Computadora (ACI) con Módulos Expertos:** Para reducir la carga cognitiva de los modelos fundacionales, Agent S2 descarga tareas complejas de bajo nivel (ej. resaltado de texto) a **módulos expertos especializados**. Esto permite que los modelos fundacionales se centren en la planificación de alto nivel y la toma de decisiones estratégicas [2].

*   **Mecanismo de Memoria Agéntica:** El framework incorpora un mecanismo de memoria de aprendizaje continuo. La experiencia de tareas completadas previamente se retiene, permitiendo a Agent S2 recordar acciones anteriores y refinar estrategias futuras basándose en éxitos y fracasos históricos. Esta capacidad de aprendizaje adaptativo mejora la eficiencia y la competencia del agente con el tiempo [2].

## 3. Implementación/Patrones Clave

La implementación de Agent S se centra en la flexibilidad y la capacidad de integración con diversos modelos de IA:

*   **Instalación:** Se puede instalar fácilmente a través de `pip` con `pip install gui-agents` [1].

*   **Configuración de API:** Las claves de API para los modelos principales (ej. OpenAI, Anthropic) y los modelos de grounding se configuran mediante variables de entorno (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `HF_TOKEN`) o directamente en un script de Python [1].

*   **Modelos Soportados:** Agent S es compatible con una variedad de proveedores de modelos de generación, incluyendo Azure OpenAI, Anthropic, Gemini, Open Router y vLLM [1].

*   **Modelos de Grounding:** Para un rendimiento óptimo, se recomienda el uso de modelos como UI-TARS-1.5-7B (con `--grounding_width 1920 --grounding_height 1080`) o UI-TARS-72B (con `--grounding_width 1000 --grounding_height 1000`), alojados en endpoints de inferencia [1].

*   **Uso de CLI:** El agente se ejecuta a través de la línea de comandos, especificando el proveedor y el modelo principal, así como el proveedor, la URL, el modelo y las dimensiones del modelo de grounding. Por ejemplo:

    ```bash
    agent_s \
        --provider openai \
        --model gpt-5-2025-08-07 \
        --ground_provider huggingface \
        --ground_url http://localhost:8080 \
        --ground_model ui-tars-1.5-7b \
        --grounding_width 1920 \
        --grounding_height 1080
    ```
    [1]

*   **Entorno de Codificación Local:** Agent S3 puede habilitar un entorno de codificación local (`--enable_local_env`) para ejecutar código Python y Bash directamente en la máquina del usuario. Esto es útil para tareas que requieren manipulación de datos, operaciones de archivos, automatización del sistema o desarrollo de código, permitiendo al agente usar la acción `call_code_agent` [1].

*   **SDK:** El framework proporciona clases como `AgentS3` y `OSWorldACI` dentro del paquete `gui_agents.s3.agents` para la construcción y control programático del agente [1].

## 4. Lecciones para el Monstruo

La arquitectura de Agent S ofrece varias lecciones valiosas para el desarrollo de nuestro propio agente:

*   **Priorizar la Modularidad:** Adoptar un diseño modular permite una mayor flexibilidad, escalabilidad y la capacidad de integrar y cambiar componentes (modelos fundacionales, modelos expertos) según sea necesario. Esto reduce la dependencia de un único modelo y permite aprovechar las fortalezas de diferentes soluciones de IA [2].

*   **Implementar Planificación Proactiva:** La estrategia de actualizar dinámicamente los planes después de cada subtarea, en lugar de solo reaccionar a los errores, es crucial para mejorar la adaptabilidad y la eficiencia en tareas complejas. Esto minimiza los pasos de retroceso y optimiza la trayectoria general [2].

*   **Aprovechar el Grounding Visual Directo:** La capacidad de operar directamente sobre capturas de pantalla sin depender de árboles de accesibilidad es un avance significativo. Nuestro agente podría beneficiarse de modelos de grounding visual especializados para una interacción más precisa y robusta con cualquier GUI, independientemente de su estructura interna [2].

*   **Delegar Tareas de Bajo Nivel:** Offload tareas complejas y de bajo nivel a módulos expertos dedicados puede reducir la carga cognitiva de los modelos de lenguaje grandes (LLMs) principales, permitiéndoles enfocarse en el razonamiento de alto nivel y la toma de decisiones estratégicas [2].

*   **Desarrollar un Mecanismo de Memoria Robusto:** La implementación de un sistema de memoria que permita el aprendizaje continuo y la adaptación basada en experiencias pasadas es fundamental. Esto no solo mejora el rendimiento del agente con el tiempo, sino que también facilita la personalización y la automatización a largo plazo [2].

---
*Referencias:*
[1] [GitHub - simular-ai/Agent-S: Agent S: an open agentic framework that uses computers like a human](https://github.com/simular-ai/agent-s)
[2] [Agent S2 - Open, Modular, and Scalable Framework for Computer Use Agents | Simular AI](https://www.simular.ai/articles/agent-s2)


---

# Biblia de Implementación: Agent-S v0.3.2 (Simular AI) — Fase 2

## Introducción

Agent-S v0.3.2, desarrollado por Simular AI, representa un avance significativo en el campo de los agentes de interfaz gráfica de usuario (GUI) capaces de interactuar con computadoras de manera autónoma. Este agente ha demostrado un rendimiento superior al humano en benchmarks clave como OSWorld, lo que lo posiciona como una solución de vanguardia para la automatización de tareas digitales complejas. La presente "Biblia de Implementación - Fase 2" tiene como objetivo proporcionar una investigación profunda y detallada sobre la arquitectura, el funcionamiento interno y las capacidades técnicas de Agent-S v0.3.2, cubriendo doce módulos específicos para ofrecer una comprensión exhaustiva de su diseño y operación.

La investigación se basa en artículos técnicos, papers de investigación, repositorios de código abierto y discusiones relevantes publicadas en los últimos meses, asegurando la inclusión de la información más actualizada y pertinente. Se busca ir más allá de las descripciones de marketing para desglosar los componentes técnicos que permiten a Agent-S lograr sus impresionantes resultados, desde su ciclo de agente y sistema de herramientas hasta su gestión de memoria, capacidades multimodales y rendimiento en benchmarks.

El objetivo final es ofrecer una guía técnica completa que sirva como referencia para comprender, implementar y potencialmente mejorar agentes de IA con capacidades similares, extrayendo lecciones valiosas de la ingeniería y el diseño de Agent-S v0.3.2.

## MÓDULO A: Ciclo del agente (loop/ReAct)

Agent S opera bajo un marco de **Agente-Computadora Interfaz (ACI)**, diseñado para la interacción autónoma con computadoras [1]. Su ciclo de operación se puede enmarcar como un **Proceso de Decisión de Markov Parcialmente Observable (POMDP)**, definido como M = ⟨S, O, A, T, I, R⟩ [3]:

*   **S (Espacio de Estados)**: Codifica el estado de la computadora. Este espacio abarca todos los elementos visuales y de sistema que el agente puede observar y manipular, formando una representación integral del entorno operativo en un momento dado.
*   **O (Espacio de Observaciones)**: Incluye capturas de pantalla del escritorio (`desktop screenshots`) [3]. Estas observaciones visuales son la principal fuente de información sensorial del agente, permitiéndole percibir el estado actual de la interfaz gráfica de usuario (GUI) y los cambios que ocurren en ella.
*   **A (Espacio de Acciones)**: Contiene acciones del agente como `agent.click(...)` y `agent.type(...)` [3]. Estas son las primitivas de interacción que el agente utiliza para manipular el entorno, simulando las acciones de un usuario humano. La granularidad de estas acciones es crucial para la precisión en la interacción GUI.
*   **T (Función de Transición)**: Una función estocástica T : S × A → ∆(S) que describe cómo el estado de la computadora cambia después de una acción [3]. Esta función modela la dinámica del entorno, prediciendo el próximo estado del sistema dada una acción específica del agente. La naturaleza estocástica reconoce la imprevisibilidad inherente de los sistemas complejos.
*   **I (Instrucciones)**: El espacio de posibles instrucciones de usuario representadas en lenguaje natural [3]. Estas instrucciones son el objetivo de alto nivel que el agente debe lograr, y su interpretación precisa es fundamental para la planificación y ejecución de tareas.
*   **R (Función de Recompensa)**: R : (S × A)∗ × I → [0, 1] asigna una recompensa escalar a una trayectoria de estados y acciones (τ) en la tarea I [3]. Esta función proporciona la señal de aprendizaje para el agente, indicando qué tan bien ha logrado el objetivo de la instrucción. Una recompensa más alta significa un mejor desempeño.

El agente mantiene un historial ordenado por tiempo de todas las observaciones y acciones consecutivas (`ht := (o0, a0, ..., ot−1, at−1, ot)`) [3]. Este historial es una forma de memoria a corto plazo que permite al agente contextualizar sus decisiones actuales basándose en interacciones pasadas. Es esencial para tareas de largo horizonte donde la secuencia de acciones es crítica.

Agent S utiliza un enfoque híbrido que combina un **agente GUI** (interacción visual) y un **agente de código** [3]. El agente principal (GUI) interactúa con el entorno, y puede delegar tareas al agente de código mediante la acción `call_code_agent` [1]. Esta delegación es un mecanismo clave para manejar la diversidad de tareas: las interacciones visuales se manejan directamente, mientras que las tareas programáticas se externalizan a un componente especializado.

El agente de código, a su vez, opera en un bucle interno acotado con un presupuesto de pasos (`B`), iterando sobre el código generado y la retroalimentación del terminal. En cada paso interno, el agente de codificación se basa en la retroalimentación (`ccode`, que incluye estado, código de retorno, stdout/stderr) de iteraciones anteriores. Puede emitir código Python/Bash para ser ejecutado en una VM aislada o devolver un token de control [3]. La elección entre el agente GUI y el agente de código se realiza en función de la tarea [3]. Esta arquitectura modular permite a Agent S explotar las fortalezas de ambos paradigmas: la flexibilidad de la interacción GUI y la precisión y eficiencia de la ejecución de código.

Este ciclo permite a Agent S abordar tareas complejas que requieren tanto interacción visual como ejecución programática, adaptándose dinámicamente a los requisitos de la tarea. La integración de la reflexión (`enable_reflection`) [1] añade una capa adicional de inteligencia, permitiendo al agente evaluar y ajustar su plan, lo que mejora la robustez y la capacidad de recuperación ante errores.

## MÓDULO B: Estados del agente

El **estado del agente** en Agent S se define principalmente por el **espacio de estados (S)**, que codifica el estado de la computadora [3]. Esto incluye todos los elementos visuales y de sistema que el agente puede observar y manipular. Las **observaciones (O)**, como las capturas de pantalla del escritorio (`desktop screenshots`), son fundamentales para que el agente perciba su estado actual [3]. La riqueza de estas observaciones visuales es crucial para la capacidad del agente de comprender el contexto operativo y los elementos interactivos disponibles.

Las transiciones entre estados ocurren a través de las acciones del agente. El agente mantiene un **historial (`ht`)** de observaciones y acciones consecutivas, lo que le permite recordar el camino recorrido y el estado previo del sistema [3]. Este historial es una representación secuencial de los estados visitados y las acciones tomadas, formando una cadena de eventos que el agente puede consultar para la toma de decisiones futuras o para la reflexión.

Aunque el documento no detalla explícitamente una máquina de estados finitos con estados discretos predefinidos, la naturaleza de su operación como un POMDP implica que el agente transiciona entre estados basándose en sus observaciones y las acciones ejecutadas. Cada acción del agente modifica el entorno, lo que a su vez genera una nueva observación y, por lo tanto, un nuevo estado percibido. La capacidad de **reflexión (`enable_reflection`)** [1] sugiere un mecanismo para evaluar y ajustar su plan, lo que podría implicar un cambio de estado interno o una reevaluación del estado percibido del entorno. Esta reflexión permite al agente corregir errores, refinar estrategias o adaptar su comportamiento a situaciones inesperadas, lo que es una forma sofisticada de gestión de estados internos.

Los estados pueden ser implícitamente complejos, representando la configuración completa del sistema operativo, las aplicaciones abiertas, el contenido de las ventanas, la posición del cursor, y cualquier otro elemento visual o de sistema relevante. La capacidad de Agent S para operar en diversos sistemas operativos (Linux, Mac, Windows) [1] implica que su representación de estado debe ser lo suficientemente abstracta o adaptable para manejar las diferencias entre estas plataformas.

## MÓDULO C: Sistema de herramientas

El sistema de herramientas de Agent S se compone de dos agentes principales que actúan como herramientas: un **agente GUI** y un **agente de código**, coordinados por el agente principal `AgentS3` [1, 3]. Esta dualidad permite a Agent S abordar una amplia gama de tareas, desde interacciones visuales directas hasta manipulaciones programáticas complejas.

### Herramientas de Interacción GUI

Las herramientas de interacción con la Interfaz Gráfica de Usuario (GUI) son fundamentales para que Agent S opere como un humano. Estas incluyen acciones básicas como:

*   `agent.click(...)`: Permite al agente simular un clic en un elemento de la interfaz [3]. Esta acción es crucial para interactuar con botones, enlaces, iconos y otros componentes visuales. La precisión de esta acción se basa en la capacidad del agente de *grounding* para identificar las coordenadas correctas.
*   `agent.type(...)`: Permite al agente simular la escritura de texto en campos de entrada [3]. Esta herramienta es esencial para rellenar formularios, introducir comandos o escribir documentos. La capacidad de introducir texto de manera precisa y contextual es vital para muchas tareas de automatización.

Estas acciones son ejecutadas por el agente principal `AgentS3` y son traducidas a código Python ejecutable por el agente de *grounding* `OSWorldACI` [1]. El `OSWorldACI` actúa como un puente entre las intenciones de alto nivel del agente y las operaciones de bajo nivel necesarias para manipular la GUI, utilizando bibliotecas como `pyautogui` [1].

### Herramientas de Ejecución de Código

Agent S incorpora un **entorno de codificación local (Local Coding Environment)** que le permite ejecutar código Python y Bash directamente en la máquina [1]. Esta capacidad se activa mediante el parámetro `--enable_local_env` [1]. Esta herramienta es un diferenciador clave, ya que permite al agente ir más allá de la interacción puramente visual y realizar tareas que requieren lógica programática o acceso al sistema de archivos.

Cuando se habilita, el agente puede utilizar la acción `call_code_agent` para delegar tareas que requieren programación en lugar de interacción GUI [1]. El agente de código opera en un bucle interno con un presupuesto de pasos (`B`), generando y ejecutando código Python/Bash en una máquina virtual aislada (sandboxed VM) y procesando la retroalimentación del terminal (estado, código de retorno, stdout/stderr) [3]. Esta retroalimentación es crucial para la depuración y la iteración del código generado.

Las tareas típicas para el agente de código incluyen [1]:

*   **Procesamiento de Datos**: Manipulación de hojas de cálculo, archivos CSV o bases de datos. Esto abarca desde la limpieza y transformación de datos hasta la generación de informes.
*   **Operaciones de Archivos**: Procesamiento masivo de archivos, extracción de contenido u organización de archivos. Por ejemplo, renombrar múltiples archivos, buscar patrones en documentos o comprimir directorios.
*   **Automatización del Sistema**: Cambios de configuración, configuración del sistema o scripts de automatización. Esto puede incluir la instalación de software, la modificación de variables de entorno o la gestión de servicios.
*   **Desarrollo de Código**: Escritura, edición o ejecución de archivos de código. El agente puede actuar como un desarrollador, creando o modificando scripts para resolver problemas específicos.
*   **Procesamiento de Texto**: Manipulación de documentos, edición de contenido o formato. Esto es útil para tareas como la extracción de información de PDFs, la reformateo de texto o la generación de resúmenes.

### Parámetros y Límites de las Herramientas

La configuración de las herramientas y modelos subyacentes se realiza a través de parámetros en la línea de comandos o variables de entorno [1]. Algunos parámetros clave incluyen:

*   `--provider`: Proveedor del modelo de generación principal (e.g., `openai`, `anthropic`, `gemini`, `open_router`, `vllm`) [1]. Esto permite la flexibilidad de usar diferentes LLMs para la lógica central del agente.
*   `--model`: Nombre del modelo de generación principal (e.g., `gpt-5-2025-08-07`) [1]. Especifica el modelo exacto a utilizar del proveedor seleccionado.
*   `--ground_provider`: Proveedor del modelo de *grounding* (e.g., `huggingface`) [1]. Define dónde se aloja el modelo que traduce las observaciones visuales en acciones.
*   `--ground_url`: URL del modelo de *grounding* [1]. La dirección del endpoint del modelo de *grounding*.
*   `--ground_model`: Nombre del modelo de *grounding* (e.g., `ui-tars-1.5-7b`) [1]. El modelo específico utilizado para el *grounding* visual.
*   `--grounding_width`, `--grounding_height`: Resolución de coordenadas de salida del modelo de *grounding* (e.g., `1920x1080` para UI-TARS-1.5-7B) [1]. Estos parámetros son críticos para la precisión de las interacciones GUI, asegurando que el agente pueda apuntar correctamente a los elementos de la pantalla.
*   `--max_trajectory_length`: Número máximo de turnos de imagen a mantener en la trayectoria (Default: 8) [1]. Limita la ventana de contexto visual del agente.
*   `--enable_reflection`: Habilita un agente de reflexión para asistir al agente trabajador (Default: `True`) [1]. Permite al agente evaluar y refinar sus planes.
*   `--enable_local_env`: Habilita el entorno de codificación local (Default: `False`) [1]. Controla la activación de la capacidad de ejecución de código.

Los límites de las herramientas están relacionados con la seguridad y el entorno de ejecución. El entorno de codificación local ejecuta código arbitrario con los mismos permisos que el usuario, lo que requiere precaución y uso en entornos de confianza [1]. Los scripts Bash tienen un tiempo de espera de 30 segundos para evitar procesos colgados [1]. Esta limitación es una medida de seguridad para prevenir la ejecución indefinida de scripts maliciosos o erróneos.

El `gui_agents` SDK proporciona las clases `AgentS3` y `OSWorldACI` para construir y configurar estos agentes, permitiendo una personalización de los modelos de lenguaje y *grounding* utilizados [1]. Esto facilita la adaptación de Agent S a diferentes necesidades y la integración con nuevas tecnologías de IA.

## MÓDULO D: Ejecución de código

Agent S3 incorpora un **entorno de codificación local (Local Coding Environment)** que le permite ejecutar código directamente en la máquina del usuario [1]. Esta funcionalidad es crucial para tareas que requieren manipulación de datos, operaciones de archivos, automatización del sistema o desarrollo de código [1]. La capacidad de ejecutar código programáticamente extiende significativamente el alcance de las tareas que el agente puede realizar, yendo más allá de las interacciones puramente visuales.

### Lenguajes y Entorno de Ejecución

El agente de código de Agent S3 puede ejecutar código en dos lenguajes principales [1]:

*   **Python**: Utiliza el mismo intérprete de Python que se usa para ejecutar Agent S3 (detectado automáticamente). Esto asegura la compatibilidad y la facilidad de integración con el resto del sistema del agente, que está escrito en Python.
*   **Bash**: Disponible en `/bin/bash` (estándar en macOS y Linux). La inclusión de Bash permite al agente interactuar con el sistema operativo a un nivel más bajo, ejecutar comandos de shell y automatizar tareas administrativas.

El código se ejecuta en un **entorno de máquina virtual aislada (sandboxed VM)** [3]. Sin embargo, es importante destacar que, cuando se habilita el entorno de codificación local (`--enable_local_env`), el código se ejecuta directamente en la máquina del usuario con los mismos permisos que el usuario que lo ejecuta [1]. Esto implica que, aunque hay un concepto de "sandboxed VM" mencionado en el paper [3], la implementación de "local_env" en el README [1] advierte sobre la ejecución de código arbitrario con los permisos del usuario, lo que sugiere una capa de aislamiento limitada o un sandbox a nivel de proceso en lugar de una virtualización completa. Esta distinción es crucial para entender las implicaciones de seguridad.

### Manejo de Errores y Retroalimentación

El agente de código opera en un bucle interno con un presupuesto de pasos (`B`). En cada paso, el agente genera código y lo ejecuta, recibiendo retroalimentación del terminal (`ccode`) que incluye [3]:

*   **Estado (`statusk`)**: Indica el estado general de la ejecución del código.
*   **Código de retorno (`return codek`)**: Un valor numérico que señala el éxito o fracaso de la ejecución del comando o script.
*   **Salida estándar (`stdoutk`)**: La salida generada por el código ejecutado, que puede contener resultados, mensajes informativos o datos.
*   **Error estándar (`stderrk`)**: Los mensajes de error o advertencia generados durante la ejecución del código.

Esta retroalimentación permite al agente iterar y ajustar su código. Si el agente de código determina que una tarea no puede completarse mediante código, puede fallar y devolver el control al agente GUI [3]. Esta capacidad de "fallar con gracia" es importante para evitar bucles infinitos o intentos infructuosos de resolver problemas programáticamente.

Los scripts Bash ejecutados por el agente tienen un **tiempo de espera de 30 segundos** para evitar procesos colgados [1]. Este timeout es una medida de seguridad y estabilidad, previniendo que scripts erróneos o maliciosos consuman recursos indefinidamente.

### Verificación y Seguridad

Después de que el agente de código modifica archivos, el agente GUI es responsable de **verificar los cambios** a través de acciones GUI (por ejemplo, abriendo o inspeccionando los archivos en las aplicaciones relevantes) [3]. Es **CRÍTICO** que el agente GUI no confíe únicamente en la salida del agente de código y siempre verifique los resultados visualmente [3]. Esta verificación cruzada entre el agente de código y el agente GUI es una salvaguarda esencial para la fiabilidad y la corrección de las tareas.

**Advertencia de Seguridad**: La ejecución de código arbitrario con los permisos del usuario local conlleva riesgos significativos. Se recomienda usar esta característica solo en entornos de confianza y con entradas de confianza. Se sugiere considerar la ejecución en un entorno de sandbox más robusto para tareas no confiables [1]. Esta advertencia subraya la importancia de la concienciación sobre la seguridad al habilitar y utilizar el entorno de codificación local.

## MÓDULO E: Sandbox y entorno

Agent S opera en entornos que varían en su nivel de aislamiento y seguridad, dependiendo de la configuración y el propósito de la ejecución. La elección del entorno adecuado es crucial para equilibrar la funcionalidad con la seguridad y la reproducibilidad.

### Entorno de Ejecución Local

Cuando se habilita el **entorno de codificación local (`--enable_local_env`)**, Agent S ejecuta código Python y Bash directamente en la máquina del usuario [1]. En este escenario:

*   **Ubicación**: El código se ejecuta localmente en la máquina donde se inicia Agent S [1]. Esto significa que el agente tiene acceso directo a los recursos y al sistema de archivos del host.
*   **Aislamiento**: El nivel de aislamiento es limitado. El código se ejecuta con los **mismos permisos que el usuario** que ejecuta el agente [1]. Esto significa que no hay un sandbox de seguridad robusto a nivel de sistema operativo para el código generado por el agente en este modo. El documento advierte explícitamente sobre la ejecución de código arbitrario y recomienda su uso solo en **entornos de confianza** [1]. La falta de un aislamiento fuerte implica que cualquier vulnerabilidad en el código generado o en las herramientas utilizadas podría tener un impacto directo en el sistema del usuario.
*   **Recursos**: Utiliza los recursos del sistema local (CPU, memoria, almacenamiento) directamente. Esto puede ser eficiente para tareas que requieren acceso rápido a recursos locales, pero también puede llevar a un consumo elevado de recursos si el agente no está optimizado.
*   **Manejo de Errores**: Los scripts Bash tienen un **tiempo de espera de 30 segundos** para prevenir procesos colgados [1]. Esta es una medida de control para evitar que procesos erróneos se ejecuten indefinidamente y consuman recursos del sistema.

### Entorno de Benchmarking (OSWorld)

Para los benchmarks como OSWorld, el entorno de ejecución es más estructurado y potencialmente más aislado, diseñado para la evaluación rigurosa y reproducible del rendimiento del agente:

*   **Ubicación**: Las trayectorias de los agentes se recopilan ejecutando OSWorld en **AWS** [3]. Esto indica el uso de infraestructura en la nube para proporcionar entornos de ejecución escalables y gestionados.
*   **Aislamiento**: Una instancia anfitriona (por ejemplo, `c4.8xlarge`) contiene el código de OSWorld y el script para ejecutar Agent S3. El marco de OSWorld **genera un número especificado de instancias EC2**, cada una ejecutando una tarea de OSWorld [3]. Esto sugiere un aislamiento a nivel de máquina virtual o contenedor para cada tarea, proporcionando un entorno más controlado y reproducible para la evaluación. Cada instancia EC2 actúa como un sandbox virtual, donde las tareas se ejecutan de forma independiente, minimizando la interferencia y mejorando la seguridad entre tareas.
*   **Seguridad**: Aunque el paper no detalla las medidas de seguridad específicas de AWS, el uso de instancias EC2 separadas para cada tarea implica un nivel de aislamiento inherente que es superior a la ejecución local sin sandbox. AWS proporciona una infraestructura segura que puede ser configurada para aislar aún más los entornos de ejecución.
*   **Recursos**: Las instancias EC2 proporcionan recursos dedicados para cada tarea, permitiendo la ejecución en paralelo de múltiples `rollouts` [3]. Por ejemplo, una instancia `c4.8xlarge` puede soportar 40 instancias de OSWorld generadas en paralelo [3]. Esta capacidad de paralelización es esencial para realizar evaluaciones a gran escala de manera eficiente.

En resumen, Agent S puede operar en un entorno local con aislamiento limitado para tareas de desarrollo y en un entorno de nube más aislado y escalable para benchmarking y evaluación rigurosa. La elección del entorno depende de la necesidad de seguridad, aislamiento y recursos computacionales.

## MÓDULO F: Memoria y contexto

La gestión de la memoria y el contexto es fundamental para la capacidad de Agent S de operar de manera autónoma y realizar tareas complejas. El agente mantiene varios tipos de información para guiar su comportamiento, permitiéndole aprender de experiencias pasadas y adaptarse a nuevas situaciones.

### Historial de Observaciones y Acciones

Agent S mantiene un **historial ordenado por tiempo (`ht`)** de todas las observaciones y acciones consecutivas. Este historial incluye `(o0, a0, ..., ot−1, at−1, ot)`, donde `o` representa una observación (como una captura de pantalla) y `a` representa una acción [3]. Este `ht` sirve como la memoria principal del agente sobre su interacción con el entorno. Es una representación detallada de la secuencia de eventos que han ocurrido, permitiendo al agente reconstruir el flujo de la interacción y entender cómo sus acciones han afectado el estado del sistema.

### Ventana de Contexto

Existe un parámetro clave, `--max_trajectory_length`, que define el **número máximo de "turnos de imagen" a mantener en la trayectoria**, con un valor predeterminado de 8 [1]. Esto sugiere una ventana de contexto limitada para las observaciones visuales, lo que implica que el agente solo "recuerda" las últimas 8 interacciones visuales para tomar decisiones. Las trayectorias densas y multimodales pueden ser difíciles de interpretar, por lo que la gestión de esta ventana es crucial para la eficiencia [3]. Una ventana de contexto limitada ayuda a mantener la complejidad computacional manejable y a enfocar al agente en la información más reciente y relevante.

### Narrativas de Comportamiento (Behavior Narratives)

Para abordar el desafío de evaluar y comparar trayectorias complejas, Agent S introduce el concepto de **Narrativas de Comportamiento (Behavior Narratives)** [3]. Estas son resúmenes concisos que capturan lo que el agente hizo y cómo afectó al entorno, preservando los resúmenes de acción-efecto relevantes para la tarea y filtrando detalles irrelevantes en pasos individuales [3]. Las narrativas de comportamiento proporcionan una representación compacta y fiel que facilita la selección entre múltiples `rollouts`, lo que puede considerarse una forma de compresión y abstracción de la memoria a largo plazo para la evaluación. Esta abstracción es vital para el escalado y la eficiencia en la evaluación de múltiples ejecuciones del agente.

### Contexto del Agente de Código

Cuando el agente de código está activo, mantiene un contexto específico para la ejecución de código. Este contexto incluye la retroalimentación (`ccode`) de iteraciones anteriores, que abarca el estado, el código de retorno, la salida estándar (`stdout`) y el error estándar (`stderr`) [3]. Esta información es crucial para que el agente de código itere y ajuste su lógica de programación. El agente principal (`worker`) anexa este bloque de contexto (`ccode`) a su historial (`ht+1`) [3]. Esto permite que el agente de código tenga una memoria de sus intentos de programación y los resultados obtenidos, facilitando la depuración y la mejora iterativa.

### Reflexión

El parámetro `--enable_reflection` (Default: `True`) [1] indica la capacidad del agente para reflexionar. Esto implica que el agente puede revisar su historial y contexto para evaluar su desempeño, identificar errores o mejorar su estrategia, lo que requiere acceso a su memoria para un autoanálisis y ajuste de su comportamiento.

## MÓDULO G: Browser/GUI

Agent S está fundamentalmente diseñado como un **agente GUI (Graphical User Interface)**, lo que le permite interactuar con computadoras de manera autónoma como lo haría un humano [1]. Su capacidad para navegar y manipular interfaces gráficas es un pilar central de su arquitectura.

### Interacción y Observación

La interacción de Agent S con el entorno GUI se basa en un **espacio de acciones (A)** que incluye operaciones directas sobre la interfaz, como `agent.click(...)` para simular clics y `agent.type(...)` para introducir texto [3]. Estas acciones son ejecutadas por el agente principal `AgentS3` [1].

El agente percibe el entorno a través de un **espacio de observaciones (O)** que se compone principalmente de **capturas de pantalla del escritorio (`desktop screenshots`)** [3]. Estas observaciones visuales son cruciales para que el agente entienda el estado actual de la interfaz y tome decisiones informadas.

### Modelos de Grounding Visual

Para traducir las observaciones visuales en acciones significativas, Agent S utiliza **modelos de *grounding* multimodal (MLLM)**. El modelo recomendado para un rendimiento óptimo es **UI-TARS-1.5-7B**, que se encarga de traducir las acciones del agente en código Python ejecutable [1]. La resolución de coordenadas de salida de estos modelos de *grounding* se define mediante los parámetros `--grounding_width` y `--grounding_height` (por ejemplo, `1920x1080` para UI-TARS-1.5-7B) [1]. Esto asegura que el agente pueda identificar y apuntar con precisión a elementos en la pantalla.

### Manejo de Login y Sesiones

Aunque los documentos no detallan explícitamente un mecanismo de "manejo de login" genérico, la capacidad de Agent S para operar en entornos como WindowsAgentArena y OSWorld, que a menudo requieren autenticación, sugiere que puede interactuar con formularios de login estándar a través de sus acciones `type` y `click`. La persistencia de sesiones no se menciona directamente, pero la capacidad de completar tareas de "largo horizonte" implica que puede mantener el estado de la sesión durante la ejecución de una tarea.

### Verificación de Acciones

Un aspecto crítico de la operación GUI de Agent S es la **verificación de las acciones del agente de código**. Si el agente de código realiza modificaciones en archivos o aplicaciones, el agente GUI es responsable de **verificar visualmente** estos cambios. Esto se logra abriendo o inspeccionando los archivos en las aplicaciones relevantes a través de la interfaz gráfica [3]. Se enfatiza que el agente GUI **nunca debe confiar únicamente en la salida del agente de código** y siempre debe verificar los resultados visualmente [3].

### Limitaciones del Entorno GUI

Agent S está diseñado para operar en **pantallas de un solo monitor** [1]. Esto implica una limitación en su capacidad para manejar configuraciones de múltiples pantallas, lo que podría ser relevante para ciertos escenarios de uso. Además, el rendimiento en benchmarks como OSWorld destaca los desafíos en el *grounding* GUI y las operaciones, lo que sugiere que la interpretación visual y la ejecución precisa siguen siendo áreas de mejora continua [3].

## MÓDULO H: Multi-agente

Agent S demuestra capacidades multi-agente tanto a nivel de su arquitectura interna como en su estrategia de ejecución para mejorar el rendimiento y la robustez.

### Arquitectura Interna de Agentes Colaborativos

Agent S opera con una arquitectura que integra al menos dos tipos de agentes especializados [1, 3]:

*   **Agente GUI (Graphical User Interface)**: Este es el agente principal responsable de interactuar con la interfaz gráfica del sistema operativo, realizando acciones como clics y escritura de texto [3].
*   **Agente de Código (Code Agent)**: Un agente especializado en la ejecución de código Python y Bash para tareas programáticas, como procesamiento de datos o automatización del sistema [1].

El agente principal (`AgentS3`) coordina la interacción entre estos dos agentes, delegando tareas al agente de código mediante la acción `call_code_agent` cuando la tarea lo requiere [1]. La elección del agente apropiado (GUI o código) se basa en la naturaleza de la tarea a realizar [3].

Además, el parámetro `--enable_reflection` (Default: `True`) [1] sugiere la presencia de un **agente de reflexión** que asiste al agente trabajador. Este agente de reflexión probablemente se encarga de revisar y refinar las acciones o planes del agente principal, contribuyendo a la mejora continua del rendimiento.

### Estrategia de Escalado Múltiple (Wide Scaling)

Para superar las limitaciones de las ejecuciones de un solo `rollout` (trayectoria), Agent S implementa una estrategia de **escalado múltiple (`wide scaling`)** [3]. En lugar de depender de una única ejecución de un agente, esta estrategia permite:

*   **Generación de Múltiples Rollouts**: Se generan múltiples trayectorias en paralelo, ya sea a partir de diferentes instancias de agentes o utilizando múltiples modelos base y políticas [3]. Esto se basa en la observación de que los agentes, aunque subóptimos individualmente, a menudo tienen éxito en subconjuntos complementarios de tareas [3].
*   **Behavior Judge (BJudge)**: Para seleccionar la mejor trayectoria entre los múltiples `rollouts` generados, Agent S introduce el **Behavior Judge (BJudge)** [3]. Este componente clave aborda el desafío de la evaluación de trayectorias complejas convirtiéndolas en **narrativas de comportamiento (`behavior narratives`)** concisas. Estas narrativas resumen lo que el agente hizo y cómo afectó al entorno, filtrando detalles irrelevantes y facilitando la comparación y selección de la trayectoria óptima [3].

Esta aproximación multi-agente y de escalado múltiple es fundamental para la capacidad de Agent S de lograr un rendimiento superior al humano en benchmarks como OSWorld, mejorando la robustez y la tasa de éxito en tareas de largo horizonte [3].

## MÓDULO I: Integraciones

Agent S está diseñado para integrarse con una variedad de modelos de lenguaje grandes (LLMs) y modelos de *grounding* multimodal (MLLMs) a través de sus respectivas APIs, lo que le confiere una gran flexibilidad y capacidad de adaptación a diferentes proveedores y configuraciones.

### Integración con Modelos de Lenguaje y Multimodales (MLLMs)

Agent S soporta la integración con los siguientes proveedores de MLLM para inferencia [1, 2]:

*   **OpenAI**: Requiere `OPENAI_API_KEY`.
*   **Anthropic**: Requiere `ANTHROPIC_API_KEY`.
*   **Gemini**: Requiere `GEMINI_API_KEY` y `GEMINI_ENDPOINT_URL`.
*   **Azure OpenAI**: Requiere `AZURE_OPENAI_API_BASE` y `AZURE_OPENAI_API_KEY`.
*   **vLLM para Modelos Locales**: Requiere `vLLM_ENDPOINT_URL` para modelos desplegados localmente.
*   **Open Router**: Requiere `OPENROUTER_API_KEY` y `OPEN_ROUTER_ENDPOINT_URL`.

La configuración de estas integraciones se puede realizar mediante variables de entorno o directamente pasando las claves API en el argumento `engine_params` al instanciar el agente [1, 2].

### Integración con Modelos de Grounding

Para un rendimiento óptimo, Agent S recomienda la integración con modelos de *grounding* específicos. El modelo **UI-TARS-1.5-7B** es el recomendado y puede ser alojado en Hugging Face Inference Endpoints u otros proveedores [1]. La configuración de estos modelos de *grounding* incluye:

*   `--ground_provider`: Proveedor del modelo de *grounding* (e.g., `huggingface`) [1].
*   `--ground_url`: URL del modelo de *grounding* [1].
*   `--ground_model`: Nombre del modelo de *grounding* (e.g., `ui-tars-1.5-7b`) [1].
*   `--ground_api_key`: Clave API para el endpoint del modelo de *grounding* (opcional) [1].

### Integración con Entornos de Evaluación

Agent S se integra con entornos de evaluación como **OSWorld**, **WindowsAgentArena** y **AndroidWorld** para benchmarking y demostración de sus capacidades [1, 3]. Estas integraciones permiten al agente operar y ser evaluado en diversas plataformas y aplicaciones, lo que es crucial para validar su generalizabilidad.

### SDK y Librerías

El `gui_agents` SDK es una parte fundamental de la integración, proporcionando las clases `AgentS3` y `OSWorldACI` para construir y configurar los agentes. La librería `dotenv` se utiliza para cargar las claves API desde variables de entorno, facilitando la gestión de credenciales [1].

### OAuth y APIs Específicas

Aunque los documentos mencionan el uso de claves API para la autenticación con los proveedores de MLLM, no se detalla explícitamente el uso de **OAuth** para integraciones más complejas con servicios de terceros. Las integraciones se centran principalmente en la conexión con modelos de IA para inferencia y *grounding*, así como con entornos de evaluación.

## MÓDULO J: Multimodal

La capacidad multimodal es un pilar fundamental en la arquitectura de Agent S, permitiéndole interactuar con el entorno informático de una manera similar a la humana, a través de la percepción visual y la comprensión del lenguaje.

### Procesamiento de Imágenes y Video

Agent S utiliza **capturas de pantalla del escritorio (`desktop screenshots`)** como su principal forma de observación del entorno [3]. Estas imágenes son el input visual que el agente procesa para entender el estado actual de la interfaz gráfica de usuario (GUI). La interacción se basa en la traducción de estas observaciones visuales en acciones concretas, como clics o escritura.

Para el procesamiento de estas imágenes, Agent S se apoya en **Modelos de Lenguaje Multimodal (MLLMs)** para inferencia [1, 2]. Estos modelos son capaces de procesar tanto texto como imágenes, lo que es esencial para interpretar el contenido visual de las capturas de pantalla y relacionarlo con las instrucciones en lenguaje natural.

### Modelos de Grounding Visual

Un componente crítico de la capacidad multimodal de Agent S son los **modelos de *grounding* visual**. Estos modelos son responsables de traducir las observaciones visuales en acciones ejecutables. El modelo recomendado para un rendimiento óptimo es **UI-TARS-1.5-7B**, que puede ser alojado en Hugging Face Inference Endpoints [1].

Los modelos de *grounding* operan con una resolución de coordenadas específica, definida por `--grounding_width` y `--grounding_height` (por ejemplo, `1920x1080` para UI-TARS-1.5-7B) [1]. Esto asegura que el agente pueda identificar y localizar con precisión los elementos interactivos en la pantalla, permitiendo acciones a nivel de píxel cuando sea necesario [3].

### Integración con MLLMs

Agent S soporta la integración con una variedad de proveedores de MLLM, lo que le permite aprovechar diferentes capacidades y modelos para la inferencia multimodal [1, 2]:

*   **OpenAI**
*   **Anthropic**
*   **Gemini**
*   **Azure OpenAI**
*   **vLLM para Modelos Locales**
*   **Open Router**

Estos modelos son utilizados para la inferencia principal del agente, lo que implica que son cruciales para la comprensión de las instrucciones, la planificación y la generación de las acciones a realizar, basándose en la información multimodal recibida.

### Ausencia de Procesamiento Directo de Audio

Los documentos revisados no mencionan explícitamente la capacidad de Agent S para procesar audio o video directamente como entrada para la toma de decisiones. Su enfoque multimodal se centra principalmente en la **interacción visual a través de capturas de pantalla** y la comprensión del lenguaje natural.

## MÓDULO K: Límites y errores

Agent S, a pesar de sus capacidades avanzadas, presenta ciertas limitaciones y desafíos inherentes a la complejidad de la interacción autónoma con computadoras. Estos se manifiestan en su rendimiento, seguridad y diseño arquitectónico.

### Limitaciones de Rendimiento y Robustez

*   **Fiabilidad en Tareas de Largo Horizonte**: Los agentes de uso de computadora (CUAs) como Agent S, aunque prometedores, aún son **poco fiables en problemas complejos y de largo horizonte** [3]. La ejecución de un solo `rollout` es frágil, con pequeños errores que se acumulan con el tiempo, llevando a una alta varianza en los resultados [3].
*   **Dificultad en la Corrección Sostenida**: Mantener la corrección a lo largo de docenas o cientos de interacciones es un desafío. Pequeños errores se acumulan, la retroalimentación se retrasa, las rutas de solución se ramifican de manera impredecible y el ruido ambiental (cambios en la interfaz de usuario, ventanas emergentes, latencia) desestabiliza aún más el rendimiento [3].
*   **Cuello de Botella en la Evaluación**: La estrategia de escalado múltiple (`wide scaling`), aunque efectiva para generar múltiples `rollouts`, enfrenta un **cuello de botella fundamental en la evaluación**. Determinar de manera fiable cuál de las múltiples trayectorias es la correcta es difícil debido a la densidad de información y la naturaleza multimodal de las trayectorias [3].
*   **Limitaciones de los Jueces VLM**: Los jueces basados en Modelos de Visión-Lenguaje (VLM) suelen estar ajustados para el dominio web, requieren rúbricas definidas por humanos y no generalizan bien a tareas más amplias de CUAs. Alinear estos jueces con el juicio humano requiere un esfuerzo manual sustancial [3].

### Errores y Fallos Específicos

*   **Alucinaciones en Narrativas de Comportamiento**: Se han identificado fallos relacionados con **alucinaciones en la generación de narrativas de comportamiento** y problemas en la interacción entre el agente de código y la GUI [3].
*   **Fallo del Agente de Código**: Si el agente de código determina que una tarea no puede completarse programáticamente, puede fallar y devolver el control al agente GUI [3].

### Consideraciones de Seguridad y Entorno

*   **Ejecución de Código Arbitrario Local**: El **entorno de codificación local** de Agent S ejecuta código Python y Bash arbitrario directamente en la máquina del usuario con los **mismos permisos que el usuario** [1]. Esto representa un riesgo de seguridad significativo y se advierte que solo debe usarse en entornos de confianza y con entradas de confianza. Se recomienda considerar la ejecución en un entorno de sandbox más robusto para tareas no confiables [1].
*   **Dependencia de un Solo Monitor**: El agente está diseñado para operar en **pantallas de un solo monitor** [1], lo que limita su aplicabilidad en configuraciones de múltiples pantallas.
*   **Persistencia del Código**: El código de cada paso en el agente de código **no persiste** en el siguiente paso; se requiere escribir fragmentos de código completos e independientes en cada iteración [3].
*   **Limpieza del Entorno**: El agente debe devolver el control con un escritorio limpio, cerrando cualquier ventana emergente, pestaña o barra de herramientas [3].

### Recuperación y Verificación

*   **Verificación Crítica del Agente GUI**: Después de que el agente de código modifica archivos, el agente GUI es **CRÍTICO** para verificar visualmente estos cambios a través de acciones GUI (por ejemplo, abriendo o inspeccionando los archivos en las aplicaciones relevantes). El agente GUI **nunca debe confiar únicamente en la salida del agente de código** [3].
*   **Tiempo de Espera para Scripts Bash**: Los scripts Bash ejecutados tienen un **tiempo de espera de 30 segundos** para evitar procesos colgados [1].

Estas limitaciones y consideraciones son cruciales para entender el alcance y las precauciones necesarias al implementar y utilizar Agent S.

## MÓDULO L: Benchmarks

Agent S ha sido rigurosamente evaluado en varios benchmarks de uso de computadora (CUA), demostrando un rendimiento superior y estableciendo nuevos estados del arte en la interacción autónoma con interfaces gráficas.

### OSWorld

**OSWorld** es un benchmark clave para evaluar agentes multimodales en tareas de computadora de extremo a extremo [1, 3]. Agent S3 ha logrado resultados sobresalientes en este benchmark:

*   **Rendimiento Superior al Humano**: Agent S3 fue el **primero en superar el rendimiento a nivel humano en OSWorld**, alcanzando un impresionante **72.60%** de éxito en tareas de 100 pasos [1, 3]. Esto supera el rendimiento humano del 72.36% [3] y el estado del arte anterior del 63.4% (GTA1 con GPT-5) [1, 3].
*   **Mejora con Behavior Best-of-N (bBoN)**: Con la adición de la estrategia Behavior Best-of-N, el rendimiento de Agent S3 en OSWorld se eleva aún más al 72.6% [1].
*   **Conjunto de Tareas**: El benchmark OSWorld incluye 361 tareas [3].
*   **Evaluación**: Las trayectorias de los agentes se recopilan ejecutando OSWorld en AWS, donde el marco de OSWorld genera instancias EC2 para cada tarea, permitiendo la ejecución en paralelo [3].

### WindowsAgentArena

Agent S3 demuestra una **fuerte generalizabilidad *zero-shot*** en **WindowsAgentArena**, un benchmark de Windows con 154 tareas que abarcan aplicaciones como LibreOffice Writer/Calc, Edge/Chrome, Explorador de Archivos/Configuración de Windows, VS Code y VLC [1, 3].

*   **Mejora de Precisión**: La precisión en WindowsAgentArena aumenta del 50.2% (usando solo Agent S3) al 56.6% al seleccionar entre 3 `rollouts` [1].

### AndroidWorld

Similarmente, Agent S3 muestra una **fuerte generalizabilidad *zero-shot*** en **AndroidWorld**, un benchmark de Android con 116 tareas [1, 3].

*   **Mejora de Rendimiento**: El rendimiento en AndroidWorld mejora del 68.1% al 71.6% [1].

### Comparaciones con Otros Agentes

Agent S2 (una versión anterior) ya se posicionó como el **estado del arte para agentes de uso de computadora (CUA)**, superando a agentes como CUA/Operator de OpenAI y Claude 3.7 Sonnet Computer-Use de Anthropic [1].

### Métricas de Evaluación

Además de la tasa de éxito, el paper de Agent S3 también menciona otras métricas como [3]:

*   **Reducción de Llamadas a LLM**: Una mejora del 13.8% en la tasa de éxito, una reducción del 52.3% en las llamadas a LLM por tarea y una reducción del 62.4% en el tiempo promedio de finalización de la tarea.
*   **Eficiencia**: Se proporcionan estadísticas de eficiencia en OSWorld, particularmente cuando se utiliza GPT-5 como modelo principal [3].

Estos resultados demuestran la robustez y la capacidad de Agent S para operar eficazmente en diversos entornos informáticos, superando las capacidades de otros agentes y, en algunos casos, el rendimiento humano.

## Lecciones para el Monstruo

La investigación detallada de Agent S3 y su arquitectura ofrece varias lecciones valiosas para el desarrollo de agentes de IA avanzados, especialmente aquellos diseñados para interactuar con entornos complejos como los sistemas operativos.

1.  **La modularidad es clave para la robustez y la generalizabilidad**: La arquitectura de Agent S, que separa las capacidades GUI del agente de código y utiliza un agente principal para coordinarlos, demuestra cómo la modularidad puede mejorar la capacidad del agente para abordar diversas tareas. Para "El Monstruo", esto significa diseñar componentes especializados (e.g., para interacción web, manipulación de archivos, análisis de datos) que puedan ser orquestados por un agente de alto nivel.

2.  **La verificación visual es indispensable para la fiabilidad**: La insistencia de Agent S en que el agente GUI verifique visualmente los resultados de las acciones del agente de código es una lección crítica. No se debe confiar ciegamente en la salida de un sub-agente o una herramienta. "El Monstruo" debe incorporar mecanismos de verificación cruzada y validación visual (o multimodal) para asegurar que las acciones se han ejecutado correctamente y que el estado del entorno es el esperado, especialmente después de operaciones críticas o que involucran la modificación de datos.

3.  **La gestión inteligente del contexto es vital para tareas de largo horizonte**: La estrategia de Agent S de mantener un historial de observaciones y acciones, junto con una ventana de contexto limitada para las observaciones visuales y la creación de "narrativas de comportamiento", subraya la importancia de una gestión eficiente de la memoria. Para "El Monstruo", esto implica desarrollar mecanismos sofisticados para resumir, abstraer y priorizar la información relevante a lo largo de una tarea, evitando la sobrecarga de contexto y permitiendo un razonamiento efectivo en tareas que se extienden por muchas interacciones.

4.  **El escalado múltiple y la evaluación post-hoc mejoran la tasa de éxito**: La estrategia de "wide scaling" de Agent S, que genera múltiples `rollouts` y utiliza un "Behavior Judge" para seleccionar la mejor trayectoria, es una poderosa técnica para superar la fragilidad inherente de las ejecuciones individuales. "El Monstruo" podría beneficiarse enormemente de la ejecución paralela de múltiples estrategias o caminos de acción, seguida de un mecanismo de evaluación inteligente que identifique la solución más prometedora. Esto es especialmente relevante para tareas con alta varianza o donde la exploración de múltiples enfoques es beneficiosa.

5.  **La seguridad y el aislamiento del entorno son consideraciones primordiales**: La advertencia explícita sobre la ejecución de código arbitrario en el entorno local de Agent S y la recomendación de usar sandboxes más robustos para tareas no confiables, es una lección fundamental. "El Monstruo" debe priorizar la seguridad del sistema anfitrión. Esto implica la implementación de entornos de ejecución aislados (sandboxes robustos, contenedores, VMs) para cualquier componente que ejecute código generado por IA, y una clara delimitación de permisos para mitigar riesgos potenciales.

6.  **La adaptabilidad a diversos modelos y entornos es una ventaja competitiva**: La capacidad de Agent S para integrarse con múltiples proveedores de LLM/MLLM y operar en diferentes entornos de evaluación (OSWorld, WindowsAgentArena, AndroidWorld) demuestra la importancia de un diseño flexible. "El Monstruo" debería ser agnóstico a los modelos subyacentes y a los entornos específicos, permitiendo la fácil sustitución de componentes de IA y la adaptación a nuevas plataformas o APIs. Esto asegura la longevidad y la relevancia del agente a medida que la tecnología evoluciona.

## Referencias

[1] Simular AI. (2026). *Agent S: Use Computer Like a Human*. GitHub Repository. Disponible en: [https://github.com/simular-ai/Agent-S](https://github.com/simular-ai/Agent-S)

[2] Simular AI. (2026). *Supported Models for Agent S*. GitHub Repository. Disponible en: [https://github.com/simular-ai/Agent-S/blob/main/models.md](https://github.com/simular-ai/Agent-S/blob/main/models.md)

[3] Li, Z., Hao, S., Agashe, S., Wang, X., & Zhang, Y. (2025). *Agent S3: Surpassing Human Performance on OSWorld with Enhanced Generalization*. arXiv preprint arXiv:2510.00000. Disponible en: [https://arxiv.org/pdf/2510.02250](https://arxiv.org/pdf/2510.02250)


---

## Fase 3 — Módulos Complementarios: Agent-S v0.3.2 (Simular AI)

### Orquestación Multi-Agente

Agent-S v0.3.2, desarrollado por Simular AI, aborda la orquestación multi-agente a través de un paradigma de **escalado amplio** (wide scaling) que busca mejorar la robustez y las tasas de éxito en tareas complejas de uso de computadoras (Computer-Use Agents o CUAs) [1]. A diferencia de los enfoques que se centran en mejorar el rendimiento de un solo agente o en la selección de acciones paso a paso, Agent-S se enfoca en generar múltiples "rollouts" o trayectorias de solución en paralelo y luego seleccionar la mejor entre ellas [1].

#### Creación y Coordinación de Sub-Agentes

El marco de Agent-S no crea explícitamente sub-agentes en el sentido tradicional de entidades autónomas con roles distintos. En cambio, su estrategia de escalado amplio implica la generación de **múltiples ejecuciones de un agente base** en paralelo. Cada una de estas ejecuciones puede considerarse una instancia de "sub-agente" que explora una trayectoria de solución diferente para una tarea dada [1].

La coordinación de estos "sub-agentes" se realiza a través de un componente central llamado **Behavior Judge (BJudge)**. BJudge es un marco novedoso que transforma las trayectorias densas de los agentes en **narrativas de comportamiento compactas**. Estas narrativas resumen lo que el agente hizo y cómo afectó al entorno, filtrando detalles irrelevantes y preservando la información crucial de acción-efecto [1]. Al comparar estas narrativas de comportamiento, BJudge puede evaluar y seleccionar la trayectoria óptima entre las múltiples generadas. Esto permite que el sistema aproveche la complementariedad de las soluciones propuestas por diferentes instancias del agente, incluso si individualmente son subóptimas [1].

El Agent-S también incorpora un **agente de reflexión** (`enable_reflection=True`) que asiste al agente trabajador [2]. Aunque los detalles específicos de su funcionamiento no se describen en profundidad en la documentación pública, la presencia de un agente de reflexión sugiere un mecanismo de coordinación interno donde una entidad monitorea y posiblemente guía o refina las acciones del agente principal o de las instancias de los sub-agentes.

#### Protocolos de Comunicación y Límites de Paralelismo

Los protocolos de comunicación entre las instancias de los agentes y el BJudge se basan en la representación de las trayectorias como narrativas de comportamiento. Cada instancia de agente genera su propia trayectoria, que luego es procesada por el BJudge para su evaluación y selección. Esto implica un flujo de información unidireccional desde los agentes ejecutores hacia el juez de comportamiento [1].

En cuanto a los límites de paralelismo, el concepto de escalado amplio de Agent-S implica inherentemente la ejecución de múltiples rollouts en paralelo. El paper de Agent S3 discute cómo el rendimiento de BJudge varía con el presupuesto total de recursos y el número de "trabajadores" (N) [1]. Se observa que a presupuestos más pequeños, un solo agente puede rendir mejor, ya que distribuir el cómputo entre muchos trabajadores puede reducir el presupuesto de pasos por trabajador por debajo de lo necesario para completar la tarea. Sin embargo, a medida que aumenta el presupuesto total, valores más grandes de N (por ejemplo, N=4 o N=10) se vuelven más efectivos, logrando mejoras significativas en el rendimiento [1].

Es crucial destacar que la ejecución de agentes en paralelo requiere entornos aislados para evitar interferencias. El paper menciona que ejecutar agentes directamente en el escritorio en vivo de un usuario sin aislamiento puede violar la suposición de independencia, ya que los rollouts concurrentes pueden interferir entre sí. Esto subraya la necesidad de entornos virtualizados (VMs o contenedores) que soporten la duplicación y el "snapshotting" para permitir rollouts paralelos con latencia adicional limitada [1]. Las tareas que interactúan con recursos compartidos en línea (como correo electrónico o almacenamiento en la nube) también pueden introducir interferencias entre ejecuciones a través de un estado externo compartido, lo que representa un desafío para futuras mejoras en la infraestructura de CUAs [1].

### Integraciones y Connectors

Agent-S v0.3.2 está diseñado para interactuar con computadoras a través de una Interfaz Agente-Computadora (ACI), lo que le permite automatizar tareas digitales cotidianas [2]. Las integraciones y conectores de Agent-S se centran principalmente en su capacidad para interactuar con el sistema operativo subyacente y con modelos de lenguaje grandes (LLMs) y modelos de "grounding" externos.

#### APIs/Servicios Soportados

Agent-S soporta la integración con varios proveedores de modelos de lenguaje grandes (LLMs) para la generación principal y modelos de "grounding" para la comprensión visual y la interacción con la interfaz gráfica de usuario (GUI). Los proveedores de LLMs soportados incluyen [2]:

*   **Azure OpenAI**
*   **Anthropic**
*   **Gemini**
*   **Open Router**
*   **vLLM inference**

Para los modelos de "grounding", Agent-S recomienda y soporta **UI-TARS-1.5-7B** y **UI-TARS-72B**, que pueden ser alojados en Hugging Face Inference Endpoints o en otros proveedores [2]. Estos modelos de "grounding" son cruciales para traducir las acciones del agente en código Python ejecutable y para la comprensión visual de la interfaz de usuario [2].

El framework utiliza claves API para la autenticación con estos servicios, que pueden configurarse a través de variables de entorno (por ejemplo, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `HF_TOKEN`) o mediante un script de Python [2]. Esto indica un enfoque directo de integración a través de APIs RESTful o SDKs específicos de cada proveedor, donde la autenticación se gestiona mediante tokens o claves API.

#### Manejo de OAuth y Webhooks

La documentación disponible de Agent-S v0.3.2 no detalla explícitamente el manejo de OAuth o webhooks como mecanismos de integración directa para conectores externos. Sin embargo, la capacidad del agente para ejecutar código Python y Bash en un entorno local (`--enable_local_env`) [2] sugiere que puede interactuar con servicios que utilizan OAuth o webhooks de manera programática. Un agente habilitado con el entorno de codificación local puede:

*   **Procesar Datos**: Manipular hojas de cálculo, archivos CSV o bases de datos [2].
*   **Operaciones de Archivos**: Procesamiento masivo de archivos, extracción de contenido u organización de archivos [2].
*   **Automatización del Sistema**: Cambios de configuración, configuración del sistema o scripts de automatización [2].
*   **Desarrollo de Código**: Escribir, editar o ejecutar archivos de código [2].
*   **Procesamiento de Texto**: Manipulación de documentos, edición de contenido o formato [2].

Esto implica que, si un servicio externo requiere autenticación OAuth o la recepción de webhooks, el agente podría ser programado para manejar estos flujos a través de scripts personalizados. Por ejemplo, un script Python podría implementar el flujo de OAuth 2.0 para obtener tokens de acceso y luego usar esos tokens para interactuar con una API protegida. De manera similar, un script podría configurar un "listener" para webhooks y procesar las cargas útiles entrantes. Sin embargo, esta funcionalidad no está integrada de forma nativa o simplificada a través de un "conector" predefinido para OAuth/webhooks en la versión actual.

#### Lista de Conectores Disponibles

Agent-S v0.3.2 se enfoca en la interacción con la interfaz gráfica de usuario (GUI) y la ejecución de código local, más que en una amplia gama de conectores pre-construidos a servicios de terceros. Los "conectores" principales son los que permiten la comunicación con los LLMs y modelos de "grounding" mencionados anteriormente [2].

La capacidad de interactuar con el entorno local a través de la ejecución de código Python y Bash (`call_code_agent` action) [2] le otorga una flexibilidad considerable para integrarse con cualquier servicio o API que pueda ser accedido o manipulado mediante programación. Esto significa que, aunque no haya una lista exhaustiva de "conectores" pre-construidos en el sentido de integraciones directas con plataformas SaaS específicas (como Asana, Notion, PayPal, Gmail, Google Calendar, Outlook Mail, etc.), el agente tiene la capacidad de "construir" sus propias integraciones a través de la codificación. La integración con **OpenClaw** mencionada en el historial de commits de GitHub [2] sugiere un enfoque modular para añadir capacidades de integración, aunque los detalles específicos de OpenClaw no se proporcionan en el README.

En resumen, Agent-S v0.3.2 no ofrece una lista predefinida de conectores externos en el mismo sentido que una plataforma de integración empresarial. En cambio, su arquitectura permite la integración programática con cualquier servicio a través de su entorno de codificación local y su soporte para diversas APIs de LLMs y modelos de "grounding".

### Referencias

[1] Gonzalez-Pumariega, G., Tu, V., Lee, C.-L., Yang, J., Li, A., & Wang, X. E. (2025). *Scaling Agents for Computer Use*. arXiv. https://arxiv.org/abs/2510.02250
[2] simular-ai. (n.d.). *Agent-S: an open agentic framework that uses computers like a human*. GitHub. Recuperado el 1 de mayo de 2026, de https://github.com/simular-ai/Agent-S