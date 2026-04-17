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

# Copy and prepare start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Environment variables
ENV PYTHONPATH=/app:/app/cidp/scripts
ENV PYTHONUNBUFFERED=1

# Railway injects PORT dynamically — do NOT set EXPOSE or hardcode PORT
# start.sh reads $PORT at runtime with fallback to 8080

CMD ["/app/start.sh"]
