# BIBLIA DE SKYVERN v7.3

**Fecha de Actualización:** 30 de Abril de 2026

**Versión más actual:** v1.0.22 (al 30 de abril de 2026)

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO

<table header-row="true">
<tr><td>Nombre oficial</td><td>Skyvern</td></tr>
<tr><td>Desarrollador</td><td>Skyvern-AI</td></tr>
<tr><td>País de Origen</td><td>Estados Unidos (San Francisco)</td></tr>
<tr><td>Inversión y Financiamiento</td><td>Total: $3.43M. Ronda Seed: $2.7M (finales de 2025). Inversores incluyen Y Combinator, Sixty Degree Capital, Unpopular Ventures.</td></tr>
<tr><td>Modelo de Precios</td><td>Freemium (1000 créditos/mes), Hobby ($29/mes por 30,000 créditos), Pro ($149/mes por 150,000 créditos), Enterprise (personalizado, créditos ilimitados). Basado en créditos/pasos de automatización.</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>Automatización de flujos de trabajo basados en navegador utilizando IA (LLMs y visión por computadora). Se posiciona como una alternativa a la automatización tradicional de RPA, ofreciendo mayor robustez y menor mantenimiento. SDK de código abierto compatible con Playwright.</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Se integra con Playwright. Utiliza LLMs y visión por computadora. Dependencias de paquetes Python (mencionadas en GitHub como "restricciones ajustadas").</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Compatible con navegadores web modernos a través de Playwright. SDKs disponibles para Python y TypeScript. API REST. Despliegue en la nube o auto-hospedado (Docker, Kubernetes).</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>No se encontraron SLOs públicos específicos, pero la empresa se enfoca en la fiabilidad y el bajo mantenimiento de las automatizaciones.</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA

<table header-row="true">
<tr><td>Licencia</td><td>GNU Affero General Public License v3 (AGPL-3.0) para el core lógico de código abierto.</td></tr>
<tr><td>Política de Privacidad</td><td>Disponible en skyven.co/privacy-policy/ (actualizada a Oct 9, 2024). Recopila, usa, mantiene y divulga información de los usuarios.</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>Certificación SOC 2 Tipo II, compatible con HIPAA, GDPR. Soporte para ISO 27001, SOC 2 Tipo 2, HIPAA Tipo 2.</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>Auditoría independiente para la certificación SOC 2 Tipo II (Agosto 7, 2025). Centro de Confianza (trust.skyvern.com) detalla controles de acceso, gestión de datos y protección, recuperación ante desastres.</td></tr>
<tr><td>Respuesta a Incidentes</td><td>No se encontró información pública específica sobre la política de respuesta a incidentes, pero el Trust Center menciona la recuperación ante desastres con copias de seguridad automatizadas.</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>No se encontró información pública específica.</td></tr>
<tr><td>Política de Obsolescencia</td><td>No se encontró información pública específica.</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA

Skyvern se basa en un modelo mental que simula la interacción humana con navegadores web, utilizando inteligencia artificial para interpretar visualmente las páginas y ejecutar acciones. Su enfoque principal es la automatización de flujos de trabajo complejos en línea que tradicionalmente requerirían intervención manual o scripts frágiles. Al abstraer la complejidad de los selectores y la lógica de navegación, Skyvern permite a los usuarios definir tareas en lenguaje natural, transformando intenciones de alto nivel en acciones concretas en el navegador.

<table header-row="true">
<tr><td>Paradigma Central</td><td>Automatización de navegador basada en IA (LLMs y Visión por Computadora). Agente autónomo impulsado por tareas (Task-Driven Autonomous Agent).</td></tr>
<tr><td>Abstracciones Clave</td><td>**Tareas (Tasks):** Un trabajo de automatización individual. **Flujos de Trabajo (Workflows):** Secuencias de tareas. **Sesiones de Navegador (Browser Sessions):** Entornos aislados donde se ejecutan las automatizaciones. **Credenciales (Credentials):** Gestión segura de accesos. **Bloques (Blocks):** Componentes reutilizables de automatización.</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>Pensar en términos de objetivos de alto nivel y lenguaje natural. Describir el "qué" en lugar del "cómo". Identificar los pasos lógicos que un humano seguiría en el navegador. Enfocarse en la robustez y adaptabilidad a cambios en la UI.</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>Dependencia excesiva de selectores CSS/XPath frágiles. Intentar micro-gestionar cada clic o entrada de texto. Ignorar la capacidad de auto-curación de Skyvern. Crear automatizaciones que no toleren cambios menores en la interfaz de usuario.</td></tr>
<tr><td>Curva de Aprendizaje</td><td>Baja para usuarios que definen tareas en lenguaje natural. Moderada para desarrolladores que utilizan el SDK y la API, ya que requiere comprender las abstracciones clave y la integración con Playwright.</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS

<table header-row="true">
<tr><td>Capacidades Core</td><td>Automatización de flujos de trabajo basados en navegador con IA (LLMs y visión por computadora). Interacción con sitios web no vistos previamente. Relleno de formularios, extracción de datos, navegación. SDK compatible con Playwright.</td></tr>
<tr><td>Capacidades Avanzadas</td><td>Resolución de CAPTCHAs (básico y avanzado), soporte para 2FA/TOTP, integración con gestores de contraseñas (1Password, Bitwarden), proxies residenciales, geo-targeting a nivel de país y ciudad, webhooks, manejo de credenciales, ejecución concurrente de tareas, soporte para flujos de trabajo complejos (bucles, parsing de archivos, envío de emails, prompts de texto, peticiones HTTP).</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>Auto-curación de flujos de trabajo (adaptación a cambios en la UI), mejora continua en la interpretación visual de páginas, optimización de la velocidad de instalación y resolución de dependencias del paquete open source. Desarrollo de agentes sin código y con código.</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>Dependencias con restricciones ajustadas en `pyproject.toml` que pueden dificultar actualizaciones independientes (mencionado en GitHub). La eficacia de la automatización puede depender de la complejidad visual y la interactividad del sitio web.</td></tr>
<tr><td>Roadmap Público</td><td>No se encontró un roadmap público formal, pero las actualizaciones de blog y GitHub indican un enfoque en la mejora de la robustez, la velocidad y la expansión de las capacidades de IA para la automatización de navegadores.</td></tr>
</table>

## L05 — DOMINIO TÉCNICO

<table header-row="true">
<tr><td>Stack Tecnológico</td><td>Python, TypeScript, Playwright (extensión), LLMs (ej. Gemini 2.5 Pro), Visión por Computadora, Docker, Kubernetes. Soporte para Model Context Protocol (MCP).</td></tr>
<tr><td>Arquitectura Interna</td><td>Agente de automatización de navegador basado en IA. Utiliza un "agent loop" y una arquitectura "Planner-Agent-Validator". Interactúa con navegadores reales, lee páginas visualmente y completa tareas. Puede ser auto-hospedado.</td></tr>
<tr><td>Protocolos Soportados</td><td>HTTP/HTTPS para interacciones web. Chrome DevTools Protocol (CDP) para interacción con el navegador. Model Context Protocol (MCP).</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>**Entrada:** Lenguaje natural (prompts), SOPs (Standard Operating Procedures), scripts (Python, TypeScript). **Salida:** Datos estructurados (extraídos de sitios web), resultados de tareas automatizadas, logs de ejecución. Soporte para parsing de archivos.</td></tr>
<tr><td>APIs Disponibles</td><td>SDKs para Python y TypeScript. API REST para todas las capacidades (tareas, flujos de trabajo, credenciales, estado de ejecución, cancelación, reenvío de webhooks).</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS

<table header-row="true">
<tr><td>Caso de Uso</td><td>Automatización de Descarga de Facturas de Portales de Proveedores</td><td>Pasos Exactos</td><td>1. Iniciar sesión en el portal del proveedor. 2. Navegar a la sección de facturas. 3. Identificar y descargar facturas en formato PDF. 4. Extraer datos clave de las facturas (número, fecha, monto). 5. Almacenar facturas y datos en el sistema de gestión interno.</td><td>Herramientas Necesarias</td><td>Skyvern (con capacidad de inicio de sesión, navegación, descarga de archivos, extracción de datos), credenciales del portal.</td><td>Tiempo Estimado</td><td>Minutos por factura (vs. horas manuales).</td><td>Resultado Esperado</td><td>Facturas descargadas y datos estructurados disponibles automáticamente, reducción de errores manuales.</td></tr>
<tr><td>Caso de Uso</td><td>Relleno y Envío Masivo de Formularios Gubernamentales</td><td>Pasos Exactos</td><td>1. Acceder al formulario gubernamental en línea. 2. Rellenar campos del formulario con datos predefinidos o extraídos de una fuente. 3. Manejar CAPTCHAs o 2FA si es necesario. 4. Enviar el formulario. 5. Confirmar el envío y registrar el estado.</td><td>Herramientas Necesarias</td><td>Skyvern (con capacidades de relleno de formularios, resolución de CAPTCHA/2FA), fuente de datos para el formulario.</td><td>Tiempo Estimado</td><td>Segundos por formulario (vs. minutos/horas manuales).</td><td>Resultado Esperado</td><td>Formularios completados y enviados de manera eficiente, cumplimiento de plazos.</td></tr>
<tr><td>Caso de Uso</td><td>Extracción de Datos Estructurados de Sitios Web sin API</td><td>Pasos Exactos</td><td>1. Navegar a la página web objetivo. 2. Identificar los elementos visuales que contienen los datos deseados (ej. tablas de productos, listados). 3. Extraer los datos en un formato estructurado (ej. JSON, CSV). 4. Validar la integridad de los datos extraídos.</td><td>Herramientas Necesarias</td><td>Skyvern (con capacidades de visión por computadora y extracción de datos), Playwright SDK (para desarrolladores).</td><td>Tiempo Estimado</td><td>Variable, dependiendo de la complejidad del sitio y la cantidad de datos.</td><td>Resultado Esperado</td><td>Acceso a datos web para análisis, inteligencia de mercado o integración con otros sistemas.</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD

<table header-row="true">
<tr><td>Benchmark</td><td>WebVoyager Eval</td><td>Score/Resultado</td><td>85.8%</td><td>Fecha</td><td>16 de Enero de 2025</td><td>Fuente</td><td>Skyvern (blog oficial), Dassi.ai, Steel.dev (leaderboard de agentes AI)</td><td>Comparativa</td><td>Considerado "state-of-the-art" y el mejor rendimiento en su clase para WebAgents en el momento de la evaluación.</td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN

<table header-row="true">
<tr><td>Método de Integración</td><td>SDKs (Python, TypeScript), API REST, auto-hospedaje con Docker, integraciones con plataformas de automatización de terceros (Zapier, Make, n8n, Workato, Clay, Activepieces).</td></tr>
<tr><td>Protocolo</td><td>API-first approach. HTTP/HTTPS para la API REST. Model Context Protocol (MCP) para conectar aplicaciones de IA al navegador.</td></tr>
<tr><td>Autenticación</td><td>Manejo seguro de credenciales (passwords, 2FA/TOTP secrets) en vaults encriptados (Bitwarden, 1Password, Azure Key Vault). Soporte para servicios de credenciales personalizados a través de APIs HTTP. Re-autenticación automática de tokens expirados.</td></tr>
<tr><td>Latencia Típica</td><td>No se especifica una latencia típica en la documentación pública, pero el diseño está optimizado para la eficiencia en la automatización de flujos de trabajo de navegador.</td></tr>
<tr><td>Límites de Rate</td><td>No se especifican límites de rate públicos en la documentación. Los planes de precios se basan en créditos/mes, lo que implica un límite de uso general.</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS

<table header-row="true">
<tr><td>Tipo de Test</td><td>Pruebas de UI automatizadas</td><td>Herramienta Recomendada</td><td>Skyvern (utilizado para automatizar pruebas de UI en aplicaciones web)</td><td>Criterio de Éxito</td><td>Interacción exitosa con elementos web sin selectores predefinidos, adaptación a cambios en la UI, finalización de flujos de trabajo complejos (ej. checkout de e-commerce).</td><td>Frecuencia</td><td>Según la necesidad de pruebas de regresión y nuevas funcionalidades de las aplicaciones web.</td></tr>
<tr><td>Tipo de Test</td><td>Benchmarking de Agentes AI</td><td>Herramienta Recomendada</td><td>WebVoyager Eval</td><td>Criterio de Éxito</td><td>Puntuación alta en la capacidad de navegación web y ejecución de tareas en diversos sitios.</td><td>Frecuencia</td><td>Periódica, para validar el rendimiento del agente frente a otros en el mercado.</td></tr>
<tr><td>Tipo de Test</td><td>Verificación de Flujos de Trabajo</td><td>Herramienta Recomendada</td><td>Skyvern (agentes que se adaptan en tiempo real, esperan la carga de contenido y ajustan su estrategia)</td><td>Criterio de Éxito</td><td>Completar tareas en sitios web no vistos previamente, rellenar formularios, extraer datos con precisión.</td><td>Frecuencia</td><td>Continua, como parte de la ejecución de las automatizaciones.</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN

<table header-row="true">
<tr><td>Versión</td><td>Fecha de Lanzamiento</td><td>Estado</td><td>Cambios Clave</td><td>Ruta de Migración</td></tr>
<tr><td>v1.0.31</td><td>14 de Abril de 2026</td><td>Estable</td><td>Corrección de errores en la generación de `fill_form()` para flujos de trabajo no ATS.</td><td>Actualización directa desde versiones anteriores de la serie 1.0.x.</td></tr>
<tr><td>v1.0.22</td><td>Desconocida (mencionada como "latest" en la documentación principal)</td><td>Estable</td><td>Versión base de la documentación actual.</td><td>Actualización directa desde versiones anteriores.</td></tr>
<tr><td>Skyvern 2.0</td><td>16 de Enero de 2025</td><td>Mayor actualización</td><td>Logró un 85.8% en WebVoyager Eval, considerado "state-of-the-art" en navegación web. Mejoras significativas en la capacidad de los agentes para entender y navegar páginas web.</td><td>Requiere revisión de flujos de trabajo existentes para aprovechar las nuevas capacidades.</td></tr>
<tr><td>Actualizaciones de Agosto 2025</td><td>Agosto 2025</td><td>Actualización importante</td><td>Nueva opción "Use Script Cache" y configuración de clave de caché personalizada para reutilizar scripts de forma inteligente, reduciendo tiempos de ejecución.</td><td>Beneficios de rendimiento al habilitar nuevas configuraciones.</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA

<table header-row="true">
<tr><td>Competidor Directo</td><td>Ventaja vs Competidor</td><td>Desventaja vs Competidor</td><td>Caso de Uso Donde Gana</td></tr>
<tr><td>Browser-use</td><td>Skyvern utiliza visión por computadora y LLMs para entender visualmente las páginas web, lo que lo hace más robusto a cambios en la UI y menos dependiente de selectores DOM frágiles. Ofrece una solución más completa y "production-ready".</td><td>Browser-use puede ser preferido por desarrolladores Python que buscan una integración más directa con sus scripts existentes y un control más granular a nivel de código.</td><td>Automatización de flujos de trabajo complejos en sitios web dinámicos con UI cambiantes, donde la robustez y la adaptabilidad son críticas.</td></tr>
<tr><td>Selenium/Playwright (scripts tradicionales)</td><td>Skyvern elimina la necesidad de escribir y mantener scripts frágiles basados en selectores. Su enfoque basado en IA permite la auto-curación y la adaptación a sitios web no vistos previamente, reduciendo drásticamente el mantenimiento.</td><td>Los scripts tradicionales ofrecen un control de bajo nivel y pueden ser más eficientes para tareas muy específicas y estáticas. La curva de aprendizaje para desarrolladores familiarizados con estas herramientas puede ser menor inicialmente.</td><td>Automatización de tareas en portales de proveedores, llenado de formularios gubernamentales, extracción de datos de sitios sin API, donde la complejidad y el mantenimiento de scripts tradicionales serían prohibitivos.</td></tr>
<tr><td>Herramientas RPA tradicionales (ej. Automation Anywhere, UiPath)</td><td>Skyvern ofrece una solución más flexible y menos costosa para la automatización de navegadores, especialmente para flujos de trabajo complejos y dinámicos. Su enfoque de IA reduce la "tasa de mantenimiento" asociada con RPA.</td><td>Las herramientas RPA tradicionales pueden ofrecer una suite más amplia de automatización de procesos de negocio que va más allá del navegador, incluyendo automatización de escritorio y backend.</td><td>Automatización de procesos de negocio que involucran principalmente la interacción con aplicaciones web, donde la agilidad y la reducción de costos son prioritarias.</td></tr>
<tr><td>Firecrawl</td><td>Skyvern se enfoca en la automatización de flujos de trabajo completos, incluyendo interacción y manipulación de datos, mientras que Firecrawl se centra más en la extracción de datos web.</td><td>Firecrawl puede ser más eficiente para tareas puramente de scraping de datos a gran escala.</td><td>Flujos de trabajo que requieren no solo la extracción de datos, sino también la interacción con la página (iniciar sesión, rellenar formularios, navegar por múltiples pasos).</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)

<table header-row="true">
<tr><td>Capacidad de IA</td><td>Automatización de navegador basada en IA, comprensión visual de páginas web, procesamiento de lenguaje natural (NLP) para interpretar instrucciones, auto-curación de flujos de trabajo, resolución de CAPTCHAs y 2FA.</td></tr>
<tr><td>Modelo Subyacente</td><td>Utiliza Large Language Models (LLMs) como Gemini 2.5 Pro y visión por computadora para interactuar con sitios web. Soporta múltiples motores de IA para la ejecución de tareas.</td></tr>
<tr><td>Nivel de Control</td><td>Permite a los usuarios definir tareas en lenguaje natural (alto nivel de abstracción) o a través de SDKs (control más granular). El agente de IA planifica y ejecuta los pasos necesarios de forma autónoma.</td></tr>
<tr><td>Personalización Posible</td><td>Configuración de LLMs, integración con servicios de credenciales personalizados. La arquitectura de código abierto permite a los desarrolladores extender y personalizar funcionalidades.</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA

<table header-row="true">
<tr><td>Métrica</td><td>Valor Reportado por Comunidad</td><td>Fuente</td><td>Fecha</td></tr>
<tr><td>Puntuación de Producto</td><td>5.0/5.0 (basado en 7 reseñas)</td><td>Product Hunt</td><td>Desconocida</td></tr>
<tr><td>Adopción de IA (equipo de ingeniería)</td><td>0.6%</td><td>Exceeds.ai (skyvern.com Engineering AI Productivity Report)</td><td>25 de Marzo de 2026</td></tr>
<tr><td>Productividad (equipo de ingeniería)</td><td>0.01x lift</td><td>Exceeds.ai (skyvern.com Engineering AI Productivity Report)</td><td>25 de Marzo de 2026</td></tr>
<tr><td>Calidad de Código (equipo de ingeniería)</td><td>0.2%</td><td>Exceeds.ai (skyvern.com Engineering AI Productivity Report)</td><td>25 de Marzo de 2026</td></tr>
<tr><td>Clones de Git (usuarios únicos)</td><td>Mencionado como métrica de interés para proyectos open source.</td><td>Blog de Skyvern</td><td>13 de Mayo de 2024</td></tr>
<tr><td>Discusiones Comunitarias</td><td>Activas en GitHub Discussions y Discord.</td><td>GitHub, Discord</td><td>Desde Abril de 2024</td></tr>
<tr><td>Reseñas de Usuarios</td><td>Experiencias positivas destacando la capacidad de automatizar tareas complejas y la reducción de mantenimiento.</td><td>Trustpilot, Product Hunt, Reddit</td><td>Varias fechas (ej. 23 de Julio de 2025 en Trustpilot)</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM

<table header-row="true">
<tr><td>Plan</td><td>Precio</td><td>Límites</td><td>Ideal Para</td><td>ROI Estimado</td></tr>
<tr><td>Free</td><td>$0/mes</td><td>1000 créditos/mes, 1 ejecución concurrente</td><td>Proyectos personales, pruebas iniciales.</td><td>Alto, al ser gratuito permite validar el concepto sin inversión.</td></tr>
<tr><td>Hobby</td><td>$29/mes</td><td>30,000 créditos/mes, 10 ejecuciones concurrentes</td><td>Proyectos secundarios, pequeñas automatizaciones.</td><td>Rápida recuperación de la inversión para tareas repetitivas.</td></tr>
<tr><td>Pro</td><td>$149/mes</td><td>150,000 créditos/mes, 25 ejecuciones concurrentes</td><td>Equipos que implementan automatizaciones en producción.</td><td>ROI promedio del 2560%, con recuperación de la inversión en el primer año para proyectos de automatización sin código. Reducción de costos del 30-50% y procesamiento 75% más rápido en casos como reclamos de seguros.</td></tr>
<tr><td>Enterprise</td><td>Personalizado</td><td>Créditos ilimitados, ejecuciones concurrentes ilimitadas</td><td>Industrias reguladas y operaciones a gran escala (ej. HIPAA compliant, SOC-2 Report).</td><td>Significativo para grandes empresas que buscan reemplazar trabajo manual intensivo, con ahorros anuales de $2,000-5,000 para tareas como descarga de facturas de 50 portales.</td></tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING

<table header-row="true">
<tr><td>Escenario de Test</td><td>Resultado</td><td>Fortaleza Identificada</td><td>Debilidad Identificada</td></tr>
<tr><td>WebVoyager Eval (Navegación Web General)</td><td>85.8% de éxito</td><td>Capacidad "state-of-the-art" para navegar y completar tareas en sitios web no vistos previamente, adaptándose a diversas interfaces.</td><td>No se especifican debilidades en el benchmark, pero la naturaleza de la evaluación implica que aún hay un 14.2% de escenarios donde el agente no tuvo éxito.</td></tr>
<tr><td>Automatización de Relleno de Formularios Complejos</td><td>Alta tasa de éxito reportada por usuarios.</td><td>Manejo robusto de CAPTCHAs, 2FA/TOTP, y campos dinámicos, reduciendo la fragilidad de los scripts tradicionales.</td><td>Posibles desafíos con formularios extremadamente complejos o con lógicas de validación muy específicas que requieran intervención humana o ajustes finos.</td></tr>
<tr><td>Extracción de Datos de Sitios Web Dinámicos</td><td>Capacidad para extraer datos estructurados de sitios sin API.</td><td>Uso de visión por computadora y LLMs para identificar y extraer información relevante, incluso con cambios en el diseño de la página.</td><td>La precisión puede verse afectada en sitios con estructuras de datos muy inconsistentes o con elementos visuales ambiguos.</td></tr>
<tr><td>Red Teaming (Inferido)</td><td>No hay datos públicos específicos de red teaming.</td><td>La arquitectura basada en IA y la auto-curación sugieren una mayor resiliencia a ataques de manipulación de UI o cambios inesperados.</td><td>Potenciales vulnerabilidades en la interpretación de instrucciones ambiguas o en la interacción con elementos maliciosos en páginas web.</td></tr>
</table>
