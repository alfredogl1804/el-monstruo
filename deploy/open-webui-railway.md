# Open WebUI — Railway Deployment Guide

## Overview
Open WebUI v0.8.12 deployed as a separate Railway service, connected to
El Monstruo kernel via the OpenAI-compatible adapter.

## Step 1: Create New Railway Service

In the El Monstruo Railway project, add a new service:
- **Source:** Docker Image
- **Image:** `ghcr.io/open-webui/open-webui:main`

## Step 2: Environment Variables

Set these environment variables in the Railway service:

```env
# Connect to El Monstruo kernel via internal network
OPENAI_API_BASE_URL=http://el-monstruo-kernel.railway.internal:8000/openai/v1
OPENAI_API_KEY=<same as MONSTRUO_API_KEY>

# Disable Ollama (we don't use local models)
OLLAMA_BASE_URL=

# Security
WEBUI_SECRET_KEY=<generate a random 32-char string>
ENABLE_SIGNUP=false
ENABLE_LOGIN_FORM=true
DEFAULT_USER_ROLE=admin

# Single user setup
WEBUI_AUTH=true

# Disable telemetry
SCARF_NO_ANALYTICS=true
DO_NOT_TRACK=true
ANONYMIZED_TELEMETRY=false

# Performance
ENABLE_WEBSOCKET_SUPPORT=true
ENABLE_COMMUNITY_SHARING=false
```

## Step 3: Persistent Storage

Add a volume mount in Railway:
- **Mount path:** `/app/backend/data`
- This stores Open WebUI's internal database (users, chats, settings)

## Step 4: Networking

- Railway auto-assigns a public domain: `open-webui-xxx.up.railway.app`
- Or set a custom domain in Railway settings

## Step 5: First Login

1. Navigate to the public URL
2. Create admin account (first signup becomes admin)
3. In Settings → Connections, verify the OpenAI connection shows El Monstruo models
4. Test by selecting "monstruo-auto" and sending a message

## Step 6: Verify Models

In the Open WebUI chat interface, the model dropdown should show:
- monstruo-auto (Router decides)
- monstruo-estratega (GPT-5.4)
- monstruo-investigador (Sonar Pro)
- monstruo-arquitecto (Claude Opus)
- monstruo-creativo (Gemini Pro)
- monstruo-critico (Grok)
- monstruo-rapido (Gemini Flash)

## Troubleshooting

### Models not showing
- Check that `OPENAI_API_BASE_URL` points to the correct internal URL
- Check that `OPENAI_API_KEY` matches `MONSTRUO_API_KEY` in the kernel
- Test manually: `curl -H "Authorization: Bearer <key>" http://kernel:8000/openai/v1/models`

### Connection refused
- Ensure both services are in the same Railway project
- Use `.railway.internal` hostname (not public URL) for internal communication
- Check kernel health: `curl http://kernel:8000/health`

### Streaming not working
- Verify `X-Accel-Buffering: no` header is set (done in adapter)
- Check Railway doesn't have a proxy timeout too short (default 300s is fine)
