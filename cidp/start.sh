#!/bin/bash
exec python -m uvicorn cidp.api_server:app --host 0.0.0.0 --port ${PORT:-8080}
