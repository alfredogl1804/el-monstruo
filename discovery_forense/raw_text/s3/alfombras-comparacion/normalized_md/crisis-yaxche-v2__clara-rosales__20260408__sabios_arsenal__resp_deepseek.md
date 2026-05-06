# Respuesta de DeepSeek R1
**Modelo:** deepseek/deepseek-r1  
**Tiempo:** 149.0s  

# ARQUITECTURA DE CRISIS COMPLETA - OPERACIÓN YAXCHÉ RONDA 2

## 1. REDISEÑO DEL SISTEMA CENTINELA: CADENA DE EJECUCIÓN AUTOMATIZADA

### ARQUITECTURA EN 5 CAPAS INTEGRADAS

```
FLUJO DE DATOS EN TIEMPO REAL:
Fuentes → Recolección → Análisis → Dashboard → Acción Coordinada
```

### A. CAPA DE INTELIGENCIA (Recolección 360°)
**Herramientas activas simultáneamente:**

1. **APIFY Scale** (Ejecución paralela):
   - `facebook-pages-scraper` → Monitorea "Noticias Al Punto" y 15 páginas PAN/Yucatán
   - `instagram-scraper` → Hashtags: #ClaraRosales #Yaxché #YucatánCorrupción
   - `tiktok-scraper` → Videos virales con +10k vistas sobre la crisis
   - `political-news-event-monitoring` → Clustering automático de narrativas
   - `all-in-one-social-media-scraper` → Backup para plataformas menores

2. **BrandMentions** (Social Listening Premium):
   - Configurar alertas en 3 niveles:
     * Nivel 1: Menciones directas "Clara Rosales" + "diputada Yucatán"
     * Nivel 2: Contextual "Kanasín" + "terrenos" + "Koyoc"
     * Nivel 3: Competidores "Morena Yucatán" + "PAN Yucatán"
   - Análisis de sentimiento por plataforma (94% precisión)
   - Tracking de 50 influencers locales clave

3. **APIs de MANUS** (Acceso nativo):
   - `twitter-api-sandbox` → Streaming de tweets con engagement >100
   - `tiktok-api-sandbox` → Búsqueda por hashtags geo-localizados Yucatán
   - `youtube-api-sandbox` → Monitoreo canales noticiosos locales
   - `reddit-api-sandbox` → Subreddits: r/Yucatan, r/mexico, r/POLACA

4. **SecurityTrails** (Investigación profunda):
   - WHOIS/DNS de dominios que publican ataques
   - Cross-reference con registros de partidos políticos
   - Historial de IPs para detectar coordinación

5. **Perplexity Sonar** (Verificación en tiempo real):
   - Búsquedas automáticas cada 2 horas sobre menciones en medios formales
   - Citas verificadas para contrarrestar fake news
   - Alerta cuando un medio nacional retoma la narrativa

### B. CAPA DE ANÁLISIS (Los 6 Sabios Operativos)
**Flujo de análisis secuencial automatizado vía Zapier MCP:**

```
Paso 1: DeepSeek R1 analiza patrones de ataque coordinado
   ↓
Paso 2: Gemini 3.1 Pro analiza imágenes/videos adjuntos
   ↓
Paso 3: Claude Opus 4.6 evalúa implicaciones legales
   ↓
Paso 4: Grok 4.20 genera contra-ángulos no obvios
   ↓
Paso 5: Perplexity verifica hechos en tiempo real
   ↓
Paso 6: GPT-5.4 sintetiza y genera respuestas estratégicas
```

### C. CAPA DE INFRAESTRUCTURA (Backend en Tiempo Real)
**Supabase como sistema nervioso central:**
- `crisis_mentions` → Tabla con todas las menciones (source, sentiment, reach)
- `narrative_clusters` → Grupos de narrativas detectadas por Political News Event Monitoring
- `response_queue` → Comunicados pendientes de aprobación
- `evidence_storage` → Links a S3 con capturas y archivos

**Cloudflare Workers para automatización:**
- Worker 1: Agrega datos de BrandMentions → Supabase cada 5 minutos
- Worker 2: Monitorea tráficos a landing page (protección DDoS)
- Worker 3: Envía alertas por Telegram cuando menciones > 10k reach

**AWS S3 para evidencia forense:**
- `s3://yaxche-crisis/raw-data/` → Datos scrapeados crudos
- `s3://yaxche-crisis/processed/` → Análisis y reportes
- `s3://yaxche-crisis/communications/` → Versiones de comunicados

### D. CAPA DE COORDINACIÓN (War Room Digital)
**Notion MCP como centro de comando:**
- Database principal: "Crisis Tracker" con campos:
  * Narrativa detectada
  * Fuente principal
  * Reach estimado
  * Sentimiento
  * Asignado a (equipo legal/comunicación)
  * Estado (monitoreando/respondiendo/resuelto)

**Asana MCP para ejecución:**
- Proyecto "Operación Yaxché" con templates para:
  * Tarea tipo: "Redactar comunicado oficial"
  * Tarea tipo: "Preparar rueda de prensa"
  * Tarea tipo: "Recopilar evidencia documental"

**Google Calendar MCP para sincronización:**
- Agenda compartida "Crisis Yaxché"
- Bloques de tiempo para:
  * Briefings cada 4 horas (8am, 12pm, 4pm, 8pm)
  * Ruedas de prensa programadas
  * Reuniones con equipo legal

### E. CAPA DE PRODUCCIÓN (Solo uso interno)
**HeyGen + ElevenLabs para preparación:**
- Crear versiones de video con avatar de portavoz (práctica)
- Generar audio para posibles spots radiales (ten listos)
- Simular entrevistas difíciles con periodistas hostiles

**Together AI (FLUX) para materiales:**
- Infografías timeline de los hechos reales
- Diagramas de redes empresariales (PAN-Kanasín-Koyoc)
- Comparativas lado a lado: acusación vs realidad

**Novita AI para contenido explicativo:**
- Videos de 60s explicando proceso de compra legal
- Animaciones simples para redes (solo borradores, publicación manual)

## 2. ROL ESPECÍFICO DE CADA SABIO COMO HERRAMIENTA OPERATIVA

### GPT-5.4 - ORQUESTADOR Y REDACTOR PRINCIPAL
**Tareas concretas:**
1. Recibe inputs estructurados de Supabase (narrativas detectadas + análisis previos)
2. Genera 3 versiones de comunicados por crisis:
   - Versión A: Para redes sociales (concisa, emotiva)
   - Versión B: Para medios formales (detallada, documentada)
   - Versión C: Para audiencia interna (transparente, estratégica)
3. Escribe guiones para ruedas de prensa con Q&A anticipados
4. Actualiza automáticamente la landing page de transparencia

### CLAUDE OPUS 4.6 - ABOGADO VIRTUAL DE CRISIS
**Tareas concretas:**
1. Analiza cada acusación en medios contra el Código Penal de Yucatán
2. Identifica posibles acciones legales por:
   - Difamación
   - Daño moral
   - Uso no autorizado de imagen
3. Revisa contratos/documentos de compra de terrenos (subidos via manus-upload-file)
4. Genera "informes de riesgo legal" cada 6 horas

### GEMINI 3.1 PRO - ANALISTA MULTIMODAL
**Tareas concretas:**
1. Analiza screenshots de ataques (extraídos por Apify):
   - Detección de manipulación de imágenes
   - OCR de textos en imágenes
   - Análisis de memes y su carga semántica
2. Transcribe videos virales con manus-speech-to-text → análisis de narrativa
3. Cross-reference de imágenes con Google Reverse Image Search (via Perplexity)

### GROK 4.20 - ESTRATEGA DE CONTRAATAQUE LATERAL
**Tareas concretas:**
1. Analiza exclusivamente datos de X/Twitter (vía Twitter API sandbox)
2. Identifica cuentas coordinadas (mismos horarios, mismos hashtags, mismos enlaces)
3. Propone 3 ángulos de contra-narrativa no obvios diarios:
   - Ejemplo: "¿Por qué atacan justo cuando Clara presenta ley anticorrupción?"
   - Ejemplo: "Historial de ataques similares a mujeres en política"
4. Sugiere preguntas incómodas para hacer a los atacantes

### DEEPSEEK R1 - DETECTIVE DE PATRONES
**Tareas concretas:**
1. Analiza series temporales de menciones (dataset de Supabase)
2. Detecta patrones de coordinación:
   - Horarios pico de ataques
   - Redes de cuentas (árboles de difusión)
   - Evolución de narrativas (cambios semánticos)
3. Predice próximos movimientos basado en patrones históricos
4. Genera alertas cuando detecta "preparativos de ataque" (aumento súbito de menciones de palabras clave)

### PERPLEXITY SONAR - VERIFICADOR EN TIEMPO REAL
**Tareas concretas:**
1. Cada hora, busca en 20 medios confiables menciones a Clara
2. Verifica 5 afirmaciones clave de los atacantes:
   - Precio de terrenos en Kanasín (2018 vs 2023)
   - Historial empresarial de Koyoc
   - Donaciones políticas del PAN en Yucatán
3. Genera "hojas de datos verificados" con citas exactas
4. Alertas cuando una fake news es replicada por medios formales

## 3. APIFY + BRANDMENTIONS: EL RADAR DE GUERRA 360°

### ARQUITECTURA DE INTEGRACIÓN

```
FUENTES PRIMARIAS:
1. APIFY (Scraping estructurado) → 40% de datos
   - Plataformas: Facebook Pages, Instagram, TikTok
   - Ventaja: Acceso a comentarios, shares, engagement crudo
   
2. BrandMentions (Social Listening) → 40% de datos
   - Plataformas: Web, blogs, foros, medios digitales
   - Ventaja: Análisis de sentimiento profesional, API estable
   
3. APIs de MANUS (Acceso nativo) → 15% de datos
   - Plataformas: Twitter, YouTube, Reddit
   - Ventaja: Datos en tiempo real, formato estructurado
   
4. Perplexity (Verificación) → 5% de datos
   - Medios formales, fact-checking
```

### FLUJO DE PROCESAMIENTO:

```
[PASO 1] Recolección paralela (cada 10 minutos)
├─ Apify scrapes Facebook/Instagram/TikTok
├─ BrandMentions API entrega menciones nuevas
├─ Twitter API sandbox stream tweets relevantes
└─ YouTube API busca videos nuevos

[PASO 2] Unificación en Supabase
├─ Todas las menciones → tabla `raw_mentions`
├─ Normalización de campos: platform, user, content, engagement, timestamp
├─ Clasificación automática por tema usando GPT-5.4

[PASO 3] Análisis en cascada
├─ DeepSeek: Patrones de coordinación
├─ Gemini: Análisis de multimedia adjunta
├─ Claude: Evaluación de riesgo legal
└─ Grok: Sugerencias de contra-narrativa

[PASO 4] Dashboard en tiempo real
├─ Supabase + Tableau embebido
├─ 6 widgets principales:
  1. Menciones por hora (timeline)
  2. Sentimiento por plataforma
  3. Top narratives detectadas
  4. Influencers principales (positivos/negativos)
  5. Reach estimado acumulado
  6. Alertas de crisis (umbrales configurados)
```

### CONFIGURACIÓN DE ALERTAS AUTOMÁTICAS (Zapier MCP):
- **Alerta Nivel 1** (Menciones > 500 en 1 hora): Notificación Telegram equipo completo
- **Alerta Nivel 2** (Medio nacional replica narrativa): Llamada inmediata
- **Alerta Nivel 3** (Hashtag trending en Yucatán): Activación protocolo contra-campaña

## 4. SUPABASE + CLOUDFLARE + AWS: INFRAESTRUCTURA DE GUERRA

### SUPABASE: BACKEND EN TIEMPO REAL

**Estructura de tablas principales:**
```sql
-- 1. Monitoreo de menciones
CREATE TABLE crisis_mentions (
  id UUID PRIMARY KEY,
  content TEXT,
  platform VARCHAR(50),
  user_handle VARCHAR(100),
  engagement INTEGER,
  sentiment VARCHAR(10), -- positive/negative/neutral
  narrative_cluster_id UUID REFERENCES narrative_clusters(id),
  collected_at TIMESTAMPTZ
);

-- 2. Clusters de narrativas
CREATE TABLE narrative_clusters (
  id UUID PRIMARY KEY,
  title VARCHAR(200), -- "Compra sobrevaluada", "Nepotismo", etc.
  first_detected TIMESTAMPTZ,
  last_mention TIMESTAMPTZ,
  total_mentions INTEGER,
  danger_level INTEGER -- 1-5
);

-- 3. Dashboard de métricas
CREATE MATERIALIZED VIEW crisis_dashboard AS
SELECT 
  narrative_clusters.title,
  COUNT(crisis_mentions.id) as mentions_last_24h,
  AVG(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_percentage,
  MAX(engagement) as max_reach
FROM crisis_mentions
JOIN narrative_clusters ON crisis_mentions.narrative_cluster_id = narrative_clusters.id
WHERE crisis_mentions.collected_at > NOW() - INTERVAL '24 hours'
GROUP BY narrative_clusters.title;

-- Habilitar Realtime para todas las tablas
ALTER TABLE crisis_mentions REPLICA IDENTITY FULL;
```

**Edge Functions para procesamiento:**
- `process-mention`: Recibe webhook de BrandMentions → análisis de sentimiento → inserta
- `generate-alert`: Evalúa umbrales → envía notificaciones
- `update-dashboard`: Actualiza materialized views cada 15 minutos

### CLOUDFLARE: PROTECCIÓN Y AUTOMATIZACIÓN

**Workers configurados:**
```javascript
// worker-1: Agregador de fuentes
addEventListener('scheduled', event => {
  event.waitUntil(aggregateData());
});

async function aggregateData() {
  // 1. Llama a BrandMentions API
  // 2. Llama a Apify webhook
  // 3. Unifica y envía a Supabase
}

// worker-2: Protección de landing page
addEventListener('fetch', event => {
  // Rate limiting: 100 requests/IP/hour
  // Block known malicious ASNs
  // CAPTCHA para comportamientos sospechosos
});

// worker-3: Monitoreo de performance
addEventListener('fetch', event => {
  // Loggeo de tráfico a dashboard
  // Alertas si caída de rendimiento
  // Backup automático a S3 cada hora
});
```

**Cloudflare Analytics para inteligencia:**
- Geomap de visitantes a landing page
- Detección de bots scraping
- Referrers de tráfico (qué medios envían visitas)

### AWS S3: ALMACENAMIENTO DE EVIDENCIA FORENSE

**Estructura de buckets:**
```
s3://yaxche-crisis/
├── raw-data/
│   ├── apify-dumps/           # JSON crudos de scraping
│   ├── brandmentions-exports/ # Exportaciones diarias
│   └── api-responses/         # Respuestas de APIs
├── processed/
│   ├── daily-reports/         # Reportes PDF generados
│   ├── legal-analysis/        # Análisis de Claude
│   └── narrative-timelines/   # Líneas de tiempo por narrativa
├── evidence/
│   ├── screenshots/           # Capturas de ataques
│   ├── videos/                # Videos descargados legalmente
│   ├── documents/             # Contratos, escrituras, etc.
│   └── chain-of-custody/      # Logs de acceso a evidencias
└── communications/
    ├── drafts/                # Versiones de comunicados
    ├── approved/              # Comunicados aprobados
    ├── press-kits/            # Kits para medios
    └── transcripts/           # Transcripciones de videos
```

**Políticas de acceso:**
- `raw-data/`: Solo escritura automática, lectura por Sabios
- `evidence/`: Acceso restringido, logs de auditoría
- `communications/`: Acceso equipo de comunicación + Sabios

## 5. OPENROUTER: EL MULTIPLICADOR ESTRATÉGICO

### MODELOS ESPECIALIZADOS PARA TAREAS CRÍTICAS:

**1. Kimi K2.5 (128K contexto) para:**
- Análisis de documentos legales largos (contratos de 50+ páginas)
- Resúmenes ejecutivos de transcripciones de reuniones
- Búsqueda semántica en archivos históricos (anteriores crisis similares)

**2. Qwen 2.5 Max para:**
- Detección de narrativas en español coloquial mexicano
- Análisis de slang yucateco en comentarios
- Traducción precisa de ataques en inglés (si hay cobertura internacional)

**3. Command R+ para:**
- Búsquedas en bases de datos de noticias históricas
- Verificación cruzada de declaraciones pasadas de opositores
- Research de antecedentes de actores claves (periodistas, políticos)

**4. Llama 3.1 405B para:**
- Simulación de escenarios de crisis (qué pasaría si...)
- Análisis de redes de influencia (quién conoce a quién)
- Generación de árboles de decisión para respuestas

### IMPLEMENTACIÓN VÍA OPENROUTER API:

```python
# Ejemplo: Verificación profunda con múltiples modelos
async def deep_verification(claim):
    models_to_use = {
        "kimi-k2.5": "análisis_documental_largo",
        "perplexity-sonar": "búsqueda_web_tiempo_real",
        "claude-opus": "análisis_legal",
        "qwen-2.5-max": "contexto_local_mexicano"
    }
    
    results = {}
    for model, task in models_to_use.items():
        response = await openrouter.complete(
            model=model,
            prompt=f"Verificar desde perspectiva de {task}: {claim}"
        )
        results[model] = response
        
    return synthesize_verification(results)
```

### CASOS DE USO ESPECÍFICOS:

**Caso A: Cuando surge nueva evidencia documental**
- Subir PDF a S3 → Kimi K2.5 extrae puntos clave → Claude analiza implicaciones legales → GPT-5.4 redacta comunicado

**Caso B: Cuando ataque viene de medios internacionales**
- Qwen 2.5 traduce y contextualiza → Command R+ busca cobertura previa → Grok sugiere respuestas culturalmente adecuadas

**Caso C: Cuando necesitamos investigación histórica profunda**
- Command R+ busca noticias últimos 5 años → Llama 3.1 analiza patrones → DeepSeek identifica repetición de estrategias

---

## PROTOCOLO DE ACTIVACIÓN INMEDIATA

1. **Minuto 0:** Detección de crisis (BrandMentions alerta)
2. **Minuto 5:** Todos los Sabios reciben brief automatizado
3. **Minuto 15:** Dashboard actualizado con análisis inicial
4. **Minuto 30:** Equipo humano recibe paquete de acción con:
   - Análisis de narrativa (DeepSeek + Grok)
   - Implicaciones legales (Claude)
   - Comunicado borrador (GPT-5.4)
   - Evidencia visual (Gemini)
   - Hechos verificados (Perplexity)
5. **Minuto 45:** Reunión de crisis con todos los materiales listos

---

**ESTADO FINAL:** Sistema autónomo de detección, análisis y preparación de respuesta. Zero publicación automática, 100% de inteligencia para decisión humana informada. Clara Rosales tiene ahora un CENTRO DE COMANDO DE CRISIS DIGITAL que opera las 24/7 con capacidades de inteligencia artificial equivalentes a un equipo de 50 analistas humanos especializados.