# Patrones de Conexión — Copy-Paste Funcionales

> Cada patrón incluye: auth, request, error handling mínimo.
> Verificado: 2026-04-08 | TTL: 30 días

## LLMs — Los 6 Sabios

### OpenAI (GPT-5.4)
```python
from openai import OpenAI
client = OpenAI()  # Usa OPENAI_API_KEY automáticamente
response = client.chat.completions.create(
    model="gpt-5.4",
    max_completion_tokens=16000,  # NUNCA max_tokens
    messages=[{"role": "user", "content": "..."}]
)
print(response.choices[0].message.content)
```

### Claude Sonnet 4.6 (vía OpenRouter — recomendado)
```python
from openai import OpenAI
import os
client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)
response = client.chat.completions.create(
    model="anthropic/claude-sonnet-4-6",  # Vía OpenRouter (Opus tiene timeouts)
    max_tokens=8192,
    messages=[{"role": "user", "content": "..."}]
)
print(response.choices[0].message.content)
```

### Claude Opus 4.6 (API directa — solo fallback)
```python
from anthropic import Anthropic
client = Anthropic()  # Usa ANTHROPIC_API_KEY automáticamente
response = client.messages.create(
    model="claude-opus-4-6",  # Solo para fallback, NO para uso primario
    max_tokens=8192,
    messages=[{"role": "user", "content": "..."}]
)
print(response.content[0].text)
```

### Google Gemini (3.1 Pro)
```python
from google import genai
client = genai.Client()  # Usa GEMINI_API_KEY automáticamente
response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="..."
)
print(response.text)
```

### xAI Grok (4.20)
```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["XAI_API_KEY"], base_url="https://api.x.ai/v1")
response = client.chat.completions.create(
    model="grok-4.20-0309-reasoning",  # NO grok-4-latest
    messages=[{"role": "user", "content": "..."}]
)
print(response.choices[0].message.content)
```

### DeepSeek R1 (via OpenRouter)
```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(
    model="deepseek/deepseek-r1",
    messages=[{"role": "user", "content": "..."}]
)
print(response.choices[0].message.content)
```

### Perplexity Sonar (SOLO requests — PROHIBIDO SDK OpenAI)
```python
import requests, os
response = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={
        "Authorization": f"Bearer {os.environ['SONAR_API_KEY']}",
        "Content-Type": "application/json"
    },
    json={
        "model": "sonar-reasoning-pro",
        "messages": [{"role": "user", "content": "..."}]
    }
)
data = response.json()
print(data["choices"][0]["message"]["content"])
# Citas en: data.get("citations", [])
```

### OpenRouter (cualquier modelo de 500+)
```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(
    model="meta-llama/llama-4-maverick",  # O cualquier modelo del arsenal
    messages=[{"role": "user", "content": "..."}]
)
print(response.choices[0].message.content)
```

## Media APIs

### HeyGen (Video con Avatar)
```python
import requests, os
# Crear video
response = requests.post(
    "https://api.heygen.com/v2/video/generate",
    headers={"X-Api-Key": os.environ["HEYGEN_API_KEY"], "Content-Type": "application/json"},
    json={
        "video_inputs": [{
            "character": {"type": "avatar", "avatar_id": "AVATAR_ID"},
            "voice": {"type": "text", "input_text": "Tu texto aquí", "voice_id": "VOICE_ID"}
        }],
        "dimension": {"width": 1920, "height": 1080}
    }
)
video_id = response.json()["data"]["video_id"]

# Verificar estado
status = requests.get(
    f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
    headers={"X-Api-Key": os.environ["HEYGEN_API_KEY"]}
)
```

### ElevenLabs (TTS)
```python
from elevenlabs import ElevenLabs
client = ElevenLabs()  # Usa ELEVENLABS_API_KEY
audio = client.text_to_speech.convert(
    text="Tu texto aquí",
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # George
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128"
)
with open("output.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

## Conectores-Puerta

### Apify (Scraping)
```python
import requests
# Token: obtener de Notion DB
APIFY_TOKEN = "OBTENER_DE_NOTION"

# Ejecutar actor
response = requests.post(
    "https://api.apify.com/v2/acts/compass~crawler-google-places/runs",
    params={"token": APIFY_TOKEN},
    json={"searchStringsArray": ["restaurants in Miami"], "maxCrawledPlaces": 100}
)
run_id = response.json()["data"]["id"]

# Obtener resultados
results = requests.get(
    f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items",
    params={"token": APIFY_TOKEN}
)
```

### Cloudflare Workers AI (Inferencia Edge)
```python
import requests, os
response = requests.post(
    "https://api.cloudflare.com/client/v4/accounts/ACCOUNT_ID/ai/run/@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    headers={"Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}"},
    json={"messages": [{"role": "user", "content": "..."}]}
)
print(response.json()["result"]["response"])
```

### Cloudflare R2 (Object Storage)
```python
import boto3, os
# R2 es S3-compatible
s3 = boto3.client('s3',
    endpoint_url='https://ACCOUNT_ID.r2.cloudflarestorage.com',
    aws_access_key_id='R2_ACCESS_KEY',
    aws_secret_access_key='R2_SECRET_KEY'
)
s3.upload_file('local_file.pdf', 'my-bucket', 'remote_file.pdf')
```

### AWS Bedrock (Multi-Modelo)
```python
import boto3, json
# Credenciales: obtener de Notion DB
session = boto3.Session(
    aws_access_key_id="FROM_NOTION",
    aws_secret_access_key="FROM_NOTION",
    region_name="us-east-1"
)
bedrock = session.client("bedrock-runtime")
response = bedrock.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    body=json.dumps({"messages": [{"role": "user", "content": "..."}], "max_tokens": 4096, "anthropic_version": "bedrock-2023-05-31"})
)
result = json.loads(response["body"].read())
```

### AWS SES (Email Transaccional)
```python
import boto3
ses = boto3.client('ses', region_name='us-east-1',
    aws_access_key_id="FROM_NOTION", aws_secret_access_key="FROM_NOTION")
ses.send_email(
    Source='from@example.com',
    Destination={'ToAddresses': ['to@example.com']},
    Message={
        'Subject': {'Data': 'Asunto'},
        'Body': {'Html': {'Data': '<h1>Contenido</h1>'}}
    }
)
```

### MCPs (via manus-mcp-cli)
```bash
# Listar herramientas de un MCP
manus-mcp-cli tool list --server notion

# Llamar herramienta
manus-mcp-cli tool call notion-search --server notion --input '{"query": "mi búsqueda"}'

# Servidores disponibles: notion, supabase, gmail, google-calendar, asana,
# zapier, vercel, paypal-for-business, revenuecat, instagram, outlook-mail
```

### Google Workspace (via gws CLI)
```bash
# Listar archivos en Drive
gws drive list

# Crear documento
gws docs create "Mi Documento"

# Operaciones en Sheets
gws sheets read SPREADSHEET_ID RANGE
```

### GitHub (via gh CLI)
```bash
# Clonar repo
gh repo clone owner/repo

# Crear repo privado
gh repo create my-repo --private

# Crear issue
gh issue create --title "Bug" --body "Descripción"
```

## Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|---------|
| `401 Unauthorized` | API key inválida o expirada | Verificar env var, re-obtener de Notion |
| `429 Too Many Requests` | Rate limit excedido | Esperar, usar fallback, o reducir frecuencia |
| `403 Forbidden` | Scope insuficiente | Verificar permisos del token |
| `timeout` | Servicio lento o caído | Usar fallback chain |
| `ModuleNotFoundError` | SDK no instalado | `sudo pip3 install {paquete}` |
