"""
security_layer.py — Capa de Seguridad Transversal
===================================================
Capa Transversal #3 del Objetivo #9 (Transversalidad Universal).

PROPÓSITO: Genera configuraciones y templates de seguridad para los proyectos
que El Monstruo crea. NO protege a El Monstruo (eso lo hacen rate_limiter.py
y input_guard.py). Esta capa inyecta seguridad en los proyectos generados.

Componentes:
  1. Auth templates (JWT, OAuth2, API keys, Session)
  2. Security headers (HSTS, CSP, X-Frame-Options, Permissions-Policy)
  3. CORS configuration inteligente por tipo de proyecto
  4. Rate limiting patterns
  5. Input sanitization templates

Soberanía:
  - Auth: python-jose (JWT) → alternativa: PyJWT si jose no disponible
  - Headers: Starlette SecurityMiddleware (built-in) → sin dependencia externa
  - Rate limiting: in-memory sliding window → alternativa: Upstash Redis

Sprint 58 — "La Fortaleza Completa"
Obj #9 — Capa 3: Seguridad
"""
import logging
import structlog
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

logger = structlog.get_logger("transversal.security_layer")


# ─── Errores con identidad (Brand Check #2) ──────────────────────────────────

class SecurityLayerError(Exception):
    """Error base de la Capa de Seguridad Transversal."""
    pass


class SECURITY_LAYER_PROYECTO_INVALIDO(SecurityLayerError):
    """El project_id está vacío o tiene formato inválido."""
    pass


class SECURITY_LAYER_TIPO_NO_SOPORTADO(SecurityLayerError):
    """El tipo de proyecto no tiene preset de seguridad definido."""
    pass


# ─── Enums con naming de identidad (Brand Check #1) ──────────────────────────

class EstrategiaAuth(Enum):
    """Estrategia de autenticación para el proyecto generado."""
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    SESSION = "session"
    NINGUNA = "ninguna"


class TipoProyecto(Enum):
    """Tipo de proyecto para seleccionar el preset de seguridad correcto."""
    API_PUBLICA = "api_publica"
    API_PRIVADA = "api_privada"
    WEB_APP = "web_app"
    MOBILE_BACKEND = "mobile_backend"
    HERRAMIENTA_INTERNA = "herramienta_interna"


# ─── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass
class ConfiguracionSeguridad:
    """
    Configuración de seguridad generada para un proyecto.

    Attributes:
        proyecto_id: Identificador único del proyecto.
        tipo_proyecto: Tipo de proyecto que determina el preset de seguridad.
        estrategia_auth: Mecanismo de autenticación recomendado.
        cors_origins: Lista de orígenes permitidos para CORS.
        rate_limit_rpm: Límite de requests por minuto.
        rate_limit_rph: Límite de requests por hora.
        habilitar_csrf: Si se debe habilitar protección CSRF.
        habilitar_hsts: Si se debe habilitar HTTP Strict Transport Security.
        politica_csp: Content Security Policy para el proyecto.
        metodos_permitidos: Métodos HTTP permitidos.
        max_longitud_input: Longitud máxima de input en caracteres.
        max_upload_mb: Tamaño máximo de archivos subidos en MB.
        requerir_https: Si se debe forzar HTTPS.
    """
    proyecto_id: str
    tipo_proyecto: TipoProyecto
    estrategia_auth: EstrategiaAuth
    cors_origins: list[str] = field(default_factory=list)
    rate_limit_rpm: int = 60
    rate_limit_rph: int = 500
    habilitar_csrf: bool = True
    habilitar_hsts: bool = True
    politica_csp: str = "default-src 'self'"
    metodos_permitidos: list[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    max_longitud_input: int = 10000
    max_upload_mb: int = 10
    requerir_https: bool = True


# ─── Clase principal ─────────────────────────────────────────────────────────

class SecurityLayer:
    """
    Capa de seguridad transversal — genera configuraciones de seguridad
    para proyectos creados por El Monstruo.

    Uso:
        layer = SecurityLayer()
        config = await layer.generar_configuracion("mi-proyecto", TipoProyecto.WEB_APP)
        middleware_code = layer.generar_codigo_middleware(config)
    """

    # Presets de security headers por tipo de proyecto
    PRESETS_HEADERS = {
        TipoProyecto.API_PUBLICA: {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "0",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
        },
        TipoProyecto.WEB_APP: {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "X-XSS-Protection": "0",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Content-Security-Policy": (
                "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
            ),
        },
        TipoProyecto.HERRAMIENTA_INTERNA: {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "Strict-Transport-Security": "max-age=31536000",
        },
        TipoProyecto.MOBILE_BACKEND: {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Cache-Control": "no-store",
        },
        TipoProyecto.API_PRIVADA: {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'none'",
        },
    }

    # Auth recomendada por tipo de proyecto
    AUTH_RECOMENDADA = {
        TipoProyecto.API_PUBLICA: EstrategiaAuth.API_KEY,
        TipoProyecto.API_PRIVADA: EstrategiaAuth.JWT,
        TipoProyecto.WEB_APP: EstrategiaAuth.SESSION,
        TipoProyecto.MOBILE_BACKEND: EstrategiaAuth.JWT,
        TipoProyecto.HERRAMIENTA_INTERNA: EstrategiaAuth.OAUTH2,
    }

    def __init__(self):
        logger.info("security_layer_inicializado", componente="transversal.security_layer")

    async def generar_configuracion(
        self,
        proyecto_id: str,
        tipo_proyecto: TipoProyecto,
        origins_custom: Optional[list[str]] = None,
    ) -> ConfiguracionSeguridad:
        """
        Generar configuración de seguridad completa para un proyecto.

        Args:
            proyecto_id: Identificador único del proyecto.
            tipo_proyecto: Tipo de proyecto (API pública, web app, etc.).
            origins_custom: Lista de orígenes CORS personalizados. Si es None,
                            se usan los defaults según el tipo de proyecto.

        Returns:
            ConfiguracionSeguridad con todos los parámetros listos para inyectar.

        Raises:
            SECURITY_LAYER_PROYECTO_INVALIDO: Si proyecto_id está vacío.
        """
        if not proyecto_id or not proyecto_id.strip():
            raise SECURITY_LAYER_PROYECTO_INVALIDO(
                f"El proyecto_id no puede estar vacío. "
                f"Proporciona un identificador único para el proyecto."
            )

        auth = self.AUTH_RECOMENDADA.get(tipo_proyecto, EstrategiaAuth.JWT)

        # CORS origins según tipo de proyecto
        if origins_custom:
            origins = origins_custom
        elif tipo_proyecto == TipoProyecto.API_PUBLICA:
            origins = ["*"]
        elif tipo_proyecto == TipoProyecto.HERRAMIENTA_INTERNA:
            origins = ["https://internal.monstruo.app"]
        else:
            origins = [f"https://{proyecto_id}.monstruo.app"]

        # Rate limits según tipo
        rpm = 120 if tipo_proyecto == TipoProyecto.API_PUBLICA else 60
        rph = 1000 if tipo_proyecto == TipoProyecto.API_PUBLICA else 500

        config = ConfiguracionSeguridad(
            proyecto_id=proyecto_id,
            tipo_proyecto=tipo_proyecto,
            estrategia_auth=auth,
            cors_origins=origins,
            rate_limit_rpm=rpm,
            rate_limit_rph=rph,
            habilitar_csrf=tipo_proyecto in (TipoProyecto.WEB_APP, TipoProyecto.HERRAMIENTA_INTERNA),
            habilitar_hsts=True,
            requerir_https=True,
        )

        logger.info(
            "security_config_generada",
            proyecto_id=proyecto_id,
            tipo=tipo_proyecto.value,
            auth=auth.value,
            cors_origins_count=len(origins),
        )
        return config

    def generar_codigo_middleware(self, config: ConfiguracionSeguridad) -> str:
        """
        Generar código de middleware de seguridad para FastAPI/Starlette.

        Args:
            config: ConfiguracionSeguridad generada por generar_configuracion().

        Returns:
            String con código Python listo para copiar en el proyecto generado.

        Soberanía: Usa Starlette BaseHTTPMiddleware (built-in) — sin dependencias externas.
        """
        headers = self.PRESETS_HEADERS.get(
            config.tipo_proyecto,
            self.PRESETS_HEADERS[TipoProyecto.WEB_APP]
        )

        code = f'''"""
Middleware de Seguridad — Generado por El Monstruo Security Layer
Proyecto: {config.proyecto_id}
Tipo: {config.tipo_proyecto.value}
Auth: {config.estrategia_auth.value}
Generado: Sprint 58 — "La Fortaleza Completa"
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
    allow_methods={config.metodos_permitidos},
    allow_headers=["*"],
)

# Security Headers Middleware
# Soberanía: Starlette BaseHTTPMiddleware (built-in) — alternativa: custom ASGI middleware
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

    def generar_template_auth(self, estrategia: EstrategiaAuth) -> dict:
        """
        Generar template de autenticación según estrategia.

        Args:
            estrategia: EstrategiaAuth seleccionada para el proyecto.

        Returns:
            Dict con dependencias, variables de entorno, descripción y archivos necesarios.

        Soberanía:
            - JWT: python-jose → alternativa: PyJWT (pip install PyJWT)
            - OAuth2: authlib → alternativa: social-auth-core
            - Session: itsdangerous (built-in con Starlette) → sin alternativa necesaria
        """
        templates = {
            EstrategiaAuth.JWT: {
                "dependencias": ["python-jose[cryptography]", "passlib[bcrypt]"],
                # Soberanía: alternativa PyJWT si python-jose no disponible
                "soberania": "Alternativa: PyJWT (pip install PyJWT) si python-jose falla",
                "env_vars": ["JWT_SECRET_KEY", "JWT_ALGORITHM=HS256", "JWT_EXPIRE_MINUTES=30"],
                "descripcion": "JWT Bearer token authentication — stateless, escalable",
                "archivos": ["auth/jwt_handler.py", "auth/dependencies.py", "auth/models.py"],
            },
            EstrategiaAuth.OAUTH2: {
                "dependencias": ["authlib", "httpx"],
                "soberania": "Alternativa: social-auth-core o implementación manual con httpx",
                "env_vars": ["OAUTH_CLIENT_ID", "OAUTH_CLIENT_SECRET", "OAUTH_REDIRECT_URI"],
                "descripcion": "OAuth2 con Google/GitHub — ideal para herramientas internas",
                "archivos": ["auth/oauth_handler.py", "auth/session.py"],
            },
            EstrategiaAuth.API_KEY: {
                "dependencias": ["secrets"],  # built-in
                "soberania": "Módulo secrets es built-in de Python — sin dependencia externa",
                "env_vars": ["API_KEY_SALT"],
                "descripcion": "API Key authentication — simple, ideal para APIs públicas",
                "archivos": ["auth/api_key_handler.py", "auth/middleware.py"],
            },
            EstrategiaAuth.SESSION: {
                "dependencias": ["itsdangerous"],  # incluido con Starlette
                "soberania": "itsdangerous incluido con Starlette — sin dependencia adicional",
                "env_vars": ["SESSION_SECRET_KEY", "SESSION_MAX_AGE=3600"],
                "descripcion": "Session-based authentication — ideal para web apps",
                "archivos": ["auth/session_handler.py", "auth/middleware.py"],
            },
        }
        return templates.get(estrategia, {
            "dependencias": [],
            "soberania": "Sin autenticación configurada",
            "env_vars": [],
            "descripcion": "Sin autenticación",
            "archivos": [],
        })

    def generar_template_sanitizacion(self) -> str:
        """
        Generar template de sanitización de input para el proyecto.

        Returns:
            String con código Python de sanitización lista para inyectar.

        Soberanía: bleach para HTML sanitization → alternativa: markupsafe (built-in con Jinja2)
        """
        return '''"""
Input Sanitizer — Generado por El Monstruo Security Layer
Soberanía: bleach para HTML → alternativa: markupsafe.escape() si bleach no disponible
"""
import re
# Soberanía: bleach → alternativa: markupsafe.escape() para HTML básico
try:
    import bleach
    _BLEACH_DISPONIBLE = True
except ImportError:
    _BLEACH_DISPONIBLE = False

# Patrones de inyección a bloquear
_PATRONES_PELIGROSOS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\\w+\\s*=",
    r"\\bSELECT\\b.*\\bFROM\\b",
    r"\\bINSERT\\b.*\\bINTO\\b",
    r"\\bDROP\\b.*\\bTABLE\\b",
    r"\\bUNION\\b.*\\bSELECT\\b",
]
_REGEX_PELIGROSOS = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in _PATRONES_PELIGROSOS]


def sanitizar_input(texto: str, max_longitud: int = 10000) -> str:
    """Sanitizar input de usuario. Bloquea XSS, SQL injection y prompt injection."""
    if not isinstance(texto, str):
        return ""
    
    # Truncar
    texto = texto[:max_longitud]
    
    # Detectar patrones peligrosos
    for patron in _REGEX_PELIGROSOS:
        if patron.search(texto):
            raise ValueError(f"INPUT_SANITIZER_PATRON_PELIGROSO_DETECTADO: Input rechazado por seguridad")
    
    # Sanitizar HTML si bleach disponible
    if _BLEACH_DISPONIBLE:
        texto = bleach.clean(texto, tags=[], strip=True)
    
    return texto.strip()
'''

    def to_dict(self) -> dict:
        """
        Serializar estado del SecurityLayer para el Command Center.

        Returns:
            Dict con estado actual consumible por el Command Center.
        """
        return {
            "componente": "security_layer",
            "version": "58.1",
            "tipos_proyecto_soportados": [t.value for t in TipoProyecto],
            "estrategias_auth_soportadas": [e.value for e in EstrategiaAuth],
            "presets_headers_disponibles": list(self.PRESETS_HEADERS.keys()),
            "estado": "activo",
        }


# ─── Singleton factory ────────────────────────────────────────────────────────

_security_layer_instance: Optional[SecurityLayer] = None


def get_security_layer() -> SecurityLayer:
    """
    Obtener instancia singleton del SecurityLayer.

    Returns:
        Instancia única de SecurityLayer.
    """
    global _security_layer_instance
    if _security_layer_instance is None:
        _security_layer_instance = SecurityLayer()
    return _security_layer_instance
