#!/usr/bin/env python3.11
"""
investigar_contexto.py — Capa de Investigación en Tiempo Real (PRE-CONSULTA)
=============================================================================
Se ejecuta ANTES de consultar a los sabios. Analiza el prompt del usuario,
identifica los temas que requieren datos actualizados, y genera un
"Dossier de Realidad" con información verificada al día de hoy.

Este dossier se inyecta como contexto adicional a los sabios, para que
razonen sobre datos frescos en lugar de su entrenamiento congelado.

Estrategia dual:
    1. Perplexity Sonar (búsqueda web + razonamiento) → hallazgos estructurados
    2. GPT-5.4 (análisis del prompt) → identifica qué temas necesitan verificación

Uso:
    python3.11 investigar_contexto.py \\
        --prompt /ruta/al/prompt.md \\
        --output /ruta/dossier_realidad.md \\
        [--profundidad rapida|normal|profunda]
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conector_sabios import consultar_sabio, _get_creds, _json_serialize
import aiohttp

# Semáforo de concurrencia para Perplexity (P0-4: evita ráfagas que causan 429)
PERPLEXITY_SEMAPHORE = asyncio.Semaphore(4)  # Máximo 4 consultas simultáneas


# ═══════════════════════════════════════════════════════════════════
# PASO 1: GPT-5.4 analiza el prompt e identifica qué investigar
# ═══════════════════════════════════════════════════════════════════

SYSTEM_ANALIZADOR = """Eres un analista experto en identificar qué información de un prompt
necesita ser verificada o actualizada con datos en tiempo real.

Tu tarea: dado un prompt que se enviará a un consejo de 6 modelos de IA,
identifica EXACTAMENTE qué temas, datos, regulaciones, tecnologías, precios,
o hechos necesitan ser investigados en tiempo real porque los modelos de IA
podrían tener información desactualizada.

Responde ÚNICAMENTE con un JSON válido con esta estructura:
{
    "temas_a_investigar": [
        {
            "tema": "Descripción breve del tema",
            "queries": ["query de búsqueda 1", "query de búsqueda 2"],
            "razon": "Por qué este dato podría estar desactualizado",
            "prioridad": "alta|media|baja"
        }
    ],
    "fecha_sensibilidad": "alta|media|baja",
    "nota": "Breve explicación de por qué estos temas son sensibles al tiempo"
}

Reglas:
- Máximo 8 temas para profundidad "rapida", 15 para "normal", 25 para "profunda"
- Las queries deben ser en inglés Y español para máxima cobertura
- Prioriza: regulaciones > precios/costos > tecnologías > tendencias > opiniones
- Si el prompt es puramente filosófico/abstracto sin datos verificables, retorna lista vacía"""


async def analizar_prompt(prompt: str, profundidad: str) -> dict:
    """GPT-5.4 analiza el prompt e identifica qué investigar."""
    print("🔍 Paso 1: GPT-5.4 analizando qué necesita investigación en tiempo real...")

    instruccion = f"""Analiza el siguiente prompt que se enviará a 6 modelos de IA.
La fecha de hoy es {datetime.now().strftime('%d de %B de %Y')}.
Profundidad de investigación solicitada: {profundidad}

PROMPT A ANALIZAR:
---
{prompt}
---

Identifica qué temas necesitan datos actualizados en tiempo real."""

    resultado = await consultar_sabio(
        sabio_id="gpt54",
        prompt=instruccion,
        system=SYSTEM_ANALIZADOR,
        reintentos=2,
    )

    if not resultado["exito"]:
        print(f"  ❌ Error al analizar: {resultado['error']}")
        return {"temas_a_investigar": [], "fecha_sensibilidad": "desconocida", "nota": "Error en análisis"}

    # Parsear JSON de la respuesta
    try:
        texto = resultado["respuesta"]
        # Extraer JSON si viene envuelto en markdown code blocks
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0]
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0]
        analisis = json.loads(texto.strip())
        n_temas = len(analisis.get("temas_a_investigar", []))
        print(f"  ✅ Identificados {n_temas} temas que requieren investigación en tiempo real")
        return analisis
    except (json.JSONDecodeError, IndexError) as e:
        print(f"  ⚠️ No se pudo parsear JSON, usando respuesta como texto: {str(e)[:100]}")
        return {
            "temas_a_investigar": [],
            "fecha_sensibilidad": "desconocida",
            "nota": f"Respuesta no estructurada: {resultado['respuesta'][:200]}",
        }


# ═══════════════════════════════════════════════════════════════════
# PASO 2: Perplexity Sonar investiga cada tema en tiempo real
# ═══════════════════════════════════════════════════════════════════

async def investigar_tema_perplexity(tema: dict) -> dict:
    """Usa Perplexity Sonar para investigar un tema específico en tiempo real.
    Usa semáforo para limitar concurrencia y evitar rate limits (429)."""
    queries_text = "\n".join(f"- {q}" for q in tema["queries"])

    prompt = f"""Investiga el siguiente tema con información actualizada al día de hoy ({datetime.now().strftime('%d de %B de %Y')}):

TEMA: {tema['tema']}
RAZÓN DE LA INVESTIGACIÓN: {tema['razon']}

Queries de referencia:
{queries_text}

INSTRUCCIONES:
1. Proporciona DATOS CONCRETOS, FECHAS, NÚMEROS, NOMBRES actualizados
2. Cita las fuentes cuando sea posible
3. Si hay cambios recientes (últimos 6 meses), destácalos explícitamente
4. Si no encuentras información actualizada, dilo claramente
5. Sé conciso pero completo: máximo 500 palabras por tema"""

    async with PERPLEXITY_SEMAPHORE:
        resultado = await consultar_sabio(
            sabio_id="perplexity",
            prompt=prompt,
            system="Eres un investigador experto. Proporciona datos verificados y actualizados con fuentes.",
            reintentos=3,
        )

    return {
        "tema": tema["tema"],
        "prioridad": tema["prioridad"],
        "hallazgos": resultado["respuesta"] if resultado["exito"] else f"❌ Sin datos: {resultado.get('error', '?')[:100]}",
        "exito": resultado["exito"],
        "fuente": "Perplexity Sonar (búsqueda web en tiempo real)",
    }


# ═══════════════════════════════════════════════════════════════════
# PASO 3: Compilar el Dossier de Realidad
# ═══════════════════════════════════════════════════════════════════

def compilar_dossier(analisis: dict, hallazgos: list, prompt_original: str) -> str:
    """Compila todos los hallazgos en un Dossier de Realidad estructurado."""
    timestamp = datetime.now().strftime("%d de %B de %Y, %H:%M")

    lines = [
        "# Dossier de Realidad — Investigación en Tiempo Real",
        f"**Fecha de investigación:** {timestamp}",
        f"**Sensibilidad temporal del tema:** {analisis.get('fecha_sensibilidad', 'N/A')}",
        f"**Temas investigados:** {len(hallazgos)}",
        f"**Temas exitosos:** {sum(1 for h in hallazgos if h['exito'])}",
        "",
        "> Este dossier fue generado automáticamente por la capa de investigación en tiempo real",
        "> de Manus. Contiene datos verificados al momento de la consulta. Los sabios deben",
        "> considerar esta información como la más actualizada disponible.",
        "",
    ]

    # Hallazgos por prioridad
    for prioridad in ["alta", "media", "baja"]:
        temas_prio = [h for h in hallazgos if h["prioridad"] == prioridad]
        if not temas_prio:
            continue

        lines.append(f"## Prioridad {prioridad.upper()}")
        lines.append("")

        for h in temas_prio:
            estado = "✅" if h["exito"] else "❌"
            lines.append(f"### {estado} {h['tema']}")
            lines.append("")
            lines.append(h["hallazgos"])
            lines.append("")
            lines.append(f"*Fuente: {h['fuente']}*")
            lines.append("")
            lines.append("---")
            lines.append("")

    # Nota para los sabios
    lines.extend([
        "## Instrucción para los Sabios",
        "",
        "La información en este dossier es más reciente que tu fecha de entrenamiento.",
        "Cuando haya conflicto entre lo que sabes y lo que dice este dossier,",
        "**prioriza los datos del dossier** ya que fueron verificados en tiempo real.",
        "Si detectas inconsistencias, señálalas explícitamente en tu respuesta.",
    ])

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

async def main():
    parser = argparse.ArgumentParser(description="Investigación en tiempo real pre-consulta")
    parser.add_argument("--prompt", required=True, help="Ruta al archivo con el prompt")
    parser.add_argument("--output", required=True, help="Ruta de salida para el dossier")
    parser.add_argument("--profundidad", choices=["rapida", "normal", "profunda"], default="normal",
                        help="Profundidad de investigación (default: normal)")

    args = parser.parse_args()

    # Leer prompt
    with open(args.prompt, "r", encoding="utf-8") as f:
        prompt = f.read()

    print("=" * 60)
    print("🔬 CAPA DE INVESTIGACIÓN EN TIEMPO REAL (PRE-CONSULTA)")
    print(f"   Profundidad: {args.profundidad}")
    print(f"   Fecha: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("=" * 60)

    # Paso 1: Analizar qué investigar
    analisis = await analizar_prompt(prompt, args.profundidad)
    temas = analisis.get("temas_a_investigar", [])

    if not temas:
        print("\n✅ El prompt no requiere investigación en tiempo real (es puramente conceptual/abstracto).")
        # Generar dossier vacío
        dossier = (
            "# Dossier de Realidad\n\n"
            f"**Fecha:** {datetime.now().strftime('%d de %B de %Y, %H:%M')}\n\n"
            "El análisis del prompt determinó que no hay temas que requieran verificación en tiempo real.\n"
            "Los sabios pueden responder basándose en su conocimiento de entrenamiento.\n"
        )
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(dossier)
        print(f"📁 Dossier (vacío) guardado en: {args.output}")
        return

    # Paso 2: Investigar cada tema con Perplexity
    print(f"\n🌐 Paso 2: Investigando {len(temas)} temas con Perplexity Sonar...")
    tareas = [investigar_tema_perplexity(t) for t in temas]
    hallazgos = await asyncio.gather(*tareas)

    exitosos = sum(1 for h in hallazgos if h["exito"])
    print(f"  ✅ {exitosos}/{len(hallazgos)} temas investigados exitosamente")

    # Paso 3: Compilar dossier
    print("\n📋 Paso 3: Compilando Dossier de Realidad...")
    dossier = compilar_dossier(analisis, hallazgos, prompt)

    # Guardar
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(dossier)

    print(f"\n✅ Dossier de Realidad generado: {len(dossier):,} caracteres")
    print(f"📁 Guardado en: {args.output}")
    print("\n→ Este dossier debe inyectarse como contexto adicional al prompt de los sabios.")


if __name__ == "__main__":
    asyncio.run(main())
