# BIBLIA DE DEEPSEEK_V3 v7.3

**Fecha de Actualización:** 30 de Abril de 2026

**Versión más actual:** DeepSeek-V3.2

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO

<table header-row="true">
<tr><td>Nombre oficial</td><td>DeepSeek-V3</td></tr>
<tr><td>Desarrollador</td><td>DeepSeek AI</td></tr>
<tr><td>País de Origen</td><td>China</td></tr>
<tr><td>Inversión y Financiamiento</td><td>Menos de $6 millones de dólares para entrenamiento [3] [5]</td></tr>
<tr><td>Modelo de Precios</td><td>Basado en tokens. DeepSeek-V3.2: $0.14/M tokens de entrada (cache hit), $0.28/M tokens de salida [6]. Descuentos por caché del 90% [1].</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>LLM de código abierto con arquitectura MoE, enfocado en eficiencia y escalabilidad, comparable a modelos de código cerrado líderes a un costo significativamente menor [2] [3] [4]. Alternativa rentable y de alto rendimiento [3] [6].</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Se basa en arquitecturas como Multi-head Latent Attention (MLA) y DeepSeekMoE [13] [14].</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Compatible con formatos OpenAI y Anthropic API [1].</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>No se encontró información pública específica sobre SLOs.</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA

<table header-row="true">
<tr><td>Licencia</td><td>Licencia de modelo (LICENSE-MODEL) [12]. Licencia MIT para el código [69].</td></tr>
<tr><td>Política de Privacidad</td><td>DeepSeek tiene una Política de Privacidad que detalla la recopilación, protección y uso de información personal [10].</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>Menciona SOC 2, GDPR, DPPDA e ISO certificaciones para seguridad [11].</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>No se encontró historial de auditorías específico, pero se menciona un informe de transparencia [15].</td></tr>
<tr><td>Respuesta a Incidentes</td><td>No se encontró información pública específica.</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>No se encontró información pública específica.</td></tr>
<tr><td>Política de Obsolescencia</td><td>Los modelos `deepseek-chat` y `deepseek-reasoner` serán deprecados, correspondiendo a modos de `deepseek-v4-flash` [1].</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA

DeepSeek-V3 es un modelo de lenguaje grande (LLM) que se basa en una arquitectura Mixture-of-Experts (MoE) y Multi-head Latent Attention (MLA) para lograr eficiencia y escalabilidad. Su diseño se centra en un equilibrio entre rendimiento y costo, buscando democratizar el acceso a capacidades avanzadas de IA. Se entrena con un objetivo de predicción multi-token y un balanceo de carga sin pérdida auxiliar, lo que contribuye a su estabilidad y rendimiento superior [2].

<table header-row="true">
<tr><td>Paradigma Central</td><td>Mixture-of-Experts (MoE) y Multi-head Latent Attention (MLA) para eficiencia y escalabilidad [2] [13] [14].</td></tr>
<tr><td>Abstracciones Clave</td><td>MoE, MLA, balanceo de carga sin pérdida auxiliar, objetivo de entrenamiento de predicción multi-token [2].</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>Utilizar para tareas que requieren razonamiento avanzado, aplicaciones de IA agénticas, uso de herramientas y resolución de problemas complejos [7].</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>Uso ineficiente de tokens sin aprovechar el caché. No considerar la optimización de costos.</td></tr>
<tr><td>Curva de Aprendizaje</td><td>Moderada para usuarios familiarizados con APIs de LLMs. La documentación y ejemplos facilitan la integración [1].</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS

<table header-row="true">
<tr><td>Capacidades Core</td><td>Generación de texto, comprensión del lenguaje natural, razonamiento avanzado, capacidades agénticas, uso de herramientas [7].</td></tr>
<tr><td>Capacidades Avanzadas</td><td>Resolución de problemas complejos, soporte para JSON Output, Tool Calls, Chat Prefix Completion (Beta), FIM Completion (Beta) [1].</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>DeepSeek-V4 Preview con capacidades de agente más fuertes y razonamiento de primer nivel [1].</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>FIM Completion solo en modo no-thinking [1]. Contexto máximo de 1M tokens y salida máxima de 384K tokens [1].</td></tr>
<tr><td>Roadmap Público</td><td>Continuas mejoras en eficiencia, escalabilidad y rendimiento. Desarrollo de nuevas versiones como DeepSeek-V4 [1].</td></tr>
</table>

## L05 — DOMINIO TÉCNICO

<table header-row="true">
<tr><td>Stack Tecnológico</td><td>Arquitectura Mixture-of-Experts (MoE), Multi-head Latent Attention (MLA), DeepSeekMoE [2] [13] [14]. Entrenado en GPUs NVIDIA H800 [16].</td></tr>
<tr><td>Arquitectura Interna</td><td>671B parámetros totales con 37B activados por token (MoE). Estrategia de balanceo de carga sin pérdida auxiliar. Objetivo de entrenamiento de predicción multi-token [2].</td></tr>
<tr><td>Protocolos Soportados</td><td>API compatible con formatos OpenAI y Anthropic [1].</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>Texto (tokens). JSON Output soportado [1].</td></tr>
<tr><td>APIs Disponibles</td><td>API de DeepSeek con endpoints compatibles con OpenAI y Anthropic [1].</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS

<table header-row="true">
<tr><td>Caso de Uso</td><td>Generación de Contenido impulsada por IA</td><td>Mejora del Servicio al Cliente</td><td>Tutoría Personalizada en Educación</td></tr>
<tr><td>Pasos Exactos</td><td>1. Definir el tema y el estilo. 2. Proporcionar un prompt detallado a DeepSeek-V3. 3. Revisar y refinar el contenido generado.</td><td>1. Integrar DeepSeek-V3 con el sistema de chat o soporte. 2. Configurar el modelo para responder preguntas frecuentes y escalar a agentes humanos cuando sea necesario. 3. Monitorear y ajustar las respuestas del modelo.</td><td>1. Alimentar a DeepSeek-V3 con el material de estudio. 2. Permitir que los estudiantes hagan preguntas y reciban explicaciones personalizadas. 3. Evaluar el progreso del estudiante y adaptar el plan de estudio.</td></tr>
<tr><td>Herramientas Necesarias</td><td>API de DeepSeek-V3, editor de texto/IDE.</td><td>API de DeepSeek-V3, plataforma de CRM/chat.</td><td>API de DeepSeek-V3, plataforma de e-learning.</td></tr>
<tr><td>Tiempo Estimado</td><td>Minutos por artículo/segmento.</td><td>Horas para configuración inicial, continuo para monitoreo.</td><td>Minutos por sesión de tutoría.</td></tr>
<tr><td>Resultado Esperado</td><td>Contenido de alta calidad, relevante y coherente.</td><td>Respuestas rápidas y precisas a consultas de clientes, reducción de carga de trabajo para agentes.</td><td>Mejora en la comprensión y el rendimiento académico de los estudiantes.</td></tr>
<tr><td>ROI Estimado</td><td>Significativo debido a los bajos costos operativos y el alto rendimiento, lo que permite un desarrollo y despliegue de IA más económico [3] [6].</td><td>Ahorros sustanciales en costos de inferencia para cargas de trabajo repetitivas.</td><td>Mayor eficiencia en el desarrollo y despliegue de aplicaciones de IA.</td><td>Innovación acelerada y reducción de la dependencia de proveedores de modelos cerrados.</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD

<table header-row="true">
<tr><td>Benchmark</td><td>MMLU-Pro</td><td>MATH 500</td><td>Codeforces</td><td>GPQA-Diamond</td><td>Artificial Analysis Intelligence Index</td></tr>
<tr><td>Score/Resultado</td><td>Superior a GPT-4o [4]</td><td>Superior a GPT-4o [4]</td><td>Superior a GPT-4o [4]</td><td>~79.9 (V3.2-Exp) [9]</td><td>16 (DeepSeek V3 Dec '24) [7], 28 (DeepSeek V3.1 Non-reasoning) [8]</td></tr>
<tr><td>Fecha</td><td>Desconocida</td><td>Desconocida</td><td>Desconocida</td><td>Desconocida</td><td>Dic 2024 / Ago 2025</td></tr>
<tr><td>Fuente</td><td>Medium [4]</td><td>Medium [4]</td><td>Medium [4]</td><td>Medium [9]</td><td>Artificial Analysis [7] [8]</td></tr>
<tr><td>Comparativa</td><td>Supera a GPT-4o en varios benchmarks [4].</td><td>Supera a GPT-4o en varios benchmarks [4].</td><td>Supera a GPT-4o en varios benchmarks [4].</td><td>Comparable a V3.1 [9].</td><td>Evalúa modelos en diversas tareas [7] [8].</td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN

<table header-row="true">
<tr><td>Método de Integración</td><td>API RESTful</td></tr>
<tr><td>Protocolo</td><td>HTTPS</td></tr>
<tr><td>Autenticación</td><td>Clave API (API Key)</td></tr>
<tr><td>Latencia Típica</td><td>60 tokens/segundo (3x más rápido que V2) [1].</td></tr>
<tr><td>Límites de Rate</td><td>No se encontró información pública específica sobre límites de rate.</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS

<table header-row="true">
<tr><td>Tipo de Test</td><td>Pruebas de Rendimiento</td><td>Pruebas de Integración</td><td>Pruebas de Seguridad</td><td>Pruebas de Robustez</td></tr>
<tr><td>Herramienta Recomendada</td><td>Herramientas de benchmarking de LLMs (ej. EleutherAI LM Evaluation Harness), scripts personalizados.</td><td>Frameworks de pruebas de API (ej. Postman, Pytest con requests).</td><td>Herramientas de escaneo de vulnerabilidades, auditorías de código.</td><td>Generación de prompts adversarios, pruebas de estrés.</td></tr>
<tr><td>Criterio de Éxito</td><td>Cumplimiento de métricas de rendimiento (ej. MMLU, MATH) [4].</td><td>Comunicación exitosa con la API, manejo correcto de entradas/salidas.</td><td>Identificación y mitigación de vulnerabilidades.</td><td>Resistencia a entradas inesperadas, estabilidad bajo carga.</td></tr>
<tr><td>Frecuencia</td><td>Periódica (con cada nueva versión o actualización).</td><td>Con cada nueva integración o cambio en la API.</td><td>Anual o tras cambios significativos.</td><td>Continuo durante el desarrollo y despliegue.</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN

<table header-row="true">
<tr><td>Versión</td><td>DeepSeek-V3</td><td>DeepSeek-V3.1</td><td>DeepSeek-V3.2</td><td>DeepSeek-V4</td></tr>
<tr><td>Fecha de Lanzamiento</td><td>Dic 2024 [7]</td><td>Desconocida (mencionado en Ago 2025) [8]</td><td>Dic 2025 [1]</td><td>Preview (Abril 2026) [1]</td></tr>
<tr><td>Estado</td><td>Activo</td><td>Activo</td><td>Activo</td><td>En desarrollo/Preview</td></tr>
<tr><td>Cambios Clave</td><td>MoE, MLA, balanceo de carga sin pérdida auxiliar, predicción multi-token [2].</td><td>Versátil, actúa como V3 para salidas rápidas o R1 para razonamiento [1].</td><td>Mejora en razonamiento y rendimiento de agente, sistema Front and Back View [1] [10].</td><td>Capacidades de agente más fuertes, razonamiento de primer nivel, 1M de longitud de contexto [1].</td></tr>
<tr><td>Ruta de Migración</td><td>Migración de versiones anteriores a V3.2 o V4. Modelos `deepseek-chat` y `deepseek-reasoner` serán deprecados a favor de `deepseek-v4-flash` [1].</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA

<table header-row="true">
<tr><td>Competidor Directo</td><td>GPT-4o (OpenAI)</td><td>Claude (Anthropic)</td><td>Gemini (Google)</td></tr>
<tr><td>Ventaja vs Competidor</td><td>Rendimiento comparable a un costo significativamente menor [3] [6]. Modelo de código abierto [2].</td><td>Costo-efectividad, arquitectura MoE para eficiencia [2] [3].</td><td>Costo-efectividad, flexibilidad de integración [2] [3].</td></tr>
<tr><td>Desventaja vs Competidor</td><td>Menor reconocimiento de marca global.</td><td>Posiblemente menos madurez en el ecosistema de herramientas/integraciones.</td><td>Menor base de usuarios inicial.</td></tr>
<tr><td>Caso de Uso Donde Gana</td><td>Aplicaciones donde el costo es un factor crítico y se requiere alto rendimiento. Proyectos de investigación y desarrollo que buscan modelos de código abierto.</td><td>Casos de uso que requieren eficiencia computacional y escalabilidad.</td><td>Aplicaciones que buscan una alternativa potente y económica a los modelos líderes.</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)

<table header-row="true">
<tr><td>Capacidad de IA</td><td>Generación de texto</td><td>Razonamiento avanzado</td><td>Uso de herramientas</td><td>JSON Output</td></tr>
<tr><td>Modelo Subyacente</td><td>DeepSeek-V3 (MoE LLM) [2]</td><td>DeepSeek-V3 (MoE LLM) [2]</td><td>DeepSeek-V3 (MoE LLM) [2]</td><td>DeepSeek-V3 (MoE LLM) [2]</td></tr>
<tr><td>Nivel de Control</td><td>Alto (a través de prompts detallados y parámetros de API).</td><td>Alto (a través de prompts estructurados y ejemplos de razonamiento).</td><td>Alto (a través de la definición de herramientas y sus funciones).</td><td>Alto (a través de la especificación del esquema JSON).</td></tr>
<tr><td>Personalización Posible</td><td>Fine-tuning del modelo para tareas específicas [1].</td><td>Adaptación a dominios específicos mediante prompts y datos.</td><td>Definición de herramientas personalizadas para interactuar con sistemas externos.</td><td>Definición de esquemas JSON personalizados para la salida.</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA

<table header-row="true">
<tr><td>Métrica</td><td>Costo de entrenamiento</td><td>Velocidad de inferencia</td><td>Satisfacción del usuario</td><td>Adopción en la comunidad open-source</td></tr>
<tr><td>Valor Reportado por Comunidad</td><td>Menos de $6 millones de dólares [3] [5].</td><td>60 tokens/segundo (3x más rápido que V2) [1].</td><td>Usuarios impresionados por la eficiencia y el rendimiento [3].</td><td>Creciente, especialmente en la comunidad de modelos de código abierto [2].</td></tr>
<tr><td>Fuente</td><td>Reddit [3] [5]</td><td>DeepSeek API Docs [1]</td><td>Facebook [3]</td><td>GitHub, Hugging Face [2] [1]</td></tr>
<tr><td>Fecha</td><td>Desconocida</td><td>Dic 2024</td><td>Desconocida</td><td>2024-2026</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM

<table header-row="true">
<tr><td>Plan</td><td>Precios competitivos</td><td>Descuentos por caché</td><td>API flexible</td><td>Modelos de código abierto</td></tr>
<tr><td>Precio</td><td>DeepSeek-V3.2: $0.14/M tokens de entrada (cache hit), $0.28/M tokens de salida [6].</td><td>Hasta 90% de descuento en tokens de entrada con caché [1].</td><td>Precios diferenciados por modelo y uso.</td><td>Modelos base disponibles para uso y fine-tuning.</td></tr>
<tr><td>Límites</td><td>Basado en tokens. Contexto máximo de 1M tokens, salida máxima de 384K tokens [1].</td><td>No se encontraron límites de rate específicos.</td><td>No se encontraron límites de uso específicos más allá de los tokens.</td><td>No se encontraron límites de uso específicos.</td></tr>
<tr><td>Ideal Para</td><td>Desarrolladores y empresas que buscan soluciones de IA rentables y de alto rendimiento.</td><td>Aplicaciones con patrones de uso repetitivos que pueden beneficiarse del caché.</td><td>Integraciones personalizadas y aplicaciones agénticas.</td><td>Investigadores y desarrolladores que buscan flexibilidad y transparencia.</td></tr>
<tr><td>ROI Estimado</td><td>Significativo debido a los bajos costos operativos y el alto rendimiento, lo que permite un desarrollo y despliegue de IA más económico [3] [6].</td><td>Ahorros sustanciales en costos de inferencia para cargas de trabajo repetitivas.</td><td>Mayor eficiencia en el desarrollo y despliegue de aplicaciones de IA.</td><td>Innovación acelerada y reducción de la dependencia de proveedores de modelos cerrados.</td></tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING

<table header-row="true">
<tr><td>Escenario de Test</td><td>Generación de código complejo</td><td>Resolución de problemas matemáticos avanzados</td><td>Respuesta a preguntas de conocimiento general</td><td>Manejo de prompts adversarios</td></tr>
<tr><td>Resultado</td><td>Alto rendimiento en benchmarks de codificación [4].</td><td>Supera a GPT-4o en MATH 500 [4].</td><td>Rendimiento comparable a modelos líderes [2].</td><td>No se encontró información específica sobre red teaming.</td></tr>
<tr><td>Fortaleza Identificada</td><td>Capacidad de razonamiento superior, eficiencia en el entrenamiento y la inferencia [2] [4].</td><td>Habilidad para manejar tareas complejas y generar resultados precisos.</td><td>Amplio conocimiento y capacidad de comprensión.</td><td>Estabilidad del modelo y resistencia a fallos [2].</td></tr>
<tr><td>Debilidad Identificada</td><td>No se encontraron debilidades específicas en la investigación.</td><td>No se encontraron debilidades específicas en la investigación.</td><td>No se encontraron debilidades específicas en la investigación.</td><td>No se encontró información específica sobre vulnerabilidades.</td></tr>
</table>

## Referencias

[1] DeepSeek API Docs. *Models & Pricing*. Disponible en: https://api-docs.deepseek.com/quick_start/pricing
[2] deepseek-ai/DeepSeek-V3. *GitHub*. Disponible en: https://github.com/deepseek-ai/deepseek-v3
[3] Shenzhen Story. *On 26 April, DeepSeek announced that prices for its full...*. Disponible en: https://www.facebook.com/ShenzhenStory/posts/on-26-april-deepseek-announced-that-prices-for-its-full-range-of-deepseek-api-se/1400196122129177/
[4] LM Po. *Exploring DeepSeek-V3: A Technical Overview*. Disponible en: https://medium.com/@lmpo/exploring-deepseek-version-3-a-technical-deep-dive-0b3d2c78b777
[5] Reddit. *does deepseek v3\'s training cost of under $6 million...*. Disponible en: https://www.reddit.com/r/OpenAI/comments/1hsh31t/does_deepseek_v3s_training_cost_of_under_6/
[6] TLDL. *DeepSeek API Pricing 2026 — Cheapest LLM ($0.14/M Input)*. Disponible en: https://www.tldl.io/resources/deepseek-api-pricing
[7] Artificial Analysis. *DeepSeek V3 (Dec) - Intelligence, Performance & Price Analysis*. Disponible en: https://artificialanalysis.ai/models/deepseek-v3
[8] Artificial Analysis. *DeepSeek V3.1 - Intelligence, Performance & Price Analysis*. Disponible en: https://artificialanalysis.ai/models/deepseek-v3-1
[9] Medium. *DeepSeek V3.2-Exp Review*. Disponible en: https://medium.com/@leucopsis/deepseek-v3-2-exp-review-49ba1e1beb7c
[10] DeepSeek. *DeepSeek Terms of Use*. Disponible en: https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html
[11] Quash. *DeepSeek v3: AI\'s New Game-Changer*. Disponible en: https://quashbugs.com/newsletter/deepseek-v3-breakthrough-quash-security-certifications
[12] GitHub. *DeepSeek-V3/LICENSE-MODEL at main*. Disponible en: https://github.com/deepseek-ai/DeepSeek-V3/blob/main/LICENSE-MODEL
[13] PyImageSearch. *Build DeepSeek-V3: Multi-Head Latent Attention (MLA)...*. Disponible en: https://pyimagesearch.com/2026/03/16/build-deepseek-v3-multi-head-latent-attention-mla-architecture/
[14] Medium. *DeepSeek R1 & V3.2 Architecture Deep Dive along with 3...*. Disponible en: https://medium.com/mlwithdev/deepseek-series-deepseek-r1-v3-2-79410b2ab7bb
[15] Stanford FM Transparency Initiative. *DeepSeek Transparency Report*. Disponible en: https://crfm.stanford.edu/fmti/December-2025/company-reports/DeepSeek_FinalReport_FMTI2025.html
[16] arXiv. *DeepSeek-V3 Technical Report*. Disponible en: https://arxiv.org/html/2412.19437v1