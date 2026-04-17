"""
CIDP Entrypoint — Reads PORT from environment and starts uvicorn.
Railway injects PORT as an env var; this script reads it programmatically
to avoid all shell variable expansion issues.
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"[CIDP] Starting on port {port}...")
    uvicorn.run(
        "cidp.api_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
