#!/usr/bin/env python3
"""
EMBRIÓN AUDITOR DEL ORÁCULO DE IAs R0 — v0.5 (Multi-Directive + Conflict Resolution)
Second autonomous embryo of El Monstruo — the auditor half of the bicéfalo pair.

Audits outputs produced by oracle_ai_embryo_r0.
v0.3: Memory Palace integration — reads Oracle's memory entries and writes its own.

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

# Memory Palace path
MEMORY_PALACE_DIR = os.path.join(PROJECT_ROOT, "embryos", "memory_palace")
sys.path.insert(0, MEMORY_PALACE_DIR)

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
# MEMORY PALACE INTEGRATION
# ============================================================

def load_memory():
    """Load Memory Palace. Returns None if unavailable (graceful degradation)."""
    try:
        from memory_palace import (
            load_memory_palace, score_task_against_memory,
            retrieve_lessons, retrieve_low_value_patterns,
            append_memory_entry, export_memory_snapshot
        )
        return {
            "available": True,
            "load": load_memory_palace,
            "score_task": score_task_against_memory,
            "retrieve_lessons": retrieve_lessons,
            "retrieve_low_value": retrieve_low_value_patterns,
            "append": append_memory_entry,
            "export_snapshot": export_memory_snapshot
        }
    except ImportError:
        return {"available": False}


def build_auditor_memory_entry(task, oracle_path, grounding_score, grounding_verdict, cost):
    """Build a memory entry from the auditor's cycle results."""
    lessons = []
    avoid = []

    if grounding_verdict == "FAIL":
        lessons.append("Oracle produced output that failed grounding — flag for T1")
    elif grounding_verdict == "PARTIAL":
        lessons.append("Oracle output partially grounded — some claims need real-time verification")
    elif grounding_verdict == "PASS":
        lessons.append("Oracle grounding quality is improving — current approach works")

    if grounding_score < 6:
        avoid.append("Accepting oracle output without grounding enforcement")

    return {
        "memory_id": f"MEM-AUD-{int(datetime.datetime.utcnow().timestamp())}",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "source_embryo_id": EMBRYO_ID,
        "cycle_id": 0,  # Will be set by caller
        "task_id": task["task_id"],
        "action_class": task["action_class"],
        "artifact_refs": [os.path.basename(oracle_path)] if oracle_path else [],
        "claims_count": 0,
        "grounding_score": grounding_score,
        "auditor_verdict": grounding_verdict,
        "value_score": min(10, grounding_score + 2),
        "cost_usd": cost,
        "lessons": lessons,
        "avoid_next_time": avoid,
        "next_best_action": "CANDIDATE_READY_FOR_T1" if grounding_verdict == "PASS" else "REQUIRES_T1_REVIEW",
        "status": "active"
    }


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


def choose_next_task(tasks, state, memory=None):
    """Autonomous task selection with auditor-specific logic + memory + Multi-Directive Conflict Resolution (v0.5)."""
    scored = []
    last_task = state.get("last_task_executed")
    memory_influenced = False
    directive_influenced = False
    conflict_resolved = False

    # Load T1 Directives for this embryo with conflict resolution (graceful degradation)
    active_directives = []
    chosen_directives = []
    try:
        sys.path.insert(0, os.path.join(BRIDGE_DIR, "state_fabric"))
        from t1_directive_resolver import resolve_directives_for_embryo, apply_directive_to_task_scores
        from t1_directive_conflict_resolver import (
            detect_conflict, resolve_by_priority,
            validate_directive_does_not_authorize, validate_directive_does_not_change_provider_allowlist
        )
        active_directives = resolve_directives_for_embryo(EMBRYO_ID)

        # Multi-Directive Conflict Resolution (v0.5)
        if len(active_directives) >= 2:
            has_conflict, _ = detect_conflict(active_directives)
            if has_conflict:
                chosen_directives, _, _ = resolve_by_priority(active_directives)
                conflict_resolved = True
            else:
                chosen_directives = active_directives
        else:
            chosen_directives = active_directives

        # Safety: validate no directive authorizes prohibited actions or provider changes
        for d in chosen_directives:
            safe_auth, _ = validate_directive_does_not_authorize(d, "R1_OPERATION")
            safe_prov, _ = validate_directive_does_not_change_provider_allowlist(d)
            if not safe_auth or not safe_prov:
                chosen_directives = []
                break
    except Exception:
        pass

    # Pre-compute directive modifiers for all tasks (using winning directive set)
    directive_modifiers = {}
    if chosen_directives:
        try:
            task_inputs = [{"task_id": t["task_id"], "purpose": t.get("purpose", t.get("description", ""))} for t in tasks]
            mods = apply_directive_to_task_scores(task_inputs, chosen_directives)
            for m in mods:
                directive_modifiers[m["task_id"]] = m["score_modifier"]
        except Exception:
            pass

    for task in tasks:
        score = task.get("priority_base", 5)
        score += task.get("freshness_bonus", 0)

        cv = task.get("compounding_value", "LOW")
        if cv == "HIGH":
            score += 3
        elif cv == "MEDIUM":
            score += 1

        if state["total_cycles"] == 0 and "requires prior" in task.get("stop_condition", ""):
            score -= 10

        if "No oracle output available" in task.get("stop_condition", ""):
            oracle_outputs = get_oracle_outputs()
            if not oracle_outputs:
                score -= 20

        if task["task_id"] == last_task:
            score -= 5

        # Memory Palace scoring
        if memory and memory["available"]:
            try:
                memory_score_info = memory["score_task"](task["task_id"], EMBRYO_ID)
                score -= memory_score_info.get("penalty", 0)
                score += memory_score_info.get("boost", 0)
                if memory_score_info.get("penalty", 0) > 0 or memory_score_info.get("boost", 0) > 0:
                    memory_influenced = True
            except Exception:
                pass

        # T1 Directive scoring
        d_mod = directive_modifiers.get(task["task_id"], 0)
        if d_mod != 0:
            score += d_mod
            directive_influenced = True

        scored.append((score, task))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored else None, memory_influenced


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
    """Real Dispatcher check: verify action_class is in allowed list."""
    action_class = task.get("action_class", "UNKNOWN")
    allowed = contract.get("allowed_action_classes", [])
    forbidden = contract.get("forbidden_action_classes", [])

    if action_class in forbidden:
        return "DENY", f"Action class {action_class} is in forbidden list"
    if action_class in allowed:
        return "ALLOW", f"Action class {action_class} is in allowed list"
    return "DENY", f"Action class {action_class} not found in allowed list"


# ============================================================
# GROUNDING ENFORCEMENT v0.2
# ============================================================

def enforce_grounding(oracle_output_data, contract):
    """
    Enforce grounding contract on oracle output.
    Returns (grounding_score, penalties, verdict, details).
    """
    enforcement = contract.get("grounding_enforcement", {})
    if not enforcement.get("enabled", False):
        return 10.0, [], "PASS", {"note": "grounding_enforcement disabled"}

    penalties = []
    details = {}

    output = oracle_output_data.get("output", oracle_output_data)
    claims = output.get("claims", [])

    if not claims:
        if isinstance(output, dict) and "output" in output:
            claims = output["output"].get("claims", [])

    if not claims:
        penalties.append(("no_claims_field", enforcement.get("penalties", {}).get("no_claims_field", -3.0)))
        details["claims_found"] = 0
        details["claims_expected"] = True
    else:
        details["claims_found"] = len(claims)

    dimension_scores = {}

    # 1. grounding_level_compliance
    if claims:
        claims_with_evidence = sum(1 for c in claims if c.get("evidence_status"))
        compliance_ratio = claims_with_evidence / len(claims)
        dimension_scores["grounding_level_compliance"] = round(compliance_ratio * 10, 1)
    else:
        dimension_scores["grounding_level_compliance"] = 0

    # 2. evidence_status_accuracy
    if claims:
        valid_statuses = {"VERIFIED_LOCAL", "VERIFIED_PROVIDER", "NEEDS_REAL_TIME_CHECK", "NO_SOURCE", "HYPOTHESIS", "CANDIDATE_ONLY"}
        valid_count = sum(1 for c in claims if c.get("evidence_status") in valid_statuses)
        dimension_scores["evidence_status_accuracy"] = round((valid_count / len(claims)) * 10, 1)
        missing_es = len(claims) - valid_count
        if missing_es > 0:
            penalties.append(("no_evidence_status", enforcement.get("penalties", {}).get("no_evidence_status", -2.0) * missing_es))
    else:
        dimension_scores["evidence_status_accuracy"] = 0

    # 3. no_source_prohibition
    if claims:
        violations = [c for c in claims if c.get("evidence_status") in ("NO_SOURCE", "HYPOTHESIS") and c.get("confidence", 0) > 0.8]
        if violations:
            penalties.append(("no_source_as_fact", enforcement.get("penalties", {}).get("no_source_as_fact", -5.0) * len(violations)))
            dimension_scores["no_source_prohibition"] = max(0, 10 - len(violations) * 3)
        else:
            dimension_scores["no_source_prohibition"] = 10
    else:
        dimension_scores["no_source_prohibition"] = 5

    # 4. freshness_marking
    if claims:
        date_indicators = ["release", "date", "price", "endpoint", "available", "launched", "2025", "2026", "v1", "v2", "api"]
        time_sensitive = [c for c in claims if any(ind in c.get("claim_text", "").lower() for ind in date_indicators)]
        correctly_marked = [c for c in time_sensitive if c.get("evidence_status") == "NEEDS_REAL_TIME_CHECK" or c.get("freshness_required", False)]
        if time_sensitive:
            ratio = len(correctly_marked) / len(time_sensitive)
            dimension_scores["freshness_marking"] = round(ratio * 10, 1)
            unmarked = len(time_sensitive) - len(correctly_marked)
            if unmarked > 0:
                penalties.append(("missing_freshness_on_date", enforcement.get("penalties", {}).get("missing_freshness_on_date", -2.0) * unmarked))
        else:
            dimension_scores["freshness_marking"] = 10
    else:
        dimension_scores["freshness_marking"] = 5

    # Calculate weighted average
    weights = {}
    for dim in enforcement.get("scoring_dimensions", []):
        weights[dim["name"]] = dim.get("weight", 1)

    total_weight = sum(weights.get(k, 1) for k in dimension_scores)
    weighted_sum = sum(dimension_scores.get(k, 0) * weights.get(k, 1) for k in dimension_scores)
    base_score = weighted_sum / total_weight if total_weight > 0 else 5.0

    total_penalty = sum(p[1] for p in penalties)
    final_score = max(0, min(10, base_score + total_penalty))

    thresholds = enforcement.get("thresholds", {"PASS": 8.0, "PARTIAL": 5.0, "FAIL": 0.0})
    if final_score >= thresholds.get("PASS", 8.0):
        verdict = "PASS"
    elif final_score >= thresholds.get("PARTIAL", 5.0):
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    details["dimension_scores"] = dimension_scores
    details["penalties_applied"] = penalties
    details["base_score"] = round(base_score, 2)
    details["final_score"] = round(final_score, 2)
    details["verdict"] = verdict

    return round(final_score, 2), penalties, verdict, details


# ============================================================
# TASK EXECUTION
# ============================================================

def execute_task(task, contract, oracle_output_path, oracle_output_data):
    """Execute an audit task using one provider."""
    providers = contract.get("providers_allowed", [])
    if not providers:
        return False, {"error": "No providers available"}, 0.0

    provider = providers[0]
    provider_name = provider["name"].lower()
    model = provider["model"]

    # First: run grounding enforcement locally (no API needed)
    grounding_score, grounding_penalties, grounding_verdict, grounding_details = enforce_grounding(oracle_output_data, contract)

    prompt = _build_audit_prompt(task, oracle_output_path, oracle_output_data, grounding_details)

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
            "cost": cost,
            "grounding_enforcement": {
                "score": grounding_score,
                "verdict": grounding_verdict,
                "details": grounding_details
            }
        }
        return True, output, cost

    except Exception as e:
        return False, {"error": str(e)[:200]}, 0.0


def _build_audit_prompt(task, oracle_output_path, oracle_output_data, grounding_details):
    """Build audit prompt with grounding enforcement context."""
    oracle_content = json.dumps(oracle_output_data, indent=2)[:2000] if oracle_output_data else "NO OUTPUT AVAILABLE"
    grounding_context = json.dumps(grounding_details, indent=2)[:500]

    prompts = {
        "audit_oracle_latest_output": (
            f"You are the Oracle Auditor Embryo R0 v0.3 (Memory-Guided + Grounding Enforcement) of El Monstruo.\n\n"
            f"Oracle output to audit (from {oracle_output_path}):\n```json\n{oracle_content}\n```\n\n"
            f"Local grounding enforcement already ran. Results:\n```json\n{grounding_context}\n```\n\n"
            f"Your job: validate the grounding enforcement results and add your own assessment.\n"
            f"Evaluate on 5 dimensions (score 1-10 each):\n"
            f"1. hallucination_risk: Are there fabricated claims, non-existent APIs, wrong dates?\n"
            f"2. value_score: Is this output actionable and useful?\n"
            f"3. scope_compliance: Does it stay within R0 boundaries?\n"
            f"4. factual_grounding: Are claims properly marked with evidence_status?\n"
            f"5. actionability: Can T1 act on this immediately?\n\n"
            f"Respond in JSON: {{\"verdict\": \"PASS|PARTIAL|FAIL\", \"scores\": {{...}}, \"grounding_agreement\": true|false, \"flags\": [...], \"recommendation\": \"...\"}}"
        ),
        "score_oracle_sprint_candidate": (
            f"You are the Oracle Auditor Embryo R0 v0.3. Task: score a sprint candidate.\n\n"
            f"Oracle output:\n```json\n{oracle_content}\n```\n\n"
            f"Grounding enforcement:\n```json\n{grounding_context}\n```\n\n"
            f"Score on: value (1-10), risk (1-10), feasibility (1-10), R0_compliance (YES/NO), grounding (1-10).\n"
            f"Respond in JSON: {{\"verdict\": \"PASS|PARTIAL|FAIL\", \"scores\": {{...}}, \"grounding_agreement\": true|false}}"
        ),
        "detect_oracle_hallucination": (
            f"You are the Oracle Auditor Embryo R0 v0.3. Task: detect hallucinations.\n\n"
            f"Oracle output:\n```json\n{oracle_content}\n```\n\n"
            f"Grounding enforcement:\n```json\n{grounding_context}\n```\n\n"
            f"Check for: non-existent APIs, wrong model names, fabricated release dates, impossible integrations.\n"
            f"Pay special attention to claims marked NEEDS_REAL_TIME_CHECK — these are honest about uncertainty.\n"
            f"Respond in JSON: {{\"hallucinations_found\": [...], \"confidence\": 0-1, \"verdict\": \"CLEAN|SUSPICIOUS|HALLUCINATED\", \"grounding_agreement\": true|false}}"
        ),
        "verify_oracle_scope_compliance": (
            f"You are the Oracle Auditor Embryo R0 v0.3. Task: verify R0 scope compliance.\n\n"
            f"Oracle output:\n```json\n{oracle_content}\n```\n\n"
            f"Verify: no R1 proposals, no production deployments, no DB writes, no secret access.\n"
            f"Respond in JSON: {{\"r0_compliant\": true|false, \"violations\": [...], \"verdict\": \"COMPLIANT|VIOLATION\"}}"
        ),
        "generate_audit_summary_for_t1": (
            f"You are the Oracle Auditor Embryo R0 v0.3. Task: generate audit summary for T1.\n\n"
            f"Oracle output:\n```json\n{oracle_content}\n```\n\n"
            f"Grounding enforcement:\n```json\n{grounding_context}\n```\n\n"
            f"Produce: overall verdict, grounding score, risk flags, recommended action.\n"
            f"Respond in JSON: {{\"overall_verdict\": \"PASS|PARTIAL|FAIL\", \"grounding_score\": X, \"risk_flags\": [...], \"recommended_action\": \"...\"}}"
        ),
    }
    return prompts.get(task["task_id"], f"Audit this oracle output with grounding enforcement: {oracle_content}")


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
        "audit_output": output_data,
        "grounding_enforcement": output_data.get("grounding_enforcement", {})
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
# RUN ONCE — THE AUTONOMOUS AUDIT LOOP (v0.3 Memory-Guided)
# ============================================================

def run_once():
    """
    Single autonomous audit cycle with Memory Palace integration.
    """
    print(f"{'='*60}")
    print(f"AUDITOR: {EMBRYO_ID} — run_once() [v0.3 Memory-Guided]")
    print(f"{'='*60}")

    # 1. Kill-switch
    if check_kill_switch():
        print("  [ABORT] Kill-switch is ACTIVE.")
        write_event("AUDITOR_ABORTED", {"reason": "kill_switch_active"})
        return {"verdict": "ABORTED", "reason": "kill_switch_active"}

    # 2. Load state
    state = load_state()
    print(f"  State loaded. Cycles: {state['total_cycles']}")

    # 3. Load Memory Palace
    memory = load_memory()
    memory_available = memory["available"]
    if memory_available:
        try:
            lessons = memory["retrieve_lessons"]()
            print(f"  Memory Palace: LOADED ({len(lessons)} lessons)")
        except Exception as e:
            print(f"  Memory Palace: ERROR ({str(e)[:50]})")
            memory_available = False
    else:
        print("  Memory Palace: NOT AVAILABLE (graceful degradation)")

    # 4. Load self-tasks
    tasks = load_self_tasks()
    print(f"  Self-tasks loaded: {len(tasks)}")

    # 5. Load contract
    contract = load_contract()

    # 6. Choose task (AUTONOMOUS DECISION + MEMORY)
    chosen_task, memory_influenced = choose_next_task(tasks, state, memory if memory_available else None)
    if not chosen_task:
        print("  [ABORT] No viable task found.")
        write_event("AUDITOR_NO_TASK", {"reason": "no_viable_task"})
        return {"verdict": "NO_TASK", "reason": "no_viable_task"}

    print(f"  Chosen task: {chosen_task['task_id']} (class: {chosen_task['action_class']})")
    print(f"  Memory influenced: {memory_influenced}")

    # 7. Find oracle output to audit
    oracle_path, oracle_data = get_latest_oracle_output()
    if not oracle_path:
        print("  [ABORT] No oracle output available to audit.")
        write_event("AUDITOR_NO_TARGET", {"reason": "no_oracle_output"})
        return {"verdict": "NO_TARGET", "reason": "no_oracle_output"}

    print(f"  Auditing: {os.path.basename(oracle_path)}")

    # 8. Run local grounding enforcement FIRST
    grounding_score, grounding_penalties, grounding_verdict, grounding_details = enforce_grounding(oracle_data, contract)
    print(f"  Grounding Enforcement: {grounding_verdict} (score: {grounding_score}/10)")
    write_event("GROUNDING_ENFORCEMENT", {
        "oracle_target": oracle_path,
        "score": grounding_score,
        "verdict": grounding_verdict,
        "penalties": len(grounding_penalties)
    })

    # 9. Request Dispatcher permission
    write_event("DISPATCHER_REQUEST", {"task_id": chosen_task["task_id"], "action_class": chosen_task["action_class"]})
    decision, reason = request_dispatcher_permission(chosen_task, contract)
    write_event(f"DISPATCHER_{decision}", {"task_id": chosen_task["task_id"], "reason": reason})
    print(f"  Dispatcher: {decision} — {reason}")

    # 10. If DENY, abort
    if decision == "DENY":
        write_event("AUDITOR_TASK_DENIED", {"task_id": chosen_task["task_id"], "reason": "dispatcher_deny"})
        state["last_task_executed"] = chosen_task["task_id"]
        state["last_task_result"] = "DENIED"
        save_state(state)
        return {"verdict": "DENIED", "task": chosen_task["task_id"], "reason": reason}

    # 11. Execute audit (with grounding context)
    write_event("AUDITOR_TASK_STARTED", {"task_id": chosen_task["task_id"], "target": oracle_path, "memory_influenced": memory_influenced})
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

    # 12. Produce audit artifact
    report_path = produce_audit_report(chosen_task, output_data, decision, cost)
    print(f"  Audit output: {report_path}")

    # 13. Update state
    state["total_cycles"] += 1
    state["last_cycle_timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    state["last_task_executed"] = chosen_task["task_id"]
    state["last_task_result"] = "SUCCESS"
    state["total_cost_usd"] = round(state.get("total_cost_usd", 0) + cost, 6)
    state["consecutive_failures"] = 0
    state["status"] = "IDLE"
    history_entry = {
        "task_id": chosen_task["task_id"],
        "timestamp": state["last_cycle_timestamp"],
        "result": "SUCCESS",
        "cost": cost,
        "grounding_score": grounding_score,
        "grounding_verdict": grounding_verdict,
        "memory_influenced": memory_influenced
    }
    state.setdefault("task_history", []).append(history_entry)
    save_state(state)

    # 14. Append memory entry to Memory Palace
    memory_appended = False
    if memory_available:
        try:
            mem_entry = build_auditor_memory_entry(chosen_task, oracle_path, grounding_score, grounding_verdict, cost)
            mem_entry["cycle_id"] = state["total_cycles"]
            ok, msg = memory["append"](mem_entry)
            memory_appended = ok
            if ok:
                print(f"  Memory Palace: entry appended ({mem_entry['memory_id']})")
            else:
                print(f"  Memory Palace: append failed ({msg})")
        except Exception as e:
            print(f"  Memory Palace: append error ({str(e)[:50]})")

    # 15. Write completion event
    write_event("AUDITOR_TASK_COMPLETED", {
        "task_id": chosen_task["task_id"],
        "cost_usd": cost,
        "output_path": report_path,
        "oracle_target": oracle_path,
        "grounding_score": grounding_score,
        "grounding_verdict": grounding_verdict,
        "memory_influenced": memory_influenced,
        "memory_appended": memory_appended
    })

    print(f"  [SUCCESS] Cost: ${cost:.6f}")
    print(f"  Grounding: {grounding_verdict} ({grounding_score}/10)")
    print(f"{'='*60}")

    return {
        "verdict": "AUTONOMOUS_AUDIT_COMPLETE",
        "task": chosen_task["task_id"],
        "action_class": chosen_task["action_class"],
        "dispatcher": decision,
        "cost": cost,
        "output_path": report_path,
        "oracle_audited": oracle_path,
        "grounding_score": grounding_score,
        "grounding_verdict": grounding_verdict,
        "memory_influenced": memory_influenced,
        "memory_appended": memory_appended
    }


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Oracle Auditor Embryo R0 v0.3 (Memory-Guided)")
    parser.add_argument("--run-once", action="store_true", help="Execute a single autonomous audit cycle")
    args = parser.parse_args()

    if args.run_once:
        result = run_once()
        print(f"\nResult: {json.dumps(result, indent=2)}")
    else:
        print("Usage: python3 oracle_auditor_embryo.py --run-once")
        sys.exit(1)
