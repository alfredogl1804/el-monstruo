"""
El Monstruo — Sprint 51: Ejecutar migración 013 (Error Memory + pgvector)
Conexión directa via psycopg2 al PostgreSQL de Supabase.
"""
import subprocess
import sys
import os

# Ensure psycopg2 is available
try:
    import psycopg2
except ImportError:
    print("Installing psycopg2-binary...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
    import psycopg2

# Supabase connection
DB_HOST = "aws-1-us-east-2.pooler.supabase.com"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres.xsumzuhwmivjgftsneov"
DB_PASS = "0SsKDCchJpN5GhO3"


def main():
    print("╔══════════════════════════════════════════════════════╗")
    print("║  Sprint 51 — Migración 013 (Error Memory + pgvector) ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    # Read the SQL file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(script_dir, "013_error_memory_table.sql")

    with open(sql_path, "r") as f:
        migration_sql = f.read()

    print(f"✓ SQL leído: {len(migration_sql)} caracteres")

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

        # Execute migration 013
        print("\n── Migración 013: error_memory + pgvector ──")
        cur.execute(migration_sql)
        print("✓ Migración 013 ejecutada")

        # Verify pgvector extension
        print("\n── Verificaciones ──")
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        ext = cur.fetchall()
        if ext:
            print("✓ pgvector: ACTIVO")
        else:
            print("⚠ pgvector: NO encontrado (modo degradado)")

        # Verify error_memory table
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'error_memory'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        if columns:
            print(f"✓ Tabla error_memory: {len(columns)} columnas")
            for col in columns:
                print(f"  • {col[0]:25s} {col[1]}")
        else:
            print("✗ ERROR: error_memory no encontrada")

        # Verify error_memory_patterns table
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'error_memory_patterns'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        if columns:
            print(f"✓ Tabla error_memory_patterns: {len(columns)} columnas")
        else:
            print("✗ ERROR: error_memory_patterns no encontrada")

        # Verify seed data
        cur.execute("SELECT error_signature, error_type, status FROM error_memory;")
        seeds = cur.fetchall()
        if seeds:
            print(f"✓ Reglas semilla: {len(seeds)} filas")
            for s in seeds:
                print(f"  • {s[0]:40s} [{s[1]}] status={s[2]}")
        else:
            print("⚠ Sin reglas semilla (INSERT pudo haber fallado)")

        # Verify RPC function
        cur.execute("""
            SELECT routine_name FROM information_schema.routines
            WHERE routine_name = 'search_similar_errors';
        """)
        rpc = cur.fetchall()
        if rpc:
            print("✓ RPC search_similar_errors: CREADA")
        else:
            print("⚠ RPC search_similar_errors: no encontrada")

        # Verify indexes
        cur.execute("SELECT indexname FROM pg_indexes WHERE tablename = 'error_memory';")
        indexes = cur.fetchall()
        print(f"✓ Indexes error_memory: {[i[0] for i in indexes]}")

        cur.close()
        conn.close()
        print("\n✓ Migración 013 completa.")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
