# Consulta al Consejo de Sabios: Arquitectura del Skill "api-context-injector"

## Contexto
Necesito diseñar un skill para Manus AI que funcione como **inyector de contexto universal de APIs e IAs**. Este skill debe:

1. **Centralizar** toda la información de credenciales, APIs e IAs disponibles en un solo lugar
2. **Inyectar contexto** a Manus sobre qué IA usar para qué tarea, cómo conectarse, y qué capacidades tiene cada una
3. **Mantenerse actualizado** consultando fuentes vivas (Notion DB, variables de entorno, Supabase)
4. **Ser seguro** — no exponer credenciales en texto plano en el SKILL.md, sino referenciar variables de entorno y fuentes seguras

## Fuentes de datos identificadas:
- **Notion DB "API Keys y Credenciales"**: 25+ servicios con API keys, categorías, estados, endpoints
- **Variables de entorno del sandbox**: 15 APIs (OpenAI, Anthropic, Gemini, xAI, Perplexity, OpenRouter, HeyGen, ElevenLabs, Cloudflare, Dropbox, GitHub, Google Drive/Workspace)
- **Semilla v7.3**: Los 6 Sabios con model_ids verificados
- **Notion pages**: Biblia Manus, Mapa de Expansión APIs/MCPs, Integraciones MCP
- **MCPs configurados**: 11 servidores (asana, zapier, supabase, notion, revenuecat, vercel, paypal, gmail, google-calendar, instagram, outlook-mail)
- **Skills existentes**: 12 skills con sus propias dependencias de APIs
- **Herramientas nativas del sandbox**: 10 utilidades CLI

## Inventario completo:
- 6 IAs LLM directas (GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro, Grok 4.20, DeepSeek R1, Perplexity Sonar)
- 8 APIs de media/generación (HeyGen, ElevenLabs, Together AI, Replicate, Novita AI, Atlas Cloud, Meshy AI, Fashn AI)
- 9 APIs de infraestructura (Cloudflare, Dropbox, GitHub, Google Drive, GWS, AWS, Vercel, RunPod, Supabase)
- 5 APIs de datos/monitoreo (Best Buy, Keepa, SecurityTrails, HIBP, Mentionlytics)
- 1 API de pagos (Stripe)
- 11 MCPs
- 10 herramientas nativas
- 12 skills existentes

## Pregunta para los Sabios:
¿Cuál es la mejor arquitectura para este skill considerando:

1. **Estructura del SKILL.md**: ¿Cómo organizar la información para que sea inyectable como contexto sin ser demasiado larga ni demasiado corta?
2. **Seguridad**: ¿Cómo manejar credenciales sin exponerlas en texto plano? ¿Usar solo nombres de variables de entorno?
3. **Actualización**: ¿Debe tener un script que consulte Notion/Supabase para auto-actualizarse?
4. **Router inteligente**: ¿Debe incluir lógica de routing (qué IA usar para qué tipo de tarea)?
5. **Formato de inyección**: ¿YAML, JSON, Markdown tables, o un formato híbrido?
6. **Granularidad**: ¿Un solo archivo monolítico o archivos separados por categoría?
7. **Integración con skills existentes**: ¿Cómo hacer que consulta-sabios, skill-factory y otros skills referencien este skill como fuente de verdad?
8. **Versionado**: ¿Cómo manejar cambios en modelos, endpoints, o credenciales?

Proporcionen una arquitectura concreta con estructura de directorios, archivos, y flujo de ejecución.
