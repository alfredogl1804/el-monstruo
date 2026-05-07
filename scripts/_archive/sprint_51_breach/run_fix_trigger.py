"""
Sprint 81.5: Fix the trg_budget_tracker trigger that references NEW.cycles
(column doesn't exist in task_plans — should use revision_count).
"""
import psycopg2

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

    # ── Fix: Replace NEW.cycles with NEW.revision_count in trigger function ──
    print("=== Fixing trg_budget_tracker trigger function ===")

    # First, get the full current function source
    cur.execute("""
        SELECT prosrc FROM pg_proc WHERE proname = 'update_budget_on_plan_change';
    """)
    row = cur.fetchone()
    if row:
        old_src = row[0]
        print(f"  Current function source ({len(old_src)} chars)")
        print(f"  Contains 'cycles': {'cycles' in old_src}")

        # Replace cycles with revision_count
        new_src = old_src.replace("NEW.cycles", "NEW.revision_count")
        print(f"  Replaced NEW.cycles -> NEW.revision_count")

        # Recreate the function
        cur.execute(f"""
            CREATE OR REPLACE FUNCTION update_budget_on_plan_change()
            RETURNS TRIGGER AS $$
            {new_src}
            $$ LANGUAGE plpgsql;
        """)
        print("  OK: Function updated")

        # Verify
        cur.execute("""
            SELECT prosrc FROM pg_proc WHERE proname = 'update_budget_on_plan_change';
        """)
        verify = cur.fetchone()
        if verify:
            print(f"  Verification: 'cycles' in new source: {'cycles' in verify[0]}")
            print(f"  Verification: 'revision_count' in new source: {'revision_count' in verify[0]}")
    else:
        print("  ERROR: Function update_budget_on_plan_change not found")

    cur.close()
    conn.close()
    print("\n=== Trigger fix complete ===")

if __name__ == "__main__":
    run()
