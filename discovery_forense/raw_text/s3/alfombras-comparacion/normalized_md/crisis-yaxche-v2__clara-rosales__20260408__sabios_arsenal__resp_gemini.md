# Respuesta de Gemini 3.1 Pro
**Modelo:** gemini-3.1-pro-preview  
**Tiempo:** 50.8s  

Bienvenido a la Sala de Guerra de la Operación YAXCHÉ, Ronda 2. 

Como consultor en manejo de crisis, te lo digo claro: en la política mexicana, la diferencia entre un escándalo letal y una crisis neutralizada es la velocidad y la asimetría de la información. Ahora sí tenemos el arsenal completo desplegado. 

**RESTRICCIÓN CERO DE FUEGO AUTOMÁTICO ACEPTADA Y BLINDADA.** Bajo ninguna circunstancia conectaremos canales de salida (escritura) a redes sociales. Un script automatizado publicando en crisis es un suicidio político. Todo el social media será nuestra red de sonar pasivo (Solo Lectura). El fuego de respuesta será milimétrico, humano en su emisión final, pero construido con esteroides algorítmicos.

Aquí tienes la arquitectura táctica y accionable para rescatar a la Diputada Clara Rosales.

---

### 1. REDISEÑO DEL SISTEMA CENTINELA (La Máquina de Guerra)

Hemos orquestado un *pipeline* de 5 capas integrando cada pieza del arsenal mediante **Zapier MCP** y **Cloudflare Workers** como pegamento lógico.

*   **Capa 1: Radar Pasivo e Inteligencia (READ-ONLY)**
    *   **BrandMentions + Mentionlytics:** El "Trigger". Escuchan la web 24/7. Si detectan un pico anómalo de menciones negativas sobre "Clara Rosales" o "Kanasín", disparan un Webhook.
    *   **Apify Scrapers + Manus APIs:** Al recibir el Webhook, Apify extrae históricamente las páginas de Facebook/TikTok atacantes. Las APIs de Manus extraen la metadata de X/Twitter y Reddit en tiempo real.
    *   **SecurityTrails:** Cruza los dominios de las noticias falsas para extraer registros WHOIS/DNS y descubrir quién financia el portal (ej. conexiones con el PAN u opositores locales).
*   **Capa 2: Procesamiento y Triaje (Los 6 Sabios + Replicate)**
    *   **Replicate:** Recibe miles de comentarios scrapeados y corre modelos rápidos de ML para clasificarlos por sentimiento y toxicidad en segundos.
    *   Los **6 Sabios** ingieren la data estructurada para ejecutar análisis especializado (ver sección 2).
*   **Capa 3: Bóveda e Infraestructura (El Backend)**
    *   **AWS S3:** Recibe automáticamente (vía *manus-upload-file*) todas las evidencias en video, audio o capturas. Cadena de custodia garantizada.
    *   **Supabase:** Actúa como el cerebro central. Su base de datos PostgreSQL almacena el mapa de actores hostiles, y *Realtime* actualiza el dashboard de crisis al segundo.
    *   **Vercel + Cloudflare:** Alojan y protegen una *Landing Page de Transparencia* (ej. "LaVerdadDeClara.mx") donde se suben los desmentidos oficiales.
*   **Capa 4: Coordinación Operativa (War Room)**
    *   **Notion MCP:** El tablero maestro de crisis. Todo el flujo de Supabase se refleja aquí para que el equipo humano lo lea.
    *   **Asana MCP:** Genera tareas automáticas ("Revisar borrador de prensa", "Contactar a medio X").
    *   **Gmail / Outlook / Calendar MCPs:** Envío de comunicados masivos a la prensa (BCC) y agendamiento urgente de ruedas de prensa.
*   **Capa 5: Factoría de Contra-Narrativa (Assets off-line)**
    *   **Together AI (FLUX) + ElevenLabs + HeyGen + Novita:** Si necesitamos explicar la trama de corrupción que nos ataca, FLUX genera infografías, ElevenLabs da voz a un video explicativo en *off*, y Novita/HeyGen renderizan bocetos de video. **Todo esto se exporta a GDrive/Dropbox para revisión humana** y uso exclusivo en la Landing Page o proyecciones en ruedas de prensa. NUNCA posteo en redes.

---

### 2. ROL OPERATIVO DE CADA SABIO (Agentes Tácticos)

No son chatbots, son micro-departamentos trabajando en paralelo:

1.  **GPT-5.4 (El Orquestador / Director de Comunicación):**
    *   **Rol:** Redactor en Jefe y Mando Central.
    *   **Acción:** Ingiere el reporte unificado de crisis. Redacta los *Talking Points* para Clara Rosales, genera los comunicados de prensa institucionales (vía Google Docs MCP) y redacta los correos para enviar a directores de medios (vía Gmail MCP).
2.  **Claude Opus 4.6 (El Despacho Jurídico / Auditor):**
    *   **Rol:** Control de daños legales e institucionales.
    *   **Acción:** Revisa cada comunicado generado por GPT contra las leyes de difamación y derecho de réplica en México. Analiza PDFs filtrados o amparos (usando *manus-md-to-pdf*) para encontrar lagunas en los ataques de la oposición.
3.  **Gemini 3.1 Pro (El Analista Forense Multimodal):**
    *   **Rol:** Cazador de Deepfakes y manipulaciones visuales.
    *   **Acción:** Toma los videos virales de TikTok/FB que extrae Apify (descargados de AWS S3), los procesa *frame por frame* para detectar si el audio fue clonado o si la imagen está sacada de contexto. Extrae placas de vehículos o rostros en fotos difamatorias.
4.  **Grok 4.20 (El Estratega de Guerra Sucia / X-Twitter):**
    *   **Rol:** Entender el subtexto y la cultura digital del ataque.
    *   **Acción:** Analiza la data extraída de la API de X por Manus. Detecta "granjas de bots" por patrones de retweets exactos, identifica el "humor" o memes que están usando contra Clara, y diseña tácticas laterales (ej. "¿Cómo hacemos que el ataque se vuelva en contra de quien lo financia?").
5.  **DeepSeek R1 (El Analista de Inteligencia de Señales):**
    *   **Rol:** Trazar la telaraña financiera/política.
    *   **Acción:** Ingiere los datos crudos de SecurityTrails (IPs, dominios), bases de datos de contratos públicos de Yucatán, y reportes de clustering de noticias (Apify). Usa cadenas lógicas masivas y *manus-render-diagram* para mapear: *"El portal A, la cuenta B y el periodista C reciben dinero del mismo nodo en el Ayuntamiento opositor"*.
6.  **Perplexity Sonar Pro (El Verificador de Campo en Tiempo Real):**
    *   **Rol:** Equipo de reacción rápida contra Fake News.
    *   **Acción:** Si un troll dice *"Clara Rosales votó a favor del impuesto X"*, Perplexity escanea las gacetas parlamentarias, periódicos locales de los últimos 10 años, y entrega en 3 segundos un reporte con **citas verificadas** demostrando la mentira, listo para enviar a prensa.

---

### 3. APIFY + BRANDMENTIONS: EL RADAR DE GUERRA 360°

Así funciona nuestro ecosistema de inteligencia ininterrumpida:

1.  **Detección Inmediata:** BrandMentions actúa como el sismógrafo. Si la palabra "Clara" + "Corrupción" sube un 15% en 10 minutos, dispara una alerta.
2.  **Focalización:** Esa alerta activa a *Political News Event Monitoring* (Apify) para agrupar todas las noticias formales que han replicado la nota, mapeando qué medios tradicionales ya compraron el ataque.
3.  **Extracción Quirúrgica (Scraping):** Simultáneamente, el *Facebook/TikTok/Instagram Scraper* de Apify hace un barrido del "paciente cero" (la página que inició el rumor), bajando todos los comentarios.
4.  **Sandbox API (Manus):** Usamos las APIs de Reddit, YouTube y Twitter no para raspar masivamente, sino para rastrear la propagación en nichos de alto impacto periodístico (quién lo está debatiendo en foros o qué YouTubers políticos están preparando videos).
5.  **Cruce de Datos:** Perplexity cruza en tiempo real los nombres de usuario más ruidosos con el Padrón de Proveedores de Yucatán o nóminas públicas para desenmascarar si son bots pagados o funcionarios del PAN/PRI con cuentas troll.

---

### 4. SUPABASE + CLOUDFLARE + AWS: LA INFRAESTRUCTURA DE GUERRA

No dependemos de servidores compartidos ni Excel. Operamos como grado militar:

*   **Supabase (El Tablero de Mando):** 
    *   Es el backend de nuestro *War Room*. Recibe a través de Edge Functions (Webhooks) toda la data de BrandMentions, Apify y Replicate.
    *   Su base de datos PostgreSQL ordena: *ID del Ataque, Plataforma, Nivel de Riesgo, Actor Hostil*.
    *   Usando **Supabase MCP**, el equipo y los IAs consultan en tiempo real este dashboard sin salir de Notion.
*   **AWS S3 (El Búnker de Evidencia):**
    *   Todo video difamatorio en TikTok o post en FB se borra cuando expones al atacante. S3 es nuestro notario digital.
    *   Cada vez que Apify raspa un video, *manus-upload-file* lo sube a S3. Se genera un hash inmutable. Si vamos a denunciar a una página por daño moral ante autoridades electorales/civiles en México, S3 nos da la prueba legal (Cadena de custodia).
*   **Cloudflare (El Escudo Activo):**
    *   Al desplegar nuestra landing de defensa (*Vercel MCP*), la envolvemos en Cloudflare.
    *   **DDoS Protection:** Impide que los opositores tiren la página de transparencia.
    *   **Cloudflare Workers:** Actúan como contrainteligencia. Si detectamos que IPs del palacio de gobierno opositor están visitando intensamente nuestra página buscando errores, el Worker registra esas IPs. Podemos usar ese dato para decir: *"Sabemos que nos están vigilando desde las oficinas del partido X"*.

---

### 5. OPENROUTER: EL MULTIPLICADOR (Fuerza de Reserva)

Los 6 Sabios son la élite, pero OpenRouter nos da acceso a "mercenarios" especializados para tareas específicas de alta demanda que no ameritan gastar los tokens de los modelos principales:

1.  **Kimi K2.5 (La Aspiradora de Contexto):** Si la crisis estalla porque nos filtraron un expediente de 3,000 páginas de una licitación en Kanasín, Kimi tiene una ventana de contexto titánica y estable. Puede ingerir el expediente COMPLETO de un golpe y encontrar dónde alteraron las cifras los atacantes.
2.  **Llama 3.1 (405B / 70B) vía OpenRouter:** Procesamiento masivo de bajo costo. Cuando Apify nos trae 100,000 comentarios de Facebook en una hora, enviamos el dataset a Llama 3 para que haga el análisis de sentimiento a granel. Liberamos a GPT-5.4 y Claude de esa tarea repetitiva para que se enfoquen en estrategia.
3.  **Mistral Large 2:** Especialista en matices lingüísticos. Si necesitamos regionalizar un discurso con jerga política específica de la Península de Yucatán sin que suene artificial ("robótico"), Mistral suele tener un ajuste fino excelente para matices latinoamericanos.

**Conclusión Operativa:**
Tenemos una máquina de succión de datos masiva, almacenamiento inmutable, análisis por inteligencias especializadas, y una capa de coordinación que entrega directrices pulidas a tu equipo humano. Clara Rosales no va a publicar un solo tuit automático. Cuando ella hable ante las cámaras, tendrá en sus manos el mapa financiero de sus atacantes, la refutación legal de sus mentiras, y el análisis frame-por-frame de sus manipulaciones. 

**Orden táctica: Autorizar despliegue de Vercel/Cloudflare e inicializar Webhooks de Supabase.**