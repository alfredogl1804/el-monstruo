"""
Notion integration tool for El Monstruo kernel.
Uses Notion REST API v2026-03-11 (validated 2026-04-17).

Capabilities:
- Search workspace (pages + databases)
- Read page properties and content (blocks)
- Create pages in databases
- Update page properties
- Append content blocks to pages
- Query databases with filters

Risk: MEDIUM (can create/modify pages)
HITL: Required for write operations (create_page, update_page, append_content)

Uses httpx (async) — same as web_search, consult_sabios, webhook tools.
"""

import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger("monstruo.tools.notion")

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"  # validated 2026-04-17


def _headers() -> dict:
    token = os.environ.get("NOTION_TOKEN", "")
    if not token:
        raise RuntimeError("NOTION_TOKEN not configured")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


async def _request(method: str, path: str, body: dict | None = None) -> dict:
    """Make authenticated request to Notion API."""
    url = f"{NOTION_API}{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        kwargs: dict[str, Any] = {"headers": _headers()}
        if body is not None:
            kwargs["json"] = body
        resp = await client.request(method, url, **kwargs)
        if resp.status_code >= 400:
            text = resp.text[:500]
            logger.error(f"Notion API {resp.status_code}: {text}")
            return {"error": f"Notion API returned {resp.status_code}", "detail": text}
        if resp.text:
            return resp.json()
        return {"status": "ok"}


# ── Read Operations ──────────────────────────────────────────────


async def search(query: str, filter_type: str | None = None, limit: int = 10) -> dict:
    """Search Notion workspace for pages and databases."""
    body: dict[str, Any] = {"query": query, "page_size": min(limit, 100)}
    if filter_type in ("page", "database"):
        body["filter"] = {"value": filter_type, "property": "object"}
    data = await _request("POST", "/search", body)
    if "error" in data:
        return data
    results = data.get("results", [])
    return {
        "total": len(results),
        "has_more": data.get("has_more", False),
        "results": [
            {
                "id": r["id"],
                "type": r["object"],
                "title": _extract_title(r),
                "url": r.get("url", ""),
                "last_edited": r.get("last_edited_time", ""),
            }
            for r in results
        ],
    }


async def get_page(page_id: str) -> dict:
    """Get a page's properties."""
    data = await _request("GET", f"/pages/{page_id}")
    if "error" in data:
        return data
    return {
        "id": data["id"],
        "title": _extract_title(data),
        "url": data.get("url", ""),
        "created_time": data.get("created_time", ""),
        "last_edited_time": data.get("last_edited_time", ""),
        "properties": _simplify_properties(data.get("properties", {})),
    }


async def get_page_content(page_id: str, limit: int = 50) -> dict:
    """Get a page's content (block children)."""
    data = await _request("GET", f"/blocks/{page_id}/children?page_size={min(limit, 100)}")
    if "error" in data:
        return data
    blocks = data.get("results", [])
    return {
        "page_id": page_id,
        "block_count": len(blocks),
        "has_more": data.get("has_more", False),
        "content": [_simplify_block(b) for b in blocks],
    }


async def query_database(
    database_id: str,
    filter_obj: dict | None = None,
    sorts: list | None = None,
    limit: int = 20,
) -> dict:
    """Query a Notion database with optional filters and sorts."""
    body: dict[str, Any] = {"page_size": min(limit, 100)}
    if filter_obj:
        body["filter"] = filter_obj
    if sorts:
        body["sorts"] = sorts
    data = await _request("POST", f"/databases/{database_id}/query", body)
    if "error" in data:
        return data
    results = data.get("results", [])
    return {
        "total": len(results),
        "has_more": data.get("has_more", False),
        "pages": [
            {
                "id": r["id"],
                "title": _extract_title(r),
                "url": r.get("url", ""),
                "properties": _simplify_properties(r.get("properties", {})),
            }
            for r in results
        ],
    }


# ── Write Operations (HITL required) ────────────────────────────


async def create_page(parent_database_id: str, properties: dict, content_blocks: list | None = None) -> dict:
    """Create a new page in a Notion database. HITL required."""
    body: dict[str, Any] = {
        "parent": {"database_id": parent_database_id},
        "properties": properties,
    }
    if content_blocks:
        body["children"] = content_blocks
    return await _request("POST", "/pages", body)


async def update_page(page_id: str, properties: dict) -> dict:
    """Update a page's properties. HITL required."""
    return await _request("PATCH", f"/pages/{page_id}", {"properties": properties})


async def append_content(page_id: str, blocks: list) -> dict:
    """Append content blocks to a page. HITL required."""
    return await _request("PATCH", f"/blocks/{page_id}/children", {"children": blocks})


# ── Helpers ──────────────────────────────────────────────────────


def _extract_title(obj: dict) -> str:
    """Extract title from a Notion page or database object."""
    # Database title
    if obj.get("object") == "database":
        title_arr = obj.get("title", [])
        if title_arr:
            return "".join(t.get("plain_text", "") for t in title_arr)
        return "(untitled database)"

    # Page title — search through properties for title type
    props = obj.get("properties", {})
    for prop_name, prop_val in props.items():
        if prop_val.get("type") == "title":
            title_arr = prop_val.get("title", [])
            if title_arr:
                return "".join(t.get("plain_text", "") for t in title_arr)
    return "(untitled)"


def _simplify_properties(properties: dict) -> dict:
    """Simplify Notion properties to human-readable format."""
    simplified = {}
    for name, prop in properties.items():
        prop_type = prop.get("type", "")
        if prop_type == "title":
            arr = prop.get("title", [])
            simplified[name] = "".join(t.get("plain_text", "") for t in arr)
        elif prop_type == "rich_text":
            arr = prop.get("rich_text", [])
            simplified[name] = "".join(t.get("plain_text", "") for t in arr)
        elif prop_type == "number":
            simplified[name] = prop.get("number")
        elif prop_type == "select":
            sel = prop.get("select")
            simplified[name] = sel.get("name", "") if sel else None
        elif prop_type == "multi_select":
            simplified[name] = [s.get("name", "") for s in prop.get("multi_select", [])]
        elif prop_type == "date":
            d = prop.get("date")
            simplified[name] = d.get("start", "") if d else None
        elif prop_type == "checkbox":
            simplified[name] = prop.get("checkbox", False)
        elif prop_type == "url":
            simplified[name] = prop.get("url")
        elif prop_type == "email":
            simplified[name] = prop.get("email")
        elif prop_type == "phone_number":
            simplified[name] = prop.get("phone_number")
        elif prop_type == "status":
            st = prop.get("status")
            simplified[name] = st.get("name", "") if st else None
        elif prop_type == "relation":
            simplified[name] = [r.get("id", "") for r in prop.get("relation", [])]
        elif prop_type == "formula":
            formula = prop.get("formula", {})
            f_type = formula.get("type", "")
            simplified[name] = formula.get(f_type)
        else:
            simplified[name] = f"({prop_type})"
    return simplified


def _simplify_block(block: dict) -> dict:
    """Simplify a Notion block to human-readable format."""
    block_type = block.get("type", "")
    result: dict[str, Any] = {
        "id": block.get("id", ""),
        "type": block_type,
    }

    block_data = block.get(block_type, {})

    # Extract text from rich_text blocks
    if "rich_text" in block_data:
        text_arr = block_data.get("rich_text", [])
        result["text"] = "".join(t.get("plain_text", "") for t in text_arr)

    # Special handling for specific block types
    if block_type == "image":
        img = block_data.get("file", block_data.get("external", {}))
        result["url"] = img.get("url", "")
    elif block_type == "code":
        text_arr = block_data.get("rich_text", [])
        result["text"] = "".join(t.get("plain_text", "") for t in text_arr)
        result["language"] = block_data.get("language", "")
    elif block_type == "to_do":
        text_arr = block_data.get("rich_text", [])
        result["text"] = "".join(t.get("plain_text", "") for t in text_arr)
        result["checked"] = block_data.get("checked", False)
    elif block_type == "child_database":
        result["title"] = block_data.get("title", "")
    elif block_type == "child_page":
        result["title"] = block_data.get("title", "")

    result["has_children"] = block.get("has_children", False)
    return result


# ── Dispatch Entry Point ────────────────────────────────────────


async def execute_notion(action: str, params: dict[str, Any]) -> str:
    """Main dispatch for Notion tool calls from the kernel."""
    actions = {
        "search": search,
        "get_page": get_page,
        "get_page_content": get_page_content,
        "query_database": query_database,
        "create_page": create_page,
        "update_page": update_page,
        "append_content": append_content,
    }

    fn = actions.get(action)
    if not fn:
        return json.dumps({"error": f"Unknown Notion action: {action}. Available: {list(actions.keys())}"})

    try:
        result = await fn(**params)
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Notion tool error: {e}")
        return json.dumps({"error": str(e)})
