#!/usr/bin/env python3.11
"""
validate_quality.py — Evaluación de calidad profunda de una skill usando IA como juez.

Usa Claude como juez independiente para evaluar la calidad de la skill
en 8 dimensiones definidas en quality-rubric.md.

Uso:
    python3.11 validate_quality.py --skill-dir /path/to/skill --output quality.yaml
"""

import argparse, asyncio, json, os, sys, yaml
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

FACTORY_ROOT = Path(__file__).parent.parent


def collect_skill_content(skill_dir: Path) -> str:
    """Recopila el contenido de la skill para evaluación."""
    content_parts = []
    
    # SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content_parts.append(f"=== SKILL.md ===\n{skill_md.read_text(encoding='utf-8')}")
    
    # Scripts (primeras 50 líneas de cada uno)
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for script in sorted(scripts_dir.glob("*.py")):
            code = script.read_text(encoding="utf-8")
            lines = code.split("\n")[:50]
            content_parts.append(f"=== scripts/{script.name} ({len(code.split(chr(10)))} líneas total) ===\n" + "\n".join(lines))
    
    # References (primeras 30 líneas de cada uno)
    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        for ref in sorted(refs_dir.glob("*.md")):
            text = ref.read_text(encoding="utf-8")
            lines = text.split("\n")[:30]
            content_parts.append(f"=== references/{ref.name} ===\n" + "\n".join(lines))
    
    return "\n\n".join(content_parts)


async def evaluate_quality(skill_content: str, spec: dict = None) -> dict:
    """Usa Claude como juez para evaluar la calidad de la skill."""
    
    spec_context = ""
    if spec:
        spec_context = f"""
Especificación original de la skill:
- Nombre: {spec.get('name')}
- Dominio: {spec.get('domain')}
- Descripción: {spec.get('description')}
- Capacidades: {spec.get('core_capabilities', [])}
"""
    
    prompt = f"""Eres un evaluador experto de skills de IA. Evalúa esta skill en 8 dimensiones.

{spec_context}

## Contenido de la Skill
{skill_content[:30000]}

---

Evalúa en estas 8 dimensiones (score 0-100 cada una):

1. **structure**: Frontmatter válido, directorios correctos, sin archivos innecesarios
2. **completeness**: Todos los scripts y referencias existen y están completos
3. **executability**: Scripts ejecutan sin errores, dependencias documentadas
4. **documentation**: SKILL.md claro, ejemplos de uso, credenciales documentadas
5. **robustness**: Manejo de errores, timeouts, fallbacks
6. **conciseness**: Sin repetición, tokens justificados, progressive disclosure
7. **domain_fit**: Terminología correcta, mejores prácticas del área
8. **improvability**: Logging, configuración externalizada, puntos de extensión

Responde SOLO con JSON:
{{
  "dimensions": {{
    "structure": {{"score": 85, "reasoning": "..."}},
    "completeness": {{"score": 80, "reasoning": "..."}},
    "executability": {{"score": 75, "reasoning": "..."}},
    "documentation": {{"score": 90, "reasoning": "..."}},
    "robustness": {{"score": 70, "reasoning": "..."}},
    "conciseness": {{"score": 85, "reasoning": "..."}},
    "domain_fit": {{"score": 80, "reasoning": "..."}},
    "improvability": {{"score": 75, "reasoning": "..."}}
  }},
  "global_score": 80,
  "grade": "Buena",
  "top_strengths": ["fortaleza 1", "fortaleza 2"],
  "top_weaknesses": ["debilidad 1", "debilidad 2"],
  "critical_fixes": ["fix urgente si hay"],
  "improvement_suggestions": ["sugerencia 1", "sugerencia 2", "sugerencia 3"]
}}"""

    # Usar Claude como juez (independiente del generador GPT-5.4)
    response = await consultar_sabio("claude", prompt, timeout=90)
    text = response.get("respuesta", "")
    
    # Extraer JSON
    import re
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    # Fallback
    return {
        "dimensions": {},
        "global_score": 0,
        "grade": "Error",
        "top_strengths": [],
        "top_weaknesses": ["No se pudo evaluar"],
        "critical_fixes": [],
        "improvement_suggestions": [],
        "_raw_response": text[:500]
    }


async def main():
    parser = argparse.ArgumentParser(description="Evalúa la calidad de una skill")
    parser.add_argument("--skill-dir", required=True, help="Directorio de la skill")
    parser.add_argument("--spec", default=None, help="Path al skill_spec.yaml (opcional)")
    parser.add_argument("--output", required=True, help="Path de salida para quality.yaml")
    args = parser.parse_args()
    
    skill_dir = Path(args.skill_dir)
    
    if not skill_dir.exists():
        print(f"❌ Directorio no existe: {skill_dir}")
        sys.exit(1)
    
    spec = None
    if args.spec and Path(args.spec).exists():
        with open(args.spec, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
    
    print(f"🏆 Evaluando calidad de: {skill_dir.name}")
    
    # Recopilar contenido
    print("  📦 Recopilando contenido de la skill...")
    content = collect_skill_content(skill_dir)
    print(f"  📄 {len(content):,} chars recopilados")
    
    # Evaluar
    print("  🤖 Claude evaluando calidad (8 dimensiones)...")
    evaluation = await evaluate_quality(content, spec)
    
    # Guardar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(evaluation, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Imprimir resultados
    print(f"\n{'='*50}")
    print(f"  Score Global: {evaluation.get('global_score', 'N/A')}/100")
    print(f"  Grado: {evaluation.get('grade', 'N/A')}")
    
    dims = evaluation.get("dimensions", {})
    if dims:
        print(f"\n  Dimensiones:")
        for dim, data in dims.items():
            score = data.get("score", "?") if isinstance(data, dict) else data
            print(f"    {dim}: {score}/100")
    
    strengths = evaluation.get("top_strengths", [])
    if strengths:
        print(f"\n  Fortalezas:")
        for s in strengths:
            print(f"    ✅ {s}")
    
    weaknesses = evaluation.get("top_weaknesses", [])
    if weaknesses:
        print(f"\n  Debilidades:")
        for w in weaknesses:
            print(f"    ⚠️ {w}")
    
    fixes = evaluation.get("critical_fixes", [])
    if fixes:
        print(f"\n  Fixes Críticos:")
        for fix in fixes:
            print(f"    ❌ {fix}")
    
    print(f"\n📁 Evaluación guardada en: {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
