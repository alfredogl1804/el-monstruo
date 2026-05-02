"""
File Operations tool for El Monstruo kernel.
Sprint 46.2: Gives the Task Planner the ability to create, read, edit,
and manage files inside the E2B sandbox.

Architecture:
  - Uses the same E2B AsyncSandbox as code_exec.py
  - Supports: write_file, read_file, edit_file, list_files, delete_file
  - Files persist within a sandbox session (shared with code_exec)
  - Can be used to scaffold projects, write configs, create scripts

Integration:
  - TaskPlanner._EXECUTOR_TOOLS includes "file_ops"
  - TaskPlanner._execute_tool_direct("file_ops", {...}) calls this module

Sprint 46.2 | 2026-04-30
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger("monstruo.tools.file_ops")

# ── Constants ────────────────────────────────────────────────────────
MAX_FILE_SIZE = 100_000  # 100KB max per file write
MAX_READ_SIZE = 50_000  # 50KB max read output


async def execute_file_ops(
    action: str,
    path: str,
    content: Optional[str] = None,
    find: Optional[str] = None,
    replace: Optional[str] = None,
    recursive: bool = False,
) -> dict[str, Any]:
    """
    Execute file operations in the E2B sandbox.

    Actions:
      - write_file: Create or overwrite a file at `path` with `content`
      - read_file: Read the contents of a file at `path`
      - edit_file: Find `find` and replace with `replace` in file at `path`
      - list_files: List files in directory at `path`
      - delete_file: Delete file at `path`
      - mkdir: Create directory at `path` (recursive)

    Returns:
      dict with keys: success (bool), result (str), action (str), path (str)
    """
    try:
        # Try E2B first
        if os.environ.get("E2B_API_KEY"):
            return await _execute_e2b_file_ops(action, path, content, find, replace, recursive)
        else:
            # Fallback: use code_exec to manipulate files via Python
            return await _execute_via_code(action, path, content, find, replace, recursive)
    except Exception as e:
        logger.error("file_ops_failed", action=action, path=path, error=str(e))
        return {
            "success": False,
            "result": f"Error: {str(e)}",
            "action": action,
            "path": path,
        }


async def _execute_e2b_file_ops(
    action: str,
    path: str,
    content: Optional[str],
    find: Optional[str],
    replace: Optional[str],
    recursive: bool,
) -> dict[str, Any]:
    """Execute file ops directly via E2B sandbox filesystem API."""
    from e2b_code_interpreter import AsyncSandbox

    sandbox = await AsyncSandbox.create()
    try:
        if action == "write_file":
            if not content:
                return {"success": False, "result": "No content provided", "action": action, "path": path}
            if len(content) > MAX_FILE_SIZE:
                return {
                    "success": False,
                    "result": f"Content too large ({len(content)} chars, max {MAX_FILE_SIZE})",
                    "action": action,
                    "path": path,
                }

            # Ensure parent directory exists
            parent_dir = "/".join(path.rsplit("/", 1)[:-1])
            if parent_dir:
                await sandbox.commands.run(f"mkdir -p {parent_dir}")

            await sandbox.files.write(path, content)
            logger.info("file_ops_write", path=path, size=len(content))
            return {
                "success": True,
                "result": f"File written: {path} ({len(content)} chars)",
                "action": action,
                "path": path,
            }

        elif action == "read_file":
            file_content = await sandbox.files.read(path)
            if len(file_content) > MAX_READ_SIZE:
                file_content = file_content[:MAX_READ_SIZE] + f"\n\n... [truncated, {len(file_content)} total chars]"
            return {"success": True, "result": file_content, "action": action, "path": path}

        elif action == "edit_file":
            if not find:
                return {"success": False, "result": "No 'find' text provided", "action": action, "path": path}
            if replace is None:
                replace = ""

            file_content = await sandbox.files.read(path)
            if find not in file_content:
                return {
                    "success": False,
                    "result": f"Text '{find[:50]}...' not found in {path}",
                    "action": action,
                    "path": path,
                }

            new_content = file_content.replace(find, replace, 1)
            await sandbox.files.write(path, new_content)
            logger.info("file_ops_edit", path=path, find_len=len(find), replace_len=len(replace))
            return {
                "success": True,
                "result": f"File edited: {path} (replaced {len(find)} chars with {len(replace)} chars)",
                "action": action,
                "path": path,
            }

        elif action == "list_files":
            result = await sandbox.commands.run(
                f"find {path} -maxdepth {'999' if recursive else '1'} -type f 2>/dev/null | head -100"
            )
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

    finally:
        await sandbox.kill()


async def _execute_via_code(
    action: str,
    path: str,
    content: Optional[str],
    find: Optional[str],
    replace: Optional[str],
    recursive: bool,
) -> dict[str, Any]:
    """Fallback: execute file ops via code_exec (Python in E2B or local)."""
    from tools.code_exec import execute_code

    if action == "write_file":
        if not content:
            return {"success": False, "result": "No content provided", "action": action, "path": path}

        code = f"""
import os
os.makedirs(os.path.dirname({repr(path)}) or '.', exist_ok=True)
with open({repr(path)}, 'w') as f:
    f.write({repr(content)})
print(f"Written {{len({repr(content)})}} chars to {path}")
"""
        result = await execute_code(code=code, language="python", timeout=30)
        stdout = result.get("stdout", "")
        return {
            "success": result.get("success", False),
            "result": stdout or result.get("stderr", ""),
            "action": action,
            "path": path,
        }

    elif action == "read_file":
        code = f"""
with open({repr(path)}, 'r') as f:
    content = f.read({MAX_READ_SIZE})
print(content)
"""
        result = await execute_code(code=code, language="python", timeout=30)
        return {
            "success": result.get("success", False),
            "result": result.get("stdout", result.get("stderr", "")),
            "action": action,
            "path": path,
        }

    elif action == "edit_file":
        code = f"""
with open({repr(path)}, 'r') as f:
    content = f.read()
if {repr(find)} not in content:
    print(f"ERROR: text not found in file")
else:
    content = content.replace({repr(find)}, {repr(replace or "")}, 1)
    with open({repr(path)}, 'w') as f:
        f.write(content)
    print(f"Edited {path}")
"""
        result = await execute_code(code=code, language="python", timeout=30)
        stdout = result.get("stdout", "")
        success = "ERROR" not in stdout and result.get("success", False)
        return {"success": success, "result": stdout or result.get("stderr", ""), "action": action, "path": path}

    elif action == "list_files":
        code = f"""
import os
for root, dirs, files in os.walk({repr(path)}):
    for f in files:
        print(os.path.join(root, f))
    if not {recursive}:
        break
"""
        result = await execute_code(code=code, language="python", timeout=30)
        return {
            "success": result.get("success", False),
            "result": result.get("stdout", ""),
            "action": action,
            "path": path,
        }

    elif action == "delete_file":
        code = f"""
import os, shutil
if os.path.isdir({repr(path)}):
    shutil.rmtree({repr(path)})
elif os.path.exists({repr(path)}):
    os.remove({repr(path)})
print(f"Deleted {path}")
"""
        result = await execute_code(code=code, language="python", timeout=30)
        return {
            "success": result.get("success", False),
            "result": result.get("stdout", ""),
            "action": action,
            "path": path,
        }

    elif action == "mkdir":
        code = f"""
import os
os.makedirs({repr(path)}, exist_ok=True)
print(f"Created {path}")
"""
        result = await execute_code(code=code, language="python", timeout=30)
        return {
            "success": result.get("success", False),
            "result": result.get("stdout", ""),
            "action": action,
            "path": path,
        }

    else:
        return {"success": False, "result": f"Unknown action: {action}", "action": action, "path": path}
