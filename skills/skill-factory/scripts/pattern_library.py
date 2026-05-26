#!/usr/bin/env python3.11
"""
pattern_library.py — Biblioteca de patrones reutilizables.

Extrae y almacena patrones exitosos de skills creadas para reutilizar
en futuras creaciones. Aprende de cada skill que pasa el quality gate.

Uso:
    python3.11 pattern_library.py --extract --skill-dir /path/to/skill --score 85
    python3.11 pattern_library.py --search --domain finance --capability api_integration
    python3.11 pattern_library.py --list
"""

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

import yaml

FACTORY_ROOT = Path(__file__).parent.parent
PATTERNS_FILE = FACTORY_ROOT / "data" / "pattern_library.jsonl"


def extract_patterns(skill_dir: Path, score: float) -> list:
    """Extrae patrones reutilizables de una skill exitosa."""
    patterns = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return patterns

    content = skill_md.read_text(encoding="utf-8")

    # Extraer frontmatter
    parts = content.split("---", 2)
    fm = {}
    if len(parts) >= 3:
        try:
            fm = yaml.safe_load(parts[1]) or {}
        except:
            pass

    skill_name = fm.get("name", skill_dir.name)

    # Patrón: estructura de directorios
    dirs = [str(d.relative_to(skill_dir)) for d in skill_dir.rglob("*") if d.is_dir()]
    if dirs:
        patterns.append(
            {
                "type": "directory_structure",
                "source_skill": skill_name,
                "source_score": score,
                "data": dirs,
                "description": f"Estructura de directorios de {skill_name}",
            }
        )

    # Patrón: scripts y sus propósitos
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        script_patterns = []
        for script in scripts_dir.glob("*.py"):
            code = script.read_text(encoding="utf-8")
            # Extraer docstring
            docstring = ""
            if '"""' in code:
                start = code.index('"""') + 3
                end = code.index('"""', start)
                docstring = code[start:end].strip()

            script_patterns.append(
                {
                    "filename": script.name,
                    "docstring": docstring[:200],
                    "lines": len(code.split("\n")),
                    "has_argparse": "argparse" in code,
                    "has_async": "async " in code,
                    "uses_apis": any(x in code for x in ["consultar_sabio", "aiohttp", "requests"]),
                }
            )

        if script_patterns:
            patterns.append(
                {
                    "type": "script_inventory",
                    "source_skill": skill_name,
                    "source_score": score,
                    "data": script_patterns,
                    "description": f"Inventario de scripts de {skill_name}",
                }
            )

    # Patrón: imports comunes
    all_imports = set()
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            code = script.read_text(encoding="utf-8")
            for line in code.split("\n"):
                line = line.strip()
                if line.startswith("import ") or line.startswith("from "):
                    all_imports.add(line)

    if all_imports:
        patterns.append(
            {
                "type": "common_imports",
                "source_skill": skill_name,
                "source_score": score,
                "data": sorted(all_imports),
                "description": f"Imports comunes de {skill_name}",
            }
        )

    # Agregar metadata
    for p in patterns:
        p["extracted_at"] = datetime.now().isoformat()
        p["fingerprint"] = hashlib.sha256(
            json.dumps(p["data"], sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()[:12]

    return patterns


def save_patterns(patterns: list):
    """Guarda patrones en la biblioteca."""
    PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PATTERNS_FILE, "a", encoding="utf-8") as f:
        for p in patterns:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")


def load_patterns() -> list:
    """Carga todos los patrones."""
    if not PATTERNS_FILE.exists():
        return []

    patterns = []
    with open(PATTERNS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    patterns.append(json.loads(line))
                except:
                    pass
    return patterns


def search_patterns(domain: str = None, capability: str = None, pattern_type: str = None) -> list:
    """Busca patrones relevantes."""
    patterns = load_patterns()

    results = []
    for p in patterns:
        match = True
        if pattern_type and p.get("type") != pattern_type:
            match = False
        if domain and domain.lower() not in json.dumps(p, ensure_ascii=False).lower():
            match = False
        if capability and capability.lower() not in json.dumps(p, ensure_ascii=False).lower():
            match = False

        if match:
            results.append(p)

    # Ordenar por score de la skill fuente
    results.sort(key=lambda x: x.get("source_score", 0), reverse=True)
    return results


def main():
    parser = argparse.ArgumentParser(description="Biblioteca de patrones reutilizables")
    parser.add_argument("--extract", action="store_true", help="Extraer patrones de una skill")
    parser.add_argument("--search", action="store_true", help="Buscar patrones")
    parser.add_argument("--list", action="store_true", help="Listar todos los patrones")
    parser.add_argument("--skill-dir", default=None, help="Directorio de la skill (para extract)")
    parser.add_argument("--score", type=float, default=0, help="Score de la skill (para extract)")
    parser.add_argument("--domain", default=None, help="Dominio a buscar")
    parser.add_argument("--capability", default=None, help="Capacidad a buscar")
    args = parser.parse_args()

    if args.extract:
        if not args.skill_dir:
            print("❌ --skill-dir requerido para extract")
            return

        skill_dir = Path(args.skill_dir)
        print(f"📚 Extrayendo patrones de: {skill_dir.name}")
        patterns = extract_patterns(skill_dir, args.score)
        save_patterns(patterns)
        print(f"  ✅ {len(patterns)} patrones extraídos y guardados")
        for p in patterns:
            print(f"    [{p['type']}] {p['description']}")

    elif args.search:
        print("🔍 Buscando patrones...")
        results = search_patterns(args.domain, args.capability)
        print(f"  {len(results)} patrones encontrados")
        for r in results:
            print(f"  [{r['type']}] {r.get('description', 'N/A')} (score: {r.get('source_score', '?')})")

    elif args.list:
        patterns = load_patterns()
        print(f"📚 Biblioteca de patrones: {len(patterns)} patrones")
        types = {}
        for p in patterns:
            t = p.get("type", "unknown")
            types[t] = types.get(t, 0) + 1
        for t, count in sorted(types.items()):
            print(f"  {t}: {count}")


if __name__ == "__main__":
    main()
