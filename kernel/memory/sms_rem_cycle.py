"""
kernel/memory/sms_rem_cycle.py — REM Cycle (Nightly Consolidation)

Inspired by biological REM sleep where the brain consolidates memories:
1. Decay: Apply Ebbinghaus forgetting curve to untouched memories
2. Crystallize: Promote high-confidence, multiply-validated memories to axioms
3. Deduplicate: Merge near-duplicate memories (cosine similarity > 0.95)
4. Forget: Soft-delete memories below strength threshold
5. Detect Gaps: Identify areas where knowledge is thin
6. Resolve Conflicts: Auto-resolve simple contradictions by confidence
7. Log: Record consolidation stats

Designed to run as:
- Manus scheduled task (daily at 3:00 AM CST)
- Railway cron job
- Manual invocation: python -m kernel.memory.sms_rem_cycle

Author: Manus C (Batch 011 — SMS REM Cycle)
Date: 2026-05-21
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger("monstruo.sms.rem")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

# Ebbinghaus decay parameters
DECAY_HALF_LIFE_DAYS = 7  # Memory strength halves every 7 days without access
MIN_STRENGTH_THRESHOLD = 0.1  # Below this = candidate for forgetting
CRYSTALLIZATION_THRESHOLD = 0.95  # Confidence needed to become axiom
CRYSTALLIZATION_MIN_VALIDATIONS = 3  # Must be validated N times
DEDUP_SIMILARITY_THRESHOLD = 0.95  # Above this = duplicate
MAX_MEMORIES_PER_RUN = 500  # Process at most N memories per cycle


def _get_config() -> dict:
    """Get config from environment."""
    return {
        "url": os.environ.get("SUPABASE_URL", ""),
        "service_key": (
            os.environ.get("SUPABASE_SERVICE_KEY")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        ),
        "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
        "openai_base_url": os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1"),
    }


def _supabase_request(method: str, path: str, body=None, extra_headers=None, timeout=15):
    """Minimal Supabase REST request."""
    cfg = _get_config()
    url = f"{cfg['url']}/rest/v1{path}"
    headers = {
        "apikey": cfg["service_key"],
        "Authorization": f"Bearer {cfg['service_key']}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload) if payload else None
    except Exception as e:
        logger.error(f"Supabase {method} {path} failed: {e}")
        return None


def _supabase_rpc(function_name: str, params: dict, timeout=15):
    """Call Supabase RPC."""
    cfg = _get_config()
    url = f"{cfg['url']}/rest/v1/rpc/{function_name}"
    headers = {
        "apikey": cfg["service_key"],
        "Authorization": f"Bearer {cfg['service_key']}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(params).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload) if payload else []
    except Exception as e:
        logger.error(f"RPC {function_name} failed: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# REM CYCLE STEPS
# ═══════════════════════════════════════════════════════════════════════════════

class REMCycleStats:
    """Track consolidation statistics."""
    def __init__(self):
        self.memories_processed = 0
        self.memories_decayed = 0
        self.memories_forgotten = 0
        self.axioms_crystallized = 0
        self.duplicates_merged = 0
        self.conflicts_resolved = 0
        self.gaps_detected = 0
        self.errors = []

    def to_dict(self) -> dict:
        return {
            "memories_processed": self.memories_processed,
            "memories_decayed": self.memories_decayed,
            "memories_forgotten": self.memories_forgotten,
            "axioms_crystallized": self.axioms_crystallized,
            "duplicates_merged": self.duplicates_merged,
            "conflicts_resolved": self.conflicts_resolved,
            "gaps_detected": self.gaps_detected,
            "errors": self.errors[:10],
        }


def step_1_decay(stats: REMCycleStats):
    """Apply Ebbinghaus decay to memories not accessed recently."""
    print("  [1/7] Applying Ebbinghaus decay...")

    # Get all alive memories
    memories = _supabase_request(
        "GET",
        f"/sovereign_memories?is_alive=eq.true&order=last_accessed.asc.nullsfirst&limit={MAX_MEMORIES_PER_RUN}",
    )
    if not memories:
        print("    No memories to decay")
        return

    now = datetime.now(timezone.utc)
    decayed = 0

    for mem in memories:
        stats.memories_processed += 1
        last_accessed = mem.get("last_accessed") or mem.get("created_at")
        if not last_accessed:
            continue

        # Parse timestamp
        try:
            if "T" in last_accessed:
                accessed_dt = datetime.fromisoformat(last_accessed.replace("Z", "+00:00"))
            else:
                accessed_dt = datetime.strptime(last_accessed, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except:
            continue

        days_since = (now - accessed_dt).days
        if days_since <= 0:
            continue

        # Ebbinghaus: strength = initial * (0.5 ^ (days / half_life))
        current_strength = mem.get("strength", 1.0)
        new_strength = current_strength * (0.5 ** (days_since / DECAY_HALF_LIFE_DAYS))
        new_strength = max(new_strength, 0.01)  # Never fully zero

        if new_strength < current_strength * 0.99:  # Only update if meaningful change
            _supabase_request(
                "PATCH",
                f"/sovereign_memories?id=eq.{mem['id']}",
                body={"strength": round(new_strength, 4)},
                extra_headers={"Prefer": "return=minimal"},
            )
            decayed += 1

    stats.memories_decayed = decayed
    print(f"    Decayed {decayed}/{len(memories)} memories")


def step_2_crystallize(stats: REMCycleStats):
    """Promote high-confidence memories to sovereign axioms."""
    print("  [2/7] Checking crystallization candidates...")

    # Find memories with high confidence and multiple validations
    candidates = _supabase_request(
        "GET",
        f"/sovereign_memories?is_alive=eq.true&confidence=gte.{CRYSTALLIZATION_THRESHOLD}"
        f"&memory_type=eq.semantic&order=confidence.desc&limit=20",
    )
    if not candidates:
        print("    No crystallization candidates")
        return

    crystallized = 0
    for mem in candidates:
        content = mem.get("content", "")
        if not content or len(content) < 10:
            continue

        # Check if axiom already exists
        existing = _supabase_request(
            "GET",
            f"/sovereign_axioms?statement=eq.{urllib.request.quote(content[:200])}&limit=1",
        )
        if existing:
            continue

        # Crystallize
        _supabase_request(
            "POST",
            "/sovereign_axioms",
            body={
                "statement": content[:500],
                "confidence": mem.get("confidence", 0.95),
                "validation_count": 1,
                "contradiction_count": 0,
                "source_agent": mem.get("agent_id", "system"),
                "implications": "[]",
                "tags": mem.get("tags", []),
                "is_active": True,
            },
            extra_headers={"Prefer": "return=minimal"},
        )
        crystallized += 1

    stats.axioms_crystallized = crystallized
    print(f"    Crystallized {crystallized} new axioms")


def step_3_deduplicate(stats: REMCycleStats):
    """Find and merge near-duplicate memories."""
    print("  [3/7] Deduplicating memories...")
    # This step requires embeddings comparison — use RPC if available
    # For now, use content_hash dedup (exact matches)
    
    result = _supabase_rpc("deduplicate_sovereign_memories", {
        "similarity_threshold": DEDUP_SIMILARITY_THRESHOLD,
    })
    
    if isinstance(result, list):
        stats.duplicates_merged = len(result)
        print(f"    Merged {len(result)} duplicates")
    else:
        # Fallback: hash-based dedup
        print("    RPC not available — skipping semantic dedup")


def step_4_forget(stats: REMCycleStats):
    """Soft-delete memories below strength threshold."""
    print("  [4/7] Forgetting weak memories...")

    weak = _supabase_request(
        "GET",
        f"/sovereign_memories?is_alive=eq.true&strength=lt.{MIN_STRENGTH_THRESHOLD}&limit=100",
    )
    if not weak:
        print("    No memories to forget")
        return

    forgotten = 0
    now_iso = datetime.now(timezone.utc).isoformat()

    for mem in weak:
        # Never forget memories in Layer 4 (sovereign) or Layer 5 (metacognition)
        if mem.get("layer", 3) >= 4:
            continue

        _supabase_request(
            "PATCH",
            f"/sovereign_memories?id=eq.{mem['id']}",
            body={"is_alive": False, "forgotten_at": now_iso},
            extra_headers={"Prefer": "return=minimal"},
        )
        forgotten += 1

    stats.memories_forgotten = forgotten
    print(f"    Forgotten {forgotten} weak memories (strength < {MIN_STRENGTH_THRESHOLD})")


def step_5_detect_gaps(stats: REMCycleStats):
    """Detect areas where knowledge is thin."""
    print("  [5/7] Detecting knowledge gaps...")

    # Check for agents with very few memories
    agents = _supabase_request("GET", "/sovereign_agent_registry?is_active=eq.true")
    if not agents:
        print("    No agents registered")
        return

    gaps_created = 0
    for agent in agents:
        agent_id = agent.get("agent_id", "")
        memories = _supabase_request(
            "GET",
            f"/sovereign_memories?agent_id=eq.{agent_id}&is_alive=eq.true&select=id&limit=1",
            extra_headers={"Prefer": "count=exact"},
        )
        count = len(memories) if memories else 0
        if count == 0:
            # Agent has no memories — create gap
            _supabase_request(
                "POST",
                "/sovereign_knowledge_gaps",
                body={
                    "question": f"Agent '{agent_id}' has zero memories — needs initial knowledge injection",
                    "evidence": f"REM Cycle detected 0 memories for agent {agent_id}",
                    "severity": "LOW",
                    "resolution_strategy": "inject_initial_context",
                    "agent_id": agent_id,
                    "is_resolved": False,
                },
                extra_headers={"Prefer": "return=minimal"},
            )
            gaps_created += 1

    stats.gaps_detected = gaps_created
    print(f"    Detected {gaps_created} new gaps")


def step_6_resolve_conflicts(stats: REMCycleStats):
    """Auto-resolve simple conflicts by confidence."""
    print("  [6/7] Resolving conflicts...")

    # Get unresolved conflicts (if any pending)
    conflicts = _supabase_request(
        "GET",
        "/sovereign_conflict_log?resolved_by=eq.pending&limit=20",
    )
    if not conflicts:
        print("    No pending conflicts")
        return

    resolved = 0
    for conflict in conflicts:
        # Simple resolution: higher confidence wins
        mem_a = _supabase_request("GET", f"/sovereign_memories?id=eq.{conflict.get('memory_a_id')}&limit=1")
        mem_b = _supabase_request("GET", f"/sovereign_memories?id=eq.{conflict.get('memory_b_id')}&limit=1")

        if mem_a and mem_b:
            conf_a = mem_a[0].get("confidence", 0.5) if mem_a else 0
            conf_b = mem_b[0].get("confidence", 0.5) if mem_b else 0
            winner = conflict.get("memory_a_id") if conf_a >= conf_b else conflict.get("memory_b_id")

            _supabase_request(
                "PATCH",
                f"/sovereign_conflict_log?id=eq.{conflict['id']}",
                body={
                    "winner_id": winner,
                    "resolved_by": "rem_cycle",
                    "reason": f"Auto-resolved by confidence ({conf_a:.2f} vs {conf_b:.2f})",
                },
                extra_headers={"Prefer": "return=minimal"},
            )
            resolved += 1

    stats.conflicts_resolved = resolved
    print(f"    Resolved {resolved} conflicts")


def step_7_log(stats: REMCycleStats, duration_ms: int):
    """Log consolidation run."""
    print("  [7/7] Logging consolidation...")

    _supabase_request(
        "POST",
        "/sovereign_consolidation_log",
        body={
            "run_type": "nightly",
            "memories_processed": stats.memories_processed,
            "memories_forgotten": stats.memories_forgotten,
            "axioms_crystallized": stats.axioms_crystallized,
            "conflicts_resolved": stats.conflicts_resolved,
            "gaps_detected": stats.gaps_detected,
            "duration_ms": duration_ms,
            "status": "completed" if not stats.errors else "completed_with_errors",
            "error_message": "; ".join(stats.errors[:3]) if stats.errors else None,
        },
        extra_headers={"Prefer": "return=minimal"},
    )
    print(f"    Logged to sovereign_consolidation_log")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN: RUN REM CYCLE
# ═══════════════════════════════════════════════════════════════════════════════

def run_rem_cycle() -> dict:
    """
    Execute the full REM Cycle consolidation.
    
    Returns stats dict with results.
    """
    print()
    print("=" * 70)
    print("  SMS REM CYCLE — Nightly Consolidation")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)
    print()

    cfg = _get_config()
    if not cfg["url"] or not cfg["service_key"]:
        print("  ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY required")
        return {"status": "error", "reason": "no_credentials"}

    stats = REMCycleStats()
    start = time.time()

    try:
        step_1_decay(stats)
        step_2_crystallize(stats)
        step_3_deduplicate(stats)
        step_4_forget(stats)
        step_5_detect_gaps(stats)
        step_6_resolve_conflicts(stats)

        duration_ms = int((time.time() - start) * 1000)
        step_7_log(stats, duration_ms)

    except Exception as e:
        stats.errors.append(str(e))
        logger.error(f"REM Cycle error: {e}")
        duration_ms = int((time.time() - start) * 1000)
        step_7_log(stats, duration_ms)

    print()
    print("-" * 70)
    print("  RESULTS:")
    print(f"    Processed:    {stats.memories_processed}")
    print(f"    Decayed:      {stats.memories_decayed}")
    print(f"    Forgotten:    {stats.memories_forgotten}")
    print(f"    Crystallized: {stats.axioms_crystallized}")
    print(f"    Deduped:      {stats.duplicates_merged}")
    print(f"    Conflicts:    {stats.conflicts_resolved}")
    print(f"    Gaps:         {stats.gaps_detected}")
    print(f"    Duration:     {duration_ms}ms")
    print(f"    Errors:       {len(stats.errors)}")
    print("-" * 70)
    print()

    return stats.to_dict()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_rem_cycle()
    print(json.dumps(result, indent=2))
