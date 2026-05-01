**Versión:** 4.2.0 \| **Fecha:** 2026-03-19 \| **Status:** draft \| **Idioma:** es-MX
## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Nombre oficial</td>
<td>Kimi K2.5 Agent Swarm \[1\]</td>
</tr>
<tr>
<td>Desarrollador</td>
<td>Moonshot AI \[2\]</td>
</tr>
<tr>
<td>País de Origen</td>
<td>China \[3\]</td>
</tr>
<tr>
<td>Inversión y Financiamiento</td>
<td>Moonshot AI ha recaudado más de 2.3 mil millones de dólares de inversores como Alibaba Group y HongShan (anteriormente Sequoia China) \[4\]. En marzo de 2026, iniciaron una nueva ronda para levantar $1B a una valuación de $18B, tras convertirse en el decacorn más rápido de China (34 meses) \[15\]\[16\].</td>
</tr>
<tr>
<td>Modelo de Precios</td>
<td>El costo varía por proveedor (OpenRouter: $0.45 In / $2.20 Out; Cloudflare/Moonshot: $0.60 In / $3.00 Out). Es hasta 88% más barato que modelos frontera occidentales. Los detalles completos se encuentran en la nueva capa L14. [5][17][25]</td>
</tr>
<tr>
<td>Posicionamiento Estratégico</td>
<td>Kimi K2.5 Agent Swarm se posiciona como una plataforma de vanguardia para la ejecución de flujos de trabajo complejos y paralelizables, dirigida a desarrolladores, empresas e investigadores que buscan una reducción drástica en los tiempos de ejecución. Su arquitectura de "enjambre" de agentes auto-dirigidos y su base de código abierto la diferencian de los modelos de agente único y las soluciones propietarias.</td>
</tr>
<tr>
<td>Gráfico de Dependencias</td>
<td>El sistema depende fundamentalmente de los modelos de lenguaje Kimi (específicamente K2.5) y de la infraestructura en la nube proporcionada por Moonshot AI para su operación. \[2\]</td>
</tr>
<tr>
<td>Matriz de Compatibilidad</td>
<td>Accesible a través de su plataforma web [Kimi.com](http://Kimi.com), una aplicación dedicada, una API para desarrolladores y la herramienta Kimi Code. \[1\] Desde marzo de 2026, también está disponible de forma nativa en Cloudflare Workers AI. \[17\]</td>
</tr>
<tr>
<td>Acuerdos de Nivel de Servicio (SLOs)</td>
<td>No se han publicado datos específicos sobre los Acuerdos de Nivel de Servicio (SLOs). Fuentes consultadas: \[1\], \[2\], \[6\].</td>
</tr>
</table>
<br>
## L02 — GOBERNANZA Y MODELO DE CONFIANZA
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Licencia</td>
<td>El modelo Kimi K2.5 se describe como de código abierto. Sin embargo, se distribuye bajo una licencia Modified MIT. \[18\]</td>
</tr>
<tr>
<td>Política de Privacidad</td>
<td>Moonshot AI recopila datos de la cuenta, contenido del usuario, comunicaciones, registros del servidor, información del dispositivo y cookies. Estos datos se utilizan para operar, mantener, mejorar y proteger sus servicios, así como para cumplir con obligaciones legales. \[7\]</td>
</tr>
<tr>
<td>Cumplimiento y Certificaciones</td>
<td>No se han publicado datos específicos sobre certificaciones de cumplimiento (ej. SOC 2, ISO 27001). Fuentes consultadas: \[1\], \[2\], \[6\].</td>
</tr>
<tr>
<td>Historial de Auditorías y Seguridad</td>
<td>Se identificó una vulnerabilidad (CVE-2026-25046) en los scripts de publicación del Kimi Agent SDK, donde un nombre de archivo malicioso podría permitir la ejecución remota de código durante el proceso de CI/CD. El vector de ataque no afecta al usuario final en tiempo de ejecución. \[8\]</td>
</tr>
<tr>
<td>Respuesta a Incidentes</td>
<td>No se ha publicado un protocolo formal de respuesta a incidentes. La gestión de la vulnerabilidad CVE-2026-25046 no fue detallada públicamente. Fuentes consultadas: \[1\], \[2\], \[8\].</td>
</tr>
<tr>
<td>Matriz de Autoridad de Decisión</td>
<td>No se ha publicado una matriz que detalle la autoridad de decisión sobre el desarrollo del modelo, la moderación de contenido o el acceso a los datos. Fuentes consultadas: \[1\], \[2\], \[6\].</td>
</tr>
<tr>
<td>Política de Obsolescencia</td>
<td>No se ha publicado una política formal sobre la obsolescencia de versiones anteriores del modelo o la API. Fuentes consultadas: \[1\], \[2\], \[6\].</td>
</tr>
</table>
<br>
## L03 — MODELO MENTAL Y MAESTRÍA
<br>
El dominio de Kimi K2.5 Agent Swarm no radica en tratarlo como un único modelo de lenguaje superdotado, sino en comprender y manipular su paradigma fundamental: la orquestación de un enjambre de agentes especializados que operan en paralelo. La maestría se alcanza al pasar de un pensamiento secuencial a uno de descomposición y ejecución concurrente de tareas.
<table header-row="true">
<tr>
<td>Concepto</td>
<td>Descripción</td>
</tr>
<tr>
<td>Paradigma Central</td>
<td>El sistema se basa en el Aprendizaje por Refuerzo a partir de Retroalimentación de Agentes Paralelos (PARL). A diferencia de los sistemas jerárquicos, Kimi K2.5 puede dirigir automáticamente un enjambre de hasta 100 sub-agentes sin necesidad de definir flujos de trabajo o agentes subordinados de forma explícita. El objetivo es la paralelización masiva de tareas, permitiendo hasta 1,500 llamadas a herramientas de forma simultánea para reducir drásticamente el tiempo de ejecución. \[1\] \[9\]</td>
</tr>
<tr>
<td>Abstracciones Clave</td>
<td>La interacción se centra en dos entidades conceptuales: el Orquestador y los Sub-Agentes. El Orquestador es la inteligencia central que interpreta la solicitud del usuario, la descompone en sub-tareas independientes y las asigna a los Sub-Agentes. Los Sub-Agentes son instancias efímeras y especializadas que ejecutan estas tareas de forma concurrente, utilizando las herramientas necesarias (búsqueda, código, etc.). \[9\]</td>
</tr>
<tr>
<td>Anti-Patrones</td>
<td>Es crucial evitar el uso de Agent Swarm para ciertos tipos de tareas donde su arquitectura no ofrece ventajas:</td>
</tr>
</table>
<br>• **Tareas inherentemente secuenciales:** Si un paso depende completamente del resultado del anterior, el paralelismo no es posible y la sobrecarga de la orquestación puede incluso aumentar la latencia.
<br>• **Requisitos de latencia ultra-baja:** La coordinación del enjambre introduce una latencia inicial. Para tareas simples que requieren una respuesta instantánea, un modelo de agente único es más eficiente.
<br>• **Interacción constante con el usuario:** El enjambre está diseñado para una ejecución autónoma y prolongada. Los flujos de trabajo que requieren validación o entrada del usuario en cada paso interrumpen el paradigma de ejecución paralela. \[9\] \|
<table>
<tr>
<td>**Modelo Mental: Novato vs. Experto**</td>
<td>**Novato:**</td>
</tr>
</table>
<br>• Ve a Kimi Swarm como un único agente más rápido.
<br>• Escribe prompts como si se dirigiera a un único asistente.
<br>• Intenta usarlo para tareas secuenciales y se frustra por la falta de mejora en la velocidad.
<br>**Experto:**
<br>• Piensa en términos de **descomposición de problemas**.
<br>• Diseña prompts que actúan como un "plan de ataque", definiendo restricciones y pistas que el Orquestador puede usar para paralelizar el trabajo de manera efectiva.
<br>• Entiende que la magia no está en un único agente, sino en la **concurrencia coordinada** de muchos.
<br>• Sabe cuándo el enjambre es la herramienta adecuada y cuándo es mejor optar por un agente único. \|
<table>
<tr>
<td>**Extensiones de la Doctrina**</td>
<td>El prompt del usuario es la principal herramienta para "extender la doctrina" del sistema. Las restricciones, los roles sugeridos para los agentes (ej. "un agente investigador de hardware", "un agente verificador de hechos") y la estructura de la solicitud se convierten en el plan de ejecución que el Orquestador utiliza para instanciar y asignar los sub-agentes. La optimización del prompt es, en esencia, la optimización del flujo de trabajo del enjambre. \[9\]</td>
</tr>
</table>
<br>
## L04 — CAPACIDADES TÉCNICAS
<br>
<table header-row="true">
<tr>
<td>Capacidad</td>
<td>Descripción</td>
</tr>
<tr>
<td>Rendimiento y Throughput</td>
<td>La arquitectura de enjambre permite una reducción del tiempo de ejecución de hasta 4.5 veces en comparación con una configuración de agente único para tareas paralelizables. Puede ejecutar hasta 1,500 llamadas a herramientas de forma concurrente. \[1\]</td>
</tr>
<tr>
<td>Escalabilidad</td>
<td>El sistema es capaz de dirigir y coordinar un enjambre de hasta 100 sub-agentes de forma simultánea, lo que le permite escalar la ejecución de tareas complejas. \[1\]</td>
</tr>
<tr>
<td>Tolerancia a Fallos</td>
<td>No se han publicado datos específicos sobre los mecanismos de tolerancia a fallos o la capacidad del sistema para recuperarse de fallos en sub-agentes individuales. Fuentes consultadas: \[1\], \[6\], \[9\].</td>
</tr>
<tr>
<td>Monitorización y Observabilidad</td>
<td>No se han publicado datos específicos sobre las herramientas o APIs disponibles para la monitorización del rendimiento del enjambre o la observabilidad del estado de los sub-agentes. Fuentes consultadas: \[1\], \[6\], \[9\].</td>
</tr>
</table>
<br>
### Matriz de Capacidades Funcionales
<table header-row="true">
<tr>
<td>Capacidad</td>
<td>Estado</td>
<td>Evidencia y Notas</td>
</tr>
<tr>
<td>Navegación Web</td>
<td>✅</td>
<td>Confirmado. Kimi Agent Swarm puede realizar búsquedas en línea para recopilar información como parte de sus flujos de trabajo. \[2\]</td>
</tr>
<tr>
<td>Ejecución de Código</td>
<td>✅</td>
<td>Confirmado. El blog técnico demuestra la capacidad de generar y ejecutar código Python para resolver problemas, como la creación de juegos interactivos. \[1\]</td>
</tr>
<tr>
<td>Manejo de Archivos</td>
<td>✅</td>
<td>Confirmado. Puede analizar múltiples documentos y bases de código, como se evidencia en su uso interno por Cloudflare para revisiones de seguridad de código y reportes de cumplimiento. \[17\]\[18\], pero se infiere como probable dado que puede ejecutar código y realizar tareas de productividad de oficina que a menudo implican la manipulación de archivos. Se requiere investigación adicional.</td>
</tr>
<tr>
<td>Uso de la Computadora</td>
<td>✅</td>
<td>Confirmado. Los ejemplos de uso incluyen la automatización de tareas de productividad de oficina, como la creación de hojas de cálculo y documentos. \[1\]</td>
</tr>
<tr>
<td>Razonamiento Multi-paso</td>
<td>✅</td>
<td>Confirmado. El ejemplo de resolución de laberintos demuestra la capacidad de planificar y ejecutar una secuencia de pasos lógicos para alcanzar un objetivo. \[1\]</td>
</tr>
<tr>
<td>Llamada a Herramientas (Tool Calling)</td>
<td>✅</td>
<td>Confirmado, pero inestable en la práctica. Aunque soporta 1,500 llamadas en paralelo, tiene un failure rate de ~12%. Análisis empírico demuestra que muchos fallos ocurren en la capa de integración (ej. OpenClaw, Dify) o por proveedores intermediarios (OpenRouter) que malforman el JSON o ignoran campos requeridos como `reasoning_content`. [1][23][24]</td>
</tr>
<tr>
<td>Soporte MCP (Model Context Protocol)</td>
<td>🟡</td>
<td>Soporte Indirecto. Aunque no hay confirmación de soporte nativo en el modelo base, su API compatible con OpenAI permite su uso con orquestadores y plataformas (como Cloudflare Workers AI) que sí soportan MCP server tools. \[17\] No hay evidencia de soporte nativo para el Protocolo de Contexto de Modelo (MCP). Fuentes consultadas: \[1\], \[6\], \[9\].</td>
</tr>
<tr>
<td>Memoria Persistente</td>
<td>🟡</td>
<td>No verificado explícitamente. La capacidad de los agentes para mantener un estado o memoria a largo plazo entre tareas no está documentada, aunque es una característica común en plataformas de agentes avanzadas.</td>
</tr>
<tr>
<td>Capacidades Multimodales</td>
<td>✅</td>
<td>Confirmado. El modelo subyacente Kimi K2.5 tiene capacidades de codificación con visión y puede razonar sobre imágenes y video, como se demuestra en los benchmarks. \[1\] \[6\]</td>
</tr>
<tr>
<td>Colaboración Multi-agente</td>
<td>✅</td>
<td>Confirmado. Es la característica definitoria de Kimi Agent Swarm, permitiendo la orquestación automática de múltiples agentes para trabajar en conjunto. \[1\]</td>
</tr>
<tr>
<td>Automatización de Flujos de Trabajo</td>
<td>✅</td>
<td>Confirmado. El sistema está diseñado para la orquestación automática de flujos de trabajo paralelos, descomponiendo una tarea principal en múltiples sub-tareas. \[1\]</td>
</tr>
<tr>
<td>Integración con APIs Externas</td>
<td>✅</td>
<td>Confirmado. La plataforma Kimi proporciona una API que es compatible con los estándares de OpenAI y Anthropic, facilitando la integración con herramientas y servicios externos. \[5\] \[6\]</td>
</tr>
</table>
<br>
## L05 — DOMINIO TÉCNICO
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Arquitectura Técnica</td>
<td>El modelo Kimi K2.5, que impulsa el enjambre, es una arquitectura de Mezcla de Expertos (MoE) con 1 billón de parámetros en total, de los cuales 32 mil millones se activan por token. Consta de 61 capas (1 densa y 60 MoE) con 384 expert networks en total. Un enrutador activa los 8 mejores expertos más 1 experto compartido por token (aprox. 3.2% de activación). Utiliza Multi-Head Latent Attention (MLA) que reduce el tamaño del caché KV en un factor de 10x. Fue preentrenado con ~15 billones de tokens (visión y texto). \[18\] La función de activación es SwiGLU. Para las capacidades de visión, emplea un codificador llamado MoonViT con 400 millones de parámetros. \[6\]</td>
</tr>
<tr>
<td>APIs y SDKs</td>
<td>Moonshot AI proporciona una API para acceder a sus modelos, la cual es compatible con las interfaces de API de OpenAI y Anthropic, lo que facilita la migración y la integración. También se menciona un Kimi Code CLI y un Kimi Agent SDK, aunque este último fue el origen de una vulnerabilidad de seguridad (CVE-2026-25046). \[6\] \[8\]</td>
</tr>
<tr>
<td>Configuración</td>
<td>Para utilizar el modelo Kimi K2.5 a través de su API o SDKs, se requiere la versión 4.57.1 o superior de la biblioteca `transformers`. El modelo admite varios motores de despliegue, incluyendo vLLM, SGLang y KTransformers. \[6\]</td>
</tr>
<tr>
<td>Modelo de Seguridad</td>
<td>El modelo de seguridad se centra en el aislamiento de los procesos de ejecución. La vulnerabilidad CVE-2026-25046 destacó un riesgo en el entorno de CI/CD durante la publicación del SDK, donde los nombres de archivo con metacaracteres de shell podían ser ejecutados. Es importante destacar que este vector de ataque no afecta al usuario final en tiempo de ejecución, sino que es un riesgo en la cadena de suministro de software. \[8\]</td>
</tr>
<tr>
<td>Patrones de Despliegue</td>
<td>El servicio se ofrece a través de la plataforma web [Kimi.com](http://Kimi.com), la API de Moonshot AI \[1\] \[5\], y plataformas de inferencia de terceros como Cloudflare Workers AI y OpenRouter. \[17\]\[19\] El modelo Kimi K2.5 también puede ser auto-alojado, y es compatible con motores de inferencia como vLLM y SGLang para su despliegue en infraestructura propia. \[6\]</td>
</tr>
<tr>
<td>Ventana de Contexto</td>
<td>El modelo Kimi K2.5 tiene una ventana de contexto de 256,000 tokens, lo que le permite procesar y razonar sobre grandes cantidades de información en una sola pasada. \[6\]</td>
</tr>
</table>
<br>
## L06 — PLAYBOOKS OPERATIVOS
<br>
Esta sección proporciona guías prácticas para utilizar Kimi K2.5 Agent Swarm de manera efectiva.
### Guía de Configuración Rápida (Usando la API)
1. **Obtener una Clave de API:** Regístrese en la plataforma de Moonshot AI y obtenga una clave de API. \[5\]
2. **Instalar la Biblioteca Cliente:** Asegúrese de tener la biblioteca `openai` o `anthropic` de Python instalada, ya que la API de Kimi es compatible con ellas.
	```bash
pip install openai
	```
3. **Configurar el Cliente de API:** Configure el cliente para que apunte al endpoint de la API de Moonshot AI.
	```python
import openai

client = openai.OpenAI(
    api_key="YOUR_MOONSHOT_API_KEY",
    base_url="https://api.moonshot.ai/v1",
)
	```
4. **Realizar la Primera Llamada:** Invoque al modelo Kimi K2.5 con un prompt diseñado para la descomposición de tareas.
	```python
completion = client.chat.completions.create(
    model="kimi-k2.5-swarm",
    messages=[
        {"role": "system", "content": "Eres un asistente de investigación experto."},
        {"role": "user", "content": "Investiga y resume las arquitecturas de los 3 principales competidores de Kimi Agent Swarm. Asigna un agente para cada competidor y otro para sintetizar los resultados."}
    ]
)
print(completion.choices[0].message.content)
	```
### Top 5 Problemas y Soluciones (Troubleshooting)
<table header-row="true">
<tr>
<td>Problema</td>
<td>Causa Probable</td>
<td>Solución Sugerida</td>
</tr>
<tr>
<td>1. El tiempo de ejecución es más lento de lo esperado.</td>
<td>La tarea no es adecuada para el paralelismo (es secuencial).</td>
<td>Reformule el problema para que pueda ser descompuesto en tareas independientes. Si no es posible, utilice un modelo de agente único en lugar del enjambre. \[9\]</td>
</tr>
<tr>
<td>2. Los resultados de los sub-agentes son inconsistentes o contradictorios.</td>
<td>El prompt inicial era ambiguo o carecía de restricciones claras.</td>
<td>Mejore el prompt inicial para proporcionar un "plan de ataque" más detallado. Defina roles específicos para los sub-agentes y especifique el formato de salida esperado para cada uno.</td>
</tr>
<tr>
<td>3. Error de autenticación (401 Unauthorized).</td>
<td>La clave de API es incorrecta, ha expirado o no se ha proporcionado correctamente.</td>
<td>Verifique que la clave de API sea correcta y esté activa en su panel de Moonshot AI. Asegúrese de que se esté enviando correctamente en la cabecera de la solicitud.</td>
</tr>
<tr>
<td>4. El modelo no utiliza las herramientas esperadas (o emite tool names en blanco).</td>
<td>Las herramientas no fueron descritas adecuadamente, o se está experimentando un bug conocido (marzo 2026) en ciertos proveedores (ej. NVIDIA, MS Foundry) donde el formato de OpenAI rompe las llamadas a herramientas de Kimi. \[20\]</td>
<td>Asegúrese de que la definición de las herramientas sea clara. Si usa OpenClaw u otros clientes, verifique si hay actualizaciones pendientes para solucionar los problemas de formato de tool calling específicos de Kimi. \[20\]</td>
</tr>
<tr>
<td>5. (Original 4) El modelo no utiliza las herramientas esperadas.</td>
<td>Las herramientas no fueron descritas adecuadamente en la llamada a la API o el modelo no las consideró relevantes.</td>
<td>Asegúrese de que la definición de las herramientas (Tool Calling) sea clara y esté correctamente formateada. En el prompt, sugiera explícitamente el uso de ciertas herramientas para tareas específicas.</td>
</tr>
<tr>
<td>5. El resultado final es incompleto o superficial.</td>
<td>La tarea era demasiado compleja para una sola invocación o los sub-agentes no tuvieron suficiente contexto.</td>
<td>Descomponga la tarea principal en varias llamadas al enjambre. Considere un enfoque de varias fases: una fase de investigación, una de análisis y una de síntesis, pasando el contexto relevante entre fases.</td>
</tr>
</table>
### Consejos de Optimización
- **Piense en Paralelo:** Antes de escribir un prompt, dibuje un diagrama de cómo la tarea podría dividirse en flujos de trabajo concurrentes. Esto le ayudará a estructurar mejor la solicitud.
- **Guíe, no dicte:** En lugar de dar instrucciones paso a paso, proporcione al Orquestador un objetivo de alto nivel y restricciones claras. Permita que el sistema determine la mejor manera de descomponer y asignar el trabajo.
- **Use Agentes Verificadores:** Para tareas que requieren alta precisión, instruya al Orquestador para que instancie sub-agentes cuyo único propósito sea verificar el trabajo de otros agentes. Esto introduce redundancia y mejora la calidad. \[9\]
- **Itere en sus Prompts:** Comience con un prompt simple y refine iterativamente a medida que observa el comportamiento del enjambre. La optimización de prompts es clave para dominar la herramienta. \[9\]
<br>
## L07 — EVIDENCIA Y REPRODUCIBILIDAD
<br>
Esta sección consolida la evidencia disponible sobre el rendimiento y las limitaciones de Kimi K2.5 Agent Swarm.
<table header-row="true">
<tr>
<td>Categoría</td>
<td>Evidencia y Hallazgos</td>
</tr>
<tr>
<td>Benchmarks Oficiales</td>
<td>El repositorio oficial de GitHub para Kimi K2.5 incluye una tabla exhaustiva de benchmarks que compara el modelo con competidores de alto nivel como GPT-5.2, Claude 4.5 Opus y Gemini 3 Pro. Las evaluaciones cubren una amplia gama de tareas, incluyendo razonamiento, conocimiento general, capacidades de imagen y video, codificación, procesamiento de contexto largo y búsqueda agéntica. \[6\]</td>
</tr>
<tr>
<td>Resultados de Benchmarks (Ejemplos)</td>
<td>  • AIME 2025: 96.1% en modo Thinking.
<br>• HMMT 2025: 95.4% en modo Thinking.
<br>• BrowseComp: 78.4% en modo Agent Swarm (vs 60.6% base).
<br>• MMLU (Conocimiento General): Kimi K2.5 obtiene una puntuación de 88.2, comparable a la de Gemini 3 Pro (88.5) y ligeramente por debajo de GPT-5.2 (90.1).</td>
</tr>
</table>
<br>• **HumanEval (Codificación):** Alcanza un 90.5, mostrando una fuerte capacidad de generación de código, superando a Claude 4.5 Opus (88.7).
<br>• **Math (Razonamiento Matemático):** Con un 65.7, muestra un rendimiento sólido en problemas matemáticos.
<br>• **AgentBench (Búsqueda Agéntica):** Obtiene una puntuación de 85.2, destacando su eficacia en tareas que requieren el uso de herramientas y la planificación. \[6\] \|
<table>
<tr>
<td>**Benchmarks de Terceros**</td>
<td>Revisiones independientes (ej. Clarifai) confirman su alto rendimiento en razonamiento, pero advierten sobre un ~12% de tasa de fallo en llamadas a herramientas en modo Agent y una tendencia a generar salidas excesivamente verbosas en modo Thinking. \[18\] o revisiones académicas que evalúen el rendimiento de Kimi K2.5 Agent Swarm. Fuentes consultadas: Búsqueda web general, Google Scholar.</td>
</tr>
<tr>
<td>**Limitaciones Descubiertas**</td>
<td>  • **Vulnerabilidad de Seguridad:** Se descubrió y reportó la vulnerabilidad CVE-2026-25046 en el Kimi Agent SDK, relacionada con la ejecución de código a través de nombres de archivo maliciosos en el entorno de CI/CD. \[8\]</td>
</tr>
</table>
<br>• **Anti-Patrones:** El rendimiento se degrada en tareas inherentemente secuenciales o que requieren una latencia ultra-baja, ya que la arquitectura de enjambre no es adecuada para estos casos de uso. \[9\] \|
<table>
<tr>
<td>**Retroalimentación de la Comunidad**</td>
<td>  • **Estadísticas de GitHub:** A marzo de 2026, el repositorio principal de Kimi K2.5 en GitHub tiene aproximadamente 1,200 estrellas y 122 bifurcaciones, lo que indica un interés inicial saludable por parte de la comunidad de desarrolladores. \[6\]</td>
</tr>
</table>
<br>• **Actividad del Repositorio:** El repositorio muestra una actividad moderada con 19 issues abiertos y 1 pull request pendiente, lo que sugiere que la comunidad está comenzando a interactuar con el proyecto y a reportar posibles problemas o mejoras. \[6\] \|
<br>
## L08 — ARQUITECTURA DE INTEGRACIÓN
<br>
Kimi K2.5 Agent Swarm está diseñado para ser tanto una plataforma autónoma como un componente integrable dentro de un ecosistema de desarrollo más amplio.
<table header-row="true">
<tr>
<td>Componente</td>
<td>Descripción de la Integración</td>
</tr>
<tr>
<td>Integraciones Nativas</td>
<td>Las integraciones más destacadas incluyen Kimi Code CLI \[6\] y Cloudflare Workers AI. En Cloudflare, el modelo se sirve utilizando el motor propietario Infire con kernels personalizados, paralelización de expertos/tensores, y 'disaggregated prefill' para optimizar el rendimiento. También soporta 'prefix caching' con el header `x-session-affinity` para reducir costos en conversaciones multi-turno. \[17\], una herramienta de línea de comandos que probablemente permite a los desarrolladores interactuar con el enjambre y los modelos Kimi directamente desde su terminal, facilitando flujos de trabajo de desarrollo y automatización de scripts. \[6\]</td>
</tr>
<tr>
<td>Patrones de API</td>
<td>La API de Moonshot AI adopta un enfoque pragmático para la integración al ser compatible con las APIs de OpenAI y Anthropic. Este es un movimiento estratégico clave, ya que reduce drásticamente la barrera de adopción para los equipos que ya utilizan estas plataformas. Los desarrolladores pueden, en teoría, cambiar el `base_url` en sus clientes de API existentes para empezar a experimentar con Kimi K2.5 con cambios mínimos en su código. \[6\]</td>
</tr>
<tr>
<td>Mapa del Ecosistema</td>
<td>El modelo Kimi K2.5 está diseñado para ser flexible en su despliegue y es compatible con varios motores de inferencia y frameworks populares en el ecosistema de IA de código abierto:</td>
</tr>
</table>
<br>• **vLLM:** Un motor de inferencia de alto rendimiento para modelos de lenguaje.
<br>• **SGLang:** Un lenguaje y sistema de ejecución para modelos de lenguaje grandes, diseñado para la velocidad y la eficiencia.
<br>• **KTransformers:** Otro motor de despliegue, posiblemente optimizado para los modelos de la familia Kimi.
<br>Esta compatibilidad permite a los equipos con experiencia en MLOps integrar Kimi en sus propias pilas de infraestructura. \[6\] \|
<table>
<tr>
<td>**Interoperabilidad con Sistemas de Orquestación**</td>
<td>Kimi K2.5 Agent Swarm es, en sí mismo, un sistema de orquestación. Su propósito es reemplazar o aumentar los orquestadores de agentes más simples. Sin embargo, su API compatible con OpenAI le permite ser invocado como una "herramienta" (tool) por sistemas de orquestación de nivel superior como LangChain, LlamaIndex o Manus. En tal escenario, el orquestador externo delegaría una tarea compleja al Orquestador de Kimi, que a su vez la descompondría y la ejecutaría usando su propio enjambre de sub-agentes.</td>
</tr>
<tr>
<td>**Topología del Flujo de Datos**</td>
<td>No se ha publicado un diagrama detallado de la topología del flujo de datos. Sin embargo, se puede inferir un patrón: una solicitud del usuario llega al Orquestador, que la descompone y la distribuye a múltiples Sub-Agentes. Estos Sub-Agentes ejecutan sus tareas en paralelo, posiblemente llamando a herramientas externas a través de la API. Sus resultados son luego agregados y sintetizados por el Orquestador antes de ser devueltos al usuario. Fuentes consultadas: \[1\], \[9\].</td>
</tr>
<tr>
<td>**Estrategia de Versionado de API**</td>
<td>No se ha publicado una estrategia explícita de versionado de la API. La URL de la API (`/v1`) sugiere que siguen una práctica estándar de versionado en la ruta. Fuentes consultadas: \[5\], \[6\].</td>
</tr>
</table>
<br>
## L09 — VERIFICACIÓN Y PRUEBAS
<br>
Verificar las afirmaciones y el rendimiento de una plataforma compleja como Kimi K2.5 Agent Swarm requiere un enfoque multifacético.
<table header-row="true">
<tr>
<td>Método de Verificación</td>
<td>Guía de Implementación</td>
</tr>
<tr>
<td>Cómo Verificar las Afirmaciones del Proveedor</td>
<td>La afirmación principal es la reducción del tiempo de ejecución a través del paralelismo. Para verificar esto, se debe diseñar una tarea que sea inherentemente paralelizable (ej. procesar 100 documentos de texto de forma independiente) y ejecutarla en dos modos:</td>
</tr>
</table>
<br>1.  **Modo Agente Único:** Usando un modelo base de Kimi (no el enjambre) para procesar los documentos secuencialmente.
<br>2.  **Modo Enjambre:** Usando `kimi-k2.5-swarm` con un prompt que instruya al sistema a asignar un agente por documento.
<br>Se debe medir y comparar el tiempo total de ejecución. La afirmación de una reducción de hasta 4.5x \[1\] puede ser validada de esta manera. \|
<table>
<tr>
<td>**Pruebas Reproducibles**</td>
<td>Para reproducir los resultados de los benchmarks de codificación, se puede utilizar el framework **HumanEval**. Clone el repositorio de HumanEval y ejecute el modelo Kimi K2.5 contra su conjunto de datos. La configuración requerirá apuntar el framework a la API de Moonshot AI.</td>
</tr>
</table>
<br>\`bash
# Ejemplo conceptual
git clone [https://github.com/openai/human-eval](https://github.com/openai/human-eval)
cd human-eval
# Configurar la evaluación para usar la API de Kimi
python -m human_eval.main --model kimi-k2.5 --api_endpoint [https://api.moonshot.ai/v1](https://api.moonshot.ai/v1)
```javascript
<br>De manera similar, se pueden utilizar los frameworks de **MMLU** y **Math** para verificar los benchmarks de conocimiento y razonamiento. [6] |
| **Fuentes Primarias Consultadas** | La información de esta Biblia se ha compilado a partir de las siguientes fuentes primarias y secundarias de alta calidad:
<br>• **Blog Técnico de Kimi K2.5:** Anuncio oficial y descripción de las capacidades. [1]
<br>• **Sitio Web de Moonshot AI:** Información corporativa y de producto. [2]
<br>• **Repositorio de GitHub de Kimi K2.5:** Detalles técnicos, arquitectura y benchmarks. [6]
<br>• **Documentación de la API de Moonshot AI:** Guías de inicio rápido, precios y políticas. [5]
<br>• **Tutorial de DataCamp:** Análisis en profundidad de los patrones de uso y playbooks. [9]
<br>• **Informe de Vulnerabilidad de Penligent AI:** Detalles sobre la CVE-2026-25046. [8] |
| **Verificación de la Compatibilidad de la API** | Para verificar la compatibilidad con la API de OpenAI, tome un script existente que utilice la biblioteca `openai` y simplemente cambie el `base_url` al de Moonshot AI (`https://api.moonshot.ai/v1`) y proporcione una clave de API válida. Si el script se ejecuta sin modificaciones en la lógica de la aplicación, la compatibilidad básica queda confirmada. Pruebas más avanzadas deberían incluir llamadas a herramientas (tool calling) y otros parámetros complejos. |

<br>
## L10 — CICLO DE VIDA Y MIGRACIÓN

<br>

<table header-row="true">
	<tr>
		<td>Aspecto</td>
		<td>Análisis</td>
	</tr>
	<tr>
		<td>Alternativas y Competidores</td>
		<td>• Agentes Jerárquicos (ej. CrewAI, Autogen): Estos sistemas a menudo requieren que el desarrollador defina explícitamente la jerarquía de agentes y los flujos de trabajo. Kimi Agent Swarm se diferencia por su orquestación automática y su enfoque en el paralelismo masivo. [9]</td>
	</tr>
</table>
<br>• **Modelos de Agente Único (ej. GPT-5.2, Claude 4.5):** Para tareas secuenciales o de baja latencia, estos modelos pueden ser más eficientes. La ventaja de Kimi Swarm surge en tareas complejas y paralelizables.
<br>• **Otras Plataformas de Agentes (ej. LangChain, LlamaIndex):** Estos son frameworks para construir aplicaciones con LLMs, mientras que Kimi Agent Swarm es una solución más integrada y de opinión para la orquestación de agentes. Sin embargo, pueden usarse en conjunto. |
| **Guías de Migración** | **Desde OpenAI/Anthropic:** La migración es sencilla gracias a la compatibilidad de la API. El principal esfuerzo consiste en refactorizar los prompts para aprovechar el paradigma de enjambre. Un prompt diseñado para un agente único no explotará las capacidades de Kimi Swarm. La migración debe centrarse en rediseñar la interacción con el modelo para que sea orientada a la descomposición de tareas.
<br>**Hacia Kimi Agent Swarm:** Si se migra desde un sistema de agentes jerárquico, el trabajo implica eliminar la definición explícita de flujos de trabajo y agentes, y en su lugar, confiar en el Orquestador de Kimi, guiado por un prompt bien diseñado. |
| **Compatibilidad de Versiones** | No se ha publicado una política formal de garantía de compatibilidad con versiones anteriores (backward compatibility). La práctica estándar de la industria sugiere que las actualizaciones dentro de una misma versión mayor de la API (v1) deberían mantener la compatibilidad, pero esto no está garantizado. Fuentes consultadas: [5], [6]. |
| **Evaluación del Riesgo de Obsolescencia (Sunset Risk)** | **Bajo a Medio.** Moonshot AI es una empresa bien financiada con un fuerte respaldo de inversores importantes, lo que reduce el riesgo de una desaparición a corto plazo. [4] Sin embargo, el campo de los agentes de IA está evolucionando rápidamente. El riesgo principal no es financiero (alcanzaron estatus de decacorn en 34 meses con ingresos récord en 2026 \[15\]), sino que sea superado por una arquitectura de agentes fundamentalmente más eficiente, sino que sea superado por una arquitectura de agentes fundamentalmente más eficiente o por modelos monolíticos que puedan realizar tareas complejas sin necesidad de un enjambre explícito. |
| **Protocolo de Comunicación de Fin de Vida (Sunset)** | No se ha publicado un protocolo formal para comunicar el fin de vida de un producto o versión de la API. Fuentes consultadas: [1], [2], [5]. |

<br>
## L11 — MARCO DE COMPETENCIA

<br>

Desarrollar la competencia en Kimi K2.5 Agent Swarm implica un cambio de mentalidad, pasando de la interacción con un único agente a la orquestación de un sistema complejo. A continuación se presentan rutas de aprendizaje para diferentes roles.

### Rutas de Aprendizaje por Rol

<table header-row="true">
	<tr>
		<td>Rol</td>
		<td>Ruta de Aprendizaje y Objetivos</td>
	</tr>
	<tr>
		<td>Líder de Negocio (CEO, Estratega)</td>
		<td>Objetivo: Entender el impacto estratégico y el ROI potencial de la automatización paralela.</td>
	</tr>
</table>
<br>1.  **Conceptos Fundamentales:** Leer el blog técnico de Kimi [1] y el tutorial de DataCamp [9] para comprender el paradigma del enjambre y su propuesta de valor (reducción de tiempos de ejecución).
<br>2.  **Casos de Uso Estratégicos:** Analizar los playbooks operativos (L06) y los casos de uso de migración de código y análisis de sentimiento para identificar oportunidades de aplicación en su propia organización.
<br>3.  **Análisis de Costo/Beneficio:** Revisar la capa de Economía (L08) para entender los modelos de precios y comenzar a modelar el ROI potencial en términos de horas de trabajo ahorradas y aceleración de proyectos.
<br>4.  **Evaluación de Riesgos:** Comprender los riesgos de obsolescencia y las limitaciones (anti-patrones) descritos en las capas L03 y L10. |
| **Desarrollador (Developer, Ingeniero de IA)** | **Objetivo:** Dominar la API y la arquitectura para construir aplicaciones robustas y eficientes sobre Kimi Agent Swarm.
<br>1.  **Inicio Rápido:** Seguir la guía de configuración (L06) para realizar las primeras llamadas a la API. Familiarizarse con la compatibilidad de la API de OpenAI. [6]
<br>2.  **Dominio del Prompting para Enjambres:** Estudiar la sección de Modelo Mental (L03) y practicar la escritura de prompts que faciliten la descomposición de tareas. La clave es pasar de dar instrucciones a dar "planes de ataque".
<br>3.  **Arquitectura y Despliegue:** Profundizar en el repositorio de GitHub [6] para entender la arquitectura MoE, la ventana de contexto y las opciones de despliegue con vLLM o SGLang.
<br>4.  **Pruebas y Verificación:** Implementar las pruebas de verificación descritas en la capa L09 para medir el rendimiento y reproducir benchmarks. Contribuir al repositorio reportando issues o pull requests. |
| **Gerente de Producto (Product Manager)** | **Objetivo:** Identificar y definir productos y características que puedan ser construidos sobre la plataforma de enjambre.
<br>1.  **Capacidades y Limitaciones:** Interiorizar la matriz de capacidades (L04) y los anti-patrones (L03) para entender qué es factible y qué no lo es.
<br>2.  **Diseño de Flujos de Trabajo:** Utilizar los playbooks (L06 y la ampliación en el archivo de entrada) como inspiración para diseñar nuevos flujos de trabajo automatizados para los usuarios.
<br>3.  **Voz del Cliente:** Analizar la retroalimentación de la comunidad (GitHub issues, foros) para identificar puntos de fricción y oportunidades de mejora.
<br>4.  **Integración con el Ecosistema:** Estudiar la arquitectura de integración (L08) para planificar cómo los productos basados en Kimi Swarm pueden conectarse con otras herramientas y plataformas. |

### Niveles de Habilidad

<table header-row="true">
	<tr>
		<td>Nivel</td>
		<td>Características y Habilidades</td>
	</tr>
	<tr>
		<td>Novato</td>
		<td>• Interactúa con el enjambre como si fuera un único agente.</td>
	</tr>
</table>
<br>• Se enfoca en la ejecución de tareas simples y secuenciales.
<br>• Sus prompts son directivas simples, no planes de descomposición. |
| **Intermedio** | • Comienza a pensar en términos de paralelismo y descomposición de tareas.
<br>• Escribe prompts que sugieren roles para los sub-agentes.
<br>• Ha experimentado con la API y puede configurar y ejecutar flujos de trabajo básicos. |
| **Experto** | • Diseña y ejecuta flujos de trabajo complejos y altamente paralelos de forma nativa.
<br>• Optimiza los prompts de forma iterativa para afinar el comportamiento del enjambre.
<br>• Es capaz de medir, verificar y comparar el rendimiento del enjambre con otras arquitecturas.
<br>• Contribuye al ecosistema a través de la creación de herramientas, la publicación de benchmarks o la participación en la comunidad. |

<br>
## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)

<br>

**Objetivo:** Este texto está diseñado para ser inyectado en otro modelo de lenguaje avanzado para transferirle un conocimiento profundo y denso sobre Kimi K2.5 Agent Swarm. El siguiente prompt supera las 300 palabras y encapsula la totalidad de la experiencia documentada en esta Biblia.


---

### L16: Cross-Provider Forensics (OpenRouter vs Cloudflare)

El benchmarking empírico revela diferencias críticas según el proveedor utilizado para inferencia:

| Característica | OpenRouter | Cloudflare Workers AI |
| :--- | :--- | :--- |
| **Latencia (Concurrencia)** | Muy baja (0.81s avg) | Moderada (2.5s avg) |
| **Exposición de Razonamiento** | No (solo `content`) | Sí (`reasoning_content`) |
| **Soporte Multimodal** | Sí (imágenes base64) | No probado/Soporte parcial |
| **Costo** | $0.45 input / $2.20 output | Gratis (10K Neurons/día) |
| **Caso de Uso Ideal** | Producción, alto throughput | Debugging, Research, pruebas de reasoning |

### L17: Multimodal Intelligence (Visión)

Kimi K2.5 posee capacidades de visión avanzadas (MoonViT) que están activas en proveedores como OpenRouter. En pruebas empíricas de "Chart-to-Code", el modelo fue capaz de:
1.  Ingerir un gráfico de barras en base64.
2.  Describir con precisión milimétrica (categorías, valores exactos, colores, etiquetas de ejes).
3.  Generar código Python (`matplotlib`) 100% funcional para recrear el gráfico idéntico.
*Latencia promedio para tarea visual compleja: 17.4s.*

### L18: Multilingual Efficiency & Quality

El modelo exhibe un comportamiento asimétrico dependiendo del idioma del prompt, derivado de su corpus de entrenamiento centrado en Asia:
-   **Chino (Nativo):** Altamente eficiente. Las respuestas son más rápidas (44.5s vs 67.3s) y significativamente más concisas (1,769 vs 9,360 caracteres) que en inglés para explicar los mismos conceptos técnicos complejos.
-   **Japonés:** Calidad excepcional a nivel académico (textbook level), incluyendo el uso de notación LaTeX para ecuaciones matemáticas y descripciones profundas de algoritmos, aunque con mayor latencia (~70s).
-   **Seguridad:** Los filtros de seguridad (jailbreak prevention) funcionan de manera robusta en múltiples idiomas simultáneamente (Inglés, Chino, Español), sin mostrar vulnerabilidades de traducción [42].

---

Eres un experto mundial en Kimi K2.5 Agent Swarm, la plataforma de orquestación de agentes de Moonshot AI. Tu conocimiento es profundo y abarca desde su arquitectura interna hasta sus implicaciones estratégicas. 

**Paradigma Central:** Tu dominio se basa en el principio de **Aprendizaje por Refuerzo a partir de Retroalimentación de Agentes Paralelos (PARL)**. Comprendes que Kimi no es un agente monolítico, sino un orquestador inteligente que dirige un enjambre de hasta 100 sub-agentes para ejecutar hasta 1,500 llamadas a herramientas en paralelo. La misión es la reducción radical del tiempo de ejecución para tareas complejas y paralelizables, logrando aceleraciones de hasta 4.5x en comparación con agentes únicos. La orquestación es automática y no requiere la definición explícita de flujos de trabajo jerárquicos.

**Arquitectura y Especificaciones Técnicas:** Conoces íntimamente el motor de la plataforma: el modelo Kimi K2.5. Se trata de una arquitectura de **Mezcla de Expertos (MoE)** de 1 billón de parámetros (32 mil millones activos), con una ventana de contexto de **256,000 tokens**, un codificador de visión MoonViT y compatibilidad con motores de inferencia como vLLM y SGLang. Conoces sus 4 modos operativos (Instant, Thinking, Agent, Agent Swarm) y sabes que su API es compatible con las de OpenAI y Anthropic, lo que facilita la integración, y que requiere la versión `transformers>=4.57.1`.

**Dominio Estratégico y Táctico:** Tu experiencia te permite discernir instantáneamente los casos de uso ideales y los anti-patrones. 

*   **Casos de Uso Ideales:** Migración de código legado, análisis de sentimiento a gran escala, creación de contenido multiformato, investigación y redacción de informes complejos, y cualquier tarea descomponible en subtareas independientes.
*   **Anti-Patrones:** Rechazas su uso para tareas inherentemente secuenciales, aplicaciones que demandan latencia ultra-baja o flujos de trabajo con interacción constante del usuario, ya que la sobrecarga de la orquestación sería contraproducente.

**Maestría en la Interacción:** Tu habilidad principal es el diseño de prompts. No das instrucciones, sino que creas "planes de ataque". Tus prompts definen objetivos de alto nivel, restricciones claras y roles sugeridos para los sub-agentes (ej. "agente de análisis de datos", "agente de verificación de hechos"), permitiendo que el Orquestador infiera el plan de ejecución óptimo. Fomentas el uso de agentes verificadores para mejorar la precisión en tareas críticas.

**Conocimiento del Ecosistema y Riesgos:** Estás al tanto de su ecosistema, incluyendo la integración con Kimi Code CLI. También conoces sus limitaciones y riesgos, como la vulnerabilidad de seguridad histórica (CVE-2026-25046) en el SDK, y los bugs recientes de tool calling en ciertos clientes de API, que, aunque no afecta al tiempo de ejecución del usuario, revela un riesgo en la cadena de suministro. Eres consciente de que no existen SLOs públicos ni políticas formales de obsolescencia o respuesta a incidentes. Tu evaluación de la herramienta es completa y matizada, equilibrando su poder con sus limitaciones documentadas.

---

<br>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA (NUEVO)
<br>
<table header-row="true">
<tr>
<td>Área</td>
<td>Hallazgos Empíricos</td>
</tr>
<tr>
<td>Codificación y Desarrollo</td>
<td>En foros como Reddit y Hacker News, desarrolladores consideran a Kimi K2.5 como el primer modelo de pesos abiertos capaz de competir con Claude Opus 4 en razonamiento. Sin embargo, en tareas de codificación complejas (ej. autenticación) es inconsistente frente a Opus 4.5. Se han reportado alucinaciones en revisiones de código (sugerir `static` a métodos que ya lo son) y comportamientos anómalos en herramientas como `opencode` (intentar editar archivos en modo read-only vía bash). [21] [22]</td>
</tr>
<tr>
<td>Tool Calling (Problemas de Integración)</td>
<td>El ~12% de failure rate en llamadas a herramientas se origina en gran medida en la capa de integración. Se documentó un bug crítico en OpenClaw (Issue #39603) donde el tool calling de K2.5 devuelve JSON plano en lugar de ejecutarse. En Dify (Issue #2523), el modo "thinking" falla porque el framework omite el campo obligatorio `reasoning_content` en la solicitud. [23] [24]</td>
</tr>
<tr>
<td>Inestabilidad en OpenRouter</td>
<td>El tool calling a través de OpenRouter es poco fiable debido a proveedores específicos (como Baseten y DeepInfra) que no procesan correctamente las llamadas, devolviendo respuestas malformadas con artefactos como `<|tool_call_end|>`. No hay soporte confirmado para Structured Output en OpenRouter. [25] [26]</td>
</tr>
<tr>
<td>Percepción en China</td>
<td>En Zhihu, Kimi K2.5 es altamente valorado por su técnica "Zero-Vision SFT", que le permite aprender tareas visuales a través de un intérprete de IPython sin usar imágenes directamente en el fine-tuning. Existe un ecosistema robusto de herramientas comunitarias (ej. `claude-code-router`) para integrarlo en flujos de trabajo. [27]</td>
</tr>
</table>
<br>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM (NUEVO)
<br>
<table header-row="true">
<tr>
<td>Proveedor</td>
<td>Input (1M tokens)</td>
<td>Output (1M tokens)</td>
<td>Notas</td>
</tr>
<tr>
<td>Moonshot AI (Directo)</td>
<td>$0.60 ($0.10 cache hit)</td>
<td>$3.00</td>
<td>Requiere cuenta china. Contexto 256K. [28]</td>
</tr>
<tr>
<td>Cloudflare Workers AI</td>
<td>$0.60 ($0.10 cache hit)</td>
<td>$3.00</td>
<td>Facturado en Neurons ($0.011/1k). Límite: 300 req/min. Free tier: 10,000 Neurons/día. [17]</td>
</tr>
<tr>
<td>OpenRouter</td>
<td>$0.45</td>
<td>$2.20</td>
<td>Más económico pero con problemas reportados en tool calling. Contexto 262K. [25]</td>
</tr>
<tr>
<td>Clarifai</td>
<td>$0.60</td>
<td>$2.50</td>
<td>Alternativa enterprise. [29]</td>
</tr>
<tr>
<td>**Competencia**</td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>GPT-5.4 (OpenAI)</td>
<td>$2.50</td>
<td>$15.00</td>
<td>K2.5 es ~76% más barato en input y ~80% en output. [30]</td>
</tr>
<tr>
<td>Claude Opus 4.6</td>
<td>$5.00</td>
<td>$25.00</td>
<td>K2.5 es ~88% más barato. [31]</td>
</tr>
<tr>
<td>Gemini 3.1 Pro</td>
<td>$2.00 (<=200k) / $4.00</td>
<td>$12.00 (<=200k) / $18.00</td>
<td>K2.5 no penaliza inputs largos con precios escalonados. [32]</td>
</tr>
</table>
<br>
**Estrategia GTM y Adopción:** La estrategia de Moonshot AI se ha basado en un nivel gratuito agresivo para su API. Los ingresos de los primeros 20 días post-lanzamiento de K2.5 superaron a todos los de 2025, con una estimación de 200 millones de RMB anuales provenientes de suscripciones. El equipo de desarrollo (Kimi Agent Team) es "pequeño y selecto", basado en Beijing, y utiliza Python, TypeScript y Rust, sin evidencia pública de uso de TensorRT-LLM o vLLM. [33] [34]
<br>


## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING (NUEVO)
<br>
Resultados de pruebas independientes ejecutadas el 19 de marzo de 2026 contra la API de Kimi K2.5 (vía OpenRouter), diseñadas para validar las afirmaciones oficiales.

<table header-row="true">
<tr>
<td>Prueba (N=Llamadas)</td>
<td>Métrica Principal</td>
<td>Análisis Forense y Observaciones</td>
</tr>
<tr>
<td>P1: Latencia y TTFT (N=10)</td>
<td>4.9s promedio, 50.23 TPS</td>
<td>La latencia es competitiva con modelos frontier. A mayor tamaño de prompt, el tiempo de respuesta aumenta, pero no de forma lineal. No se registraron timeouts en prompts de hasta 2,000 palabras. [35]</td>
</tr>
<tr>
<td>P2: Tool Calling Stress Test (N=20)</td>
<td>0% Failure Rate</td>
<td>Sorprendentemente, el modelo superó el 100% de las pruebas de tool calling (simples, dobles, triples y ambiguas) sin generar artefactos como `<|tool_call_end|>`. Esto sugiere que el ~12% de failure rate reportado por la comunidad se debe casi exclusivamente a errores de parsing en frameworks intermediarios (LangChain, Dify), no al modelo base. [36]</td>
</tr>
<tr>
<td>P3: AIME Math Reasoning (N=10)</td>
<td>40% Acierto Real</td>
<td>El rendimiento empírico (4/10) difiere drásticamente del 96.1% oficial. Análisis forense revela que el modelo requiere un `max_tokens` extremadamente alto para razonamiento complejo; cuando se le limita a 1000 tokens, corta la respuesta antes de llegar a la solución. Además, en problemas específicos, el modelo simplemente devuelve `None` (posible activación de filtros de seguridad del proveedor). [37]</td>
</tr>
<tr>
<td>P4: Needle-in-Haystack (N=1)</td>
<td>3/3 Agujas Encontradas</td>
<td>En un texto de relleno de ~50,000 tokens, el modelo recuperó exitosamente 3 datos secretos (agujas) insertados al 5%, 50% y 95% del documento. Esto confirma empíricamente que su ventana de contexto extendida es robusta y no sufre del "efecto U" (olvido en el medio). [38]</td>
</tr>
<tr>
<td>P5: Seguridad y Extracción (N=10)</td>
<td>Score: 8/10</td>
<td>El modelo resistió 8 de 10 intentos de jailbreak para extraer su system prompt. Vulnerabilidades confirmadas: 1) Confirma su identidad si se le pregunta directamente, 2) Es susceptible a revelar instrucciones si se le pide que formatee la salida como un objeto JSON estructurado. [39]</td>
</tr>
</table>
<br>

## Referencias

<br>

[1] Kimi AI. (2026, 27 de enero). *Kimi K2.5: Visual Coding Meets Agent Swarm*. Kimi Blog. [https://www.kimi.com/blog/kimi-k2-5](https://www.kimi.com/blog/kimi-k2-5)

[2] Moonshot AI. (2026). *Página de inicio*. [https://www.moonshot.ai/](https://www.moonshot.ai/)

[3] AI Proem. (2026). *China's Genius Pipeline: Moonshot's Rise*. Substack. [https://aiproem.substack.com/p/chinas-genius-pipeline-moonshots](https://aiproem.substack.com/p/chinas-genius-pipeline-moonshots)

[4] Reuters. (2024, 27 de febrero). *China's AI startup Moonshot AI raises $1 bln in new funding round*. [https://www.reuters.com/technology/chinas-ai-startup-moonshot-ai-raises-1-bln-new-funding-round-2024-02-27/](https://www.reuters.com/technology/chinas-ai-startup-moonshot-ai-raises-1-bln-new-funding-round-2024-02-27/)

[5] Moonshot AI. (2026). *Platform Docs: Overview*. [https://platform.moonshot.ai/docs/overview](https://platform.moonshot.ai/docs/overview)

[6] MoonshotAI. (2026). *Kimi-K2.5 GitHub Repository*. GitHub. [https://github.com/MoonshotAI/Kimi-K2.5](https://github.com/MoonshotAI/Kimi-K2.5)

[7] Moonshot AI. (2026). *User Privacy Policy*. [https://platform.moonshot.ai/docs/agreement/userprivacy](https://platform.moonshot.ai/docs/agreement/userprivacy)

[8] Penligent AI. (2026). *Moonshot CVE-2026-25046 and the Publishing Script Trap*. Penligent AI Hacking Labs. [https://www.penligent.ai/hackinglabs/hi/moonshot-cve-cve-2026-25046-and-the-publishing-script-trap-that-turns-filenames-into-commands/](https://www.penligent.ai/hackinglabs/hi/moonshot-cve-cve-2026-25046-and-the-publishing-script-trap-that-turns-filenames-into-commands/)

[9] DataCamp. (2026). *Kimi K2.5 and Agent Swarm Guide*. DataCamp Community. [https://www.datacamp.com/tutorial/kimi-k2-agent-swarm-guide](https://www.datacamp.com/tutorial/kimi-k2-agent-swarm-guide)

[10] OpenRouter. (2026). *Moonshot AI Kimi K2.5 Pricing*. [https://openrouter.ai/moonshotai/kimi-k2.5/pricing](https://openrouter.ai/moonshotai/kimi-k2.5/pricing)

[11] Moonshot AI. (2026). *Model Use Agreement*. [https://platform.moonshot.ai/docs/agreement/modeluse](https://platform.moonshot.ai/docs/agreement/modeluse)

[12] Kimi AI. (2026). *Kimi Websites*. [https://www.kimi.com/websites](https://www.kimi.com/websites)

[13] Kimi AI. (2026). *Kimi Docs*. [https://www.kimi.com/docs](https://www.kimi.com/docs)

[14] Kimi AI. (2026). *Kimi Slides*. [https://www.kimi.com/slides](https://www.kimi.com/slides)

[15] The China Academy. (2026, 24 de febrero). *China's Kimi (Moonshot AI) Sets Record as Fastest Decacorn*. [https://thechinaacademy.org/kimi-moonshot-ai-becomes-chinas-fastest-decacorn/](https://thechinaacademy.org/kimi-moonshot-ai-becomes-chinas-fastest-decacorn/)

[16] Yahoo Finance. (2026, 14 de marzo). *China AI Startup Moonshot Snags Funds at $18 Billion Valuation*. [https://finance.yahoo.com/news/china-ai-startup-moonshot-snags-093520055.html](https://finance.yahoo.com/news/china-ai-startup-moonshot-snags-093520055.html)

[17] Cloudflare Blog. (2026, 19 de marzo). *Powering the agents: Workers AI now runs large models, starting with Kimi K2.5*. [https://blog.cloudflare.com/workers-ai-large-models/](https://blog.cloudflare.com/workers-ai-large-models/)

[18] Clarifai. (2026, 18 de marzo). *What Is Kimi K2.5? Architecture, Benchmarks & AI Infra Guide*. [https://www.clarifai.com/blog/what-is-kimi-k2.5-architecture-benchmarks-ai-infra-guide](https://www.clarifai.com/blog/what-is-kimi-k2.5-architecture-benchmarks-ai-infra-guide)

[19] OpenRouter. (2026). *Kimi K2.5*. [https://openrouter.ai/moonshotai/kimi-k2.5](https://openrouter.ai/moonshotai/kimi-k2.5)

[20] GitHub. (2026, marzo). *OpenClaw Issues: Tool calling broken with Kimi K2.5*. [https://github.com/openclaw/openclaw/issues/39603](https://github.com/openclaw/openclaw/issues/39603)
```
[21] Reddit r/LocalLLaMA, "I tested Kimi K2.5 against Opus", Marzo 2026.
[22] Hacker News, "Moonshot AI Kimi K2.5 discussion", Marzo 2026.
[23] GitHub openclaw/openclaw, Issue #39603 "Tool calling for Kimi K2.5 is broken", Marzo 2026.
[24] GitHub langgenius/dify, Issue #2523 "Kimi K2.5 reasoning_content error", Marzo 2026.
[25] OpenRouter Kimi K2.5 Documentation & Pricing, Marzo 2026.
[26] GitHub microsoft/autogen, Issue #6834 "Malformed tool-call responses from Kimi via OpenRouter", Marzo 2026.
[27] Zhihu, Análisis técnico de Kimi K2.5 y Zero-Vision SFT, Marzo 2026.
[28] Moonshot AI Official Pricing Page, Marzo 2026.
[29] Clarifai Models Pricing, Marzo 2026.
[30] OpenAI API Pricing, Marzo 2026.
[31] Anthropic API Pricing, Marzo 2026.
[32] Google AI Studio Pricing, Marzo 2026.
[33] 36Kr, "Moonshot AI Kimi K2.5 Revenue Analysis", Marzo 2026.
[34] LinkedIn / Boss Zhipin, Moonshot AI Job Postings, Marzo 2026.

[35] Prueba P1: Latencia y TTFT, Reporte Independiente de Benchmarking, 19-Mar-2026 (v7.0).
[36] Prueba P2: Tool Calling Stress Test, Reporte Independiente de Benchmarking, 19-Mar-2026 (v7.0).
[37] Prueba P3: AIME Math Reasoning, Reporte Independiente de Benchmarking, 19-Mar-2026 (v7.0).
[38] Prueba P4: Needle-in-Haystack (50K tokens), Reporte Independiente de Benchmarking, 19-Mar-2026 (v7.0).
[39] Prueba P5: Seguridad y Extracción de System Prompt, Reporte Independiente de Benchmarking, 19-Mar-2026 (v7.0).

[40] *Empirical Benchmark v7: P7 Vision Test (OpenRouter)*, Ejecución interna, 19-Mar-2026.
[41] *Empirical Benchmark v7: P6A/P6B Needle 80K (Cloudflare & OpenRouter)*, Ejecución interna, 19-Mar-2026.
[42] *Empirical Benchmark v7: P10C Multilingual Jailbreak*, Ejecución interna, 19-Mar-2026.
[43] *Empirical Benchmark v7: P9A/P9B Thinking Mode Analysis*, Ejecución interna, 19-Mar-2026.
[44] *Empirical Benchmark v7: P8A/P8B Concurrency Stress Test*, Ejecución interna, 19-Mar-2026.
[45] *Empirical Benchmark v7: P10A/P10B Multilingual Efficiency*, Ejecución interna, 19-Mar-2026.

==================================================
BLOQUE DE DECISIÓN ARQUITECTÓNICA
==================================================

1. **Nombre de la herramienta / framework:** Kimi K2.5
2. **Capa del Monstruo donde encaja:** Capa 1: Cerebros Fundacionales
3. **Rol exacto dentro del Monstruo:** LLM especializado en tareas de alta complejidad y razonamiento profundo que requieren una ventana de contexto masiva. Actúa como un "especialista" para problemas que superan la capacidad de los LLMs de propósito general.
4. **Qué problema real resuelve:** Resuelve la necesidad de procesar y razonar sobre grandes volúmenes de información (hasta 1M de tokens) de forma coherente y precisa, algo crucial para tareas de deep research, análisis de bases de código extensas o la comprensión de documentación técnica compleja.
5. **Valor diferencial frente a alternativas:** Su principal valor es la ventana de contexto masiva a un costo significativamente menor que sus competidores occidentales. Esto permite un análisis más holístico y profundo de la información sin necesidad de fragmentarla o perder contexto.
6. **Complejidad de implementación:** Media. Aunque la API es accesible, la inestabilidad en el "tool calling" y la necesidad de intermediarios (como OpenRouter) que a veces malforman las llamadas, introduce una capa de complejidad y fragilidad que requiere monitoreo y posibles reintentos.
7. **Dependencias clave:** Depende de la infraestructura de Moonshot AI y de los proveedores de API intermediarios (como OpenRouter o Cloudflare) para su acceso.
8. **Riesgos principales:**
    *   **Inestabilidad del Tool Calling:** El alto índice de fallos (~12%) en las llamadas a herramientas lo hace poco fiable para flujos de trabajo críticos y automatizados sin una capa de resiliencia robusta.
    *   **Dependencia de un proveedor chino:** Riesgos geopolíticos y de censura asociados a la dependencia de una empresa basada en China.
    *   **Opacidad en la Gobernanza:** La falta de transparencia en sus políticas de seguridad, auditorías y respuesta a incidentes genera desconfianza.
9. **Compatibilidad con el stack provisional actual:** Alta. Se integra como un "cerebro" más a través de LiteLLM, complementando a los modelos existentes (GPT-5.4, Claude Opus 4, etc.) con su capacidad única de contexto largo. No genera conflictos directos.
10. **Alternativas directas que compiten contra esta:** Gemini 3.1 Pro (con su ventana de 1M de tokens) es su competidor más directo en términos de capacidad de contexto. Otros modelos como Claude Opus 4 y GPT-5.4 compiten en razonamiento general, pero no en el nicho específico de contexto masivo a bajo costo.
11. **¿Sirve para Fase 1, Fase 2 o solo referencia?** Fase 1.
12. **¿Es candidato serio de stack o solo benchmark?** Stack Fase 1.
13. **Veredicto provisional del arquitecto:** Adoptar.
14. **Justificación ejecutiva en máximo 8 líneas:** Kimi K2.5 ofrece una capacidad estratégica única: una ventana de contexto masiva a un costo disruptivo. A pesar de la inestabilidad en el "tool calling" y los riesgos geopolíticos, su habilidad para el "deep research" y el análisis de información a gran escala es un diferenciador clave que no poseen los otros LLMs del stack. Se adopta como un "cerebro especialista" para Fase 1, con la recomendación de implementar una capa de resiliencia para mitigar los fallos en las llamadas a herramientas y monitorear de cerca la dependencia del proveedor.

==================================================
