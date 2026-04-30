"""
El Monstruo — AG-UI Mobile Gateway
====================================
Bridges the Flutter mobile app to the Monstruo kernel on Railway.

The kernel already exposes:
  - POST /v1/agui/run       → AG-UI SSE streaming (main chat)
  - GET  /v1/agui/info      → AG-UI capabilities
  - GET  /v1/memory/stats   → Memory statistics
  - POST /v1/memory/search  → Semantic memory search
  - GET  /v1/memory/boot    → Boot context
  - GET  /v1/embrion/*      → Embrión status
  - GET  /v1/usage/*        → FinOps data
  - GET  /health            → Kernel health

This gateway:
  1. Translates kernel SSE → WebSocket (for Flutter real-time)
  2. Adds connection management, heartbeat, reconnection
  3. Handles push notification registration
  4. Provides mobile-optimized REST wrappers

Deploy: Railway (same project, separate service).
"""

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from typing import Optional
from uuid import uuid4

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ─── Config ───
KERNEL_URL = os.getenv("KERNEL_URL", "https://el-monstruo-kernel-production.up.railway.app")
KERNEL_API_KEY = os.getenv("KERNEL_API_KEY", "")
GATEWAY_PORT = int(os.getenv("PORT", "8090"))
HEARTBEAT_INTERVAL = 25  # seconds (< Railway's 30s timeout)
MAX_CONNECTIONS = 50

# ─── State ───
active_connections: dict[str, WebSocket] = {}
http_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage HTTP client lifecycle."""
    global http_client
    headers = {}
    if KERNEL_API_KEY:
        headers["X-API-Key"] = KERNEL_API_KEY
    http_client = httpx.AsyncClient(
        base_url=KERNEL_URL,
        headers=headers,
        timeout=httpx.Timeout(180.0, connect=10.0, read=180.0),
        limits=httpx.Limits(max_connections=100),
    )
    yield
    await http_client.aclose()


app = FastAPI(
    title="El Monstruo Mobile Gateway",
    version="0.2.0",
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
class ChatMessage(BaseModel):
    role: str = "user"
    content: str


class AGUIRequest(BaseModel):
    """Matches kernel's AGUIRunRequest format."""
    thread_id: Optional[str] = None
    run_id: Optional[str] = None
    messages: list[dict] = Field(default_factory=list)
    tools: list[dict] = Field(default_factory=list)
    context: list[dict] = Field(default_factory=list)
    forwarded_props: dict = Field(default_factory=dict)


class SimpleChatRequest(BaseModel):
    """Simplified chat request for mobile — auto-wraps into AG-UI format."""
    message: str
    thread_id: Optional[str] = None


class PushTokenRequest(BaseModel):
    token: str
    platform: str  # "ios" | "android"
    device_id: Optional[str] = None


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
            "version": "0.2.0",
            "active_connections": len(active_connections),
        },
        "kernel": kernel_health,
    }


# ─── REST Endpoints (Mobile-optimized wrappers) ───

@app.post("/api/chat")
async def mobile_chat(req: SimpleChatRequest):
    """
    Simple chat endpoint for mobile.
    Wraps message into AG-UI format and calls kernel /v1/agui/run.
    Returns full response (non-streaming) for simple use cases.
    """
    agui_payload = {
        "thread_id": req.thread_id or str(uuid4()),
        "run_id": str(uuid4()),
        "messages": [{"role": "user", "content": req.message}],
        "forwarded_props": {"user_id": "alfredo", "source": "mobile_app"},
    }

    try:
        # Call kernel AG-UI endpoint (SSE) and collect full response
        full_response = ""
        tool_calls = []

        async with http_client.stream("POST", "/v1/agui/run", json=agui_payload) as response:
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                try:
                    event = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                event_type = event.get("type", "")
                if event_type == "TEXT_MESSAGE_CONTENT":
                    full_response += event.get("delta", "")
                elif event_type == "TOOL_CALL_START":
                    tool_calls.append(event.get("toolCallName", "unknown"))

        return {
            "response": full_response,
            "thread_id": agui_payload["thread_id"],
            "tool_calls": tool_calls,
        }

    except httpx.TimeoutException:
        raise HTTPException(504, "Kernel timeout")
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


@app.get("/api/memory/stats")
async def proxy_memory_stats():
    """Proxy memory stats from kernel."""
    try:
        resp = await http_client.get("/v1/memory/stats")
        return resp.json()
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


@app.post("/api/memory/search")
async def proxy_memory_search(query: dict):
    """Proxy semantic memory search."""
    try:
        resp = await http_client.post("/v1/memory/search/semantic", json=query)
        return resp.json()
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


@app.get("/api/embrion")
async def proxy_embrion():
    """Proxy embrion status."""
    try:
        resp = await http_client.get("/v1/embrion/status")
        return resp.json()
    except Exception as e:
        # Fallback to health endpoint
        try:
            resp = await http_client.get("/health")
            health = resp.json()
            embrion_data = health.get("components", {}).get("embrion", {})
            return embrion_data if embrion_data else {"status": "unknown"}
        except Exception:
            raise HTTPException(502, f"Kernel error: {e}")


@app.get("/api/finops")
async def proxy_finops(period: str = "today"):
    """Proxy FinOps dashboard — Sprint 38: usa /v1/finops/summary real."""
    try:
        resp = await http_client.get("/v1/finops/summary")
        return resp.json()
    except Exception as e:
        # Fallback al status básico
        try:
            resp = await http_client.get("/v1/finops/status")
            return resp.json()
        except Exception:
            raise HTTPException(502, f"Kernel error: {e}")


@app.get("/api/moc")
async def proxy_moc_status():
    """Proxy MOC status and latest insights — Sprint 38."""
    try:
        resp = await http_client.get("/v1/moc/status")
        status = resp.json()
        # Enrich with latest insights
        try:
            insights_resp = await http_client.get("/v1/moc/insights?limit=5")
            status["latest_insights"] = insights_resp.json().get("insights", [])
        except Exception:
            status["latest_insights"] = []
        return status
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


@app.post("/api/moc/sintetizar")
async def proxy_moc_sintetizar():
    """Trigger manual MOC synthesis — Sprint 38."""
    try:
        resp = await http_client.post("/v1/moc/sintetizar")
        return resp.json()
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


@app.get("/api/tools")
async def proxy_tools():
    """Proxy available tools list."""
    try:
        resp = await http_client.get("/v1/tools")
        return resp.json()
    except httpx.HTTPStatusError:
        # Fallback: extract from health
        try:
            resp = await http_client.get("/health")
            health = resp.json()
            components = health.get("components", {})
            tools = [k for k, v in components.items() if v.get("status") == "active"]
            return {"tools": tools}
        except Exception as e:
            raise HTTPException(502, f"Kernel error: {e}")
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


@app.get("/api/agui/info")
async def proxy_agui_info():
    """Proxy AG-UI adapter info."""
    try:
        resp = await http_client.get("/v1/agui/info")
        return resp.json()
    except Exception as e:
        raise HTTPException(502, f"Kernel error: {e}")


# ─── WebSocket Streaming (AG-UI → WS bridge for Flutter) ───

@app.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    """
    WebSocket endpoint for Flutter real-time chat.

    Protocol:
    - Client sends: { "type": "message", "content": "...", "thread_id": "..." }
    - Server sends AG-UI events translated to WS frames:
      { "type": "text_chunk|tool_start|tool_end|run_start|run_end|error|heartbeat" }
    """
    await ws.accept()
    connection_id = f"conn_{int(time.time() * 1000)}"
    active_connections[connection_id] = ws

    # Start heartbeat
    heartbeat_task = asyncio.create_task(_heartbeat(ws, connection_id))

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type", "")

            if msg_type == "ping":
                await ws.send_json({"type": "pong", "ts": time.time()})
                continue

            if msg_type == "message":
                # Stream kernel response via AG-UI SSE → WebSocket
                asyncio.create_task(
                    _stream_agui_to_ws(
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


async def _stream_agui_to_ws(
    ws: WebSocket,
    message: str,
    thread_id: Optional[str],
    connection_id: str,
):
    """
    Call kernel /v1/agui/run (SSE) and translate events to WebSocket frames.
    """
    thread_id = thread_id or str(uuid4())
    run_id = str(uuid4())

    agui_payload = {
        "thread_id": thread_id,
        "run_id": run_id,
        "messages": [{"role": "user", "content": message}],
        "forwarded_props": {"user_id": "alfredo", "source": "mobile_app"},
    }

    try:
        await ws.send_json({
            "type": "run_start",
            "run_id": run_id,
            "thread_id": thread_id,
            "ts": time.time(),
        })

        full_content = ""
        message_id = str(uuid4())

        async with http_client.stream(
            "POST", "/v1/agui/run",
            json=agui_payload,
            headers={"Accept": "text/event-stream", "Cache-Control": "no-cache"},
        ) as response:
            # Use aiter_bytes + manual SSE parsing to avoid Railway buffering
            sse_buffer = ""
            async for raw_bytes in response.aiter_bytes():
                sse_buffer += raw_bytes.decode("utf-8", errors="replace")
                while "\n\n" in sse_buffer:
                    frame, sse_buffer = sse_buffer.split("\n\n", 1)
                    for line in frame.split("\n"):
                        if not line.startswith("data: "):
                            continue
                        data_str = line[6:]
                        try:
                            event = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

                        # Check if connection still active
                        if connection_id not in active_connections:
                            return

                        event_type = event.get("type", "")

                        if event_type == "THINKING_STATE":
                            # Forward thinking/routing metadata to Flutter
                            await ws.send_json({
                                "type": "thinking_state",
                                "message_id": event.get("messageId", message_id),
                                "intent": event.get("intent", ""),
                                "model": event.get("model", ""),
                                "enriched": event.get("enriched", False),
                                "memories_found": event.get("memoriesFound", 0),
                                "ts": time.time(),
                            })

                        elif event_type == "TEXT_MESSAGE_CONTENT":
                            delta = event.get("delta", "")
                            full_content += delta
                            await ws.send_json({
                                "type": "text_chunk",
                                "message_id": message_id,
                                "content": delta,
                            })

                        elif event_type == "TEXT_MESSAGE_START":
                            message_id = event.get("messageId", message_id)
                            await ws.send_json({
                                "type": "message_start",
                                "message_id": message_id,
                            })

                        elif event_type == "TEXT_MESSAGE_END":
                            await ws.send_json({
                                "type": "message_end",
                                "message_id": message_id,
                                "content": full_content,
                            })

                        elif event_type == "TOOL_CALL_START":
                            await ws.send_json({
                                "type": "tool_start",
                                "tool_name": event.get("toolCallName", "unknown"),
                                "tool_call_id": event.get("toolCallId", ""),
                            })

                        elif event_type == "TOOL_CALL_ARGS":
                            await ws.send_json({
                                "type": "tool_args",
                                "tool_call_id": event.get("toolCallId", ""),
                                "args": event.get("delta", ""),
                            })

                        elif event_type == "TOOL_CALL_END":
                            await ws.send_json({
                                "type": "tool_end",
                                "tool_call_id": event.get("toolCallId", ""),
                                "result": event.get("result", ""),
                            })

                        elif event_type == "RUN_ERROR":
                            await ws.send_json({
                                "type": "error",
                                "message": event.get("message", "Unknown error"),
                            })
                            return

        # Run complete
        await ws.send_json({
            "type": "run_end",
            "run_id": run_id,
            "thread_id": thread_id,
            "content": full_content,
            "ts": time.time(),
        })

    except httpx.TimeoutException:
        await ws.send_json({
            "type": "error",
            "message": "Kernel timeout — el agente está tardando más de lo esperado",
        })
    except Exception as e:
        await ws.send_json({
            "type": "error",
            "message": f"Gateway error: {str(e)}",
        })


# ─── Push Notification Registration ───

@app.post("/api/push/register")
async def register_push_token(req: PushTokenRequest):
    """Register FCM/APNs token for push notifications."""
    # Store in kernel memory for later use
    try:
        await http_client.post(
            "/v1/memory/thoughts",
            json={
                "content": f"Push token registered: platform={req.platform}, device={req.device_id}",
                "type": "system",
                "metadata": {
                    "push_token": req.token,
                    "platform": req.platform,
                    "device_id": req.device_id,
                },
            },
        )
    except Exception:
        pass  # Non-critical

    return {"status": "registered", "platform": req.platform}


# ─── Entry Point ───
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=GATEWAY_PORT,
        reload=os.getenv("ENV", "production") != "production",
    )
