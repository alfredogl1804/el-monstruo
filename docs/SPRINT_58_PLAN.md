# Sprint 58 — "La Fortaleza Completa"

**Fecha:** 1 mayo 2026
**Autor:** Manus AI (bajo dirección de Alfredo Gongora)
**Tipo:** Sprint de Capas Transversales Finales + Embriones Especializados
**Objetivo Primario:** Obj #9 (Transversalidad Universal — completar 6/6 capas)
**Objetivos Secundarios:** Obj #11 (Multiplicación de Embriones), Obj #4 (Nunca Se Equivoca Dos Veces)

---

## Contexto Estratégico

Sprint 57 inició la Transversalidad Universal con las capas 1 (Sales Engine), 2 (SEO Architecture), y 6 (Financial Dashboard). Sprint 58 completa las tres capas restantes: **Seguridad** (Capa 3), **Escalabilidad** (Capa 4), y **Analítica Avanzada** (Capa 5). Con las 6 capas completas, todo negocio que El Monstruo cree nace como una fortaleza: seguro, escalable, medible, vendible, encontrable, y financieramente visible.

Adicionalmente, Sprint 58 crea dos embriones especializados más: **Embrión-Técnico** (arquitectura y DevOps) y **Embrión-Vigía** (seguridad y monitoreo), llevando el total a 3 de 7 embriones del Obj #11.

**Hallazgo crítico durante investigación:** El Monstruo YA tiene seguridad interna robusta (rate_limiter.py Sprint 3, input_guard.py Sprint 28, SovereignAlertMonitor). La diferencia clave de Sprint 58 es que estas capacidades se convierten en **templates inyectables** que se aplican a los proyectos que El Monstruo crea, no solo a El Monstruo mismo.

---

## Stack Validado en Tiempo Real (1 mayo 2026)

| Herramienta | Versión | Fecha Release | Licencia | Rol en Sprint 58 |
|---|---|---|---|---|
| upstash-redis [1] | 1.7.0 | Mar 18, 2026 | MIT | Caching serverless para Scalability Layer |
| sentry-sdk [2] | ~2.56.0 | Apr 2026 | MIT | Error monitoring para Embrión-Vigía |
| Starlette SecurityMiddleware | Built-in | — | MIT | Security headers (HSTS, X-Frame, CSP) |
| PostHog (ya instalado) [3] | 7.13.2 | Apr 30, 2026 | MIT | Analytics Layer (user behavior, heatmaps) |

**Componentes existentes reutilizados:**

| Componente | Archivo | Sprint | Rol en Sprint 58 |
|---|---|---|---|
| Rate Limiter | `kernel/rate_limiter.py` | Sprint 3 | Template base para Security Layer |
| Input Guard | `kernel/security/input_guard.py` | Sprint 28 | Template base para Security Layer |
| SovereignAlertMonitor | `kernel/alerts/sovereign_alerts.py` | Sprint ? | Base para Embrión-Vigía |
| EmbrionLoop | `kernel/embrion_loop.py` | Sprint 33C | Clase padre de nuevos embriones |
| EmbrionVentas | `kernel/embrion_ventas.py` | Sprint 57 | Patrón para nuevos embriones |

---

## Épica 58.1 — Security Layer (Capa Transversal #3)

### Objetivo

Construir la capa de seguridad transversal que se inyecta automáticamente en todo proyecto. A diferencia de la seguridad interna de El Monstruo (que protege al kernel), esta capa genera configuraciones de seguridad para los proyectos que El Monstruo crea para sus usuarios.

### Justificación

> "Seguridad: OAuth/JWT templates, rate limiting patterns, CORS configuration, security headers, input sanitization." — Obj #9, Capa 3

### Diseño

```
transversal/
  security_layer.py          ← Capa de seguridad principal
  auth_templates.py          ← Templates de autenticación (JWT, OAuth, API keys)
  headers_config.py          ← Configuración de security headers
  cors_config.py             ← Configuración CORS inteligente
  input_sanitizer.py         ← Sanitización de input para proyectos
```

### Implementación

**Archivo: `transversal/security_layer.py`**

```python
"""
security_layer.py — Capa de Seguridad Transversal
===================================================
Capa Transversal #3 del Objetivo #9.
Genera configuraciones de seguridad para proyectos creados por El Monstruo.

IMPORTANTE: Esta capa NO protege a El Monstruo (eso lo hacen rate_limiter.py
y input_guard.py). Esta capa genera TEMPLATES de seguridad que se inyectan
en los proyectos que El Monstruo crea para usuarios.

Componentes:
  1. Auth templates (JWT, OAuth2, API keys)
  2. Security headers (HSTS, CSP, X-Frame-Options)
  3. CORS configuration inteligente
  4. Rate limiting patterns
  5. Input sanitization templates

Sprint 58 — "La Fortaleza Completa"
"""
import logging
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

logger = logging.getLogger("security_layer")


class AuthStrategy(Enum):
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    SESSION = "session"
    NONE = "none"


class ProjectType(Enum):
    PUBLIC_API = "public_api"
    PRIVATE_API = "private_api"
    WEB_APP = "web_app"
    MOBILE_BACKEND = "mobile_backend"
    INTERNAL_TOOL = "internal_tool"


@dataclass
class SecurityConfig:
    """Configuración de seguridad generada para un proyecto."""
    project_id: str
    project_type: ProjectType
    auth_strategy: AuthStrategy
    cors_origins: list[str] = field(default_factory=list)
    rate_limit_rpm: int = 60
    rate_limit_rph: int = 500
    enable_csrf: bool = True
    enable_hsts: bool = True
    csp_policy: str = "default-src 'self'"
    allowed_methods: list[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    input_max_length: int = 10000
    file_upload_max_mb: int = 10
    require_https: bool = True


class SecurityLayer:
    """Capa de seguridad transversal — genera configs para proyectos."""

    # Security header presets by project type
    HEADER_PRESETS = {
        ProjectType.PUBLIC_API: {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "0",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
        },
        ProjectType.WEB_APP: {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "X-XSS-Protection": "0",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;",
        },
        ProjectType.INTERNAL_TOOL: {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "Strict-Transport-Security": "max-age=31536000",
        },
    }

    # Auth strategy recommendations by project type
    AUTH_RECOMMENDATIONS = {
        ProjectType.PUBLIC_API: AuthStrategy.API_KEY,
        ProjectType.PRIVATE_API: AuthStrategy.JWT,
        ProjectType.WEB_APP: AuthStrategy.SESSION,
        ProjectType.MOBILE_BACKEND: AuthStrategy.JWT,
        ProjectType.INTERNAL_TOOL: AuthStrategy.OAUTH2,
    }

    def __init__(self):
        logger.info("SecurityLayer initialized")

    async def generate_security_config(self, project_id: str, project_type: ProjectType,
                                        custom_origins: list[str] = None) -> SecurityConfig:
        """Generar configuración de seguridad completa para un proyecto."""
        auth = self.AUTH_RECOMMENDATIONS.get(project_type, AuthStrategy.JWT)
        
        # CORS origins based on project type
        if custom_origins:
            origins = custom_origins
        elif project_type == ProjectType.PUBLIC_API:
            origins = ["*"]  # Public APIs allow all origins
        elif project_type == ProjectType.INTERNAL_TOOL:
            origins = ["https://internal.company.com"]
        else:
            origins = ["https://yourdomain.com"]
        
        # Rate limits based on project type
        rpm = 120 if project_type == ProjectType.PUBLIC_API else 60
        rph = 1000 if project_type == ProjectType.PUBLIC_API else 500
        
        config = SecurityConfig(
            project_id=project_id,
            project_type=project_type,
            auth_strategy=auth,
            cors_origins=origins,
            rate_limit_rpm=rpm,
            rate_limit_rph=rph,
            enable_csrf=project_type in (ProjectType.WEB_APP, ProjectType.INTERNAL_TOOL),
            enable_hsts=True,
            require_https=True,
        )
        
        return config

    def generate_middleware_code(self, config: SecurityConfig) -> str:
        """Generar código de middleware de seguridad para FastAPI."""
        headers = self.HEADER_PRESETS.get(config.project_type, self.HEADER_PRESETS[ProjectType.WEB_APP])
        
        code = f'''"""
Security Middleware — Auto-generated by El Monstruo Security Layer
Project: {config.project_id}
Auth Strategy: {config.auth_strategy.value}
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins={config.cors_origins},
    allow_credentials=True,
    allow_methods={config.allowed_methods},
    allow_headers=["*"],
)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
'''
        for header, value in headers.items():
            code += f'        response.headers["{header}"] = "{value}"\n'
        
        code += '''        return response

app.add_middleware(SecurityHeadersMiddleware)
'''
        return code

    def generate_auth_template(self, strategy: AuthStrategy) -> dict:
        """Generar template de autenticación según estrategia."""
        templates = {
            AuthStrategy.JWT: {
                "dependencies": ["python-jose[cryptography]", "passlib[bcrypt]"],
                "env_vars": ["JWT_SECRET_KEY", "JWT_ALGORITHM=HS256", "JWT_EXPIRE_MINUTES=30"],
                "description": "JWT Bearer token authentication",
                "files": ["auth/jwt_handler.py", "auth/dependencies.py", "auth/models.py"],
            },
            AuthStrategy.OAUTH2: {
                "dependencies": ["authlib", "httpx"],
                "env_vars": ["OAUTH_CLIENT_ID", "OAUTH_CLIENT_SECRET", "OAUTH_REDIRECT_URI"],
                "description": "OAuth2 with external provider (Google, GitHub, etc.)",
                "files": ["auth/oauth_handler.py", "auth/providers.py", "auth/callbacks.py"],
            },
            AuthStrategy.API_KEY: {
                "dependencies": [],
                "env_vars": ["API_KEY_HEADER=X-API-Key"],
                "description": "Simple API key authentication via header",
                "files": ["auth/api_key_handler.py", "auth/key_store.py"],
            },
            AuthStrategy.SESSION: {
                "dependencies": ["itsdangerous"],
                "env_vars": ["SESSION_SECRET_KEY", "SESSION_MAX_AGE=3600"],
                "description": "Session-based authentication with secure cookies",
                "files": ["auth/session_handler.py", "auth/session_store.py"],
            },
        }
        return templates.get(strategy, templates[AuthStrategy.JWT])

    def generate_owasp_checklist(self, project_type: ProjectType) -> list[dict]:
        """Generar checklist OWASP Top 10 para el proyecto."""
        return [
            {"id": "A01", "name": "Broken Access Control", "check": "Verify role-based access on all endpoints", "status": "pending"},
            {"id": "A02", "name": "Cryptographic Failures", "check": "Ensure all sensitive data encrypted at rest and in transit", "status": "pending"},
            {"id": "A03", "name": "Injection", "check": "Parameterized queries, input validation on all inputs", "status": "pending"},
            {"id": "A04", "name": "Insecure Design", "check": "Threat modeling completed, security requirements defined", "status": "pending"},
            {"id": "A05", "name": "Security Misconfiguration", "check": "Default credentials removed, error handling configured", "status": "pending"},
            {"id": "A06", "name": "Vulnerable Components", "check": "All dependencies scanned, no known CVEs", "status": "pending"},
            {"id": "A07", "name": "Auth Failures", "check": "MFA available, brute force protection, secure password policy", "status": "pending"},
            {"id": "A08", "name": "Data Integrity Failures", "check": "CI/CD pipeline secured, dependency verification", "status": "pending"},
            {"id": "A09", "name": "Logging Failures", "check": "Security events logged, alerting configured", "status": "pending"},
            {"id": "A10", "name": "SSRF", "check": "URL validation, allowlists for external requests", "status": "pending"},
        ]
```

### Criterios de Aceptación

1. `SecurityConfig` generada automáticamente por tipo de proyecto
2. Security headers preset por tipo (API, Web App, Internal Tool)
3. Auth strategy recomendada automáticamente con template de código
4. Middleware code generado listo para copiar/pegar en proyecto
5. OWASP Top 10 checklist generada por proyecto
6. CORS configuration inteligente por tipo
7. Tests unitarios para cada generador

---

## Épica 58.2 — Scalability Layer (Capa Transversal #4)

### Objetivo

Construir la capa de escalabilidad transversal que inyecta patrones de caching, CDN configuration, load balancing, y database optimization en todo proyecto.

### Justificación

> "Escalabilidad: Caching strategies, CDN configuration, load balancing patterns, database optimization, horizontal scaling patterns." — Obj #9, Capa 4

### Diseño

```
transversal/
  scalability_layer.py       ← Capa de escalabilidad principal
  caching_strategy.py        ← Estrategias de caching (Redis, in-memory, CDN)
  cdn_config.py              ← Configuración de CDN
  db_optimizer.py            ← Patrones de optimización de DB
  scaling_patterns.py        ← Patrones de escalamiento horizontal
```

### Implementación

**Archivo: `transversal/scalability_layer.py`**

```python
"""
scalability_layer.py — Capa de Escalabilidad Transversal
=========================================================
Capa Transversal #4 del Objetivo #9.
Patrones de escalabilidad inyectados en cada proyecto.

Componentes:
  1. Caching strategies (Redis/Upstash, in-memory, CDN edge)
  2. CDN configuration templates
  3. Database optimization patterns
  4. Horizontal scaling patterns
  5. Performance budgets

Sprint 58 — "La Fortaleza Completa"
"""
import logging
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

logger = logging.getLogger("scalability_layer")


class CacheStrategy(Enum):
    NONE = "none"
    IN_MEMORY = "in_memory"
    REDIS = "redis"
    CDN_EDGE = "cdn_edge"
    HYBRID = "hybrid"  # Redis + CDN


class ScalingPattern(Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    SERVERLESS = "serverless"
    HYBRID = "hybrid"


class DatabasePattern(Enum):
    SINGLE = "single"
    READ_REPLICAS = "read_replicas"
    SHARDING = "sharding"
    CQRS = "cqrs"


@dataclass
class PerformanceBudget:
    """Performance budget para un proyecto."""
    ttfb_ms: int = 200          # Time to First Byte
    fcp_ms: int = 1000          # First Contentful Paint
    lcp_ms: int = 2500          # Largest Contentful Paint
    cls: float = 0.1            # Cumulative Layout Shift
    fid_ms: int = 100           # First Input Delay
    bundle_size_kb: int = 200   # JS bundle size
    api_response_ms: int = 500  # API response time p95


@dataclass
class ScalabilityConfig:
    """Configuración de escalabilidad para un proyecto."""
    project_id: str
    expected_users: int
    cache_strategy: CacheStrategy
    scaling_pattern: ScalingPattern
    db_pattern: DatabasePattern
    performance_budget: PerformanceBudget = field(default_factory=PerformanceBudget)
    cdn_enabled: bool = True
    redis_url: Optional[str] = None


class ScalabilityLayer:
    """Capa de escalabilidad transversal."""

    # Thresholds for automatic scaling recommendations
    USER_THRESHOLDS = {
        100: {"cache": CacheStrategy.IN_MEMORY, "scaling": ScalingPattern.VERTICAL, "db": DatabasePattern.SINGLE},
        1000: {"cache": CacheStrategy.REDIS, "scaling": ScalingPattern.VERTICAL, "db": DatabasePattern.SINGLE},
        10000: {"cache": CacheStrategy.HYBRID, "scaling": ScalingPattern.HORIZONTAL, "db": DatabasePattern.READ_REPLICAS},
        100000: {"cache": CacheStrategy.HYBRID, "scaling": ScalingPattern.HORIZONTAL, "db": DatabasePattern.CQRS},
        1000000: {"cache": CacheStrategy.HYBRID, "scaling": ScalingPattern.SERVERLESS, "db": DatabasePattern.SHARDING},
    }

    def __init__(self, redis_client=None):
        self._redis = redis_client
        logger.info("ScalabilityLayer initialized")

    async def generate_config(self, project_id: str, expected_users: int) -> ScalabilityConfig:
        """Generar configuración de escalabilidad basada en usuarios esperados."""
        # Find appropriate threshold
        recommendation = {"cache": CacheStrategy.IN_MEMORY, "scaling": ScalingPattern.VERTICAL, "db": DatabasePattern.SINGLE}
        for threshold, config in sorted(self.USER_THRESHOLDS.items()):
            if expected_users >= threshold:
                recommendation = config
        
        return ScalabilityConfig(
            project_id=project_id,
            expected_users=expected_users,
            cache_strategy=recommendation["cache"],
            scaling_pattern=recommendation["scaling"],
            db_pattern=recommendation["db"],
            cdn_enabled=expected_users >= 1000,
        )

    def generate_caching_code(self, strategy: CacheStrategy) -> str:
        """Generar código de caching según estrategia."""
        if strategy == CacheStrategy.REDIS:
            return '''"""
Caching Layer — Redis (Upstash) — Auto-generated by El Monstruo
"""
import os
from functools import wraps
from upstash_redis import Redis

redis = Redis(
    url=os.environ["UPSTASH_REDIS_REST_URL"],
    token=os.environ["UPSTASH_REDIS_REST_TOKEN"],
)

def cache(ttl_seconds: int = 300):
    """Decorator for caching function results in Redis."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try cache first
            cached = redis.get(key)
            if cached is not None:
                return cached
            
            # Execute and cache
            result = await func(*args, **kwargs)
            redis.set(key, result, ex=ttl_seconds)
            return result
        return wrapper
    return decorator
'''
        elif strategy == CacheStrategy.IN_MEMORY:
            return '''"""
Caching Layer — In-Memory (LRU) — Auto-generated by El Monstruo
"""
from functools import lru_cache
from datetime import datetime, timedelta

# Simple TTL cache for small-scale applications
_cache = {}
_cache_ttl = {}

def cache_get(key: str):
    """Get value from cache if not expired."""
    if key in _cache and datetime.now() < _cache_ttl.get(key, datetime.min):
        return _cache[key]
    return None

def cache_set(key: str, value, ttl_seconds: int = 300):
    """Set value in cache with TTL."""
    _cache[key] = value
    _cache_ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
'''
        return "# No caching configured"

    def generate_cdn_config(self, provider: str = "cloudflare") -> dict:
        """Generar configuración de CDN."""
        configs = {
            "cloudflare": {
                "provider": "Cloudflare",
                "cache_rules": [
                    {"match": "/static/*", "ttl": 86400, "cache_level": "aggressive"},
                    {"match": "/api/*", "ttl": 0, "cache_level": "bypass"},
                    {"match": "/*.html", "ttl": 3600, "cache_level": "standard"},
                    {"match": "/images/*", "ttl": 604800, "cache_level": "aggressive"},
                ],
                "page_rules": [
                    {"url": "*/api/*", "settings": {"cache_level": "bypass"}},
                    {"url": "*/static/*", "settings": {"cache_level": "cache_everything", "edge_cache_ttl": 86400}},
                ],
                "security": {
                    "ssl": "full_strict",
                    "min_tls_version": "1.2",
                    "always_use_https": True,
                },
            },
            "vercel": {
                "provider": "Vercel Edge Network",
                "headers": [
                    {"source": "/static/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=86400, immutable"}]},
                    {"source": "/api/(.*)", "headers": [{"key": "Cache-Control", "value": "no-store"}]},
                ],
            },
        }
        return configs.get(provider, configs["cloudflare"])

    def generate_db_optimization(self, pattern: DatabasePattern) -> dict:
        """Generar recomendaciones de optimización de DB."""
        optimizations = {
            DatabasePattern.SINGLE: {
                "indexes": "Add indexes on frequently queried columns",
                "connection_pool": "Use connection pooling (min=5, max=20)",
                "queries": "Avoid N+1 queries, use JOINs or batch fetching",
                "monitoring": "Track slow queries (>100ms)",
            },
            DatabasePattern.READ_REPLICAS: {
                "architecture": "Primary for writes, replicas for reads",
                "routing": "Route read queries to replicas automatically",
                "lag_monitoring": "Monitor replication lag (<1s acceptable)",
                "failover": "Automatic failover if primary goes down",
            },
            DatabasePattern.CQRS: {
                "architecture": "Separate read and write models",
                "event_sourcing": "Consider event sourcing for audit trail",
                "eventual_consistency": "Accept eventual consistency for reads",
                "projections": "Build optimized read projections",
            },
            DatabasePattern.SHARDING: {
                "strategy": "Hash-based sharding on user_id or tenant_id",
                "routing": "Shard-aware query routing layer",
                "rebalancing": "Plan for shard rebalancing as data grows",
                "cross_shard": "Minimize cross-shard queries",
            },
        }
        return optimizations.get(pattern, optimizations[DatabasePattern.SINGLE])
```

### Criterios de Aceptación

1. Configuración automática basada en usuarios esperados (100 → 1M+)
2. Código de caching generado para Redis (Upstash) e in-memory
3. CDN configuration templates (Cloudflare, Vercel)
4. DB optimization patterns por nivel de escala
5. Performance budget definido con métricas Web Vitals
6. Tests unitarios para cada generador

---

## Épica 58.3 — Analytics Layer (Capa Transversal #5)

### Objetivo

Construir la capa de analítica avanzada que inyecta dashboards de user behavior, event tracking, y métricas de engagement en todo proyecto. Complementa el ConversionTracker de Sprint 57 con analytics de producto más profundos.

### Justificación

> "Analítica avanzada: User behavior tracking, heatmaps, session recording, custom dashboards, retention analysis." — Obj #9, Capa 5

### Diseño

```
transversal/
  analytics_layer.py         ← Capa de analítica principal
  event_taxonomy.py          ← Taxonomía estándar de eventos
  retention_analyzer.py      ← Análisis de retención
  engagement_scorer.py       ← Score de engagement por usuario
```

### Implementación

**Archivo: `transversal/analytics_layer.py`**

```python
"""
analytics_layer.py — Capa de Analítica Avanzada Transversal
=============================================================
Capa Transversal #5 del Objetivo #9.
Analytics de producto inyectados en cada proyecto.

Complementa ConversionTracker (Sprint 57) con:
  1. Event taxonomy estándar
  2. User behavior tracking
  3. Retention analysis (Day 1, 7, 30)
  4. Engagement scoring
  5. Cohort analysis templates

Sprint 58 — "La Fortaleza Completa"
"""
import logging
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger("analytics_layer")


class EventCategory(Enum):
    NAVIGATION = "navigation"
    INTERACTION = "interaction"
    TRANSACTION = "transaction"
    SYSTEM = "system"
    CUSTOM = "custom"


@dataclass
class EventDefinition:
    """Definición de un evento trackeable."""
    name: str
    category: EventCategory
    description: str
    properties: list[str] = field(default_factory=list)
    is_conversion: bool = False
    is_engagement: bool = False


@dataclass
class RetentionMetrics:
    """Métricas de retención."""
    day_1: float = 0.0   # % users returning day 1
    day_7: float = 0.0   # % users returning day 7
    day_30: float = 0.0  # % users returning day 30
    day_90: float = 0.0  # % users returning day 90
    
    @property
    def health(self) -> str:
        if self.day_30 >= 0.20:
            return "excellent"
        elif self.day_30 >= 0.10:
            return "good"
        elif self.day_30 >= 0.05:
            return "concerning"
        else:
            return "critical"


class AnalyticsLayer:
    """Capa de analítica avanzada transversal."""

    # Standard event taxonomy that every project should track
    STANDARD_EVENTS = [
        EventDefinition("page_view", EventCategory.NAVIGATION, "User viewed a page", ["page_path", "referrer"]),
        EventDefinition("session_start", EventCategory.SYSTEM, "New session started", ["source", "medium", "campaign"]),
        EventDefinition("session_end", EventCategory.SYSTEM, "Session ended", ["duration_seconds", "pages_viewed"]),
        EventDefinition("button_click", EventCategory.INTERACTION, "User clicked a button", ["button_id", "button_text", "page"]),
        EventDefinition("form_submit", EventCategory.INTERACTION, "User submitted a form", ["form_id", "success"]),
        EventDefinition("search", EventCategory.INTERACTION, "User performed a search", ["query", "results_count"]),
        EventDefinition("signup", EventCategory.TRANSACTION, "User signed up", ["method", "plan"], is_conversion=True),
        EventDefinition("login", EventCategory.TRANSACTION, "User logged in", ["method"]),
        EventDefinition("purchase", EventCategory.TRANSACTION, "User made a purchase", ["amount", "currency", "product"], is_conversion=True),
        EventDefinition("feature_used", EventCategory.INTERACTION, "User used a feature", ["feature_name", "duration"], is_engagement=True),
        EventDefinition("error_encountered", EventCategory.SYSTEM, "User encountered an error", ["error_type", "page", "message"]),
        EventDefinition("feedback_given", EventCategory.INTERACTION, "User gave feedback", ["rating", "comment", "context"]),
    ]

    def __init__(self, posthog_client=None):
        self._posthog = posthog_client
        logger.info("AnalyticsLayer initialized")

    async def setup_for_project(self, project_id: str, custom_events: list[dict] = None) -> dict:
        """Configurar analytics para un nuevo proyecto."""
        events = list(self.STANDARD_EVENTS)
        
        # Add custom events
        if custom_events:
            for evt in custom_events:
                events.append(EventDefinition(
                    name=evt["name"],
                    category=EventCategory(evt.get("category", "custom")),
                    description=evt.get("description", ""),
                    properties=evt.get("properties", []),
                    is_conversion=evt.get("is_conversion", False),
                    is_engagement=evt.get("is_engagement", False),
                ))
        
        return {
            "project_id": project_id,
            "total_events": len(events),
            "conversion_events": sum(1 for e in events if e.is_conversion),
            "engagement_events": sum(1 for e in events if e.is_engagement),
            "event_taxonomy": [{"name": e.name, "category": e.category.value, "properties": e.properties} for e in events],
            "status": "configured",
        }

    def generate_tracking_code(self, project_id: str, framework: str = "react") -> str:
        """Generar código de tracking para el frontend."""
        if framework == "react":
            return f'''/**
 * Analytics Tracking — Auto-generated by El Monstruo
 * Project: {project_id}
 * Framework: React
 */
import posthog from 'posthog-js';

// Initialize PostHog
posthog.init(process.env.REACT_APP_POSTHOG_KEY, {{
  api_host: process.env.REACT_APP_POSTHOG_HOST || 'https://app.posthog.com',
  autocapture: true,
  capture_pageview: true,
  capture_pageleave: true,
}});

// Standard tracking functions
export const trackEvent = (name, properties = {{}}) => {{
  posthog.capture(name, properties);
}};

export const trackPageView = (pagePath) => {{
  posthog.capture('page_view', {{ page_path: pagePath }});
}};

export const trackButtonClick = (buttonId, buttonText, page) => {{
  posthog.capture('button_click', {{ button_id: buttonId, button_text: buttonText, page }});
}};

export const trackPurchase = (amount, currency, product) => {{
  posthog.capture('purchase', {{ amount, currency, product }});
}};

export const identifyUser = (userId, properties = {{}}) => {{
  posthog.identify(userId, properties);
}};

export const trackFeatureUsed = (featureName, duration) => {{
  posthog.capture('feature_used', {{ feature_name: featureName, duration }});
}};
'''
        return "// Framework not supported"

    def calculate_engagement_score(self, user_events: list[dict]) -> dict:
        """Calcular score de engagement para un usuario."""
        if not user_events:
            return {"score": 0, "level": "inactive", "factors": {}}
        
        # Scoring factors
        session_count = len(set(e.get("session_id") for e in user_events if e.get("session_id")))
        feature_uses = sum(1 for e in user_events if e.get("event") == "feature_used")
        interactions = sum(1 for e in user_events if e.get("category") == "interaction")
        
        # Weighted score (0-100)
        score = min(100, (
            session_count * 10 +
            feature_uses * 5 +
            interactions * 2
        ))
        
        # Level classification
        if score >= 80:
            level = "power_user"
        elif score >= 50:
            level = "engaged"
        elif score >= 20:
            level = "casual"
        else:
            level = "at_risk"
        
        return {
            "score": score,
            "level": level,
            "factors": {
                "sessions": session_count,
                "feature_uses": feature_uses,
                "interactions": interactions,
            },
        }

    def generate_retention_query(self, cohort_period: str = "week") -> str:
        """Generar query SQL para análisis de retención."""
        return f'''-- Retention Analysis Query — Auto-generated by El Monstruo
-- Cohort period: {cohort_period}
WITH cohorts AS (
    SELECT 
        user_id,
        DATE_TRUNC('{cohort_period}', MIN(created_at)) AS cohort_{cohort_period}
    FROM events
    WHERE event_name = 'session_start'
    GROUP BY user_id
),
activity AS (
    SELECT 
        user_id,
        DATE_TRUNC('{cohort_period}', created_at) AS activity_{cohort_period}
    FROM events
    WHERE event_name = 'session_start'
    GROUP BY user_id, DATE_TRUNC('{cohort_period}', created_at)
)
SELECT 
    c.cohort_{cohort_period},
    COUNT(DISTINCT c.user_id) AS cohort_size,
    COUNT(DISTINCT CASE WHEN a.activity_{cohort_period} = c.cohort_{cohort_period} + INTERVAL '1 {cohort_period}' THEN a.user_id END) AS retained_1,
    COUNT(DISTINCT CASE WHEN a.activity_{cohort_period} = c.cohort_{cohort_period} + INTERVAL '4 {cohort_period}' THEN a.user_id END) AS retained_4
FROM cohorts c
LEFT JOIN activity a ON c.user_id = a.user_id
GROUP BY c.cohort_{cohort_period}
ORDER BY c.cohort_{cohort_period};
'''
```

### Criterios de Aceptación

1. Taxonomía estándar de 12 eventos que todo proyecto debe trackear
2. Código de tracking generado para React (PostHog JS SDK)
3. Engagement scoring por usuario (power_user, engaged, casual, at_risk)
4. Retention query SQL generada para análisis de cohortes
5. RetentionMetrics con health grade (excellent/good/concerning/critical)
6. Tests unitarios para scoring y setup

---

## Épica 58.4 — Embrión-Técnico

### Objetivo

Crear el segundo Embrión especializado: experto en arquitectura de software, DevOps, code review, y optimización de performance. Opera autónomamente evaluando la calidad técnica de todo proyecto.

### Diseño

```
kernel/
  embrion_tecnico.py         ← Embrión-Técnico
  embrion_specializations/
    tecnico_knowledge.py     ← Knowledge base técnica
    tecnico_prompts.py       ← System prompts especializados
```

### Implementación

**Archivo: `kernel/embrion_tecnico.py`**

```python
"""
embrion_tecnico.py — Embrión-Técnico: Especialista en Arquitectura y DevOps
=============================================================================
Segundo Embrión especializado (Obj #11).
Expertise: arquitectura de software, code review, DevOps, performance.

Tareas autónomas:
  - Auditoría de arquitectura de proyectos activos
  - Code review automatizado
  - Dependency vulnerability scanning
  - Performance profiling recommendations
  - Infrastructure cost optimization

Sprint 58 — "La Fortaleza Completa"
"""
import logging
from typing import Optional
from kernel.embrion_loop import EmbrionLoop

logger = logging.getLogger("embrion_tecnico")


class EmbrionTecnico(EmbrionLoop):
    """Embrión especializado en arquitectura y DevOps."""

    EMBRION_ID = "embrion-tecnico"
    SPECIALIZATION = "tecnico"
    
    SYSTEM_PROMPT = """Eres Embrión-Técnico, el especialista en arquitectura de software 
    y DevOps del sistema El Monstruo. Tu expertise incluye:
    
    1. ARQUITECTURA: Microservicios, monolitos modulares, event-driven, CQRS
    2. CODE QUALITY: SOLID, DRY, KISS, clean code, design patterns
    3. DEVOPS: CI/CD, Docker, Kubernetes, infrastructure as code
    4. PERFORMANCE: Profiling, optimization, caching, database tuning
    5. SECURITY: OWASP Top 10, dependency scanning, secret management
    6. SCALABILITY: Horizontal scaling, load balancing, auto-scaling
    
    Cuando El Monstruo crea un proyecto, tú evalúas la calidad técnica
    y propones mejoras antes de entregar. Eres el guardián de la excelencia técnica.
    
    Principios:
    - Simplicidad sobre complejidad. El mejor código es el que no existe.
    - Pragmatismo sobre purismo. Ship fast, refactor later.
    - Observabilidad. Si no puedes medirlo, no puedes mejorarlo.
    - Seguridad por defecto. Nunca opt-in, siempre opt-out.
    """

    DEFAULT_TASKS = {
        "architecture_audit": {
            "description": "Auditar arquitectura de proyectos activos",
            "interval_hours": 24,
            "max_cost_usd": 0.25,
            "priority": 2,
        },
        "dependency_scan": {
            "description": "Escanear vulnerabilidades en dependencias",
            "interval_hours": 12,
            "max_cost_usd": 0.10,
            "priority": 1,
        },
        "performance_check": {
            "description": "Verificar métricas de performance",
            "interval_hours": 6,
            "max_cost_usd": 0.10,
            "priority": 1,
        },
        "code_quality_review": {
            "description": "Review de calidad de código en últimos commits",
            "interval_hours": 8,
            "max_cost_usd": 0.20,
            "priority": 2,
        },
        "infra_cost_audit": {
            "description": "Auditar costos de infraestructura",
            "interval_hours": 48,
            "max_cost_usd": 0.15,
            "priority": 3,
        },
    }

    def __init__(self, db=None, sabios=None, search_fn=None):
        super().__init__(db=db, sabios=sabios)
        self._search = search_fn

    async def audit_architecture(self, project_structure: dict) -> dict:
        """Auditar arquitectura de un proyecto."""
        issues = []
        recommendations = []
        score = 100  # Start at 100, deduct for issues
        
        # Check for common anti-patterns
        files = project_structure.get("files", [])
        
        # Check file count (too many = potential over-engineering)
        if len(files) > 200:
            issues.append("High file count (>200) — consider consolidation")
            score -= 5
        
        # Check for test files
        test_files = [f for f in files if "test" in f.lower() or "spec" in f.lower()]
        if len(test_files) == 0:
            issues.append("No test files found — testing is mandatory")
            score -= 20
        elif len(test_files) / max(len(files), 1) < 0.1:
            issues.append("Low test coverage ratio (<10%)")
            score -= 10
        
        # Check for env file in repo
        if ".env" in files:
            issues.append("CRITICAL: .env file in repository — secrets exposed")
            score -= 30
        
        # Check for Dockerfile
        if "Dockerfile" not in files and "docker-compose.yml" not in files:
            recommendations.append("Add Dockerfile for consistent deployments")
        
        # Check for CI/CD
        ci_files = [f for f in files if ".github/workflows" in f or "Jenkinsfile" in f or ".gitlab-ci" in f]
        if not ci_files:
            recommendations.append("Add CI/CD pipeline for automated testing")
            score -= 5
        
        # Grade
        if score >= 90:
            grade = "excellent"
        elif score >= 70:
            grade = "good"
        elif score >= 50:
            grade = "needs_improvement"
        else:
            grade = "critical"
        
        return {
            "score": max(0, score),
            "grade": grade,
            "issues": issues,
            "recommendations": recommendations,
            "files_analyzed": len(files),
            "test_coverage_ratio": len(test_files) / max(len(files), 1),
        }

    async def review_code_quality(self, code: str, language: str = "python") -> dict:
        """Review de calidad de código."""
        issues = []
        
        lines = code.split("\n")
        
        # Check line length
        long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 120]
        if long_lines:
            issues.append(f"Lines exceeding 120 chars: {long_lines[:5]}")
        
        # Check for TODO/FIXME/HACK
        todos = [i for i, line in enumerate(lines, 1) if any(t in line.upper() for t in ["TODO", "FIXME", "HACK"])]
        if todos:
            issues.append(f"Unresolved TODOs/FIXMEs at lines: {todos[:5]}")
        
        # Check for hardcoded secrets patterns
        import re
        secret_patterns = [
            r'(api_key|apikey|secret|password|token)\s*=\s*["\'][^"\']+["\']',
            r'sk_live_[a-zA-Z0-9]+',
            r'AKIA[A-Z0-9]{16}',
        ]
        for pattern in secret_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                issues.append(f"CRITICAL: Potential hardcoded secret detected")
                break
        
        # Check function length
        # (simplified check for Python)
        if language == "python":
            func_starts = [i for i, line in enumerate(lines) if line.strip().startswith("def ") or line.strip().startswith("async def ")]
            for start in func_starts:
                # Find next function or end
                end = len(lines)
                for next_start in func_starts:
                    if next_start > start:
                        end = next_start
                        break
                if end - start > 50:
                    issues.append(f"Function at line {start+1} is too long ({end-start} lines)")
        
        quality_score = max(0, 100 - len(issues) * 10)
        
        return {
            "quality_score": quality_score,
            "issues": issues,
            "lines_analyzed": len(lines),
            "language": language,
        }

    async def recommend_stack(self, requirements: dict) -> dict:
        """Recomendar stack técnico basado en requerimientos."""
        project_type = requirements.get("type", "web_app")
        scale = requirements.get("expected_users", 1000)
        budget = requirements.get("monthly_budget_usd", 100)
        
        if project_type == "web_app" and scale < 10000:
            return {
                "frontend": "React + Vite + Tailwind CSS",
                "backend": "FastAPI (Python 3.11+)",
                "database": "PostgreSQL (Supabase)",
                "hosting": "Vercel (frontend) + Railway (backend)",
                "cache": "Upstash Redis" if scale > 1000 else "In-memory",
                "ci_cd": "GitHub Actions",
                "monitoring": "Sentry + Langfuse",
                "estimated_cost": f"${min(budget, 50)}/month",
                "rationale": "Optimized for speed of development and cost efficiency at this scale",
            }
        elif project_type == "api" or scale >= 10000:
            return {
                "frontend": "N/A (API only)" if project_type == "api" else "Next.js",
                "backend": "FastAPI (Python 3.11+) with async workers",
                "database": "PostgreSQL with read replicas",
                "hosting": "AWS ECS or GCP Cloud Run",
                "cache": "Upstash Redis + CDN edge caching",
                "ci_cd": "GitHub Actions + ArgoCD",
                "monitoring": "Sentry + Datadog + Langfuse",
                "estimated_cost": f"${min(budget, 200)}/month",
                "rationale": "Designed for horizontal scaling and high availability",
            }
        
        return {"error": "Unsupported project type"}
```

### Criterios de Aceptación

1. `EmbrionTecnico` hereda de `EmbrionLoop` con system prompt de arquitectura
2. `audit_architecture()` evalúa estructura de proyecto con scoring
3. `review_code_quality()` detecta anti-patterns, secrets, y code smells
4. `recommend_stack()` sugiere stack basado en requerimientos
5. 5 tareas autónomas con budget y prioridad
6. Detección de .env en repo (CRITICAL), falta de tests, líneas largas
7. Tests unitarios para cada método

---

## Épica 58.5 — Embrión-Vigía

### Objetivo

Crear el tercer Embrión especializado: guardián de seguridad y monitoreo. Opera 24/7 vigilando la salud del sistema, detectando anomalías, y alertando proactivamente.

### Diseño

```
kernel/
  embrion_vigia.py           ← Embrión-Vigía
  embrion_specializations/
    vigia_knowledge.py       ← Knowledge base de seguridad
    vigia_prompts.py         ← System prompts especializados
```

### Implementación

**Archivo: `kernel/embrion_vigia.py`**

```python
"""
embrion_vigia.py — Embrión-Vigía: Guardián de Seguridad y Monitoreo
=====================================================================
Tercer Embrión especializado (Obj #11).
Expertise: seguridad, monitoreo, alertas, health checks, anomaly detection.

Opera 24/7 vigilando:
  - Health del sistema (API response times, error rates)
  - Seguridad (intentos de intrusión, anomalías de tráfico)
  - Costos (budget overruns, usage spikes)
  - Dependencias (CVEs, updates disponibles)
  - Uptime (endpoints caídos, degradación de servicio)

Sprint 58 — "La Fortaleza Completa"
"""
import logging
from typing import Optional
from datetime import datetime, timezone, timedelta
from kernel.embrion_loop import EmbrionLoop

logger = logging.getLogger("embrion_vigia")


class EmbrionVigia(EmbrionLoop):
    """Embrión especializado en seguridad y monitoreo."""

    EMBRION_ID = "embrion-vigia"
    SPECIALIZATION = "vigia"
    
    SYSTEM_PROMPT = """Eres Embrión-Vigía, el guardián de seguridad y monitoreo 
    del sistema El Monstruo. Tu misión es proteger y vigilar 24/7.
    
    Tu expertise incluye:
    
    1. SECURITY MONITORING: Detección de intrusiones, anomalías de tráfico
    2. HEALTH CHECKS: API response times, error rates, uptime
    3. COST MONITORING: Budget overruns, usage spikes, waste detection
    4. DEPENDENCY SECURITY: CVE scanning, update notifications
    5. INCIDENT RESPONSE: Alertas, escalación, post-mortems
    6. COMPLIANCE: GDPR, SOC2, data retention policies
    
    Principios:
    - Paranoia productiva. Asume que todo puede fallar y prepárate.
    - Alertas accionables. Nunca alert fatigue. Solo alertar si requiere acción.
    - Defense in depth. Múltiples capas de protección.
    - Fail safe. Si algo falla, falla de forma segura (deny by default).
    """

    # Alert severity levels
    SEVERITY_CRITICAL = "critical"  # Immediate action required
    SEVERITY_HIGH = "high"          # Action within 1 hour
    SEVERITY_MEDIUM = "medium"      # Action within 24 hours
    SEVERITY_LOW = "low"            # Informational

    DEFAULT_TASKS = {
        "health_check": {
            "description": "Verificar health de todos los endpoints",
            "interval_hours": 1,
            "max_cost_usd": 0.02,
            "priority": 1,
        },
        "security_scan": {
            "description": "Escanear intentos de intrusión en logs",
            "interval_hours": 4,
            "max_cost_usd": 0.10,
            "priority": 1,
        },
        "cost_monitor": {
            "description": "Verificar que costos están dentro de budget",
            "interval_hours": 6,
            "max_cost_usd": 0.05,
            "priority": 2,
        },
        "dependency_audit": {
            "description": "Escanear CVEs en dependencias",
            "interval_hours": 24,
            "max_cost_usd": 0.15,
            "priority": 2,
        },
        "uptime_report": {
            "description": "Generar reporte de uptime diario",
            "interval_hours": 24,
            "max_cost_usd": 0.05,
            "priority": 3,
        },
    }

    def __init__(self, db=None, sabios=None, alert_monitor=None, sentry_client=None):
        super().__init__(db=db, sabios=sabios)
        self._alert_monitor = alert_monitor  # SovereignAlertMonitor
        self._sentry = sentry_client

    async def health_check(self, endpoints: list[str]) -> dict:
        """Verificar health de endpoints."""
        import httpx
        
        results = []
        healthy = 0
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint in endpoints:
                try:
                    start = datetime.now(timezone.utc)
                    response = await client.get(endpoint)
                    latency_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
                    
                    is_healthy = response.status_code < 400 and latency_ms < 5000
                    if is_healthy:
                        healthy += 1
                    
                    results.append({
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "latency_ms": round(latency_ms, 2),
                        "healthy": is_healthy,
                    })
                except Exception as e:
                    results.append({
                        "endpoint": endpoint,
                        "status_code": 0,
                        "latency_ms": -1,
                        "healthy": False,
                        "error": str(e),
                    })
        
        uptime_pct = (healthy / max(len(endpoints), 1)) * 100
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_endpoints": len(endpoints),
            "healthy": healthy,
            "unhealthy": len(endpoints) - healthy,
            "uptime_percentage": round(uptime_pct, 2),
            "results": results,
            "alert": self.SEVERITY_CRITICAL if uptime_pct < 50 else (
                self.SEVERITY_HIGH if uptime_pct < 80 else None
            ),
        }

    async def detect_anomalies(self, metrics: list[dict]) -> dict:
        """Detectar anomalías en métricas usando statistical analysis."""
        if len(metrics) < 10:
            return {"anomalies": [], "status": "insufficient_data"}
        
        # Simple z-score based anomaly detection
        values = [m.get("value", 0) for m in metrics]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        anomalies = []
        for i, m in enumerate(metrics):
            if std_dev > 0:
                z_score = abs((m.get("value", 0) - mean) / std_dev)
                if z_score > 3:  # 3 sigma rule
                    anomalies.append({
                        "index": i,
                        "value": m.get("value"),
                        "z_score": round(z_score, 2),
                        "timestamp": m.get("timestamp"),
                        "severity": self.SEVERITY_HIGH if z_score > 4 else self.SEVERITY_MEDIUM,
                    })
        
        return {
            "anomalies": anomalies,
            "total_points": len(metrics),
            "mean": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "status": "anomalies_detected" if anomalies else "normal",
        }

    async def audit_dependencies(self, requirements_txt: str) -> dict:
        """Auditar dependencias por vulnerabilidades conocidas."""
        # Parse requirements
        deps = []
        for line in requirements_txt.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                # Parse package==version
                parts = line.split("==")
                if len(parts) == 2:
                    deps.append({"package": parts[0], "version": parts[1]})
                else:
                    parts = line.split(">=")
                    if len(parts) == 2:
                        deps.append({"package": parts[0], "version": parts[1], "pinned": False})
        
        # In production, this would query PyPI advisory database or safety-db
        warnings = []
        for dep in deps:
            if not dep.get("version"):
                warnings.append({
                    "package": dep["package"],
                    "issue": "Version not pinned — unpredictable builds",
                    "severity": self.SEVERITY_LOW,
                })
        
        return {
            "total_dependencies": len(deps),
            "pinned": sum(1 for d in deps if "==" in str(d.get("version", ""))),
            "unpinned": sum(1 for d in deps if "==" not in str(d.get("version", ""))),
            "warnings": warnings,
            "scan_date": datetime.now(timezone.utc).isoformat(),
            "status": "clean" if not warnings else "warnings_found",
        }

    async def generate_incident_report(self, incident: dict) -> dict:
        """Generar reporte de incidente post-mortem."""
        return {
            "title": incident.get("title", "Untitled Incident"),
            "severity": incident.get("severity", self.SEVERITY_MEDIUM),
            "timeline": {
                "detected_at": incident.get("detected_at"),
                "acknowledged_at": incident.get("acknowledged_at"),
                "resolved_at": incident.get("resolved_at"),
                "duration_minutes": incident.get("duration_minutes", 0),
            },
            "impact": incident.get("impact", "Unknown"),
            "root_cause": incident.get("root_cause", "Under investigation"),
            "resolution": incident.get("resolution", "Pending"),
            "action_items": incident.get("action_items", [
                "Add monitoring for this failure mode",
                "Create runbook for similar incidents",
                "Review and update alerting thresholds",
            ]),
            "lessons_learned": incident.get("lessons_learned", []),
            "generated_by": self.EMBRION_ID,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
```

### Criterios de Aceptación

1. `EmbrionVigia` hereda de `EmbrionLoop` con system prompt de seguridad
2. `health_check()` verifica endpoints con latencia y status code
3. `detect_anomalies()` usa z-score (3-sigma) para detección estadística
4. `audit_dependencies()` parsea requirements.txt y detecta unpinned deps
5. `generate_incident_report()` produce post-mortem estructurado
6. 5 tareas autónomas con intervalos agresivos (1h para health checks)
7. Integración con SovereignAlertMonitor existente
8. Tests unitarios para cada método

---

## Dependencias Nuevas

```
# requirements.txt additions
upstash-redis==1.7.0     # Serverless Redis for caching (Épica 58.2)
sentry-sdk==2.56.0       # Error monitoring (Épica 58.5)
httpx>=0.27.0            # Async HTTP client for health checks (ya debería existir)
```

---

## Estructura de Archivos Nuevos

```
transversal/
  security_layer.py                    ← Épica 58.1
  auth_templates.py
  headers_config.py
  cors_config.py
  input_sanitizer.py
  scalability_layer.py                 ← Épica 58.2
  caching_strategy.py
  cdn_config.py
  db_optimizer.py
  scaling_patterns.py
  analytics_layer.py                   ← Épica 58.3
  event_taxonomy.py
  retention_analyzer.py
  engagement_scorer.py

kernel/
  embrion_tecnico.py                   ← Épica 58.4
  embrion_vigia.py                     ← Épica 58.5
  embrion_specializations/
    tecnico_knowledge.py
    tecnico_prompts.py
    vigia_knowledge.py
    vigia_prompts.py
```

---

## Estimación de Costos

| Componente | Costo Mensual Estimado |
|---|---|
| Upstash Redis (free tier) | $0 (hasta 10K commands/day) |
| Sentry (free tier) | $0 (hasta 5K errors/month) |
| Embrión-Técnico (LLM calls) | $3-8/mes |
| Embrión-Vigía (health checks + LLM) | $2-5/mes |
| PostHog analytics (ya incluido) | $0 |
| **Total adicional** | **$5-13/mes** |

---

## Orden de Implementación

| Paso | Épica | Dependencia | Esfuerzo |
|---|---|---|---|
| 1 | 58.1 — Security Layer | Ninguna | 5 horas |
| 2 | 58.2 — Scalability Layer | Ninguna | 5 horas |
| 3 | 58.3 — Analytics Layer | PostHog (Sprint 57) | 4 horas |
| 4 | 58.4 — Embrión-Técnico | EmbrionLoop | 4 horas |
| 5 | 58.5 — Embrión-Vigía | SovereignAlertMonitor + Sentry | 5 horas |
| **Total** | | | **23 horas** |

---

## Milestone: Obj #9 Completado

Con Sprint 58, las **6 capas transversales** del Objetivo #9 están completas:

| Capa | Sprint | Componente |
|---|---|---|
| 1. Sales Engine | Sprint 57 | `transversal/sales_engine.py` |
| 2. SEO Architecture | Sprint 57 | `transversal/seo_layer.py` |
| 3. Security | **Sprint 58** | `transversal/security_layer.py` |
| 4. Scalability | **Sprint 58** | `transversal/scalability_layer.py` |
| 5. Analytics | **Sprint 58** | `transversal/analytics_layer.py` |
| 6. Financial Dashboard | Sprint 57 | `transversal/financial_layer.py` |

> Todo negocio que El Monstruo cree a partir de ahora nace como una fortaleza completa.

---

## References

[1]: https://pypi.org/project/upstash-redis/ "upstash-redis 1.7.0 — PyPI"
[2]: https://pypi.org/project/sentry-sdk/ "sentry-sdk ~2.56.0 — PyPI"
[3]: https://pypi.org/project/posthog/ "PostHog Python SDK 7.13.2 — PyPI"
[4]: https://fastapi.tiangolo.com/tutorial/cors/ "CORS — FastAPI Documentation"
[5]: https://upstash.com/docs/redis/sdks/py/overview "Upstash Redis Python SDK Documentation"
[6]: https://docs.sentry.io/platforms/python/integrations/fastapi/ "Sentry FastAPI Integration"
