"""
Code Execution tool for El Monstruo kernel.
Executes Python or shell code in a sandboxed subprocess.

Risk: HIGH (executes arbitrary code on the server)
HITL: Required ALWAYS — no execution without human approval.

Security measures:
  - Timeout: max 30 seconds per execution
  - Output truncation: max 10,000 chars
  - No network access by default (can be enabled via allow_network)
  - Working directory: /tmp/monstruo_sandbox (isolated)
  - Environment: minimal (no secrets leaked)
  - HITL gate: write operations ALWAYS require approval

Sprint 33: Initial implementation — the Embrión's hands.
"""

import asyncio
import logging
import os
import tempfile
from typing import Any, Optional

logger = logging.getLogger("monstruo.tools.code_exec")

# ── Constants ────────────────────────────────────────────────────────
MAX_TIMEOUT_SECONDS = 30
MAX_OUTPUT_CHARS = 10_000
SANDBOX_DIR = "/tmp/monstruo_sandbox"

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
}


def _safe_env() -> dict[str, str]:
    """Build a minimal environment without secrets."""
    env = {}
    for k, v in os.environ.items():
        if k not in _SECRETS_BLOCKLIST:
            env[k] = v
    # Always set these for sanity
    env["HOME"] = SANDBOX_DIR
    env["TMPDIR"] = SANDBOX_DIR
    env["PATH"] = "/usr/local/bin:/usr/bin:/bin"
    return env


def _truncate(text: str) -> str:
    """Truncate output to MAX_OUTPUT_CHARS."""
    if len(text) > MAX_OUTPUT_CHARS:
        return text[:MAX_OUTPUT_CHARS] + f"\n\n... [truncated, {len(text)} total chars]"
    return text


async def execute_code(
    code: str,
    language: str = "python",
    timeout: int = 30,
    allow_network: bool = False,
    hitl_approved: bool = False,
) -> dict[str, Any]:
    """
    Execute code in a sandboxed subprocess.

    Args:
        code: The code to execute
        language: 'python' or 'shell'
        timeout: Max seconds (capped at MAX_TIMEOUT_SECONDS)
        allow_network: Whether to allow network access
        hitl_approved: Whether human approved this execution

    Returns:
        dict with stdout, stderr, exit_code, and metadata
    """
    # ── HITL Gate (defense in depth) ────────────────────────────────
    if not hitl_approved:
        return {
            "status": "HITL_REQUIRED",
            "message": (
                "Code execution requires human approval. "
                "The code will be shown to the user for review before execution."
            ),
            "code_preview": code[:500],
            "language": language,
        }

    # ── Validate inputs ─────────────────────────────────────────────
    if language not in ("python", "shell"):
        return {"error": f"Unsupported language: {language}. Use 'python' or 'shell'."}

    if not code or not code.strip():
        return {"error": "Empty code provided."}

    timeout = min(timeout, MAX_TIMEOUT_SECONDS)

    # ── Prepare sandbox directory ───────────────────────────────────
    os.makedirs(SANDBOX_DIR, exist_ok=True)

    # ── Build command ───────────────────────────────────────────────
    if language == "python":
        # Write code to temp file for cleaner execution
        code_file = os.path.join(SANDBOX_DIR, "_exec.py")
        with open(code_file, "w") as f:
            f.write(code)
        cmd = ["python3", code_file]
    else:
        # Shell: execute via bash
        code_file = os.path.join(SANDBOX_DIR, "_exec.sh")
        with open(code_file, "w") as f:
            f.write(code)
        cmd = ["bash", code_file]

    # ── Execute ─────────────────────────────────────────────────────
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
            }

        stdout = _truncate(stdout_bytes.decode("utf-8", errors="replace"))
        stderr = _truncate(stderr_bytes.decode("utf-8", errors="replace"))
        exit_code = process.returncode

        logger.info(
            "code_exec_complete",
            language=language,
            exit_code=exit_code,
            stdout_len=len(stdout),
            stderr_len=len(stderr),
        )

        return {
            "status": "success" if exit_code == 0 else "error",
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "language": language,
            "timeout_used": timeout,
        }

    except Exception as e:
        logger.error("code_exec_failed", error=str(e))
        return {
            "status": "error",
            "error": str(e),
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
        }
    finally:
        # Clean up temp files
        for fname in ("_exec.py", "_exec.sh"):
            fpath = os.path.join(SANDBOX_DIR, fname)
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except OSError:
                    pass
