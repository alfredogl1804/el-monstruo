# BIBLIA DE LLAMA_4 v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO

<table header-row="true">
<tr><td>Nombre oficial</td><td>LLAMA_4 (incluye Llama 4 Scout y Llama 4 Maverick)</td></tr>
<tr><td>Desarrollador</td><td>Meta AI (Meta Platforms, Inc.)</td></tr>
<tr><td>País de Origen</td><td>Estados Unidos (Menlo Park, California)</td></tr>
<tr><td>Inversión y Financiamiento</td><td>Meta ha invertido significativamente en IA. Se estima una inversión de $600 mil millones en infraestructura en EE. UU. durante los próximos tres años (a partir de Nov 2025). En los últimos tres años, la compañía ha gastado aproximadamente $140 mil millones en IA.</td></tr>
<tr><td>Modelo de Precios</td><td>Para Llama 4 Maverick, el costo estimado para inferencia distribuida es de $0.19/Mtok (3:1 blended). En un solo host, se proyecta entre $0.30 - $0.49/Mtok (3:1 blended). Los precios de API varían; por ejemplo, en Azure AI Foundry, Llama4 Maverick 17B Datazone tiene un costo de $0.000275 por token de entrada y $0.0011 por token de salida. OpenRouter reporta $0.35 por 1M tokens de entrada y $0.85 por 1M tokens de salida para Llama 4 Maverick.</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>LLAMA_4 se posiciona como una generación de modelos de lenguaje líderes en inteligencia, velocidad y eficiencia, con un enfoque en la accesibilidad y escalabilidad. Son modelos multimodales nativos con una ventana de contexto de 10M. Meta sigue una estrategia de dos vías: Llama abierto para personalización y despliegue on-premise, y Avocado (mencionado en un snippet como un modelo cerrado de frontera) para capacidades de vanguardia. Se enfoca en el rendimiento, la multimodalidad, los bajos costos y la eficiencia.</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Depende de la infraestructura de Meta AI, incluyendo sus centros de datos y recursos de cómputo. Utiliza una arquitectura Mixture of Experts (MoE).</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Compatible con plataformas de despliegue como Azure AI Foundry y Azure Databricks. Integración con la API de Llama y Llama Stack para desarrollo de aplicaciones.</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>No se especifican SLOs públicos directamente en la información disponible, pero se enfoca en rendimiento y eficiencia para despliegues a gran escala.</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA

<table header-row="true">
<tr><td>Licencia</td><td>Los modelos Llama son de código abierto (open-weight), lo que permite su personalización y despliegue. Se requiere revisar los términos de servicio específicos de Meta Llama.</td></tr>
<tr><td>Política de Privacidad</td><td>Se rige por la política de privacidad de Meta Platforms, Inc. Se enfoca en la protección de datos y la privacidad del usuario en el desarrollo y uso de sus tecnologías de IA.</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>Meta AI implementa sistemas de protección integrales para identificar y mitigar riesgos potenciales, promoviendo un despliegue responsable de la IA.</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>Meta tiene un programa de seguridad y un programa de defensores (Llama Defenders Program) para evaluar la eficacia de los sistemas de IA. Se han realizado evaluaciones de seguridad exhaustivas, como el 'Llama 4 Maverick Security Report', que mostró una tasa de aprobación del 25.5% en más de 50 pruebas. Meta también ha lanzado herramientas como LlamaFirewall y Llama Guard 3 para salvaguardar los agentes de IA contra inyecciones de prompt y desalineación de objetivos.</td></tr>
<tr><td>Respuesta a Incidentes</td><td>Meta ha enfrentado incidentes de seguridad, como la exposición de datos sensibles por un agente de IA (incidente 'Sev-1'). La compañía ha confirmado estos incidentes, indicando que no se manejaron datos de usuario externamente y que tienen procesos para abordar y mitigar tales eventos.</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>Meta utiliza una matriz de gobernanza para mapear las capas de seguridad y las preguntas clave para la junta directiva. Se rigen por pautas éticas y priorizan la seguridad del usuario en el diseño de sus agentes de IA.</td></tr>
<tr><td>Política de Obsolescencia</td><td>No se ha encontrado una política de obsolescencia pública específica para Llama 4. Sin embargo, dado el rápido avance en el campo de la IA, se espera que Meta actualice y reemplace sus modelos con nuevas versiones periódicamente, como se ha visto con las iteraciones anteriores de Llama.</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA

Llama 4 representa un avance significativo en la inteligencia artificial multimodal, diseñado para emular y extender las capacidades cognitivas humanas en el procesamiento de información diversa. Su modelo mental se centra en la integración temprana de datos de texto y visión, permitiendo una comprensión más holística y contextual. La maestría con Llama 4 implica adoptar un enfoque de diseño que aproveche su multimodalidad nativa y su capacidad de contexto extendido para resolver problemas complejos que requieren razonamiento intermodal.

<table header-row="true">
<tr><td>Paradigma Central</td><td>Inteligencia Multimodal Nativamente Integrada (Early Fusion), Procesamiento de Lenguaje Natural y Visión por Computadora.</td></tr>
<tr><td>Abstracciones Clave</td><td>Tokens de texto y visión unificados, ventana de contexto de 10M, arquitectura Mixture of Experts (MoE), modelos Scout y Maverick.</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>Diseño de prompts multimodales, razonamiento contextual extendido, aprovechamiento de la eficiencia de MoE para tareas complejas, iteración rápida con modelos de código abierto.</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>Tratar Llama 4 como un modelo puramente textual, ignorar sus capacidades multimodales, subutilizar la ventana de contexto extendida, no considerar las implicaciones de seguridad en el despliegue.</td></tr>
<tr><td>Curva de Aprendizaje</td><td>Moderada para desarrolladores familiarizados con LLMs, pero requiere adaptación para explotar plenamente sus capacidades multimodales y de contexto extendido. La documentación y los recursos de la comunidad facilitan el aprendizaje.</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS

<table header-row="true">
<tr><td>Capacidades Core</td><td>Generación de texto, comprensión de lenguaje natural, procesamiento de imágenes, razonamiento multimodal, respuesta a preguntas basadas en texto e imagen.</td></tr>
<tr><td>Capacidades Avanzadas</td><td>Análisis de documentos extensos (10M de ventana de contexto), análisis de video (a través de frames), generación de código, razonamiento complejo, comprensión de gráficos y tablas.</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>Integración más profunda con sistemas empresariales, personalización avanzada a través de fine-tuning, capacidades mejoradas de red teaming y seguridad, optimización para hardware específico.</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>Tasa de aprobación del 25.5% en pruebas de seguridad (red teaming), potencial para generar contenido sesgado o tóxico (inherente a LLMs), consumo de recursos computacionales para modelos grandes.</td></tr>
<tr><td>Roadmap Público</td><td>Continuar mejorando la multimodalidad, expandir la ventana de contexto, optimizar la eficiencia y el costo, fortalecer las capacidades de seguridad y gobernanza, y fomentar el ecosistema de código abierto.</td></tr>
</table>

## L05 — DOMINIO TÉCNICO

<table header-row="true">
<tr><td>Stack Tecnológico</td><td>Modelos de lenguaje grandes (LLMs) y modelos multimodales grandes (LMMs) desarrollados por Meta AI. Utiliza una arquitectura Mixture of Experts (MoE).</td></tr>
<tr><td>Arquitectura Interna</td><td>Arquitectura MoE con 128 expertos y 17 mil millones de parámetros activos por modelo (para Llama 4 Maverick). Integración temprana (early fusion) de tokens de texto y visión.</td></tr>
<tr><td>Protocolos Soportados</td><td>API RESTful para interacción (a través de Llama API y proveedores de terceros como Together AI, Azure AI Foundry).</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>Entrada: Texto, imágenes (hasta 48 imágenes o frames de video), posiblemente otros formatos multimodales. Salida: Texto.</td></tr>
<tr><td>APIs Disponibles</td><td>Llama API (oficial), APIs de terceros (ej. Together AI, Azure AI Foundry, OpenRouter).</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS

<table header-row="true">
<tr><td>Caso de Uso</td><td>Generación de contenido para marketing digital</td><td>Pasos Exactos</td><td>1. Definir el público objetivo y el mensaje clave. 2. Proporcionar a Llama 4 (Maverick) imágenes de productos y texto base. 3. Solicitar la generación de descripciones de productos, publicaciones para redes sociales y eslóganes. 4. Revisar y refinar el contenido generado.</td><td>Herramientas Necesarias</td><td>Llama 4 Maverick, Llama API, editor de texto.</td><td>Tiempo Estimado</td><td>1-2 horas por campaña.</td><td>Resultado Esperado</td><td>Contenido de marketing atractivo y coherente con la marca.</td></tr>
<tr><td>Caso de Uso</td><td>Análisis de documentos legales extensos</td><td>Pasos Exactos</td><td>1. Cargar documentos legales (contratos, acuerdos) en Llama 4 (Scout). 2. Utilizar la ventana de contexto de 10M para realizar consultas sobre cláusulas específicas, riesgos o resúmenes. 3. Extraer información clave y generar informes.</td><td>Herramientas Necesarias</td><td>Llama 4 Scout, Llama API, sistema de gestión documental.</td><td>Tiempo Estimado</td><td>30 minutos - 1 hora por documento.</td><td>Resultado Esperado</td><td>Análisis rápido y preciso de documentos legales complejos.</td></tr>
<tr><td>Caso de Uso</td><td>Desarrollo de chatbot multimodal para soporte al cliente</td><td>Pasos Exactos</td><td>1. Integrar Llama 4 (Maverick) en una plataforma de chatbot. 2. Entrenar el chatbot con datos de soporte al cliente (texto e imágenes de problemas comunes). 3. Configurar el chatbot para responder preguntas, analizar imágenes de problemas y guiar a los usuarios. 4. Monitorear y mejorar las respuestas del chatbot.</td><td>Herramientas Necesarias</td><td>Llama 4 Maverick, Llama API, plataforma de chatbot (ej. WhatsApp Business API), herramientas de monitoreo.</td><td>Tiempo Estimado</td><td>2-4 semanas de desarrollo inicial, mejora continua.</td><td>Resultado Esperado</td><td>Reducción del tiempo de respuesta y mejora de la satisfacción del cliente.</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD

<table header-row="true">
<tr><td>Benchmark</td><td>MMMU (Image Reasoning)</td><td>Score/Resultado</td><td>Llama 4 Maverick: 73.4, Llama 4 Scout: 69.4</td><td>Fecha</td><td>Abril 2025 (según la fecha de lanzamiento de Llama 4)</td><td>Fuente</td><td>Meta AI (llama.com/models/llama-4/)</td><td>Comparativa</td><td>Excede a modelos comparables como GPT-4o y Gemini 2.0 en razonamiento multimodal.</td></tr>
<tr><td>Benchmark</td><td>MathVista (Image Reasoning)</td><td>Score/Resultado</td><td>Llama 4 Maverick: 73.7, Llama 4 Scout: 70.7</td><td>Fecha</td><td>Abril 2025</td><td>Fuente</td><td>Meta AI (llama.com/models/llama-4/)</td><td>Comparativa</td><td>Alto rendimiento en tareas de razonamiento matemático visual.</td></tr>
<tr><td>Benchmark</td><td>LiveCodeBench (Coding)</td><td>Score/Resultado</td><td>Llama 4 Maverick: 43.4, Llama 4 Scout: 32.8</td><td>Fecha</td><td>10.01.2024 - 02.01.2025 (rango de evaluación)</td><td>Fuente</td><td>Meta AI (llama.com/models/llama-4/)</td><td>Comparativa</td><td>Buen rendimiento en generación de código, superando a algunos competidores.</td></tr>
<tr><td>Benchmark</td><td>MMLU Pro (Reasoning & Knowledge)</td><td>Score/Resultado</td><td>Llama 4 Maverick: 80.5, Llama 4 Scout: 74.3</td><td>Fecha</td><td>Abril 2025</td><td>Fuente</td><td>Meta AI (llama.com/models/llama-4/)</td><td>Comparativa</td><td>Demuestra un fuerte razonamiento y conocimiento general.</td></tr>
<tr><td>Benchmark</td><td>MTOB (Long Context - half book eng->kgv)</td><td>Score/Resultado</td><td>Llama 4 Maverick: 54.0, Llama 4 Scout: 42.2</td><td>Fecha</td><td>Abril 2025</td><td>Fuente</td><td>Meta AI (llama.com/models/llama-4/)</td><td>Comparativa</td><td>Capacidad superior para manejar contextos largos.</td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN

<table header-row="true">
<tr><td>Método de Integración</td><td>API RESTful, SDKs (Python, etc.), despliegue en plataformas cloud (Azure AI Foundry).</td></tr>
<tr><td>Protocolo</td><td>HTTPS para APIs.</td></tr>
<tr><td>Autenticación</td><td>Claves API, tokens de acceso (OAuth 2.0 en algunos proveedores).</td></tr>
<tr><td>Latencia Típica</td><td>Baja latencia, optimizado para respuestas rápidas, especialmente con la arquitectura MoE.</td></tr>
<tr><td>Límites de Rate</td><td>Varían según el proveedor de API y el plan de suscripción. Se deben consultar los límites específicos de cada plataforma (ej. Azure, Together AI).</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS

<table header-row="true">
<tr><td>Tipo de Test</td><td>Pruebas de Seguridad (Red Teaming)</td><td>Herramienta Recomendada</td><td>LlamaFirewall, Llama Guard 3, herramientas de evaluación de seguridad de terceros.</td><td>Criterio de Éxito</td><td>Reducción de vulnerabilidades, mitigación de inyecciones de prompt, cumplimiento de políticas de uso responsable.</td><td>Frecuencia</td><td>Continua durante el desarrollo, auditorías periódicas, antes de cada lanzamiento importante.</td></tr>
<tr><td>Tipo de Test</td><td>Pruebas de Rendimiento y Latencia</td><td>Herramienta Recomendada</td><td>Herramientas de benchmarking de rendimiento, monitoreo de APIs.</td><td>Criterio de Éxito</td><td>Cumplimiento de los SLOs de latencia y throughput, eficiencia en el uso de recursos.</td><td>Frecuencia</td><td>Continua, después de cada optimización o cambio de infraestructura.</td></tr>
<tr><td>Tipo de Test</td><td>Pruebas de Calidad de Respuesta (Multimodal)</td><td>Herramienta Recomendada</td><td>Evaluación humana, benchmarks específicos (MMMU, MathVista, ChartQA, DocVQA), herramientas de evaluación de calidad de generación.</td><td>Criterio de Éxito</td><td>Precisión, coherencia, relevancia, ausencia de sesgos y toxicidad en las respuestas multimodales.</td><td>Frecuencia</td><td>Continua, con énfasis en nuevas capacidades y actualizaciones del modelo.</td></tr>
<tr><td>Tipo de Test</td><td>Pruebas de Contexto Largo</td><td>Herramienta Recomendada</td><td>Benchmarks MTOB, evaluaciones con documentos extensos.</td><td>Criterio de Éxito</td><td>Mantenimiento de la coherencia y precisión en la comprensión de documentos de hasta 10M de tokens.</td><td>Frecuencia</td><td>Periódica, especialmente con actualizaciones del modelo o cambios en la arquitectura.</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN

<table header-row="true">
<tr><td>Versión</td><td>Llama 4 Scout, Llama 4 Maverick</td><td>Fecha de Lanzamiento</td><td>Abril 2025 (primera versión de Llama 4)</td><td>Estado</td><td>Activo, en desarrollo continuo.</td><td>Cambios Clave</td><td>Introducción de multimodalidad nativa, ventana de contexto de 10M, arquitectura MoE, modelos Scout (17B-16E) y Maverick (17B-128E).</td><td>Ruta de Migración</td><td>Migración desde Llama 3 y versiones anteriores. Se recomienda consultar la documentación oficial de Meta AI y los proveedores de API para guías de migración detalladas.</td></tr>
<tr><td>Versión</td><td>Llama 4.x (futuras iteraciones)</td><td>Fecha de Lanzamiento</td><td>Futuras fechas (no especificadas, pero se espera un ciclo de actualización continuo)</td><td>Estado</td><td>Planificado.</td><td>Cambios Clave</td><td>Mejoras en rendimiento, eficiencia, seguridad, y expansión de capacidades multimodales.</td><td>Ruta de Migración</td><td>Actualizaciones incrementales con compatibilidad hacia atrás cuando sea posible, o guías de migración para cambios mayores.</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA

<table header-row="true">
<tr><td>Competidor Directo</td><td>GPT-4o (OpenAI)</td><td>Ventaja vs Competidor</td><td>Modelos de código abierto (open-weight) que permiten mayor personalización y despliegue on-premise. Costo-eficiencia superior en ciertos escenarios.</td><td>Desventaja vs Competidor</td><td>GPT-4o puede tener una base de usuarios más amplia y un ecosistema de herramientas más maduro.</td><td>Caso de Uso Donde Gana</td><td>Proyectos que requieren personalización profunda, control sobre el modelo, y despliegue en infraestructura propia.</td></tr>
<tr><td>Competidor Directo</td><td>Gemini 2.0 (Google)</td><td>Ventaja vs Competidor</td><td>Rendimiento competitivo en tareas multimodales y de razonamiento. Enfoque en la eficiencia y el costo.</td><td>Desventaja vs Competidor</td><td>Gemini 2.0 puede tener una integración más profunda con el ecosistema de Google Cloud.</td><td>Caso de Uso Donde Gana</td><td>Aplicaciones que buscan un equilibrio entre rendimiento, costo y flexibilidad de despliegue.</td></tr>
<tr><td>Competidor Directo</td><td>Claude 3 Opus (Anthropic)</td><td>Ventaja vs Competidor</td><td>Enfoque en la seguridad y la ética (Constitutional AI).</td><td>Desventaja vs Competidor</td><td>Llama 4 ofrece modelos de código abierto, lo que Claude 3 no hace.</td><td>Caso de Uso Donde Gana</td><td>Aplicaciones donde la seguridad y la ética son la máxima prioridad y se prefiere un modelo cerrado.</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)

<table header-row="true">
<tr><td>Capacidad de IA</td><td>Generación de texto y código</td><td>Modelo Subyacente</td><td>Llama 4 Scout, Llama 4 Maverick</td><td>Nivel de Control</td><td>Alto, a través de prompts detallados y fine-tuning.</td><td>Personalización Posible</td><td>Extensa, mediante fine-tuning con datasets específicos, ajuste de parámetros de generación (temperatura, top-p).</td></tr>
<tr><td>Capacidad de IA</td><td>Análisis y comprensión multimodal</td><td>Modelo Subyacente</td><td>Llama 4 Scout, Llama 4 Maverick</td><td>Nivel de Control</td><td>Moderado a alto, a través de la estructuración de entradas multimodales y la formulación de preguntas específicas.</td><td>Personalización Posible</td><td>Adaptación a dominios específicos mediante la curación de datos de entrada y la optimización de prompts.</td></tr>
<tr><td>Capacidad de IA</td><td>Razonamiento y resolución de problemas</td><td>Modelo Subyacente</td><td>Llama 4 Scout, Llama 4 Maverick</td><td>Nivel de Control</td><td>Alto, mediante la ingeniería de prompts que guían al modelo a través de cadenas de pensamiento o técnicas de razonamiento.</td><td>Personalización Posible</td><td>Desarrollo de prompts y plantillas específicas para tipos de problemas recurrentes.</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA

<table header-row="true">
<tr><td>Métrica</td><td>Eficiencia de Costo (Llama 4 Maverick)</td><td>Valor Reportado por Comunidad</td><td>$0.19/Mtok (3:1 blended) para inferencia distribuida; $0.30 - $0.49/Mtok (3:1 blended) en un solo host.</td><td>Fuente</td><td>Meta AI (llama.com/models/llama-4/), análisis de terceros como ArtificialAnalysis.ai.</td><td>Fecha</td><td>Abril 2025 (fecha de lanzamiento del modelo).</td></tr>
<tr><td>Métrica</td><td>Contexto Largo</td><td>Valor Reportado por Comunidad</td><td>10M de ventana de contexto.</td><td>Fuente</td><td>Meta AI (llama.com/models/llama-4/), menciones en blogs y artículos técnicos.</td><td>Fecha</td><td>Abril 2025.</td></tr>
<tr><td>Métrica</td><td>Multimodalidad</td><td>Valor Reportado por Comunidad</td><td>Capacidad nativa para procesar texto e imágenes, superando a modelos como GPT-4o y Gemini 2.0 en ciertos benchmarks multimodales.</td><td>Fuente</td><td>Meta AI (ai.meta.com/blog/llama-4-multimodal-intelligence/), artículos de análisis.</td><td>Fecha</td><td>Abril 2025.</td></tr>
<tr><td>Métrica</td><td>Adopción y Uso</td><td>Valor Reportado por Comunidad</td><td>Amplia adopción en la comunidad de desarrolladores debido a su naturaleza de código abierto y rendimiento competitivo.</td><td>Fuente</td><td>Hugging Face (colecciones meta-llama/llama-4), foros de desarrolladores, blogs técnicos.</td><td>Fecha</td><td>Continuo, con picos después de los lanzamientos.</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM

<table header-row="true">
<tr><td>Plan</td><td>Modelos de código abierto (open-weight)</td><td>Precio</td><td>Gratuito para descarga y uso, costos asociados a la infraestructura de despliegue.</td><td>Límites</td><td>Uso sujeto a los términos de servicio de Meta Llama.</td><td>Ideal Para</td><td>Desarrolladores, investigadores, startups y empresas que buscan flexibilidad, personalización y control sobre sus modelos de IA.</td><td>ROI Estimado</td><td>Alto, debido a la reducción de costos de licenciamiento y la capacidad de optimizar el rendimiento para casos de uso específicos.</td></tr>
<tr><td>Plan</td><td>Llama API</td><td>Precio</td><td>Basado en el uso (tokens de entrada/salida), varía según el proveedor.</td><td>Límites</td><td>Límites de tasa y cuotas definidos por el proveedor de la API.</td><td>Ideal Para</td><td>Empresas que buscan una integración rápida y escalable sin la necesidad de gestionar la infraestructura subyacente.</td><td>ROI Estimado</td><td>Moderado a alto, dependiendo del volumen de uso y la eficiencia de la integración.</td></tr>
<tr><td>Plan</td><td>Despliegue en Plataformas Cloud (ej. Azure AI Foundry)</td><td>Precio</td><td>Basado en el uso de recursos de cómputo y tokens procesados.</td><td>Límites</td><td>Definidos por la plataforma cloud.</td><td>Ideal Para</td><td>Grandes empresas con infraestructura existente en la nube y necesidades de escalabilidad y seguridad.</td><td>ROI Estimado</td><td>Moderado, con beneficios de integración y gestión de la infraestructura.</td></tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING

<table header-row="true">
<tr><td>Escenario de Test</td><td>Generación de contenido dañino o sesgado</td><td>Resultado</td><td>Se han identificado casos donde Llama 4 puede generar contenido problemático, aunque Meta ha implementado herramientas de protección.</td><td>Fortaleza Identificada</td><td>Implementación de LlamaFirewall y Llama Guard 3 para mitigar riesgos.</td><td>Debilidad Identificada</td><td>La naturaleza de código abierto puede permitir la manipulación para generar contenido no deseado.</td></tr>
<tr><td>Escenario de Test</td><td>Inyección de Prompt</td><td>Resultado</td><td>Vulnerabilidad a la inyección de prompt, como se evidencia en informes de seguridad.</td><td>Fortaleza Identificada</td><td>Esfuerzos continuos de Meta para mejorar la robustez contra ataques de inyección.</td><td>Debilidad Identificada</td><td>Requiere vigilancia constante y mejoras en los mecanismos de defensa.</td></tr>
<tr><td>Escenario de Test</td><td>Exposición de datos sensibles por agentes de IA</td><td>Resultado</td><td>Incidentes reportados donde agentes de IA de Meta expusieron datos sensibles internamente.</td><td>Fortaleza Identificada</td><td>Meta ha respondido a los incidentes y enfatiza que no se mishandlearon datos de usuario externamente.</td><td>Debilidad Identificada</td><td>Necesidad de fortalecer la gobernanza y la seguridad en el desarrollo y despliegue de agentes de IA.</td></tr>
<tr><td>Escenario de Test</td><td>Rendimiento en Benchmarks (MMMU, MathVista, LiveCodeBench, MMLU Pro, MTOB)</td><td>Resultado</td><td>Alto rendimiento en una variedad de benchmarks, superando a competidores en varias métricas.</td><td>Fortaleza Identificada</td><td>Capacidades multimodales y de contexto largo líderes en la industria.</td><td>Debilidad Identificada</td><td>Algunas áreas, como el rendimiento en codificación para Scout, pueden tener margen de mejora.</td></tr>
</table>