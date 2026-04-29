import os, json
import aiohttp, asyncio

async def call_gpt(prompt):
    url = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1") + "/chat/completions"
    headers = {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-5.4-mini",  # Updated 2026-04-22 — gpt-4o RETIRED
        "messages": [{"role": "system", "content": "Eres un experto en gestión de crisis políticas LATAM-POLICRIS v1. Clasifica las menciones dadas. Responde en JSON estricto."}, {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
                data = await resp.json()
                return json.loads(data["choices"][0]["message"]["content"])
        except Exception as e:
            return {"error": str(e)}

def classify_crisis(mentions, target_name):
    print(f"  -> Evaluando con GPT-5.4-mini...")
    
    prompt = f"""
    Evalúa la siguiente cobertura mediática y social sobre {target_name}:
    
    {json.dumps(mentions, indent=2)}
    
    Identifica:
    1. crisis_type (ej. criminal_association, policy_backlash, compound_crisis)
    2. damage_axes (reputacional, legal, electoral, etc.)
    3. accusation_types (corrupción, narco, incompetencia, moral)
    4. evidence_state (rumor, documento, proceso)
    5. attack_vectors (actores atacantes, narrativas dominantes)
    6. sentiment_score (0-100, donde 100 es máximo hostilidad)
    7. allegations (lista de acusaciones concretas)
    
    Devuelve un JSON con esas claves.
    """
    
    result = asyncio.run(call_gpt(prompt))
    return result
