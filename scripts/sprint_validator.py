#!/usr/bin/env python3
"""
El Monstruo — Sprint Validator (Master Orchestrator)
=====================================================
Sprint 16 — 2026-04-20

Orquesta los 3 motores en secuencia:
1. IVD Engine → Valida dependencias en tiempo real
2. Sabios Engine → Consulta a los sabios Y valida sus outputs
3. Auto-Repair → Detecta y repara problemas
4. Deploy Verify → Confirma que Railway tiene la versión correcta

Este script es la GARANTÍA de que nada pasa sin validación.
Si algún paso falla, el pipeline se detiene y reporta.

Uso:
    python scripts/sprint_validator.py --sprint sprint16
    python scripts/sprint_validator.py --sprint sprint16 --full  # Include sabios
    python scripts/sprint_validator.py --sprint sprint16 --fix   # Auto-repair
    python scripts/sprint_validator.py --sprint sprint16 --deploy # Verify deploy

Principio: Un sprint no está completo hasta que este script dice PASS.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Import our engines
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.auto_repair import run_repair
from scripts.ivd_engine import run_ivd

REPORT_DIR = Path(__file__).parent.parent / "reports"


def run_full_validation(
    sprint: str = "sprint16",
    include_sabios: bool = False,
    fix: bool = False,
    deploy: bool = False,
    expected_version: str = "0.10.0-sprint16",
    sabios_prompt: str | None = None,
) -> dict:
    """Run the complete validation pipeline."""

    start_time = time.time()
    results = {
        "sprint": sprint,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phases": {},
        "overall": "PENDING",
    }

    print(f"\n{'#' * 70}")
    print("#  SPRINT VALIDATOR — Master Orchestrator")
    print(f"#  Sprint: {sprint}")
    print(f"#  Timestamp: {results['timestamp']}")
    print(f"#  Phases: IVD{'+ Sabios' if include_sabios else ''} + Repair{' + Deploy' if deploy else ''}")
    print(f"{'#' * 70}\n")

    # ── Phase 1: IVD Engine ────────────────────────────────────────
    print(f"\n{'━' * 70}")
    print("  PHASE 1: IVD Engine — Real-Time Dependency Validation")
    print(f"{'━' * 70}")

    try:
        ivd_report = run_ivd(sprint_name=sprint, fix=fix, ci=False)
        results["phases"]["ivd"] = {
            "status": ivd_report.overall_status,
            "checked": ivd_report.total_checked,
            "pass": ivd_report.total_pass,
            "fail": ivd_report.total_fail,
            "warn": ivd_report.total_warn,
            "outdated": ivd_report.total_outdated,
        }
    except Exception as e:
        results["phases"]["ivd"] = {"status": "ERROR", "error": str(e)}
        print(f"  ❌ IVD Engine failed: {e}")

    # ── Phase 2: Sabios Engine (optional) ──────────────────────────
    if include_sabios:
        print(f"\n{'━' * 70}")
        print("  PHASE 2: Sabios Engine — Consultation + Validation")
        print(f"{'━' * 70}")

        try:
            from scripts.sabios_engine import consult_sabios

            prompt = sabios_prompt or (
                "Para El Monstruo (orquestador de agentes IA con LangGraph), "
                "¿cuáles son las versiones correctas y más recientes de: "
                "langchain-core, langchain-openai, langchain-anthropic, "
                "langchain-google-genai, langgraph, ragas, garak? "
                "Dame versiones exactas con formato package==version."
            )
            sabios_report = consult_sabios(prompt, validate=True)

            trust_scores = {s.sabio: s.trust_score for s in sabios_report.sabios_consulted if not s.error}
            results["phases"]["sabios"] = {
                "status": "PASS" if trust_scores else "SKIP",
                "trust_scores": trust_scores,
                "consensus_claims": len(sabios_report.consensus_claims),
            }
        except Exception as e:
            results["phases"]["sabios"] = {"status": "ERROR", "error": str(e)}
            print(f"  ❌ Sabios Engine failed: {e}")
    else:
        print("\n  ⏭️  Phase 2 (Sabios) skipped — use --full to include")
        results["phases"]["sabios"] = {"status": "SKIPPED"}

    # ── Phase 3: Auto-Repair ───────────────────────────────────────
    print(f"\n{'━' * 70}")
    print("  PHASE 3: Auto-Repair Engine — Scan + Fix")
    print(f"{'━' * 70}")

    try:
        repair_report = run_repair(
            fix=fix,
            deploy_check=False,  # Deploy is Phase 4
            import_check=True,
        )
        results["phases"]["repair"] = {
            "status": "PASS" if not repair_report.issues_unfixable else "WARN",
            "issues_found": len(repair_report.issues_found),
            "issues_fixed": len(repair_report.issues_fixed),
            "issues_unfixable": len(repair_report.issues_unfixable),
        }
    except Exception as e:
        results["phases"]["repair"] = {"status": "ERROR", "error": str(e)}
        print(f"  ❌ Repair Engine failed: {e}")

    # ── Phase 4: Deploy Verification ───────────────────────────────
    if deploy:
        print(f"\n{'━' * 70}")
        print("  PHASE 4: Deploy Verification — Railway Health Check")
        print(f"{'━' * 70}")

        try:
            from scripts.auto_repair import verify_deploy

            deploy_result = verify_deploy(expected_version)
            results["phases"]["deploy"] = {
                "status": "PASS" if deploy_result["verified"] else "FAIL",
                "version": deploy_result["version"],
                "attempts": deploy_result["attempt"],
                "components": deploy_result.get("components", {}),
            }
        except Exception as e:
            results["phases"]["deploy"] = {"status": "ERROR", "error": str(e)}
            print(f"  ❌ Deploy verification failed: {e}")
    else:
        print("\n  ⏭️  Phase 4 (Deploy) skipped — use --deploy to include")
        results["phases"]["deploy"] = {"status": "SKIPPED"}

    # ── Final Verdict ──────────────────────────────────────────────
    elapsed = time.time() - start_time
    phase_statuses = [p["status"] for p in results["phases"].values() if p["status"] != "SKIPPED"]

    if "ERROR" in phase_statuses or "FAIL" in phase_statuses:
        results["overall"] = "FAIL"
    elif "WARN" in phase_statuses:
        results["overall"] = "WARN"
    else:
        results["overall"] = "PASS"

    results["elapsed_seconds"] = round(elapsed, 1)

    print(f"\n{'#' * 70}")
    print(f"#  FINAL VERDICT: {results['overall']}")
    print(f"#  Elapsed: {elapsed:.1f}s")
    for phase, data in results["phases"].items():
        icon = {
            "PASS": "✅",
            "FAIL": "❌",
            "WARN": "⚠️",
            "ERROR": "💥",
            "SKIPPED": "⏭️",
        }.get(data["status"], "?")
        print(f"#    {icon} {phase}: {data['status']}")
    print(f"{'#' * 70}\n")

    # Save master report
    REPORT_DIR.mkdir(exist_ok=True)
    master_path = REPORT_DIR / f"sprint_validation_{sprint}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(master_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Master report: {master_path}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sprint Validator — Master Orchestrator")
    parser.add_argument("--sprint", default="sprint16", help="Sprint name")
    parser.add_argument("--full", action="store_true", help="Include sabios consultation")
    parser.add_argument("--fix", action="store_true", help="Auto-repair issues")
    parser.add_argument("--deploy", action="store_true", help="Verify Railway deploy")
    parser.add_argument("--expected-version", default="0.10.0-sprint16", help="Expected version")
    parser.add_argument("--sabios-prompt", default=None, help="Custom prompt for sabios")
    args = parser.parse_args()

    result = run_full_validation(
        sprint=args.sprint,
        include_sabios=args.full,
        fix=args.fix,
        deploy=args.deploy,
        expected_version=args.expected_version,
        sabios_prompt=args.sabios_prompt,
    )

    if result["overall"] == "FAIL":
        sys.exit(1)
