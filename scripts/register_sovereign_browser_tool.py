import psycopg2
import json

DB_URL = "postgresql://postgres.xsumzuhwmivjgftsneov:0SsKDCchJpN5GhO3@aws-1-us-east-2.pooler.supabase.com:5432/postgres?sslmode=require"

conn = psycopg2.connect(DB_URL)
conn.autocommit = True
cur = conn.cursor()

parameters = {
    "type": "object",
    "properties": {
        "url": {"type": "string", "description": "URL http:// o https:// a renderizar"},
        "viewport_preset": {"type": "string", "enum": ["desktop", "mobile"], "default": "desktop"},
        "full_page": {"type": "boolean", "default": True},
        "capture_html": {"type": "boolean", "default": True},
    },
    "required": ["url"],
}

try:
    cur.execute(
        """
        INSERT INTO tool_registry (tool_name, display_name, category, description, risk_level, requires_hitl, is_active, parameters, schema, timeout_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (tool_name) DO UPDATE SET
            description = EXCLUDED.description,
            is_active = EXCLUDED.is_active,
            parameters = EXCLUDED.parameters,
            schema = EXCLUDED.schema,
            updated_at = NOW()
        """,
        (
            "sovereign_browser_render",
            "Sovereign Browser Render",
            "browser_automation",
            "Renderiza URL en browser soberano (Playwright + Chromium dentro del kernel) y devuelve screenshot, HTML y Core Web Vitals. Sprint 84.6.",
            "low",
            False,
            True,
            json.dumps(parameters),
            json.dumps(parameters),
            30000,
        ),
    )
    print("[OK] sovereign_browser_render registrado en tool_registry")
except Exception as e:
    print(f"[ERR] {e}")

cur.close()
conn.close()
