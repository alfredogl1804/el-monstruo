# Biblia de Implementación: Claude Cowork / Managed Agents (Anthropic)

**Fecha de Lanzamiento:** 8 de abril de 2026
**Versión:** Managed Agents v1 (Claude Cowork)
**Arquitectura Principal:** Desacoplamiento de Cerebro (Brain), Manos (Hands/Sandbox) y Sesión (Session Log).

## 1. Visión General y Diferenciador Único

Claude Cowork es la interfaz de usuario para la arquitectura subyacente de **Managed Agents** de Anthropic. Su diferenciador técnico más importante es el **desacoplamiento radical** de los componentes del agente. En lugar de tener un bucle de agente monolítico que vive dentro del mismo contenedor donde se ejecuta el código, Anthropic separó el sistema en tres entidades independientes: el cerebro (el modelo y su arnés), las manos (el sandbox de ejecución) y la sesión (el registro de eventos duradero).

Esta arquitectura resuelve tres problemas críticos que afectan a la mayoría de los agentes: la fragilidad del entorno de ejecución, la vulnerabilidad a la inyección de prompts (prompt injection) para el robo de credenciales, y la pérdida de contexto en tareas de horizonte largo ("context anxiety").

## 2. Arquitectura Técnica: El Desacoplamiento

### 2.1. El Cerebro (Brain / Harness)
El "arnés" (harness) es el código que envuelve al modelo Claude. Ya no vive dentro del contenedor de ejecución. Llama al contenedor como si fuera cualquier otra herramienta: `execute(name, input) -> string`. Si el contenedor muere, el arnés lo captura como un error de llamada a herramienta y se lo pasa a Claude, quien puede decidir reintentar aprovisionando un nuevo contenedor.

### 2.2. Las Manos (Hands / Sandbox)
El contenedor de ejecución (sandbox) se trata como "ganado" (cattle), no como "mascota" (pet). Es efímero y desechable. Si falla, se inicializa uno nuevo con una receta estándar: `provision({resources})`. No hay necesidad de intentar recuperar un contenedor fallido.

### 2.3. La Sesión (Session Log)
El registro de sesión vive fuera del arnés y del sandbox. Es un registro duradero de eventos. Si el arnés falla, un nuevo arnés puede reiniciarse con `wake(sessionId)`, usar `getSession(id)` para recuperar el registro de eventos y reanudar desde el último evento. Durante el bucle del agente, el arnés escribe en la sesión con `emitEvent(id, event)`.

## 3. Seguridad y Manejo de Credenciales

En diseños acoplados, el código no confiable generado por el LLM se ejecuta en el mismo contenedor que las credenciales, haciendo que una inyección de prompt pueda robar tokens. Managed Agents resuelve esto asegurando que los tokens **nunca sean accesibles desde el sandbox** donde se ejecuta el código de Claude.

- **Integración Git:** El token de acceso del repositorio se usa para clonar el repo durante la inicialización del sandbox y se conecta al remoto git local. Los comandos `git push` y `pull` funcionan desde dentro del sandbox sin que el agente maneje el token directamente.
- **Herramientas MCP (Model Context Protocol):** Los tokens OAuth se almacenan en una bóveda (vault) segura externa. Claude llama a las herramientas MCP a través de un proxy dedicado. Este proxy toma un token asociado con la sesión, obtiene las credenciales correspondientes de la bóveda y realiza la llamada al servicio externo. El arnés nunca tiene conocimiento de las credenciales.

## 4. Gestión de Contexto Largo (Más allá de la Ventana de Contexto)

Las tareas largas a menudo exceden la ventana de contexto de Claude. Las soluciones estándar (como resumir o recortar contexto) implican decisiones irreversibles sobre qué descartar, lo que puede llevar a fallos si se necesita información antigua más adelante.

En Managed Agents, **la sesión no es la ventana de contexto de Claude**. La sesión actúa como un objeto de contexto duradero que vive *fuera* de la ventana de contexto.

- **Interrogación de Contexto:** La interfaz `getEvents()` permite al cerebro interrogar el contexto seleccionando porciones posicionales del flujo de eventos. El cerebro puede retomar la lectura desde donde la dejó, retroceder unos eventos antes de un momento específico, o releer el contexto antes de una acción crítica.
- **Transformación en el Arnés:** Los eventos recuperados pueden ser transformados por el arnés antes de pasar a la ventana de contexto de Claude (ej. para optimizar el caché de prompts). La sesión garantiza el almacenamiento recuperable, mientras que el arnés maneja la ingeniería de contexto específica para el modelo actual.

## 5. Lecciones para el Monstruo

La arquitectura de Managed Agents ofrece un blueprint claro para robustecer al Monstruo:

1.  **Sandboxes Efímeros:** El Monstruo debe tratar sus entornos de ejecución de código como desechables. Si un script falla catastróficamente o el entorno se corrompe, debe poder aprovisionar uno nuevo limpio y continuar, en lugar de intentar arreglar el entorno roto.
2.  **Bóveda de Credenciales Externa:** Implementar un proxy para llamadas a APIs externas donde el código generado por el LLM solo interactúe con el proxy, y este último inyecte las credenciales reales almacenadas de forma segura, previniendo el robo de tokens.
3.  **Estado Fuera del Contexto:** El `StateWriterTool` implementado recientemente es un paso en la dirección correcta, pero debe evolucionar hacia un registro de eventos interrogable (`getEvents()`) que permita al Monstruo "paginar" a través de su historial a largo plazo sin saturar su ventana de contexto activa.

---
*Referencias:*
[1] Anthropic Engineering Blog: Scaling Managed Agents: Decoupling the brain from the hands (Abril 2026)


---

# Biblia de Implementación: Claude Cowork y Managed Agents (Anthropic) — Fase 2

## Introducción

Este documento presenta una investigación profunda de Fase 2 sobre los agentes Claude Cowork y Managed Agents de Anthropic, con el objetivo de expandir la comprensión técnica de su arquitectura y funcionamiento. Basándose en la información disponible públicamente y en artículos técnicos, se detallan los aspectos clave de estos agentes, cubriendo doce módulos fundamentales para su implementación y operación.

## MÓDULO A: Ciclo del agente (loop/ReAct)

El corazón de Claude Managed Agents reside en su concepto de **harness**, un bucle de orquestación que gestiona la interacción entre el modelo Claude y las herramientas externas [1]. Este harness es responsable de invocar a Claude, enrutar sus llamadas a herramientas a la infraestructura pertinente y mantener la persistencia del estado a lo largo del tiempo. La arquitectura sugiere un patrón de tipo ReAct (Reasoning and Acting), donde el agente observa el entorno, razona sobre la mejor acción a tomar y luego ejecuta esa acción a través de sus herramientas [1].

Para tareas de larga duración, Anthropic ha implementado una solución de dos fases: un **agente inicializador** y un **agente de codificación** [3]. El agente inicializador se encarga de configurar el entorno en la primera ejecución, lo que incluye la creación de un script `init.sh`, un archivo `claude-progress.txt` para registrar el progreso, y un commit inicial de Git. Este paso es crucial para establecer una base sólida para el trabajo futuro del agente [3].

El agente de codificación, por su parte, se enfoca en realizar un progreso incremental en cada sesión. Su ciclo de operación típico implica una serie de pasos para "orientarse" antes de proceder con la tarea principal:

1.  **Verificación del directorio de trabajo**: Ejecuta `pwd` para confirmar el directorio actual, ya que solo puede editar archivos dentro de este espacio [3].
2.  **Revisión del progreso anterior**: Lee los logs de Git y el archivo `claude-progress.txt` para entender el trabajo reciente y el estado actual del proyecto [3].
3.  **Selección de la tarea**: Consulta el archivo `feature_list.json` para identificar la característica de mayor prioridad que aún no ha sido completada [3].
4.  **Verificación del entorno**: Revisa la existencia de un script `init.sh` para reiniciar los servidores de desarrollo si es necesario [3].
5.  **Pruebas de funcionalidad básica**: Inicia el servidor de desarrollo y realiza pruebas de extremo a extremo utilizando herramientas de automatización del navegador (como Puppeteer MCP) para asegurar que la funcionalidad fundamental sigue operativa [3].

Una vez completados estos pasos de orientación, el agente procede a trabajar en la nueva característica, asegurándose de dejar el entorno en un "estado limpio" al finalizar la sesión, lo que incluye commits de Git descriptivos y actualizaciones en el archivo de progreso [3]. Los eventos, que son mensajes intercambiados entre la aplicación y el agente (turnos de usuario, resultados de herramientas, actualizaciones de estado), son fundamentales para este ciclo, permitiendo la dirección y la interrupción del agente a mitad de la ejecución [2].

## MÓDULO B: Estados del agente

El estado de un agente en Claude Managed Agents se define principalmente a través de la **sesión**, que es una instancia de agente en ejecución dentro de un entorno específico, dedicada a una tarea y a la generación de resultados [2]. La sesión actúa como un registro de solo anexión (`append-only log`) de todos los eventos y acciones que han ocurrido [1].

Esta persistencia del historial de eventos en el servidor es crucial para la robustez del sistema. Permite que el agente sea reiniciado (`wake(sessionId)`) y reanude su trabajo desde el último evento registrado, recuperando el historial completo de la sesión (`getSession(id)`) [1]. La durabilidad de este registro asegura que el estado del agente persista incluso frente a fallos del harness, evitando la pérdida de contexto y progreso [1].

Además de la sesión, otros elementos contribuyen al estado persistente del agente, especialmente en tareas de desarrollo de software:

*   **`claude-progress.txt`**: Un archivo que registra las acciones y el progreso de los agentes, permitiendo que las sesiones futuras se pongan al día rápidamente [3].
*   **Logs de Git**: El historial de versiones de Git es fundamental para rastrear los cambios en el código y permite al agente revertir modificaciones incorrectas o recuperar estados de trabajo anteriores [3].
*   **`feature_list.json`**: Un archivo JSON que detalla los requisitos de las características, indicando cuáles están completas o pendientes. Este archivo es editado por el agente para reflejar el progreso, y su formato JSON ayuda a prevenir modificaciones inapropiadas por parte del modelo [3].

Estos componentes trabajan en conjunto para proporcionar un estado detallado y recuperable para el agente, permitiéndole gestionar tareas complejas y de larga duración a través de múltiples interacciones y sesiones.

## MÓDULO C: Sistema de herramientas

El sistema de herramientas en Claude Managed Agents se conceptualiza como las "manos" del agente, desacopladas del "cerebro" (el modelo Claude y su harness) [1]. Esta separación permite una gran flexibilidad y extensibilidad. Cada herramienta se invoca a través de una interfaz genérica: `execute(name, input) → string`, donde `name` es el identificador de la herramienta y `input` son sus parámetros [1].

Claude Managed Agents ofrece un conjunto completo de herramientas integradas que permiten al agente interactuar con su entorno de ejecución y con servicios externos [2]:

*   **Bash**: Permite ejecutar comandos de shell directamente en el contenedor del agente. Esto es fundamental para tareas de automatización, configuración del entorno y ejecución de scripts [2].
*   **Operaciones de archivos**: Incluye funcionalidades para leer, escribir, editar, buscar por patrón (`glob`) y buscar por contenido (`grep`) archivos dentro del contenedor. Estas operaciones son esenciales para la gestión de proyectos de software y la manipulación de datos [2].
*   **Búsqueda y recuperación web**: Habilita al agente para buscar información en la web y recuperar contenido de URLs específicas. Esta capacidad es vital para la investigación, la recopilación de datos y la interacción con recursos en línea [2].
*   **Servidores MCP (Model Context Protocol)**: Permiten la conexión a proveedores de herramientas externas. Esta es una capacidad clave para la integración con una amplia gama de servicios y APIs de terceros [2].

Para la gestión segura de credenciales, especialmente con herramientas como Git y MCP, Anthropic ha implementado un enfoque robusto [1]:

*   **Git**: Los tokens de acceso a repositorios se utilizan para clonar el repositorio durante la inicialización del sandbox y se configuran en el remoto local. El agente puede realizar operaciones `push` y `pull` sin manejar directamente el token, lo que mejora la seguridad [1].
*   **Herramientas personalizadas (vía MCP)**: Los tokens OAuth se almacenan en una bóveda segura fuera del sandbox. Claude invoca las herramientas MCP a través de un proxy dedicado que recupera las credenciales correspondientes de la bóveda y realiza la llamada al servicio externo. De esta manera, el harness nunca tiene acceso directo a las credenciales [1].
*   **Puppeteer MCP**: Se ha identificado el uso de Puppeteer MCP como una herramienta específica para la automatización del navegador, lo que permite a Claude realizar pruebas de extremo a extremo y simular interacciones de usuario en interfaces gráficas [3].

La modularidad y la seguridad en el diseño del sistema de herramientas son fundamentales para la capacidad de Claude Managed Agents de operar de manera autónoma y segura en una variedad de contextos.

## MÓDULO D: Ejecución de código

Claude Managed Agents está diseñado para ejecutar código dentro de un entorno controlado y seguro conocido como **sandbox** [1]. Esta capacidad es fundamental para que el agente pueda realizar tareas de desarrollo de software, automatización y manipulación de datos. La ejecución de código se realiza principalmente a través de la herramienta **Bash**, que permite al agente ejecutar comandos de shell directamente en el contenedor [2].

Los entornos de los agentes se configuran como plantillas de contenedor que pueden incluir una variedad de paquetes preinstalados, lo que sugiere soporte para múltiples lenguajes de programación. La documentación menciona explícitamente el soporte para **Python, Node.js y Go**, lo que valida la capacidad de ejecutar código en estos lenguajes dentro del sandbox [2].

El proceso de ejecución de código se integra con el ciclo del agente. Por ejemplo, el agente inicializador crea un script `init.sh` que puede ser ejecutado por el agente de codificación para configurar o reiniciar el entorno de desarrollo [3]. Esto demuestra una interacción fluida entre la lógica del agente y la ejecución de código en el sandbox.

Un aspecto crítico de la ejecución de código es la **seguridad**. Anthropic ha implementado una solución estructural para garantizar que el código no confiable generado por Claude nunca pueda acceder a las credenciales del entorno [1]. Esto se logra asegurando que los tokens de autenticación no sean accesibles desde el sandbox donde se ejecuta el código. Las credenciales pueden agruparse con un recurso o mantenerse en una bóveda externa al sandbox, lo que previene ataques de inyección de prompt que intenten acceder a información sensible [1].

## MÓDULO E: Sandbox y entorno

El **sandbox** es el entorno de ejecución aislado donde Claude Managed Agents opera, ejecuta código y manipula archivos [1]. Este entorno es un **contenedor gestionado** en la nube, lo que proporciona un alto grado de aislamiento, seguridad y reproducibilidad [2].

Las características clave del sandbox y su entorno incluyen:

*   **Aislamiento**: Cada sesión de agente se ejecuta dentro de un contenedor dedicado, lo que garantiza que las operaciones de un agente no interfieran con otras sesiones o con la infraestructura subyacente. Este aislamiento es crucial para la estabilidad y la seguridad [1].
*   **Configuración flexible**: Los entornos se definen mediante plantillas de contenedor configurables. Estas plantillas permiten especificar paquetes preinstalados (como Python, Node.js, Go), reglas de acceso a la red y archivos montados. Esta flexibilidad permite adaptar el entorno a las necesidades específicas de cada tarea o agente [2].
*   **Seguridad robusta**: La seguridad es una prioridad fundamental. Se ha implementado una separación estricta entre el "cerebro" del agente (Claude y su harness) y el "sandbox" (las "manos" que ejecutan el código) [1]. Esto asegura que las credenciales sensibles nunca sean accesibles desde el sandbox donde se ejecuta el código generado por Claude. Los tokens de autenticación se gestionan externamente, ya sea agrupados con un recurso o almacenados en una bóveda segura, y se accede a ellos a través de proxies dedicados para herramientas como Git y MCP [1].
*   **Recursos**: Aunque no se detallan los recursos específicos (CPU, RAM), el hecho de que se ejecute en contenedores gestionados implica que los recursos son asignados y escalados según sea necesario por la infraestructura de Anthropic. La mención de la reducción del TTFT (Time-To-First-Token) en un 60% (p50) y más del 90% (p95) gracias al desacoplamiento del cerebro y las manos, sugiere una optimización significativa en la asignación y gestión de recursos para mejorar la latencia percibida por el usuario [1].

El diseño del sandbox como un entorno de "cattle" (ganado) en lugar de "pet" (mascota) significa que los contenedores son desechables y pueden ser reemplazados fácilmente en caso de fallo, sin perder el estado de la sesión gracias a la persistencia del registro de eventos [1].

## MÓDULO F: Memoria y contexto

La gestión de la memoria y el contexto en Claude Managed Agents es un aspecto fundamental para su capacidad de manejar tareas complejas y de larga duración, superando las limitaciones de la ventana de contexto de los modelos de lenguaje [1]. El sistema se basa en el concepto de **sesión** como un objeto de contexto duradero que reside fuera de la ventana de contexto directa de Claude [1].

Las características clave de la memoria y el contexto incluyen:

*   **Registro de sesión duradero**: El contexto se almacena de forma persistente en un registro de sesión (`session log`) de solo anexión. Este registro contiene todos los eventos que han ocurrido durante la vida útil de una sesión [1].
*   **Interfaz `getEvents()`**: Permite al "cerebro" del agente interrogar el contexto almacenado en el registro de sesión. Esta interfaz es flexible y permite al agente seleccionar segmentos posicionales del flujo de eventos, lo que significa que puede retomar la lectura desde donde la dejó, rebobinar unos pocos eventos antes de un momento específico o releer el contexto antes de una acción determinada [1].
*   **Transformación de eventos**: Los eventos recuperados del registro de sesión pueden ser transformados por el harness antes de ser pasados a la ventana de contexto de Claude. Estas transformaciones pueden incluir la organización del contexto para optimizar la tasa de aciertos de la caché de prompts y otras técnicas de ingeniería de contexto [1]. Esta separación de preocupaciones garantiza que el almacenamiento del contexto sea recuperable y que la gestión del contexto pueda evolucionar con los modelos futuros [1].
*   **Externalización del estado**: Para tareas de desarrollo de software, se utilizan archivos como `claude-progress.txt` y `feature_list.json`, junto con los logs de Git, para externalizar y persistir el estado del proyecto. Estos archivos actúan como una forma de memoria a largo plazo que el agente puede consultar para entender el progreso y el estado actual del trabajo, incluso a través de múltiples sesiones y reinicios [3].
*   **Compactación y recorte de contexto**: Aunque la compactación por sí sola no es suficiente para tareas de larga duración, el harness soporta técnicas como la compactación (para que Claude guarde un resumen de su ventana de contexto) y el recorte de contexto (para eliminar selectivamente tokens como resultados de herramientas antiguos o bloques de pensamiento) [1, 2]. Sin embargo, se reconoce que las decisiones irreversibles sobre qué retener o descartar pueden llevar a fallos, lo que subraya la importancia del registro de sesión duradero [1].

Esta arquitectura de memoria y contexto permite a Claude Managed Agents superar las limitaciones inherentes a las ventanas de contexto de los LLM, facilitando la ejecución de tareas complejas y de larga duración con una comprensión coherente del estado del proyecto.

## MÓDULO G: Browser/GUI

Claude Managed Agents posee capacidades explícitas para interactuar con entornos web y, por extensión, con interfaces gráficas de usuario (GUI), aunque los detalles finos de esta interacción son abstractos para el agente [2, 3].

Las herramientas clave que habilitan esta funcionalidad son:

*   **Búsqueda y recuperación web**: Esta herramienta permite a Claude buscar información en la web y recuperar contenido de URLs. Es una capacidad fundamental para la investigación y la recopilación de datos en línea [2].
*   **Puppeteer MCP**: Se ha confirmado el uso de Puppeteer MCP como una herramienta de automatización del navegador [3]. Esto significa que Claude puede simular interacciones de usuario en un navegador web, como hacer clic en elementos, introducir texto en campos y navegar por páginas. Esta capacidad es crucial para realizar pruebas de extremo a extremo de aplicaciones web, verificando la funcionalidad como lo haría un usuario humano [3].

Es importante destacar que, si bien el agente puede interactuar con la web, el harness abstrae el entorno de ejecución. El artículo de Anthropic menciona que el harness "no sabe si el sandbox es un contenedor, un teléfono o un emulador de Pokémon" [1]. Esto implica que la interacción con la GUI se realiza a través de una interfaz estandarizada, y el agente no necesita comprender los detalles de la renderización o la plataforma subyacente. Sin embargo, se ha identificado una limitación: Claude no puede "ver" modales de alerta nativos del navegador a través de Puppeteer MCP, lo que puede causar problemas en características que dependen de ellos [3]. Los detalles sobre cómo maneja los inicios de sesión o la gestión de cookies no se especifican en la información disponible, pero la capacidad de usar herramientas de automatización del navegador sugiere que puede manejar flujos de autenticación si se le instruye adecuadamente.

## MÓDULO H: Multi-agente

La arquitectura de Claude Managed Agents está diseñada para soportar y escalar a escenarios multi-agente, aunque algunas de estas capacidades están en vista previa de investigación [1, 2]. El concepto de "muchos cerebros, muchas manos" es central en este diseño [1].

Las características que habilitan la capacidad multi-agente incluyen:

*   **Desacoplamiento Cerebro-Manos**: La separación del "cerebro" (Claude y su harness) de las "manos" (sandboxes y herramientas) permite que múltiples instancias de Claude (múltiples "cerebros") operen de forma independiente. Cada "cerebro" puede ser un harness sin estado que se conecta a las "manos" solo cuando es necesario, lo que mejora la escalabilidad y el rendimiento [1].
*   **Compartición de "Manos"**: El diseño permite que los "cerebros" pasen "manos" (herramientas o sandboxes) entre sí. Esto sugiere un mecanismo de coordinación y delegación donde diferentes agentes pueden colaborar compartiendo recursos o capacidades de ejecución [1].
*   **Arquitectura de Agentes Especializados**: Para tareas complejas como el desarrollo de aplicaciones, Anthropic ha explorado una arquitectura de tres agentes: un **planificador**, un **generador** y un **evaluador** [3].
    *   El **planificador** se encarga de descomponer la tarea principal en subtareas y definir los requisitos.
    *   El **generador** implementa las características de forma incremental.
    *   El **evaluador** verifica la funcionalidad y la calidad del código.
    Esta especialización y colaboración entre agentes demuestran un enfoque multi-agente para abordar problemas complejos [3].
*   **Sesiones Multiagente**: La documentación de la API menciona explícitamente las "sesiones multiagente" como una característica en vista previa de investigación [2]. Esto indica que Anthropic está desarrollando activamente funcionalidades para la coordinación y gestión de múltiples agentes trabajando en conjunto.

Aunque los detalles específicos sobre los mecanismos de coordinación complejos o la creación explícita de sub-agentes no se detallan completamente, la base arquitectónica y las características mencionadas apuntan a un sistema con un fuerte potencial para la colaboración multi-agente, donde diferentes instancias de Claude pueden trabajar en conjunto para lograr objetivos más grandes.

## MÓDULO I: Integraciones

Claude Managed Agents está diseñado con una fuerte capacidad de integración, permitiendo la conexión con una variedad de servicios externos y APIs [1, 2]. El sistema de herramientas es el principal facilitador de estas integraciones.

Las vías de integración clave incluyen:

*   **Servidores MCP (Model Context Protocol)**: Esta es una herramienta integrada que permite a Claude Managed Agents conectarse a proveedores de herramientas externas [2]. El protocolo MCP actúa como un puente para que el agente interactúe con servicios de terceros. Para garantizar la seguridad, los tokens OAuth para estas herramientas se almacenan en una bóveda segura fuera del sandbox. Claude invoca las herramientas MCP a través de un proxy dedicado que recupera las credenciales de la bóveda y realiza la llamada al servicio externo, asegurando que el harness nunca tenga acceso directo a las credenciales [1].
*   **Herramientas personalizadas**: El sistema es compatible con "cualquier herramienta personalizada", lo que significa que los desarrolladores pueden crear sus propias herramientas y conectarlas al harness del agente. Esto proporciona una flexibilidad ilimitada para extender las capacidades de Claude a cualquier servicio o sistema [1].
*   **Integración con Git**: Para tareas de desarrollo de software, Claude Managed Agents se integra con sistemas de control de versiones como Git. Los tokens de acceso a repositorios se utilizan de forma segura para clonar repositorios durante la inicialización del sandbox, permitiendo al agente realizar operaciones de `push` y `pull` sin manejar directamente las credenciales [1].
*   **APIs de terceros**: La capacidad de conectarse a servidores MCP y herramientas personalizadas implica que Claude puede interactuar con cualquier API de terceros, siempre que se configure una herramienta o un conector MCP adecuado. Esto abre la puerta a integraciones con bases de datos, servicios en la nube, plataformas de comunicación, etc.

La gestión segura de OAuth y otras credenciales a través de bóvedas y proxies dedicados es un pilar fundamental de la estrategia de integración de Anthropic, garantizando que las interacciones con servicios externos se realicen de manera segura y controlada [1].

## MÓDULO J: Multimodal

Claude Managed Agents demuestra capacidades multimodales, lo que le permite procesar y trabajar con diferentes tipos de datos más allá del texto. Aunque los detalles específicos de los modelos subyacentes no se proporcionan en la documentación principal, la información disponible sugiere un enfoque creciente en la multimodalidad [2, 3].

Las evidencias de capacidades multimodales incluyen:

*   **Imágenes y visión**: La documentación de la API menciona explícitamente "Imágenes y visión" como una capacidad [2]. Esto indica que Claude Managed Agents puede procesar entradas visuales. Además, el lanzamiento de **Claude Design** por Anthropic Labs, que permite a los usuarios "colaborar con Claude para crear trabajo visual pulido", refuerza la idea de que Claude tiene habilidades en el procesamiento y la generación de imágenes [3]. Esto podría implicar la capacidad de analizar imágenes, generar gráficos o incluso asistir en tareas de diseño gráfico.
*   **Soporte de PDF**: La documentación también lista "Soporte de PDF" como una capacidad [2]. Esto es significativo ya que los archivos PDF pueden contener una mezcla compleja de texto, imágenes, gráficos y formatos. La capacidad de procesar PDFs implica que el agente puede extraer y comprender información de documentos estructurados y visuales.
*   **Automatización del navegador**: El uso de herramientas como Puppeteer MCP para la automatización del navegador implica que Claude puede "ver" y reaccionar a elementos visuales en una página web, aunque con ciertas limitaciones (como los modales de alerta nativos) [3]. Esta interacción visual, aunque mediada por una herramienta, es una forma de multimodalidad en la que el agente interpreta una representación visual del entorno.

Aunque no se detallan los modelos específicos de visión por computadora o procesamiento de audio utilizados, la existencia de estas capacidades posiciona a Claude Managed Agents como un sistema que puede interactuar con un mundo más allá del texto, abriendo puertas a aplicaciones en campos como el diseño, el análisis de documentos y la interacción con interfaces gráficas complejas.

## MÓDULO K: Límites y errores

La experiencia de Anthropic en el desarrollo de Claude Managed Agents ha revelado varios límites y modos de fallo, y la arquitectura actual está diseñada para mitigar muchos de ellos [1, 3].

**Límites inherentes y desafíos iniciales:**

*   **"Ansiedad de contexto"**: Modelos anteriores de Claude (como Claude Sonnet 4.5) mostraban una tendencia a terminar tareas prematuramente al sentir que se acercaba el límite de su ventana de contexto [1]. Aunque las mejoras en modelos posteriores (como Claude Opus 4.5) han reducido este comportamiento, la gestión del contexto sigue siendo un desafío fundamental [1].
*   **Decisiones irreversibles de contexto**: Las decisiones sobre qué información retener o descartar dentro de la ventana de contexto pueden ser irreversibles y llevar a fallos si se elimina información crucial para turnos futuros. El registro de sesión duradero busca mitigar esto al proporcionar un contexto recuperable fuera de la ventana directa del LLM [1].
*   **"One-shotting" y finalización prematura**: Los agentes tendían a intentar hacer demasiado a la vez, agotando el contexto, o declaraban el trabajo terminado prematuramente sin haber completado todas las características [3]. Esto se aborda con un enfoque de progreso incremental y una lista de características explícita [3].

**Modos de fallo y mitigaciones:**

*   **Fallo del contenedor ("Pet" problem)**: En diseños iniciales, si un contenedor fallaba, la sesión se perdía y la depuración era difícil. El desacoplamiento del "cerebro" y las "manos" convierte los contenedores en "cattle" (ganado), permitiendo que un contenedor fallido sea reemplazado sin perder el estado de la sesión, ya que el harness captura el fallo como un error de llamada a herramienta y Claude puede reintentar [1].
*   **Fallo del harness**: Dado que el registro de sesión reside fuera del harness, un fallo del harness no resulta en la pérdida de estado. Un nuevo harness puede ser reiniciado (`wake(sessionId)`) y recuperar el historial de eventos (`getSession(id)`) para reanudar el trabajo [1].
*   **Seguridad (inyección de prompt)**: La preocupación de que el código generado por Claude pudiera acceder a credenciales sensibles se aborda estructuralmente. Los tokens de autenticación nunca son accesibles desde el sandbox donde se ejecuta el código, y se utilizan bóvedas seguras y proxies para gestionar las credenciales [1].
*   **Pruebas inadecuadas**: Claude tendía a marcar características como completas sin pruebas exhaustivas. Esto se mitiga instruyendo al agente para que utilice herramientas de automatización del navegador (como Puppeteer MCP) para realizar pruebas de extremo a extremo, simulando el comportamiento de un usuario humano [3].
*   **Limitaciones de herramientas**: Una limitación específica identificada es que Claude no puede "ver" modales de alerta nativos del navegador a través de Puppeteer MCP, lo que puede causar problemas en características que dependen de ellos [3].

**Límites de tasa:**

*   **Creación de endpoints**: 300 solicitudes por minuto para la creación de agentes, sesiones, entornos, etc. [2].
*   **Lectura de endpoints**: 600 solicitudes por minuto para recuperar, listar, transmitir, etc. [2].
*   **Límites de gasto**: Se aplican límites de gasto a nivel de organización y límites de tasa basados en niveles [2].

El estado beta del producto implica que los comportamientos pueden ser refinados entre lanzamientos para mejorar las salidas, lo que sugiere que algunos límites y errores aún están en proceso de optimización [2].

## MÓDULO L: Benchmarks

La documentación y los artículos técnicos revisados sobre Claude Managed Agents y Claude Cowork no proporcionan resultados de benchmarks específicos como SWE-bench, WebArena, OSWorld u otros estándares de la industria [1, 2, 3]. La información disponible se centra más en la arquitectura, los principios de diseño y las mejoras internas de rendimiento.

Sin embargo, se menciona una métrica de rendimiento interna significativa relacionada con la eficiencia del sistema:

*   **Time-To-First-Token (TTFT)**: El desacoplamiento del "cerebro" (harness) de las "manos" (sandboxes/herramientas) ha resultado en una mejora sustancial del TTFT. El p50 (percentil 50) del TTFT se redujo aproximadamente un 60%, y el p95 (percentil 95) se redujo en más del 90% [1]. El TTFT mide el tiempo que una sesión espera entre aceptar el trabajo y producir su primer token de respuesta, siendo una métrica clave para la latencia percibida por el usuario [1].

Aunque la ausencia de benchmarks externos estandarizados dificulta una comparación directa con otros agentes, la mejora en el TTFT es un indicador importante de la eficiencia operativa y la capacidad de respuesta de Claude Managed Agents. Esto sugiere que el enfoque arquitectónico de Anthropic está optimizado para la velocidad y la escalabilidad en la ejecución de tareas de agentes de larga duración.

## Lecciones para el Monstruo

La arquitectura y el desarrollo de Claude Managed Agents ofrecen varias lecciones valiosas para el diseño y la implementación de sistemas de agentes de IA avanzados:

1.  **Desacoplamiento radical de componentes**: La separación del "cerebro" (modelo y lógica del agente) de las "manos" (herramientas y entornos de ejecución) y la "sesión" (estado persistente) es fundamental. Este desacoplamiento permite que cada componente evolucione, falle y se escale de forma independiente, mejorando la robustez, la seguridad y la eficiencia del sistema. Para "El Monstruo", esto significa diseñar una arquitectura modular donde el LLM central sea agnóstico a los detalles de la ejecución y la persistencia del estado.
2.  **La sesión como contexto duradero fuera de la ventana del LLM**: Depender únicamente de la ventana de contexto del LLM para tareas de larga duración es insostenible. La implementación de un registro de sesión duradero y consultable que vive fuera de la ventana de contexto del modelo es crucial. Esto permite al agente mantener una memoria coherente y recuperable, mitigando la "ansiedad de contexto" y las decisiones irreversibles. "El Monstruo" debe tener un mecanismo de memoria externa robusto y flexible, posiblemente con interfaces para interrogar y transformar el historial de eventos.
3.  **Seguridad por diseño en la ejecución de código**: La ejecución de código generado por un LLM en un sandbox presenta riesgos inherentes. La lección clave es implementar una separación estructural que impida que el código no confiable acceda a credenciales sensibles. Esto implica el uso de bóvedas de credenciales, proxies dedicados y la garantía de que los tokens de autenticación nunca sean accesibles desde el entorno de ejecución del código. "El Monstruo" debe priorizar la seguridad del sandbox, aislando completamente la ejecución de código de la gestión de credenciales.
4.  **Estrategias para tareas de larga duración y progreso incremental**: Los agentes tienden a fallar en tareas complejas y de larga duración al intentar hacer demasiado a la vez o al terminar prematuramente. La solución de Anthropic con agentes inicializadores y de codificación, junto con la gestión de un `feature_list.json` y `claude-progress.txt`, es un modelo efectivo. "El Monstruo" debería adoptar un enfoque similar, descomponiendo tareas grandes en pasos incrementales, manteniendo un registro explícito del progreso y utilizando archivos de estado para guiar las sesiones futuras.
5.  **Pruebas de extremo a extremo con automatización de navegador**: La confianza en la finalización de tareas por parte del agente no debe basarse únicamente en la ejecución de código o pruebas unitarias. La capacidad de realizar pruebas de extremo a extremo utilizando herramientas de automatización del navegador (como Puppeteer MCP) es vital para verificar la funcionalidad como lo haría un usuario humano. "El Monstruo" debe integrar herramientas de automatización de UI/navegador en su sistema de evaluación y ejecución para validar el comportamiento del agente en entornos interactivos.

## Referencias

[1] Anthropic. (2026, 8 de abril). *Scaling Managed Agents: Decoupling the brain from the hands*. Recuperado de [https://www.anthropic.com/engineering/managed-agents](https://www.anthropic.com/engineering/managed-agents)

[2] Claude API Docs. (s.f.). *Claude Managed Agents overview*. Recuperado de [https://platform.claude.com/docs/en/managed-agents/overview](https://platform.claude.com/docs/en/managed-agents/overview)

[3] Anthropic. (2025, 26 de noviembre). *Effective harnesses for long-running agents*. Recuperado de [https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)


---

## Fase 3 — Módulos Complementarios: Claude Cowork / Managed Agents (Anthropic)

### Capacidades Multimodales

La familia de modelos Claude de Anthropic, incluyendo Claude 3 Haiku, Claude 3 Sonnet, Claude 3 Opus, y la versión más reciente Claude Opus 4.7, posee capacidades multimodales centradas principalmente en la comprensión de imágenes y texto. Estos modelos están diseñados para analizar y entender imágenes en conjunto con instrucciones textuales, permitiendo una interacción rica y contextualizada. Es importante destacar que, según la documentación oficial y la información disponible, los modelos Claude **no soportan de forma nativa la entrada de video o audio**; su funcionalidad multimodal se limita a la interpretación de imágenes estáticas y texto.

**Modelos de Imagen y sus Capacidades:**

Los modelos Claude 3 (Haiku, Sonnet, Opus) y Claude Opus 4.7 integran capacidades de visión que les permiten procesar y razonar sobre el contenido visual. Claude Opus 4.7, en particular, representa un avance significativo en este ámbito, ofreciendo soporte para imágenes de alta resolución. Mientras que los modelos anteriores tenían una resolución nativa máxima de 1568 píxeles en el lado más largo, Claude Opus 4.7 eleva este límite a 2576 píxeles. Esta mejora es crucial para tareas que requieren un análisis visual detallado, como la comprensión de capturas de pantalla, el análisis de documentos complejos o el uso en aplicaciones de visión por computadora. La capacidad de procesar imágenes de mayor resolución se traduce en una mayor fidelidad y precisión en la interpretación, lo que es especialmente valioso en cargas de trabajo intensivas en visión [1].

**Límites de Archivos y Dimensiones:**

Anthropic ha establecido límites claros para la cantidad y el tamaño de las imágenes que se pueden incluir en una solicitud. En la interfaz de usuario de claude.ai, el límite es de 20 imágenes por mensaje. Para las solicitudes a través de la API, el límite es de 100 imágenes para modelos con una ventana de contexto de 200k tokens y hasta 600 imágenes para otros modelos. Sin embargo, estos límites pueden verse afectados por las restricciones de tamaño total de la solicitud. El tamaño máximo de las dimensiones por imagen es de 8000x8000 píxeles. Si se envían más de 20 imágenes en una sola solicitud API, este límite se reduce a 2000x2000 píxeles para cada imagen. Además, existe un límite de tamaño de solicitud de 32 MB para los "endpoints" estándar de la API. Para manejar un gran número de imágenes o imágenes de gran tamaño, se recomienda utilizar la API de Archivos (`Files API`) de Anthropic, que permite subir imágenes una vez y referenciarlas por su `file_id` en solicitudes posteriores, reduciendo así el tamaño de la carga útil de la solicitud [1].

**Formatos Soportados:**

Los modelos Claude soportan los formatos de imagen más comunes: JPEG, PNG, GIF y WebP. Es importante tener en cuenta que las animaciones no son compatibles; en caso de subir un archivo animado, solo se procesará el primer fotograma. Para obtener los mejores resultados, Anthropic recomienda asegurar que las imágenes sean claras, no estén borrosas ni pixeladas. Si la imagen contiene texto importante, debe ser legible y no demasiado pequeño. También se aconseja considerar el redimensionamiento previo de las imágenes para optimizar el rendimiento y controlar los costos de tokens, ya que las imágenes muy grandes pueden ser redimensionadas automáticamente por el modelo, lo que podría afectar la legibilidad del texto o la precisión del análisis [1].

**Cálculo de Costos y Tokenización de Imágenes:**

Cada imagen incluida en una solicitud a Claude contribuye al uso de tokens y, por ende, al costo. El número aproximado de tokens que consume una imagen se calcula mediante la fórmula `ancho * alto / 750`, donde el ancho y el alto se expresan en píxeles. Por ejemplo, una imagen de 1000x1000 píxeles consume aproximadamente 1334 tokens. Claude Opus 4.7, al soportar imágenes de mayor resolución, puede consumir hasta aproximadamente 4784 tokens por imagen, lo que es casi tres veces más que los modelos anteriores. Es fundamental que los desarrolladores consideren estos costos y, si la fidelidad adicional no es necesaria, opten por reducir el tamaño de las imágenes antes de enviarlas para gestionar eficientemente el consumo de tokens [1].

**Limitaciones Conocidas:**

A pesar de sus avanzadas capacidades de visión, Claude presenta algunas limitaciones. No puede ser utilizado para identificar personas en imágenes y se negará a hacerlo. Puede "alucinar" o cometer errores al interpretar imágenes de baja calidad, rotadas o muy pequeñas (menos de 200 píxeles). Sus habilidades de razonamiento espacial son limitadas, lo que significa que puede tener dificultades con tareas que requieren localización precisa o comprensión de diseños complejos. Claude puede dar recuentos aproximados de objetos, pero no siempre es preciso, especialmente con un gran número de objetos pequeños. Además, Claude no puede determinar si una imagen ha sido generada por IA y no debe utilizarse para detectar imágenes falsas o sintéticas. Finalmente, no procesa contenido inapropiado o explícito y, aunque puede analizar imágenes médicas generales, no está diseñado para interpretar escaneos de diagnóstico complejos como tomografías o resonancias magnéticas, y sus resultados no deben considerarse un sustituto del consejo médico profesional [1].

**Ausencia de Soporte para Video y Audio:**

Es crucial reiterar que, a la fecha de esta investigación, la documentación oficial de Anthropic y las fuentes técnicas consultadas indican que los modelos Claude no ofrecen soporte nativo para la entrada de video o audio. La multimodalidad de Claude se enfoca exclusivamente en la combinación de texto e imágenes. Cualquier mención de capacidades de video o audio en fuentes no oficiales debe ser tratada con escepticismo, ya que no hay evidencia técnica que respalde dicha funcionalidad en la API o en las interfaces de usuario de Claude.

**Referencias y Fuentes:**

1.  **Título:** Vision - Claude API Docs
    **URL:** https://platform.claude.com/docs/en/build-with-claude/vision
    **Fecha:** Desconocida (última actualización de la plataforma)

2.  **Título:** Introducing the next generation of Claude - Anthropic
    **URL:** https://www.anthropic.com/news/claude-3-family
    **Fecha:** 4 de marzo de 2024

3.  **Título:** Introducing Claude Opus 4.7 - Anthropic
    **URL:** https://www.anthropic.com/news/claude-opus-4-7
    **Fecha:** 16 de abril de 2026

4.  **Título:** Claude AI File Uploading: Supported File Types, Maximum Size ... - DataStudios.org
    **URL:** https://www.datastudios.org/post/claude-ai-file-uploading-supported-file-types-maximum-size-limits-upload-rules-and-document-read
    **Fecha:** 13 de enero de 2026

5.  **Título:** What Is Claude AI? - IBM
    **URL:** https://www.ibm.com/think/topics/claude-ai
    **Fecha:** 24 de septiembre de 2024

## Fase 4 — Módulos Complementarios: Claude Cowork / Managed Agents (Anthropic)

### Ciclo del Agente y Loop (Validado con Ingeniería Inversa)

Fuente: Pluto Security reverse-engineering del runtime (27 Abr 2026)

El ciclo del agente en Claude Managed Agents tiene 3 capas completamente desacopladas:

**Capa 1 — Session (Registro de Eventos):**
- Log append-only y durable almacenado FUERA del container
- Registra cada mensaje de usuario, tool call y resultado
- Sobrevive crashes del container y reinicios del harness
- Proporciona audit trail inmutable por defecto
- Operaciones disponibles: `archive` (read-only, secretos purgados) y `delete` (hard delete)

**Capa 2 — Harness (Orquestador):**
- Loop de orquestación stateless que llama a la Claude API
- Enruta tool calls y escribe eventos al Session
- Si crashea, una nueva instancia retoma desde el último evento via `wake(sessionId)`
- No pierde estado porque el estado vive en el Session, no en el Harness

**Capa 3 — Sandbox (Ejecución):**
- Container gVisor desechable, provisionado on-demand
- Tratado como **untrusted por diseño**
- Tiene bash, file I/O, acceso web y conexiones MCP
- Un sandbox comprometido NO puede acceder al Session log ni a las credenciales del vault

**El ciclo ReAct dentro del Harness:**
```
while not done:
    response = claude_api.call(session_history)
    if response.has_tool_call:
        result = execute_tool_in_sandbox(response.tool_call)
        session.append(tool_result)
    else:
        session.append(response)
        if response.is_final:
            done = True
```

### Estados del Agente

Los estados del agente se comunican vía el Session event stream:

| Estado | Evento | Descripción |
|--------|--------|-------------|
| `running` | `session.status_running` | El agente está ejecutando activamente |
| `idle` | `session.status_idle` | El agente terminó un paso, esperando |
| `error` | `session.error` | Fallo de MCP auth u otro error |
| `waiting_input` | `session.waiting_for_input` | El agente necesita input del usuario |
| `complete` | `session.complete` | La tarea fue completada |

**Transición clave:** En la transición `status_idle → status_running`, el harness reintenta autenticaciones MCP fallidas automáticamente.

### Sandbox y Entorno de Ejecución

**Container:** gVisor (sandbox de kernel de Google, más seguro que Docker estándar)
- Filtrado de syscalls via gVisor
- MITM TLS inspection proxy para tráfico de red
- Sistema de control de egress en capas

**Aislamiento de credenciales (el mecanismo más importante):**
1. Las credenciales se almacenan en un vault via API (campos secretos son write-only — la API nunca los devuelve)
2. Al crear una sesión, se pasan `vault_ids`
3. En runtime, cuando Claude necesita autenticarse con un MCP server, un **credential proxy externo al sandbox** inyecta el token server-side
4. El sandbox NUNCA ve la credencial
5. El agente no puede enumerar qué hay en el vault

```python
# Crear vault con credencial
vault = client.beta.vaults.create(
    credentials=[{
        "type": "oauth",
        "mcp_server_url": "https://api.github.com/mcp/",
        "token": "ghp_xxxx"  # write-only, nunca se devuelve
    }]
)

# Crear sesión con vault
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    vault_ids=[vault.id]
)
```

### Integraciones y Connectors (Validados)

**MCP Servers soportados (cualquier servidor MCP con HTTP streamable transport):**
- GitHub: `https://api.githubcopilot.com/mcp/`
- Notion: `https://mcp.notion.com/mcp`
- Slack (via MCP)
- Gmail (via MCP)
- Cualquier servidor MCP personalizado

**Configuración del agente con MCP:**
```bash
AGENT_ID=$(ant beta:agents create \
  --name "GitHub Assistant" \
  --model claude-opus-4-7 \
  --mcp-server '{type: url, name: github, url: "https://api.githubcopilot.com/mcp/"}' \
  --tool '{type: agent_toolset_20260401}' \
  --tool '{type: mcp_toolset, mcp_server_name: github}')
```

**Header requerido:** `managed-agents-2026-04-01` beta header en todas las requests.

**Plataformas cloud:**
- Amazon Bedrock
- Google Cloud Vertex AI
- API directa de Anthropic

**Integración con Microsoft Hosted Agents:**
- Compatible con Azure OpenAI, GitHub Copilot
- Soporta protocolos A2A, AG-UI, MCP

### Manejo de Errores

- **MCP auth failure:** El harness emite `session.error` pero la sesión continúa. El agente puede operar sin el MCP fallido.
- **Sandbox crash:** El harness detecta el crash, provisiona un nuevo sandbox, retoma desde el último evento del Session log.
- **Harness crash:** Una nueva instancia del harness llama a `wake(sessionId)` y retoma desde el último evento.
- **Prompt injection:** Estructuralmente imposible robar credenciales del vault — nunca entran al sandbox.

### Referencias y Fuentes

1. [Inside Claude Managed Agents — Pluto Security (27 Abr 2026)](https://pluto.security/blog/inside-claude-managed-agents/)
2. [MCP connector — Claude API Docs (Abr 2026)](https://platform.claude.com/docs/en/managed-agents/mcp-connector)
3. [Authenticate with vaults — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/vaults)
4. [Scaling Managed Agents — Anthropic Engineering (8 Abr 2026)](https://www.anthropic.com/engineering/managed-agents)
5. [When Anthropic's Managed Agents Meet Microsoft Hosted Agents — Azure Dev Community (Abr 2026)](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/when-anthropic%E2%80%99s-managed-agents-meet-microsoft-hosted-agents/4514337)
