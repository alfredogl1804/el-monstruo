"""Smoke test local del Sprint 84 — sin tocar APIs externas."""
import sys

sys.path.insert(0, ".")

from kernel.embrion_loop import EmbrionLoop
from tools.deploy_app import (
    DeployAppFalla,
    _decide_target,
    execute_deploy_app,
)
from tools.deploy_to_github_pages import (
    GitHubPagesDeployFalla,
    execute_deploy_to_github_pages,
)
from tools.deploy_to_railway import (
    RailwayDeployFalla,
    RailwayMissingToken,
    execute_deploy_to_railway,
)

print("OK imports (3 tools + EmbrionLoop)")

# Magna decide
target, motivo, conf = _decide_target({"index.html": "<html></html>", "style.css": "body{}"})
assert target == "github_pages" and conf >= 0.9
print(f"OK Magna estatico: {target} conf={conf}")

target, motivo, conf = _decide_target({"main.py": "x", "requirements.txt": "flask"})
assert target == "railway" and conf >= 0.9
print(f"OK Magna python backend: {target} conf={conf}")

target, motivo, conf = _decide_target({"index.js": "x", "package.json": "{}"})
assert target == "railway"
print(f"OK Magna node backend: {target} conf={conf}")

target, motivo, conf = _decide_target({"Dockerfile": "FROM python", "app.py": "x"})
assert target == "railway"
print(f"OK Magna docker: {target} conf={conf}")

try:
    _decide_target({})
except DeployAppFalla:
    print("OK Magna rechaza files vacios")

# EmbrionLoop helpers
loop = EmbrionLoop(db=None, kernel=None)
loop.start_orchestration("smoke test trigger")
loop.report_orchestration_step("paso1", "agent_a", "in_flight")
loop.report_orchestration_step("paso1", "agent_a", "done", tokens=100, cost_usd=0.01)
assert loop._current_orchestration["current_step"] == 1
assert loop._current_orchestration["cost_so_far_usd"] == 0.01
loop.end_orchestration("done")
assert loop._current_orchestration is None
assert loop._last_orchestration["final_status"] == "done"
print("OK EmbrionLoop helpers (start/report/end)")

print("\n✅ SMOKE TESTS LOCAL: TODOS PASARON")
