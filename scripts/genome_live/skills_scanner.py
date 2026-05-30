#!/usr/bin/env python3
"""
skills_scanner.py — Scanner de Skills del ecosistema Monstruo.

Escanea el directorio skills/ del repo y extrae metadata de cada SKILL.md:
  - name, version, status, description, owner, last_reviewed
  - Tamaño total del skill (archivos, líneas)

Verificación binaria:
  - Cuenta de skills con SKILL.md válido vs total de directorios en skills/

Output: _genome_out/skills.json

Autor: Manus — Sprint 91.11
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = ROOT / "skills"
OUT_DIR = ROOT / "_genome_out"


def count_lines(directory: Path) -> int:
    """Cuenta líneas totales de archivos de texto en un directorio."""
    total = 0
    for f in directory.rglob("*"):
        if f.is_file() and f.suffix in (".md", ".py", ".sh", ".yaml", ".yml", ".json", ".txt", ".toml"):
            try:
                total += len(f.read_text(errors="ignore").splitlines())
            except Exception:
                pass
    return total


def parse_skill_md(skill_dir: Path) -> dict[str, Any] | None:
    """Parsea SKILL.md y extrae metadata del frontmatter YAML."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None

    try:
        content = skill_md.read_text(errors="ignore")
    except Exception:
        return None

    # Extraer frontmatter YAML (entre --- y ---)
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    metadata: dict[str, Any] = {}

    if fm_match:
        fm_text = fm_match.group(1)
        # Parseo simple sin pyyaml
        for line in fm_text.splitlines():
            if ":" in line and not line.strip().startswith("#"):
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key in ("name", "description", "version", "status", "owner", "last_reviewed"):
                    metadata[key] = val
                elif key == "metadata":
                    continue  # nested block, handle below

        # Try nested metadata block
        nested_match = re.search(r"metadata:\s*\n((?:\s+.+\n)+)", fm_text)
        if nested_match:
            for line in nested_match.group(1).splitlines():
                if ":" in line:
                    key, _, val = line.strip().partition(":")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key in ("version", "status", "owner", "last_reviewed"):
                        metadata[key] = val

    lines = count_lines(skill_dir)
    files_count = sum(1 for f in skill_dir.rglob("*") if f.is_file())

    return {
        "name": metadata.get("name", skill_dir.name),
        "version": metadata.get("version", "unknown"),
        "status": metadata.get("status", "unknown"),
        "description": (metadata.get("description", ""))[:200],
        "owner": metadata.get("owner", "unknown"),
        "last_reviewed": metadata.get("last_reviewed", "unknown"),
        "lines": lines,
        "files": files_count,
    }


def scan() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()

    if not SKILLS_DIR.exists():
        return {
            "scanner": "skills",
            "version": 1,
            "started_at": started,
            "finished_at": started,
            "error": "skills/ directory not found",
            "coverage_match": False,
            "skills": [],
        }

    # Listar todos los directorios en skills/
    all_dirs = sorted([d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")])
    expected_total = len(all_dirs)

    skills: list[dict[str, Any]] = []
    for skill_dir in all_dirs:
        parsed = parse_skill_md(skill_dir)
        if parsed:
            skills.append(parsed)
        else:
            skills.append({
                "name": skill_dir.name,
                "version": "unknown",
                "status": "NO_SKILL_MD",
                "description": "",
                "owner": "unknown",
                "last_reviewed": "unknown",
                "lines": count_lines(skill_dir),
                "files": sum(1 for f in skill_dir.rglob("*") if f.is_file()),
            })

    finished = datetime.now(timezone.utc).isoformat()
    got_total = len(skills)
    coverage_match = got_total == expected_total and expected_total > 0

    # Aggregate stats
    total_lines = sum(s.get("lines", 0) for s in skills)
    active_count = sum(1 for s in skills if s.get("status", "").upper() in ("ACTUAL", "ACTIVE", "PRODUCTION"))

    return {
        "scanner": "skills",
        "version": 1,
        "started_at": started,
        "finished_at": finished,
        "expected_total": expected_total,
        "got_total": got_total,
        "coverage_match": coverage_match,
        "total_lines": total_lines,
        "active_count": active_count,
        "skills": skills,
    }


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    out_file = OUT_DIR / "skills.json"

    result = scan()
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print("\nSKILLS SCAN RESUMEN")
    print(f"  expected: {result.get('expected_total', 0)}")
    print(f"  got     : {result.get('got_total', 0)}")
    print(f"  active  : {result.get('active_count', 0)}")
    print(f"  lines   : {result.get('total_lines', 0):,}")
    print(f"  match   : {result['coverage_match']}")
    print(f"  output  : {out_file}")

    return 0 if result["coverage_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
