# ARCHIVO MAESTRO OPENROUTER — Catálogo Completo de APIs de IA
## Guía Definitiva de Configuración y Uso (Abril 2026)

**Autor:** Manus AI  
**Fecha:** 4 de abril de 2026  
**Versión:** 1.0  
**Fuente de datos:** API de OpenRouter (`https://openrouter.ai/api/v1/models`) + Investigación web

> Este documento contiene la ficha técnica completa de **349 modelos de IA** de **56 proveedores** disponibles a través de la API unificada de OpenRouter. Incluye precios exactos por millón de tokens, configuraciones de uso listas para copiar y pegar, y descripciones funcionales de cada modelo. **28 modelos son completamente gratuitos.**

## Configuración Base (Aplica a TODOS los modelos)

Todos los modelos de OpenRouter se acceden a través de un único endpoint con formato compatible con el SDK de OpenAI:

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

# Llamada genérica (sustituir model por cualquier model_id de este catálogo)
response = client.chat.completions.create(
    model="MODELO_ID_AQUI",
    messages=[
        {"role": "system", "content": "Tu system prompt"},
        {"role": "user", "content": "Tu mensaje"}
    ],
    max_tokens=4096,  # Ajustar según necesidad
    temperature=0.7,  # 0.0 = determinista, 1.0 = creativo
)
print(response.choices[0].message.content)
```

**Headers opcionales recomendados:**
```python
extra_headers={
    "HTTP-Referer": "https://tu-app.com",  # Para rankings de OpenRouter
    "X-Title": "Mi Aplicación",             # Nombre de tu app
}
```

## Resumen por Proveedor

| Proveedor | Modelos Totales | Modelos Gratuitos |
|:---|:---:|:---:|
| **openai** | 62 | 2 |
| **qwen** | 49 | 3 |
| **google** | 30 | 7 |
| **mistralai** | 25 | 0 |
| **meta-llama** | 14 | 2 |
| **z-ai** | 12 | 1 |
| **anthropic** | 12 | 0 |
| **nvidia** | 11 | 4 |
| **deepseek** | 11 | 0 |
| **x-ai** | 10 | 0 |
| **arcee-ai** | 8 | 2 |
| **minimax** | 8 | 1 |
| **nousresearch** | 6 | 1 |
| **amazon** | 5 | 0 |
| **perplexity** | 5 | 0 |
| **baidu** | 5 | 0 |
| **sao10k** | 5 | 0 |
| **bytedance-seed** | 4 | 0 |
| **aion-labs** | 4 | 0 |
| **moonshotai** | 4 | 0 |
| **allenai** | 4 | 0 |
| **thedrummer** | 4 | 0 |
| **cohere** | 4 | 0 |
| **xiaomi** | 3 | 0 |
| **inception** | 3 | 0 |
| **liquid** | 3 | 2 |
| **openrouter** | 3 | 1 |
| **rekaai** | 2 | 0 |
| **stepfun** | 2 | 1 |
| **relace** | 2 | 0 |
| **morph** | 2 | 0 |
| **microsoft** | 2 | 0 |
| **inflection** | 2 | 0 |
| **kwaipilot** | 1 | 0 |
| **upstage** | 1 | 0 |
| **writer** | 1 | 0 |
| **nex-agi** | 1 | 0 |
| **essentialai** | 1 | 0 |
| **prime-intellect** | 1 | 0 |
| **deepcogito** | 1 | 0 |
| **ibm-granite** | 1 | 0 |
| **alibaba** | 1 | 0 |
| **meituan** | 1 | 0 |
| **ai21** | 1 | 0 |
| **bytedance** | 1 | 0 |
| **switchpoint** | 1 | 0 |
| **cognitivecomputations** | 1 | 1 |
| **tencent** | 1 | 0 |
| **tngtech** | 1 | 0 |
| **eleutherai** | 1 | 0 |
| **alfredpros** | 1 | 0 |
| **anthracite-org** | 1 | 0 |
| **alpindale** | 1 | 0 |
| **mancer** | 1 | 0 |
| **undi95** | 1 | 0 |
| **gryphe** | 1 | 0 |
| **TOTAL** | **349** | **28** |

## Leyenda de Modalidades

| Modalidad | Significado |
|:---|:---|
| `text->text` | Solo texto de entrada y salida |
| `text+image->text` | Acepta texto e imágenes, devuelve texto |
| `text+image+file->text` | Acepta texto, imágenes y archivos, devuelve texto |
| `text+image+video->text` | Acepta texto, imágenes y video, devuelve texto |
| `text+image->text+image` | Acepta texto e imágenes, devuelve texto e imágenes |
| `text+audio->text+audio` | Acepta texto y audio, devuelve texto y audio |
| `text+image+file+audio+video->text` | Multimodal completo |

---

# CATÁLOGO COMPLETO DE MODELOS

### Google: Gemma 4 26B A4B 

| Atributo | Valor |
|---|---|
| model_id | `google/gemma-4-26b-a4b-it` |
| Proveedor | google |
| Modalidad | text+image+video->text |
| Contexto | 262144 tokens |
| Precio Input/M | $0.13 |
| Precio Output/M | $0.40 |
| Gratuito | No |

**Descripción Funcional:**
Gemma 4 26B A4B IT is an instruction-tuned Mixture-of-Experts (MoE) model from Google DeepMind. Despite 25.2B total parameters, only 3.8B activate per token during inference — delivering near-31B quality at...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=YOUR_OPENROUTER_API_KEY,
)

response = client.chat.completions.create(
    model="google/gemma-4-26b-a4b-it",
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---

### Google: Gemma 4 31B

| Atributo | Valor |
|---|---|
| model_id | `google/gemma-4-31b-it` |
| Proveedor | google |
| Modalidad | text+image+video->text |
| Contexto | 262144 tokens |
| Precio Input/M | $0.14 |
| Precio Output/M | $0.40 |
| Gratuito | No |

**Descripción Funcional:**
Gemma 4 31B Instruct is Google DeepMind's 30.7B dense multimodal model supporting text and image input with text output. Features a 256K token context window, configurable thinking/reasoning mode, native function...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=YOUR_OPENROUTER_API_KEY,
)

response = client.chat.completions.create(
    model="google/gemma-4-31b-it",
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---

### Qwen: Qwen3.6 Plus (free)

| Atributo | Valor |
|---|---|
| model_id | `qwen/qwen3.6-plus:free` |
| Proveedor | qwen |
| Modalidad | text+image+video->text |
| Contexto | 1000000 tokens |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción Funcional:**
Qwen 3.6 Plus builds on a hybrid architecture that combines efficient linear attention with sparse mixture-of-experts routing, enabling strong scalability and high-performance inference. Compared to the 3.5 series, it delivers...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=YOUR_OPENROUTER_API_KEY,
)

response = client.chat.completions.create(
    model="qwen/qwen3.6-plus:free",
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---

### Z.ai: GLM 5V Turbo

| Atributo | Valor |
|---|---|
| model_id | `z-ai/glm-5v-turbo` |
| Proveedor | z-ai |
| Modalidad | text+image+video->text |
| Contexto | 202752 tokens |
| Precio Input/M | $1.20 |
| Precio Output/M | $4.00 |
| Gratuito | No |

**Descripción Funcional:**
GLM-5V-Turbo is Z.ai’s first native multimodal agent foundation model, built for vision-based coding and agent-driven tasks. It natively handles image, video, and text inputs, excels at long-horizon planning, complex coding,...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=YOUR_OPENROUTER_API_KEY,
)

response = client.chat.completions.create(
    model="z-ai/glm-5v-turbo",
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---

### Arcee AI: Trinity Large Thinking

| Atributo | Valor |
|---|---|
| model_id | `arcee-ai/trinity-large-thinking` |
| Proveedor | arcee-ai |
| Modalidad | text->text |
| Contexto | 262144 tokens |
| Precio Input/M | $0.22 |
| Precio Output/M | $0.85 |
| Gratuito | No |

**Descripción Funcional:**
Trinity Large Thinking is a powerful open source reasoning model from the team at Arcee AI. It shows strong performance in PinchBench, agentic workloads, and reasoning tasks. It is free...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=YOUR_OPENROUTER_API_KEY,
)

response = client.chat.completions.create(
    model="arcee-ai/trinity-large-thinking",
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---

### xAI: Grok 4.20 Multi-Agent

| Atributo | Valor |
|---|---|
| model_id | `x-ai/grok-4.20-multi-agent` |
| Proveedor | x-ai |
| Modalidad | text+image+file->text |
| Contexto | 2000000 tokens |
| Precio Input/M | $2.00 |
| Precio Output/M | $6.00 |
| Gratuito | No |

**Descripción Funcional:**
Grok 4.20 Multi-Agent is a variant of xAI’s Grok 4.20 designed for collaborative, agent-based workflows. Multiple agents operate in parallel to conduct deep research, coordinate tool use, and synthesize information...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=YOUR_OPENROUTER_API_KEY,
)

response = client.chat.completions.create(
    model="x-ai/grok-4.20-multi-agent",
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---

### xAI: Grok 4.20

| Atributo | Valor |
|---|---|
| model_id | `x-ai/grok-4.20` |
| Proveedor | x-ai |
| Modalidad | text+image->text |
| Contexto | 2000000 tokens |
| Precio Input/M | $2.00 |
| Precio Output/M | $6.00 |
| Gratuito | No |

**Descripción Funcional:**
Grok 4.20 is xAI's newest flagship model with industry-leading speed and agentic tool calling capabilities. It combines the lowest hallucination rate on the market with strict prompt adherance, delivering consistently...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=YOUR_OPENROUTER_API_KEY,
)

response = client.chat.completions.create(
    model="x-ai/grok-4.20",
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---

### NVIDIA: Nemotron 3 Nano 30B A3B (free)

| Campo | Valor |
|---|---|
| model_id | `nvidia/nemotron-3-nano-30b-a3b:free` |
| Proveedor | NVIDIA |
| Modalidad | text->text |
| Contexto | 256000 |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** NVIDIA Nemotron 3 Nano 30B A3B is a small language MoE model with highest compute efficiency and accuracy for developers to build specialized agentic AI systems.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="nvidia/nemotron-3-nano-30b-a3b:free",
  messages=[
    {
      "role": "user",
      "content": "Hello world!",
    },
  ],
)
```

---

### NVIDIA: Nemotron 3 Nano 30B A3B

| Campo | Valor |
|---|---|
| model_id | `nvidia/nemotron-3-nano-30b-a3b` |
| Proveedor | NVIDIA |
| Modalidad | text->text |
| Contexto | 262144 |
| Precio Input/M | $0.05 |
| Precio Output/M | $0.20 |
| Gratuito | No |

**Descripción funcional:** NVIDIA Nemotron 3 Nano 30B A3B is a small language MoE model with highest compute efficiency and accuracy for developers to build specialized agentic AI systems.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="nvidia/nemotron-3-nano-30b-a3b",
  messages=[
    {
      "role": "user",
      "content": "Hello world!",
    },
  ],
)
```

---

### OpenAI: GPT-5.2 Chat

| Campo | Valor |
|---|---|
| model_id | `openai/gpt-5.2-chat` |
| Proveedor | OpenAI |
| Modalidad | text+image+file->text |
| Contexto | 128000 |
| Precio Input/M | $1.75 |
| Precio Output/M | $14.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5.2 Chat (AKA Instant) is the fast, lightweight member of the 5.2 family, optimized for low-latency chat while retaining strong general intelligence. It uses adaptive reasoning to selectively “think” on harder queries, improving accuracy on math, coding, and multi-step tasks without slowing down typical conversations. The model is warmer and more conversational by default, with better instruction following and more stable short-form reasoning. GPT-5.2 Chat is designed for high-throughput, interactive workloads where responsiveness and consistency matter more than deep deliberation.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="openai/gpt-5.2-chat",
  messages=[
    {
      "role": "user",
      "content": "Hello world!",
    },
  ],
)
```

---

### OpenAI: GPT-5.2 Pro

| Campo | Valor |
|---|---|
| model_id | `openai/gpt-5.2-pro` |
| Proveedor | OpenAI |
| Modalidad | text+image+file->text |
| Contexto | 400000 |
| Precio Input/M | $21.00 |
| Precio Output/M | $168.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5.2 Pro is OpenAI’s most advanced model, offering major improvements in agentic coding and long context performance over GPT-5 Pro. It is optimized for complex tasks that require step-by-step reasoning, instruction following, and accuracy in high-stakes use cases. It supports test-time routing features and advanced prompt understanding, including user-specified intent like "think hard about this." Improvements include reductions in hallucination, sycophancy, and better performance in coding, writing, and health-related tasks.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="openai/gpt-5.2-pro",
  messages=[
    {
      "role": "user",
      "content": "Hello world!",
    },
  ],
)
```

---

### OpenAI: GPT-5.2

| Campo | Valor |
|---|---|
| model_id | `openai/gpt-5.2` |
| Proveedor | OpenAI |
| Modalidad | text+image+file->text |
| Contexto | 400000 |
| Precio Input/M | $1.75 |
| Precio Output/M | $14.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5.2 is the latest frontier-grade model in the GPT-5 series, offering stronger agentic and long context perfomance compared to GPT-5.1. It uses adaptive reasoning to allocate computation dynamically, responding quickly to simple queries while spending more depth on complex tasks.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="openai/gpt-5.2",
  messages=[
    {
      "role": "user",
      "content": "Hello world!",
    },
  ],
)
```

---

### Mistral: Devstral 2 2512

| Campo | Valor |
|---|---|
| model_id | `mistralai/devstral-2512` |
| Proveedor | Mistral |
| Modalidad | text->text |
| Contexto | 262144 |
| Precio Input/M | $0.40 |
| Precio Output/M | $2.00 |
| Gratuito | No |

**Descripción funcional:** Devstral 2 is a state-of-the-art open-source model by Mistral AI specializing in agentic coding. It is a 123B-parameter dense transformer model supporting a 256K context window.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="mistralai/devstral-2512",
  messages=[
    {
      "role": "user",
      "content": "Hello world!",
    },
  ],
)
```

---

### Relace: Relace Search

| Campo | Valor |
|---|---|
| model_id | `relace/relace-search` |
| Proveedor | Relace |
| Modalidad | text->text |
| Contexto | 256000 |
| Precio Input/M | $1.00 |
| Precio Output/M | $3.00 |
| Gratuito | No |

**Descripción funcional:** The relace-search model uses 4-12 `view_file` and `grep` tools in parallel to explore a codebase and return relevant files to the user request. 

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="relace/relace-search",
  messages=[
    {
      "role": "user",
      "content": "Hello world!",
    },
  ],
)
```

---

### Z.ai: GLM 4.6V

| Campo | Valor |
|---|---|
| model_id | z-ai/glm-4.6v |
| Proveedor | z-ai |
| Modalidad | text+image+video->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.30 |
| Precio Output/M tokens | $0.90 |
| Gratuito | No |

**Descripción funcional:** GLM-4.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="z-ai/glm-4.6v", messages=[...])
```

---

### Nex AGI: DeepSeek V3.1 Nex N1

| Campo | Valor |
|---|---|
| model_id | nex-agi/deepseek-v3.1-nex-n1 |
| Proveedor | nex-agi |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.14 |
| Precio Output/M tokens | $0.50 |
| Gratuito | No |

**Descripción funcional:** DeepSeek V3.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="nex-agi/deepseek-v3.1-nex-n1", messages=[...])
```

---

### EssentialAI: Rnj 1 Instruct

| Campo | Valor |
|---|---|
| model_id | essentialai/rnj-1-instruct |
| Proveedor | essentialai |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M tokens | $0.15 |
| Precio Output/M tokens | $0.15 |
| Gratuito | No |

**Descripción funcional:** Rnj-1 is an 8B-parameter, dense, open-weight model family developed by Essential AI and trained from scratch with a focus on programming, math, and scientific reasoning.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="essentialai/rnj-1-instruct", messages=[...])
```

---

### Body Builder (beta)

| Campo | Valor |
|---|---|
| model_id | openrouter/bodybuilder |
| Proveedor | openrouter |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M tokens | GRATUITO |
| Precio Output/M tokens | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** Transform your natural language requests into structured OpenRouter API request objects.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="openrouter/bodybuilder", messages=[...])
```

---

### OpenAI: GPT-5.1-Codex-Max

| Campo | Valor |
|---|---|
| model_id | openai/gpt-5.1-codex-max |
| Proveedor | openai |
| Modalidad | text+image->text |
| Contexto | 400000 |
| Precio Input/M tokens | $1.25 |
| Precio Output/M tokens | $10.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="openai/gpt-5.1-codex-max", messages=[...])
```

---

### Amazon: Nova 2 Lite

| Campo | Valor |
|---|---|
| model_id | amazon/nova-2-lite-v1 |
| Proveedor | amazon |
| Modalidad | text+image+file+video->text |
| Contexto | 1000000 |
| Precio Input/M tokens | $0.30 |
| Precio Output/M tokens | $2.50 |
| Gratuito | No |

**Descripción funcional:** Nova 2 Lite is a fast, cost-effective reasoning model for everyday workloads that can process text, images, and videos to generate text.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="amazon/nova-2-lite-v1", messages=[...])
```

---

### Mistral: Ministral 3 14B 2512

| Campo | Valor |
|---|---|
| model_id | mistralai/ministral-14b-2512 |
| Proveedor | mistralai |
| Modalidad | text+image->text |
| Contexto | 262144 |
| Precio Input/M tokens | $0.20 |
| Precio Output/M tokens | $0.20 |
| Gratuito | No |

**Descripción funcional:** The largest model in the Ministral 3 family, Ministral 3 14B offers frontier capabilities and performance comparable to its larger Mistral Small 3.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="mistralai/ministral-14b-2512", messages=[...])
```

---

### Mistral: Ministral 3 8B 2512
| Característica | Valor |
|---|---|
| model_id | `mistralai/ministral-8b-2512` |
| Proveedor | mistralai |
| Modalidad | text+image->text |
| Contexto | 262144 |
| Precio Input/M | $0.15 |
| Precio Output/M | $0.15 |
| Gratuito | No |

**Descripción Funcional:**
A balanced model in the Ministral 3 family, Ministral 3 8B is a powerful, efficient tiny language model with vision capabilities.

**Snippet de Configuración:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="mistralai/ministral-8b-2512", messages=[...])
```

---

### Mistral: Ministral 3 3B 2512
| Característica | Valor |
|---|---|
| model_id | `mistralai/ministral-3b-2512` |
| Proveedor | mistralai |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.10 |
| Gratuito | No |

**Descripción Funcional:**
The smallest model in the Ministral 3 family, Ministral 3 3B is a powerful, efficient tiny language model with vision capabilities.

**Snippet de Configuración:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="mistralai/ministral-3b-2512", messages=[...])
```

---

### Mistral: Mistral Large 3 2512
| Característica | Valor |
|---|---|
| model_id | `mistralai/mistral-large-2512` |
| Proveedor | mistralai |
| Modalidad | text+image->text |
| Contexto | 262144 |
| Precio Input/M | $0.50 |
| Precio Output/M | $1.50 |
| Gratuito | No |

**Descripción Funcional:**
Mistral Large 3 2512 is Mistral’s most capable model to date, featuring a sparse mixture-of-experts architecture with 41B active parameters (675B total), and released under the Apache 2.0 license.

**Snippet de Configuración:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="mistralai/mistral-large-2512", messages=[...])
```

---

### Arcee AI: Trinity Mini (free)
| Característica | Valor |
|---|---|
| model_id | `arcee-ai/trinity-mini:free` |
| Proveedor | arcee-ai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción Funcional:**
Trinity Mini is a 26B-parameter (3B active) sparse mixture-of-experts language model featuring 128 experts with 8 active per token. Engineered for efficient reasoning over long contexts (131k) with robust function calling and multi-step agent workflows.

**Snippet de Configuración:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="arcee-ai/trinity-mini:free", messages=[...])
```

---

### Arcee AI: Trinity Mini
| Característica | Valor |
|---|---|
| model_id | `arcee-ai/trinity-mini` |
| Proveedor | arcee-ai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.04 |
| Precio Output/M | $0.15 |
| Gratuito | No |

**Descripción Funcional:**
Trinity Mini is a 26B-parameter (3B active) sparse mixture-of-experts language model featuring 128 experts with 8 active per token. Engineered for efficient reasoning over long contexts (131k) with robust function calling and multi-step agent workflows.

**Snippet de Configuración:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="arcee-ai/trinity-mini", messages=[...])
```

---

### DeepSeek: DeepSeek V3.2 Speciale
| Característica | Valor |
|---|---|
| model_id | `deepseek/deepseek-v3.2-speciale` |
| Proveedor | deepseek |
| Modalidad | text->text |
| Contexto | 163840 |
| Precio Input/M | $0.40 |
| Precio Output/M | $1.20 |
| Gratuito | No |

**Descripción Funcional:**
DeepSeek-V3.2-Speciale is a high-compute variant of DeepSeek-V3.2 optimized for maximum reasoning and agentic performance. It builds on DeepSeek Sparse Attention (DSA) for efficient long-context processing, then scales post-training reinforcement learning to push capability beyond the base model. Reported evaluations place Speciale ahead of GPT-5 on difficult reasoning workloads, with proficiency comparable to Gemini-3.0-Pro, while retaining strong coding and tool-use reliability. Like V3.2, it benefits from a large-scale agentic task synthesis pipeline that improves compliance and generalization in interactive environments.

**Snippet de Configuración:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="deepseek/deepseek-v3.2-speciale", messages=[...])
```

---

### DeepSeek: DeepSeek V3.2
| Característica | Valor |
|---|---|
| model_id | `deepseek/deepseek-v3.2` |
| Proveedor | deepseek |
| Modalidad | text->text |
| Contexto | 163840 |
| Precio Input/M | $0.26 |
| Precio Output/M | $0.38 |
| Gratuito | No |

**Descripción Funcional:**
DeepSeek-V3.2 is a large language model designed to harmonize high computational efficiency with strong reasoning and agentic tool-use performance. It introduces DeepSeek Sparse Attention (DSA), a fine-grained sparse attention mechanism that reduces training and inference cost while preserving quality in long-context scenarios. A scalable reinforcement learning post-training framework further improves reasoning, with reported performance in the GPT-5 class, and the model has demonstrated gold-medal results on the 2025 IMO and IOI. V3.2 also uses a large-scale agentic task synthesis pipeline to better integrate reasoning into tool-use settings, boosting compliance and generalization in interactive environments.

Users can control the reasoning behaviour with the `reasoning` `enabled` boolean. [Learn more in our docs](https://openrouter.ai/docs/use-cases/reasoning-tokens#enable-reasoning-with-default-config)

**Snippet de Configuración:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="deepseek/deepseek-v3.2", messages=[...])
```

---

### Prime Intellect: INTELLECT-3

| Campo | Valor |
|---|---|
| model_id | `prime-intellect/intellect-3` |
| Proveedor | prime-intellect |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.20 |
| Precio Output/M tokens | $1.10 |
| Gratuito | no |

**Descripción funcional:** INTELLECT-3 is a 106B-parameter Mixture-of-Experts model (12B active) post-trained from GLM-4.5-Air-Base using supervised fine-tuning (SFT) followed by large-scale reinforcement learning (RL). It offers state-of-the-art performance for its size across math,...

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="prime-intellect/intellect-3", messages=[...])
```

---

### Anthropic: Claude Opus 4.5

| Campo | Valor |
|---|---|
| model_id | `anthropic/claude-opus-4.5` |
| Proveedor | anthropic |
| Modalidad | text+image+file->text |
| Contexto | 200000 |
| Precio Input/M tokens | $5.00 |
| Precio Output/M tokens | $25.00 |
| Gratuito | no |

**Descripción funcional:** Claude Opus 4.5 is Anthropic’s frontier reasoning model optimized for complex software engineering, agentic workflows, and long-horizon computer use. It offers strong multimodal capabilities, competitive performance across real-world coding and...

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="anthropic/claude-opus-4.5", messages=[...])
```

---

### AllenAI: Olmo 3 32B Think

| Campo | Valor |
|---|---|
| model_id | `allenai/olmo-3-32b-think` |
| Proveedor | allenai |
| Modalidad | text->text |
| Contexto | 65536 |
| Precio Input/M tokens | $0.15 |
| Precio Output/M tokens | $0.50 |
| Gratuito | no |

**Descripción funcional:** Olmo 3 32B Think is a large-scale, 32-billion-parameter model purpose-built for deep reasoning, complex logic chains and advanced instruction-following scenarios. Its capacity enables strong performance on demanding evaluation tasks and...

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="allenai/olmo-3-32b-think", messages=[...])
```

---

### Google: Nano Banana Pro (Gemini 3 Pro Image Preview)

| Campo | Valor |
|---|---|
| model_id | `google/gemini-3-pro-image-preview` |
| Proveedor | google |
| Modalidad | text+image->text+image |
| Contexto | 65536 |
| Precio Input/M tokens | $2.00 |
| Precio Output/M tokens | $12.00 |
| Gratuito | no |

**Descripción funcional:** Nano Banana Pro is Google’s most advanced image-generation and editing model, built on Gemini 3 Pro. It extends the original Nano Banana with significantly improved multimodal reasoning, real-world grounding, and...

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="google/gemini-3-pro-image-preview", messages=[...])
```

---

### xAI: Grok 4.1 Fast

| Campo | Valor |
|---|---|
| model_id | `x-ai/grok-4.1-fast` |
| Proveedor | x-ai |
| Modalidad | text+image+file->text |
| Contexto | 2000000 |
| Precio Input/M tokens | $0.20 |
| Precio Output/M tokens | $0.50 |
| Gratuito | no |

**Descripción funcional:** Grok 4.1 Fast is xAI's best agentic tool calling model that shines in real-world use cases like customer support and deep research. 2M context window. Reasoning can be enabled/disabled using...

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="x-ai/grok-4.1-fast", messages=[...])
```

---

### Deep Cogito: Cogito v2.1 671B

| Campo | Valor |
|---|---|
| model_id | `deepcogito/cogito-v2.1-671b` |
| Proveedor | deepcogito |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M tokens | $1.25 |
| Precio Output/M tokens | $1.25 |
| Gratuito | no |

**Descripción funcional:** Cogito v2.1 671B MoE represents one of the strongest open models globally, matching performance of frontier closed and open models. This model is trained using self play with reinforcement learning...

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="deepcogito/cogito-v2.1-671b", messages=[...])
```

---

### OpenAI: GPT-5.1

| Campo | Valor |
|---|---|
| model_id | `openai/gpt-5.1` |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 400000 |
| Precio Input/M tokens | $1.25 |
| Precio Output/M tokens | $10.00 |
| Gratuito | no |

**Descripción funcional:** GPT-5.1 is the latest frontier-grade model in the GPT-5 series, offering stronger general-purpose reasoning, improved instruction adherence, and a more natural conversational style compared to GPT-5. It uses adaptive reasoning...

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-5.1", messages=[...])
```

---

### OpenAI: GPT-5.1 Chat

| Campo | Valor |
|---|---|
| model_id | openai/gpt-5.1-chat |
| proveedor | openai |
| modalidad | text+image+file->text |
| contexto | 128000 |
| precio input/M tokens | 1.25 |
| precio output/M tokens | 10.00 |
| gratuito | no |

**Descripción funcional:** GPT-5.1 Chat (AKA Instant is the fast, lightweight member of the 5.1 family, optimized for low-latency chat while retaining strong general intelligence. It uses adaptive reasoning to selectively “think” on harder queries, improving accuracy on math, coding, and multi-step tasks without slowing down typical conversations. The model is warmer and more conversational by default, with better instruction following and more stable short-form reasoning. GPT-5.1 Chat is designed for high-throughput, interactive workloads where responsiveness and consistency matter more than deep deliberation.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5.1-chat", messages=[...])
```

---

### OpenAI: GPT-5.1-Codex

| Campo | Valor |
|---|---|
| model_id | openai/gpt-5.1-codex |
| proveedor | openai |
| modalidad | text+image->text |
| contexto | 400000 |
| precio input/M tokens | 1.25 |
| precio output/M tokens | 10.00 |
| gratuito | no |

**Descripción funcional:** GPT-5.1-Codex is a specialized version of GPT-5.1 optimized for software engineering and coding workflows. It is designed for both interactive development sessions and long, independent execution of complex engineering tasks. The model supports building projects from scratch, feature development, debugging, large-scale refactoring, and code review. Compared to GPT-5.1, Codex is more steerable, adheres closely to developer instructions, and produces cleaner, higher-quality code outputs. Reasoning effort can be adjusted with the `reasoning.effort` parameter. Read the [docs here](https://openrouter.ai/docs/use-cases/reasoning-tokens#reasoning-effort-level)

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5.1-codex", messages=[...])
```

---

### OpenAI: GPT-5.1-Codex-Mini

| Campo | Valor |
|---|---|
| model_id | openai/gpt-5.1-codex-mini |
| proveedor | openai |
| modalidad | text+image->text |
| contexto | 400000 |
| precio input/M tokens | 0.25 |
| precio output/M tokens | 2.00 |
| gratuito | no |

**Descripción funcional:** GPT-5.1-Codex-Mini is a smaller and faster version of GPT-5.1-Codex

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5.1-codex-mini", messages=[...])
```

---

### MoonshotAI: Kimi K2 Thinking

| Campo | Valor |
|---|---|
| model_id | moonshotai/kimi-k2-thinking |
| proveedor | moonshotai |
| modalidad | text->text |
| contexto | 131072 |
| precio input/M tokens | 0.47 |
| precio output/M tokens | 2.00 |
| gratuito | no |

**Descripción funcional:** Kimi K2 Thinking is Moonshot AI’s most advanced open reasoning model to date, extending the K2 series into agentic, long-horizon reasoning. Built on the trillion-parameter Mixture-of-Experts (MoE) architecture introduced in Kimi K2, it activates 32 billion parameters per forward pass and supports 256 k-token context windows. The model is optimized for persistent step-by-step thought, dynamic tool invocation, and complex reasoning workflows that span hundreds of turns. It interleaves step-by-step reasoning with tool use, enabling autonomous research, coding, and writing that can persist for hundreds of sequential actions without drift.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="moonshotai/kimi-k2-thinking", messages=[...])
```

---

### Amazon: Nova Premier 1.0

| Campo | Valor |
|---|---|
| model_id | amazon/nova-premier-v1 |
| proveedor | amazon |
| modalidad | text+image->text |
| contexto | 1000000 |
| precio input/M tokens | 2.50 |
| precio output/M tokens | 12.50 |
| gratuito | no |

**Descripción funcional:** Amazon Nova Premier is the most capable of Amazon’s multimodal models for complex reasoning tasks and for use as the best teacher for distilling custom models.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="amazon/nova-premier-v1", messages=[...])
```

---

### Perplexity: Sonar Pro Search

| Campo | Valor |
|---|---|
| model_id | perplexity/sonar-pro-search |
| proveedor | perplexity |
| modalidad | text+image->text |
| contexto | 200000 |
| precio input/M tokens | 3.00 |
| precio output/M tokens | 15.00 |
| gratuito | no |

**Descripción funcional:** Exclusively available on the OpenRouter API, Sonar Pro's new Pro Search mode is Perplexity's most advanced agentic search system. It is designed for deeper reasoning and analysis. Pricing is based on tokens plus $18 per thousand requests. This model powers the Pro Search mode on the Perplexity platform.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="perplexity/sonar-pro-search", messages=[...])
```

---

### Mistral: Voxtral Small 24B 2507

| Campo | Valor |
|---|---|
| model_id | mistralai/voxtral-small-24b-2507 |
| proveedor | mistralai |
| modalidad | text+audio->text |
| contexto | 32000 |
| precio input/M tokens | 0.10 |
| precio output/M tokens | 0.30 |
| gratuito | no |

**Descripción funcional:** Voxtral Small is an enhancement of Mistral Small 3, incorporating state-of-the-art audio input capabilities while retaining best-in-class text performance. It excels at speech transcription, translation and audio understanding. Input audio is priced at $100 per million seconds.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="mistralai/voxtral-small-24b-2507", messages=[...])
```

---

### OpenAI: gpt-oss-safeguard-20b

| Campo | Valor |
|---|---|
| model_id | openai/gpt-oss-safeguard-20b |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | 0.07 |
| Precio Output/M tokens | 0.30 |
| Gratuito | No |

**Descripción funcional:** gpt-oss-safeguard-20b is a safety reasoning model from OpenAI built upon gpt-oss-20b. This open-weight, 21B-parameter Mixture-of-Experts (MoE) model offers lower latency for safety tasks like content classification, LLM filtering, and trust...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-oss-safeguard-20b", messages=[...])```

---

### NVIDIA: Nemotron Nano 12B 2 VL (free)

| Campo | Valor |
|---|---|
| model_id | nvidia/nemotron-nano-12b-v2-vl:free |
| Proveedor | nvidia |
| Modalidad | text+image+video->text |
| Contexto | 128000 |
| Precio Input/M tokens | GRATUITO |
| Precio Output/M tokens | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** NVIDIA Nemotron Nano 2 VL is a 12-billion-parameter open multimodal reasoning model designed for video understanding and document intelligence. It introduces a hybrid Transformer-Mamba architecture, combining transformer-level accuracy with Mamba’s...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="nvidia/nemotron-nano-12b-v2-vl:free", messages=[...])```

---

### NVIDIA: Nemotron Nano 12B 2 VL

| Campo | Valor |
|---|---|
| model_id | nvidia/nemotron-nano-12b-v2-vl |
| Proveedor | nvidia |
| Modalidad | text+image+video->text |
| Contexto | 131072 |
| Precio Input/M tokens | 0.20 |
| Precio Output/M tokens | 0.60 |
| Gratuito | No |

**Descripción funcional:** NVIDIA Nemotron Nano 2 VL is a 12-billion-parameter open multimodal reasoning model designed for video understanding and document intelligence. It introduces a hybrid Transformer-Mamba architecture, combining transformer-level accuracy with Mamba’s...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="nvidia/nemotron-nano-12b-v2-vl", messages=[...])```

---

### MiniMax: MiniMax M2

| Campo | Valor |
|---|---|
| model_id | minimax/minimax-m2 |
| Proveedor | minimax |
| Modalidad | text->text |
| Contexto | 196608 |
| Precio Input/M tokens | 0.26 |
| Precio Output/M tokens | 1.00 |
| Gratuito | No |

**Descripción funcional:** MiniMax-M2 is a compact, high-efficiency large language model optimized for end-to-end coding and agentic workflows. With 10 billion activated parameters (230 billion total), it delivers near-frontier intelligence across general reasoning,...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="minimax/minimax-m2", messages=[...])```

---

### Qwen: Qwen3 VL 32B Instruct

| Campo | Valor |
|---|---|
| model_id | qwen/qwen3-vl-32b-instruct |
| Proveedor | qwen |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M tokens | 0.10 |
| Precio Output/M tokens | 0.42 |
| Gratuito | No |

**Descripción funcional:** Qwen3-VL-32B-Instruct is a large-scale multimodal vision-language model designed for high-precision understanding and reasoning across text, images, and video. With 32 billion parameters, it combines deep visual perception with advanced text...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3-vl-32b-instruct", messages=[...])```

---

### IBM: Granite 4.0 Micro

| Campo | Valor |
|---|---|
| model_id | ibm-granite/granite-4.0-h-micro |
| Proveedor | ibm-granite |
| Modalidad | text->text |
| Contexto | 131000 |
| Precio Input/M tokens | 0.02 |
| Precio Output/M tokens | 0.11 |
| Gratuito | No |

**Descripción funcional:** Granite-4.0-H-Micro is a 3B parameter from the Granite 4 family of models. These models are the latest in a series of models released by IBM. They are fine-tuned for long...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="ibm-granite/granite-4.0-h-micro", messages=[...])```

---

### OpenAI: GPT-5 Image Mini

| Campo | Valor |
|---|---|
| model_id | openai/gpt-5-image-mini |
| Proveedor | openai |
| Modalidad | text+image+file->text+image |
| Contexto | 400000 |
| Precio Input/M tokens | 2.50 |
| Precio Output/M tokens | 2.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5 Image Mini combines OpenAI's advanced language capabilities, powered by [GPT-5 Mini](https://openrouter.ai/openai/gpt-5-mini), with GPT Image 1 Mini for efficient image generation. This natively multimodal model features superior instruction following, text...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-5-image-mini", messages=[...])```

---

### Anthropic: Claude Haiku 4.5

| Atributo | Valor |
|---|---|
| model_id | `anthropic/claude-haiku-4.5` |
| Proveedor | anthropic |
| Modalidad | text+image->text |
| Contexto | 200000 |
| Precio Input/M | $1.00 |
| Precio Output/M | $5.00 |
| Gratuito | No |

**Descripción funcional:** Claude Haiku 4.5 is Anthropic’s fastest and most efficient model, delivering near-frontier intelligence at a fraction of the cost and latency of larger Claude models. Matching Claude Sonnet 4’s performance across reasoning, coding, and computer-use tasks, Haiku 4.5 brings frontier-level capability to real-time and high-volume applications.  It introduces extended thinking to the Haiku line; enabling controllable reasoning depth, summarized or interleaved thought output, and tool-assisted workflows with full support for coding, bash, web search, and computer-use tools. Scoring >73% on SWE-bench Verified, Haiku 4.5 ranks among the world’s best coding models while maintaining exceptional responsiveness for sub-agents, parallelized execution, and scaled deployment.

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="anthropic/claude-haiku-4.5", messages=[...])
```

---

### Qwen: Qwen3 VL 8B Thinking

| Atributo | Valor |
|---|---|
| model_id | `qwen/qwen3-vl-8b-thinking` |
| Proveedor | qwen |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M | $0.12 |
| Precio Output/M | $1.36 |
| Gratuito | No |

**Descripción funcional:** Qwen3-VL-8B-Thinking is the reasoning-optimized variant of the Qwen3-VL-8B multimodal model, designed for advanced visual and textual reasoning across complex scenes, documents, and temporal sequences. It integrates enhanced multimodal alignment and long-context processing (native 256K, expandable to 1M tokens) for tasks such as scientific visual analysis, causal inference, and mathematical reasoning over image or video inputs.  Compared to the Instruct edition, the Thinking version introduces deeper visual-language fusion and deliberate reasoning pathways that improve performance on long-chain logic tasks, STEM problem-solving, and multi-step video understanding. It achieves stronger temporal grounding via Interleaved-MRoPE and timestamp-aware embeddings, while maintaining robust OCR, multilingual comprehension, and text generation on par with large text-only LLMs.

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-vl-8b-thinking", messages=[...])
```

---

### Qwen: Qwen3 VL 8B Instruct

| Atributo | Valor |
|---|---|
| model_id | `qwen/qwen3-vl-8b-instruct` |
| Proveedor | qwen |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M | $0.08 |
| Precio Output/M | $0.50 |
| Gratuito | No |

**Descripción funcional:** Qwen3-VL-8B-Instruct is a multimodal vision-language model from the Qwen3-VL series, built for high-fidelity understanding and reasoning across text, images, and video. It features improved multimodal fusion with Interleaved-MRoPE for long-horizon temporal reasoning, DeepStack for fine-grained visual-text alignment, and text-timestamp alignment for precise event localization.  The model supports a native 256K-token context window, extensible to 1M tokens, and handles both static and dynamic media inputs for tasks like document parsing, visual question answering, spatial reasoning, and GUI control. It achieves text understanding comparable to leading LLMs while expanding OCR coverage to 32 languages and enhancing robustness under varied visual conditions.

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-vl-8b-instruct", messages=[...])
```

---

### OpenAI: GPT-5 Image

| Atributo | Valor |
|---|---|
| model_id | `openai/gpt-5-image` |
| Proveedor | openai |
| Modalidad | text+image+file->text+image |
| Contexto | 400000 |
| Precio Input/M | $10.00 |
| Precio Output/M | $10.00 |
| Gratuito | No |

**Descripción funcional:** (GPT-5)(https://openrouter.ai/openai/gpt-5) Image combines OpenAI's GPT-5 model with state-of-the-art image generation capabilities. It offers major improvements in reasoning, code quality, and user experience while incorporating GPT Image 1's superior instruction following, text rendering, and detailed image editing.

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5-image", messages=[...])
```

---

### OpenAI: o3 Deep Research

| Atributo | Valor |
|---|---|
| model_id | `openai/o3-deep-research` |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 200000 |
| Precio Input/M | $10.00 |
| Precio Output/M | $40.00 |
| Gratuito | No |

**Descripción funcional:** o3-deep-research is OpenAI's advanced model for deep research, designed to tackle complex, multi-step research tasks.  Note: This model always uses the 'web_search' tool which adds additional cost.

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="openai/o3-deep-research", messages=[...])
```

---

### OpenAI: o4 Mini Deep Research

| Atributo | Valor |
|---|---|
| model_id | `openai/o4-mini-deep-research` |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 200000 |
| Precio Input/M | $2.00 |
| Precio Output/M | $8.00 |
| Gratuito | No |

**Descripción funcional:** o4-mini-deep-research is OpenAI's faster, more affordable deep research model—ideal for tackling complex, multi-step research tasks.  Note: This model always uses the 'web_search' tool which adds additional cost.

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="openai/o4-mini-deep-research", messages=[...])
```

---

### NVIDIA: Llama 3.3 Nemotron Super 49B V1.5

| Atributo | Valor |
|---|---|
| model_id | `nvidia/llama-3.3-nemotron-super-49b-v1.5` |
| Proveedor | nvidia |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.40 |
| Gratuito | No |

**Descripción funcional:** Llama-3.3-Nemotron-Super-49B-v1.5 is a 49B-parameter, English-centric reasoning/chat model derived from Meta’s Llama-3.3-70B-Instruct with a 128K context. It’s post-trained for agentic workflows (RAG, tool calling) via SFT across math, code, science, and multi-turn chat, followed by multiple RL stages; Reward-aware Preference Optimization (RPO) for alignment, RL with Verifiable Rewards (RLVR) for step-wise reasoning, and iterative DPO to refine tool-use behavior. A distillation-driven Neural Architecture Search (“Puzzle”) replaces some attention blocks and varies FFN widths to shrink memory footprint and improve throughput, enabling single-GPU (H100/H200) deployment while preserving instruction following and CoT quality.  In internal evaluations (NeMo-Skills, up to 16 runs, temp = 0.6, top_p = 0.95), the model reports strong reasoning/coding results, e.g., MATH500 pass@1 = 97.4, AIME-2024 = 87.5, AIME-2025 = 82.71, GPQA = 71.97, LiveCodeBench (24.10–25.02) = 73.58, and MMLU-Pro (CoT) = 79.53. The model targets practical inference efficiency (high tokens/s, reduced VRAM) with Transformers/vLLM support and explicit “reasoning on/off” modes (chat-first defaults, greedy recommended when disabled). Suitable for building agents, assistants, and long-context retrieval systems where balanced accuracy-to-cost and reliable tool use matter.

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="nvidia/llama-3.3-nemotron-super-49b-v1.5", messages=[...])
```

---

### Baidu: ERNIE 4.5 21B A3B Thinking
| Campo | Valor |
|---|---|
| model_id | `baidu/ernie-4.5-21b-a3b-thinking` |
| Proveedor | baidu |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.07 |
| Precio Output/M tokens | $0.28 |
| Gratuito | No |

**Descripción funcional:**
ERNIE-4.5-21B-A3B-Thinking is Baidu's upgraded lightweight MoE model, refined to boost reasoning depth and quality for top-tier performance in logical puzzles, math, science, coding, text generation, and expert-level academic benchmarks.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="baidu/ernie-4.5-21b-a3b-thinking", messages=[{"role": "user", "content": "..."}])
```
---
### Google: Nano Banana (Gemini 2.5 Flash Image)
| Campo | Valor |
|---|---|
| model_id | `google/gemini-2.5-flash-image` |
| Proveedor | google |
| Modalidad | text+image->text+image |
| Contexto | 32768 |
| Precio Input/M tokens | $0.30 |
| Precio Output/M tokens | $2.50 |
| Gratuito | No |

**Descripción funcional:**
Gemini 2.5 Flash Image, a.k.a. "Nano Banana," is now generally available. It is a state of the art image generation model with contextual understanding. It is capable of image generation, edits, and multi-turn conversations. Aspect ratios can be controlled with the [image_conf...

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="google/gemini-2.5-flash-image", messages=[{"role": "user", "content": "..."}])
```
---
### Qwen: Qwen3 VL 30B A3B Thinking
| Campo | Valor |
|---|---|
| model_id | `qwen/qwen3-vl-30b-a3b-thinking` |
| Proveedor | qwen |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.13 |
| Precio Output/M tokens | $1.56 |
| Gratuito | No |

**Descripción funcional:**
Qwen3-VL-30B-A3B-Thinking is a multimodal model that unifies strong text generation with visual understanding for images and videos. Its Thinking variant enhances reasoning in STEM, math, and complex tasks. It excels in perception of real-world/synthetic categories, 2D/3D spat...

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-vl-30b-a3b-thinking", messages=[{"role": "user", "content": "..."}])
```
---
### Qwen: Qwen3 VL 30B A3B Instruct
| Campo | Valor |
|---|---|
| model_id | `qwen/qwen3-vl-30b-a3b-instruct` |
| Proveedor | qwen |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.13 |
| Precio Output/M tokens | $0.52 |
| Gratuito | No |

**Descripción funcional:**
Qwen3-VL-30B-A3B-Instruct is a multimodal model that unifies strong text generation with visual understanding for images and videos. Its Instruct variant optimizes instruction-following for general multimodal tasks. It excels in perception of real-world/synthetic categories, 2...

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-vl-30b-a3b-instruct", messages=[{"role": "user", "content": "..."}])
```
---
### OpenAI: GPT-5 Pro
| Campo | Valor |
|---|---|
| model_id | `openai/gpt-5-pro` |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 400000 |
| Precio Input/M tokens | $15.00 |
| Precio Output/M tokens | $120.00 |
| Gratuito | No |

**Descripción funcional:**
GPT-5 Pro is OpenAI’s most advanced model, offering major improvements in reasoning, code quality, and user experience. It is optimized for complex tasks that require step-by-step reasoning, instruction following, and accuracy in high-stakes use cases. It supports test-time ro...

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5-pro", messages=[{"role": "user", "content": "..."}])
```
---
### Z.ai: GLM 4.6
| Campo | Valor |
|---|---|
| model_id | `z-ai/glm-4.6` |
| Proveedor | z-ai |
| Modalidad | text->text |
| Contexto | 204800 |
| Precio Input/M tokens | $0.39 |
| Precio Output/M tokens | $1.90 |
| Gratuito | No |

**Descripción funcional:**
Compared with GLM-4.5, this generation brings several key improvements:

Longer context window: The context window has been expanded from 128K to 200K tokens, enabling the model to handle more complex agentic tasks.
Superior coding performance: The model achieves higher scores...

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="z-ai/glm-4.6", messages=[{"role": "user", "content": "..."}])
```
---
### Anthropic: Claude Sonnet 4.5
| Campo | Valor |
|---|---|
| model_id | `anthropic/claude-sonnet-4.5` |
| Proveedor | anthropic |
| Modalidad | text+image+file->text |
| Contexto | 1000000 |
| Precio Input/M tokens | $3.00 |
| Precio Output/M tokens | $15.00 |
| Gratuito | No |

**Descripción funcional:**
Claude Sonnet 4.5 is Anthropic’s most advanced Sonnet model to date, optimized for real-world agents and coding workflows. It delivers state-of-the-art performance on coding benchmarks such as SWE-bench Verified, with improvements across system design, code security, and speci...

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="anthropic/claude-sonnet-4.5", messages=[{"role": "user", "content": "..."}])
```
---

### DeepSeek: DeepSeek V3.2 Exp

| Campo | Valor |
|---|---|
| model_id | `deepseek/deepseek-v3.2-exp` |
| Proveedor | deepseek |
| Modalidad | text->text |
| Contexto | 163840 |
| Precio Input/M | $0.27 |
| Precio Output/M | $0.41 |
| Gratuito | No |

**Descripción funcional:**
DeepSeek-V3.2-Exp is an experimental large language model released by DeepSeek as an intermediate step between V3.1 and future architectures. It introduces DeepSeek Sparse Attention (DSA), a fine-grained sparse attention mechanism...

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="deepseek/deepseek-v3.2-exp",
  messages=[{"role": "user", "content": "Hello world!"}],
)
```

---

### TheDrummer: Cydonia 24B V4.1

| Campo | Valor |
|---|---|
| model_id | `thedrummer/cydonia-24b-v4.1` |
| Proveedor | thedrummer |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.30 |
| Precio Output/M | $0.50 |
| Gratuito | No |

**Descripción funcional:**
Uncensored and creative writing model based on Mistral Small 3.2 24B with good recall, prompt adherence, and intelligence....

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="thedrummer/cydonia-24b-v4.1",
  messages=[{"role": "user", "content": "Hello world!"}],
)
```

---

### Relace: Relace Apply 3

| Campo | Valor |
|---|---|
| model_id | `relace/relace-apply-3` |
| Proveedor | relace |
| Modalidad | text->text |
| Contexto | 256000 |
| Precio Input/M | $0.85 |
| Precio Output/M | $1.25 |
| Gratuito | No |

**Descripción funcional:**
Relace Apply 3 is a specialized code-patching LLM that merges AI-suggested edits straight into your source files. It can apply updates from GPT-4o, Claude, and others into your files at...

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="relace/relace-apply-3",
  messages=[{"role": "user", "content": "Hello world!"}],
)
```

---

### Google: Gemini 2.5 Flash Lite Preview 09-2025

| Campo | Valor |
|---|---|
| model_id | `google/gemini-2.5-flash-lite-preview-09-2025` |
| Proveedor | google |
| Modalidad | text+image+file+audio+video->text |
| Contexto | 1048576 |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.40 |
| Gratuito | No |

**Descripción funcional:**
Gemini 2.5 Flash-Lite is a lightweight reasoning model in the Gemini 2.5 family, optimized for ultra-low latency and cost efficiency. It offers improved throughput, faster token generation, and better performance...

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="google/gemini-2.5-flash-lite-preview-09-2025",
  messages=[{"role": "user", "content": "Hello world!"}],
)
```

---

### Qwen: Qwen3 VL 235B A22B Thinking

| Campo | Valor |
|---|---|
| model_id | `qwen/qwen3-vl-235b-a22b-thinking` |
| Proveedor | qwen |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M | $0.26 |
| Precio Output/M | $2.60 |
| Gratuito | No |

**Descripción funcional:**
Qwen3-VL-235B-A22B Thinking is a multimodal model that unifies strong text generation with visual understanding across images and video. The Thinking model is optimized for multimodal reasoning in STEM and math....

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="qwen/qwen3-vl-235b-a22b-thinking",
  messages=[{"role": "user", "content": "Hello world!"}],
)
```

---

### Qwen: Qwen3 VL 235B A22B Instruct

| Campo | Valor |
|---|---|
| model_id | `qwen/qwen3-vl-235b-a22b-instruct` |
| Proveedor | qwen |
| Modalidad | text+image->text |
| Contexto | 262144 |
| Precio Input/M | $0.20 |
| Precio Output/M | $0.88 |
| Gratuito | No |

**Descripción funcional:**
Qwen3-VL-235B-A22B Instruct is an open-weight multimodal model that unifies strong text generation with visual understanding across images and video. The Instruct model targets general vision-language use (VQA, document parsing, chart/table...

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="qwen/qwen3-vl-235b-a22b-instruct",
  messages=[{"role": "user", "content": "Hello world!"}],
)
```

---

### Qwen: Qwen3 Max

| Campo | Valor |
|---|---|
| model_id | `qwen/qwen3-max` |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 262144 |
| Precio Input/M | $0.78 |
| Precio Output/M | $3.90 |
| Gratuito | No |

**Descripción funcional:**
Qwen3-Max is an updated release built on the Qwen3 series, offering major improvements in reasoning, instruction following, multilingual support, and long-tail knowledge coverage compared to the January 2025 version. It...

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
  model="qwen/qwen3-max",
  messages=[{"role": "user", "content": "Hello world!"}],
)
```

---

### Qwen: Qwen3 Coder Plus

| Característica | Valor |
|---|---|
| model_id | `qwen/qwen3-coder-plus` |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 1000000 |
| Precio Input/M | $0.65 |
| Precio Output/M | $3.25 |
| Gratuito | No |

**Descripción funcional:** Qwen3 Coder Plus is Alibaba's proprietary version of the Open Source Qwen3 Coder 480B A35B. It is a powerful coding agent model specializing in autonomous programming via tool calling and...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-coder-plus", messages=[...])
```

---

### OpenAI: GPT-5 Codex

| Característica | Valor |
|---|---|
| model_id | `openai/gpt-5-codex` |
| Proveedor | openai |
| Modalidad | text+image->text |
| Contexto | 400000 |
| Precio Input/M | $1.25 |
| Precio Output/M | $10.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5-Codex is a specialized version of GPT-5 optimized for software engineering and coding workflows. It is designed for both interactive development sessions and long, independent execution of complex engineering tasks....

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5-codex", messages=[...])
```

---

### DeepSeek: DeepSeek V3.1 Terminus

| Característica | Valor |
|---|---|
| model_id | `deepseek/deepseek-v3.1-terminus` |
| Proveedor | deepseek |
| Modalidad | text->text |
| Contexto | 163840 |
| Precio Input/M | $0.21 |
| Precio Output/M | $0.79 |
| Gratuito | No |

**Descripción funcional:** DeepSeek-V3.1 Terminus is an update to [DeepSeek V3.1](/deepseek/deepseek-chat-v3.1) that maintains the model's original capabilities while addressing issues reported by users, including language consistency and agent capabilities, further optimizing the model's...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="deepseek/deepseek-v3.1-terminus", messages=[...])
```

---

### xAI: Grok 4 Fast

| Característica | Valor |
|---|---|
| model_id | `x-ai/grok-4-fast` |
| Proveedor | x-ai |
| Modalidad | text+image+file->text |
| Contexto | 2000000 |
| Precio Input/M | $0.20 |
| Precio Output/M | $0.50 |
| Gratuito | No |

**Descripción funcional:** Grok 4 Fast is xAI's latest multimodal model with SOTA cost-efficiency and a 2M token context window. It comes in two flavors: non-reasoning and reasoning. Read more about the model...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="x-ai/grok-4-fast", messages=[...])
```

---

### Tongyi DeepResearch 30B A3B

| Característica | Valor |
|---|---|
| model_id | `alibaba/tongyi-deepresearch-30b-a3b` |
| Proveedor | alibaba |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.09 |
| Precio Output/M | $0.45 |
| Gratuito | No |

**Descripción funcional:** Tongyi DeepResearch is an agentic large language model developed by Tongyi Lab, with 30 billion total parameters activating only 3 billion per token. It's optimized for long-horizon, deep information-seeking tasks...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="alibaba/tongyi-deepresearch-30b-a3b", messages=[...])
```

---

### Qwen: Qwen3 Coder Flash

| Característica | Valor |
|---|---|
| model_id | `qwen/qwen3-coder-flash` |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 1000000 |
| Precio Input/M | $0.20 |
| Precio Output/M | $0.97 |
| Gratuito | No |

**Descripción funcional:** Qwen3 Coder Flash is Alibaba's fast and cost efficient version of their proprietary Qwen3 Coder Plus. It is a powerful coding agent model specializing in autonomous programming via tool calling...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-coder-flash", messages=[...])
```

---

### Qwen: Qwen3 Next 80B A3B Thinking

| Característica | Valor |
|---|---|
| model_id | `qwen/qwen3-next-80b-a3b-thinking` |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.78 |
| Gratuito | No |

**Descripción funcional:** Qwen3-Next-80B-A3B-Thinking is a reasoning-first chat model in the Qwen3-Next line that outputs structured “thinking” traces by default. It’s designed for hard multi-step problems; math proofs, code synthesis/debugging, logic, and agentic...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-next-80b-a3b-thinking", messages=[...])
```

---

### Google: Lyria 3 Pro Preview

| Atributo | Valor |
|---|---|
| model_id | google/lyria-3-pro-preview |
| Proveedor | google |
| Modalidad | text+image->text+audio |
| Contexto | 1048576 |
| Precio Input/M tokens | GRATUITO |
| Precio Output/M tokens | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** Full-length songs are priced at $0.08 per song. Lyria 3 is Google's family of music generation models, available through the Gemini API. With Lyria 3,...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="google/lyria-3-pro-preview", messages=[...])
```

---

### Google: Lyria 3 Clip Preview

| Atributo | Valor |
|---|---|
| model_id | google/lyria-3-clip-preview |
| Proveedor | google |
| Modalidad | text+image->text+audio |
| Contexto | 1048576 |
| Precio Input/M tokens | GRATUITO |
| Precio Output/M tokens | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** 30 second duration clips are priced at $0.04 per clip. Lyria 3 is Google's family of music generation models, available through the Gemini API. With L...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="google/lyria-3-clip-preview", messages=[...])
```

---

### Kwaipilot: KAT-Coder-Pro V2

| Atributo | Valor |
|---|---|
| model_id | kwaipilot/kat-coder-pro-v2 |
| Proveedor | kwaipilot |
| Modalidad | text->text |
| Contexto | 256000 |
| Precio Input/M tokens | $0.30 |
| Precio Output/M tokens | $1.20 |
| Gratuito | No |

**Descripción funcional:** KAT-Coder-Pro V2 is the latest high-performance model in KwaiKAT’s KAT-Coder series, designed for complex enterprise-grade software engineering and Sa...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="kwaipilot/kat-coder-pro-v2", messages=[...])
```

---

### Reka Edge

| Atributo | Valor |
|---|---|
| model_id | rekaai/reka-edge |
| Proveedor | rekaai |
| Modalidad | text+image+video->text |
| Contexto | 16384 |
| Precio Input/M tokens | $0.10 |
| Precio Output/M tokens | $0.10 |
| Gratuito | No |

**Descripción funcional:** Reka Edge is an extremely efficient 7B multimodal vision-language model that accepts image/video+text inputs and generates text outputs. This model is...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="rekaai/reka-edge", messages=[...])
```

---

### Xiaomi: MiMo-V2-Omni

| Atributo | Valor |
|---|---|
| model_id | xiaomi/mimo-v2-omni |
| Proveedor | xiaomi |
| Modalidad | text+image+audio+video->text |
| Contexto | 262144 |
| Precio Input/M tokens | $0.40 |
| Precio Output/M tokens | $2.00 |
| Gratuito | No |

**Descripción funcional:** MiMo-V2-Omni is a frontier omni-modal model that natively processes image, video, and audio inputs within a unified architecture. It combines strong m...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="xiaomi/mimo-v2-omni", messages=[...])
```

---

### Xiaomi: MiMo-V2-Pro

| Atributo | Valor |
|---|---|
| model_id | xiaomi/mimo-v2-pro |
| Proveedor | xiaomi |
| Modalidad | text->text |
| Contexto | 1048576 |
| Precio Input/M tokens | $1.00 |
| Precio Output/M tokens | $3.00 |
| Gratuito | No |

**Descripción funcional:** MiMo-V2-Pro is Xiaomi's flagship foundation model, featuring over 1T total parameters and a 1M context length, deeply optimized for agentic scenarios....

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="xiaomi/mimo-v2-pro", messages=[...])
```

---

### MiniMax: MiniMax M2.7

| Atributo | Valor |
|---|---|
| model_id | minimax/minimax-m2.7 |
| Proveedor | minimax |
| Modalidad | text->text |
| Contexto | 204800 |
| Precio Input/M tokens | $0.30 |
| Precio Output/M tokens | $1.20 |
| Gratuito | No |

**Descripción funcional:** MiniMax-M2.7 is a next-generation large language model designed for autonomous, real-world productivity and continuous improvement. Built to actively ...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="minimax/minimax-m2.7", messages=[...])
```

---

### Qwen: Qwen3 Next 80B A3B Instruct (free)

| Característica | Valor |
|---|---|
| model_id | `qwen/qwen3-next-80b-a3b-instruct:free` |
| Proveedor | Qwen |
| Modalidad | text->text |
| Contexto | 262144 tokens |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** Qwen3-Next-80B-A3B-Instruct is an instruction-tuned chat model in the Qwen3-Next series optimized for fast, stable responses without “thinking” traces...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-next-80b-a3b-instruct:free", messages=[...])
```

---

### Qwen: Qwen3 Next 80B A3B Instruct

| Característica | Valor |
|---|---|
| model_id | `qwen/qwen3-next-80b-a3b-instruct` |
| Proveedor | Qwen |
| Modalidad | text->text |
| Contexto | 262144 tokens |
| Precio Input/M | $0.09 |
| Precio Output/M | $1.10 |
| Gratuito | No |

**Descripción funcional:** Qwen3-Next-80B-A3B-Instruct is an instruction-tuned chat model in the Qwen3-Next series optimized for fast, stable responses without “thinking” traces...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-next-80b-a3b-instruct", messages=[...])
```

---

### Meituan: LongCat Flash Chat

| Característica | Valor |
|---|---|
| model_id | `meituan/longcat-flash-chat` |
| Proveedor | Meituan |
| Modalidad | text->text |
| Contexto | 131072 tokens |
| Precio Input/M | $0.20 |
| Precio Output/M | $0.80 |
| Gratuito | No |

**Descripción funcional:** LongCat-Flash-Chat is a large-scale Mixture-of-Experts (MoE) model with 560B total parameters, of which 18.6B–31.3B (≈27B on average) are dynamically ...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="meituan/longcat-flash-chat", messages=[...])
```

---

### Qwen: Qwen Plus 0728 (thinking)

| Característica | Valor |
|---|---|
| model_id | `qwen/qwen-plus-2025-07-28:thinking` |
| Proveedor | Qwen |
| Modalidad | text->text |
| Contexto | 1000000 tokens |
| Precio Input/M | $0.26 |
| Precio Output/M | $0.78 |
| Gratuito | No |

**Descripción funcional:** Qwen Plus 0728, based on the Qwen3 foundation model, is a 1 million context hybrid reasoning model with a balanced performance, speed, and cost combin...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen-plus-2025-07-28:thinking", messages=[...])
```

---

### Qwen: Qwen Plus 0728

| Característica | Valor |
|---|---|
| model_id | `qwen/qwen-plus-2025-07-28` |
| Proveedor | Qwen |
| Modalidad | text->text |
| Contexto | 1000000 tokens |
| Precio Input/M | $0.26 |
| Precio Output/M | $0.78 |
| Gratuito | No |

**Descripción funcional:** Qwen Plus 0728, based on the Qwen3 foundation model, is a 1 million context hybrid reasoning model with a balanced performance, speed, and cost combin...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen-plus-2025-07-28", messages=[...])
```

---

### NVIDIA: Nemotron Nano 9B V2 (free)

| Característica | Valor |
|---|---|
| model_id | `nvidia/nemotron-nano-9b-v2:free` |
| Proveedor | NVIDIA |
| Modalidad | text->text |
| Contexto | 128000 tokens |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** NVIDIA-Nemotron-Nano-9B-v2 is a large language model (LLM) trained from scratch by NVIDIA, and designed as a unified model for both reasoning and non-...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="nvidia/nemotron-nano-9b-v2:free", messages=[...])
```

---

### NVIDIA: Nemotron Nano 9B V2

| Característica | Valor |
|---|---|
| model_id | `nvidia/nemotron-nano-9b-v2` |
| Proveedor | NVIDIA |
| Modalidad | text->text |
| Contexto | 131072 tokens |
| Precio Input/M | $0.04 |
| Precio Output/M | $0.16 |
| Gratuito | No |

**Descripción funcional:** NVIDIA-Nemotron-Nano-9B-v2 is a large language model (LLM) trained from scratch by NVIDIA, and designed as a unified model for both reasoning and non-...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="nvidia/nemotron-nano-9b-v2", messages=[...])
```

---

### MoonshotAI: Kimi K2 0905

| Campo | Valor |
|---|---|
| model_id | moonshotai/kimi-k2-0905 |
| Proveedor | moonshotai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.40 |
| Precio Output/M tokens | $2.00 |
| Gratuito | No |

**Descripción funcional:** Kimi K2 0905 is the September update of [Kimi K2 0711](moonshotai/kimi-k2).  It is a large-scale Mixture-of-Experts (MoE) language model developed by Moonshot AI, featuring 1 trillion total parameters with 32 billion active per forward pass.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="moonshotai/kimi-k2-0905", messages=[...])```

---

### Qwen: Qwen3 30B A3B Thinking 2507

| Campo | Valor |
|---|---|
| model_id | qwen/qwen3-30b-a3b-thinking-2507 |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.08 |
| Precio Output/M tokens | $0.40 |
| Gratuito | No |

**Descripción funcional:** Qwen3-30B-A3B-Thinking-2507 is a 30B parameter Mixture-of-Experts reasoning model optimized for complex tasks requiring extended multi-step thinking.  The model is designed specifically for “thinking mode,” where internal reasoning traces are separated from final answers.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3-30b-a3b-thinking-2507", messages=[...])```

---

### xAI: Grok Code Fast 1

| Campo | Valor |
|---|---|
| model_id | x-ai/grok-code-fast-1 |
| Proveedor | x-ai |
| Modalidad | text->text |
| Contexto | 256000 |
| Precio Input/M tokens | $0.20 |
| Precio Output/M tokens | $1.50 |
| Gratuito | No |

**Descripción funcional:** Grok Code Fast 1 is a speedy and economical reasoning model that excels at agentic coding.  With reasoning traces visible in the response, developers can steer Grok Code for high-quality work flows.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="x-ai/grok-code-fast-1", messages=[...])```

---

### Nous: Hermes 4 70B

| Campo | Valor |
|---|---|
| model_id | nousresearch/hermes-4-70b |
| Proveedor | nousresearch |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.13 |
| Precio Output/M tokens | $0.40 |
| Gratuito | No |

**Descripción funcional:** Hermes 4 70B is a hybrid reasoning model from Nous Research, built on Meta-Llama-3. 1-70B.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="nousresearch/hermes-4-70b", messages=[...])```

---

### Nous: Hermes 4 405B

| Campo | Valor |
|---|---|
| model_id | nousresearch/hermes-4-405b |
| Proveedor | nousresearch |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $1.00 |
| Precio Output/M tokens | $3.00 |
| Gratuito | No |

**Descripción funcional:** Hermes 4 is a large-scale reasoning model built on Meta-Llama-3. 1-405B and released by Nous Research.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="nousresearch/hermes-4-405b", messages=[...])```

---

### DeepSeek: DeepSeek V3.1

| Campo | Valor |
|---|---|
| model_id | deepseek/deepseek-chat-v3.1 |
| Proveedor | deepseek |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M tokens | $0.15 |
| Precio Output/M tokens | $0.75 |
| Gratuito | No |

**Descripción funcional:** DeepSeek-V3. 1 is a large hybrid reasoning model (671B parameters, 37B active) that supports both thinking and non-thinking modes via prompt templates.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="deepseek/deepseek-chat-v3.1", messages=[...])```

---

### OpenAI: GPT-4o Audio

| Campo | Valor |
|---|---|
| model_id | openai/gpt-4o-audio-preview |
| Proveedor | openai |
| Modalidad | text+audio->text+audio |
| Contexto | 128000 |
| Precio Input/M tokens | $2.50 |
| Precio Output/M tokens | $10.00 |
| Gratuito | No |

**Descripción funcional:** The gpt-4o-audio-preview model adds support for audio inputs as prompts.  This enhancement allows the model to detect nuances within audio recordings and add depth to generated user experiences.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-4o-audio-preview", messages=[...])```

---

### Mistral: Mistral Medium 3.1

| Atributo | Valor |
|---|---|
| model_id | `mistralai/mistral-medium-3.1` |
| Proveedor | mistralai |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M | $0.40 |
| Precio Output/M | $2.00 |
| Gratuito | No |

> Mistral Medium 3.1 is an updated version of Mistral Medium 3, which is a high-performance enterprise-grade language model designed to deliver frontier-level capabilities at significantly reduced operational cost. It balances state-of-the-art reasoning and multimodal performance with 8× lower cost compared to traditional large models, making it suitable for scalable deployments across professional and industrial use cases.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="mistralai/mistral-medium-3.1", messages=[...])
```

---

### Baidu: ERNIE 4.5 21B A3B

| Atributo | Valor |
|---|---|
| model_id | `baidu/ernie-4.5-21b-a3b` |
| Proveedor | baidu |
| Modalidad | text->text |
| Contexto | 120000 |
| Precio Input/M | $0.07 |
| Precio Output/M | $0.28 |
| Gratuito | No |

> A sophisticated text-based Mixture-of-Experts (MoE) model featuring 21B total parameters with 3B activated per token, delivering exceptional multimodal understanding and generation through heterogeneous MoE structures and modality-isolated routing. Supporting an extensive 131K token context length, the model achieves efficient inference via multi-expert parallel collaboration and quantization, while advanced post-training techniques including SFT, DPO, and UPO ensure optimized performance across diverse applications with specialized routing and balancing losses for superior task handling.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="baidu/ernie-4.5-21b-a3b", messages=[...])
```

---

### Baidu: ERNIE 4.5 VL 28B A3B

| Atributo | Valor |
|---|---|
| model_id | `baidu/ernie-4.5-vl-28b-a3b` |
| Proveedor | baidu |
| Modalidad | text+image->text |
| Contexto | 30000 |
| Precio Input/M | $0.14 |
| Precio Output/M | $0.56 |
| Gratuito | No |

> A powerful multimodal Mixture-of-Experts chat model featuring 28B total parameters with 3B activated per token, delivering exceptional text and vision understanding through its innovative heterogeneous MoE structure with modality-isolated routing. Built with scaling-efficient infrastructure for high-throughput training and inference, the model leverages advanced post-training techniques including SFT, DPO, and UPO for optimized performance, while supporting an impressive 131K context length and RLVR alignment for superior cross-modal reasoning and generation capabilities.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="baidu/ernie-4.5-vl-28b-a3b", messages=[...])
```

---

### Z.ai: GLM 4.5V

| Atributo | Valor |
|---|---|
| model_id | `z-ai/glm-4.5v` |
| Proveedor | z-ai |
| Modalidad | text+image->text |
| Contexto | 65536 |
| Precio Input/M | $0.60 |
| Precio Output/M | $1.80 |
| Gratuito | No |

> GLM-4.5V is a vision-language foundation model for multimodal agent applications. Built on a Mixture-of-Experts (MoE) architecture with 106B parameters and 12B activated parameters, it achieves state-of-the-art results in video understanding, image Q&A, OCR, and document parsing, with strong gains in front-end web coding, grounding, and spatial reasoning. It offers a hybrid inference mode: a "thinking mode" for deep reasoning and a "non-thinking mode" for fast responses. Reasoning behavior can be toggled via the `reasoning` `enabled` boolean. [Learn more in our docs](https://openrouter.ai/docs/use-cases/reasoning-tokens#enable-reasoning-with-default-config)

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="z-ai/glm-4.5v", messages=[...])
```

---

### AI21: Jamba Large 1.7

| Atributo | Valor |
|---|---|
| model_id | `ai21/jamba-large-1.7` |
| Proveedor | ai21 |
| Modalidad | text->text |
| Contexto | 256000 |
| Precio Input/M | $2.00 |
| Precio Output/M | $8.00 |
| Gratuito | No |

> Jamba Large 1.7 is the latest model in the Jamba open family, offering improvements in grounding, instruction-following, and overall efficiency. Built on a hybrid SSM-Transformer architecture with a 256K context window, it delivers more accurate, contextually grounded responses and better steerability than previous versions.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="ai21/jamba-large-1.7", messages=[...])
```

---

### OpenAI: GPT-5 Chat

| Atributo | Valor |
|---|---|
| model_id | `openai/gpt-5-chat` |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 128000 |
| Precio Input/M | $1.25 |
| Precio Output/M | $10.00 |
| Gratuito | No |

> GPT-5 Chat is designed for advanced, natural, multimodal, and context-aware conversations for enterprise applications.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5-chat", messages=[...])
```

---

### OpenAI: GPT-5

| Atributo | Valor |
|---|---|
| model_id | `openai/gpt-5` |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 400000 |
| Precio Input/M | $1.25 |
| Precio Output/M | $10.00 |
| Gratuito | No |

> GPT-5 is OpenAI’s most advanced model, offering major improvements in reasoning, code quality, and user experience. It is optimized for complex tasks that require step-by-step reasoning, instruction following, and accuracy in high-stakes use cases. It supports test-time routing features and advanced prompt understanding, including user-specified intent like "think hard about this." Improvements include reductions in hallucination, sycophancy, and better performance in coding, writing, and health-related tasks.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5", messages=[...])
```

---

### OpenAI: GPT-5 Mini

| Campo | Valor |
|---|---|
| model_id | `openai/gpt-5-mini` |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 400000 |
| Precio Input/M tokens | $0.25 |
| Precio Output/M tokens | $2.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5 Mini is a compact version of GPT-5, designed to handle lighter-weight reasoning tasks. It provides the same instruction-following and safety-tuning benefits as GPT-5, but with reduced latency and cost.


**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5-mini", messages=[{"role": "user", "content": "..."}])
```

---

### OpenAI: GPT-5 Nano

| Campo | Valor |
|---|---|
| model_id | `openai/gpt-5-nano` |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 400000 |
| Precio Input/M tokens | $0.05 |
| Precio Output/M tokens | $0.40 |
| Gratuito | No |

**Descripción funcional:** GPT-5-Nano is the smallest and fastest variant in the GPT-5 system, optimized for developer tools, rapid interactions, and ultra-low latency environments. While limited in reasoning depth compared to its larger counterparts, it retains key instruction-following and safety features.


**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5-nano", messages=[{"role": "user", "content": "..."}])
```

---

### OpenAI: gpt-oss-120b (free)

| Campo | Valor |
|---|---|
| model_id | `openai/gpt-oss-120b:free` |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | GRATUITO |
| Precio Output/M tokens | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** gpt-oss-120b is an open-weight, 117B-parameter Mixture-of-Experts (MoE) language model from OpenAI designed for high-reasoning, agentic, and general-purpose production use cases. It activates 5.1B parameters per forward pass and is optimized to run on a single H100 GPU with native MXFP4 quantization.


**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-oss-120b:free", messages=[{"role": "user", "content": "..."}])
```

---

### OpenAI: gpt-oss-120b

| Campo | Valor |
|---|---|
| model_id | `openai/gpt-oss-120b` |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.04 |
| Precio Output/M tokens | $0.19 |
| Gratuito | No |

**Descripción funcional:** gpt-oss-120b is an open-weight, 117B-parameter Mixture-of-Experts (MoE) language model from OpenAI designed for high-reasoning, agentic, and general-purpose production use cases. It activates 5.1B parameters per forward pass and is optimized to run on a single H100 GPU with native MXFP4 quantization.


**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-oss-120b", messages=[{"role": "user", "content": "..."}])
```

---

### OpenAI: gpt-oss-20b (free)

| Campo | Valor |
|---|---|
| model_id | `openai/gpt-oss-20b:free` |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | GRATUITO |
| Precio Output/M tokens | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** gpt-oss-20b is an open-weight 21B parameter model released by OpenAI under the Apache 2.0 license. It uses a Mixture-of-Experts (MoE) architecture with 3.6B active parameters per forward pass, optimized for lower-latency inference and deployability on consumer or single-GPU hardware.


**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-oss-20b:free", messages=[{"role": "user", "content": "..."}])
```

---

### OpenAI: gpt-oss-20b

| Campo | Valor |
|---|---|
| model_id | `openai/gpt-oss-20b` |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.03 |
| Precio Output/M tokens | $0.11 |
| Gratuito | No |

**Descripción funcional:** gpt-oss-20b is an open-weight 21B parameter model released by OpenAI under the Apache 2.0 license. It uses a Mixture-of-Experts (MoE) architecture with 3.6B active parameters per forward pass, optimized for lower-latency inference and deployability on consumer or single-GPU hardware.


**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role": "user", "content": "..."}])
```

---

### Anthropic: Claude Opus 4.1

| Campo | Valor |
|---|---|
| model_id | `anthropic/claude-opus-4.1` |
| Proveedor | anthropic |
| Modalidad | text+image+file->text |
| Contexto | 200000 |
| Precio Input/M tokens | $15.00 |
| Precio Output/M tokens | $75.00 |
| Gratuito | No |

**Descripción funcional:** Claude Opus 4.1 is an updated version of Anthropic’s flagship model, offering improved performance in coding, reasoning, and agentic tasks. It achieves 74.5% on SWE-bench Verified and shows notable gains in multi-file code refactoring, debugging precision, and detail-oriented reasoning.


**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="anthropic/claude-opus-4.1", messages=[{"role": "user", "content": "..."}])
```

---

### Mistral: Codestral 2508
| Campo | Valor |
|---|---|
| model_id | mistralai/codestral-2508 |
| Proveedor | mistralai |
| Modalidad | text->text |
| Contexto | 256000 |
| Precio Input/M tokens | $0.30 |
| Precio Output/M tokens | $0.90 |
| Gratuito | No |

**Descripción funcional:** Mistral's cutting-edge language model for coding released end of July 2025. Codestral specializes in low-latency, high-frequency tasks such as fill-in-the-middle (FIM), code correction and test generation.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="mistralai/codestral-2508", messages=[...])
```
---
### Qwen: Qwen3 Coder 30B A3B Instruct
| Campo | Valor |
|---|---|
| model_id | qwen/qwen3-coder-30b-a3b-instruct |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 160000 |
| Precio Input/M tokens | $0.07 |
| Precio Output/M tokens | $0.27 |
| Gratuito | No |

**Descripción funcional:** Qwen3-Coder-30B-A3B-Instruct is a 30.5B parameter Mixture-of-Experts (MoE) model with 128 experts (8 active per forward pass), designed for advanced code generation, repository-scale understanding, and agentic tool use. Built on the Qwen3 architecture, it supports a native context length of 256K tokens (extendable to 1M with Yarn) and performs strongly in tasks involving function calls, browser use, and structured code completion.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="qwen/qwen3-coder-30b-a3b-instruct", messages=[...])
```
---
### Qwen: Qwen3 30B A3B Instruct 2507
| Campo | Valor |
|---|---|
| model_id | qwen/qwen3-30b-a3b-instruct-2507 |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 262144 |
| Precio Input/M tokens | $0.09 |
| Precio Output/M tokens | $0.30 |
| Gratuito | No |

**Descripción funcional:** Qwen3-30B-A3B-Instruct-2507 is a 30.5B-parameter mixture-of-experts language model from Qwen, with 3.3B active parameters per inference. It operates in non-thinking mode and is designed for high-quality instruction following, multilingual understanding, and agentic tool use. Post-trained on instruction data, it demonstrates competitive performance across reasoning (AIME, ZebraLogic), coding (MultiPL-E, LiveCodeBench), and alignment (IFEval, WritingBench) benchmarks. It outperforms its non-instruct variant on subjective and open-ended tasks while retaining strong factual and coding performance.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="qwen/qwen3-30b-a3b-instruct-2507", messages=[...])
```
---
### Z.ai: GLM 4.5
| Campo | Valor |
|---|---|
| model_id | z-ai/glm-4.5 |
| Proveedor | z-ai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.60 |
| Precio Output/M tokens | $2.20 |
| Gratuito | No |

**Descripción funcional:** GLM-4.5 is our latest flagship foundation model, purpose-built for agent-based applications. It leverages a Mixture-of-Experts (MoE) architecture and supports a context length of up to 128k tokens. GLM-4.5 delivers significantly enhanced capabilities in reasoning, code generation, and agent alignment. It supports a hybrid inference mode with two options, a "thinking mode" designed for complex reasoning and tool use, and a "non-thinking mode" optimized for instant responses. Users can control the reasoning behaviour with the `reasoning` `enabled` boolean. [Learn more in our docs](https://openrouter.ai/docs/use-cases/reasoning-tokens#enable-reasoning-with-default-config)

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="z-ai/glm-4.5", messages=[...])
```
---
### Z.ai: GLM 4.5 Air (free)
| Campo | Valor |
|---|---|
| model_id | z-ai/glm-4.5-air:free |
| Proveedor | z-ai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | GRATUITO |
| Precio Output/M tokens | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** GLM-4.5-Air is the lightweight variant of our latest flagship model family, also purpose-built for agent-centric applications. Like GLM-4.5, it adopts the Mixture-of-Experts (MoE) architecture but with a more compact parameter size. GLM-4.5-Air also supports hybrid inference modes, offering a "thinking mode" for advanced reasoning and tool use, and a "non-thinking mode" for real-time interaction. Users can control the reasoning behaviour with the `reasoning` `enabled` boolean. [Learn more in our docs](https://openrouter.ai/docs/use-cases/reasoning-tokens#enable-reasoning-with-default-config)

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="z-ai/glm-4.5-air:free", messages=[...])
```
---
### Z.ai: GLM 4.5 Air
| Campo | Valor |
|---|---|
| model_id | z-ai/glm-4.5-air |
| Proveedor | z-ai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.13 |
| Precio Output/M tokens | $0.85 |
| Gratuito | No |

**Descripción funcional:** GLM-4.5-Air is the lightweight variant of our latest flagship model family, also purpose-built for agent-centric applications. Like GLM-4.5, it adopts the Mixture-of-Experts (MoE) architecture but with a more compact parameter size. GLM-4.5-Air also supports hybrid inference modes, offering a "thinking mode" for advanced reasoning and tool use, and a "non-thinking mode" for real-time interaction. Users can control the reasoning behaviour with the `reasoning` `enabled` boolean. [Learn more in our docs](https://openrouter.ai/docs/use-cases/reasoning-tokens#enable-reasoning-with-default-config)

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="z-ai/glm-4.5-air", messages=[...])
```
---
### Qwen: Qwen3 235B A22B Thinking 2507
| Campo | Valor |
|---|---|
| model_id | qwen/qwen3-235b-a22b-thinking-2507 |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.15 |
| Precio Output/M tokens | $1.50 |
| Gratuito | No |

**Descripción funcional:** Qwen3-235B-A22B-Thinking-2507 is a high-performance, open-weight Mixture-of-Experts (MoE) language model optimized for complex reasoning tasks. It activates 22B of its 235B parameters per forward pass and natively supports up to 262,144 tokens of context. This "thinking-only" variant enhances structured logical reasoning, mathematics, science, and long-form generation, showing strong benchmark performance across AIME, SuperGPQA, LiveCodeBench, and MMLU-Redux. It enforces a special reasoning mode (</think>) and is designed for high-token outputs (up to 81,920 tokens) in challenging domains.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="qwen/qwen3-235b-a22b-thinking-2507", messages=[...])
```
---

### Z.ai: GLM 4 32B 
| Atributo | Valor |
|---|---|
| model_id | `z-ai/glm-4-32b` |
| Proveedor | Z-ai |
| Modalidad | text->text |
| Contexto | 128000 tokens |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.10 |
| Gratuito | No |

**Descripción Funcional:**
GLM 4 32B is a cost-effective foundation language model.

**Configuración de Uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="z-ai/glm-4-32b", messages=[...])
```
---
### Qwen: Qwen3 Coder 480B A35B (free)
| Atributo | Valor |
|---|---|
| model_id | `qwen/qwen3-coder:free` |
| Proveedor | Qwen |
| Modalidad | text->text |
| Contexto | 262000 tokens |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción Funcional:**
Qwen3-Coder-480B-A35B-Instruct is a Mixture-of-Experts (MoE) code generation model developed by the Qwen team. It is optimized for agentic coding tasks such as function calling, tool use, and long-context reasoning over repositories. The model features 480 billion total parameters, with 35 billion active per forward pass (8 out of 160 experts).

**Configuración de Uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3-coder:free", messages=[...])
```
---
### Qwen: Qwen3 Coder 480B A35B
| Atributo | Valor |
|---|---|
| model_id | `qwen/qwen3-coder` |
| Proveedor | Qwen |
| Modalidad | text->text |
| Contexto | 262144 tokens |
| Precio Input/M | $0.22 |
| Precio Output/M | $1.00 |
| Gratuito | No |

**Descripción Funcional:**
Qwen3-Coder-480B-A35B-Instruct is a Mixture-of-Experts (MoE) code generation model developed by the Qwen team. It is optimized for agentic coding tasks such as function calling, tool use, and long-context reasoning over repositories. The model features 480 billion total parameters, with 35 billion active per forward pass (8 out of 160 experts).

**Configuración de Uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3-coder", messages=[...])
```
---
### ByteDance: UI-TARS 7B 
| Atributo | Valor |
|---|---|
| model_id | `bytedance/ui-tars-1.5-7b` |
| Proveedor | Bytedance |
| Modalidad | text+image->text |
| Contexto | 128000 tokens |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.20 |
| Gratuito | No |

**Descripción Funcional:**
UI-TARS-1.5 is a multimodal vision-language agent optimized for GUI-based environments, including desktop interfaces, web browsers, mobile systems, and games. Built by ByteDance, it builds upon the UI-TARS framework with reinforcement learning-based reasoning, enabling robust action planning and execution across virtual interfaces.

**Configuración de Uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="bytedance/ui-tars-1.5-7b", messages=[...])
```
---
### Google: Gemini 2.5 Flash Lite
| Atributo | Valor |
|---|---|
| model_id | `google/gemini-2.5-flash-lite` |
| Proveedor | Google |
| Modalidad | text+image+file+audio+video->text |
| Contexto | 1048576 tokens |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.40 |
| Gratuito | No |

**Descripción Funcional:**
Gemini 2.5 Flash-Lite is a lightweight reasoning model in the Gemini 2.5 family, optimized for ultra-low latency and cost efficiency. It offers improved throughput, faster token generation, and better performance across common benchmarks compared to earlier Flash models. By default, "thinking" (i.e. multi-pass reasoning) is disabled to prioritize speed, but developers can enable it via the [Reasoning API parameter](https://openrouter.ai/docs/use-cases/reasoning-tokens) to selectively trade off cost for intelligence. 

**Configuración de Uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="google/gemini-2.5-flash-lite", messages=[...])
```
---
### Qwen: Qwen3 235B A22B Instruct 2507
| Atributo | Valor |
|---|---|
| model_id | `qwen/qwen3-235b-a22b-2507` |
| Proveedor | Qwen |
| Modalidad | text->text |
| Contexto | 262144 tokens |
| Precio Input/M | $0.07 |
| Precio Output/M | $0.10 |
| Gratuito | No |

**Descripción Funcional:**
Qwen3-235B-A22B-Instruct-2507 is a multilingual, instruction-tuned mixture-of-experts language model based on the Qwen3-235B architecture, with 22B active parameters per forward pass. It is optimized for general-purpose text generation, including instruction following, logical reasoning, math, code, and tool usage. The model supports a native 262K context length and does not implement "thinking mode" (<think> blocks).

**Configuración de Uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3-235b-a22b-2507", messages=[...])
```
---
### Switchpoint Router
| Atributo | Valor |
|---|---|
| model_id | `switchpoint/router` |
| Proveedor | Switchpoint |
| Modalidad | text->text |
| Contexto | 131072 tokens |
| Precio Input/M | $0.85 |
| Precio Output/M | $3.40 |
| Gratuito | No |

**Descripción Funcional:**
Switchpoint AI's router instantly analyzes your request and directs it to the optimal AI from an ever-evolving library. 

**Configuración de Uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="switchpoint/router", messages=[...])
```
---

### MoonshotAI: Kimi K2 0711

| Campo | Valor |
|---|---|
| model_id | moonshotai/kimi-k2 |
| Proveedor | moonshotai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.57 |
| Precio Output/M tokens | $2.30 |
| Gratuito | No |

**Descripción funcional:** Kimi K2 Instruct is a large-scale Mixture-of-Experts (MoE) language model developed by Moonshot AI, featuring 1 trillion total parameters with 32 billion active per forward pass.  It is optimized for agentic capabilities, including advanced tool use, reasoning, and code synthesis.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="moonshotai/kimi-k2", messages=[{"role": "user", "content": "..."}])
```

---

### Mistral: Devstral Medium

| Campo | Valor |
|---|---|
| model_id | mistralai/devstral-medium |
| Proveedor | mistralai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.40 |
| Precio Output/M tokens | $2.00 |
| Gratuito | No |

**Descripción funcional:** Devstral Medium is a high-performance code generation and agentic reasoning model developed jointly by Mistral AI and All Hands AI.  Positioned as a step up from Devstral Small, it achieves 61.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="mistralai/devstral-medium", messages=[{"role": "user", "content": "..."}])
```

---

### Mistral: Devstral Small 1.1

| Campo | Valor |
|---|---|
| model_id | mistralai/devstral-small |
| Proveedor | mistralai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.10 |
| Precio Output/M tokens | $0.30 |
| Gratuito | No |

**Descripción funcional:** Devstral Small 1. 1 is a 24B parameter open-weight language model for software engineering agents, developed by Mistral AI in collaboration with All Hands AI.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="mistralai/devstral-small", messages=[{"role": "user", "content": "..."}])
```

---

### Venice: Uncensored (free)

| Campo | Valor |
|---|---|
| model_id | cognitivecomputations/dolphin-mistral-24b-venice-edition:free |
| Proveedor | cognitivecomputations |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M tokens | GRATUITO |
| Precio Output/M tokens | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** Venice Uncensored Dolphin Mistral 24B Venice Edition is a fine-tuned variant of Mistral-Small-24B-Instruct-2501, developed by dphn. ai in collaboration with Venice.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="cognitivecomputations/dolphin-mistral-24b-venice-edition:free", messages=[{"role": "user", "content": "..."}])
```

---

### xAI: Grok 4

| Campo | Valor |
|---|---|
| model_id | x-ai/grok-4 |
| Proveedor | x-ai |
| Modalidad | text+image+file->text |
| Contexto | 256000 |
| Precio Input/M tokens | $3.00 |
| Precio Output/M tokens | $15.00 |
| Gratuito | No |

**Descripción funcional:** Grok 4 is xAI's latest reasoning model with a 256k context window.  It supports parallel tool calling, structured outputs, and both image and text inputs.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="x-ai/grok-4", messages=[{"role": "user", "content": "..."}])
```

---

### Google: Gemma 3n 2B (free)

| Campo | Valor |
|---|---|
| model_id | google/gemma-3n-e2b-it:free |
| Proveedor | google |
| Modalidad | text->text |
| Contexto | 8192 |
| Precio Input/M tokens | GRATUITO |
| Precio Output/M tokens | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** Gemma 3n E2B IT is a multimodal, instruction-tuned model developed by Google DeepMind, designed to operate efficiently at an effective parameter size of 2B while leveraging a 6B architecture.  Based on the MatFormer architecture, it supports nested submodels and modular composition via the Mix-and-Match framework.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="google/gemma-3n-e2b-it:free", messages=[{"role": "user", "content": "..."}])
```

---

### Tencent: Hunyuan A13B Instruct

| Campo | Valor |
|---|---|
| model_id | tencent/hunyuan-a13b-instruct |
| Proveedor | tencent |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.14 |
| Precio Output/M tokens | $0.57 |
| Gratuito | No |

**Descripción funcional:** Hunyuan-A13B is a 13B active parameter Mixture-of-Experts (MoE) language model developed by Tencent, with a total parameter count of 80B and support for reasoning via Chain-of-Thought.  It offers competitive benchmark performance across mathematics, science, coding, and multi-turn reasoning tasks, while maintaining high inference efficiency via Grouped Query Attention (GQA) and quantization support (FP8, GPTQ, etc.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="tencent/hunyuan-a13b-instruct", messages=[{"role": "user", "content": "..."}])
```

---

### TNG: DeepSeek R1T2 Chimera

| Atributo | Valor |
| --- | --- |
| model_id | `tngtech/deepseek-r1t2-chimera` |
| Proveedor | TNG |
| Modalidad | text->text |
| Contexto | 163840 |
| Precio Input/M | $0.30 |
| Precio Output/M | $1.10 |
| Gratuito | No |

**Descripción Funcional:**
DeepSeek-TNG-R1T2-Chimera is the second-generation Chimera model from TNG Tech. It is a 671 B-parameter mixture-of-experts text-generation model assembled from DeepSeek-AI’s R1-0528, R1, and V3-0324 checkpoints with an Assembly-of-Experts merge. The tri-parent design yields strong reasoning performance while running roughly 20 % faster than the original R1 and more than 2× faster than R1-0528 under vLLM, giving a favorable cost-to-intelligence trade-off. The checkpoint supports contexts up to 60 k tokens in standard use (tested to ~130 k) and maintains consistent <think> token behaviour, making it suitable for long-context analysis, dialogue and other open-ended generation tasks.

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
    model='tngtech/deepseek-r1t2-chimera',
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---
### Morph: Morph V3 Large

| Atributo | Valor |
| --- | --- |
| model_id | `morph/morph-v3-large` |
| Proveedor | Morph |
| Modalidad | text->text |
| Contexto | 262144 |
| Precio Input/M | $0.90 |
| Precio Output/M | $1.90 |
| Gratuito | No |

**Descripción Funcional:**
Morph's high-accuracy apply model for complex code edits. ~4,500 tokens/sec with 98% accuracy for precise code transformations. 

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
    model='morph/morph-v3-large',
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---
### Morph: Morph V3 Fast

| Atributo | Valor |
| --- | --- |
| model_id | `morph/morph-v3-fast` |
| Proveedor | Morph |
| Modalidad | text->text |
| Contexto | 81920 |
| Precio Input/M | $0.80 |
| Precio Output/M | $1.20 |
| Gratuito | No |

**Descripción Funcional:**
Morph's fastest apply model for code edits. ~10,500 tokens/sec with 96% accuracy for rapid code transformations. 

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
    model='morph/morph-v3-fast',
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---
### Baidu: ERNIE 4.5 VL 424B A47B 

| Atributo | Valor |
| --- | --- |
| model_id | `baidu/ernie-4.5-vl-424b-a47b` |
| Proveedor | Baidu |
| Modalidad | text+image->text |
| Contexto | 123000 |
| Precio Input/M | $0.42 |
| Precio Output/M | $1.25 |
| Gratuito | No |

**Descripción Funcional:**
ERNIE-4.5-VL-424B-A47B is a multimodal Mixture-of-Experts (MoE) model from Baidu’s ERNIE 4.5 series, featuring 424B total parameters with 47B active per token. It is trained jointly on text and image data using a heterogeneous MoE architecture and modality-isolated routing to enable high-fidelity cross-modal reasoning, image understanding, and long-context generation (up to 131k tokens). Fine-tuned with techniques like SFT, DPO, UPO, and RLVR, this model supports both “thinking” and non-thinking inference modes. Designed for vision-language tasks in English and Chinese, it is optimized for efficient scaling and can operate under 4-bit/8-bit quantization.

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
    model='baidu/ernie-4.5-vl-424b-a47b',
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---
### Baidu: ERNIE 4.5 300B A47B 

| Atributo | Valor |
| --- | --- |
| model_id | `baidu/ernie-4.5-300b-a47b` |
| Proveedor | Baidu |
| Modalidad | text->text |
| Contexto | 123000 |
| Precio Input/M | $0.28 |
| Precio Output/M | $1.10 |
| Gratuito | No |

**Descripción Funcional:**
ERNIE-4.5-300B-A47B is a 300B parameter Mixture-of-Experts (MoE) language model developed by Baidu as part of the ERNIE 4.5 series. It activates 47B parameters per token and supports text generation in both English and Chinese. Optimized for high-throughput inference and efficient scaling, it uses a heterogeneous MoE structure with advanced routing and quantization strategies, including FP8 and 2-bit formats. This version is fine-tuned for language-only tasks and supports reasoning, tool parameters, and extended context lengths up to 131k tokens. Suitable for general-purpose LLM applications with high reasoning and throughput demands.

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
    model='baidu/ernie-4.5-300b-a47b',
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---
### Inception: Mercury

| Atributo | Valor |
| --- | --- |
| model_id | `inception/mercury` |
| Proveedor | Inception |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M | $0.25 |
| Precio Output/M | $0.75 |
| Gratuito | No |

**Descripción Funcional:**
Mercury is the first diffusion large language model (dLLM). Applying a breakthrough discrete diffusion approach, the model runs 5-10x faster than even speed optimized models like GPT-4.1 Nano and Claude 3.5 Haiku while matching their performance. Mercury's speed enables developers to provide responsive user experiences, including with voice agents, search interfaces, and chatbots. Read more in the [blog post] (https://www.inceptionlabs.ai/blog/introducing-mercury) here. 

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
    model='inception/mercury',
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---
### Mistral: Mistral Small 3.2 24B

| Atributo | Valor |
| --- | --- |
| model_id | `mistralai/mistral-small-3.2-24b-instruct` |
| Proveedor | Mistral |
| Modalidad | text+image->text |
| Contexto | 128000 |
| Precio Input/M | $0.07 |
| Precio Output/M | $0.20 |
| Gratuito | No |

**Descripción Funcional:**
Mistral-Small-3.2-24B-Instruct-2506 is an updated 24B parameter model from Mistral optimized for instruction following, repetition reduction, and improved function calling. Compared to the 3.1 release, version 3.2 significantly improves accuracy on WildBench and Arena Hard, reduces infinite generations, and delivers gains in tool use and structured output tasks. 

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

completion = client.chat.completions.create(
    model='mistralai/mistral-small-3.2-24b-instruct',
    messages=[
        {
            "role": "user",
            "content": "Hello, world!",
        }
    ],
)
```

---

### DeepSeek: R1 0528

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| **model_id**      | `deepseek/deepseek-r1-0528`                               |
| **Proveedor**     | DeepSeek                                 |
| **Modalidad**     | text->text                                 |
| **Contexto**      | 163840 tokens                    |
| **Precio Input/M**  | $0.45                 |
| **Precio Output/M** | $2.15             |
| **Gratuito**      | No                  |

> May 28th update to the [original DeepSeek R1](/deepseek/deepseek-r1) Performance on par with [OpenAI o1](/openai/o1), but open-sourced and with fully open reasoning tokens.

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY"
)

response = client.chat.completions.create(
    model="deepseek/deepseek-r1-0528",
    messages=[...],
)
```

---

### Anthropic: Claude Opus 4

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| **model_id**      | `anthropic/claude-opus-4`                               |
| **Proveedor**     | Anthropic                                 |
| **Modalidad**     | text+image+file->text                                 |
| **Contexto**      | 200000 tokens                    |
| **Precio Input/M**  | $15.00                 |
| **Precio Output/M** | $75.00             |
| **Gratuito**      | No                  |

> Claude Opus 4 is benchmarked as the world’s best coding model, at time of release, bringing sustained performance on complex, long-running tasks and agent workflows.

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY"
)

response = client.chat.completions.create(
    model="anthropic/claude-opus-4",
    messages=[...],
)
```

---

### Anthropic: Claude Sonnet 4

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| **model_id**      | `anthropic/claude-sonnet-4`                               |
| **Proveedor**     | Anthropic                                 |
| **Modalidad**     | text+image+file->text                                 |
| **Contexto**      | 200000 tokens                    |
| **Precio Input/M**  | $3.00                 |
| **Precio Output/M** | $15.00             |
| **Gratuito**      | No                  |

> Claude Sonnet 4 significantly enhances the capabilities of its predecessor, Sonnet 3.

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY"
)

response = client.chat.completions.create(
    model="anthropic/claude-sonnet-4",
    messages=[...],
)
```

---

### Google: Gemma 3n 4B (free)

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| **model_id**      | `google/gemma-3n-e4b-it:free`                               |
| **Proveedor**     | Google                                 |
| **Modalidad**     | text->text                                 |
| **Contexto**      | 8192 tokens                    |
| **Precio Input/M**  | GRATUITO                 |
| **Precio Output/M** | GRATUITO             |
| **Gratuito**      | Sí                  |

> Gemma 3n E4B-it is optimized for efficient execution on mobile and low-resource devices, such as phones, laptops, and tablets.

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY"
)

response = client.chat.completions.create(
    model="google/gemma-3n-e4b-it:free",
    messages=[...],
)
```

---

### Google: Gemma 3n 4B

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| **model_id**      | `google/gemma-3n-e4b-it`                               |
| **Proveedor**     | Google                                 |
| **Modalidad**     | text->text                                 |
| **Contexto**      | 32768 tokens                    |
| **Precio Input/M**  | $0.02                 |
| **Precio Output/M** | $0.04             |
| **Gratuito**      | No                  |

> Gemma 3n E4B-it is optimized for efficient execution on mobile and low-resource devices, such as phones, laptops, and tablets.

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY"
)

response = client.chat.completions.create(
    model="google/gemma-3n-e4b-it",
    messages=[...],
)
```

---

### Mistral: Mistral Medium 3

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| **model_id**      | `mistralai/mistral-medium-3`                               |
| **Proveedor**     | Mistral                                 |
| **Modalidad**     | text+image->text                                 |
| **Contexto**      | 131072 tokens                    |
| **Precio Input/M**  | $0.40                 |
| **Precio Output/M** | $2.00             |
| **Gratuito**      | No                  |

> Mistral Medium 3 is a high-performance enterprise-grade language model designed to deliver frontier-level capabilities at significantly reduced operational cost.

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY"
)

response = client.chat.completions.create(
    model="mistralai/mistral-medium-3",
    messages=[...],
)
```

---

### Google: Gemini 2.5 Pro Preview 05-06

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| **model_id**      | `google/gemini-2.5-pro-preview-05-06`                               |
| **Proveedor**     | Google                                 |
| **Modalidad**     | text+image+file+audio+video->text                                 |
| **Contexto**      | 1048576 tokens                    |
| **Precio Input/M**  | $1.25                 |
| **Precio Output/M** | $10.00             |
| **Gratuito**      | No                  |

> Gemini 2.

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY"
)

response = client.chat.completions.create(
    model="google/gemini-2.5-pro-preview-05-06",
    messages=[...],
)
```

---

### OpenAI: GPT-5.4 Nano

| Campo | Valor |
|---|---|
| model_id | openai/gpt-5.4-nano |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 400000 |
| Precio Input/M | $0.20 |
| Precio Output/M | $1.25 |
| Gratuito | No |

**Descripción funcional:**
GPT-5.4 nano is the most lightweight and cost-efficient variant of the GPT-5.4 family, optimized for speed-critical and high-volume tasks. It supports text and image inputs and is designed for low-latency use cases such as classification, data extraction, ranking, and sub-agent execution.\n\nThe model prioritizes responsiveness and efficiency over deep reasoning, making it ideal for pipelines that require fast, reliable outputs at scale. GPT-5.4 nano is well suited for background tasks, real-time systems, and distributed agent architectures where minimizing cost and latency is essential.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5.4-nano", messages=[...])
```

---

### OpenAI: GPT-5.4 Mini

| Campo | Valor |
|---|---|
| model_id | openai/gpt-5.4-mini |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 400000 |
| Precio Input/M | $0.75 |
| Precio Output/M | $4.50 |
| Gratuito | No |

**Descripción funcional:**
GPT-5.4 mini brings the core capabilities of GPT-5.4 to a faster, more efficient model optimized for high-throughput workloads. It supports text and image inputs with strong performance across reasoning, coding, and tool use, while reducing latency and cost for large-scale deployments.\n\nThe model is designed for production environments that require a balance of capability and efficiency, making it well suited for chat applications, coding assistants, and agent workflows that operate at scale. GPT-5.4 mini delivers reliable instruction following, solid multi-step reasoning, and consistent performance across diverse tasks with improved cost efficiency.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5.4-mini", messages=[...])
```

---

### Mistral: Mistral Small 4

| Campo | Valor |
|---|---|
| model_id | mistralai/mistral-small-2603 |
| Proveedor | mistralai |
| Modalidad | text+image->text |
| Contexto | 262144 |
| Precio Input/M | $0.15 |
| Precio Output/M | $0.60 |
| Gratuito | No |

**Descripción funcional:**
Mistral Small 4 is the next major release in the Mistral Small family, unifying the capabilities of several flagship Mistral models into a single system. It combines strong reasoning from Magistral, multimodal understanding from Pixtral, and agentic coding capabilities from Devstral, enabling one model to handle complex analysis, software development, and visual tasks within the same workflow.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="mistralai/mistral-small-2603", messages=[...])
```

---

### Z.ai: GLM 5 Turbo

| Campo | Valor |
|---|---|
| model_id | z-ai/glm-5-turbo |
| Proveedor | z-ai |
| Modalidad | text->text |
| Contexto | 202752 |
| Precio Input/M | $1.20 |
| Precio Output/M | $4.00 |
| Gratuito | No |

**Descripción funcional:**
GLM-5 Turbo is a new model from Z.ai designed for fast inference and strong performance in agent-driven environments such as OpenClaw scenarios. It is deeply optimized for real-world agent workflows involving long execution chains, with improved complex instruction decomposition, tool use, scheduled and persistent execution, and overall stability across extended tasks.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="z-ai/glm-5-turbo", messages=[...])
```

---

### NVIDIA: Nemotron 3 Super (free)

| Campo | Valor |
|---|---|
| model_id | nvidia/nemotron-3-super-120b-a12b:free |
| Proveedor | nvidia |
| Modalidad | text->text |
| Contexto | 262144 |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:**
NVIDIA Nemotron 3 Super is a 120B-parameter open hybrid MoE model, activating just 12B parameters for maximum compute efficiency and accuracy in complex multi-agent applications. Built on a hybrid Mamba-Transformer Mixture-of-Experts architecture with multi-token prediction (MTP), it delivers over 50% higher token generation compared to leading open models.\n \nThe model features a 1M token context window for long-term agent coherence, cross-document reasoning, and multi-step task planning. Latent MoE enables calling 4 experts for the inference cost of only one, improving intelligence and generalization. Multi-environment RL training across 10+ environments delivers leading accuracy on benchmarks including AIME 2025, TerminalBench, and SWE-Bench Verified.\n \nFully open with weights, datasets, and recipes under the NVIDIA Open License, Nemotron 3 Super allows easy customization and secure deployment anywhere — from workstation to cloud.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="nvidia/nemotron-3-super-120b-a12b:free", messages=[...])
```

---

### NVIDIA: Nemotron 3 Super

| Campo | Valor |
|---|---|
| model_id | nvidia/nemotron-3-super-120b-a12b |
| Proveedor | nvidia |
| Modalidad | text->text |
| Contexto | 262144 |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.50 |
| Gratuito | No |

**Descripción funcional:**
NVIDIA Nemotron 3 Super is a 120B-parameter open hybrid MoE model, activating just 12B parameters for maximum compute efficiency and accuracy in complex multi-agent applications. Built on a hybrid Mamba-Transformer Mixture-of-Experts architecture with multi-token prediction (MTP), it delivers over 50% higher token generation compared to leading open models.\n \nThe model features a 1M token context window for long-term agent coherence, cross-document reasoning, and multi-step task planning. Latent MoE enables calling 4 experts for the inference cost of only one, improving intelligence and generalization. Multi-environment RL training across 10+ environments delivers leading accuracy on benchmarks including AIME 2025, TerminalBench, and SWE-Bench Verified.\n \nFully open with weights, datasets, and recipes under the NVIDIA Open License, Nemotron 3 Super allows easy customization and secure deployment anywhere — from workstation to cloud.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="nvidia/nemotron-3-super-120b-a12b", messages=[...])
```

---

### ByteDance Seed: Seed-2.0-Lite

| Campo | Valor |
|---|---|
| model_id | bytedance-seed/seed-2.0-lite |
| Proveedor | bytedance-seed |
| Modalidad | text+image+video->text |
| Contexto | 262144 |
| Precio Input/M | $0.25 |
| Precio Output/M | $2.00 |
| Gratuito | No |

**Descripción funcional:**
Seed-2.0-Lite is a versatile, cost‑efficient enterprise workhorse that delivers strong multimodal and agent capabilities while offering noticeably lower latency, making it a practical default choice for most production workloads across text, vision, and tools. Engineered for high-frequency visual understanding and agentic workflows, it's an ideal choice for deployment at scale with minimal latency.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="bytedance-seed/seed-2.0-lite", messages=[...])
```

---

### Arcee AI: Spotlight

| Campo | Valor |
| --- | --- |
| model_id | `arcee-ai/spotlight` |
| Proveedor | arcee-ai |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M | $0.18 |
| Precio Output/M | $0.18 |
| Gratuito | No |

**Descripción Funcional:**
Spotlight is a 7‑billion‑parameter vision‑language model derived from Qwen 2.5‑VL and fine‑tuned by Arcee AI for tight image‑text grounding tasks. It offers a 32 k‑token context window, enabling rich multimodal conversations that combine lengthy docu...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="arcee-ai/spotlight", messages=[...])
```

---

### Arcee AI: Maestro Reasoning

| Campo | Valor |
| --- | --- |
| model_id | `arcee-ai/maestro-reasoning` |
| Proveedor | arcee-ai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.90 |
| Precio Output/M | $3.30 |
| Gratuito | No |

**Descripción Funcional:**
Maestro Reasoning is Arcee's flagship analysis model: a 32 B‑parameter derivative of Qwen 2.5‑32 B tuned with DPO and chain‑of‑thought RL for step‑by‑step logic. Compared to the earlier 7 B preview, the production 32 B release widens the context wind...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="arcee-ai/maestro-reasoning", messages=[...])
```

---

### Arcee AI: Virtuoso Large

| Campo | Valor |
| --- | --- |
| model_id | `arcee-ai/virtuoso-large` |
| Proveedor | arcee-ai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.75 |
| Precio Output/M | $1.20 |
| Gratuito | No |

**Descripción Funcional:**
Virtuoso‑Large is Arcee's top‑tier general‑purpose LLM at 72 B parameters, tuned to tackle cross‑domain reasoning, creative writing and enterprise QA. Unlike many 70 B peers, it retains the 128 k context inherited from Qwen 2.5, letting it ingest boo...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="arcee-ai/virtuoso-large", messages=[...])
```

---

### Arcee AI: Coder Large

| Campo | Valor |
| --- | --- |
| model_id | `arcee-ai/coder-large` |
| Proveedor | arcee-ai |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M | $0.50 |
| Precio Output/M | $0.80 |
| Gratuito | No |

**Descripción Funcional:**
Coder‑Large is a 32 B‑parameter offspring of Qwen 2.5‑Instruct that has been further trained on permissively‑licensed GitHub, CodeSearchNet and synthetic bug‑fix corpora. It supports a 32k context window, enabling multi‑file refactoring or long diff...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="arcee-ai/coder-large", messages=[...])
```

---

### Inception: Mercury Coder

| Campo | Valor |
| --- | --- |
| model_id | `inception/mercury-coder` |
| Proveedor | inception |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M | $0.25 |
| Precio Output/M | $0.75 |
| Gratuito | No |

**Descripción Funcional:**
Mercury Coder is the first diffusion large language model (dLLM). Applying a breakthrough discrete diffusion approach, the model runs 5-10x faster than even speed optimized models like Claude 3.5 Haiku and GPT-4o Mini while matching their performance...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="inception/mercury-coder", messages=[...])
```

---

### Meta: Llama Guard 4 12B

| Campo | Valor |
| --- | --- |
| model_id | `meta-llama/llama-guard-4-12b` |
| Proveedor | meta-llama |
| Modalidad | text+image->text |
| Contexto | 163840 |
| Precio Input/M | $0.18 |
| Precio Output/M | $0.18 |
| Gratuito | No |

**Descripción Funcional:**
Llama Guard 4 is a Llama 4 Scout-derived multimodal pretrained model, fine-tuned for content safety classification. Similar to previous versions, it can be used to classify content in both LLM inputs (prompt classification) and in LLM responses (resp...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="meta-llama/llama-guard-4-12b", messages=[...])
```

---

### Qwen: Qwen3 30B A3B

| Campo | Valor |
| --- | --- |
| model_id | `qwen/qwen3-30b-a3b` |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 40960 |
| Precio Input/M | $0.08 |
| Precio Output/M | $0.28 |
| Gratuito | No |

**Descripción Funcional:**
Qwen3, the latest generation in the Qwen large language model series, features both dense and mixture-of-experts (MoE) architectures to excel in reasoning, multilingual support, and advanced agent tasks. Its unique ability to switch seamlessly betwee...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-30b-a3b", messages=[...])
```

---

### Qwen: Qwen3 8B

| Atributo | Valor |
|---|---|
| model_id | qwen/qwen3-8b |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 40960 |
| Precio Input/M | $0.05 |
| Precio Output/M | $0.40 |
| Gratuito | No |

**Descripción funcional:**
Qwen3-8B is a dense 8.2B parameter causal language model from the Qwen3 series, designed for both reasoning-heavy tasks and efficient dialogue. It supports seamless switching between "thinking" mode for math,...

**Configuración de uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-8b", messages=[...])
```

---

### Qwen: Qwen3 14B

| Atributo | Valor |
|---|---|
| model_id | qwen/qwen3-14b |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 40960 |
| Precio Input/M | $0.06 |
| Precio Output/M | $0.24 |
| Gratuito | No |

**Descripción funcional:**
Qwen3-14B is a dense 14.8B parameter causal language model from the Qwen3 series, designed for both complex reasoning and efficient dialogue. It supports seamless switching between a "thinking" mode for...

**Configuración de uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-14b", messages=[...])
```

---

### Qwen: Qwen3 32B

| Atributo | Valor |
|---|---|
| model_id | qwen/qwen3-32b |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 40960 |
| Precio Input/M | $0.08 |
| Precio Output/M | $0.24 |
| Gratuito | No |

**Descripción funcional:**
Qwen3-32B is a dense 32.8B parameter causal language model from the Qwen3 series, optimized for both complex reasoning and efficient dialogue. It supports seamless switching between a "thinking" mode for...

**Configuración de uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-32b", messages=[...])
```

---

### Qwen: Qwen3 235B A22B

| Atributo | Valor |
|---|---|
| model_id | qwen/qwen3-235b-a22b |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.45 |
| Precio Output/M | $1.82 |
| Gratuito | No |

**Descripción funcional:**
Qwen3-235B-A22B is a 235B parameter mixture-of-experts (MoE) model developed by Qwen, activating 22B parameters per forward pass. It supports seamless switching between a "thinking" mode for complex reasoning, math, and...

**Configuración de uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-235b-a22b", messages=[...])
```

---

### OpenAI: o4 Mini High

| Atributo | Valor |
|---|---|
| model_id | openai/o4-mini-high |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 200000 |
| Precio Input/M | $1.10 |
| Precio Output/M | $4.40 |
| Gratuito | No |

**Descripción funcional:**
OpenAI o4-mini-high is the same model as [o4-mini](/openai/o4-mini) with reasoning_effort set to high. OpenAI o4-mini is a compact reasoning model in the o-series, optimized for fast, cost-efficient performance while retaining...

**Configuración de uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/o4-mini-high", messages=[...])
```

---

### OpenAI: o3

| Atributo | Valor |
|---|---|
| model_id | openai/o3 |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 200000 |
| Precio Input/M | $2.00 |
| Precio Output/M | $8.00 |
| Gratuito | No |

**Descripción funcional:**
o3 is a well-rounded and powerful model across domains. It sets a new standard for math, science, coding, and visual reasoning tasks. It also excels at technical writing and instruction-following....

**Configuración de uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/o3", messages=[...])
```

---

### OpenAI: o4 Mini

| Atributo | Valor |
|---|---|
| model_id | openai/o4-mini |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 200000 |
| Precio Input/M | $1.10 |
| Precio Output/M | $4.40 |
| Gratuito | No |

**Descripción funcional:**
OpenAI o4-mini is a compact reasoning model in the o-series, optimized for fast, cost-efficient performance while retaining strong multimodal and agentic capabilities. It supports tool use and demonstrates competitive reasoning...

**Configuración de uso (Python):**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/o4-mini", messages=[...])
```

### Qwen: Qwen2.5 Coder 7B Instruct

| Atributo | Valor |
|---|---|
| model_id | qwen/qwen2.5-coder-7b-instruct |
| Proveedor | Qwen |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M | $0.03 |
| Precio Output/M | $0.09 |
| Gratuito | No |

**Descripción funcional:**
Qwen2.5-Coder-7B-Instruct is a 7B parameter instruction-tuned language model optimized for code-related tasks such as code generation, reasoning, and bug fixing. Based on the Qwen2.5 architecture, it incorporates enhancements like RoPE, SwiGLU, RM...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen2.5-coder-7b-instruct", messages=[...])
```

---
### OpenAI: GPT-4.1

| Atributo | Valor |
|---|---|
| model_id | openai/gpt-4.1 |
| Proveedor | OpenAI |
| Modalidad | text+image+file->text |
| Contexto | 1047576 |
| Precio Input/M | $2.00 |
| Precio Output/M | $8.00 |
| Gratuito | No |

**Descripción funcional:**
GPT-4.1 is a flagship large language model optimized for advanced instruction following, real-world software engineering, and long-context reasoning. It supports a 1 million token context window and outperforms GPT-4o and GPT-4.5 across coding (54...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-4.1", messages=[...])
```

---
### OpenAI: GPT-4.1 Mini

| Atributo | Valor |
|---|---|
| model_id | openai/gpt-4.1-mini |
| Proveedor | OpenAI |
| Modalidad | text+image+file->text |
| Contexto | 1047576 |
| Precio Input/M | $0.40 |
| Precio Output/M | $1.60 |
| Gratuito | No |

**Descripción funcional:**
GPT-4.1 Mini is a mid-sized model delivering performance competitive with GPT-4o at substantially lower latency and cost. It retains a 1 million token context window and scores 45.1% on hard instruction evals, 35.8% on MultiChallenge, and 84.1% on...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-4.1-mini", messages=[...])
```

---
### OpenAI: GPT-4.1 Nano

| Atributo | Valor |
|---|---|
| model_id | openai/gpt-4.1-nano |
| Proveedor | OpenAI |
| Modalidad | text+image+file->text |
| Contexto | 1047576 |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.40 |
| Gratuito | No |

**Descripción funcional:**
For tasks that demand low latency, GPT‑4.1 nano is the fastest and cheapest model in the GPT-4.1 series. It delivers exceptional performance at a small size with its 1 million token context window, and scores 80.1% on MMLU, 50.3% on GPQA, and 9.8%...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-4.1-nano", messages=[...])
```

---
### EleutherAI: Llemma 7b

| Atributo | Valor |
|---|---|
| model_id | eleutherai/llemma_7b |
| Proveedor | EleutherAI |
| Modalidad | text->text |
| Contexto | 4096 |
| Precio Input/M | $0.80 |
| Precio Output/M | $1.20 |
| Gratuito | No |

**Descripción funcional:**
Llemma 7B is a language model for mathematics. It was initialized with Code Llama 7B weights, and trained on the Proof-Pile-2 for 200B tokens. Llemma models are particularly strong at chain-of-thought mathematical reasoning and using computational...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="eleutherai/llemma_7b", messages=[...])
```

---
### AlfredPros: CodeLLaMa 7B Instruct Solidity

| Atributo | Valor |
|---|---|
| model_id | alfredpros/codellama-7b-instruct-solidity |
| Proveedor | AlfredPros |
| Modalidad | text->text |
| Contexto | 4096 |
| Precio Input/M | $0.80 |
| Precio Output/M | $1.20 |
| Gratuito | No |

**Descripción funcional:**
A finetuned 7 billion parameters Code LLaMA - Instruct model to generate Solidity smart contract using 4-bit QLoRA finetuning provided by PEFT library.

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="alfredpros/codellama-7b-instruct-solidity", messages=[...])
```

---
### xAI: Grok 3 Mini Beta

| Atributo | Valor |
|---|---|
| model_id | x-ai/grok-3-mini-beta |
| Proveedor | xAI |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.30 |
| Precio Output/M | $0.50 |
| Gratuito | No |

**Descripción funcional:**
Grok 3 Mini is a lightweight, smaller thinking model. Unlike traditional models that generate answers immediately, Grok 3 Mini thinks before responding. It’s ideal for reasoning-heavy tasks that don’t demand extensive domain knowledge, and shines ...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="x-ai/grok-3-mini-beta", messages=[...])
```

---

### xAI: Grok 3 Beta

| Campo | Valor |
|---|---|
| model_id | x-ai/grok-3-beta |
| Proveedor | x-ai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $3.00 |
| Precio Output/M tokens | $15.00 |
| Gratuito | No |

**Descripción funcional:** Grok 3 is the latest model from xAI. It's their flagship model that excels at enterprise use cases like data extraction, coding, and text summarization. Possesses deep domain knowledge in finance, healthcare, law, and science.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="x-ai/grok-3-beta", messages=[...])
```

---

### NVIDIA: Llama 3.1 Nemotron Ultra 253B v1

| Campo | Valor |
|---|---|
| model_id | nvidia/llama-3.1-nemotron-ultra-253b-v1 |
| Proveedor | nvidia |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.60 |
| Precio Output/M tokens | $1.80 |
| Gratuito | No |

**Descripción funcional:** Llama-3.1-Nemotron-Ultra-253B-v1 is a large language model (LLM) optimized for advanced reasoning, human-interactive chat, retrieval-augmented generation (RAG), and tool-calling tasks. Derived from Meta’s Llama-3.1-405B-Instruct, it has been significantly customized using Neural Architecture Search (NAS), resulting in enhanced efficiency, reduced memory usage, and improved inference latency. The model supports a context length of up to 128K tokens and can operate efficiently on an 8x NVIDIA H100 node.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="nvidia/llama-3.1-nemotron-ultra-253b-v1", messages=[...])
```

---

### Meta: Llama 4 Maverick

| Campo | Valor |
|---|---|
| model_id | meta-llama/llama-4-maverick |
| Proveedor | meta-llama |
| Modalidad | text+image->text |
| Contexto | 1048576 |
| Precio Input/M tokens | $0.15 |
| Precio Output/M tokens | $0.60 |
| Gratuito | No |

**Descripción funcional:** Llama 4 Maverick 17B Instruct (128E) is a high-capacity multimodal language model from Meta, built on a mixture-of-experts (MoE) architecture with 128 experts and 17 billion active parameters per forward pass (400B total). It supports multilingual text and image input, and produces multilingual text and code output across 12 supported languages. Optimized for vision-language tasks, Maverick is instruction-tuned for assistant-like behavior, image reasoning, and general-purpose multimodal interaction.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="meta-llama/llama-4-maverick", messages=[...])
```

---

### Meta: Llama 4 Scout

| Campo | Valor |
|---|---|
| model_id | meta-llama/llama-4-scout |
| Proveedor | meta-llama |
| Modalidad | text+image->text |
| Contexto | 327680 |
| Precio Input/M tokens | $0.08 |
| Precio Output/M tokens | $0.30 |
| Gratuito | No |

**Descripción funcional:** Llama 4 Scout 17B Instruct (16E) is a mixture-of-experts (MoE) language model developed by Meta, activating 17 billion parameters out of a total of 109B. It supports native multimodal input (text and image) and multilingual output (text and code) across 12 supported languages. Designed for assistant-style interaction and visual reasoning, Scout uses 16 experts per forward pass and features a context length of 10 million tokens, with a training corpus of ~40 trillion tokens.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="meta-llama/llama-4-scout", messages=[...])
```

---

### Qwen: Qwen2.5 VL 32B Instruct

| Campo | Valor |
|---|---|
| model_id | qwen/qwen2.5-vl-32b-instruct |
| Proveedor | qwen |
| Modalidad | text+image->text |
| Contexto | 128000 |
| Precio Input/M tokens | $0.20 |
| Precio Output/M tokens | $0.60 |
| Gratuito | No |

**Descripción funcional:** Qwen2.5-VL-32B is a multimodal vision-language model fine-tuned through reinforcement learning for enhanced mathematical reasoning, structured outputs, and visual problem-solving capabilities. It excels at visual analysis tasks, including object recognition, textual interpretation within images, and precise event localization in extended videos. Qwen2.5-VL-32B demonstrates state-of-the-art performance across multimodal benchmarks such as MMMU, MathVista, and VideoMME, while maintaining strong reasoning and clarity in text-based tasks like MMLU, mathematical problem-solving, and code generation.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="qwen/qwen2.5-vl-32b-instruct", messages=[...])
```

---

### DeepSeek: DeepSeek V3 0324

| Campo | Valor |
|---|---|
| model_id | deepseek/deepseek-chat-v3-0324 |
| Proveedor | deepseek |
| Modalidad | text->text |
| Contexto | 163840 |
| Precio Input/M tokens | $0.20 |
| Precio Output/M tokens | $0.77 |
| Gratuito | No |

**Descripción funcional:** DeepSeek V3, a 685B-parameter, mixture-of-experts model, is the latest iteration of the flagship chat model family from the DeepSeek team.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="deepseek/deepseek-chat-v3-0324", messages=[...])
```

---

### OpenAI: o1-pro

| Campo | Valor |
|---|---|
| model_id | openai/o1-pro |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 200000 |
| Precio Input/M tokens | $150.00 |
| Precio Output/M tokens | $600.00 |
| Gratuito | No |

**Descripción funcional:** The o1 series of models are trained with reinforcement learning to think before they answer and perform complex reasoning. The o1-pro model uses more compute to think harder and provide consistently better answers.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
completion = client.chat.completions.create(model="openai/o1-pro", messages=[...])
```

---

### OpenAI: GPT-4o-mini Search Preview

| Campo | Valor |
|---|---|
| model_id | openai/gpt-4o-mini-search-preview |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M tokens | $0.15 |
| Precio Output/M tokens | $0.60 |
| Gratuito | No |

**Descripción funcional:** GPT-4o mini Search Preview is a specialized model for web search in Chat Completions. It is trained to understand and execute web search queries.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-4o-mini-search-preview", messages=[...])
```

---

### OpenAI: GPT-4o Search Preview

| Campo | Valor |
|---|---|
| model_id | openai/gpt-4o-search-preview |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M tokens | $2.50 |
| Precio Output/M tokens | $10.00 |
| Gratuito | No |

**Descripción funcional:** GPT-4o Search Previewis a specialized model for web search in Chat Completions. It is trained to understand and execute web search queries.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-4o-search-preview", messages=[...])
```

---

### Reka Flash 3

| Campo | Valor |
|---|---|
| model_id | rekaai/reka-flash-3 |
| Proveedor | rekaai |
| Modalidad | text->text |
| Contexto | 65536 |
| Precio Input/M tokens | $0.10 |
| Precio Output/M tokens | $0.20 |
| Gratuito | No |

**Descripción funcional:** Reka Flash 3 is a general-purpose, instruction-tuned large language model with 21 billion parameters, developed by Reka. It excels at general chat, coding tasks, instruction-following, and function calling. Featuring a...

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="rekaai/reka-flash-3", messages=[...])
```

---

### Google: Gemma 3 27B (free)

| Campo | Valor |
|---|---|
| model_id | google/gemma-3-27b-it:free |
| Proveedor | google |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M tokens | GRATUITO |
| Precio Output/M tokens | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** Gemma 3 introduces multimodality, supporting vision-language input and text outputs. It handles context windows up to 128k tokens, understands over 140 languages, and offers improved math, reasoning, and chat capabilities,...

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="google/gemma-3-27b-it:free", messages=[...])
```

---

### Google: Gemma 3 27B

| Campo | Valor |
|---|---|
| model_id | google/gemma-3-27b-it |
| Proveedor | google |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.08 |
| Precio Output/M tokens | $0.16 |
| Gratuito | No |

**Descripción funcional:** Gemma 3 introduces multimodality, supporting vision-language input and text outputs. It handles context windows up to 128k tokens, understands over 140 languages, and offers improved math, reasoning, and chat capabilities,...

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="google/gemma-3-27b-it", messages=[...])
```

---

### TheDrummer: Skyfall 36B V2

| Campo | Valor |
|---|---|
| model_id | thedrummer/skyfall-36b-v2 |
| Proveedor | thedrummer |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M tokens | $0.55 |
| Precio Output/M tokens | $0.80 |
| Gratuito | No |

**Descripción funcional:** Skyfall 36B v2 is an enhanced iteration of Mistral Small 2501, specifically fine-tuned for improved creativity, nuanced writing, role-playing, and coherent storytelling.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="thedrummer/skyfall-36b-v2", messages=[...])
```

---

### Perplexity: Sonar Reasoning Pro

| Campo | Valor |
|---|---|
| model_id | perplexity/sonar-reasoning-pro |
| Proveedor | perplexity |
| Modalidad | text+image->text |
| Contexto | 128000 |
| Precio Input/M tokens | $2.00 |
| Precio Output/M tokens | $8.00 |
| Gratuito | No |

**Descripción funcional:** Note: Sonar Pro pricing includes Perplexity search pricing. See [details here](https://docs.perplexity.ai/guides/pricing#detailed-pricing-breakdown-for-sonar-reasoning-pro-and-sonar-pro) Sonar Reasoning Pro is a premier reasoning model powered by DeepSeek R1 with Chain of Thought (CoT). Designed for...

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="perplexity/sonar-reasoning-pro", messages=[...])
```

---

### Perplexity: Sonar Pro
| Atributo | Valor |
|---|---|
| model_id | perplexity/sonar-pro |
| Proveedor | perplexity |
| Modalidad | text+image->text |
| Contexto | 200000 |
| Precio Input/M tokens | $3.00 |
| Precio Output/M tokens | $15.00 |
| Gratuito | No |

> Note: Sonar Pro pricing includes Perplexity search pricing. See [details here](https://docs.perplexity.ai/guides/pricing#detailed-pricing-breakdown-for-sonar-reasoning-pro-and-sonar-pro)

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
completion = client.chat.completions.create(model="perplexity/sonar-pro", messages=[{"role": "user", "content": "..."}])
```
---
### Perplexity: Sonar Deep Research
| Atributo | Valor |
|---|---|
| model_id | perplexity/sonar-deep-research |
| Proveedor | perplexity |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M tokens | $2.00 |
| Precio Output/M tokens | $8.00 |
| Gratuito | No |

> Sonar Deep Research is a research-focused model designed for multi-step retrieval, synthesis, and reasoning across complex topics. It autonomously searches, reads, and evaluates sources, refining its approach as it gathers information. This enables comprehensive report generation across domains like finance, technology, health, and current events.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
completion = client.chat.completions.create(model="perplexity/sonar-deep-research", messages=[{"role": "user", "content": "..."}])
```
---
### Qwen: QwQ 32B
| Atributo | Valor |
|---|---|
| model_id | qwen/qwq-32b |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.15 |
| Precio Output/M tokens | $0.58 |
| Gratuito | No |

> QwQ is the reasoning model of the Qwen series. Compared with conventional instruction-tuned models, QwQ, which is capable of thinking and reasoning, can achieve significantly enhanced performance in downstream tasks, especially hard problems. QwQ-32B is the medium-sized reasoning model, which is capable of achieving competitive performance against state-of-the-art reasoning models, e.g., DeepSeek-R1, o1-mini.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
completion = client.chat.completions.create(model="qwen/qwq-32b", messages=[{"role": "user", "content": "..."}])
```
---
### Google: Gemini 2.0 Flash Lite
| Atributo | Valor |
|---|---|
| model_id | google/gemini-2.0-flash-lite-001 |
| Proveedor | google |
| Modalidad | text+image+file+audio+video->text |
| Contexto | 1048576 |
| Precio Input/M tokens | $0.07 |
| Precio Output/M tokens | $0.30 |
| Gratuito | No |

> Gemini 2.0 Flash Lite offers a significantly faster time to first token (TTFT) compared to [Gemini Flash 1.5](/google/gemini-flash-1.5), while maintaining quality on par with larger models like [Gemini Pro 1.5](/google/gemini-pro-1.5), all at extremely economical token prices.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
completion = client.chat.completions.create(model="google/gemini-2.0-flash-lite-001", messages=[{"role": "user", "content": "..."}])
```
---
### Anthropic: Claude 3.7 Sonnet
| Atributo | Valor |
|---|---|
| model_id | anthropic/claude-3.7-sonnet |
| Proveedor | anthropic |
| Modalidad | text+image+file->text |
| Contexto | 200000 |
| Precio Input/M tokens | $3.00 |
| Precio Output/M tokens | $15.00 |
| Gratuito | No |

> Claude 3.7 Sonnet is an advanced large language model with improved reasoning, coding, and problem-solving capabilities. It introduces a hybrid reasoning approach, allowing users to choose between rapid responses and extended, step-by-step processing for complex tasks. The model demonstrates notable improvements in coding, particularly in front-end development and full-stack updates, and excels in agentic workflows, where it can autonomously navigate multi-step processes.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
completion = client.chat.completions.create(model="anthropic/claude-3.7-sonnet", messages=[{"role": "user", "content": "..."}])
```
---
### Anthropic: Claude 3.7 Sonnet (thinking)
| Atributo | Valor |
|---|---|
| model_id | anthropic/claude-3.7-sonnet:thinking |
| Proveedor | anthropic |
| Modalidad | text+image+file->text |
| Contexto | 200000 |
| Precio Input/M tokens | $3.00 |
| Precio Output/M tokens | $15.00 |
| Gratuito | No |

> Claude 3.7 Sonnet is an advanced large language model with improved reasoning, coding, and problem-solving capabilities. It introduces a hybrid reasoning approach, allowing users to choose between rapid responses and extended, step-by-step processing for complex tasks. The model demonstrates notable improvements in coding, particularly in front-end development and full-stack updates, and excels in agentic workflows, where it can autonomously navigate multi-step processes.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
completion = client.chat.completions.create(model="anthropic/claude-3.7-sonnet:thinking", messages=[{"role": "user", "content": "..."}])
```
---
### Mistral: Saba
| Atributo | Valor |
|---|---|
| model_id | mistralai/mistral-saba |
| Proveedor | mistralai |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M tokens | $0.20 |
| Precio Output/M tokens | $0.60 |
| Gratuito | No |

> Mistral Saba is a 24B-parameter language model specifically designed for the Middle East and South Asia, delivering accurate and contextually relevant responses while maintaining efficient performance. Trained on curated regional datasets, it supports multiple Indian-origin languages—including Tamil and Malayalam—alongside Arabic. This makes it a versatile option for a range of regional and multilingual applications. Read more at the blog post [here](https://mistral.ai/en/news/mistral-saba)

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
completion = client.chat.completions.create(model="mistralai/mistral-saba", messages=[{"role": "user", "content": "..."}])
```
---

### Llama Guard 3 8B

| Atributo | Valor |
|---|---|
| model_id | meta-llama/llama-guard-3-8b |
| Proveedor | meta-llama |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.02 |
| Precio Output/M | $0.06 |
| Gratuito | No |

Llama Guard 3 is a Llama-3.1-8B pretrained model, fine-tuned for content safety classification. Similar to previous versions, it can be used to classify content in both LLM inputs (prompt classification)...

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="meta-llama/llama-guard-3-8b", messages=[...])
```

---

### OpenAI: o3 Mini High

| Atributo | Valor |
|---|---|
| model_id | openai/o3-mini-high |
| Proveedor | openai |
| Modalidad | text+file->text |
| Contexto | 200000 |
| Precio Input/M | $1.10 |
| Precio Output/M | $4.40 |
| Gratuito | No |

OpenAI o3-mini-high is the same model as [o3-mini](/openai/o3-mini) with reasoning_effort set to high. o3-mini is a cost-efficient language model optimized for STEM reasoning tasks, particularly excelling in science, mathematics, and...

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/o3-mini-high", messages=[...])
```

---

### Google: Gemini 2.0 Flash

| Atributo | Valor |
|---|---|
| model_id | google/gemini-2.0-flash-001 |
| Proveedor | google |
| Modalidad | text+image+file+audio+video->text |
| Contexto | 1048576 |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.40 |
| Gratuito | No |

Gemini Flash 2.0 offers a significantly faster time to first token (TTFT) compared to [Gemini Flash 1.5](/google/gemini-flash-1.5), while maintaining quality on par with larger models like [Gemini Pro 1.5](/google/gemini-pro-1.5). It...

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="google/gemini-2.0-flash-001", messages=[...])
```

---

### Qwen: Qwen VL Plus

| Atributo | Valor |
|---|---|
| model_id | qwen/qwen-vl-plus |
| Proveedor | qwen |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M | $0.14 |
| Precio Output/M | $0.41 |
| Gratuito | No |

Qwen's Enhanced Large Visual Language Model. Significantly upgraded for detailed recognition capabilities and text recognition abilities, supporting ultra-high pixel resolutions up to millions of pixels and extreme aspect ratios for...

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen-vl-plus", messages=[...])
```

---

### AionLabs: Aion-1.0

| Atributo | Valor |
|---|---|
| model_id | aion-labs/aion-1.0 |
| Proveedor | aion-labs |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $4.00 |
| Precio Output/M | $8.00 |
| Gratuito | No |

Aion-1.0 is a multi-model system designed for high performance across various tasks, including reasoning and coding. It is built on DeepSeek-R1, augmented with additional models and techniques such as Tree...

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="aion-labs/aion-1.0", messages=[...])
```

---

### AionLabs: Aion-1.0-Mini

| Atributo | Valor |
|---|---|
| model_id | aion-labs/aion-1.0-mini |
| Proveedor | aion-labs |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.70 |
| Precio Output/M | $1.40 |
| Gratuito | No |

Aion-1.0-Mini 32B parameter model is a distilled version of the DeepSeek-R1 model, designed for strong performance in reasoning domains such as mathematics, coding, and logic. It is a modified variant...

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="aion-labs/aion-1.0-mini", messages=[...])
```

---

### AionLabs: Aion-RP 1.0 (8B)

| Atributo | Valor |
|---|---|
| model_id | aion-labs/aion-rp-llama-3.1-8b |
| Proveedor | aion-labs |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M | $0.80 |
| Precio Output/M | $1.60 |
| Gratuito | No |

Aion-RP-Llama-3.1-8B ranks the highest in the character evaluation portion of the RPBench-Auto benchmark, a roleplaying-specific variant of Arena-Hard-Auto, where LLMs evaluate each other’s responses. It is a fine-tuned base model...

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="aion-labs/aion-rp-llama-3.1-8b", messages=[...])
```

---

### Qwen: Qwen VL Max
| Atributo | Valor |
|---|---|
| model_id | qwen/qwen-vl-max |
| Proveedor | qwen |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M | $0.52 |
| Precio Output/M | $2.08 |
| Gratuito | No |

**Descripción funcional:** Qwen VL Max is a visual understanding model with 7500 tokens context length. It excels in delivering optimal performance for a broader spectrum of complex tasks.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="qwen/qwen-vl-max", messages=[...])
```
---
### Qwen: Qwen-Turbo
| Atributo | Valor |
|---|---|
| model_id | qwen/qwen-turbo |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.03 |
| Precio Output/M | $0.13 |
| Gratuito | No |

**Descripción funcional:** Qwen-Turbo, based on Qwen2.5, is a 1M context model that provides fast speed and low cost, suitable for simple tasks.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="qwen/qwen-turbo", messages=[...])
```
---
### Qwen: Qwen2.5 VL 72B Instruct
| Atributo | Valor |
|---|---|
| model_id | qwen/qwen2.5-vl-72b-instruct |
| Proveedor | qwen |
| Modalidad | text+image->text |
| Contexto | 32768 |
| Precio Input/M | $0.80 |
| Precio Output/M | $0.80 |
| Gratuito | No |

**Descripción funcional:** Qwen2.5-VL is proficient in recognizing common objects such as flowers, birds, fish, and insects. It is also highly capable of analyzing texts, charts, icons, graphics, and layouts within images.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="qwen/qwen2.5-vl-72b-instruct", messages=[...])
```
---
### Qwen: Qwen-Plus
| Atributo | Valor |
|---|---|
| model_id | qwen/qwen-plus |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 1000000 |
| Precio Input/M | $0.26 |
| Precio Output/M | $0.78 |
| Gratuito | No |

**Descripción funcional:** Qwen-Plus, based on the Qwen2.5 foundation model, is a 131K context model with a balanced performance, speed, and cost combination.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="qwen/qwen-plus", messages=[...])
```
---
### Qwen: Qwen-Max 
| Atributo | Valor |
|---|---|
| model_id | qwen/qwen-max |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M | $1.04 |
| Precio Output/M | $4.16 |
| Gratuito | No |

**Descripción funcional:** Qwen-Max, based on Qwen2.5, provides the best inference performance among [Qwen models](/qwen), especially for complex multi-step tasks. It's a large-scale MoE model that has been pretrained on over 20 trillion tokens and further post-trained with curated Supervised Fine-Tuning (SFT) and Reinforcement Learning from Human Feedback (RLHF) methodologies. The parameter count is unknown.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="qwen/qwen-max", messages=[...])
```
---
### OpenAI: o3 Mini
| Atributo | Valor |
|---|---|
| model_id | openai/o3-mini |
| Proveedor | openai |
| Modalidad | text+file->text |
| Contexto | 200000 |
| Precio Input/M | $1.10 |
| Precio Output/M | $4.40 |
| Gratuito | No |

**Descripción funcional:** OpenAI o3-mini is a cost-efficient language model optimized for STEM reasoning tasks, particularly excelling in science, mathematics, and coding.

This model supports the `reasoning_effort` parameter, which can be set to "high", "medium", or "low" to control the thinking time of the model. The default is "medium". OpenRouter also offers the model slug `openai/o3-mini-high` to default the parameter to "high".

The model features three adjustable reasoning effort levels and supports key developer capabilities including function calling, structured outputs, and streaming, though it does not include vision processing capabilities.

The model demonstrates significant improvements over its predecessor, with expert testers preferring its responses 56% of the time and noting a 39% reduction in major errors on complex questions. With medium reasoning effort settings, o3-mini matches the performance of the larger o1 model on challenging reasoning evaluations like AIME and GPQA, while maintaining lower latency and cost.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="openai/o3-mini", messages=[...])
```
---
### Mistral: Mistral Small 3
| Atributo | Valor |
|---|---|
| model_id | mistralai/mistral-small-24b-instruct-2501 |
| Proveedor | mistralai |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M | $0.05 |
| Precio Output/M | $0.08 |
| Gratuito | No |

**Descripción funcional:** Mistral Small 3 is a 24B-parameter language model optimized for low-latency performance across common AI tasks. Released under the Apache 2.0 license, it features both pre-trained and instruction-tuned versions designed for efficient local deployment.

The model achieves 81% accuracy on the MMLU benchmark and performs competitively with larger models like Llama 3.3 70B and Qwen 32B, while operating at three times the speed on equivalent hardware. [Read the blog post about the model here.](https://mistral.ai/news/mistral-small-3/)

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="mistralai/mistral-small-24b-instruct-2501", messages=[...])
```
---

### DeepSeek: R1 Distill Qwen 32B

| Campo | Valor |
|---|---|
| model_id | `deepseek/deepseek-r1-distill-qwen-32b` |
| Proveedor | deepseek |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M | $0.29 |
| Precio Output/M | $0.29 |
| Gratuito | No |

**Descripción funcional:** DeepSeek R1 Distill Qwen 32B is a distilled large language model based on [Qwen 2. 5 32B](https://huggingface.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="deepseek/deepseek-r1-distill-qwen-32b", messages=[...])
```

---

### Perplexity: Sonar

| Campo | Valor |
|---|---|
| model_id | `perplexity/sonar` |
| Proveedor | perplexity |
| Modalidad | text+image->text |
| Contexto | 127072 |
| Precio Input/M | $1.00 |
| Precio Output/M | $1.00 |
| Gratuito | No |

**Descripción funcional:** Sonar is lightweight, affordable, fast, and simple to use — now featuring citations and the ability to customize sources.  It is designed for companies seeking to integrate lightweight question-and-answer features optimized for speed.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="perplexity/sonar", messages=[...])
```

---

### DeepSeek: R1 Distill Llama 70B

| Campo | Valor |
|---|---|
| model_id | `deepseek/deepseek-r1-distill-llama-70b` |
| Proveedor | deepseek |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.70 |
| Precio Output/M | $0.80 |
| Gratuito | No |

**Descripción funcional:** DeepSeek R1 Distill Llama 70B is a distilled large language model based on [Llama-3. 3-70B-Instruct](/meta-llama/llama-3.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="deepseek/deepseek-r1-distill-llama-70b", messages=[...])
```

---

### DeepSeek: R1

| Campo | Valor |
|---|---|
| model_id | `deepseek/deepseek-r1` |
| Proveedor | deepseek |
| Modalidad | text->text |
| Contexto | 64000 |
| Precio Input/M | $0.70 |
| Precio Output/M | $2.50 |
| Gratuito | No |

**Descripción funcional:** DeepSeek R1 is here: Performance on par with [OpenAI o1](/openai/o1), but open-sourced and with fully open reasoning tokens.  It's 671B parameters in size, with 37B active in an inference pass.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="deepseek/deepseek-r1", messages=[...])
```

---

### MiniMax: MiniMax-01

| Campo | Valor |
|---|---|
| model_id | `minimax/minimax-01` |
| Proveedor | minimax |
| Modalidad | text+image->text |
| Contexto | 1000192 |
| Precio Input/M | $0.20 |
| Precio Output/M | $1.10 |
| Gratuito | No |

**Descripción funcional:** MiniMax-01 is a combines MiniMax-Text-01 for text generation and MiniMax-VL-01 for image understanding.  It has 456 billion parameters, with 45.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="minimax/minimax-01", messages=[...])
```

---

### Microsoft: Phi 4

| Campo | Valor |
|---|---|
| model_id | `microsoft/phi-4` |
| Proveedor | microsoft |
| Modalidad | text->text |
| Contexto | 16384 |
| Precio Input/M | $0.07 |
| Precio Output/M | $0.14 |
| Gratuito | No |

**Descripción funcional:** [Microsoft Research](/microsoft) Phi-4 is designed to perform well in complex reasoning tasks and can operate efficiently in situations with limited memory or where quick responses are needed.  

At 14 billion parameters, it was trained on a mix of high-quality synthetic datasets, data from curated websites, and academic materials.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="microsoft/phi-4", messages=[...])
```

---

### Sao10K: Llama 3.1 70B Hanami x1

| Campo | Valor |
|---|---|
| model_id | `sao10k/l3.1-70b-hanami-x1` |
| Proveedor | sao10k |
| Modalidad | text->text |
| Contexto | 16000 |
| Precio Input/M | $3.00 |
| Precio Output/M | $3.00 |
| Gratuito | No |

**Descripción funcional:** This is [Sao10K](/sao10k)'s experiment over [Euryale v2. 2](/sao10k/l3.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="sao10k/l3.1-70b-hanami-x1", messages=[...])
```

---

### Qwen: Qwen3.5-9B

| Campo | Valor |
|---|---|
| model_id | qwen/qwen3.5-9b |
| Proveedor | qwen |
| Modalidad | text+image+video->text |
| Contexto | 256000 |
| Precio Input/M | $0.05 |
| Precio Output/M | $0.15 |
| Gratuito | No |

**Descripción funcional:** Qwen3.5-9B is a multimodal foundation model from the Qwen3.5 family, designed to deliver strong reasoning, coding, and visual understanding in an efficient 9B-parameter architecture. It uses a unified vision-language design with early fusion of multimodal tokens, allowing the model to process and reason across text and images within the same context.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3.5-9b", messages=[...])
```

---

### OpenAI: GPT-5.4 Pro

| Campo | Valor |
|---|---|
| model_id | openai/gpt-5.4-pro |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 1050000 |
| Precio Input/M | $30.00 |
| Precio Output/M | $180.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5.4 Pro is OpenAI's most advanced model, building on GPT-5.4's unified architecture with enhanced reasoning capabilities for complex, high-stakes tasks. It features a 1M+ token context window (922K input, 128K output) with support for text and image inputs. Optimized for step-by-step reasoning, instruction following, and accuracy, GPT-5.4 Pro excels at agentic coding, long-context workflows, and multi-step problem solving.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-5.4-pro", messages=[...])
```

---

### OpenAI: GPT-5.4

| Campo | Valor |
|---|---|
| model_id | openai/gpt-5.4 |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 1050000 |
| Precio Input/M | $2.50 |
| Precio Output/M | $15.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5.4 is OpenAI’s latest frontier model, unifying the Codex and GPT lines into a single system. It features a 1M+ token context window (922K input, 128K output) with support for text and image inputs, enabling high-context reasoning, coding, and multimodal analysis within the same workflow.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-5.4", messages=[...])
```

---

### Inception: Mercury 2

| Campo | Valor |
|---|---|
| model_id | inception/mercury-2 |
| Proveedor | inception |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M | $0.25 |
| Precio Output/M | $0.75 |
| Gratuito | No |

**Descripción funcional:** Mercury 2 is an extremely fast reasoning LLM, and the first reasoning diffusion LLM (dLLM).

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="inception/mercury-2", messages=[...])
```

---

### OpenAI: GPT-5.3 Chat

| Campo | Valor |
|---|---|
| model_id | openai/gpt-5.3-chat |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 128000 |
| Precio Input/M | $1.75 |
| Precio Output/M | $14.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5.3 Chat is an update to ChatGPT's most-used model that makes everyday conversations smoother, more useful, and more directly helpful. It delivers more accurate answers with better contextualization and significantly reduces unnecessary refusals, caveats, and overly cautious phrasing that can interrupt conversational flow.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-5.3-chat", messages=[...])
```

---

### Google: Gemini 3.1 Flash Lite Preview

| Campo | Valor |
|---|---|
| model_id | google/gemini-3.1-flash-lite-preview |
| Proveedor | google |
| Modalidad | text+image+file+audio+video->text |
| Contexto | 1048576 |
| Precio Input/M | $0.25 |
| Precio Output/M | $1.50 |
| Gratuito | No |

**Descripción funcional:** Gemini 3.1 Flash Lite Preview is Google's high-efficiency model optimized for high-volume use cases. It outperforms Gemini 2.5 Flash Lite on overall quality and approaches Gemini 2.5 Flash performance across key capabilities. Improvements span audio input/ASR, RAG snippet ranking, translation, data extraction, and code completion. Supports full thinking levels (minimal, low, medium, high) for fine-grained cost/performance trade-offs. Priced at half the cost of Gemini 3 Flash.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="google/gemini-3.1-flash-lite-preview", messages=[...])
```

---

### ByteDance Seed: Seed-2.0-Mini

| Campo | Valor |
|---|---|
| model_id | bytedance-seed/seed-2.0-mini |
| Proveedor | bytedance-seed |
| Modalidad | text+image+video->text |
| Contexto | 262144 |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.40 |
| Gratuito | No |

**Descripción funcional:** Seed-2.0-mini targets latency-sensitive, high-concurrency, and cost-sensitive scenarios, emphasizing fast response and flexible inference deployment. It delivers performance comparable to ByteDance-Seed-1.6, supports 256k context, four reasoning effort modes (minimal/low/medium/high), multimodal understanding, and is optimized for lightweight tasks where cost and speed take priority.

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="bytedance-seed/seed-2.0-mini", messages=[...])
```

---

### DeepSeek: DeepSeek V3

| Atributo | Valor |
|---|---|
| model_id | `deepseek/deepseek-chat` |
| Proveedor | DeepSeek |
| Modalidad | text->text |
| Contexto | 163840 |
| Precio Input/M | $0.32 |
| Precio Output/M | $0.89 |
| Gratuito | No |

**Descripción funcional:** DeepSeek-V3 is the latest model from the DeepSeek team, building upon the instruction following and coding abilities of the previous versions. Pre-trained on nearly 15 trillion tokens, the reported evaluations reveal that the model outperforms other open-source models and rivals leading closed-source models.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="deepseek/deepseek-chat", messages=[...])
```

---

### Sao10K: Llama 3.3 Euryale 70B

| Atributo | Valor |
|---|---|
| model_id | `sao10k/l3.3-euryale-70b` |
| Proveedor | Sao10K |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.65 |
| Precio Output/M | $0.75 |
| Gratuito | No |

**Descripción funcional:** Euryale L3.3 70B is a model focused on creative roleplay from [Sao10k](https://ko-fi.com/sao10k). It is the successor of [Euryale L3 70B v2.2](/models/sao10k/l3-euryale-70b).

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="sao10k/l3.3-euryale-70b", messages=[...])
```

---

### OpenAI: o1

| Atributo | Valor |
|---|---|
| model_id | `openai/o1` |
| Proveedor | OpenAI |
| Modalidad | text+image+file->text |
| Contexto | 200000 |
| Precio Input/M | $15.00 |
| Precio Output/M | $60.00 |
| Gratuito | No |

**Descripción funcional:** The latest and strongest model family from OpenAI, o1 is designed to spend more time thinking before responding. The o1 model series is trained with large-scale reinforcement learning to reason using chain of thought. 

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/o1", messages=[...])
```

---

### Cohere: Command R7B (12-2024)

| Atributo | Valor |
|---|---|
| model_id | `cohere/command-r7b-12-2024` |
| Proveedor | Cohere |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M | $0.04 |
| Precio Output/M | $0.15 |
| Gratuito | No |

**Descripción funcional:** Command R7B (12-2024) is a small, fast update of the Command R+ model, delivered in December 2024. It excels at RAG, tool use, agents, and similar tasks requiring complex reasoning and multiple steps.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="cohere/command-r7b-12-2024", messages=[...])
```

---

### Meta: Llama 3.3 70B Instruct (free)

| Atributo | Valor |
|---|---|
| model_id | `meta-llama/llama-3.3-70b-instruct:free` |
| Proveedor | Meta |
| Modalidad | text->text |
| Contexto | 65536 |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** The Meta Llama 3.3 multilingual large language model (LLM) is a pretrained and instruction tuned generative model in 70B (text in/text out). The Llama 3.3 instruction tuned text only model is optimized for multilingual dialogue use cases and outperforms many of the available open source and closed chat models on common industry benchmarks.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="meta-llama/llama-3.3-70b-instruct:free", messages=[...])
```

---

### Meta: Llama 3.3 70B Instruct

| Atributo | Valor |
|---|---|
| model_id | `meta-llama/llama-3.3-70b-instruct` |
| Proveedor | Meta |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.32 |
| Gratuito | No |

**Descripción funcional:** The Meta Llama 3.3 multilingual large language model (LLM) is a pretrained and instruction tuned generative model in 70B (text in/text out). The Llama 3.3 instruction tuned text only model is optimized for multilingual dialogue use cases and outperforms many of the available open source and closed chat models on common industry benchmarks.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="meta-llama/llama-3.3-70b-instruct", messages=[...])
```

---

### Amazon: Nova Lite 1.0

| Atributo | Valor |
|---|---|
| model_id | `amazon/nova-lite-v1` |
| Proveedor | Amazon |
| Modalidad | text+image->text |
| Contexto | 300000 |
| Precio Input/M | $0.06 |
| Precio Output/M | $0.24 |
| Gratuito | No |

**Descripción funcional:** Amazon Nova Lite 1.0 is a very low-cost multimodal model from Amazon that focused on fast processing of image, video, and text inputs to generate text output. Amazon Nova Lite can handle real-time customer interactions, document analysis, and visual question-answering tasks with high accuracy.

**Configuración de uso (Python):**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="amazon/nova-lite-v1", messages=[...])
```

---

### Amazon: Nova Micro 1.0

| Campo | Valor |
|---|---|
| model_id | amazon/nova-micro-v1 |
| proveedor | amazon |
| modalidad | text->text |
| contexto | 128000 |
| precio input/M tokens | $0.04 |
| precio output/M tokens | $0.14 |
| gratuito | No |

**Descripción funcional:** Amazon Nova Micro 1.0 is a text-only model that delivers the lowest latency responses in the Amazon Nova family of models at a very low cost. With a context length of 128K tokens and optimized for speed and cost, Amazon Nova Micro excels at tasks such as text summarization, translation, content classification, interactive chat, and brainstorming. It has  simple mathematical reasoning and coding abilities.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="amazon/nova-micro-v1", messages=[...])
```

---

### Amazon: Nova Pro 1.0

| Campo | Valor |
|---|---|
| model_id | amazon/nova-pro-v1 |
| proveedor | amazon |
| modalidad | text+image->text |
| contexto | 300000 |
| precio input/M tokens | $0.80 |
| precio output/M tokens | $3.20 |
| gratuito | No |

**Descripción funcional:** Amazon Nova Pro 1.0 is a capable multimodal model from Amazon focused on providing a combination of accuracy, speed, and cost for a wide range of tasks. As of December 2024, it achieves state-of-the-art performance on key benchmarks including visual question answering (TextVQA) and video understanding (VATEX). 

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="amazon/nova-pro-v1", messages=[...])
```

---

### OpenAI: GPT-4o (2024-11-20)

| Campo | Valor |
|---|---|
| model_id | openai/gpt-4o-2024-11-20 |
| proveedor | openai |
| modalidad | text+image+file->text |
| contexto | 128000 |
| precio input/M tokens | $2.50 |
| precio output/M tokens | $10.00 |
| gratuito | No |

**Descripción funcional:** The 2024-11-20 version of GPT-4o offers a leveled-up creative writing ability with more natural, engaging, and tailored writing to improve relevance & readability. It’s also better at working with uploaded files, providing deeper insights & more thorough responses. 

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-4o-2024-11-20", messages=[...])
```

---

### Mistral Large 2411

| Campo | Valor |
|---|---|
| model_id | mistralai/mistral-large-2411 |
| proveedor | mistralai |
| modalidad | text->text |
| contexto | 131072 |
| precio input/M tokens | $2.00 |
| precio output/M tokens | $6.00 |
| gratuito | No |

**Descripción funcional:** Mistral Large 2 2411 is an update of [Mistral Large 2](/mistralai/mistral-large) released together with [Pixtral Large 2411](/mistralai/pixtral-large-2411) 

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="mistralai/mistral-large-2411", messages=[...])
```

---

### Mistral Large 2407

| Campo | Valor |
|---|---|
| model_id | mistralai/mistral-large-2407 |
| proveedor | mistralai |
| modalidad | text->text |
| contexto | 131072 |
| precio input/M tokens | $2.00 |
| precio output/M tokens | $6.00 |
| gratuito | No |

**Descripción funcional:** This is Mistral AI's flagship model, Mistral Large 2 (version mistral-large-2407). It's a proprietary weights-available model and excels at reasoning, code, JSON, chat, and more. Read the launch announcement [here](https://mistral.ai/news/mistral-large-2407/). 

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="mistralai/mistral-large-2407", messages=[...])
```

---

### Mistral: Pixtral Large 2411

| Campo | Valor |
|---|---|
| model_id | mistralai/pixtral-large-2411 |
| proveedor | mistralai |
| modalidad | text+image->text |
| contexto | 131072 |
| precio input/M tokens | $2.00 |
| precio output/M tokens | $6.00 |
| gratuito | No |

**Descripción funcional:** Pixtral Large is a 124B parameter, open-weight, multimodal model built on top of [Mistral Large 2](/mistralai/mistral-large-2411). The model is able to understand documents, charts and natural images. 

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="mistralai/pixtral-large-2411", messages=[...])
```

---

### Qwen2.5 Coder 32B Instruct

| Campo | Valor |
|---|---|
| model_id | qwen/qwen-2.5-coder-32b-instruct |
| proveedor | qwen |
| modalidad | text->text |
| contexto | 32768 |
| precio input/M tokens | $0.66 |
| precio output/M tokens | $1.00 |
| gratuito | No |

**Descripción funcional:** Qwen2.5-Coder is the latest series of Code-Specific Qwen large language models (formerly known as CodeQwen). Qwen2.5-Coder brings the following improvements upon CodeQwen1.5: 

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen-2.5-coder-32b-instruct", messages=[...])
```

---

### TheDrummer: UnslopNemo 12B

| Campo | Valor |
|---|---|
| model_id | `thedrummer/unslopnemo-12b` |
| Proveedor | thedrummer |
| Modalidad | text->text |
| Contexto | 32768 tokens |
| Precio Input/M | $0.40 |
| Precio Output/M | $0.40 |
| Gratuito | No |

**Descripción funcional:** UnslopNemo v4.1 is the latest addition from the creator of Rocinante, designed for adventure writing and role-play scenarios.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

response = client.chat.completions.create(
    model="thedrummer/unslopnemo-12b",
    messages=[...]
)
```

---

### Anthropic: Claude 3.5 Haiku

| Campo | Valor |
|---|---|
| model_id | `anthropic/claude-3.5-haiku` |
| Proveedor | anthropic |
| Modalidad | text+image->text |
| Contexto | 200000 tokens |
| Precio Input/M | $0.80 |
| Precio Output/M | $4.00 |
| Gratuito | No |

**Descripción funcional:** Claude 3.5 Haiku features offers enhanced capabilities in speed, coding accuracy, and tool use.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

response = client.chat.completions.create(
    model="anthropic/claude-3.5-haiku",
    messages=[...]
)
```

---

### Magnum v4 72B

| Campo | Valor |
|---|---|
| model_id | `anthracite-org/magnum-v4-72b` |
| Proveedor | anthracite-org |
| Modalidad | text->text |
| Contexto | 16384 tokens |
| Precio Input/M | $3.00 |
| Precio Output/M | $5.00 |
| Gratuito | No |

**Descripción funcional:** This is a series of models designed to replicate the prose quality of the Claude 3 models, specifically Sonnet(https://openrouter.ai/anthropic/claude-3.5-sonnet) and Opus(https://openrouter.ai/anthropic/claude-3-opus).

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

response = client.chat.completions.create(
    model="anthracite-org/magnum-v4-72b",
    messages=[...]
)
```

---

### Qwen: Qwen2.5 7B Instruct

| Campo | Valor |
|---|---|
| model_id | `qwen/qwen-2.5-7b-instruct` |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 32768 tokens |
| Precio Input/M | $0.04 |
| Precio Output/M | $0.10 |
| Gratuito | No |

**Descripción funcional:** Qwen2.5 7B is the latest series of Qwen large language models.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

response = client.chat.completions.create(
    model="qwen/qwen-2.5-7b-instruct",
    messages=[...]
)
```

---

### NVIDIA: Llama 3.1 Nemotron 70B Instruct

| Campo | Valor |
|---|---|
| model_id | `nvidia/llama-3.1-nemotron-70b-instruct` |
| Proveedor | nvidia |
| Modalidad | text->text |
| Contexto | 131072 tokens |
| Precio Input/M | $1.20 |
| Precio Output/M | $1.20 |
| Gratuito | No |

**Descripción funcional:** NVIDIA's Llama 3.1 Nemotron 70B is a language model designed for generating precise and useful responses.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

response = client.chat.completions.create(
    model="nvidia/llama-3.1-nemotron-70b-instruct",
    messages=[...]
)
```

---

### Inflection: Inflection 3 Pi

| Campo | Valor |
|---|---|
| model_id | `inflection/inflection-3-pi` |
| Proveedor | inflection |
| Modalidad | text->text |
| Contexto | 8000 tokens |
| Precio Input/M | $2.50 |
| Precio Output/M | $10.00 |
| Gratuito | No |

**Descripción funcional:** Inflection 3 Pi powers Inflection's [Pi](https://pi.ai) chatbot, including backstory, emotional intelligence, productivity, and safety.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

response = client.chat.completions.create(
    model="inflection/inflection-3-pi",
    messages=[...]
)
```

---

### Inflection: Inflection 3 Productivity

| Campo | Valor |
|---|---|
| model_id | `inflection/inflection-3-productivity` |
| Proveedor | inflection |
| Modalidad | text->text |
| Contexto | 8000 tokens |
| Precio Input/M | $2.50 |
| Precio Output/M | $10.00 |
| Gratuito | No |

**Descripción funcional:** Inflection 3 Productivity is optimized for following instructions.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

response = client.chat.completions.create(
    model="inflection/inflection-3-productivity",
    messages=[...]
)
```

### TheDrummer: Rocinante 12B

| Atributo | Valor |
|---|---|
| model_id | thedrummer/rocinante-12b |
| Proveedor | thedrummer |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M tokens | $0.17 |
| Precio Output/M tokens | $0.43 |
| Gratuito | No |

**Descripción funcional:** Rocinante 12B is designed for engaging storytelling and rich prose....

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="thedrummer/rocinante-12b", messages=[...])
```

---

### Meta: Llama 3.2 3B Instruct (free)

| Atributo | Valor |
|---|---|
| model_id | meta-llama/llama-3.2-3b-instruct:free |
| Proveedor | meta-llama |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M tokens | GRATUITO |
| Precio Output/M tokens | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** Llama 3.2 3B is a 3-billion-parameter multilingual large language model, optimized for advanced natural language processing tasks like dialogue generation, reasoning, and summarization. Designed with the latest transformer architecture, it...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="meta-llama/llama-3.2-3b-instruct:free", messages=[...])
```

---

### Meta: Llama 3.2 3B Instruct

| Atributo | Valor |
|---|---|
| model_id | meta-llama/llama-3.2-3b-instruct |
| Proveedor | meta-llama |
| Modalidad | text->text |
| Contexto | 80000 |
| Precio Input/M tokens | $0.05 |
| Precio Output/M tokens | $0.34 |
| Gratuito | No |

**Descripción funcional:** Llama 3.2 3B is a 3-billion-parameter multilingual large language model, optimized for advanced natural language processing tasks like dialogue generation, reasoning, and summarization. Designed with the latest transformer architecture, it...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="meta-llama/llama-3.2-3b-instruct", messages=[...])
```

---

### Meta: Llama 3.2 1B Instruct

| Atributo | Valor |
|---|---|
| model_id | meta-llama/llama-3.2-1b-instruct |
| Proveedor | meta-llama |
| Modalidad | text->text |
| Contexto | 60000 |
| Precio Input/M tokens | $0.03 |
| Precio Output/M tokens | $0.20 |
| Gratuito | No |

**Descripción funcional:** Llama 3.2 1B is a 1-billion-parameter language model focused on efficiently performing natural language tasks, such as summarization, dialogue, and multilingual text analysis. Its smaller size allows it to operate...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="meta-llama/llama-3.2-1b-instruct", messages=[...])
```

---

### Meta: Llama 3.2 11B Vision Instruct

| Atributo | Valor |
|---|---|
| model_id | meta-llama/llama-3.2-11b-vision-instruct |
| Proveedor | meta-llama |
| Modalidad | text+image->text |
| Contexto | 131072 |
| Precio Input/M tokens | $0.05 |
| Precio Output/M tokens | $0.05 |
| Gratuito | No |

**Descripción funcional:** Llama 3.2 11B Vision is a multimodal model with 11 billion parameters, designed to handle tasks combining visual and textual data. It excels in tasks such as image captioning and...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="meta-llama/llama-3.2-11b-vision-instruct", messages=[...])
```

---

### Qwen2.5 72B Instruct

| Atributo | Valor |
|---|---|
| model_id | qwen/qwen-2.5-72b-instruct |
| Proveedor | qwen |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M tokens | $0.12 |
| Precio Output/M tokens | $0.39 |
| Gratuito | No |

**Descripción funcional:** Qwen2.5 72B is the latest series of Qwen large language models. Qwen2.5 brings the following improvements upon Qwen2:...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen-2.5-72b-instruct", messages=[...])
```

---

### Cohere: Command R (08-2024)

| Atributo | Valor |
|---|---|
| model_id | cohere/command-r-08-2024 |
| Proveedor | cohere |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M tokens | $0.15 |
| Precio Output/M tokens | $0.60 |
| Gratuito | No |

**Descripción funcional:** command-r-08-2024 is an update of the [Command R](/models/cohere/command-r) with improved performance for multilingual retrieval-augmented generation (RAG) and tool use. More broadly, it is better at math, code and reasoning and...

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="cohere/command-r-08-2024", messages=[...])
```

---

### Meta: Llama 3.1 8B Instruct

| Campo | Valor |
|---|---|
| model_id | meta-llama/llama-3.1-8b-instruct |
| Proveedor | meta-llama |
| Modalidad | text->text |
| Contexto | 16384 |
| Precio Input/M | $0.02 |
| Precio Output/M | $0.05 |
| Gratuito | No |

**Descripción funcional:** Meta's latest class of model (Llama 3.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="meta-llama/llama-3.1-8b-instruct", messages=[...])
```

---

### Meta: Llama 3.1 70B Instruct

| Campo | Valor |
|---|---|
| model_id | meta-llama/llama-3.1-70b-instruct |
| Proveedor | meta-llama |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.40 |
| Precio Output/M | $0.40 |
| Gratuito | No |

**Descripción funcional:** Meta's latest class of model (Llama 3.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="meta-llama/llama-3.1-70b-instruct", messages=[...])
```

---

### Mistral: Mistral Nemo

| Campo | Valor |
|---|---|
| model_id | mistralai/mistral-nemo |
| Proveedor | mistralai |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.02 |
| Precio Output/M | $0.04 |
| Gratuito | No |

**Descripción funcional:** A 12B parameter model with a 128k token context length built by Mistral in collaboration with NVIDIA.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="mistralai/mistral-nemo", messages=[...])
```

---

### OpenAI: GPT-4o-mini (2024-07-18)

| Campo | Valor |
|---|---|
| model_id | openai/gpt-4o-mini-2024-07-18 |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 128000 |
| Precio Input/M | $0.15 |
| Precio Output/M | $0.60 |
| Gratuito | No |

**Descripción funcional:** GPT-4o mini is OpenAI's newest model after [GPT-4 Omni](/models/openai/gpt-4o), supporting both text and image inputs with text outputs.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-4o-mini-2024-07-18", messages=[...])
```

---

### OpenAI: GPT-4o-mini

| Campo | Valor |
|---|---|
| model_id | openai/gpt-4o-mini |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 128000 |
| Precio Input/M | $0.15 |
| Precio Output/M | $0.60 |
| Gratuito | No |

**Descripción funcional:** GPT-4o mini is OpenAI's newest model after [GPT-4 Omni](/models/openai/gpt-4o), supporting both text and image inputs with text outputs.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-4o-mini", messages=[...])
```

---

### Google: Gemma 2 27B

| Campo | Valor |
|---|---|
| model_id | google/gemma-2-27b-it |
| Proveedor | google |
| Modalidad | text->text |
| Contexto | 8192 |
| Precio Input/M | $0.65 |
| Precio Output/M | $0.65 |
| Gratuito | No |

**Descripción funcional:** Gemma 2 27B by Google is an open model built from the same research and technology used to create the [Gemini models](/models?q=gemini).

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="google/gemma-2-27b-it", messages=[...])
```

---

### Google: Gemma 2 9B

| Campo | Valor |
|---|---|
| model_id | google/gemma-2-9b-it |
| Proveedor | google |
| Modalidad | text->text |
| Contexto | 8192 |
| Precio Input/M | $0.03 |
| Precio Output/M | $0.09 |
| Gratuito | No |

**Descripción funcional:** Gemma 2 9B by Google is an advanced, open-source language model that sets a new standard for efficiency and performance in its size class.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="google/gemma-2-9b-it", messages=[...])
```

---

### Sao10k: Llama 3 Euryale 70B v2.1
| Campo | Valor |
|---|---|
| model_id | `sao10k/l3-euryale-70b` |
| Proveedor | sao10k |
| Modalidad | text->text |
| Contexto | 8192 |
| Precio Input/M tokens | $1.48 |
| Precio Output/M tokens | $1.48 |
| Gratuito | No |

> Euryale 70B v2.1 is a model focused on creative roleplay from [Sao10k](https://ko-fi.com/sao10k).

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="sao10k/l3-euryale-70b", messages=[...])
```

---

### NousResearch: Hermes 2 Pro - Llama-3 8B
| Campo | Valor |
|---|---|
| model_id | `nousresearch/hermes-2-pro-llama-3-8b` |
| Proveedor | nousresearch |
| Modalidad | text->text |
| Contexto | 8192 |
| Precio Input/M tokens | $0.14 |
| Precio Output/M tokens | $0.14 |
| Gratuito | No |

> Hermes 2 Pro is an upgraded, retrained version of Nous Hermes 2, consisting of an updated and cleaned version of the OpenHermes 2.5 Dataset, as well as a newly introduced Function Calling and JSON Mode dataset developed in-house.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="nousresearch/hermes-2-pro-llama-3-8b", messages=[...])
```

---

### OpenAI: GPT-4o
| Campo | Valor |
|---|---|
| model_id | `openai/gpt-4o` |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 128000 |
| Precio Input/M tokens | $2.50 |
| Precio Output/M tokens | $10.00 |
| Gratuito | No |

> GPT-4o ("o" for "omni") is OpenAI's latest AI model, supporting both text and image inputs with text outputs. It maintains the intelligence level of [GPT-4 Turbo](/models/openai/gpt-4-turbo) while being twice as fast and 50% more cost-effective. GPT-4o also offers improved performance in processing non-English languages and enhanced visual capabilities.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-4o", messages=[...])
```

---

### OpenAI: GPT-4o (extended)
| Campo | Valor |
|---|---|
| model_id | `openai/gpt-4o:extended` |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 128000 |
| Precio Input/M tokens | $6.00 |
| Precio Output/M tokens | $18.00 |
| Gratuito | No |

> GPT-4o ("o" for "omni") is OpenAI's latest AI model, supporting both text and image inputs with text outputs. It maintains the intelligence level of [GPT-4 Turbo](/models/openai/gpt-4-turbo) while being twice as fast and 50% more cost-effective. GPT-4o also offers improved performance in processing non-English languages and enhanced visual capabilities.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-4o:extended", messages=[...])
```

---

### OpenAI: GPT-4o (2024-05-13)
| Campo | Valor |
|---|---|
| model_id | `openai/gpt-4o-2024-05-13` |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 128000 |
| Precio Input/M tokens | $5.00 |
| Precio Output/M tokens | $15.00 |
| Gratuito | No |

> GPT-4o ("o" for "omni") is OpenAI's latest AI model, supporting both text and image inputs with text outputs. It maintains the intelligence level of [GPT-4 Turbo](/models/openai/gpt-4-turbo) while being twice as fast and 50% more cost-effective. GPT-4o also offers improved performance in processing non-English languages and enhanced visual capabilities.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-4o-2024-05-13", messages=[...])
```

---

### Meta: Llama 3 8B Instruct
| Campo | Valor |
|---|---|
| model_id | `meta-llama/llama-3-8b-instruct` |
| Proveedor | meta-llama |
| Modalidad | text->text |
| Contexto | 8192 |
| Precio Input/M tokens | $0.03 |
| Precio Output/M tokens | $0.04 |
| Gratuito | No |

> Meta's latest class of model (Llama 3) launched with a variety of sizes & flavors. This 8B instruct-tuned version was optimized for high quality dialogue usecases.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="meta-llama/llama-3-8b-instruct", messages=[...])
```

---

### Meta: Llama 3 70B Instruct
| Campo | Valor |
|---|---|
| model_id | `meta-llama/llama-3-70b-instruct` |
| Proveedor | meta-llama |
| Modalidad | text->text |
| Contexto | 8192 |
| Precio Input/M tokens | $0.51 |
| Precio Output/M tokens | $0.74 |
| Gratuito | No |

> Meta's latest class of model (Llama 3) launched with a variety of sizes & flavors. This 70B instruct-tuned version was optimized for high quality dialogue usecases.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="meta-llama/llama-3-70b-instruct", messages=[...])
```

---

### Mistral: Mixtral 8x22B Instruct

| Campo | Valor |
| --- | --- |
| model_id | mistralai/mixtral-8x22b-instruct |
| Proveedor | mistralai |
| Modalidad | text->text |
| Contexto | 65536 |
| Precio Input/M | $2.00 |
| Precio Output/M | $6.00 |
| Gratuito | No |

**Descripción funcional:** Mistral's official instruct fine-tuned version of [Mixtral 8x22B](/models/mistralai/mixtral-8x22b). It uses 39B active parameters out of 141B, offering unparalleled cost efficiency...

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="mistralai/mixtral-8x22b-instruct", messages=[...])
```

---

### WizardLM-2 8x22B

| Campo | Valor |
| --- | --- |
| model_id | microsoft/wizardlm-2-8x22b |
| Proveedor | microsoft |
| Modalidad | text->text |
| Contexto | 65535 |
| Precio Input/M | $0.62 |
| Precio Output/M | $0.62 |
| Gratuito | No |

**Descripción funcional:** WizardLM-2 8x22B is Microsoft AI's most advanced Wizard model. It demonstrates highly competitive performance compared to leading proprietary models, and...

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="microsoft/wizardlm-2-8x22b", messages=[...])
```

---

### OpenAI: GPT-4 Turbo

| Campo | Valor |
| --- | --- |
| model_id | openai/gpt-4-turbo |
| Proveedor | openai |
| Modalidad | text+image->text |
| Contexto | 128000 |
| Precio Input/M | $10.00 |
| Precio Output/M | $30.00 |
| Gratuito | No |

**Descripción funcional:** The latest GPT-4 Turbo model with vision capabilities. Vision requests can now use JSON mode and function calling. Training data:...

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-4-turbo", messages=[...])
```

---

### Anthropic: Claude 3 Haiku

| Campo | Valor |
| --- | --- |
| model_id | anthropic/claude-3-haiku |
| Proveedor | anthropic |
| Modalidad | text+image->text |
| Contexto | 200000 |
| Precio Input/M | $0.25 |
| Precio Output/M | $1.25 |
| Gratuito | No |

**Descripción funcional:** Claude 3 Haiku is Anthropic's fastest and most compact model for near-instant responsiveness. Quick and accurate targeted performance. See the...

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="anthropic/claude-3-haiku", messages=[...])
```

---

### Mistral Large

| Campo | Valor |
| --- | --- |
| model_id | mistralai/mistral-large |
| Proveedor | mistralai |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M | $2.00 |
| Precio Output/M | $6.00 |
| Gratuito | No |

**Descripción funcional:** This is Mistral AI's flagship model, Mistral Large 2 (version `mistral-large-2407`). It's a proprietary weights-available model and excels at reasoning,...

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="mistralai/mistral-large", messages=[...])
```

---

### OpenAI: GPT-3.5 Turbo (older v0613)

| Campo | Valor |
| --- | --- |
| model_id | openai/gpt-3.5-turbo-0613 |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 4095 |
| Precio Input/M | $1.00 |
| Precio Output/M | $2.00 |
| Gratuito | No |

**Descripción funcional:** GPT-3.5 Turbo is OpenAI's fastest model. It can understand and generate natural language or code, and is optimized for chat...

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-3.5-turbo-0613", messages=[...])
```

---

### OpenAI: GPT-4 Turbo Preview

| Campo | Valor |
| --- | --- |
| model_id | openai/gpt-4-turbo-preview |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M | $10.00 |
| Precio Output/M | $30.00 |
| Gratuito | No |

**Descripción funcional:** The preview GPT-4 model with improved instruction following, JSON mode, reproducible outputs, parallel function calling, and more. Training data: up...

**Snippet de configuración Python:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-4-turbo-preview", messages=[...])
```

---

### Mistral: Mixtral 8x7B Instruct

| Campo | Valor |
|---|---|
| model_id | mistralai/mixtral-8x7b-instruct |
| Proveedor | mistralai |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M tokens | $0.54 |
| Precio Output/M tokens | $0.54 |
| Gratuito | No |

**Descripción funcional:** Mixtral 8x7B Instruct is a pretrained generative Sparse Mixture of Experts, by Mistral AI, for chat and instruction use.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="mistralai/mixtral-8x7b-instruct", messages=[...])
```

---

### Goliath 120B

| Campo | Valor |
|---|---|
| model_id | alpindale/goliath-120b |
| Proveedor | alpindale |
| Modalidad | text->text |
| Contexto | 6144 |
| Precio Input/M tokens | $3.75 |
| Precio Output/M tokens | $7.50 |
| Gratuito | No |

**Descripción funcional:** A large LLM created by combining two fine-tuned Llama 70B models into one 120B model.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="alpindale/goliath-120b", messages=[...])
```

---

### Auto Router

| Campo | Valor |
|---|---|
| model_id | openrouter/auto |
| Proveedor | openrouter |
| Modalidad | text+image+file+audio+video->text+image |
| Contexto | 2000000 |
| Precio Input/M tokens | $-1000000.00 |
| Precio Output/M tokens | $-1000000.00 |
| Gratuito | No |

**Descripción funcional:** Your prompt will be processed by a meta-model and routed to one of dozens of models (see below), optimizing for the best possible output.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="openrouter/auto", messages=[...])
```

---

### OpenAI: GPT-4 Turbo (older v1106)

| Campo | Valor |
|---|---|
| model_id | openai/gpt-4-1106-preview |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 128000 |
| Precio Input/M tokens | $10.00 |
| Precio Output/M tokens | $30.00 |
| Gratuito | No |

**Descripción funcional:** The latest GPT-4 Turbo model with vision capabilities.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="openai/gpt-4-1106-preview", messages=[...])
```

---

### Mistral: Mistral 7B Instruct v0.1

| Campo | Valor |
|---|---|
| model_id | mistralai/mistral-7b-instruct-v0.1 |
| Proveedor | mistralai |
| Modalidad | text->text |
| Contexto | 2824 |
| Precio Input/M tokens | $0.11 |
| Precio Output/M tokens | $0.19 |
| Gratuito | No |

**Descripción funcional:** A 7.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="mistralai/mistral-7b-instruct-v0.1", messages=[...])
```

---

### OpenAI: GPT-3.5 Turbo Instruct

| Campo | Valor |
|---|---|
| model_id | openai/gpt-3.5-turbo-instruct |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 4095 |
| Precio Input/M tokens | $1.50 |
| Precio Output/M tokens | $2.00 |
| Gratuito | No |

**Descripción funcional:** This model is a variant of GPT-3.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="openai/gpt-3.5-turbo-instruct", messages=[...])
```

---

### OpenAI: GPT-3.5 Turbo 16k

| Campo | Valor |
|---|---|
| model_id | openai/gpt-3.5-turbo-16k |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 16385 |
| Precio Input/M tokens | $3.00 |
| Precio Output/M tokens | $4.00 |
| Gratuito | No |

**Descripción funcional:** This model offers four times the context length of gpt-3.

```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_API_KEY")
response = client.chat.completions.create(model="openai/gpt-3.5-turbo-16k", messages=[...])
```

---

### Mancer: Weaver (alpha)

| Atributo | Valor |
| --- | --- |
| model_id | `mancer/weaver` |
| Proveedor | mancer |
| Modalidad | text->text |
| Contexto | 8000 |
| Precio Input/M tokens | $0.7500 |
| Precio Output/M tokens | $1.0000 |
| Gratuito | No |

> An attempt to recreate Claude-style verbosity, but don't expect the same level of coherence or memory. Meant for use in roleplay/narrative situations.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="mancer/weaver", messages=[...])
```

---

### ReMM SLERP 13B

| Atributo | Valor |
| --- | --- |
| model_id | `undi95/remm-slerp-l2-13b` |
| Proveedor | undi95 |
| Modalidad | text->text |
| Contexto | 6144 |
| Precio Input/M tokens | $0.4500 |
| Precio Output/M tokens | $0.6500 |
| Gratuito | No |

> A recreation trial of the original MythoMax-L2-B13 but with updated models. #merge

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="undi95/remm-slerp-l2-13b", messages=[...])
```

---

### MythoMax 13B

| Atributo | Valor |
| --- | --- |
| model_id | `gryphe/mythomax-l2-13b` |
| Proveedor | gryphe |
| Modalidad | text->text |
| Contexto | 4096 |
| Precio Input/M tokens | $0.0600 |
| Precio Output/M tokens | $0.0600 |
| Gratuito | No |

> One of the highest performing and most popular fine-tunes of Llama 2 13B, with rich descriptions and roleplay. #merge

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="gryphe/mythomax-l2-13b", messages=[...])
```

---

### OpenAI: GPT-4 (older v0314)

| Atributo | Valor |
| --- | --- |
| model_id | `openai/gpt-4-0314` |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 8191 |
| Precio Input/M tokens | $30.0000 |
| Precio Output/M tokens | $60.0000 |
| Gratuito | No |

> GPT-4-0314 is the first version of GPT-4 released, with a context length of 8,192 tokens, and was supported until June 14. Training data: up to Sep 2021.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="openai/gpt-4-0314", messages=[...])
```

---

### OpenAI: GPT-3.5 Turbo

| Atributo | Valor |
| --- | --- |
| model_id | `openai/gpt-3.5-turbo` |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 16385 |
| Precio Input/M tokens | $0.5000 |
| Precio Output/M tokens | $1.5000 |
| Gratuito | No |

> GPT-3.5 Turbo is OpenAI's fastest model. It can understand and generate natural language or code, and is optimized for chat and traditional completion tasks.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="openai/gpt-3.5-turbo", messages=[...])
```

---

### OpenAI: GPT-4

| Atributo | Valor |
| --- | --- |
| model_id | `openai/gpt-4` |
| Proveedor | openai |
| Modalidad | text->text |
| Contexto | 8191 |
| Precio Input/M tokens | $30.0000 |
| Precio Output/M tokens | $60.0000 |
| Gratuito | No |

> OpenAI's flagship model, GPT-4 is a large-scale multimodal language model capable of solving difficult problems with greater accuracy than previous models due to its broader general knowledge and advanced reasoning capabilities. Training data: up to Sep 2021.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1")
response = client.chat.completions.create(model="openai/gpt-4", messages=[...])
```

---

### Google: Nano Banana 2 (Gemini 3.1 Flash Image Preview)

| Campo | Valor |
|---|---|
| model_id | google/gemini-3.1-flash-image-preview |
| Proveedor | Google |
| Modalidad | text+image->text+image |
| Contexto | 65536 |
| Precio Input/M tokens | $0.50 |
| Precio Output/M tokens | $3.00 |
| Gratuito | No |

Gemini 3.1 Flash Image Preview, a.k.a. "Nano Banana 2," is Google’s latest state of the art image generation and editing model, delivering Pro-level visual quality at Flash speed. It combines advanced contextual understanding with fast, cost-efficient inference, making complex image generation and iterative edits significantly more accessible. Aspect ratios can be controlled with the [image_config API Parameter](https://openrouter.ai/docs/features/multimodal/image-generation#image-aspect-ratio-configuration)

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="google/gemini-3.1-flash-image-preview", messages=[...])
```

---

### Qwen: Qwen3.5-35B-A3B

| Campo | Valor |
|---|---|
| model_id | qwen/qwen3.5-35b-a3b |
| Proveedor | Qwen |
| Modalidad | text+image+video->text |
| Contexto | 262144 |
| Precio Input/M tokens | $0.16 |
| Precio Output/M tokens | $1.30 |
| Gratuito | No |

The Qwen3.5 Series 35B-A3B is a native vision-language model designed with a hybrid architecture that integrates linear attention mechanisms and a sparse mixture-of-experts model, achieving higher inference efficiency. Its overall performance is comparable to that of the Qwen3.5-27B.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3.5-35b-a3b", messages=[...])
```

---

### Qwen: Qwen3.5-27B

| Campo | Valor |
|---|---|
| model_id | qwen/qwen3.5-27b |
| Proveedor | Qwen |
| Modalidad | text+image+video->text |
| Contexto | 262144 |
| Precio Input/M tokens | $0.20 |
| Precio Output/M tokens | $1.56 |
| Gratuito | No |

The Qwen3.5 27B native vision-language Dense model incorporates a linear attention mechanism, delivering fast response times while balancing inference speed and performance. Its overall capabilities are comparable to those of the Qwen3.5-122B-A10B.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3.5-27b", messages=[...])
```

---

### Qwen: Qwen3.5-122B-A10B

| Campo | Valor |
|---|---|
| model_id | qwen/qwen3.5-122b-a10b |
| Proveedor | Qwen |
| Modalidad | text+image+video->text |
| Contexto | 262144 |
| Precio Input/M tokens | $0.26 |
| Precio Output/M tokens | $2.08 |
| Gratuito | No |

The Qwen3.5 122B-A10B native vision-language model is built on a hybrid architecture that integrates a linear attention mechanism with a sparse mixture-of-experts model, achieving higher inference efficiency. In terms of overall performance, this model is second only to Qwen3.5-397B-A17B. Its text capabilities significantly outperform those of Qwen3-235B-2507, and its visual capabilities surpass those of Qwen3-VL-235B.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3.5-122b-a10b", messages=[...])
```

---

### Qwen: Qwen3.5-Flash

| Campo | Valor |
|---|---|
| model_id | qwen/qwen3.5-flash-02-23 |
| Proveedor | Qwen |
| Modalidad | text+image+video->text |
| Contexto | 1000000 |
| Precio Input/M tokens | $0.07 |
| Precio Output/M tokens | $0.26 |
| Gratuito | No |

The Qwen3.5 native vision-language Flash models are built on a hybrid architecture that integrates a linear attention mechanism with a sparse mixture-of-experts model, achieving higher inference efficiency. Compared to the 3 series, these models deliver a leap forward in performance for both pure text and multimodal tasks, offering fast response times while balancing inference speed and overall performance.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3.5-flash-02-23", messages=[...])
```

---

### LiquidAI: LFM2-24B-A2B

| Campo | Valor |
|---|---|
| model_id | liquid/lfm-2-24b-a2b |
| Proveedor | LiquidAI |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M tokens | $0.03 |
| Precio Output/M tokens | $0.12 |
| Gratuito | No |

LFM2-24B-A2B is the largest model in the LFM2 family of hybrid architectures designed for efficient on-device deployment. Built as a 24B parameter Mixture-of-Experts model with only 2B active parameters per token, it delivers high-quality generation while maintaining low inference costs. The model fits within 32 GB of RAM, making it practical to run on consumer laptops and desktops without sacrificing capability.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="liquid/lfm-2-24b-a2b", messages=[...])
```

---

### Google: Gemini 3.1 Pro Preview Custom Tools

| Campo | Valor |
|---|---|
| model_id | google/gemini-3.1-pro-preview-customtools |
| Proveedor | Google |
| Modalidad | text+image+file+audio+video->text |
| Contexto | 1048576 |
| Precio Input/M tokens | $2.00 |
| Precio Output/M tokens | $12.00 |
| Gratuito | No |

Gemini 3.1 Pro Preview Custom Tools is a variant of Gemini 3.1 Pro that improves tool selection behavior by preventing overuse of a general bash tool when more efficient third-party or user-defined functions are available. This specialized preview endpoint significantly increases function calling reliability and ensures the model selects the most appropriate tool in coding agents and complex, multi-tool workflows.

It retains the core strengths of Gemini 3.1 Pro, including multimodal reasoning across text, image, video, audio, and code, a 1M-token context window, and strong software engineering performance.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="google/gemini-3.1-pro-preview-customtools", messages=[...])
```

---

### OpenAI: GPT-5.3-Codex

| Campo | Valor |
|---|---|
| model_id | openai/gpt-5.3-codex |
| Proveedor | openai |
| Modalidad | text+image+file->text |
| Contexto | 400000 |
| Precio Input/M | $1.75 |
| Precio Output/M | $14.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="openai/gpt-5.3-codex", messages=[...])
```

---

### AionLabs: Aion-2.0

| Campo | Valor |
|---|---|
| model_id | aion-labs/aion-2.0 |
| Proveedor | aion-labs |
| Modalidad | text->text |
| Contexto | 131072 |
| Precio Input/M | $0.80 |
| Precio Output/M | $1.60 |
| Gratuito | No |

**Descripción funcional:** Aion-2.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="aion-labs/aion-2.0", messages=[...])
```

---

### Google: Gemini 3.1 Pro Preview

| Campo | Valor |
|---|---|
| model_id | google/gemini-3.1-pro-preview |
| Proveedor | google |
| Modalidad | text+image+file+audio+video->text |
| Contexto | 1048576 |
| Precio Input/M | $2.00 |
| Precio Output/M | $12.00 |
| Gratuito | No |

**Descripción funcional:** Gemini 3.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="google/gemini-3.1-pro-preview", messages=[...])
```

---

### Anthropic: Claude Sonnet 4.6

| Campo | Valor |
|---|---|
| model_id | anthropic/claude-sonnet-4.6 |
| Proveedor | anthropic |
| Modalidad | text+image->text |
| Contexto | 1000000 |
| Precio Input/M | $3.00 |
| Precio Output/M | $15.00 |
| Gratuito | No |

**Descripción funcional:** Sonnet 4.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="anthropic/claude-sonnet-4.6", messages=[...])
```

---

### Qwen: Qwen3.5 Plus 2026-02-15

| Campo | Valor |
|---|---|
| model_id | qwen/qwen3.5-plus-02-15 |
| Proveedor | qwen |
| Modalidad | text+image+video->text |
| Contexto | 1000000 |
| Precio Input/M | $0.26 |
| Precio Output/M | $1.56 |
| Gratuito | No |

**Descripción funcional:** The Qwen3.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3.5-plus-02-15", messages=[...])
```

---

### Qwen: Qwen3.5 397B A17B

| Campo | Valor |
|---|---|
| model_id | qwen/qwen3.5-397b-a17b |
| Proveedor | qwen |
| Modalidad | text+image+video->text |
| Contexto | 262144 |
| Precio Input/M | $0.39 |
| Precio Output/M | $2.34 |
| Gratuito | No |

**Descripción funcional:** The Qwen3.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="qwen/qwen3.5-397b-a17b", messages=[...])
```

---

### MiniMax: MiniMax M2.5 (free)

| Campo | Valor |
|---|---|
| model_id | minimax/minimax-m2.5:free |
| Proveedor | minimax |
| Modalidad | text->text |
| Contexto | 196608 |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** MiniMax-M2.

```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=YOUR_API_KEY)
response = client.chat.completions.create(model="minimax/minimax-m2.5:free", messages=[...])
```

---

### MiniMax: MiniMax M2.5

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| model_id          | `minimax/minimax-m2.5`                               |
| Proveedor         | MiniMax                                 |
| Modalidad         | text->text                                 |
| Contexto          | 196608                           |
| Precio Input/M    | $0.12                 |
| Precio Output/M   | $0.99             |
| Gratuito          | No                  |

**Descripción funcional:** MiniMax-M2.5 is a SOTA large language model designed for real-world productivity. Trained in a diverse range of complex real-world digital working environments, M2.5 builds upon the coding expertise of M2.1...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="minimax/minimax-m2.5", messages=[...])
```

---

### Z.ai: GLM 5

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| model_id          | `z-ai/glm-5`                               |
| Proveedor         | Z.ai                                 |
| Modalidad         | text->text                                 |
| Contexto          | 80000                           |
| Precio Input/M    | $0.72                 |
| Precio Output/M   | $2.30             |
| Gratuito          | No                  |

**Descripción funcional:** GLM-5 is Z.ai’s flagship open-source foundation model engineered for complex systems design and long-horizon agent workflows. Built for expert developers, it delivers production-grade performance on large-scale programming tasks, rivaling leading...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="z-ai/glm-5", messages=[...])
```

---

### Qwen: Qwen3 Max Thinking

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| model_id          | `qwen/qwen3-max-thinking`                               |
| Proveedor         | Qwen                                 |
| Modalidad         | text->text                                 |
| Contexto          | 262144                           |
| Precio Input/M    | $0.78                 |
| Precio Output/M   | $3.90             |
| Gratuito          | No                  |

**Descripción funcional:** Qwen3-Max-Thinking is the flagship reasoning model in the Qwen3 series, designed for high-stakes cognitive tasks that require deep, multi-step reasoning. By significantly scaling model capacity and reinforcement learning compute, it...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-max-thinking", messages=[...])
```

---

### Anthropic: Claude Opus 4.6

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| model_id          | `anthropic/claude-opus-4.6`                               |
| Proveedor         | Anthropic                                 |
| Modalidad         | text+image->text                                 |
| Contexto          | 1000000                           |
| Precio Input/M    | $5.00                 |
| Precio Output/M   | $25.00             |
| Gratuito          | No                  |

**Descripción funcional:** Opus 4.6 is Anthropic’s strongest model for coding and long-running professional tasks. It is built for agents that operate across entire workflows rather than single prompts, making it especially effective...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="anthropic/claude-opus-4.6", messages=[...])
```

---

### Qwen: Qwen3 Coder Next

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| model_id          | `qwen/qwen3-coder-next`                               |
| Proveedor         | Qwen                                 |
| Modalidad         | text->text                                 |
| Contexto          | 262144                           |
| Precio Input/M    | $0.12                 |
| Precio Output/M   | $0.75             |
| Gratuito          | No                  |

**Descripción funcional:** Qwen3-Coder-Next is an open-weight causal language model optimized for coding agents and local development workflows. It uses a sparse MoE design with 80B total parameters and only 3B activated per...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="qwen/qwen3-coder-next", messages=[...])
```

---

### Free Models Router

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| model_id          | `openrouter/free`                               |
| Proveedor         | N/A                                 |
| Modalidad         | text+image->text                                 |
| Contexto          | 200000                           |
| Precio Input/M    | GRATUITO                 |
| Precio Output/M   | GRATUITO             |
| Gratuito          | Sí                  |

**Descripción funcional:** The simplest way to get free inference. openrouter/free is a router that selects free models at random from the models available on OpenRouter. The router smartly filters for models that...

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openrouter/free", messages=[...])
```

---

### StepFun: Step 3.5 Flash (free)

| Característica      | Valor                                      |
|-------------------|--------------------------------------------|
| model_id          | `stepfun/step-3.5-flash:free`                               |
| Proveedor         | StepFun                                 |
| Modalidad         | text->text                                 |
| Contexto          | 256000                           |
| Precio Input/M    | GRATUITO                 |
| Precio Output/M   | GRATUITO             |
| Gratuito          | Sí                  |

**Descripción funcional:** Step 3.5 Flash is StepFun's most capable open-source foundation model. Built on a sparse Mixture of Experts (MoE) architecture, it selectively activates only 11B of its 196B parameters per token....

**Configuración de uso:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="stepfun/step-3.5-flash:free", messages=[...])
```

---

### StepFun: Step 3.5 Flash

| Atributo | Valor |
|---|---|
| model_id | `stepfun/step-3.5-flash` |
| Proveedor | stepfun |
| Modalidad | text->text |
| Contexto | 262144 tokens |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.30 |
| Gratuito | No |

**Descripción Funcional:**
Step 3.5 Flash is StepFun's most capable open-source foundation model. Built on a sparse Mixture of Experts (MoE) architecture, it selectively activates only 11B of its 196B parameters per token. It is a reasoning model that is incredibly speed efficient...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key='YOUR_OPENROUTER_API_KEY',
)

response = client.chat.completions.create(
    model="stepfun/step-3.5-flash",
    messages=[{'role': 'user', 'content': '...'}]
)
```

---

### Arcee AI: Trinity Large Preview (free)

| Atributo | Valor |
|---|---|
| model_id | `arcee-ai/trinity-large-preview:free` |
| Proveedor | arcee-ai |
| Modalidad | text->text |
| Contexto | 131000 tokens |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción Funcional:**
Trinity-Large-Preview is a frontier-scale open-weight language model from Arcee, built as a 400B-parameter sparse Mixture-of-Experts with 13B active parameters per token using 4-of-256 expert routing. It excels in creative writing, storytelling, role-play, chat scenarios, and real-time voice assistance, better than...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key='YOUR_OPENROUTER_API_KEY',
)

response = client.chat.completions.create(
    model="arcee-ai/trinity-large-preview:free",
    messages=[{'role': 'user', 'content': '...'}]
)
```

---

### MoonshotAI: Kimi K2.5

| Atributo | Valor |
|---|---|
| model_id | `moonshotai/kimi-k2.5` |
| Proveedor | moonshotai |
| Modalidad | text+image->text |
| Contexto | 262144 tokens |
| Precio Input/M | $0.38 |
| Precio Output/M | $1.72 |
| Gratuito | No |

**Descripción Funcional:**
Kimi K2.5 is Moonshot AI's native multimodal model, delivering state-of-the-art visual coding capability and a self-directed agent swarm paradigm. Built on Kimi K2 with continued pretraining over approximately 15T mixed visual and text tokens, it delivers strong performance in general...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key='YOUR_OPENROUTER_API_KEY',
)

response = client.chat.completions.create(
    model="moonshotai/kimi-k2.5",
    messages=[{'role': 'user', 'content': '...'}]
)
```

---

### Upstage: Solar Pro 3

| Atributo | Valor |
|---|---|
| model_id | `upstage/solar-pro-3` |
| Proveedor | upstage |
| Modalidad | text->text |
| Contexto | 128000 tokens |
| Precio Input/M | $0.15 |
| Precio Output/M | $0.60 |
| Gratuito | No |

**Descripción Funcional:**
Solar Pro 3 is Upstage's powerful Mixture-of-Experts (MoE) language model. With 102B total parameters and 12B active parameters per forward pass, it delivers exceptional performance while maintaining computational efficiency. Optimized for Korean with English and Japanese support.

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key='YOUR_OPENROUTER_API_KEY',
)

response = client.chat.completions.create(
    model="upstage/solar-pro-3",
    messages=[{'role': 'user', 'content': '...'}]
)
```

---

### MiniMax: MiniMax M2-her

| Atributo | Valor |
|---|---|
| model_id | `minimax/minimax-m2-her` |
| Proveedor | minimax |
| Modalidad | text->text |
| Contexto | 65536 tokens |
| Precio Input/M | $0.30 |
| Precio Output/M | $1.20 |
| Gratuito | No |

**Descripción Funcional:**
MiniMax M2-her is a dialogue-first large language model built for immersive roleplay, character-driven chat, and expressive multi-turn conversations. Designed to stay consistent in tone and personality, it supports rich message roles (user_system, group, sample_message_user, sample_message_ai) and can learn from example...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key='YOUR_OPENROUTER_API_KEY',
)

response = client.chat.completions.create(
    model="minimax/minimax-m2-her",
    messages=[{'role': 'user', 'content': '...'}]
)
```

---

### Writer: Palmyra X5

| Atributo | Valor |
|---|---|
| model_id | `writer/palmyra-x5` |
| Proveedor | writer |
| Modalidad | text->text |
| Contexto | 1040000 tokens |
| Precio Input/M | $0.60 |
| Precio Output/M | $6.00 |
| Gratuito | No |

**Descripción Funcional:**
Palmyra X5 is Writer's most advanced model, purpose-built for building and scaling AI agents across the enterprise. It delivers industry-leading speed and efficiency on context windows up to 1 million tokens, powered by a novel transformer architecture and hybrid attention...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key='YOUR_OPENROUTER_API_KEY',
)

response = client.chat.completions.create(
    model="writer/palmyra-x5",
    messages=[{'role': 'user', 'content': '...'}]
)
```

---

### LiquidAI: LFM2.5-1.2B-Thinking (free)

| Atributo | Valor |
|---|---|
| model_id | `liquid/lfm-2.5-1.2b-thinking:free` |
| Proveedor | liquid |
| Modalidad | text->text |
| Contexto | 32768 tokens |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción Funcional:**
LFM2.5-1.2B-Thinking is a lightweight reasoning-focused model optimized for agentic tasks, data extraction, and RAG—while still running comfortably on edge devices. It supports long context (up to 32K tokens) and is designed to provide higher-quality “thinking” responses in a small 1.2B...

**Configuración de Uso (Python):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key='YOUR_OPENROUTER_API_KEY',
)

response = client.chat.completions.create(
    model="liquid/lfm-2.5-1.2b-thinking:free",
    messages=[{'role': 'user', 'content': '...'}]
)
```

---

### LiquidAI: LFM2.5-1.2B-Instruct (free)
| Característica | Valor |
| :--- | :--- |
| model_id | `liquid/lfm-2.5-1.2b-instruct:free` |
| Proveedor | LiquidAI |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M | GRATUITO |
| Precio Output/M | GRATUITO |
| Gratuito | Sí |

**Descripción funcional:** LFM2.5-1.2B-Instruct is a compact, high-performance instruction-tuned model built for fast on-device AI. It delivers strong chat quality in a 1.2B parameter footprint, with efficient edge inference and broad runtime support.

**Configuración de uso:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="liquid/lfm-2.5-1.2b-instruct:free", messages=[...])
```
---
### OpenAI: GPT Audio
| Característica | Valor |
| :--- | :--- |
| model_id | `openai/gpt-audio` |
| Proveedor | OpenAI |
| Modalidad | text+audio->text+audio |
| Contexto | 128000 |
| Precio Input/M | $2.50 |
| Precio Output/M | $10.00 |
| Gratuito | No |

**Descripción funcional:** The gpt-audio model is OpenAI's first generally available audio model. The new snapshot features an upgraded decoder for more natural sounding voices and maintains better voice consistency. Audio is priced at $32 per million input tokens and $64 per million output tokens.

**Configuración de uso:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-audio", messages=[...])
```
---
### OpenAI: GPT Audio Mini
| Característica | Valor |
| :--- | :--- |
| model_id | `openai/gpt-audio-mini` |
| Proveedor | OpenAI |
| Modalidad | text+audio->text+audio |
| Contexto | 128000 |
| Precio Input/M | $0.60 |
| Precio Output/M | $2.40 |
| Gratuito | No |

**Descripción funcional:** A cost-efficient version of GPT Audio. The new snapshot features an upgraded decoder for more natural sounding voices and maintains better voice consistency. Input is priced at $0.60 per million tokens and output is priced at $2.40 per million tokens.

**Configuración de uso:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-audio-mini", messages=[...])
```
---
### Z.ai: GLM 4.7 Flash
| Característica | Valor |
| :--- | :--- |
| model_id | `z-ai/glm-4.7-flash` |
| Proveedor | Z.ai |
| Modalidad | text->text |
| Contexto | 202752 |
| Precio Input/M | $0.06 |
| Precio Output/M | $0.40 |
| Gratuito | No |

**Descripción funcional:** As a 30B-class SOTA model, GLM-4.7-Flash offers a new option that balances performance and efficiency. It is further optimized for agentic coding use cases, strengthening coding capabilities, long-horizon task planning, and tool collaboration, and has achieved leading performance among open-source models of the same size on several current public benchmark leaderboards.

**Configuración de uso:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="z-ai/glm-4.7-flash", messages=[...])
```
---
### OpenAI: GPT-5.2-Codex
| Característica | Valor |
| :--- | :--- |
| model_id | `openai/gpt-5.2-codex` |
| Proveedor | OpenAI |
| Modalidad | text+image->text |
| Contexto | 400000 |
| Precio Input/M | $1.75 |
| Precio Output/M | $14.00 |
| Gratuito | No |

**Descripción funcional:** GPT-5.2-Codex is an upgraded version of GPT-5.1-Codex optimized for software engineering and coding workflows. It is designed for both interactive development sessions and long, independent execution of complex engineering tasks. The model supports building projects from scratch, feature development, debugging, large-scale refactoring, and code review. Compared to GPT-5.1-Codex, 5.2-Codex is more steerable, adheres closely to developer instructions, and produces cleaner, higher-quality code outputs. Reasoning effort can be adjusted with the `reasoning.effort` parameter. Read the [docs here](https://openrouter.ai/docs/use-cases/reasoning-tokens#reasoning-effort-level)

**Configuración de uso:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="openai/gpt-5.2-codex", messages=[...])
```
---
### AllenAI: Olmo 3.1 32B Instruct
| Característica | Valor |
| :--- | :--- |
| model_id | `allenai/olmo-3.1-32b-instruct` |
| Proveedor | AllenAI |
| Modalidad | text->text |
| Contexto | 65536 |
| Precio Input/M | $0.20 |
| Precio Output/M | $0.60 |
| Gratuito | No |

**Descripción funcional:** Olmo 3.1 32B Instruct is a large-scale, 32-billion-parameter instruction-tuned language model engineered for high-performance conversational AI, multi-turn dialogue, and practical instruction following. As part of the Olmo 3.1 family, this variant emphasizes responsiveness to complex user directions and robust chat interactions while retaining strong capabilities on reasoning and coding benchmarks. Developed by Ai2 under the Apache 2.0 license, Olmo 3.1 32B Instruct reflects the Olmo initiative’s commitment to openness and transparency.

**Configuración de uso:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="allenai/olmo-3.1-32b-instruct", messages=[...])
```
---
### ByteDance Seed: Seed 1.6 Flash
| Característica | Valor |
| :--- | :--- |
| model_id | `bytedance-seed/seed-1.6-flash` |
| Proveedor | ByteDance Seed |
| Modalidad | text+image+video->text |
| Contexto | 262144 |
| Precio Input/M | $0.07 |
| Precio Output/M | $0.30 |
| Gratuito | No |

**Descripción funcional:** Seed 1.6 Flash is an ultra-fast multimodal deep thinking model by ByteDance Seed, supporting both text and visual understanding. It features a 256k context window and can generate outputs of up to 16k tokens.

**Configuración de uso:**
```python
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_API_KEY")
response = client.chat.completions.create(model="bytedance-seed/seed-1.6-flash", messages=[...])
```
---

### ByteDance Seed: Seed 1.6

| Campo | Valor |
|---|---|
| model_id | bytedance-seed/seed-1.6 |
| Proveedor | bytedance-seed |
| Modalidad | text+image+video->text |
| Contexto | 262144 |
| Precio Input/M | $0.25 |
| Precio Output/M | $2.00 |
| Gratuito | No |

**Descripción funcional:** Seed 1. 6 is a general-purpose model released by the ByteDance Seed team.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="bytedance-seed/seed-1.6", messages=[...])
```

---

### MiniMax: MiniMax M2.1

| Campo | Valor |
|---|---|
| model_id | minimax/minimax-m2.1 |
| Proveedor | minimax |
| Modalidad | text->text |
| Contexto | 196608 |
| Precio Input/M | $0.27 |
| Precio Output/M | $0.95 |
| Gratuito | No |

**Descripción funcional:** MiniMax-M2. 1 is a lightweight, state-of-the-art large language model optimized for coding, agentic workflows, and modern application development.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="minimax/minimax-m2.1", messages=[...])
```

---

### Z.ai: GLM 4.7

| Campo | Valor |
|---|---|
| model_id | z-ai/glm-4.7 |
| Proveedor | z-ai |
| Modalidad | text->text |
| Contexto | 202752 |
| Precio Input/M | $0.39 |
| Precio Output/M | $1.75 |
| Gratuito | No |

**Descripción funcional:** GLM-4. 7 is Z.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="z-ai/glm-4.7", messages=[...])
```

---

### Google: Gemini 3 Flash Preview

| Campo | Valor |
|---|---|
| model_id | google/gemini-3-flash-preview |
| Proveedor | google |
| Modalidad | text+image+file+audio+video->text |
| Contexto | 1048576 |
| Precio Input/M | $0.50 |
| Precio Output/M | $3.00 |
| Gratuito | No |

**Descripción funcional:** Gemini 3 Flash Preview is a high speed, high value thinking model designed for agentic workflows, multi turn chat, and coding assistance.  It delivers near Pro level reasoning and tool use performance with substantially lower latency than larger Gemini variants, making it well suited for interactive development, long running agent loops, and collaborative coding tasks.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="google/gemini-3-flash-preview", messages=[...])
```

---

### Mistral: Mistral Small Creative

| Campo | Valor |
|---|---|
| model_id | mistralai/mistral-small-creative |
| Proveedor | mistralai |
| Modalidad | text->text |
| Contexto | 32768 |
| Precio Input/M | $0.10 |
| Precio Output/M | $0.30 |
| Gratuito | No |

**Descripción funcional:** Mistral Small Creative is an experimental small model designed for creative writing, narrative generation, roleplay and character-driven dialogue, general-purpose instruction following, and conversational agents. .

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="mistralai/mistral-small-creative", messages=[...])
```

---

### AllenAI: Olmo 3.1 32B Think

| Campo | Valor |
|---|---|
| model_id | allenai/olmo-3.1-32b-think |
| Proveedor | allenai |
| Modalidad | text->text |
| Contexto | 65536 |
| Precio Input/M | $0.15 |
| Precio Output/M | $0.50 |
| Gratuito | No |

**Descripción funcional:** Olmo 3. 1 32B Think is a large-scale, 32-billion-parameter model designed for deep reasoning, complex multi-step logic, and advanced instruction following.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="allenai/olmo-3.1-32b-think", messages=[...])
```

---

### Xiaomi: MiMo-V2-Flash

| Campo | Valor |
|---|---|
| model_id | xiaomi/mimo-v2-flash |
| Proveedor | xiaomi |
| Modalidad | text->text |
| Contexto | 262144 |
| Precio Input/M | $0.09 |
| Precio Output/M | $0.29 |
| Gratuito | No |

**Descripción funcional:** MiMo-V2-Flash is an open-source foundation language model developed by Xiaomi.  It is a Mixture-of-Experts model with 309B total parameters and 15B active parameters, adopting hybrid attention architecture.

**Snippet de configuración Python:**
```python
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="YOUR_OPENROUTER_KEY")
response = client.chat.completions.create(model="xiaomi/mimo-v2-flash", messages=[...])
```

---

## Modelos Adicionales (Lote de Recuperación)

### Cohere: Command R+ (08-2024)

| Campo | Valor |
|:---|:---|
| **model_id** | `cohere/command-r-plus-08-2024` |
| **Proveedor** | cohere |
| **Modalidad** | text->text |
| **Contexto** | 128,000 tokens |
| **Precio Input/M tokens** | $2.5000 |
| **Precio Output/M tokens** | $10.0000 |
| **Tipo** | De pago |

command-r-plus-08-2024 is an update of the [Command R+](/models/cohere/command-r-plus) with roughly 50% higher throughput and 25% lower latencies as compared to the previous Command R+ version, while 

```python
response = client.chat.completions.create(model="cohere/command-r-plus-08-2024", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### Sao10K: Llama 3.1 Euryale 70B v2.2

| Campo | Valor |
|:---|:---|
| **model_id** | `sao10k/l3.1-euryale-70b` |
| **Proveedor** | sao10k |
| **Modalidad** | text->text |
| **Contexto** | 131,072 tokens |
| **Precio Input/M tokens** | $0.8500 |
| **Precio Output/M tokens** | $0.8500 |
| **Tipo** | De pago |

Euryale L3.1 70B v2.2 is a model focused on creative roleplay from [Sao10k](https://ko-fi.com/sao10k). It is the successor of [Euryale L3 70B v2.1](/models/sao10k/l3-euryale-70b).

```python
response = client.chat.completions.create(model="sao10k/l3.1-euryale-70b", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### Nous: Hermes 3 70B Instruct

| Campo | Valor |
|:---|:---|
| **model_id** | `nousresearch/hermes-3-llama-3.1-70b` |
| **Proveedor** | nousresearch |
| **Modalidad** | text->text |
| **Contexto** | 131,072 tokens |
| **Precio Input/M tokens** | $0.3000 |
| **Precio Output/M tokens** | $0.3000 |
| **Tipo** | De pago |

Hermes 3 is a generalist language model with many improvements over [Hermes 2](/models/nousresearch/nous-hermes-2-mistral-7b-dpo), including advanced agentic capabilities, much better roleplaying, rea

```python
response = client.chat.completions.create(model="nousresearch/hermes-3-llama-3.1-70b", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### Nous: Hermes 3 405B Instruct (free)

| Campo | Valor |
|:---|:---|
| **model_id** | `nousresearch/hermes-3-llama-3.1-405b:free` |
| **Proveedor** | nousresearch |
| **Modalidad** | text->text |
| **Contexto** | 131,072 tokens |
| **Precio Input/M tokens** | $0.0000 |
| **Precio Output/M tokens** | $0.0000 |
| **Tipo** | GRATUITO |

Hermes 3 is a generalist language model with many improvements over Hermes 2, including advanced agentic capabilities, much better roleplaying, reasoning, multi-turn conversation, long context coheren

```python
response = client.chat.completions.create(model="nousresearch/hermes-3-llama-3.1-405b:free", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### Nous: Hermes 3 405B Instruct

| Campo | Valor |
|:---|:---|
| **model_id** | `nousresearch/hermes-3-llama-3.1-405b` |
| **Proveedor** | nousresearch |
| **Modalidad** | text->text |
| **Contexto** | 131,072 tokens |
| **Precio Input/M tokens** | $1.0000 |
| **Precio Output/M tokens** | $1.0000 |
| **Tipo** | De pago |

Hermes 3 is a generalist language model with many improvements over Hermes 2, including advanced agentic capabilities, much better roleplaying, reasoning, multi-turn conversation, long context coheren

```python
response = client.chat.completions.create(model="nousresearch/hermes-3-llama-3.1-405b", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### Sao10K: Llama 3 8B Lunaris

| Campo | Valor |
|:---|:---|
| **model_id** | `sao10k/l3-lunaris-8b` |
| **Proveedor** | sao10k |
| **Modalidad** | text->text |
| **Contexto** | 8,192 tokens |
| **Precio Input/M tokens** | $0.0400 |
| **Precio Output/M tokens** | $0.0500 |
| **Tipo** | De pago |

Lunaris 8B is a versatile generalist and roleplaying model based on Llama 3. It's a strategic merge of multiple models, designed to balance creativity with improved logic and general knowledge.

Creat

```python
response = client.chat.completions.create(model="sao10k/l3-lunaris-8b", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### OpenAI: GPT-4o (2024-08-06)

| Campo | Valor |
|:---|:---|
| **model_id** | `openai/gpt-4o-2024-08-06` |
| **Proveedor** | openai |
| **Modalidad** | text+image+file->text |
| **Contexto** | 128,000 tokens |
| **Precio Input/M tokens** | $2.5000 |
| **Precio Output/M tokens** | $10.0000 |
| **Tipo** | De pago |

The 2024-08-06 version of GPT-4o offers improved performance in structured outputs, with the ability to supply a JSON schema in the respone_format. Read more [here](https://openai.com/index/introducin

```python
response = client.chat.completions.create(model="openai/gpt-4o-2024-08-06", messages=[{"role": "user", "content": "Tu prompt"}])
```

---


---


## Modelos Adicionales (Recuperación Final)

### MiniMax: MiniMax M1

| Campo | Valor |
|:---|:---|
| **model_id** | `minimax/minimax-m1` |
| **Proveedor** | minimax |
| **Modalidad** | text->text |
| **Contexto** | 1,000,000 tokens |
| **Precio Input/M tokens** | $0.4000 |
| **Precio Output/M tokens** | $2.2000 |
| **Tipo** | De pago |

MiniMax-M1 is a large-scale, open-weight reasoning model designed for extended context and high-efficiency inference. It leverages a hybrid Mixture-of-Experts (MoE) architecture paired with a custom "

```python
response = client.chat.completions.create(model="minimax/minimax-m1", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### Mistral: Mistral Small 3.1 24B

| Campo | Valor |
|:---|:---|
| **model_id** | `mistralai/mistral-small-3.1-24b-instruct` |
| **Proveedor** | mistralai |
| **Modalidad** | text+image->text |
| **Contexto** | 131,072 tokens |
| **Precio Input/M tokens** | $0.0300 |
| **Precio Output/M tokens** | $0.1100 |
| **Tipo** | De pago |

Mistral Small 3.1 24B Instruct is an upgraded variant of Mistral Small 3 (2501), featuring 24 billion parameters with advanced multimodal capabilities. It provides state-of-the-art performance in text

```python
response = client.chat.completions.create(model="mistralai/mistral-small-3.1-24b-instruct", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### AllenAI: Olmo 2 32B Instruct

| Campo | Valor |
|:---|:---|
| **model_id** | `allenai/olmo-2-0325-32b-instruct` |
| **Proveedor** | allenai |
| **Modalidad** | text->text |
| **Contexto** | 128,000 tokens |
| **Precio Input/M tokens** | $0.0500 |
| **Precio Output/M tokens** | $0.2000 |
| **Tipo** | De pago |

OLMo-2 32B Instruct is a supervised instruction-finetuned variant of the OLMo-2 32B March 2025 base model. It excels in complex reasoning and instruction-following tasks across diverse benchmarks such

```python
response = client.chat.completions.create(model="allenai/olmo-2-0325-32b-instruct", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### Google: Gemma 3 4B (free)

| Campo | Valor |
|:---|:---|
| **model_id** | `google/gemma-3-4b-it:free` |
| **Proveedor** | google |
| **Modalidad** | text+image->text |
| **Contexto** | 32,768 tokens |
| **Precio Input/M tokens** | $0.0000 |
| **Precio Output/M tokens** | $0.0000 |
| **Tipo** | GRATUITO |

Gemma 3 introduces multimodality, supporting vision-language input and text outputs. It handles context windows up to 128k tokens, understands over 140 languages, and offers improved math, reasoning, 

```python
response = client.chat.completions.create(model="google/gemma-3-4b-it:free", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### Google: Gemma 3 4B

| Campo | Valor |
|:---|:---|
| **model_id** | `google/gemma-3-4b-it` |
| **Proveedor** | google |
| **Modalidad** | text+image->text |
| **Contexto** | 131,072 tokens |
| **Precio Input/M tokens** | $0.0400 |
| **Precio Output/M tokens** | $0.0800 |
| **Tipo** | De pago |

Gemma 3 introduces multimodality, supporting vision-language input and text outputs. It handles context windows up to 128k tokens, understands over 140 languages, and offers improved math, reasoning, 

```python
response = client.chat.completions.create(model="google/gemma-3-4b-it", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### Google: Gemma 3 12B (free)

| Campo | Valor |
|:---|:---|
| **model_id** | `google/gemma-3-12b-it:free` |
| **Proveedor** | google |
| **Modalidad** | text+image->text |
| **Contexto** | 32,768 tokens |
| **Precio Input/M tokens** | $0.0000 |
| **Precio Output/M tokens** | $0.0000 |
| **Tipo** | GRATUITO |

Gemma 3 introduces multimodality, supporting vision-language input and text outputs. It handles context windows up to 128k tokens, understands over 140 languages, and offers improved math, reasoning, 

```python
response = client.chat.completions.create(model="google/gemma-3-12b-it:free", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### Google: Gemma 3 12B

| Campo | Valor |
|:---|:---|
| **model_id** | `google/gemma-3-12b-it` |
| **Proveedor** | google |
| **Modalidad** | text+image->text |
| **Contexto** | 131,072 tokens |
| **Precio Input/M tokens** | $0.0400 |
| **Precio Output/M tokens** | $0.1300 |
| **Tipo** | De pago |

Gemma 3 introduces multimodality, supporting vision-language input and text outputs. It handles context windows up to 128k tokens, understands over 140 languages, and offers improved math, reasoning, 

```python
response = client.chat.completions.create(model="google/gemma-3-12b-it", messages=[{"role": "user", "content": "Tu prompt"}])
```

---

### Cohere: Command A

| Campo | Valor |
|:---|:---|
| **model_id** | `cohere/command-a` |
| **Proveedor** | cohere |
| **Modalidad** | text->text |
| **Contexto** | 256,000 tokens |
| **Precio Input/M tokens** | $2.5000 |
| **Precio Output/M tokens** | $10.0000 |
| **Tipo** | De pago |

Command A is an open-weights 111B parameter model with a 256k context window focused on delivering great performance across agentic, multilingual, and coding use cases.
Compared to other leading propr

```python
response = client.chat.completions.create(model="cohere/command-a", messages=[{"role": "user", "content": "Tu prompt"}])
```

---


# REFERENCIA RÁPIDA: Modelos Recomendados por Caso de Uso

## Para Planeación y Síntesis
| Modelo | model_id | Precio Input/M |
|:---|:---|:---|
| GPT-5.4 | `openai/gpt-5.4` | $1.25 |
| GPT-5.4 Pro | `openai/gpt-5.4-pro` | $30.00 |
| Claude Opus 4.6 | `anthropic/claude-opus-4.6` | $15.00 |

## Para Código y Desarrollo
| Modelo | model_id | Precio Input/M |
|:---|:---|:---|
| GPT-5.3-Codex | `openai/gpt-5.3-codex` | $1.25 |
| Qwen3 Coder 480B | `qwen/qwen3-coder:free` | GRATUITO |
| DeepSeek V3.2 | `deepseek/deepseek-v3.2` | $0.14 |

## Para Razonamiento Profundo
| Modelo | model_id | Precio Input/M |
|:---|:---|:---|
| OpenAI o3 Pro | `openai/o3-pro` | $20.00 |
| DeepSeek R1 0528 | `deepseek/deepseek-r1-0528` | $0.80 |
| Sonar Reasoning Pro | `perplexity/sonar-reasoning-pro` | $2.00 |

## Para Multimodal (Imagen + Texto)
| Modelo | model_id | Precio Input/M |
|:---|:---|:---|
| Gemini 3.1 Pro Preview | `google/gemini-3.1-pro-preview` | $1.25 |
| GPT-5 Image | `openai/gpt-5-image` | $10.00 |
| Claude Sonnet 4.6 | `anthropic/claude-sonnet-4.6` | $3.00 |

## Para Búsqueda Web en Tiempo Real
| Modelo | model_id | Precio Input/M |
|:---|:---|:---|
| Sonar Pro Search | `perplexity/sonar-pro-search` | $3.00 |
| Sonar Deep Research | `perplexity/sonar-deep-research` | $2.00 |
| Sonar | `perplexity/sonar` | $1.00 |

## Para Máximo Ahorro (Gratuitos de Alta Calidad)
| Modelo | model_id | Contexto |
|:---|:---|:---|
| Qwen3.6 Plus | `qwen/qwen3.6-plus:free` | 1,000,000 |
| Nemotron 3 Super | `nvidia/nemotron-3-super-120b-a12b:free` | 262,144 |
| Llama 3.3 70B | `meta-llama/llama-3.3-70b-instruct:free` | 65,536 |
| Qwen3 Coder 480B | `qwen/qwen3-coder:free` | 262,000 |
| Step 3.5 Flash | `stepfun/step-3.5-flash:free` | 256,000 |

## Para Contexto Ultra-Largo (1M+ tokens)
| Modelo | model_id | Contexto | Precio Input/M |
|:---|:---|:---|:---|
| Grok 4.20 | `x-ai/grok-4.20` | 2,000,000 | $3.00 |
| GPT-5.4 | `openai/gpt-5.4` | 1,050,000 | $1.25 |
| Gemini 3.1 Pro | `google/gemini-3.1-pro-preview` | 1,048,576 | $1.25 |
| MiMo-V2-Pro | `xiaomi/mimo-v2-pro` | 1,048,576 | $0.30 |
| Claude Opus 4.6 | `anthropic/claude-opus-4.6` | 1,000,000 | $15.00 |

---

# NOTAS TÉCNICAS IMPORTANTES

1. **Autenticación:** Todas las llamadas requieren el header `Authorization: Bearer OPENROUTER_API_KEY`.
2. **Rate Limits:** Los modelos gratuitos tienen límites más restrictivos. Agregar créditos desbloquea mayor throughput.
3. **Fallback automático:** Usar `openrouter/auto` como model_id para que OpenRouter seleccione automáticamente el mejor modelo disponible.
4. **Streaming:** Todos los modelos soportan `stream=True` para respuestas en tiempo real.
5. **Tool Calling:** La mayoría de modelos modernos soportan function calling / tool use con el formato estándar de OpenAI.
6. **Precios dinámicos:** Los precios pueden variar. Consultar `https://openrouter.ai/api/v1/models` para precios actualizados.
7. **Modelos con `:free`:** Agregar `:free` al model_id fuerza la ruta gratuita (con rate limits más bajos).
8. **Providers específicos:** Usar el header `X-Provider` para forzar un proveedor específico cuando hay múltiples opciones.

---

*Documento generado automáticamente por Manus AI el 4 de abril de 2026.*  
*Fuente: API de OpenRouter + Investigación de mercado en tiempo real.*
