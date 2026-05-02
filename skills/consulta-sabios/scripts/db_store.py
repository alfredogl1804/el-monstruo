#!/usr/bin/env python3.11
"""
db_store.py — Capa de Persistencia SQLite + Supabase Ready
============================================================
Almacena historial de consultas, métricas por sabio, scores,
y mejoras en SQLite. Preparado para sync a Supabase.

Funciones públicas:
    - init_db() → crea tablas si no existen
    - save_run(run_data) → guarda un run completo
    - save_sabio_metric(metric) → guarda métrica de un sabio
    - save_score(run_id, scores) → guarda scores de un run
    - save_improvement(improvement) → guarda una mejora propuesta/aplicada
    - query_runs(filters) → consulta runs con filtros
    - query_sabio_stats(sabio_id) → estadísticas de un sabio
    - export_for_supabase() → exporta datos para sync

Creado: 2026-04-08 (P2 auditoría sabios)
"""

import json
import os
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

SKILL_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
DATA_DIR = SKILL_DIR / "data"
DB_PATH = DATA_DIR / "consulta_sabios.db"


# ═══════════════════════════════════════════════════════════════
# CONEXIÓN
# ═══════════════════════════════════════════════════════════════


@contextmanager
def get_db():
    """Context manager para conexión SQLite."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# SCHEMA
# ═══════════════════════════════════════════════════════════════

SCHEMA_SQL = """
-- Runs: cada consulta completa al consejo
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    timestamp_start TEXT NOT NULL,
    timestamp_end TEXT,
    status TEXT DEFAULT 'running',  -- running, success, partial, failed
    modo TEXT DEFAULT 'enjambre',   -- enjambre, consejo, iterativo
    prompt_fingerprint TEXT,
    prompt_chars INTEGER,
    prompt_tokens_est INTEGER,
    dossier_chars INTEGER,
    sabios_total INTEGER DEFAULT 6,
    sabios_successful INTEGER DEFAULT 0,
    duration_ms_total INTEGER,
    score_global REAL,
    score_factualidad REAL,
    score_cobertura REAL,
    score_consenso REAL,
    contradicciones INTEGER DEFAULT 0,
    score_sintesis REAL,
    metadata_json TEXT,  -- JSON con datos adicionales
    synced_to_supabase INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Métricas por sabio por run
CREATE TABLE IF NOT EXISTS sabio_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    sabio_id TEXT NOT NULL,
    success INTEGER NOT NULL DEFAULT 0,
    duration_ms INTEGER,
    input_tokens_est INTEGER,
    output_tokens_est INTEGER,
    retry_count INTEGER DEFAULT 0,
    error_type TEXT,
    error_message TEXT,
    quality_score REAL,
    quality_verdict TEXT,
    response_chars INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    synced_to_supabase INTEGER DEFAULT 0
);

-- Scores detallados por run
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    factualidad REAL,
    cobertura REAL,
    consenso REAL,
    contradicciones INTEGER,
    sintesis_quality REAL,
    score_global REAL,
    detalle_json TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    synced_to_supabase INTEGER DEFAULT 0
);

-- Mejoras propuestas y aplicadas
CREATE TABLE IF NOT EXISTS improvements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    improvement_id TEXT UNIQUE,
    tipo TEXT NOT NULL,  -- config, prompt, script, workflow
    descripcion TEXT NOT NULL,
    estado TEXT DEFAULT 'propuesta',  -- propuesta, aprobada, aplicada, revertida, rechazada
    fuente TEXT,  -- run_id que originó la propuesta
    diff_json TEXT,  -- cambios propuestos
    score_antes REAL,
    score_despues REAL,
    aplicada_en TEXT,  -- timestamp
    revertida_en TEXT,
    motivo_reversion TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    synced_to_supabase INTEGER DEFAULT 0
);

-- Cache de dossiers
CREATE TABLE IF NOT EXISTS dossier_cache (
    fingerprint TEXT PRIMARY KEY,
    tema TEXT,
    dossier_text TEXT,
    chars INTEGER,
    ttl_hours INTEGER DEFAULT 24,
    created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT,
    hit_count INTEGER DEFAULT 0,
    synced_to_supabase INTEGER DEFAULT 0
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp_start);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_sync ON runs(synced_to_supabase);
CREATE INDEX IF NOT EXISTS idx_sabio_metrics_run ON sabio_metrics(run_id);
CREATE INDEX IF NOT EXISTS idx_sabio_metrics_sabio ON sabio_metrics(sabio_id);
CREATE INDEX IF NOT EXISTS idx_improvements_estado ON improvements(estado);
CREATE INDEX IF NOT EXISTS idx_dossier_cache_expires ON dossier_cache(expires_at);
"""


def init_db():
    """Inicializa la base de datos con el schema completo."""
    with get_db() as conn:
        conn.executescript(SCHEMA_SQL)
    print(f"✅ Base de datos inicializada: {DB_PATH}")


# ═══════════════════════════════════════════════════════════════
# OPERACIONES CRUD
# ═══════════════════════════════════════════════════════════════


def save_run(run_data: dict):
    """Guarda o actualiza un run."""
    with get_db() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO runs 
            (run_id, timestamp_start, timestamp_end, status, modo,
             prompt_fingerprint, prompt_chars, prompt_tokens_est,
             dossier_chars, sabios_total, sabios_successful,
             duration_ms_total, score_global, score_factualidad,
             score_cobertura, score_consenso, contradicciones,
             score_sintesis, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                run_data.get("run_id"),
                run_data.get("timestamp_start"),
                run_data.get("timestamp_end"),
                run_data.get("status", "running"),
                run_data.get("modo", "enjambre"),
                run_data.get("prompt_fingerprint"),
                run_data.get("prompt_chars"),
                run_data.get("prompt_tokens_est"),
                run_data.get("dossier_chars"),
                run_data.get("sabios_total", 6),
                run_data.get("sabios_successful", 0),
                run_data.get("duration_ms_total"),
                run_data.get("score_global"),
                run_data.get("score_factualidad"),
                run_data.get("score_cobertura"),
                run_data.get("score_consenso"),
                run_data.get("contradicciones"),
                run_data.get("score_sintesis"),
                json.dumps(run_data.get("metadata", {}), ensure_ascii=False),
            ),
        )


def save_sabio_metric(metric: dict):
    """Guarda una métrica de sabio."""
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO sabio_metrics
            (run_id, sabio_id, success, duration_ms, input_tokens_est,
             output_tokens_est, retry_count, error_type, error_message,
             quality_score, quality_verdict, response_chars)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metric.get("run_id"),
                metric.get("sabio_id"),
                1 if metric.get("success") else 0,
                metric.get("duration_ms"),
                metric.get("input_tokens_est"),
                metric.get("output_tokens_est"),
                metric.get("retry_count", 0),
                metric.get("error_type"),
                metric.get("error_message"),
                metric.get("quality_score"),
                metric.get("quality_verdict"),
                metric.get("response_chars"),
            ),
        )


def save_score(run_id: str, scores: dict):
    """Guarda scores de un run."""
    with get_db() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO scores
            (run_id, factualidad, cobertura, consenso, contradicciones,
             sintesis_quality, score_global, detalle_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                run_id,
                scores.get("factualidad"),
                scores.get("cobertura"),
                scores.get("consenso"),
                scores.get("contradicciones"),
                scores.get("sintesis_quality"),
                scores.get("score_global"),
                json.dumps(scores.get("detalle_por_sabio", {}), ensure_ascii=False),
            ),
        )
        # Update run with scores
        conn.execute(
            """
            UPDATE runs SET
                score_global = ?,
                score_factualidad = ?,
                score_cobertura = ?,
                score_consenso = ?,
                contradicciones = ?,
                score_sintesis = ?
            WHERE run_id = ?
        """,
            (
                scores.get("score_global"),
                scores.get("factualidad"),
                scores.get("cobertura"),
                scores.get("consenso"),
                scores.get("contradicciones"),
                scores.get("sintesis_quality"),
                run_id,
            ),
        )


def save_improvement(improvement: dict):
    """Guarda una mejora propuesta."""
    with get_db() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO improvements
            (improvement_id, tipo, descripcion, estado, fuente,
             diff_json, score_antes, score_despues, aplicada_en,
             revertida_en, motivo_reversion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                improvement.get("improvement_id"),
                improvement.get("tipo"),
                improvement.get("descripcion"),
                improvement.get("estado", "propuesta"),
                improvement.get("fuente"),
                json.dumps(improvement.get("diff", {}), ensure_ascii=False),
                improvement.get("score_antes"),
                improvement.get("score_despues"),
                improvement.get("aplicada_en"),
                improvement.get("revertida_en"),
                improvement.get("motivo_reversion"),
            ),
        )


# ═══════════════════════════════════════════════════════════════
# CONSULTAS
# ═══════════════════════════════════════════════════════════════


def query_runs(limit: int = 50, status: str = None) -> list:
    """Consulta runs con filtros opcionales."""
    with get_db() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM runs WHERE status = ? ORDER BY timestamp_start DESC LIMIT ?", (status, limit)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM runs ORDER BY timestamp_start DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


def query_sabio_stats(sabio_id: str = None) -> list:
    """Estadísticas agregadas por sabio."""
    with get_db() as conn:
        if sabio_id:
            rows = conn.execute(
                """
                SELECT sabio_id,
                    COUNT(*) as total,
                    SUM(success) as exitosos,
                    AVG(duration_ms) as duracion_media,
                    AVG(quality_score) as quality_media,
                    SUM(CASE WHEN error_type IS NOT NULL THEN 1 ELSE 0 END) as errores
                FROM sabio_metrics
                WHERE sabio_id = ?
                GROUP BY sabio_id
            """,
                (sabio_id,),
            ).fetchall()
        else:
            rows = conn.execute("""
                SELECT sabio_id,
                    COUNT(*) as total,
                    SUM(success) as exitosos,
                    AVG(duration_ms) as duracion_media,
                    AVG(quality_score) as quality_media,
                    SUM(CASE WHEN error_type IS NOT NULL THEN 1 ELSE 0 END) as errores
                FROM sabio_metrics
                GROUP BY sabio_id
                ORDER BY sabio_id
            """).fetchall()
        return [dict(r) for r in rows]


def query_improvements(estado: str = None) -> list:
    """Consulta mejoras con filtro opcional."""
    with get_db() as conn:
        if estado:
            rows = conn.execute(
                "SELECT * FROM improvements WHERE estado = ? ORDER BY created_at DESC", (estado,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM improvements ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
# CACHE DE DOSSIER
# ═══════════════════════════════════════════════════════════════


def cache_dossier(fingerprint: str, tema: str, dossier: str, ttl_hours: int = 24):
    """Guarda un dossier en caché."""
    from datetime import timedelta

    expires = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
    with get_db() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO dossier_cache
            (fingerprint, tema, dossier_text, chars, ttl_hours, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (fingerprint, tema, dossier, len(dossier), ttl_hours, expires),
        )


def get_cached_dossier(fingerprint: str) -> str:
    """Recupera un dossier del caché si no ha expirado."""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT dossier_text FROM dossier_cache
            WHERE fingerprint = ? AND expires_at > datetime('now')
        """,
            (fingerprint,),
        ).fetchone()
        if row:
            conn.execute("UPDATE dossier_cache SET hit_count = hit_count + 1 WHERE fingerprint = ?", (fingerprint,))
            return row["dossier_text"]
    return None


def cleanup_expired_cache():
    """Limpia dossiers expirados."""
    with get_db() as conn:
        result = conn.execute("DELETE FROM dossier_cache WHERE expires_at < datetime('now')")
        return result.rowcount


# ═══════════════════════════════════════════════════════════════
# EXPORT PARA SUPABASE
# ═══════════════════════════════════════════════════════════════


def export_for_supabase() -> dict:
    """Exporta registros no sincronizados para Supabase."""
    with get_db() as conn:
        runs = [dict(r) for r in conn.execute("SELECT * FROM runs WHERE synced_to_supabase = 0").fetchall()]

        metrics = [dict(r) for r in conn.execute("SELECT * FROM sabio_metrics WHERE synced_to_supabase = 0").fetchall()]

        scores = [dict(r) for r in conn.execute("SELECT * FROM scores WHERE synced_to_supabase = 0").fetchall()]

        improvements = [
            dict(r) for r in conn.execute("SELECT * FROM improvements WHERE synced_to_supabase = 0").fetchall()
        ]

    return {
        "runs": runs,
        "sabio_metrics": metrics,
        "scores": scores,
        "improvements": improvements,
        "total_pending": len(runs) + len(metrics) + len(scores) + len(improvements),
    }


def mark_synced(table: str, ids: list):
    """Marca registros como sincronizados con Supabase."""
    with get_db() as conn:
        id_col = "run_id" if table == "runs" else "id"
        placeholders = ",".join("?" * len(ids))
        conn.execute(f"UPDATE {table} SET synced_to_supabase = 1 WHERE {id_col} IN ({placeholders})", ids)


# ═══════════════════════════════════════════════════════════════
# MIGRACIÓN DESDE JSONL
# ═══════════════════════════════════════════════════════════════


def migrate_from_jsonl():
    """Migra datos existentes de JSONL a SQLite."""
    from telemetry import HISTORY_DIR, read_jsonl

    init_db()

    # Migrar consultas
    runs = read_jsonl(HISTORY_DIR / "consultas.jsonl")
    migrated_runs = 0
    for r in runs:
        try:
            save_run(r)
            migrated_runs += 1
        except Exception as e:
            print(f"⚠️  Error migrando run: {e}")

    # Migrar métricas de sabios
    metrics = read_jsonl(HISTORY_DIR / "sabios_metrics.jsonl")
    migrated_metrics = 0
    for m in metrics:
        try:
            save_sabio_metric(m)
            migrated_metrics += 1
        except Exception as e:
            print(f"⚠️  Error migrando metric: {e}")

    print(f"✅ Migración completada: {migrated_runs} runs, {migrated_metrics} métricas")


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        migrate_from_jsonl()
    elif len(sys.argv) > 1 and sys.argv[1] == "stats":
        init_db()
        stats = query_sabio_stats()
        if stats:
            print("📊 Estadísticas por sabio:")
            for s in stats:
                print(
                    f"  {s['sabio_id']}: {s['exitosos']}/{s['total']} exitosos, "
                    f"duración media: {s['duracion_media']:.0f}ms"
                )
        else:
            print("Sin datos aún.")
    else:
        init_db()
        # Verificar tablas
        with get_db() as conn:
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
            print(f"📦 DB: {DB_PATH}")
            print(f"   Tablas: {', '.join(t['name'] for t in tables)}")
            for t in tables:
                count = conn.execute(f"SELECT COUNT(*) as c FROM {t['name']}").fetchone()
                print(f"   {t['name']}: {count['c']} registros")
