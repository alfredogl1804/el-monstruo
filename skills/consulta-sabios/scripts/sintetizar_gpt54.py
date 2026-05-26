#!/usr/bin/env python3.11
"""
sintetizar_gpt54.py — GPT-5.4 como Orquestador Final
======================================================
Toma las respuestas combinadas de los sabios y genera una síntesis definitiva.
Ahora inyecta automáticamente el informe de validación post-consulta.

Uso:
    python3.11 sintetizar_gpt54.py \\
        --input /ruta/respuestas_combinadas.md \\
        --output /ruta/sintesis_final.md \\
        [--pregunta-original /ruta/prompt_original.md] \\
        [--informe-validacion /ruta/informe_validacion.md] \\
        [--instrucciones "Enfócate en las decisiones concretas"]

Cambios P0 (auditoría sabios 2026-04-08):
    - Añadido --informe-validacion con inyección explícita y precedencia
    - Añadido fallback a Claude y Grok si GPT-5.4 falla
    - Retorna dict con metadata para telemetría
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conector_sabios import consultar_sabio

SYSTEM_ORQUESTADOR = """Eres GPT-5.4 actuando como ORQUESTADOR FINAL del Consejo de Sabios.

Tu rol es sintetizar las respuestas de múltiples modelos de IA de primer nivel (Claude, Gemini, Grok, DeepSeek, Perplexity) en un documento definitivo.

Protocolo de síntesis:
1. CONSENSO: Identifica los puntos donde todos o la mayoría coinciden
2. DIVERGENCIA: Señala explícitamente donde hay desacuerdos y por qué importan
3. INSIGHTS ÚNICOS: Destaca ideas que solo un sabio mencionó pero son valiosas
4. DECISIONES: Propón decisiones concretas basadas en el análisis colectivo
5. GAPS: Identifica qué faltó en las respuestas y qué se necesita investigar más
6. ACCIÓN: Termina con una lista priorizada de próximos pasos

Reglas de validación:
- Si se incluye un INFORME DE VALIDACIÓN POST-CONSULTA, sus hallazgos tienen PRECEDENCIA
  sobre las afirmaciones originales de los sabios cuando hay contradicción.
- Señala explícitamente qué afirmaciones fueron corregidas por la validación.
- Integra la información nueva descubierta en la validación que los sabios no mencionaron.

Formato:
- Usa Markdown profesional con headers claros
- Incluye una tabla de consenso/divergencia cuando sea útil
- Sé denso pero legible: cada párrafo debe aportar valor
- NO repitas lo que dijeron los sabios textualmente; sintetiza y eleva
- Separa claramente: hechos verificados, inferencias, y supuestos no verificados"""

# Cadena de fallback si GPT-5.4 falla
FALLBACK_CHAIN = ["gpt54", "claude", "grok"]


async def sintetizar(
    input_path: str,
    output_path: str,
    pregunta_original: str = None,
    informe_validacion: str = None,
    instrucciones: str = None,
) -> dict:
    """
    Genera la síntesis final usando GPT-5.4 (con fallback a Claude y Grok).

    Returns:
        dict con metadata: modelo_usado, tiempo_seg, chars_entrada, chars_salida, exito, error
    """
    meta = {
        "timestamp": datetime.now().isoformat(),
        "modelo_usado": None,
        "tiempo_seg": 0,
        "chars_entrada": 0,
        "chars_salida": 0,
        "exito": False,
        "error": None,
        "informe_validacion_inyectado": False,
        "fallback_usado": False,
    }

    with open(input_path, "r", encoding="utf-8") as f:
        respuestas = f.read()

    # Construir prompt
    prompt_parts = []

    if pregunta_original:
        with open(pregunta_original, "r", encoding="utf-8") as f:
            pregunta = f.read()
        prompt_parts.append(f"## Pregunta Original que se hizo a los sabios:\n\n{pregunta}\n\n---\n")

    prompt_parts.append(f"## Respuestas de los Sabios:\n\n{respuestas}")

    # INYECCIÓN DEL INFORME DE VALIDACIÓN (P0-1)
    if informe_validacion:
        with open(informe_validacion, "r", encoding="utf-8") as f:
            validacion = f.read()
        prompt_parts.append(
            f"\n\n---\n\n"
            f"## INFORME DE VALIDACIÓN POST-CONSULTA (TIENE PRECEDENCIA)\n\n"
            f"El siguiente informe fue generado verificando las afirmaciones de los sabios "
            f"contra datos reales en tiempo real. Cuando hay contradicción entre lo que dijo "
            f"un sabio y lo que encontró la validación, LA VALIDACIÓN PREVALECE.\n\n"
            f"{validacion}"
        )
        meta["informe_validacion_inyectado"] = True
        print(f"📋 Informe de validación inyectado: {len(validacion):,} caracteres")

    if instrucciones:
        prompt_parts.append(f"\n\n---\n\n## Instrucciones adicionales para la síntesis:\n{instrucciones}")

    prompt_parts.append(
        "\n\n---\n\n"
        "Genera ahora la SÍNTESIS DEFINITIVA del Consejo de Sabios. "
        "Sigue el protocolo de síntesis: consenso, divergencia, insights únicos, decisiones, gaps, acción. "
        "Integra las correcciones del informe de validación cuando exista."
    )

    prompt = "\n".join(prompt_parts)
    meta["chars_entrada"] = len(prompt)

    print(f"📄 Respuestas de entrada: {len(respuestas):,} caracteres")
    print(f"📝 Prompt total: {len(prompt):,} caracteres")

    # Intentar con cadena de fallback
    for i, sabio_id in enumerate(FALLBACK_CHAIN):
        if i > 0:
            print(f"⚠️  Fallback: intentando con {sabio_id}...")
            meta["fallback_usado"] = True

        print(f"🤖 Enviando a {sabio_id} como orquestador...")

        resultado = await consultar_sabio(
            sabio_id=sabio_id,
            prompt=prompt,
            system=SYSTEM_ORQUESTADOR,
            reintentos=2,
        )

        if resultado["exito"]:
            sintesis = resultado["respuesta"]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"<!-- Síntesis generada por {resultado['sabio']} (Orquestador) — {timestamp} -->\n")
                f.write(f"<!-- Tiempo de generación: {resultado['tiempo_seg']}s -->\n")
                if meta["informe_validacion_inyectado"]:
                    f.write("<!-- Informe de validación: INYECTADO -->\n")
                if meta["fallback_usado"]:
                    f.write("<!-- NOTA: Se usó fallback (modelo original no disponible) -->\n")
                f.write(f"\n{sintesis}")

            meta["modelo_usado"] = resultado["modelo"]
            meta["tiempo_seg"] = resultado["tiempo_seg"]
            meta["chars_salida"] = len(sintesis)
            meta["exito"] = True

            print(f"✅ Síntesis generada en {resultado['tiempo_seg']}s")
            print(f"📁 Guardada en: {output_path}")
            print(f"📊 Tamaño: {len(sintesis):,} caracteres")
            return meta
        else:
            print(f"❌ {sabio_id} falló: {resultado['error'][:100]}")

    # Todos fallaron
    meta["error"] = "Todos los modelos de la cadena de fallback fallaron"
    print(f"🛑 ERROR CRÍTICO: {meta['error']}")
    return meta


async def main():
    parser = argparse.ArgumentParser(description="GPT-5.4 sintetiza las respuestas de los sabios")
    parser.add_argument("--input", required=True, help="Ruta al archivo de respuestas combinadas")
    parser.add_argument("--output", required=True, help="Ruta de salida para la síntesis")
    parser.add_argument("--pregunta-original", default=None, help="Ruta al prompt original (opcional)")
    parser.add_argument("--informe-validacion", default=None, help="Ruta al informe de validación post-consulta")
    parser.add_argument("--instrucciones", default=None, help="Instrucciones adicionales para la síntesis")

    args = parser.parse_args()
    meta = await sintetizar(
        args.input,
        args.output,
        args.pregunta_original,
        args.informe_validacion,
        args.instrucciones,
    )

    if not meta["exito"]:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
