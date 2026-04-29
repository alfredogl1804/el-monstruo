"""Quick test for code_exec tool."""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from tools.code_exec import execute_code


async def test_all():
    print("=" * 60)
    print("TEST 1: HITL gate (should block without approval)")
    print("=" * 60)
    result = await execute_code(code="print('hello')", hitl_approved=False)
    assert result["status"] == "HITL_REQUIRED", f"Expected HITL_REQUIRED, got {result}"
    print(f"  PASS: {result['status']}")

    print()
    print("=" * 60)
    print("TEST 2: Python execution (with approval)")
    print("=" * 60)
    result = await execute_code(
        code="print('Hello from the Embrión')\nprint(2 + 2)",
        language="python",
        hitl_approved=True,
    )
    assert result["status"] == "success", f"Expected success, got {result}"
    assert "Hello from the Embrión" in result["stdout"], f"Missing output: {result['stdout']}"
    assert "4" in result["stdout"], f"Missing calculation: {result['stdout']}"
    print(f"  PASS: exit_code={result['exit_code']}")
    print(f"  stdout: {result['stdout'].strip()}")

    print()
    print("=" * 60)
    print("TEST 3: Shell execution (with approval)")
    print("=" * 60)
    result = await execute_code(
        code="echo 'Shell works' && echo $((6 * 7))",
        language="shell",
        hitl_approved=True,
    )
    assert result["status"] == "success", f"Expected success, got {result}"
    assert "Shell works" in result["stdout"], f"Missing output: {result['stdout']}"
    assert "42" in result["stdout"], f"Missing calculation: {result['stdout']}"
    print(f"  PASS: exit_code={result['exit_code']}")
    print(f"  stdout: {result['stdout'].strip()}")

    print()
    print("=" * 60)
    print("TEST 4: Timeout (should kill after 2 seconds)")
    print("=" * 60)
    result = await execute_code(
        code="import time; time.sleep(10); print('should not appear')",
        language="python",
        timeout=2,
        hitl_approved=True,
    )
    assert result["status"] == "timeout", f"Expected timeout, got {result}"
    print(f"  PASS: {result['status']} — {result['error']}")

    print()
    print("=" * 60)
    print("TEST 5: Error handling (bad code)")
    print("=" * 60)
    result = await execute_code(
        code="raise ValueError('intentional error')",
        language="python",
        hitl_approved=True,
    )
    assert result["status"] == "error", f"Expected error, got {result}"
    assert result["exit_code"] != 0
    print(f"  PASS: exit_code={result['exit_code']}")
    print(f"  stderr: {result['stderr'].strip()[:200]}")

    print()
    print("=" * 60)
    print("TEST 6: Secrets NOT leaked")
    print("=" * 60)
    # Set a fake secret to verify it's blocked
    os.environ["OPENAI_API_KEY"] = "sk-test-secret-12345"
    result = await execute_code(
        code="import os; print(os.environ.get('OPENAI_API_KEY', 'NOT_FOUND'))",
        language="python",
        hitl_approved=True,
    )
    assert "sk-test-secret" not in result["stdout"], f"SECRET LEAKED: {result['stdout']}"
    assert "NOT_FOUND" in result["stdout"], f"Expected NOT_FOUND, got {result['stdout']}"
    print(f"  PASS: Secret not leaked. stdout: {result['stdout'].strip()}")

    print()
    print("=" * 60)
    print("TEST 7: Invalid language")
    print("=" * 60)
    result = await execute_code(
        code="console.log('hi')",
        language="javascript",
        hitl_approved=True,
    )
    assert "error" in result, f"Expected error, got {result}"
    print(f"  PASS: {result['error']}")

    print()
    print("=" * 60)
    print("ALL 7 TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_all())
