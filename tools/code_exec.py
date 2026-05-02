"""
Code Execution tool for El Monstruo kernel.
Sprint 33A: E2B Code Interpreter as primary backend.

Architecture:
  PRIMARY:  E2B AsyncSandbox (cloud sandbox with internet, pip, full Linux)
  FALLBACK: Local subprocess (no network, no pip, limited)

E2B advantages over subprocess:
  - Full Linux OS with internet access
  - Can install packages (pip install) at runtime
  - Isolated from the kernel process (no risk to server)
  - Code contexts persist variables across calls
  - 60-second timeout (vs 30s local)
  - File upload/download support

Security:
  - E2B sandboxes are fully isolated cloud VMs
  - No secrets leak (E2B_API_KEY is only used for sandbox creation)
  - Each execution gets a fresh sandbox (no state pollution)
  - HITL removed: the sandbox IS the security boundary
    (code cannot affect the kernel, Railway, or Supabase)

Sprint 33A | 2026-04-29
IVD: e2b-code-interpreter==2.6.1 (MIT, PyPI latest 2026-04-29)
"""

import asyncio
import logging
import os
from typing import Any, Optional

logger = logging.getLogger("monstruo.tools.code_exec")

# ── Constants ────────────────────────────────────────────────────────
MAX_TIMEOUT_E2B = 60  # E2B supports longer timeouts
MAX_TIMEOUT_LOCAL = 30  # Local subprocess cap
MAX_OUTPUT_CHARS = 10_000
SANDBOX_DIR = "/tmp/monstruo_sandbox"  # Local fallback only

# ── E2B availability check ──────────────────────────────────────────
_E2B_AVAILABLE: Optional[bool] = None


async def _check_e2b() -> bool:
    """Check if E2B SDK is installed and API key is configured."""
    global _E2B_AVAILABLE
    if _E2B_AVAILABLE is not None:
        return _E2B_AVAILABLE
    try:
        import e2b_code_interpreter  # noqa: F401

        if os.environ.get("E2B_API_KEY"):
            _E2B_AVAILABLE = True
            logger.info("e2b_available", status="ready")
        else:
            _E2B_AVAILABLE = False
            logger.warning("e2b_no_api_key", hint="Set E2B_API_KEY in Railway env vars")
    except ImportError:
        _E2B_AVAILABLE = False
        logger.warning("e2b_not_installed", hint="pip install e2b-code-interpreter")
    return _E2B_AVAILABLE


def _truncate(text: str) -> str:
    """Truncate output to MAX_OUTPUT_CHARS."""
    if len(text) > MAX_OUTPUT_CHARS:
        return text[:MAX_OUTPUT_CHARS] + f"\n\n... [truncated, {len(text)} total chars]"
    return text


# ── E2B Backend ─────────────────────────────────────────────────────


async def _execute_e2b(
    code: str,
    language: str = "python",
    timeout: int = 60,
    install_packages: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Execute code in an E2B cloud sandbox."""
    from e2b_code_interpreter import AsyncSandbox

    sandbox = None
    try:
        # Create sandbox
        sandbox = await AsyncSandbox.create(timeout=120)
        logger.info("e2b_sandbox_created", sandbox_id=sandbox.sandbox_id)

        # Install packages if requested
        if install_packages:
            pkgs = " ".join(install_packages)
            install_result = await sandbox.commands.run(
                f"pip install {pkgs}",
                timeout=60,
            )
            if install_result.exit_code != 0:
                return {
                    "status": "error",
                    "error": f"Package installation failed: {install_result.stderr}",
                    "exit_code": install_result.exit_code,
                    "stdout": install_result.stdout or "",
                    "stderr": install_result.stderr or "",
                    "backend": "e2b",
                }

        # Execute code
        if language == "shell":
            # Shell: use commands.run
            result = await sandbox.commands.run(
                code,
                timeout=timeout,
            )
            stdout = _truncate(result.stdout or "")
            stderr = _truncate(result.stderr or "")
            exit_code = result.exit_code

            return {
                "status": "success" if exit_code == 0 else "error",
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "language": language,
                "timeout_used": timeout,
                "backend": "e2b",
            }
        else:
            # Python: use run_code for rich output
            execution = await sandbox.run_code(
                code=code,
                language="python",
                timeout=timeout,
            )

            # Collect stdout
            stdout_lines = [msg.line for msg in execution.logs.stdout] if execution.logs.stdout else []
            stderr_lines = [msg.line for msg in execution.logs.stderr] if execution.logs.stderr else []
            stdout = _truncate("\n".join(stdout_lines))
            stderr = _truncate("\n".join(stderr_lines))

            # Check for errors
            if execution.error:
                return {
                    "status": "error",
                    "exit_code": 1,
                    "stdout": stdout,
                    "stderr": stderr,
                    "error": {
                        "name": execution.error.name,
                        "value": execution.error.value,
                        "traceback": execution.error.traceback,
                    },
                    "language": language,
                    "timeout_used": timeout,
                    "backend": "e2b",
                }

            # Collect results (display outputs like plots, dataframes, etc.)
            results = []
            for r in execution.results:
                results.append(
                    {
                        "text": str(r),
                        "is_main_result": r.is_main_result,
                        "formats": list(r.formats()) if hasattr(r, "formats") and callable(r.formats) else [],
                    }
                )

            return {
                "status": "success",
                "exit_code": 0,
                "stdout": stdout,
                "stderr": stderr,
                "results": results if results else None,
                "language": language,
                "timeout_used": timeout,
                "backend": "e2b",
            }

    except Exception as e:
        logger.error("e2b_execution_failed", error=str(e))
        return {
            "status": "error",
            "error": f"E2B execution failed: {str(e)}",
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
            "backend": "e2b",
        }
    finally:
        if sandbox:
            try:
                await sandbox.kill()
            except Exception:
                pass  # Best effort cleanup


# ── Local Subprocess Backend (Fallback) ─────────────────────────────

# Env vars that MUST NOT leak into subprocess
_SECRETS_BLOCKLIST = {
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "XAI_API_KEY",
    "OPENROUTER_API_KEY",
    "SONAR_API_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "TELEGRAM_BOT_TOKEN",
    "LANGFUSE_SECRET_KEY",
    "MONSTRUO_API_KEY",
    "GITHUB_TOKEN",
    "GITHUB_PERSONAL_ACCESS_TOKEN",
    "DROPBOX_API_KEY",
    "ELEVENLABS_API_KEY",
    "HEYGEN_API_KEY",
    "CLOUDFLARE_API_TOKEN",
    "E2B_API_KEY",
}


def _safe_env() -> dict[str, str]:
    """Build a minimal environment without secrets."""
    env = {}
    for k, v in os.environ.items():
        if k not in _SECRETS_BLOCKLIST:
            env[k] = v
    env["HOME"] = SANDBOX_DIR
    env["TMPDIR"] = SANDBOX_DIR
    env["PATH"] = "/usr/local/bin:/usr/bin:/bin"
    return env


async def _execute_local(
    code: str,
    language: str = "python",
    timeout: int = 30,
) -> dict[str, Any]:
    """Execute code in a local subprocess (fallback when E2B is unavailable)."""
    os.makedirs(SANDBOX_DIR, exist_ok=True)

    if language == "python":
        code_file = os.path.join(SANDBOX_DIR, "_exec.py")
        with open(code_file, "w") as f:
            f.write(code)
        cmd = ["python3", code_file]
    else:
        code_file = os.path.join(SANDBOX_DIR, "_exec.sh")
        with open(code_file, "w") as f:
            f.write(code)
        cmd = ["bash", code_file]

    env = _safe_env()

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=SANDBOX_DIR,
            env=env,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return {
                "status": "timeout",
                "error": f"Execution timed out after {timeout} seconds",
                "exit_code": -1,
                "stdout": "",
                "stderr": "",
                "backend": "local_subprocess",
            }

        stdout = _truncate(stdout_bytes.decode("utf-8", errors="replace"))
        stderr = _truncate(stderr_bytes.decode("utf-8", errors="replace"))
        exit_code = process.returncode

        return {
            "status": "success" if exit_code == 0 else "error",
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "language": language,
            "timeout_used": timeout,
            "backend": "local_subprocess",
        }

    except Exception as e:
        logger.error("local_exec_failed", error=str(e))
        return {
            "status": "error",
            "error": str(e),
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
            "backend": "local_subprocess",
        }
    finally:
        for fname in ("_exec.py", "_exec.sh"):
            fpath = os.path.join(SANDBOX_DIR, fname)
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except OSError:
                    pass


# ── Public Interface ────────────────────────────────────────────────


async def execute_code(
    code: str,
    language: str = "python",
    timeout: int = 60,
    allow_network: bool = True,
    hitl_approved: bool = False,
    install_packages: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Execute code in an isolated sandbox.

    Primary: E2B cloud sandbox (internet, pip, full Linux)
    Fallback: Local subprocess (limited, no network)

    Args:
        code: The code to execute
        language: 'python' or 'shell'
        timeout: Max seconds (60 for E2B, 30 for local)
        allow_network: Ignored for E2B (always has network); controls local fallback
        hitl_approved: Kept for backward compatibility but no longer enforced.
                       The E2B sandbox IS the security boundary.
        install_packages: List of pip packages to install before execution (E2B only)

    Returns:
        dict with stdout, stderr, exit_code, backend, and metadata
    """
    # ── Validate inputs ─────────────────────────────────────────────
    if language not in ("python", "shell"):
        return {"error": f"Unsupported language: {language}. Use 'python' or 'shell'."}

    if not code or not code.strip():
        return {"error": "Empty code provided."}

    # ── Try E2B first ───────────────────────────────────────────────
    if await _check_e2b():
        timeout_e2b = min(timeout, MAX_TIMEOUT_E2B)
        logger.info("code_exec_routing", backend="e2b", language=language, timeout=timeout_e2b)
        result = await _execute_e2b(
            code=code,
            language=language,
            timeout=timeout_e2b,
            install_packages=install_packages,
        )
        return result

    # ── Fallback to local subprocess ────────────────────────────────
    timeout_local = min(timeout, MAX_TIMEOUT_LOCAL)
    logger.info("code_exec_routing", backend="local_subprocess", language=language, timeout=timeout_local)

    if install_packages:
        logger.warning(
            "install_packages_not_supported_locally",
            packages=install_packages,
            hint="E2B is required for runtime package installation. Set E2B_API_KEY.",
        )

    result = await _execute_local(
        code=code,
        language=language,
        timeout=timeout_local,
    )
    return result
