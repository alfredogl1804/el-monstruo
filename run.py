"""
Wrapper de arranque para Railway.
Lee PORT desde variable de entorno (Railway lo inyecta).
Evita depender de shell expansion en Dockerfile CMD.
Recomendación del Consejo de Sabios — 13 abril 2026.
"""
import os
import uvicorn

port = int(os.getenv("PORT", "8000"))

if __name__ == "__main__":
    uvicorn.run(
        "kernel.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
