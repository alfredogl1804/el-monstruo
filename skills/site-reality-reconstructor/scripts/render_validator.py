#!/usr/bin/env python3.11
"""
Render Validator — Valida un render contra el Site Reality Document.
Compara el render con las restricciones del SRD y emite un reporte de fidelidad.
"""

import argparse
import json
import os
import sys


def _encode_image(path: str) -> bytes:
    """Read image as bytes."""
    with open(path, "rb") as f:
        return f.read()


async def validate_render(srd_path: str, render_path: str) -> dict:
    """Valida un render contra un SRD."""
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "No GEMINI_API_KEY", "pass_fail": "ERROR"}

    # Load SRD
    with open(srd_path, "r") as f:
        srd = json.load(f)

    client = genai.Client(api_key=api_key)

    # Build validation prompt from SRD constraints
    constraints = srd.get("render_constraints", {})
    validation_rules = srd.get("validation_rules", {})
    context = srd.get("surrounding_context", {})
    blind_spots = srd.get("blind_spots", [])

    prompt = f"""Eres un validador de renders arquitectónicos. Tu trabajo es comparar este render con el Site Reality Document (SRD) y determinar si es fiel a la realidad.

## SITIO: {srd.get("site_metadata", {}).get("name", "Unknown")}

## CONTEXTO REAL POR ORIENTACIÓN
Norte: {json.dumps(context.get("north", {}), ensure_ascii=False)}
Sur: {json.dumps(context.get("south", {}), ensure_ascii=False)}
Este: {json.dumps(context.get("east", {}), ensure_ascii=False)}
Oeste: {json.dumps(context.get("west", {}), ensure_ascii=False)}

## RESTRICCIONES — DEBE INCLUIR
{json.dumps(constraints.get("must_include", []), indent=1, ensure_ascii=False)}

## RESTRICCIONES — NO DEBE INCLUIR
{json.dumps(constraints.get("must_not_include", []), indent=1, ensure_ascii=False)}

## LÍMITES DE ALTURA
{json.dumps(constraints.get("height_limits", []), indent=1, ensure_ascii=False)}

## RESTRICCIONES DE PAISAJE
{json.dumps(constraints.get("landscape_constraints", []), indent=1, ensure_ascii=False)}

## BLIND SPOTS (zonas sin información — no deben tener detalle)
{json.dumps(blind_spots, indent=1, ensure_ascii=False)}

## REGLAS CRÍTICAS (fallo automático si se viola)
{json.dumps(validation_rules.get("critical", []), indent=1, ensure_ascii=False)}

## REGLAS MAYORES
{json.dumps(validation_rules.get("major", []), indent=1, ensure_ascii=False)}

## TU TAREA
Analiza el render y responde en JSON:

{{
  "reality_fidelity_score": 0.0,
  "pass_fail": "PASS|FAIL",
  "critical_violations": [
    {{"rule": "descripción", "found_in_render": "qué se ve", "expected_reality": "qué debería ser"}}
  ],
  "major_violations": [
    {{"rule": "descripción", "found_in_render": "qué se ve", "expected_reality": "qué debería ser"}}
  ],
  "minor_violations": [
    {{"rule": "descripción", "found_in_render": "qué se ve", "expected_reality": "qué debería ser"}}
  ],
  "positive_matches": [
    {{"element": "qué está correcto", "note": "por qué está bien"}}
  ],
  "corrective_instructions": "Instrucciones específicas para corregir el render si falla",
  "summary": "Resumen de la validación"
}}

REGLA: Si hay CUALQUIER critical_violation, pass_fail DEBE ser "FAIL" sin importar el score."""

    # Read render image
    img_bytes = _encode_image(render_path)
    mime = "image/png" if render_path.lower().endswith(".png") else "image/jpeg"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(inline_data=types.Blob(mime_type=mime, data=img_bytes)),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        text = response.text if response.text else "{}"
        report = json.loads(text)
        report["render_file"] = os.path.basename(render_path)
        report["srd_file"] = os.path.basename(srd_path)
        return report

    except Exception as e:
        return {
            "error": str(e),
            "pass_fail": "ERROR",
            "render_file": os.path.basename(render_path),
        }


async def validate_all_renders(srd_path: str, renders_dir: str, output_path: str):
    """Valida todos los renders en un directorio contra un SRD."""
    renders = sorted(
        [
            os.path.join(renders_dir, f)
            for f in os.listdir(renders_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        ]
    )

    results = []
    passed = 0
    failed = 0

    for render_path in renders:
        print(f"  Validando: {os.path.basename(render_path)}...")
        report = await validate_render(srd_path, render_path)
        results.append(report)

        status = report.get("pass_fail", "ERROR")
        if status == "PASS":
            passed += 1
            print(f"    ✓ PASS (score: {report.get('reality_fidelity_score', 'N/A')})")
        elif status == "FAIL":
            failed += 1
            crits = len(report.get("critical_violations", []))
            print(f"    ✗ FAIL — {crits} violaciones críticas")
        else:
            print(f"    ? ERROR — {report.get('error', 'unknown')}")

    summary = {
        "total_renders": len(renders),
        "passed": passed,
        "failed": failed,
        "errors": len(renders) - passed - failed,
        "results": results,
    }

    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n  Resumen: {passed}/{len(renders)} PASS, {failed}/{len(renders)} FAIL")
    return summary


if __name__ == "__main__":
    import asyncio

    parser = argparse.ArgumentParser(description="Render Validator")
    parser.add_argument("--srd", required=True, help="Path to site_reality.json")
    parser.add_argument("--render", default=None, help="Path to single render image")
    parser.add_argument("--renders-dir", default=None, help="Path to directory with renders")
    parser.add_argument("--output", required=True, help="Path to output report")
    args = parser.parse_args()

    if args.render:
        report = asyncio.run(validate_render(args.srd, args.render))
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        print(f"Resultado: {report.get('pass_fail', 'ERROR')}")
    elif args.renders_dir:
        asyncio.run(validate_all_renders(args.srd, args.renders_dir, args.output))
    else:
        print("Error: Debe especificar --render o --renders-dir")
        sys.exit(1)
