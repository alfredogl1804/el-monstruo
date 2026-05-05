"""
El Catastro · Capa de persistencia atómica a Supabase.

Wiring del pipeline → Supabase via RPC PL/pgSQL.

Diseño:
  - supabase-py (PostgREST stateless) NO soporta transacciones HTTP.
  - Para garantizar atomicidad de las 3 operaciones del Catastro
    (UPSERT modelo + INSERT evento + UPDATE deltas curadores), se delega
    a la función `catastro_apply_quorum_outcome` (scripts/018).
  - Esta capa SOLO transforma DTO Python → jsonb, llama RPC, parsea
    respuesta. Toda la lógica transaccional vive del lado servidor.

Disciplina os.environ:
  - SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY se leen lazy en `.persist()`.
  - Nunca se cachean a nivel módulo.
  - Si alguna falta → modo dry_run (devuelve PersistResult.dry_run=True).

Memento (decisiones contextuales · anti-Dory):
  1. La RPC ya garantiza atomicidad — esta capa NO debe hacer fallback
     a operaciones secuenciales (eso rompería el contrato de "atómico
     o nada").
  2. El `dry_run` se activa si faltan env vars O si se pasa
     explícitamente al constructor (para tests).
  3. El cliente supabase se crea lazy (primera llamada a .persist())
     para que importar este módulo en tests SIN supabase-py instalado
     funcione (imports de runtime, no de top-level).
  4. Identidad de marca en errores: prefijo `catastro_persist_` en
     todos los códigos de error para que el bridge filtre.
  5. Si la RPC devuelve error PostgREST, NO se ejecuta nada parcial
     (la transacción del lado servidor hace ROLLBACK automático).

[Hilo Manus Catastro] · Sprint 86 Bloque 3 · 2026-05-04
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, Optional

# Categorías canónicas de error (mejora #2 audit Cowork Bloque 3).
# Permiten al monitor de cron detectar degradación por categoría.
ErrorCategory = Literal[
    "db_down",          # red/socket/connection refused → infra Supabase caída
    "rpc_validation",   # la función PL/pgSQL rechazó input (ERRCODE P0001 etc)
    "item_crash",       # excepción local antes de llegar a la red
    "network_timeout",  # timeout HTTP
    "none",             # éxito (placeholder)
    "unknown",          # default cuando no encaja en categorías
]

from kernel.catastro.quorum import QuorumResult
from kernel.catastro.schema import (
    CatastroEvento,
    CatastroModelo,
    PrioridadEvento,
    TipoEvento,
)


logger = logging.getLogger(__name__)


# ============================================================================
# RESULTADO DE PERSISTENCIA
# ============================================================================

@dataclass
class PersistResult:
    """Resultado de un intento de persistencia (single modelo)."""

    modelo_id: str
    success: bool
    dry_run: bool = False

    # Datos retornados por la RPC (cuando success)
    evento_id: Optional[str] = None
    curadores_actualizados: int = 0
    aplicado_at: Optional[str] = None

    # Diagnóstico (cuando NO success)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_category: ErrorCategory = "none"  # mejora #2 audit Cowork Bloque 3

    # Métrica del batch al que pertenece este resultado.
    # Se llena en `persist_many` después del loop, NO por item individual.
    # Permite que el monitor de cron alerte si failure_rate_observed > 0.10.
    failure_rate_observed: Optional[float] = None  # mejora #2 audit Cowork Bloque 3

    # Echo del payload enviado (útil para debug y dry_run)
    rpc_params_preview: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        return {
            "modelo_id": self.modelo_id,
            "success": self.success,
            "dry_run": self.dry_run,
            "evento_id": self.evento_id,
            "curadores_actualizados": self.curadores_actualizados,
            "aplicado_at": self.aplicado_at,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "error_category": self.error_category,
            "failure_rate_observed": self.failure_rate_observed,
        }


# ============================================================================
# EXCEPCIONES (identidad de marca: catastro_persist_*)
# ============================================================================

class CatastroPersistError(Exception):
    """Base de errores de la capa de persistencia."""

    code = "catastro_persist_error"


class CatastroPersistRpcFailure(CatastroPersistError):
    """La RPC PostgREST devolvió error (la transacción hizo ROLLBACK)."""

    code = "catastro_persist_rpc_failure"


class CatastroPersistMissingClient(CatastroPersistError):
    """supabase-py no está instalado en el entorno actual."""

    code = "catastro_persist_missing_client"


# ============================================================================
# CAPA DE PERSISTENCIA
# ============================================================================

class CatastroPersistence:
    """
    Persiste un quorum outcome a Supabase de forma ATÓMICA.

    Uso típico:
        persistence = CatastroPersistence()  # lee env vars al .persist()
        result = persistence.persist(
            modelo=catastro_modelo,
            evento=catastro_evento,
            trust_deltas={"artificial_analysis": -0.05, "openrouter": 0.0},
        )
        if not result.success and not result.dry_run:
            logger.error(result.error_message)
    """

    RPC_FUNCTION_NAME = "catastro_apply_quorum_outcome"
    REQUIRED_ENV_VARS = ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")

    def __init__(
        self,
        *,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        dry_run: bool = False,
        client_factory: Optional[Any] = None,
    ) -> None:
        """
        Args:
            supabase_url: si None, se lee de os.environ["SUPABASE_URL"] al persist.
            supabase_key: si None, se lee de os.environ["SUPABASE_SERVICE_ROLE_KEY"].
            dry_run: si True, no llama a Supabase (devuelve PersistResult.dry_run).
            client_factory: callable(url, key) → cliente. Útil para tests con mock.
                            Si None, se importa supabase.create_client lazy.
        """
        self._explicit_url = supabase_url
        self._explicit_key = supabase_key
        self._explicit_dry_run = dry_run
        self._client_factory = client_factory
        self._client: Any = None  # lazy init

    # ------------------------------------------------------------------
    # Resolución de credenciales (lazy, anti-os.environ-cache)
    # ------------------------------------------------------------------

    def _resolve_credentials(self) -> tuple[Optional[str], Optional[str]]:
        url = self._explicit_url or os.environ.get("SUPABASE_URL")
        key = self._explicit_key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        return url, key

    def _is_dry_run(self) -> bool:
        if self._explicit_dry_run:
            return True
        url, key = self._resolve_credentials()
        return not (url and key)

    # ------------------------------------------------------------------
    # Cliente Supabase (lazy import + lazy init)
    # ------------------------------------------------------------------

    def _get_client(self) -> Any:
        """Inicializa el cliente la primera vez. Reutiliza después."""
        if self._client is not None:
            return self._client

        url, key = self._resolve_credentials()
        if not (url and key):
            raise CatastroPersistError(
                "[catastro_persist_missing_env] SUPABASE_URL y "
                "SUPABASE_SERVICE_ROLE_KEY son obligatorias para modo real."
            )

        if self._client_factory is not None:
            self._client = self._client_factory(url, key)
            return self._client

        # Lazy import de supabase (puede no estar instalado en sandbox/tests)
        try:
            from supabase import create_client  # type: ignore
        except ImportError as e:
            raise CatastroPersistMissingClient(
                "[catastro_persist_missing_client] supabase-py no está "
                "instalado. Instala con `pip install supabase==2.29.0` o "
                "usa dry_run=True."
            ) from e

        self._client = create_client(url, key)
        return self._client

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def persist(
        self,
        *,
        modelo: CatastroModelo,
        evento: Optional[CatastroEvento] = None,
        trust_deltas: Optional[dict[str, float]] = None,
    ) -> PersistResult:
        """
        Persiste un modelo + evento + deltas atómicamente via RPC.

        Args:
            modelo: instancia de CatastroModelo (Pydantic).
            evento: instancia opcional de CatastroEvento. Si None, se
                    genera uno por default tipo=new_model prioridad=info.
            trust_deltas: dict {fuente: delta_float}. Si None, no se
                          actualiza ningún curador.

        Returns:
            PersistResult con success/error y datos de la RPC.
        """
        # Generar evento default si no se pasa
        if evento is None:
            evento = CatastroEvento(
                tipo=TipoEvento.NEW_MODEL,
                prioridad=PrioridadEvento.INFO,
                modelo_id=modelo.id,
                descripcion=f"Quorum outcome aplicado para {modelo.id} por el Catastro",
            )

        # Serializar a jsonb-friendly dicts
        modelo_jsonb = self._serialize_modelo(modelo)
        evento_jsonb = self._serialize_evento(evento)
        deltas_jsonb = self._serialize_deltas(trust_deltas)

        rpc_params = {
            "p_modelo": modelo_jsonb,
            "p_evento": evento_jsonb,
            "p_trust_deltas": deltas_jsonb,
        }

        # Dry run: devolver preview sin tocar red
        if self._is_dry_run():
            logger.info(
                f"[catastro_persist_dry_run] modelo={modelo.id} "
                f"evento={evento.tipo.value} deltas_count={len(deltas_jsonb)}"
            )
            return PersistResult(
                modelo_id=modelo.id,
                success=True,
                dry_run=True,
                rpc_params_preview=rpc_params,
            )

        # Llamada real
        try:
            client = self._get_client()
            response = client.rpc(self.RPC_FUNCTION_NAME, rpc_params).execute()
        except CatastroPersistError:
            raise
        except Exception as e:  # noqa: BLE001
            logger.exception(
                f"[catastro_persist_rpc_failure] modelo={modelo.id} error={e}"
            )
            return PersistResult(
                modelo_id=modelo.id,
                success=False,
                error_code=CatastroPersistRpcFailure.code,
                error_message=f"{type(e).__name__}: {e}",
                error_category=self._categorize_error(e),
                rpc_params_preview=rpc_params,
            )

        # Parsear respuesta de la RPC
        rpc_payload = self._extract_rpc_payload(response)

        if rpc_payload is None:
            return PersistResult(
                modelo_id=modelo.id,
                success=False,
                error_code=CatastroPersistRpcFailure.code,
                error_message="RPC devolvió respuesta vacía o no parseable",
                error_category="rpc_validation",
                rpc_params_preview=rpc_params,
            )

        return PersistResult(
            modelo_id=modelo.id,
            success=True,
            dry_run=False,
            evento_id=str(rpc_payload.get("evento_id")) if rpc_payload.get("evento_id") else None,
            curadores_actualizados=int(rpc_payload.get("curadores_actualizados") or 0),
            aplicado_at=rpc_payload.get("aplicado_at"),
            rpc_params_preview=rpc_params,
        )

    def persist_many(
        self,
        items: list[dict[str, Any]],
    ) -> list[PersistResult]:
        """
        Persiste múltiples items SECUENCIALMENTE.

        Cada llamada es atómica de forma INDIVIDUAL (transacción por
        modelo). NO hay atomicidad inter-modelo: si el item 5 falla,
        los items 0-4 ya quedaron persistidos.

        Esto es intencional: el Catastro prefiere persistencia parcial
        a perder un día completo de datos por un solo modelo malformado.

        Args:
            items: lista de dicts con keys "modelo", "evento" (opcional),
                   "trust_deltas" (opcional).

        Returns:
            lista de PersistResult, uno por item.
        """
        results: list[PersistResult] = []
        for idx, item in enumerate(items):
            modelo = item["modelo"]
            try:
                result = self.persist(
                    modelo=modelo,
                    evento=item.get("evento"),
                    trust_deltas=item.get("trust_deltas"),
                )
            except Exception as e:  # noqa: BLE001
                logger.exception(
                    f"[catastro_persist_item_crash] idx={idx} modelo={getattr(modelo, 'id', '?')}"
                )
                result = PersistResult(
                    modelo_id=getattr(modelo, "id", "unknown"),
                    success=False,
                    error_code="catastro_persist_item_crash",
                    error_message=f"{type(e).__name__}: {e}",
                    error_category="item_crash",
                )
            results.append(result)

        # Calcular failure_rate del batch y propagarlo a todos los results.
        # Así cada PersistResult lleva contexto de su batch para el monitor.
        if results:
            failed = sum(1 for r in results if not r.success and not r.dry_run)
            rate = failed / len(results)
            for r in results:
                r.failure_rate_observed = rate
        return results

    # ------------------------------------------------------------------
    # Helpers de serialización
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_modelo(modelo: CatastroModelo) -> dict[str, Any]:
        """Convierte CatastroModelo → dict jsonb-friendly (datetimes ISO)."""
        # Pydantic v2: model_dump con mode="json" maneja datetimes/UUIDs/Enums
        data = modelo.model_dump(mode="json", exclude_none=False, exclude={"embedding"})
        # Forzar campos JSON anidados a string-de-json para que el SQL los
        # parsee con (->>'key')::jsonb (la RPC usa ese pattern para listas/dicts)
        for key in (
            "dominios", "subcapacidades", "limitaciones", "fortalezas",
            "debilidades", "casos_uso_recomendados_monstruo",
            "fuentes_evidencia", "capacidades_tecnicas", "velocidad",
            "data_extra",
        ):
            if key in data and not isinstance(data[key], str):
                # En la RPC accedemos como p_modelo->'key' (preserva jsonb).
                # Pero el campo `(p_modelo->'dominios')::jsonb` requiere que
                # ya sea jsonb. En jsonb, una lista/dict Python serializan
                # naturalmente — NO los convertimos a string aquí.
                pass
        return data

    @staticmethod
    def _serialize_evento(evento: CatastroEvento) -> dict[str, Any]:
        return evento.model_dump(mode="json", exclude_none=False)

    @staticmethod
    def _serialize_deltas(
        deltas: Optional[dict[str, float]],
    ) -> dict[str, float]:
        if not deltas:
            return {}
        # Asegurar float puro (no numpy, no Decimal)
        return {str(k): float(v) for k, v in deltas.items()}

    # ------------------------------------------------------------------
    # Helpers de respuesta
    # ------------------------------------------------------------------

    @staticmethod
    def _categorize_error(exc: Exception) -> ErrorCategory:
        """
        Clasifica una excepción en una categoría canónica para el monitor.

        Heurística conservadora basada en tipo y mensaje. Mejora #2 del
        audit Cowork Bloque 3 — permite que el cron alerte por categoría.
        """
        name = type(exc).__name__
        msg = str(exc).lower()

        # Timeouts explícitos
        if "timeout" in name.lower() or "timeout" in msg:
            return "network_timeout"

        # Errores de red / conectividad
        network_markers = (
            "connection", "refused", "unreachable", "dns", "socket",
            "name resolution", "no route to host", "network is unreachable",
        )
        if any(m in msg for m in network_markers) or name in (
            "ConnectionError", "ConnectionRefusedError", "OSError", "gaierror",
        ):
            return "db_down"

        # Errores de validación del lado servidor (PostgREST/PL/pgSQL)
        validation_markers = (
            "postgrest", "check constraint", "violates", "invalid input",
            "errcode", "p0001", "23502", "23503", "23505", "22p02",
            "catastro_persist_invalid_input",
        )
        if any(m in msg for m in validation_markers) or name == "APIError":
            return "rpc_validation"

        return "unknown"

    @staticmethod
    def _extract_rpc_payload(response: Any) -> Optional[dict[str, Any]]:
        """
        Extrae el payload jsonb de una respuesta supabase-py 2.29.0.

        El cliente devuelve un objeto con `.data` (lista o dict) según
        el tipo de RPC. Para nuestra función SCALAR-RETURNING, suele
        venir como:
            response.data = {"modelo_id": "...", "evento_id": "...", ...}
          o como string JSON que requiere parse.
        """
        if response is None:
            return None
        data = getattr(response, "data", None)
        if data is None:
            return None
        if isinstance(data, dict):
            return data
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                return first
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                return None
        return None


# ============================================================================
# Helper de alto nivel para integración en pipeline.py
# ============================================================================

def build_modelo_from_pipeline_persistible(
    slug: str,
    persistible: dict[str, Any],
    quorum_results: list[QuorumResult],
) -> CatastroModelo:
    """
    Construye un CatastroModelo a partir del dict `modelos_persistibles`
    que produce el pipeline.

    Mapea los nombres de campo del quorum a las columnas del schema.
    """
    fields = persistible.get("fields", {})

    # Mapping de nombres del quorum → atributos de CatastroModelo
    pricing_input = fields.get("pricing.input_per_million")
    pricing_output = fields.get("pricing.output_per_million")
    organization = fields.get("organization") or "unknown"

    # Confidence proviene del presence quorum
    presence_confidence = float(persistible.get("presence_confidence", 0.5))

    # Sources que confirmaron presencia
    confirming_sources = persistible.get("confirming_sources", [])

    # fuentes_evidencia = una entrada simple por cada fuente confirmante
    now_iso = datetime.now(timezone.utc)
    fuentes_evidencia = [
        {
            "url": f"https://catastro.internal/{src}/{slug}",
            "fetched_at": now_iso,
            "payload_hash": "pipeline-derived",
            "curador": src,
            "tipo_dato": "presence",
        }
        for src in confirming_sources
    ]

    return CatastroModelo(
        id=slug,
        nombre=slug,
        proveedor=str(organization),
        dominios=["llm_frontier"],  # default Sprint 86
        precio_input_per_million=pricing_input,
        precio_output_per_million=pricing_output,
        fuentes_evidencia=fuentes_evidencia,
        quorum_alcanzado=True,
        confidence=presence_confidence,
        ultima_validacion=now_iso,
    )


__all__ = [
    "CatastroPersistence",
    "PersistResult",
    "CatastroPersistError",
    "CatastroPersistRpcFailure",
    "CatastroPersistMissingClient",
    "build_modelo_from_pipeline_persistible",
]
