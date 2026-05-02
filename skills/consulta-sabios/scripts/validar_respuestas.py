#!/usr/bin/env python3.11
"""
validar_respuestas.py — Capa de Validación en Tiempo Real (POST-CONSULTA)
==========================================================================
Se ejecuta DESPUÉS de recibir las respuestas de los sabios.
Extrae afirmaciones verificables (datos, fechas, regulaciones, herramientas,
precios) y las contrasta con la realidad actual usando Perplexity Sonar.

Genera un "Informe de Validación" que señala:
    - Afirmaciones confirmadas ✅
    - Afirmaciones desactualizadas ⚠️
    - Afirmaciones incorrectas ❌
    - Información que ningún sabio mencionó pero es relevante 🆕

Uso:
    python3.11 validar_respuestas.py \\
        --respuestas /ruta/respuestas_combinadas.md \\
        --output /ruta/informe_validacion.md \\
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

from conector_sabios import consultar_sabio

# Semáforo de concurrencia para Perplexity (P0-4: evita ráfagas que causan 429)
PERPLEXITY_SEMAPHORE = asyncio.Semaphore(4)  # Máximo 4 consultas simultáneas


# ═══════════════════════════════════════════════════════════════════
# PASO 1: GPT-5.4 extrae afirmaciones verificables
# ═══════════════════════════════════════════════════════════════════

SYSTEM_EXTRACTOR = """Eres un fact-checker de primer nivel. Tu tarea es analizar las respuestas
de múltiples modelos de IA y extraer TODAS las afirmaciones que pueden ser verificadas
contra la realidad actual.

Responde ÚNICAMENTE con un JSON válido con esta estructura:
{
    "afirmaciones": [
        {
            "texto": "La afirmación textual exacta",
            "sabio": "Nombre del sabio que la hizo",
            "tipo": "regulacion|dato_numerico|tecnologia|herramienta|fecha|precio|tendencia|otro",
            "query_verificacion": "Query para buscar si esto sigue siendo cierto hoy",
            "riesgo_desactualizacion": "alto|medio|bajo"
        }
    ],
    "temas_no_mencionados": [
        {
            "tema": "Tema relevante que ningún sabio mencionó",
            "query": "Query para investigar este tema"
        }
    ]
}

Reglas:
- Extrae máximo 10 afirmaciones para "rapida", 20 para "normal", 35 para "profunda"
- Prioriza afirmaciones con riesgo alto de desactualización
- Ignora opiniones subjetivas; solo extrae hechos verificables
- Las queries deben ser específicas y en inglés para máxima cobertura"""


async def extraer_afirmaciones(respuestas: str, profundidad: str) -> dict:
    """GPT-5.4 extrae afirmaciones verificables de las respuestas."""
    print("🔍 Paso 1: Extrayendo afirmaciones verificables de las respuestas...")

    prompt = f"""Analiza las siguientes respuestas de 6 modelos de IA y extrae las afirmaciones verificables.
Fecha de hoy: {datetime.now().strftime("%d de %B de %Y")}
Profundidad: {profundidad}

RESPUESTAS DE LOS SABIOS:
---
{respuestas}
---

Extrae las afirmaciones verificables ahora."""

    resultado = await consultar_sabio(
        sabio_id="gpt54",
        prompt=prompt,
        system=SYSTEM_EXTRACTOR,
        reintentos=2,
    )

    if not resultado["exito"]:
        print(f"  ❌ Error: {resultado['error']}")
        return {"afirmaciones": [], "temas_no_mencionados": []}

    try:
        texto = resultado["respuesta"]
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0]
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0]
        datos = json.loads(texto.strip())
        n_af = len(datos.get("afirmaciones", []))
        n_tm = len(datos.get("temas_no_mencionados", []))
        print(f"  ✅ {n_af} afirmaciones extraídas, {n_tm} temas no mencionados identificados")
        return datos
    except (json.JSONDecodeError, IndexError) as e:
        print(f"  ⚠️ Error parseando JSON: {str(e)[:100]}")
        return {"afirmaciones": [], "temas_no_mencionados": []}


# ═══════════════════════════════════════════════════════════════════
# PASO 2: Perplexity verifica cada afirmación
# ═══════════════════════════════════════════════════════════════════


async def verificar_afirmacion(af: dict) -> dict:
    """Verifica una afirmación individual contra la realidad actual."""
    prompt = f"""Verifica si la siguiente afirmación sigue siendo correcta al día de hoy ({datetime.now().strftime("%d de %B de %Y")}):

AFIRMACIÓN: "{af["texto"]}"
TIPO: {af["tipo"]}
QUERY DE VERIFICACIÓN: {af["query_verificacion"]}

Responde de forma concisa (máximo 200 palabras):
1. ¿Es correcta, parcialmente correcta, o incorrecta HOY?
2. Si hay cambios recientes, ¿cuáles son?
3. Fuentes que respaldan tu verificación"""

    async with PERPLEXITY_SEMAPHORE:
        resultado = await consultar_sabio(
            sabio_id="perplexity",
            prompt=prompt,
            system="Eres un verificador de hechos. Sé preciso y cita fuentes.",
            reintentos=3,
        )

    return {
        "afirmacion": af["texto"],
        "sabio": af["sabio"],
        "tipo": af["tipo"],
        "riesgo": af["riesgo_desactualizacion"],
        "verificacion": resultado["respuesta"] if resultado["exito"] else "❌ No se pudo verificar",
        "exito": resultado["exito"],
    }


async def investigar_tema_faltante(tema: dict) -> dict:
    """Investiga un tema que ningún sabio mencionó."""
    prompt = f"""Investiga el siguiente tema que es relevante pero no fue mencionado por ningún modelo de IA:

TEMA: {tema["tema"]}

Proporciona información actualizada al día de hoy ({datetime.now().strftime("%d de %B de %Y")}).
Máximo 300 palabras. Incluye datos concretos y fuentes."""

    async with PERPLEXITY_SEMAPHORE:
        resultado = await consultar_sabio(
            sabio_id="perplexity",
            prompt=prompt,
            system="Eres un investigador experto. Proporciona datos verificados y actualizados.",
            reintentos=3,
        )

    return {
        "tema": tema["tema"],
        "hallazgos": resultado["respuesta"] if resultado["exito"] else "❌ No se pudo investigar",
        "exito": resultado["exito"],
    }


# ═══════════════════════════════════════════════════════════════════
# PASO 3: Compilar Informe de Validación
# ═══════════════════════════════════════════════════════════════════


def compilar_informe(verificaciones: list, temas_nuevos: list) -> str:
    """Compila el informe de validación final."""
    timestamp = datetime.now().strftime("%d de %B de %Y, %H:%M")

    lines = [
        "# Informe de Validación en Tiempo Real",
        f"**Fecha de validación:** {timestamp}",
        f"**Afirmaciones verificadas:** {len(verificaciones)}",
        f"**Temas nuevos investigados:** {len(temas_nuevos)}",
        "",
        "> Este informe contrasta las respuestas de los sabios contra datos verificados",
        "> en tiempo real. Las discrepancias señaladas deben considerarse en la síntesis final.",
        "",
    ]

    # Verificaciones por riesgo
    if verificaciones:
        lines.append("## Verificación de Afirmaciones")
        lines.append("")

        for prioridad in ["alto", "medio", "bajo"]:
            verifs = [v for v in verificaciones if v["riesgo"] == prioridad]
            if not verifs:
                continue

            lines.append(f"### Riesgo {prioridad.upper()}")
            lines.append("")

            for v in verifs:
                lines.append(f'**Afirmación ({v["sabio"]}):** "{v["afirmacion"]}"')
                lines.append("")
                lines.append(f"**Verificación:** {v['verificacion']}")
                lines.append("")
                lines.append("---")
                lines.append("")

    # Temas no mencionados
    if temas_nuevos:
        lines.append("## Información Nueva (No Mencionada por Ningún Sabio)")
        lines.append("")

        for t in temas_nuevos:
            if t["exito"]:
                lines.append(f"### 🆕 {t['tema']}")
                lines.append("")
                lines.append(t["hallazgos"])
                lines.append("")
                lines.append("---")
                lines.append("")

    # Instrucción para el orquestador
    lines.extend(
        [
            "## Instrucción para el Orquestador (GPT-5.4)",
            "",
            "Al generar la síntesis final, incorpora las correcciones de este informe.",
            "Si una afirmación fue marcada como desactualizada o incorrecta, la síntesis",
            "debe reflejar la información correcta y actualizada, no la versión original del sabio.",
        ]
    )

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════


async def main():
    parser = argparse.ArgumentParser(description="Validación post-consulta en tiempo real")
    parser.add_argument("--respuestas", required=True, help="Ruta al archivo de respuestas combinadas")
    parser.add_argument("--output", required=True, help="Ruta de salida para el informe de validación")
    parser.add_argument(
        "--profundidad",
        choices=["rapida", "normal", "profunda"],
        default="normal",
        help="Profundidad de validación (default: normal)",
    )

    args = parser.parse_args()

    with open(args.respuestas, "r", encoding="utf-8") as f:
        respuestas = f.read()

    print("=" * 60)
    print("🔬 CAPA DE VALIDACIÓN EN TIEMPO REAL (POST-CONSULTA)")
    print(f"   Profundidad: {args.profundidad}")
    print(f"   Fecha: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print("=" * 60)

    # Paso 1: Extraer afirmaciones
    datos = await extraer_afirmaciones(respuestas, args.profundidad)
    afirmaciones = datos.get("afirmaciones", [])
    temas_faltantes = datos.get("temas_no_mencionados", [])

    if not afirmaciones and not temas_faltantes:
        print("\n✅ No se encontraron afirmaciones que requieran verificación.")
        informe = (
            "# Informe de Validación\n\n"
            f"**Fecha:** {datetime.now().strftime('%d de %B de %Y, %H:%M')}\n\n"
            "No se identificaron afirmaciones verificables que requieran contraste con datos actuales.\n"
        )
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(informe)
        return

    # Paso 2: Verificar afirmaciones en paralelo
    print(f"\n🌐 Paso 2: Verificando {len(afirmaciones)} afirmaciones con Perplexity Sonar...")
    tareas_verif = [verificar_afirmacion(af) for af in afirmaciones]

    print(f"🌐 Investigando {len(temas_faltantes)} temas no mencionados...")
    tareas_temas = [investigar_tema_faltante(t) for t in temas_faltantes]

    # Ejecutar todo en paralelo
    todos = await asyncio.gather(*(tareas_verif + tareas_temas))
    verificaciones = todos[: len(afirmaciones)]
    temas_nuevos = todos[len(afirmaciones) :]

    v_exitosas = sum(1 for v in verificaciones if v["exito"])
    t_exitosos = sum(1 for t in temas_nuevos if t["exito"])
    print(f"  ✅ {v_exitosas}/{len(verificaciones)} afirmaciones verificadas")
    print(f"  ✅ {t_exitosos}/{len(temas_nuevos)} temas nuevos investigados")

    # Paso 3: Compilar informe
    print("\n📋 Paso 3: Compilando Informe de Validación...")
    informe = compilar_informe(verificaciones, temas_nuevos)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(informe)

    print(f"\n✅ Informe de Validación generado: {len(informe):,} caracteres")
    print(f"📁 Guardado en: {args.output}")
    print("\n→ Este informe debe alimentar la síntesis final del orquestador (sintetizar_gpt54.py).")


if __name__ == "__main__":
    asyncio.run(main())
