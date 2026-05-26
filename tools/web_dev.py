"""
Web Dev tool for El Monstruo kernel.
Sprint 47.2: Gives the Task Planner the ability to scaffold, build,
and deploy web projects end-to-end.

Architecture:
  - Scaffolds projects inside E2B sandbox (Vite + React + Tailwind)
  - Deploys to Vercel via REST API (no git required)
  - Supports: scaffold, preview, deploy, add_page, install_package

Integration:
  - TaskPlanner._EXECUTOR_TOOLS includes "web_dev"
  - TaskPlanner._execute_tool_direct("web_dev", {...}) calls this module

Deployment flow:
  1. scaffold → creates project structure in E2B
  2. file_ops → writes custom code (pages, components, styles)
  3. code_exec → runs `npm run build` in E2B
  4. deploy → uploads build output to Vercel via /v13/deployments API

Sprint 47.2 | 2026-04-30
"""

import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger("monstruo.tools.web_dev")

# ── Constants ────────────────────────────────────────────────────────
VERCEL_API_BASE = "https://api.vercel.com"
DEFAULT_FRAMEWORK = "vite-react"  # Vite + React + Tailwind
PROJECT_ROOT = "/home/user/project"  # E2B sandbox path


# ── Templates ────────────────────────────────────────────────────────
VITE_REACT_TEMPLATE = {
    "package.json": json.dumps(
        {
            "name": "monstruo-web-project",
            "private": True,
            "version": "1.0.0",
            "type": "module",
            "scripts": {"dev": "vite", "build": "vite build", "preview": "vite preview"},
            "dependencies": {"react": "^19.0.0", "react-dom": "^19.0.0"},
            "devDependencies": {
                "@vitejs/plugin-react": "^4.3.0",
                "vite": "^6.0.0",
                "tailwindcss": "^4.0.0",
                "@tailwindcss/vite": "^4.0.0",
            },
        },
        indent=2,
    ),
    "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
""",
    "index.html": """<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Mi Proyecto</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""",
    "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
""",
    "src/App.jsx": """export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-white mb-4">
          Hola Mundo
        </h1>
        <p className="text-xl text-slate-300">
          Proyecto creado por El Monstruo
        </p>
      </div>
    </div>
  )
}
""",
    "src/index.css": """@import "tailwindcss";
""",
}


async def execute_web_dev(
    action: str,
    project_name: Optional[str] = None,
    framework: str = DEFAULT_FRAMEWORK,
    vercel_token: Optional[str] = None,
) -> dict[str, Any]:
    """
    Execute web development operations.

    Actions:
      - scaffold: Create a new project from template in E2B sandbox
      - build: Run npm install + npm run build in E2B
      - deploy: Deploy the built project to Vercel
      - get_preview_url: Get the local dev server URL (E2B)

    Returns:
      dict with keys: success (bool), result (str), action (str), url (str|None)
    """
    try:
        if action == "scaffold":
            return await _scaffold_project(project_name or "my-project", framework)
        elif action == "build":
            return await _build_project()
        elif action == "deploy":
            token = vercel_token or os.environ.get("VERCEL_TOKEN", "")
            if not token:
                return {
                    "success": False,
                    "result": "No VERCEL_TOKEN configured. Set it in environment variables.",
                    "action": action,
                    "url": None,
                }
            return await _deploy_to_vercel(project_name or "monstruo-project", token)
        else:
            return {
                "success": False,
                "result": f"Unknown action: {action}. Available: scaffold, build, deploy",
                "action": action,
                "url": None,
            }
    except Exception as e:
        logger.error("web_dev_failed", action=action, error=str(e))
        return {
            "success": False,
            "result": f"Error: {str(e)}",
            "action": action,
            "url": None,
        }


async def _scaffold_project(project_name: str, framework: str) -> dict[str, Any]:
    """Create project structure in E2B sandbox."""
    from tools.code_exec import execute_code

    # Create all template files
    template = VITE_REACT_TEMPLATE
    file_creation_code = f"""
import os
import json

PROJECT_ROOT = "{PROJECT_ROOT}"
os.makedirs(PROJECT_ROOT, exist_ok=True)
os.chdir(PROJECT_ROOT)

files = {json.dumps(template)}

for filepath, content in files.items():
    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Created: {{filepath}}")

print(f"\\nProject scaffolded at {{PROJECT_ROOT}}")
print(f"Files created: {{len(files)}}")
"""

    result = await execute_code(code=file_creation_code, language="python", timeout=30)
    stdout = result.get("stdout", "")

    if result.get("success"):
        return {
            "success": True,
            "result": f"Project '{project_name}' scaffolded with {framework} template.\n{stdout}",
            "action": "scaffold",
            "url": None,
        }
    else:
        return {
            "success": False,
            "result": f"Scaffold failed: {result.get('stderr', stdout)}",
            "action": "scaffold",
            "url": None,
        }


async def _build_project() -> dict[str, Any]:
    """Run npm install + npm run build in E2B sandbox."""
    from tools.code_exec import execute_code

    build_code = f"""
import subprocess
import os

os.chdir("{PROJECT_ROOT}")

# Install dependencies
print("Installing dependencies...")
result = subprocess.run(["npm", "install"], capture_output=True, text=True, timeout=120)
if result.returncode != 0:
    print(f"npm install failed: {{result.stderr}}")
    exit(1)
print("Dependencies installed.")

# Build
print("Building project...")
result = subprocess.run(["npm", "run", "build"], capture_output=True, text=True, timeout=60)
if result.returncode != 0:
    print(f"Build failed: {{result.stderr}}")
    exit(1)
print("Build successful!")

# List output files
import glob
dist_files = glob.glob("dist/**/*", recursive=True)
print(f"\\nBuild output ({{len(dist_files)}} files):")
for f in dist_files[:20]:
    if os.path.isfile(f):
        size = os.path.getsize(f)
        print(f"  {{f}} ({{size}} bytes)")
"""

    result = await execute_code(code=build_code, language="python", timeout=180)
    stdout = result.get("stdout", "")

    if result.get("success") and "Build successful" in stdout:
        return {
            "success": True,
            "result": stdout,
            "action": "build",
            "url": None,
        }
    else:
        return {
            "success": False,
            "result": f"Build failed: {result.get('stderr', stdout)}",
            "action": "build",
            "url": None,
        }


async def _deploy_to_vercel(project_name: str, token: str) -> dict[str, Any]:
    """Deploy built project to Vercel via REST API."""
    from tools.code_exec import execute_code

    # First, collect all files from dist/ in E2B
    collect_code = f"""
import os
import json
import base64

os.chdir("{PROJECT_ROOT}")
dist_dir = "dist"

if not os.path.isdir(dist_dir):
    print(json.dumps({{"error": "No dist/ directory. Run build first."}}))
    exit(0)

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

    collect_result = await execute_code(code=collect_code, language="python", timeout=30)
    stdout = collect_result.get("stdout", "").strip()

    try:
        file_data = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        return {
            "success": False,
            "result": f"Failed to collect build files: {stdout}",
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

    # Deploy via Vercel API
    import httpx

    deployment_payload = {
        "name": project_name,
        "files": file_data["files"],
        "projectSettings": {
            "framework": "vite",
        },
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{VERCEL_API_BASE}/v13/deployments",
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
            logger.info(
                "web_dev_deployed",
                project=project_name,
                url=deployment_url,
                status=resp.status_code,
            )
            return {
                "success": True,
                "result": f"Deployed successfully!\nURL: {deployment_url}\nFiles: {file_data['count']}",
                "action": "deploy",
                "url": deployment_url,
            }
        else:
            error_body = resp.text[:500]
            logger.error(
                "web_dev_deploy_failed",
                status=resp.status_code,
                body=error_body,
            )
            return {
                "success": False,
                "result": f"Vercel API error ({resp.status_code}): {error_body}",
                "action": "deploy",
                "url": None,
            }
