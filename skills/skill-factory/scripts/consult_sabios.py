#!/usr/bin/env python3.11
"""
consult_sabios.py — Integración con consulta-sabios para diseño de skills complejas.

Cuando la skill es de complejidad alta o expert, consulta a los 6 sabios
para obtener recomendaciones de arquitectura, mejores prácticas y
validación del diseño.

Uso:
    python3.11 consult_sabios.py --spec spec.yaml --classification class.yaml \
        --dossier dossier.md --output-dir /path/to/output/
"""

import argparse, asyncio, json, os, sys, yaml, subprocess
from pathlib import Path

SABIOS_SCRIPTS = Path("/home/ubuntu/skills/consulta-sabios/scripts")


def prepare_consultation_prompt(spec: dict, classification: dict, dossier: str) -> str:
    """Prepara el prompt de consulta para los sabios."""
    
    return f"""# Consulta de Diseño de Skill — Consejo de Sabios

## Contexto
Estamos diseñando una skill de primer nivel para Manus (agente de IA autónomo).
Necesitamos la mejor arquitectura posible.

## Especificación
- **Nombre:** {spec.get('name')}
- **Dominio:** {spec.get('domain')}
- **Descripción:** {spec.get('description')}
- **Complejidad:** {classification.get('complexity_level')} (score: {classification.get('complexity_score')}/10)
- **Regulado:** {spec.get('regulated', False)}
- **Sensibilidad datos:** {spec.get('data_sensitivity', 'bajo')}

## Capacidades Core
{json.dumps(spec.get('core_capabilities', []), indent=2, ensure_ascii=False)}

## APIs Disponibles
{json.dumps(spec.get('apis_needed', []), indent=2, ensure_ascii=False)}

## Investigación de Dominio
{dossier[:8000]}

## Lo que necesitamos del Consejo

1. **Arquitectura óptima:** Scripts, flujo de ejecución, entrypoint
2. **Mejores prácticas del dominio:** Qué NO hacer, errores comunes
3. **Quality gates:** Qué validar antes de entregar
4. **Escalabilidad:** Cómo preparar para crecimiento
5. **Seguridad:** Riesgos específicos del dominio
6. **Diferenciadores:** Qué haría esta skill mejor que cualquier otra

Responde con recomendaciones concretas y accionables. No generalidades."""


async def run_consultation(prompt_path: str, output_dir: str, mode: str = "enjambre") -> dict:
    """Ejecuta la consulta a los sabios usando el entrypoint de consulta-sabios."""
    
    # Verificar que consulta-sabios existe
    entrypoint = SABIOS_SCRIPTS / "run_consulta_sabios.py"
    if not entrypoint.exists():
        # Fallback: usar consultar_paralelo.py directamente
        entrypoint = SABIOS_SCRIPTS / "consultar_paralelo.py"
    
    cmd = [
        "python3.11", str(entrypoint),
        "--prompt", prompt_path,
        "--output-dir", output_dir,
        "--modo", mode,
        "--profundidad-pre", "rapida"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=600,
            cwd=str(SABIOS_SCRIPTS)
        )
        
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-1000:] if result.stderr else ""
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "Consulta excedió 600s"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def extract_recommendations(output_dir: Path) -> dict:
    """Extrae recomendaciones de la salida de los sabios."""
    
    recommendations = {
        "architecture": [],
        "best_practices": [],
        "quality_gates": [],
        "security": [],
        "differentiators": []
    }
    
    # Buscar síntesis final
    synthesis = output_dir / "sintesis_final.md"
    if synthesis.exists():
        content = synthesis.read_text(encoding="utf-8")
        recommendations["synthesis"] = content
    
    # Buscar respuestas individuales
    for resp_file in output_dir.glob("resp_*.md"):
        sabio = resp_file.stem.replace("resp_", "")
        content = resp_file.read_text(encoding="utf-8")
        recommendations[f"sabio_{sabio}"] = content[:5000]
    
    return recommendations


async def main():
    parser = argparse.ArgumentParser(description="Consulta a los sabios para diseño de skills")
    parser.add_argument("--spec", required=True, help="Path al skill_spec.yaml")
    parser.add_argument("--classification", required=True, help="Path al classification.yaml")
    parser.add_argument("--dossier", default=None, help="Path al dossier de dominio")
    parser.add_argument("--output-dir", required=True, help="Directorio de salida")
    parser.add_argument("--mode", default="enjambre", choices=["enjambre", "consejo", "iterativo"],
                       help="Modo de consulta")
    args = parser.parse_args()
    
    with open(args.spec, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    
    with open(args.classification, 'r', encoding='utf-8') as f:
        classification = yaml.safe_load(f)
    
    dossier = ""
    if args.dossier and Path(args.dossier).exists():
        dossier = Path(args.dossier).read_text(encoding="utf-8")
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🧠 Consultando a los sabios para: {spec.get('name')}")
    print(f"   Modo: {args.mode}")
    
    # Preparar prompt
    prompt_text = prepare_consultation_prompt(spec, classification, dossier)
    prompt_path = output_dir / "prompt.md"
    prompt_path.write_text(prompt_text, encoding="utf-8")
    print(f"   Prompt: {len(prompt_text):,} chars")
    
    # Ejecutar consulta
    salida_dir = output_dir / "salida"
    salida_dir.mkdir(exist_ok=True)
    
    result = await run_consultation(str(prompt_path), str(salida_dir), args.mode)
    
    if result["status"] == "ok":
        print(f"   ✅ Consulta completada")
        recommendations = extract_recommendations(salida_dir)
        
        # Guardar recomendaciones
        rec_path = output_dir / "recommendations.yaml"
        with open(rec_path, 'w', encoding='utf-8') as f:
            yaml.dump(recommendations, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"   📁 Recomendaciones en: {rec_path}")
    else:
        print(f"   ❌ Error: {result.get('error', result.get('stderr', 'Unknown'))}")
    
    # Guardar resultado de ejecución
    exec_path = output_dir / "execution_result.yaml"
    with open(exec_path, 'w', encoding='utf-8') as f:
        yaml.dump(result, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    asyncio.run(main())
