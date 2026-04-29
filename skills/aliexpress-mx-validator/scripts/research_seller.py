#!/usr/bin/env python3
"""
AliExpress Seller Reputation Researcher
Uses Perplexity Sonar API to search the internet for real-world reputation
data about an AliExpress seller (complaints, scam reports, external reviews).

Usage: python research_seller.py <store_name> [store_url]

Requires: SONAR_API_KEY environment variable.
Output: JSON file with findings and a trust assessment.
"""

import json
import os
import sys
import requests
from datetime import datetime


SONAR_API_KEY = os.environ.get("SONAR_API_KEY", "")
SONAR_URL = "https://api.perplexity.ai/chat/completions"


def research_seller(store_name: str, store_url: str = "") -> dict:
    """Search the internet for reputation data about the seller."""
    if not SONAR_API_KEY:
        return {
            "error": "SONAR_API_KEY no configurada",
            "suggestion": "Configura la variable de entorno SONAR_API_KEY para usar Perplexity.",
            "manual_fallback": True,
        }

    # Build the research prompt
    context = f"URL de la tienda: {store_url}" if store_url else ""
    prompt = f"""Investiga la reputación de la tienda de AliExpress llamada "{store_name}". {context}

Busca en internet:
1. ¿Hay quejas o reportes de estafa sobre esta tienda en Reddit, foros, redes sociales o sitios de reseñas?
2. ¿Hay reseñas externas positivas o negativas fuera de AliExpress?
3. ¿La tienda tiene presencia en otras plataformas (sitio web propio, redes sociales)?
4. ¿Hay alertas de fraude o advertencias sobre esta tienda?
5. ¿Qué dicen compradores mexicanos o latinoamericanos sobre esta tienda?

Responde en español. Sé específico con las fuentes que encuentres. Si no encuentras información, dilo claramente."""

    headers = {
        "Authorization": f"Bearer {SONAR_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "Eres un investigador especializado en verificar la legitimidad de vendedores en plataformas de e-commerce. Responde siempre en español y sé directo con tus hallazgos.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    try:
        response = requests.post(SONAR_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        citations = data.get("citations", [])

        return {
            "store_name": store_name,
            "store_url": store_url,
            "research_date": datetime.now().isoformat(),
            "findings": content,
            "sources": citations,
            "status": "success",
        }

    except requests.exceptions.Timeout:
        return {
            "store_name": store_name,
            "error": "Timeout al consultar Perplexity API",
            "status": "error",
        }
    except requests.exceptions.RequestException as e:
        return {
            "store_name": store_name,
            "error": str(e),
            "status": "error",
        }


def main():
    if len(sys.argv) < 2:
        print("Uso: python research_seller.py <nombre_tienda> [url_tienda]")
        print("Requiere: SONAR_API_KEY en variables de entorno")
        sys.exit(1)

    store_name = sys.argv[1]
    store_url = sys.argv[2] if len(sys.argv) > 2 else ""

    print(f"Investigando reputación de: {store_name}...")
    result = research_seller(store_name, store_url)

    # Save output
    safe_name = store_name.replace(" ", "_").replace("/", "_")[:50]
    output_path = f"seller_research_{safe_name}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    if result.get("status") == "success":
        print("\n=== HALLAZGOS ===")
        print(result["findings"])
        if result.get("sources"):
            print("\n=== FUENTES ===")
            for i, src in enumerate(result["sources"], 1):
                print(f"  [{i}] {src}")
    else:
        print(f"\nError: {result.get('error', 'desconocido')}")

    print(f"\n--- Resultados guardados en: {output_path} ---")


if __name__ == "__main__":
    main()
