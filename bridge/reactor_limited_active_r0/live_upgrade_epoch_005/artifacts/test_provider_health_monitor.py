"""Tests for Provider Health Monitor v0.1"""
import json
import os
import sys
import tempfile
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))
from provider_health_monitor_v0_1 import (
    analyze_provider_health,
    generate_health_report,
    check_kill_switch
)

PASS = 0
FAIL = 0

def test(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")

# Test 1: Empty entries returns empty stats
stats = analyze_provider_health([], {})
test("Empty entries → empty stats", len(stats) == 0)

# Test 2: Single success entry
entries = [{"provider": "openai", "status": "SUCCESS", "cost": 0.001, "latency": 2.0, "timestamp": "2026-05-21T04:00:00Z"}]
stats = analyze_provider_health(entries, {})
test("Single success → 1 provider", len(stats) == 1)
test("Single success → success count", stats["openai"]["successes"] == 1)

# Test 3: Multiple providers
entries = [
    {"provider": "openai", "status": "SUCCESS", "cost": 0.001, "latency": 2.0, "timestamp": "2026-05-21T04:00:00Z"},
    {"provider": "anthropic", "status": "SUCCESS", "cost": 0.003, "latency": 8.0, "timestamp": "2026-05-21T04:00:01Z"},
    {"provider": "google", "status": "FAILED", "error": "model_not_found", "timestamp": "2026-05-21T04:00:02Z"},
]
stats = analyze_provider_health(entries, {})
test("Multiple providers → 3 found", len(stats) == 3)
test("Google has 1 failure", stats["google"]["failures"] == 1)

# Test 4: Health report generation
report = generate_health_report(stats, {})
test("Report has providers", "providers" in report)
test("Report has alerts", "alerts" in report)
test("Report has summary", "summary" in report)
test("Summary total = 3", report["summary"]["total_providers_monitored"] == 3)

# Test 5: HEALTHY status for 100% success rate
test("OpenAI is HEALTHY", report["providers"]["openai"]["status"] == "HEALTHY")

# Test 6: UNHEALTHY status for 0% success rate
test("Google is UNHEALTHY", report["providers"]["google"]["status"] == "UNHEALTHY")

# Test 7: Alert generated for low success rate
low_rate_alerts = [a for a in report["alerts"] if a["type"] == "LOW_SUCCESS_RATE"]
test("Alert for low success rate exists", len(low_rate_alerts) > 0)

# Test 8: Cost tracking
test("OpenAI cost tracked", stats["openai"]["total_cost"] == 0.001)

# Test 9: Latency tracking
test("OpenAI latency tracked", stats["openai"]["latencies"] == [2.0])

# Test 10: Embryo-based entries (verdict instead of status)
entries_embryo = [
    {"embryo": "oracle_ai_embryo_r0", "verdict": "AUTONOMOUS_CYCLE_COMPLETE", "cost_usd": 0.0003, "timestamp": "2026-05-21T04:27:00Z"},
]
stats_e = analyze_provider_health(entries_embryo, {})
test("Embryo entries parsed", "oracle_ai_embryo_r0" in stats_e)
test("Embryo success counted", stats_e["oracle_ai_embryo_r0"]["successes"] == 1)

# Test 11: No external API calls in artifact
import inspect
source = inspect.getsource(analyze_provider_health)
test("No requests import", "requests" not in source)

# Test 12: No secrets in artifact
artifact_path = Path(__file__).parent / "provider_health_monitor_v0_1.py"
content = artifact_path.read_text()
test("No API keys in artifact", "OPENAI_API_KEY" not in content and "ANTHROPIC_API_KEY" not in content)

print(f"\n{'='*40}")
print(f"Results: {PASS}/{PASS+FAIL} PASS")
if FAIL > 0:
    print(f"FAILURES: {FAIL}")
    sys.exit(1)
else:
    print("ALL PASS")
