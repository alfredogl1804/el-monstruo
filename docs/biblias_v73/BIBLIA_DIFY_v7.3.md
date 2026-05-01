# BIBLIA DE DIFY v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<table header-row="true">
<tr><td>Nombre oficial</td><td>Dify</td></tr>
<tr><td>Desarrollador</td><td>Langenius (según LinkedIn y GitHub)</td></tr>
<tr><td>País de Origen</td><td>China (origen de la fundación), con operaciones en EE. UU. (Delaware)</td></tr>
<tr><td>Inversión y Financiamiento</td><td>Serie Pre-A de $30 millones (Marzo 2026), Private Seed.</td></tr>
<tr><td>Modelo de Precios</td><td>Ofrece un plan gratuito y un plan 'Professional' de $59/workspace/mes (según dify.ai/pricing)</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>Plataforma de código abierto y LLMOps para construir, desplegar y gestionar aplicaciones nativas de IA, flujos de trabajo agenticos, RAG pipelines, integraciones y observabilidad. Se posiciona como una herramienta para democratizar el desarrollo de agentes de IA, con un fuerte enfoque en soluciones no-code/low-code y despliegue en producción.</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Modular, con Dify API (Flask backend) y otros servicios. Integración con bases de datos como YugabyteDB.</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Compatible con diversos LLMs (ej. GPT-4, Ollama) y herramientas (ej. Google Search, DALL·E, Stable Diffusion, WolframAlpha). Consideraciones de compatibilidad para dependencias de terceros.</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>No se encuentran SLOs públicos definidos formalmente para la versión de código abierto.</td></tr>
</table>
## L02 — GOBERNANZA Y MODELO DE CONFIANZA
<table header-row="true">
<tr><td>Licencia</td><td>Dify Community Edition: Licencia Apache 2.0 modificada con condiciones adicionales. Dify Enterprise: Licencia comercial de pago.</td></tr>
<tr><td>Política de Privacidad</td><td>Disponible en su sitio web oficial y en los documentos de sus versiones legacy. Directrices para desarrolladores de plugins sobre políticas de privacidad.</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>SOC 2 Tipo II, ISO 27001:2022, GDPR (certificaciones obtenidas por segundo año consecutivo a marzo de 2026).</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>Certificaciones SOC 2 Tipo II e ISO 27001:2022 confirman auditorías regulares y cumplimiento continuo en seguridad de datos, disponibilidad, integridad, confidencialidad y privacidad.</td></tr>
<tr><td>Respuesta a Incidentes</td><td>Las certificaciones SOC 2 e ISO 27001 implican la existencia de procesos robustos de respuesta a incidentes, aunque los detalles específicos no son públicos.</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>No hay información pública específica sobre una matriz de autoridad de decisión. Se infiere que sigue un modelo de gobernanza interna estándar para empresas de software.</td></tr>
<tr><td>Política de Obsolescencia</td><td>No se encontró información pública específica sobre una política de obsolescencia.</td></tr>
</table>
## L03 — MODELO MENTAL Y MAESTRÍA

Dify se posiciona como una plataforma integral para el desarrollo de aplicaciones de IA, facilitando la creación de agentes autónomos y flujos de trabajo complejos. Su diseño se centra en la orquestación de IA y las operaciones de modelos de lenguaje (LLMOps), buscando democratizar el acceso a la construcción de soluciones de IA mediante enfoques no-code y low-code. Esto permite a los desarrolladores y equipos enfocarse en la lógica de negocio y la experiencia del usuario, abstraer la complejidad subyacente de los modelos de IA.

<table header-row="true">
<tr><td>Paradigma Central</td><td>Construcción de aplicaciones agenticas de IA, orquestación de IA, LLMOps, desarrollo no-code/low-code para la creación y gestión de flujos de trabajo inteligentes.</td></tr>
<tr><td>Abstracciones Clave</td><td>**Nodos:** Componentes fundamentales de un flujo de trabajo que representan tareas o funciones específicas. **Variables:** Mecanismos para conectar las entradas y salidas entre nodos, permitiendo el flujo de datos. **RAG Engine:** Motor de Generación Aumentada por Recuperación para mejorar la relevancia y precisión de las respuestas de los LLMs. **Plugins:** Extensiones que añaden funcionalidades y herramientas externas. **Arquitectura Modular (Beehive):** Permite que cada módulo funcione de manera independiente, mejorando la flexibilidad y escalabilidad.</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>**Diseño de Prompts como Especificaciones de Producto:** Tratar los prompts como requisitos de ingeniería para asegurar salidas estables y estructuradas. **Construcción Visual de Flujos de Trabajo:** Utilizar la interfaz de arrastrar y soltar para diseñar y orquestar lógicas complejas de agentes de IA. **Iteración Basada en Datos:** Recopilar y analizar insights para refinar y optimizar continuamente las aplicaciones de IA. **Modularidad:** Descomponer problemas complejos en componentes más pequeños y manejables (nodos, plugins).</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>**Complejidad Innecesaria en el Código:** Aunque Dify soporta código, el abuso de lógica compleja que podría ser gestionada visualmente o con configuraciones, va en contra de su filosofía no-code/low-code. **Falta de Modularidad:** Crear flujos de trabajo monolíticos que dificultan el mantenimiento y la escalabilidad. **Dependencia Excesiva de un Solo Modelo:** No aprovechar la compatibilidad de Dify con múltiples LLMs y herramientas, limitando la flexibilidad y resiliencia. **Ignorar la Observabilidad:** No monitorear y analizar el rendimiento de las aplicaciones de IA en producción.</td></tr>
<tr><td>Curva de Aprendizaje</td><td>**Baja para Conceptos Básicos:** La interfaz visual de arrastrar y soltar permite a usuarios con poca experiencia en programación construir aplicaciones de IA rápidamente. **Moderada para Agentes Complejos:** La creación de agentes autónomos avanzados, la integración de plugins personalizados y la optimización de RAG pipelines requieren una comprensión más profunda de los conceptos de IA y las capacidades de la plataforma.</td></tr>
</table>
## L04 — CAPACIDADES TÉCNICAS
<table header-row="true">
<tr><td>Capacidades Core</td><td>
<ul>
<li>**Orquestación Visual de LLM:** Interfaz de arrastrar y soltar para construir flujos de trabajo de IA.</li>
<li>**Desarrollo de Agentes:** Creación, despliegue y gestión de agentes autónomos de IA.</li>
<li>**RAG Pipelines:** Implementación de Generación Aumentada por Recuperación para mejorar la precisión y relevancia de las respuestas.</li>
<li>**Integraciones:** Conexión con diversas herramientas y modelos de IA (ej. Google Search, DALL·E, Stable Diffusion, WolframAlpha, Ollama).</li>
<li>**LLMOps:** Funcionalidades para monitorear, analizar y entrenar aplicaciones de LLM en producción.</li>
<li>**Gestión de Prompts:** Herramientas para diseñar, probar y optimizar prompts.</li>
<li>**Despliegue en Producción:** Soporte para desplegar aplicaciones de IA listas para producción.</li>
</ul>
</td></tr>
<tr><td>Capacidades Avanzadas</td><td>
<ul>
<li>**Modo Experto en Orquestación de Prompts:** Control y personalización avanzados para desarrolladores profesionales.</li>
<li>**Sistema de Plugins:** Permite extender la funcionalidad de Dify con plugins personalizados y de terceros.</li>
<li>**Arquitectura Modular (Beehive):** Facilita la flexibilidad y escalabilidad al permitir que los módulos operen de forma independiente.</li>
<li>**Debugging en Tiempo Real:** Herramientas para identificar y resolver problemas en los flujos de trabajo de IA.</li>
<li>**Auto-escalado de Infraestructura:** Soporte para manejar el aumento de tráfico y necesidades cambiantes.</li>
<li>**Gestión de Datos Empresariales:** Seguridad de grado empresarial para datos críticos.</li>
</ul>
</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>
<ul>
<li>**Mejoras en la Estabilidad de Tareas con Grandes Volúmenes de Datos:** Optimización de sesiones de base de datos, ejecución de limpieza por lotes, ajuste de índices y limitación configurable entre lotes para retención (según GitHub releases).</li>
<li>**Ampliación del Ecosistema de Plugins:** Continuo desarrollo y expansión de plugins para diversas funcionalidades (ej. InfraNodus para Q&A avanzado, plugins SSH para gestión de servidores).</li>
<li>**Integración con Bases de Datos Vectoriales y Gráficas:** Soporte para arquitecturas unificadas de IA con bases de datos como YugabyteDB para GraphRAG.</li>
<li>**Nuevas Funcionalidades para Agentes de IA de Próxima Generación:** Eventos y discusiones en la comunidad sugieren un enfoque continuo en la mejora de las capacidades agenticas.</li>
</ul>
</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>
<ul>
<li>**Requisitos de Recursos:** Mínimo de CPU >= 2 Core y RAM >= 4 GiB para la instalación local.</li>
<li>**Problemas de Rendimiento en Auto-alojamiento:** Posibles problemas de lentitud y alto uso de CPU en contenedores worker y API si no se optimiza la configuración (según GitHub issues).</li>
<li>**Incompatibilidad de Arquitectura con Dependencias de Terceros:** La instalación de dependencias de terceros puede causar problemas de compatibilidad.</li>
<li>**SQL Lento en Plugins:** Problemas reportados con la lentitud de consultas SQL en plugins, incluso con PostgreSQL.</li>
</ul>
</td></tr>
<tr><td>Roadmap Público</td><td>El roadmap público no se presenta como un documento formal único, pero se puede inferir a través de: 
<ul>
<li>**Anuncios en el Blog de Dify:** Publicaciones sobre nuevas arquitecturas, lanzamientos de versiones y mejoras de características.</li>
<li>**Actividad en GitHub:** Lanzamientos de nuevas versiones, discusiones en issues y pull requests que indican el desarrollo futuro.</li>
<li>**Eventos y Foros de la Comunidad:** Discusiones sobre futuras funcionalidades y direcciones de desarrollo.</li>
<li>**Enfoque en Agentes de IA y RAG:** La dirección general apunta a la mejora continua de las capacidades de orquestación de IA, agentes y RAG.</li>
</ul>
</td></tr>
</table>
## L05 — DOMINIO TÉCNICO
<table header-row="true">
<tr><td>Stack Tecnológico</td><td>
<ul>
<li>**Backend:** Dify API (basado en Flask).</li>
<li>**Bases de Datos:** Integración con bases de datos relacionales y distribuidas como YugabyteDB y TiDB para escalabilidad y gestión de grandes volúmenes de datos.</li>
<li>**Almacenamiento de Objetos:** Soporte para múltiples proveedores de almacenamiento en la nube, incluyendo Opendal, AWS S3, Azure Blob Storage, Aliyun OSS, Google Cloud Storage, Huawei OBS, Volcengine TOS, Tencent COS, Baidu OBS, OCI Storage y Supabase.</li>
<li>**Contenedores:** Despliegue a menudo mediante Docker (para auto-alojamiento).</li>
<li>**Lenguajes:** Python es el lenguaje principal para el desarrollo de la plataforma y plugins.</li>
</ul>
</td></tr>
<tr><td>Arquitectura Interna</td><td>
<ul>
<li>**Arquitectura Modular (Beehive):** Un diseño desacoplado donde cada módulo (ej. API, worker, etc.) puede operar de forma independiente, mejorando la flexibilidad, escalabilidad y mantenibilidad.</li>
<li>**Plataforma LLMOps:** Integra Backend as a Service con capacidades de orquestación, observabilidad y gestión del ciclo de vida de las aplicaciones LLM.</li>
<li>**Motor de Orquestación de Flujos de Trabajo:** Permite la creación visual de lógicas complejas mediante nodos y variables.</li>
<li>**Motor RAG:** Componente dedicado para la Generación Aumentada por Recuperación, gestionando la indexación y recuperación de datos para los LLMs.</li>
<li>**Sistema de Plugins:** Permite la extensión de funcionalidades a través de módulos externos.</li>
</ul>
</td></tr>
<tr><td>Protocolos Soportados</td><td>
<ul>
<li>**Model Context Protocol (MCP):** Protocolo estandarizado para que los agentes de IA descubran y utilicen servidores externos, facilitando la integración de herramientas.</li>
<li>**HTTP/HTTPS:** Para la comunicación general de la API y la integración con servicios web externos.</li>
<li>**OpenAPI/Swagger:** Utilizado para definir y consumir APIs externas de manera estandarizada.</li>
</ul>
</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>
<ul>
<li>**Texto:** Formato principal para prompts, respuestas de LLMs y procesamiento de documentos.</li>
<li>**JSON:** Para la configuración de flujos de trabajo, datos estructurados de entrada/salida de nodos y respuestas de API.</li>
<li>**Imágenes:** Soporte implícito a través de integraciones con modelos de generación de imágenes (ej. DALL·E, Stable Diffusion).</li>
<li>**Documentos:** Procesamiento de diversos formatos de documentos para el motor RAG.</li>
<li>**Audio/Video:** Potencialmente soportado a través de plugins o integraciones con modelos multimodales.</li>
</ul>
</td></tr>
<tr><td>APIs Disponibles</td><td>
<ul>
<li>**Dify API:** Interfaz RESTful para interactuar con la plataforma, construir y gestionar aplicaciones de IA.</li>
<li>**API de Modelos:** Interfaz para integrar y utilizar diferentes modelos de IA.</li>
<li>**API de Herramientas:** Para la integración de herramientas externas y la creación de plugins.</li>
</ul>
</td></tr>
</table>
## L06 — PLAYBOOKS OPERATIVOS
<table header-row="true">
<tr><td>Caso de Uso</td><td>Pasos Exactos</td><td>Herramientas Necesarias</td><td>Tiempo Estimado</td><td>Resultado Esperado</td></tr>
<tr><td>**Creación de un Chatbot de Soporte al Cliente**</td><td>
<ol>
<li>Definir el propósito y el alcance del chatbot.</li>
<li>Recopilar y preparar datos de conocimiento (FAQs, manuales, etc.) para el motor RAG.</li>
<li>Configurar un nuevo flujo de trabajo en Dify, arrastrando y soltando nodos para la entrada del usuario, el procesamiento RAG y la generación de respuestas.</li>
<li>Integrar un LLM (ej. GPT-4, Claude) y configurar los prompts.</li>
<li>Probar el chatbot con escenarios de usuario y depurar el flujo de trabajo.</li>
<li>Desplegar el chatbot como una aplicación web o integrarlo en una plataforma existente.</li>
<li>Monitorear el rendimiento y recopilar feedback para iteraciones futuras.</li>
</ol>
</td><td>Dify Studio, Motor RAG de Dify, LLM (ej. OpenAI GPT-4), Fuentes de datos (ej. documentos PDF, bases de datos).</td><td>2-4 horas (para un prototipo básico), 1-3 días (para una versión inicial robusta).</td><td>Un chatbot funcional capaz de responder preguntas de soporte al cliente de manera precisa y consistente.</td></tr>
<tr><td>**Automatización de Investigación de Mercado**</td><td>
<ol>
<li>Definir los temas de investigación y las fuentes de datos (ej. sitios web, bases de datos públicas).</li>
<li>Crear un flujo de trabajo en Dify que utilice un agente para buscar información en la web (usando la herramienta Google Search).</li>
<li>Configurar nodos para extraer y resumir información clave de los resultados de búsqueda.</li>
<li>Utilizar un LLM para analizar los datos recopilados y generar informes estructurados.</li>
<li>Implementar un mecanismo de revisión y validación de los resultados.</li>
</ol>
</td><td>Dify Studio, Herramienta Google Search (integrada en Dify), LLM (ej. Claude Opus), Nodos de procesamiento de texto.</td><td>4-8 horas (para un flujo de trabajo básico), 3-7 días (para un sistema de investigación más complejo).</td><td>Informes de investigación de mercado automatizados y resumidos, identificando tendencias y puntos clave.</td></tr>
<tr><td>**Generación de Contenido Personalizado**</td><td>
<ol>
<li>Identificar el tipo de contenido a generar (ej. descripciones de productos, posts de blog).</li>
<li>Definir las características del público objetivo y el tono de voz.</li>
<li>Crear un flujo de trabajo en Dify que tome entradas (ej. nombre del producto, características) y utilice un LLM para generar el contenido.</li>
<li>Integrar herramientas de edición o revisión para asegurar la calidad y coherencia del contenido.</li>
<li>Implementar un bucle de feedback para refinar el modelo de generación.</li>
</ol>
</td><td>Dify Studio, LLM (ej. Gemini Pro), Nodos de entrada/salida de texto, Herramientas de edición (opcional).</td><td>1-2 horas (para un generador simple), 2-5 días (para un sistema de generación de contenido avanzado).</td><td>Contenido de marketing o informativo generado automáticamente, adaptado a las especificaciones del usuario.</td></tr>
</table>
## L07 — EVIDENCIA Y REPRODUCIBILIDAD
<table header-row="true">
<tr><td>Benchmark</td><td>Score/Resultado</td><td>Fecha</td><td>Fuente</td><td>Comparativa</td></tr>
<tr><td>**Rendimiento de Recuperación RAG**</td><td>Aumento del 20% en la tasa de aciertos de recuperación.</td><td>Noviembre 2023</td><td>Dify Blog (dify.ai/blog/dify-ai-rag-technology-upgrade-performance-improvement-qa-accuracy)</td><td>Supera a la API de Asistentes de OpenAI en la tasa de aciertos de recuperación.</td></tr>
<tr><td>**Estrellas en GitHub**</td><td>Más de 40,000 estrellas.</td><td>Septiembre 2024 (y en aumento)</td><td>GitHub (langgenius/dify)</td><td>Líder en comparación con Langflow y Flowise (aproximadamente 30,000 cada uno en la misma fecha).</td></tr>
<tr><td>**Adopción y Uso**</td><td>Más de 100,000 aplicaciones de IA construidas.</td><td>Marzo 2026</td><td>Dify.ai (página principal)</td><td>Demuestra una amplia adopción y confianza en la plataforma.</td></tr>
<tr><td>**Evaluación de Agentes (con Arize)**</td><td>Capacidad de evaluar, monitorear y mejorar agentes mediante trazas anotadas, datasets de prueba estructurados y evaluaciones personalizadas.</td><td>Septiembre 2025</td><td>Dify Blog (dify.ai/blog/dify-arize-how-to-evaluate-monitor-and-improve-agents)</td><td>Proporciona un marco robusto para la reproducibilidad y mejora continua de agentes de IA.</td></tr>
<tr><td>**Reducción de Horas de Trabajo**</td><td>Reducción de 18,000 horas anuales en tareas repetitivas para clientes empresariales.</td><td>Desconocida (reportado en contexto empresarial)</td><td>Dify Enterprise (dify.ai/enterprise)</td><td>Demuestra un ROI significativo en la automatización de procesos empresariales.</td></tr>
</table>
## L08 — ARQUITECTURA DE INTEGRACIÓN
<table header-row="true">
<tr><td>Método de Integración</td><td>
<ul>
<li>**Dify API:** Interfaz RESTful para la interacción programática con la plataforma.</li>
<li>**Sistema de Plugins:** Permite la integración de herramientas y servicios externos, incluyendo aquellos definidos por especificaciones OpenAPI.</li>
<li>**Model Context Protocol (MCP):** Un protocolo estandarizado para que los agentes de IA descubran y utilicen servidores externos.</li>
<li>**Integraciones Directas:** Conexión con diversos LLMs y herramientas pre-construidas.</li>
</ul>
</td></tr>
<tr><td>Protocolo</td><td>
<ul>
<li>**HTTP/HTTPS:** Protocolo estándar para la comunicación de la API y la mayoría de las integraciones web.</li>
<li>**MCP:** Protocolo específico para la interacción con agentes de IA y herramientas externas.</li>
<li>**OpenAPI:** Utilizado para la descripción y el consumo de APIs externas.</li>
<li>**Posible A2A:** Se ha discutido la incorporación de soporte para el protocolo A2A para mejorar la interoperabilidad.</li>
</ul>
</td></tr>
<tr><td>Autenticación</td><td>
<ul>
<li>**API Key:** Método común para autenticar solicitudes a la Dify API.</li>
<li>**OAuth:** Soporte para autenticación basada en OAuth para integraciones con servicios de terceros.</li>
<li>**Credenciales de Workspace:** Autenticación de usuarios dentro de un workspace de Dify (contraseña, código de verificación, SSO).</li>
<li>**SSO (Single Sign-On):** Integración con proveedores de SSO para la autenticación de usuarios en aplicaciones web privadas.</li>
<li>**Capa de Autenticación Externa:** Se recomienda construir una capa de autenticación independiente fuera de Dify para mayor flexibilidad y seguridad.</li>
</ul>
</td></tr>
<tr><td>Latencia Típica</td><td>La latencia típica puede variar significativamente dependiendo de la infraestructura de despliegue (auto-alojado vs. Dify Cloud), la complejidad del flujo de trabajo de IA, el LLM utilizado y la carga del sistema. No hay datos públicos específicos de latencia promedio.</td></tr>
<tr><td>Límites de Rate</td><td>No se han encontrado límites de tasa explícitos documentados públicamente para la versión de código abierto de Dify. En la versión Dify Cloud, los límites de tasa se gestionan internamente para asegurar la estabilidad del servicio. Para despliegues auto-alojados, los límites de tasa dependerán de la configuración de la infraestructura subyacente.</td></tr>
</table>
## L09 — VERIFICACIÓN Y PRUEBAS
<table header-row="true">
<tr><td>Tipo de Test</td><td>Herramienta Recomendada</td><td>Criterio de Éxito</td><td>Frecuencia</td></tr>
<tr><td>Depuración de Flujos de Trabajo</td><td>Dify 1.5.0 (funcionalidad integrada de depuración en tiempo real)</td><td>Capacidad de probar pasos individuales del flujo de trabajo y rastrear variables en vivo.</td><td>Durante el desarrollo y la iteración de flujos de trabajo.</td></tr>
<tr><td>Evaluación y Monitoreo de Agentes</td><td>Integración con Arize</td><td>Medición de la calidad del agente a través de trazas anotadas, datasets de prueba estructurados y evaluaciones personalizadas.</td><td>Continuo en producción, y durante ciclos de mejora del agente.</td></tr>
<tr><td>Pruebas de Escenario para Chatbots</td><td>Herramienta de pruebas de escenario multi-turno (desarrollada por la comunidad)</td><td>Identificación de problemas de calidad en interacciones complejas, capacidad de ejecutar pruebas repetidamente y automáticamente.</td><td>Regularmente durante el desarrollo y antes de cada despliegue significativo.</td></tr>
<tr><td>Pruebas Unitarias y de Integración (Frontend)</td><td>Vitest & React Testing Library (RTL) (a través de una skill de la comunidad)</td><td>Automatización de pruebas para componentes de interfaz de usuario y su interacción.</td><td>Durante el desarrollo de componentes de frontend y en pipelines de CI/CD.</td></tr>
<tr><td>Aseguramiento de Calidad (QA) de Respuestas de LLM</td><td>Sistema de Anotación de Dify</td><td>Asegurar que preguntas sensibles o importantes reciban respuestas pre-aprobadas, minimizando la variabilidad de la IA.</td><td>Revisión continua de interacciones críticas y ajuste de respuestas.</td></tr>
<tr><td>Verificación de Firma de Plugins</td><td>Funcionalidad integrada en Dify Community Edition</td><td>Validación de la autenticidad e integridad de plugins de terceros.</td><td>Al instalar o actualizar plugins de terceros.</td></tr>
</table>
## L10 — CICLO DE VIDA Y MIGRACIÓN
<table header-row="true">
<tr><td>Versión</td><td>Fecha de Lanzamiento</td><td>Estado</td><td>Cambios Clave</td><td>Ruta de Migración</td></tr>
<tr><td>v0.3.31</td><td>Noviembre 2023</td><td>Activo/Legacy</td><td>Mejoras significativas en la tecnología RAG, aumento del 20% en la tasa de aciertos de recuperación, introducción de búsqueda híbrida y modelo de reranking semántico.</td><td>Actualización a versiones posteriores.</td></tr>
<tr><td>v0.3.34</td><td>Diciembre 2023</td><td>Activo/Legacy</td><td>Introducción de la función de Respuesta con Anotaciones (Annotation Reply) para capacidades mejoradas de Q&A.</td><td>Actualización a versiones posteriores.</td></tr>
<tr><td>v1.0.0</td><td>Febrero 2025</td><td>Activo</td><td>Establecimiento de la base para un ecosistema de plugins robusto, mejoras en la escalabilidad y facilidad de innovación.</td><td>Guía de migración disponible para la Community Edition a v1.0.0.</td></tr>
<tr><td>v1.5.0</td><td>Junio 2025</td><td>Activo</td><td>Introducción de depuración de flujos de trabajo en tiempo real, permitiendo probar nodos individuales y rastrear variables en vivo.</td><td>Actualización a versiones posteriores.</td></tr>
<tr><td>v1.6.0</td><td>Julio 2025</td><td>Activo</td><td>Soporte bidireccional integrado para el Model Context Protocol (MCP).</td><td>Actualización a versiones posteriores.</td></tr>
<tr><td>v1.9.1</td><td>Marzo 2026</td><td>Activo</td><td>Mejoras de rendimiento, corrección de errores, interfaz de usuario más fluida, nuevas características para desarrolladores y mayor internacionalización.</td><td>Actualización a versiones posteriores.</td></tr>
<tr><td>v3.9.1 (Enterprise)</td><td>Desconocido (posterior a v3.9.0)</td><td>Activo</td><td>Notas de lanzamiento movidas a ee.dify.ai.</td><td>Actualización desde versiones anteriores de Enterprise.</td></tr>
<tr><td>Versiones Antiguas</td><td>Varias</td><td>End-of-Life (EOL)</td><td>No reciben parches de seguridad ni correcciones de errores.</td><td>Se recomienda encarecidamente la migración a versiones más recientes.</td></tr>
<tr><td>Migración de Weaviate</td><td>N/A</td><td>N/A</td><td>Guía para migrar de Weaviate client v3 a v4.17.0 y de Weaviate server 1.19.0 a 1.27.0 o superior.</td><td>Procedimiento detallado que incluye copia de seguridad, actualización de Weaviate y corrección de datos huérfanos.</td></tr>
<tr><td>Migración de Almacenamiento</td><td>N/A</td><td>N/A</td><td>Guía para migrar archivos de almacenamiento local a proveedores de almacenamiento en la nube (ej. Alibaba Cloud OSS).</td><td>Configuración de variables de entorno para el almacenamiento en la nube.</td></tr>
</table>
## L11 — MARCO DE COMPETENCIA
<table header-row="true">
<tr><td>Competidor Directo</td><td>Ventaja vs Competidor</td><td>Desventaja vs Competidor</td><td>Caso de Uso Donde Gana</td></tr>
<tr><td>**Flowise**</td><td>
<ul>
<li>**Escalabilidad:** Dify está diseñado para la escalabilidad y el despliegue en producción.</li>
<li>**Documentación:** Generalmente mejor documentación.</li>
<li>**LLMOps:** Ofrece un conjunto más completo de funcionalidades LLMOps (observabilidad, gestión de prompts, etc.).</li>
</ul>
</td><td>
<ul>
<li>**Facilidad de Uso Inicial:** Flowise puede ser percibido como más fácil para prototipos rápidos y demos debido a su enfoque más simple en la construcción visual de agentes tipo LangChain.</li>
</ul>
</td><td>
<ul>
<li>**Aplicaciones de IA en Producción:** Dify es superior para construir y desplegar aplicaciones de IA robustas y escalables en entornos de producción.</li>
<li>**LLMOps Completos:** Para equipos que requieren un control integral sobre el ciclo de vida de las aplicaciones LLM.</li>
</ul>
</td></tr>
<tr><td>**LangChain**</td><td>
<ul>
<li>**Builder Visual:** Dify ofrece una interfaz visual de arrastrar y soltar, simplificando el desarrollo.</li>
<li>**Plataforma Integral:** Dify es una plataforma LLMOps completa (prompt + workflow + RAG + tools + observabilidad).</li>
<li>**Curva de Aprendizaje:** Más accesible para desarrolladores que prefieren un enfoque low-code.</li>
</ul>
</td><td>
<ul>
<li>**Control a Nivel de Código:** LangChain ofrece un control más granular a nivel de código, lo que puede ser preferido por desarrolladores que necesitan máxima flexibilidad y personalización.</li>
<li>**Flexibilidad:** LangChain es un framework, no una plataforma, lo que le da una flexibilidad inherente para casos de uso muy específicos o experimentales.</li>
</ul>
</td><td>
<ul>
<li>**Desarrollo Rápido y Despliegue:** Dify es ideal para equipos que buscan prototipar y desplegar rápidamente aplicaciones de IA sin una inversión profunda en codificación.</li>
<li>**Equipos Multidisciplinares:** Facilita la colaboración entre desarrolladores y no-desarrolladores.</li>
</ul>
</td></tr>
<tr><td>**n8n**</td><td>
<ul>
<li>**Enfoque en IA:** Dify está específicamente diseñado para el desarrollo de aplicaciones de IA y LLMOps.</li>
<li>**RAG y Agentes:** Capacidades nativas y avanzadas para RAG y la construcción de agentes autónomos.</li>
</ul>
</td><td>
<ul>
<li>**Automatización General:** n8n es una herramienta de automatización de flujos de trabajo más generalista, no centrada exclusivamente en IA.</li>
<li>**Integraciones:** n8n tiene una biblioteca muy extensa de integraciones para automatización general.</li>
</ul>
</td><td>
<ul>
<li>**Orquestación de IA y Agentes:** Dify es la elección superior cuando el objetivo principal es construir y gestionar flujos de trabajo y agentes de IA complejos.</li>
</ul>
</td></tr>
<tr><td>**StackAI**</td><td>
<ul>
<li>**Madurez y Comunidad:** Dify tiene una comunidad más grande y un ecosistema más maduro (según el número de estrellas en GitHub y descargas).</li>
<li>**Funcionalidades LLMOps:** Dify ofrece un conjunto más amplio de herramientas para la gestión del ciclo de vida de las aplicaciones LLM.</li>
</ul>
</td><td>
<ul>
<li>**Experiencia de Usuario:** StackAI puede tener una UX más amigable para ciertos usuarios, especialmente en marketing, ventas, etc.</li>
</ul>
</td><td>
<ul>
<li>**Plataforma Integral de LLMOps:** Dify es más adecuado para equipos que buscan una solución completa para construir, desplegar y operar aplicaciones de IA a escala.</li>
</ul>
</td></tr>
</table>
## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)
<table header-row="true">
<tr><td>Capacidad de IA</td><td>
<ul>
<li>**Orquestación de Flujos de Trabajo Agenticos:** Construcción, despliegue y gestión de agentes autónomos de IA mediante una interfaz visual.</li>
<li>**RAG (Retrieval-Augmented Generation):** Implementación de pipelines RAG para mejorar la precisión y relevancia de las respuestas de los LLMs, utilizando fuentes de conocimiento externas.</li>
<li>**Ingeniería de Prompts:** Herramientas para diseñar, probar y optimizar prompts, incluyendo un "Modo Experto" para control avanzado.</li>
<li>**Soporte Multi-Modelo:** Acceso y capacidad de cambiar entre una amplia gama de modelos de lenguaje grandes (LLMs) de diferentes proveedores.</li>
<li>**LLMOps:** Funcionalidades para el ciclo de vida completo de las aplicaciones LLM, incluyendo monitoreo, evaluación y mejora continua.</li>
<li>**Herramientas Integradas:** Más de 50 herramientas pre-construidas para agentes de IA (ej. Google Search, DALL·E, Stable Diffusion, WolframAlpha).</li>
</ul>
</td></tr>
<tr><td>Modelo Subyacente</td><td>
<ul>
<li>Dify no tiene un único modelo subyacente, sino que actúa como una plataforma de orquestación que soporta una amplia gama de proveedores de modelos de IA.</li>
<li>**Proveedores Soportados:** OpenAI, Anthropic, Azure OpenAI, Google Gemini, Google Cloud, Nvidia API Catalog, Nvidia NIM, Nvidia Triton Inference Server, y modelos de código abierto como Ollama.</li>
<li>**Flexibilidad:** Permite a los usuarios seleccionar y cambiar entre diferentes LLMs según las necesidades de la aplicación, utilizando modelos más pequeños y económicos para tareas básicas y modelos más potentes para tareas complejas.</li>
</ul>
</td></tr>
<tr><td>Nivel de Control</td><td>
<ul>
<li>**Alto Nivel de Control:** Los usuarios tienen un control significativo sobre la lógica de la IA a través de la orquestación visual de flujos de trabajo, la configuración detallada de los prompts y la selección de modelos.</li>
<li>**Control de Datos:** En despliegues auto-alojados, los equipos tienen control total sobre sus datos, acceso y escalabilidad.</li>
<li>**Debugging en Tiempo Real:** Permite un control preciso durante el desarrollo y la depuración de los flujos de trabajo de IA.</li>
</ul>
</td></tr>
<tr><td>Personalización Posible</td><td>
<ul>
<li>**Selección de Modelos:** Personalización al elegir el LLM más adecuado para cada tarea.</li>
<li>**Configuración de Prompts:** Ajuste fino de los prompts para optimizar el comportamiento del LLM.</li>
<li>**Desarrollo de Plugins:** Creación de plugins personalizados para extender las funcionalidades de Dify y adaptarlas a necesidades específicas.</li>
<li>**Flujos de Trabajo Personalizados:** Diseño de flujos de trabajo únicos mediante la interfaz visual para abordar casos de uso específicos.</li>
<li>**Integración de Datos:** Conexión con diversas fuentes de datos para el motor RAG, permitiendo una personalización del conocimiento.</li>
</ul>
</td></tr>
</table>
## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA
<table header-row="true">
<tr><td>Métrica</td><td>Valor Reportado por Comunidad</td><td>Fuente</td><td>Fecha</td></tr>
<tr><td>Facilidad de Uso y Potentes Capacidades de Integración</td><td>Elogios consistentes por su interfaz intuitiva y la capacidad de crear flujos de trabajo de IA y chatbots.</td><td>G2.com, dev.to</td><td>Actualizado a 2026</td></tr>
<tr><td>Rendimiento bajo Cargas de Trabajo Grandes</td><td>Puede tener dificultades para manejar cargas de trabajo grandes, con reportes de degradación significativa del rendimiento tras pruebas de carga.</td><td>AWS Marketplace, GitHub (langgenius/dify/issues/7978)</td><td>Septiembre 2024 - Actualizado a 2026</td></tr>
<tr><td>Fiabilidad General</td><td>Considerado muy fiable, atribuido a la experiencia del equipo fundador en Tencent DevOps.</td><td>Medium (medium.com/iris-by-argon-co)</td><td>Desconocida</td></tr>
<tr><td>Eficacia en Casos de Uso Directos</td><td>Excelente para casos de uso sencillos como soporte al cliente, calificación de leads, generación de contenido y extracción de datos de documentos.</td><td>dev.to (dev.to/nova_gg)</td><td>Abril 2026</td></tr>
<tr><td>Capacidad de Pruebas de Escenario</td><td>La comunidad ha desarrollado herramientas para pruebas de escenario multi-turno, lo que indica una necesidad y capacidad de validación de la calidad de los chatbots.</td><td>Reddit (r/difyai), dev.to (dev.to/shuntarookuma)</td><td>Marzo 2026</td></tr>
<tr><td>Mejora en el Rendimiento de RAG</td><td>Aumento del 20% en la tasa de aciertos de recuperación.</td><td>Dify Blog (dify.ai/blog/dify-ai-rag-technology-upgrade-performance-improvement-qa-accuracy)</td><td>Noviembre 2023</td></tr>
<tr><td>Actividad y Soporte de la Comunidad</td><td>Comunidad activa en GitHub Discussions y foros de Dify, con contribuciones y discusiones sobre mejoras y resolución de problemas.</td><td>GitHub (langgenius/dify/discussions), forum.dify.ai</td><td>Continuo (Actualizado a 2026)</td></tr>
</table>
## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM
<table header-row="true">
<tr><td>Plan</td><td>Precio</td><td>Límites</td><td>Ideal Para</td><td>ROI Estimado</td></tr>
<tr><td>**Open Source (Community Edition)**</td><td>Gratuito</td><td>Depende de la infraestructura auto-alojada del usuario.</td><td>Desarrolladores y equipos que buscan control total, máxima personalización, y la capacidad de auto-alojar la plataforma. Ideal para experimentación y proyectos con requisitos específicos de infraestructura.</td><td>Alto, al eliminar costos de licencia y permitir el uso de recursos existentes. El ROI se maximiza a través de la flexibilidad y el control total sobre los datos y la infraestructura.</td></tr>
<tr><td>**Dify Cloud (Sandbox)**</td><td>Gratuito</td><td>200 llamadas gratuitas a GPT-4 (para prueba).</td><td>Nuevos usuarios y desarrolladores que desean probar las capacidades de Dify sin configuración inicial. Ideal para prototipos rápidos y exploración de funcionalidades.</td><td>Rápido, al permitir la validación de ideas y la experimentación sin inversión inicial.</td></tr>
<tr><td>**Dify Cloud (Professional)**</td><td>$59/workspace/mes</td><td>Diseñado para desarrolladores individuales y pequeños equipos. Límites de uso de LLM y recursos de cómputo gestionados por Dify Cloud.</td><td>Desarrolladores independientes y pequeños equipos listos para construir y desplegar aplicaciones de IA en producción. Ofrece un equilibrio entre costo y funcionalidades gestionadas.</td><td>Moderado a alto, al acelerar el tiempo de lanzamiento al mercado y reducir la complejidad operativa para equipos pequeños.</td></tr>
<tr><td>**Dify Cloud (Team)**</td><td>$159/workspace/mes</td><td>Diseñado para equipos en crecimiento. Límites de uso de LLM y recursos de cómputo gestionados por Dify Cloud, superiores al plan Professional.</td><td>Equipos en crecimiento que necesitan colaborar en el desarrollo de aplicaciones de IA y requieren más recursos y soporte.</td><td>Alto, al mejorar la colaboración del equipo, la eficiencia en el desarrollo y la capacidad de escalar aplicaciones de IA.</td></tr>
<tr><td>**Dify Enterprise**</td><td>Personalizado (a partir de $150,000/año según AWS Marketplace)</td><td>Límites personalizados y adaptados a las necesidades de grandes organizaciones, incluyendo recursos de cómputo, uso de LLM y soporte.</td><td>Grandes empresas, CTOs, Directores de TI, CAIOs que requieren infraestructura robusta, seguridad de grado empresarial, cumplimiento normativo, soporte dedicado y personalización profunda. También para startups que buscan validar ideas y construir MVPs con respaldo empresarial.</td><td>Muy alto, al permitir la implementación de soluciones de IA a gran escala que pueden generar eficiencias operativas significativas (ej. reducción de 18,000 horas anuales en tareas repetitivas), mejorar la toma de decisiones y habilitar nuevos modelos de negocio.</td></tr>
</table>
## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING
<table header-row="true">
<tr><td>Escenario de Test</td><td>Resultado</td><td>Fortaleza Identificada</td><td>Debilidad Identificada</td></tr>
<tr><td>**Rendimiento de Recuperación RAG**</td><td>Aumento del 20% en la tasa de aciertos de recuperación, superando a la API de Asistentes de OpenAI.</td><td>Eficacia superior en la recuperación de información relevante para LLMs.</td><td>N/A (no se identificaron debilidades específicas en este benchmark).</td></tr>
<tr><td>**Generación de Flujos de Trabajo Agenticos (Chat2Workflow)**</td><td>Dify es una plataforma mainstream para la construcción de flujos de trabajo agenticos visuales, lo que implica su capacidad para generar y ejecutar lógicas complejas.</td><td>Capacidad robusta para la orquestación visual de agentes de IA.</td><td>N/A (el benchmark se centra en la capacidad de generación, no en fallos).</td></tr>
<tr><td>**Evaluación y Monitoreo de Agentes (con Arize)**</td><td>Integración con Arize para evaluar, monitorear y mejorar agentes, permitiendo la creación de datasets de prueba estructurados y evaluaciones personalizadas.</td><td>Marco sólido para la evaluación continua y la mejora de la calidad de los agentes de IA.</td><td>N/A (la integración con Arize es una fortaleza).</td></tr>
<tr><td>**Seguridad de Aplicaciones de IA (Plugin Palo Alto Networks)**</td><td>Integración con el plugin PANW AI Runtime Security para filtrar entradas de usuario y salidas de modelo, protegiendo contra amenazas.</td><td>Defensa proactiva contra ataques dirigidos a aplicaciones de IA, como inyecciones de prompts.</td><td>N/A (la integración de seguridad es una fortaleza).</td></tr>
<tr><td>**Vulnerabilidades de Seguridad (Reportes en GitHub)**</td><td>Identificación y discusión de vulnerabilidades como XSS en la plataforma.</td><td>Transparencia y compromiso con la comunidad para abordar y resolver problemas de seguridad.</td><td>Existencia de vulnerabilidades que requieren atención y parches.</td></tr>
<tr><td>**Pruebas de Carga y Escalabilidad**</td><td>Reportes de degradación significativa del rendimiento bajo cargas de trabajo elevadas en despliegues auto-alojados.</td><td>Capacidad de auto-alojamiento y flexibilidad en la infraestructura.</td><td>Potenciales cuellos de botella de rendimiento y escalabilidad si no se optimiza la configuración de la infraestructura subyacente.</td></tr>
</table>