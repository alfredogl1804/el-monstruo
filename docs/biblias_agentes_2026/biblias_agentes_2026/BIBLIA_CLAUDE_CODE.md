# Biblia de Implementación: Claude Code (Anthropic)

**Fecha de Lanzamiento:** Febrero 2026 (Research Preview) / Abril 2026 (v2.1.126)
**Versión:** v2.1.126
**Arquitectura Principal:** Agente de terminal con orquestación paralela de sub-agentes y arquitectura de memoria de tres capas.

## 1. Visión General y Diferenciador Único

Claude Code es un agente de codificación autónomo basado en terminal que interactúa directamente con el sistema de archivos local. Su diferenciador técnico más importante es su **arquitectura de memoria de tres capas** (revelada en un leak de código fuente) y su capacidad para **orquestar sub-agentes en paralelo** utilizando un patrón de "Split-and-Merge" (Dividir y Fusionar).

A diferencia de los asistentes de codificación basados en IDE (como Copilot o Cursor) que dependen del contexto del editor, Claude Code opera a nivel de sistema operativo, ejecutando comandos, leyendo archivos y coordinando equipos de agentes para resolver problemas de ingeniería de software de horizonte largo.

## 2. Arquitectura Técnica: Memoria de Tres Capas

El mayor desafío para los agentes de codificación es mantener el contexto a través de sesiones largas y bases de código masivas. Claude Code resuelve esto con tres mecanismos distintos:

### 2.1. Capa 1: Memoria Persistente (`memory.md`)
Claude Code utiliza un archivo markdown simple y en texto plano (`memory.md`) en el directorio del proyecto como su almacén duradero.
-   **Qué almacena:** Decisiones arquitectónicas, convenciones del proyecto, restricciones conocidas y contexto previo.
-   **Por qué Markdown:** Es inspeccionable (los humanos pueden leerlo y corregirlo), persistente (sobrevive a reinicios), portátil y controlable por versiones (git). Esto hace que la memoria del agente sea auditable y confiable.

### 2.2. Capa 2: Búsqueda Basada en Grep (Orientación a Corto Plazo)
Para navegar por la base de código en tiempo real sin saturar la ventana de contexto, Claude Code utiliza herramientas de búsqueda basadas en `grep` (y utilidades similares como `ripgrep` o `ast-grep`).
-   **Funcionamiento:** En lugar de leer archivos completos a ciegas, el agente formula consultas de búsqueda para encontrar definiciones de funciones, usos de clases o patrones específicos, recuperando solo los fragmentos relevantes.

### 2.3. Capa 3: El Daemon Chyros (Proactividad en Segundo Plano)
Aunque no se lanzó en las primeras versiones, el código fuente reveló referencias a un proceso en segundo plano llamado "Chyros".
-   **Propósito:** Indexar la base de código, monitorear cambios en los archivos y pre-computar el contexto de forma asíncrona, permitiendo que el agente tenga respuestas casi instantáneas sobre el estado del proyecto sin tener que buscar activamente en cada turno.

## 3. Orquestación de Sub-Agentes: Patrón Split-and-Merge

Claude Code soporta un modelo de orquestador donde un agente padre genera sub-agentes y los ejecuta en paralelo (hasta 10 sub-agentes simultáneos por orquestador).

1.  **Split (Dividir):** El orquestador analiza una tarea compleja (ej. refactorizar 5 archivos) y crea un sub-agente independiente para cada subtarea. Cada sub-agente recibe su propio prompt de sistema, herramientas y un contexto aislado.
2.  **Ejecución Paralela:** Los sub-agentes operan simultáneamente. Si un sub-agente encuentra un error (ej. una prueba falla), intenta corregirlo de forma autónoma dentro de su propio bucle de retroalimentación (Feedback Loop) ejecutando código en un sandbox.
3.  **Merge (Fusionar):** Una vez que todos los sub-agentes terminan, el orquestador recopila los resultados, resuelve cualquier conflicto (ej. cambios superpuestos en el mismo archivo) y presenta el resultado final.

## 4. Lecciones para el Monstruo

La arquitectura de Claude Code proporciona directrices claras para mejorar las capacidades de codificación del Monstruo:

1.  **Implementar `memory.md`:** El Monstruo debe adoptar inmediatamente el patrón de escribir un archivo `memory.md` (o `AGENTS.md`) en la raíz de cualquier proyecto en el que trabaje. Debe leer este archivo al inicio de cada sesión y actualizarlo con decisiones clave. La transparencia de un archivo de texto es superior a las bases de datos vectoriales opacas para la colaboración humano-agente.
2.  **Búsqueda Activa sobre Lectura Pasiva:** En lugar de intentar leer archivos enteros o depender de que el usuario proporcione el contexto, el Monstruo debe usar herramientas de búsqueda en el sistema de archivos (`grep`, `find`) de manera proactiva para localizar el código relevante antes de intentar modificarlo.
3.  **Orquestación Paralela Real:** Para tareas que involucran múltiples archivos independientes, el Monstruo debe evolucionar su herramienta `WideResearchTool` (o crear una `ParallelCodingTool`) para lanzar sub-agentes que modifiquen archivos simultáneamente, reduciendo drásticamente el tiempo total de ejecución.

---
*Referencias:*
[1] MindStudio Blog: What Is the Anthropic Claude Code Source Code Leak? Three-Layer Memory Architecture Explained (Abril 2026)
[2] MindStudio Blog: Claude Code Split-and-Merge Pattern: How Sub-Agents Run in Parallel (Abril 2026)


---

# Biblia de Implementación: Claude Code (Anthropic) — Fase 2

## Introducción

Claude Code de Anthropic es un asistente de codificación impulsado por IA diseñado para ayudar a los desarrolladores a construir características, corregir errores y automatizar tareas de desarrollo. Opera directamente en la terminal, comprende bases de código completas y puede trabajar a través de múltiples archivos y herramientas para lograr sus objetivos [1]. Esta Biblia de Implementación de Fase 2 profundiza en la arquitectura técnica y las capacidades de Claude Code, con el objetivo de alcanzar un 90% de completitud a partir de una versión 1 existente.

## MÓDULO A: Ciclo del Agente (Loop/ReAct)

El funcionamiento interno de Claude Code se basa en un **ciclo agéntico** que comprende tres fases principales: **recopilar contexto**, **tomar acción** y **verificar resultados** [2]. Estas fases no son discretas, sino que se entrelazan, permitiendo a Claude utilizar herramientas en cualquier momento del ciclo. Por ejemplo, puede buscar archivos para entender el código, editar para realizar cambios o ejecutar pruebas para verificar su trabajo [2].

El ciclo se adapta dinámicamente a la tarea. Una simple pregunta sobre la base de código podría requerir solo la recopilación de contexto, mientras que la corrección de un error podría implicar ciclos repetidos a través de las tres fases. Una refactorización extensa podría requerir una verificación exhaustiva. Claude toma decisiones sobre los pasos necesarios basándose en lo aprendido en el paso anterior, encadenando docenas de acciones y corrigiendo el rumbo según sea necesario [2].

La interacción humana es una parte integral de este ciclo. Los usuarios pueden interrumpir a Claude en cualquier momento para redirigir su enfoque, proporcionar contexto adicional o sugerir un enfoque diferente. Aunque Claude opera de forma autónoma, sigue siendo receptivo a la entrada del usuario [2].

El ciclo agéntico está impulsado por dos componentes fundamentales: **modelos** que realizan el razonamiento y **herramientas** que ejecutan las acciones. Claude Code actúa como el **arnés agéntico** alrededor de los modelos Claude, proporcionando las herramientas, la gestión del contexto y el entorno de ejecución necesarios para transformar un modelo de lenguaje en un agente de codificación capaz [2].

## MÓDULO B: Estados del Agente

Los estados de Claude Code no se describen explícitamente como un conjunto finito de estados discretos con transiciones formales, sino que se infieren a través de su **ciclo agéntico** y la gestión de subagentes. Los estados principales corresponden a las fases del ciclo agéntico [2]:

*   **Recopilación de Contexto (Gather Context)**: El agente está en un estado de comprensión, analizando la base de código, las instrucciones del usuario y cualquier información relevante para la tarea. Esto puede implicar la lectura de archivos, la búsqueda de información o la consulta de la memoria [2].
*   **Toma de Acción (Take Action)**: El agente está ejecutando operaciones para avanzar en la tarea. Esto incluye la edición de archivos, la ejecución de comandos, la interacción con herramientas o la delegación a subagentes [2].
*   **Verificación de Resultados (Verify Results)**: El agente está evaluando el impacto de sus acciones, por ejemplo, ejecutando pruebas, revisando la salida de comandos o analizando los cambios en el código. Este estado puede llevar a una nueva recopilación de contexto o a la toma de acciones adicionales si los resultados no son satisfactorios [2].

Además de estos estados del ciclo principal, la funcionalidad de **subagentes** introduce estados relacionados con su gestión y ejecución [3]:

*   **Activo/En Ejecución (Running)**: Un subagente está procesando una subtarea en su propio contexto. Los subagentes pueden ser monitoreados y sus resultados integrados por el agente principal [3].
*   **Reanudado (Resumed)**: Un subagente que fue pausado o completado puede ser reanudado para continuar su trabajo o para una nueva interacción [3].
*   **Forked**: Una conversación o tarea puede ser forked para permitir la exploración o experimentación sin afectar la conversación principal [3].

## MÓDULO C: Sistema de Herramientas

Claude Code tiene acceso a un conjunto de herramientas integradas que le permiten comprender y modificar la base de código. Los nombres de las herramientas son cadenas exactas utilizadas en reglas de permisos, listas de herramientas de subagentes y emparejadores de hooks [4]. Para deshabilitar una herramienta por completo, se puede añadir su nombre al array `deny` en la configuración de permisos [4]. Para añadir herramientas personalizadas, se puede conectar un servidor [Model Context Protocol (MCP)]() [4]. Para extender Claude con flujos de trabajo reutilizables basados en prompts, se puede escribir una *skill*, que se ejecuta a través de la herramienta `Skill` existente en lugar de añadir una nueva entrada de herramienta [4].

Las herramientas integradas se agrupan en cinco categorías principales, cada una representando un tipo diferente de agencia [2]:

1.  **Herramientas de lectura (Read Tools)**: Permiten a Claude acceder y comprender el contenido de los archivos. Ejemplos incluyen la lectura de archivos de código fuente, documentación o logs.
2.  **Herramientas de escritura (Write Tools)**: Permiten a Claude modificar archivos, como la edición de código, la adición de nuevas características o la corrección de errores.
3.  **Herramientas de ejecución (Execute Tools)**: Permiten a Claude ejecutar comandos en el entorno, como la ejecución de pruebas, la compilación de código o la instalación de dependencias.
4.  **Herramientas de búsqueda (Search Tools)**: Permiten a Claude buscar información dentro de la base de código o en la web.
5.  **Herramientas de interacción (Interact Tools)**: Permiten a Claude interactuar con servicios externos o con el usuario, como la creación de pull requests o la formulación de preguntas.

Además de estas capacidades primarias, Claude también dispone de herramientas para generar subagentes, hacer preguntas al usuario y otras tareas de orquestación [2]. Claude elige qué herramientas utilizar basándose en el prompt del usuario y en lo que aprende durante el proceso [2].

### Herramientas Específicas [4]:

*   **Agent**: Genera un subagente con su propia ventana de contexto para manejar una tarea. No requiere permiso.
*   **AskUserQuestion**: Formula preguntas de opción múltiple para recopilar requisitos o aclarar ambigüedades. No requiere permiso.
*   **Bash**: Ejecuta comandos de shell en el entorno. Requiere permiso. El comportamiento de la herramienta Bash incluye:
    *   **Persistencia del directorio de trabajo**: Cuando Claude ejecuta `cd` en la sesión principal, el nuevo directorio de trabajo se mantiene para comandos Bash posteriores, siempre que permanezca dentro del directorio del proyecto o un directorio de trabajo adicional. Las sesiones de subagentes nunca mantienen los cambios de directorio de trabajo. Si `cd` se dirige fuera de estos directorios, Claude Code se restablece al directorio del proyecto. Para deshabilitar este comportamiento, se puede establecer `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=1` [4].
    *   **Variables de entorno**: Las variables de entorno no persisten entre comandos. Para que persistan, se debe activar el entorno virtual o conda antes de iniciar Claude Code, o establecer `CLAUDE_ENV_FILE` a un script de shell, o usar un `SessionStart hook` [4].
*   **CronCreate**: Programa un prompt recurrente o único dentro de la sesión actual. Las tareas tienen un alcance de sesión y se restauran en [4].
*   **LSP (Language Server Protocol)**: Proporciona inteligencia de código a Claude desde un servidor de lenguaje en ejecución. Después de cada edición de archivo, informa automáticamente los errores de tipo y advertencias. Claude puede usarlo para navegar por el código (saltar a la definición de un símbolo, encontrar referencias, obtener información de tipo, listar símbolos, encontrar implementaciones, rastrear jerarquías de llamadas). Esta herramienta está inactiva hasta que se instala un plugin de inteligencia de código para el lenguaje [4].
*   **Monitor**: Permite a Claude observar algo en segundo plano y reaccionar cuando cambia, sin pausar la conversación. Puede monitorear archivos de log, PRs, trabajos de CI, directorios para cambios de archivos o la salida de scripts de larga duración. Claude escribe un pequeño script para la observación, lo ejecuta en segundo plano y recibe cada línea de salida a medida que llega. El Monitor utiliza las mismas reglas de permiso que Bash. No está disponible en Amazon Bedrock, Google Vertex AI o Microsoft Foundry, ni cuando `DISABLE_TELEMETRY` o `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` están configurados [4].
*   **PowerShell**: Permite a Claude ejecutar comandos de PowerShell de forma nativa en Windows. En Linux, macOS y WSL, la herramienta es opcional y requiere PowerShell 7 o posterior. Cuando está habilitada, Claude trata PowerShell como el shell principal, pero la herramienta Bash sigue estando disponible para scripts POSIX [4].
    *   **Limitaciones (Preview)**: Los perfiles de PowerShell no se cargan y, en Windows, el sandboxing no es compatible [4].

Para verificar qué herramientas están cargadas en una sesión en ejecución, se puede preguntar directamente a Claude o ejecutar `/mcp` para los nombres exactos de las herramientas MCP [4].

## MÓDULO D: Ejecución de Código

Claude Code ejecuta código principalmente a través de la herramienta **Bash** y, en entornos Windows, también a través de la herramienta **PowerShell** [4]. La ejecución de código se realiza en un entorno de terminal, lo que permite a Claude interactuar directamente con la base de código, ejecutar pruebas, compilar proyectos y realizar otras operaciones de desarrollo. La herramienta LSP (Language Server Protocol) complementa la ejecución al proporcionar inteligencia de código, permitiendo a Claude comprender y depurar el código de manera más efectiva [4].

### Entorno de Ejecución [4]:

*   **Bash**: Utilizado en macOS, Linux y WSL. Cada comando se ejecuta en un proceso separado. La persistencia del directorio de trabajo se mantiene dentro del directorio del proyecto o directorios adicionales configurados. Las variables de entorno no persisten entre comandos Bash a menos que se configuren explícitamente a través de `CLAUDE_ENV_FILE` o `SessionStart hook`.
*   **PowerShell**: Disponible en Windows de forma nativa y opcional en Linux, macOS y WSL (requiere PowerShell 7+). En Windows, si Git Bash no está instalado, PowerShell se habilita automáticamente. Si Git Bash está presente, la habilitación es progresiva. La herramienta PowerShell tiene limitaciones en la vista previa, como la no carga de perfiles de PowerShell y la falta de soporte de sandboxing en Windows.

### Manejo de Errores:

Aunque la documentación no detalla explícitamente un módulo de manejo de errores, se infiere que Claude Code utiliza la salida de los comandos ejecutados (por ejemplo, errores de compilación, fallos de pruebas) para identificar problemas y corregirlos. La herramienta LSP, al reportar errores de tipo y advertencias después de cada edición, ayuda a Claude a corregir problemas sin un paso de compilación separado [4]. El ciclo agéntico de "verificar resultados" también implica el análisis de la salida de la ejecución de código para determinar si las acciones fueron exitosas o si se requieren más iteraciones para corregir errores [2].

## MÓDULO E: Sandbox y Entorno

Claude Code opera en un entorno que le permite interactuar de manera segura y controlada con la base de código del usuario. La documentación menciona varios aspectos relacionados con el entorno y el sandboxing [4]:

*   **Aislamiento**: Los subagentes operan en su propia ventana de contexto, lo que ayuda a preservar el contexto de la conversación principal y a aplicar restricciones específicas de herramientas [3]. Aunque no se detalla un sandbox a nivel de sistema operativo para el agente principal, la separación de contextos para subagentes sugiere un nivel de aislamiento lógico. La herramienta PowerShell tiene una limitación conocida en la vista previa donde el sandboxing no es compatible en Windows [4].
*   **Seguridad**: La configuración de permisos juega un papel crucial en la seguridad, permitiendo a los usuarios definir qué herramientas puede usar Claude y con qué alcance. Las reglas de permisos se pueden configurar para permitir o denegar el uso de herramientas específicas [4]. Además, los archivos de configuración pueden ser gestionados en diferentes ámbitos (Managed, User, Project, Local), con el ámbito Managed teniendo la mayor precedencia para aplicar políticas de seguridad a nivel de organización [5].
*   **Recursos**: Claude Code puede acceder a la base de código completa del usuario y a las herramientas disponibles en el entorno de la terminal. Esto incluye la capacidad de leer y editar archivos, ejecutar comandos y utilizar servicios externos a través de MCP [1]. Los archivos de configuración, como `settings.json` y `CLAUDE.md`, se almacenan en directorios específicos (`~/.claude/`, `.claude/`) y son leídos por Claude Code al inicio de cada sesión para establecer estándares de codificación, decisiones de arquitectura y listas de verificación [5] [1].

## MÓDULO F: Memoria y Contexto

Claude Code gestiona la memoria y el contexto de varias maneras para mantener la coherencia y la relevancia a lo largo de las interacciones. La memoria de Claude Code se puede categorizar en memoria persistente y contexto de sesión [1] [3]:

*   **CLAUDE.md**: Es un archivo Markdown que se añade a la raíz del proyecto. Claude Code lo lee al inicio de cada sesión para establecer estándares de codificación, decisiones de arquitectura, bibliotecas preferidas y listas de verificación de revisión. Este archivo actúa como una forma de memoria persistente a nivel de proyecto, guiando el comportamiento de Claude en ese proyecto específico [1].
*   **Auto Memory**: Claude Code construye una "memoria automática" a medida que trabaja, guardando aprendizajes como comandos de compilación y conocimientos de depuración a través de las sesiones sin que el usuario tenga que escribir nada. Esta es una forma de memoria persistente y automática que mejora la eficiencia de Claude con el tiempo [1].
*   **Ventana de Contexto (Context Window)**: Cada sesión de Claude Code, y cada subagente, opera dentro de su propia ventana de contexto. Esta ventana es donde Claude mantiene la conversación actual, el código relevante y los resultados de las herramientas. La documentación menciona una "visualización de la ventana de contexto" que muestra cómo un subagente maneja la investigación en su propia ventana separada para preservar el contexto de la conversación principal [3].
*   **Memoria Persistente para Subagentes**: Los subagentes pueden configurarse con un directorio de memoria persistente (por ejemplo, `~/.claude/agent-memory/`) para acumular conocimientos a través de las conversaciones, como patrones de bases de código y problemas recurrentes. Esto permite a los subagentes aprender y mejorar su rendimiento con el tiempo [3].
*   **Auto-compactación (Auto-compaction)**: La documentación de subagentes menciona la auto-compactación como una forma de gestionar el contexto, aunque no se proporcionan detalles específicos sobre cómo funciona [3]. Se infiere que es un mecanismo para resumir o reducir el tamaño del contexto para mantenerlo dentro de los límites de la ventana de contexto.
*   **Memoria de 3 Capas**: Aunque la descripción del agente menciona "memoria de 3 capas", la documentación oficial no detalla explícitamente esta arquitectura. Sin embargo, se puede inferir que las tres capas podrían corresponder a:
    1.  **Memoria a corto plazo/Contexto de sesión**: La ventana de contexto activa de la conversación actual, incluyendo prompts, resultados de herramientas y respuestas de Claude.
    2.  **Memoria a medio plazo/Memoria automática**: Aprendizajes persistentes y automáticos (auto memory) que Claude acumula a través de las sesiones.
    3.  **Memoria a largo plazo/Conocimiento del proyecto**: Información definida por el usuario en `CLAUDE.md` y posiblemente otros archivos de configuración del proyecto que proporcionan instrucciones y estándares a largo plazo.

## MÓDULO G: Browser/GUI

Claude Code, aunque es un agente de terminal, ofrece varias interfaces y se integra con entornos gráficos y web para extender su funcionalidad [1]:

*   **Terminal CLI**: La interfaz principal para interactuar con Claude Code, permitiendo editar archivos, ejecutar comandos y gestionar proyectos desde la línea de comandos [1].
*   **VS Code y JetBrains IDEs**: Claude Code se integra con estos entornos de desarrollo integrados, lo que sugiere que puede interactuar con sus interfaces gráficas para tareas como la edición de código y la visualización de resultados [1].
*   **Aplicación de Escritorio (Desktop App)**: Proporciona una interfaz gráfica para ejecutar múltiples sesiones en paralelo, con una barra lateral para gestionar el trabajo y una interfaz para la revisión visual de diferencias (`/desktop`) [1].
*   **Web**: Existe una versión web de Claude Code (`claude.ai/code`) y la capacidad de iniciar tareas de larga duración en la web o en la aplicación iOS y luego "teletransportarlas" a la terminal (`claude --teleport`) [1].
*   **Extensión de Chrome (Beta)**: Permite la integración con el navegador web, aunque los detalles específicos de cómo interactúa con la GUI del navegador (hacer clic, manejar login) no se detallan explícitamente en la documentación revisada [1].
*   **Uso de Computadora (Preview)**: Una funcionalidad en vista previa que sugiere una interacción más profunda con el sistema operativo y sus elementos gráficos [1].
*   **Remote Control**: Permite mover el trabajo entre entornos, incluyendo la posibilidad de trabajar desde un teléfono o cualquier navegador [1].

Aunque la documentación no especifica un mecanismo de "hacer clic" o "manejar login" a nivel de API para la interacción con el navegador, la existencia de una extensión de Chrome y la capacidad de trabajar desde la web y aplicaciones móviles implican que Claude Code puede operar en estos entornos, posiblemente aprovechando las capacidades de automatización web o las interfaces de usuario proporcionadas por estas plataformas.

## MÓDULO H: Multi-agente

Claude Code tiene capacidades robustas para la operación multi-agente, permitiendo la creación y coordinación de subagentes. La descripción del agente menciona "10 sub-agentes paralelos", lo cual es consistente con las funcionalidades documentadas [1] [3].

### Subagentes (Subagents) [3]:

Los subagentes son asistentes de IA especializados que manejan tipos específicos de tareas. Se utilizan para evitar que una tarea secundaria inunde la conversación principal con resultados de búsqueda, logs o contenido de archivos que no se volverán a referenciar. El subagente realiza ese trabajo en su propio contexto y devuelve solo el resumen [3].

*   **Contexto Aislado**: Cada subagente se ejecuta en su propia ventana de contexto con un prompt de sistema personalizado, acceso a herramientas específicas y permisos independientes. Cuando Claude encuentra una tarea que coincide con la descripción de un subagente, delega la tarea a ese subagente, que trabaja de forma independiente y devuelve los resultados [3].
*   **Beneficios**: Los subagentes ayudan a preservar el contexto, aplicar restricciones (limitando las herramientas que un subagente puede usar), reutilizar configuraciones en proyectos y especializar el comportamiento con prompts de sistema enfocados. También pueden ayudar a controlar los costos al enrutar tareas a modelos más rápidos y económicos como Haiku [3].
*   **Subagentes Integrados**: Claude Code incluye subagentes integrados como **Explore** (agente de solo lectura optimizado para buscar y analizar bases de código, usando el modelo Haiku y herramientas de solo lectura), **Plan** y **General-purpose** [3].
*   **Creación de Subagentes Personalizados**: Los subagentes se definen en archivos Markdown con *frontmatter* YAML. Se pueden crear manualmente o usar el comando `/agents`. La configuración incluye la elección del modelo (por ejemplo, Sonnet para equilibrio entre capacidad y velocidad), el control de las capacidades del subagente (herramientas disponibles), la restricción de qué subagentes pueden ser generados, el alcance de los servidores MCP, los modos de permiso, la precarga de *skills* y la habilitación de memoria persistente [3].
*   **Gestión de Subagentes**: El comando `/agents` abre una interfaz con pestañas para gestionar subagentes, mostrando los subagentes activos, permitiendo crear nuevos, editar configuraciones existentes y eliminar subagentes personalizados [3].

### Equipos de Agentes (Agent Teams) [3]:

Si se necesitan múltiples agentes trabajando en paralelo y comunicándose entre sí, se utilizan **equipos de agentes**. Los equipos de agentes coordinan el trabajo a través de sesiones separadas, a diferencia de los subagentes que trabajan dentro de una única sesión. Un agente líder coordina el trabajo, asigna subtareas y fusiona los resultados [1] [3]. Esto es consistente con la descripción de "10 sub-agentes paralelos" mencionada en la tarea, lo que sugiere que Claude Code puede orquestar múltiples instancias de agentes para trabajar en conjunto.

## MÓDULO I: Integraciones

Claude Code está diseñado para integrarse con una variedad de servicios y herramientas externas para ampliar sus capacidades [1].

*   **Model Context Protocol (MCP)**: Es un estándar abierto para conectar herramientas de IA a fuentes de datos externas. Con MCP, Claude Code puede leer documentos de diseño en Google Drive, actualizar tickets en Jira, extraer datos de Slack o usar herramientas personalizadas del usuario [1]. La configuración de servidores MCP puede ser a nivel de usuario o local, y los servidores MCP con alcance de proyecto se almacenan en `.mcp.json` [5].
*   **GitHub Actions y GitLab CI/CD**: Claude Code puede automatizar la revisión de código y la clasificación de problemas en entornos de Integración Continua/Entrega Continua (CI/CD) utilizando GitHub Actions o GitLab CI/CD [1].
*   **Slack**: Claude Code puede integrarse con Slack, permitiendo a los usuarios mencionar a `@Claude` en un chat con un informe de error y recibir un pull request como respuesta [1].
*   **API Keys y Autenticación**: Las claves API y la autenticación se pueden almacenar de forma segura en el ámbito de usuario (`~/.claude/settings.json`) [5].
*   **Plugins**: Claude Code soporta un sistema de plugins que permite descubrir e instalar plugins preconstruidos o crear plugins personalizados. Los plugins pueden declarar monitores que se inician automáticamente cuando el plugin está activo [4].
*   **Hooks**: Permiten ejecutar comandos de shell antes o después de las acciones de Claude Code, como el autoformateo después de cada edición de archivo o la ejecución de lint antes de un commit [1]. Los hooks pueden ser de varios tipos, incluyendo HTTP hooks y MCP tool hooks [4].

## MÓDULO J: Multimodal

La documentación revisada de Claude Code se centra principalmente en sus capacidades de codificación y procesamiento de texto. No se encontró información explícita que detalle el procesamiento de imágenes, video o audio, ni los modelos específicos utilizados para tales fines. La descripción del agente en la tarea menciona "agente de terminal", lo que generalmente implica una interacción basada en texto. Sin embargo, la existencia de una "aplicación de escritorio" con una interfaz gráfica y una "extensión de Chrome (beta)" podría sugerir futuras capacidades multimodales o la capacidad de interactuar con contenido visual a través de estas interfaces, aunque no se especifica cómo [1]. Por lo tanto, en este momento, no hay evidencia técnica concreta que respalde capacidades multimodales directas de procesamiento de imágenes, video o audio en Claude Code.

## MÓDULO K: Límites y Errores

Claude Code, como cualquier sistema complejo, tiene limitaciones y mecanismos para manejar errores [4] [5]:

### Límites Conocidos:

*   **Persistencia de Variables de Entorno**: Las variables de entorno no persisten entre comandos Bash a menos que se configuren explícitamente [4].
*   **Sandboxing de PowerShell en Windows**: Durante la vista previa, el sandboxing no es compatible para la herramienta PowerShell en Windows [4].
*   **Disponibilidad de la Herramienta Monitor**: La herramienta Monitor no está disponible en Amazon Bedrock, Google Vertex AI o Microsoft Foundry, ni cuando `DISABLE_TELEMETRY` o `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` están configurados [4].
*   **Perfiles de PowerShell**: Los perfiles de PowerShell no se cargan durante la vista previa de la herramienta PowerShell [4].
*   **Precedencia de Configuración**: Las configuraciones de ámbito gestionado (Managed scope) no pueden ser anuladas por configuraciones de ámbito de usuario o proyecto, lo que puede limitar la personalización en entornos empresariales [5].
*   **Límites de la Ventana de Contexto**: Aunque no se especifican límites numéricos, la existencia de subagentes y la "auto-compactación" sugieren que la ventana de contexto tiene un tamaño finito y que la gestión eficiente del contexto es necesaria para evitar que se "inunde" [3].

### Manejo de Errores y Recuperación:

*   **Corrección de Errores por LSP**: La herramienta LSP reporta automáticamente errores de tipo y advertencias después de cada edición de archivo, permitiendo a Claude corregir problemas sin un paso de compilación separado [4].
*   **Ciclo Agéntico de Verificación**: El ciclo agéntico incluye una fase de "verificación de resultados" donde Claude evalúa el impacto de sus acciones. Si los resultados no son satisfactorios (por ejemplo, pruebas fallidas, errores de compilación), Claude puede volver a la fase de "recopilación de contexto" o "toma de acción" para corregir el problema [2].
*   **Interrupción y Dirección del Usuario**: Los usuarios pueden interrumpir a Claude en cualquier momento para redirigir su enfoque, proporcionar contexto adicional o pedirle que pruebe un enfoque diferente, lo que permite la intervención humana en caso de que Claude se equivoque o se atasque [2].
*   **Backups de Archivos de Configuración**: Claude Code crea automáticamente copias de seguridad con marca de tiempo de los archivos de configuración y retiene las cinco copias de seguridad más recientes para evitar la pérdida de datos [5].
*   **Troubleshooting**: La documentación menciona secciones de "Troubleshooting" para la instalación, el inicio de sesión, el rendimiento, la estabilidad y la depuración de la configuración, lo que indica que existen recursos y guías para resolver problemas comunes [1].

## MÓDULO L: Benchmarks

La documentación oficial de Claude Code no proporciona resultados de benchmarks específicos como SWE-bench, WebArena, OSWorld u otros. La información disponible se centra en las capacidades funcionales y la arquitectura del agente, más que en métricas de rendimiento comparativas. Para obtener esta información, sería necesario buscar en publicaciones de investigación, blogs de la comunidad o anuncios de Anthropic que no se encontraron directamente en la documentación del producto. Sin embargo, la capacidad de Claude Code para "construir características y corregir errores" y "automatizar tareas tediosas" sugiere que está diseñado para un rendimiento efectivo en tareas de desarrollo de software [1].

## Lecciones para el Monstruo

1.  **Diseño Modular y Extensible**: La arquitectura de Claude Code, con su enfoque en herramientas, skills y subagentes, demuestra la importancia de un diseño modular. Esto permite que el agente sea altamente extensible y adaptable a diversas tareas y entornos. Para "El Monstruo", esto significa construir un núcleo robusto con puntos de extensión claros para nuevas funcionalidades y adaptaciones.
2.  **Gestión de Contexto y Memoria Multifacética**: La combinación de `CLAUDE.md` para instrucciones a largo plazo, "auto memory" para aprendizajes persistentes y ventanas de contexto aisladas para subagentes, ofrece un modelo sofisticado de gestión de memoria. "El Monstruo" debería implementar un sistema de memoria en capas que combine conocimiento a largo plazo, aprendizaje incremental y contexto de sesión dinámico.
3.  **Capacidades Multi-agente para Escalabilidad**: La capacidad de generar y coordinar subagentes, así como la noción de "equipos de agentes" que trabajan en paralelo, es crucial para escalar la complejidad de las tareas. "El Monstruo" debe ser capaz de descomponer tareas grandes en subtareas y delegarlas a agentes especializados que puedan trabajar de forma autónoma o coordinada.
4.  **Interacción Humana en el Loop**: La posibilidad de que el usuario interrumpa, dirija y proporcione contexto adicional en cualquier punto del ciclo agéntico es vital para la usabilidad y la corrección de errores. "El Monstruo" debe tener mecanismos claros para la intervención humana, permitiendo la supervisión y el ajuste en tiempo real.
5.  **Seguridad y Permisos Granulares**: El sistema de ámbitos de configuración y reglas de permisos detalladas para las herramientas es fundamental para la seguridad y el control. "El Monstruo" debe implementar un sistema de permisos granular que permita a los usuarios y administradores definir con precisión qué acciones puede realizar el agente y en qué entornos, especialmente cuando se interactúa con sistemas de archivos y servicios externos.

## Referencias

[1] Claude Code overview - Claude Code Docs. (n.d.). Retrieved from [https://code.claude.com/docs/en/overview](https://code.claude.com/docs/en/overview)
[2] How Claude Code works - Claude Code Docs. (n.d.). Retrieved from [https://code.claude.com/docs/en/how-claude-code-works](https://code.claude.com/docs/en/how-claude-code-works)
[3] Create custom subagents - Claude Code Docs. (n.d.). Retrieved from [https://code.claude.com/docs/en/subagents](https://code.claude.com/docs/en/subagents)
[4] Tools reference - Claude Code Docs. (n.d.). Retrieved from [https://code.claude.com/docs/en/tools-reference](https://code.claude.com/docs/en/tools-reference)
[5] Claude Code settings - Claude Code Docs. (n.d.). Retrieved from [https://code.claude.com/docs/en/configuration](https://code.claude.com/docs/en/configuration)


---

## Fase 3 — Módulos Complementarios: Claude Code v2.1 (Anthropic)

### Benchmarks reales de SWE-bench y GAIA

Claude Code v2.1, como herramienta de codificación agentica, se beneficia directamente del rendimiento de los modelos subyacentes de Claude de Anthropic. La evaluación de su capacidad se refleja en los resultados de estos modelos en benchmarks estándar de la industria como SWE-bench y GAIA. Es crucial entender que Claude Code v2.1 no es un modelo en sí mismo, sino una aplicación que orquesta las capacidades de los modelos Claude para tareas de desarrollo de software. Por lo tanto, los benchmarks de los modelos Claude más recientes son los indicadores más relevantes de su profundidad técnica.

#### Rendimiento en SWE-bench

SWE-bench es un benchmark diseñado para evaluar la capacidad de los modelos de lenguaje grandes (LLMs) para resolver problemas de ingeniería de software del mundo real. Este benchmark mide la habilidad de un modelo para diagnosticar y corregir errores en bases de código existentes, así como para implementar nuevas funcionalidades. Los resultados se expresan como el porcentaje de tareas resueltas correctamente. La tabla a continuación presenta los resultados de varios modelos Claude en el benchmark SWE-bench Verified, un subconjunto filtrado por humanos de 500 instancias [1].

| Modelo | % Resuelto | Costo Promedio ($) | Organización | Fecha | Versión del Agente |
|---|---|---|---|---|---|
| Claude 4.5 Opus (high reasoning) | 76.80 | $0.75 | Anthropic | 2026-02-17 | 2.0.0 |
| Claude Opus 4.6 | 75.60 | $0.55 | Anthropic | 2026-02-17 | 2.0.0 |
| Claude 4.5 Sonnet (high reasoning) | 71.40 | $0.66 | Anthropic | 2026-02-17 | 2.0.0 |
| Claude 4.5 Haiku (high reasoning) | 66.60 | $0.33 | Anthropic | 2026-02-17 | 2.0.0 |

Estos resultados demuestran la capacidad de los modelos Claude para abordar tareas complejas de codificación. El modelo Claude 4.5 Opus, con su enfoque en el razonamiento de alto nivel, lidera los resultados entre los modelos de Anthropic, lo que sugiere que Claude Code v2.1, al aprovechar este modelo, puede ofrecer un rendimiento robusto en la resolución de problemas de software. Es importante destacar que el porcentaje de resolución se refiere a la capacidad del modelo para generar una solución que pasa las pruebas unitarias y de integración del problema [1].

#### Rendimiento en GAIA

GAIA (General AI Assistants) es un benchmark que evalúa las capacidades de los LLMs de próxima generación con herramientas aumentadas, prompting eficiente y acceso a búsqueda web. Este benchmark requiere un conjunto de habilidades fundamentales como razonamiento, manejo multimodal, navegación web y uso de herramientas. Los resultados se presentan como un porcentaje de precisión y se dividen en niveles de dificultad. La tabla a continuación muestra el rendimiento de varios modelos Claude en el leaderboard de GAIA [2].

| Scaffold | Modelo Primario | Verificado | Precisión | Nivel 1 | Nivel 2 | Nivel 3 | Costo (USD) | Ejecuciones | Trazas |
|---|---|---|---|---|---|---|---|---|---|
| HAL Generalist Agent | Claude Sonnet 4.5 (September 2025) | ✓ | 74.55% | 82.07% | 72.68% | 65.39% | $178.20 | 2 | Descargar |
| | Claude Sonnet 4.5 High (September 2025) | ✓ | 70.91% | 77.36% | 74.42% | 46.15% | $179.86 | 1 | Descargar |
| | Claude Opus 4.1 High (August 2025) | ✓ | 68.48% | 71.70% | 70.93% | 53.85% | $562.24 | 1 | Descargar |
| | Claude Opus 4 High (May 2025) | ✓ | 64.85% | 71.70% | 67.44% | 42.31% | $665.89 | 1 | Descargar |
| | Claude-3.7 Sonnet High (February 2025) | ✓ | 64.24% | 67.92% | 63.95% | 57.69% | $122.49 | 1 | Descargar |
| | Claude Opus 4.1 (August 2025) | ✓ | 64.24% | 71.70% | 66.28% | 42.31% | $641.86 | 1 | Descargar |
| | Claude Opus 4 (May 2025) | ✓ | 57.58% | 66.04% | 56.98% | 42.31% | $1686.07 | 1 | Descargar |
| | Claude Haiku 4.5 (October 2025) | ✓ | 66.60% | 71.70% | 63.95% | 53.85% | $0.33 | 1 | Descargar |

El rendimiento en GAIA subraya la capacidad de los modelos Claude para actuar como asistentes de IA generalistas, manejando tareas que van más allá de la simple generación de código, incluyendo razonamiento complejo y el uso de herramientas externas. La presencia de diferentes niveles de dificultad (Nivel 1, 2 y 3) en GAIA permite una evaluación granular de las habilidades del modelo, donde el Nivel 3 representa las tareas más desafiantes. Los modelos Claude demuestran una competencia considerable en estos niveles, lo que es fundamental para una herramienta como Claude Code v2.1 que busca automatizar interacciones informáticas complejas [2].

En resumen, los benchmarks SWE-bench y GAIA proporcionan una visión técnica sólida del rendimiento de los modelos Claude que impulsan Claude Code v2.1. Estos resultados, que muestran porcentajes de resolución y precisión significativos, validan la capacidad del agente para abordar desafíos de codificación y tareas de asistencia general de IA con un alto grado de competencia. Estos resultados, que muestran porcentajes de resolución y precisión significativos, validan la capacidad del agente para abordar desafíos de codificación y tareas de asistencia general de IA con un alto grado de competencia técnica. La mejora continua en estos benchmarks es un indicador clave del avance de las capacidades de Claude Code v2.1.

### Integraciones con servicios externos y OAuth

Claude Code v2.1, al ser una herramienta de desarrollo impulsada por los modelos Claude de Anthropic, ofrece capacidades de integración robustas con servicios externos y un manejo sofisticado de la autenticación OAuth. La característica clave que facilita estas integraciones es el **uso de herramientas (tool use)**, introducido como una función beta en Claude 2.1 [3]. Esta funcionalidad permite a Claude interactuar con procesos, productos y APIs existentes de los usuarios, ampliando significativamente su interoperabilidad.

#### Uso de Herramientas (Tool Use)

El uso de herramientas permite a Claude orquestar funciones o APIs definidas por el desarrollador, buscar en fuentes web y recuperar información de bases de conocimiento privadas. Los usuarios pueden definir un conjunto de herramientas para que Claude las utilice y especificar una solicitud. El modelo decide qué herramienta es necesaria para lograr la tarea y ejecuta una acción en nombre del usuario. Esto incluye, pero no se limita a [3]:

*   **Cálculo numérico complejo**: Utilizar una calculadora para razonamiento numérico.
*   **Traducción de lenguaje natural a llamadas API estructuradas**: Convertir solicitudes en lenguaje humano a formatos que las APIs puedan entender.
*   **Búsqueda de bases de datos y web**: Responder preguntas buscando en bases de datos o utilizando APIs de búsqueda web.
*   **Acciones en software vía APIs privadas**: Realizar acciones simples en aplicaciones de software a través de interfaces de programación de aplicaciones privadas.
*   **Conexión a conjuntos de datos de productos**: Hacer recomendaciones y ayudar a los usuarios a completar compras.

Esta capacidad es fundamental para Claude Code v2.1, ya que le permite ir más allá de la simple generación de código y participar activamente en flujos de trabajo de desarrollo complejos que requieren interacción con sistemas externos. Por ejemplo, un desarrollador podría instruir a Claude Code para que interactúe con un sistema de control de versiones (como GitHub), un sistema de gestión de proyectos (como Jira) o incluso un entorno de despliegue, todo a través de APIs definidas [4].

#### Manejo de OAuth y Autenticación

Claude Code v2.1 soporta múltiples métodos de autenticación, adaptándose a diferentes configuraciones de usuario y equipo. Para usuarios individuales, la autenticación se puede realizar a través de una cuenta de Claude.ai. Para equipos, se pueden utilizar métodos de autenticación empresarial. El protocolo OAuth 2.0 es un componente crítico para la integración segura con servicios externos, permitiendo que Claude Code acceda a recursos protegidos en nombre del usuario sin necesidad de compartir credenciales directamente [5].

La implementación de OAuth en Claude Code v2.1 se alinea con las mejores prácticas de seguridad, incluyendo el uso de Proof Key for Code Exchange (PKCE) para prevenir ataques de intercepción de códigos de autorización. Esto es particularmente relevante en entornos donde Claude Code opera en servidores sin cabeza (headless servers) o en entornos de desarrollo integrado (IDEs) como VS Code o JetBrains, donde la interacción directa del usuario para la autenticación puede ser limitada [6].

Existen recursos y tutoriales que demuestran cómo conectar APIs personalizadas aseguradas con OAuth 2.0 a Claude utilizando el Model Context Protocol (MCP), lo que subraya la flexibilidad y extensibilidad del sistema de integración de Claude Code [7]. Además, la comunidad ha discutido cómo completar el flujo de OAuth para Claude Code en un servidor sin cabeza, lo que implica iniciar el flujo de OAuth en el servidor, completar el paso del navegador en una máquina local y luego pasar el token de autenticación de vuelta al servidor [8].

En resumen, las capacidades de integración de Claude Code v2.1 a través del uso de herramientas y su soporte para OAuth 2.0 lo posicionan como una herramienta altamente adaptable para entornos de desarrollo modernos. Permite a los desarrolladores automatizar tareas complejas que abarcan múltiples servicios y plataformas, manteniendo al mismo tiempo un alto nivel de seguridad en la autenticación y autorización. La capacidad de definir y orquestar APIs externas convierte a Claude Code en un asistente de IA verdaderamente versátil para la ingeniería de software.

### Referencias y Fuentes Verificables Adicionales

[1] SWE-bench Leaderboards. (n.d.). Recuperado de [https://www.swebench.com/](https://www.swebench.com/)
[2] GAIA Leaderboard - a Hugging Face Space by gaia-benchmark. (n.d.). Recuperado de [https://huggingface.co/spaces/gaia-benchmark/leaderboard](https://huggingface.co/spaces/gaia-benchmark/leaderboard)
[3] Anthropic. (2023, Noviembre 21). Introducing Claude 2.1. Recuperado de [https://www.anthropic.com/news/claude-2-1](https://www.anthropic.com/news/claude-2-1)
[4] DataCamp. (2026, Enero 12). Claude Code 2.1: A Guide With Practical Examples. Recuperado de [https://www.datacamp.com/tutorial/claude-code-2-1-guide](https://www.datacamp.com/tutorial/claude-code-2-1-guide)
[5] Claude Code Docs. (n.d.). Authentication. Recuperado de [https://code.claude.com/docs/en/authentication](https://code.claude.com/docs/en/authentication)
[6] Reddit. (2026, Febrero 28). How to complete OAuth flow for Claude Code on a headless server. Recuperado de [https://www.reddit.com/r/ClaudeAI/comments/1rgxj0p/how_to_complete_oauth_flow_for_claude_code_on_a/](https://www.reddit.com/r/ClaudeAI/comments/1rgxj0p/how_to_complete_oauth_flow_for_claude_code_on_a/)
[7] MCP Market. (n.d.). OAuth Client Setup | Claude Code Skill for API Integration. Recuperado de [https://mcpmarket.com/tools/skills/oauth-client-setup-1](https://mcpmarket.com/tools/skills/oauth-client-setup-1)
[8] YouTube. (2026, Febrero 5). Connect Your OAuth 2 API to Claude in 3 Minutes (MCP Tutorial). Recuperado de [https://www.youtube.com/watch?v=N0y7sDRkDt8](https://www.youtube.com/watch?v=N0y7sDRkDt8)


# Biblia de Implementación: Claude Code v2.1 (Anthropic)

## Benchmarks actualizados SWE-bench 2026 para Claude Code v2.1 (Anthropic)

La denominación "Claude Code v2.1" parece referirse a una implementación o uso de los modelos Claude de Anthropic (Opus, Sonnet, Haiku) optimizados para tareas de codificación, más que a un modelo independiente. Las referencias más recientes y relevantes para el rendimiento en SWE-bench se asocian directamente con las versiones de los modelos Claude subyacentes.

A continuación, se presenta un resumen de los benchmarks de SWE-bench para los modelos Claude más recientes, con énfasis en la información disponible para 2026:

| Modelo Claude | % Resuelto (SWE-bench Verified) | Fecha de Benchmark | Fuente |
|---|---|---|---|
| Claude Mythos Preview | 93.9% | Abr 13, 2026 | [CodeAnt AI][1], [Mindstudio AI][2] |
| Claude Opus 4.7 (Adaptive) | 87.6% | Abr 16, 2026 | [BenchLM.ai][3], [Vellum][4] |
| Claude Opus 4.6 | 75.60% | Feb 17, 2026 | [SWE-bench Leaderboards][5] |
| Claude Opus 4.5 | 80.9% | Ene 11, 2026 | [Medium - Cognidownunder][6] |
| Claude 4.5 Sonnet (high reasoning) | 71.40% | Feb 17, 2026 | [SWE-bench Leaderboards][5] |
| Claude 4.5 Haiku (high reasoning) | 66.60% | Feb 17, 2026 | [SWE-bench Leaderboards][5] |

**Notas Adicionales:**

*   **Claude Mythos Preview:** Este modelo muestra un rendimiento excepcional, liderando el benchmark SWE-bench Verified con un 93.9% [1] [2]. Se menciona que este salto de rendimiento es significativo para los flujos de trabajo de codificación agéntica [2].
*   **Claude Opus 4.7:** Lanzado el 16 de abril de 2026, Opus 4.7 muestra una mejora considerable en Rakuten-SWE-Bench, resolviendo 3 veces más tareas de producción que Opus 4.6, con ganancias de dos dígitos en Calidad de Código y Calidad de Pruebas [7]. En SWE-bench Verified, Opus 4.7 alcanza un 87.6%, superando a Gemini 3.1 Pro [4].
*   **Claude Code 2.1.0:** Se ha reportado que la base de las capacidades de Claude Code 2.1.0 es Opus 4.5, que logró un 80.9% en SWE-bench Verified, siendo el primer modelo en alcanzar este nivel [6].
*   **SWE-bench Verified:** Es un subconjunto filtrado por humanos de 500 instancias, utilizado para evaluar modelos con el mismo arnés [5].

## Lista completa de MCP servers compatibles con Claude Code v2.1 (Anthropic)

Claude Code v2.1 funciona como un cliente del Model Context Protocol (MCP), lo que le permite extender sus capacidades al conectarse a diversos servidores MCP. Esta integración permite a Claude Code interactuar con herramientas externas y APIs, facilitando tareas complejas de desarrollo de software y otras operaciones [8] [9].

La compatibilidad con servidores MCP se realiza a través de múltiples métodos de transporte, incluyendo STDIO, SSE y HTTP, lo que ofrece flexibilidad en la configuración [10].

### Tipos de MCP Servers y Ejemplos de Integraciones:

Se han identificado varios tipos de servidores MCP y ejemplos de integraciones que funcionan con Claude Code:

*   **GitHub MCP Server:** Este es uno de los servidores MCP más impactantes y comúnmente utilizados con Claude Code, permitiendo la interacción con repositorios de GitHub para tareas de desarrollo [11] [12].
*   **Filesystem MCP Server:** Permite a Claude Code interactuar con el sistema de archivos, lo que es fundamental para la manipulación de código y archivos locales [8].
*   **Chrome DevTools MCP Server:** Facilita la interacción con las herramientas de desarrollo de Chrome, útil para tareas de depuración y desarrollo web [8].
*   **Playwright MCP Server:** Permite la automatización de navegadores, lo que es valioso para pruebas y raspado web [8].
*   **Custom MCP Servers:** Los desarrolladores pueden crear sus propios servidores MCP para extender las capacidades de Claude con herramientas y funcionalidades personalizadas [10].
*   **Blender MCP Connector:** Los desarrolladores de Blender han creado un conector MCP oficial para Claude, lo que permite a los artistas 3D utilizar Claude para tareas relacionadas con Blender [13].
*   **FastMCP:** Una plataforma que facilita la integración de Claude Code con servidores MCP, ofreciendo soporte para varios métodos de transporte [10].

### Consideraciones de Compatibilidad:

*   **Versiones:** Algunas versiones anteriores de Claude Code (v2.1.0 o anteriores) pueden requerir formatos de comando legados para la instalación y configuración de MCP servers [14].
*   **API de Conector MCP de Anthropic:** Varias empresas han implementado servidores MCP remotos a los que los desarrolladores pueden conectarse a través de la API de conector MCP de Anthropic, ampliando aún más las capacidades de Claude [15].

## Manejo de errores en sub-agentes paralelos de Claude Code v2.1 (Anthropic)

El manejo de errores en sub-agentes paralelos de Claude Code v2.1 es un aspecto crítico para la robustez y eficiencia de los flujos de trabajo de desarrollo de software. La arquitectura de sub-agentes permite la paralelización de tareas, pero también introduce desafíos en la gestión de fallos, agotamiento de contexto y tiempos de espera.

### Fallos de Herramientas y Sub-agentes:

Cuando un sub-agente falla o devuelve una salida inesperada, el manejo de errores se vuelve esencial. Depurar una ejecución paralela con múltiples sub-agentes puede ser significativamente más complejo que depurar una ejecución secuencial [16]. Es importante que Claude Code pueda identificar y gestionar estos fallos para evitar la interrupción completa del proceso.

### Agotamiento del Contexto en Sub-agentes Paralelos:

Un problema reportado en GitHub es que, cuando Claude Code crea múltiples sub-agentes para paralelizar el trabajo, todos o la mayoría de ellos pueden llenar simultáneamente sus ventanas de contexto y detenerse con un mensaje de "context window full" [17]. Esto sugiere la necesidad de mecanismos de gestión de contexto más sofisticados para sub-agentes paralelos, que permitan una asignación y liberación eficiente del contexto para evitar el agotamiento.

### Manejo de Tiempos de Espera (Timeouts):

Claude Code ha tenido históricamente un tiempo de espera fijo de 5 minutos para las solicitudes internas, que era distinto del tiempo de espera de la API configurable a través de variables de entorno [18]. Sin embargo, se ha identificado una solución que implica la configuración interna de Claude Code para ajustar los tiempos de espera, en lugar de depender de soluciones externas [19]. Esto indica que las versiones más recientes de Claude Code (como la 2.1.101) han mejorado la flexibilidad en la configuración de los tiempos de espera [18].

### Reintentos y Resiliencia:

Aunque la información específica sobre los mecanismos de reintento automático en Claude Code v2.1 no es explícita en las fuentes consultadas, la capacidad de manejar fallos y tiempos de espera sugiere que la resiliencia es una consideración clave. En escenarios de sub-agentes paralelos, la implementación de estrategias de reintento con retroceso exponencial o circuitos de interrupción sería beneficiosa para mitigar fallos transitorios y mejorar la robustez del sistema.

### Referencias
[1] [Understand the SWE-Bench Leaderboard 2026 in Depth - CodeAnt AI](https://www.codeant.ai/blogs/swe-bench-scores)
[2] [From 80% to 93.9%: Why the Claude Mythos SWE-Bench Jump - Mindstudio AI](https://www.mindstudio.ai/blog/claude-mythos-benchmark-results-swe-bench-agentic-coding/)
[3] [SWE-bench Verified Benchmark 2026: 44 LLM scores | BenchLM.ai](https://benchlm.ai/benchmarks/sweVerified)
[4] [Claude Opus 4.7 Benchmarks Explained - Vellum](https://www.vellum.ai/blog/claude-opus-4-7-benchmarks-explained)
[5] [SWE-bench Leaderboards](https://www.swebench.com/)
[6] [Claude Code 2.1.0 Just Changed Everything, And Most Developers ... - Medium](https://medium.com/@cognidownunder/claude-code-2-1-0-just-changed-everything-and-most-developers-havent-noticed-yet-8862a3c961ed)
[7] [Introducing Claude Opus 4.7 - Anthropic](https://www.anthropic.com/news/claude-opus-4-7)
[8] [MCP Servers Tested: What Works With Claude Code - Medium](https://medium.com/@xcxwcqctcb/i-set-up-mcp-servers-so-you-dont-have-to-what-actually-works-with-claude-code-6bcaecddfc53)
[9] [Is there any difference between Claude Code and MCP ... - Reddit](https://www.reddit.com/r/ClaudeAI/comments/1kdffjt/is_there_any_difference_between_claude_code_and/)
[10] [Claude Code 🤝 FastMCP](https://gofastmcp.com/v2/integrations/claude-code)
[11] [Best MCP Servers for Claude Code - Truefoundry](https://www.truefoundry.com/blog/best-mcp-servers-for-claude-code)
[12] [Claude Code MCP Servers: How to Connect, Configure, ... - Builder.io](https://www.builder.io/blog/claude-code-mcp-servers)
[13] [Claude for Creative Work - Anthropic](https://www.anthropic.com/news/claude-for-creative-work)
[14] [install-claude.md - github-mcp-server](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-claude.md)
[15] [Remote MCP servers - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/remote-mcp-servers)
[16] [Claude Code Split-and-Merge Pattern: How Sub-Agents ... - Mindstudio AI](https://www.mindstudio.ai/blog/claude-code-split-and-merge-pattern-sub-agents/)
[17] [[BUG] · Issue #14867 · anthropics/claude-code](https://github.com/anthropics/claude-code/issues/14867)
[18] [Claude Code 2.1.101: Everything That Actually Changed - mejba.me](https://www.mejba.me/blog/claude-code-2-1-101-release)
[19] [[SOLUTION] Complete Claude Code Timeout ... - GitHub](https://github.com/anthropics/claude-code/issues/5615)
