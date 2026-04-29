# Lecciones Aprendidas — Consulta a los Sabios

**Última actualización:** 16 abril 2026

## Errores Resueltos y Soluciones Permanentes

### 1. Claude vía API directa de Anthropic se cuelga (Timeout)
- **Problema:** Claude Opus vía API directa de Anthropic tiene timeouts frecuentes con prompts largos
- **Causa raíz:** El modelo es extremadamente lento para prompts >50K caracteres vía API directa
- **Solución permanente:** Usar Claude vía OpenRouter (`anthropic/claude-opus-4.7`). Alfredo aprobó este patrón.
- **NUNCA:** Intentar Claude Opus vía API directa de Anthropic
- **Nota (16 abril 2026):** Claude Opus 4.7 reemplaza a Sonnet 4.6 como sabio principal. El patrón de usar OpenRouter se mantiene.

### 2. aiohttp no decodifica Brotli (Error 400 fantasma)
- **Problema:** OpenAI devuelve respuestas comprimidas en Brotli (br). aiohttp lanza `ContentEncodingError: Can not decode content-encoding: br`
- **Causa raíz:** La librería aiohttp no tiene soporte nativo para Brotli
- **Solución permanente:** Enviar header `Accept-Encoding: gzip, deflate` y usar `auto_decompress=False` con descompresión manual de gzip
- **NUNCA:** Usar `json=payload` con aiohttp para OpenAI; siempre usar `data=_json_serialize(payload)`

### 3. Caracteres Unicode corrompen el payload
- **Problema:** Prompts con acentos (á, é, ñ, Ú) causan errores de decodificación
- **Causa raíz:** `json.dumps()` por defecto usa `ensure_ascii=True`, escapando caracteres Unicode
- **Solución permanente:** Siempre usar `json.dumps(payload, ensure_ascii=False).encode('utf-8')`

### 4. Pérdida de respuestas cuando el proceso muere
- **Problema:** En ronda 3, el proceso fue matado antes de guardar y se perdieron 5 respuestas
- **Causa raíz:** Las respuestas se guardaban al final, no incrementalmente
- **Solución permanente:** `conector_sabios.py` guarda cada respuesta INMEDIATAMENTE al disco cuando llega (parámetro `guardar_en`)

### 5. Scripts se reescriben desde cero cada vez
- **Problema:** Cada consulta requería escribir un nuevo script Python
- **Causa raíz:** No existía infraestructura reutilizable
- **Solución permanente:** Esta skill. El agente SOLO debe importar `from conector_sabios import consultar_todos` y ejecutar `consultar_paralelo.py`

### 6. Perplexity responde "no puedo responder"
- **Problema:** Sonar busca en web y a veces no encuentra información relevante para prompts abstractos
- **Causa raíz:** Es un modelo de búsqueda, no de razonamiento puro
- **Solución:** Aceptar que Perplexity puede fallar en prompts muy abstractos. No es un error del sistema, es una limitación del modelo. Si falla, el protocolo de semilla v7.3 permite continuar con 5 sabios.

## Buenas Prácticas Confirmadas

1. **Pre-vuelo SIEMPRE:** Ejecutar `ping_sabios.py` antes de cada consulta real
2. **Guardar incrementalmente:** Cada respuesta se guarda al disco inmediatamente
3. **Prompt condensado para 128K:** Usar `condensar_contexto.py` cuando el contexto excede 100K chars
4. **GPT-5.4 como orquestador:** Siempre sintetizar al final con `sintetizar_gpt54.py`
5. **Mínimo 3 sabios:** Si menos de 3 responden, NO proceder (protocolo semilla v7.3)
6. **Anti-autoboicot:** Validar model IDs en tiempo real antes de cada consulta. NUNCA asumir que un model ID sigue vigente.
