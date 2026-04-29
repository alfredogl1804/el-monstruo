# El Monstruo — AG-UI Gateway

Servidor que traduce entre el protocolo AG-UI (usado por la app Flutter) y la API del kernel de El Monstruo en Railway.

## Funciones

- **WebSocket streaming** — Recibe mensajes del usuario, los envía al kernel, y retransmite la respuesta token por token
- **REST proxy** — Endpoints para health, memory, tools, files, embrion
- **AG-UI events** — Traduce eventos del kernel (tool_call, genui, etc.) al formato AG-UI
- **Heartbeat** — Mantiene conexiones WebSocket vivas
- **Push registration** — Registra tokens FCM/APNs para notificaciones

## Deploy

```bash
# Local
pip install -r requirements.txt
python server.py

# Docker
docker build -t monstruo-gateway .
docker run -p 8090:8090 -e KERNEL_URL=https://... monstruo-gateway

# Railway
# Apuntar root directory a apps/mobile/gateway/
```

## Variables de Entorno

| Variable | Default | Descripción |
|---|---|---|
| `KERNEL_URL` | `https://el-monstruo-kernel-production.up.railway.app` | URL del kernel |
| `PORT` | `8090` | Puerto del gateway |
