"""
El Catastro · Pipeline orquestador.

Orquesta el ciclo diario:
  1. Fetch paralelo de las 3 fuentes (Artificial Analysis, OpenRouter, LMArena)
  2. Normalización a `ModeloIA` por fuente
  3. Cross-validation con QuorumValidator 2-de-3 por modelo y por campo
  4. Persistencia en `catastro_modelos` (solo campos con quorum)
  5. Audit trail en `catastro_eventos` (todos los votos, incluso los failed)
  6. Update de `catastro_curadores.trust_score` con deltas

Diseño:
  - Async first: las 3 fuentes corren en paralelo con asyncio.gather
  - Tolerante a fallos: si una fuente cae, el quorum 2-de-3 sigue posible
    con las otras 2 (siempre que pasen >=2 valores)
  - Idempotente: si un modelo ya existe en BD, hace UPSERT con merge de
    fuentes_evidencia
  - Logging estructurado: cada paso emite log con run_id

Disciplina os.environ:
  - SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY se leen al ejecutar `.run()`
  - Nunca se cachean a nivel módulo

[Hilo Manus Catastro] · Sprint 86 Bloque 2 · 2026-05-04
"""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from kernel.catastro.persistence import (
    CatastroPersistence,
    PersistResult,
    build_modelo_from_pipeline_persistible,
)
from kernel.catastro.quorum import (
    FieldType,
    FuenteVote,
    QuorumOutcome,
    QuorumResult,
    QuorumValidator,
)
from kernel.catastro.sources import (
    ArtificialAnalysisFuente,
    BaseFuente,
    FuenteError,
    LMArenaFuente,
    OpenRouterFuente,
    RawSnapshot,
)


logger = logging.getLogger(__name__)


# ============================================================================
# RESULTADO DE UN RUN COMPLETO
# ============================================================================

@dataclass
class PipelineRunResult:
    """Resultado completo de un ciclo del pipeline."""

    run_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None

    # Snapshots crudos por fuente
    snapshots: dict[str, RawSnapshot] = field(default_factory=dict)
    # Errores por fuente (si hubo)
    fuente_errors: dict[str, str] = field(default_factory=dict)

    # Modelos procesados (slug → quorum_results por campo)
    modelos_procesados: dict[str, list[QuorumResult]] = field(default_factory=dict)

    # Modelos que pasaron quorum y serán persistidos
    modelos_persistibles: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Trust deltas finales por fuente
    trust_deltas: dict[str, float] = field(default_factory=dict)

    # Resultados de persistencia (Bloque 3)
    persist_results: list[PersistResult] = field(default_factory=list)

    # Métricas resumen
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        if not self.finished_at:
            return None
        return (self.finished_at - self.started_at).total_seconds()

    @property
    def is_success(self) -> bool:
        """True si al menos 2 fuentes respondieron exitosamente."""
        return len(self.snapshots) >= 2

    def summary(self) -> dict[str, Any]:
        """Resumen serializable para logs / API."""
        persist_ok = sum(1 for r in self.persist_results if r.success and not r.dry_run)
        persist_dry = sum(1 for r in self.persist_results if r.dry_run)
        persist_fail = sum(1 for r in self.persist_results if not r.success)
        return {
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": self.duration_seconds,
            "is_success": self.is_success,
            "fuentes_ok": list(self.snapshots.keys()),
            "fuentes_error": self.fuente_errors,
            "modelos_total": len(self.modelos_procesados),
            "modelos_persistibles": len(self.modelos_persistibles),
            "trust_deltas": self.trust_deltas,
            "persist_summary": {
                "ok": persist_ok,
                "dry_run": persist_dry,
                "failed": persist_fail,
            },
            "metrics": self.metrics,
        }


# ============================================================================
# PIPELINE
# ============================================================================

class CatastroPipeline:
    """
    Orquestador del ciclo diario del Catastro.

    Uso típico (Railway cron):
        pipeline = CatastroPipeline()
        result = await pipeline.run()
        if result.is_success:
            log.info(result.summary())
    """

    DEFAULT_SOURCES: tuple[type[BaseFuente], ...] = (
        ArtificialAnalysisFuente,
        OpenRouterFuente,
        LMArenaFuente,
    )

    def __init__(
        self,
        *,
        sources: Optional[list[BaseFuente]] = None,
        validator: Optional[QuorumValidator] = None,
        dry_run: bool = False,
        persistence: Optional[CatastroPersistence] = None,
    ) -> None:
        """
        Args:
            sources: lista de instancias de BaseFuente. Si None, se usan
                     las 3 oficiales con dry_run=False.
            validator: instancia de QuorumValidator. Si None, default 10%.
            dry_run: si True, todas las fuentes corren con dry_run=True
                     (sin red, devuelven snapshots fake) Y persistence
                     hereda dry_run=True (no toca Supabase).
            persistence: instancia de CatastroPersistence. Si None, se
                         construye una con dry_run igual al del pipeline.
                         Se respeta el dry_run propio si se pasa explícita.
        """
        self.dry_run = dry_run
        if sources is not None:
            self.sources = sources
        else:
            self.sources = [cls(dry_run=dry_run) for cls in self.DEFAULT_SOURCES]

        self.validator = validator or QuorumValidator(numeric_tolerance=0.10)
        self.persistence = persistence or CatastroPersistence(dry_run=dry_run)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    async def run(self) -> PipelineRunResult:
        """
        Ejecuta un ciclo completo del pipeline.

        Returns:
            PipelineRunResult con snapshots, modelos, quorum results, deltas.
        """
        run_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)

        result = PipelineRunResult(run_id=run_id, started_at=started_at)

        logger.info(f"[catastro_pipeline] Run {run_id} starting (dry_run={self.dry_run})")

        # Paso 1: fetch paralelo
        await self._fetch_all(result)

        # Paso 2: si <2 fuentes respondieron, marcar como degradado
        if not result.is_success:
            logger.error(
                f"[catastro_pipeline] Run {run_id} DEGRADED: solo "
                f"{len(result.snapshots)} fuente(s) respondieron"
            )
            result.finished_at = datetime.now(timezone.utc)
            return result

        # Paso 3: normalizar y agrupar por modelo
        modelos_por_fuente = self._normalize_snapshots(result)

        # Paso 4: cross-validate con quorum
        all_quorum_results = self._cross_validate(modelos_por_fuente, result)

        # Paso 5: identificar persistibles
        self._extract_persistible(all_quorum_results, result)

        # Paso 6: trust deltas
        flat_results = [qr for qrs in result.modelos_procesados.values() for qr in qrs]
        result.trust_deltas = self.validator.compute_trust_deltas(flat_results)

        # Paso 7: persistencia atómica via RPC (Bloque 3)
        await self._persist_all(result)

        # Métricas finales
        result.metrics = {
            "total_modelos_vistos": len(result.modelos_procesados),
            "total_modelos_persistibles": len(result.modelos_persistibles),
            "total_quorum_validations": len(flat_results),
            "quorum_unanimous_count": sum(
                1 for qr in flat_results if qr.outcome == QuorumOutcome.QUORUM_UNANIMOUS
            ),
            "quorum_reached_count": sum(
                1 for qr in flat_results if qr.outcome == QuorumOutcome.QUORUM_REACHED
            ),
            "quorum_failed_count": sum(
                1 for qr in flat_results if qr.outcome == QuorumOutcome.QUORUM_FAILED
            ),
            "insufficient_data_count": sum(
                1 for qr in flat_results if qr.outcome == QuorumOutcome.INSUFFICIENT_DATA
            ),
        }

        result.finished_at = datetime.now(timezone.utc)
        persist_ok = sum(1 for r in result.persist_results if r.success and not r.dry_run)
        persist_dry = sum(1 for r in result.persist_results if r.dry_run)
        persist_fail = sum(1 for r in result.persist_results if not r.success)
        logger.info(
            f"[catastro_pipeline] Run {run_id} OK \u00b7 "
            f"persistibles={result.metrics['total_modelos_persistibles']}/{result.metrics['total_modelos_vistos']} \u00b7 "
            f"persist_ok={persist_ok} dry={persist_dry} fail={persist_fail} \u00b7 "
            f"duration={result.duration_seconds:.2f}s"
        )
        return result

    # ------------------------------------------------------------------
    # Paso 7: persistencia atómica (Bloque 3)
    # ------------------------------------------------------------------

    async def _persist_all(self, result: PipelineRunResult) -> None:
        """
        Persiste todos los modelos persistibles via RPC atómica.

        Cada modelo es una transacci\u00f3n independiente del lado servidor.
        Si uno falla, los dem\u00e1s contin\u00faan (degraded gracefully).

        Memento:
          - Esta llamada NO es paralela: la RPC actualiza
            catastro_curadores compartido y queremos serializaci\u00f3n
            para que los deltas no se sobreescriban en concurrent UPDATEs
            (PostgreSQL los acumular\u00eda igual gracias a `+ delta`, pero
            preferimos serializaci\u00f3n estricta por simplicidad de debug).
        """
        if not result.modelos_persistibles:
            logger.info("[catastro_pipeline] Paso 7 skip: sin modelos persistibles")
            return

        for slug, persistible in result.modelos_persistibles.items():
            quorum_results = result.modelos_procesados.get(slug, [])
            try:
                modelo = build_modelo_from_pipeline_persistible(
                    slug=slug,
                    persistible=persistible,
                    quorum_results=quorum_results,
                )
            except Exception as e:  # noqa: BLE001
                logger.exception(
                    f"[catastro_pipeline] persist build_modelo CRASH slug={slug}: {e}"
                )
                result.persist_results.append(
                    PersistResult(
                        modelo_id=slug,
                        success=False,
                        error_code="catastro_persist_build_modelo_crash",
                        error_message=f"{type(e).__name__}: {e}",
                    )
                )
                continue

            try:
                # Solo enviamos los deltas que aplican a este modelo
                # (los acumulados globales — la RPC los aplicar\u00e1 una vez
                # por modelo, lo cual es contable y deseado: cada modelo
                # contribuye su propio delta al curador correspondiente)
                pr = self.persistence.persist(
                    modelo=modelo,
                    trust_deltas=result.trust_deltas,
                )
            except Exception as e:  # noqa: BLE001
                logger.exception(
                    f"[catastro_pipeline] persist CRASH slug={slug}: {e}"
                )
                pr = PersistResult(
                    modelo_id=slug,
                    success=False,
                    error_code="catastro_persist_call_crash",
                    error_message=f"{type(e).__name__}: {e}",
                )
            result.persist_results.append(pr)

    # ------------------------------------------------------------------
    # Paso 1: fetch paralelo
    # ------------------------------------------------------------------

    async def _fetch_all(self, result: PipelineRunResult) -> None:
        """Fetch concurrente de todas las fuentes con tolerancia a fallos."""
        tasks = [self._fetch_one(source, result) for source in self.sources]
        await asyncio.gather(*tasks, return_exceptions=False)

    async def _fetch_one(self, source: BaseFuente, result: PipelineRunResult) -> None:
        """Fetch de una fuente, atrapando errores."""
        try:
            snapshot = await source.fetch()
            result.snapshots[source.nombre] = snapshot
            logger.info(
                f"[catastro_pipeline] {source.nombre} OK · "
                f"hash={snapshot.payload_hash} · meta={snapshot.metadata}"
            )
        except FuenteError as e:
            result.fuente_errors[source.nombre] = str(e)
            logger.warning(f"[catastro_pipeline] {source.nombre} FAILED: {e}")
        except Exception as e:  # noqa: BLE001
            result.fuente_errors[source.nombre] = f"{type(e).__name__}: {e}"
            logger.exception(f"[catastro_pipeline] {source.nombre} CRASH: {e}")

    # ------------------------------------------------------------------
    # Paso 3: normalización
    # ------------------------------------------------------------------

    def _normalize_snapshots(
        self, result: PipelineRunResult
    ) -> dict[str, dict[str, dict[str, Any]]]:
        """
        Normaliza cada snapshot a dict por modelo:
          { modelo_slug: { fuente: campos_normalizados } }

        El slug es la KEY canónica de cross-source. Estrategia simple:
          - Artificial Analysis: usa `slug` directamente
          - OpenRouter: usa `id` lowercased y normalizado
          - LMArena: usa `model_name`

        Para matching cross-source, se aplica `normalize_slug()` que
        maneja variaciones (claude-opus-4-7 vs claude-opus-4.7).
        """
        modelos_por_fuente: dict[str, dict[str, dict[str, Any]]] = {}

        for fuente_name, snapshot in result.snapshots.items():
            if fuente_name == "artificial_analysis":
                self._extract_aa(snapshot, modelos_por_fuente)
            elif fuente_name == "openrouter":
                self._extract_openrouter(snapshot, modelos_por_fuente)
            elif fuente_name == "lmarena":
                self._extract_lmarena(snapshot, modelos_por_fuente)
            else:
                logger.warning(f"[catastro_pipeline] fuente desconocida: {fuente_name}")

        return modelos_por_fuente

    @staticmethod
    def normalize_slug(raw: str) -> str:
        """Normaliza slug: lowercase, replace . con -, replace _ con -."""
        return raw.strip().lower().replace(".", "-").replace("_", "-").replace("/", "-")

    def _extract_aa(self, snapshot: RawSnapshot, agg: dict) -> None:
        for item in snapshot.payload.get("data", []):
            slug = self.normalize_slug(item.get("slug") or item.get("id") or "")
            if not slug:
                continue
            agg.setdefault(slug, {})["artificial_analysis"] = {
                "raw_slug": item.get("slug"),
                "name": item.get("name"),
                "organization": (item.get("model_creator") or {}).get("name"),
                "quality_score": ArtificialAnalysisFuente.extract_quality_score(item),
                "pricing": ArtificialAnalysisFuente.extract_pricing(item),
                "tokens_per_second": item.get("median_output_tokens_per_second"),
                "ttft_seconds": item.get("median_time_to_first_token_seconds"),
            }

    def _extract_openrouter(self, snapshot: RawSnapshot, agg: dict) -> None:
        for item in snapshot.payload.get("data", []):
            slug = self.normalize_slug(item.get("canonical_slug") or item.get("id") or "")
            if not slug:
                continue
            agg.setdefault(slug, {})["openrouter"] = {
                "raw_id": item.get("id"),
                "name": item.get("name"),
                "context_length": OpenRouterFuente.extract_context_length(item),
                "pricing": OpenRouterFuente.extract_pricing(item),
                "is_open_source": OpenRouterFuente.is_open_source(item),
                "supported_parameters": item.get("supported_parameters", []),
                "input_modalities": (item.get("architecture") or {}).get("input_modalities", []),
                "output_modalities": (item.get("architecture") or {}).get("output_modalities", []),
            }

    def _extract_lmarena(self, snapshot: RawSnapshot, agg: dict) -> None:
        for row in snapshot.payload.get("rows", []):
            slug = self.normalize_slug(row.get("model_name") or "")
            if not slug:
                continue
            agg.setdefault(slug, {})["lmarena"] = {
                "raw_model_name": row.get("model_name"),
                "organization": row.get("organization"),
                "license": row.get("license"),
                "arena_score": LMArenaFuente.extract_arena_score(row),
                "rank": LMArenaFuente.extract_rank(row),
                "vote_count": row.get("vote_count"),
                "category": row.get("category"),
                "leaderboard_publish_date": row.get("leaderboard_publish_date"),
            }

    # ------------------------------------------------------------------
    # Paso 4: cross-validate
    # ------------------------------------------------------------------

    def _cross_validate(
        self,
        modelos_por_fuente: dict[str, dict[str, dict[str, Any]]],
        result: PipelineRunResult,
    ) -> dict[str, list[QuorumResult]]:
        """
        Para cada modelo, valida campos cross-source con QuorumValidator.

        Campos cross-source:
          - presence: ¿el modelo aparece en N fuentes?
          - organization (categorical)
          - license (categorical) — solo lmarena lo provee, así que su
            quorum será insufficient_data, pero registramos el voto
          - pricing.input_per_million (numeric, AA + OR)
          - pricing.output_per_million (numeric, AA + OR)

        Nota: quality_score y arena_score son métricas DIFERENTES con
        escalas distintas (0-100 vs Elo). NO se cross-validan entre sí.
        Se persisten ambas como columnas separadas.
        """
        all_results: dict[str, list[QuorumResult]] = {}

        for slug, fuentes_data in modelos_por_fuente.items():
            quorum_results: list[QuorumResult] = []

            # Validation 1: presence (¿en cuántas fuentes aparece?)
            presence_votes = [
                FuenteVote(f, True if f in fuentes_data else None)
                for f in QuorumValidator.OFFICIAL_SOURCES
            ]
            quorum_results.append(
                self.validator.validate(
                    field_name="presence",
                    field_type=FieldType.PRESENCE,
                    votes=presence_votes,
                )
            )

            # Validation 2: organization
            org_votes = [
                FuenteVote(f, fuentes_data.get(f, {}).get("organization") if f in fuentes_data else None)
                for f in QuorumValidator.OFFICIAL_SOURCES
            ]
            if any(v.has_data for v in org_votes):
                quorum_results.append(
                    self.validator.validate(
                        field_name="organization",
                        field_type=FieldType.CATEGORICAL,
                        votes=org_votes,
                    )
                )

            # Validation 3: pricing.input_per_million
            input_votes = [
                FuenteVote(
                    f,
                    (fuentes_data.get(f, {}).get("pricing") or {}).get("input_per_million")
                    if f in fuentes_data else None,
                )
                for f in QuorumValidator.OFFICIAL_SOURCES
            ]
            if sum(1 for v in input_votes if v.has_data) >= 2:
                quorum_results.append(
                    self.validator.validate(
                        field_name="pricing.input_per_million",
                        field_type=FieldType.NUMERIC,
                        votes=input_votes,
                    )
                )

            # Validation 4: pricing.output_per_million
            output_votes = [
                FuenteVote(
                    f,
                    (fuentes_data.get(f, {}).get("pricing") or {}).get("output_per_million")
                    if f in fuentes_data else None,
                )
                for f in QuorumValidator.OFFICIAL_SOURCES
            ]
            if sum(1 for v in output_votes if v.has_data) >= 2:
                quorum_results.append(
                    self.validator.validate(
                        field_name="pricing.output_per_million",
                        field_type=FieldType.NUMERIC,
                        votes=output_votes,
                    )
                )

            all_results[slug] = quorum_results
            result.modelos_procesados[slug] = quorum_results

        return all_results

    # ------------------------------------------------------------------
    # Paso 5: extracción de persistibles
    # ------------------------------------------------------------------

    def _extract_persistible(
        self,
        all_quorum_results: dict[str, list[QuorumResult]],
        result: PipelineRunResult,
    ) -> None:
        """
        Identifica modelos que pasaron quorum de presence + tienen al
        menos 1 campo más con quorum.
        """
        for slug, qrs in all_quorum_results.items():
            presence_qr = next((qr for qr in qrs if qr.field_name == "presence"), None)
            if not presence_qr or not presence_qr.is_persistable:
                continue

            persistible_fields: dict[str, Any] = {}
            for qr in qrs:
                if qr.field_name == "presence":
                    continue
                if qr.is_persistable:
                    persistible_fields[qr.field_name] = qr.consensus_value

            if persistible_fields:  # debe tener ≥1 campo además de presence
                result.modelos_persistibles[slug] = {
                    "slug": slug,
                    "fields": persistible_fields,
                    "presence_confidence": presence_qr.confidence_score,
                    "confirming_sources": presence_qr.confirming_sources,
                }
