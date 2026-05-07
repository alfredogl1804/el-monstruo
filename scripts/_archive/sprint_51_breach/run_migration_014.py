"""
Run migration 014: ALTER TABLE verification_results ADD COLUMN cost_usd
Also investigate task_plans.cycles trigger.
"""
import psycopg2

# Direct Supabase connection (session mode)
CONN = {
    "host": "aws-1-us-east-2.pooler.supabase.com",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres.xsumzuhwmivjgftsneov",
    "password": "0SsKDCchJpN5GhO3",
    "sslmode": "require",
    "options": "-c statement_timeout=30000",
}

def run():
    conn = psycopg2.connect(**CONN)
    conn.autocommit = True
    cur = conn.cursor()

    # ── Fix 1: verification_results.cost_usd ──
    print("=== Fix 1: verification_results.cost_usd ===")
    try:
        cur.execute("""
            ALTER TABLE verification_results
            ADD COLUMN IF NOT EXISTS cost_usd NUMERIC(10,6) DEFAULT 0;
        """)
        print("OK: cost_usd column added (or already exists)")
    except Exception as e:
        print(f"ERROR: {e}")

    # Verify
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'verification_results' AND column_name = 'cost_usd';
    """)
    row = cur.fetchone()
    print(f"  Verification: {row}")

    # ── Investigate: task_plans.cycles trigger ──
    print("\n=== Investigating task_plans.cycles ===")

    # Check if cycles column exists
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'task_plans' AND column_name = 'cycles';
    """)
    row = cur.fetchone()
    print(f"  Column 'cycles' exists: {row is not None}")

    # Check for triggers on task_plans
    cur.execute("""
        SELECT trigger_name, event_manipulation, action_statement
        FROM information_schema.triggers
        WHERE event_object_table = 'task_plans';
    """)
    triggers = cur.fetchall()
    if triggers:
        print(f"  Triggers found: {len(triggers)}")
        for t in triggers:
            print(f"    - {t[0]} ({t[1]}): {t[2][:200]}")
    else:
        print("  No triggers on task_plans")

    # Check for RPC/functions that reference task_plans
    cur.execute("""
        SELECT routine_name
        FROM information_schema.routines
        WHERE routine_definition LIKE '%task_plans%' AND routine_schema = 'public';
    """)
    funcs = cur.fetchall()
    if funcs:
        print(f"  Functions referencing task_plans: {[f[0] for f in funcs]}")
    else:
        print("  No functions reference task_plans")

    # The error says "record new has no field cycles" — this is a trigger error.
    # Check if there's a trigger that references 'cycles'
    cur.execute("""
        SELECT routine_name, routine_definition
        FROM information_schema.routines
        WHERE routine_schema = 'public'
        AND routine_definition LIKE '%cycles%';
    """)
    cycle_funcs = cur.fetchall()
    if cycle_funcs:
        print(f"\n  Functions referencing 'cycles':")
        for f in cycle_funcs:
            print(f"    - {f[0]}: {f[1][:300]}")
    else:
        print("  No functions reference 'cycles'")

    # Also check pg_trigger directly
    cur.execute("""
        SELECT t.tgname, p.proname, p.prosrc
        FROM pg_trigger t
        JOIN pg_class c ON t.tgrelid = c.oid
        JOIN pg_proc p ON t.tgfoid = p.oid
        WHERE c.relname = 'task_plans'
        AND NOT t.tgisinternal;
    """)
    pg_triggers = cur.fetchall()
    if pg_triggers:
        print(f"\n  pg_trigger entries for task_plans:")
        for t in pg_triggers:
            print(f"    - trigger: {t[0]}, function: {t[1]}")
            print(f"      source: {t[2][:500]}")
    else:
        print("  No pg_trigger entries for task_plans")

    cur.close()
    conn.close()
    print("\n=== Migration 014 complete ===")

if __name__ == "__main__":
    run()
