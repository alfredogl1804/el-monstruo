#!/usr/bin/env python3.11
"""
Diagnóstico de Crisis Real: Clara Rosales Montiel
Usando framework LATAM-POLICRIS v1 con datos recopilados el 8 de abril de 2026.
"""

import asyncio
import datetime
import json
import os

import aiohttp

DOSSIER = """
# DOSSIER DE MENCIONES RECOPILADAS — 8 de abril de 2026
## Persona: Clara Paola Rosales Montiel, Diputada Local de Morena por Yucatán

### NOTA 1 — Noticias Al Punto (Facebook, hace 6h, ~7h de publicado)
TITULAR: "Funcionarios del Gobierno del Renacimiento Maya y diputados de MORENA apadrinan a delincuente implicado en red de distribución de narcóticos en Yucatán"
CONTENIDO: Clara Paola Rosales, junto con Darío Flota (Secretaría de Fomento Turístico) y Ermilo Barrera (Secretaría de Economía y Trabajo), firmaron alianza con Carlos Guadalupe Koyoc Uribe, implicado en vasta red de distribución de drogas en Yucatán. Koyoc Uribe está vinculado a proceso penal por amenazas contra dos periodistas (FEADLE). Ha sido detenido múltiples veces por la Guardia Nacional y SSP por posesión de drogas con fines de distribución y armas de fuego. Fue presidente del Comité Ejecutivo Municipal del PT en Kanasín y candidato del PT a la presidencia municipal en 2021. Se le señala como "principal distribuidor de drogas de Kanasín y municipios cercanos".
FUENTE: Portal Noticias Al Punto (medio local verificado de Yucatán)
ENGAGEMENT: Alto (múltiples shares en grupos de Facebook)
TONO: Muy negativo, acusatorio directo

### NOTA 2 — Escándala (portal digital, hace 21h)
TITULAR: "Organizaciones y activistas en Yucatán respaldan iniciativa para derogar el delito de peligro de contagio"
CONTENIDO: Organizaciones civiles, activistas y personas con VIH respaldan la iniciativa de Clara Rosales Montiel para derogar el artículo 189 del Código Penal. El CEDISEX califica la figura legal como desactualizada, sin sustento científico y contraria a los derechos humanos. Precedentes: CDMX, Nayarit, Zacatecas, Colima ya eliminaron disposiciones similares. ONUSIDA y OMS respaldan la postura.
FUENTE: Escándala (portal digital LGBTQ+)
TONO: Positivo hacia Clara Rosales

### NOTA 3 — Haz Ruido (medio digital yucateco, hace 7h)
TITULAR: "Llaman a no distorsionar iniciativa que pone fin a la criminalización del VIH"
CONTENIDO: El CEDISEX pide detener la desinformación sobre la iniciativa. Clara Rosales lamentó discursos estigmatizantes en redes y medios. Señaló que diputadas de PAN, MC y sin partido se adhirieron a su proyecto. El PRI presentó su propia iniciativa similar. Rosales dice que la reforma busca evitar diagnósticos tardíos de VIH. "No se hacen las pruebas a tiempo porque consideran que tener VIH es un delito."
FUENTE: Haz Ruido (medio digital local de Mérida)
TONO: Positivo/neutral hacia Clara Rosales

### NOTA 4 — Grupos de Facebook (múltiples, hace 16-23h)
TITULAR: "¡De Ripley! Diputada Clara Rosales mete al narco hasta la cocina"
CONTENIDO: Publicaciones virales en grupos de Facebook acusándola de meter al narco en mesas de trabajo del gobierno. "No permitan que la diputada le siembre a gente de esta calaña en sus mesas de trabajo." Se replica en al menos 3 grupos grandes de Yucatán.
FUENTE: Grupos públicos de Facebook (Que Todo Yucatán Se Entere, etc.)
ENGAGEMENT: Alto (cientos de interacciones)
TONO: Muy negativo, viral

### NOTA 5 — PAN Yucatán (Instagram, hace 22h)
TITULAR: Post del PAN Yucatán sobre cáncer y salud
CONTENIDO: El PAN Yucatán, con su presidente Álvaro Cetina, publica sobre deficiencias en salud del gobierno de Morena. Clara Rosales había confrontado a Cetina cuestionándole el "donativo" de su sueldo al sector Salud cuando votó contra presupuesto de salud.
FUENTE: Instagram @panyucatan
TONO: Ataque indirecto a Morena/Clara Rosales

### NOTA 6 — Noticias y Más Mid (Facebook, hace 4 días pero circulando hoy)
TITULAR: "LEGISLAR DESDE LA IGNORANCIA: EL PELIGROSO VACÍO LEGAL QUE PROPONE MORENA EN YUCATÁN"
CONTENIDO: Artículo de opinión que ataca duramente la propuesta de Clara Rosales. La acusa de "confundir la condición de una persona con su conducta" y de "garantizar impunidad total para quienes intenten contagiar a otros con enfermedades mortales". Dice que "Yucatán merece legisladores que dominen la técnica jurídica".
FUENTE: Noticias y Más Mid (medio local)
ENGAGEMENT: 6 likes, 14 shares, 1 comentario
TONO: Muy negativo, ataque directo a su competencia legislativa

### NOTA 7 — Morena Sí Yucatán (Instagram, hace 19h)
CONTENIDO: Morena Yucatán destaca acciones de Clara Rosales en el Congreso.
FUENTE: Instagram @morena_siyucatan
TONO: Positivo (defensa partidista)

### NOTA 8 — Yaaj México / Colectivo S3D (Facebook e Instagram, múltiples posts)
CONTENIDO: Organizaciones LGBTQ+ y de VIH respaldan públicamente la iniciativa de Clara Rosales con pronunciamientos formales.
FUENTE: Organizaciones civiles verificadas
TONO: Muy positivo

### NOTA 9 — TikTok @clara_rosales4t
CONTENIDO: Video de Clara Rosales hablando sobre leyes y presentándose como "diputada joven del sur de Mérida". Contenido proactivo, no reactivo a la crisis.
FUENTE: TikTok personal
TONO: Positivo (contenido propio)
"""


async def analizar_con_claude(dossier):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    prompt = f"""Eres un analista experto en crisis políticas en Latinoamérica usando el framework LATAM-POLICRIS v1.

Analiza el siguiente dossier de menciones sobre la diputada Clara Rosales Montiel (Morena, Yucatán) recopiladas el 8 de abril de 2026 y genera un diagnóstico completo en formato JSON con la siguiente estructura:

{{
  "person": "nombre completo",
  "date": "2026-04-08",
  "crisis_level": "VERDE|AMARILLO|NARANJA|ROJO",
  "severity_score": 0-100,
  "trend": "creciente|estable|decreciente",
  "crisis_type": "tipo principal",
  "damage_axes": ["lista de ejes de daño"],
  "accusation_types": ["tipos de acusación"],
  "evidence_state": "estado probatorio",
  "propagation_mode": "modo de propagación",
  "contagion_level": "nivel de contagio",
  "confirmed_facts": ["hechos confirmados"],
  "unverified_claims": ["acusaciones no verificadas"],
  "narratives": [
    {{"narrative": "nombre", "share_of_voice": 0.0-1.0, "momentum": "up|stable|down", "evidence_status": "estado"}}
  ],
  "attack_vectors": [
    {{"actor": "nombre", "type": "tipo", "platform": "plataforma", "narrative": "narrativa", "risk": "alto|medio|bajo"}}
  ],
  "allies": [
    {{"actor": "nombre", "type": "tipo", "strength": "fuerte|moderado|débil"}}
  ],
  "critical_window": "ventana crítica de respuesta",
  "immediate_actions_24h": ["acciones"],
  "strategy_72h": ["estrategias"],
  "campaign_7d": ["campaña"],
  "what_not_to_do": ["errores a evitar"],
  "spokesperson_recommendation": "quién debe hablar",
  "tone_recommendation": "tono recomendado",
  "executive_summary": "resumen ejecutivo de 3-5 oraciones"
}}

DOSSIER:
{dossier}

IMPORTANTE: 
- Sé extremadamente preciso en separar hechos confirmados de acusaciones no verificadas.
- La acusación de narcotráfico viene de UN medio local (Noticias Al Punto) y grupos de Facebook. No hay cobertura nacional ni documentos oficiales.
- La iniciativa de VIH sí tiene respaldo de organizaciones civiles, ONUSIDA, OMS y precedentes en otros estados.
- Evalúa el riesgo real, no el ruido.
"""

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload, timeout=120) as resp:
            data = await resp.json()
            text = data["content"][0]["text"]
            # Extract JSON from response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {"error": "No JSON found", "raw": text}


async def analizar_con_perplexity_update():
    """Buscar actualizaciones de última hora"""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {os.environ.get('SONAR_API_KEY')}", "Content-Type": "application/json"}
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": "¿Hay noticias de hoy 8 de abril de 2026 sobre la diputada Clara Rosales Montiel de Yucatán? ¿Alguna crisis, escándalo o polémica? Incluye fuentes.",
            }
        ],
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
        except:
            return "No se pudo obtener actualización en tiempo real."


async def main():
    print("=" * 70)
    print("DIAGNÓSTICO DE CRISIS — CLARA ROSALES MONTIEL")
    print(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("Framework: LATAM-POLICRIS v1")
    print("=" * 70)

    # 1. Actualización en tiempo real
    print("\n📡 Buscando actualizaciones de última hora...")
    update = await analizar_con_perplexity_update()
    print(f"  Perplexity update: {len(update)} chars")

    # 2. Análisis profundo con Claude
    print("\n🧠 Analizando con Claude (LATAM-POLICRIS v1)...")
    diagnosis = await analizar_con_claude(DOSSIER + "\n\nACTUALIZACIÓN EN TIEMPO REAL:\n" + update)

    # 3. Guardar JSON
    os.makedirs("/home/ubuntu/skills/media-crisis-control/data/reports", exist_ok=True)
    json_path = "/home/ubuntu/skills/media-crisis-control/data/reports/diagnostico_clara_rosales_20260408.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(diagnosis, f, indent=2, ensure_ascii=False)
    print(f"\n✅ JSON guardado: {json_path}")

    # 4. Imprimir resumen
    print(f"\n{'=' * 70}")
    print(f"RESULTADO: {diagnosis.get('crisis_level', 'N/A')} (Score: {diagnosis.get('severity_score', 'N/A')}/100)")
    print(f"Tipo: {diagnosis.get('crisis_type', 'N/A')}")
    print(f"Tendencia: {diagnosis.get('trend', 'N/A')}")
    print(f"Resumen: {diagnosis.get('executive_summary', 'N/A')}")
    print(f"{'=' * 70}")


asyncio.run(main())
