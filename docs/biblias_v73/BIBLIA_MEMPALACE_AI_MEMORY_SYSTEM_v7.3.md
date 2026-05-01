# BIBLIA DE MEMPALACE_AI_MEMORY_SYSTEM v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<table header-row="true">
<tr><td>Nombre oficial</td><td>MemPalace AI Memory System</td></tr>
<tr><td>Desarrollador</td><td>Milla Jovovich y Ben Sigman (con contribuciones de la comunidad)</td></tr>
<tr><td>País de Origen</td><td>No especificado (proyecto open-source distribuido)</td></tr>
<tr><td>Inversión y Financiamiento</td><td>Open-source, sin inversión de capital de riesgo (VC) mencionada. Desarrollo impulsado por la comunidad.</td></tr>
<tr><td>Modelo de Precios</td><td>Gratuito (open-source, licencia MIT). MemPalace Cloud ofrece un nivel gratuito (200 memorias, 1 herramienta, 30 días de búsqueda) y planes de pago.</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>Sistema de memoria AI local-first, de código abierto, con almacenamiento verbatim y recuperación semántica. Enfocado en privacidad de datos y costos cero en la nube. Supera a alternativas financiadas por VC en benchmarks de memoria.</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Backend de recuperación pluggable (ChromaDB por defecto). Requisito: Python 3.9+.</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Claude Code, Gemini CLI, herramientas compatibles con MCP, modelos locales.</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>No se encontraron SLOs explícitos para la versión open-source. Para MemPalace Cloud, se promete que las memorias nunca se eliminan.</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA
<table header-row="true">
<tr><td>Licencia</td><td>MIT (para la versión open-source)</td></tr>
<tr><td>Política de Privacidad</td><td>Al ser local-first, los datos permanecen en la máquina del usuario a menos que se opte por servicios en la nube. MemPalace Cloud tendrá su propia política de privacidad.</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>No se encontraron certificaciones específicas para la versión open-source. La naturaleza local-first reduce la necesidad de cumplimiento externo.</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>El proyecto es de código abierto, lo que permite la auditoría por parte de la comunidad. No se encontraron auditorías de seguridad formales publicadas.</td></tr>
<tr><td>Respuesta a Incidentes</td><td>Al ser un proyecto de código abierto, la respuesta a incidentes se gestiona a través de los canales de la comunidad de GitHub (issues, pull requests).</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>El desarrollo principal es liderado por Milla Jovovich y Ben Sigman, con contribuciones de la comunidad.</td></tr>
<tr><td>Política de Obsolescencia</td><td>No se encontró una política de obsolescencia explícita. Como proyecto de código abierto, la longevidad depende de la actividad de la comunidad y los mantenedores.</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA
MemPalace se basa en el concepto del 'palacio de la memoria' (method of loci), una técnica mnemotécnica antigua que organiza la información en una jerarquía espacial. Esto permite a los agentes de IA almacenar y recuperar recuerdos de conversaciones de forma contextual y estructurada, evitando la recuperación basada en palabras clave que a menudo resulta en "un almacén lleno de basura". Su enfoque local-first garantiza la privacidad y el control del usuario sobre sus datos.
<table header-row="true">
<tr><td>Paradigma Central</td><td>Memoria a largo plazo basada en la metáfora del "palacio de la memoria" (method of loci). Almacenamiento verbatim y recuperación semántica.</td></tr>
<tr><td>Abstracciones Clave</td><td>**Alas (Wings):** Personas y proyectos. **Salas (Rooms):** Temas. **Cajones (Drawers):** Contenido original (conversaciones, documentos).</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>Organización proactiva de la información en la estructura del palacio. Uso de búsquedas con ámbito para una recuperación precisa. Integración con flujos de trabajo locales para mantener la privacidad.</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>Confiar únicamente en la búsqueda por palabras clave. Permitir que los datos de memoria salgan de la máquina local sin consentimiento explícito.</td></tr>
<tr><td>Curva de Aprendizaje</td><td>Moderada para la configuración inicial y la comprensión de la arquitectura del palacio. Fácil para la integración con herramientas compatibles con MCP y el uso de la CLI.</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS
<table header-row="true">
<tr><td>Capacidades Core</td><td>Almacenamiento verbatim de historial de conversaciones. Recuperación semántica de información. Organización jerárquica de la memoria (alas, salas, cajones). Soporte para agentes especializados con alas y diarios individuales.</td></tr>
<tr><td>Capacidades Avanzadas</td><td>Grafo de conocimiento temporal con ventanas de validez (añadir, consultar, invalidar, línea de tiempo) respaldado por SQLite local. Hooks de auto-guardado para Claude Code. Herramientas MCP para operaciones de lectura/escritura del palacio, grafo de conocimiento y gestión de cajones.</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>Compresión AAAK 30x. Inicio en 170 tokens. Soporte para Python 3.13 en CI (Windows y macOS).</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>No realiza resumen, extracción o parafraseo de la memoria. Requiere Python 3.9+. Necesita un backend de almacén de vectores (ChromaDB por defecto). ~300 MB de disco para el modelo de embedding predeterminado.</td></tr>
<tr><td>Roadmap Público</td><td>El roadmap público se encuentra en `ROADMAP.md` en el repositorio de GitHub, mencionando un parche de estabilidad v3.1.1 y un plan v4.0.0-alpha.</td></tr>
</table>

## L05 — DOMINIO TÉCNICO
<table header-row="true">
<tr><td>Stack Tecnológico</td><td>Python 3.9+, ChromaDB (backend de vector-store por defecto), SQLite (para grafo de conocimiento).</td></tr>
<tr><td>Arquitectura Interna</td><td>Sistema local-first. Capa de recuperación pluggable. Arquitectura de palacio de memoria (alas, salas, cajones). Grafo de conocimiento temporal.</td></tr>
<tr><td>Protocolos Soportados</td><td>No se especifican protocolos de comunicación externos, ya que es un sistema local. Soporta la integración con herramientas compatibles con MCP.</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>Entrada: Texto verbatim (historial de conversaciones, archivos de proyecto). Salida: Texto recuperado semánticamente.</td></tr>
<tr><td>APIs Disponibles</td><td>API de Python (referencia en `mempalaceofficial.com/reference/python-api`). CLI (referencia en `mempalaceofficial.com/reference/cli`).</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS
<table header-row="true">
<tr><td>Caso de Uso</td><td>Minar archivos de proyecto en el palacio de memoria</td><td>Pasos Exactos</td><td>1. Instalar MemPalace (`pip install mempalace`). 2. Inicializar un nuevo palacio (`mempalace init ~/projects/myapp`). 3. Minar los archivos del proyecto (`mempalace mine ~/projects/myapp`).</td><td>Herramientas Necesarias</td><td>Python, pip, terminal.</td><td>Tiempo Estimado</td><td>Variable, dependiendo del tamaño del proyecto.</td><td>Resultado Esperado</td><td>Archivos del proyecto indexados y disponibles para búsqueda semántica en el palacio.</td></tr>
<tr><td>Caso de Uso</td><td>Buscar información específica en el palacio de memoria</td><td>Pasos Exactos</td><td>1. Asegurarse de que el palacio esté inicializado y minado. 2. Ejecutar una búsqueda (`mempalace search "por qué cambiamos a GraphQL"`).</td><td>Herramientas Necesarias</td><td>Terminal.</td><td>Tiempo Estimado</td><td>Segundos.</td><td>Resultado Esperado</td><td>Recuperación de fragmentos de conversación o documentos relevantes basados en la consulta semántica.</td></tr>
<tr><td>Caso de Uso</td><td>Cargar contexto para una nueva sesión de agente de IA</td><td>Pasos Exactos</td><td>1. Asegurarse de que el palacio esté minado con el contexto relevante. 2. Ejecutar el comando de activación (`mempalace wake-up`).</td><td>Herramientas Necesarias</td><td>Terminal, agente de IA compatible.</td><td>Tiempo Estimado</td><td>Segundos.</td><td>Resultado Esperado</td><td>El agente de IA tiene acceso al contexto de memoria a largo plazo de MemPalace.</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD
<table header-row="true">
<tr><td>Benchmark</td><td>LongMemEval (Raw, semantic search, no heuristics, no LLM)</td><td>Score/Resultado</td><td>96.6% R@5</td><td>Fecha</td><td>Abril 2026</td><td>Fuente</td><td>GitHub oficial de MemPalace, mempalaceofficial.com</td><td>Comparativa</td><td>El puntaje más alto publicado para un sistema de memoria AI gratuito y local-first.</td></tr>
<tr><td>Benchmark</td><td>LongMemEval (Hybrid v4, held-out 450q)</td><td>Score/Resultado</td><td>98.4% R@5</td><td>Fecha</td><td>Abril 2026</td><td>Fuente</td><td>GitHub oficial de MemPalace</td><td>Comparativa</td><td>Mejora con boosting de palabras clave y proximidad temporal.</td></tr>
<tr><td>Benchmark</td><td>LongMemEval (Hybrid v4 + LLM rerank)</td><td>Score/Resultado</td><td>≥99% R@5</td><td>Fecha</td><td>Abril 2026</td><td>Fuente</td><td>GitHub oficial de MemPalace</td><td>Comparativa</td><td>Requiere un LLM para reranking, funciona con modelos como Claude Haiku, Claude Sonnet, minimax-m2.7.</td></tr>
<tr><td>Benchmark</td><td>LoCoMo (session, top-10, no rerank)</td><td>Score/Resultado</td><td>60.3% R@10</td><td>Fecha</td><td>Abril 2026</td><td>Fuente</td><td>GitHub oficial de MemPalace</td><td>Comparativa</td><td>1,986 preguntas.</td></tr>
<tr><td>Benchmark</td><td>LoCoMo (hybrid v5, top-10, no rerank)</td><td>Score/Resultado</td><td>88.9% R@10</td><td>Fecha</td><td>Abril 2026</td><td>Fuente</td><td>GitHub oficial de MemPalace</td><td>Comparativa</td><td>Mismo conjunto de preguntas.</td></tr>
<tr><td>Benchmark</td><td>ConvoMem (all categories, 250 items)</td><td>Score/Resultado</td><td>92.9% Avg recall</td><td>Fecha</td><td>Abril 2026</td><td>Fuente</td><td>GitHub oficial de MemPalace</td><td>Comparativa</td><td>50 ítems por categoría.</td></tr>
<tr><td>Benchmark</td><td>MemBench (ACL 2025, 8,500 items)</td><td>Score/Resultado</td><td>80.3% R@5</td><td>Fecha</td><td>Abril 2026</td><td>Fuente</td><td>GitHub oficial de MemPalace</td><td>Comparativa</td><td>Todas las categorías.</td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN
<table header-row="true">
<tr><td>Método de Integración</td><td>Integración basada en MCP (Model Context Protocol). MemPalace expone 29 herramientas MCP.</td></tr>
<tr><td>Protocolo</td><td>Interno al sistema local. Para MCP, sigue el estándar del protocolo.</td></tr>
<tr><td>Autenticación</td><td>No requerida para la instalación local. Para integraciones MCP, se gestiona a través del sistema MCP.</td></tr>
<tr><td>Latencia Típica</td><td>Baja, ya que es un sistema local-first. No se especifican valores exactos.</td></tr>
<tr><td>Límites de Rate</td><td>No aplicable para la instalación local.</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS
<table header-row="true">
<tr><td>Tipo de Test</td><td>Pruebas de recuperación de memoria (LongMemEval, LoCoMo, ConvoMem, MemBench).</td></tr>
<tr><td>Herramienta Recomendada</td><td>Framework de benchmarks de MemPalace (scripts en `benchmarks/`).</td></tr>
<tr><td>Criterio de Éxito</td><td>Altos porcentajes de recall (R@5, R@10) en los benchmarks, superando a sistemas de memoria basados en la nube.</td></tr>
<tr><td>Frecuencia</td><td>Los benchmarks son reproducibles y se ejecutan para validar nuevas versiones y cambios.</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN
<table header-row="true">
<tr><td>Versión</td><td>v3.3.4 (última versión estable conocida al 30 de abril de 2026)</td></tr>
<tr><td>Fecha de Lanzamiento</td><td>Abril 2026 (para v3.3.4, según commits en GitHub)</td></tr>
<tr><td>Estado</td><td>Activo, en desarrollo continuo y con soporte de la comunidad.</td></tr>
<tr><td>Cambios Clave</td><td>v3.3.3: Restauración de integridad, solución de problemas de instalación. v3.3.0: Corrección de bloqueo de archivos para evitar duplicados multi-agente.</td></tr>
<tr><td>Ruta de Migración</td><td>Actualización vía `pip install --upgrade mempalace`. La compatibilidad con versiones anteriores se mantiene en la medida de lo posible para la estructura del palacio.</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA
<table header-row="true">
<tr><td>Competidor Directo</td><td>Mem0</td><td>Ventaja vs Competidor</td><td>Gratuito, local-first, mayor puntuación en LongMemEval (96.6% raw) sin LLM ni API.</td><td>Desventaja vs Competidor</td><td>Menor financiación (Mem0 tiene $24M).</td><td>Caso de Uso Donde Gana</td><td>Desarrolladores individuales o equipos pequeños que buscan memoria persistente con cero costos en la nube y privacidad de datos completa.</td></tr>
<tr><td>Competidor Directo</td><td>Zep</td><td>Ventaja vs Competidor</td><td>Gratuito (MemPalace) vs. planes de pago ($0-$475/mes para Zep Cloud). Local-first (MemPalace) vs. cloud-first (Zep).</td><td>Desventaja vs Competidor</td><td>Zep ofrece una solución más orientada a la nube y posiblemente más escalable para grandes empresas.</td><td>Caso de Uso Donde Gana</td><td>Proyectos que requieren una solución de memoria AI completamente local y de bajo costo.</td></tr>
<tr><td>Competidor Directo</td><td>Hindsight</td><td>Ventaja vs Competidor</td><td>MemPalace se enfoca en el almacenamiento verbatim y la recuperación semántica de alta precisión.</td><td>Desventaja vs Competidor</td><td>Hindsight incluye modelos mentales estructurados que se actualizan automáticamente, una característica que MemPalace no intenta.</td><td>Caso de Uso Donde Gana</td><td>Aplicaciones donde la fidelidad del recuerdo verbatim y la recuperación contextual son críticas.</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)
<table header-row="true">
<tr><td>Capacidad de IA</td><td>Recuperación de memoria para agentes de IA.</td></tr>
<tr><td>Modelo Subyacente</td><td>Sistema de recuperación semántica con backend pluggable (ChromaDB por defecto). No utiliza un LLM para la recuperación raw.</td></tr>
<tr><td>Nivel de Control</td><td>Alto. El usuario tiene control total sobre los datos de memoria al ser un sistema local-first.</td></tr>
<tr><td>Personalización Posible</td><td>Sí. La capa de recuperación es pluggable, permitiendo la integración de diferentes backends. Los agentes pueden tener sus propias "alas" y "diarios" personalizados.</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA
<table header-row="true">
<tr><td>Métrica</td><td>Estrellas en GitHub</td><td>Valor Reportado por Comunidad</td><td>50.6k (al 30 de abril de 2026)</td><td>Fuente</td><td>GitHub</td><td>Fecha</td><td>30 de abril de 2026</td></tr>
<tr><td>Métrica</td><td>Forks en GitHub</td><td>Valor Reportado por Comunidad</td><td>6.6k (al 30 de abril de 2026)</td><td>Fuente</td><td>GitHub</td><td>Fecha</td><td>30 de abril de 2026</td></tr>
<tr><td>Métrica</td><td>Adopción</td><td>Valor Reportado por Comunidad</td><td>Considerado el sistema de memoria AI de mayor puntuación y de código abierto.</td><td>Fuente</td><td>Artículos de prensa y redes sociales.</td><td>Fecha</td><td>Abril 2026</td></tr>
<tr><td>Métrica</td><td>Costo Anual (comparado con herramientas de resumen)</td><td>Valor Reportado por Comunidad</td><td>$10/año (MemPalace) vs $507/año (herramientas de resumen que pierden contexto).</td><td>Fuente</td><td>LinkedIn, Reddit.</td><td>Fecha</td><td>Abril 2026</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM
<table header-row="true">
<tr><td>Plan</td><td>Open-source (gratuito)</td><td>Precio</td><td>$0/año</td><td>Límites</td><td>Depende de los recursos locales del usuario.</td><td>Ideal Para</td><td>Desarrolladores, equipos pequeños, usuarios preocupados por la privacidad, proyectos con presupuestos limitados.</td><td>ROI Estimado</td><td>Alto, debido a la eliminación de costos de API y nube, y la mejora en la retención de contexto para agentes de IA.</td></tr>
<tr><td>Plan</td><td>MemPalace Cloud (Nivel Gratuito)</td><td>Precio</td><td>€0</td><td>Límites</td><td>200 memorias almacenadas, 1 herramienta conectada, 30 días de búsqueda.</td><td>Ideal Para</td><td>Usuarios que desean probar el servicio en la nube o tienen necesidades de memoria muy limitadas.</td><td>ROI Estimado</td><td>N/A (para nivel gratuito).</td></tr>
<tr><td>Plan</td><td>MemPalace Cloud (Planes de Pago)</td><td>Precio</td><td>No especificado en detalle, pero se menciona "precios simples y honestos".</td><td>Límites</td><td>Escalables según el plan.</td><td>Ideal Para</td><td>Usuarios que requieren mayor capacidad de memoria o más herramientas conectadas en un entorno gestionado.</td><td>ROI Estimado</td><td>Variable, dependiendo de las necesidades del usuario y el costo del plan.</td></tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING
<table header-row="true">
<tr><td>Escenario de Test</td><td>Recuperación de información en conversaciones largas y complejas.</td><td>Resultado</td><td>96.6% R@5 en LongMemEval (raw).</td><td>Fortaleza Identificada</td><td>Alta precisión en la recuperación de memoria verbatim, incluso sin el uso de LLMs para reranking.</td><td>Debilidad Identificada</td><td>La mejora del 0.6% para alcanzar el 100% en LongMemEval se logró inspeccionando respuestas incorrectas específicas, lo que indica un posible "enseñar para el examen".</td></tr>
<tr><td>Escenario de Test</td><td>Resistencia a la pérdida de contexto en agentes de IA.</td><td>Resultado</td><td>Mantiene el contexto a través de sesiones, proyectos y agentes.</td><td>Fortaleza Identificada</td><td>Diseño local-first y arquitectura de palacio de memoria que previene la "amnesia" de la IA.</td><td>Debilidad Identificada</td><td>No se encontraron pruebas de red teaming específicas publicadas que evalúen la robustez del sistema contra ataques maliciosos o manipulación de memoria.</td></tr>
<tr><td>Escenario de Test</td><td>Integración con diferentes LLMs y herramientas.</td><td>Resultado</td><td>Funciona con Claude Code, Gemini CLI, herramientas MCP y modelos locales.</td><td>Fortaleza Identificada</td><td>Flexibilidad y compatibilidad con un ecosistema diverso de herramientas de IA.</td><td>Debilidad Identificada</td><td>La dependencia de la comunidad para el desarrollo y mantenimiento podría ser una debilidad si la actividad disminuye.</td></tr>
</table>