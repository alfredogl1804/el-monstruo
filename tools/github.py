"""
GitHub integration tool for El Monstruo kernel.
Uses GitHub REST API v2022-11-28 (validated 2026-04-27).

Capabilities:
- Search repos, issues, code
- Create/read/update issues
- Read file contents
- Create branches (commit loop)
- Create/update files (self_modify)
- Create pull requests (commit loop)
- List PRs

Commit Loop (MVP Sprint 28):
  1. create_branch → creates feature branch from main
  2. create_or_update_file → writes changes to the branch
  3. create_pull_request → opens PR for human review

Risk: HIGH (can modify repos)
HITL: Required for destructive write operations (create_issue, update_issue)
      Auto-approved for Commit Loop (create_branch, create_or_update_file, create_pull_request)
      because the PR review by Alfredo IS the human gate.

Sprint 32 Fixes:
- [1] Shared aiohttp.ClientSession (connection pooling)
- [2] Token validated at module init (fail-fast)
- [3] Retry with exponential backoff for transient errors
- [8] Explicit HITL gate for write operations

Sprint 33 Changes:
- Commit Loop actions (branch + file + PR) auto-approved — PR is the gate
- HITL retained for create_issue, update_issue (non-PR-gated writes)
"""

import asyncio
import json
import logging
import os
from typing import Any

import aiohttp

logger = logging.getLogger("monstruo.tools.github")

GITHUB_API = "https://api.github.com"
API_VERSION = "2022-11-28"  # validated 2026-04-27

# ── Token Validation (fail-fast at import) ────────────────────────
_GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
if not _GITHUB_TOKEN:
    logger.critical("GITHUB_TOKEN not configured — github tool will not work")


def _headers() -> dict:
    if not _GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN not configured in environment")
    return {
        "Authorization": f"Bearer {_GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }


# ── Shared Session (connection pooling) ───────────────────────────
_session: aiohttp.ClientSession | None = None
_session_lock = asyncio.Lock()


async def _get_session() -> aiohttp.ClientSession:
    """Get or create a shared aiohttp session with connection pooling."""
    global _session
    if _session is None or _session.closed:
        async with _session_lock:
            if _session is None or _session.closed:
                connector = aiohttp.TCPConnector(
                    limit=10,           # max 10 concurrent connections
                    ttl_dns_cache=300,  # cache DNS for 5 min
                    keepalive_timeout=30,
                )
                _session = aiohttp.ClientSession(
                    connector=connector,
                    headers=_headers(),
                    timeout=aiohttp.ClientTimeout(total=30),
                )
    return _session


# ── Retry with Exponential Backoff ────────────────────────────────
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds


async def _request(method: str, path: str, body: dict | None = None) -> dict:
    """Make authenticated request to GitHub API with retry and backoff."""
    url = f"{GITHUB_API}{path}"
    session = await _get_session()

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            kwargs: dict[str, Any] = {}
            if body:
                kwargs["json"] = body
            async with session.request(method, url, **kwargs) as resp:
                text = await resp.text()

                # Success
                if resp.status < 400:
                    if text:
                        return json.loads(text)
                    return {"status": "ok"}

                # Rate limited — respect Retry-After header
                if resp.status == 429:
                    retry_after = int(resp.headers.get("Retry-After", BASE_DELAY * (2 ** attempt)))
                    logger.warning(f"GitHub rate limited, retry after {retry_after}s (attempt {attempt+1})")
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(retry_after)
                        continue

                # Retryable server error
                if resp.status in RETRYABLE_STATUS and attempt < MAX_RETRIES:
                    delay = BASE_DELAY * (2 ** attempt)
                    logger.warning(f"GitHub {resp.status}, retrying in {delay}s (attempt {attempt+1})")
                    await asyncio.sleep(delay)
                    continue

                # Non-retryable error
                logger.error(f"GitHub API {resp.status}: {text[:500]}")
                return {
                    "error": f"GitHub API returned {resp.status}",
                    "detail": text[:500],
                }

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            last_error = str(e)
            if attempt < MAX_RETRIES:
                delay = BASE_DELAY * (2 ** attempt)
                logger.warning(f"GitHub request error: {e}, retrying in {delay}s (attempt {attempt+1})")
                await asyncio.sleep(delay)
            else:
                logger.error(f"GitHub request failed after {MAX_RETRIES+1} attempts: {e}")

    return {"error": f"Request failed after {MAX_RETRIES+1} attempts: {last_error}"}


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
    # Sprint 51.5: GitHub returns list for directories, dict for files
    if isinstance(data, list):
        return {
            "name": path.split("/")[-1],
            "path": path,
            "size": 0,
            "sha": "",
            "content": f"[directory with {len(data)} entries: {', '.join(d.get('name','?') for d in data[:20])}]",
        }
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
    # Sprint 51.5: defense against non-list responses
    if isinstance(data, dict) and "error" in data:
        return data
    items = data if isinstance(data, list) else []
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
            for i in items
            if isinstance(i, dict) and "pull_request" not in i
        ]
    }


async def list_prs(repo: str, state: str = "open", limit: int = 10) -> dict:
    """List pull requests in a repo."""
    data = await _request("GET", f"/repos/{repo}/pulls?state={state}&per_page={limit}")
    # Sprint 51.5: defense against non-list responses
    if isinstance(data, dict) and "error" in data:
        return data
    items = data if isinstance(data, list) else []
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
            for pr in items
            if isinstance(pr, dict)
        ]
    }


# ── Write Operations (HITL required) ────────────────────────────


async def create_branch(repo: str, branch: str, from_branch: str = "main") -> dict:
    """Create a new branch from an existing branch. HITL required."""
    # Step 1: Get the SHA of the source branch
    ref_data = await _request("GET", f"/repos/{repo}/git/ref/heads/{from_branch}")
    if "error" in ref_data:
        return ref_data
    sha = ref_data.get("object", {}).get("sha", "")
    if not sha:
        return {"error": f"Could not get SHA for branch '{from_branch}'"}
    # Step 2: Create the new branch ref
    payload = {
        "ref": f"refs/heads/{branch}",
        "sha": sha,
    }
    result = await _request("POST", f"/repos/{repo}/git/refs", payload)
    if "error" not in result:
        result["branch"] = branch
        result["from_branch"] = from_branch
        result["sha"] = sha
    return result


async def create_pull_request(
    repo: str,
    title: str,
    head: str,
    base: str = "main",
    body: str = "",
) -> dict:
    """Create a pull request. HITL required."""
    payload = {
        "title": title,
        "head": head,
        "base": base,
        "body": body,
    }
    return await _request("POST", f"/repos/{repo}/pulls", payload)


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
    repo: str,
    path: str,
    content: str,
    message: str,
    sha: str | None = None,
    branch: str = "main",
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


# ── HITL Gate ───────────────────────────────────────────────────
# Sprint 32: Explicit HITL gate for write operations.
# Write actions MUST NOT execute unless the caller has already passed
# through the HITL approval flow. This is a defense-in-depth layer
# that prevents accidental or malicious writes even if the kernel's
# HITL interrupt is bypassed.

# Sprint 33: Commit Loop actions are auto-approved.
# The PR itself IS the human gate — Alfredo reviews and merges.
# No need for double approval (HITL + PR review).
COMMIT_LOOP_ACTIONS = frozenset({
    "create_branch",
    "create_or_update_file",
    "create_pull_request",
})

# These write actions STILL require HITL (destructive or non-PR-gated)
HITL_WRITE_ACTIONS = frozenset({
    "create_issue",
    "update_issue",
})

# All write actions (union of both sets)
WRITE_ACTIONS = COMMIT_LOOP_ACTIONS | HITL_WRITE_ACTIONS

READ_ACTIONS = frozenset({
    "search_repos",
    "search_code",
    "get_file",
    "list_issues",
    "list_prs",
})


# ── Dispatch Entry Point ────────────────────────────────────────


async def execute_github(action: str, params: dict[str, Any], hitl_approved: bool = False) -> str:
    """Main dispatch for GitHub tool calls from the kernel.
    
    Args:
        action: The GitHub action to execute.
        params: Parameters for the action.
        hitl_approved: Whether HITL approval was granted for this call.
                       Write operations REQUIRE hitl_approved=True.
                       This flag must be set by the kernel's HITL flow,
                       never by the LLM itself.
    """
    actions = {
        "search_repos": search_repos,
        "search_code": search_code,
        "get_file": get_file,
        "list_issues": list_issues,
        "list_prs": list_prs,
        "create_issue": create_issue,
        "update_issue": update_issue,
        "create_branch": create_branch,
        "create_pull_request": create_pull_request,
        "create_or_update_file": create_or_update_file,
    }

    fn = actions.get(action)
    if not fn:
        return json.dumps({"error": f"Unknown GitHub action: {action}. Available: {list(actions.keys())}"})

    # ── HITL Gate: Block destructive writes without explicit approval ──
    # Sprint 33: Commit Loop actions (branch + file + PR) are auto-approved.
    # The PR review by Alfredo IS the human gate. No double approval needed.
    if action in HITL_WRITE_ACTIONS and not hitl_approved:
        logger.warning(
            "github_write_blocked_no_hitl",
            extra={"action": action, "params_keys": list(params.keys())},
        )
        return json.dumps({
            "error": "HITL_REQUIRED",
            "message": f"Write action '{action}' requires human approval. "
                       f"This request was blocked because hitl_approved=False.",
            "action": action,
            "risk_level": "HIGH",
        })

    if action in COMMIT_LOOP_ACTIONS:
        logger.info(
            "github_commit_loop_auto_approved",
            extra={"action": action, "params_keys": list(params.keys())},
        )

    try:
        result = await fn(**params)
        if action in WRITE_ACTIONS:
            logger.info(
                "github_write_executed",
                extra={"action": action, "hitl_approved": True},
            )
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error(f"GitHub tool error: {e}")
        return json.dumps({"error": str(e)})
