#!/usr/bin/env python3
"""
AI-Powered Review Authenticity Analyzer
Uses Google Gemini or OpenAI to analyze AliExpress reviews with AI,
detecting fake reviews, sentiment patterns, and providing a trust assessment.

Usage: python ai_review_analyzer.py <reviews_file.json>

Requires: GEMINI_API_KEY or OPENAI_API_KEY environment variable.
Falls back to rule-based analysis if no API key is available.
"""

import json
import os
import sys
from datetime import datetime

import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")


def analyze_with_gemini(reviews_text: str, product_name: str) -> dict:
    """Use Google Gemini to analyze reviews."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    )

    prompt = _build_prompt(reviews_text, product_name)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json",
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        return {"status": "success", "engine": "gemini", "analysis": json.loads(content)}
    except Exception as e:
        return {"status": "error", "engine": "gemini", "error": str(e)}


def analyze_with_openai(reviews_text: str, product_name: str) -> dict:
    """Use OpenAI to analyze reviews."""
    url = f"{OPENAI_API_BASE}/chat/completions"
    prompt = _build_prompt(reviews_text, product_name)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-5.4-mini",  # Updated 2026-04-22 — gpt-4o-mini RETIRED
        "messages": [
            {
                "role": "system",
                "content": "Eres un experto en detección de reseñas falsas en plataformas de e-commerce. Responde siempre en formato JSON válido y en español.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return {"status": "success", "engine": "openai", "analysis": json.loads(content)}
    except Exception as e:
        return {"status": "error", "engine": "openai", "error": str(e)}


def _build_prompt(reviews_text: str, product_name: str) -> str:
    """Build the analysis prompt for the AI model."""
    return f"""Analiza las siguientes reseñas del producto "{product_name}" de AliExpress y determina cuáles son probablemente reales y cuáles falsas.

RESEÑAS:
{reviews_text}

Responde en JSON con esta estructura exacta:
{{
  "resumen_general": "Resumen de 2-3 oraciones sobre la autenticidad general de las reseñas",
  "porcentaje_reales_estimado": 65,
  "porcentaje_falsas_estimado": 35,
  "patrones_sospechosos": [
    "Descripción del patrón sospechoso 1",
    "Descripción del patrón sospechoso 2"
  ],
  "señales_positivas": [
    "Señal de autenticidad 1",
    "Señal de autenticidad 2"
  ],
  "reseñas_mas_confiables": [
    {{
      "texto_original": "texto de la reseña",
      "razon_confiable": "por qué parece real"
    }}
  ],
  "reseñas_mas_sospechosas": [
    {{
      "texto_original": "texto de la reseña",
      "razon_sospechosa": "por qué parece falsa"
    }}
  ],
  "recomendacion_compra": "Recomendación basada en las reseñas para un comprador en México",
  "nivel_confianza_reseñas": "alto|medio|bajo",
  "alertas_para_mexico": [
    "Alerta específica para compradores mexicanos basada en las reseñas"
  ]
}}

Sé riguroso en tu análisis. Busca:
- Reseñas genéricas y cortas (posible bot)
- Patrones de fecha sospechosos (muchas en el mismo día)
- Lenguaje repetitivo entre reseñas
- Reseñas que no mencionan detalles específicos del producto
- Reseñas con fotos que parecen reales vs profesionales
- Reseñas de compradores mexicanos/latinoamericanos (más relevantes)
- Inconsistencias entre calificación alta y texto negativo"""


def main():
    if len(sys.argv) < 2:
        print("Uso: python ai_review_analyzer.py <reviews_file.json>")
        print("Requiere: GEMINI_API_KEY o OPENAI_API_KEY en variables de entorno")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: No se encontró '{filepath}'")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    # Extract product name if available
    product_name = "Producto de AliExpress"
    if isinstance(reviews, dict) and "product_name" in reviews:
        product_name = reviews["product_name"]
        reviews_list = reviews.get("reviews", reviews.get("sample_real_reviews", []))
    elif isinstance(reviews, list):
        reviews_list = reviews
    else:
        print("Error: Formato de archivo no reconocido")
        sys.exit(1)

    # Format reviews for the prompt
    reviews_text = ""
    for i, r in enumerate(reviews_list[:50], 1):  # Limit to 50 reviews
        rating = r.get("rating", "N/A")
        text = r.get("text", "Sin texto")
        photo = "📷 Con foto" if r.get("has_photo") else "Sin foto"
        country = r.get("buyer_country", r.get("country", "N/D"))
        date = r.get("date", "N/D")
        reviews_text += f'\nReseña #{i}: ⭐{rating} | {country} | {date} | {photo}\n"{text}"\n'

    if not reviews_text.strip():
        print("No hay reseñas para analizar.")
        sys.exit(1)

    print(f"Analizando {len(reviews_list[:50])} reseñas con IA...")

    # Try Gemini first, then OpenAI
    result = None
    if GEMINI_API_KEY:
        print("Usando Google Gemini...")
        result = analyze_with_gemini(reviews_text, product_name)

    if (not result or result.get("status") != "success") and OPENAI_API_KEY:
        print("Usando OpenAI...")
        result = analyze_with_openai(reviews_text, product_name)

    if not result or result.get("status") != "success":
        print("\n⚠️  No se pudo conectar con ninguna API de IA.")
        print("Configura GEMINI_API_KEY o OPENAI_API_KEY para análisis con IA.")
        print("Usa analyze_reviews.py como alternativa basada en reglas.")
        if result:
            print(f"Error: {result.get('error', 'desconocido')}")
        sys.exit(1)

    # Save output
    output_path = filepath.replace(".json", "_ai_analysis.json")
    output_data = {
        "product_name": product_name,
        "analysis_date": datetime.now().isoformat(),
        "ai_engine": result["engine"],
        "reviews_analyzed": len(reviews_list[:50]),
        **result["analysis"],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n=== ANÁLISIS CON IA ({result['engine'].upper()}) ===")
    print(json.dumps(output_data, ensure_ascii=False, indent=2))
    print(f"\n--- Análisis guardado en: {output_path} ---")


if __name__ == "__main__":
    main()
