import os, json, time
import aiohttp, asyncio

async def search_perplexity(query):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {os.environ.get('SONAR_API_KEY')}", "Content-Type": "application/json"}
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "system", "content": "Busca noticias recientes y menciones en redes sociales sobre el siguiente tema. Responde con un resumen detallado y fuentes."}, {"role": "user", "content": query}]
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error en Perplexity: {str(e)}"

def collect_mentions(target_name):
    # En un caso real, esto haría scraping intensivo.
    # Aquí simularemos usando Perplexity Sonar para buscar menciones recientes.
    query = f"Noticias de hoy, polémicas, crisis, acusaciones sobre {target_name} en Yucatán. Incluye menciones en Facebook, Twitter, medios locales."
    print(f"  -> Buscando en Perplexity: {query}")
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Si ya hay un loop, usar task (menos común en scripts CLI simples, pero por si acaso)
            # En este caso, como es un script CLI, asyncio.run es seguro si se llama desde el main thread.
            pass
    except RuntimeError:
        pass
        
    result = asyncio.run(search_perplexity(query))
    
    # Simular una estructura de menciones extraída del resultado de Perplexity
    mentions = [
        {
            "id": "1",
            "source_type": "news",
            "headline": "Acusaciones de vínculos con narcotráfico",
            "body": result,
            "engagement": {"likes": 100, "shares": 50}
        }
    ]
    return mentions
