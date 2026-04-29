#!/usr/bin/env python3.11
"""
cidp_memory.py — Memoria Jerárquica Externa.

Implementa tres niveles de memoria:
1. Permanente (facts_store): Hechos verificados, decisiones, contradicciones
2. Trabajo (working_memory): Contexto de la iteración actual
3. Histórica (history): Resúmenes de iteraciones anteriores

Backend: SQLite local para persistencia entre ejecuciones.
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path


class CIDPMemory:
    """Hierarchical external memory for CIDP."""

    def __init__(self, db_path: Path):
        """Initialize memory with SQLite backend."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Create tables if they don't exist."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT,
                value TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                source TEXT,
                verified BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                ttl_days INTEGER DEFAULT 90
            );

            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                rationale TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS contradictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                claim_1 TEXT,
                claim_2 TEXT,
                sabio_1 TEXT,
                sabio_2 TEXT,
                resolution TEXT,
                resolved BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                iteration INTEGER NOT NULL,
                summary TEXT NOT NULL,
                score REAL,
                created_at TEXT DEFAULT (datetime('now'))
            );

            
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                iteration INTEGER NOT NULL,
                stage TEXT NOT NULL,
                state_data TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                UNIQUE(run_id, iteration, stage)
            );

            CREATE INDEX IF NOT EXISTS idx_facts_category ON facts(category);
            CREATE INDEX IF NOT EXISTS idx_facts_key ON facts(key);
            CREATE INDEX IF NOT EXISTS idx_history_run ON history(run_id);
        """)
        self.conn.commit()

    def store_fact(self, category: str, data, key: str = None,
                   confidence: float = 0.5, source: str = None):
        """Store a fact in permanent memory."""
        value = json.dumps(data, ensure_ascii=False) if isinstance(data, (dict, list)) else str(data)
        self.conn.execute(
            "INSERT INTO facts (category, key, value, confidence, source) VALUES (?, ?, ?, ?, ?)",
            (category, key, value, confidence, source)
        )
        self.conn.commit()

    def get_facts(self, category: str = None, limit: int = 50) -> list:
        """Retrieve facts from permanent memory."""
        if category:
            rows = self.conn.execute(
                "SELECT * FROM facts WHERE category = ? ORDER BY created_at DESC LIMIT ?",
                (category, limit)
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM facts ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()

        results = []
        for row in rows:
            try:
                value = json.loads(row["value"])
            except (json.JSONDecodeError, TypeError):
                value = row["value"]
            results.append({
                "id": row["id"],
                "category": row["category"],
                "key": row["key"],
                "value": value,
                "confidence": row["confidence"],
                "source": row["source"],
                "verified": bool(row["verified"]),
                "created_at": row["created_at"],
            })
        return results

    def store_decision(self, decision_id: str, data: dict, rationale: str = None):
        """Store a decision in the decision log."""
        value = json.dumps(data, ensure_ascii=False)
        self.conn.execute(
            """INSERT OR REPLACE INTO decisions (decision_id, data, rationale)
               VALUES (?, ?, ?)""",
            (decision_id, value, rationale)
        )
        self.conn.commit()

    def get_decisions(self, limit: int = 10) -> list:
        """Retrieve recent decisions."""
        rows = self.conn.execute(
            "SELECT * FROM decisions ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()

        results = []
        for row in rows:
            try:
                data = json.loads(row["data"])
            except (json.JSONDecodeError, TypeError):
                data = row["data"]
            results.append({
                "decision_id": row["decision_id"],
                "data": data,
                "rationale": row["rationale"],
                "created_at": row["created_at"],
            })
        return results

    def store_contradiction(self, contradiction: dict):
        """Store a detected contradiction."""
        self.conn.execute(
            """INSERT INTO contradictions (type, claim_1, claim_2, sabio_1, sabio_2)
               VALUES (?, ?, ?, ?, ?)""",
            (
                contradiction.get("type", "unknown"),
                contradiction.get("claim_1", contradiction.get("claim", "")),
                contradiction.get("claim_2", ""),
                contradiction.get("sabio_1", contradiction.get("sabio", "")),
                contradiction.get("sabio_2", ""),
            )
        )
        self.conn.commit()

    def get_contradictions(self, resolved: bool = None, limit: int = 20) -> list:
        """Retrieve contradictions."""
        if resolved is not None:
            rows = self.conn.execute(
                "SELECT * FROM contradictions WHERE resolved = ? ORDER BY created_at DESC LIMIT ?",
                (int(resolved), limit)
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM contradictions ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()

        return [dict(row) for row in rows]

    def resolve_contradiction(self, contradiction_id: int, resolution: str):
        """Mark a contradiction as resolved."""
        self.conn.execute(
            "UPDATE contradictions SET resolved = 1, resolution = ? WHERE id = ?",
            (resolution, contradiction_id)
        )
        self.conn.commit()

    def store_history(self, run_id: str, iteration: int, summary: str, score: float = None):
        """Store an iteration summary in historical memory."""
        self.conn.execute(
            "INSERT INTO history (run_id, iteration, summary, score) VALUES (?, ?, ?, ?)",
            (run_id, iteration, summary, score)
        )
        self.conn.commit()

    def get_history(self, run_id: str = None, limit: int = 20) -> list:
        """Retrieve historical summaries."""
        if run_id:
            rows = self.conn.execute(
                "SELECT * FROM history WHERE run_id = ? ORDER BY iteration ASC LIMIT ?",
                (run_id, limit)
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM history ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()

        return [dict(row) for row in rows]

    
    def save_checkpoint(self, run_id: str, iteration: int, stage: str, state_data: dict, status: str = "completed"):
        """Save a checkpoint for a specific stage."""
        value = json.dumps(state_data, ensure_ascii=False)
        self.conn.execute(
            """INSERT OR REPLACE INTO checkpoints (run_id, iteration, stage, state_data, status)
               VALUES (?, ?, ?, ?, ?)""",
            (run_id, iteration, stage, value, status)
        )
        self.conn.commit()

    def get_checkpoint(self, run_id: str, iteration: int, stage: str) -> dict:
        """Retrieve a specific checkpoint."""
        row = self.conn.execute(
            "SELECT * FROM checkpoints WHERE run_id = ? AND iteration = ? AND stage = ?",
            (run_id, iteration, stage)
        ).fetchone()
        
        if not row:
            return None
            
        try:
            return json.loads(row["state_data"])
        except (json.JSONDecodeError, TypeError):
            return None

    def get_latest_checkpoint(self, run_id: str) -> dict:
        """Get the most recent checkpoint for a run to resume from."""
        row = self.conn.execute(
            "SELECT * FROM checkpoints WHERE run_id = ? ORDER BY iteration DESC, id DESC LIMIT 1",
            (run_id,)
        ).fetchone()
        
        if not row:
            return None
            
        return {
            "iteration": row["iteration"],
            "stage": row["stage"],
            "status": row["status"],
            "state_data": json.loads(row["state_data"])
        }

    def get_stats(self) -> dict:
        """Get memory statistics."""
        facts_count = self.conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        decisions_count = self.conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        contradictions_count = self.conn.execute("SELECT COUNT(*) FROM contradictions").fetchone()[0]
        unresolved = self.conn.execute(
            "SELECT COUNT(*) FROM contradictions WHERE resolved = 0"
        ).fetchone()[0]
        history_count = self.conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]

        return {
            "facts": facts_count,
            "decisions": decisions_count,
            "contradictions_total": contradictions_count,
            "contradictions_unresolved": unresolved,
            "history_entries": history_count,
        }

    def close(self):
        """Close the database connection."""
        self.conn.close()
