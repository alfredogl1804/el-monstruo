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

# Railway injects PORT dynamically as env var.
# Use python __main__ block which reads os.environ.get("PORT", "8080")
# This avoids all shell variable expansion issues.
CMD ["python", "-c", "import os; port = int(os.environ.get('PORT', '8080')); import uvicorn; uvicorn.run('cidp.api_server:app', host='0.0.0.0', port=port, log_level='info')"]
