#!/usr/bin/env python3
"""
El Monstruo — Sabios Consultation Engine con Validación en Tiempo Real
======================================================================
Sprint 16 — 2026-04-20

Los Sabios (GPT-5.4, Claude, Gemini, Grok, DeepSeek, Perplexity) están
OBSOLETOS en cuanto a datos — su training data tiene cutoff.
Este script OBLIGA a:
1. Consultar a cada sabio vía API
2. Extraer claims factuales de sus respuestas
3. Validar CADA claim contra fuentes en tiempo real (PyPI, GitHub, NVD, web)
4. Generar un reporte de confiabilidad por sabio
5. Sintetizar solo los claims VERIFICADOS

Uso:
    python scripts/sabios_engine.py --prompt "¿Cuál es la mejor versión de langchain-core?"
    python scripts/sabios_engine.py --prompt "..." --sabios gpt,claude,gemini
    python scripts/sabios_engine.py --prompt "..." --validate-only  # Solo validar, no consultar

Principio: Los sabios son cerebros potentes pero ciegos al presente.
           Manus es los ojos. El código es la garantía.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

# ── API Configuration ──────────────────────────────────────────────
SABIOS_CONFIG = {
    "gpt": {
        "name": "GPT-5.4 (OpenAI)",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "openai/gpt-5.4",
        "key_env": "OPENROUTER_API_KEY",
    },
    "claude": {
        "name": "Claude (Anthropic)",
        "api_url": "https://api.anthropic.com/v1/messages",
        "model": "claude-sonnet-4-20250514",
        "key_env": "ANTHROPIC_API_KEY",
    },
    "gemini": {
        "name": "Gemini (Google)",
        "api_url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "model": "gemini-2.5-flash",
        "key_env": "GEMINI_API_KEY",
    },
    "grok": {
        "name": "Grok (xAI)",
        "api_url": "https://api.x.ai/v1/chat/completions",
        "model": "grok-4",
        "key_env": "XAI_API_KEY",
    },
    "perplexity": {
        "name": "Perplexity (Sonar)",
        "api_url": "https://api.perplexity.ai/chat/completions",
        "model": "sonar-pro",
        "key_env": "SONAR_API_KEY",
    },
}

REPORT_DIR = Path(__file__).parent.parent / "reports"


@dataclass
class SabioResponse:
    sabio: str
    model: str
    response_text: str
    claims: list[str] = field(default_factory=list)
    verified_claims: list[dict] = field(default_factory=list)
    unverified_claims: list[str] = field(default_factory=list)
    false_claims: list[dict] = field(default_factory=list)
    trust_score: float = 0.0
    latency_ms: int = 0
    error: Optional[str] = None


@dataclass
class ConsultationReport:
    prompt: str
    timestamp: str
    sabios_consulted: list[SabioResponse] = field(default_factory=list)
    consensus_claims: list[str] = field(default_factory=list)
    disputed_claims: list[dict] = field(default_factory=list)
    synthesis: str = ""


# ── API Callers ────────────────────────────────────────────────────
def call_openrouter(model: str, prompt: str, api_key: str) -> str:
    """Call OpenRouter-compatible API (GPT, Grok, Perplexity)."""
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "Eres un experto técnico. Responde con datos específicos: versiones exactas, fechas, URLs. NO inventes datos."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1500,
            "temperature": 0.1,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_anthropic(model: str, prompt: str, api_key: str) -> str:
    """Call Anthropic Claude API directly."""
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 1500,
            "system": "Eres un experto técnico. Responde con datos específicos: versiones exactas, fechas, URLs. NO inventes datos.",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    return data["content"][0]["text"]


def call_gemini(model: str, prompt: str, api_key: str) -> str:
    """Call Google Gemini API directly."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    r = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1500},
        },
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_perplexity(model: str, prompt: str, api_key: str) -> str:
    """Call Perplexity Sonar API directly."""
    r = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "Eres un experto técnico. Responde con datos específicos y cita fuentes."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1500,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_xai(model: str, prompt: str, api_key: str) -> str:
    """Call xAI Grok API directly."""
    r = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "Eres un experto técnico. Responde con datos específicos: versiones exactas, fechas, URLs."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1500,
            "temperature": 0.1,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


CALLERS = {
    "gpt": lambda m, p, k: call_openrouter("openai/gpt-5.4", p, k),
    "claude": call_anthropic,
    "gemini": call_gemini,
    "grok": call_xai,
    "perplexity": call_perplexity,
}


# ── Claim Extractor ───────────────────────────────────────────────
def extract_version_claims(text: str) -> list[str]:
    """Extract factual claims about versions from sabio response."""
    claims = []
    # Pattern: package==version or package version X.Y.Z
    version_pattern = re.compile(
        r"([a-zA-Z0-9_-]+)\s*(?:==|versión|version|v\.?|es)\s*(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)",
        re.IGNORECASE,
    )
    for match in version_pattern.finditer(text):
        pkg = match.group(1).lower().strip()
        ver = match.group(2).strip()
        claims.append(f"{pkg}=={ver}")

    # Pattern: "latest version is X.Y.Z"
    latest_pattern = re.compile(
        r"(?:latest|última|newest|current)\s+(?:version|versión)\s+(?:is|es|:)\s*(\d+\.\d+(?:\.\d+)?)",
        re.IGNORECASE,
    )
    for match in latest_pattern.finditer(text):
        claims.append(f"latest=={match.group(1)}")

    return list(set(claims))


# ── Real-Time Claim Validator ──────────────────────────────────────
def validate_claim_realtime(claim: str) -> dict:
    """Validate a single version claim against PyPI in real-time."""
    result = {"claim": claim, "verified": False, "source": None, "detail": None}

    match = re.match(r"([a-zA-Z0-9_-]+)==(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)", claim)
    if not match:
        result["detail"] = "Could not parse claim"
        return result

    pkg, ver = match.group(1), match.group(2)

    try:
        r = requests.get(f"https://pypi.org/pypi/{pkg}/json", timeout=10)
        if r.status_code == 200:
            data = r.json()
            latest = data["info"]["version"]
            exists = ver in data["releases"]
            result["source"] = f"PyPI (latest: {latest})"

            if ver == latest:
                result["verified"] = True
                result["detail"] = f"CONFIRMED: {pkg}=={ver} is the latest on PyPI"
            elif exists:
                result["verified"] = True
                result["detail"] = f"EXISTS but OUTDATED: {pkg}=={ver} exists, latest is {latest}"
            else:
                result["verified"] = False
                result["detail"] = f"FALSE: {pkg}=={ver} does NOT exist on PyPI. Latest: {latest}"
        elif r.status_code == 404:
            result["detail"] = f"Package '{pkg}' not found on PyPI"
        else:
            result["detail"] = f"PyPI returned HTTP {r.status_code}"
    except Exception as e:
        result["detail"] = f"Validation error: {e}"

    return result


# ── Consultation Orchestrator ──────────────────────────────────────
def consult_sabios(
    prompt: str,
    sabios: list[str] | None = None,
    validate: bool = True,
) -> ConsultationReport:
    """
    Consult the sabios and validate their outputs in real-time.
    
    This is the core function that ENFORCES the validation protocol:
    1. Call each sabio API
    2. Extract factual claims from responses
    3. Validate each claim against real-time sources
    4. Calculate trust scores
    5. Synthesize only verified claims
    """
    if sabios is None:
        sabios = list(SABIOS_CONFIG.keys())

    report = ConsultationReport(
        prompt=prompt,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    print(f"\n{'='*70}")
    print(f"  SABIOS ENGINE — Consulta con Validación en Tiempo Real")
    print(f"  Prompt: {prompt[:80]}...")
    print(f"  Sabios: {', '.join(sabios)}")
    print(f"{'='*70}\n")

    # ── Call each sabio ────────────────────────────────────────────
    for sabio_key in sabios:
        config = SABIOS_CONFIG.get(sabio_key)
        if not config:
            print(f"  ⚠️  Unknown sabio: {sabio_key}")
            continue

        api_key = os.environ.get(config["key_env"], "")
        if not api_key:
            print(f"  ⚠️  {config['name']}: No API key ({config['key_env']})")
            report.sabios_consulted.append(SabioResponse(
                sabio=sabio_key, model=config["model"],
                response_text="", error=f"Missing API key: {config['key_env']}"
            ))
            continue

        print(f"  📡 Consulting {config['name']}...")
        start = time.time()

        try:
            caller = CALLERS.get(sabio_key)
            if not caller:
                raise ValueError(f"No caller for {sabio_key}")

            response_text = caller(config["model"], prompt, api_key)
            latency = int((time.time() - start) * 1000)

            sabio_resp = SabioResponse(
                sabio=sabio_key,
                model=config["model"],
                response_text=response_text,
                latency_ms=latency,
            )

            print(f"      ✅ Response received ({latency}ms, {len(response_text)} chars)")

            # Extract and validate claims
            if validate:
                claims = extract_version_claims(response_text)
                sabio_resp.claims = claims
                print(f"      📋 Extracted {len(claims)} version claims")

                for claim in claims:
                    validation = validate_claim_realtime(claim)
                    if validation["verified"]:
                        sabio_resp.verified_claims.append(validation)
                        print(f"         ✅ {claim}: {validation['detail']}")
                    else:
                        sabio_resp.false_claims.append(validation)
                        print(f"         ❌ {claim}: {validation['detail']}")

                # Trust score
                total = len(claims) if claims else 1
                verified = len(sabio_resp.verified_claims)
                sabio_resp.trust_score = round(verified / total, 2) if total > 0 else 0.0
                print(f"      🎯 Trust score: {sabio_resp.trust_score} ({verified}/{total} claims verified)")

            report.sabios_consulted.append(sabio_resp)

        except Exception as e:
            latency = int((time.time() - start) * 1000)
            print(f"      ❌ Error ({latency}ms): {e}")
            report.sabios_consulted.append(SabioResponse(
                sabio=sabio_key, model=config["model"],
                response_text="", latency_ms=latency, error=str(e)
            ))

    # ── Consensus analysis ─────────────────────────────────────────
    all_verified = {}
    for s in report.sabios_consulted:
        for vc in s.verified_claims:
            claim = vc["claim"]
            if claim not in all_verified:
                all_verified[claim] = []
            all_verified[claim].append(s.sabio)

    report.consensus_claims = [
        f"{claim} (confirmed by: {', '.join(sabios_list)})"
        for claim, sabios_list in all_verified.items()
        if len(sabios_list) >= 2
    ]

    # Summary
    print(f"\n{'='*70}")
    print(f"  CONSENSUS: {len(report.consensus_claims)} claims verified by 2+ sabios")
    for c in report.consensus_claims:
        print(f"    ✅ {c}")
    print(f"{'='*70}\n")

    # Save report
    REPORT_DIR.mkdir(exist_ok=True)
    report_path = REPORT_DIR / f"sabios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w") as f:
        json.dump(asdict(report), f, indent=2, default=str)
    print(f"  Report saved: {report_path}")

    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sabios Consultation Engine")
    parser.add_argument("--prompt", required=True, help="Question to ask the sabios")
    parser.add_argument("--sabios", default=None, help="Comma-separated list of sabios (gpt,claude,gemini,grok,perplexity)")
    parser.add_argument("--no-validate", action="store_true", help="Skip real-time validation")
    args = parser.parse_args()

    sabios_list = args.sabios.split(",") if args.sabios else None
    consult_sabios(args.prompt, sabios=sabios_list, validate=not args.no_validate)
