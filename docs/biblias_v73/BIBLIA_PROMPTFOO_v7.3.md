# BIBLIA DE PROMPTFOO v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<table header-row="true">
<tr><td>Nombre oficial</td><td>Promptfoo</td></tr>
<tr><td>Desarrollador</td><td>Originalmente por Ian Webster y Michael D'Angelo; adquirido por OpenAI.</td></tr>
<tr><td>País de Origen</td><td>Estados Unidos (San Francisco, California)</td></tr>
<tr><td>Inversión y Financiamiento</td><td>Recaudó $18.4M en Serie A (Julio 2025, liderada por Insight Partners). Financiación total de $23M antes de la adquisición. Adquirido por OpenAI por $86M (Marzo 2026).</td></tr>
<tr><td>Modelo de Precios</td><td>Open-core (versión de código abierto disponible). Precios empresariales personalizados.</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>Plataforma líder en seguridad de IA para evaluación y red-teaming de aplicaciones LLM. Ayuda a identificar y remediar vulnerabilidades en sistemas de IA. Integrado en OpenAI Frontier.</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Depende de la integración con diversos modelos de lenguaje grandes (LLMs) y plataformas de IA (ej. Amazon Bedrock).</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Compatible con GPT, Claude, Gemini, Llama y otros LLMs.</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>Como parte de OpenAI, se espera que se adhiera a los SLOs de OpenAI para clientes empresariales, enfocados en disponibilidad y rendimiento de la plataforma.</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA
<table header-row="true">
<tr><td>Licencia</td><td>MIT License (código abierto).</td></tr>
<tr><td>Política de Privacidad</td><td>Política de privacidad detallada (promptfoo.dev/privacy) que cubre información personal, telemetría, cookies, intercambio y seguridad. Permite deshabilitar la transmisión de datos al backend.</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>SOC 2 Tipo II e ISO 27001 (desde Julio 2025).</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>Diseñado para identificar vulnerabilidades en sistemas de IA. No se detalla un historial de auditorías internas, pero su función principal es la auditoría de seguridad de LLMs.</td></tr>
<tr><td>Respuesta a Incidentes</td><td>No hay una política pública específica de Promptfoo; se asume alineación con las políticas de OpenAI tras la adquisición.</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>La autoridad de decisión sobre su implementación y configuración recae en los equipos de desarrollo y seguridad de las organizaciones usuarias.</td></tr>
<tr><td>Política de Obsolescencia</td><td>No se ha publicado una política de obsolescencia específica.</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA
Promptfoo introduce un paradigma de prueba y evaluación sistemática para aplicaciones basadas en Large Language Models (LLMs), alejándose del enfoque tradicional de prueba y error. Su objetivo es permitir a los desarrolladores y equipos de seguridad construir aplicaciones de IA seguras y confiables mediante la identificación proactiva de vulnerabilidades y la comparación del rendimiento de diferentes modelos y prompts.
<table header-row="true">
<tr><td>Paradigma Central</td><td>Evaluación y red-teaming de LLMs. Asegurar la fiabilidad y seguridad de las aplicaciones de IA mediante pruebas automatizadas y sistemáticas.</td></tr>
<tr><td>Abstracciones Clave</td><td>Prompts (entradas para LLMs), Proveedores (LLMs como GPT, Claude), Casos de Prueba (escenarios de evaluación), Aserciones (criterios de validación de salida), Métricas (cuantificación del rendimiento), Plugins (extensibilidad para red-teaming), Estrategias (enfoques de ataque), Targets (sistemas de IA a probar).</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>Pensamiento adversarial (red-teaming), enfoque basado en pruebas (test-driven development para LLMs), evaluación comparativa (benchmarking de modelos y prompts), integración continua (CI/CD para LLMs).</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>Despliegue de LLMs sin pruebas rigurosas, depender de la intuición para la calidad del prompt, ignorar las implicaciones de seguridad de los LLMs, falta de evaluación sistemática.</td></tr>
<tr><td>Curva de Aprendizaje</td><td>Moderada. Requiere comprensión de la configuración de archivos (YAML/JSON) y conceptos de evaluación de LLMs. La documentación y guías de inicio rápido facilitan la adopción.</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS
<table header-row="true">
<tr><td>Capacidades Core</td><td>Evaluación de prompts y modelos con evaluaciones automatizadas; Red-teaming y escaneo de vulnerabilidades para aplicaciones LLM; Pruebas de seguridad de IA; Comparación del rendimiento de GPT, Claude, Gemini, Llama y otros LLMs; Detección de inyección de prompts; Prevención de fuga de datos; Identificación de jailbreaks; Monitoreo de cumplimiento; Análisis de archivos de modelos para código malicioso y backdoors; Pruebas de comportamiento del modelo contra ataques reales; Generación de pruebas listas para usar.</td></tr>
<tr><td>Capacidades Avanzadas</td><td>Arquitectura modular con plugins, estrategias y targets para red-teaming; Evaluación sistemática; Pruebas adversariales; Integración con CI/CD (GitHub Actions, GitLab CI); Configuración de aserciones y métricas para validar salidas de LLM; Evaluación de modelos con calificación de modelos; Puntuación personalizada; Métricas de rendimiento.</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>Integración directa con OpenAI Frontier para seguridad y pruebas; Capacidades de prueba de IA agentic; Mayor enfoque en la seguridad de ecosistemas de agentes de IA.</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>La configuración inicial puede requerir familiaridad con archivos YAML/JSON. La complejidad de la evaluación de LLMs puede ser un desafío para usuarios sin experiencia en pruebas de IA.</td></tr>
<tr><td>Roadmap Público</td><td>Continuar construyendo herramientas para una IA segura y confiable, con una integración más profunda en la plataforma OpenAI Frontier y un enfoque en la seguridad de los agentes de IA.</td></tr>
</table>

## L05 — DOMINIO TÉCNICO
<table header-row="true">
<tr><td>Stack Tecnológico</td><td>Principalmente JavaScript/TypeScript, Node.js (inferido por la instalación vía npm y el repositorio de GitHub).</td></tr>
<tr><td>Arquitectura Interna</td><td>Modular, compuesta por plugins, estrategias y targets. Diseñada para ser reutilizable y extensible. Soporta la evaluación de prompts, agentes y aplicaciones RAG (Retrieval Augmented Generation).</td></tr>
<tr><td>Protocolos Soportados</td><td>Model Context Protocol (MCP) para la integración con proveedores de LLM y habilitar capacidades agenticas. HTTP/HTTPS para comunicación con APIs de LLM y servicios externos.</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>Entrada: Archivos de configuración en formatos YAML/JSON para definir prompts, proveedores, casos de prueba, aserciones y métricas. Salida: Informes de evaluación, resultados de red-teaming, métricas de rendimiento y vulnerabilidades identificadas.</td></tr>
<tr><td>APIs Disponibles</td><td>Interfaz de línea de comandos (CLI) para ejecución directa. Librería programática (JavaScript/TypeScript) para integración en flujos de trabajo de desarrollo y CI/CD.</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS
<table header-row="true">
<tr><td>Caso de Uso</td><td>Pasos Exactos</td><td>Herramientas Necesarias</td><td>Tiempo Estimado</td><td>Resultado Esperado</td></tr>
<tr><td>Evaluación Comparativa de Prompts y Modelos</td><td>1. Definir prompts y proveedores de LLM en un archivo de configuración (YAML/JSON). 2. Crear casos de prueba que cubran diferentes escenarios. 3. Ejecutar `promptfoo eval` desde la CLI. 4. Analizar los resultados en el visor web interactivo de Promptfoo para comparar el rendimiento de los prompts y modelos.</td><td>Promptfoo CLI, archivo de configuración (YAML/JSON), LLMs (GPT, Claude, Gemini, etc.), visor web de Promptfoo.</td><td>Horas a días, dependiendo de la complejidad y el número de pruebas.</td><td>Identificación del prompt y/o modelo óptimo para una tarea específica, mejora en la calidad y relevancia de las respuestas del LLM.</td></tr>
<tr><td>Red-Teaming y Escaneo de Vulnerabilidades en Aplicaciones LLM</td><td>1. Configurar la aplicación LLM objetivo como un 'target' en Promptfoo. 2. Seleccionar y configurar plugins y estrategias de ataque (ej. inyección de prompts, fuga de datos, jailbreaks). 3. Ejecutar `npx promptfoo@latest redteam setup` para simular ataques adversarios. 4. Analizar los informes de vulnerabilidades generados por Promptfoo. 5. Remediar las vulnerabilidades identificadas y repetir el proceso.</td><td>Promptfoo CLI, plugins de red-teaming, aplicación LLM objetivo, informes de vulnerabilidades de Promptfoo.</td><td>Días a semanas, dependiendo de la profundidad del red-teaming y la complejidad de la aplicación.</td><td>Identificación y mitigación proactiva de vulnerabilidades de seguridad en aplicaciones LLM antes de su despliegue, fortaleciendo la postura de seguridad de la IA.</td></tr>
<tr><td>Integración Continua (CI/CD) para Pruebas Automatizadas de LLMs</td><td>1. Configurar un pipeline de CI/CD (ej. GitHub Actions, GitLab CI). 2. Integrar el comando `promptfoo eval` en el pipeline para que se ejecute automáticamente en cada cambio de código. 3. Definir criterios de éxito basados en métricas y aserciones de Promptfoo. 4. Monitorear los resultados del pipeline para asegurar que los cambios en prompts o modelos no introduzcan regresiones o vulnerabilidades.</td><td>Promptfoo CLI, plataforma CI/CD (GitHub Actions, GitLab CI), repositorio de código, archivos de configuración de Promptfoo.</td><td>Días para la configuración inicial, luego ejecución automática en cada ciclo de CI/CD.</td><td>Asegurar la calidad y seguridad continua de las aplicaciones LLM a través de pruebas automatizadas en el ciclo de desarrollo, reduciendo el riesgo de errores en producción.</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD
<table header-row="true">
<tr><td>Benchmark</td><td>Score/Resultado</td><td>Fecha</td><td>Fuente</td><td>Comparativa</td></tr>
<tr><td>Humanity's Last Exam (HLE)</td><td>Permite ejecutar evaluaciones contra HLE, un benchmark desafiante con preguntas expertas en más de 100 temas.</td><td>Desconocido (capacidad disponible)</td><td>promptfoo.dev/docs/guides/hle-benchmark</td><td>Permite a los usuarios comparar el rendimiento de sus LLMs contra un benchmark reconocido.</td></tr>
<tr><td>Comparación de Modelos Open-Source (DeepSeek, Mistral, Qwen, Llama)</td><td>Permite comparar el rendimiento de estos modelos en datos personalizados del usuario.</td><td>Desconocido (capacidad disponible)</td><td>promptfoo.dev/docs/guides/compare-open-source-models</td><td>Facilita la selección del modelo open-source más adecuado para casos de uso específicos.</td></tr>
<tr><td>Comparación de Modelos GPT (GPT-5.2 vs GPT-5-mini)</td><td>Permite evaluar capacidades de razonamiento, costos y latencia de respuesta en datos personalizados.</td><td>Desconocido (capacidad disponible)</td><td>promptfoo.dev/docs/guides/choosing-best-gpt-model</td><td>Ayuda a optimizar la elección del modelo GPT para eficiencia y rendimiento.</td></tr>
<tr><td>Evaluación de Facticidad</td><td>Un score de 0 significa fallo, cualquier score positivo se considera aprobado. Los valores del score se usan para ranking y comparación.</td><td>Desconocido (capacidad disponible)</td><td>promptfoo.dev/docs/guides/factuality-eval</td><td>Permite validar la precisión factual de las salidas de LLM contra información de referencia.</td></tr>
<tr><td>Métricas Model-Graded</td><td>Permite la evaluación model-graded para evaluar calidad, seguridad y precisión usando modelos de IA.</td><td>Desconocido (capacidad disponible)</td><td>promptfoo.dev/docs/configuration/expected-outputs/model-graded</td><td>Ofrece una forma avanzada de evaluación donde un LLM evalúa la salida de otro LLM.</td></tr>
<tr><td>Comparación con Braintrust</td><td>Promptfoo es CLI-first, open-source, con pruebas basadas en YAML que se ejecutan localmente y en CI.</td><td>Abril 2026</td><td>braintrust.dev/articles/braintrust-vs-promptfoo</td><td>Braintrust se posiciona como una plataforma más empresarial con un enfoque diferente.</td></tr>
<tr><td>Comparación con DeepEval, RAGAS, Galileo</td><td>Promptfoo se enfoca en evaluación y red-teaming de LLM. DeepEval y RAGAS son frameworks de evaluación. Galileo se enfoca en observabilidad y evaluación empresarial.</td><td>Marzo 2026 (para DeepEval, RAGAS), Diciembre 2025 (para Galileo)</td><td>medium.com/@srinib100/llm-evaluation-frameworks-deepeval-promptfoo-and-giskard-ad4e1547ec1c, galileo.ai/blog/galileo-vs-promptfoo</td><td>Promptfoo se distingue por su enfoque en seguridad y red-teaming, además de la evaluación general.</td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN
<table header-row="true">
<tr><td>Método de Integración</td><td>CLI (Command Line Interface) para ejecución directa y scripting. Librería programática (JavaScript/TypeScript) para integración en aplicaciones y flujos de trabajo. Integración con CI/CD (GitHub Actions, GitLab CI, Jenkins, AWS CodeBuild).</td></tr>
<tr><td>Protocolo</td><td>Model Context Protocol (MCP) para la comunicación con proveedores de LLM y habilitar capacidades de orquestación de herramientas. HTTP/HTTPS para comunicación con APIs de LLM y servicios externos.</td></tr>
<tr><td>Autenticación</td><td>Tokens de API (vía argumentos CLI o variables de entorno). Autenticación basada en magic link para características de la nube. Soporte para autenticación básica HTTP en servidores auto-alojados.</td></tr>
<tr><td>Latencia Típica</td><td>Variable, depende en gran medida de la latencia de los LLMs subyacentes y la complejidad de las evaluaciones. Para pruebas locales, la latencia es mínima. Para pruebas que involucran APIs externas, la latencia es la suma de la latencia de la red y la del proveedor del LLM.</td></tr>
<tr><td>Límites de Rate</td><td>Depende de los límites de rate impuestos por los proveedores de LLM integrados (ej. OpenAI, Anthropic). Promptfoo en sí mismo no impone límites de rate intrínsecos, pero puede ser configurado para respetar los límites de los proveedores.</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS
<table header-row="true">
<tr><td>Tipo de Test</td><td>Herramienta Recomendada</td><td>Criterio de Éxito</td><td>Frecuencia</td></tr>
<tr><td>Evaluación de Prompts y Modelos</td><td>Promptfoo CLI y librería</td><td>Aserciones configurables (pruebas deterministas, evaluación model-graded, puntuación personalizada), métricas derivadas (F1 scores, promedios ponderados), comparación de salidas de LLM lado a lado.</td><td>Continuo, en cada cambio de prompt o modelo, y antes del despliegue.</td></tr>
<tr><td>Red-Teaming y Escaneo de Vulnerabilidades</td><td>Promptfoo (con plugins de red-teaming)</td><td>No detección de vulnerabilidades (inyección de prompts, jailbreaks, fuga de datos, etc.), cumplimiento con OWASP, NIST, EU AI frameworks.</td><td>Continuo, especialmente antes de cada despliegue importante y en ciclos de desarrollo.</td></tr>
<tr><td>Pruebas de Seguridad de IA</td><td>Promptfoo (cubre más de 50 tipos de vulnerabilidades)</td><td>Ausencia de vulnerabilidades críticas, cumplimiento con políticas de seguridad personalizadas.</td><td>Continuo, integrado en el pipeline de CI/CD.</td></tr>
<tr><td>Pruebas Unitarias para Prompts</td><td>Promptfoo CLI y librería</td><td>El prompt genera la salida esperada para un conjunto de entradas específicas.</td><td>Durante el desarrollo de prompts y en cada modificación.</td></tr>
<tr><td>Pruebas de Regresión</td><td>Promptfoo (integrado en CI/CD)</td><td>Mantenimiento del rendimiento y comportamiento esperado del LLM tras cambios en el código o los prompts.</td><td>Automático en cada ciclo de CI/CD.</td></tr>
<tr><td>Pruebas de Facticidad</td><td>Promptfoo (con aserciones de facticidad)</td><td>Score positivo en la evaluación de facticidad, que indica precisión factual de las salidas del LLM.</td><td>Según sea necesario para aplicaciones que requieren alta precisión factual.</td></tr>
<tr><td>Pruebas de Agentes de IA y RAGs</td><td>Promptfoo (con estrategias y plugins específicos)</td><td>Comportamiento esperado del agente, recuperación de información relevante y precisa por parte del RAG.</td><td>Continuo, durante el desarrollo y optimización de agentes y RAGs.</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN
<table header-row="true">
<tr><td>Versión</td><td>Fecha de Lanzamiento</td><td>Estado</td><td>Cambios Clave</td><td>Ruta de Migración</td></tr>
<tr><td>0.119.x (ej. 0.119.11)</td><td>Últimas actualizaciones en Enero 2026</td><td>Activo</td><td>Mejoras continuas en evaluación, red-teaming y soporte de proveedores.</td><td>Actualización vía npm (`npm install -g promptfoo`).</td></tr>
<tr><td>Integración con OpenAI Frontier</td><td>Marzo 2026 (Anuncio de adquisición)</td><td>Activo (en proceso de integración)</td><td>Promptfoo se convierte en parte de OpenAI, integrando sus capacidades de seguridad de IA en la plataforma Frontier de OpenAI.</td><td>Los usuarios existentes de Promptfoo pueden esperar una transición gradual hacia la integración con OpenAI Frontier, con soporte continuo para la versión open-source.</td></tr>
<tr><td>Versión actual (al 30 de abril de 2026)</td><td>Continuamente actualizado</td><td>Activo</td><td>La versión más actual se mantiene a través de actualizaciones frecuentes en el repositorio de GitHub y npm, reflejando mejoras en evaluación, red-teaming y compatibilidad con los últimos LLMs.</td><td>Actualización regular a través de los canales oficiales (npm, GitHub).</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA
<table header-row="true">
<tr><td>Competidor Directo</td><td>Ventaja vs Competidor</td><td>Desventaja vs Competidor</td><td>Caso de Uso Donde Gana</td></tr>
<tr><td>DeepEval</td><td>Promptfoo es más robusto para red-teaming, pruebas de seguridad adversarial y comparación A/B de prompts multi-modelo.</td><td>DeepEval ofrece una experiencia de desarrollo más limpia y "code-first" con APIs intuitivas, mientras que Promptfoo se basa más en archivos YAML y plugins.</td><td>Red-teaming y evaluación de seguridad de LLMs, comparación de prompts y modelos a gran escala.</td></tr>
<tr><td>RAGAS</td><td>Promptfoo ofrece una solución más completa para la evaluación general de LLMs y red-teaming, mientras que RAGAS se especializa en la evaluación de pipelines RAG.</td><td>RAGAS está diseñado específicamente para métricas de evaluación sin referencia en sistemas RAG, lo que puede ser más preciso para ese caso de uso particular.</td><td>Evaluación general de LLMs, pruebas de seguridad, comparación de modelos y prompts más allá de RAG.</td></tr>
<tr><td>Galileo AI</td><td>Promptfoo es una herramienta CLI-first, open-source, con un enfoque en pruebas locales y en CI/CD, más accesible para desarrolladores individuales y equipos pequeños.</td><td>Galileo AI funciona como una plataforma empresarial con un enfoque en observabilidad y evaluación a nivel de empresa, lo que puede ofrecer una solución más integrada para grandes organizaciones.</td><td>Desarrollo y pruebas de LLM para equipos pequeños y medianos, integración en flujos de trabajo de CI/CD existentes.</td></tr>
<tr><td>Braintrust</td><td>Promptfoo es open-source y se enfoca en pruebas locales y en CI/CD con configuraciones basadas en YAML, lo que puede ser preferido por desarrolladores que buscan control y flexibilidad.</td><td>Braintrust se posiciona como una plataforma más empresarial con un enfoque diferente, posiblemente ofreciendo una interfaz de usuario más amigable y características de colaboración avanzadas.</td><td>Evaluación de LLM y red-teaming para desarrolladores y equipos que prefieren una herramienta de código abierto y control granular.</td></tr>
<tr><td>LangSmith, TruLens, Giskard, ChainForge, Humanloop, etc.</td><td>Promptfoo se destaca por su enfoque en la seguridad de IA y el red-teaming, cubriendo una amplia gama de vulnerabilidades y ofreciendo automatización a escala.</td><td>Algunas alternativas pueden ofrecer características específicas o una experiencia de usuario diferente que se adapte mejor a nichos particulares (ej. observabilidad, gestión de experimentos).</td><td>Casos de uso donde la seguridad y el red-teaming son prioridades clave, y se requiere una herramienta robusta para identificar y remediar vulnerabilidades en LLMs.</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)
<table header-row="true">
<tr><td>Capacidad de IA</td><td>Modelo Subyacente</td><td>Nivel de Control</td><td>Personalización Posible</td></tr>
<tr><td>Detección de Inyección de Prompts</td><td>No se basa en un único modelo subyacente, sino en estrategias y plugins de red-teaming que simulan ataques.</td><td>Alto. Los usuarios pueden configurar y personalizar las estrategias de ataque para adaptarse a sus necesidades específicas.</td><td>Amplia personalización a través de la configuración de plugins, estrategias y targets. Permite la creación de cadenas de ataque sofisticadas.</td></tr>
<tr><td>Detección de Jailbreaks</td><td>Similar a la inyección de prompts, utiliza estrategias de red-teaming para identificar y prevenir jailbreaks.</td><td>Alto. Control granular sobre los tipos de jailbreaks a probar y los criterios de éxito.</td><td>Personalización de escenarios de jailbreak y adaptación a nuevos vectores de ataque.</td></tr>
<tr><td>Prevención de Fuga de Datos</td><td>Estrategias de red-teaming diseñadas para simular intentos de exfiltración de datos.</td><td>Alto. Permite definir qué tipos de datos son sensibles y cómo se deben detectar los intentos de fuga.</td><td>Configuración de políticas de seguridad personalizadas para la prevención de fuga de datos.</td></tr>
<tr><td>Red-Teaming contra Agentes de IA</td><td>Utiliza plugins y estrategias adaptadas para probar la seguridad de agentes de IA.</td><td>Alto. Permite definir el comportamiento esperado del agente y los escenarios de ataque.</td><td>Personalización de estrategias de ataque para agentes de IA, incluyendo ataques multi-turno.</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA
<table header-row="true">
<tr><td>Métrica</td><td>Valor Reportado por Comunidad</td><td>Fuente</td><td>Fecha</td></tr>
<tr><td>Eficiencia en Pruebas de Prompts</td><td>"Más rápido y directo" para iterar en prompts y configurar pruebas en YAML. "Resolvió el 80% de mis necesidades de pruebas de IA sin infraestructura personalizada."</td><td>FeaturedCustomers, Medium (Israeli Tech Radar)</td><td>Desconocido, Marzo 2026</td></tr>
<tr><td>Facilidad de Uso para Desarrolladores</td><td>"Developer-Friendly" con características como recargas en vivo y caching.</td><td>Promptfoo.tenereteam.com</td><td>Desconocido</td></tr>
<tr><td>Capacidad de Red-Teaming</td><td>"Potente" para red-teaming y escaneo de vulnerabilidades.</td><td>FeaturedCustomers</td><td>Desconocido</td></tr>
<tr><td>Comparación de Modelos</td><td>Permite comparar diferentes modelos (open-source y propietarios) de manera efectiva.</td><td>Reddit (r/PromptEngineering)</td><td>Hace 5 meses (aprox. Nov 2025)</td></tr>
<tr><td>Integración CI/CD</td><td>"Activo clave para encajar sin problemas en los flujos de trabajo de desarrollo."</td><td>Medium (Vincent Lambert)</td><td>Desconocido</td></tr>
<tr><td>Evaluación de Relevancia de Respuesta</td><td>En una comparación con DeepEval, ambos calificaron la relevancia de la respuesta más baja de lo esperado, indicando la necesidad de refinamiento.</td><td>Nimble Approach Blog</td><td>Marzo 2026</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM
<table header-row="true">
<tr><td>Plan</td><td>Precio</td><td>Límites</td><td>Ideal Para</td><td>ROI Estimado</td></tr>
<tr><td>Open-Source (Comunidad)</td><td>Gratis</td><td>10,000 red team probes/mes. Límites de uso aplicados a modelos auto-alojados.</td><td>Desarrolladores individuales, equipos pequeños, pruebas locales, evaluación básica de LLMs, escaneo de vulnerabilidades inicial.</td><td>Reducción significativa del tiempo y esfuerzo en pruebas de prompts, prevención de vulnerabilidades de seguridad, mejora de la calidad del LLM.</td></tr>
<tr><td>Team Plan</td><td>$50/mes (estimado, basado en alternativas)</td><td>Características de colaboración, resultados compartidos, gestión de equipos.</td><td>Equipos en crecimiento que requieren colaboración y gestión centralizada de pruebas y evaluaciones.</td><td>Mejora de la eficiencia del equipo, estandarización de procesos de prueba, colaboración efectiva en proyectos de IA.</td></tr>
<tr><td>Enterprise</td><td>Precios personalizados</td><td>Funcionalidades adicionales como gestión de equipos, monitoreo continuo, centro de seguridad centralizado, SSO, logs de auditoría.</td><td>Grandes empresas y organizaciones con requisitos de seguridad y cumplimiento estrictos, necesidad de escalar pruebas de IA a nivel organizacional.</td><td>Mitigación de riesgos de seguridad a gran escala, cumplimiento normativo, aceleración del desarrollo de IA segura, protección de la reputación de la marca.</td></tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING
<table header-row="true">
<tr><td>Escenario de Test</td><td>Resultado</td><td>Fortaleza Identificada</td><td>Debilidad Identificada</td></tr>
<tr><td>Inyección de Prompts</td><td>Promptfoo identifica y remedia vulnerabilidades de inyección de prompts, incluyendo ataques directos e indirectos (ej. en agentes de navegación web).</td><td>Capacidad robusta para generar ataques adaptativos y detectar inyecciones de prompts.</td><td>La efectividad depende de la configuración y actualización de las estrategias de ataque.</td></tr>
<tr><td>Jailbreaks</td><td>Promptfoo es efectivo en la identificación de jailbreaks, permitiendo a los desarrolladores mitigar estos riesgos antes del despliegue.</td><td>Amplia cobertura de tipos de jailbreaks y automatización en su detección.</td><td>Requiere una comprensión continua de las nuevas técnicas de jailbreaking para mantener la efectividad.</td></tr>
<tr><td>Fuga de Datos</td><td>La herramienta ayuda a identificar escenarios donde los LLMs podrían filtrar información sensible.</td><td>Capacidad para simular intentos de exfiltración de datos y evaluar la resistencia del sistema.</td><td>La definición de lo que constituye una "fuga de datos" debe ser precisa y adaptada al contexto de la aplicación.</td></tr>
<tr><td>Ataques de Competidores (Plugin)</td><td>El plugin de competidores permite probar si un sistema de IA puede ser influenciado para promocionar productos o servicios de la competencia.</td><td>Identificación de sesgos o vulnerabilidades que podrían llevar a la promoción no deseada de competidores.</td><td>Depende de la configuración del plugin y la relevancia de los competidores definidos.</td></tr>
<tr><td>Cumplimiento OWASP LLM Top 10</td><td>Promptfoo es una herramienta clave para identificar y remediar muchas de las vulnerabilidades descritas en el OWASP LLM Top 10.</td><td>Alineación con estándares de seguridad reconocidos, proporcionando un marco estructurado para la evaluación.</td><td>La implementación completa del cumplimiento requiere un esfuerzo continuo y la adaptación a las actualizaciones del OWASP LLM Top 10.</td></tr>
<tr><td>Red-Teaming Adaptativo</td><td>Genera ataques adaptativos para aplicaciones específicas, no solo pruebas estáticas de jailbreak.</td><td>Alta capacidad de adaptación a las características únicas de cada aplicación de IA.</td><td>Requiere una configuración inicial detallada para maximizar la relevancia de los ataques generados.</td></tr>
</table>

