#!/usr/bin/env python3.11
"""
generate_scripts.py — Genera el código fuente de los scripts de una skill.

Toma la arquitectura y el dossier de dominio, y usa GPT-5.4 para generar
el código de cada script definido en la arquitectura.

Uso:
    python3.11 generate_scripts.py --spec spec.yaml --architecture arch.yaml \
        --dossier dossier.md --target /path/to/skill/scripts/
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

FACTORY_ROOT = Path(__file__).parent.parent

CODEGEN_SYSTEM = """Eres un programador experto de Python 3.11. Generas scripts para skills de Manus.

REGLAS ESTRICTAS:
1. Código limpio, documentado, con docstrings
2. Manejo de errores robusto (try/except con mensajes claros)
3. Usar argparse para CLI
4. Paths absolutos (no relativos)
5. Imports al inicio del archivo
6. Usar async/await cuando se llaman APIs
7. Usar sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts") si necesita conector_sabios
8. NO usar input() interactivo
9. Encoding UTF-8 explícito en file operations
10. Shebang: #!/usr/bin/env python3.11

Responde SOLO con el código Python completo, sin markdown, sin explicaciones, sin ```."""


async def generate_single_script(
    script_detail: dict, spec: dict, architecture: dict, dossier_excerpt: str, previously_generated: dict
) -> str:
    """Genera el código de un solo script."""

    # Contexto de scripts ya generados (para coherencia)
    prev_context = ""
    if previously_generated:
        prev_context = "\n\nScripts ya generados en esta skill (para coherencia de imports y interfaces):\n"
        for name, code in list(previously_generated.items())[:3]:  # Max 3 para no exceder contexto
            # Solo incluir las primeras 30 líneas de cada uno
            lines = code.split("\n")[:30]
            prev_context += f"\n--- {name} (primeras 30 líneas) ---\n" + "\n".join(lines) + "\n"

    prompt = f"""{CODEGEN_SYSTEM}

## Skill
Nombre: {spec.get("name")}
Dominio: {spec.get("domain")}
Descripción: {spec.get("description")}

## Script a Generar
Archivo: {script_detail.get("filename")}
Propósito: {script_detail.get("purpose")}
Tipo: {script_detail.get("type")}
APIs que usa: {script_detail.get("apis_used", [])}
Inputs: {script_detail.get("inputs", [])}
Outputs: {script_detail.get("outputs", [])}
Dependencias: {script_detail.get("dependencies", [])}
Líneas estimadas: {script_detail.get("estimated_lines", 100)}

## Contexto del Dominio
{dossier_excerpt[:3000] if dossier_excerpt else "No hay dossier disponible."}

## Entrypoint de la skill
{architecture.get("entrypoint", "N/A")}

## Flujo de ejecución
{json.dumps(architecture.get("execution_flow", []), indent=2, ensure_ascii=False)[:2000]}
{prev_context}

Genera el código completo del script. Responde SOLO con código Python."""

    # Usar GPT-5.4 para scripts complejos, Claude para review/validación
    model = "gpt54"
    if script_detail.get("type") == "validator":
        model = "claude"  # Claude es mejor para validación/crítica

    response = await consultar_sabio(model, prompt, timeout=120)
    code = response.get("respuesta", "")

    # Limpiar markdown si lo incluyó
    if code.startswith("```python"):
        code = code[len("```python") :].strip()
    if code.startswith("```"):
        code = code[3:].strip()
    if code.endswith("```"):
        code = code[:-3].strip()

    # Asegurar shebang
    if not code.startswith("#!/"):
        code = "#!/usr/bin/env python3.11\n" + code

    return code


def validate_script(code: str, filename: str) -> list:
    """Validación básica del script generado."""
    issues = []

    if not code.strip():
        issues.append(f"CRITICAL: {filename} está vacío")
        return issues

    if "import" not in code:
        issues.append(f"WARNING: {filename} no tiene imports")

    if '"""' not in code and "'''" not in code:
        issues.append(f"WARNING: {filename} no tiene docstring")

    # Verificar syntax
    try:
        compile(code, filename, "exec")
    except SyntaxError as e:
        issues.append(f"CRITICAL: {filename} tiene error de sintaxis: {e}")

    return issues


async def main():
    parser = argparse.ArgumentParser(description="Genera los scripts de una skill")
    parser.add_argument("--spec", required=True, help="Path al skill_spec.yaml")
    parser.add_argument("--architecture", required=True, help="Path al architecture.yaml")
    parser.add_argument("--dossier", default=None, help="Path al dossier de dominio")
    parser.add_argument("--target", required=True, help="Directorio destino para los scripts")
    parser.add_argument("--only", default=None, help="Generar solo un script específico")
    args = parser.parse_args()

    with open(args.spec, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    with open(args.architecture, "r", encoding="utf-8") as f:
        architecture = yaml.safe_load(f)

    dossier = ""
    if args.dossier and Path(args.dossier).exists():
        dossier = Path(args.dossier).read_text(encoding="utf-8")

    target = Path(args.target)
    target.mkdir(parents=True, exist_ok=True)

    scripts = architecture.get("scripts_detail", [])
    if args.only:
        scripts = [s for s in scripts if s.get("filename") == args.only]

    # Ordenar por prioridad (P0 primero)
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    scripts.sort(key=lambda s: priority_order.get(s.get("priority", "P1"), 1))

    print(f"🔨 Generando {len(scripts)} scripts para: {spec.get('name')}")

    generated = {}
    errors = []

    for i, script_detail in enumerate(scripts):
        filename = script_detail.get("filename", f"script_{i}.py")
        print(f"\n  [{i + 1}/{len(scripts)}] Generando {filename}...")

        try:
            code = await generate_single_script(script_detail, spec, architecture, dossier, generated)

            # Validar
            issues = validate_script(code, filename)
            critical = [i for i in issues if "CRITICAL" in i]

            if critical:
                print(f"    ❌ Errores críticos: {critical}")
                errors.append({"file": filename, "issues": critical})
                # Intentar regenerar una vez
                print("    🔄 Reintentando...")
                code = await generate_single_script(script_detail, spec, architecture, dossier, generated)
                issues = validate_script(code, filename)
                critical = [i for i in issues if "CRITICAL" in i]
                if critical:
                    print(f"    ❌ Falló de nuevo: {critical}")
                    continue

            # Guardar
            script_path = target / filename
            script_path.write_text(code, encoding="utf-8")
            generated[filename] = code

            lines = len(code.split("\n"))
            warnings = [i for i in issues if "WARNING" in i]
            status = "✅" if not warnings else "⚠️"
            print(f"    {status} {filename}: {lines} líneas")
            if warnings:
                for w in warnings:
                    print(f"       {w}")

        except Exception as e:
            print(f"    ❌ Error generando {filename}: {e}")
            errors.append({"file": filename, "error": str(e)})

    print(f"\n{'=' * 50}")
    print(f"✅ Generados: {len(generated)}/{len(scripts)} scripts")
    if errors:
        print(f"❌ Errores: {len(errors)}")
        for e in errors:
            print(f"   {e}")
    print(f"📁 Destino: {target}")


if __name__ == "__main__":
    asyncio.run(main())
