"""
El Monstruo — Causal Knowledge Base (Sprint 55.3)
==================================================
Base de conocimiento causal persistente.
Almacena eventos del mundo descompuestos en factores causales atómicos.

Cada evento tiene:
  - Descripción del evento
  - Categoría (político, económico, tecnológico, social, empresarial)
  - Factores causales (lista de factores con peso probabilístico)
  - Embedding del evento (para búsqueda semántica)
  - Fuentes (de dónde se extrajo la información)
  - Fecha del evento
  - Predicciones derivadas (si aplica)

Arquitectura: Mismo patrón que memory/thoughts.py
  - Supabase tabla `causal_events`
  - pgvector para embeddings (vector(1536))
  - RPC `search_causal_events` para búsqueda semántica
  - CRUD completo

Objetivo #10 (Simulador Predictivo): Esta es la materia prima del motor predictivo.
El CausalDecomposer (Sprint 55.4) alimenta esta base.
El PredictiveSimulator (Sprint 57+) la consulta para generar predicciones.

Validated: Supabase pgvector (ya en stack), text-embedding-3-small (ya en uso en thoughts.py)
Sprint 55.3 | Biblia: Simulador Predictivo v1 (Obj #10)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger("memory.causal_kb")


# ── Dataclasses ──────────────────────────────────────────────────────────────


@dataclass
class CausalFactor:
    """
    Un factor causal atómico con peso probabilístico.

    Representa una causa individual de un evento.
    Cada factor tiene:
      - weight: qué tanto contribuyó al evento (0.0 = irrelevante, 1.0 = determinante)
      - confidence: qué tan seguro estamos de que es causal (no solo correlacional)
      - direction: si el factor contribuye (positive), previene (negative) o es neutro
    """
    factor_id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    category: str = "general"  # economic, political, social, technological, cultural, environmental
    weight: float = 0.5        # 0.0 (irrelevante) → 1.0 (determinante)
    confidence: float = 0.7    # Confianza en causalidad (no correlación)
    direction: str = "positive"  # positive | negative | neutral
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "factor_id": self.factor_id,
            "description": self.description,
            "category": self.category,
            "weight": self.weight,
            "confidence": self.confidence,
            "direction": self.direction,
            "evidence": self.evidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CausalFactor":
        return cls(
            factor_id=data.get("factor_id", str(uuid4())),
            description=data.get("description", ""),
            category=data.get("category", "general"),
            weight=float(data.get("weight", 0.5)),
            confidence=float(data.get("confidence", 0.7)),
            direction=data.get("direction", "positive"),
            evidence=data.get("evidence", []),
        )


@dataclass
class CausalEvent:
    """
    Un evento del mundo descompuesto en factores causales.

    Es la unidad atómica de la Causal Knowledge Base.
    Alimenta el Simulador Predictivo (Obj #10) con patrones históricos.
    """
    event_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    category: str = "general"   # political, economic, technological, social, business, environmental
    date: Optional[str] = None  # ISO date del evento (YYYY-MM-DD)
    outcome: str = ""           # Qué pasó como resultado final
    factors: list[CausalFactor] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    decomposed_by: str = "system"  # sabio | embrion | manual | system
    decomposed_at: Optional[str] = None
    validation_score: float = 0.0  # 0.0-1.0 — qué tan validada está la descomposición

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "date": self.date,
            "outcome": self.outcome,
            "factors": [f.to_dict() for f in self.factors],
            "sources": self.sources,
            "tags": self.tags,
            "decomposed_by": self.decomposed_by,
            "decomposed_at": self.decomposed_at,
            "validation_score": self.validation_score,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CausalEvent":
        factors_raw = data.get("factors", [])
        if isinstance(factors_raw, str):
            factors_raw = json.loads(factors_raw)
        factors = [CausalFactor.from_dict(f) for f in factors_raw]
        return cls(
            event_id=data.get("event_id", str(uuid4())),
            title=data.get("title", ""),
            description=data.get("description", ""),
            category=data.get("category", "general"),
            date=data.get("date"),
            outcome=data.get("outcome", ""),
            factors=factors,
            sources=data.get("sources", []),
            tags=data.get("tags", []),
            decomposed_by=data.get("decomposed_by", "system"),
            decomposed_at=data.get("decomposed_at"),
            validation_score=float(data.get("validation_score", 0.0)),
        )

    @property
    def dominant_factor(self) -> Optional[CausalFactor]:
        """Retorna el factor causal con mayor peso."""
        if not self.factors:
            return None
        return max(self.factors, key=lambda f: f.weight)

    @property
    def average_confidence(self) -> float:
        """Confianza promedio de todos los factores."""
        if not self.factors:
            return 0.0
        return sum(f.confidence for f in self.factors) / len(self.factors)


# ── CausalKnowledgeBase ──────────────────────────────────────────────────────


class CausalKnowledgeBase:
    """
    Base de conocimiento causal con persistencia en Supabase.

    Patrón: ThoughtsStore (memory/thoughts.py) adaptado para causalidad.
    Usa pgvector para búsqueda semántica de eventos similares.

    Uso típico:
        kb = CausalKnowledgeBase(db=supabase_client)
        await kb.initialize()

        event = CausalEvent(
            title="Tesla superó $1T de market cap",
            category="business",
            factors=[
                CausalFactor(description="EV adoption acceleration", weight=0.85),
                CausalFactor(description="Zero interest rate environment", weight=0.80),
            ]
        )
        await kb.store_event(event)

        similar = await kb.search_similar("valuación de empresas de vehículos eléctricos")
    """

    TABLE = "causal_events"
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIM = 1536

    def __init__(self, db: Any = None):
        self._db = db
        self._openai = None
        self._initialized = False

    async def initialize(self) -> None:
        """Inicializar cliente OpenAI para embeddings."""
        try:
            from openai import AsyncOpenAI
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self._openai = AsyncOpenAI(api_key=api_key)
                logger.info("causal_kb_openai_ready", model=self.EMBEDDING_MODEL)
            else:
                logger.warning("causal_kb_no_openai_key", hint="Embeddings disabled — set OPENAI_API_KEY")
            self._initialized = True
            logger.info("causal_kb_initialized", db=self._db is not None)
        except Exception as e:
            logger.error("causal_kb_init_failed", error=str(e))
            self._initialized = True  # Funcionar en modo degradado

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generar embedding para un texto usando text-embedding-3-small."""
        if not self._openai:
            return [0.0] * self.EMBEDDING_DIM

        try:
            response = await self._openai.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=text[:8000],  # Límite seguro para el modelo
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("causal_kb_embedding_failed", error=str(e))
            return [0.0] * self.EMBEDDING_DIM

    async def store_event(self, event: CausalEvent) -> str:
        """
        Almacenar un evento causal con su embedding en Supabase.

        El embedding se genera del título + descripción + factores concatenados.
        Usa upsert para evitar duplicados (idempotente).

        Returns:
            event_id del evento almacenado
        """
        # Construir texto para embedding — incluye factores para búsqueda semántica rica
        factors_text = "; ".join([
            f"{f.description} (peso:{f.weight:.2f}, dir:{f.direction})"
            for f in event.factors
        ])
        embed_text = f"{event.title}. {event.description}. Factores: {factors_text}"

        embedding = await self._generate_embedding(embed_text)

        event.decomposed_at = datetime.now(timezone.utc).isoformat()

        row = {
            "id": event.event_id,
            "title": event.title,
            "description": event.description,
            "category": event.category,
            "event_date": event.date,
            "outcome": event.outcome,
            "factors": json.dumps([f.to_dict() for f in event.factors]),
            "sources": event.sources,
            "tags": event.tags,
            "decomposed_by": event.decomposed_by,
            "decomposed_at": event.decomposed_at,
            "validation_score": event.validation_score,
            "embedding": embedding,
        }

        if self._db:
            await self._db.upsert(self.TABLE, row)

        logger.info(
            "causal_event_stored",
            event_id=event.event_id,
            title=event.title[:60],
            factors=len(event.factors),
            category=event.category,
        )
        return event.event_id

    async def search_similar(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        """
        Buscar eventos causales similares por semántica.

        Usa pgvector cosine similarity via RPC `search_causal_events`.
        Retorna eventos ordenados por similitud descendente.

        Args:
            query: Texto de búsqueda (ej: "crisis financiera 2008")
            limit: Máximo de resultados (default: 10)
            threshold: Similitud mínima 0.0-1.0 (default: 0.7)

        Returns:
            Lista de dicts con event data + similarity score
        """
        embedding = await self._generate_embedding(query)

        if not self._db:
            logger.warning("causal_kb_search_no_db")
            return []

        try:
            results = await self._db.rpc("search_causal_events", {
                "query_embedding": embedding,
                "match_threshold": threshold,
                "match_count": limit,
            })
            return results or []
        except Exception as e:
            logger.error("causal_kb_search_failed", error=str(e), query=query[:50])
            return []

    async def get_event(self, event_id: str) -> Optional[CausalEvent]:
        """Obtener un evento causal por ID."""
        if not self._db:
            return None

        try:
            rows = await self._db.select(self.TABLE, filters={"id": event_id})
            if not rows:
                return None
            row = rows[0]
            return CausalEvent.from_dict({
                "event_id": row["id"],
                **row,
            })
        except Exception as e:
            logger.error("causal_kb_get_failed", event_id=event_id, error=str(e))
            return None

    async def get_factors_for_category(self, category: str) -> list[dict[str, Any]]:
        """
        Obtener todos los factores causales de una categoría.

        Útil para identificar patrones recurrentes en una categoría
        (ej: todos los factores de eventos económicos).

        Returns:
            Lista de dicts con factor data + event_title + event_id
        """
        if not self._db:
            return []

        try:
            rows = await self._db.select(self.TABLE, filters={"category": category})
            all_factors: list[dict[str, Any]] = []
            for row in rows:
                factors_raw = row.get("factors", "[]")
                if isinstance(factors_raw, str):
                    factors = json.loads(factors_raw)
                else:
                    factors = factors_raw
                for f in factors:
                    f["event_title"] = row.get("title", "")
                    f["event_id"] = row.get("id", "")
                    all_factors.append(f)
            return all_factors
        except Exception as e:
            logger.error("causal_kb_category_failed", category=category, error=str(e))
            return []

    async def get_recent_events(self, limit: int = 20) -> list[dict[str, Any]]:
        """Obtener los eventos más recientemente almacenados."""
        if not self._db:
            return []

        try:
            rows = await self._db.select(
                self.TABLE,
                order_by="decomposed_at",
                order_desc=True,
                limit=limit,
            )
            return rows or []
        except Exception as e:
            logger.error("causal_kb_recent_failed", error=str(e))
            return []

    async def get_stats(self) -> dict[str, Any]:
        """Estadísticas de la base causal."""
        if not self._db:
            return {
                "total_events": 0,
                "status": "no_db",
                "embedding_model": self.EMBEDDING_MODEL,
            }

        try:
            count = await self._db.count(self.TABLE)
            return {
                "total_events": count,
                "status": "active",
                "embedding_model": self.EMBEDDING_MODEL,
                "embedding_dim": self.EMBEDDING_DIM,
                "table": self.TABLE,
            }
        except Exception as e:
            return {
                "total_events": -1,
                "status": f"error: {e}",
                "embedding_model": self.EMBEDDING_MODEL,
            }


# ── Singleton global ──────────────────────────────────────────────────────────

_causal_kb: Optional[CausalKnowledgeBase] = None


def get_causal_kb(db: Any = None) -> CausalKnowledgeBase:
    """
    Retorna la instancia global de CausalKnowledgeBase.

    Args:
        db: SupabaseClient — requerido solo en la primera llamada.

    Returns:
        CausalKnowledgeBase instance (crea una nueva si no existe)
    """
    global _causal_kb
    if _causal_kb is None:
        _causal_kb = CausalKnowledgeBase(db=db)
        logger.info("causal_kb_singleton_created")
    return _causal_kb
