#!/usr/bin/env python3.11
"""
Web Researcher — Investiga cambios recientes, noticias y descripciones del sitio
usando Perplexity Sonar para contexto temporal.
"""
import json
import os
import requests
from pathlib import Path


async def research_web(site_info: dict, evidence_dir: Path) -> dict:
    """Investiga el sitio en la web para contexto temporal."""
    api_key = os.environ.get("SONAR_API_KEY")
    if not api_key:
        return {"source": "web_research", "observations": [], "error": "No SONAR_API_KEY"}

    observations = []
    raw_responses = []
    name = site_info["name"]

    queries = [
        f"¿Cuál es el estado actual de {name} en {site_info['target_date'][:4]}? ¿Ha habido remodelaciones, construcciones nuevas o cambios recientes?",
        f"¿Qué hay alrededor de {name}? Describe los negocios, edificios, terrenos y características del entorno inmediato.",
        f"¿Hay proyectos de construcción o desarrollo urbano recientes cerca de {name}?",
    ]

    for i, query in enumerate(queries):
        try:
            resp = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar-reasoning-pro",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Eres un investigador urbano. Responde con hechos verificables sobre el estado actual del lugar. Incluye fechas y fuentes cuando sea posible. NO inventes información."
                        },
                        {"role": "user", "content": query}
                    ],
                    "max_tokens": 2000,
                },
                timeout=60,
            )

            if resp.status_code == 200:
                data = resp.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                citations = data.get("citations", [])

                raw_responses.append({
                    "query": query,
                    "response": text,
                    "citations": citations,
                })

                if text:
                    obs = {
                        "observation_id": f"web_research_{i}",
                        "category": "context",
                        "source": "web_research",
                        "description": text[:500],
                        "attributes": {
                            "full_response": text,
                            "query": query,
                            "citations": citations,
                            "citations_count": len(citations),
                        },
                        "confidence": 0.6,  # Web research has lower confidence than visual
                    }
                    observations.append(obs)

                print(f"      Web research {i+1}/3: {len(text)} chars, {len(citations)} citas")
            else:
                print(f"      Web research {i+1}/3 error: HTTP {resp.status_code}")
                raw_responses.append({"query": query, "error": f"HTTP {resp.status_code}"})

        except Exception as e:
            print(f"      Web research {i+1}/3 error: {str(e)[:80]}")
            raw_responses.append({"query": query, "error": str(e)})

    # Save raw data
    with open(evidence_dir / "web_research_raw.json", "w") as f:
        json.dump(raw_responses, f, indent=2, ensure_ascii=False, default=str)

    return {
        "source": "web_research",
        "observations": observations,
        "summary": {
            "queries_sent": len(queries),
            "total_citations": sum(len(r.get("citations", [])) for r in raw_responses),
        },
    }
