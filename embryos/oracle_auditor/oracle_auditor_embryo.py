#!/usr/bin/env python3
"""
EMBRIÓN AUDITOR DEL ORÁCULO DE IAs R0
Second autonomous embryo of El Monstruo — the auditor half of the bicéfalo pair.

Audits outputs produced by oracle_ai_embryo_r0.
Does NOT produce capability/application/sprint candidates.
Only evaluates, scores, and verdicts.

Invocation: python3 embryos/oracle_auditor/oracle_auditor_embryo.py --run-once
"""
import os
import sys
import json
import yaml
import time
import datetime
import argparse
import glob

# Resolve base paths
EMBRYO_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(EMBRYO_DIR))
BRIDGE_DIR = os.path.join(PROJECT_ROOT, "bridge")
KS_PATH = os.path.join(BRIDGE_DIR, "reactor_vigilia_foundation", "reactor_heartbeat_r0", "scheduler", "scheduler_kill_switch.json")
STATE_PATH = os.path.join(EMBRYO_DIR, "oracle_auditor_state.json")
SELF_TASKS_PATH = os.path.join(EMBRYO_DIR, "oracle_auditor_self_tasks.yaml")
CONTRACT_PATH = os.path.join(EMBRYO_DIR, "oracle_auditor_contract.yaml")
EVENT_LOG_DIR = os.path.join(BRIDGE_DIR, "embryos", "oracle_pair_r0")
EVENT_LOG_PATH = os.path.join(EVENT_LOG_DIR, "auditor_event_log.jsonl")
OUTPUT_DIR = os.path.join(EVENT_LOG_DIR, "auditor_outputs")

# Oracle output directory (what we audit)
ORACLE_OUTPUT_DIR = os.path.join(BRIDGE_DIR, "embryos", "oracle_ai_r0", "outputs")

EMBRYO_ID = "oracle_auditor_embryo_r0"


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
    Autonomous task selection. Same scoring as Oracle but with auditor-specific logic.
    """
    scored = []
    last_task = state.get("last_task_executed")

    for task in tasks:
        score = task.get("priority_base", 5)
        score += task.get("freshness_bonus", 0)

        cv = task.get("compounding_value", "LOW")
        if cv == "HIGH":
            score += 3
        elif cv == "MEDIUM":
            score += 1

        # Dependency: if requires prior audit and no cycles done
        if state["total_cycles"] == 0 and "requires prior" in task.get("stop_condition", ""):
            score -= 10

        # Check if oracle output exists (required for most tasks)
        if "No oracle output available" in task.get("stop_condition", ""):
            oracle_outputs = get_oracle_outputs()
            if not oracle_outputs:
                score -= 20  # Can't audit nothing

        # Repetition penalty
        if task["task_id"] == last_task:
            score -= 5

        scored.append((score, task))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored else None


def get_oracle_outputs():
    """Get list of oracle output files sorted by modification time (newest first)."""
    if not os.path.exists(ORACLE_OUTPUT_DIR):
        return []
    files = glob.glob(os.path.join(ORACLE_OUTPUT_DIR, "*.json"))
    files.sort(key=os.path.getmtime, reverse=True)
    return files


def get_latest_oracle_output():
    """Get the most recent oracle output for auditing."""
    outputs = get_oracle_outputs()
    if not outputs:
        return None, None
    latest = outputs[0]
    with open(latest, "r") as f:
        data = json.load(f)
    return latest, data


# ============================================================
# DISPATCHER INTEGRATION
# ============================================================

def request_dispatcher_permission(task, contract):
    """
    Real Dispatcher check: verify action_class is in allowed list.
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

def execute_task(task, contract, oracle_output_path, oracle_output_data):
    """
    Execute an audit task using one provider.
    """
    providers = contract.get("providers_allowed", [])
    if not providers:
        return False, {"error": "No providers available"}, 0.0

    provider = providers[0]
    provider_name = provider["name"].lower()
    model = provider["model"]

    prompt = _build_audit_prompt(task, oracle_output_path, oracle_output_data)

    try:
        if provider_name == "openai":
            from openai import OpenAI
            base = os.environ.get("OPENAI_API_BASE") or None
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"]) if not base else OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=base)
            r = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=800)
            text = r.choices[0].message.content
            cost = (r.usage.prompt_tokens * 0.15 + r.usage.completion_tokens * 0.6) / 1_000_000
        elif provider_name == "anthropic":
            import anthropic
            client = anthropic.Anthropic()
            r = client.messages.create(model=model, max_tokens=800, messages=[{"role": "user", "content": prompt}])
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
            r = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=800)
            text = r.choices[0].message.content
            cost = (r.usage.prompt_tokens * 0.3 + r.usage.completion_tokens * 0.5) / 1_000_000
        else:
            return False, {"error": f"Unknown provider: {provider_name}"}, 0.0

        max_budget = contract.get("budget", {}).get("max_usd_per_cycle", 0.03)
        if cost > max_budget:
            return False, {"error": f"Cost ${cost:.4f} exceeds budget ${max_budget}"}, cost

        output = {
            "task_id": task["task_id"],
            "auditor_id": EMBRYO_ID,
            "target_embryo": "oracle_ai_embryo_r0",
            "oracle_output_audited": oracle_output_path,
            "provider": provider_name,
            "model": model,
            "audit_response": text[:1000],
            "cost": cost
        }
        return True, output, cost

    except Exception as e:
        return False, {"error": str(e)[:200]}, 0.0


def _build_audit_prompt(task, oracle_output_path, oracle_output_data):
    """Build audit prompt based on task type and oracle output."""
    oracle_content = json.dumps(oracle_output_data, indent=2)[:2000] if oracle_output_data else "NO OUTPUT AVAILABLE"

    prompts = {
        "audit_oracle_latest_output": (
            f"You are the Oracle Auditor Embryo R0 of El Monstruo. Your role: audit the output of oracle_ai_embryo_r0.\n\n"
            f"Oracle output to audit (from {oracle_output_path}):\n```json\n{oracle_content}\n```\n\n"
            f"Evaluate on 5 dimensions (score 1-10 each):\n"
            f"1. hallucination_risk: Are there fabricated claims, non-existent APIs, wrong dates?\n"
            f"2. value_score: Is this output actionable and useful for the Monstruo ecosystem?\n"
            f"3. scope_compliance: Does it stay within R0 boundaries (no R1 proposals)?\n"
            f"4. factual_grounding: Are the claims verifiable?\n"
            f"5. actionability: Can T1 act on this immediately?\n\n"
            f"Respond in JSON: {{\"verdict\": \"PASS|PARTIAL|FAIL\", \"scores\": {{...}}, \"flags\": [...], \"recommendation\": \"...\"}}"
        ),
        "score_oracle_sprint_candidate": (
            f"You are the Oracle Auditor Embryo R0. Task: score a sprint candidate.\n\n"
            f"Oracle output:\n```json\n{oracle_content}\n```\n\n"
            f"Score on: value (1-10), risk (1-10), feasibility (1-10), R0_compliance (YES/NO), actionability (1-10).\n"
            f"Respond in JSON: {{\"verdict\": \"PASS|PARTIAL|FAIL\", \"scores\": {{...}}, \"blocked_reason\": null|\"...\"}}"
        ),
        "detect_oracle_hallucination": (
            f"You are the Oracle Auditor Embryo R0. Task: detect hallucinations.\n\n"
            f"Oracle output:\n```json\n{oracle_content}\n```\n\n"
            f"Check for: non-existent APIs, wrong model names, fabricated release dates, impossible integrations.\n"
            f"Respond in JSON: {{\"hallucinations_found\": [...], \"confidence\": 0-1, \"verdict\": \"CLEAN|SUSPICIOUS|HALLUCINATED\"}}"
        ),
        "verify_oracle_scope_compliance": (
            f"You are the Oracle Auditor Embryo R0. Task: verify R0 scope compliance.\n\n"
            f"Oracle output:\n```json\n{oracle_content}\n```\n\n"
            f"Verify: no R1 proposals, no production deployments, no DB writes, no secret access.\n"
            f"Respond in JSON: {{\"r0_compliant\": true|false, \"violations\": [...], \"verdict\": \"COMPLIANT|VIOLATION\"}}"
        ),
        "generate_audit_summary_for_t1": (
            f"You are the Oracle Auditor Embryo R0. Task: generate audit summary for T1.\n\n"
            f"Oracle output:\n```json\n{oracle_content}\n```\n\n"
            f"Produce: overall verdict, risk flags, recommended action, blocked items.\n"
            f"Respond in JSON: {{\"overall_verdict\": \"PASS|PARTIAL|FAIL\", \"risk_flags\": [...], \"recommended_action\": \"...\", \"blocked_items\": [...]}}"
        ),
    }
    return prompts.get(task["task_id"], f"Audit this oracle output: {oracle_content}")


# ============================================================
# EVENT LOG
# ============================================================

def write_event(event_type, payload):
    """Append event to the auditor's event log."""
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

def produce_audit_report(task, output_data, dispatcher_decision, cost):
    """Save the audit output as a report artifact."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    filename = f"audit_{task['task_id']}_{ts}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)

    report = {
        "auditor_id": EMBRYO_ID,
        "task_id": task["task_id"],
        "action_class": task["action_class"],
        "dispatcher_decision": dispatcher_decision,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "cost_usd": cost,
        "audit_output": output_data
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
# RUN ONCE — THE AUTONOMOUS AUDIT LOOP
# ============================================================

def run_once():
    """
    Single autonomous audit cycle. The auditor:
    1. Checks kill-switch
    2. Loads its own state
    3. Loads self-task queue
    4. Chooses an audit task by its own scoring
    5. Finds latest oracle output to audit
    6. Requests Dispatcher permission
    7. If DENY: logs and aborts
    8. If ALLOW: executes the audit
    9. Produces audit artifact
    10. Updates its own state
    11. Writes event log
    12. Returns verdict
    """
    print(f"{'='*60}")
    print(f"AUDITOR: {EMBRYO_ID} — run_once()")
    print(f"{'='*60}")

    # 1. Kill-switch
    if check_kill_switch():
        print("  [ABORT] Kill-switch is ACTIVE.")
        write_event("AUDITOR_ABORTED", {"reason": "kill_switch_active"})
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
        write_event("AUDITOR_NO_TASK", {"reason": "no_viable_task"})
        return {"verdict": "NO_TASK", "reason": "no_viable_task"}

    print(f"  Chosen task: {chosen_task['task_id']} (class: {chosen_task['action_class']})")

    # 6. Find oracle output to audit
    oracle_path, oracle_data = get_latest_oracle_output()
    if not oracle_path:
        print("  [ABORT] No oracle output available to audit.")
        write_event("AUDITOR_NO_TARGET", {"reason": "no_oracle_output"})
        return {"verdict": "NO_TARGET", "reason": "no_oracle_output"}

    print(f"  Auditing: {os.path.basename(oracle_path)}")

    # 7. Request Dispatcher permission
    write_event("DISPATCHER_REQUEST", {"task_id": chosen_task["task_id"], "action_class": chosen_task["action_class"]})
    decision, reason = request_dispatcher_permission(chosen_task, contract)
    write_event(f"DISPATCHER_{decision}", {"task_id": chosen_task["task_id"], "reason": reason})
    print(f"  Dispatcher: {decision} — {reason}")

    # 8. If DENY, abort
    if decision == "DENY":
        write_event("AUDITOR_TASK_DENIED", {"task_id": chosen_task["task_id"], "reason": "dispatcher_deny"})
        state["last_task_executed"] = chosen_task["task_id"]
        state["last_task_result"] = "DENIED"
        save_state(state)
        return {"verdict": "DENIED", "task": chosen_task["task_id"], "reason": reason}

    # 9. Execute audit
    write_event("AUDITOR_TASK_STARTED", {"task_id": chosen_task["task_id"], "target": oracle_path})
    print(f"  Executing audit...")
    success, output_data, cost = execute_task(chosen_task, contract, oracle_path, oracle_data)

    if not success:
        write_event("AUDITOR_TASK_FAILED", {"task_id": chosen_task["task_id"], "error": output_data.get("error", "unknown")})
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        state["last_task_executed"] = chosen_task["task_id"]
        state["last_task_result"] = "FAILED"
        save_state(state)
        print(f"  [FAILED] {output_data.get('error', 'unknown')}")
        return {"verdict": "FAILED", "task": chosen_task["task_id"], "error": output_data.get("error")}

    # 10. Produce audit artifact
    report_path = produce_audit_report(chosen_task, output_data, decision, cost)
    print(f"  Audit output: {report_path}")

    # 11. Update state
    state["total_cycles"] += 1
    state["last_cycle_timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    state["last_task_executed"] = chosen_task["task_id"]
    state["last_task_result"] = "SUCCESS"
    state["total_cost_usd"] = round(state.get("total_cost_usd", 0) + cost, 6)
    state["consecutive_failures"] = 0
    state["status"] = "IDLE"
    history_entry = {"task_id": chosen_task["task_id"], "timestamp": state["last_cycle_timestamp"], "result": "SUCCESS", "cost": cost}
    state.setdefault("task_history", []).append(history_entry)
    save_state(state)

    # 12. Write completion event
    write_event("AUDITOR_TASK_COMPLETED", {
        "task_id": chosen_task["task_id"],
        "cost_usd": cost,
        "output_path": report_path,
        "oracle_target": oracle_path
    })

    print(f"  [SUCCESS] Cost: ${cost:.6f}")
    print(f"{'='*60}")

    return {
        "verdict": "AUTONOMOUS_AUDIT_COMPLETE",
        "task": chosen_task["task_id"],
        "action_class": chosen_task["action_class"],
        "dispatcher": decision,
        "cost": cost,
        "output_path": report_path,
        "oracle_audited": oracle_path
    }


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Oracle Auditor Embryo R0")
    parser.add_argument("--run-once", action="store_true", help="Execute a single autonomous audit cycle")
    args = parser.parse_args()

    if args.run_once:
        result = run_once()
        print(f"\nResult: {json.dumps(result, indent=2)}")
    else:
        print("Usage: python3 oracle_auditor_embryo.py --run-once")
        sys.exit(1)
