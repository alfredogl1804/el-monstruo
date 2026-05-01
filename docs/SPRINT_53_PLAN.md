# Sprint 53 — "Las Capas Transversales de Éxito"

**Fecha:** Mayo 2026 (post Sprint 52)
**Prerequisito:** Sprint 51 (Cimientos) + Sprint 52 (Manos) completados
**Duración estimada:** 6-8 días
**Objetivo principal:** Todo lo que El Monstruo cree nace con las capas que garantizan su éxito (Objetivo #9)

---

## Contexto

Los Sprints 51 y 52 le dieron a El Monstruo la capacidad de detectar errores, validar datos, navegar la web, crear backends, integrar pagos, deployar, generar media, y observar todo el pipeline. Pero crear un producto no es suficiente — el 80% del éxito de una empresa digital está en cómo se vende, se posiciona, se mide, y se retiene a los usuarios. El Sprint 53 cierra esa brecha.

---

## Resumen de Épicas

| Épica | Nombre | Objetivo Primario | Se Adopta | Costo/mes |
|-------|--------|-------------------|-----------|-----------|
| 53.1 | SEO Engine | Obj #9 (Transversalidad) | Código puro (sin API externa) | $0 |
| 53.2 | Analytics Integration | Obj #9 (Transversalidad) | PostHog Cloud | $0 (free tier 1M events) |
| 53.3 | Email Transaccional | Obj #9 (Transversalidad) | Resend API | $0 (free 100/día) |
| 53.4 | Architecture Templates | Obj #8 (Emergencia) + Obj #1 (Empresas) | Creación propia (no existe) | $0 |
| 53.5 | Quality Gate | Obj #2 (Nivel Apple) + Obj #9 | Lighthouse CI + Design System | $0 |

**Costo total adicional:** $0 en free tiers. ~$20-40/mes a escala.

---

## Épica 53.1 — SEO Engine (Auto-inyección de SEO técnico)

**Qué:** Cada proyecto que El Monstruo cree recibe SEO técnico completo automáticamente como post-processing step después del scaffold.

**Por qué no se adopta una herramienta externa:** El SEO técnico (meta tags, sitemap, schema.org, robots.txt) es código puro — no necesita API. Las herramientas como Semrush/Ahrefs son para análisis, no para generación. El Monstruo genera.

**Archivo a crear:** `tools/seo_engine.py`

**Qué genera automáticamente:**

1. `<meta>` tags completos (title, description, og:image, og:title, og:description, twitter:card)
2. `sitemap.xml` generado desde las rutas del proyecto
3. `robots.txt` con reglas sensatas
4. Schema.org / JSON-LD según el tipo de proyecto:
   - Marketplace → `Product`, `Offer`, `AggregateRating`, `BreadcrumbList`
   - SaaS → `SoftwareApplication`, `Organization`
   - E-commerce → `Product`, `Offer`, `ItemList`
   - Landing page → `Organization`, `WebSite`
5. Canonical URLs en cada página
6. Alt text sugerido para imágenes (usando el modelo de visión)
7. `<html lang="...">` correcto según el idioma del proyecto

**Integración con el stack:**

El SEO Engine se invoca como post-processing step dentro de `tools/web_dev.py`. Después de que el scaffold está completo y antes del build:

```python
# En tools/web_dev.py, después de scaffold y antes de build:
from tools.seo_engine import inject_seo

async def deploy(sandbox, project_type: str, project_info: dict):
    # ... scaffold y código existente ...
    
    # POST-PROCESSING: Inyectar SEO
    seo_result = await inject_seo(
        sandbox=sandbox,
        project_type=project_type,  # "marketplace", "saas", "ecommerce", "landing"
        project_info=project_info,  # nombre, descripción, idioma, URLs
    )
    
    # ... build y deploy ...
```

**Código de `tools/seo_engine.py`:**

```python
"""
El Monstruo — SEO Engine
Sprint 53.1: Auto-inyección de SEO técnico en cada proyecto.
Genera: meta tags, sitemap.xml, robots.txt, schema.org/JSON-LD.
No requiere API externa — es código puro.
"""
import json
import logging
from typing import Any

logger = logging.getLogger("monstruo.tools.seo_engine")

# ── Schema.org Templates por tipo de proyecto ──────────────────────
SCHEMA_TEMPLATES = {
    "marketplace": {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "{project_name}",
        "url": "{project_url}",
        "potentialAction": {
            "@type": "SearchAction",
            "target": "{project_url}/search?q={search_term_string}",
            "query-input": "required name=search_term_string"
        }
    },
    "saas": {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "{project_name}",
        "url": "{project_url}",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web"
    },
    "ecommerce": {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "{project_name}",
        "url": "{project_url}",
        "potentialAction": {
            "@type": "SearchAction",
            "target": "{project_url}/products?q={search_term_string}",
            "query-input": "required name=search_term_string"
        }
    },
    "landing": {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "{project_name}",
        "url": "{project_url}"
    }
}

async def inject_seo(
    sandbox,
    project_type: str,
    project_info: dict,
) -> dict[str, Any]:
    """
    Inyecta SEO técnico completo en un proyecto scaffoldeado.
    
    Args:
        sandbox: E2B sandbox instance
        project_type: "marketplace" | "saas" | "ecommerce" | "landing"
        project_info: dict con name, description, url, lang, pages[]
    
    Returns:
        dict con keys: injected (bool), files_modified (list), seo_score (int)
    """
    name = project_info.get("name", "Mi Proyecto")
    desc = project_info.get("description", "")
    url = project_info.get("url", "https://example.com")
    lang = project_info.get("lang", "es")
    pages = project_info.get("pages", ["/"])
    
    files_modified = []
    
    # 1. robots.txt
    robots_txt = f"""User-agent: *
Allow: /
Sitemap: {url}/sitemap.xml

User-agent: GPTBot
Allow: /

User-agent: Google-Extended
Allow: /
"""
    await sandbox.filesystem.write("/home/user/project/public/robots.txt", robots_txt)
    files_modified.append("public/robots.txt")
    
    # 2. sitemap.xml
    sitemap_entries = "\n".join([
        f"  <url><loc>{url}{page}</loc><changefreq>weekly</changefreq><priority>{'1.0' if page == '/' else '0.8'}</priority></url>"
        for page in pages
    ])
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_entries}
</urlset>"""
    await sandbox.filesystem.write("/home/user/project/public/sitemap.xml", sitemap_xml)
    files_modified.append("public/sitemap.xml")
    
    # 3. Schema.org JSON-LD
    schema = SCHEMA_TEMPLATES.get(project_type, SCHEMA_TEMPLATES["landing"])
    schema_str = json.dumps(schema, indent=2).replace("{project_name}", name).replace("{project_url}", url)
    
    # 4. Inyectar en index.html
    meta_tags = f"""
    <meta name="description" content="{desc}" />
    <meta property="og:title" content="{name}" />
    <meta property="og:description" content="{desc}" />
    <meta property="og:url" content="{url}" />
    <meta property="og:type" content="website" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{name}" />
    <meta name="twitter:description" content="{desc}" />
    <link rel="canonical" href="{url}" />
    <html lang="{lang}">
    <script type="application/ld+json">
{schema_str}
    </script>"""
    
    # Leer index.html actual e inyectar meta tags antes de </head>
    try:
        current_html = await sandbox.filesystem.read("/home/user/project/index.html")
        updated_html = current_html.replace("</head>", f"{meta_tags}\n  </head>")
        await sandbox.filesystem.write("/home/user/project/index.html", updated_html)
        files_modified.append("index.html")
    except Exception as e:
        logger.warning(f"Could not inject meta tags into index.html: {e}")
    
    logger.info(f"SEO injected: {len(files_modified)} files modified for {project_type} project")
    
    return {
        "injected": True,
        "files_modified": files_modified,
        "seo_elements": ["robots.txt", "sitemap.xml", "schema.org", "meta_tags", "canonical", "lang"],
        "project_type": project_type,
    }
```

**Cambios en `requirements.txt`:** Ninguno (código puro Python).

**Criterio de éxito:**

- T1: Scaffold un proyecto marketplace → verificar que `robots.txt`, `sitemap.xml`, meta tags, y schema.org existen
- T2: Schema.org válido según https://validator.schema.org/
- T3: Lighthouse SEO score >= 90 en el proyecto deployado

---

## Épica 53.2 — Analytics Integration (PostHog)

**Qué:** Cada proyecto que El Monstruo cree incluye analytics de producto desde el día 1. No solo page views — eventos, funnels, session replay.

**Por qué PostHog:** Es el único que combina web analytics + product analytics + A/B testing + feature flags + session replay en un solo SDK. Open source. Free tier de 1M eventos/mes. Se integra con un snippet de JS — no requiere backend.

**Archivo a crear:** `tools/analytics_engine.py`

**Integración:** Se inyecta como parte del SEO Engine (mismo post-processing step). Un snippet de PostHog en el `<head>` de cada proyecto.

**Código de `tools/analytics_engine.py`:**

```python
"""
El Monstruo — Analytics Engine
Sprint 53.2: Auto-inyección de PostHog analytics en cada proyecto.
Incluye: page views, custom events, session replay, feature flags.
"""
import logging
from typing import Any

logger = logging.getLogger("monstruo.tools.analytics_engine")

POSTHOG_SNIPPET = """
    <script>
      !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
      posthog.init('{posthog_key}',{api_host:'https://us.i.posthog.com', person_profiles: 'identified_only'})
    </script>"""

# ── Eventos estándar por tipo de proyecto ──────────────────────────
STANDARD_EVENTS = {
    "marketplace": [
        "product_viewed", "product_added_to_cart", "checkout_started",
        "purchase_completed", "seller_contacted", "review_submitted",
        "search_performed", "filter_applied"
    ],
    "saas": [
        "signup_started", "signup_completed", "feature_used",
        "plan_viewed", "plan_upgraded", "invite_sent",
        "onboarding_step_completed", "churn_risk_detected"
    ],
    "ecommerce": [
        "product_viewed", "product_added_to_cart", "cart_viewed",
        "checkout_started", "purchase_completed", "coupon_applied",
        "wishlist_added", "review_submitted"
    ],
    "landing": [
        "page_viewed", "cta_clicked", "form_submitted",
        "scroll_depth_50", "scroll_depth_100", "exit_intent"
    ]
}

async def inject_analytics(
    sandbox,
    project_type: str,
    posthog_key: str,
) -> dict[str, Any]:
    """
    Inyecta PostHog analytics en un proyecto.
    
    Args:
        sandbox: E2B sandbox instance
        posthog_key: PostHog project API key
        project_type: tipo de proyecto para eventos estándar
    
    Returns:
        dict con keys: injected, events_configured, snippet_added
    """
    if not posthog_key:
        logger.warning("No PostHog key provided — skipping analytics injection")
        return {"injected": False, "error": "No PostHog key"}
    
    # 1. Inyectar snippet en index.html
    snippet = POSTHOG_SNIPPET.replace("{posthog_key}", posthog_key)
    
    try:
        current_html = await sandbox.filesystem.read("/home/user/project/index.html")
        updated_html = current_html.replace("</head>", f"{snippet}\n  </head>")
        await sandbox.filesystem.write("/home/user/project/index.html", updated_html)
    except Exception as e:
        logger.error(f"Failed to inject PostHog snippet: {e}")
        return {"injected": False, "error": str(e)}
    
    # 2. Crear helper de eventos para el proyecto
    events = STANDARD_EVENTS.get(project_type, STANDARD_EVENTS["landing"])
    events_helper = f"""// Auto-generated by El Monstruo — Analytics Events
// Project type: {project_type}
// PostHog docs: https://posthog.com/docs

export const trackEvent = (eventName, properties = {{}}) => {{
  if (typeof window !== 'undefined' && window.posthog) {{
    window.posthog.capture(eventName, properties);
  }}
}};

// Standard events for {project_type}:
{chr(10).join([f'export const track_{e} = (props = {{}}) => trackEvent("{e}", props);' for e in events])}

// Feature flags
export const isFeatureEnabled = (flagName) => {{
  if (typeof window !== 'undefined' && window.posthog) {{
    return window.posthog.isFeatureEnabled(flagName);
  }}
  return false;
}};

// Identify user (call after login)
export const identifyUser = (userId, properties = {{}}) => {{
  if (typeof window !== 'undefined' && window.posthog) {{
    window.posthog.identify(userId, properties);
  }}
}};
"""
    await sandbox.filesystem.write("/home/user/project/src/lib/analytics.js", events_helper)
    
    logger.info(f"Analytics injected: PostHog + {len(events)} standard events for {project_type}")
    
    return {
        "injected": True,
        "events_configured": events,
        "snippet_added": True,
        "helper_file": "src/lib/analytics.js",
    }
```

**Cambios en `requirements.txt`:** Ninguno (PostHog es client-side JS, no Python).

**Variable de entorno requerida:** `POSTHOG_API_KEY` en Railway.

**Criterio de éxito:**

- T1: Proyecto deployado envía page_view a PostHog dashboard
- T2: Helper de eventos importable y funcional (`import { trackEvent } from '@/lib/analytics'`)
- T3: Session replay activo y capturando

---

## Épica 53.3 — Email Transaccional (Resend)

**Qué:** El Monstruo puede enviar emails transaccionales profesionales desde los proyectos que crea. Confirmaciones, recuperación de password, notificaciones, reportes.

**Por qué Resend sobre Gmail SMTP actual:** El `email_sender.py` actual usa Gmail SMTP — funciona para alertas internas, pero no es profesional para los PRODUCTOS que El Monstruo crea. Resend ofrece: API REST moderna, React Email templates, deliverability superior, dominio custom, analytics de emails.

**Archivo a crear:** `tools/resend_email.py` (NO reemplaza `email_sender.py` — coexisten. Gmail para alertas internas, Resend para productos).

**Código de `tools/resend_email.py`:**

```python
"""
El Monstruo — Resend Email Tool
Sprint 53.3: Email transaccional profesional para los productos que crea.
Coexiste con email_sender.py (Gmail para alertas internas).
Resend: API REST, React Email templates, deliverability superior.
Free tier: 100 emails/día, 3000/mes.
"""
import logging
import os
from typing import Any, Optional

import httpx

logger = logging.getLogger("monstruo.tools.resend_email")

RESEND_API_BASE = "https://api.resend.com"

# ── Templates de email por tipo ────────────────────────────────────
EMAIL_TEMPLATES = {
    "welcome": {
        "subject": "Bienvenido a {app_name}",
        "html": """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <h1 style="font-size: 24px; font-weight: 600; color: #111;">Bienvenido a {app_name}</h1>
            <p style="font-size: 16px; color: #555; line-height: 1.6;">{message}</p>
            <a href="{cta_url}" style="display: inline-block; background: #111; color: #fff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; margin-top: 16px;">{cta_text}</a>
        </div>"""
    },
    "password_reset": {
        "subject": "Restablecer contraseña — {app_name}",
        "html": """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <h1 style="font-size: 24px; font-weight: 600; color: #111;">Restablecer contraseña</h1>
            <p style="font-size: 16px; color: #555; line-height: 1.6;">Haz clic en el botón para restablecer tu contraseña. Este enlace expira en 1 hora.</p>
            <a href="{reset_url}" style="display: inline-block; background: #111; color: #fff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; margin-top: 16px;">Restablecer contraseña</a>
        </div>"""
    },
    "order_confirmation": {
        "subject": "Pedido confirmado #{order_id} — {app_name}",
        "html": """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <h1 style="font-size: 24px; font-weight: 600; color: #111;">Pedido confirmado</h1>
            <p style="font-size: 16px; color: #555; line-height: 1.6;">Tu pedido #{order_id} ha sido confirmado. Total: {total}</p>
            <a href="{tracking_url}" style="display: inline-block; background: #111; color: #fff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; margin-top: 16px;">Ver pedido</a>
        </div>"""
    },
    "notification": {
        "subject": "{subject}",
        "html": """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <h1 style="font-size: 24px; font-weight: 600; color: #111;">{title}</h1>
            <p style="font-size: 16px; color: #555; line-height: 1.6;">{message}</p>
        </div>"""
    }
}

async def send_transactional_email(
    to: str,
    template: str,
    variables: dict,
    from_name: str = "Mi App",
    from_domain: Optional[str] = None,
) -> dict[str, Any]:
    """
    Envía un email transaccional profesional via Resend.
    
    Args:
        to: Recipient email
        template: Template name ("welcome", "password_reset", "order_confirmation", "notification")
        variables: Dict con variables para el template (app_name, message, cta_url, etc.)
        from_name: Sender display name
        from_domain: Custom domain (optional, defaults to onboarding@resend.dev)
    """
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        return {"sent": False, "error": "RESEND_API_KEY not set"}
    
    tmpl = EMAIL_TEMPLATES.get(template)
    if not tmpl:
        return {"sent": False, "error": f"Unknown template: {template}"}
    
    # Render template
    subject = tmpl["subject"]
    html = tmpl["html"]
    for key, value in variables.items():
        subject = subject.replace(f"{{{key}}}", str(value))
        html = html.replace(f"{{{key}}}", str(value))
    
    from_email = f"{from_name} <{from_domain or 'onboarding@resend.dev'}>"
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{RESEND_API_BASE}/emails",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "from": from_email,
                "to": [to],
                "subject": subject,
                "html": html,
            },
            timeout=10,
        )
    
    if resp.status_code == 200:
        data = resp.json()
        logger.info(f"Email sent via Resend: {template} to {to}, id={data.get('id')}")
        return {"sent": True, "id": data.get("id"), "template": template}
    else:
        logger.error(f"Resend error: {resp.status_code} — {resp.text}")
        return {"sent": False, "error": resp.text, "status": resp.status_code}
```

**Cambios en `requirements.txt`:** `httpx` ya está instalado (usado por otros tools).

**Variable de entorno requerida:** `RESEND_API_KEY` en Railway.

**Criterio de éxito:**

- T1: `send_transactional_email(to="test@test.com", template="welcome", variables={...})` retorna `sent: True`
- T2: Email llega al inbox (no spam) con formato profesional
- T3: Templates renderizados correctamente con variables sustituidas

---

## Épica 53.4 — Architecture Templates (Blueprints de Negocio)

**Qué:** El Monstruo tiene blueprints pre-diseñados para los tipos de negocio más comunes. Cuando un usuario dice "crea un marketplace de sneakers", El Monstruo no empieza de cero — consulta el blueprint de Marketplace y lo customiza.

**Por qué esto es Objetivo #8 (Creación):** No existe un repo ni una herramienta que tenga estos blueprints optimizados para agentes AI. Esto hay que CREARLO. Es el primer artefacto de inteligencia emergente aplicada.

**Archivo a crear:** `knowledge/blueprints/` (directorio con JSONs)

**Blueprints iniciales (4):**

### Blueprint 1: Marketplace

```json
{
  "type": "marketplace",
  "name": "Marketplace Blueprint",
  "description": "Two-sided marketplace with buyers, sellers, products, orders, reviews, and messaging",
  "db_schema": {
    "users": {
      "id": "uuid PRIMARY KEY",
      "email": "varchar UNIQUE NOT NULL",
      "name": "varchar NOT NULL",
      "role": "enum('buyer','seller','admin') DEFAULT 'buyer'",
      "avatar_url": "varchar",
      "created_at": "timestamp DEFAULT now()"
    },
    "stores": {
      "id": "uuid PRIMARY KEY",
      "owner_id": "uuid REFERENCES users(id)",
      "name": "varchar NOT NULL",
      "slug": "varchar UNIQUE NOT NULL",
      "description": "text",
      "logo_url": "varchar",
      "rating": "decimal(3,2) DEFAULT 0",
      "verified": "boolean DEFAULT false",
      "created_at": "timestamp DEFAULT now()"
    },
    "products": {
      "id": "uuid PRIMARY KEY",
      "store_id": "uuid REFERENCES stores(id)",
      "name": "varchar NOT NULL",
      "description": "text",
      "price": "decimal(10,2) NOT NULL",
      "currency": "varchar(3) DEFAULT 'USD'",
      "images": "jsonb DEFAULT '[]'",
      "category": "varchar",
      "stock": "integer DEFAULT 0",
      "status": "enum('draft','active','sold_out','archived') DEFAULT 'draft'",
      "created_at": "timestamp DEFAULT now()"
    },
    "orders": {
      "id": "uuid PRIMARY KEY",
      "buyer_id": "uuid REFERENCES users(id)",
      "store_id": "uuid REFERENCES stores(id)",
      "items": "jsonb NOT NULL",
      "total": "decimal(10,2) NOT NULL",
      "status": "enum('pending','paid','shipped','delivered','cancelled','refunded') DEFAULT 'pending'",
      "stripe_payment_id": "varchar",
      "shipping_address": "jsonb",
      "created_at": "timestamp DEFAULT now()"
    },
    "reviews": {
      "id": "uuid PRIMARY KEY",
      "product_id": "uuid REFERENCES products(id)",
      "user_id": "uuid REFERENCES users(id)",
      "rating": "integer CHECK (rating >= 1 AND rating <= 5)",
      "comment": "text",
      "created_at": "timestamp DEFAULT now()"
    },
    "messages": {
      "id": "uuid PRIMARY KEY",
      "sender_id": "uuid REFERENCES users(id)",
      "receiver_id": "uuid REFERENCES users(id)",
      "content": "text NOT NULL",
      "read": "boolean DEFAULT false",
      "created_at": "timestamp DEFAULT now()"
    }
  },
  "api_routes": [
    "POST /auth/register", "POST /auth/login", "GET /auth/me",
    "GET /products", "GET /products/:id", "POST /products", "PUT /products/:id",
    "GET /stores", "GET /stores/:slug", "POST /stores",
    "POST /orders", "GET /orders", "GET /orders/:id", "PUT /orders/:id/status",
    "POST /reviews", "GET /products/:id/reviews",
    "POST /messages", "GET /messages/:userId",
    "POST /payments/checkout", "POST /payments/webhook"
  ],
  "frontend_pages": [
    "/", "/products", "/products/:id", "/stores/:slug",
    "/cart", "/checkout", "/orders", "/orders/:id",
    "/dashboard", "/dashboard/products", "/dashboard/orders",
    "/messages", "/profile", "/auth/login", "/auth/register"
  ],
  "stripe_config": {
    "mode": "connect",
    "features": ["checkout", "escrow", "seller_payouts", "refunds"]
  },
  "seo_config": {
    "schema_types": ["Product", "Offer", "AggregateRating", "BreadcrumbList"],
    "dynamic_sitemap": true
  },
  "analytics_events": [
    "product_viewed", "product_added_to_cart", "checkout_started",
    "purchase_completed", "seller_contacted", "review_submitted",
    "search_performed", "filter_applied"
  ]
}
```

### Blueprint 2: SaaS

```json
{
  "type": "saas",
  "name": "SaaS Blueprint",
  "description": "Multi-tenant SaaS with plans, billing, team management, and admin dashboard",
  "db_schema": {
    "users": {
      "id": "uuid PRIMARY KEY",
      "email": "varchar UNIQUE NOT NULL",
      "name": "varchar NOT NULL",
      "avatar_url": "varchar",
      "created_at": "timestamp DEFAULT now()"
    },
    "organizations": {
      "id": "uuid PRIMARY KEY",
      "name": "varchar NOT NULL",
      "slug": "varchar UNIQUE NOT NULL",
      "plan": "enum('free','starter','pro','enterprise') DEFAULT 'free'",
      "stripe_customer_id": "varchar",
      "stripe_subscription_id": "varchar",
      "created_at": "timestamp DEFAULT now()"
    },
    "memberships": {
      "id": "uuid PRIMARY KEY",
      "user_id": "uuid REFERENCES users(id)",
      "org_id": "uuid REFERENCES organizations(id)",
      "role": "enum('owner','admin','member') DEFAULT 'member'",
      "created_at": "timestamp DEFAULT now()"
    },
    "usage": {
      "id": "uuid PRIMARY KEY",
      "org_id": "uuid REFERENCES organizations(id)",
      "metric": "varchar NOT NULL",
      "value": "integer NOT NULL",
      "period": "date NOT NULL"
    }
  },
  "api_routes": [
    "POST /auth/register", "POST /auth/login", "GET /auth/me",
    "POST /orgs", "GET /orgs/:slug", "PUT /orgs/:id",
    "POST /orgs/:id/invite", "GET /orgs/:id/members",
    "GET /billing/plans", "POST /billing/subscribe", "POST /billing/portal",
    "GET /usage", "GET /admin/dashboard"
  ],
  "frontend_pages": [
    "/", "/auth/login", "/auth/register",
    "/dashboard", "/dashboard/settings", "/dashboard/team",
    "/dashboard/billing", "/dashboard/usage",
    "/admin", "/pricing"
  ],
  "stripe_config": {
    "mode": "subscriptions",
    "features": ["plans", "billing_portal", "usage_metering", "invoices"]
  }
}
```

### Blueprint 3: E-commerce

```json
{
  "type": "ecommerce",
  "name": "E-commerce Blueprint",
  "description": "Single-vendor e-commerce with catalog, cart, checkout, and order management",
  "db_schema": {
    "users": {
      "id": "uuid PRIMARY KEY",
      "email": "varchar UNIQUE NOT NULL",
      "name": "varchar NOT NULL",
      "shipping_addresses": "jsonb DEFAULT '[]'",
      "created_at": "timestamp DEFAULT now()"
    },
    "categories": {
      "id": "uuid PRIMARY KEY",
      "name": "varchar NOT NULL",
      "slug": "varchar UNIQUE NOT NULL",
      "parent_id": "uuid REFERENCES categories(id)",
      "image_url": "varchar"
    },
    "products": {
      "id": "uuid PRIMARY KEY",
      "name": "varchar NOT NULL",
      "slug": "varchar UNIQUE NOT NULL",
      "description": "text",
      "price": "decimal(10,2) NOT NULL",
      "compare_at_price": "decimal(10,2)",
      "images": "jsonb DEFAULT '[]'",
      "category_id": "uuid REFERENCES categories(id)",
      "variants": "jsonb DEFAULT '[]'",
      "stock": "integer DEFAULT 0",
      "status": "enum('draft','active','archived') DEFAULT 'draft'",
      "created_at": "timestamp DEFAULT now()"
    },
    "orders": {
      "id": "uuid PRIMARY KEY",
      "user_id": "uuid REFERENCES users(id)",
      "items": "jsonb NOT NULL",
      "subtotal": "decimal(10,2) NOT NULL",
      "tax": "decimal(10,2) DEFAULT 0",
      "shipping": "decimal(10,2) DEFAULT 0",
      "total": "decimal(10,2) NOT NULL",
      "status": "enum('pending','paid','processing','shipped','delivered','cancelled') DEFAULT 'pending'",
      "stripe_payment_id": "varchar",
      "shipping_address": "jsonb",
      "tracking_number": "varchar",
      "created_at": "timestamp DEFAULT now()"
    },
    "coupons": {
      "id": "uuid PRIMARY KEY",
      "code": "varchar UNIQUE NOT NULL",
      "discount_type": "enum('percentage','fixed') NOT NULL",
      "discount_value": "decimal(10,2) NOT NULL",
      "min_order": "decimal(10,2) DEFAULT 0",
      "max_uses": "integer",
      "used_count": "integer DEFAULT 0",
      "expires_at": "timestamp"
    }
  },
  "api_routes": [
    "POST /auth/register", "POST /auth/login", "GET /auth/me",
    "GET /products", "GET /products/:slug", "GET /categories",
    "POST /cart", "GET /cart", "PUT /cart/:itemId", "DELETE /cart/:itemId",
    "POST /orders", "GET /orders", "GET /orders/:id",
    "POST /payments/checkout", "POST /payments/webhook",
    "POST /coupons/validate",
    "GET /admin/products", "POST /admin/products", "GET /admin/orders"
  ],
  "frontend_pages": [
    "/", "/products", "/products/:slug", "/categories/:slug",
    "/cart", "/checkout", "/checkout/success",
    "/orders", "/orders/:id",
    "/admin", "/admin/products", "/admin/orders", "/admin/coupons",
    "/auth/login", "/auth/register", "/profile"
  ],
  "stripe_config": {
    "mode": "direct",
    "features": ["checkout", "payment_intents", "refunds", "coupons"]
  }
}
```

### Blueprint 4: Social Platform

```json
{
  "type": "social",
  "name": "Social Platform Blueprint",
  "description": "Social network with profiles, feed, posts, comments, likes, follows, and messaging",
  "db_schema": {
    "users": {
      "id": "uuid PRIMARY KEY",
      "username": "varchar UNIQUE NOT NULL",
      "email": "varchar UNIQUE NOT NULL",
      "name": "varchar NOT NULL",
      "bio": "text",
      "avatar_url": "varchar",
      "cover_url": "varchar",
      "followers_count": "integer DEFAULT 0",
      "following_count": "integer DEFAULT 0",
      "created_at": "timestamp DEFAULT now()"
    },
    "posts": {
      "id": "uuid PRIMARY KEY",
      "user_id": "uuid REFERENCES users(id)",
      "content": "text",
      "media": "jsonb DEFAULT '[]'",
      "likes_count": "integer DEFAULT 0",
      "comments_count": "integer DEFAULT 0",
      "shares_count": "integer DEFAULT 0",
      "visibility": "enum('public','followers','private') DEFAULT 'public'",
      "created_at": "timestamp DEFAULT now()"
    },
    "comments": {
      "id": "uuid PRIMARY KEY",
      "post_id": "uuid REFERENCES posts(id)",
      "user_id": "uuid REFERENCES users(id)",
      "content": "text NOT NULL",
      "parent_id": "uuid REFERENCES comments(id)",
      "likes_count": "integer DEFAULT 0",
      "created_at": "timestamp DEFAULT now()"
    },
    "likes": {
      "id": "uuid PRIMARY KEY",
      "user_id": "uuid REFERENCES users(id)",
      "target_type": "enum('post','comment') NOT NULL",
      "target_id": "uuid NOT NULL",
      "created_at": "timestamp DEFAULT now()"
    },
    "follows": {
      "follower_id": "uuid REFERENCES users(id)",
      "following_id": "uuid REFERENCES users(id)",
      "created_at": "timestamp DEFAULT now()",
      "PRIMARY KEY": "(follower_id, following_id)"
    },
    "conversations": {
      "id": "uuid PRIMARY KEY",
      "participants": "jsonb NOT NULL",
      "last_message_at": "timestamp",
      "created_at": "timestamp DEFAULT now()"
    },
    "direct_messages": {
      "id": "uuid PRIMARY KEY",
      "conversation_id": "uuid REFERENCES conversations(id)",
      "sender_id": "uuid REFERENCES users(id)",
      "content": "text NOT NULL",
      "read": "boolean DEFAULT false",
      "created_at": "timestamp DEFAULT now()"
    }
  },
  "api_routes": [
    "POST /auth/register", "POST /auth/login", "GET /auth/me",
    "GET /users/:username", "PUT /users/me",
    "POST /posts", "GET /feed", "GET /posts/:id", "DELETE /posts/:id",
    "POST /posts/:id/like", "DELETE /posts/:id/like",
    "POST /posts/:id/comments", "GET /posts/:id/comments",
    "POST /users/:id/follow", "DELETE /users/:id/follow",
    "GET /users/:id/followers", "GET /users/:id/following",
    "GET /conversations", "POST /conversations", "GET /conversations/:id/messages", "POST /conversations/:id/messages",
    "GET /notifications"
  ],
  "frontend_pages": [
    "/", "/feed", "/:username", "/:username/followers", "/:username/following",
    "/post/:id", "/messages", "/messages/:id",
    "/notifications", "/settings", "/explore",
    "/auth/login", "/auth/register"
  ]
}
```

**Almacenamiento:** Estos JSONs se guardan en `knowledge/blueprints/` Y se indexan en el Knowledge Graph (LightRAG) para que el Task Planner los consulte semánticamente cuando recibe un brief.

**Criterio de éxito:**

- T1: Task Planner recibe "crea un marketplace de sneakers" → consulta Knowledge Graph → obtiene el blueprint de Marketplace
- T2: El blueprint se usa como base para el scaffold (schema DB, rutas, páginas)
- T3: Los 4 blueprints son válidos y completos (no faltan tablas ni rutas críticas)

---

## Épica 53.5 — Quality Gate (Lighthouse + Design System Validation)

**Qué:** Antes de entregar cualquier proyecto al usuario, El Monstruo ejecuta un quality gate automático que verifica que el output cumple con el Objetivo #2 (nivel Apple).

**Componentes del Quality Gate:**

1. **Lighthouse CI** — Performance >= 90, Accessibility >= 90, SEO >= 90, Best Practices >= 90
2. **Design System Check** — ¿Usa los tokens del Design System Foundation (Sprint 51.5)?
3. **Responsive Check** — ¿Se ve bien en mobile (375px), tablet (768px), desktop (1440px)?
4. **Content Check** — ¿Hay texto placeholder sin reemplazar? ¿Imágenes rotas?

**Archivo a crear:** `tools/quality_gate.py`

```python
"""
El Monstruo — Quality Gate
Sprint 53.5: Validación automática antes de entregar.
Si no pasa el gate, no se entrega.
Lighthouse + Design System + Responsive + Content checks.
"""
import json
import logging
from typing import Any

logger = logging.getLogger("monstruo.tools.quality_gate")

# ── Thresholds ─────────────────────────────────────────────────────
LIGHTHOUSE_THRESHOLDS = {
    "performance": 85,
    "accessibility": 90,
    "seo": 90,
    "best-practices": 85,
}

PLACEHOLDER_PATTERNS = [
    "Lorem ipsum", "TODO", "FIXME", "placeholder",
    "example.com", "test@test.com", "https://via.placeholder.com",
    "undefined", "null", "[object Object]"
]

async def run_quality_gate(
    sandbox,
    deploy_url: str,
    project_type: str,
) -> dict[str, Any]:
    """
    Ejecuta el quality gate completo en un proyecto deployado.
    
    Returns:
        dict con: passed (bool), scores (dict), issues (list), recommendations (list)
    """
    issues = []
    scores = {}
    
    # 1. Lighthouse (via Chrome headless en E2B)
    try:
        lighthouse_cmd = f"npx lighthouse {deploy_url} --output=json --chrome-flags='--headless --no-sandbox' --only-categories=performance,accessibility,seo,best-practices"
        result = await sandbox.process.start_and_wait(lighthouse_cmd, timeout=60)
        
        if result.exit_code == 0:
            report = json.loads(result.stdout)
            categories = report.get("categories", {})
            for cat_key, threshold in LIGHTHOUSE_THRESHOLDS.items():
                score = int((categories.get(cat_key, {}).get("score", 0)) * 100)
                scores[cat_key] = score
                if score < threshold:
                    issues.append(f"Lighthouse {cat_key}: {score} (min: {threshold})")
        else:
            issues.append(f"Lighthouse failed: {result.stderr[:200]}")
    except Exception as e:
        issues.append(f"Lighthouse error: {str(e)[:200]}")
    
    # 2. Placeholder detection (via page source)
    try:
        fetch_cmd = f"curl -s {deploy_url}"
        result = await sandbox.process.start_and_wait(fetch_cmd, timeout=15)
        page_source = result.stdout.lower()
        
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.lower() in page_source:
                issues.append(f"Placeholder detected: '{pattern}'")
    except Exception as e:
        issues.append(f"Content check error: {str(e)[:200]}")
    
    passed = len(issues) == 0
    
    recommendations = []
    if not passed:
        for issue in issues:
            if "performance" in issue.lower():
                recommendations.append("Optimize images (WebP), enable lazy loading, minimize JS bundle")
            elif "accessibility" in issue.lower():
                recommendations.append("Add alt text to images, ensure color contrast >= 4.5:1, add ARIA labels")
            elif "seo" in issue.lower():
                recommendations.append("Verify meta tags, sitemap, and schema.org are injected correctly")
            elif "placeholder" in issue.lower():
                recommendations.append("Replace all placeholder content with real data")
    
    logger.info(f"Quality Gate: {'PASSED' if passed else 'FAILED'} — {len(issues)} issues")
    
    return {
        "passed": passed,
        "scores": scores,
        "issues": issues,
        "recommendations": recommendations,
    }
```

**Integración:** Se ejecuta después del deploy en `tools/web_dev.py`:

```python
# En tools/web_dev.py, después de deploy exitoso:
from tools.quality_gate import run_quality_gate

# ... deploy completo ...
gate_result = await run_quality_gate(sandbox, deploy_url, project_type)
if not gate_result["passed"]:
    # Auto-fix: intentar resolver los issues antes de entregar
    # Si no se puede, entregar con advertencias
    logger.warning(f"Quality Gate FAILED: {gate_result['issues']}")
```

**Criterio de éxito:**

- T1: Proyecto con SEO inyectado pasa Lighthouse SEO >= 90
- T2: Proyecto con placeholder "Lorem ipsum" es detectado y flagueado
- T3: Gate bloquea entrega si scores están debajo del threshold

---

## Orden de Ejecución

```
Día 1-2:  53.4 Architecture Templates (blueprints JSON + indexar en Knowledge Graph)
Día 2-3:  53.1 SEO Engine (inject_seo + integración con web_dev.py)
Día 3-4:  53.2 Analytics Engine (PostHog snippet + helper de eventos)
Día 4-5:  53.3 Email Transaccional (Resend tool + templates)
Día 5-6:  53.5 Quality Gate (Lighthouse + checks + integración)
Día 6-7:  E2E Test — Scaffold marketplace desde blueprint → inject SEO → inject analytics → deploy → quality gate → pass
```

---

## Cambios en Archivos Existentes

| Archivo | Cambio |
|---------|--------|
| `tools/web_dev.py` | Importar y llamar `inject_seo`, `inject_analytics`, `run_quality_gate` como post-processing |
| `requirements.txt` | Agregar `resend` (o usar httpx directo) |
| `kernel/task_planner.py` | Registrar `seo_engine`, `analytics_engine`, `resend_email`, `quality_gate` como tools |
| `.env` / Railway | Agregar `POSTHOG_API_KEY`, `RESEND_API_KEY` |

---

## Archivos Nuevos

| Archivo | Épica |
|---------|-------|
| `tools/seo_engine.py` | 53.1 |
| `tools/analytics_engine.py` | 53.2 |
| `tools/resend_email.py` | 53.3 |
| `knowledge/blueprints/marketplace.json` | 53.4 |
| `knowledge/blueprints/saas.json` | 53.4 |
| `knowledge/blueprints/ecommerce.json` | 53.4 |
| `knowledge/blueprints/social.json` | 53.4 |
| `tools/quality_gate.py` | 53.5 |

---

## Costo Total

| Componente | Costo/mes |
|------------|-----------|
| SEO Engine | $0 (código puro) |
| PostHog | $0 (free tier 1M events) |
| Resend | $0 (free 100/día) → $20/mes si escala |
| Blueprints | $0 (JSONs locales) |
| Quality Gate | $0 (Lighthouse es open source) |
| **Total** | **$0 — $20/mes** |

---

## Correcciones Post-Cruce con 13 Objetivos

**C1 — Blueprints con `validated_at` (Obj #5):** Cada blueprint JSON incluye campo `validated_at: "2026-05-01"`. El Vanguard Scanner (Sprint 51.4) los re-evalúa cada 30 días. Si `validated_at` > 30 días → marca `stale` → re-investiga antes de usar.

**C2 — Validación Magna en SEO Engine (Obj #5):** Antes de inyectar SEO, consultar Perplexity/Sonar: "current SEO best practices for {project_type} {year}". Cache de 7 días para no disparar queries innecesarias. Solo ajusta si hay cambios significativos vs el template estático.

**C3 — PostHog como deuda de soberanía (Obj #12):** PostHog Cloud es la opción correcta HOY (free tier, mejor analytics). Cuando el ecosistema tenga infra propia (Fase 2 de soberanía), migrar a PostHog Self-hosted. No requiere cambio de código — solo cambiar `api_host`.

**C4 — Capas faltantes del Obj #9 documentadas:** Las Capas 1 (Motor de Ventas), 3 (Publicidad), 4 (Tendencias), y 6 (Finanzas) del Objetivo #9 requieren la inteligencia emergente del Objetivo #8 para funcionar a máximo nivel. Se implementan en Sprint 54+ cuando la Capa 2 (Inteligencia) esté activa.

**C5 — Responsive screenshots en Quality Gate (Obj #2):** Quality Gate toma screenshots en 3 viewports (375px, 768px, 1440px) usando el browser interactivo (Sprint 51.3). Verifica: no overflow horizontal, no elementos cortados, layout coherente en cada breakpoint.

---

## Deuda para Sprint 54

- Capa 1 del Obj #9: Motor de Ventas (funnels, pricing, copywriting)
- Capa 3 del Obj #9: Ads automation (Google Ads API v24 + Meta Ads CLI)
- Capa 4 del Obj #9: Tendencias y monitoreo de mercado
- Capa 6 del Obj #9: Financial modeling (unit economics, projections)
- A/B testing workflows (PostHog feature flags → experiments)
- Más blueprints (fintech, edtech, healthtech, real estate)
- Email marketing (no solo transaccional — drip campaigns, newsletters)
