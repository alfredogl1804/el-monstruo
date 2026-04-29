#!/usr/bin/env python3.11
"""
scan_env.py — Verifica qué variables de entorno de APIs están disponibles.

Escanea todas las env vars conocidas y reporta cuáles están presentes,
cuáles faltan, y genera un reporte de disponibilidad.

Uso:
    python3.11 scan_env.py [--output report.json]
"""

import os
import json
import argparse
from datetime import datetime

# Registro de todas las env vars conocidas del ecosistema
KNOWN_ENV_VARS = {
    # IA/LLM APIs
    "OPENAI_API_KEY": {"service": "OpenAI (GPT-5.4)", "category": "ia_llm", "critical": True},
    "ANTHROPIC_API_KEY": {"service": "Anthropic (Claude)", "category": "ia_llm", "critical": True},
    "GEMINI_API_KEY": {"service": "Google Gemini", "category": "ia_llm", "critical": True},
    "XAI_API_KEY": {"service": "xAI (Grok)", "category": "ia_llm", "critical": True},
    "SONAR_API_KEY": {"service": "Perplexity Sonar", "category": "ia_llm", "critical": True},
    "OPENROUTER_API_KEY": {"service": "OpenRouter (DeepSeek, Kimi)", "category": "ia_llm", "critical": True},
    
    # Media APIs
    "HEYGEN_API_KEY": {"service": "HeyGen Video", "category": "media", "critical": False},
    "ELEVENLABS_API_KEY": {"service": "ElevenLabs Voice", "category": "media", "critical": False},
    
    # Infrastructure
    "CLOUDFLARE_API_TOKEN": {"service": "Cloudflare", "category": "infra", "critical": False},
    "DROPBOX_API_KEY": {"service": "Dropbox", "category": "infra", "critical": False},
    "GH_TOKEN": {"service": "GitHub", "category": "infra", "critical": False},
    "GOOGLE_DRIVE_TOKEN": {"service": "Google Drive", "category": "infra", "critical": False},
    "GOOGLE_WORKSPACE_CLI_TOKEN": {"service": "Google Workspace", "category": "infra", "critical": False},
    
    # OpenAI extras
    "OPENAI_API_BASE": {"service": "OpenAI Base URL", "category": "config", "critical": False},
    "OPENAI_BASE_URL": {"service": "OpenAI Base URL", "category": "config", "critical": False},
}


def scan_environment():
    """Escanea el entorno y reporta disponibilidad de APIs."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_known": len(KNOWN_ENV_VARS),
        "available": [],
        "missing": [],
        "by_category": {},
        "sabios_status": {},
    }
    
    for var_name, info in KNOWN_ENV_VARS.items():
        value = os.environ.get(var_name, "")
        entry = {
            "env_var": var_name,
            "service": info["service"],
            "category": info["category"],
            "critical": info["critical"],
            "present": bool(value),
            "key_prefix": value[:8] + "..." if value else "N/A",
        }
        
        if value:
            results["available"].append(entry)
        else:
            results["missing"].append(entry)
        
        # Agrupar por categoría
        cat = info["category"]
        if cat not in results["by_category"]:
            results["by_category"][cat] = {"available": 0, "missing": 0}
        if value:
            results["by_category"][cat]["available"] += 1
        else:
            results["by_category"][cat]["missing"] += 1
    
    # Estado de los 6 sabios
    sabios = {
        "GPT-5.4": "OPENAI_API_KEY",
        "Claude": "ANTHROPIC_API_KEY",
        "Gemini": "GEMINI_API_KEY",
        "Grok": "XAI_API_KEY",
        "DeepSeek": "OPENROUTER_API_KEY",
        "Perplexity": "SONAR_API_KEY",
    }
    
    sabios_ok = 0
    for name, var in sabios.items():
        available = bool(os.environ.get(var, ""))
        results["sabios_status"][name] = available
        if available:
            sabios_ok += 1
    
    results["sabios_available"] = sabios_ok
    results["sabios_total"] = 6
    results["sabios_healthy"] = sabios_ok >= 3
    
    return results


def print_report(results):
    """Imprime un reporte legible."""
    print("=" * 60)
    print(f"  API Environment Scan — {results['timestamp']}")
    print("=" * 60)
    
    print(f"\n  Total conocidas: {results['total_known']}")
    print(f"  Disponibles:     {len(results['available'])}")
    print(f"  Faltantes:       {len(results['missing'])}")
    
    print(f"\n  6 Sabios: {results['sabios_available']}/{results['sabios_total']}", end="")
    print(" ✅" if results['sabios_healthy'] else " ❌ ALERTA: < 3 sabios")
    
    print("\n--- Por Categoría ---")
    for cat, counts in results["by_category"].items():
        total = counts["available"] + counts["missing"]
        print(f"  {cat}: {counts['available']}/{total}")
    
    print("\n--- Disponibles ---")
    for entry in results["available"]:
        critical = " [CRITICAL]" if entry["critical"] else ""
        print(f"  ✅ {entry['env_var']}: {entry['service']}{critical}")
    
    if results["missing"]:
        print("\n--- Faltantes ---")
        for entry in results["missing"]:
            critical = " [CRITICAL]" if entry["critical"] else ""
            print(f"  ❌ {entry['env_var']}: {entry['service']}{critical}")
    
    print("\n--- Sabios ---")
    for name, available in results["sabios_status"].items():
        status = "✅" if available else "❌"
        print(f"  {status} {name}")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Escanea variables de entorno de APIs")
    parser.add_argument("--output", help="Guardar reporte en JSON")
    args = parser.parse_args()
    
    results = scan_environment()
    print_report(results)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nReporte guardado en: {args.output}")


if __name__ == "__main__":
    main()
