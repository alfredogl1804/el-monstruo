"""
SOVEREIGN MEMORY SYSTEM (SMS) — Core Engine
El sistema más poderoso del mundo de preservación de memoria,
contexto y entendimiento sostenido.

Versión: 1.0.0
Fecha: 2026-05-21
Arquitectura: 5 Capas Biológicas

Integra con stack existente del Monstruo:
- Mem0 Bridge (pgvector)
- Knowledge Graph (LightRAG)
- Error Memory
- Guardian V3 (tri-anchor)
- Context Broker
- Dory Orchestrator
- B8/B9 Classifiers
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SMS_ENABLED = os.environ.get("SMS_ENABLED", "false").lower() == "true"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
MAX_AXIOMS_INJECT = int(os.environ.get("SMS_MAX_AXIOMS_INJECT", "20"))
CRYSTALLIZATION_THRESHOLD = int(os.environ.get("SMS_CRYSTAL_THRESHOLD", "3"))
CONFIDENCE_THRESHOLD = float(os.environ.get("SMS_CONFIDENCE_THRESHOLD", "0.9"))
DECAY_RATE = float(os.environ.get("SMS_DECAY_RATE", "0.1"))


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS & DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryLayer(Enum):
    SENSORY = 1      # Buffer — TTL: 1 session
    WORKING = 2      # Active context — TTL: current session
    LONG_TERM = 3    # Episodic + Semantic + Procedural
    SOVEREIGN = 4    # Axioms — NEVER forgotten
    META = 5         # Self-knowledge — updated, never deleted


class MemoryType(Enum):
    EPISODIC = "episodic"       # Events (what happened)
    SEMANTIC = "semantic"       # Facts (what is true)
    PROCEDURAL = "procedural"   # Skills (how to do)
    CAUSAL = "causal"           # Why chains (what caused what)
    AXIOM = "axiom"             # Crystallized understanding


class ConflictResolution(Enum):
    HIGHER_CONFIDENCE = "higher_confidence"
    NEWER_TIMESTAMP = "newer_timestamp"
    T1_OVERRIDE = "t1_override"
    MERGE = "merge"
    ESCALATE = "escalate"


@dataclass
class Percept:
    """Layer 1: Raw sensory input with causal metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    content: str = ""
    source: str = "unknown"          # user, tool, agent, system
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: str = ""
    causal_parent: Optional[str] = None  # ID of percept that caused this
    confidence: float = 1.0          # tool output = 1.0, inference = variable
    ttl_hours: float = 24.0          # Time to live before consolidation or death
    processed: bool = False


@dataclass
class Memory:
    """Layer 3: Long-term memory unit."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    content: str = ""
    memory_type: MemoryType = MemoryType.SEMANTIC
    layer: MemoryLayer = MemoryLayer.LONG_TERM
    
    # Temporal
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None  # None = still valid
    
    # Strength & Relevance
    strength: float = 1.0            # Decays over time
    access_count: int = 0
    validation_count: int = 0
    contradiction_count: int = 0
    
    # Relations
    entities: List[str] = field(default_factory=list)
    causal_parents: List[str] = field(default_factory=list)
    causal_children: List[str] = field(default_factory=list)
    implications: List[str] = field(default_factory=list)
    
    # Scoping
    agent_id: str = "monstruo"
    scope: str = "org"               # agent, org, global
    
    # Embedding (for vector search)
    embedding: Optional[List[float]] = None
    
    @property
    def confidence(self) -> float:
        """Confidence based on validation vs contradiction ratio."""
        total = self.validation_count + self.contradiction_count
        if total == 0:
            return 0.5
        return self.validation_count / total
    
    @property
    def age_hours(self) -> float:
        """Hours since last access."""
        return (datetime.utcnow() - self.last_accessed).total_seconds() / 3600
    
    @property
    def relevance_score(self) -> float:
        """Ebbinghaus forgetting curve + access frequency boost."""
        base_decay = math.exp(-DECAY_RATE * self.age_hours / max(self.strength, 0.01))
        access_boost = math.log1p(self.access_count) * 0.1
        recency_boost = 1.0 if self.age_hours < 24 else 0.0
        return min(1.0, base_decay + access_boost + recency_boost)
    
    def access(self):
        """Record an access — boosts strength."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
        self.strength = min(10.0, self.strength + 0.1)
    
    def validate(self):
        """Record a validation — increases confidence."""
        self.validation_count += 1
        self.strength = min(10.0, self.strength + 0.2)
    
    def contradict(self):
        """Record a contradiction — decreases confidence."""
        self.contradiction_count += 1
        self.strength = max(0.1, self.strength - 0.3)


@dataclass
class Axiom:
    """Layer 4: Crystallized understanding — NEVER forgotten."""
    id: str = field(default_factory=lambda: f"AX-{str(uuid.uuid4())[:8]}")
    statement: str = ""
    evidence_chain: List[str] = field(default_factory=list)  # Memory IDs
    first_observed: datetime = field(default_factory=datetime.utcnow)
    last_validated: datetime = field(default_factory=datetime.utcnow)
    validation_count: int = 3        # Minimum to crystallize
    contradiction_count: int = 0
    implications: List[str] = field(default_factory=list)
    scope: str = "org"
    agent_id: str = "monstruo"
    compaction_proof: bool = True     # ALWAYS True
    
    @property
    def confidence(self) -> float:
        total = self.validation_count + self.contradiction_count
        if total == 0:
            return 0.5
        return self.validation_count / total
    
    def to_injection_line(self) -> str:
        """Ultra-compact format for context window injection."""
        conf = f"{self.confidence:.2f}"
        val = f"{self.validation_count}x"
        since = self.first_observed.strftime("%Y-%m-%d")
        return f"[{self.id}] {self.statement} (conf:{conf}, validated:{val}, since:{since})"


@dataclass
class KnowledgeGap:
    """Layer 5: Metacognitive gap detection."""
    id: str = field(default_factory=lambda: f"GAP-{str(uuid.uuid4())[:8]}")
    domain: str = ""
    detected_at: datetime = field(default_factory=datetime.utcnow)
    severity: str = "MEDIUM"         # CRITICAL, HIGH, MEDIUM, LOW
    evidence: str = ""
    resolution_strategy: str = ""    # ask_t1, research, consult_sabio, self_resolve
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class CausalChain:
    """A chain of causally linked events/facts."""
    id: str = field(default_factory=lambda: f"CC-{str(uuid.uuid4())[:8]}")
    nodes: List[str] = field(default_factory=list)  # Memory IDs in causal order
    summary: str = ""
    depth: int = 0
    root_cause: Optional[str] = None
    final_effect: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# CORE ENGINES
# ═══════════════════════════════════════════════════════════════════════════════

class PerceptionEngine:
    """Layer 1 → Layer 2: Captures inputs with temporal and causal metadata."""
    
    def __init__(self):
        self.buffer: List[Percept] = []
        self.session_id = str(uuid.uuid4())[:8]
    
    def perceive(
        self,
        content: str,
        source: str = "system",
        confidence: float = 1.0,
        causal_parent: Optional[str] = None,
    ) -> Percept:
        """Capture a new percept into the sensory buffer."""
        percept = Percept(
            content=content,
            source=source,
            timestamp=datetime.utcnow(),
            session_id=self.session_id,
            causal_parent=causal_parent,
            confidence=confidence,
        )
        self.buffer.append(percept)
        return percept
    
    def flush_expired(self) -> List[Percept]:
        """Remove percepts that have exceeded their TTL without being processed."""
        now = datetime.utcnow()
        expired = []
        alive = []
        for p in self.buffer:
            age = (now - p.timestamp).total_seconds() / 3600
            if age > p.ttl_hours and not p.processed:
                expired.append(p)
            else:
                alive.append(p)
        self.buffer = alive
        return expired
    
    def get_unprocessed(self) -> List[Percept]:
        """Get all percepts waiting to be comprehended."""
        return [p for p in self.buffer if not p.processed]


class ComprehensionEngine:
    """Layer 2 → Layer 3: Extracts relations, causes, implications."""
    
    def __init__(self):
        self.causal_chains: List[CausalChain] = []
    
    def comprehend(self, percept: Percept, existing_memories: List[Memory]) -> Memory:
        """Convert a percept into a structured memory with relations."""
        # Determine memory type based on content analysis
        memory_type = self._classify_type(percept.content)
        
        # Extract entities
        entities = self._extract_entities(percept.content)
        
        # Find causal parents in existing memories
        causal_parents = []
        if percept.causal_parent:
            causal_parents.append(percept.causal_parent)
        
        # Create memory
        memory = Memory(
            content=percept.content,
            memory_type=memory_type,
            layer=MemoryLayer.LONG_TERM,
            created_at=percept.timestamp,
            last_accessed=percept.timestamp,
            valid_from=percept.timestamp,
            strength=percept.confidence,
            entities=entities,
            causal_parents=causal_parents,
            agent_id="monstruo",
        )
        
        # Mark percept as processed
        percept.processed = True
        
        # Update causal chains
        if causal_parents:
            self._extend_causal_chain(memory, existing_memories)
        
        return memory
    
    def _classify_type(self, content: str) -> MemoryType:
        """Classify memory type based on content patterns."""
        content_lower = content.lower()
        
        # Causal indicators
        if any(w in content_lower for w in ["porque", "caused", "therefore", "por lo tanto", "implies", "implica"]):
            return MemoryType.CAUSAL
        
        # Procedural indicators
        if any(w in content_lower for w in ["how to", "cómo", "step", "paso", "process", "proceso", "run", "execute"]):
            return MemoryType.PROCEDURAL
        
        # Episodic indicators (events)
        if any(w in content_lower for w in ["happened", "pasó", "ocurrió", "yesterday", "ayer", "sprint", "session"]):
            return MemoryType.EPISODIC
        
        # Default: semantic (facts)
        return MemoryType.SEMANTIC
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract entity mentions from content."""
        entities = []
        # Pattern-based extraction for Monstruo domain
        patterns = {
            "tables": ["sovereign_axioms", "cowork_sesiones", "anti_dory", "error_memory", "knowledge_graph"],
            "agents": ["manus", "cowork", "chatgpt", "guardian", "t1", "t2"],
            "repos": ["el-monstruo", "el_monstruo"],
            "concepts": ["dory", "axiom", "crystallization", "compaction", "merge", "deploy", "rls"],
        }
        content_lower = content.lower()
        for category, terms in patterns.items():
            for term in terms:
                if term in content_lower:
                    entities.append(f"{category}:{term}")
        return entities
    
    def _extend_causal_chain(self, memory: Memory, existing: List[Memory]):
        """Extend or create causal chains."""
        for chain in self.causal_chains:
            if memory.causal_parents and any(p in chain.nodes for p in memory.causal_parents):
                chain.nodes.append(memory.id)
                chain.depth = len(chain.nodes) - 1
                chain.final_effect = memory.id
                return
        
        # Create new chain
        new_chain = CausalChain(
            nodes=memory.causal_parents + [memory.id],
            depth=len(memory.causal_parents),
            root_cause=memory.causal_parents[0] if memory.causal_parents else memory.id,
            final_effect=memory.id,
        )
        self.causal_chains.append(new_chain)


class CrystallizationEngine:
    """Layer 3 → Layer 4: Promotes validated understandings to axioms."""
    
    def __init__(self):
        self.axioms: List[Axiom] = []
        self.candidates: List[Memory] = []
    
    def evaluate_for_crystallization(self, memory: Memory) -> Optional[Axiom]:
        """Check if a memory qualifies for promotion to axiom."""
        # Criteria:
        # 1. Validated at least N times
        # 2. Confidence >= threshold
        # 3. Age >= 48h (don't crystallize fresh insights)
        # 4. Has implications
        
        age_hours = (datetime.utcnow() - memory.created_at).total_seconds() / 3600
        
        if (
            memory.validation_count >= CRYSTALLIZATION_THRESHOLD
            and memory.confidence >= CONFIDENCE_THRESHOLD
            and age_hours >= 48
            and len(memory.implications) > 0
        ):
            axiom = Axiom(
                statement=memory.content,
                evidence_chain=[memory.id] + memory.causal_parents,
                first_observed=memory.created_at,
                last_validated=memory.last_accessed,
                validation_count=memory.validation_count,
                contradiction_count=memory.contradiction_count,
                implications=memory.implications,
                scope=memory.scope,
                agent_id=memory.agent_id,
            )
            self.axioms.append(axiom)
            return axiom
        
        # Track as candidate if close
        if memory.validation_count >= 2 and memory.confidence >= 0.8:
            if memory not in self.candidates:
                self.candidates.append(memory)
        
        return None
    
    def get_injection_block(self, max_axioms: int = MAX_AXIOMS_INJECT) -> str:
        """Generate the compaction-proof injection block."""
        if not self.axioms:
            return ""
        
        # Sort by confidence * validation_count (most solid first)
        sorted_axioms = sorted(
            self.axioms,
            key=lambda a: a.confidence * a.validation_count,
            reverse=True,
        )[:max_axioms]
        
        lines = ["--- SOVEREIGN AXIOMS (compaction-proof) ---"]
        for ax in sorted_axioms:
            lines.append(ax.to_injection_line())
        lines.append("--- END SOVEREIGN AXIOMS ---")
        
        return "\n".join(lines)


class ForgettingEngine:
    """All layers: Biological decay + strategic consolidation."""
    
    def __init__(self):
        self.archived: List[Memory] = []
        self.consolidated: List[Dict] = []
    
    def apply_decay(self, memories: List[Memory]) -> Tuple[List[Memory], List[Memory]]:
        """Apply Ebbinghaus decay. Returns (alive, dead)."""
        alive = []
        dead = []
        
        for mem in memories:
            # Layer 4 (Sovereign) NEVER decays
            if mem.layer == MemoryLayer.SOVEREIGN:
                alive.append(mem)
                continue
            
            # Check relevance score
            if mem.relevance_score < 0.1:
                # Check if it's been irrelevant for 30+ days
                if mem.age_hours > 720:  # 30 days
                    dead.append(mem)
                else:
                    alive.append(mem)
            else:
                alive.append(mem)
        
        self.archived.extend(dead)
        return alive, dead
    
    def consolidate(self, memories: List[Memory]) -> List[Memory]:
        """
        REM Cycle: 7-phase background consolidation.
        1. Merge duplicates (AUDN)
        2. Promote frequent memories
        3. Degrade inactive memories
        4. Cluster related memories
        5. Generate cluster summaries
        6. Update retrieval indices
        7. Report health metrics
        """
        # Phase 1: Merge duplicates
        unique = self._merge_duplicates(memories)
        
        # Phase 2: Promote frequent (access_count > 10 → boost strength)
        for mem in unique:
            if mem.access_count > 10:
                mem.strength = min(10.0, mem.strength + 0.5)
        
        # Phase 3: Degrade inactive (no access in 7+ days)
        for mem in unique:
            if mem.age_hours > 168:  # 7 days
                mem.strength = max(0.1, mem.strength * 0.9)
        
        # Phase 4-5: Cluster (simplified — full version uses embeddings)
        # Phase 6: Indices updated implicitly
        # Phase 7: Metrics
        self.consolidated.append({
            "timestamp": datetime.utcnow().isoformat(),
            "total_memories": len(unique),
            "merged": len(memories) - len(unique),
            "avg_strength": sum(m.strength for m in unique) / max(len(unique), 1),
            "avg_relevance": sum(m.relevance_score for m in unique) / max(len(unique), 1),
        })
        
        return unique
    
    def _merge_duplicates(self, memories: List[Memory]) -> List[Memory]:
        """AUDN: Add/Update/Delete/None — resolve duplicates at write time."""
        seen_content: Dict[str, Memory] = {}
        unique = []
        
        for mem in memories:
            # Hash content for dedup
            content_hash = hashlib.md5(mem.content.lower().encode()).hexdigest()[:8]
            
            if content_hash in seen_content:
                existing = seen_content[content_hash]
                # Update: keep the one with higher confidence
                if mem.confidence > existing.confidence:
                    seen_content[content_hash] = mem
                    unique = [m for m in unique if m.id != existing.id]
                    unique.append(mem)
                else:
                    # Boost existing's validation count
                    existing.validate()
            else:
                seen_content[content_hash] = mem
                unique.append(mem)
        
        return unique


class RetrievalEngine:
    """Layer 3/4 → Layer 2: Multi-modal retrieval with fusion."""
    
    def __init__(self):
        self.last_retrieval_stats: Dict[str, Any] = {}
    
    def retrieve(
        self,
        query: str,
        memories: List[Memory],
        axioms: List[Axiom],
        mode: str = "all",  # semantic, temporal, causal, entity, all
        max_results: int = 10,
        time_window_days: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Multi-modal retrieval with Reciprocal Rank Fusion.
        Returns memories ranked by combined relevance.
        """
        results = {}
        
        if mode in ("semantic", "all"):
            semantic = self._semantic_search(query, memories)
            for i, (mem, score) in enumerate(semantic):
                results.setdefault(mem.id, {"memory": mem, "scores": {}})
                results[mem.id]["scores"]["semantic"] = score
        
        if mode in ("temporal", "all"):
            temporal = self._temporal_search(query, memories, time_window_days)
            for i, (mem, score) in enumerate(temporal):
                results.setdefault(mem.id, {"memory": mem, "scores": {}})
                results[mem.id]["scores"]["temporal"] = score
        
        if mode in ("causal", "all"):
            causal = self._causal_search(query, memories)
            for i, (mem, score) in enumerate(causal):
                results.setdefault(mem.id, {"memory": mem, "scores": {}})
                results[mem.id]["scores"]["causal"] = score
        
        if mode in ("entity", "all"):
            entity = self._entity_search(query, memories)
            for i, (mem, score) in enumerate(entity):
                results.setdefault(mem.id, {"memory": mem, "scores": {}})
                results[mem.id]["scores"]["entity"] = score
        
        # Reciprocal Rank Fusion
        fused = []
        for mem_id, data in results.items():
            rrf_score = sum(
                1.0 / (60 + rank)  # k=60 standard RRF constant
                for rank, score in enumerate(sorted(data["scores"].values(), reverse=True))
            )
            # Multiply by relevance score (forgetting curve)
            rrf_score *= data["memory"].relevance_score
            fused.append({"memory": data["memory"], "rrf_score": rrf_score, "modes": data["scores"]})
        
        # Sort by RRF score
        fused.sort(key=lambda x: x["rrf_score"], reverse=True)
        
        # Axioms always on top (compaction-proof)
        axiom_results = [{"axiom": ax, "rrf_score": 999.0} for ax in axioms if query.lower() in ax.statement.lower()]
        
        self.last_retrieval_stats = {
            "query": query,
            "candidates": len(results),
            "returned": min(max_results, len(fused)),
            "modes_used": mode,
        }
        
        final = axiom_results + fused[:max_results]
        return final
    
    def _semantic_search(self, query: str, memories: List[Memory]) -> List[Tuple[Memory, float]]:
        """Keyword-based semantic search (full version uses embeddings)."""
        query_words = set(query.lower().split())
        scored = []
        for mem in memories:
            content_words = set(mem.content.lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                score = overlap / max(len(query_words), 1)
                scored.append((mem, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:20]
    
    def _temporal_search(self, query: str, memories: List[Memory], window_days: Optional[int]) -> List[Tuple[Memory, float]]:
        """Search by temporal proximity."""
        now = datetime.utcnow()
        window = timedelta(days=window_days or 7)
        scored = []
        for mem in memories:
            if mem.valid_from and (now - mem.valid_from) <= window:
                # More recent = higher score
                age_factor = 1.0 - ((now - mem.valid_from).total_seconds() / window.total_seconds())
                scored.append((mem, max(0, age_factor)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:20]
    
    def _causal_search(self, query: str, memories: List[Memory]) -> List[Tuple[Memory, float]]:
        """Search by causal connections."""
        # Find memories that are causally connected to query-matching memories
        query_words = set(query.lower().split())
        root_matches = [m for m in memories if len(set(m.content.lower().split()) & query_words) > 0]
        
        causal_related = []
        root_ids = {m.id for m in root_matches}
        
        for mem in memories:
            if any(p in root_ids for p in mem.causal_parents):
                causal_related.append((mem, 0.8))
            elif mem.id in root_ids:
                causal_related.append((mem, 1.0))
        
        return causal_related[:20]
    
    def _entity_search(self, query: str, memories: List[Memory]) -> List[Tuple[Memory, float]]:
        """Search by entity overlap."""
        query_lower = query.lower()
        scored = []
        for mem in memories:
            entity_match = sum(1 for e in mem.entities if e.split(":")[-1] in query_lower)
            if entity_match > 0:
                scored.append((mem, entity_match / max(len(mem.entities), 1)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:20]


class MetacognitionEngine:
    """Layer 5: Self-reflective gap detection and confidence calibration."""
    
    def __init__(self):
        self.gaps: List[KnowledgeGap] = []
        self.confidence_history: List[Dict] = []
    
    def detect_gaps(self, query: str, retrieval_results: List[Dict]) -> Optional[KnowledgeGap]:
        """Detect if the agent lacks knowledge to answer a query."""
        # Gap indicators:
        # 1. No retrieval results
        # 2. All results have low relevance
        # 3. Results are contradictory
        
        if not retrieval_results:
            gap = KnowledgeGap(
                domain=query,
                severity="HIGH",
                evidence="No memories found for this query",
                resolution_strategy="research",
            )
            self.gaps.append(gap)
            return gap
        
        # Check average confidence
        scores = [r.get("rrf_score", 0) for r in retrieval_results if "rrf_score" in r]
        if scores and max(scores) < 0.3:
            gap = KnowledgeGap(
                domain=query,
                severity="MEDIUM",
                evidence=f"Best retrieval score is only {max(scores):.2f}",
                resolution_strategy="consult_sabio",
            )
            self.gaps.append(gap)
            return gap
        
        return None
    
    def calibrate_confidence(self, axioms: List[Axiom]) -> List[Dict]:
        """Periodic confidence calibration — decay unvalidated axioms."""
        now = datetime.utcnow()
        alerts = []
        
        for axiom in axioms:
            days_since_validation = (now - axiom.last_validated).total_seconds() / 86400
            
            if days_since_validation > 30 and axiom.confidence < 0.95:
                alerts.append({
                    "axiom_id": axiom.id,
                    "statement": axiom.statement,
                    "days_stale": int(days_since_validation),
                    "confidence": axiom.confidence,
                    "action": "needs_revalidation",
                })
        
        self.confidence_history.append({
            "timestamp": now.isoformat(),
            "total_axioms": len(axioms),
            "stale_axioms": len(alerts),
        })
        
        return alerts
    
    def pre_action_check(self, action_description: str, axioms: List[Axiom]) -> Dict[str, Any]:
        """Pre-action metacognitive check: do I have enough context?"""
        # Check if any axiom contradicts the proposed action
        contradictions = []
        for axiom in axioms:
            # Simple keyword overlap check (full version uses semantic similarity)
            if any(word in action_description.lower() for word in axiom.statement.lower().split()[:5]):
                contradictions.append(axiom)
        
        return {
            "has_sufficient_context": len(contradictions) == 0 or all(
                "proceed" in c.statement.lower() or "allow" in c.statement.lower()
                for c in contradictions
            ),
            "relevant_axioms": [a.to_injection_line() for a in contradictions],
            "gaps_detected": len(self.gaps),
            "unresolved_gaps": len([g for g in self.gaps if not g.resolved]),
        }


class ConflictResolver:
    """Cross-agent conflict resolution protocol."""
    
    def resolve(
        self,
        fact_a: Memory,
        fact_b: Memory,
        strategy: ConflictResolution = ConflictResolution.HIGHER_CONFIDENCE,
    ) -> Tuple[Memory, str]:
        """Resolve a conflict between two memories from different agents."""
        
        if strategy == ConflictResolution.T1_OVERRIDE:
            # T1 always wins
            winner = fact_a if fact_a.agent_id == "t1" else fact_b
            return winner, "T1 override applied"
        
        if strategy == ConflictResolution.HIGHER_CONFIDENCE:
            if fact_a.confidence > fact_b.confidence:
                fact_b.contradict()
                return fact_a, f"Higher confidence: {fact_a.confidence:.2f} > {fact_b.confidence:.2f}"
            elif fact_b.confidence > fact_a.confidence:
                fact_a.contradict()
                return fact_b, f"Higher confidence: {fact_b.confidence:.2f} > {fact_a.confidence:.2f}"
            else:
                # Equal confidence — escalate
                return fact_a, "ESCALATE: Equal confidence, needs T1 decision"
        
        if strategy == ConflictResolution.NEWER_TIMESTAMP:
            if fact_a.created_at > fact_b.created_at:
                fact_b.valid_until = fact_a.created_at
                return fact_a, "Newer timestamp wins, older marked invalid"
            else:
                fact_a.valid_until = fact_b.created_at
                return fact_b, "Newer timestamp wins, older marked invalid"
        
        if strategy == ConflictResolution.MERGE:
            merged = Memory(
                content=f"{fact_a.content} | ALSO: {fact_b.content}",
                memory_type=fact_a.memory_type,
                entities=list(set(fact_a.entities + fact_b.entities)),
                validation_count=fact_a.validation_count + fact_b.validation_count,
                strength=max(fact_a.strength, fact_b.strength),
            )
            return merged, "Merged complementary facts"
        
        return fact_a, "ESCALATE: No resolution strategy matched"


# ═══════════════════════════════════════════════════════════════════════════════
# SOVEREIGN MEMORY SYSTEM — UNIFIED ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class SovereignMemorySystem:
    """
    The unified orchestrator that connects all engines into a single
    cognitive system for memory preservation, context, and understanding.
    """
    
    def __init__(self):
        self.perception = PerceptionEngine()
        self.comprehension = ComprehensionEngine()
        self.crystallization = CrystallizationEngine()
        self.forgetting = ForgettingEngine()
        self.retrieval = RetrievalEngine()
        self.metacognition = MetacognitionEngine()
        self.conflict_resolver = ConflictResolver()
        
        # Memory stores
        self.memories: List[Memory] = []
        self.axioms: List[Axiom] = []
        
        # Metrics
        self.stats = {
            "percepts_processed": 0,
            "memories_created": 0,
            "axioms_crystallized": 0,
            "memories_forgotten": 0,
            "conflicts_resolved": 0,
            "gaps_detected": 0,
        }
    
    def ingest(
        self,
        content: str,
        source: str = "system",
        confidence: float = 1.0,
        causal_parent: Optional[str] = None,
    ) -> Memory:
        """Full pipeline: Perceive → Comprehend → Store."""
        # Step 1: Perceive
        percept = self.perception.perceive(content, source, confidence, causal_parent)
        
        # Step 2: Comprehend
        memory = self.comprehension.comprehend(percept, self.memories)
        
        # Step 3: Check for duplicates (AUDN)
        existing_match = self._find_duplicate(memory)
        if existing_match:
            existing_match.validate()
            self.stats["percepts_processed"] += 1
            return existing_match
        
        # Step 4: Store
        self.memories.append(memory)
        self.stats["percepts_processed"] += 1
        self.stats["memories_created"] += 1
        
        # Step 5: Check crystallization candidacy
        self._check_crystallization(memory)
        
        return memory
    
    def recall(
        self,
        query: str,
        mode: str = "all",
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """Full retrieval pipeline with metacognitive check."""
        # Step 1: Retrieve
        results = self.retrieval.retrieve(query, self.memories, self.axioms, mode, max_results)
        
        # Step 2: Metacognitive gap check
        gap = self.metacognition.detect_gaps(query, results)
        if gap:
            self.stats["gaps_detected"] += 1
        
        # Step 3: Access boost for retrieved memories
        for r in results:
            if "memory" in r:
                r["memory"].access()
        
        return {
            "results": results,
            "gap_detected": gap is not None,
            "gap": gap,
            "stats": self.retrieval.last_retrieval_stats,
        }
    
    def get_context_injection(self) -> str:
        """Generate the full context injection block for the agent."""
        parts = []
        
        # Axioms (compaction-proof)
        axiom_block = self.crystallization.get_injection_block()
        if axiom_block:
            parts.append(axiom_block)
        
        # Unresolved gaps
        unresolved = [g for g in self.metacognition.gaps if not g.resolved]
        if unresolved:
            parts.append("--- KNOWLEDGE GAPS (unresolved) ---")
            for gap in unresolved[:5]:
                parts.append(f"[{gap.id}] {gap.domain} (severity:{gap.severity}, strategy:{gap.resolution_strategy})")
            parts.append("--- END GAPS ---")
        
        # Causal chains (top 3 most relevant)
        if self.comprehension.causal_chains:
            parts.append("--- ACTIVE CAUSAL CHAINS ---")
            for chain in self.comprehension.causal_chains[-3:]:
                parts.append(f"[{chain.id}] depth:{chain.depth} | {chain.summary or 'chain of ' + str(len(chain.nodes)) + ' events'}")
            parts.append("--- END CHAINS ---")
        
        return "\n".join(parts)
    
    def run_consolidation(self) -> Dict[str, Any]:
        """Run the full REM cycle consolidation."""
        # Apply decay
        alive, dead = self.forgetting.apply_decay(self.memories)
        self.memories = alive
        self.stats["memories_forgotten"] += len(dead)
        
        # Consolidate
        self.memories = self.forgetting.consolidate(self.memories)
        
        # Calibrate axiom confidence
        stale_alerts = self.metacognition.calibrate_confidence(self.axioms)
        
        # Check crystallization for all candidates
        for candidate in self.crystallization.candidates[:]:
            axiom = self.crystallization.evaluate_for_crystallization(candidate)
            if axiom:
                self.axioms.append(axiom)
                self.crystallization.candidates.remove(candidate)
                self.stats["axioms_crystallized"] += 1
        
        return {
            "memories_alive": len(self.memories),
            "memories_forgotten": len(dead),
            "axioms_total": len(self.axioms),
            "stale_axioms": len(stale_alerts),
            "consolidation_report": self.forgetting.consolidated[-1] if self.forgetting.consolidated else {},
        }
    
    def resolve_conflict(self, memory_a: Memory, memory_b: Memory) -> Dict[str, Any]:
        """Resolve a cross-agent conflict."""
        # Determine strategy
        if memory_a.agent_id == "t1" or memory_b.agent_id == "t1":
            strategy = ConflictResolution.T1_OVERRIDE
        elif abs(memory_a.confidence - memory_b.confidence) > 0.2:
            strategy = ConflictResolution.HIGHER_CONFIDENCE
        else:
            strategy = ConflictResolution.ESCALATE
        
        winner, reason = self.conflict_resolver.resolve(memory_a, memory_b, strategy)
        self.stats["conflicts_resolved"] += 1
        
        return {
            "winner": winner.id,
            "reason": reason,
            "strategy": strategy.value,
        }
    
    def pre_action_gate(self, action_description: str) -> Dict[str, Any]:
        """Pre-action check: should this action proceed?"""
        meta_check = self.metacognition.pre_action_check(action_description, self.axioms)
        return meta_check
    
    def get_health_report(self) -> Dict[str, Any]:
        """Full system health report."""
        return {
            "stats": self.stats,
            "memory_count": len(self.memories),
            "axiom_count": len(self.axioms),
            "gap_count": len(self.metacognition.gaps),
            "unresolved_gaps": len([g for g in self.metacognition.gaps if not g.resolved]),
            "causal_chains": len(self.comprehension.causal_chains),
            "avg_memory_strength": sum(m.strength for m in self.memories) / max(len(self.memories), 1),
            "avg_memory_relevance": sum(m.relevance_score for m in self.memories) / max(len(self.memories), 1),
            "buffer_size": len(self.perception.buffer),
            "crystallization_candidates": len(self.crystallization.candidates),
        }
    
    def _find_duplicate(self, memory: Memory) -> Optional[Memory]:
        """Check if a memory already exists (AUDN: Update instead of Add)."""
        content_hash = hashlib.md5(memory.content.lower().encode()).hexdigest()[:8]
        for existing in self.memories:
            existing_hash = hashlib.md5(existing.content.lower().encode()).hexdigest()[:8]
            if content_hash == existing_hash:
                return existing
        return None
    
    def _check_crystallization(self, memory: Memory):
        """Check if memory should be tracked for crystallization."""
        if memory.validation_count >= 2 and memory.confidence >= 0.8:
            if memory not in self.crystallization.candidates:
                self.crystallization.candidates.append(memory)
    
    def validate_memory(self, memory_id: str) -> Optional[Memory]:
        """Validate a memory externally (e.g., T1 confirms it). Tracks for crystallization."""
        for mem in self.memories:
            if mem.id == memory_id:
                mem.validate()
                self._check_crystallization(mem)
                return mem
        return None
    
    def add_implication(self, memory_id: str, implication: str) -> bool:
        """Add an implication to a memory (required for crystallization)."""
        for mem in self.memories:
            if mem.id == memory_id:
                mem.implications.append(implication)
                return True
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# STANDALONE DEMO
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("SOVEREIGN MEMORY SYSTEM — Demo")
    print("=" * 70)
    
    sms = SovereignMemorySystem()
    
    # Simulate a session with the Monstruo
    print("\n[1] Ingesting memories...")
    
    m1 = sms.ingest(
        "T1 blocked merge to main because B8 classifier had no red-team validation",
        source="user",
        confidence=1.0,
    )
    
    m2 = sms.ingest(
        "Grok 4 Heavy found 3 evasion vectors: fragmentation, semantic inversion, encoding",
        source="tool",
        confidence=0.95,
        causal_parent=m1.id,
    )
    
    m3 = sms.ingest(
        "Layer 6 was implemented to cover the 3 evasion vectors",
        source="agent",
        confidence=1.0,
        causal_parent=m2.id,
    )
    
    m4 = sms.ingest(
        "GPT-5.5 Pro identified CONSTRUCT_MISMATCH: B8 measures classification, not retention",
        source="tool",
        confidence=0.98,
        causal_parent=m3.id,
    )
    
    m5 = sms.ingest(
        "RLS is mandatory for all new tables in Supabase — DSC-S-006",
        source="system",
        confidence=1.0,
    )
    # Validate m5 multiple times to test crystallization
    for _ in range(5):
        sms.validate_memory(m5.id)
    sms.add_implication(m5.id, "Any CREATE TABLE must include ENABLE ROW LEVEL SECURITY")
    # Force age for crystallization test
    m5.created_at = datetime.utcnow() - timedelta(hours=72)
    
    print(f"  Memories created: {sms.stats['memories_created']}")
    print(f"  Causal chains: {len(sms.comprehension.causal_chains)}")
    
    # Test retrieval
    print("\n[2] Retrieving memories...")
    result = sms.recall("Why was merge blocked?")
    print(f"  Results: {len(result['results'])}")
    print(f"  Gap detected: {result['gap_detected']}")
    for r in result["results"][:3]:
        if "memory" in r:
            print(f"    - [{r['rrf_score']:.3f}] {r['memory'].content[:60]}...")
    
    # Test crystallization
    print("\n[3] Running consolidation + crystallization...")
    report = sms.run_consolidation()
    print(f"  Memories alive: {report['memories_alive']}")
    print(f"  Axioms crystallized: {report['axioms_total']}")
    
    # Check if RLS axiom was crystallized
    if sms.axioms:
        print(f"\n[4] Sovereign Axioms:")
        for ax in sms.axioms:
            print(f"    {ax.to_injection_line()}")
    
    # Test context injection
    print("\n[5] Context injection block:")
    injection = sms.get_context_injection()
    if injection:
        print(injection)
    else:
        print("  (No injection needed — all clear)")
    
    # Test pre-action gate
    print("\n[6] Pre-action gate test:")
    gate = sms.pre_action_gate("merge feature branch to main without review")
    print(f"  Sufficient context: {gate['has_sufficient_context']}")
    print(f"  Relevant axioms: {len(gate['relevant_axioms'])}")
    
    # Health report
    print("\n[7] Health Report:")
    health = sms.get_health_report()
    for k, v in health.items():
        print(f"  {k}: {v}")
    
    print("\n" + "=" * 70)
    print("SOVEREIGN MEMORY SYSTEM — Demo Complete")
    print("=" * 70)
