FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (retry on transient failures)
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

# Expose API port (Railway sets PORT env var, default 8080)
EXPOSE 8080

# Health check using PORT env var
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:' + __import__('os').environ.get('PORT','8080') + '/health')" || exit 1

# Run the API server — use PORT env var from Railway
CMD ["sh", "-c", "python -m uvicorn cidp.api_server:app --host 0.0.0.0 --port ${PORT:-8080}"]
