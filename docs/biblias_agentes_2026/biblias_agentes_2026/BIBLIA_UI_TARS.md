# Biblia de Implementación: UI-TARS-desktop

**Fecha de Lanzamiento:** Enero 2025 (Paper inicial) / Abril 2025 (v0.1.0 Desktop)
**Versión:** UI-TARS-1.5 / UI-TARS-2 (según el paper)
**Arquitectura Principal:** Agente GUI Nativo Multimodal de Extremo a Extremo

## 1. Visión General y Diferenciador Único

UI-TARS (User Interface - Task Automation and Reasoning System) es un modelo de agente GUI nativo desarrollado por ByteDance que percibe exclusivamente capturas de pantalla como entrada y realiza interacciones similares a las humanas (por ejemplo, operaciones de teclado y ratón) [1]. A diferencia de los frameworks de agentes predominantes que dependen de modelos comerciales (como GPT-4o) con prompts y flujos de trabajo elaborados por expertos, UI-TARS es un modelo de extremo a extremo que supera a estos frameworks sofisticados [1].

Su diferenciador único radica en su capacidad para unificar la percepción, el razonamiento, la memoria y la acción dentro de un único modelo, aprendiendo y adaptándose continuamente a través de un proceso de entrenamiento iterativo y retroalimentación reflexiva. Esto le permite operar con una intervención humana mínima y generalizar en una amplia gama de tareas y entornos GUI [1]. UI-TARS Desktop es la aplicación de escritorio que materializa este agente GUI nativo para el control local de computadoras [2].

## 2. Arquitectura Técnica

La arquitectura de UI-TARS se basa en un modelo de agente GUI nativo que integra de forma holística cuatro capacidades principales: **Percepción Mejorada**, **Modelado de Acciones Unificado**, **Razonamiento System-2** y **Aprendizaje Iterativo con Memoria a Largo Plazo** [1].

### 2.1. Percepción Mejorada para Capturas de Pantalla GUI

UI-TARS aborda la alta densidad de información y los diseños intrincados de los entornos GUI mediante capacidades de percepción robustas. Esto se logra a través de la **Descripción de Elementos**, que proporciona descripciones estructuradas y detalladas de los componentes GUI, incluyendo tipo de elemento, descripción visual, información de posición y función, permitiendo reconocer elementos pequeños y complejos con precisión. Además, utiliza el **Subtitulado Denso (Dense Captioning)** para generar descripciones completas y detalladas de la captura de pantalla GUI, capturando no solo los elementos sino también sus relaciones espaciales y el diseño general de la interfaz. El **Subtitulado de Transición de Estado (State Transition Captioning)** identifica y describe las diferencias sutiles entre capturas de pantalla consecutivas, lo que permite al agente comprender los efectos de las acciones y los cambios no interactivos de la UI. La capacidad de **Preguntas y Respuestas (QA)** sintetiza datos de QA para mejorar la capacidad del agente de procesar consultas que involucran un mayor grado de abstracción o razonamiento visual. Finalmente, el **Set-of-Mark (SoM) Prompting** utiliza marcadores visualmente distintos en las capturas de pantalla para asociar elementos GUI con contextos espaciales y funcionales específicos, mejorando la localización y la identificación de elementos [1].

### 2.2. Modelado de Acciones Unificado para Ejecución Multi-paso

UI-TARS estandariza las acciones en un espacio de acción unificado que es consistente en diferentes plataformas (web, móvil, escritorio) [1]. Esto incluye un **Espacio de Acción Unificado** que define un conjunto común de operaciones (clic, escribir, desplazar, arrastrar) que se mapean a través de distintas plataformas, incluyendo acciones específicas de cada plataforma y acciones terminales como `Finished()` y `CallUser()`. La **Recopilación de Trazas de Acción** se realiza a través de un conjunto de datos anotado especializado y la integración de conjuntos de datos de código abierto existentes, lo que permite al modelo aprender secuencias de acciones efectivas. La **Mejora de la Capacidad de Grounding** se logra mediante la predicción directa de coordenadas, asociando cada elemento GUI con sus coordenadas espaciales y metadatos, entrenando el modelo para predecir coordenadas normalizadas [1].

### 2.3. Razonamiento System-2 para la Toma de Decisiones Deliberada

Para manejar escenarios complejos y entornos cambiantes, UI-TARS incorpora capacidades de razonamiento de nivel System-2, que implican un pensamiento deliberado y analítico [1]. Esto se infunde a través del **Enriquecimiento del Razonamiento con Tutoriales GUI**, utilizando tutoriales disponibles públicamente que intercalan texto e imágenes para establecer conocimientos fundamentales de la GUI y patrones de razonamiento lógico, con un proceso de filtrado multi-etapa que garantiza la alta calidad de estos datos. Además, la **Estimulación del Razonamiento con Aumento de Pensamientos (Thought Augmentation)** aumenta los conjuntos de datos de trazas de acción con "pensamientos" explícitos (t) generados antes de cada acción (a). Estos pensamientos, inspirados en el framework ReAct, guían al agente a reconsiderar acciones y observaciones previas, fomentando patrones de razonamiento como la descomposición de tareas, la consistencia a largo plazo, el reconocimiento de hitos, el ensayo y error, y la reflexión [1].

### 2.4. Aprendizaje Iterativo con Memoria a Largo Plazo

UI-TARS aborda la escasez de datos de procesos del mundo real para operaciones GUI mediante el aprendizaje iterativo de experiencias previas almacenadas en la memoria a largo plazo [1]. Esto se logra a través del **Online Trace Bootstrapping**, un proceso semi-automatizado de recopilación, filtrado y refinamiento de datos que permite al modelo aprender continuamente de las interacciones con dispositivos del mundo real. El modelo genera trazas, que luego son filtradas (por reglas, puntuación VLM y revisión humana) y utilizadas para el ajuste fino. El **Ajuste por Reflexión (Reflection Tuning)** enseña al agente a recuperarse de errores, exponiendo al modelo a errores del mundo real junto con sus correcciones, lo que implica etiquetar acciones incorrectas y proporcionar acciones y pensamientos corregidos, permitiendo a UI-TARS aprender a ajustar su estrategia cuando se enfrenta a situaciones subóptimas. Finalmente, la **Optimización de Preferencia Directa (DPO) del Agente** se utiliza para optimizar el agente, codificando directamente una preferencia por las acciones corregidas sobre las erróneas, lo que permite un uso más efectivo de los datos disponibles y guía al agente a evitar acciones subóptimas [1].

## 3. Implementación/Patrones Clave

La implementación de UI-TARS se centra en un enfoque de entrenamiento de tres fases para refinar sus capacidades en diversas tareas GUI, utilizando un total de aproximadamente 50 mil millones de tokens [1]. La **Fase de Pre-entrenamiento Continuo** utiliza el conjunto completo de datos (excluyendo los datos de ajuste por reflexión) para el pre-entrenamiento continuo con una tasa de aprendizaje constante, permitiendo al modelo aprender el conocimiento necesario para la interacción GUI automatizada, incluyendo percepción, grounding y trazas de acción. La **Fase de Recocido (Annealing Phase)** selecciona subconjuntos de alta calidad de datos de percepción, grounding, trazas de acción y ajuste por reflexión para el recocido, ajustando gradualmente la dinámica de aprendizaje del modelo, promoviendo un aprendizaje más enfocado y una mejor optimización de la toma de decisiones. La **Fase de Ajuste Fino (Fine-tuning Phase)** utiliza un conjunto de datos de alta calidad que incluye datos de ajuste por reflexión y DPO para el ajuste fino, lo cual es crucial para mejorar el rendimiento del modelo en tareas de razonamiento complejas y para enseñarle a recuperarse de errores [1].

El modelo utiliza un backbone VLM (Vision-Language Model) como Qwen-2-VL (Wang et al., 2024c) [1].

## 4. Lecciones para el Monstruo

La arquitectura de UI-TARS ofrece varias lecciones valiosas para el desarrollo de nuestro propio agente:

*   **Enfoque de Extremo a Extremo:** La capacidad de UI-TARS para unificar percepción, razonamiento, memoria y acción en un solo modelo, en lugar de depender de frameworks modulares, es clave para la escalabilidad y adaptabilidad. Esto reduce la fragilidad y la sobrecarga de mantenimiento asociadas con los flujos de trabajo definidos manualmente.
*   **Percepción Basada en Visión Pura:** La dependencia exclusiva de capturas de pantalla como entrada, en lugar de representaciones textuales (como HTML), simplifica el proceso y evita las limitaciones específicas de la plataforma. Esto permite una alineación más estrecha con los procesos cognitivos humanos.
*   **Razonamiento System-2 Integrado:** La infusión de capacidades de razonamiento deliberado (descomposición de tareas, consistencia a largo plazo, reconocimiento de hitos, ensayo y error, reflexión) es fundamental para manejar tareas complejas y dinámicas. Nuestro agente podría beneficiarse enormemente de la integración explícita de estos patrones de pensamiento.
*   **Aprendizaje Iterativo y Reflexivo:** El proceso de Online Trace Bootstrapping y Reflection Tuning es un patrón poderoso para superar la escasez de datos y permitir que el agente aprenda continuamente de sus errores y se adapte a situaciones imprevistas con mínima intervención humana. La incorporación de DPO para optimizar las preferencias de acción es un enfoque robusto para el aprendizaje a partir de ejemplos positivos y negativos.
*   **Recopilación de Datos a Gran Escala y Curación:** La creación de conjuntos de datos a gran escala y de alta calidad para la percepción (descripciones de elementos, subtitulado denso, subtitulado de transición de estado) y las trazas de acción es vital. La combinación de datos anotados y de código abierto, junto con un riguroso filtrado, es un patrón efectivo.

---
*Referencias:*
[1] Qin, Y., Ye, Y., Fang, J., Wang, H., Liang, S., Tian, S., ... & Shi, G. (2025). UI-TARS: Pioneering Automated GUI Interaction with Native Agents. *arXiv preprint arXiv:2501.12326*. [https://arxiv.org/abs/2501.12326](https://arxiv.org/abs/2501.12326)
[2] bytedance/UI-TARS-desktop: The Open-Source Multimodal AI Agent Stack: Connecting Cutting-Edge AI Models and Agent Infra. (n.d.). GitHub. [https://github.com/bytedance/ui-tars-desktop](https://github.com/bytedance/ui-tars-desktop)


---

# Biblia de Implementación: UI-TARS-desktop (ByteDance) — Fase 2

## Introducción

UI-TARS-desktop de ByteDance es un agente de IA multimodal de código abierto diseñado para el control de escritorio, que permite la automatización de tareas en interfaces gráficas de usuario (GUI) a través de la percepción visual y la ejecución de acciones. Este documento profundiza en la arquitectura y el funcionamiento interno de UI-TARS-desktop, cubriendo aspectos técnicos clave de su ciclo de agente, estados, sistema de herramientas, ejecución de código, entorno de sandbox, gestión de memoria y contexto, interacción con navegadores/GUI, capacidades multi-agente, integraciones, multimodalidad, límites y manejo de errores, y benchmarks de rendimiento.


## MÓDULO A: Ciclo del agente (loop/ReAct)

El ciclo de vida del agente UI-TARS-desktop se orquesta a través de una secuencia bien definida de pasos que integran la percepción visual, el razonamiento del modelo y la ejecución de acciones. Este proceso se gestiona principalmente en los archivos `runAgent.ts` y `GUIAgent.ts`, con el `Model.ts` manejando la interacción con el VLM (Vision-Language Model).

### Orquestación del Ciclo (runAgent.ts)

El archivo `runAgent.ts` actúa como el punto de entrada principal para iniciar una sesión del agente. Sus responsabilidades clave incluyen:

*   **Selección del Operador**: Basándose en la configuración del usuario (`settings.operator`), el sistema elige el operador adecuado para la interacción con la GUI. Las opciones incluyen `LocalComputer` (control local del escritorio), `LocalBrowser` (control local del navegador), `RemoteComputer` (control remoto del escritorio) y `RemoteBrowser` (control remoto del navegador) [1].
*   **Configuración del Modelo**: Se configura el modelo VLM, incluyendo la URL base, la clave API, el nombre del modelo y si se utiliza la API de respuestas de OpenAI. Para operadores remotos, se ajusta la configuración del modelo para usar `FREE_MODEL_BASE_URL` y se obtienen encabezados de autenticación remotos [1].
*   **Generación del System Prompt**: Se construye el `systemPrompt` que guiará el comportamiento del VLM, adaptándose a la versión del modelo y al tipo de operador (computadora o navegador) [1].
*   **Instanciación y Ejecución de `GUIAgent`**: Se crea una instancia de `GUIAgent` con la configuración recopilada (modelo, `systemPrompt`, logger, señal de aborto, operador, callbacks `onData` y `onError`, configuración de reintentos, `maxLoopCount` y `loopIntervalInMs`). Finalmente, se invoca el método `run()` de `guiAgent` para comenzar el ciclo de ejecución [1].

### Bucle Principal del Agente (GUIAgent.ts)

La clase `GUIAgent` encapsula la lógica central del ciclo `screenshot -> model -> parse -> execute`, que es fundamental para la operación del agente. El método `run()` implementa un bucle iterativo que sigue estos pasos:

*   **Inicialización de la Sesión**: Se inicializa un objeto `GUIAgentData` que contiene la versión, el `systemPrompt`, la instrucción inicial, el nombre del modelo, el estado (`StatusEnum.INIT`) y un historial de conversaciones. Este objeto se actualiza y se emite a través del callback `onData` para mantener la interfaz de usuario informada [2].
*   **Bucle de Ejecución**: El agente entra en un bucle `while(true)` que continúa hasta que se cumpla una condición de terminación (éxito, error, detención por el usuario o límite de bucles) [2].
    *   **Control de Pausa/Reanudación/Parada**: Dentro del bucle, se verifica el estado de pausa (`isPaused`) o detención (`isStopped`) del agente. Si está pausado, el agente espera una señal de reanudación. Si está detenido o la señal de aborto está activada, el bucle se rompe [2].
    *   **Límites de Bucle y Errores de Captura de Pantalla**: Se verifica si se ha alcanzado el `maxLoopCount` o si se ha excedido el número máximo de errores de captura de pantalla (`MAX_SNAPSHOT_ERR_CNT`). En cualquiera de estos casos, el agente establece su estado en `ERROR` y termina el bucle [2].
    *   **Captura de Pantalla**: El operador (`operator.screenshot()`) captura una imagen de la GUI. Esta operación incluye un mecanismo de reintento (`asyncRetry`) con un `maxRetries` configurable (por defecto, 5 reintentos) [2].
    *   **Validación de Imagen**: La captura de pantalla se valida para asegurar que es una imagen válida con dimensiones correctas. Si la imagen no es válida, se incrementa un contador de errores de captura de pantalla y se reintenta la captura después de un breve `sleep` [2].
    *   **Actualización del Historial de Conversaciones**: La captura de pantalla válida se añade al historial de conversaciones como un mensaje del tipo `human` con un `IMAGE_PLACEHOLDER` y metadatos de la captura (dimensiones, `scaleFactor`). Esta información se envía a través del callback `onData` [2].
    *   **Preparación para el VLM**: El historial de conversaciones y las imágenes se transforman en un formato adecuado para la invocación del VLM (`toVlmModelFormat`). Esto incluye la inyección de mensajes históricos y el `systemPrompt` [2] [4].
    *   **Invocación del VLM**: El método `model.invoke()` se llama con los parámetros preparados. Esta invocación también utiliza `asyncRetry` con un `maxRetries` configurable (por defecto, 5 reintentos) para manejar posibles fallos del modelo. El VLM devuelve una predicción de texto y acciones parseadas [2] [3].
    *   **Procesamiento de la Respuesta del VLM**: La predicción del VLM se resume (`getSummary`) y se añade al historial de conversaciones como un mensaje del tipo `gpt`, junto con las acciones parseadas y los metadatos de la captura de pantalla. Esta información se envía a través del callback `onData` [2].
    *   **Ejecución de Acciones**: Cada acción parseada (`parsedPrediction`) de la respuesta del VLM se ejecuta secuencialmente a través del operador (`operator.execute()`). La ejecución de acciones también tiene un mecanismo de reintento (por defecto, 1 reintento) [2].
    *   **Manejo de Acciones Internas**: Durante la ejecución, se manejan acciones internas como `error_env` (error de entorno), `max_loop` (límite de bucles alcanzado), `call_user` (requiere intervención del usuario) y `finished` (tarea completada). Estas acciones pueden cambiar el estado del agente y, en algunos casos, terminar el bucle [2].
    *   **Intervalo de Bucle**: Si se configura `loopIntervalInMs`, el agente espera el tiempo especificado antes de la siguiente iteración del bucle [2].
*   **Finalización y Manejo de Errores**: Al salir del bucle (ya sea por éxito o error), el estado del modelo se reinicia (`model.reset()`). Si el agente fue detenido por el usuario, se ejecuta una acción `user_stop`. Finalmente, se emite el estado final a través de `onData` y, si hubo un error, se invoca el callback `onError` [2].

### Interacción con el Modelo (Model.ts)

La clase `UITarsModel` gestiona la comunicación con el VLM. El método `invoke()` es crucial para este proceso:

*   **Preprocesamiento de Imágenes**: Las imágenes de las capturas de pantalla se preprocesan y redimensionan para cumplir con los límites de píxeles del modelo (`maxPixels`), que varían según la versión del modelo (V1_0, V1_5, Doubao) [3] [4].
*   **Conversión de Mensajes**: El historial de conversaciones (texto e imágenes) se convierte a un formato compatible con la API de OpenAI (`convertToOpenAIMessages`). Si se utiliza la API de respuestas, se realiza una conversión adicional (`convertToResponseApiInput`) para manejar mensajes incrementales y `previous_response_id` [3] [4].
*   **Invocación del Proveedor del Modelo**: Se llama a `invokeModelProvider()` para interactuar con el VLM. Este método puede usar la API de Chat Completions de OpenAI o la API de Responses de OpenAI. La API de Responses permite un procesamiento incremental y la gestión de un contexto de imagen deslizante, eliminando las imágenes más antiguas cuando el contexto avanza [3].
*   **Parseo de Acciones**: La predicción de texto del VLM se pasa a `actionParser` para extraer las acciones estructuradas (`parsedPredictions`), que luego serán ejecutadas por el operador [3].

Este ciclo iterativo permite a UI-TARS percibir el estado actual de la GUI, razonar sobre la mejor acción a tomar y ejecutar esa acción, adaptándose dinámicamente al entorno para completar la tarea asignada.

## MÓDULO B: Estados del agente

El agente UI-TARS-desktop gestiona su ciclo de vida a través de una máquina de estados bien definida, representada por el enumerador `StatusEnum` en el archivo `agent.ts`. Estos estados determinan el comportamiento actual del agente y cómo responde a los eventos del sistema y del usuario.

### Estados Principales (`StatusEnum`)

*   **`INIT` (Inicialización)**: Es el estado inicial del agente cuando se crea una nueva sesión (`GUIAgentData`). Ocurre inmediatamente al llamar al método `run()` de `GUIAgent`, antes de que comience el bucle principal. En este estado, se configuran los parámetros iniciales, como el `systemPrompt`, la instrucción del usuario y el historial de conversaciones inicial [2].
*   **`RUNNING` (En Ejecución)**: Indica que el agente está activamente ejecutando su ciclo principal (captura de pantalla, invocación del modelo, ejecución de acciones). El agente pasa a este estado justo antes de entrar en el bucle `while(true)` en `GUIAgent.ts`. También puede volver a este estado desde `PAUSE` si se reanuda la ejecución [2].
*   **`PAUSE` (Pausado)**: El agente ha suspendido temporalmente su ejecución. Se activa mediante el método `pause()` de `GUIAgent`, que establece la bandera `isPaused` en `true`. El agente entra en este estado al comienzo de la siguiente iteración del bucle y espera a que se resuelva una promesa (`resumePromise`) antes de continuar [2].
*   **`END` (Finalizado)**: El agente ha completado su tarea con éxito. Ocurre cuando el modelo VLM predice la acción `finished()`. El bucle principal se rompe y el agente finaliza su ejecución [2].
*   **`CALL_USER` (Llamar al Usuario)**: El agente ha encontrado una situación que no puede resolver por sí mismo y requiere la intervención del usuario. Se activa cuando el modelo VLM predice la acción `call_user()`. El bucle principal se rompe y el agente espera la asistencia del usuario [2].
*   **`USER_STOPPED` (Detenido por el Usuario)**: La ejecución del agente ha sido cancelada explícitamente por el usuario. Ocurre si se activa la señal de aborto (`signal?.aborted`) o si se llama al método `stop()` de `GUIAgent` (que establece `isStopped` en `true`). En este caso, el agente ejecuta una acción especial `user_stop` para limpiar el estado antes de finalizar [2].
*   **`ERROR` (Error)**: El agente ha encontrado un error irrecuperable durante su ejecución. Puede ser desencadenado por múltiples condiciones, como alcanzar el límite máximo de bucles (`maxLoopCount`), fallos repetidos en la captura de pantalla (`MAX_SNAPSHOT_ERR_CNT`), errores en la invocación del modelo, errores durante la ejecución de acciones, o si el modelo predice la acción interna `error_env`. El agente captura el error específico (definido en `ErrorStatusEnum`) y termina el bucle [2].
*   **`MAX_LOOP` (Límite de Bucles - Obsoleto)**: Un estado obsoleto mantenido por compatibilidad hacia atrás, que indicaba que el agente había alcanzado el número máximo de iteraciones permitidas. Actualmente, esta condición se maneja transicionando al estado `ERROR` con el código `REACH_MAXLOOP_ERROR` [2].

### Estados de Error Detallados (`ErrorStatusEnum`)

Cuando el agente entra en el estado `ERROR`, proporciona información adicional sobre la causa del fallo a través de `ErrorStatusEnum`:

*   **`SCREENSHOT_RETRY_ERROR` (-100000)**: Fallo al capturar la pantalla después del número máximo de reintentos permitidos.
*   **`INVOKE_RETRY_ERROR` (-100001)**: Fallo al invocar el modelo VLM después del número máximo de reintentos permitidos.
*   **`EXECUTE_RETRY_ERROR` (-100002)**: Fallo al ejecutar una acción a través del operador después del número máximo de reintentos permitidos.
*   **`MODEL_SERVICE_ERROR` (-100003)**: Error interno del servicio del modelo (por ejemplo, un error 500 de la API de OpenAI).
*   **`REACH_MAXLOOP_ERROR` (-100004)**: El agente ha alcanzado el límite máximo de iteraciones del bucle (`maxLoopCount`) sin completar la tarea.
*   **`ENVIRONMENT_ERROR` (-100005)**: Error de entorno detectado al analizar la acción (por ejemplo, si el modelo predice la acción interna `error_env`).
*   **`UNKNOWN_ERROR` (-100099)**: Un error no clasificado o inesperado durante la ejecución [2].

### Transiciones de Estado y Manejo de Eventos

Las transiciones de estado se gestionan principalmente dentro del bucle `while(true)` en `GUIAgent.ts`. El agente verifica continuamente las banderas de control (`isPaused`, `isStopped`, `signal?.aborted`) y las condiciones de error (`loopCnt >= maxLoopCount`, `snapshotErrCnt >= MAX_SNAPSHOT_ERR_CNT`).

Además, las acciones predichas por el modelo pueden forzar transiciones de estado. Por ejemplo, si el modelo devuelve `finished()`, el estado cambia a `END` y el bucle se rompe. Si devuelve `call_user()`, el estado cambia a `CALL_USER` y el bucle se rompe.

Cualquier cambio de estado se comunica a la aplicación principal a través del callback `onData`, permitiendo que la interfaz de usuario se actualice en consecuencia (por ejemplo, mostrando un mensaje de error, indicando que la tarea se ha completado o solicitando la intervención del usuario) [2].

## MÓDULO C: Sistema de herramientas

El agente UI-TARS-desktop interactúa con el entorno GUI a través de un conjunto de herramientas (acciones) que son comunicadas al modelo de lenguaje visual (VLM) mediante el `systemPrompt`. El espacio de acciones varía ligeramente dependiendo de la versión del modelo y el tipo de operador (computadora o navegador). A continuación, se detallan las herramientas principales y sus parámetros, extraídas de los archivos `prompts.ts` y la implementación de los operadores [1] [5].

### Espacio de Acciones General (NutJSElectronOperator)

Para el operador `NutJSElectronOperator` (usado en `LocalComputer`), el espacio de acciones manuales incluye [5]:

*   **`click(start_box='<|box_start|>(x1,y1)<|box_end|>')`**: Realiza un clic simple en las coordenadas especificadas por el `start_box`.
*   **`left_double(start_box='<|box_start|>(x1,y1)<|box_end|>')`**: Realiza un doble clic izquierdo en las coordenadas especificadas.
*   **`right_single(start_box='<|box_start|>(x1,y1)<|box_end|>')`**: Realiza un clic derecho simple en las coordenadas especificadas.
*   **`drag(start_box='<|box_start|>(x1,y1)<|box_end|>', end_box='<|box_start|>(x3,y3)<|box_end|>')`**: Inicia un arrastre desde `start_box` hasta `end_box`.
*   **`hotkey(key='ctrl c')`**: Presiona una combinación de teclas. Las teclas se dividen por espacios y deben estar en minúsculas. No se deben usar más de 3 teclas en una acción `hotkey`.
*   **`type(content='xxx')`**: Escribe el `content` especificado. Se deben usar caracteres de escape (`\'`, `\"`, y `\n`) para asegurar el parseo correcto. Si se desea enviar la entrada (simular un Enter), se debe incluir `\n` al final del `content`.
*   **`scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', direction='down or up or right or left')`**: Realiza un desplazamiento en la dirección especificada, mostrando más información en esa dirección.
*   **`wait()`**: Pausa la ejecución durante 5 segundos y toma una captura de pantalla para verificar cambios.
*   **`finished()`**: Indica que la tarea ha sido completada con éxito.
*   **`call_user()`**: Envía la tarea y solicita la intervención del usuario cuando la tarea es irresoluble o se necesita ayuda.

### Espacio de Acciones para `getSystemPromptV1_5` y `getSystemPromptPoki`

Estos prompts utilizan un espacio de acciones similar al general, con la misma sintaxis para `start_box` y `end_box` (`<|box_start|>(x1,y1)<|box_end|>`) y las mismas consideraciones para `hotkey` y `type` [5].

### Espacio de Acciones para `getSystemPromptDoubao_15_15B`

Esta versión del prompt utiliza un formato diferente para las coordenadas de las cajas (`[x1, y1, x2, y2]`) y añade un parámetro `content` a la acción `finished()` [5]:

*   **`click(start_box='[x1, y1, x2, y2]')`**
*   **`left_double(start_box='[x1, y1, x2, y2]')`**
*   **`right_single(start_box='[x1, y1, x2, y2]')`**
*   **`drag(start_box='[x1, y1, x2, y2]', end_box='[x3, y3, x4, y4]')`**
*   **`hotkey(key='')`**: Similar a la anterior, pero el ejemplo de `key` está vacío.
*   **`type(content='xxx')`**: Mismas consideraciones de escape y `\n`.
*   **`scroll(start_box='[x1, y1, x2, y2]', direction='down or up or right or left')`**
*   **`wait()`**: Pausa durante 5 segundos y toma una captura de pantalla.
*   **`finished(content='xxx')`**: La acción `finished` ahora puede incluir un `content` con las mismas consideraciones de escape.

### Espacio de Acciones para `getSystemPromptDoubao_15_20B`

Esta versión introduce un formato de punto (`<point>x1 y1</point>`) para las coordenadas y, si el `operatorType` es `browser`, incluye acciones específicas de navegación web [5]:

*   **`click(point='<point>x1 y1</point>')`**
*   **`left_double(point='<point>x1 y1</point>')`**
*   **`right_single(point='<point>x1 y1</point>')`**
*   **`drag(start_point='<point>x1 y1</point>', end_point='<point>x2 y2</point>')`**
*   **`scroll(point='<point>x1 y1</point>', direction='down or up or right or left')`**
*   **`hotkey(key='')`**
*   **`type(content='xxx')`**
*   **`wait()`**
*   **`finished(content='xxx')`**
*   **`call_user()`**

**Acciones específicas del navegador (si `operatorType` es `browser`)**:

*   **`navigate(content='xxx')`**: Navega a la URL especificada en `content`.
*   **`navigate_back()`**: Vuelve a la página anterior.

### Parámetros y Límites Clave

*   **Coordenadas**: Las coordenadas se especifican mediante `start_box` o `point`, que representan áreas o puntos en la pantalla. La interpretación exacta (por ejemplo, centro de la caja) se realiza en el `actionParser` [3] [4].
*   **`hotkey`**: Limitado a un máximo de 3 teclas por acción.
*   **`type`**: Requiere el uso de caracteres de escape para `\'`, `\"`, y `\n`. `\n` al final del contenido simula la pulsación de Enter.
*   **`wait`**: Siempre implica una pausa de 5 segundos y una nueva captura de pantalla.
*   **Acciones Internas**: Además de las acciones expuestas al VLM, existen acciones internas (`INTERNAL_ACTION_SPACES_ENUM`) como `ERROR_ENV`, `MAX_LOOP`, `CALL_USER` y `FINISHED` que controlan el flujo del agente y las transiciones de estado [2] [6].

El sistema de herramientas de UI-TARS está diseñado para ser flexible, permitiendo al VLM interactuar con precisión con elementos GUI tanto en entornos de escritorio como de navegador, adaptándose a diferentes modelos y sus capacidades de salida.

## MÓDULO D: Ejecución de código

El agente UI-TARS-desktop no ejecuta código arbitrario en el sentido tradicional (por ejemplo, scripts de Python o JavaScript directamente en un intérprete). En cambio, su "ejecución de código" se refiere a la **ejecución de acciones predefinidas de GUI** que son interpretadas a partir de la salida del modelo de lenguaje visual (VLM). Estas acciones son realizadas por un componente denominado `operator`, que abstrae las interacciones de bajo nivel con el sistema operativo o el navegador [1] [2].

### Lenguajes y Entorno de Ejecución

La "ejecución" en UI-TARS se basa en la traducción de las predicciones del VLM a operaciones concretas de GUI. Los "lenguajes" de ejecución son, en esencia, el conjunto de acciones definidas en el `Action Space` de los prompts del sistema, como `click`, `type`, `scroll`, `hotkey`, `drag`, `wait`, `finished` y `call_user` [5].

El entorno de ejecución depende del `operator` seleccionado:

*   **`LocalComputer`**: Utiliza `NutJSElectronOperator`, que a su vez se basa en la librería `nut-js` para interactuar directamente con el sistema operativo local y controlar el escritorio (movimientos del ratón, clics, escritura, atajos de teclado, etc.) [1] [5].
*   **`LocalBrowser`**: Emplea `DefaultBrowserOperator`, que interactúa con un navegador local (como Chrome) para realizar acciones de navegación y manipulación de la interfaz web [1].
*   **`RemoteComputer`**: Utiliza `RemoteComputerOperator`, que delega las acciones a un servicio remoto a través de llamadas HTTP a un proxy (`PROXY_URL`). Este servicio remoto ejecuta las acciones en un entorno de máquina virtual o sandbox [1] [6].
*   **`RemoteBrowser`**: Emplea `RemoteBrowserOperator`, que se conecta a un navegador remoto (posiblemente a través de un CDP URL) para realizar acciones web en un entorno aislado [1] [6].

### Proceso de Ejecución de Acciones

Dentro del bucle principal del agente (`GUIAgent.ts`), después de que el VLM ha generado una predicción y esta ha sido parseada en `parsedPredictions`, el agente itera sobre estas predicciones y las ejecuta secuencialmente [2]:

*   **Parseo de la Predicción**: La salida textual del VLM es procesada por un `actionParser` que la convierte en una estructura de datos (`PredictionParsed`) que contiene el tipo de acción (`action_type`) y sus parámetros (`action_inputs`) [3].
*   **Delegación al Operador**: La acción parseada se pasa al método `operator.execute()`, junto con el contexto de la pantalla (ancho, alto, `scaleFactor`) y los factores de escalado del modelo [2].
*   **Ejecución de la Acción**: El operador específico (local o remoto) traduce la acción abstracta en comandos de bajo nivel. Por ejemplo, un `click` se convierte en una operación de clic del ratón en las coordenadas especificadas, y un `type` se convierte en la simulación de pulsaciones de teclado o pegado de texto [6].

### Manejo de Errores durante la Ejecución

UI-TARS implementa un robusto mecanismo de manejo de errores y reintentos para la ejecución de acciones:

*   **Reintentos (`asyncRetry`)**: La ejecución de cada acción a través de `operator.execute()` está envuelta en un bloque `asyncRetry`. Por defecto, se configura con `maxRetries: 1`, lo que significa que si una acción falla, se intentará una vez más antes de reportar un error fatal [2].
*   **Captura de Errores**: Si la ejecución de una acción falla después de los reintentos, el error es capturado y registrado. El estado del agente se actualiza a `StatusEnum.ERROR`, y se asigna un `ErrorStatusEnum.EXECUTE_RETRY_ERROR` para indicar que el fallo ocurrió durante la ejecución de una acción [2].
*   **Acciones Internas de Error**: El VLM puede predecir acciones internas como `error_env` si detecta un problema en el entorno. Cuando esto ocurre, el agente transiciona inmediatamente al estado `ERROR` con un `ErrorStatusEnum.ENVIRONMENT_ERROR` [2].
*   **Callback `onError`**: En caso de un error irrecuperable durante la ejecución, se invoca el callback `onError` para notificar a la aplicación principal, proporcionando detalles del error (`GUIAgentError`) [1] [2].

En resumen, la "ejecución de código" en UI-TARS-desktop es un proceso controlado y mediado por operadores que traducen las intenciones del VLM (expresadas como acciones de GUI) en interacciones reales con el sistema o el navegador, con mecanismos integrados para la resiliencia y el manejo de fallos.

## MÓDULO E: Sandbox y entorno

El agente UI-TARS-desktop está diseñado para operar en diversos entornos, desde el control local del escritorio hasta sandboxes remotos y navegadores. La gestión de estos entornos y la interacción con ellos se abstraen a través de la arquitectura de operadores y el `ProxyClient`, garantizando aislamiento, seguridad y acceso a recursos [1] [7].

### Tipos de Entorno y Operadores

UI-TARS soporta principalmente cuatro tipos de entornos, cada uno gestionado por un operador específico:

*   **`LocalComputer`**: El agente interactúa directamente con el sistema operativo local del usuario. Utiliza `NutJSElectronOperator`, que se basa en la librería `nut-js` para simular entradas de usuario (movimientos de ratón, clics, pulsaciones de teclado) y capturar la pantalla. Este entorno no proporciona un aislamiento de sandbox inherente, ya que opera directamente en la máquina del usuario [1] [5].
*   **`LocalBrowser`**: El agente controla un navegador web instalado localmente. El `DefaultBrowserOperator` se encarga de la interacción con el navegador, permitiendo la navegación, clics en elementos web, escritura en campos de texto, etc. Similar al `LocalComputer`, el aislamiento depende de las características de seguridad del navegador y del sistema operativo local [1].
*   **`RemoteComputer`**: Para tareas que requieren un entorno aislado o recursos computacionales específicos, UI-TARS puede operar en un "computador remoto" o sandbox. El `RemoteComputerOperator` se comunica con un servicio de proxy (`PROXY_URL`) para ejecutar acciones en una máquina virtual o contenedor remoto. Este entorno ofrece un aislamiento significativo, ya que las operaciones se realizan fuera de la máquina local del usuario [1] [6] [7].
*   **`RemoteBrowser`**: Similar al `RemoteComputer`, pero enfocado en el control de un navegador web dentro de un sandbox remoto. El `RemoteBrowserOperator` obtiene un CDP URL (Chrome DevTools Protocol URL) de un `ProxyClient` y lo utiliza para interactuar con el navegador remoto. Esto proporciona un entorno de navegación aislado y controlado [1] [6] [7].

### Arquitectura del Sandbox y Aislamiento

El `ProxyClient` (`proxyClient.ts`) es fundamental para la gestión de los entornos remotos (sandbox y navegador remoto). Actúa como una interfaz entre el agente local y los servicios remotos, manejando la asignación, liberación y comunicación con los recursos [7].

*   **Asignación de Recursos (`allocResource`, `allocHeadfulBrowser`)**: El `ProxyClient` es responsable de solicitar y obtener instancias de sandboxes (`SandboxInfo`) o navegadores con interfaz gráfica (`HdfBrowserInfo`). Estas instancias son recursos remotos que se asignan al agente para su uso. La asignación puede estar sujeta a un período de prueba gratuito (`FREE_TRIAL_DURATION_MS`) [7].
*   **Aislamiento**: Los sandboxes remotos proporcionan un entorno aislado para la ejecución de tareas. Esto significa que cualquier acción realizada por el agente en un `RemoteComputer` o `RemoteBrowser` se ejecuta dentro de un entorno virtualizado o contenedorizado, lo que protege el sistema local del usuario de posibles efectos secundarios o software malicioso. La comunicación con estos sandboxes se realiza a través de APIs bien definidas, lo que limita la superficie de ataque [7].
*   **Seguridad**: La comunicación con los servicios de proxy se realiza a través de `fetchWithAuth`, que incluye encabezados de autenticación (`getAuthHeader()`) para asegurar que solo los clientes autorizados puedan acceder a los recursos remotos. Esto añade una capa de seguridad a la interacción con el sandbox [7].
*   **Liberación de Recursos (`releaseResource`)**: Una vez que la tarea ha finalizado o el recurso ya no es necesario, el `ProxyClient` se encarga de liberar el sandbox o el navegador remoto, asegurando que los recursos se devuelvan al pool y se eviten costos innecesarios o el uso indebido [7].

### Recursos y Conectividad

*   **`PROXY_URL` y `BROWSER_URL`**: Estas constantes definen los endpoints de los servicios de proxy a los que se conecta el `ProxyClient` para gestionar los recursos remotos [7].
*   **`SandboxInfo`**: Contiene detalles sobre el sandbox asignado, como `sandBoxId`, `osType` (tipo de sistema operativo) y `rdpUrl` (URL para acceso RDP, lo que sugiere que los sandboxes pueden ser máquinas virtuales completas) [7].
*   **`BrowserInfo` / `HdfBrowserInfo`**: Proporcionan información sobre el navegador remoto, incluyendo `browserId`, `podName`, `wsUrl` (WebSocket URL para CDP) o `cdpUrl` y `vncUrl` (URL para acceso VNC, indicando acceso visual al navegador remoto) [7].
*   **`TIME_URL`**: Se utiliza para consultar el balance de tiempo de uso de los recursos (`TimeBalance`), lo que implica un modelo de consumo basado en el tiempo para los entornos remotos [7].

En resumen, el entorno de UI-TARS-desktop es flexible, permitiendo operaciones locales o remotas. Los entornos remotos se gestionan a través de un `ProxyClient` que asigna y libera sandboxes y navegadores aislados, garantizando seguridad y eficiencia en el uso de recursos a través de una comunicación autenticada y APIs bien definidas.

## MÓDULO F: Memoria y contexto

La gestión de la memoria y el contexto en UI-TARS-desktop es crucial para que el agente pueda mantener un hilo de conversación coherente y tomar decisiones informadas a lo largo de múltiples iteraciones. Esto se logra mediante el mantenimiento de un historial de conversaciones y capturas de pantalla, y la forma en que esta información se empaqueta y se presenta al modelo de lenguaje visual (VLM) [2] [4].

### Persistencia del Estado y Ventana de Contexto

El estado del agente se persiste principalmente a través del objeto `GUIAgentData`, que contiene un array de `conversations` (`Message[]`). Cada `Message` puede ser de tipo `human` o `gpt` y contiene el valor textual de la conversación. Además, las capturas de pantalla se asocian a los mensajes `human` mediante un `IMAGE_PLACEHOLDER` y el `screenshotBase64` real [2] [4].

La ventana de contexto se gestiona de la siguiente manera:

*   **Historial de Mensajes (`historyMessages`)**: El agente mantiene un historial de los últimos 30 mensajes (`messages.slice(-30)`) para inyectarlos en el `systemPrompt` del VLM. Estos mensajes se formatean como `human: xxx` o `assistant: xxx` y se insertan bajo una sección `## History Messages` [4].
*   **Ventana Deslizante de Imágenes (`MAX_IMAGE_LENGTH`)**: Para evitar exceder los límites de tokens de imagen del VLM, UI-TARS implementa una ventana deslizante para las capturas de pantalla. La constante `MAX_IMAGE_LENGTH` (por defecto, 6) define el número máximo de imágenes que se mantienen en el contexto. Si el número de imágenes excede este límite, las imágenes más antiguas y sus correspondientes mensajes `IMAGE_PLACEHOLDER` se eliminan del historial [4].
*   **Contexto de Imagen en la API de Respuestas (`headImageContext`)**: Cuando se utiliza la API de Respuestas de OpenAI, UI-TARS gestiona un `headImageContext` para rastrear los `responseIds` de las imágenes. Esto permite un procesamiento incremental y la eliminación de objetos de respuesta de imagen antiguos a medida que la ventana deslizante avanza, optimizando el uso de recursos y el contexto del modelo [3].

### Qué Recuerda el Agente

El agente recuerda la siguiente información clave:

*   **Instrucción del Usuario (`instruction`)**: La tarea original que se le asignó al agente [2].
*   **`System Prompt`**: Las directrices iniciales que guían su comportamiento y el formato de salida esperado [2].
*   **Historial de Conversaciones (`conversations`)**: Una secuencia de mensajes de texto y capturas de pantalla que representan el diálogo entre el usuario y el agente, así como las observaciones del entorno [2] [4].
*   **Acciones Parseadas (`predictionParsed`)**: Las acciones que el VLM ha predicho y que se han ejecutado o están pendientes de ejecución. Estas se almacenan junto con el mensaje del VLM [2] [4].
*   **Metadatos de Captura de Pantalla (`screenshotContext`)**: Información sobre las dimensiones físicas de la pantalla, el tipo MIME de la imagen y el `scaleFactor` (DPR) en el momento de la captura. Esto es crucial para interpretar correctamente las coordenadas de las acciones [2] [4].
*   **Estado Actual (`status`) y Errores (`error`)**: El estado operativo actual del agente y cualquier error que haya ocurrido, lo que le permite recuperarse o informar al usuario [2].

### Preparación del Contexto para el VLM

Antes de invocar al VLM, el historial de conversaciones y las imágenes se transforman en un formato adecuado:

*   **`toVlmModelFormat()`**: Esta función inserta los `historyMessages` en el `systemPrompt` y extrae los `screenshotBase64` de los mensajes de conversación para enviarlos por separado [4].
*   **`convertToOpenAIMessages()`**: Convierte los mensajes de texto y los `IMAGE_PLACEHOLDER` (con sus `screenshotBase64` asociados) en el formato `ChatCompletionMessageParam` de OpenAI, donde las imágenes se representan como `image_url` con datos base64 [4].
*   **`convertToResponseApiInput()`**: Si se utiliza la API de Respuestas, los mensajes se transforman para incluir `input_image` en lugar de `image_url` y se manejan de forma incremental [4].
*   **Preprocesamiento de Imágenes (`preprocessResizeImage`)**: Las imágenes se redimensionan para ajustarse a los límites de píxeles del modelo, asegurando que el VLM reciba imágenes optimizadas para su procesamiento [3] [4].

Esta cuidadosa gestión del contexto y la memoria permite a UI-TARS operar de manera efectiva en entornos dinámicos, manteniendo la coherencia y la capacidad de razonamiento a lo largo del tiempo.

## MÓDULO G: Browser/GUI

El agente UI-TARS-desktop está diseñado para interactuar con interfaces gráficas de usuario (GUI) tanto en entornos de escritorio como de navegador. Esta capacidad se logra a través de una arquitectura modular de operadores que traducen las intenciones del modelo de lenguaje visual (VLM) en acciones concretas de interacción. La interacción con la GUI se basa en la percepción visual (capturas de pantalla) y la ejecución de acciones predefinidas [1] [2].

### Interacción con la GUI del Escritorio

Para el control del escritorio, UI-TARS utiliza el `NutJSElectronOperator` [5]. Este operador se basa en la librería `nut-js` y en las capacidades de Electron para realizar las siguientes acciones:

*   **Movimiento del Ratón (`moveMouse`)**: Permite mover el cursor a coordenadas específicas en la pantalla [7].
*   **Clics del Ratón (`clickMouse`)**: Soporta clics izquierdos, derechos, dobles clics y clics centrales en coordenadas dadas [7].
*   **Arrastrar y Soltar (`dragMouse`)**: Simula operaciones de arrastre desde un punto de inicio a un punto final [7].
*   **Pulsaciones de Teclas (`pressKey`, `hotkey`)**: Permite simular la pulsación de teclas individuales o combinaciones de teclas (atajos). En Windows, la acción `type` utiliza Ctrl+V para pegar texto, lo que mejora la fiabilidad [5] [6].
*   **Escritura de Texto (`typeText`)**: Introduce texto en campos de entrada, con soporte para caracteres de escape y la simulación de la tecla Enter [5] [7].
*   **Desplazamiento (`scroll`)**: Permite desplazar la vista en una dirección específica (arriba, abajo, izquierda, derecha) en una ubicación dada [5] [7].
*   **Captura de Pantalla (`takeScreenshot`)**: Captura una imagen de la pantalla completa o de una región específica, que luego se utiliza como entrada visual para el VLM [6] [7].
*   **Obtención del Tamaño de la Pantalla (`getScreenSize`)**: Recupera las dimensiones de la pantalla para ajustar las coordenadas de las acciones [7].

### Interacción con la GUI del Navegador

UI-TARS puede controlar navegadores web tanto localmente (`LocalBrowser`) como en entornos remotos (`RemoteBrowser`). La interacción con el navegador se realiza a través de un `BrowserOperator` [1] [6].

*   **Navegación (`navigate`, `navigate_back`)**: Permite al agente abrir URLs específicas y navegar hacia atrás en el historial del navegador [5] [6].
*   **Clics en Elementos Web**: El agente puede hacer clic en elementos interactivos de la página web, utilizando coordenadas o identificadores de elementos [5] [6].
*   **Entrada de Texto en Formularios**: Similar al escritorio, el agente puede escribir texto en campos de formulario y otros elementos de entrada [5] [6].
*   **Desplazamiento en Páginas Web**: Permite el desplazamiento dentro de la página web para visualizar contenido fuera de la vista actual [5] [6].
*   **Manejo de Login**: Aunque no se detalla explícitamente un módulo de manejo de login, la capacidad de `type` (escribir texto) y `click` (hacer clic en botones de envío) le permite al agente interactuar con formularios de login estándar. La persistencia de la sesión de navegador (cookies, etc.) dependería del entorno del navegador subyacente (local o remoto) [5].

### Mecanismos de Percepción Visual

La percepción visual es fundamental para la interacción con la GUI. El agente toma capturas de pantalla (`screenshot`) del entorno actual, que luego son procesadas y enviadas al VLM. El VLM analiza estas imágenes junto con el historial de la conversación para determinar la siguiente acción. Las coordenadas de las acciones (por ejemplo, `start_box`, `point`) se interpretan en relación con estas capturas de pantalla [2] [3] [4].

### Abstracción y Adaptabilidad

La arquitectura de operadores permite a UI-TARS adaptarse a diferentes entornos GUI sin cambiar la lógica central del agente. El `GUIAgent` invoca el método `execute()` del operador, que se encarga de la implementación específica de la interacción, ya sea a través de APIs del sistema operativo, protocolos de navegador (como CDP) o servicios remotos [2] [6].

En resumen, UI-TARS-desktop utiliza un conjunto de herramientas de interacción con la GUI, impulsadas por la percepción visual y un VLM, para automatizar tareas tanto en aplicaciones de escritorio como en navegadores web, con una arquitectura flexible que soporta entornos locales y remotos.

## MÓDULO H: Multi-agente

La investigación del código fuente de UI-TARS-desktop no ha revelado evidencia de una arquitectura multi-agente explícita o de la capacidad del agente para crear y coordinar sub-agentes. Las búsquedas de términos como "multi-agent", "sub-agent" u "orchestration" en el repositorio de GitHub no arrojaron resultados relevantes que indiquen la implementación de tales funcionalidades.

Basado en el análisis de los archivos clave como `GUIAgent.ts`, `runAgent.ts`, `Model.ts` y `prompts.ts`, UI-TARS-desktop opera como un **agente singular** que sigue un ciclo iterativo de percepción, razonamiento y acción. Su diseño se centra en la interacción autónoma con interfaces gráficas de usuario (GUI) a través de un modelo de lenguaje visual (VLM) y un sistema de operadores [1] [2] [3] [5].

### Funcionamiento como Agente Singular

El agente UI-TARS-desktop aborda las tareas de forma individual, ejecutando un bucle principal donde:

*   **Percibe el entorno**: Toma capturas de pantalla de la GUI actual.
*   **Razona**: Envía la captura de pantalla y el historial de conversación a un VLM para obtener una predicción de la siguiente acción.
*   **Actúa**: Ejecuta la acción predicha a través de un operador (local o remoto).

Este ciclo se repite hasta que la tarea se completa (`finished()`), requiere intervención del usuario (`call_user()`) o se encuentra un error (`ERROR`) [2].

### Implicaciones de la Arquitectura Singular

La ausencia de capacidades multi-agente implica que:

*   **No hay delegación de tareas**: El agente no puede dividir una tarea compleja en subtareas y asignarlas a otros agentes especializados.
*   **No hay colaboración explícita**: No existe un mecanismo incorporado para que UI-TARS colabore con otras instancias de agentes o sistemas autónomos.
*   **Control centralizado**: Todas las decisiones y ejecuciones son manejadas por una única instancia del agente.

Aunque la arquitectura actual no soporta explícitamente la funcionalidad multi-agente, la modularidad del sistema de operadores y la capacidad de interactuar con entornos remotos (`RemoteComputer`, `RemoteBrowser`) podrían sentar las bases para futuras extensiones que permitan la integración con sistemas de orquestación externos o la coordinación de múltiples instancias de UI-TARS. Sin embargo, en la versión actual, el enfoque es el control autónomo de una única instancia de GUI.

## MÓDULO I: Integraciones

El agente UI-TARS-desktop se integra con varios servicios y sistemas para extender sus capacidades más allá del control local. Estas integraciones son fundamentales para operar en entornos remotos (sandboxes y navegadores remotos) y para interactuar con modelos de lenguaje visual (VLM) externos. El `ProxyClient` y el módulo de autenticación (`auth.ts`) son componentes clave en la gestión de estas integraciones [1] [7].

### Integración con Servicios Remotos de Sandbox y Navegador

UI-TARS se integra con servicios remotos para proporcionar entornos aislados y escalables para la ejecución de tareas. Esta integración se realiza a través de APIs HTTP que son invocadas por el `ProxyClient`:

*   **Servicios de Proxy (`PROXY_URL`, `BROWSER_URL`)**: El agente se conecta a endpoints de proxy definidos por `PROXY_URL` (para recursos de computadora/sandbox) y `BROWSER_URL` (para recursos de navegador). Estos servicios son responsables de la asignación, gestión y liberación de los entornos remotos [7].
*   **Asignación y Liberación de Recursos**: El `ProxyClient` realiza llamadas a la API para `allocResource` (asignar un sandbox o navegador) y `releaseResource` (liberar un sandbox o navegador). Esto permite al agente obtener y gestionar dinámicamente los recursos computacionales remotos según sea necesario [7].
*   **Información del Sandbox/Navegador**: El agente puede obtener información detallada sobre los recursos asignados, como `SandboxInfo` (que incluye `sandBoxId`, `osType`, `rdpUrl`) y `BrowserInfo` o `HdfBrowserInfo` (que contienen `browserId`, `wsUrl`, `cdpUrl`, `vncUrl`). Estas URLs son cruciales para establecer la conexión y el control sobre los entornos remotos [7].
*   **Balance de Tiempo (`TIME_URL`)**: Existe una integración con un servicio de balance de tiempo (`TIME_URL`) para consultar el `computerBalance` y `browserBalance`, lo que sugiere un modelo de consumo basado en el tiempo para el uso de los recursos remotos [7].

### Integración con Modelos de Lenguaje Visual (VLM)

La integración con VLMs es central para la capacidad de razonamiento de UI-TARS. El `Model.ts` gestiona esta integración [3]:

*   **API de OpenAI**: UI-TARS utiliza la API de OpenAI para interactuar con modelos de lenguaje visual. Esto incluye la configuración de `baseURL`, `apiKey`, `model`, `max_tokens`, `temperature` y `top_p` [3].
*   **API de Chat Completions**: El agente puede utilizar la API estándar de Chat Completions de OpenAI para enviar mensajes de texto e imágenes al VLM y recibir predicciones [3].
*   **API de Responses**: Para un procesamiento más eficiente y contextual, UI-TARS puede integrarse con la API de Responses de OpenAI. Esta API permite el envío de mensajes incrementales y la gestión de un contexto de imagen deslizante a través de `previous_response_id`, optimizando el uso de tokens y el rendimiento del modelo [3].
*   **Modelos Remotos de VLM**: El `ProxyClient` también se integra con un servicio para obtener la versión del VLM remoto (`getRemoteVLMProvider`) y verificar si soporta la API de Responses (`getRemoteVLMResponseApiSupport`). Esto indica que UI-TARS puede utilizar VLMs alojados remotamente, posiblemente proporcionados por ByteDance o terceros [7].

### Autenticación y Seguridad

La seguridad de las integraciones se maneja a través de un mecanismo de autenticación:

*   **`getAuthHeader()`**: Antes de realizar cualquier solicitud a los servicios de proxy, se obtiene un encabezado de autenticación. Esto asegura que todas las comunicaciones con los servicios remotos estén autenticadas y autorizadas [7].
*   **`registerDevice()`**: El dispositivo (la instancia de UI-TARS) se registra con el servicio de autenticación. Este paso es crucial para obtener las credenciales necesarias para interactuar con los servicios integrados [7].
*   **Manejo de Errores de Autenticación**: Si el registro del dispositivo falla, el `ProxyClient` lanza un error, impidiendo la asignación de recursos remotos [7].

En resumen, UI-TARS-desktop se integra de manera robusta con servicios remotos para la gestión de sandboxes y navegadores, así como con APIs de modelos de lenguaje visual. La autenticación es un pilar fundamental de estas integraciones, asegurando un acceso seguro y controlado a los recursos y capacidades externas.

## MÓDULO J: Multimodal

El agente UI-TARS-desktop es inherentemente multimodal, ya que su capacidad principal radica en la interacción con interfaces gráficas de usuario (GUI) a través de la percepción visual y la generación de acciones. Su multimodalidad se centra principalmente en el procesamiento de imágenes (capturas de pantalla) y la integración con modelos de lenguaje visual (VLM) para el razonamiento y la toma de decisiones. No se ha encontrado evidencia en el código fuente de soporte directo para el procesamiento de audio o video.

### Procesamiento de Imágenes

La multimodalidad de UI-TARS se manifiesta en el siguiente flujo de procesamiento de imágenes:

*   **Captura de Pantalla**: El agente captura el estado visual actual del entorno (escritorio o navegador) mediante la toma de capturas de pantalla. Estas capturas se obtienen en formato base64 (`screenshotBase64`) y se almacenan junto con metadatos como las dimensiones físicas (`screenWidth`, `screenHeight`) y el factor de escala (`scaleFactor`) [2] [4].
*   **Preprocesamiento y Redimensionamiento**: Antes de enviar las imágenes al VLM, se someten a un proceso de preprocesamiento y redimensionamiento (`preprocessResizeImage`). Este paso es crucial para optimizar el tamaño de la imagen y asegurar que se ajuste a los límites de píxeles que el VLM puede manejar. Los límites de píxeles varían según la versión del modelo VLM utilizado:
    *   `MAX_PIXELS_V1_0`
    *   `MAX_PIXELS_V1_5`
    *   `MAX_PIXELS_DOUBAO`
    Este redimensionamiento se realiza para mantener la eficiencia y evitar exceder los límites de entrada del modelo, utilizando la librería `Jimp` para la manipulación de imágenes [3] [4].
*   **Codificación para el VLM**: Las imágenes preprocesadas se codifican en formato base64 y se integran en los mensajes que se envían al VLM. Para la API de OpenAI, esto implica convertir las imágenes en objetos `image_url` dentro del contenido del mensaje. Si se utiliza la API de Responses, se transforman en `input_image` para un procesamiento incremental [3] [4].

### Modelos de Lenguaje Visual (VLM) Utilizados

UI-TARS se integra con modelos de lenguaje visual, principalmente a través de la API de OpenAI. La configuración del modelo (`UITarsModelConfig`) permite especificar el `model` a utilizar, así como otros parámetros como `max_tokens`, `temperature` y `top_p` [3].

El agente puede interactuar con diferentes versiones de modelos VLM, que se identifican a través de `UITarsModelVersion`:

*   `UITarsModelVersion.V1_0`
*   `UITarsModelVersion.V1_5`
*   `UITarsModelVersion.DOUBAO_1_5_15B`
*   `UITarsModelVersion.DOUBAO_1_5_20B`

La elección de la versión del modelo influye en los límites de píxeles para el procesamiento de imágenes y en la configuración de `max_tokens` [3]. El `ProxyClient` también puede obtener la versión del VLM remoto (`getRemoteVLMProvider`) y verificar si soporta la API de Responses (`getRemoteVLMResponseApiSupport`), lo que sugiere flexibilidad en la elección del proveedor del modelo [7].

### Ausencia de Procesamiento de Audio y Video

Aunque UI-TARS es multimodal en el dominio visual, el análisis del código fuente no ha revelado componentes o integraciones específicas para el procesamiento de audio o video. Las entradas al modelo se limitan a texto y capturas de pantalla. Esto implica que el agente no puede percibir o interactuar directamente con elementos de audio o video en el entorno GUI, más allá de lo que pueda inferirse de las imágenes estáticas.

## MÓDULO K: Límites y errores

El agente UI-TARS-desktop incorpora varios mecanismos para manejar errores y limitaciones inherentes a su operación, asegurando una cierta robustez y la capacidad de informar sobre fallos. La gestión de errores se centraliza en la clase `GUIAgent` y las definiciones de `ErrorStatusEnum` y `GUIAgentError` en `agent.ts` [2].

### Límites Operacionales

*   **Límite de Bucles (`maxLoopCount`)**: El agente está configurado con un número máximo de iteraciones (`maxLoopCount`) para evitar bucles infinitos. Si se alcanza este límite sin que la tarea se complete, el agente transiciona al estado `ERROR` con el código `REACH_MAXLOOP_ERROR` [2].
*   **Límite de Errores de Captura de Pantalla (`MAX_SNAPSHOT_ERR_CNT`)**: Existe un umbral para el número de fallos consecutivos en la toma de capturas de pantalla. Si este contador excede `MAX_SNAPSHOT_ERR_CNT` (por defecto, 10), el agente considera que el entorno no es estable o accesible y termina con un `SCREENSHOT_RETRY_ERROR` [2] [8].
*   **Límites de Píxeles de Imagen (`MAX_PIXELS_V1_0`, `MAX_PIXELS_V1_5`, `MAX_PIXELS_DOUBAO`)**: Los modelos de lenguaje visual (VLM) tienen limitaciones en la resolución de las imágenes que pueden procesar. UI-TARS preprocesa y redimensiona las capturas de pantalla para ajustarse a estos límites, que varían según la versión del modelo VLM utilizado. Esto puede implicar una pérdida de detalle en la imagen si la resolución original es muy alta [3] [4].
*   **Ventana de Contexto de Imagen (`MAX_IMAGE_LENGTH`)**: Para gestionar la memoria y el contexto del VLM, el agente mantiene una ventana deslizante de imágenes. Solo un número limitado de las capturas de pantalla más recientes (`MAX_IMAGE_LENGTH`, por defecto 6) se conservan en el historial, eliminando las más antiguas. Esto significa que el VLM solo tiene acceso a un historial visual reciente [4].
*   **Límite de Tokens del Modelo (`max_tokens`)**: Los modelos VLM tienen un límite en la cantidad de tokens que pueden procesar en una sola invocación. UI-TARS configura `max_tokens` para el VLM, lo que puede afectar la longitud de la predicción de texto que el modelo puede generar [3].
*   **Límites de Reintentos**: Las operaciones críticas como la captura de pantalla, la invocación del modelo y la ejecución de acciones tienen un número configurable de reintentos (`maxRetries`). Si una operación falla repetidamente después de estos reintentos, se considera un error fatal [2].

### Mecanismos de Fallo y Recuperación

UI-TARS implementa un sistema de manejo de errores que permite al agente identificar, clasificar y, en algunos casos, recuperarse de los fallos:

*   **Reintentos (`asyncRetry`)**: La ejecución de cada acción a través de `operator.execute()` está envuelta en un bloque `asyncRetry`. Por defecto, se configura con `maxRetries: 1`, lo que significa que si una acción falla, se intentará una vez más antes de reportar un error fatal [2].
*   **Clasificación de Errores (`ErrorStatusEnum`)**: El agente utiliza un enumerador `ErrorStatusEnum` para clasificar los diferentes tipos de errores que pueden ocurrir, como `SCREENSHOT_RETRY_ERROR`, `INVOKE_RETRY_ERROR`, `EXECUTE_RETRY_ERROR`, `MODEL_SERVICE_ERROR`, `REACH_MAXLOOP_ERROR`, `ENVIRONMENT_ERROR` y `UNKNOWN_ERROR` [2].
*   **Objeto `GUIAgentError`**: Los errores se encapsulan en objetos `GUIAgentError`, que proporcionan un `status` (del `ErrorStatusEnum`), un `message` descriptivo y el `stack` de la traza para facilitar la depuración [2].
*   **Acciones Internas de Error**: El VLM puede predecir una acción interna `error_env` si detecta un problema en el entorno. Esto permite al modelo señalar proactivamente un fallo y hacer que el agente transicione al estado `ERROR` [2].
*   **Notificación de Errores (`onError` Callback)**: Cuando ocurre un error irrecuperable, el agente invoca un callback `onError` para notificar a la aplicación principal o al usuario. Esto permite que la interfaz de usuario muestre mensajes de error apropiados o que se tomen acciones correctivas externas [2].
*   **Manejo de Aborto por Usuario**: Si el usuario detiene la ejecución del agente (`signal?.aborted` o `isStopped`), el agente transiciona al estado `USER_STOPPED` y ejecuta una acción `user_stop` para limpiar el estado, lo que representa una terminación controlada en lugar de un fallo [2].
*   **Restablecimiento del Modelo**: Después de cualquier terminación (exitosa o con error), el estado interno del modelo VLM se restablece (`model.reset()`) para asegurar que la próxima ejecución comience desde un estado limpio [2].

En resumen, UI-TARS-desktop está diseñado para operar dentro de límites definidos para sus recursos y para manejar una variedad de escenarios de error a través de reintentos, clasificación de errores y mecanismos de notificación, aunque la recuperación de errores complejos a menudo requiere la intervención del usuario o la reconfiguración de la tarea.

## MÓDULO L: Benchmarks

El agente UI-TARS-desktop ha sido evaluado en una variedad de benchmarks para demostrar sus capacidades en el control de interfaces gráficas de usuario (GUI) en diferentes entornos. La información disponible, principalmente de su repositorio GitHub y artículos técnicos, destaca su rendimiento en tareas de uso de computadora, navegador y teléfono, comparándolo con otros agentes y modelos de lenguaje visual (VLM) [9] [10] [11] [12] [13] [14] [15] [16] [17] [18] [19] [20] [21].

### Benchmarks Clave y Resultados

*   **OSWorld**: UI-TARS ha sido evaluado en el benchmark OSWorld, que se centra en tareas de uso de computadora. Las comparaciones de rendimiento se han realizado entre diferentes escalas del modelo UI-TARS, como UI-TARS-72B-DPO y UI-TARS-1.5-7B [10] [14]. Aunque no se proporcionan cifras exactas en los snippets, se menciona que UI-TARS-1.5-7B es un modelo de 7B que puede ejecutarse en la mayoría de los equipos [12]. El informe técnico de UI-TARS-2 también menciona que OSWorld [75] proporciona 369 tareas [15].
*   **BrowseComp**: UI-TARS-2 demuestra un fuerte rendimiento en benchmarks de búsqueda de información de largo horizonte, como BrowseComp, alcanzando un 29.6 [13]. Este benchmark evalúa la capacidad del agente para navegar y extraer información de la web de manera efectiva.
*   **Comparaciones con Otros Modelos**: UI-TARS ha sido comparado con modelos líderes en el campo:
    *   **Claude 3.5 Sonnet**: UI-TARS igualó o superó a Claude 3.5 Sonnet en tareas de uso de computadora [11].
    *   **GPT-4o**: También se comparó con GPT-4o en varios frameworks de uso de computadora [11].
    *   **Aguvis Framework**: UI-TARS superó al framework Aguvis con su enfoque nativo [11].
*   **SWE-bench**: Aunque UI-TARS no aparece directamente en las tablas de clasificación de SWE-bench en los resultados de búsqueda, el informe técnico de UI-TARS-2 menciona que SWE-bench enmarca la corrección de errores a nivel de repositorio y ha generado una serie de sistemas agénticos como SWE-agent [17]. Esto sugiere que la capacidad de UI-TARS para el control de escritorio podría ser relevante para tareas de ingeniería de software, aunque no se presentan resultados directos de UI-TARS en este benchmark.

### Tipos de Benchmarks Cubiertos

La superioridad de UI-TARS-1.5 es consistente en siete benchmarks que abarcan las siguientes categorías [9]:

*   **Uso de Computadora (Computer Use)**
*   **Uso de Navegador (Browser Use)**
*   **Uso de Teléfono (Phone Use)**

### Implicaciones de los Resultados

Los resultados de los benchmarks indican que UI-TARS-desktop es un agente GUI competitivo, capaz de realizar tareas complejas en diversos entornos. Su rendimiento en OSWorld y BrowseComp subraya su habilidad para el control de escritorio y la navegación web. Las comparaciones favorables con modelos como Claude 3.5 Sonnet y GPT-4o resaltan su eficacia en la automatización de tareas GUI. La mención de UI-TARS-2 y su enfoque en el aprendizaje por refuerzo multi-turno sugiere una evolución continua en la capacidad del agente para manejar tareas más complejas y de largo plazo [16].

Es importante señalar que, si bien se mencionan varios benchmarks, la disponibilidad de datos numéricos detallados para cada uno de ellos en los snippets es limitada. Sin embargo, la recurrencia de UI-TARS en discusiones sobre agentes GUI y su presencia en plataformas como Hugging Face [14] y Medium [18] [19] confirman su relevancia en la comunidad de investigación y desarrollo de agentes de IA.

## Lecciones para el Monstruo

La investigación profunda de UI-TARS-desktop ofrece varias lecciones valiosas para el desarrollo de agentes de IA avanzados, especialmente aquellos enfocados en la interacción con interfaces gráficas de usuario. Estas lecciones pueden guiar la creación de sistemas más robustos, eficientes y autónomos:

1.  **La Abstracción del Operador es Clave para la Flexibilidad del Entorno**: La arquitectura de UI-TARS, que separa la lógica del agente de la implementación específica de la interacción con la GUI a través de operadores (`LocalComputer`, `LocalBrowser`, `RemoteComputer`, `RemoteBrowser`), es fundamental. Esta abstracción permite al agente operar en diversos entornos (local, remoto, escritorio, navegador) sin reescribir su lógica central. Para un "Monstruo" (agente generalista), esto significa que la capacidad de adaptarse a cualquier entorno computacional (sistemas operativos, navegadores, dispositivos móviles, etc.) se logra mediante una capa de abstracción bien diseñada que traduce las intenciones del agente en acciones específicas del entorno. Esto minimiza la complejidad y maximiza la portabilidad.

2.  **La Percepción Visual y el VLM son el Corazón de la Interacción GUI**: La dependencia de UI-TARS en las capturas de pantalla y los Modelos de Lenguaje Visual (VLM) para la percepción y el razonamiento es una lección crítica. La capacidad de "ver" la interfaz de usuario y comprender su estado visual es lo que permite al agente interactuar de manera similar a un humano. Un "Monstruo" debe priorizar el desarrollo de capacidades de percepción visual altamente sofisticadas, incluyendo el preprocesamiento inteligente de imágenes para optimizar la entrada del VLM, y la capacidad de interpretar elementos visuales complejos, no solo texto. La evolución hacia VLMs más potentes y eficientes es directamente proporcional a la autonomía del agente.

3.  **La Gestión del Contexto y la Memoria es Esencial para la Coherencia a Largo Plazo**: La implementación de una ventana deslizante para el historial de conversaciones y, crucialmente, para las imágenes, demuestra la importancia de una gestión de memoria eficiente. Mantener un contexto relevante y actualizado para el VLM, sin exceder los límites de tokens o sobrecargar el procesamiento, es vital para tareas de largo horizonte. Un "Monstruo" debe desarrollar mecanismos avanzados de memoria que no solo almacenen el historial, sino que también prioricen y resuman la información más relevante, y que puedan manejar grandes volúmenes de datos multimodales de manera eficiente para mantener la coherencia y el razonamiento a lo largo de interacciones prolongadas.

4.  **Mecanismos Robustos de Manejo de Errores y Reintentos son Indispensables**: UI-TARS incorpora reintentos automáticos, clasificación de errores y callbacks de notificación, lo que subraya la inevitabilidad de los fallos en entornos dinámicos. Un "Monstruo" debe tener un sistema de manejo de errores aún más sofisticado, capaz de diagnosticar la causa raíz de los problemas, intentar estrategias de recuperación alternativas y, cuando sea necesario, solicitar aclaraciones o asistencia al usuario de manera inteligente. La resiliencia ante errores transitorios y la capacidad de recuperarse de fallos inesperados son características definitorias de un agente verdaderamente autónomo.

5.  **La Autenticación y la Seguridad en las Integraciones Remotas son No Negociables**: La forma en que UI-TARS maneja la autenticación (`fetchWithAuth`, `getAuthHeader`, `registerDevice`) para sus integraciones con servicios de proxy remotos es un modelo a seguir. Para un "Monstruo" que interactuará con una multitud de servicios externos (APIs, sandboxes, bases de datos, etc.), la seguridad y la autenticación robusta son primordiales. Esto implica no solo el uso de tokens y encabezados de autenticación, sino también la gestión segura de credenciales, el cumplimiento de protocolos OAuth y la capacidad de operar en entornos con diferentes requisitos de seguridad, protegiendo tanto los datos del usuario como la integridad del agente.

## Referencias

[1] `bytedance/UI-TARS-desktop` GitHub Repository. (n.d.). Retrieved from https://github.com/bytedance/UI-TARS-desktop
[2] `GUIAgent.ts` source code. (n.d.). Retrieved from /home/ubuntu/UI-TARS-desktop/packages/ui-tars/sdk/src/GUIAgent.ts
[3] `Model.ts` source code. (n.d.). Retrieved from /home/ubuntu/UI-TARS-desktop/packages/ui-tars/sdk/src/Model.ts
[4] `utils.ts` source code. (n.d.). Retrieved from /home/ubuntu/UI-TARS-desktop/packages/ui-tars/sdk/src/utils.ts
[5] `prompts.ts` source code. (n.d.). Retrieved from /home/ubuntu/UI-TARS-desktop/apps/ui-tars/src/main/agent/prompts.ts
[6] `runAgent.ts` source code. (n.d.). Retrieved from /home/ubuntu/UI-TARS-desktop/apps/ui-tars/src/main/services/runAgent.ts
[7] `proxyClient.ts` source code. (n.d.). Retrieved from /home/ubuntu/UI-TARS-desktop/apps/ui-tars/src/main/remote/proxyClient.ts
[8] `agent.ts` source code. (n.d.). Retrieved from /home/ubuntu/UI-TARS-desktop/packages/ui-tars/shared/src/types/agent.ts
[9] Introducing UI-TARS-1.5. (n.d.). Retrieved from https://seed.bytedance.com/en/ui-tars
[10] bytedance/UI-TARS: Pioneering Automated GUI Interaction ... (n.d.). Retrieved from https://github.com/bytedance/ui-tars
[11] UI-TARS Shows Strong Computer Use Capabilities in ... (2025, February 5). Retrieved from https://www.deeplearning.ai/the-batch/ui-tars-shows-strong-computer-use-capabilities-in-benchmarks/
[12] UI-TARS desktop agent - this actually looks interesting as it ... (n.d.). Retrieved from https://www.reddit.com/r/LocalLLaMA/comments/1r1fnon/uitars_desktop_agent_this_actually_looks/
[13] UI-TARS-2 Technical Report: Advancing GUI Agent with ... (2025, September 5). Retrieved from https://arxiv.org/html/2509.02544v2
[14] Mungert/UI-TARS-1.5-7B-GGUF. (n.d.). Retrieved from https://huggingface.co/Mungert/UI-TARS-1.5-7B-GGUF
[15] Ui-tars-2 technical report: Advancing gui agent with multi-turn reinforcement learning. (n.d.). Retrieved from https://arxiv.org/abs/2509.02544
[16] KG-RAG: Enhancing GUI Agent Decision-Making via Knowledge Graph-Driven Retrieval-Augmented Generation. (n.d.). Retrieved from https://aclanthology.org/2025.emnlp-main.274/
[17] UI-TARS-2 Technical Report: Advancing GUI Agent with ... (n.d.). Retrieved from https://arxiv.org/pdf/2509.02544
[18] Run your Local Desktop AI Agents at Zero Cost with UI-TARS ... (2026, January 12). Retrieved from https://medium.com/towardsdev/run-your-local-desktop-ai-agents-at-zero-cost-with-ui-tars-desktop-agents-and-lm-studio-0631b01844b1
[19] Bytedance UI-TARS AI Desktop: AI Agent for Computer Control. (n.d.). Retrieved from https://ui-tarsai.com/
[20] UI-TARS-desktop: The AI Agent That Actually Sees and Controls Our ... (2026, January 11). Retrieved from https://yuv.ai/blog/ui-tars-desktop
[21] ByteDance just released a desktop automation agent that runs 100 ... (2026, February 4). Retrieved from https://www.reddit.com/r/accelerate/comments/1qvcs2e/bytedance_just_released_a_desktop_automation/

---

## Fase 3 — Módulos Complementarios: UI-TARS-desktop (ByteDance)

### Integraciones y Connectors

UI-TARS-desktop, desarrollado por ByteDance, se posiciona como una plataforma robusta para la automatización de interfaces gráficas de usuario (GUI) mediante agentes de IA. Su arquitectura está diseñada para facilitar una interacción fluida con entornos de escritorio y navegadores, lo que se logra a través de un sistema de integraciones y conectores bien definidos, siendo el **Model Context Protocol (MCP)** un pilar fundamental de esta capacidad [1].

El núcleo de UI-TARS-desktop se basa en el **Model Context Protocol (MCP)**, lo que le permite no solo operar de manera autónoma en el escritorio, sino también "montar" servidores MCP externos para extender sus funcionalidades y conectarse con una amplia gama de herramientas del mundo real [1]. Esta integración con MCP es crucial, ya que transforma a UI-TARS-desktop de un simple agente de automatización en una plataforma extensible capaz de interactuar con diversos servicios y aplicaciones. Los servidores MCP actúan como puentes, permitiendo que el agente acceda a APIs y herramientas externas, lo que es esencial para tareas complejas que requieren más allá de la manipulación directa de la GUI [1].

En cuanto a las **APIs externas y conectores de escritorio soportados**, UI-TARS-desktop expone sus propias APIs para que otros agentes de IA puedan interactuar con el entorno de escritorio. Estas APIs proporcionan herramientas para la gestión de ventanas, el acceso al portapapeles y operaciones del sistema de archivos [2]. Esto significa que, a través de estas APIs nativas, los desarrolladores pueden construir agentes de IA que no solo automatizan tareas de escritorio, sino que también gestionan ventanas y manipulan archivos de manera programática. La capacidad de interactuar con el sistema de archivos y el portapapeles es fundamental para la automatización de flujos de trabajo que implican la transferencia de datos entre aplicaciones o la manipulación de documentos locales [2].

Un componente clave en la estrategia de integración de UI-TARS-desktop es el mecanismo **UTIO (UI-TARS Insights and Observation)**. UTIO es un sistema de recolección de datos diseñado para obtener información sobre el comportamiento y el rendimiento de UI-TARS-desktop. Más allá de la telemetría, UTIO también está relacionado con la capacidad de compartir información y eventos [3]. El servidor UTIO acepta eventos a través de solicitudes HTTP POST, manejando tres tipos principales de eventos:

*   **`AppLaunched`**: Este evento se dispara cuando la aplicación UI-TARS-desktop se inicia, proporcionando detalles como el tipo de plataforma, la versión del sistema operativo, y las dimensiones de la pantalla [3]. Esto es útil para monitorear el uso y la compatibilidad del agente en diferentes entornos.
*   **`SendInstruction`**: Registra las instrucciones enviadas por el usuario al agente, lo que permite un seguimiento detallado de las interacciones y el rendimiento del agente en la ejecución de tareas específicas [3].
*   **`ShareReport`**: Facilita el intercambio de informes, que pueden incluir la URL de la última captura de pantalla o un reporte más detallado, junto con la instrucción asociada [3]. Esta funcionalidad es vital para la depuración, la colaboración y la mejora continua del agente.

La especificación de la interfaz del servidor UTIO detalla que los eventos se envían a un `Endpoint` específico (`POST /your-utio-endpoint`) con un `Content-Type: application/json`. Las respuestas exitosas se indican con un `200 OK` y un JSON `{"success": true}` [3]. Aunque la documentación no profundiza explícitamente en **OAuth** o **webhooks** en el contexto de integraciones directas para autenticación o notificaciones asíncronas, la naturaleza de la integración MCP y la capacidad de montar servidores externos sugieren que estas funcionalidades pueden ser implementadas a través de la configuración de dichos servidores MCP. Es decir, si un servidor MCP externo requiere OAuth para acceder a una API, UI-TARS-desktop, al interactuar con ese servidor, se beneficiaría indirectamente de esa capacidad. De manera similar, los webhooks podrían ser gestionados por servidores MCP externos para recibir notificaciones de eventos de terceros y luego ser procesados por UI-TARS-desktop [1].

En resumen, UI-TARS-desktop ofrece un marco de integración flexible y potente a través de su dependencia en el Model Context Protocol. Esto le permite no solo interactuar profundamente con el entorno de escritorio a través de sus APIs nativas, sino también extender sus capacidades mediante la conexión a servidores MCP externos, lo que abre la puerta a una vasta gama de herramientas y servicios. El sistema UTIO complementa estas integraciones al proporcionar un mecanismo robusto para la recolección de datos y el intercambio de información, lo que es fundamental para la operabilidad y el desarrollo continuo de agentes de IA [1, 2, 3].

### Referencias

[1] bytedance/UI-TARS-desktop: The Open-Source Multimodal AI Agent Stack: Connecting Cutting-Edge AI Models and Agent Infra. GitHub. Disponible en: [https://github.com/bytedance/ui-tars-desktop](https://github.com/bytedance/ui-tars-desktop)
[2] UI TARS Desktop MCP Server - Seamless Multimodal. Shyft.ai. Disponible en: [https://shyft.ai/mcp/bytedance-ui-tars-desktop-github](https://shyft.ai/mcp/bytedance-ui-tars-desktop-github)
[3] UI-TARS-desktop/docs/setting.md at main · bytedance/UI-TARS-desktop · GitHub. Disponible en: [https://github.com/bytedance/UI-TARS-desktop/blob/main/docs/setting.md](https://github.com/bytedance/UI-TARS-desktop/blob/main/docs/setting.md)


 donde el agente hace clic en ubicaciones incorrectas [11]. Esto sugiere la necesidad de robustecer los mecanismos de *grounding* visual y la gestión de la conectividad.

### Timeouts

La gestión de *timeouts* es un área de mejora activa. Se ha discutido en GitHub la necesidad de aumentar el *timeout* por defecto para operaciones de MCP (Model Context Protocol) de larga duración, sugiriendo un rango de 60 a 120 segundos para acomodar tareas que requieren más tiempo, como la gestión de paquetes [8].

### Contexto Agotado y Reintentos

No se encontró información explícita sobre cómo UI-TARS-desktop maneja el agotamiento del contexto o si implementa mecanismos de reintentos automáticos para tareas fallidas. Sin embargo, un informe técnico de UI-TARS-2 (una versión posterior o relacionada) de septiembre de 2025 menciona un "lease-based lifecycle mechanism" que libera recursos automáticamente después de la finalización o fallo de la tarea, y las sesiones vencidas se recuperan [12]. Esto indica un enfoque en la gestión de recursos y la recuperación ante fallos a un nivel más amplio.

### Mejoras en el Manejo de Errores

Un *pull request* en el repositorio de GitHub de UI-TARS-desktop menciona una mejora en el manejo de errores de inicialización de la aplicación ("improve app initialization error handling") [7], lo que sugiere un esfuerzo continuo por hacer el agente más robusto.

## Referencias

[1] ScreenSpot-Pro Leaderboard. (n.d.). *ScreenSpot-Pro Leaderboard*. Recuperado de [https://gui-agent.github.io/grounding-leaderboard/](https://gui-agent.github.io/grounding-leaderboard/)
[2] bytedance/UI-TARS. (n.d.). *GitHub - bytedance/UI-TARS: Pioneering Automated GUI Interaction with Native Agents*. Recuperado de [https://github.com/bytedance/ui-tars](https://github.com/bytedance/ui-tars)
[3] bytedance/UI-TARS-desktop. (n.d.). *GitHub - bytedance/UI-TARS-desktop: The Open-Source Multimodal AI Agent Stack: Connecting Cutting-Edge AI Models and Agent Infra*. Recuperado de [https://github.com/bytedance/ui-tars-desktop](https://github.com/bytedance/ui-tars-desktop)
[4] bytedance/UI-TARS-desktop. (2025, Enero 21). *Issue #9 · bytedance/UI-TARS-desktop - Linux Support*. Recuperado de [https://github.com/bytedance/UI-TARS-desktop/issues/9](https://github.com/bytedance/UI-TARS-desktop/issues/9)
[5] r/LocalLLaMA. (n.d.). *UI-TARS doesn't yet support Linux, Can someone...*. Recuperado de [https://www.reddit.com/r/LocalLLaMA/comments/1ibiinr/uitars_doesnt_yet_support_linux_can_someone/](https://www.reddit.com/r/LocalLLaMA/comments/1ibiinr/uitars_doesnt_yet_support_linux_can_someone/)
[6] bytedance/UI-TARS-desktop. (n.d.). *UI-TARS-desktop/docs/sdk.md at main*. Recuperado de [https://github.com/bytedance/UI-TARS-desktop/blob/main/docs/sdk.md](https://github.com/bytedance/UI-TARS-desktop/blob/main/docs/sdk.md)
[7] bytedance/UI-TARS-desktop. (n.d.). *Pull requests · bytedance/UI-TARS-desktop*. Recuperado de [https://github.com/bytedance/UI-TARS-desktop/pulls](https://github.com/bytedance/UI-TARS-desktop/pulls)
[8] bytedance/UI-TARS-desktop. (2025, Agosto 8). *feat: increase default MCP agent timeout for long-running operations...*. Recuperado de [https://github.com/bytedance/UI-TARS-desktop/issues/1050](https://github.com/bytedance/UI-TARS-desktop/issues/1050)
[9] bytedance/UI-TARS-desktop. (2025, Junio 5). *Connection error with UITARS-1.5-7B deployed on HF...*. Recuperado de [https://github.com/bytedance/UI-TARS-desktop/issues/663](https://github.com/bytedance/UI-TARS-desktop/issues/663)
[10] bytedance/UI-TARS-desktop. (2025, Julio 25). *Too many model invoke failures: Connection error....*. Recuperado de [https://github.com/bytedance/UI-TARS-desktop/issues/985](https://github.com/bytedance/UI-TARS-desktop/issues/985)
[11] ByteDance-Seed/UI-TARS-1.5-7B. (2025, Abril 18). *Error bbox locating*. Recuperado de [https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B/discussions/3](https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B/discussions/3)
[12] UI-TARS-2 Technical Report: Advancing GUI Agent with.... (2025, Septiembre 5). *arXiv*. Recuperado de [https://arxiv.org/html/2509.02544v2](https://arxiv.org/html/2509.02544v2)