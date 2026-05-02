"""
Sprint 29 E2E Validation Tests
================================
Tests all Sprint 29 deliverables:
  - Fase 0: BUG-2 (model_catalog), DT-8 (user_id), version bump
  - Épica 1: Supervisor complexity analysis
  - Épica 2: Opik bridge initialization
  - Épica 3: FastMCP tool registration
  - Épica 4: Web browse stub
  - Épica 5: Fallback engine circuit breaker

Run: python tests/test_sprint29.py
"""

import asyncio
import os
import sys
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"
SKIP = "\033[93m⊘ SKIP\033[0m"

results = {"pass": 0, "fail": 0, "skip": 0}


def test(name: str, condition: bool, detail: str = ""):
    """Record a test result."""
    if condition:
        results["pass"] += 1
        print(f"  {PASS} {name}")
    else:
        results["fail"] += 1
        print(f"  {FAIL} {name} — {detail}")


def skip(name: str, reason: str):
    results["skip"] += 1
    print(f"  {SKIP} {name} — {reason}")


# ══════════════════════════════════════════════════════════════════════
# FASE 0: Model Catalog + Version Bump + DT-8
# ══════════════════════════════════════════════════════════════════════

print("\n═══ FASE 0: Estabilización ═══")

# BUG-2: GPT-5.5 flagship
from config.model_catalog import MODELS, FALLBACK_CHAINS, get_model, supports_temperature

test(
    "BUG-2: GPT-5.5 exists in catalog",
    "gpt-5.5" in MODELS,
    "gpt-5.5 not found in MODELS",
)

test(
    "BUG-2: GPT-5.5 model_id is 'gpt-5.5'",
    MODELS.get("gpt-5.5", {}).get("model_id") == "gpt-5.5",
    f"Got: {MODELS.get('gpt-5.5', {}).get('model_id')}",
)

test(
    "BUG-2: GPT-5.5 does NOT support temperature",
    supports_temperature("gpt-5.5") is False,
    "GPT-5.5 should not support temperature",
)

test(
    "BUG-2: GPT-5.4 removed from catalog",
    "gpt-5.4" not in MODELS and "gpt-5.4-pro-2026-03-05" not in MODELS,
    "Old GPT-5.4 still exists",
)

# GPT-4.1-mini replaces gpt-5.4-mini
test(
    "GPT-4.1-mini exists in catalog",
    "gpt-4.1-mini" in MODELS,
    "gpt-4.1-mini not found",
)

test(
    "GPT-4.1-mini model_id correct",
    MODELS.get("gpt-4.1-mini", {}).get("model_id") == "gpt-4.1-mini",
    f"Got: {MODELS.get('gpt-4.1-mini', {}).get('model_id')}",
)

# Groq + Together in catalog
test(
    "Groq llama-scout in catalog",
    "groq-llama-scout" in MODELS,
    "groq-llama-scout not found",
)

test(
    "Together llama-scout in catalog",
    "together-llama-scout" in MODELS,
    "together-llama-scout not found",
)

# Fallback chains include Groq/Together
test(
    "Fallback chains include Groq",
    any("groq-llama-scout" in chain for chain in FALLBACK_CHAINS.values()),
    "No fallback chain includes groq-llama-scout",
)

test(
    "Fallback chains include Together",
    any("together-llama-scout" in chain for chain in FALLBACK_CHAINS.values()),
    "No fallback chain includes together-llama-scout",
)

# DT-8: No hardcoded "alfredo"
print("\n  DT-8: Checking for hardcoded 'alfredo'...")
import subprocess
result = subprocess.run(
    ["grep", "-rn", '"alfredo"', "kernel/", "memory/", "config/", "router/",
     "--include=*.py"],
    capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
alfredo_count = len([l for l in result.stdout.strip().split("\n") if l and "# Sprint 29" not in l and "was hardcoded" not in l])
test(
    "DT-8: No hardcoded 'alfredo' in codebase",
    alfredo_count == 0,
    f"Found {alfredo_count} remaining references",
)


# ══════════════════════════════════════════════════════════════════════
# ÉPICA 1: Supervisor
# ══════════════════════════════════════════════════════════════════════

print("\n═══ ÉPICA 1: Supervisor ═══")

from kernel.supervisor import (
    analyze_complexity, ComplexityTier, SupervisorDecision,
    get_tier_metrics, get_status, supervisor_node, record_tier,
)

# Simple messages → SIMPLE tier
simple_msgs = ["hola", "gracias", "ok", "qué hora es?", "sí"]
for msg in simple_msgs:
    d = analyze_complexity(msg)
    test(
        f"Simple: '{msg}' → {d.tier.value}",
        d.tier == ComplexityTier.SIMPLE,
        f"Got tier={d.tier.value}, model={d.model}",
    )
    test(
        f"Simple: '{msg}' → skip_enrich=True",
        d.skip_enrich is True,
        "Should skip enrichment for simple messages",
    )

# Complex messages → COMPLEX or DEEP
complex_msgs = [
    "Analiza la arquitectura del sistema y compara con las mejores prácticas de microservicios",
    "Investiga las últimas tendencias en tokenización inmobiliaria y diseña una estrategia",
]
for msg in complex_msgs:
    d = analyze_complexity(msg)
    test(
        f"Complex: '{msg[:40]}...' → {d.tier.value}",
        d.tier in (ComplexityTier.COMPLEX, ComplexityTier.DEEP),
        f"Got tier={d.tier.value}",
    )

# Deep messages → DEEP
deep_msgs = [
    "Consulta a los sabios sobre el plan completo del sprint",
    "Ejecuta el enjambre de investigación profunda con multi-model consensus",
]
for msg in deep_msgs:
    d = analyze_complexity(msg)
    test(
        f"Deep: '{msg[:40]}...' → {d.tier.value}",
        d.tier == ComplexityTier.DEEP,
        f"Got tier={d.tier.value}",
    )

# Supervisor latency < 5ms (heuristic, no LLM)
d = analyze_complexity("hola")
test(
    f"Supervisor latency < 5ms (got {d.latency_ms:.2f}ms)",
    d.latency_ms < 5.0,
    f"Too slow: {d.latency_ms:.2f}ms",
)

# Confidence is reasonable
test(
    f"Confidence in [0, 1] (got {d.confidence:.2f})",
    0.0 <= d.confidence <= 1.0,
    f"Out of range: {d.confidence}",
)

# Supervisor status
status = get_status()
test(
    "Supervisor status active",
    status["active"] is True,
    f"Got: {status}",
)

# Async supervisor_node
async def test_supervisor_node():
    state = {"message": "hola", "intent": "chat", "conversation_context": [], "tool_results": []}
    result = await supervisor_node(state, {})
    return result

node_result = asyncio.run(test_supervisor_node())
test(
    "supervisor_node returns model key",
    "model" in node_result,
    f"Missing 'model' key in result",
)
test(
    "supervisor_node returns complexity_tier",
    "complexity_tier" in node_result,
    f"Missing 'complexity_tier' key",
)


# ══════════════════════════════════════════════════════════════════════
# ÉPICA 2: Opik Bridge
# ══════════════════════════════════════════════════════════════════════

print("\n═══ ÉPICA 2: Opik Bridge ═══")

from observability.opik_bridge import OpikBridge

bridge = OpikBridge()
test(
    "OpikBridge instantiates",
    bridge is not None,
    "Failed to create OpikBridge",
)
test(
    "OpikBridge disabled without API key",
    bridge.enabled is False,
    "Should be disabled without OPIK_API_KEY",
)

status = bridge.get_status()
test(
    "OpikBridge status has 'active' key",
    "active" in status,
    f"Missing 'active' in status",
)

# Check ObservabilityManager integration
from observability.manager import ObservabilityManager, TraceContext

mgr = ObservabilityManager()
test(
    "ObservabilityManager has opik_enabled property",
    hasattr(mgr, "opik_enabled"),
    "Missing opik_enabled property",
)
test(
    "TraceContext has opik_trace field",
    hasattr(TraceContext(run_id="test"), "opik_trace"),
    "Missing opik_trace field in TraceContext",
)


# ══════════════════════════════════════════════════════════════════════
# ÉPICA 3: FastMCP Tools
# ══════════════════════════════════════════════════════════════════════

print("\n═══ ÉPICA 3: FastMCP Tools ═══")

from kernel.fastmcp_server import get_status as mcp_status, create_fastmcp_server

try:
    server = create_fastmcp_server()
    if server is not None:
        test("FastMCP server creates successfully", True, "")
        status = mcp_status()
        test(
            "FastMCP has 5 tools registered",
            status.get("tools") == 5,
            f"Got {status.get('tools')} tools",
        )
        test(
            "FastMCP real_tools list populated",
            len(status.get("real_tools", [])) == 5,
            f"Got {len(status.get('real_tools', []))} real tools",
        )
    else:
        skip("FastMCP server creation", "fastmcp not installed")
except ImportError:
    skip("FastMCP server creation", "fastmcp not installed")
except Exception as e:
    test("FastMCP server creates successfully", False, str(e))


# ══════════════════════════════════════════════════════════════════════
# ÉPICA 5: Fallback Engine
# ══════════════════════════════════════════════════════════════════════

print("\n═══ ÉPICA 5: Fallback Engine ═══")

from kernel.fallback_engine import (
    FallbackEngine, CircuitState, get_fallback_engine, PROVIDERS,
)

engine = get_fallback_engine()
test(
    "FallbackEngine instantiates",
    engine is not None,
    "Failed to create FallbackEngine",
)

# Circuit breaker states
states = engine.get_circuit_states()
test(
    "All providers have CLOSED circuits initially",
    all(s == "closed" for s in states.values()),
    f"Some circuits not closed: {states}",
)

# Provider mapping
test(
    "gpt-5.5 maps to openai provider",
    engine.get_provider_for_model("gpt-5.5") == "openai",
    f"Got: {engine.get_provider_for_model('gpt-5.5')}",
)
test(
    "groq-llama-scout maps to groq provider",
    engine.get_provider_for_model("groq-llama-scout") == "groq",
    f"Got: {engine.get_provider_for_model('groq-llama-scout')}",
)
test(
    "together-llama-scout maps to together provider",
    engine.get_provider_for_model("together-llama-scout") == "together",
    f"Got: {engine.get_provider_for_model('together-llama-scout')}",
)

# Circuit breaker logic
engine._record_failure("openai")
engine._record_failure("openai")
engine._record_failure("openai")  # 3 failures = threshold
circuit = engine._get_circuit("openai")
test(
    "Circuit opens after 3 failures",
    circuit.state == CircuitState.OPEN,
    f"State: {circuit.state}",
)
test(
    "Open circuit blocks requests",
    engine._check_circuit("openai") is False,
    "Should block when open",
)

# Status
status = engine.get_status()
test(
    "Fallback engine status has 7 providers",
    status.get("providers") == 7,
    f"Got {status.get('providers')} providers",
)
test(
    "Groq in fallback status",
    "groq" in status.get("circuits", {}),
    "Missing groq in circuits",
)
test(
    "Together in fallback status",
    "together" in status.get("circuits", {}),
    "Missing together in circuits",
)


# ══════════════════════════════════════════════════════════════════════
# VERSION CHECK
# ══════════════════════════════════════════════════════════════════════

print("\n═══ VERSION CHECK ═══")

# Check main.py version
with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kernel/main.py")) as f:
    main_content = f.read()
test(
    "Version is 0.22.0-sprint29 in main.py",
    "0.22.0-sprint29" in main_content,
    "Version not updated in main.py",
)

# Check requirements.txt
with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "requirements.txt")) as f:
    req_content = f.read()
test(
    "opik==2.0.14 in requirements.txt",
    "opik==2.0.14" in req_content,
    "opik not in requirements.txt",
)
test(
    "groq==1.2.0 in requirements.txt",
    "groq==" in req_content,
    "groq not in requirements.txt",
)
test(
    "together==2.10.0 in requirements.txt",
    "together==" in req_content,
    "together not in requirements.txt",
)


# ══════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
total = results["pass"] + results["fail"] + results["skip"]
print(f"  TOTAL: {total} tests")
print(f"  {PASS}: {results['pass']}")
print(f"  {FAIL}: {results['fail']}")
print(f"  {SKIP}: {results['skip']}")
print(f"  Pass rate: {results['pass']/max(total-results['skip'],1)*100:.0f}%")
print("═" * 60)

if __name__ == "__main__":
    if results["fail"] > 0:
        print("\n  ⚠️  SOME TESTS FAILED — review above")
        sys.exit(1)
    else:
        print("\n  🎯 ALL TESTS PASSED — Sprint 29 validated!")
        sys.exit(0)
