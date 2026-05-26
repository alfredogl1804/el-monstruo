#!/usr/bin/env python3.11
"""
consultar_paralelo.py — Motor de Consulta Paralela a los 6 Sabios
==================================================================
Script principal para lanzar consultas al enjambre.

Uso:
    python3.11 consultar_paralelo.py \\
        --prompt /ruta/al/prompt.md \\
        --system "Eres un experto en..." \\
        --output /ruta/salida/ \\
        [--prompt-condensado /ruta/al/resumen.md] \\
        [--sabios gpt54,claude,gemini,grok,deepseek,perplexity] \\
        [--modo enjambre|consejo|iterativo]

Modos:
    enjambre  (default): Los 6 sabios en paralelo → GPT-5.4 sintetiza
    consejo:  Solo los 4 sabios de 1M+ contexto (excluye DeepSeek y Perplexity)
    iterativo: Consulta secuencial, cada sabio lee lo que dijo el anterior
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio del script al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conector_sabios import (
    SABIOS,
    consultar_sabio,
    consultar_todos,
    ping_todos,
    resumen_resultados,
)


def leer_archivo(ruta: str) -> str:
    """Lee un archivo de texto y retorna su contenido."""
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def guardar_resumen(directorio: str, resultados: list, modo: str):
    """Guarda el resumen general de la consulta."""
    path = Path(directorio)
    path.mkdir(parents=True, exist_ok=True)

    resumen = resumen_resultados(resultados)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Resumen legible
    with open(path / f"resumen_{timestamp}.md", "w", encoding="utf-8") as f:
        f.write(f"# Consulta a los Sabios — {timestamp}\n")
        f.write(f"**Modo:** {modo}\n\n")
        f.write(resumen)

    # Metadata JSON completa
    meta = {
        "timestamp": datetime.now().isoformat(),
        "modo": modo,
        "sabios_consultados": len(resultados),
        "exitosos": sum(1 for r in resultados if r.get("exito")),
        "resultados": [{k: v for k, v in r.items() if k != "respuesta"} for r in resultados],
    }
    with open(path / f"metadata_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return resumen


async def modo_enjambre(prompt: str, prompt_condensado: str, system: str, sabios_ids: list, output_dir: str):
    """Modo Enjambre: Todos los sabios en paralelo."""
    print(f"\n🐝 MODO ENJAMBRE — Consultando {len(sabios_ids)} sabios en paralelo...\n")

    resultados = await consultar_todos(
        prompt_completo=prompt,
        prompt_condensado=prompt_condensado,
        system=system,
        sabios=sabios_ids,
        guardar_en=output_dir,
    )

    resumen = guardar_resumen(output_dir, resultados, "enjambre")
    print(resumen)

    exitosos = sum(1 for r in resultados if r.get("exito"))
    if exitosos < 3:
        print("\n🛑 ALTO: Menos de 3 sabios respondieron. Protocolo semilla v7.3 violado.")
    else:
        print(f"\n✅ {exitosos}/{len(resultados)} sabios respondieron.")
        print(f"📁 Respuestas guardadas en: {output_dir}")

    return resultados


async def modo_consejo(prompt: str, system: str, output_dir: str):
    """Modo Consejo Reducido: Solo los 4 sabios de 1M+ contexto."""
    sabios_1m = [sid for sid, cfg in SABIOS.items() if cfg["grupo"] == "completo"]
    print(f"\n👥 MODO CONSEJO — Consultando {len(sabios_1m)} sabios de 1M+ contexto...\n")

    resultados = await consultar_todos(
        prompt_completo=prompt,
        system=system,
        sabios=sabios_1m,
        guardar_en=output_dir,
    )

    resumen = guardar_resumen(output_dir, resultados, "consejo")
    print(resumen)
    return resultados


async def modo_iterativo(prompt: str, system: str, sabios_ids: list, output_dir: str):
    """Modo Iterativo: Consulta secuencial, cada sabio lee lo que dijo el anterior."""
    print(f"\n🔄 MODO ITERATIVO — Consultando {len(sabios_ids)} sabios secuencialmente...\n")

    acumulado = ""
    resultados = []

    for i, sid in enumerate(sabios_ids):
        config = SABIOS.get(sid)
        if not config:
            continue

        # Construir prompt iterativo
        if acumulado:
            prompt_iterativo = (
                f"{prompt}\n\n"
                f"---\n\n"
                f"## Respuestas anteriores de otros sabios (para que las consideres, mejores y complementes):\n\n"
                f"{acumulado}"
            )
        else:
            prompt_iterativo = prompt

        print(f"  [{i + 1}/{len(sabios_ids)}] Consultando {config['nombre']}...")

        resultado = await consultar_sabio(
            sabio_id=sid,
            prompt=prompt_iterativo,
            system=system,
            guardar_en=output_dir,
        )

        resultados.append(resultado)

        if resultado.get("exito"):
            acumulado += f"\n### {config['nombre']}:\n{resultado['respuesta']}\n\n---\n"
            print(f"       ✅ Respondió en {resultado['tiempo_seg']}s")
        else:
            print(f"       ❌ Error: {resultado.get('error', '?')[:80]}")

    resumen = guardar_resumen(output_dir, resultados, "iterativo")
    print(f"\n{resumen}")
    return resultados


async def main():
    parser = argparse.ArgumentParser(
        description="Consulta paralela a los 6 sabios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--prompt", required=True, help="Ruta al archivo con el prompt principal")
    parser.add_argument(
        "--system", default="Eres un experto analista y estratega de primer nivel mundial.", help="System prompt"
    )
    parser.add_argument("--output", required=True, help="Directorio de salida para las respuestas")
    parser.add_argument("--prompt-condensado", default=None, help="Ruta al prompt condensado para sabios de 128K")
    parser.add_argument("--sabios", default=None, help="Lista de sabios separados por coma (default: todos)")
    parser.add_argument(
        "--modo", choices=["enjambre", "consejo", "iterativo"], default="enjambre", help="Modo de consulta"
    )
    parser.add_argument("--skip-ping", action="store_true", help="Saltar pre-vuelo (no recomendado)")

    args = parser.parse_args()

    # Leer prompt
    prompt = leer_archivo(args.prompt)
    prompt_condensado = leer_archivo(args.prompt_condensado) if args.prompt_condensado else None

    # Determinar sabios
    if args.sabios:
        sabios_ids = [s.strip() for s in args.sabios.split(",")]
    else:
        sabios_ids = list(SABIOS.keys())

    # Pre-vuelo
    if not args.skip_ping:
        print("🏓 Pre-vuelo: Verificando conexiones...")
        ping_results = await ping_todos()
        operativos = sum(1 for r in ping_results if r.get("exito"))
        if operativos < 3:
            print(f"🛑 ALTO: Solo {operativos}/6 sabios operativos. Abortando.")
            sys.exit(1)
        print(f"✅ {operativos}/6 sabios operativos. Procediendo.\n")

    # Ejecutar según modo
    if args.modo == "enjambre":
        resultados = await modo_enjambre(prompt, prompt_condensado, args.system, sabios_ids, args.output)
    elif args.modo == "consejo":
        resultados = await modo_consejo(prompt, args.system, args.output)
    elif args.modo == "iterativo":
        resultados = await modo_iterativo(prompt, args.system, sabios_ids, args.output)

    # Generar archivo combinado para el orquestador
    output_path = Path(args.output)
    combinado = output_path / "respuestas_combinadas.md"
    with open(combinado, "w", encoding="utf-8") as f:
        f.write("# Respuestas Combinadas de los Sabios\n")
        f.write(f"**Fecha:** {datetime.now().isoformat()}\n")
        f.write(f"**Modo:** {args.modo}\n\n")
        for r in resultados:
            if r.get("exito"):
                f.write(f"---\n\n## {r['sabio']} ({r['modelo']})\n\n")
                f.write(f"{r['respuesta']}\n\n")
            else:
                f.write(f"---\n\n## {r['sabio']} — ❌ NO RESPONDIÓ\n\n")
                f.write(f"Error: {r.get('error', 'Desconocido')}\n\n")

    print(f"\n📄 Respuestas combinadas guardadas en: {combinado}")
    print("   → Listo para enviar al orquestador (sintetizar_gpt54.py)")


if __name__ == "__main__":
    asyncio.run(main())
