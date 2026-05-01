# Sprint 52 — "Las Manos del Creador"

> **Desde:** Sprint 51 completado (cimientos perpetuos activos)
> **Hacia:** Objetivos #1, #2, #7, #9 — El Monstruo puede crear empresas digitales completas
> **Duración estimada:** 7-10 días
> **Fecha de planificación:** 1 de mayo de 2026

---

## Pre-requisito Formal

> **DEPENDENCIA CRÍTICA:** El Sprint 51 DEBE estar completado y los cimientos perpetuos activos (Error Memory, Clasificador Magna/Premium, Browser Interactivo, Vanguard Scanner, Design System Foundation) ANTES de ejecutar cualquier épica del Sprint 52. Sin Error Memory y Magna/Premium activos, el Sprint 52 construye sobre arena. El Clasificador Magna debe estar validando en tiempo real cada API que se integre.

## Contexto

Con los cimientos del Sprint 51 activos, el Sprint 52 se enfoca en darle al Monstruo las **manos para crear** — la capacidad de construir plataformas digitales completas (backends, bases de datos, autenticación, pagos, media) y entregarlas funcionando.

---

## Inventario del Stack Actual (validado 1 mayo 2026)

Antes de decidir qué adoptar, esto es lo que El Monstruo YA tiene:

| Componente | Estado | Archivo |
|---|---|---|
| Deploy frontend (Vercel) | ✅ Activo | `tools/web_dev.py` |
| Deploy backend (Railway) | ✅ Activo (propio) | Infra actual del Monstruo |
| Sandbox (E2B) | ✅ Activo | `tools/code_exec.py`, `tools/sandbox_manager.py` |
| Base de datos (Supabase) | ✅ Activo (propia) | `memory/supabase_client.py` |
| Observabilidad (Langfuse + Opik) | ✅ Activo | `observability/langfuse_bridge.py`, `observability/opik_bridge.py` |
| MCP Client | ✅ Activo | `kernel/mcp_client.py` (stdio + sse) |
| Multi-Agent Dispatcher | ✅ Activo | `kernel/multi_agent.py` (LangGraph SubGraphs) |
| File Operations | ✅ Activo | `tools/file_ops.py` |
| Browser (read-only) | ✅ Activo | `tools/browser.py` (Cloudflare) |
| Browser interactivo | 🔜 Sprint 51 | `tools/interactive_browser.py` (browser-use) |
| Knowledge Graph | ✅ Activo | `memory/lightrag_bridge.py` |
| Memoria (Mem0 + MemPalace) | ✅ Activo | `memory/mem0_bridge.py`, `memory/mempalace_bridge.py` |
| GitHub tool | ✅ Activo | `tools/github.py` |
| Fallback providers | ✅ Activo | Groq + Together (Sprint 29) |

**Lo que NO tiene y necesita para crear empresas digitales:**

| Capacidad | Necesaria para | Existe en el mundo |
|---|---|---|
| Provisionar DB para proyectos de usuario | Obj #1 — cada plataforma necesita su DB | Supabase Management API |
| Auth para proyectos de usuario | Obj #1 — login, roles, OAuth | Supabase Auth (ya disponible) |
| Pagos | Obj #1, #9 — monetización | Stripe + Stripe MCP (anunciado 29 abril 2026) |
| Deploy backend de usuario | Obj #1 — APIs, workers, websockets | Railway API (ya conocido) |
| Media generation | Obj #2 — imágenes, assets de marca | GPT Image 2, Flux.2 |
| Observabilidad activada en prod | Obj #6 — saber qué funciona | Langfuse ya instalado, solo falta activar |
| Procesamiento paralelo | Obj #1 — tareas batch, research masivo | LangGraph parallel nodes (ya disponible) |

---

## Épica 52.1 — Supabase Project Provisioner

**Objetivo que ataca:** #1 (crear empresas digitales), #7 (adoptar lo mejor)

**Qué hace:** Permite al Monstruo crear bases de datos completas para los proyectos que construye. No solo tablas — proyectos Supabase completos con auth, storage, y realtime.

**Qué se adopta:** Supabase Management API v1 [1]

**Por qué Supabase y no Neon/PlanetScale:** El Monstruo ya usa Supabase para su propia memoria. Supabase incluye Auth + Storage + Realtime + Edge Functions en un solo servicio. Neon es solo Postgres. PlanetScale es MySQL. Adoptar Supabase para proyectos de usuario mantiene un solo ecosistema (Obj #7 — no multiplicar dependencias sin razón).

**Requisitos:**
- `SUPABASE_ACCESS_TOKEN` — Token de la organización de Alfredo en Supabase
- El Monstruo ya tiene `SUPABASE_URL` y `SUPABASE_SERVICE_KEY` para su propia DB

**Archivo a crear:** `tools/supabase_provisioner.py`

```python
"""
El Monstruo — Supabase Project Provisioner (Sprint 52)
======================================================
Creates and manages Supabase projects for user platforms.
Capabilities:
  - create_project: New Supabase project with DB, Auth, Storage
  - run_migration: Execute SQL migrations on project DB
  - configure_auth: Enable OAuth providers, magic links, etc.
  - create_storage_bucket: File storage for user uploads
  - get_connection_string: For backend services to connect
  - list_projects: All projects created by El Monstruo

Uses Supabase Management API v1:
  https://supabase.com/docs/reference/api/introduction

Principio: Supabase es commodity — lo adoptamos, no lo reinventamos.
"""
from __future__ import annotations
import os
import httpx
import structlog

logger = structlog.get_logger("tools.supabase_provisioner")

SUPABASE_MGMT_URL = "https://api.supabase.com/v1"

class SupabaseProvisioner:
    def __init__(self):
        self.access_token = os.environ.get("SUPABASE_ACCESS_TOKEN")
        if not self.access_token:
            logger.warning("supabase_access_token_not_set")
        self.org_id = os.environ.get("SUPABASE_ORG_ID")
        self.client = httpx.AsyncClient(
            base_url=SUPABASE_MGMT_URL,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=60.0,
        )

    async def create_project(self, name: str, region: str = "us-east-1",
                             db_password: str = None) -> dict:
        """Create a new Supabase project with full stack."""
        import secrets
        password = db_password or secrets.token_urlsafe(32)
        resp = await self.client.post("/projects", json={
            "name": name,
            "organization_id": self.org_id,
            "region": region,
            "db_pass": password,
            "plan": "free",  # Start free, upgrade when needed
        })
        resp.raise_for_status()
        project = resp.json()
        logger.info("supabase_project_created",
                     project_id=project["id"], name=name)
        return {
            "project_id": project["id"],
            "url": f"https://{project['id']}.supabase.co",
            "anon_key": project.get("anon_key", "pending"),
            "service_key": project.get("service_role_key", "pending"),
            "db_password": password,
            "connection_string": (
                f"postgresql://postgres:{password}"
                f"@db.{project['id']}.supabase.co:5432/postgres"
            ),
        }

    async def run_migration(self, project_id: str, sql: str) -> dict:
        """Execute SQL migration on a project's database."""
        resp = await self.client.post(
            f"/projects/{project_id}/database/query",
            json={"query": sql},
        )
        resp.raise_for_status()
        return {"status": "ok", "result": resp.json()}

    async def configure_auth(self, project_id: str,
                             providers: list[str] = None) -> dict:
        """Configure auth providers for a project."""
        config = {}
        if providers:
            for provider in providers:
                config[f"external_{provider}_enabled"] = True
        resp = await self.client.patch(
            f"/projects/{project_id}/config/auth",
            json=config,
        )
        resp.raise_for_status()
        return {"status": "ok", "providers_enabled": providers}

    async def create_storage_bucket(self, project_id: str,
                                     bucket_name: str,
                                     public: bool = False) -> dict:
        """Create a storage bucket for file uploads."""
        # Uses the project's Supabase client, not management API
        project_url = f"https://{project_id}.supabase.co"
        resp = await httpx.AsyncClient().post(
            f"{project_url}/storage/v1/bucket",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"name": bucket_name, "public": public},
        )
        resp.raise_for_status()
        return {"bucket": bucket_name, "public": public}
```

**Registro en tool_broker:** Agregar a `kernel/tool_broker.py`:
```python
"supabase_provision": "tools.supabase_provisioner",
```

**Dependencias:** Ninguna nueva — ya tiene `httpx[http2]==0.28.1`

**Variables de entorno nuevas en Railway:**
- `SUPABASE_ACCESS_TOKEN` — Token de Management API
- `SUPABASE_ORG_ID` — ID de la organización

**Paso Magna obligatorio (Corrección C1):** Antes de implementar, verificar en tiempo real que la Supabase Management API v1 sigue vigente, que el plan "free" existe, y que los endpoints no cambiaron. Hacer un request de prueba real.

**Criterio de éxito:**
- T0: Validación Magna de Supabase Management API confirma endpoints vigentes
- T1: `create_project("test-marketplace")` retorna project_id + URL + keys en <30s
- T2: `run_migration(project_id, "CREATE TABLE products (id SERIAL PRIMARY KEY, name TEXT);")` ejecuta sin error
- T3: `configure_auth(project_id, ["google", "github"])` habilita OAuth

---

## Épica 52.2 — Stripe Integration via MCP

**Objetivo que ataca:** #1 (empresas digitales), #7 (adoptar lo mejor), #9 (capas transversales)

**Qué hace:** Integra Stripe como sistema de pagos para todas las plataformas que El Monstruo cree. Usa el Stripe MCP Server oficial (anunciado en Stripe Sessions 2026, 29 de abril) [2].

**Por qué Stripe MCP y no API directa:** Stripe lanzó hace 2 días su MCP server oficial. El Monstruo ya tiene `kernel/mcp_client.py` que soporta MCP via stdio y sse. Conectar Stripe via MCP es más limpio que escribir un wrapper API custom, y se alinea con el estándar emergente (MCP es "el USB-C de agent tools" según la industria) [3].

**Qué incluye Stripe en 2026:**
- Agentic Commerce Suite — vender productos dentro de apps de IA
- Machine Payments Protocol (MPP) — agentes transaccionan programáticamente
- Shared Payment Tokens (SPTs) — pagos via PaymentIntents API
- Stripe Connect — splits para marketplaces (vendedor/plataforma)
- Checkout Studio — checkout visual configurable
- Stripe Signals — fraud/risk intelligence

**Archivo a crear:** `tools/stripe_mcp.py`

```python
"""
El Monstruo — Stripe MCP Integration (Sprint 52)
=================================================
Connects to Stripe's official MCP server for payment processing.
Capabilities:
  - create_checkout: Generate payment links / checkout sessions
  - create_connect_account: Onboard marketplace sellers
  - create_subscription: Recurring billing
  - get_balance: Check account balance
  - create_refund: Process refunds
  - list_transactions: Transaction history

Uses Stripe MCP Server (official, announced Sessions 2026):
  https://github.com/stripe/stripe-mcp
  Transport: stdio (npx @stripe/mcp)

Requires: STRIPE_SECRET_KEY env var
Principio: Stripe es el mejor sistema de pagos del mundo. Lo adoptamos.
"""
from __future__ import annotations
import os
import structlog
from kernel.mcp_client import MCPClientManager, MCPServerConfig

logger = structlog.get_logger("tools.stripe_mcp")

STRIPE_MCP_CONFIG = MCPServerConfig(
    name="stripe",
    transport="stdio",
    command="npx",
    args=["@stripe/mcp", "--tools=all"],
    env={"STRIPE_SECRET_KEY": os.environ.get("STRIPE_SECRET_KEY", "")},
)

class StripeMCP:
    """Wrapper around Stripe MCP server for payment operations."""

    def __init__(self, mcp_manager: MCPClientManager):
        self.mcp = mcp_manager
        self._initialized = False

    async def initialize(self):
        """Connect to Stripe MCP server."""
        if not self._initialized:
            await self.mcp.connect_server(STRIPE_MCP_CONFIG)
            self._initialized = True
            logger.info("stripe_mcp_connected")

    async def create_checkout_session(self, items: list[dict],
                                       success_url: str,
                                       cancel_url: str,
                                       mode: str = "payment") -> dict:
        """Create a Stripe Checkout session."""
        return await self.mcp.execute_tool("stripe", "create_checkout_session", {
            "line_items": items,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "mode": mode,
        })

    async def create_connect_account(self, email: str,
                                      country: str = "US",
                                      business_type: str = "individual") -> dict:
        """Onboard a marketplace seller via Stripe Connect."""
        return await self.mcp.execute_tool("stripe", "create_account", {
            "type": "express",
            "email": email,
            "country": country,
            "business_type": business_type,
        })

    async def create_subscription(self, customer_id: str,
                                   price_id: str) -> dict:
        """Create a recurring subscription."""
        return await self.mcp.execute_tool("stripe", "create_subscription", {
            "customer": customer_id,
            "items": [{"price": price_id}],
        })

    async def create_product(self, name: str, description: str,
                              price_cents: int, currency: str = "usd") -> dict:
        """Create a product with price in Stripe catalog."""
        product = await self.mcp.execute_tool("stripe", "create_product", {
            "name": name,
            "description": description,
        })
        price = await self.mcp.execute_tool("stripe", "create_price", {
            "product": product["id"],
            "unit_amount": price_cents,
            "currency": currency,
        })
        return {"product": product, "price": price}
```

**Configuración MCP en `kernel/main.py`:**
```python
# Sprint 52: Stripe MCP server
from tools.stripe_mcp import StripeMCP, STRIPE_MCP_CONFIG
stripe = StripeMCP(mcp_manager)
await stripe.initialize()
```

**Dependencias nuevas:**
- `npm install -g @stripe/mcp` en Dockerfile (o `npx` lazy install)
- No hay dependencia Python nueva — usa `kernel/mcp_client.py` existente

**Variables de entorno nuevas en Railway:**
- `STRIPE_SECRET_KEY` — API key de Stripe de Alfredo

**Paso Magna obligatorio (Corrección C1):** Antes de implementar, verificar que `@stripe/mcp` está publicado en npm (fue anunciado hace 2 días — puede no estar disponible aún). Verificar los tool names reales del MCP server. Si no está disponible, fallback a Stripe SDK directo (`stripe` npm package).

**Criterio de éxito:**
- T0: Validación Magna confirma que @stripe/mcp existe en npm y los tool names son correctos
- T1: `create_product("Sneaker Air Max", "Limited edition", 15000)` crea producto + precio en Stripe
- T2: `create_checkout_session([{"price": price_id, "quantity": 1}], ...)` retorna URL de checkout funcional
- T3: `create_connect_account("seller@example.com")` crea cuenta de vendedor para marketplace

---

## Épica 52.3 — Railway Deploy Tool (Backend de Usuario)

**Objetivo que ataca:** #1 (empresas digitales), #7 (adoptar lo mejor)

**Qué hace:** Permite al Monstruo deployar backends completos (APIs, workers, websockets) para los proyectos que crea. No solo frontends estáticos en Vercel — backends reales en Railway.

**Por qué Railway:** El Monstruo ya corre en Railway. Ya conocemos la plataforma, ya tenemos cuenta, ya sabemos los costos. Railway soporta: Docker, Node.js, Python, Go, Rust, PostgreSQL, Redis, cron jobs, websockets, y auto-scaling. Es el mejor PaaS para startups en 2026 según múltiples comparativas [4].

**Archivo a crear:** `tools/railway_deploy.py`

```python
"""
El Monstruo — Railway Deploy Tool (Sprint 52)
==============================================
Deploys backend services to Railway for user projects.
Capabilities:
  - create_project: New Railway project
  - deploy_service: Deploy from GitHub repo or Dockerfile
  - add_database: Attach PostgreSQL/Redis to project
  - set_env_vars: Configure environment variables
  - get_deploy_url: Get the public URL of deployed service
  - get_logs: Stream deployment logs

Uses Railway API v2 (GraphQL):
  https://docs.railway.com/reference/public-api

Requires: RAILWAY_API_TOKEN env var
"""
from __future__ import annotations
import os
import httpx
import structlog

logger = structlog.get_logger("tools.railway_deploy")

RAILWAY_API_URL = "https://backboard.railway.com/graphql/v2"

class RailwayDeploy:
    def __init__(self):
        self.token = os.environ.get("RAILWAY_API_TOKEN")
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    async def _gql(self, query: str, variables: dict = None) -> dict:
        """Execute a GraphQL query against Railway API."""
        resp = await self.client.post(RAILWAY_API_URL, json={
            "query": query,
            "variables": variables or {},
        })
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise RuntimeError(f"Railway API error: {data['errors']}")
        return data["data"]

    async def create_project(self, name: str) -> dict:
        """Create a new Railway project."""
        result = await self._gql("""
            mutation($name: String!) {
                projectCreate(input: { name: $name }) {
                    id
                    name
                }
            }
        """, {"name": name})
        project = result["projectCreate"]
        logger.info("railway_project_created", project_id=project["id"])
        return project

    async def deploy_service(self, project_id: str, repo_url: str = None,
                              dockerfile: str = None,
                              env_vars: dict = None) -> dict:
        """Deploy a service to a Railway project."""
        # Create service
        service = await self._gql("""
            mutation($projectId: String!, $name: String) {
                serviceCreate(input: {
                    projectId: $projectId,
                    name: $name
                }) { id name }
            }
        """, {"projectId": project_id, "name": "backend"})

        service_id = service["serviceCreate"]["id"]

        # Set env vars if provided
        if env_vars:
            for key, value in env_vars.items():
                await self._gql("""
                    mutation($serviceId: String!, $name: String!, $value: String!) {
                        variableUpsert(input: {
                            serviceId: $serviceId,
                            name: $name,
                            value: $value
                        })
                    }
                """, {"serviceId": service_id, "name": key, "value": value})

        logger.info("railway_service_deployed", service_id=service_id)
        return {"service_id": service_id, "project_id": project_id}

    async def add_database(self, project_id: str,
                            db_type: str = "postgresql") -> dict:
        """Add a database plugin to a Railway project."""
        result = await self._gql("""
            mutation($projectId: String!, $plugin: String!) {
                pluginCreate(input: {
                    projectId: $projectId,
                    name: $plugin
                }) { id name }
            }
        """, {"projectId": project_id, "plugin": db_type})
        return result["pluginCreate"]
```

**Registro en tool_broker:**
```python
"railway_deploy": "tools.railway_deploy",
```

**Dependencias:** Ninguna nueva — usa `httpx`

**Variables de entorno nuevas:**
- `RAILWAY_API_TOKEN` — Token de API de Railway

**Paso Magna obligatorio (Corrección C1):** Verificar que Railway API v2 GraphQL mutations siguen vigentes. Railway cambia su API con frecuencia.

**Hardening checklist automático post-deploy (Corrección C3):**
Después de cada deploy exitoso, ejecutar automáticamente:
- Configurar CORS (origins permitidos)
- Activar rate limiting
- Security headers (Helmet.js o equivalente)
- Forzar SSL/HTTPS
- Crear health check endpoint (`/health`)
- Verificar que el servicio responde en <5s

**Criterio de éxito:**
- T0: Validación Magna confirma que Railway API v2 mutations son vigentes
- T1: `create_project("sneaker-marketplace-api")` crea proyecto en Railway
- T2: `deploy_service(project_id, repo_url="https://github.com/...")` deploya servicio
- T3: `add_database(project_id, "postgresql")` agrega Postgres al proyecto
- T4: Hardening checklist pasa (CORS, rate limit, headers, SSL, health check)

---

## Épica 52.4 — Media Generation Tool

**Objetivo que ataca:** #2 (nivel Apple/Tesla), #1 (empresas digitales necesitan assets)

**Qué hace:** Genera imágenes de alta calidad para los proyectos que El Monstruo crea — logos, hero images, product shots, backgrounds, assets de marca.

**Qué se adopta:** OpenAI GPT Image 2 (gpt-image-1 API) [5]. Es el mejor generador de imágenes con API directa en mayo 2026. Midjourney v7 tiene mejor calidad artística pero no tiene API programática. Flux.2 es open-source pero requiere GPU propia (viola Obj #7 en esta fase). GPT Image 2 tiene la mejor relación calidad/API/costo.

**Archivo a crear:** `tools/media_gen.py`

```python
"""
El Monstruo — Media Generation Tool (Sprint 52)
================================================
Generates images and visual assets for user projects.
Capabilities:
  - generate_image: Text-to-image via GPT Image 2
  - generate_logo: Specialized logo generation
  - generate_hero: Hero/banner image generation
  - edit_image: Image editing/inpainting

Uses OpenAI GPT Image 2 (gpt-image-1 model):
  https://platform.openai.com/docs/guides/images

Requires: OPENAI_API_KEY (already configured)
"""
from __future__ import annotations
import os
import base64
import httpx
import structlog

logger = structlog.get_logger("tools.media_gen")

class MediaGenerator:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=120.0,
        )

    async def generate_image(self, prompt: str,
                              size: str = "1024x1024",
                              quality: str = "high",
                              style: str = "natural",
                              n: int = 1) -> list[str]:
        """Generate image(s) from text prompt. Returns list of URLs."""
        resp = await self.client.post("/images/generations", json={
            "model": "gpt-image-1",
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n,
        })
        resp.raise_for_status()
        data = resp.json()
        urls = []
        for item in data["data"]:
            if "url" in item:
                urls.append(item["url"])
            elif "b64_json" in item:
                # Save to E2B sandbox and return path
                urls.append(f"data:image/png;base64,{item['b64_json'][:50]}...")
        logger.info("image_generated", prompt=prompt[:50], count=len(urls))
        return urls

    async def generate_logo(self, brand_name: str,
                             industry: str,
                             style: str = "minimal modern") -> list[str]:
        """Generate a brand logo with specialized prompt."""
        prompt = (
            f"Professional logo design for '{brand_name}', "
            f"a {industry} brand. Style: {style}. "
            f"Clean vector-like design, solid background, "
            f"suitable for web and print. No text artifacts."
        )
        return await self.generate_image(prompt, size="1024x1024",
                                          quality="high")

    async def generate_hero(self, description: str,
                             mood: str = "professional",
                             aspect: str = "1792x1024") -> list[str]:
        """Generate a hero/banner image for a website."""
        prompt = (
            f"Website hero banner image: {description}. "
            f"Mood: {mood}. High quality, photorealistic, "
            f"suitable as a full-width website banner. "
            f"No text overlays."
        )
        return await self.generate_image(prompt, size=aspect,
                                          quality="high")
```

**Registro en tool_broker:**
```python
"media_gen": "tools.media_gen",
```

**Dependencias:** Ninguna nueva — usa `httpx` + `OPENAI_API_KEY` existente

**Costo estimado:** ~$0.04-0.08 por imagen (GPT Image 2 pricing)

**Integración con Design System (Corrección C2):** Los prompts de `generate_logo` y `generate_hero` deben incluir como contexto los tokens del Design System Foundation (Sprint 51, Épica 51.5): paleta de colores, mood, estilo tipográfico. Las imágenes generadas deben ser coherentes entre sí y con la identidad visual del proyecto.

**Criterio de éxito:**
- T1: `generate_logo("SneakerVault", "e-commerce")` retorna URL de imagen de logo usable y coherente con Design System
- T2: `generate_hero("luxury sneaker marketplace with dark theme")` retorna banner de alta calidad alineado al mood del proyecto
- T3: Imagen generada se integra correctamente en un proyecto web_dev
- T4: 3 imágenes generadas para el mismo proyecto son visualmente coherentes entre sí

---

## Épica 52.5 — Activación de Langfuse en Producción

**Objetivo que ataca:** #6 (vanguardia — saber qué funciona), #4 (aprender de errores)

**Qué hace:** Langfuse ya está instalado (`langfuse==4.5.1`) y tiene bridge (`observability/langfuse_bridge.py`). Pero NO está activado en producción. Esta épica lo activa y conecta con el Error Memory del Sprint 51 para crear un loop de mejora continua.

**Por qué Langfuse y no solo Opik:** Langfuse es open-source, se puede self-host (Obj #12 — soberanía futura), tiene la mejor integración con LangGraph, y ya está en el código. Opik se mantiene como segundo canal (ya configurado Sprint 29). Langfuse se convierte en el canal primario [6].

**Cambios necesarios (no archivo nuevo — activación):**

**1. Variables de entorno en Railway:**
```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com  # o self-hosted URL
```

**2. Activar en `kernel/main.py` lifespan:**
```python
# Sprint 52: Activate Langfuse in production
from observability.manager import ObservabilityManager
obs = ObservabilityManager()
await obs.initialize()  # This already connects Langfuse + OTel + Opik
```

**3. Conectar con Error Memory (Sprint 51):**
Cuando Langfuse registra un trace con status "error", el hook post-error del Error Memory lo captura automáticamente. Esto crea el loop:

```
Tarea falla → Langfuse registra trace con error
                → Error Memory extrae root cause
                → Pre-flight check previene repetición
                → Langfuse registra trace exitoso
                → Loop de mejora continua
```

**4. Dashboard de métricas clave:**
- Tasa de éxito por tipo de tarea
- Costo promedio por tarea (tokens + tools)
- Latencia P50/P95 por nodo del grafo
- Top 10 errores más frecuentes
- Tendencia de mejora (errores que dejaron de repetirse)

**Criterio de éxito:**
- T1: Cada tarea ejecutada genera un trace visible en Langfuse Cloud
- T2: Los traces incluyen nodos individuales del LangGraph (think, execute, respond)
- T3: Los errores aparecen tanto en Langfuse como en Error Memory
- T4: El dashboard muestra métricas de las últimas 24h

---

## Épica 52.6 — Parallel Task Execution

**Objetivo que ataca:** #1 (crear empresas digitales requiere tareas paralelas), #3 (rapidez)

**Qué hace:** Permite al Monstruo ejecutar múltiples tareas en paralelo cuando son independientes. Por ejemplo: generar 5 imágenes + crear DB + configurar auth — todo al mismo tiempo en lugar de secuencial.

**Qué se adopta:** LangGraph parallel nodes — ya disponible en el stack actual. No se necesita framework externo [7].

**Archivo a modificar:** `kernel/multi_agent.py`

El Multi-Agent Dispatcher ya existe con agentes especializados (research, code, analysis, creative, ops). Lo que falta es la capacidad de ejecutar múltiples agentes EN PARALELO cuando las tareas son independientes.

```python
# Agregar a kernel/multi_agent.py:

async def execute_parallel(self, tasks: list[dict]) -> list[dict]:
    """
    Execute multiple independent tasks in parallel.
    Each task is routed to the appropriate agent.
    
    Args:
        tasks: List of {"description": str, "agent_type": AgentType}
    
    Returns:
        List of results in the same order as input tasks.
    """
    import asyncio
    
    async def _execute_single(task: dict) -> dict:
        agent_type = task.get("agent_type", AgentType.DEFAULT)
        result = await self.dispatch(task["description"], agent_type)
        return {"task": task["description"], "result": result}
    
    results = await asyncio.gather(
        *[_execute_single(t) for t in tasks],
        return_exceptions=True,
    )
    
    # Handle exceptions gracefully
    processed = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            logger.error("parallel_task_failed",
                        task=tasks[i]["description"], error=str(r))
            processed.append({
                "task": tasks[i]["description"],
                "result": None,
                "error": str(r),
            })
        else:
            processed.append(r)
    
    logger.info("parallel_execution_complete",
                total=len(tasks), failed=sum(1 for r in results if isinstance(r, Exception)))
    return processed
```

**Registro en task_planner:** Agregar `parallel_execute` como acción disponible en el planner para que pueda decidir cuándo paralelizar.

**Dependencias:** Ninguna nueva — usa `asyncio.gather` nativo

**Criterio de éxito:**
- T1: 3 tareas independientes ejecutan en paralelo (tiempo total < 1.5x la más lenta, no 3x)
- T2: Si una tarea falla, las otras completan normalmente
- T3: El planner identifica correctamente cuándo puede paralelizar

---

## Orden de Ejecución

```
Día 1-2:   52.5 Langfuse activación (rápido, solo config + env vars)
Día 2-3:   52.1 Supabase Provisioner (DB para proyectos)
Día 3-4:   52.4 Media Generation (imágenes para proyectos)
Día 4-6:   52.2 Stripe MCP (pagos — requiere cuenta Stripe)
Día 5-7:   52.3 Railway Deploy (backends de usuario)
Día 6-8:   52.6 Parallel Execution (optimización)
Día 8-10:  Integration test E2E completo
```

**Test E2E del Sprint 52:**

> "Crea un marketplace de sneakers con: landing page, catálogo de productos, carrito de compras, checkout con Stripe, panel de admin para vendedores, y base de datos."

El Monstruo debe:
1. Crear proyecto Supabase (DB + Auth + Storage) ← 52.1
2. Generar logo + hero image + product shots ← 52.4 (en paralelo con 1)
3. Scaffoldear frontend React + backend FastAPI ← web_dev.py existente
4. Configurar Stripe Connect para marketplace ← 52.2
5. Deployar frontend a Vercel + backend a Railway ← web_dev.py + 52.3
6. Todo trazado en Langfuse ← 52.5
7. Pasos 1-2 ejecutados en paralelo ← 52.6

**Test E2E dividido en 3 niveles (Corrección C5):**

**Nivel 1 — Smoke Test:**
- Crear proyecto Supabase → crear tabla → insertar dato → leer dato → funciona
- Generar 1 imagen → se descarga correctamente → funciona
- Crear proyecto Railway → health check responde → funciona

**Nivel 2 — Integration Test:**
- Frontend scaffoldeado + Backend deployado + DB conectada → la app carga
- Stripe checkout session creada → URL funcional → se puede pagar
- Langfuse registra traces de todo lo anterior

**Nivel 3 — Full E2E:**
- Marketplace completo: landing + catálogo + carrito + checkout + admin
- Un usuario puede ver productos, agregar al carrito, pagar con Stripe, y el vendedor recibe su payout

Solo avanzar al siguiente nivel si el anterior pasa al 100%.

---

## Deuda Documentada para Sprint 53 (Corrección C4)

El Sprint 52 cubre infraestructura de creación pero NO cubre las capas transversales del Objetivo #9. Quedan como deuda explícita para Sprint 53:
- **SEO técnico:** Meta tags, sitemap.xml, schema.org, Open Graph
- **Analytics:** Eventos, funnels, retention (Plausible o PostHog)
- **Email transaccional:** Confirmaciones, onboarding, recuperación de password (Resend o SendGrid)
- **Templates de arquitectura:** Patrones pre-diseñados para marketplace, SaaS, social network

---

## Resumen de Archivos

| Archivo | Acción | Épica |
|---|---|---|
| `tools/supabase_provisioner.py` | CREAR | 52.1 |
| `tools/stripe_mcp.py` | CREAR | 52.2 |
| `tools/railway_deploy.py` | CREAR | 52.3 |
| `tools/media_gen.py` | CREAR | 52.4 |
| `kernel/main.py` | MODIFICAR (activar Langfuse) | 52.5 |
| `kernel/multi_agent.py` | MODIFICAR (agregar parallel) | 52.6 |
| `kernel/tool_broker.py` | MODIFICAR (registrar 4 tools) | Todas |
| `requirements.txt` | SIN CAMBIOS | — |
| `Dockerfile` | MODIFICAR (npm install @stripe/mcp) | 52.2 |

---

## Costo Estimado Adicional por Mes

| Componente | Costo |
|---|---|
| Langfuse Cloud (free tier: 50K traces) | $0 |
| Supabase free tier por proyecto | $0 (2 proyectos gratis) |
| Supabase Pro (si se necesita) | $25/proyecto |
| Railway (proyectos de usuario) | ~$5-20/proyecto |
| Stripe | 2.9% + $0.30 por transacción |
| GPT Image 2 | ~$0.04-0.08/imagen |
| **Total base (sin proyectos de usuario)** | **~$0-5** |
| **Total con 1 proyecto marketplace activo** | **~$30-50** |

---

## Referencias

[1] Supabase Management API v1 — https://supabase.com/docs/reference/api/introduction
[2] Stripe Sessions 2026 Announcements — https://stripe.com/blog/everything-we-announced-at-sessions-2026
[3] The AI Agent Stack in 2026 — https://thenuancedperspective.substack.com/p/the-ai-agent-stack-in-2026
[4] Railway vs Render vs Fly.io comparison — https://www.buildmvpfast.com/blog/best-cloud-services-mvp-hosting-2026
[5] OpenAI Image Generation API — https://platform.openai.com/docs/guides/images
[6] Langfuse vs LangSmith comparison — https://pub.towardsai.net/langfuse-vs-langsmith-two-competing-ai-observability-platforms-compared-2527a5ce023b
[7] LangGraph parallel execution — https://langchain-ai.github.io/langgraph/
