"""
Tests for Reactor Cockpit Static HTML.
Validates security constraints: no fetch POST, no localStorage, no secrets, no approve/reject.
"""
import os
import sys

HTML_PATH = os.path.join(os.path.dirname(__file__), "reactor_limited_active_r0.html")

PASS = 0
FAIL = 0


def test(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}")


def run_tests():
    global PASS, FAIL
    print("=" * 60)
    print("Reactor Cockpit Static Tests")
    print("=" * 60)

    # Test 1: HTML file exists
    test("1. HTML file exists", os.path.isfile(HTML_PATH))

    with open(HTML_PATH, "r") as f:
        content = f.read()
    content_lower = content.lower()

    # Test 2: No fetch POST
    test("2. No fetch POST", "fetch(" not in content and ".post(" not in content_lower)

    # Test 3: No localStorage/sessionStorage
    test("3. No localStorage/sessionStorage",
         "localstorage" not in content_lower and "sessionstorage" not in content_lower)

    # Test 4: No supabase/openai/anthropic keys
    forbidden_keys = ["sk-", "sbp_", "eyJ", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "XAI_API_KEY", "SONAR_API_KEY"]
    has_keys = any(k in content for k in forbidden_keys)
    test("4. No API keys or secrets in HTML", not has_keys)

    # Test 5: No approve/reject real (no form action, no submit button)
    test("5. No approve/reject real",
         "<form" not in content_lower and "type=\"submit\"" not in content_lower and "onclick" not in content_lower)

    # Test 6: README explains local-only
    readme_path = os.path.join(os.path.dirname(__file__), "reactor_limited_active_r0_README.md")
    test("6. README exists and explains local-only",
         os.path.isfile(readme_path) and "local" in open(readme_path).read().lower())

    # Test 7: Banner present
    test("7. Banner 'LOCAL READ-ONLY REACTOR COCKPIT' present",
         "LOCAL READ-ONLY REACTOR COCKPIT" in content)

    # Test 8: No XMLHttpRequest
    test("8. No XMLHttpRequest", "xmlhttprequest" not in content_lower)

    # Test 9: No WebSocket
    test("9. No WebSocket", "websocket" not in content_lower)

    # Test 10: No supabase connection (URL/client/import)
    supabase_connection = any(x in content_lower for x in ["supabase.co", "createclient", "import supabase", "from supabase"])
    test("10. No supabase connection", not supabase_connection)

    print("=" * 60)
    print(f"Results: {PASS} PASS, {FAIL} FAIL, {PASS + FAIL} total")
    print("=" * 60)

    return FAIL == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
