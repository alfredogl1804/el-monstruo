"""
El Catastro · Recommendation Engine (Sprint 86 Bloque 5).

Capa de lógica de recomendación pura, desacoplada de FastMCP/FastAPI.
Consume la vista `catastro_trono_view` (creada en migration 019) que ya
trae el ranking por dominio, las bandas de confianza y los datos
desnormalizados — cero JOIN necesario.

Doctrina (Cowork green light Bloque 5):
  · Filtra por dominio/macroarea opcionales; ordena por trono_global desc.
  · Top N con metadata: rank_dominio, trono_low/high, métricas, precios.
  · Filtros opcionales: estado=production, quorum_alcanzado=true.
  · Cache LRU 60 s para queries idénticas (reduce carga Supabase).
  · Modo degraded: si Supabase falla, retorna lista vacía con
    `degraded=True, reason="supabase_down"` — NUNCA crashea.

Disciplina obligatoria (AGENTS.md regla #4 Brand Engine):
  · Errores con identidad `catastro_recommend_*`.
  · Naming `recommend / get_modelo / list_dominios / status` consistente
    con la spec de Cowork (NO genéricos service/handler/utils).
  · Pydantic models con descripciones humanas para el dossier MCP.

Disciplina anti-Dory:
  · `os.environ.get(...)` en cada uso (no se cachea al boot).
  · `db_factory` inyectable para tests con mock (sin tocar Supabase real).
  · Cache invalidable explícitamente desde el cron (`invalidate_cache()`).

[Hilo Manus Catastro] · Sprint 86 Bloque 5 · 2026-05-04 · v0.86.5
"""
from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Constantes
# ============================================================================

CATASTRO_TRONO_VIEW = "catastro_trono_view"
CATASTRO_MODELOS_TABLE = "catastro_modelos"
CATASTRO_EVENTOS_TABLE = "catastro_eventos"

DEFAULT_TOP_N = 3
MAX_TOP_N = 25  # safeguard para no traer toda la BD por accidente

DEFAULT_CACHE_TTL_SECONDS = 60
DEFAULT_CACHE_MAX_ENTRIES = 256

DEGRADED_REASON_NO_DB = "no_db_factory_configured"
DEGRADED_REASON_SUPABASE_DOWN = "supabase_down"
DEGRADED_REASON_NO_DATA = "no_models_match_filters"


# ============================================================================
# Errores con identidad de marca (catastro_recommend_*)
# ============================================================================


class CatastroRecommendError(Exception):
    """Error base del recommender. Identidad de marca: catastro_recommend_*."""

    code: str = "catastro_recommend_error"

    def __init__(self, message: str, **context: Any) -> None:
        super().__init__(message)
        self.context = context


class CatastroRecommendInvalidArgs(CatastroRecommendError):
    """Argumentos de entrada inválidos (top_n fuera de rango, etc.)."""

    code = "catastro_recommend_invalid_args"


class CatastroRecommendModeloNotFound(CatastroRecommendError):
    """get_modelo() no encontró el id solicitado."""

    code = "catastro_recommend_modelo_not_found"


# ============================================================================
# Pydantic models — JSON-serializable directo para MCP
# ============================================================================


class ModeloRecomendado(BaseModel):
    """Vista compacta de un modelo recomendado para un dominio dado."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., description="Identificador canónico del modelo")
    nombre: str = Field(..., description="Nombre humano del modelo")
    proveedor: str = Field(..., description="Proveedor del modelo (anthropic, openai, ...)")
    macroarea: Optional[str] = Field(None, description="Macroárea del Catastro (Inteligencia/Visión/Agentes)")
    dominio: str = Field(..., description="Dominio en el que se recomienda este modelo")

    trono_global: float = Field(..., description="Trono Score [0,100] dentro del dominio")
    trono_delta: Optional[float] = Field(None, description="Cambio respecto al cálculo previo")
    trono_low: float = Field(..., description="Banda inferior de confianza")
    trono_high: float = Field(..., description="Banda superior de confianza")
    rank_dominio: int = Field(..., description="Posición en el ranking del dominio (1=top)")

    quality_score: Optional[float] = None
    cost_efficiency: Optional[float] = None
    speed_score: Optional[float] = None
    reliability_score: Optional[float] = None
    brand_fit: Optional[float] = None
    confidence: Optional[float] = None

    precio_input_per_million: Optional[float] = None
    precio_output_per_million: Optional[float] = None
    open_weights: bool = False

    last_validated_at: Optional[datetime] = None


class ModeloDetallado(ModeloRecomendado):
    """Vista detallada para get_modelo: agrega subcapacidades, sovereignty, velocity."""

    subcapacidades: Optional[list[str]] = None
    sovereignty: Optional[float] = None
    velocity: Optional[float] = None
    estado: Optional[str] = None


class DominioInfo(BaseModel):
    """Dominio + cuántos modelos lo cubren + macroárea de pertenencia."""

    dominio: str
    macroarea: Optional[str] = None
    modelos_count: int


class StatusSnapshot(BaseModel):
    """Snapshot del Catastro: salud + métricas operativas."""

    trust_level: str = Field(..., description='"healthy" | "degraded" | "down"')
    last_update: Optional[datetime] = None
    modelos_count: int = 0
    dominios_count: int = 0
    macroareas: list[str] = Field(default_factory=list)
    cache_entries: int = 0
    degraded: bool = False
    degraded_reason: Optional[str] = None
    queried_at: datetime


class RecommendationResponse(BaseModel):
    """Respuesta canónica de catastro.recommend()."""

    use_case: str
    dominio_consultado: Optional[str]
    macroarea_consultada: Optional[str]
    top_n: int
    modelos: list[ModeloRecomendado]
    degraded: bool = False
    degraded_reason: Optional[str] = None
    cache_hit: bool = False
    generated_at: datetime


class ListDominiosResponse(BaseModel):
    """Respuesta canónica de catastro.list_dominios()."""

    macroareas: dict[str, list[DominioInfo]]
    total_dominios: int
    degraded: bool = False
    degraded_reason: Optional[str] = None
    queried_at: datetime


# ============================================================================
# Cache LRU con TTL — minimal, sin dependencias externas
# ============================================================================


@dataclass
class _CacheEntry:
    value: Any
    expires_at: float


class _LRUTTLCache:
    """Cache LRU con TTL absoluto. Thread-safe básico (RLock)."""

    def __init__(self, max_entries: int, ttl_seconds: int) -> None:
        self._max = int(max_entries)
        self._ttl = int(ttl_seconds)
        self._lock = threading.RLock()
        self._store: dict[Any, _CacheEntry] = {}

    def get(self, key: Any) -> Optional[Any]:
        now = time.time()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.expires_at < now:
                self._store.pop(key, None)
                return None
            # LRU: re-insert para mover al final
            self._store.pop(key)
            self._store[key] = entry
            return entry.value

    def set(self, key: Any, value: Any) -> None:
        with self._lock:
            if key in self._store:
                self._store.pop(key)
            self._store[key] = _CacheEntry(
                value=value,
                expires_at=time.time() + self._ttl,
            )
            while len(self._store) > self._max:
                # FIFO: pop más viejo
                oldest_key = next(iter(self._store))
                self._store.pop(oldest_key)

    def invalidate(self) -> int:
        with self._lock:
            n = len(self._store)
            self._store.clear()
            return n

    def size(self) -> int:
        with self._lock:
            return len(self._store)


# ============================================================================
# RecommendationEngine
# ============================================================================


class RecommendationEngine:
    """
    Motor puro de recomendación. Sin acoplamiento a FastMCP/FastAPI.

    Args:
        db_factory: callable que retorna un cliente Supabase SÍNCRONO
            (mismo patrón que CatastroPersistence). Si es None, el engine
            entra en modo degraded automáticamente.
        cache_ttl_seconds: TTL del cache LRU en segundos (default 60).
        cache_max_entries: tamaño máximo del cache LRU (default 256).

    Patrones de uso:
        engine = RecommendationEngine(db_factory=lambda: supabase_client())
        resp = engine.recommend(use_case="razonamiento legal LATAM",
                                dominio="llm_frontier", top_n=3)
        for m in resp.modelos: print(m.nombre, m.trono_global)
    """

    def __init__(
        self,
        db_factory: Optional[Callable[[], Any]] = None,
        *,
        cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
        cache_max_entries: int = DEFAULT_CACHE_MAX_ENTRIES,
    ) -> None:
        self.db_factory = db_factory
        self._cache = _LRUTTLCache(cache_max_entries, cache_ttl_seconds)

    # ------------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------------

    def recommend(
        self,
        *,
        use_case: str,
        dominio: Optional[str] = None,
        macroarea: Optional[str] = None,
        top_n: int = DEFAULT_TOP_N,
        estado: str = "production",
        only_quorum: bool = False,
    ) -> RecommendationResponse:
        """
        Devuelve los Top N modelos recomendados para `use_case`.

        Args:
            use_case: descripción del caso de uso (texto libre, audit-only).
            dominio: si se especifica, solo modelos de ese dominio.
            macroarea: si se especifica, solo modelos de esa macroárea.
            top_n: cuántos modelos retornar (clamped a [1, MAX_TOP_N]).
            estado: filtra por catastro_modelos.estado (default 'production').
            only_quorum: si True, futuro filtro por quorum_alcanzado.

        Returns:
            RecommendationResponse — siempre. Modo degraded si la DB falla.
        """
        if not use_case or not use_case.strip():
            raise CatastroRecommendInvalidArgs(
                "use_case no puede ser vacío",
                use_case=use_case,
            )
        top_n_clamped = max(1, min(int(top_n), MAX_TOP_N))

        cache_key = (
            "recommend",
            use_case.strip().lower(),
            dominio,
            macroarea,
            top_n_clamped,
            estado,
            bool(only_quorum),
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached.model_copy(update={"cache_hit": True})

        modelos, degraded_reason = self._fetch_recommend_rows(
            dominio=dominio,
            macroarea=macroarea,
            top_n=top_n_clamped,
            estado=estado,
        )
        response = RecommendationResponse(
            use_case=use_case,
            dominio_consultado=dominio,
            macroarea_consultada=macroarea,
            top_n=top_n_clamped,
            modelos=modelos,
            degraded=degraded_reason is not None,
            degraded_reason=degraded_reason,
            cache_hit=False,
            generated_at=datetime.now(timezone.utc),
        )
        # Solo cacheamos respuestas no-degraded (sino servimos basura)
        if not response.degraded and response.modelos:
            self._cache.set(cache_key, response)
        return response

    def get_modelo(self, modelo_id: str) -> Optional[ModeloDetallado]:
        """
        Recupera la ficha detallada de un modelo por id canónico.

        Returns:
            ModeloDetallado o None si no existe / DB caída.
        """
        if not modelo_id or not modelo_id.strip():
            raise CatastroRecommendInvalidArgs(
                "modelo_id no puede ser vacío",
                modelo_id=modelo_id,
            )
        client = self._client_or_none()
        if client is None:
            return None
        try:
            res = (
                client.table(CATASTRO_MODELOS_TABLE)
                .select("*")
                .eq("id", modelo_id.strip())
                .limit(1)
                .execute()
            )
            data = getattr(res, "data", None) or []
            if not data:
                return None
            row = data[0]
            return ModeloDetallado(
                id=row.get("id"),
                nombre=row.get("nombre"),
                proveedor=row.get("proveedor"),
                macroarea=row.get("macroarea"),
                dominio=(row.get("dominios") or [""])[0],
                trono_global=float(row.get("trono_global") or 50.0),
                trono_delta=row.get("trono_delta"),
                trono_low=float(row.get("trono_global") or 50.0),
                trono_high=float(row.get("trono_global") or 50.0),
                rank_dominio=0,  # rank no aplica para vista detallada
                quality_score=row.get("quality_score"),
                cost_efficiency=row.get("cost_efficiency"),
                speed_score=row.get("speed_score"),
                reliability_score=row.get("reliability_score"),
                brand_fit=row.get("brand_fit"),
                confidence=row.get("confidence"),
                precio_input_per_million=row.get("precio_input_per_million"),
                precio_output_per_million=row.get("precio_output_per_million"),
                open_weights=bool(row.get("open_weights") or False),
                last_validated_at=_parse_dt(row.get("ultima_validacion") or row.get("last_validated_at")),
                subcapacidades=row.get("subcapacidades"),
                sovereignty=row.get("sovereignty"),
                velocity=row.get("velocity"),
                estado=row.get("estado"),
            )
        except Exception:
            return None

    def list_dominios(self) -> ListDominiosResponse:
        """
        Lista todos los dominios agrupados por macroárea con conteo.
        """
        client = self._client_or_none()
        if client is None:
            return ListDominiosResponse(
                macroareas={},
                total_dominios=0,
                degraded=True,
                degraded_reason=DEGRADED_REASON_NO_DB,
                queried_at=datetime.now(timezone.utc),
            )
        try:
            res = (
                client.table(CATASTRO_MODELOS_TABLE)
                .select("macroarea,dominios")
                .neq("estado", "deprecated")
                .execute()
            )
            rows = getattr(res, "data", None) or []
        except Exception:
            return ListDominiosResponse(
                macroareas={},
                total_dominios=0,
                degraded=True,
                degraded_reason=DEGRADED_REASON_SUPABASE_DOWN,
                queried_at=datetime.now(timezone.utc),
            )

        # Agrupar
        # macroareas[macroarea] -> dict[dominio -> count]
        agg: dict[str, dict[str, int]] = {}
        for r in rows:
            ma = r.get("macroarea") or "sin_macroarea"
            agg.setdefault(ma, {})
            for d in (r.get("dominios") or []):
                agg[ma][d] = agg[ma].get(d, 0) + 1

        macroareas_out: dict[str, list[DominioInfo]] = {}
        total = 0
        for ma in sorted(agg.keys()):
            lst = []
            for dom in sorted(agg[ma].keys()):
                lst.append(DominioInfo(
                    dominio=dom, macroarea=ma, modelos_count=agg[ma][dom]
                ))
                total += 1
            macroareas_out[ma] = lst

        return ListDominiosResponse(
            macroareas=macroareas_out,
            total_dominios=total,
            degraded=False,
            queried_at=datetime.now(timezone.utc),
        )

    def status(self) -> StatusSnapshot:
        """
        Snapshot operativo del Catastro: salud + conteos.
        """
        now = datetime.now(timezone.utc)
        client = self._client_or_none()
        if client is None:
            return StatusSnapshot(
                trust_level="down",
                modelos_count=0,
                dominios_count=0,
                macroareas=[],
                cache_entries=self._cache.size(),
                degraded=True,
                degraded_reason=DEGRADED_REASON_NO_DB,
                queried_at=now,
            )
        try:
            res = (
                client.table(CATASTRO_MODELOS_TABLE)
                .select("macroarea,dominios,ultima_validacion")
                .neq("estado", "deprecated")
                .execute()
            )
            rows = getattr(res, "data", None) or []
        except Exception:
            return StatusSnapshot(
                trust_level="degraded",
                modelos_count=0,
                dominios_count=0,
                macroareas=[],
                cache_entries=self._cache.size(),
                degraded=True,
                degraded_reason=DEGRADED_REASON_SUPABASE_DOWN,
                queried_at=now,
            )

        macroareas: set[str] = set()
        dominios: set[str] = set()
        last_update: Optional[datetime] = None
        for r in rows:
            if r.get("macroarea"):
                macroareas.add(r["macroarea"])
            for d in (r.get("dominios") or []):
                dominios.add(d)
            ts = _parse_dt(r.get("ultima_validacion") or r.get("last_validated_at"))
            if ts and (last_update is None or ts > last_update):
                last_update = ts

        return StatusSnapshot(
            trust_level="healthy" if rows else "degraded",
            last_update=last_update,
            modelos_count=len(rows),
            dominios_count=len(dominios),
            macroareas=sorted(macroareas),
            cache_entries=self._cache.size(),
            degraded=not bool(rows),
            degraded_reason=None if rows else DEGRADED_REASON_NO_DATA,
            queried_at=now,
        )

    def invalidate_cache(self) -> int:
        """Vacía el cache LRU. Retorna el número de entries flusheados."""
        return self._cache.invalidate()

    # ------------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------------

    def _client_or_none(self) -> Optional[Any]:
        """Construye el cliente lazy. Retorna None si no se puede."""
        if self.db_factory is None:
            return None
        try:
            return self.db_factory()
        except Exception:
            return None

    def _fetch_recommend_rows(
        self,
        *,
        dominio: Optional[str],
        macroarea: Optional[str],
        top_n: int,
        estado: str,
    ) -> tuple[list[ModeloRecomendado], Optional[str]]:
        """
        Query a la vista catastro_trono_view con filtros.

        Returns:
            (modelos, degraded_reason). Si degraded_reason no es None, modelos=[].
        """
        client = self._client_or_none()
        if client is None:
            return [], DEGRADED_REASON_NO_DB
        try:
            q = (
                client.table(CATASTRO_TRONO_VIEW)
                .select("*")
            )
            if dominio:
                q = q.eq("dominio", dominio)
            if macroarea:
                q = q.eq("macroarea", macroarea)
            if estado:
                q = q.eq("estado", estado)
            # Trono desc; rank_dominio asc como tiebreaker
            q = q.order("trono_global", desc=True).order("rank_dominio", desc=False)
            q = q.limit(top_n)
            res = q.execute()
            rows = getattr(res, "data", None) or []
        except Exception:
            return [], DEGRADED_REASON_SUPABASE_DOWN

        if not rows:
            return [], DEGRADED_REASON_NO_DATA

        out: list[ModeloRecomendado] = []
        for r in rows:
            try:
                out.append(ModeloRecomendado(
                    id=r["id"],
                    nombre=r.get("nombre", r["id"]),
                    proveedor=r.get("proveedor", "unknown"),
                    macroarea=r.get("macroarea"),
                    dominio=r.get("dominio", dominio or ""),
                    trono_global=float(r.get("trono_global") or 50.0),
                    trono_delta=r.get("trono_delta"),
                    trono_low=float(r.get("trono_low") or 0.0),
                    trono_high=float(r.get("trono_high") or 100.0),
                    rank_dominio=int(r.get("rank_dominio") or 0),
                    quality_score=r.get("quality_score"),
                    cost_efficiency=r.get("cost_efficiency"),
                    speed_score=r.get("speed_score"),
                    reliability_score=r.get("reliability_score"),
                    brand_fit=r.get("brand_fit"),
                    confidence=r.get("confidence"),
                    precio_input_per_million=r.get("precio_input_per_million"),
                    precio_output_per_million=r.get("precio_output_per_million"),
                    open_weights=bool(r.get("open_weights") or False),
                    last_validated_at=_parse_dt(r.get("ultima_validacion") or r.get("last_validated_at")),
                ))
            except Exception:
                # Fila corrupta — skip silencioso, no rompemos el batch
                continue

        return out, None


# ============================================================================
# Helpers
# ============================================================================


def _parse_dt(value: Any) -> Optional[datetime]:
    """Parser tolerante: acepta None, datetime, ISO string, epoch."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            # Soporta '2026-05-04T20:00:00Z' y variantes
            v = value.replace("Z", "+00:00") if value.endswith("Z") else value
            return datetime.fromisoformat(v)
        except Exception:
            return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except Exception:
            return None
    return None


def build_default_db_factory() -> Optional[Callable[[], Any]]:
    """
    Construye un db_factory por defecto que lee SUPABASE_URL +
    service-role key del entorno (lazy, no cacheado).

    Acepta dos convenciones de naming para la service-role key (Sprint 86.4.5
    Bloque 1 fix: Railway prod usa la convención histórica del repo,
    mientras la doc oficial de Supabase usa la convención con `_ROLE_`):
      1. SUPABASE_SERVICE_ROLE_KEY  (oficial Supabase, preferida)
      2. SUPABASE_SERVICE_KEY       (histórica del repo, fallback)
    Si ambas están seteadas, gana la oficial. Si ninguna, error claro.

    Returns:
        Callable que construye client al invocarse. None si no hay env vars.
    """
    def _factory() -> Any:
        url = os.environ.get("SUPABASE_URL", "")
        key = (
            os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
            or os.environ.get("SUPABASE_SERVICE_KEY", "")
        )
        if not url or not key:
            raise CatastroRecommendError(
                "catastro_recommend_supabase_env_missing",
                missing_url=not bool(url),
                missing_key=not bool(key),
                hint=(
                    "Configurar SUPABASE_URL y una de "
                    "SUPABASE_SERVICE_ROLE_KEY (preferida) o "
                    "SUPABASE_SERVICE_KEY (legacy)."
                ),
            )
        try:
            from supabase import create_client
        except ImportError as exc:
            raise CatastroRecommendError(
                "catastro_recommend_supabase_package_missing",
                hint="pip install supabase",
            ) from exc
        return create_client(url, key)

    return _factory
