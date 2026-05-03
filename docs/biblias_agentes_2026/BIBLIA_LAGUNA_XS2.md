# Biblia de Implementación: Laguna XS.2

**Fecha de Lanzamiento:** 28 de Abril de 2026
**Versión:** XS.2
**Arquitectura Principal:** Mixture of Experts (MoE)

## 1. Visión General y Diferenciador Único

Laguna XS.2 es el modelo de segunda generación de la familia Laguna de Poolside, diseñado específicamente como un agente de codificación de pesos abiertos (open-weight). Su principal diferenciador radica en su eficiencia y capacidad en relación con su tamaño. Con 33 mil millones (33B) de parámetros totales y solo 3 mil millones (3B) activados durante la inferencia, Laguna XS.2 puede ejecutarse en una sola GPU, pero compite con modelos mucho más grandes en tareas de codificación agentic y de horizonte largo.

A diferencia de los agentes tradicionales que dependen en gran medida de la llamada a herramientas (tool calling) con interfaces estructuradas y fijas, Poolside concibe a Laguna XS.2 como un paso hacia agentes que utilizan el software como una interfaz más expresiva. La visión es que un agente capaz de escribir y ejecutar código puede componer acciones, paralelizar el trabajo y construir sus propios sistemas ad-hoc para interactuar con el mundo, superando las limitaciones de las herramientas predefinidas.

## 2. Arquitectura Técnica

La arquitectura de Laguna XS.2 se basa en un enfoque de Mixture of Experts (MoE), lo que permite un alto rendimiento con un costo computacional reducido durante la inferencia.

*   **Parámetros:** 33B parámetros totales, con 3B parámetros activados por token.
*   **Entrenamiento:** Entrenado desde cero en la "Model Factory" de Poolside utilizando 30 billones (30T) de tokens.
*   **Hardware de Entrenamiento:** Todo el proceso, desde la curación de datos hasta el post-entrenamiento, se realizó en hardware NVIDIA (específicamente GPUs NVIDIA Hopper).
*   **Optimizador:** Utiliza una versión optimizada para eficiencia del optimizador Muon.
*   **Infraestructura de Entrenamiento:** Entrenado utilizando la base de código propietaria de Poolside llamada "Titan".
*   **Compatibilidad:** Soporte desde el primer día en NVIDIA TensorRT-LLM y disponibilidad de una versión NVFP4 para un rendimiento óptimo en la arquitectura NVIDIA Blackwell.

## 3. Implementación/Patrones Clave

La implementación de Laguna XS.2 destaca por su enfoque en los datos, el aprendizaje por refuerzo y la integración con un entorno de ejecución.

*   **Curación de Datos y Automixing:** Poolside trata la curación de datos web como una optimización conjunta de calidad y diversidad. Utilizan modelos para puntuar la calidad de los datos, pero retienen intencionalmente porciones de datos de calidad media y baja para preservar la diversidad, lo cual es crítico para la generalización. Este enfoque produce aproximadamente el doble de tokens únicos en comparación con los pipelines centrados únicamente en la precisión.
*   **Datos Sintéticos:** Los datos sintéticos constituyen aproximadamente el 13% de la mezcla de entrenamiento final en todas las etapas de pre-entrenamiento. Se utilizan para complementar los datos web naturales en dimensiones difíciles de controlar, remodelando el contenido en varios formatos (Q&A, listas estructuradas, diálogos) para regularizar la presentación de la información.
*   **Aprendizaje por Refuerzo (RL) de Agente Asíncrono On-Policy:** Laguna XS.2 se beneficia de un esquema de RL de agente asíncrono on-policy, lo que mejora su capacidad para manejar tareas de horizonte largo y codificación agentic.
*   **Arnés de Agente (Agent Harness):** Poolside utiliza un servidor Agent Client Protocol (ACP) como arnés de agente. Este mismo arnés se utiliza tanto para el entrenamiento de RL del agente como para la evaluación, cerrando la brecha entre el modelo y el agente.
*   **Ecosistema de Productos:** Laguna XS.2 se integra con productos como `pool`, un agente de codificación basado en terminal, y `Shimmer`, un entorno de desarrollo en la nube para iterar en aplicaciones web, APIs y CLIs.

## 4. Lecciones para el Monstruo

De la arquitectura y el enfoque de Laguna XS.2, nuestro propio agente puede extraer lecciones valiosas:

*   **Priorizar la Codificación Agentic sobre Tool Calling:** La capacidad de escribir y ejecutar código es fundamental para la verdadera autonomía. Nuestro agente debe evolucionar más allá de la simple llamada a herramientas predefinidas para poder componer acciones complejas y construir soluciones ad-hoc mediante la generación de código.
*   **Eficiencia a través de MoE:** La arquitectura Mixture of Experts demuestra que es posible lograr un rendimiento de nivel de frontera en tareas específicas (como la codificación) manteniendo un tamaño de modelo manejable y eficiente para la inferencia (ej. ejecutable en una sola GPU).
*   **Equilibrio entre Calidad y Diversidad en Datos:** Al curar datos de entrenamiento, no debemos descartar agresivamente los datos que no son de "máxima calidad" si eso compromete la diversidad. La diversidad es crucial para la capacidad de generalización del modelo.
*   **Integración de Datos Sintéticos:** El uso estratégico de datos sintéticos para reformatear y regularizar la información existente puede mejorar significativamente la comprensión del modelo sobre conceptos complejos desde múltiples ángulos.
*   **Unificación de Entrenamiento y Evaluación:** Utilizar el mismo "arnés de agente" (entorno de ejecución) para el entrenamiento por refuerzo y la evaluación asegura que el modelo se optimice para el entorno real en el que operará.

---
*Referencias:*
[1] Introducing Laguna XS.2 and Laguna M.1 — Poolside: https://poolside.ai/blog/introducing-laguna-xs2-m1
[2] Laguna XS.2 and M.1: A Deeper Dive — Poolside: https://poolside.ai/blog/laguna-a-deeper-dive

---

# Biblia de Implementación: Laguna XS.2 (Poolside) — Fase 2

## Introducción

Esta Biblia de Implementación detalla la investigación técnica profunda (Fase 2) sobre **Laguna XS.2**, el modelo de codificación agéntica de pesos abiertos desarrollado por Poolside. Lanzado recientemente, Laguna XS.2 es un modelo Mixture-of-Experts (MoE) con 33 mil millones de parámetros totales y 3 mil millones de parámetros activados por token. Diseñado específicamente para tareas de codificación y trabajo de largo horizonte en máquinas locales, este documento explora su arquitectura interna, capacidades operativas, integraciones y rendimiento en benchmarks estándar de la industria.

## MÓDULO A: Ciclo del agente (loop/ReAct)

El ciclo operativo de Laguna XS.2 se caracteriza por su soporte nativo para el razonamiento, lo que le permite ejecutar un **pensamiento intercalado entre las llamadas a herramientas** [1]. Esta arquitectura sugiere un ciclo de agente fuertemente alineado con el paradigma ReAct (Reasoning and Acting), donde el modelo alterna dinámicamente entre la generación de pensamientos internos para planificar o evaluar situaciones y la ejecución de acciones concretas a través de herramientas externas.

Una característica técnica destacada es la capacidad de controlar este ciclo de razonamiento a nivel de solicitud. Los desarrolladores pueden habilitar o deshabilitar el pensamiento mediante el parámetro `enable_thinking=True` o `False` [1]. Este control granular permite optimizar el rendimiento del agente: en tareas complejas que requieren planificación, el pensamiento intercalado es crucial; en tareas directas o repetitivas, deshabilitarlo puede reducir la latencia y el costo computacional.

La implementación de Laguna XS.2 en entornos como vLLM confirma la existencia de mecanismos especializados para gestionar este ciclo. El uso de parsers específicos, como `--reasoning-parser poolside_v1` y `--tool-call-parser poolside_v1` [1], indica que el sistema subyacente está diseñado para separar, interpretar y procesar de manera distinta el flujo de razonamiento interno y las instrucciones de ejecución de herramientas, asegurando un ciclo ReAct fluido y estructurado.

## MÓDULO B: Estados del agente

Aunque la documentación oficial no proporciona un diagrama de estados explícito, el análisis de sus capacidades revela al menos dos estados operativos fundamentales derivados de su arquitectura de pensamiento intercalado [1]:

1.  **Estado de Razonamiento (Thinking State)**: En este estado, el agente procesa la información contextual, evalúa el progreso hacia el objetivo y formula un plan de acción. La característica de **pensamiento preservado** (`preserved thinking`) [1] es vital aquí, ya que indica que el estado de razonamiento no es efímero, sino que se mantiene y evoluciona a lo largo de la interacción. Esto es esencial para el "trabajo de largo horizonte" para el cual Laguna XS.2 fue diseñado, permitiendo al agente mantener la coherencia en tareas complejas de codificación que requieren múltiples pasos.
2.  **Estado de Acción (Acting State)**: En este estado, el agente transiciona de la planificación a la ejecución, interactuando con su entorno a través de llamadas a herramientas o generando código/texto como respuesta final.

La transición entre estos estados está mediada por la lógica interna del modelo y puede ser influenciada externamente mediante el parámetro `enable_thinking` [1]. Cuando el pensamiento está habilitado, el agente transiciona fluidamente entre razonar y actuar. Cuando está deshabilitado, el agente opera predominantemente en el estado de acción, respondiendo directamente a las solicitudes sin un paso de planificación explícito visible.

## MÓDULO C: Sistema de herramientas

El sistema de herramientas de Laguna XS.2 está intrínsecamente ligado a su propósito como **agente de codificación** [2]. La interacción principal con las herramientas se facilita a través de **pool**, descrito como un "agente de codificación basado en terminal" y un "cliente-servidor de Protocolo de Cliente de Agente (ACP)" [1].

*   **Interfaz de Terminal**: El uso de `pool` sugiere que el sistema de herramientas opera principalmente ejecutando comandos en un entorno de terminal (CLI). Esto implica que las herramientas disponibles para el agente incluyen, pero no se limitan a, la manipulación de archivos, la ejecución de scripts, la compilación de código y la interacción con sistemas de control de versiones (como git).
*   **Protocolo ACP**: La designación de `pool` como cliente-servidor ACP indica un enfoque estandarizado para la comunicación entre el agente y las herramientas o entornos de desarrollo.
*   **Integración con Editores**: La capacidad de configurar `pool` automáticamente con editores de código populares como Zed y JetBrains (`pool acp setup --editor zed|jetbrains`) [1] revela que el sistema de herramientas está diseñado para integrarse profundamente en el flujo de trabajo del desarrollador, permitiendo al agente interactuar directamente con el código fuente en el entorno de desarrollo integrado (IDE).
*   **Selección Autónoma**: En implementaciones como vLLM, la opción `--enable-auto-tool-choice` [1] demuestra que Laguna XS.2 tiene la capacidad de seleccionar de forma autónoma la herramienta más adecuada para una tarea dada, basándose en su razonamiento interno y el contexto de la solicitud.

## MÓDULO D: Ejecución de código

Como modelo diseñado para la "codificación agéntica" [2], la ejecución de código es una capacidad central de Laguna XS.2.

*   **Entorno de Ejecución**: La ejecución de código se realiza típicamente en un **entorno aislado (sandbox)** [2]. Esto se evidencia en la metodología de los benchmarks (como SWE-bench y Terminal-Bench 2.0), donde las tareas se ejecutan en sandboxes con recursos estrictamente definidos (por ejemplo, 8 GB RAM/2 CPUs) [2]. Este aislamiento es crucial para garantizar que el código generado y ejecutado por el agente no comprometa la seguridad o la estabilidad del sistema host.
*   **Lenguajes y Contextos**: Los ejemplos de uso proporcionados en la documentación (como la generación de un "Python retry wrapper") [1] indican una fuerte competencia en **Python**, aunque su evaluación en "SWE-bench Multilingual" [2] sugiere capacidades en múltiples lenguajes de programación. Además, la plataforma **Shimmer** de Poolside, diseñada para "iterar en aplicaciones web, APIs y CLIs" [2], demuestra que el agente puede ejecutar y probar código en diversos contextos de desarrollo de software.
*   **Manejo de Errores**: Aunque los mecanismos internos de manejo de errores no se detallan exhaustivamente, la documentación menciona que durante las pruebas, "algunas imágenes de tareas base y verificadores fueron parcheados para solucionar problemas de fiabilidad de la infraestructura" [2]. Esto sugiere que el entorno de ejecución está diseñado para ser robusto frente a fallos. Además, la capacidad de "pensamiento intercalado" [1] teóricamente permite al agente analizar los errores de ejecución (por ejemplo, un traceback de Python) y formular estrategias para corregir el código y volver a intentarlo.

## MÓDULO E: Sandbox y entorno

El entorno operativo de Laguna XS.2 prioriza el aislamiento y la reproducibilidad, elementos esenciales para un agente de codificación seguro y eficaz.

*   **Aislamiento Estricto**: Como se mencionó en el Módulo D, Laguna XS.2 opera dentro de un **sandbox** [2]. Durante las evaluaciones de rendimiento, este sandbox se configuró con límites de recursos específicos (8 GB RAM/2 CPUs para la mayoría de las pruebas, y 48 GB RAM/32 CPUs para pruebas más intensivas como Terminal-Bench 2.0) [2]. Este enfoque garantiza que las acciones del agente estén contenidas y no afecten al sistema subyacente, previniendo el consumo excesivo de recursos o modificaciones no deseadas en el sistema de archivos del host.
*   **Shimmer (Cloud Sandbox)**: Poolside ofrece **Shimmer**, descrito como una "máquina virtual sandbox instantánea" que viene con el agente de Poolside preinstalado [2]. Shimmer proporciona un entorno de desarrollo en la nube listo para usar, diseñado específicamente para que los desarrolladores construyan y prueben aplicaciones web, APIs y CLIs con la asistencia de Laguna XS.2 y M.1. La existencia de Shimmer subraya la importancia de proporcionar un entorno controlado, seguro y estandarizado para maximizar la utilidad del agente.

## MÓDULO F: Memoria y contexto

Laguna XS.2 exhibe capacidades técnicas avanzadas para gestionar la memoria y el contexto, optimizadas para el "trabajo de largo horizonte" [1].

*   **Ventana de Contexto Masiva**: El modelo cuenta con una **ventana de contexto de 131,072 tokens** [1]. Esta capacidad masiva le permite ingerir y retener grandes volúmenes de información, como bases de código extensas, documentación técnica detallada y largos historiales de interacción. Esta es una característica crítica para tareas de ingeniería de software que requieren comprender el contexto global de un proyecto.
*   **Sliding Window Attention (SWA)**: Para manejar eficientemente esta gran ventana de contexto, Laguna XS.2 implementa una arquitectura de atención mixta. Utiliza **Sliding Window Attention con gating por cabeza** en 30 de sus 40 capas (una proporción de 3:1 entre capas SWA y de atención global) [1]. El SWA (con una ventana de 512 tokens) [1] permite una inferencia más rápida y reduce significativamente los requisitos de memoria de la caché KV, al limitar la atención a un vecindario local de tokens en la mayoría de las capas, mientras que las capas de atención global mantienen la comprensión del contexto a largo plazo.
*   **Optimización de Caché KV**: Además del SWA, la **caché KV se cuantifica a FP8** [1]. Esta técnica de cuantificación reduce drásticamente la huella de memoria por token, lo que es fundamental para permitir que un modelo con una ventana de contexto tan grande se ejecute eficientemente en hardware local con recursos limitados (como un Mac con 36 GB de RAM) [1].
*   **Pensamiento Preservado**: La capacidad de **pensamiento preservado** (`preserved thinking`) [1] actúa como una forma de memoria de trabajo a corto y medio plazo. Permite al agente mantener su estado de razonamiento a través de múltiples interacciones, asegurando la coherencia en la ejecución de planes complejos de varios pasos.

## MÓDULO G: Browser/GUI

La información técnica disponible sobre Laguna XS.2 no indica capacidades directas de interacción con navegadores web o interfaces gráficas de usuario (GUI) [1] [2]. El enfoque principal del agente es la **codificación agéntica** [2] [1], lo que implica una interacción predominante con entornos de desarrollo basados en texto y terminales. El agente `pool` de Poolside, la interfaz principal para Laguna XS.2, se describe explícitamente como un "agente de codificación basado en terminal" [1] [2]. Esto sugiere que su modo de operación se centra en la entrada y salida de texto, la ejecución de comandos y la manipulación de archivos, en lugar de la navegación visual o la interacción con elementos gráficos de una página web.

Aunque la plataforma Shimmer proporciona una "experiencia de desarrollo en la nube para iterar en aplicaciones web, APIs y CLIs" [2], esto se refiere a la capacidad del agente para *ayudar a construir* aplicaciones web, no a su capacidad para *navegar* por ellas. Por lo tanto, no hay evidencia que sugiera que Laguna XS.2 pueda hacer clic en elementos de la interfaz, manejar inicios de sesión en navegadores o extraer información de páginas web de manera autónoma a través de una GUI.

## MÓDULO H: Multi-agente

Las fuentes consultadas no proporcionan detalles sobre las capacidades multi-agente de Laguna XS.2 [1] [2]. El diseño y la descripción del modelo se centran en su funcionalidad como un **agente de codificación individual** [2]. Aunque el agente `pool` se describe como un "cliente-servidor de Protocolo de Cliente de Agente (ACP)" [1], esta designación se refiere a su papel como interfaz de comunicación para Laguna XS.2, no como un marco para la orquestación de múltiples agentes. No hay mención de mecanismos para la creación, coordinación o comunicación entre sub-agentes. Por lo tanto, en base a la información técnica actual, Laguna XS.2 no parece tener funcionalidades multi-agente integradas.

## MÓDULO I: Integraciones

Laguna XS.2 se distingue por su amplia gama de integraciones, lo que facilita su adopción y despliegue en diversos ecosistemas de desarrollo [1] [2]:

*   **Hugging Face**: El modelo está disponible como pesos abiertos (`open-weights`) en la plataforma Hugging Face [2], lo que permite a los desarrolladores descargar y utilizar el modelo directamente, aprovechando el vasto ecosistema de herramientas y recursos de Hugging Face.
*   **API de Poolside**: Poolside ofrece una API oficial para interactuar con Laguna XS.2 y Laguna M.1 [2]. Los desarrolladores pueden obtener claves API en `platform.poolside.ai` para integrar el modelo en sus aplicaciones y flujos de trabajo.
*   **OpenRouter**: El modelo también es accesible a través de OpenRouter [2], una plataforma que consolida el acceso a múltiples modelos de lenguaje, proporcionando una opción adicional para los usuarios.
*   **Ollama**: Para la ejecución local, Laguna XS.2 cuenta con soporte nativo para MLX y se integra con Ollama [1] [2]. Esto permite una configuración sencilla para ejecutar el modelo en máquinas locales mediante el comando `ollama launch pool --model laguna-xs.2` [2].
*   **vLLM**: Laguna XS.2 tiene soporte desde el día de su lanzamiento en vLLM [1], una biblioteca de inferencia de alto rendimiento para LLMs. La integración incluye parsers específicos (`--tool-call-parser poolside_v1`, `--reasoning-parser poolside_v1`) y la opción de selección automática de herramientas (`--enable-auto-tool-choice`) [1].
*   **Hugging Face Transformers**: El modelo es compatible con la biblioteca Transformers de Hugging Face a partir de la versión `v5.7.0` [1], lo que permite a los desarrolladores aprovechar las funcionalidades existentes de Transformers para cargar y utilizar Laguna XS.2.
*   **NVIDIA TRT-LLM (TensorRT-LLM)**: Existe soporte para Laguna XS.2 en TRT-LLM [1], la solución de NVIDIA para optimizar la inferencia de LLMs. Esta integración requiere una compilación específica de TRT-LLM desde una rama de desarrollo que incluye el soporte para Laguna XS.2 [1].
*   **Editores de Código (Zed y JetBrains)**: El agente `pool` de Poolside puede configurarse automáticamente con editores como Zed y JetBrains [1], lo que facilita una integración profunda en el flujo de trabajo de desarrollo, permitiendo al agente interactuar directamente con el código fuente.

## MÓDULO J: Multimodal

La modalidad de Laguna XS.2 se especifica como **text-to-text** [1]. Esto significa que el agente está diseñado fundamentalmente para procesar y generar información en formato textual. Su enfoque principal es la **codificación agéntica** [2], lo que implica la comprensión y manipulación de código fuente, documentación y otros artefactos basados en texto. No hay indicaciones en la documentación técnica de que Laguna XS.2 posea capacidades para procesar o generar imágenes, video, audio u otras formas de datos multimodales. Por lo tanto, no se clasifica como un agente multimodal en el sentido de manejar diversas modalidades de entrada y salida más allá del texto.

## MÓDULO K: Límites y errores

La documentación proporciona información valiosa sobre los límites inherentes y los mecanismos de manejo de errores en el contexto de Laguna XS.2 y su operación [1] [2]:

*   **Límites de Recursos en Sandbox**: Durante las evaluaciones de rendimiento, Laguna XS.2 se ejecutó en entornos de sandbox con recursos estrictamente definidos: un máximo de 500 pasos, 8 GB de RAM y 2 CPUs para la mayoría de los benchmarks, y 48 GB de RAM y 32 CPUs para Terminal-Bench 2.0 [2]. Estos límites establecen las fronteras operativas del agente, lo que implica que tareas que excedan estos recursos podrían experimentar degradación del rendimiento o fallos. Estos límites son cruciales para el control de costos y la prevención de abusos en entornos compartidos.
*   **Fiabilidad de la Infraestructura y Dependencias**: Se ha documentado que "algunas imágenes de tareas base y verificadores fueron parcheados para solucionar problemas de fiabilidad de la infraestructura inherentes a la configuración de la tarea, como límites de tasa en dependencias de terceros en registros externos utilizados por el verificador" [2]. Esto subraya la susceptibilidad del sistema a fallos relacionados con la infraestructura subyacente y las dependencias externas. La necesidad de parches sugiere un enfoque proactivo para mejorar la robustez y la capacidad de recuperación del sistema frente a interrupciones externas.
*   **Límites de Tasa de API**: El acceso a Laguna XS.2 a través de la API de Poolside está sujeto a límites de tasa predeterminados [2]. Aunque existe la posibilidad de solicitar un aumento de estos límites para equipos pequeños, su existencia implica que el uso intensivo del agente a través de la API puede verse restringido, afectando la escalabilidad para ciertos casos de uso. Esto es una práctica común para gestionar la carga del servidor y garantizar un servicio equitativo.
*   **Errores de Compatibilidad**: La integración con bibliotecas como TRT-LLM puede presentar desafíos de compatibilidad, como la necesidad de parches debido a diferencias en las versiones de dependencias (por ejemplo, `transformers >= 4.58` vs. `transformers 4.57`) [1]. Estos errores requieren soluciones específicas y demuestran la complejidad de mantener la compatibilidad en un ecosistema de software en rápida evolución.
*   **Ventana de Contexto**: A pesar de su generosa ventana de contexto de 131,072 tokens [1], existe un límite inherente. Tareas de codificación extremadamente grandes o complejas que superen este umbral podrían experimentar truncamiento de información o una comprensión incompleta del contexto, lo que podría llevar a errores o soluciones subóptimas.
*   **Modo de Fallo y Recuperación**: La capacidad de "pensamiento intercalado" y "pensamiento preservado" [1] sugiere un mecanismo interno para la recuperación de errores, donde el agente puede reevaluar su plan y ajustar su comportamiento en respuesta a resultados inesperados o fallos. Sin embargo, la documentación no detalla explícitamente los modos de fallo específicos del agente o las estrategias automatizadas de recuperación de errores.

## MÓDULO L: Benchmarks

Laguna XS.2 ha sido rigurosamente evaluado en benchmarks estándar de la industria, demostrando un rendimiento notable en tareas de codificación agéntica [2]. Las evaluaciones se llevaron a cabo utilizando el Harbor Framework del Laude Institute, empleando un arnés de agente interno de Poolside. Los parámetros de muestreo fueron consistentes en todas las pruebas (`temperature=0.7` y `top_k=20`), con un límite máximo de 500 pasos por tarea [2].

Los resultados clave para Laguna XS.2 (33B total, 3B activados) son los siguientes [2]:

| Benchmark              | Resultado (mean pass@1) | Detalles                                                                    |
| :--------------------- | :---------------------- | :-------------------------------------------------------------------------- |
| SWE-bench Verified     | 68.2%                   | Promediado sobre 4 ejecuciones.                                             |
| SWE-bench Multilingual | 62.4%                   | Promediado sobre 7 ejecuciones.                                             |
| SWE-bench Pro          | 44.5%                   | Promediado sobre 3 ejecuciones.                                             |
| Terminal-Bench 2.0     | 30.1%                   | Promediado sobre 5 ejecuciones, ejecutado en 48GB RAM/32 CPUs.              |

Estos resultados son particularmente significativos porque Laguna XS.2, a pesar de ser un modelo más pequeño (33B total, 3B activados) con una arquitectura Mixture-of-Experts (MoE), logra un rendimiento competitivo e incluso superior a modelos densos considerablemente más grandes en estas métricas [2]. Por ejemplo, supera a Devstral Small 2 (24B denso) y Gemma 4 (31B denso) en varios de estos benchmarks. Esto resalta la eficiencia y la capacidad de la arquitectura MoE de Laguna XS.2 para tareas de resolución de problemas de software y operación de terminal, validando su diseño para la codificación agéntica.

## Lecciones para el Monstruo

La investigación sobre Laguna XS.2 (Poolside) ofrece varias lecciones valiosas para el desarrollo de agentes de IA, especialmente en el ámbito de la codificación agéntica:

1.  **Eficiencia a través de arquitecturas MoE**: Laguna XS.2 demuestra que los modelos Mixture-of-Experts (MoE) pueden lograr un rendimiento competitivo en tareas complejas (como SWE-bench) con un número significativamente menor de parámetros activos en comparación con modelos densos más grandes [2]. Esto subraya la importancia de explorar arquitecturas eficientes que permitan un alto rendimiento con menores requisitos computacionales, lo que es crucial para la implementación en entornos locales o con recursos limitados.

2.  **La importancia del pensamiento intercalado y preservado**: La capacidad de Laguna XS.2 para el "pensamiento intercalado con pensamiento preservado" [1] es una característica clave para el trabajo de largo horizonte. Permitir que el agente razone explícitamente y mantenga ese razonamiento a lo largo de múltiples pasos mejora la coherencia y la capacidad de abordar problemas complejos. Para el "Monstruo", esto significa que un sistema de razonamiento robusto y persistente es más valioso que simplemente generar respuestas directas.

3.  **Ventanas de contexto masivas son habilitadoras**: Una ventana de contexto de 131,072 tokens [1] es un factor determinante para la capacidad de un agente de codificación para comprender y manipular grandes bases de código. La inversión en técnicas como Sliding Window Attention y la cuantificación de la caché KV para hacer esto factible [1] es una lección sobre cómo la gestión eficiente de la memoria puede desbloquear capacidades de contexto que son críticas para tareas del mundo real.

4.  **Integración profunda con el ecosistema de desarrollo**: La amplia gama de integraciones de Laguna XS.2 (Hugging Face, Ollama, vLLM, Transformers, TRT-LLM, y editores de código como Zed y JetBrains) [1] [2] destaca la necesidad de que los agentes de IA se integren sin problemas en los flujos de trabajo existentes de los desarrolladores. Un agente potente es mucho más útil si es fácilmente accesible y compatible con las herramientas que los ingenieros ya utilizan.

5.  **Sandbox y aislamiento para seguridad y fiabilidad**: La ejecución en entornos de sandbox con recursos definidos [2] es fundamental para la seguridad y la reproducibilidad en la codificación agéntica. Para el "Monstruo", esto implica que cualquier agente que interactúe con código o sistemas debe operar dentro de límites estrictos para prevenir efectos secundarios no deseados y garantizar un comportamiento predecible.

6.  **Enfoque en la codificación agéntica**: El éxito de Laguna XS.2 en benchmarks de codificación como SWE-bench [2] valida el enfoque en la especialización. En lugar de ser un agente de propósito general, su diseño optimizado para la codificación agéntica le permite sobresalir en un dominio específico. Esto sugiere que para construir agentes altamente capaces, la especialización y la optimización para un conjunto de tareas bien definido pueden ser más efectivas que un enfoque excesivamente amplio.

## Referencias

[1] Poolside AI. (2026, April 28). *Introducing Laguna XS.2 and Laguna M.1*. Recuperado de [https://poolside.ai/blog/introducing-laguna-xs2-m1](https://poolside.ai/blog/introducing-laguna-xs2-m1)

[2] Poolside AI. (2026, April 28). *Laguna XS.2 and M.1: A Deeper Dive*. Recuperado de [https://poolside.ai/blog/laguna-a-deeper-dive](https://poolside.ai/blog/laguna-a-deeper-dive)

[3] Hugging Face. (n.d.). *poolside/Laguna-XS.2*. Recuperado de [https://huggingface.co/poolside/Laguna-XS.2](https://huggingface.co/poolside/Laguna-XS.2)


---

## Fase 3 — Módulos Complementarios: Laguna XS.2 (Poolside)

### Estados del Agente

El agente Laguna XS.2 (Poolside) opera bajo el marco del **Agent Client Protocol (ACP)**, un estándar que define la comunicación entre editores de código/IDEs y agentes de codificación [1]. Este protocolo establece un ciclo de vida claro para los agentes, que se puede desglosar en varios estados clave y sus transiciones. Aunque la documentación de Poolside AI menciona que Laguna XS.2 utiliza un "agent harness, an Agent Client Protocol (ACP) server" [2], la especificación del ACP proporciona la base para entender los estados operativos del agente.

Los estados principales que un agente ACP, y por extensión Laguna XS.2, puede transitar son: **Inicialización**, **Configuración de Sesión**, **Turno de Prompt (Ejecución)**, **Pausa/Cancelación**, **Error** y **Completado**.

1.  **Estado de Inicialización**: Este es el estado inicial del agente. Cuando un cliente (como un IDE) desea interactuar con Laguna XS.2, primero debe establecer una conexión. Esto se logra mediante el envío de un mensaje `initialize` del cliente al agente. Si el agente requiere autenticación, el cliente procederá a enviar un mensaje `authenticate`. Este proceso asegura que el agente esté listo para recibir comandos y que la comunicación sea segura y compatible entre las versiones del protocolo [1].

2.  **Estado de Configuración de Sesión**: Una vez inicializado y autenticado, el agente pasa a un estado donde se prepara para una interacción específica. Aquí, el cliente puede optar por crear una nueva sesión de conversación enviando un mensaje `session/new`, o reanudar una sesión existente mediante `session/load` si esta funcionalidad es soportada por el agente. Este estado es crucial para mantener el contexto de las interacciones a lo largo del tiempo, permitiendo que el agente recuerde trabajos previos o configuraciones específicas [1].

3.  **Estado de Turno de Prompt (Ejecución)**: Este es el estado activo donde el agente realiza su trabajo principal. El cliente envía un `session/prompt` que contiene el mensaje o la tarea del usuario. Durante este estado, Laguna XS.2 estaría ejecutando código, analizando problemas o generando soluciones. El agente puede enviar notificaciones `session/update` al cliente para informar sobre el progreso, como fragmentos de mensajes (agente, usuario, pensamiento), actualizaciones de llamadas a herramientas, planes o cambios de modo. También puede realizar operaciones de sistema de archivos o solicitar permisos al usuario según sea necesario para completar la tarea [1]. Este estado representa el ciclo de ejecución principal del agente.

4.  **Estado de Pausa/Cancelación**: Un agente en estado de ejecución puede ser interrumpido. El protocolo ACP permite que el cliente envíe un mensaje `session/cancel` para detener las operaciones en curso del agente. Esto puede llevar al agente a un estado de pausa o a la terminación de la tarea actual, dependiendo de la implementación específica del agente y la naturaleza de la operación. La capacidad de `session/set_mode` también sugiere que un agente podría transicionar a diferentes modos operativos, lo que podría incluir un modo "pausado" donde el agente espera nuevas instrucciones o una reanudación [1].

5.  **Estado de Error**: Si durante cualquiera de los estados anteriores ocurre un problema, el agente transiciona a un estado de error. El protocolo ACP sigue la especificación JSON-RPC 2.0 para el manejo de errores, lo que significa que las respuestas fallidas incluirán un objeto `error` con un `code` y un `message` descriptivos. Esto permite al cliente entender la naturaleza del fallo y tomar las acciones correctivas adecuadas. Los errores pueden surgir de problemas de ejecución de código, fallos en la comunicación, o cualquier otra condición inesperada [1].

6.  **Estado Completado**: Un turno de prompt finaliza cuando el agente envía una respuesta al `session/prompt` que incluye una "razón de detención". Esto indica que el agente ha completado la tarea solicitada o ha llegado a un punto de finalización natural para esa interacción específica. Después de este estado, el agente puede estar listo para un nuevo turno de prompt o para que la sesión sea cerrada [1].

En resumen, el ciclo de vida de Laguna XS.2, basado en el ACP, es dinámico y permite una interacción fluida y controlada entre el cliente y el agente, con mecanismos claros para la gestión de tareas, la notificación de progreso y el manejo de excepciones. La implementación de estos estados es fundamental para la robustez y la capacidad de gestión de un agente de codificación como Laguna XS.2.

### Integraciones y Connectors

Laguna XS.2 (Poolside) se posiciona como un modelo de codificación agéntica con un ecosistema de integración robusto, diseñado para facilitar su uso en diversos entornos de desarrollo y flujos de trabajo. Las capacidades de integración se centran en APIs bien definidas, soporte para plataformas clave y mecanismos de autenticación que garantizan la seguridad y el control [3] [11].

**1. APIs Soportadas:**

Poolside AI ofrece varias APIs para interactuar con Laguna XS.2 y gestionar su entorno:

*   **OpenAI-compatible API**: Esta es la interfaz principal para las solicitudes de modelos. Permite a los desarrolladores enviar solicitudes de completado de chat, listar los modelos disponibles, gestionar el streaming de respuestas y utilizar la funcionalidad de llamada a herramientas (tool calling) con los modelos de Poolside, incluyendo Laguna XS.2. La base de la URL para esta API es `/openai/v1`, lo que facilita su integración en sistemas y herramientas que ya son compatibles con la API de OpenAI [11].
*   **Poolside API**: Esta API está diseñada para la automatización de la administración de Poolside. Se utiliza para tareas como la gestión de usuarios y la membresía de equipos dentro de la plataforma. Su base de URL es `/poolside/v1` [11].
*   **System for Cross-domain Identity Management (SCIM) API**: Para la gestión de identidades y el aprovisionamiento de usuarios, Poolside soporta la API SCIM 2.0. Esto permite a las organizaciones aprovisionar y eliminar usuarios desde un proveedor de identidad compatible, facilitando la integración con sistemas de gestión de usuarios empresariales existentes. La base de URL para esta API es `/scim` [11].

**2. Manejo de Autenticación (OAuth y API Keys):**

La autenticación para acceder a las APIs de Poolside se realiza principalmente a través de **API keys**. Los usuarios deben crear una clave API para autenticar sus solicitudes [12]. Si bien la documentación no detalla explícitamente el soporte directo para OAuth 2.0 como un flujo de autenticación para el acceso a la API del modelo, la presencia de la API SCIM 2.0 sugiere un enfoque en la gestión de identidades empresariales que a menudo se integra con sistemas de SSO (Single Sign-On) y proveedores de identidad que utilizan OAuth/OpenID Connect internamente. Para el acceso programático a las APIs, las API keys son el método estándar [11].

**3. Conectores y Plataformas Soportadas:**

Laguna XS.2 está diseñado para ser accesible y utilizable en una variedad de entornos:

*   **OpenRouter**: Laguna XS.2 está disponible a través de OpenRouter, lo que permite a los desarrolladores y usuarios interactuar con el modelo a través de esta plataforma, que actúa como un agregador de APIs de modelos de lenguaje [3] [4].
*   **Hugging Face**: Los pesos de Laguna XS.2 están disponibles en Hugging Face, lo que facilita su integración en configuraciones locales y permite a la comunidad de investigación y desarrollo experimentar y construir sobre el modelo [10].
*   **Puter.js**: Laguna M.1 y Laguna XS.2 son compatibles con Puter.js, una biblioteca que permite a los desarrolladores integrar estos modelos en sus aplicaciones web y proyectos Node.js [8] [9].
*   **Asistente de VSCode**: Poolside ofrece un asistente para el IDE de VSCode, lo que indica una integración directa en entornos de desarrollo populares para mejorar la experiencia de codificación agéntica [7].
*   **Frameworks de Agentes**: Una publicación en Threads menciona que Laguna XS.2 "works with LangChain/CrewAI/LlamaIndex" [6]. Aunque esta afirmación no se encuentra en la documentación oficial de Poolside, sugiere una compatibilidad o facilidad de integración con estos populares frameworks de desarrollo de agentes de IA, lo que ampliaría significativamente su alcance y aplicabilidad.

**4. Webhooks:**

La documentación actual de Poolside AI no menciona explícitamente el soporte para webhooks. Sin embargo, dado que el Agente Cliente Protocol (ACP) permite que el agente envíe notificaciones `session/update` al cliente para informar sobre el progreso y los cambios [1], es plausible que las implementaciones de clientes puedan configurar sus propios mecanismos para actuar sobre estas actualizaciones, simulando la funcionalidad de un webhook a nivel de aplicación. Para eventos asíncronos o notificaciones push, los desarrolladores podrían implementar sus propios sistemas de escucha que interactúen con las APIs de Poolside o monitoreen el estado del agente a través del ACP.

En resumen, Laguna XS.2 ofrece una base sólida para la integración a través de sus APIs compatibles con OpenAI y específicas de Poolside, junto con la gestión de identidades a través de SCIM. Su disponibilidad en plataformas como OpenRouter y Hugging Face, y las integraciones con IDEs y posibles frameworks de agentes, lo convierten en una herramienta versátil para el desarrollo de software agéntico.

### Referencias

[1] Agent Client Protocol. (n.d.). *Overview - Agent Client Protocol*. Recuperado de [https://agentclientprotocol.com/protocol/overview](https://agentclientprotocol.com/protocol/overview)
[2] Poolside. (n.d.). *Laguna XS.2 and M.1: A Deeper Dive*. Recuperado de [https://poolside.ai/blog/laguna-a-deeper-dive](https://poolside.ai/blog/laguna-a-deeper-dive)
[3] Poolside. (n.d.). *Introducing Laguna XS.2 and Laguna M.1*. Recuperado de [https://poolside.ai/blog/introducing-laguna-xs2-m1](https://poolside.ai/blog/introducing-laguna-xs2-m1)
[4] OpenRouter. (n.d.). *Laguna XS.2 (free) - API Pricing & Providers*. Recuperado de [https://openrouter.ai/poolside/laguna-xs.2:free](https://openrouter.ai/poolside/laguna-xs.2:free)
[5] Sung Kim. (n.d.). *Poolside AI releases Laguna XS.2...*. Threads. Recuperado de [https://www.threads.com/@sung.kim.mw/post/DXsWy13ErKb/poolside-ai-releases-laguna-xs-poolsides-first-open-weight-model-its-a-b-total/](https://www.threads.com/@sung.kim.mw/post/DXsWy13ErKb/poolside-ai-releases-laguna-xs-poolsides-first-open-weight-model-its-a-b-total/)
[6] Jason C. Warner. (n.d.). *We'll be making public all our applications...*. X. Recuperado de [https://x.com/jasoncwarner/status/2049152100521889991](https://x.com/jasoncwarner/status/2049152100521889991)
[7] Puter. (n.d.). *Poolside Laguna M.1 and Laguna XS.2 Are Now Available...*. Recuperado de [https://developer.puter.com/blog/poolside-laguna-m1-and-xs2-in-puter-js/](https://developer.puter.com/blog/poolside-laguna-m1-and-xs2-in-puter-js/)
[8] Puter. (n.d.). *Laguna XS.2 - API, Specs, Playground & Pricing*. Recuperado de [https://developer.puter.com/ai/poolside/laguna-xs.2/](https://developer.puter.com/ai/poolside/laguna-xs.2/)
[9] MLQ.AI. (n.d.). *Poolside Launches Open-Source Laguna XS.2 AI Model...*. Recuperado de [https://mlq.ai/news/poolside-launches-open-source-laguna-xs2-ai-model-for-coding/](https://mlq.ai/news/poolside-launches-open-source-laguna-xs2-ai-model-for-coding/)
[10] Poolside. (n.d.). *API overview*. Recuperado de [https://docs.poolside.ai/api/overview.md](https://docs.poolside.ai/api/overview.md)
[11] Poolside. (n.d.). *Authentication*. Recuperado de [https://docs.poolside.ai/api/authentication.md](https://docs.poolside.ai/api/authentication.md)

## Hallazgos Técnicos en GitHub (Fase 5)

# Hallazgos Técnicos: Laguna XS.2 (Poolside AI)

## 1. URL exacta del repo oficial

El agente de código `pool` de Poolside AI se encuentra en el siguiente repositorio de GitHub: [https://github.com/poolsideai/pool](https://github.com/poolsideai/pool) [1].

El modelo Laguna XS.2, que es utilizado por el agente `pool`, tiene su documentación en el repositorio de Hugging Face Transformers: [https://github.com/huggingface/transformers/blob/main/docs/source/en/model_doc/laguna.md](https://github.com/huggingface/transformers/blob/main/docs/source/en/model_doc/laguna.md) [2].

## 2. Arquitectura interna revelada en el código o issues

El modelo Laguna XS.2 es una familia de modelos de lenguaje de mezcla de expertos (MoE) de Poolside. Las diferencias específicas de Laguna en comparación con un transformador MoE SwiGLU estándar son [2]:

*   **Conteo de cabezas por capa (`num_attention_heads_per_layer`)**: Diferentes capas de decodificador pueden tener diferentes conteos de cabezas de consulta mientras comparten la misma forma de caché KV.
*   **Enrutador MoE Sigmoide con balanceo de carga sin pérdida auxiliar** ([arXiv:2408.15664](https://arxiv.org/abs/2408.15664)) y soft-capping de logits opcional (`moe_router_logit_softcapping`): Las puntuaciones del enrutador son la sigmoide elemento a elemento de los logits de la puerta más un sesgo por experto aprendido (`e_score_correction_bias`) que se añade solo en el momento de la selección.

El agente `pool` en sí mismo es una aplicación que puede ejecutarse en varios modos, lo que sugiere una arquitectura modular [1]:

*   Aplicación interactiva independiente en el terminal.
*   Servidor ACP (Agent Client Protocol) con un editor compatible.
*   Cliente ACP conectado a otro servidor ACP.
*   Ejecución no interactiva con `pool exec`.

## 3. Ciclo del agente (loop, estados, transiciones)

El agente `pool` opera en diferentes modos que influyen en su ciclo de aprobación de herramientas [1]:

*   **Always ask (`default`)**: Solicita aprobación en el primer uso de cada tipo de herramienta.
*   **Accept edits (`accept-edits`)**: Aprueba automáticamente las lecturas y escrituras de archivos del espacio de trabajo.
*   **Allow all (`allow-all`)**: Aprueba automáticamente todas las llamadas a herramientas.
*   **Plan (`plan`)**: Planifica cambios sin modificar el código base.

El agente puede cambiar entre estos modos usando `Shift+Tab` o el comando `/mode <id>`.

## 4. Sistema de memoria y contexto

El agente `pool` utiliza archivos `AGENTS.md` para el contexto del proyecto y las instrucciones. Esto sugiere un sistema de memoria basado en archivos locales que el agente lee para entender el entorno y las tareas [1].

La persistencia de la sesión y las opciones de configuración (modo y modelo) pueden ser persistidas en `pool.json` y se envían al inicio usando `session/set_config_option` [1].

## 5. Manejo de herramientas (tools/functions)

El agente `pool` puede conectarse a servidores MCP (Model Context Protocol) para exponer herramientas adicionales. La gestión de estas herramientas se realiza con `pool mcp` [1].

Ejemplos de configuración de servidores MCP incluyen:

*   Basados en comandos (stdio).
*   Servidores HTTP remotos (ej. Notion).
*   Servidores SSE remotos (ej. Linear).

Las reglas de permisos para las herramientas se pueden configurar en archivos `settings.yaml` a nivel local, de proyecto o personal. Estas reglas permiten o deniegan la ejecución de comandos específicos de shell, utilizando comodines para mayor flexibilidad [1].

## 6. Sandbox y entorno de ejecución

El agente `pool` puede ejecutarse en el terminal del usuario como una aplicación interactiva independiente. También puede funcionar como un cliente ACP, conectándose a otros servidores ACP (como Claude Agent, Codex o Gemini), lo que implica que puede operar en diferentes entornos de ejecución proporcionados por estos servidores [1].

Las reglas de permisos de rutas (`paths`) en los archivos `settings.yaml` controlan el acceso del agente al sistema de archivos, permitiendo o denegando lecturas, escrituras, eliminaciones, movimientos y renombres en rutas específicas [1].

## 7. Integraciones y conectores

El agente `pool` se integra con las siguientes especificaciones de agente abiertas [1]:

*   **AGENTS.md**: Para contexto e instrucciones del proyecto.
*   **Skills**: Permite extender el agente con flujos de trabajo reutilizables.
*   **MCP (Model Context Protocol)**: Para conectar herramientas y fuentes de datos a través de servidores MCP.
*   **ACP (Agent Client Protocol)**: Puede funcionar como servidor ACP para editores (Zed, JetBrains) o como cliente ACP para otros agentes (Claude Agent, Codex, Gemini).

## 8. Benchmarks y métricas de rendimiento

Aunque el repositorio `poolsideai/pool` no detalla benchmarks específicos para el agente `pool`, la información de búsqueda inicial menciona que Laguna XS.2 logra un 68.2% en SWE-bench Verified, un estándar para evaluar agentes de codificación de IA en problemas reales de GitHub [3].

## 9. Decisiones de diseño reveladas en PRs o issues técnicos

La documentación de Hugging Face Transformers menciona que el modelo Laguna XS.2 fue implementado en el repositorio de `transformers` a través de un pull request con el título "Laguna XS.2 implementation (#45673)" [2]. Esto indica que las decisiones de diseño relacionadas con la integración del modelo en el framework de Hugging Face se discutieron y aprobaron en ese PR.

El documento de Hugging Face también hace referencia a un paper de arXiv ([arXiv:2408.15664](https://arxiv.org/abs/2408.15664)) sobre el enrutador MoE Sigmoide con balanceo de carga sin pérdida auxiliar, lo que sugiere una base de investigación sólida para las decisiones de diseño de la arquitectura del modelo [2].

## 10. Cualquier información técnica que NO esté en la documentación oficial del sitio web

La información detallada sobre la arquitectura del modelo Laguna XS.2, incluyendo el conteo de cabezas por capa y el enrutador MoE Sigmoide con balanceo de carga sin pérdida auxiliar, así como las implementaciones específicas en el framework de Hugging Face Transformers, no se encuentra directamente en el README del repositorio `poolsideai/pool`. Esta información proviene de la documentación de Hugging Face Transformers, que es una fuente externa pero relacionada y verificada [2].

El repositorio `poolsideai/pool` es un agente de codificación que utiliza modelos como Laguna XS.2, pero no es el repositorio del modelo en sí. La información sobre el modelo se encuentra en otros lugares, como Hugging Face.

## Referencias

[1] [https://github.com/poolsideai/pool](https://github.com/poolsideai/pool) - Repositorio de GitHub de poolsideai/pool
[2] [https://github.com/huggingface/transformers/blob/main/docs/source/en/model_doc/laguna.md](https://github.com/huggingface/transformers/blob/main/docs/source/en/model_doc/laguna.md) - Documentación de Laguna XS.2 en Hugging Face Transformers
[3] [https://byteiota.com/poolside-laguna-xs-2-open-source-ai-coding-for-mac/](https://byteiota.com/poolside-laguna-xs-2-open-source-ai-coding-for-mac/) - Poolside Laguna XS.2: Open-Source AI Coding for Mac
---
## ACTUALIZACIÓN MAYO 2026

### Estado Actual (Mayo 2026)
- **Última versión/lanzamiento:** Laguna XS.2 (Lanzado el 28 de Abril de 2026 bajo licencia Apache 2.0).
- **Cambios clave desde la Biblia original:** Disponibilidad en plataformas principales como Hugging Face, OpenRouter, Ollama y Baseten. Introducción del arnés de agente de codificación "pool" y el entorno de desarrollo web optimizado para móviles "shimmer".
- **Modelo de precios actual:** Gratuito y de código abierto (licencia Apache 2.0).

### Fortalezas Confirmadas
- Sobresale en codificación agéntica y tareas de horizonte largo, con un fuerte rendimiento en benchmarks como SWE-bench Pro (44.5%) y SWE-bench Verified (68.2%).
- Alta eficiencia que permite su ejecución en una sola GPU (ej. RTX 5090 o Mac con 36GB RAM).
- Integración profunda con entornos locales y editores como Zed y JetBrains.

### Debilidades y Limitaciones Actuales
- Limitado a modalidades de texto a texto; carece de capacidades multimodales.
- Su rendimiento aún está por detrás de algunos modelos de frontera como Claude Sonnet 4.6 en benchmarks específicos.
- Susceptible a problemas de fiabilidad de infraestructura en entornos sandbox y carece de orquestación multi-agente integrada.

### Posición en el Mercado
- **Posición en el mercado:** Alternativa de código abierto altamente capaz y eficiente para codificación agéntica local.
- **Base de usuarios:** Ganando tracción rápidamente entre desarrolladores que buscan agentes de codificación locales y de código abierto.
- **Comparación competitiva:** Compite directamente con modelos como Qwen-3.5, DeepSeek V4-Flash, Devstral 2 y Gemma 4, superando a menudo a modelos densos más grandes.

### Puntuación Global
- **Autonomía:** 8/10
- **Puntuación Global:** 85/100
- **Despliegue:** Local (Open-source self-hosted) / Cloud APIs

### Diferenciador Clave
La capacidad de Laguna XS.2 para ofrecer capacidades de codificación agéntica de nivel de frontera en un paquete MoE altamente eficiente de 33B que puede ejecutarse localmente en una sola GPU, haciéndolo accesible y potente para desarrolladores individuales.
