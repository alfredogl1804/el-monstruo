"""
El Monstruo — Knowledge Graph (Día 2)
========================================
Sovereign knowledge graph: entities, relations, and traversal.
In-memory + Supabase dual mode.

This is what Mem0 charges $249/mo for. We own it.

Principio: El conocimiento es tuyo. Las relaciones son tuyas.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

import structlog

from contracts.memory_interface import Entity, EntityType, Relation
from memory.supabase_client import SupabaseClient

logger = structlog.get_logger("knowledge_graph")


class KnowledgeGraph:
    """
    Sovereign knowledge graph.

    Stores entities (nodes) and relations (edges) with:
    - Temporal validity (valid_from, valid_to)
    - Weighted relations
    - Graph traversal up to N depth
    - Full-text search on entity names/attributes

    Dual mode: in-memory (always) + Supabase (when configured).
    """

    def __init__(self, db: Optional[SupabaseClient] = None) -> None:
        # In-memory stores
        self._entities: dict[UUID, Entity] = {}
        self._entities_by_name: dict[str, list[UUID]] = defaultdict(list)
        self._entities_by_type: dict[EntityType, list[UUID]] = defaultdict(list)
        self._relations: dict[UUID, Relation] = {}
        self._outgoing: dict[UUID, list[UUID]] = defaultdict(list)  # source -> [relation_ids]
        self._incoming: dict[UUID, list[UUID]] = defaultdict(list)  # target -> [relation_ids]

        # Persistence
        self._db = db

    @property
    def entity_count(self) -> int:
        """Return total number of entities in the graph."""
        return len(self._entities)

    @property
    def relation_count(self) -> int:
        """Return total number of relations in the graph."""
        return len(self._relations)

    async def initialize(self) -> None:
        """Load existing graph from Supabase if available."""
        if self._db and self._db.connected:
            try:
                # Load entities
                entity_rows = await self._db.select("entities", order_by="last_seen", order_desc=True, limit=1000)
                for row in entity_rows:
                    entity = self._row_to_entity(row)
                    if entity:
                        self._index_entity(entity)

                # Load relations
                relation_rows = await self._db.select("relations", order_by="valid_from", order_desc=True, limit=5000)
                for row in relation_rows:
                    relation = self._row_to_relation(row)
                    if relation:
                        self._index_relation(relation)

                logger.info(
                    "knowledge_graph_initialized",
                    entities=len(self._entities),
                    relations=len(self._relations),
                    persistence="supabase",
                )
            except Exception as e:
                logger.warning("knowledge_graph_load_failed", error=str(e))
        else:
            logger.info("knowledge_graph_initialized", persistence="in-memory")

    # ── Entity Operations ──────────────────────────────────────────

    async def upsert_entity(self, entity: Entity) -> UUID:
        """Create or update an entity."""
        # Check if entity with same name and type exists
        existing_id = self._find_existing_entity(entity.name, entity.entity_type)

        if existing_id:
            # Update existing entity
            old = self._entities[existing_id]
            # Merge attributes
            merged_attrs = {**old.attributes, **entity.attributes}
            updated = Entity(
                entity_id=existing_id,
                entity_type=entity.entity_type,
                name=entity.name,
                attributes=merged_attrs,
                first_seen=old.first_seen,
                last_seen=datetime.now(timezone.utc),
            )
            self._entities[existing_id] = updated

            # Persist update
            if self._db and self._db.connected:
                await self._db.upsert("entities", self._entity_to_row(updated), on_conflict="entity_id")

            logger.debug("entity_updated", entity_id=str(existing_id), name=entity.name)
            return existing_id
        else:
            # Create new entity
            self._index_entity(entity)

            # Persist
            if self._db and self._db.connected:
                await self._db.insert("entities", self._entity_to_row(entity))

            logger.debug("entity_created", entity_id=str(entity.entity_id), name=entity.name)
            return entity.entity_id

    async def get_entity(self, entity_id: UUID) -> Optional[Entity]:
        """Get an entity by ID."""
        return self._entities.get(entity_id)

    async def find_entities(
        self,
        query: str,
        entity_type: Optional[EntityType] = None,
        limit: int = 10,
    ) -> list[Entity]:
        """Search entities by name or attributes."""
        query_lower = query.lower()
        results = []

        candidates = self._entities.values()
        if entity_type:
            candidate_ids = self._entities_by_type.get(entity_type, [])
            candidates = [self._entities[eid] for eid in candidate_ids if eid in self._entities]

        for entity in candidates:
            score = 0.0

            # Name match
            name_lower = entity.name.lower()
            if query_lower == name_lower:
                score = 1.0
            elif query_lower in name_lower:
                score = 0.8
            elif name_lower in query_lower:
                score = 0.6
            else:
                # Check attributes
                attr_str = str(entity.attributes).lower()
                if query_lower in attr_str:
                    score = 0.4

            if score > 0:
                results.append((entity, score))

        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        return [entity for entity, _ in results[:limit]]

    # ── Relation Operations ────────────────────────────────────────

    async def add_relation(self, relation: Relation) -> UUID:
        """Add a relation between two entities."""
        # Validate entities exist
        if relation.source_id not in self._entities:
            raise ValueError(f"Source entity {relation.source_id} not found")
        if relation.target_id not in self._entities:
            raise ValueError(f"Target entity {relation.target_id} not found")

        self._index_relation(relation)

        # Persist
        if self._db and self._db.connected:
            await self._db.insert("relations", self._relation_to_row(relation))

        logger.debug(
            "relation_added",
            relation_id=str(relation.relation_id),
            source=str(relation.source_id),
            target=str(relation.target_id),
            relation_type=relation.relation_type,
        )
        return relation.relation_id

    async def get_relations(
        self,
        entity_id: UUID,
        direction: str = "both",  # "outgoing", "incoming", "both"
    ) -> list[Relation]:
        """Get all relations for an entity."""
        relation_ids = set()

        if direction in ("outgoing", "both"):
            relation_ids.update(self._outgoing.get(entity_id, []))
        if direction in ("incoming", "both"):
            relation_ids.update(self._incoming.get(entity_id, []))

        relations = [self._relations[rid] for rid in relation_ids if rid in self._relations]

        # Filter to currently valid relations
        now = datetime.now(timezone.utc)
        return [r for r in relations if r.valid_to is None or r.valid_to > now]

    async def invalidate_relation(self, relation_id: UUID) -> bool:
        """Mark a relation as no longer valid (temporal graph)."""
        relation = self._relations.get(relation_id)
        if not relation:
            return False

        # Create updated relation with valid_to set
        updated = Relation(
            relation_id=relation.relation_id,
            source_id=relation.source_id,
            target_id=relation.target_id,
            relation_type=relation.relation_type,
            weight=relation.weight,
            metadata=relation.metadata,
            valid_from=relation.valid_from,
            valid_to=datetime.now(timezone.utc),
        )
        self._relations[relation_id] = updated

        # Persist
        if self._db and self._db.connected:
            await self._db.update(
                "relations",
                {"valid_to": updated.valid_to.isoformat()},
                {"relation_id": str(relation_id)},
            )

        return True

    # ── Graph Traversal ────────────────────────────────────────────

    async def get_entity_graph(
        self,
        entity_id: UUID,
        depth: int = 2,
    ) -> tuple[list[Entity], list[Relation]]:
        """
        Get the subgraph around an entity.
        depth=1: only direct relations
        depth=2: relations of relations
        """
        if entity_id not in self._entities:
            return [], []

        visited_entities: set[UUID] = set()
        visited_relations: set[UUID] = set()
        queue: list[tuple[UUID, int]] = [(entity_id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)

            if current_id in visited_entities:
                continue
            visited_entities.add(current_id)

            if current_depth >= depth:
                continue

            # Get all relations for this entity
            relations = await self.get_relations(current_id)
            for relation in relations:
                visited_relations.add(relation.relation_id)

                # Queue the other end of the relation
                other_id = relation.target_id if relation.source_id == current_id else relation.source_id
                if other_id not in visited_entities:
                    queue.append((other_id, current_depth + 1))

        entities = [self._entities[eid] for eid in visited_entities if eid in self._entities]
        relations = [self._relations[rid] for rid in visited_relations if rid in self._relations]

        return entities, relations

    async def get_shortest_path(
        self,
        source_id: UUID,
        target_id: UUID,
        max_depth: int = 5,
    ) -> Optional[list[UUID]]:
        """Find shortest path between two entities (BFS)."""
        if source_id not in self._entities or target_id not in self._entities:
            return None

        visited: set[UUID] = set()
        queue: list[list[UUID]] = [[source_id]]

        while queue:
            path = queue.pop(0)
            current = path[-1]

            if current == target_id:
                return path

            if current in visited or len(path) > max_depth:
                continue
            visited.add(current)

            # Get neighbors
            relations = await self.get_relations(current)
            for relation in relations:
                neighbor = relation.target_id if relation.source_id == current else relation.source_id
                if neighbor not in visited:
                    queue.append(path + [neighbor])

        return None

    # ── Stats ──────────────────────────────────────────────────────

    async def get_stats(self) -> dict[str, Any]:
        """Get knowledge graph statistics."""
        now = datetime.now(timezone.utc)
        valid_relations = [r for r in self._relations.values() if r.valid_to is None or r.valid_to > now]

        type_counts = {}
        for eid_list in self._entities_by_type.values():
            for eid in eid_list:
                entity = self._entities.get(eid)
                if entity:
                    t = entity.entity_type.value
                    type_counts[t] = type_counts.get(t, 0) + 1

        relation_type_counts = {}
        for r in valid_relations:
            relation_type_counts[r.relation_type] = relation_type_counts.get(r.relation_type, 0) + 1

        return {
            "total_entities": len(self._entities),
            "total_relations": len(valid_relations),
            "expired_relations": len(self._relations) - len(valid_relations),
            "entities_by_type": type_counts,
            "relations_by_type": relation_type_counts,
            "persistence": "supabase" if (self._db and self._db.connected) else "in-memory",
        }

    # ── Private Helpers ────────────────────────────────────────────

    def _index_entity(self, entity: Entity) -> None:
        """Add entity to in-memory indexes."""
        self._entities[entity.entity_id] = entity
        self._entities_by_name[entity.name.lower()].append(entity.entity_id)
        self._entities_by_type[entity.entity_type].append(entity.entity_id)

    def _index_relation(self, relation: Relation) -> None:
        """Add relation to in-memory indexes."""
        self._relations[relation.relation_id] = relation
        self._outgoing[relation.source_id].append(relation.relation_id)
        self._incoming[relation.target_id].append(relation.relation_id)

    def _find_existing_entity(self, name: str, entity_type: EntityType) -> Optional[UUID]:
        """Find an existing entity by name and type."""
        candidates = self._entities_by_name.get(name.lower(), [])
        for eid in candidates:
            entity = self._entities.get(eid)
            if entity and entity.entity_type == entity_type:
                return eid
        return None

    @staticmethod
    def _entity_to_row(entity: Entity) -> dict[str, Any]:
        """Convert Entity to Supabase row."""
        return {
            "entity_id": str(entity.entity_id),
            "entity_type": entity.entity_type.value,
            "name": entity.name,
            "attributes": entity.attributes,
            "first_seen": entity.first_seen.isoformat()
            if hasattr(entity.first_seen, "isoformat")
            else str(entity.first_seen),
            "last_seen": entity.last_seen.isoformat()
            if hasattr(entity.last_seen, "isoformat")
            else str(entity.last_seen),
        }

    @staticmethod
    def _relation_to_row(relation: Relation) -> dict[str, Any]:
        """Convert Relation to Supabase row."""
        return {
            "relation_id": str(relation.relation_id),
            "source_id": str(relation.source_id),
            "target_id": str(relation.target_id),
            "relation_type": relation.relation_type,
            "weight": relation.weight,
            "metadata": relation.metadata,
            "valid_from": relation.valid_from.isoformat()
            if hasattr(relation.valid_from, "isoformat")
            else str(relation.valid_from),
            "valid_to": relation.valid_to.isoformat()
            if relation.valid_to and hasattr(relation.valid_to, "isoformat")
            else None,
        }

    @staticmethod
    def _row_to_entity(row: dict) -> Optional[Entity]:
        """Convert Supabase row to Entity."""
        try:
            from uuid import UUID as _UUID

            return Entity(
                entity_id=_UUID(row["entity_id"]),
                entity_type=EntityType(row.get("entity_type", "custom")),
                name=row.get("name", ""),
                attributes=row.get("attributes", {}),
                first_seen=datetime.fromisoformat(row["first_seen"])
                if isinstance(row.get("first_seen"), str)
                else datetime.now(timezone.utc),
                last_seen=datetime.fromisoformat(row["last_seen"])
                if isinstance(row.get("last_seen"), str)
                else datetime.now(timezone.utc),
            )
        except Exception:
            return None

    @staticmethod
    def _row_to_relation(row: dict) -> Optional[Relation]:
        """Convert Supabase row to Relation."""
        try:
            from uuid import UUID as _UUID

            return Relation(
                relation_id=_UUID(row["relation_id"]),
                source_id=_UUID(row["source_id"]),
                target_id=_UUID(row["target_id"]),
                relation_type=row.get("relation_type", ""),
                weight=row.get("weight", 1.0),
                metadata=row.get("metadata", {}),
                valid_from=datetime.fromisoformat(row["valid_from"])
                if isinstance(row.get("valid_from"), str)
                else datetime.now(timezone.utc),
                valid_to=datetime.fromisoformat(row["valid_to"])
                if isinstance(row.get("valid_to"), str) and row.get("valid_to")
                else None,
            )
        except Exception:
            return None
