# Biblia de Implementación: Hermes-Agent v0.12

**Fecha de Lanzamiento:** 2026.04.30
**Versión:** v0.12.0
**Arquitectura Principal:** Agente de IA auto-mejorable con bucle de aprendizaje, memoria curada, sistema de habilidades y soporte multiplataforma.

## 1. Visión General y Diferenciador Único

Hermes-Agent v0.12, desarrollado por Nous Research, se posiciona como un agente de IA auto-mejorable con un **bucle de aprendizaje interno** distintivo. A diferencia de otros agentes, Hermes-Agent está diseñado para crear y refinar sus propias habilidades a partir de la experiencia, persistir el conocimiento a través de "nudges" periódicos, y construir un modelo profundo del usuario a lo largo de múltiples sesiones. Su capacidad para buscar en conversaciones pasadas y resumir sesiones con LLMs (Large Language Models) le confiere una memoria contextual robusta. Este agente es agnóstico al modelo, permitiendo la integración con una amplia gama de LLMs y proveedores (Nous Portal, OpenRouter, NVIDIA NIM, Xiaomi MiMo, z.ai/GLM, Kimi/Moonshot, MiniMax, Hugging Face, OpenAI, entre otros), lo que elimina el bloqueo del proveedor y facilita la adaptabilidad. Su diseño permite la ejecución en diversas infraestructuras, desde un VPS de bajo costo hasta clústeres de GPU o entornos serverless, con una interfaz de terminal completa (TUI) y soporte para múltiples plataformas de mensajería (Telegram, Discord, Slack, WhatsApp, Signal, CLI).

## 2. Arquitectura Técnica

La arquitectura de Hermes-Agent se centra en la modularidad, la persistencia y la adaptabilidad. Los componentes clave incluyen:

*   **Bucle de Aprendizaje Interno:** El núcleo del agente, que orquesta la creación autónoma de habilidades, la mejora continua de estas durante su uso y la consolidación del conocimiento. Este bucle permite al agente evolucionar y adaptarse a nuevas tareas y contextos sin intervención manual constante.
*   **Sistema de Memoria Curada:** Implementa una memoria persistente a través de "nudges" periódicos que consolidan el conocimiento. Utiliza FTS5 (Full-Text Search) para la búsqueda en el historial de conversaciones y resúmenes generados por LLMs para la recuperación de información relevante entre sesiones. También incorpora el modelado de usuario dialéctico "Honcho" para una comprensión más profunda del usuario.
*   **Sistema de Habilidades (Skills System):** Compatible con el estándar abierto `agentskills.io`, permite al agente desarrollar y utilizar herramientas específicas para tareas. Las habilidades se crean de forma autónoma y se auto-mejoran con el tiempo. El agente puede acceder a un "Skills Hub" para gestionar y descubrir habilidades.
*   **Gestión de Modelos LLM:** A través del comando `hermes model`, el agente puede cambiar dinámicamente entre diferentes proveedores y modelos de LLM sin requerir cambios en el código base, lo que proporciona una gran flexibilidad y resiliencia ante la evolución de los modelos.
*   **Backends de Terminal y Despliegue:** Soporta seis backends de terminal (local, Docker, SSH, Daytona, Singularity y Modal), lo que permite una ejecución flexible. Los entornos serverless como Daytona y Modal ofrecen persistencia con hibernación cuando está inactivo, optimizando los costos.
*   **Delegación y Paralelización:** La arquitectura permite la creación de subagentes aislados para flujos de trabajo paralelos y la ejecución de scripts Python que invocan herramientas vía RPC (Remote Procedure Call), lo que facilita la descomposición de tareas complejas y la optimización del uso del contexto.
*   **Programador Cron Integrado:** Permite la automatización de tareas programadas con entrega a cualquier plataforma, como informes diarios o auditorías semanales, ejecutándose de forma desatendida.
*   **Integración MCP (Model Context Protocol):** Permite la conexión con servidores MCP externos para extender las capacidades del agente.

## 3. Implementación/Patrones Clave

La implementación de Hermes-Agent se basa en Python y utiliza `uv venv` para la gestión de dependencias, asegurando un entorno de ejecución consistente y aislado. Los patrones clave de implementación incluyen:

*   **Instalación y Configuración:** Se facilita mediante un script de instalación (`install.sh`) que maneja la configuración específica de la plataforma (Linux, macOS, WSL2, Android vía Termux). El comando `hermes setup` guía al usuario a través de una configuración completa, mientras que `hermes config set` permite ajustar valores individuales.
*   **Interfaz de Línea de Comandos (CLI) y Gateway de Mensajería:** El agente ofrece una TUI completa con edición multilínea, autocompletado de comandos, historial de conversaciones y salida de herramientas en streaming. Además, un proceso de gateway unificado permite la interacción a través de múltiples plataformas de mensajería, manteniendo la continuidad de la conversación.
*   **Migración de OpenClaw:** Se proporciona una funcionalidad de migración (`hermes claw migrate`) para usuarios que provienen de OpenClaw, permitiendo importar configuraciones, memorias, habilidades y claves API, lo que demuestra un enfoque en la interoperabilidad y la experiencia del usuario.
*   **Estructura de Directorios:** El repositorio de GitHub muestra una estructura modular con directorios como `agent`, `skills`, `tools`, `environments`, `gateway`, `hermes_cli`, entre otros, lo que sugiere una clara separación de responsabilidades y facilita el desarrollo y mantenimiento.
*   **RL Training:** Incluye capacidades para la generación de trayectorias por lotes, entornos RL de Atropos y compresión de trayectorias, lo que indica un enfoque en la investigación y el entrenamiento de modelos de llamada a herramientas de próxima generación.

## 4. Lecciones para el Monstruo

De la arquitectura y la implementación de Hermes-Agent, nuestro propio agente puede aprender varias lecciones valiosas:

*   **Bucle de Aprendizaje Continuo:** La implementación de un bucle de aprendizaje interno que permite la creación y mejora autónoma de habilidades es fundamental para la adaptabilidad y la evolución del agente. Esto reduce la necesidad de intervención humana para la adaptación a nuevas tareas.
*   **Memoria Contextual Robusta:** La combinación de memoria curada, "nudges" para la persistencia del conocimiento y búsqueda en el historial de conversaciones con resúmenes de LLMs es crucial para mantener un contexto rico y relevante a lo largo del tiempo y entre sesiones.
*   **Agnosticismo del Modelo LLM:** La capacidad de integrar y cambiar entre diversos modelos y proveedores de LLM sin cambios en el código base es una ventaja estratégica. Esto proporciona flexibilidad, resiliencia y evita el bloqueo tecnológico.
*   **Modularidad y Estándares Abiertos:** La adhesión a estándares abiertos como `agentskills.io` y una estructura modular facilita la extensibilidad, la colaboración y la integración con el ecosistema de herramientas de IA.
*   **Soporte Multiplataforma y Despliegue Flexible:** Ofrecer una experiencia consistente a través de múltiples plataformas (CLI, mensajería) y backends de despliegue (local, Docker, serverless) amplía el alcance y la utilidad del agente, permitiendo su uso en diversos escenarios y con diferentes requisitos de recursos.
*   **Automatización y Paralelización:** La capacidad de delegar tareas a subagentes y ejecutar scripts vía RPC para paralelizar el trabajo es esencial para manejar la complejidad y mejorar la eficiencia en la ejecución de tareas.

---
*Referencias:*
[1] NousResearch/hermes-agent GitHub Repository: [https://github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
[2] Hermes Agent Official Documentation: [https://hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs)
[3] Hermes Agent v0.12.0 Release: [https://github.com/NousResearch/hermes-agent/releases/tag/v0.12.0](https://github.com/NousResearch/hermes-agent/releases/tag/v0.12.0)

---

# Biblia de Implementación: Hermes-Agent v0.12 (NousResearch) — Fase 2

# MÓDULO A: Ciclo del agente (loop/ReAct)

El motor de orquestación principal del Hermes Agent es la clase `AIAgent` en `run_agent.py`. Esta clase, que abarca aproximadamente 13,700 líneas de código, gestiona desde el ensamblaje de prompts hasta el despacho de herramientas y la conmutación por error del proveedor [1].

## Responsabilidades Principales de `AIAgent`

La clase `AIAgent` es responsable de varias funciones críticas dentro del ciclo del agente [1]:

*   **Ensamblaje de Prompts y Esquemas de Herramientas**: Construye el prompt del sistema efectivo y los esquemas de herramientas utilizando `prompt_builder.py`.
*   **Selección del Modo de Proveedor/API**: Elige el proveedor y modo de API correctos, como `chat_completions`, `codex_responses` o `anthropic_messages`.
*   **Llamadas al Modelo Interrumpibles**: Realiza llamadas al modelo que pueden ser canceladas, con soporte para interrupciones.
*   **Ejecución de Llamadas a Herramientas**: Ejecuta llamadas a herramientas, ya sea de forma secuencial o concurrente a través de un pool de hilos.
*   **Mantenimiento del Historial de Conversaciones**: Gestiona el historial de conversaciones en formato de mensaje de OpenAI.
*   **Manejo de Compresión, Reintentos y Fallback**: Se encarga de la compresión del contexto, los reintentos en caso de fallos y la conmutación a modelos de fallback.
*   **Seguimiento de Presupuestos de Iteración**: Controla los presupuestos de iteración tanto para el agente principal como para los subagentes.
*   **Vaciado de Memoria Persistente**: Asegura que la memoria persistente se vacíe antes de que el contexto se pierda.

## Llamadas a la API Interrumpibles

El `AIAgent` realiza llamadas a la API interrumpibles (`_interruptible_api_call`) que ejecutan la llamada HTTP real en un hilo en segundo plano mientras monitorean un evento de interrupción. El hilo principal espera la respuesta, un evento de interrupción o un tiempo de espera [1].

```
┌────────────────────────────────────────────────────┐
│  Hilo principal               Hilo de la API       │
│                                                    │
│   espera en:                  POST HTTP            │
│    - respuesta lista    ───▶   al proveedor        │
│    - evento de interrupción                        │
│    - tiempo de espera                              │
└────────────────────────────────────────────────────┘
```

Cuando se interrumpe (por ejemplo, el usuario envía un nuevo mensaje, un comando `/stop` o una señal) [1]:

*   El hilo de la API se abandona y la respuesta se descarta.
*   El agente puede procesar la nueva entrada o apagarse limpiamente.
*   No se inyecta ninguna respuesta parcial en el historial de la conversación.

## Ejecución de Herramientas

Cuando el modelo devuelve llamadas a herramientas, el Hermes Agent las maneja de la siguiente manera [1]:

*   **Una sola llamada a herramienta**: Se ejecuta directamente en el hilo principal.
*   **Múltiples llamadas a herramientas**: Se ejecutan concurrentemente a través de `ThreadPoolExecutor`.
    *   **Excepción**: Las herramientas marcadas como interactivas (por ejemplo, `clarify`) fuerzan la ejecución secuencial.
    *   Los resultados se reinsertan en el orden original de la llamada a la herramienta, independientemente del orden de finalización.

El proceso de ejecución de cada llamada a herramienta implica [1]:

1.  **Resolución del Handler**: Se resuelve el handler de `tools/registry.py`.
2.  **Hook de Plugin `pre_tool_call`**: Se dispara el hook de plugin `pre_tool_call`.
3.  **Verificación de Comando Peligroso**: Se verifica si es un comando peligroso (`tools/approval.py`). Si es peligroso, se invoca `approval_callback` y se espera la aprobación del usuario.
4.  **Ejecución del Handler**: Se ejecuta el handler con los argumentos y el `task_id`.
5.  **Hook de Plugin `post_tool_call`**: Se dispara el hook de plugin `post_tool_call`.
6.  **Adjuntar Resultado al Historial**: Se añade `{"role": "tool", "content": result}` al historial.

Algunas herramientas son interceptadas por `run_agent.py` *antes* de llegar a `handle_function_call()` porque modifican directamente el estado del agente y devuelven resultados de herramientas sintéticos sin pasar por el registro [1]:

| Herramienta | Razón de Interceptación |
| --- | --- |
| `todo` | Lee/escribe el estado de la tarea local del agente |
| `memory` | Escribe en archivos de memoria persistente con límites de caracteres |
| `session_search` | Consulta el historial de la sesión a través de la base de datos de sesión del agente |
| `delegate_task` | Genera subagentes con contexto aislado |

## Callbacks y Presupuesto de Iteración

El `AIAgent` soporta callbacks específicos de la plataforma para el progreso en tiempo real en la CLI, gateway e integraciones ACP [1]:

| Callback | Cuándo se dispara | Utilizado por |
| --- | --- | --- |
| `tool_progress_callback` | Antes/después de cada ejecución de herramienta | Spinner de CLI, mensajes de progreso de gateway |
| `thinking_callback` | Cuando el modelo comienza/detiene el pensamiento | Indicador "thinking..." de CLI |
| `reasoning_callback` | Cuando el modelo devuelve contenido de razonamiento | Visualización de razonamiento de CLI, bloques de razonamiento de gateway |
| `clarify_callback` | Cuando se llama a la herramienta `clarify` | Prompt de entrada de CLI, mensaje interactivo de gateway |
| `step_callback` | Después de cada turno completo del agente | Seguimiento de pasos de gateway, progreso de ACP |
| `stream_delta_callback` | Cada token de streaming (cuando está habilitado) | Visualización de streaming de CLI |
| `tool_gen_callback` | Cuando se analiza la llamada a la herramienta desde el stream | Vista previa de la herramienta de CLI en el spinner |
| `status_callback` | Cambios de estado (pensando, ejecutando, etc.) | Actualizaciones de estado de ACP |

El agente rastrea las iteraciones a través de `IterationBudget` [1]:

*   **Por defecto**: 90 iteraciones (configurable a través de `agent.max_turns`).
*   Cada agente tiene su propio presupuesto. Los subagentes tienen presupuestos independientes limitados por `delegation.max_iterations` (por defecto 50). El total de iteraciones entre el padre y los subagentes puede exceder el límite del padre.
*   Al 100%, el agente se detiene y devuelve un resumen del trabajo realizado.

## Fallback y Compresión del Contexto

Cuando el modelo primario falla (por ejemplo, límite de tasa 429, error de servidor 5xx, error de autenticación 401/403), el sistema de fallback entra en acción [1]:

1.  Verifica la lista `fallback_providers` en la configuración.
2.  Intenta con cada fallback en orden.
3.  Si tiene éxito, continúa la conversación con el nuevo proveedor.
4.  En caso de 401/403, intenta actualizar las credenciales antes de fallar.

El sistema de fallback también cubre tareas auxiliares de forma independiente (visión, compresión, extracción web y búsqueda de sesión), cada una con su propia cadena de fallback configurable a través de la sección de configuración `auxiliary.*` [1].

La compresión del contexto se activa en los siguientes escenarios [1]:

*   **Preflight (antes de la llamada a la API)**: Si la conversación excede el 50% de la ventana de contexto del modelo.
*   **Autocompresión del Gateway**: Si la conversación excede el 85% (más agresiva, se ejecuta entre turnos).

Durante la compresión [1]:

1.  La memoria se vacía primero al disco para evitar la pérdida de datos.
2.  Los turnos intermedios de la conversación se resumen en un resumen compacto.
3.  Los últimos N mensajes se conservan intactos (`compression.protect_last_n`, por defecto: 20).
4.  Los pares de mensajes de llamada/resultado de herramientas se mantienen juntos (never se dividen).
5.  Se genera un nuevo ID de linaje de sesión (la compresión crea una sesión "hija").

## Referencias

[1] Agent Loop Internals | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/developer-guide/agent-loop](https://hermes-agent.nousresearch.com/docs/developer-guide/agent-loop)

# MÓDULO B: Estados del agente

El Hermes Agent, desarrollado por Nous Research, opera a través de un ciclo de aprendizaje incorporado que le permite crear y refinar habilidades a partir de la experiencia. Este proceso implica una serie de estados y transiciones que definen su comportamiento y evolución. La arquitectura del agente se puede entender a través de un "bucle de agente" central y un "sistema de memoria multicapa" [1].

## Estados Principales del Agente

El flujo de trabajo del Hermes Agent se puede desglosar en los siguientes estados clave, que se activan en respuesta a la interacción del usuario y las necesidades internas del agente [1]:

1.  **Estado Inicial (YOU SEND A MESSAGE)**:
    *   **Descripción**: El agente se encuentra en un estado de espera, listo para recibir una nueva entrada o comando del usuario. Este es el punto de partida para cualquier interacción.
    *   **Transición a**: `Performing Task` cuando el usuario envía un mensaje.

2.  **Realizando Tarea (AGENT PERFORMS TASK)**:
    *   **Descripción**: Una vez que el agente recibe una solicitud, entra en este estado para procesarla. Esto implica una combinación de llamadas a modelos de lenguaje grandes (LLM), uso de herramientas y un razonamiento de múltiples pasos para lograr el objetivo de la tarea.
    *   **Transición a**: `Knowledge Extraction` después de completar la tarea.

3.  **Extracción de Conocimiento (KNOWLEDGE EXTRACTION)**:
    *   **Descripción**: Tras la ejecución de una tarea, el agente evalúa si la complejidad y la naturaleza de la misma justifican la creación de una nueva habilidad reutilizable. Este es un paso crítico en el ciclo de auto-mejora.
    *   **Transición a**: `Skill Creation` si la tarea es lo suficientemente compleja para una nueva habilidad, o `Memory Update` si contribuye a la memoria existente sin formar una nueva habilidad.

4.  **Creación de Habilidad (SKILL CREATED)**:
    *   **Descripción**: Si la fase de extracción de conocimiento determina que se debe crear una nueva habilidad, el agente entra en este estado. Aquí, los pasos de la tarea se documentan, las herramientas utilizadas se registran y la estrategia se captura, guardándose como un archivo de habilidad en formato `.md`.
    *   **Transición a**: `Stored State` para integrar la nueva habilidad en la base de conocimiento persistente del agente.

5.  **Actualización de Memoria (MEMORY UPDATED)**:
    *   **Descripción**: En este estado, los hechos y preferencias relevantes de la tarea completada se almacenan y se escriben en los archivos `MEMORY.md` y `USER.md`. Al finalizar la sesión, la memoria se archiva en una base de datos SQLite.
    *   **Transición a**: `Stored State` para asegurar la persistencia de la memoria actualizada.

6.  **Estado Almacenado (STORED STATE)**:
    *   **Descripción**: Este estado representa la base de conocimiento persistente del agente. Incluye la biblioteca de habilidades, los archivos `MEMORY.md` y `USER.md`, y el archivo de sesión en SQLite. Es el repositorio de todo lo que el agente ha aprendido y experimentado.
    *   **Transición a**: `Next Session Starts` cuando se inicia una nueva sesión.

7.  **Inicio de Próxima Sesión (NEXT SESSION STARTS)**:
    *   **Descripción**: Al comienzo de una nueva sesión, el agente carga las habilidades relevantes, inyecta la memoria en el contexto actual, recupera recuerdos pasados mediante una búsqueda FTS5 y reutiliza prefijos en caché para optimizar el rendimiento.
    *   **Transición a**: `Skills Reused & Refined` si una tarea coincide con una habilidad existente, o de vuelta a `Performing Task` para nuevas solicitudes.

8.  **Habilidades Reutilizadas y Refinadas (SKILLS REUSED & REFINED)**:
    *   **Descripción**: Si una tarea entrante puede ser manejada por una habilidad existente, el agente entra en este estado. La habilidad se ejecuta y se mejora basándose en el resultado de su aplicación, contribuyendo al ciclo de auto-mejora.
    *   **Transición a**: `Continuous Loop` para continuar el proceso de aprendizaje y ejecución.

9.  **Bucle Continuo (CONTINUOUS LOOP)**:
    *   **Descripción**: Este es el estado general que abarca la ejecución reactiva y el crecimiento compuesto de la inteligencia del sistema. Representa el ciclo ininterrumpido de aprendizaje, adaptación y mejora del agente.
    *   **Transición a**: `Performing Task` para abordar nuevas solicitudes o continuar con tareas en curso.

## Rítmos Operacionales (Sub-estados)

Dentro del estado `Performing Task`, el Hermes Agent puede operar en diferentes ritmos, que pueden considerarse sub-estados o modos de operación, adaptándose a la naturaleza de la tarea [1]:

*   **Ritmo Interactivo (Interactive Rhythm)**:
    *   **Descripción**: Este es el bucle de retroalimentación en tiempo real que los usuarios experimentan directamente. El agente procesa comandos y genera respuestas de manera inmediata, manteniendo un contexto persistente para manejar tareas complejas de múltiples pasos sin perder el hilo. La máquina de estados asegura que el agente recuerde el contexto actual de la interacción.

*   **Ritmo por Lotes (Batch Rhythm)**:
    *   **Descripción**: Se utiliza cuando se necesita realizar una gran cantidad de trabajo de una sola vez y el usuario está dispuesto a esperar. Durante este ritmo, el agente puede trabajar en paralelo, generando múltiples componentes o completando fases extensas de una tarea de forma simultánea.

*   **Ritmo en Segundo Plano (Background Rhythm)**:
    *   **Descripción**: Este ritmo opera de forma menos visible, pero es crucial para el mantenimiento a largo plazo del agente. Incluye tareas como resumir sesiones completadas para consolidar la memoria, asegurando que el agente se mantenga eficiente y relevante a lo largo del tiempo sin sobrecargar su contexto activo.

## Transiciones entre Estados

Las transiciones entre estos estados son impulsadas por eventos, ya sean externos (entrada del usuario) o internos (evaluación de tareas, finalización de procesos). La capacidad del agente para moverse fluidamente entre estos estados es fundamental para su naturaleza auto-mejorada y su capacidad para manejar tareas complejas y persistir el conocimiento a lo largo del tiempo [1].

## Referencias

[1] Raghunaathan. (2026, April 19). Understanding The Hermes Agent Through D&D. *Towards AI*. Recuperado de [https://pub.towardsai.net/understanding-the-hermes-agent-through-d-d-0f7db2d53d77](https://pub.towardsai.net/understanding-the-hermes-agent-through-d-d-0f7db2d53d77)

# MÓDULO C: Sistema de herramientas

El Hermes Agent cuenta con un robusto sistema de herramientas que le permite interactuar con el entorno, ejecutar código, navegar por la web y gestionar tareas complejas. El registro de herramientas de Hermes documenta 68 herramientas integradas, agrupadas por conjuntos de herramientas (toolsets). La disponibilidad de estas herramientas varía según la plataforma, las credenciales y los conjuntos de herramientas habilitados [1].

## Resumen de Herramientas Integradas

El sistema de herramientas de Hermes incluye una amplia gama de funcionalidades, con un desglose aproximado de las herramientas principales [1]:

*   **Herramientas de Navegador (core)**: 10 herramientas.
*   **Herramientas de Navegador (CDP)**: 2 herramientas (requieren un endpoint del Protocolo de Herramientas de Desarrollo de Chrome).
*   **Herramientas de Archivos**: 4 herramientas.
*   **Herramientas de RL (Reinforcement Learning)**: 10 herramientas.
*   **Herramientas de Home Assistant**: 4 herramientas.
*   **Herramientas de Terminal**: 2 herramientas.
*   **Herramientas Web**: 2 herramientas.
*   **Herramientas de Feishu**: 5 herramientas.
*   **Herramientas de Spotify**: 7 herramientas.
*   **Herramientas de Yuanbao**: 5 herramientas.
*   **Herramientas de Discord**: 2 herramientas.
*   **Herramientas Standalone**: 15 herramientas adicionales distribuidas en otros conjuntos.

## Herramientas MCP (Model Context Protocol)

Además de las herramientas integradas, Hermes puede cargar herramientas dinámicamente desde servidores MCP. Las herramientas MCP aparecen con un prefijo de nombre de servidor (por ejemplo, `github_create_issue` para el servidor MCP de GitHub) [1].

## Conjuntos de Herramientas Detallados

A continuación, se presenta una descripción detallada de algunos de los conjuntos de herramientas más relevantes [1]:

### Toolset: `browser`

Este conjunto de herramientas permite la interacción con un navegador web. Requiere que `browser_navigate` se haya llamado primero para inicializar la sesión.

| Herramienta | Descripción |
| --- | --- |
| `browser_back` | Navega a la página anterior en el historial del navegador. |
| `browser_click` | Simula un clic en un elemento interactivo de la página, identificado por su ID de referencia (`@eX`) obtenido de un `browser_snapshot`. |
| `browser_console` | Obtiene la salida de la consola del navegador y los errores de JavaScript, útil para depuración y detección de problemas en la página. |
| `browser_get_images` | Lista todas las imágenes presentes en la página actual, incluyendo sus URLs y texto alternativo, lo que puede ser útil para el análisis con herramientas de visión. |
| `browser_navigate` | Navega a una URL específica. Esta herramienta es fundamental para iniciar cualquier sesión de navegación y debe ser la primera en ser invocada. Para tareas de recuperación de información más simples y eficientes, se recomienda `web_search` o `web_extract`. |
| `browser_press` | Simula la pulsación de una tecla del teclado, permitiendo acciones como enviar formularios (Enter), navegar (Tab) o ejecutar atajos de teclado. |
| `browser_scroll` | Desplaza la página en una dirección específica (arriba, abajo, izquierda, derecha), lo que permite revelar contenido que no está visible en el viewport actual. |
| `browser_snapshot` | Genera una representación textual del árbol de accesibilidad de la página actual. Devuelve elementos interactivos con IDs de referencia (ej. `@e1`, `@e2`) que pueden ser utilizados por `browser_click` y `browser_type`. Puede generar una vista compacta (`full=false`, por defecto) o una vista completa (`full=true`). |
| `browser_type` | Escribe texto en un campo de entrada editable, identificado por su ID de referencia. Primero borra el contenido existente y luego inserta el nuevo texto. |
| `browser_vision` | Captura una captura de pantalla de la página y la analiza utilizando IA de visión. Esta herramienta es útil para escenarios complejos como CAPTCHAs, verificaciones visuales, diseños intrincados o cuando el `browser_snapshot` textual es insuficiente. |

### Toolset: `browser-cdp`

Este conjunto de herramientas se activa solo cuando un endpoint del Protocolo de Herramientas de Desarrollo de Chrome (CDP) está disponible al inicio de la sesión. Esto puede configurarse a través de `/browser connect`, la configuración `browser.cdp_url`, o mediante sesiones de Browserbase o Camofox [1].

| Herramienta | Descripción |
| --- | --- |
| `browser_cdp` | Permite enviar comandos raw del Protocolo de Herramientas de Desarrollo de Chrome. Actúa como una vía de escape para realizar operaciones del navegador que no están cubiertas por las herramientas `browser_*` de nivel superior. |
| `browser_dialog` | Responde a diálogos nativos de JavaScript (alert, confirm, prompt, beforeunload). Para usarla, primero se debe llamar a `browser_snapshot`, ya que los diálogos pendientes aparecen en su campo `pending_dialogs`. Luego se invoca `browser_dialog` con la acción deseada (`action=\'accept\'|\'dismiss\'`). |

### Toolset: `clarify`

| Herramienta | Descripción |
| --- | --- |
| `clarify` | Hace una pregunta al usuario cuando se necesita aclaración, retroalimentación o una decisión antes de continuar. Soporta dos modos: 1. **Opción múltiple**: proporciona hasta 4 opciones. El usuario elige una o escribe su propia respuesta a través de una 5ª opción \'Otro\'. 2. **Pregunta abierta**: el usuario proporciona una respuesta de texto libre. |

### Toolset: `code_execution`

| Herramienta | Descripción |
| --- | --- |
| `execute_code` | Ejecuta un script de Python que puede llamar programáticamente a las herramientas de Hermes. Útil cuando se necesitan 3 o más llamadas a herramientas con lógica de procesamiento entre ellas, se necesita filtrar/reducir grandes salidas de herramientas antes de que entren en el contexto, o se necesita ramificación condicional. |

### Toolset: `cronjob`

| Herramienta | Descripción |
| --- | --- |
| `cronjob` | Gestor unificado de tareas programadas. Permite `action=\'create\'`, `\'list\'`, `\'update\'`, `\'pause\'`, `\'resume\'`, `\'run\'` o `\'remove\'` para gestionar trabajos. Soporta trabajos respaldados por habilidades con una o más habilidades adjuntas, y `skills=[]` en la actualización borra las habilidades adjuntas. Las ejecuciones de Cron ocurren en sesiones nuevas sin contexto de chat actual. |

### Toolset: `delegation`

| Herramienta | Descripción |
| --- | --- |
| `delegate_task` | Genera uno o más subagentes para trabajar en tareas en contextos aislados. Cada subagente obtiene su propia conversación, sesión de terminal y conjunto de herramientas. Solo se devuelve el resumen final; los resultados de herramientas intermedios nunca entran en la ventana de contexto. |

### Toolset: `feishu_doc`

Este conjunto de herramientas está limitado al manejador de respuesta inteligente de comentarios de documentos de Feishu (`gateway/platforms/feishu_comment.py`). No se expone en `hermes-cli` ni en el adaptador de chat regular de Feishu [1].

| Herramienta | Descripción |
| --- | --- |
| `feishu_doc_read` | Lee el contenido de texto completo de un documento de Feishu/Lark (Docx, Doc o Sheet) dado su `file_type` y `token`. | Credenciales de la aplicación Feishu |

### Toolset: `feishu_drive`

Este conjunto de herramientas está diseñado para operaciones de lectura/escritura de comentarios en archivos de Feishu Drive [1].

| Herramienta | Descripción |
| --- | --- |
| `feishu_drive_add_comment` | Agrega un comentario de nivel superior en un documento o archivo de Feishu/Lark. | Credenciales de la aplicación Feishu |
| `feishu_drive_list_comments` | Lista los comentarios de documentos completos en un archivo de Feishu/Lark, los más recientes primero. | Credenciales de la aplicación Feishu |
| `feishu_drive_list_comment_replies` | Lista las respuestas en un hilo de comentarios específico de Feishu (documento completo o selección local). | Credenciales de la aplicación Feishu |
| `feishu_drive_reply_comment` | Publica una respuesta en un hilo de comentarios de Feishu, con mención `@` opcional. | Credenciales de la aplicación Feishu |

### Toolset: `file`

| Herramienta | Descripción |
| --- | --- |
| `patch` | Ediciones de buscar y reemplazar dirigidas en archivos. Utiliza coincidencia difusa (9 estrategias) para que las diferencias menores de espacios en blanco/indentación no lo rompan. Devuelve un diff unificado. Ejecuta automáticamente comprobaciones de sintaxis después de la edición. |
| `read_file` | Lee un archivo de texto con números de línea y paginación. El formato de salida es `LINE_NUM|CONTENIDO`. Sugiere nombres de archivo similares si no se encuentra. Utiliza `offset` y `limit` para archivos grandes. **NOTA**: No puede leer imágenes o archivos binarios. |
| `search_files` | Busca contenido de archivos o encuentra archivos por nombre. Respaldado por Ripgrep, más rápido que los equivalentes de shell. Búsqueda de contenido (`target=\'content\'`) : búsqueda de expresiones regulares dentro de archivos. Modos de salida: coincidencias completas con números de línea, o solo nombres de archivo. |
| `write_file` | Escribe contenido en un archivo, reemplazando completamente el contenido existente. Crea directorios padre automáticamente. **SOBREESCRIBE** todo el archivo; utiliza `patch` para ediciones dirigidas. |

### Toolset: `homeassistant`

| Herramienta | Descripción |
| --- | --- |
| `ha_call_service` | Llama a un servicio de Home Assistant para controlar un dispositivo. Utiliza `ha_list_services` para descubrir los servicios disponibles y sus parámetros para cada dominio. |
| `ha_get_state` | Obtiene el estado detallado de una sola entidad de Home Assistant, incluyendo todos los atributos (brillo, color, punto de ajuste de temperatura, lecturas de sensores, etc.). |
| `ha_list_entities` | Lista las entidades de Home Assistant. Opcionalmente filtra por dominio (light, switch, climate, sensor, binary_sensor, cover, fan, etc.) o por nombre de área (living room, kitchen, bedroom, etc.). |
| `ha_list_services` | Lista los servicios (acciones) disponibles de Home Assistant para el control de dispositivos. Muestra qué acciones se pueden realizar en cada tipo de dispositivo y qué parámetros aceptan. |

### Toolset: `image_gen`

| Herramienta | Descripción |
| --- | --- |
| `image_generate` | Genera imágenes de alta calidad a partir de prompts de texto utilizando FAL.ai. El modelo subyacente se configura por el usuario (por defecto: FLUX 2 Klein 9B, generación en menos de 1 segundo) y no es seleccionable por el agente. Devuelve una única URL de imagen. | `FAL_KEY` |

### Toolset: `memory`

| Herramienta | Descripción |
| --- | --- |
| `memory` | Guarda información importante en la memoria persistente que sobrevive a través de las sesiones. Tu memoria aparece en tu prompt del sistema al inicio de la sesión; así es como recuerdas cosas sobre el usuario y tu entorno entre conversaciones. |

### Toolset: `messaging`

| Herramienta | Descripción |
| --- | --- |
| `send_message` | Envía un mensaje a una plataforma de mensajería conectada, o lista los objetivos disponibles. **IMPORTANTE**: Cuando el usuario pide enviar a un canal o persona específica (no solo un nombre de plataforma), llama a `send_message(action=\'list\')` PRIMERO para ver los objetivos disponibles. |

### Toolset: `moa`

| Herramienta | Descripción |
| --- | --- |
| `mixture_of_agents` | Dirige un problema difícil a través de múltiples LLMs de frontera de forma colaborativa. Realiza 5 llamadas a la API (4 modelos de referencia + 1 agregador) con el máximo esfuerzo de razonamiento; úsalo con moderación para problemas genuinamente difíciles. Ideal para: matemáticas complejas, algoritmos avanzados, etc. | `OPENROUTER_API_KEY` |

### Toolset: `rl`

Este conjunto de herramientas está diseñado para la gestión de entornos de Reinforcement Learning (RL) [1].

| Herramienta | Descripción |
| --- | --- |
| `rl_check_status` | Obtiene el estado y las métricas de una ejecución de entrenamiento. **LIMITADO POR TASA**: impone un mínimo de 30 minutos entre comprobaciones para la misma ejecución. Devuelve métricas de WandB: `step`, `state`, `reward_mean`, `loss`, `percent_correct`. | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_edit_config` | Actualiza un campo de configuración. Utiliza `rl_get_current_config()` primero para ver todos los campos disponibles para el entorno seleccionado. Cada entorno tiene diferentes opciones configurables. | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_get_current_config` | Obtiene la configuración actual del entorno. Devuelve solo los campos que se pueden modificar: `group_size`, `max_token_length`, `total_steps`, `steps_per_eval`, `use_wandb`, `wandb_name`, `max_num_workers`. | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_get_results` | Obtiene los resultados finales y las métricas de una ejecución de entrenamiento completada. Devuelve las métricas finales y la ruta a los pesos entrenados. | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_list_runs` | Lista todas las ejecuciones de entrenamiento (activas y completadas) con su estado. | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_select_environment` | Selecciona un entorno de RL para el entrenamiento. Carga la configuración predeterminada del entorno. Después de seleccionar, utiliza `rl_get_current_config()` para ver la configuración y `rl_edit_config()` para modificarlos. | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_start_training` | Inicia una nueva ejecución de entrenamiento de RL con el entorno y la configuración actuales. La mayoría de los parámetros de entrenamiento (`lora_rank`, `learning_rate`, etc.) son fijos. Utiliza `rl_edit_config()` para establecer `group_size`, `batch_size`, `wandb_project` antes de comenzar. **ADVERTENCIA**: El entrenamiento puede ser costoso. | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_stop_training` | Detiene un trabajo de entrenamiento en ejecución. Útil si las métricas no son buenas, el entrenamiento está estancado o se quieren probar diferentes configuraciones. | `TINKER_API_KEY`, `WANDB_API_KEY` |
| `rl_test_inference` | Prueba rápida de inferencia para cualquier entorno. Ejecuta algunos pasos de inferencia + puntuación utilizando OpenRouter. Por defecto: 3 pasos x 16 finalizaciones = 48 rollouts por modelo, probando 3 modelos = 144 en total. Prueba la carga del entorno, la construcción del prompt, la inferencia. | `TINKER_API_KEY`, `WANDB_API_KEY` |

### Toolset: `session_search`

| Herramienta | Descripción |
| --- | --- |
| `session_search` | Busca en la memoria a largo plazo de conversaciones pasadas. Esta es tu capacidad de recordar; cada sesión pasada es searchable, y esta herramienta resume lo que sucedió. **ÚSALA PROACTIVAMENTE cuando**: - El usuario dice \'ya hicimos esto antes\', \'recuerdas cuando\', \'la última vez\'. - Necesitas recordar un hecho de una conversación anterior. - Necesitas recordar un skill que creaste antes. |

### Toolset: `skills`

| Herramienta | Descripción |
| --- | --- |
| `skill_manage` | Gestiona habilidades (crear, actualizar, eliminar). Las habilidades son tu memoria procedimental: enfoques reutilizables para tipos de tareas recurrentes. Las nuevas habilidades van a `~/.hermes/skills/`; las habilidades existentes se pueden modificar dondequiera que residan. Acciones: `create` (SKILL.md completo), `update` (parámetros específicos), `delete` (por nombre). |
| `skill_view` | Permite cargar información sobre tareas y flujos de trabajo específicos, así como scripts y plantillas. Carga el contenido completo de una habilidad o accede a sus archivos vinculados (referencias, plantillas, scripts). La primera llamada devuelve el contenido de SKILL.md más una lista de archivos vinculados. |
| `skills_list` | Lista las habilidades disponibles (nombre + descripción). Utiliza `skill_view(name)` para cargar el contenido completo. |

### Toolset: `terminal`

| Herramienta | Descripción |
| --- | --- |
| `process` | Gestiona procesos en segundo plano iniciados con `terminal(background=true)`. Acciones: `list` (mostrar todos), `poll` (verificar estado + nueva salida), `log` (salida completa con paginación), `wait` (bloquear hasta que termine o tiempo de espera), `kill` (terminar proceso). |
| `terminal` | Ejecuta un comando de shell en un entorno de terminal. Por defecto, se ejecuta en primer plano y bloquea hasta que se completa. Utiliza `background=true` para ejecutar en segundo plano y obtener un `process_id` para gestionar con la herramienta `process`. |

### Toolset: `todo`

| Herramienta | Descripción |
| --- | --- |
| `todo` | Gestiona una lista de tareas pendientes. Acciones: `add`, `list`, `complete`, `clear`. Las tareas se almacenan en `~/.hermes/todo.md`. |

### Toolset: `vision`

| Herramienta | Descripción |
| --- | --- |
| `vision` | Analiza una imagen con IA de visión. Proporciona una URL de imagen o un archivo local. Devuelve una descripción de la imagen. | `VISION_API_KEY` |

### Toolset: `web`

| Herramienta | Descripción |
| --- | --- |
| `web_extract` | Extrae el contenido principal de una página web (artículo, blog, etc.) y lo devuelve como texto limpio. Utiliza `web_search` primero para encontrar la URL. |
| `web_search` | Realiza una búsqueda web utilizando la API de Perplexity. Devuelve una lista de resultados de búsqueda con títulos, URLs y snippets. | `PERPLEXITY_API_KEY` |

### Toolset: `tts` (Text-to-Speech)

| Herramienta | Descripción |
| --- | --- |
| `tts` | Convierte texto en voz utilizando la API de ElevenLabs. Devuelve una URL al archivo de audio generado. | `ELEVENLABS_API_KEY` |

### Toolset: `discord`

| Herramienta | Descripción |
| --- | --- |
| `discord_send_message` | Envía un mensaje a un canal de Discord. Requiere `discord_channel_id`. | `DISCORD_BOT_TOKEN` |
| `discord_list_channels` | Lista los canales de Discord disponibles para el bot. | `DISCORD_BOT_TOKEN` |

### Toolset: `discord_admin`

| Herramienta | Descripción |
| --- | --- |
| `discord_kick_member` | Expulsa a un miembro de un servidor de Discord. Requiere `discord_guild_id` y `discord_user_id`. | `DISCORD_BOT_TOKEN` |
| `discord_ban_member` | Banea a un miembro de un servidor de Discord. Requiere `discord_guild_id` y `discord_user_id`. | `DISCORD_BOT_TOKEN` |

### Toolset: `spotify`

| Herramienta | Descripción |
| --- | --- |
| `spotify_play` | Reproduce una canción, álbum o lista de reproducción en Spotify. Requiere `spotify_uri`. | `SPOTIFY_ACCESS_TOKEN` |
| `spotify_pause` | Pausa la reproducción actual de Spotify. | `SPOTIFY_ACCESS_TOKEN` |
| `spotify_resume` | Reanuda la reproducción de Spotify. | `SPOTIFY_ACCESS_TOKEN` |
| `spotify_skip_next` | Salta a la siguiente canción en la cola de Spotify. | `SPOTIFY_ACCESS_TOKEN` |
| `spotify_skip_previous` | Vuelve a la canción anterior en la cola de Spotify. | `SPOTIFY_ACCESS_TOKEN` |
| `spotify_volume` | Ajusta el volumen de Spotify. Requiere `volume_percent` (0-100). | `SPOTIFY_ACCESS_TOKEN` |
| `spotify_search` | Busca canciones, artistas, álbumes o listas de reproducción en Spotify. | `SPOTIFY_ACCESS_TOKEN` |

### Toolset: `hermes-yuanbao`

| Herramienta | Descripción |
| --- | --- |
| `yuanbao_get_balance` | Obtiene el saldo actual de la cuenta de Yuanbao. | `YUANBAO_API_KEY` |
| `yuanbao_send_payment` | Envía un pago a otra cuenta de Yuanbao. Requiere `recipient_id` y `amount`. | `YUANBAO_API_KEY` |
| `yuanbao_list_transactions` | Lista las transacciones recientes de Yuanbao. | `YUANBAO_API_KEY` |
| `yuanbao_create_invoice` | Crea una factura de Yuanbao. Requiere `amount` y `description`. | `YUANBAO_API_KEY` |
| `yuanbao_pay_invoice` | Paga una factura de Yuanbao. Requiere `invoice_id`. | `YUANBAO_API_KEY` |

## Referencias

[1] Built-in Tools Reference | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/reference/tools-reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference)

# MÓDULO D: Ejecución de código

El Hermes Agent facilita la ejecución de código a través de la herramienta `execute_code`, que permite al agente escribir scripts de Python para llamar programáticamente a otras herramientas de Hermes. Esto consolida flujos de trabajo de múltiples pasos en un solo turno del LLM [1].

## Cómo Funciona la Ejecución de Código

El proceso de ejecución de código en Hermes Agent sigue los siguientes pasos [1]:

1.  **Escritura del Script**: El agente escribe un script de Python utilizando `from hermes_tools import ...` para importar las herramientas necesarias.
2.  **Generación del Módulo Stub**: Hermes genera un módulo stub `hermes_tools.py` con funciones RPC.
3.  **Comunicación RPC**: Hermes abre un socket de dominio Unix e inicia un hilo de escucha RPC.
4.  **Ejecución en Proceso Hijo**: El script se ejecuta en un proceso hijo, y las llamadas a herramientas viajan a través del socket de vuelta a Hermes.
5.  **Retorno de Salida**: Solo la salida `print()` del script se devuelve al LLM; los resultados de herramientas intermedias nunca entran en la ventana de contexto.

## Lenguajes y Entorno

*   **Lenguaje**: El lenguaje principal para la ejecución de código programático es **Python**. Los scripts son escritos en Python y pueden invocar otras herramientas de Hermes [1].
*   **Entorno**: Los scripts se ejecutan en un **proceso hijo** en el host del agente. La comunicación entre el script en ejecución y el agente principal se realiza a través de un **socket de dominio Unix** y un **hilo de escucha RPC** [1].

## Cuándo el Agente Utiliza `execute_code`

El agente utiliza la herramienta `execute_code` en los siguientes escenarios [1]:

*   Cuando se necesitan **3 o más llamadas a herramientas** con lógica de procesamiento entre ellas.
*   Cuando es necesario **filtrar o reducir grandes salidas de herramientas** antes de que entren en el contexto.
*   Cuando se requiere **ramificación condicional** (declaraciones `if/else`).
*   Para **bucles** (`for/while`).
*   Para **manejo de errores** (`try/except`).

## Herramientas Disponibles dentro de los Scripts

Dentro de los scripts de Python ejecutados por `execute_code`, el agente puede acceder a un subconjunto de herramientas de Hermes, incluyendo [1]:

*   `web_search`
*   `web_extract`
*   `read_file`
*   `write_file`
*   `search_files`
*   `patch`
*   `terminal` (solo en primer plano)

## Manejo de Errores

La documentación menciona una sección específica sobre el manejo de errores. En el contexto de la ejecución de código, se espera que el agente pueda implementar bloques `try/except` dentro de sus scripts de Python para manejar excepciones y errores que puedan surgir durante la ejecución de las herramientas o la lógica del script [1].

## Seguridad

La documentación de seguridad de Hermes Agent indica que un vector de ataque de ejecución remota de código es demasiado amplio para ser aprobado. Si se activa la lista de bloqueo, la llamada a la herramienta devuelve un error explicativo al agente y no se ejecuta nada [2]. Esto sugiere que existen mecanismos de seguridad para prevenir la ejecución de código malicioso o no autorizado.

## Referencias

[1] Code Execution | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/user-guide/features/code-execution](https://hermes-agent.nousresearch.com/docs/user-guide/features/code-execution)
[2] Security | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/user-guide/security](https://hermes-agent.nousresearch.com/docs/user-guide/security)

# MÓDULO E: Sandbox y entorno

El Hermes Agent está diseñado con un modelo de seguridad de defensa en profundidad que abarca desde la aprobación de comandos hasta el aislamiento de contenedores y la autorización de usuarios en plataformas de mensajería [1].

## Modelo de Seguridad de Siete Capas

El modelo de seguridad de Hermes Agent se compone de siete capas interconectadas para garantizar un entorno de ejecución seguro y aislado [1]:

1.  **Autorización de usuario**: Controla quién puede interactuar con el agente (listas blancas, emparejamiento de DM).
2.  **Aprobación de comandos peligrosos**: Implementa un sistema de "humano en el bucle" para operaciones potencialmente destructivas.
3.  **Aislamiento de contenedores**: Utiliza sandboxing con Docker, Singularity o Modal con configuraciones endurecidas para aislar el entorno de ejecución.
4.  **Filtrado de credenciales MCP**: Aísla las variables de entorno para los subprocesos de MCP.
5.  **Escaneo de archivos de contexto**: Detecta la inyección de prompts en los archivos del proyecto.
6.  **Aislamiento entre sesiones**: Las sesiones no pueden acceder a los datos o estados de otras sesiones; las rutas de almacenamiento de trabajos cron están protegidas contra ataques de "path traversal".
7.  **Sanitización de entradas**: Los parámetros del directorio de trabajo en los backends de herramientas de terminal se validan contra una lista blanca para prevenir la inyección de shell.

## Aprobación de Comandos Peligrosos

Antes de ejecutar cualquier comando, Hermes lo verifica contra una lista curada de patrones peligrosos. Si se encuentra una coincidencia, el usuario debe aprobarlo explícitamente. El sistema de aprobación soporta tres modos, configurables a través de `approvals.mode` en `~/.hermes/config.yaml` [1]:

| Modo | Comportamiento |
| --- | --- |
| **manual** (por defecto) | Siempre solicita la aprobación del usuario para comandos peligrosos. |
| **smart** | Utiliza un LLM auxiliar para evaluar el riesgo. Los comandos de bajo riesgo se aprueban automáticamente. Los comandos genuinamente peligrosos se deniegan automáticamente. Los casos inciertos escalan a una solicitud manual. |
| **off** | Deshabilita todas las comprobaciones de aprobación. Todos los comandos se ejecutan sin solicitudes. **ADVERTENCIA**: Solo debe usarse en entornos de confianza. |

El modo YOLO (`--yolo` o `/yolo`) omite todas las solicitudes de aprobación de comandos peligrosos para la sesión actual, excepto la lista de bloqueo de línea dura [1].

### Lista de Bloqueo de Línea Dura

Algunos comandos son tan catastróficos que Hermes se niega a ejecutarlos independientemente de cualquier configuración de aprobación. Estos incluyen [1]:

*   `rm -rf /` y variantes obvias (borra la raíz del sistema de archivos).
*   `:(){ :|:& };:` (bomba fork de bash).
*   `mkfs.*` en un dispositivo raíz montado (formatea el sistema en vivo).
*   `dd if=/dev/zero of=/dev/sd*` (borra un disco físico).
*   Redireccionar URLs no confiables a `sh` en el nivel superior del sistema de archivos raíz (vector de ataque de ejecución remota de código demasiado amplio para aprobar).

Si se intenta ejecutar un comando de la lista de bloqueo, la llamada a la herramienta devuelve un error explicativo al agente y no se ejecuta nada [1].

## Aislamiento de Contenedores

Hermes Agent utiliza contenedores para proporcionar aislamiento. Cuando se ejecuta en backends como `docker`, `singularity`, `modal`, `daytona` o `vercel_sandbox`, las comprobaciones de comandos peligrosos se omiten porque el propio contenedor actúa como límite de seguridad. Los comandos destructivos dentro de un contenedor no pueden dañar el host [1].

### Banderas de Seguridad de Docker

La documentación menciona banderas de seguridad específicas para Docker, aunque no se detallan en el fragmento proporcionado, lo que implica una configuración endurecida para el entorno de contenedores [1].

## Límites de Recursos

El sistema permite la configuración de límites de recursos, lo que es crucial para la gestión del entorno y la prevención de abusos. Estos límites aseguran que el agente no consuma recursos excesivos del sistema anfitrión [1].

## Persistencia del Sistema de Archivos

La persistencia del sistema de archivos se gestiona cuidadosamente para garantizar que los datos del agente se mantengan seguros y accesibles, mientras se previene el acceso no autorizado o la manipulación [1].

## Comparación de Seguridad del Backend de Terminal

Existe una comparación de seguridad para los backends de terminal, lo que sugiere que Hermes evalúa y aplica diferentes niveles de seguridad dependiendo del método de ejecución de comandos de terminal [1].

## Passthrough de Variables de Entorno

El agente gestiona el passthrough de variables de entorno, incluyendo el manejo seguro de credenciales (tokens OAuth, etc.), filtrando lo que cada sandbox puede acceder para evitar la exposición de información sensible [1].

## Referencias

[1] Security | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/user-guide/security](https://hermes-agent.nousresearch.com/docs/user-guide/security)

# MÓDULO F: Memoria y contexto

El Hermes Agent está diseñado con un sistema de memoria persistente que le permite recordar información a través de las sesiones, aprender de la experiencia y mantener un contexto coherente. Este sistema es fundamental para su capacidad de auto-mejora y para manejar tareas complejas a largo plazo [1] [2].

## Componentes de la Memoria

La memoria del Hermes Agent se compone de varios elementos clave [1]:

*   **Memoria a Corto Plazo (Ventana de Contexto del LLM)**: Es la memoria activa del agente, limitada por la ventana de contexto del modelo de lenguaje grande (LLM) subyacente. Contiene la conversación actual y los resultados de las herramientas intermedias. Cuando esta ventana se llena, se activa el mecanismo de compresión.
*   **Memoria Persistente (Archivos `MEMORY.md` y `USER.md`)**: Estos archivos almacenan hechos y preferencias relevantes que el agente ha aprendido o que el usuario ha proporcionado. `MEMORY.md` contiene información general aprendida por el agente, mientras que `USER.md` almacena preferencias y detalles específicos del usuario. Esta información se inyecta en el prompt del sistema al inicio de cada sesión, permitiendo que el agente "recuerde" cosas importantes entre conversaciones [1].
*   **Base de Datos de Sesiones (SQLite)**: Al finalizar cada sesión, la memoria se archiva en una base de datos SQLite. Esta base de datos almacena el historial completo de conversaciones y permite la búsqueda en la memoria a largo plazo a través de la herramienta `session_search` [1].
*   **Biblioteca de Habilidades**: Las habilidades creadas por el agente a partir de la experiencia se almacenan como archivos `.md` en `~/.hermes/skills/`. Estas habilidades representan conocimiento procedimental reutilizable para tipos de tareas recurrentes [1].

## Gestión del Contexto y Compresión

La gestión eficiente del contexto es crucial para evitar exceder los límites de la ventana de contexto del LLM y para mantener la relevancia de la información. Hermes Agent emplea un sistema de compresión que se activa en dos escenarios principales [1]:

*   **Preflight (antes de la llamada a la API)**: Si la conversación excede el 50% de la ventana de contexto del modelo.
*   **Autocompresión del Gateway**: Si la conversación excede el 85% de la ventana de contexto, se activa una compresión más agresiva que se ejecuta entre turnos.

Durante el proceso de compresión [1]:

1.  La memoria se vacía primero al disco para evitar la pérdida de datos.
2.  Los turnos intermedios de la conversación se resumen en un formato compacto.
3.  Los últimos N mensajes se conservan intactos (`compression.protect_last_n`, por defecto: 20).
4.  Los pares de mensajes de llamada/resultado de herramientas se mantienen juntos y nunca se dividen.
5.  Se genera un nuevo ID de linaje de sesión, lo que significa que la compresión crea una sesión "hija".

## Recuperación de Memoria a Largo Plazo

La herramienta `session_search` permite al agente buscar en la memoria a largo plazo de conversaciones pasadas. Esta capacidad es fundamental para recordar hechos de conversaciones anteriores, habilidades creadas previamente o cuando el usuario hace referencia a interacciones pasadas [1].

## Ventana de Contexto

La ventana de contexto es un factor limitante para los LLM. Hermes Agent aborda esto de varias maneras [1]:

*   **Detección Automática**: Hermes intenta detectar la longitud de contexto del modelo LLM utilizado. Esta información se muestra en la línea de inicio de la CLI (por ejemplo, `📊 Context limit: 128000 tokens`).
*   **Configuración Explícita**: Si la detección automática es incorrecta, la longitud de contexto se puede establecer explícitamente en `~/.hermes/config.yaml` bajo `model.context_length`.
*   **Modelos con Ventanas Grandes**: Se recomienda el uso de modelos con ventanas de contexto más grandes para conversaciones extensas.
*   **Compresión**: La compresión de sesiones es el mecanismo principal para gestionar la ventana de contexto y reducir el uso de tokens.

## Referencias

[1] Agent Loop Internals | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/developer-guide/agent-loop](https://hermes-agent.nousresearch.com/docs/developer-guide/agent-loop)
[2] Memory | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/user-guide/features/memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)

# MÓDULO G: Browser/GUI

El Hermes Agent interactúa con entornos web y de interfaz gráfica de usuario (GUI) a través de un conjunto de herramientas dedicadas que le permiten navegar, extraer información y simular interacciones humanas. Estas herramientas se agrupan principalmente en el `toolset: browser` y `toolset: browser-cdp` [1].

## Toolset: `browser`

Este conjunto de herramientas proporciona funcionalidades básicas para la interacción con un navegador web. Es importante destacar que para utilizar la mayoría de estas herramientas, `browser_navigate` debe ser llamado primero para inicializar la sesión del navegador [1].

| Herramienta | Descripción |
| --- | --- |
| `browser_back` | Navega a la página anterior en el historial del navegador. |
| `browser_click` | Simula un clic en un elemento interactivo de la página, identificado por su ID de referencia (`@eX`) obtenido de un `browser_snapshot`. |
| `browser_console` | Obtiene la salida de la consola del navegador y los errores de JavaScript, útil para depuración y detección de problemas en la página. |
| `browser_get_images` | Lista todas las imágenes presentes en la página actual, incluyendo sus URLs y texto alternativo, lo que puede ser útil para el análisis con herramientas de visión. |
| `browser_navigate` | Navega a una URL específica. Esta herramienta es fundamental para iniciar cualquier sesión de navegación y debe ser la primera en ser invocada. Para tareas de recuperación de información más simples y eficientes, se recomienda `web_search` o `web_extract`. |
| `browser_press` | Simula la pulsación de una tecla del teclado, permitiendo acciones como enviar formularios (Enter), navegar (Tab) o ejecutar atajos de teclado. |
| `browser_scroll` | Desplaza la página en una dirección específica (arriba, abajo, izquierda, derecha), lo que permite revelar contenido que no está visible en el viewport actual. |
| `browser_snapshot` | Genera una representación textual del árbol de accesibilidad de la página actual. Devuelve elementos interactivos con IDs de referencia (ej. `@e1`, `@e2`) que pueden ser utilizados por `browser_click` y `browser_type`. Puede generar una vista compacta (`full=false`, por defecto) o una vista completa (`full=true`). |
| `browser_type` | Escribe texto en un campo de entrada editable, identificado por su ID de referencia. Primero borra el contenido existente y luego inserta el nuevo texto. |
| `browser_vision` | Captura una captura de pantalla de la página y la analiza utilizando IA de visión. Esta herramienta es útil para escenarios complejos como CAPTCHAs, verificaciones visuales, diseños intrincados o cuando el `browser_snapshot` textual es insuficiente. |

## Toolset: `browser-cdp`

Este conjunto de herramientas se activa solo cuando un endpoint del Protocolo de Herramientas de Desarrollo de Chrome (CDP) está disponible al inicio de la sesión. Esto puede configurarse a través de `/browser connect`, la configuración `browser.cdp_url`, o mediante sesiones de Browserbase o Camofox [1].

| Herramienta | Descripción |
| --- | --- |
| `browser_cdp` | Permite enviar comandos raw del Protocolo de Herramientas de Desarrollo de Chrome. Actúa como una vía de escape para realizar operaciones del navegador que no están cubiertas por las herramientas `browser_*` de nivel superior. |
| `browser_dialog` | Responde a diálogos nativos de JavaScript (alert, confirm, prompt, beforeunload). Para usarla, primero se debe llamar a `browser_snapshot`, ya que los diálogos pendientes aparecen en su campo `pending_dialogs`. Luego se invoca `browser_dialog` con la acción deseada (`action=\'accept\'|\'dismiss\'`). |

## Interacción con la GUI y Navegación Web

El Hermes Agent utiliza estas herramientas para simular un usuario humano interactuando con una interfaz gráfica. La combinación de `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type` y `browser_scroll` le permite al agente realizar tareas como:

*   **Recopilación de información**: Navegar a sitios web, extraer contenido relevante y buscar datos específicos.
*   **Automatización de formularios**: Rellenar campos de texto, seleccionar opciones en menús desplegables y enviar formularios.
*   **Interacción con elementos dinámicos**: Hacer clic en botones, enlaces y otros elementos interactivos para avanzar en flujos de trabajo web.
*   **Manejo de autenticación**: Aunque no se detalla explícitamente un mecanismo de login general, la capacidad de `browser_type` y `browser_click` sugiere que el agente puede interactuar con formularios de inicio de sesión. La persistencia de la sesión del navegador (cookies, etc.) también es un factor clave para mantener el estado de autenticación.
*   **Análisis visual**: La herramienta `browser_vision` es crucial para interpretar elementos visuales complejos o cuando la estructura textual de la página no es suficiente para comprender el contexto o el contenido.

La capacidad de Hermes Agent para interactuar con la web de esta manera lo convierte en una herramienta potente para tareas que requieren navegación y manipulación de interfaces gráficas, como investigación en línea, automatización de procesos web y extracción de datos de sitios complejos [1].

## Referencias

[1] Built-in Tools Reference | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/reference/tools-reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference)

# MÓDULO H: Multi-agente

El Hermes Agent está diseñado con capacidades multi-agente, permitiéndole delegar tareas a subagentes para trabajar en contextos aislados. Esta funcionalidad es crucial para abordar problemas complejos que requieren la división del trabajo y la especialización [1].

## Herramienta de Delegación: `delegate_task`

La herramienta principal para la funcionalidad multi-agente es `delegate_task`, que permite al agente principal generar uno o más subagentes. Cada subagente opera con su propio entorno y contexto, lo que garantiza un aislamiento efectivo [1].

| Herramienta | Descripción |
| --- | --- |
| `delegate_task` | Genera uno o más subagentes para trabajar en tareas en contextos aislados. Cada subagente obtiene su propia conversación, sesión de terminal y conjunto de herramientas. Solo se devuelve el resumen final; los resultados de herramientas intermedios nunca entran en la ventana de contexto. |

## Características de los Subagentes

Cuando se delega una tarea a un subagente, este opera con las siguientes características [1]:

*   **Contexto Aislado**: Cada subagente tiene su propia conversación, lo que significa que su historial de interacciones y su estado son independientes del agente principal y de otros subagentes. Esto previene la contaminación del contexto y permite que cada subagente se concentre en su tarea específica sin distracciones.
*   **Sesión de Terminal Propia**: Los subagentes pueden ejecutar comandos en su propia sesión de terminal, lo que les permite realizar operaciones de línea de comandos sin interferir con el entorno del agente principal.
*   **Conjunto de Herramientas Independiente**: Cada subagente tiene acceso a su propio conjunto de herramientas, que puede ser configurado para la tarea específica que se le ha delegado. Esto permite la especialización y optimización de recursos.
*   **Comunicación Resumida**: El agente principal solo recibe un resumen final del trabajo realizado por el subagente. Los resultados intermedios de las herramientas ejecutadas por el subagente no se inyectan en la ventana de contexto del agente principal, lo que ayuda a mantener la eficiencia y a evitar la sobrecarga de información.

## Presupuesto de Iteración para Subagentes

Los subagentes tienen presupuestos de iteración independientes, limitados por `delegation.max_iterations` (por defecto, 50 iteraciones). Es importante destacar que el total de iteraciones entre el agente principal y sus subagentes puede exceder el límite del agente principal (por defecto, 90 iteraciones), ya que cada uno gestiona su propio presupuesto [2].

## Coordinación de Subagentes

Aunque la herramienta `delegate_task` permite la creación de subagentes con contextos aislados, la coordinación entre ellos se gestiona a través del agente principal, que es el encargado de recibir los resúmenes finales y consolidar el trabajo. Esto implica que el agente principal debe tener la capacidad de interpretar los resultados de los subagentes y utilizarlos para avanzar en la tarea general [1].

## Beneficios del Enfoque Multi-agente

El enfoque multi-agente en Hermes Agent ofrece varios beneficios clave:

*   **Resolución de Problemas Complejos**: Permite dividir problemas grandes y complejos en subtareas más pequeñas y manejables, que pueden ser abordadas por subagentes especializados.
*   **Eficiencia**: Al aislar el contexto y los recursos, los subagentes pueden trabajar de manera más eficiente en sus tareas específicas.
*   **Escalabilidad**: Facilita la escalabilidad al permitir que múltiples agentes trabajen en paralelo en diferentes partes de un problema.
*   **Reducción de la Carga de Contexto**: Al recibir solo resúmenes finales de los subagentes, el agente principal evita la sobrecarga de su ventana de contexto con detalles intermedios.

## Referencias

[1] Built-in Tools Reference | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/reference/tools-reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference)
[2] Agent Loop Internals | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/developer-guide/agent-loop](https://hermes-agent.nousresearch.com/docs/developer-guide/agent-loop)

# MÓDULO I: Integraciones

El Hermes Agent está diseñado para interactuar con una variedad de servicios externos y plataformas a través de un sistema de integraciones robusto. Esto le permite extender sus capacidades más allá de su entorno local y conectarse con el mundo digital de manera efectiva. Las integraciones se gestionan a través de herramientas específicas y el Model Context Protocol (MCP) [1].

## Integraciones Nativas y Toolsets

Hermes Agent incluye toolsets para integraciones con servicios populares, permitiéndole realizar acciones específicas en esas plataformas [1]:

*   **Home Assistant**: Permite controlar dispositivos inteligentes y automatizaciones del hogar. Herramientas como `ha_call_service`, `ha_get_state`, `ha_list_entities` y `ha_list_services` facilitan la interacción con el ecosistema de Home Assistant.
*   **Feishu/Lark**: Proporciona herramientas para interactuar con documentos y archivos en Feishu Drive, como `feishu_doc_read`, `feishu_drive_add_comment`, `feishu_drive_list_comments`, `feishu_drive_list_comment_replies` y `feishu_drive_reply_comment`.
*   **Spotify**: Permite controlar la reproducción de música, buscar canciones y gestionar listas de reproducción con herramientas como `spotify_play`, `spotify_pause`, `spotify_resume`, `spotify_skip_next`, `spotify_skip_previous`, `spotify_volume` y `spotify_search`.
*   **Discord**: Facilita el envío de mensajes a canales de Discord y la gestión de miembros con herramientas como `discord_send_message`, `discord_list_channels`, `discord_kick_member` y `discord_ban_member`.
*   **Yuanbao**: Ofrece herramientas para la gestión financiera, como `yuanbao_get_balance`, `yuanbao_send_payment`, `yuanbao_list_transactions`, `yuanbao_create_invoice` y `yuanbao_pay_invoice`.
*   **ElevenLabs**: Permite la conversión de texto a voz utilizando la herramienta `tts`.
*   **FAL.ai**: Utilizado para la generación de imágenes a partir de texto con la herramienta `image_generate`.
*   **Perplexity API**: Empleado para realizar búsquedas web a través de la herramienta `web_search`.

## Model Context Protocol (MCP)

El Model Context Protocol (MCP) es un componente clave para la extensibilidad de Hermes Agent, permitiéndole cargar herramientas dinámicamente desde servidores externos. Esto significa que Hermes puede integrarse con cualquier servicio que exponga una API compatible con MCP [1].

### Funcionamiento del MCP

*   **Carga Dinámica de Herramientas**: Las herramientas MCP aparecen con un prefijo de nombre de servidor (por ejemplo, `github_create_issue` para el servidor MCP de GitHub), lo que indica su origen externo.
*   **Configuración**: La configuración de los servidores MCP se realiza a través de `~/.hermes/config.yaml`, donde se especifican los comandos y argumentos para iniciar los servidores MCP [2].
*   **Manejo de Errores**: El sistema de MCP incluye mecanismos para manejar errores de conexión, detección de herramientas y tiempos de espera, lo que garantiza una integración robusta [2].

## OAuth y Gestión de Credenciales

Para muchas de estas integraciones, especialmente aquellas que interactúan con servicios de terceros, Hermes Agent requiere credenciales de autenticación, como claves API o tokens OAuth. La gestión de estas credenciales se realiza de forma segura [2]:

*   **Variables de Entorno**: Las claves API y los tokens se suelen configurar como variables de entorno (por ejemplo, `FAL_KEY`, `PERPLEXITY_API_KEY`, `SPOTIFY_ACCESS_TOKEN`, `DISCORD_BOT_TOKEN`, `YUANBAO_API_KEY`, `ELEVENLABS_API_KEY`).
*   **Filtrado de Credenciales**: Hermes implementa un filtrado de credenciales para los subprocesos, asegurando que las variables de entorno sensibles no se expongan innecesariamente en los sandboxes de ejecución de código o terminal [2].
*   **Actualización de Credenciales**: En caso de fallos de autenticación (errores 401/403), el sistema de fallback intenta actualizar las credenciales antes de fallar por completo, lo que mejora la resiliencia de las integraciones [2].

## Referencias

[1] Built-in Tools Reference | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/reference/tools-reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference)
[2] Security | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/user-guide/security](https://hermes-agent.nousresearch.com/docs/user-guide/security)

# MÓDULO J: Multimodal

El Hermes Agent posee capacidades multimodales que le permiten procesar y generar información en diversos formatos, incluyendo imágenes y audio. Estas capacidades se integran a través de sus proveedores de IA y herramientas específicas, extendiendo su interacción con el entorno digital [1].

## Procesamiento de Imágenes (Visión)

Hermes Agent integra capacidades de visión a través de sus proveedores de IA y herramientas dedicadas [1]:

*   **Proveedores de IA con Visión**: Hermes es capaz de auto-detectar las capacidades de visión de los proveedores de IA que utiliza (OpenRouter, Anthropic, OpenAI, Google, y cualquier endpoint compatible con OpenAI). Esto significa que puede interactuar con modelos que tienen la habilidad de procesar entradas visuales.
*   **Fallback para Visión**: El sistema incluye un mecanismo de respaldo automático para tareas auxiliares como la visión, asegurando que las operaciones relacionadas con imágenes puedan ser manejadas incluso si el proveedor principal falla.
*   **Herramienta `browser_vision`**: Esta herramienta permite al agente tomar una captura de pantalla de la página actual del navegador y analizarla con IA de visión. Es particularmente útil para comprender visualmente el contenido de una página, resolver CAPTCHAs, superar desafíos de verificación visual, interpretar diseños complejos o cuando el texto no se extrae correctamente. Esto demuestra una capacidad directa para el análisis de imágenes y la interacción visual con interfaces gráficas [2].

## Procesamiento de Audio (Texto a Voz y Voz a Texto)

Hermes Agent soporta funcionalidades de texto a voz (TTS) y voz a texto (STT) a través de múltiples proveedores, lo que le permite interactuar con el audio en diversas plataformas de mensajería [1]:

### Texto a Voz (TTS)

El agente puede convertir texto en audio de voz utilizando varios proveedores, cada uno con diferentes características de calidad y costo [1]:

| Proveedor | Calidad | Costo | Clave API |
| --- | --- | --- | --- |
| **Edge TTS** (por defecto) | Buena | Gratuito | No necesaria |
| **ElevenLabs** | Excelente | Pagado | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | Buena | Pagado | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax** | Buena | Pagado | `MINIMAX_API_KEY` |
| **NeuTTS** | Buena | Gratuito | No necesaria |

El audio generado se entrega como un mensaje de voz en plataformas como Telegram (burbuja de voz) o Discord/WhatsApp (adjunto de audio). En modo CLI, se guarda en `~/voice-memos/` [2].

### Voz a Texto (STT)

Para la conversión de voz a texto, Hermes Agent soporta seis proveedores, lo que permite la transcripción de mensajes de voz en diversas plataformas de mensajería [1]:

*   **faster-whisper local**: Solución gratuita que se ejecuta en el dispositivo.
*   **Wrapper de comandos local**: Una interfaz para comandos locales de STT.
*   **Groq**: Proveedor de STT.
*   **OpenAI Whisper API**: Utiliza la API de Whisper de OpenAI.
*   **Mistral**: Proveedor de STT.
*   **xAI**: Proveedor de STT.

La transcripción de mensajes de voz funciona en plataformas como Telegram, Discord, WhatsApp y otras [1].

## Procesamiento de Video

Aunque la documentación oficial no detalla una herramienta específica para el procesamiento de video en la versión 0.12.0, existe una solicitud de característica ([Feature Request] Add video content learning — ingest, ...) en el repositorio de GitHub de NousResearch para que Hermes pueda recibir URLs de video (YouTube, TikTok, etc.) y auto-transcribir y analizar su contenido [3]. Esto sugiere que, si bien no es una capacidad completamente implementada en la versión actual, es un área de desarrollo activo y una necesidad reconocida para futuras versiones.

## Modelos Utilizados

Los modelos específicos utilizados para las capacidades multimodales dependen de los proveedores de IA configurados. Para la visión, Hermes auto-detecta las capacidades de los modelos de OpenRouter, Anthropic, OpenAI y Google. Para TTS y STT, se utilizan los modelos subyacentes de los proveedores mencionados (ElevenLabs, OpenAI Whisper, etc.) [1].

## Referencias

[1] Integrations | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/integrations/](https://hermes-agent.nousresearch.com/docs/integrations/)
[2] Built-in Tools Reference | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/reference/tools-reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference)
[3] [Feature Request] Add video content learning — ingest, ... (n.d.). GitHub. Recuperado de [https://github.com/NousResearch/hermes-agent/issues/12885](https://github.com/NousResearch/hermes-agent/issues/12885)

# MÓDULO K: Límites y errores

El Hermes Agent, como cualquier sistema complejo, presenta una serie de límites y modos de fallo, así como mecanismos para la recuperación y solución de problemas. La documentación oficial proporciona una sección exhaustiva de Preguntas Frecuentes y Solución de Problemas que detalla estos aspectos [1].

## Límites Generales y Capacidades No Nativas

*   **Compatibilidad con Windows**: Hermes Agent no funciona de forma nativa en Windows. Requiere un entorno tipo Unix, por lo que en Windows es necesario instalar WSL2 y ejecutar Hermes desde allí [1].
*   **Soporte Completo en Android/Termux**: Aunque Hermes tiene una ruta de instalación probada para Termux en Android, la extensión completa `.[all]` no está disponible actualmente. Esto se debe a que la extensión `voice` depende de `faster-whisper` → `ctranslate2`, y `ctranslate2` no publica paquetes para Android. En su lugar, se debe usar la extensión `.[termux]` [1].
*   **Modelos LLM**: Los modelos Hermes 3 y 4 de Nous Research NO son agenticos y no están diseñados para usarse con Hermes Agent, ya que carecen de capacidades de llamada a herramientas [2].
*   **Uso de `sudo` en Gateway de Mensajería**: El gateway de mensajería se ejecuta sin una terminal interactiva, lo que impide que `sudo` solicite una contraseña. Por lo tanto, se debe evitar el uso de `sudo` en el gateway o configurar `sudo` sin contraseña para comandos específicos [1].
*   **Compartir Tokens de Bot entre Perfiles**: Dos perfiles no pueden compartir el mismo token de bot para una plataforma de mensajería. Cada plataforma requiere acceso exclusivo a un token de bot, por lo que se debe crear un bot separado por perfil [1].
*   **Aislamiento de Perfiles**: Los perfiles no comparten memoria ni sesiones. Cada perfil tiene su propio almacén de memoria, base de datos de sesiones y directorio de habilidades, estando completamente aislados [1].

## Modos de Fallo y Errores Comunes

### Errores de Instalación

*   **`hermes: command not found`**: Causa común es que el shell no ha recargado el PATH actualizado. La solución implica recargar los perfiles del shell (`~/.bashrc`, `~/.zshrc`) o iniciar una nueva sesión de terminal [1].
*   **Versión de Python Antigua**: Hermes requiere Python 3.11 o superior. Si la versión es antigua, se debe actualizar Python [1].
*   **Comandos de Terminal (`node`, `nvm`, `pyenv`, etc.) no encontrados**: Hermes crea una instantánea del entorno por sesión. Si las herramientas se instalan en ubicaciones que no son fuente por el shell de inicio de sesión (`~/.bashrc` no se carga por defecto en shells de inicio de sesión), no serán visibles. La solución es configurar `~/.hermes/config.yaml` para que incluya los archivos de inicialización del shell relevantes [1].
*   **`uv: command not found`**: Indica que el gestor de paquetes `uv` no está instalado o no está en el PATH. La solución es instalar `uv` [1].
*   **Errores de Permiso Denegado durante la Instalación**: Generalmente ocurre por intentar instalar con `sudo`. La instalación estándar se realiza en `~/.local/bin` sin `sudo` [1].

### Errores de Proveedor y Modelo

*   **`/model` solo muestra un proveedor / no puede cambiar de proveedor**: Ocurre si solo se ha configurado un proveedor. La solución es salir de la sesión y usar `hermes model` desde la terminal para añadir nuevos proveedores [1].
*   **Clave API no funciona**: Puede deberse a una clave faltante, caducada, incorrectamente configurada o para el proveedor equivocado. Se debe verificar la configuración con `hermes config show` o reconfigurar el proveedor con `hermes model` [1].
*   **Modelo no disponible / modelo no encontrado**: El identificador del modelo es incorrecto o no está disponible en el proveedor. Se debe listar los modelos disponibles con `hermes model` y establecer un modelo válido [1].
*   **Límite de Tasa (errores 429)**: Se excede el límite de tasa del proveedor. La solución es esperar y reintentar, considerar actualizar el plan del proveedor, cambiar a un modelo o proveedor diferente, o usar `hermes chat --provider <alternative>` [1].
*   **Longitud de Contexto Excedida**: La conversación se ha vuelto demasiado larga. La solución es comprimir la sesión actual con `/compress`, iniciar una nueva sesión, o usar un modelo con una ventana de contexto más grande. También se puede ajustar explícitamente la longitud de contexto en `config.yaml` si la detección automática es incorrecta [1].
*   **Tiempos de Espera con Modelos Locales**: Hermes auto-detecta endpoints locales y relaja los tiempos de espera de streaming. Si aún hay problemas, se puede aumentar `HERMES_STREAM_READ_TIMEOUT` en el archivo `.env` [1].

### Errores de Terminal

*   **Comando bloqueado como peligroso**: Hermes detecta comandos potencialmente destructivos (ej. `rm -rf`) como una característica de seguridad. Se solicita confirmación al usuario. Se puede pedir al agente que use una alternativa más segura o revisar la lista de patrones peligrosos en la documentación de seguridad [1].
*   **Docker backend no conecta**: El demonio de Docker no está en ejecución o el usuario carece de permisos. Se debe verificar que Docker esté funcionando y añadir el usuario al grupo `docker` [1].

### Errores de Mensajería

*   **Bot no responde a mensajes**: El bot no está en ejecución, no está autorizado o el usuario no está en la lista de permitidos. Se debe verificar el estado del gateway (`hermes gateway status`), iniciarlo (`hermes gateway start`) y revisar los logs [1].
*   **Mensajes no se entregan**: Problemas de red, token de bot caducado o mala configuración del webhook. Se debe verificar el token del bot, revisar los logs del gateway y asegurar que el servidor sea accesible públicamente para plataformas basadas en webhook [1].
*   **Gateway no inicia**: Dependencias faltantes, conflictos de puerto o tokens mal configurados. Se deben instalar las dependencias de mensajería, verificar conflictos de puerto y revisar la configuración [1].
*   **WSL: Gateway se desconecta o falla al iniciar**: El soporte de `systemd` en WSL es poco fiable. La solución es usar el modo en primer plano (`hermes gateway run`), `tmux` o `nohup`. Si se desea usar `systemd`, se debe asegurar que esté habilitado en `wsl.conf` [1].
*   **macOS: Node.js / ffmpeg / otras herramientas no encontradas por el gateway**: Los servicios `launchd` heredan un PATH mínimo. Se debe volver a ejecutar `hermes gateway install` para que capture el PATH actualizado [1].

### Problemas de Rendimiento

*   **Respuestas lentas**: Causado por modelos grandes, servidor API distante o un `system prompt` pesado. Se puede intentar un modelo más rápido/pequeño, reducir los conjuntos de herramientas activos, verificar la latencia de red o asegurar suficiente VRAM para modelos locales [1].
*   **Alto uso de tokens**: Conversaciones largas, `system prompts` verbosos o muchas llamadas a herramientas acumulan contexto. La solución es comprimir la conversación con `/compress` o verificar el uso de tokens con `/usage` [1].
*   **Sesión demasiado larga**: Las conversaciones extendidas acumulan mensajes y salidas de herramientas, acercándose a los límites de contexto. Se puede comprimir la sesión actual, iniciar una nueva sesión con una referencia a la anterior, o reanudar una sesión específica más tarde [1].

### Problemas de MCP (Model Context Protocol)

*   **Servidor MCP no conecta**: El binario del servidor no se encuentra, la ruta del comando es incorrecta o falta el entorno de ejecución. Se deben instalar las dependencias de MCP y verificar la configuración en `config.yaml` [1].
*   **Herramientas no aparecen desde el servidor MCP**: El servidor inició pero la detección de herramientas falló, las herramientas fueron filtradas por la configuración o el servidor no soporta la capacidad MCP esperada. Se deben revisar los logs del gateway/agente, asegurar que el servidor responda al método `tools/list RPC` y revisar la configuración de filtrado de herramientas [1].
*   **Errores de tiempo de espera de MCP**: El servidor MCP tarda demasiado en responder o falló durante la ejecución. Se puede aumentar el tiempo de espera en la configuración del servidor MCP, verificar si el proceso del servidor MCP sigue en ejecución o revisar la conectividad de red para servidores HTTP remotos [1].

## Mecanismos de Recuperación

Hermes Agent incorpora varios mecanismos de recuperación y solución de problemas:

*   **Curator (v0.12.0)**: Una característica autónoma en segundo plano que califica, poda y consolida la biblioteca de habilidades del agente por sí misma, contribuyendo a su mantenimiento y mejora continua [3].
*   **Fallback Providers**: Para los proveedores de IA, Hermes tiene un mecanismo de conmutación por error automática a proveedores de respaldo cuando el modelo principal encuentra errores, incluyendo respaldo para tareas auxiliares como visión y extracción web [1].
*   **Compresión de Sesiones (`/compress`)**: Permite resumir el historial de la conversación para reducir el uso de tokens y evitar exceder la longitud del contexto, preservando la información clave [1].
*   **Detección de Comandos Peligrosos**: Bloquea comandos potencialmente destructivos y solicita la aprobación del usuario, evitando ejecuciones accidentales [1].
*   **Manejo de Tiempos de Espera**: Ajusta los tiempos de espera para modelos locales y permite la configuración manual para evitar interrupciones en contextos grandes [1].
*   **Logs y Herramientas de Diagnóstico**: Proporciona logs detallados (`~/.hermes/logs/gateway.log`) y comandos como `hermes config show` y `hermes gateway status` para diagnosticar problemas [1].

## Referencias

[1] FAQ & Troubleshooting | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/reference/faq](https://hermes-agent.nousresearch.com/docs/reference/faq)
[2] Greetings from the Nous Research team! AMA? (n.d.). Reddit. Recuperado de [https://www.reddit.com/r/hermesagent/comments/1sg57v5/greetings_from_the_nous_research_team_ama/](https://www.reddit.com/r/hermesagent/comments/1sg57v5/greetings_from_the_nous_research_team_ama/)
[3] hermes-agent/RELEASE_v0.12.0.md at main. (n.d.). GitHub. Recuperado de [https://github.com/NousResearch/hermes-agent/blob/main/RELEASE_v0.12.0.md](https://github.com/NousResearch/hermes-agent/blob/main/RELEASE_v0.12.0.md)

# MÓDULO L: Benchmarks

El Hermes Agent integra un marco de entornos completo que conecta sus capacidades de llamada a herramientas con el marco de entrenamiento de RL Atropos. Esto permite tres flujos de trabajo principales: entrenamiento de RL, benchmarks y generación de datos. El sistema de entornos se basa en una cadena de herencia de tres capas, proporcionando una base robusta para la evaluación y el desarrollo [1].

## Benchmarks Disponibles

Hermes Agent utiliza varios benchmarks estandarizados para evaluar el rendimiento de los modelos en tareas agenticas. A continuación, se detallan los principales benchmarks mencionados en la documentación [1]:

### TerminalBench2

*   **Descripción**: Un conjunto de 89 tareas de terminal desafiantes, cada una con su propio entorno de sandbox Docker. Está diseñado para evaluar la capacidad de codificación y administración de sistemas en tareas individuales.
*   **Puntuación**: Binaria (pasa/falla), verificada mediante un conjunto de pruebas.
*   **Sandbox**: Utiliza sandboxes en la nube de Modal, con imágenes Docker por tarea.
*   **Herramientas**: Requiere las herramientas `terminal` y `file`.
*   **Costo**: Aproximadamente $50–200 para una evaluación completa (ejecución paralela).
*   **Tiempo**: Aproximadamente 2–4 horas.
*   **Dataset**: Disponible en HuggingFace bajo [NousResearch/terminal-bench-2](https://huggingface.co/datasets/NousResearch/terminal-bench-2).

### TBLite (OpenThoughts Terminal Bench Lite)

*   **Descripción**: Un conjunto de 100 tareas calibradas por dificultad que sirve como un proxy más rápido para TerminalBench2. Evalúa las mismas habilidades de codificación y administración de sistemas, pero con una eficiencia mejorada.
*   **Puntuación**: Binaria (pasa/falla).
*   **Sandbox**: Utiliza sandboxes en la nube de Modal.
*   **Herramientas**: Requiere las herramientas `terminal` y `file`.
*   **Tareas**: 100 tareas divididas en niveles de dificultad: Fácil (40), Medio (26), Difícil (26), Extremo (8).
*   **Correlación**: Presenta una correlación de r=0.911 con el TerminalBench2 completo.
*   **Velocidad**: Es 2.6–8 veces más rápido que TerminalBench2.
*   **Dataset**: Disponible en HuggingFace bajo [NousResearch/openthoughts-tblite](https://huggingface.co/datasets/NousResearch/openthoughts-tblite).

### YC-Bench

*   **Descripción**: Un benchmark estratégico de largo horizonte donde el agente asume el rol de CEO de una startup de IA. Evalúa la coherencia estratégica del agente a lo largo de cientos de turnos.
*   **Puntuación**: Compuesta por `0.5 × supervivencia + 0.5 × fondos normalizados`.
*   **Sandbox**: Utiliza una terminal local (no requiere Modal).
*   **Herramientas**: Requiere únicamente la herramienta `terminal`.
*   **Ejecuciones**: 9 ejecuciones por defecto (3 preajustes × 3 semillas), ejecutadas secuencialmente.
*   **Costo**: Aproximadamente $50–200 para una evaluación completa.
*   **Tiempo**: Aproximadamente 3–6 horas.

## Integración con Atropos

El sistema de entornos de Hermes Agent se integra con el marco de entrenamiento de RL Atropos, que proporciona [1]:

*   **Gestión de Servidores**: Conexión a APIs compatibles con OpenAI (VLLM, SGLang, OpenRouter).
*   **Programación de Workers**: Coordinación de despliegues paralelos.
*   **Integración con Wandb**: Registro de métricas y visualización de despliegues.
*   **Interfaz CLI**: Tres subcomandos: `serve`, `process`, `evaluate`.
*   **Registro de Evaluación**: `evaluate_log()` guarda los resultados en formato JSON + JSONL.

## Herramientas de Entrenamiento RL

Además de los benchmarks, Hermes Agent ofrece herramientas `rl_*` para la orquestación de flujos de trabajo de entrenamiento de RL remotos, lo que permite a los usuarios entrenar modelos de lenguaje en tareas agenticas de múltiples turnos [1].

## Referencias

[1] Environments, Benchmarks & Data Generation | Hermes Agent. (n.d.). Nous Research. Recuperado de [https://hermes-agent.nousresearch.com/docs/developer-guide/environments](https://hermes-agent.nousresearch.com/docs/developer-guide/environments)

# Lecciones para el Monstruo

A partir de la investigación profunda sobre la arquitectura y el funcionamiento del Hermes Agent v0.12, se pueden extraer las siguientes lecciones clave para el desarrollo y mejora de sistemas agenticos complejos (el "Monstruo"):

1.  **Aislamiento y Seguridad como Base, no como Añadido**: La arquitectura de seguridad de siete capas de Hermes, que incluye la aprobación de comandos peligrosos (con modos manual, smart y off), el aislamiento de contenedores (Docker, Modal, etc.) y el filtrado de credenciales, demuestra que la seguridad debe estar integrada en el núcleo del agente. **Lección**: Implementar un sistema de "humano en el bucle" para operaciones destructivas y asegurar que la ejecución de código no confiable ocurra en entornos estrictamente aislados (sandboxes) para prevenir daños al sistema anfitrión.
2.  **Gestión Proactiva del Contexto y la Memoria**: Hermes aborda el problema de la ventana de contexto limitada mediante un sistema de compresión de dos niveles (preflight al 50% y autocompresión al 85%) y una memoria persistente estructurada (`MEMORY.md`, `USER.md`, base de datos SQLite). **Lección**: No depender únicamente de ventanas de contexto masivas. Implementar mecanismos de compresión inteligente que resuman interacciones pasadas mientras protegen los pares de llamadas/resultados de herramientas recientes, y utilizar una memoria a largo plazo consultable para mantener la coherencia a lo largo del tiempo.
3.  **Ejecución de Código Programático para Eficiencia**: La herramienta `execute_code` de Hermes permite al agente escribir scripts de Python que llaman a otras herramientas internamente, devolviendo solo el resultado final (`print()`) al LLM. Esto reduce drásticamente el uso de tokens y permite flujos de trabajo complejos (bucles, condicionales). **Lección**: Capacitar al agente para que escriba y ejecute scripts que orquesten múltiples llamadas a herramientas en un solo turno, manteniendo los resultados intermedios fuera de la ventana de contexto principal para optimizar el rendimiento y el costo.
4.  **Delegación y Aislamiento de Subagentes**: La capacidad de Hermes para generar subagentes (`delegate_task`) con sus propios contextos, sesiones de terminal y presupuestos de iteración permite abordar problemas complejos de manera modular. **Lección**: Implementar una arquitectura multi-agente donde el agente principal pueda delegar subtareas a agentes especializados. Es crucial que estos subagentes operen en contextos aislados para evitar la contaminación de la memoria y que solo devuelvan resúmenes estructurados al agente principal.
5.  **Resiliencia a través de Fallbacks y Manejo de Errores**: Hermes cuenta con un sistema de fallback automático para proveedores de IA, tanto para el modelo principal como para tareas auxiliares (visión, extracción web). Además, maneja errores de ejecución de código de manera estructurada (tiempos de espera, límites de llamadas). **Lección**: Diseñar el sistema asumiendo que las APIs externas y las ejecuciones de código fallarán. Implementar cadenas de fallback robustas para servicios críticos y asegurar que el agente reciba retroalimentación estructurada sobre los errores para que pueda intentar estrategias alternativas de recuperación.


---

## Fase 3 — Módulos Complementarios: Hermes-Agent v0.12 (NousResearch)

### Benchmarks y Métricas de Rendimiento

El módulo de **Benchmarks y Métricas de Rendimiento** en Hermes-Agent v0.12, desarrollado por NousResearch, es fundamental para la evaluación sistemática y la mejora continua de las capacidades de los agentes de IA. Este módulo integra las funcionalidades de llamada a herramientas del agente con el framework de entrenamiento por refuerzo (RL) Atropos, permitiendo tres flujos de trabajo principales: entrenamiento RL, evaluación de benchmarks estandarizados y generación de datos para el entrenamiento de *Supervised Fine-Tuning* (SFT) [1]. Todos estos flujos comparten un núcleo común: una clase de entorno que define las tareas, ejecuta el bucle del agente y puntúa los resultados.

La arquitectura del entorno de evaluación se basa en una cadena de herencia de tres capas. La base proviene de `atroposlib`, que proporciona gestión de servidores (conectividad con APIs compatibles con OpenAI como VLLM, SGLang, OpenRouter), programación de trabajadores para la coordinación de *rollouts* paralelos, integración con Wandb para el registro de métricas y visualización de *rollouts*, una interfaz CLI con subcomandos `serve`, `process` y `evaluate`, y registro de evaluaciones (`evaluate_log()`) que guarda los resultados en formatos JSON y JSONL [1].

La capa de `hermes-agent` (`environments/hermes_base_env.py`) añade configuraciones de *backend* de terminal para ejecución en entornos *sandbox* (local, Docker, Modal, Daytona, SSH, Singularity), resolución de herramientas (`_resolve_tools_for_group()`) para obtener esquemas de herramientas basados en conjuntos de herramientas habilitados/deshabilitados, integración del bucle del agente (`collect_trajectory()`) que ejecuta `HermesAgentLoop` y puntúa el resultado, y una operación de dos fases. La Fase 1 utiliza un servidor OpenAI para evaluación y SFT, mientras que la Fase 2 emplea un `VLLM ManagedServer` para entrenamiento RL completo con *logprobs* [1].

El `HermesAgentLoop` (`environments/agent_loop.py`) es el motor reutilizable de agente multi-turno que sigue el mismo patrón de llamada a herramientas que el bucle principal de Hermes-Agent. Este proceso implica enviar mensajes y esquemas de herramientas a la API, despachar llamadas a herramientas si la respuesta las contiene, añadir los resultados de las herramientas a la conversación y finalizar cuando no hay más llamadas a herramientas. Las llamadas a herramientas se ejecutan en un *thread pool* (`ThreadPoolExecutor(128)`) para evitar interbloqueos con *backends* asíncronos [1].

El `ToolContext` (`environments/tool_context.py`) proporciona a las funciones de recompensa acceso directo al mismo *sandbox* utilizado por el modelo durante su *rollout*, preservando el estado (archivos, procesos, pestañas del navegador) a través del alcance de `task_id` [1].

#### Benchmarks Disponibles

Hermes-Agent v0.12 soporta varios benchmarks clave para evaluar diferentes aspectos del rendimiento del agente:

*   **TerminalBench2**: Este benchmark consta de 89 tareas desafiantes de terminal con entornos *sandbox* de Docker por tarea. Evalúa la capacidad de codificación y administración de sistemas de una sola tarea. La puntuación es binaria (aprobado/fallido) mediante verificación de suite de pruebas. Utiliza *sandboxes* en la nube de Modal y las herramientas `terminal` y `file`. El costo estimado para una evaluación completa es de ~$50–200 y el tiempo de ejecución es de ~2–4 horas [1]. El dataset asociado es `NousResearch/terminal-bench-2` en HuggingFace.

*   **TBLite (OpenThoughts Terminal Bench Lite)**: Una versión más rápida de TerminalBench2, con 100 tareas calibradas por dificultad. Evalúa las mismas capacidades de codificación y administración de sistemas que TB2, pero con tiers de dificultad calibrados. La puntuación también es binaria. Utiliza *sandboxes* en la nube de Modal y las herramientas `terminal` y `file`. Las tareas se dividen en Fácil (40), Medio (26), Difícil (26) y Extremo (8). Presenta una correlación de r=0.911 con el TB2 completo y es 2.6–8 veces más rápido. El dataset es `NousResearch/openthoughts-tblite` [1].

*   **YC-Bench**: Un benchmark estratégico de largo horizonte donde el agente asume el rol de CEO de una startup de IA. Evalúa la coherencia estratégica multi-turno a lo largo de cientos de turnos. La puntuación es compuesta: `0.5 × supervivencia + 0.5 × fondos_normalizados`. Utiliza un terminal local como *sandbox* (no requiere Modal) y solo la herramienta `terminal`. Se ejecutan 9 *runs* por defecto (3 *presets* × 3 *seeds*) de forma secuencial. El costo estimado es de ~$50–200 y el tiempo de ejecución es de ~3–6 horas [1]. YC-Bench utiliza `collinear-ai/yc-bench`, una simulación determinista con 4 dominios de habilidades (investigación, inferencia, entorno de datos, entrenamiento), un sistema de prestigio, gestión de empleados y presión financiera. A diferencia de la puntuación binaria de TB2, YC-Bench mide la capacidad del agente para mantener una estrategia coherente a lo largo de cientos de decisiones compuestas [1].

*   **HermesSweEnv**: Un entorno de entrenamiento al estilo SWE-bench. El modelo recibe una tarea de codificación, utiliza herramientas de terminal, archivos y web para resolverla, y la función de recompensa ejecuta pruebas en el mismo *sandbox* de Modal [1].

#### Proceso de Ejecución de Benchmarks

Cada entorno es un script Python autónomo con tres subcomandos CLI para su operación:

*   `evaluate`: Ejecuta un benchmark para entornos de solo evaluación. Corre todos los ítems, calcula métricas y las registra en Wandb. No requiere un servidor de entrenamiento o API de ejecución [1].
*   `process`: Ejecuta *rollouts* y guarda trayectorias puntuadas en JSONL. Es útil para generar datos de entrenamiento sin un bucle RL completo [1].
*   `serve`: Conecta el entorno a un servidor API de Atropos en ejecución (`run-api`). Se utiliza durante el entrenamiento RL en vivo, donde el entorno recibe ítems de Atropos, ejecuta *rollouts* del agente, calcula recompensas y envía trayectorias puntuadas de vuelta para el entrenamiento [1].

#### Configuración de Entornos

Los entornos pueden configurarse a través de archivos YAML pasados con `--config`. Los valores YAML anulan los valores predeterminados de `config_init()`, y los argumentos de la CLI anulan los valores YAML. Por ejemplo, se pueden especificar `enabled_toolsets`, `max_agent_turns`, `terminal_backend`, `dataset_name`, entre otros [1].

### Referencias

[1] Hermes Agent. (n.d.). *Environments, Benchmarks & Data Generation*. Recuperado de [https://hermes-agent.nousresearch.com/docs/developer-guide/environments](https://hermes-agent.nousresearch.com/docs/developer-guide/environments)



---
## ACTUALIZACIÓN MAYO 2026

### Estado Actual (Mayo 2026)
La versión más reciente de Hermes Agent es la v0.12.0, lanzada el 30 de abril de 2026. Desde la redacción original de la Biblia, el proyecto ha experimentado un crecimiento significativo, alcanzando más de 64,200 estrellas en GitHub, lo que indica una adopción masiva por parte de los desarrolladores. Se ha establecido una asociación importante con MiniMax, ampliando su soporte de modelos. El agente ahora incluye 118 habilidades (96 integradas y 22 opcionales) en más de 26 categorías. Además, la introducción del sistema de entrenamiento de aprendizaje por refuerzo (RL) Atropos permite entrenar mejores modelos de llamada a herramientas. El modelo de precios sigue siendo completamente gratuito y de código abierto bajo la licencia MIT. Los usuarios son responsables de los costos de alojamiento, que pueden ser tan bajos como $5 USD por mes para un VPS, y los costos de API generalmente oscilan entre $15 y $80 USD por mes, aunque esto puede reducirse a $0 utilizando modelos locales como Ollama.

### Fortalezas Confirmadas
Hermes Agent destaca por su bucle de aprendizaje auto-mejorable, su memoria persistente y sus capacidades de modelado de usuarios. Su naturaleza agnóstica al modelo (con soporte para más de 200 modelos) y su puerta de enlace multiplataforma (Telegram, Discord, Slack, WhatsApp, Signal, CLI) lo hacen altamente versátil y personalizable. La capacidad de generar autónomamente documentos de habilidades reutilizables en Markdown tras completar tareas complejas es una fortaleza validada con los datos actuales.

### Debilidades y Limitaciones Actuales
A pesar de sus fortalezas, el agente tiene dificultades para transferir aprendizajes a diferentes tipos de problemas. Las funciones de autoaprendizaje de Honcho están desactivadas por defecto. Además, su sistema de memoria es menos transparente que el enfoque basado en archivos utilizado por competidores como OpenClaw, y puede no ofrecer la misma calidad de resultados para tareas de codificación en comparación con herramientas especializadas como Claude Code o Cursor.

### Posición en el Mercado
Hermes Agent se posiciona actualmente como líder en el espacio de agentes de código abierto y auto-mejorables. Está experimentando una migración masiva de usuarios provenientes de OpenClaw, impulsada por su bucle de aprendizaje único y su robusto conjunto de características. En comparación con los 5 principales agentes de su categoría, destaca por su enfoque en la creación autónoma de habilidades y su flexibilidad de despliegue, aunque puede quedar rezagado en tareas de codificación pura frente a agentes especializados.

### Puntuación Global
- Autonomía: 8/10
- Puntuación Global: 85/100
- Despliegue: Cloud/Local/Hybrid (Local, Docker, SSH, Daytona, Singularity, Modal, VPS)

### Diferenciador Clave
El diferenciador clave de Hermes Agent es que es el único agente de código abierto con un bucle de aprendizaje integrado que crea y refina autónomamente documentos de habilidades reutilizables a partir de la experiencia. Esta capacidad de auto-mejora continua, combinada con su memoria persistente y modelado de usuario, le permite evolucionar y adaptarse a nuevas tareas sin intervención manual constante.
