"""
El Monstruo Toolkit — Connection Snippets
Código copy-paste listo para conectar cada servicio.
Última verificación: 2026-04-09

USO: Copiar el snippet relevante al proyecto. Todos usan env vars.
"""

import os


# =====================================================================
# 1. GPT-5.4 (Estratega + Clasificador + Embeddings)
# =====================================================================
def connect_gpt54(prompt: str, system: str = "Eres un estratega experto.") -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-5.4",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=4000,  # NUNCA usar max_tokens con GPT-5.4
    )
    return response.choices[0].message.content


def get_embedding(text: str) -> list:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8000],
    )
    return response.data[0].embedding


# =====================================================================
# 2. Claude Opus 4.6 (Arquitecto + Crítico)
# =====================================================================
def connect_claude(prompt: str, system: str = "Eres un arquitecto experto.") -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-opus-4-6",  # NO claude-4-20250514
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# =====================================================================
# 3. Gemini 3.1 Pro (Creativo + Multimodal)
# =====================================================================
def connect_gemini(prompt: str) -> str:
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=prompt,
    )
    return response.text


# =====================================================================
# 4. Grok 4.20 (Código + Creativo + Tiempo Real)
# =====================================================================
def connect_grok(prompt: str, system: str = "Eres un experto.") -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["XAI_API_KEY"],
        base_url="https://api.x.ai/v1",
    )
    response = client.chat.completions.create(
        model="grok-4.20-0309-reasoning",  # NO grok-4-latest
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2000,
    )
    return response.choices[0].message.content


# =====================================================================
# 5. DeepSeek R1 (Razonador — via OpenRouter)
# =====================================================================
def connect_deepseek(prompt: str, system: str = "Eres un analista técnico.") -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",  # SIEMPRE via OpenRouter
    )
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2000,
    )
    return response.choices[0].message.content


# =====================================================================
# 6. Perplexity Sonar Pro (Investigador — NO usar OpenAI SDK)
# =====================================================================
def connect_perplexity(prompt: str, system: str = "Investiga con fuentes.") -> str:
    import requests

    headers = {
        "Authorization": f"Bearer {os.environ['SONAR_API_KEY']}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "sonar-reasoning-pro",  # NO sonar-pro
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        json=data,
        timeout=120,  # Timeout largo
    )
    return resp.json()["choices"][0]["message"]["content"]


# =====================================================================
# 7. OpenRouter — Modelos Gratis
# =====================================================================
def connect_free_model(prompt: str, model: str = "nvidia/nemotron-3-super:free") -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    return response.choices[0].message.content


# =====================================================================
# 8. Supabase — Memoria Semántica
# =====================================================================
def save_memory(user_id: str, role: str, content: str, task_type: str = None, brain_used: str = None) -> bool:
    import requests

    url = os.environ.get("SUPABASE_URL", "https://xsumzuhwmivjgftsneov.supabase.co")
    key = os.environ["SUPABASE_SERVICE_KEY"]
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    embedding = get_embedding(content)
    payload = {
        "user_id": str(user_id),
        "role": role,
        "content": content[:10000],
        "task_type": task_type,
        "brain_used": brain_used,
    }
    if embedding:
        payload["embedding"] = embedding
    resp = requests.post(f"{url}/rest/v1/monstruo_memory", headers=headers, json=payload, timeout=15)
    return resp.status_code in (200, 201)


def recall_memories(user_id: str, query: str, limit: int = 5) -> list:
    import requests

    url = os.environ.get("SUPABASE_URL", "https://xsumzuhwmivjgftsneov.supabase.co")
    key = os.environ["SUPABASE_SERVICE_KEY"]
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    embedding = get_embedding(query)
    if not embedding:
        return []
    resp = requests.post(
        f"{url}/rest/v1/rpc/match_memories",
        headers=headers,
        json={
            "query_embedding": embedding,
            "match_threshold": 0.3,
            "match_count": limit,
            "filter_user_id": str(user_id),
        },
        timeout=15,
    )
    return resp.json() if resp.status_code == 200 else []


# =====================================================================
# 9. ElevenLabs — Voz
# =====================================================================
def generate_speech(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
    from elevenlabs import ElevenLabs

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
    )
    return b"".join(audio)


# =====================================================================
# 10. HeyGen — Video
# =====================================================================
def create_video(text: str, avatar_id: str = "default") -> str:
    import requests

    headers = {
        "X-Api-Key": os.environ["HEYGEN_API_KEY"],
        "Content-Type": "application/json",
    }
    payload = {
        "video_inputs": [
            {
                "character": {"type": "avatar", "avatar_id": avatar_id},
                "voice": {"type": "text", "input_text": text},
            }
        ],
    }
    resp = requests.post("https://api.heygen.com/v2/video/generate", headers=headers, json=payload)
    return resp.json().get("data", {}).get("video_id", "")


def check_video_status(video_id: str) -> dict:
    import requests

    headers = {"X-Api-Key": os.environ["HEYGEN_API_KEY"]}
    resp = requests.get(
        f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
        headers=headers,
    )
    return resp.json()


# =====================================================================
# 11. Clasificador de Tareas (como lo usa el bot)
# =====================================================================
def classify_task(task_text: str) -> str:
    """Clasifica en: investigacion, codigo, estrategia, creativo, analisis, leads."""
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-5.4",
        messages=[
            {
                "role": "system",
                "content": (
                    "Clasifica la tarea en UNA categoría: investigacion, codigo, estrategia, "
                    "creativo, analisis, leads. Responde SOLO con la categoría."
                ),
            },
            {"role": "user", "content": task_text},
        ],
        max_completion_tokens=20,
    )
    return response.choices[0].message.content.strip().lower()


# =====================================================================
# 12. Router de Cerebros (brain_map actualizado)
# =====================================================================
BRAIN_MAP = {
    "investigacion": ("perplexity", connect_perplexity),
    "leads": ("perplexity", connect_perplexity),
    "codigo": ("grok", connect_grok),
    "estrategia": ("gpt54", connect_gpt54),
    "creativo": ("gemini", connect_gemini),
    "analisis": ("deepseek", connect_deepseek),
}


def route_and_execute(task_text: str) -> tuple:
    """Clasifica la tarea y la ejecuta con el cerebro óptimo."""
    task_type = classify_task(task_text)
    brain_id, brain_fn = BRAIN_MAP.get(task_type, ("gpt54", connect_gpt54))
    result = brain_fn(task_text)
    return brain_id, task_type, result
