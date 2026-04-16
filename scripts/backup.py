"""
El Monstruo — Automated Backup Script
======================================
Backs up Supabase data and Railway environment to Dropbox.

USAGE:
  python scripts/backup.py              # Run full backup
  python scripts/backup.py --tables     # Backup specific tables only
  python scripts/backup.py --env-only   # Backup env vars only

REQUIREMENTS:
  - SUPABASE_URL and SUPABASE_SERVICE_KEY env vars
  - DROPBOX_API_KEY env var (for cloud storage)
  - supabase, dropbox pip packages

SCHEDULE:
  Designed to run as a daily cron job or via the /v1/backup endpoint.
"""
from __future__ import annotations

import asyncio
import io
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("backup")

# ── Configuration ──────────────────────────────────────────────────

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
DROPBOX_TOKEN = os.environ.get("DROPBOX_API_KEY", "")

# Tables to backup (all Monstruo tables)
BACKUP_TABLES = [
    "conversations",
    "memories",
    "events",
    "knowledge_nodes",
    "knowledge_edges",
    "checkpoints",
    "checkpoint_writes",
]

BACKUP_DIR = "/monstruo-backups"  # Dropbox path


# ── Supabase Data Export ───────────────────────────────────────────

async def export_table_data(table_name: str) -> list[dict]:
    """Export all rows from a Supabase table via REST API."""
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Paginate through all rows (1000 at a time)
        all_rows = []
        offset = 0
        page_size = 1000

        while True:
            response = (
                client.table(table_name)
                .select("*")
                .range(offset, offset + page_size - 1)
                .execute()
            )
            rows = response.data or []
            all_rows.extend(rows)

            if len(rows) < page_size:
                break
            offset += page_size

        logger.info("table_exported", table=table_name, rows=len(all_rows))
        return all_rows

    except Exception as e:
        logger.error("table_export_failed", table=table_name, error=str(e))
        return []


async def export_all_tables(tables: Optional[list[str]] = None) -> dict[str, Any]:
    """Export all specified tables to a single JSON structure."""
    tables = tables or BACKUP_TABLES
    backup_data = {
        "metadata": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "supabase_url": SUPABASE_URL[:50] + "..." if SUPABASE_URL else "not_configured",
            "tables": tables,
        },
        "tables": {},
    }

    for table in tables:
        rows = await export_table_data(table)
        backup_data["tables"][table] = {
            "row_count": len(rows),
            "data": rows,
        }

    total_rows = sum(t["row_count"] for t in backup_data["tables"].values())
    backup_data["metadata"]["total_rows"] = total_rows
    logger.info("full_export_complete", tables=len(tables), total_rows=total_rows)

    return backup_data


# ── Environment Variables Backup ───────────────────────────────────

def export_env_vars() -> dict[str, str]:
    """Export relevant environment variables (redacted secrets)."""
    # Only export non-secret config vars, redact actual secrets
    env_vars = {}
    relevant_prefixes = [
        "SUPABASE_", "KERNEL_", "MONSTRUO_", "LANGFUSE_",
        "OPENAI_", "ANTHROPIC_", "GOOGLE_", "PERPLEXITY_",
        "XAI_", "DEEPSEEK_", "MOONSHOT_", "ELEVENLABS_",
        "HEYGEN_", "TELEGRAM_", "NOTION_", "DROPBOX_",
    ]

    for key, value in os.environ.items():
        for prefix in relevant_prefixes:
            if key.startswith(prefix):
                # Redact the actual value, just store that it exists
                if "KEY" in key or "SECRET" in key or "TOKEN" in key or "PASSWORD" in key:
                    env_vars[key] = f"***SET*** (len={len(value)})"
                else:
                    env_vars[key] = value
                break

    return env_vars


# ── Dropbox Upload ─────────────────────────────────────────────────

def upload_to_dropbox(content: bytes, remote_path: str) -> Optional[str]:
    """Upload a file to Dropbox and return the shared link."""
    if not DROPBOX_TOKEN:
        logger.warning("dropbox_not_configured", hint="Set DROPBOX_API_KEY")
        return None

    try:
        import dropbox
        dbx = dropbox.Dropbox(DROPBOX_TOKEN)

        # Upload file (overwrite if exists)
        dbx.files_upload(
            content,
            remote_path,
            mode=dropbox.files.WriteMode.overwrite,
        )

        logger.info("dropbox_uploaded", path=remote_path, size_bytes=len(content))

        # Create shared link
        try:
            link = dbx.sharing_create_shared_link_with_settings(remote_path)
            return link.url
        except dropbox.exceptions.ApiError:
            # Link might already exist
            links = dbx.sharing_list_shared_links(path=remote_path).links
            if links:
                return links[0].url
            return None

    except Exception as e:
        logger.error("dropbox_upload_failed", path=remote_path, error=str(e))
        return None


# ── Local Backup (Fallback) ────────────────────────────────────────

def save_local_backup(content: bytes, filename: str) -> str:
    """Save backup locally as fallback when Dropbox is unavailable."""
    backup_dir = "/tmp/monstruo-backups"
    os.makedirs(backup_dir, exist_ok=True)
    filepath = os.path.join(backup_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    logger.info("local_backup_saved", path=filepath, size_bytes=len(content))
    return filepath


# ── Main Backup Orchestrator ───────────────────────────────────────

async def run_backup(
    tables: Optional[list[str]] = None,
    include_env: bool = True,
    upload: bool = True,
) -> dict[str, Any]:
    """
    Run a full backup of Supabase data and environment.

    Returns:
        dict with backup results including paths and stats.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    results = {
        "timestamp": timestamp,
        "status": "started",
        "data_backup": None,
        "env_backup": None,
        "dropbox_links": [],
        "local_paths": [],
        "errors": [],
    }

    # 1. Export Supabase data
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            backup_data = await export_all_tables(tables)
            data_json = json.dumps(backup_data, indent=2, default=str).encode("utf-8")
            data_filename = f"monstruo_data_{timestamp}.json"

            results["data_backup"] = {
                "tables": len(backup_data["tables"]),
                "total_rows": backup_data["metadata"]["total_rows"],
                "size_bytes": len(data_json),
            }

            if upload and DROPBOX_TOKEN:
                link = upload_to_dropbox(data_json, f"{BACKUP_DIR}/{data_filename}")
                if link:
                    results["dropbox_links"].append(link)

            # Always save locally too
            local_path = save_local_backup(data_json, data_filename)
            results["local_paths"].append(local_path)

        except Exception as e:
            results["errors"].append(f"Data backup failed: {str(e)}")
            logger.error("data_backup_failed", error=str(e))
    else:
        results["errors"].append("Supabase not configured — skipping data backup")

    # 2. Export environment variables
    if include_env:
        try:
            env_data = export_env_vars()
            env_json = json.dumps(
                {"timestamp": timestamp, "env_vars": env_data},
                indent=2,
            ).encode("utf-8")
            env_filename = f"monstruo_env_{timestamp}.json"

            results["env_backup"] = {
                "vars_count": len(env_data),
                "size_bytes": len(env_json),
            }

            if upload and DROPBOX_TOKEN:
                link = upload_to_dropbox(env_json, f"{BACKUP_DIR}/{env_filename}")
                if link:
                    results["dropbox_links"].append(link)

            local_path = save_local_backup(env_json, env_filename)
            results["local_paths"].append(local_path)

        except Exception as e:
            results["errors"].append(f"Env backup failed: {str(e)}")
            logger.error("env_backup_failed", error=str(e))

    results["status"] = "completed" if not results["errors"] else "partial"
    logger.info(
        "backup_completed",
        status=results["status"],
        dropbox_links=len(results["dropbox_links"]),
        errors=len(results["errors"]),
    )

    return results


# ── CLI Entry Point ────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="El Monstruo Backup Script")
    parser.add_argument("--tables", nargs="*", help="Specific tables to backup")
    parser.add_argument("--env-only", action="store_true", help="Only backup env vars")
    parser.add_argument("--no-upload", action="store_true", help="Skip Dropbox upload")
    args = parser.parse_args()

    if args.env_only:
        env_data = export_env_vars()
        print(json.dumps(env_data, indent=2))
    else:
        result = asyncio.run(run_backup(
            tables=args.tables,
            include_env=True,
            upload=not args.no_upload,
        ))
        print(json.dumps(result, indent=2, default=str))
