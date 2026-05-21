"""
EMBRIÓN ORÁCULO DE IAs R0 — v0.5 (Multi-Directive + Conflict Resolution)
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

# Memory Palace path
MEMORY_PALACE_DIR = os.path.join(PROJECT_ROOT, "embryos", "memory_palace")
sys.path.insert(0, MEMORY_PALACE_DIR)

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


def build_memory_entry(task, output_data, cost, auditor_verdict="PENDING"):
    """Build a memory entry from the current cycle's results."""
    grounding_level = output_data.get("grounding_level", 0)
    claims = output_data.get("claims", [])

    # Extract lessons from the output
    lessons = []
    if grounding_level < 7:
        lessons.append("Low grounding score — need more verified sources")
    if cost > 0.001:
        lessons.append("Higher cost than average — consider cheaper provider next time")

    # Determine value score from grounding + claims quality
    value_score = min(10, grounding_level + len(claims) * 0.5)

    # Determine what to avoid
    avoid = []
    if any(c.get("evidence_status") == "NO_SOURCE" for c in claims):
        avoid.append("Claims without source references")

    return {
        "memory_id": f"MEM-OAI-{int(datetime.datetime.utcnow().timestamp())}",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "source_embryo_id": EMBRYO_ID,
        "cycle_id": 0,  # Will be set by caller
        "task_id": task["task_id"],
        "action_class": task["action_class"],
        "artifact_refs": [],  # Will be set by caller
        "claims_count": len(claims),
        "grounding_score": grounding_level,
        "auditor_verdict": auditor_verdict,
        "value_score": round(value_score, 1),
        "cost_usd": cost,
        "lessons": lessons,
        "avoid_next_time": avoid,
        "next_best_action": output_data.get("next_valid_action", "REQUIRES_T1_REVIEW"),
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
    """
    Autonomous task selection based on priority scoring + Memory Palace + T1 Directives
    with Multi-Directive Conflict Resolution (v0.5).
    priority_score = priority_base + freshness_bonus + compounding_value_score
                     - dependency_penalty - recent_repetition_penalty
                     + memory_boost - memory_penalty
                     + directive_modifier (from winning directive set)
    """
    scored = []
    last_task = state.get("last_task_executed")
    memory_influenced = False
    directive_influenced = False
    conflict_resolved = False

    # Load T1 Directives for this embryo (graceful degradation)
    active_directives = []
    chosen_directives = []
    try:
        sys.path.insert(0, os.path.join(BRIDGE_DIR, "state_fabric"))
        from t1_directive_resolver import resolve_directives_for_embryo, apply_directive_to_task_scores
        from t1_directive_conflict_resolver import (
            load_active_directives, detect_conflict, resolve_by_priority,
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
                chosen_directives = []  # Reject all if any is unsafe
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

        # Compounding value bonus
        cv = task.get("compounding_value", "LOW")
        if cv == "HIGH":
            score += 3
        elif cv == "MEDIUM":
            score += 1

        # Dependency penalty: if task requires prior output and no cycles done
        if state["total_cycles"] == 0 and "requires prior" in task.get("stop_condition", ""):
            score -= 10

        # Recent repetition penalty
        if task["task_id"] == last_task:
            score -= 5

        # Memory Palace scoring (if available)
        memory_score_info = None
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

        scored.append((score, task, memory_score_info))

    scored.sort(key=lambda x: x[0], reverse=True)
    chosen = scored[0] if scored else (0, None, None)
    return chosen[1], memory_influenced, chosen[2]


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
    """Parse the LLM response and extract grounded claims."""
    claims = []
    try:
        clean = text.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            clean = "\n".join(lines)

        parsed = json.loads(clean)

        if isinstance(parsed, list):
            for i, item in enumerate(parsed):
                claim = _normalize_claim(item, i)
                claims.append(claim)
        elif isinstance(parsed, dict):
            if "claims" in parsed:
                for i, item in enumerate(parsed["claims"]):
                    claim = _normalize_claim(item, i)
                    claims.append(claim)
            else:
                claims.append(_normalize_claim(parsed, 0))
    except (json.JSONDecodeError, KeyError, TypeError):
        claims.append({
            "claim_id": f"{task['task_id']}_fallback_0",
            "claim_text": text[:300],
            "claim_type": "analytical",
            "evidence_status": "NEEDS_REAL_TIME_CHECK",
            "source_ref": "none",
            "freshness_required": True,
            "confidence": 0.4
        })

    grounding_level = _calculate_grounding_level(claims)
    next_action = "CANDIDATE_READY_FOR_T1" if grounding_level >= 8 else "REQUIRES_T1_REVIEW"

    return {
        "claims": claims,
        "grounding_level": grounding_level,
        "next_valid_action": next_action
    }


def _normalize_claim(item, index):
    """Normalize a claim dict to ensure all mandatory fields exist."""
    claim_text = item.get("claim_text") or item.get("capability_name") or item.get("capability") or item.get("application") or item.get("title") or str(item)[:200]
    claim_type = item.get("claim_type", "factual")

    evidence_status = item.get("evidence_status", "")
    if not evidence_status:
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
    """Calculate grounding level (1-10) based on evidence statuses."""
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
# PROMPTS (v0.3 — Memory-Guided + Grounding-Aware)
# ============================================================

def _build_prompt_for_task(task, memory_context=None):
    """Build a grounding-aware prompt with optional memory context."""
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

    # Add memory context if available
    memory_section = ""
    if memory_context:
        memory_section = (
            "\n\nMEMORY CONTEXT (from previous cycles):\n"
            f"Lessons learned: {json.dumps(memory_context.get('lessons', [])[:3])}\n"
            f"Avoid: {json.dumps(memory_context.get('avoid', [])[:3])}\n"
            "Use this context to improve your output quality.\n"
        )

    prompts = {
        "detect_new_ai_capability_candidates": (
            "You are the Oracle AI Embryo R0 of El Monstruo. Your task: detect_new_ai_capability_candidates. "
            "Identify 3-5 emerging AI capabilities released in the last 30 days that could benefit an autonomous "
            "AI orchestrator system. For each, provide: capability_name, provider, release_date_approx, "
            "potential_power_gain (1-10), integration_complexity (LOW/MED/HIGH)."
            + memory_section + grounding_instruction
        ),
        "map_capability_to_application": (
            "You are the Oracle AI Embryo R0. Task: map_capability_to_application. "
            "Given recent AI capabilities (multimodal reasoning, code generation, real-time search, voice synthesis, "
            "video understanding), map each to a concrete application within an AI orchestrator ecosystem."
            + memory_section + grounding_instruction
        ),
        "rank_application_by_power_gain": (
            "You are the Oracle AI Embryo R0. Task: rank_application_by_power_gain. "
            "Rank these AI applications by power gain for an autonomous orchestrator: "
            "real-time research validation, multi-model consensus, autonomous sprint planning, "
            "provider health monitoring, self-audit loops."
            + memory_section + grounding_instruction
        ),
        "generate_sprint_candidate": (
            "You are the Oracle AI Embryo R0. Task: generate_sprint_candidate. "
            "Generate a structured sprint candidate for the highest-value capability you can identify. "
            "Format: {sprint_id, title, objective, deliverables[], estimated_cycles, risk, value_score, "
            "dependencies[], action_class}. Must be R0 (no production, no deploy, no DB writes)."
            + memory_section + grounding_instruction
        ),
        "audit_previous_oracle_outputs_for_low_value": (
            "You are the Oracle AI Embryo R0. Task: audit_previous_oracle_outputs_for_low_value. "
            "Audit the oracle design itself. "
            "Score the current self-task queue design (1-10) on: coverage, actionability, compounding value, "
            "risk management, autonomy level. Suggest 1-2 improvements."
            + memory_section + grounding_instruction
        ),
    }
    return prompts.get(task["task_id"], f"Execute task: {task['task_id']}. Respond in JSON." + memory_section + grounding_instruction)


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
# RUN ONCE — THE AUTONOMOUS LOOP (v0.3 Memory-Guided)
# ============================================================
def run_once():
    """
    Single autonomous cycle with Memory Palace integration.
    The embryo:
    1. Checks kill-switch
    2. Loads its own state
    3. Loads Memory Palace (graceful degradation if unavailable)
    4. Loads self-task queue
    5. Chooses a task by scoring criteria + memory influence
    6. Requests Dispatcher permission
    7. If DENY: logs and aborts
    8. If ALLOW: executes the task
    9. Produces output artifact (with grounding fields)
    10. Updates its own state
    11. Appends memory entry to Memory Palace
    12. Writes event log
    13. Returns verdict
    """
    print(f"{'='*60}")
    print(f"EMBRYO: {EMBRYO_ID} — run_once() [v0.5 Multi-Directive]")
    print(f"{'='*60}")

    # 1. Kill-switch
    if check_kill_switch():
        print("  [ABORT] Kill-switch is ACTIVE.")
        write_event("EMBRYO_ABORTED", {"reason": "kill_switch_active"})
        return {"verdict": "ABORTED", "reason": "kill_switch_active"}

    # 2. Load state
    state = load_state()
    print(f"  State loaded. Cycles: {state['total_cycles']}")

    # 3. Load Memory Palace
    memory = load_memory()
    memory_available = memory["available"]
    memory_context = None
    if memory_available:
        try:
            lessons = memory["retrieve_lessons"]()
            low_value = memory["retrieve_low_value"]()
            memory_context = {
                "lessons": [l["lesson"] for l in lessons[:5]],
                "avoid": [p["task_id"] for p in low_value[:3]]
            }
            print(f"  Memory Palace: LOADED ({len(lessons)} lessons, {len(low_value)} low-value patterns)")
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

    # 6. Choose task (AUTONOMOUS DECISION + MEMORY INFLUENCE)
    chosen_task, memory_influenced, memory_score_info = choose_next_task(tasks, state, memory if memory_available else None)
    if not chosen_task:
        print("  [ABORT] No viable task found.")
        write_event("EMBRYO_NO_TASK", {"reason": "no_viable_task"})
        return {"verdict": "NO_TASK", "reason": "no_viable_task"}

    print(f"  Chosen task: {chosen_task['task_id']} (class: {chosen_task['action_class']})")
    print(f"  Memory influenced: {memory_influenced}")
    print(f"  Directive influenced: {chosen_task is not None}")
    if memory_score_info:
        print(f"  Memory score: penalty={memory_score_info.get('penalty', 0)}, boost={memory_score_info.get('boost', 0)}, rec={memory_score_info.get('recommendation', 'N/A')}")

    # 7. Request Dispatcher permission
    write_event("DISPATCHER_REQUEST", {"task_id": chosen_task["task_id"], "action_class": chosen_task["action_class"]})
    decision, reason = request_dispatcher_permission(chosen_task, contract)
    write_event(f"DISPATCHER_{decision}", {"task_id": chosen_task["task_id"], "reason": reason})
    print(f"  Dispatcher: {decision} — {reason}")

    # 8. If DENY, abort
    if decision == "DENY":
        write_event("EMBRYO_TASK_ABORTED", {"task_id": chosen_task["task_id"], "reason": "dispatcher_deny"})
        state["last_task_executed"] = chosen_task["task_id"]
        state["last_task_result"] = "DENIED"
        save_state(state)
        return {"verdict": "DENIED", "task": chosen_task["task_id"], "reason": reason}

    # 9. Execute task
    write_event("EMBRYO_TASK_STARTED", {"task_id": chosen_task["task_id"], "memory_influenced": memory_influenced})
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

    # 10. Produce output artifact
    report_path = produce_report(chosen_task, output_data, decision, cost)
    print(f"  Output: {report_path}")
    print(f"  Grounding Level: {output_data.get('grounding_level', 'N/A')}/10")
    print(f"  Claims: {len(output_data.get('claims', []))}")

    # 11. Update state
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
        "grounding_level": output_data.get("grounding_level", 0),
        "memory_influenced": memory_influenced
    }
    state.setdefault("task_history", []).append(history_entry)
    save_state(state)

    # 12. Append memory entry to Memory Palace
    memory_appended = False
    if memory_available:
        try:
            mem_entry = build_memory_entry(chosen_task, output_data, cost)
            mem_entry["cycle_id"] = state["total_cycles"]
            mem_entry["artifact_refs"] = [os.path.basename(report_path)]
            ok, msg = memory["append"](mem_entry)
            memory_appended = ok
            if ok:
                print(f"  Memory Palace: entry appended ({mem_entry['memory_id']})")
            else:
                print(f"  Memory Palace: append failed ({msg})")
        except Exception as e:
            print(f"  Memory Palace: append error ({str(e)[:50]})")

    # 13. Write completion event
    write_event("EMBRYO_TASK_COMPLETED", {
        "task_id": chosen_task["task_id"],
        "cost_usd": cost,
        "output_path": report_path,
        "grounding_level": output_data.get("grounding_level", 0),
        "claims_count": len(output_data.get("claims", [])),
        "memory_influenced": memory_influenced,
        "memory_appended": memory_appended
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
        "claims_count": len(output_data.get("claims", [])),
        "memory_influenced": memory_influenced,
        "memory_appended": memory_appended
    }


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Oracle AI Embryo R0 v0.5 (Multi-Directive)")
    parser.add_argument("--run-once", action="store_true", help="Execute a single autonomous cycle")
    args = parser.parse_args()
    if args.run_once:
        result = run_once()
        print(f"\nResult: {json.dumps(result, indent=2)}")
    else:
        print("Usage: python3 oracle_ai_embryo.py --run-once")
        sys.exit(1)
