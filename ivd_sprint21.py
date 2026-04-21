#!/usr/bin/env python3
"""
IVD Post-Implementation Validation — Sprint 21
================================================
Validates all Sprint 21 changes compile and are structurally correct.
"""

import ast
import importlib
import os
import sys

# Ensure project root is in path
sys.path.insert(0, "/home/ubuntu/el-monstruo-kernel")

PASS = 0
FAIL = 0
WARN = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name} — {detail}")

def warn(name, detail=""):
    global WARN
    WARN += 1
    print(f"  ⚠️  WARN: {name} — {detail}")

print("=" * 70)
print("IVD Sprint 21 — Post-Implementation Validation")
print("=" * 70)

# ── 1. Syntax Validation ─────────────────────────────────────────────
print("\n📋 1. SYNTAX VALIDATION")

files_to_check = [
    "kernel/main.py",
    "kernel/nodes.py",
    "kernel/state.py",
    "kernel/hitl.py",
    "kernel/multi_agent.py",
    "kernel/mcp_client.py",
    "kernel/engine.py",
    "memory/mempalace_bridge.py",
    "bot/__init__.py",
    "bot/hitl_handler.py",
]

for f in files_to_check:
    path = f"/home/ubuntu/el-monstruo-kernel/{f}"
    try:
        with open(path) as fh:
            ast.parse(fh.read())
        check(f"Syntax OK: {f}", True)
    except SyntaxError as e:
        check(f"Syntax OK: {f}", False, str(e))
    except FileNotFoundError:
        check(f"File exists: {f}", False, "File not found")

# ── 2. Import Validation ─────────────────────────────────────────────
print("\n📋 2. IMPORT VALIDATION")

# bot.hitl_handler
try:
    from bot.hitl_handler import get_pending_reviews, get_pending_count, add_pending_review, remove_pending_review
    check("bot.hitl_handler imports", True)
    check("get_pending_reviews() returns dict", isinstance(get_pending_reviews(), dict))
    check("get_pending_count() returns int", isinstance(get_pending_count(), int))
except Exception as e:
    check("bot.hitl_handler imports", False, str(e))

# kernel.multi_agent
try:
    from kernel.multi_agent import dispatch, classify_task, AgentType, get_registry_status
    check("kernel.multi_agent imports", True)

    # Test classify_task
    result = classify_task("investiga el mercado inmobiliario")
    check("classify_task('investiga...') → RESEARCH", result == AgentType.RESEARCH)

    result = classify_task("escribe un correo")
    check("classify_task('escribe...') → CREATIVE", result == AgentType.CREATIVE)

    result = classify_task("hola")
    check("classify_task('hola') → DEFAULT", result == AgentType.DEFAULT)

    # Test dispatch
    dr = dispatch("investiga el mercado inmobiliario")
    check("dispatch() returns DispatchResult", dr.agent_type == AgentType.RESEARCH)
    check("dispatch() has system_prompt", bool(dr.system_prompt))
    check("dispatch() has tools", isinstance(dr.tools, list))

    # Test registry status
    status = get_registry_status()
    check("get_registry_status() has agents", status["total_agents"] == 6)
except Exception as e:
    check("kernel.multi_agent imports", False, str(e))

# memory.mempalace_bridge
try:
    from memory.mempalace_bridge import store_episode, store_semantic, recall, get_stats, _get_palace
    check("memory.mempalace_bridge imports", True)
except Exception as e:
    check("memory.mempalace_bridge imports", False, str(e))

# kernel.state — check new fields
try:
    from kernel.state import MonstruoState
    annotations = MonstruoState.__annotations__
    check("MonstruoState has agent_type", "agent_type" in annotations)
    check("MonstruoState has agent_system_prompt", "agent_system_prompt" in annotations)
    check("MonstruoState has agent_tools", "agent_tools" in annotations)
except Exception as e:
    check("kernel.state imports", False, str(e))

# ── 3. Version Consistency ────────────────────────────────────────────
print("\n📋 3. VERSION CONSISTENCY")

with open("/home/ubuntu/el-monstruo-kernel/kernel/main.py") as f:
    main_content = f.read()

version_count = main_content.count("0.14.0-sprint21")
old_version_count = main_content.count("0.13.0-sprint19")
check(f"Version 0.14.0-sprint21 appears {version_count} times", version_count >= 5)
check(f"Old version 0.13.0-sprint19 appears {old_version_count} times", old_version_count == 0, f"Found {old_version_count} occurrences")

# ── 4. Route Registration ────────────────────────────────────────────
print("\n📋 4. ROUTE REGISTRATION")

routes_expected = [
    "/v1/finops/status",
    "/v1/hitl/pending",
    "/v1/history",
    "/v1/mcp/status",
    "/v1/memory/status",
    "/v1/agents/status",
    "/health",
]

for route in routes_expected:
    check(f"Route registered: {route}", route in main_content)

# ── 5. Integration Points ────────────────────────────────────────────
print("\n📋 5. INTEGRATION POINTS")

with open("/home/ubuntu/el-monstruo-kernel/kernel/nodes.py") as f:
    nodes_content = f.read()

check("Multi-agent dispatch in classify_and_route", "multi_agent_dispatch" in nodes_content)
check("Agent system prompt injection in execute", "agent_system_prompt" in nodes_content)
check("MemPalace recall in enrich", "recall_mempalace" in nodes_content)
check("MemPalace store_episode in memory_write", "store_episode" in nodes_content)

# ── 6. Supabase env var fix ───────────────────────────────────────────
print("\n📋 6. SUPABASE ENV VAR FIX")

with open("/home/ubuntu/el-monstruo-kernel/kernel/mcp_client.py") as f:
    mcp_content = f.read()

check("SUPABASE_SERVICE_KEY fallback", "SUPABASE_SERVICE_KEY" in mcp_content)
check("Both env var names accepted", 'os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")' in mcp_content)

# ── 7. MemPalace Warm-up in Lifespan ─────────────────────────────────
print("\n📋 7. MEMPALACE WARM-UP")

check("MemPalace warm-up in lifespan", "mempalace_warmed_up" in main_content)
check("_mempalace_ready stored in app.state", "_mempalace_ready" in main_content)

# ── SUMMARY ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print(f"IVD Sprint 21 Results: {PASS} PASS, {FAIL} FAIL, {WARN} WARN")
print("=" * 70)

if FAIL > 0:
    print("⚠️  SOME CHECKS FAILED — Review before pushing")
    sys.exit(1)
else:
    print("✅ ALL CHECKS PASSED — Ready for commit & push")
    sys.exit(0)
