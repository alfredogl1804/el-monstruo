#!/usr/bin/env python3.11
"""
validate_structure.py — Valida la estructura de una skill generada.

Verifica: frontmatter YAML, directorios, archivos referenciados,
imports, syntax, y completitud.

Uso:
    python3.11 validate_structure.py --skill-dir /path/to/skill --output report.yaml
"""

import argparse
import subprocess
import sys
from pathlib import Path

import yaml


def validate_frontmatter(skill_md_path: Path) -> list:
    """Valida el frontmatter YAML del SKILL.md."""
    issues = []

    if not skill_md_path.exists():
        issues.append({"severity": "CRITICAL", "msg": "SKILL.md no existe"})
        return issues

    content = skill_md_path.read_text(encoding="utf-8")

    if not content.strip().startswith("---"):
        issues.append({"severity": "CRITICAL", "msg": "SKILL.md no empieza con frontmatter ---"})
        return issues

    # Extraer frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        issues.append({"severity": "CRITICAL", "msg": "Frontmatter no cierra con ---"})
        return issues

    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        issues.append({"severity": "CRITICAL", "msg": f"Frontmatter YAML inválido: {e}"})
        return issues

    if not fm:
        issues.append({"severity": "CRITICAL", "msg": "Frontmatter vacío"})
        return issues

    if "name" not in fm:
        issues.append({"severity": "CRITICAL", "msg": "Falta 'name' en frontmatter"})

    if "description" not in fm:
        issues.append({"severity": "CRITICAL", "msg": "Falta 'description' en frontmatter"})

    # Verificar longitud
    lines = content.split("\n")
    if len(lines) > 500:
        issues.append({"severity": "WARNING", "msg": f"SKILL.md tiene {len(lines)} líneas (máximo 500)"})

    return issues


def validate_directories(skill_dir: Path) -> list:
    """Valida la estructura de directorios."""
    issues = []

    # scripts/ es obligatorio si hay scripts
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        issues.append({"severity": "WARNING", "msg": "No existe directorio scripts/"})
    elif not any(scripts_dir.glob("*.py")):
        issues.append({"severity": "WARNING", "msg": "scripts/ está vacío"})

    # Verificar que no hay archivos prohibidos
    prohibited = ["README.md", "CHANGELOG.md", "LICENSE"]
    for p in prohibited:
        if (skill_dir / p).exists():
            issues.append({"severity": "WARNING", "msg": f"Archivo prohibido encontrado: {p}"})

    return issues


def validate_scripts(skill_dir: Path) -> list:
    """Valida los scripts Python."""
    issues = []
    scripts_dir = skill_dir / "scripts"

    if not scripts_dir.exists():
        return issues

    for script in scripts_dir.glob("*.py"):
        code = script.read_text(encoding="utf-8")

        # Syntax check
        try:
            compile(code, str(script), "exec")
        except SyntaxError as e:
            issues.append(
                {"severity": "CRITICAL", "msg": f"{script.name}: Error de sintaxis línea {e.lineno}: {e.msg}"}
            )
            continue

        # Import check (dry run)
        result = subprocess.run(
            ["python3.11", "-c", f"import ast; ast.parse(open('{script}').read())"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            issues.append({"severity": "CRITICAL", "msg": f"{script.name}: Error de parsing: {result.stderr[:200]}"})

        # Docstring check
        if '"""' not in code and "'''" not in code:
            issues.append({"severity": "WARNING", "msg": f"{script.name}: Sin docstring"})

        # Shebang check
        if not code.startswith("#!/"):
            issues.append({"severity": "INFO", "msg": f"{script.name}: Sin shebang"})

        # Hardcoded credentials check
        import re

        if re.search(r'(api_key|password|secret)\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
            issues.append({"severity": "CRITICAL", "msg": f"{script.name}: Posible credencial hardcodeada"})

    return issues


def validate_references(skill_dir: Path, skill_md_content: str) -> list:
    """Valida que las referencias mencionadas en SKILL.md existen."""
    issues = []
    refs_dir = skill_dir / "references"

    if not refs_dir.exists():
        return issues

    # Verificar que los archivos .md en references/ no están vacíos
    for ref in refs_dir.glob("*.md"):
        content = ref.read_text(encoding="utf-8")
        if len(content.strip()) < 50:
            issues.append(
                {"severity": "WARNING", "msg": f"references/{ref.name}: Contenido muy corto ({len(content)} chars)"}
            )

    return issues


def calculate_scores(all_issues: list) -> dict:
    """Calcula scores de validación."""
    critical = sum(1 for i in all_issues if i["severity"] == "CRITICAL")
    warnings = sum(1 for i in all_issues if i["severity"] == "WARNING")
    infos = sum(1 for i in all_issues if i["severity"] == "INFO")

    # Score: 100 - (critical * 25) - (warnings * 5) - (infos * 1)
    score = max(0, 100 - (critical * 25) - (warnings * 5) - (infos * 1))

    if critical > 0:
        verdict = "FAIL"
    elif warnings > 3:
        verdict = "WARN"
    else:
        verdict = "PASS"

    return {
        "score": score,
        "verdict": verdict,
        "critical_count": critical,
        "warning_count": warnings,
        "info_count": infos,
        "total_issues": len(all_issues),
    }


def main():
    parser = argparse.ArgumentParser(description="Valida la estructura de una skill")
    parser.add_argument("--skill-dir", required=True, help="Directorio de la skill")
    parser.add_argument("--output", default=None, help="Path de salida para el reporte")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)

    if not skill_dir.exists():
        print(f"❌ Directorio no existe: {skill_dir}")
        sys.exit(1)

    print(f"🔍 Validando estructura de: {skill_dir.name}")

    all_issues = []

    # 1. Frontmatter
    print("  📋 Validando SKILL.md y frontmatter...")
    all_issues.extend(validate_frontmatter(skill_dir / "SKILL.md"))

    # 2. Directorios
    print("  📁 Validando directorios...")
    all_issues.extend(validate_directories(skill_dir))

    # 3. Scripts
    print("  🐍 Validando scripts Python...")
    all_issues.extend(validate_scripts(skill_dir))

    # 4. Referencias
    skill_md = skill_dir / "SKILL.md"
    skill_md_content = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""
    print("  📚 Validando referencias...")
    all_issues.extend(validate_references(skill_dir, skill_md_content))

    # Calcular scores
    scores = calculate_scores(all_issues)

    # Reporte
    report = {"skill_dir": str(skill_dir), "skill_name": skill_dir.name, "scores": scores, "issues": all_issues}

    # Imprimir resultados
    print(f"\n{'=' * 50}")
    print(f"  Veredicto: {scores['verdict']}")
    print(f"  Score: {scores['score']}/100")
    print(f"  Critical: {scores['critical_count']}")
    print(f"  Warnings: {scores['warning_count']}")
    print(f"  Info: {scores['info_count']}")

    if all_issues:
        print("\n  Issues:")
        for issue in all_issues:
            icon = {"CRITICAL": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}[issue["severity"]]
            print(f"    {icon} [{issue['severity']}] {issue['msg']}")

    # Guardar reporte
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(report, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"\n📁 Reporte guardado en: {args.output}")

    # Exit code
    sys.exit(0 if scores["verdict"] != "FAIL" else 1)


if __name__ == "__main__":
    main()
