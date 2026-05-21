"""
Test Suite: R0+ Cost Anomaly Guard v0.1
Sprint: SPR-R0PLUS-PRODUCTION-SURGE-002

14 tests covering:
- Empty history handling
- Statistics computation
- Z-score calculation
- Anomaly classification (NORMAL, WARNING, SPIKE, CRITICAL)
- Drift detection (detected, not detected, insufficient data)
- Recommendations generation
- Full analyze() integration
- Guard status (GREEN, YELLOW, RED)
- Custom config thresholds

Constraints: No network, no Supabase, no secrets, no DB.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r0plus_cost_anomaly_guard_v0_1 import CostAnomalyGuard, run

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS [{passed:02d}] {name}")
    else:
        failed += 1
        print(f"  FAIL [{passed + failed:02d}] {name}")


print("=" * 60)
print("TEST SUITE: R0+ Cost Anomaly Guard v0.1 — 14 Tests")
print("=" * 60)

# 1. Empty history returns GREEN
result = run([])
test("01. empty history returns GREEN guard_status",
     result["guard_status"] == "GREEN")

# 2. Statistics on empty = zeros
test("02. empty history statistics are zeros",
     result["statistics"]["mean"] == 0.0 and result["statistics"]["count"] == 0)

# 3. Normal costs produce no anomalies
normal_history = [{"cost_usd": 0.001, "timestamp": f"2026-05-{i:02d}T00:00:00Z"} for i in range(1, 11)]
result_normal = run(normal_history)
test("03. uniform costs produce 0 anomalies",
     result_normal["anomaly_counts"]["total"] == 0)

# 4. Single spike detected
spike_history = [{"cost_usd": 0.001} for _ in range(9)] + [{"cost_usd": 0.01}]
result_spike = run(spike_history)
test("04. single spike detected as anomaly",
     result_spike["anomaly_counts"]["total"] >= 1)

# 5. Spike classified correctly (z > 2.0)
guard = CostAnomalyGuard(spike_history)
test("05. classify_anomaly SPIKE for z=2.5",
     guard.classify_anomaly(2.5) == "SPIKE")

# 6. Critical classification
test("06. classify_anomaly CRITICAL for z=3.5",
     guard.classify_anomaly(3.5) == "CRITICAL")

# 7. Warning classification
test("07. classify_anomaly WARNING for z=1.7",
     guard.classify_anomaly(1.7) == "WARNING")

# 8. Normal classification
test("08. classify_anomaly NORMAL for z=0.5",
     guard.classify_anomaly(0.5) == "NORMAL")

# 9. Drift detection with increasing costs
drift_history = (
    [{"cost_usd": 0.001} for _ in range(5)] +
    [{"cost_usd": 0.003} for _ in range(5)]
)
guard_drift = CostAnomalyGuard(drift_history)
drift = guard_drift.detect_drift()
test("09. drift detected when late_mean >> early_mean",
     drift["detected"] is True and drift["drift_ratio"] >= 1.5)

# 10. No drift with stable costs
stable_history = [{"cost_usd": 0.001} for _ in range(10)]
guard_stable = CostAnomalyGuard(stable_history)
drift_stable = guard_stable.detect_drift()
test("10. no drift with stable costs",
     drift_stable["detected"] is False)

# 11. Insufficient data for drift
short_history = [{"cost_usd": 0.001} for _ in range(3)]
guard_short = CostAnomalyGuard(short_history)
drift_short = guard_short.detect_drift()
test("11. insufficient data returns detected=False",
     drift_short["detected"] is False and drift_short.get("reason") == "insufficient_data")

# 12. Full analyze returns all required keys
full_result = run(spike_history)
required_keys = ["version", "generated_at", "guard_status", "statistics",
                 "anomalies", "anomaly_counts", "drift", "recommendations", "config"]
test("12. analyze() returns all required keys",
     all(k in full_result for k in required_keys))

# 13. RED status on critical anomaly
critical_history = [{"cost_usd": 0.001} for _ in range(19)] + [{"cost_usd": 0.05}]
result_critical = run(critical_history)
test("13. critical anomaly produces RED guard_status",
     result_critical["guard_status"] == "RED")

# 14. Custom config thresholds respected
custom_config = {"threshold_warning": 1.0, "threshold_spike": 1.5, "threshold_critical": 2.0}
guard_custom = CostAnomalyGuard(spike_history, config=custom_config)
test("14. custom config thresholds applied",
     guard_custom.threshold_warning == 1.0 and guard_custom.threshold_critical == 2.0)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
