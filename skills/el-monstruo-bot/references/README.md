# El Monstruo - Bot de Telegram

Orquestador de IAs con 6 cerebros (GPT-5.4, Claude Opus 4.6, Gemini 3.1, Grok 4.20, Perplexity Sonar, DeepSeek R1) y 11 MCPs conectados.

## Comandos
- `/start` - Bienvenida
- `/research [empresa]` - Investigar un lead completo
- `/status` - Estado del sistema
- `/help` - Ayuda

## Variables de Entorno Requeridas
- `TELEGRAM_TOKEN` - Token del bot de Telegram
- `OPENAI_API_KEY` - API key de OpenAI
- `SONAR_API_KEY` - API key de Perplexity
- `XAI_API_KEY` - API key de Grok/xAI
- `OPENROUTER_API_KEY` - API key de OpenRouter (DeepSeek)
- `GEMINI_API_KEY` - API key de Google Gemini

## Deploy en Railway
1. Conectar este repo a Railway
2. Configurar las variables de entorno
3. Railway detecta el Procfile y arranca el worker automáticamente
