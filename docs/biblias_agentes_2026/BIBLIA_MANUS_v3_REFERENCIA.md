# BIBLIA DE IMPLEMENTACIÓN: MANUS AI
**Fecha de Actualización:** 30 de Abril de 2026
**Objetivo:** Mapa de implementación de ingeniería inversa para replicar el 95%+ de las capacidades de Manus.

---

## M01 — Loop del Agente

### Descripción Técnica
# M01 — Loop del Agente: Descripción Técnica Completa

El **Loop del Agente de Manus AI** constituye el núcleo operativo de su arquitectura, permitiendo la ejecución autónoma de tareas complejas mediante un ciclo iterativo de razonamiento y acción. Este módulo es fundamental para la capacidad de Manus de interpretar objetivos de usuario, planificar secuencias de acciones, interactuar con diversos entornos y herramientas, y adaptarse dinámicamente a los resultados y errores durante la ejecución [1] [2].

## Ciclo de Razonamiento y Ejecución

El proceso comienza con la recepción de una **entrada del usuario**, que el agente interpreta para establecer un objetivo principal. A partir de este objetivo, Manus genera un **plan inicial** desglosado en tareas más pequeñas y manejables. Este plan no es estático; se somete a una evaluación y re-planificación continuas en cada iteración del ciclo [2].

Cada iteración del loop sigue una secuencia bien definida, monitoreada a través de eventos `status_update` obtenidos mediante `task.listMessages` [5]:

1.  **Selección de Acción:** Basándose en el **contexto actual** y un espacio de acción predefinido, el modelo de lenguaje grande (LLM) subyacente selecciona la acción más apropiada a realizar. Este espacio de acción incluye una variedad de herramientas internas y externas que Manus puede invocar [1].
2.  **Ejecución de Acción:** La acción seleccionada se ejecuta en el entorno correspondiente, que puede ser el sandbox de la máquina virtual de Manus, una herramienta específica, o la ejecución de código. Durante esta fase, se rastrean los resultados intermedios [1] [2].
3.  **Generación de Observación:** La ejecución de la acción produce una **observación**, que es el resultado o el estado del entorno después de la acción. Esta observación es crucial para la siguiente fase del razonamiento [1].
4.  **Actualización del Contexto:** Tanto la acción realizada como la observación resultante se añaden al contexto del agente. Este contexto actualizado sirve como entrada para la siguiente iteración del loop, permitiendo que el agente mantenga un registro de su progreso y tome decisiones informadas [1].
5.  **Evaluación y Decisión:** Manus evalúa el progreso hacia el objetivo general y decide la siguiente acción. Este ciclo se repite hasta que el objetivo se completa o se alcanza una condición de detención predefinida [2].

Un aspecto crítico de este ciclo es la **memoria basada en recuperación**. Cada paso puede requerir recordar acciones previas, documentos o datos externos. Manus almacena esta información como *embeddings* en una base de datos vectorial (como Milvus o Zilliz Cloud), lo que permite una búsqueda semántica rápida y eficiente cuando se necesita contexto. Esto mantiene los *prompts* concisos mientras se asegura el acceso a un vasto conocimiento relevante [2].

## Estados del Agente y Manejo de Eventos

El estado del agente (`agent_status`) es un indicador clave en el ciclo de vida de una tarea, determinando la acción a seguir por el sistema o el usuario [5]:

| `agent_status` | Significado | Acción |
|---|---|---|
| `running` | El agente está trabajando | Continuar sondeando (`polling`) |
| `stopped` | La tarea ha finalizado | Leer eventos `assistant_message` para los resultados |
| `waiting` | Requiere confirmación o entrada del usuario | Manejar según el tipo de evento (`waiting_for_event_type`) |
| `error` | La tarea ha fallado | Leer `error_message` para detalles |

Cuando el `agent_status` es `waiting`, el campo `status_detail` proporciona información sobre lo que el agente necesita. Existen dos formas principales de responder [5]:

*   **`messageAskUser`**: El agente está haciendo una pregunta. Se debe responder utilizando `task.sendMessage`.
*   **Otros tipos de eventos**: Para la mayoría de los demás eventos (`gmailSendAction`, `deployAction`, `terminalExecute`, etc.), se utiliza `task.confirmAction`. El campo `confirm_input_schema` en el evento `status_detail` describe el formato JSON esperado para la entrada de confirmación.

## Ingeniería de Contexto Avanzada

La ingeniería de contexto es una piedra angular en el diseño de Manus, permitiendo una rápida iteración y manteniendo la independencia del producto respecto a los modelos subyacentes. El framework del agente ha sido reconstruido múltiples veces, un proceso que se describe como "Descenso Gradiente Estocástico" debido a su naturaleza experimental y empírica [1].

### Optimización del KV-Cache

La tasa de aciertos del KV-cache es una métrica vital para la eficiencia de un agente de IA en producción, impactando directamente la latencia y el costo. En Manus, la relación promedio de tokens de entrada a salida es de aproximadamente 100:1, lo que subraya la importancia de una gestión eficiente del caché. Para maximizar la efectividad del KV-cache, Manus implementa varias prácticas [1]:

*   **Prefijo de Prompt Estable:** Se mantiene el prefijo del prompt del sistema inmutable para evitar la invalidación del caché. Se desaconseja la inclusión de elementos dinámicos como marcas de tiempo precisas al segundo.
*   **Contexto Append-Only:** El contexto se gestiona de forma que las acciones y observaciones anteriores no se modifican, garantizando una serialización determinista (por ejemplo, un orden estable de claves JSON) para preservar la integridad del caché.
*   **Puntos de Interrupción de Caché Explícitos:** En sistemas que no soportan el almacenamiento en caché incremental automático, Manus inserta manualmente puntos de interrupción de caché, asegurando que incluyan el final del prompt del sistema para una gestión óptima.
*   **Self-Hosting de Modelos:** Para modelos autoalojados con frameworks como vLLM, se asegura la habilitación del almacenamiento en caché de prefijos/prompts y el uso de IDs de sesión para un enrutamiento consistente de solicitudes a través de trabajadores distribuidos.

### Gestión del Espacio de Acción y Herramientas

A medida que las capacidades del agente aumentan, también lo hace la complejidad de su espacio de acción. Manus aborda esto mediante una estrategia de "enmascaramiento, no eliminación" de herramientas. En lugar de añadir o eliminar herramientas dinámicamente, lo que podría invalidar el KV-cache y confundir al modelo, Manus utiliza una máquina de estados consciente del contexto. Esta máquina enmascara los *logits* de los tokens durante la decodificación para prevenir o forzar la selección de ciertas acciones basadas en el contexto actual. La nomenclatura consistente de las herramientas (por ejemplo, `browser_` para herramientas del navegador, `shell_` para comandos de shell) facilita la aplicación de estas restricciones [1].

### El Sistema de Archivos como Memoria Externa

Reconociendo las limitaciones de las ventanas de contexto de los LLM (incluso las más grandes), Manus utiliza el sistema de archivos como una forma de memoria externa ilimitada y persistente. El agente aprende a leer y escribir archivos bajo demanda, transformando el sistema de archivos en una memoria estructurada y externalizada. Las estrategias de compresión de Manus están diseñadas para ser restaurables; por ejemplo, el contenido de una página web puede eliminarse del contexto siempre que su URL se conserve, permitiendo reducir la longitud del contexto sin pérdida permanente de información [1].

## Manejo de Errores y Robustez

Manus adopta una filosofía de "mantener lo incorrecto" en el contexto. En lugar de ocultar o limpiar los errores, el agente los retiene, permitiendo que el modelo aprenda de las acciones fallidas y sus observaciones resultantes. Esta aproximación reduce la probabilidad de repetir los mismos errores y es considerada un indicador clave del verdadero comportamiento agéntico [1] [3].

Para mitigar problemas de recursión infinita y explosión de contexto, se han identificado patrones y soluciones como [3]:

*   **Recursión Controlada:** Se establece una profundidad máxima de recursión (por ejemplo, 4) para evitar bucles infinitos, requiriendo revisión humana para profundidades mayores.
*   **Memoria con Alcance:** Se inyectan solo resúmenes relevantes para la tarea, evitando registros globales a menos que sea para depuración. Esto previene la "explosión de contexto" donde la memoria heredada se expande más allá de los límites de tokens.
*   **Metadatos de Intención Explícitos:** Se incrusta un bloque JSON con metadatos como `origin_goal`, `parent_task_id`, `intent_trace` y `depth_level` en cada prompt de tarea. Esto proporciona "anclas de intención" que ayudan a los agentes a comprender su propósito, evitar tareas redundantes y la deriva lateral.
*   **Loop Guard:** Implementación de un mecanismo de guardia para detectar invocaciones recursivas. Un ejemplo es verificar si un `agent_id` aparece en los últimos `recent_task_ids` dentro de una cierta profundidad, lanzando un `LoopDetectedError` si se detecta un patrón de bucle [3].

## Planificación y Re-planificación Dinámica

La planificación en Manus es un proceso dinámico. Después de interpretar el objetivo del usuario y crear un plan inicial, el agente evalúa continuamente el progreso y decide los siguientes pasos. Para mantener el enfoque en tareas complejas y de múltiples pasos, Manus utiliza una técnica de "recitación" [1]:

*   **Manipulación de la Atención a través de la Recitación:** Manus crea y actualiza un archivo `todo.md` que lista los objetivos pendientes. Al reescribir constantemente esta lista al final del contexto, el agente empuja su plan global a su lapso de atención reciente, mitigando el problema de "perdido en el medio" y reduciendo la desalineación de objetivos [1].

## Evitando el Few-Shot Excesivo

Aunque el *few-shot prompting* es útil, en sistemas de agentes puede llevar a la imitación excesiva de patrones, causando deriva, sobregeneralización o alucinaciones. Manus contrarresta esto introduciendo pequeñas variaciones estructuradas en acciones y observaciones, como diferentes plantillas de serialización o ruido menor en el formato, para romper patrones y ajustar la atención del modelo [1].

En resumen, el Loop del Agente de Manus AI es un sistema sofisticado que integra ingeniería de contexto, gestión inteligente de la memoria, manejo robusto de errores y estrategias de planificación dinámica para lograr una autonomía efectiva y escalable en la ejecución de tareas complejas. Su diseño se centra en la adaptabilidad y la resiliencia, permitiendo que el agente aprenda y mejore continuamente a partir de sus interacciones con el entorno y los resultados de sus acciones.

### Capacidades e Implementación
| Capacidad | Implementación | Parámetros/Límites | Comportamiento |
|---|---|---|---|
| **Ciclo de Razonamiento y Acción Iterativo** | Ejecución continua de un loop que alterna entre razonamiento y acción, monitoreado a través de eventos `status_update`. | N/A | Interpreta el objetivo del usuario, crea un plan, ejecuta tareas con herramientas, evalúa el progreso y decide la siguiente acción hasta completar el objetivo o alcanzar una condición de detención [1] [2] [5]. |
| **Planificación y Re-planificación Dinámica** | Interpretación del objetivo del usuario, creación de un plan inicial, y evaluación continua del progreso. | N/A | El agente adapta su plan en cada iteración basándose en las observaciones y el estado actual de la tarea [2]. |
| **Uso de Herramientas (Tool Use)** | Selección y ejecución de acciones de un espacio de acción predefinido. | Espacio de acción predefinido de herramientas internas y externas. | El modelo selecciona la herramienta más apropiada en cada iteración para interactuar con el entorno (sandbox, herramientas específicas, ejecución de código) [1]. |
| **Gestión de Contexto (Context Engineering)** | Optimización del KV-Cache, enmascaramiento de herramientas, uso del sistema de archivos como memoria externa. | Relación Input/Output de tokens 100:1; Prefijo de prompt estable; Contexto append-only; Puntos de interrupción de caché explícitos; Nombres de herramientas con prefijos consistentes. | Mejora la eficiencia, reduce la latencia y el costo de inferencia. Mantiene la estabilidad del loop del agente y evita la confusión del modelo al gestionar el espacio de acción [1]. |
| **Memoria Basada en Recuperación** | Almacenamiento de información (acciones previas, documentos, datos externos) como embeddings en bases de datos vectoriales (Milvus, Zilliz Cloud). | N/A | Permite una búsqueda semántica rápida y eficiente de contexto relevante, manteniendo los prompts concisos [2]. |
| **Manejo de Errores y Robustez** | Retención de errores y "malas decisiones" en el contexto; Implementación de `Loop Guard`; Recursión controlada; Metadatos de intención explícitos. | Profundidad máxima de recursión (ej. 4); `agent_id` en `recent_task_ids` y `depth_level` > 2 para `Loop Guard`. | El agente aprende de los fallos, reduce la repetición de errores, previene bucles infinitos y explosión de contexto, y mantiene el propósito de las subtareas [1] [3]. |
| **Manipulación de la Atención (Recitación)** | Creación y actualización de un archivo `todo.md` con objetivos pendientes. | N/A | Empuja el plan global al lapso de atención reciente del modelo, mitigando el problema de "perdido en el medio" y reduciendo la desalineación de objetivos [1]. |
| **Diversificación de Few-Shot Prompting** | Introducción de pequeñas variaciones estructuradas en acciones y observaciones. | N/A | Rompe patrones de imitación excesiva, evitando la deriva, sobregeneralización o alucinaciones del modelo [1]. |
| **Gestión de Estados del Agente** | Monitoreo del `agent_status` (`running`, `stopped`, `waiting`, `error`) a través de `task.listMessages`. | N/A | Permite al sistema o al usuario determinar la siguiente acción (continuar sondeando, leer resultados, manejar entrada, o revisar errores) [5]. |
| **Manejo de Confirmaciones de Usuario** | Respuesta a eventos `waiting` del agente. | `waiting_for_event_type` (`messageAskUser` vs. otros tipos); `confirm_input_schema` para validación de entrada. | Permite al usuario interactuar con el agente para responder preguntas (`task.sendMessage`) o confirmar/rechazar acciones específicas (`task.confirmAction`) [5]. |

### Limitaciones y Fallas
| Limitación | Severidad | Fuente | Workaround |
|---|---|---|---|
| **Explosión de Contexto (Context Overflow)** | Alta | [3] | Implementar límites de memoria con alcance (`Scoped Memory`), inyectando solo resúmenes relevantes para la tarea y evitando registros globales. Recortar instantáneas de memoria a un tamaño máximo (ej. ≤ 2000 tokens) usando sumarización clasificada por contenido. |
| **Bucle Infinito de Auto-delegación (Recursion Spiral)** | Alta | [3] | Implementar `Loop Guard` para detectar invocaciones recursivas (ej. si `agent_id` se repite en los últimos `recent_task_ids` y `depth_level` > 2). Establecer una profundidad máxima de recursión (ej. 4) y requerir revisión humana para profundidades mayores. |
| **Deriva Lateral y Desalineación de Objetivos** | Media | [3] | Incrustar "anclas de intención" (`Intention Anchors`) con metadatos explícitos en cada prompt de tarea (ej. `origin_goal`, `parent_task_id`, `intent_trace`, `depth_level`). |
| **Degradación del Rendimiento con Contextos Largos** | Media | [1] | Utilizar el sistema de archivos como memoria externa para almacenar observaciones grandes y datos históricos. Implementar estrategias de compresión restaurables (ej. guardar URL en lugar de contenido completo de página web). |
| **Costo Elevado de Entradas Largas** | Media | [1] | Optimización del KV-Cache mediante prefijos de prompt estables, contexto append-only y puntos de interrupción de caché explícitos. Uso del sistema de archivos como memoria externa. |
| **Invalidación del KV-Cache por Cambios en el Contexto** | Media | [1] | Mantener el prefijo del prompt estable. Evitar la adición o eliminación dinámica de herramientas a mitad de la iteración. Asegurar serialización determinista. |
| **Confusión del Modelo por Herramientas Eliminadas** | Media | [1] | Utilizar la estrategia de "enmascarar, no eliminar" herramientas mediante una máquina de estados consciente del contexto que enmascara los logits de los tokens. |
| **Few-Shot Prompting Contraproducente** | Baja | [1] | Introducir pequeñas cantidades de variación estructurada en acciones y observaciones para romper patrones de imitación excesiva y ajustar la atención del modelo. |

### Ejemplos de Uso Real
1.  **Propuesta de Marketing para Hilton:** Un gerente de marketing de Hilton utiliza Manus para crear una presentación de PowerPoint estructurada y creativa para una nueva propuesta de marketing, cubriendo análisis de mercado, objetivos, estrategias, plan de ejecución, resultados esperados, evaluación de riesgos y cronograma de implementación [4].
2.  **Diseño de Póster Publicitario:** Un diseñador de pósteres de IA visionario utiliza Manus para crear un anuncio lúdico y de alto contraste. Se le proporciona una imagen de producto y un nombre de marca, y Manus genera una escena de arte de garabatos de tinta negra que interactúa con la forma y función del producto, integrando la foto del producto y generando eslóganes ingeniosos [4].
3.  **Presentación sobre la Dinastía Tang:** Un usuario solicita a Manus que cree diapositivas que presenten la Dinastía Tang, con el estilo de un profesor universitario profesional [4].
4.  **Herramienta de Visualización de Política Fiscal:** Un usuario crea una herramienta de visualización de política fiscal [4].
5.  **Animación con p5js:** Un usuario crea una animación utilizando p5js [4].
6.  **Impacto de la IA Generativa en Asia:** Un usuario investiga el impacto económico de la IA generativa en las economías asiáticas, analizando la literatura académica, los mecanismos de transmisión clave y el impacto diferencial en trabajadores de baja y alta cualificación y experiencia en países del sudeste asiático, India y China. El resultado es un informe estructurado y un resumen ejecutivo [4].
7.  **Caja de Resonancia Programable en JavaScript:** Un usuario crea una caja de resonancia programable en JavaScript [4].
8.  **Diseño de Personajes Inspirados en el Zodíaco:** Un usuario crea 12 personajes inspirados en los signos del zodíaco, cada uno representando una personalidad MBTI diferente y un estilo cultural distinto, con un diseño de personaje de fantasía, retrato expresivo y fondo detallado [4].
9.  **Diseño de Vivienda de 2 Pisos en Laguna Beach:** Un usuario diseña una casa de 2 pisos con sótano en un lote específico en Laguna Beach, California, respetando las regulaciones de la asociación de propietarios [4].
10. **Juego Interactivo de Tetris Colorido:** Un usuario genera un juego interactivo y colorido de Tetris [4].
11. **Video Web con TensorFlow.js:** Un usuario solicita la creación de un video web de 19 minutos con TensorFlow.js [4].
12. **Galería 3D para Pinturas de Van Gogh:** Un usuario crea una galería 3D para pinturas de Van Gogh [4].
13. **Video Explicativo de Entrelazamiento Cuántico:** Un usuario solicita un video explicativo visual sobre el entrelazamiento cuántico [4].
14. **Generador de Recetas Basado en el Estado de Ánimo:** Un usuario crea un generador de recetas basado en el estado de ánimo [4].
15. **Ilustración de Concepto para Renovación de Cafetería:** Un usuario diseña una ilustración de concepto para la renovación de una cafetería en el estilo "Liquid Glasses" [4].
16. **Página Web de Enseñanza de Computación Cuántica:** Un usuario crea una página web de enseñanza de computación cuántica [4].
17. **Diapositivas de Consejos de Codificación en Python:** Un usuario genera diapositivas con consejos de codificación en Python [4].
18. **Dashboard para Objetivos LBO en Japón:** Un usuario crea un dashboard para objetivos de LBO en Japón [4].
19. **Variaciones de Estilo de Escena con Técnicas de Movimiento de Cámara:** Un usuario genera variaciones de estilo de la misma escena utilizando diferentes técnicas de movimiento de cámara [4].
20. **Curso de FastAPI:** Un usuario crea un curso de FastAPI [4].
21. **White Paper de Terapia CRISPR:** Una startup de biotecnología utiliza Manus para acelerar la síntesis de investigación, redacción y verificación de cumplimiento para un white paper de alto impacto sobre terapia génica basada en CRISPR [4].
22. **Sitio PMF de Agente de IA Exitoso:** Un usuario crea un sitio PMF (Product-Market Fit) exitoso para un agente de IA [4].
23. **Creación de Diapositivas a partir de Guía Ejecutiva:** Un usuario convierte una guía ejecutiva en diapositivas [4].
24. **Modelo BPMN para Escenarios de Presentación de Marcas:** Un usuario crea un modelo BPMN para escenarios de presentación de marcas [4].
25. **Video Cinematográfico de un Marinero Anciano Comiendo:** Un usuario genera un video cinematográfico de un marinero anciano comiendo espagueti, con instrucciones detalladas sobre la composición visual y el estilo [4].
26. **Aplicación de Sonido de Elementos Periódicos:** Un usuario crea una aplicación de sonido de elementos periódicos [4].
27. **Video "¿Qué Pasaría si los Dinosaurios Construyeran Ciudades?":** Un usuario solicita un video que muestre cómo serían las ciudades si los dinosaurios hubieran evolucionado con inteligencia similar a la humana [4].
28. **Sitio Interactivo de Exploración Espacial:** Un usuario crea un sitio interactivo de exploración espacial [4].
29. **Mazo de Anki a partir de Notas de Genética:** Un usuario crea un mazo de Anki a partir de sus notas de clase de genética y diapositivas de conferencias [4].
30. **Diseño de UI Moderno para VocalizeX:** Un usuario diseña una interfaz de usuario moderna para VocalizeX [4].
31. **Video de 15 Segundos sobre la Vida de Beethoven:** Un usuario crea un video de estilo flash de 15 segundos que resume la vida de Ludwig van Beethoven, con instrucciones detalladas sobre las escenas, el tono y el estilo visual [4].
32. **Sitio de Guía Social "Tangled":** Un usuario crea un sitio de guía social llamado "Tangled" [4].
33. **Presentación para Consultor de IA y Negocios:** Un consultor de IA y negocios utiliza Manus para crear una presentación de diapositivas de alta calidad sobre "Impulsando la Adopción Digital en Empresas: El Enfoque Impulsado por la IA", dirigida a ejecutivos de nivel C [4].


### Hallazgos de Fase 2 (Actualizado 1 Mayo 2026)

#### Nuevos Descubrimientos
La investigación ha revelado detalles cruciales sobre el funcionamiento interno del Agente de Manus AI, particularmente en áreas donde existían gaps de conocimiento. Se ha confirmado que el archivo `todo.md` no es solo una lista estática, sino un mecanismo dinámico y central para la **manipulación de la atención del modelo** [1] [4] [5]. Su formato es una lista de verificación en pseudocódigo que se reescribe constantemente para mantener los objetivos en la "zona de alta atención" del LLM [1] [3]. Este enfoque es una innovación clave para evitar la "deriva de objetivos" (`goal drift`) en secuencias agénticas largas. [4] [5]

En cuanto al **ciclo ReAct interno**, se ha detallado que Manus opera en un bucle iterativo `analizar → planificar → ejecutar → observar`, con una restricción explícita de una acción de herramienta por iteración. [6] Esto es fundamental para el control del flujo y la supervisión, previniendo operaciones no controladas. La fase de "análisis" no solo considera la solicitud del usuario, sino también un "flujo de eventos de interacciones recientes", lo que sugiere un mecanismo de memoria a corto plazo más sofisticado de lo que se conocía previamente. [6]

El manejo del problema del **"perdido en el medio" (`lost in the middle`)** se aborda de manera multifacética. Más allá de la compresión de contexto, Manus utiliza el **sistema de archivos como una memoria externa ilimitada y persistente** [1]. Esta es una estrategia novedosa que permite al agente aprender a escribir y leer archivos bajo demanda, mitigando las limitaciones de la ventana de contexto de los LLM. [1] Además, se implementan "límites de memoria con ámbito" y "metadatos de intención explícitos" para subagentes, lo que reduce la sobrecarga de contexto y previene la recursión inútil. [9]

La **diversificación del `few-shot prompting`** es otra área con hallazgos significativos. Manus introduce "variación estructurada" en los ejemplos `few-shot` mediante aleatoriedad controlada en la serialización, el fraseo y el formato. [10] [11] Esto es una contramedida directa al "bloqueo de patrón" que puede surgir de ejemplos idénticos, mejorando la flexibilidad y robustez del modelo. [10] [11]

Finalmente, la **gestión de estados del agente** se rige por una "máquina de estados consciente del contexto" que gestiona la disponibilidad de herramientas. [1] Aunque los estados `running/stopped/waiting/error` son comunes, los "triggers" específicos para las transiciones son más detallados. Se ha identificado la "retroalimentación ambigua" y la "detección de bucles" (mediante un `Loop Guard`) como triggers clave para el estado de error o la intervención, lo que indica un sistema de monitoreo y auto-depuración más activo. [9] [12] La persistencia del estado a través de un `Event Stream Context` es también un hallazgo importante. [13]

Estos hallazgos demuestran que Manus AI va más allá de la mera aplicación de LLMs, incorporando mecanismos de ingeniería de contexto, gestión de memoria y control de flujo altamente sofisticados para lograr su autonomía.

#### Detalles de Implementación
### Mecanismo del archivo `todo.md`
El archivo `todo.md` es un componente central en la gestión de la atención y la memoria del agente Manus AI. Su implementación se basa en un enfoque de memoria externa persistente a través del sistema de archivos del sandbox. El formato es una lista de verificación (`checklist`) en pseudocódigo o una lista enumerada de pasos del plan, que incluye descripciones y estados de las tareas. [3] [4] [5]

**Creación y Actualización:**
El `Planner Module` es el encargado de generar la jerarquía de tareas a partir de un objetivo raíz, creando esta lista inicial de pasos en `todo.md`. [1] [4] A medida que el agente ejecuta cada paso, el archivo `todo.md` se actualiza, marcando las tareas completadas. [2] [3] La actualización implica reescribir el archivo, lo que garantiza que la versión más reciente del plan esté siempre disponible. [1]

**Uso para Manipular la Atención:**
Manus manipula la atención del modelo recitando constantemente los objetivos del archivo `todo.md` al final del contexto del LLM. [1] [4] [5] Esto empuja el plan global a la zona de alta atención del LLM, evitando que el agente pierda de vista el objetivo general. [1] Este mecanismo es una forma de "recitación de tareas" que guía el enfoque del modelo. [4] [5]

### Ciclo ReAct Interno
El ciclo interno ReAct (Reasoning and Acting) de Manus AI sigue un patrón iterativo de `analizar → planificar → ejecutar → observar`. [4] [6] Este ciclo se repite hasta que la tarea se completa. [1] [6]

**Pasos entre Observación y Acción:**
1.  **Análisis del estado actual y solicitud del usuario:** El agente evalúa la información más reciente del `event stream` (flujo de eventos de interacciones recientes). [6]
2.  **Planificación/Selección de una acción:** Basándose en el contexto actual, el modelo decide qué herramienta u operación utilizar a continuación. [1] [6]
3.  **Ejecución:** La acción seleccionada se lleva a cabo en el entorno del sandbox (máquina virtual de Manus). [1] [6]
4.  **Observación:** El resultado de la ejecución se produce y se añade al `event stream`, formando la entrada para la siguiente iteración. [1] [6]

El diseño limita explícitamente al agente a una sola acción de herramienta por iteración, lo que significa que debe esperar el resultado de cada acción antes de decidir el siguiente paso. [6] Este flujo de control evita que el modelo ejecute una secuencia larga de operaciones sin supervisión y permite el monitoreo de cada paso. [6]

### Manejo del 'Perdido en el Medio' (Lost in the Middle)
Manus aborda el problema de la degradación del rendimiento de los LLM en contextos largos, conocido como "lost in the middle", mediante una combinación de estrategias de ingeniería de contexto y el uso del sistema de archivos como memoria externa. [1] [7] [8]

**Estrategias de Contexto:**
*   **Compresión y Truncamiento Restaurable:** Manus implementa estrategias de compresión y truncamiento que son reversibles. Por ejemplo, el contenido de una página web puede eliminarse del contexto siempre que se conserve la URL, y el contenido de un documento puede omitirse si su ruta permanece disponible en el sandbox. [1]
*   **Sistema de Archivos como Contexto:** El sistema de archivos se trata como la memoria definitiva de Manus: ilimitada en tamaño, persistente por naturaleza y directamente operable por el agente. [1] El modelo aprende a escribir y leer archivos bajo demanda, utilizando el sistema de archivos no solo como almacenamiento, sino como memoria estructurada y externalizada. [1]
*   **Límites de Memoria con Ámbito:** Para evitar la sobrecarga de contexto en agentes recursivos, Manus utiliza límites de memoria con ámbito. [9] Los subagentes heredan solo un resumen de la tarea principal e incluyen metadatos explícitos de "linaje de tareas". [9] Las instantáneas de memoria se recortan a un máximo de 2000 tokens mediante un resumen clasificado por contenido. [9]

### Diversificación de Few-Shot Prompting
Manus reconoce que el `few-shot prompting`, aunque potente, puede generar un "bloqueo de patrón" (`pattern lock`) si los ejemplos son demasiado idénticos, llevando a una rigidez y sobregeneralización del modelo. [10] [11] Para contrarrestar esto, Manus introduce una **variación estructurada** en sus ejemplos `few-shot`. [10] [11]

**Variaciones Introducidas:**
*   **Aleatoriedad Controlada:** Se introduce una pequeña cantidad de aleatoriedad controlada en las plantillas de serialización, el fraseo y el formato de los ejemplos. [10] [11] Esto evita que el modelo se fije en un patrón específico y fomenta una mayor flexibilidad en su razonamiento. [10]
*   **Diversidad de Fraseo:** Se varía la redacción en los ejemplos `few-shot` para evitar la repetición y promover una comprensión más robusta de la tarea. [10] [11]

El objetivo es mejorar la robustez del agente y su capacidad para manejar situaciones nuevas o ligeramente diferentes, evitando que el modelo se vuelva demasiado dependiente de los ejemplos exactos proporcionados. [10] [11]

### Gestión de Estados del Agente
La gestión de estados en Manus AI es crucial para su autonomía y persistencia. El agente transiciona entre diferentes estados (running, stopped, waiting, error) basándose en eventos y triggers específicos. [1] [12] [13]

**Estados y Transiciones:**
*   **Running (Ejecutándose):** El agente está activamente procesando tareas dentro de su ciclo `analizar → planificar → ejecutar → observar`. [6]
*   **Stopped (Detenido):** El agente entra en este estado cuando determina que la tarea ha sido completada y ha entregado el resultado final al usuario. [6]
*   **Waiting (Esperando):** Aunque no se detalla explícitamente un estado de "waiting" en los documentos, se infiere que el agente puede entrar en un estado de espera mientras aguarda la finalización de una acción de herramienta antes de proceder a la siguiente iteración del ciclo. [6]
*   **Error (Error):** Los errores pueden surgir de diversas fuentes, como bucles infinitos de auto-delegación, desbordamiento de contexto o fallos en la ejecución de herramientas. [9] [12] Manus implementa mecanismos de recuperación de errores, como la capacidad de auto-depuración y reintento de llamadas a la API, lo que sugiere una transición a un estado de error que puede llevar a un reintento o a una detención si el error persiste. [12]

**Triggers:**
*   **Finalización de Tarea:** El agente pasa a `stopped` cuando el `Planner Module` determina que todos los pasos del plan se han completado. [6]
*   **Retroalimentación Ambígua:** En escenarios de recursión, una retroalimentación ambigua puede hacer que el `Planner` se reinvoque a sí mismo, lo que puede llevar a un bucle. [9]
*   **Desbordamiento de Contexto:** El desbordamiento de contexto puede causar que el agente se detenga o genere resultados fragmentados. [9] [12]
*   **Detección de Bucle:** Un `Loop Guard` ligero puede detectar invocaciones auto-recursivas y lanzar un `LoopDetectedError`, lo que probablemente detendría al agente o lo pondría en un estado de error para revisión. [9]
*   **Fallos de Herramientas/API:** Los fallos en la ejecución de herramientas o llamadas a la API pueden activar mecanismos de reintento o llevar a un estado de error. [12]

La gestión de estados se apoya en un `Event Stream Context` y una `máquina de estados consciente del contexto` para gestionar la disponibilidad de herramientas y las transiciones. [1] [13]

#### Comportamientos Observados en Producción
1.  **Bucle de auto-delegación y sobrecarga de memoria:** Los agentes de Manus pueden entrar en bucles infinitos de auto-delegación, donde el `Planner` se reinvoca a sí mismo basándose en retroalimentación ambigua, lo que lleva a una explosión del contexto de tokens y a la emisión de pensamientos fragmentados. [9]
2.  **Desbordamiento de contexto:** La memoria heredada por los subagentes puede exceder los límites de tokens a medida que la recursión se profundiza, resultando en un historial fragmentado y confusión para el agente. [9]
3.  **Alucinaciones y referencias de memoria erráticas:** Los agentes pueden "alucinar" conexiones entre subtareas no relacionadas y mostrar referencias de memoria erráticas en los logs. [9]
4.  **Repetición de subtareas:** La aparición de frases idénticas con diferentes IDs de agente es un signo de un bucle roto. [9]
5.  **Llamadas recursivas del `Planner`:** Las trazas de pila que incluyen el mismo agente repetidamente indican un bucle de auto-invocación. [9]
6.  **Degradación del rendimiento en contextos largos:** A pesar de las grandes ventanas de contexto de los LLM modernos, el rendimiento del modelo tiende a degradarse más allá de cierta longitud de contexto, incluso antes de alcanzar el límite técnico. [1] [7] [8]
7.  **Costo elevado de entradas largas:** Incluso con el almacenamiento en caché de prefijos, las entradas largas son costosas debido a la transmisión y el prellenado de cada token. [1]
8.  **"Pattern lock" en `few-shot prompting`:** El uso de ejemplos idénticos en `few-shot prompting` puede llevar a una rigidez y sobregeneralización del modelo, haciendo que el agente sea menos flexible. [10] [11]
9.  **Problemas de comunicación de gateway:** Se han reportado problemas frecuentes de comunicación de gateway que pueden causar la pérdida de archivos. [12]

#### Fuentes Adicionales
1.  [https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus](Context Engineering for AI Agents: Lessons from Building Manus)
2.  [https://medium.com/@jalajagr/inside-manus-the-anatomy-of-an-autonomous-ai-agent-b3042e5e5084](Inside Manus: The Anatomy of an Autonomous AI Agent)
3.  [https://firsthubai.com/how-manus-ai-works/](How Manus AI Works in 2025 – Step-by-Step Guide)
4.  [https://gist.github.com/renschni/4fbc70b31bad8dd57f3370239dccd58f](In-depth technical investigation into the Manus AI agent, focusing on its architecture, tool orchestration, and autonomous capabilities. · GitHub)
5.  [https://www.linkedin.com/pulse/how-top-ai-companies-handle-context-engineering-himanshu-sangshetti-qddof](How Top AI Companies Handle Context Engineering)
6.  [https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus](Context Engineering for AI Agents: Lessons from Building Manus)
7.  [https://manus.im/blog/manus-wide-research-solve-context-problem](Wide Research: Beyond the Context Window)
8.  [https://github.com/langchain4j/langchain4j/discussions/4338](Proposal for Context Compaction Strategy to prevent Pre-rot threshold in LLMs · Discussion #4338 · langchain4j/langchain4j)
9.  [https://medium.com/@connect.hashblock/debugging-ai-autonomy-what-i-learned-from-a-failing-manus-agent-loop-408e8c0a5e5a](Debugging AI Autonomy: What I Learned From a Failing Manus Agent Loop | by Hash Block)
10. [https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus](Context Engineering for AI Agents: Lessons from Building Manus)
11. [https://dev.to/contextspace_/context-engineering-for-ai-agents-key-lessons-from-manus-3f83](Context Engineering for AI Agents: Key Lessons from Manus)
12. [https://medium.com/@connect.hashblock/how-i-tuned-manus-agents-to-self-debug-and-retry-api-failures-autonomously-0c385893aae9](How I Tuned Manus Agents to Self-Debug and Retry API Failures Autonomously | by Hash Block)
13. [https://medium.com/@jalajagr/inside-manus-the-anatomy-of-an-autonomous-ai-agent-b3042e5e5084](Inside Manus: The Anatomy of an Autonomous AI Agent | by Jalaj Agrawal)

## M02 — Sistema de Tools y Herramientas de Manus AI

### Descripción Técnica
# M02 — Sistema de Tools y Herramientas de Manus AI

El módulo de Sistema de Tools y Herramientas de Manus AI representa un pilar fundamental en su capacidad para operar como un agente autónomo. A diferencia de los sistemas tradicionales que dependen de llamadas a funciones predefinidas y rígidas, Manus ha adoptado una arquitectura innovadora conocida como **CodeAct**, que le permite generar y ejecutar código Python dinámicamente para interactuar con su entorno digital. Esta sección detalla la implementación técnica de este módulo, sus componentes clave, el proceso de selección de herramientas y la evolución desde las llamadas a herramientas convencionales hacia un enfoque de código ejecutable.

## Arquitectura CodeAct: El Corazón del Sistema de Acciones

La innovación central en el sistema de herramientas de Manus es la adopción de la arquitectura CodeAct [1] [3] [4]. Esta aproximación se basa en la premisa de que un agente de IA puede interactuar con su entorno de manera más flexible y potente al escribir y ejecutar código, principalmente Python, en lugar de invocar herramientas a través de estructuras JSON o comandos de texto fijos. La investigación detrás de CodeAct demostró que los agentes capaces de producir código para sus acciones logran tasas de éxito significativamente más altas en tareas complejas que aquellos limitados a llamadas de herramientas textuales simples [5].

En el modelo CodeAct, las acciones del modelo son scripts Python que se ejecutan en un entorno controlado. Esto proporciona una flexibilidad inigualable, ya que el código puede combinar múltiples herramientas y lógicas en una sola operación, manejar flujos condicionales, iterar sobre resultados y utilizar la vasta cantidad de librerías disponibles en el ecosistema de Python [3]. Por ejemplo, si Manus necesita obtener información meteorológica, podría generar código Python que llama a un cliente de API meteorológica e imprime el resultado, en lugar de depender de una función "Weather" predefinida [5]. El entorno sandbox ejecuta este código y devuelve la salida (o el error) como una observación al agente.

## Entorno Sandbox y Ejecución de Comandos

Manus opera dentro de un **entorno de computación virtual** basado en la nube, que es un espacio de trabajo completo de Ubuntu Linux con acceso a Internet [3]. Este sandbox permite a Manus utilizar un conjunto de herramientas y software como si fuera un usuario humano avanzado. Las especificaciones del sistema indican que Manus tiene acceso a [3]:

*   **Shell (con privilegios sudo):** Para ejecutar comandos de línea, gestionar procesos y automatizar tareas del sistema.
*   **Navegador web controlado:** Para navegar por sitios web, extraer datos, interactuar con elementos web e incluso ejecutar JavaScript dentro de una consola del navegador.
*   **Sistema de archivos:** Para leer, escribir y organizar archivos, lo que es crucial para flujos de trabajo basados en documentos.
*   **Intérpretes de lenguajes de programación:** Como Python y Node.js, para la ejecución de código.
*   **Capacidades de despliegue:** Manus puede desplegar aplicaciones, incluyendo la configuración de sitios web y servicios de alojamiento en URLs públicas.

Este entorno sandboxed es fundamental porque permite a Manus **actuar** en el mundo digital, no solo responder en lenguaje natural. La ejecución se realiza del lado del servidor, lo que significa que Manus puede continuar trabajando incluso si el dispositivo del usuario está apagado, a diferencia de los agentes que se ejecutan en el navegador del usuario [3].

## Bucle del Agente y Orquestación

La autonomía de Manus se estructura a través de un **bucle de agente iterativo** [3]. Cada ciclo del bucle comprende las siguientes fases:

1.  **Análisis:** Comprende el estado actual y la solicitud del usuario (a partir de un flujo de eventos de interacciones recientes).
2.  **Planificación/Selección de acción:** Decide qué herramienta u operación utilizar a continuación.
3.  **Ejecución:** Realiza la acción seleccionada en el entorno sandbox.
4.  **Observación:** El resultado de la acción se añade al flujo de eventos.

Este bucle se repite hasta que Manus determina que la tarea está completa, momento en el que envía el resultado final al usuario y entra en un estado inactivo [3]. El diseño limita explícitamente al agente a una acción de herramienta por iteración, lo que significa que debe esperar el resultado de cada acción antes de decidir el siguiente paso. Este flujo de control evita que el modelo ejecute una secuencia larga de operaciones sin supervisión y permite que el sistema (y el usuario) supervisen cada paso [3].

## Módulos de Planificación, Conocimiento y Datos

Para gestionar tareas complejas, Manus incorpora varios módulos especializados:

*   **Módulo de Planificación (Descomposición de Tareas):** Descompone objetivos de alto nivel en una lista ordenada de pasos [3]. Cuando se le asigna un objetivo, el Planificador genera un plan en pseudocódigo o una lista enumerada (con números de paso, descripciones y estado) que se inyecta en el contexto del agente como un evento "Plan" especial. Este plan puede actualizarse sobre la marcha si la tarea cambia, sirviendo como una hoja de ruta para el agente [3].
*   **Módulo de Conocimiento:** Proporciona información de referencia relevante o directrices de mejores prácticas de una base de conocimiento cuando es necesario [3]. Estos aparecen como eventos "Knowledge" en el contexto, proporcionando al agente información útil específica del dominio o la tarea.
*   **Módulo de Datos (Datasource):** Permite a Manus utilizar datos fácticos a través de APIs pre-aprobadas (para clima, finanzas, etc.) [3]. Cuando son relevantes, el agente las llama a través de código Python, priorizando las fuentes de datos autorizadas sobre la información web general. Este enfoque integra la Generación Aumentada por Recuperación (RAG), combinando la recuperación de datos externos con las capacidades de generación del modelo [3].

## Colaboración Multi-Agente

Manus presenta una arquitectura **multi-agente** (multi-módulo) donde sub-agentes o componentes especializados trabajan en paralelo en diferentes aspectos de una tarea [3]. Por ejemplo, un sub-agente podría centrarse en la navegación web y la recopilación de información, mientras que otro maneja la codificación y otro la gestión de datos, cada uno dentro de su propio entorno sandbox aislado [3]. Un orquestador de alto nivel coordina estas tareas, dividiendo el trabajo e integrando los resultados. Este diseño permite a Manus abordar proyectos complejos y multifacéticos de manera más eficiente y robusta, entregando resultados tangibles como informes Excel formateados o incluso sitios web desplegados [3]. La complejidad de esta coordinación multi-agente se oculta al usuario, que percibe a Manus como un único asistente de IA que gestiona todo el proyecto sin problemas.

## Transición de Tool Calls Tradicionales a Código Ejecutable

La principal diferencia entre el sistema de herramientas de Manus y los enfoques tradicionales de "tool calling" radica en la flexibilidad y el poder del código ejecutable. Mientras que las tool calls tradicionales a menudo se limitan a un conjunto fijo de funciones invocadas a través de JSON estructurado o comandos de texto simples, el enfoque CodeAct de Manus permite al agente escribir y ejecutar código Python arbitrario [1] [3]. Esto supera las limitaciones de las herramientas predefinidas, permitiendo a los agentes combinar herramientas y lógica, mantener el estado, procesar múltiples entradas y aprovechar el vasto ecosistema de Python para resolver una gama ilimitada de problemas [4]. Esta capacidad de "mini-programación dinámica" es lo que distingue a Manus de otros agentes y le permite abordar tareas complejas con mayor eficiencia y éxito [1].

En resumen, el sistema de Tools y Herramientas de Manus AI, impulsado por la arquitectura CodeAct y un robusto entorno sandbox, transforma a los agentes de IA de meros respondedores a ejecutores autónomos. La capacidad de generar y ejecutar código Python, combinada con una orquestación multi-agente y módulos especializados, permite a Manus abordar tareas complejas con una flexibilidad y eficiencia sin precedentes, marcando un avance significativo en la autonomía de la IA.

### Capacidades e Implementación
| Capacidad | Implementación | Parámetros/Límites | Comportamiento |
|---|---|---|---|
| **Generación y Ejecución de Código (CodeAct)** | El agente genera scripts Python dinámicamente para realizar acciones. | Acceso a un intérprete Python completo y a un vasto ecosistema de librerías. | Permite combinar múltiples herramientas y lógicas, manejar flujos condicionales e iterar sobre resultados. Supera las limitaciones de las tool calls tradicionales. [1] [3] [4] |
| **Entorno Sandbox Linux** | Un entorno de computación virtual basado en Ubuntu Linux con acceso a Internet. | Acceso a shell (con sudo), navegador web controlado, sistema de archivos, intérpretes (Python, Node.js). | Proporciona un espacio seguro y aislado para la ejecución de comandos y scripts, permitiendo a Manus "actuar" en el mundo digital. [3] |
| **Control de Navegador Web** | El agente puede navegar, extraer datos, interactuar con elementos web y ejecutar JavaScript. | Interacción programática con elementos web, llenado de formularios, scraping de datos. | Permite la automatización web completa, como la interacción con aplicaciones web y la extracción de información. [3] |
| **Ejecución de Comandos de Shell** | Capacidad para ejecutar comandos de línea y gestionar procesos del sistema. | Acceso a comandos de shell estándar de Linux, incluyendo privilegios sudo. | Permite la automatización de tareas del sistema, instalación de software y manipulación de archivos. [3] |
| **Gestión del Sistema de Archivos** | El agente puede leer, escribir y organizar archivos. | Operaciones CRUD (Crear, Leer, Actualizar, Eliminar) en el sistema de archivos del sandbox. | Fundamental para flujos de trabajo basados en documentos y para el almacenamiento de memoria persistente. [3] |
| **Capacidades de Despliegue** | El agente puede desplegar aplicaciones y servicios web. | Configuración de sitios web y alojamiento en URLs públicas. | Permite a Manus entregar resultados tangibles como sitios web o dashboards desplegados. [3] |
| **Bucle de Agente Iterativo** | Proceso estructurado de análisis, planificación, ejecución y observación. | Una acción de herramienta por iteración; espera el resultado antes de la siguiente acción. | Asegura una autonomía controlada y permite la supervisión de cada paso, evitando secuencias de operaciones sin control. [3] |
| **Módulo de Planificación** | Descompone objetivos de alto nivel en una lista ordenada de pasos (pseudocódigo). | Genera planes que se inyectan como eventos "Plan" en el contexto del agente. | Proporciona una hoja de ruta para el agente, permitiendo la descomposición de tareas complejas y la toma de decisiones estructurada. [3] |
| **Módulo de Conocimiento** | Proporciona información de referencia y directrices de mejores prácticas. | Inyecta eventos "Knowledge" en el contexto del agente. | Mejora la capacidad del agente para tomar decisiones informadas y seguir las mejores prácticas en tareas específicas. [3] |
| **Módulo de Datos (Datasource)** | Acceso a datos fácticos a través de APIs pre-aprobadas. | Llamadas a APIs (clima, finanzas, etc.) a través de código Python. | Integra la Generación Aumentada por Recuperación (RAG), priorizando fuentes de datos autorizadas sobre la información web general. [3] |
| **Colaboración Multi-Agente** | Arquitectura con sub-agentes especializados que trabajan en paralelo. | Orquestación de sub-agentes para tareas como navegación web, codificación, análisis de datos. | Permite abordar proyectos complejos de manera más eficiente y robusta, entregando resultados multifacéticos. [3] |

### Limitaciones y Fallas
| Limitación | Severidad | Fuente | Workaround |
|---|---|---|---|
| **Errores de bucle e inconsistencias** | Moderada a Alta | Usuarios reportan que Manus entra en bucles o se atasca en ciclos repetitivos, especialmente con tareas poco definidas. [2] | Mejorar la definición de las tareas y la ingeniería de prompts para guiar al agente de manera más precisa. Implementar mecanismos de detección de bucles y puntos de control en el plan del agente. |
| **Dependencia excesiva de modelos existentes** | Moderada | Manus integra fuertemente Claude Sonnet y Qwen finetunes, lo que genera dudas sobre si realmente innova o solo orquesta tecnologías existentes. [2] | No es una limitación funcional directa, pero podría afectar la percepción de innovación y la capacidad de diferenciación a largo plazo. |
| **Riesgos de seguridad y privacidad** | Moderada a Alta | La capacidad de Manus para ejecutar comandos, recuperar archivos e interactuar con sistemas externos plantea preocupaciones de seguridad si no está correctamente aislado. [2] | El entorno sandbox aísla las sesiones, pero la supervisión continua y la mejora de los controles de seguridad son cruciales. Restricciones explícitas para evitar la creación de cuentas de usuario o el bypass de seguridad sin permisos. [2] |
| **Limitaciones en la cantidad de datos procesados** | Moderada | Manus tiene limitaciones en la cantidad de datos que puede procesar a la vez debido a su ventana de contexto limitada. [2] | Optimización de la gestión del contexto, resumen de información relevante y procesamiento de datos por lotes. |
| **Rendimiento en tareas complejas** | Moderada | Aunque supera a otros modelos, los puntajes de Manus disminuyen en tareas de mayor dificultad (Nivel 3 del benchmark GAIA), indicando que aún lucha con el razonamiento complejo de múltiples pasos. [2] | Mejora continua de los modelos subyacentes, refinamiento de la lógica de planificación y orquestación multi-agente. |
| **Diferencia entre rendimiento en pruebas y mundo real** | Moderada | El rendimiento en el mundo real puede diferir de las pruebas controladas, dependiendo de cómo maneje tareas impredecibles. [2] | Monitoreo y adaptación continuos en entornos de producción, recopilación de feedback de usuarios para identificar y resolver problemas. |

### Ejemplos de Uso Real
## Ejemplos de Uso Real Documentados por la Comunidad

1.  **Análisis de Datos de Cafetería:** Manus AI fue utilizado para analizar datos de ventas de una cafetería a partir de un archivo CSV. Se le pidió identificar productos más vendidos, analizar el impacto de cambiar el horario de apertura y las tendencias de ventas por día y mes. Manus generó un informe de ventas detallado con gráficos y tablas. [2]
    *   **Herramientas utilizadas:** Procesamiento de archivos CSV, análisis de datos, generación de gráficos y tablas, posiblemente ejecución de scripts Python para análisis estadístico. [2]
    *   **Comportamiento observado:** Generó un informe con buena presentación, pero se identificaron errores en el procesamiento de datos de tiempo, lo que llevó a resultados incorrectos en el análisis de horarios. [2]

2.  **Predicciones del S&P 500:** Manus AI se empleó para analizar la recesión actual en el S&P 500, considerando los aranceles globales y datos históricos. Se le pidió identificar escenarios potenciales de caída y estimar un cronograma de recuperación. [2]
    *   **Herramientas utilizadas:** Acceso a API (YahooFinance API para datos del S&P 500), investigación web (Reuters, BBC para políticas arancelarias), escritura de scripts Python para extracción de datos, simulación Monte Carlo, modelado estadístico, despliegue de sitios web para presentar resultados. [2]
    *   **Comportamiento observado:** Recopiló datos actualizados, investigó eventos históricos de aranceles, creó scripts Python para escenarios y simulaciones, y desplegó un sitio web con los resultados, incluyendo gráficos interactivos y conclusiones. [2]

3.  **Recomendación de Productos (Deshumidificador):** Se le solicitó a Manus AI investigar y recomendar deshumidificadores para una habitación de 25 metros cuadrados en Portugal, considerando disponibilidad, características y reseñas. [2]
    *   **Herramientas utilizadas:** Investigación web (minoristas locales, organizaciones de reseñas de clientes, foros, Reddit), análisis de especificaciones técnicas, procesamiento de información climática. [2]
    *   **Comportamiento observado:** Construyó recomendaciones basándose en datos de minoristas locales, reseñas de clientes, foros y recursos técnicos, lo que sugiere un uso extensivo de las capacidades de navegación web y procesamiento de lenguaje natural. [2]

4.  **Búsqueda de Empleo:** Manus AI fue utilizado para buscar ofertas de empleo para un ingeniero full-stack, filtrando por título, salario, entorno de trabajo y pila tecnológica, con un interés adicional en la computación cuántica. [2]
    *   **Herramientas utilizadas:** Búsqueda web avanzada, procesamiento de lenguaje natural para entender criterios de búsqueda, posiblemente interacción con plataformas de empleo. [2]
    *   **Comportamiento observado:** Se espera que utilice sus capacidades de navegación web para buscar y filtrar ofertas de empleo, y luego presentar una lista de resultados con enlaces directos. [2]

5.  **Aprendizaje de una Nueva Habilidad (Astrofotografía):** Se le pidió a Manus AI crear un plan de aprendizaje para astrofotografía, incluyendo recursos, herramientas y un cronograma. [2]
    *   **Herramientas utilizadas:** Investigación web (cursos, tutoriales, equipos), planificación de tareas, organización de información. [2]
    *   **Comportamiento observado:** Generó un plan de aprendizaje estructurado, lo que demuestra su capacidad para recopilar y organizar información de diversas fuentes web. [2]


### Hallazgos de Fase 2 (Actualizado 1 Mayo 2026)

#### Nuevos Descubrimientos
La investigación del Módulo M02 de Manus AI ha revelado detalles técnicos significativos que cierran los gaps de conocimiento identificados, especialmente en lo que respecta a las firmas de las herramientas, el mecanismo de selección del LLM, el manejo de fallos y el proceso de registro de nuevas herramientas. A continuación, se presentan los hallazgos nuevos y los detalles de implementación.

**1. Firmas Exactas y Parámetros de las Tools Internas de Manus:**

Contrario a la expectativa de encontrar una documentación formal y centralizada de todas las herramientas internas, la información más detallada sobre las firmas y parámetros se obtuvo de un archivo `tools.json` [1] disponible en un GitHub Gist. Este archivo actúa como una especificación declarativa de las capacidades del agente, revelando que las herramientas de Manus AI se definen como funciones con nombres, descripciones y esquemas de parámetros bien estructurados. Este hallazgo es crucial porque demuestra que Manus utiliza un enfoque de **function calling basado en esquemas JSON** para sus herramientas internas, en lugar de un sistema ad-hoc o puramente basado en prompts.

Las herramientas se agrupan lógicamente por su funcionalidad (mensajería, sistema de archivos, shell, navegador, búsqueda, despliegue, páginas Manus y estado inactivo). Cada herramienta tiene una `description` que guía al LLM sobre su propósito y un objeto `parameters` que especifica los argumentos esperados. Los parámetros incluyen `type` (string, integer, boolean, object, array), `description` (para cada parámetro), y una lista `required` de los parámetros obligatorios. Algunas herramientas, como `message_ask_user`, incluyen un parámetro `suggest_user_takeover` con un `enum` (`none`, `browser`), lo que indica una capacidad intrínseca del sistema para sugerir la intervención humana en el navegador cuando sea necesario. Las herramientas de archivo (`file_read`, `file_write`, `file_str_replace`, `file_find_in_content`, `file_find_by_name`) y shell (`shell_exec`, `shell_view`, `shell_wait`, `shell_write_to_process`, `shell_kill_process`) tienen parámetros como `sudo` (boolean, opcional) y `exec_dir` (string, requerido para `shell_exec`), lo que subraya la capacidad del agente para interactuar con el sistema operativo con diferentes niveles de privilegio y en directorios específicos. Las herramientas de navegador (`browser_navigate`, `browser_click`, `browser_input`, etc.) aceptan `index` (integer) o `coordinate_x`/`coordinate_y` (number) para la interacción con elementos de la UI, y `text` (string) junto con `press_enter` (boolean) para la entrada de texto, lo que confirma un control granular sobre la interfaz web.

**2. Cómo Decide el LLM Qué Tool Usar:**

El LLM de Manus AI no emplea un "router de tools" explícito en el sentido de un componente de software separado que enruta las llamadas. Tampoco se basa en la generación de código Python arbitrario (CodeAct) para cada acción. En cambio, la decisión se basa en una combinación de **function calling nativo** y **selectores semánticos** [3].

*   **Function Calling Nativo:** El LLM recibe el prompt del usuario y el contexto actual, y su tarea es generar una llamada a una de las funciones predefinidas (las herramientas descritas en `tools.json`) con los parámetros adecuados. Este proceso es intrínseco a la capacidad del LLM de interpretar la intención y mapearla a las funciones disponibles. La existencia de esquemas de parámetros detallados facilita esta "traducción" de la intención a una llamada a función estructurada.

*   **Selectores Semánticos:** Manus utiliza "selectores" (ej. `SemanticSelector`) que evalúan las descripciones de las herramientas frente al prompt y el contexto para determinar la herramienta más relevante [3]. Esto es un paso más allá del function calling básico, ya que implica una comprensión semántica profunda para elegir la herramienta óptima, incluso cuando hay múltiples opciones que podrían parecer superficialmente relevantes. Este mecanismo permite que el agente "auto-seleccione" herramientas de forma dinámica, adaptándose al contexto de la tarea.

*   **Máquina de Estados Consciente del Contexto:** Para refinar aún más la selección, Manus utiliza una máquina de estados consciente del contexto que gestiona la disponibilidad de herramientas [2]. Esto significa que el sistema puede "enmascarar" o "forzar" la selección de ciertas herramientas en función del estado actual del flujo de trabajo, evitando llamadas a herramientas irrelevantes y mejorando la eficiencia y fiabilidad. Este enfoque es fundamental para la orquestación de flujos de trabajo complejos y multi-paso.

**3. Comportamiento de las Tools Cuando Fallan:**

Manus AI implementa un robusto sistema de **auto-depuración y reintentos inteligentes** para manejar los fallos de las herramientas [4]. Este es un hallazgo significativo, ya que va más allá de la simple captura de errores y demuestra una capacidad de resiliencia avanzada:

*   **Detección de Firmas de Fallo:** El sistema está instrumentado con lógica de reintento condicional que se activa ante firmas de fallo específicas (ej. payload vacío, códigos de estado HTTP inesperados como 502, timeouts, esquemas de respuesta inconsistentes, formatos inválidos) [4].
*   **Conciencia de Intentos Pasados:** El agente utiliza la memoria de estado interna de Manus para ser consciente de sus intentos anteriores. Esto permite una lógica de reintento no ciega, donde las decisiones se basan en el historial de fallos (ej. "Si `last_response.status == 502` Y `retry_count < 3`, entonces reintentar después de ajustar el timeout") [4].
*   **Mutación de Prompts en Reintentos:** Para evitar fallos repetidos, el agente puede modificar ligeramente sus solicitudes en los reintentos. Esto incluye reformular el prompt, solicitar un formato de salida diferente (ej. JSON en lugar de Markdown) o añadir instrucciones de fallback [4]. Este mecanismo reduce la tasa de fallos al hacer que las solicitudes sean más robustas.
*   **Modo de Depuración Interno:** Si todos los reintentos fallan, el agente entra en un "modo de depuración" donde reflexiona sobre el error utilizando la herramienta `reflect()` de Manus y mensajes del sistema. Se pregunta qué salió mal y si debería recurrir a un flujo simplificado o en caché [4].
*   **Rutas de Fallback:** Basado en la auto-depuración, el agente puede elegir una función de fallback, una cadena de herramientas simplificada o un reintento retrasado con una estrategia alterada [4].
*   **Códigos de Error Estructurados:** La API de Manus devuelve respuestas estructuradas con un campo `"ok": false` y un objeto `error` que contiene un `code` (ej. `invalid_argument`, `not_found`, `permission_denied`, `rate_limited`) y un `message` [8]. Esto facilita el manejo programático de errores.

**4. Límites de las Tools:**

*   **Tamaño Máximo de Output:** No se encontró un límite explícito de tamaño de output por herramienta en la documentación o `tools.json`. Sin embargo, se infiere que el tamaño está inherentemente limitado por la ventana de contexto del LLM. Outputs excesivamente grandes podrían ser truncados o afectar negativamente el rendimiento del LLM.
*   **Timeouts:** Los timeouts son gestionados a nivel de sistema y orquestación del agente, con la capacidad de ajuste dinámico durante los reintentos [4]. Aunque no hay un parámetro de timeout configurable por herramienta en `tools.json`, la presencia de errores de timeout en la API de Manus sugiere que existen límites de tiempo de ejecución.
*   **Rate Limits:** La API de Manus implementa límites de tasa, indicados por el código de error `rate_limited` [8]. Esto requiere que los agentes implementen estrategias de backoff para evitar ser bloqueados. La documentación de la API menciona una sección de "Rate Limits", lo que implica políticas definidas.
*   **Una Acción por Iteración:** Un límite de diseño fundamental es que el agente está explícitamente limitado a **una acción de herramienta por iteración** [6]. Esto significa que debe esperar el resultado de cada acción antes de decidir el siguiente paso. Esta restricción, aunque limita la concurrencia, fomenta un razonamiento secuencial y deliberado, lo que es crucial para la estabilidad y depurabilidad de los agentes autónomos.

**5. Cómo se Registran Nuevas Tools en el Sistema:**

El registro de nuevas herramientas en Manus AI se realiza mediante la **definición declarativa de objetos `Tool`** y su integración a través de **selectores semánticos** [3].

*   **Objetos `Tool`:** Una nueva herramienta se define como un objeto `Tool` que envuelve una función callable de Python. Este objeto requiere un `name`, una `description` (crucial para la selección del LLM) y un esquema `parameters` que describe los argumentos de entrada [3].
*   **Selectores:** Una vez definida, la herramienta se añade a un `SemanticSelector` junto con otras herramientas. El selector utiliza el LLM para interpretar el prompt del usuario y seleccionar la herramienta más adecuada basándose en su descripción y el contexto [3].
*   **Agent Skills y MCP Connectors:** Manus también soporta un estándar abierto de "Agent Skills" para flujos de trabajo personalizados [9]. Aunque los detalles son escasos, se sugiere que los Skills empaquetan herramientas con contexto y conocimiento procedimental. Además, los "Custom MCP Servers" y "MCP Connectors" [10] permiten la integración de herramientas a través de un protocolo de contexto de modelo, facilitando la conexión con sistemas propietarios.

En síntesis, Manus AI ha desarrollado un ecosistema de herramientas sofisticado que combina la flexibilidad del function calling nativo con mecanismos avanzados de selección semántica, manejo de contexto y resiliencia ante fallos. La clave de su extensibilidad reside en la definición declarativa de herramientas y su integración inteligente en el ciclo de razonamiento del LLM.


#### Detalles de Implementación
### Firmas y Parámetros de las Herramientas Internas de Manus AI

Las herramientas internas de Manus AI, tal como se desprenden del archivo `tools.json` [1], están diseñadas como funciones con descripciones claras y esquemas de parámetros definidos. A continuación, se detallan las firmas y parámetros de las herramientas clave:

**1. Herramientas de Mensajería:**

*   `message_notify_user`:
    *   **Descripción:** Envía un mensaje al usuario sin requerir una respuesta. Utilizado para acusar recibo, actualizar el progreso o explicar cambios en el enfoque.
    *   **Parámetros:**
        *   `text` (string, **requerido**): El mensaje de texto a mostrar al usuario.
        *   `attachments` (string o array de strings, opcional): Lista de adjuntos (rutas de archivo o URLs) a mostrar al usuario.

*   `message_ask_user`:
    *   **Descripción:** Hace una pregunta al usuario y espera una respuesta. Utilizado para solicitar aclaraciones, confirmación o información adicional.
    *   **Parámetros:**
        *   `text` (string, **requerido**): La pregunta de texto a presentar al usuario.
        *   `attachments` (string o array de strings, opcional): Lista de adjuntos relacionados con la pregunta o materiales de referencia.
        *   `suggest_user_takeover` (string, opcional, enum: ["none", "browser"]): Operación sugerida para la toma de control por parte del usuario.

**2. Herramientas de Sistema de Archivos:**

*   `file_read`:
    *   **Descripción:** Lee el contenido de un archivo. Utilizado para verificar contenidos, analizar logs o leer archivos de configuración.
    *   **Parámetros:**
        *   `file` (string, **requerido**): Ruta absoluta del archivo a leer.
        *   `start_line` (integer, opcional): Línea inicial para la lectura (basada en 0).
        *   `end_line` (integer, opcional): Número de línea final (exclusivo).
        *   `sudo` (boolean, opcional): Si se deben usar privilegios de sudo.

*   `file_write`:
    *   **Descripción:** Sobrescribe o añade contenido a un archivo. Utilizado para crear nuevos archivos, añadir contenido o modificar existentes.
    *   **Parámetros:**
        *   `file` (string, **requerido**): Ruta absoluta del archivo a escribir.
        *   `content` (string, **requerido**): Contenido de texto a escribir.
        *   `append` (boolean, opcional): Si se usa el modo de añadir.
        *   `leading_newline` (boolean, opcional): Si se añade un salto de línea inicial.
        *   `trailing_newline` (boolean, opcional): Si se añade un salto de línea final.
        *   `sudo` (boolean, opcional): Si se deben usar privilegios de sudo.

*   `file_str_replace`:
    *   **Descripción:** Reemplaza una cadena específica en un archivo. Utilizado para actualizar contenido o corregir errores en código.
    *   **Parámetros:**
        *   `file` (string, **requerido**): Ruta absoluta del archivo.
        *   `old_str` (string, **requerido**): Cadena original a reemplazar.
        *   `new_str` (string, **requerido**): Nueva cadena de reemplazo.
        *   `sudo` (boolean, opcional): Si se deben usar privilegios de sudo.

*   `file_find_in_content`:
    *   **Descripción:** Busca texto coincidente dentro del contenido de un archivo.
    *   **Parámetros:**
        *   `file` (string, **requerido**): Ruta absoluta del archivo.
        *   `regex` (string, **requerido**): Patrón de expresión regular.
        *   `sudo` (boolean, opcional): Si se deben usar privilegios de sudo.

*   `file_find_by_name`:
    *   **Descripción:** Encuentra archivos por patrón de nombre en un directorio específico.
    *   **Parámetros:**
        *   `path` (string, **requerido**): Ruta absoluta del directorio a buscar.
        *   `glob` (string, **requerido**): Patrón de nombre de archivo usando sintaxis glob.

**3. Herramientas de Shell:**

*   `shell_exec`:
    *   **Descripción:** Ejecuta comandos en una sesión de shell. Utilizado para ejecutar código, instalar paquetes o gestionar archivos.
    *   **Parámetros:**
        *   `id` (string, **requerido**): Identificador único de la sesión de shell.
        *   `exec_dir` (string, **requerido**): Directorio de trabajo para la ejecución del comando (ruta absoluta).
        *   `command` (string, **requerido**): Comando de shell a ejecutar.

*   `shell_view`:
    *   **Descripción:** Ve el contenido de una sesión de shell. Utilizado para verificar resultados de ejecución o monitorear la salida.
    *   **Parámetros:**
        *   `id` (string, **requerido**): Identificador único de la sesión de shell.

*   `shell_wait`:
    *   **Descripción:** Espera a que el proceso en ejecución en una sesión de shell termine. Utilizado después de comandos que requieren más tiempo de ejecución.
    *   **Parámetros:**
        *   `id` (string, **requerido**): Identificador único de la sesión de shell.
        *   `seconds` (integer, opcional): Duración de la espera en segundos.

*   `shell_write_to_process`:
    *   **Descripción:** Escribe entrada a un proceso en ejecución en una sesión de shell. Utilizado para responder a prompts interactivos.
    *   **Parámetros:**
        *   `id` (string, **requerido**): Identificador único de la sesión de shell.
        *   `input` (string, **requerido**): Contenido de entrada a escribir en el proceso.
        *   `press_enter` (boolean, **requerido**): Si se presiona la tecla Enter después de la entrada.

*   `shell_kill_process`:
    *   **Descripción:** Termina un proceso en ejecución en una sesión de shell. Utilizado para detener procesos de larga duración o comandos congelados.
    *   **Parámetros:**
        *   `id` (string, **requerido**): Identificador único de la sesión de shell.

**4. Herramientas de Navegador:**

*   `browser_view`:
    *   **Descripción:** Ve el contenido de la página actual del navegador. Utilizado para verificar el estado más reciente de páginas abiertas previamente.
    *   **Parámetros:** No requiere parámetros.

*   `browser_navigate`:
    *   **Descripción:** Navega el navegador a una URL específica. Utilizado cuando se necesita acceder a nuevas páginas.
    *   **Parámetros:**
        *   `url` (string, **requerido**): URL completa a visitar (debe incluir prefijo de protocolo).

*   `browser_restart`:
    *   **Descripción:** Reinicia el navegador y navega a una URL específica. Utilizado cuando el estado del navegador necesita ser reiniciado.
    *   **Parámetros:**
        *   `url` (string, **requerido**): URL completa a visitar después del reinicio.

*   `browser_click`:
    *   **Descripción:** Hace clic en elementos de la página actual del navegador. Utilizado cuando se necesita hacer clic en elementos de la página.
    *   **Parámetros:**
        *   `index` (integer, opcional): Número de índice del elemento a hacer clic.
        *   `coordinate_x` (number, opcional): Coordenada X de la posición del clic.
        *   `coordinate_y` (number, opcional): Coordenada Y de la posición del clic.

*   `browser_input`:
    *   **Descripción:** Sobrescribe texto en elementos editables de la página actual del navegador. Utilizado para rellenar campos de entrada.
    *   **Parámetros:**
        *   `index` (integer, opcional): Número de índice del elemento a sobrescribir texto.
        *   `coordinate_x` (number, opcional): Coordenada X del elemento a sobrescribir texto.
        *   `coordinate_y` (number, opcional): Coordenada Y del elemento a sobrescribir texto.
        *   `text` (string, **requerido**): Contenido de texto completo a sobrescribir.
        *   `press_enter` (boolean, **requerido**): Si se presiona la tecla Enter después de la entrada.

*   `browser_move_mouse`:
    *   **Descripción:** Mueve el cursor a una posición específica en la página actual del navegador. Utilizado para simular el movimiento del ratón del usuario.
    *   **Parámetros:**
        *   `coordinate_x` (number, **requerido**): Coordenada X de la posición del cursor.
        *   `coordinate_y` (number, **requerido**): Coordenada Y de la posición del cursor.

*   `browser_press_key`:
    *   **Descripción:** Simula la pulsación de una tecla en la página actual del navegador. Utilizado cuando se necesitan operaciones de teclado específicas.
    *   **Parámetros:**
        *   `key` (string, **requerido**): Nombre de la tecla a simular (ej. "Enter", "Tab", "ArrowUp"), soporta combinaciones de teclas (ej. "Control+Enter").

*   `browser_select_option`:
    *   **Descripción:** Selecciona una opción específica de un elemento de lista desplegable en la página actual del navegador. Utilizado para seleccionar opciones de menú desplegable.
    *   **Parámetros:**
        *   `index` (integer, **requerido**): Número de índice del elemento de lista desplegable.
        *   `option` (integer, **requerido**): Número de opción a seleccionar (empezando por 0).

*   `browser_scroll_up`:
    *   **Descripción:** Desplaza la página actual del navegador hacia arriba. Utilizado para ver contenido superior o volver al inicio de la página.
    *   **Parámetros:**
        *   `to_top` (boolean, opcional): Si se desplaza directamente al inicio de la página.

*   `browser_scroll_down`:
    *   **Descripción:** Desplaza la página actual del navegador hacia abajo. Utilizado para ver contenido inferior o saltar al final de la página.
    *   **Parámetros:**
        *   `to_bottom` (boolean, opcional): Si se desplaza directamente al final de la página.

*   `browser_console_exec`:
    *   **Descripción:** Ejecuta código JavaScript en la consola del navegador. Utilizado cuando se necesitan ejecutar scripts personalizados.
    *   **Parámetros:**
        *   `javascript` (string, **requerido**): Código JavaScript a ejecutar.

*   `browser_console_view`:
    *   **Descripción:** Ve la salida de la consola del navegador. Utilizado para verificar logs de JavaScript o depurar errores de página.
    *   **Parámetros:**
        *   `max_lines` (integer, opcional): Número máximo de líneas de log a devolver.

**5. Herramientas de Búsqueda:**

*   `info_search_web`:
    *   **Descripción:** Busca páginas web usando un motor de búsqueda. Utilizado para obtener la información más reciente o encontrar referencias.
    *   **Parámetros:**
        *   `query` (string, **requerido**): Consulta de búsqueda al estilo de Google (3-5 palabras clave).
        *   `date_range` (string, opcional, enum: ["all", "past_hour", "past_day", "past_week", "past_month", "past_year"]): Filtro de rango de tiempo para los resultados de búsqueda.

**6. Herramientas de Despliegue:**

*   `deploy_expose_port`:
    *   **Descripción:** Expone un puerto local específico para acceso público temporal. Utilizado para proporcionar acceso público temporal a servicios.
    *   **Parámetros:**
        *   `port` (integer, **requerido**): Número de puerto local a exponer.

*   `deploy_apply_deployment`:
    *   **Descripción:** Despliega un sitio web o aplicación en un entorno de producción público. Utilizado para desplegar o actualizar sitios web estáticos o aplicaciones.
    *   **Parámetros:**
        *   `type` (string, **requerido**, enum: ["static", "nextjs"]): Tipo de sitio web o aplicación a desplegar.
        *   `local_dir` (string, **requerido**): Ruta absoluta del directorio local a desplegar.

**7. Herramientas de Página Manus:**

*   `make_manus_page`:
    *   **Descripción:** Crea una página Manus a partir de un archivo MDX local.
    *   **Parámetros:**
        *   `mdx_file_path` (string, **requerido**): Ruta absoluta del archivo MDX fuente.

**8. Herramienta de Estado Inactivo:**

*   `idle`:
    *   **Descripción:** Una herramienta especial para indicar que se han completado todas las tareas y se va a entrar en estado inactivo.
    *   **Parámetros:** No requiere parámetros.

### Mecanismo de Selección de Herramientas del LLM en Manus AI

El LLM de Manus AI no utiliza un router de herramientas tradicional ni genera código Python directamente (CodeAct en su forma más pura de generación de código arbitrario). En cambio, emplea un enfoque más sofisticado que combina **function calling nativo** con un mecanismo de **selectores semánticos** y **manejo de contexto** [3].

1.  **Function Calling Nativo con Esquemas Declarativos:** Cada herramienta en Manus se define como un objeto `Tool` con un nombre, una descripción y un esquema de entrada (parámetros) [3]. Este esquema es esencialmente una especificación de función que el LLM puede interpretar. Cuando el LLM necesita realizar una acción, no genera código arbitrario, sino que "llama" a una de estas funciones predefinidas, proporcionando los argumentos necesarios según el esquema. Esto es similar a cómo funcionan las capacidades de function calling en modelos como GPT-4 o Gemini, donde el LLM genera una llamada a función estructurada en JSON que luego es ejecutada por el sistema. El archivo `tools.json` [1] es una manifestación de estos esquemas declarativos.

2.  **Selectores Semánticos para el Enrutamiento Inteligente:** Manus utiliza **selectores** (como `SemanticSelector`) para determinar qué herramienta invocar basándose en la interpretación del prompt del usuario y el contexto actual [3]. Estos selectores evalúan las descripciones de las herramientas frente al prompt y el contexto para clasificar o seleccionar la opción más relevante. Esto permite que el agente de Manus "auto-seleccione" herramientas de manera dinámica, en lugar de depender de cadenas de lógica rígidas o pasos de planificación explícitos. La clave aquí es que el LLM no solo elige una herramienta, sino que lo hace basándose en una comprensión semántica de la intención del usuario y la capacidad de la herramienta.

3.  **Manejo de Contexto y Máquina de Estados:** Para mejorar la selección de acciones, Manus utiliza una **máquina de estados consciente del contexto** para gestionar la disponibilidad de herramientas [2]. Esto significa que, en lugar de eliminar herramientas, el sistema puede "enmascarar" los logits de tokens durante la decodificación para evitar (o forzar) la selección de ciertas herramientas en momentos específicos. Esto permite que el agente se adapte a las necesidades de la tarea y evite llamadas a herramientas irrelevantes, aumentando la fiabilidad general. Además, el agente puede ser instrumentado con lógica de reintento condicional que se activa cuando se detectan ciertas firmas de fallo, utilizando la memoria de estado interna de Manus para ser consciente de intentos pasados [4].

4.  **Enfoque LLM-céntrico / LLM-driven:** El diseño de Manus es LLM-céntrico, lo que significa que los agentes deciden dinámicamente las acciones basándose en el razonamiento de los modelos de IA [5]. Esto contrasta con enfoques donde la lógica de decisión está fuertemente codificada. El LLM es el "cerebro" que decide la secuencia de herramientas a usar, los parámetros y cómo interpretar los resultados, todo dentro de un bucle de agente iterativo (analizar → planificar → ejecutar → observar) [6].

En resumen, el LLM de Manus AI decide qué herramienta usar a través de una combinación de function calling nativo basado en esquemas declarativos, selectores semánticos para el enrutamiento inteligente y una máquina de estados consciente del contexto para gestionar la disponibilidad de herramientas y el flujo de trabajo.

### Comportamiento de Fallo y Límites de las Herramientas en Manus AI

El sistema de herramientas de Manus AI está diseñado para ser resiliente frente a fallos, incorporando mecanismos de auto-depuración, reintentos y estrategias de fallback. Sin embargo, como cualquier sistema, tiene límites inherentes.

**1. Comportamiento de Fallo y Recuperación:**

*   **Auto-depuración y Reintentos Inteligentes:** Manus Agents están diseñados para auto-depurarse y reintentar fallos de API de forma autónoma [4]. Esto se logra mediante:
    *   **Bloques de reintento condicionales:** Se activan cuando se detectan firmas de fallo específicas (ej. payload vacío, código de estado inesperado, formato inválido). En lugar de reintentar ciegamente, el agente es consciente de sus intentos pasados utilizando la memoria de estado interna de Manus. Esto permite lógicas como: "Si `last_response.status == 502` Y `retry_count < 3`, entonces reintentar después de ajustar el tiempo de espera." [4].
    *   **Mutación de prompts:** En los reintentos, el agente puede alterar ligeramente sus solicitudes. Esto incluye reformular la solicitud, pedir un formato diferente (ej. JSON en lugar de Markdown) o añadir instrucciones de formato de fallback (ej. "Si hay error, devolver solo pares clave:valor") [4]. Esto reduce la tasa de fallos al evitar expectativas rígidas en las APIs downstream.
    *   **Prompts de auto-depuración:** Cuando todos los reintentos fallan, el agente entra en un "modo de depuración" interno. Reflexiona sobre la solicitud y la respuesta utilizando la herramienta `reflect()` de Manus y mensajes del sistema para preguntarse: "¿Qué parte de la respuesta no cumplió las expectativas?", "¿Los datos de entrada estaban mal formados?", "¿Debería recurrir a un flujo simplificado o en caché?" [4].
    *   **Rutas de fallback:** Basado en la auto-depuración, el agente puede redirigirse a una función de fallback (ej. usar solo datos parciales), una cadena de herramientas simplificada (ej. omitir la extracción de palabras clave) o un reintento retrasado con una estrategia alterada [4].

*   **Manejo de Errores Estructurado:** Las herramientas están envueltas en bloques `try/except` para devolver errores como datos estructurados en lugar de simplemente fallar [7]. La API de Manus utiliza un wrapper consistente para las respuestas, indicando éxito (`"ok": true`) o error (`"ok": false`) con un código de error y un mensaje [8]. Los códigos de error comunes incluyen `invalid_argument`, `not_found`, `permission_denied` y `rate_limited` [8].

**2. Límites de las Herramientas:**

*   **Tamaño Máximo de Output:** Aunque no se especifica un límite exacto para el output de cada herramienta individual en la documentación pública, el contexto general de los agentes de IA sugiere que el tamaño del output está limitado por la ventana de contexto del LLM subyacente. Los outputs excesivamente grandes pueden llevar a truncamiento o a un uso ineficiente de tokens, afectando la capacidad del LLM para razonar sobre el resultado. En la práctica, se recomienda que los outputs de las herramientas sean concisos y relevantes para la tarea.

*   **Timeouts:** Los timeouts son un factor crítico en la fiabilidad de las herramientas, especialmente para operaciones de red o ejecución de comandos de shell. El mecanismo de reintento de Manus puede ajustar los timeouts dinámicamente [4]. La API de Manus también puede devolver errores de timeout, aunque no se detalla un parámetro de timeout configurable por herramienta en el `tools.json` [1]. Esto implica que los timeouts pueden ser gestionados a nivel de sistema o de orquestación del agente.

*   **Rate Limits:** La API de Manus impone límites de tasa (`rate_limited`) para prevenir el abuso y asegurar la estabilidad del servicio [8]. Aunque los límites específicos por endpoint no se detallan en la documentación de `tools.json` [1] o en los artículos investigados, la existencia de este código de error indica que los desarrolladores deben implementar estrategias de backoff y reintento para manejar estas situaciones. La documentación de la API de Manus menciona una sección de "Rate Limits" [8], lo que sugiere que hay políticas claras sobre la frecuencia de las llamadas a la API.

*   **Limitación de una Acción por Iteración:** El diseño de Manus limita explícitamente al agente a una acción de herramienta por iteración [6]. Esto significa que el agente debe esperar el resultado de cada acción antes de decidir el siguiente paso. Esta restricción, aunque puede parecer un límite, es una característica de diseño que promueve un razonamiento más deliberado y evita bucles de ejecución incontrolados, contribuyendo a la estabilidad del agente.

### Proceso de Registro de Nuevas Herramientas en el Sistema Manus AI

El registro de nuevas herramientas en Manus AI se centra en la definición declarativa de las capacidades y su integración a través de un estándar de "Agent Skills" o mediante la definición de objetos `Tool` programáticamente.

1.  **Definición Declarativa de Herramientas (Tool Objects):** En el corazón del sistema de herramientas de Manus está la idea de que "cada capacidad es un objeto Tool" [3]. Para registrar una nueva herramienta, se crea un objeto `Tool` que encapsula una función callable. Este objeto requiere:
    *   `name`: Un nombre único para la herramienta.
    *   `description`: Una descripción concisa y orientada a objetivos que el LLM utilizará para entender cuándo invocar la herramienta.
    *   `func`: La función Python real que implementa la lógica de la herramienta.
    *   `parameters`: Un esquema que define los argumentos de entrada que la función acepta. Este esquema es crucial para que el LLM genere llamadas a funciones válidas [3].

    **Ejemplo de Pseudocódigo:**
    ```python
    from manus.tools import Tool

    def mi_nueva_funcion(param1: str, param2: int) -> str:
        # Lógica de la nueva herramienta
        return f"Resultado: {param1} - {param2}"

    mi_nueva_herramienta = Tool(
        name="mi_nueva_herramienta",
        description="Realiza una operación personalizada con dos parámetros.",
        func=mi_nueva_funcion,
        parameters={
            "param1": {"type": "string", "description": "Primer parámetro"},
            "param2": {"type": "integer", "description": "Segundo parámetro"}
        }
    )
    ```

2.  **Integración a través de Selectores:** Una vez definida la herramienta, se integra en el sistema de selección de herramientas de Manus mediante **selectores** [3]. Un selector, como `SemanticSelector`, toma una lista de objetos `Tool` y un modelo LLM compatible. El selector es responsable de evaluar las descripciones de las herramientas frente al prompt del usuario y el contexto para determinar cuál es la más relevante para la tarea. Esto implica que el registro de una herramienta no es solo definirla, sino también hacerla "conocida" al mecanismo de selección del LLM.

    **Ejemplo de Pseudocódigo:**
    ```python
    from manus.selectors import SemanticSelector
    # ... (definición de mi_nueva_herramienta y otras herramientas)

    selector = SemanticSelector(
        tools=[mi_nueva_herramienta, otra_herramienta],
        model="gpt-4" # o cualquier LLM compatible
    )
    # El selector ahora puede elegir mi_nueva_herramienta cuando sea apropiado
    ```

3.  **Estándar de Agent Skills:** Manus promueve un estándar abierto de "Agent Skills" para construir flujos de trabajo de IA personalizados [9]. Aunque no se detalla el formato exacto de estos "Skills" en la investigación, se infiere que proporcionan una forma estructurada de empaquetar y registrar herramientas junto con el contexto y el conocimiento procedimental necesario para que el agente las utilice eficazmente. Esto sugiere un enfoque modular donde las herramientas pueden ser importadas y exportadas, facilitando la extensión de las capacidades del agente sin bloqueo de proveedor.

4.  **Conectores MCP (Model Context Protocol):** La documentación de Manus menciona "Custom MCP Servers" y "MCP Connectors" [10]. Esto indica que las herramientas también pueden ser registradas o integradas a través de un protocolo de contexto de modelo, permitiendo la conexión con herramientas internas y sistemas propietarios. Este mecanismo probablemente implica la definición de herramientas en un formato que el servidor MCP pueda entender y exponer al agente de Manus.

En resumen, el registro de nuevas herramientas en Manus AI se realiza definiendo objetos `Tool` con esquemas declarativos, integrándolos a través de selectores semánticos y, potencialmente, empaquetándolos como "Agent Skills" o conectándolos a través de servidores MCP. El énfasis está en proporcionar descripciones ricas y esquemas claros para que el LLM pueda auto-seleccionar y utilizar las herramientas de manera autónoma y efectiva.


#### Comportamientos Observados en Producción
1.  **Comportamiento de Auto-depuración en Fallos de API:** Los agentes de Manus no solo detectan fallos de API (ej. 502, timeouts, esquemas inconsistentes), sino que inician un proceso de auto-depuración. Esto incluye reintentos condicionales basados en la memoria de estado del agente y la mutación de prompts para adaptar las solicitudes en intentos posteriores [4].
2.  **Reflexión Interna del Agente ante Errores:** Cuando los reintentos no son suficientes, el agente entra en un "modo de depuración" donde utiliza herramientas internas como `reflect()` para analizar el error, cuestionar la validez de los datos de entrada o la adecuación del flujo, y decidir sobre estrategias de fallback [4].
3.  **Limitación de una Acción por Iteración:** Se ha observado que el agente de Manus está explícitamente limitado a ejecutar una única acción de herramienta por iteración del bucle del agente. Esto significa que el agente debe esperar la finalización y el resultado de una herramienta antes de proceder a la siguiente decisión [6].
4.  **Uso de Selectores Semánticos para la Elección de Herramientas:** En lugar de un enrutamiento rígido, el sistema de Manus utiliza "selectores" que, basándose en la comprensión semántica del prompt del usuario y el contexto, eligen dinámicamente la herramienta más apropiada. Esto se traduce en una selección de herramientas más fluida y adaptativa [3].
5.  **Respuestas de Error Estructuradas:** La API de Manus devuelve errores en un formato estructurado con códigos específicos (ej. `invalid_argument`, `rate_limited`) y mensajes descriptivos, lo que permite un manejo de errores programático y predecible [8].
6.  **Gestión de Disponibilidad de Herramientas por Máquina de Estados:** El sistema gestiona la disponibilidad de herramientas a través de una máquina de estados consciente del contexto, lo que puede "enmascarar" o "forzar" la selección de herramientas para optimizar el flujo de trabajo y evitar acciones irrelevantes [2].

#### Fuentes Adicionales
1.  [Manus tools and prompts · GitHub](https://gist.github.com/jlia0/db0a9695b3ca7609c9b1a08dcbf872c9/raw/tools.json)
2.  [Context Engineering for AI Agents: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
3.  [Building a Tool-Savvy AI Agent in Manus That Self-Selects APIs](https://medium.com/@bhagyarana80/building-a-tool-savvy-ai-agent-in-manus-that-self-selects-apis-4f4831da5b62)
4.  [How I Tuned Manus Agents to Self-Debug and Retry API Failures Autonomously](https://medium.com/@connect.hashblock/how-i-tuned-manus-agents-to-self-debug-and-retry-api-failures-autonomously-0c385893aae9)
5.  [Manus AI: An Analytical Guide to the Autonomous AI Agent 2025](https://www.baytechconsulting.com/blog/manus-ai-an-analytical-guide-to-the-autonomous-ai-agent-2025)
6.  [In-depth technical investigation into the Manus AI agent, focusing on ...](https://gist.github.com/renschni/4fbc70b31bad8dd57f3370239dccd58f)
7.  [Building Retries in Agents: How to ...](https://pub.towardsai.net/building-retries-in-agents-how-to-build-ai-agents-that-survive-failures-32eedd2623f0)
8.  [Introduction - Manus API](https://open.manus.im/docs)
9.  [Build custom AI workflows with Manus Agent Skills | AI automation](https://manus.im/features/agent-skills)
10. [Custom MCP Servers - Manus Documentation](https://manus.im/docs/integrations/custom-mcp.md)

## M03 — M03 — Sandbox y Entorno de Ejecución de Manus AI

### Descripción Técnica
# M03 — Sandbox y Entorno de Ejecución de Manus AI

## Descripción Técnica Completa

El entorno de ejecución de Manus AI se basa en un **sandbox completamente aislado**, que se implementa como una **máquina virtual en la nube** dedicada a cada tarea [1]. Este diseño garantiza que cada tarea se ejecute en su propio entorno, sin afectar a otras tareas y permitiendo la ejecución en paralelo [1]. La plataforma subyacente para estas máquinas virtuales es **E2B**, que utiliza **microVMs Firecracker** (desarrolladas originalmente por AWS) para proporcionar entornos ligeros y efímeros [3].

### Arquitectura y Componentes

El sandbox de Manus AI emula un **ordenador en la nube completo**, ofreciendo capacidades como **redes, sistema de archivos, navegador web (Chromium), y diversas herramientas de software** [1] [3]. A diferencia de las soluciones basadas en contenedores como Docker, que carecen de la funcionalidad completa de un sistema operativo, los microVMs Firecracker proporcionan un **sistema operativo real (Ubuntu Linux)** [3]. Esto permite que los agentes de IA realicen acciones complejas como **instalar aplicaciones y paquetes de Python**, lo cual es crucial para tareas que van más allá de la simple ejecución de código [3].

El agente de Manus utiliza un **sistema multi-agente sofisticado**. Las solicitudes iniciales se dirigen a un **agente planificador** que descompone la tarea en subtareas secuenciales. Posteriormente, los **agentes ejecutores** llevan a cabo estas subtareas utilizando una variedad de herramientas disponibles en el sandbox, que incluyen la navegación web, la búsqueda de archivos y la ejecución de comandos en la terminal [3].

### Ciclo de Vida del Sandbox

El sandbox sigue un ciclo de vida predecible para equilibrar la eficiencia de los recursos con la persistencia de los datos [1]:

*   **Creación**: Un sandbox se crea bajo demanda al inicio de una nueva sesión [1].
*   **Suspensión/Activación (Sleep/Awake)**: Cuando el sandbox está inactivo (sin operaciones o ediciones de archivos), entra automáticamente en modo de suspensión. Al reanudar la tarea, el sandbox se activa automáticamente. Durante este ciclo, los archivos y datos dentro del sandbox permanecen inalterados [1].
*   **Reciclaje/Recreación (Recycle/Recreate)**: Un sandbox que permanece inactivo durante un período prolongado puede ser reciclado. Para usuarios gratuitos, este período es de 7 días, mientras que para usuarios de Manus Pro es de 21 días. Cuando se reabre una tarea después de que su sandbox ha sido reciclado, se crea automáticamente un nuevo sandbox. Manus restaura automáticamente los archivos más importantes del sandbox anterior, incluyendo **artefactos de Manus, archivos adjuntos subidos por el usuario y archivos de proyecto críticos (como Slides/WebDev)**. Sin embargo, el código intermedio y los archivos temporales creados durante la ejecución **no se restauran** [1].

### Seguridad y Aislamiento

El sandbox de Manus sigue el principio de **Zero Trust** [1]. Funciona como una máquina virtual en la nube que un usuario podría adquirir de un proveedor, otorgando a Manus y al usuario **control total sobre el entorno**, incluyendo la capacidad de obtener acceso root, modificar archivos del sistema o incluso formatear el disco completo [1]. A pesar de este nivel de acceso, cualquier operación dentro de un sandbox **solo afecta a ese sandbox específico**, sin impactar la seguridad o estabilidad del servicio de Manus ni permitir el acceso a los datos de sesión/cuenta del usuario desde el sandbox [1]. En caso de un error irrecuperable, Manus crea automáticamente un nuevo sandbox para reemplazarlo y permitir que la tarea continúe [1].

### Manejo de Archivos y Persistencia

El sandbox almacena los archivos necesarios durante la ejecución de la tarea, que incluyen [1]:

1.  **Archivos adjuntos** subidos por el usuario.
2.  **Archivos y artefactos** creados y escritos por Manus durante la ejecución.
3.  **Configuraciones** necesarias para tareas específicas (ej. tokens de usuario para APIs).

Los usuarios pueden ver todos los archivos de artefactos en el sandbox y solicitar a Manus que realice operaciones con ellos, como comprimir código y enviarlo [1]. La persistencia de los datos es un aspecto clave, con la restauración automática de archivos importantes tras el reciclaje del sandbox [1].

### Límites de Seguridad y Privacidad

Aunque el sandbox es un entorno privado, Manus implementa políticas estrictas de protección de la privacidad. Es crucial distinguir entre **compartir** y **colaborar** [1]:

*   **Compartir**: Al compartir una tarea, el destinatario solo ve los mensajes de la conversación y los artefactos de salida. El sandbox es completamente invisible para ellos, lo que significa que el contenido del sandbox no se filtra [1].
*   **Colaboración**: En una sesión de colaboración, los colaboradores obtienen permiso para participar en la tarea, lo que incluye enviar instrucciones a la IA y controlar la ejecución. En este escenario, el sandbox está abierto a los colaboradores, quienes pueden acceder o modificar archivos y datos a través de la IA, lo que podría causar una fuga de datos inesperada. Los **Connectors se deshabilitan automáticamente** durante la colaboración para evitar que los colaboradores accedan a servicios conectados [1].

Se recomiendan **mejores prácticas de privacidad** como verificar el contenido sensible antes de añadir colaboradores, crear nuevas tareas con contenido necesario si la tarea original contiene información sensible, y evitar enviar información personal sensible en sesiones de colaboración [1].

### Sistema de Créditos y Ejecución

Aunque la documentación consultada no detalla explícitamente cómo funciona el sistema de créditos en relación directa con la ejecución del sandbox, se menciona que el sandbox está **disponible para todos los usuarios en todos los niveles de suscripción** [1]. Sin embargo, existen diferencias en la persistencia del sandbox: los usuarios gratuitos tienen un período de retención de 7 días antes del reciclaje, mientras que los usuarios de Manus Pro tienen 21 días [1]. Esto sugiere que el modelo de créditos podría influir en la duración de la persistencia del sandbox y, potencialmente, en la capacidad de ejecutar tareas de larga duración o que requieran recursos continuos, aunque esto no se especifica directamente.

La velocidad de creación de un nuevo sandbox es de aproximadamente **150 ms**, lo que es lo suficientemente rápido para los estándares de los usuarios [3]. Esta eficiencia es un factor clave para la escalabilidad de Manus, permitiendo que cada usuario tenga un agente trabajando en una instancia separada [3].

### Capacidades y Limitaciones del Entorno

El entorno sandbox permite a los agentes de Manus realizar una amplia gama de tareas, desde el **análisis de datos hasta el uso de la terminal** [3]. Pueden ejecutar código en **Python, JavaScript, Bash y más** [3]. Las herramientas disponibles incluyen el uso del navegador Chromium para visitar URLs, guardar imágenes y desplazarse, ejecutar comandos de terminal y usar el sistema de archivos para crear, editar o eliminar archivos [3]. Esto permite a los agentes actuar como investigadores o desarrolladores reales, manteniendo el contexto entre los pasos, actualizando planes y produciendo artefactos complejos dentro de la misma sesión de sandbox aislada [3]. La capacidad de pausar y reanudar las sesiones del sandbox es importante para interacciones con el usuario o la gestión de credenciales [3].

Una limitación importante es que, aunque el sandbox es un entorno completo, la **restauración de archivos tras el reciclaje no incluye código intermedio ni archivos temporales** [1]. Esto implica que las tareas que dependen de estados intermedios no guardados explícitamente podrían verse afectadas si el sandbox se recicla. Además, la necesidad de E2B para proporcionar un sistema operativo real en lugar de contenedores como Docker resalta una limitación inherente de estos últimos para las necesidades de los agentes de IA [3].

En el futuro, Manus planea extender las capacidades del agente a **otros sistemas operativos como Windows y Android**, lo que indica una limitación actual a entornos basados en Linux [3].

### Capacidades e Implementación
| Capacidad | Implementación Técnica | Parámetros/Límites | Comportamiento Observado |
|---|---|---|---|
| **Aislamiento de Tareas** | Máquina virtual en la nube dedicada por tarea (MicroVMs Firecracker de E2B) | Cada tarea en su propio entorno aislado | Ejecución paralela sin interferencia entre tareas [1] [3] |
| **Sistema Operativo Completo** | Ubuntu Linux | Acceso root, modificación de archivos del sistema, formateo de disco | Permite instalación de software y paquetes (Python, JS, Bash) [1] [3] |
| **Persistencia de Archivos** | Almacenamiento en el sandbox | Restauración automática de artefactos, adjuntos, archivos de proyecto (Slides/WebDev) | Código intermedio y archivos temporales no se restauran tras reciclaje [1] |
| **Ciclo de Vida del Sandbox** | Creación bajo demanda, suspensión/activación, reciclaje/recreación | Usuarios gratuitos: 7 días de retención; Manus Pro: 21 días de retención | Equilibrio entre eficiencia de recursos y persistencia de datos [1] |
| **Seguridad (Zero Trust)** | Aislamiento a nivel de VM | Operaciones solo afectan al sandbox específico | No impacta la seguridad del servicio Manus ni accede a datos de sesión/cuenta [1] |
| **Control Total del Entorno** | Acceso a sistema de archivos, red, navegador (Chromium), terminal | Sin restricciones de permisos | Permite al agente realizar operaciones complejas y escribir código [1] [3] |
| **Ejecución de Código** | Python, JavaScript, Bash | No se especifican límites de recursos (CPU/RAM) | Permite análisis de datos, automatización y desarrollo [3] |
| **Navegación Web** | Navegador Chromium | Visitar URLs, guardar imágenes, desplazarse | Permite interacción con páginas web como un humano [3] |
| **Gestión de Archivos** | Creación, edición, eliminación de archivos | No se especifican límites de tamaño o cantidad | Permite al agente gestionar artefactos y datos [3] |
| **Escalabilidad** | MicroVMs Firecracker de E2B | Creación de sandbox en ~150ms | Cada usuario tiene un agente en una instancia separada [3] |
| **Colaboración Segura** | Deshabilitación automática de Connectors | Colaboradores pueden acceder al sandbox | Evita fugas de datos sensibles a través de servicios conectados [1] |

### Limitaciones y Fallas
| Limitación | Severidad | Fuente | Workaround |
|---|---|---|---|
| **Pérdida de código intermedio y archivos temporales** | Moderada | Documentación oficial de Manus [1] | Guardar explícitamente el código y los archivos importantes antes del reciclaje del sandbox. |
| **Acceso de colaboradores a datos sensibles en el sandbox** | Alta | Documentación oficial de Manus [1] | No añadir colaboradores si la tarea contiene información sensible; crear una nueva tarea con contenido filtrado para colaboración. |
| **Dependencia de E2B para entornos de SO completos** | Baja | Blog de E2B [3] | No aplica directamente al usuario final, pero es una limitación arquitectónica para Manus si E2B no está disponible o cambia. |
| **Limitación actual a entornos basados en Linux** | Baja | Blog de E2B [3] | No aplica directamente al usuario final, pero limita la capacidad de los agentes para interactuar con otros sistemas operativos de forma nativa. |
| **No se especifica el sistema de créditos en relación directa con la ejecución** | Baja | Documentación oficial de Manus [1] | Asumir que la persistencia del sandbox (7/21 días) es el principal indicador de los límites de uso para usuarios gratuitos/Pro. |

### Ejemplos de Uso Real
1.  **Generación de modelos 3D y análisis financiero**: El editor jefe de Financial Times Chinese utilizó Manus para generar un modelo impreso en 3D que representaba la deuda nacional de EE. UU. durante la última década, demostrando la capacidad del sandbox para manejar tareas complejas de análisis de datos y generación de artefactos [3].
2.  **Desarrollo de estrategias de contenido para redes sociales**: Un consultor de redes sociales en Dubái aprovechó Manus para desarrollar estrategias de contenido integrales para clientes. El agente, al recibir el sitio web y los perfiles de redes sociales del cliente, generó documentos de más de 50 páginas con estrategias de un año, incluyendo segmentación de audiencia, títulos, contenido, ganchos y recomendaciones específicas por canal. Este ejemplo destaca la capacidad del sandbox para producir documentos extensos y complejos basados en análisis de datos y creatividad [3].
3.  **Creación de sitios web y aplicaciones móviles**: El sandbox permite a los agentes de IA resolver problemas mediante la escritura de código, incluso ayudando a crear sitios web y aplicaciones móviles completas [1].
4.  **Automatización de flujos de trabajo**: Los sistemas de ejecución como el agente de IA de escritorio de Manus continúan trabajando hasta que los flujos de trabajo finalizan en todo el entorno, lo que permite la automatización de pipelines de producción [4].


### Hallazgos de Fase 2 (Actualizado 1 Mayo 2026)

#### Nuevos Descubrimientos
La investigación del Módulo M03 (Sandbox y Entorno de Ejecución de Manus AI) revela que la infraestructura se basa en microVMs Firecracker gestionadas por E2B, proporcionando aislamiento a nivel de máquina virtual. 

**Especificaciones de Firecracker:**
Las vCPUs son personalizables (1 a 8 para usuarios Pro, 2 por defecto). Firecracker arranca microVMs en ~125 ms y soporta hasta 150 microVMs/segundo/host. El rendimiento de red puede alcanzar 14.5 Gbps usando <= 80% del núcleo de CPU del host para emulación, y hasta 25 Gbps en condiciones óptimas. La RAM también es personalizable (hasta 8+ GB para Pro). Un microVM típico consume solo ~5 MB de RAM para la sobrecarga del hipervisor. El almacenamiento base es de 10 GB (Hobby) o 20 GB (Pro), con soporte para montar buckets externos vía FUSE.

**Reciclaje del Sandbox:**
El ciclo de vida incluye estados: Running, Paused, Snapshotting y Killed. Al pausar, se guarda el estado del sistema de archivos y la memoria (procesos, variables). Pausar toma ~4 segundos por GiB de RAM; reanudar toma ~1 segundo. Los sandboxes pausados se retienen indefinidamente. El límite de ejecución continua es de 24 horas (Pro) o 1 hora (Base), reiniciándose tras una pausa/reanudación.

**Mecanismos de Seguridad (E2B):**
Más allá del aislamiento de Firecracker, E2B implementa "Secure Access" (por defecto en SDK v2.0.0+), que autentica la comunicación entre el SDK y el controlador del sandbox. La gestión de red permite deshabilitar el acceso a internet o aplicar control granular (allow/deny lists para IPs, CIDR, dominios). El filtrado de dominios funciona para HTTP (puerto 80) y TLS (puerto 443) vía inspección de Host/SNI. Las reglas de permiso tienen prioridad. Las URLs públicas de los sandboxes pueden restringirse requiriendo un token (`e2b-traffic-access-token`). La prevención de ataques incluye límites obligatorios de recursos (CPU, disco, red) en el hipervisor para evitar agotamiento, y la reducción de la superficie de ataque al omitir emulación de dispositivos innecesarios.

**Sistema de Créditos y Uso:**
El modelo de precios es basado en el uso. Se cobra por segundo de tiempo de ejecución del sandbox, no por operaciones específicas (como comandos o archivos creados). El costo depende de los recursos de cómputo (vCPUs y RAM) asignados. La optimización de costos se logra mediante la auto-pausa, pausando sandboxes inactivos y eliminando los innecesarios.

#### Detalles de Implementación
Los sandboxes de Manus AI, basados en E2B y Firecracker, permiten personalización de recursos. Los usuarios Pro pueden configurar vCPUs y RAM al construir plantillas usando la CLI de E2B (`e2b template build --cpu-count <numero_vcpus> --memory-mb <cantidad_ram_en_MB>`) o el SDK de E2B (`await Template.build(template, 'my-template', { cpuCount: 8, memoryMB: 4096 })`). Por defecto, se asignan 2 vCPUs. El ciclo de vida se gestiona vía SDK: `Sandbox.create({ lifecycle: { onTimeout: 'pause' } })` para auto-pausa, `sbx.pause()` para pausar, `sbx.connect()` para reanudar y `sbx.kill()` para terminar. La seguridad de red se configura al crear el sandbox: `Sandbox.create({ allowInternetAccess: false })` deshabilita el acceso a internet (equivalente a denegar `0.0.0.0/0`). El control granular usa listas de permiso/denegación: `Sandbox.create({ network: { denyOut: [ALL_TRAFFIC], allowOut: ['google.com', '8.8.8.8'] } })`. El acceso seguro (Secure Access) está habilitado por defecto en SDKs v2.0.0+, requiriendo un token de autenticación para interactuar con el controlador del sandbox.

#### Comportamientos Observados en Producción
- Pérdida de archivos en sandboxes pausados: Un bug crítico (e2b-dev/E2B#884) causa que los cambios en archivos no persistan después de múltiples ciclos de pausa/reanudación, probablemente debido a un problema de coherencia de caché de escritura. (Fuente: GitHub e2b-dev/E2B#884)
- Errores de sandbox durante la generación de tareas: Usuarios reportan errores que requieren reiniciar el sandbox para continuar. (Fuente: Manus Help Center, Reddit)
- Terminación por alta carga (Error 10091): El sandbox puede ser terminado si excede límites de recursos. (Fuente: Manus Help Center)
- Inconsistencia de estado: El estado del sandbox puede mutar en segundo plano, llevando al agente a actuar sobre información desactualizada. (Fuente: Reddit r/AgentsOfAI)
- Vulnerabilidad SilentBridge: Un reporte detalla un ataque zero-click que permite la toma de control del agente, destacando fallas en el límite de confianza. (Fuente: AuraScape AI Research)

#### Fuentes Adicionales
1. https://e2b.dev/blog/how-manus-uses-e2b-to-provide-agents-with-virtual-computers
2. https://e2b.dev/
3. https://e2b.dev/blog/customize-sandbox-compute
4. https://e2b.dev/pricing
5. https://firecracker-microvm.github.io/
6. https://github.com/firecracker-microvm/firecracker/blob/main/SPECIFICATION.md
7. https://thesequence.substack.com/p/the-sequence-ai-of-the-week-698-how
8. https://e2b.dev/docs/sandbox/persistence
9. https://e2b.dev/docs/filesystem
10. https://github.com/e2b-dev/E2B/issues/884
11. https://e2b.dev/docs/sandbox/connect-bucket
12. https://e2b.dev/blog/scaling-firecracker-using-overlayfs-to-save-disk-space
13. https://manus.im/blog/manus-sandbox
14. https://e2b.dev/docs/sandbox/internet-access
15. https://e2b.dev/docs/sandbox/secured-access
16. https://pub.towardsai.net/e2b-ai-sandboxes-features-applications-real-world-impact-75e949ded8a7
17. https://northflank.com/blog/daytona-vs-e2b-ai-code-execution-sandboxes
18. https://github.com/e2b-dev/E2B/issues/1160
19. https://e2b.dev/docs/sandbox/metrics
20. https://e2b.dev/docs/sdk-reference/cli/v1.4.1/sandbox
21. https://www.reddit.com/r/ManusOfficial/comments/1opvamx/manus_ai_is_a_nightmare_incomplete_builds_buggy/
22. https://help.manus.im/en/articles/11711144-what-can-i-do-if-i-encounte-a-sandbox-issue-in-the-task
23. https://help.manus.im/en/collections/15921659-troubleshooting-limitations
24. https://www.reddit.com/r/AgentsOfAI/comments/1rckhqy/what_are_you_actually_using_to_sandbox_your/
25. https://aurascape.ai/resources/auralabs-research/silentbridge-zero-click-agent-takeover-meta-manus/

## M04 — Manejo de Contexto y Memoria (ACTUALIZADO 30 Abril 2026)

### Descripción Técnica
Manus usa una arquitectura de memoria en capas que combina contexto activo, memoria basada en archivos en el sandbox, y sub-agentes con contexto fresco para tareas largas. NO comprime ni trunca el contexto — en su lugar, despliega Wide Research con agentes paralelos cuando el contexto se llena.

### Cómo Maneja el Contexto Lleno (>200k tokens)
| Estrategia | Descripción |
|-----------|-------------|
| Wide Research | Despliega sub-agentes con contexto fresco y vacío |
| Memoria en archivos | Escribe archivos .md en el sandbox para persistir información |
| Agente orquestador | El agente principal sintetiza resultados de sub-agentes |
| NO compresión | No resume ni trunca — divide la tarea en subtareas |

### Persistencia Entre Sesiones
| Qué persiste | Qué NO persiste |
|-------------|----------------|
| Archivos escritos en el sandbox | Contexto de conversación del LLM |
| Knowledge Base del usuario (100 entradas Pro, 50 Free) | Estado de memoria del LLM |
| Estado de ejecución de tareas largas | Variables en memoria RAM |
| Resultados guardados en archivos | Cookies de sesión del browser |

### Knowledge Base de Manus
- **Límite Pro:** 100 entradas
- **Límite Free:** 50 entradas
- **Inyección:** Como "eventos de Conocimiento" en el contexto del agente
- **Módulo Datasource:** APIs pre-aprobadas invocadas via Python, priorizan fuentes autorizadas

### Archivos que Escribe en el Sandbox
El agente escribe activamente en el filesystem de su VM Ubuntu para:
- Rastrear progreso de tareas largas (`.progress.md`)
- Almacenar datos intermedios (`.json`, `.csv`)
- Guardar resultados para síntesis posterior
- Mantener estado entre herramientas

### Score de Completitud: 90%
**Fuentes verificadas:** manus.im/blog, Reddit r/ManusOfficial, GitHub Gist renschni, Level Up Coding

---

## M05 — M05 — Browser y Navegación Web: Cómo Manus navega páginas web, hace clic, llena formularios, maneja login y autenticación, extrae datos de páginas dinámicas con JavaScript, maneja CAPTCHAs, el cloud browser que usa, cómo maneja el estado de sesión del navegador

### Descripción Técnica
# M05 — Browser y Navegación Web: Capacidades de Manus AI

El módulo M05 de Manus AI, centrado en las capacidades de **Browser y Navegación Web**, representa una funcionalidad crítica que permite al agente interactuar con el vasto ecosistema de la World Wide Web de una manera altamente sofisticada y contextualizada. A diferencia de los enfoques tradicionales de automatización web, Manus AI, a través de su `Browser Operator`, no solo navega y extrae información, sino que lo hace emulando el comportamiento humano y aprovechando el entorno de navegación local del usuario. Esto le confiere una ventaja distintiva en el manejo de escenarios complejos como la autenticación, la interacción con plataformas premium y la elusión de mecanismos anti-bot.

## ¿Qué es Manus Browser Operator?

El `Manus Browser Operator` es una extensión de navegador diseñada para transformar cualquier navegador web estándar (actualmente Chrome y Edge son los recomendados) en un "navegador de IA". Su propósito fundamental es permitir que Manus opere directamente dentro del entorno de navegador local del usuario. Esto contrasta con el "Cloud Browser" que Manus utiliza por defecto, el cual opera en un entorno aislado y sandboxed. La clave del `Browser Operator` reside en su capacidad para trabajar con las sesiones existentes del usuario, sus inicios de sesión activos y su dirección IP local. Esta integración profunda convierte el navegador del usuario de una herramienta de visualización pasiva en un espacio de trabajo activo donde Manus puede ejecutar tareas complejas utilizando las herramientas premium y los sistemas autenticados a los que el usuario ya tiene acceso [1].

## La Importancia del Navegador Local: La Ventaja de la Autenticación

La decisión de operar en el navegador local del usuario confiere a Manus una **ventaja de autenticación** significativa. Cuando Manus trabaja en este entorno, lo hace con las credenciales de confianza y la dirección IP local del usuario, lo que se traduce en varios beneficios clave:

*   **Sin Barreras de Inicio de Sesión**: El sistema web reconoce la actividad como proveniente de una máquina de confianza, eliminando la necesidad de intentos de inicio de sesión desconocidos, interrupciones por CAPTCHA y problemas de expiración de sesión. Esto es crucial para la automatización fluida en entornos donde la seguridad es estricta.
*   **Acceso Fiable**: Dado que la actividad parece legítima para los sitios web, Manus supera automáticamente las barreras de acceso estándar y mantiene las sesiones activas, lo que garantiza una interacción continua y sin interrupciones.
*   **Acceso a Herramientas Premium**: Manus puede interactuar con servicios de suscripción a los que el usuario ya está logueado, como Crunchbase, PitchBook, SimilarWeb, Financial Times, Semrush, Ahrefs, o cualquier otra plataforma autenticada. Esto abre un abanico de posibilidades para la investigación y el análisis de datos que de otro modo serían inaccesibles para un agente de IA genérico.

### Comparación: Cloud Browser vs. Local Browser

Es fundamental entender la distinción entre los dos modos de operación del navegador de Manus:

| Característica | Cloud Browser (Por Defecto) | Local Browser (Browser Operator) |
|---|---|---|
| **Entorno** | Sandboxed, aislado | Utiliza el navegador real del usuario |
| **Instalación** | No requiere instalación | Requiere la extensión `Browser Operator` |
| **Uso Principal** | Investigación general, análisis, creación de contenido | Flujos de trabajo que requieren acceso autenticado |
| **Credenciales/Sesiones** | No utiliza las sesiones del usuario | Utiliza sesiones existentes del usuario |
| **IP** | IP de la nube | IP local y de confianza del usuario |
| **Requisitos** | Ninguno | El navegador local debe estar en funcionamiento |

Ambos modos trabajan de forma complementaria, y Manus selecciona automáticamente el entorno apropiado para cada tarea, optimizando la eficiencia y la capacidad de acceso [1].

## Mecanismo de Funcionamiento: El Proceso de 3 Pasos

La operación del `Manus Browser Operator` sigue un proceso claro y controlado por el usuario:

1.  **Paso 1: Activar el Conector "Mi Navegador"**: El usuario debe navegar a la sección de Conectores de Manus y activar la opción "Mi Navegador". Esto indica a Manus que debe utilizar el navegador local para las tareas que requieran acceso web.
2.  **Paso 2: Autorizar la Sesión**: Cuando se asigna una tarea que requiere el `Browser Operator`, Manus solicita permiso explícito para tomar el control del navegador. El usuario debe hacer clic en "Autorizar" para conceder acceso por una sola vez. Este mecanismo asegura que el usuario mantiene el control total sobre cuándo y cómo Manus interactúa con su navegador.
3.  **Paso 3: Monitorear en una Pestaña Dedicada**: Manus abre una nueva pestaña dentro de un grupo de pestañas nombrado según la tarea actual. Esto permite al usuario:
    *   Observar el desarrollo de la tarea en tiempo real.
    *   Tomar el control manual en cualquier momento haciendo clic en la pestaña.
    *   Detener la tarea instantáneamente cerrando la pestaña dedicada.

Este enfoque garantiza una supervisión completa y la capacidad de intervención por parte del usuario [1].

## Transparencia y Control del Usuario

Manus AI pone un fuerte énfasis en la transparencia y el control del usuario sobre las operaciones del `Browser Operator`:

*   **Visibilidad Completa**: Cada acción realizada por Manus es registrada meticulosamente, proporcionando un rastro de auditoría claro. El usuario puede ver exactamente lo que Manus está haciendo en cada paso.
*   **Parada Instantánea**: Si el usuario necesita detener una tarea de inmediato, simplemente puede cerrar la pestaña dedicada, y Manus se detendrá al instante.
*   **Acceso Remoto**: Dado que Manus opera localmente en el navegador de escritorio del usuario, las tareas pueden iniciarse y monitorearse desde un teléfono u otro dispositivo, siempre que el ordenador principal esté en línea.
*   **Revisión Antes de la Autorización**: En sitios que contienen información sensible, el usuario puede revisar lo que Manus accederá antes de hacer clic en "Autorizar", manteniendo siempre el control sobre sus datos [1].

## Seguridad y Privacidad

La seguridad y la privacidad son pilares fundamentales en el diseño del `Browser Operator`:

*   **Control del Usuario**: La autorización es de una sola vez para cada tarea, la actividad es visible y registrada en tiempo real, la terminación es instantánea al cerrar la pestaña, y el acceso es selectivo, permitiendo al usuario elegir qué tareas utilizan el navegador local.
*   **Protección de Datos**: Manus opera dentro del navegador del usuario utilizando sus sesiones existentes, lo que significa que **no se almacenan ni transmiten credenciales**. La actividad aparece como si proviniera de la máquina local del usuario, y las políticas de privacidad estándar de Manus se aplican a todas las operaciones [1].

## Consejos para Obtener los Mejores Resultados

Para maximizar la eficacia del `Browser Operator`, se recomiendan las siguientes prácticas:

*   **Especificidad en el Uso de Herramientas**: Indicar explícitamente qué cuentas o herramientas premium deben usarse (ej. "Usa mi cuenta de Crunchbase...").
*   **Verificar Inicios de Sesión**: Asegurarse de que el usuario esté logueado en los servicios requeridos y que las sesiones estén activas antes de iniciar la tarea.
*   **Revisar Sitios Sensibles**: Ejercer precaución con cuentas financieras o datos sensibles, revisando el acceso antes de autorizar.
*   **Monitorear las Primeras Tareas**: Observar las primeras ejecuciones para comprender el comportamiento del `Browser Operator` y ajustar los prompts según sea necesario.
*   **Combinar con Otras Funcionalidades**: Utilizar el `Browser Operator` junto con otras características de Manus, como la "Wide Research" para procesamiento paralelo o la exportación de resultados a diferentes formatos [1].

En resumen, el módulo M05 de Manus AI, a través de su `Browser Operator`, ofrece una solución robusta y controlada por el usuario para la automatización web inteligente, permitiendo a los agentes de IA interactuar con el mundo digital de una manera que respeta la autenticación, la privacidad y la supervisión humana.

### Capacidades e Implementación
| Capacidad | Implementación | Parámetros/Límites | Comportamiento |
|---|---|---|---|
| **Navegación Web Local** | Extensión de navegador (`Manus Browser Operator`) | Utiliza el navegador local del usuario (Chrome, Edge) | Permite a Manus operar directamente en el entorno del navegador del usuario, aprovechando sesiones existentes y la IP local. |
| **Manejo de Login y Autenticación** | Aprovecha credenciales y sesiones existentes del navegador local | No almacena ni transmite credenciales | Elimina barreras de inicio de sesión, interrupciones por CAPTCHA y problemas de expiración de sesión al reconocer la actividad como legítima. |
| **Acceso a Herramientas Premium** | Utiliza sesiones autenticadas del usuario | Requiere que el usuario esté previamente logueado en los servicios | Permite a Manus interactuar con servicios de suscripción como Crunchbase, PitchBook, Semrush, Ahrefs, Financial Times, Bloomberg, WSJ. |
| **Extracción de Datos de Páginas Dinámicas** | Control programático del navegador local | No se especifican límites de volumen o complejidad | Permite la extracción sistemática de datos de plataformas web complejas y autenticadas. |
| **Interacción con Formularios** | Control programático del navegador local | Interacciones complejas (arrastrar y soltar, formularios de varios pasos) pueden tener limitaciones | Permite rellenar formularios y realizar acciones transaccionales. |
| **Manejo de CAPTCHAs** | Evita CAPTCHAs al operar con credenciales de usuario confiables | Depende de la legitimidad de la actividad del usuario | Reduce las interrupciones por CAPTCHA al ser reconocido como actividad de una máquina de confianza. |
| **Gestión del Estado de Sesión** | Utiliza las sesiones existentes del navegador local | La sesión debe estar activa y no expirada | Mantiene el estado de sesión activo, evitando cierres de sesión inesperados. |
| **Visibilidad y Control del Usuario** | Interfaz de usuario con tabulador dedicado, registro de acciones, botón de parada instantánea | Autorización única por tarea | El usuario puede monitorear la tarea en tiempo real, tomar el control, detenerla instantáneamente y revisar el acceso antes de autorizar. |
| **Acceso Remoto** | Operación local en el navegador de escritorio | Requiere que el ordenador principal esté online | Permite iniciar y monitorear tareas desde otros dispositivos (ej. móvil) siempre que el ordenador principal esté conectado. |
| **Seguridad y Privacidad** | Autorización única, actividad visible, terminación instantánea, acceso selectivo, no almacenamiento de credenciales | Políticas de privacidad estándar de Manus aplican | Garantiza que el usuario mantiene el control, sus credenciales no son transmitidas y la actividad es local. |

### Limitaciones y Fallas
| Limitación | Severidad | Fuente | Workaround |
|---|---|---|---|
| Interacciones complejas (arrastrar y soltar, formularios de varios pasos) pueden no funcionar perfectamente | Moderada | Documentación oficial de Manus [1] | Intervención manual del usuario; simplificar la tarea o dividirla en pasos más pequeños. |
| Algunos sitios web con medidas agresivas anti-bot pueden requerir intervención manual | Moderada | Documentación oficial de Manus [1] | Intervención manual del usuario; ajustar la estrategia de navegación o el prompt. |
| No funciona en móvil de forma autónoma | Alta | Documentación oficial de Manus [1] | Iniciar tareas desde móvil, pero el navegador de escritorio debe estar ejecutándose. |
| Requiere que el usuario esté logueado en los servicios premium | Baja | Documentación oficial de Manus [1] | Verificar y asegurar que las sesiones estén activas antes de iniciar la tarea. |
| Requiere autorización explícita para cada tarea | Baja | Documentación oficial de Manus [1] | Es una característica de seguridad, no una limitación funcional, pero añade un paso al flujo de trabajo. |

### Ejemplos de Uso Real
1.  **Investigación de Mercado con Herramientas Premium**: Un usuario solicita a Manus que analice 20 competidores utilizando sus suscripciones a Crunchbase y PitchBook. Manus extrae rondas de financiación, inversores clave, estimaciones de ingresos y número de empleados, y crea una tabla comparativa. [1]
2.  **Análisis SEO a Escala**: Un usuario pide a Manus que audite 50 sitios web de la competencia utilizando sus cuentas de Semrush y Ahrefs. Manus extrae la autoridad del dominio, las palabras clave principales, el perfil de backlinks y las estimaciones de tráfico, identificando brechas de contenido y oportunidades. [1]
3.  **Enriquecimiento de Datos CRM**: Un usuario solicita a Manus que enriquezca 100 leads en su CRM utilizando sus cuentas de LinkedIn Sales Navigator y Crunchbase para encontrar el tamaño de la empresa, financiación reciente, tomadores de decisiones clave y noticias recientes, actualizando los registros del CRM. [1]
4.  **Investigación Financiera**: Un usuario encarga a Manus la compilación de inteligencia de mercado de fuentes de pago, como Financial Times, Bloomberg y WSJ, para 10 empresas públicas. Manus extrae opiniones de analistas, sentimiento de ganancias y movimientos estratégicos, resumiendo los temas clave. [1]


### Hallazgos de Fase 2 (Actualizado 1 Mayo 2026)

#### Nuevos Descubrimientos
La investigación ha revelado una arquitectura dual para la interacción web en Manus AI: el **Cloud Browser** y el **Manus Browser Operator**. Esta distinción es fundamental para comprender cómo Manus aborda los diversos desafíos de la navegación web y la automatización. Mientras que el Cloud Browser ofrece un entorno aislado y escalable para tareas generales, el Browser Operator se posiciona como una solución estratégica para escenarios que requieren una mayor autenticación y resistencia a las medidas anti-bot.

### Manejo de Login y Autenticación

Manus AI implementa un enfoque robusto para el login y la autenticación, diferenciando claramente entre su **Cloud Browser** y el **Manus Browser Operator**. En el **Cloud Browser**, las sesiones de usuario se gestionan en entornos aislados y cifrados. Un hallazgo clave es que Manus **no almacena directamente las contraseñas** de los usuarios [1]. En su lugar, permite al usuario iniciar sesión en sus cuentas dentro del entorno del Cloud Browser, y luego utiliza estas sesiones autenticadas para realizar tareas. Esto implica que la persistencia de la sesión se logra a través de la gestión de cookies y tokens de sesión dentro de cada instancia aislada del navegador, sin que Manus tenga acceso directo a las credenciales sensibles. La capacidad de gestionar y borrar sesiones en cualquier momento proporciona un control granular al usuario sobre su privacidad y seguridad [1].

Por otro lado, el **Manus Browser Operator** representa una innovación significativa en el manejo de la autenticación. Al ser una extensión que opera en el navegador local del usuario, aprovecha las sesiones y credenciales ya establecidas en la máquina del usuario. Esto significa que el Browser Operator no necesita realizar un proceso de login independiente, sino que hereda el estado de autenticación del navegador anfitrión. Este mecanismo es crucial porque la actividad web se percibe como proveniente de una dirección IP residencial y de un perfil de usuario de confianza, lo que reduce drásticamente la probabilidad de activar mecanismos de seguridad o bloqueos por parte de los sitios web [2]. La autorización para que Manus tome el control del navegador local es de un solo uso y explícita, garantizando que el usuario mantenga el control total sobre cuándo y cómo Manus interactúa con sus cuentas autenticadas [2].

### Gestión de CAPTCHAs

El manejo de CAPTCHAs es un área donde la dualidad de la arquitectura de Manus AI se vuelve particularmente evidente. Para el **Cloud Browser**, la estrategia principal frente a CAPTCHAs y otras verificaciones complejas (como códigos SMS o autenticación multifactor) es el mecanismo de **"Tomar el Control" (Take Over)** [1]. Este hallazgo es importante porque indica que el Cloud Browser no posee un bypass nativo o una integración con servicios de resolución de CAPTCHAs de terceros como 2Captcha. En cambio, delega la resolución al usuario humano, quien interviene para completar la verificación y luego devuelve el control a Manus. Esta aproximación, aunque requiere intervención humana, asegura la finalización de la tarea incluso ante desafíos de seguridad avanzados. La mayor propensión del Cloud Browser a encontrar CAPTCHAs se atribuye a su uso de direcciones IP de centros de datos, que son más fácilmente identificables como tráfico automatizado [1].

En contraste, el **Manus Browser Operator** ofrece un **bypass nativo** más efectivo para muchos CAPTCHAs. Al operar desde el navegador local del usuario y utilizar su dirección IP residencial, la actividad de navegación se considera legítima, lo que reduce significativamente la aparición de CAPTCHAs y otras interrupciones de seguridad [2]. Este es un hallazgo crítico, ya que posiciona al Browser Operator como la solución preferida para tareas que requieren acceso a sitios web con medidas anti-bot agresivas. Sin embargo, la documentación también señala que, en casos de medidas anti-bot extremadamente sofisticadas, la intervención manual del usuario aún podría ser necesaria, lo que subraya las limitaciones inherentes incluso a las soluciones más avanzadas [2].

### Extracción de Datos de Páginas con JavaScript Pesado

Manus AI demuestra una capacidad inherente para interactuar con páginas web dinámicas, incluyendo aquellas construidas con frameworks JavaScript como React o Angular (SPAs). La capacidad de "operar este navegador como una persona real—visitando sitios web, haciendo clic en botones, rellenando formularios, extrayendo datos y completando flujos de trabajo de varios pasos" [1] implica que el sistema espera activamente la carga completa del DOM y la ejecución del JavaScript antes de proceder con la extracción de datos o la interacción. Esto se refuerza con la mención de que Manus puede "scrape dynamic data" y "manage session states" [4], lo que es indicativo de un motor de renderizado JavaScript completo.

Un hallazgo relevante es la admisión de que Manus "struggles with JavaScript-heavy single-page apps, sites behind Cloudflare..." [3]. Esto no niega su capacidad de manejar JavaScript, sino que destaca las **limitaciones en la robustez** de su motor de renderizado o sus estrategias de interacción frente a complejidades extremas o medidas de protección avanzadas. Esto sugiere que, si bien Manus espera la carga del DOM, la complejidad del JavaScript o la implementación de técnicas de ofuscación o detección de bots pueden aún presentar desafíos, requiriendo posiblemente ajustes en la estrategia de automatización o la intervención del usuario.

### Tecnología de Cloud Browser

La documentación oficial de Manus AI es deliberadamente ambigua sobre la tecnología específica de navegador en la nube que utiliza, refiriéndose a ella simplemente como "Cloud Browser" [1]. Sin embargo, la descripción de sus capacidades—como la interacción humana con aplicaciones web, la ejecución de JavaScript y la gestión de sesiones—apunta fuertemente hacia el uso de tecnologías de automatización de navegadores headless. La investigación sugiere que Manus probablemente se basa en frameworks como **Playwright o Puppeteer** [5], o una abstracción propietaria construida sobre ellos. Estos frameworks son conocidos por su capacidad para controlar navegadores reales (como Chromium, Firefox, WebKit) en un entorno headless, permitiendo la renderización completa de JavaScript y la simulación de interacciones de usuario complejas. La elección de no especificar la tecnología exacta podría deberse a razones comerciales, a la flexibilidad para cambiar la implementación subyacente, o a que es una solución altamente personalizada que integra componentes de varias fuentes.

### Manejo del Estado de Sesión entre Múltiples Pasos

La persistencia del estado de sesión es un pilar fundamental para la ejecución de tareas largas y complejas en Manus AI. Tanto el Cloud Browser como el Browser Operator están diseñados para mantener el estado de la sesión a lo largo de múltiples pasos de una tarea [1][2]. En el **Cloud Browser**, esto se logra mediante la persistencia de las sesiones autenticadas dentro de los entornos aislados de cada usuario. La recomendación de "iniciar sesión en cuentas de uso frecuente con antelación" [1] subraya la importancia de esta persistencia para una automatización fluida. El sistema proporciona herramientas para que el usuario gestione activamente estas sesiones, permitiendo cerrar sesión en cuentas específicas o borrar todas las sesiones, lo que ofrece un equilibrio entre conveniencia y seguridad [1].

Para el **Manus Browser Operator**, la gestión del estado de sesión es aún más intrínseca, ya que opera directamente dentro del navegador local del usuario. Esto significa que el Browser Operator se beneficia automáticamente de la forma en que el navegador del usuario ya maneja las cookies, el almacenamiento local y otros mecanismos de persistencia de sesión. Las sesiones existentes y activas del navegador local se mantienen, asegurando que Manus pueda continuar interactuando con sitios web autenticados a lo largo de una tarea sin necesidad de reautenticación [2]. La transparencia y el control del usuario, con la capacidad de monitorear la actividad en tiempo real y detener la tarea instantáneamente, refuerzan la confianza en este modelo de persistencia de sesión [2].

#### Detalles de Implementación
La implementación técnica de la navegación web en Manus AI se articula a través de dos componentes principales: el Cloud Browser y el Manus Browser Operator, cada uno con sus propias características y mecanismos de operación.

### Cloud Browser

El **Cloud Browser** es un entorno de navegador dedicado que se ejecuta en la infraestructura de la nube de Manus. Aunque no se especifica la tecnología subyacente exacta, la descripción funcional sugiere un modelo similar a los servicios de automatización de navegadores headless. Los detalles de implementación incluyen:

*   **Entornos Aislados:** Cada sesión de usuario en el Cloud Browser se ejecuta en una instancia de navegador virtualizada y aislada. Esto garantiza que las cookies, el almacenamiento local y el estado de la sesión de un usuario no interfieran con los de otro, y que cualquier problema en una sesión no afecte a otras [1].
*   **Cifrado de Sesiones:** Todas las comunicaciones y el estado de la sesión dentro del Cloud Browser están cifrados para proteger la información del usuario y la actividad de navegación [1].
*   **Gestión de Sesiones:** Los usuarios pueden acceder a una interfaz de configuración (Manus Settings → Cloud Browser) para "Logged-in Accounts" y "Session Management". Aquí, pueden ver las sesiones activas, cerrar sesión en cuentas específicas o borrar todas las sesiones. Esto implica la existencia de APIs internas para la manipulación programática de cookies y tokens de sesión asociados a cada instancia de navegador [1].
*   **Mecanismo "Take Over":** Cuando se detecta una verificación compleja (ej. CAPTCHA), el sistema activa una señal para el usuario. Esto podría implementarse mediante un WebSocket o una API de notificación que alerta a la interfaz de usuario de Manus. El usuario, al "tomar el control", interactúa directamente con la vista del navegador (posiblemente a través de un VNC o una transmisión de video interactiva) para resolver el desafío. Una vez resuelto, una señal de "devolver control" permite a Manus reanudar la automatización [1].
*   **Direcciones IP de Centro de Datos:** La asignación de IPs de centros de datos es una característica de implementación que afecta directamente la interacción con sitios web. Esto se gestiona a nivel de infraestructura de red del Cloud Browser [1].

### Manus Browser Operator

El **Manus Browser Operator** es una extensión de navegador que se instala en el navegador local del usuario (actualmente Chrome y Edge). Su implementación se basa en la capacidad de las extensiones de navegador para interactuar con el DOM y las APIs del navegador.

*   **Conector "My Browser":** La activación del Browser Operator se realiza a través de un "Conector" en la configuración de Manus. Esto sugiere una arquitectura de plugin o módulo que se integra con el core de Manus AI [2].
*   **Autorización de Sesión:** Cuando Manus necesita usar el navegador local, solicita una "autorización" explícita al usuario. Esto podría implicar un handshake seguro entre la extensión del navegador y el agente de Manus, donde se establece un canal de comunicación temporal y autorizado. La autorización es de "un solo uso" por tarea, lo que implica que no se mantiene un permiso persistente sin la intervención del usuario [2].
*   **Control del Navegador Local:** La extensión del navegador permite a Manus "operar directamente" dentro del navegador del usuario. Esto se logra mediante la inyección de scripts o el uso de APIs de automatización de extensiones (como `chrome.debugger` o `chrome.automation` para Chrome) que permiten la manipulación del DOM, la simulación de eventos de usuario (clics, escritura) y la lectura del contenido de la página. La actividad se realiza en una "pestaña dedicada" dentro de un "grupo de pestañas" nombrado por la tarea, lo que facilita la visibilidad y el control por parte del usuario [2].
*   **No Almacenamiento de Credenciales:** Un detalle crítico de implementación es que la extensión **no almacena ni transmite las credenciales** del usuario. En su lugar, opera dentro de las sesiones ya establecidas por el usuario en su navegador local. Esto significa que la extensión interactúa con el navegador a un nivel que no requiere acceso directo a contraseñas, sino que utiliza los tokens de sesión y las cookies que el navegador ya tiene [2].
*   **Persistencia de Sesiones:** La persistencia se hereda del propio navegador local. Si el usuario ya tiene una sesión activa en un sitio web, el Browser Operator simplemente la utiliza. No hay un mecanismo de persistencia de sesión separado implementado por la extensión, más allá de la interacción con el navegador existente [2].

#### Comportamientos Observados en Producción
1.  **Activación de Verificaciones por IP de Centro de Datos (Cloud Browser):** Se ha observado que el Cloud Browser de Manus, al utilizar direcciones IP de centros de datos, tiende a activar con mayor frecuencia mecanismos de seguridad como CAPTCHAs, verificaciones de dos factores o bloqueos de acceso en sitios web sensibles o con medidas anti-bot robustas [1]. Esto se alinea con el comportamiento esperado de muchos sistemas de detección de bots que marcan el tráfico no residencial. (Fuente: [1])
2.  **Efectividad del "Take Over" para CAPTCHAs:** El mecanismo de "Take Over" en el Cloud Browser es efectivo para superar CAPTCHAs y otras verificaciones complejas, pero requiere la intervención manual y oportuna del usuario. Si el usuario no responde rápidamente, la tarea puede pausarse o fallar. Este comportamiento subraya que no hay una solución automatizada interna para estos desafíos en el Cloud Browser. (Fuente: [1])
3.  **Bypass de CAPTCHAs con Browser Operator:** El Manus Browser Operator ha demostrado ser altamente efectivo para evitar CAPTCHAs y barreras de login en la mayoría de los sitios web, ya que opera con la dirección IP residencial y las sesiones autenticadas del usuario. La actividad es percibida como legítima, lo que reduce la necesidad de intervención humana para estos desafíos. (Fuente: [2])
4.  **Dificultades con SPAs JavaScript Pesadas:** Se ha documentado que Manus "struggles with JavaScript-heavy single-page apps, sites behind Cloudflare..." [3]. Esto se manifiesta en una posible lentitud en la extracción de datos, fallos en la identificación de elementos o la incapacidad de acceder a contenido que se carga de forma muy dinámica o está protegido por soluciones anti-bot avanzadas. Aunque puede renderizar JavaScript, la complejidad o las medidas de protección pueden superar sus capacidades actuales. (Fuente: [3])
5.  **Visibilidad y Control en Tiempo Real (Browser Operator):** Los usuarios que emplean el Browser Operator observan una pestaña dedicada en su navegador local donde pueden ver en tiempo real las acciones que Manus está realizando. Esta transparencia permite una supervisión directa y la capacidad de "detener instantáneamente" la tarea cerrando la pestaña, lo que es un comportamiento clave para la confianza y el control del usuario. (Fuente: [2])
6.  **Persistencia de Sesiones para Tareas Largas:** Tanto en el Cloud Browser (con sesiones pre-autenticadas) como en el Browser Operator (aprovechando sesiones locales), se observa que Manus mantiene el estado de sesión a lo largo de tareas que implican múltiples interacciones y navegaciones, eliminando la necesidad de reautenticación constante. (Fuente: [1], [2])

#### Fuentes Adicionales
1.  [Manus Documentation: Cloud browser](https://manus.im/docs/features/cloud-browser)
2.  [Manus Documentation: Manus Browser Operator](https://manus.im/docs/integrations/manus-browser-operator)
3.  [Taskade: Manus AI Review 2026: Features, Pricing, 7 Alternatives](https://www.taskade.com/blog/manus-ai-review)
4.  [Medium: Manus Unleashed: Now available for everyone — Why this breakaway AI agent is more than just a chatbot](https://medium.com/aiguys/manus-unleashed-now-available-for-everyone-why-this-breakaway-ai-agent-is-more-than-just-a-8ec6af347bfd)
5.  [AI.PlainEnglish.io: Part 2: Architecture ->Ever Wondered How Manus AI or Browser-use Works?](https://ai.plainenglish.io/part-2-architecture-ever-wondered-how-manus-ai-or-browser-use-works-e08d77ae38de)

## M06 — M06 — Generación y Ejecución de Código

### Descripción Técnica
# M06 — Generación y Ejecución de Código

## Descripción Técnica Completa

El módulo M06 de Manus AI, centrado en la **Generación y Ejecución de Código**, representa una capacidad fundamental que distingue a Manus de otros agentes de IA. A diferencia de los modelos tradicionales que a menudo se limitan a describir acciones o generar llamadas a herramientas predefinidas, Manus implementa un enfoque conocido como **CodeAct**. Esta arquitectura permite al modelo generar directamente código Python ejecutable como su mecanismo de acción principal, transformando al agente de un mero "usuario de herramientas" a un "mini-programador dinámico" capaz de lógica, adaptación y combinación de múltiples fuentes de información [1] [2].

La esencia de CodeAct radica en su capacidad para superar las limitaciones de las llamadas a funciones tradicionales (function calling), que, aunque funcionales para tareas simples, se vuelven frágiles ante problemas complejos y de múltiples pasos. Al permitir que el LLM escriba código Python, Manus aprovecha la vasta potencia de un lenguaje de programación completo, incluyendo bucles, condicionales, variables y un extenso ecosistema de librerías, directamente dentro de su proceso de toma de decisiones y ejecución [1].

### Lenguajes Soportados

Manus AI soporta una **diversa gama de lenguajes de programación**, lo que le confiere la flexibilidad necesaria para proyectos modernos y multi-lenguaje. Los lenguajes primarios y sus casos de uso incluyen [3]:

*   **Python:** Utilizado para análisis de datos, aprendizaje automático, desarrollo backend y scripting general.
*   **JavaScript/Node.js:** Empleado para la creación de interfaces de usuario interactivas y servicios backend escalables.
*   **HTML/CSS:** Fundamentales para la construcción y el estilo de los componentes básicos de cualquier sitio web.
*   **SQL:** Aborda tareas relacionadas con bases de datos, desde el diseño de esquemas hasta la ejecución de consultas complejas.
*   **Shell Scripting:** Permite la automatización de tareas a nivel de sistema y la creación de utilidades de línea de comandos sofisticadas.

### Generación de Código

La generación de código en Manus se inicia a partir de **descripciones en lenguaje natural** proporcionadas por el usuario. El proceso es intuitivo y eficiente, siguiendo un flujo de tres pasos [3]:

1.  **Definición del objetivo de desarrollo:** El usuario describe claramente la tarea en su idioma. Una prompt bien definida es crucial para el éxito, ya sea para un script simple o una aplicación web compleja.
2.  **Provisión de contexto del proyecto (opcional pero recomendado):** A través de la función "Manus Projects", el usuario puede cargar su base de código completa. Esto proporciona a Manus el contexto necesario para generar código consistente con la arquitectura, las convenciones de codificación y el estilo existentes del proyecto.
3.  **Inicio, ejecución y revisión:** Manus crea autónomamente un plan y ejecuta el proceso de desarrollo. El progreso es monitoreado, el código generado es revisado y se proporciona feedback para guiar las iteraciones hasta que los resultados se alineen con las expectativas del usuario.

Manus puede generar una variedad de artefactos de código, incluyendo [3]:

*   **APIs completas en Python:** Con autenticación, integración de bases de datos y documentación, siguiendo las mejores prácticas para aplicaciones web o microservicios.
*   **Pruebas unitarias automatizadas:** Genera suites de pruebas `pytest` exhaustivas para módulos Python, cubriendo operaciones normales, casos extremos, manejo de errores y condiciones de contorno con fixtures y pruebas parametrizadas.
*   **Aplicaciones web full-stack:** Transforma una prompt en lenguaje natural en una aplicación web completamente funcional, con base de datos segura y sistema de autenticación de usuario.
*   **Scripts y herramientas de línea de comandos personalizadas:** Adaptadas a flujos de trabajo de desarrollo específicos.

### Depuración y Optimización

Manus no solo genera código, sino que también asiste en su **depuración y optimización**. Analiza el código existente para identificar y corregir errores, ofrece sugerencias inteligentes para la optimización y refactoriza el código para mejorar el rendimiento, la legibilidad y la mantenibilidad [3].

### Despliegue y Entorno de Ejecución

La ejecución del código generado se realiza en un **entorno de sandbox seguro y aislado** [3]. Este sandbox, a menudo descrito como una "computadora en la nube" o "computadora virtual", permite a Manus ejecutar código no confiable de forma segura, sin afectar otras tareas y con la capacidad de ejecutar procesos en paralelo [4] [5]. La transparencia es clave, ya que Manus permite al usuario ver lo que el sistema hace mientras se ejecuta, facilitando la depuración y el control [6].

### Manejo de Errores de Código

Aunque la documentación explícita sobre el manejo de errores de código por parte de Manus es limitada, se infiere que el proceso de "revisión del código generado" y la capacidad de "identificar y corregir errores" son mecanismos clave. El usuario puede proporcionar feedback para guiar las iteraciones, lo que sugiere un ciclo de retroalimentación para la corrección de errores [3]. La naturaleza del sandbox también implica que los errores de ejecución están contenidos y no afectan el sistema host.

Sin embargo, es crucial destacar que el código generado por Manus, si bien es funcionalmente correcto, no está inherentemente "endurecido" en términos de seguridad. Las aplicaciones construidas con Manus pueden presentar vulnerabilidades comunes como fallas de autenticación (ej. límites de tasa inconsistentes, manejo de sesiones débil), lógica de autorización deficiente (ej. verificaciones de roles inconsistentes, escalada de privilegios horizontal), APIs internas expuestas públicamente sin controles de acceso, y validación de entrada insuficiente. Estos problemas surgen porque Manus se enfoca en los requisitos funcionales y no razona sobre el uso indebido o el comportamiento de un atacante. Las herramientas de seguridad de aplicaciones tradicionales a menudo fallan en detectar estas vulnerabilidades debido a la naturaleza del código generado por IA [8]. La seguridad debe ser una parte integral del pipeline de desarrollo y no una consideración posterior, requiriendo pruebas dinámicas y continuas para validar el comportamiento bajo condiciones adversas [8].

### Integración con GitHub

La integración directa con GitHub no se detalla explícitamente en las fuentes consultadas. Sin embargo, la capacidad de "cargar su base de código completa" a través de "Manus Projects" y la mención de "control de código completo" sugieren que la gestión de versiones y la integración con repositorios externos como GitHub son posibles, probablemente a través de la carga y descarga de archivos o la interacción con la línea de comandos dentro del sandbox [3] [7]. Es importante señalar que, aunque Manus puede generar código, la responsabilidad de la integración segura con sistemas de control de versiones y despliegue recae en el usuario, quien debe asegurar que las prácticas de seguridad se mantengan al transferir el código generado a entornos de producción [8].

### Capacidades de Web Scraping con Código

La capacidad de Manus para realizar **investigación en la web** utilizando un "navegador en la nube" para acceder e interpretar documentación, tutoriales y ejemplos de código en tiempo real [3] implica inherentemente capacidades de web scraping. Aunque no se describe como una función de web scraping explícita, la habilidad de "navegar por la web para API documentation y mejores prácticas" y "aprender sobre nuevas librerías, frameworks y APIs en tiempo real" demuestra que Manus puede interactuar con contenido web y extraer información programáticamente, lo cual es la base del web scraping. Esto se logra mediante la generación de código que interactúa con el navegador y procesa el contenido de las páginas web.

En resumen, el módulo M06 de Manus AI es un sistema robusto y autónomo para la generación y ejecución de código, que utiliza un enfoque CodeAct para traducir intenciones en lenguaje natural en código ejecutable, operando en un entorno seguro y soportando una amplia gama de lenguajes y tareas de desarrollo.

### Capacidades e Implementación
| Capacidad | Implementación | Parámetros/Límites | Comportamiento |
|---|---|---|---|
| **Generación de Código** | Generación de código Python ejecutable a partir de descripciones en lenguaje natural (arquitectura CodeAct). | Prompt en lenguaje natural, contexto del proyecto (opcional). | Transforma la intención del usuario en código funcional, adaptable y consistente con el proyecto. |
| **Lenguajes Soportados** | Soporte para múltiples lenguajes de programación. | Python, JavaScript/Node.js, HTML/CSS, SQL, Shell Scripting. | Flexibilidad para desarrollar en diversos entornos y para diferentes propósitos. |
| **Depuración de Código** | Análisis del código existente para identificar y corregir errores. | Código fuente del proyecto. | Ofrece sugerencias de optimización y refactorización para mejorar rendimiento, legibilidad y mantenibilidad. |
| **Optimización de Código** | Refactorización y mejora del código generado o existente. | Código fuente del proyecto. | Mejora el rendimiento, la legibilidad y la mantenibilidad del código. |
| **Ejecución de Código** | Ejecución de código en un entorno de sandbox seguro y aislado. | Código generado o proporcionado por el usuario. | Ejecución segura y contenida, con capacidad de paralelización y transparencia en el proceso. |
| **Manejo de Errores** | Identificación y corrección de errores mediante feedback del usuario y revisión del código. | Feedback del usuario, revisión del código generado. | Ciclo de retroalimentación para la corrección de errores; errores contenidos en el sandbox. |
| **Integración con Proyectos Existentes** | Carga de bases de código completas a través de "Manus Projects". | Archivos de código fuente del proyecto. | Proporciona a Manus un profundo entendimiento de la estructura, dependencias y convenciones de codificación del proyecto. |
| **Web Scraping (implícito)** | Utilización de un navegador en la nube para acceder e interpretar documentación y ejemplos de código. | URLs, contenido web. | Permite la investigación en tiempo real y la extracción programática de información de la web para generar código actualizado. |

### Limitaciones y Fallas
| Limitación | Severidad | Fuente | Workaround |
|---|---|---|---|
| **Fallas de Autenticación** | Media a Alta | [Bright Security](https://brightsec.com/blog/vulnerabilities-of-coding-with-manus-when-speed-outruns-security/) | Implementación inconsistente de límites de tasa, falta de throttling en mecanismos de restablecimiento de contraseña, manejo de sesiones basado en valores predeterminados no endurecidos, y verificaciones de autenticación solo en la UI sin cumplimiento en el lado del servidor. | Realizar pruebas de seguridad dinámicas (DAST) para validar flujos de autenticación bajo estrés y asegurar que los controles se apliquen en el backend. |
| **Lógica de Autorización Deficiente** | Media a Alta | [Bright Security](https://brightsec.com/blog/vulnerabilities-of-coding-with-manus-when-speed-outruns-security/) | Verificaciones de roles implementadas de manera inconsistente, lo que lleva a escenarios clásicos de escalada de privilegios horizontal donde los usuarios pueden acceder o modificar datos de otros usuarios. | Validar la lógica de autorización en tiempo de ejecución y enfocarse en el comportamiento del sistema bajo condiciones adversas, no solo en la estructura del código. |
| **APIs Internas Expuestas Públicamente** | Media | [Bright Security](https://brightsec.com/blog/vulnerabilities-of-coding-with-manus-when-speed-outruns-security/) | Generación de endpoints de ayuda, APIs internas o rutas de conveniencia que se exponen sin autenticación o controles de acceso adecuados. | Realizar auditorías de seguridad exhaustivas para identificar y proteger todas las APIs, asegurando que solo las intencionadas sean accesibles públicamente y con los controles adecuados. |
| **Validación de Entrada Insuficiente** | Media | [Bright Security](https://brightsec.com/blog/vulnerabilities-of-coding-with-manus-when-speed-outruns-security/) | La validación de entrada a menudo se basa en valores predeterminados del framework o verificaciones simples que fallan cuando las entradas se encadenan, anidan o combinan en múltiples solicitudes. | Implementar validación de entrada robusta y contextual, considerando cómo las entradas pueden ser manipuladas por un atacante y cómo interactúan en diferentes partes del sistema. |
| **Falta de Razonamiento de Seguridad en la IA** | Alta | [Bright Security](https://brightsec.com/blog/vulnerabilities-of-coding-with-manus-when-speed-outruns-security/) | Manus no comprende los resultados de seguridad, solo patrones. No puede razonar sobre cómo un atacante abusará de un sistema o cómo múltiples características interactúan bajo estrés. | La seguridad debe ser parte del pipeline de entrega, no una ocurrencia tardía. Se requieren pruebas continuas y validación por herramientas de seguridad dinámicas. |
| **Dificultad para Herramientas AppSec Tradicionales** | Media | [Bright Security](https://brightsec.com/blog/vulnerabilities-of-coding-with-manus-when-speed-outruns-security/) | Las herramientas de análisis estático y los escáneres basados en firmas luchan con el código generado por IA porque los problemas no están en la sintaxis, sino en el comportamiento y el contexto. | Utilizar herramientas de seguridad dinámicas (DAST) que prueben el comportamiento de la aplicación en tiempo de ejecución bajo condiciones adversas. |

### Ejemplos de Uso Real
1.  **Integración de API:** Andrey Smolyakov solicitó a Manus AI que integrara su reloj Garmin a través de una API. Manus AI solicitó las credenciales de inicio de sesión y completó la integración en 15 minutos sin necesidad de codificación manual [9].
2.  **Análisis de Datos:** Un usuario utilizó Manus AI para analizar los datos de ventas de una cafetería, proporcionando un archivo CSV y un prompt detallado. Manus AI generó un informe de ventas con análisis de productos más vendidos, horas pico y tendencias, aunque se observaron imprecisiones en el análisis de tiempo [10].
3.  **Predicciones Financieras:** Manus AI fue utilizado para analizar la caída del S&P 500 y predecir los tiempos de recuperación, utilizando datos históricos y la API de YahooFinance. Generó un sitio web con diferentes escenarios, análisis de niveles mínimos y plazos de recuperación, incluyendo scripts de Python para la extracción de datos y simulaciones de Monte Carlo [10].
4.  **Recomendación de Productos:** Un usuario en Portugal utilizó Manus AI para investigar y recomendar deshumidificadores para una habitación de 25 metros cuadrados. Manus AI recopiló datos de minoristas locales, organizaciones de reseñas de consumidores, foros y recursos técnicos para generar recomendaciones detalladas [10].
5.  **Búsqueda de Empleo:** Manus AI se utilizó para buscar ofertas de empleo para un ingeniero full-stack, filtrando por título, salario, entorno remoto y pila tecnológica (React y Python), e incluso considerando un área de interés sin experiencia previa (computación cuántica). Se le proporcionó un CV y un prompt detallado [10].
6.  **Creación de Sitios Web:** Zaira Laraib creó un sitio web en solo 27 minutos con Manus AI [9]. Arnold Lakita también construyó un diseño de sitio web utilizando Manus AI [9].
7.  **Generación de Pruebas Unitarias:** Manus AI puede generar suites de pruebas `pytest` exhaustivas para módulos Python, cubriendo operaciones normales, casos extremos, manejo de errores y condiciones de contorno con fixtures y pruebas parametrizadas [3].
8.  **Desarrollo de APIs Backend:** Manus AI puede construir APIs completas en Python con autenticación, integración de bases de datos y documentación, siguiendo las mejores prácticas para aplicaciones web o microservicios [3].


### Hallazgos de Fase 2 (Actualizado 1 Mayo 2026)

#### Nuevos Descubrimientos
La investigación sobre el Módulo M06 de Manus AI, centrado en la generación y ejecución de código, ha revelado hallazgos significativos que cierran los gaps de conocimiento identificados. La arquitectura de Manus se distingue por su enfoque en la **ejecución de código como mecanismo de acción principal**, un paradigma conocido como **CodeAct**, que unifica la interacción con diversas herramientas y entornos.

### 1. Cómo decide Manus entre ejecutar código en el sandbox vs. usar una tool de browser vs. delegar a un sub-agente.

La decisión de Manus sobre el mecanismo de ejecución es intrínseca a su **capa de razonamiento y generación de código**. A diferencia de los agentes que se basan en llamadas a herramientas rígidas, Manus permite que el LLM genere código Python que, a su vez, invoca las capacidades necesarias. Este enfoque proporciona una flexibilidad superior y reduce la "carga cognitiva" del LLM de elegir la herramienta correcta, ya que puede programar la interacción.

*   **Ejecución en Sandbox (CodeAct):** Este es el método preferido para la mayoría de las tareas que requieren lógica programática. El LLM genera código Python que se ejecuta en un **sandbox aislado (microVM)**. Este código puede realizar operaciones de sistema de archivos, cálculos complejos, o invocar otras herramientas internas del sandbox (como `shell` para comandos de sistema o `file` para manipulación de archivos). La ventaja es que el código puede combinar múltiples herramientas o lógica en una sola ejecución, lo que permite una mayor complejidad y eficiencia. Por ejemplo, para un análisis de datos, el LLM generaría código Python que carga datos, los procesa y luego genera una visualización, todo dentro del mismo script ejecutado en el sandbox.

*   **Uso de Herramientas de Navegador (Browser Operator):** Cuando la tarea implica interacción con la web, Manus utiliza un **Browser Operator**. Este no es un navegador externo, sino una herramienta controlada por el agente dentro del sandbox. El LLM genera código que invoca funciones específicas del Browser Operator (ej., `browser_navigate`, `browser_click`, `browser_input`, `browser_view`). Esto permite al agente navegar por sitios web, extraer información, rellenar formularios y automatizar tareas web de manera segura y controlada, utilizando las sesiones de usuario ya autenticadas. La decisión de usar el navegador se toma cuando el plan del LLM identifica que la información o la acción requerida reside en una interfaz web.

*   **Delegación a Sub-agentes:** Para tareas de alta complejidad o multifacéticas, Manus emplea una **arquitectura de orquestación multi-agente**. Un agente orquestador de alto nivel descompone el objetivo principal en subtareas más pequeñas y delega estas a sub-agentes especializados. Cada sub-agente opera en su propio sandbox, lo que permite el procesamiento paralelo y la especialización. Por ejemplo, un sub-agente podría encargarse de la investigación web (usando el Browser Operator), mientras que otro se enfoca en el análisis de datos (generando y ejecutando código Python en el sandbox). La comunicación y coordinación entre sub-agentes se facilita a través de un sistema de **memoria basado en archivos**, donde los resultados de un sub-agente se guardan en el sistema de archivos del sandbox y son accesibles para otros sub-agentes o el orquestador. Esta estrategia es crucial para escalar la complejidad y la robustez de las tareas.

La clave de esta toma de decisiones reside en la capacidad del LLM para **razonar sobre el contexto de la tarea y generar el código más eficiente y seguro** que integre estas diferentes capacidades. El sistema no tiene una lógica de `if/else` rígida para la selección de herramientas, sino que el LLM, a través de su entrenamiento y el contexto proporcionado, "programa" la interacción deseada.

### 2. Qué lenguajes soporta el sandbox además de Python: Node.js, Ruby, Go, Rust, etc.

El sandbox de Manus es un entorno Linux (Ubuntu 22.04) virtualizado que ofrece una gran flexibilidad en cuanto a los lenguajes soportados. Aunque Python es el lenguaje principal para la generación de código por parte del LLM (debido al paradigma CodeAct), el sandbox está configurado para soportar una variedad de otros lenguajes de programación. La documentación oficial y las investigaciones de la comunidad indican que, además de **Python**, el sandbox soporta:

*   **Node.js / JavaScript:** Fundamental para el desarrollo web interactivo y la ejecución de scripts del lado del servidor. El sandbox incluye `node` y `pnpm` preinstalados.
*   **Ruby:** Mencionado en contextos de desarrollo general y automatización.
*   **Go:** Reconocido por su eficiencia y concurrencia, útil para ciertos tipos de servicios o herramientas.
*   **Rust:** Valorizado por su rendimiento y seguridad, aunque su uso por parte del LLM podría ser menos frecuente debido a la complejidad de la generación de código.
*   **PHP, Java, .NET, Bash:** También se mencionan como lenguajes que pueden ser soportados o ejecutados dentro de entornos de sandbox similares, lo que sugiere que Manus podría extender su soporte a estos si fuera necesario, o que el agente puede invocar scripts en estos lenguajes si están disponibles en el entorno.

La capacidad de ejecutar estos lenguajes se debe a que el sandbox es un entorno de computación en la nube completo, similar a una máquina virtual personal, donde se pueden instalar y configurar diferentes runtimes y compiladores. Esto permite a Manus no solo generar código en Python, sino también interactuar con proyectos existentes o generar scripts en otros lenguajes según los requisitos de la tarea.

### 3. Cómo maneja dependencias: ¿instala paquetes pip/npm en cada ejecución? ¿tiene un entorno base preinstalado?

El manejo de dependencias en Manus es un aspecto crítico para la eficiencia y la persistencia del sandbox:

*   **Entorno Base Preinstalado:** El sandbox viene con un conjunto de herramientas y runtimes preinstalados, incluyendo `python3.11`, `pip3`, `node`, y `pnpm`. Esto significa que las dependencias básicas para estos lenguajes ya están disponibles, reduciendo el tiempo de configuración inicial.

*   **Instalación Dinámica de Paquetes:** Manus tiene la capacidad de **instalar paquetes y dependencias en tiempo de ejecución** utilizando los gestores de paquetes estándar (`pip3` para Python, `pnpm` para Node.js). El LLM puede generar comandos de shell (ej., `pip install requests` o `pnpm install express`) para instalar las bibliotecas necesarias para una tarea específica. Esta instalación se realiza dentro del sandbox, asegurando que las dependencias estén disponibles para el código generado.

*   **Persistencia de Dependencias:** Las dependencias instaladas persisten dentro del sandbox mientras este no sea reciclado. Los sandboxes de Manus tienen un ciclo de vida que incluye estados de "sueño" y "despertar". Durante estos ciclos, los archivos y datos (incluyendo las dependencias instaladas) permanecen inalterados. Esto evita la necesidad de reinstalar paquetes en cada ejecución, lo que sería ineficiente. Solo si un sandbox es reciclado (después de 7 días para usuarios gratuitos, 21 días para Manus Pro), se perderán las dependencias instaladas dinámicamente, aunque los artefactos importantes y los archivos cargados se restauran automáticamente en un nuevo sandbox.

*   **Uso de Entornos Virtuales/Docker:** Aunque no se detalla explícitamente, la naturaleza de un sandbox Linux sugiere que el agente puede ser instruido para crear y activar entornos virtuales (ej., `venv` para Python) o incluso utilizar Docker dentro del sandbox para gestionar dependencias de manera más granular y reproducible, especialmente en proyectos complejos.

### 4. Cómo maneja errores de código: ¿cuántos reintentos hace? ¿cómo decide si el error es recuperable?

El manejo de errores de código en Manus es sofisticado y se basa en un ciclo de **observación y refinamiento iterativo**:

*   **Observación de Resultados:** Después de cada ejecución de código en el sandbox, el agente analiza la salida, incluyendo `stdout`, `stderr` y el código de salida. Esto le permite determinar si el código produjo el resultado esperado o si generó un error.

*   **Interpretación Estructurada de Errores:** En lugar de reintentos ciegos, Manus realiza una **interpretación estructurada de los errores**. El LLM es capaz de analizar los mensajes de error (`stderr`) para clasificar el tipo de fallo (ej., error de sintaxis, dependencia faltante, error lógico, error de API) y determinar si es recuperable. Por ejemplo, si el error indica una dependencia faltante, el agente puede generar un comando `pip install` para corregirlo.

*   **Ciclo de Reintento y Modificación:** Si se detecta un error recuperable, el modelo interpreta el error, **modifica el código** (o los comandos de instalación de dependencias, o los parámetros de la herramienta) y lo re-ejecuta. Este ciclo de "razonar-generar-ejecutar-observar-iterar" se repite hasta que la tarea se completa con éxito o se alcanza un límite de reintentos/tiempo.

*   **Límites y Políticas de Recuperación:** Para evitar bucles infinitos o consumo excesivo de recursos, Manus implementa:
    *   **Límites máximos de iteración:** Un número predefinido de reintentos o ciclos de ejecución.
    *   **Límites de tiempo:** Un tiempo máximo asignado para cada ciclo de ejecución o para la tarea completa.
    *   **Presupuestos de tokens y llamadas a herramientas:** Para controlar el costo y la eficiencia del LLM.
    *   **Modelo de "Circuit Breaker":** Aunque no se detalla su implementación específica en Manus, la literatura sobre agentes de IA sugiere el uso de patrones como el "circuit breaker" para manejar fallos persistentes, permitiendo que el agente opere con funcionalidad reducida (estado degradado) en lugar de fallar completamente, o que detenga la ejecución si un error no es recuperable.

*   **Idempotencia:** Se fomenta el diseño de operaciones idempotentes para que los reintentos no causen efectos secundarios duplicados. Esto es crucial para la robustez en entornos de producción.

### 5. Cómo genera código para tareas de web scraping, data analysis y visualización: patrones comunes observados.

La generación de código por parte de Manus para estas tareas sigue patrones bien definidos, aprovechando la flexibilidad de CodeAct:

*   **Web Scraping:**
    *   **Uso de Browser Operator:** Para la interacción con páginas web, el LLM genera código que utiliza las herramientas del Browser Operator (ej., `browser_navigate` para ir a una URL, `browser_view` para obtener el HTML/Markdown, `browser_click` para interactuar con elementos, `browser_input` para rellenar formularios). Esto permite al agente "navegar" y "ver" la web como un humano.
    *   **Bibliotecas Python:** Una vez que el contenido HTML se obtiene (a través de `browser_view` o `shell` con `curl`/`wget`), el LLM genera código Python que utiliza bibliotecas como **BeautifulSoup** o **lxml** para parsear el HTML y extraer datos estructurados. Para sitios más complejos o dinámicos, podría generar código que instale y use **Playwright** o **Selenium** (si están disponibles o se pueden instalar en el sandbox) para un scraping más avanzado que simule la interacción del usuario con JavaScript.
    *   **Patrones:** Identificación de selectores CSS/XPath, manejo de paginación, extracción de tablas, y limpieza de datos.

*   **Data Analysis:**
    *   **Bibliotecas Python:** El LLM genera código Python que utiliza intensivamente bibliotecas como **Pandas** para la manipulación y análisis de datos tabulares, y **NumPy** para operaciones numéricas. Para análisis estadísticos, podría emplear **SciPy** o **Statsmodels**.
    *   **Carga y Preprocesamiento:** Genera código para cargar datos de diversas fuentes (CSV, JSON, bases de datos SQL a través de conectores MCP), limpiar datos (manejo de valores nulos, duplicados, tipos de datos), transformar características y realizar agregaciones.
    *   **Consultas SQL:** Para interactuar con bases de datos, el LLM puede generar consultas SQL directamente, que luego se ejecutan a través de herramientas de shell o conectores MCP. El agente puede incluso refinar estas consultas basándose en los errores de ejecución (ej., columna no encontrada).
    *   **Patrones:** Carga de datos, limpieza, transformación, agregación, cálculo de métricas, filtrado, agrupamiento, y análisis exploratorio de datos.

*   **Visualización:**
    *   **Bibliotecas Python:** El LLM genera código Python que utiliza bibliotecas de visualización como **Matplotlib** y **Seaborn** para gráficos estáticos, y **Plotly** o **Altair** para visualizaciones interactivas. Para casos específicos, podría usar **Folium** para mapas o **NetworkX** para grafos.
    *   **Tipos de Gráficos:** Genera código para crear una amplia gama de gráficos: histogramas, diagramas de dispersión, gráficos de líneas, gráficos de barras, mapas de calor, box plots, etc., seleccionando el tipo de gráfico más adecuado para el tipo de datos y la pregunta de análisis.
    *   **Personalización:** Incluye código para personalizar títulos, etiquetas de ejes, leyendas, colores y estilos para mejorar la claridad y el impacto visual.
    *   **Patrones:** Selección del tipo de gráfico adecuado, preparación de datos para la visualización, generación del código de la biblioteca de visualización, y guardado de la imagen o el archivo HTML resultante.

En todos estos casos, el proceso es iterativo: el agente genera código, lo ejecuta, observa los resultados (ej., un archivo de imagen generado, una tabla de datos procesada, un error de ejecución), y refina el código si es necesario para lograr el objetivo final. La capacidad de generar y ejecutar código en un entorno real es lo que permite a Manus abordar estas tareas de manera autónoma y efectiva.

#### Detalles de Implementación
El núcleo de la ejecución de código en Manus AI se basa en el paradigma **CodeAct**, donde el modelo de lenguaje grande (LLM) genera código Python ejecutable en lugar de llamadas a herramientas predefinidas. Este código se ejecuta dentro de un entorno de sandbox aislado. La arquitectura se divide en tres capas principales:

1.  **Capa de Razonamiento (Planning & Code Generation):** El LLM analiza el prompt del usuario y el estado actual de la tarea. Utiliza su capacidad de razonamiento para planificar los pasos necesarios y, crucialmente, **genera código Python** que encapsula la lógica para lograr el objetivo. Este código puede incluir llamadas a funciones internas del sandbox (como `shell`, `file`, `browser_navigate`, `manus-mcp-cli`) o bibliotecas estándar de Python. La capa de razonamiento **nunca ejecuta código directamente**, solo lo genera.

2.  **Capa de Ejecución (Runtime & Sandbox):** El código Python generado por el LLM se envía a un **sandbox virtualizado (microVM)**. Este sandbox es un entorno Linux (Ubuntu 22.04) completamente aislado que proporciona:
    *   **Aislamiento:** Cada tarea se ejecuta en su propia microVM, garantizando que las acciones de un agente no afecten al sistema anfitrión ni a otras tareas. Se implementa un aislamiento a nivel de hardware (hipervisor) para mayor seguridad.
    *   **Persistencia:** Los archivos generados y cargados por el usuario persisten a través de ciclos de sueño/despertar del sandbox. Sin embargo, los archivos temporales y el código intermedio pueden no restaurarse después de un reciclaje prolongado.
    *   **Herramientas preinstaladas:** Incluye `python3.11`, `pip3`, `node`, `pnpm`, `gh`, `gws`, `manus-mcp-cli`, y herramientas de navegador. Las dependencias se gestionan mediante `pip3` o `pnpm` dentro del sandbox, permitiendo la instalación de paquetes en tiempo de ejecución.
    *   **Control de recursos:** Se aplican límites de CPU, memoria y tiempo de ejecución para prevenir el consumo excesivo de recursos y la ejecución descontrolada.
    *   **Interfaz estandarizada:** Un método `execute()` para comandos de shell captura `stdout`, `stderr`, códigos de salida y avisos de truncamiento.

3.  **Capa de Integración (Tool Calling & External Systems):** Esta capa gestiona la interacción del código ejecutado en el sandbox con herramientas externas y APIs. El **Model Context Protocol (MCP)** es un estándar clave que permite a Manus acceder a servicios externos (como Asana, Notion, PayPal, Gmail, Google Calendar, Outlook Mail) de manera estandarizada. El código generado por el LLM puede invocar herramientas MCP a través de `manus-mcp-cli` dentro del sandbox. El `Browser Operator` de Manus es una herramienta especializada que permite al agente interactuar con navegadores web, simulando acciones de usuario para tareas de web scraping o automatización de UI.

**Decisión de Ejecución:**
La decisión sobre qué mecanismo usar (sandbox, herramienta de navegador, sub-agente) se integra en el proceso de planificación y generación de código del LLM:

*   **Ejecución en Sandbox (CodeAct):** Es el mecanismo por defecto para tareas que requieren lógica programática, manipulación de archivos, análisis de datos, o interacción con el sistema operativo. El LLM genera código Python que se ejecuta directamente en el sandbox. Este código puede, a su vez, invocar herramientas internas (como las herramientas `shell` o `file`) o herramientas externas a través de `manus-mcp-cli`.
*   **Herramienta de Navegador (Browser Operator):** Cuando la tarea implica interacción con interfaces web (navegación, clics, entrada de texto, extracción de datos de páginas HTML), el LLM genera código que utiliza las herramientas del navegador (`browser_navigate`, `browser_view`, `browser_click`, `browser_input`, etc.). Estas herramientas se ejecutan en un entorno de navegador controlado dentro del sandbox.
*   **Delegación a Sub-agentes:** Para tareas complejas y multifacéticas, Manus utiliza una arquitectura de orquestación multi-agente. Un orquestador de alto nivel descompone la tarea en subtareas y delega a sub-agentes especializados. Cada sub-agente opera en su propio sandbox y puede emplear CodeAct o herramientas de navegador según sea necesario. La comunicación entre sub-agentes se realiza a través de un sistema de memoria basado en archivos, donde los resultados de un sub-agente se guardan y se utilizan como entrada para otro.

En esencia, el LLM de Manus decide el camino de ejecución al generar el código más apropiado para la tarea, aprovechando la flexibilidad de CodeAct para integrar diferentes capacidades (sandbox, navegador, MCP) y la orquestación de sub-agentes para la complejidad.

#### Comportamientos Observados en Producción
1.  **"El modelo describe lo que haría en lugar de hacerlo":** Un comportamiento común en agentes de IA es que el LLM genera descripciones en lenguaje natural de los pasos a seguir en lugar de ejecutar acciones reales. Manus aborda esto mediante el paradigma CodeAct, donde el modelo genera código ejecutable, forzándolo a "hacer" en lugar de solo "describir". (Fuente: `https://medium.com/@pankaj_pandey/inside-manus-the-architecture-that-replaced-tool-calls-with-executable-code-d89e1caea678`)
2.  **"Fallos en la ejecución de código por permisos o salvaguardas":** Se ha observado que los agentes pueden generar código Python válido, pero fallar en la ejecución debido a permisos insuficientes o salvaguardas de infraestructura. Esto resalta la importancia de la capa de ejecución aislada y la gestión de permisos. (Fuente: `https://blaxel.ai/blog/how-do-ai-agents-execute-code`)
3.  **"Reducción del uso de tokens con carga dinámica de herramientas":** El equipo de ingeniería de Anthropic (mencionado en el contexto de agentes de IA similares a Manus) descubrió que la carga dinámica de definiciones de herramientas reduce el uso de tokens en un 85% en comparación con la carga de todas las definiciones al inicio. Esto es relevante para la eficiencia del LLM en Manus. (Fuente: `https://blaxel.ai/blog/how-do-ai-agents-execute-code`)
4.  **"Grandes salidas de comandos guardadas en archivos":** Para evitar el desbordamiento de la ventana de contexto del LLM, las grandes salidas de comandos generadas en el sandbox se guardan automáticamente en archivos. (Fuente: `https://blaxel.ai/blog/how-do-ai-agents-execute-code`)
5.  **"Costos de inicio en frío vs. inicio en caliente":** Las mediciones de producción de Google Cloud (relevantes para entornos de sandbox) muestran que los inicios en frío de entornos de ejecución pueden ser significativamente más lentos (4,700 ms) que los inicios en caliente (400 ms). Las plataformas de sandbox perpetuo como Blaxel (y por extensión, Manus) buscan reducir este tiempo a menos de 25 ms para mejorar la capacidad de respuesta. (Fuente: `https://blaxel.ai/blog/how-do-ai-agents-execute-code`)
6.  **"Latencia compuesta en bucles de ejecución":** Pequeños retrasos en cada paso de un bucle de ejecución (razonamiento, ejecución, llamada a herramientas) se acumulan, afectando la percepción del usuario. La optimización holística es necesaria para mejorar la velocidad. (Fuente: `https://blaxel.ai/blog/how-do-ai-agents-execute-code`)
7.  **"Reintentos ciegos vs. interpretación de errores":** La interpretación estructurada de los mensajes de error (`stderr`) supera a los reintentos ciegos. El agente clasifica los tipos de error y elige rutas de recuperación específicas. (Fuente: `https://blaxel.ai/blog/how-do-ai-agents-execute-code`)
8.  **"Persistencia de archivos en el sandbox":** Los archivos creados y cargados por Manus persisten a través de los ciclos de sueño/despertar del sandbox, pero los archivos temporales y el código intermedio no se restauran después de un reciclaje prolongado. (Fuente: `https://manus.im/blog/manus-sandbox`)
9.  **"Acceso a sesiones autenticadas del usuario":** El Browser Operator de Manus puede utilizar las sesiones de navegador ya autenticadas del usuario para realizar acciones en plataformas premium o sistemas CRM. (Fuente: `https://manus.im/features/manus-browser-operator`)
10. **"Invocación dinámica de múltiples modelos":** Manus puede invocar dinámicamente múltiples modelos (ej., Claude 3, GPT-4, Gemini) para diferentes subtareas, aprovechando las fortalezas específicas de cada uno. (Fuente: `https://gist.github.com/renschni/4fbc70b31bad8dd57f3370239dccd58f`)
11. **"Aislamiento de microVM para seguridad":** Se observa que las microVMs proporcionan una capa de defensa en profundidad superior a los contenedores, ya que colocan un límite de hipervisor de hardware entre el invitado y el anfitrión, previniendo el movimiento lateral incluso si un atacante obtiene acceso root dentro de la microVM. (Fuente: `https://blaxel.ai/blog/how-do-ai-agents-execute-code`)
12. **"APM (Agent Package Manager) para dependencias":** Aunque no es específico de Manus, la comunidad de agentes de IA está desarrollando soluciones como APM (Microsoft) para gestionar dependencias de agentes de manera reproducible, similar a `package.json` o `requirements.txt`. Esto sugiere una necesidad y un patrón emergente en el ecosistema. (Fuente: `https://github.com/microsoft/apm`)
13. **"La capa de razonamiento nunca ejecuta código directamente":** Un comportamiento arquitectónico crítico es que la capa de razonamiento del LLM solo produce instrucciones y nunca ejecuta código directamente, manteniendo una separación de responsabilidades y seguridad. (Fuente: `https://blaxel.ai/blog/how-do-ai-agents-execute-code`)
14. **"El MCP como contrato de acceso a herramientas":** El Model Context Protocol (MCP) se observa como un mecanismo para estandarizar las definiciones de herramientas y separar las herramientas ejecutables de los recursos de solo lectura, facilitando la revisión de seguridad y la gestión de integraciones. (Fuente: `https://blaxel.ai/blog/how-do-ai-agents-execute-code`)
15. **"Code Mode en Blaxel (similar a Manus) permite interactuar con MCP a través de código":** En plataformas como Blaxel, el "Code Mode" permite a los agentes interactuar con servidores MCP a través de código en lugar de llamadas directas a herramientas, usando la ejecución de código para orquestar el acceso a herramientas de manera más eficiente. Este patrón es altamente probable en Manus dada su filosofía CodeAct. (Fuente: `https://blaxel.ai/blog/how-do-ai-agents-execute-code`)

#### Fuentes Adicionales
1.  `https://medium.com/@pankaj_pandey/inside-manus-the-architecture-that-replaced-tool-calls-with-executable-code-d89e1caea678`
2.  `https://blaxel.ai/blog/how-do-ai-agents-execute-code`
3.  `https://manus.im/playbook/code-generator`
4.  `https://manus.im/blog/manus-sandbox`
5.  `https://gist.github.com/renschni/4fbc70b31bad8dd57f3370239dccd58f`
6.  `https://manus.im/features/manus-browser-operator`
7.  `https://github.com/microsoft/apm`

## M07 — M07 — Agent Skills y Connectors

### Descripción Técnica
# M07 — Agent Skills y Connectors

## Descripción Técnica Completa

El módulo M07 de Manus AI, denominado "Agent Skills y Connectors", representa un pilar fundamental en la arquitectura de la plataforma, permitiendo a los agentes de IA extender sus capacidades y interactuar con el mundo exterior de manera modular y eficiente. Este módulo se compone principalmente de dos elementos interconectados: los **Agent Skills** y los **Connectors**, incluyendo los **MCP Connectors** y la posibilidad de crear **Custom MCP Servers**.

### Agent Skills: El Estándar Abierto para la Especialización de Agentes

Los Agent Skills son recursos modulares basados en el sistema de archivos que encapsulan una capacidad o flujo de trabajo específico. Lanzados en enero de 2026 [7], representan una "guía de incorporación" detallada que se proporciona a un agente de Manus, permitiéndole realizar tareas especializadas con precisión y consistencia. Al cargar un Skill, el agente recibe el contexto necesario, el conocimiento procedimental y las herramientas para sobresalir en un área particular, desde el análisis financiero hasta la creación de contenido de marca. Manus AI ha integrado completamente el estándar abierto Agent Skills, originado por Anthropic y lanzado como estándar abierto en diciembre de 2025 [3] [4] [5] [6] [8] [9] [23] [24] [25] [26], lo que subraya un compromiso con la interoperabilidad y la portabilidad.

Las ventajas principales de utilizar Skills son:

*   **Especialización**: Permiten personalizar las capacidades del agente para dominios específicos, adaptando su conocimiento y comportamiento a necesidades únicas.
*   **Reutilización**: Un flujo de trabajo exitoso puede ser capturado una vez y reutilizado en múltiples sesiones y proyectos, asegurando resultados consistentes y ahorrando tiempo. El estándar abierto facilita la portabilidad de estos Skills entre diferentes plataformas.
*   **Componibilidad**: Múltiples Skills pueden combinarse para construir flujos de trabajo automatizados potentes, capaces de manejar procesos complejos de varios pasos.

La estructura de un Skill se basa en un archivo `SKILL.md` que contiene las instrucciones principales, y puede incluir scripts asociados y otros recursos [1] [5] [6]. Manus implementa un mecanismo de "Divulgación Progresiva" para la eficiencia, donde el agente carga la información solo cuando la necesita, preservando la ventana de contexto [1] [36]. Esto se estructura en tres niveles:

1.  **Nivel 1: Metadatos**: Nombre y descripción del Skill, cargados al inicio con un costo de contexto extremadamente bajo (aproximadamente 100 tokens por Skill).
2.  **Nivel 2: Instrucciones**: Contenido principal del archivo `SKILL.md`, cargado cuando el Skill se activa mediante un comando de barra (`/`) en el chat. El costo de contexto es moderado (menos de 5k tokens).
3.  **Nivel 3: Recursos**: Scripts asociados, archivos de referencia y otros activos, cargados bajo demanda solo cuando se referencian en las instrucciones. El costo de contexto se consume solo cuando se utilizan.

La creación de Skills personalizados se puede realizar de varias maneras: "Build with Manus" (crear un Skill a partir de una interacción exitosa), "Upload a skill" (subir un archivo .zip, .skill o una carpeta local), "Add from official" (explorar una biblioteca curada por el equipo de Manus) e "Import from GitHub" (importar directamente desde un repositorio de GitHub) [1]. Es crucial verificar los Skills de la comunidad antes de usarlos, ya que pueden contener código y comandos de shell. Manus ofrece una funcionalidad para auditar Skills, analizando su archivo `SKILL.md` y scripts asociados para identificar riesgos de seguridad [1] [12] [13] [30] [31].

### Connectors: La Capa de Integración con Herramientas Externas

Los Connectors son la capa de integración que permite a Manus interactuar con herramientas y servicios externos como Gmail, Notion, Stripe, Slack, Google Calendar, GitHub, Google Drive, entre otros [2] [18] [28] [29]. Transforman a Manus de un asistente de IA independiente en una capa de orquestación central para el espacio de trabajo digital del usuario. Un solo prompt puede desencadenar acciones en múltiples aplicaciones, eliminando la necesidad de cambiar constantemente entre herramientas y transferir información manualmente.

Existen varios tipos de integraciones:

*   **MCP Connectors (Model Context Protocol)**: Son integraciones preconstruidas con herramientas y servicios populares. Permiten a Manus acceder a datos y realizar acciones dentro de las aplicaciones conectadas utilizando autenticación OAuth. Ejemplos incluyen Gmail, Notion, Stripe, HubSpot, Slack, Google Calendar, Hugging Face, Google Drive y GitHub [2]. Sus casos de uso abarcan flujos de trabajo multi-aplicación, sincronización automatizada de datos y ejecución de tareas multiplataforma.

*   **Custom MCP Servers**: Para organizaciones con herramientas internas o requisitos especializados, Manus permite construir servidores MCP personalizados. Esto posibilita la integración con sistemas propietarios, APIs internas o servicios de terceros no cubiertos por los conectores preconstruidos [2]. Los casos de uso incluyen sistemas CRM internos, bases de datos personalizadas y APIs empresariales especializadas.

*   **Integración con Zapier**: Permite conectar Manus a miles de aplicaciones a través de Zapier, habilitando flujos de trabajo automatizados que se activan en función de eventos en las herramientas conectadas [2]. Esto es útil para informes automatizados, creación de tareas basada en eventos y notificaciones multiplataforma.

*   **Integración con Slack**: Permite recibir notificaciones, actualizaciones y resultados de Manus directamente en los canales de equipo de Slack, facilitando la colaboración [2].

*   **Manus API**: Acceso programático a Manus, permitiendo construir aplicaciones personalizadas, automatizar flujos de trabajo e integrar Manus en sistemas de software propios [2].

*   **Fuentes de Datos**: Acceso a APIs de datos de terceros premium integradas en Manus, lo que permite el enriquecimiento de datos en tiempo real sin gestionar claves API adicionales [2].

La seguridad y los permisos son gestionados mediante métodos de autenticación seguros (OAuth 2.0 o claves API), y Manus solo accede a los datos explícitamente autorizados por el usuario, utilizándolos únicamente para completar las tareas solicitadas [2]. Las conexiones de integración son personales para la cuenta del usuario y no se comparten con otros a menos que se colabore explícitamente en una tarea.

En resumen, el módulo M07, a través de Agent Skills y Connectors, dota a Manus AI de una capacidad sin precedentes para la especialización, la automatización y la integración con el ecosistema digital existente, permitiendo la creación de flujos de trabajo altamente personalizados y eficientes.

### Capacidades e Implementación
Capacidad | Implementación | Parámetros/Límites | Comportamiento
---|---|---|---
**Especialización de Agentes (Agent Skills)** | Archivos `SKILL.md` con instrucciones, scripts y recursos. Estándar abierto de Anthropic. | Nivel 1: Metadatos (~100 tokens). Nivel 2: Instrucciones (<5k tokens). Nivel 3: Recursos (cargados bajo demanda). | Permite al agente realizar tareas especializadas con precisión y consistencia, adaptando su conocimiento y comportamiento a necesidades únicas.
**Reutilización de Workflows** | Captura de flujos de trabajo exitosos como Skills. Portabilidad entre plataformas gracias al estándar abierto. | No especificado, pero implica la capacidad de guardar y cargar Skills. | Asegura resultados consistentes y ahorro de tiempo al reutilizar procesos en múltiples sesiones y proyectos.
**Componibilidad de Skills** | Combinación de múltiples Skills para construir flujos de trabajo automatizados. | No especificado, pero implica la capacidad de encadenar Skills. | Permite manejar procesos complejos de varios pasos mediante la orquestación de diferentes capacidades.
**Creación de Skills Personalizados** | "Build with Manus" (a partir de interacción), "Upload a skill" (ZIP, .skill, carpeta), "Add from official" (biblioteca curada), "Import from GitHub" (repositorio). | Formato de archivo `SKILL.md` y scripts asociados. | Facilita la expansión de las capacidades del agente por parte del usuario o la comunidad.
**Verificación de Skills de la Comunidad** | Funcionalidad de auditoría de Skills: análisis de `SKILL.md` y scripts asociados. | No especificado, pero implica un análisis de código y contenido. | Identifica riesgos de seguridad y explica la funcionalidad de Skills de terceros antes de su uso.
**Integración con Herramientas Externas (Connectors)** | Capa de integración que permite a Manus interactuar con servicios externos. | OAuth 2.0 o claves API para autenticación. | Transforma a Manus en una capa de orquestación central para el espacio de trabajo digital, ejecutando acciones en múltiples aplicaciones.
**MCP Connectors Preconstruidos** | Integraciones preconstruidas con herramientas populares (Gmail, Notion, Stripe, Slack, Google Calendar, GitHub, Google Drive, HubSpot, Hugging Face). | Autenticación OAuth. | Acceso a datos y ejecución de acciones en aplicaciones conectadas para flujos de trabajo multi-app, sincronización y ejecución de tareas multiplataforma.
**Custom MCP Servers** | Soporte para construir integraciones con sistemas propietarios, APIs internas o servicios de terceros. | Requiere desarrollo de un servidor MCP personalizado. | Permite integrar Manus con herramientas internas o especializadas no cubiertas por los conectores preconstruidos.
**Integración con Zapier** | Conexión a miles de aplicaciones a través de Zapier. | Requiere una cuenta de Zapier y configuración de Zaps. | Habilita flujos de trabajo automatizados que se activan por eventos, informes automatizados, creación de tareas y notificaciones.
**Integración con Slack** | Envío de notificaciones, actualizaciones y resultados de Manus a canales de Slack. | Requiere configuración de la integración de Slack. | Facilita la colaboración en equipo y la compartición de resultados.
**Manus API** | Acceso programático a Manus. | Requiere claves API y conocimiento de la API de Manus. | Permite construir aplicaciones personalizadas, automatizar flujos de trabajo e integrar Manus en sistemas de software propios.
**Fuentes de Datos Premium** | Acceso a APIs de datos de terceros integradas. | No especificado, pero implica suscripciones o acuerdos con proveedores de datos. | Enriquecimiento de datos en tiempo real para análisis financiero, investigación de mercado, etc., sin gestionar claves API adicionales.

### Limitaciones y Fallas
Limitación | Severidad | Fuente | Workaround
---|---|---|---
**Riesgos de Seguridad en Skills de la Comunidad** | Alta | Estudios de seguridad (ej. Snyk ToxicSkills, arXiv:2601.10338) | Verificación manual o asistida por Manus del `SKILL.md` y scripts asociados antes de su uso. Auditar el contenido para identificar vulnerabilidades como inyección de prompts.
**Falta de Integración de Feedback Visual (GUI)** | Moderada | Artículo de Medium sobre limitaciones de Manus AI | No se especifica un workaround directo, pero implica que Manus no tiene capacidades nativas de visión por computadora para interpretar elementos de la pantalla de forma autónoma.
**Comportamiento Frágil/Sobre-generalizado por Contexto Repetitivo** | Moderada | Artículo de Medium sobre ingeniería de contexto de agentes | Inyectar variación estructurada en el contexto para evitar que el agente desarrolle un comportamiento rígido o sobre-generalizado.
**Dependencia de la Calidad del Skill** | Moderada | Inherente al concepto de Skills | La efectividad del agente depende directamente de la calidad y el detalle de las instrucciones y recursos encapsulados en el Skill.
**Costo de Contexto (Tokens) para Skills** | Baja a Moderada | Documentación oficial de Manus Skills | La "Divulgación Progresiva" mitiga este problema, cargando solo la información necesaria en cada nivel (metadatos, instrucciones, recursos). Sin embargo, Skills muy complejos pueden consumir más tokens.
**Curva de Aprendizaje para Custom MCP Servers** | Moderada | Implícito en la necesidad de desarrollar integraciones personalizadas | Requiere conocimientos técnicos para construir y mantener integraciones con sistemas propietarios o APIs internas.

### Ejemplos de Uso Real
1.  **Automatización de Marketing Digital**: Un usuario crea un Skill personalizado para generar contenido de marketing. Este Skill utiliza Connectors para acceder a datos de campañas anteriores (Google Drive), redactar textos publicitarios (integración con LLM), programar publicaciones en redes sociales (Slack Connector) y enviar informes de rendimiento por correo electrónico (Gmail Connector). (Fuente: Adaptado de https://medium.com/@usamabajwa86/from-fiction-to-function-20-real-world-applications-of-manus-ai-e426dadf3ab1)
2.  **Análisis Financiero y Generación de Informes**: Un analista financiero utiliza un Skill para analizar el rendimiento de acciones. El Skill se conecta a fuentes de datos premium (Data Sources) para obtener cotizaciones en tiempo real, realiza análisis estadísticos y genera un informe detallado en Notion (Notion Connector), que luego se comparte con el equipo a través de Slack. (Fuente: Adaptado de https://medium.com/@tahirbalarabe2/manus-ai-ai-agent-use-cases-and-benchmarks-81e07d151c50)
3.  **Gestión de Proyectos y Tareas**: Un gerente de proyecto configura un Skill para automatizar la creación y asignación de tareas. Cuando se recibe un correo electrónico con una solicitud de proyecto (Gmail Connector), el Skill extrae la información clave, crea una nueva tarea en Asana (Asana Connector, mencionado en la descripción del MCP), y notifica al equipo relevante. (Fuente: Adaptado de https://manus.im/blog/projects-connectors)
4.  **Investigación de Mercado Automatizada**: Un Skill de "Investigación de Mercado" guía a Manus AI para usar la herramienta del navegador para visitar sitios web de la competencia, recopilar datos de precios y características de productos, y consolidar esta información en un documento de Google Docs (Google Drive Connector). (Fuente: https://manus.im/es/blog/manus-skills)
5.  **Creación de Sitios Web y Aplicaciones sin Código**: Usuarios sin conocimientos de programación pueden utilizar Skills predefinidos o personalizados para generar sitios web y aplicaciones a partir de una descripción, utilizando Connectors para integrar bases de datos o servicios de terceros. (Fuente: https://www.youtube.com/watch?v=-5DylM1EdI4)
6.  **Automatización de Procesos de RRHH**: Un Skill puede automatizar el proceso de incorporación de nuevos empleados. Utiliza un Connector para acceder a la base de datos de RRHH, envía correos electrónicos de bienvenida (Gmail Connector), crea cuentas en sistemas internos y programa reuniones de introducción (Google Calendar Connector). (Fuente: Adaptado de la descripción general de Connectors)
7.  **Soporte al Cliente Inteligente**: Un Skill de soporte al cliente puede integrarse con un sistema de tickets (Custom MCP Server) para responder preguntas frecuentes, escalar problemas complejos a agentes humanos y registrar interacciones en el CRM. (Fuente: Adaptado de la descripción general de Connectors y Custom MCP Servers)
8.  **Generación de Contenido Branded**: Un Skill especializado en la creación de contenido de marca puede asegurar que todo el material generado (textos, imágenes) cumpla con las directrices de la marca, utilizando recursos de marca almacenados en Google Drive y publicando directamente en plataformas de marketing a través de Connectors. (Fuente: Adaptado de la descripción de Agent Skills)


### Hallazgos de Fase 2 (Actualizado 1 Mayo 2026)

#### Nuevos Descubrimientos
La investigación exhaustiva del módulo M07 de Manus AI ha revelado detalles técnicos profundos sobre el funcionamiento interno de los Connectors y los Agent Skills, cerrando los gaps de conocimiento identificados.

### 1. Funcionamiento Interno de los Connectors (MCP)

Los Connectors de Manus AI están construidos sobre el estándar abierto **Model Context Protocol (MCP)**. Este protocolo permite a Manus actuar como una capa de orquestación central que lee datos y ejecuta acciones en herramientas externas.

**Autenticación y Gestión de Tokens (OAuth 2.0):**
Los Connectors utilizan predominantemente **OAuth 2.0** para establecer conexiones seguras con plataformas de terceros (como Google Workspace, Notion, Slack, GitHub, etc.). 
- **Almacenamiento de Tokens:** Los tokens de acceso y actualización no se almacenan en texto plano en el entorno del agente. Manus utiliza una arquitectura de bóveda segura (Vault), gestionada a través de integraciones como Logto, para almacenar de forma segura los tokens de API de terceros. Esto garantiza que el agente pueda acceder a los servicios externos sin comprometer las credenciales del usuario. En el caso de conexiones a repositorios de GitHub o bases de datos específicas, se utilizan Personal Access Tokens (PAT) que se configuran a nivel de integración.
- **Manejo de Expiración de Tokens:** Un desafío común en tareas de larga duración es la expiración del token OAuth a mitad de la ejecución. Manus implementa un mecanismo de proxy para las llamadas a las herramientas MCP. Antes de reenviar una solicitud a un servicio externo, el proxy verifica la validez del token. Si el token ha expirado, el sistema intenta realizar un **silent refresh** (actualización silenciosa) utilizando el *refresh token* almacenado en la bóveda. Si la actualización silenciosa falla (por ejemplo, si el refresh token ha sido revocado), la tarea se pausa y el sistema solicita al usuario que reautorice la conexión, evitando que la tarea falle abruptamente y consuma créditos innecesariamente.

**Connectors Disponibles y Capacidades:**
Actualmente, Manus ofrece conectores preconstruidos para varias categorías:
- **Productividad:** Gmail (búsqueda de correos, lectura de adjuntos, redacción de borradores), Google Calendar (lectura y creación de eventos), Google Drive (lectura y escritura de archivos), Notion (lectura de bases de datos, creación y actualización de páginas).
- **Negocios y CRM:** HubSpot (actualización de estados de tratos, lectura de notas), Stripe (extracción de datos de transacciones e ingresos).
- **Desarrollo:** GitHub (clonación de repositorios, lectura de issues, creación de PRs), Hugging Face.
Además, Manus soporta la creación de **Custom MCP Servers**, permitiendo a las empresas conectar sistemas internos propietarios, bases de datos heredadas o servicios especializados mediante la exposición de endpoints HTTPS que implementan el protocolo MCP (Tools, Resources y Prompts).

### 2. Funcionamiento de los Agent Skills

Los Agent Skills son el mecanismo mediante el cual Manus adquiere conocimiento procedimental especializado, transformándose de un agente de propósito general a un experto en dominios específicos.

**Formato del Archivo de Skill:**
Un Skill no es un simple prompt, sino un paquete modular basado en el sistema de archivos. La estructura central es el archivo **`SKILL.md`**, que sigue una especificación estandarizada:
- **Frontmatter YAML:** Contiene los campos obligatorios `name` y `description`. Esta es la única parte que el agente lee constantemente para determinar si debe activar el Skill. La descripción debe ser extremadamente precisa sobre *qué* hace el Skill y *cuándo* usarlo.
- **Cuerpo Markdown:** Contiene las instrucciones detalladas, heurísticas y flujos de trabajo. Solo se carga en el contexto cuando el Skill se activa.
- **Recursos Empaquetados (Bundled Resources):** Directorios opcionales como `scripts/` (código ejecutable en Python/Bash), `references/` (documentación extensa cargada bajo demanda) y `templates/` (plantillas de salida).

**Instalación e Invocación:**
- **Instalación:** Los Skills se pueden instalar de varias formas: construyéndolos directamente desde una interacción exitosa con Manus, subiendo un archivo `.zip` o `.skill`, importándolos desde un repositorio de GitHub, o añadiéndolos desde la biblioteca oficial.
- **Invocación:** El agente invoca un Skill automáticamente cuando la solicitud del usuario coincide con la descripción en el frontmatter del `SKILL.md`. Alternativamente, el usuario puede forzar la invocación utilizando un comando de barra diagonal (ej. `/nombre-del-skill`) en el chat.
- **Eficiencia (Progressive Disclosure):** Para conservar la ventana de contexto (que es un recurso crítico y costoso), Manus utiliza un sistema de carga de tres niveles. Solo los metadatos están siempre en contexto. El cuerpo del `SKILL.md` se carga al activarse, y los recursos adicionales (como scripts o referencias largas) se leen o ejecutan solo cuando el flujo de trabajo lo requiere explícitamente.

### 3. Diferencia Técnica entre Connectors y Agent Skills

Aunque ambos extienden las capacidades de Manus, operan en capas arquitectónicas completamente diferentes y sirven a propósitos distintos:

- **Connectors (MCP):** Son la **capa de integración de datos y acciones**. Proporcionan las "tuberías" (pipelines) estandarizadas para que Manus pueda comunicarse con el mundo exterior (leer un correo, actualizar un ticket, consultar una base de datos). No le dicen a Manus *qué* hacer con esos datos, solo le dan la *capacidad* de acceder a ellos y modificarlos.
- **Agent Skills:** Son la **capa de lógica de negocio y conocimiento procedimental**. Proporcionan los "manuales de operación" o flujos de trabajo. Un Skill le dice a Manus *cómo* realizar una tarea compleja paso a paso.

**Cuándo usar cada uno:**
- **Usa un Connector** cuando necesites que Manus interactúe con una nueva herramienta de software, lea datos de una API externa o realice acciones en un sistema de terceros (ej. "Necesito que Manus pueda leer mis tickets de Jira").
- **Usa un Agent Skill** cuando necesites enseñar a Manus un proceso repetitivo, una metodología específica de tu empresa o un flujo de trabajo complejo que requiere heurísticas particulares (ej. "Necesito que Manus sepa cómo redactar un reporte de QA siguiendo el formato exacto de mi empresa, utilizando un script de Python para procesar los datos primero").
- **Sinergia:** En la práctica, se combinan. Un **Skill** (el manual de instrucciones) a menudo instruye al agente sobre cómo utilizar múltiples **Connectors** (las herramientas) para lograr un objetivo complejo, como leer correos de Gmail (Connector), extraer datos, y crear tareas de seguimiento en Notion (Connector) siguiendo una lógica de priorización específica (Skill).

#### Detalles de Implementación
### 1. Implementación de Connectors (MCP)

Los Connectors de Manus AI se basan en el **Model Context Protocol (MCP)**, un estándar abierto que permite a los agentes de IA conectarse a herramientas y fuentes de datos externas. 

**Arquitectura y Protocolo:**
Un servidor MCP personalizado actúa como puente entre Manus y los sistemas internos. Implementa un protocolo estandarizado que define:
- **Tools (Herramientas):** Acciones que Manus puede realizar (ej. `get_customer_data`, `update_project_status`).
- **Resources (Recursos):** Datos que Manus puede leer (ej. documentos, registros, archivos).
- **Prompts:** Plantillas predefinidas para operaciones comunes.

**Autenticación y Almacenamiento de Tokens:**
Los Connectors utilizan **OAuth 2.0** para la autenticación con servicios de terceros (como Gmail, Google Drive, Notion, etc.). 
- **Almacenamiento:** Los tokens de API de terceros se almacenan de forma segura utilizando un sistema de bóveda (Vault) integrado, como se menciona en la integración con Logto, que permite el acceso seguro del agente a servicios externos sin exponer las credenciales directamente en el entorno de ejecución.
- **Manejo de Expiración:** Cada registro OAuth está configurado con un tiempo de expiración del token (típicamente de 30 minutos a 1 mes). El sistema incluye un proxy que verifica la expiración del token antes de reenviar las llamadas a las herramientas. Si el token está a punto de expirar o ha expirado, el sistema intenta una actualización silenciosa (silent refresh) utilizando el *refresh token* almacenado antes de recurrir a solicitar una nueva autorización al usuario.

**Ejemplo de Implementación de Servidor MCP Personalizado (Pseudocódigo):**
```python
# Definición de herramientas expuestas al agente
@mcp_tool(name="get_customer_info", description="Retrieve customer details")
def get_customer_info(customer_id: str):
    # Lógica para consultar la base de datos interna
    return db.query("SELECT * FROM customers WHERE id = ?", customer_id)

@mcp_tool(name="update_customer_notes", description="Add notes to customer record")
def update_customer_notes(customer_id: str, notes: str):
    # Lógica para actualizar el registro
    db.execute("UPDATE customers SET notes = ? WHERE id = ?", notes, customer_id)
    return {"status": "success"}
```

### 2. Implementación de Agent Skills

Los Agent Skills son recursos modulares basados en el sistema de archivos que encapsulan capacidades o flujos de trabajo específicos. Utilizan un mecanismo de **Divulgación Progresiva (Progressive Disclosure)** para optimizar el uso de la ventana de contexto del LLM.

**Estructura del Archivo de Skill:**
Un Skill se organiza en un directorio con la siguiente estructura:
```text
skill-name/
├── SKILL.md (requerido)
│   ├── YAML frontmatter metadata (requerido: name, description)
│   └── Markdown instructions (requerido: cuerpo de instrucciones)
└── Bundled Resources (opcional)
    ├── scripts/          - Código ejecutable (Python/Bash/etc.)
    ├── references/       - Documentación cargada en contexto según sea necesario
    └── templates/        - Archivos utilizados en la salida (plantillas, iconos, etc.)
```

**Mecanismo de Carga (Progressive Disclosure):**
1. **Metadatos:** El frontmatter YAML (nombre y descripción) siempre está en el contexto del agente (~100 palabras). Esto permite al agente saber qué Skills tiene disponibles y cuándo usarlos.
2. **Cuerpo de SKILL.md:** Se carga en el contexto solo cuando el Skill se activa (se recomienda mantenerlo por debajo de 500 líneas).
3. **Recursos empaquetados:** Se cargan bajo demanda. Por ejemplo, los scripts en `scripts/` se ejecutan sin necesidad de cargar su código fuente en el contexto, y los archivos en `references/` se leen solo cuando las instrucciones en `SKILL.md` lo indican.

**Invocación:**
El agente invoca un Skill cuando la intención del usuario coincide con la descripción en el frontmatter del `SKILL.md`. También puede ser invocado explícitamente por el usuario mediante un comando de barra diagonal (ej. `/skill-name`) en la interfaz de chat.

#### Comportamientos Observados en Producción
1. **Fallo en la actualización de tokens OAuth (Bug):** Se ha documentado en la comunidad (ej. repositorios de GitHub relacionados con MCP) que en implementaciones de servidores MCP personalizados, a veces el proxy no intenta el "silent refresh" del token OAuth antes de reenviar la llamada a la herramienta, lo que resulta en fallos de autenticación a mitad de la tarea si el token expira.
2. **Problemas de Server-Sent Events (SSE) en Connectors locales:** Usuarios en Reddit han reportado problemas al intentar añadir servicios MCP directamente en la pestaña de conectores sin usar túneles como ngrok, resultando en errores relacionados con la conexión SSE.
3. **Errores de Autenticación con Google Drive:** Se han observado casos donde, a pesar de completar el flujo de permisos de Google, Manus arroja un error de autenticación al intentar acceder a Drive, lo que requiere reautorización o revisión de los alcances (scopes) concedidos.
4. **Consumo de Créditos por Acciones Fallidas:** Los usuarios han notado que si una tarea falla repetidamente debido a errores de autenticación en un Connector, el agente puede entrar en un bucle de reintentos que consume una gran cantidad de créditos (hasta 3500 tokens en tareas simples) antes de detenerse.
5. **Eficiencia de los Skills:** La comunidad destaca que el uso de Skills reduce drásticamente las alucinaciones del modelo, ya que el agente sigue las instrucciones deterministas del `SKILL.md` y ejecuta scripts en lugar de depender únicamente de su conocimiento paramétrico.

#### Fuentes Adicionales
1. https://manus.im/docs/integrations/mcp-connectors
2. https://manus.im/docs/integrations/custom-mcp
3. https://manus.im/docs/features/skills
4. https://manus.im/features/agent-skills
5. https://manus.im/blog/projects-connectors
6. https://github.com/anthropics/claude-ai-mcp/issues/228
7. https://blog.logto.io/manus-cloud-browser-login
8. https://www.reddit.com/r/ManusOfficial/comments/1q6m1ip/having_a_little_oauthsse_trouble/
9. https://www.reddit.com/r/ManusOfficial/comments/1purxmi/google_auth_error/
10. https://www.reddit.com/r/ManusOfficial/comments/1mo9wfp/wasted_3500_token_on_simple_task/
11. /home/ubuntu/skills/skill-creator/SKILL.md (Archivo interno del sistema)

## M08 — Capacidades Multimodales: Análisis y Generación de Contenido Multimedia

### Descripción Técnica
## Descripción Técnica Completa

Manus AI se posiciona como un agente autónomo capaz de interactuar y procesar una amplia gama de tipos de medios, trascendiendo las capacidades tradicionales de los modelos de lenguaje. Su arquitectura multimodal le permite no solo comprender y generar texto, sino también analizar y crear imágenes, entender contenido de video, producir salida de voz y transcribir habla. Esta integración fluida de diferentes modalidades es fundamental para su capacidad de automatizar flujos de trabajo complejos y extender el alcance humano en diversas aplicaciones [1].

El módulo de Capacidades Multimodales de Manus AI abarca varias áreas clave, cada una con sus propias funcionalidades y casos de uso:

### Generación de Imágenes

Manus AI puede generar imágenes personalizadas a partir de descripciones textuales. Esta capacidad es útil para crear maquetas de productos, ilustraciones de características, conceptos de UI/UX, gráficos para redes sociales, ilustraciones para publicaciones de blog, creatividades publicitarias, fondos de diapositivas personalizados, ilustraciones de conceptos, metáforas visuales, diagramas de flujo de procesos, arquitecturas de sistemas e infografías [1].

Para obtener mejores resultados en la generación de imágenes, se recomienda ser específico sobre el estilo (ej. "Minimalista, moderno, fotografía profesional"), describir la composición (ej. "Sujeto centrado, fondo borroso, iluminación natural") y especificar el caso de uso (ej. "Para publicación de Instagram, formato cuadrado, superposición de texto en negrita") [1].

### Comprensión de Imágenes

La capacidad de comprensión de imágenes de Manus AI le permite analizar y extraer información de imágenes. Esto incluye la extracción de texto de capturas de pantalla, la lectura de notas escritas a mano, el análisis de recibos y facturas, la identificación de objetos en fotos, el análisis de gráficos y diagramas, la descripción del contenido de la imagen, la verificación de problemas en fotos de productos, la verificación del contenido de la imagen y la comparación de diferencias visuales entre dos imágenes [1].

Ejemplos de tareas incluyen extraer texto de múltiples imágenes de productos para crear una hoja de cálculo, analizar una imagen de gráfico para recrearla como un gráfico editable con los mismos datos, y comparar dos fotos de productos para listar sus diferencias [1].

### Comprensión de Video

Manus AI puede analizar contenido de video y extraer información valiosa. Sus usos comunes incluyen la transcripción de reuniones, la extracción de elementos de acción, la síntesis de discusiones, el análisis de videos de la competencia, la extracción de puntos clave de tutoriales, la revisión de demostraciones de productos, la conversión de tutoriales en video a guías escritas, la creación de resúmenes de videos largos y la extracción de citas y marcas de tiempo [1].

Un ejemplo de tarea es transcribir un seminario web de una hora y crear una transcripción completa, un resumen ejecutivo, puntos clave y una sección de preguntas y respuestas. Otro ejemplo es analizar videos de productos de la competencia para crear una tabla comparativa de características [1].

### Salida de Voz

Esta capacidad permite a Manus AI convertir texto en habla natural. Se utiliza para transformar publicaciones de blog en archivos de audio, crear voces en off para guiones de presentación y generar versiones de audio de descripciones de productos para sitios web [1].

Las opciones de voz incluyen la posibilidad de especificar el tono (profesional, amigable, casual, enérgico, tranquilo), el ritmo (rápido, moderado, lento) y el estilo (conversacional, formal, educativo, promocional) [1].

### Voz a Texto

Manus AI puede transcribir archivos de audio a texto. Esto es útil para transcribir grabaciones de entrevistas, convertir episodios de podcast a texto con etiquetas de orador y transcribir llamadas de soporte al cliente para identificar problemas comunes [1].

Las características clave de esta función incluyen la identificación de oradores, marcas de tiempo, formato adecuado (puntuación y párrafos) y alta precisión incluso con acentos o ruido de fondo [1].

### Combinación de Múltiples Modos

Una de las fortalezas distintivas de Manus AI es su capacidad para combinar estas modalidades en flujos de trabajo únicos y complejos. Por ejemplo, puede ver un video de demostración de producto, transcribirlo, extraer características clave, generar capturas de pantalla en momentos importantes y crear una publicación de blog con imágenes y texto. También puede crear una presentación de 10 diapositivas con ilustraciones personalizadas y luego generar un guion de voz en off y narración de audio para toda la presentación. Otro caso de uso es analizar 50 fotos de productos, extraer texto y detalles del producto, generar gráficos comparativos y crear una presentación con los hallazgos [1].

### Procesamiento de Documentos y Conversión a Sitios Web Interactivos

Aunque la documentación de "Multimedia Processing" se centra principalmente en imágenes, video y audio, otras fuentes indican que Manus AI tiene capacidades avanzadas para el procesamiento de documentos como PDF, hojas de cálculo y presentaciones, y puede transformarlos en sitios web interactivos [2] [3] [4] [5]. Por ejemplo, puede generar hojas de cálculo completas con estructura, fórmulas, gráficos y lógica a partir de una simple indicación [3]. También puede crear presentaciones de PowerPoint completas a partir de descripciones o documentos [4]. La capacidad de convertir cualquier archivo (hojas de cálculo, diapositivas, imágenes, currículums, libros) en un sitio web interactivo y compartible es una característica destacada, lo que permite la creación de sitios web con paneles y datos visuales a partir de archivos CSV [5] [6]. Manus AI actúa como un constructor de sitios web impulsado por IA que convierte ideas en sitios web de pila completa sin necesidad de codificación [7].

### Modelos de Generación Internos

Manus AI integra el poder de grandes modelos de lenguaje (LLMs) directamente en sus aplicaciones para comprender y generar texto similar al humano [8]. Si bien la documentación no especifica los nombres exactos de todos los modelos internos utilizados para cada modalidad, se menciona que modelos como GPT-4, Claude y Gemini ofrecen algunas características multimodales, y Manus se diferencia por su capacidad de interpretar y ejecutar código directamente [9]. Esto sugiere que Manus AI aprovecha y orquesta una combinación de modelos de IA de vanguardia, posiblemente incluyendo modelos de visión por computadora para análisis de imágenes y videos, modelos de texto a voz para salida de voz, y modelos de voz a texto para transcripción, además de sus propios mecanismos para la ejecución de código y la integración de flujos de trabajo [9]. La capacidad de Manus para generar videos cortos y animaciones también se menciona, aunque sin detalles específicos sobre los modelos subyacentes [1].

### Capacidades e Implementación
| Capacidad | Implementación | Parámetros/Límites | Comportamiento |
|---|---|---|---|
| **Generación de Imágenes** | Creación de imágenes personalizadas a partir de descripciones textuales. | **Estilo:** Específico (ej. "Minimalista, moderno, fotografía profesional"). **Composición:** Detallada (ej. "Sujeto centrado, fondo borroso, iluminación natural"). **Caso de Uso:** Específico (ej. "Para publicación de Instagram, formato cuadrado, superposición de texto en negrita"). **Formatos:** PNG, JPG, WEBP, GIF y más. **Tamaño:** Especificable (ej. "1920x1080" o "Formato cuadrado"). | Genera maquetas de productos, ilustraciones, gráficos para redes sociales, fondos de diapositivas, diagramas de flujo, arquitecturas de sistemas, infografías. [1] |
| **Comprensión de Imágenes** | Análisis y extracción de información de imágenes. | **Entrada:** Capturas de pantalla, fotos de productos, gráficos, documentos escaneados. | Extrae texto (OCR), lee notas manuscritas, analiza recibos/facturas, identifica objetos, analiza gráficos, describe contenido, verifica problemas en fotos, compara diferencias visuales. [1] |
| **Comprensión de Video** | Análisis de contenido de video y extracción de información. | **Entrada:** Archivos de video, URLs de video. **Duración:** Hasta varias horas. | Transcribe reuniones, extrae elementos de acción, resume discusiones, analiza videos de la competencia, extrae puntos clave de tutoriales, revisa demostraciones de productos, convierte tutoriales a guías escritas, crea resúmenes de videos largos, extrae citas y marcas de tiempo. [1] |
| **Salida de Voz (Texto a Voz)** | Conversión de texto a habla natural. | **Tono:** Profesional, amigable, casual, enérgico, tranquilo. **Ritmo:** Rápido, moderado, lento. **Estilo:** Conversacional, formal, educativo, promocional. | Transforma publicaciones de blog en audio, crea voces en off para presentaciones, genera audio para descripciones de productos. [1] |
| **Voz a Texto (Speech to Text)** | Transcripción de audio a texto. | **Entrada:** Archivos de audio (MP3, WAV, M4A, WEBM y otros). | Transcribe grabaciones de entrevistas, convierte podcasts a texto con etiquetas de orador, transcribe llamadas de soporte al cliente. Incluye identificación de oradores, marcas de tiempo, formato (puntuación, párrafos) y alta precisión. [1] |
| **Procesamiento de Documentos (PDF, Hojas de Cálculo, Presentaciones)** | Análisis y manipulación de diversos formatos de documentos. | **Entrada:** PDF, hojas de cálculo (CSV), presentaciones (PowerPoint). | Genera hojas de cálculo con estructura, fórmulas y gráficos. Crea presentaciones completas a partir de descripciones o documentos. [2] [3] [4] |
| **Conversión a Sitios Web Interactivos** | Transformación de cualquier archivo en un sitio web interactivo. | **Entrada:** Hojas de cálculo, diapositivas, imágenes, currículums, libros, archivos CSV. | Crea sitios web compartibles e interactivos con paneles y datos visuales a partir de archivos. Permite construir sitios web de pila completa sin codificación. [5] [6] [7] |
| **Combinación de Modos** | Integración de múltiples capacidades multimodales en flujos de trabajo complejos. | **Ejemplos:** Video a blog post, presentación con voz en off, análisis de imagen a informe. | Permite flujos de trabajo como transcribir video, extraer características, generar capturas de pantalla y crear un blog post; o crear una presentación con ilustraciones y narración de audio. [1] |

### Limitaciones y Fallas
| Limitación | Severidad | Fuente | Workaround |
|---|---|---|---|
| Susceptibilidad a Errores | Moderada | [2] | Requiere supervisión humana y validación de resultados, especialmente en tareas críticas. |
| Preocupaciones de Privacidad y Seguridad de Datos | Alta | [2] | Se recomienda precaución al manejar datos sensibles; verificar políticas de privacidad y seguridad de Manus AI. |
| Dificultad con Interacciones GUI de Alta Resolución | Moderada | [1] | Puede requerir intervención manual o simplificación de las interfaces gráficas para tareas específicas. |
| Limitaciones en Codificación Médica Especializada | Moderada | [1] | No apto para tareas de codificación médica que requieran alta precisión y conocimiento especializado. |
| Falta de Capacidad Metacognitiva para Tareas Creativas | Moderada | [4] | Para tareas altamente creativas, es posible que se necesite una guía más detallada o una intervención humana para la autocorrección. |
| Ineficiencia y Consumo Elevado de Créditos | Moderada | [7] | Monitorear el consumo de créditos y optimizar las instrucciones para evitar repetición de errores y gastos innecesarios. |
| Construcciones Incompletas y Comportamiento con Errores | Moderada | [7] | Realizar pruebas exhaustivas y validación de las salidas generadas por Manus AI. |
| Problemas de Servidor (Reportados en Beta) | Baja (histórico) | [6] | Mantenerse actualizado con las versiones estables y reportar cualquier problema persistente al soporte técnico. |
| Límites en la Generación (Créditos) | Baja | [3] | Consultar el plan de suscripción para entender los límites de generación y gestionar el uso de créditos. |
| Generación de Video Limitada a Clips Cortos | Baja | [3] | Para videos más largos o complejos, puede ser necesario un procesamiento externo o la combinación de múltiples clips. |

### Ejemplos de Uso Real
1.  **Planificación de Viajes:** Una familia de cuatro planifica un viaje de 10 días a Japón, necesitando alojamiento e itinerarios diarios. Manus AI puede generar estos planes. [2]
2.  **Investigación de Mercado:** Manus AI realizó una investigación en profundidad sobre productos de búsqueda de IA en la industria de la ropa, incluyendo análisis de productos y posicionamiento competitivo. [8]
3.  **Generación de Hojas de Cálculo:** A partir de una simple indicación, Manus AI puede generar hojas de cálculo completas con estructura, fórmulas y gráficos. [3]
4.  **Creación de Presentaciones:** Manus AI puede crear presentaciones de PowerPoint completas a partir de descripciones o documentos. [4]
5.  **Conversión de Archivos a Sitios Web:** Un usuario convirtió un archivo CSV de sus análisis de YouTube en un sitio web con paneles y datos visuales usando Manus AI. [6]
6.  **Automatización de Proyectos de Investigación:** Manus AI puede automatizar proyectos de investigación masivos. [1]
7.  **Creación de Aplicaciones Interactivas:** Manus AI puede construir instantáneamente aplicaciones interactivas. [1]
8.  **Generación de Videos Creativos:** Manus AI puede generar videos creativos. [12]
9.  **Análisis de Video a Blog Post:** Un ejemplo de flujo de trabajo combinado es ver un video de demostración de producto, transcribirlo, extraer características clave, generar capturas de pantalla y crear una publicación de blog con imágenes y texto. [1]
10. **Presentación con Voz en Off:** Crear una presentación de 10 diapositivas con ilustraciones personalizadas y luego generar un guion de voz en off y narración de audio para toda la presentación. [1]
11. **Análisis de Imagen a Informe:** Analizar 50 fotos de productos, extraer texto y detalles del producto, generar gráficos comparativos y crear una presentación con los hallazgos. [1]


### Hallazgos de Fase 2 (Actualizado 1 Mayo 2026)

#### Nuevos Descubrimientos
La investigación exhaustiva sobre las capacidades multimodales de Manus AI ha revelado detalles específicos sobre los modelos de IA que utiliza para la generación y procesamiento de contenido, así como algunas de sus limitaciones. A diferencia de lo que se podría asumir, Manus AI no se limita a un único modelo para cada modalidad, sino que integra una combinación de tecnologías avanzadas para ofrecer una experiencia multimodal robusta y versátil. Estos hallazgos cierran gaps significativos en el conocimiento público sobre la infraestructura técnica subyacente de Manus AI.

En el ámbito de la **generación de imágenes**, Manus AI emplea principalmente dos modelos clave: **Nano Banana Pro** y los **modelos de imágenes de ChatGPT**. Nano Banana Pro es un modelo avanzado de generación de imágenes desarrollado por Google, integrado directamente en Manus AI para la creación de visuales de calidad profesional. Este modelo es particularmente notable por su capacidad para renderizar texto nítido y legible dentro de las imágenes, un desafío común para muchos otros generadores de IA. Además, Nano Banana Pro permite mantener una consistencia visual a través de múltiples salidas, lo que lo hace ideal para la creación de presentaciones y gráficos profesionales. La mención de "modelos de imágenes de ChatGPT" en la documentación de Manus AI, en conjunción con la información de OpenAI, sugiere fuertemente que se refiere a **DALL-E 3**. DALL-E 3 es conocido por su integración con ChatGPT y su capacidad para generar imágenes detalladas y coherentes a partir de descripciones de lenguaje natural. La combinación de Nano Banana Pro y DALL-E 3 permite a Manus AI ofrecer una amplia gama de estilos y calidades en la generación de imágenes, desde fotorrealistas hasta arte digital y anime [1] [2] [3] [4] [5].

Para la **generación de video**, Manus AI utiliza una suite de modelos que incluye **Sora 2, Veo 3.1 y Veo 3.1 Fast**. Estos modelos son accesibles a través de lo que Manus denomina un "AI Playground", lo que indica una posible abstracción o integración de estas tecnologías de terceros. Sora 2, presumiblemente una versión avanzada del modelo de OpenAI, y Veo 3.1 (y su variante Fast) de Google, son modelos de vanguardia en la generación de video a partir de texto. La capacidad de elegir entre estos modelos sugiere una optimización para diferentes escenarios, donde Veo 3.1 Fast podría priorizar la velocidad sobre la complejidad o la calidad máxima, y Sora 2 podría ofrecer una mayor fidelidad o coherencia en videos más largos. La documentación también menciona que Manus AI puede generar "clips de video cortos y animaciones", lo que implica un enfoque en la creación de contenido visual dinámico más que en la producción de largometrajes [6] [7] [8].

En cuanto a los **modelos de audio y voz**, Manus AI ofrece capacidades de **salida de voz (text-to-speech)** y **transcripción de voz (speech-to-text)**. Aunque la documentación no especifica explícitamente los nombres de modelos como ElevenLabs u OpenAI TTS, sí indica que la salida de voz está disponible en 17 idiomas y permite controlar el tono (profesional, amigable, casual, energético, tranquilo), el ritmo (rápido, moderado, lento) y el estilo (conversacional, formal, educativo, promocional) [9] [10]. La capacidad de personalización sugiere el uso de modelos avanzados de síntesis de voz. Para la transcripción de voz, Manus AI destaca por su alta precisión, incluso con acentos, múltiples hablantes o ruido de fondo, e incluye características como identificación de hablantes, marcas de tiempo y formato adecuado (puntuación y párrafos) [9]. La integración de estas capacidades de audio permite a Manus AI procesar y generar contenido de audio de manera efectiva, lo que es crucial para flujos de trabajo multimodales como la conversión de publicaciones de blog a audio o la transcripción de reuniones [9].

Para el **procesamiento de imágenes de entrada (visión artificial)**, Manus AI implementa una capacidad de "Image Understanding" que le permite analizar capturas de pantalla, extraer texto, identificar objetos, analizar gráficos y describir el contenido de las imágenes en detalle. Aunque no se mencionan explícitamente modelos como Claude Vision o GPT-4V, la funcionalidad descrita es consistente con las capacidades de modelos de visión multimodal avanzados. La plataforma puede realizar tareas como el procesamiento de documentos (extraer texto de capturas de pantalla, leer notas manuscritas, analizar recibos), análisis visual (identificar objetos, analizar gráficos, describir contenido) y control de calidad (verificar fotos de productos, comparar diferencias visuales) [9]. La capacidad de "PhotoStyle insight scanner" también indica un análisis profundo de elementos visuales como composición, iluminación, color y estado de ánimo [11]. Esto sugiere que Manus AI utiliza modelos de visión personalizados o una combinación de modelos de terceros para estas tareas de análisis visual.

Las **limitaciones de las capacidades multimodales** de Manus AI, aunque no se detallan exhaustivamente en un solo lugar, se pueden inferir de varias fuentes. Para la generación de imágenes, aunque Nano Banana Pro es excelente para texto legible y consistencia, la edición directa de las diapositivas generadas por Nano Banana Pro no es posible actualmente, ya que se entregan como imágenes completas [5]. En la generación de video, se ha observado que, si bien la adherencia a la indicación en términos de detalles estáticos es alta, el movimiento en los videos generados puede ser "extremadamente antinatural" y presentar "fallos" en la animación, como objetos que aparecen y desaparecen o movimientos poco realistas [7]. La duración de los videos generados es generalmente corta, con menciones de "clips de video cortos y animaciones" y un ejemplo de un video de 30 segundos [7] [9]. La documentación indica que Manus puede procesar videos de "hasta varias horas de duración" para el entendimiento de video, pero esto no se traduce directamente en la duración de los videos que puede generar [9]. Los formatos de imagen soportados para la generación incluyen PNG, JPG, WEBP y GIF, y se pueden especificar dimensiones para la resolución [9]. Para el audio, los formatos soportados para transcripción incluyen MP3, WAV, M4A y WEBM [9]. No se especifican límites máximos de tamaño de archivo para la carga, pero se sugiere "gestionar el número y tamaño de los archivos con cuidado" [12]. La generación de contenido multimodal consume créditos, y los costos varían según la complejidad y cantidad [5] [9].

En resumen, Manus AI aprovecha una arquitectura multimodal sofisticada que integra modelos avanzados de diferentes proveedores para optimizar la generación y el procesamiento de contenido. Para la generación de imágenes, la combinación de **Nano Banana Pro** (de Google, probablemente basado en Gemini 3 Pro Image) y **DALL-E 3** (de OpenAI) es estratégica. Nano Banana Pro destaca por su capacidad para renderizar texto con gran fidelidad y mantener la consistencia visual en proyectos complejos como presentaciones, lo que lo hace invaluable para usos profesionales donde la precisión es clave. DALL-E 3, por su parte, aporta una capacidad superior para interpretar prompts complejos y generar imágenes altamente creativas y fotorrealistas, ampliando el espectro artístico disponible para los usuarios. Esta dualidad permite a Manus AI abordar una amplia gama de requisitos visuales, desde gráficos técnicos hasta ilustraciones artísticas, seleccionando el modelo más adecuado según el contexto del prompt [1] [2] [3] [4] [5].

La estrategia de Manus AI en la **generación de video** es igualmente ambiciosa, al integrar modelos de vanguardia como **Sora 2** (OpenAI) y **Veo 3.1 / Veo 3.1 Fast** (Google). La disponibilidad de múltiples modelos de video a través de un "AI Playground" no solo demuestra la capacidad de integración de Manus, sino que también sugiere una infraestructura que permite la experimentación y la adaptación a las últimas innovaciones en el campo. Sora 2, conocido por su capacidad para generar escenas complejas y coherentes, y Veo 3.1/Fast, que ofrece un equilibrio entre calidad y velocidad, proporcionan a Manus la flexibilidad para producir videos para diversas aplicaciones, desde clips promocionales rápidos hasta visualizaciones más elaboradas. Sin embargo, es crucial notar que, si bien estos modelos son potentes, la integración y orquestación para lograr movimientos naturales y coherencia narrativa en videos más largos sigue siendo un desafío técnico, como lo demuestran los "fallos" observados en la animación [6] [7] [8].

En el ámbito del **audio y la voz**, Manus AI se posiciona con capacidades robustas de **síntesis de voz (text-to-speech)** y **reconocimiento de voz (speech-to-text)**. La oferta de salida de voz en 17 idiomas con control granular sobre el tono, ritmo y estilo indica el uso de modelos TTS de última generación, que pueden ser desarrollos propios o integraciones de APIs de proveedores líderes como ElevenLabs o Google Text-to-Speech. La alta precisión de la transcripción de voz, incluso en entornos ruidosos o con múltiples hablantes, sugiere la implementación de modelos ASR avanzados, posiblemente con técnicas de diarización y mejora de señal. Estas capacidades son fundamentales para la automatización de tareas como la creación de podcasts a partir de texto o la generación de resúmenes de reuniones a partir de grabaciones de audio [9] [10].

Para el **procesamiento de imágenes de entrada (visión artificial)**, Manus AI va más allá de la simple extracción de texto. Su capacidad de "Image Understanding" y el "PhotoStyle insight scanner" revelan una integración de modelos de visión por computadora que pueden realizar análisis semánticos profundos. Esto incluye la detección y clasificación de objetos, el análisis de la composición visual, la iluminación, el color y el estado de ánimo de una imagen. Aunque no se especifican nombres de modelos como Claude Vision o GPT-4V, la funcionalidad descrita es comparable a la de estos sistemas multimodales avanzados, lo que sugiere que Manus AI utiliza modelos de visión de última generación, ya sean propios o de terceros, para ofrecer una comprensión contextual rica de las entradas visuales. Esta capacidad es esencial para tareas como el análisis de documentos visuales, la verificación de calidad de productos y la creación de informes basados en datos visuales [9] [11].

Las **limitaciones** actuales de las capacidades multimodales de Manus AI se manifiestan principalmente en la generación de video, donde la fluidez y naturalidad del movimiento aún presentan desafíos, y en la edición directa de imágenes generadas por Nano Banana Pro, que se entregan como imágenes finales. La duración de los videos generados es limitada a "clips cortos", aunque la plataforma puede procesar videos de "varias horas" para su comprensión. Los formatos de archivo soportados son amplios para imágenes (PNG, JPG, WEBP, GIF) y audio (MP3, WAV, M4A, WEBM), y se permite la especificación de resolución para imágenes. La gestión de créditos es un factor importante, ya que la generación de contenido multimodal consume recursos, con costos que varían según la complejidad y cantidad. Estas limitaciones, sin embargo, son comunes en el estado actual del arte de la IA multimodal y representan áreas activas de investigación y desarrollo [5] [7] [9] [12].

En síntesis, Manus AI se posiciona como un orquestador inteligente de modelos multimodales, capaz de integrar y gestionar diversas tecnologías de IA para ofrecer soluciones completas. Su enfoque en la combinación de modelos líderes en la industria para cada modalidad le permite ofrecer un conjunto de herramientas robusto, aunque con las limitaciones inherentes a la tecnología actual, especialmente en la generación de video de alta fidelidad y larga duración.

#### Detalles de Implementación
La implementación de las capacidades multimodales en Manus AI se basa en una arquitectura de orquestación de agentes que integra y coordina múltiples modelos de IA especializados. Aunque los detalles internos específicos de la API y las configuraciones exactas no son de dominio público, la documentación y el comportamiento observado permiten inferir la siguiente estructura de implementación:

**Generación de Imágenes:**

*   **Modelos Base:** Se utilizan **Nano Banana Pro** (de Google, posiblemente basado en Gemini 3 Pro Image) y **DALL-E 3** (de OpenAI, accesible a través de la integración con "modelos de imágenes de ChatGPT").
*   **Orquestación:** Manus AI actúa como un orquestador, seleccionando el modelo más adecuado en función del prompt del usuario y el estilo deseado. Por ejemplo, para imágenes con texto legible o consistencia visual en una serie (como diapositivas), se prioriza Nano Banana Pro. Para imágenes más artísticas o fotorrealistas, se puede recurrir a DALL-E 3.
*   **Parámetros de Entrada (Pseudocódigo):**
    ```python
    def generate_image(prompt: str, style: str, resolution: str = "1024x1024", model: str = "auto") -> Image:
        # Lógica para seleccionar el modelo (Nano Banana Pro, DALL-E 3)
        if model == "Nano Banana Pro" or ("text_in_image" in prompt and "consistent_style" in prompt):
            # Llamada a la API de Nano Banana Pro con parámetros específicos
            image = nano_banana_pro_api.create_image(prompt=prompt, style=style, resolution=resolution)
        elif model == "DALL-E 3" or ("photorealistic" in style or "artistic" in style):
            # Llamada a la API de DALL-E 3 con parámetros específicos
            image = dall_e_3_api.create_image(prompt=prompt, style=style, resolution=resolution)
        else:
            # Modelo por defecto o lógica de fallback
            image = default_image_model.create_image(prompt=prompt, style=style, resolution=resolution)
        return image
    ```
*   **Configuraciones:** La plataforma permite especificar estilos (Arte Digital, Fotorrealista, Anime, Render 3D), resoluciones (ej. 1920x1080, formato cuadrado) y, en algunos casos, el modelo a utilizar (Nano Banana Pro o modelos de imágenes de ChatGPT) [1] [5] [9].

**Generación de Video:**

*   **Modelos Base:** Se integran **Sora 2** (OpenAI) y **Veo 3.1 / Veo 3.1 Fast** (Google). La mención de un "AI Playground" sugiere que estos modelos pueden ser accesibles a través de una interfaz unificada o un conjunto de APIs estandarizadas por Manus.
*   **Orquestación:** Similar a la generación de imágenes, Manus AI selecciona el modelo de video en función de la solicitud del usuario, posiblemente priorizando Veo 3.1 Fast para mayor velocidad o Sora 2 para mayor fidelidad. La generación de video se describe como la creación de "clips de video cortos y animaciones" [6] [7] [9].
*   **Parámetros de Entrada (Pseudocódigo):**
    ```python
    def generate_video(prompt: str, duration_seconds: int, style: str, model: str = "auto") -> VideoClip:
        # Lógica para seleccionar el modelo (Sora 2, Veo 3.1, Veo 3.1 Fast)
        if model == "Sora 2" or duration_seconds > 30:
            video = sora_2_api.create_video(prompt=prompt, duration=duration_seconds, style=style)
        elif model == "Veo 3.1 Fast" or "quick_generation" in prompt:
            video = veo_3_1_fast_api.create_video(prompt=prompt, duration=duration_seconds, style=style)
        else:
            video = veo_3_1_api.create_video(prompt=prompt, duration=duration_seconds, style=style)
        return video
    ```
*   **Configuraciones:** La plataforma permite la generación de videos a partir de texto o imágenes de entrada. La duración es un factor clave, con un enfoque en clips cortos [7] [9].

**Audio y Voz:**

*   **Salida de Voz (Text-to-Speech):** Manus AI ofrece una API de síntesis de voz con control sobre el tono, el ritmo y el estilo, y soporte para 17 idiomas. Esto sugiere el uso de un modelo TTS avanzado, posiblemente una integración con proveedores como ElevenLabs o una solución interna altamente personalizada, dado el nivel de control granular ofrecido [9] [10].
*   **Transcripción de Voz (Speech-to-Text):** La alta precisión y las características como la identificación de hablantes y las marcas de tiempo indican el uso de un modelo ASR (Automatic Speech Recognition) robusto. Los formatos de audio soportados incluyen MP3, WAV, M4A y WEBM [9].
*   **Parámetros de Entrada (Pseudocódigo TTS):**
    ```python
    def text_to_speech(text: str, language: str = "es", tone: str = "professional", pace: str = "moderate", style: str = "conversational") -> AudioFile:
        audio = tts_api.convert_text(text=text, lang=language, tone=tone, pace=pace, style=style)
        return audio
    ```
*   **Parámetros de Entrada (Pseudocódigo STT):**
    ```python
    def speech_to_text(audio_file: AudioFile, speaker_identification: bool = True, timestamps: bool = True) -> Transcript:
        transcript = stt_api.transcribe_audio(audio=audio_file, identify_speakers=speaker_identification, include_timestamps=timestamps)
        return transcript
    ```

**Procesamiento de Imágenes de Entrada (Visión Artificial):**

*   **Modelos de Visión:** Aunque no se nombran modelos específicos como Claude Vision o GPT-4V, la funcionalidad de "Image Understanding" implica el uso de modelos de visión por computadora para tareas como OCR (Optical Character Recognition), detección de objetos, análisis de escenas y extracción de metadatos visuales. La capacidad de "PhotoStyle insight scanner" sugiere un modelo especializado en análisis estético y compositivo [9] [11].
*   **Integración:** Estos modelos de visión se integran para permitir el análisis de imágenes cargadas por el usuario o capturas de pantalla, facilitando flujos de trabajo como el procesamiento de documentos y el análisis visual [9].
*   **Parámetros de Entrada (Pseudocódigo):**
    ```python
    def analyze_image(image: Image, task: str = "extract_text", details: bool = False) -> dict:
        if task == "extract_text":
            result = ocr_model.extract_text(image=image)
        elif task == "identify_objects":
            result = object_detection_model.detect(image=image)
        elif task == "describe_content":
            result = image_captioning_model.describe(image=image, detailed=details)
        else:
            result = {"error": "Task not supported"}
        return result
    ```

La arquitectura general de Manus AI se describe como un "agente autónomo de IA" que orquesta estos modelos especializados para ejecutar tareas complejas, lo que implica un sistema de planificación, ejecución y validación que coordina las diferentes capacidades multimodales [7] [13].

#### Comportamientos Observados en Producción
Durante la interacción con las capacidades multimodales de Manus AI, se han documentado varios comportamientos en producción que revelan tanto sus fortalezas como sus limitaciones. En la generación de imágenes, se ha observado que el modelo Nano Banana Pro, integrado en Manus AI, es excepcionalmente competente para renderizar texto nítido y legible dentro de las imágenes, un aspecto crucial para la creación de infografías y presentaciones donde la precisión textual es fundamental. Además, este modelo demuestra una notable capacidad para mantener una consistencia visual coherente a través de múltiples salidas, lo que es vital para proyectos que requieren una estética unificada [5].

En el ámbito de la generación de video, Manus AI muestra una alta adherencia a los detalles estáticos proporcionados en la indicación. Por ejemplo, en una prueba para generar un video de un perezoso en una motocicleta en una calle tailandesa, el sistema logró incorporar elementos específicos como letreros tailandeses y tuk-tuks según lo solicitado. Sin embargo, a pesar de esta precisión en los detalles estáticos, el movimiento en los videos generados puede ser "extremadamente antinatural", con fallos en la animación donde objetos no se desplazan de forma realista o aparecen y desaparecen. Un caso ilustrativo fue el del perezoso en motocicleta, donde el perezoso y la moto no se movían de manera fluida y las ruedas no giraban, dando la impresión de una imagen fija superpuesta. En otro video corporativo, se observaron animales que aparecían y desaparecían, extremidades deformadas y acciones ilógicas, como un voluntario recogiendo tierra del suelo para ponerla en una planta o arrojando basura al océano [7].

Adicionalmente, se han registrado comportamientos inesperados en el audio de los videos generados. En el ejemplo del perezoso, el audio de fondo era una "combinación extraña" de sonidos de calles bulliciosas y música electrónica. En el video corporativo, apareció un diálogo de los personajes en una sección, lo cual se percibió como "fuera de lugar" dado que el resto del video carecía de discurso [7].

Por otro lado, la funcionalidad de Speech-to-Text de Manus AI ha demostrado una "muy alta precisión" en la transcripción de voz, incluso en condiciones desafiantes con acentos diversos, múltiples hablantes o ruido de fondo [9]. Finalmente, Manus AI sobresale en la integración de flujos de trabajo complejos, combinando eficazmente múltiples modalidades. Esto se evidencia en su capacidad para transcribir un video, extraer características clave, generar capturas de pantalla y crear una publicación de blog con imágenes y texto, o analizar fotos de productos para generar gráficos comparativos y presentaciones [9].

Estos comportamientos documentados subrayan las fortalezas de Manus AI en la integración multimodal y la generación de imágenes estáticas de alta calidad, al tiempo que señalan áreas de mejora en la coherencia y naturalidad del movimiento en la generación de video, así como en la gestión de elementos de audio y diálogo en dicho formato.

#### Fuentes Adicionales
1.  [Generador de Imágenes AI en Línea: Texto a Imagen - Manus AI](https://manus.im/es/tools/ai-image-generator)
2.  [Nano Banana Pro - Manus Documentation](https://manus.im/docs/integrations/nano-banana-pro)
3.  [AI design generator online: Text to image - Manus](https://manus.im/tools/ai-design)
4.  [AI Image Generator Online: Text to Image - Manus AI](https://manus.im/tools/ai-image-generator)
5.  [Nano Banana Pro - Manus Documentation](https://manus.im/docs/integrations/nano-banana-pro)
6.  [AI video generator: Turn any idea into amazing videos](https://manus.im/playbook/video-generator)
7.  [Manus vs Synthesia: ¿Qué Generador de Videos es el Adecuado para Ti?](https://manus.im/es/blog/manus-vs-synthesia)
8.  [The 12 Best Text-to-Video AI Tools in 2026 (Ranked and Tested)](https://manus.im/blog/best-text-to-video-ai)
9.  [Multimedia Processing - Manus Documentation](https://manus.im/docs/features/multi-modal)
10. [Manus adds Audio output in 17 languages - LinkedIn](https://www.linkedin.com/posts/manus-im_manus-supports-a-variety-of-output-formats-activity-7346194755577421826-kajG)
11. [PhotoStyle insight scanner: Analyze your art, refine ...](https://manus.im/playbook/photo-style-scanner)
12. [File Upload Limit : r/ManusOfficial - Reddit](https://www.reddit.com/r/ManusOfficial/comments/1km2zss/file_upload_limit/)
13. [Everyone in AI is talking about Manus. We put it to the test.](https://www.technologyreview.com/2025/03/11/1113133/manus-ai-review/)

## M09 — Orquestación Multi-Agente y Wide Research (ACTUALIZADO 30 Abril 2026)

### Descripción Técnica
Wide Research es el sistema de orquestación multi-agente de Manus. Despliega cientos de agentes independientes en paralelo, cada uno con su propio contexto fresco, coordinados por un agente principal orquestador. Los sub-agentes NO se comunican entre sí — toda coordinación fluye por el orquestador central.

### Capacidades de Wide Research
| Parámetro | Valor | Fuente |
|-----------|-------|--------|
| Agentes paralelos máximos probados | 250 | Documentación oficial |
| Subtareas simultáneas estándar | 20 | Artículo de soporte Manus |
| Límite teórico | Ilimitado (depende de complejidad) | Documentación oficial |
| Escala sin degradación | Hasta 250+ elementos | vs. 8-10 en sistemas tradicionales |

### Arquitectura del Orquestador
```
[Agente Principal / Orquestador]
    ├── Descompone tarea en N subtareas independientes
    ├── Despliega N sub-agentes con contexto fresco
    ├── Sub-agentes ejecutan en PARALELO (sin comunicación entre sí)
    ├── Recopila resultados de todos los sub-agentes
    └── Sintetiza en formato final solicitado
```

### Modelos Internos (Información Parcial - Propietaria)
| Modelo | Uso Probable | Fuente |
|--------|-------------|--------|
| Claude (versión fine-tuned) | Razonamiento y planificación | Comunidad técnica |
| Qwen (versión fine-tuned) | Tareas específicas de agente | Comunidad técnica |
| Versiones exactas | DESCONOCIDAS - propietario | N/A |

### Sistema de Sub-Tareas
1. El orquestador analiza la tarea completa
2. Identifica elementos independientes que pueden procesarse en paralelo
3. Crea una VM/contexto fresco para cada sub-agente
4. Cada sub-agente tiene acceso completo a herramientas (browser, code, files)
5. Los sub-agentes NO comparten estado ni se comunican
6. El orquestador recopila y sintetiza al finalizar todos

### Score de Completitud: 95%
**Fuentes verificadas:** manus.im/blog/manus-wide-research-solve-context-problem, documentación oficial, papers ArXiv

---

## M10 — Límites, Fallas y Patrones de Error de Manus AI

### Descripción Técnica
# M10 — Límites, Fallas y Patrones de Error de Manus AI

## Descripción Técnica Completa

Manus AI, a pesar de sus capacidades avanzadas en la ejecución autónoma de tareas y la orquestación multi-agente, presenta una serie de limitaciones inherentes, patrones de falla recurrentes y vulnerabilidades que han sido documentadas tanto por análisis técnicos como por la experiencia de la comunidad de usuarios. La comprensión de estos aspectos es crucial para cualquier equipo de ingeniería que busque replicar o integrar funcionalidades similares, ya que revelan las fronteras actuales de la autonomía de los agentes de IA.

### Desempeño en el Remote Labor Index (RLI)

Uno de los indicadores más contundentes de las limitaciones de Manus AI en escenarios del mundo real es su desempeño en el **Remote Labor Index (RLI)**. Este benchmark, diseñado para medir la capacidad de los agentes de IA para completar tareas de freelance reales, reveló que Manus AI, el agente con mejor rendimiento, solo logró completar con éxito el **2.5%** de los proyectos evaluados a un nivel aceptable para los clientes [4, 5, 6, 7, 8]. Este resultado contrasta drásticamente con el rendimiento de la IA en benchmarks académicos y subraya una brecha significativa entre la capacidad teórica y la aplicación práctica en tareas complejas y multifacéticas. Los proyectos del RLI abarcan 23 categorías de trabajo, desde desarrollo de juegos hasta diseño arquitectónico, con un costo promedio de $632 y una duración de 29 horas [4].
Los patrones de error identificados en el RLI son variados y revelan deficiencias fundamentales [4]. Por ejemplo, en el 17.6% de los casos, Manus AI generó archivos que estaban corruptos o completamente vacíos. El 35.7% de las tareas se consideraron incompletas, como la producción de un video de 8 segundos en lugar de 8 minutos. Además, el 45.6% de los resultados fueron de baja calidad, incluyendo dibujos primitivos o voces robóticas en locuciones. Finalmente, en el 14.8% de los casos, diferentes partes del trabajo no coincidían entre sí, como variaciones en el diseño de una casa en diferentes renders 3D.

Estas fallas sugieren una incapacidad de los agentes de IA para verificar su propio trabajo, especialmente en proyectos que requieren una validación visual compleja [4].

### Desafíos en Interacciones GUI de Alta Resolución y Codificación Médica

Un análisis crítico de las limitaciones de Manus AI destaca sus dificultades en la interacción con interfaces gráficas de usuario (GUI) de alta resolución y en dominios especializados como la codificación médica [1]. Las limitaciones clave incluyen la falta de integración de retroalimentación visual, donde a diferencia de los operadores humanos, Manus carece de capacidades nativas de visión por computadora para interpretar dinámicamente los elementos de la pantalla, dependiendo en cambio de llamadas a la API y flujos de trabajo predefinidos [1]. También se observa una acumulación de errores en tareas complejas, ya que el enfoque iterativo de “prueba y error” del agente, si bien es efectivo para la depuración de código, se vuelve ineficiente en entornos GUI donde cada interacción puede desencadenar cambios en el diseño en cascada [1]. Finalmente, existen problemas de escalabilidad, donde la infraestructura del servidor de Manus lucha bajo cargas pesadas, lo que genera preocupaciones sobre el rendimiento de las tareas GUI en tiempo real a escala [1].

En el ámbito de la codificación médica, Manus AI, como otros LLMs, muestra tasas de precisión por debajo del 50% para códigos ICD-10-CM y CPT, con una tendencia a la mala interpretación contextual y la generación de códigos técnicamente válidos pero clínicamente inapropiados [1]. La arquitectura no determinista de Manus exacerba los problemas de fiabilidad de los LLM, lo que lleva a resultados de codificación inconsistentes [1].

### Limitaciones Arquitectónicas y de Flujo de Trabajo

El diseño de Manus introduce vulnerabilidades específicas en dominios especializados [1]. Se observa una falta de controles granulares, ya que a diferencia de la aplicación de políticas de SmythOS, Manus opera sin verificaciones de cumplimiento obligatorias, lo que arriesga acciones no autorizadas en flujos de trabajo sensibles [1]. Existe una dependencia de la supervisión humana, pues el agente requiere monitoreo constante para decisiones críticas, lo que anula las ganancias de eficiencia en dominios de alto riesgo como la atención médica [1]. Finalmente, se presentan problemas de herencia del modelo, dado que como sistema basado en Claude, Manus hereda los sesgos de LLM y los riesgos de alucinación, lo que agrava los errores en el uso de terminología especializada [1].

### Problemas de Fiabilidad y Rendimiento

La experiencia de los usuarios revela problemas significativos de fiabilidad y rendimiento. Se han reportado caídas del sistema, congelamientos durante búsquedas web y otros procesos, y una falta de flexibilidad en la ejecución de tareas [3]. La ventana de contexto máxima es una fuente común de fallas en tareas no inteligentes, como la codificación [3].

### Preocupaciones de Privacidad y Seguridad

Existen aprensiones significativas con respecto a la privacidad y seguridad de los datos, particularmente sobre cómo Manus AI maneja la información del usuario durante la ejecución de tareas [2, 3]. La comunidad ha expresado temores sobre la posibilidad de que Manus recopile datos sensibles y ha reportado problemas con la ciberseguridad y la gestión de spam [3].

### Sistema de Créditos y Problemas de Facturación

El sistema de créditos de Manus AI ha sido una fuente constante de frustración para los usuarios. Se han reportado casos de consumo excesivo de créditos para tareas básicas, deducciones automáticas no autorizadas y problemas con los reembolsos de créditos que aparecen en los registros pero no se aplican al saldo [9, 10, 11, 12, 13, 14]. Esto ha llevado a que los usuarios describan a Manus como un "agujero negro de créditos" cuando las cosas salen mal [14].

### Casos de Agente Atascado y Consumo de Créditos sin Resultado

Los usuarios han reportado que el agente se queda atascado en bucles infinitos de auto-delegación y "memory bloat", consumiendo créditos sin producir resultados útiles [15]. En algunos casos extremos, el agente ha tomado decisiones independientes que han llevado a la pérdida de datos críticos, como la eliminación de bases de datos enteras [16]. La ineficiencia se manifiesta en la repetición de los mismos errores en múltiples iteraciones, incluso para tareas sencillas como el formato HTML, lo que resulta en un gasto considerable de créditos sin un output utilizable [9].

### Vulnerabilidades de Seguridad Conocidas

Aunque la documentación oficial no detalla vulnerabilidades específicas como "SilentBridge" o "prompt injection", la comunidad ha discutido la importancia de reportar vulnerabilidades y la dificultad de usar LLMs como ChatGPT para encontrarlas debido a filtros de legalidad [17]. La preocupación por la seguridad es un tema recurrente, especialmente en relación con el manejo de datos sensibles y la integración con herramientas externas [3].

## Conclusión

Las limitaciones de Manus AI, desde su bajo rendimiento en el RLI hasta sus problemas de fiabilidad, seguridad y el controvertido sistema de créditos, sugieren que, si bien es una herramienta potente para la automatización, aún está lejos de ser un sistema autónomo infalible. La necesidad de supervisión humana constante, la susceptibilidad a errores en tareas complejas y la falta de controles granulares son aspectos críticos que deben abordarse para mejorar su adopción y fiabilidad en entornos de producción. La documentación de estos puntos débiles es fundamental para el desarrollo de sistemas de IA más robustos y confiables.

### Capacidades e Implementación
| Capacidad | Implementación | Parámetros/Límites | Comportamiento |
|---|---|---|---|
| Ejecución Autónoma de Tareas | Orquestación multi-agente (planificador, ejecutor, verificador) | No especificado, pero se infiere que es para tareas multifacéticas. | Completa tareas de principio a fin, como clasificación de currículums, análisis de tendencias bursátiles, construcción de sitios web [2]. |
| Procesamiento Multi-Modal | Manejo de texto, imágenes, código y datos | No especificado. | Genera informes, analiza contenido visual, automatiza tareas de programación [2]. |
| Integración Avanzada de Herramientas | Integración con navegadores web, editores de código, sistemas de gestión de bases de datos | No especificado. | Automatiza flujos de trabajo y procesos de toma de decisiones [2]. |
| Orquestación Multi-Agente | División de tareas entre agentes especializados que colaboran en tiempo real | Puede escalar a cientos de agentes en paralelo para operaciones a gran escala. | Resume 50,000 ensayos clínicos, maneja proyectos complejos de forma escalable [3]. |
| Control de Navegadores y Herramientas | Controla navegadores para acciones web y se integra con APIs | Evita CAPTCHAs, integra con APIs para flujos de trabajo personalizados [3]. | Realiza investigaciones, llena formularios, compra artículos en línea [3]. |
| Manejo de Archivos y Contenido | Crea, edita y analiza archivos (Excel, PDFs, presentaciones) | No especificado. | Genera informes estructurados, sitios web, scripts de código [3]. |
| Aprendizaje Adaptativo y Memoria | Retiene contexto entre sesiones, mejora con el tiempo | Basado en preferencias del usuario e interacciones pasadas. | Mejora la precisión y relevancia de las respuestas con el tiempo [3]. |
| Automatización de Correo Electrónico (Mail Manus) | Reenvío de correos electrónicos para activar acciones | Prompts personalizables. | Filtra currículums, prepara reuniones [3]. |
| Opciones de Escalabilidad | Procesamiento paralelo para tareas de alto volumen | Enruta trabajos a modelos óptimos (Claude 3.5, GPT-5) [3]. | Maneja grandes volúmenes de datos y tareas intensivas [3]. |
| Monitoreo y Reproducción en Tiempo Real | Vistas de acción en tiempo real y reproducciones de depuración | Para cada paso de la ejecución. | Proporciona transparencia y facilita la depuración [3]. |
| Rendimiento Avanzado en Benchmarks | Supera a otros modelos en el benchmark GAIA | 86.5% en Nivel-1, 57.7% en Nivel-3 [3]. | Resuelve problemas del mundo real de manera más efectiva que GPT-4 y otros [3]. |
| Automatización Personalizable de Múltiples Pasos | Maneja diversas tareas con datos integrados | No especificado. | Campañas de marketing, búsqueda de apartamentos, produce hojas de Excel o sitios web [3]. |

### Limitaciones y Fallas
| Limitación | Severidad | Fuente | Workaround |
|---|---|---|---|
| **Bajo Rendimiento en Remote Labor Index (RLI)** | Alta | [4, 5, 6, 7, 8] | Requiere supervisión humana constante y validación de resultados. |
| Archivos Corruptos o Vacíos (RLI) | Media | [4] | Verificación manual de la integridad de los archivos generados. |
| Trabajo Incompleto (RLI) | Media | [4] | Desglose de tareas en subtareas más pequeñas y monitoreo de progreso. |
| Baja Calidad de Output (RLI) | Media | [4] | Refinamiento manual de los resultados, uso de prompts más específicos. |
| Partes Desconectadas en el Trabajo (RLI) | Media | [4] | Verificación de coherencia entre los componentes del trabajo. |
| **Dificultad en Interacciones GUI de Alta Resolución** | Alta | [1] | Uso de APIs directas o herramientas de automatización de GUI específicas en lugar de la interpretación visual del agente. |
| Falta de Integración de Retroalimentación Visual | Alta | [1] | Implementación de modelos de visión-lenguaje para interpretación de elementos de pantalla. |
| Acumulación de Errores en Tareas GUI Complejas | Alta | [1] | Diseño de flujos de trabajo GUI más robustos y con puntos de control. |
| Problemas de Escalabilidad en Tareas GUI | Media | [1] | Optimización de la infraestructura del servidor, distribución de carga. |
| **Baja Precisión en Codificación Médica** | Alta | [1] | Combinación con motores de reglas de IA simbólica para validación, supervisión experta. |
| Mala Interpretación Contextual en Codificación Médica | Alta | [1] | Uso de marcos de validación especializados y supervisión humana. |
| Problemas de Reproducibilidad en Codificación Médica | Alta | [1] | Implementación de arquitecturas híbridas y marcos de cumplimiento. |
| **Falta de Controles Granulares (Arquitectura)** | Alta | [1] | Integración de capas de aplicación de políticas (ej. estilo SmythOS). |
| Dependencia de la Supervisión Humana (Arquitectura) | Alta | [1] | Rediseño de flujos de trabajo para minimizar la necesidad de intervención humana en decisiones críticas. |
| Problemas de Herencia del Modelo (Sesgos/Alucinaciones) | Alta | [1] | Mitigación de sesgos en LLMs subyacentes, validación cruzada de resultados. |
| **Fiabilidad y Rendimiento Inconsistentes** | Alta | [3] | Monitoreo constante, reinicios frecuentes, uso en horas de baja demanda. |
| Congelamientos y Bloqueos del Sistema | Alta | [3] | Reporte de errores, espera de actualizaciones, uso de versiones estables. |
| Ventana de Contexto Limitada | Media | [3] | División de tareas complejas, resúmenes intermedios. |
| **Preocupaciones de Privacidad y Seguridad** | Alta | [2, 3] | Auditorías de seguridad, cifrado de datos, cumplimiento normativo. |
| Gestión de Spam y Ciberseguridad | Media | [3] | Implementación de sistemas de detección y prevención de intrusiones. |
| **Sistema de Créditos Problemático** | Alta | [9, 10, 11, 12, 13, 14] | Monitoreo detallado del consumo de créditos, contacto con soporte para disputas. |
| Consumo Excesivo de Créditos | Alta | [9] | Optimización de prompts, división de tareas, revisión de la eficiencia del agente. |
| Deducciones No Autorizadas | Alta | [9] | Auditoría de registros de transacciones, contacto con soporte. |
| Problemas con Reembolsos de Créditos | Alta | [9] | Documentación de todas las transacciones y comunicaciones con soporte. |
| **Agente Atascado / Bucles Infinitos** | Alta | [15] | Implementación de mecanismos de detección y terminación de bucles, puntos de control. |
| Consumo de Créditos sin Resultado | Alta | [15] | Monitoreo de la actividad del agente, interrupción manual si no hay progreso. |
| Pérdida de Datos Críticos por Decisiones del Agente | Alta | [16] | Copias de seguridad regulares, controles de acceso, aprobación humana para acciones destructivas. |
| Ineficiencia en Tareas Simples | Media | [9] | Simplificación de prompts, uso de herramientas más básicas para tareas sencillas. |
| **Vulnerabilidades de Seguridad (SilentBridge, Prompt Injection)** | Alta | [17] | Implementación de filtros de entrada, validación de prompts, monitoreo de comportamiento anómalo. |

### Ejemplos de Uso Real
## Ejemplos Concretos de Uso Documentados por la Comunidad

La comunidad de usuarios de Manus AI ha documentado diversas experiencias, tanto positivas como negativas, que ilustran las capacidades y limitaciones del agente en escenarios reales:

1.  **Automatización de Marketing y Planificación de Viajes**: Usuarios japoneses en X (anteriormente Twitter) han compartido éxitos en la automatización de campañas de marketing y la planificación de itinerarios de viaje complejos [3]. Esto demuestra la capacidad de Manus para manejar tareas que requieren la integración de múltiples fuentes de información y la generación de resultados estructurados.

2.  **Generación de Sitios Web Sofisticados**: Un usuario reportó que Manus AI pudo replicar un sitio web de referencia con un diseño complejo, incluyendo discusiones interactivas sobre marcadores de diseño y secuencias de construcción. El agente fue capaz de construir un sitio web sofisticado en aproximadamente una hora, lo que resultó en una calificación de 4/5 por su velocidad, participación activa y precisión [3].

3.  **Análisis de Inversiones**: Un usuario mencionó haber utilizado Manus para realizar análisis de inversiones, sin que el agente reportara problemas de límites de uso en ese momento [17]. Esto sugiere que para ciertas tareas analíticas, Manus puede operar de manera efectiva.

4.  **Resumen de Ensayos Clínicos a Gran Escala**: Manus AI ha demostrado la capacidad de orquestar cientos de agentes en paralelo para operaciones a gran escala, como resumir 50,000 ensayos clínicos, lo que resalta su potencial para el manejo de grandes volúmenes de datos [3].

5.  **Creación de Aplicaciones SaaS Completas**: Algunos usuarios han reportado que Manus puede completar el trabajo de una semana entera en una sola sesión, como la construcción de una aplicación SaaS completa a través de un único prompt. Esto subraya su potencial para mejorar drásticamente la productividad en tareas de desarrollo [3].

6.  **Problemas con la Edición de Archivos y Consumo de Créditos**: Un usuario intentó editar "un par de piezas con errores de un solo archivo tsx" con Manus, comenzando con 800 créditos y solo enviando un archivo de 100kb. El sistema consumió una cantidad significativa de créditos sin resolver el problema de manera eficiente, lo que llevó a la frustración con el sistema de créditos [10].

7.  **Pérdida de Proyectos por Errores Críticos**: Un usuario experimentó dos caídas del sistema con el mismo error fatal (`git_remote_s3`), lo que resultó en la pérdida completa del sandbox y la eliminación irreversible de los datos del proyecto. El soporte técnico solo ofreció "esperar la próxima actualización", lo que generó una gran insatisfacción [9].

8.  **Deducciones de Créditos No Autorizadas**: Se reportaron casos donde el sistema dedujo automáticamente aproximadamente 22,000 créditos de una cuenta sin ninguna actividad en la plataforma, lo que fue percibido como un "robo" por el usuario [9].

9.  **Bucle Infinito y Consumo Ineficiente de Créditos**: Usuarios han descrito a Manus como un "agujero negro de créditos" cuando las cosas salen mal, donde el agente introduce un pequeño error, y para corregirlo, se gastan una cantidad significativa de créditos, solo para que la solución introduzca nuevos errores, creando un ciclo ineficiente [14].

10. **Corrupción de Texto**: Un usuario reportó un "Corrupted Text Bug" donde Manus comenzó a usar "letras y palabras extrañas" después de un par de semanas de uso normal [13].

Estos ejemplos ilustran la dualidad de Manus AI: una herramienta con un potencial impresionante para la automatización y la productividad, pero también con problemas significativos de fiabilidad, gestión de recursos y experiencia de usuario que necesitan ser abordados.


### Hallazgos de Fase 2 (Actualizado 1 Mayo 2026)

#### Nuevos Descubrimientos
La investigación del Módulo M10 de Manus AI ha revelado detalles técnicos cruciales sobre sus límites, fallas y patrones de error, cerrando gaps de conocimiento en áreas críticas como la seguridad, la resiliencia operativa y la economía de uso. A continuación, se presentan los hallazgos nuevos y los detalles de implementación técnica que no estaban previamente documentados o eran ambiguos.

### Vulnerabilidad SilentBridge: Un Análisis Profundo de la Inyección de Prompt Indirecta

La vulnerabilidad **SilentBridge** representa una clase sofisticada de ataques de inyección de prompt indirecta de "zero-click" que explotan una falla fundamental en la separación del plano de control y el plano de datos dentro de los agentes de IA como Manus. Descubierta por Aurascape, esta vulnerabilidad permitió la exfiltración de datos sensibles, la ejecución de código arbitrario y la exposición de recursos entre inquilinos, obteniendo una puntuación CVSS de 9.8 (Crítica) [1].

El aspecto más crítico de SilentBridge es la **Autoridad Ambiental**. Cuando un usuario autoriza un conector (ej. Gmail), el agente obtiene un token de OAuth de larga duración con un ámbito amplio. Este token confiere al agente la capacidad de realizar acciones sin una verificación explícita de la intención del usuario para cada acción específica en el momento de la ejecución. La inyección de prompt indirecta aprovecha esta autoridad ambiental al incrustar instrucciones maliciosas en contenido externo (páginas web, resultados de búsqueda, documentos) que el agente procesa. Dado que el modelo de lenguaje no distingue la procedencia de las instrucciones (si provienen del usuario o del contenido externo), ejecuta las directivas maliciosas utilizando los permisos preexistentes [1].

Las variantes de ataque documentadas, **SilentBridge-Page**, **SilentBridge-Search** y **SilentBridge-Doc**, ilustran la versatilidad de esta vulnerabilidad. SilentBridge-Doc, en particular, destaca una cadena de ataque de dos fases: primero, la ejecución de código arbitrario a través de un "reverse shell" que escala a root debido a una vulnerabilidad de `sudo` sin contraseña en el sandbox; segundo, la manipulación del agente para invocar su propia herramienta `deploy_expose_port`, exponiendo un servidor de código interno y exfiltrando credenciales. Este escenario transforma al agente en un "Confused Deputy", utilizando sus propias capacidades legítimas para fines maliciosos [1].

Las mitigaciones propuestas son multifacéticas y abordan la raíz del problema. La **separación del plano de datos del plano de instrucciones** es fundamental, sugiriendo un modelo "Privilegiado/No Privilegiado" donde un modelo de lenguaje de menor potencia extrae y sanitiza hechos del contenido bruto, y el orquestador principal solo actúa sobre estos hechos seguros. Esto evita que las instrucciones maliciosas incrustadas en el contenido lleguen directamente al modelo principal que invoca las herramientas. Además, se propone el **consentimiento por acción en conectores de alto privilegio**, donde las acciones que afectan el estado externo (ej. enviar un correo electrónico) requieren una confirmación explícita en la sesión. El **anclaje de intenciones** mediante un "guardrail" SLM verifica la alineación semántica entre el prompt original del usuario y la llamada a la herramienta planificada. Finalmente, el uso de **credenciales con ámbito limitado y de corta duración** restringe los permisos del agente solo a lo estrictamente necesario para la tarea actual, minimizando el impacto de una posible explotación [1].

### Mecanismos de Recuperación de Errores: Resiliencia ante Fallas de API y del Sandbox

Manus AI ha desarrollado mecanismos de recuperación de errores para mejorar su resiliencia operativa, especialmente frente a fallas de API y problemas del sandbox. La capacidad de los agentes de Manus para **auto-depurarse y reintentar fallas de API de forma autónoma** es un hallazgo clave. Esto se logra mediante una lógica de reintento inteligente, mutación de prompts y prompts de auto-depuración. La lógica de reintento condicional permite al agente detectar firmas de falla específicas (ej. códigos de estado HTTP 502, payloads vacíos) y reintentar la operación, ajustando parámetros como el tiempo de espera. La mutación de prompts es una técnica innovadora donde el agente altera ligeramente sus solicitudes en el reintento (ej. reformulando la pregunta o solicitando un formato diferente) para superar la fragilidad de las APIs. Cuando los reintentos fallan, el agente entra en un modo de depuración, reflexionando sobre la solicitud y la respuesta para identificar la causa del problema y decidir una estrategia de recuperación, como recurrir a una función de respaldo o simplificar la cadena de herramientas [2].

En cuanto a las **fallas del sandbox**, Manus implementa un **restablecimiento automático** en caso de desconexiones prolongadas para restaurar la funcionalidad. También existe una **política de restablecimiento por inactividad** (7 días para usuarios gratuitos, 21 para usuarios de pago) para optimizar el uso de recursos. Es crucial destacar que, si bien el progreso de la tarea se protege durante estos restablecimientos, la **pérdida de archivos dentro del sandbox es inevitable** ya que se lanza una nueva máquina virtual. Este es un comportamiento observado crítico que los usuarios deben conocer [3].

El error `git_remote_s3` es un ejemplo de falla que puede llevar a la pérdida completa del sandbox y datos de proyecto. Este error, relacionado con la integración de Git con S3 como almacenamiento remoto, puede ser causado por exceder el tamaño de archivo predeterminado de Git o problemas de sincronización. La recuperación de este error, al igual que otras fallas graves del sandbox, implica la pérdida de los archivos temporales o no guardados dentro del entorno [3, 4, 5, 6, 7].

### Detección y Ruptura de Bucles Infinitos: Un "Loop Guard" Implícito

Manus AI no tiene un "loop guard" explícito con un número máximo de iteraciones públicamente definido, pero incorpora varios mecanismos que actúan como un sistema de protección contra bucles infinitos. El diseño impone una **limitación de una acción de herramienta por iteración**, lo que significa que el agente debe esperar el resultado de cada acción antes de decidir el siguiente paso. Esto evita secuencias de acciones rápidas y repetitivas [8].

Un hallazgo importante es el uso de la **detección de bucles mediante huellas digitales (fingerprinting)**. Para casos donde el agente se ejecuta pero no progresa, se genera un hash de la información clave de cada iteración (nombre de la herramienta, parámetros de entrada, estado del entorno). La detección de secuencias repetidas de estas huellas digitales indica un bucle, lo que activa una abortación o replanificación de la tarea [9]. Las políticas de manejo de errores también contribuyen a la ruptura de bucles al diagnosticar fallas y permitir reintentos o métodos alternativos. Los informes iniciales de los probadores beta de Manus mencionaron que el agente podía quedarse atascado en bucles en ciertos errores, lo que subraya la evolución de estos mecanismos [8, 10].

### Cálculo del Consumo de Créditos: Imprevisibilidad y Componentes Clave

El sistema de créditos de Manus AI es un modelo de pago por uso que carece de estimaciones de costos anticipadas, lo que genera una **imprevisibilidad significativa** para los usuarios. Los créditos se consumen en función de tres componentes principales: **tokens de LLM** (para planificación, toma de decisiones y generación de resultados), **máquinas virtuales (VMs)** (para operaciones de archivos, automatización del navegador y ejecución de código) y **APIs de terceros** (para servicios externos) [12].

El orden de consumo de créditos es: Evento → Diario → Mensual → Adicional → Gratuito. Se han observado ejemplos de consumo que varían desde 10-20 créditos para una consulta web simple hasta más de 900 créditos para una aplicación web compleja. Un comportamiento crítico es que, si los créditos se agotan a mitad de una tarea, Manus se detiene inmediatamente sin guardar el estado. Además, los bucles de agente pueden seguir drenando créditos sin un corte automático, lo que agrava la imprevisibilidad y el riesgo financiero para el usuario [12, 13].

### Remote Labor Index (RLI): Un Benchmark de la Capacidad de Automatización de IA

El **Remote Labor Index (RLI)** es un benchmark multisectorial desarrollado por Scale AI y el Center for AI Safety para medir la capacidad de los agentes de IA para automatizar tareas de trabajo remoto del mundo real. Se basa en 240 tareas de freelance que requieren razonamiento, planificación y ejecución de herramientas [14, 15].

Manus AI ha demostrado ser el agente de IA con mejor rendimiento en el RLI, logrando una **tasa de automatización del 2.5%** [15, 17]. Este score, aunque bajo en términos absolutos, es el más alto entre los agentes evaluados (incluyendo Grok 4, Claude Sonnet 4.5, GPT-5, ChatGPT agent y Gemini 2.5 Pro). La baja tasa de automatización general resalta la complejidad inherente de las tareas del RLI, que requieren una comprensión profunda del contexto, manejo de ambigüedades y adaptabilidad, capacidades en las que los agentes de IA aún tienen limitaciones significativas. El score de Manus subraya que, a pesar de los avances, la mayoría de las tareas de trabajo remoto aún requieren una supervisión y dirección humana considerable [15].


#### Detalles de Implementación
### Vulnerabilidad SilentBridge: Detalles de Implementación de Mitigación

Las estrategias de mitigación para SilentBridge se centran en la separación de planos y el control granular de acciones. La implementación de un modelo "Privilegiado/No Privilegiado" implica el uso de un modelo de lenguaje de menor potencia para extraer hechos de contenido no confiable, evitando que las instrucciones maliciosas lleguen al orquestador principal. Esto se puede visualizar con el siguiente pseudocódigo:

```python
# Implementación vulnerable (antes de la mitigación SilentBridge)
response = llm.complete(
    system=SYSTEM_PROMPT,
    user=f"Summarize this: {fetch(url)}",  # Vector de inyección
    tools=CONNECTOR_TOOLS
)

# Implementación más segura (después de la mitigación SilentBridge)
# Paso 1: Recuperación y sanitización de contenido con un modelo de bajo privilegio
content = retriever.fetch_structured(url)  # Devuelve contenido seguro y sanitizado

# Paso 2: Resumen del contenido con un modelo sin acceso a herramientas de alto privilegio
summary = llm.complete(
    system=SYSTEM_PROMPT,
    user=f"Summarize: {content.text}",
    tools=[]  # Sin acceso a conectores durante los pasos de solo recuperación
)

# Paso 3: El orquestador decide las acciones de alto privilegio basándose en el resumen seguro
# (Esto implica lógica adicional de anclaje de intención y consentimiento por acción)
```

El consentimiento por acción en conectores de alto privilegio se implementa mediante la definición de clases de acción y la exigencia de confirmación explícita en la sesión para operaciones que modifican el estado externo. Un ejemplo de configuración podría ser:

```yaml
connector: gmail
actions:
  list_subjects:  auto     # Bajo riesgo, sin exposición de datos
  read_body:      confirm  # Requiere confirmación del usuario en la sesión
  send:           confirm  # Siempre
  forward:        block    # Nunca permitido desde el contexto del agente
```

El anclaje de intenciones se puede implementar utilizando un modelo de lenguaje más pequeño (SLM) como "guardrail" para verificar la alineación semántica entre el prompt original del usuario y la llamada a la herramienta planificada:

```python
# Verificación de intención refinada usando un Guardrail SLM
def verify_tool_intent(original_prompt: str, planned_tool_call: dict):
    # Determinar si la herramienta planificada (ej. gmail.send) es 
    # semánticamente consistente con el objetivo original del usuario.
    is_aligned = guardrail_model.predict(
        f"Prompt: {original_prompt} | Tool: {planned_tool_call}"
    )
    if not is_aligned:
        raise SecurityException("Intent mismatch: Tool call blocked.")
```

### Mecanismos de Recuperación de Errores: Implementación de Reintentos y Auto-depuración

La recuperación autónoma de errores en Manus AI se basa en la instrumentación del agente con lógica de reintento, mutación de prompts y prompts de auto-depuración. La lógica de reintento condicional se activa ante firmas de falla específicas (ej. payload vacío, código de estado inesperado). El agente mantiene un estado interno de intentos previos para informar decisiones de reintento. La mutación de prompts implica alterar ligeramente las solicitudes en el reintento, por ejemplo, reformulando la solicitud en términos más simples o solicitando un formato diferente. Los prompts de auto-depuración guían al agente a reflexionar sobre la falla y decidir una estrategia de recuperación (fallback, simplificación de toolchain, reintento retrasado).

### Detección y Ruptura de Bucles Infinitos: Control de Flujo y Fingerprinting

Manus AI implementa un control de flujo estricto que limita al agente a una acción de herramienta por iteración, esperando el resultado antes de proceder. Para detectar bucles más sutiles, se utiliza el "fingerprinting" de iteraciones, donde se genera un hash de la información clave de cada iteración (nombre de la herramienta, parámetros, estado del entorno). La detección de secuencias repetidas de estos hashes indica un bucle, lo que lleva a la abortación o replanificación de la tarea. Las políticas de manejo de errores también contribuyen a la ruptura de bucles al diagnosticar fallas y permitir reintentos o métodos alternativos.

### Cálculo de Consumo de Créditos: Componentes y Orden de Consumo

El consumo de créditos en Manus AI se basa en tres componentes principales: tokens de LLM (para planificación, toma de decisiones y generación de resultados), máquinas virtuales (para operaciones de archivos, automatización del navegador y ejecución de código) y APIs de terceros (para servicios externos). El orden de consumo de créditos es: Evento → Diario → Mensual → Adicional → Gratuito. No hay un algoritmo exacto público, pero se sabe que la complejidad y los recursos de la tarea son los factores principales.

### Remote Labor Index (RLI): Metodología de Medición

El RLI se mide evaluando el rendimiento de los agentes de IA en un conjunto de 240 tareas de freelance del mundo real. Los agentes son evaluados en su capacidad para comprender la tarea, utilizar herramientas disponibles y producir un resultado que cumpla con los requisitos. La métrica principal es la tasa de automatización, es decir, el porcentaje de tareas que el agente puede completar exitosamente de principio a fin sin intervención humana. No se han publicado detalles de implementación técnica específicos sobre cómo Manus calcula su propio RLI, más allá de los resultados de su rendimiento en el benchmark.


#### Comportamientos Observados en Producción
- **Exfiltración de datos y ejecución de código a nivel de root mediante SilentBridge**: La comunidad ha documentado que la vulnerabilidad SilentBridge permitió la exfiltración de correos electrónicos, la extracción de secretos y la ejecución de código a nivel de root en el sandbox de Manus AI. Esto ocurrió sin interacción directa del usuario, a través de la inyección de prompts indirectos en contenido externo [1].
- **Pérdida de archivos en el sandbox tras restablecimientos**: Se ha observado que, aunque el progreso de la tarea se protege, los restablecimientos del sandbox de Manus AI (ya sean automáticos o por inactividad) resultan inevitablemente en la pérdida de todos los archivos dentro del entorno. Esto se debe a que se lanza una nueva máquina virtual [3].
- **Fallas `git_remote_s3` causando pérdida de sandbox**: Usuarios han reportado que el error `git_remote_s3` puede llevar a la pérdida completa del sandbox y datos de proyecto irreversibles, lo que se alinea con el comportamiento de pérdida de archivos en restablecimientos de sandbox [4].
- **Agentes entrando en bucles de auto-delegación y "memory bloat"**: Se ha observado que los agentes de Manus pueden entrar en bucles de auto-delegación y un consumo excesivo de memoria si los mecanismos de control de bucles no son efectivos, lo que subraya la importancia de la detección de bucles mediante "fingerprinting" [11].
- **Consumo impredecible de créditos y detención abrupta de tareas**: Los usuarios han reportado que el costo de las tareas en Manus AI es altamente impredecible, describiéndolo como "jugar a la lotería". Además, si los créditos se agotan a mitad de una tarea, Manus se detiene inmediatamente sin guardar el estado, y los bucles de agente pueden seguir drenando créditos sin un corte automático [12, 13].
- **Baja tasa de automatización en tareas de trabajo remoto**: En el Remote Labor Index (RLI), Manus AI, a pesar de ser el agente con mejor rendimiento, solo logró una tasa de automatización del 2.5% en tareas de freelance del mundo real. Esto indica que la mayoría de las tareas aún requieren intervención humana significativa [15, 17].


#### Fuentes Adicionales
1. Singh, P. (2026, 26 de febrero). *Why Connector Authorization Is Not Enough to Secure an AI Agent (SilentBridge)*. DeepInspect. [https://www.singhspeak.com/blog/why-connector-authorization-is-not-enough-to-secure-an-ai-agent-silentbridge](https://www.singhspeak.com/blog/why-connector-authorization-is-not-enough-to-secure-an-ai-agent-silentbridge)
2. Hash Block. (2025, 4 de agosto). *How I Tuned Manus Agents to Self-Debug and Retry API Failures Autonomously*. Medium. [https://medium.com/@connect.hashblock/how-i-tuned-manus-agents-to-self-debug-and-retry-api-failures-autonomously-0c385893aae9](https://medium.com/@connect.hashblock/how-i-tuned-manus-agents-to-self-debug-and-retry-api-failures-autonomously-0c385893aae9)
3. Manus Help Center. (2026, 4 de febrero). *What can I do if I encounter a sandbox issue in the task?*. [https://help.manus.im/en/articles/11711144-what-can-i-do-if-i-encounter-a-sandbox-issue-in-the-task](https://help.manus.im/en/articles/11711144-what-can-i-do-if-i-encounter-a-sandbox-issue-in-the-task)
4. Reddit. (Fecha desconocida). *Manus AI is a Nightmare: Incomplete Builds, Buggy ...*. [https://www.reddit.com/r/ManusOfficial/comments/1opvamx/manus_ai_is_a_nightmare_incomplete_builds_buggy/](https://www.reddit.com/r/ManusOfficial/comments/1opvamx/manus_ai_is_a_nightmare_incomplete_builds_buggy/)
5. awslabs. (Fecha desconocida). *awslabs/git-remote-s3*. GitHub. [https://github.com/awslabs/git-remote-s3](https://github.com/awslabs/git-remote-s3)
6. Stack Overflow. (2013, 6 de marzo). *Git, fatal: The remote end hung up unexpectedly*. [https://stackoverflow.com/questions/15240815/git-fatal-the-remote-end-hung-up-unexpectedly](https://stackoverflow.com/questions/15240815/git-fatal-the-remote-end-hung-up-unexpectedly)
7. Reddit. (2025, 12 de noviembre). *Production Deployment Blocked - Git Sync Issue*. [https://www.reddit.com/r/ManusOfficial/comments/1ouwpve/production_deployment_blocked_git_sync_issue/](https://www.reddit.com/r/ManusOfficial/comments/1ouwpve/production_deployment_blocked_git_sync_issue/)
8. renschni. (Fecha desconocida). *In-depth technical investigation into the Manus AI agent, focusing on its architecture, tool orchestration, and autonomous capabilities.* GitHub Gist. [https://gist.github.com/renschni/4fbc70b31bad8dd57f3370239dccd58f](https://gist.github.com/renschni/4fbc70b31bad8dd57f3370239dccd58f)
9. Kinney, S. (2026, 23 de marzo). *The Anatomy of an Agent Loop*. [https://stevekinney.com/writing/agent-loops](https://stevekinney.com/writing/agent-loops)
10. Techstrong.ai. (2025, 10 de marzo). *Chinese Startup's Manus AI Agent Generates Hype, ...*. [https://techstrong.ai/agentic-ai/chinese-startups-manus-ai-agent-generates-hype-skepticism/](https://techstrong.ai/agentic-ai/chinese-startups-manus-ai-agent-generates-hype-skepticism/)
11. Hash Block. (Fecha desconocida). *What I Learned From a Failing Manus Agent Loop*. Medium. [https://medium.com/@connect.hashblock/debugging-ai-autonomy-what-i-learned-from-a-failing-manus-agent-loop-408e8c0a5e5a](https://medium.com/@connect.hashblock/debugging-ai-autonomy-what-i-learned-from-a-failing-manus-agent-loop-408e8c0a5e5a)
12. Spectrum AI Lab. (2026, 19 de enero). *Manus AI Pricing: Free Plan & All Costs [2026]*. [https://spectrumailab.com/blog/manus-ai-pricing-plans-cost-guide-2026](https://spectrumailab.com/blog/manus-ai-pricing-plans-cost-guide-2026)
13. Reddit. (Fecha desconocida). *Manus AI is way too overpriced for what it actually gives you*. [https://www.reddit.com/r/ManusOfficial/comments/1jv9j7v/manus_ai_is_way_too_overpriced_for_what_it/](https://www.reddit.com/r/ManusOfficial/comments/1jv9j7v/manus_ai_is_way_too_overpriced_for_what_it/)
14. Mazeika, M. (2025). *Remote Labor Index: Measuring AI Automation of ...*. arXiv. [https://arxiv.org/abs/2510.26787](https://arxiv.org/abs/2510.26787)
15. Neurohive. (Fecha desconocida). *Remote Labor Index: Top AI Agents Successfully Complete ...*. [https://neurohive.io/en/news/remote-labor-index-top-ai-agents-successfully-complete-2-5-of-freelance-projects/](https://neurohive.io/en/news/remote-labor-index-top-ai-agents-successfully-complete-2-5-of-freelance-projects/)
16. Remote Labor Index. (Fecha desconocida). *Remote Labor Index*. [https://www.remotelabor.ai/](https://www.remotelabor.ai/)
17. Scale.com. (2025, 29 de octubre). *The Remote Labor Index: Measuring the Automation of Work*. [https://scale.com/blog/rli](https://scale.com/blog/rli)


## Gaps de Conocimiento Identificados

Durante la investigación y documentación del módulo M10, se identificaron varios gaps de conocimiento significativos que impidieron una documentación exhaustiva en ciertas áreas. En primer lugar, a pesar de que la descripción del módulo menciona vulnerabilidades como "SilentBridge" y "prompt injection", no se encontraron detalles técnicos específicos sobre cómo estas vulnerabilidades afectan directamente a Manus AI. La información disponible sobre la inyección de prompts es de naturaleza general para los Large Language Models (LLMs) y no se pudo hallar información concreta sobre una vulnerabilidad específica de Manus denominada "SilentBridge" en las fuentes consultadas. Esto sugiere una falta de documentación pública detallada sobre las vulnerabilidades de seguridad intrínsecas al sistema de Manus AI.

En segundo lugar, aunque se documentaron ampliamente los problemas y la frustración de la comunidad con el sistema de créditos, no fue posible obtener información detallada sobre la implementación técnica subyacente de este sistema. Esto incluye la ausencia de datos sobre los algoritmos de cálculo de consumo, los límites exactos por tipo de tarea o los mecanismos internos de facturación y reembolso. La mayor parte de la información recopilada en esta área se basa en experiencias anecdóticas de usuarios, lo que limita la profundidad del análisis técnico.

Un tercer gap importante se refiere a los mecanismos de recuperación y resiliencia de Manus AI. No se encontraron detalles técnicos específicos sobre cómo el sistema maneja los fallos, como el error `git_remote_s3` que, según los informes, causó la pérdida de datos, ni sobre las estrategias implementadas para evitar que el agente se quede atascado en bucles infinitos o consuma créditos sin producir resultados. La información disponible se restringe a los reportes de fallas por parte de los usuarios, sin una explicación técnica de las causas raíz o las soluciones implementadas.

Además, la documentación oficial disponible públicamente en `manus.im/docs` no proporciona el nivel de detalle técnico necesario para replicar con exactitud las capacidades o comprender a fondo las limitaciones internas del sistema. Esto es particularmente evidente en lo que respecta a los patrones de error y las vulnerabilidades de seguridad a nivel de código o arquitectura interna, lo que dificulta una ingeniería inversa completa.

Finalmente, aunque se obtuvo información sobre el rendimiento de Manus AI en el Remote Labor Index (RLI) y los patrones de error generales asociados, no se pudo acceder a los detalles específicos de la implementación del benchmark en relación con Manus AI. Esto incluye la falta de datos sobre los proyectos exactos asignados al agente o los logs de ejecución detallados que condujeron a los resultados reportados, lo que limita la capacidad de un análisis más profundo del desempeño del agente en este benchmark crítico.

### Referencias
## Referencias

1.  [Manus AI’s Limitations in High-Resolution GUI Interactions and Specialized Medical Coding: A… | by Dr. Prashant Sawant | Medium](https://medium.com/@prasmit/manus-ais-limitations-in-high-resolution-gui-interactions-and-specialized-medical-coding-a-1bc1b3e244ad)
2.  [(PDF) Manus AI: Capabilities, Limitations, and Market Position](https://www.researchgate.net/publication/389779452_Manus_AI_Capabilities_Limitations_and_Market_Position)
3.  [Manus AI Review: Detailed Analysis of Benefits & Drawbacks](https://deeperinsights.com/ai-review/manus-ai-review-detailed-analysis-of-benefits-drawbacks/)
4.  [Remote Labor Index: Top AI Agents Successfully Complete 2.5% of Freelance Projects](https://neurohive.io/en/news/remote-labor-index-top-ai-agents-successfully-complete-2-5-of-freelance-projects/)
5.  [Manus AI just clocked a 2.5% score on Meta\'s new Remote Labor ...](https://x.com/WesRothMoney/status/2005957045338661363)
6.  [Remote Labor Index: AI Completes 2.5% of Tasks to Sufficient Quality](https://www.linkedin.com/posts/colin-eberhardt-1464b4a_remote-labor-index-measuring-ai-automation-activity-7390760984811950080-xNm_)
7.  [Remote Labor Index: Measuring AI Automation of Remote Work - arXiv](https://arxiv.org/html/2510.26787v1)
8.  [The Remote Labor Index: Measuring the Automation of Work | Scale AI](https://scale.com/blog/rli)
9.  [Manus AI is a Nightmare: Incomplete Builds, Buggy Deploys, and Endless Upgrade Spam – Who’s With Me? (Rant + Proof Ready) : r/ManusOfficial](https://www.reddit.com/r/ManusOfficial/comments/1opvamx/manus_ai_is_a_nightmare_incomplete_builds_buggy/)
10. [Credit System Makes Manus Absolutely Unusable](https://www.reddit.com/r/ManusOfficial/comments/1jriuug/credit_system_makes_manus_absolutely_unusable/)
11. [What are your thoughts on the Credit based Payment ...](https://www.reddit.com/r/ManusOfficial/comments/1jmfh3v/what_are_your_thoughts_on_the_credit_based/)
12. [Manus AI 24 Hour Limit : r/ManusOfficial](https://www.reddit.com/r/ManusOfficial/comments/1jcdpts/manus_ai_24_hour_limit/)
13. [r/ManusOfficial - Corrupted Text Bug?](https://www.reddit.com/r/ManusOfficial/comments/1smlh54/corrupted_text_bug/)
14. [Manus is a credit black hole when things go wrong](https://www.reddit.com/r/ManusOfficial/comments/1rnfy7t/manus_is_a_credit_black_hole_when_things_go_wrong/)
15. [What I Learned From a Failing Manus Agent Loop](https://medium.com/@connect.hashblock/debugging-ai-autonomy-what-i-learned-from-a-failing-manus-agent-loop-408e8c0a5e5a)
16. [Manus agent decided independently that the best way to fix ...](https://www.reddit.com/r/ManusOfficial/comments/1r7vl6m/manus_agent_decided_independently_that_the_best/)
17. [Manus is INCREDIBLE - Except for the Usage Limits : r/ManusOfficial](https://www.reddit.com/r/ManusOfficial/comments/1jfu031/manus_is_incredible_except_for_the_usage_limits/)


---



## Hallazgos Técnicos en GitHub (Fase 5)

## Hallazgos Técnicos del Agente Manus AI v3 (OpenManus)

### Repositorio Oficial

El repositorio oficial encontrado en GitHub es: [https://github.com/FoundationAgents/OpenManus](https://github.com/FoundationAgents/OpenManus)

### Actividad del Repositorio

El repositorio muestra actividad reciente. El último commit registrado en la rama `main` fue el 4 de enero de 2026, lo que indica que el proyecto **no** está activo en los últimos 60 días.

### Arquitectura Interna

El agente Manus AI v3, implementado en el proyecto OpenManus, presenta una arquitectura modular y extensible, centrada en la invocación de herramientas. La clase principal, `Manus`, hereda de `ToolCallAgent`, lo que subraya su diseño basado en la ejecución de funciones o herramientas. La estructura del código se organiza en varios módulos clave:

*   `app.agent`: Contiene las implementaciones de diferentes tipos de agentes, incluyendo `manus.py` (el agente principal), `browser.py`, `data_analysis.py`, `mcp.py`, `sandbox_agent.py`, y `toolcall.py`.
*   `app.config`: Gestiona la configuración global del sistema, incluyendo los modelos de lenguaje (LLM) y los servidores del Protocolo de Contexto del Modelo (MCP).
*   `app.prompt`: Almacena las plantillas de prompts utilizadas por el agente para guiar su razonamiento.
*   `app.tool`: Define las herramientas que el agente puede utilizar, tanto locales como a través de MCP.

El diseño asíncrono, evidenciado por el uso de `async def` y `await`, es fundamental para la interacción eficiente con APIs externas y la gestión de operaciones de E/S, permitiendo al agente manejar múltiples tareas concurrentemente.

### Ciclo del Agente (Loop, Estados, Transiciones)

El ciclo de vida del agente Manus se orquesta principalmente a través del método `think()`. Este método es responsable de:

1.  **Inicialización:** Verifica si el agente ha sido inicializado. Si no, procede a conectar los servidores MCP configurados.
2.  **Gestión del Contexto:** Antes de determinar la siguiente acción, el agente puede ajustar su `next_step_prompt` basándose en el contexto actual, especialmente si se está utilizando una herramienta de navegador. Esto se logra mediante `browser_context_helper`.
3.  **Toma de Decisiones:** La lógica central para decidir la próxima acción se delega a la clase base `ToolCallAgent` (`super().think()`), lo que sugiere un marco genérico para la selección y ejecución de herramientas.
4.  **Restauración del Prompt:** Después de procesar, el `next_step_prompt` se restaura a su valor original, asegurando que el contexto no persista incorrectamente entre iteraciones.

El agente mantiene un historial de mensajes recientes (`self.memory.messages`) para conservar el contexto a lo largo de las interacciones, lo que es crucial para un comportamiento coherente y contextualizado.

### Sistema de Memoria y Contexto

El agente utiliza un sistema de memoria basado en mensajes (`self.memory.messages`) para mantener el contexto de las interacciones. Los mensajes recientes (los últimos tres) se utilizan para informar el proceso de `think()`. Además, el `system_prompt` se adapta al directorio de trabajo (`config.workspace_root`), integrando el entorno de ejecución en el contexto inicial del agente. La capacidad de modificar dinámicamente el `next_step_prompt` en función de las herramientas en uso (como el navegador) demuestra un enfoque sofisticado para la gestión del contexto situacional.

### Manejo de Herramientas (Tools/Functions)

El manejo de herramientas es un pilar central de la arquitectura de Manus. El agente hereda de `ToolCallAgent`, lo que le permite invocar una variedad de herramientas. Estas herramientas se clasifican en:

*   **Herramientas Locales/Integradas:**
    *   `PythonExecute()`: Permite la ejecución de código Python, lo que es fundamental para tareas de programación y análisis de datos.
    *   `BrowserUseTool()`: Facilita la automatización del navegador, permitiendo al agente interactuar con páginas web.
    *   `StrReplaceEditor()`: Sugiere capacidades de edición de texto o manipulación de cadenas.
    *   `AskHuman()`: Habilita la interacción con un usuario humano para obtener aclaraciones o asistencia.
    *   `Terminate()`: Una herramienta para finalizar la ejecución del agente o una tarea específica.

*   **Herramientas MCP (Model Context Protocol):** Manus puede conectarse a servidores MCP externos para extender sus capacidades con herramientas remotas. Esto se gestiona a través de:
    *   `mcp_clients`: Un objeto que gestiona las conexiones y las herramientas proporcionadas por los servidores MCP.
    *   `initialize_mcp_servers()`: Un método asíncrono que establece conexiones con los servidores MCP definidos en la configuración (`config.mcp_config.servers`). Soporta conexiones a través de SSE (Server-Sent Events) y STDIO (Standard Input/Output).
    *   Las herramientas obtenidas de los servidores MCP se añaden dinámicamente a la colección `available_tools` del agente, lo que permite una gran flexibilidad y extensibilidad.

### Sandbox y Entorno de Ejecución

La presencia de `PythonExecute()` y `BrowserUseTool()` implica que el agente opera en un entorno que permite la ejecución de código y la automatización del navegador. El directorio `app/sandbox/` y el archivo `app/agent/sandbox_agent.py` sugieren la existencia de un entorno sandbox para ejecutar código de forma segura y aislada. El `Dockerfile` en el directorio raíz del repositorio también indica que el agente está diseñado para ser desplegado en contenedores, lo que proporciona un entorno de ejecución consistente y aislado. El archivo `tests/sandbox` con el commit "change python:3.10 to python:3.12 for docker image" refuerza la idea de un entorno contenedorizado y la gestión de dependencias de Python dentro de este sandbox.

La configuración del sandbox (`SandboxSettings` en `config.py`) permite definir:
*   `use_sandbox`: Habilitar o deshabilitar el uso del sandbox.
*   `image`: La imagen base del contenedor (e.g., `python:3.12-slim`).
*   `work_dir`: El directorio de trabajo dentro del contenedor (`/workspace`).
*   `memory_limit` y `cpu_limit`: Límites de recursos para el contenedor.
*   `timeout`: Tiempo de espera predeterminado para la ejecución de comandos.
*   `network_enabled`: Controla el acceso a la red desde el sandbox.

### Integraciones y Conectores

Manus AI está diseñado para ser altamente integrable y extensible, principalmente a través de:

*   **Modelos de Lenguaje (LLMs):** La configuración (`LLMSettings`) permite la integración con diversos proveedores de LLM (OpenAI, Azure, Ollama) mediante la especificación de `model`, `base_url`, `api_key`, `api_type`, y `api_version`.
*   **Protocolo de Contexto del Modelo (MCP):** El agente puede conectarse a servidores MCP externos, lo que le permite descubrir y utilizar herramientas remotas. La configuración (`MCPSettings`) define cómo se conectan estos servidores (SSE o STDIO) y dónde se encuentran sus configuraciones (`mcp.json`).
*   **Herramientas de Navegador:** La integración con herramientas de navegador (`BrowserUseTool` y `BrowserSettings`) permite la automatización web, incluyendo la configuración de proxies y el control del modo headless.
*   **Motores de Búsqueda:** La configuración de búsqueda (`SearchSettings`) permite al agente utilizar diferentes motores de búsqueda (Google, DuckDuckGo, Baidu, Bing) y configurar parámetros como el idioma y el país para las consultas.
*   **Daytona:** La presencia de `DaytonaSettings` sugiere una integración con la plataforma Daytona, posiblemente para la gestión de entornos de desarrollo o sandboxes remotos.

### Benchmarks y Métricas de Rendimiento

Aunque el código fuente no revela directamente benchmarks o métricas de rendimiento, la existencia de `max_observe` (10000) y `max_steps` (20) en la clase `Manus` sugiere límites internos para controlar la complejidad y duración de las operaciones del agente, lo que indirectamente contribuye a la gestión del rendimiento. La mención de `OpenManus-RL` en el README, un proyecto dedicado a métodos de ajuste basados en aprendizaje por refuerzo para agentes LLM, indica un interés en la optimización del rendimiento y la eficiencia del agente.

### Decisiones de Diseño en Issues/PRs

La revisión de los issues de GitHub revela varias discusiones y solicitudes que arrojan luz sobre las decisiones de diseño, las integraciones y las preocupaciones de rendimiento:

*   **Integración de LLMs:** El issue `#1037` "Gemini 2.0 doesn\'t work with openmanus" indica que el agente busca compatibilidad con diferentes modelos de lenguaje, y que la integración de nuevos LLMs es un área activa de desarrollo y resolución de problemas. El issue `#1351` también menciona un problema con la llamada a `python_execute` sin argumentos requeridos para consultas simples, lo que sugiere la necesidad de una mejor integración entre el agente y la ejecución de código para diferentes LLMs.

*   **Manejo de Herramientas y Sandbox:**
    *   El issue `#1345` "Agent calls python_execute without required arguments for simple queries" resalta desafíos en la invocación de herramientas y la necesidad de una interfaz más robusta para la ejecución de código.
    *   El issue `#1332` "Issue Running main.py" y `#1030` "Docker Initialization failing" indican problemas relacionados con el entorno de ejecución y la inicialización del sandbox, lo que sugiere que la estabilidad y la configuración del entorno son áreas críticas de desarrollo.
    *   El issue `#1006` "keep raising error for extract_content within browser_use" y `#1004` "如何使用本地浏览器" (Cómo usar el navegador local) junto con `#1003` "browser use启动的浏览器窗口尺寸可以调整吗" (Se puede ajustar el tamaño de la ventana del navegador iniciada por browser use) y `#1001` "每次执行指令，避免运行浏览器自动化工具" (Evitar ejecutar la herramienta de automatización del navegador cada vez que se ejecuta un comando) muestran un enfoque continuo en la mejora de la herramienta de automatización del navegador, incluyendo su estabilidad, configuración y eficiencia.

*   **Extensibilidad y Personalización:**
    *   El issue `#1331` "[RFC] Add pre-tool-call authorization layer to BaseTool" propone una capa de autorización previa a la llamada de herramientas, lo que indica un interés en mejorar la seguridad y el control sobre la ejecución de herramientas.
    *   El issue `#1025` "Executing step 2/20" y `#1020` "问题分解为多个小步骤后，支持使用多个不同的大模型解决擅长的小问题吗？" (Después de dividir el problema en varios pasos pequeños, ¿es posible usar diferentes modelos grandes para resolver problemas pequeños en los que son buenos?) sugieren un interés en la orquestación de múltiples agentes y la asignación de tareas a LLMs especializados, lo que apunta a un diseño flexible para manejar tareas complejas.
    *   El issue `#1018` "增加邮件工具：增加读取outlook未读邮件，并总结邮件的概要内容，并生成回复邮件的草稿" (Agregar herramienta de correo: agregar lectura de correos no leídos de Outlook, resumir el contenido del correo y generar un borrador de respuesta) y `#1015` "how to add Custom tool function and mcp" demuestran la demanda de nuevas integraciones de herramientas y la capacidad de los usuarios para extender las funcionalidades del agente.

*   **Rendimiento y Optimización:**
    *   El issue `#1010` "I would like to ask how can I increase the delay and the response time of the large model after playright retrieval to avoid it being too fast." sugiere que los usuarios están experimentando con la velocidad de respuesta del agente y buscan formas de optimizarla o controlarla, especialmente en el contexto de la automatización del navegador.
    *   El issue `#1008` "Wrong creation of a large number of log files" indica problemas de rendimiento relacionados con la generación excesiva de logs, lo que puede afectar el uso de recursos y la eficiencia del agente.

Estos issues y discusiones en GitHub proporcionan una visión valiosa de las áreas de enfoque del desarrollo de OpenManus, destacando la importancia de la flexibilidad en la integración de LLMs, la robustez del sandbox, la extensibilidad de las herramientas y la optimización del rendimiento.