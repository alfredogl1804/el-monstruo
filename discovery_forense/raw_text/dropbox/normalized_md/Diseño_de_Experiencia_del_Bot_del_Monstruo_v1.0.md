# Diseño de Experiencia del Bot del Monstruo v1.0

Documento de diseño basado en la consulta a los 6 Sabios (semilla v7.3)
Fecha: 6 de abril de 2026
Autor: Síntesis de GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro, Grok 4.20, Perplexity Sonar Pro, DeepSeek R1

## 1. Diagnóstico: Por qué el bot no sirve hoy

Los 6 sabios coinciden unánimemente en el mismo diagnóstico:

El bot actual es un router de APIs con branding. No tiene inteligencia propia. Toda la inteligencia viene de las APIs externas, y eso es exactamente lo que puedes obtener abriendo cada servicio directamente.

El problema no es técnico, es arquitectónico-cognitivo (Claude). El bot es un switch-case glorificado que no agrega ninguna capa de inteligencia propia del Monstruo.

## 2. Principio de diseño: El Monstruo no es un asistente, es un Chief of Staff

Gemini lo articuló mejor: el error es usar el paradigma del oráculo (le rezas y te devuelve una profecía) cuando debería ser el paradigma del Jefe de Estado Mayor — alguien que piensa contigo, no por ti.

Grok lo llevó más lejos: "El Monstruo es el primer empleado cabrón que Alfredo ha tenido." Uno que conoce sus patrones, sus fracasos anteriores, y no tiene miedo de decírselo.

Regla de oro: Si el bot puede ser reemplazado por copiar-pegar el prompt en ChatGPT, el bot no tiene razón de existir.

## 3. Flujo de interacción completo (5 fases)

ALFREDO ENVÍA MENSAJE

|

v

+---------------------+

|  FASE 1: INTAKE     |  <-- El Monstruo PIENSA antes de actuar (1-3s)

|  - Clasifica intent  |

|  - Busca memoria     |

|  - Detecta ambiguedad|

+----------+----------+

|

v

+---------------------+

|  FASE 2: BRIEFING   |  <-- El Monstruo MUESTRA su razonamiento

|  - Contexto mostrado |      y PREGUNTA si es necesario

|  - Plan de ataque    |

|  - Opciones de ruta  |

+----------+----------+

|

v

+---------------------+

|  FASE 3: ORQUESTA   |  <-- El Monstruo EJECUTA con estrategia

|  - Multi-cerebro     |      (prompts DIFERENTES por cerebro)

|  - Progreso en vivo  |

|  - Sintesis soberana |

+----------+----------+

|

v

+---------------------+

|  FASE 4: ENTREGA    |  <-- El Monstruo PRESENTA con estructura

|  - Resultado         |

|  - Transparencia     |

|  - Siguiente paso    |

+----------+----------+

|

v

+---------------------+

|  FASE 5: REGISTRO   |  <-- El Monstruo APRENDE

|  - Memoria episodica |

|  - Calidad tracking  |

+---------------------+

## 4. Detalle de cada fase

### FASE 1: INTAKE (1-3 segundos, invisible al usuario)

Qué pasa internamente:

Clasificar intención (tipo + complejidad + ambiguedad)

Buscar memoria relevante en Supabase/pgvector

Recuperar perfil del usuario y proyectos activos

Decidir ruta: preguntar primero vs ejecutar directo

Qué ve el usuario:

Procesando...

Solo eso. Maximo 3 segundos.

### FASE 2: BRIEFING (el cambio mas importante)

El bot tiene 3 modos segun la complejidad y ambiguedad:

Modo A: Ejecucion directa (trivial, ambiguedad baja)

Para preguntas simples. No pregunta, ejecuta, pero muestra razonamiento minimo.

Ejemplo: "Cual es la diferencia entre pgvector y Pinecone?"

Contexto detectado

- Proyecto activo: Monstruo (usa Supabase/pgvector)

- Memoria: Evaluaste Pinecone el 15 de marzo, descartado por costo

- Ruta: Perplexity (datos actuales) + Claude (analisis tecnico)

Ejecutando...

Pasa directo a Fase 3.

Modo B: Briefing + confirmacion (complejidad media-alta)

Para tareas sustanciales donde el Monstruo tiene suficiente contexto pero quiere validar el enfoque.

Ejemplo: "Disena una estrategia para lanzar una startup de IA en LATAM con $50K"

Analisis del Monstruo

Entendi esto:

Estrategia de lanzamiento para startup de IA en mercado LATAM

con capital semilla de $50K USD.

Contexto relevante de tu historial:

- Estas en Mexico, eres solopreneur tech

- Ya operas el Monstruo (infra: Railway + Supabase + APIs de IA)

- El 22 de abril exploraste monetizacion del Monstruo como SaaS

- Tu stack dominante: Python, PostgreSQL, APIs de LLMs

- Restriccion recurrente: no quieres levantar capital externo

Plan de ejecucion:

Voy a consultar 3 cerebros con roles diferentes:

- Perplexity -> Investigacion de mercado LATAM en tiempo real

- Claude -> Arquitectura de negocio y modelo financiero

- GPT -> Sintesis estrategica y plan de ejecucion

Descartados: Grok (especulativo para finanzas), DeepSeek (mejor para codigo)

Luego yo (el Monstruo) sintetizo, cruzo contradicciones

y te doy un plan unificado con mi recomendacion.

Ajusto algo antes de ejecutar?

- El enfoque es "bootstrap rentable desde mes 1"

- Si prefieres otro enfoque (growth, fundraising, etc), dime

- Hay vertical especifica? (salud, fintech, educacion, etc)

[Ejecutar asi]  [Ajustar enfoque]  [Cambiar cerebros]

Modo C: Interrogatorio (ambiguedad alta)

Para prompts vagos donde ejecutar seria desperdiciar tokens.

Ejemplo: "Ayudame con lo del proyecto"

Necesito precisar

Tienes 3 proyectos activos:

1. Monstruo -- bot de Telegram (ultima actividad: hoy)

2. API de auditorias -- concepto (ultima actividad: 5 dias)

3. Landing page -- diseno (ultima actividad: 12 dias)

Cual? Y ayudame a entender que necesitas:

- Resolver un problema tecnico?

- Tomar una decision?

- Generar contenido/codigo?

[1 Monstruo]  [2 API auditorias]  [3 Landing]

### FASE 3: ORQUESTACION (5-30 segundos)

Cambio critico: Cada cerebro recibe un prompt DIFERENTE con un ROL especifico. No es el mismo prompt para todos.

Ejemplo para la tarea de startup:

Perplexity recibe: "Rol: Scout de mercado. Busca datos REALES del mercado de IA en LATAM. Competidores, tamano de mercado, regulacion. NO des consejos genericos. Dame DATOS y NOMBRES concretos."

Claude recibe: "Rol: Arquitecto de negocios. Disena modelo de negocio y plan financiero para $50K. Restricciones: solopreneur, stack Python/Railway/Supabase, no quiere fundraising. Dame breakdown financiero con numeros reales."

GPT recibe: "Rol: Estratega ejecutivo. Vas a recibir analisis de mercado (de otro analista) y modelo financiero (de otro arquitecto). Tu trabajo: sintetizar en plan ejecutable semana a semana."

Ejecucion escalonada:

Perplexity y Claude van en paralelo (son independientes)

GPT va despues, con los resultados de los otros como input

El Monstruo genera su propia capa de sintesis soberana

Qué ve el usuario durante la ejecucion (mensaje que se edita en vivo):

Ejecutando plan multi-cerebro...

Perplexity -> Analisis de mercado LATAM (completado, 3.2s)

Claude -> Modelo financiero (completado, 5.1s)

GPT -> Sintetizando con inputs anteriores (pensando...)

Sintesis del Monstruo...

### FASE 4: ENTREGA

El resultado tiene estructura fija con estas secciones obligatorias:

RESULTADO DEL MONSTRUO

========================================

[Titulo de la tarea]

LO QUE ENCONTRE (datos reales)

----------------------------------------

[Datos de mercado, competidores, numeros reales de Perplexity]

ESTRATEGIA RECOMENDADA

----------------------------------------

[Plan del cerebro estrategico, personalizado al contexto de Alfredo]

POR QUE ESTA ESTRATEGIA Y NO OTRA

----------------------------------------

[Razonamiento: que se descarto y por que]

CONEXION CON TU HISTORIAL

----------------------------------------

[Memorias relevantes: "El 15 de marzo investigaste X, aplica aqui porque Y"]

RIESGOS ESPECIFICOS (no genericos)

----------------------------------------

[Riesgos reales basados en contexto, no "competencia" y "presupuesto"]

CONTRA-INDICADORES (pivota si ves esto)

----------------------------------------

[Senales de alarma concretas con umbrales]

========================================

PROVENIENCIA COGNITIVA:

Datos mercado: Perplexity | Estrategia: Claude | Sintesis: GPT

SIGUIENTES PASOS:

[A] Profundizar en X

[B] Financiero detallado

[C] Analisis de competencia

[D] Tu contexto cambio, redisena

Elige una letra o escribe libre.

### FASE 5: REGISTRO (invisible al usuario)

Despues de entregar el resultado:

Guardar la conversacion completa como memoria episodica en Supabase

Actualizar el perfil del usuario con nuevas preferencias detectadas

Registrar calidad: si el usuario pidio profundizar = buena senal, si abandono = mala senal

Log de gobernanza: decision_record completo

## 5. Diferenciadores concretos vs ChatGPT

## 6. Anti-patrones (prohibidos)

Ejecutar sin contexto -- Nunca mandar el prompt crudo al LLM sin enriquecerlo con memoria y perfil

Ocultar seleccion de cerebros -- Siempre mostrar que cerebro, por que, y que se descarto

Terminar conversacion -- Siempre ofrecer siguientes pasos concretos

Ignorar historial -- Siempre buscar y mostrar conexiones con interacciones previas

Respuestas genericas -- Si la respuesta aplica a "cualquier usuario", esta mal

Inventar datos -- Si no tiene datos reales, decirlo: "Estoy especulando, valida con [fuente]"

Muros de texto -- Maximo 250 palabras por seccion, botones para expandir

Lenguaje de IA -- Nunca "Como IA...", "Basado en tu consulta...", "Espero que esto te sea util"

Ser neutral -- El Monstruo tiene opiniones y las dice

Dar listas de 7 puntos -- Estructura con secciones claras, no bullet points infinitos

## 7. Ejemplo completo Before/After

### BEFORE (hoy):

Alfredo escribe: "Disena una estrategia para lanzar una startup de IA en LATAM con $50K"

Bot responde (15 segundos despues):

Resultado del Monstruo

Cerebro: GPT-5.4

Tipo: estrategia

Estrategia de Lanzamiento para Startup de IA en LATAM

1. Modelo de Negocio

- Sector: Salud

- Solucion: Plataforma SaaS de analisis predictivo

- Precio: $500/mes

2. Stack Tecnologico

- Python + TensorFlow + React + Node.js + AWS

3. Primeros 3 Clientes

- Clinicas del Valle (Mexico) [INVENTADO]

- Hospital Universitario de Montevideo [GENERICO]

- Centro Medico ABC (Colombia) [INVENTADO]

4. Timeline de 90 Dias

- Dia 1-15: Investigacion

- Dia 16-30: MVP

- Dia 31-60: Beta

- Dia 61-90: Lanzamiento

5. Riesgos

- Adopcion lenta

- Competencia

- Presupuesto limitado

Problemas: Generico, nombres inventados, stack copy-paste, riesgos obvios, cero personalizacion, cero razonamiento, cero memoria, cero interaccion.

### AFTER (nuevo diseno):

Alfredo escribe: "Disena una estrategia para lanzar una startup de IA en LATAM con $50K"

Bot responde (2 segundos):

Analisis del Monstruo

Entendi: Estrategia de lanzamiento, startup IA, LATAM, $50K.

Contexto de tu historial:

- Eres solopreneur tech en Mexico

- Stack: Python, Railway, Supabase (lo usas para el Monstruo)

- El 22 de abril exploraste monetizar el Monstruo como SaaS

- Restriccion recurrente: no quieres levantar capital externo

- Tu proyecto anterior EdTech fallo por alto CAC

Plan: Consultar 3 cerebros con roles diferentes:

- Perplexity -> Datos reales del mercado IA en LATAM

- Claude -> Modelo financiero para solopreneur con $50K

- GPT -> Sintesis estrategica con inputs de los otros

Descartados: Grok (especulativo para finanzas), DeepSeek (mejor para codigo)

Enfoque por defecto: bootstrap rentable desde mes 1.

Ajusto algo?

[Ejecutar asi]  [Cambiar enfoque]  [Cambiar cerebros]

Alfredo presiona [Ejecutar asi]

Bot muestra progreso (editando el mismo mensaje):

Ejecutando plan multi-cerebro...

Perplexity -> Datos de mercado LATAM (completado)

Claude -> Modelo financiero (completado)

GPT -> Sintetizando con inputs... (pensando)

Sintesis del Monstruo...

Bot entrega resultado (30 segundos despues):

ESTRATEGIA: Startup IA en Mexico -- $50K Bootstrap

MERCADO REAL (via Perplexity):

El mercado de IA en Mexico crecio 28% en 2025. Competidores

directos en tu nicho: Truora (verificacion), Prometeo (banking).

Tu ventaja: ya tienes infra de orquestacion multi-LLM funcionando.

MODELO FINANCIERO (via Claude):

Con $50K y sin equipo:

- $30K: Pista de aterrizaje para ti (12-15 meses en Mexico)

- $10K: Presupuesto API (OpenRouter/Anthropic/OpenAI)

- $10K: Legal + fondo de emergencia

NO gastes en marketing pagado. Tu canal es distribucion B2B.

ESTRATEGIA (sintesis del Monstruo):

No hagas otro SaaS generico. Monetiza lo que ya tienes:

el Monstruo como plataforma de orquestacion de IAs.

Tu primer cliente: tu mismo. Tu segundo: otros solopreneurs.

POR QUE ESTO Y NO OTRA COSA:

Tu proyecto EdTech fallo por alto CAC. Esta estrategia

tiene CAC cercano a $0 porque tu canal es producto propio.

RIESGO REAL:

Tu impulso de "construir en publico" te ha saboteado antes.

Esta estrategia requiere 3 meses de construccion silenciosa.

PROVENIENCIA: Mercado: Perplexity | Finanzas: Claude | Sintesis: GPT

SIGUIENTES PASOS:

[A] Detallar plan financiero mes a mes

[B] Analizar competidores directos en Mexico

[C] Disenar MVP minimo del Monstruo como producto

[D] Contexto cambio, redisenar

## 8. Implementacion tecnica (resumen para el desarrollador)

Archivos a modificar: bot.py (unico archivo)

Funciones nuevas necesarias:

intake() -- Clasificacion + busqueda de memoria + deteccion de ambiguedad

build_briefing() -- Genera el mensaje de briefing segun modo A/B/C

orchestrate_multi_brain() -- Ejecuta cerebros con prompts diferenciados y escalonados

sovereign_synthesis() -- Capa de sintesis propia del Monstruo que cruza resultados

deliver_result() -- Formatea con estructura fija + proveniencia + siguientes pasos

register_episode() -- Guarda en memoria + actualiza perfil + log de gobernanza

Funciones a eliminar:

classify_task() (reemplazada por intake())

generate_plan() (reemplazada por build_briefing())

execute_task() (reemplazada por orchestrate_multi_brain() + sovereign_synthesis())

Cambios en Supabase:

Tabla user_profiles: preferencias, restricciones, stack, proyectos activos

Tabla active_projects: nombre, estado, ultima actividad

Tabla episode_quality: tracking de si el usuario profundizo o abandono

Restricciones de Telegram:

Usar edit_message_text para actualizar progreso en vivo (no inundar de mensajes)

Maximo ~4000 chars por mensaje, usar botones para expandir secciones

Inline keyboards para todas las opciones de interaccion

## 9. Prioridad de implementacion

Sprint 1 (inmediato): Fase 2 (Briefing) -- Es el cambio que mas impacto tiene. Mostrar contexto + razonamiento + opciones antes de ejecutar.

Sprint 2: Fase 3 (Orquestacion multi-cerebro) -- Prompts diferenciados por cerebro + ejecucion escalonada.

Sprint 3: Fase 4 (Entrega estructurada) -- Formato fijo con proveniencia + siguientes pasos.

Sprint 4: Fase 1 (Intake con memoria) -- Busqueda semantica real en Supabase + perfil de usuario.

Sprint 5: Fase 5 (Registro y aprendizaje) -- Tracking de calidad + actualizacion de perfil.

## 10. Consenso y divergencias entre los 6 sabios

Consenso unanime (6/6):

El bot actual es un proxy sin valor agregado

Mostrar razonamiento es el cambio mas importante

Multi-cerebro con roles diferenciados es la ventaja real

Memoria persistente es lo que hace imposible replicar con ChatGPT

Siempre ofrecer siguientes pasos, nunca terminar la conversacion

Divergencias interesantes:

Grok quiere personalidad agresiva ("socio psicoata cabrón") vs Gemini prefiere tono profesional con "friccion positiva"

Perplexity enfatiza preguntar ANTES de ejecutar vs Claude permite ejecucion directa en tareas triviales

DeepSeek propone barra de progreso visual vs Gemini propone edicion de mensaje en vivo

Resolucion: Adoptamos el modelo de 3 modos de Claude (A/B/C segun complejidad), la personalidad directa-pero-profesional de Gemini, y el progreso en vivo de ambos.



| Lo que la doctrina promete | Lo que el bot entrega hoy |

| Cognición soberana | Proxy de APIs |

| Memoria persistente | Cada conversación empieza de cero |

| Razonamiento visible | "Cerebro: GPT-5.4" y nada más |

| Maduración continua | Misma calidad en interacción 1 e interacción 500 |

| Gobernanza auditable | Logs técnicos, no decisiones explicadas |





| Dimension | ChatGPT | El Monstruo |

| Razonamiento | "Aqui esta tu plan" | "Seleccione Claude porque X, descarte Grok porque Y" |

| Contexto | Sesion aislada | Conecta con proyectos previos del usuario |

| Validacion | No pregunta | Captura ambiguedad antes de ejecutar |

| Multi-cerebro | Un solo modelo | 3 cerebros con roles diferentes + sintesis |

| Alternativas | Fin de conversacion | Ofrece 4-5 opciones para profundizar |

| Critica | Siempre afirmativo | Senala contra-indicadores y riesgos reales |

| Memoria | Volatil (ventana de contexto) | Persistente (embeddings + metadata) |

| Personalidad | Neutral, corporate | Directo, con opiniones, conoce al usuario |

