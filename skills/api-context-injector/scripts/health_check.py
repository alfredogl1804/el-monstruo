#!/usr/bin/env python3.11
"""
health_check.py — Verifica el estado de todas las APIs disponibles.

Hace ping a cada API con credenciales disponibles en env vars
y reporta cuáles están operativas.

Uso:
    python3.11 health_check.py [--output report.json] [--quick]
"""

import os
import json
import argparse
import time
from datetime import datetime


def check_openai():
    """Verifica OpenAI GPT-5.4."""
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-5.4",
            max_completion_tokens=10,
            messages=[{"role": "user", "content": "ping"}]
        )
        return {"status": "ok", "model": "gpt-5.4", "response_id": response.id}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


def check_anthropic():
    """Verifica Claude Sonnet 4.6 vía OpenRouter (lección #1: Opus tiene timeouts)."""
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        response = client.chat.completions.create(
            model="anthropic/claude-sonnet-4-6",
            max_tokens=10,
            messages=[{"role": "user", "content": "ping"}]
        )
        return {"status": "ok", "model": "anthropic/claude-sonnet-4-6", "id": response.id}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


def check_gemini():
    """Verifica Google Gemini."""
    try:
        from google import genai
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-3.1-pro-preview",
            contents="ping"
        )
        return {"status": "ok", "model": "gemini-3.1-pro-preview"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


def check_grok():
    """Verifica xAI Grok."""
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ.get("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        response = client.chat.completions.create(
            model="grok-4.20-0309-reasoning",
            max_tokens=10,
            messages=[{"role": "user", "content": "ping"}]
        )
        return {"status": "ok", "model": "grok-4.20-0309-reasoning"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


def check_perplexity():
    """Verifica Perplexity Sonar."""
    try:
        import requests
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {os.environ.get('SONAR_API_KEY', '')}"},
            json={
                "model": "sonar-pro",
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 10
            },
            timeout=30
        )
        if response.status_code == 200:
            return {"status": "ok", "model": "sonar-pro"}
        else:
            return {"status": "error", "http_code": response.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


def check_openrouter():
    """Verifica OpenRouter (DeepSeek R1)."""
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1",
            max_tokens=10,
            messages=[{"role": "user", "content": "ping"}]
        )
        return {"status": "ok", "model": "deepseek/deepseek-r1"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


def check_heygen():
    """Verifica HeyGen API."""
    try:
        import requests
        response = requests.get(
            "https://api.heygen.com/v1/video_status.list",
            headers={"X-Api-Key": os.environ.get("HEYGEN_API_KEY", "")},
            timeout=15
        )
        if response.status_code in [200, 401]:
            return {"status": "ok" if response.status_code == 200 else "auth_issue"}
        return {"status": "error", "http_code": response.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


def check_elevenlabs():
    """Verifica ElevenLabs API."""
    try:
        import requests
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "")},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            return {"status": "ok", "voices_count": len(data.get("voices", []))}
        return {"status": "error", "http_code": response.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


# Registro de checks
HEALTH_CHECKS = {
    "OpenAI (GPT-5.4)": {"check": check_openai, "env": "OPENAI_API_KEY", "critical": True},
    "Claude Sonnet 4.6 (OpenRouter)": {"check": check_anthropic, "env": "OPENROUTER_API_KEY", "critical": True},
    "Google Gemini": {"check": check_gemini, "env": "GEMINI_API_KEY", "critical": True},
    "xAI (Grok)": {"check": check_grok, "env": "XAI_API_KEY", "critical": True},
    "Perplexity Sonar": {"check": check_perplexity, "env": "SONAR_API_KEY", "critical": True},
    "OpenRouter (DeepSeek)": {"check": check_openrouter, "env": "OPENROUTER_API_KEY", "critical": True},
    "HeyGen": {"check": check_heygen, "env": "HEYGEN_API_KEY", "critical": False},
    "ElevenLabs": {"check": check_elevenlabs, "env": "ELEVENLABS_API_KEY", "critical": False},
}


def run_health_checks(quick=False):
    """Ejecuta todos los health checks."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "summary": {"ok": 0, "error": 0, "skipped": 0},
        "sabios_healthy": 0,
    }
    
    for name, config in HEALTH_CHECKS.items():
        env_var = config["env"]
        
        if not os.environ.get(env_var):
            results["checks"][name] = {"status": "skipped", "reason": f"{env_var} not set"}
            results["summary"]["skipped"] += 1
            continue
        
        if quick and not config["critical"]:
            results["checks"][name] = {"status": "skipped", "reason": "quick mode"}
            results["summary"]["skipped"] += 1
            continue
        
        print(f"  Checking {name}...", end=" ", flush=True)
        start = time.time()
        
        try:
            result = config["check"]()
            elapsed = round(time.time() - start, 2)
            result["latency_s"] = elapsed
            results["checks"][name] = result
            
            if result["status"] == "ok":
                results["summary"]["ok"] += 1
                if config["critical"]:
                    results["sabios_healthy"] += 1
                print(f"✅ ({elapsed}s)")
            else:
                results["summary"]["error"] += 1
                print(f"❌ {result.get('error', 'unknown')[:50]}")
        except Exception as e:
            elapsed = round(time.time() - start, 2)
            results["checks"][name] = {"status": "error", "error": str(e)[:200], "latency_s": elapsed}
            results["summary"]["error"] += 1
            print(f"❌ {str(e)[:50]}")
    
    results["all_sabios_ok"] = results["sabios_healthy"] >= 3
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Health check de todas las APIs")
    parser.add_argument("--output", help="Guardar reporte en JSON")
    parser.add_argument("--quick", action="store_true", help="Solo verificar APIs críticas")
    args = parser.parse_args()
    
    print("=" * 50)
    print("  API Health Check")
    print("=" * 50)
    
    results = run_health_checks(quick=args.quick)
    
    print(f"\n  OK: {results['summary']['ok']}")
    print(f"  Error: {results['summary']['error']}")
    print(f"  Skipped: {results['summary']['skipped']}")
    print(f"  Sabios healthy: {results['sabios_healthy']}/6", end="")
    print(" ✅" if results["all_sabios_ok"] else " ❌ ALERTA")
    print("=" * 50)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nReporte guardado: {args.output}")


if __name__ == "__main__":
    main()
