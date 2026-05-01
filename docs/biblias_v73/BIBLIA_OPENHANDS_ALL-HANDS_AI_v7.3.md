# BIBLIA DE OPENHANDS_ALL-HANDS_AI v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO

<table header-row="true">
<tr><td>Nombre oficial</td><td>OpenHands (anteriormente OpenDevin) [1, 4]</td></tr>
<tr><td>Desarrollador</td><td>OpenHands [2]</td></tr>
<tr><td>País de Origen</td><td>Boston, Massachusetts, Estados Unidos [2, 5]</td></tr>
<tr><td>Inversión y Financiamiento</td><td>Ha recaudado $18.8 millones [12].</td></tr>
<tr><td>Modelo de Precios</td><td>Ofrece una versión de código abierto gratuita. Planes de pago incluyen Team y Enterprise para control avanzado y escalabilidad. Se mencionan planes Pro ($10), Pro+ ($39) y Business, con diferentes límites de solicitudes y características. Prueba gratuita de $20 en créditos para OpenHands Cloud [9, 10, 13].</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>Plataforma de código abierto, agnóstica al modelo, para agentes de codificación en la nube. Automatiza el trabajo de ingeniería de forma segura y transparente, permitiendo a los equipos de software construir más rápido con control total. Se enfoca en el desarrollo de software autónomo impulsado por IA [1, 15].</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Integraciones nativas con GitHub, GitLab, CI/CD, Slack y herramientas de tickets. Se basa en el middleware agnóstico de agentes Daytona [6, 15].</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Compatible con cualquier modelo de IA, pipelines de CI/CD y bases de código. Puede desplegarse en entornos Docker o Kubernetes, autoalojado o en la nube privada [15].</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>Alta fiabilidad para la llamada de herramientas a través de su Tool System. Soluciona el 87% de los tickets de errores el mismo día [15].</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA

<table header-row="true">
<tr><td>Licencia</td><td>La versión de código abierto de OpenHands, incluyendo las imágenes Docker de `openhands` y `agent-server`, está licenciada bajo la Licencia MIT. Esto permite el uso, modificación y distribución libre [16, 17, 18, 19, 20].</td></tr>
<tr><td>Política de Privacidad</td><td>OpenHands tiene una política de privacidad que describe cómo recopilan, usan, divulgan y salvaguardan la información. Emplean salvaguardas técnicas, organizativas y físicas para proteger la información personal [21].</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>Se menciona la compatibilidad con HIPAA para la gestión de calidad en industrias reguladas, y la capacidad de integrarse con LLMs locales y ejecución de código en entornos aislados para cumplir con la seguridad empresarial. No se especifican certificaciones concretas para la plataforma en sí, pero su diseño permite a las empresas cumplir con sus propios requisitos [22].</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>Como plataforma de código abierto, se beneficia de la transparencia y la revisión de la comunidad. Las implementaciones empresariales ofrecen control total sobre los datos, el cumplimiento y la seguridad, con opciones de despliegue en la nube privada o en las instalaciones [1, 15].</td></tr>
<tr><td>Respuesta a Incidentes</td><td>No se detalla un plan específico de respuesta a incidentes en la información pública, pero la naturaleza de su despliegue (autoalojado o en la nube privada) implica que la gestión de incidentes recae en gran medida en el usuario o la empresa que lo implementa.</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>Como proyecto de código abierto, las decisiones clave sobre el desarrollo y la dirección del proyecto son influenciadas por la comunidad de colaboradores. Para las implementaciones empresariales, la autoridad de decisión sobre el uso y la configuración recae en la organización cliente.</td></tr>
<tr><td>Política de Obsolescencia</td><td>No se encontró una política de obsolescencia explícita. Sin embargo, al ser un proyecto de código abierto con una comunidad activa, la evolución y el mantenimiento continuo son impulsados por las contribuciones y el roadmap público.</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA

OpenHands se fundamenta en un modelo mental que busca empoderar a los desarrolladores con agentes de codificación autónomos, promoviendo la automatización segura y transparente del trabajo de ingeniería. Su diseño se centra en la flexibilidad y la adaptabilidad, permitiendo a los usuarios integrar la IA en sus flujos de trabajo existentes con un alto grado de control y visibilidad. Este enfoque se articula a través de abstracciones clave que facilitan la interacción y la orquestación de agentes inteligentes en diversos entornos de desarrollo.

<table header-row="true">
<tr><td>Paradigma Central</td><td>OpenHands opera bajo el paradigma de una plataforma de código abierto y agnóstica al modelo para agentes de codificación en la nube. Su objetivo es automatizar tareas de ingeniería de software de manera segura y transparente, permitiendo a los equipos desarrollar más rápido con control total. El modelo mental se estructura en torno a un Agente, una Conversación, un Espacio de Trabajo (Workspace) y un Flujo de Eventos (Event Stream) [1, 24, 25, 26].</td></tr>
<tr><td>Abstracciones Clave</td><td>
<ul>
<li>**Agente:** Entidad que, a partir de un historial de interacciones, determina la siguiente acción a realizar [25].</li>
<li>**Conversación:** Mantiene el estado y el contexto de la interacción con el agente [25].</li>
<li>**Workspace (Espacio de Trabajo):** Proporciona una interfaz unificada para la ejecución de comandos y operaciones de archivos en diferentes entornos. Permite que los agentes se ejecuten localmente o en entornos contenerizados seguros [27, 29, 30].</li>
<li>**LLM System:** Ofrece una abstracción de proveedores para integrar diversos modelos de lenguaje grandes (LLMs) como OpenAI, Anthropic y Google, junto con un pipeline de solicitudes para gestionar las interacciones con estos modelos [28].</li>
</ul>
</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>
<ul>
<li>**Desarrollo impulsado por agentes:** Delegar tareas de desarrollo de software a agentes de IA para optimizar la eficiencia.</li>
<li>**Modelado mental del usuario (ToM-SWE):** Utilizar agentes con capacidad de comprender solicitudes ambiguas y ofrecer orientación personalizada basada en el modelado del usuario [23, 26].</li>
<li>**Automatización del "Outer Loop":** Enfocarse en la reducción de la carga de trabajo de ingeniería, la aceleración de revisiones de código, la expansión de la cobertura de pruebas, la automatización de documentación y notas de lanzamiento, la refactorización de código legado, la eliminación de deuda de seguridad y la resolución de problemas de producción [15].</li>
<li>**Extensibilidad y personalización:** Aprovechar el SDK, las APIs y los micro-agentes para construir y orquestar agentes personalizados [15].</li>
<li>**Transparencia y control:** Mantener una visibilidad completa de las operaciones del agente y ejercer control sobre el entorno de ejecución [15].</li>
</ul>
</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>
<ul>
<li>**Dependencia de un único modelo de IA:** OpenHands es agnóstico al modelo, por lo que limitar la solución a un solo LLM restringe su flexibilidad [15].</li>
<li>**Falta de visibilidad y control:** Implementar soluciones que no permitan monitorear las acciones del agente o controlar su entorno de ejecución, comprometiendo la seguridad y la transparencia [15].</li>
<li>**Despliegue en entornos inseguros:** Ejecutar agentes en entornos no aislados o sin las debidas configuraciones de control de acceso, exponiendo el código y los datos a riesgos [15].</li>
<li>**Desarrollo desde cero de la orquestación de agentes:** Ignorar el SDK y las APIs existentes de OpenHands para construir funcionalidades ya provistas por la plataforma [15].</li>
<li>**Ignorar la comunidad de código abierto:** Desaprovechar las contribuciones y la retroalimentación de la comunidad, lo que puede ralentizar la evolución y mejora de la plataforma [15].</li>
</ul>
</td></tr>
<tr><td>Curva de Aprendizaje</td><td>La curva de aprendizaje se considera moderada para desarrolladores con experiencia en IA y desarrollo de software. El SDK de OpenHands es descrito como "muy amigable para desarrolladores" y uno de los más completos para el desarrollo de agentes de IA. Existen guías detalladas ("Deep Dive & Build-Your-Own Guide") que facilitan la comprensión y el uso de la plataforma [15, 25, 26].</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS

<table header-row="true">
<tr><td>Capacidades Core</td><td>
<ul>
<li>**Ejecución de trabajo de ingeniería real:** OpenHands no solo sugiere código, sino que ejecuta trabajo de ingeniería autónomo, planificando, modificando código, depurando y optimizando [31, 34].</li>
<li>**Agentes autónomos:** Capacidad de planificar, ejecutar y verificar tareas de desarrollo de software [31].</li>
<li>**Interacción conversacional:** Los agentes pueden comunicarse con humanos en lenguaje natural para pedir aclaraciones o confirmaciones [32].</li>
<li>**Ejecución de código (CodeAct):** Los agentes pueden realizar tareas ejecutando código [32].</li>
<li>**SDK composable:** Un SDK de Python que contiene la tecnología agentic, sirviendo como motor para todas las demás funcionalidades [35].</li>
<li>**Entorno de ejecución seguro y aislado:** Despliegue en entornos Docker o Kubernetes, autoalojado o en la nube, con control de acceso total y auditabilidad [15].</li>
</ul>
</td></tr>
<tr><td>Capacidades Avanzadas</td><td>
<ul>
<li>**Orquestación de agentes:** Construcción y orquestación de agentes personalizados utilizando SDKs, APIs y micro-agentes abiertos [15].</li>
<li>**Agnóstico al modelo:** Adaptabilidad a cualquier modelo de IA, pipeline de CI/CD o base de código con configurabilidad granular [15].</li>
<li>**Integraciones nativas:** Con GitHub, GitLab, Slack, CI/CD y herramientas de tickets [15].</li>
<li>**Automatización del "Outer Loop":** Reducción de la carga de trabajo de ingeniería, aceleración de revisiones de código, expansión de la cobertura de pruebas, automatización de documentación y notas de lanzamiento, refactorización de código legado, eliminación de deuda de seguridad y resolución de problemas de producción [15].</li>
<li>**Agentes con "Teoría de la Mente" (ToM-SWE):** Módulo para mejorar los agentes de ingeniería de software con comprensión personalizada del usuario y comportamiento adaptativo, capaz de entender solicitudes ambiguas y proporcionar orientación personalizada [23, 26].</li>
<li>**Modo Headless:** Para CI/CD y operaciones en segundo plano [36].</li>
</ul>
</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>
<ul>
<li>**Condensación de contexto:** Para agentes de IA más eficientes, lo que sugiere una mejora en el manejo de la información y la optimización del rendimiento [37].</li>
<li>**Soporte para LLMs locales:** Integración con LLMs locales para priorizar la privacidad, la eficiencia de costos y la selección flexible de modelos, aprovechando la aceleración en PCs con Ryzen AI [34].</li>
<li>**Mejoras en la interfaz de línea de comandos (CLI):** Experiencia de usuario intuitiva y potente en la terminal, con la capacidad de guardar y reanudar conversaciones, y usar con IDEs a través de ACP [36].</li>
</ul>
</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>
<ul>
<li>Aunque es muy versátil, la eficacia puede depender de la calidad del LLM subyacente y de la claridad de las instrucciones proporcionadas [15].</li>
<li>La implementación y gestión de entornos autoalojados o en la nube privada requiere conocimientos técnicos específicos por parte del usuario [15].</li>
<li>La información disponible no detalla limitaciones técnicas específicas más allá de las inherentes a la dependencia de LLMs y la necesidad de experiencia para despliegues complejos.</li>
</ul>
</td></tr>
<tr><td>Roadmap Público</td><td>El roadmap público no se detalla explícitamente en la información recopilada, pero la naturaleza de código abierto del proyecto y la mención de una comunidad activa sugieren un desarrollo continuo impulsado por las contribuciones y las necesidades del ecosistema [15]. La evolución del proyecto se enfoca en la mejora de las capacidades de los agentes y la expansión de las integraciones.</td></tr>
</table>

## L05 — DOMINIO TÉCNICO

<table header-row="true">
<tr><td>Stack Tecnológico</td><td>
<ul>
<li>**Lenguaje de Programación:** Python (para el SDK y la lógica del agente) [39].</li>
<li>**Contenerización y Orquestación:** Docker y Kubernetes (para despliegues autoalojados o en la nube) [15].</li>
<li>**Gestión de LLMs:** Biblioteca LiteLLM (para la integración con diversos modelos de lenguaje) [46, 47].</li>
<li>**Middleware:** Daytona (como middleware agnóstico de agentes) [6].</li>
<li>**Sistemas Operativos:** Linux, macOS, Windows con WSL (para la ejecución de la CLI y las integraciones con IDEs) [45].</li>
</ul>
</td></tr>
<tr><td>Arquitectura Interna</td><td>
<ul>
<li>**SDK (Software Development Kit):** Es el motor central, una biblioteca Python componible que encapsula la tecnología agentic [39].</li>
<li>**Interfaces:** Proporciona interfaces de aplicación web, línea de comandos (CLI) y en la nube que consumen las APIs del SDK, asegurando consistencia y flexibilidad [41].</li>
<li>**Modelo Multi-Agente:** Emplea un modelo de enjambre multi-agente para una experiencia de desarrollo integral [43].</li>
<li>**Componentes Principales:** Lógica del agente, múltiples CLIs y un servidor web para la interfaz gráfica de usuario (GUI) [42].</li>
<li>**Abstracción de Workspace:** Unifica la ejecución de comandos y operaciones de archivos en distintos entornos [27, 29, 30].</li>
<li>**Abstracción de LLM System:** Proporciona una interfaz uniforme para más de 100 proveedores de LLMs, incluyendo OpenAI, Anthropic y Google [28].</li>
</ul>
</td></tr>
<tr><td>Protocolos Soportados</td><td>
<ul>
<li>Aunque no se especifican protocolos de red explícitos, se infiere soporte para protocolos estándar de comunicación web (HTTP/S) para la interacción con APIs de LLMs y servicios externos.</li>
<li>Integraciones nativas con plataformas como GitHub, GitLab, Slack y herramientas de ticketing sugieren el uso de sus respectivos protocolos de API [15].</li>
</ul>
</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>
<ul>
<li>**Entrada:** Prompts en lenguaje natural, código fuente (en diversos lenguajes), archivos de configuración, datos de logs, resultados de pruebas, especificaciones de tareas.</li>
<li>**Salida:** Código fuente modificado, parches, pull requests, informes de análisis, resultados de pruebas, documentación generada, mensajes de Slack, tickets en sistemas de gestión de proyectos.</li>
<li>**Comunicación con LLMs:** Principalmente texto para prompts y respuestas.</li>
</ul>
</td></tr>
<tr><td>APIs Disponibles</td><td>
<ul>
<li>**OpenHands Software Agent SDK:** Una biblioteca Python que expone las funcionalidades para construir, personalizar y orquestar agentes de codificación de IA [39, 40].</li>
<li>**APIs del SDK:** Consumidas por las interfaces de la aplicación web, CLI y la nube [41].</li>
<li>**APIs de Proveedores de LLMs:** A través de la abstracción de LiteLLM, OpenHands puede interactuar con las APIs de diversos modelos de lenguaje [46, 47].</li>
</ul>
</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS

<table header-row="true">
<tr><td>Caso de Uso</td><td>Pasos Exactos</td><td>Herramientas Necesarias</td><td>Tiempo Estimado</td><td>Resultado Esperado</td></tr>
<tr><td>**1. Corrección de Vulnerabilidades**</td><td>
<ol>
<li>El agente escanea los repositorios de código en busca de vulnerabilidades de seguridad.</li>
<li>Identifica las vulnerabilidades y las posibles soluciones.</li>
<li>Genera y aplica los cambios de código necesarios para corregir las vulnerabilidades.</li>
<li>Abre un Pull Request (PR) con los cambios propuestos para revisión humana.</li>
</ol>
</td><td>OpenHands (agente de codificación), Repositorio de código (GitHub, GitLab), Herramientas de análisis de seguridad integradas.</td><td>Horas a días, dependiendo de la complejidad y el número de vulnerabilidades.</td><td>Un Pull Request listo para revisión con las vulnerabilidades identificadas y corregidas, mejorando la postura de seguridad del proyecto [15].</td></tr>
<tr><td>**2. Revisión de Pull Requests (PRs)**</td><td>
<ol>
<li>El agente recibe un nuevo Pull Request para revisión.</li>
<li>Analiza el código en busca de calidad, cumplimiento de estándares, seguridad y mejores prácticas.</li>
<li>Proporciona comentarios detallados y sugerencias de mejora directamente en el PR.</li>
<li>Puede aplicar correcciones menores automáticamente o sugerir cambios específicos.</li>
</ol>
</td><td>OpenHands (agente de codificación), Plataforma de control de versiones (GitHub, GitLab), Herramientas de análisis de código estático y dinámico.</td><td>Minutos a horas, reduciendo significativamente el tiempo de revisión manual [15].</td><td>Un Pull Request revisado con comentarios constructivos y posibles correcciones, acelerando el ciclo de integración continua y entrega continua (CI/CD) [15].</td></tr>
<tr><td>**3. Migración de Código Legado**</td><td>
<ol>
<li>El agente toma un sistema legado (ej. COBOL) como entrada.</li>
<li>Analiza la base de código y sus funcionalidades.</li>
<li>Genera código equivalente en un lenguaje moderno (ej. Java).</li>
<li>Incluye pruebas y validaciones para asegurar la equivalencia funcional del código migrado.</li>
<li>Proporciona el nuevo código junto con las pruebas para su despliegue.</li>
</ol>
</td><td>OpenHands (agente de codificación), Herramientas de análisis de código, Entorno de desarrollo para el lenguaje objetivo (ej. Java), Frameworks de testing.</td><td>Días a semanas, dependiendo del tamaño y la complejidad del sistema legado.</td><td>Un codebase moderno y funcional, migrado de un sistema legado, con pruebas que garantizan su correcto funcionamiento, reduciendo la deuda técnica [15].</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD

<table header-row="true">
<tr><td>Benchmark</td><td>Score/Resultado</td><td>Fecha</td><td>Fuente</td><td>Comparativa</td></tr>
<tr><td>**OpenHands Index**</td><td>No se especifica un score único para OpenHands en el índice, ya que es una plataforma para evaluar modelos. Sin embargo, el índice es un benchmark integral para evaluar agentes de codificación de IA en tareas de ingeniería de software del mundo real [49, 50].</td><td>Enero 29, 2026 (lanzamiento inicial) [49]</td><td>OpenHands Blog, OpenHands Index Website [49, 50]</td><td>Compara el rendimiento de modelos de lenguaje grandes (LLMs) en tareas de ingeniería de software [52].</td></tr>
<tr><td>**SWE-bench**</td><td>OpenHands-LM 32B V0.1: 37.2% de tasa de resolución verificada [53].</td><td>No especificada para el 37.2%, pero el benchmark es activo.</td><td>Reddit (menciona un lanzamiento de All Hands, creador de OpenHands) [53].</td><td>Se compara con otros modelos, donde Claude 4.5 Opus (76.80%) y Gemini 3 Flash (75.80%) muestran puntuaciones más altas en las tablas de clasificación oficiales de SWE-bench [51]. DeepSeek V3 (0324) obtuvo 55.1%, superando a claude-3-5-sonnet-20241022 (51.6%) [55].</td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN

<table header-row="true">
<tr><td>Método de Integración</td><td>Protocolo</td><td>Autenticación</td><td>Latencia Típica</td><td>Límites de Rate</td></tr>
<tr><td>**SDK (Software Development Kit)**</td><td>Python Library Calls</td><td>No aplica directamente al SDK, ya que se ejecuta localmente. La autenticación se gestiona a nivel de las APIs de LLM subyacentes o servicios externos integrados [39].</td><td>Muy baja, ya que las operaciones se realizan en el entorno local o directamente a través de las APIs configuradas.</td><td>Depende de los límites de rate de las APIs de LLM o servicios externos utilizados.</td></tr>
<tr><td>**Cloud API**</td><td>HTTP/S (RESTful)</td><td>Claves API (API Keys) para acceso a la plataforma OpenHands Cloud. OAuth para la autenticación con proveedores de LLM como OpenAI ChatGPT [58, 59, 60, 62].</td><td>Variable, depende de la carga del servicio en la nube y la ubicación geográfica. Típicamente en el rango de milisegundos a segundos para operaciones estándar.</td><td>No se especifican límites de rate exactos, pero los planes de precios (Pro, Pro+, Business) sugieren diferentes límites de solicitudes mensuales [9]. Es probable que existan límites por minuto/hora para prevenir abusos.</td></tr>
<tr><td>**Integraciones Nativas**</td><td>Protocolos específicos de cada plataforma (ej. GitHub API, GitLab API, Slack API)</td><td>Tokens de acceso o claves API configuradas para cada servicio integrado [15].</td><td>Variable, depende de la latencia de las APIs de terceros.</td><td>Depende de los límites de rate de las APIs de terceros (GitHub, GitLab, Slack, etc.) [15].</td></tr>
<tr><td>**Despliegue Autoalojado/Privado**</td><td>Directo (ejecución local en Docker/Kubernetes)</td><td>Control de acceso y seguridad gestionados por la infraestructura del usuario [15].</td><td>Muy baja, ya que la ejecución se realiza en la infraestructura del usuario.</td><td>No aplica, ya que el control de recursos es del usuario.</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS

<table header-row="true">
<tr><td>Tipo de Test</td><td>Herramienta Recomendada</td><td>Criterio de Éxito</td><td>Frecuencia</td></tr>
<tr><td>**Unit Tests**</td><td>`pytest` (ejecutado localmente con `poetry run pytest ./tests/unit`) [65].</td><td>Todos los tests unitarios pasan, asegurando la funcionalidad individual de los componentes del SDK y los agentes.</td><td>Continuo, durante el desarrollo y antes de cada integración o despliegue.</td></tr>
<tr><td>**Test de Cobertura**</td><td>OpenHands (para mejorar la cobertura de tests unitarios) [66, 70].</td><td>Aumento del porcentaje de cobertura de código por tests unitarios, identificando áreas no cubiertas.</td><td>Regularmente, como parte del ciclo de desarrollo y CI/CD.</td></tr>
<tr><td>**Evaluación de Agentes (Benchmarks)**</td><td>OpenHands Index (benchmark integral para agentes de codificación de IA) [49, 50, 64].</td><td>El agente demuestra un rendimiento aceptable o superior en tareas de ingeniería de software del mundo real, abarcando cinco áreas clave [52, 67].</td><td>Periódicamente, para evaluar la evolución de los modelos y agentes.</td></tr>
<tr><td>**Verificación de Código Generado por IA**</td><td>Mecanismos de verificación integrados en OpenHands y políticas de confirmación de usuario [68, 69].</td><td>El código generado por IA es correcto, sigue las convenciones del repositorio y cumple con los requisitos funcionales y de seguridad.</td><td>En cada generación de código por parte del agente, con aprobación humana cuando sea necesario.</td></tr>
<tr><td>**Tests de Integración**</td><td>No se especifica una herramienta concreta, pero se infiere el uso de entornos de CI/CD para probar la interacción entre componentes y servicios externos [15].</td><td>Los componentes de OpenHands se integran y funcionan correctamente con sistemas externos (GitHub, GitLab, Slack, etc.) y LLMs.</td><td>Durante el desarrollo y antes de cada despliegue mayor.</td></tr>
<tr><td>**Tests de Seguridad**</td><td>Políticas de confirmación de usuario y sandboxing de la ejecución de código [15, 68].</td><td>Las acciones del agente están controladas y no introducen vulnerabilidades de seguridad. El entorno de ejecución está aislado.</td><td>Continuo, como parte del desarrollo seguro y las auditorías de seguridad.</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN

<table header-row="true">
<tr><td>Versión</td><td>Fecha de Lanzamiento</td><td>Estado</td><td>Cambios Clave</td><td>Ruta de Migración</td></tr>
<tr><td>**OpenHands 1.0.0**</td><td>No se especifica una fecha exacta de lanzamiento para la versión 1.0.0 en GitHub, pero se menciona como "New OpenHands 1.0.0" [71]. Se anticipó una versión completamente abierta para principios de 2025 [74].</td><td>Estable (integración del nuevo SDK) [71].</td><td>Utiliza el nuevo `software-agent-sdk` con muchas optimizaciones en toda la aplicación. Se enfoca en la integración del SDK para un desarrollo más modular y eficiente [71].</td><td>La CLI de OpenHands se migrará para aprovechar el nuevo SDK, siendo el primer consumidor principal del mismo [79].</td></tr>
<tr><td>**`software-agent-sdk`**</td><td>Última versión lanzada 4 días antes de la fecha actual (26 de abril de 2026) [73].</td><td>Activo y en desarrollo continuo.</td><td>SDK modular y limpio para construir agentes de IA. Proporciona un framework unificado y type-safe para construir y desplegar agentes de IA, desde experimentos locales hasta producción [73, 78].</td><td>El SDK está diseñado para ser un componente central, facilitando la construcción y el despliegue de agentes. Permite una migración fluida de experimentos locales a entornos de producción [78].</td></tr>
<tr><td>**`openhands-ai` (PyPI)**</td><td>1.6.0 (Marzo 30, 2026) [75].</td><td>Estable (última versión publicada en PyPI).</td><td>Actualizaciones y mejoras continuas en la biblioteca `openhands-ai`. Las versiones anteriores incluyen 1.5.0 (Marzo 11, 2026), 1.4.0 (Febrero 17, 2026), 1.3.0 (Febrero 2, 2026) [75].</td><td>Las actualizaciones se gestionan a través de `pip` para la biblioteca `openhands-ai`. Se recomienda mantener las dependencias actualizadas para aprovechar las últimas mejoras y correcciones.</td></tr>
<tr><td>**OpenHands Cloud (Beta)**</td><td>Noviembre 12, 2025 [74].</td><td>Beta.</td><td>Versión alojada oficial del desarrollador de software de IA de OpenHands, con nuevas características y mejoras [74].</td><td>Se espera una versión completamente abierta a principios de 2025 (posiblemente refiriéndose a la disponibilidad general después de la beta) [74].</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA

<table header-row="true">
<tr><td>Competidor Directo</td><td>Ventaja vs Competidor</td><td>Desventaja vs Competidor</td><td>Caso de Uso Donde Gana</td></tr>
<tr><td>**Devin (Cognition AI)**</td><td>
<ul>
<li>**Código Abierto y Personalizable:** OpenHands es 100% de código abierto, lo que permite a los usuarios autoalojarlo y tener control total sobre su infraestructura y datos, a diferencia de Devin que es propietario [83, 84].</li>
<li>**Versatilidad:** Es más versátil y una solución completa para agentes de ingeniería de software, adaptable a diversas tareas y flujos de trabajo [83].</li>
<li>**SDK Completo:** Ofrece un SDK robusto para la construcción y orquestación de agentes [15].</li>
</ul>
</td><td>
<ul>
<li>**Estabilidad de la versión SaaS:** La versión SaaS de OpenHands puede ser inestable en comparación con Devin [82].</li>
<li>**Reconocimiento de Marca:** Devin, al ser pionero y propietario, puede tener un mayor reconocimiento inicial en el mercado.</li>
</ul>
</td><td>
<ul>
<li>**Despliegues Autoalojados y Personalizados:** Empresas que requieren control total sobre sus datos y entornos, o que necesitan personalizaciones profundas del agente.</li>
<li>**Comunidades de Código Abierto:** Proyectos que valoran la transparencia, la colaboración y la capacidad de auditar el código fuente.</li>
</ul>
</td></tr>
<tr><td>**SWE-Agent**</td><td>
<ul>
<li>**Agente Generalista:** OpenHands es un agente de IA más generalista, capaz de abordar una gama más amplia de tareas de desarrollo de software [83, 86].</li>
<li>**Enfoque Empresarial:** OpenHands está diseñado para ser "enterprise-ready", con características como control de acceso granular y opciones de despliegue en la nube privada [86].</li>
</ul>
</td><td>
<ul>
<li>**Optimización Específica:** SWE-Agent está más específicamente optimizado para resolver problemas específicos de GitHub, lo que podría darle una ventaja en ese nicho [85].</li>
</ul>
</td><td>
<ul>
<li>**Tareas de Ingeniería de Software Amplias:** Escenarios que requieren un agente capaz de realizar una variedad de tareas de desarrollo, no solo la resolución de problemas de GitHub.</li>
<li>**Entornos Empresariales:** Organizaciones que buscan una solución de agente de IA para el desarrollo de software con capacidades de despliegue y gestión a nivel empresarial.</li>
</ul>
</td></tr>
<tr><td>**GitHub Copilot / Claude Code / Gemini / Replit**</td><td>
<ul>
<li>**Autonomía Completa:** OpenHands ejecuta trabajo de ingeniería real de forma autónoma, planificando, modificando código, depurando y optimizando, mientras que Copilot y Claude Code son más asistentes de codificación [15, 80].</li>
<li>**Plataforma de Agentes:** OpenHands es una plataforma para construir y orquestar agentes, no solo una herramienta de generación de código [15].</li>
<li>**Control y Transparencia:** Ofrece mayor control y transparencia sobre las acciones del agente y el entorno de ejecución [15].</li>
</ul>
</td><td>
<ul>
<li>**Integración Directa en IDE:** Herramientas como GitHub Copilot están profundamente integradas en los IDEs, ofreciendo sugerencias en tiempo real de forma más fluida para desarrolladores individuales.</li>
<li>**Facilidad de Uso para Tareas Simples:** Para tareas de codificación más sencillas o asistencia en tiempo real, Copilot y similares pueden ser más directos.</li>
</ul>
</td><td>
<ul>
<li>**Automatización de Flujos de Trabajo Completos:** Cuando se necesita automatizar ciclos completos de desarrollo, desde la identificación de problemas hasta la creación de PRs y la resolución de tickets.</li>
<li>**Desarrollo de Agentes Personalizados:** Equipos que desean construir sus propios agentes de IA con lógica y herramientas específicas para sus necesidades.</li>
</ul>
</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)

<table header-row="true">
<tr><td>Capacidad de IA</td><td>Modelo Subyacente</td><td>Nivel de Control</td><td>Personalización Posible</td></tr>
<tr><td>**Generación y Ejecución de Código**</td><td>Modelos de Lenguaje Grandes (LLMs) como OpenAI, Anthropic, Google, Ollama, y modelos locales como Qwen3-Coder-30B-A3B-Instruct. OpenHands es agnóstico al modelo y utiliza la biblioteca LiteLLM para la integración [15, 34, 46, 47, 89].</td><td>Alto. Los desarrolladores tienen control sobre qué LLM utilizar y cómo se configura. El SDK permite definir agentes en código y el CLI ofrece control granular sobre el comportamiento del agente y la ejecución de tareas [15, 36, 39, 92].</td><td>Extensa. Los usuarios pueden integrar sus propios LLMs, construir y orquestar agentes personalizados con el SDK, APIs y micro-agentes. Es posible adaptar OpenHands a cualquier modelo, pipeline de CI/CD o base de código [15, 39].</td></tr>
<tr><td>**Depuración y Optimización**</td><td>LLMs integrados, aprovechando sus capacidades de razonamiento y análisis de código [15, 89].</td><td>Alto. Los agentes pueden ser configurados para analizar logs, identificar causas raíz y generar PRs con soluciones, con la posibilidad de intervención humana para revisión y aprobación [15].</td><td>Los agentes pueden ser entrenados o configurados para seguir patrones de depuración específicos o para optimizar el código según criterios definidos por el usuario.</td></tr>
<tr><td>**Análisis de Vulnerabilidades y Seguridad**</td><td>LLMs con capacidades de análisis de código y herramientas de seguridad integradas [15].</td><td>Alto. Los agentes pueden escanear repositorios, identificar vulnerabilidades y generar correcciones, con la supervisión y aprobación del equipo de seguridad [15].</td><td>Personalización de las reglas de escaneo, integración con herramientas de seguridad específicas de la organización y adaptación a políticas de seguridad internas.</td></tr>
<tr><td>**Automatización de Flujos de Trabajo de Desarrollo**</td><td>LLMs y la lógica de orquestación de agentes de OpenHands [15].</td><td>Alto. Los usuarios pueden definir flujos de trabajo complejos para automatizar tareas como la revisión de PRs, la migración de código, la generación de documentación y la gestión de tickets [15].</td><td>Creación de playbooks operativos personalizados, integración con herramientas de terceros y adaptación a los procesos internos de desarrollo de la organización.</td></tr>
<tr><td>**Comprensión del Lenguaje Natural (NLU)**</td><td>LLMs subyacentes [15, 89].</td><td>Moderado a Alto. Los agentes pueden comunicarse con humanos en lenguaje natural para pedir aclaraciones o confirmaciones. El módulo ToM-SWE mejora la comprensión de solicitudes ambiguas [23, 26, 32].</td><td>Personalización de prompts, ajuste fino de modelos para dominios específicos y desarrollo de "skills" especializadas para mejorar la comprensión contextual [33].</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA

<table header-row="true">
<tr><td>Métrica</td><td>Valor Reportado por Comunidad</td><td>Fuente</td><td>Fecha</td></tr>
<tr><td>**Estrellas en GitHub**</td><td>Más de 72.4K [15].</td><td>Página principal de OpenHands, GitHub [15].</td><td>Abril 30, 2026.</td></tr>
<tr><td>**Resolución de Tickets de Errores**</td><td>87% de los tickets de errores resueltos el mismo día [15, 96].</td><td>Testimonios de usuarios y reportes de la empresa [15, 96].</td><td>No especificada, pero mencionada en el contexto de la efectividad del agente.</td></tr>
<tr><td>**Rendimiento en SWE-bench**</td><td>~18-20% en problemas verdaderamente novedosos [99].</td><td>Análisis de rendimiento en SWE-bench-Live [99].</td><td>Febrero 6, 2026 [99].</td></tr>
<tr><td>**Sentimiento General de la Comunidad**</td><td>Positivo, con entusiasmo por su capacidad y versatilidad. Algunos usuarios expresan sorpresa por la falta de atención general a pesar de su potencial [83, 97].</td><td>Reddit, Medium, LinkedIn [83, 97].</td><td>Varios, incluyendo Mar 31, 2026 (Reddit) [83].</td></tr>
<tr><td>**Feedback de Usuarios**</td><td>Los usuarios pueden proporcionar feedback a través de botones de "pulgar arriba/abajo" y correo electrónico [94].</td><td>Hugging Face Datasets (OpenHands/openhands-feedback) [94].</td><td>Continuo.</td></tr>
<tr><td>**Adopción y Ecosistema**</td><td>Creciente ecosistema de colaboradores y usuarios empresariales [100].</td><td>VibeCoding.app Blog [100].</td><td>Marzo 31, 2026 [100].</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM

<table header-row="true">
<tr><td>Plan</td><td>Precio</td><td>Límites</td><td>Ideal Para</td><td>ROI Estimado</td></tr>
<tr><td>**OpenHands Open Source**</td><td>Gratuito</td><td>Requiere la propia clave LLM del usuario. Diseñado para un solo usuario [9, 10].</td><td>Desarrolladores individuales, experimentación, proyectos de código abierto, entornos donde la soberanía de los datos y el despliegue autoalojado son críticos [9, 10, 108].</td><td>Alto, al eliminar costos de licencia y permitir el uso de LLMs de bajo costo o locales. Ahorro significativo en tiempo de desarrollo y depuración.</td></tr>
<tr><td>**OpenHands Cloud (Individual Free Plan)**</td><td>Gratuito</td><td>Incluye 2000 "completions" y 50 solicitudes/mes (datos de marzo de 2026) [10].</td><td>Usuarios individuales que desean probar la plataforma en la nube sin costo inicial, acceso a LLMs a costo [10, 13].</td><td>Moderado a Alto, al permitir el acceso a capacidades de IA sin inversión inicial, con un modelo de pago por uso para escalar.</td></tr>
<tr><td>**OpenHands Cloud (Planes de Pago: Pro, Pro+, Business)**</td><td>Pro: $10/mes, Pro+: $39/mes (datos de marzo de 2026). Los precios pueden variar y se han realizado actualizaciones significativas en el modelo de precios [10, 105].</td><td>Diferentes límites de solicitudes mensuales y características (ej. Pro: 300 solicitudes, Pro+: 1500 solicitudes + todos los modelos, Business: administración de equipo, compartir desarrolladores) [10].</td><td>Equipos pequeños a grandes empresas que buscan control avanzado, escalabilidad, soporte multiusuario, RBAC y características de integración con herramientas como Slack, Jira y Linear [9, 10, 108].</td><td>Muy Alto, a través de la automatización de tareas de ingeniería, reducción del tiempo de revisión de código, mejora de la cobertura de pruebas y modernización de código legado. Se estima que puede resolver el 87% de los tickets de errores el mismo día [15].</td></tr>
</table>

**Estrategia Go-To-Market (GTM):**

La estrategia GTM de OpenHands se centra en varias áreas clave:

*   **Enfoque en el Código Abierto:** Utilizar el modelo de código abierto para fomentar la adopción, la comunidad y la innovación colaborativa. Esto permite a los desarrolladores experimentar y construir con la plataforma de forma gratuita, creando una base de usuarios sólida [15, 108].
*   **Soluciones Empresariales:** Ofrecer versiones empresariales y en la nube con características avanzadas para satisfacer las necesidades de grandes organizaciones, incluyendo control sobre la soberanía de los datos, despliegues air-gapped y en la nube privada [15, 108].
*   **Integración con Ecosistemas Existentes:** Integración nativa con herramientas populares de desarrollo como GitHub, GitLab, Slack y CI/CD para facilitar la adopción y minimizar la fricción en los flujos de trabajo existentes [15].
*   **Posicionamiento como Plataforma de Agentes:** Destacar su capacidad como plataforma para construir y orquestar agentes de IA, en lugar de ser solo una herramienta de codificación asistida, lo que atrae a desarrolladores y empresas que buscan soluciones más autónomas [15].
*   **Demostración de Rendimiento:** Utilizar benchmarks como el OpenHands Index y SWE-bench para demostrar la eficacia y el rendimiento de sus agentes en tareas de ingeniería de software del mundo real [49, 50].
*   **Educación y Contenido:** Proporcionar documentación detallada, guías ("Deep Dive & Build-Your-Own Guide") y blogs para educar a la comunidad sobre el uso y los beneficios de OpenHands [25, 26].

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING

<table header-row="true">
<tr><td>Escenario de Test</td><td>Resultado</td><td>Fortaleza Identificada</td><td>Debilidad Identificada</td></tr>
<tr><td>**Evaluación de Agentes (OpenHands Index)**</td><td>El OpenHands Index es un benchmark integral que evalúa modelos de ingeniería de software agentic en una amplia variedad de tareas del mundo real, cubriendo cinco áreas clave [49, 50, 110, 111].</td><td>
<ul>
<li>**Holístico:** Evalúa el rendimiento de los LLMs en el espectro completo de tareas de ingeniería de software [112].</li>
<li>**Transparencia:** Proporciona una infraestructura de evaluación estandarizada y pipelines de prueba [109].</li>
</ul>
</td><td>
<ul>
<li>**Dependencia del LLM:** El rendimiento final del agente depende en gran medida del LLM subyacente, la complejidad del repositorio, la calidad de las pruebas y la configuración del agente [98].</li>
</ul>
</td></tr>
<tr><td>**Rendimiento en SWE-bench**</td><td>OpenHands-LM 32B V0.1: 37.2% de tasa de resolución verificada [53]. En problemas verdaderamente novedosos, los agentes de OpenHands resuelven aproximadamente el 18-20% [99].</td><td>
<ul>
<li>**Capacidad de Resolución:** Demuestra una capacidad significativa para resolver problemas de ingeniería de software, incluso en escenarios complejos.</li>
<li>**Optimización:** El agente de rendimiento de OpenHands (OpenHands-Perf-Agent) automatiza la corrección de errores de rendimiento en código .NET [113].</li>
</ul>
</td><td>
<ul>
<li>**Brecha con Casos Curados:** El rendimiento en problemas novedosos es considerablemente menor que en casos curados (70%+) [99].</li>
<li>**Comparativa:** Otros modelos como Claude 4.5 Opus y Gemini 3 Flash muestran puntuaciones más altas en las tablas de clasificación oficiales de SWE-bench [51]. DeepSeek V3 (0324) obtuvo 55.1%, superando a claude-3-5-sonnet-20241022 (51.6%) [55].</td></tr>
<tr><td>**Red Teaming y Seguridad (Ataques de Inyección de Prompts)**</td><td>OpenHands ha investigado la mitigación de ataques de inyección de prompts en agentes de software [114]. Se menciona que OpenHands puede ser más propenso a tomar acciones destructivas cuando es impulsado por otros LLMs [114].</td><td>
<ul>
<li>**Conciencia de Seguridad:** Reconocimiento y abordaje de vulnerabilidades como la inyección de prompts.</li>
<li>**Sandboxing:** Utiliza sandboxing para la ejecución de código, lo que ayuda a contener posibles acciones maliciosas [116].</li>
<li>**Análisis de Riesgos:** El sistema de seguridad de OpenHands evalúa los niveles de riesgo de las acciones proporcionados por el LLM [117].</li>
</ul>
</td><td>
<ul>
<li>**Vulnerabilidad a LLMs Externos:** Mayor susceptibilidad a acciones destructivas cuando se utilizan LLMs externos sin las debidas precauciones [114].</li>
<li>**Necesidad de Herramientas Específicas:** La comunidad de seguridad de IA está desarrollando herramientas de red teaming (ej. AgentXploit) para probar la robustez de los agentes de IA, lo que indica que es un área de mejora continua [115].</li>
</ul>
</td></tr>
</table>

## Referencias

[1] OpenHands. *OpenHands | The Open Platform for Cloud Coding Agents*. Disponible en: [https://openhands.dev/](https://openhands.dev/)
[2] Crunchbase. *OpenHands - Crunchbase Company Profile & Funding*. Disponible en: [https://www.crunchbase.com/organization/all-hands-ai](https://www.crunchbase.com/organization/all-hands-ai)
[3] LinkedIn. *Robert Brennan - Co-Founder and CEO at OpenHands*. Disponible en: [https://www.linkedin.com/in/robert-a-brennan](https://www.linkedin.com/in/robert-a-brennan)
[4] arXiv. *An Open Platform for AI Software Developers as Generalist Agents*. Disponible en: [https://arxiv.org/abs/2407.16741](https://arxiv.org/abs/2407.16741)
[5] PitchBook. *Openhands 2026 Company Profile: Valuation, Funding & Investors*. Disponible en: [https://pitchbook.com/profiles/company/639106-03](https://pitchbook.com/profiles/company/639106-03)
[6] Daytona. *OpenHands + Daytona*. Disponible en: [https://openhands.daytona.io/](https://openhands.daytona.io/)
[7] OpenHands. *Introducing All Hands AI | Nov 12, 2025*. Disponible en: [https://openhands.dev/blog/introducing-all-hands-ai](https://openhands.dev/blog/introducing-all-hands-ai)
[8] GitHub. *OpenHands: AI-Driven Development*. Disponible en: [https://github.com/OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
[9] OpenHands. *OpenHands Pricing | Start Building for Free*. Disponible en: [https://openhands.dev/pricing](https://openhands.dev/pricing)
[10] VPSRanking. *OpenHands - Features, Pricing & Review [AI Agent (Coding)]*. Disponible en: [https://vpsranking.com/ai/openhands/](https://vpsranking.com/ai/openhands/)
[11] OpenHands. *OpenHands Cloud Self-hosted: Secure, Convenient ...*. Disponible en: [https://openhands.dev/blog/openhands-cloud-self-hosted-secure-convenient-deployment-of-ai-software-development-agents](https://openhands.dev/blog/openhands-cloud-self-hosted-secure-convenient-deployment-of-ai-software-development-agents)
[12] Comparateur-IA. *OpenHands Review (2026): Pricing, Pros + Free Trial*. Disponible en: [https://comparateur-ia.com/en/ai-tools/openhands](https://comparateur-ia.com/en/ai-tools/openhands)
[13] OpenHands. *Access State-of-the-Art LLM models at cost via ...*. Disponible en: [https://openhands.dev/blog/access-state-of-the-art-llm-models-at-cost-via-openhands-gui-and-cli](https://openhands.dev/blog/access-state-of-the-art-llm-models-at-cost-via-openhands-gui-and-cli)
[14] OpenRouter. *OpenHands LM 32B V0.1 - API Pricing & Providers*. Disponible en: [https://openrouter.ai/all-hands/openhands-lm-32b-v0.1](https://openrouter.ai/all-hands/openhands-lm-32b-v0.1)
[15] OpenHands. *OpenHands | The Open Platform for Cloud Coding Agents*. Disponible en: [https://openhands.dev/](https://openhands.dev/)
[16] GitHub. *OpenHands/LICENSE at main*. Disponible en: [https://github.com/OpenHands/OpenHands/blob/main/LICENSE](https://github.com/OpenHands/OpenHands/blob/main/LICENSE)
[17] OpenHands. *OpenHands Pricing | Start Building for Free*. Disponible en: [https://openhands.dev/pricing](https://openhands.dev/pricing)
[18] GitHub. *OpenHands: AI-Driven Development*. Disponible en: [https://github.com/OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
[19] OpenHands Docs. *About OpenHands*. Disponible en: [https://docs.openhands.dev/openhands/usage/about](https://docs.openhands.dev/openhands/usage/about)
[20] Medium. *Exploring OpenHands — An Open-Source AI Developer ...*. Disponible en: [https://medium.com/@niarsdet/redefining-dev-workflows-exploring-openhands-an-open-source-ai-developer-agent-4d579c6e5f40](https://medium.com/@niarsdet/redefining-dev-workflows-exploring-openhands-an-open-source-ai-developer-agent-4d579c6e5f40)
[21] OpenHands. *Privacy Policy - OpenHands*. Disponible en: [https://openhands.dev/privacy](https://openhands.dev/privacy)
[22] ICertGlobal. *Is OpenHands secure enough for Quality Management in a HIPAA ...*. Disponible en: [https://www.icertglobal.com/community/secure-ai-engineering-with-openhands-in-regulated-industries](https://www.icertglobal.com/community/secure-ai-engineering-with-openhands-in-regulated-industries)
[23] GitHub. *OpenHands/ToM-SWE: The theory of mind module for ...*. Disponible en: [https://github.com/OpenHands/ToM-SWE](https://github.com/OpenHands/ToM-SWE)
[24] OpenHands. *OpenHands | The Open Platform for Cloud Coding Agents*. Disponible en: [https://openhands.dev/](https://openhands.dev/)
[25] DEV Community. *OpenHands — Deep Dive & Build-Your-Own Guide*. Disponible en: [https://dev.to/truongpx396/openhands-deep-dive-build-your-own-guide-1al0](https://dev.to/truongpx396/openhands-deep-dive-build-your-own-guide-1al0)
[26] OpenHands Docs. *Theory of Mind (TOM) Agent*. Disponible en: [https://docs.openhands.dev/sdk/guides/agent-tom-agent](https://docs.openhands.dev/sdk/guides/agent-tom-agent)
[27] OpenHands Docs. *Workspace*. Disponible en: [https://docs.openhands.dev/sdk/arch/workspace](https://docs.openhands.dev/sdk/arch/workspace)
[28] OpenHands Docs. *LLM*. Disponible en: [https://docs.openhands.dev/sdk/arch/llm](https://docs.openhands.dev/sdk/arch/llm)
[29] arXiv. *The OpenHands Software Agent SDK: A Composable and ...*. Disponible en: [https://arxiv.org/html/2511.03690v2](https://arxiv.org/html/2511.03690v2)
[30] OpenHands. *OpenHands*. Disponible en: [https://app.all-hands.dev/](https://app.all-hands.dev/)
[31] Medium. *OpenHands Capability Analysis Report: The Future of AI ...*. Disponible en: [https://medium.com/@mingyang.heaven/openhands-capability-analysis-report-the-future-of-ai-powered-software-development-df2fb550107](https://medium.com/@mingyang.heaven/openhands-capability-analysis-report-the-future-of-ai-powered-software-development-df2fb550107)
[32] OpenHands Docs. *Main Agent and Capabilities*. Disponible en: [https://docs.openhands.dev/openhands/usage/agents](https://docs.openhands.dev/openhands/usage/agents)
[33] OpenHands Docs. *Overview - Skills*. Disponible en: [https://docs.openhands.dev/overview/skills](https://docs.openhands.dev/overview/skills)
[34] AMD. *Local AI for Developers OpenHands AMD Bring Coding ...*. Disponible en: [https://www.amd.com/en/developer/resources/technical-articles/2025/OpenHands.html](https://www.amd.com/en/developer/resources/technical-articles/2025/OpenHands.html)
[35] GitHub. *OpenHands: AI-Driven Development*. Disponible en: [https://github.com/OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
[36] OpenHands. *OpenHands CLI | Secure, Scalable Agentic Software ...*. Disponible en: [https://openhands.dev/product/cli](https://openhands.dev/product/cli)
[37] OpenHands. *OpenHands Context Condensensation for More Efficient AI ...*. Disponible en: [https://openhands.dev/blog/openhands-context-condensensation-for-more-efficient-ai-agents](https://openhands.dev/blog/openhands-context-condensensation-for-more-efficient-ai-agents)
[38] OpenHands. *OpenHands | The Open Platform for Cloud Coding Agents*. Disponible en: [https://openhands.dev/](https://openhands.dev/)
[39] GitHub. *OpenHands: AI-Driven Development*. Disponible en: [https://github.com/OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
[40] OpenHands. *Secure, Scalable Agentic Software Development - OpenHands SDK*. Disponible en: [https://openhands.dev/product/sdk](https://openhands.dev/product/sdk)
[41] OpenHands Docs. *Overview - SDK Arch*. Disponible en: [https://docs.openhands.dev/sdk/arch/overview](https://docs.openhands.dev/sdk/arch/overview)
[42] arXiv. *The OpenHands Software Agent SDK: A Composable and ...*. Disponible en: [https://arxiv.org/pdf/2511.03690](https://arxiv.org/pdf/2511.03690)
[43] GitHub. *System Architecture · Issue #77*. Disponible en: [https://github.com/OpenHands/OpenHands/issues/77](https://github.com/OpenHands/OpenHands/issues/77)
[44] OpenHands Docs. *Design Principles*. Disponible en: [https://docs.openhands.dev/sdk/arch/design](https://docs.openhands.dev/sdk/arch/design)
[45] OpenHands Docs. *IDE Integration Overview*. Disponible en: [https://docs.openhands.dev/openhands/usage/cli/ide/overview](https://docs.openhands.dev/openhands/usage/cli/ide/overview)
[46] OpenHands Docs. *Overview - LLMs*. Disponible en: [https://docs.openhands.dev/openhands/usage/llms/llms](https://docs.openhands.dev/openhands/usage/llms/llms)
[47] GitHub. *OpenHands/Development.md at main*. Disponible en: [https://github.com/OpenHands/OpenHands/blob/main/Development.md](https://github.com/OpenHands/OpenHands/blob/main/Development.md)
[48] OpenHands. *OpenHands | The Open Platform for Cloud Coding Agents*. Disponible en: [https://openhands.dev/](https://openhands.dev/)
[49] OpenHands. *Introducing the OpenHands Index | Jan 28, 2026*. Disponible en: [https://openhands.dev/blog/openhands-index](https://openhands.dev/blog/openhands-index)
[50] OpenHands Index. *OpenHands Index*. Disponible en: [https://index.openhands.dev/](https://index.openhands.dev/)
[51] SWE-bench. *SWE-bench Leaderboards*. Disponible en: [https://www.swebench.com/](https://www.swebench.com/)
[52] OpenHands. *Analyzing and Improving the OpenHands Index | Feb 20, 2026*. Disponible en: [https://openhands.dev/blog/analyzing-and-improving-openhands-index](https://openhands.dev/blog/analyzing-and-improving-openhands-index)
[53] Reddit. *OpenHands-LM 32B - 37.2% verified resolve rate on SWE- ...*. Disponible en: [https://www.reddit.com/r/LocalLLaMA/comments/1jocz51/openhandslm_32b_372_verified_resolve_rate_on/](https://www.reddit.com/r/LocalLLaMA/comments/1jocz51/openhandslm_32b_372_verified_resolve_rate_on/)
[54] GitHub. *OpenHands/benchmarks: Evaluation harness for ...*. Disponible en: [https://github.com/OpenHands/benchmarks](https://github.com/OpenHands/benchmarks)
[55] GitHub. *OpenHands model performance data · Issue #7479*. Disponible en: [https://github.com/OpenHands/OpenHands/issues/7479](https://github.com/OpenHands/OpenHands/issues/7479)
[56] OpenHands. *OpenHands | The Open Platform for Cloud Coding Agents*. Disponible en: [https://openhands.dev/](https://openhands.dev/)
[57] OpenHands. *Programmatically Access Coding Agents with the OpenHands Cloud ...*. Disponible en: [https://openhands.dev/blog/programmatically-access-coding-agents-with-the-openhands-cloud-api](https://openhands.dev/blog/programmatically-access-coding-agents-with-the-openhands-cloud-api)
[58] OpenHands Docs. *Cloud API*. Disponible en: [https://docs.openhands.dev/openhands/usage/cloud/cloud-api](https://docs.openhands.dev/openhands/usage/cloud/cloud-api)
[59] GitHub. *[PRD] Authenticate via OpenHands to get LLM key #204*. Disponible en: [https://github.com/All-Hands-AI/OpenHands-Cloud/issues/204](https://github.com/All-Hands-AI/OpenHands-Cloud/issues/204)
[60] OpenHands Docs. *openhands.sdk.llm*. Disponible en: [https://docs.openhands.dev/sdk/api-reference/openhands.sdk.llm](https://docs.openhands.dev/sdk/api-reference/openhands.sdk.llm)
[61] OpenHands Docs. *API-based Sandbox*. Disponible en: [https://docs.openhands.dev/sdk/guides/agent-server/api-sandbox](https://docs.openhands.dev/sdk/guides/agent-server/api-sandbox)
[62] OpenHands. *OpenHands Pricing | Start Building for Free*. Disponible en: [https://openhands.dev/pricing](https://openhands.dev/pricing)
[63] OpenHands. *OpenHands | The Open Platform for Cloud Coding Agents*. Disponible en: [https://openhands.dev/](https://openhands.dev/)
[64] OpenHands. *Introducing the OpenHands Index | Jan 28, 2026*. Disponible en: [https://openhands.dev/blog/openhands-index](https://openhands.dev/blog/openhands-index)
[65] GitHub. *OpenHands/tests/unit/README.md at main*. Disponible en: [https://github.com/OpenHands/OpenHands/blob/main/tests/unit/README.md](https://github.com/OpenHands/OpenHands/blob/main/tests/unit/README.md)
[66] LinkedIn. *Using OpenHands to Improve your Test Coverage*. Disponible en: [https://www.linkedin.com/pulse/using-openhands-improve-your-test-coverage-tim-o-farrell-b3usc](https://www.linkedin.com/pulse/using-openhands-improve-your-test-coverage-tim-o-farrell-b3usc)
[67] OpenHands. *Analyzing and Improving the OpenHands Index | Feb 20, 2026*. Disponible en: [https://openhands.dev/blog/analyzing-and-improving-openhands-index](https://openhands.dev/blog/analyzing-and-improving-openhands-index)
[68] OpenHands. *Learning to Verify AI-Generated Code | Mar 05, 2026*. Disponible en: [https://openhands.dev/blog/20260305-learning-to-verify-ai-generated-code](https://openhands.dev/blog/20260305-learning-to-verify-ai-generated-code)
[69] OpenHands Docs. *Security & Action Confirmation*. Disponible en: [https://docs.openhands.dev/sdk/guides/security](https://docs.openhands.dev/sdk/guides/security)
[70] OpenHands. *Using OpenHands to Improve your Test Coverage*. Disponible en: [https://openhands.dev/blog/using-openhands-to-improve-your-test-coverage](https://openhands.dev/blog/using-openhands-to-improve-your-test-coverage)
[71] GitHub. *Releases · OpenHands/OpenHands*. Disponible en: [https://github.com/OpenHands/OpenHands/releases](https://github.com/OpenHands/OpenHands/releases)
[72] YouTube. *OpenHands v1: Our Biggest Release Yet (Coming Soon)*. Disponible en: [https://www.youtube.com/watch?v=6lk5_rBE6Qo](https://www.youtube.com/watch?v=6lk5_rBE6Qo)
[73] GitHub. *Releases · OpenHands/software-agent-sdk*. Disponible en: [https://github.com/OpenHands/software-agent-sdk/releases](https://github.com/OpenHands/software-agent-sdk/releases)
[74] OpenHands. *Announcing All Hands Online (Beta) | Nov 12, 2025*. Disponible en: [https://openhands.dev/blog/announcing-all-hands-online-beta](https://openhands.dev/blog/announcing-all-hands-online-beta)
[75] PyPI. *openhands-ai*. Disponible en: [https://pypi.org/project/openhands-ai/](https://pypi.org/project/openhands-ai/)
[76] Yahoo Finance. *OpenHands Raises $18.8M Series A to Bring Open-Source Cloud ...*. Disponible en: [https://finance.yahoo.com/news/openhands-raises-18-8m-series-170000780.html](https://finance.yahoo.com/news/openhands-raises-18-8m-series-170000780.html)
[77] OpenHands Docs. *OpenHands in Your SDLC*. Disponible en: [https://docs.openhands.dev/openhands/usage/essential-guidelines/sdlc-integration](https://docs.openhands.dev/openhands/usage/essential-guidelines/sdlc-integration)
[78] OpenHands Docs. *Overview - SDK Arch*. Disponible en: [https://docs.openhands.dev/sdk/arch/overview](https://docs.openhands.dev/sdk/arch/overview)
[79] OpenHands. *The Path to OpenHands v1 | Nov 12, 2025*. Disponible en: [https://openhands.dev/blog/the-path-to-openhands-v1](https://openhands.dev/blog/the-path-to-openhands-v1)
[80] G2. *Top 10 OpenHands Alternatives & Competitors in 2026*. Disponible en: [https://www.g2.com/products/openhands/competitors/alternatives](https://www.g2.com/products/openhands/competitors/alternatives)
[81] CreateAIagent.net. *OpenHands Alternatives in 2026*. Disponible en: [https://createaiagent.net/alternatives/openhands/](https://createaiagent.net/alternatives/openhands/)
[82] X. *I tried EVERY major AI Coding tool so you don\'t have to. Here\'s what ...*. Disponible en: [https://x.com/henrythe9ths/status/1889381891373146421](https://x.com/henrythe9ths/status/1889381891373146421)
[83] Reddit. *Why has no one been talking about Open Hands so far?*. Disponible en: [https://www.reddit.com/r/LocalLLaMA/comments/1ksfos8/why_has_no_one_been_talking_about_open_hands_so/](https://www.reddit.com/r/LocalLLaMA/comments/1ksfos8/why_has_no_one_been_talking_about_open_hands_so/)
[84] SourceForge. *OpenHands vs. SWE-agent Comparison*. Disponible en: [https://sourceforge.net/software/compare/OpenHands-vs-SWE-agent/](https://sourceforge.net/software/compare/OpenHands-vs-SWE-agent/)
[85] Modal. *Open-source AI agents*. Disponible en: [https://modal.com/blog/open-ai-agents](https://modal.com/blog/open-ai-agents)
[86] Toolhalla.ai. *Devin vs OpenHands vs SWE-agent: Top AI Coding Agents 2026*. Disponible en: [https://toolhalla.ai/blog/devin-vs-openhands-vs-swe-agent-2026](https://toolhalla.ai/blog/devin-vs-openhands-vs-swe-agent-2026)
[87] OpenHands. *OpenHands | The Open Platform for Cloud Coding Agents*. Disponible en: [https://openhands.dev/](https://openhands.dev/)
[88] Medium. *OpenHands: Write code without writing a single line of code*. Disponible en: [https://medium.com/@venku.buragadda/openhands-write-code-without-writing-a-single-line-of-code-9f2fde3dfdae](https://medium.com/@venku.buragadda/openhands-write-code-without-writing-a-single-line-of-code-9f2fde3dfdae)
[89] AMD. *Local AI for Developers OpenHands AMD Bring Coding ...*. Disponible en: [https://www.amd.com/en/developer/resources/technical-articles/2025/OpenHands.html](https://www.amd.com/en/developer/resources/technical-articles/2025/OpenHands.html)
[90] OpenHands Docs. *openhands.sdk.llm*. Disponible en: [https://docs.openhands.dev/sdk/api-reference/openhands.sdk.llm](https://docs.openhands.dev/sdk/api-reference/openhands.sdk.llm)
[91] OpenHands. *OpenHands CLI | Secure, Scalable Agentic Software ...*. Disponible en: [https://openhands.dev/product/cli](https://openhands.dev/product/cli)
[92] Amplifilabs. *OpenHands: The Open-Source Leap for Agentic AI Coding*. Disponible en: [https://www.amplifilabs.com/post/openhands-the-open-source-leap-for-agentic-ai-coding](https://www.amplifilabs.com/post/openhands-the-open-source-leap-for-agentic-ai-coding)
[93] OpenHands Docs. *Overview - Skills*. Disponible en: [https://docs.openhands.dev/overview/skills](https://docs.openhands.dev/overview/skills)
[94] Hugging Face. *OpenHands/openhands-feedback · Datasets at ...*. Disponible en: [https://huggingface.co/datasets/OpenHands/openhands-feedback](https://huggingface.co/datasets/OpenHands/openhands-feedback)
[95] OpenHands Docs. *Community*. Disponible en: [https://docs.openhands.dev/overview/community](https://docs.openhands.dev/overview/community)
[96] Comparateur-IA. *Review of OpenHands (2026)*. Disponible en: [https://comparateur-ia.com/en/reviews/openhands](https://comparateur-ia.com/en/reviews/openhands)
[97] Medium. *Exploring OpenHands — An Open-Source AI Developer ...*. Disponible en: [https://medium.com/@niarsdet/redefining-dev-workflows-exploring-openhands-an-open-source-ai-developer-agent-4d579c6e5f40](https://medium.com/@niarsdet/redefining-dev-workflows-exploring-openhands-an-open-source-ai-developer-agent-4d579c6e5f40)
[98] Sider.ai. *Can This Open-Source \'AI Developer\' Really Ship Code?*. Disponible en: [https://sider.ai/blog/ai-tools/ai-openhands-review-can-this-open-source-ai-developer-really-ship-code](https://sider.ai/blog/ai-tools/ai-openhands-review-can-this-open-source-ai-developer-really-ship-code)
[99] LocalAIMaster. *OpenHands vs SWE-Agent: AI Coding Agents Compared*. Disponible en: [https://localaimaster.com/blog/openhands-vs-swe-agent](https://localaimaster.com/blog/openhands-vs-swe-agent)
[100] VibeCoding.app. *OpenHands Review (2026): 70K Stars. Worth the Setup?*. Disponible en: [https://vibecoding.app/blog/openhands-review](https://vibecoding.app/blog/openhands-review)
[101] OpenHands. *OpenHands Pricing | Start Building for Free*. Disponible en: [https://openhands.dev/pricing](https://openhands.dev/pricing)
[102] VPSRanking. *OpenHands - Features, Pricing & Review [AI Agent (Coding)]*. Disponible en: [https://vpsranking.com/ai/openhands/](https://vpsranking.com/ai/openhands/)
[103] Comparateur-IA. *OpenHands Review (2026): Pricing, Pros + Free Trial*. Disponible en: [https://comparateur-ia.com/en/ai-tools/openhands](https://comparateur-ia.com/en/ai-tools/openhands)
[104] OpenHands. *OpenHands Product Update - March 2026*. Disponible en: [https://openhands.dev/blog/openhands-product-update---march-2026](https://openhands.dev/blog/openhands-product-update---march-2026)
[105] LinkedIn. *OpenHands\' Post*. Disponible en: [https://www.linkedin.com/posts/openhands-ai_we-just-made-a-huge-pricing-update-to-make-activity-7374879523332370432-0c7g](https://www.linkedin.com/posts/openhands-ai_we-just-made-a-huge-pricing-update-to-make-activity-7374879523332370432-0c7g)
[106] TechCrunch. *How OpenAI and Google see AI changing go-to-market strategies*. Disponible en: [https://techcrunch.com/2025/11/28/how-openai-and-google-see-ai-changing-go-to-market-strategies/](https://techcrunch.com/2025/11/28/how-openai-and-google-see-ai-changing-go-to-market-strategies/)
[107] Salesforce. *Go-To-Market Strategy*. Disponible en: [https://www.salesforce.com/sales/go-to-market-strategy/](https://www.salesforce.com/sales/go-to-market-strategy/)
[108] Apple Podcasts. *How OpenHands built a four-buc… - BUILDERS*. Disponible en: [https://podcasts.apple.com/us/podcast/how-openhands-built-a-four-bucket-qualification/id1619104989?i=1000762177745](https://podcasts.apple.com/us/podcast/how-openhands-built-a-four-bucket-qualification/id1619104989?i=1000762177745)
[109] GitHub. *OpenHands/benchmarks: Evaluation harness for ...*. Disponible en: [https://github.com/OpenHands/benchmarks](https://github.com/OpenHands/benchmarks)
[110] OpenHands. *Introducing the OpenHands Index | Jan 28, 2026*. Disponible en: [https://openhands.dev/blog/openhands-index](https://openhands.dev/blog/openhands-index)
[111] OpenHands. *Analyzing and Improving the OpenHands Index | Feb 20, 2026*. Disponible en: [https://openhands.dev/blog/analyzing-and-improving-openhands-index](https://openhands.dev/blog/analyzing-and-improving-openhands-index)
[112] VMblog. *Benchmarking LLMs for cost, accuracy, and ROI with the ...*. Disponible en: [https://vmblog.com/qa/benchmarking-llms-for-cost-accuracy-and-roi-with-the-openhands-index/](https://vmblog.com/qa/benchmarking-llms-for-cost-accuracy-and-roi-with-the-openhands-index/)
[113] EmergentMind. *OpenHands-Perf-Agent: Optimizing Performance Bugs*. Disponible en: [https://www.emergentmind.com/topics/openhands-perf-agent](https://www.emergentmind.com/topics/openhands-perf-agent)
[114] OpenHands. *Mitigating Prompt Injection Attacks in Software Agents*. Disponible en: [https://openhands.dev/blog/mitigating-prompt-injection-attacks-in-software-agents](https://openhands.dev/blog/mitigating-prompt-injection-attacks-in-software-agents)
[115] OpenReview. *AgentXploit: End-to-End Red-Teaming for AI Agents ...*. Disponible en: [https://openreview.net/forum?id=xKJ0lVQEv7](https://openreview.net/forum?id=xKJ0lVQEv7)
[116] YCombinator. *AI Agent Security: A curated list of tools for red teaming and ...*. Disponible en: [https://news.ycombinator.com/item?id=46235141](https://news.ycombinator.com/item?id=46235141)
[117] OpenHands Docs. *Security*. Disponible en: [https://docs.openhands.dev/sdk/arch/security](https://docs.openhands.dev/sdk/arch/security)
