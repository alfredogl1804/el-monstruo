# Matriz de Capacidades de APIs y Modelos — v2.0

Última actualización: 2026-04-09
Source of truth: `/home/ubuntu/skills/api-context-injector/` (v4.0)

## Modelos de IA Disponibles (Directos)

| Modelo | Proveedor | Variable | Contexto | Fortalezas |
|--------|-----------|----------|----------|------------|
| gpt-5.4 | OpenAI | OPENAI_API_KEY | 1.05M | Orquestación, código complejo, síntesis |
| anthropic/claude-sonnet-4-6 | OpenRouter | OPENROUTER_API_KEY | 1M | Arquitectura, crítica, legal, diseño |
| gemini-3.1-pro-preview | Google | GEMINI_API_KEY | 1M | Contexto largo, grounding, investigación |
| grok-4.20-0309-reasoning | xAI | XAI_API_KEY | 2M | Razonamiento, creatividad, contexto masivo |
| deepseek/deepseek-r1 | OpenRouter | OPENROUTER_API_KEY | 128K | Código económico, challenger |
| sonar-reasoning-pro | Perplexity | SONAR_API_KEY | 128K | Investigación web en tiempo real |

## Arsenal OpenRouter (500+ modelos adicionales vía OPENROUTER_API_KEY)

| Modelo | Contexto | Uso Recomendado | Costo |
|--------|----------|----------------|-------|
| meta-llama/llama-4-maverick | 1M | Alternativa open-source a GPT-5 | Bajo |
| moonshotai/kimi-k2.5 | 128K | Código + razonamiento | Bajo |
| qwen/qwen3-coder | 128K | Generación de código | Bajo |
| google/gemma-3-27b | 128K | Tasks medianas, gratis | Gratis |
| deepseek/deepseek-v3-0324 | 128K | Alternativa económica | Muy bajo |
| microsoft/phi-4 | 128K | Tasks ligeras, gratis | Gratis |
| mistralai/mistral-large-2411 | 128K | Europeo, multilingüe | Medio |

## Routing por Capacidad

| Capacidad | Primario | Fallback 1 | Fallback 2 |
|-----------|----------|-----------|-----------|
| Investigación web | Perplexity Sonar | Gemini (grounding) | Grok |
| Síntesis contexto largo | Gemini 3.1 Pro | Grok 4.20 | GPT-5.4 |
| Arquitectura y diseño | Claude Sonnet 4.6 | GPT-5.4 | — |
| Generación de código | GPT-5.4 | Claude Sonnet 4.6 | DeepSeek R1 |
| Juez/Crítico | Claude (si generó GPT) | GPT (si generó Claude) | Gemini |
| Challenger económico | DeepSeek R1 | Llama 4 Maverick | Qwen3 |
| Orquestación | GPT-5.4 | Claude Sonnet 4.6 | — |
| Código económico masivo | DeepSeek R1 | Qwen3 Coder | Llama 4 |

## APIs de Media y Generación

| Servicio | Variable | Capacidades |
|----------|----------|-------------|
| ElevenLabs | ELEVENLABS_API_KEY | TTS, clonación de voz, STS, dubbing, sound effects |
| HeyGen | HEYGEN_API_KEY | Video con avatares IA, lip-sync, text-to-video |
| Generación nativa Manus | — | Imágenes, video, audio, música, speech (tool generate) |

## APIs de Infraestructura

| Servicio | Variable | Arsenal |
|----------|----------|---------|
| Cloudflare | CLOUDFLARE_API_TOKEN | Workers, R2, D1, KV, Pages, Workers AI (50+ modelos), Vectorize, Images, Stream |
| Dropbox | DROPBOX_API_KEY | Files, sharing, team folders |
| Vercel | MCP vercel | Projects, deployments, domains, env vars, serverless functions |

## APIs de Datos y Scraping

| Servicio | Variable/MCP | Arsenal |
|----------|-------------|---------|
| Apify | Notion DB | 23,000+ actors: Instagram, Google Maps, Amazon, LinkedIn, Zillow, YouTube |
| BrandMentions | Notion DB | Social listening: mentions, sentiment, influencers, competitors |
| Mentionlytics | Notion DB | Social monitoring: v1/v2 API, alerts, reports |

## APIs de Pagos

| Servicio | Variable/MCP | Arsenal |
|----------|-------------|---------|
| PayPal | MCP paypal-for-business | Orders, invoices, subscriptions, catalog, shipments |
| Stripe | Notion DB | Payments, subscriptions, billing portal, webhooks |
| RevenueCat | MCP revenuecat | In-app subscriptions, entitlements, offerings, paywalls |

## MCPs Configurados (11)

| MCP | Uso en Skills |
|-----|---------------|
| asana | Gestión de proyectos, tareas, goals, teams |
| zapier | Automatización: 8,000+ apps (Slack, Salesforce, Shopify, Mailchimp, HubSpot) |
| supabase | PostgreSQL, pgvector RAG, Auth, Storage, Realtime, Edge Functions |
| notion | Documentación, bases de datos, wikis, workflows |
| gmail | Email: redactar, buscar, resumir hilos |
| google-calendar | Eventos, scheduling, time management |
| instagram | Publicar posts, stories, reels; insights |
| outlook-mail | Email corporativo: redactar, buscar, gestionar |
| vercel | Deploy, projects, domains, logs |
| paypal-for-business | Pagos, facturas, suscripciones |
| revenuecat | Suscripciones in-app, entitlements |

## CLIs y Herramientas Nativas

| Herramienta | Uso |
|-------------|-----|
| gh | GitHub: repos, issues, PRs, Actions, Pages, Packages |
| gws | Google Drive, Docs, Sheets, Slides |
| rclone | Sync de archivos (Dropbox, Drive, S3) |
| manus-render-diagram | Diagramas D2/Mermaid/PlantUML → PNG |
| manus-md-to-pdf | Markdown → PDF |
| manus-speech-to-text | Audio/Video → texto |
| manus-upload-file | Upload a S3 público |
| manus-analyze-video | Análisis de video con LLM multimodal |
| manus-mcp-cli | Interacción con servidores MCP |
| manus-export-slides | Exportar slides a PDF/PPT |

## Arsenal AWS (vía credenciales en Notion DB)

| Servicio | Uso |
|----------|-----|
| S3 | Object storage, hosting estático |
| Bedrock | 20+ modelos IA (Titan, Llama, Claude) |
| Lambda | Serverless functions |
| SES | Email transaccional masivo |
| Rekognition | Computer vision |
| Polly | TTS |
| Transcribe | STT |
| DynamoDB | NoSQL database |

## Paquetes Python Preinstalados

beautifulsoup4, fastapi, flask, fpdf2, markdown, matplotlib, numpy, openpyxl, pandas, pdf2image, pillow, plotly, reportlab, requests, seaborn, tabulate, uvicorn, weasyprint, xhtml2pdf

## Nota de Integración

Para información completa y actualizada de todas las APIs, arsenals, routing y pipelines,
consultar directamente el skill `api-context-injector`:
- SKILL.md: `/home/ubuntu/skills/api-context-injector/SKILL.md`
- Capability Registry: `/home/ubuntu/skills/api-context-injector/routing/capability_registry.yaml`
- Arsenals: `/home/ubuntu/skills/api-context-injector/arsenals/`
- Decision Router: `/home/ubuntu/skills/api-context-injector/routing/decision_router.yaml`
