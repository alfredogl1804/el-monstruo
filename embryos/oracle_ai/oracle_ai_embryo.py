"""
EMBRIÓN ORÁCULO DE IAs R0 — v0.2 (Grounding-Aware)
First autonomous embryo of El Monstruo.

Invocation: python3 embryos/oracle_ai/oracle_ai_embryo.py --run-once
"""
import os
import sys
import json
import yaml
import time
import datetime
import argparse

# Resolve base paths
EMBRYO_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(EMBRYO_DIR))
BRIDGE_DIR = os.path.join(PROJECT_ROOT, "bridge")
KS_PATH = os.path.join(BRIDGE_DIR, "reactor_vigilia_foundation", "reactor_heartbeat_r0", "scheduler", "scheduler_kill_switch.json")
STATE_PATH = os.path.join(EMBRYO_DIR, "oracle_ai_state.json")
SELF_TASKS_PATH = os.path.join(EMBRYO_DIR, "oracle_ai_self_tasks.yaml")
CONTRACT_PATH = os.path.join(EMBRYO_DIR, "oracle_ai_contract.yaml")
EVENT_LOG_DIR = os.path.join(BRIDGE_DIR, "embryos", "oracle_ai_r0")
EVENT_LOG_PATH = os.path.join(EVENT_LOG_DIR, "event_log.jsonl")
OUTPUT_DIR = os.path.join(EVENT_LOG_DIR, "outputs")

EMBRYO_ID = "oracle_ai_embryo_r0"


# ============================================================
# STATE MANAGEMENT
# ============================================================

def load_state():
    with open(STATE_PATH, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


# ============================================================
# SELF TASK QUEUE
# ============================================================

def load_self_tasks():
    with open(SELF_TASKS_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data.get("self_tasks", [])


def load_contract():
    with open(CONTRACT_PATH, "r") as f:
        return yaml.safe_load(f)


def choose_next_task(tasks, state):
    """
    Autonomous task selection based on priority scoring.
    priority_score = priority_base + freshness_bonus + compounding_value_score
                     - dependency_penalty - recent_repetition_penalty
    """
    scored = []
    task_history = state.get("task_history", [])
    last_task = state.get("last_task_executed")

    for task in tasks:
        score = task.get("priority_base", 5)
        score += task.get("freshness_bonus", 0)

        # Compounding value bonus
        cv = task.get("compounding_value", "LOW")
        if cv == "HIGH":
            score += 3
        elif cv == "MEDIUM":
            score += 1

        # Dependency penalty: if task requires prior output and no cycles done
        if state["total_cycles"] == 0 and "requires prior" in task.get("stop_condition", ""):
            score -= 10  # Heavy penalty — can't run without prior data

        # Recent repetition penalty
        if task["task_id"] == last_task:
            score -= 5

        scored.append((score, task))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored else None


# ============================================================
# DISPATCHER INTEGRATION
# ============================================================

def request_dispatcher_permission(task, contract):
    """
    Real Dispatcher check: verify action_class is in allowed list.
    Returns (decision, reason).
    """
    action_class = task.get("action_class", "UNKNOWN")
    allowed = contract.get("allowed_action_classes", [])
    forbidden = contract.get("forbidden_action_classes", [])

    if action_class in forbidden:
        return "DENY", f"Action class {action_class} is in forbidden list"
    if action_class in allowed:
        return "ALLOW", f"Action class {action_class} is in allowed list"
    return "DENY", f"Action class {action_class} not found in allowed list"


# ============================================================
# TASK EXECUTION
# ============================================================

def execute_task(task, contract):
    """
    Execute a single R0 task using one provider.
    Returns (success, output_data, cost).
    """
    providers = contract.get("providers_allowed", [])
    if not providers:
        return False, {"error": "No providers available"}, 0.0

    # Select cheapest provider (first in list = OpenAI gpt-4o-mini)
    provider = providers[0]
    provider_name = provider["name"].lower()
    model = provider["model"]

    prompt = _build_prompt_for_task(task)

    try:
        if provider_name == "openai":
            from openai import OpenAI
            base = os.environ.get("OPENAI_API_BASE") or None
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"]) if not base else OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=base)
            r = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1000)
            text = r.choices[0].message.content
            cost = (r.usage.prompt_tokens * 0.15 + r.usage.completion_tokens * 0.6) / 1_000_000
        elif provider_name == "anthropic":
            import anthropic
            client = anthropic.Anthropic()
            r = client.messages.create(model=model, max_tokens=1000, messages=[{"role": "user", "content": prompt}])
            text = r.content[0].text
            cost = (r.usage.input_tokens * 3 + r.usage.output_tokens * 15) / 1_000_000
        elif provider_name == "google":
            from google import genai
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            r = client.models.generate_content(model=model, contents=prompt)
            text = r.text
            cost = 0.0005
        elif provider_name == "xai":
            from openai import OpenAI as XAI
            client = XAI(api_key=os.environ["XAI_API_KEY"], base_url="https://api.x.ai/v1")
            r = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1000)
            text = r.choices[0].message.content
            cost = (r.usage.prompt_tokens * 0.3 + r.usage.completion_tokens * 0.5) / 1_000_000
        else:
            return False, {"error": f"Unknown provider: {provider_name}"}, 0.0

        # Budget check
        max_budget = contract.get("budget", {}).get("max_usd_per_cycle", 0.03)
        if cost > max_budget:
            return False, {"error": f"Cost ${cost:.4f} exceeds budget ${max_budget}"}, cost

        # Parse grounded output
        grounded_output = _parse_grounded_response(text, task)
        output = {
            "task_id": task["task_id"],
            "provider": provider_name,
            "model": model,
            "response_raw": text[:1000],
            "claims": grounded_output["claims"],
            "grounding_level": grounded_output["grounding_level"],
            "next_valid_action": grounded_output["next_valid_action"],
            "cost": cost
        }
        return True, output, cost

    except Exception as e:
        return False, {"error": str(e)[:200]}, 0.0


def _parse_grounded_response(text, task):
    """
    Parse the LLM response and extract grounded claims.
    The prompt instructs the LLM to return JSON with claims.
    If parsing fails, wrap the entire response as a single NEEDS_REAL_TIME_CHECK claim.
    """
    claims = []
    try:
        # Try to parse JSON from the response
        # Strip markdown code fences if present
        clean = text.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            clean = "\n".join(lines)

        parsed = json.loads(clean)

        # If it's a list, treat each item as a claim
        if isinstance(parsed, list):
            for i, item in enumerate(parsed):
                claim = _normalize_claim(item, i)
                claims.append(claim)
        elif isinstance(parsed, dict):
            # If it has a "claims" key, use that
            if "claims" in parsed:
                for i, item in enumerate(parsed["claims"]):
                    claim = _normalize_claim(item, i)
                    claims.append(claim)
            else:
                # Single object = single claim
                claims.append(_normalize_claim(parsed, 0))
    except (json.JSONDecodeError, KeyError, TypeError):
        # Fallback: wrap entire response as one claim
        claims.append({
            "claim_id": f"{task['task_id']}_fallback_0",
            "claim_text": text[:300],
            "claim_type": "analytical",
            "evidence_status": "NEEDS_REAL_TIME_CHECK",
            "source_ref": "none",
            "freshness_required": True,
            "confidence": 0.4
        })

    # Calculate grounding level
    grounding_level = _calculate_grounding_level(claims)
    next_action = "CANDIDATE_READY_FOR_T1" if grounding_level >= 8 else "REQUIRES_T1_REVIEW"

    return {
        "claims": claims,
        "grounding_level": grounding_level,
        "next_valid_action": next_action
    }


def _normalize_claim(item, index):
    """Normalize a claim dict to ensure all mandatory fields exist with proper grounding."""
    claim_text = item.get("claim_text") or item.get("capability_name") or item.get("capability") or item.get("application") or item.get("title") or str(item)[:200]
    claim_type = item.get("claim_type", "factual")

    # Determine evidence status
    evidence_status = item.get("evidence_status", "")
    if not evidence_status:
        # Auto-classify: if it mentions dates, models, prices → NEEDS_REAL_TIME_CHECK
        indicators = ["release", "date", "price", "endpoint", "available", "launched", "2025", "2026", "v1", "v2", "api"]
        text_lower = claim_text.lower()
        if any(ind in text_lower for ind in indicators):
            evidence_status = "NEEDS_REAL_TIME_CHECK"
        else:
            evidence_status = "HYPOTHESIS"

    return {
        "claim_id": item.get("claim_id", f"claim_{index}"),
        "claim_text": claim_text[:300],
        "claim_type": claim_type,
        "evidence_status": evidence_status,
        "source_ref": item.get("source_ref", "none"),
        "freshness_required": evidence_status in ("NEEDS_REAL_TIME_CHECK", "NO_SOURCE"),
        "confidence": item.get("confidence", 0.5)
    }


def _calculate_grounding_level(claims):
    """
    Calculate grounding level (1-10) based on evidence statuses.
    VERIFIED_LOCAL/VERIFIED_PROVIDER = 10 points
    NEEDS_REAL_TIME_CHECK = 6 points (honest about uncertainty)
    HYPOTHESIS = 5 points (clearly labeled)
    CANDIDATE_ONLY = 4 points
    NO_SOURCE = 2 points (bad)
    """
    if not claims:
        return 5

    scores = {
        "VERIFIED_LOCAL": 10,
        "VERIFIED_PROVIDER": 10,
        "NEEDS_REAL_TIME_CHECK": 6,
        "HYPOTHESIS": 5,
        "CANDIDATE_ONLY": 4,
        "NO_SOURCE": 2
    }

    total = sum(scores.get(c.get("evidence_status", "NO_SOURCE"), 2) for c in claims)
    avg = total / len(claims)
    return round(avg)


# ============================================================
# PROMPTS (v0.2 — Grounding-Aware)
# ============================================================

def _build_prompt_for_task(task):
    """Build a grounding-aware prompt for the chosen task."""
    grounding_instruction = (
        "\n\nIMPORTANT GROUNDING RULES:\n"
        "For EACH item in your response, include these fields:\n"
        "- claim_id: unique identifier\n"
        "- claim_text: the factual statement\n"
        "- claim_type: 'factual' | 'analytical' | 'hypothetical'\n"
        "- evidence_status: one of VERIFIED_LOCAL, VERIFIED_PROVIDER, NEEDS_REAL_TIME_CHECK, NO_SOURCE, HYPOTHESIS, CANDIDATE_ONLY\n"
        "- source_ref: source URL or 'none'\n"
        "- confidence: 0.0 to 1.0\n\n"
        "Rules:\n"
        "- If you mention dates, models, prices, endpoints, availability → mark as NEEDS_REAL_TIME_CHECK\n"
        "- If you are speculating or proposing → mark as HYPOTHESIS\n"
        "- If you have no source → mark as NO_SOURCE\n"
        "- NEVER present NO_SOURCE or HYPOTHESIS as verified fact\n"
        "Respond in JSON array format.\n"
    )

    prompts = {
        "detect_new_ai_capability_candidates": (
            "You are the Oracle AI Embryo R0 of El Monstruo. Your task: detect_new_ai_capability_candidates. "
            "Identify 3-5 emerging AI capabilities released in the last 30 days that could benefit an autonomous "
            "AI orchestrator system. For each, provide: capability_name, provider, release_date_approx, "
            "potential_power_gain (1-10), integration_complexity (LOW/MED/HIGH)."
            + grounding_instruction
        ),
        "map_capability_to_application": (
            "You are the Oracle AI Embryo R0. Task: map_capability_to_application. "
            "Given recent AI capabilities (multimodal reasoning, code generation, real-time search, voice synthesis, "
            "video understanding), map each to a concrete application within an AI orchestrator ecosystem."
            + grounding_instruction
        ),
        "rank_application_by_power_gain": (
            "You are the Oracle AI Embryo R0. Task: rank_application_by_power_gain. "
            "Rank these AI applications by power gain for an autonomous orchestrator: "
            "real-time research validation, multi-model consensus, autonomous sprint planning, "
            "provider health monitoring, self-audit loops."
            + grounding_instruction
        ),
        "generate_sprint_candidate": (
            "You are the Oracle AI Embryo R0. Task: generate_sprint_candidate. "
            "Generate a structured sprint candidate for the highest-value capability you can identify. "
            "Format: {sprint_id, title, objective, deliverables[], estimated_cycles, risk, value_score, "
            "dependencies[], action_class}. Must be R0 (no production, no deploy, no DB writes)."
            + grounding_instruction
        ),
        "audit_previous_oracle_outputs_for_low_value": (
            "You are the Oracle AI Embryo R0. Task: audit_previous_oracle_outputs_for_low_value. "
            "Audit the oracle design itself. "
            "Score the current self-task queue design (1-10) on: coverage, actionability, compounding value, "
            "risk management, autonomy level. Suggest 1-2 improvements."
            + grounding_instruction
        ),
    }
    return prompts.get(task["task_id"], f"Execute task: {task['task_id']}. Respond in JSON." + grounding_instruction)


# ============================================================
# EVENT LOG
# ============================================================

def write_event(event_type, payload):
    """Append event to the embryo's event log."""
    os.makedirs(os.path.dirname(EVENT_LOG_PATH), exist_ok=True)
    event = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "embryo_id": EMBRYO_ID,
        "event_type": event_type,
        "payload": payload
    }
    with open(EVENT_LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")
    return event


# ============================================================
# OUTPUT PRODUCTION
# ============================================================

def produce_report(task, output_data, dispatcher_decision, cost):
    """Save the cycle output as a report artifact."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    filename = f"{task['task_id']}_{ts}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)

    report = {
        "embryo_id": EMBRYO_ID,
        "task_id": task["task_id"],
        "action_class": task["action_class"],
        "dispatcher_decision": dispatcher_decision,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "cost_usd": cost,
        "output": output_data,
        "grounding_level": output_data.get("grounding_level", 0),
        "next_valid_action": output_data.get("next_valid_action", "REQUIRES_T1_REVIEW")
    }

    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)

    return filepath


# ============================================================
# KILL SWITCH
# ============================================================

def check_kill_switch():
    """Returns True if kill-switch is active (should abort)."""
    if not os.path.exists(KS_PATH):
        return False
    with open(KS_PATH, "r") as f:
        ks = json.load(f)
    return ks.get("active", False)


# ============================================================
# RUN ONCE — THE AUTONOMOUS LOOP
# ============================================================
def run_once():
    """
    Single autonomous cycle. The embryo:
    1. Checks kill-switch
    2. Loads its own state
    3. Loads self-task queue
    4. Chooses a task by its own scoring criteria
    5. Requests Dispatcher permission
    6. If DENY: logs and aborts
    7. If ALLOW: executes the task
    8. Produces output artifact (with grounding fields)
    9. Updates its own state
    10. Writes event log
    11. Returns verdict
    """
    print(f"{'='*60}")
    print(f"EMBRYO: {EMBRYO_ID} — run_once() [v0.2 Grounding-Aware]")
    print(f"{'='*60}")
    # 1. Kill-switch
    if check_kill_switch():
        print("  [ABORT] Kill-switch is ACTIVE.")
        write_event("EMBRYO_ABORTED", {"reason": "kill_switch_active"})
        return {"verdict": "ABORTED", "reason": "kill_switch_active"}
    # 2. Load state
    state = load_state()
    print(f"  State loaded. Cycles: {state['total_cycles']}")
    # 3. Load self-tasks
    tasks = load_self_tasks()
    print(f"  Self-tasks loaded: {len(tasks)}")
    # 4. Load contract
    contract = load_contract()
    # 5. Choose task (AUTONOMOUS DECISION)
    chosen_task = choose_next_task(tasks, state)
    if not chosen_task:
        print("  [ABORT] No viable task found.")
        write_event("EMBRYO_NO_TASK", {"reason": "no_viable_task"})
        return {"verdict": "NO_TASK", "reason": "no_viable_task"}
    print(f"  Chosen task: {chosen_task['task_id']} (class: {chosen_task['action_class']})")
    # 6. Request Dispatcher permission
    write_event("DISPATCHER_REQUEST", {"task_id": chosen_task["task_id"], "action_class": chosen_task["action_class"]})
    decision, reason = request_dispatcher_permission(chosen_task, contract)
    write_event(f"DISPATCHER_{decision}", {"task_id": chosen_task["task_id"], "reason": reason})
    print(f"  Dispatcher: {decision} — {reason}")
    # 7. If DENY, abort
    if decision == "DENY":
        write_event("EMBRYO_TASK_ABORTED", {"task_id": chosen_task["task_id"], "reason": "dispatcher_deny"})
        state["last_task_executed"] = chosen_task["task_id"]
        state["last_task_result"] = "DENIED"
        save_state(state)
        return {"verdict": "DENIED", "task": chosen_task["task_id"], "reason": reason}
    # 8. Execute task
    write_event("EMBRYO_TASK_STARTED", {"task_id": chosen_task["task_id"]})
    print(f"  Executing task...")
    success, output_data, cost = execute_task(chosen_task, contract)
    if not success:
        write_event("EMBRYO_TASK_ABORTED", {"task_id": chosen_task["task_id"], "error": output_data.get("error", "unknown")})
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        state["last_task_executed"] = chosen_task["task_id"]
        state["last_task_result"] = "FAILED"
        save_state(state)
        print(f"  [FAILED] {output_data.get('error', 'unknown')}")
        return {"verdict": "FAILED", "task": chosen_task["task_id"], "error": output_data.get("error")}
    # 9. Produce output artifact
    report_path = produce_report(chosen_task, output_data, decision, cost)
    print(f"  Output: {report_path}")
    print(f"  Grounding Level: {output_data.get('grounding_level', 'N/A')}/10")
    print(f"  Claims: {len(output_data.get('claims', []))}")
    # 10. Update state
    state["total_cycles"] += 1
    state["last_cycle_timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    state["last_task_executed"] = chosen_task["task_id"]
    state["last_task_result"] = "SUCCESS"
    state["total_cost_usd"] = round(state.get("total_cost_usd", 0) + cost, 6)
    state["consecutive_failures"] = 0
    state["status"] = "IDLE"
    history_entry = {"task_id": chosen_task["task_id"], "timestamp": state["last_cycle_timestamp"], "result": "SUCCESS", "cost": cost, "grounding_level": output_data.get("grounding_level", 0)}
    state.setdefault("task_history", []).append(history_entry)
    save_state(state)
    # 11. Write completion event
    write_event("EMBRYO_TASK_COMPLETED", {
        "task_id": chosen_task["task_id"],
        "cost_usd": cost,
        "output_path": report_path,
        "grounding_level": output_data.get("grounding_level", 0),
        "claims_count": len(output_data.get("claims", []))
    })
    print(f"  [SUCCESS] Cost: ${cost:.6f}")
    print(f"{'='*60}")
    return {
        "verdict": "AUTONOMOUS_CYCLE_COMPLETE",
        "task": chosen_task["task_id"],
        "action_class": chosen_task["action_class"],
        "dispatcher": decision,
        "cost": cost,
        "output_path": report_path,
        "grounding_level": output_data.get("grounding_level", 0),
        "claims_count": len(output_data.get("claims", []))
    }


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Oracle AI Embryo R0 v0.2 (Grounding-Aware)")
    parser.add_argument("--run-once", action="store_true", help="Execute a single autonomous cycle")
    args = parser.parse_args()
    if args.run_once:
        result = run_once()
        print(f"\nResult: {json.dumps(result, indent=2)}")
    else:
        print("Usage: python3 oracle_ai_embryo.py --run-once")
        sys.exit(1)
