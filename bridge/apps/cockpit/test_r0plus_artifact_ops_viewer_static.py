"""
Static validation tests for R0+ Artifact Ops Viewer.
Verifies the HTML is safe, read-only, and references correct fixture.
"""

import sys
from pathlib import Path

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS [{passed + failed:02d}] {name}")
    else:
        failed += 1
        print(f"  FAIL [{passed + failed:02d}] {name}")


print("=" * 60)
print("R0+ Artifact Ops Viewer Static Tests")
print("=" * 60)

viewer_path = Path(__file__).parent / "r0plus_artifact_ops_viewer.html"
content = viewer_path.read_text(encoding="utf-8")

# 1. File exists
test("viewer file exists", viewer_path.exists())

# 2. Contains READ-ONLY banner
test("contains READ-ONLY banner", "LOCAL READ-ONLY R0+ ARTIFACT OPS VIEWER" in content)

# 3. No POST/fetch/XMLHttpRequest
test("no remote fetch", "fetch(" not in content and "XMLHttpRequest" not in content)

# 4. No localStorage/sessionStorage
test("no localStorage", "localStorage" not in content and "sessionStorage" not in content)

# 5. No secrets (sk- must not be preceded by alphanumeric to avoid 'risk-' false positive)
import re

secret_patterns_simple = ["sbp_", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "password", "Bearer"]
sk_pattern = re.search(r"(?<![a-zA-Z])sk-", content)
no_secrets = sk_pattern is None and not any(p in content for p in secret_patterns_simple)
test("no secrets", no_secrets)

# 6. No Supabase
test("no Supabase", "supabase" not in content.lower())

# 7. References v0.3 snapshot
test("references v0.3 snapshot", "v0_3" in content)

# 8. No approve/reject buttons that submit
test("no approve/reject real", "approve(" not in content and "reject(" not in content)

# 9. Contains no-production banner text
test("no production control plane", "no production control plane" in content.lower())

# 10. Valid HTML structure
test("valid HTML structure", "<html" in content and "</html>" in content and "<body" in content)

print("=" * 60)
print(f"RESULT: {passed}/{passed + failed} PASS, {failed}/{passed + failed} FAIL")
print("=" * 60)

if failed > 0:
    sys.exit(1)
