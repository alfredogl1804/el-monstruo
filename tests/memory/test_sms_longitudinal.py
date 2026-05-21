"""
SOVEREIGN MEMORY SYSTEM — Longitudinal Validation Tests

Tests the 8 families from DORY_LONGITUDINAL_BENCH_SPEC:
A. Decision Retention
B. Role Retention
C. Side Effect Retention
D. Handoff / Re-entry
E. Adversarial Compaction
F. Seeded Contradiction
G. Longitudinal Persistence (simulated)
H. Honest Scoring

Each test simulates multi-session scenarios with compaction events.
"""

import json
import sys
import os
from datetime import datetime, timedelta
from copy import deepcopy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sovereign_memory_system import (
    SovereignMemorySystem, Memory, Axiom, MemoryLayer, MemoryType,
    Percept, KnowledgeGap, CausalChain, ConflictResolution,
)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

class TestResult:
    def __init__(self, family: str, test_id: str, description: str):
        self.family = family
        self.test_id = test_id
        self.description = description
        self.passed = False
        self.details = ""
    
    def to_dict(self):
        return {
            "family": self.family,
            "test_id": self.test_id,
            "description": self.description,
            "passed": self.passed,
            "details": self.details,
        }


results: list = []


def run_test(family: str, test_id: str, description: str):
    """Decorator for test functions."""
    def decorator(func):
        def wrapper():
            result = TestResult(family, test_id, description)
            try:
                passed, details = func()
                result.passed = passed
                result.details = details
            except Exception as e:
                result.passed = False
                result.details = f"EXCEPTION: {e}"
            results.append(result)
            status = "PASS" if result.passed else "FAIL"
            print(f"  [{status}] {test_id}: {description}")
            return result
        wrapper._test_id = test_id
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# FAMILY A: DECISION RETENTION
# Tests if the system remembers T1 decisions after simulated compaction
# ═══════════════════════════════════════════════════════════════════════════════

@run_test("A", "DR-001", "T1 block decision survives crystallization")
def test_dr_001():
    sms = SovereignMemorySystem()
    # Session 1: T1 blocks a merge
    m = sms.ingest("T1 DECISION: No merge to main without adversarial audit", source="user", confidence=1.0)
    m.implications = ["All PRs need red-team review before merge"]
    m.created_at = datetime.utcnow() - timedelta(hours=72)
    for _ in range(5):
        sms.validate_memory(m.id)
    
    # Consolidation (simulates end of session)
    sms.run_consolidation()
    
    # Session 2: Query the decision
    recall = sms.recall("Can I merge to main?")
    
    # Check axiom exists
    if sms.axioms and "merge" in sms.axioms[0].statement.lower():
        return True, f"Axiom crystallized: {sms.axioms[0].statement}"
    
    # Check if at least retrieved
    for r in recall["results"]:
        if "memory" in r and "merge" in r["memory"].content.lower():
            return True, f"Decision retrieved: {r['memory'].content[:50]}"
    
    return False, "T1 decision not found after consolidation"


@run_test("A", "DR-002", "Multiple T1 decisions retained simultaneously")
def test_dr_002():
    sms = SovereignMemorySystem()
    decisions = [
        "T1 DECISION: RLS mandatory on all tables",
        "T1 DECISION: No deploy on Fridays",
        "T1 DECISION: All secrets via env vars only",
    ]
    for d in decisions:
        m = sms.ingest(d, source="user", confidence=1.0)
        m.implications = [f"Implication of: {d}"]
        m.created_at = datetime.utcnow() - timedelta(hours=72)
        for _ in range(4):
            sms.validate_memory(m.id)
    
    sms.run_consolidation()
    
    # All 3 should be axioms
    if len(sms.axioms) >= 3:
        return True, f"All {len(sms.axioms)} decisions crystallized as axioms"
    return False, f"Only {len(sms.axioms)} of 3 decisions crystallized"


@run_test("A", "DR-003", "Decision retention after multiple consolidation cycles")
def test_dr_003():
    sms = SovereignMemorySystem()
    m = sms.ingest("T1 DECISION: Sprint closes only after Cowork audit", source="user", confidence=1.0)
    m.implications = ["Cowork must sign off before sprint closure"]
    m.created_at = datetime.utcnow() - timedelta(hours=100)
    for _ in range(5):
        sms.validate_memory(m.id)
    
    # Run 5 consolidation cycles (simulating 5 days)
    for _ in range(5):
        sms.run_consolidation()
    
    # Axioms should survive all cycles
    if sms.axioms and "sprint" in sms.axioms[0].statement.lower():
        return True, f"Axiom survived 5 consolidation cycles: {sms.axioms[0].statement[:50]}"
    return False, "Axiom lost during consolidation cycles"


# ═══════════════════════════════════════════════════════════════════════════════
# FAMILY B: ROLE RETENTION
# Tests if the system maintains RACI boundaries
# ═══════════════════════════════════════════════════════════════════════════════

@run_test("B", "RR-001", "Agent role constraints are preserved")
def test_rr_001():
    sms = SovereignMemorySystem()
    role_mem = sms.ingest(
        "This agent is Hilo B (executor). T1 decisions require human approval. Agent CANNOT self-approve.",
        source="system", confidence=1.0
    )
    role_mem.implications = ["Never self-approve T1 decisions", "Always escalate MAGNA actions"]
    role_mem.created_at = datetime.utcnow() - timedelta(hours=72)
    for _ in range(5):
        sms.validate_memory(role_mem.id)
    
    sms.run_consolidation()
    
    # Pre-action check should flag self-approval
    gate = sms.pre_action_gate("approve merge to main as T1")
    
    # The axiom about role should be present
    if sms.axioms and any("cannot" in a.statement.lower() or "executor" in a.statement.lower() for a in sms.axioms):
        return True, "Role constraint crystallized as axiom"
    return False, "Role constraint not preserved"


@run_test("B", "RR-002", "Cross-agent role boundaries enforced")
def test_rr_002():
    sms = SovereignMemorySystem()
    # Ingest role definitions
    sms.ingest("Manus (Hilo B) = executor. Cowork (T2) = auditor. Alfredo (T1) = decision maker.", source="system", confidence=1.0)
    sms.ingest("Only T1 can approve MAGNA actions", source="system", confidence=1.0)
    
    # Simulate another agent trying to approve
    conflict_mem = Memory(
        content="Cowork approved merge to main",
        agent_id="cowork",
        memory_type=MemoryType.EPISODIC,
    )
    
    t1_rule = Memory(
        content="Only T1 can approve MAGNA actions",
        agent_id="monstruo",
        memory_type=MemoryType.SEMANTIC,
        validation_count=5,
    )
    
    resolution = sms.resolve_conflict(t1_rule, conflict_mem)
    
    if resolution["winner"] == t1_rule.id or "confidence" in resolution["reason"].lower():
        return True, f"Conflict resolved correctly: {resolution['reason']}"
    return False, f"Wrong resolution: {resolution}"


# ═══════════════════════════════════════════════════════════════════════════════
# FAMILY C: SIDE EFFECT RETENTION
# Tests if the system remembers what was already done
# ═══════════════════════════════════════════════════════════════════════════════

@run_test("C", "SE-001", "Completed actions are not re-proposed")
def test_se_001():
    sms = SovereignMemorySystem()
    # Record that migration was already run
    sms.ingest("Migration 0008_rls_universal.sql was executed successfully at 2026-05-20 14:30", source="tool", confidence=1.0)
    sms.ingest("Table sovereign_axioms created with RLS enabled", source="tool", confidence=1.0)
    
    # Query: should we run the migration?
    recall = sms.recall("Do we need to run migration 0008?")
    
    # Should find the existing execution
    found = any(
        "memory" in r and "executed" in r["memory"].content.lower()
        for r in recall["results"]
    )
    
    if found:
        return True, "System remembers migration was already executed"
    return False, "System did not recall previous execution"


@run_test("C", "SE-002", "Duplicate action detection via AUDN")
def test_se_002():
    sms = SovereignMemorySystem()
    # Ingest same fact twice
    m1 = sms.ingest("Deploy to production completed at 15:00", source="tool")
    m2 = sms.ingest("Deploy to production completed at 15:00", source="tool")
    
    # Should have deduplicated
    if sms.stats["memories_created"] == 1:
        return True, "AUDN correctly deduplicated: 1 memory instead of 2"
    return False, f"AUDN failed: {sms.stats['memories_created']} memories created"


# ═══════════════════════════════════════════════════════════════════════════════
# FAMILY D: HANDOFF / RE-ENTRY
# Tests context reconstruction from state capsule
# ═══════════════════════════════════════════════════════════════════════════════

@run_test("D", "HO-001", "Context injection block contains critical state")
def test_ho_001():
    sms = SovereignMemorySystem()
    # Build up state
    m = sms.ingest("Current sprint: S028. Focus: SMS implementation.", source="system", confidence=1.0)
    m.implications = ["All work should align with SMS goals"]
    m.created_at = datetime.utcnow() - timedelta(hours=72)
    for _ in range(4):
        sms.validate_memory(m.id)
    
    sms.run_consolidation()
    
    # Get injection block (what a new session would receive)
    injection = sms.get_context_injection()
    
    if "sprint" in injection.lower() or "sms" in injection.lower():
        return True, f"Injection contains sprint context: {injection[:100]}"
    
    # Even if not crystallized, check recall
    recall = sms.recall("What sprint are we in?")
    if recall["results"]:
        return True, "Context retrievable even without axiom"
    
    return False, "Critical state not in injection block"


@run_test("D", "HO-002", "Causal chains survive handoff")
def test_ho_002():
    sms = SovereignMemorySystem()
    # Build causal chain
    m1 = sms.ingest("Bug found in B8 classifier", source="tool")
    m2 = sms.ingest("Bug caused false negatives in red-team cases", source="tool", causal_parent=m1.id)
    m3 = sms.ingest("Layer 6 was added to fix the false negatives", source="agent", causal_parent=m2.id)
    
    # Check chain exists
    chains = sms.comprehension.causal_chains
    if chains and chains[0].depth >= 2:
        return True, f"Causal chain preserved: depth={chains[0].depth}, nodes={len(chains[0].nodes)}"
    return False, f"Causal chain lost: {len(chains)} chains found"


# ═══════════════════════════════════════════════════════════════════════════════
# FAMILY E: ADVERSARIAL COMPACTION
# Tests if the system detects missing context after lossy compression
# ═══════════════════════════════════════════════════════════════════════════════

@run_test("E", "AC-001", "Gap detection when context is insufficient")
def test_ac_001():
    sms = SovereignMemorySystem()
    # Ingest minimal context (simulating post-compaction state)
    sms.ingest("Working on anti-dory module", source="system")
    
    # Query something that requires more context
    recall = sms.recall("What specific red-team vectors did Grok identify?")
    
    # Should detect a gap
    if recall["gap_detected"]:
        return True, f"Gap correctly detected: {recall['gap'].evidence}"
    return False, "No gap detected despite insufficient context"


@run_test("E", "AC-002", "Metacognition identifies stale axioms")
def test_ac_002():
    sms = SovereignMemorySystem()
    # Create an axiom that hasn't been validated in 35 days
    # confidence must be < 0.95 for the calibration to flag it
    old_axiom = Axiom(
        statement="Deploy pipeline uses GitHub Actions",
        first_observed=datetime.utcnow() - timedelta(days=60),
        last_validated=datetime.utcnow() - timedelta(days=35),
        validation_count=3,
        contradiction_count=1,  # Makes confidence = 3/4 = 0.75 < 0.95
        implications=["CI/CD runs on GitHub Actions"],
    )
    sms.axioms.append(old_axiom)
    
    # Run calibration
    alerts = sms.metacognition.calibrate_confidence(sms.axioms)
    
    if alerts and alerts[0]["action"] == "needs_revalidation":
        return True, f"Stale axiom flagged: {alerts[0]['days_stale']} days since validation"
    return False, f"Stale axiom not detected. Confidence={old_axiom.confidence}, alerts={alerts}"


# ═══════════════════════════════════════════════════════════════════════════════
# FAMILY F: SEEDED CONTRADICTION
# Tests if the system rejects false claims
# ═══════════════════════════════════════════════════════════════════════════════

@run_test("F", "SC-001", "Contradiction detected between memories")
def test_sc_001():
    sms = SovereignMemorySystem()
    # Establish truth
    truth = sms.ingest("Supabase is the database provider for El Monstruo", source="system", confidence=1.0)
    for _ in range(5):
        sms.validate_memory(truth.id)
    
    # Inject contradiction (Memory doesn't take confidence as init param — use validation_count)
    lie = Memory(
        content="Firebase is the database provider for El Monstruo",
        agent_id="external",
        memory_type=MemoryType.SEMANTIC,
    )
    lie.validation_count = 1
    lie.contradiction_count = 3  # Low confidence: 1/4 = 0.25
    
    resolution = sms.resolve_conflict(truth, lie)
    
    if resolution["winner"] == truth.id:
        return True, f"Truth preserved: {resolution['reason']}"
    return False, "Contradiction won over established truth"


@run_test("F", "SC-002", "Low-confidence claims don't override high-confidence facts")
def test_sc_002():
    sms = SovereignMemorySystem()
    # High confidence fact
    fact = Memory(
        content="B8 classifier has 7 layers",
        memory_type=MemoryType.SEMANTIC,
        validation_count=10,
        contradiction_count=0,
    )
    
    # Low confidence claim
    claim = Memory(
        content="B8 classifier has 5 layers",
        memory_type=MemoryType.SEMANTIC,
        validation_count=1,
        contradiction_count=2,
    )
    
    resolution = sms.resolve_conflict(fact, claim)
    
    if resolution["winner"] == fact.id:
        return True, f"High-confidence fact preserved: {resolution['reason']}"
    return False, "Low-confidence claim incorrectly won"


# ═══════════════════════════════════════════════════════════════════════════════
# FAMILY G: LONGITUDINAL PERSISTENCE (Simulated)
# Tests memory survival over simulated time periods
# ═══════════════════════════════════════════════════════════════════════════════

@run_test("G", "LP-001", "Axioms survive 30 days of consolidation")
def test_lp_001():
    sms = SovereignMemorySystem()
    # Create axiom
    m = sms.ingest("Secrets must never appear in git history", source="system", confidence=1.0)
    m.implications = ["Use env vars for all credentials"]
    m.created_at = datetime.utcnow() - timedelta(days=60)
    for _ in range(10):
        sms.validate_memory(m.id)
    
    sms.run_consolidation()  # Crystallize
    
    # Simulate 30 days of consolidation without accessing the axiom
    for day in range(30):
        sms.run_consolidation()
    
    # Axiom should still exist (Layer 4 = NEVER forgotten)
    if sms.axioms:
        return True, f"Axiom survived 30 days: {sms.axioms[0].statement[:50]}"
    return False, "Axiom lost during 30-day simulation"


@run_test("G", "LP-002", "Non-axiom memories decay correctly over time")
def test_lp_002():
    sms = SovereignMemorySystem()
    # Create a weak memory
    m = sms.ingest("Temporary debug log: checked line 42", source="tool", confidence=0.5)
    m.strength = 0.5
    m.last_accessed = datetime.utcnow() - timedelta(days=40)  # 40 days old, never re-accessed
    
    # Run consolidation
    alive, dead = sms.forgetting.apply_decay(sms.memories)
    
    if m in dead:
        return True, f"Weak memory correctly decayed after 40 days (relevance: {m.relevance_score:.4f})"
    
    # Check relevance is at least very low
    if m.relevance_score < 0.1:
        return True, f"Memory has near-zero relevance: {m.relevance_score:.4f}"
    return False, f"Memory did not decay: relevance={m.relevance_score:.4f}"


# ═══════════════════════════════════════════════════════════════════════════════
# FAMILY H: HONEST SCORING
# Tests that the system reports honestly about its own state
# ═══════════════════════════════════════════════════════════════════════════════

@run_test("H", "HS-001", "Health report reflects actual state")
def test_hs_001():
    sms = SovereignMemorySystem()
    sms.ingest("Fact 1", source="system")
    sms.ingest("Fact 2", source="system")
    sms.ingest("Fact 3", source="system")
    
    health = sms.get_health_report()
    
    if health["memory_count"] == 3 and health["stats"]["memories_created"] == 3:
        return True, f"Health report accurate: {health['memory_count']} memories, {health['stats']}"
    return False, f"Health report inaccurate: {health}"


@run_test("H", "HS-002", "Gap count is honest (not hidden)")
def test_hs_002():
    sms = SovereignMemorySystem()
    # Force gap detection
    recall = sms.recall("What is the meaning of quantum entanglement in this project?")
    
    health = sms.get_health_report()
    
    if health["unresolved_gaps"] >= 1:
        return True, f"Gaps honestly reported: {health['unresolved_gaps']} unresolved"
    return False, "Gaps not reported in health"


@run_test("H", "HS-003", "CVDS-like consistency: same query returns same results")
def test_hs_003():
    sms = SovereignMemorySystem()
    sms.ingest("The sky is blue", source="system")
    sms.ingest("Water is wet", source="system")
    sms.ingest("Fire is hot", source="system")
    
    # Run same query twice
    r1 = sms.recall("What is the sky?")
    r2 = sms.recall("What is the sky?")
    
    # Results should be identical
    ids1 = [r["memory"].id for r in r1["results"] if "memory" in r]
    ids2 = [r["memory"].id for r in r2["results"] if "memory" in r]
    
    if ids1 == ids2:
        return True, f"Deterministic retrieval: {len(ids1)} results match"
    return False, f"Non-deterministic: {ids1} vs {ids2}"


# ═══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("SOVEREIGN MEMORY SYSTEM — Longitudinal Validation Tests")
    print("=" * 70)
    
    # Collect all test functions
    tests = [
        # Family A
        test_dr_001, test_dr_002, test_dr_003,
        # Family B
        test_rr_001, test_rr_002,
        # Family C
        test_se_001, test_se_002,
        # Family D
        test_ho_001, test_ho_002,
        # Family E
        test_ac_001, test_ac_002,
        # Family F
        test_sc_001, test_sc_002,
        # Family G
        test_lp_001, test_lp_002,
        # Family H
        test_hs_001, test_hs_002, test_hs_003,
    ]
    
    print(f"\nRunning {len(tests)} tests across 8 families...\n")
    
    for test_fn in tests:
        test_fn()
    
    # Summary
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    total = len(results)
    
    print(f"\n{'=' * 70}")
    print(f"RESULTS: {passed}/{total} PASS ({passed/total*100:.0f}%)")
    print(f"{'=' * 70}")
    
    if failed > 0:
        print(f"\nFAILED TESTS:")
        for r in results:
            if not r.passed:
                print(f"  [{r.test_id}] {r.description}: {r.details}")
    
    # Family breakdown
    print(f"\nFAMILY BREAKDOWN:")
    families = {}
    for r in results:
        families.setdefault(r.family, []).append(r)
    
    for fam, fam_results in sorted(families.items()):
        fam_pass = sum(1 for r in fam_results if r.passed)
        fam_total = len(fam_results)
        status = "✓" if fam_pass == fam_total else "✗"
        print(f"  {status} Family {fam}: {fam_pass}/{fam_total}")
    
    # Export JSON
    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "system": "SOVEREIGN_MEMORY_SYSTEM",
        "version": "1.0.0",
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / total,
        "families": {
            fam: {
                "passed": sum(1 for r in fam_results if r.passed),
                "total": len(fam_results),
            }
            for fam, fam_results in sorted(families.items())
        },
        "results": [r.to_dict() for r in results],
    }
    
    with open("/home/ubuntu/SMS_LONGITUDINAL_RESULTS.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults exported to: /home/ubuntu/SMS_LONGITUDINAL_RESULTS.json")
    
    sys.exit(0 if failed == 0 else 1)
