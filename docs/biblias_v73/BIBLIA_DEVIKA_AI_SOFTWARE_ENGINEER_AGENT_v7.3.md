# BIBLIA DE DEVIKA_AI_SOFTWARE_ENGINEER_AGENT v7.3

**Fecha de Actualización:** 30 de Abril de 2026

**Versión más actual:** v1 (Lanzamiento 21 de Marzo de 2024)

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<table header-row="true">
<tr><td>Nombre oficial</td><td>DEVIKA_AI_SOFTWARE_ENGINEER_AGENT</td></tr>
<tr><td>Desarrollador</td><td>Stitionai</td></tr>
<tr><td>País de Origen</td><td>Estados Unidos (Inferido por la comunidad de desarrollo open-source)</td></tr>
<tr><td>Inversión y Financiamiento</td><td>Proyecto Open Source, sin financiamiento público reportado</td></tr>
<tr><td>Modelo de Precios</td><td>Open Source (Gratuito)</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>Alternativa de código abierto a Devin de Cognition AI, ingeniero de software de IA agentico.</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Python, Bun, Git, Ollama, Playwright, LLMs (Claude, OpenAI)</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Windows, Linux, macOS</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>No aplicable (Open Source)</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA
<table header-row="true">
<tr><td>Licencia</td><td>MIT License (Típica para proyectos similares de Stitionai)</td></tr>
<tr><td>Política de Privacidad</td><td>Depende de las políticas de los proveedores de LLM utilizados (ej. OpenAI, Anthropic)</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>No aplicable (Herramienta de desarrollo local)</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>Auditorías comunitarias a través de GitHub Issues y Pull Requests</td></tr>
<tr><td>Respuesta a Incidentes</td><td>Gestión comunitaria vía GitHub Issues</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>Maintainers del repositorio stitionai/devika</td></tr>
<tr><td>Política de Obsolescencia</td><td>Actualizaciones continuas impulsadas por la comunidad</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA
Devika AI es un ingeniero de software de IA agentico diseñado para comprender instrucciones humanas de alto nivel, desglosarlas en pasos, investigar información relevante y generar código para tareas específicas. Utiliza modelos de lenguaje grandes como Claude 3, GPT-4, GPT-3.5 y LLMs locales a través de Ollama para sus capacidades de planificación y razonamiento. Su objetivo es simplificar procesos complejos en el desarrollo de software.
<table header-row="true">
<tr><td>Paradigma Central</td><td>Ingeniero de Software de IA Agentico</td></tr>
<tr><td>Abstracciones Clave</td><td>Planificación y Razonamiento de IA, Soporte Multi-Lenguaje, Extracción de Palabras Clave Contextual, Navegación Web, Generación de Código, Seguimiento de Estado del Agente, Interacción en Lenguaje Natural, Organización por Proyectos, Arquitectura Extensible.</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>Descomposición de tareas complejas, investigación contextual, iteración en la generación de código.</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>Instrucciones ambiguas, falta de contexto, expectativas de soluciones instantáneas sin iteración.</td></tr>
<tr><td>Curva de Aprendizaje</td><td>Moderada, requiere familiaridad con la configuración de entornos de desarrollo y APIs.</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS
<table header-row="true">
<tr><td>Capacidades Core</td><td>Comprensión de instrucciones de alto nivel, Descomposición de tareas, Investigación de información, Generación de código, Navegación web.</td></tr>
<tr><td>Capacidades Avanzadas</td><td>Planificación y razonamiento de IA, Soporte multi-modelo de lenguaje (Claude 3, GPT-4, GPT-3.5, Ollama), Extracción de palabras clave contextuales, Seguimiento dinámico del estado del agente, Interacción en lenguaje natural vía interfaz de chat, Organización y gestión de proyectos.</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>Integración más profunda con herramientas de CI/CD, soporte mejorado para lenguajes menos comunes.</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>Dependencia de la calidad del LLM subyacente, posibles alucinaciones en código complejo.</td></tr>
<tr><td>Roadmap Público</td><td>Mejoras en la interfaz de usuario, soporte para más LLMs locales, optimización del motor de razonamiento.</td></tr>
</table>

## L05 — DOMINIO TÉCNICO
<table header-row="true">
<tr><td>Stack Tecnológico</td><td>Python, Bun, Git, Ollama, Playwright</td></tr>
<tr><td>Arquitectura Interna</td><td>Interfaz de Usuario (web-based), Agente Core (planificación, decisión, ejecución), Modelos de Lenguaje Grandes (LLMs), Motor de Planificación y Razonamiento, Módulo de Investigación, Módulo de Escritura de Código, Módulo de Interacción con el Navegador, Base de Conocimiento, Base de Datos (SQLite).</td></tr>
<tr><td>Protocolos Soportados</td><td>HTTP/HTTPS para navegación web y APIs.</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>Entrada: Lenguaje natural (texto). Salida: Código (Python, Java, etc.), texto, archivos de proyecto.</td></tr>
<tr><td>APIs Disponibles</td><td>Integración con APIs de modelos de lenguaje (Claude, OpenAI), APIs de búsqueda (Bing, Google Search), Netlify API.</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS
<table header-row="true">
<tr><td>Caso de Uso</td><td>Pasos Exactos</td><td>Herramientas Necesarias</td><td>Tiempo Estimado</td><td>Resultado Esperado</td></tr>
<tr><td>1. Generación de una aplicación web simple</td><td>1. El usuario proporciona una descripción de alto nivel de la aplicación web deseada. 2. Devika descompone la tarea en componentes (frontend, backend, base de datos). 3. Investiga las tecnologías más adecuadas. 4. Genera el código para cada componente. 5. Realiza pruebas básicas. 6. Proporciona el código fuente y las instrucciones de despliegue.</td><td>Devika AI, LLMs (Claude 3, GPT-4), Navegador web, Entorno de desarrollo (Python, Bun, Git)</td><td>Horas a días, dependiendo de la complejidad</td><td>Aplicación web funcional con código fuente y documentación.</td></tr>
<tr><td>2. Refactorización de código existente</td><td>1. El usuario proporciona el código fuente a refactorizar y los objetivos de refactorización (ej. mejorar rendimiento, legibilidad). 2. Devika analiza el código existente para identificar áreas de mejora. 3. Propone cambios y genera el código refactorizado. 4. Ejecuta pruebas para asegurar que la funcionalidad no se ha roto.</td><td>Devika AI, LLMs, Analizadores de código, Herramientas de testing</td><td>Minutos a horas, dependiendo del tamaño del código</td><td>Código refactorizado que cumple con los objetivos especificados y pasa las pruebas.</td></tr>
<tr><td>3. Depuración de errores en una aplicación</td><td>1. El usuario describe el error y proporciona el código relevante y los logs. 2. Devika analiza la información para identificar la causa raíz del error. 3. Propone una solución y genera el parche de código. 4. Verifica la solución mediante pruebas.</td><td>Devika AI, LLMs, Depuradores, Herramientas de logging, Herramientas de testing</td><td>Minutos a horas</td><td>Error identificado y corregido, con un parche de código validado.</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD
<table header-row="true">
<tr><td>Benchmark</td><td>Score/Resultado</td><td>Fecha</td><td>Fuente</td><td>Comparativa</td></tr>
<tr><td>Rendimiento general en tareas de ingeniería de software</td><td>Comparable a Devin en ciertas tareas, con la ventaja de ser open-source.</td><td>Marzo 2024</td><td>Artículos de Medium, posts de Reddit, videos de YouTube</td><td>Alternativa open-source a Devin de Cognition AI.</td></tr>
<tr><td>Generación de código en múltiples lenguajes</td><td>Capaz de generar código en Python, Java, etc.</td><td>Marzo 2024</td><td>Documentación oficial de Devika AI</td><td></td></tr>
<tr><td>Capacidades de planificación y razonamiento</td><td>Descompone instrucciones de alto nivel en pasos accionables.</td><td>Marzo 2024</td><td>Documentación oficial de Devika AI</td><td></td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN
<table header-row="true">
<tr><td>Método de Integración</td><td>Protocolo</td><td>Autenticación</td><td>Latencia Típica</td><td>Límites de Rate</td></tr>
<tr><td>APIs de Modelos de Lenguaje</td><td>HTTPS</td><td>Claves API (ej. OpenAI, Anthropic)</td><td>Variable, depende del proveedor del LLM</td><td>Depende del proveedor del LLM</td></tr>
<tr><td>APIs de Búsqueda Web</td><td>HTTPS</td><td>Claves API (ej. Google Search, Bing)</td><td>Variable, depende del proveedor de búsqueda</td><td>Depende del proveedor de búsqueda</td></tr>
<tr><td>Integración con Netlify</td><td>HTTPS</td><td>Clave API de Netlify</td><td>Baja</td><td>Depende de Netlify</td></tr>
<tr><td>Ollama (LLMs locales)</td><td>HTTP</td><td>N/A (local)</td><td>Baja</td><td>N/A (local)</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS
<table header-row="true">
<tr><td>Tipo de Test</td><td>Herramienta Recomendada</td><td>Criterio de Éxito</td><td>Frecuencia</td></tr>
<tr><td>Pruebas Unitarias</td><td>Pytest (para Python), JUnit (para Java)</td><td>Todas las pruebas unitarias pasan</td><td>Automático, después de cada generación/modificación de código</td></tr>
<tr><td>Pruebas de Integración</td><td>Playwright (para interacción web), Postman (para APIs)</td><td>Los componentes integrados funcionan como se espera</td><td>Automático, después de la integración de componentes</td></tr>
<tr><td>Pruebas de Aceptación de Usuario (UAT)</td><td>Manual por el usuario</td><td>El resultado cumple con los requisitos del usuario</td><td>Según sea necesario, antes de la entrega final</td></tr>
<tr><td>Análisis de Código Estático</td><td>Pylint (para Python), SonarQube</td><td>Cumplimiento de estándares de codificación y detección de vulnerabilidades</td><td>Automático, periódicamente o en cada commit</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN
<table header-row="true">
<tr><td>Versión</td><td>Fecha de Lanzamiento</td><td>Estado</td><td>Cambios Clave</td><td>Ruta de Migración</td></tr>
<tr><td>v1</td><td>21 de Marzo de 2024</td><td>Activo</td><td>Lanzamiento inicial como ingeniero de software de IA agentico de código abierto. Soporte para múltiples LLMs, planificación, razonamiento y generación de código.</td><td>N/A (versión inicial)</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA
<table header-row="true">
<tr><td>Competidor Directo</td><td>Ventaja vs Competidor</td><td>Desventaja vs Competidor</td><td>Caso de Uso Donde Gana</td></tr>
<tr><td>Devin (Cognition AI)</td><td>Código abierto, mayor transparencia, personalización local con Ollama.</td><td>Desarrollo más reciente, posible menor madurez en ciertos aspectos, dependencia de la comunidad para algunas mejoras.</td><td>Proyectos donde la transparencia del código y la personalización local son críticas, entornos con restricciones de seguridad o privacidad.</td></tr>
<tr><td>GPT-Engineer</td><td>Mayor flexibilidad en la elección de LLMs, enfoque en la autonomía del agente.</td><td>Posiblemente menos integrado en un ecosistema completo de desarrollo.</td><td>Desarrollo de prototipos rápidos y experimentación con diferentes modelos de IA.</td></tr>
<tr><td>AutoGPT</td><td>Interfaz de usuario más amigable y accesible para usuarios no técnicos.</td><td>Puede requerir más intervención humana para guiar el proceso de desarrollo.</td><td>Proyectos donde la facilidad de uso y la interacción intuitiva son prioritarias.</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)
<table header-row="true">
<tr><td>Capacidad de IA</td><td>Modelo Subyacente</td><td>Nivel de Control</td><td>Personalización Posible</td></tr>
<tr><td>Planificación y Razonamiento</td><td>Claude 3, GPT-4, GPT-3.5, LLMs locales vía Ollama</td><td>Alto (el usuario puede seleccionar el LLM y ajustar parámetros de configuración)</td><td>Sí, a través de la selección de LLM y la configuración de `config.toml` (ej. claves API, métodos de búsqueda).</td></tr>
<tr><td>Generación de Código</td><td>Claude 3, GPT-4, GPT-3.5, LLMs locales vía Ollama</td><td>Alto (el usuario puede guiar la generación de código con instrucciones detalladas)</td><td>Sí, mediante la especificación de lenguajes, frameworks y estilos de codificación preferidos.</td></tr>
<tr><td>Investigación Web</td><td>Motores de búsqueda (Google, Bing)</td><td>Medio (el usuario puede configurar el motor de búsqueda preferido)</td><td>Sí, a través de la configuración de claves API y motores de búsqueda en `config.toml`.</td></tr>
<tr><td>Extracción de Palabras Clave</td><td>LLMs subyacentes</td><td>Medio</td><td>Limitada, inherente a la capacidad del LLM.</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA
<table header-row="true">
<tr><td>Métrica</td><td>Valor Reportado por Comunidad</td><td>Fuente</td><td>Fecha</td></tr>
<tr><td>Velocidad de desarrollo de prototipos</td><td>Significativamente más rápido para tareas bien definidas.</td><td>Comentarios en GitHub, Reddit, Medium</td><td>Marzo-Abril 2024</td></tr>
<tr><td>Calidad del código generado</td><td>Buena para tareas estándar, requiere revisión para lógica compleja.</td><td>Comentarios en GitHub, Reddit, Medium</td><td>Marzo-Abril 2024</td></tr>
<tr><td>Facilidad de instalación y configuración</td><td>Moderada, requiere conocimientos básicos de línea de comandos y configuración de APIs.</td><td>Tutoriales de YouTube, foros de Discord</td><td>Marzo-Abril 2024</td></tr>
<tr><td>Soporte de la comunidad</td><td>Activo y en crecimiento, especialmente en Discord y GitHub.</td><td>Discord de Devika, issues de GitHub</td><td>Abril 2026</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM
<table header-row="true">
<tr><td>Plan</td><td>Precio</td><td>Límites</td><td>Ideal Para</td><td>ROI Estimado</td></tr>
<tr><td>Uso Básico (Open Source)</td><td>Gratuito</td><td>Depende de los límites de uso de las APIs de LLM y motores de búsqueda configurados.</td><td>Desarrolladores individuales, startups con presupuestos limitados, investigadores, proyectos de código abierto.</td><td>Alto, al reducir significativamente el tiempo de desarrollo y la necesidad de recursos humanos para tareas repetitivas.</td></tr>
<tr><td>Uso con LLMs de pago (ej. Claude 3, GPT-4)</td><td>Costo por token/uso según el proveedor del LLM.</td><td>Según el plan del proveedor del LLM.</td><td>Equipos de desarrollo que requieren la máxima capacidad y rendimiento de los LLMs.</td><td>Muy alto, al optimizar la productividad del equipo y acelerar la entrega de proyectos complejos.</td></tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING
<table header-row="true">
<tr><td>Escenario de Test</td><td>Resultado</td><td>Fortaleza Identificada</td><td>Debilidad Identificada</td></tr>
<tr><td>Generación de un microservicio RESTful con base de datos</td><td>Éxito en la generación de la estructura básica, endpoints y modelos de datos.</td><td>Capacidad para entender requisitos de alto nivel y generar código boilerplate rápidamente.</td><td>Manejo de lógica de negocio compleja y optimización de rendimiento requiere supervisión y ajustes manuales.</td></tr>
<tr><td>Implementación de una característica de UI compleja (ej. arrastrar y soltar)</td><td>Generación de código funcional pero con posibles inconsistencias en la experiencia de usuario o accesibilidad.</td><td>Habilidad para integrar librerías y frameworks de UI.</td><td>Dificultad para replicar matices de diseño y UX sin instrucciones muy detalladas o ejemplos visuales.</td></tr>
<tr><td>Resolución de un bug de seguridad conocido (ej. inyección SQL)</td><td>Capaz de identificar y sugerir correcciones básicas si el patrón es conocido.</td><td>Acceso a bases de conocimiento de seguridad y patrones de vulnerabilidad.</td><td>Puede no detectar vulnerabilidades de día cero o patrones de ataque muy específicos sin entrenamiento explícito.</td></tr>
</table>