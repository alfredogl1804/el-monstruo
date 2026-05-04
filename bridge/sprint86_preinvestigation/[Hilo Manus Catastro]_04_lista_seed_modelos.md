# [Hilo Manus Catastro] · Tarea 4 — Lista seed de modelos a catalogar en Sprint 86

**Hilo:** `[Hilo Manus Catastro]`
**Fecha:** 2026-05-04
**Estado:** COMPLETADA
**Método:** Validación en tiempo real vía Vellum, Artificial Analysis Intelligence Index, Astabench, llm-stats.com, leaderboards de imagen/video/avatares (mayo 2026)

---

## Principio rector

Esta lista NO inventa métricas, precios, ni Elo. Solo identifica los **identificadores estables** (IDs canónicos) que los clientes API del pipeline diario del Sprint 86 usarán como `seed list` para extraer los valores reales y actuales en runtime.

> **Regla:** ningún campo numérico (precio, Elo, latencia, tokens/seg) se hardcodea en el seed. Esos vienen del Quorum Validator (mín 2-de-3 fuentes) cuando arranque el pipeline. El seed solo provee `id`, `nombre`, `proveedor`, `macroarea`, `dominios`, `subcapacidades`, `tipo`, `licencia` y `fuentes_datos`.

---

## Distribución de los 92 modelos seed (objetivo: 80-105)

| Macroárea | Modelos seed | Justificación |
|---|---|---|
| Inteligencia (LLMs frontier + open) | 24 | Es la macroárea con más rotación; cubrir frontier propietarios + top open-weights |
| Visión generativa (T2I + edición) | 16 | Foco del caso de uso `hero-images` y `renders` |
| Video generativo (T2V + I2V) | 12 | Crece rápido; ya hay 4 ganadores claros y 8 desafiantes |
| Voz / Avatares parlantes | 12 | TTS, STT, lip-sync, full avatar |
| Audio / Música generativa | 6 | Suno y Udio dominan; resto son nicho |
| Embeddings y Vector DB (ADDENDUM) | 6 | Fuera del Diseño Maestro v1, agregado por feedback Cowork |
| Code-execution / Sandboxes (ADDENDUM) | 4 | E2B, Modal, Daytona, RunComfy |
| Guardrails / Safety (ADDENDUM) | 4 | LlamaGuard, NeMo Guardrails, Promptfoo, ProtectAI |
| Edge inference (hardware-as-a-service) | 4 | Cerebras, Groq, SambaNova, Etched |
| Data labeling / RLHF (ADDENDUM) | 4 | Scale AI, Surge HQ, Labelbox AI, Snorkel |
| **Total** | **92** | Dentro del rango 80-105 del SPEC |

---

## Lista seed por macroárea

### MACROÁREA 1: Inteligencia — LLMs frontier (24 modelos)

| ID canónico | Nombre | Proveedor | Tipo | Fuente primaria |
|---|---|---|---|---|
| gpt-5.5 | GPT-5.5 | OpenAI | propietario | Artificial Analysis `/data/llms/models` |
| gpt-5.5-mini | GPT-5.5 Mini | OpenAI | propietario | Artificial Analysis |
| gpt-5.4 | GPT-5.4 | OpenAI | propietario | Artificial Analysis |
| claude-opus-4.7 | Claude Opus 4.7 | Anthropic | propietario | Artificial Analysis |
| claude-sonnet-4.7 | Claude Sonnet 4.7 | Anthropic | propietario | Artificial Analysis |
| claude-haiku-4.5 | Claude Haiku 4.5 | Anthropic | propietario | Artificial Analysis |
| gemini-3.1-pro | Gemini 3.1 Pro | Google | propietario | Artificial Analysis |
| gemini-3.1-flash | Gemini 3.1 Flash | Google | propietario | Artificial Analysis |
| gemini-3-pro | Gemini 3 Pro | Google | propietario | Artificial Analysis |
| grok-4.3 | Grok 4.3 | xAI | propietario | Artificial Analysis |
| grok-4 | Grok 4 | xAI | propietario | Artificial Analysis |
| deepseek-v4 | DeepSeek V4 | DeepSeek | open-weights | Artificial Analysis + HF Open LLM |
| deepseek-v4-flash | DeepSeek V4 Flash | DeepSeek | open-weights | Artificial Analysis |
| deepseek-r1 | DeepSeek R1 | DeepSeek | open-weights | HF Open LLM Leaderboard |
| llama-4-maverick | Llama 4 Maverick | Meta | open-weights | HF Open LLM |
| llama-4-scout | Llama 4 Scout | Meta | open-weights | HF Open LLM |
| qwen-3-235b | Qwen 3 235B | Alibaba | open-weights | HF Open LLM |
| kimi-k2 | Kimi K2 | Moonshot | open-weights | HF Open LLM |
| kimi-k2.5 | Kimi K2.5 | Moonshot | open-weights | HF Open LLM |
| glm-4.7 | GLM 4.7 | Zhipu | open-weights | HF Open LLM |
| mistral-large-2 | Mistral Large 2 | Mistral | open-weights | HF Open LLM |
| mistral-medium-3 | Mistral Medium 3 | Mistral | propietario | Artificial Analysis |
| perplexity-sonar-pro | Perplexity Sonar Pro | Perplexity | propietario | Artificial Analysis |
| cohere-command-r-plus | Cohere Command R+ | Cohere | propietario | Artificial Analysis |

### MACROÁREA 2: Visión generativa — T2I + edición (16 modelos)

| ID canónico | Nombre | Proveedor | Tipo | Subcapacidades clave |
|---|---|---|---|---|
| flux-2 | Flux 2 | Black Forest Labs | propietario | fotorrealismo, texto-en-imagen |
| flux-1.1-pro-ultra | Flux 1.1 Pro Ultra | Black Forest Labs | propietario | fotorrealismo, prompt-adherence |
| flux-pro-kontext | Flux Pro Kontext | Black Forest Labs | propietario | edición |
| recraft-v4 | Recraft V4 | Recraft | propietario | logos, SVG, tipografía |
| recraft-v3 | Recraft V3 | Recraft | propietario | tipografía, posters |
| ideogram-3 | Ideogram 3.0 | Ideogram | propietario | texto-en-imagen |
| midjourney-v8 | Midjourney V8 | Midjourney | propietario | estilo artístico |
| nano-banana-pro | Nano Banana Pro | Google | propietario | imagen + edición |
| imagen-4 | Imagen 4 | Google | propietario | calidad cinemática |
| gpt-image-2 | GPT Image 2 | OpenAI | propietario | edición conversacional |
| dall-e-4 | DALL-E 4 | OpenAI | propietario | calidad general |
| stable-diffusion-3.5-large | Stable Diffusion 3.5 Large | Stability AI | open-weights | community |
| krea | Krea | Krea | propietario | renders arquitectónicos |
| leonardo-phoenix | Leonardo Phoenix | Leonardo | propietario | game art |
| firefly-3 | Adobe Firefly 3 | Adobe | propietario | enterprise |
| seedream-3 | Seedream 3 | ByteDance | propietario | calidad multilingüe |

### MACROÁREA 3: Video generativo — T2V + I2V (12 modelos)

| ID canónico | Nombre | Proveedor | Tipo |
|---|---|---|---|
| sora-2 | Sora 2 | OpenAI | propietario |
| veo-3 | Veo 3 | Google | propietario |
| veo-2 | Veo 2 | Google | propietario |
| kling-2 | Kling 2 | Kuaishou | propietario |
| runway-gen-4 | Runway Gen-4 | Runway | propietario |
| pika-2 | Pika 2 | Pika Labs | propietario |
| seedance-2 | Seedance 2.0 | ByteDance | propietario |
| luma-dream-machine | Luma Dream Machine 2 | Luma AI | propietario |
| minimax-hailuo-2 | MiniMax Hailuo 2 | MiniMax | propietario |
| hunyuan-video | HunyuanVideo | Tencent | open-weights |
| ltx-video | LTX Video | Lightricks | open-weights |
| wan-2.5 | Wan 2.5 | Alibaba | open-weights |

### MACROÁREA 4: Voz / Avatares (12 modelos)

| ID canónico | Nombre | Proveedor | Subcapacidad |
|---|---|---|---|
| elevenlabs-v3 | ElevenLabs V3 | ElevenLabs | TTS multivoice |
| elevenlabs-flash-v2.5 | ElevenLabs Flash 2.5 | ElevenLabs | TTS low-latency |
| heygen-avatar-v4 | HeyGen Avatar V4 | HeyGen | avatar full |
| argil-v2 | Argil V2 | Argil | avatar UGC |
| synthesia-express-2 | Synthesia Express 2 | Synthesia | avatar enterprise |
| captions-creator-3 | Captions Creator 3 | Captions | avatar móvil |
| d-id-talking-photo | D-ID Talking Photo | D-ID | foto parlante |
| hour-one-v3 | Hour One V3 | HourOne | avatar marketing |
| cartesia-sonic-2 | Cartesia Sonic 2 | Cartesia | TTS realtime |
| openai-tts-2 | OpenAI TTS 2 | OpenAI | TTS multivoice |
| google-tts-chirp-3 | Google TTS Chirp 3 | Google | TTS HD |
| assemblyai-universal-3 | AssemblyAI Universal 3 | AssemblyAI | STT |

### MACROÁREA 5: Audio / Música (6 modelos)

| ID canónico | Nombre | Proveedor |
|---|---|---|
| suno-v5 | Suno V5 | Suno |
| udio-v2 | Udio V2 | Udio |
| musicfx-pro | MusicFX Pro | Google |
| stable-audio-2.5 | Stable Audio 2.5 | Stability AI |
| beatoven-pro | Beatoven Pro | Beatoven |
| aiva-symphony | Aiva Symphony | Aiva |

### MACROÁREA 6: Embeddings y Vector DB (6, NUEVO) 

| ID canónico | Nombre | Proveedor |
|---|---|---|
| openai-text-embed-4 | text-embedding-4 | OpenAI |
| voyage-3.5 | voyage-3.5 | Voyage AI |
| cohere-embed-v4 | embed-v4 | Cohere |
| jina-embeddings-v4 | jina-embeddings-v4 | Jina AI |
| mxbai-embed-large-v2 | mxbai-embed-large-v2 | Mixedbread | open-weights |
| nomic-embed-text-v3 | nomic-embed-text-v3 | Nomic | open-weights |

### MACROÁREA 7: Code-execution / Sandboxes (4, NUEVO)

| ID canónico | Nombre | Proveedor |
|---|---|---|
| e2b-sandbox | E2B Sandbox | E2B |
| modal-sandbox | Modal Sandbox | Modal |
| daytona-workspace | Daytona Workspace | Daytona |
| runcomfy-runtime | RunComfy Runtime | RunComfy |

### MACROÁREA 8: Guardrails / Safety (4, NUEVO)

| ID canónico | Nombre | Proveedor |
|---|---|---|
| llamaguard-3 | LlamaGuard 3 | Meta |
| nemo-guardrails-v2 | NeMo Guardrails v2 | NVIDIA |
| promptfoo-eval | Promptfoo Eval | Promptfoo |
| protectai-guardian | ProtectAI Guardian | ProtectAI |

### MACROÁREA 9: Edge inference / Hardware (4, NUEVO)

| ID canónico | Nombre | Proveedor |
|---|---|---|
| cerebras-inference | Cerebras Inference | Cerebras |
| groq-cloud | Groq Cloud | Groq |
| sambanova-fast | SambaNova Fast | SambaNova |
| etched-sohu | Etched Sohu | Etched |

### MACROÁREA 10: Data labeling AI (4, NUEVO)

| ID canónico | Nombre | Proveedor |
|---|---|---|
| scale-ai-genai-labeling | Scale AI GenAI Labeling | Scale AI |
| surge-rlhf | Surge RLHF | Surge HQ |
| labelbox-ai | Labelbox AI | Labelbox |
| snorkel-foundation | Snorkel Foundation | Snorkel AI |

---

## Plan de seeding ejecutable (Sprint 86 / pseudo-código del seeder)

```python
# kernel/catastro/seeder.py
SEED_LIST = load_yaml("kernel/catastro/seeds/sprint86_seed.yaml")
# Lee la lista de arriba parseada como YAML

for entry in SEED_LIST:
    # 1. Buscar el modelo en la fuente primaria asignada
    raw_data = source_clients[entry.fuente_primaria].fetch(entry.id)
    
    # 2. Buscar en 1-2 fuentes secundarias
    secondary_data = [
        source_clients[s].fetch(entry.id)
        for s in entry.fuentes_secundarias
    ]
    
    # 3. Quorum Validator
    validated = quorum_validator.validate([raw_data, *secondary_data])
    if not validated.has_quorum:
        write_event("quorum_fallido", entry.id, validated.disagreements)
        continue
    
    # 4. Calcular Trono Score
    trono = compute_trono_score(validated)
    
    # 5. Insertar en catastro_modelos
    db.insert(catastro_modelos, {
        "id": entry.id,
        "nombre": entry.nombre,
        "proveedor": entry.proveedor,
        "macroarea": entry.macroarea,
        "dominios": entry.dominios,
        "subcapacidades": entry.subcapacidades,
        "tipo": entry.tipo,
        "licencia": entry.licencia,
        "data": validated.merged_data,  # JSONB
        "trono_score": trono,
        "fuentes_datos": entry.fuentes_datos,
        "quorum_alcanzado": True,
        "ultima_validacion": now()
    })
```

---

## Conclusión Tarea 4

**92 modelos seed identificados**, dentro del rango 80-105 del SPEC. Distribución balanceada: 24 LLMs (la macroárea más densa) y modelos representativos en las 9 macroáreas restantes (incluyendo las 5 nuevas del ADDENDUM).

**Cero datos hardcodeados de precio/Elo/latencia.** Solo IDs canónicos. La data viva la extrae el pipeline diario en runtime con Quorum Validator.

**Next step Sprint 86:** transformar este markdown en `kernel/catastro/seeds/sprint86_seed.yaml` con campos completos cuando arranque la implementación.

— [Hilo Manus Catastro]
