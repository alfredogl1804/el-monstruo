FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY cidp/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy CIDP microservice code
COPY cidp/ ./cidp/

# Copy CIDP scripts and config from skill
# These are the 16 validated scripts + 6 config files
COPY cidp/scripts/ ./scripts/
COPY cidp/config/ ./config/

# Create data directories
RUN mkdir -p data/telemetry data/runs

# Environment variables
ENV PYTHONPATH=/app:/app/scripts
ENV PYTHONUNBUFFERED=1

# Expose API port (Railway sets PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the API server
CMD ["python", "-m", "uvicorn", "cidp.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
