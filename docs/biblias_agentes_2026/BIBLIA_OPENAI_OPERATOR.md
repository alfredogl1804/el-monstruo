# Biblia de Implementación: OpenAI Operator CUA

**Fecha de Lanzamiento:** 23 de enero de 2025
**Versión:** Research Preview
**Arquitectura Principal:** Computer-Using Agent (CUA) impulsado por las capacidades de visión de GPT-4o y aprendizaje por refuerzo para la interacción con GUI.

## 1. Visión General y Diferenciador Único

OpenAI Operator es un agente de inteligencia artificial diseñado para interactuar con interfaces gráficas de usuario (GUI) de manera similar a un humano, permitiéndole ejecutar tareas en la web sin la necesidad de integraciones de API personalizadas. Su principal diferenciador radica en su capacidad para "ver" (a través de capturas de pantalla) e "interactuar" (utilizando acciones de ratón y teclado virtuales) con cualquier navegador. Esta capacidad se logra combinando las avanzadas capacidades de visión de GPT-4o con un razonamiento sofisticado, entrenado mediante aprendizaje por refuerzo. El agente puede auto-corregirse y adaptarse a desafíos inesperados, lo que le otorga una flexibilidad considerable para operar en diversos entornos digitales sin depender de APIs específicas del sistema operativo o de la web.

## 2. Arquitectura Técnica

La arquitectura central de OpenAI Operator se basa en el modelo **Computer-Using Agent (CUA)**. Este modelo está diseñado para comprender y manipular entornos digitales a través de la interacción con GUI. Los componentes clave de su arquitectura incluyen:

*   **Modelo de Visión (GPT-4o):** CUA integra las capacidades multimodales de GPT-4o, lo que le permite procesar y comprender datos de píxeles brutos de capturas de pantalla. Esto proporciona una "visión" del estado actual de la interfaz de usuario, identificando elementos como botones, menús, campos de texto y el diseño general de la página.
*   **Razonamiento Avanzado:** El modelo utiliza técnicas de aprendizaje por refuerzo para desarrollar capacidades de razonamiento que le permiten interpretar el contexto visual, planificar secuencias de acciones y adaptarse a situaciones dinámicas. Emplea una "cadena de pensamiento" (chain-of-thought) o monólogo interno para evaluar sus observaciones, seguir pasos intermedios y ajustar su estrategia de forma dinámica.
*   **Mecanismos de Acción:** CUA interactúa con el entorno digital mediante un ratón y un teclado virtuales. Esto le permite realizar acciones fundamentales como hacer clic, desplazarse, escribir texto y arrastrar elementos, replicando la interacción humana con una GUI.
*   **Bucle Iterativo Percepción-Razonamiento-Acción:** El funcionamiento de CUA se basa en un ciclo continuo:
    1.  **Percepción:** Se toman capturas de pantalla del estado actual del ordenador, que se añaden al contexto del modelo.
    2.  **Razonamiento:** CUA procesa estas capturas de pantalla junto con el historial de acciones y su monólogo interno para determinar el siguiente paso lógico.
    3.  **Acción:** Ejecuta la acción decidida (clic, desplazamiento, escritura) hasta que la tarea se completa o se requiere la intervención del usuario.
*   **Auto-corrección y Adaptabilidad:** Una característica fundamental es su capacidad para detectar cuando se encuentra con un desafío o comete un error, y luego utilizar sus capacidades de razonamiento para corregir su curso de acción. Esto le permite manejar la variabilidad inherente de las interfaces de usuario y los flujos de trabajo.
*   **Independencia de Plataforma:** Al operar a nivel de GUI (píxeles, ratón, teclado), CUA evita la necesidad de APIs específicas del sistema operativo o de la web, lo que lo convierte en una interfaz universal para la interacción con el mundo digital.

## 3. Implementación/Patrones Clave

La implementación de CUA se centra en un enfoque de aprendizaje por refuerzo para la interacción con GUI, permitiendo al agente aprender a navegar y operar en entornos digitales complejos. Los patrones clave de implementación incluyen:

*   **Entrenamiento Basado en Interacción:** CUA es entrenado para aprender a interactuar con GUIs a través de la observación y la experimentación, similar a cómo un humano aprende a usar un nuevo software. Esto implica la exposición a una amplia gama de interfaces y tareas para desarrollar una comprensión generalizada de la interacción con el ordenador.
*   **Representación del Estado Visual:** La información visual de la pantalla se convierte en una representación que el modelo puede procesar. Esto va más allá del simple reconocimiento de objetos, buscando comprender la semántica y la interactividad de los elementos de la GUI.
*   **Generación de Acciones Discretas:** Las acciones del agente se discretizan en operaciones de bajo nivel (clic en coordenadas X,Y, escribir texto, desplazar). El modelo aprende a seleccionar la secuencia correcta de estas acciones para lograr un objetivo.
*   **Manejo de la Incertidumbre:** Dada la naturaleza dinámica de las interfaces de usuario, CUA está diseñado para manejar la incertidumbre. Esto se logra a través de su capacidad de razonamiento, que le permite reevaluar el estado actual y ajustar su plan si una acción no produce el resultado esperado.
*   **Intervención Humana:** Para garantizar la seguridad y la fiabilidad, CUA está diseñado para solicitar la confirmación del usuario en puntos críticos, como la introducción de información sensible (credenciales de inicio de sesión, detalles de pago) o la resolución de CAPTCHAs. También puede ceder el control al usuario si se encuentra con una situación que no puede resolver de forma autónoma.
*   **Optimización de Tareas Repetitivas:** Un patrón de uso clave es la automatización de tareas repetitivas basadas en el navegador, como rellenar formularios, hacer pedidos en línea o gestionar citas. Los usuarios pueden guardar instrucciones personalizadas y prompts para estas tareas, lo que facilita su ejecución recurrente.

## 4. Lecciones para el Monstruo

Para nuestro propio agente, el "Monstruo", la arquitectura de OpenAI Operator CUA ofrece varias lecciones valiosas:

*   **Universalidad de la Interfaz:** La capacidad de CUA para interactuar con cualquier GUI a través de la percepción visual y acciones de ratón/teclado es un modelo poderoso. El Monstruo podría beneficiarse enormemente de una interfaz universal similar, que le permitiría operar en un espectro más amplio de aplicaciones y plataformas sin necesidad de integraciones específicas.
*   **Razonamiento Multimodal Integrado:** La combinación de capacidades de visión (GPT-4o) con razonamiento avanzado y aprendizaje por refuerzo es crucial. El Monstruo debería aspirar a una integración profunda de la percepción multimodal con sus capacidades de razonamiento para una comprensión más rica del entorno y una toma de decisiones más efectiva.
*   **Auto-corrección y Robustez:** La habilidad de CUA para auto-corregirse y adaptarse a errores es fundamental para la robustez en entornos del mundo real. El Monstruo debe incorporar mecanismos robustos de monitoreo y auto-corrección para manejar fallos inesperados y desviaciones del plan.
*   **Bucle Percepción-Razonamiento-Acción:** La estructura iterativa de CUA proporciona un marco claro para la operación autónoma. El Monstruo podría adoptar un ciclo similar para procesar información, tomar decisiones y ejecutar acciones de manera continua y adaptativa.
*   **Gestión de la Seguridad y la Intervención Humana:** El enfoque de CUA en la seguridad, con modos de "toma de control" y confirmaciones de usuario para acciones sensibles, es una plantilla esencial. El Monstruo debe implementar salvaguardias similares para garantizar que el usuario mantenga el control y para manejar información delicada de manera segura.
*   **Aprendizaje Continuo y Benchmarking:** La mejora de CUA a través de benchmarks como WebArena y WebVoyager subraya la importancia de la evaluación rigurosa y el aprendizaje continuo. El Monstruo debería tener un marco para la evaluación de su rendimiento y la integración de nuevos aprendizajes para cerrar la brecha con el rendimiento humano en tareas complejas.

---
*Referencias:*
[1] Introducing Operator | OpenAI: [https://openai.com/index/introducing-operator/](https://openai.com/index/introducing-operator/)
[2] Computer-Using Agent | OpenAI: [https://openai.com/index/computer-using-agent/](https://openai.com/index/computer-using-agent/)
[3] OpenAI Operator Explained: How AI Agents Actually Work: [https://anchorbrowser.io/blog/how-openai-operator-works-with-ai-agents](https://anchorbrowser.io/blog/how-openai-operator-works-with-ai-agents)
[4] Building Computer Use Agents with OpenAI's API: [https://www.riis.com/blog/building-computer-use-agents-with-openai-api](https://www.riis.com/blog/building-computer-use-agents-with-openai-api)
[5] Computer use | OpenAI API: [https://developers.openai.com/api/docs/guides/tools-computer-use](https://developers.openai.com/api/docs/guides/tools-computer-use)
[6] From model to agent: Equipping the Responses API with a computer environment: [https://openai.com/index/equip-responses-api-computer-environment/](https://openai.com/index/equip-responses-api-computer-environment/)
[7] OpenAI Operator - Cobus Greyling - Medium: [https://cobusgreyling.medium.com/openai-operator-845ee152aed0](https://cobusgreyling.medium.com/openai-operator-845ee152aed0)
[8] Threat modeling — Computer-Using Agent (CUA) — Part 1: [https://systemweakness.com/threat-modeling-computer-using-agent-cua-part-1-45560879be96](https://systemweakness.com/threat-modeling-computer-using-agent-cua-part-1-45560879be96)
[9] Using the CUA model in Azure OpenAI for procure to Pay automation: [https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/using-the-cua-model-in-azure-openai-for-procure-to-pay-automation/4407537](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/using-the-cua-model-in-azure-openai-for-procure-to-pay-automation/4407537)
[10] Sharing: Vision-based CUA on enterprise remote desktops: [https://github.com/openai/openai-cua-sample-app/issues/69](https://github.com/openai/openai-cua-sample-app/issues/69)
[11] Anthropic's Computer Use versus OpenAI's Computer-Using Agent (CUA): [https://workos.com/blog/anthropics-computer-use-versus-openais-computer-using-agent-cua](https://workos.com/blog/anthropics-computer-use-versus-openais-computer-using-agent-cua)
[12] A practical guide to building agents: [https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
[13] Deep Dive into OpenClaw: Architecture, Code & Ecosystem: [https://medium.com/@dingzhanjun/deep-dive-into-openclaw-architecture-code-ecosystem-e6180f34bd07](https://medium.com/@dingzhanjun/deep-dive-into-openclaw-architecture-code-ecosystem-e6180f34bd07)


---

# Biblia de Implementación: OpenAI Operator con Computer Use Agent (CUA) — Fase 2

## Introducción

El presente documento detalla una investigación profunda de Fase 2 sobre el agente de inteligencia artificial **OpenAI Operator con Computer Use Agent (CUA)**, lanzado entre 2025 y 2026. Este agente representa un avance significativo en la capacidad de las IAs para interactuar con entornos digitales, utilizando un control de computadora basado en píxeles. El objetivo de esta fase de investigación es expandir la comprensión técnica del agente, llevando la completitud de su Biblia de Implementación a un 90% mediante la recopilación de información técnica específica y detallada para cada uno de los módulos definidos.

El OpenAI Operator, potenciado por el CUA, se distingue por su habilidad para "ver" y "operar" cualquier software a través de su interfaz gráfica de usuario (GUI), emulando la interacción humana. Esto incluye la navegación web, la manipulación de aplicaciones de escritorio y la ejecución de código en entornos controlados. La información presentada a continuación se basa en artículos técnicos, papers, repositorios de GitHub, blogs oficiales y discusiones relevantes publicadas en los últimos seis meses, asegurando la actualidad y la relevancia de los datos.

---

## MÓDULO A: Ciclo del agente (loop/ReAct)

El Computer-Using Agent (CUA) de OpenAI opera a través de un **ciclo iterativo** que integra percepción, razonamiento y acción, permitiéndole interactuar con interfaces gráficas de usuario (GUI) de manera similar a como lo haría un humano. Este ciclo se describe a continuación:

### Percepción

En esta fase, el CUA recibe **capturas de pantalla** del entorno informático. Estas capturas de pantalla se añaden al contexto del modelo, proporcionando una instantánea visual del estado actual de la computadora. A través del procesamiento de **datos de píxeles en bruto**, el CUA es capaz de comprender lo que está ocurriendo en la pantalla [1].

### Razonamiento

Utilizando la información visual obtenida de las capturas de pantalla actuales y pasadas, el CUA razona sobre los siguientes pasos a seguir. Este proceso de razonamiento se potencia mediante el uso de la **cadena de pensamiento (chain-of-thought)**, lo que le permite al modelo mantener un monólogo interno. Este monólogo interno es fundamental para mejorar el rendimiento de la tarea, ya que permite al CUA evaluar sus observaciones, rastrear los pasos intermedios y adaptarse dinámicamente a los desafíos o cambios inesperados en el entorno [1].

### Acción

Basándose en su razonamiento, el CUA ejecuta acciones en la interfaz gráfica. Estas acciones incluyen operaciones como hacer clic, desplazarse (scroll) o escribir, utilizando un ratón y un teclado virtuales. El agente continúa realizando estas acciones hasta que determina que la tarea ha sido completada o que se requiere la intervención del usuario. Es importante destacar que, para acciones sensibles como la introducción de credenciales de inicio de sesión o la respuesta a formularios CAPTCHA, el CUA busca la confirmación del usuario, lo que añade una capa de seguridad y control [1].

Este enfoque permite al CUA navegar tareas de varios pasos, manejar errores y adaptarse a cambios inesperados, lo que le confiere la flexibilidad para realizar tareas digitales sin depender de APIs específicas del sistema operativo o de la web.

---

## MÓDULO B: Estados del agente

Aunque el Computer-Using Agent (CUA) de OpenAI no define explícitamente un conjunto formal de estados en el sentido de una máquina de estados finitos, su funcionamiento iterativo y sus mecanismos de manejo de errores implican una serie de estados operacionales y transiciones que guían su comportamiento. Estos estados se infieren de su ciclo de Percepción-Razonamiento-Acción y de cómo maneja las interrupciones y los fallos.

Los estados principales que se pueden inferir para el CUA incluyen:

### 1. Estado Inicial/Inactivo

El agente se encuentra en este estado antes de recibir una instrucción del usuario o después de completar una tarea. Está listo para aceptar nuevas directrices.

### 2. Estado de Ejecución de Tarea

Una vez que el CUA recibe una instrucción, entra en este estado. Aquí, el agente comienza su ciclo iterativo de Percepción, Razonamiento y Acción. Este es el estado operativo principal donde el agente intenta progresar hacia la finalización de la tarea.

*   **Sub-estado de Percepción**: El agente captura el estado visual actual de la interfaz (capturas de pantalla) y lo añade a su contexto.
*   **Sub-estado de Razonamiento**: El agente procesa la información visual y el contexto actual para determinar la siguiente acción lógica, utilizando un monólogo interno (chain-of-thought).
*   **Sub-estado de Acción**: El agente ejecuta una acción en la interfaz (clic, scroll, escritura) utilizando un ratón y teclado virtuales.

### 3. Estado de Espera de Confirmación del Usuario

El CUA transiciona a este estado cuando encuentra acciones sensibles que requieren la aprobación explícita del usuario. Ejemplos incluyen la introducción de credenciales de inicio de sesión o la respuesta a CAPTCHA. El agente permanece en este estado hasta que recibe la entrada del usuario [1].

### 4. Estado de Error/Recuperación

Este estado se activa cuando el agente encuentra un problema durante la ejecución de una acción o una llamada a una herramienta. El SDK de OpenAI Agents, que subyace a CUA, proporciona mecanismos robustos para el manejo de errores [2]:

*   **Detección de Excepciones**: Cuando una herramienta genera una excepción (por ejemplo, un tiempo de espera de la API, un error de red, un argumento de herramienta no válido), el SDK la captura.
*   **Notificación al LLM**: La excepción se convierte en un mensaje de error legible y se envía de vuelta al Large Language Model (LLM) como resultado de la herramienta. Esto permite que el LLM sea consciente del fallo.
*   **Razonamiento de Recuperación**: El LLM, al recibir el mensaje de error, entra en un sub-estado de razonamiento de recuperación. Aquí, decide cómo proceder: puede intentar una acción diferente, reintentar la misma acción (si el error es transitorio y la política de reintento lo permite), pedir aclaraciones al usuario o reportar el error como irrecuperable.
*   **Reintentos Automáticos**: Para fallos transitorios a nivel de la API del LLM (por ejemplo, problemas de red o límites de tasa), el SDK puede aplicar políticas de reintento configurables (con `max_retries`, `initial_delay`, `max_delay`, `backoff_factor`). Estos reintentos ocurren automáticamente antes de que el error llegue al código de la aplicación, lo que implica un sub-estado de 'reintento' antes de volver al estado de acción o razonamiento.

### 5. Estado de Tarea Completada

El agente transiciona a este estado cuando ha logrado el objetivo de la instrucción del usuario y no hay más acciones pendientes. En este punto, puede proporcionar un resultado final.

### 6. Estado de Tarea Fallida

Si el agente no puede completar la tarea después de múltiples intentos, o si se encuentra con un error irrecuperable, o si excede un límite de turnos (`MaxTurnsExceeded`), transiciona a este estado. En este caso, el agente reporta el fallo y puede proporcionar resultados parciales o un mensaje de error al usuario.

### Transiciones entre Estados

*   **Inactivo -> Ejecución de Tarea**: Al recibir una nueva instrucción.
*   **Ejecución de Tarea -> Espera de Confirmación del Usuario**: Al encontrar una acción sensible.
*   **Espera de Confirmación del Usuario -> Ejecución de Tarea**: Al recibir la confirmación del usuario.
*   **Ejecución de Tarea -> Error/Recuperación**: Al fallar una acción o herramienta.
*   **Error/Recuperación -> Ejecución de Tarea**: Si el LLM decide reintentar o tomar una acción correctiva.
*   **Error/Recuperación -> Tarea Fallida**: Si el error es irrecuperable o se agotan los reintentos.
*   **Ejecución de Tarea -> Tarea Completada**: Al finalizar exitosamente la tarea.
*   **Cualquier estado -> Inactivo**: Después de completar o fallar una tarea, o si se cancela la operación.

Este modelo de estados permite al CUA ser resiliente y adaptable, manejando la complejidad de las interacciones con GUI y recuperándose de fallos de manera autónoma o con asistencia del usuario.

---

## MÓDULO C: Sistema de herramientas

El sistema de herramientas de OpenAI Operator, impulsado por el Computer-Using Agent (CUA), permite al modelo interactuar con software a través de la interfaz de usuario. Este sistema se basa en la capacidad del modelo para inspeccionar capturas de pantalla y generar acciones de interfaz, o trabajar a través de un arnés personalizado que combina la interacción visual y programática con la UI. El modelo `gpt-5.4` y las versiones futuras están entrenados específicamente para este tipo de interacción [3].

El CUA puede operar a través de varias configuraciones de arnés, lo que demuestra su flexibilidad:

### 1. Herramienta `computer` integrada de la API de Responses

Esta es la opción predeterminada y está diseñada explícitamente para la interacción visual. El modelo devuelve acciones UI estructuradas como clics, escritura, desplazamiento y solicitudes de captura de pantalla. El flujo de trabajo de este bucle integrado es el siguiente [3]:

*   Se envía una tarea al modelo con la herramienta `computer` habilitada.
*   Se inspecciona la `computer_call` devuelta por el modelo.
*   Se ejecuta cada acción en el array `actions[]` devuelto, en orden.
*   Se captura la pantalla actualizada y se envía de vuelta como `computer_call_output`.
*   Este proceso se repite hasta que el modelo deja de devolver una `computer_call`.

Las acciones que el modelo puede solicitar incluyen:

*   `screenshot`: Solicita una nueva captura de pantalla para actualizar el contexto visual del modelo.
*   `click`: Realiza un clic en coordenadas específicas o en un elemento identificado en la pantalla.
*   `type`: Escribe texto en un campo de entrada.
*   `scroll`: Desplaza la vista en una dirección específica.

### 2. Herramientas o arneses personalizados

Para escenarios donde ya existe un marco de automatización (como Playwright, Selenium, VNC o un arnés basado en MCP), el modelo puede ser configurado para impulsar esa interfaz a través de llamadas de herramientas normales. Esto permite una integración con infraestructuras de automatización existentes [3].

### 3. Arnés de ejecución de código

Esta opción permite al modelo escribir y ejecutar scripts cortos en un entorno de tiempo de ejecución, lo que le permite moverse de manera flexible entre la interacción visual y la interacción programática de la UI, incluyendo flujos de trabajo basados en el DOM. Los modelos como `gpt-5.4` están explícitamente entrenados para sobresalir en este enfoque [3].

### Parámetros y Limitaciones

*   **Entrada Visual**: La entrada principal para el CUA son las capturas de pantalla, que proporcionan el contexto visual del estado actual de la interfaz de usuario. El modelo procesa estos datos de píxeles en bruto [1].
*   **Salida de Acciones**: La salida del modelo son acciones discretas que se ejecutan en el entorno. Estas acciones son de bajo nivel (clics, escritura, desplazamiento) y se traducen en interacciones con el ratón y el teclado virtuales [3].
*   **Seguridad y Aislamiento**: Se enfatiza la necesidad de ejecutar el uso de la computadora en un navegador aislado o una máquina virtual (VM). Se recomienda mantener a un humano en el bucle para acciones de alto impacto y tratar el contenido de la página como entrada no confiable. Para la automatización local del navegador, se sugieren salvaguardas como ejecutar el navegador en un entorno aislado, pasar un objeto `env` vacío para evitar heredar variables de entorno del host, y deshabilitar extensiones y acceso al sistema de archivos local cuando sea posible [3].
*   **Manejo de Errores**: El sistema de herramientas está integrado con el mecanismo de manejo de errores del SDK de Agentes de OpenAI, donde las excepciones de las herramientas se capturan, se convierten en mensajes de error y se retroalimentan al LLM para que razone sobre la recuperación [2].
*   **Límites de Tasa**: Aunque no se especifican límites exactos para las acciones de CUA, la API de OpenAI en general tiene límites de tasa que restringen el número de veces que un usuario o cliente puede acceder a los servicios dentro de un período de tiempo específico. Esto podría afectar la velocidad y el volumen de las operaciones del CUA si se realizan muchas llamadas a la API subyacente.
*   **Interacción Humana**: Para acciones sensibles como la entrada de credenciales de inicio de sesión o la respuesta a CAPTCHA, el CUA está diseñado para buscar la confirmación del usuario, lo que representa una limitación en su autonomía total para ciertas tareas [1].

En resumen, el sistema de herramientas del CUA es un conjunto flexible de capacidades que permiten al agente interactuar con cualquier GUI, ya sea a través de un bucle integrado de Percepción-Acción, arneses personalizados o ejecución de código, siempre priorizando la seguridad y la adaptabilidad.

---

## MÓDULO D: Ejecución de código

El OpenAI Operator, a través de su Computer-Using Agent (CUA) y el **Code Interpreter** (conocido internamente por el modelo como la "herramienta python"), tiene la capacidad de escribir y ejecutar código para resolver problemas complejos. Esta funcionalidad es crucial para tareas que involucran análisis de datos, codificación, matemáticas y manipulación de imágenes [4].

### Lenguajes de Programación

El Code Interpreter está diseñado para ejecutar código **Python** en un entorno controlado. Aunque el enfoque principal es Python, la capacidad de interactuar con la interfaz de usuario (UI) a través de acciones de píxeles y la posible integración con arneses de ejecución de código personalizados (como se mencionó en el Módulo C) sugiere que, en teoría, podría interactuar con aplicaciones que utilizan otros lenguajes, pero la ejecución directa de código se limita a Python [4].

### Entorno de Ejecución

El código Python se ejecuta en un **entorno aislado y sandboxed**, conocido como "contenedor" o "máquina virtual". Este contenedor proporciona un entorno seguro y efímero para la ejecución del código. Las características clave del entorno son [4]:

*   **Aislamiento**: Cada ejecución de código ocurre dentro de un contenedor virtualizado, lo que garantiza que el código no afecte el sistema host ni otros procesos. Esto es fundamental para la seguridad.
*   **Recursos**: Los contenedores pueden configurarse con diferentes límites de memoria (1GB por defecto, con opciones de 4GB, 16GB o 64GB), lo que permite manejar tareas con diferentes requisitos computacionales. Estos límites de memoria se aplican durante toda la vida útil del contenedor.
*   **Almacenamiento Efímero**: El contenedor tiene un espacio de disco efímero. Esto significa que cualquier archivo creado o modificado dentro del contenedor se perderá una vez que el contenedor expire o se reinicie. Se recomienda a los desarrolladores que almacenen cualquier dato persistente en sus propios sistemas.
*   **Gestión de Contenedores**: Los contenedores pueden crearse de dos maneras:
    *   **Modo Automático**: El sistema crea automáticamente un nuevo contenedor o reutiliza uno activo de una ejecución anterior. Esto simplifica la gestión para el usuario.
    *   **Modo Explícito**: Los desarrolladores pueden crear contenedores explícitamente a través de un endpoint `v1/containers`, especificando límites de memoria y gestionando su ciclo de vida.
*   **Caducidad**: Un contenedor caduca si no se utiliza durante 20 minutos. Una vez caducado, todos los datos asociados con el contenedor se descartan y no son recuperables. Es responsabilidad del usuario descargar los archivos necesarios mientras el contenedor está activo.

### Manejo de Errores

El Code Interpreter y el SDK de Agentes de OpenAI incorporan mecanismos robustos para el manejo de errores durante la ejecución de código [2, 4]:

*   **Reescritura y Reejecución Iterativa**: Una de las capacidades más destacadas es que el modelo puede escribir y ejecutar código de forma iterativa. Si un script falla al ejecutarse, el modelo puede analizar el error, reescribir el código y volver a intentarlo hasta que tenga éxito. Esto demuestra una capacidad de auto-corrección significativa.
*   **Retroalimentación al LLM**: Cuando se produce una excepción durante la ejecución de una herramienta (incluido el Code Interpreter), el SDK la captura, la convierte en un mensaje de error legible y la envía de vuelta al Large Language Model (LLM). Esto permite que el LLM entienda la naturaleza del fallo y razone sobre cómo proceder, ya sea reintentando, ajustando los parámetros o cambiando la estrategia.
*   **Excepciones Específicas**: El SDK de Agentes define tipos de excepciones como `ToolTimeoutError` (para herramientas que exceden un tiempo de espera) o `ModelBehaviorError` (cuando el modelo produce una salida inesperada). Estas excepciones son manejadas internamente y retroalimentadas al LLM.
*   **Manejo de Archivos**: El Code Interpreter puede generar sus propios archivos (por ejemplo, gráficos, CSV) dentro del contenedor. Estos archivos se citan en las anotaciones de los mensajes del asistente, permitiendo al usuario descargarlos. Los archivos de entrada del modelo se cargan automáticamente al contenedor.

En resumen, la ejecución de código en el CUA se realiza en un entorno Python sandboxed, con capacidades de auto-corrección y un manejo de errores integrado que permite al agente adaptarse y superar fallos, lo que lo convierte en una herramienta poderosa para tareas computacionales complejas.

---

## MÓDULO E: Sandbox y entorno

El OpenAI Operator, a través de su Computer-Using Agent (CUA) y el Code Interpreter, opera en entornos altamente controlados y aislados, lo que es fundamental para la seguridad, la reproducibilidad y la gestión de recursos. Estos entornos se diseñan para permitir que el agente interactúe con sistemas informáticos o ejecute código sin comprometer la integridad del sistema subyacente.

### Entorno de Ejecución Principal (CUA)

El CUA está diseñado para interactuar con interfaces gráficas de usuario (GUI) mediante la inspección de capturas de pantalla y la ejecución de acciones de UI (clics, escritura, desplazamiento). Para lograr esto de manera segura y efectiva, se recomiendan y utilizan varios tipos de entornos [3]:

*   **Navegador Aislado**: Para tareas basadas en la web, el CUA se ejecuta idealmente dentro de un navegador aislado. Esto se puede lograr utilizando marcos de automatización de navegador como Playwright o Selenium, configurados para operar en un entorno seguro. Las recomendaciones incluyen:
    *   Ejecutar el navegador en un entorno aislado (por ejemplo, un contenedor Docker o una máquina virtual ligera).
    *   Pasar un objeto `env` vacío para evitar que el navegador herede variables de entorno del host, lo que previene posibles fugas de información o accesos no autorizados.
    *   Deshabilitar extensiones y el acceso al sistema de archivos local siempre que sea posible para minimizar la superficie de ataque.
*   **Máquina Virtual (VM) o Contenedor Local**: Para tareas que requieren un entorno de escritorio más completo, el modelo puede operar contra una VM o un contenedor local. Esto implica traducir las acciones del agente en eventos de entrada a nivel del sistema operativo. Un ejemplo proporcionado por OpenAI es la creación de una imagen Docker con un escritorio Ubuntu, Xvfb (servidor X virtual), x11vnc y Firefox, lo que permite al agente interactuar con un entorno de escritorio completo de forma remota y aislada.

### Entorno de Ejecución del Code Interpreter

El Code Interpreter, utilizado para la ejecución de código Python, se basa en un concepto de "contenedor" o "máquina virtual" completamente sandboxed. Este entorno está diseñado específicamente para la ejecución segura de código y presenta las siguientes características [4]:

*   **Aislamiento Completo**: Cada instancia del Code Interpreter se ejecuta en un contenedor virtualizado, lo que garantiza un aislamiento estricto entre las ejecuciones de código y el sistema host. Esto previene que el código malicioso o erróneo afecte el sistema subyacente.
*   **Seguridad**: El entorno sandboxed limita las capacidades del código ejecutado, restringiendo el acceso a recursos del sistema, la red y otros procesos. Esto es crucial para la seguridad al permitir que el modelo escriba y ejecute código de forma autónoma.
*   **Recursos Asignados**: Los contenedores del Code Interpreter tienen recursos dedicados, principalmente memoria RAM, que pueden configurarse en diferentes niveles (1GB, 4GB, 16GB, 64GB). Estos recursos se asignan para la vida útil del contenedor, lo que permite al agente manejar tareas con diferentes demandas computacionales.
*   **Almacenamiento Efímero**: El entorno proporciona un espacio de disco efímero. Cualquier archivo creado o modificado durante la ejecución del código se almacena temporalmente dentro del contenedor y se elimina una vez que el contenedor caduca (después de 20 minutos de inactividad) o se reinicia. Esto asegura que no queden rastros persistentes de la ejecución del código.
*   **Gestión de Archivos**: Los archivos de entrada proporcionados al modelo se cargan automáticamente en el contenedor. El modelo también puede generar sus propios archivos (por ejemplo, gráficos, CSV) dentro del contenedor, los cuales pueden ser descargados por el usuario a través de anotaciones.

### Principios de Seguridad Generales

OpenAI enfatiza la importancia de la seguridad en ambos entornos. Se recomienda encarecidamente [3]:

*   Tratar todas las entradas externas (capturas de pantalla, texto de página, salidas de herramientas, PDFs, correos electrónicos, chats) como **entrada no confiable**. Solo las instrucciones directas del usuario deben considerarse permisos.
*   Mantener a un **humano en el bucle** para acciones de alto impacto o sensibles, como la introducción de credenciales o la aprobación de transacciones.

En resumen, el sandbox y el entorno de ejecución del OpenAI Operator y CUA se caracterizan por un aislamiento robusto, medidas de seguridad estrictas y una gestión de recursos flexible, lo que permite al agente operar de manera autónoma y segura en una variedad de tareas digitales.

---

## MÓDULO F: Memoria y contexto

La gestión de la memoria y el contexto en el OpenAI Operator, impulsado por el Computer-Using Agent (CUA), es fundamental para su capacidad de mantener el estado, recordar interacciones pasadas y razonar de manera coherente a lo largo de una tarea. El SDK de Agentes de OpenAI distingue entre dos clases principales de contexto:

### 1. Contexto local para el código (Local Context)

Este se refiere a los datos y dependencias que el código del desarrollador puede necesitar durante la ejecución de funciones de herramientas, callbacks de ciclo de vida, etc. Se representa a través de la clase `RunContextWrapper` [5].

*   **Persistencia de estado local**: Los desarrolladores pueden crear cualquier objeto Python (comúnmente un dataclass o un objeto Pydantic) y pasarlo a los métodos de ejecución (`Runner.run(..., context=whatever)`). Este objeto de contexto es accesible a través de `wrapper.context` en todas las llamadas a herramientas y hooks de ciclo de vida. Es importante destacar que este objeto de contexto **no se envía al LLM**; es puramente un objeto local que el código puede leer, escribir y sobre el que puede llamar métodos.
*   **Uso del contexto local**: Se utiliza para datos contextuales de la ejecución (como nombre de usuario, ID de usuario), dependencias (objetos de logger, fetchers de datos) y funciones auxiliares.
*   **Compartición de contexto**: Dentro de una misma ejecución, los `wrappers` derivados comparten el mismo contexto de aplicación subyacente, estado de aprobación y seguimiento de uso. Las ejecuciones anidadas de `Agent.as_tool()` pueden adjuntar una `tool_input` diferente, pero no obtienen una copia aislada del estado de la aplicación por defecto.
*   **Consideraciones de seguridad**: Si se serializa un `RunState` para flujos de trabajo con intervención humana o trabajos duraderos, los metadatos de tiempo de ejecución se guardan con el estado. Se recomienda evitar colocar secretos en `RunContextWrapper.context` si se tiene la intención de persistir o transmitir el estado serializado.

### 2. Contexto disponible para los LLMs (Agent/LLM Context)

Esta es la información que el Large Language Model (LLM) puede "ver" cuando genera una respuesta. La única forma en que el LLM puede acceder a nuevos datos es si estos se hacen disponibles en el historial de conversación. Hay varias estrategias para lograr esto [5]:

*   **Instrucciones del Agente (System Prompt)**: Se puede añadir información a las `instructions` del agente. Estas pueden ser cadenas estáticas o funciones dinámicas que reciben el contexto y generan una cadena. Esto es útil para información que es siempre relevante (por ejemplo, el nombre del usuario o la fecha actual).
*   **Entrada en `Runner.run`**: Se puede añadir información directamente a la `input` al llamar a las funciones `Runner.run`. Esto es similar a las instrucciones, pero permite mensajes con una posición más baja en la cadena de comandos.
*   **Herramientas de Función (Function Tools)**: Exponer información a través de herramientas de función es útil para el contexto bajo demanda. El LLM decide cuándo necesita ciertos datos y puede llamar a la herramienta para obtenerlos. Por ejemplo, una herramienta puede recuperar información de una base de datos o un servicio externo.
*   **Recuperación y Búsqueda Web**: Se pueden utilizar herramientas especiales para recuperar datos relevantes de archivos o bases de datos (recuperación) o de la web (búsqueda web). Esto es crucial para "fundamentar" la respuesta del LLM en datos contextuales relevantes y actualizados.

### Ventana de Contexto (Context Window)

La ventana de contexto se refiere a la cantidad de información (tokens) que el LLM puede procesar en una sola interacción. Modelos como `gpt-5.4` y `gpt-4.1` (mencionado en algunas discusiones) tienen ventanas de contexto grandes, lo que les permite recordar conversaciones más largas y procesar documentos más extensos. Sin embargo, la información específica sobre el tamaño exacto de la ventana de contexto para el CUA o el Operator no se detalla explícitamente en la documentación principal, pero se infiere que es lo suficientemente grande como para manejar el historial de interacciones, capturas de pantalla y resultados de herramientas necesarios para tareas complejas de uso de la computadora.

### Persistencia del Estado del Agente

La persistencia del estado del agente se logra a través de la combinación de la gestión del contexto local (para el código del desarrollador) y la gestión del contexto del LLM (para el historial de conversación). Además, la capacidad de serializar un `RunState` permite guardar el estado de una ejecución para flujos de trabajo duraderos o para la intervención humana, lo que implica que el estado puede ser guardado y restaurado para continuar una tarea en otro momento o por otro agente/a agente/humano [5].

---

## MÓDULO G: Browser/GUI

El OpenAI Operator, a través de su Computer-Using Agent (CUA), está diseñado para interactuar con interfaces gráficas de usuario (GUI) y navegadores web de una manera que imita la interacción humana. Su capacidad para "ver" y "actuar" en entornos digitales es fundamental para su funcionamiento [1].

### Interacción Basada en Píxeles

El CUA procesa **datos de píxeles en bruto** obtenidos de capturas de pantalla del entorno informático. Esta aproximación le permite comprender el estado actual de la interfaz de usuario, incluyendo la disposición de botones, menús, campos de texto y otros elementos visuales, sin depender de APIs específicas del sistema operativo o de la web. Esto le confiere una gran flexibilidad para operar en diversos entornos digitales [1].

### Acciones de Interfaz de Usuario

Para interactuar con la GUI, el CUA utiliza un **ratón y un teclado virtuales**. Esto le permite ejecutar una variedad de acciones, incluyendo [1]:

*   **Clics**: Identifica elementos interactivos en la pantalla y simula clics de ratón sobre ellos.
*   **Escritura**: Introduce texto en campos de entrada, formularios y otras áreas editables.
*   **Desplazamiento (Scrolling)**: Navega por el contenido de la página o la ventana mediante el desplazamiento vertical u horizontal.
*   **Navegación Autónoma**: Puede abrir aplicaciones, hacer clic en botones, rellenar formularios y navegar por flujos de trabajo de varias páginas de forma autónoma.

### Manejo de Inicios de Sesión y Acciones Sensibles

Una característica importante del CUA es su enfoque en la seguridad y la supervisión humana para acciones sensibles. Para tareas como la introducción de credenciales de inicio de sesión o la respuesta a CAPTCHAs, el CUA está diseñado para **solicitar la confirmación o intervención del usuario**. Esto asegura que la información sensible no sea manejada de forma autónoma sin la aprobación explícita del usuario, añadiendo una capa de seguridad y control [1].

### Integración con Marcos de Automatización

Aunque el CUA puede operar de forma nativa a través de su herramienta `computer` integrada, también puede integrarse con marcos de automatización de navegador existentes como **Playwright** o **Selenium**. Esto permite a los desarrolladores aprovechar sus infraestructuras de automatización ya establecidas y configurar el modelo para que impulse esas interfaces a través de llamadas de herramientas normales. Para la automatización local del navegador, se recomiendan prácticas de seguridad como ejecutar el navegador en un entorno aislado, deshabilitar extensiones y el acceso al sistema de archivos local [3].

### Operación en Entornos de Escritorio Completos

Más allá de la interacción con navegadores, el CUA tiene la capacidad de operar en **entornos de escritorio completos**, incluyendo sistemas operativos como macOS, Windows y Linux. Esto significa que puede interactuar con diversas aplicaciones de escritorio, no solo con navegadores web, lo que amplía significativamente su rango de acción para automatizar tareas digitales complejas.

En resumen, el CUA de OpenAI Operator interactúa con el navegador y la GUI mediante una combinación de percepción visual basada en píxeles y acciones simuladas de ratón y teclado, con un énfasis en la seguridad y la intervención humana para acciones críticas, y la flexibilidad para integrarse en diversos entornos de automatización.

---

## MÓDULO H: Multi-agente

El OpenAI Operator, a través de su Computer-Using Agent (CUA) y el SDK de Agentes de OpenAI, soporta la creación y coordinación de sistemas multi-agente, lo que permite abordar tareas complejas que requieren la colaboración de múltiples entidades de IA. La orquestación se refiere al flujo de agentes en una aplicación: qué agentes se ejecutan, en qué orden y cómo deciden qué sucede a continuación. Existen dos enfoques principales para orquestar agentes, que pueden combinarse [6]:

### 1. Orquestación vía LLM (Large Language Model)

En este patrón, el LLM toma las decisiones. Un agente es un LLM equipado con instrucciones, herramientas y "handoffs" (delegaciones). Dada una tarea abierta, el LLM puede planificar autónomamente cómo abordará la tarea, utilizando herramientas para realizar acciones y adquirir datos, y delegando tareas a sub-agentes. Por ejemplo, un agente de investigación podría estar equipado con herramientas como [6]:

*   Búsqueda web para encontrar información en línea.
*   Búsqueda y recuperación de archivos para examinar datos propietarios.
*   Uso de la computadora (CUA) para realizar acciones en una computadora.
*   Ejecución de código para análisis de datos.
*   Delegaciones a agentes especializados en planificación, redacción de informes, etc.

### 2. Orquestación vía código

Este enfoque determina el flujo de agentes mediante el código del desarrollador, lo que hace que las tareas sean más deterministas y predecibles en términos de velocidad, costo y rendimiento. Los patrones comunes incluyen [6]:

*   Uso de **salidas estructuradas** para generar datos bien formados que el código puede inspeccionar. Por ejemplo, un agente podría clasificar una tarea en categorías, y el código selecciona el siguiente agente basándose en esa categoría.
*   **Encadenamiento de múltiples agentes** transformando la salida de uno en la entrada del siguiente. Esto permite descomponer una tarea compleja en una serie de pasos secuenciales.
*   Ejecutar el agente que realiza la tarea en un bucle `while` con un agente que evalúa y proporciona retroalimentación, hasta que el evaluador aprueba la salida.
*   Ejecutar múltiples agentes en paralelo, por ejemplo, utilizando primitivas de Python como `asyncio.gather`, cuando las tareas no dependen entre sí.

### Patrones Centrales del SDK para la Colaboración Multi-agente

El SDK de Python de OpenAI Agents destaca dos patrones de orquestación principales [6]:

*   **Agentes como herramientas (Agents as tools)**: Un agente gestor mantiene el control de la conversación y llama a agentes especialistas a través de `Agent.as_tool()`. Este patrón es ideal cuando se desea que un agente principal sea el propietario de la respuesta final, combine las salidas de múltiples especialistas o aplique guardarraíles compartidos en un solo lugar. El especialista ayuda con una subtarea acotada pero no toma el control de la conversación orientada al usuario.

*   **Delegaciones (Handoffs)**: Un agente de triaje dirige la conversación a un especialista, y ese especialista se convierte en el agente activo para el resto del turno. Este patrón es adecuado cuando el enrutamiento es parte del flujo de trabajo y se desea que el especialista elegido sea el responsable de la siguiente parte de la interacción, manteniendo los prompts enfocados o intercambiando instrucciones sin que el gestor narre el resultado.

Es posible combinar ambos patrones: un agente de triaje podría delegar a un especialista, y ese especialista aún podría llamar a otros agentes como herramientas para subtareas específicas.

### Coordinación de Sub-agentes

La coordinación se logra mediante el intercambio de contexto y la definición clara de roles y responsabilidades. En el patrón de "Agentes como herramientas", el agente gestor coordina implícitamente al llamar a los especialistas. En el patrón de "Delegaciones", la coordinación se realiza mediante la transferencia explícita del control. El contexto compartido (como el historial de conversación) es crucial para que los agentes mantengan una comprensión común de la tarea y el progreso.

En resumen, el OpenAI Operator y CUA, a través del SDK de Agentes, ofrecen una infraestructura flexible para construir sistemas multi-agente, permitiendo tanto la orquestación impulsada por LLM para tareas abiertas como la orquestación basada en código para un control más determinista, con patrones claros para la colaboración y delegación de tareas entre agentes especializados.

---

## MÓDULO I: Integraciones

El OpenAI Operator, a través de su Computer-Using Agent (CUA), presenta un enfoque innovador para las integraciones, priorizando la interacción directa con la interfaz de usuario (UI) sobre las integraciones API tradicionales. Sin embargo, también ofrece vías para la conectividad basada en API a través del SDK de Agentes de OpenAI [7].

### Integración Primaria: Interacción con la UI sin API

La característica distintiva del CUA es su capacidad para interactuar con cualquier software a través de su interfaz gráfica de usuario, de manera similar a como lo haría un humano. Esto significa que el CUA puede "integrarse" con una vasta gama de servicios y aplicaciones **sin requerir APIs específicas o integraciones personalizadas**. Al procesar capturas de pantalla y emitir acciones de UI (clics, escritura, desplazamiento), el agente puede operar en entornos web y de escritorio, realizando tareas como [7]:

*   Rellenar formularios en sitios web.
*   Navegar por aplicaciones de software.
*   Interactuar con elementos visuales en cualquier GUI.

Este enfoque permite al CUA trabajar con servicios que no exponen APIs públicas o que tienen APIs complejas, simplemente interactuando con ellos a nivel de la UI. La promesa es que el CUA puede tomar acción en la web "sin APIs y sin integraciones personalizadas" [7].

### Integraciones a través del SDK de Agentes de OpenAI (Function Tools)

Aunque el CUA se enfoca en la interacción UI, el SDK de Agentes de OpenAI, que subyace a la construcción de agentes, permite la integración con servicios externos a través de **herramientas de función (function tools)**. Estas herramientas permiten a los agentes [7]:

*   **Conectarse con servicios externos**: Los desarrolladores pueden definir herramientas que encapsulen llamadas a APIs de terceros, permitiendo al agente acceder a información en tiempo real o realizar acciones en otros sistemas.
*   **Acceder a información en tiempo real**: Mediante la invocación de estas herramientas, el agente puede consultar bases de datos, servicios web o cualquier otra fuente de datos externa.
*   **Realizar acciones programáticas**: Más allá de la interacción UI, las herramientas de función permiten al agente ejecutar código o interactuar con sistemas que requieren una interfaz programática.

### OAuth y Mecanismos de Autenticación

La documentación no detalla explícitamente el soporte nativo de OAuth dentro del CUA para la interacción UI. Sin embargo, dado que el CUA está diseñado para solicitar la confirmación del usuario para acciones sensibles como la introducción de credenciales de inicio de sesión, se infiere que para servicios que requieren autenticación, el CUA podría [1]:

*   **Solicitar al usuario que complete el proceso de inicio de sesión**: El agente podría navegar a la página de inicio de sesión y esperar la intervención humana para introducir las credenciales o completar un flujo OAuth.
*   **Utilizar credenciales almacenadas de forma segura**: En un entorno controlado y con la aprobación del usuario, las credenciales podrían ser proporcionadas al agente para su uso en formularios de inicio de sesión.

Para las integraciones basadas en APIs a través de herramientas de función, la gestión de la autenticación (incluido OAuth) recaería en la implementación de la herramienta de función por parte del desarrollador. Es decir, el desarrollador sería responsable de configurar la herramienta para manejar la autenticación necesaria con el servicio externo.

### Disponibilidad de CUA en la API

OpenAI ha indicado planes para exponer el modelo que impulsa Operator (CUA) en la API. Esto permitiría a los desarrolladores utilizar CUA para construir sus propios agentes de uso de la computadora, lo que abriría nuevas vías para la integración programática y la personalización de las capacidades del CUA [7].

En resumen, las integraciones del OpenAI Operator y CUA se caracterizan por una fuerte capacidad de interacción UI sin necesidad de APIs, complementada por la flexibilidad del SDK de Agentes para conectar con servicios externos a través de herramientas de función, con un enfoque en la seguridad y la intervención humana para la autenticación sensible.

---

## MÓDULO J: Multimodal

El OpenAI Operator, a través de su Computer-Using Agent (CUA), posee capacidades multimodales significativas, siendo la visión el pilar fundamental de su interacción con los entornos digitales. Estas capacidades se derivan principalmente del uso de modelos avanzados de OpenAI, en particular GPT-4o [8].

### Visión (Imágenes)

La capacidad más destacada del CUA es su **visión computacional**, que le permite "ver" y comprender el contenido de una pantalla. Esto se logra mediante [1, 8]:

*   **Procesamiento de datos de píxeles en bruto**: El CUA analiza las capturas de pantalla del entorno informático como datos de píxeles en bruto. Esto le permite identificar y comprender la disposición de los elementos de la interfaz gráfica de usuario (GUI), como botones, campos de texto, menús y otros componentes visuales, sin depender de la estructura subyacente del DOM o de APIs específicas.
*   **GPT-4o**: El CUA está impulsado por GPT-4o, un modelo multimodal de última generación de OpenAI. GPT-4o es capaz de razonar a través de audio, visión y texto en tiempo real. Esto significa que la capacidad del CUA para interpretar y comprender las capturas de pantalla se beneficia directamente de las avanzadas capacidades de visión de GPT-4o, permitiéndole entender el contexto visual y planificar acciones de manera efectiva.
*   **Mejora de la inteligencia visual**: El Code Interpreter, una herramienta utilizada por el CUA, también contribuye a la multimodalidad al permitir que el modelo procese y transforme imágenes (recortar, hacer zoom, rotar), lo que potencia aún más su inteligencia visual para tareas específicas [4].

### Audio

Aunque la interacción principal del CUA con el entorno se centra en la visión y las acciones de UI, OpenAI ha lanzado modelos de audio de próxima generación (speech-to-text y text-to-speech) en su API. Si bien no se especifica directamente que el CUA los utilice para interactuar con el entorno de la computadora (por ejemplo, escuchar sonidos del sistema o dictar comandos), la integración de GPT-4o, que puede razonar a través del audio, sugiere un potencial para futuras capacidades de procesamiento de audio o para la interacción con el usuario a través de voz. Es plausible que, en escenarios donde el agente necesite interactuar con aplicaciones de audio o responder a comandos de voz, estas capacidades puedan ser integradas [8].

### Video

La capacidad de procesar "datos de píxeles en bruto" de capturas de pantalla implica que el CUA está constantemente analizando secuencias de imágenes (frames) para comprender los cambios en la UI. Esto es, en esencia, una forma de procesamiento de video a nivel de la interfaz. Aunque no se menciona explícitamente el análisis de contenido de video incrustado en páginas web o aplicaciones, la base tecnológica para ello existe a través de las capacidades de visión de GPT-4o y el procesamiento de secuencias visuales [8].

En resumen, el OpenAI Operator y CUA son inherentemente multimodales, con una fuerte dependencia de las capacidades de visión de GPT-4o para comprender y navegar por las interfaces gráficas de usuario. Existe un potencial claro para la integración de capacidades de audio y un procesamiento de video implícito a través del análisis continuo de capturas de pantalla.

---

## MÓDULO K: Límites y errores

El OpenAI Operator, impulsado por el Computer-Using Agent (CUA), aunque representa un avance significativo en la automatización de tareas digitales, aún se encuentra en sus primeras etapas de desarrollo y presenta una serie de límites y desafíos. Sin embargo, también incorpora mecanismos robustos para el manejo y la recuperación de errores.

### Límites y Qué No Puede Hacer

1.  **Etapa Temprana de Desarrollo**: El CUA es una tecnología en evolución. Las primeras impresiones de los usuarios y los informes sugieren que aún puede ser "inacabado, infructuoso e inseguro" en ciertas situaciones, lo que indica que no es completamente fiable para todas las tareas complejas o críticas [9].
2.  **Interacción con Campos de Entrada**: Se han reportado errores específicos donde el Operator no es capaz de escribir en campos de entrada, lo que limita su capacidad para completar formularios o interactuar con elementos de texto de manera consistente [10].
3.  **Desafíos de Verificación Humana**: El CUA encuentra dificultades con mecanismos de verificación diseñados para humanos, como CAPTCHAs, contraseñas de un solo uso (OTPs) y autenticación de dos factores (2FA). Para estas acciones sensibles, el agente está diseñado para solicitar la intervención o confirmación del usuario, lo que interrumpe la autonomía total [1].
4.  **Enfoque en el Navegador**: Aunque el CUA puede operar en entornos de escritorio, su "enfoque láser en el navegador" sugiere que puede tener limitaciones o un rendimiento subóptimo en tareas que requieren una interacción profunda y compleja con aplicaciones de escritorio fuera del navegador [11].
5.  **Vulnerabilidad a Ataques Adversarios**: Existe la preocupación de que el CUA, al depender de la visión computacional, pueda ser susceptible a ataques adversarios. Un atacante podría crear GUIs falsas o sitios web diseñados para engañar al agente, lo que representa un riesgo de seguridad [12].
6.  **Errores Genéricos y Congelamientos**: Los usuarios han reportado que el Operator a veces se "congela" y muestra mensajes genéricos como "Algo salió mal. Inténtalo de nuevo", lo que indica fallos internos que no se comunican de manera específica al usuario [13].

### Cómo Falla y Cómo se Recupera

El CUA y el SDK de Agentes de OpenAI están diseñados con una arquitectura que permite la detección y recuperación de errores, aunque no siempre de forma transparente o exitosa para el usuario final:

1.  **Ciclo de Percepción-Razonamiento-Acción con Retroalimentación**: Como se describe en el Módulo A, el CUA opera en un ciclo iterativo. Si una acción falla o el estado de la UI no es el esperado (Percepción), el agente puede usar su capacidad de Razonamiento (chain-of-thought) para evaluar el problema, adaptar su plan y intentar una acción diferente o reintentar la misma. Este "bucle de retroalimentación" es clave para su capacidad de adaptarse a condiciones cambiantes y recuperarse de errores [1].
2.  **Manejo de Errores del SDK de Agentes**: El SDK proporciona múltiples capas de manejo de errores [2]:
    *   **Tipos de Excepciones**: Define excepciones específicas (`MaxTurnsExceeded`, `ModelBehaviorError`, `UserError`, `InputGuardrailTripwireTriggered`, `OutputGuardrailTripwireTriggered`, `ToolTimeoutError`) para diferentes modos de fallo. Estas excepciones son capturadas internamente.
    *   **Recuperación de Errores de Herramientas**: Cuando una herramienta (incluyendo las acciones de CUA o el Code Interpreter) genera una excepción, el SDK la captura, convierte el mensaje de error a una cadena y lo envía de vuelta al LLM como resultado de la herramienta. Esto permite que el LLM sea consciente del fallo y decida cómo proceder: reintentar, probar un enfoque diferente o reportar el error.
    *   **Políticas de Reintento**: Para fallos transitorios a nivel de la API del LLM (por ejemplo, problemas de red o límites de tasa), el SDK soporta políticas de reintento configurables. Estos reintentos ocurren automáticamente antes de que el error llegue al código de la aplicación, mejorando la resiliencia.
    *   **Hooks para Manejo de Errores Personalizado**: Los desarrolladores pueden implementar lógica de manejo de errores personalizada para adaptar el comportamiento del agente a necesidades específicas.
3.  **Auto-corrección en Ejecución de Código**: En el contexto del Code Interpreter (Módulo D), si el código Python escrito por el agente falla al ejecutarse, el modelo puede analizar el error, reescribir el código y volver a intentarlo hasta que tenga éxito, demostrando una forma de auto-recuperación [4].
4.  **Intervención Humana**: Para errores irrecuperables o situaciones sensibles, el sistema está diseñado para escalar a la intervención humana, solicitando ayuda o confirmación del usuario. Esto actúa como una última línea de defensa para la recuperación [1].

En resumen, mientras que el OpenAI Operator y CUA enfrentan límites inherentes a su etapa de desarrollo y a la complejidad de la interacción UI, están equipados con mecanismos de auto-corrección y manejo de errores que les permiten adaptarse y recuperarse de muchos fallos, aunque la intervención humana sigue siendo crucial para ciertos desafíos.

---

## MÓDULO L: Benchmarks

El OpenAI Operator, impulsado por el Computer-Using Agent (CUA), ha sido evaluado en varios benchmarks estándar para agentes de uso de la computadora y agentes web, demostrando un rendimiento notable en comparación con otros modelos. Estos benchmarks miden la capacidad del agente para completar tareas en entornos digitales complejos [1, 14].

Los principales benchmarks y resultados reportados para el CUA incluyen:

*   **OSWorld**: Este benchmark evalúa la capacidad de los agentes multimodales para realizar tareas de uso de la computadora de propósito general en entornos de escritorio, incluyendo aplicaciones web y de escritorio, E/S de archivos del sistema operativo y flujos de trabajo que abarcan múltiples dominios. El CUA ha logrado una tasa de éxito del **38.1%** en tareas completas de uso de la computadora en OSWorld [1, 14]. Algunas fuentes mencionan un 38% o 38.4% de éxito en este benchmark [15].

*   **WebArena**: Este benchmark se centra en tareas basadas en la web. El CUA ha alcanzado una tasa de éxito del **58.1%** en WebArena [1, 14]. Este resultado es significativo para la navegación y operación en entornos web.

*   **WebVoyager**: Similar a WebArena, WebVoyager es otro benchmark para tareas basadas en la web. El CUA ha demostrado un rendimiento aún más fuerte aquí, con una tasa de éxito del **87%** [1, 14].

*   **Mind2Web**: Algunas revisiones de OpenAI Operator en 2026 mencionan una puntuación del **43%** en Mind2Web, otro benchmark relevante para la interacción web [16].

### Contexto y Comparaciones

*   Estos resultados establecen un nuevo estado del arte en los benchmarks de uso de la computadora y uso del navegador, utilizando la misma interfaz universal de pantalla, ratón y teclado [1].
*   Aunque el CUA muestra un rendimiento sólido, especialmente en tareas web, aún se encuentra por debajo del rendimiento humano en OSWorld (72.4% para humanos), lo que indica áreas para futuras mejoras [1].
*   Existen agentes de código abierto que han logrado superar al CUA de OpenAI en 3 de 4 benchmarks, lo que sugiere un panorama competitivo en el desarrollo de agentes de uso de la computadora [17].
*   La evaluación del CUA se realiza en entornos (navegador/VM) y con parámetros de muestreo y prompts específicos, lo que se detalla en documentos adicionales de evaluación de OpenAI [18].

En resumen, el OpenAI Operator y CUA han establecido un alto estándar en los benchmarks de uso de la computadora y web, demostrando su capacidad para interactuar eficazmente con entornos digitales. Sin embargo, la investigación y el desarrollo continúan para cerrar la brecha con el rendimiento humano y mejorar aún más su robustez y autonomía.

---

## Lecciones para el Monstruo

La investigación sobre el OpenAI Operator y su Computer-Using Agent (CUA) ofrece varias lecciones valiosas para el desarrollo de agentes de IA avanzados, especialmente aquellos que buscan interactuar con entornos digitales de manera autónoma:

1.  **La Visión Basada en Píxeles es un Habilitador Clave**: La capacidad del CUA para procesar datos de píxeles en bruto y comprender la GUI sin depender de APIs específicas del sistema operativo o del DOM es una lección fundamental. Esto permite una flexibilidad y generalización sin precedentes para interactuar con cualquier software, independientemente de su tecnología subyacente. Para el Monstruo, esto sugiere que invertir en capacidades de visión robustas y de bajo nivel es crucial para la interacción universal con el entorno digital.

2.  **El Ciclo Percepción-Razonamiento-Acción con Chain-of-Thought es Esencial para la Adaptabilidad**: El bucle iterativo del CUA, que incluye un monólogo interno (chain-of-thought) para el razonamiento, es vital para su capacidad de adaptarse a entornos dinámicos y recuperarse de errores. Esta estrategia permite al agente evaluar el estado actual, planificar los siguientes pasos y ajustar su comportamiento. El Monstruo debe adoptar un ciclo de toma de decisiones similar, con un fuerte énfasis en el razonamiento explícito y la auto-corrección.

3.  **La Seguridad y la Intervención Humana son Imperativas para Acciones Sensibles**: La implementación del CUA subraya la importancia de la supervisión humana para tareas de alto impacto, como inicios de sesión o transacciones. La necesidad de solicitar confirmación del usuario para acciones sensibles no es una limitación, sino una característica de seguridad crítica. El Monstruo debe integrar mecanismos claros para la intervención humana y la escalada en situaciones de riesgo o cuando se maneja información sensible.

4.  **La Ejecución de Código en un Sandbox Aislado Potencia la Versatilidad y la Seguridad**: La capacidad del Code Interpreter para ejecutar código Python en un entorno sandboxed y efímero es una herramienta poderosa. Permite al agente realizar análisis de datos complejos, manipular archivos y resolver problemas programáticos de forma segura. El Monstruo debería incorporar un entorno de ejecución de código aislado y robusto para ampliar sus capacidades más allá de la interacción UI directa.

5.  **La Orquestación Flexible de Agentes Permite Abordar Tareas Complejas**: El SDK de Agentes de OpenAI demuestra que la combinación de orquestación impulsada por LLM y orquestación basada en código, junto con patrones como "agentes como herramientas" y "delegaciones", es fundamental para construir sistemas multi-agente capaces de abordar tareas complejas. El Monstruo debe desarrollar un marco de orquestación flexible que permita la colaboración de agentes especializados y la delegación dinámica de subtareas.

6.  **La Resiliencia a Través del Manejo de Errores Iterativo es Clave**: La capacidad del CUA para analizar errores, reescribir código y reintentar acciones fallidas demuestra una resiliencia significativa. El Monstruo debe implementar estrategias de manejo de errores que permitan la auto-diagnóstico, la adaptación del plan y la recuperación autónoma de fallos, minimizando la necesidad de intervención externa.

---

## Referencias

[1] OpenAI. (2025, Enero 23). *Computer-Using Agent*. Recuperado de [https://openai.com/index/computer-using-agent/](https://openai.com/index/computer-using-agent/)
[2] CallSphere. (n.d.). *OpenAI Agents SDK: Error Handling, Exceptions, Retries, Recovery*. Recuperado de [https://callsphere.tech/blog/openai-agents-sdk-error-handling-exceptions-retries-recovery](https://callsphere.tech/blog/openai-agents-sdk-error-handling-exceptions-retries-recovery)
[3] OpenAI Developers. (n.d.). *Computer use | OpenAI API*. Recuperado de [https://developers.openai.com/api/docs/guides/tools-computer-use](https://developers.openai.com/api/docs/guides/tools-computer-use)
[4] OpenAI Developers. (n.d.). *Code Interpreter | OpenAI API*. Recuperado de [https://developers.openai.com/api/docs/guides/tools-code-interpreter](https://developers.openai.com/api/docs/guides/tools-code-interpreter)
[5] OpenAI GitHub. (n.d.). *Context management - OpenAI Agents SDK*. Recuperado de [https://openai.github.io/openai-agents-python/context/](https://openai.github.io/openai-agents-python/context/)
[6] OpenAI GitHub. (n.d.). *Agent orchestration - OpenAI Agents SDK*. Recuperado de [https://openai.github.io/openai-agents-python/multi_agent/](https://openai.github.io/openai-agents-python/multi_agent/)
[7] OpenAI. (2025, Enero 23). *Introducing Operator*. Recuperado de [https://openai.com/index/introducing-operator/](https://openai.com/index/introducing-operator/)
[8] OpenAI. (2024, Mayo 13). *Hello GPT-4o*. Recuperado de [https://openai.com/index/hello-gpt-4o/](https://openai.com/index/hello-gpt-4o/)
[9] Furze, L. (2025, Julio 19). *Initial Impressions of OpenAI's Agents: Unfinished, Unsuccessful, and Unsafe*. Recuperado de [https://leonfurze.com/2025/07/19/initial-impressions-of-openais-agents-unfinished-unsuccessful-and-unsafe/](https://leonfurze.com/2025/07/19/initial-impressions-of-openais-agents-unfinished-unsuccessful-and-unsafe/)
[10] OpenAI Community. (2025, Julio 1). *Operator is broken – and it's definitely NOT a browser or OS issue*. Recuperado de [https://community.openai.com/t/operator-is-broken-and-it-s-definitely-not-a-browser-or-os-issue/1304436](https://community.openai.com/t/operator-is-broken-and-it-s-definitely-not-a-browser-or-os-issue/1304436)
[11] WorkOS. (2025, Julio 30). *Anthropic's Computer Use versus OpenAI's Computer Using Agent (CUA)*. Recuperado de [https://workos.com/blog/anthropics-computer-use-versus-openais-computer-using-agent-cua](https://workos.com/blog/anthropics-computer-use-versus-openais-computer-using-agent-cua)
[12] Blue, A. (n.d.). *Threat modelling — Open AI Operator*. Medium. Recuperado de [https://medium.com/@arohablue/open-ai-operator-a-security-nightmare-c6bca48355a5](https://medium.com/@arohablue/open-ai-operator-a-security-nightmare-c6bca48355a5)
[13] OpenAI Community. (2025, Julio 10). *Operator not working since many days*. Recuperado de [https://community.openai.com/t/operator-not-working-since-many-days/1312422](https://community.openai.com/t/operator-not-working-since-many-days/1312422)
[14] Coasty.ai. (2026, Abril 4). *The OSWorld Benchmark Results Are In and Most AI ...*. Recuperado de [https://coasty.ai/blog/osworld-benchmark-results-2026-who-actually-leads-20260405](https://coasty.ai/blog/osworld-benchmark-results-2026-who-actually-leads-20260405)
[15] Greyling, C. (n.d.). *GPT-5.5 Computer Use Agent Harness*. Substack. Recuperado de [https://cobusgreyling.substack.com/p/gpt-55-computer-use-agent-harness](https://cobusgreyling.substack.com/p/gpt-55-computer-use-agent-harness)
[16] Coasty.ai. (2026, Marzo 24). *OpenAI Operator Review 2026: The Computer Use Agent ...*. Recuperado de [https://coasty.ai/blog/openai-operator-review-2026](https://coasty.ai/blog/openai-operator-review-2026)
[17] Shaik, P. (2026, Marzo 24). *Open-source AI agent beats OpenAI CUA on 3/4 benchmarks*. LinkedIn. Recuperado de [https://www.linkedin.com/posts/pasha-shaik_an-open-source-ai-agent-that-browses-the-activity-7442409652480389120-jOnb](https://www.linkedin.com/posts/pasha-shaik_an-open-source-ai-agent-that-browses-the-activity-7442409652480389120-jOnb)
[18] OpenAI. (n.d.). *CUA eval extra information*. Recuperado de [https://cdn.openai.com/cua/CUA_eval_extra_information.pdf](https://cdn.openai.com/cua/CUA_eval_extra_information.pdf)


## Hallazgos Técnicos en GitHub (Fase 5)

# Hallazgos Técnicos del Agente OpenAI Operator (openai/operator en GitHub)

## URL del Repositorio Oficial

El repositorio oficial encontrado en GitHub es: [https://github.com/openai/openai-cua-sample-app](https://github.com/openai/openai-cua-sample-app)

## Actividad del Repositorio

El repositorio `openai/openai-cua-sample-app` ha mostrado actividad reciente, con commits registrados en los últimos 60 días. Esto indica que el proyecto está siendo mantenido activamente.

## Arquitectura Interna

El repositorio `openai-cua-sample-app` es una aplicación de ejemplo en TypeScript diseñada para flujos de trabajo de uso de computadora centrados en el navegador con GPT-5.4. La arquitectura se compone de varios componentes clave:

*   `apps/demo-web`: Una consola de operador Next.js que permite iniciar ejecuciones, revisar capturas de pantalla, eventos y artefactos de reproducción.
*   `apps/runner`: Un *runner* Fastify que gestiona espacios de trabajo mutables, sesiones de navegador, SSE (Server-Sent Events) y paquetes de reproducción.
*   `packages/*`: Paquetes compartidos para escenarios, tiempo de ejecución y contratos que facilitan la adición de nuevos laboratorios.

El diseño modular sugiere una clara separación de responsabilidades, donde la interfaz de usuario (`demo-web`) se encarga de la interacción con el operador, el `runner` orquesta la ejecución del agente y los `packages` proporcionan componentes reutilizables.

## Ciclo del Agente (Loop, Estados, Transiciones)

El ciclo del agente se centra en la integración con la API de Responses. El `runner-core` es el encargado de la orquestación, el bucle de Responses, los ejecutores de escenarios y la verificación. El repositorio demuestra cómo integrar la API de Responses desde un lugar canónico: `packages/runner-core/src/responses-loop.ts`. Esto implica que el agente opera en un bucle donde recibe una entrada, procesa la información, interactúa con el navegador (ya sea en modo `native` o `code`) y luego verifica los resultados.

## Sistema de Memoria y Contexto

Aunque el `README.md` no detalla explícitamente un sistema de memoria y contexto, la mención de "espacios de trabajo mutables" en el `apps/runner` sugiere que el agente mantiene un estado o contexto durante sus ejecuciones. Además, la capacidad de "revisar capturas de pantalla, eventos y artefactos de reproducción" en la consola del operador implica que se guarda un historial de las interacciones del agente, lo que podría considerarse parte de su contexto o memoria para depuración y análisis.

## Manejo de Herramientas (Tools/Functions)

El agente utiliza dos modos principales de ejecución para interactuar con el navegador, que pueden considerarse como el manejo de herramientas:

*   **Modo `native`**: Expone directamente la herramienta de computadora de la API de Responses. El modelo solicita clics, arrastres, escritura, esperas y capturas de pantalla contra la sesión del navegador en vivo. Este modo es la muestra más cercana de la herramienta de computadora en sí.
*   **Modo `code`**: Expone un REPL (Read-Eval-Print Loop) persistente de JavaScript de Playwright a través de `exec_js`. El modelo *scripta* el navegador en lugar de emitir acciones de computadora en bruto. Este modo es una muestra clara de un arnés REPL de navegador.

Ambos modos utilizan los mismos manifiestos de escenario y pipeline de reproducción. La verificación funciona de la misma manera en ambos, ya que lee el estado final del laboratorio, no la transcripción del agente.

## Sandbox y Entorno de Ejecución

El entorno de ejecución se basa en:

*   **Node.js**: Versión `22.20.0`
*   **pnpm**: Versión `10.26.0`
*   **Playwright**: Se requiere la instalación del navegador Chromium de Playwright.

El `apps/runner` gestiona "espacios de trabajo mutables" y "sesiones de navegador", lo que sugiere un entorno aislado para cada ejecución del agente. Esto proporciona un sandbox donde el agente puede interactuar con el navegador sin afectar el sistema subyacente. Los "labs" son plantillas de laboratorio estáticas que se copian en espacios de trabajo con alcance de ejecución, lo que refuerza la idea de un entorno controlado y reproducible.

## Integraciones y Conectores

La integración principal es con la **API de Responses de OpenAI**. El repositorio demuestra cómo integrar esta API para el control del navegador. No se mencionan explícitamente otras integraciones o conectores externos en el `README.md`, pero la naturaleza modular del proyecto y el uso de `packages/*` para contratos compartidos podrían facilitar futuras integraciones.

## Benchmarks y Métricas de Rendimiento

El `README.md` no proporciona benchmarks o métricas de rendimiento específicas. Sin embargo, los "escenarios oficiales" (`kanban-reprioritize-sprint`, `paint-draw-poster`, `booking-complete-reservation`) están diseñados para "verificación determinista" y "laboratorios locales". Esto implica que el enfoque está en la funcionalidad y la capacidad de verificar los resultados de las acciones del agente, más que en la velocidad o eficiencia en esta etapa de la muestra.

## Decisiones de Diseño Reveladas en PRs o Issues Técnicos

Al revisar los issues, se encuentran algunas discusiones que revelan decisiones de diseño o limitaciones:

*   **Limitaciones de seguridad**: El repositorio advierte que "el uso de la computadora sigue siendo de alto riesgo" y aconseja "no apuntar esta muestra a entornos autenticados, financieros, médicos o de alto riesgo". Esto subraya una decisión de diseño de priorizar la seguridad y la contención en esta etapa de desarrollo, limitando el alcance del agente a tareas de bajo riesgo.
*   **Enfoque en el navegador**: El repositorio está "intencionalmente centrado en el navegador". Los escenarios de "parcheo de espacio de trabajo y edición de archivos están fuera del alcance de la rama de lanzamiento de OSS". Esto indica una decisión de diseño de especializar el agente en interacciones web, dejando otras formas de uso de la computadora para futuras iteraciones o proyectos separados.
*   **Ausencia de reconocimiento de seguridad**: "Los reconocimientos de seguridad pendientes del uso de la computadora no se implementan en esta muestra todavía". Esto es una limitación conocida y una decisión de diseño temporal, lo que sugiere que se planean futuras mejoras en la seguridad.
*   **Escenarios locales y deterministas**: Los escenarios públicos son "laboratorios locales diseñados para verificación determinista" y "no están destinados como pruebas de autonomía web general". Esto refleja una decisión de diseño de crear un entorno controlado para el desarrollo y la prueba, en lugar de buscar una autonomía completa en entornos web complejos de inmediato.
*   **Discusiones en Issues**: Algunos issues, como "Sharing: Vision-based CUA on enterprise remote desktops — lessons from a multi-agent approach" (#69) o "Async Computer API?" (#60), sugieren discusiones sobre la evolución de las capacidades del agente, como el soporte para entornos de escritorio remotos o APIs asíncronas, lo que podría influir en futuras decisiones de diseño.

## Información Técnica Nueva (No en la Documentación Oficial del Sitio Web)

La información detallada sobre la arquitectura interna del `openai-cua-sample-app`, los modos de ejecución (`native` y `code`), la estructura de los paquetes (`apps/demo-web`, `apps/runner`, `packages/*`), los requisitos de Node.js, pnpm y Playwright, y las advertencias de seguridad específicas del repositorio no se encuentran en la documentación general de OpenAI sobre "Operator" o "Computer-Using Agent". El `README.md` de este repositorio de ejemplo proporciona una visión mucho más profunda de la implementación técnica y las consideraciones de diseño de un agente CUA en un entorno de desarrollo real. Los issues también revelan discusiones y limitaciones que no suelen estar presentes en la documentación de alto nivel.