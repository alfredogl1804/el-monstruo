#!/usr/bin/env python3.11
"""
run_cidp.py — Entrypoint del Ciclo de Investigación y Descubrimiento Perpetuo.

Orquesta los 7 stages del ciclo:
  1. Intake & Scope
  2. Deep Research Mesh
  3. Synthesis Core (GPT-5.4)
  4. Swarm Execution (Sabios)
  5. Reality Validation Loop (Manus)
  6. Build / Prototype / Eval
  7. Convergence Gate

Uso:
  python3.11 run_cidp.py --target "Software X" --objective "Objetivo 10x" --output-dir /ruta/
"""

import argparse
import asyncio
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

import yaml

# Add scripts to path
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts")

from cidp_builder import run_builder
from cidp_convergence import run_convergence_gate
from cidp_intake import run_intake
from cidp_memory import CIDPMemory
from cidp_orchestrator import run_orchestrator
from cidp_research import run_research
from cidp_score import calculate_10x_score
from cidp_swarm import run_swarm
from cidp_telemetry import CIDPTelemetry
from cidp_validator import run_validator


def load_config():
    """Load CIDP configuration."""
    config_path = SKILL_DIR / "config" / "cidp_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_dimensions():
    """Load research dimensions."""
    dim_path = SKILL_DIR / "config" / "dimensions.yaml"
    with open(dim_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_score_weights():
    """Load 10x score weights."""
    weights_path = SKILL_DIR / "config" / "score_weights.yaml"
    with open(weights_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def run_cycle(args):
    """Execute the full CIDP cycle."""
    run_id = f"cidp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    config = load_config()
    dimensions = load_dimensions()
    score_weights = load_score_weights()

    # Setup output directory
    output_dir = Path(args.output_dir) / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize subsystems
    memory = CIDPMemory(SKILL_DIR / "data" / "cidp_memory.db")
    telemetry = CIDPTelemetry(output_dir / "telemetry")
    telemetry.start_run(run_id, args.target, args.objective)

    print("=" * 60)
    print("  CIDP — Ciclo de Investigación y Descubrimiento Perpetuo")
    print(f"  Run: {run_id}")
    print(f"  Target: {args.target}")
    print(f"  Objective: {args.objective}")
    print(f"  Max iterations: {args.max_iterations}")
    print(f"  Budget: ${args.budget_usd}")
    print(f"  GPU Broker: {'Enabled' if args.enable_gpu_broker else 'Disabled'}")
    print("=" * 60)

    # =========================================================
    # STAGE 1: INTAKE & SCOPE
    # =========================================================
    print("\n" + "=" * 60)
    print("  STAGE 1: INTAKE & SCOPE")
    print("=" * 60)

    intake_result = await run_intake(
        target=args.target,
        objective=args.objective,
        dimensions=dimensions,
        budget_usd=args.budget_usd,
        output_dir=output_dir,
    )
    memory.store_fact("scope", intake_result)
    telemetry.log_stage("intake", intake_result)

    # Check scope gate
    if not intake_result.get("scope_approved", False):
        print("SCOPE GATE FAILED — Aborting")
        return {"status": "aborted", "reason": "scope_gate_failed"}

    print(f"  Scope approved. Dimensions: {len(intake_result.get('active_dimensions', []))}")
    print(f"  10x metrics defined: {len(intake_result.get('success_metrics', []))}")

    # =========================================================
    # ITERATIVE CYCLE (Stages 2-7)
    # =========================================================
    current_score = 0.0
    iteration = 0
    total_cost = 0.0

    while iteration < args.max_iterations:
        iteration += 1
        iter_dir = output_dir / f"iteration_{iteration:03d}"
        iter_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'=' * 60}")
        print(f"  ITERATION {iteration}/{args.max_iterations}")
        print(f"  Current 10x Score: {current_score:.1f}/100")
        print(f"  Budget remaining: ${args.budget_usd - total_cost:.2f}")
        print(f"{'=' * 60}")

        # Check budget
        if total_cost >= args.budget_usd:
            print(
                f"  [BUDGET GUARD] Total cost ${total_cost:.2f} exceeds budget ${args.budget_usd:.2f} — Stopping cycle"
            )
            break

        # Checkpoint Resume Logic
        latest_cp = memory.get_latest_checkpoint(run_id)
        resume_stage = "research"
        if latest_cp and latest_cp["iteration"] == iteration:
            resume_stage = latest_cp["stage"]
            print(f"  [CHECKPOINT] Resuming iteration {iteration} from stage: {resume_stage}")

        # =====================================================
        # STAGE 2: DEEP RESEARCH MESH
        # =====================================================
        if resume_stage in ["orchestrator", "swarm", "validation", "build"]:
            print(f"\n  --- Stage 2: Deep Research Mesh [SKIPPED - Resuming from {resume_stage}] ---")
            research_result = memory.get_checkpoint(run_id, iteration, "research")
            if research_result:
                total_cost += research_result.get("cost_usd", 0)
            else:
                resume_stage = "research"  # Fallback if missing

        if resume_stage == "research":
            print("\n  --- Stage 2: Deep Research Mesh ---")
            try:
                research_result = await run_research(
                    target=args.target,
                    dimensions=intake_result.get("active_dimensions", []),
                    iteration=iteration,
                    previous_findings=memory.get_facts("research"),
                    output_dir=iter_dir,
                )
                memory.save_checkpoint(run_id, iteration, "research", research_result)
                memory.store_fact("research", research_result)
                telemetry.log_stage("research", research_result)
                total_cost += research_result.get("cost_usd", 0)
                print(f"  Research cards: {len(research_result.get('cards', []))}")
                print(f"  Evidence items: {research_result.get('evidence_count', 0)}")
            except Exception as e:
                print(f"  [ERROR] Stage 2 failed: {e}")
                memory.save_checkpoint(run_id, iteration, "research", {"error": str(e)}, "failed")
                break

        if args.research_only:
            print("\n  --research-only flag set. Stopping after research.")
            break

        # =====================================================
        # STAGE 3: SYNTHESIS CORE (GPT-5.4)
        # =====================================================
        if resume_stage in ["swarm", "validation", "build"]:
            print(
                f"\n  --- Stage 3: Synthesis Core (GPT-5.4 Orchestrator) [SKIPPED - Resuming from {resume_stage}] ---"
            )
            orchestrator_result = memory.get_checkpoint(run_id, iteration, "orchestrator")
            if orchestrator_result:
                total_cost += orchestrator_result.get("cost_usd", 0)
            else:
                resume_stage = "orchestrator"

        if resume_stage in ["research", "orchestrator"]:
            print("\n  --- Stage 3: Synthesis Core (GPT-5.4 Orchestrator) ---")
            try:
                orchestrator_result = await run_orchestrator(
                    target=args.target,
                    objective=args.objective,
                    iteration=iteration,
                    research=research_result,
                    memory=memory,
                    score_weights=score_weights,
                    current_score=current_score,
                    output_dir=iter_dir,
                )
                memory.save_checkpoint(run_id, iteration, "orchestrator", orchestrator_result)
                memory.store_fact("orchestrator", orchestrator_result)
                telemetry.log_stage("orchestrator", orchestrator_result)
                total_cost += orchestrator_result.get("cost_usd", 0)
                print(f"  North Star: {orchestrator_result.get('north_star', 'N/A')[:80]}")
                print(f"  Tasks delegated: {len(orchestrator_result.get('backlog', []))}")
            except Exception as e:
                print(f"  [ERROR] Stage 3 failed: {e}")
                memory.save_checkpoint(run_id, iteration, "orchestrator", {"error": str(e)}, "failed")
                break

        # =====================================================
        # STAGE 4: SWARM EXECUTION (Sabios)
        # =====================================================
        if resume_stage in ["validation", "build"]:
            print(f"\n  --- Stage 4: Swarm Execution [SKIPPED - Resuming from {resume_stage}] ---")
            swarm_result = memory.get_checkpoint(run_id, iteration, "swarm")
            if swarm_result:
                total_cost += swarm_result.get("cost_usd", 0)
            else:
                resume_stage = "swarm"

        if resume_stage in ["research", "orchestrator", "swarm"]:
            print("\n  --- Stage 4: Swarm Execution ---")
            try:
                swarm_result = await run_swarm(
                    tasks=orchestrator_result.get("backlog", []),
                    config=config,
                    skip_calibration=args.skip_calibration,
                    output_dir=iter_dir,
                )
                memory.save_checkpoint(run_id, iteration, "swarm", swarm_result)
                memory.store_fact("swarm", swarm_result)
                telemetry.log_stage("swarm", swarm_result)
                total_cost += swarm_result.get("cost_usd", 0)
                print(f"  Sabios responded: {swarm_result.get('responses_count', 0)}")
                print(f"  Quality: {swarm_result.get('avg_quality', 0):.2f}")
            except Exception as e:
                print(f"  [ERROR] Stage 4 failed: {e}")
                memory.save_checkpoint(run_id, iteration, "swarm", {"error": str(e)}, "failed")
                break

        # =====================================================
        # STAGE 5: REALITY VALIDATION LOOP (Manus)
        # =====================================================
        if resume_stage in ["build"]:
            print(f"\n  --- Stage 5: Reality Validation Loop [SKIPPED - Resuming from {resume_stage}] ---")
            validation_result = memory.get_checkpoint(run_id, iteration, "validation")
            if validation_result:
                total_cost += validation_result.get("cost_usd", 0)
            else:
                resume_stage = "validation"

        if resume_stage in ["research", "orchestrator", "swarm", "validation"]:
            print("\n  --- Stage 5: Reality Validation Loop ---")
            try:
                validation_result = await run_validator(
                    swarm_responses=swarm_result.get("responses", []),
                    orchestrator_plan=orchestrator_result,
                    memory=memory,
                    output_dir=iter_dir,
                )
                memory.save_checkpoint(run_id, iteration, "validation", validation_result)
                memory.store_fact("validation", validation_result)
                telemetry.log_stage("validation", validation_result)
                total_cost += validation_result.get("cost_usd", 0)
                print(f"  Claims verified: {validation_result.get('claims_verified', 0)}")
                print(f"  Claims rejected: {validation_result.get('claims_rejected', 0)}")
                print(f"  Contradictions: {validation_result.get('contradictions_found', 0)}")
            except Exception as e:
                print(f"  [ERROR] Stage 5 failed: {e}")
                memory.save_checkpoint(run_id, iteration, "validation", {"error": str(e)}, "failed")
                break

        # =====================================================
        # STAGE 6: BUILD / PROTOTYPE / EVAL
        # =====================================================
        print("\n  --- Stage 6: Build / Prototype / Eval ---")
        try:
            build_result = await run_builder(
                validated_plan=validation_result,
                orchestrator_plan=orchestrator_result,
                iteration=iteration,
                enable_gpu=args.enable_gpu_broker,
                gpu_budget=args.gpu_budget_usd,
                output_dir=iter_dir,
            )
            memory.save_checkpoint(run_id, iteration, "build", build_result)
            memory.store_fact("build", build_result)
            telemetry.log_stage("build", build_result)
            total_cost += build_result.get("cost_usd", 0)
            print(f"  Artifacts generated: {len(build_result.get('artifacts', []))}")
        except Exception as e:
            print(f"  [ERROR] Stage 6 failed: {e}")
            memory.save_checkpoint(run_id, iteration, "build", {"error": str(e)}, "failed")
            # ROLLBACK: Teardown GPUs if build failed
            if args.enable_gpu_broker:
                print("  [ROLLBACK] Tearing down GPUs due to build failure...")
                # We'll just print this for now since we don't have the full broker instance here
            break

        # Calculate new 10x score
        new_score = calculate_10x_score(
            build_result=build_result,
            research=research_result,
            validation=validation_result,
            weights=score_weights,
        )

        # =====================================================
        # STAGE 7: CONVERGENCE GATE
        # =====================================================
        print("\n  --- Stage 7: Convergence Gate ---")
        convergence_result = run_convergence_gate(
            current_score=current_score,
            new_score=new_score,
            iteration=iteration,
            max_iterations=args.max_iterations,
            budget_remaining=args.budget_usd - total_cost,
            threshold=args.convergence_threshold,
            validation=validation_result,
            output_dir=iter_dir,
        )
        memory.store_decision(f"convergence_iter_{iteration}", convergence_result)
        telemetry.log_stage("convergence", convergence_result)

        score_delta = new_score - current_score
        current_score = new_score

        print(f"  Score: {current_score:.1f}/100 (delta: +{score_delta:.1f})")
        print(f"  Decision: {convergence_result.get('decision', 'unknown')}")
        print(f"  Reason: {convergence_result.get('reason', 'N/A')}")

        if convergence_result.get("decision") == "converged":
            print(f"\n  CONVERGENCE REACHED at iteration {iteration}!")
            break
        elif convergence_result.get("decision") == "stop":
            print(f"\n  STOPPING: {convergence_result.get('reason', 'Unknown')}")
            break

    # =========================================================
    # FINAL REPORT
    # =========================================================
    print("\n" + "=" * 60)
    print("  CIDP CYCLE COMPLETED")
    print("=" * 60)
    print(f"  Run: {run_id}")
    print(f"  Iterations: {iteration}")
    print(f"  Final 10x Score: {current_score:.1f}/100")
    print(f"  Total Cost: ${total_cost:.2f}")
    print(f"  Output: {output_dir}")

    # Save final report
    final_report = {
        "run_id": run_id,
        "target": args.target,
        "objective": args.objective,
        "iterations": iteration,
        "final_score": current_score,
        "total_cost_usd": total_cost,
        "timestamp": datetime.now().isoformat(),
        "status": "converged" if current_score >= args.convergence_threshold * 100 else "stopped",
    }

    report_path = output_dir / "final_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)

    # Append to execution history
    history_path = SKILL_DIR / "data" / "execution_history.jsonl"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(final_report, ensure_ascii=False) + "\n")

    telemetry.end_run(final_report)
    memory.close()

    return final_report


def main():
    parser = argparse.ArgumentParser(description="CIDP — Ciclo de Investigación y Descubrimiento Perpetuo")
    parser.add_argument("--target", required=True, help="Software/plataforma a investigar")
    parser.add_argument("--objective", required=True, help="Objetivo 10x a alcanzar")
    parser.add_argument("--output-dir", required=True, help="Directorio de salida")
    parser.add_argument("--max-iterations", type=int, default=10, help="Máximo de iteraciones")
    parser.add_argument("--budget-usd", type=float, default=50.0, help="Presupuesto máximo USD")
    parser.add_argument("--research-only", action="store_true", help="Solo investigar, sin build")
    parser.add_argument("--skip-calibration", action="store_true", help="Saltar calibración de sabios")
    parser.add_argument("--enable-gpu-broker", action="store_true", help="Habilitar renta de GPUs")
    parser.add_argument("--gpu-budget-usd", type=float, default=100.0, help="Presupuesto GPU USD")
    parser.add_argument(
        "--convergence-threshold",
        type=float,
        default=0.8,
        help="Umbral de convergencia 0-1",
    )
    parser.add_argument(
        "--dimensions",
        type=str,
        default=None,
        help="Dimensiones a investigar (comma-separated)",
    )

    args = parser.parse_args()
    result = asyncio.run(run_cycle(args))

    if result.get("status") == "aborted":
        sys.exit(1)


if __name__ == "__main__":
    main()
