#!/usr/bin/env python3.11
"""
benchmark_before_build.py — Gap Analysis + Benchmark Before Build

NUEVO en skill-factory v2.0. Antes de construir cualquier skill,
verifica si ya existe interna o externamente, evalúa opciones, y
recomienda: install / fork / compose / build.

Integración directa con api-context-injector v4.0:
  - ecosystem_state.yaml → contrato compartido
  - capability_registry.yaml → capacidades existentes
  - skill_scout.py → búsqueda externa
  - trust_fit_evaluator.yaml → evaluación de candidatos

Uso:
    python3.11 benchmark_before_build.py --spec spec.yaml
    python3.11 benchmark_before_build.py --spec spec.yaml --deep-scout
    python3.11 benchmark_before_build.py --spec spec.yaml --output benchmark_report.yaml
"""

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import yaml
from pathlib import Path
from datetime import datetime

# ============================================================
# PATHS
# ============================================================

FACTORY_ROOT = Path(__file__).parent.parent
INJECTOR_ROOT = Path("/home/ubuntu/skills/api-context-injector")
SKILLS_ROOT = Path("/home/ubuntu/skills")

ECOSYSTEM_STATE = INJECTOR_ROOT / "routing" / "ecosystem_state.yaml"
CAPABILITY_REGISTRY = INJECTOR_ROOT / "routing" / "capability_registry.yaml"
SKILLS_REGISTRY = INJECTOR_ROOT / "references" / "skills-registry.yaml"
TRUST_FIT = INJECTOR_ROOT / "routing" / "trust_fit_evaluator.yaml"
SKILL_SCOUT = INJECTOR_ROOT / "scripts" / "skill_scout.py"


# ============================================================
# STEP 1: INTERNAL GAP ANALYSIS
# ============================================================

def analyze_internal_coverage(spec: dict) -> dict:
    """Analiza qué porcentaje de la skill propuesta ya existe internamente."""
    
    result = {
        "internal_coverage_pct": 0,
        "matching_capabilities": [],
        "matching_skills": [],
        "missing_capabilities": [],
        "composable_from": [],
    }
    
    # Extraer capabilities necesarias de la spec
    needed_capabilities = set()
    for cap in spec.get("core_capabilities", []):
        needed_capabilities.add(cap.lower().replace(" ", "_").replace("-", "_"))
    
    # También inferir del dominio y descripción
    description = (spec.get("description", "") + " " + spec.get("domain", "")).lower()
    
    capability_keywords = {
        "text_generation": ["text", "write", "generate text", "content"],
        "code_generation": ["code", "programming", "script", "developer"],
        "image_generation": ["image", "photo", "visual", "render"],
        "video_generation": ["video", "animation", "clip"],
        "audio_generation": ["audio", "sound", "music", "voice"],
        "web_scraping": ["scraping", "crawl", "extract data", "web data"],
        "data_analysis": ["analysis", "analytics", "data", "statistics"],
        "database": ["database", "sql", "storage", "persist"],
        "email": ["email", "mail", "notification"],
        "payment": ["payment", "billing", "invoice", "stripe"],
        "social_media": ["social", "instagram", "tiktok", "twitter"],
        "real_time_search": ["search", "research", "real-time", "current"],
    }
    
    for cap, keywords in capability_keywords.items():
        if any(kw in description for kw in keywords):
            needed_capabilities.add(cap)
    
    if not needed_capabilities:
        needed_capabilities.add("general")
    
    # Cargar capability registry (nested under 'capabilities' key)
    existing_capabilities = set()
    if CAPABILITY_REGISTRY.exists():
        try:
            with open(CAPABILITY_REGISTRY) as f:
                cap_data = yaml.safe_load(f)
            caps = cap_data.get("capabilities", cap_data) if isinstance(cap_data, dict) else {}
            for key in caps:
                if isinstance(caps[key], dict):
                    existing_capabilities.add(key)
        except Exception:
            pass
    
    # Fuzzy matching: map needed capabilities to existing ones
    matched = set()
    missing = set()
    
    for needed in needed_capabilities:
        # Direct match
        if needed in existing_capabilities:
            matched.add(needed)
            continue
        
        # Fuzzy: check if needed is a substring of any existing or vice versa
        found = False
        for existing in existing_capabilities:
            # "web_scraping" matches "web_scraping_static", "web_scraping_dynamic", etc.
            if needed in existing or existing in needed:
                matched.add(needed)
                found = True
                break
            # "email" matches "email_send_personal", "email_send_transactional"
            if needed.split("_")[0] == existing.split("_")[0] and len(needed.split("_")[0]) > 3:
                matched.add(needed)
                found = True
                break
            # "data_analysis" matches via keyword overlap
            needed_parts = set(needed.split("_"))
            existing_parts = set(existing.split("_"))
            overlap = needed_parts & existing_parts - {"and", "the", "of"}
            if len(overlap) >= 1 and len(needed_parts) <= 3:
                matched.add(needed)
                found = True
                break
        
        if not found:
            missing.add(needed)
    
    result["matching_capabilities"] = sorted(matched)
    result["missing_capabilities"] = sorted(missing)
    
    if needed_capabilities:
        result["internal_coverage_pct"] = round(len(matched) / len(needed_capabilities) * 100, 1)
    
    # Buscar skills existentes similares
    if SKILLS_ROOT.exists():
        spec_name = spec.get("name", "").lower()
        spec_domain = spec.get("domain", "").lower()
        spec_desc = spec.get("description", "").lower()
        
        for skill_dir in SKILLS_ROOT.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            
            try:
                content = skill_md.read_text(encoding="utf-8")[:1000].lower()
                
                # Check for name/domain overlap
                overlap_score = 0
                if spec_name and spec_name in content:
                    overlap_score += 3
                if spec_domain and spec_domain in content:
                    overlap_score += 2
                
                # Check keyword overlap
                spec_words = set(spec_desc.split())
                content_words = set(content.split())
                common = spec_words & content_words - {"de", "la", "el", "en", "para", "con", "y", "a", "the", "and", "for"}
                if len(common) > 3:
                    overlap_score += min(len(common), 5)
                
                if overlap_score >= 3:
                    result["matching_skills"].append({
                        "name": skill_dir.name,
                        "overlap_score": overlap_score,
                        "path": str(skill_dir),
                    })
            except Exception:
                continue
    
    result["matching_skills"].sort(key=lambda x: -x["overlap_score"])
    
    # Determine composability
    if result["internal_coverage_pct"] >= 60:
        result["composable_from"] = result["matching_capabilities"]
    
    return result


# ============================================================
# STEP 2: EXTERNAL SCOUT
# ============================================================

def scout_external(spec: dict, deep: bool = False) -> dict:
    """Busca skills externas que cubran la necesidad."""
    
    result = {
        "candidates_found": 0,
        "candidates": [],
        "evaluations": [],
        "best_candidate": None,
    }
    
    if not SKILL_SCOUT.exists():
        result["error"] = "skill_scout.py not found — api-context-injector not installed"
        return result
    
    # Build search query from spec
    search_terms = []
    if spec.get("domain"):
        search_terms.append(spec["domain"])
    if spec.get("name"):
        search_terms.append(spec["name"])
    if spec.get("core_capabilities"):
        search_terms.extend(spec["core_capabilities"][:2])
    
    query = " ".join(search_terms[:3])
    
    try:
        cmd = ["python3.11", str(SKILL_SCOUT), "--search", query]
        if deep:
            cmd.append("--evaluate")
        cmd.extend(["--output", "/tmp/skill-factory/scout_results.md"])
        
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if proc.returncode == 0:
            output = proc.stdout
            
            # Parse results count
            count_match = re.search(r'(\d+) resultados encontrados', output)
            if count_match:
                result["candidates_found"] = int(count_match.group(1))
            
            # Parse evaluations if deep
            if deep and "Evaluaciones TRUST+FIT" in output:
                for line in output.split("\n"):
                    if "github.com" in line and "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 7:
                            result["evaluations"].append({
                                "url": parts[1],
                                "score": parts[2],
                                "recommendation": parts[6],
                            })
                
                # Find best candidate
                for ev in result["evaluations"]:
                    if "INSTALL" in ev.get("recommendation", "").upper():
                        result["best_candidate"] = ev
                        break
                if not result["best_candidate"] and result["evaluations"]:
                    result["best_candidate"] = result["evaluations"][0]
        else:
            result["error"] = proc.stderr[:200] if proc.stderr else "Scout failed"
    except subprocess.TimeoutExpired:
        result["error"] = "Scout timed out (120s)"
    except Exception as e:
        result["error"] = str(e)
    
    return result


# ============================================================
# STEP 3: DECISION ENGINE
# ============================================================

def decide_action(spec: dict, internal: dict, external: dict) -> dict:
    """Decide: install / fork / compose / build / reject."""
    
    decision = {
        "action": "build",
        "confidence": 0.5,
        "reasoning": [],
        "alternatives": [],
    }
    
    internal_pct = internal.get("internal_coverage_pct", 0)
    matching_skills = internal.get("matching_skills", [])
    best_external = external.get("best_candidate")
    external_count = external.get("candidates_found", 0)
    
    # Rule 1: If exact internal match exists
    if matching_skills and matching_skills[0].get("overlap_score", 0) >= 7:
        decision["action"] = "extend_existing"
        decision["confidence"] = 0.9
        decision["reasoning"].append(
            f"Skill interna '{matching_skills[0]['name']}' tiene overlap score {matching_skills[0]['overlap_score']}/10. "
            "Mejor extender que duplicar."
        )
        decision["target"] = matching_skills[0]["path"]
        return decision
    
    # Rule 2: If external candidate scores INSTALL
    if best_external and "INSTALL" in best_external.get("recommendation", "").upper():
        decision["action"] = "install"
        decision["confidence"] = 0.8
        decision["reasoning"].append(
            f"Candidato externo {best_external.get('url', '?')} evaluado como INSTALL "
            f"(score: {best_external.get('score', '?')}). Más eficiente que construir."
        )
        decision["target"] = best_external.get("url")
        decision["alternatives"].append({"action": "build", "reason": "Si se necesita personalización profunda"})
        return decision
    
    # Rule 3: If external candidate scores FORK
    if best_external and "FORK" in best_external.get("recommendation", "").upper():
        decision["action"] = "fork_and_harden"
        decision["confidence"] = 0.7
        decision["reasoning"].append(
            f"Candidato externo {best_external.get('url', '?')} evaluado como FORK_AND_HARDEN. "
            "Buena base pero necesita adaptación."
        )
        decision["target"] = best_external.get("url")
        decision["alternatives"].append({"action": "build", "reason": "Si la base no es suficiente"})
        return decision
    
    # Rule 4: If >60% composable from internal pieces
    if internal_pct >= 60:
        decision["action"] = "compose"
        decision["confidence"] = 0.7
        decision["reasoning"].append(
            f"{internal_pct}% de las capacidades ya existen internamente. "
            "Componer desde piezas existentes es más eficiente."
        )
        decision["composable_from"] = internal.get("composable_from", [])
        decision["alternatives"].append({"action": "build", "reason": "Si la composición no alcanza"})
        return decision
    
    # Rule 5: Default to build
    decision["action"] = "build"
    decision["confidence"] = 0.6
    reasons = []
    
    if internal_pct < 30:
        reasons.append(f"Solo {internal_pct}% de cobertura interna — gap significativo")
    if external_count == 0:
        reasons.append("No se encontraron candidatos externos")
    elif best_external and "REJECT" in best_external.get("recommendation", "").upper():
        reasons.append("Candidatos externos no pasan evaluación TRUST+FIT")
    else:
        reasons.append("No hay alternativa viable a construir")
    
    decision["reasoning"] = reasons
    
    # Check if we should suggest NOT building
    if spec.get("core_capabilities") and len(spec["core_capabilities"]) > 10:
        decision["alternatives"].append({
            "action": "decompose",
            "reason": "Skill demasiado amplia — considerar dividir en 2-3 skills más pequeñas"
        })
    
    return decision


# ============================================================
# STEP 4: GENERATE REPORT
# ============================================================

def generate_report(spec: dict, internal: dict, external: dict, decision: dict) -> dict:
    """Genera reporte completo de benchmark."""
    
    return {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "spec_name": spec.get("name", "unknown"),
            "spec_domain": spec.get("domain", "unknown"),
        },
        "internal_analysis": internal,
        "external_analysis": {
            "candidates_found": external.get("candidates_found", 0),
            "best_candidate": external.get("best_candidate"),
            "error": external.get("error"),
        },
        "decision": decision,
        "ecosystem_state_consulted": ECOSYSTEM_STATE.exists(),
        "capability_registry_consulted": CAPABILITY_REGISTRY.exists(),
        "recommendation_summary": (
            f"ACTION: {decision['action'].upper()} | "
            f"Confidence: {decision['confidence']*100:.0f}% | "
            f"Internal coverage: {internal.get('internal_coverage_pct', 0)}% | "
            f"External candidates: {external.get('candidates_found', 0)}"
        ),
    }


# ============================================================
# MAIN
# ============================================================

async def run_benchmark(spec: dict, deep_scout: bool = False) -> dict:
    """Ejecuta el benchmark completo."""
    
    print(f"[BENCHMARK] Analizando: {spec.get('name', 'unknown')}")
    
    # Step 1: Internal analysis
    print("[BENCHMARK] [1/3] Análisis interno...")
    internal = analyze_internal_coverage(spec)
    print(f"  Cobertura interna: {internal['internal_coverage_pct']}%")
    print(f"  Skills similares: {len(internal['matching_skills'])}")
    print(f"  Capabilities match: {len(internal['matching_capabilities'])}")
    print(f"  Capabilities missing: {len(internal['missing_capabilities'])}")
    
    # Step 2: External scout
    print(f"[BENCHMARK] [2/3] Scout externo {'(deep)' if deep_scout else '(quick)'}...")
    external = scout_external(spec, deep=deep_scout)
    print(f"  Candidatos encontrados: {external.get('candidates_found', 0)}")
    if external.get("best_candidate"):
        print(f"  Mejor candidato: {external['best_candidate'].get('url', '?')}")
    if external.get("error"):
        print(f"  Error: {external['error']}")
    
    # Step 3: Decision
    print("[BENCHMARK] [3/3] Tomando decisión...")
    decision = decide_action(spec, internal, external)
    print(f"  DECISIÓN: {decision['action'].upper()} (confianza: {decision['confidence']*100:.0f}%)")
    for reason in decision.get("reasoning", []):
        print(f"    → {reason}")
    
    # Generate report
    report = generate_report(spec, internal, external, decision)
    
    return report


async def main():
    parser = argparse.ArgumentParser(description="Benchmark Before Build — Gap Analysis")
    parser.add_argument("--spec", required=True, help="Path to spec.yaml")
    parser.add_argument("--deep-scout", action="store_true", help="Deep external scout with TRUST+FIT evaluation")
    parser.add_argument("--output", help="Path to save benchmark report")
    args = parser.parse_args()
    
    with open(args.spec) as f:
        spec = yaml.safe_load(f)
    
    report = await run_benchmark(spec, deep_scout=args.deep_scout)
    
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            yaml.dump(report, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"\nReporte guardado en: {args.output}")
    else:
        print(f"\n{yaml.dump(report, default_flow_style=False, allow_unicode=True, sort_keys=False)}")


if __name__ == "__main__":
    asyncio.run(main())
