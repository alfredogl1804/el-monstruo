#!/usr/bin/env python3.11
"""
record_outcome.py — Registra el resultado de cada skill creada.

Guarda métricas, scores, errores y metadata en un historial JSONL
para análisis posterior y mejora perpetua del factory.

Uso:
    python3.11 record_outcome.py --workspace /tmp/skill-factory/my-skill/ --skill-dir /home/ubuntu/skills/my-skill/
"""

import argparse, json, hashlib, yaml, time
from pathlib import Path
from datetime import datetime

FACTORY_ROOT = Path(__file__).parent.parent
HISTORY_FILE = FACTORY_ROOT / "data" / "creation_history.jsonl"
STATS_FILE = FACTORY_ROOT / "data" / "factory_stats.yaml"


def collect_outcome(workspace: Path, skill_dir: Path) -> dict:
    """Recopila el resultado completo de una creación."""
    
    outcome = {
        "timestamp": datetime.now().isoformat(),
        "skill_name": skill_dir.name,
        "skill_dir": str(skill_dir),
        "workspace": str(workspace)
    }
    
    # Spec
    spec_path = workspace / "spec.yaml"
    if spec_path.exists():
        with open(spec_path, 'r') as f:
            spec = yaml.safe_load(f)
        outcome["domain"] = spec.get("domain", "unknown")
        outcome["complexity_target"] = spec.get("complexity_hint", "unknown")
        outcome["regulated"] = spec.get("regulated", False)
    
    # Classification
    class_path = workspace / "classification.yaml"
    if class_path.exists():
        with open(class_path, 'r') as f:
            classification = yaml.safe_load(f)
        outcome["complexity_level"] = classification.get("complexity_level", "unknown")
        outcome["complexity_score"] = classification.get("complexity_score", 0)
    
    # Final score
    score_path = workspace / "final_score.yaml"
    if score_path.exists():
        with open(score_path, 'r') as f:
            final = yaml.safe_load(f)
        outcome["final_score"] = final.get("final_score", 0)
        outcome["verdict"] = final.get("verdict", "unknown")
        outcome["deliverable"] = final.get("deliverable", False)
        outcome["structure_score"] = final.get("breakdown", {}).get("structure_score", 0)
        outcome["quality_score"] = final.get("breakdown", {}).get("quality_score", 0)
    
    # Pipeline log
    log_path = workspace / "pipeline_log.txt"
    if log_path.exists():
        log = log_path.read_text(encoding="utf-8")
        lines = log.strip().split("\n")
        outcome["pipeline_steps"] = len(lines)
        # Extraer tiempo total del último log
        if lines:
            last = lines[-1]
            try:
                elapsed = float(last.split("]")[0].strip("[").strip().rstrip("s"))
                outcome["elapsed_seconds"] = elapsed
            except:
                pass
    
    # Contar archivos generados
    if skill_dir.exists():
        scripts = list((skill_dir / "scripts").glob("*.py")) if (skill_dir / "scripts").exists() else []
        refs = list((skill_dir / "references").glob("*.md")) if (skill_dir / "references").exists() else []
        outcome["scripts_count"] = len(scripts)
        outcome["references_count"] = len(refs)
        outcome["total_lines"] = sum(
            len(f.read_text(encoding="utf-8").split("\n")) for f in scripts
        ) if scripts else 0
    
    # Fingerprint
    content = json.dumps(outcome, sort_keys=True, ensure_ascii=False)
    outcome["fingerprint"] = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    return outcome


def append_to_history(outcome: dict):
    """Agrega el resultado al historial JSONL."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(outcome, ensure_ascii=False) + "\n")


def update_stats():
    """Actualiza las estadísticas globales del factory."""
    if not HISTORY_FILE.exists():
        return
    
    entries = []
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    
    if not entries:
        return
    
    scores = [e.get("final_score", 0) for e in entries if e.get("final_score")]
    times = [e.get("elapsed_seconds", 0) for e in entries if e.get("elapsed_seconds")]
    
    stats = {
        "total_skills_created": len(entries),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "min_score": min(scores) if scores else 0,
        "avg_time_seconds": round(sum(times) / len(times), 1) if times else 0,
        "deliverable_rate": round(
            sum(1 for e in entries if e.get("deliverable")) / len(entries) * 100, 1
        ),
        "domains": list(set(e.get("domain", "unknown") for e in entries)),
        "complexity_distribution": {},
        "last_updated": datetime.now().isoformat()
    }
    
    # Distribución de complejidad
    for e in entries:
        level = e.get("complexity_level", "unknown")
        stats["complexity_distribution"][level] = stats["complexity_distribution"].get(level, 0) + 1
    
    STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(stats, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def main():
    parser = argparse.ArgumentParser(description="Registra el resultado de una creación de skill")
    parser.add_argument("--workspace", required=True, help="Directorio workspace de la creación")
    parser.add_argument("--skill-dir", required=True, help="Directorio final de la skill")
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    skill_dir = Path(args.skill_dir)
    
    print(f"📊 Registrando resultado para: {skill_dir.name}")
    
    outcome = collect_outcome(workspace, skill_dir)
    append_to_history(outcome)
    update_stats()
    
    print(f"  Score: {outcome.get('final_score', 'N/A')}/100")
    print(f"  Veredicto: {outcome.get('verdict', 'N/A')}")
    print(f"  Entregable: {outcome.get('deliverable', 'N/A')}")
    print(f"  Fingerprint: {outcome.get('fingerprint', 'N/A')}")
    print(f"  Historial: {HISTORY_FILE}")

if __name__ == "__main__":
    main()
