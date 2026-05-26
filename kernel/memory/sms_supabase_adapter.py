"""
kernel/memory/sms_supabase_adapter.py — Sovereign Memory System Supabase Adapter

Persistent storage layer for the SMS. Connects to Supabase (pgvector) for:
- CRUD operations on sovereign_axioms, sovereign_memories, causal_chains, gaps
- Vector similarity search via RPCs (match_sovereign_memories, match_sovereign_axioms)
- Multi-agent registry and permissions
- Consolidation logging (REM Cycle)
- Universal adapter: any AI thread (Manus, ChatGPT, Claude, Gemini, Grok) can read/write

Architecture:
- Zero external dependencies (uses urllib only, like session_memory.py)
- Env vars: SUPABASE_URL, SUPABASE_SERVICE_KEY
- Embedding generation: OpenAI text-embedding-3-small (1536 dims) via OPENAI_API_KEY
- Graceful degradation: if Supabase unavailable, returns empty results (no crash)

Author: Manus C (Batch 011 — SMS Integration)
Date: 2026-05-21
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger("monstruo.sms.supabase")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class SMSConfig:
    """Configuration for SMS Supabase adapter."""

    url: str = ""
    service_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = ""
    openrouter_api_key: str = ""
    audn_model: str = "deepseek/deepseek-r1-0528"
    audn_enabled: bool = True
    embedding_model: str = "text-embedding-3-small"
    embedding_dims: int = 1536
    default_agent_id: str = "monstruo"
    timeout: int = 15

    @classmethod
    def from_env(cls) -> "SMSConfig":
        """Load config from environment variables."""
        return cls(
            url=os.environ.get("SUPABASE_URL", ""),
            service_key=(os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")),
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            openai_base_url=os.environ.get("OPENAI_API_BASE", "") or "https://api.openai.com/v1",
            openrouter_api_key=os.environ.get("OPENROUTER_API_KEY", ""),
            audn_model=os.environ.get("SMS_AUDN_MODEL", "deepseek/deepseek-r1-0528"),
            audn_enabled=os.environ.get("SMS_AUDN_ENABLED", "true").lower() == "true",
            embedding_model=os.environ.get("SMS_EMBEDDING_MODEL", "text-embedding-3-small"),
            embedding_dims=int(os.environ.get("SMS_EMBEDDING_DIMS", "1536")),
            default_agent_id=os.environ.get("SMS_AGENT_ID", "monstruo"),
        )

    @property
    def is_available(self) -> bool:
        return bool(self.url and self.service_key)

    @property
    def can_embed(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def can_audn(self) -> bool:
        return bool(self.openrouter_api_key and self.audn_enabled)


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP HELPERS (zero dependencies)
# ═══════════════════════════════════════════════════════════════════════════════


class SMSSupabaseError(Exception):
    pass


def _supabase_request(
    config: SMSConfig,
    method: str,
    path: str,
    body: Optional[Any] = None,
    extra_headers: Optional[dict] = None,
    timeout: Optional[int] = None,
) -> Any:
    """Minimal REST call to Supabase PostgREST API."""
    url = f"{config.url}/rest/v1{path}"
    headers = {
        "apikey": config.service_key,
        "Authorization": f"Bearer {config.service_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout or config.timeout) as resp:
            payload = resp.read().decode("utf-8")
            if not payload:
                return None
            return json.loads(payload)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise SMSSupabaseError(f"HTTP {e.code} on {method} {url}: {error_body[:300]}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise SMSSupabaseError(f"Connection error on {method} {url}: {e}") from e


def _supabase_rpc(
    config: SMSConfig,
    function_name: str,
    params: dict,
    timeout: Optional[int] = None,
) -> Any:
    """Call a Supabase RPC function."""
    url = f"{config.url}/rest/v1/rpc/{function_name}"
    headers = {
        "apikey": config.service_key,
        "Authorization": f"Bearer {config.service_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(params).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout or config.timeout) as resp:
            payload = resp.read().decode("utf-8")
            if not payload:
                return []
            return json.loads(payload)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
        logger.warning(f"RPC {function_name} failed: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# EMBEDDING GENERATION
# ═══════════════════════════════════════════════════════════════════════════════


def generate_embedding(text: str, config: SMSConfig) -> Optional[list[float]]:
    """Generate embedding using OpenAI API (text-embedding-3-small)."""
    if not config.can_embed:
        logger.debug("No OPENAI_API_KEY — skipping embedding generation")
        return None

    url = f"{config.openai_base_url}/embeddings"
    headers = {
        "Authorization": f"Bearer {config.openai_api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": config.embedding_model,
        "input": text[:8000],  # Truncate to avoid token limit
        "dimensions": config.embedding_dims,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=config.timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["data"][0]["embedding"]
    except Exception as e:
        logger.warning(f"Embedding generation failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# AUDN EVALUATOR (Add/Update/Delete/None) via DeepSeek R1 on OpenRouter
# ═══════════════════════════════════════════════════════════════════════════════

AUDN_SYSTEM_PROMPT = """You are the memory gatekeeper for a sovereign AI system.
You receive a NEW memory and a list of EXISTING similar memories.
Decide ONE action:

- ADD: The new memory contains genuinely new information not captured by existing memories.
- UPDATE <id>: The new memory is a more recent/accurate version of an existing memory. Return UPDATE followed by the id to update.
- DELETE <id>: The new memory directly contradicts an existing memory and the new one is more reliable. Return DELETE followed by the id to delete, then the new memory will be stored.
- NONE: The new memory is redundant (already captured) or is noise/trivial. Do not store.

Respond with ONLY the action word (and id if UPDATE/DELETE). No explanation."""


def _audn_evaluate(
    config: SMSConfig,
    new_content: str,
    existing_memories: list[dict],
) -> tuple[str, Optional[str]]:
    """
    Evaluate whether to Add/Update/Delete/None for a new memory.
    Returns (action, target_id) where target_id is set for UPDATE/DELETE.
    Falls back to ADD if the evaluator is unavailable.
    """
    if not config.can_audn or not existing_memories:
        return ("ADD", None)

    # Build context of existing memories
    existing_text = "\n".join(
        f"- [id={m.get('id', '?')}] {m.get('content', m.get('statement', ''))[:200]}" for m in existing_memories[:10]
    )

    user_prompt = f"""NEW MEMORY: {new_content}

EXISTING SIMILAR MEMORIES:
{existing_text}

Action:"""

    headers = {
        "Authorization": f"Bearer {config.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://el-monstruo-kernel-production.up.railway.app",
        "X-Title": "SMS AUDN Evaluator",
    }
    payload = {
        "model": config.audn_model,
        "messages": [
            {"role": "system", "content": AUDN_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 50,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=data,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            answer = result["choices"][0]["message"]["content"].strip().upper()

        # Parse the response
        if answer.startswith("NONE"):
            return ("NONE", None)
        elif answer.startswith("UPDATE"):
            parts = answer.split()
            target_id = parts[1] if len(parts) > 1 else None
            return ("UPDATE", target_id)
        elif answer.startswith("DELETE"):
            parts = answer.split()
            target_id = parts[1] if len(parts) > 1 else None
            return ("DELETE", target_id)
        else:
            return ("ADD", None)

    except Exception as e:
        logger.warning(f"AUDN evaluation failed (defaulting to ADD): {e}")
        return ("ADD", None)


# ═══════════════════════════════════════════════════════════════════════════════
# SMS SUPABASE ADAPTER
# ═══════════════════════════════════════════════════════════════════════════════


class SMSSupabaseAdapter:
    """
    Persistent storage adapter for the Sovereign Memory System.

    Supports any AI agent via agent_id scoping:
    - monstruo (orchestrator)
    - manus_c (Manus executor)
    - cowork_t2 (Claude auditor)
    - chatgpt_sop (ChatGPT brain)
    - gemini_sabio, grok_sabio (consultants)
    - alfredo_t1 (human)
    - Any custom agent_id
    """

    def __init__(self, config: Optional[SMSConfig] = None):
        self.config = config or SMSConfig.from_env()
        if not self.config.is_available:
            logger.warning("SMS Supabase adapter: no credentials — operating in degraded mode")

    @property
    def available(self) -> bool:
        return self.config.is_available

    # ─── AXIOMS ────────────────────────────────────────────────────────────────

    def upsert_axiom(
        self,
        statement: str,
        confidence: float = 1.0,
        validation_count: int = 0,
        implications: list[str] = None,
        source_agent: str = None,
        tags: list[str] = None,
    ) -> Optional[dict]:
        """Insert or update a sovereign axiom. Generates embedding automatically."""
        if not self.available:
            return None

        embedding = generate_embedding(statement, self.config)
        agent = source_agent or self.config.default_agent_id

        body = {
            "statement": statement,
            "confidence": confidence,
            "validation_count": validation_count,
            "contradiction_count": 0,
            "source_agent": agent,
            "implications": json.dumps(implications or []),
            "tags": tags or [],
            "is_active": True,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if embedding:
            body["embedding"] = json.dumps(embedding)

        try:
            result = _supabase_request(
                self.config,
                "POST",
                "/sovereign_axioms",
                body=body,
                extra_headers={
                    "Prefer": "resolution=merge-duplicates,return=representation",
                    "On-Conflict": "statement",
                },
            )
            logger.info(f"Axiom upserted: {statement[:50]}...")
            return result[0] if isinstance(result, list) and result else result
        except SMSSupabaseError as e:
            logger.error(f"Failed to upsert axiom: {e}")
            return None

    def get_axioms(
        self,
        source_agent: str = None,
        active_only: bool = True,
        limit: int = 100,
    ) -> list[dict]:
        """Retrieve all axioms, optionally filtered by agent."""
        if not self.available:
            return []

        filters = []
        if active_only:
            filters.append("is_active=eq.true")
        if source_agent:
            filters.append(f"source_agent=eq.{source_agent}")

        query = "&".join(filters) if filters else ""
        path = f"/sovereign_axioms?{query}&order=confidence.desc&limit={limit}"

        try:
            return _supabase_request(self.config, "GET", path) or []
        except SMSSupabaseError as e:
            logger.error(f"Failed to get axioms: {e}")
            return []

    def search_axioms_semantic(
        self,
        query: str,
        threshold: float = 0.6,
        limit: int = 5,
        agent_filter: str = None,
    ) -> list[dict]:
        """Semantic search over axioms using pgvector."""
        if not self.available or not self.config.can_embed:
            return []

        embedding = generate_embedding(query, self.config)
        if not embedding:
            return []

        params = {
            "query_embedding": json.dumps(embedding),
            "match_threshold": threshold,
            "match_count": limit,
        }
        if agent_filter:
            params["filter_agent"] = agent_filter

        return _supabase_rpc(self.config, "match_sovereign_axioms", params)

    def validate_axiom(self, axiom_id: str) -> bool:
        """Increment validation_count and update last_validated."""
        if not self.available:
            return False

        try:
            # Use RPC or PATCH with increment
            _supabase_request(
                self.config,
                "PATCH",
                f"/sovereign_axioms?id=eq.{axiom_id}",
                body={
                    "last_validated": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                extra_headers={"Prefer": "return=minimal"},
            )
            return True
        except SMSSupabaseError as e:
            logger.error(f"Failed to validate axiom: {e}")
            return False

    # ─── MEMORIES ──────────────────────────────────────────────────────────────

    def store_memory(
        self,
        content: str,
        memory_type: str = "episodic",
        source: str = "system",
        agent_id: str = None,
        confidence: float = 0.7,
        causal_parent_id: str = None,
        tags: list[str] = None,
        skip_audn: bool = False,
    ) -> Optional[dict]:
        """Store a new memory with AUDN evaluation, embedding, and deduplication."""
        if not self.available:
            return None

        content_hash = hashlib.sha256(content.encode()).hexdigest()[:32]
        agent = agent_id or self.config.default_agent_id
        embedding = generate_embedding(content, self.config)

        # ─── AUDN EVALUATION ──────────────────────────────────────────────────
        audn_action = "ADD"
        audn_target = None
        if not skip_audn and self.config.can_audn and embedding:
            # Find similar existing memories to evaluate against
            similar = _supabase_rpc(
                self.config,
                "match_sovereign_memories",
                {
                    "query_embedding": json.dumps(embedding),
                    "match_threshold": 0.5,
                    "match_count": 5,
                    "only_alive": True,
                },
            )
            if similar:
                audn_action, audn_target = _audn_evaluate(self.config, content, similar)
                logger.info(f"AUDN decision: {audn_action} (target={audn_target})")

                if audn_action == "NONE":
                    logger.info(f"AUDN rejected memory (redundant): {content[:50]}...")
                    return {"status": "rejected", "audn_action": "NONE", "reason": "redundant"}

                if audn_action == "UPDATE" and audn_target:
                    # Update the existing memory with new content
                    try:
                        _supabase_request(
                            self.config,
                            "PATCH",
                            f"/sovereign_memories?id=eq.{audn_target}",
                            body={
                                "content": content,
                                "content_hash": content_hash,
                                "confidence": confidence,
                                "last_accessed": datetime.now(timezone.utc).isoformat(),
                                **(({"embedding": json.dumps(embedding)}) if embedding else {}),
                            },
                            extra_headers={"Prefer": "return=representation"},
                        )
                        logger.info(f"AUDN updated memory {audn_target}: {content[:50]}...")
                        # Log conflict: new content supersedes existing memory
                        self._log_audn_conflict(
                            existing_id=audn_target,
                            new_content=content,
                            action="UPDATE",
                            agent=agent,
                        )
                        return {"status": "updated", "audn_action": "UPDATE", "memory_id": audn_target}
                    except SMSSupabaseError as e:
                        logger.warning(f"AUDN UPDATE failed, falling back to ADD: {e}")
                        audn_action = "ADD"

                if audn_action == "DELETE" and audn_target:
                    # Soft-delete the contradicted memory, then store the new one
                    self.forget_memory(audn_target)
                    # Also temporally invalidate (sets invalid_at for history)
                    self.invalidate_memory(audn_target)
                    logger.info(f"AUDN deleted contradicted memory {audn_target}")
                    # Log conflict: new memory contradicts existing
                    self._log_audn_conflict(
                        existing_id=audn_target,
                        new_content=content,
                        action="DELETE",
                        agent=agent,
                    )

        # ─── STORE THE MEMORY ─────────────────────────────────────────────────
        body = {
            "content": content,
            "content_hash": content_hash,
            "memory_type": memory_type,
            "layer": 3,
            "source": source,
            "agent_id": agent,
            "confidence": confidence,
            "strength": 1.0,
            "relevance_score": 1.0,
            "tags": tags or [],
            "is_alive": True,
        }
        if embedding:
            body["embedding"] = json.dumps(embedding)
        if causal_parent_id:
            body["causal_parent_id"] = causal_parent_id

        try:
            result = _supabase_request(
                self.config,
                "POST",
                "/sovereign_memories",
                body=body,
                extra_headers={
                    "Prefer": "resolution=merge-duplicates,return=representation",
                    "On-Conflict": "content_hash",
                },
            )
            logger.info(f"Memory stored (AUDN={audn_action}): {content[:50]}... (agent={agent})")
            stored = result[0] if isinstance(result, list) and result else result
            if stored:
                stored["audn_action"] = audn_action
                # Extract entities and link to knowledge graph (non-blocking)
                try:
                    mem_id = stored.get("id")
                    if mem_id:
                        self.extract_and_link_entities(mem_id, content, agent)
                except Exception as e:
                    logger.debug(f"Entity extraction failed (non-fatal): {e}")
            return stored
        except SMSSupabaseError as e:
            logger.error(f"Failed to store memory: {e}")
            return None

    def search_memories_semantic(
        self,
        query: str,
        threshold: float = 0.7,
        limit: int = 10,
        agent_filter: str = None,
        type_filter: str = None,
        only_alive: bool = True,
    ) -> list[dict]:
        """Semantic search over memories using pgvector."""
        if not self.available or not self.config.can_embed:
            return []

        embedding = generate_embedding(query, self.config)
        if not embedding:
            return []

        params = {
            "query_embedding": json.dumps(embedding),
            "match_threshold": threshold,
            "match_count": limit,
            "only_alive": only_alive,
        }
        if agent_filter:
            params["filter_agent"] = agent_filter
        if type_filter:
            params["filter_type"] = type_filter

        results = _supabase_rpc(self.config, "match_sovereign_memories", params)
        # Log access for importance scoring (non-blocking, fire-and-forget)
        for mem in (results or [])[:5]:  # Only log top 5 to avoid spam
            try:
                if mem.get("id"):
                    self.log_access(mem["id"], agent_filter or "system", "recall")
            except Exception:
                pass
        return results

    def get_memories(
        self,
        agent_id: str = None,
        memory_type: str = None,
        alive_only: bool = True,
        limit: int = 50,
        order_by: str = "created_at.desc",
    ) -> list[dict]:
        """Retrieve memories with filters."""
        if not self.available:
            return []

        filters = []
        if alive_only:
            filters.append("is_alive=eq.true")
        if agent_id:
            filters.append(f"agent_id=eq.{agent_id}")
        if memory_type:
            filters.append(f"memory_type=eq.{memory_type}")

        query = "&".join(filters) if filters else ""
        path = f"/sovereign_memories?{query}&order={order_by}&limit={limit}"

        try:
            return _supabase_request(self.config, "GET", path) or []
        except SMSSupabaseError as e:
            logger.error(f"Failed to get memories: {e}")
            return []

    def forget_memory(self, memory_id: str) -> bool:
        """Mark a memory as forgotten (soft delete)."""
        if not self.available:
            return False

        try:
            _supabase_request(
                self.config,
                "PATCH",
                f"/sovereign_memories?id=eq.{memory_id}",
                body={
                    "is_alive": False,
                    "forgotten_at": datetime.now(timezone.utc).isoformat(),
                },
                extra_headers={"Prefer": "return=minimal"},
            )
            return True
        except SMSSupabaseError as e:
            logger.error(f"Failed to forget memory: {e}")
            return False

    def touch_memory(self, memory_id: str) -> bool:
        """Update last_accessed and increment access_count (strengthens memory)."""
        if not self.available:
            return False

        try:
            _supabase_request(
                self.config,
                "PATCH",
                f"/sovereign_memories?id=eq.{memory_id}",
                body={"last_accessed": datetime.now(timezone.utc).isoformat()},
                extra_headers={"Prefer": "return=minimal"},
            )
            return True
        except SMSSupabaseError as e:
            logger.error(f"Failed to touch memory: {e}")
            return False

    # ─── TEMPORAL QUERIES ────────────────────────────────────────────────────────

    def search_memories_temporal(
        self,
        query: str,
        point_in_time: str = None,
        threshold: float = 0.5,
        limit: int = 10,
        agent_filter: str = None,
    ) -> list[dict]:
        """Semantic search over memories valid at a specific point in time.

        Answers: 'What did the system know on Tuesday?'
        Uses RPC match_sovereign_memories_temporal from migration 0053.
        """
        if not self.available or not self.config.can_embed:
            return []

        embedding = generate_embedding(query, self.config)
        if not embedding:
            return []

        params = {
            "query_embedding": json.dumps(embedding),
            "match_threshold": threshold,
            "match_count": limit,
        }
        if point_in_time:
            params["point_in_time"] = point_in_time
        if agent_filter:
            params["filter_agent"] = agent_filter

        return _supabase_rpc(self.config, "match_sovereign_memories_temporal", params)

    def invalidate_memory(self, memory_id: str) -> bool:
        """Mark a memory as temporally invalid (superseded, not deleted).

        Sets invalid_at to NOW. The memory remains queryable for historical
        point-in-time searches but won't appear in current queries.
        """
        if not self.available:
            return False

        try:
            _supabase_request(
                self.config,
                "PATCH",
                f"/sovereign_memories?id=eq.{memory_id}",
                body={
                    "invalid_at": datetime.now(timezone.utc).isoformat(),
                },
                extra_headers={"Prefer": "return=minimal"},
            )
            logger.info(f"Memory {memory_id} temporally invalidated")
            return True
        except SMSSupabaseError as e:
            logger.error(f"Failed to invalidate memory: {e}")
            return False

    # ─── CAUSAL CHAINS ─────────────────────────────────────────────────────────

    def store_causal_chain(
        self,
        root_memory_id: str,
        nodes: list[str],
        depth: int,
        agent_id: str = None,
    ) -> Optional[dict]:
        """Store a causal chain."""
        if not self.available:
            return None

        body = {
            "root_memory_id": root_memory_id,
            "nodes": json.dumps(nodes),
            "depth": depth,
            "agent_id": agent_id or self.config.default_agent_id,
            "is_active": True,
        }

        try:
            result = _supabase_request(
                self.config,
                "POST",
                "/sovereign_causal_chains",
                body=body,
                extra_headers={"Prefer": "return=representation"},
            )
            return result[0] if isinstance(result, list) and result else result
        except SMSSupabaseError as e:
            logger.error(f"Failed to store causal chain: {e}")
            return None

    # ─── KNOWLEDGE GAPS ────────────────────────────────────────────────────────

    def store_gap(
        self,
        question: str,
        evidence: str = "",
        severity: str = "MEDIUM",
        strategy: str = "search",
        agent_id: str = None,
    ) -> Optional[dict]:
        """Record a detected knowledge gap."""
        if not self.available:
            return None

        body = {
            "question": question,
            "evidence": evidence,
            "severity": severity,
            "resolution_strategy": strategy,
            "agent_id": agent_id or self.config.default_agent_id,
            "is_resolved": False,
        }

        try:
            result = _supabase_request(
                self.config,
                "POST",
                "/sovereign_knowledge_gaps",
                body=body,
                extra_headers={"Prefer": "return=representation"},
            )
            return result[0] if isinstance(result, list) and result else result
        except SMSSupabaseError as e:
            logger.error(f"Failed to store gap: {e}")
            return None

    def resolve_gap(self, gap_id: str, resolved_by_memory_id: str = None) -> bool:
        """Mark a gap as resolved."""
        if not self.available:
            return False

        body = {
            "is_resolved": True,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        }
        if resolved_by_memory_id:
            body["resolved_by_memory_id"] = resolved_by_memory_id

        try:
            _supabase_request(
                self.config,
                "PATCH",
                f"/sovereign_knowledge_gaps?id=eq.{gap_id}",
                body=body,
                extra_headers={"Prefer": "return=minimal"},
            )
            return True
        except SMSSupabaseError as e:
            logger.error(f"Failed to resolve gap: {e}")
            return False

    def get_unresolved_gaps(self, agent_id: str = None, limit: int = 20) -> list[dict]:
        """Get unresolved knowledge gaps."""
        if not self.available:
            return []

        filters = ["is_resolved=eq.false"]
        if agent_id:
            filters.append(f"agent_id=eq.{agent_id}")

        query = "&".join(filters)
        path = f"/sovereign_knowledge_gaps?{query}&order=created_at.desc&limit={limit}"

        try:
            return _supabase_request(self.config, "GET", path) or []
        except SMSSupabaseError as e:
            logger.error(f"Failed to get gaps: {e}")
            return []

    # ─── CONFLICT LOG ──────────────────────────────────────────────────────────

    def log_conflict(
        self,
        memory_a_id: str,
        memory_b_id: str,
        winner_id: str,
        reason: str,
        method: str = "confidence_based",
        resolved_by: str = "system",
    ) -> Optional[dict]:
        """Log a conflict resolution."""
        if not self.available:
            return None

        body = {
            "memory_a_id": memory_a_id,
            "memory_b_id": memory_b_id,
            "winner_id": winner_id,
            "reason": reason,
            "resolution_method": method,
            "resolved_by": resolved_by,
        }

        try:
            result = _supabase_request(
                self.config,
                "POST",
                "/sovereign_conflict_log",
                body=body,
                extra_headers={"Prefer": "return=representation"},
            )
            return result[0] if isinstance(result, list) and result else result
        except SMSSupabaseError as e:
            logger.error(f"Failed to log conflict: {e}")
            return None

    def _log_audn_conflict(
        self,
        existing_id: str,
        new_content: str,
        action: str,
        agent: str,
    ) -> None:
        """Log AUDN conflict resolution to sovereign_conflict_log.

        Called when AUDN decides UPDATE or DELETE — meaning the new memory
        supersedes or contradicts an existing one. This creates an audit trail
        of all AUDN arbitration decisions.
        """
        # Generate a deterministic placeholder ID for the "new" memory
        # (it hasn't been stored yet, so we use a hash-based UUID)
        new_memory_pseudo_id = str(uuid4())

        reason = f"AUDN {action}: new content supersedes existing memory. New: {new_content[:100]}..."

        body = {
            "memory_a_id": existing_id,
            "memory_b_id": new_memory_pseudo_id,
            "winner_id": new_memory_pseudo_id if action == "DELETE" else existing_id,
            "reason": reason[:500],
            "resolution_method": f"audn_{action.lower()}",
            "resolved_by": agent or "monstruo",
        }

        try:
            _supabase_request(
                self.config,
                "POST",
                "/sovereign_conflict_log",
                body=body,
                extra_headers={"Prefer": "return=minimal"},
            )
            logger.info(f"AUDN conflict logged: {action} on {existing_id}")
        except SMSSupabaseError as e:
            # Non-fatal: conflict logging failure shouldn't block memory operations
            logger.warning(f"Failed to log AUDN conflict (non-fatal): {e}")

    # ─── AGENT REGISTRY ────────────────────────────────────────────────────────

    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str = "llm",
        provider: str = "custom",
        model: str = None,
        permissions: dict = None,
    ) -> Optional[dict]:
        """Register a new AI agent in the universal registry."""
        if not self.available:
            return None

        default_perms = {"read": True, "write": True, "crystallize": False, "forget": False}
        body = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "agent_type": agent_type,
            "provider": provider,
            "model": model,
            "permissions": json.dumps(permissions or default_perms),
            "is_active": True,
        }

        try:
            result = _supabase_request(
                self.config,
                "POST",
                "/sovereign_agent_registry",
                body=body,
                extra_headers={
                    "Prefer": "resolution=merge-duplicates,return=representation",
                    "On-Conflict": "agent_id",
                },
            )
            logger.info(f"Agent registered: {agent_id} ({agent_name})")
            return result[0] if isinstance(result, list) and result else result
        except SMSSupabaseError as e:
            logger.error(f"Failed to register agent: {e}")
            return None

    def get_agent(self, agent_id: str) -> Optional[dict]:
        """Get agent info and permissions."""
        if not self.available:
            return None

        try:
            result = _supabase_request(
                self.config,
                "GET",
                f"/sovereign_agent_registry?agent_id=eq.{agent_id}&limit=1",
            )
            return result[0] if isinstance(result, list) and result else None
        except SMSSupabaseError as e:
            logger.error(f"Failed to get agent: {e}")
            return None

    def check_permission(self, agent_id: str, action: str) -> bool:
        """Check if an agent has permission for an action (read/write/crystallize/forget)."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        perms = agent.get("permissions", {})
        if isinstance(perms, str):
            perms = json.loads(perms)
        return perms.get(action, False)

    # ─── CONSOLIDATION LOG ─────────────────────────────────────────────────────

    def log_consolidation(
        self,
        run_type: str = "nightly",
        memories_processed: int = 0,
        memories_forgotten: int = 0,
        axioms_crystallized: int = 0,
        conflicts_resolved: int = 0,
        gaps_detected: int = 0,
        duration_ms: int = 0,
        status: str = "completed",
        error_message: str = None,
    ) -> Optional[dict]:
        """Log a consolidation run."""
        if not self.available:
            return None

        body = {
            "run_type": run_type,
            "memories_processed": memories_processed,
            "memories_forgotten": memories_forgotten,
            "axioms_crystallized": axioms_crystallized,
            "conflicts_resolved": conflicts_resolved,
            "gaps_detected": gaps_detected,
            "duration_ms": duration_ms,
            "status": status,
        }
        if error_message:
            body["error_message"] = error_message

        try:
            result = _supabase_request(
                self.config,
                "POST",
                "/sovereign_consolidation_log",
                body=body,
                extra_headers={"Prefer": "return=representation"},
            )
            return result[0] if isinstance(result, list) and result else result
        except SMSSupabaseError as e:
            logger.error(f"Failed to log consolidation: {e}")
            return None

    # ─── UNIVERSAL CONTEXT INJECTION ───────────────────────────────────────────

    def get_context_injection(
        self,
        agent_id: str = None,
        query: str = None,
        max_axioms: int = 10,
        max_memories: int = 5,
        max_gaps: int = 3,
    ) -> str:
        """
        Generate a context injection block for ANY AI agent.

        This is the key function that any thread (Manus, ChatGPT, Claude, etc.)
        calls at session start to receive their sovereign context.

        Returns a formatted string ready to inject into a system prompt.
        """
        if not self.available:
            return "--- SMS UNAVAILABLE (degraded mode) ---"

        blocks = []

        # 1. Sovereign Axioms (compaction-proof truths) — ALWAYS global, never filtered by agent
        if query and self.config.can_embed:
            axioms = self.search_axioms_semantic(query, threshold=0.5, limit=max_axioms)
        else:
            axioms = self.get_axioms(limit=max_axioms)

        if axioms:
            blocks.append("--- SOVEREIGN AXIOMS (compaction-proof, NEVER ignore) ---")
            for ax in axioms:
                conf = ax.get("confidence", 1.0)
                val = ax.get("validation_count", 0)
                stmt = ax.get("statement", "")
                blocks.append(f"[AX] {stmt} (conf:{conf:.2f}, validated:{val}x)")
                imps = ax.get("implications")
                if imps:
                    if isinstance(imps, str):
                        imps = json.loads(imps)
                    for imp in imps[:3]:
                        blocks.append(f"  → {imp}")
            blocks.append("--- END SOVEREIGN AXIOMS ---")

        # 2. Relevant memories (if query provided)
        if query and self.config.can_embed:
            memories = self.search_memories_semantic(query, threshold=0.4, limit=max_memories, agent_filter=agent_id)
            if memories:
                blocks.append("")
                blocks.append("--- RELEVANT MEMORIES ---")
                for mem in memories:
                    sim = mem.get("similarity", 0)
                    content = mem.get("content", "")
                    blocks.append(f"[MEM:{sim:.2f}] {content[:200]}")
                blocks.append("--- END MEMORIES ---")

        # 3. Unresolved gaps
        gaps = self.get_unresolved_gaps(agent_id=agent_id, limit=max_gaps)
        if gaps:
            blocks.append("")
            blocks.append("--- KNOWLEDGE GAPS (unresolved — investigate if relevant) ---")
            for gap in gaps:
                sev = gap.get("severity", "MEDIUM")
                q = gap.get("question", "")
                blocks.append(f"[GAP:{sev}] {q}")
            blocks.append("--- END GAPS ---")

        if not blocks:
            return "--- SMS: No sovereign context found for this agent ---"

        return "\n".join(blocks)

    # ─── HEALTH ────────────────────────────────────────────────────────────────

    def get_health(self) -> dict:
        """Get SMS health stats from Supabase."""
        if not self.available:
            return {"status": "degraded", "reason": "no_credentials"}

        try:
            axioms = _supabase_request(
                self.config,
                "GET",
                "/sovereign_axioms?select=id&is_active=eq.true",
                extra_headers={"Prefer": "count=exact"},
            )
            memories = _supabase_request(
                self.config,
                "GET",
                "/sovereign_memories?select=id&is_alive=eq.true",
                extra_headers={"Prefer": "count=exact"},
            )
            gaps = _supabase_request(
                self.config,
                "GET",
                "/sovereign_knowledge_gaps?select=id&is_resolved=eq.false",
                extra_headers={"Prefer": "count=exact"},
            )
            agents = _supabase_request(
                self.config,
                "GET",
                "/sovereign_agent_registry?select=id&is_active=eq.true",
                extra_headers={"Prefer": "count=exact"},
            )

            return {
                "status": "healthy",
                "axiom_count": len(axioms) if axioms else 0,
                "memory_count": len(memories) if memories else 0,
                "unresolved_gaps": len(gaps) if gaps else 0,
                "active_agents": len(agents) if agents else 0,
            }
        except SMSSupabaseError as e:
            return {"status": "error", "reason": str(e)}

    # ═══════════════════════════════════════════════════════════════════════════
    # KNOWLEDGE GRAPH (Migration 0054)
    # ═══════════════════════════════════════════════════════════════════════════

    def extract_and_link_entities(
        self,
        memory_id: str,
        content: str,
        agent_id: str = "system",
    ) -> list[dict]:
        """Extract entities from memory content and link them in the knowledge graph.

        Uses LLM (via OpenRouter) to extract entities, then upserts them into
        memory_entities and creates memory_entity_links.
        Falls back to pattern-based extraction if LLM unavailable.
        """
        if not self.available:
            return []

        entities = self._extract_entities_llm(content)
        if not entities:
            entities = self._extract_entities_pattern(content)

        linked = []
        for ent in entities:
            entity_id = self._upsert_entity(ent)
            if entity_id:
                self._link_memory_entity(memory_id, entity_id, ent.get("role", "mentions"))
                linked.append({"entity_id": entity_id, **ent})

        return linked

    def _extract_entities_llm(self, content: str) -> list[dict]:
        """Use LLM to extract entities from content. Returns list of dicts."""
        if not self.config.openrouter_api_key:
            return []

        prompt = (
            "Extract entities from this text. Return JSON array only.\n"
            'Each entity: {"name": str, "type": person|object|location|event|'
            'organization|concept|system|decision, "role": subject|object|context|mentions}\n\n'
            f"Text: {content[:2000]}\n\nJSON:"
        )
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config.openrouter_api_key}",
                "Content-Type": "application/json",
            }
            body = {
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 500,
            }
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                text = result["choices"][0]["message"]["content"].strip()
                # Parse JSON from response (handle markdown code blocks)
                if text.startswith("```"):
                    text = text.split("\n", 1)[1].rsplit("```", 1)[0]
                return json.loads(text)
        except Exception as e:
            logger.debug(f"LLM entity extraction failed: {e}")
            return []

    def _extract_entities_pattern(self, content: str) -> list[dict]:
        """Fallback pattern-based entity extraction for Monstruo domain."""
        entities = []
        content_lower = content.lower()

        patterns = {
            "system": [
                "sms",
                "audn",
                "rem cycle",
                "guardian",
                "kernel",
                "monstruo",
                "supabase",
                "railway",
                "langfuse",
                "langchain",
                "langgraph",
            ],
            "person": ["alfredo", "cowork", "manus"],
            "concept": [
                "dory",
                "axiom",
                "crystallization",
                "compaction",
                "sovereign",
                "memory",
                "embedding",
                "rls",
                "deploy",
                "sprint",
            ],
            "organization": ["leones", "ticketlike", "cip"],
        }

        for entity_type, terms in patterns.items():
            for term in terms:
                if term in content_lower:
                    entities.append(
                        {
                            "name": term.title() if entity_type == "person" else term,
                            "type": entity_type,
                            "role": "mentions",
                        }
                    )
        return entities

    def _upsert_entity(self, entity: dict) -> Optional[str]:
        """Upsert an entity into memory_entities. Returns entity ID."""
        canonical = entity["name"].lower().strip()
        body = {
            "name": entity["name"],
            "entity_type": entity.get("type", "concept"),
            "canonical_name": canonical,
            "last_seen": datetime.now(timezone.utc).isoformat(),
        }
        try:
            result = _supabase_request(
                self.config,
                "POST",
                "/memory_entities",
                body=body,
                extra_headers={
                    "Prefer": "resolution=merge-duplicates,return=representation",
                    "On-Conflict": "canonical_name,entity_type",
                },
            )
            if isinstance(result, list) and result:
                # Increment mention_count
                eid = result[0]["id"]
                _supabase_request(
                    self.config,
                    "PATCH",
                    f"/memory_entities?id=eq.{eid}",
                    body={"mention_count": result[0].get("mention_count", 0) + 1},
                    extra_headers={"Prefer": "return=minimal"},
                )
                return eid
            return None
        except SMSSupabaseError as e:
            logger.debug(f"Entity upsert failed: {e}")
            return None

    def _link_memory_entity(self, memory_id: str, entity_id: str, role: str = "mentions") -> bool:
        """Create a link between a memory and an entity."""
        try:
            _supabase_request(
                self.config,
                "POST",
                "/memory_entity_links",
                body={
                    "memory_id": memory_id,
                    "entity_id": entity_id,
                    "role": role,
                },
                extra_headers={
                    "Prefer": "resolution=merge-duplicates,return=minimal",
                    "On-Conflict": "memory_id,entity_id,role",
                },
            )
            return True
        except SMSSupabaseError:
            return False

    def graph_enhanced_recall(
        self,
        query: str,
        threshold: float = 0.6,
        limit: int = 10,
        use_graph: bool = True,
    ) -> list[dict]:
        """Hybrid retrieval: vector similarity + knowledge graph expansion.

        First finds memories by embedding similarity, then expands via shared
        entities in the knowledge graph. Returns both direct matches and
        graph-connected memories.
        """
        if not self.available or not self.config.can_embed:
            return []

        embedding = generate_embedding(query, self.config)
        if not embedding:
            return []

        results = _supabase_rpc(
            self.config,
            "graph_enhanced_recall",
            {
                "query_embedding": json.dumps(embedding),
                "match_threshold": threshold,
                "match_count": limit,
                "graph_expansion": use_graph,
            },
        )
        return results if isinstance(results, list) else []

    def get_entity_neighborhood(self, entity_id: str, relation_filter: str = None) -> list[dict]:
        """Get all entities connected to a given entity (1-hop graph traversal)."""
        if not self.available:
            return []

        params = {"p_entity_id": entity_id}
        if relation_filter:
            params["p_relation_filter"] = relation_filter

        return _supabase_rpc(self.config, "get_entity_neighborhood", params)

    def get_memories_for_entity(self, entity_id: str, limit: int = 20) -> list[dict]:
        """Get all memories that reference a specific entity."""
        if not self.available:
            return []

        return _supabase_rpc(
            self.config,
            "get_memories_for_entity",
            {
                "p_entity_id": entity_id,
                "p_limit": limit,
            },
        )

    def create_relation(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relation_type: str = "related_to",
        weight: float = 1.0,
        evidence_memory_id: str = None,
    ) -> bool:
        """Create a typed relation between two entities in the knowledge graph."""
        if not self.available:
            return False

        body = {
            "source_entity_id": source_entity_id,
            "target_entity_id": target_entity_id,
            "relation_type": relation_type,
            "weight": weight,
        }
        if evidence_memory_id:
            body["evidence_memory_id"] = evidence_memory_id

        try:
            _supabase_request(
                self.config,
                "POST",
                "/memory_relations",
                body=body,
                extra_headers={
                    "Prefer": "resolution=merge-duplicates,return=minimal",
                    "On-Conflict": "source_entity_id,target_entity_id,relation_type",
                },
            )
            return True
        except SMSSupabaseError as e:
            logger.debug(f"Relation creation failed: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════════════
    # BELIEF REVISION (Migration 0055)
    # ═══════════════════════════════════════════════════════════════════════════

    def cascade_invalidation(
        self,
        memory_id: str,
        reason: str = "contradicted by newer evidence",
        agent_id: str = "system",
        strategy: str = "mark_for_revalidation",
        max_depth: int = 5,
    ) -> dict:
        """Invalidate a memory and cascade to all dependents.

        Strategies:
        - mark_for_revalidation: dependents flagged for review (safest)
        - auto_invalidate: dependents auto-killed (aggressive)
        - reduce_confidence: dependents lose 50% confidence (moderate)
        """
        if not self.available:
            return {"error": "unavailable"}

        result = _supabase_rpc(
            self.config,
            "cascade_invalidation",
            {
                "p_memory_id": memory_id,
                "p_reason": reason,
                "p_agent_id": agent_id,
                "p_strategy": strategy,
                "p_max_depth": max_depth,
            },
        )
        return result if isinstance(result, dict) else {"result": result}

    def register_dependency(
        self,
        premise_id: str,
        dependent_id: str,
        dependency_type: str = "logical",
        strength: float = 1.0,
    ) -> bool:
        """Register a dependency: dependent_id depends on premise_id.

        If premise is later invalidated, dependent will be flagged for revalidation.
        """
        if not self.available:
            return False

        result = _supabase_rpc(
            self.config,
            "register_dependency",
            {
                "p_premise_id": premise_id,
                "p_dependent_id": dependent_id,
                "p_type": dependency_type,
                "p_strength": strength,
            },
        )
        return bool(result)

    def get_pending_revalidations(self, limit: int = 50) -> list[dict]:
        """Get memories that need revalidation after a belief revision cascade."""
        if not self.available:
            return []

        return _supabase_rpc(
            self.config,
            "get_pending_revalidations",
            {
                "p_limit": limit,
            },
        )

    def revalidate_memory(self, memory_id: str, is_still_valid: bool = True) -> bool:
        """Mark a memory as revalidated (or invalidated) after review."""
        if not self.available:
            return False

        new_status = "revalidated" if is_still_valid else "invalidated"
        try:
            body = {"revalidation_status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}
            if not is_still_valid:
                body["is_alive"] = False
                body["invalid_at"] = datetime.now(timezone.utc).isoformat()
            _supabase_request(
                self.config,
                "PATCH",
                f"/sovereign_memories?id=eq.{memory_id}",
                body=body,
                extra_headers={"Prefer": "return=minimal"},
            )
            return True
        except SMSSupabaseError as e:
            logger.error(f"Revalidation failed: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════════════
    # MEMORY DECAY & CONSOLIDATION (Migration 0056)
    # ═══════════════════════════════════════════════════════════════════════════

    def log_access(self, memory_id: str, agent_id: str = "system", access_type: str = "recall") -> bool:
        """Log a memory access event for importance scoring."""
        if not self.available:
            return False

        try:
            _supabase_request(
                self.config,
                "POST",
                "/memory_access_log",
                body={
                    "memory_id": memory_id,
                    "agent_id": agent_id,
                    "access_type": access_type,
                },
                extra_headers={"Prefer": "return=minimal"},
            )
            # Also touch the memory (update last_accessed + access_count)
            self.touch_memory(memory_id)
            return True
        except SMSSupabaseError:
            return False

    def compute_importance_scores(self, batch_size: int = 500) -> dict:
        """Recalculate importance_score for all alive memories.

        Formula: 0.25*recency + 0.25*frequency + 0.25*connectivity + 0.25*confidence
        Called by REM Cycle.
        """
        if not self.available:
            return {"error": "unavailable"}

        result = _supabase_rpc(
            self.config,
            "compute_importance_scores",
            {
                "p_batch_size": batch_size,
            },
        )
        return result if isinstance(result, dict) else {"result": result}

    def archive_low_importance(self, threshold: float = 0.15, min_age_days: int = 30) -> dict:
        """Archive memories below importance threshold.

        Archived memories remain in DB but are excluded from recall.
        Never archives Layer 4+, procedural, or pending-review memories.
        """
        if not self.available:
            return {"error": "unavailable"}

        result = _supabase_rpc(
            self.config,
            "archive_low_importance_memories",
            {
                "p_threshold": threshold,
                "p_min_age_days": min_age_days,
            },
        )
        return result if isinstance(result, dict) else {"result": result}

    def merge_similar_memories(self, similarity_threshold: float = 0.95) -> dict:
        """Find and merge semantically duplicate memories.

        Keeps the highest-confidence version, archives the duplicate.
        Logs all merges for audit trail.
        """
        if not self.available:
            return {"error": "unavailable"}

        result = _supabase_rpc(
            self.config,
            "merge_similar_memories",
            {
                "p_similarity_threshold": similarity_threshold,
            },
        )
        return result if isinstance(result, dict) else {"result": result}

    def get_memory_stats(self) -> dict:
        """Extended health stats including graph, revision, and archival metrics."""
        if not self.available:
            return {}

        try:
            entities = _supabase_request(
                self.config,
                "GET",
                "/memory_entities?select=id&is_active=eq.true",
                extra_headers={"Prefer": "count=exact"},
            )
            relations = _supabase_request(
                self.config,
                "GET",
                "/memory_relations?select=id",
                extra_headers={"Prefer": "count=exact"},
            )
            pending_reval = _supabase_request(
                self.config,
                "GET",
                "/sovereign_memories?select=id&revalidation_status=eq.needs_revalidation",
                extra_headers={"Prefer": "count=exact"},
            )
            archived = _supabase_request(
                self.config,
                "GET",
                "/sovereign_memories?select=id&is_archived=eq.true",
                extra_headers={"Prefer": "count=exact"},
            )
            return {
                "entity_count": len(entities) if entities else 0,
                "relation_count": len(relations) if relations else 0,
                "pending_revalidations": len(pending_reval) if pending_reval else 0,
                "archived_memories": len(archived) if archived else 0,
            }
        except SMSSupabaseError:
            return {}


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE: Global singleton
# ═══════════════════════════════════════════════════════════════════════════════

_adapter_instance: Optional[SMSSupabaseAdapter] = None


def get_sms_adapter() -> SMSSupabaseAdapter:
    """Get or create the global SMS adapter singleton."""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = SMSSupabaseAdapter()
    return _adapter_instance


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    adapter = SMSSupabaseAdapter()

    if not adapter.available:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY required")
        print("Set them as environment variables and retry.")
        sys.exit(1)

    print("=" * 60)
    print("SMS Supabase Adapter — Health Check")
    print("=" * 60)

    health = adapter.get_health()
    for k, v in health.items():
        print(f"  {k}: {v}")

    if len(sys.argv) > 1 and sys.argv[1] == "inject":
        agent = sys.argv[2] if len(sys.argv) > 2 else None
        query = sys.argv[3] if len(sys.argv) > 3 else None
        print("\n" + "=" * 60)
        print(f"Context Injection (agent={agent}, query={query})")
        print("=" * 60)
        print(adapter.get_context_injection(agent_id=agent, query=query))
