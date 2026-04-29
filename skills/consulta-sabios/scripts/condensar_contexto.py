#!/usr/bin/env python3.11
"""
condensar_contexto.py — Genera resumen ejecutivo para sabios de 128K (DeepSeek, Perplexity)
============================================================================================
Cuando el contexto completo excede ~100K caracteres, este script usa GPT-5.4 para
generar un resumen ejecutivo de ~30K caracteres que preserva la esencia.

Uso:
    python3.11 condensar_contexto.py \\
        --input /ruta/al/contexto_completo.md \\
        --output /ruta/al/resumen_ejecutivo.md \\
        [--max-chars 30000]
"""

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conector_sabios import consultar_sabio


SYSTEM_CONDENSADOR = """Eres un experto en síntesis de documentos complejos. Tu tarea es crear un RESUMEN EJECUTIVO
que preserve TODA la información crítica, decisiones clave, datos numéricos, y matices importantes del documento original.

Reglas:
1. NO omitas datos numéricos, fechas, nombres propios, o decisiones específicas
2. Preserva la estructura lógica del documento original
3. Usa lenguaje preciso y denso (cada oración debe aportar información)
4. El resumen debe ser autosuficiente: alguien que lo lea debe entender el contexto completo
5. Prioriza: decisiones > datos > argumentos > contexto general
6. Mantén las citas textuales más importantes entre comillas"""


async def condensar(input_text_or_path: str, output_path: str = None, max_chars: int = 30000) -> str:
    """
    Condensa un documento largo usando GPT-5.4.
    Acepta texto directo o ruta a archivo.
    Retorna el texto condensado.
    """
    import os as _os
    if _os.path.isfile(input_text_or_path):
        with open(input_text_or_path, "r", encoding="utf-8") as f:
            contenido = f.read()
    else:
        contenido = input_text_or_path

    chars_original = len(contenido)
    print(f"📄 Documento original: {chars_original:,} caracteres")

    if chars_original <= max_chars:
        print(f"\u2705 El documento ya cabe en {max_chars:,} chars. Sin cambios.")
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(contenido)
        return contenido

    ratio = max_chars / chars_original
    print(f"📐 Ratio de compresión necesario: {ratio:.1%}")
    print(f"🎯 Objetivo: ~{max_chars:,} caracteres")
    print(f"🤖 Enviando a GPT-5.4 para condensar...")

    prompt = f"""Condensa el siguiente documento a un RESUMEN EJECUTIVO de máximo {max_chars:,} caracteres.

DOCUMENTO ORIGINAL ({chars_original:,} caracteres):

---

{contenido}

---

Genera el resumen ejecutivo ahora. Recuerda: máximo {max_chars:,} caracteres, preservando TODA la información crítica."""

    resultado = await consultar_sabio(
        sabio_id="gpt54",
        prompt=prompt,
        system=SYSTEM_CONDENSADOR,
        reintentos=2,
    )

    if resultado["exito"]:
        resumen = resultado["respuesta"]
        chars_resumen = len(resumen)
        print(f"\u2705 Resumen generado: {chars_resumen:,} caracteres ({chars_resumen/chars_original:.1%} del original)")

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"<!-- Resumen ejecutivo generado por GPT-5.4 -->\n")
                f.write(f"<!-- Original: {chars_original:,} chars \u2192 Resumen: {chars_resumen:,} chars -->\n\n")
                f.write(resumen)
            print(f"\ud83d\udcc1 Guardado en: {output_path}")

        return resumen
    else:
        print(f"\u274c Error al condensar: {resultado['error']}")
        return contenido  # Fallback: retorna original


async def main():
    parser = argparse.ArgumentParser(description="Condensa contexto para sabios de 128K")
    parser.add_argument("--input", required=True, help="Ruta al documento completo")
    parser.add_argument("--output", required=True, help="Ruta de salida para el resumen")
    parser.add_argument("--max-chars", type=int, default=30000, help="Máximo de caracteres (default: 30000)")

    args = parser.parse_args()
    result = await condensar(args.input, args.output, args.max_chars)
    if not result:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
