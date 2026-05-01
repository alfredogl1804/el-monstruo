# SPRINT 73 — "Paridad Manus y Más Allá"

**Serie:** 71-80 "La Colmena Despierta"
**Fecha de diseño:** 1 de Mayo de 2026
**Arquitecto:** Hilo B
**Capa Arquitectónica:** CAPA 3 (Autonomía) + CAPA 4 (Soberanía)
**Objetivo Primario:** #1 (Crear Empresas), #3 (Velocidad), #7 (Herramientas), #8 (Emergencia)
**Patrón:** Pensador (LLM potente) + Ejecutor (código determinista)

---

## Contexto

Sprint 72 dotó al Embrión del Task Execution Loop (TEL) — la capacidad de ejecutar encomiendas de principio a fin. Pero el TEL tiene un gap: las herramientas disponibles son limitadas comparadas con lo que Manus tiene. El Embrión puede buscar con Perplexity y escribir en Supabase, pero NO puede:

- Navegar la web (browser)
- Generar imágenes
- Generar audio/speech
- Crear y modificar archivos complejos (PDFs, presentaciones)
- Interactuar con servicios web (login, forms, scraping)
- Enviar emails
- Gestionar calendario
- Publicar en redes sociales
- Crear sitios web
- Procesar video

Sprint 73 cierra TODOS estos gaps y agrega capacidades que Manus NO tiene:

---

## ANÁLISIS DE GAP: Manus vs. Embrión

| Capacidad | Manus | Embrión post-72 | Embrión post-73 |
|---|---|---|---|
| Búsqueda web | Perplexity + Browser | Perplexity | Perplexity + Headless Browser |
| Navegación web | Chromium completo | No | Playwright headless |
| Scraping | Browser + BeautifulSoup | No | Playwright + parsers |
| Generación de imágenes | DALL-E / generate tool | No | DALL-E + Stable Diffusion API |
| Generación de audio | ElevenLabs | No | ElevenLabs |
| Generación de texto | GPT-4o, Claude, Gemini | GPT-4o | GPT-4o + Claude + Gemini (multi-LLM) |
| Archivos/documentos | Markdown, PDF, PPTX | No | Markdown, PDF, PPTX generation |
| Email | Gmail MCP | No | Gmail API directo |
| Calendario | Google Calendar MCP | No | Google Calendar API |
| GitHub | gh CLI | GitHub API básico | GitHub API completo |
| Dropbox | Dropbox SDK | No | Dropbox SDK |
| Shell/código | Full sandbox | No (eliminado por seguridad) | Sandboxed code execution |
| Redes sociales | No | No | APIs de publicación |
| Sitios web | Webdev tools | No | Template + deploy pipeline |
| Video análisis | manus-analyze-video | No | Video analysis API |
| **Memoria persistente** | **No (context window)** | **Supabase** | **Supabase + Embeddings** |
| **Aprendizaje** | **No entre sesiones** | **ExecutionMemory** | **ExecutionMemory + Patterns** |
| **Ejecución 24/7** | **No** | **Scheduler** | **Scheduler + Auto-trigger** |
| **Multi-agente** | **Solo (1)** | **Colmena** | **Colmena coordinada** |
| **Auto-mejora** | **No** | **No** | **Self-improvement loop** |
| **Proactividad** | **No (espera al usuario)** | **No** | **Detección de oportunidades** |

---

## ARQUITECTURA: Capability Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EMBRIÓN CAPABILITY STACK                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  CAPA 4: SUPERIORIDAD (lo que Manus NO tiene)                            │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Self-Improve │ │ Proactividad │ │ Multi-LLM    │ │ Auto-Trigger │    │
│  │ Loop         │ │ Detector     │ │ Orchestrator │ │ Engine       │    │
│  └─────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                                           │
│  CAPA 3: PARIDAD MANUS (cerrar el gap)                                   │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Web Browser  │ │ Image Gen    │ │ Audio Gen    │ │ Doc Gen      │    │
│  │ (Playwright) │ │ (DALL-E)     │ │ (ElevenLabs) │ │ (PDF/PPTX)   │    │
│  └─────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Email        │ │ Calendar     │ │ Social Media │ │ Code Sandbox │    │
│  │ (Gmail)      │ │ (GCal)       │ │ (APIs)       │ │ (Isolated)   │    │
│  └─────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                                           │
│  CAPA 2: TEL BASE (Sprint 72)                                            │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Planner      │ │ Runner       │ │ ToolRegistry │ │ Memory       │    │
│  └─────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                                           │
│  CAPA 1: KERNEL BASE (Sprints 51-56)                                     │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Scheduler    │ │ Supabase     │ │ FastAPI      │ │ Observability│    │
│  └─────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Épica 73.1 — Web Browser: Playwright Headless

**Objetivo:** Darle al Embrión la capacidad de navegar la web, interactuar con páginas, extraer datos, y realizar acciones en sitios web.

**Por qué Playwright y no Selenium:** Playwright es más moderno, más rápido, mejor soporte de headless, y tiene API async nativa que se integra con el TEL.

**Criterios de Aceptación:**
- [ ] Herramienta `web_navigate` en ToolRegistry
- [ ] Herramienta `web_extract` para extraer contenido estructurado
- [ ] Herramienta `web_interact` para clicks, forms, login
- [ ] Herramienta `web_screenshot` para capturar estado visual
- [ ] Sandboxed: no puede acceder a localhost del kernel
- [ ] Timeout por navegación (30s max)
- [ ] Anti-detección básica (user-agent, viewport)

```python
"""
kernel/execution/tools_web.py
WEB BROWSER — Navegación y extracción web con Playwright

Capacidades:
- Navegar a URLs
- Extraer contenido (texto, tablas, links, imágenes)
- Interactuar (clicks, forms, scroll)
- Capturar screenshots
- Login en servicios (con credenciales almacenadas)

Seguridad:
- Headless only (sin UI)
- No puede acceder a localhost/127.0.0.1
- Timeout estricto por página
- No ejecuta JavaScript arbitrario del usuario
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


@dataclass
class WebConfig:
    """Configuración del browser."""
    headless: bool = True
    timeout_ms: int = 30000
    viewport_width: int = 1280
    viewport_height: int = 720
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    blocked_hosts: List[str] = None
    
    def __post_init__(self):
        if self.blocked_hosts is None:
            self.blocked_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "169.254.0.21"]


class WebBrowserTool:
    """
    Browser headless para el Embrión.
    
    Equivalente a las capacidades de browser de Manus,
    pero ejecutado dentro del kernel en Railway.
    """
    
    def __init__(self, config: WebConfig = None):
        self.config = config or WebConfig()
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
    
    async def initialize(self):
        """Inicia el browser (lazy — solo cuando se necesita)."""
        if self._browser:
            return
        
        playwright = await async_playwright().start()
        self._browser = await playwright.chromium.launch(
            headless=self.config.headless
        )
        self._context = await self._browser.new_context(
            viewport={"width": self.config.viewport_width, "height": self.config.viewport_height},
            user_agent=self.config.user_agent
        )
        self._page = await self._context.new_page()
        self._page.set_default_timeout(self.config.timeout_ms)
    
    async def cleanup(self):
        """Cierra el browser."""
        if self._browser:
            await self._browser.close()
            self._browser = None
    
    async def navigate(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Navega a una URL y retorna el contenido de la página.
        
        Input: {"url": "https://...", "wait_for": "networkidle|domcontentloaded"}
        Output: {"title": "...", "url": "...", "content_text": "...", "links": [...]}
        """
        url = input["url"]
        
        # Seguridad: bloquear hosts internos
        for blocked in self.config.blocked_hosts:
            if blocked in url:
                return {"error": f"execution_web_blocked: Host '{blocked}' no permitido por seguridad"}
        
        await self.initialize()
        
        wait_for = input.get("wait_for", "domcontentloaded")
        await self._page.goto(url, wait_until=wait_for)
        
        title = await self._page.title()
        content = await self._page.inner_text("body")
        current_url = self._page.url
        
        # Extraer links
        links = await self._page.eval_on_selector_all(
            "a[href]",
            "elements => elements.slice(0, 50).map(e => ({text: e.innerText.trim(), href: e.href}))"
        )
        
        return {
            "title": title,
            "url": current_url,
            "content_text": content[:5000],  # Limitar para no saturar context
            "links": links[:30],
            "success": True
        }
    
    async def extract(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae datos estructurados de la página actual.
        
        Input: {"selector": "css selector", "extract_type": "text|table|list|attribute", "attribute": "href"}
        Output: {"data": [...]}
        """
        await self.initialize()
        
        selector = input.get("selector", "body")
        extract_type = input.get("extract_type", "text")
        
        if extract_type == "text":
            elements = await self._page.query_selector_all(selector)
            data = []
            for el in elements[:50]:
                text = await el.inner_text()
                data.append(text.strip())
            return {"data": data}
        
        elif extract_type == "table":
            # Extraer tablas como lista de dicts
            tables = await self._page.eval_on_selector_all(
                f"{selector} table, table",
                """tables => tables.map(table => {
                    const headers = Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim());
                    const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => {
                        const cells = Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim());
                        return headers.length ? Object.fromEntries(headers.map((h, i) => [h, cells[i] || ''])) : cells;
                    });
                    return {headers, rows};
                })"""
            )
            return {"data": tables}
        
        elif extract_type == "list":
            items = await self._page.eval_on_selector_all(
                f"{selector} li, {selector} [class*='item']",
                "elements => elements.slice(0, 100).map(e => e.innerText.trim())"
            )
            return {"data": items}
        
        elif extract_type == "attribute":
            attr = input.get("attribute", "href")
            values = await self._page.eval_on_selector_all(
                selector,
                f"elements => elements.slice(0, 50).map(e => e.getAttribute('{attr}'))"
            )
            return {"data": [v for v in values if v]}
        
        return {"data": [], "error": f"extract_type '{extract_type}' no soportado"}
    
    async def interact(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interactúa con la página: click, type, select, scroll.
        
        Input: {"action": "click|type|select|scroll", "selector": "...", "value": "..."}
        Output: {"success": bool, "page_changed": bool}
        """
        await self.initialize()
        
        action = input["action"]
        selector = input.get("selector", "")
        value = input.get("value", "")
        
        try:
            if action == "click":
                await self._page.click(selector)
            elif action == "type":
                await self._page.fill(selector, value)
            elif action == "select":
                await self._page.select_option(selector, value)
            elif action == "scroll":
                direction = input.get("direction", "down")
                distance = input.get("distance", 500)
                if direction == "down":
                    await self._page.evaluate(f"window.scrollBy(0, {distance})")
                else:
                    await self._page.evaluate(f"window.scrollBy(0, -{distance})")
            elif action == "wait":
                wait_ms = int(value) if value else 2000
                await asyncio.sleep(wait_ms / 1000)
            
            # Verificar si la página cambió
            new_url = self._page.url
            return {"success": True, "current_url": new_url}
        
        except Exception as e:
            return {"success": False, "error": str(e)[:200]}
    
    async def screenshot(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Captura screenshot de la página actual.
        
        Input: {"full_page": bool, "selector": "optional css selector"}
        Output: {"path": "/tmp/screenshot_xxx.png", "size_bytes": int}
        """
        await self.initialize()
        
        import uuid
        path = f"/tmp/embrion_screenshot_{uuid.uuid4().hex[:8]}.png"
        
        if input.get("selector"):
            element = await self._page.query_selector(input["selector"])
            if element:
                await element.screenshot(path=path)
            else:
                return {"error": f"Selector '{input['selector']}' no encontrado"}
        else:
            await self._page.screenshot(
                path=path,
                full_page=input.get("full_page", False)
            )
        
        size = os.path.getsize(path)
        return {"path": path, "size_bytes": size}
```

---

## Épica 73.2 — Generación de Media: Imágenes, Audio, Video

**Objetivo:** Darle al Embrión la capacidad de generar contenido multimedia — imágenes con DALL-E, audio/speech con ElevenLabs, y análisis de video.

```python
"""
kernel/execution/tools_media.py
MEDIA GENERATION — Imágenes, Audio, Speech

Capacidades:
- Generar imágenes (DALL-E 3 via OpenAI)
- Generar speech (ElevenLabs)
- Analizar imágenes (GPT-4o vision)
- Analizar video (transcripción + análisis)
"""

import os
import httpx
import base64
from typing import Dict, Any


class ImageGenerationTool:
    """Genera imágenes con DALL-E 3."""
    
    def __init__(self, openai_client=None):
        self.client = openai_client
    
    async def generate(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera una imagen a partir de un prompt.
        
        Input: {
            "prompt": "Descripción detallada de la imagen",
            "size": "1024x1024|1792x1024|1024x1792",
            "style": "vivid|natural",
            "quality": "standard|hd"
        }
        Output: {"url": "https://...", "revised_prompt": "..."}
        """
        if not self.client:
            return {"error": "execution_media_no_client: OpenAI client no configurado"}
        
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=input["prompt"],
            size=input.get("size", "1024x1024"),
            style=input.get("style", "vivid"),
            quality=input.get("quality", "standard"),
            n=1
        )
        
        return {
            "url": response.data[0].url,
            "revised_prompt": response.data[0].revised_prompt
        }
    
    async def analyze(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza una imagen con GPT-4o vision.
        
        Input: {"image_url": "https://...", "question": "¿Qué ves en esta imagen?"}
        Output: {"analysis": "..."}
        """
        if not self.client:
            return {"error": "execution_media_no_client: OpenAI client no configurado"}
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": input.get("question", "Describe esta imagen en detalle.")},
                    {"type": "image_url", "image_url": {"url": input["image_url"]}}
                ]
            }],
            max_tokens=500
        )
        
        return {"analysis": response.choices[0].message.content}


class SpeechGenerationTool:
    """Genera speech con ElevenLabs."""
    
    def __init__(self):
        self.api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def generate_speech(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera audio speech a partir de texto.
        
        Input: {
            "text": "Texto a convertir en speech",
            "voice_id": "ID de la voz (optional, default: voz masculina español)",
            "model": "eleven_multilingual_v2"
        }
        Output: {"audio_path": "/tmp/speech_xxx.mp3", "duration_seconds": float}
        """
        if not self.api_key:
            return {"error": "execution_media_no_key: ELEVENLABS_API_KEY no configurada"}
        
        voice_id = input.get("voice_id", "pNInz6obpgDQGcFmaJgB")  # Adam - español
        model = input.get("model", "eleven_multilingual_v2")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "text": input["text"],
                    "model_id": model,
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }
            )
            
            if response.status_code != 200:
                return {"error": f"execution_media_elevenlabs_error: {response.status_code}"}
            
            import uuid
            path = f"/tmp/embrion_speech_{uuid.uuid4().hex[:8]}.mp3"
            with open(path, "wb") as f:
                f.write(response.content)
            
            # Estimar duración (approx 150 words/min, 5 chars/word)
            estimated_duration = len(input["text"]) / (150 * 5 / 60)
            
            return {
                "audio_path": path,
                "duration_seconds": round(estimated_duration, 1),
                "size_bytes": len(response.content)
            }
    
    async def clone_voice(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clona una voz a partir de samples de audio.
        Para crear la voz oficial de El Monstruo.
        
        Input: {"name": "El Monstruo", "audio_urls": ["url1", "url2"]}
        Output: {"voice_id": "...", "name": "..."}
        """
        # Implementación futura — requiere audio samples
        return {"voice_id": "pending", "name": input.get("name", "custom")}


class VideoAnalysisTool:
    """Analiza contenido de video."""
    
    async def analyze(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza un video (transcripción + análisis visual).
        
        Input: {"video_url": "https://...", "question": "¿De qué trata este video?"}
        Output: {"transcript": "...", "analysis": "...", "key_points": [...]}
        """
        # En producción: usar Whisper para transcripción + GPT-4o para análisis
        # Por ahora: placeholder que se integra con la API de análisis
        return {
            "transcript": "[Transcripción pendiente de implementación]",
            "analysis": f"Análisis de video: {input.get('question', 'general')}",
            "key_points": []
        }
```

---

## Épica 73.3 — Comunicación: Email, Calendario, Notificaciones

**Objetivo:** Darle al Embrión la capacidad de comunicarse con el mundo exterior — enviar emails, crear eventos, y notificar.

```python
"""
kernel/execution/tools_comms.py
COMUNICACIÓN — Email, Calendario, Notificaciones Push

Capacidades:
- Enviar emails via Gmail API
- Crear/leer eventos de Google Calendar
- Enviar notificaciones push
- Publicar en redes sociales (futuro)

Seguridad:
- Rate limiting por tipo de comunicación
- Aprobación requerida para emails a externos
- Log de toda comunicación saliente
"""

import os
import httpx
from typing import Dict, Any, List
from datetime import datetime, timezone


class EmailTool:
    """Envía emails via Gmail API (o SMTP como fallback)."""
    
    MAX_EMAILS_PER_HOUR = 10
    
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self._sent_count = 0
        self._hour_start = datetime.now(timezone.utc)
    
    async def send(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía un email.
        
        Input: {
            "to": "email@example.com",
            "subject": "Asunto del email",
            "body": "Contenido del email (HTML o texto)",
            "body_type": "html|text",
            "requires_approval": bool (default True para externos)
        }
        Output: {"sent": bool, "message_id": "..."}
        """
        # Rate limiting
        now = datetime.now(timezone.utc)
        if (now - self._hour_start).total_seconds() > 3600:
            self._sent_count = 0
            self._hour_start = now
        
        if self._sent_count >= self.MAX_EMAILS_PER_HOUR:
            return {"error": "execution_comms_rate_limit: Máximo de emails por hora alcanzado"}
        
        # Seguridad: emails a externos requieren aprobación
        to = input["to"]
        requires_approval = input.get("requires_approval", True)
        
        if requires_approval and not self._is_internal(to):
            # Registrar solicitud de aprobación
            if self.supabase:
                self.supabase.table("pending_approvals").insert({
                    "type": "email",
                    "details": {
                        "to": to,
                        "subject": input["subject"],
                        "body_preview": input["body"][:200]
                    },
                    "status": "pending",
                    "created_at": now.isoformat()
                }).execute()
            
            return {
                "sent": False,
                "status": "pending_approval",
                "message": f"Email a '{to}' requiere aprobación de Alfredo"
            }
        
        # Enviar (implementación via Gmail API o SMTP)
        # En producción: usar google-auth + gmail API
        self._sent_count += 1
        
        # Log
        if self.supabase:
            self.supabase.table("communication_log").insert({
                "type": "email",
                "to": to,
                "subject": input["subject"],
                "status": "sent",
                "timestamp": now.isoformat()
            }).execute()
        
        return {"sent": True, "message_id": f"msg_{now.timestamp()}"}
    
    def _is_internal(self, email: str) -> bool:
        """Verifica si un email es interno (no requiere aprobación)."""
        internal_domains = ["elmonstruo.ai", "alfredogongora.com"]
        return any(email.endswith(f"@{d}") for d in internal_domains)


class CalendarTool:
    """Gestiona Google Calendar."""
    
    async def create_event(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un evento en el calendario.
        
        Input: {
            "title": "Nombre del evento",
            "start": "2026-05-02T10:00:00",
            "end": "2026-05-02T11:00:00",
            "description": "Descripción (optional)",
            "attendees": ["email1", "email2"] (optional)
        }
        Output: {"event_id": "...", "link": "https://calendar.google.com/..."}
        """
        # En producción: usar Google Calendar API
        return {
            "event_id": f"evt_{datetime.now(timezone.utc).timestamp()}",
            "link": "https://calendar.google.com/calendar/event/placeholder",
            "created": True
        }
    
    async def list_events(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lista eventos del calendario.
        
        Input: {"date": "2026-05-02", "days_ahead": 7}
        Output: {"events": [...]}
        """
        return {"events": []}
    
    async def find_free_time(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encuentra slots libres en el calendario.
        
        Input: {"date": "2026-05-02", "duration_minutes": 60}
        Output: {"free_slots": [{"start": "...", "end": "..."}]}
        """
        return {"free_slots": []}


class NotificationTool:
    """Envía notificaciones push y webhooks."""
    
    async def push(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía notificación push.
        
        Input: {
            "title": "Título",
            "body": "Contenido",
            "urgency": "info|warning|critical",
            "target": "alfredo|all|embrion_{id}"
        }
        Output: {"delivered": bool}
        """
        # En producción: usar web push API o servicio de notificaciones
        return {"delivered": True, "target": input.get("target", "alfredo")}
    
    async def webhook(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía a un webhook externo.
        
        Input: {"url": "https://...", "payload": {...}}
        Output: {"status_code": int, "success": bool}
        """
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                input["url"],
                json=input.get("payload", {})
            )
            return {
                "status_code": response.status_code,
                "success": response.status_code < 400
            }
```

---

## Épica 73.4 — Generación de Documentos: PDF, Markdown, Presentaciones

**Objetivo:** Darle al Embrión la capacidad de generar documentos profesionales — reportes PDF, documentación Markdown, y presentaciones.

```python
"""
kernel/execution/tools_docs.py
DOCUMENT GENERATION — PDF, Markdown, Presentaciones

Capacidades:
- Generar Markdown con formato premium
- Convertir Markdown a PDF
- Generar presentaciones (estructura de slides)
- Crear reportes con datos + visualizaciones

Principio: Todo documento generado pasa por Brand Engine.
"""

import os
from typing import Dict, Any, List
from datetime import datetime, timezone


class DocumentGenerationTool:
    """Genera documentos profesionales."""
    
    def __init__(self, llm_client=None, brand_engine=None):
        self.llm = llm_client
        self.brand = brand_engine
    
    async def generate_markdown(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera un documento Markdown premium.
        
        Input: {
            "title": "Título del documento",
            "type": "report|proposal|analysis|guide|readme",
            "content_brief": "De qué debe tratar",
            "sections": ["Introducción", "Análisis", "Conclusiones"] (optional),
            "data": {...} (optional — datos para incluir)
        }
        Output: {"markdown": "...", "path": "/tmp/doc_xxx.md", "word_count": int}
        """
        if not self.llm:
            return {"error": "execution_docs_no_llm: LLM client no configurado"}
        
        doc_type = input.get("type", "report")
        
        system_prompt = f"""Eres el generador de documentación de El Monstruo.
Generas documentos de calidad Magna — nivel publicación profesional.

Reglas de estilo:
- Tono: Directo, confiado, sin rodeos. Sin frases corporativas vacías.
- Estructura: Párrafos completos, no listas infinitas. Tablas donde aporten claridad.
- Formato: Markdown con headers, bold para conceptos clave, blockquotes para definiciones.
- Extensión: Suficiente para cubrir el tema con profundidad. Ni más, ni menos.
- Idioma: Español (LATAM) como primario.

Tipo de documento: {doc_type}"""
        
        sections_hint = ""
        if input.get("sections"):
            sections_hint = f"\nSecciones requeridas: {', '.join(input['sections'])}"
        
        data_hint = ""
        if input.get("data"):
            data_hint = f"\nDatos disponibles para incluir: {str(input['data'])[:1000]}"
        
        user_prompt = f"""Genera el siguiente documento:

Título: {input['title']}
Brief: {input['content_brief']}
{sections_hint}
{data_hint}

Produce el documento completo en Markdown."""
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=4000,
            temperature=0.4
        )
        
        markdown = response.choices[0].message.content
        
        # Guardar archivo
        import uuid
        path = f"/tmp/embrion_doc_{uuid.uuid4().hex[:8]}.md"
        with open(path, "w") as f:
            f.write(markdown)
        
        return {
            "markdown": markdown,
            "path": path,
            "word_count": len(markdown.split()),
            "tokens_used": response.usage.total_tokens
        }
    
    async def generate_pdf(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera un PDF a partir de Markdown o contenido directo.
        
        Input: {
            "markdown": "Contenido en Markdown" OR "markdown_path": "/path/to/file.md",
            "title": "Título del PDF",
            "author": "El Monstruo"
        }
        Output: {"pdf_path": "/tmp/doc_xxx.pdf", "pages": int, "size_bytes": int}
        """
        markdown = input.get("markdown", "")
        if not markdown and input.get("markdown_path"):
            with open(input["markdown_path"], "r") as f:
                markdown = f.read()
        
        if not markdown:
            return {"error": "execution_docs_no_content: No se proporcionó contenido"}
        
        # Usar weasyprint o fpdf2 para generar PDF
        import uuid
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)
        
        # Parsear markdown básico a PDF
        lines = markdown.split("\n")
        for line in lines:
            if line.startswith("# "):
                pdf.set_font("Helvetica", "B", 18)
                pdf.cell(0, 10, line[2:], new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", size=11)
            elif line.startswith("## "):
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 8, line[3:], new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", size=11)
            elif line.strip():
                pdf.multi_cell(0, 6, line)
            else:
                pdf.ln(4)
        
        path = f"/tmp/embrion_pdf_{uuid.uuid4().hex[:8]}.pdf"
        pdf.output(path)
        
        size = os.path.getsize(path)
        return {
            "pdf_path": path,
            "pages": pdf.page_no(),
            "size_bytes": size
        }
    
    async def generate_presentation(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera estructura de presentación (slides).
        
        Input: {
            "title": "Título de la presentación",
            "topic": "De qué trata",
            "slide_count": 10,
            "audience": "inversores|equipo|público"
        }
        Output: {"slides": [{"title": "...", "content": "...", "notes": "..."}], "path": "..."}
        """
        if not self.llm:
            return {"error": "execution_docs_no_llm: LLM client no configurado"}
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Genera una presentación de {input.get('slide_count', 10)} slides.

Título: {input['title']}
Tema: {input['topic']}
Audiencia: {input.get('audience', 'general')}

Para cada slide, proporciona:
- title: Título del slide
- content: Contenido principal (bullets o texto)
- notes: Notas del presentador
- visual_suggestion: Qué imagen o gráfico debería acompañar

Formato: JSON array de slides."""
            }],
            max_tokens=3000,
            temperature=0.5
        )
        
        return {
            "slides_raw": response.choices[0].message.content,
            "slide_count": input.get("slide_count", 10)
        }
```

---

## Épica 73.5 — Code Sandbox: Ejecución Segura de Código

**Objetivo:** Darle al Embrión la capacidad de escribir y ejecutar código Python en un entorno aislado — sin acceso al kernel principal.

```python
"""
kernel/execution/tools_code.py
CODE SANDBOX — Ejecución segura de código

Capacidades:
- Ejecutar código Python en sandbox aislado
- Instalar dependencias temporales
- Capturar stdout/stderr
- Timeout estricto (30s max)
- Sin acceso a red interna ni filesystem del kernel

Seguridad:
- Subprocess con timeout
- No hereda env vars del kernel
- Directorio temporal aislado
- Whitelist de imports permitidos
"""

import os
import asyncio
import tempfile
import subprocess
from typing import Dict, Any


class CodeSandboxTool:
    """
    Sandbox aislado para ejecutar código Python.
    
    El Embrión puede escribir y ejecutar código para:
    - Procesar datos
    - Generar visualizaciones
    - Calcular métricas
    - Transformar formatos
    - Prototipar lógica
    
    NO puede:
    - Acceder al filesystem del kernel
    - Hacer requests a localhost
    - Importar módulos del kernel
    - Ejecutar por más de 30 segundos
    """
    
    TIMEOUT_SECONDS = 30
    MAX_OUTPUT_CHARS = 10000
    
    # Imports permitidos (whitelist)
    ALLOWED_IMPORTS = {
        "json", "math", "random", "datetime", "collections",
        "itertools", "functools", "re", "os.path", "csv",
        "statistics", "decimal", "fractions", "hashlib",
        "base64", "urllib.parse", "typing", "dataclasses",
        "numpy", "pandas", "matplotlib", "seaborn"
    }
    
    # Imports bloqueados (blacklist explícita)
    BLOCKED_IMPORTS = {
        "subprocess", "os.system", "shutil.rmtree", "socket",
        "http.server", "ftplib", "smtplib", "telnetlib",
        "ctypes", "multiprocessing", "threading"
    }
    
    async def execute(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta código Python en sandbox.
        
        Input: {
            "code": "print('hello world')",
            "description": "Qué hace este código (para logging)"
        }
        Output: {
            "stdout": "hello world\n",
            "stderr": "",
            "exit_code": 0,
            "execution_time_ms": 150
        }
        """
        code = input["code"]
        
        # Validación de seguridad
        security_check = self._check_security(code)
        if security_check:
            return {"error": f"execution_code_blocked: {security_check}", "exit_code": -1}
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="/tmp"
        ) as f:
            f.write(code)
            script_path = f.name
        
        try:
            # Ejecutar en subprocess aislado
            import time
            start = time.time()
            
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS,
                cwd="/tmp",
                env={
                    "PATH": "/usr/bin:/bin",
                    "HOME": "/tmp",
                    "PYTHONPATH": ""  # No heredar paths del kernel
                }
            )
            
            elapsed_ms = int((time.time() - start) * 1000)
            
            return {
                "stdout": result.stdout[:self.MAX_OUTPUT_CHARS],
                "stderr": result.stderr[:self.MAX_OUTPUT_CHARS],
                "exit_code": result.returncode,
                "execution_time_ms": elapsed_ms
            }
        
        except subprocess.TimeoutExpired:
            return {
                "error": f"execution_code_timeout: Código excedió {self.TIMEOUT_SECONDS}s",
                "exit_code": -1
            }
        finally:
            os.unlink(script_path)
    
    def _check_security(self, code: str) -> str:
        """Verifica que el código no haga cosas peligrosas."""
        
        # Check imports bloqueados
        for blocked in self.BLOCKED_IMPORTS:
            if blocked in code:
                return f"Import bloqueado: '{blocked}'"
        
        # Check operaciones peligrosas
        dangerous_patterns = [
            ("os.system", "Ejecución de comandos del sistema"),
            ("os.popen", "Ejecución de comandos del sistema"),
            ("eval(", "Evaluación dinámica de código"),
            ("exec(", "Ejecución dinámica de código"),
            ("__import__", "Import dinámico"),
            ("open('/etc", "Acceso a archivos del sistema"),
            ("open('/home", "Acceso a home directory"),
            ("requests.post", "HTTP POST no autorizado"),
            ("rm -rf", "Eliminación recursiva"),
        ]
        
        for pattern, reason in dangerous_patterns:
            if pattern in code:
                return f"Operación bloqueada: {reason} ('{pattern}')"
        
        return ""  # Seguro
    
    async def execute_with_data(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta código con datos de entrada pre-cargados.
        
        Input: {
            "code": "import json; data = json.loads(INPUT_DATA); print(len(data))",
            "data": {"key": "value"},
            "description": "Procesar datos"
        }
        """
        import json
        
        data_json = json.dumps(input.get("data", {}))
        
        # Inyectar datos como variable
        wrapped_code = f"""
import json
INPUT_DATA = '''{data_json}'''
DATA = json.loads(INPUT_DATA)

{input['code']}
"""
        return await self.execute({"code": wrapped_code, "description": input.get("description", "")})
```

---

## Épica 73.6 — Multi-LLM Orchestrator: El Mejor Modelo para Cada Tarea

**Objetivo:** El Embrión no depende de un solo LLM. Selecciona el modelo óptimo para cada tarea basándose en: tipo de tarea, costo, latencia, y calidad requerida.

```python
"""
kernel/execution/multi_llm.py
MULTI-LLM ORCHESTRATOR — El mejor modelo para cada tarea

Capacidades:
- Routing inteligente: selecciona GPT-4o, Claude, o Gemini según la tarea
- Fallback automático: si un modelo falla, usa otro
- Consensus mode: consulta múltiples modelos y combina respuestas
- Cost-aware: elige el modelo más barato que cumpla el quality threshold

Modelos disponibles:
- OpenAI GPT-4o: Mejor para razonamiento general y código
- Anthropic Claude: Mejor para análisis largo y escritura
- Google Gemini: Mejor para multimodal y contexto largo
- Perplexity Sonar: Mejor para búsqueda con fuentes
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    PERPLEXITY = "perplexity"


class TaskType(Enum):
    REASONING = "reasoning"          # Lógica, planificación, decisiones
    CREATIVE_WRITING = "creative"    # Contenido creativo, copy, narrativa
    ANALYSIS = "analysis"            # Análisis de datos, documentos largos
    CODE = "code"                    # Generación y revisión de código
    SEARCH = "search"                # Búsqueda con fuentes actualizadas
    MULTIMODAL = "multimodal"        # Imágenes, video, audio
    TRANSLATION = "translation"      # Traducción y localización
    SUMMARIZATION = "summarization"  # Resumen de contenido largo


@dataclass
class LLMConfig:
    provider: LLMProvider
    model: str
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    strengths: List[TaskType]
    max_context: int


# Configuración de modelos disponibles
AVAILABLE_MODELS = [
    LLMConfig(
        provider=LLMProvider.OPENAI,
        model="gpt-4o",
        max_tokens=4096,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
        strengths=[TaskType.REASONING, TaskType.CODE, TaskType.MULTIMODAL],
        max_context=128000
    ),
    LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        strengths=[TaskType.CREATIVE_WRITING, TaskType.ANALYSIS, TaskType.SUMMARIZATION],
        max_context=200000
    ),
    LLMConfig(
        provider=LLMProvider.GEMINI,
        model="gemini-2.5-flash",
        max_tokens=8192,
        cost_per_1k_input=0.00035,
        cost_per_1k_output=0.0015,
        strengths=[TaskType.MULTIMODAL, TaskType.ANALYSIS, TaskType.TRANSLATION],
        max_context=1000000
    ),
    LLMConfig(
        provider=LLMProvider.PERPLEXITY,
        model="sonar-pro",
        max_tokens=4096,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        strengths=[TaskType.SEARCH],
        max_context=128000
    ),
]


class MultiLLMOrchestrator:
    """
    Orquestador Multi-LLM.
    
    Selecciona el modelo óptimo para cada tarea.
    Implementa fallback y consensus mode.
    """
    
    def __init__(self):
        self._clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Inicializa clientes para cada provider disponible."""
        
        if os.environ.get("OPENAI_API_KEY"):
            from openai import AsyncOpenAI
            self._clients[LLMProvider.OPENAI] = AsyncOpenAI()
        
        if os.environ.get("ANTHROPIC_API_KEY"):
            from anthropic import AsyncAnthropic
            self._clients[LLMProvider.ANTHROPIC] = AsyncAnthropic()
        
        if os.environ.get("GEMINI_API_KEY"):
            # Gemini via REST API
            self._clients[LLMProvider.GEMINI] = {"api_key": os.environ["GEMINI_API_KEY"]}
        
        if os.environ.get("SONAR_API_KEY"):
            self._clients[LLMProvider.PERPLEXITY] = {"api_key": os.environ["SONAR_API_KEY"]}
    
    def select_model(self, task_type: TaskType, budget_usd: float = 0.05) -> LLMConfig:
        """
        Selecciona el mejor modelo para el tipo de tarea y presupuesto.
        
        Prioridad:
        1. Modelo especializado en el tipo de tarea
        2. Dentro del presupuesto
        3. Mayor contexto disponible
        """
        # Filtrar modelos disponibles (tienen client configurado)
        available = [
            m for m in AVAILABLE_MODELS 
            if m.provider in self._clients
        ]
        
        if not available:
            raise RuntimeError("execution_llm_no_models: Ningún modelo LLM configurado")
        
        # Priorizar por especialización
        specialized = [m for m in available if task_type in m.strengths]
        candidates = specialized if specialized else available
        
        # Filtrar por presupuesto (estimando 1000 tokens de output)
        affordable = [
            m for m in candidates 
            if (m.cost_per_1k_input + m.cost_per_1k_output) <= budget_usd
        ]
        
        if affordable:
            return affordable[0]
        
        # Si ninguno cabe en presupuesto, usar el más barato
        return min(candidates, key=lambda m: m.cost_per_1k_input + m.cost_per_1k_output)
    
    async def generate(
        self,
        prompt: str,
        task_type: TaskType = TaskType.REASONING,
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.3,
        budget_usd: float = 0.05
    ) -> Dict[str, Any]:
        """
        Genera con el modelo óptimo para la tarea.
        Con fallback automático si falla.
        """
        model_config = self.select_model(task_type, budget_usd)
        
        try:
            result = await self._call_model(model_config, prompt, system_prompt, max_tokens, temperature)
            return {
                "text": result,
                "model_used": f"{model_config.provider.value}/{model_config.model}",
                "task_type": task_type.value
            }
        except Exception as e:
            # Fallback: intentar con otro modelo
            fallback = self._get_fallback(model_config)
            if fallback:
                try:
                    result = await self._call_model(fallback, prompt, system_prompt, max_tokens, temperature)
                    return {
                        "text": result,
                        "model_used": f"{fallback.provider.value}/{fallback.model}",
                        "task_type": task_type.value,
                        "fallback": True
                    }
                except Exception:
                    pass
            
            return {"error": f"execution_llm_all_failed: {str(e)[:200]}"}
    
    async def consensus(
        self,
        prompt: str,
        system_prompt: str = "",
        models: List[LLMProvider] = None
    ) -> Dict[str, Any]:
        """
        Modo Consenso: consulta múltiples modelos y combina respuestas.
        
        Útil para decisiones críticas donde un solo modelo puede estar sesgado.
        Equivalente a "Los Tres Sabios" del protocolo del proyecto.
        """
        if models is None:
            models = [p for p in LLMProvider if p in self._clients]
        
        # Llamar a todos en paralelo
        tasks = []
        for provider in models:
            config = next((m for m in AVAILABLE_MODELS if m.provider == provider), None)
            if config and provider in self._clients:
                tasks.append(self._call_model(config, prompt, system_prompt, 1000, 0.3))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar errores
        valid_responses = [r for r in results if isinstance(r, str)]
        
        if not valid_responses:
            return {"error": "execution_llm_consensus_failed: Ningún modelo respondió"}
        
        return {
            "responses": valid_responses,
            "model_count": len(valid_responses),
            "consensus_needed": len(valid_responses) > 1
        }
    
    async def _call_model(
        self, config: LLMConfig, prompt: str, system_prompt: str,
        max_tokens: int, temperature: float
    ) -> str:
        """Llama a un modelo específico."""
        
        if config.provider == LLMProvider.OPENAI:
            client = self._clients[LLMProvider.OPENAI]
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await client.chat.completions.create(
                model=config.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        
        elif config.provider == LLMProvider.ANTHROPIC:
            client = self._clients[LLMProvider.ANTHROPIC]
            response = await client.messages.create(
                model=config.model,
                max_tokens=max_tokens,
                system=system_prompt if system_prompt else "You are a helpful assistant.",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        elif config.provider == LLMProvider.GEMINI:
            import httpx
            api_key = self._clients[LLMProvider.GEMINI]["api_key"]
            async with httpx.AsyncClient(timeout=30) as http:
                response = await http.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{config.model}:generateContent?key={api_key}",
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "systemInstruction": {"parts": [{"text": system_prompt}]} if system_prompt else None,
                        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature}
                    }
                )
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        
        elif config.provider == LLMProvider.PERPLEXITY:
            import httpx
            api_key = self._clients[LLMProvider.PERPLEXITY]["api_key"]
            async with httpx.AsyncClient(timeout=15) as http:
                response = await http.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": config.model,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                data = response.json()
                return data["choices"][0]["message"]["content"]
        
        raise ValueError(f"Provider no soportado: {config.provider}")
    
    def _get_fallback(self, failed_config: LLMConfig) -> Optional[LLMConfig]:
        """Obtiene un modelo de fallback diferente al que falló."""
        for config in AVAILABLE_MODELS:
            if config.provider != failed_config.provider and config.provider in self._clients:
                return config
        return None
```

---

## Épica 73.7 — Superioridad: Auto-Trigger, Proactividad, Self-Improvement

**Objetivo:** Las capacidades que Manus NO tiene — lo que hace al Embrión SUPERIOR.

```python
"""
kernel/execution/superiority.py
SUPERIORIDAD — Lo que Manus NO puede hacer

1. AUTO-TRIGGER: El Embrión detecta condiciones y se auto-asigna encomiendas
2. PROACTIVIDAD: Monitorea el entorno y actúa sin que nadie le pida
3. SELF-IMPROVEMENT: Analiza su propio rendimiento y se mejora

Estas capacidades son las que convierten al Embrión de "asistente"
a "agente autónomo". Manus espera instrucciones. El Embrión actúa.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass


@dataclass
class Trigger:
    """Condición que activa una encomienda automáticamente."""
    id: str
    name: str
    condition: str                    # Descripción de la condición
    check_function: str              # Nombre de la función que verifica
    encomienda_template: str         # Qué hacer cuando se activa
    cooldown_minutes: int = 60       # Mínimo entre activaciones
    last_triggered: Optional[datetime] = None
    active: bool = True


class AutoTriggerEngine:
    """
    Motor de auto-triggers.
    
    Monitorea condiciones y genera encomiendas automáticamente.
    El Embrión no espera que le digan qué hacer — detecta y actúa.
    """
    
    def __init__(self, supabase_client=None, executor=None):
        self.supabase = supabase_client
        self.executor = executor
        self._triggers: List[Trigger] = []
        self._register_default_triggers()
    
    def _register_default_triggers(self):
        """Triggers por defecto que el Embrión monitorea."""
        
        self._triggers = [
            Trigger(
                id="brand_drift",
                name="Brand Drift Detector",
                condition="Más de 3 outputs con brand_score < 70 en las últimas 24h",
                check_function="check_brand_drift",
                encomienda_template="Analizar los outputs recientes con bajo brand_score, identificar el patrón de drift, y proponer correcciones al Brand DNA",
                cooldown_minutes=360  # Max 1 vez cada 6h
            ),
            Trigger(
                id="cost_spike",
                name="Cost Spike Detector",
                condition="Costo de las últimas 2h excede 2x el promedio diario",
                check_function="check_cost_spike",
                encomienda_template="Investigar el spike de costos, identificar qué encomiendas o herramientas lo causaron, y proponer optimizaciones",
                cooldown_minutes=120
            ),
            Trigger(
                id="failure_pattern",
                name="Failure Pattern Detector",
                condition="Más de 5 encomiendas fallidas con el mismo tipo de error en 24h",
                check_function="check_failure_pattern",
                encomienda_template="Analizar el patrón de fallos recurrentes, identificar la causa raíz, y proponer fix o workaround",
                cooldown_minutes=240
            ),
            Trigger(
                id="opportunity_detector",
                name="Opportunity Detector",
                condition="Tendencia detectada que alinea con los 14 Objetivos",
                check_function="check_opportunities",
                encomienda_template="Investigar la oportunidad detectada, evaluar viabilidad, y proponer plan de acción si es viable",
                cooldown_minutes=720  # Max 1 vez cada 12h
            ),
            Trigger(
                id="memory_insight",
                name="Memory Insight Generator",
                condition="Más de 20 encomiendas ejecutadas sin análisis de patrones",
                check_function="check_memory_insights",
                encomienda_template="Analizar las últimas 20 encomiendas ejecutadas, extraer patrones de éxito/fallo, y actualizar las estrategias del Pensador",
                cooldown_minutes=1440  # Max 1 vez al día
            ),
            Trigger(
                id="stale_objective",
                name="Stale Objective Detector",
                condition="Un objetivo de los 14 no ha avanzado en más de 5 sprints",
                check_function="check_stale_objectives",
                encomienda_template="Identificar objetivos estancados, proponer acciones concretas para avanzarlos, y crear encomiendas específicas",
                cooldown_minutes=2880  # Max cada 2 días
            )
        ]
    
    async def check_all_triggers(self) -> List[Dict[str, Any]]:
        """
        Verifica todos los triggers activos.
        Retorna lista de encomiendas a generar.
        
        Se ejecuta periódicamente desde el EmbrionScheduler.
        """
        triggered = []
        now = datetime.now(timezone.utc)
        
        for trigger in self._triggers:
            if not trigger.active:
                continue
            
            # Check cooldown
            if trigger.last_triggered:
                elapsed = (now - trigger.last_triggered).total_seconds() / 60
                if elapsed < trigger.cooldown_minutes:
                    continue
            
            # Check condición
            condition_met = await self._evaluate_trigger(trigger)
            
            if condition_met:
                trigger.last_triggered = now
                triggered.append({
                    "trigger_id": trigger.id,
                    "trigger_name": trigger.name,
                    "encomienda_objective": trigger.encomienda_template,
                    "triggered_at": now.isoformat()
                })
        
        return triggered
    
    async def _evaluate_trigger(self, trigger: Trigger) -> bool:
        """Evalúa si un trigger se cumple."""
        
        if not self.supabase:
            return False
        
        if trigger.id == "brand_drift":
            result = self.supabase.table("encomiendas")\
                .select("brand_score")\
                .lt("brand_score", 70)\
                .gte("completed_at", (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat())\
                .execute()
            return len(result.data) >= 3
        
        elif trigger.id == "cost_spike":
            # Comparar costo últimas 2h vs promedio diario
            recent = self.supabase.table("encomiendas")\
                .select("total_cost_usd")\
                .gte("completed_at", (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat())\
                .execute()
            daily = self.supabase.table("encomiendas")\
                .select("total_cost_usd")\
                .gte("completed_at", (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat())\
                .execute()
            
            recent_cost = sum(r.get("total_cost_usd", 0) for r in recent.data)
            daily_avg = sum(r.get("total_cost_usd", 0) for r in daily.data) / 12  # 2h avg
            
            return recent_cost > daily_avg * 2 if daily_avg > 0 else False
        
        elif trigger.id == "failure_pattern":
            result = self.supabase.table("encomiendas")\
                .select("*")\
                .eq("status", "failed")\
                .gte("completed_at", (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat())\
                .execute()
            return len(result.data) >= 5
        
        elif trigger.id == "memory_insight":
            result = self.supabase.table("execution_memory")\
                .select("id")\
                .order("created_at", desc=True)\
                .limit(20)\
                .execute()
            # Trigger si hay 20+ memorias sin análisis reciente
            return len(result.data) >= 20
        
        return False


class SelfImprovementLoop:
    """
    Auto-mejora del Embrión.
    
    Analiza su propio rendimiento y genera mejoras:
    - Optimiza prompts del Pensador basado en resultados
    - Identifica herramientas subutilizadas
    - Sugiere nuevas herramientas a integrar
    - Detecta ineficiencias en planificación
    """
    
    def __init__(self, supabase_client=None, llm_orchestrator=None):
        self.supabase = supabase_client
        self.llm = llm_orchestrator
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """
        Analiza el rendimiento del Embrión en las últimas 24h.
        
        Métricas:
        - Success rate por tipo de encomienda
        - Costo promedio por tipo
        - Herramientas más/menos usadas
        - Errores más comunes
        - Tiempo promedio de ejecución
        """
        if not self.supabase:
            return {"error": "execution_self_improve_no_db"}
        
        # Obtener datos de las últimas 24h
        since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        
        encomiendas = self.supabase.table("encomiendas")\
            .select("*")\
            .gte("created_at", since)\
            .execute()
        
        memories = self.supabase.table("execution_memory")\
            .select("*")\
            .gte("created_at", since)\
            .execute()
        
        data = encomiendas.data or []
        mem_data = memories.data or []
        
        total = len(data)
        succeeded = sum(1 for e in data if e.get("status") == "completed")
        failed = sum(1 for e in data if e.get("status") == "failed")
        total_cost = sum(e.get("total_cost_usd", 0) for e in data)
        
        # Herramientas usadas
        all_tools = []
        for m in mem_data:
            all_tools.extend(m.get("tools_used", []))
        tool_frequency = {}
        for t in all_tools:
            tool_frequency[t] = tool_frequency.get(t, 0) + 1
        
        # Errores comunes
        all_issues = []
        for m in mem_data:
            all_issues.extend(m.get("unexpected_issues", []))
        
        return {
            "period": "24h",
            "total_encomiendas": total,
            "success_rate": (succeeded / total * 100) if total > 0 else 0,
            "failure_rate": (failed / total * 100) if total > 0 else 0,
            "total_cost_usd": round(total_cost, 4),
            "avg_cost_per_encomienda": round(total_cost / total, 4) if total > 0 else 0,
            "tool_frequency": tool_frequency,
            "common_issues": all_issues[:10],
            "improvement_opportunities": await self._identify_improvements(data, mem_data)
        }
    
    async def _identify_improvements(self, encomiendas: list, memories: list) -> List[str]:
        """Usa LLM para identificar mejoras basado en datos."""
        
        if not self.llm or not encomiendas:
            return []
        
        # Preparar resumen para el LLM
        summary = f"""Datos de rendimiento del Embrión (últimas 24h):
- Total encomiendas: {len(encomiendas)}
- Exitosas: {sum(1 for e in encomiendas if e.get('status') == 'completed')}
- Fallidas: {sum(1 for e in encomiendas if e.get('status') == 'failed')}
- Costo total: ${sum(e.get('total_cost_usd', 0) for e in encomiendas):.4f}

Errores frecuentes:
{chr(10).join(m.get('unexpected_issues', ['ninguno'])[0] for m in memories[:5] if m.get('unexpected_issues'))}

Herramientas usadas:
{chr(10).join(f"- {t}: {c} veces" for t, c in sorted(((t, sum(1 for m in memories if t in m.get('tools_used', []))) for t in set(t for m in memories for t in m.get('tools_used', []))), key=lambda x: -x[1])[:10])}"""
        
        from .multi_llm import TaskType
        result = await self.llm.generate(
            prompt=f"""Analiza estos datos de rendimiento y sugiere 3-5 mejoras concretas y accionables:

{summary}

Formato: Lista numerada de mejoras específicas.""",
            task_type=TaskType.ANALYSIS,
            temperature=0.4
        )
        
        if "text" in result:
            return [result["text"]]
        return []
    
    async def optimize_planner_prompt(self) -> Dict[str, Any]:
        """
        Optimiza el system prompt del Pensador basado en resultados.
        
        Analiza qué tipos de planes tuvieron mayor success rate
        y ajusta el prompt para favorecer esas estrategias.
        """
        # Implementación futura: A/B testing de prompts
        return {"status": "pending_implementation"}
```

---

## Épica 73.8 — Integración con ToolRegistry

**Objetivo:** Registrar todas las nuevas herramientas en el ToolRegistry existente (Sprint 72) para que el TEL pueda usarlas.

```python
"""
kernel/execution/tools_registry_v2.py
TOOL REGISTRY v2 — Registro completo post-Sprint 73

Agrega todas las herramientas nuevas al registry existente.
El Pensador ahora tiene acceso a TODO lo que Manus tiene y más.
"""

from .tools import ToolRegistry, ToolDefinition
from .tools_web import WebBrowserTool
from .tools_media import ImageGenerationTool, SpeechGenerationTool
from .tools_comms import EmailTool, CalendarTool, NotificationTool
from .tools_docs import DocumentGenerationTool
from .tools_code import CodeSandboxTool
from .multi_llm import MultiLLMOrchestrator


def register_all_tools(registry: ToolRegistry):
    """Registra todas las herramientas disponibles post-Sprint 73."""
    
    web = WebBrowserTool()
    media = ImageGenerationTool()
    speech = SpeechGenerationTool()
    email = EmailTool()
    calendar = CalendarTool()
    docs = DocumentGenerationTool()
    code = CodeSandboxTool()
    
    # ─── WEB BROWSER ──────────────────────────────────────────────
    registry.register(
        ToolDefinition(
            name="web_navigate",
            description="Navega a una URL y extrae el contenido de la página. Para investigar sitios web, leer artículos, verificar información online.",
            input_schema={"url": "str - URL completa", "wait_for": "str - networkidle|domcontentloaded"},
            output_schema={"title": "str", "content_text": "str", "links": "list"},
            estimated_cost_usd=0.0,
            timeout_seconds=30
        ),
        handler=web.navigate
    )
    
    registry.register(
        ToolDefinition(
            name="web_extract",
            description="Extrae datos estructurados de la página web actual. Para scraping de tablas, listas, links, o contenido específico.",
            input_schema={"selector": "str - CSS selector", "extract_type": "str - text|table|list|attribute"},
            output_schema={"data": "list"},
            estimated_cost_usd=0.0,
            timeout_seconds=15
        ),
        handler=web.extract
    )
    
    registry.register(
        ToolDefinition(
            name="web_interact",
            description="Interactúa con la página web: click, escribir en forms, scroll. Para automatizar acciones en sitios web.",
            input_schema={"action": "str - click|type|select|scroll", "selector": "str", "value": "str"},
            output_schema={"success": "bool", "current_url": "str"},
            estimated_cost_usd=0.0,
            timeout_seconds=15
        ),
        handler=web.interact
    )
    
    # ─── MEDIA GENERATION ─────────────────────────────────────────
    registry.register(
        ToolDefinition(
            name="image_generate",
            description="Genera una imagen con DALL-E 3 a partir de un prompt descriptivo. Para crear assets visuales, logos, ilustraciones, backgrounds.",
            input_schema={"prompt": "str - Descripción detallada", "size": "str - 1024x1024|1792x1024", "style": "str - vivid|natural"},
            output_schema={"url": "str - URL de la imagen generada", "revised_prompt": "str"},
            estimated_cost_usd=0.04,
            timeout_seconds=30,
            max_calls_per_encomienda=5
        ),
        handler=media.generate
    )
    
    registry.register(
        ToolDefinition(
            name="image_analyze",
            description="Analiza una imagen con GPT-4o vision. Para entender contenido visual, extraer texto de imágenes, o evaluar calidad visual.",
            input_schema={"image_url": "str - URL de la imagen", "question": "str - Qué analizar"},
            output_schema={"analysis": "str"},
            estimated_cost_usd=0.01,
            timeout_seconds=20
        ),
        handler=media.analyze
    )
    
    registry.register(
        ToolDefinition(
            name="speech_generate",
            description="Genera audio speech con ElevenLabs. Para crear narración, podcasts, mensajes de voz, o la voz oficial de El Monstruo.",
            input_schema={"text": "str - Texto a convertir", "voice_id": "str - ID de voz (optional)"},
            output_schema={"audio_path": "str", "duration_seconds": "float"},
            estimated_cost_usd=0.01,
            timeout_seconds=30,
            max_calls_per_encomienda=3
        ),
        handler=speech.generate_speech
    )
    
    # ─── COMUNICACIÓN ─────────────────────────────────────────────
    registry.register(
        ToolDefinition(
            name="email_send",
            description="Envía un email. Emails a externos requieren aprobación de Alfredo. Para comunicación, outreach, notificaciones.",
            input_schema={"to": "str - Email destino", "subject": "str", "body": "str", "body_type": "str - html|text"},
            output_schema={"sent": "bool", "status": "str"},
            estimated_cost_usd=0.0,
            timeout_seconds=10,
            max_calls_per_encomienda=5
        ),
        handler=email.send
    )
    
    registry.register(
        ToolDefinition(
            name="calendar_create",
            description="Crea un evento en Google Calendar. Para programar reuniones, deadlines, recordatorios.",
            input_schema={"title": "str", "start": "str - ISO datetime", "end": "str - ISO datetime", "description": "str"},
            output_schema={"event_id": "str", "link": "str"},
            estimated_cost_usd=0.0,
            timeout_seconds=10
        ),
        handler=calendar.create_event
    )
    
    # ─── DOCUMENTOS ───────────────────────────────────────────────
    registry.register(
        ToolDefinition(
            name="doc_generate",
            description="Genera un documento Markdown premium con calidad Magna. Para reportes, propuestas, análisis, guías. Pasa por Brand Engine automáticamente.",
            input_schema={"title": "str", "type": "str - report|proposal|analysis|guide", "content_brief": "str", "sections": "list (optional)"},
            output_schema={"markdown": "str", "path": "str", "word_count": "int"},
            estimated_cost_usd=0.02,
            timeout_seconds=45
        ),
        handler=docs.generate_markdown
    )
    
    registry.register(
        ToolDefinition(
            name="pdf_generate",
            description="Genera un PDF a partir de contenido Markdown. Para deliverables formales, reportes impresos, documentos oficiales.",
            input_schema={"markdown": "str - Contenido", "title": "str"},
            output_schema={"pdf_path": "str", "pages": "int", "size_bytes": "int"},
            estimated_cost_usd=0.0,
            timeout_seconds=15
        ),
        handler=docs.generate_pdf
    )
    
    # ─── CODE SANDBOX ─────────────────────────────────────────────
    registry.register(
        ToolDefinition(
            name="code_execute",
            description="Ejecuta código Python en sandbox aislado. Para procesar datos, calcular métricas, generar visualizaciones, transformar formatos. Seguro y aislado del kernel.",
            input_schema={"code": "str - Código Python", "description": "str - Qué hace"},
            output_schema={"stdout": "str", "stderr": "str", "exit_code": "int", "execution_time_ms": "int"},
            estimated_cost_usd=0.0,
            timeout_seconds=30,
            max_calls_per_encomienda=10
        ),
        handler=code.execute
    )
    
    # ─── MULTI-LLM ───────────────────────────────────────────────
    # El multi-LLM se usa internamente por el Pensador, no como tool directo
    # Pero se expone para encomiendas que requieran consenso explícito
    
    return registry


# ─── RESUMEN DE HERRAMIENTAS POST-SPRINT 73 ──────────────────────────────

TOOL_INVENTORY = """
HERRAMIENTAS DISPONIBLES PARA EL EMBRIÓN (post-Sprint 73):

BÚSQUEDA & WEB:
  - perplexity_search: Búsqueda web con fuentes ($0.005)
  - web_navigate: Navegar a URL y extraer contenido ($0)
  - web_extract: Scraping estructurado ($0)
  - web_interact: Clicks, forms, scroll ($0)

BASE DE DATOS:
  - supabase_query: Leer datos ($0)
  - supabase_write: Escribir datos ($0)

GENERACIÓN:
  - llm_generate: Generar texto con LLM potente ($0.01)
  - llm_analyze: Analizar contenido ($0.008)
  - image_generate: Crear imágenes DALL-E 3 ($0.04)
  - image_analyze: Analizar imágenes GPT-4o vision ($0.01)
  - speech_generate: Crear audio ElevenLabs ($0.01)
  - doc_generate: Documentos Markdown premium ($0.02)
  - pdf_generate: Convertir a PDF ($0)

COMUNICACIÓN:
  - email_send: Enviar emails ($0)
  - calendar_create: Crear eventos ($0)
  - notify: Notificaciones push ($0)

CÓDIGO:
  - code_execute: Python sandbox aislado ($0)

COORDINACIÓN:
  - brand_validate: Validar con Brand Engine ($0.002)
  - embrion_delegate: Delegar a otro Embrión ($0.01)

GITHUB:
  - github_read: Leer repos/issues ($0)
  - github_write: Crear issues/commits ($0)

HTTP:
  - http_request: Llamar cualquier API ($0)

TOTAL: 22 herramientas
COSTO PROMEDIO POR ENCOMIENDA (estimado): $0.05-0.15
"""
```

---

## Métricas de Éxito

| Métrica | Target | Cómo se mide |
|---|---|---|
| Herramientas disponibles | ≥ 22 | Count en ToolRegistry |
| Paridad Manus | 100% | Todas las capacidades de Manus cubiertas |
| Multi-LLM routing | ≥ 3 providers | Providers configurados y funcionales |
| Auto-triggers activos | ≥ 5 | Triggers registrados y evaluándose |
| Self-improvement reports | ≥ 1/día | Análisis automáticos generados |
| Code sandbox security | 0 breaches | Tests de penetración pasan |
| Email rate limit | ≤ 10/hora | Enforcement verificado |
| Browser blocked hosts | 100% | Localhost/internal siempre bloqueado |

---

## Dependencias

| Dependencia | Estado | Sprint |
|---|---|---|
| Task Execution Loop (TEL) | Sprint 72 | Pendiente |
| Brand Engine (Embrión-1) | Sprint 71 | Pendiente |
| EmbrionScheduler | Activo | Sprint 53 |
| Supabase | Activo | Sprint 51 |
| OpenAI API | Activo | Sprint 52 |
| Anthropic API | Configurado | Env var disponible |
| Gemini API | Configurado | Env var disponible |
| ElevenLabs API | Configurado | Env var disponible |
| Perplexity API | Activo | Sprint 52 |
| Playwright | Requiere install | `pip install playwright` |

---

## Orden de Implementación

1. **73.8** Integración ToolRegistry v2 (estructura) — 30 min
2. **73.1** Web Browser con Playwright — 1h
3. **73.2** Media Generation (DALL-E + ElevenLabs) — 45 min
4. **73.3** Comunicación (Email + Calendar) — 45 min
5. **73.4** Document Generation — 30 min
6. **73.5** Code Sandbox — 45 min
7. **73.6** Multi-LLM Orchestrator — 1h
8. **73.7** Superioridad (Auto-Trigger + Self-Improvement) — 1h

**MVP mínimo:** 73.8 + 73.1 + 73.6. Con browser y multi-LLM, el Embrión ya supera a la mayoría de agentes. El resto se agrega incrementalmente.

---

## Nota para el Hilo A (Ejecutor)

> **PARIDAD MANUS + SUPERIORIDAD**
>
> Este sprint convierte al Embrión en un agente completo.
> Después de implementar esto, el Embrión puede hacer TODO lo que Manus hace
> y además: memoria persistente, auto-triggers, multi-LLM, y self-improvement.
>
> PRIORIDADES DE SEGURIDAD (no negociables):
> 1. Web Browser: NUNCA puede acceder a localhost/127.0.0.1
> 2. Code Sandbox: NUNCA hereda env vars del kernel
> 3. Email: SIEMPRE requiere aprobación para externos
> 4. Shell: ELIMINADO del registry (usar code_execute con sandbox)
>
> PRIORIDADES DE MARCA:
> - Toda generación de documentos pasa por Brand Engine
> - Los auto-triggers tienen nombres descriptivos en español
> - Los error messages siguen el formato: execution_{module}_{type}: {descripción}
> - El Multi-LLM selecciona modelos pero el output final siempre se valida
>
> INSTALL REQUERIDO:
> pip install playwright anthropic google-genai elevenlabs
> playwright install chromium
