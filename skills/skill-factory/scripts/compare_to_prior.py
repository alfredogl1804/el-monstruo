#!/usr/bin/env python3.11
"""
compare_to_prior.py — Compara skills nuevas con versiones anteriores o similares.

Analiza el historial para encontrar skills del mismo dominio o tipo,
y compara métricas para detectar mejoras o regresiones.

Uso:
    python3.11 compare_to_prior.py --skill-name my-skill --domain finance
"""

import argparse, json, yaml
from pathlib import Path

FACTORY_ROOT = Path(__file__).parent.parent
HISTORY_FILE = FACTORY_ROOT / "data" / "creation_history.jsonl"


def load_history() -> list:
    """Carga el historial de creaciones."""
    if not HISTORY_FILE.exists():
        return []
    
    entries = []
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    return entries


def find_similar(entries: list, skill_name: str, domain: str) -> list:
    """Encuentra skills similares en el historial."""
    similar = []
    
    for e in entries:
        # Mismo nombre (versiones anteriores)
        if e.get("skill_name") == skill_name:
            similar.append({**e, "match_type": "same_name"})
        # Mismo dominio
        elif e.get("domain") == domain:
            similar.append({**e, "match_type": "same_domain"})
    
    return sorted(similar, key=lambda x: x.get("timestamp", ""), reverse=True)


def compare(current: dict, prior: dict) -> dict:
    """Compara dos skills."""
    comparison = {
        "current": current.get("skill_name", "unknown"),
        "prior": prior.get("skill_name", "unknown"),
        "match_type": prior.get("match_type", "unknown"),
        "deltas": {}
    }
    
    metrics = ["final_score", "structure_score", "quality_score", "elapsed_seconds",
               "scripts_count", "total_lines"]
    
    for metric in metrics:
        curr_val = current.get(metric)
        prior_val = prior.get(metric)
        
        if curr_val is not None and prior_val is not None:
            delta = curr_val - prior_val
            pct = round(delta / prior_val * 100, 1) if prior_val != 0 else 0
            comparison["deltas"][metric] = {
                "current": curr_val,
                "prior": prior_val,
                "delta": round(delta, 1),
                "pct_change": pct,
                "improved": delta > 0 if metric in ("final_score", "structure_score", "quality_score") else delta < 0
            }
    
    # Veredicto de comparación
    score_delta = comparison["deltas"].get("final_score", {}).get("delta", 0)
    if score_delta > 5:
        comparison["trend"] = "IMPROVING"
    elif score_delta < -5:
        comparison["trend"] = "REGRESSING"
    else:
        comparison["trend"] = "STABLE"
    
    return comparison


def main():
    parser = argparse.ArgumentParser(description="Compara skills con versiones anteriores")
    parser.add_argument("--skill-name", required=True, help="Nombre de la skill actual")
    parser.add_argument("--domain", default=None, help="Dominio para buscar similares")
    parser.add_argument("--output", default=None, help="Path de salida para comparación")
    args = parser.parse_args()
    
    entries = load_history()
    
    if not entries:
        print("ℹ️ No hay historial previo para comparar")
        return
    
    # La última entrada es la skill actual
    current = None
    for e in reversed(entries):
        if e.get("skill_name") == args.skill_name:
            current = e
            break
    
    if not current:
        print(f"ℹ️ No se encontró {args.skill_name} en el historial")
        return
    
    domain = args.domain or current.get("domain", "unknown")
    similar = find_similar(entries, args.skill_name, domain)
    
    # Excluir la entrada actual
    similar = [s for s in similar if s.get("fingerprint") != current.get("fingerprint")]
    
    if not similar:
        print(f"ℹ️ No hay skills similares para comparar")
        return
    
    print(f"📊 Comparando {args.skill_name} con {len(similar)} skills similares")
    
    comparisons = []
    for prior in similar[:5]:  # Max 5 comparaciones
        comp = compare(current, prior)
        comparisons.append(comp)
        
        print(f"\n  vs {prior.get('skill_name')} ({prior.get('match_type')}):")
        print(f"    Tendencia: {comp['trend']}")
        for metric, data in comp["deltas"].items():
            arrow = "↑" if data.get("improved") else "↓"
            print(f"    {metric}: {data['current']} vs {data['prior']} ({arrow} {data['delta']})")
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(comparisons, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"\n📁 Comparación guardada en: {args.output}")

if __name__ == "__main__":
    main()
