# CONSULTA RONDA 2: Rediseñar el Plan de Crisis con el Arsenal COMPLETO

## RESTRICCIÓN ABSOLUTA
**NUNCA se usará ninguna herramienta para PUBLICAR contenido en redes sociales (Instagram, Facebook, X, TikTok, etc.).** Todas las herramientas conectadas a redes sociales se usan EXCLUSIVAMENTE para monitoreo, escucha, análisis e inteligencia. Solo lectura, cero escritura.

## CONTEXTO
Estamos en la Ronda 2 de la Operación YAXCHÉ (crisis de Clara Rosales, diputada de Yucatán). En la Ronda 1, los Sabios recomendaron solo 5 herramientas y dejaron fuera la mayoría del arsenal. El usuario (Alfredo) identificó las herramientas faltantes. Ahora necesitamos un plan que use TODO el poder disponible.

## ARSENAL COMPLETO DISPONIBLE (Organizado por función en la crisis)

### A. LOS 6 SABIOS (IAs LLM) — No solo para consultar, sino como herramientas operativas
| Sabio | Modelo | Contexto | Rol operativo en crisis |
|-------|--------|----------|------------------------|
| GPT-5.4 | gpt-5.4 | 1.05M | Orquestador, redactor de comunicados, análisis de escenarios |
| Claude Opus 4.6 | claude-opus-4-6 | 1M | Análisis legal profundo, crítica de narrativas, revisión de documentos |
| Gemini 3.1 Pro | gemini-3.1-pro-preview | 1M | Análisis multimodal (imágenes, videos, capturas de pantalla de ataques) |
| Grok 4.20 | grok-4.20-0309-reasoning | 2M | Pensamiento lateral, ángulos no obvios de contraataque, análisis de X/Twitter |
| DeepSeek R1 | deepseek-r1 | 128K | Cadenas de razonamiento, análisis de patrones en ataques coordinados |
| Perplexity Sonar | sonar-reasoning-pro | 128K | Búsqueda web en tiempo real, verificación de hechos con citas |

### B. APIFY (Plan Scale) — Web scraping masivo
| Actor | Función en crisis |
|-------|-------------------|
| Facebook Pages Scraper | Scraping de páginas que atacan a Clara (Noticias Al Punto, etc.) |
| Instagram Scraper | Monitoreo de perfiles, posts, comentarios, hashtags sobre Clara |
| All-in-One Social Media Scraper | Scraping multi-plataforma |
| Political News Event Monitoring | Clustering de noticias políticas en tiempo real |
| TikTok Scraper | Monitoreo de videos virales sobre la crisis |

### C. BRANDMENTIONS — Social listening profesional
- Monitoreo en tiempo real en 70+ fuentes
- 94% precisión en análisis de sentimiento
- Alertas instantáneas de menciones nuevas
- API propia para integración con otros sistemas
- Tracking de influencers y propagadores

### D. MANUS (Todas sus versiones/capacidades nativas)
| Herramienta | Función en crisis |
|-------------|-------------------|
| manus-analyze-video | Analizar videos de opositores, detectar manipulación, extraer narrativas |
| manus-speech-to-text | Transcribir audios/videos de ataques automáticamente |
| manus-render-diagram | Crear diagramas de redes de conexiones (PAN-Kanasín-Koyoc) |
| manus-md-to-pdf | Convertir comunicados y reportes a PDF profesional |
| manus-upload-file | Subir archivos a S3 para URLs públicas |
| manus-export-slides | Exportar presentaciones para ruedas de prensa |
| Twitter API (sandbox) | Obtener perfiles, tweets, análisis de cuentas que atacan |
| TikTok API (sandbox) | Buscar videos virales sobre la crisis |
| YouTube API (sandbox) | Monitorear canales que cubren la crisis |
| Reddit API (sandbox) | Monitorear discusiones en subreddits relevantes |

### E. INFRAESTRUCTURA Y BACKEND
| Herramienta | Función en crisis |
|-------------|-------------------|
| AWS S3 | Almacenamiento de evidencia, archivos pesados, backups |
| Cloudflare (env activa) | Protección de landing page, Workers para automatización, monitoreo de tráfico, DNS security |
| Supabase (29 herramientas MCP) | Dashboard de crisis en tiempo real con PostgreSQL + Edge Functions + Realtime |
| OpenRouter | Acceso a modelos adicionales (Kimi K2.5, etc.) como fallback o para tareas específicas |
| Vercel MCP | Deploy de landing page de transparencia |

### F. COMUNICACIÓN Y COORDINACIÓN
| Herramienta | Función en crisis |
|-------------|-------------------|
| Notion MCP (14 herramientas) | War room digital, knowledge base, tracking |
| Asana MCP | Gestión de tareas del equipo de crisis |
| Gmail MCP | Envío de comunicados a medios |
| Outlook MCP | Canal alternativo de comunicados |
| Google Calendar MCP | Agenda de crisis, programar reuniones, ruedas de prensa |
| Google Workspace (gws) | Docs colaborativos, Sheets para dashboards, Slides para presentaciones |
| Dropbox | Compartir documentos legales de forma segura |
| GitHub | Versionado de documentos, tracking de cambios |

### G. MEDIA Y GENERACIÓN
| Herramienta | Función en crisis |
|-------------|-------------------|
| HeyGen | Videos con avatar para respuestas rápidas (uso interno/borrador) |
| ElevenLabs | Narración para videos explicativos, audio para spots |
| Together AI (FLUX) | Infografías profesionales |
| Novita AI (Kling v3, Minimax) | Video AI generativo para contenido explicativo |
| Replicate | Modelos ML para análisis de sentimiento en español |

### H. INTELIGENCIA Y SEGURIDAD
| Herramienta | Función en crisis |
|-------------|-------------------|
| SecurityTrails | DNS/WHOIS de medios atacantes, investigar quién está detrás |
| Mentionlytics | Social listening profesional (complemento de BrandMentions) |
| Zapier MCP | Automatización de flujos entre todas las herramientas |

## PREGUNTA PARA CADA SABIO

Con este arsenal COMPLETO (no el recortado de la Ronda 1), y respetando la restricción de NUNCA publicar en redes:

### 1. REDISEÑO DEL SISTEMA CENTINELA
Diseña la cadena de ejecución automatizada completa que integre TODAS las herramientas relevantes. No dejes nada fuera. Incluye:
- Capa de inteligencia (Apify + BrandMentions + Perplexity + APIs de Manus + SecurityTrails)
- Capa de análisis (6 Sabios operativos, cada uno con su rol específico)
- Capa de infraestructura (Supabase + Cloudflare + AWS)
- Capa de coordinación (Notion + Asana + Gmail + Calendar)
- Capa de producción (HeyGen + ElevenLabs + Together AI — solo para materiales internos y comunicados)

### 2. ROL ESPECÍFICO DE CADA SABIO COMO HERRAMIENTA OPERATIVA
No como "consultores" sino como agentes activos. ¿Qué tarea concreta ejecuta cada uno en el flujo de crisis?

### 3. APIFY + BRANDMENTIONS: EL RADAR DE GUERRA
¿Cómo se combinan Apify (scraping masivo) + BrandMentions (social listening) + Perplexity (búsqueda web) + APIs de Manus (Twitter, TikTok, YouTube, Reddit) para crear un sistema de inteligencia de 360°?

### 4. SUPABASE + CLOUDFLARE + AWS: LA INFRAESTRUCTURA DE GUERRA
¿Cómo se usa Supabase como backend del dashboard de crisis en tiempo real? ¿Cloudflare para proteger y monitorear? ¿AWS para almacenamiento de evidencia?

### 5. OPENROUTER: EL MULTIPLICADOR
¿Qué modelos adicionales de OpenRouter (Kimi K2.5, etc.) podrían aportar valor que los 6 Sabios principales no cubren?

Responde con arquitectura concreta y accionable. Esto es una crisis real, no un ejercicio teórico.
