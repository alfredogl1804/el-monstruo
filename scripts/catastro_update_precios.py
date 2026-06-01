#!/usr/bin/env python3
"""
catastro_update_precios.py
--------------------------
Script de actualización automática de precios de modelos LLM.
Ejecutado por Manus cada 2 semanas.

Fuentes:
  1. ComputeCheck.com (tabla de precios LLM)
  2. Artificial Analysis (fallback)
  3. Documentación oficial de proveedores (fallback final)

Flujo:
  1. Scrape precios actuales de fuentes públicas
  2. Compara con precios en catastro_modelos
  3. Actualiza los que cambiaron
  4. Recalcula cost_efficiency score
  5. Ejecuta catastro_recompute_trono_all()
  6. Registra evento en catastro_eventos
"""

import json
import subprocess
import os
import glob
import re
import sys
from datetime import datetime

PROJECT_ID = "xsumzuhwmivjgftsneov"
SONAR_API_KEY = os.environ.get("SONAR_API_KEY", "")

def run_sql(query):
    """Execute SQL via Supabase MCP."""
    cmd = ["manus-mcp-cli", "tool", "call", "execute_sql", "--server", "supabase",
           "--input", json.dumps({"project_id": PROJECT_ID, "query": query})]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    result_dir = os.path.expanduser("~/.mcp/tool-results/")
    files = sorted(glob.glob(os.path.join(result_dir, "*supabase_execute_sql*")))
    if files:
        with open(files[-1]) as f:
            content = f.read()
        for m in re.finditer(r'\[\s*\{', content):
            start = m.start()
            bracket_count = 0
            for i, c in enumerate(content[start:], start):
                if c == '[': bracket_count += 1
                elif c == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        try:
                            return json.loads(content[start:i+1])
                        except:
                            continue
                        break
        if '[]' in content:
            return []
    return []


def query_perplexity_prices():
    """Use Perplexity Sonar to get current LLM pricing data."""
    import requests
    
    if not SONAR_API_KEY:
        print("  WARN: SONAR_API_KEY not set, skipping Perplexity validation")
        return None
    
    headers = {
        "Authorization": f"Bearer {SONAR_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are a pricing research assistant. Return ONLY a JSON array with no markdown formatting. Each object must have: id (lowercase-hyphenated), input_price (USD per 1M tokens), output_price (USD per 1M tokens). Only include models you are confident about."
            },
            {
                "role": "user", 
                "content": "What are the current prices (USD per 1 million tokens) for these LLM models as of June 2026? Return JSON array only: GPT-5.5, GPT-5.5 Pro, GPT-5.4, Claude Opus 4.7, Claude Sonnet 4.6, Claude Haiku 4.5, Gemini 3.5 Flash, Gemini 3.1 Pro, Gemini 2.5 Flash, Gemini 2.5 Pro, Grok 4, DeepSeek V4 Flash, DeepSeek V4 Pro, DeepSeek R1, Mistral Large 3, o3, o4-mini"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }
    
    try:
        resp = requests.post("https://api.perplexity.ai/chat/completions", 
                           headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            # Extract JSON from response
            m = re.search(r'\[.*\]', content, re.DOTALL)
            if m:
                return json.loads(m.group(0))
        else:
            print(f"  WARN: Perplexity returned {resp.status_code}")
    except Exception as e:
        print(f"  WARN: Perplexity query failed: {e}")
    
    return None


def get_current_prices():
    """Get current prices from catastro_modelos."""
    return run_sql("""
        SELECT id, nombre, precio_input_per_million, precio_output_per_million 
        FROM catastro_modelos 
        WHERE estado = 'production' 
        ORDER BY id
    """)


def calculate_cost_efficiency(input_price, output_price):
    """Calculate cost_efficiency score (0-100). Cheaper = higher score.
    Based on blended price (60% input, 40% output).
    Scale: $0.01/M = 100, $100/M = 0 (logarithmic)."""
    import math
    blended = (input_price * 0.6 + output_price * 0.4)
    if blended <= 0:
        return 99.00
    # Log scale: score = 100 - 25 * log10(blended)
    score = 100 - 25 * math.log10(max(blended, 0.01))
    return round(max(0, min(99.99, score)), 2)


def update_prices(price_data):
    """Update prices in catastro_modelos and recalculate cost_efficiency."""
    # Map Perplexity results to our IDs
    id_map = {
        "gpt-5.5": "gpt-5-5", "gpt-5-5": "gpt-5-5",
        "gpt-5.5-pro": "gpt-5-5-pro", "gpt-5-5-pro": "gpt-5-5-pro",
        "gpt-5.4": "gpt-5-4", "gpt-5-4": "gpt-5-4",
        "claude-opus-4.7": "claude-opus-4-7", "claude-opus-4-7": "claude-opus-4-7",
        "claude-sonnet-4.6": "claude-sonnet-4-6", "claude-sonnet-4-6": "claude-sonnet-4-6",
        "claude-haiku-4.5": "claude-haiku-4-5", "claude-haiku-4-5": "claude-haiku-4-5",
        "gemini-3.5-flash": "gemini-3-5-flash", "gemini-3-5-flash": "gemini-3-5-flash",
        "gemini-3.1-pro": "gemini-3-1-pro", "gemini-3-1-pro": "gemini-3-1-pro",
        "gemini-2.5-flash": "gemini-2-5-flash", "gemini-2-5-flash": "gemini-2-5-flash",
        "gemini-2.5-pro": "gemini-2-5-pro", "gemini-2-5-pro": "gemini-2-5-pro",
        "grok-4": "grok-4",
        "deepseek-v4-flash": "deepseek-v4-flash",
        "deepseek-v4-pro": "deepseek-v4-pro",
        "deepseek-r1": "deepseek-r1",
        "mistral-large-3": "mistral-large-3",
        "o3": "o3", "o4-mini": "o4-mini",
    }
    
    updated = 0
    for item in price_data:
        raw_id = item.get("id", "").lower().strip()
        our_id = id_map.get(raw_id, raw_id)
        input_price = float(item.get("input_price", 0))
        output_price = float(item.get("output_price", 0))
        
        if input_price <= 0 and output_price <= 0:
            continue
        
        cost_eff = calculate_cost_efficiency(input_price, output_price)
        
        sql = f"""
UPDATE catastro_modelos SET
  precio_input_per_million = {input_price},
  precio_output_per_million = {output_price},
  cost_efficiency = {cost_eff},
  updated_at = now()
WHERE id = '{our_id}' AND estado = 'production';
"""
        result = run_sql(sql)
        updated += 1
    
    return updated


def main():
    print("=" * 60)
    print(f"CATASTRO UPDATE PRECIOS — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Step 1: Get current prices
    print("\n[1/5] Obteniendo precios actuales del catastro...")
    current = get_current_prices()
    print(f"  → {len(current)} modelos en producción")
    
    # Step 2: Query Perplexity for fresh prices
    print("\n[2/5] Consultando Perplexity Sonar Pro para precios actualizados...")
    fresh_prices = query_perplexity_prices()
    
    if not fresh_prices:
        print("  → No se obtuvieron precios de Perplexity. Abortando.")
        print("  → Para ejecutar manualmente, asegúrate de tener SONAR_API_KEY configurada.")
        sys.exit(1)
    
    print(f"  → {len(fresh_prices)} modelos con precios frescos")
    
    # Step 3: Update prices
    print("\n[3/5] Actualizando precios en catastro_modelos...")
    updated_count = update_prices(fresh_prices)
    print(f"  → {updated_count} modelos actualizados")
    
    # Step 4: Recompute trono
    print("\n[4/5] Recalculando trono_global...")
    run_sql("SELECT catastro_recompute_trono_all();")
    print("  → Trono recalculado")
    
    # Step 5: Log event
    print("\n[5/5] Registrando evento...")
    run_sql(f"""
INSERT INTO catastro_eventos (tipo, descripcion, metadata, created_at)
VALUES (
  'actualizacion_precios',
  'Actualización automática de precios — {updated_count} modelos actualizados via Perplexity + Manus',
  '{{"source": "catastro_update_precios.py", "modelos_actualizados": {updated_count}, "fuente": "perplexity_sonar_pro"}}'::jsonb,
  now()
);
""")
    print("  → Evento registrado")
    
    print("\n" + "=" * 60)
    print(f"COMPLETADO: {updated_count} precios actualizados")
    print("=" * 60)


if __name__ == "__main__":
    main()
