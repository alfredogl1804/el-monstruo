# Respuesta de GPT-5.4
**Modelo:** gpt-5.4  
**Tiempo:** 107.2s  

Aquí va el rediseño serio, completo y operativo de la **Operación YAXCHÉ – Ronda 2**, usando el arsenal entero bajo una regla inviolable:

> **CERO automatización para publicar en redes.**
> Todo lo conectado a redes sociales se usa **solo para monitoreo, lectura, scraping, análisis, inteligencia y preservación de evidencia**.

---

# I. VISIÓN GENERAL: SISTEMA CENTINELA 360°

La arquitectura debe funcionar como un **sistema de defensa, inteligencia, análisis, decisión y respuesta documental**, no como un sistema de “marketing digital”.

## Objetivo operativo
Construir un **Centro de Mando de Crisis** que haga 5 cosas en paralelo:

1. **Detectar** menciones, ataques, narrativas y coordinaciones.
2. **Clasificar** riesgo, origen, alcance y probabilidad de escalamiento.
3. **Producir inteligencia accionable** para decisiones políticas, legales y mediáticas.
4. **Coordinar** al equipo interno con trazabilidad.
5. **Generar materiales de respuesta** para prensa, vocería, legal y territorio.

---

# II. ARQUITECTURA MAESTRA POR CAPAS

---

## CAPA 1. INGESTA E INTELIGENCIA DE FUENTES

Esta capa capta todo lo que se dice, publica, comparte o amplifica sobre Clara Rosales y su crisis.

### 1) Social listening continuo
#### Herramientas:
- **BrandMentions**
- **Mentionlytics**

### Función:
- Monitoreo en tiempo real de menciones de:
  - Clara Rosales
  - variaciones del nombre
  - hashtags vinculados
  - nombres de aliados, adversarios, operadores y medios
  - términos de escándalo, corrupción, nepotismo, desvío, audio filtrado, etc.
- Alertas por:
  - pico de volumen
  - cambio brusco de sentimiento
  - aparición de influencer o medio nuevo
  - crecimiento anómalo de narrativa hostil

### Uso conjunto:
- **BrandMentions** como radar primario por cobertura y sentimiento.
- **Mentionlytics** como segundo radar para validación cruzada y detección de huecos.

---

### 2) Scraping masivo y preservación de evidencia
#### Herramientas:
- **Apify Facebook Pages Scraper**
- **Apify Instagram Scraper**
- **Apify All-in-One Social Media Scraper**
- **Apify Political News Event Monitoring**
- **Apify TikTok Scraper**

### Función:
- Extraer posts, captions, comentarios, timestamps, URLs, engagement, hashtags, perfiles propagadores.
- Hacer snapshots periódicos de contenido que pueda borrarse.
- Detectar clusters de ataque por plataforma.
- Crear histórico para análisis temporal y evidencia legal.

### Casos concretos:
- Scraping de páginas como “Noticias Al Punto”, cuentas locales, páginas de memes políticos, perfiles de operadores.
- Extracción de comentarios repetidos o plantillas.
- Detección de copy-paste masivo de narrativa.

---

### 3) APIs sandbox y monitoreo por plataforma
#### Herramientas Manus:
- **Twitter API (sandbox)**
- **TikTok API (sandbox)**
- **YouTube API (sandbox)**
- **Reddit API (sandbox)**

### Función:
- Complementar scraping con lectura estructurada por plataforma.
- Obtener metadatos de cuentas, publicaciones, frecuencia, engagement, redes de interacción.
- Identificar:
  - cuentas recién creadas
  - cuentas coordinadas
  - videos con aceleración anómala
  - canales que estén editorializando la crisis

### Valor:
Apify da amplitud; las APIs de Manus dan estructura y lectura más limpia.

---

### 4) Web abierta, noticias y fact-checking
#### Herramientas:
- **Perplexity Sonar**
- **Apify Political News Event Monitoring**

### Función:
- Buscar cobertura externa en tiempo real.
- Confirmar si la narrativa ya brincó de redes a portales, blogs, radio, prensa o columnas.
- Generar fichas con:
  - qué medio publicó
  - cuándo
  - qué afirmó
  - qué citó
  - qué omite
  - qué riesgo legal presenta

### Resultado:
Mapa diario de “qué ya salió de la burbuja social y entró al ecosistema noticioso”.

---

### 5) Inteligencia de infraestructura y actores
#### Herramientas:
- **SecurityTrails**
- **Cloudflare logs/analytics**
- **WHOIS / DNS intelligence**

### Función:
- Investigar dominios de sitios que impulsan ataques.
- Ver relaciones entre medios “independientes” y redes de dominios.
- Detectar:
  - dueños técnicos
  - patrones de hosting
  - dominios espejo
  - infraestructura vinculada entre medios o páginas de ataque

### Uso:
No para “hack back”, sino para **atribución técnica y contexto estratégico/legal**.

---

## CAPA 2. PROCESAMIENTO Y NORMALIZACIÓN

Todo lo captado debe entrar a un backend unificado.

### Herramienta eje:
- **Supabase**

### Flujo:
1. Apify y BrandMentions envían resultados vía API/webhook.
2. Zapier o Edge Functions de Supabase normalizan el dato.
3. Se guardan en PostgreSQL con esquema único.
4. Archivos pesados, capturas, video y audio van a **AWS S3**.
5. Supabase guarda el índice, metadata, scoring y referencias.

### Tablas mínimas en Supabase
- `mentions`
- `posts_scraped`
- `accounts`
- `media_assets`
- `narratives`
- `incidents`
- `risk_scores`
- `actor_networks`
- `legal_flags`
- `press_inquiries`
- `tasks`
- `briefings`
- `approvals`
- `evidence_chain`

### Campos clave
- fuente
- plataforma
- URL
- autor
- fecha
- texto
- sentimiento
- narrativa detectada
- riesgo reputacional
- riesgo legal
- riesgo territorial/electoral
- nivel de coordinación sospechada
- evidencia preservada sí/no
- respuesta recomendada

---

## CAPA 3. ANÁLISIS OPERATIVO — LOS 6 SABIOS COMO AGENTES

Aquí no son “opinadores”; son **workers especializados** dentro del flujo.

---

### 1) GPT-5.4 — ORQUESTADOR CENTRAL
## Rol operativo:
- Director de orquestación analítica.
- Resume cada ola de información.
- Prioriza incidentes.
- Redacta borradores de:
  - holding statements
  - Q&A de vocería
  - talking points
  - cronologías
  - reportes ejecutivos
- Convierte el ruido técnico en instrucciones operativas para humanos.

## Inputs:
- Data consolidada de Supabase
- Alertas de BrandMentions
- scraping de Apify
- análisis de otros sabios

## Outputs:
- “Brief Ejecutivo 7 AM / 1 PM / 8 PM”
- “Top 5 riesgos del día”
- “Matriz de respuesta inmediata”
- borrador de comunicado para prensa
- minuta de guerra

---

### 2) Claude Opus 4.6 — CÉLULA LEGAL Y DESTRUCTORA DE NARRATIVA
## Rol operativo:
- Analiza si una acusación tiene riesgo jurídico real.
- Revisa documentos, contratos, capturas, notas, derechos de réplica.
- Identifica difamación, imputaciones falsas, vacíos probatorios.
- Hace crítica lógica de la narrativa enemiga.

## Tareas concretas:
- marcar frases con exposición legal
- preparar líneas de defensa documental
- revisar comunicados antes de enviarlos
- redactar fichas de “esto sí se puede afirmar / esto no”
- preparar paquete para abogados y eventual derecho de réplica

## Output:
- memo legal por incidente
- “riesgo jurídico alto/medio/bajo”
- check de compliance del mensaje

---

### 3) Gemini 3.1 Pro — LABORATORIO MULTIMODAL
## Rol operativo:
- Analiza imágenes, videos, capturas, flyers, memes, audios con soporte visual.
- Detecta edición engañosa, recorte tendencioso, inconsistencias visuales.
- Compara versiones de un video o screenshot.

## Tareas:
- analizar videos virales de TikTok/YouTube
- leer screenshots de chats o supuestos documentos filtrados
- extraer texto visual y contexto
- señalar manipulación narrativa basada en imagen

## Output:
- ficha multimodal
- “video manipulado / contexto recortado / no concluyente”
- evidencias visuales para prensa o legal

---

### 4) Grok 4.20 — RADAR DE X/TWITTER Y CONTRAINTELIGENCIA NARRATIVA
## Rol operativo:
- Especialista en dinámica de conversación agresiva y viral en X.
- Detecta chistes, sarcasmo, subtexto, frames hostiles.
- Encuentra ángulos no obvios de ataque o escalamiento.

## Tareas:
- mapear cómo se está cocinando una narrativa antes de explotar
- detectar cuentas bisagra e influenciadores hostiles
- identificar oportunidades de neutralización discursiva en medios, no en redes automáticas
- proponer líneas de contraste narrativo para voceros humanos

## Output:
- mapa de frames hostiles
- lista de cuentas nodales
- escenarios de escalamiento de 6, 12 y 24 horas

---

### 5) DeepSeek R1 — DETECTOR DE PATRONES Y COORDINACIÓN
## Rol operativo:
- Analiza secuencias, patrones repetitivos, timings y estructuras.
- Sirve para identificar campañas coordinadas.

## Tareas:
- comparar oleadas de publicaciones
- detectar copy-paste semántico
- encontrar correlación entre páginas, cuentas y horarios
- modelar si el ataque parece orgánico, semiorgánico o inducido

## Output:
- score de coordinación
- patrón temporal
- hipótesis de operación
- priorización de actor-red

---

### 6) Perplexity Sonar — OSINT Y VERIFICACIÓN EXTERNA
## Rol operativo:
- Motor de búsqueda viva con citas.
- Verifica hechos públicos y contexto noticioso.
- Busca antecedentes de medios, personajes, casos similares, expedientes públicos.

## Tareas:
- verificar si una afirmación ya fue publicada antes
- rastrear si un medio atacante tiene historial partidista
- ubicar fuentes originales
- alimentar fact packs para vocería y legal

## Output:
- dossier con fuentes citables
- línea de tiempo pública verificable
- ficha de contexto y antecedentes

---

# III. EL FLUJO AUTOMATIZADO COMPLETO DEL SISTEMA CENTINELA

---

## Fase 0. Configuración inicial
### Herramientas:
- Notion
- Asana
- Supabase
- Cloudflare
- AWS S3
- BrandMentions
- Mentionlytics
- Apify
- Gmail/Outlook
- Google Calendar
- Zapier

### Acción:
- Crear taxonomía única de crisis:
  - nombres
  - hashtags
  - actores
  - temas
  - medios
  - municipios
  - operadores
- Definir umbrales de alerta:
  - volumen
  - negatividad
  - velocidad
  - salto a medios
  - aparición de evidencia visual
- Definir tipos de incidente:
  - rumor
  - acusación
  - filtración
  - ataque coordinado
  - cobertura adversa
  - video viral
  - nota de medio
  - solicitud de prensa

---

## Fase 1. Captura
### 24/7
- BrandMentions y Mentionlytics monitorean y alertan.
- Apify scrapea cada X minutos/horas según plataforma.
- APIs de Manus consultan Twitter/TikTok/YouTube/Reddit.
- Perplexity corre búsquedas recurrentes web/news.
- SecurityTrails revisa dominios nuevos o sospechosos vinculados.

### Automatización:
- Todo entra por webhook/API a Supabase.
- Zapier enruta eventos de alto riesgo.

---

## Fase 2. Normalización y scoring
### En Supabase:
- Deduplicación
- Enriquecimiento con metadatos
- Clasificación de plataforma
- etiquetado de narrativa
- score inicial:
  - alcance
  - toxicidad
  - verosimilitud
  - riesgo jurídico
  - riesgo electoral
  - riesgo de contagio mediático

### Realtime:
- Dashboard en vivo para war room.

---

## Fase 3. Análisis especializado por sabios
### Pipeline:
1. **GPT-5.4** recibe lote priorizado y decide ruta analítica.
2. **Gemini** analiza assets visuales.
3. **Claude** revisa implicación legal y consistencia.
4. **Grok** evalúa dinámica hostil y framing.
5. **DeepSeek** analiza coordinación/patrones.
6. **Perplexity** verifica hechos y fuentes externas.
7. **GPT-5.4** recompone todo en brief final.

---

## Fase 4. Escalamiento operativo
Dependiendo del score:

### Nivel Verde
- Monitoreo
- registro
- sin acción pública

### Nivel Amarillo
- ficha de narrativa
- talking points internos
- preparar Q&A
- alertar al equipo político

### Nivel Naranja
- memo legal
- paquete de evidencia
- briefing a voceros
- agenda de reunión de crisis en Calendar
- tareas en Asana
- actualización en Notion

### Nivel Rojo
- comité de crisis inmediato
- holding statement por correo a prensa si aplica
- paquete jurídico
- dossier de evidencias en Dropbox/S3
- slides para vocería
- landing page de transparencia si conviene
- monitoreo intensivo por hora

---

# IV. APIFY + BRANDMENTIONS + PERPLEXITY + MANUS APIs = RADAR DE GUERRA

La combinación correcta no es redundante; es complementaria.

---

## 1. BrandMentions = alarma temprana
Te dice:
- “ya está subiendo”
- “quién lo impulsa”
- “cómo viene el sentimiento”
- “qué influencers aparecen”

Es el sensor de humo.

---

## 2. Mentionlytics = segunda capa de escucha
Te confirma o contradice:
- si la señal es robusta
- si hay fuentes que BrandMentions no tomó
- si el sentimiento cambia en otra audiencia

Es el segundo radar.

---

## 3. Apify = excavadora forense
Te baja:
- posts
- comentarios
- textos
- hashtags
- métricas
- histórico
- contenido borrable

Sirve para:
- evidencia
- dataset de análisis
- reconstrucción temporal

Es la caja negra del incidente.

---

## 4. Manus APIs = lectura estructurada por plataforma
Te permite:
- leer cuentas y videos con mejor estructura
- obtener metadatos útiles para análisis de actores
- vigilar X, TikTok, YouTube, Reddit donde suelen incubarse ataques

Es la capa de precisión.

---

## 5. Perplexity = validación externa
Te responde:
- ¿esto ya salió en medios?
- ¿esta acusación tiene antecedente?
- ¿qué dicen fuentes públicas?
- ¿quién citó primero a quién?

Es el verificador de contexto.

---

## Resultado conjunto: inteligencia 360°
### Ejemplo operativo
1. BrandMentions detecta subida abrupta de menciones negativas.
2. Apify scrapea cuentas, páginas y comentarios asociados.
3. Manus Twitter/TikTok/YouTube identifica nodos y videos acelerados.
4. DeepSeek detecta copy-paste coordinado.
5. Perplexity confirma que un portal local levantó la narrativa.
6. Claude dice si hay imputación accionable legalmente.
7. GPT produce brief ejecutivo y propuesta de respuesta.
8. Asana asigna tareas; Gmail prepara envío a medios; Calendar convoca comité.

---

# V. SUPABASE + CLOUDFLARE + AWS = INFRAESTRUCTURA DE GUERRA

---

## A. SUPABASE = NÚCLEO OPERATIVO

### Funciones:
- Base de datos PostgreSQL central
- Realtime dashboard
- auth por roles
- Edge Functions para automatización
- API interna del sistema
- almacenamiento de metadatos
- auditoría de acciones

### Qué vive en Supabase:
- menciones
- incidentes
- narrativas
- tareas ligadas a incidentes
- decisiones
- estatus legal
- rutas de aprobación
- timeline de crisis

### Dashboard sugerido:
#### Vista 1: Resumen ejecutivo
- menciones últimas 24h
- sentimiento
- top narrativas
- top amplificadores
- incidentes por nivel

#### Vista 2: Mapa de narrativas
- narrativa
- volumen
- velocidad
- origen
- evidencia
- estatus de respuesta

#### Vista 3: Red de actores
- medios
- páginas
- influencers
- cuentas sospechosas
- conexiones

#### Vista 4: Legal
- incidentes con riesgo jurídico
- status de revisión
- evidencias resguardadas

#### Vista 5: Prensa
- preguntas recibidas
- medio
- deadline
- respuesta aprobada o pendiente

---

## B. AWS S3 = BÓVEDA DE EVIDENCIA

### Uso:
- guardar:
  - videos
  - audios
  - capturas
  - PDFs
  - documentos legales
  - exportaciones de scraping
  - versiones de reportes

### Buenas prácticas:
- bucket por caso/incidente
- versionado activado
- políticas IAM estrictas
- checksum/hash para cadena de custodia
- carpetas:
  - `/raw/`
  - `/processed/`
  - `/legal/`
  - `/press/`
  - `/briefings/`

### Clave:
Todo asset sensible debe guardar:
- fecha de captura
- fuente
- URL original
- método de obtención
- hash
- responsable de carga

---

## C. CLOUDFLARE = ESCUDO Y CAPA DE ENTREGA

### Uso 1: Protección de landing page
Si se crea una página de transparencia o repositorio documental:
- WAF
- rate limiting
- bot protection
- TLS
- firewall rules

### Uso 2: Workers
- enrutamiento ligero de webhooks
- preprocesamiento de eventos
- validación de firmas
- cache de consultas públicas no sensibles

### Uso 3: DNS/observabilidad
- controlar dominios de crisis
- monitorear tráfico a landing page
- detectar picos o intentos de saturación

### Uso 4: Zero Trust
- acceso restringido al dashboard interno
- segmentación por roles

---

## D. VERCEL MCP = FRONTEND RÁPIDO
### Uso:
- desplegar landing page de transparencia
- micrositio de documentos
- sala de prensa digital
- repositorio de comunicados y PDF descargables

### Importante:
No es para publicar a redes; es para **presentar información oficial en web propia**.

---

# VI. CAPA DE COORDINACIÓN: WAR ROOM REAL

---

## 1. Notion MCP = cuartel general
### Espacios:
- timeline de crisis
- biblioteca de narrativas
- perfil de actores
- matriz de riesgos
- repositorio de FAQs
- playbooks
- aprobaciones
- bitácora ejecutiva

### Útil para:
- que todo el equipo vea la misma verdad operacional

---

## 2. Asana MCP = ejecución
### Proyectos sugeridos:
- Monitoreo y análisis
- Legal
- Prensa
- Territorio
- Documentación
- Vocería

### Tareas automáticas:
- “Validar video viral X”
- “Preparar ficha legal de nota Y”
- “Llamar a periodista Z”
- “Armar Q&A para rueda”
- “Subir evidencia a S3”
- “Actualizar brief 8 PM”

---

## 3. Gmail MCP + Outlook MCP = distribución formal
### Usos:
- envío de comunicados a medios
- respuestas a periodistas
- envío de derecho de réplica
- convocatorias a rueda de prensa
- circulación de briefs internos

### Regla:
Comunicación formal por correo, no por automatización social.

---

## 4. Google Calendar MCP = disciplina temporal
### Calendarios:
- comité de crisis
- cortes informativos
- entrevistas
- deadlines de prensa
- revisiones legales
- comparecencias

---

## 5. Google Workspace
### Uso:
- Docs: comunicados, Q&A, argumentarios
- Sheets: tracking de medios, dashboard espejo, matriz de actores
- Slides: ruedas de prensa, briefings al equipo
- Drive si aplica dentro de Workspace

---

## 6. Dropbox
### Uso:
- compartir paquetes pesados con abogados, aliados o medios seleccionados
- carpetas seguras de documentos

---

## 7. GitHub
### Uso no obvio pero muy útil:
- versionado de comunicados
- control de cambios de argumentarios
- trazabilidad de quién editó qué
- repositorio privado de plantillas y playbooks

---

# VII. CAPA DE PRODUCCIÓN DE MATERIALES

Ojo: esto es **para uso interno, prensa, web propia, vocería y documentación**, no para autopublicación en redes.

---

## 1. HeyGen
### Uso permitido y útil:
- simulaciones internas de vocería
- previsualización de mensaje
- prueba de tono antes de grabación real
- borradores de videos explicativos para revisión interna

No se recomienda como pieza final pública si compromete autenticidad política.

---

## 2. ElevenLabs
### Uso:
- narración para cápsulas explicativas
- audio para spots de circulación interna o revisión
- apoyo para versiones de accesibilidad
- voiceover para materiales informativos en web

---

## 3. Together AI (FLUX)
### Uso:
- infografías internas
- visuales para presentaciones a prensa
- esquemas explicativos
- fichas visuales del caso

---

## 4. Novita AI
### Uso:
- prototipos de video explicativo
- maquetas narrativas para revisar estructura audiovisual

---

## 5. manus-export-slides / manus-md-to-pdf
### Uso:
- convertir reportes a PDF profesional
- exportar slides para ruedas de prensa
- empaquetar briefing ejecutivo rápido

---

## 6. manus-render-diagram
### Uso:
- diagramas de red:
  - PAN–Kanasín–Koyoc
  - red de medios
  - secuencia de propagación
  - vínculos entre actores

Esto es oro para briefings internos y legales.

---

## 7. manus-speech-to-text / manus-analyze-video
### Uso:
- transcribir entrevistas, lives, audios filtrados, videos de ataque
- extraer citas exactas
- comparar lo dicho con lo reportado
- detectar manipulación audiovisual

---

# VIII. OPENROUTER: EL MULTIPLICADOR

OpenRouter no sustituye a los 6 sabios; los **extiende** para tareas puntuales.

## Modelos que sí aportarían valor

### 1. Kimi K2.5
#### Valor:
- contexto largo
- síntesis documental extensa
- consolidación de expedientes grandes
- comparación de múltiples documentos y notas

#### Uso:
- consolidar expediente completo del caso
- resumir semanas de crisis en un solo memo
- comparar 50 notas/50 posts y encontrar divergencias

---

### 2. Modelos rápidos/baratos para triage masivo
Si OpenRouter da acceso a modelos económicos de alta velocidad:
#### Uso:
- clasificación inicial de miles de comentarios/posteos
- detección preliminar de narrativa
- etiquetado antes de pasar a sabios premium

Esto baja costo y acelera tiempo de reacción.

---

### 3. Modelos especializados en coding/data
#### Uso:
- ayudar a construir queries SQL para Supabase
- generar parsers
- preparar scripts de limpieza de datos
- optimizar pipelines de scraping y scoring

---

### 4. Modelos multilingües o regionales
#### Uso:
- detectar variaciones idiomáticas locales
- entender ironía regional o expresiones de Yucatán/México
- analizar mezcla de español coloquial, memes y anglicismos

---

### 5. Modelos para extracción estructurada
#### Uso:
- convertir texto caótico en JSON:
  - actor
  - acusación
  - prueba citada
  - tono
  - llamado a acción
  - riesgo

---

## Estrategia concreta con OpenRouter
- **Tier 1:** modelo barato/rápido clasifica.
- **Tier 2:** sabio especializado profundiza.
- **Tier 3:** GPT-5.4 integra y redacta.
- **Tier 4:** Claude valida legal.
  
Así no gastas a los sabios premium en tareas triviales.

---

# IX. CADENA DE EJECUCIÓN AUTOMATIZADA COMPLETA

Aquí va el flujo integrado extremo a extremo.

---

## Trigger A: nueva mención crítica detectada
1. BrandMentions detecta mención negativa relevante.
2. Zapier recibe alerta.
3. Zapier dispara:
   - inserción en Supabase
   - consulta complementaria a Apify
   - búsqueda relacionada en Perplexity
4. Si hay video o imagen:
   - asset a S3
   - Gemini + manus-analyze-video
5. Si hay cuenta sospechosa:
   - Manus Twitter/TikTok/YouTube API
   - SecurityTrails si hay dominio adjunto
6. DeepSeek calcula coordinación.
7. Claude evalúa riesgo legal.
8. Grok analiza framing y posibilidad de escalamiento.
9. GPT-5.4 genera brief.
10. Asana crea tareas.
11. Notion actualiza incidente.
12. Gmail/Outlook prepara respuesta formal si se aprueba.
13. Calendar agenda comité si score > umbral.

---

## Trigger B: video viral
1. TikTok Scraper + TikTok API detectan crecimiento.
2. Video a S3.
3. manus-speech-to-text transcribe.
4. Gemini revisa imagen/edición.
5. GPT resume contenido.
6. Grok evalúa framing y memes asociados.
7. DeepSeek compara replicación entre cuentas.
8. Claude define riesgo legal por afirmaciones.
9. Perplexity busca si medios ya lo levantaron.
10. Se genera:
   - ficha audiovisual
   - Q&A
   - recomendación de vocería
   - paquete de evidencia

---

## Trigger C: nota de medio hostil
1. Apify Political News Event Monitoring detecta nota.
2. Perplexity ubica antecedentes y citas.
3. Claude revisa exposición legal.
4. GPT redacta:
   - resumen ejecutivo
   - derecho de réplica borrador
   - puntos para llamada con editor
5. Asana asigna:
   - prensa
   - legal
   - documentación
6. Gmail/Outlook envía si se aprueba.

---

## Trigger D: ataque coordinado sospechado
1. BrandMentions reporta pico.
2. Apify extrae lote amplio.
3. DeepSeek detecta patrones.
4. Grok identifica nodos hostiles y cuentas bisagra.
5. SecurityTrails investiga dominios relacionados.
6. manus-render-diagram produce mapa de red.
7. Claude revisa si hay calumnia o campaña negra documentable.
8. GPT arma dossier ejecutivo.
9. Comité decide:
   - ignorar
   - contener por prensa
   - responder legalmente
   - activar landing page de transparencia

---

# X. REGLAS DE DECISIÓN PARA EL WAR ROOM

## Responder públicamente solo si:
- la narrativa ya saltó a medios o actores con credibilidad
- hay riesgo de fijación en agenda pública
- existe falsedad demostrable
- el silencio incrementa daño
- hay ventana clara para cortar el frame

## No responder si:
- es ruido marginal de cuentas pequeñas
- responder amplifica una narrativa débil
- no hay evidencia suficiente para desmontar
- la acusación está confinada y no escala

---

# XI. ENTREGABLES DIARIOS DEL SISTEMA

## 7:00 AM
- brief ejecutivo
- top narrativas
- top actores
- riesgos del día
- agenda crítica

## 1:00 PM
- actualización de escalamiento
- incidentes nuevos
- medios que preguntaron
- piezas listas

## 8:00 PM
- cierre del día
- efectividad de contención
- incidentes abiertos
- riesgos de madrugada/siguiente mañana

## En tiempo real
- alertas rojas por:
  - video viral
  - nota de medio
  - mención de actor nacional
  - filtración documental
  - tendencia súbita

---

# XII. REPARTO FINAL DE ROLES POR HERRAMIENTA

## Inteligencia
- BrandMentions: escucha primaria
- Mentionlytics: validación listening
- Apify: scraping forense
- Manus APIs: lectura estructurada de plataformas
- Perplexity: OSINT y contexto web
- SecurityTrails: atribución técnica

## Análisis
- GPT-5.4: orquestación y redacción
- Claude: legal
- Gemini: multimodal
- Grok: X/framing hostil
- DeepSeek: coordinación/patrones
- Perplexity: validación externa

## Infraestructura
- Supabase: backend central
- AWS S3: evidencia
- Cloudflare: protección/Workers/DNS
- Vercel: frontend de transparencia
- OpenRouter: clasificación auxiliar y modelos fallback

## Coordinación
- Notion: knowledge base
- Asana: tasking
- Gmail/Outlook: comunicación formal
- Calendar: disciplina de crisis
- GWS: producción colaborativa
- Dropbox: intercambio seguro
- GitHub: versionado

## Producción
- HeyGen: simulación/borrador interno
- ElevenLabs: voz/narración
- Together AI: infografías
- Novita: prototipos audiovisuales
- Manus PDF/Slides/Diagram: empaquetado ejecutivo

---

# XIII. RECOMENDACIÓN EJECUTIVA FINAL

Si esto fuera mi implementación real para Clara Rosales, lo haría en **3 tiempos**:

## En 24 horas
- Supabase base
- BrandMentions + Mentionlytics + Apify + S3
- Notion + Asana + Gmail
- pipeline mínimo de alertas
- GPT/Claude/Perplexity operando

## En 72 horas
- dashboard completo
- scoring de incidentes
- Gemini/Grok/DeepSeek conectados
- APIs de Manus integradas
- diagramas de red
- landing page protegida por Cloudflare/Vercel

## En 7 días
- automatización madura
- scoring histórico
- detección de coordinación
- playbooks estables
- cadena de custodia robusta
- reportes ejecutivos y legales industrializados

---

Si quieres, en el siguiente paso te puedo entregar una de estas 3 cosas:

1. **Diagrama técnico completo del sistema en formato arquitectura**
2. **Esquema de tablas de Supabase + campos + relaciones**
3. **Playbook operativo de 72 horas con responsables por rol y automatizaciones Zapier/Edge Functions**