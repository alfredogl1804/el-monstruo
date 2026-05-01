# BIBLIA DE LANGFUSE v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO

Langfuse es una plataforma de ingeniería de Modelos de Lenguaje Grandes (LLM) de código abierto, diseñada para ayudar a los equipos a construir, monitorear, evaluar y depurar aplicaciones de IA de manera colaborativa. Su enfoque principal es proporcionar visibilidad profunda en el ciclo de vida de desarrollo de LLM, desde el prototipo hasta la producción a escala, permitiendo una mejora continua basada en datos de uso reales.

<table>
  <tr header-row="true">
    <td>Atributo</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Nombre oficial</td>
    <td>Langfuse</td>
  </tr>
  <tr>
    <td>Desarrollador</td>
    <td>Langfuse GmbH (adquirida por ClickHouse Inc.)</td>
  </tr>
  <tr>
    <td>País de Origen</td>
    <td>Alemania (Langfuse GmbH) / Estados Unidos (ClickHouse Inc.)</td>
  </tr>
  <tr>
    <td>Inversión y Financiamiento</td>
    <td>Ronda Seed de $4M (Noviembre 2023) de Lightspeed Venture Partners, La Famiglia y Y Combinator. Adquirida por ClickHouse Inc. en Enero de 2026.</td>
  </tr>
  <tr>
    <td>Modelo de Precios</td>
    <td>Nivel gratuito (Free tier) con 50k observaciones/mes; no requiere tarjeta de crédito. Modelos de precios empresariales disponibles bajo consulta.</td>
  </tr>
  <tr>
    <td>Posicionamiento Estratégico</td>
    <td>Plataforma de ingeniería LLM de código abierto que cubre el ciclo completo de desarrollo de aplicaciones de IA, desde la observabilidad y gestión de prompts hasta la evaluación y experimentación. Destaca por su flexibilidad, no bloqueo de datos y soporte para cualquier stack tecnológico.</td>
  </tr>
  <tr>
    <td>Gráfico de Dependencias</td>
    <td>Funciona con cualquier lenguaje y framework que soporte instrumentación OpenTelemetry (OTel). Ofrece más de 80 integraciones con SDKs nativos, frameworks de agentes y proveedores de modelos.</td>
  </tr>
  <tr>
    <td>Matriz de Compatibilidad</td>
    <td><b>Lenguajes (vía OTel):</b> Python (SDK Nativo), TypeScript (SDK Nativo), Go, Java, .NET, Ruby, PHP, Swift.<br><b>Frameworks de Agentes:</b> LangChain, Vercel AI SDK, LiteLLM, Pydantic AI, Google ADK, CrewAI, LiveKit, etc.<br><b>Proveedores de Modelos:</b> OpenAI, Anthropic, Amazon Bedrock, Azure OpenAI, Mistral AI, Google Gemini, xAI, vLLM, Groq, etc.</td>
  </tr>
  <tr>
    <td>Acuerdos de Nivel de Servicio (SLOs)</td>
    <td>99.9% de tiempo de actividad (uptime) reportado.</td>
  </tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA

Langfuse se compromete con la transparencia y la seguridad, ofreciendo un modelo de gobernanza que prioriza la privacidad de los datos y el cumplimiento normativo. Su naturaleza de código abierto y las certificaciones de seguridad refuerzan la confianza en la plataforma.

<table>
  <tr header-row="true">
    <td>Atributo</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Licencia</td>
    <td>Licencia MIT para todas las características del producto.</td>
  </tr>
  <tr>
    <td>Política de Privacidad</td>
    <td>La página principal menciona el uso de cookies y la gestión de preferencias de privacidad. Se adhiere a GDPR. Se requeriría una revisión de su política de privacidad completa para detalles específicos.</td>
  </tr>
  <tr>
    <td>Cumplimiento y Certificaciones</td>
    <td>SOC 2 Tipo II, ISO 27001, GDPR, Regiones de Datos en la UE y EE. UU., Elegible para HIPAA.</td>
  </tr>
  <tr>
    <td>Historial de Auditorías y Seguridad</td>
    <td>Las certificaciones SOC 2 Tipo II e ISO 27001 implican auditorías de seguridad regulares y exitosas. No se detalla un historial público específico de auditorías.</td>
  </tr>
  <tr>
    <td>Respuesta a Incidentes</td>
    <td>No se especifica públicamente un plan detallado de respuesta a incidentes en la información disponible.</td>
  </tr>
  <tr>
    <td>Matriz de Autoridad de Decisión</td>
    <td>No se detalla públicamente.</td>
  </tr>
  <tr>
    <td>Política de Obsolescencia</td>
    <td>No se detalla públicamente.</td>
  </tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA

Langfuse promueve un modelo mental centrado en la **observabilidad de ciclo completo** para aplicaciones de LLM. Esto implica ver el desarrollo de IA como un proceso iterativo de lanzamiento, observación y mejora continua. La maestría en Langfuse se logra al entender cómo cada componente de una aplicación LLM (llamadas a modelos, herramientas, pasos de recuperación) contribuye al resultado final, permitiendo una depuración eficiente y una optimización basada en datos reales de producción.

<table>
  <tr header-row="true">
    <td>Atributo</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Paradigma Central</td>
    <td>Observabilidad de ciclo de vida completo para aplicaciones LLM: construir, monitorear, evaluar y depurar. Enfoque en la mejora continua basada en datos de producción.</td>
  </tr>
  <tr>
    <td>Abstracciones Clave</td>
    <td><b>Trazas (Traces):</b> Representación jerárquica de cada llamada a LLM, invocación de herramientas y pasos de recuperación. Permite una visibilidad profunda del flujo de ejecución.<br><b>Spans:</b> Unidades individuales dentro de una traza que representan operaciones específicas.<br><b>Evaluaciones (Evals):</b> Mecanismos para medir la calidad de las salidas del modelo, incluyendo LLM-as-a-judge, funciones heurísticas y revisión humana.<br><b>Gestión de Prompts:</b> Separación de prompts del código para facilitar la iteración y el despliegue.<br><b>Experimentos:</b> Definición y ejecución de casos de prueba para comparar el rendimiento de diferentes modelos o prompts.</td>
  </tr>
  <tr>
    <td>Patrones de Pensamiento Recomendados</td>
    <td>Pensamiento iterativo y basado en datos para el desarrollo de LLM. Enfoque en la depuración proactiva y la identificación temprana de problemas. Colaboración en equipo para la mejora de prompts y la anotación humana. Utilización de la instrumentación OpenTelemetry para una observabilidad estándar.</td>
  </tr>
  <tr>
    <td>Anti-patrones a Evitar</td>
    <td>Desarrollo de LLM sin visibilidad del comportamiento interno. Ignorar la importancia de la evaluación continua y la retroalimentación humana. Gestión manual y desorganizada de prompts. No aprovechar las capacidades de auto-hosting o las APIs para la automatización.</td>
  </tr>
  <tr>
    <td>Curva de Aprendizaje</td>
    <td>Moderada. Requiere familiaridad con conceptos de observabilidad y desarrollo de LLM. La documentación y los SDKs facilitan la integración, pero la maestría en la interpretación de trazas y la configuración de evaluaciones puede requerir práctica.</td>
  </tr>
</table>

## L04 — CAPACIDADES TÉCNICAS

Langfuse ofrece un conjunto robusto de capacidades técnicas diseñadas para la ingeniería de LLM, abarcando desde la observabilidad fundamental hasta herramientas avanzadas para la evaluación y gestión de prompts. Su arquitectura está optimizada para manejar grandes volúmenes de datos generados por aplicaciones de IA.

<table>
  <tr header-row="true">
    <td>Capacidad</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Capacidades Core</td>
    <td><b>Trazado (Tracing):</b> Captura jerárquica de cada llamada a LLM, invocación de herramientas y pasos de recuperación. Soporte para OpenTelemetry.<br><b>Observabilidad:</b> Visibilidad profunda del comportamiento de las aplicaciones LLM, incluyendo entradas, salidas, llamadas a herramientas, reintentos y uso de tokens.<br><b>Gestión de Sesiones:</b> Agrupación de trazas relacionadas en sesiones para un análisis contextual.<br><b>Métricas:</b> Monitoreo de costos, latencia y calidad con paneles de control y alertas automatizadas.</td>
  </tr>
  <tr>
    <td>Capacidades Avanzadas</td>
    <td><b>Evaluación (Evaluation):</b> Soporte para LLM-as-a-judge, funciones heurísticas y revisión humana. Ejecución de evaluadores en datos de producción o durante experimentos.<br><b>Gestión de Prompts:</b> Separación de prompts del código con despliegues y reversiones con un solo clic. Permite la colaboración en la mejora de prompts.<br><b>Experimentación:</b> Definición de casos de prueba y ejecución de experimentos para comparar resultados lado a lado.<br><b>Anotación Humana:</b> Flujos de trabajo colaborativos Human-in-the-Loop para revisar trazas y crear conjuntos de datos dorados.<br><b>APIs y Exportaciones:</b> APIs REST para todas las funcionalidades, SDK de consulta y exportación a almacenamiento de objetos S3.</td>
  </tr>
  <tr>
    <td>Capacidades Emergentes (Abril 2026)</td>
    <td><b>Servidor MCP (Model Context Protocol) nativo con capacidades de escritura:</b> Permite a los agentes de IA obtener y actualizar prompts directamente. (Según Changelog, Noviembre 2025).<br><b>Langfuse Cloud Japan:</b> Expansión de la infraestructura de la nube a Japón (Según Changelog, 4 días antes del 30 de Abril de 2026).<br><b>Boolean LLM-as-a-Judge Scores:</b> Nuevas capacidades de evaluación (Según Changelog, 3 semanas antes del 30 de Abril de 2026).</td>
  </tr>
  <tr>
    <td>Limitaciones Técnicas Confirmadas</td>
    <td>La documentación no especifica limitaciones técnicas explícitas más allá de la necesidad de instrumentación OTel para una integración completa. Sin embargo, como cualquier sistema de observabilidad, el rendimiento puede depender de la configuración y el volumen de datos.</td>
  </tr>
  <tr>
    <td>Roadmap Público</td>
    <td>El sitio web menciona un roadmap público que es un documento vivo y se actualiza a medida que avanzan. Se alienta a los usuarios a añadir nuevas ideas en GitHub o votar sobre las existentes. El roadmap incluye elementos ya lanzados y en desarrollo activo. Algunos elementos recientes lanzados (hasta abril de 2026) incluyen Langfuse Cloud Japan, Experimentos como Concepto de Primera Clase, Puntuaciones Booleanas LLM-as-a-Judge, Actualizaciones de Dashboards, Puntuaciones Categóricas LLM-as-a-Judge, Simplificación de Langfuse para Escala, Langfuse CLI, Evaluación de Operaciones Individuales, Ejecución de Experimentos en Conjuntos de Datos Versionados y Salidas Corregidas para Trazas y Observaciones. Los elementos en desarrollo activo se centran en la observabilidad de agentes, evaluaciones, playground, UI/UX e infraestructura/plataforma de datos, incluyendo la simplificación del modelo de datos central para aumentar el rendimiento y la escalabilidad, y la mejora de la UI de trazado para agentes complejos.
  </tr>
</table>

## L05 — DOMINIO TÉCNICO

Langfuse se basa en una arquitectura robusta y escalable, diseñada para manejar la complejidad y el volumen de datos de las aplicaciones LLM. Utiliza tecnologías de vanguardia para garantizar un rendimiento óptimo y una integración flexible.

<table>
  <tr header-row="true">
    <td>Atributo</td>
    <td>Descripción</td>
  </tr>
  <tr>
    <td>Stack Tecnológico</td>
    <td><b>Base de Datos:</b> ClickHouse (OLAP database) para el almacenamiento y consulta de datos a escala.<br><b>Cola de Mensajes:</b> Redis para la ingesta asíncrona de eventos.<br><b>Almacenamiento de Objetos:</b> S3/Blob storage para payloads grandes.<br><b>Cache:</b> Prompts con cache en el borde (edge-cached prompts).</td>
  </tr>
  <tr>
    <td>Arquitectura Interna</td>
    <td>Diseñada para la ingesta eficiente de datos de eventos a través de SDKs y API. Modelo de datos optimizado para patrones de acceso a ClickHouse, eliminando uniones y deduplicación en tiempo de lectura. Se está moviendo hacia un modelo de datos inmutable y solo de observación para alinearse mejor con agentes complejos y escalar la plataforma.</td>
  </tr>
  <tr>
    <td>Protocolos Soportados</td>
    <td>OpenTelemetry (OTel) para instrumentación. Protocolo de Contexto del Modelo (MCP) para interacción con agentes de IA.</td>
  </tr>
  <tr>
    <td>Formatos de Entrada/Salida</td>
    <td>Entradas y salidas de LLM, invocaciones de herramientas, datos de recuperación. Soporte para esquemas de datos de entrada/salida de modelos para aumentar la interoperabilidad.</td>
  </tr>
  <tr>
    <td>APIs Disponibles</td>
    <td>APIs REST completas para todas las funcionalidades. SDK de consulta para acceso programático a los datos.</td>
  </tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS

Langfuse facilita la implementación de flujos de trabajo operativos para el desarrollo y mantenimiento de aplicaciones LLM, permitiendo a los equipos depurar, evaluar y mejorar sus sistemas de manera eficiente. A continuación, se presentan algunos casos de uso reales:

<table>
  <tr header-row="true">
    <td>Caso de Uso</td>
    <td>Pasos Exactos</td>
    <td>Herramientas Necesarias</td>
    <td>Tiempo Estimado</td>
    <td>Resultado Esperado</td>
  </tr>
  <tr>
    <td>Análisis de Errores en Aplicaciones LLM</td>
    <td>1. Instrumentar la aplicación LLM con el SDK de Langfuse para generar trazas detalladas. 2. Navegar al dashboard de Langfuse para visualizar las trazas. 3. Filtrar y revisar trazas que muestren comportamientos inesperados (ej. alucinaciones, respuestas irrelevantes). 4. Clasificar los errores identificados para entender patrones y causas raíz.</td>
    <td>SDK de Langfuse, Plataforma Langfuse (módulo de Observabilidad).</td>
    <td>Variable (depende de la complejidad y volumen de las trazas, desde minutos para casos específicos hasta horas para análisis profundos).</td>
    <td>Identificación y clasificación de errores comunes en LLM, obtención de insights accionables para la mejora del modelo y el prompt.</td>
  </tr>
  <tr>
    <td>Evaluaciones Automatizadas de Modelos LLM</td>
    <td>1. Definir criterios de éxito y métricas para la evaluación. 2. Configurar evaluadores automatizados en Langfuse (ej. LLM-as-a-judge, funciones heurísticas) para ejecutarse en datos de producción o conjuntos de datos de prueba. 3. Monitorear los resultados de las evaluaciones en los paneles de control de Langfuse. 4. Ajustar prompts o modelos basándose en los resultados para mejorar la calidad.</td>
    <td>Plataforma Langfuse (módulo de Evaluación, evaluadores automatizados), Conjuntos de datos de prueba/producción.</td>
    <td>Configuración inicial (horas), ejecución continua y monitoreo (diario/semanal).</td>
    <td>Medición escalable y monitoreo continuo de la calidad del modelo, detección temprana de regresiones y validación de mejoras.</td>
  </tr>
  <tr>
    <td>Observabilidad y Evaluación de Pipelines RAG</td>
    <td>1. Instrumentar el pipeline RAG (recuperación y generación) con el SDK de Langfuse. 2. Configurar métricas especializadas en Langfuse para RAG (ej. relevancia de recuperación, fidelidad de la respuesta, completitud del contexto). 3. Analizar las trazas y métricas para identificar cuellos de botella o fallos en la recuperación de información o en la generación de respuestas. 4. Iterar en los componentes del RAG (ej. base de datos de conocimiento, prompt de generación) para optimizar el rendimiento.</td>
    <td>SDK de Langfuse, Plataforma Langfuse (módulo de Observabilidad y Evaluación), Base de datos de conocimiento/vectorial.</td>
    <td>Configuración (horas), análisis y optimización iterativa (días/semanas).</td>
    <td>Medición precisa del rendimiento de pipelines RAG, identificación de áreas de mejora en la recuperación y generación, y optimización del sistema RAG.</td>
  </tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD

Langfuse enfatiza la importancia de la evidencia empírica y la reproducibilidad en el desarrollo de LLM, proporcionando herramientas para realizar benchmarks y evaluaciones sistemáticas. A continuación, se presenta un benchmark de rendimiento para la gestión de prompts.

<table>
  <tr header-row="true">
    <td>Benchmark</td>
    <td>Score/Resultado</td>
    <td>Fecha</td>
    <td>Fuente</td>
    <td>Comparativa</td>
  </tr>
  <tr>
    <td>Rendimiento de Gestión de Prompts (sin caché)</td>
    <td><b>Conteo:</b> 1000.000000<br><b>Media:</b> 0.039335 seg<br><b>Desviación Estándar:</b> 0.014172 seg<br><b>Mínimo:</b> 0.032702 seg<br><b>Percentil 25%:</b> 0.035387 seg<br><b>Percentil 50%:</b> 0.037030 seg<br><b>Percentil 75%:</b> 0.041111 seg<br><b>Percentil 99%:</b> 0.068914 seg<br><b>Máximo:</b> 0.409609 seg</td>
    <td>Desconocida (última prueba de rendimiento mencionada en la documentación)</td>
    <td>Documentación oficial de Langfuse: Prompt Management Performance Benchmark</td>
    <td>La latencia no es crítica en la práctica ya que el prompt se almacena en caché del lado del cliente en los SDKs. Los valores absolutos pueden variar según la geografía y la carga. Se recomienda usar las estadísticas para comparar mejoras relativas entre versiones de SDK o configuraciones de caché.</td>
  </tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN

La arquitectura de integración de Langfuse está diseñada para ser flexible y compatible con una amplia gama de tecnologías, utilizando estándares abiertos como OpenTelemetry para facilitar la conexión con diversas aplicaciones y servicios.

<table>
  <tr header-row="true">
    <td>Método de Integración</td>
    <td>Protocolo</td>
    <td>Autenticación</td>
    <td>Latencia Típica</td>
    <td>Límites de Rate</td>
  </tr>
  <tr>
    <td>SDKs Nativos (Python, TypeScript, Go, Java, .NET, Ruby, PHP, Swift)</td>
    <td>HTTP/HTTPS (comunicación con la API de Langfuse)</td>
    <td>Claves API (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)</td>
    <td>Mínimo impacto, ya que la instrumentación se ejecuta en segundo plano y las solicitudes se envían por lotes. La latencia de recuperación de prompts sin caché es de ~39ms (media).</td>
    <td>No especificados públicamente, pero la plataforma está diseñada para escalar a miles de millones de observaciones mensuales.</td>
  </tr>
  <tr>
    <td>OpenTelemetry (OTel)</td>
    <td>Protocolo OTLP (OpenTelemetry Protocol)</td>
    <td>N/A (OTel se enfoca en la recolección de telemetría, la autenticación se maneja a nivel de la plataforma Langfuse)</td>
    <td>Diseñado para ser asíncrono y no bloquear la aplicación, minimizando el impacto en la latencia.</td>
    <td>Gestionado por la infraestructura de Langfuse, diseñada para alta ingesta.</td>
  </tr>
  <tr>
    <td>APIs REST</td>
    <td>HTTP/HTTPS</td>
    <td>Claves API (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)</td>
    <td>Variable, depende de la complejidad de la consulta y la carga del servidor.</td>
    <td>No especificados públicamente.</td>
  </tr>
  <tr>
    <td>Servidor MCP (Model Context Protocol)</td>
    <td>Protocolo MCP</td>
    <td>Claves API (a través de la configuración del servidor MCP)</td>
    <td>Diseñado para una interacción rápida con agentes de IA.</td>
    <td>No especificados públicamente.</td>
  </tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS

Langfuse proporciona un marco integral para la verificación y prueba de aplicaciones LLM, centrándose en la evaluación continua y la detección temprana de problemas. Esto se logra a través de una combinación de métodos de evaluación automatizados y manuales, integrados en el ciclo de desarrollo.

<table>
  <tr header-row="true">
    <td>Tipo de Test</td>
    <td>Herramienta Recomendada</td>
    <td>Criterio de Éxito</td>
    <td>Frecuencia</td>
  </tr>
  <tr>
    <td>Evaluaciones Automatizadas (LLM-as-a-Judge)</td>
    <td>Plataforma Langfuse (módulo de Evaluación), LLM-as-a-judge configurados.</td>
    <td>Puntuaciones (numéricas, categóricas, booleanas) que cumplen con umbrales predefinidos para calidad, relevancia, fidelidad, etc.</td>
    <td>Continuo en producción, durante experimentos, o en pipelines de CI/CD.</td>
  </tr>
  <tr>
    <td>Evaluaciones Automatizadas (Heurísticas)</td>
    <td>Plataforma Langfuse (módulo de Evaluación), funciones heurísticas personalizadas.</td>
    <td>Resultados que pasan reglas lógicas o patrones predefinidos (ej. detección de palabras clave, formato de salida).</td>
    <td>Continuo en producción, durante experimentos, o en pipelines de CI/CD.</td>
  </tr>
  <tr>
    <td>Revisión Humana y Anotación</td>
    <td>Plataforma Langfuse (módulo de Anotación Humana).</td>
    <td>Consistencia en las etiquetas, alta calidad de los datos anotados, acuerdo entre anotadores.</td>
    <td>Periódica, especialmente para la creación de datasets dorados y la validación de evaluadores automatizados.</td>
  </tr>
  <tr>
    <td>Pruebas de Regresión (con Datasets)</td>
    <td>Plataforma Langfuse (módulo de Experimentos), datasets versionados.</td>
    <td>Métricas de rendimiento (precisión, latencia, costo) que se mantienen estables o mejoran entre versiones.</td>
    <td>Durante el desarrollo de nuevas características o cambios significativos en el modelo/prompt.</td>
  </tr>
  <tr>
    <td>Análisis de Errores</td>
    <td>Plataforma Langfuse (módulo de Observabilidad).</td>
    <td>Identificación y clasificación de tipos de errores (alucinaciones, irrelevancia, formato) para informar mejoras.</td>
    <td>Continuo en producción, como parte del proceso de depuración.</td>
  </tr>
  <tr>
    <td>Pruebas de Penetración</td>
    <td>Expertos de seguridad externos e independientes.</td>
    <td>Identificación y mitigación de vulnerabilidades de seguridad.</td>
    <td>Regularmente (ej. anualmente), según las políticas de seguridad de la empresa.</td>
  </tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN

Langfuse mantiene un ciclo de desarrollo activo con lanzamientos frecuentes que introducen nuevas características, mejoras y correcciones. La plataforma también proporciona guías de migración para facilitar las actualizaciones entre versiones significativas.

<table>
  <tr header-row="true">
    <td>Versión</td>
    <td>Fecha de Lanzamiento</td>
    <td>Estado</td>
    <td>Cambios Clave</td>
    <td>Ruta de Migración</td>
  </tr>
  <tr>
    <td>v3.172.0</td>
    <td>29 de Abril de 2026</td>
    <td>Estable</td>
    <td>Adición de modo de filtro 'none' para etiquetas en la barra lateral, ingesta de metadatos de experimentos aplanados, mejoras de rendimiento en ClickHouse, correcciones en el parser de salida y límites en el número de nombres y valores de puntuación categóricos.</td>
    <td>Actualización incremental desde v3.171.0.</td>
  </tr>
  <tr>
    <td>v3.171.0</td>
    <td>27 de Abril de 2026</td>
    <td>Estable</td>
    <td>Permite `source=ANNOTATION` en `POST /api/public/scores`, añade `gpt-5.5` a precios de modelos, correcciones en la exportación de PostHog y en las consultas de ClickHouse.</td>
    <td>Actualización incremental desde v3.170.0.</td>
  </tr>
  <tr>
    <td>v3.170.0</td>
    <td>23 de Abril de 2026</td>
    <td>Estable</td>
    <td>Advertencia sobre caracteres especiales no codificados en `DATABASE_URL`, emisión de métricas `.rate` y `.time` con etiquetas de shard para DataDog, soporte para activar evaluaciones en experimentos, adición de endpoints públicos inestables para evaluaciones, y un selector de región en el menú de usuario.</td>
    <td>Actualización incremental desde v3.169.0.</td>
  </tr>
  <tr>
    <td>v4 SDK</td>
    <td>Marzo de 2026</td>
    <td>Estable</td>
    <td>Reescritura completa del SDK.</td>
    <td>Se requiere seguir la guía de migración de v4 para actualizar el código.</td>
  </tr>
</table>

## L11 — MARCO DE COMPETENCIA

Langfuse opera en un mercado competitivo de plataformas de ingeniería y observabilidad de LLM. Sus principales competidores ofrecen funcionalidades similares, pero Langfuse se distingue por su enfoque de código abierto, flexibilidad y énfasis en la portabilidad de datos.

<table>
  <tr header-row="true">
    <td>Competidor Directo</td>
    <td>Ventaja vs Competidor</td>
    <td>Desventaja vs Competidor</td>
    <td>Caso de Uso Donde Gana</td>
  </tr>
  <tr>
    <td>LangSmith (OpenAI)</td>
    <td>Mayor integración nativa con el ecosistema de LangChain.</td>
    <td>Menos agnóstico al framework, puede generar un bloqueo con el proveedor. No es de código abierto.</td>
    <td>Equipos que ya están profundamente invertidos en LangChain y buscan una integración sin fisuras dentro de ese ecosistema.</td>
  </tr>
  <tr>
    <td>Arize AI (Arize Phoenix)</td>
    <td>Plataforma ML Observability más amplia que cubre modelos tradicionales y LLM.</td>
    <td>Puede ser más complejo y costoso si el enfoque es exclusivamente en LLM. No es de código abierto.</td>
    <td>Empresas con un portafolio diverso de modelos de ML (tradicionales y LLM) que buscan una solución de observabilidad unificada.</td>
  </tr>
  <tr>
    <td>Helicone</td>
    <td>Enfoque en la optimización de costos y rendimiento de API de LLM, con características como caching y reintentos.</td>
    <td>Puede tener un conjunto de características de observabilidad y evaluación menos completo que Langfuse.</td>
    <td>Equipos que priorizan la optimización de costos y la gestión de proxies para sus llamadas a API de LLM.</td>
  </tr>
  <tr>
    <td>Braintrust</td>
    <td>Enfoque en la evaluación de prompts y la generación de datasets sintéticos.</td>
    <td>Puede ser menos maduro en la observabilidad de trazas complejas en comparación con Langfuse.</td>
    <td>Equipos que buscan herramientas avanzadas para la evaluación y mejora iterativa de prompts.</td>
  </tr>
  <tr>
    <td>MLflow</td>
    <td>Plataforma completa de MLOps que abarca todo el ciclo de vida del ML, incluyendo seguimiento de experimentos, gestión de modelos y despliegue.</td>
    <td>Su enfoque en LLM es más reciente y puede no ser tan especializado como Langfuse en la observabilidad de trazas de LLM.</td>
    <td>Equipos que ya utilizan MLflow para sus flujos de trabajo de ML y buscan extender sus capacidades a LLM dentro de la misma plataforma.</td>
  </tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)

Langfuse, como plataforma de ingeniería de LLM, no es un modelo de IA en sí mismo, sino una herramienta que permite la **inyección y gestión de capacidades de IA** en otras aplicaciones. Facilita la integración de diversos modelos de IA y proporciona las herramientas para monitorear y optimizar su rendimiento.

<table>
  <tr header-row="true">
    <td>Capacidad de IA</td>
    <td>Modelo Subyacente</td>
    <td>Nivel de Control</td>
    <td>Personalización Posible</td>
  </tr>
  <tr>
    <td>Observabilidad de LLM</td>
    <td>N/A (Langfuse observa el comportamiento de los LLM, no es un LLM)</td>
    <td>Alto. Permite a los desarrolladores ver el flujo completo de ejecución de sus aplicaciones LLM, incluyendo entradas, salidas, llamadas a herramientas y uso de tokens.</td>
    <td>Personalización de dashboards, filtros, alertas y la forma en que se visualizan las trazas.</td>
  </tr>
  <tr>
    <td>Evaluación de LLM</td>
    <td>Modelos de lenguaje grandes (LLM) externos (para LLM-as-a-judge), funciones heurísticas definidas por el usuario.</td>
    <td>Alto. Los usuarios pueden definir sus propios criterios de evaluación, configurar LLM-as-a-judge con prompts específicos y crear funciones heurísticas personalizadas.</td>
    <td>Definición de métricas personalizadas, prompts para LLM-as-a-judge, y lógica para evaluadores heurísticos.</td>
  </tr>
  <tr>
    <td>Gestión de Prompts</td>
    <td>N/A (Langfuse gestiona los prompts, no los genera)</td>
    <td>Alto. Permite la creación, versionado, despliegue y reversión de prompts. Los prompts pueden ser separados del código.</td>
    <td>Creación de plantillas de prompts, variables dinámicas, y flujos de trabajo de aprobación.</td>
  </tr>
  <tr>
    <td>Experimentación con LLM</td>
    <td>Modelos de lenguaje grandes (LLM) externos.</td>
    <td>Alto. Los usuarios pueden definir conjuntos de datos de prueba, ejecutar experimentos con diferentes modelos y prompts, y comparar los resultados.</td>
    <td>Configuración de experimentos, selección de modelos y prompts, definición de métricas de comparación.</td>
  </tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA

Langfuse se nutre de una comunidad activa y proporciona métricas claras sobre el rendimiento de las aplicaciones LLM en entornos reales. La plataforma permite capturar y analizar el feedback de los usuarios, lo que contribuye a una mejora continua y a una experiencia comunitaria robusta.

<table>
  <tr header-row="true">
    <td>Métrica</td>
    <td>Valor Reportado por Comunidad</td>
    <td>Fuente</td>
    <td>Fecha</td>
  </tr>
  <tr>
    <td>Estrellas en GitHub</td>
    <td>26.4k+</td>
    <td>Página principal de Langfuse / GitHub</td>
    <td>30 de Abril de 2026</td>
  </tr>
  <tr>
    <td>Miembros en Discord</td>
    <td>5,000+</td>
    <td>Página principal de Langfuse</td>
    <td>30 de Abril de 2026</td>
  </tr>
  <tr>
    <td>Hilos de Preguntas y Respuestas en la Comunidad</td>
    <td>1.3k+</td>
    <td>Página principal de Langfuse</td>
    <td>30 de Abril de 2026</td>
  </tr>
  <tr>
    <td>Hilos de Roadmap</td>
    <td>1.1k+</td>
    <td>Página principal de Langfuse</td>
    <td>30 de Abril de 2026</td>
  </tr>
  <tr>
    <td>Observaciones Procesadas</td>
    <td>10+ mil millones por mes</td>
    <td>Página principal de Langfuse</td>
    <td>30 de Abril de 2026</td>
  </tr>
  <tr>
    <td>Instalaciones de SDK</td>
    <td>50M+ por mes</td>
    <td>Página principal de Langfuse</td>
    <td>30 de Abril de 2026</td>
  </tr>
  <tr>
    <td>Clientes</td>
    <td>2300+</td>
    <td>Página principal de Langfuse</td>
    <td>30 de Abril de 2026</td>
  </tr>
  <tr>
    <td>Tiempo de Actividad (Uptime)</td>
    <td>99.9%</td>
    <td>Página principal de Langfuse</td>
    <td>30 de Abril de 2026</td>
  </tr>
  <tr>
    <td>Feedback de Usuario</td>
    <td>Captura de feedback de usuario y puntuaciones personalizadas (numéricas, categóricas, booleanas) a través del SDK o API de Langfuse.</td>
    <td>Documentación de Langfuse (User Feedback, Discussions de GitHub)</td>
    <td>30 de Abril de 2026</td>
  </tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM

La economía operativa de Langfuse se basa en un modelo freemium con una clara estrategia de Go-to-Market (GTM) que capitaliza su naturaleza de código abierto y su enfoque en la comunidad de desarrolladores. Esto permite una adopción amplia y una escalabilidad para empresas de todos los tamaños.

<table>
  <tr header-row="true">
    <td>Plan</td>
    <td>Precio</td>
    <td>Límites</td>
    <td>Ideal Para</td>
    <td>ROI Estimado</td>
  </tr>
  <tr>
    <td>Free Tier</td>
    <td>Gratuito</td>
    <td>50k observaciones/mes. No requiere tarjeta de crédito.</td>
    <td>Desarrolladores individuales, startups, pruebas de concepto, proyectos de código abierto.</td>
    <td>Alto, permite la experimentación y el desarrollo inicial sin costo, reduciendo la barrera de entrada.</td>
  </tr>
  <tr>
    <td>Enterprise / Cloud</td>
    <td>Basado en uso, precios personalizados.</td>
    <td>Diseñado para escalar a miles de millones de observaciones mensuales.</td>
    <td>Grandes empresas, equipos con altos volúmenes de tráfico, requisitos de seguridad y cumplimiento avanzados (SOC 2 Tipo II, ISO 27001, HIPAA).</td>
    <td>Mejora significativa en la eficiencia de depuración, reducción de costos operativos de LLM, aceleración del ciclo de desarrollo y mejora de la calidad del producto final.</td>
  </tr>
  <tr>
    <td>Self-Hosting</td>
    <td>Gratuito (código abierto), costos de infraestructura propios.</td>
    <td>Escalabilidad limitada por la infraestructura del usuario.</td>
    <td>Empresas que requieren control total sobre sus datos, personalización profunda, o que operan en entornos con estrictas regulaciones de datos.</td>
    <td>Control total sobre los datos y la infraestructura, reducción de la dependencia de proveedores externos, flexibilidad para adaptar la plataforma a necesidades específicas.</td>
  </tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING

Langfuse proporciona las herramientas necesarias para realizar benchmarking empírico y facilitar actividades de red teaming, permitiendo a los equipos evaluar el rendimiento y la robustez de sus aplicaciones LLM en escenarios adversos y reales. Esto es crucial para identificar debilidades y fortalecer la seguridad y confiabilidad de los sistemas de IA.

<table>
  <tr header-row="true">
    <td>Escenario de Test</td>
    <td>Resultado</td>
    <td>Fortaleza Identificada</td>
    <td>Debilidad Identificada</td>
  </tr>
  <tr>
    <td>Pruebas de Inyección de Prompts (Prompt Injection)</td>
    <td>Identificación de prompts maliciosos que manipulan el comportamiento del LLM.</td>
    <td>Capacidad de trazar y registrar todas las interacciones del LLM, permitiendo la revisión post-mortem de ataques de inyección.</td>
    <td>Dependencia de la configuración de evaluadores para detectar automáticamente la inyección de prompts.</td>
  </tr>
  <tr>
    <td>Generación de Contenido Tóxico o Sesgado</td>
    <td>Detección de salidas del LLM que contienen lenguaje ofensivo, sesgado o inapropiado.</td>
    <td>Uso de evaluadores LLM-as-a-judge o heurísticos para puntuar la toxicidad/sesgo de las respuestas.</td>
    <td>La efectividad depende de la calidad y el entrenamiento de los evaluadores.</td>
  </tr>
  <tr>
    <td>Fugas de Información Sensible</td>
    <td>Identificación de casos en los que el LLM expone datos confidenciales o privados.</td>
    <td>Registro detallado de entradas y salidas del LLM, facilitando la auditoría de posibles fugas.</td>
    <td>Requiere una revisión manual o evaluadores específicos para detectar patrones de fuga de datos.</td>
  </tr>
  <tr>
    <td>Denegación de Servicio (DoS) por Uso Excesivo de Recursos</td>
    <td>Monitoreo del uso de tokens y latencia para identificar patrones de abuso o ineficiencia.</td>
    <td>Métricas de costo y latencia en tiempo real que alertan sobre picos inusuales.</td>
    <td>No previene directamente el ataque, pero proporciona visibilidad para una respuesta rápida.</td>
  </tr>
  <tr>
    <td>Evaluación de Robustez ante Entradas Adversarias</td>
    <td>Medición del rendimiento del LLM frente a entradas diseñadas para confundirlo o provocar fallos.</td>
    <td>La capacidad de ejecutar experimentos con datasets sintéticos y comparar el rendimiento del modelo.</td>
    <td>La creación de entradas adversarias efectivas puede ser un desafío.</td>
  </tr>
</table>