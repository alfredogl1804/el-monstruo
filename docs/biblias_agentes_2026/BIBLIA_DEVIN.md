# Biblia de Implementación: Devin 2.2 Cognition AI

**Fecha de Lanzamiento:** Febrero 24, 2026
**Versión:** 2.2
**Arquitectura Principal:** Agente Autónomo de Ingeniería de Software con Planificación Basada en DAG y Bucle ReAct (Planificar, Ejecutar, Observar, Re-planificar)

## 1. Visión General y Diferenciador Único

Devin 2.2 es un agente autónomo de ingeniería de software desarrollado por Cognition AI. Su principal diferenciador radica en su capacidad para manejar tareas de codificación de largo alcance de manera autónoma, no solo generando código sino también planificando, ejecutando, observando y re-planificando en un ciclo continuo [1] [2]. A diferencia de las herramientas de codificación de IA tradicionales que esperan instrucciones paso a paso, Devin 2.2 puede descomponer una solicitud vaga en un plan estructurado, ejecutarlo en un entorno aislado (sandbox), observar los resultados y adaptarse dinámicamente a los problemas inesperados [2]. Esta capacidad de auto-verificación y auto-corrección, junto con el acceso a un escritorio Linux completo para pruebas de aplicaciones de escritorio, lo posiciona como un "compañero de equipo de IA" capaz de gestionar el ciclo de vida completo del desarrollo de software [1].

## 2. Arquitectura Técnica

La arquitectura técnica de Devin 2.2 se centra en un modelo de agente autónomo diseñado para tareas de codificación de largo alcance. En su núcleo, utiliza un modelo de lenguaje grande (LLM) entrenado específicamente para razonamiento de múltiples pasos, uso de herramientas y mantenimiento de contexto a lo largo de una sesión completa [2].

### 2.1. Planificación Basada en Grafos Acíclicos Dirigidos (DAG)

Cuando se le asigna una tarea, Devin no genera código inmediatamente, sino que primero elabora un plan estructurado. Este plan no es una lista secuencial simple, sino un **Grafo Acíclico Dirigido (DAG)**. Un DAG representa las tareas donde algunas etapas deben completarse antes que otras (bordes dirigidos) y no existen dependencias circulares. Esta estructura permite a Devin comprender las dependencias entre las subtareas, lo que facilita el paralelismo y la toma de decisiones más inteligentes cuando surgen problemas [2].

Por ejemplo, para una tarea como "Agregar pago de Stripe a la aplicación de comercio electrónico", el plan de Devin podría incluir pasos como:

*   Inspeccionar el código base existente.
*   Verificar dependencias de librerías de pago.
*   Instalar SDK de Stripe.
*   Crear un endpoint de API para la intención de pago.
*   Integrar el componente frontend.
*   Escribir pruebas unitarias.
*   Ejecutar pruebas y verificar [2].

Este "punto de control de planificación" es visible para el usuario, permitiendo la corrección del curso antes de la ejecución [2].

### 2.2. Bucle ReAct (Reason + Act)

La ejecución de Devin se basa en un bucle continuo de **ReAct (Reason + Act)**. En cada paso, Devin decide qué herramienta usar, la ejecuta y observa el resultado. Este ciclo se repite docenas o cientos de veces en una sola sesión, manteniendo el contexto a lo largo de toda la interacción [2].

El entorno sandboxed de Devin le proporciona acceso a tres herramientas principales:

*   **Shell (terminal):** Para ejecutar comandos como `npm install`, `git checkout`, `pytest`, etc.
*   **Editor de código:** Para leer y escribir archivos.
*   **Navegador web:** Para buscar documentación, Stack Overflow, problemas de GitHub, etc. [2].

### 2.3. Re-planificación Dinámica

Una característica crucial de la arquitectura de Devin es su capacidad de **re-planificación dinámica**. Cuando encuentra un bloqueador o un resultado inesperado (por ejemplo, conflictos de dependencias, fallos en las pruebas), Devin no se detiene. En cambio, razona sobre la situación utilizando su contexto completo (la tarea, los resultados de las pruebas, las acciones previas) y ajusta su plan. Esto puede implicar investigar la causa del problema, intentar una solución, continuar con el objetivo principal si el problema no es crítico, o escalar el problema al usuario con una explicación clara [2]. La re-planificación es una señal de que el sistema está funcionando correctamente y adaptándose a la realidad del desarrollo de software [2].

### 2.4. Razonamiento a Largo Plazo y Memoria Persistente

Devin está diseñado para mantener un **razonamiento a largo plazo** y una **memoria de trabajo persistente** a lo largo de toda la sesión. Esto le permite recordar acciones previas, errores y decisiones para informar sus acciones actuales, a diferencia de las interacciones de IA basadas en chat que son en gran medida sin estado. Esta memoria persistente es fundamental para manejar tareas de ingeniería complejas que requieren cientos de decisiones a lo largo del tiempo [2].

## 3. Implementación/Patrones Clave

La implementación de Devin 2.2 se basa en varios patrones clave que le otorgan su autonomía y eficacia:

*   **Entorno Sandboxed con Acceso a Herramientas:** Devin opera en un entorno de nube aislado que le proporciona un shell, un editor de código y un navegador web. Esto le permite interactuar con el sistema como lo haría un ingeniero humano, ejecutando comandos, modificando archivos y buscando información [2].
*   **Pruebas de Extremo a Extremo con Uso de Computadora:** Devin 2.2 ha mejorado sus capacidades de prueba, pudiendo lanzar y probar aplicaciones de escritorio con acceso completo a su propio escritorio Linux. Después de crear un Pull Request (PR), Devin puede sugerir probarlo en su escritorio, ejecutando la aplicación y enviando grabaciones de pantalla para revisión. Esto permite una verificación exhaustiva de su trabajo [1].
*   **Auto-verificación y Auto-corrección (Devin Review Autofix):** Un patrón fundamental es la capacidad de Devin para revisar su propia salida, identificar problemas y corregirlos antes de que el usuario abra un PR. Este ciclo completo de planificación, codificación, revisión y corrección se maneja de forma autónoma, reduciendo la carga de trabajo del desarrollador [1].
*   **Interfaz Reconstruida y Flujo de Trabajo Unificado:** La versión 2.2 presenta una interfaz completamente reconstruida que unifica todo el ciclo de vida del desarrollo, desde la planificación hasta la revisión del código. Esto mejora la experiencia del usuario y facilita la comprensión y acción sobre el trabajo de Devin [1].
*   **Agentes en la Nube Paralelos:** Devin utiliza agentes en la nube paralelos, lo que sugiere una arquitectura distribuida donde múltiples instancias o componentes del agente pueden trabajar simultáneamente en diferentes aspectos de una tarea, mejorando la eficiencia y escalabilidad [1].

## 4. Lecciones para el Monstruo

Para nuestro propio agente, las lecciones clave de la arquitectura de Devin 2.2 son las siguientes:

*   **Adoptar la Planificación Basada en DAG:** La descomposición de tareas en un DAG es fundamental para manejar la complejidad y las dependencias. Nuestro agente podría beneficiarse enormemente de una estructura de planificación similar para optimizar la ejecución de tareas y la gestión de errores.
*   **Implementar un Bucle ReAct Robusto:** La capacidad de razonar, actuar y observar en un ciclo continuo es esencial para la autonomía. Fortalecer nuestro propio bucle ReAct, asegurando que el contexto se mantenga a lo largo de toda la sesión, mejoraría la capacidad de nuestro agente para manejar tareas de largo alcance.
*   **Desarrollar Capacidades de Re-planificación Dinámica:** La habilidad de Devin para adaptarse a lo inesperado es un diferenciador clave. Nuestro agente debería ser capaz de re-planificar dinámicamente cuando encuentre obstáculos, en lugar de fallar o requerir intervención humana constante. Esto implica una lógica sofisticada para evaluar la situación y ajustar el plan.
*   **Integrar Herramientas de Entorno Sandboxed:** Proporcionar a nuestro agente acceso a un shell, editor de código y navegador web en un entorno controlado le permitiría interactuar con el sistema de manera más flexible y autónoma, similar a un humano.
*   **Enfocarse en la Auto-verificación y Auto-corrección:** La capacidad de Devin para revisar y corregir su propio trabajo antes de la intervención humana es un objetivo valioso. Nuestro agente debería aspirar a un nivel similar de auto-inspección y depuración para reducir la necesidad de supervisión.
*   **Mantener Contexto a Largo Plazo:** La memoria persistente de Devin para el razonamiento a largo plazo es crucial. Nuestro agente debe ser capaz de recordar y referenciar decisiones y observaciones pasadas para informar sus acciones futuras en tareas complejas.

---
*Referencias:*
[1] [Introducing Devin 2.2 - Cognition AI Blog](https://cognition.ai/blog/introducing-devin-2-2)
[2] [How Devin AI Actually Thinks: Autonomous Planning, DAG Execution, and Dynamic Re-Planning Explained - Medium](https://medium.com/@nitinmatani22/how-devin-ai-actually-thinks-autonomous-planning-dag-execution-and-dynamic-re-planning-explained-997be175a475)


---

# Biblia de Implementación: Devin 2.2 (Cognition AI) — Fase 2

## MÓDULO A: Ciclo del agente (loop/ReAct)

Devin 2.2, desarrollado por Cognition AI, opera bajo un sofisticado ciclo de agente que va más allá de la simple generación de código. Su núcleo reside en un bucle continuo de **planificación, ejecución, observación y re-planificación** [1]. Este enfoque le permite abordar tareas de ingeniería de software complejas de manera autónoma, adaptándose a los desafíos inesperados que surgen durante el proceso [1].

### 1. Planificación Estructurada

Al recibir una tarea, incluso si es vaga, Devin no procede directamente a escribir código. En su lugar, dedica un tiempo a **pensar** y descomponer la solicitud en un plan estructurado y multi-pasos [1]. Este plan inicial es visible para el usuario y se presenta como una serie de pasos, pero internamente se representa como un **Grafo Acíclico Dirigido (DAG)** [1].

La estructura DAG es crucial porque permite a Devin:
*   **Paralelismo y Conciencia de Dependencias**: Identifica qué pasos deben completarse antes que otros y cuáles pueden ejecutarse simultáneamente [1].
*   **Identificación de Bloqueadores**: Reconoce pasos críticos que, si fallan, ponen en riesgo todo el flujo de trabajo posterior [1].

Este plan inicial sirve como un **punto de control de planificación**, donde el usuario puede revisar y corregir la comprensión de Devin sobre la tarea antes de que comience la ejecución, lo que ahorra tiempo y recursos computacionales [1].

### 2. Ejecución y Observación (Bucle ReAct)

Una vez aprobado el plan, Devin comienza la ejecución. En cada paso, toma una decisión sobre qué herramienta utilizar, ejecuta la acción y luego **observa** el resultado [1]. Este proceso es el **bucle ReAct (Reason + Act)**, fundamental en los agentes de IA modernos [1].

El ciclo conceptual de ejecución de un paso se puede describir de la siguiente manera [1]:

```python
def execute_step(step, context):
    # 1. Razonar sobre qué hacer
    action = think(step, context)
    # e.g. "Necesito verificar si Stripe ya está instalado"

    # 2. Elegir y usar la herramienta correcta
    result = run_tool(action)
    # e.g. shell: "cat package.json | grep stripe"

    # 3. Observar el resultado
    observation = parse_result(result)
    # e.g. "No se encontró la dependencia de Stripe"

    # 4. Actualizar el contexto y decidir la siguiente acción
    return update_context(context, observation)
    # e.g. "Necesito instalar stripe antes de continuar"
```

Este bucle se repite cientos de veces en una sesión, y cada acción se basa en todo lo observado previamente, manteniendo un contexto continuo a lo largo de toda la sesión [1].

### 3. Re-planificación Dinámica

Una de las características más distintivas de Devin es su capacidad para **re-planificar dinámicamente** cuando encuentra un bloqueador o un resultado inesperado [1]. A diferencia de la automatización tradicional que falla ante lo imprevisto, Devin razona sobre la situación utilizando su contexto completo (la tarea, los fallos de las pruebas, lo que ha hecho hasta ahora) y elige el camino más apropiado [1].

Por ejemplo, si durante la ejecución de pruebas se encuentran fallos, Devin puede [1]:
*   **Investigar**: Determinar si los fallos son preexistentes o están relacionados con la tarea actual.
*   **Corregir**: Si los fallos están en código adyacente a lo que está modificando, puede intentar corregirlos.
*   **Registrar y Continuar**: Si los fallos no están relacionados, los registra y continúa con su objetivo principal.
*   **Escalar**: Si los fallos bloquean genuinamente la tarea, informa al usuario con una explicación clara.

Esta capacidad de re-planificación no es un estado de fallo, sino una parte integral del sistema que le permite adaptarse a la realidad cambiante del desarrollo de software [1].

### Referencias
[1] Nitinmatani. (2026, April 9). *How Devin AI Actually Thinks: Autonomous Planning, DAG Execution, and Dynamic Re-Planning Explained*. Medium. https://medium.com/@nitinmatani22/how-devin-ai-actually-thinks-autonomous-planning-dag-execution-and-dynamic-re-planning-explained-997be175a475

## MÓDULO B: Estados del agente

Aunque la documentación de Devin no define explícitamente un conjunto formal de "estados" del agente en el sentido de una máquina de estados finitos, su funcionamiento implica transiciones lógicas entre diferentes fases operativas, impulsadas por su ciclo de planificación, ejecución, observación y re-planificación [1]. Estos "estados" se manifiestan a través de las etapas de su proceso de resolución de tareas y su capacidad para adaptarse a los resultados.

Los principales estados o fases operativas que Devin puede exhibir incluyen:

*   **Estado de Planificación Inicial**: Devin recibe una tarea y la descompone en un plan estructurado (DAG). Durante esta fase, el agente analiza la solicitud, inspecciona el código base relevante y define los pasos a seguir. El usuario puede interactuar en este punto para refinar el plan [1].

*   **Estado de Ejecución Activa**: Una vez que el plan es aprobado, Devin entra en un estado de ejecución donde interactúa con su entorno (terminal, editor de código, navegador) para llevar a cabo los pasos definidos en el plan. Este es el estado donde el bucle ReAct está en pleno funcionamiento, con Devin razonando, actuando y observando continuamente [1].

*   **Estado de Observación y Evaluación**: Después de cada acción, Devin entra en un estado de observación para evaluar el resultado. Esto implica analizar la salida de los comandos de la terminal, los cambios en los archivos o la información obtenida del navegador. La información recopilada se utiliza para actualizar el contexto interno del agente [1].

*   **Estado de Re-planificación/Adaptación**: Si la observación revela un resultado inesperado, un error o un bloqueo, Devin transiciona a un estado de re-planificación. En este estado, el agente razona sobre la nueva situación y modifica su plan de acción para superar el obstáculo. Esto puede implicar investigar el problema, intentar una solución alternativa, registrar el problema para futuras referencias o escalar la situación al usuario [1].

*   **Estado de Espera/Interacción con el Usuario**: Devin puede entrar en un estado de espera si necesita la aprobación del usuario para un plan modificado, si encuentra un problema que requiere juicio humano, o si se le ha instruido para hacer una pausa en ciertos hitos (puntos de control) [1].

*   **Estado de Finalización**: Una vez que todos los objetivos de la tarea se han cumplido y verificado, Devin entra en un estado de finalización, donde la sesión puede cerrarse o los resultados pueden presentarse al usuario.

Las transiciones entre estos estados son fluidas y dinámicas, impulsadas por el bucle ReAct y la capacidad de Devin para el razonamiento a largo plazo y la re-planificación. La persistencia del contexto a lo largo de la sesión permite a Devin recordar acciones pasadas, errores y decisiones, lo que influye en sus transiciones de estado y en su capacidad para aprender y mejorar [1].

## MÓDULO C: Sistema de herramientas

Devin opera con un conjunto de herramientas fundamentales que le permiten interactuar con su entorno de desarrollo de software de manera autónoma. Estas herramientas son análogas a las que usaría un ingeniero de software humano y son esenciales para la ejecución de sus planes [1].

Las herramientas principales a las que Devin tiene acceso en su entorno de sandbox en la nube son [1]:

1.  **Shell (Terminal)**: Permite a Devin ejecutar comandos de línea de comandos, como `npm install`, `git checkout`, `pytest`, `ls`, `cd`, etc. Esta herramienta es crucial para la gestión de dependencias, el control de versiones, la ejecución de pruebas y la interacción general con el sistema operativo subyacente [1].

2.  **Editor de Código**: Devin puede leer y escribir archivos de código. Esto le permite inspeccionar el código base existente, realizar modificaciones, refactorizar, implementar nuevas características y corregir errores. Aunque no se especifica un editor de código particular (como VS Code o Vim), la funcionalidad es equivalente a la de un IDE completo [1].

3.  **Navegador Web**: Esta herramienta le permite a Devin buscar información en la web, como documentación, Stack Overflow, problemas de GitHub o blogs técnicos. Es vital para la investigación, la comprensión de APIs externas y la resolución de problemas que requieren conocimiento externo [1].

Además de estas herramientas básicas, Devin extiende sus capacidades a través de:

*   **Devin Session Tools**: Estas son herramientas específicas de la sesión que permiten a Devin realizar acciones como el uso de la computadora (Computer Use), grabación de pruebas y videos (Testing & Video Recordings), y el uso de comandos slash (Slash Commands) [2].

*   **Ask Devin**: Una funcionalidad que actúa como una ventana del asistente de IA al código base del usuario. Una vez que se agrega un repositorio, se indexa automáticamente para que Devin pueda entenderlo y responder preguntas sobre él [3].

*   **Data Analyst Agent (DANA)**: Una versión especializada de Devin optimizada para consultar bases de datos, analizar datos y crear visualizaciones [2].

*   **DeepWiki**: Un sistema de gestión de conocimiento que permite a Devin acceder y crear documentación, diagramas de sistemas y conocimiento organizacional [2].

*   **MCP (Model Context Protocol) Marketplace**: Devin puede integrarse con servicios externos a través de MCP, lo que le permite acceder a herramientas y datos de plataformas como Figma, bases de datos, herramientas de monitoreo y más [2, 4].

*   **Playbooks**: Devin puede crear y utilizar playbooks reutilizables que son esencialmente plantillas de prompts compartibles para delegar tareas de manera eficiente. Estos playbooks encapsulan procedimientos, especificaciones y consejos para tareas repetitivas o complejas [2, 4].

*   **Knowledge**: Para el contexto persistente que Devin debe recordar en todas las sesiones (estándares de codificación, errores comunes, flujos de trabajo de implementación), utiliza Knowledge. Los elementos de conocimiento se recuperan automáticamente cuando son relevantes [2, 4].

**Parámetros y Límites**: La documentación enfatiza la importancia de instrucciones claras y específicas para Devin. Aunque no se detallan límites de parámetros explícitos para cada herramienta individual, la efectividad de Devin está directamente relacionada con la claridad y el contexto proporcionados en las instrucciones [4]. La capacidad de Devin para re-planificar dinámicamente y su razonamiento a largo plazo mitigan algunos de los límites que tendrían otros agentes con ventanas de contexto fijas [1]. La gestión de ACUs (Agent Compute Units) también impone un límite práctico en la complejidad y duración de las tareas [1].

## MÓDULO D: Ejecución de código

La ejecución de código en Devin es una parte integral de su ciclo de trabajo, permitiéndole no solo escribir código sino también probarlo y depurarlo de manera autónoma. Devin ejecuta código dentro de su entorno de sandbox, que es una máquina virtual Linux [1, 5].

### Lenguajes de Programación

Devin es un ingeniero de software autónomo, lo que implica que puede trabajar con una amplia gama de lenguajes de programación. Aunque la documentación no lista explícitamente todos los lenguajes soportados, su capacidad para instalar dependencias (`npm install`, `pip install`, etc.) y ejecutar comandos de shell sugiere compatibilidad con cualquier lenguaje que pueda ejecutarse en un entorno Linux, incluyendo, pero no limitado a:

*   **JavaScript/TypeScript** (con Node.js y npm/yarn) [1]
*   **Python** (con pip y entornos virtuales) [1]
*   **Java** (con Maven/Gradle)
*   **Go**
*   **Ruby**
*   **Rust**
*   **C/C++**

Su capacidad para refactorizar y migrar código en proyectos de gran escala (como el caso de Nubank, que involucró millones de líneas de código) [6] y su mención de acelerar modernizaciones en COBOL, .NET y Talend [2] demuestran su versatilidad en diferentes stacks tecnológicos.

### Entorno de Ejecución

Devin ejecuta el código en un **entorno de cómputo en la nube aislado y sandboxed** [1, 5]. Este entorno es una máquina virtual basada en Linux que replica el espacio de trabajo de un desarrollador humano, incluyendo [5]:

*   **Sistema Operativo**: Linux.
*   **Terminal**: Acceso completo a la línea de comandos para ejecutar scripts, compilar, instalar paquetes, etc. [1].
*   **Editor de Código**: Para modificar y guardar archivos [1].
*   **Repositorios Clonados**: Los repositorios del usuario se clonan en este entorno [5].
*   **Herramientas Instaladas**: Las herramientas necesarias para el desarrollo (compiladores, intérpretes, linters, etc.) se instalan según la configuración del entorno [5].
*   **Dependencias Resueltas**: Las dependencias del proyecto se instalan y gestionan dentro de este entorno [5].

Cada sesión de Devin arranca desde un **snapshot** (instantánea) del entorno, que es una imagen congelada y booteable. Esto asegura que cada sesión comience desde un estado limpio y conocido, y que los cambios realizados durante una sesión no persistan en el snapshot base [5].

### Manejo de Errores

El manejo de errores es una característica clave de la capacidad de re-planificación dinámica de Devin [1]. Cuando Devin ejecuta código o pruebas y encuentra errores, no se detiene. En su lugar, utiliza su bucle ReAct para observar el error, razonar sobre su causa y adaptar su plan para resolverlo [1].

Las estrategias de manejo de errores incluyen [1]:

*   **Investigación**: Analizar los mensajes de error, logs y el contexto del código para entender la raíz del problema.
*   **Depuración**: Utilizar el terminal y el editor de código para inspeccionar el estado del programa, realizar cambios y volver a ejecutar.
*   **Re-planificación**: Modificar el plan de acción para incluir pasos de corrección de errores, como ajustar dependencias, refactorizar código o buscar soluciones en línea.
*   **Autofix**: Devin puede auto-corregir comentarios de revisión y fallos de CI, creando un bucle cerrado donde los PRs iteran hacia la calidad sin intervención humana constante [4].
*   **Escalamiento**: Si un error es demasiado complejo o bloquea genuinamente la tarea, Devin puede escalarlo al usuario con una explicación clara [1].

La capacidad de Devin para aprender de sesiones pasadas y mantener un contexto a largo plazo también contribuye a un manejo de errores más robusto, permitiéndole evitar "agujeros de conejo" y encontrar soluciones más rápidas a errores y casos límite previamente vistos [6].

## MÓDULO E: Sandbox y entorno

El entorno de sandbox de Devin es un componente fundamental de su arquitectura, proporcionando el espacio de trabajo aislado y seguro donde el agente opera. Este entorno está diseñado para replicar fielmente el espacio de trabajo de un desarrollador humano, pero con capas adicionales de seguridad y gestión [1, 5].

### Dónde se Ejecuta

Devin se ejecuta en un **entorno de cómputo en la nube aislado** [1]. Específicamente, cada sesión de Devin se ejecuta dentro de su propia **máquina virtual (VM) basada en Linux** [5]. Esto significa que cada instancia de Devin tiene su propio sistema operativo, recursos y herramientas, completamente separado de otras sesiones o del sistema anfitrión.

### Aislamiento

El aislamiento es una característica clave del sandbox de Devin. Cada VM proporciona un entorno completamente aislado para cada sesión, lo que garantiza que [5]:

*   **Separación de Sesiones**: Los cambios realizados en una sesión no afectan a otras sesiones de Devin. Cada sesión comienza desde un "snapshot" limpio y preconfigurado.
*   **Protección del Sistema Anfitrión**: Las operaciones realizadas por Devin dentro de la VM no pueden afectar directamente el sistema subyacente de la infraestructura de Cognition AI.
*   **Control de Recursos**: Los recursos (CPU, RAM, almacenamiento) asignados a cada VM pueden ser gestionados y limitados, lo que contribuye a la estabilidad y eficiencia del sistema.

Cuando Devin orquesta múltiples "Devins gestionados" para tareas paralelas, cada uno de estos sub-agentes también se ejecuta en su propia VM aislada, lo que refuerza el aislamiento y permite la ejecución concurrente sin interferencias [2].

### Seguridad

La seguridad es una prioridad para Cognition AI, dado que Devin opera con código y repositorios de los usuarios. Las medidas de seguridad implementadas incluyen [7, 8]:

*   **Transmisión y Cifrado de Datos**: Toda la transmisión de datos está cifrada tanto en tránsito como en reposo. Los sistemas de producción son monitoreados continuamente a través de registros y auditorías [7].
*   **Gestión de Secretos**: Devin utiliza un "Secrets Manager" para almacenar y compartir de forma segura credenciales (claves API, contraseñas, cookies) que Devin pueda necesitar para interactuar con servicios externos [8]. Esto evita que los secretos se expongan directamente en el código o en los prompts.
*   **Prácticas Generales de Seguridad**: Cognition AI implementa prácticas de seguridad estándar de la industria, incluyendo la formación de empleados, auditorías de seguridad y controles de acceso [7].
*   **Control de Acceso Basado en Roles (RBAC)**: La API de Devin permite el uso de usuarios de servicio con RBAC para integrar Devin en aplicaciones y automatizar flujos de trabajo, asegurando que Devin solo tenga los permisos necesarios [9].
*   **Permisos Granulares**: Las capacidades avanzadas de Devin requieren permisos específicos (`UseDevinExpert`), que pueden ser gestionados por los administradores de la organización para restringir el acceso si es necesario [2].

Sin embargo, es importante destacar que la seguridad también depende de la configuración adecuada por parte del usuario. Se han señalado posibles vulnerabilidades si no se configuran correctamente los controles de acceso a la base de datos o si se exponen claves API [10, 11]. La preocupación por la exfiltración de datos a través de agentes con acceso a shell/navegador/editor también ha sido un tema de discusión [12, 13].

### Recursos

El entorno de Devin está equipado con todos los recursos que un desarrollador humano necesitaría, incluyendo [1, 5]:

*   **Herramientas de Desarrollo**: Shell, editor de código, navegador web [1].
*   **Dependencias**: Capacidad para instalar y gestionar dependencias de proyectos (ej. `npm`, `pip`) [5].
*   **Configuración Personalizada**: Los usuarios pueden configurar el entorno de Devin para que incluya herramientas, runtimes, credenciales y conocimiento específico del proyecto. Esta configuración se guarda como un snapshot para asegurar un estado inicial consistente en cada sesión [5].
*   **Unidades de Cómputo del Agente (ACUs)**: Devin mide y factura el consumo de cómputo a través de ACUs. Esto implica que los recursos computacionales utilizados por Devin (CPU, RAM, tiempo de ejecución) están cuantificados y pueden ser monitoreados y limitados por los administradores [2, 1].

La configuración del entorno es el factor más importante para mejorar la efectividad de Devin, ya que le proporciona las herramientas y el contexto necesarios para ser productivo desde el primer momento [5].

## MÓDULO F: Memoria y contexto

La gestión de la memoria y el contexto es una de las fortalezas clave de Devin, lo que le permite mantener el hilo de tareas complejas y de larga duración, a diferencia de los modelos de lenguaje tradicionales que a menudo tienen ventanas de contexto limitadas o son esencialmente sin estado [1]. Devin está diseñado para razonar sobre horizontes de tiempo largos y recordar lo que ha intentado, lo que funcionó, lo que falló y por qué [1].

### Cómo Persiste el Estado

Devin mantiene una **memoria de trabajo persistente** a lo largo de toda la sesión [1]. Esto significa que el estado de la sesión, incluyendo el historial de la shell, los cambios de código, los resultados de las pruebas y el historial de navegación, se conserva y se puede consultar en cualquier momento [14]. Esta persistencia es fundamental para su capacidad de re-planificación dinámica y para evitar repetir errores o soluciones ya probadas [1].

El entorno de Devin se inicia desde un **snapshot** (instantánea) preconfigurado, que contiene los repositorios, herramientas y dependencias. Sin embargo, los cambios realizados durante una sesión no persisten de vuelta al snapshot, asegurando que cada nueva sesión comience desde un estado limpio y conocido [5]. La persistencia del estado se gestiona a nivel de la sesión activa, permitiendo a Devin construir sobre su trabajo anterior dentro de esa sesión.

### Qué Recuerda

Devin recuerda una amplia gama de información para informar sus decisiones y acciones [1]:

*   **Historial de Acciones**: Cada acción ejecutada (comandos de shell, ediciones de código, navegaciones web) y sus resultados.
*   **Observaciones**: Los resultados de sus interacciones con el entorno, incluyendo mensajes de error, salidas de comandos y contenido web.
*   **Decisiones y Razonamientos**: El proceso de pensamiento detrás de sus acciones y las razones por las que eligió un camino sobre otro.
*   **Contexto del Código Base**: Una vez que un repositorio se indexa, Devin tiene una comprensión del código base, lo que le permite responder preguntas y trabajar de manera más efectiva [3].
*   **Conocimiento Organizacional (Knowledge)**: Devin puede acceder a una base de conocimiento persistente que contiene estándares de codificación, errores comunes, flujos de trabajo de implementación y cómo usar herramientas internas. Este conocimiento se recupera automáticamente cuando es relevante [2, 4].
*   **Playbooks**: Recuerda y utiliza playbooks, que son procedimientos estructurados para tareas específicas, aprendidos de sesiones exitosas [2, 4].

### Ventana de Contexto

Devin se distingue de muchos otros agentes de IA por su gestión de la ventana de contexto. En lugar de una ventana de contexto fija basada en tokens que se trunca, Devin mantiene un **contexto efectivo que abarca toda la sesión** [14]. Esto se logra mediante la capacidad de Devin para resumir y referenciar pasos anteriores, lo que le permite trabajar con grandes bases de código y mantener conversaciones más largas sin perder detalles importantes [14].

Aunque los modelos de lenguaje subyacentes pueden tener sus propias limitaciones de tokens (como Claude Sonnet 4.5, que tiene cierta intuición sobre cómo gestionar su propio contexto [15]), la arquitectura de Devin está optimizada para el razonamiento multi-paso y el mantenimiento del contexto a lo largo de una sesión completa, no solo para respuestas conversacionales [1]. Esto le permite "mantener notas mentales" y "captar casos límite" al recordar patrones similares vistos anteriormente, de manera similar a un desarrollador humano experimentado [1].

### Referencias
[1] Nitinmatani. (2026, April 9). *How Devin AI Actually Thinks: Autonomous Planning, DAG Execution, and Dynamic Re-Planning Explained*. Medium. https://medium.com/@nitinmatani22/how-devin-ai-actually-thinks-autonomous-planning-dag-execution-and-dynamic-re-planning-explained-997be175a475
[2] Advanced Capabilities - Devin Docs. (n.d.). Recuperado de https://docs.devin.ai/work-with-devin/advanced-capabilities
[3] Ask Devin. (n.d.). Recuperado de https://docs.devin.ai/work-with-devin/ask-devin
[4] Instructing Devin Effectively - Devin Docs. (n.d.). Recuperado de https://docs.devin.ai/essential-guidelines/instructing-devin-effectively
[5] Environment configuration - Devin Docs. (n.d.). Recuperado de https://docs.devin.ai/onboard-devin/environment
[6] How Nubank refactors millions of lines of code to improve engineering efficiency with Devin. (n.d.). Recuperado de https://devin.ai/
[7] Security at Cognition - Devin Docs. (n.d.). Recuperado de https://docs.devin.ai/admin/security
[8] Enterprise security - Devin Docs. (n.d.). Recuperado de https://docs.devin.ai/enterprise/security-access/security/enterprise-security
[9] API Overview - Devin Docs. (n.d.). Recuperado de https://docs.devin.ai/api-reference/overview
[10] Devin AI Security Issues | Vulnerabilities - Vibe App Scanner. (n.d.). Recuperado de https://vibeappscanner.com/issues/devin
[11] The Hidden Security Risks of SWE Agents like OpenAI Codex and Devin AI. (n.d.). Recuperado de https://www.pillar.security/blog/the-hidden-security-risks-of-swe-agents-like-openai-codex-and-devin-ai
[12] How Devin AI Can Leak Your Secrets via Multiple Means. (n.d.). Recuperado de https://embracethered.com/blog/posts/2025/devin-can-leak-your-secrets/
[13] Are we over-engineering coding agents? Thoughts on the ... (n.d.). Recuperado de https://www.reddit.com/r/ChatGPTCoding/comments/1latkqz/are_we_overengineering_coding_agents_thoughts_on/
[14] Context Window Management - AI Coding Agent Feature Comparison. (n.d.). Recuperado de https://agents.4geeks.com/feature/context-window
[15] Rebuilding Devin for Claude Sonnet 4.5: Lessons and ... (n.d.). Recuperado de https://cognition.ai/blog/devin-sonnet-4-5-lessons-and-challenges

## MÓDULO G: Browser/GUI

Devin posee capacidades avanzadas para interactuar con interfaces gráficas de usuario (GUI) y navegadores web, lo que le permite probar y operar software de la misma manera que lo haría un humano. Esta funcionalidad se denomina **"Computer Use"** [16].

### Interacción con el Entorno de Escritorio Completo

Devin tiene acceso a un **entorno de escritorio Linux completo**, no solo a un navegador. Esto significa que puede [16]:

*   **Mover el ratón**: Controlar el puntero del ratón en la pantalla.
*   **Hacer clic en elementos de la UI**: Interactuar con botones, enlaces, campos de entrada, etc.
*   **Escribir en el teclado**: Introducir texto en cualquier aplicación.
*   **Tomar capturas de pantalla**: Capturar el estado visual de la pantalla.
*   **Interactuar con cualquier aplicación**: Esto incluye aplicaciones web en Chrome, aplicaciones de escritorio nativas de Linux (Electron, Java Swing/AWT, GTK/Qt), e interfaces de usuario basadas en terminal (TUI) [16].

Devin percibe la pantalla como una **pantalla de 1024x768 píxeles** y puede realizar acciones como hacer clic, escribir, desplazarse, arrastrar y tomar capturas de pantalla [16].

### Cómo Funciona "Computer Use"

Cuando Devin utiliza "Computer Use", sigue un bucle de acción-observación [16]:

1.  **Toma una captura de pantalla** de la pantalla actual para entender lo que’s visible.
2.  **Identifica elementos interactivos** (botones, campos de texto, menús, enlaces) y decide con qué interactuar.
3.  **Realiza una acción** (hace clic, escribe, se desplaza o usa atajos de teclado).
4.  **Espera y observa** (toma otra captura de pantalla para ver el resultado de la acción).
5.  **Repite** hasta que la tarea se completa.

Este bucle le permite a Devin adaptarse a contenido dinámico, estados de carga, ventanas emergentes y diálogos inesperados, tal como lo haría un humano [16].

### Casos de Uso de "Computer Use"

*   **Pruebas de aplicaciones web de extremo a extremo**: Iniciar la aplicación localmente, abrirla en Chrome, y navegar por flujos de usuario completos (inicio de sesión, navegación, envío de formularios, pago) [16].
*   **Pruebas de aplicaciones de escritorio**: Lanzar y interactuar con la GUI de cualquier aplicación Linux [16].
*   **Verificación visual**: Tomar capturas de pantalla para verificar diseños, estilos y elementos de la UI [16].
*   **Interacción con flujos de UI complejos**: Manejar escenarios que requieren interacciones multi-paso como arrastrar y soltar, menús contextuales o atajos de teclado [16].
*   **Grabación de sesiones de prueba**: Grabar su pantalla mientras realiza pruebas, anotando momentos clave en el video para revisión [16].

### Manejo de Login y Autenticación

Devin puede manejar flujos de inicio de sesión y autenticación de varias maneras [16]:

*   **Pre-configuración de acceso**: Si una aplicación requiere autenticación, se pueden configurar **secretos** (credenciales) de antemano para que Devin pueda iniciar sesión sin intervención manual durante la sesión [16].
*   **Scripts de navegador con Playwright**: Devin expone un endpoint del **Chrome DevTools Protocol (CDP)** al que Playwright puede conectarse. Devin puede escribir y ejecutar scripts de Playwright para automatizar interacciones del navegador, como flujos de inicio de sesión o entrada sistemática de datos [16].
    *   El script se conecta al navegador existente de Devin, lo que permite que los cambios de estado (cookies, localStorage, tokens de autenticación) persistan después de que el script finaliza. Esto significa que Devin puede usar la sesión autenticada inmediatamente [16].
    *   Esto es útil para flujos de SSO/OAuth complejos o para incluir scripts de inicio de sesión en la configuración del entorno para que Devin comience cada sesión ya autenticado [16].

### Referencias
[16] Computer Use - Devin Docs. (n.d.). Recuperado de https://docs.devin.ai/work-with-devin/computer-use

## MÓDULO H: Multi-agente

Devin exhibe capacidades multi-agente, pero con una filosofía y arquitectura distintivas que difieren de los enfoques tradicionales de sistemas multi-agente donde los agentes colaboran directamente a través de la comunicación. En lugar de construir sistemas donde los agentes "hablan" entre sí para resolver conflictos, Cognition AI se enfoca en un modelo donde un agente coordinador delega tareas a "Devins gestionados" que operan en entornos aislados [2, 17].

### Orquestación de "Devins Gestionados"

Devin puede descomponer tareas grandes y delegar partes de ellas a un equipo de **"Devins gestionados"** que trabajan en paralelo. Cada uno de estos sub-agentes se ejecuta en su propia **máquina virtual (VM) aislada** [2]. El agente principal actúa como coordinador, realizando las siguientes funciones [2]:

*   **Alcance del trabajo**: Define las responsabilidades de cada sub-agente.
*   **Monitoreo del progreso**: Supervisa el avance de las tareas delegadas.
*   **Resolución de conflictos**: Interviene para resolver cualquier conflicto que surja entre los resultados de los sub-agentes.
*   **Compilación de resultados**: Integra los resultados de los sub-agentes para completar la tarea general.

Esta capacidad permite a Devin abordar trabajos que abarcan múltiples archivos, módulos o repositorios, como migraciones de código, cobertura de pruebas masivas o investigación paralela [2]. Por ejemplo, Devin puede analizar un código base, agrupar archivos en paquetes de trabajo independientes y lanzar una sesión paralela para cada paquete [2].

### Filosofía de Cognition AI sobre Multi-agentes

Cognition AI ha expresado una postura crítica sobre la construcción de sistemas multi-agente donde los agentes toman decisiones de forma dispersa y la comunicación entre ellos es ineficiente o frágil [17]. Argumentan que, en 2025, la colaboración de múltiples agentes a menudo resulta en sistemas frágiles debido a la dispersión de la toma de decisiones y la dificultad de compartir el contexto de manera exhaustiva entre los agentes [17].

Los principios que guían su enfoque incluyen [17]:

*   **Compartir contexto y trazas completas del agente**: En lugar de solo mensajes individuales, es crucial compartir el contexto completo y las trazas de ejecución del agente.
*   **Las acciones conllevan decisiones implícitas**: Las decisiones en conflicto pueden llevar a malos resultados.

La empresa cree que la mejora de los agentes "single-threaded" (agentes individuales) en su capacidad para comunicarse eficazmente con humanos eventualmente desbloqueará mayores niveles de paralelismo y eficiencia, en lugar de forzar una comunicación compleja entre agentes [17]. Por lo tanto, el modelo multi-agente de Devin se centra en la **orquestación centralizada** por un agente principal, que delega y coordina, en lugar de una colaboración distribuida y autónoma entre sub-agentes.

### Sub-agentes y Herramientas

Aunque la filosofía general se inclina hacia la orquestación, Devin también utiliza el concepto de "sub-agentes" en un sentido más cercano a las llamadas a herramientas. Por ejemplo, Devin puede invocar un sub-agente DeepWiki para adquirir contexto del código base [18]. Estos sub-agentes comparten herramientas y contexto del código base con el agente padre, pero operan en su propio hilo de ejecución [19].

### Referencias
[17] Cognition. (2025, June 12). *Don’t Build Multi-Agents*. https://cognition.ai/blog/dont-build-multi-agents
[18] Yan, W. (n.d.). *Multi-Agents: What\'s Actually Working*. X (formerly Twitter). Recuperado de https://x.com/walden_yan/status/2047054401341370639
[19] Subagents - Quickstart - Devin for Terminal. (n.d.). Recuperado de https://cli.devin.ai/docs/subagents

## MÓDULO I: Integraciones

Devin está diseñado para integrarse sin problemas con las herramientas y plataformas que los equipos de ingeniería ya utilizan, facilitando la incorporación del desarrollo impulsado por IA en los flujos de trabajo existentes. Las integraciones abarcan desde el control de código fuente hasta la gestión de proyectos y la comunicación [20].

Las integraciones se pueden establecer de varias maneras [20]:

*   **Integraciones Nativas**: Conexiones directas a plataformas populares como GitHub, Slack y Jira.
*   **Secrets Manager**: Almacena de forma segura claves API y credenciales para que Devin las utilice, evitando que se expongan en el código o en los prompts.
*   **MCP (Model Context Protocol)**: Permite conectar Devin a cientos de herramientas externas y fuentes de datos.

### Integraciones Clave

Devin se integra con una variedad de servicios y plataformas, categorizados de la siguiente manera [20]:

#### 1. Control de Código Fuente

Devin se conecta con plataformas de control de código fuente para acceder a repositorios, crear solicitudes de extracción (Pull Requests) y contribuir con código. Las integraciones incluyen:

*   **GitHub** [20]
*   **GitLab** [20]
*   **Bitbucket** [20]
*   **Azure DevOps** [20]

Estas integraciones permiten a Devin clonar repositorios, realizar cambios, y gestionar el ciclo de vida del código de manera autónoma.

#### 2. Comunicación

Para facilitar la colaboración y la comunicación del equipo, Devin se integra con herramientas de chat, permitiendo iniciar sesiones y recibir actualizaciones directamente en estas plataformas:

*   **Slack**: Permite iniciar ejecuciones etiquetando a @Devin en conversaciones [20].
*   **Microsoft Teams**: Similar a Slack, permite la interacción directa con Devin a través de la plataforma [20].

#### 3. Gestión de Proyectos

Devin se conecta con herramientas de gestión de proyectos para crear sesiones a partir de tickets y rastrear el trabajo automáticamente:

*   **Jira**: Permite a Devin crear y actualizar incidencias, rastrear el trabajo e integrarse con los flujos de trabajo de gestión de proyectos [20].
*   **Linear**: Habilita a Devin para trabajar con incidencias y proyectos de Linear [20].

#### 4. MCP Marketplace

El **Model Context Protocol (MCP)** es una característica poderosa que permite a Devin conectarse a una amplia gama de herramientas externas y fuentes de datos. A través del MCP Marketplace, Devin puede integrarse con [20]:

*   **Monitoreo**: Sentry, Datadog, PagerDuty.
*   **Bases de Datos**: PostgreSQL, MySQL, MongoDB.
*   **Documentación**: Notion, Confluence.
*   **Y muchos más**: Cientos de herramientas y fuentes de datos adicionales.

El MCP permite a Devin extender sus capacidades más allá de su entorno de sandbox, interactuando con servicios específicos para realizar tareas como consultar bases de datos, actualizar documentación o responder a alertas de monitoreo [2].

#### 5. Integración API

Devin ofrece una API robusta que permite flujos de trabajo automatizados y acceso programático. Los usuarios pueden utilizar la API de Devin para crear sesiones, recuperar resultados e integrar a Devin en sus pipelines de CI/CD [20, 21]. La API utiliza un modelo de "principal + token" para la autenticación, asegurando un acceso seguro y basado en roles [22].

### Referencias
[20] Integrations Overview - Devin Docs. (n.d.). Recuperado de https://docs.devin.ai/integrations/overview
[21] API Overview - Devin Docs. (n.d.). Recuperado de https://docs.devin.ai/api-reference/overview
[22] Authentication - Devin Docs. (n.d.). Recuperado de https://docs.devin.ai/api-reference/authentication

## MÓDULO J: Multimodal

Devin AI incorpora capacidades multimodales, centrándose principalmente en la interacción visual y la comprensión de imágenes y video. Aunque no se menciona explícitamente el procesamiento de audio, sus funcionalidades visuales son robustas y esenciales para su rol como ingeniero de software autónomo [16, 23].

### Procesamiento de Imágenes y Video

Las capacidades multimodales de Devin se manifiestan a través de su función de **"Computer Use"**, que le otorga acceso a un entorno de escritorio Linux completo [16]. Dentro de este entorno, Devin puede:

*   **Tomar capturas de pantalla**: Devin puede capturar el estado visual de la pantalla en cualquier momento durante una sesión. Esto es fundamental para entender lo que es visible y para la verificación visual [16].
*   **Verificación visual**: Devin puede comparar las capturas de pantalla tomadas con el comportamiento esperado y señalar problemas visuales. Esto es crucial para las pruebas de UI/UX, asegurando que los diseños y estilos se representen correctamente [16].
*   **Reconocimiento de imágenes**: Devin incorpora visión por computadora para reconocer objetos y extraer información de las imágenes [23]. Esta capacidad es valiosa para tareas que requieren la comprensión del contenido visual en una interfaz de usuario o en documentos.
*   **Grabación de sesiones de prueba**: Devin puede grabar su pantalla mientras realiza pruebas, anotando momentos clave en el video. Estas grabaciones se procesan y se envían al usuario para su revisión, proporcionando evidencia visual de las interacciones de Devin con la aplicación [16].

### Modelos Utilizados

La documentación no especifica los modelos multimodales exactos que utiliza Devin para el procesamiento de imágenes y video. Sin embargo, dado que Devin utiliza un modelo "purpose-built" entrenado específicamente para tareas de codificación de largo plazo y optimizado para el razonamiento multi-paso y el mantenimiento del contexto [1], es plausible que integre modelos de visión por computadora adaptados a sus necesidades de comprensión de interfaces de usuario y depuración visual.

### Limitaciones y Consideraciones

Aunque Devin puede interactuar visualmente con el entorno, la efectividad de sus capacidades multimodales depende de la claridad de las instrucciones y la disponibilidad de referencias visuales. Por ejemplo, para tareas visuales, se recomienda proporcionar archivos Figma, diseños de referencia o especificaciones detalladas, ya que Devin puede construir a partir de estos pero no "inventará la estética por sí mismo" [4].

### Referencias
[23] What is Devin AI. (n.d.). Recuperado de https://www.geeksforgeeks.org/what-is-devin-ai/

## MÓDULO K: Límites y errores

Aunque Devin 2.2 es un ingeniero de software autónomo impresionante, no está exento de limitaciones y puede cometer errores. Comprender estos límites es crucial para utilizarlo de manera efectiva y establecer expectativas realistas [24].

### Limitaciones Principales

Las pruebas y revisiones de Devin han revelado varias áreas donde sus capacidades son limitadas [24]:

1.  **Requisitos Ambiguos**: Devin tiene un rendimiento deficiente cuando los requisitos son vagos o poco claros. Instrucciones como "hacer la aplicación más rápida" o "mejorar la experiencia del usuario" producirán resultados mediocre o irrelevantes. Devin necesita objetivos específicos y medibles [24].

2.  **Decisiones Arquitectónicas**: Devin no comprende las compensaciones (trade-offs) de la misma manera que lo hacen los ingenieros experimentados. Puede seguir patrones, pero no puede evaluar si un patrón es apropiado para un contexto específico. Las decisiones arquitectónicas complejas aún requieren juicio humano [24].

3.  **El Problema del "Agujero de Conejo"**: Cuando Devin encuentra un error inesperado, a veces puede caer en "agujeros de conejo", intentando soluciones cada vez más complejas que agravan el problema en lugar de reconsiderar el enfoque. Esto puede consumir mucho tiempo y producir código de peor calidad [24].

4.  **Contexto y Convenciones**: Cada código base tiene convenciones no escritas (patrones de nombres, enfoques de manejo de errores, capas arquitectónicas). Devin a menudo pasa por alto estas convenciones sutiles, produciendo código que funciona pero que no se ajusta al estilo del proyecto [24].

5.  **Depuración Compleja**: Aunque Devin puede corregir errores obvios, la depuración compleja que requiere comprender las interacciones del sistema, las condiciones de carrera o el comportamiento del sistema distribuido está más allá de sus capacidades actuales [24].

6.  **Conciencia de Seguridad**: Devin no identifica ni previene de forma fiable las vulnerabilidades de seguridad. Puede introducir inyección SQL, XSS o problemas de omisión de autenticación sin darse cuenta. Todo el código generado por Devin debe ser revisado por seguridad [24].

7.  **El Problema del "Último 30%"**: Devin con frecuencia entrega el 70% de una característica: la lógica central funciona, pero los casos extremos, el manejo de errores, el pulido de la UI y la integración con el resto del código base están incompletos. El 30% restante a menudo requiere la finalización humana [24].

8.  **Eficiencia de Costos**: A un costo de $500/mes, Devin solo es rentable si se mantiene constantemente ocupado con tareas apropiadas. Si solo hay unas pocas tareas bien definidas por semana, el costo por tarea es alto en comparación con alternativas [24].

### Cómo Falla y Cómo se Recupera

Devin está diseñado para ser resiliente y adaptarse a los fallos a través de su bucle de re-planificación dinámica [1].

*   **Detección de Errores**: Devin detecta errores a través de la observación de los resultados de la ejecución de código, pruebas, o interacciones con el entorno (terminal, navegador) [1].
*   **Re-planificación**: Ante un error o un resultado inesperado, Devin no se detiene. En su lugar, razona sobre la situación y adapta su plan de acción. Esto puede implicar investigar la causa del error, intentar una solución alternativa, o ajustar su enfoque [1].
*   **Autofix**: Devin puede auto-corregir comentarios de revisión y fallos de CI, creando un bucle cerrado donde los Pull Requests (PRs) iteran hacia la calidad sin intervención humana constante [4].
*   **Escalamiento**: Si un problema es demasiado complejo o bloquea genuinamente la tarea, Devin puede escalarlo al usuario con una explicación clara, solicitando orientación o intervención humana [1].
*   **Aprendizaje de Sesiones Pasadas**: Devin aprende de sus experiencias pasadas, incluyendo los errores y las soluciones exitosas. Esto le permite evitar "agujeros de conejo" y encontrar soluciones más rápidas a problemas recurrentes [6].

En resumen, Devin no es un reemplazo para los ingenieros de software, sino una herramienta poderosa que puede manejar una parte significativa de las tareas de ingeniería bien definidas de forma autónoma. El éxito de su uso radica en comprender sus fortalezas y debilidades, y en saber cuándo y cómo intervenir [24].

### Referencias
[24] Devin, the AI Engineer: Review, Testing & Limitations in 2026. (2026, March 3). Idlen. https://www.idlen.io/blog/devin-ai-engineer-review-limits-2026/

## MÓDULO L: Benchmarks

Devin AI ha sido evaluado en varios benchmarks para medir su capacidad como ingeniero de software autónomo. El benchmark más prominente y citado por Cognition AI es **SWE-bench**, un marco de evaluación que utiliza problemas de ingeniería de software extraídos de problemas reales de GitHub y solicitudes de extracción (pull requests) [25, 26].

### Resultados en SWE-bench

En SWE-bench, Devin ha demostrado una capacidad significativamente superior a las líneas base anteriores. Los resultados clave son los siguientes [25]:

*   **Resolución Autónoma**: Devin resuelve con éxito el **13.86%** de los problemas de SWE-bench de forma autónoma, superando con creces la línea base anterior más alta sin asistencia del **1.96%**.
*   **Resolución Asistida**: Incluso cuando se le proporcionan los archivos exactos para editar (modo "asistido"), el mejor modelo anterior solo resolvía el **4.80%** de los problemas. Devin supera esto con su capacidad autónoma.
*   **Conjunto de Pruebas**: Devin fue evaluado en un **25%** elegido aleatoriamente del conjunto de pruebas de SWE-bench (570 de 2,294 problemas). De estos, Devin resolvió con éxito 79 problemas, lo que arroja una tasa de éxito del 13.86% [25].
*   **Desarrollo Dirigido por Pruebas (TDD)**: En un entorno de desarrollo dirigido por pruebas, la tasa de éxito de Devin aumentó al **23%** en 100 pruebas muestreadas [25].

Estos resultados demuestran que Devin puede manejar tareas de ingeniería de software complejas de principio a fin, incluyendo la escritura de código, la depuración y la ejecución de pruebas [27].

### Comparación con Otros Agentes

Es importante señalar que, si bien el rendimiento de Devin en SWE-bench es notable, el panorama de los agentes de codificación está evolucionando rápidamente. Otros agentes como SWE-agent también han mostrado resultados prometedores, con un 12.29% en SWE-bench [28]. La discusión en la comunidad a menudo se centra en la metodología de evaluación y si los resultados se basan en el conjunto completo de SWE-bench o en subconjuntos [28].

### Otros Benchmarks

Aunque SWE-bench es el benchmark principal para Devin, su capacidad para interactuar con un entorno de escritorio completo ("Computer Use") sugiere que podría ser evaluado en benchmarks que requieren interacción con GUI, como **WebArena** u **OSWorld**. Sin embargo, la documentación oficial de Cognition AI se centra principalmente en SWE-bench para cuantificar sus capacidades de ingeniería de software [16].

### Referencias
[25] SWE-bench technical report - Cognition. (2024, March 15). Recuperado de https://cognition.ai/blog/swe-bench-technical-report
[26] SWE-bench Leaderboards. (n.d.). Recuperado de https://www.swebench.com/
[27] Devin AI review | The first autonomous AI coding agent?. (2025, March 13). Qubika. https://qubika.com/blog/devin-ai-coding-agent/
[28] SWE-agent: an open source coding agent that achieves 12.29% on SWE-bench. (2024, April 2). Reddit. https://www.reddit.com/r/singularity/comments/1bu9iae/sweagent_an_open_source_coding_agent_that/

## Lecciones para el Monstruo

La investigación sobre Devin 2.2 de Cognition AI ofrece varias lecciones valiosas para el desarrollo de agentes de IA, especialmente aquellos diseñados para tareas complejas como la ingeniería de software. Estas lecciones pueden guiar la construcción de futuros agentes, incluyendo el "Monstruo" (un agente hipotético de IA con capacidades avanzadas).

### 1. La Planificación Dinámica y la Re-planificación son Fundamentales

La capacidad de Devin para generar un plan estructurado (DAG) y, crucialmente, para re-planificar dinámicamente ante obstáculos o resultados inesperados [1], es una de sus mayores fortalezas. Un agente como el Monstruo, que opera en entornos complejos y cambiantes, no puede depender de planes estáticos. Debe ser capaz de:

*   **Descomponer tareas complejas**: Convertir objetivos de alto nivel en una secuencia de pasos ejecutables.
*   **Adaptarse a la incertidumbre**: Modificar su plan en tiempo real basándose en nuevas observaciones y errores.
*   **Razonar sobre fallos**: Entender por qué una acción falló y cómo corregirla, en lugar de simplemente reintentar o abortar.

Esta lección subraya la importancia de un ciclo robusto de **observación-razonamiento-acción-re-planificación** en el núcleo del Monstruo.

### 2. El Contexto Persistente es Clave para el Razonamiento a Largo Plazo

La gestión de la memoria y el contexto de Devin, que le permite recordar el historial completo de la sesión, las acciones pasadas, los errores y las decisiones [1, 14], es vital para tareas de larga duración. El Monstruo necesitará una arquitectura de memoria que vaya más allá de la ventana de contexto limitada de los LLMs. Esto implica:

*   **Almacenamiento de trazas completas**: No solo mensajes, sino el historial detallado de todas las interacciones y resultados.
*   **Recuperación de conocimiento relevante**: La capacidad de acceder y utilizar información de sesiones pasadas o bases de conocimiento externas (como DeepWiki o Knowledge en Devin) [2, 4].
*   **Síntesis de contexto**: La habilidad de resumir y priorizar la información relevante para la tarea actual, evitando la sobrecarga de contexto.

Un Monstruo con una memoria contextual rica podrá evitar errores repetidos y construir sobre el conocimiento adquirido.

### 3. La Interacción con el Entorno a Través de Herramientas Diversas es Indispensable

El amplio sistema de herramientas de Devin, que incluye terminal, editor de código, navegador web, y la capacidad de interactuar con la GUI (Computer Use) [1, 16], demuestra que un agente autónomo debe ser capaz de operar en un entorno rico y multifacético. Para el Monstruo, esto significa:

*   **Acceso a herramientas de bajo nivel**: Capacidad para ejecutar comandos de shell, manipular archivos y scripts.
*   **Interacción con interfaces gráficas**: Habilidad para "ver" y "actuar" en entornos visuales, como aplicaciones de escritorio o web, lo que es crucial para la verificación y depuración.
*   **Integración con APIs y servicios externos**: Conectividad con el mundo exterior a través de integraciones nativas y protocolos como MCP [20].

La versatilidad en el uso de herramientas es lo que permite a Devin trascender las limitaciones de un simple asistente de codificación.

### 4. La Orquestación Centralizada es Preferible a la Colaboración Distribuida para Multi-agentes Actuales

La filosofía de Cognition AI de "no construir multi-agentes" en el sentido de colaboración distribuida, sino de orquestar "Devins gestionados" desde un agente principal [17], ofrece una perspectiva importante. Para el Monstruo, si se contempla una arquitectura multi-agente, la lección es:

*   **Coordinación clara**: Un agente principal debe ser responsable de la planificación general, la delegación de tareas y la resolución de conflictos.
*   **Aislamiento de sub-agentes**: Los sub-agentes deben operar en entornos aislados para evitar interferencias y simplificar la depuración.
*   **Énfasis en la comunicación humano-agente**: Mejorar la capacidad del agente principal para comunicarse eficazmente con los humanos puede ser más productivo que intentar una comunicación compleja entre agentes.

Esto sugiere un modelo de "equipo de especialistas" bajo un "gerente de proyecto" inteligente, en lugar de un "comité de agentes" que intenta negociar entre sí.

### 5. La Claridad de las Instrucciones y la Intervención Humana Siguen Siendo Cruciales

Las limitaciones de Devin, como su dificultad con requisitos ambiguos, el problema del "último 30%" y la necesidad de revisión humana para decisiones arquitectónicas y de seguridad [24], resaltan que incluso los agentes más avanzados no son completamente autónomos. Para el Monstruo, esto implica:

*   **Diseño para la interpretabilidad**: El Monstruo debe poder explicar su razonamiento y sus planes de manera que los humanos puedan entenderlos y corregirlos.
*   **Puntos de control de intervención**: Incorporar mecanismos para que los humanos puedan revisar, guiar y corregir al agente en etapas críticas del proceso.
*   **Gestión de expectativas**: Reconocer que el Monstruo será una herramienta poderosa para aumentar la productividad, no un reemplazo completo para la inteligencia humana en todas las tareas de ingeniería de software.

Esta lección enfatiza la importancia de un diseño centrado en el humano, donde el agente y el humano colaboran de manera efectiva, aprovechando las fortalezas de cada uno.

---

## Fase 3 — Módulos Complementarios: Devin 2.2 (Cognition AI)

### Benchmarks y Métricas de Rendimiento: SWE-bench 2026

La evaluación del rendimiento de agentes de IA en tareas de ingeniería de software es crucial para comprender sus capacidades y limitaciones. SWE-bench es un benchmark automatizado diseñado para este propósito, utilizando problemas reales de GitHub para evaluar la habilidad de un sistema para resolver issues en bases de código del mundo real [1]. A diferencia de benchmarks más limitados como HumanEval, que se centran en funciones aisladas, SWE-bench evalúa la capacidad de un agente para navegar, comprender y modificar repositorios completos, validando las soluciones a través de pruebas unitarias [2].

El informe técnico inicial de Cognition AI, publicado el 15 de marzo de 2024, detalló el rendimiento de Devin en SWE-bench. En esta evaluación, Devin logró resolver con éxito el 13.86% de los issues (79 de 570), una cifra significativamente superior al 1.96% del mejor sistema no asistido previo y al 4.80% del mejor modelo asistido (Claude 2) [2]. Es importante destacar que Devin fue evaluado en un "entorno de agente", lo que significa que navegó por los archivos de forma autónoma, sin recibir una lista predefinida de archivos a editar, a diferencia de los modelos LLM "asistidos" o "no asistidos" [2].

La metodología de evaluación de Cognition AI para Devin en SWE-bench implicó la ejecución del agente de principio a fin con un prompt estandarizado, clonando el repositorio en el entorno del agente (manteniendo solo el commit base y sus ancestros para evitar fugas de información), configurando un entorno Python Conda y limitando el tiempo de ejecución a 45 minutos. Tras la ejecución, se restablecieron los archivos de prueba, se extrajo un parche de las diferencias generadas por el agente y se aplicó junto con el parche de prueba original. El éxito se determinó si todas las pruebas pasaban después de aplicar el parche de Devin [2].

El informe también destacó la capacidad de Devin para la planificación multi-pasos, con un 72% de las pruebas superadas requiriendo más de 10 minutos para completarse, lo que sugiere que la iteración es clave para su éxito. Ejemplos cualitativos mostraron cómo Devin podía corregir errores basándose en la retroalimentación de las pruebas. Un experimento adicional, donde se proporcionaron a Devin las pruebas unitarias finales junto con el problema (desarrollo guiado por pruebas), aumentó la tasa de éxito al 23% en 100 pruebas muestreadas, aunque estos resultados no son directamente comparables con las evaluaciones estándar de SWE-bench [2].

Sin embargo, al considerar los benchmarks actualizados de 2026, la situación ha evolucionado. Según BenchLM.ai, un líder en la evaluación de modelos de lenguaje, el 30 de abril de 2026, el benchmark SWE-bench Verified es liderado por Claude Mythos Preview con un 93.9%, seguido por Claude Opus 4.7 (Adaptive) con 87.6% y GPT-5.3 Codex con 85% [3]. En esta lista de 44 modelos evaluados, no se menciona explícitamente a Devin 2.2 con un score actualizado para 2026. Esto sugiere que, si bien el rendimiento inicial de Devin fue notable, los modelos más recientes han superado significativamente sus resultados reportados en 2024. Es posible que Cognition AI no haya publicado aún resultados actualizados para Devin 2.2 en los benchmarks públicos de SWE-bench 2026, o que su enfoque se haya desplazado hacia otras métricas de rendimiento o capacidades específicas no reflejadas directamente en estas tablas de clasificación [4].

### Integraciones Enterprise: Jira, GitHub y Slack

Devin 2.2 de Cognition AI está diseñado para integrarse fluidamente en los flujos de trabajo de ingeniería de software existentes, ofreciendo conexiones directas con plataformas empresariales clave como Jira, GitHub y Slack. Estas integraciones permiten que Devin actúe como un colaborador activo dentro de los equipos de desarrollo, desde la gestión de proyectos hasta el control de versiones y la comunicación [5].

**Integración con Jira:**
La integración de Devin con Jira permite automatizar la creación de sesiones de trabajo a partir de tickets y el seguimiento automático de las tareas. La configuración inicial se realiza en la cuenta de Devin, donde se conecta con Jira y se revisan los permisos. Se recomienda conectar una cuenta de servicio (mediante credenciales de cliente OAuth 2.0) para que los comentarios de Devin aparezcan bajo una identidad de bot dedicada, en lugar de una cuenta personal [6].

Devin puede ser activado desde Jira de varias maneras:
*   **Asignación directa del ticket a Devin:** Utiliza el playbook predeterminado configurado en los ajustes de integración de Jira [6].
*   **Etiquetas de playbook:** Al añadir etiquetas específicas (ej. `!plan`, `!implement`, `!triage`) a un ticket, Devin inicia una sesión utilizando el playbook correspondiente. Estas etiquetas deben crearse manualmente en Jira [6].
*   **Etiqueta "devin":** Añadir la etiqueta `devin` (o variantes como `devin-workshop`) a cualquier issue de Jira activa el playbook predeterminado [6].
*   **Mención @Devin en un comentario:** Mencionar a `@Devin` con instrucciones específicas en un comentario de Jira inicia una sesión o reenvía el mensaje a una sesión existente [6].

La configuración de la integración permite definir un "modo de sesión" (creación directa de sesión o solo alcance), etiquetas de playbook y "disparadores de automatización" basados en proyectos, etiquetas o estados de tickets. Para implementaciones empresariales, los administradores pueden mapear proyectos de Jira a organizaciones específicas de Devin, asegurando un enrutamiento adecuado de los tickets [6].

**Integración con GitHub:**
La integración de Devin con GitHub permite al agente crear pull requests, responder a comentarios de PR y colaborar directamente dentro de los repositorios, funcionando como un contribuidor más del equipo de ingeniería. La configuración implica otorgar a Devin acceso a repositorios específicos o a todos los repositorios de una organización de GitHub, revisando los permisos necesarios [7].

Devin requiere permisos de **lectura** y **escritura** para operar en los repositorios, lo que le permite enviar ramas, abrir pull requests y participar en discusiones de PR. Para los pull requests, Devin puede utilizar plantillas personalizadas (`devin_pr_template.md`) para estructurar las descripciones, lo que permite incluir contexto adicional como listas de verificación o diagramas Mermaid [7]. La integración también soporta la firma de commits con GPG, aunque requiere una configuración cuidadosa del entorno para asegurar que las claves persistan entre sesiones y que la identidad del autor del commit coincida con la clave GPG [7]. Para organizaciones con listas blancas de IP, Devin proporciona un conjunto de direcciones IP que deben ser permitidas para el acceso a GitHub [7].

**Integración con Slack:**
La integración de Devin con Slack facilita la comunicación y la colaboración en tiempo real. Los usuarios pueden interactuar con Devin mencionándolo con `@Devin` en cualquier canal de Slack para iniciar sesiones, enviar instrucciones o recibir actualizaciones. Devin responde en el hilo de conversación, permitiendo un diálogo continuo [8].

La instalación de la aplicación de Devin para Slack se realiza a través de la configuración de integraciones en la cuenta de Devin. Una vez instalada, todos los usuarios de la organización deben vincular su cuenta individual. La integración permite habilitar notificaciones de Slack para ejecuciones específicas, donde Devin envía mensajes privados con actualizaciones de estado. También se recomienda configurar un canal dedicado (ej. `#devin-runs`) para centralizar las conversaciones relacionadas con Devin [8]. La aplicación permite renombrar a Devin en el espacio de trabajo de Slack y, aunque la experiencia de la barra lateral del asistente de IA requiere un plan de Slack de pago, otras funcionalidades como las menciones y los comandos de barra (`/ask-devin`) funcionan en cualquier plan, incluyendo los gratuitos [8].

### Referencias y Fuentes

[1] SWE-bench Leaderboards. (n.d.). *SWE-bench*. Recuperado el 1 de mayo de 2026, de [https://www.swebench.com/](https://www.swebench.com/)
[2] The Cognition Team. (2024, March 15). *SWE-bench technical report*. Cognition. Recuperado el 1 de mayo de 2026, de [https://cognition.ai/blog/swe-bench-technical-report](https://cognition.ai/blog/swe-bench-technical-report)
[3] BenchLM.ai. (2026, April 30). *SWE-bench Verified Benchmark 2026: 44 LLM scores*. Recuperado el 1 de mayo de 2026, de [https://benchlm.ai/benchmarks/sweVerified](https://benchlm.ai/benchmarks/sweVerified)
[4] Capitaly.vc. (2026, April 17). *Why Cognition\'s Devin Still Matters in 2026*. Recuperado el 1 de mayo de 2026, de [https://capitaly.vc/blog/why-cognitions-devin-still-matters-2026](https://capitaly.vc/blog/why-cognitions-devin-still-matters-2026)
[5] Devin Docs. (n.d.). *Integrations Overview*. Recuperado el 1 de mayo de 2026, de [https://docs.devin.ai/integrations/overview](https://docs.devin.ai/integrations/overview)
[6] Devin Docs. (n.d.). *Jira*. Recuperado el 1 de mayo de 2026, de [https://docs.devin.ai/integrations/jira](https://docs.devin.ai/integrations/jira)
[7] Devin Docs. (n.d.). *GitHub*. Recuperado el 1 de mayo de 2026, de [https://docs.devin.ai/integrations/gh](https://docs.devin.ai/integrations/gh)
[8] Devin Docs. (n.d.). *Slack*. Recuperado el 1 de mayo de 2026, de [https://docs.devin.ai/integrations/slack](https://docs.devin.ai/integrations/slack)


## Hallazgos Técnicos en GitHub (Fase 5)

# Informe Técnico: Agente de IA Devin 2.2

## 1. Introducción

Este informe detalla una investigación técnica exhaustiva del agente de IA Devin 2.2, desarrollado por Cognition AI, con un enfoque en la información disponible públicamente en GitHub y fuentes web verificadas. El objetivo es desglosar la arquitectura, el ciclo de vida, la gestión de memoria, el uso de herramientas, el entorno de ejecución, las integraciones, los benchmarks y las decisiones de diseño del agente, proporcionando una visión técnica que complementa la documentación oficial.

## 2. Repositorio Oficial en GitHub

No se encontró un único repositorio público en GitHub específicamente etiquetado como "Devin 2.2". En cambio, Cognition AI mantiene una organización en GitHub [1] que alberga varios repositorios relacionados con Devin. Estos repositorios ofrecen información valiosa sobre diferentes aspectos del agente. La URL de la organización es: https://github.com/CognitionAI

## 3. Hallazgos Técnicos

### 3.1. Arquitectura Interna y Ciclo del Agente

La arquitectura de Devin, según se desprende de los repositorios `qa-devin` [2] y `deepwiki` [3], sugiere un diseño modular donde Devin interactúa con su entorno a través de múltiples interfaces. El repositorio `qa-devin` revela que Devin utiliza un navegador para interactuar con aplicaciones web (por ejemplo, `app.devin.ai`) y realizar pruebas de funcionalidad de extremo a extremo. También se integra con plataformas de comunicación como Slack para iniciar sesiones y enviar resultados [2].

El ciclo del agente, ilustrado por los ejemplos de pruebas en `qa-devin`, sigue un patrón iterativo:

1.  **Recepción de Prompt**: Devin recibe instrucciones iniciales (por ejemplo, a través de Slack o una interfaz de usuario).
2.  **Inicio de Sesión**: Se inicia una sesión de Devin, a menudo con un prompt específico para la tarea.
3.  **Ejecución de Acciones**: Devin utiliza su navegador para interactuar con aplicaciones, crea Pull Requests en GitHub, y ejecuta comandos de shell (como `gh pr comment` para interactuar con PRs) [2].
4.  **Estados del Agente**: Devin puede entrar en un estado de "SLEEP" (dormido) y ser "WAKE UP" (despertado) para pausar y reanudar tareas, lo que indica una gestión de estado interna para optimizar recursos o esperar feedback [2].
5.  **Feedback y Corrección**: El agente es capaz de recibir feedback, ya sea a través de mensajes en Slack o comentarios en Pull Requests de GitHub. Este feedback se utiliza para corregir errores y refinar su trabajo, demostrando una capacidad de auto-corrección y mejora iterativa [2].
6.  **Finalización**: Una vez completada la tarea, Devin puede enviar los resultados finales a la plataforma de comunicación (por ejemplo, Slack) [2].

### 3.2. Sistema de Memoria y Contexto

Aunque no se detalla explícitamente un "sistema de memoria" en los repositorios públicos, la capacidad de Devin para mantener el contexto a lo largo de una sesión y responder a feedback implica un mecanismo robusto para gestionar el estado y la información relevante. El proyecto `deepwiki` [3] es particularmente relevante aquí, ya que permite a Devin generar y utilizar documentación para cualquier repositorio público. Esto sugiere que Devin puede construir y consultar una base de conocimiento contextual para ayudar en sus tareas de ingeniería de software. La integración de un servidor MCP (Model Context Protocol) para DeepWiki [3] indica un enfoque estructurado para acceder y gestionar el contexto de información.

### 3.3. Manejo de Herramientas (Tools/Functions)

Devin demuestra una capacidad significativa para manejar diversas herramientas:

*   **Navegador Web**: Utilizado para interactuar con aplicaciones web, realizar pruebas y acceder a información [2].
*   **Slack**: Integración para comunicación, inicio de sesiones y recepción/envío de feedback [2].
*   **GitHub API**: Interacción programática con GitHub para crear Pull Requests y gestionar comentarios [2].
*   **Herramientas de DeepWiki MCP**: El servidor MCP de DeepWiki expone herramientas como `ask_question`, `read_wiki_structure` y `read_wiki_contents`, lo que permite a Devin consultar y comprender la documentación de un repositorio [3].

### 3.4. Sandbox y Entorno de Ejecución

El informe técnico de SWE-bench [4] proporciona detalles cruciales sobre el entorno de ejecución de Devin. Para las evaluaciones, Devin opera en un entorno sandboxed donde:

*   El repositorio objetivo es clonado. Solo se mantienen el commit base y sus ancestros en el historial de Git para evitar la fuga de información al agente [4].
*   El `git remote` se elimina para que `git pull` no funcione, asegurando que el agente no acceda a información externa durante la evaluación [4].
*   Los entornos Python `conda` se configuran antes de que comience la prueba [4].
*   Devin tiene un límite de tiempo de ejecución (45 minutos en el benchmark SWE-bench), aunque tiene la capacidad de ejecutarse indefinidamente [4].

Estas medidas garantizan un entorno controlado y reproducible para la evaluación, y sugieren que Devin está diseñado para operar en entornos aislados con acceso controlado a recursos.

### 3.5. Integraciones y Conectores

Las integraciones clave identificadas incluyen:

*   **Navegador Web**: Para interacción con UIs y aplicaciones web.
*   **Slack**: Para comunicación y orquestación de tareas.
*   **GitHub**: Para control de versiones, creación de PRs y colaboración.
*   **MCP Servers**: El `metabase-mcp-server` y el `deepwiki` MCP server indican la capacidad de Devin para conectarse a servicios externos y bases de datos a través de un protocolo de contexto de modelo [1, 3].

### 3.6. Benchmarks y Métricas de Rendimiento

El informe técnico de SWE-bench [4] es la fuente principal de métricas de rendimiento:

*   **SWE-bench**: Devin logró una tasa de éxito del **13.86%** al resolver 79 de 570 problemas en un subconjunto del benchmark SWE-bench. Esto es significativamente superior a los mejores sistemas asistidos anteriores (Claude 2 con 4.80%) [4].
*   **Experimento de Desarrollo Dirigido por Pruebas (Test-driven experiment)**: Cuando se le proporcionaron las pruebas unitarias finales junto con la descripción del problema, la tasa de éxito de Devin aumentó al **23%** en 100 pruebas muestreadas [4]. Esto resalta la importancia de las pruebas en el ciclo de desarrollo de software y la capacidad de Devin para utilizarlas para depurar y corregir errores.

### 3.7. Decisiones de Diseño en PRs o Issues Técnicos

Los ejemplos cualitativos del informe SWE-bench [4] revelan varias decisiones de diseño y comportamientos de Devin:

*   **Iteración y Corrección de Errores**: Devin puede corregir sus errores al ejecutar pruebas en su entorno. Esta capacidad de iterar es crucial para los desarrolladores de software y es una característica fundamental del diseño de Devin [4].
*   **Manejo de Instrucciones**: Devin sigue las instrucciones del problema muy de cerca, incluso si inicialmente son inexactas, lo que indica una posible "sobre-alineación" con las preferencias del usuario [4].
*   **Modificaciones de Código Complejas**: Devin es capaz de modificar grandes bloques de código y manejar varias líneas a la vez, a diferencia de otros LLMs que a menudo se limitan a cambios de una sola línea [4].
*   **Desafíos con Razonamiento Lógico Complejo y Edición de Múltiples Archivos**: Devin aún enfrenta desafíos con tareas que requieren un razonamiento lógico muy complejo o la edición coordinada de múltiples archivos [4].
*   **Importancia de las Pruebas**: La mejora en el rendimiento con el desarrollo dirigido por pruebas subraya una decisión de diseño que enfatiza la capacidad de Devin para aprovechar las pruebas para la depuración y la validación.

### 3.8. Información Técnica Nueva (No en la Documentación Oficial del Sitio Web)

La información más detallada sobre la metodología de evaluación de Devin en SWE-bench, incluyendo los detalles del entorno sandboxed, la eliminación del `git remote`, la configuración de `conda`, y los ejemplos cualitativos de su comportamiento (errores, correcciones, limitaciones), no se encuentra típicamente en la documentación de marketing del sitio web oficial. Los repositorios `qa-devin` y `deepwiki` también proporcionan una visión más profunda de las capacidades de integración y las herramientas internas de Devin que no se detallan en la página principal del producto.

## 4. Actividad Reciente del Repositorio

Se verificó la actividad de los repositorios `qa-devin`, `devin-swebench-results` y `deepwiki` en GitHub. Ninguno de estos repositorios mostró actividad de commits en los últimos 60 días a partir de la fecha de esta investigación (1 de mayo de 2026). Esto sugiere que, si bien estos repositorios son informativos, no están siendo activamente actualizados o desarrollados públicamente en este momento.

## 5. Conclusión

Devin 2.2 se presenta como un agente de ingeniería de software autónomo con capacidades impresionantes en la resolución de problemas de código, especialmente cuando se le proporciona un entorno de prueba robusto. Su arquitectura permite la interacción con navegadores, sistemas de comunicación y APIs de GitHub, y su ciclo de agente iterativo le permite aprender y corregir errores. Aunque no hay un único repositorio "Devin 2.2", la organización Cognition AI en GitHub y su blog técnico ofrecen una visión profunda de sus capacidades y limitaciones.

## 6. Referencias

[1] CognitionAI GitHub Organization. (n.d.). Recuperado de https://github.com/CognitionAI
[2] CognitionAI/qa-devin. (n.d.). GitHub. Recuperado de https://github.com/CognitionAI/qa-devin
[3] CognitionAI/deepwiki. (n.d.). GitHub. Recuperado de https://github.com/CognitionAI/deepwiki
[4] Cognition | SWE-bench technical report. (2024, March 15). Recuperado de https://cognition-labs.com/post/swe-bench-technical-report
---
## ACTUALIZACIÓN MAYO 2026

### Estado Actual (Mayo 2026)
- **Última versión/lanzamiento:** Devin 2.2 (Lanzado el 24 de febrero de 2026).
- **Cambios clave desde la Biblia original:**
  - Pruebas de extremo a extremo con uso de computadora: Devin ahora puede lanzar y probar aplicaciones de escritorio con acceso completo a su propio escritorio Linux, enviando grabaciones de pantalla para revisión.
  - Devin Review Autofix: Devin planifica, codifica, revisa su propio trabajo, detecta problemas y los soluciona antes de que el usuario abra un Pull Request (PR).
  - Interfaz más rápida y rediseñada: Se inicia 3 veces más rápido y presenta una interfaz completamente reconstruida que unifica el ciclo de vida del desarrollo.
  - Cambios en los precios: Se introdujeron nuevos planes de autoservicio, reduciendo el precio de entrada de $500/mes a $20/mes para el plan Pro.
- **Modelo de precios actual:**
  - Free: Uso limitado, Devin Review, DeepWiki.
  - Pro: $20/mes (Cuota de uso de Devin, cuota de Windsurf IDE, pago por uso adicional).
  - Teams: $80/mes (Miembros de equipo ilimitados, facturación centralizada).
  - Max: $200/mes (Cuotas incrementadas).
  - Enterprise: Precio personalizado (SSO, controles de administrador).

### Fortalezas Confirmadas
- Corrección de errores bien definidos (tasa de éxito del 78%).
- Escritura de pruebas (tasa de éxito del 82%).
- Migraciones de código y generación de código repetitivo (boilerplate).
- Documentación y configuración de entornos.

### Debilidades y Limitaciones Actuales
- Requisitos ambiguos (tiene dificultades con tareas vagas).
- Decisiones arquitectónicas (carece de juicio profundo).
- Problema de "agujero de conejo" (puede quedarse atascado en depuraciones complejas).
- El problema del "último 30%" (a menudo deja incompletos los casos extremos o el pulido de la interfaz de usuario).
- Conciencia de seguridad (puede introducir vulnerabilidades sin saberlo).

### Posición en el Mercado
- **Posición en el mercado:** Líder en ingeniería de software de IA autónoma, pero enfrenta una intensa competencia de alternativas más económicas como Claude Code y SWE-Agent.
- **Base de usuarios:** Adoptado por líderes de la industria (Ramp, Anduril, MongoDB, Goldman Sachs, Microsoft, Zillow).
- **Comparación:** Aunque es el líder, la competencia de Claude Code y SWE-Agent lo presiona en precio y accesibilidad.

### Puntuación Global
- **Autonomía:** 8/10
- **Puntuación Global:** 80/100
- **Despliegue:** Cloud (opera en un entorno de nube completamente aislado/sandboxed).

### Diferenciador Clave
El diferenciador clave de Devin es su verdadera ejecución autónoma de tareas de ingeniería de software de larga duración en un entorno de nube aislado (sandboxed), completo con auto-verificación y re-planificación dinámica. A diferencia de los asistentes de codificación tradicionales, Devin puede gestionar el ciclo de vida completo de una tarea, desde la planificación hasta la prueba final, adaptándose a los problemas inesperados en el camino.
