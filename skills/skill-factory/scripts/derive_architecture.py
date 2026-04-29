#!/usr/bin/env python3.11
"""
derive_architecture.py — Diseña la arquitectura de una skill.

Toma la spec, clasificación y dossier de dominio, y usa GPT-5.4 para
diseñar la arquitectura completa: scripts, referencias, templates, flujo.

Uso:
    python3.11 derive_architecture.py --spec spec.yaml --classification class.yaml \
        --dossier dossier.md --output architecture.yaml
"""

import argparse, asyncio, json, os, sys, yaml
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

FACTORY_ROOT = Path(__file__).parent.parent


def load_recipe(domain: str) -> str:
    """Carga la recipe del dominio si existe."""
    recipe_path = FACTORY_ROOT / "references" / "recipes" / f"{domain}.md"
    if recipe_path.exists():
        return recipe_path.read_text(encoding="utf-8")
    return ""


def load_api_matrix() -> str:
    """Carga la matriz de capacidades de APIs."""
    matrix_path = FACTORY_ROOT / "references" / "api-capability-matrix.md"
    if matrix_path.exists():
        return matrix_path.read_text(encoding="utf-8")
    return ""


def load_ecosystem_state() -> str:
    """Carga el ecosystem state de api-context-injector (contrato compartido v4.0)."""
    eco_path = Path("/home/ubuntu/skills/api-context-injector/routing/ecosystem_state.yaml")
    if eco_path.exists():
        try:
            with open(eco_path) as f:
                data = yaml.safe_load(f)
            # Extraer solo las secciones relevantes para arquitectura
            relevant = {
                "capability_summary": data.get("capability_summary", {}),
                "secrets_deployment": {
                    "sandbox_env_vars": data.get("secrets_deployment", {}).get("sandbox_env_vars", {}),
                    "scaffold_rules": data.get("secrets_deployment", {}).get("scaffold_rules", {}),
                },
                "policy_compliance": data.get("policy_compliance", {}),
            }
            return yaml.dump(relevant, default_flow_style=False, allow_unicode=True)
        except Exception:
            return ""
    return ""


async def design_architecture(spec: dict, classification: dict, dossier: str) -> dict:
    """Usa GPT-5.4 para diseñar la arquitectura de la skill."""
    
    recipe = load_recipe(spec.get("domain", "general"))
    api_matrix = load_api_matrix()
    ecosystem_state = load_ecosystem_state()
    
    # Truncar dossier si es muy largo
    if len(dossier) > 30000:
        dossier = dossier[:30000] + "\n\n[... truncado por longitud ...]"
    
    prompt = f"""Eres el arquitecto principal de skill-factory. Diseña la arquitectura completa
para construir esta skill.

## Especificación
```yaml
{yaml.dump(spec, default_flow_style=False, allow_unicode=True)}
```

## Clasificación de Complejidad
```yaml
{yaml.dump(classification, default_flow_style=False, allow_unicode=True)}
```

## Dossier de Dominio (investigación en tiempo real)
{dossier[:15000]}

## APIs y Herramientas Disponibles
{api_matrix[:5000]}

## Recipe del Dominio
{recipe[:3000] if recipe else "No hay recipe específica para este dominio."}

## Ecosystem State (api-context-injector v4.0)
{ecosystem_state[:4000] if ecosystem_state else "No disponible — usar api_matrix como referencia."}

---

Diseña la arquitectura como un JSON con esta estructura exacta:

{{
  "skill_name": "nombre-kebab",
  "directory_structure": {{
    "scripts": ["lista de scripts .py con descripción breve"],
    "references": ["lista de archivos .md de referencia"],
    "templates": ["lista de templates si aplica"],
    "config": ["lista de archivos de configuración si aplica"]
  }},
  "scripts_detail": [
    {{
      "filename": "script.py",
      "purpose": "qué hace",
      "type": "core|utility|validator|entrypoint",
      "apis_used": ["apis que usa"],
      "inputs": ["qué recibe"],
      "outputs": ["qué produce"],
      "dependencies": ["otros scripts de los que depende"],
      "estimated_lines": 150,
      "priority": "P0|P1|P2"
    }}
  ],
  "references_detail": [
    {{
      "filename": "reference.md",
      "purpose": "qué contiene",
      "sections": ["secciones principales"]
    }}
  ],
  "execution_flow": [
    {{
      "step": 1,
      "script": "script.py",
      "description": "qué hace en el flujo",
      "depends_on": []
    }}
  ],
  "entrypoint": "nombre del script principal",
  "skill_md_sections": ["secciones que debe tener el SKILL.md"],
  "quality_gates": ["validaciones que se deben ejecutar"],
  "estimated_total_lines": 500,
  "estimated_build_time_minutes": 30,
  "risks": ["riesgos identificados"],
  "mitigations": ["mitigaciones para cada riesgo"]
}}

Sé concreto y práctico. Cada script debe tener un propósito claro y único.
No sobrediseñes — ajusta la complejidad al nivel clasificado ({classification.get('complexity_level', 'standard')}).
Responde SOLO con el JSON, sin markdown ni explicaciones."""

    response = await consultar_sabio("gpt54", prompt, timeout=120)
    text = response.get("respuesta", "")
    
    # Extraer JSON
    import re
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"No se pudo extraer la arquitectura del response:\n{text[:500]}")


def validate_architecture(arch: dict, spec: dict) -> list:
    """Valida la arquitectura contra la spec y retorna warnings."""
    warnings = []
    
    if not arch.get("scripts_detail"):
        warnings.append("CRITICAL: No hay scripts definidos")
    
    if not arch.get("entrypoint"):
        warnings.append("WARNING: No hay entrypoint definido")
    
    if not arch.get("execution_flow"):
        warnings.append("WARNING: No hay flujo de ejecución definido")
    
    # Verificar que el entrypoint existe en los scripts
    entrypoint = arch.get("entrypoint", "")
    script_names = [s.get("filename", "") for s in arch.get("scripts_detail", [])]
    if entrypoint and entrypoint not in script_names:
        warnings.append(f"WARNING: Entrypoint '{entrypoint}' no está en la lista de scripts")
    
    # Verificar dependencias circulares
    deps = {s["filename"]: s.get("dependencies", []) for s in arch.get("scripts_detail", [])}
    for script, script_deps in deps.items():
        for dep in script_deps:
            if dep in deps and script in deps.get(dep, []):
                warnings.append(f"WARNING: Dependencia circular entre {script} y {dep}")
    
    return warnings


async def main():
    parser = argparse.ArgumentParser(description="Diseña la arquitectura de una skill")
    parser.add_argument("--spec", required=True, help="Path al skill_spec.yaml")
    parser.add_argument("--classification", required=True, help="Path al classification.yaml")
    parser.add_argument("--dossier", default=None, help="Path al dossier de dominio (opcional)")
    parser.add_argument("--output", required=True, help="Path de salida para architecture.yaml")
    args = parser.parse_args()
    
    # Leer inputs
    with open(args.spec, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    
    with open(args.classification, 'r', encoding='utf-8') as f:
        classification = yaml.safe_load(f)
    
    dossier = ""
    if args.dossier and Path(args.dossier).exists():
        dossier = Path(args.dossier).read_text(encoding="utf-8")
        print(f"📚 Dossier cargado: {len(dossier):,} chars")
    
    print(f"🏗️ Diseñando arquitectura para: {spec.get('name')}")
    print(f"   Nivel: {classification.get('complexity_level')}")
    
    # Diseñar
    architecture = await design_architecture(spec, classification, dossier)
    
    # Validar
    warnings = validate_architecture(architecture, spec)
    if warnings:
        print("⚠️ Warnings de validación:")
        for w in warnings:
            print(f"   {w}")
    
    architecture["_warnings"] = warnings
    architecture["_spec_name"] = spec.get("name")
    architecture["_complexity"] = classification.get("complexity_level")
    
    # Guardar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(architecture, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    scripts_count = len(architecture.get("scripts_detail", []))
    refs_count = len(architecture.get("references_detail", []))
    print(f"✅ Arquitectura diseñada: {scripts_count} scripts, {refs_count} referencias")
    print(f"   Entrypoint: {architecture.get('entrypoint', 'N/A')}")
    print(f"   Líneas estimadas: {architecture.get('estimated_total_lines', 'N/A')}")
    print(f"📁 Guardada en: {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
