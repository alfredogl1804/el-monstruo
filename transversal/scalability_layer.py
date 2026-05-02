"""
scalability_layer.py — Capa de Escalabilidad Transversal
=========================================================
Capa Transversal #4 del Objetivo #9 (Transversalidad Universal).

PROPÓSITO: Genera configuraciones y templates de escalabilidad para los proyectos
que El Monstruo crea. Cada proyecto nace con la arquitectura correcta para su
escala esperada — desde 100 usuarios hasta 1M+.

Componentes:
  1. Recomendación automática de estrategia de caching (Redis/in-memory/CDN)
  2. Configuración de CDN (Cloudflare, Vercel Edge)
  3. Patrones de optimización de base de datos
  4. Patrones de escalamiento horizontal
  5. Performance budgets (Core Web Vitals)

Soberanía:
  - Redis: upstash-redis → alternativa: redis-py con Redis local
  - CDN: Cloudflare → alternativa: Vercel Edge, AWS CloudFront
  - DB pooling: asyncpg → alternativa: psycopg3

Sprint 58 — "La Fortaleza Completa"
Obj #9 — Capa 4: Escalabilidad
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import structlog

logger = structlog.get_logger("transversal.scalability_layer")


# ─── Errores con identidad (Brand Check #2) ──────────────────────────────────


class ScalabilityLayerError(Exception):
    """Error base de la Capa de Escalabilidad Transversal."""

    pass


class SCALABILITY_LAYER_USUARIOS_INVALIDOS(ScalabilityLayerError):
    """El número de usuarios esperados es inválido (debe ser > 0)."""

    pass


# ─── Enums con naming de identidad (Brand Check #1) ──────────────────────────


class EstrategiaCaching(Enum):
    """Estrategia de caching recomendada según escala."""

    NINGUNA = "ninguna"
    EN_MEMORIA = "en_memoria"
    REDIS = "redis"
    CDN_EDGE = "cdn_edge"
    HIBRIDA = "hibrida"  # Redis + CDN edge


class PatronEscalamiento(Enum):
    """Patrón de escalamiento horizontal/vertical."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    SERVERLESS = "serverless"
    HIBRIDO = "hibrido"


class PatronBaseDatos(Enum):
    """Patrón de arquitectura de base de datos."""

    SIMPLE = "simple"
    REPLICAS_LECTURA = "replicas_lectura"
    SHARDING = "sharding"
    CQRS = "cqrs"


# ─── Dataclasses ─────────────────────────────────────────────────────────────


@dataclass
class PresupuestoPerformance:
    """
    Performance budget basado en Core Web Vitals.

    Attributes:
        ttfb_ms: Time to First Byte (objetivo: <200ms).
        fcp_ms: First Contentful Paint (objetivo: <1000ms).
        lcp_ms: Largest Contentful Paint (objetivo: <2500ms).
        cls: Cumulative Layout Shift (objetivo: <0.1).
        fid_ms: First Input Delay (objetivo: <100ms).
        bundle_kb: Tamaño máximo del bundle JS en KB.
        api_p95_ms: Latencia p95 de la API en ms.
    """

    ttfb_ms: int = 200
    fcp_ms: int = 1000
    lcp_ms: int = 2500
    cls: float = 0.1
    fid_ms: int = 100
    bundle_kb: int = 200
    api_p95_ms: int = 500


@dataclass
class ConfiguracionEscalabilidad:
    """
    Configuración de escalabilidad generada para un proyecto.

    Attributes:
        proyecto_id: Identificador único del proyecto.
        usuarios_esperados: Número de usuarios concurrentes esperados.
        estrategia_caching: Estrategia de caching recomendada.
        patron_escalamiento: Patrón de escalamiento recomendado.
        patron_db: Patrón de arquitectura de base de datos.
        presupuesto_performance: Core Web Vitals targets.
        cdn_habilitado: Si se recomienda usar CDN.
        redis_url: URL de conexión a Redis (si aplica).
    """

    proyecto_id: str
    usuarios_esperados: int
    estrategia_caching: EstrategiaCaching
    patron_escalamiento: PatronEscalamiento
    patron_db: PatronBaseDatos
    presupuesto_performance: PresupuestoPerformance = field(default_factory=PresupuestoPerformance)
    cdn_habilitado: bool = True
    redis_url: Optional[str] = None


# ─── Clase principal ─────────────────────────────────────────────────────────


class ScalabilityLayer:
    """
    Capa de escalabilidad transversal — genera configuraciones de escalabilidad
    para proyectos creados por El Monstruo.

    Uso:
        layer = ScalabilityLayer()
        config = await layer.generar_configuracion("mi-proyecto", 10000)
        caching_code = layer.generar_codigo_caching(config.estrategia_caching)
    """

    # Umbrales de usuarios → recomendaciones automáticas
    UMBRALES_USUARIOS = {
        100: {
            "caching": EstrategiaCaching.EN_MEMORIA,
            "escalamiento": PatronEscalamiento.VERTICAL,
            "db": PatronBaseDatos.SIMPLE,
        },
        1_000: {
            "caching": EstrategiaCaching.REDIS,
            "escalamiento": PatronEscalamiento.VERTICAL,
            "db": PatronBaseDatos.SIMPLE,
        },
        10_000: {
            "caching": EstrategiaCaching.HIBRIDA,
            "escalamiento": PatronEscalamiento.HORIZONTAL,
            "db": PatronBaseDatos.REPLICAS_LECTURA,
        },
        100_000: {
            "caching": EstrategiaCaching.HIBRIDA,
            "escalamiento": PatronEscalamiento.HORIZONTAL,
            "db": PatronBaseDatos.CQRS,
        },
        1_000_000: {
            "caching": EstrategiaCaching.HIBRIDA,
            "escalamiento": PatronEscalamiento.SERVERLESS,
            "db": PatronBaseDatos.SHARDING,
        },
    }

    def __init__(self, redis_client=None):
        # Soberanía: upstash-redis → alternativa: redis-py con Redis local
        self._redis = redis_client
        logger.info("scalability_layer_inicializado", componente="transversal.scalability_layer")

    async def generar_configuracion(
        self,
        proyecto_id: str,
        usuarios_esperados: int,
    ) -> ConfiguracionEscalabilidad:
        """
        Generar configuración de escalabilidad basada en usuarios esperados.

        Args:
            proyecto_id: Identificador único del proyecto.
            usuarios_esperados: Número de usuarios concurrentes esperados.

        Returns:
            ConfiguracionEscalabilidad con estrategias recomendadas.

        Raises:
            SCALABILITY_LAYER_USUARIOS_INVALIDOS: Si usuarios_esperados <= 0.
        """
        if usuarios_esperados <= 0:
            raise SCALABILITY_LAYER_USUARIOS_INVALIDOS(
                f"El número de usuarios esperados debe ser mayor a 0. "
                f"Recibido: {usuarios_esperados}. "
                f"Ejemplo: 1000 para un proyecto pequeño, 100000 para uno mediano."
            )

        # Encontrar el umbral apropiado
        recomendacion = {
            "caching": EstrategiaCaching.EN_MEMORIA,
            "escalamiento": PatronEscalamiento.VERTICAL,
            "db": PatronBaseDatos.SIMPLE,
        }
        for umbral, config in sorted(self.UMBRALES_USUARIOS.items()):
            if usuarios_esperados >= umbral:
                recomendacion = config

        # Ajustar performance budget según escala
        if usuarios_esperados >= 100_000:
            presupuesto = PresupuestoPerformance(
                ttfb_ms=100, fcp_ms=800, lcp_ms=2000, cls=0.05, fid_ms=50, bundle_kb=150, api_p95_ms=300
            )
        elif usuarios_esperados >= 10_000:
            presupuesto = PresupuestoPerformance(
                ttfb_ms=150, fcp_ms=900, lcp_ms=2200, cls=0.08, fid_ms=75, bundle_kb=175, api_p95_ms=400
            )
        else:
            presupuesto = PresupuestoPerformance()

        config = ConfiguracionEscalabilidad(
            proyecto_id=proyecto_id,
            usuarios_esperados=usuarios_esperados,
            estrategia_caching=recomendacion["caching"],
            patron_escalamiento=recomendacion["escalamiento"],
            patron_db=recomendacion["db"],
            presupuesto_performance=presupuesto,
            cdn_habilitado=usuarios_esperados >= 1_000,
        )

        logger.info(
            "scalability_config_generada",
            proyecto_id=proyecto_id,
            usuarios_esperados=usuarios_esperados,
            caching=recomendacion["caching"].value,
            escalamiento=recomendacion["escalamiento"].value,
            db=recomendacion["db"].value,
        )
        return config

    def generar_codigo_caching(self, estrategia: EstrategiaCaching) -> str:
        """
        Generar código de caching según estrategia recomendada.

        Args:
            estrategia: EstrategiaCaching seleccionada.

        Returns:
            String con código Python listo para copiar en el proyecto generado.

        Soberanía:
            - Redis: upstash-redis → alternativa: redis-py con Redis local
            - In-memory: built-in Python dict — sin dependencias externas
        """
        if estrategia == EstrategiaCaching.REDIS:
            return '''"""
Caching Layer — Redis (Upstash) — Generado por El Monstruo
Soberanía: upstash-redis → alternativa: redis-py con Redis local (pip install redis)
"""
import os
from functools import wraps
# Soberanía: upstash-redis → alternativa: from redis import Redis
from upstash_redis import Redis

redis = Redis(
    url=os.environ["UPSTASH_REDIS_REST_URL"],
    token=os.environ["UPSTASH_REDIS_REST_TOKEN"],
)

def cache(ttl_segundos: int = 300):
    """Decorator para cachear resultados de funciones en Redis."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            clave = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Intentar desde cache primero
            cached = redis.get(clave)
            if cached is not None:
                return cached
            
            # Ejecutar y cachear
            resultado = await func(*args, **kwargs)
            redis.set(clave, resultado, ex=ttl_segundos)
            return resultado
        return wrapper
    return decorator
'''
        elif estrategia in (EstrategiaCaching.EN_MEMORIA, EstrategiaCaching.NINGUNA):
            return '''"""
Caching Layer — In-Memory (LRU) — Generado por El Monstruo
Soberanía: built-in Python — sin dependencias externas
"""
from datetime import datetime, timedelta

# Cache simple con TTL — para proyectos pequeños (<1000 usuarios)
_cache: dict = {}
_cache_ttl: dict = {}


def cache_get(clave: str):
    """Obtener valor del cache si no expiró."""
    if clave in _cache and datetime.now() < _cache_ttl.get(clave, datetime.min):
        return _cache[clave]
    return None


def cache_set(clave: str, valor, ttl_segundos: int = 300):
    """Guardar valor en cache con TTL."""
    _cache[clave] = valor
    _cache_ttl[clave] = datetime.now() + timedelta(seconds=ttl_segundos)


def cache_invalidar(clave: str):
    """Invalidar entrada del cache."""
    _cache.pop(clave, None)
    _cache_ttl.pop(clave, None)
'''
        return "# Sin estrategia de caching configurada"

    def generar_config_cdn(self, proveedor: str = "cloudflare") -> dict:
        """
        Generar configuración de CDN para el proyecto.

        Args:
            proveedor: Proveedor de CDN. Opciones: "cloudflare", "vercel".

        Returns:
            Dict con configuración de CDN lista para aplicar.

        Soberanía: Cloudflare → alternativa: Vercel Edge Network, AWS CloudFront
        """
        configs = {
            "cloudflare": {
                "proveedor": "Cloudflare",
                # Soberanía: alternativa Vercel Edge o AWS CloudFront
                "soberania": "Alternativa: Vercel Edge Network o AWS CloudFront",
                "reglas_cache": [
                    {"match": "/static/*", "ttl": 86400, "nivel": "agresivo"},
                    {"match": "/api/*", "ttl": 0, "nivel": "bypass"},
                    {"match": "/*.html", "ttl": 3600, "nivel": "estandar"},
                    {"match": "/images/*", "ttl": 604800, "nivel": "agresivo"},
                ],
                "seguridad": {
                    "ssl": "full_strict",
                    "min_tls": "1.2",
                    "forzar_https": True,
                },
            },
            "vercel": {
                "proveedor": "Vercel Edge Network",
                "soberania": "Alternativa: Cloudflare o AWS CloudFront",
                "headers": [
                    {
                        "source": "/static/(.*)",
                        "headers": [{"key": "Cache-Control", "value": "public, max-age=86400, immutable"}],
                    },
                    {"source": "/api/(.*)", "headers": [{"key": "Cache-Control", "value": "no-store"}]},
                ],
            },
        }
        return configs.get(proveedor, configs["cloudflare"])

    def generar_optimizacion_db(self, patron: PatronBaseDatos) -> dict:
        """
        Generar recomendaciones de optimización de base de datos.

        Args:
            patron: PatronBaseDatos seleccionado según escala.

        Returns:
            Dict con recomendaciones específicas para el patrón.
        """
        optimizaciones = {
            PatronBaseDatos.SIMPLE: {
                "indices": "Agregar índices en columnas frecuentemente consultadas",
                "connection_pool": "Usar connection pooling (min=5, max=20)",
                "queries": "Evitar N+1 queries — usar JOINs o batch fetching",
                "monitoreo": "Rastrear queries lentas (>100ms)",
                "soberania": "asyncpg para async → alternativa: psycopg3",
            },
            PatronBaseDatos.REPLICAS_LECTURA: {
                "arquitectura": "Primary para escrituras, réplicas para lecturas",
                "routing": "Rutear queries de lectura a réplicas automáticamente",
                "lag_monitoreo": "Monitorear replication lag (<1s aceptable)",
                "failover": "Failover automático si primary cae",
                "soberania": "Supabase read replicas → alternativa: PgBouncer + PostgreSQL",
            },
            PatronBaseDatos.CQRS: {
                "arquitectura": "Modelos separados de lectura y escritura",
                "event_sourcing": "Considerar event sourcing para audit trail",
                "consistencia_eventual": "Aceptar consistencia eventual para lecturas",
                "proyecciones": "Construir proyecciones de lectura optimizadas",
                "soberania": "EventStoreDB → alternativa: PostgreSQL + triggers",
            },
            PatronBaseDatos.SHARDING: {
                "estrategia": "Hash-based sharding en user_id o tenant_id",
                "routing": "Capa de routing shard-aware",
                "rebalanceo": "Planear rebalanceo de shards conforme crece la data",
                "cross_shard": "Minimizar queries cross-shard",
                "soberania": "Citus (PostgreSQL) → alternativa: sharding manual con múltiples DBs",
            },
        }
        return optimizaciones.get(patron, optimizaciones[PatronBaseDatos.SIMPLE])

    def to_dict(self) -> dict:
        """
        Serializar estado del ScalabilityLayer para el Command Center.

        Returns:
            Dict con estado actual consumible por el Command Center.
        """
        return {
            "componente": "scalability_layer",
            "version": "58.2",
            "umbrales_usuarios": list(self.UMBRALES_USUARIOS.keys()),
            "estrategias_caching_soportadas": [e.value for e in EstrategiaCaching],
            "patrones_escalamiento_soportados": [p.value for p in PatronEscalamiento],
            "patrones_db_soportados": [p.value for p in PatronBaseDatos],
            "estado": "activo",
        }


# ─── Singleton factory ────────────────────────────────────────────────────────

_scalability_layer_instance: Optional[ScalabilityLayer] = None


def get_scalability_layer(redis_client=None) -> ScalabilityLayer:
    """
    Obtener instancia singleton del ScalabilityLayer.

    Args:
        redis_client: Cliente Redis opcional (upstash-redis o redis-py).

    Returns:
        Instancia única de ScalabilityLayer.
    """
    global _scalability_layer_instance
    if _scalability_layer_instance is None:
        _scalability_layer_instance = ScalabilityLayer(redis_client=redis_client)
    return _scalability_layer_instance
