FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything into /app/cidp/ so api_server.py's Path(__file__).parent works
# Structure inside container:
#   /app/cidp/__init__.py
#   /app/cidp/api_server.py
#   /app/cidp/client.py
#   /app/cidp/scripts/   (16 validated CIDP scripts)
#   /app/cidp/config/    (6 config files)
#   /app/cidp/data/      (runtime data)
COPY __init__.py ./cidp/__init__.py
COPY api_server.py ./cidp/api_server.py
COPY client.py ./cidp/client.py
COPY scripts/ ./cidp/scripts/
COPY config/ ./cidp/config/

# Create data directories
RUN mkdir -p /app/cidp/data/telemetry /app/cidp/data/runs

# Environment variables
ENV PYTHONPATH=/app:/app/cidp/scripts
ENV PYTHONUNBUFFERED=1

# Expose default port
EXPOSE 8080

# Start script that reads PORT from env at runtime
# Railway injects PORT as env var; uvicorn needs it as --port flag
COPY <<'EOF' /app/start.py
import os, subprocess, sys
port = os.environ.get("PORT", "8080")
sys.exit(subprocess.call([
    sys.executable, "-m", "uvicorn",
    "cidp.api_server:app",
    "--host", "0.0.0.0",
    "--port", port
]))
EOF

CMD ["python", "/app/start.py"]
