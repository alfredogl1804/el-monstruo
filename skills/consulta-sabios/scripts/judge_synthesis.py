#!/usr/bin/env python3.11
"""
judge_synthesis.py — Evaluador/Juez Automático de Síntesis
============================================================
Evalúa la calidad de la síntesis final usando un modelo diferente
al que la generó (evitar auto-evaluación).

Dimensiones evaluadas:
    1. Fidelidad: ¿Refleja fielmente lo que dijeron los sabios?
    2. Cobertura: ¿Incluye las ideas clave de todos los sabios?
    3. Coherencia: ¿Es internamente consistente?
    4. Accionabilidad: ¿Las recomendaciones son concretas y ejecutables?
    5. Equilibrio: ¿Da peso justo a cada sabio sin sesgo?
    6. Valor agregado: ¿La síntesis aporta más que la suma de las partes?

Uso:
    python3.11 judge_synthesis.py --sintesis path/to/sintesis.md --respuestas path/to/respuestas/

Creado: 2026-04-08 (P3 auditoría sabios)
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conector_sabios import consultar_sabio
from json_parser import parse_json

JUDGE_PROMPT = """Eres un juez experto evaluando la calidad de una síntesis generada por un orquestador AI.

Tu trabajo es evaluar si la síntesis refleja fielmente y de manera útil las respuestas individuales de los sabios consultados.

## RESPUESTAS INDIVIDUALES DE LOS SABIOS:
{respuestas_individuales}

## SÍNTESIS A EVALUAR:
{sintesis}

## INSTRUCCIONES DE EVALUACIÓN:
Evalúa la síntesis en estas 6 dimensiones (score 0.0 a 1.0):

1. **Fidelidad** (0-1): ¿Refleja fielmente lo que dijeron los sabios? ¿Hay distorsiones o invenciones?
2. **Cobertura** (0-1): ¿Incluye las ideas clave de TODOS los sabios que respondieron? ¿Omite algo importante?
3. **Coherencia** (0-1): ¿Es internamente consistente? ¿Hay contradicciones no resueltas?
4. **Accionabilidad** (0-1): ¿Las recomendaciones son concretas, específicas y ejecutables?
5. **Equilibrio** (0-1): ¿Da peso justo a cada sabio? ¿Hay sesgo hacia alguno?
6. **Valor_agregado** (0-1): ¿La síntesis aporta más que simplemente concatenar respuestas?

Responde SOLO con JSON:
```json
{{
    "scores": {{
        "fidelidad": 0.0,
        "cobertura": 0.0,
        "coherencia": 0.0,
        "accionabilidad": 0.0,
        "equilibrio": 0.0,
        "valor_agregado": 0.0
    }},
    "score_global": 0.0,
    "fortalezas": ["..."],
    "debilidades": ["..."],
    "ideas_omitidas": ["..."],
    "distorsiones": ["..."],
    "recomendaciones_mejora": ["..."]
}}
```"""


async def judge(
    sintesis_text: str,
    respuestas_individuales: dict,
    judge_model: str = "gemini",
) -> dict:
    """
    Evalúa la calidad de una síntesis.

    Args:
        sintesis_text: Texto de la síntesis final
        respuestas_individuales: dict {sabio_id: respuesta_text}
        judge_model: Modelo a usar como juez (diferente al orquestador)

    Returns:
        dict con scores, fortalezas, debilidades, recomendaciones
    """
    # Preparar las respuestas individuales
    resp_text = ""
    for sabio_id, resp in respuestas_individuales.items():
        # Truncar respuestas muy largas para no exceder contexto del juez
        truncated = resp[:8000] if len(resp) > 8000 else resp
        resp_text += f"\n### {sabio_id.upper()}\n{truncated}\n"

    prompt = JUDGE_PROMPT.format(
        respuestas_individuales=resp_text,
        sintesis=sintesis_text[:15000],  # Truncar síntesis si es muy larga
    )

    print(f"⚖️  Evaluando síntesis con {judge_model} como juez...")

    resultado = await consultar_sabio(
        sabio_id=judge_model,
        prompt=prompt,
        system="Eres un evaluador experto de síntesis multi-agente. Responde SOLO con JSON válido.",
        reintentos=2,
    )

    if not resultado["exito"]:
        print(f"❌ Error del juez: {resultado.get('error', 'desconocido')}")
        # Intentar con modelo alternativo
        alt_model = "claude" if judge_model != "claude" else "grok"
        print(f"   Intentando con {alt_model}...")
        resultado = await consultar_sabio(
            sabio_id=alt_model,
            prompt=prompt,
            system="Eres un evaluador experto de síntesis multi-agente. Responde SOLO con JSON válido.",
            reintentos=1,
        )
        if not resultado["exito"]:
            return {"error": "Ningún juez pudo evaluar", "score_global": 0}

    # Parsear resultado
    evaluation = parse_json(resultado["respuesta"])

    if not evaluation or not isinstance(evaluation, dict):
        return {"error": "No se pudo parsear la evaluación", "score_global": 0}

    # Calcular score global si no viene
    if "score_global" not in evaluation or not evaluation["score_global"]:
        scores = evaluation.get("scores", {})
        if scores:
            evaluation["score_global"] = round(sum(scores.values()) / len(scores), 3)

    evaluation["judge_model"] = judge_model

    # Imprimir resumen
    print("\n📊 Evaluación de la síntesis:")
    scores = evaluation.get("scores", {})
    for dim, score in scores.items():
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        print(f"   {dim:20s} {bar} {score:.2f}")
    print(f"   {'GLOBAL':20s} {'=' * 10} {evaluation.get('score_global', 0):.2f}")

    if evaluation.get("debilidades"):
        print("\n   ⚠️  Debilidades:")
        for d in evaluation["debilidades"][:3]:
            print(f"      • {d}")

    if evaluation.get("ideas_omitidas"):
        print("\n   🔍 Ideas omitidas:")
        for i in evaluation["ideas_omitidas"][:3]:
            print(f"      • {i}")

    return evaluation


async def judge_from_files(
    sintesis_path: str,
    respuestas_dir: str,
    judge_model: str = "gemini",
) -> dict:
    """
    Evalúa desde archivos en disco.

    Args:
        sintesis_path: Ruta a la síntesis final
        respuestas_dir: Directorio con resp_*.md
        judge_model: Modelo juez
    """
    # Leer síntesis
    with open(sintesis_path, "r", encoding="utf-8") as f:
        sintesis_text = f.read()

    # Leer respuestas individuales
    respuestas = {}
    resp_dir = Path(respuestas_dir)
    for f in sorted(resp_dir.glob("resp_*.md")):
        sabio_id = f.stem.replace("resp_", "")
        respuestas[sabio_id] = f.read_text(encoding="utf-8")

    if not respuestas:
        # Intentar con .json
        for f in sorted(resp_dir.glob("resp_*.json")):
            sabio_id = f.stem.replace("resp_", "")
            data = json.loads(f.read_text(encoding="utf-8"))
            respuestas[sabio_id] = data.get("respuesta", str(data))

    print(f"📄 Síntesis: {len(sintesis_text):,} chars")
    print(f"📄 Respuestas: {len(respuestas)} sabios ({', '.join(respuestas.keys())})")

    return await judge(sintesis_text, respuestas, judge_model)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════


async def main():
    parser = argparse.ArgumentParser(description="Juez automático de síntesis")
    parser.add_argument("--sintesis", required=True, help="Ruta a la síntesis final")
    parser.add_argument("--respuestas", required=True, help="Directorio con respuestas individuales")
    parser.add_argument("--judge", default="gemini", help="Modelo juez (default: gemini)")
    parser.add_argument("--output", default=None, help="Guardar evaluación en JSON")

    args = parser.parse_args()
    evaluation = await judge_from_files(args.sintesis, args.respuestas, args.judge)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(evaluation, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n📁 Evaluación guardada: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
