"""
Sandbox Manager for El Monstruo kernel.
Sprint 48: Persistent E2B sandbox sessions for multi-step task execution.

Problem solved:
  Previously, each tool call (file_ops, web_dev, code_exec) created and
  destroyed its own E2B sandbox. This meant multi-step plans could NOT
  share state — scaffold() created files in sandbox A, build() ran in
  sandbox B (which was empty), and deploy() ran in sandbox C (also empty).

Solution:
  SandboxManager creates ONE sandbox per plan execution and shares it
  across all tool calls. Tools receive the sandbox_id and reconnect to
  the same sandbox using AsyncSandbox.connect(sandbox_id).

Architecture:
  - SandboxManager.acquire(plan_id) → creates or reconnects to sandbox
  - SandboxManager.get_sandbox(plan_id) → returns active sandbox instance
  - SandboxManager.release(plan_id) → kills sandbox when plan completes
  - Tools call get_or_create_sandbox(plan_id) to get a shared sandbox

Lifecycle:
  1. TaskPlanner.stream_plan_and_execute() calls acquire() at start
  2. Each tool call uses get_sandbox() to get the shared instance
  3. TaskPlanner calls release() when plan finishes (success or failure)
  4. Sandbox auto-kills after 10 minutes if not explicitly released

Sprint 48 | 2026-04-30
IVD: e2b-code-interpreter==2.6.1 (MIT, PyPI latest 2026-04-29)
"""

import asyncio
import os
import time
from typing import Any, Optional

try:
    import structlog

    logger = structlog.get_logger("monstruo.tools.sandbox_manager")
except ImportError:
    import logging

    logger = logging.getLogger("monstruo.tools.sandbox_manager")

# ── Constants ────────────────────────────────────────────────────────
SANDBOX_TIMEOUT_S = 600  # 10 minutes max per plan
SANDBOX_KEEPALIVE_S = 300  # Extend timeout if still active
MAX_CONCURRENT_SANDBOXES = 3  # Safety limit


class SandboxSession:
    """Represents an active sandbox session tied to a plan."""

    def __init__(self, sandbox_id: str, plan_id: str):
        self.sandbox_id = sandbox_id
        self.plan_id = plan_id
        self.created_at = time.time()
        self.last_used_at = time.time()
        self.tool_calls = 0

    @property
    def age_s(self) -> float:
        return time.time() - self.created_at

    def touch(self):
        """Mark as recently used."""
        self.last_used_at = time.time()
        self.tool_calls += 1


# ── Global state ─────────────────────────────────────────────────────
_active_sessions: dict[str, SandboxSession] = {}
_lock = asyncio.Lock()


async def acquire(plan_id: str) -> str:
    """
    Create a new E2B sandbox for this plan and return its sandbox_id.
    If a sandbox already exists for this plan_id, reconnect to it.
    """
    async with _lock:
        # Check if we already have a session for this plan
        if plan_id in _active_sessions:
            session = _active_sessions[plan_id]
            logger.info(
                "sandbox_reuse",
                plan_id=plan_id,
                sandbox_id=session.sandbox_id,
                age_s=round(session.age_s),
            )
            # Extend timeout
            try:
                from e2b_code_interpreter import AsyncSandbox

                sandbox = await AsyncSandbox.connect(session.sandbox_id)
                await sandbox.set_timeout(SANDBOX_KEEPALIVE_S)
                session.touch()
                return session.sandbox_id
            except Exception as e:
                logger.warning(
                    "sandbox_reconnect_failed",
                    plan_id=plan_id,
                    sandbox_id=session.sandbox_id,
                    error=str(e),
                )
                # Remove dead session, create new one below
                del _active_sessions[plan_id]

        # Safety: don't exceed max concurrent sandboxes
        if len(_active_sessions) >= MAX_CONCURRENT_SANDBOXES:
            # Kill oldest session
            oldest_key = min(_active_sessions, key=lambda k: _active_sessions[k].last_used_at)
            await _force_kill(oldest_key)

        # Create new sandbox
        from e2b_code_interpreter import AsyncSandbox

        sandbox = await AsyncSandbox.create(timeout=SANDBOX_TIMEOUT_S)
        sandbox_id = sandbox.sandbox_id

        # Install Node.js for web dev tasks
        try:
            await sandbox.commands.run(
                "which node || (curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y nodejs)",
                timeout=60,
            )
        except Exception as e:
            logger.warning("sandbox_node_install_failed", error=str(e))

        session = SandboxSession(sandbox_id=sandbox_id, plan_id=plan_id)
        _active_sessions[plan_id] = session

        logger.info(
            "sandbox_created",
            plan_id=plan_id,
            sandbox_id=sandbox_id,
            timeout_s=SANDBOX_TIMEOUT_S,
        )
        return sandbox_id


async def get_sandbox(plan_id: str) -> Optional[Any]:
    """
    Get the active sandbox instance for a plan.
    Returns None if no sandbox exists for this plan.
    """
    async with _lock:
        session = _active_sessions.get(plan_id)
        if not session:
            return None

    # Reconnect outside the lock to avoid blocking
    try:
        from e2b_code_interpreter import AsyncSandbox

        sandbox = await AsyncSandbox.connect(session.sandbox_id)
        session.touch()
        return sandbox
    except Exception as e:
        logger.error(
            "sandbox_get_failed",
            plan_id=plan_id,
            sandbox_id=session.sandbox_id,
            error=str(e),
        )
        # Remove dead session
        async with _lock:
            _active_sessions.pop(plan_id, None)
        return None


async def get_or_create(plan_id: str) -> Any:
    """
    Get existing sandbox or create a new one for this plan.
    Returns the sandbox instance (not just the ID).
    """
    sandbox = await get_sandbox(plan_id)
    if sandbox:
        return sandbox

    # Create new
    sandbox_id = await acquire(plan_id)
    from e2b_code_interpreter import AsyncSandbox

    return await AsyncSandbox.connect(sandbox_id)


async def release(plan_id: str) -> bool:
    """
    Kill the sandbox for this plan and clean up.
    Returns True if sandbox was killed, False if not found.
    """
    async with _lock:
        session = _active_sessions.pop(plan_id, None)

    if not session:
        return False

    try:
        from e2b_code_interpreter import AsyncSandbox

        sandbox = await AsyncSandbox.connect(session.sandbox_id)
        await sandbox.kill()
        logger.info(
            "sandbox_released",
            plan_id=plan_id,
            sandbox_id=session.sandbox_id,
            age_s=round(session.age_s),
            tool_calls=session.tool_calls,
        )
        return True
    except Exception as e:
        logger.warning(
            "sandbox_release_failed",
            plan_id=plan_id,
            sandbox_id=session.sandbox_id,
            error=str(e),
        )
        return False


async def _force_kill(plan_id: str):
    """Force kill a sandbox session (used for cleanup)."""
    session = _active_sessions.pop(plan_id, None)
    if session:
        try:
            from e2b_code_interpreter import AsyncSandbox

            sandbox = await AsyncSandbox.connect(session.sandbox_id)
            await sandbox.kill()
        except Exception:
            pass
        logger.info("sandbox_force_killed", plan_id=plan_id, sandbox_id=session.sandbox_id)


async def get_status() -> dict[str, Any]:
    """Get status of all active sandbox sessions."""
    return {
        "active_sessions": len(_active_sessions),
        "sessions": [
            {
                "plan_id": s.plan_id,
                "sandbox_id": s.sandbox_id,
                "age_s": round(s.age_s),
                "tool_calls": s.tool_calls,
            }
            for s in _active_sessions.values()
        ],
    }


# ── Convenience: execute code in plan's sandbox ─────────────────────


async def execute_in_sandbox(
    plan_id: str,
    code: str,
    language: str = "python",
    timeout: int = 60,
    install_packages: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Execute code in the plan's persistent sandbox.
    This is the replacement for code_exec.execute_code() when called
    from the Task Planner context.
    """
    sandbox = await get_or_create(plan_id)

    try:
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
                    "backend": "e2b_persistent",
                }

        # Execute code
        if language == "shell":
            result = await sandbox.commands.run(code, timeout=timeout)
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            exit_code = result.exit_code

            return {
                "status": "success" if exit_code == 0 else "error",
                "exit_code": exit_code,
                "stdout": stdout[:10000],
                "stderr": stderr[:10000],
                "language": language,
                "backend": "e2b_persistent",
            }
        else:
            # Python: use run_code for rich output
            execution = await sandbox.run_code(
                code=code,
                language="python",
                timeout=timeout,
            )

            # Handle both SDK versions: 2.4.x returns strings, 2.6.x returns objects with .line
            raw_stdout = execution.logs.stdout if execution.logs.stdout else []
            raw_stderr = execution.logs.stderr if execution.logs.stderr else []
            stdout_lines = []
            for msg in raw_stdout:
                if isinstance(msg, str):
                    stdout_lines.append(msg)
                elif hasattr(msg, "line"):
                    stdout_lines.append(msg.line)
                else:
                    stdout_lines.append(str(msg))
            stderr_lines = []
            for msg in raw_stderr:
                if isinstance(msg, str):
                    stderr_lines.append(msg)
                elif hasattr(msg, "line"):
                    stderr_lines.append(msg.line)
                else:
                    stderr_lines.append(str(msg))
            stdout = "\n".join(stdout_lines)
            stderr = "\n".join(stderr_lines)

            if execution.error:
                return {
                    "status": "error",
                    "exit_code": 1,
                    "stdout": stdout[:10000],
                    "stderr": stderr[:10000],
                    "error": {
                        "name": execution.error.name,
                        "value": execution.error.value,
                        "traceback": execution.error.traceback,
                    },
                    "backend": "e2b_persistent",
                }

            results = []
            for r in execution.results:
                results.append(
                    {
                        "text": str(r),
                        "is_main_result": r.is_main_result,
                    }
                )

            return {
                "status": "success",
                "exit_code": 0,
                "stdout": stdout[:10000],
                "stderr": stderr[:10000],
                "results": results if results else None,
                "backend": "e2b_persistent",
            }

    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "error": f"Execution timed out after {timeout}s",
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
            "backend": "e2b_persistent",
        }
    except Exception as e:
        logger.error("sandbox_exec_failed", plan_id=plan_id, error=str(e))
        return {
            "status": "error",
            "error": str(e),
            "exit_code": -1,
            "stdout": "",
            "stderr": "",
            "backend": "e2b_persistent",
        }


async def file_op_in_sandbox(
    plan_id: str,
    action: str,
    path: str,
    content: Optional[str] = None,
    find: Optional[str] = None,
    replace: Optional[str] = None,
    recursive: bool = False,
) -> dict[str, Any]:
    """
    Execute file operations in the plan's persistent sandbox.
    This is the replacement for file_ops.execute_file_ops() when called
    from the Task Planner context.
    """
    sandbox = await get_or_create(plan_id)

    try:
        if action == "write_file":
            if not content:
                return {"success": False, "result": "No content provided", "action": action, "path": path}
            if len(content) > 100_000:
                return {
                    "success": False,
                    "result": f"Content too large ({len(content)} chars)",
                    "action": action,
                    "path": path,
                }

            # Ensure parent directory exists
            parent_dir = "/".join(path.rsplit("/", 1)[:-1])
            if parent_dir:
                await sandbox.commands.run(f"mkdir -p {parent_dir}")

            await sandbox.files.write(path, content)
            return {
                "success": True,
                "result": f"File written: {path} ({len(content)} chars)",
                "action": action,
                "path": path,
            }

        elif action == "read_file":
            file_content = await sandbox.files.read(path)
            if len(file_content) > 50_000:
                file_content = file_content[:50_000] + "\n... [truncated]"
            return {"success": True, "result": file_content, "action": action, "path": path}

        elif action == "edit_file":
            if not find:
                return {"success": False, "result": "No 'find' text provided", "action": action, "path": path}
            if replace is None:
                replace = ""

            file_content = await sandbox.files.read(path)
            if find not in file_content:
                return {"success": False, "result": f"Text not found in {path}", "action": action, "path": path}

            new_content = file_content.replace(find, replace, 1)
            await sandbox.files.write(path, new_content)
            return {"success": True, "result": f"File edited: {path}", "action": action, "path": path}

        elif action == "list_files":
            depth = "999" if recursive else "1"
            result = await sandbox.commands.run(f"find {path} -maxdepth {depth} -type f 2>/dev/null | head -100")
            files = result.stdout.strip() if result.stdout else "No files found"
            return {"success": True, "result": files, "action": action, "path": path}

        elif action == "delete_file":
            await sandbox.commands.run(f"rm -rf {path}")
            return {"success": True, "result": f"Deleted: {path}", "action": action, "path": path}

        elif action == "mkdir":
            await sandbox.commands.run(f"mkdir -p {path}")
            return {"success": True, "result": f"Directory created: {path}", "action": action, "path": path}

        else:
            return {"success": False, "result": f"Unknown action: {action}", "action": action, "path": path}

    except Exception as e:
        logger.error("sandbox_file_op_failed", plan_id=plan_id, action=action, path=path, error=str(e))
        return {"success": False, "result": f"Error: {str(e)}", "action": action, "path": path}


async def web_dev_in_sandbox(
    plan_id: str,
    action: str,
    project_name: Optional[str] = None,
) -> dict[str, Any]:
    """
    Execute web dev operations in the plan's persistent sandbox.
    This replaces web_dev.execute_web_dev() for Task Planner context.
    """
    import json as _json

    sandbox = await get_or_create(plan_id)
    project_root = "/home/user/project"

    try:
        if action == "scaffold":
            # Import template from web_dev module
            from tools.web_dev import VITE_REACT_TEMPLATE

            # Create all template files in the persistent sandbox
            for filepath, content in VITE_REACT_TEMPLATE.items():
                full_path = f"{project_root}/{filepath}"
                parent = "/".join(full_path.rsplit("/", 1)[:-1])
                if parent:
                    await sandbox.commands.run(f"mkdir -p {parent}")
                await sandbox.files.write(full_path, content)

            # Update project name in package.json if provided
            if project_name:
                pkg_content = await sandbox.files.read(f"{project_root}/package.json")
                pkg_content = pkg_content.replace("monstruo-web-project", project_name)
                await sandbox.files.write(f"{project_root}/package.json", pkg_content)

            # Verify
            result = await sandbox.commands.run(f"ls -la {project_root}/")
            logger.info("web_dev_scaffold_done", project_name=project_name, files=result.stdout)

            return {
                "success": True,
                "result": f"Project '{project_name}' scaffolded at {project_root}\nFiles: {result.stdout}",
                "action": "scaffold",
                "url": None,
            }

        elif action == "build":
            # Install deps and build in the SAME sandbox
            install_result = await sandbox.commands.run(
                f"cd {project_root} && npm install",
                timeout=120,
            )
            if install_result.exit_code != 0:
                return {
                    "success": False,
                    "result": f"npm install failed: {install_result.stderr}",
                    "action": "build",
                    "url": None,
                }

            build_result = await sandbox.commands.run(
                f"cd {project_root} && npm run build",
                timeout=60,
            )
            if build_result.exit_code != 0:
                return {
                    "success": False,
                    "result": f"Build failed: {build_result.stderr}",
                    "action": "build",
                    "url": None,
                }

            # List dist files
            dist_result = await sandbox.commands.run(f"find {project_root}/dist -type f | head -20")

            return {
                "success": True,
                "result": f"Build successful!\n{dist_result.stdout}",
                "action": "build",
                "url": None,
            }

        elif action == "deploy":
            token = os.environ.get("VERCEL_TOKEN", "")
            if not token:
                return {
                    "success": False,
                    "result": "No VERCEL_TOKEN configured",
                    "action": "deploy",
                    "url": None,
                }

            # Collect dist files from the persistent sandbox
            collect_code = f"""
import os, json, base64
dist_dir = "{project_root}/dist"
if not os.path.isdir(dist_dir):
    print(json.dumps({{"error": "No dist/ directory. Run build first."}}))
else:
    files = []
    for root, dirs, filenames in os.walk(dist_dir):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, dist_dir)
            with open(filepath, 'rb') as f:
                content = f.read()
            files.append({{
                "file": rel_path,
                "data": base64.b64encode(content).decode(),
                "encoding": "base64"
            }})
    print(json.dumps({{"files": files, "count": len(files)}}))
"""
            execution = await sandbox.run_code(code=collect_code, language="python", timeout=30)
            raw_stdout = execution.logs.stdout if execution.logs.stdout else []
            stdout_lines = []
            for msg in raw_stdout:
                if isinstance(msg, str):
                    stdout_lines.append(msg)
                elif hasattr(msg, "line"):
                    stdout_lines.append(msg.line)
                else:
                    stdout_lines.append(str(msg))
            stdout = "\n".join(stdout_lines).strip()

            try:
                file_data = _json.loads(stdout)
            except (ValueError, _json.JSONDecodeError):
                return {
                    "success": False,
                    "result": f"Failed to collect build files: {stdout[:500]}",
                    "action": "deploy",
                    "url": None,
                }

            if "error" in file_data:
                return {
                    "success": False,
                    "result": file_data["error"],
                    "action": "deploy",
                    "url": None,
                }

            # Deploy via Vercel API (from kernel process, not sandbox)
            import httpx

            deployment_payload = {
                "name": project_name or "monstruo-project",
                "files": file_data["files"],
                "projectSettings": {
                    "framework": "vite",
                },
            }

            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.vercel.com/v13/deployments",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json=deployment_payload,
                )

                if resp.status_code in (200, 201):
                    data = resp.json()
                    url = data.get("url", "")
                    deployment_url = f"https://{url}" if url else "URL pending..."
                    logger.info("web_dev_deployed", project=project_name, url=deployment_url)
                    return {
                        "success": True,
                        "result": f"Deployed!\nURL: {deployment_url}\nFiles: {file_data['count']}",
                        "action": "deploy",
                        "url": deployment_url,
                    }
                else:
                    return {
                        "success": False,
                        "result": f"Vercel API error ({resp.status_code}): {resp.text[:500]}",
                        "action": "deploy",
                        "url": None,
                    }

        else:
            return {
                "success": False,
                "result": f"Unknown action: {action}",
                "action": action,
                "url": None,
            }

    except Exception as e:
        logger.error("sandbox_web_dev_failed", plan_id=plan_id, action=action, error=str(e))
        return {
            "success": False,
            "result": f"Error: {str(e)}",
            "action": action,
            "url": None,
        }
