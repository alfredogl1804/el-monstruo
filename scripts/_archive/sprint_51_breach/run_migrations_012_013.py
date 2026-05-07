"""
El Despertador — Sprint 81: Ejecutar migraciones 012 + 013
Conexión directa via psycopg2 al PostgreSQL de Supabase.
"""
import subprocess
import sys

# Ensure psycopg2 is available
try:
    import psycopg2
except ImportError:
    print("Installing psycopg2-binary...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
    import psycopg2

# Supabase connection (from Railway SUPABASE_DB_URL)
DB_HOST = "aws-1-us-east-2.pooler.supabase.com"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres.xsumzuhwmivjgftsneov"
DB_PASS = "0SsKDCchJpN5GhO3"

MIGRATION_012 = """
CREATE TABLE IF NOT EXISTS magna_cache (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    cache_key       TEXT NOT NULL UNIQUE,
    tool_name       TEXT NOT NULL,
    query           TEXT NOT NULL,
    result          JSONB NOT NULL DEFAULT '{}',
    ttl_seconds     INTEGER NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL,
    hit_count       INTEGER NOT NULL DEFAULT 0,
    last_hit_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_magna_cache_key ON magna_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_magna_cache_expires ON magna_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_magna_cache_tool ON magna_cache(tool_name);

ALTER TABLE magna_cache ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'magna_cache' AND policyname = 'service_role_all'
    ) THEN
        CREATE POLICY service_role_all ON magna_cache
            FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;
END $$;

COMMENT ON TABLE magna_cache IS 'Sprint 81: Magna Classifier — cache de clasificaciones con TTL';
COMMENT ON COLUMN magna_cache.cache_key IS 'Hash determinístico de query normalizada + tool_name';
COMMENT ON COLUMN magna_cache.result IS 'Resultado: {route, score, suggested_tool, category}';
COMMENT ON COLUMN magna_cache.ttl_seconds IS 'TTL en segundos: APIs=86400, precios=3600, trending=21600';
COMMENT ON COLUMN magna_cache.hit_count IS 'Contador de consultas exitosas';
"""


def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  Sprint 81 — Migraciones 012 (Magna Cache)  ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    try:
        print(f"Conectando a {DB_HOST}:{DB_PORT}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            sslmode="require",
            connect_timeout=15,
        )
        conn.autocommit = True
        cur = conn.cursor()
        print("✓ Conectado a Supabase PostgreSQL")

        # Execute migration 012
        print("\n── Migración 012: magna_cache ──")
        cur.execute(MIGRATION_012)
        print("✓ Migración 012 ejecutada")

        # Verify magna_cache
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'magna_cache'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        if columns:
            print(f"✓ Tabla magna_cache: {len(columns)} columnas")
            for col in columns:
                print(f"  • {col[0]:20s} {col[1]}")
        else:
            print("✗ ERROR: magna_cache no encontrada")

        # Verify indexes
        cur.execute("SELECT indexname FROM pg_indexes WHERE tablename = 'magna_cache';")
        indexes = cur.fetchall()
        print(f"✓ Indexes: {[i[0] for i in indexes]}")

        # Verify RLS
        cur.execute("SELECT polname FROM pg_policies WHERE tablename = 'magna_cache';")
        policies = cur.fetchall()
        print(f"✓ RLS policies: {[p[0] for p in policies]}")

        cur.close()
        conn.close()
        print("\n✓ Migraciones completas.")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\n⚠ Ejecuta manualmente en Supabase SQL Editor:")
        print("  1. Abre https://supabase.com/dashboard/project/xsumzuhwmivjgftsneov/sql/new")
        print("  2. Pega el contenido de scripts/012_magna_cache_table.sql")
        print("  3. Click 'Run'")


if __name__ == "__main__":
    main()
