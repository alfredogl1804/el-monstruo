"""
Sprint 82 — Run migration 015: brand_compliance_log table.
Execute from repo root: python3 scripts/run_migration_015.py
"""

import os
import sys

import psycopg2


def main():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        # Fallback to direct connection params
        db_url = (
            "postgresql://postgres.xsumzuhwmivjgftsneov:0SsKDCchJpN5GhO3"
            "@aws-1-us-east-2.pooler.supabase.com:5432/postgres"
            "?sslmode=require"
        )

    sql_path = os.path.join(os.path.dirname(__file__), "015_brand_compliance_log.sql")
    with open(sql_path) as f:
        sql = f.read()

    print(f"Connecting to Supabase...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            print("Migration 015 executed successfully.")

            # Verify
            cur.execute(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = 'brand_compliance_log' ORDER BY ordinal_position"
            )
            cols = cur.fetchall()
            print(f"\nbrand_compliance_log columns ({len(cols)}):")
            for name, dtype in cols:
                print(f"  {name}: {dtype}")
    finally:
        conn.close()

    print("\nDone.")


if __name__ == "__main__":
    main()
