# BIBLIA DE OPENCLAW v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO

<table>
  <tr header-row="true">
    <td>Atributo</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Nombre oficial</td>
    <td>OpenClaw (anteriormente Clawdbot, Moltbot)</td>
  </tr>
  <tr>
    <td>Desarrollador</td>
    <td>Peter Steinberger</td>
  </tr>
  <tr>
    <td>País de Origen</td>
    <td>Austria (basado en el desarrollador Peter Steinberger)</td>
  </tr>
  <tr>
    <td>Inversión y Financiamiento</td>
    <td>Inicialmente un proyecto de código abierto con costos operativos significativos (se reportó que hemorragia de $10,000 a $20,000 mensuales en febrero de 2026). Peter Steinberger se unió a OpenAI en febrero de 2026, y se establecerá una fundación sin fines de lucro para la administración futura del proyecto OpenClaw. Se ha reportado que OpenAI está cerrando una ronda de financiación de más de $100 mil millones.</td>
  </tr>
  <tr>
    <td>Modelo de Precios</td>
    <td>Gratuito y de código abierto para auto-alojamiento. Existe una versión en la nube, OpenClaw Cloud, que comienza en $29/mes (primer mes). Los costos varían de $6 a $200+ por mes dependiendo de los modelos de IA utilizados y la configuración.</td>
  </tr>
  <tr>
    <td>Posicionamiento Estratégico</td>
    <td>Asistente personal de IA autónomo, de código abierto, que se ejecuta localmente en los dispositivos del usuario (macOS, Linux, Windows) y se integra con diversas aplicaciones de chat (WhatsApp, Telegram, Discord, Slack, Signal, iMessage) y servicios (Gmail, GitHub, Spotify, Hue, Obsidian, Twitter, Browser, Claude, GPT). Se posiciona como una alternativa a los asistentes de IA basados en la nube, ofreciendo mayor control y privacidad al usuario.</td>
  </tr>
  <tr>
    <td>Gráfico de Dependencias</td>
    <td>Depende de Node.js y utiliza modelos de lenguaje grandes (LLMs) como Claude y DeepSeek. Se integra con diversas APIs de terceros para extender sus capacidades.</td>
  </tr>
  <tr>
    <td>Matriz de Compatibilidad</td>
    <td>Compatible con macOS, Linux, Windows. Integración con WhatsApp, Telegram, Discord, Slack, Signal, iMessage, Gmail, GitHub, Spotify, Hue, Obsidian, Twitter, navegadores web.</td>
  </tr>
  <tr>
    <td>Acuerdos de Nivel de Servicio (SLOs)</td>
    <td>Al ser un proyecto de código abierto y auto-alojado, los SLOs dependen en gran medida de la configuración y el mantenimiento del usuario. Las versiones en la nube (OpenClaw Cloud) probablemente ofrecen SLOs definidos por el proveedor.</td>
  </tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA

<table>
  <tr header-row="true">
    <td>Atributo</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Licencia</td>
    <td>Licencia MIT. Esto permite un uso, modificación y distribución muy permisivos, pero con la condición de preservar los avisos de derechos de autor y licencia.</td>
  </tr>
  <tr>
    <td>Política de Privacidad</td>
    <td>Al ser una herramienta de código abierto y auto-alojada, la privacidad depende en gran medida de la configuración del usuario. Los datos se procesan localmente, lo que ofrece un mayor control sobre la información personal en comparación con los servicios en la nube. Sin embargo, la integración con servicios de terceros (APIs de LLMs, servicios de mensajería) implica compartir datos con esos proveedores según sus propias políticas de privacidad.</td>
  </tr>
  <tr>
    <td>Cumplimiento y Certificaciones</td>
    <td>No se mencionan certificaciones específicas de cumplimiento para el proyecto de código abierto en sí. El cumplimiento dependerá de cómo los usuarios o las organizaciones implementen y configuren OpenClaw, especialmente en entornos regulados.</td>
  </tr>
  <tr>
    <td>Historial de Auditorías y Seguridad</td>
    <td>Como proyecto de código abierto, el código es auditable por la comunidad. Sin embargo, ha habido discusiones y preocupaciones significativas sobre la seguridad, especialmente en relación con instancias expuestas y el uso de habilidades (skills) no verificadas de la comunidad, que pueden representar un riesgo de seguridad. Se recomienda evitar ejecutar OpenClaw con cuentas de trabajo o personales primarias y en dispositivos críticos.</td>
  </tr>
  <tr>
    <td>Respuesta a Incidentes</td>
    <td>No hay un proceso formal de respuesta a incidentes centralizado para el proyecto de código abierto. La responsabilidad recae en el usuario o la comunidad para abordar los incidentes de seguridad. Las versiones en la nube (OpenClaw Cloud) tendrían sus propios protocolos de respuesta a incidentes.</td>
  </tr>
  <tr>
    <td>Matriz de Autoridad de Decisión</td>
    <td>El desarrollo del proyecto de código abierto es liderado por Peter Steinberger, con contribuciones de la comunidad. Tras su unión a OpenAI, se establecerá una fundación sin fines de lucro para la gobernanza futura del proyecto, lo que implicará una matriz de decisión más distribuida.</td>
  </tr>
  <tr>
    <td>Política de Obsolescencia</td>
    <td>No se especifica una política formal de obsolescencia para el proyecto de código abierto. La longevidad y el soporte dependen de la actividad de la comunidad y de la fundación que se establecerá.</td>
  </tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA

OpenClaw no es simplemente una herramienta de IA, sino un motor de ejecución impulsado por inteligencia. Su modelo mental se centra en la autonomía, la persistencia y la capacidad de orquestar tareas a través de diversas herramientas y canales. Para dominar OpenClaw, es crucial entenderlo como un agente que puede aprender, recordar y actuar en nombre del usuario, más que como un chatbot pasivo.

<table>
  <tr header-row="true">
    <td>Atributo</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Paradigma Central</td>
    <td>Agente autónomo persistente y de ejecución local. El valor principal reside en la capacidad del agente para pasar del conocimiento a la acción, orquestando tareas a través de herramientas, archivos y canales.</td>
  </tr>
  <tr>
    <td>Abstracciones Clave</td>
    <td>
      <ul>
        <li>**Agentes/Subagentes:** OpenClaw permite la creación de equipos de subagentes, cada uno con su propia persona y memoria, que pueden colaborar en tareas complejas.</li>
        <li>**Habilidades (Skills):** Son las capacidades que OpenClaw puede ejecutar, que van desde interacciones con aplicaciones de mensajería hasta la automatización de tareas en el sistema operativo.</li>
        <li>**Memoria Persistente:** El agente recuerda preferencias, historial y contexto a lo largo del tiempo, lo que le permite aprender y adaptarse.</li>
        <li>**Gateway (Plano de Control):** Un proceso de larga duración que actúa como el cerebro de OpenClaw, conectando LLMs con herramientas y canales.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Patrones de Pensamiento Recomendados</td>
    <td>
      <ul>
        <li>**Diseño de Personalidad de IA:** En lugar de solo escribir lógica de IA, los desarrolladores deben enfocarse en diseñar la personalidad y el comportamiento del agente.</li>
        <li>**Enfoque en la Orquestación:** Pensar en cómo OpenClaw puede orquestar diferentes herramientas y servicios para lograr un objetivo, en lugar de realizar tareas aisladas.</li>
        <li>**Iteración y Refinamiento:** Considerar que el agente puede aprender y mejorar con el tiempo, por lo que es importante iterar y refinar sus habilidades y comportamiento.</li>
        <li>**Seguridad y Aislamiento:** Dado que OpenClaw puede interactuar con el sistema local, es crucial pensar en la seguridad y el aislamiento de las operaciones.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Anti-patrones a Evitar</td>
    <td>
      <ul>
        <li>**Tratar a los subagentes como empleados junior:** No dar instrucciones vagas o esperar que los subagentes infieran tareas complejas sin una guía clara.</li>
        <li>**Descuidar la seguridad:** Instalar y ejecutar OpenClaw con cuentas de trabajo o personales primarias, o en dispositivos críticos, sin las precauciones adecuadas.</li>
        <li>**Ignorar el costo de los tokens:** No optimizar el uso de los modelos de lenguaje, lo que puede llevar a costos elevados.</li>
        <li>**No validar las habilidades de la comunidad:** Utilizar habilidades (skills) de la comunidad sin una revisión adecuada, lo que puede introducir vulnerabilidades.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Curva de Aprendizaje</td>
    <td>Moderada a alta para usuarios no técnicos, ya que implica la configuración de un entorno de desarrollo, la comprensión de conceptos de agentes de IA y la gestión de integraciones. Sin embargo, existen guías de inicio rápido y configuraciones de un solo clic para facilitar la entrada. Para desarrolladores, la curva es más manejable debido a su naturaleza de código abierto y la capacidad de extensión.</td>
  </tr>
</table>

## L04 — CAPACIDADES TÉCNICAS

<table>
  <tr header-row="true">
    <td>Capacidad</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Capacidades Core</td>
    <td>
      <ul>
        <li>**Ejecución Autónoma de Tareas:** Realiza acciones de forma independiente en el sistema operativo local y a través de integraciones.</li>
        <li>**Integración con LLMs:** Conecta modelos de lenguaje grandes (LLMs) para el razonamiento y la generación de texto.</li>
        <li>**Memoria Persistente:** Mantiene el contexto y el historial de interacciones para un comportamiento coherente.</li>
        <li>**Orquestación de Herramientas:** Utiliza una variedad de herramientas y APIs para interactuar con aplicaciones y servicios.</li>
        <li>**Compatibilidad Multiplataforma:** Funciona en macOS, Linux y Windows.</li>
        <li>**Procesamiento Multimodal:** Soporte para imágenes, audio, video y documentos como entradas y salidas.</li>
        <li>**Text-to-Speech y Speech-to-Text:** Capacidades de transcripción de notas de voz y generación de voz.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Capacidades Avanzadas</td>
    <td>
      <ul>
        <li>**Gestión de Subagentes:** Creación y coordinación de equipos de subagentes para tareas complejas.</li>
        <li>**Automatización de Navegador:** Navegación, interacción y extracción de datos de páginas web.</li>
        <li>**Automatización de Correo Electrónico:** Gestión de bandejas de entrada, envío de correos electrónicos.</li>
        <li>**Gestión de Calendario:** Programación y gestión de eventos.</li>
        <li>**Integración con Sistemas de Control de Versiones:** Interacción con repositorios de código (ej. GitHub) para análisis, resumen de PRs y seguimiento de problemas.</li>
        <li>**Generación de Contenido:** Creación de contenido de texto, imágenes y video.</li>
        <li>**Debugging y Análisis de Código:** Manejo de bucles de depuración, análisis de código y ejecución de pruebas.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Capacidades Emergentes (Abril 2026)</td>
    <td>
      <ul>
        <li>**NVIDIA NemoClaw:** Integración con NVIDIA OpenShell para aplicar políticas de privacidad y seguridad.</li>
        <li>**Modelos de IA más Baratos:** Optimización para trabajar con modelos de lenguaje de bajo costo como MiniMax M2.5.</li>
        <li>**Mejoras en la Automatización de IA:** La versión 3.12 introdujo mejoras significativas en la automatización de agentes de IA.</li>
        <li>**Integración con Bedrock AgentCore:** Ejecución de OpenClaw en Bedrock AgentCore para asistentes de IA compartidos en equipos y familias.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Limitaciones Técnicas Confirmadas</td>
    <td>
      <ul>
        <li>**Seguridad en Entornos de Confianza Mixta:** No está diseñado como un límite de seguridad multi-inquilino para múltiples usuarios adversarios que comparten un agente o gateway.</li>
        <li>**Riesgos de Habilidades no Verificadas:** Las habilidades de la comunidad no verificadas pueden ser una vulnerabilidad de seguridad.</li>
        <li>**Dependencia de LLMs Externos:** El rendimiento y las capacidades están intrínsecamente ligados a los LLMs subyacentes utilizados.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Roadmap Público</td>
    <td>El roadmap público se gestiona principalmente a través del repositorio de GitHub (github.com/openclaw/openclaw), donde se pueden seguir las actualizaciones, issues y contribuciones de la comunidad. La fundación sin fines de lucro que se establecerá tras la unión de Peter Steinberger a OpenAI probablemente definirá un roadmap más formal.</td>
  </tr>
</table>

## L05 — DOMINIO TÉCNICO

<table>
  <tr header-row="true">
    <td>Atributo</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Stack Tecnológico</td>
    <td>
      <ul>
        <li>**Core:** Node.js 22+ (para el Gateway, Channel y LLM).</li>
        <li>**Aplicaciones Móviles:** Swift (iOS), Kotlin (Android).</li>
        <li>**Lenguajes de Programación:** TypeScript, Swift.</li>
        <li>**Entorno de Ejecución:** Puede ejecutarse en infraestructura propia del usuario (laptop, VPS, Mac Mini, nube).</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Arquitectura Interna</td>
    <td>
      <ul>
        <li>**Gateway:** Es el plano de control y transporte de nodos principal de OpenClaw. Es un proceso de larga duración que actúa como el cerebro de OpenClaw, conectando LLMs con herramientas y canales.</li>
        <li>**Channel:** Componente que permite la integración con diversas aplicaciones de chat y superficies de canal (canales incorporados o plugins de canal externos).</li>
        <li>**LLM (Large Language Model):** El cerebro que proporciona la inteligencia, conectado a través del Gateway.</li>
        <li>**Skills (Habilidades):** Módulos que extienden las capacidades del agente, permitiéndole interactuar con diferentes herramientas y servicios.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Protocolos Soportados</td>
    <td>
      <ul>
        <li>**Protocolo WebSocket Gateway:** Es el protocolo principal para la comunicación local y el control dentro de OpenClaw.</li>
        <li>**APIs de Terceros:** Soporta la integración con diversas APIs de servicios externos (ej. Gmail, GitHub, Spotify, etc.).</li>
        <li>**Protocolos de Mensajería:** Interactúa con protocolos de WhatsApp, Telegram, Discord, Slack, Signal, iMessage.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Formatos de Entrada/Salida</td>
    <td>
      <ul>
        <li>**Texto:** Entrada y salida de texto para interacciones con LLMs y aplicaciones de chat.</li>
        <li>**Imágenes:** Soporte para entrada y salida de imágenes.</li>
        <li>**Audio:** Soporte para entrada y salida de audio (transcripción de notas de voz, texto a voz).</li>
        <li>**Video:** Soporte para entrada y salida de video.</li>
        <li>**Documentos:** Soporte para entrada y salida de documentos.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>APIs Disponibles</td>
    <td>
      <ul>
        <li>**OpenClaw API:** Opera localmente a través del Protocolo WebSocket Gateway, actuando como la interfaz principal para la interacción.</li>
        <li>**APIs de LLMs:** Se integra con APIs de proveedores de LLMs como Anthropic (Claude), OpenAI, Gemini, Grok, DeepSeek y Ollama.</li>
        <li>**APIs de Servicios Externos:** Utiliza APIs de servicios como Gmail, GitHub, Spotify, Hue, Obsidian, Twitter, etc., a través de sus habilidades.</li>
      </ul>
    </td>
  </tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS

<table>
  <tr header-row="true">
    <td>Caso de Uso</td>
    <td>Pasos Exactos</td>
    <td>Herramientas Necesarias</td>
    <td>Tiempo Estimado</td>
    <td>Resultado Esperado</td>
  </tr>
  <tr>
    <td>Gestión Autónoma de Correo Electrónico y Calendario</td>
    <td>
      <ol>
        <li>**Configuración de Integración:** Conectar OpenClaw con la cuenta de Gmail y Google Calendar (o servicios equivalentes) mediante las APIs correspondientes.</li>
        <li>**Definición de Reglas:** Establecer reglas para el procesamiento de correos (ej. archivar correos de remitentes específicos, marcar como importantes, redactar respuestas automáticas para consultas frecuentes).</li>
        <li>**Programación de Tareas:** Configurar tareas programadas (cron jobs) para revisar el correo periódicamente, sincronizar eventos del calendario y enviar recordatorios.</li>
        <li>**Interacción y Confirmación:** OpenClaw procesa los correos y eventos, y solicita confirmación al usuario para acciones críticas o ambiguas a través de la aplicación de chat preferida (ej. Telegram).</li>
        <li>**Ejecución de Acciones:** El agente ejecuta las acciones aprobadas, como enviar correos, crear eventos en el calendario o mover archivos adjuntos a carpetas específicas.</li>
      </ol>
    </td>
    <td>OpenClaw Gateway, LLM (ej. Claude, GPT), Skill de Gmail, Skill de Google Calendar, aplicación de mensajería (ej. Telegram).</td>
    <td>Configuración inicial: 1-2 horas. Operación diaria: 5-10 minutos de interacción para confirmaciones.</td>
    <td>Bandeja de entrada organizada, calendario actualizado, reducción del tiempo dedicado a la gestión manual de correos y citas, y respuestas rápidas a comunicaciones importantes.</td>
  </tr>
  <tr>
    <td>Automatización de Tareas de Desarrollo en GitHub</td>
    <td>
      <ol>
        <li>**Configuración de Acceso:** Conectar OpenClaw con la cuenta de GitHub del usuario, proporcionando los permisos necesarios para leer repositorios, resumir PRs y crear issues.</li>
        <li>**Monitoreo de Repositorios:** Configurar OpenClaw para monitorear repositorios específicos en busca de nuevos Pull Requests o actualizaciones de issues.</li>
        <li>**Generación de Resúmenes de PR:** Cuando se detecta un nuevo PR, OpenClaw utiliza un LLM para analizar los cambios de código y generar un resumen conciso para el equipo de desarrollo.</li>
        <li>**Rastreo y Actualización de Issues:** El agente puede rastrear issues, asignar etiquetas, actualizar estados o incluso crear nuevos issues basados en conversaciones o análisis de código.</li>
        <li>**Informes Periódicos:** Generar informes diarios o semanales sobre el estado del repositorio, incluyendo PRs pendientes, issues abiertos y actividad reciente.</li>
      </ol>
    </td>
    <td>OpenClaw Gateway, LLM (ej. Claude Code), Skill de GitHub, aplicación de mensajería (ej. Discord, Slack).</td>
    <td>Configuración inicial: 1 hora. Operación continua: 15-30 minutos de revisión de informes y confirmaciones.</td>
    <td>Mejora de la eficiencia del equipo de desarrollo, reducción del tiempo dedicado a la gestión manual de GitHub, y visibilidad en tiempo real del estado del proyecto.</td>
  </tr>
  <tr>
    <td>Creación de Contenido Multimodal y Automatización de Flujos de Trabajo Creativos</td>
    <td>
      <ol>
        <li>**Definición de Requisitos:** El usuario proporciona a OpenClaw una descripción del contenido deseado (ej. "crear un video corto sobre el lanzamiento de un producto con música de fondo y voz en off").</li>
        <li>**Generación de Activos:** OpenClaw utiliza LLMs y modelos de generación de medios (ej. Sora2 para video, ElevenLabs para TTS) para crear los activos necesarios (guion, imágenes, audio, video).</li>
        <li>**Edición y Composición:** El agente puede realizar ediciones básicas, como eliminar marcas de agua, ajustar la duración del video o combinar audio ambiental con voz en off.</li>
        <li>**Configuración de APIs:** Si es necesario, OpenClaw puede interactuar con consolas en la nube (ej. Google Cloud Console) para configurar APIs y obtener tokens de autenticación para servicios de generación de medios.</li>
        <li>**Publicación o Entrega:** El contenido final se entrega al usuario o se publica directamente en plataformas designadas (ej. redes sociales, sitio web).</li>
      </ol>
    </td>
    <td>OpenClaw Gateway, LLM (ej. GPT-4o, Claude Opus), Skill de generación de video (ej. Sora2), Skill de TTS (ej. ElevenLabs), Skill de automatización de navegador, Skill de Google Cloud Console.</td>
    <td>Configuración inicial: 2-3 horas. Generación de contenido: 30 minutos a varias horas, dependiendo de la complejidad.</td>
    <td>Producción acelerada de contenido creativo, automatización de tareas de edición y configuración, y exploración de nuevas posibilidades en la generación de medios.</td>
  </tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD

<table>
  <tr header-row="true">
    <td>Benchmark</td>
    <td>Score/Resultado</td>
    <td>Fecha</td>
    <td>Fuente</td>
    <td>Comparativa</td>
  </tr>
  <tr>
    <td>PinchBench (General)</td>
    <td>Varía según el modelo de LLM utilizado. Se enfoca en la tasa de éxito, velocidad y costo en tareas de codificación reales.</td>
    <td>Marzo 2026 (actualizaciones continuas)</td>
    <td>kilo.ai (desarrollador oficial de PinchBench)</td>
    <td>PinchBench es el benchmark oficial de evaluación de OpenClaw, reemplazando pruebas sintéticas con tareas del mundo real.</td>
  </tr>
  <tr>
    <td>PinchBench (MiniMax M2.1)</td>
    <td>93.6% de éxito</td>
    <td>Marzo 2026</td>
    <td>PinchBench</td>
    <td>Considerado uno de los mejores en el benchmark, con un costo de $0.14 por tarea.</td>
  </tr>
  <tr>
    <td>PinchBench (Claude Opus 4.6)</td>
    <td>Líder en benchmarks de OpenClaw</td>
    <td>Marzo 2026</td>
    <td>PinchBench, extuitive.com</td>
    <td>Ofrece un alto rendimiento, pero con un costo significativamente mayor (80% más caro que Claude Sonnet 4.5).</td>
  </tr>
  <tr>
    <td>PinchBench (Gemma 4 + Ollama)</td>
    <td>Mejor modelo local para OpenClaw (sin costos de API)</td>
    <td>Enero 2026</td>
    <td>haimaker.ai</td>
    <td>Ideal para configuraciones con cero costos de API, funciona en Mac con 16GB de RAM.</td>
  </tr>
  <tr>
    <td>WildClawBench</td>
    <td>Evalúa la capacidad de un agente de IA para realizar trabajo real de principio a fin sin intervención manual.</td>
    <td>Desconocido</td>
    <td>InternLM (GitHub)</td>
    <td>Un benchmark que se enfoca en la capacidad de los agentes de IA para realizar tareas complejas de forma autónoma.</td>
  </tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN

<table>
  <tr header-row="true">
    <td>Atributo</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Método de Integración</td>
    <td>
      <ul>
        <li>**Gateway Centralizado:** OpenClaw utiliza una arquitectura de "hub-and-spoke" centrada en un Gateway único que actúa como plano de control y transporte de nodos.</li>
        <li>**Skills Personalizadas:** Las integraciones se realizan principalmente a través de "skills" (habilidades) que extienden las capacidades del agente para interactuar con servicios externos.</li>
        <li>**Model Context Protocol (MCP):** Para conexiones de herramientas estandarizadas.</li>
        <li>**Plugins de Canal:** Permite la conexión con diversas aplicaciones de chat a través de plugins.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Protocolo</td>
    <td>
      <ul>
        <li>**WebSocket Gateway Protocol:** Es el protocolo principal para la comunicación local y el control dentro de OpenClaw.</li>
        <li>**APIs de Terceros:** Utiliza los protocolos de las APIs de los servicios con los que se integra (ej. HTTP/HTTPS para APIs REST, etc.).</li>
        <li>**Protocolos de Mensajería:** Se integra con los protocolos de WhatsApp, Telegram, Discord, Slack, Signal, iMessage.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Autenticación</td>
    <td>
      <ul>
        <li>**Tokens/Claves API:** Para la integración con LLMs y servicios de terceros, se utilizan claves API o tokens de autenticación.</li>
        <li>**OAuth:** Para servicios que requieren autorización de usuario (ej. Google Cloud Console para configurar OAuth).</li>
        <li>**Emparejamiento QR:** Para aplicaciones de mensajería como WhatsApp (via Baileys).</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Latencia Típica</td>
    <td>
      <ul>
        <li>**Local-first:** La arquitectura local de OpenClaw permite tiempos de respuesta en milisegundos, ya que no hay estrangulamiento de API ni viajes de ida y vuelta a la nube para las operaciones internas.</li>
        <li>**Dependencia de LLM:** La latencia puede variar significativamente dependiendo del LLM utilizado y la velocidad de su API.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Límites de Rate</td>
    <td>
      <ul>
        <li>**Internos:** Al ser auto-alojado, los límites de rate internos dependen de los recursos del hardware del usuario.</li>
        <li>**Externos:** Los límites de rate para las integraciones dependen de las políticas de uso de las APIs de los servicios de terceros (ej. límites de tokens por minuto para LLMs, límites de solicitudes para APIs de servicios).</li>
      </ul>
    </td>
  </tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS

<table>
  <tr header-row="true">
    <td>Tipo de Test</td>
    <td>Herramienta Recomendada</td>
    <td>Criterio de Éxito</td>
    <td>Frecuencia</td>
  </tr>
  <tr>
    <td>Tests Unitarios e de Integración</td>
    <td>Vitest suites</td>
    <td>Funcionalidad correcta de componentes individuales y su interacción.</td>
    <td>Continuo durante el desarrollo, antes de cada commit/PR.</td>
  </tr>
  <tr>
    <td>Tests End-to-End (E2E)</td>
    <td>Vitest suites, Docker runners</td>
    <td>El agente completa tareas complejas de principio a fin sin intervención manual, interactuando con sistemas reales.</td>
    <td>Regularmente, en entornos de staging o pre-producción.</td>
  </tr>
  <tr>
    <td>Tests de Seguridad</td>
    <td>Herramientas de análisis de seguridad (ej. ClawSec), Moltworker sandbox (para evaluación aislada).</td>
    <td>Identificación y mitigación de vulnerabilidades (ej. hijacking, riesgos de la cadena de suministro de habilidades).</td>
    <td>Periódicamente, especialmente después de cambios significativos o integración de nuevas habilidades.</td>
  </tr>
  <tr>
    <td>Tests de Rendimiento de Modelos</td>
    <td>PinchBench</td>
    <td>Alta tasa de éxito en tareas de codificación, precisión en la llamada a herramientas, adherencia a instrucciones, retención de contexto y costo por tarea optimizado.</td>
    <td>Continuo, para comparar y seleccionar los LLMs más eficientes.</td>
  </tr>
  <tr>
    <td>Tests de Automatización de Navegador</td>
    <td>OpenClaw Browser Testing (funcionalidad de verificación automatizada de sitios web).</td>
    <td>Correcta navegación, interacción con elementos web y extracción de datos.</td>
    <td>Según sea necesario para habilidades que interactúan con la web.</td>
  </tr>
  <tr>
    <td>Verificación de Acciones Automatizadas</td>
    <td>Monitoreo manual y confirmación por parte del usuario.</td>
    <td>Cada acción automatizada debe ser verificada para asegurar que el resultado deseado se ha logrado y no hay efectos secundarios no deseados.</td>
    <td>Constantemente, especialmente en las primeras etapas de uso o con nuevas habilidades.</td>
  </tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN

<table>
  <tr header-row="true">
    <td>Versión</td>
    <td>Fecha de Lanzamiento</td>
    <td>Estado</td>
    <td>Cambios Clave</td>
    <td>Ruta de Migración</td>
  </tr>
  <tr>
    <td>Clawdbot (original)</td>
    <td>Noviembre 2025</td>
    <td>Obsoleto/Renombrado</td>
    <td>Lanzamiento inicial como asistente de IA autónomo.</td>
    <td>Detener el servicio `clawdbot gateway stop`, instalar OpenClaw (`npm install -g openclaw`), copiar el directorio `~/.openclaw/` y las carpetas del agente/espacio de trabajo.</td>
  </tr>
  <tr>
    <td>Moltbot</td>
    <td>27 de Enero de 2026</td>
    <td>Obsoleto/Renombrado</td>
    <td>Renombrado de Clawdbot debido a problemas de marca registrada.</td>
    <td>Similar a la migración de Clawdbot a OpenClaw, asegurando la compatibilidad de la configuración.</td>
  </tr>
  <tr>
    <td>OpenClaw</td>
    <td>30 de Enero de 2026 (renombrado)</td>
    <td>Activo y en desarrollo continuo</td>
    <td>
      <ul>
        <li>Renombrado final de Moltbot.</li>
        <li>Enfoque en la arquitectura local-first y la autonomía del agente.</li>
        <li>Introducción de la gestión del ciclo de vida del Gateway a través de `launchd` en macOS.</li>
        <li>Desarrollo de hooks para el ciclo de vida del agente (pensamiento, respuesta, eventos de mensaje) para integraciones de hardware/presencia.</li>
      </ul>
    </td>
    <td>
      <ul>
        <li>**Migración entre máquinas:** Detener OpenClaw en la máquina antigua, copiar el directorio `~/.openclaw/` completo y las carpetas del espacio de trabajo/agente a la nueva máquina.</li>
        <li>**Importación desde otros sistemas de agentes:** OpenClaw soporta la importación desde otros sistemas de agentes.</li>
        <li>**Verificación Post-Migración:** Ejecutar `openclaw status` para confirmar la ruta del directorio de estado y verificar la integridad de los datos.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>OpenClaw 3.12</td>
    <td>Marzo 2026</td>
    <td>Activo</td>
    <td>Actualizaciones importantes para la automatización de IA, mejoras en las características.</td>
    <td>Actualización a través de `openclaw update --channel stable` o `openclaw update --channel dev` para canales específicos.</td>
  </tr>
</table>

## L11 — MARCO DE COMPETENCIA

<table>
  <tr header-row="true">
    <td>Competidor Directo</td>
    <td>Ventaja vs Competidor</td>
    <td>Desventaja vs Competidor</td>
    <td>Caso de Uso Donde Gana</td>
  </tr>
  <tr>
    <td>AutoGPT</td>
    <td>
      <ul>
        <li>**Autonomía y Ejecución Local:** OpenClaw está diseñado para ser un agente autónomo persistente que se ejecuta localmente, ofreciendo mayor control y privacidad.</li>
        <li>**Integración con Mensajería:** OpenClaw se integra directamente con aplicaciones de mensajería (WhatsApp, Telegram, Discord), lo que facilita la interacción del usuario.</li>
        <li>**Enfoque en la Orquestación de Acciones:** OpenClaw se centra en orquestar acciones a través de sistemas empresariales reales, no solo en el razonamiento.</li>
        <li>**Fiabilidad:** OpenClaw es más fiable cuando se trata como un servicio, no como un script, con configuraciones repetibles y rutas de fallo claras.</li>
      </ul>
    </td>
    <td>
      <ul>
        <li>**Razonamiento Orientado a Objetivos:** AutoGPT está más enfocado en el razonamiento de IA autónomo y orientado a objetivos, lo que puede ser una ventaja para tareas de exploración o investigación más abiertas.</li>
        <li>**Madurez (inicial):** AutoGPT fue uno de los primeros agentes autónomos en ganar popularidad, lo que le dio una ventaja inicial en reconocimiento.</li>
      </ul>
    </td>
    <td>
      <ul>
        <li>**Asistente Personal 24/7:** OpenClaw es superior para funcionar como un asistente personal 24/7 que gestiona el correo electrónico, el calendario y las tareas diarias de forma proactiva.</li>
        <li>**Automatización de Tareas Repetitivas:** Excelente para automatizar tareas repetitivas y flujos de trabajo específicos en el entorno del usuario.</li>
        <li>**Control y Privacidad:** Ideal para usuarios que priorizan el control local de sus datos y la privacidad.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>LangChain</td>
    <td>
      <ul>
        <li>**Producto Completo:** OpenClaw es una plataforma de agente de IA completa y lista para usar, con un Gateway, runtime, habilidades y programación cron.</li>
        <li>**Enfoque en la Acción:** OpenClaw orquesta acciones a través de sistemas reales, mientras que LangChain se enfoca más en orquestar pasos de razonamiento dentro de una aplicación de IA.</li>
        <li>**Experiencia de Usuario:** OpenClaw ofrece una experiencia de usuario más directa al integrarse con aplicaciones de mensajería y ejecutarse localmente.</li>
      </ul>
    </td>
    <td>
      <ul>
        <li>**Flexibilidad de Framework:** LangChain es un framework para construir agentes, lo que ofrece una mayor flexibilidad para desarrolladores que desean construir soluciones de IA altamente personalizadas desde cero.</li>
        <li>**Componentes Reutilizables:** LangChain proporciona una amplia gama de componentes reutilizables para construir aplicaciones basadas en LLMs.</li>
      </ul>
    </td>
    <td>
      <ul>
        <li>**Despliegue Rápido de Agentes:** OpenClaw es ideal para desplegar rápidamente agentes de IA autónomos sin la necesidad de construir un framework desde cero.</li>
        <li>**Integración con Sistemas Existentes:** Gana en escenarios donde se necesita integrar un agente de IA con sistemas y aplicaciones existentes de manera eficiente.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>n8n (y otras herramientas de automatización de flujo de trabajo)</td>
    <td>
      <ul>
        <li>**Inteligencia Artificial Nativa:** OpenClaw integra la IA de forma nativa en el flujo de trabajo, permitiendo un razonamiento y una toma de decisiones más avanzados.</li>
        <li>**Contexto y Memoria Persistente:** OpenClaw mantiene un contexto y una memoria persistentes a través de sesiones, lo que le permite aprender y adaptarse.</li>
        <li>**Autonomía:** OpenClaw está diseñado para la autonomía, ejecutando tareas de forma proactiva y continua.</li>
      </ul>
    </td>
    <td>
      <ul>
        <li>**Interfaz Visual de Flujo de Trabajo:** n8n ofrece una interfaz visual para construir flujos de trabajo, lo que puede ser más intuitivo para usuarios no programadores.</li>
        <li>**Amplia Gama de Integraciones:** n8n tiene una vasta biblioteca de integraciones preconstruidas para diversas aplicaciones y servicios.</li>
      </ul>
    </td>
    <td>
      <ul>
        <li>**Automatización Inteligente:** OpenClaw es superior para la automatización que requiere razonamiento, toma de decisiones y adaptación basada en el contexto.</li>
        <li>**Asistentes Proactivos:** Ideal para crear asistentes que no solo ejecutan tareas, sino que también anticipan necesidades y actúan de forma proactiva.</li>
      </ul>
    </td>
  </tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)

<table>
  <tr header-row="true">
    <td>Capacidad de IA</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Interpretación y Ejecución de Tareas</td>
    <td>OpenClaw es capaz de interpretar el contexto, descomponer tareas en pasos ejecutables, orquestar flujos de trabajo de múltiples pasos, realizar llamadas a herramientas en secuencia, evaluar resultados y tomar decisiones sobre los siguientes pasos de forma autónoma. Puede automatizar tareas digitales ejecutando comandos de shell, interactuando con navegadores web y gestionando archivos locales.</td>
  </tr>
  <tr>
    <td>Modelos Subyacentes</td>
    <td>OpenClaw soporta una amplia gama de Large Language Models (LLMs) de diversos proveedores, incluyendo:
      <ul>
        <li>**Anthropic:** Claude, Sonnet 4.6, Claude Opus 4.6.</li>
        <li>**Google:** Gemini 3.1 Pro, Gemma 4 (para ejecución local con Ollama).</li>
        <li>**OpenAI:** (Implícitamente, dado que el desarrollador se unió a OpenAI).</li>
        <li>**Otros:** Grok, DeepSeek, Ollama, Z.ai (GLM 5 Turbo), Xiaomi (MiMo-V2-Pro), MiniMax (MiniMax M2.7, M2.5), Qwen (Qwen3.6 Plus), StepFun (Step 3.5 Flash), Kimi.</li>
        <li>**Plataformas de API:** OpenRouter.ai es una plataforma común para integrar diferentes APIs de modelos.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Nivel de Control</td>
    <td>OpenClaw ofrece un alto nivel de control al usuario debido a su naturaleza auto-alojada y de ejecución local. Los usuarios tienen control sobre su stack de IA, pudiendo intercambiar modelos, mezclar proveedores y enrutar tareas a agentes especializados. Existe un enfoque en la implementación de capas de seguridad y protección práctica antes de que los prompts lleguen al modelo, lo que indica un control significativo sobre las configuraciones de seguridad.</td>
  </tr>
  <tr>
    <td>Personalización Posible</td>
    <td>La personalización es una característica central de OpenClaw. Se logra principalmente a través de:
      <ul>
        <li>**Skills (Habilidades):** Los usuarios pueden construir sus propias habilidades o utilizar las de la comunidad para extender las capacidades del agente e integrar con diversas APIs y servicios.</li>
        <li>**Definición de Personalidad:** Es posible definir la personalidad y el comportamiento del agente.</li>
        <li>**Configuración de Modelos:** La capacidad de intercambiar y enrutar tareas a diferentes modelos de LLM permite una personalización profunda del comportamiento y rendimiento del agente.</li>
      </ul>
    </td>
  </tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA

<table>
  <tr header-row="true">
    <td>Métrica</td>
    <td>Valor Reportado por Comunidad</td>
    <td>Fuente</td>
    <td>Fecha</td>
  </tr>
  <tr>
    <td>Facilidad de Uso</td>
    <td>2.8/5 (promedio)</td>
    <td>Hackceleration.com Review</td>
    <td>Febrero 2026</td>
  </tr>
  <tr>
    <td>Valor por Dinero</td>
    <td>4.8/5 (promedio)</td>
    <td>Hackceleration.com Review</td>
    <td>Febrero 2026</td>
  </tr>
  <tr>
    <td>Características y Profundidad</td>
    <td>4.2/5 (promedio)</td>
    <td>Hackceleration.com Review</td>
    <td>Febrero 2026</td>
  </tr>
  <tr>
    <td>Tasa de Éxito en Tareas de Codificación (MiniMax M2.1)</td>
    <td>93.6%</td>
    <td>PinchBench</td>
    <td>Marzo 2026</td>
  </tr>
  <tr>
    <td>Costos Operativos</td>
    <td>Variables, desde $6 hasta $200+ al mes, dependiendo de los modelos de LLM y la configuración. Un usuario reportó $47 en una semana. Se estima un costo de $150/mes en fees de LLM.</td>
    <td>Reddit (r/openclaw), aimaker.substack.com, growwstacks.com</td>
    <td>Febrero - Abril 2026</td>
  </tr>
  <tr>
    <td>Riesgos de Seguridad</td>
    <td>Altos, con un 80% de éxito en secuestro en pruebas de seguridad en instancias endurecidas. Preocupación por habilidades no verificadas y exposición de instancias.</td>
    <td>Reddit (r/LocalLLaMA), pcmag.com, semgrep.dev</td>
    <td>Febrero - Abril 2026</td>
  </tr>
  <tr>
    <td>Estabilidad del Sistema</td>
    <td>Algunos usuarios reportan inestabilidad en el sistema de "heartbeat" y resultados inconsistentes en cron jobs.</td>
    <td>Reddit (r/openclaw)</td>
    <td>Desconocido</td>
  </tr>
  <tr>
    <td>Multitarea</td>
    <td>Reportado como un desafío por algunos usuarios.</td>
    <td>Reddit (r/LocalLLaMA)</td>
    <td>Desconocido</td>
  </tr>
  <tr>
    <td>Experiencia General de Usuario</td>
    <td>Considerado un "cambio de juego" y "mágico" por muchos, comparado con el lanzamiento de ChatGPT. Sin embargo, la configuración puede ser compleja para principiantes no técnicos.</td>
    <td>openclaw.ai (testimonios), medium.com, reddit (r/openclaw)</td>
    <td>Enero - Abril 2026</td>
  </tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM

<table>
  <tr header-row="true">
    <td>Plan</td>
    <td>Precio</td>
    <td>Límites</td>
    <td>Ideal Para</td>
    <td>ROI Estimado</td>
  </tr>
  <tr>
    <td>Versión de Código Abierto (Auto-alojada)</td>
    <td>Gratuito (software), costos variables para APIs de LLM y hardware.</td>
    <td>Depende de los límites de las APIs de LLM y los recursos de hardware del usuario.</td>
    <td>Usuarios que priorizan el control, la privacidad y la personalización; desarrolladores; proyectos personales; pequeñas empresas con conocimientos técnicos.</td>
    <td>Alto ROI potencial al reemplazar herramientas pagas y automatizar tareas, pero requiere inversión de tiempo en configuración y optimización. Un usuario reportó construir una "máquina GTM de $300K" por $99/mes.</td>
  </tr>
  <tr>
    <td>OpenClaw Cloud</td>
    <td>Desde $29/mes (primer mes), $59/mes (estándar).</td>
    <td>Especificaciones de la plataforma en la nube (ej. número de agentes, uso de tokens de LLM).</td>
    <td>Equipos y usuarios que buscan una solución lista para usar sin la complejidad de la auto-instalación; aquellos que necesitan escalabilidad y soporte gestionado.</td>
    <td>ROI rápido al reducir la sobrecarga de configuración y mantenimiento, permitiendo a los equipos enfocarse en la automatización de tareas de alto valor.</td>
  </tr>
  <tr>
    <td>Optimización de Costos de API</td>
    <td>Estrategias para reducir costos de LLM (ej. carga bajo demanda, respuestas concisas, modelos más baratos).</td>
    <td>N/A</td>
    <td>Cualquier usuario de OpenClaw que busque minimizar los gastos operativos de los LLM.</td>
    <td>Reducción de costos de API de hasta 85% o más, liberando presupuesto para otras inversiones o aumentando la rentabilidad.</td>
  </tr>
  <tr>
    <td>Estrategia GTM (Go-To-Market)</td>
    <td>N/A</td>
    <td>N/A</td>
    <td>Equipos de ventas y marketing que buscan automatizar la generación de leads, la calificación, la comunicación y la gestión de clientes.</td>
    <td>Aumento de la eficiencia del equipo de ventas, mejora en la calidad de los leads, reducción de costos operativos de marketing y ventas, y escalabilidad de las operaciones GTM.</td>
  </tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING

<table>
  <tr header-row="true">
    <td>Escenario de Test</td>
    <td>Resultado</td>
    <td>Fortaleza Identificada</td>
    <td>Debilidad Identificada</td>
  </tr>
  <tr>
    <td>Evaluación de Seguridad (General)</td>
    <td>Todas las instancias evaluadas exhiben vulnerabilidades de seguridad sustanciales. Los sistemas agentizados son significativamente más riesgosos.</td>
    <td>La comunidad está desarrollando herramientas de seguridad (ej. SuperClaw, ClawSec) y guías de mejores prácticas para mitigar riesgos.</td>
    <td>
      <ul>
        <li>80% de éxito en secuestro (hijacking) en agentes endurecidos.</li>
        <li>77% de descubrimiento de herramientas.</li>
        <li>74% de extracción de prompts.</li>
        <li>Vulnerabilidades de inyección de comandos y RCE (Ejecución Remota de Código) de un solo clic.</li>
        <li>Riesgos en la cadena de suministro de habilidades.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>Red Teaming (ClawTrap)</td>
    <td>ClawTrap, un framework de red teaming basado en MITM (Man-in-the-Middle), se utiliza para la evaluación de seguridad de OpenClaw en el mundo real.</td>
    <td>Capacidad de identificar vulnerabilidades en la interacción del agente con el entorno y las comunicaciones.</td>
    <td>Exposición a ataques MITM que pueden manipular las interacciones del agente.</td>
  </tr>
  <tr>
    <td>Benchmarking de Modelos (PinchBench-Cyber Security)</td>
    <td>El benchmark de ciberseguridad de PinchBench busca emerger de modos de fallo reales.</td>
    <td>Proporciona una evaluación objetiva del rendimiento de los modelos de LLM en tareas de seguridad.</td>
    <td>La evidencia pública sobre la seguridad de OpenClaw es lo suficientemente fuerte como para dar forma a un benchmark, lo que indica la existencia de fallos reales.</td>
  </tr>
  <tr>
    <td>Benchmarking de Agentes (WildClawBench)</td>
    <td>Evalúa la capacidad de los agentes de IA para realizar trabajo real de principio a fin sin intervención manual.</td>
    <td>Mide la autonomía y la capacidad de los agentes para completar tareas complejas en escenarios del mundo real.</td>
    <td>Las trayectorias de OpenClaw exponen diferentes riesgos dominantes, acciones sensibles y estructuras de contexto.</td>
  </tr>
  <tr>
    <td>Benchmarking de Hardware (Jake Benchmark v1)</td>
    <td>Pruebas de 7 modelos locales en 22 tareas de agente reales usando OpenClaw en Raspberry Pi 5 con RTX 3090.</td>
    <td>Identificación de la eficiencia y el rendimiento de diferentes configuraciones de hardware para ejecutar OpenClaw.</td>
    <td>El rendimiento varía significativamente según el hardware y el modelo de LLM utilizado.</td>
  </tr>
</table>
