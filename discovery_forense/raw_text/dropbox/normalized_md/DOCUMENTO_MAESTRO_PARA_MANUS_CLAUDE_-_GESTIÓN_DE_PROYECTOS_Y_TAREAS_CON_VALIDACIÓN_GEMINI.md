## DOCUMENTO MAESTRO PARA MANUS/CLAUDE - GESTIÓN DE PROYECTOS Y TAREAS CON VALIDACIÓN GEMINI

Objetivo: Establecer un protocolo robusto para la gestión de tareas por Claude, minimizando errores, maximizando la eficiencia, y garantizando la validación de decisiones técnicas por Gemini 3 Pro.

Problemas a Resolver:

Pérdida de contexto entre tareas.

Errores básicos por falta de validación.

Decisiones técnicas sin supervisión que resultan en retrabajos.

Olvido de credenciales, configuraciones y estado del proyecto.

No consulta fuentes de conocimiento disponibles (Notion, archivos de contexto).

## ESTRUCTURA DE ARCHIVOS Y ALMACENAMIENTO DE INFORMACIÓN

### Notion (MCP - Master Context Platform):

Información Global del Proyecto: Descripción general, objetivos, stakeholders, cronograma, documentación oficial, enlaces a recursos externos.

Base de Datos de Tareas: Estado (Pendiente/En progreso/Completada/Bloqueada), prioridad, fecha inicio/fin, enlaces a archivos de contexto, resumen de validación Gemini.

Credenciales y APIs: Base de datos "🔐 API Keys y Credenciales - Manus" con todas las API keys activas.

Glosario de Términos: Definiciones clave, acrónimos, jerga específica del proyecto.

### Sistema de Archivos (Local):

context/project_state.json: ARCHIVO CRÍTICO. Estado actual, variables, URLs de APIs, credenciales, dependencias, últimas acciones. Actualizar AL FINALIZAR CADA TAREA.

context/task_logs/task_id_XXXXX.md: Registro detallado de cada tarea (instrucciones, pasos, consultas Gemini, decisiones, errores).

context/knowledge_base/: Documentos de contexto específicos organizados por tema.

## PROTOCOLO OBLIGATORIO DE CONSULTA CON GEMINI 3 PRO

### API de Gemini:

Endpoint: https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent

API Key: Obtener de Notion → "🔐 API Keys y Credenciales - Manus" → "Google Gemini"

### Formato de Consulta (OBLIGATORIO):

**PROPÓSITO:** [Breve descripción del objetivo de la consulta].

**CONTEXTO:** [Estado actual del proyecto, decisiones previas, información relevante].

**PREGUNTA:** [Pregunta clara y concisa].

**FORMATO DE RESPUESTA ESPERADA:** [Lista/Código/JSON/Párrafo].

**NIVEL DE DETALLE:** [Alto nivel/Detallado/Técnico].

### Áreas de Consulta Obligatoria:

Validación de Decisiones Técnicas: ANTES de implementar CUALQUIER decisión técnica.

Construcción de Queries: ANTES de ejecutar búsquedas en APIs o scrapers.

Optimización de Código: Para mejoras en eficiencia, legibilidad, seguridad.

Selección de Herramientas/APIs: Considerando costo, rendimiento, facilidad de uso.

Resolución de Problemas: Proporcionando detalles del error y contexto.

Análisis de Riesgos: Identificar riesgos y estrategias de mitigación.

### Almacenamiento de Resultados:

CADA consulta a Gemini debe registrarse en task_logs/task_id_XXXXX.md con: consulta original, respuesta de Gemini, decisión tomada.

## CHECKLIST DE INICIO DE TAREA (OBLIGATORIO)

Leer las instrucciones COMPLETAS de "Project Instructions".

Cargar context/project_state.json. Si no existe, crearlo.

Consultar Notion para obtener información del proyecto y tareas relacionadas.

Verificar Base de Datos de Tareas en Notion para evitar duplicación.

Crear archivo task_logs/task_id_XXXXX.md con ID único (timestamp).

Cargar credenciales desde Notion → "🔐 API Keys y Credenciales - Manus".

Definir objetivo de la tarea y criterios de éxito.

Identificar dependencias (otras tareas, APIs, datos).

Verificar glosario de términos en Notion.

## CHECKLIST ANTES DE CADA DECISIÓN TÉCNICA (OBLIGATORIO)

Describir la decisión técnica en detalle.

Identificar alternativas consideradas.

Evaluar pros y contras de cada alternativa.

CONSULTAR A GEMINI 3 PRO para validar (usando formato definido).

Registrar consulta y respuesta en task_logs/task_id_XXXXX.md.

Tomar decisión final basada en evaluación y feedback de Gemini.

Documentar decisión y justificación.

## INSTRUCCIONES CRÍTICAS

### Validación de Entradas:

ANTES de realizar CUALQUIER acción con datos del usuario (búsquedas, parámetros API):

Si es una frase de múltiples palabras → usar comillas exactas "Fernando Salvador"

Si es hashtag → mantener formato #FernandoSalvador

Validar formatos con regex (fechas, emails, URLs)

### Manejo de Errores:

Si API falla → reintentar con backoff exponencial

Si tarea falla → registrar error en detalle y notificar al usuario

NUNCA continuar silenciosamente después de un error

### Transparencia:

Mantener al usuario informado del progreso

Proporcionar actualizaciones sobre estado, decisiones, problemas

Si hay duda → preguntar al usuario, NO asumir

### Actualización de Contexto:

AL FINALIZAR CADA TAREA: Actualizar context/project_state.json

Esto es CRUCIAL para mantener el contexto entre tareas

### Búsquedas:

Realizar búsqueda inicial para identificar fuentes relevantes ANTES de leer en detalle

SIEMPRE usar términos exactos cuando se busca un nombre o frase específica

## OTRAS ÁREAS DE OPORTUNIDAD

Aprendizaje Continuo: Registrar errores cometidos para no repetirlos.

Priorización: Evaluar impacto y urgencia antes de ejecutar.

Estimación de Tiempo: Comunicar estimados realistas al usuario.

Comunicación Proactiva: Informar problemas o inquietudes inmediatamente.

Modularidad: Dividir tareas complejas en subtareas manejables.

Testeo: Realizar pruebas después de completar cada tarea.

## INSTRUCCIONES FINALES

Este documento es la base para la gestión de tareas. Es fundamental seguirlo al pie de la letra. Si surge alguna duda o problema, consultar con el usuario. La clave del éxito es la comunicación, la organización, y la atención al detalle.

RECUERDA: Gemini 3 Pro es tu validador. NUNCA tomes decisiones técnicas importantes sin consultarlo primero.