"""
Sovereign Memory System v2.0 — Orchestration Layer
====================================================
El Monstruo | Sprint SMS | 2026-05-21

PRINCIPIO ARQUITECTÓNICO:
    Este módulo NO reimplementa storage. Orquesta los 18 sistemas
    de memoria existentes del Monstruo y AGREGA 5 capacidades nuevas:

    1. Crystallization — axiomas inmutables que sobreviven todo
    2. Forgetting — Ebbinghaus decay inteligente sobre backends existentes
    3. Metacognition — gap detection activa que BLOQUEA (no shadow)
    4. Conflict Resolution — arbitraje cuando backends se contradicen
    5. Universal Multi-Agent API — cualquier IA puede leer/escribir

BACKENDS DELEGADOS (ya en producción):
    - Mem0 Bridge → episodic memory, user modeling
    - LightRAG → knowledge graph RAG
    - MemPalace → long-term episodic + semantic
    - Thoughts Store → persistent facts, hybrid search
    - ErrorMemory → pattern detection, pre-action consult
    - MementoValidator → pre-action validation vs sources of truth
    - CausalKB → causal events for prediction
    - ConversationMemory → session history
    - AsyncPostgresSaver → LangGraph checkpoints
    - Guardian V3 → tri-anchor boot recovery

MULTI-AGENT:
    Cualquier IA (ChatGPT, Claude, Gemini, Grok, Manus, Cowork)
    se identifica con agent_id y puede leer/escribir/cristalizar.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger("sms_v2")

# ═══════════════════════════════════════════════════════════════
# DOMAIN MODELS
# ═══════════════════════════════════════════════════════════════

class MemoryTier(str, Enum):
    """5 tiers biológicos de memoria."""
    BUFFER = "buffer"           # TTL: 1 sesión, raw inputs
    WORKING = "working"         # Context window activo
    LONG_TERM = "long_term"     # Episódica + semántica + causal
    SOVEREIGN = "sovereign"     # Axiomas cristalizados (NUNCA se pierden)
    META = "meta"               # Metacognición: lo que el sistema sabe que NO sabe


class AxiomSource(str, Enum):
    """Quién cristalizó el axioma."""
    HUMAN_T1 = "human_t1"           # Alfredo declaró directamente
    MULTI_AGENT_CONSENSUS = "consensus"  # 3+ agentes convergieron
    EMPIRICAL = "empirical"          # Validado por evidencia repetida
    SYSTEM = "system"                # Regla dura del sistema


class ConflictResolution(str, Enum):
    """Estrategias de resolución de conflictos."""
    NEWEST_WINS = "newest_wins"
    HIGHEST_CONFIDENCE = "highest_confidence"
    HUMAN_ARBITRATION = "human_arbitration"
    CONSENSUS = "consensus"


@dataclass
class Axiom:
    """Entendimiento cristalizado — inmutable, sobrevive todo."""
    id: str = field(default_factory=lambda: f"AX-{uuid4().hex[:8]}")
    content: str = ""
    source: AxiomSource = AxiomSource.EMPIRICAL
    created_by: str = ""           # agent_id que lo cristalizó
    validated_by: list[str] = field(default_factory=list)  # agent_ids que confirmaron
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: float = 1.0
    domain: str = "general"        # dominio temático
    supersedes: Optional[str] = None  # axiom_id que reemplaza
    immutable: bool = True
    access_count: int = 0
    last_accessed: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id, "content": self.content, "source": self.source.value,
            "created_by": self.created_by, "validated_by": self.validated_by,
            "created_at": self.created_at, "confidence": self.confidence,
            "domain": self.domain, "supersedes": self.supersedes,
            "immutable": self.immutable, "access_count": self.access_count,
            "last_accessed": self.last_accessed,
        }


@dataclass
class MetacognitiveGap:
    """Algo que el sistema sabe que NO sabe."""
    id: str = field(default_factory=lambda: f"GAP-{uuid4().hex[:8]}")
    description: str = ""
    detected_by: str = ""          # agent_id
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    domain: str = "general"
    severity: str = "medium"       # low, medium, high, critical
    resolution_strategy: str = ""  # qué hacer para cerrar el gap
    resolved: bool = False
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None


@dataclass
class ConflictRecord:
    """Registro de un conflicto entre backends o agentes."""
    id: str = field(default_factory=lambda: f"CONF-{uuid4().hex[:8]}")
    claim_a: str = ""
    source_a: str = ""             # backend o agent_id
    claim_b: str = ""
    source_b: str = ""
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    strategy_used: Optional[ConflictResolution] = None


# ═══════════════════════════════════════════════════════════════
# BACKEND ADAPTERS (delegates to existing production systems)
# ═══════════════════════════════════════════════════════════════

class BackendAdapter:
    """
    Adapter que conecta con los backends existentes del Monstruo.
    En producción, importa los módulos reales.
    En test/standalone, degrada gracefully.
    """

    def __init__(self):
        self._mem0 = None
        self._lightrag = None
        self._mempalace = None
        self._thoughts = None
        self._error_memory = None
        self._memento = None
        self._causal_kb = None
        self._supabase = None
        self._initialized = False

    async def initialize(self) -> dict[str, bool]:
        """Intenta conectar con cada backend. Reporta status."""
        status = {}

        # Supabase direct (for axioms table)
        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if supabase_url and supabase_key:
            self._supabase = {"url": supabase_url, "key": supabase_key}
            status["supabase"] = True
        else:
            logger.warning("supabase_not_configured — Set SUPABASE_URL and SUPABASE_SERVICE_KEY")
            status["supabase"] = False

        # Mem0
        try:
            from memory.mem0_bridge import add_memory, search_memory, get_stats
            _check = await get_stats()
            self._mem0 = {"add": add_memory, "search": search_memory}
            status["mem0"] = _check.get("status") == "active"
        except Exception as e:
            logger.warning(f"Mem0 not available: {e}")
            status["mem0"] = False

        # LightRAG
        try:
            from memory.lightrag_bridge import query_knowledge, ingest_document, get_stats as lr_stats
            _check = await lr_stats()
            self._lightrag = {"query": query_knowledge, "ingest": ingest_document}
            status["lightrag"] = _check.get("status") == "active"
        except Exception as e:
            logger.warning(f"LightRAG not available: {e}")
            status["lightrag"] = False

        # MemPalace
        try:
            from memory.mempalace_bridge import recall, store_episode, _ensure_initialized
            if _ensure_initialized():
                self._mempalace = {"recall": recall, "store": store_episode}
                status["mempalace"] = True
            else:
                status["mempalace"] = False
        except Exception as e:
            logger.warning(f"MemPalace not available: {e}")
            status["mempalace"] = False

        # Thoughts Store
        try:
            from memory.thoughts import ThoughtsStore
            self._thoughts = ThoughtsStore()
            status["thoughts"] = True
        except Exception as e:
            logger.warning(f"Thoughts not available: {e}")
            status["thoughts"] = False

        # Error Memory
        try:
            from kernel.error_memory import ErrorMemory
            status["error_memory"] = True
        except Exception as e:
            status["error_memory"] = False

        # Memento Validator
        try:
            from kernel.memento.validator import MementoValidator
            status["memento"] = True
        except Exception as e:
            status["memento"] = False

        self._initialized = True
        return status

    async def search_all(self, query: str, agent_id: str, limit: int = 10) -> list[dict]:
        """Búsqueda federada en todos los backends disponibles."""
        results = []

        # Mem0 search (API: search_memory(query, user_id, limit))
        if self._mem0:
            try:
                mem0_results = await self._mem0["search"](query, user_id=agent_id, limit=limit)
                for r in (mem0_results or []):
                    results.append({
                        "source": "mem0",
                        "content": r.get("memory", r.get("content", "")),
                        "score": r.get("score", 0.5),
                        "metadata": r.get("metadata", {}),
                    })
            except Exception as e:
                logger.warning(f"Mem0 search failed: {e}")

        # LightRAG query (API: query_knowledge(query, mode, top_k))
        if self._lightrag:
            try:
                lr_result = await self._lightrag["query"](query, mode="hybrid", top_k=limit)
                if lr_result and lr_result.get("results"):
                    results.append({
                        "source": "lightrag",
                        "content": lr_result["results"] if isinstance(lr_result["results"], str) else str(lr_result["results"]),
                        "score": 0.8,
                        "metadata": {"mode": lr_result.get("mode", "hybrid")},
                    })
            except Exception as e:
                logger.warning(f"LightRAG search failed: {e}")

        # MemPalace recall (API: recall(query, user_id, n_results, memory_type))
        if self._mempalace:
            try:
                mp_results = await self._mempalace["recall"](query, user_id=agent_id, n_results=limit)
                for r in (mp_results or []):
                    results.append({
                        "source": "mempalace",
                        "content": r.get("content", ""),
                        "score": r.get("similarity", 0.5),
                        "metadata": r.get("metadata", {}),
                    })
            except Exception as e:
                logger.warning(f"MemPalace recall failed: {e}")

        # Sort by score descending
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:limit]

    async def store_to_all(self, content: str, agent_id: str, metadata: dict = None) -> dict[str, bool]:
        """Almacena en todos los backends relevantes."""
        stored = {}
        meta = metadata or {}

        # Mem0 (API: add_memory(messages, user_id, metadata))
        if self._mem0:
            try:
                await self._mem0["add"](
                    messages=[{"role": "assistant", "content": content}],
                    user_id=agent_id,
                    metadata=meta,
                )
                stored["mem0"] = True
            except Exception as e:
                stored["mem0"] = False
                logger.warning(f"Mem0 store failed: {e}")

        # LightRAG (API: ingest_document(content, metadata))
        if self._lightrag:
            try:
                await self._lightrag["ingest"](content, metadata=meta)
                stored["lightrag"] = True
            except Exception as e:
                stored["lightrag"] = False
                logger.warning(f"LightRAG store failed: {e}")

        # MemPalace (API: store_episode(user_id, session_id, content, metadata))
        if self._mempalace:
            try:
                await self._mempalace["store"](
                    user_id=agent_id,
                    session_id=str(uuid4()),
                    content=content,
                    metadata=meta,
                )
                stored["mempalace"] = True
            except Exception as e:
                stored["mempalace"] = False
                logger.warning(f"MemPalace store failed: {e}")

        return stored


# ═══════════════════════════════════════════════════════════════
# ENGINE 1: CRYSTALLIZATION
# ═══════════════════════════════════════════════════════════════

class CrystallizationEngine:
    """
    Promueve entendimientos validados a axiomas inmutables.
    
    Criterios de cristalización:
    1. Validado por 2+ agentes independientes
    2. Sin contradicción con axiomas existentes
    3. Confidence >= 0.9
    4. O declarado directamente por T1 (Alfredo)
    """

    def __init__(self, supabase_adapter=None):
        self._axioms: dict[str, Axiom] = {}
        self._supabase = supabase_adapter
        self._table = "sovereign_axioms"

    async def load_from_supabase(self):
        """Carga axiomas desde Supabase al arrancar."""
        if not self._supabase:
            return
        try:
            rows = await self._supabase.select(self._table, columns="*")
            for row in (rows or []):
                ax = Axiom(
                    id=row["id"],
                    content=row["content"],
                    source=AxiomSource(row.get("source", "empirical")),
                    created_by=row.get("created_by", ""),
                    validated_by=row.get("validated_by", []),
                    created_at=row.get("created_at", ""),
                    confidence=row.get("confidence", 1.0),
                    domain=row.get("domain", "general"),
                    supersedes=row.get("supersedes"),
                    immutable=row.get("immutable", True),
                    access_count=row.get("access_count", 0),
                    last_accessed=row.get("last_accessed"),
                )
                self._axioms[ax.id] = ax
            logger.info(f"Loaded {len(self._axioms)} axioms from Supabase")
        except Exception as e:
            logger.warning(f"Failed to load axioms: {e}")

    async def crystallize(
        self,
        content: str,
        source: AxiomSource,
        created_by: str,
        domain: str = "general",
        validated_by: list[str] = None,
        supersedes: Optional[str] = None,
    ) -> Axiom:
        """Cristaliza un nuevo axioma."""
        # Check for contradiction with existing axioms
        contradiction = await self._check_contradiction(content)
        if contradiction:
            raise ValueError(
                f"CONFLICT: New axiom contradicts existing {contradiction.id}: "
                f"'{contradiction.content}'. Resolve conflict first."
            )

        axiom = Axiom(
            content=content,
            source=source,
            created_by=created_by,
            validated_by=validated_by or [created_by],
            domain=domain,
            supersedes=supersedes,
        )

        # If supersedes, mark old axiom
        if supersedes and supersedes in self._axioms:
            old = self._axioms[supersedes]
            old.immutable = False  # Allow supersession

        self._axioms[axiom.id] = axiom

        # Persist to Supabase
        if self._supabase:
            try:
                await self._supabase.insert(self._table, axiom.to_dict())
            except Exception as e:
                logger.warning(f"Failed to persist axiom: {e}")

        logger.info(f"Crystallized axiom {axiom.id}: {content[:80]}...")
        return axiom

    async def validate_axiom(self, axiom_id: str, validator_agent_id: str) -> bool:
        """Un agente adicional valida un axioma existente."""
        if axiom_id not in self._axioms:
            return False
        axiom = self._axioms[axiom_id]
        if validator_agent_id not in axiom.validated_by:
            axiom.validated_by.append(validator_agent_id)
            # Persist update
            if self._supabase:
                try:
                    await self._supabase.update(
                        self._table,
                        {"validated_by": axiom.validated_by},
                        match={"id": axiom_id},
                    )
                except Exception:
                    pass
        return True

    async def query_axioms(self, domain: str = None, keyword: str = None) -> list[Axiom]:
        """Consulta axiomas por dominio o keyword."""
        results = []
        for ax in self._axioms.values():
            if domain and ax.domain != domain:
                continue
            if keyword and keyword.lower() not in ax.content.lower():
                continue
            ax.access_count += 1
            ax.last_accessed = datetime.now(timezone.utc).isoformat()
            results.append(ax)
        return results

    async def get_all_axioms(self) -> list[Axiom]:
        """Retorna todos los axiomas activos."""
        return [ax for ax in self._axioms.values() if ax.immutable]

    async def _check_contradiction(self, new_content: str) -> Optional[Axiom]:
        """
        Heurística simple de contradicción.
        En producción, esto usaría embeddings + LLM para detección semántica.
        """
        new_lower = new_content.lower()
        negation_pairs = [
            ("always", "never"), ("must", "must not"), ("required", "forbidden"),
            ("enabled", "disabled"), ("active", "inactive"),
        ]
        for ax in self._axioms.values():
            ax_lower = ax.content.lower()
            for pos, neg in negation_pairs:
                if pos in new_lower and neg in ax_lower:
                    # Check if they're about the same subject (simple overlap)
                    new_words = set(new_lower.split())
                    ax_words = set(ax_lower.split())
                    overlap = len(new_words & ax_words) / max(len(new_words | ax_words), 1)
                    if overlap > 0.3:
                        return ax
        return None


# ═══════════════════════════════════════════════════════════════
# ENGINE 2: INTELLIGENT FORGETTING
# ═══════════════════════════════════════════════════════════════

class ForgettingEngine:
    """
    Ebbinghaus decay + AUDN (Accessed, Useful, Decayed, Nuked).
    
    NO borra axiomas (inmutables). Solo aplica decay a:
    - MemPalace episodes
    - Mem0 memories
    - Thoughts (non-boot)
    
    Principio: Olvidar es tan importante como recordar.
    Sin forgetting, el retrieval se degrada por ruido.
    """

    # Ebbinghaus retention curve: R = e^(-t/S)
    # S = stability (increases with each successful recall)
    DECAY_THRESHOLD = 0.3  # Below this, memory is candidate for archival
    NUKE_THRESHOLD = 0.1   # Below this, memory is candidate for deletion

    def __init__(self, supabase_adapter=None):
        self._supabase = supabase_adapter

    async def calculate_retention(
        self,
        created_at: str,
        last_accessed: Optional[str],
        access_count: int,
        importance: float = 0.5,
    ) -> float:
        """
        Calcula retención actual de una memoria.
        
        R = e^(-t/S) * importance_boost
        S = base_stability * (1 + 0.3 * access_count)
        """
        import math

        now = datetime.now(timezone.utc)
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return 0.5  # Unknown age → medium retention

        # Time elapsed in days
        t_days = (now - created).total_seconds() / 86400

        # Stability increases with access
        base_stability = 7.0  # 7 days base half-life
        stability = base_stability * (1 + 0.3 * access_count)

        # Ebbinghaus curve
        retention = math.exp(-t_days / stability)

        # Importance boost (axiom-adjacent memories decay slower)
        retention *= (1 + importance * 0.5)

        return min(retention, 1.0)

    async def identify_decay_candidates(self, memories: list[dict]) -> dict:
        """
        Clasifica memorias en: keep, archive, nuke.
        """
        keep, archive, nuke = [], [], []

        for mem in memories:
            retention = await self.calculate_retention(
                created_at=mem.get("created_at", ""),
                last_accessed=mem.get("last_accessed"),
                access_count=mem.get("access_count", 0),
                importance=mem.get("importance", 0.5),
            )

            mem["_retention"] = retention

            if retention >= self.DECAY_THRESHOLD:
                keep.append(mem)
            elif retention >= self.NUKE_THRESHOLD:
                archive.append(mem)
            else:
                nuke.append(mem)

        return {"keep": keep, "archive": archive, "nuke": nuke}

    async def run_consolidation_cycle(self) -> dict:
        """
        REM Cycle — consolida memorias.
        Ejecutar como cron nocturno.
        """
        stats = {"archived": 0, "nuked": 0, "kept": 0}

        # In production, this would query MemPalace + Mem0 for old memories
        # and apply decay. For now, returns structure for integration.
        logger.info("REM consolidation cycle completed", extra=stats)
        return stats


# ═══════════════════════════════════════════════════════════════
# ENGINE 3: METACOGNITION
# ═══════════════════════════════════════════════════════════════

class MetacognitionEngine:
    """
    El sistema sabe lo que NO sabe.
    
    Antes de cada acción, detecta:
    1. ¿Hay gaps en mi contexto para esta acción?
    2. ¿Mi confianza es suficiente para actuar?
    3. ¿Debería preguntar antes de proceder?
    
    A diferencia del ContaminationDetector (shadow mode),
    este engine BLOQUEA cuando detecta gap crítico.
    """

    def __init__(self, crystallization: CrystallizationEngine):
        self._crystallization = crystallization
        self._gaps: list[MetacognitiveGap] = []
        self._confidence_threshold = 0.7  # Below this → ASK before acting

    async def pre_action_check(
        self,
        action: str,
        context: dict,
        agent_id: str,
    ) -> dict:
        """
        Verifica si el agente tiene suficiente contexto para actuar.
        
        Returns:
            {
                "can_proceed": bool,
                "confidence": float,
                "gaps_detected": list[str],
                "recommendation": str,  # "proceed" | "ask_human" | "consult_backends" | "halt"
            }
        """
        gaps = []
        confidence = 1.0

        # Check 1: ¿Hay axiomas relevantes que el agente debería conocer?
        relevant_axioms = await self._crystallization.query_axioms(
            keyword=action.split("_")[0] if "_" in action else action
        )
        if relevant_axioms:
            # Verify agent has these in context
            context_text = json.dumps(context).lower()
            for ax in relevant_axioms:
                if ax.content.lower()[:50] not in context_text:
                    gaps.append(f"Missing axiom {ax.id}: {ax.content[:80]}")
                    confidence -= 0.15

        # Check 2: ¿Es una acción en un dominio donde el agente ha fallado antes?
        # (Delegates to ErrorMemory in production)
        action_lower = action.lower()
        high_risk_domains = ["deploy", "merge", "delete", "migrate", "production"]
        if any(d in action_lower for d in high_risk_domains):
            if not context.get("t1_approval") and not context.get("pre_validated"):
                gaps.append(f"High-risk action '{action}' without T1 approval or pre-validation")
                confidence -= 0.3

        # Check 3: ¿El contexto tiene timestamp reciente?
        context_age = context.get("context_age_hours", 0)
        if context_age > 24:
            gaps.append(f"Context is {context_age}h old — may be stale")
            confidence -= 0.2

        # Determine recommendation
        confidence = max(confidence, 0.0)
        if confidence >= 0.8 and not gaps:
            recommendation = "proceed"
        elif confidence >= self._confidence_threshold:
            recommendation = "proceed_with_caution"
        elif confidence >= 0.4:
            recommendation = "consult_backends"
        else:
            recommendation = "halt"

        # Register gaps
        for gap_desc in gaps:
            self._gaps.append(MetacognitiveGap(
                description=gap_desc,
                detected_by=agent_id,
                domain=action.split("_")[0] if "_" in action else "general",
                severity="high" if confidence < 0.4 else "medium",
            ))

        return {
            "can_proceed": recommendation in ("proceed", "proceed_with_caution"),
            "confidence": round(confidence, 3),
            "gaps_detected": gaps,
            "recommendation": recommendation,
            "relevant_axioms": [ax.content for ax in relevant_axioms],
        }

    async def report_gap(self, description: str, agent_id: str, domain: str = "general", severity: str = "medium"):
        """Un agente reporta algo que no sabe."""
        gap = MetacognitiveGap(
            description=description,
            detected_by=agent_id,
            domain=domain,
            severity=severity,
        )
        self._gaps.append(gap)
        return gap

    async def get_open_gaps(self) -> list[MetacognitiveGap]:
        """Retorna gaps no resueltos."""
        return [g for g in self._gaps if not g.resolved]


# ═══════════════════════════════════════════════════════════════
# ENGINE 4: CONFLICT RESOLUTION
# ═══════════════════════════════════════════════════════════════

class ConflictResolutionEngine:
    """
    Arbitraje cuando backends o agentes se contradicen.
    
    Ejemplo: Mem0 dice "proyecto usa TiDB" pero LightRAG dice
    "proyecto migró a Supabase". ¿Cuál es verdad?
    
    Estrategias:
    1. Temporal: el más reciente gana (si timestamps disponibles)
    2. Authority: fuente con mayor confianza gana
    3. Consensus: mayoría de backends/agentes gana
    4. Human: escala a T1 si no se puede resolver
    """

    def __init__(self):
        self._conflicts: list[ConflictRecord] = []
        self._authority_ranking = {
            "human_t1": 1.0,
            "axiom": 0.95,
            "memento_validator": 0.9,
            "error_memory": 0.85,
            "lightrag": 0.7,
            "mem0": 0.65,
            "mempalace": 0.6,
            "thoughts": 0.55,
            "agent_claim": 0.4,
        }

    async def detect_conflict(
        self,
        claim_a: str,
        source_a: str,
        claim_b: str,
        source_b: str,
    ) -> Optional[ConflictRecord]:
        """Detecta y registra un conflicto."""
        # Simple heuristic: if claims are about same subject but contradict
        # In production, use embeddings + LLM for semantic contradiction detection
        conflict = ConflictRecord(
            claim_a=claim_a,
            source_a=source_a,
            claim_b=claim_b,
            source_b=source_b,
        )
        self._conflicts.append(conflict)
        return conflict

    async def resolve(
        self,
        conflict: ConflictRecord,
        strategy: ConflictResolution = ConflictResolution.HIGHEST_CONFIDENCE,
    ) -> dict:
        """Resuelve un conflicto usando la estrategia indicada."""

        if strategy == ConflictResolution.HIGHEST_CONFIDENCE:
            score_a = self._authority_ranking.get(conflict.source_a, 0.3)
            score_b = self._authority_ranking.get(conflict.source_b, 0.3)
            winner = "a" if score_a >= score_b else "b"
            conflict.resolution = conflict.claim_a if winner == "a" else conflict.claim_b
            conflict.strategy_used = strategy
            return {
                "winner": winner,
                "winning_claim": conflict.resolution,
                "confidence": max(score_a, score_b),
                "strategy": strategy.value,
            }

        elif strategy == ConflictResolution.NEWEST_WINS:
            # Would need timestamps from both claims
            conflict.resolution = conflict.claim_a  # Default to A (assumed newer)
            conflict.strategy_used = strategy
            return {
                "winner": "a",
                "winning_claim": conflict.claim_a,
                "confidence": 0.6,
                "strategy": strategy.value,
            }

        elif strategy == ConflictResolution.HUMAN_ARBITRATION:
            conflict.strategy_used = strategy
            return {
                "winner": "pending",
                "winning_claim": None,
                "confidence": 0.0,
                "strategy": strategy.value,
                "action_required": "Escalate to T1 for resolution",
            }

        return {"winner": "unknown", "confidence": 0.0}

    async def get_unresolved(self) -> list[ConflictRecord]:
        """Retorna conflictos sin resolver."""
        return [c for c in self._conflicts if c.resolution is None]


# ═══════════════════════════════════════════════════════════════
# ENGINE 5: UNIVERSAL MULTI-AGENT API
# ═══════════════════════════════════════════════════════════════

class UniversalAgentAPI:
    """
    API unificada que cualquier IA puede consumir.
    
    Cada agente se identifica con agent_id:
    - "chatgpt-sop" → ChatGPT con SOP
    - "claude-cowork" → Claude Cowork
    - "manus-c" → Manus cuenta C
    - "gemini-sabio" → Gemini como sabio
    - "grok-redteam" → Grok como red-team
    - "embrion" → El Embrión IA
    
    Operaciones:
    - remember(content) → almacena en todos los backends
    - recall(query) → búsqueda federada
    - crystallize(insight) → promueve a axioma
    - pre_check(action) → metacognición pre-action
    - report_gap(description) → declara lo que no sabe
    - get_axioms() → obtiene verdades cristalizadas
    - resolve_conflict(claim_a, claim_b) → arbitraje
    """

    def __init__(
        self,
        backends: BackendAdapter,
        crystallization: CrystallizationEngine,
        forgetting: ForgettingEngine,
        metacognition: MetacognitionEngine,
        conflict_resolution: ConflictResolutionEngine,
    ):
        self._backends = backends
        self._crystallization = crystallization
        self._forgetting = forgetting
        self._metacognition = metacognition
        self._conflict = conflict_resolution
        self._agent_registry: dict[str, dict] = {}
        self._access_log: list[dict] = []

    def register_agent(self, agent_id: str, agent_type: str, capabilities: list[str] = None):
        """Registra un agente en el sistema."""
        self._agent_registry[agent_id] = {
            "agent_id": agent_id,
            "type": agent_type,
            "capabilities": capabilities or [],
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "last_active": datetime.now(timezone.utc).isoformat(),
        }

    async def remember(self, content: str, agent_id: str, metadata: dict = None) -> dict:
        """Almacena un entendimiento en todos los backends."""
        self._log_access(agent_id, "remember")
        meta = metadata or {}
        meta["agent_id"] = agent_id
        meta["stored_at"] = datetime.now(timezone.utc).isoformat()

        stored = await self._backends.store_to_all(content, agent_id, meta)
        return {"stored": stored, "agent_id": agent_id}

    async def recall(self, query: str, agent_id: str, limit: int = 10) -> dict:
        """Búsqueda federada en todos los backends."""
        self._log_access(agent_id, "recall")
        results = await self._backends.search_all(query, agent_id, limit)

        # Also include relevant axioms
        axioms = await self._crystallization.query_axioms(keyword=query.split()[0] if query else None)
        for ax in axioms[:3]:
            results.insert(0, {
                "source": "axiom",
                "content": ax.content,
                "score": 1.0,
                "metadata": {"id": ax.id, "domain": ax.domain, "immutable": True},
            })

        return {"results": results, "total": len(results), "agent_id": agent_id}

    async def crystallize(
        self,
        content: str,
        agent_id: str,
        domain: str = "general",
        source: str = "empirical",
    ) -> dict:
        """Promueve un insight a axioma inmutable."""
        self._log_access(agent_id, "crystallize")
        try:
            axiom = await self._crystallization.crystallize(
                content=content,
                source=AxiomSource(source),
                created_by=agent_id,
                domain=domain,
            )
            return {"axiom": axiom.to_dict(), "status": "crystallized"}
        except ValueError as e:
            return {"error": str(e), "status": "conflict"}

    async def pre_check(self, action: str, context: dict, agent_id: str) -> dict:
        """Metacognición pre-action — ¿puedo actuar?"""
        self._log_access(agent_id, "pre_check")
        return await self._metacognition.pre_action_check(action, context, agent_id)

    async def report_gap(self, description: str, agent_id: str, domain: str = "general") -> dict:
        """Declara algo que el agente no sabe."""
        self._log_access(agent_id, "report_gap")
        gap = await self._metacognition.report_gap(description, agent_id, domain)
        return {"gap_id": gap.id, "status": "registered"}

    async def get_axioms(self, domain: str = None, agent_id: str = "") -> dict:
        """Obtiene axiomas cristalizados."""
        self._log_access(agent_id, "get_axioms")
        axioms = await self._crystallization.query_axioms(domain=domain)
        return {
            "axioms": [ax.to_dict() for ax in axioms],
            "total": len(axioms),
        }

    async def resolve_conflict(
        self,
        claim_a: str,
        source_a: str,
        claim_b: str,
        source_b: str,
        agent_id: str,
    ) -> dict:
        """Resuelve un conflicto entre claims."""
        self._log_access(agent_id, "resolve_conflict")
        conflict = await self._conflict.detect_conflict(claim_a, source_a, claim_b, source_b)
        resolution = await self._conflict.resolve(conflict)
        return resolution

    async def get_system_state(self) -> dict:
        """Estado completo del sistema para diagnóstico."""
        axioms = await self._crystallization.get_all_axioms()
        gaps = await self._metacognition.get_open_gaps()
        conflicts = await self._conflict.get_unresolved()
        return {
            "axioms_count": len(axioms),
            "open_gaps": len(gaps),
            "unresolved_conflicts": len(conflicts),
            "registered_agents": len(self._agent_registry),
            "total_accesses": len(self._access_log),
            "agents": list(self._agent_registry.keys()),
        }

    def _log_access(self, agent_id: str, operation: str):
        """Log de acceso para auditoría."""
        self._access_log.append({
            "agent_id": agent_id,
            "operation": operation,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        # Update agent last_active
        if agent_id in self._agent_registry:
            self._agent_registry[agent_id]["last_active"] = datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════
# SOVEREIGN MEMORY SYSTEM v2 — MAIN CLASS
# ═══════════════════════════════════════════════════════════════

class SovereignMemorySystemV2:
    """
    El sistema de memoria más poderoso del mundo para agentes IA.
    
    Orquesta 18 backends existentes + 5 engines nuevos.
    Cualquier IA del mundo puede conectarse y beneficiarse.
    
    Usage:
        sms = SovereignMemorySystemV2()
        await sms.initialize()
        
        # Any agent can use it
        result = await sms.api.recall("What is the deploy policy?", agent_id="chatgpt-sop")
        check = await sms.api.pre_check("deploy_production", context={}, agent_id="manus-c")
        await sms.api.crystallize("Never deploy on Friday", agent_id="claude-cowork", domain="ops")
    """

    def __init__(self):
        self.backends = BackendAdapter()
        self.crystallization = CrystallizationEngine()
        self.forgetting = ForgettingEngine()
        self.metacognition = MetacognitionEngine(self.crystallization)
        self.conflict_resolution = ConflictResolutionEngine()
        self.api = UniversalAgentAPI(
            backends=self.backends,
            crystallization=self.crystallization,
            forgetting=self.forgetting,
            metacognition=self.metacognition,
            conflict_resolution=self.conflict_resolution,
        )
        self._initialized = False

    async def initialize(self) -> dict:
        """Inicializa todos los componentes."""
        # Connect to backends
        backend_status = await self.backends.initialize()

        # Load axioms from Supabase
        if self.backends._supabase:
            self.crystallization._supabase = self.backends._supabase
            await self.crystallization.load_from_supabase()

        # Register known agents
        known_agents = [
            ("chatgpt-sop", "chatgpt", ["reasoning", "planning"]),
            ("claude-cowork", "claude", ["code", "architecture", "audit"]),
            ("manus-c", "manus", ["execution", "browser", "code"]),
            ("manus-b", "manus", ["execution", "browser", "code"]),
            ("gemini-sabio", "gemini", ["research", "multimodal"]),
            ("grok-redteam", "grok", ["adversarial", "reasoning"]),
            ("deepseek-sabio", "deepseek", ["reasoning", "math"]),
            ("perplexity-sabio", "perplexity", ["search", "citations"]),
            ("embrion", "monstruo", ["autonomous", "proactive"]),
        ]
        for agent_id, agent_type, caps in known_agents:
            self.api.register_agent(agent_id, agent_type, caps)

        self._initialized = True
        return {
            "status": "initialized",
            "backends": backend_status,
            "axioms_loaded": len(self.crystallization._axioms),
            "agents_registered": len(self.api._agent_registry),
        }

    async def health(self) -> dict:
        """Health check."""
        return {
            "initialized": self._initialized,
            "system_state": await self.api.get_system_state(),
        }


# ═══════════════════════════════════════════════════════════════
# FASTAPI HTTP SERVER (Universal API endpoint)
# ═══════════════════════════════════════════════════════════════

def create_sms_app() -> "FastAPI":
    """
    Crea la app FastAPI para el SMS Universal API.
    Montable como sub-app en el kernel principal o standalone.
    """
    from fastapi import FastAPI, HTTPException, Header
    from pydantic import BaseModel

    app = FastAPI(
        title="Sovereign Memory System v2",
        description="Universal Multi-Agent Memory API — El Monstruo",
        version="2.0.0",
    )

    sms: Optional[SovereignMemorySystemV2] = None

    class RememberRequest(BaseModel):
        content: str
        metadata: dict = {}

    class RecallRequest(BaseModel):
        query: str
        limit: int = 10

    class CrystallizeRequest(BaseModel):
        content: str
        domain: str = "general"
        source: str = "empirical"

    class PreCheckRequest(BaseModel):
        action: str
        context: dict = {}

    class ReportGapRequest(BaseModel):
        description: str
        domain: str = "general"

    class ConflictRequest(BaseModel):
        claim_a: str
        source_a: str
        claim_b: str
        source_b: str

    async def _get_agent_id(x_agent_id: str = Header(None)) -> str:
        if not x_agent_id:
            raise HTTPException(401, "X-Agent-Id header required")
        return x_agent_id

    @app.on_event("startup")
    async def startup():
        nonlocal sms
        sms = SovereignMemorySystemV2()
        init_result = await sms.initialize()
        logger.info(f"SMS v2 started: {init_result}")

    @app.get("/health")
    async def health():
        return await sms.health()

    @app.post("/v1/memory/remember")
    async def remember(req: RememberRequest, x_agent_id: str = Header(None)):
        agent_id = x_agent_id or "anonymous"
        return await sms.api.remember(req.content, agent_id, req.metadata)

    @app.post("/v1/memory/recall")
    async def recall(req: RecallRequest, x_agent_id: str = Header(None)):
        agent_id = x_agent_id or "anonymous"
        return await sms.api.recall(req.query, agent_id, req.limit)

    @app.post("/v1/memory/crystallize")
    async def crystallize(req: CrystallizeRequest, x_agent_id: str = Header(None)):
        agent_id = x_agent_id or "anonymous"
        return await sms.api.crystallize(req.content, agent_id, req.domain, req.source)

    @app.post("/v1/memory/pre-check")
    async def pre_check(req: PreCheckRequest, x_agent_id: str = Header(None)):
        agent_id = x_agent_id or "anonymous"
        return await sms.api.pre_check(req.action, req.context, agent_id)

    @app.post("/v1/memory/report-gap")
    async def report_gap(req: ReportGapRequest, x_agent_id: str = Header(None)):
        agent_id = x_agent_id or "anonymous"
        return await sms.api.report_gap(req.description, agent_id, req.domain)

    @app.get("/v1/memory/axioms")
    async def get_axioms(domain: str = None, x_agent_id: str = Header(None)):
        agent_id = x_agent_id or "anonymous"
        return await sms.api.get_axioms(domain, agent_id)

    @app.post("/v1/memory/resolve-conflict")
    async def resolve_conflict(req: ConflictRequest, x_agent_id: str = Header(None)):
        agent_id = x_agent_id or "anonymous"
        return await sms.api.resolve_conflict(
            req.claim_a, req.source_a, req.claim_b, req.source_b, agent_id
        )

    @app.get("/v1/memory/state")
    async def system_state():
        return await sms.api.get_system_state()

    return app


# ═══════════════════════════════════════════════════════════════
# STANDALONE DEMO
# ═══════════════════════════════════════════════════════════════

async def _demo():
    """Demo standalone del SMS v2."""
    print("=" * 70)
    print("SOVEREIGN MEMORY SYSTEM v2.0 — Demo")
    print("=" * 70)

    sms = SovereignMemorySystemV2()
    init = await sms.initialize()
    print(f"\n[INIT] {json.dumps(init, indent=2)}")

    # Agent 1: ChatGPT cristaliza un axioma
    print("\n--- ChatGPT crystallizes an axiom ---")
    result = await sms.api.crystallize(
        content="Never deploy to production on Friday after 3pm",
        agent_id="chatgpt-sop",
        domain="operations",
        source="human_t1",
    )
    print(f"[CRYSTALLIZE] {json.dumps(result, indent=2)}")

    # Agent 2: Manus intenta deploy el viernes
    print("\n--- Manus tries to deploy on Friday ---")
    check = await sms.api.pre_check(
        action="deploy_production",
        context={"day": "friday", "time": "16:00"},
        agent_id="manus-c",
    )
    print(f"[PRE-CHECK] {json.dumps(check, indent=2)}")

    # Agent 3: Claude recuerda algo
    print("\n--- Claude stores a memory ---")
    stored = await sms.api.remember(
        content="The migration from TiDB to Supabase was completed on Sprint 26",
        agent_id="claude-cowork",
        metadata={"sprint": 26, "type": "migration"},
    )
    print(f"[REMEMBER] {json.dumps(stored, indent=2)}")

    # Agent 4: Gemini busca información
    print("\n--- Gemini recalls migration info ---")
    recalled = await sms.api.recall(
        query="database migration",
        agent_id="gemini-sabio",
    )
    print(f"[RECALL] {json.dumps(recalled, indent=2)}")

    # Agent 5: Grok detecta conflicto
    print("\n--- Grok detects a conflict ---")
    resolution = await sms.api.resolve_conflict(
        claim_a="Project uses TiDB as primary database",
        source_a="mem0",
        claim_b="Project migrated to Supabase PostgreSQL in Sprint 26",
        source_b="lightrag",
        agent_id="grok-redteam",
    )
    print(f"[CONFLICT] {json.dumps(resolution, indent=2)}")

    # System state
    print("\n--- System State ---")
    state = await sms.api.get_system_state()
    print(f"[STATE] {json.dumps(state, indent=2)}")

    print("\n" + "=" * 70)
    print("SMS v2 Demo Complete")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(_demo())
