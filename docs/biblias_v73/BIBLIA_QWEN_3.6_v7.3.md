# BIBLIA DE QWEN_3.6 v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<table header-row="true">
<tr><td>Nombre oficial</td><td>Desarrollador</td><td>País de Origen</td><td>Inversión y Financiamiento</td><td>Modelo de Precios</td><td>Posicionamiento Estratégico</td><td>Gráfico de Dependencias</td><td>Matriz de Compatibilidad</td><td>Acuerdos de Nivel de Servicio (SLOs)</td></tr>
<tr><td>Qwen3.6 (incluye variantes como Qwen3.6-Plus, Qwen3.6-27B, Qwen3.6-35B-A3B, Qwen3.6-Max-Preview)</td><td>Alibaba Cloud (Qwen Team, Alibaba Group) [1]</td><td>China [1]</td><td>Inversión significativa por parte de Alibaba Group en investigación y desarrollo de IA [2]</td><td>Basado en tokens de entrada y salida. Ejemplos: Qwen3.6-Plus en OpenRouter: Input $0.325/M tokens, Output $1.95/M tokens [3]. Precios varían según el modelo (Max, Plus, Turbo) y el proveedor (Alibaba Cloud, OpenRouter, DeepInfra) [4] [5].</td><td>Posicionado como un modelo de IA de vanguardia para agentes del mundo real, con un fuerte enfoque en capacidades de codificación agentica, razonamiento multimodal y ventanas de contexto de 1M de tokens. Dirigido a desarrolladores y soluciones empresariales [6] [7].</td><td>Se basa en los avances de Qwen3.5 y Qwen3-Next [8].</td><td>Compatible con APIs de OpenAI. Integración con asistentes de codificación de terceros (OpenClaw, Claude Code, Qwen Code, Kilo Code, Cline, OpenCode). Soporte oficial en vLLM [6] [9].</td><td>No se encontraron SLOs explícitos en la documentación pública inicial.</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA
<table header-row="true">
<tr><td>Licencia</td><td>Política de Privacidad</td><td>Cumplimiento y Certificaciones</td><td>Historial de Auditorías y Seguridad</td><td>Respuesta a Incidentes</td><td>Matriz de Autoridad de Decisión</td><td>Política de Obsolescencia</td></tr>
<tr><td>Muchos modelos Qwen se distribuyen bajo la licencia Apache 2.0 de código abierto [10]. Sin embargo, variantes como Qwen3.6-Max-Preview son propietarias y de código cerrado [11].</td><td>Existe una Política de Privacidad detallada, referenciada en los Términos de Servicio de Qwen [12].</td><td>Alibaba Cloud, como desarrollador, está sujeto a diversas regulaciones globales. Un artículo reciente menciona que Qwen está probando estrategias de gobernanza de modelos de IA, incluyendo mapeo de cumplimiento contra ISO, NIST y reglas de privacidad regionales [13].</td><td>No se encontró un historial de auditorías públicas específico para Qwen3.6, pero la gobernanza de modelos de IA de Alibaba Cloud implica un monitoreo continuo para la deriva y regresión [13].</td><td>Las estrategias de gobernanza de modelos de IA de Alibaba Cloud incluyen simulacros de respuesta a incidentes [13].</td><td>No se encontró información pública específica sobre una matriz de autoridad de decisión para Qwen3.6. Se infiere que Alibaba Cloud mantiene el control centralizado sobre el desarrollo y despliegue de sus modelos propietarios.</td><td>No se encontró una política de obsolescencia explícita. Sin embargo, el rápido ritmo de desarrollo de Qwen (ej. Qwen3.5 en febrero, Qwen3.6-Plus en abril) sugiere un ciclo de vida de producto activo con actualizaciones frecuentes [6].</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA

El modelo mental de Qwen3.6 se centra en la **IA Agentica** y el **Razonamiento Multimodal**, diseñado para interactuar con el mundo real y resolver problemas complejos de manera autónoma. Su maestría radica en la capacidad de comprender, razonar y actuar a través de diversas modalidades, con un énfasis particular en la codificación y la resolución de problemas a nivel de repositorio. Este enfoque busca ofrecer una experiencia de desarrollo más intuitiva y eficiente, transformando la forma en que los desarrolladores interactúan con la IA para tareas complejas.

<table header-row="true">
<tr><td>Paradigma Central</td><td>Abstracciones Clave</td><td>Patrones de Pensamiento Recomendados</td><td>Anti-patrones a Evitar</td><td>Curva de Aprendizaje</td></tr>
<tr><td>IA Agentica y Razonamiento Multimodal para Aplicaciones del Mundo Real [6] [7]</td><td>Agentes de Codificación, Razonamiento Multimodal, Ventana de Contexto de 1M de tokens, `preserve_thinking` [6]</td><td>Descomposición de problemas complejos, integración de información multimodal, aprovechamiento de la ventana de contexto extendida, uso estratégico de `preserve_thinking` para tareas de agente [6]</td><td>Tratarlo como un modelo puramente generativo, ignorar la entrada multimodal, no proporcionar suficiente contexto, desactivar `preserve_thinking` en tareas críticas de agente.</td><td>Moderada para usuarios familiarizados con LLMs y APIs tipo OpenAI. Requiere comprensión de la IA agentica y diseño de prompts para maximizar el potencial.</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS
<table header-row="true">
<tr><td>Capacidades Core</td><td>Capacidades Avanzadas</td><td>Capacidades Emergentes (Abril 2026)</td><td>Limitaciones Técnicas Confirmadas</td><td>Roadmap Público</td></tr>
<tr><td>Codificación agentica (frontend, resolución de problemas a nivel de repositorio), razonamiento multimodal, ventana de contexto de 1M de tokens [6] [7].</td><td>Comprensión de código multilingüe (119 idiomas), generación de imágenes (Qwen VLo), investigación profunda (Deep Research), desarrollo web (Web Dev), capacidades de búsqueda avanzada [14] [15].</td><td>Qwen3.6-Max-Preview (vista previa de modelo propietario con mayor conocimiento del mundo y seguimiento de instrucciones, mejoras en codificación agentica) [16]. Qwen-Scope (kit de herramientas de interpretabilidad) [17]. FlashQLA (kernels de atención lineal fusionada) [18].</td><td>Problemas de rendimiento en arquitecturas MoE (latencia), presión de memoria con 1M de tokens, errores 429 (rate limits) [19]. Algunos usuarios reportan que Qwen3.6-27B puede "romper archivos y entrar en bucles" en planes de implementación complejos [20]. Problemas con `reasoning_content` en Tool Calling para la serie Qwen3.5 [21].</td><td>Roadmap de Qwen Code disponible [22]. Alibaba Cloud ha anunciado hojas de ruta estratégicas para innovaciones de IA de próxima generación, incluyendo la familia Qwen3 [23].</td></tr>
</table>

## L05 — DOMINIO TÉCNICO
<table header-row="true">
<tr><td>Stack Tecnológico</td><td>Arquitectura Interna</td><td>Protocolos Soportados</td><td>Formatos de Entrada/Salida</td><td>APIs Disponibles</td></tr>
<tr><td>Arquitectura híbrida que combina atención lineal eficiente con enrutamiento disperso Mixture-of-Experts (MoE) [24]. Utiliza RMSNorm en lugar de LayerNorm [25].</td><td>Modelos causales de lenguaje multimodal con codificador de visión (para variantes como Qwen3.6-35B-A3B) [26]. Gated Delta Network (GDN) como capa de atención principal [18].</td><td>Soporta protocolos estándar de la industria, incluyendo APIs compatibles con OpenAI y Anthropic [27] [28]. Soporte nativo para Model Context Protocol (MCP) [29].</td><td>Texto, imágenes, audio, video (para entrada multimodal) [15]. Salida de texto, código, imágenes.</td><td>API oficial a través de Alibaba Cloud Model Studio [6]. APIs compatibles con OpenAI [27]. Qwen-Agent encapsula plantillas y parsers de llamadas a herramientas [30].</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS
<table header-row="true">
<tr><td>Caso de Uso</td><td>Pasos Exactos</td><td>Herramientas Necesarias</td><td>Tiempo Estimado</td><td>Resultado Esperado</td></tr>
<tr><td>Codificación Agentica (Refactorización de Repositorios)</td><td>1. Planificación inicial y definición del alcance del refactor. 2. Ejecución de tareas de codificación (frontend, resolución de problemas a nivel de repositorio) utilizando Qwen3.6-35B-A3B. 3. Revisión y validación del código generado.</td><td>Qwen3.6-35B-A3B, IDE, Git.</td><td>Variable (dependiendo de la complejidad del repositorio).</td><td>Código refactorizado, mejoras en la calidad del código, resolución de problemas a nivel de repositorio.</td></tr>
<tr><td>Desarrollo de Agentes de IA Multimodales</td><td>1. Definición del problema y diseño del agente. 2. Integración de capacidades multimodales (texto, imagen, video) utilizando Qwen3.6-Plus. 3. Implementación y pruebas del agente. 4. Refinamiento basado en el rendimiento.</td><td>Qwen3.6-Plus, Qwen Studio, APIs compatibles con OpenAI/Anthropic, herramientas de procesamiento de datos multimodales.</td><td>Semanas a meses (dependiendo de la complejidad del agente).</td><td>Agente de IA capaz de interactuar con el mundo real a través de múltiples modalidades, resolviendo problemas complejos.</td></tr>
<tr><td>Revisión de Código Localmente</td><td>1. Configuración local de Qwen3.6-35B-A3B (con cuantificación). 2. Alimentación del código a revisar al modelo. 3. Análisis de las sugerencias de mejora y errores identificados. 4. Implementación de las mejoras.</td><td>Qwen3.6-35B-A3B (cuantificado), Unsloth Dynamic 2.0, entorno de desarrollo local.</td><td>Horas a días (dependiendo del tamaño del código y la configuración).</td><td>Código revisado con sugerencias de mejora, identificación de errores y optimizaciones.</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD
<table header-row="true">
<tr><td>Benchmark</td><td>Score/Resultado</td><td>Fecha</td><td>Fuente</td><td>Comparativa</td></tr>
<tr><td>SWE-bench Verified</td><td>77.2%</td><td>Abril 2026</td><td>buildfastwithai.com [31]</td><td>Supera a Qwen3.5-397B-A17B (anterior modelo insignia de código abierto) [31].</td></tr>
<tr><td>Artificial Analysis Intelligence Index</td><td>50/100</td><td>Abril 2026</td><td>artificialanalysis.ai [32]</td><td>"Bien por encima del promedio" (promedio de 33) entre modelos comparables [32].</td></tr>
<tr><td>BenchLM Provisional Leaderboard</td><td>74/100 (#28 de 115)</td><td>Abril 2026</td><td>benchlm.ai [33]</td><td>Posición 28 de 115 modelos listados.</td></tr>
<tr><td>Terminal-Bench</td><td>Iguala a Claude 4.5 Opus</td><td>Abril 2026</td><td>buildfastwithai.com [31]</td><td>Rendimiento comparable con Claude 4.5 Opus en tareas de terminal [31].</td></tr>
<tr><td>Qwen3.6-35B-A3B GGUF KLD (Mean KL Divergence)</td><td>Mejor rendimiento SOTA en cuantificación</td><td>Abril 2026</td><td>unsloth.ai [34]</td><td>Cuantificaciones calibradas en conjuntos de datos de casos de uso del mundo real [34].</td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN
<table header-row="true">
<tr><td>Método de Integración</td><td>Protocolo</td><td>Autenticación</td><td>Latencia Típica</td><td>Límites de Rate</td></tr>
<tr><td>API (Alibaba Cloud Model Studio, OpenRouter, Venice AI), Qwen-Agent CLI [27] [29] [35]</td><td>OpenAI API compatible, Anthropic API compatible, Model Context Protocol (MCP) nativo [27] [28] [29]</td><td>Clave API (OpenRouter, Venice AI), OAuth (Qwen Code CLI) [36] [37]</td><td>No especificada públicamente.</td><td>No especificada públicamente.</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS
<table header-row="true">
<tr><td>Tipo de Test</td><td>Herramienta Recomendada</td><td>Criterio de Éxito</td><td>Frecuencia</td></tr>
<tr><td>Pruebas de Codificación Agentica</td><td>Qwen Studio, IDEs con integración de Qwen-Agent, entornos de ejecución de código.</td><td>Generación de código funcional y correcto, resolución de problemas a nivel de repositorio, refactorización exitosa sin introducir errores.</td><td>Continuo durante el desarrollo, pruebas de regresión con cada nueva versión.</td></tr>
<tr><td>Pruebas Multimodales</td><td>Qwen Studio, herramientas de procesamiento de datos multimodales.</td><td>Comprensión y generación precisa de contenido en múltiples modalidades (texto, imagen, video).</td><td>Regular, especialmente para nuevas capacidades multimodales.</td></tr>
<tr><td>Pruebas de Llamada a Herramientas (Tool Calling)</td><td>Jinja + Qwen3_XML + OpenCode 1.4.18, Playwright MCP Tool Calling.</td><td>Ejecución exitosa de herramientas externas, parsing correcto de las respuestas de las herramientas, integración fluida con flujos de trabajo de agentes.</td><td>Con cada nueva integración de herramientas o actualización de API.</td></tr>
<tr><td>Pruebas de Rendimiento y Escalabilidad</td><td>Herramientas de benchmarking de LLMs, monitoreo de latencia y throughput.</td><td>Latencia aceptable, alto throughput, manejo eficiente de ventanas de contexto grandes.</td><td>Periódico, especialmente antes de lanzamientos importantes.</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN
<table header-row="true">
<tr><td>Versión</td><td>Fecha de Lanzamiento</td><td>Estado</td><td>Cambios Clave</td><td>Ruta de Migración</td></tr>
<tr><td>Qwen3.6-Plus</td><td>1 de Abril de 2026 [38]</td><td>Activo</td><td>Mejoras en agentes de codificación, agentes generales y uso de herramientas, integración profunda de razonamiento y memoria, ventana de contexto de 1M de tokens [38].</td><td>Actualización desde Qwen3.5. Compatible con APIs de OpenAI y Anthropic, lo que facilita la migración desde otros modelos [27] [28].</td></tr>
<tr><td>Qwen3.6-35B-A3B</td><td>15 de Abril de 2026 [39]</td><td>Activo</td><td>Primer modelo Qwen3.6 de código abierto, capacidades de codificación agentica mejoradas, manejo de flujos de trabajo frontend y razonamiento a nivel de repositorio [39].</td><td>Migración desde Qwen3.5 y otros modelos de código abierto.</td></tr>
<tr><td>Qwen3.6-Max-Preview</td><td>17 de Abril de 2026 [40]</td><td>Activo (Vista Previa)</td><td>Mayor conocimiento del mundo y seguimiento de instrucciones, mejoras en codificación agentica, disponible a través de Alibaba Cloud Model Studio [40].</td><td>Actualización para usuarios de Alibaba Cloud Model Studio.</td></tr>
<tr><td>Qwen3.6-27B</td><td>22 de Abril de 2026 [41]</td><td>Activo</td><td>Modelo denso de 27 mil millones de parámetros, enfocado en estabilidad y utilidad en el mundo real [41].</td><td>Migración desde versiones anteriores de Qwen o modelos similares.</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA
<table header-row="true">
<tr><td>Competidor Directo</td><td>Ventaja vs Competidor</td><td>Desventaja vs Competidor</td><td>Caso de Uso Donde Gana</td></tr>
<tr><td>Claude Opus (4.5, 4.6, 4.7)</td><td>Rendimiento comparable en Terminal-Bench [31]. Qwen3.6-35B-A3B puede generar mejores imágenes en algunos casos [42]. Qwen3.6-Plus ofrece más control [43].</td><td>Claude Opus 4.6 es más fuerte en seguir instrucciones complejas de varios pasos [44].</td><td>Tareas de codificación agentica que requieren control granular y personalización [43]. Generación de imágenes específicas [42].</td></tr>
<tr><td>GPT-4, GPT-5.4 (xhigh)</td><td>Qwen3.6-Plus ofrece más control en comparación con la simplicidad de GPT-4 [43].</td><td>GPT-4 ofrece simplicidad y facilidad de uso [43].</td><td>Casos de uso donde la personalización y el control sobre el comportamiento del modelo son críticos [43].</td></tr>
<tr><td>Gemma 4</td><td>Qwen3.6 (35B-A3B) es un modelo MoE de código abierto ajustado para codificación agentica y multimodal [45].</td><td>Gemma 4-31B parece ser más inteligente en tareas generales [46].</td><td>Tareas de codificación agentica y multimodales específicas [45].</td></tr>
<tr><td>DeepSeek, Llama 3, Mistral Large, GPT-OSS-20B, GPT-OSS-120B, Xiaomi MiMo, Amazon Nova 2 Lite/Pro, Grok 4</td><td>Qwen3.6 se destaca en codificación agentica, planificación a largo plazo y uso de herramientas [47].</td><td>Algunos modelos como GPT-OSS-20B pueden escribir mejor código en ciertos escenarios [48].</td><td>Tareas que requieren una fuerte capacidad de agente, especialmente en entornos de terminal y con uso extensivo de herramientas [47].</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)
<table header-row="true">
<tr><td>Capacidad de IA</td><td>Modelo Subyacente</td><td>Nivel de Control</td><td>Personalización Posible</td></tr>
<tr><td>Codificación Agentica</td><td>Qwen3.6 (variantes como Qwen3.6-Plus, Qwen3.6-35B-A3B, Qwen3.6-27B, Qwen3.6-Max-Preview) [49]</td><td>Alto, a través de la configuración de prompts, el uso de `preserve_thinking` y la integración con frameworks de agentes como Qwen-Agent y OpenCode [50] [51].</td><td>Ajuste fino (fine-tuning) para tareas específicas de codificación, personalización de herramientas y flujos de trabajo de agentes.</td></tr>
<tr><td>Razonamiento Multimodal</td><td>Qwen3.6-Plus, Qwen VLo (para generación de imágenes) [15] [52]</td><td>Moderado a alto, dependiendo de la variante del modelo y la API utilizada. Qwen Studio ofrece funcionalidades para la comprensión y generación de imágenes y video [53].</td><td>Adaptación a diferentes tipos de datos multimodales, personalización de la interpretación y generación de contenido multimodal.</td></tr>
<tr><td>Generación de Texto y Código</td><td>Qwen3.6 (todos los modelos) [49]</td><td>Alto, a través de ingeniería de prompts, ajuste de parámetros de generación (temperatura, top-p, etc.) y uso de plantillas.</td><td>Ajuste fino para estilos de escritura específicos, dominios de código o formatos de salida.</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA
<table header-row="true">
<tr><td>Métrica</td><td>Valor Reportado por Comunidad</td><td>Fuente</td><td>Fecha</td></tr>
<tr><td>Rendimiento en Programación</td><td>"Bueno para programar, pero no tan bueno para escribir texto natural y conciso."</td><td>Reddit (r/LocalLLaMA) [54]</td><td>18 de Abril de 2026</td></tr>
<tr><td>Rendimiento en Codificación Agentica (Qwen3.6-35B vs 27B)</td><td>Qwen3.6-35B "resuelve problemas mejor que el 27B".</td><td>Reddit (r/LocalLLaMA) [55]</td><td>17 de Abril de 2026</td></tr>
<tr><td>Rendimiento en Unidades de Código Cortas (Qwen3.6-Max-Preview vs Claude Opus)</td><td>"Mucho mejor que Opus en unidades más cortas como métodos o funciones individuales."</td><td>Hacker News [56]</td><td>21 de Abril de 2026</td></tr>
<tr><td>Razonamiento Multimodal</td><td>Qwen3.6-Plus "percibe el mundo con mayor precisión y un razonamiento multimodal más nítido."</td><td>Qwen.ai Blog [57]</td><td>1 de Abril de 2026</td></tr>
<tr><td>Evaluaciones en el Mundo Real</td><td>Qwen3.6-27B "funciona bien en evaluaciones de estilo del mundo real como NL2Repo y QwenWebBench."</td><td>Medium (Data Science in Your Pocket) [58]</td><td>22 de Abril de 2026</td></tr>
<tr><td>Adopción Local</td><td>Considerado el "primer modelo local que realmente vale la pena el esfuerzo."</td><td>Reddit (r/LocalLLaMA) [59]</td><td>17 de Abril de 2026</td></tr>
<tr><td>Dependencia de Memoria para Rendimiento Local</td><td>El rendimiento óptimo requiere que la memoria total disponible (VRAM + RAM del sistema) "supere el tamaño del archivo del modelo cuantificado."</td><td>Unsloth Documentation [60]</td><td>28 de Abril de 2026</td></tr>
<tr><td>Impacto del Feedback Comunitario</td><td>El desarrollo de Qwen3.6 ha sido "moldeado por el feedback directo de la comunidad."</td><td>GitHub (QwenLM/Qwen3.6) [61]</td><td>Desconocido</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM
<table header-row="true">
<tr><td>Plan</td><td>Precio</td><td>Límites</td><td>Ideal Para</td><td>ROI Estimado</td></tr>
<tr><td>Qwen3.6-Plus (OpenRouter)</td><td>Input: $0.325/M tokens, Output: $1.95/M tokens [3]</td><td>Sujeto a límites de tasa de OpenRouter, puede experimentar errores 429 si se excede la cuota [68] [69].</td><td>Desarrollo de agentes del mundo real, codificación agentica, razonamiento multimodal [73].</td><td>No especificado.</td></tr>
<tr><td>Qwen3.6-27B (OpenRouter)</td><td>Input: $0.325/M tokens [62]</td><td>Sujeto a límites de tasa de OpenRouter [68].</td><td>Tareas de codificación agentica, visión, chat [70].</td><td>No especificado.</td></tr>
<tr><td>Qwen3.6-27B (ZeroEval API)</td><td>Input: $0.60/M tokens, Output: $3.60/M tokens [63]</td><td>No especificado.</td><td>No especificado.</td><td>No especificado.</td></tr>
<tr><td>Qwen3.6 Plus (AI-SDK.dev)</td><td>Input: $0.50/M tokens, Output: $3.00/M tokens [64]</td><td>No especificado.</td><td>No especificado.</td><td>No especificado.</td></tr>
<tr><td>Alibaba Cloud Model Studio</td><td>Varía según el modelo. No hay cuota gratuita para modelos globales (Virginia) [66].</td><td>Límites de tasa aplicados para garantizar el uso justo [67].</td><td>Desarrolladores y soluciones empresariales que buscan integrar Qwen3.6 directamente en sus aplicaciones [6].</td><td>No especificado.</td></tr>
<tr><td>Qwen3.6-35B-A3B (Open-source)</td><td>Gratuito (requiere hardware local) [39]</td><td>Depende del hardware local (VRAM, RAM) [70].</td><td>Codificación agentica, flujos de trabajo frontend, razonamiento a nivel de repositorio [39].</td><td>Alto, al eliminar costos de API para uso local y permitir personalización profunda.</td></tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING
<table header-row="true">
<tr><td>Escenario de Test</td><td>Resultado</td><td>Fortaleza Identificada</td><td>Debilidad Identificada</td></tr>
<tr><td>SWE-bench Pro, Terminal-Bench 2.0, SkillsBench, QwenClawBench, QwenWebBench, y HumanEval</td><td>Qwen3.6-Max-Preview logra la puntuación más alta [71].</td><td>Capacidad superior en codificación agentica y uso de herramientas [71].</td><td>No se especifica en este contexto.</td></tr>
<tr><td>Cuantificación de Qwen3.6</td><td>Estudio empírico de cuantificación de Qwen3.6 para identificar trade-offs de rendimiento y métodos óptimos [72].</td><td>Optimización del rendimiento para diferentes bit-widths [72].</td><td>Trade-offs de rendimiento inducidos por la cuantificación [72].</td></tr>
<tr><td>Red Teaming de Modelos de Razonamiento Grandes (LRMs)</td><td>Los LRMs carecen de robustez frente a prompts adversarios que inducen pasos de inferencia excesivos o innecesarios [73].</td><td>No se especifica en este contexto.</td><td>Falta de robustez frente a prompts adversarios [73].</td></tr>
<tr><td>Evaluación de Seguridad (Qwen 3.6 Max Preview)</td><td>81.4% de puntuación general de seguridad [74].</td><td>Buen rendimiento en sanitización de código, autenticación y control de acceso [74].</td><td>No se especifica en este contexto.</td></tr>
<tr><td>Vulnerabilidades de Seguridad (Needles and Haystacks)</td><td>Ninguno de los modelos insignia o de código abierto (incluyendo Qwen3.6) encontró dos vulnerabilidades específicas [75].</td><td>No se especifica en este contexto.</td><td>Posibles vulnerabilidades de seguridad no detectadas por los modelos actuales [75].</td></tr>
</table>