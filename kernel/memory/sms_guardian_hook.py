"""
kernel/memory/sms_guardian_hook.py — Guardian V4 Integration Hook for SMS

This module hooks into the Guardian recovery flow to inject sovereign axioms
and relevant memories at session start. It extends Guardian V3's tri-anchor
system with a 4th anchor: Sovereign Memory.

Usage:
  1. Guardian V3 runs its tri-anchor recovery
  2. After IDENTIDAD RESTAURADA, this hook is called
  3. It fetches sovereign axioms + relevant memories from Supabase
  4. Prints them as part of the Guardian output (injected into context)

Can also be called standalone:
  python -m kernel.memory.sms_guardian_hook [agent_id] [query]

Integration with guardian.py:
  Add after OMEGA section:
    from kernel.memory.sms_guardian_hook import inject_sovereign_context
    inject_sovereign_context(agent_id="manus_c")

Author: Manus C (Batch 011 — SMS Guardian Integration)
Date: 2026-05-21
"""

from __future__ import annotations

import json
import logging
import os
import sys
import urllib.error
import urllib.request
from typing import Optional

logger = logging.getLogger("monstruo.sms.guardian")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG (reads from env, same as session_memory.py pattern)
# ═══════════════════════════════════════════════════════════════════════════════


def _get_config() -> dict:
    """Get SMS config from environment."""
    return {
        "url": os.environ.get("SUPABASE_URL", ""),
        "service_key": (os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")),
        "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
        "openai_base_url": os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1"),
        "embedding_model": os.environ.get("SMS_EMBEDDING_MODEL", "text-embedding-3-small"),
    }


def _is_available() -> bool:
    """Check if SMS Supabase is configured."""
    cfg = _get_config()
    return bool(cfg["url"] and cfg["service_key"])


# ═══════════════════════════════════════════════════════════════════════════════
# SUPABASE HELPERS (zero dependencies, same pattern as session_memory.py)
# ═══════════════════════════════════════════════════════════════════════════════


def _supabase_get(path: str, timeout: int = 10) -> list:
    """GET request to Supabase REST API."""
    cfg = _get_config()
    url = f"{cfg['url']}/rest/v1{path}"
    headers = {
        "apikey": cfg["service_key"],
        "Authorization": f"Bearer {cfg['service_key']}",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload) if payload else []
    except Exception as e:
        logger.debug(f"SMS Supabase GET failed: {e}")
        return []


def _supabase_rpc(function_name: str, params: dict, timeout: int = 10) -> list:
    """Call Supabase RPC function."""
    cfg = _get_config()
    url = f"{cfg['url']}/rest/v1/rpc/{function_name}"
    headers = {
        "apikey": cfg["service_key"],
        "Authorization": f"Bearer {cfg['service_key']}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(params).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload) if payload else []
    except Exception as e:
        logger.debug(f"SMS RPC {function_name} failed: {e}")
        return []


def _generate_embedding(text: str) -> Optional[list[float]]:
    """Generate embedding for semantic search."""
    cfg = _get_config()
    if not cfg["openai_api_key"]:
        return None

    url = f"{cfg['openai_base_url']}/embeddings"
    headers = {
        "Authorization": f"Bearer {cfg['openai_api_key']}",
        "Content-Type": "application/json",
    }
    body = {
        "model": cfg["embedding_model"],
        "input": text[:4000],
        "dimensions": 1536,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["data"][0]["embedding"]
    except Exception as e:
        logger.debug(f"Embedding generation failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# CORE: FETCH SOVEREIGN CONTEXT
# ═══════════════════════════════════════════════════════════════════════════════


def fetch_sovereign_axioms(agent_id: str = None, limit: int = 20) -> list[dict]:
    """Fetch active sovereign axioms from Supabase."""
    filters = "is_active=eq.true"
    if agent_id:
        filters += f"&source_agent=eq.{agent_id}"
    path = f"/sovereign_axioms?{filters}&order=confidence.desc,validation_count.desc&limit={limit}"
    return _supabase_get(path)


def fetch_relevant_memories(query: str, agent_id: str = None, limit: int = 5) -> list[dict]:
    """Semantic search for relevant memories."""
    embedding = _generate_embedding(query)
    if not embedding:
        # Fallback: get most recent memories
        filters = "is_alive=eq.true"
        if agent_id:
            filters += f"&agent_id=eq.{agent_id}"
        path = f"/sovereign_memories?{filters}&order=created_at.desc&limit={limit}"
        return _supabase_get(path)

    params = {
        "query_embedding": json.dumps(embedding),
        "match_threshold": 0.6,
        "match_count": limit,
        "only_alive": True,
    }
    if agent_id:
        params["filter_agent"] = agent_id

    return _supabase_rpc("match_sovereign_memories", params)


def fetch_unresolved_gaps(agent_id: str = None, limit: int = 5) -> list[dict]:
    """Fetch unresolved knowledge gaps."""
    filters = "is_resolved=eq.false"
    if agent_id:
        filters += f"&agent_id=eq.{agent_id}"
    path = f"/sovereign_knowledge_gaps?{filters}&order=created_at.desc&limit={limit}"
    return _supabase_get(path)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN: INJECT SOVEREIGN CONTEXT
# ═══════════════════════════════════════════════════════════════════════════════


def inject_sovereign_context(
    agent_id: str = "manus_c",
    query: str = None,
    print_output: bool = True,
) -> str:
    """
    Inject sovereign context into the Guardian output.

    This is the main function called by Guardian V4 after tri-anchor recovery.
    It prints (and returns) the sovereign context block.
    """
    if not _is_available():
        block = "  SMS: No configurado (SUPABASE_URL/SERVICE_KEY faltantes)"
        if print_output:
            print("=" * 70)
            print("  SOVEREIGN MEMORY — DEGRADED")
            print("=" * 70)
            print(block)
        return block

    lines = []

    # ── Sovereign Axioms ──
    axioms = fetch_sovereign_axioms(agent_id=None, limit=15)
    if axioms:
        lines.append("=" * 70)
        lines.append("  SOVEREIGN AXIOMS (compaction-proof, NEVER violate)")
        lines.append("=" * 70)
        for ax in axioms:
            stmt = ax.get("statement", "")[:60]
            conf = ax.get("confidence", 1.0)
            val_count = ax.get("validation_count", 0)
            src = ax.get("source_agent", "?")[:10]
            lines.append(f"  [AX:{conf:.1f}|v{val_count}|{src}] {stmt}")
            imps = ax.get("implications")
            if imps:
                if isinstance(imps, str):
                    try:
                        imps = json.loads(imps)
                    except:
                        imps = []
                for imp in imps[:2]:
                    lines.append(f"    -> {imp[:58]}")

    # ── Relevant Memories (if query provided) ──
    if query:
        memories = fetch_relevant_memories(query, agent_id=agent_id, limit=5)
        if memories:
            lines.append("")
            lines.append("-" * 70)
            lines.append("  RELEVANT MEMORIES (semantic match)")
            lines.append("-" * 70)
            for mem in memories:
                content = mem.get("content", "")[:56]
                sim = mem.get("similarity", 0)
                mtype = mem.get("memory_type", "?")[:4]
                lines.append(f"  [{mtype}:{sim:.2f}] {content}")

    # ── Knowledge Gaps ──
    gaps = fetch_unresolved_gaps(agent_id=agent_id, limit=3)
    if gaps:
        lines.append("")
        lines.append("-" * 70)
        lines.append("  KNOWLEDGE GAPS (unresolved)")
        lines.append("-" * 70)
        for gap in gaps:
            q = gap.get("question", "")[:56]
            sev = gap.get("severity", "MED")[:4]
            lines.append(f"  [GAP:{sev}] {q}")

    # ── Stats ──
    lines.append("")
    lines.append(f"  SMS: {len(axioms)} axioms | query={query or 'none'} | agent={agent_id}")
    lines.append("=" * 70)

    block = "\n".join(lines)
    if print_output:
        print(block)

    return block


# ═══════════════════════════════════════════════════════════════════════════════
# GUARDIAN V4 PATCH INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
#
# In monstruo-memoria/guardian.py, after the OMEGA Lessons section
# (around line 410, before the closing box), add:
#
#     # === Sovereign Memory System (4th anchor) ===
#     try:
#         sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
#         from kernel.memory.sms_guardian_hook import inject_sovereign_context
#         inject_sovereign_context(
#             agent_id=identity.get("hilo", "manus_c"),
#             query=identity.get("proyecto_activo"),
#         )
#     except Exception as e:
#         print(f"  SMS: {e}")
#
# This makes Guardian V4 = V3 + Sovereign Memory injection.
# ═══════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    agent = sys.argv[1] if len(sys.argv) > 1 else "manus_c"
    query = sys.argv[2] if len(sys.argv) > 2 else None

    print()
    print("=" * 70)
    print("  SMS Guardian Hook — Standalone Test")
    print(f"  Agent: {agent} | Query: {query or 'none'}")
    print("=" * 70)
    print()

    inject_sovereign_context(agent_id=agent, query=query)
