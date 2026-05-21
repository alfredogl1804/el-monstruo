"""
T1 Cockpit Data Injector v0.1
Third R0+ Artifact of El Monstruo.

Purpose: Automatically generates a cockpit-ready JSON fixture from the current
system state (Memory Palace, Directive Queue, Provider Registry, Epoch history).
This reduces Alfredo's manual work by eliminating the need to manually compile
pilot status data for the T1 Decision Console.

Invocation: python3 t1_cockpit_data_injector_v0_1.py [--output PATH]

Output: cockpit_fixture_latest.json (or custom path)
"""
import os
import sys
import json
import glob
import datetime
import argparse

# Resolve paths
ARTIFACT_DIR = os.path.dirname(os.path.abspath(__file__))
EPOCH_DIR = os.path.dirname(ARTIFACT_DIR)
REACTOR_DIR = os.path.dirname(EPOCH_DIR)
BRIDGE_DIR = os.path.dirname(REACTOR_DIR)
PROJECT_ROOT = os.path.dirname(BRIDGE_DIR)

# Source paths
MEMORY_PALACE_PATH = os.path.join(PROJECT_ROOT, "embryos", "memory_palace", "memory_palace_state.json")
DIRECTIVE_QUEUE_PATH = os.path.join(BRIDGE_DIR, "state_fabric", "t1_directive_queue.v0_1.json")
KILL_SWITCH_PATH = os.path.join(BRIDGE_DIR, "reactor_vigilia_foundation", "scheduler_kill_switch.json")
ORACLE_STATE_PATH = os.path.join(PROJECT_ROOT, "embryos", "oracle_ai", "oracle_ai_state.json")
AUDITOR_STATE_PATH = os.path.join(PROJECT_ROOT, "embryos", "oracle_auditor", "oracle_auditor_state.json")
ORACLE_OUTPUTS_DIR = os.path.join(BRIDGE_DIR, "embryos", "oracle_ai_r0", "outputs")
AUDITOR_OUTPUTS_DIR = os.path.join(BRIDGE_DIR, "embryos", "oracle_pair_r0", "auditor_outputs")

DEFAULT_OUTPUT = os.path.join(ARTIFACT_DIR, "cockpit_fixture_latest.json")


def load_json_safe(path):
    """Load JSON file safely, return None on failure."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def count_files(directory, pattern="*.json"):
    """Count files matching pattern in directory."""
    if not os.path.exists(directory):
        return 0
    return len(glob.glob(os.path.join(directory, pattern)))


def get_latest_file(directory, pattern="*.json"):
    """Get the most recent file in a directory."""
    if not os.path.exists(directory):
        return None
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def compute_pilot_health():
    """Compute overall pilot health score (0-100)."""
    score = 0
    checks = []

    # Kill-switch should be inactive for healthy pilot
    ks = load_json_safe(KILL_SWITCH_PATH)
    if ks and not ks.get("active", True):
        score += 20
        checks.append(("kill_switch_inactive", True))
    else:
        checks.append(("kill_switch_inactive", False))

    # Memory Palace should exist and have entries
    mp = load_json_safe(MEMORY_PALACE_PATH)
    if mp and len(mp.get("entries", [])) > 0:
        score += 20
        checks.append(("memory_palace_active", True))
    else:
        checks.append(("memory_palace_active", False))

    # Oracle should have completed cycles
    oracle = load_json_safe(ORACLE_STATE_PATH)
    if oracle and oracle.get("total_cycles", 0) > 0:
        score += 20
        checks.append(("oracle_has_cycles", True))
    else:
        checks.append(("oracle_has_cycles", False))

    # Auditor should have completed cycles
    auditor = load_json_safe(AUDITOR_STATE_PATH)
    if auditor and auditor.get("total_cycles", 0) > 0:
        score += 20
        checks.append(("auditor_has_cycles", True))
    else:
        checks.append(("auditor_has_cycles", False))

    # Directive Queue should have active directives
    dq = load_json_safe(DIRECTIVE_QUEUE_PATH)
    if dq:
        active = [d for d in dq.get("directives", []) if d.get("status") == "ACTIVE"]
        if active:
            score += 20
            checks.append(("directives_active", True))
        else:
            checks.append(("directives_active", False))
    else:
        checks.append(("directives_active", False))

    return score, checks


def build_embryo_summary(state_path, name):
    """Build summary for an embryo from its state file."""
    state = load_json_safe(state_path)
    if not state:
        return {"name": name, "status": "UNKNOWN", "cycles": 0, "cost": 0}
    return {
        "name": name,
        "status": state.get("status", "UNKNOWN"),
        "cycles": state.get("total_cycles", 0),
        "cost_usd": state.get("total_cost_usd", 0),
        "last_task": state.get("last_task_executed", "none"),
        "last_result": state.get("last_task_result", "none"),
        "last_cycle": state.get("last_cycle_timestamp", "never"),
        "consecutive_failures": state.get("consecutive_failures", 0)
    }


def build_directive_summary():
    """Build summary of the directive queue."""
    dq = load_json_safe(DIRECTIVE_QUEUE_PATH)
    if not dq:
        return {"total": 0, "active": 0, "directives": []}

    directives = dq.get("directives", [])
    active = [d for d in directives if d.get("status") == "ACTIVE"]

    summaries = []
    for d in active:
        summaries.append({
            "id": d["directive_id"],
            "type": d["directive_type"],
            "priority": d["priority"],
            "focus": d.get("focus", "")[:80],
            "expires": d.get("expires_at", "never"),
            "ttl_cycles": d.get("ttl_cycles", 0)
        })

    return {
        "total": len(directives),
        "active": len(active),
        "expired": sum(1 for d in directives if d.get("status") == "EXPIRED"),
        "paused": sum(1 for d in directives if d.get("status") == "PAUSED"),
        "directives": summaries
    }


def build_memory_summary():
    """Build summary of Memory Palace state."""
    mp = load_json_safe(MEMORY_PALACE_PATH)
    if not mp:
        return {"total_entries": 0, "active": 0, "cost": 0}

    entries = mp.get("entries", [])
    stats = mp.get("stats", {})

    return {
        "total_entries": len(entries),
        "active": sum(1 for e in entries if e.get("status") == "active"),
        "archived": sum(1 for e in entries if e.get("status") == "archived"),
        "unique_embryos": stats.get("unique_embryos", []),
        "unique_tasks": stats.get("unique_tasks", []),
        "total_cost_usd": stats.get("total_cost_usd", 0),
        "avg_grounding_score": round(
            sum(e.get("grounding_score", 0) for e in entries) / max(len(entries), 1), 1
        ),
        "lessons_count": sum(len(e.get("lessons", [])) for e in entries)
    }


def build_epoch_history():
    """Build epoch history from available epoch directories."""
    epochs = []
    epoch_base = os.path.join(BRIDGE_DIR, "reactor_limited_active_r0")
    if not os.path.exists(epoch_base):
        return epochs

    for d in sorted(os.listdir(epoch_base)):
        if d.startswith("live_upgrade_epoch_"):
            epoch_num = d.replace("live_upgrade_epoch_", "")
            epoch_path = os.path.join(epoch_base, d)
            chain_log = os.path.join(epoch_path, f"EPOCH_{epoch_num}_CHAIN_LOG.jsonl")
            has_chain = os.path.exists(chain_log)
            epochs.append({
                "epoch": epoch_num,
                "directory": d,
                "has_chain_log": has_chain,
                "artifacts_count": count_files(os.path.join(epoch_path, "artifacts"))
            })

    return epochs


def generate_cockpit_fixture(output_path=None):
    """Generate the complete cockpit fixture JSON."""
    if output_path is None:
        output_path = DEFAULT_OUTPUT

    now = datetime.datetime.now(datetime.timezone.utc)
    health_score, health_checks = compute_pilot_health()

    fixture = {
        "cockpit_version": "0.1.0",
        "generated_at": now.isoformat(),
        "generator": "t1_cockpit_data_injector_v0_1",
        "pilot_health": {
            "score": health_score,
            "max_score": 100,
            "status": "HEALTHY" if health_score >= 80 else "DEGRADED" if health_score >= 40 else "CRITICAL",
            "checks": health_checks
        },
        "embryos": {
            "oracle": build_embryo_summary(ORACLE_STATE_PATH, "oracle_ai_embryo_r0"),
            "auditor": build_embryo_summary(AUDITOR_STATE_PATH, "oracle_auditor_embryo_r0")
        },
        "directives": build_directive_summary(),
        "memory_palace": build_memory_summary(),
        "epoch_history": build_epoch_history(),
        "outputs": {
            "oracle_total": count_files(ORACLE_OUTPUTS_DIR),
            "auditor_total": count_files(AUDITOR_OUTPUTS_DIR),
            "latest_oracle": os.path.basename(get_latest_file(ORACLE_OUTPUTS_DIR) or "none"),
            "latest_auditor": os.path.basename(get_latest_file(AUDITOR_OUTPUTS_DIR) or "none")
        },
        "cost_summary": {
            "oracle_total_usd": load_json_safe(ORACLE_STATE_PATH).get("total_cost_usd", 0) if load_json_safe(ORACLE_STATE_PATH) else 0,
            "auditor_total_usd": load_json_safe(AUDITOR_STATE_PATH).get("total_cost_usd", 0) if load_json_safe(AUDITOR_STATE_PATH) else 0,
            "memory_palace_total_usd": load_json_safe(MEMORY_PALACE_PATH).get("stats", {}).get("total_cost_usd", 0) if load_json_safe(MEMORY_PALACE_PATH) else 0
        }
    }

    # Compute combined cost
    fixture["cost_summary"]["combined_usd"] = round(
        fixture["cost_summary"]["oracle_total_usd"] +
        fixture["cost_summary"]["auditor_total_usd"], 6
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(fixture, f, indent=2)

    return output_path, fixture


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="T1 Cockpit Data Injector v0.1")
    parser.add_argument("--output", type=str, default=None, help="Output path for cockpit fixture JSON")
    args = parser.parse_args()

    print("=" * 60)
    print("T1 COCKPIT DATA INJECTOR v0.1")
    print("=" * 60)

    path, fixture = generate_cockpit_fixture(args.output)

    print(f"  Generated: {path}")
    print(f"  Pilot Health: {fixture['pilot_health']['score']}/100 ({fixture['pilot_health']['status']})")
    print(f"  Oracle Cycles: {fixture['embryos']['oracle']['cycles']}")
    print(f"  Auditor Cycles: {fixture['embryos']['auditor']['cycles']}")
    print(f"  Active Directives: {fixture['directives']['active']}")
    print(f"  Memory Entries: {fixture['memory_palace']['total_entries']}")
    print(f"  Epochs: {len(fixture['epoch_history'])}")
    print(f"  Combined Cost: ${fixture['cost_summary']['combined_usd']:.6f}")
    print("=" * 60)
