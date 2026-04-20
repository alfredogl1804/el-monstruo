"""
El Monstruo — Memory Module
==============================
Sovereign memory system: event store, conversation memory,
knowledge graph, and checkpoint persistence.

All data is owned. No external framework is source of truth.
"""

from memory.checkpoint_store import SovereignCheckpointStore
from memory.conversation import ConversationMemory
from memory.event_store import EventStore
from memory.knowledge_graph import KnowledgeGraph
from memory.supabase_client import SupabaseClient

__all__ = [
    "EventStore",
    "SupabaseClient",
    "ConversationMemory",
    "SovereignCheckpointStore",
    "KnowledgeGraph",
]
