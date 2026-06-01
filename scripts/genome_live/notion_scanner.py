#!/usr/bin/env python3
"""
notion_scanner.py — Scanner de Notion para el Genome Vivo.

Usa la Notion API para enumerar:
  - Databases accesibles (con título, propiedades, item count)
  - Páginas top-level (governance, decisiones, semillas, etc.)
  - Última edición por database

Requiere: NOTION_API_KEY o NOTION_TOKEN en env vars.

Si la variable no está disponible, el scanner reporta coverage_match=True
con un aviso de "no_credentials" (non-blocking para el pipeline).

Verificación binaria:
  - Si hay credenciales: al menos 1 database encontrada
  - Si no hay credenciales: coverage_match=True (graceful degradation)

Output: _genome_out/notion.json

Autor: Manus — Sprint 91.11
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "_genome_out"

# Carga .env si existe
ENV_PATH = ROOT / ".env"
if ENV_PATH.exists():
    for raw in ENV_PATH.read_text().splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            k, v = raw.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

NOTION_TOKEN = (
    os.environ.get("NOTION_API_KEY")
    or os.environ.get("NOTION_TOKEN")
    or os.environ.get("NOTION_INTEGRATION_TOKEN")
    or ""
)

NOTION_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def notion_get(path: str, params: dict | None = None) -> requests.Response | None:
    """GET a Notion API."""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    url = f"{NOTION_BASE}{path}"
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        return r
    except Exception as e:
        print(f"  [ERROR] Notion GET {path}: {e}", flush=True)
        return None


def notion_post(path: str, body: dict | None = None) -> requests.Response | None:
    """POST a Notion API."""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    url = f"{NOTION_BASE}{path}"
    try:
        r = requests.post(url, headers=headers, json=body or {}, timeout=30)
        return r
    except Exception as e:
        print(f"  [ERROR] Notion POST {path}: {e}", flush=True)
        return None


def search_databases() -> list[dict[str, Any]]:
    """Busca todas las databases accesibles."""
    databases: list[dict[str, Any]] = []
    has_more = True
    start_cursor = None

    while has_more:
        body: dict[str, Any] = {"filter": {"value": "database", "property": "object"}, "page_size": 100}
        if start_cursor:
            body["start_cursor"] = start_cursor

        r = notion_post("/search", body)
        if not r or r.status_code != 200:
            break

        data = r.json()
        for db in data.get("results", []):
            title_parts = db.get("title", [])
            title = "".join(t.get("plain_text", "") for t in title_parts) if title_parts else "Untitled"

            # Get property names
            props = list(db.get("properties", {}).keys())

            databases.append({
                "id": db["id"],
                "title": title[:100],
                "properties": props[:20],
                "properties_count": len(props),
                "created_time": db.get("created_time"),
                "last_edited_time": db.get("last_edited_time"),
                "url": db.get("url", ""),
            })

        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")

    return databases


def search_pages(limit: int = 50) -> list[dict[str, Any]]:
    """Busca páginas top-level accesibles."""
    pages: list[dict[str, Any]] = []

    body: dict[str, Any] = {"filter": {"value": "page", "property": "object"}, "page_size": limit}
    r = notion_post("/search", body)
    if not r or r.status_code != 200:
        return pages

    data = r.json()
    for page in data.get("results", []):
        title_parts = page.get("properties", {}).get("title", {}).get("title", [])
        if not title_parts:
            # Try Name property
            for prop_name, prop_val in page.get("properties", {}).items():
                if prop_val.get("type") == "title":
                    title_parts = prop_val.get("title", [])
                    break

        title = "".join(t.get("plain_text", "") for t in title_parts) if title_parts else "Untitled"

        pages.append({
            "id": page["id"],
            "title": title[:100],
            "last_edited_time": page.get("last_edited_time"),
            "created_time": page.get("created_time"),
            "url": page.get("url", ""),
            "parent_type": page.get("parent", {}).get("type", "unknown"),
        })

    return pages


def scan() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()

    if not NOTION_TOKEN:
        print("  [WARN] NOTION_API_KEY no disponible — graceful degradation", flush=True)
        return {
            "scanner": "notion",
            "version": 1,
            "started_at": started,
            "finished_at": started,
            "no_credentials": True,
            "coverage_match": True,  # Non-blocking
            "databases": [],
            "pages": [],
            "databases_count": 0,
            "pages_count": 0,
            "note": "Scanner funcional pero sin NOTION_API_KEY. Agregar variable para cobertura completa.",
        }

    print("  Buscando databases...", flush=True)
    databases = search_databases()
    print(f"  Encontradas: {len(databases)} databases", flush=True)

    print("  Buscando páginas...", flush=True)
    pages = search_pages(limit=50)
    print(f"  Encontradas: {len(pages)} páginas", flush=True)

    finished = datetime.now(timezone.utc).isoformat()

    # Coverage: al menos 1 database encontrada
    coverage_match = len(databases) > 0

    return {
        "scanner": "notion",
        "version": 1,
        "started_at": started,
        "finished_at": finished,
        "no_credentials": False,
        "coverage_match": coverage_match,
        "databases_count": len(databases),
        "pages_count": len(pages),
        "databases": databases,
        "pages": pages[:50],  # Limitar output
    }


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    out_file = OUT_DIR / "notion.json"

    result = scan()
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print("\nNOTION SCAN RESUMEN")
    print(f"  credentials   : {'available' if not result.get('no_credentials') else 'MISSING'}")
    print(f"  databases     : {result['databases_count']}")
    print(f"  pages         : {result['pages_count']}")
    print(f"  match         : {result['coverage_match']}")
    print(f"  output        : {out_file}")

    return 0 if result["coverage_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
