# Biblia de Implementación: Gemini Robotics-ER 1.6 Google DeepMind

**Fecha de Lanzamiento:** 14 de abril de 2026
**Versión:** 1.6
**Arquitectura Principal:** Modelo de Visión-Lenguaje (VLM) con capacidades agénticas para robótica.

## 1. Visión General y Diferenciador Único

Gemini Robotics-ER 1.6 es un modelo de inteligencia artificial desarrollado por Google DeepMind, diseñado específicamente para dotar a los robots de una comprensión y capacidad de interacción con el mundo físico sin precedentes [1] [2]. Este modelo se posiciona como el cerebro de alto nivel para un robot, permitiéndole interpretar datos visuales complejos, realizar razonamiento espacial avanzado y planificar acciones a partir de comandos expresados en lenguaje natural [1].

El diferenciador único de Gemini Robotics-ER 1.6 radica en su concepto de **"razonamiento encarnado" (embodied reasoning)**. Esta capacidad fundamental le permite al agente cerrar la brecha entre la inteligencia digital y la acción física, posibilitando que los robots no solo sigan instrucciones, sino que también razonen activamente sobre su entorno físico [1]. El modelo integra una comprensión visual y espacial profunda, la planificación de tareas y la detección de éxito, incluso en entornos dinámicos y ocluidos. Un componente clave de este razonamiento encarnado es la **visión agéntica**, que combina el razonamiento visual con la ejecución de código para lograr lecturas de instrumentos altamente precisas y otras interacciones complejas [1].

## 2. Arquitectura Técnica

Gemini Robotics-ER 1.6 se fundamenta en una arquitectura de **Modelo de Visión-Lenguaje (VLM)**, lo que le permite procesar y comprender información multimodal [2]. Está construido sobre la base de modelos Gemini anteriores, como Gemini 2.0, e incorpora mejoras significativas respecto a Gemini Robotics-ER 1.5 y Gemini 3.0 Flash, particularmente en sus capacidades de razonamiento espacial y físico [1].

El modelo acepta una variedad de entradas, incluyendo imágenes, video, audio y prompts en lenguaje natural. Sus salidas son estructuradas, proporcionando coordenadas (puntos o bounding boxes) que representan ubicaciones de objetos, así como respuestas en formatos como JSON para facilitar la integración con sistemas robóticos [2].

Los componentes técnicos clave que habilitan sus capacidades incluyen:

*   **Comprensión de objetos y contexto de escena:** El modelo es capaz de identificar objetos dentro de un entorno y razonar sobre sus relaciones espaciales y funcionales (affordances) [2].
*   **Comprensión de instrucciones de tarea:** Interpreta comandos complejos dados en lenguaje natural, traduciéndolos en objetivos accionables para el robot [2].
*   **Razonamiento espacial y temporal:** Posee la habilidad de comprender secuencias de acciones y cómo los objetos interactúan dentro de una escena a lo largo del tiempo, lo cual es crucial para la navegación y manipulación en entornos dinámicos [2].
*   **Visión Agéntica:** Esta es una característica distintiva que permite al modelo realizar pasos intermedios de razonamiento. Por ejemplo, puede hacer zoom en una imagen para discernir detalles finos en un instrumento, utilizar el apuntado y la ejecución de código para estimar proporciones e intervalos, y finalmente aplicar su conocimiento del mundo para interpretar el significado de la lectura [1].
*   **Orquestación de tareas:** Gemini Robotics-ER 1.6 puede descomponer comandos de alto nivel en una secuencia lógica de subtareas. Estas subtareas se ejecutan mediante la invocación de funciones de robot existentes, modelos de visión-lenguaje-acción (VLA) o cualquier otra función definida por el usuario, lo que le permite abordar tareas de largo horizonte [1] [2].

El modelo también incorpora un **"presupuesto de pensamiento" (thinking budget)** flexible, que permite a los desarrolladores controlar el equilibrio entre la latencia y la precisión. Para tareas de comprensión espacial más simples, como la detección de objetos, se puede utilizar un presupuesto pequeño para respuestas rápidas. Sin embargo, para tareas de razonamiento más complejas, como el conteo preciso o la estimación de peso, un presupuesto mayor mejora la precisión [2].

## 3. Implementación/Patrones Clave

La implementación de Gemini Robotics-ER 1.6 se centra en su accesibilidad y versatilidad para desarrolladores de robótica. El modelo está disponible a través de la API de Gemini y Google AI Studio, facilitando su integración en diversos proyectos [1] [2]. La transición desde versiones anteriores, como Gemini Robotics-ER 1.5, es sencilla, requiriendo únicamente el cambio del nombre del modelo en las llamadas a la API de `gemini-robotics-er-1.5-preview` a `gemini-robotics-er-1.6-preview` [2].

Los patrones de implementación clave y ejemplos de uso incluyen:

*   **Detección de objetos y apuntado:** Utilizando el método `generateContent` de la API, los desarrolladores pueden pasar una imagen y un prompt de texto para que el modelo identifique objetos y devuelva sus coordenadas 2D normalizadas (puntos `[y, x]` entre 0 y 1000) junto con sus etiquetas. Esto es fundamental para la interacción precisa del robot con su entorno [2].
*   **Detección de éxito:** Una capacidad crucial para la autonomía, que permite al robot determinar cuándo una tarea ha sido completada con éxito o si requiere un reintento. Esto es vital para la toma de decisiones inteligente en flujos de trabajo robóticos [1].
*   **Razonamiento multi-vista:** El modelo ha avanzado en la capacidad de procesar y correlacionar información de múltiples flujos de cámaras simultáneamente. Esto le permite construir una imagen coherente del entorno, incluso en condiciones dinámicas o con oclusiones, mejorando la percepción general del robot [1].
*   **Lectura de instrumentos:** Una aplicación destacada es la capacidad de leer e interpretar una variedad de instrumentos industriales, como manómetros circulares, indicadores de nivel y pantallas digitales. Esto se logra mediante la visión agéntica, donde el modelo realiza un zoom en la imagen, utiliza el apuntado y la ejecución de código para estimar valores y aplica su conocimiento del mundo para interpretar el significado de las lecturas [1].
*   **Ejecución de código:** Gemini Robotics-ER 1.6 puede generar y ejecutar código dinámicamente para realizar tareas específicas. Ejemplos incluyen el cálculo de niveles de líquido en contenedores, la lectura de marcas en placas de circuito impreso o la anotación de imágenes para instrucciones de eliminación [2].
*   **Orquestación de tareas:** El modelo demuestra una capacidad avanzada para la planificación de tareas de alto nivel. Puede inferir acciones y optimizar ubicaciones basándose en una comprensión contextual, lo que le permite orquestar tareas complejas y de largo horizonte, como organizar un espacio de trabajo o empacar una lonchera [2].

La **seguridad** es un pilar fundamental en el diseño de Gemini Robotics-ER 1.6. El modelo ha sido desarrollado con un enfoque en la seguridad en todos los niveles de su razonamiento encarnado. Demuestra un cumplimiento superior con las políticas de seguridad de Gemini en tareas de razonamiento espacial adversas y una capacidad mejorada para adherirse a restricciones de seguridad física, como evitar la manipulación de líquidos o el levantamiento de objetos que excedan un peso determinado [1].

## 4. Lecciones para el Monstruo

La arquitectura y las capacidades de Gemini Robotics-ER 1.6 ofrecen valiosas lecciones para el desarrollo de nuestro propio agente, "El Monstruo":

*   **Priorizar el Razonamiento Encarnado:** La capacidad de un agente para razonar intrínsecamente sobre el mundo físico y traducir la inteligencia digital en acciones concretas es indispensable para la autonomía en entornos complejos. El Monstruo debería integrar profundamente la percepción visual y espacial con sus módulos de toma de decisiones para una interacción más efectiva con el mundo real.
*   **Integrar Visión Agéntica y Ejecución de Código:** La combinación de razonamiento visual con la capacidad de generar y ejecutar código dinámicamente, como se observa en la lectura de instrumentos de Gemini Robotics-ER 1.6, es un patrón extremadamente potente. El Monstruo podría beneficiarse enormemente de una capacidad similar para interactuar con su entorno, procesar datos sensoriales de manera detallada y realizar tareas de precisión que requieran lógica programática.
*   **Desarrollar un Planificador de Tareas Robusto:** La habilidad de descomponer comandos de lenguaje natural en subtareas lógicas y orquestar su ejecución a través de un conjunto diverso de herramientas o funciones existentes es crucial para manejar tareas de largo horizonte. El Monstruo debería evolucionar su planificador para ser más adaptable y capaz de interactuar con una biblioteca extensible de herramientas.
*   **Fomentar el Razonamiento Multi-vista y la Detección de Éxito:** Para una comprensión contextual completa, El Monstruo debe ser capaz de procesar y fusionar información de múltiples fuentes sensoriales. Además, la capacidad de detectar autónomamente el éxito o fracaso de una acción es fundamental para la resiliencia, la auto-corrección y el aprendizaje continuo del agente.
*   **Implementar un Presupuesto de Pensamiento Adaptativo:** La estrategia de un "presupuesto de pensamiento" que ajusta el balance entre latencia y precisión según la complejidad de la tarea es una optimización inteligente. El Monstruo podría adoptar un mecanismo similar para asignar recursos computacionales de manera eficiente, priorizando la velocidad en tareas simples y la profundidad de análisis en tareas críticas.
*   **Diseñar con la Seguridad como Principio Fundamental:** La seguridad no debe ser una característica adicional, sino un principio de diseño inherente. La integración de políticas de seguridad y la capacidad de razonar sobre restricciones físicas son esenciales para cualquier agente que opere en el mundo real, garantizando un comportamiento seguro y confiable.

---
*Referencias:*
[1] Google DeepMind. (2026, 14 de abril). *Gemini Robotics ER 1.6: Enhanced Embodied Reasoning*. Recuperado de [https://deepmind.google/blog/gemini-robotics-er-1-6/](https://deepmind.google/blog/gemini-robotics-er-1-6/)
[2] Google AI for Developers. *Gemini Robotics-ER 1.6 | Gemini API*. Recuperado de [https://ai.google.dev/gemini-api/docs/robotics-overview](https://ai.google.dev/gemini-api/docs/robotics-overview)


---

# Biblia de Implementación: Gemini Robotics-ER 1.6 (Google DeepMind) — Fase 2

## Introducción

Gemini Robotics-ER 1.6, desarrollado por Google DeepMind, representa un avance significativo en la integración de capacidades de razonamiento visual y ejecución de código para la robótica autónoma. Este modelo está diseñado para permitir que los robots interpreten datos visuales complejos, realicen razonamiento espacial y planifiquen acciones a partir de comandos en lenguaje natural [1]. La versión 1.6 es una mejora sustancial respecto a sus predecesores, Gemini Robotics-ER 1.5 y Gemini 3.0 Flash, especialmente en la mejora de las capacidades de razonamiento espacial y físico, como el señalamiento, el conteo y la detección de éxito [1].

El objetivo de esta Fase 2 de la Biblia de Implementación es profundizar en los aspectos técnicos de Gemini Robotics-ER 1.6, desglosando su arquitectura y funcionalidades a través de módulos específicos. Se busca proporcionar una comprensión detallada de cómo opera el agente, sus herramientas, su entorno de ejecución, gestión de memoria, capacidades multimodales, integraciones, limitaciones y métricas de rendimiento.

## MÓDULO A: Ciclo del agente (loop/ReAct)

Gemini Robotics-ER 1.6 opera bajo un paradigma de **razonamiento encarnado (embodied reasoning)**, lo que implica que el robot no solo sigue instrucciones, sino que comprende y razona sobre el mundo físico para realizar tareas [1]. Este enfoque se alinea con el patrón de diseño **ReAct (Reasoning and Acting)**, donde el agente alterna entre pasos de razonamiento (pensar) y pasos de acción (ejecutar herramientas) para lograr un objetivo [2].

La arquitectura del ciclo del agente, tal como se ilustra en implementaciones que utilizan la API de Gemini, se compone de tres elementos principales [2]:

*   **Workflow (Flujo de Trabajo):** Este componente orquesta la lógica de ejecución del agente. Es el cerebro de alto nivel que descompone tareas complejas en subtareas lógicas y coordina su secuencia [1, 2]. Por ejemplo, para una tarea como 
"poner la manzana en el tazón", el flujo de trabajo descompone el comando en pasos lógicos y los integra con los controladores del robot [1].
*   **Activities (Actividades):** Son las unidades individuales de trabajo, como llamadas al LLM (Gemini) o llamadas a herramientas [2]. Estas actividades son las acciones que el agente decide tomar basándose en su razonamiento.
*   **Worker (Trabajador):** Es el proceso que ejecuta los flujos de trabajo y las actividades [2]. En un entorno de producción, este componente garantiza la durabilidad del agente, asegurando que cada llamada al LLM y cada invocación de herramienta se persista, permitiendo la recuperación en caso de fallos [2].

El ciclo del agente en Gemini Robotics-ER 1.6 se caracteriza por su capacidad de **visión agéntica (agentic vision)**, que combina el razonamiento visual con la ejecución de código [1]. Este enfoque es fundamental para la interacción del robot con el mundo físico, permitiéndole no solo percibir, sino también actuar de manera informada. Por ejemplo, en la tarea de lectura de instrumentos, el modelo no se limita a una simple interpretación visual. En cambio, adopta un enfoque de múltiples pasos:

1.  **Percepción Inicial y Enfoque:** El agente primero realiza un "zoom" virtual en la imagen del instrumento para obtener una vista más detallada de los pequeños elementos, como las marcas de la escala y las agujas [1]. Esta capacidad de enfoque dinámico es crucial para la precisión en la lectura.
2.  **Señalamiento y Cuantificación:** Utiliza el "señalamiento" (pointing) para identificar puntos clave en el instrumento, como la posición de la aguja o los límites de una escala [1]. A partir de estos puntos, el agente ejecuta código para estimar proporciones e intervalos, traduciendo la información visual en datos numéricos precisos. Esto puede implicar cálculos geométricos o interpolaciones para determinar un valor exacto.
3.  **Interpretación y Contextualización:** Finalmente, aplica su conocimiento del mundo para interpretar el significado de la lectura. Por ejemplo, si lee un manómetro, sabe que el valor numérico representa una presión y puede relacionarlo con los rangos operativos seguros o peligrosos [1].

Este proceso iterativo de percepción, razonamiento, ejecución de código y contextualización es un ejemplo claro del ciclo ReAct en acción, donde cada paso informa al siguiente y permite al agente abordar tareas complejas con alta precisión y autonomía.

## MÓDULO B: Estados del agente

El estado del agente en Gemini Robotics-ER 1.6 está intrínsecamente ligado a su capacidad de **detección de éxito (success detection)**, que actúa como el motor de toma de decisiones [1]. El agente evalúa continuamente su entorno y el progreso de la tarea para determinar su estado actual y la transición al siguiente. La fluidez entre estos estados es lo que permite al robot adaptarse a situaciones inesperadas y completar tareas complejas en entornos dinámicos.

Los estados principales del agente y sus transiciones incluyen:

1.  **Estado de Percepción y Razonamiento Inicial:**
    *   **Descripción:** El agente recibe una instrucción en lenguaje natural (por ejemplo, "recoge la taza azul") y datos sensoriales visuales (imágenes o video de su entorno) [1]. En este estado, el agente se enfoca en comprender los objetos presentes en la escena, sus relaciones espaciales y el contexto general, así como en interpretar la intención de la instrucción del usuario [1].
    *   **Transiciones:** Una vez que ha procesado la entrada y ha formado una comprensión inicial de la tarea y el entorno, transiciona al estado de Planificación y Descomposición.

2.  **Estado de Planificación y Descomposición:**
    *   **Descripción:** Basándose en su comprensión inicial, el agente descompone la instrucción compleja en una secuencia lógica de subtareas más manejables [1]. Este estado implica un razonamiento espacial y temporal profundo para prever cómo los objetos interactuarán entre sí y cómo se desarrollarán las acciones a lo largo del tiempo. Por ejemplo, para "poner la manzana en el tazón", podría planificar "identificar manzana", "identificar tazón", "alcanzar manzana", "agarrar manzana", "mover manzana sobre tazón", "soltar manzana" [1].
    *   **Transiciones:** Una vez que se ha generado un plan de acción coherente, el agente transiciona al estado de Ejecución de Acción.

3.  **Estado de Ejecución de Acción (Llamada a Herramienta/Código):**
    *   **Descripción:** En este estado, el agente ejecuta los pasos planificados. Esto implica invocar funciones específicas del robot (como comandos de movimiento o agarre), llamar a herramientas externas (como Google Search para obtener información adicional) o ejecutar código generado para realizar cálculos o manipulaciones de datos [1]. Cada acción es un intento de modificar el estado del mundo físico o de obtener más información.
    *   **Transiciones:** Después de ejecutar una acción, el agente transiciona al estado de Evaluación de Éxito para verificar el resultado de su acción.

4.  **Estado de Evaluación de Éxito (Success Detection):**
    *   **Descripción:** Este es un estado crítico donde el agente determina si la acción ejecutada ha logrado el resultado deseado y si la subtarea actual ha finalizado [1]. Utiliza su capacidad de razonamiento multi-vista para combinar información de múltiples cámaras (por ejemplo, una cámara cenital y una montada en la muñeca del robot) y evaluar si la acción fue exitosa, incluso en entornos dinámicos o con oclusiones [1]. Por ejemplo, si la tarea era "agarrar la manzana", el agente verificaría visualmente si la manzana está firmemente en la pinza del robot.
    *   **Transiciones:** Si la acción fue exitosa y la subtarea se completó, el agente puede transicionar de nuevo al estado de Planificación y Descomposición para abordar la siguiente subtarea, o al estado de Transición (Progreso) si la tarea principal ha finalizado. Si la acción falló, transiciona al estado de Transición (Reintento).

5.  **Estado de Transición (Reintento o Progreso):**
    *   **Descripción:** Basado en la evaluación de éxito, el agente toma una decisión estratégica. Si la acción falló, el agente decide inteligentemente reintentar la acción (posiblemente con parámetros ajustados o un enfoque diferente) o modificar su plan para superar el obstáculo [1]. Si la acción fue exitosa, el agente progresa a la siguiente etapa del plan o declara la finalización de la tarea si no quedan más subtareas.
    *   **Transiciones:** Desde aquí, el agente puede volver al estado de Planificación y Descomposición (para la siguiente subtarea o un plan revisado) o finalizar el ciclo si la tarea principal ha sido completada con éxito.

La **durabilidad** del estado del agente, especialmente en implementaciones robustas que utilizan frameworks como Temporal, es un factor clave [2]. Cada llamada al LLM, cada invocación de herramienta y cada paso del ciclo agéntico se persiste. Esto significa que si el proceso del agente se interrumpe debido a un fallo de hardware, un problema de red o un error en una API externa, el agente puede reanudar su operación desde el último paso completado. Esta persistencia asegura que "ningún historial de conversación se pierda" y que las llamadas a herramientas no se repitan incorrectamente, lo que es fundamental para la fiabilidad en entornos de producción [2].

## MÓDULO C: Sistema de herramientas

Gemini Robotics-ER 1.6 está diseñado para interactuar con el mundo físico y digital a través de un sistema de herramientas robusto. El modelo actúa como un modelo de razonamiento de alto nivel capaz de ejecutar tareas llamando nativamente a herramientas [1].

Las herramientas principales incluyen:

*   **Google Search:** Para buscar información externa necesaria para completar una tarea [1].
*   **Modelos de Visión-Lenguaje-Acción (VLAs):** Para generar acciones físicas específicas para el robot [1].
*   **Funciones Definidas por el Usuario (Third-party user-defined functions):** El agente puede llamar a funciones o herramientas existentes del robot [1].

En la implementación de la API de Gemini, las herramientas se definen utilizando objetos `FunctionDeclaration` [2]. Estas declaraciones especifican el nombre de la herramienta, una descripción detallada (extraída del docstring de la función) y los parámetros requeridos (definidos mediante modelos Pydantic) [2].

**Parámetros y Límites:**

*   **Thinking Budget (Presupuesto de Pensamiento):** Gemini Robotics-ER 1.6 introduce un presupuesto de pensamiento flexible que permite controlar el equilibrio entre latencia y precisión [1]. Para tareas de comprensión espacial simples como la detección de objetos, el modelo puede lograr un alto rendimiento con un presupuesto de pensamiento pequeño (incluso 0) [1]. Para tareas de razonamiento más complejas como el conteo y la estimación de peso, se beneficia de un presupuesto de pensamiento mayor [1].
*   **Formato de Salida Estructurado:** El agente puede proporcionar salidas estructuradas, como coordenadas (puntos o cajas delimitadoras) que representan ubicaciones de objetos [1]. Por ejemplo, puede devolver un JSON con el formato `[{"point": [y, x], "label": "nombre_objeto"}]`, donde los puntos están normalizados de 0 a 1000 [1].

## MÓDULO D: Ejecución de código

Una de las características distintivas de Gemini Robotics-ER 1.6 es su capacidad de **visión agéntica**, que combina el razonamiento visual con la ejecución de código [1]. Esta capacidad permite al agente realizar cálculos precisos y manipulaciones de datos que serían difíciles de lograr solo con razonamiento visual.

**Lenguajes y Entorno:**

*   El agente genera y ejecuta código, principalmente en **Python**, para realizar tareas intermedias [1].
*   En el ejemplo de lectura de instrumentos, el agente utiliza la ejecución de código para hacer zoom en una imagen, estimar proporciones e intervalos, y derivar la lectura de un medidor con precisión sub-marca [1].

**Manejo de Errores:**

*   La ejecución de código está integrada en el ciclo de razonamiento del agente. Si el código generado produce un error o un resultado inesperado, el agente puede utilizar su capacidad de detección de éxito para evaluar la situación y generar un nuevo código o ajustar su enfoque [1].
*   En implementaciones duraderas (como con Temporal), los errores en la ejecución de herramientas o código se manejan mediante reintentos automáticos, asegurando que el agente pueda recuperarse de fallos transitorios sin perder el progreso [2].

## MÓDULO E: Sandbox y entorno

El entorno de ejecución de Gemini Robotics-ER 1.6 depende de la implementación específica, pero generalmente opera en un entorno de nube o en el borde (edge) conectado a los sistemas de control del robot.

*   **Aislamiento y Seguridad:** En implementaciones que utilizan frameworks como Temporal, el código del flujo de trabajo se ejecuta en un **sandbox** (entorno aislado) [2]. Este sandbox restringe ciertas operaciones para garantizar el determinismo y la seguridad. Por ejemplo, el bloque `workflow.unsafe.imports_passed_through()` se utiliza para permitir explícitamente que ciertos módulos (como `httpx` o `pydantic`) pasen a través de las restricciones del sandbox [2].
*   **Recursos:** El agente requiere acceso a recursos computacionales significativos para el procesamiento visual y el razonamiento del LLM. La introducción del "Thinking Budget" permite a los desarrolladores gestionar el uso de recursos, optimizando para baja latencia o alta precisión según las necesidades de la tarea [1].

## MÓDULO F: Memoria y contexto

La gestión de la memoria y el contexto es fundamental para la capacidad de Gemini Robotics-ER 1.6 de realizar tareas de horizonte largo (long-horizon tasks) [1].

*   **Persistencia de Estado:** En implementaciones de producción, la persistencia del estado se logra mediante herramientas externas como Temporal, que registra cada llamada al LLM, cada invocación de herramienta y cada paso del ciclo agéntico [2]. Esto asegura que "ningún historial de conversación se pierda" y que el agente pueda reanudar su trabajo exactamente donde lo dejó en caso de interrupción [2].
*   **Ventana de Contexto:** Aunque la documentación específica no detalla el tamaño exacto de la ventana de contexto para la versión 1.6, los modelos Gemini de la serie 1.5 introdujeron ventanas de contexto masivas (hasta 1 o 2 millones de tokens). Es razonable asumir que Gemini Robotics-ER 1.6 hereda o mejora esta capacidad, permitiéndole procesar secuencias largas de video, múltiples imágenes de alta resolución y extensos historiales de interacción para mantener el contexto a lo largo de tareas complejas.
*   **Razonamiento Temporal:** El agente es capaz de razonar espacial y temporalmente, entendiendo secuencias de acciones y cómo los objetos interactúan con una escena a lo largo del tiempo [1]. Esto implica una forma de memoria a corto plazo integrada en su procesamiento visual.

## MÓDULO G: Browser/GUI

Gemini Robotics-ER 1.6 está diseñado principalmente para la interacción con el mundo físico a través de sensores robóticos (cámaras) y actuadores, más que para la navegación web tradicional o la interacción con interfaces gráficas de usuario (GUI) de software.

*   **Navegación Web:** Aunque el agente puede utilizar herramientas como Google Search para buscar información [1], su enfoque principal no es la automatización del navegador web (como hacer clic en enlaces o manejar inicios de sesión en páginas web).
*   **Interacción Visual:** En lugar de interactuar con elementos DOM de una página web, el agente interactúa con el mundo físico identificando objetos, determinando coordenadas espaciales (puntos y cajas delimitadoras) y planificando trayectorias de movimiento [1]. Su "clic" se traduce en acciones físicas, como señalar un objeto o dirigir un brazo robótico hacia una ubicación específica [1].

## MÓDULO H: Multi-agente

La arquitectura de Gemini Robotics-ER 1.6 sugiere un enfoque jerárquico que puede integrarse en sistemas multi-agente.

*   **Coordinación:** El modelo actúa como el "cerebro de alto nivel" o modelo de razonamiento para un robot [1]. Puede orquestar tareas complejas descomponiéndolas en subtareas y delegando la ejecución a modelos de nivel inferior, como los modelos de Visión-Lenguaje-Acción (VLAs) o controladores de robots específicos [1].
*   **Sub-agentes:** En este contexto, los VLAs o las funciones de control del robot actúan como sub-agentes especializados en la ejecución física, mientras que Gemini Robotics-ER 1.6 se encarga de la planificación, el razonamiento espacial y la evaluación del éxito [1].

## MÓDULO I: Integraciones

Gemini Robotics-ER 1.6 está diseñado para integrarse estrechamente con ecosistemas de robótica y herramientas de desarrollo de IA.

*   **API y SDK:** El modelo está disponible para los desarrolladores a través de la Gemini API y Google AI Studio [1]. Se puede acceder utilizando el SDK de Google GenAI en Python (`google-genai`) [1].
*   **Integración con Robots Físicos:** El modelo se ha probado y validado en colaboración con socios como Boston Dynamics, integrándose con robots como Spot para tareas de inspección de instalaciones [1].
*   **Llamadas a Herramientas Externas:** A través de su sistema de function calling, el agente puede integrarse con cualquier API externa (por ejemplo, para obtener datos meteorológicos o información de ubicación) definiendo las herramientas correspondientes [2].

## MÓDULO J: Multimodal

Las capacidades multimodales son el núcleo de Gemini Robotics-ER 1.6, permitiéndole procesar y razonar sobre información del mundo real.

*   **Procesamiento de Imágenes y Video:** El modelo es un Vision-Language Model (VLM) avanzado [1]. Toma entradas de imagen, video y audio junto con prompts en lenguaje natural [1].
*   **Razonamiento Multi-vista:** Una capacidad destacada es su avance en el razonamiento multi-vista, que permite al sistema comprender múltiples flujos de cámara (por ejemplo, vista cenital y de muñeca) y la relación entre ellos, incluso en entornos dinámicos u ocluidos [1].
*   **Modelos Subyacentes:** Gemini Robotics-ER 1.6 se basa en la arquitectura fundamental de los modelos Gemini de Google DeepMind, optimizada específicamente para tareas de robótica (Embodied Reasoning) [1].

## MÓDULO K: Límites y errores

A pesar de sus avances, Gemini Robotics-ER 1.6 opera dentro de ciertas limitaciones y cuenta con mecanismos para manejar errores.

*   **Límites de Percepción:** Lograr la comprensión visual en robótica es un desafío debido a factores complicados como oclusiones, mala iluminación e instrucciones ambiguas [1]. Aunque la versión 1.6 mejora en estas áreas, situaciones extremas aún pueden provocar fallos en la percepción.
*   **Seguridad y Restricciones Físicas:** El modelo ha mejorado sustancialmente su capacidad para adherirse a restricciones de seguridad física. Por ejemplo, toma decisiones más seguras sobre qué objetos pueden ser manipulados de forma segura bajo restricciones de pinzas o materiales (por ejemplo, "no manipular líquidos", "no recoger objetos de más de 20 kg") [1].
*   **Recuperación de Errores:** La capacidad de "Success Detection" es el mecanismo principal para la recuperación de errores. Si el agente detecta que una tarea no se ha completado con éxito, puede decidir reintentar la acción o ajustar su plan [1].

## MÓDULO L: Benchmarks

Google DeepMind ha evaluado Gemini Robotics-ER 1.6 frente a versiones anteriores y otros modelos, demostrando mejoras significativas en tareas clave de robótica.

*   **Mejoras Generales:** El modelo muestra una mejora significativa sobre Gemini Robotics-ER 1.5 y Gemini 3.0 Flash en capacidades de razonamiento espacial y físico, como el señalamiento, el conteo y la detección de éxito [1].
*   **Lectura de Instrumentos:** En tareas de lectura de instrumentos (evaluadas con visión agéntica habilitada), Gemini Robotics-ER 1.6 logra lecturas altamente precisas de medidores analógicos, indicadores de nivel vertical y lecturas digitales modernas [1]. Reportes externos indican que el modelo alcanzó un 93% de precisión en la lectura de medidores industriales mediante visión agéntica, un salto de 70 puntos sobre la versión 1.5.
*   **Seguridad:** En pruebas de seguimiento de instrucciones de seguridad (Safety Instruction Following), la versión 1.6 mejora sustancialmente en comparación con la 1.5 en la capacidad de adherirse a restricciones de seguridad física [1]. También mejora sobre el rendimiento base de Gemini 3.0 Flash en la identificación precisa de riesgos de lesiones en escenarios de texto (+6%) y video (+10%) [1].

## Lecciones para el Monstruo

Basado en la investigación de Gemini Robotics-ER 1.6, aquí hay 5 lecciones clave para el diseño e implementación de agentes de IA avanzados:

1.  **La Visión Agéntica es el Futuro del Razonamiento Físico:** La combinación de razonamiento visual puro con la ejecución de código (como se ve en la lectura de instrumentos) permite a los agentes superar las limitaciones de la estimación visual directa, logrando una precisión sub-métrica mediante el cálculo matemático de proporciones e intervalos.
2.  **La Detección de Éxito (Success Detection) es el Motor de la Autonomía:** Un agente verdaderamente autónomo no solo debe saber cómo ejecutar una acción, sino también cómo evaluar si la acción logró el resultado deseado. Implementar bucles de retroalimentación robustos basados en la percepción multi-vista es crucial para la recuperación de errores y la toma de decisiones dinámicas.
3.  **El Presupuesto de Pensamiento (Thinking Budget) Optimiza el Rendimiento:** Permitir que el agente ajuste dinámicamente la cantidad de esfuerzo de razonamiento (y por ende, la latencia y el costo computacional) según la complejidad de la tarea es una estrategia de diseño esencial para sistemas que operan en tiempo real en el mundo físico.
4.  **La Durabilidad del Estado es No Negociable para Tareas de Horizonte Largo:** En entornos de producción, depender únicamente de la memoria interna del LLM es insuficiente. La integración con sistemas de orquestación de flujos de trabajo (como Temporal) para persistir cada paso del ciclo ReAct garantiza que el agente pueda recuperarse de fallos de red o de hardware sin perder el contexto.
5.  **La Seguridad Debe Estar Integrada en el Razonamiento Espacial:** Para los agentes encarnados, la seguridad no es solo un filtro de contenido, sino una restricción física. El modelo debe ser capaz de razonar sobre las propiedades físicas de los objetos (peso, estado, fragilidad) y las limitaciones de sus propios actuadores antes de planificar una trayectoria o un agarre.

## Referencias

[1] Google DeepMind. (2026, April 14). *Gemini Robotics ER 1.6: Enhanced Embodied Reasoning*. Recuperado de https://deepmind.google/blog/gemini-robotics-er-1-6/
[2] Temporal Community. (n.d.). *Build a durable AI agent with Gemini and Temporal*. GitHub Repository. Recuperado de https://github.com/temporal-community/durable-react-agent-gemini
[3] Google AI for Developers. (n.d.). *Gemini Robotics-ER 1.6 | Gemini API*. Recuperado de https://ai.google.dev/gemini-api/docs/robotics-overview

---

## Fase 3 — Módulos Complementarios: Gemini Robotics-ER 1.6 (Google DeepMind)

### Integraciones y Connectors

Gemini Robotics-ER 1.6, desarrollado por Google DeepMind, se posiciona como un modelo de lenguaje y visión (VLM) avanzado que extiende las capacidades agenticas de Gemini al ámbito de la robótica. Su diseño fundamental permite la interpretación de datos visuales complejos, el razonamiento espacial y la planificación de acciones a partir de comandos en lenguaje natural [1]. La clave de su versatilidad y capacidad de integración reside en su robusto mecanismo de **llamada a funciones (Function Calling)** y en la disponibilidad de un **SDK (Software Development Kit)** específico para robótica.

El sistema de llamada a funciones de Gemini Robotics-ER 1.6 es un pilar central para sus capacidades de integración. Este mecanismo permite que el modelo no solo genere respuestas textuales, sino que también determine cuándo y cómo invocar herramientas y APIs externas, proporcionando los parámetros necesarios para ejecutar acciones en el mundo real [3]. Esto transforma al modelo en un puente entre el lenguaje natural y las acciones concretas, facilitando tres casos de uso principales:

*   **Aumento del Conocimiento:** Acceder a información de fuentes externas como bases de datos, APIs y bases de conocimiento para enriquecer la comprensión del modelo.
*   **Extensión de Capacidades:** Utilizar herramientas externas para realizar cálculos complejos o superar las limitaciones inherentes del modelo, como el uso de una calculadora o la creación de gráficos.
*   **Ejecución de Acciones:** Interactuar con sistemas externos a través de APIs para llevar a cabo tareas como programar citas, generar facturas, enviar correos electrónicos o controlar dispositivos inteligentes [3].

El proceso de llamada a funciones se estructura en varios pasos. Primero, el desarrollador define una **declaración de función** en el código de la aplicación, especificando el nombre, los parámetros y el propósito de la función. Luego, se envía el *prompt* del usuario junto con estas declaraciones de función al modelo. El modelo analiza la solicitud y decide si una llamada a función sería útil. Si es así, responde con un objeto JSON estructurado que contiene el nombre de la función, los argumentos y un `id` único. Es responsabilidad de la aplicación ejecutar el código de la función correspondiente, procesar el resultado y enviarlo de vuelta al modelo, incluyendo el `id` coincidente, en una interacción subsiguiente. El modelo utiliza este resultado para generar una respuesta final amigable para el usuario [3]. Este flujo puede repetirse en múltiples turnos, permitiendo interacciones y flujos de trabajo complejos. Además, el modelo soporta la llamada a múltiples funciones en un solo turno (**llamada a funciones paralela**), en secuencia (**llamada a funciones composicional**) y el uso de múltiples herramientas (combinando herramientas integradas de Gemini con llamadas a funciones) [3].

El **Gemini Robotics SDK** (disponible en GitHub bajo `google-deepmind/gemini-robotics-sdk`) es una herramienta fundamental que proporciona las funcionalidades necesarias para el ciclo de vida completo de los modelos Gemini Robotics. Esto incluye el acceso a puntos de control, el despliegue de modelos, la evaluación en robots y simulaciones, la carga de datos, el *finetuning* de modelos y la descarga de puntos de control ajustados [4]. El SDK incorpora un **framework de agentes** integral para construir agentes robóticos interactivos impulsados por modelos Gemini. Este framework se compone de:

*   **Agentes (`safari_sdk/agent/framework/agents/`):** Clases base de agentes que se integran con la API de Gemini Live para proporcionar interacción conversacional y capacidades de uso de herramientas.
*   **Embodiments (`safari_sdk/agent/framework/embodiments/`):** Interfaces específicas de hardware que conectan a los agentes con sistemas robóticos físicos (por ejemplo, el robot Aloha). Cada *embodiment* proporciona herramientas para el control del robot.
*   **Herramientas (`safari_sdk/agent/framework/tools/`):** Capacidades modulares que los agentes pueden utilizar, como 
ejecución de instrucciones, detección de éxito y descripción de escenas.
*   **Event Bus (`safari_sdk/agent/framework/event_bus/`):** Un sistema asíncrono de publicación-suscripción para la comunicación entre los componentes del agente.
*   **Configuración (`safari_sdk/agent/framework/config.py`):** Gestión centralizada de la configuración utilizando `AgentFrameworkConfig`, que soporta tanto la configuración programática como la basada en flags [4].

La integración con **Google Cloud** es un aspecto crucial para Gemini Robotics-ER 1.6. Se ha observado una colaboración con Google Cloud para integrar Gemini y Gemini Robotics-ER 1.6 en plataformas como Orbit AIVI-Learning [5]. Además, los modelos Gemini de Google, incluyendo los de robótica, están disponibles en vista previa en Google Distributed Cloud, lo que permite a los clientes ejecutar estos modelos en hardware de NVIDIA Blackwell y Blackwell Ultra GPUs [6]. Esto sugiere una infraestructura robusta para el despliegue y la ejecución de modelos de robótica a gran escala, aprovechando la potencia de cálculo y los servicios gestionados de Google Cloud.

En cuanto a la integración con **ROS (Robot Operating System)**, la documentación oficial y los repositorios de Google DeepMind no mencionan explícitamente una integración directa o un paquete ROS para Gemini Robotics-ER 1.6. Sin embargo, la naturaleza del SDK, que permite la ejecución de funciones y la interacción con APIs externas, sugiere que la integración con ROS sería posible a través de la creación de *wrappers* o nodos ROS personalizados que interactúen con el SDK de Gemini Robotics. Por ejemplo, el SDK proporciona interfaces específicas de hardware (Embodiments) que conectan a los agentes con sistemas robóticos físicos, y estas interfaces podrían ser adaptadas para comunicarse con el ecosistema ROS. La capacidad de Gemini Robotics-ER 1.6 para descomponer comandos en sub-tareas y ejecutar funciones/código existente [1] facilita la interoperabilidad con sistemas robóticos que ya utilizan ROS para el control de bajo nivel y la comunicación entre componentes. La comunidad de robótica ha explorado la compatibilidad de herramientas de Google DeepMind, como MuJoCo, con ROS [7], lo que indica un interés y una vía potencial para futuras integraciones directas o desarrollos comunitarios. La flexibilidad del SDK y el enfoque en la ejecución de acciones a través de APIs permiten a los desarrolladores integrar Gemini Robotics-ER 1.6 en entornos ROS existentes, utilizando ROS como el middleware para la comunicación entre el agente de Gemini y los actuadores y sensores del robot.

**Referencias:**
[1] Google AI for Developers. (s.f.). *Gemini Robotics-ER 1.6*. Recuperado de [https://ai.google.dev/gemini-api/docs/robotics-overview](https://ai.google.dev/gemini-api/docs/robotics-overview)
[2] Google DeepMind. (s.f.). *Gemini Robotics*. Recuperado de [https://deepmind.google/models/gemini-robotics/](https://deepmind.google/models/gemini-robotics/)
[3] Google AI for Developers. (s.f.). *Function calling with the Gemini API*. Recuperado de [https://ai.google.dev/gemini-api/docs/function-calling](https://ai.google.dev/gemini-api/docs/function-calling)
[4] google-deepmind. (s.f.). *gemini-robotics-sdk*. GitHub. Recuperado de [https://github.com/google-deepmind/gemini-robotics-sdk](https://github.com/google-deepmind/gemini-robotics-sdk)
[5] Boston Dynamics. (s.f.). *AIVI-Learning Is Now Powered by Google Gemini Robotics*. Recuperado de [https://bostondynamics.com/blog/aivi-learning-now-powered-google-gemini-robotics/](https://bostondynamics.com/blog/aivi-learning-now-powered-google-gemini-robotics/)
[6] NVIDIA. (2026, 22 de abril). *NVIDIA and Google Cloud Collaborate to Advance Agentic Physical AI Factories*. Recuperado de [https://blogs.nvidia.com/blog/google-cloud-agentic-physical-ai-factories/](https://blogs.nvidia.com/blog/google-cloud-agentic-physical-ai-factories/)
[7] google-deepmind. (s.f.). *ROS-Compatibility #990*. GitHub. Recuperado de [https://github.com/google-deepmind/mujoco/discussions/990](https://github.com/google-deepmind/mujoco/discussions/990)

## Fase 3 — Módulos Complementarios: Gemini Robotics-ER 1.6 (Google DeepMind)

### Límites, Fallas y Manejo de Errores

Gemini Robotics-ER 1.6, como modelo de razonamiento encarnado (Embodied Reasoning) de Google DeepMind, está diseñado para mejorar la capacidad de los robots para operar en el mundo físico. A pesar de sus avances significativos en la interpretación de datos visuales, el razonamiento espacial y la planificación de acciones, es crucial comprender sus límites inherentes y los mecanismos que emplea para la detección y recuperación de errores. La seguridad es un pilar fundamental en su desarrollo, y se ha enfatizado que es el modelo de robótica más seguro hasta la fecha dentro de la línea ER, demostrando una conformidad superior con las políticas de seguridad de Gemini en tareas de razonamiento espacial adversas [1].

**Limitaciones Intrínsecas y Desafíos:**

Aunque Gemini Robotics-ER 1.6 representa un salto cualitativo en la robótica, no está exento de limitaciones. Como cualquier modelo de IA generativa, puede cometer errores, y en el contexto de la robótica física, estos errores pueden tener consecuencias tangibles [1]. Las principales limitaciones se derivan de la complejidad del mundo real y la naturaleza de la percepción y el razonamiento:

*   **Fallos de Percepción:** A pesar de su capacidad para interpretar entradas de imagen, video y audio, el modelo puede enfrentar desafíos en entornos altamente dinámicos, con oclusiones severas, iluminación deficiente o situaciones ambiguas que pueden llevar a interpretaciones erróneas del entorno. La precisión en la detección de objetos y el razonamiento espacial es alta, pero no infalible, especialmente en escenarios no vistos durante el entrenamiento.
*   **Generalización en Tareas Novedosas:** Si bien el modelo está diseñado para generalizar su comportamiento a nuevas situaciones y descomponer objetivos en pasos manejables [2], la capacidad de manejar tareas completamente novedosas o entornos radicalmente diferentes a los de su entrenamiento puede ser un desafío. La robustez ante la variabilidad ilimitada del mundo real sigue siendo un área activa de investigación.
*   **Restricciones Físicas y de Hardware:** El modelo opera dentro de las limitaciones físicas del robot al que está integrado. Factores como la precisión de los actuadores, la resolución de los sensores, la capacidad de carga y la destreza de los efectores finales (manos o pinzas) pueden imponer límites a las acciones que el robot puede realizar, independientemente de la capacidad de razonamiento del modelo. El modelo puede respetar restricciones físicas como "no manipular líquidos" o "no levantar objetos pesados" [8], pero la implementación de estas restricciones depende de la configuración y las capacidades del robot.
*   **Dependencia de Datos de Entrenamiento:** Como modelo basado en aprendizaje profundo, su rendimiento está intrínsecamente ligado a la calidad y diversidad de los datos de entrenamiento. Sesgos o lagunas en los datos pueden manifestarse como errores o comportamientos inesperados en situaciones específicas.

**Detección y Manejo de Errores:**

Gemini Robotics-ER 1.6 incorpora mecanismos para la detección y el manejo de errores, centrándose en la seguridad y la fiabilidad. Uno de los aspectos clave es su capacidad de **razonamiento encarnado mejorado**, que le permite comprender el contexto espacial y temporal de las acciones. Esto incluye:

*   **Comprensión del Contexto de Objetos y Escenas:** Identifica objetos y razona sobre sus relaciones con la escena, incluyendo sus *affordances* (posibilidades de acción) [1]. Esto es fundamental para detectar inconsistencias o situaciones anómalas. Por ejemplo, si un objeto se encuentra en una posición inesperada o si una acción propuesta violaría las propiedades físicas de los objetos, el modelo puede identificarlo como un posible error.
*   **Razonamiento Espacial y Temporal:** Comprende secuencias de acciones y cómo los objetos interactúan con una escena a lo largo del tiempo [1]. Esta capacidad le permite monitorear el progreso de una tarea y detectar desviaciones del plan esperado. Si una acción no produce el resultado anticipado o si el estado del entorno no coincide con el estado predicho, el modelo puede inferir un fallo.
*   **Auto-corrección mediante Razonamiento Multi-vista:** Una característica destacada de Gemini Robotics-ER 1.6 es su capacidad para **auto-corregirse utilizando razonamiento multi-vista** [9]. Esto significa que el modelo puede integrar información de múltiples cámaras o sensores para obtener una comprensión más completa y robusta del entorno. Si una vista es ambigua o proporciona información contradictoria, el modelo puede recurrir a otras vistas para validar o corregir su percepción, lo que reduce la probabilidad de fallos de percepción y mejora la precisión en tareas delicadas como la lectura de medidores analógicos [9].
*   **Detección de Éxito:** El modelo puede determinar cuándo una tarea, como "poner el bolígrafo azul en el portalápices negro", se ha completado con éxito, tomando señales de múltiples vistas de cámara [10]. Esta capacidad es crucial para evitar la ejecución redundante de acciones o para identificar si una acción ha fallado en alcanzar su objetivo.

**Mecanismos de Recuperación:**

Los mecanismos de recuperación en Gemini Robotics-ER 1.6 se basan en su capacidad agentica y de planificación. Al descomponer comandos complejos en subtareas y orquestar tareas de largo horizonte, el modelo puede:

*   **Replanificación:** Si se detecta un error o una desviación del plan, el modelo puede reevaluar la situación y generar un nuevo plan de acción para alcanzar el objetivo. Su capacidad para "pensar antes de actuar" y su flexibilidad para adaptarse a cambios en el entorno [2] son fundamentales para esta replanificación.
*   **Uso de Herramientas (Tool Use):** En caso de un fallo, el modelo puede invocar herramientas externas o funciones predefinidas para intentar resolver el problema. Por ejemplo, si un objeto no se detecta correctamente, podría invocar una función de escaneo más detallada o ajustar los parámetros de percepción. La capacidad de llamar a APIs de robótica existentes o ejecutar código generado [1] es vital para esta flexibilidad.
*   **Interacción con el Usuario:** El modelo está diseñado para comprender y responder a comandos cotidianos, y puede explicar su enfoque mientras actúa. Los usuarios pueden redirigirlo en cualquier momento sin usar lenguaje técnico [2]. Esta interactividad permite la intervención humana en caso de fallos que el robot no pueda resolver autónomamente, facilitando la recuperación asistida.

**Timeouts y Presupuesto de Pensamiento (Thinking Budget):**

Gemini Robotics-ER 1.6 introduce un concepto de **presupuesto de pensamiento flexible** que permite controlar el equilibrio entre latencia y precisión [1]. Para tareas de comprensión espacial como la detección de objetos, el modelo puede lograr un alto rendimiento con un presupuesto de pensamiento pequeño, lo que resulta en respuestas de baja latencia. Sin embargo, para tareas de razonamiento más complejas, como el conteo o la estimación de peso, un presupuesto de pensamiento mayor beneficia la precisión. Esto permite a los desarrolladores ajustar el comportamiento del modelo según los requisitos de la aplicación, priorizando la velocidad o la exactitud según sea necesario [1]. Este "thinking budget" actúa como un mecanismo de control implícito sobre los "timeouts" en el proceso de razonamiento, permitiendo que el sistema evite bucles infinitos de deliberación y tome decisiones dentro de un marco de tiempo aceptable para aplicaciones robóticas en tiempo real.

**Referencias:**
[1] Google AI for Developers. (s.f.). *Gemini Robotics-ER 1.6*. Recuperado de [https://ai.google.dev/gemini-api/docs/robotics-overview](https://ai.google.dev/gemini-api/docs/robotics-overview)
[2] Google DeepMind. (s.f.). *Gemini Robotics*. Recuperado de [https://deepmind.google/models/gemini-robotics/](https://deepmind.google/models/gemini-robotics/)
[3] Google AI for Developers. (s.f.). *Function calling with the Gemini API*. Recuperado de [https://ai.google.dev/gemini-api/docs/function-calling](https://ai.google.dev/gemini-api/docs/function-calling)
[4] google-deepmind. (s.f.). *gemini-robotics-sdk*. GitHub. Recuperado de [https://github.com/google-deepmind/gemini-robotics-sdk](https://github.com/google-deepmind/gemini-robotics-sdk)
[5] Boston Dynamics. (s.f.). *AIVI-Learning Is Now Powered by Google Gemini Robotics*. Recuperado de [https://bostondynamics.com/blog/aivi-learning-now-powered-google-gemini-robotics/](https://bostondynamics.com/blog/aivi-learning-now-powered-google-gemini-robotics/)
[6] NVIDIA. (2026, 22 de abril). *NVIDIA and Google Cloud Collaborate to Advance Agentic Physical AI Factories*. Recuperado de [https://blogs.nvidia.com/blog/google-cloud-agentic-physical-ai-factories/](https://blogs.nvidia.com/blog/google-cloud-agentic-physical-ai-factories/)
[7] google-deepmind. (s.f.). *ROS-Compatibility #990*. GitHub. Recuperado de [https://github.com/google-deepmind/mujoco/discussions/990](https://github.com/google-deepmind/mujoco/discussions/990)
[8] Theermann, L. (s.f.). *Google DeepMind just released Gemini Robotics-ER 1.6*. LinkedIn. Recuperado de [https://www.linkedin.com/posts/theermann_google-deepmind-just-released-gemini-robotics-er-activity-7454522274553999360-SXoa](https://www.linkedin.com/posts/theermann_google-deepmind-just-released-gemini-robotics-er-activity-7454522274553999360-SXoa)
[9] Google. (s.f.). *Google just fixed the biggest flaw in robotic spatial reasoning*. Instagram. Recuperado de [https://www.instagram.com/p/DXKarr9E-kF/](https://www.instagram.com/p/DXKarr9E-kF/)
[10] AI for Success. (2026, 14 de abril). *Google has released Gemini Robotics-ER 1.6*. X. Recuperado de [https://x.com/ai_for_success/status/2044093911778636010](https://x.com/ai_for_success/status/2044093911778636010)

## Fase 3 — Módulos Complementarios: Gemini Robotics-ER 1.6 (Google DeepMind)

### Benchmarks y Métricas de Rendimiento

La evaluación del rendimiento de modelos de IA en robótica es fundamental para comprender sus capacidades y limitaciones en entornos del mundo real. Gemini Robotics-ER 1.6, el modelo de razonamiento encarnado de Google DeepMind, ha sido sometido a diversas pruebas y comparaciones para demostrar sus avances. Los benchmarks se centran en la mejora de las capacidades de razonamiento espacial y físico, la detección de éxito y la lectura de instrumentos, en comparación con sus predecesores y otros modelos relevantes [1].

**Comparación con Modelos Anteriores (Gemini Robotics-ER 1.5 y Gemini 3.0 Flash):**

Gemini Robotics-ER 1.6 muestra una mejora significativa en comparación con Gemini Robotics-ER 1.5 y Gemini 3.0 Flash, especialmente en tareas que requieren razonamiento espacial y físico, como el señalamiento, el conteo y la detección de éxito [1].

Un ejemplo concreto de esta mejora se observa en tareas de **detección y conteo de objetos**. En una evaluación donde se solicitó al modelo identificar y contar objetos en una imagen, Gemini Robotics-ER 1.6:

*   Identificó correctamente 2 martillos, 1 tijera, 1 pincel y 6 alicates.
*   No señaló objetos que no estaban presentes en la imagen, como una carretilla o un taladro Ryobi.

En contraste, Gemini Robotics-ER 1.5 falló en identificar el número correcto de martillos y pinceles, omitió completamente las tijeras, "alucinó" una carretilla y careció de precisión en el señalamiento de los alicates. Gemini 3.0 Flash, aunque cercano a Gemini Robotics-ER 1.6, no manejó los alicates con la misma eficacia [1].

En el ámbito de la **detección de riesgos de seguridad**, los modelos Gemini Robotics-ER superan el rendimiento de referencia de Gemini 3.0 Flash en la percepción precisa de riesgos de lesiones, mostrando una mejora del **+6% en escenarios de texto y +10% en escenarios de video** [1]. Además, Gemini Robotics-ER 1.6 mejora sustancialmente en comparación con Gemini Robotics-ER 1.5 en la **adhesión a instrucciones de seguridad**, que evalúa la capacidad de seguir restricciones físicas. También mejora a Gemini 3.0 Flash en el señalamiento, y ambos modelos muestran una alta precisión para el texto. Gemini 3.0 Flash, sin embargo, tiene un mejor rendimiento en la delimitación de cuadros (bounding boxes) [1].

**Lectura de Instrumentos:**

Una nueva capacidad destacada en Gemini Robotics-ER 1.6 es la **lectura de instrumentos**, que permite a los robots interpretar medidores complejos y visores de nivel. Esta capacidad es crucial para tareas de inspección en instalaciones industriales. El modelo logra lecturas de instrumentos altamente precisas utilizando una "visión agentica", que combina el razonamiento visual con la ejecución de código. Esto implica pasos intermedios como hacer zoom en una imagen para leer pequeños detalles, usar el señalamiento y la ejecución de código para estimar proporciones e intervalos y aplicar su conocimiento del mundo para interpretar el significado [1].

**Relación con Open X-Embodiment y RT-2:**

Aunque la documentación específica de Gemini Robotics-ER 1.6 no detalla su rendimiento directo en benchmarks como SWE-bench, WebArena, OSWorld o GAIA, es importante considerar el contexto más amplio de la investigación en robótica de Google DeepMind, que incluye iniciativas como **Open X-Embodiment** y modelos como **RT-2**.

El proyecto **Open X-Embodiment** es una iniciativa que busca la consolidación de modelos pre-entrenados en robótica, similar a lo que ha ocurrido en PNL y Visión por Computadora. Ha compilado el conjunto de datos de robots reales de código abierto más grande hasta la fecha, con más de 1 millón de trayectorias de robots reales que abarcan 22 *embodiments* de robots diferentes. Sobre este conjunto de datos, se entrenan modelos como RT-1 y RT-2. **RT-2** es un modelo de lenguaje y visión a gran escala co-ajustado para generar acciones de robot como tokens de lenguaje natural [11].

La relevancia de Open X-Embodiment y RT-2 para Gemini Robotics-ER 1.6 radica en que proporcionan un marco para el desarrollo de políticas robóticas generalistas y la transferencia de aprendizaje entre diferentes plataformas robóticas. Si bien Gemini Robotics-ER 1.6 se enfoca en el razonamiento encarnado y la comprensión espacial, la capacidad de integrar y ejecutar acciones a través de APIs (como se describe en la sección de Integraciones y Connectors) sugiere que podría interactuar con sistemas basados en RT-2 o beneficiarse de los principios de aprendizaje por transferencia explorados en Open X-Embodiment. Por ejemplo, la capacidad de Gemini Robotics-ER 1.6 para adaptarse a una "diversa gama de formas de robot" [2] se alinea con el objetivo de Open X-Embodiment de crear políticas robóticas que puedan adaptarse eficientemente a nuevos robots, tareas y entornos.

Aunque no se proporcionan números directos de Gemini Robotics-ER 1.6 en RT-2 o Open X-Embodiment, la filosofía de diseño de Gemini Robotics-ER 1.6, que enfatiza la generalidad y la capacidad de aprender a través de diferentes *embodiments*, es consistente con los objetivos de estas iniciativas. La mejora continua en el razonamiento espacial y la detección de éxito en Gemini Robotics-ER 1.6 contribuye directamente a la construcción de agentes robóticos más capaces y adaptables, que son el objetivo final de benchmarks como Open X-Embodiment.

**Referencias:**
[1] Google DeepMind. (2026, 14 de abril). *Gemini Robotics ER 1.6: Enhanced Embodied Reasoning*. Recuperado de [https://deepmind.google/blog/gemini-robotics-er-1-6/](https://deepmind.google/blog/gemini-robotics-er-1-6/)
[2] Google DeepMind. (s.f.). *Gemini Robotics*. Recuperado de [https://deepmind.google/models/gemini-robotics/](https://deepmind.google/models/gemini-robotics/)
[3] Google AI for Developers. (s.f.). *Function calling with the Gemini API*. Recuperado de [https://ai.google.dev/gemini-api/docs/function-calling](https://ai.google.dev/gemini-api/docs/function-calling)
[4] google-deepmind. (s.f.). *gemini-robotics-sdk*. GitHub. Recuperado de [https://github.com/google-deepmind/gemini-robotics-sdk](https://github.com/google-deepmind/gemini-robotics-sdk)
[5] Boston Dynamics. (s.f.). *AIVI-Learning Is Now Powered by Google Gemini Robotics*. Recuperado de [https://bostondynamics.com/blog/aivi-learning-now-powered-google-gemini-robotics/](https://bostondynamics.com/blog/aivi-learning-now-powered-google-gemini-robotics/)
[6] NVIDIA. (2026, 22 de abril). *NVIDIA and Google Cloud Collaborate to Advance Agentic Physical AI Factories*. Recuperado de [https://blogs.nvidia.com/blog/google-cloud-agentic-physical-ai-factories/](https://blogs.nvidia.com/blog/google-cloud-agentic-physical-ai-factories/)
[7] google-deepmind. (s.f.). *ROS-Compatibility #990*. GitHub. Recuperado de [https://github.com/google-deepmind/mujoco/discussions/990](https://github.com/google-deepmind/mujoco/discussions/990)
[8] Theermann, L. (s.f.). *Google DeepMind just released Gemini Robotics-ER 1.6*. LinkedIn. Recuperado de [https://www.linkedin.com/posts/theermann_google-deepmind-just-released-gemini-robotics-er-activity-7454522274553999360-SXoa](https://www.linkedin.com/posts/theermann_google-deepmind-just-released-gemini-robotics-er-activity-7454522274553999360-SXoa)
[9] Google. (s.f.). *Google just fixed the biggest flaw in robotic spatial reasoning*. Instagram. Recuperado de [https://www.instagram.com/p/DXKarr9E-kF/](https://www.instagram.com/p/DXKarr9E-kF/)
[10] AI for Success. (2026, 14 de abril). *Google has released Gemini Robotics-ER 1.6*. X. Recuperado de [https://x.com/ai_for_success/status/2044093911778636010](https://x.com/ai_for_success/status/2044093911778636010)
[11] Open X-Embodiment. (s.f.). *Open X-Embodiment: Robotic Learning Datasets and RT-X Models*. Recuperado de [https://robotics-transformer-x.github.io/](https://robotics-transformer-x.github.io/)


## Hallazgos Técnicos en GitHub (Fase 5)

# Hallazgos Técnicos del Agente Gemini Robotics-ER 1.6

## Agente Investigado

**Gemini Robotics-ER 1.6** (google-deepmind/gemini-robotics-sdk en GitHub) — agente de robótica de Google DeepMind

## URL del Repositorio Oficial

`https://github.com/google-deepmind/gemini-robotics-sdk`

## Actividad del Repositorio

El repositorio se encuentra **activo**, con la última actividad registrada hace 6 días (al 1 de mayo de 2026), lo que indica un desarrollo continuo y reciente. Las actualizaciones frecuentes son principalmente sincronizaciones del SDK a nuevas versiones.

## Arquitectura Interna

El **Safari SDK** está estructurado como un paquete `pip` de Python, con una dependencia interna clave: `safari-sdk-logging`. Esta dependencia maneja el código de registro en C++ y `pybind11`. Ambos paquetes utilizan el espacio de nombres de nivel superior `safari_sdk`, siguiendo la [PEP 420 – Implicit Namespace Packages](https://peps.python.org/pep-0420/).

La decisión de separar `safari-sdk` y `safari-sdk-logging` en paquetes distintos se debe a la optimización del tiempo de compilación. Las dependencias de C++ pueden tardar más de 30 minutos en compilarse desde el código fuente. Al separarlas, se permite el uso de versiones precompiladas, reduciendo el tiempo de instalación del paquete base `safari-sdk` a unos pocos segundos, siempre que no haya cambios en el código de registro de C++.

## Ciclo del Agente

El Safari SDK incluye un **framework de agente integral** (`safari_sdk/agent/framework`) diseñado para construir agentes robóticos interactivos impulsados por modelos Gemini. Este framework proporciona una arquitectura modular que permite a los agentes:

*   **Percibir su entorno:** Recopilar información del mundo físico.
*   **Razonar sobre tareas:** Procesar la información y tomar decisiones.
*   **Controlar hardware robótico:** Ejecutar acciones en el robot.

Un ejemplo notable es el agente Aloha (`examples/aloha/agent/simple_agent.py`), que demuestra un agente conversacional capaz de controlar el robot Aloha mediante instrucciones en lenguaje natural, integrando control robótico basado en visión, percepción multicámara e interacción conversacional con modelos Gemini.

## Sistema de Memoria y Contexto

Aunque el `README.md` no detalla explícitamente un 
sistema de memoria y contexto dedicado, la descripción del framework del agente menciona que los agentes se integran con la **Gemini Live API** para proporcionar interacción conversacional y capacidades de uso de herramientas. Esto sugiere que la gestión del contexto y la memoria se manejan a través de la API de Gemini, permitiendo al agente mantener el hilo de la conversación y las tareas a lo largo del tiempo.

## Manejo de Herramientas (Tools/Functions)

El framework del agente incluye un componente de **Herramientas** (`safari_sdk/agent/framework/tools/`) que proporciona capacidades modulares que los agentes pueden utilizar. Estas herramientas incluyen:

*   **Run instruction:** Para ejecutar instrucciones específicas.
*   **Success detection:** Para determinar si una acción fue exitosa.
*   **Scene description:** Para describir el entorno o la escena actual.

Estas herramientas permiten a los agentes interactuar con el entorno robótico y realizar tareas complejas de manera estructurada.

## Sandbox y Entorno de Ejecución

El `Dockerfile` presente en el repositorio (`Dockerfile`) sugiere que el SDK está diseñado para ser ejecutado en un entorno contenedorizado, lo que proporciona un sandbox aislado y reproducible para el desarrollo y la ejecución de agentes robóticos. Esto es crucial para garantizar la consistencia del entorno y facilitar la implementación en diferentes plataformas.

## Integraciones y Conectores

El SDK de Safari está diseñado para soportar todos los modelos de la serie Gemini Robotics. Las bibliotecas relacionadas con el registro de datos del robot se encuentran en `safari_sdk/logging`. Las bibliotecas para la inferencia de modelos y la interfaz con los servidores de modelos están en `safari_sdk/model`. Además, las bibliotecas y binarios para acceder a los puntos de control del modelo, cargar datos y solicitar el ajuste fino del modelo se encuentran en `safari_sdk/flywheel`.

El **Flywheel CLI** es una herramienta de línea de comandos que permite interactuar con la plataforma Gemini Robotics para tareas como:

*   `train`: Entrenar un modelo.
*   `serve`: Servir un modelo.
*   `list`: Listar trabajos de entrenamiento disponibles.
*   `list_serve`: Listar trabajos de servicio disponibles.
*   `data_stats`: Mostrar estadísticas de datos disponibles para entrenamiento.
*   `download`: Descargar artefactos de un trabajo de entrenamiento.
*   `upload_data`: Cargar datos al servicio de ingesta de datos.

Esto indica una fuerte integración con una plataforma de backend para la gestión del ciclo de vida de los modelos de robótica.

## Benchmarks y Métricas de Rendimiento

El `README.md` no proporciona benchmarks o métricas de rendimiento específicas dentro del repositorio. Sin embargo, se menciona que el SDK permite "evaluar el modelo en el robot y en sim", lo que implica que existen mecanismos para realizar evaluaciones de rendimiento. Para obtener información detallada sobre benchmarks, sería necesario consultar la "página principal de Gemini Robotics" o la documentación para "Trusted Testers".

## Decisiones de Diseño Reveladas en PRs o Issues Técnicos

El repositorio tiene 16 Pull Requests y 1 Issue. La mayoría de los commits recientes son sincronizaciones del SDK a nuevas versiones, lo que sugiere un proceso de desarrollo continuo y la integración de nuevas funcionalidades. La separación de `safari-sdk` y `safari-sdk-logging` en paquetes distintos es una decisión de diseño clara para optimizar los tiempos de compilación, como se mencionó anteriormente.

## Información Técnica Adicional (No en la Documentación Oficial del Sitio Web)

La información detallada sobre la estructura del código, la justificación de la separación de paquetes (`safari-sdk` y `safari-sdk-logging`), y la descripción de los componentes clave del framework del agente (Agentes, Embodiments, Tools, Event Bus, Configuration) se encuentra directamente en el `README.md` del repositorio de GitHub. Si bien la página principal de Gemini Robotics puede ofrecer una visión general, el repositorio de GitHub proporciona los detalles técnicos de implementación y la arquitectura del SDK, que a menudo no se encuentran en la documentación de alto nivel de un sitio web oficial. La existencia del `flywheel-cli` y sus comandos específicos también es una información técnica valiosa que se detalla en el `README.md` del repositorio.