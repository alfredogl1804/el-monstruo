# Política de Fallback — Cadenas de Degradación

> Verificado: 2026-04-08 | TTL: 30 días

## Principios

1. **Nunca fallar silenciosamente** — si el primario falla, el agente DEBE intentar el fallback
2. **Degradación graceful** — el fallback puede ser inferior pero funcional
3. **Máximo 3 saltos** — si 3 proveedores fallan, escalar a humano
4. **ALTO TOTAL** si < 3 sabios disponibles simultáneamente

## Cadenas de Fallback — LLMs

| Primario | Fallback 1 | Fallback 2 | Fallback 3 (Budget) |
|----------|-----------|-----------|---------------------|
| GPT-5.4 | Claude Opus 4.6 | Grok 4.20 | OpenRouter/Llama-4-Maverick |
| Claude Opus 4.6 | GPT-5.4 | Gemini 3.1 | OpenRouter/DeepSeek-R1 |
| Gemini 3.1 | GPT-5.4 | Claude | — |
| Grok 4.20 | GPT-5.4 | Claude | — |
| DeepSeek R1 | Gemini 3.1 | GPT-5.4 | — |
| Perplexity Sonar | Grok (tiene web access) | Gemini + search | — |

## Cadenas de Fallback — Media

| Primario | Fallback 1 | Fallback 2 |
|----------|-----------|-----------|
| HeyGen (video) | Atlas Cloud (Notion) | — |
| ElevenLabs (TTS) | AWS Polly (volumen) | OpenAI TTS |
| Together AI (imagen) | Replicate | Novita AI |
| Meshy (3D) | — | — |

## Cadenas de Fallback — Infraestructura

| Primario | Fallback 1 | Fallback 2 |
|----------|-----------|-----------|
| Cloudflare Workers | AWS Lambda | Vercel Functions |
| Cloudflare R2 | AWS S3 | Supabase Storage |
| Cloudflare D1 | Supabase PostgreSQL | — |
| Supabase PostgreSQL | AWS RDS | Cloudflare D1 |
| Supabase pgvector | Cloudflare Vectorize | — |
| Vercel Deploy | Cloudflare Pages | GitHub Pages |

## Cadenas de Fallback — Scraping/Data

| Primario | Fallback 1 | Fallback 2 |
|----------|-----------|-----------|
| Apify actor específico | Apify/web-scraper genérico | Browser nativo |
| BrandMentions | Mentionlytics | Apify social scrapers |
| Keepa (precios) | Apify/amazon-scraper | — |

## Cadenas de Fallback — Automatización

| Primario | Fallback 1 | Fallback 2 |
|----------|-----------|-----------|
| Zapier action | API directa del servicio | Script Python custom |
| Gmail MCP | Outlook MCP | AWS SES |
| Asana MCP | Zapier/Trello | Notion como task tracker |

## Protocolo de Escalación

```
1. Intentar primario
2. Si falla → log error + intentar fallback 1
3. Si falla → log error + intentar fallback 2
4. Si falla → log error + ALERTAR AL USUARIO
5. Si < 3 sabios disponibles → ALTO TOTAL
```

## Criterios de Selección de Fallback

Cuando hay múltiples opciones, priorizar por:
1. **Herramientas ya autenticadas** (env var presente > Notion > no disponible)
2. **Calidad** (para tareas críticas)
3. **Costo** (para tareas repetitivas/volumen)
4. **Latencia** (para tareas interactivas)
5. **Privacidad** (para datos sensibles, preferir proveedores con DPA)
