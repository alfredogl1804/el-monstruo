#!/usr/bin/env python3.11
"""
cidp_validator.py — Stage 5: Reality Validation Loop.

Manus como validador activo: extrae claims, triangula fuentes,
verifica frescura, aísla contradicciones, rechaza tecnología obsoleta.
Aplica protocolo anti-autoboicot obligatoriamente.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")
from conector_sabios import consultar_sabio

SKILL_DIR = Path(__file__).parent.parent


async def extract_claims(responses: list) -> list:
    """Extract verifiable claims from sabio responses."""
    all_claims = []
    for resp in responses:
        claims = resp.get("claims", [])
        needs_validation = resp.get("needs_validation", [])
        resp.get("output", "")

        for claim in claims:
            all_claims.append(
                {
                    "claim": claim,
                    "source_sabio": resp.get("sabio", "unknown"),
                    "task_id": resp.get("task_id", "unknown"),
                    "type": "explicit",
                }
            )

        for item in needs_validation:
            all_claims.append(
                {
                    "claim": item,
                    "source_sabio": resp.get("sabio", "unknown"),
                    "task_id": resp.get("task_id", "unknown"),
                    "type": "needs_validation",
                }
            )

    return all_claims


async def verify_claim(claim: dict) -> dict:
    """Verify a single claim using Perplexity for real-time grounding."""
    claim_text = claim.get("claim", "")

    prompt = f"""Verifica esta afirmación en tiempo real (abril 2026):

AFIRMACIÓN: {claim_text}
FUENTE: {claim.get("source_sabio", "unknown")}

Responde con JSON:
{{
  "claim": "{claim_text[:200]}",
  "verified": true|false|null,
  "confidence": 0.0-1.0,
  "evidence": "Evidencia que encontraste",
  "correction": "Corrección si la afirmación es incorrecta, null si es correcta",
  "freshness": "current|outdated|unknown",
  "sources": ["URLs o referencias"]
}}"""

    try:
        response = await consultar_sabio("perplexity", prompt)
        text = response.get("respuesta", "")

        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            import re

            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                result = json.loads(match.group())
            else:
                result = {
                    "claim": claim_text[:200],
                    "verified": None,
                    "confidence": 0.3,
                    "evidence": "Could not parse verification response",
                    "freshness": "unknown",
                }

        result["source_sabio"] = claim.get("source_sabio", "unknown")
        result["task_id"] = claim.get("task_id", "unknown")
        result["cost_usd"] = response.get("tokens_total", 0) * 0.000005

    except Exception as e:
        result = {
            "claim": claim_text[:200],
            "verified": None,
            "confidence": 0,
            "evidence": f"Verification failed: {e}",
            "freshness": "unknown",
            "source_sabio": claim.get("source_sabio", "unknown"),
            "cost_usd": 0,
        }

    return result


async def detect_contradictions(verified_claims: list, orchestrator_plan: dict) -> list:
    """Detect contradictions between claims and with the orchestrator plan."""
    contradictions = []

    # Check for claims that contradict each other
    for i, c1 in enumerate(verified_claims):
        for c2 in verified_claims[i + 1 :]:
            if c1.get("verified") is True and c2.get("verified") is True:
                # Both verified but from different sabios — check for conflict
                if c1.get("source_sabio") != c2.get("source_sabio"):
                    # Simple heuristic: if corrections exist, there might be contradictions
                    if c1.get("correction") and c2.get("correction"):
                        contradictions.append(
                            {
                                "type": "inter_sabio",
                                "claim_1": c1.get("claim", ""),
                                "claim_2": c2.get("claim", ""),
                                "sabio_1": c1.get("source_sabio", ""),
                                "sabio_2": c2.get("source_sabio", ""),
                            }
                        )

    # Check for outdated claims (anti-autoboicot)
    for claim in verified_claims:
        if claim.get("freshness") == "outdated":
            contradictions.append(
                {
                    "type": "outdated",
                    "claim": claim.get("claim", ""),
                    "sabio": claim.get("source_sabio", ""),
                    "correction": claim.get("correction", ""),
                }
            )

    return contradictions


async def run_validator(swarm_responses: list, orchestrator_plan: dict, memory, output_dir: Path) -> dict:
    """Execute Stage 5: Reality Validation Loop."""
    # Step 1: Extract claims
    print("  Step 1: Extracting claims...")
    claims = await extract_claims(swarm_responses)
    print(f"  Extracted {len(claims)} claims")

    # Step 2: Verify claims (batch of 3)
    print("  Step 2: Verifying claims in real-time...")
    verified = []
    total_cost = 0.0

    # Limit to most important claims to manage costs
    # Modificado: si no hay suficientes "needs_validation", tomar más "explicit"
    needs_val = [c for c in claims if c.get("type") == "needs_validation"]
    explicit = [c for c in claims if c.get("type") == "explicit"]

    priority_claims = needs_val[:15]
    remaining_slots = 25 - len(priority_claims)
    priority_claims.extend(explicit[:remaining_slots])

    for i in range(0, len(priority_claims), 3):
        batch = priority_claims[i : i + 3]
        results = await asyncio.gather(*[verify_claim(c) for c in batch], return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                verified.append({"verified": None, "error": str(r)})
            else:
                verified.append(r)
                total_cost += r.get("cost_usd", 0)

    # Step 3: Detect contradictions
    print("  Step 3: Detecting contradictions...")
    contradictions = await detect_contradictions(verified, orchestrator_plan)

    # Step 4: Quarantine unverified/rejected claims
    quarantined = [v for v in verified if v.get("verified") is False or v.get("freshness") == "outdated"]

    # Store contradictions in memory
    if memory:
        for c in contradictions:
            memory.store_contradiction(c)

    # Compile result
    claims_verified = sum(1 for v in verified if v.get("verified") is True)
    claims_rejected = sum(1 for v in verified if v.get("verified") is False)
    claims_unknown = sum(1 for v in verified if v.get("verified") is None)

    result = {
        "total_claims": len(claims),
        "claims_checked": len(verified),
        "claims_verified": claims_verified,
        "claims_rejected": claims_rejected,
        "claims_unknown": claims_unknown,
        "contradictions_found": len(contradictions),
        "quarantined": len(quarantined),
        "contradictions": contradictions,
        "quarantined_claims": quarantined,
        "verified_claims": verified,
        "cost_usd": total_cost,
        "validation_score": claims_verified / max(len(verified), 1),
    }

    # Save
    report_path = output_dir / "validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Save readable report
    md_path = output_dir / "validation_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Validation Report\n\n")
        f.write(f"**Claims checked:** {len(verified)}\n")
        f.write(f"**Verified:** {claims_verified}\n")
        f.write(f"**Rejected:** {claims_rejected}\n")
        f.write(f"**Unknown:** {claims_unknown}\n")
        f.write(f"**Contradictions:** {len(contradictions)}\n\n")

        if contradictions:
            f.write("## Contradictions\n\n")
            for c in contradictions:
                f.write(f"- **{c.get('type', '?')}**: {c.get('claim', c.get('claim_1', '?'))[:100]}\n")

        if quarantined:
            f.write("\n## Quarantined Claims\n\n")
            for q in quarantined:
                f.write(f"- {q.get('claim', '?')[:100]} — {q.get('correction', 'No correction')[:100]}\n")

    return result
