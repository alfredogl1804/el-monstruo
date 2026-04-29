#!/usr/bin/env python3.11
"""
build_skill.py — Crea la estructura de directorios de una skill.

Lee la arquitectura y crea todos los directorios necesarios.
NO genera contenido — solo la estructura vacía.

Uso:
    python3.11 build_skill.py --architecture arch.yaml --target /home/ubuntu/skills/my-skill
"""

import argparse, os, yaml
from pathlib import Path


def build_structure(architecture: dict, target_dir: Path) -> dict:
    """Crea la estructura de directorios de la skill."""
    
    created = {"dirs": [], "placeholders": []}
    
    # Crear directorio principal
    target_dir.mkdir(parents=True, exist_ok=True)
    created["dirs"].append(str(target_dir))
    
    # Directorios estándar
    dir_structure = architecture.get("directory_structure", {})
    
    # Scripts
    if dir_structure.get("scripts"):
        scripts_dir = target_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        created["dirs"].append(str(scripts_dir))
    
    # References
    if dir_structure.get("references"):
        refs_dir = target_dir / "references"
        refs_dir.mkdir(exist_ok=True)
        created["dirs"].append(str(refs_dir))
    
    # Templates
    if dir_structure.get("templates"):
        templates_dir = target_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        created["dirs"].append(str(templates_dir))
    
    # Config
    if dir_structure.get("config"):
        config_dir = target_dir / "config"
        config_dir.mkdir(exist_ok=True)
        created["dirs"].append(str(config_dir))
    
    # Data (para telemetría/persistencia)
    data_dir = target_dir / "data"
    data_dir.mkdir(exist_ok=True)
    created["dirs"].append(str(data_dir))
    
    # Crear archivos placeholder para scripts
    for script in architecture.get("scripts_detail", []):
        filename = script.get("filename", "")
        if filename:
            script_path = target_dir / "scripts" / filename
            if not script_path.exists():
                purpose = script.get("purpose", "TODO")
                script_path.write_text(
                    f'#!/usr/bin/env python3.11\n"""\n{filename} — {purpose}\n\nTODO: Implementar\n"""\n',
                    encoding="utf-8"
                )
                created["placeholders"].append(str(script_path))
    
    # Crear archivos placeholder para referencias
    for ref in architecture.get("references_detail", []):
        filename = ref.get("filename", "")
        if filename:
            ref_path = target_dir / "references" / filename
            if not ref_path.exists():
                purpose = ref.get("purpose", "TODO")
                ref_path.write_text(
                    f"# {filename}\n\n{purpose}\n\nTODO: Completar contenido\n",
                    encoding="utf-8"
                )
                created["placeholders"].append(str(ref_path))
    
    return created


def main():
    parser = argparse.ArgumentParser(description="Crea la estructura de directorios de una skill")
    parser.add_argument("--architecture", required=True, help="Path al architecture.yaml")
    parser.add_argument("--target", required=True, help="Directorio destino de la skill")
    args = parser.parse_args()
    
    with open(args.architecture, 'r', encoding='utf-8') as f:
        architecture = yaml.safe_load(f)
    
    target = Path(args.target)
    skill_name = architecture.get("skill_name", target.name)
    
    print(f"🏗️ Creando estructura para: {skill_name}")
    print(f"   Destino: {target}")
    
    result = build_structure(architecture, target)
    
    print(f"✅ Estructura creada:")
    print(f"   Directorios: {len(result['dirs'])}")
    print(f"   Placeholders: {len(result['placeholders'])}")
    
    for d in result["dirs"]:
        print(f"   📁 {d}")
    for p in result["placeholders"]:
        print(f"   📄 {p}")

if __name__ == "__main__":
    main()
