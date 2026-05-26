"""Inspección cruda del schema de catastro_agentes y catastro_tronos_agentes."""

import os

import psycopg

DB_URL = os.environ["SUPABASE_DB_URL"]

with psycopg.connect(DB_URL) as conn, conn.cursor() as cur:
    print("=" * 70)
    print("SCHEMA catastro_agentes")
    print("=" * 70)
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'catastro_agentes'
        ORDER BY ordinal_position
    """)
    for col, dt, n, d in cur.fetchall():
        print(f"  {col:<35} {dt:<25} null={n} default={d}")

    print("\n" + "=" * 70)
    print("VIEW catastro_tronos_agentes (columnas)")
    print("=" * 70)
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'catastro_tronos_agentes'
        ORDER BY ordinal_position
    """)
    rows = cur.fetchall()
    if not rows:
        print("  Vista catastro_tronos_agentes NO existe en information_schema")
    for col, dt in rows:
        print(f"  {col:<35} {dt}")

    print("\n" + "=" * 70)
    print("PRIMERAS 5 FILAS DE catastro_agentes (todas las columnas)")
    print("=" * 70)
    cur.execute("SELECT * FROM catastro_agentes LIMIT 3")
    cols = [d[0] for d in cur.description]
    for row in cur.fetchall():
        print()
        for c, v in zip(cols, row):
            v_str = str(v)[:80] if v is not None else "NULL"
            print(f"  {c:<35} = {v_str}")

    print("\n" + "=" * 70)
    print("CHECK constraints en catastro_agentes")
    print("=" * 70)
    cur.execute("""
        SELECT conname, pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conrelid = 'catastro_agentes'::regclass AND contype = 'c'
        ORDER BY conname
    """)
    for name, defn in cur.fetchall():
        print(f"  {name}")
        print(f"    {defn}")

    print("\n" + "=" * 70)
    print("CONTEO total filas catastro_agentes")
    print("=" * 70)
    cur.execute("SELECT COUNT(*) FROM catastro_agentes")
    print(f"  Total: {cur.fetchone()[0]}")
