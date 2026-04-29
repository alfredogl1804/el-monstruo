# Modelos Vigentes — Consejo de Sabios

**Última actualización:** 16 abril 2026
**Fuente:** Semilla v7.3 (Notion) + validación en tiempo real (protocolo anti-autoboicot)

## Tabla de Capacidades

| ID | Sabio | Modelo | Contexto | Grupo | Proveedor | Endpoint |
|----|-------|--------|----------|-------|-----------|----------|
| gpt54 | GPT-5.4 | gpt-5.4 | 1.05M tokens | completo | OpenAI directo | api.openai.com |
| claude | Claude Opus 4.7 | anthropic/claude-opus-4.7 | 1M tokens | completo | OpenRouter | openrouter.ai |
| gemini | Gemini 3.1 Pro | gemini-3.1-pro-preview | 1M tokens | completo | Google GenAI | google |
| grok | Grok 4.20 Reasoning | grok-4.20-0309-reasoning | 2M tokens | completo | xAI | api.x.ai |
| deepseek | DeepSeek R1 | deepseek/deepseek-r1 | 128K tokens | condensado | OpenRouter | openrouter.ai |
| perplexity | Perplexity Sonar | sonar-reasoning-pro | 128K tokens | condensado | Perplexity | api.perplexity.ai |

## Grupos de Contexto

**Grupo "completo" (1M+ tokens):** GPT-5.4, Claude, Gemini, Grok
- Pueden recibir documentos completos sin condensar
- Ideales para análisis profundo con mucho contexto

**Grupo "condensado" (128K tokens):** DeepSeek, Perplexity
- Necesitan resumen ejecutivo (~30K chars) si el contexto excede 100K chars
- Usar `condensar_contexto.py` para generar el resumen

## Roles Especiales

**GPT-5.4 — Orquestador/Sintetizador:** Después de que todos responden, GPT-5.4 sintetiza las respuestas en un documento definitivo.

**Perplexity Sonar — Investigador Web:** Tiene acceso a búsqueda web en tiempo real. Útil para validar datos y encontrar información actualizada. Puede responder "no puedo responder" si el prompt es demasiado abstracto.

**Grok — Contexto Máximo:** Con 2M tokens de contexto, puede recibir los documentos más grandes sin problemas.

**Claude Opus 4.7 — Agente Avanzado:** Modelo flagship de Anthropic lanzado el 16 de abril de 2026. Diseñado para tareas agenticas de larga duración y software engineering avanzado. Fallback #1 para síntesis.

## Notas Técnicas

- Claude Opus 4.7 se usa vía OpenRouter (`anthropic/claude-opus-4.7`). Reemplaza a Sonnet 4.6 como sabio principal.
- aiohttp no soporta Brotli (br) nativamente. El conector de OpenAI usa `Accept-Encoding: gzip, deflate` para evitar este problema.
- Todas las llamadas usan `json.dumps(ensure_ascii=False)` para soporte Unicode completo (acentos, ñ, etc.).

## Variables de Entorno Requeridas

| Variable | Servicio |
|----------|----------|
| OPENAI_API_KEY | GPT-5.4 |
| OPENROUTER_API_KEY | Claude, DeepSeek |
| GEMINI_API_KEY | Gemini |
| XAI_API_KEY | Grok |
| SONAR_API_KEY | Perplexity |
