"""
El Monstruo — AG-UI Gateway
============================
Bridges the Flutter mobile app (AG-UI protocol) to the Monstruo kernel on Railway.

Handles:
- WebSocket streaming (AG-UI events ↔ kernel chat/run)
- REST proxy for health, memory, tools, files
- A2UI component generation
- Connection management and heartbeat

Deploy: Railway or same server as kernel.
"""

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── Config ───
KERNEL_URL = os.getenv("KERNEL_URL", "https://el-monstruo-kernel-production.up.railway.app")
GATEWAY_PORT = int(os.getenv("PORT", "8090"))
HEARTBEAT_INTERVAL = 30  # seconds
MAX_CONNECTIONS = 50

# ─── State ───
active_connections: dict[str, WebSocket] = {}
http_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage HTTP client lifecycle."""
    global http_client
    http_client = httpx.AsyncClient(
        base_url=KERNEL_URL,
        timeout=httpx.Timeout(120.0, connect=10.0),
        limits=httpx.Limits(max_connections=100),
    )
    yield
    await http_client.aclose()


app = FastAPI(
    title="El Monstruo AG-UI Gateway",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Models ───
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    source: str = "mobile_app"


class RunRequest(BaseModel):
    directive: str
    thread_id: Optional[str] = None
    source: str = "mobile_app"


# ─── Health ───
@app.get("/health")
async def gateway_health():
    """Gateway health + kernel health proxy."""
    try:
        kernel_resp = await http_client.get("/health")
        kernel_health = kernel_resp.json()
    except Exception as e:
        kernel_health = {"status": "unreachable", "error": str(e)}

    return {
        "gateway": {
            "status": "healthy",
            "version": "0.1.0",
            "active_connections": len(active_connections),
        },
        "kernel": kernel_health,
    }


# ─── REST Proxy Endpoints ───
@app.post("/api/chat")
async def proxy_chat(req: ChatRequest):
    """Proxy chat request to kernel."""
    try:
        resp = await http_client.post(
            "/api/chat",
            json=req.model_dump(),
        )
        return resp.json()
    except httpx.TimeoutException:
        raise HTTPException(504, "Kernel timeout")
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


@app.post("/api/run")
async def proxy_run(req: RunRequest):
    """Proxy run request (LangGraph with tools) to kernel."""
    try:
        resp = await http_client.post(
            "/api/run",
            json=req.model_dump(),
        )
        return resp.json()
    except httpx.TimeoutException:
        raise HTTPException(504, "Kernel timeout")
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


@app.get("/api/memory")
async def proxy_memory():
    """Proxy memory context request."""
    try:
        resp = await http_client.get("/api/memory")
        return resp.json()
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


@app.get("/api/tools")
async def proxy_tools():
    """Proxy available tools list."""
    try:
        resp = await http_client.get("/api/tools")
        return resp.json()
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


@app.get("/api/embrion")
async def proxy_embrion():
    """Proxy embrion status."""
    try:
        resp = await http_client.get("/api/embrion")
        return resp.json()
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


@app.get("/api/files")
async def proxy_files():
    """Proxy files list."""
    try:
        resp = await http_client.get("/api/files")
        return resp.json()
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


# ─── WebSocket Streaming (AG-UI Protocol) ───
@app.websocket("/agui/stream")
async def agui_stream(ws: WebSocket):
    """
    AG-UI WebSocket endpoint.

    Protocol:
    - Client sends: { type: "user_message", content: "...", thread_id: "..." }
    - Server sends: { type: "message_chunk|message_complete|tool_call_start|..." }
    - Heartbeat: server sends { type: "heartbeat" } every 30s
    """
    await ws.accept()
    connection_id = f"conn_{int(time.time() * 1000)}"
    active_connections[connection_id] = ws

    # Start heartbeat task
    heartbeat_task = asyncio.create_task(_heartbeat(ws, connection_id))

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type", "")

            if msg_type == "ping":
                await ws.send_json({"type": "pong"})
                continue

            if msg_type == "user_message":
                # Forward to kernel and stream response back
                asyncio.create_task(
                    _stream_kernel_response(
                        ws=ws,
                        message=data.get("content", ""),
                        thread_id=data.get("thread_id"),
                        connection_id=connection_id,
                    )
                )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        heartbeat_task.cancel()
        active_connections.pop(connection_id, None)


async def _heartbeat(ws: WebSocket, connection_id: str):
    """Send periodic heartbeat to keep connection alive."""
    try:
        while connection_id in active_connections:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            await ws.send_json({"type": "heartbeat", "ts": time.time()})
    except Exception:
        pass


async def _stream_kernel_response(
    ws: WebSocket,
    message: str,
    thread_id: Optional[str],
    connection_id: str,
):
    """
    Send message to kernel and stream the response back via WebSocket.

    Translates kernel SSE/streaming events into AG-UI WebSocket events.
    """
    try:
        # Notify client that processing started
        await ws.send_json({
            "type": "run_start",
            "tool_name": "kernel",
            "timestamp": time.time(),
        })

        # Stream from kernel
        async with http_client.stream(
            "POST",
            "/api/chat/stream",
            json={
                "message": message,
                "thread_id": thread_id,
                "source": "mobile_app",
                "stream": True,
            },
        ) as response:
            message_id = f"msg_{int(time.time() * 1000)}"
            full_content = ""

            async for line in response.aiter_lines():
                if not line.strip():
                    continue

                # Parse SSE format
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break

                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    event_type = event.get("type", "chunk")

                    if event_type in ("chunk", "content"):
                        chunk = event.get("content", event.get("chunk", ""))
                        full_content += chunk
                        await ws.send_json({
                            "type": "message_chunk",
                            "message_id": message_id,
                            "chunk": chunk,
                        })

                    elif event_type == "tool_call":
                        await ws.send_json({
                            "type": "tool_call_start",
                            "tool_name": event.get("name", "unknown"),
                            "args": event.get("args", {}),
                        })

                    elif event_type == "tool_result":
                        await ws.send_json({
                            "type": "tool_call_result",
                            "tool_name": event.get("name", "unknown"),
                            "result": event.get("result", ""),
                        })

                    elif event_type == "genui":
                        await ws.send_json({
                            "type": "genui_component",
                            "id": event.get("id", message_id),
                            "component": event.get("component", {}),
                            "description": event.get("description", ""),
                        })

            # Send complete message
            await ws.send_json({
                "type": "message_complete",
                "id": message_id,
                "content": full_content,
                "model": event.get("model") if 'event' in dir() else None,
                "token_count": event.get("token_count") if 'event' in dir() else None,
                "cost": event.get("cost") if 'event' in dir() else None,
            })

            await ws.send_json({
                "type": "run_complete",
                "tool_name": "kernel",
                "timestamp": time.time(),
            })

    except httpx.TimeoutException:
        await ws.send_json({
            "type": "run_error",
            "tool_name": "kernel",
            "error": "Kernel timeout — el agente está tardando más de lo esperado",
        })
    except Exception as e:
        await ws.send_json({
            "type": "run_error",
            "tool_name": "kernel",
            "error": str(e),
        })


# ─── Push Notification Registration ───
class PushTokenRequest(BaseModel):
    token: str
    platform: str  # "ios" | "android"
    device_id: Optional[str] = None


@app.post("/api/push/register")
async def register_push_token(req: PushTokenRequest):
    """Register FCM/APNs token for push notifications."""
    # TODO: Store in kernel's memory or dedicated DB
    return {"status": "registered", "platform": req.platform}


# ─── Entry Point ───
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=GATEWAY_PORT,
        reload=True,
    )
