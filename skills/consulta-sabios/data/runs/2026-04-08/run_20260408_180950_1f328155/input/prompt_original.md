# Consulta al Consejo de 6 Sabios: Rediseño del Skill api-context-injector con Enfoque de Arsenal Expandido

## Contexto

Tenemos un skill llamado `api-context-injector` que cataloga 27 conectores directos de Manus + APIs adicionales en Notion. El problema actual es que el skill trata cada conector como una entidad plana, sin reconocer que muchos conectores son **puertas a ecosistemas completos**.

## El Problema (planteado por Alfredo)

> "Hay conectores que dan acceso a otros como Apify, AWS, Cloudflare, OpenRouter. El skill debe contemplar a esos que tiene acceso como parte del arsenal. Porque es verdad. Si no se estarían subutilizando."

## Datos de Investigación Real (verificados hoy 2026-04-08)

### Conectores-Puerta identificados:

1. **OpenRouter** (OPENROUTER_API_KEY activa)
   - 500+ modelos de IA de todos los proveedores (OpenAI, Anthropic, Google, Meta, Mistral, xAI, DeepSeek, Cohere, etc.)
   - Modelos propios: Hunter Alpha (1T params), Healer Alpha
   - Colecciones: coding, roleplay, vision, tool-calling, free models
   - OpenAI-compatible API — un endpoint, todos los modelos

2. **Apify** (API Key en Notion, plan Scale $39/mes)
   - 23,000+ actors pre-construidos en el Store
   - Categorías: scraping web, lead generation, social media, e-commerce, SEO, data extraction
   - Actors populares: Facebook scraper, Instagram scraper, Google Maps scraper, LinkedIn scraper, Amazon scraper, TikTok scraper
   - Capacidades: proxies integrados, scheduling, webhooks, datasets, storage

3. **Cloudflare** (CLOUDFLARE_API_TOKEN activa)
   - Workers: serverless compute en 200+ ciudades
   - Workers AI: 50+ modelos de IA (incluyendo Kimi K2.5, LLaMA, Mistral, Stable Diffusion)
   - R2: object storage (S3-compatible, zero egress fees)
   - D1: SQLite database serverless
   - KV: key-value store global
   - Pages: hosting estático
   - AI Gateway: proxy y cache para APIs de IA
   - Queues, Durable Objects, Vectorize, Hyperdrive

4. **AWS** (credenciales en Notion)
   - 200+ servicios en 30+ categorías
   - Bedrock: acceso a Claude, GPT, Llama, Mistral, Titan, Cohere, Stability AI
   - S3, Lambda, EC2, RDS, DynamoDB, SQS, SNS, SES
   - Rekognition (visión), Polly (TTS), Transcribe (STT), Comprehend (NLP)
   - CloudFront, Route 53, API Gateway

5. **Zapier** (MCP activo)
   - 8,000+ apps conectables
   - Categorías: CRM, email marketing, project management, accounting, social media, e-commerce, HR, customer support
   - Zapier MCP: permite que Manus ejecute acciones en cualquiera de las 8000+ apps
   - Zapier Tables: base de datos integrada
   - Zapier Agents: agentes AI con acceso a todas las apps

6. **GitHub** (GH_TOKEN activa)
   - Acceso a millones de repos open source
   - GitHub Actions: CI/CD
   - GitHub Copilot API
   - GitHub Packages
   - GitHub Pages

7. **Google Drive/Workspace** (tokens activos)
   - Drive: almacenamiento ilimitado
   - Docs: documentos colaborativos
   - Sheets: hojas de cálculo (pseudo-database)
   - Slides: presentaciones
   - Forms: formularios

8. **Supabase** (MCP activo, proyecto Golden Record)
   - PostgreSQL completo
   - Auth: autenticación
   - Storage: archivos
   - Edge Functions: serverless
   - Realtime: websockets
   - Vector: embeddings para RAG

## Lo que necesito de cada Sabio

1. **¿Cómo debe el skill representar estos "arsenales expandidos"?** ¿Nuevo YAML? ¿Sección en SKILL.md? ¿Sub-registros por conector-puerta?

2. **¿Cómo debe el Router de Decisión cambiar?** Actualmente dice "usa Apify para scraping". Debería decir "usa Apify → actor específico X para scraping de Instagram, actor Y para Google Maps, etc."

3. **¿Cuáles son los sub-servicios más valiosos de cada conector-puerta que deben catalogarse explícitamente?** No todos los 23,000 actors de Apify ni los 200 servicios de AWS, sino los top 10-20 más útiles de cada uno.

4. **¿Cómo evitar que el skill se vuelva un monstruo inmanejable?** Balance entre completitud y usabilidad.

5. **¿Cómo debe el inject_context.py cambiar para inyectar contexto de arsenal expandido?** Ejemplo: si la tarea es "scrape Google Maps reviews", debería inyectar: "Usa Apify → actor apify/google-maps-scraper, API key en Notion, plan Scale".

6. **¿Qué modelos de OpenRouter son los más valiosos más allá de los 6 Sabios?** Kimi K2.5, Qwen, Llama 4, etc.

## Restricciones

- El skill debe seguir siendo un SKILL.md legible + YAMLs modulares
- NUNCA credenciales en texto plano
- Debe ser accionable: cada entrada debe tener suficiente info para conectarse
- Debe ser mantenible: no 5000 líneas de YAML

## Formato de Respuesta Esperado

Responde con:
1. Diagnóstico del problema actual (2-3 párrafos)
2. Arquitectura propuesta para arsenal expandido (estructura de archivos + ejemplo)
3. Top sub-servicios por conector-puerta (tabla)
4. Cambios específicos al Router de Decisión
5. Cambios específicos a inject_context.py
6. Anti-patrones a evitar
