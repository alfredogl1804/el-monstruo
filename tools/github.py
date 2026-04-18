"""
GitHub integration tool for El Monstruo kernel.
Uses GitHub REST API v2022-11-28 (validated 2026-04-17).

Capabilities:
- Search repos, issues, code
- Create/read/update issues
- Read file contents
- Create commits (self_modify)
- List PRs

Risk: HIGH (can modify repos)
HITL: Required for write operations
"""

import os
import json
import logging
from typing import Any

import aiohttp

logger = logging.getLogger("monstruo.tools.github")

GITHUB_API = "https://api.github.com"
API_VERSION = "2022-11-28"  # validated 2026-04-17


def _headers() -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN not configured")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }


async def _request(method: str, path: str, body: dict | None = None) -> dict:
    """Make authenticated request to GitHub API."""
    url = f"{GITHUB_API}{path}"
    async with aiohttp.ClientSession() as session:
        kwargs = {"headers": _headers()}
        if body:
            kwargs["json"] = body
        async with session.request(method, url, **kwargs) as resp:
            text = await resp.text()
            if resp.status >= 400:
                logger.error(f"GitHub API {resp.status}: {text[:500]}")
                return {"error": f"GitHub API returned {resp.status}", "detail": text[:500]}
            if text:
                return json.loads(text)
            return {"status": "ok"}


# ── Read Operations ──────────────────────────────────────────────

async def search_repos(query: str, limit: int = 5) -> dict:
    """Search GitHub repositories."""
    data = await _request("GET", f"/search/repositories?q={query}&per_page={limit}")
    if "error" in data:
        return data
    items = data.get("items", [])
    return {
        "total": data.get("total_count", 0),
        "repos": [
            {
                "full_name": r["full_name"],
                "description": r.get("description", ""),
                "stars": r["stargazers_count"],
                "language": r.get("language", ""),
                "url": r["html_url"],
            }
            for r in items
        ],
    }


async def search_code(query: str, repo: str | None = None, limit: int = 10) -> dict:
    """Search code across repos or within a specific repo."""
    q = f"{query}+repo:{repo}" if repo else query
    data = await _request("GET", f"/search/code?q={q}&per_page={limit}")
    if "error" in data:
        return data
    items = data.get("items", [])
    return {
        "total": data.get("total_count", 0),
        "results": [
            {
                "name": r["name"],
                "path": r["path"],
                "repo": r["repository"]["full_name"],
                "url": r["html_url"],
            }
            for r in items
        ],
    }


async def get_file(repo: str, path: str, ref: str = "main") -> dict:
    """Get file contents from a repo."""
    import base64
    data = await _request("GET", f"/repos/{repo}/contents/{path}?ref={ref}")
    if "error" in data:
        return data
    if data.get("encoding") == "base64" and data.get("content"):
        try:
            content = base64.b64decode(data["content"]).decode("utf-8")
        except Exception:
            content = "[binary file]"
    else:
        content = data.get("content", "")
    return {
        "name": data.get("name", ""),
        "path": data.get("path", ""),
        "size": data.get("size", 0),
        "sha": data.get("sha", ""),
        "content": content[:10000],  # cap at 10KB
    }


async def list_issues(repo: str, state: str = "open", limit: int = 10) -> dict:
    """List issues in a repo."""
    data = await _request("GET", f"/repos/{repo}/issues?state={state}&per_page={limit}")
    if "error" in data:
        return data
    return {
        "issues": [
            {
                "number": i["number"],
                "title": i["title"],
                "state": i["state"],
                "labels": [l["name"] for l in i.get("labels", [])],
                "created_at": i["created_at"],
                "url": i["html_url"],
            }
            for i in data if "pull_request" not in i
        ]
    }


async def list_prs(repo: str, state: str = "open", limit: int = 10) -> dict:
    """List pull requests in a repo."""
    data = await _request("GET", f"/repos/{repo}/pulls?state={state}&per_page={limit}")
    if "error" in data:
        return data
    return {
        "pull_requests": [
            {
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "head": pr["head"]["ref"],
                "base": pr["base"]["ref"],
                "url": pr["html_url"],
            }
            for pr in data
        ]
    }


# ── Write Operations (HITL required) ────────────────────────────

async def create_issue(repo: str, title: str, body: str, labels: list[str] | None = None) -> dict:
    """Create an issue in a repo. HITL required."""
    payload = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    return await _request("POST", f"/repos/{repo}/issues", payload)


async def update_issue(repo: str, issue_number: int, **kwargs) -> dict:
    """Update an issue (title, body, state, labels). HITL required."""
    return await _request("PATCH", f"/repos/{repo}/issues/{issue_number}", kwargs)


async def create_or_update_file(
    repo: str, path: str, content: str, message: str, sha: str | None = None, branch: str = "main"
) -> dict:
    """Create or update a file in a repo (self_modify). HITL required."""
    import base64
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    return await _request("PUT", f"/repos/{repo}/contents/{path}", payload)


# ── Dispatch Entry Point ────────────────────────────────────────

async def execute_github(action: str, params: dict[str, Any]) -> str:
    """Main dispatch for GitHub tool calls from the kernel."""
    actions = {
        "search_repos": search_repos,
        "search_code": search_code,
        "get_file": get_file,
        "list_issues": list_issues,
        "list_prs": list_prs,
        "create_issue": create_issue,
        "update_issue": update_issue,
        "create_or_update_file": create_or_update_file,
    }

    fn = actions.get(action)
    if not fn:
        return json.dumps({"error": f"Unknown GitHub action: {action}. Available: {list(actions.keys())}"})

    try:
        result = await fn(**params)
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error(f"GitHub tool error: {e}")
        return json.dumps({"error": str(e)})
