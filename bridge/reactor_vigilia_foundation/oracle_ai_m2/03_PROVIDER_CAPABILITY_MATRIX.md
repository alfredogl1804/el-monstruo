# Matriz de Proveedores a Verificar

**SPRINT:** SPR-ORACLE-AI-M2-001
**Estado:** DOCTRINE_CANDIDATE

Este documento define los 6 proveedores objetivo para las sondas M2 y los endpoints/métodos que se utilizarán para verificarlos.

| Proveedor | Variable de Entorno | Método de Sonda (Probe Method) | Endpoint Objetivo | Modelos Esperados (Ejemplos) |
|-----------|---------------------|--------------------------------|-------------------|------------------------------|
| **OpenAI** | `OPENAI_API_KEY` | `official_api` (HTTP REST) | `GET https://api.openai.com/v1/models` | `gpt-4o`, `gpt-4-turbo`, `o1-preview` |
| **Anthropic** | `ANTHROPIC_API_KEY` | `official_api` (HTTP REST) | `GET https://api.anthropic.com/v1/models` | `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229` |
| **Google Gemini** | `GEMINI_API_KEY` | `official_api` (HTTP REST) | `GET https://generativelanguage.googleapis.com/v1beta/models` | `gemini-1.5-pro`, `gemini-1.5-flash` |
| **xAI (Grok)** | `XAI_API_KEY` | `official_api` (HTTP REST) | `GET https://api.x.ai/v1/models` | `grok-beta`, `grok-vision-beta` |
| **Perplexity** | `SONAR_API_KEY` | `official_api` (HTTP REST) | `GET https://api.perplexity.ai/models` | `llama-3.1-sonar-small-128k-online` |
| **DeepSeek** | `DEEPSEEK_API_KEY` | `official_api` (HTTP REST) | `GET https://api.deepseek.com/models` | `deepseek-chat`, `deepseek-reasoner` |

## Comportamiento ante Proveedores Adicionales
Si el catálogo original del Oráculo (M1) contiene capacidades de proveedores que no están en esta lista (ej. Midjourney, ElevenLabs), M2 no intentará verificarlos activamente en este sprint a menos que exista una variable de entorno explícita en el entorno actual. Si no hay llave, la capacidad de ese proveedor se marcará como `ACCESS_BLOCKED_NO_KEY` y su evidencia permanecerá como `STATIC_CATALOG`.
