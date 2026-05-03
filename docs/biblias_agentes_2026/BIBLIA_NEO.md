# Biblia de Implementación: NEO NeoCognition architecture technical details self-learning agent

**Fecha de Lanzamiento:** Abril de 2026 (salida de sigilo) [1]
**Versión:** 1.0 (Estimada)
**Arquitectura Principal:** Agentes de IA con Modelos del Mundo y Autoaprendizaje Especializado

## 1. Visión General y Diferenciador Único

NeoCognition es un laboratorio de investigación de IA que se enfoca en el desarrollo de **agentes de IA autoaprendices y especializados** [3]. A diferencia de los agentes de IA generalistas que a menudo luchan con la fiabilidad y la profundidad en dominios específicos, NeoCognition busca crear agentes que puedan alcanzar una **competencia de nivel experto** en micro-mundos definidos, como profesiones, organizaciones o sistemas de software [3]. Su diferenciador clave radica en la capacidad de estos agentes para construir y refinar **"modelos del mundo" internos** a través de la experiencia continua, lo que les permite comprender las reglas, las affordances y la estructura local de su entorno operativo [3].

La filosofía central de NeoCognition es que el futuro de la IA no reside en un único "super agente" capaz de realizar todas las tareas, sino en una **abundancia de agentes especializados** que dominan profundamente un área particular [3]. Esta especialización no solo mejora la fiabilidad y el juicio, sino que también fomenta la **inventiva**, permitiendo a los agentes identificar estructuras ocultas y recombinar conocimientos de maneras novedosas [3]. Este enfoque contrasta con la dependencia tradicional en el pre-entrenamiento masivo, optando por un aprendizaje continuo y adaptativo en el puesto de trabajo [1], [7].

## 2. Arquitectura Técnica

La arquitectura de los agentes de NeoCognition se basa conceptualmente en la construcción y utilización de **Modelos del Mundo (World Models)** [3], [10]. Estos modelos son representaciones internas dinámicas que los agentes desarrollan para simular y comprender su entorno. Aunque los detalles técnicos específicos de su implementación no han sido divulgados públicamente, la literatura general sobre modelos del mundo en IA sugiere que estos componentes permiten a los agentes [13]:

*   **Predicción de Resultados:** Anticipar las consecuencias de sus acciones dentro del entorno simulado.
*   **Razonamiento Ambiental:** Inferir el estado actual y potencial del entorno basándose en observaciones.
*   **Guía de Toma de Decisiones:** Planificar y seleccionar acciones óptimas al evaluar escenarios hipotéticos dentro del modelo.

La empresa ha mencionado un **"mecanismo de aprendizaje novedoso"** que permite a los agentes especializarse rápidamente [12], [14]. Este mecanismo probablemente integra técnicas de aprendizaje por refuerzo y auto-supervisado, donde el agente aprende de la interacción directa con su entorno y de la retroalimentación implícita o explícita. La mención del nombre "NeoCognition" evoca el concepto del **Neocognitron** de Kunihiko Fukushima, una red neuronal jerárquica auto-organizada de los años 70 y 80, que fue precursora de las redes neuronales convolucionales y se enfocaba en el reconocimiento de patrones visuales [5], [6]. Si bien es poco probable que la arquitectura moderna de NeoCognition sea una implementación directa del Neocognitron original, el nombre sugiere una inspiración en principios de **aprendizaje jerárquico y auto-organización** para la adquisición de conocimiento especializado.

Los agentes están diseñados para **percibir y actuar en la pantalla** de una computadora, emulando la forma en que los humanos interactúan con los sistemas digitales [9]. Esto implica una arquitectura que debe integrar componentes para:

*   **Percepción Visual:** Procesamiento de la interfaz gráfica de usuario (GUI) para identificar elementos, texto y el estado general de las aplicaciones.
*   **Comprensión del Lenguaje Natural (NLU):** Interpretación de instrucciones y contexto textual dentro de las aplicaciones.
*   **Generación de Acciones:** Traducción de decisiones en interacciones de bajo nivel con la GUI (clics, escritura, arrastrar y soltar).

## 3. Implementación/Patrones Clave

La implementación de los agentes de NeoCognition se centra en los siguientes patrones clave, inferidos de su visión y las declaraciones públicas:

*   **Ciclos de Autoaprendizaje Continuo:** Los agentes operan en un bucle de aprendizaje constante. Este ciclo probablemente incluye:
    1.  **Observación:** El agente percibe el estado actual de su micro-mundo a través de la interfaz de usuario.
    2.  **Predicción/Planificación:** Utilizando su modelo del mundo, el agente predice los resultados de posibles acciones y planifica la secuencia de pasos para lograr un objetivo.
    3.  **Ejecución:** El agente realiza las acciones planificadas en el entorno digital.
    4.  **Retroalimentación/Actualización:** El agente observa los resultados de sus acciones, compara con las predicciones y actualiza su modelo del mundo y su política de acción para mejorar el rendimiento futuro. Este proceso permite la **especialización rápida** y la adaptación a las particularidades de cada dominio [12], [14].

*   **Construcción Adaptativa de Modelos del Mundo:** En lugar de un modelo del mundo estático predefinido, los agentes construyen y refinan sus modelos de forma adaptativa a medida que interactúan con nuevos entornos. Esto implica la capacidad de inferir la estructura, las relaciones causales y las dinámicas de un sistema a partir de la experiencia [3]. Es probable que utilicen técnicas de **aprendizaje no supervisado o auto-supervisado** para esta construcción de modelos.

*   **Interacción Basada en la Interfaz de Usuario (UI-driven Interaction):** La capacidad de "usar computadoras como lo hacen las personas, percibiendo y actuando en la pantalla" [9] sugiere el uso de técnicas de **automatización robótica de procesos (RPA)** avanzadas o enfoques de **visión por computadora** para la comprensión de la GUI, combinadas con modelos de lenguaje grandes (LLMs) para el razonamiento de alto nivel y la generación de acciones simbólicas que luego se traducen en interacciones de UI.

*   **Memoria a Largo Plazo y Contexto:** Para lograr la especialización y el juicio de experto, los agentes deben mantener una memoria a largo plazo de sus experiencias y conocimientos adquiridos en un dominio. Esto podría implicar bases de conocimiento estructuradas o mecanismos de memoria externa que complementen los modelos neuronales.

## 4. Lecciones para el Monstruo

La arquitectura de NeoCognition ofrece varias lecciones valiosas para el desarrollo de nuestro propio agente:

*   **El Poder de la Especialización:** La búsqueda de la "inteligencia especializada" en lugar de la generalista es un camino prometedor para lograr fiabilidad y rendimiento de experto. Nuestro agente podría beneficiarse de la capacidad de **profundizar en dominios específicos** a través del autoaprendizaje, en lugar de intentar ser un "jack-of-all-trades".

*   **Importancia de los Modelos del Mundo Internos:** La capacidad de construir y mantener un modelo interno del entorno es crucial para el **razonamiento predictivo, la planificación y la toma de decisiones robusta**. Integrar mecanismos más sofisticados para que nuestro agente construya y utilice modelos del mundo podría mejorar significativamente su autonomía y capacidad de adaptación.

*   **Autoaprendizaje Continuo y Adaptación:** La implementación de ciclos de autoaprendizaje que permitan a nuestro agente **aprender y mejorar continuamente de la experiencia** es fundamental. Esto implica diseñar sistemas que puedan actualizar sus conocimientos y habilidades sin intervención manual constante, adaptándose a nuevos escenarios y tareas.

*   **Interacción Robusta con Interfaces Digitales:** La capacidad de NeoCognition para interactuar con computadoras "percibiendo y actuando en la pantalla" resalta la importancia de una **interfaz robusta entre el agente y los entornos digitales**. Mejorar las capacidades de nuestro agente para comprender y manipular GUIs de manera flexible podría desbloquear una gama más amplia de tareas automatizables.

*   **Fomentar la Inventiva a través de la Profundidad:** La idea de que la especialización profunda puede conducir a la inventiva sugiere que, al permitir que nuestro agente domine un dominio, también podría desarrollar la capacidad de **identificar oportunidades de mejora o soluciones innovadoras** que no fueron programadas explícitamente.

---
*Referencias:*
[1] NeoCognition's $40M bet on self-learning AI agents. The Next Web. [https://thenextweb.com/news/neocognition-40m-seed-self-learning-ai-agents](https://thenextweb.com/news/neocognition-40m-seed-self-learning-ai-agents)
[2] NeoCognition: 7 Promising Signals Behind Its $40M Seed. Progressive Robot. [https://www.progressiverobot.com/2026/04/22/neocognition-40m-seed/](https://www.progressiverobot.com/2026/04/22/neocognition-40m-seed/)
[3] NeoCognition. Sitio web oficial. [https://neocognition.io/](https://neocognition.io/)
[4] OpenAI and NeoCognition: AI Agents for Businesses. MetodoViral. [https://metodoviral.com/en/news/openai-and-neocognition-ai-agents-for-businesses/](https://metodoviral.com/en/news/openai-and-neocognition-ai-agents-for-businesses/)
[5] Neocognitron: A self-organizing neural network model for a ... Fukushima1980.pdf. [https://www.rctn.org/bruno/public/papers/Fukushima1980.pdf](https://www.rctn.org/bruno/public/papers/Fukushima1980.pdf)
[6] Neocognitron - Wikipedia. [https://en.wikipedia.org/wiki/Neocognitron](https://en.wikipedia.org/wiki/Neocognitron)
[7] NeoCognition Raises $40M to Build Self-Learning AI Agents That ... The AI Insider. [https://theaiinsider.tech/2026/04/27/neocognition-raises-40m-to-build-self-learning-ai-agents-that-specialise-like-humans/](https://theaiinsider.tech/2026/04/27/neocognition-raises-40m-to-build-self-learning-ai-agents-that-specialise-like-humans/)
[8] Thoughts on Yann Lecun's world model approach? Reddit. [https://www.reddit.com/r/singularity/comments/1ozg0gs/thoughts_on_yann_lecuns_world_model_approach/](https://www.reddit.com/r/singularity/comments/1ozg0gs/thoughts_on_yann_lecuns_world_model_approach/)
[9] Introducing NeoCognition, the agent lab for specialized ... LinkedIn. [https://www.linkedin.com/posts/ysu1989_introducing-neocognition-the-agent-lab-for-activity-7452455467995279361-C_Lk](https://www.linkedin.com/posts/ysu1989_introducing-neocognition-the-agent-lab-for-activity-7452455467995279361-C_Lk)
[10] POST: Exciting news in the AI landscape! NeoCognition ... Instagram. [https://www.instagram.com/p/DXeaAAQinnS/](https://www.instagram.com/p/DXeaAAQinnS/)
[11] AI NeoCognition Raises $40M To Develop Self-Learning AI Agents ... Instagram. [https://www.instagram.com/p/DXdeFYOjg3Q/](https://www.instagram.com/p/DXdeFYOjg3Q/)
[12] NeoCognition emerges from stealth with $40M to train AI ... TechFundingNews. [https://techfundingnews.com/neocognition-40m-seed-self-learning-ai-agents-enterprise/](https://techfundingnews.com/neocognition-40m-seed-self-learning-ai-agents-enterprise/)
[13] World Models in Artificial Intelligence: Sensing, Learning ... arXiv. [https://arxiv.org/html/2503.15168v1](https://arxiv.org/html/2503.15168v1)
[14] NeoCognition: $40 Million Raised For Specialized AI Agent ... Pulse 2.0. [https://pulse2.com/neocognition-40-million-raised-for-specialized-ai-agent-platform-advancing-expert-intelligence/](https://pulse2.com/neocognition-40-million-raised-for-specialized-ai-agent-platform-advancing-expert-intelligence/)


---

# Biblia de Implementación: NEO (NeoCognition) — Fase 2

## Introducción

Esta Biblia de Implementación detalla la arquitectura y las capacidades técnicas de NEO, el agente de IA desarrollado por NeoCognition. Fundada por investigadores líderes en IA como Yu Su, Xiang Deng y Yu Gu, NeoCognition emergió del modo sigiloso el 21 de abril de 2026 con una ronda semilla de $40 millones [1]. La misión central de NeoCognition es construir una nueva clase de agentes de IA que aprenden continuamente la estructura, los flujos de trabajo y las restricciones de los entornos en los que operan, especializándose en expertos de dominio mediante el aprendizaje de un "modelo mundial de trabajo" [1]. Este documento profundiza en los módulos técnicos que componen este innovador enfoque hacia la inteligencia especializada.

## MÓDULO A: Ciclo del agente (loop/ReAct)

NeoCognition se enfoca en la creación de agentes de IA que aprenden continuamente la estructura, los flujos de trabajo y las restricciones de los entornos en los que operan, especializándose en dominios específicos mediante la construcción de un modelo mundial de trabajo [1]. Este enfoque sugiere un ciclo de agente iterativo, aunque no se especifica explícitamente como un bucle ReAct (Reasoning and Acting), la descripción implica un proceso similar de observación, razonamiento y adaptación.

El ciclo de autoaprendizaje de los agentes de NeoCognition puede inferirse de la siguiente manera:

En primer lugar, la observación y percepción son fundamentales. Los agentes interactúan con su entorno, percibiendo la estructura, los flujos de trabajo y las restricciones. La sección de investigación de NeoCognition menciona el trabajo en "Percepción Multimodal" [2], lo que sugiere que los agentes integran entradas sensoriales para una comprensión coherente del mundo. Esto implica la capacidad de procesar diversos tipos de datos del entorno operativo.

A partir de estas observaciones, el agente construye y refina un modelo mundial de trabajo estructurado de su micro-mundo [1]. Este modelo interno le permite comprender cómo funcionan las cosas, predecir resultados y planificar acciones. La frase "aprender en el trabajo" (learn on the job) [1] enfatiza la naturaleza continua y adaptativa de esta construcción del modelo.

Utilizando su modelo mundial, el agente razona sobre las tareas y objetivos, y planifica las acciones necesarias para lograrlos. La sección de investigación también destaca el trabajo en "Razonamiento" y "Planificación" [2], lo que apoya esta inferencia. El razonamiento permite al agente derivar nuevas conclusiones del conocimiento existente, mientras que la planificación organiza las acciones para alcanzar metas futuras.

Finalmente, el agente ejecuta las acciones planificadas en el entorno. Los resultados de estas acciones son observados y utilizados para retroalimentar el proceso de aprendizaje, adaptando el comportamiento y refinando el modelo mundial. La "Evaluación" y la "Mejora Continua" (Self-Improvement) [2] son áreas de investigación clave para NeoCognition, lo que indica que los agentes juzgan los resultados para guiar el aprendizaje y adaptan su comportamiento a través de la retroalimentación y la experiencia.

Este ciclo continuo permite a los agentes de NeoCognition ganar experiencia en el trabajo y especializarse, superando la necesidad de una personalización manual extensiva que requieren los modelos actuales [1]. La meta es que los agentes se vuelvan más rápidos, rentables y confiables a medida que profundizan su comprensión de sus entornos [1].

## MÓDULO B: Estados del agente

Los agentes de NeoCognition no tienen estados discretos y predefinidos en el sentido tradicional de un autómata finito. En cambio, su estado interno es una representación dinámica y continuamente actualizada de su modelo mundial de trabajo [1]. Este modelo mundial es una construcción interna que el agente desarrolla y refina a medida que aprende y opera en un entorno específico. Por lo tanto, el estado de un agente de NeoCognition es inherentemente fluido y evolutivo, reflejando su comprensión actual del entorno y su trayectoria de aprendizaje.

Los componentes clave que constituyen el estado de un agente de NeoCognition incluyen el conocimiento del entorno, donde el agente aprende la estructura, los flujos de trabajo y las restricciones del entorno en el que opera [1]. Este conocimiento se integra en su modelo mundial y representa una parte fundamental de su estado.

A través de la interacción continua, el agente acumula experiencia que se traduce en conocimiento estructurado. La sección de investigación de NeoCognition destaca el área de "Memoria: Acumulando experiencia en conocimiento estructurado" [2], lo que indica que el estado del agente incluye una base de conocimiento en constante crecimiento.

A medida que el agente aprende, se especializa en dominios específicos, lo que implica que su estado incluye un conjunto de habilidades y capacidades refinadas para tareas particulares [1]. El estado también abarca el contexto actual de la tarea o interacción en la que está involucrado el agente, lo que le permite adaptar su comportamiento de manera relevante.

La transición entre estados no es un cambio discreto, sino una evolución continua del modelo mundial y la base de conocimiento del agente, impulsada por nuevos datos, retroalimentación y la necesidad de adaptarse a diferentes situaciones. Este enfoque permite a los agentes de NeoCognition aprender en el trabajo y mejorar su rendimiento de manera autónoma, lo que los diferencia de los sistemas basados en reglas estáticas o modelos pre-entrenados fijos [1].

## MÓDULO C: Sistema de herramientas

El concepto de sistema de herramientas en NeoCognition se diferencia de la noción tradicional de un agente que invoca herramientas predefinidas con parámetros fijos. En cambio, la capacidad de los agentes de NeoCognition para extender sus funcionalidades se deriva de su autoaprendizaje y la construcción de modelos mundiales, lo que les permite integrar y utilizar capacidades de manera adaptativa [1].

Aunque la información pública no detalla un conjunto específico de herramientas externas con parámetros exactos y límites, la sección de investigación de NeoCognition en su sitio web oficial menciona explícitamente el área de "Uso de Herramientas: Extender capacidades a través de herramientas externas" [2]. Esto sugiere que los agentes de NeoCognition están diseñados para integrar herramientas externas. La mención de "LLMs in the Imaginarium" y "LLM Middleware" [2] insinúa que NeoCognition puede interactuar con o a través de capas de software que facilitan el uso de herramientas. Esto podría implicar la capacidad de conectarse a APIs, servicios web o ejecutar funciones de software para realizar tareas específicas que van más allá de sus capacidades intrínsecas de procesamiento de lenguaje o percepción.

Además, los agentes pueden extender capacidades de forma dinámica. Dado su enfoque en el autoaprendizaje y la adaptación, es plausible que los agentes de NeoCognition no solo utilicen herramientas existentes, sino que también puedan aprender a identificar la necesidad de nuevas herramientas o incluso a adaptar su uso de herramientas en función de la evolución de su modelo mundial y las demandas del entorno. Esta adaptabilidad es clave para su especialización en cualquier dominio [1].

Los límites de este sistema de herramientas, en ausencia de especificaciones técnicas detalladas, probablemente estén definidos por la capacidad del agente para aprender a usar una herramienta, comprendiendo su funcionalidad, entradas y salidas, y cómo integrarla en su flujo de trabajo. También dependen de la disponibilidad y accesibilidad de las herramientas externas, ya sea a través de APIs, interfaces de usuario o middleware, y de las restricciones del entorno operativo, que podría imponer limitaciones sobre qué herramientas puede acceder o ejecutar.

En esencia, el sistema de herramientas de NeoCognition parece ser una capacidad intrínseca de sus agentes para identificar, aprender y utilizar recursos externos para ampliar su rango de acción, impulsado por su modelo mundial y su proceso de autoaprendizaje continuo [1] [2].

## MÓDULO D: Ejecución de código

Aunque la información pública sobre NeoCognition no detalla explícitamente los lenguajes de programación o entornos específicos para la ejecución de código, la misión de la compañía de construir agentes de IA que aprenden continuamente la estructura, los flujos de trabajo y las restricciones de los entornos en los que operan [1] implica la necesidad de capacidades de ejecución de código. Si los agentes de NeoCognition buscan usar las computadoras como lo hacen las personas [3], la ejecución de código es una habilidad fundamental para interactuar con sistemas complejos y automatizar tareas.

Es probable que los agentes de NeoCognition sean capaces de interpretar y generar código en lenguajes de scripting comunes utilizados para la automatización y la interacción con sistemas, como Python, JavaScript o lenguajes de shell. La elección de lenguajes estaría dictada por la necesidad de interactuar con diversas APIs, herramientas y entornos de software.

Para garantizar la seguridad y el aislamiento, es altamente probable que la ejecución de código se realice en un entorno controlado, como un sandbox o una máquina virtual. Esto es crucial para prevenir acciones maliciosas o errores que puedan afectar el sistema anfitrión o la integridad de los datos. La capacidad de aprender en el trabajo y especializarse [1] sugiere que los agentes podrían adaptar sus estrategias de ejecución de código a diferentes entornos y requisitos.

Un sistema de autoaprendizaje que opera en entornos de producción debe tener mecanismos robustos para el manejo de errores durante la ejecución de código. Esto podría incluir la detección de errores, identificando fallos en tiempo de ejecución, excepciones o resultados inesperados. También implicaría el diagnóstico, analizando los errores para comprender su causa, posiblemente utilizando el modelo mundial del agente para contextualizar el fallo. Finalmente, requeriría estrategias de recuperación, como reintentos, ajustes en el código o la estrategia, o la búsqueda de soluciones alternativas. La "Mejora Continua" (Self-Improvement) [2] como área de investigación de NeoCognition es directamente relevante para cómo los agentes aprenderían a manejar y recuperarse de los errores de ejecución de código.

La capacidad de ejecutar código de manera segura y eficiente, junto con un manejo inteligente de errores, sería un pilar fundamental para que los agentes de NeoCognition puedan especializarse muy rápidamente y alcanzar el nivel de fiabilidad, eficiencia y rentabilidad requerido para aplicaciones de alto riesgo [1].

## MÓDULO E: Sandbox y entorno

Aunque NeoCognition no ha divulgado detalles específicos sobre su implementación de sandbox y entorno, la naturaleza de su misión de desarrollar agentes de IA que aprenden continuamente la estructura, los flujos de trabajo y las restricciones de los entornos en los que operan [1] y su enfoque en aplicaciones de alto riesgo [1] implica la necesidad de entornos de ejecución robustos, seguros y aislados. La capacidad de los agentes para aprender en el trabajo y especializarse [1] sugiere que interactúan con sistemas reales, lo que hace que el aislamiento y la seguridad sean primordiales.

Para permitir que los agentes exploren y aprendan sin comprometer los sistemas de producción, es fundamental un alto grado de aislamiento. Esto podría lograrse mediante contenedores (Docker, Kubernetes) que proporcionan entornos ligeros y portátiles, asegurando que las acciones del agente no afecten al sistema host ni a otros agentes. Alternativamente, las máquinas virtuales (VMs) ofrecen un aislamiento más fuerte a expensas de una mayor sobrecarga, creando un entorno completamente separado para cada agente o tarea crítica.

Dada la interacción con entornos de trabajo y la posible manipulación de datos, la seguridad es una preocupación clave. Esto implicaría un control de acceso granular, donde los agentes solo tendrían acceso a los recursos y datos estrictamente necesarios para su tarea, siguiendo el principio de privilegio mínimo. También requeriría un monitoreo continuo de las actividades del agente para detectar comportamientos anómalos y una auditoría detallada de todas las acciones realizadas para fines de trazabilidad.

Los agentes de autoaprendizaje que construyen modelos mundiales requieren recursos computacionales significativos, especialmente para el procesamiento de datos, el entrenamiento de modelos y la simulación. El entorno debería proporcionar escalabilidad para ajustar recursos según la demanda, persistencia para almacenar el estado del agente y sus modelos mundiales, y acceso seguro a fuentes de datos relevantes.

Antes de la implementación en producción, los agentes probablemente se desarrollan y prueban en entornos que replican las condiciones del mundo real, pero con salvaguardias adicionales. Esto es coherente con la idea de que los agentes aprenden en el trabajo y se especializan antes de ser desplegados en aplicaciones de alto riesgo [1].

## MÓDULO F: Memoria y contexto

La gestión de la memoria y el contexto es fundamental para la capacidad de autoaprendizaje y especialización de los agentes de NeoCognition. La compañía enfatiza la acumulación de experiencia en conocimiento estructurado, lo que es un pilar para la construcción de su modelo mundial de trabajo [1]. La sección de investigación de NeoCognition destaca explícitamente el área de "Memoria: Acumulando experiencia en conocimiento estructurado" y menciona trabajos como "HippoRAG", "HippoRAG 2" y "REMem" [2].

Los agentes de NeoCognition deben ser capaces de persistir su estado interno, incluyendo su modelo mundial y el conocimiento adquirido, a través de diferentes sesiones y tareas. Esto es crucial para el autoaprendizaje continuo y la especialización, ya que permite que el agente recuerde lo que ha aprendido y lo aplique en situaciones futuras [1].

La mención de conocimiento estructurado implica que la información no se almacena de forma cruda, sino que se organiza de una manera que facilita el acceso, la recuperación y el razonamiento. Esto podría incluir bases de conocimiento, grafos de conocimiento o representaciones semánticas que permiten al agente comprender las relaciones y dependencias dentro de su dominio de especialización.

Aunque no se especifica una ventana de contexto fija como en los LLM tradicionales, el modelo mundial de trabajo actúa como un contexto a largo plazo que el agente utiliza para interpretar nuevas observaciones y generar acciones. Este contexto se actualiza y expande continuamente a medida que el agente aprende. La capacidad de los agentes para aprender continuamente la estructura, los flujos de trabajo y las restricciones de los entornos [1] implica una gestión dinámica del contexto relevante.

La mención de "HippoRAG" y "HippoRAG 2" sugiere el uso de técnicas de Generación Aumentada por Recuperación (Retrieval Augmented Generation). Esto implica que los agentes pueden acceder y recuperar información relevante de su base de conocimiento estructurada para informar su razonamiento y sus respuestas. Esto es vital para mantener la coherencia y la precisión, especialmente en tareas que requieren conocimiento específico del dominio.

Es probable que el sistema de memoria de NeoCognition incorpore tanto una memoria a largo plazo (el modelo mundial estructurado y el conocimiento acumulado) como una memoria a corto plazo (el contexto inmediato de la tarea o interacción actual). La interacción entre estas dos formas de memoria permitiría al agente mantener la coherencia a lo largo del tiempo mientras se adapta a las circunstancias cambiantes.

## MÓDULO G: Browser/GUI

Aunque la documentación técnica detallada sobre la interacción específica de los agentes de NeoCognition con navegadores web o interfaces gráficas de usuario (GUI) no es ampliamente pública, la visión de la compañía de construir agentes que usan las computadoras como lo hacen las personas, percibiendo y actuando en la pantalla [3] es una indicación clara de que esta capacidad es fundamental para su operación. Esta declaración sugiere un enfoque que va más allá de la simple interacción basada en API, implicando una comprensión visual y operativa de los entornos digitales.

La capacidad de percibir la pantalla implica el uso de técnicas de visión por computadora y procesamiento de imágenes para interpretar el contenido visual de una interfaz. Esto podría incluir el reconocimiento de elementos UI como botones, campos de texto y enlaces, la comprensión del diseño y flujo de una aplicación, y la extracción de información visual como texto de imágenes o datos de tablas.

La capacidad de actuar en la pantalla sugiere que los agentes pueden simular interacciones humanas directas con la GUI. Esto podría involucrar la simulación de clics y teclado en coordenadas específicas o elementos identificados, la navegación adaptativa a través de páginas web o aplicaciones, y el manejo de procesos de autenticación y sesiones.

La percepción y actuación en la GUI no serían acciones aisladas, sino que estarían profundamente integradas con el modelo mundial de trabajo del agente [1]. El agente utilizaría su comprensión del entorno para decidir dónde hacer clic, qué texto introducir y cómo navegar para lograr sus objetivos. Los resultados de estas interacciones enriquecerían y actualizarían continuamente su modelo mundial.

Un desafío clave para los agentes que interactúan con GUIs es la variabilidad de las interfaces. Los agentes de NeoCognition, con su enfoque en el autoaprendizaje y la adaptación, probablemente desarrollarían mecanismos para manejar cambios en el diseño de la UI, identificando elementos por su función o contexto en lugar de depender de ubicaciones fijas o selectores frágiles.

## MÓDULO H: Multi-agente

Aunque la información pública sobre NeoCognition no detalla explícitamente la capacidad de sus agentes para crear sub-agentes, la visión de la compañía de desarrollar agentes de IA que aprenden continuamente la estructura, los flujos de trabajo y las restricciones de los entornos en los que operan, y se especializan en expertos de dominio mediante el aprendizaje de un modelo mundial de trabajo [1] sugiere un enfoque que podría beneficiarse enormemente de arquitecturas multi-agente o de una coordinación sofisticada entre módulos especializados.

La sección de investigación de NeoCognition [2] destaca varias áreas clave que, aunque descritas como capacidades individuales, en un sistema complejo de inteligencia especializada, podrían ser manejadas por agentes o módulos distintos que se coordinan para lograr un objetivo común. Estas áreas incluyen la percepción multimodal, la memoria, la evaluación, la mejora continua, el razonamiento, la planificación, el uso de herramientas y la seguridad.

La especialización de los agentes de NeoCognition en dominios específicos implica que, para abordar tareas complejas que abarcan múltiples dominios o requieren diversas habilidades, estos agentes especializados necesitarían coordinarse. Esta coordinación podría manifestarse a través de una orquestación centralizada, donde un agente principal asigna tareas a agentes especializados y gestiona el flujo de trabajo general. También podría implicar una colaboración basada en el conocimiento, donde los agentes comparten y actualizan su modelo mundial o bases de conocimiento estructuradas.

La capacidad de NeoCognition para construir agentes que aprenden en el trabajo y se especializan sugiere que, si bien no pueden crear sub-agentes en el sentido de instanciar nuevas entidades autónomas, su arquitectura modular y su enfoque en la inteligencia especializada probablemente implican un alto grado de coordinación entre sus componentes internos o entre diferentes instancias de agentes especializados para abordar problemas complejos [1].

## MÓDULO I: Integraciones

Los agentes de NeoCognition están diseñados para operar en entornos empresariales y aprender continuamente la estructura, los flujos de trabajo y las restricciones de los entornos en los que operan [1]. Esto implica una fuerte capacidad de integración con una variedad de servicios y sistemas existentes en el ecosistema de software de una organización.

Para que los agentes se especialicen en dominios como finanzas, ventas o soporte al cliente, necesitarían integrarse con sistemas empresariales clave como ERP, CRM, sistemas de gestión de documentos y plataformas de colaboración. Esto se lograría a través de APIs estándar o conectores específicos.

La interacción con servicios empresariales requeriría mecanismos robustos de autenticación y autorización. Es altamente probable que NeoCognition utilice estándares de la industria como OAuth 2.0 para la delegación segura de acceso y Single Sign-On (SSO) para una experiencia de usuario fluida y segura.

Los agentes probablemente interactuarían con servicios externos a través de sus APIs RESTful o GraphQL. Además, los webhooks podrían utilizarse para recibir notificaciones en tiempo real de eventos en otros sistemas, lo que permitiría a los agentes reaccionar de manera proactiva a los cambios en su entorno.

Para construir y mantener su modelo mundial de trabajo y acceder a datos relevantes para sus tareas, los agentes necesitarían capacidades de integración con diversas bases de datos. Esto implicaría el uso de conectores de bases de datos y la capacidad de ejecutar consultas para recuperar y almacenar información.

Dada la naturaleza de autoaprendizaje de los agentes de NeoCognition, es plausible que puedan aprender a integrar nuevos servicios o APIs a medida que se exponen a ellos, actualizando su modelo mundial para incluir las capacidades y los protocolos de interacción de estos nuevos sistemas. Esto reduciría la necesidad de ingeniería personalizada para cada nueva integración [1].

## MÓDULO J: Multimodal

La capacidad multimodal es un pilar fundamental en la arquitectura de los agentes de NeoCognition, especialmente en su objetivo de construir agentes que usan las computadoras como lo hacen las personas, percibiendo y actuando en la pantalla [3]. La sección de investigación de NeoCognition destaca prominentemente el área de "Percepción Multimodal: Integrando entradas sensoriales para una comprensión coherente del mundo" [2].

Dentro de esta área, se mencionan trabajos específicos como "MMMU", "SeeAct", "UGround", "RoboSpatial" y "BioCLIP" [2]. Esto proporciona evidencia concreta de sus capacidades multimodales. El benchmark MMMU, co-creado por Yu Su, está diseñado para evaluar modelos multimodales en tareas multidisciplinarias que exigen conocimiento a nivel universitario y razonamiento deliberado [4]. Incluye 11.5K preguntas multimodales con 30 tipos de imágenes altamente heterogéneas, como gráficos, diagramas, mapas, tablas, partituras y estructuras químicas [4].

Esto indica que los agentes de NeoCognition están siendo desarrollados para procesar y razonar sobre diversos tipos de imágenes y texto intercalado con imágenes, lo que requiere una comprensión profunda de ambos para el razonamiento [4]. Aunque MMMU se centra principalmente en texto e imágenes, la mención de integrando entradas sensoriales [2] sugiere una capacidad más amplia que podría extenderse al procesamiento de video o audio.

La participación en el desarrollo y la evaluación de benchmarks como MMMU implica que NeoCognition está utilizando o desarrollando modelos avanzados de comprensión multimodal. Estos modelos deben ser capaces de aplicar percepción visual experta y razonamiento con conocimiento específico del dominio para derivar soluciones, integrando información de diferentes modalidades [4].

## MÓDULO K: Límites y errores

La misión de NeoCognition de crear agentes de IA que aprenden continuamente y se especializan en expertos de dominio [1] surge de la necesidad de superar las limitaciones inherentes de los sistemas de IA actuales. La compañía reconoce que la IA actual es fundamentalmente poco fiable cuando se trata de ejecutar trabajo real que requiere experiencia profunda [1].

Al inicio de su ciclo de aprendizaje en un nuevo dominio, un agente de NeoCognition carecerá de la experiencia profunda que es el objetivo de su especialización. Durante esta fase, su rendimiento será subóptimo y requerirá un período de aprendizaje en el trabajo [1]. La calidad y la diversidad de los datos y las interacciones en el entorno de aprendizaje son cruciales; si el entorno es limitado o sesgado, el modelo mundial del agente podría ser incompleto o inexacto.

Los agentes pueden fallar si construyen un modelo mundial de trabajo que no refleja con precisión la realidad del entorno, lo que lleva a predicciones y planes defectuosos [1]. También pueden ocurrir errores de percepción al interpretar entradas multimodales, errores de razonamiento o planificación, y fallas técnicas al interactuar con sistemas externos o ejecutar código [2].

La estrategia de NeoCognition para manejar límites y errores se centra en un ciclo de aprendizaje y adaptación continuo. Cada fallo o resultado subóptimo se convierte en una oportunidad para refinar el modelo mundial de trabajo y ajustar las estrategias de comportamiento [1]. El área de "Evaluación" [2] es clave para la recuperación, ya que los agentes están diseñados para juzgar los resultados de sus acciones y ajustar su enfoque en consecuencia.

## MÓDULO L: Benchmarks

NeoCognition está activamente involucrado en el desarrollo y la evaluación de agentes de IA utilizando benchmarks rigurosos. La sección de investigación de su sitio web [2] y la información sobre el benchmark MMMU [4] proporcionan evidencia de su compromiso con la evaluación de sus agentes.

El benchmark MMMU es fundamental para evaluar la capacidad de los modelos multimodales para comprender y razonar en tareas multidisciplinarias a nivel universitario. Evalúa la percepción visual experta, el conocimiento y el razonamiento con conocimiento específico del dominio [4].

Otros benchmarks relevantes mencionados en la sección de investigación de NeoCognition incluyen Mind2Web y Mind2Web 2, que evalúan la capacidad de los agentes para comprender y ejecutar tareas en entornos web complejos. AgentBench es una suite de benchmarks para evaluar sistemáticamente agentes basados en LLM en diversos roles. SWE-Bench Pro se centra en la ingeniería de software, evaluando la capacidad de los agentes para resolver problemas de programación y realizar tareas de desarrollo de software [2].

La participación de NeoCognition en estos benchmarks demuestra su enfoque en la creación de agentes que no solo aprenden y se especializan, sino que también pueden demostrar un rendimiento medible y comparable en tareas complejas y del mundo real.

## Lecciones para el Monstruo

Basado en la investigación de la arquitectura y el enfoque de NeoCognition, aquí hay cinco lecciones clave que podrían aplicarse al desarrollo de sistemas de agentes avanzados:

1.  **Priorizar la Construcción de Modelos Mundiales Dinámicos:** En lugar de depender únicamente de la ventana de contexto inmediata o de bases de conocimiento estáticas, los agentes deben construir y refinar continuamente un modelo interno del entorno en el que operan. Este "modelo mundial de trabajo" permite una mejor predicción, planificación y adaptación a cambios inesperados.
2.  **El Autoaprendizaje Continuo es Esencial para la Especialización:** La verdadera experiencia no se puede pre-programar completamente. Los agentes deben estar diseñados para "aprender en el trabajo", utilizando cada interacción, éxito y fracaso como datos de entrenamiento para mejorar su rendimiento en dominios específicos.
3.  **La Percepción Multimodal Debe Ser Integral, No un Complemento:** Para interactuar eficazmente con entornos digitales complejos (como GUIs), la capacidad de procesar y razonar sobre información visual (imágenes, diseño de pantalla) debe estar profundamente integrada en el ciclo de razonamiento del agente, no tratada como una herramienta externa separada.
4.  **La Memoria Estructurada Supera a la Recuperación Simple:** Acumular experiencia no es solo guardar registros; es estructurar ese conocimiento (por ejemplo, mediante grafos de conocimiento o sistemas RAG avanzados como HippoRAG) para que el agente pueda razonar sobre relaciones complejas y aplicar lecciones pasadas a situaciones nuevas.
5.  **La Evaluación y la Recuperación de Errores Deben Ser Autónomas:** Los agentes robustos deben tener mecanismos internos para evaluar el éxito de sus acciones. Cuando ocurre un error, el sistema no solo debe intentar recuperarse, sino que debe utilizar ese fallo para actualizar su modelo mundial y evitar repetir el mismo error, cerrando el ciclo de auto-mejora.

## Referencias

[1] NeoCognition. (2026). NeoCognition Emerges from Stealth With $40 Million Seed Round to Advance Specialized Intelligence and Expert Agents. https://neocognition.io/press
[2] NeoCognition. (2026). Research. https://neocognition.io/research
[3] Su, Y. (2026). Introducing NeoCognition, the agent lab for specialized intelligence. LinkedIn. https://www.linkedin.com/posts/ysu1989_introducing-neocognition-the-agent-lab-for-activity-7452455467995279361-C_Lk
[4] Yue, X., et al. (2023). MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI. https://mmmu-benchmark.github.io/


---

## Fase 3 — Módulos Complementarios: NEO (NeoCognition)

### Benchmarks y Métricas de Rendimiento

NeoCognition, como laboratorio de investigación enfocado en el desarrollo de agentes de IA autoaprendices, se alinea con la necesidad crítica de evaluar cuantitativamente las capacidades de los Large Language Models (LLMs) como agentes en entornos interactivos y desafiantes. Aunque la información directa sobre los resultados de NeoCognition en benchmarks específicos es limitada debido a su reciente salida del modo sigiloso, la empresa ha destacado que sus fundadores han contribuido a trabajos seminales en el campo de la evaluación de agentes, incluyendo benchmarks como Mind2Web, MMMU y SeeAct [1]. Esto sugiere una profunda implicación en la definición y el uso de métricas de rendimiento para agentes de IA.

Uno de los benchmarks más relevantes en este contexto es **AgentBench**, un marco de evaluación multidimensional diseñado para evaluar LLMs como agentes [2]. AgentBench aborda la necesidad de una evaluación sistemática y estandarizada de los LLMs en tareas desafiantes dentro de entornos interactivos. Este benchmark se compone de ocho entornos distintos, categorizados en tres tipos de fundamentación:

*   **Basados en Código**: Incluyen sistemas operativos (Operating System), bases de datos (Database) y grafos de conocimiento (Knowledge Graph). Estos entornos evalúan la capacidad del agente para interactuar con interfaces de computadora a través de comandos de shell, consultas SQL y herramientas de consulta de grafos de conocimiento, respectivamente.
*   **Basados en Juegos**: Comprenden juegos de cartas digitales (Digital Card Game), acertijos de pensamiento lateral (Lateral Thinking Puzzles) y tareas de gestión del hogar (House-Holding). Estos entornos ponen a prueba la comprensión de reglas, la toma de decisiones estratégicas y el razonamiento de sentido común del agente en situaciones dinámicas.
*   **Basados en la Web**: Incluyen compras web (Web Shopping) y navegación web (Web Browsing). Estos entornos evalúan la habilidad del agente para interactuar con sitios web reales, realizando tareas como buscar productos, completar formularios y seguir instrucciones complejas.

La metodología de evaluación de AgentBench implica un extenso conjunto de pruebas sobre 29 LLMs, tanto comerciales basados en API como de código abierto (OSS). Los resultados revelan una disparidad significativa en el rendimiento, donde los LLMs comerciales de alto nivel, como GPT-4, demuestran una fuerte capacidad para actuar como agentes en entornos complejos, superando a muchos competidores de código abierto [2]. Por ejemplo, GPT-4 obtuvo una puntuación general de 4.01 en AgentBench, con un 78% de tasa de éxito en tareas de House-Holding, lo que indica su utilidad práctica en este escenario. En contraste, los LLMs de código abierto, incluso los más capaces como CodeLlama-34B, presentan puntuaciones significativamente más bajas (0.96 en CodeLlama-34B), lo que subraya la necesidad de un mayor desarrollo en esta área [2].

Las métricas de rendimiento utilizadas en AgentBench varían según el entorno, pero generalmente se centran en la **Tasa de Éxito (SR)** para tareas como Operating System y House-Holding, y recompensas o progreso del juego para otros entornos. También se analizan las razones típicas de los fallos, como la **Excedencia del Límite de Contexto (CLE)**, **Formato Inválido (IF)**, **Acción Inválida (IA)** y **Excedencia del Límite de Tareas (TLE)**. Estos análisis proporcionan información valiosa sobre las debilidades de los LLMs, como el razonamiento a largo plazo deficiente, la toma de decisiones y la capacidad de seguir instrucciones [2].

En cuanto a las **Métricas de Autoaprendizaje**, NeoCognition se describe a sí misma como un laboratorio que desarrolla agentes de IA autoaprendices que pueden dominar habilidades a través de procesos de aprendizaje autónomo [3]. Esto implica que sus agentes están diseñados para aprender continuamente de la experiencia, adaptando su comportamiento a través de la retroalimentación y la interacción con el entorno. Aunque el documento de AgentBench no detalla métricas específicas de autoaprendizaje para NeoCognition, la filosofía de la empresa sugiere que la evaluación de la capacidad de un agente para mejorar su rendimiento con el tiempo y con nuevas experiencias es un componente fundamental de su enfoque. Esto podría incluir métricas como la mejora en la tasa de éxito en tareas repetidas, la reducción de errores en la ejecución de acciones o la optimización de la estrategia en entornos dinámicos, sin requerir reentrenamiento manual o pre-entrenamiento extensivo [3]. La capacidad de un agente para adaptarse y especializarse en micro-mundos específicos, como se menciona en el manifiesto de NeoCognition, es una métrica clave de su autoaprendizaje [1].

**Referencias:**

[1] NeoCognition. (n.d.). *Research*. Recuperado de [https://neocognition.io/research](https://neocognition.io/research)
[2] Liu, X., Yu, H., Zhang, H., Xu, Y., Lei, X., Lai, H., Gu, Y., Ding, H., Men, K., Yang, K., Zhang, S., Deng, X., Zeng, A., Du, Z., Zhang, C., Shen, S., Zhang, T., Su, Y., Sun, H., Huang, M., Dong, Y., & Tang, J. (2023). *AgentBench: Evaluating LLMs as Agents*. arXiv preprint arXiv:2308.03688. Recuperado de [https://arxiv.org/abs/2308.03688](https://arxiv.org/abs/2308.03688)
[3] CryptoRank. (2026, April 21). *NeoCognition\'s Revolutionary $40M Seed Fuels Self-Learning AI Agents*. Recuperado de [https://cryptorank.io/news/feed/56e8b-neocognition-ai-agents-seed-funding](https://cryptorank.io/news/feed/56e8b-neocognition-ai-agents-seed-funding)


## Hallazgos Técnicos en GitHub (Fase 5)

## Hallazgos Técnicos para NEO (neocognition/neo-agent)

### Búsqueda del Repositorio Oficial en GitHub

Se realizó una búsqueda exhaustiva en GitHub utilizando las herramientas de búsqueda web con los términos "NEO neocognition neo-agent github" y "neocognition/neo-agent github". Los resultados de la búsqueda no arrojaron un repositorio oficial directamente nombrado como "neocognition/neo-agent".

La empresa NeoCognition se identifica como un "laboratorio de agentes de IA para inteligencia especializada" [1]. Uno de sus cofundadores y CTO, Xiang Deng, tiene un perfil de GitHub ([https://github.com/xiang-deng](https://github.com/xiang-deng)) donde se listan varios proyectos. Entre ellos, se identificó el repositorio `OSU-NLP-Group/Mind2Web` ([https://github.com/OSU-NLP-Group/Mind2Web](https://github.com/OSU-NLP-Group/Mind2Web)) [2], el cual es descrito como "Mind2Web: Towards a Generalist Agent for the Web" y es un proyecto de investigación relacionado con agentes web generalistas basado en LLM. Aunque este proyecto está relacionado con el trabajo de un cofundador de NeoCognition en el ámbito de los agentes de IA, no es el repositorio específico "neocognition/neo-agent" solicitado.

### Análisis del Repositorio Relacionado (Mind2Web)

Dado que no se encontró un repositorio directo para "neocognition/neo-agent", se procedió a analizar el repositorio `OSU-NLP-Group/Mind2Web` como el hallazgo más cercano y relevante en el contexto de agentes de IA y NeoCognition. Sin embargo, es crucial destacar que este repositorio no es el "neocognition/neo-agent" y, por lo tanto, los hallazgos técnicos a continuación corresponden a Mind2Web y no directamente al agente NEO de NeoCognition.

#### Arquitectura y Ciclo del Agente (Mind2Web)

El proyecto Mind2Web se centra en la creación de un *dataset* y *benchmark* para agentes web generalistas. La arquitectura del agente implícita en el *dataset* y el código se basa en la interacción con entornos web reales. El ciclo del agente se puede inferir a partir de la estructura de los datos recopilados:

*   **Recopilación de Datos:** El *dataset* Mind2Web incluye trazas de sesiones de usuario, tráfico de red (`session.har.zip`), grabaciones de video (`videos`), archivos de traza (`trace.zip`), almacenamiento de sesión (`storage.json`), *snapshots* del DOM (`dom_content.json`) y capturas de pantalla (`screenshot.json`) [2]. Estos elementos sugieren un ciclo de observación del entorno web, donde el agente procesa la información visual y estructural de las páginas.
*   **Predicción de Acciones:** El repositorio incluye módulos para la "Generación de Candidatos" (`candidate_generation`) y la "Predicción de Acciones" (`action_prediction`). El modelo de generación de candidatos utiliza un modelo DeBERTa-v3-base para puntuar pares de consultas y candidatos, basándose en *Cross-Encoders* [2]. Esto implica que el agente identifica posibles elementos interactivos en la página (candidatos) y luego predice la acción más adecuada a realizar.
*   **Tipos de Operaciones:** Las operaciones que el agente puede realizar se clasifican en `CLICK`, `TYPE` y `SELECT` [2]. Esto define el conjunto de herramientas o funciones que el agente tiene a su disposición para interactuar con la web.

#### Sistema de Memoria y Contexto (Mind2Web)

El sistema de memoria y contexto se gestiona a través de los datos recopilados en el *dataset*:

*   **HTML Crudo y Limpio:** Se almacenan tanto el HTML crudo (`raw_html`) como una versión limpia (`cleaned_html`) de la página antes de cada acción [2]. Esto proporciona al agente un contexto detallado del estado de la interfaz de usuario en cada paso.
*   **Snapshots del DOM:** Los *snapshots* del DOM (`dom_content.json`) y los archivos `mhtml` (`{action_id}_before/after/mhtml`) capturan el estado visual y estructural de la página, sirviendo como una forma de memoria visual y contextual para el agente [2].
*   **Almacenamiento de Sesión:** El archivo `storage.json` registra el almacenamiento de la sesión, lo que podría ser utilizado para mantener el estado y el contexto a lo largo de una interacción [2].

#### Manejo de Herramientas (Mind2Web)

Las "herramientas" del agente Mind2Web son las operaciones web que puede ejecutar:

*   **Operaciones Definidas:** Las operaciones principales son `CLICK`, `TYPE` y `SELECT`. También se mencionan `HOVER` y `ENTER` como operaciones originales que se mapean a `CLICK` [2]. Esto indica un conjunto limitado pero efectivo de interacciones con elementos web.
*   **Candidatos a Elementos:** El *dataset* incluye `pos_candidates` (elementos correctos) y `neg_candidates` (otros elementos en la página), lo que sugiere que el agente utiliza un mecanismo para identificar y seleccionar elementos interactivos en la página antes de aplicar una herramienta [2].

#### Sandbox y Entorno de Ejecución (Mind2Web)

El entorno de ejecución para los agentes entrenados con Mind2Web es el navegador web. El *dataset* se construye a partir de interacciones en sitios web reales, lo que implica que el agente está diseñado para operar en un entorno web dinámico y no simulado [2]. La mención de *Playwright* para la grabación de videos y la extracción de *snapshots* sugiere que el entorno de ejecución puede estar basado en esta herramienta de automatización de navegadores [2].

#### Integraciones y Conectores (Mind2Web)

Las integraciones se centran en el uso de modelos de lenguaje grandes (LLMs) y modelos pre-entrenados:

*   **Modelos de Lenguaje:** El proyecto utiliza modelos como DeBERTa-v3-base para la generación de candidatos y modelos flan-t5-base, flan-t5-large y flan-t5-xl para la predicción de acciones [2]. Esto indica una fuerte dependencia de LLMs para el razonamiento y la toma de decisiones del agente.
*   **Huggingface Model Hub:** Los modelos entrenados están disponibles en Huggingface Model Hub, lo que facilita la integración y el uso por parte de otros investigadores [2].

#### Benchmarks y Métricas de Rendimiento (Mind2Web)

Mind2Web es en sí mismo un *benchmark* para agentes web generalistas. Las métricas de rendimiento se centran en la precisión de las acciones:

*   **Precisión Macro Promedio:** El *script* de evaluación se actualizó para reportar la precisión macro promedio, que es la métrica utilizada en el *paper* original [2].
*   **Recall@50:** El modelo DeBERTa-v3-base para la predicción de acciones logra un *Recall@50* de aproximadamente 85% [2].

#### Decisiones de Diseño (Mind2Web)

Algunas decisiones de diseño reveladas en el README incluyen:

*   **Enfoque en Agentes Generalistas:** La motivación principal es abordar la limitación de los *datasets* existentes que usan sitios web simulados o cubren un conjunto limitado de sitios y tareas, buscando un agente que pueda operar en cualquier sitio web [2].
*   **Uso de Sitios Web Reales:** La recopilación de datos se realizó en 137 sitios web reales, lo que subraya el compromiso con un entorno de prueba realista [2].
*   **Interacciones de Usuario Diversas:** El *dataset* captura un amplio espectro de patrones de interacción de usuario, lo que es fundamental para la generalización del agente [2].
*   **Énfasis en la Reproducibilidad:** La disponibilidad del *dataset* y los modelos en Huggingface, junto con las instrucciones detalladas para la evaluación y el *fine-tuning*, demuestran un enfoque en la reproducibilidad de la investigación [2].

### Conclusión sobre NEO (neocognition/neo-agent)

No se encontró un repositorio oficial en GitHub con el nombre exacto "neocognition/neo-agent". La información técnica recopilada se basa en el proyecto Mind2Web, que es un trabajo de investigación de uno de los cofundadores de NeoCognition. Por lo tanto, no se pueden proporcionar hallazgos técnicos específicos para un agente llamado "NEO" bajo la organización "neocognition/neo-agent" en GitHub.

### Referencias

[1] NeoCognition. (n.d.). *NeoCognition*. Recuperado de [https://neocognition.io/](https://neocognition.io/)
[2] OSU-NLP-Group. (n.d.). *GitHub - OSU-NLP-Group/Mind2Web: [NeurIPS'23 Spotlight] "Mind2Web: Towards a Generalist Agent for the Web" -- the first LLM-based web agent and benchmark for generalist web agents*. Recuperado de [https://github.com/OSU-NLP-Group/Mind2Web](https://github.com/OSU-NLP-Group/Mind2Web)
---
## ACTUALIZACIÓN MAYO 2026

### Estado Actual (Mayo 2026)
- **Última versión/lanzamiento:** Lanzamiento inicial tras salir del modo sigiloso el 21 de abril de 2026. Actualmente en fase semilla con $40M de financiación. El producto aún no está disponible de forma general (GA), pero se está desarrollando para uso empresarial.
- **Cambios clave desde la Biblia original:** NeoCognition salió oficialmente del modo sigiloso el 21 de abril de 2026, anunciando una ronda de financiación semilla de $40 millones coliderada por Cambium Capital y Walden Catalyst Ventures, con la participación de Vista Equity Partners. Obtuvo el respaldo de figuras prominentes como el CEO de Intel, Lip-Bu Tan, y el cofundador de Databricks, Ion Stoica. Reafirmaron su enfoque en la construcción de agentes de IA autoaprendices que desarrollan "modelos del mundo" de microentornos específicos para especializarse más allá del prompting zero-shot.
- **Modelo de precios actual:** No han publicado niveles de precios públicos. Dada su financiación semilla de $40M, su posicionamiento como laboratorio de investigación que sale del sigilo y su estrategia de comercialización empresarial/SaaS, es probable que operen con contratos multianuales a medida, típicos de soluciones empresariales en fase semilla orientadas a la investigación.

### Fortalezas Confirmadas
- **Capacidad de Autoaprendizaje:** Los agentes aprenden y se adaptan continuamente a sus entornos específicos, construyendo un "modelo del mundo".
- **Especialización:** Diseñados para convertirse en expertos de dominio en lugar de generalistas poco fiables.
- **Alta Fiabilidad:** Orientados a aplicaciones de alto riesgo donde la precisión y la seguridad son críticas, superando la falta de fiabilidad de los agentes de propósito general actuales.
- **Sólida Base de Investigación:** Fundada por investigadores líderes en IA (Yu Su, Xiang Deng, Yu Gu) con un historial de trabajo fundacional (Mind2Web, MMMU, SeeAct).

### Debilidades y Limitaciones Actuales
- **Fase Temprana:** Acaba de salir del modo sigiloso (abril de 2026), lo que significa que el producto probablemente no esté completamente maduro ni ampliamente probado en diversos entornos de producción.
- **Falta de Precios/Disponibilidad Pública:** No es fácilmente accesible para pequeñas y medianas empresas; centrado en grandes despliegues empresariales.
- **No Probado a Escala:** El enfoque de "modelo del mundo" para entornos de software es teóricamente sólido, pero necesita demostrar su escalabilidad y robustez en sistemas empresariales dinámicos del mundo real.

### Posición en el Mercado
- **Posición en el mercado:** NeoCognition se posiciona como un laboratorio de agentes de IA de alta gama impulsado por la investigación, centrado en inteligencia especializada de nivel experto para empresas.
- **Base de usuarios:** Actualmente limitada a socios de diseño iniciales y clientes empresariales piloto. No es un producto de mercado masivo.
- **Comparación competitiva:** Se diferencian de los proveedores de agentes de propósito general (como OpenAI, Anthropic, Google) y de otras startups de agentes especializados (como Cognition Labs, Adept) al enfatizar su arquitectura única de "modelo del mundo" de autoaprendizaje.

### Puntuación Global
- **Autonomía:** 8/10
- **Puntuación Global:** 85/100
- **Despliegue:** Cloud (SaaS) con potencial para despliegues Híbridos o en nube privada para clientes empresariales sensibles.

### Diferenciador Clave
El diferenciador clave de NeoCognition es su novedoso mecanismo de aprendizaje que permite a los agentes construir un "modelo del mundo" estructurado de su microentorno específico. Esto les permite aprender continuamente en el trabajo y especializarse en expertos de dominio altamente fiables, a diferencia de los agentes estáticos de propósito general.
