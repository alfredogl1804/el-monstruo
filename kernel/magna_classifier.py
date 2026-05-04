"""
El Monstruo — Magna Classifier (Sprint 81, Capa 0.2)
=====================================================
Clasifica cada input del Embrión para decidir si merece la ruta completa
del grafo (con tools) o la ruta barata del router (chat-only).

El Embrión tiene dos rutas en `_think()`:
  - `_think_with_graph()` → LangGraph completo con 9+ tools activas
  - `_think_with_router()` → chat directo, sin tools, barato

Hoy el 95% de los latidos autónomos van por router porque la decisión
se basa en el tipo de trigger, no en el contenido. El Magna Classifier
resuelve esto: analiza el contenido y decide la ruta óptima.

Versión 1: Solo reglas (regex + keywords). Sin LLM.
Versión 2 (futura): LLM ligero (Haiku/Flash) para casos ambiguos.

Tabla de soporte: `magna_cache` en Supabase (migración 012).

Brand Compliance:
  - Naming: MagnaClassifier, ClassificationResult — cero genéricos
  - Excepciones: MagnaClasificacionFallida, MagnaCacheVencido
  - Logs: magna_classified, magna_route_decided, magna_cache_hit/miss
  - Endpoint: POST /v1/magna/classify (en magna_routes.py)
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

import structlog

from kernel.utils.keyword_matcher import (
    compile_keyword_pattern,
    count_keyword_matches,
    match_any_keyword,
)

logger = structlog.get_logger("magna_classifier")

# ── Constantes ──────────────────────────────────────────────────────

# Threshold para decidir ruta. Score >= THRESHOLD → graph. < THRESHOLD → router.
DEFAULT_THRESHOLD = 0.6

# Cap diario de llamadas al grafo desde el Embrión (Cruz Detractora #1)
DEFAULT_GRAPH_CALLS_PER_DAY = 30

# TTL por categoría (en segundos)
TTL_API_FRAMEWORKS = 86400     # 24h — APIs, SDKs, frameworks
TTL_PRECIOS = 3600             # 1h  — precios, cotizaciones, tipos de cambio
TTL_TRENDING = 21600           # 6h  — trending tech, noticias

# Tabla en Supabase
CACHE_TABLE = "magna_cache"


# ── Enums y Dataclasses ─────────────────────────────────────────────

class RouteType(str, Enum):
    """Ruta que el Embrión debe tomar."""
    GRAPH = "graph"              # Grafo completo con tools
    ROUTER = "router"            # Chat directo, sin tools
    TOOL_SPECIFIC = "tool_specific"  # Atajo: tool específica con alta confianza


class ContentCategory(str, Enum):
    """Categoría del contenido clasificado."""
    TECH = "tech"                # Dato técnico que cambia (APIs, versiones, etc.)
    ACTION = "action"            # Solicitud de acción ejecutable
    REFLECTION = "reflection"    # Reflexión, análisis, consolidación
    QUERY_REALTIME = "query_realtime"  # Pregunta que requiere datos en tiempo real
    UNKNOWN = "unknown"          # No clasificable con reglas


@dataclass
class ClassificationResult:
    """Resultado de clasificar un input del Embrión.

    Attributes:
        route: Ruta recomendada (graph, router, tool_specific).
        score: Confianza de la clasificación (0.0 a 1.0).
        category: Categoría del contenido.
        suggested_tool: Tool específica si route == tool_specific.
        reasoning: Explicación breve de por qué se eligió esta ruta.
        cached: Si el resultado vino del cache.
        ttl_seconds: TTL aplicado si se cachea.
    """
    route: RouteType
    score: float
    category: ContentCategory
    suggested_tool: Optional[str] = None
    reasoning: str = ""
    cached: bool = False
    ttl_seconds: int = TTL_API_FRAMEWORKS

    def to_dict(self) -> dict[str, Any]:
        """Serializar para API y cache."""
        return {
            "route": self.route.value,
            "score": round(self.score, 3),
            "category": self.category.value,
            "suggested_tool": self.suggested_tool,
            "reasoning": self.reasoning,
            "cached": self.cached,
            "ttl_seconds": self.ttl_seconds,
        }


# ── Excepciones con identidad ──────────────────────────────────────

class MagnaClasificacionFallida(Exception):
    """El clasificador no pudo procesar el input.

    Attributes:
        causa: Descripción técnica del fallo.
        sugerencia: Acción recomendada para el operador.
    """
    def __init__(self, causa: str, sugerencia: str = "Verificar input y reintentar"):
        self.causa = causa
        self.sugerencia = sugerencia
        super().__init__(f"magna_clasificacion_fallida: {causa} — {sugerencia}")


class MagnaCacheVencido(Exception):
    """Una entrada del cache expiró y necesita refresh.

    Attributes:
        cache_key: Key del cache expirado.
        ttl: TTL original en segundos.
    """
    def __init__(self, cache_key: str, ttl: int):
        self.cache_key = cache_key
        self.ttl = ttl
        super().__init__(f"magna_cache_vencido: key={cache_key}, ttl={ttl}s")


# ── Vocabularios de clasificación ───────────────────────────────────

# Palabras que indican contenido técnico/volátil (requiere graph + tools)
TECH_TRIGGERS: set[str] = {
    # Infraestructura y desarrollo
    "api", "sdk", "framework", "library", "version", "release",
    "deploy", "endpoint", "schema", "migration", "package",
    "docker", "kubernetes", "railway", "vercel", "supabase",
    "postgres", "redis", "nginx", "cloudflare",
    # IA y modelos
    "model", "llm", "agent", "tool", "mcp", "embedding",
    "openai", "anthropic", "gemini", "claude", "gpt",
    "langchain", "langgraph", "langsmith",
    # Datos en tiempo real
    "precio", "cotización", "tipo de cambio", "pricing",
    "noticia", "actual", "hoy", "última", "reciente",
    "trending", "tendencia", "mercado",
    # Código específico
    "bug", "error", "fix", "patch", "commit", "pull request",
    "test", "lint", "build", "pipeline", "ci/cd",
}

# Palabras que indican solicitud de acción (requiere graph + tools)
ACTION_TRIGGERS: set[str] = {
    # Español
    "busca", "investiga", "consulta", "delega", "ejecuta",
    "crea", "lanza", "publica", "envía", "verifica", "agenda",
    "despliega", "instala", "configura", "actualiza", "repara",
    "analiza datos", "genera reporte", "escanea",
    # Inglés
    "search", "query", "fetch", "run", "deploy", "send",
    "create", "launch", "publish", "install", "configure",
    "scan", "monitor", "check",
}

# Palabras que indican reflexión pura (ruta router, sin tools)
REFLECTION_TRIGGERS: set[str] = {
    "reflexiona", "considera", "piensa", "evalúa",
    "qué opinas", "cómo te sientes", "consolida", "resume",
    "medita", "pondera", "sopesa", "contempla",
    "silencio activo", "sin acción concreta",
    "doctrina", "filosofía", "principio",
}

# Mapeo de keywords a tools específicas (para route == tool_specific)
TOOL_KEYWORD_MAP: dict[str, str] = {
    "busca en web": "web_search",
    "busca en internet": "web_search",
    "search the web": "web_search",
    "investiga a fondo": "wide_research",
    "investigación profunda": "wide_research",
    "deep research": "wide_research",
    "delega a manus": "delegate_task",
    "manus haz": "delegate_task",
    "consulta a los sabios": "consult_sabios",
    "pregunta a los sabios": "consult_sabios",
    "crea en github": "github",
    "push to github": "github",
    "commit": "github",
    "envía email": "email",
    "send email": "email",
    "agenda tarea": "schedule_task",
    "programa tarea": "schedule_task",
    "ejecuta código": "code_exec",
    "run code": "code_exec",
    "notion": "notion",
}

# Patrones regex para detección de contenido técnico
RE_URL = re.compile(r"https?://\S+", re.IGNORECASE)
RE_CODE_BLOCK = re.compile(r"```[\s\S]*?```")
RE_FILE_PATH = re.compile(r"[\w/\\]+\.\w{1,10}")
RE_VERSION = re.compile(r"v?\d+\.\d+(?:\.\d+)?")
RE_ENV_VAR = re.compile(r"[A-Z][A-Z_]{2,}=")
RE_JSON_LIKE = re.compile(r"\{[^}]*:[^}]*\}")

# Sprint 84.7: Patterns precompilados con word boundaries (anti substring matching)
_TECH_PATTERN = compile_keyword_pattern(TECH_TRIGGERS)
_ACTION_PATTERN = compile_keyword_pattern(ACTION_TRIGGERS)
_REFLECTION_PATTERN = compile_keyword_pattern(REFLECTION_TRIGGERS)
_PRECIO_PATTERN = compile_keyword_pattern(
    ("precio", "cotización", "tipo de cambio", "pricing")
)
_TRENDING_PATTERN = compile_keyword_pattern(
    ("trending", "tendencia", "noticia", "hoy")
)


# ── Clase Principal ─────────────────────────────────────────────────

class MagnaClassifier:
    """Clasifica inputs del Embrión para decidir la ruta óptima.

    Versión 1: Solo reglas (regex + keywords). Sin LLM.
    El clasificador es determinístico y rápido (<1ms por clasificación).

    Args:
        db: SupabaseClient para cache persistente (opcional).
        threshold: Score mínimo para elegir ruta graph (default 0.6).
        graph_calls_per_day: Cap diario de llamadas al grafo (default 30).
        use_cache: Habilitar cache en Supabase (default True si db disponible).

    Example:
        >>> classifier = MagnaClassifier(db=supabase_client)
        >>> result = classifier.classify("Busca el precio actual de Bitcoin")
        >>> result.route  # RouteType.GRAPH
        >>> result.category  # ContentCategory.QUERY_REALTIME
        >>> result.suggested_tool  # "web_search"
    """

    def __init__(
        self,
        db=None,
        threshold: float = DEFAULT_THRESHOLD,
        graph_calls_per_day: int = DEFAULT_GRAPH_CALLS_PER_DAY,
        use_cache: bool = True,
    ):
        self._db = db
        self._threshold = threshold
        self._graph_calls_per_day = graph_calls_per_day
        self._use_cache = use_cache and db is not None

        # Contadores en memoria (reset diario)
        self._graph_calls_today = 0
        self._total_classifications = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._last_reset_date: Optional[str] = None

        # Cache en memoria (fallback si no hay DB)
        self._memory_cache: dict[str, tuple[ClassificationResult, float]] = {}
        self._MEMORY_CACHE_MAX = 500

        logger.info(
            "magna_classifier_initialized",
            threshold=threshold,
            graph_cap=graph_calls_per_day,
            cache_enabled=self._use_cache,
        )

    # ── API Pública ─────────────────────────────────────────────────

    def classify(self, text: str, context: Optional[dict] = None) -> ClassificationResult:
        """Clasifica un input y devuelve la ruta recomendada.

        Args:
            text: Texto a clasificar (prompt del Embrión, mensaje de usuario, etc.)
            context: Contexto adicional (trigger_type, cycle, etc.)

        Returns:
            ClassificationResult con route, score, category, suggested_tool.

        Raises:
            MagnaClasificacionFallida: Si el input es vacío o inválido.
        """
        if not text or not text.strip():
            raise MagnaClasificacionFallida(
                causa="Input vacío o solo espacios",
                sugerencia="Verificar que el prompt del Embrión no esté vacío",
            )

        self._maybe_reset_daily_counters()
        self._total_classifications += 1

        text_lower = text.lower().strip()
        context = context or {}

        # 1. Check cache (memoria primero, luego DB)
        cache_key = self._make_cache_key(text_lower)
        cached = self._check_cache(cache_key)
        if cached:
            self._cache_hits += 1
            logger.info(
                "magna_cache_hit",
                cache_key=cache_key[:16],
                route=cached.route.value,
            )
            return cached

        self._cache_misses += 1

        # 2. Clasificar por reglas
        result = self._classify_by_rules(text_lower, text, context)

        # 3. Aplicar cap diario de graph calls
        if result.route in (RouteType.GRAPH, RouteType.TOOL_SPECIFIC):
            if self._graph_calls_today >= self._graph_calls_per_day:
                logger.warning(
                    "magna_graph_cap_reached",
                    cap=self._graph_calls_per_day,
                    today_count=self._graph_calls_today,
                    original_route=result.route.value,
                )
                result = ClassificationResult(
                    route=RouteType.ROUTER,
                    score=result.score,
                    category=result.category,
                    reasoning=f"Cap diario alcanzado ({self._graph_calls_per_day}). "
                              f"Ruta original: {result.route.value}. Degradando a router.",
                    ttl_seconds=0,  # No cachear decisiones de cap
                )
            else:
                self._graph_calls_today += 1

        # 4. Guardar en cache
        if result.ttl_seconds > 0:
            self._store_cache(cache_key, result, text_lower)

        logger.info(
            "magna_classified",
            route=result.route.value,
            score=result.score,
            category=result.category.value,
            suggested_tool=result.suggested_tool,
            graph_calls_today=self._graph_calls_today,
            total_classifications=self._total_classifications,
        )

        return result

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas del clasificador para el Command Center.

        Returns:
            Dict con contadores, tasas, y estado del cap.
        """
        total = self._total_classifications or 1
        return {
            "total_classifications": self._total_classifications,
            "graph_calls_today": self._graph_calls_today,
            "graph_calls_cap": self._graph_calls_per_day,
            "graph_calls_remaining": max(0, self._graph_calls_per_day - self._graph_calls_today),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": round(self._cache_hits / total, 3) if total > 0 else 0,
            "threshold": self._threshold,
            "memory_cache_size": len(self._memory_cache),
            "last_reset_date": self._last_reset_date,
        }

    def reset_daily_counters(self) -> None:
        """Reset manual de contadores diarios (para testing o emergencias)."""
        self._graph_calls_today = 0
        self._last_reset_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        logger.info("magna_daily_counters_reset", date=self._last_reset_date)

    # ── Clasificación por Reglas ────────────────────────────────────

    def _classify_by_rules(
        self, text_lower: str, text_original: str, context: dict
    ) -> ClassificationResult:
        """Motor de clasificación basado en reglas determinísticas.

        Evalúa el texto contra tres vocabularios (tech, action, reflection)
        y patrones regex. El score es proporcional a la cantidad de señales.

        Args:
            text_lower: Texto normalizado a minúsculas.
            text_original: Texto original sin normalizar.
            context: Contexto adicional del trigger.

        Returns:
            ClassificationResult con la ruta decidida.
        """
        scores = {
            "tech": 0.0,
            "action": 0.0,
            "reflection": 0.0,
        }
        signals: list[str] = []
        suggested_tool: Optional[str] = None

        # ── Señales de contenido técnico ────────────────────────────
        # Sprint 84.7: word boundaries via _TECH_PATTERN
        tech_matches = count_keyword_matches(text_lower, _TECH_PATTERN)
        if tech_matches > 0:
            scores["tech"] += min(tech_matches * 0.15, 0.6)
            signals.append(f"tech_keywords={tech_matches}")

        # URLs
        if RE_URL.search(text_original):
            scores["tech"] += 0.2
            signals.append("contains_url")

        # Code blocks
        if RE_CODE_BLOCK.search(text_original):
            scores["tech"] += 0.15
            signals.append("contains_code_block")

        # File paths
        if RE_FILE_PATH.search(text_original):
            scores["tech"] += 0.1
            signals.append("contains_file_path")

        # Version numbers
        if RE_VERSION.search(text_original):
            scores["tech"] += 0.1
            signals.append("contains_version")

        # Environment variables
        if RE_ENV_VAR.search(text_original):
            scores["tech"] += 0.1
            signals.append("contains_env_var")

        # JSON-like structures
        if RE_JSON_LIKE.search(text_original):
            scores["tech"] += 0.1
            signals.append("contains_json")

        # ── Señales de acción ───────────────────────────────────────
        # Sprint 84.7: word boundaries via _ACTION_PATTERN
        action_matches = count_keyword_matches(text_lower, _ACTION_PATTERN)
        if action_matches > 0:
            scores["action"] += min(action_matches * 0.2, 0.7)
            signals.append(f"action_keywords={action_matches}")

        # Check for tool-specific keywords
        for keyword, tool in TOOL_KEYWORD_MAP.items():
            if keyword in text_lower:
                suggested_tool = tool
                scores["action"] += 0.3
                signals.append(f"tool_match={tool}")
                break

        # ── Señales de reflexión ────────────────────────────────────
        # Sprint 84.7: word boundaries via _REFLECTION_PATTERN
        reflection_matches = count_keyword_matches(text_lower, _REFLECTION_PATTERN)
        if reflection_matches > 0:
            scores["reflection"] += min(reflection_matches * 0.2, 0.7)
            signals.append(f"reflection_keywords={reflection_matches}")

        # "Silencio activo" es señal fuerte de reflexión
        if "silencio activo" in text_lower:
            scores["reflection"] += 0.4
            signals.append("silencio_activo")

        # ── Señales de contexto ─────────────────────────────────────
        trigger_type = context.get("trigger_type", "")
        if trigger_type == "mensaje_alfredo":
            # Mensajes directos de Alfredo siempre tienen peso extra hacia graph
            scores["action"] += 0.2
            signals.append("trigger=mensaje_alfredo")

        # ── Decidir ruta ────────────────────────────────────────────
        max_category = max(scores, key=scores.get)
        max_score = scores[max_category]

        # Normalizar score a 0-1
        combined_graph_score = scores["tech"] + scores["action"]
        combined_router_score = scores["reflection"]

        # Score final: cuánto "merece" el grafo
        if combined_graph_score + combined_router_score > 0:
            final_score = combined_graph_score / (combined_graph_score + combined_router_score)
        else:
            final_score = 0.3  # Default bajo si no hay señales

        # Determinar categoría
        if max_category == "tech":
            category = ContentCategory.TECH
        elif max_category == "action":
            category = ContentCategory.ACTION
        elif max_category == "reflection":
            category = ContentCategory.REFLECTION
        else:
            category = ContentCategory.UNKNOWN

        # Determinar TTL según categoría
        # Sprint 84.7: word boundaries via _PRECIO_PATTERN / _TRENDING_PATTERN
        if match_any_keyword(text_lower, _PRECIO_PATTERN):
            ttl = TTL_PRECIOS
            category = ContentCategory.QUERY_REALTIME
        elif match_any_keyword(text_lower, _TRENDING_PATTERN):
            ttl = TTL_TRENDING
        else:
            ttl = TTL_API_FRAMEWORKS

        # Decidir ruta
        if final_score >= self._threshold:
            if suggested_tool and final_score >= 0.75:
                route = RouteType.TOOL_SPECIFIC
                reasoning = (
                    f"Tool específica detectada: {suggested_tool}. "
                    f"Score={final_score:.2f}, señales: {', '.join(signals)}"
                )
            else:
                route = RouteType.GRAPH
                reasoning = (
                    f"Contenido requiere tools (score={final_score:.2f}). "
                    f"Categoría: {category.value}. Señales: {', '.join(signals)}"
                )
        else:
            route = RouteType.ROUTER
            reasoning = (
                f"Contenido es reflexión/chat (score={final_score:.2f}). "
                f"Señales: {', '.join(signals) or 'ninguna'}"
            )

        return ClassificationResult(
            route=route,
            score=final_score,
            category=category,
            suggested_tool=suggested_tool,
            reasoning=reasoning,
            cached=False,
            ttl_seconds=ttl,
        )

    # ── Cache ───────────────────────────────────────────────────────

    def _make_cache_key(self, text_lower: str) -> str:
        """Generar key determinística para el cache.

        Normaliza el texto (strip, lower, colapsar espacios) y hashea.
        """
        normalized = re.sub(r"\s+", " ", text_lower.strip())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:32]

    def _check_cache(self, cache_key: str) -> Optional[ClassificationResult]:
        """Buscar en cache (memoria primero, luego DB).

        Returns:
            ClassificationResult si hay hit válido, None si miss o expirado.
        """
        # 1. Cache en memoria
        if cache_key in self._memory_cache:
            result, expires_at = self._memory_cache[cache_key]
            if time.time() < expires_at:
                result.cached = True
                return result
            else:
                del self._memory_cache[cache_key]

        # 2. Cache en DB (async no disponible aquí — se maneja en magna_routes)
        # La consulta a DB se hace desde el endpoint, no desde classify()
        # para mantener classify() sincrónico y rápido.

        return None

    def _store_cache(
        self, cache_key: str, result: ClassificationResult, query: str
    ) -> None:
        """Guardar resultado en cache de memoria.

        El cache en DB (Supabase) se maneja desde magna_routes.py
        para mantener classify() sincrónico.
        """
        # Evict si estamos al límite
        if len(self._memory_cache) >= self._MEMORY_CACHE_MAX:
            # Eliminar el más viejo
            oldest_key = min(
                self._memory_cache,
                key=lambda k: self._memory_cache[k][1],
            )
            del self._memory_cache[oldest_key]

        expires_at = time.time() + result.ttl_seconds
        self._memory_cache[cache_key] = (result, expires_at)

    async def store_cache_db(
        self, cache_key: str, result: ClassificationResult, query: str
    ) -> None:
        """Persistir resultado en Supabase (async, llamado desde routes).

        Args:
            cache_key: Hash del query normalizado.
            result: Resultado de clasificación.
            query: Query original para referencia.
        """
        if not self._db or not self._use_cache:
            return

        try:
            expires_at = (
                datetime.now(timezone.utc) + timedelta(seconds=result.ttl_seconds)
            ).isoformat()

            await self._db.upsert(
                CACHE_TABLE,
                {
                    "cache_key": cache_key,
                    "tool_name": result.suggested_tool or "none",
                    "query": query[:500],
                    "result": result.to_dict(),
                    "ttl_seconds": result.ttl_seconds,
                    "expires_at": expires_at,
                },
                on_conflict="cache_key",
            )
            logger.debug("magna_cache_stored", cache_key=cache_key[:16])
        except Exception as e:
            logger.warning("magna_cache_store_failed", error=str(e))

    async def check_cache_db(self, cache_key: str) -> Optional[ClassificationResult]:
        """Consultar cache en Supabase (async, llamado desde routes).

        Args:
            cache_key: Hash del query normalizado.

        Returns:
            ClassificationResult si hay hit válido, None si miss.
        """
        if not self._db or not self._use_cache:
            return None

        try:
            rows = await self._db.select(
                CACHE_TABLE,
                columns="result,expires_at,hit_count",
                filters={"cache_key": cache_key},
                limit=1,
            )
            if not rows:
                return None

            row = rows[0]
            expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))

            if expires_at < datetime.now(timezone.utc):
                logger.debug("magna_cache_expired", cache_key=cache_key[:16])
                return None

            # Incrementar hit_count
            await self._db.update(
                CACHE_TABLE,
                {"hit_count": row.get("hit_count", 0) + 1, "last_hit_at": datetime.now(timezone.utc).isoformat()},
                {"cache_key": cache_key},
            )

            data = row["result"]
            return ClassificationResult(
                route=RouteType(data["route"]),
                score=data["score"],
                category=ContentCategory(data["category"]),
                suggested_tool=data.get("suggested_tool"),
                reasoning=data.get("reasoning", "from_cache"),
                cached=True,
                ttl_seconds=data.get("ttl_seconds", TTL_API_FRAMEWORKS),
            )
        except Exception as e:
            logger.warning("magna_cache_db_check_failed", error=str(e))
            return None

    async def cleanup_expired_cache(self) -> int:
        """Limpiar entradas expiradas del cache en Supabase.

        Returns:
            Número de entradas eliminadas (estimado).
        """
        if not self._db:
            return 0

        try:
            # Supabase client no tiene delete con lt() directo,
            # usamos RPC o select + delete
            now = datetime.now(timezone.utc).isoformat()
            expired = await self._db.select(
                CACHE_TABLE,
                columns="cache_key",
                filters={},
                limit=100,
            )
            # Filtrar expirados manualmente
            count = 0
            for row in expired:
                # Solo podemos filtrar por equality en el client simple
                # La limpieza real se haría con un cron SQL
                pass

            # Limpiar cache en memoria
            now_ts = time.time()
            expired_keys = [
                k for k, (_, exp) in self._memory_cache.items() if exp < now_ts
            ]
            for k in expired_keys:
                del self._memory_cache[k]

            logger.info("magna_cache_cleanup", memory_expired=len(expired_keys))
            return len(expired_keys)
        except Exception as e:
            logger.warning("magna_cache_cleanup_failed", error=str(e))
            return 0

    # ── Utilidades ──────────────────────────────────────────────────

    def _maybe_reset_daily_counters(self) -> None:
        """Reset automático de contadores al cambiar de día (UTC)."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._last_reset_date != today:
            self._graph_calls_today = 0
            self._last_reset_date = today
            logger.info("magna_daily_auto_reset", date=today)
